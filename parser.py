from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime

class OzonParser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
    
    def parse(self, query, sku):
        url = f"https://www.ozon.ru/search/?text={query}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-widget="searchResultsV2"]'))
            )
            
            items = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"]')
            position = None
            
            for i, item in enumerate(items[:100], 1):
                href = item.get_attribute('href')
                if href and f'/product/{sku}' in href:
                    position = i
                    break
            
            return {
                "query": query,
                "sku": sku,
                "position": position or "not_found",
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self.driver.quit()

if __name__ == "__main__":
    parser = OzonParser()
    result = parser.parse("наушники", "3418469702")
    print(json.dumps(result, ensure_ascii=False, indent=2))
