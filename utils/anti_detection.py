import random
import time
from typing import List
from playwright.sync_api import Page

class AntiDetection:
    \"\"\"Класс для эмуляции человеческого поведения\"\"\"
    
    @staticmethod
    def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        \"\"\"Случайная задержка между действиями\"\"\"
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def human_scroll(page: Page):
        \"\"\"Эмуляция скроллинга человеком\"\"\"
        for i in range(3):
            page.mouse.wheel(0, random.randint(200, 500))
            time.sleep(random.uniform(0.5, 1.5))
        
        if random.random() < 0.3:
            page.mouse.wheel(0, -random.randint(100, 300))
            time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def random_mouse_movement(page: Page):
        \"\"\"Случайное движение мышью\"\"\"
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    def get_random_user_agent() -> str:
        \"\"\"Получение случайного User-Agent\"\"\"
        from config import Config
        return random.choice(Config.USER_AGENTS)
