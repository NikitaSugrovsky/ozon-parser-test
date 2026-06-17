import json
import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright
from datetime import datetime

class OzonParser:
    def __init__(self, headless=False):
        self.headless = headless
    
    def parse(self, query, sku):
        with sync_playwright() as p:
            # Антидетект
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Firefox/121.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0 Safari/537.36'
            ]
            
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent=random.choice(user_agents),
                viewport={'width': 1920, 'height': 1080},
                locale='ru-RU'
            )
            
            page = context.new_page()
            
            # ПРАВИЛЬНАЯ ССЫЛКА НА ПОИСК
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.ozon.ru/search/?text={encoded_query}&from_global=true"
            print(f"Открываю: {url}")
            
            try:
                page.goto(url, timeout=30000)
                time.sleep(5)
                
                # Ищем товары в результатах поиска
                items = page.query_selector_all('a[href*="/product/"]')
                position = None
                
                for i, item in enumerate(items[:100], 1):
                    href = item.get_attribute('href')
                    if href and f"/product/{sku}" in href:
                        position = i
                        break
                
                browser.close()
                
                return {
                    "query": query,
                    "sku": sku,
                    "position": position if position else "not_found",
                    "page": 1,
                    "total_checked": min(100, len(items)),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"Ошибка: {e}")
                browser.close()
                return {
                    "query": query,
                    "sku": sku,
                    "position": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

if __name__ == "__main__":
    parser = OzonParser(headless=False)
    result = parser.parse("наушники беспроводные", "3531022625")
    print("\n" + "="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2))