import json
import time
import random
import urllib.parse
import argparse
from playwright.sync_api import sync_playwright
from datetime import datetime
from typing import List, Dict, Optional

class OzonParser:
    def __init__(self, headless=False):
        self.headless = headless
    
    def parse(self, query: str, sku: str, max_pages: int = 3) -> Dict:
        """
        Парсинг поисковой выдачи Ozon
        
        Args:
            query: поисковый запрос
            sku: артикул товара
            max_pages: максимальное количество страниц для проверки
        
        Returns:
            Dict с результатами
        """
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
                locale='ru-RU',
                timezone_id='Europe/Moscow'
            )
            
            page = context.new_page()
            
            encoded_query = urllib.parse.quote(query)
            position = None
            total_checked = 0
            current_page = 1
            
            while current_page <= max_pages and position is None:
                if current_page == 1:
                    url = f"https://www.ozon.ru/search/?text={encoded_query}&from_global=true"
                else:
                    url = f"https://www.ozon.ru/search/?text={encoded_query}&page={current_page}&from_global=true"
                
                print(f"📄 Страница {current_page}: {url}")
                
                try:
                    page.goto(url, timeout=30000)
                    time.sleep(random.uniform(3, 5))
                    
                    # Прокрутка для загрузки всех товаров
                    for _ in range(3):
                        page.mouse.wheel(0, 500)
                        time.sleep(0.3)
                    
                    # Ищем ВСЕ ссылки на товары
                    items = page.query_selector_all('a[href*="/product/"]')
                    print(f"Найдено товаров на странице {current_page}: {len(items)}")
                    
                    if not items:
                        print("Товары не найдены")
                        break
                    
                    for i, item in enumerate(items, start=1):
                        total_checked += 1
                        if total_checked > 100:
                            break
                        
                        href = item.get_attribute('href')
                        if not href:
                            continue
                        
                        # Проверяем разные форматы SKU в ссылке
                        if (f"/product/{sku}" in href or 
                            href.endswith(f"/{sku}/") or 
                            f"-{sku}" in href or
                            f"product_id={sku}" in href):
                            position = i
                            print(f"✅ НАЙДЕН на странице {current_page}, позиция {i}")
                            break
                    
                    if position:
                        break
                    
                    # Проверяем наличие следующей страницы
                    next_button = page.query_selector('a[href*="page="]')
                    if next_button:
                        current_page += 1
                    else:
                        print("📄 Достигнут конец выдачи")
                        break
                    
                except Exception as e:
                    print(f"❌ Ошибка на странице {current_page}: {e}")
                    break
            
            browser.close()
            
            return {
                "query": query,
                "sku": sku,
                "position": position if position else "not_found",
                "page": current_page,
                "total_checked": min(100, total_checked),
                "timestamp": datetime.now().isoformat()
            }
    
    def parse_multiple(self, query: str, skus: List[str], 
                       repeat: int = 1, interval: int = 30) -> List[Dict]:
        """
        Парсинг нескольких SKU с повторами
        
        Args:
            query: поисковый запрос
            skus: список артикулов
            repeat: количество повторных запусков
            interval: интервал между запусками (секунд)
        
        Returns:
            List[Dict] с результатами
        """
        results = []
        
        for run in range(1, repeat + 1):
            print(f"\n{'='*60}")
            print(f"🏃 Запуск {run}/{repeat}")
            print(f"{'='*60}")
            
            for sku in skus:
                print(f"\n🔎 Поиск SKU: {sku}")
                
                # Случайная задержка между запросами (4-7 секунд)
                delay = random.uniform(4, 7)
                print(f"⏳ Задержка {delay:.2f} сек...")
                time.sleep(delay)
                
                result = self.parse(query, sku)
                result["run"] = run
                results.append(result)
                
                # Сохраняем промежуточные результаты
                with open('output.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 Результаты сохранены в output.json")
            
            if run < repeat:
                print(f"\n⏳ Ожидание {interval} секунд...")
                time.sleep(interval)
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Парсер поисковой выдачи Ozon')
    parser.add_argument('--query', type=str, required=True, help='Поисковый запрос')
    parser.add_argument('--sku', type=str, required=True, help='Артикул товара (SKU) или несколько через запятую')
    parser.add_argument('--repeat', type=int, default=1, help='Количество повторных запусков')
    parser.add_argument('--interval', type=int, default=30, help='Интервал между запусками (секунд)')
    parser.add_argument('--headless', action='store_true', help='Запуск в headless режиме')
    parser.add_argument('--pages', type=int, default=3, help='Максимальное количество страниц')
    
    args = parser.parse_args()
    
    skus = [sku.strip() for sku in args.sku.split(',')]
    
    print(f"\n{'='*60}")
    print(f"🔍 ПАРСЕР OZON")
    print(f"{'='*60}")
    print(f"📝 Запрос: {args.query}")
    print(f"📦 SKU: {', '.join(skus)}")
    print(f"🔄 Повторов: {args.repeat}, Интервал: {args.interval}с")
    print(f"📄 Страниц: {args.pages}")
    print(f"{'='*60}\n")
    
    ozon_parser = OzonParser(headless=args.headless)
    
    results = ozon_parser.parse_multiple(
        query=args.query,
        skus=skus,
        repeat=args.repeat,
        interval=args.interval
    )
    
    print(f"\n{'='*60}")
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅" if result["position"] != "not_found" else "❌"
        pos = result["position"] if result["position"] != "not_found" else "not_found"
        print(f"{status} SKU {result['sku']}: позиция {pos} (запуск {result['run']})")
    
    print(f"{'='*60}")
    print("✅ Парсинг завершен!")

if __name__ == "__main__":
    main() 