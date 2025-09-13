import json
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def crawl_pages(base_url, max_depth=2):
    visited = set()
    to_visit = [(base_url, 0)]  # store (url, depth)
    domain = urlparse(base_url).netloc

    while to_visit:
        url, depth = to_visit.pop()
        if url in visited or depth > max_depth:
            continue

        visited.add(url)
        print(f"Visiting (depth {depth}): {url}")

        try:
            resp = requests.get(url, timeout=10)
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            if depth < max_depth:
                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)
                    if parsed.netloc == domain and full_url not in visited:
                        to_visit.append((full_url, depth + 1))
        except Exception as e:
            print("❌ Error fetching:", url, e)

    return list(visited)

if __name__ == "__main__":
    urls = crawl_pages("https://developer.atlan.com/snippets/custom-metadata/create/", max_depth=1)
    with open("data/temp.json", "w") as f:
        json.dump(urls, f, indent=2)

    print(f"✅ Saved {len(urls)} URLs to data/temp.json")
