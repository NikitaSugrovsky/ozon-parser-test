import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class OzonParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def parse(self, query, sku):
        url = f"https://www.ozon.ru/search/?text={query}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            return {"error": "Ошибка запроса", "status": response.status_code}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('a', href=True)
        position = None
        
        for i, item in enumerate(items[:100], 1):
            if f'/product/{sku}' in item.get('href', ''):
                position = i
                break
        
        return {
            "query": query,
            "sku": sku,
            "position": position or "not_found",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    parser = OzonParser()
    result = parser.parse("наушники", "3418469702")
    print(json.dumps(result, ensure_ascii=False, indent=2))
