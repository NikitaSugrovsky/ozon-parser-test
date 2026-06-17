import random
import time
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

class AntiDetection:
    @staticmethod
    def random_delay(min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def human_scroll(page):
        for _ in range(3):
            page.mouse.wheel(0, random.randint(200, 500))
            time.sleep(random.uniform(0.5, 1.5))

class OzonParser:
    def __init__(self, headless=True):
        self.headless = headless
    
    def parse(self, query, sku):
        with sync_playwright() as p:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Firefox/121.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0'
            ]
            
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=random.choice(user_agents),
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            url = f"https://www.ozon.ru/search/?text={query}"
            page.goto(url)
            
            AntiDetection.random_delay(2, 4)
            AntiDetection.human_scroll(page)
            
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
