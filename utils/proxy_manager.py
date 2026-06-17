import random
from typing import Optional, List
from config import Config

class ProxyManager:
    \"\"\"Менеджер прокси с ротацией\"\"\"
    
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self._load_proxies()
    
    def _load_proxies(self):
        \"\"\"Загрузка прокси из конфигурации\"\"\"
        if Config.PROXY_HTTP:
            self.proxies.append({
                'http': Config.PROXY_HTTP,
                'https': Config.PROXY_HTTPS or Config.PROXY_HTTP
            })
        
        if Config.PROXY_SOCKS5:
            self.proxies.append({
                'all': Config.PROXY_SOCKS5
            })
    
    def get_next_proxy(self) -> Optional[dict]:
        \"\"\"Получение следующего прокси (ротация)\"\"\"
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random_proxy(self) -> Optional[dict]:
        \"\"\"Получение случайного прокси\"\"\"
        if not self.proxies:
            return None
        return random.choice(self.proxies)
