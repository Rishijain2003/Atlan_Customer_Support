# crawler.py
import json
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import os


class WebCrawler:
    def __init__(self):
        self.visited = set()

    def normalize_url(self, url):
        """Remove fragments and trailing slashes."""
        url = url.split('#')[0]
        return url.rstrip('/') if url.endswith('/') else url

    def fetch_page(self, url):
        """Try to fetch a page, return response or None if fails or invalid content."""
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            if "text/html" not in resp.headers.get("Content-Type", ""):
                return None

            # ✅ Only check the first 10 KB for error-like signatures
            snippet = resp.text[:10000].lower()
            error_signatures = [
                "404 - not found",
                "page not found",
                "error 404",
            ]

            if any(sig in snippet for sig in error_signatures):
                print(f" Skipping {url} (error-like content)")
                return None

            return resp.text

        except requests.exceptions.RequestException as e:
            print(f" Error fetching {url}: {e}")
        return None

    def crawl_pages(self, base_url):
        """Crawl pages within a single domain."""
        start_url = self.normalize_url(base_url)
        to_visit = [start_url]
        domain = urlparse(start_url).netloc

        while to_visit:
            current_url = to_visit.pop()

            if current_url in self.visited:
                continue
            self.visited.add(current_url)

            print("Visiting:", current_url)
            html = self.fetch_page(current_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(current_url, href)
                normalized = self.normalize_url(full_url)

                parsed = urlparse(normalized)
                if parsed.netloc == domain and normalized not in self.visited:
                    to_visit.append(normalized)

    def crawl_multiple(self, base_urls):
        """Crawl multiple seeds."""
        for base in base_urls:
            print(f"\n--- Crawling from base: {base} ---")
            self.crawl_pages(base)
        return list(self.visited)

    def validate_urls(self, urls):
        """Return only URLs that fetch successfully."""
        valid_urls = []
        for url in urls:
            if self.fetch_page(url):
                valid_urls.append(url)
            else:
                print(f"Removing dead URL: {url}")
        return valid_urls


if __name__ == "__main__":
    crawler = WebCrawler()

    # Seed URLs
    seed_urls = [
        "https://docs.atlan.com/",
        "https://developer.atlan.com/",
        "https://developer.atlan.com/getting-started/",
        "https://developer.atlan.com/concepts/"
    ]

    print("\n=== Starting crawl ===")
    all_urls = crawler.crawl_multiple(seed_urls)

    print(f"\nTotal collected URLs (before validation): {len(all_urls)}")

   

    # Ensure output directory exists
    # output_file = os.path.join("customer_support", "data", "all_urls.json")
    # os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save only valid URLs
    with open("data/all_urls.json", "w") as f:
        json.dump(all_urls, f, indent=2)

    print(f"\n✅ Crawl finished. Saved {len(all_urls)} working URLs to data/all_urls.json")
