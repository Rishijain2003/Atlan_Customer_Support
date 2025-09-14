# crawler.py
import json
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def normalize_url(url):
    """
    Normalizes a URL by removing its fragment and any trailing slashes.
    """
    # Remove the fragment part (anything after '#')
    url = url.split('#')[0]
    # Remove any trailing slashes
    if url.endswith('/'):
        url = url.rstrip('/')
    return url

def crawl_pages(base_url):
    """
    Crawls all pages within a single base URL's domain.
    """
    # Normalize the starting URL itself
    start_url = normalize_url(base_url)
    visited, to_visit = set(), [start_url]
    domain = urlparse(start_url).netloc

    while to_visit:
        current_url = to_visit.pop()
        
      
        if current_url in visited:
            continue
        visited.add(current_url)

        print("Visiting:", current_url)
        try:
            resp = requests.get(current_url, timeout=10)
            resp.raise_for_status() 

            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(current_url, href)
                
                
                normalized_new_url = normalize_url(full_url)

                parsed = urlparse(normalized_new_url)
                if parsed.netloc == domain and normalized_new_url not in visited:
                    to_visit.append(normalized_new_url)
        except requests.exceptions.RequestException as e:
            print(f" Error fetching {current_url}: {e}")
        except Exception as e:
            print(f" An unexpected error occurred for {current_url}: {e}")
            
    return list(visited)

def crawl_multiple(base_urls):
    """
    Crawls multiple base URLs and returns all unique links.
    """
    all_urls = set()
    for base in base_urls:
        print(f"\n Crawling from base: {base}")
        urls = crawl_pages(base)
        all_urls.update(urls)
    return list(all_urls)

if __name__ == "__main__":
    
    print("--- Starting crawl for docs.atlan.com ---")
    documentation_urls = crawl_pages("https://docs.atlan.com/")
    with open("data/document_urls.json", "w") as f:
        json.dump(documentation_urls, f, indent=2)
    print(f" Saved {len(documentation_urls)} unique URLs to data/document_urls.json")

   
    print("\n--- Starting crawl for developer.atlan.com ---")
    developer_seeds = [
        "https://developer.atlan.com/",
        "https://developer.atlan.com/getting-started/",
        "https://developer.atlan.com/concepts/"
    ]
    developer_urls = crawl_multiple(developer_seeds)
    with open("data/development_urls.json", "w") as f:
        json.dump(developer_urls, f, indent=2)
    print(f" Saved {len(developer_urls)} unique URLs to data/development_urls.json")