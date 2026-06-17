from playwright.sync_api import sync_playwright
import json
from datetime import datetime

class OzonParser:
    def __init__(self, headless=True):
        self.headless = headless
    
    def parse(self, query, sku):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            url = f"https://www.ozon.ru/search/?text={query}"
            page.goto(url)
            
            page.wait_for_selector('div[data-widget="searchResultsV2"]', timeout=30000)
            
            items = page.query_selector_all('a[href*="/product/"]')
            position = None
            
            for i, item in enumerate(items[:100], 1):
                href = item.get_attribute('href')
                if href and f'/product/{sku}' in href:
                    position = i
                    break
            
            browser.close()
            
            return {
                "query": query,
                "sku": sku,
                "position": position or "not_found",
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    parser = OzonParser(headless=True)
    result = parser.parse("наушники", "3418469702")
    print(json.dumps(result, ensure_ascii=False, indent=2))
