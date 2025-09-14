# validate_urls.py
import json
import requests
import os


class URLValidator:
    def __init__(self):
        pass

    def fetch_page(self, url):
        """Try to fetch a page, return True if valid HTML, False otherwise."""
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            if "text/html" not in resp.headers.get("Content-Type", ""):
                return False

            # ✅ Only check the first 10 KB for error-like signatures
            snippet = resp.text[:10000].lower()
            error_signatures = [
                "404 - not found",
                "page not found",
                "error 404",
            ]

            if any(sig in snippet for sig in error_signatures):
                print(f" Skipping {url} (error-like content)")
                return False

            return True

        except requests.exceptions.RequestException as e:
            print(f" Error fetching {url}: {e}")
        return False

    def validate_urls(self, urls):
        """Return only URLs that fetch successfully."""
        valid_urls = []
        for url in urls:
            if self.fetch_page(url):
                print(f" Valid URL: {url}")
                valid_urls.append(url)
            else:
                print(f"Removing dead URL: {url}")
        return valid_urls


if __name__ == "__main__":
    validator = URLValidator()

    input_file = os.path.join("data", "all_urls.json")
    output_file = os.path.join("data", "valid_urls.json")

    # Load all URLs
    with open(input_file, "r", encoding="utf-8") as f:
        all_urls = json.load(f)

    print(f"\nLoaded {len(all_urls)} URLs from {input_file}")

    # Validate them
    valid_urls = validator.validate_urls(all_urls)

    print(f"\nTotal valid URLs: {len(valid_urls)}")

    # Save valid URLs
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(valid_urls, f, indent=2)

    print(f"\n✅ Saved {len(valid_urls)} valid URLs to {output_file}")
