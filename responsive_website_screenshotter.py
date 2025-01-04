from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont
import logging
import os
from typing import List, Dict
from dataclasses import dataclass
import time
from selenium.common.exceptions import WebDriverException
from PIL import ImageFilter


@dataclass
class Viewport:
    width: int
    height: int
    name: str
    dpr: float
    user_agent: str


class WebsiteScreenshotter:
    VIEWPORTS = [
        # # Presentation & Portfolio Displays
        # Viewport(1440, 1024, "presentation-standard", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1680, 1050, "presentation-wide", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1200, 900, "dribbble-shot", 2.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1600, 1200, "behance-project", 2.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        #
        # # Common Design Presentation Formats
        # Viewport(1280, 720, "hd-preview", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1920, 1080, "fullhd-preview", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        #
        # # Popular Aspect Ratios
        # Viewport(1500, 1000, "3-2-ratio", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1600, 900, "16-9-ratio", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        #
        # Viewport(2560, 1600, "macbook-air-15", 2.0,
        #          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        # Viewport(2304, 1440, "macbook-air-13", 2.0,
        #          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        #
        # Viewport(2360, 1640, "ipad-air-5", 2.0,
        #          "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # Viewport(1080, 2340, "samsung-a54", 2.5,
        #          "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        #
        # # Desktop (Most common desktop resolutions in 2024)
        # Viewport(1920, 1080, "desktop-fhd", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(2560, 1440, "desktop-2k", 1.5,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(3840, 2160, "desktop-4k", 2.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1366, 768, "desktop-laptop", 1.0,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(1536, 864, "desktop-laptop-hd", 1.25,
        #          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        #
        # # Apple Devices
        # Viewport(2880, 1800, "macbook-pro-15", 2.0,
        #          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        # Viewport(2560, 1600, "macbook-pro-13", 2.0,
        #          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        # Viewport(2732, 2048, "ipad-pro-12.9", 2.0,
        #          "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(2388, 1668, "ipad-pro-11", 2.0,
        #          "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(2048, 1536, "ipad-10.9", 2.0,
        #          "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # # Popular Android Tablets
        # Viewport(2560, 1600, "samsung-tab-s9", 1.5,
        #          "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(2000, 1200, "lenovo-tab-p12", 1.5,
        #          "Mozilla/5.0 (Linux; Android 13; Tab P12 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        # Viewport(2160, 1620, "xiaomi-pad-6", 1.5,
        #          "Mozilla/5.0 (Linux; Android 13; 23043RP34G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        #
        # # Modern iPhones (2024-2023)
        # Viewport(1290, 2796, "iphone-15-pro-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1179, 2556, "iphone-15-pro", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1179, 2556, "iphone-15-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-15", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 14 Series (2022-2023)
        # Viewport(1290, 2796, "iphone-14-pro-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1179, 2556, "iphone-14-pro", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1284, 2778, "iphone-14-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-14", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 13 Series (2021-2022)
        # Viewport(1284, 2778, "iphone-13-pro-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-13-pro", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-13", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1080, 2340, "iphone-13-mini", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 12 Series (2020-2021)
        # Viewport(1284, 2778, "iphone-12-pro-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-12-pro", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1170, 2532, "iphone-12", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        # Viewport(1080, 2340, "iphone-12-mini", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 11 Series (2019-2020)
        # Viewport(1242, 2688, "iphone-11-pro-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        # Viewport(1125, 2436, "iphone-11-pro", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        # Viewport(828, 1792, "iphone-11", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone XS/XR Series (2018-2019)
        # Viewport(1242, 2688, "iphone-xs-max", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        # Viewport(1125, 2436, "iphone-xs", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        # Viewport(828, 1792, "iphone-xr", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone X (2017-2018)
        # Viewport(1125, 2436, "iphone-x", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 8 Series (2017)
        # Viewport(1080, 1920, "iphone-8-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8 Mobile/15E148 Safari/604.1"),
        # Viewport(750, 1334, "iphone-8", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 7 Series (2016)
        # Viewport(1080, 1920, "iphone-7-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8 Mobile/15E148 Safari/604.1"),
        # Viewport(750, 1334, "iphone-7", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.8 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 6 Series (2014-2015)
        # Viewport(1080, 1920, "iphone-6s-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1"),
        # Viewport(750, 1334, "iphone-6s", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1"),
        # Viewport(1080, 1920, "iphone-6-plus", 3.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1"),
        # Viewport(750, 1334, "iphone-6", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1"),
        #
        # # iPhone 5 Series (2012-2013)
        # Viewport(640, 1136, "iphone-5s", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.5.7 Mobile/15E148 Safari/604.1"),
        # Viewport(640, 1136, "iphone-5c", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.3.3 Mobile/14G60 Safari/602.1"),
        # Viewport(640, 1136, "iphone-5", 2.0,
        #          "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.3.3 Mobile/14G60 Safari/602.1"),

        # POCO Phones (2024-2023)
        Viewport(1220, 2712, "poco-x6-pro", 3.0,
                 "Mozilla/5.0 (Linux; Android 14; 23113RKC6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-x6", 2.5,
                 "Mozilla/5.0 (Linux; Android 14; 23122PCD1G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2460, "poco-m6-pro", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 23053RN02A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-m6", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 23053RN02A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-m5s", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 22031116BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-f5-pro", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 23013PC75G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-f5", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 23049PCD8G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1220, 2712, "poco-x5-pro", 3.0,
                 "Mozilla/5.0 (Linux; Android 13; 22101320G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "poco-x5", 2.5,
                 "Mozilla/5.0 (Linux; Android 13; 22111317PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),

        # # Popular Smartphones
        # Viewport(1440, 3088, "samsung-s24-ultra", 3.0,
        #          "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        # Viewport(1080, 2340, "samsung-s24", 2.5,
        #          "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        # Viewport(1080, 2400, "pixel-8-pro", 2.5,
        #          "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        # Viewport(1080, 2400, "oneplus-12", 2.5,
        #          "Mozilla/5.0 (Linux; Android 14; CPH2573) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36")
    ]
    def __init__(self, output_dir: str, max_workers: int = 3, simulate_browser_ui: bool = True):
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.simulate_browser_ui = simulate_browser_ui

        self.setup_logging()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create temp directory for checks
        self.temp_dir = os.path.join(output_dir, 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_chrome_options(self) -> Options:
        options = self.get_base_chrome_options()
        options.add_argument("--disable-web-security")  # Handle CORS in dev
        options.add_argument("--allow-insecure-localhost")  # Local dev servers
        return options

    def get_base_chrome_options(self) -> Options:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-smooth-scrolling")
        options.page_load_strategy = 'eager'
        return options

    def wait_for_page_load(self, driver: webdriver.Chrome, viewport: Viewport) -> None:
        """Enhanced page load detection"""
        wait = WebDriverWait(driver, 30)

        # Wait for basic DOM content
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Wait for complete page load
        driver.execute_script("""
            return new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    // Additional check for dynamic content
                    setTimeout(() => {
                        const content = document.body.innerHTML;
                        if (content && content.length > 100) {
                            resolve();
                        } else {
                            resolve('empty');
                        }
                    }, 1000);
                } else {
                    window.addEventListener('load', () => {
                        setTimeout(resolve, 1000);
                    });
                    setTimeout(() => resolve('timeout'), 5000);
                }
            });
        """)

    def inject_hydration_handling(self, driver: webdriver.Chrome) -> None:
        """Handle framework-specific elements and styling safely"""
        driver.execute_script("""
            // Safely check for frameworks
            try {
                // Handle React suspense boundaries if present
                document.querySelectorAll('[data-reactroot]').forEach(element => {
                    if (element.innerHTML.includes('loading')) {
                        element.style.visibility = 'visible';
                    }
                });

                // Ensure all styles are loaded
                const styleSheets = Array.from(document.styleSheets);
                styleSheets.forEach(sheet => {
                    if (sheet.href) {
                        const link = document.createElement('link');
                        link.rel = 'stylesheet';
                        link.href = sheet.href;
                        document.head.appendChild(link);
                    }
                });
            } catch (e) {
                // Ignore errors for non-framework sites
                console.log('Framework-specific handling skipped');
            }
        """)

    def check_screenshot_content(self, image_path: str) -> bool:
        """
        Проверяет скриншот на наличие реального контента
        Возвращает True если контент обнаружен, False если скриншот пустой/белый
        """
        with Image.open(image_path) as img:
            # Get UI heights for cropping
            browser_ui_height = {
                'search_bar': 56,
                'bottom_nav': 48
            }

            # Конвертируем в RGB если изображение в другом формате
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Crop out UI areas for content check
            content_area = img.crop((0, browser_ui_height['search_bar'],
                                     img.width,
                                     img.height - browser_ui_height['bottom_nav']))

            # Уменьшаем изображение для быстрого анализа
            thumb = content_area.resize((100, 100))

            # Получаем все цвета и их количество
            pixels = thumb.getcolors(10000)
            if not pixels:
                return False

            total_pixels = sum(count for count, _ in pixels)

            # Проверяем белые и почти белые пиксели
            white_pixels = sum(
                count for count, color in pixels
                if all(c > 250 for c in color)  # Немного строже для белого
            )

            # Проверяем очень светлые пиксели
            very_light_pixels = sum(
                count for count, color in pixels
                if all(c > 240 for c in color)
            )

            # Проверяем наличие темных пикселей (текст, границы и т.д.)
            dark_pixels = sum(
                count for count, color in pixels
                if any(c < 200 for c in color)
            )

            # Вычисляем процентные соотношения
            white_ratio = white_pixels / total_pixels
            very_light_ratio = very_light_pixels / total_pixels
            dark_ratio = dark_pixels / total_pixels

            # Комплексная проверка контента:
            # 1. Если более 98% чисто белых пикселей - вероятно пустой экран
            if white_ratio > 0.98:
                return False

            # 2. Если более 95% очень светлых пикселей И менее 1% темных - вероятно пустой
            if very_light_ratio > 0.95 and dark_ratio < 0.01:
                return False

            # 3. Если есть заметное количество темных пикселей - вероятно есть контент
            if dark_ratio > 0.02:  # Более 2% темных пикселей
                return True

            # По умолчанию считаем что контент есть
            return True

    def capture_screenshot(self, url: str, viewport: Viewport, retry_count: int = 3) -> Dict:
        for attempt in range(retry_count):
            driver = None
            temp_screenshot = None
            try:
                options = self.get_chrome_options()
                options.add_argument(f'user-agent={viewport.user_agent}')
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)

                # Calculate base physical pixels
                physical_width = int(viewport.width / viewport.dpr)
                physical_height = int(viewport.height / viewport.dpr)

                # Add UI heights in actual pixels (not scaled)
                browser_ui_height = {
                    'status_bar': 20 if 'iphone' in viewport.name.lower() else 24,
                    'search_bar': 56,
                    'bottom_nav': 48
                }
                total_ui_height = browser_ui_height['status_bar'] + browser_ui_height['search_bar'] + browser_ui_height[
                    'bottom_nav']

                # Set viewport size
                driver.set_window_size(physical_width, physical_height)

                # Configure device metrics
                driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                    'width': physical_width,
                    'height': physical_height,
                    'deviceScaleFactor': viewport.dpr,
                    'mobile': 'mobile' in viewport.name.lower() or 'iphone' in viewport.name.lower(),
                    'screenOrientation': {
                        'type': 'portraitPrimary',
                        'angle': 0
                    }
                })

                driver.get(url)

                # Enhanced waiting for modern frameworks
                self.wait_for_page_load(driver, viewport)
                self.inject_hydration_handling(driver)

                # Inject browser UI elements
                driver.execute_script("""
                   // Status bar height based on platform
                   const statusBarHeight = navigator.userAgent.toLowerCase().includes('iphone') ? '20px' : '24px';
                   const searchBarHeight = '56px';
                   const bottomNavHeight = '48px';

                   // Create status bar
                   const statusBar = document.createElement('div');
                   statusBar.style.cssText = `
                       position: fixed;
                       top: 0;
                       left: 0;
                       right: 0;
                       height: ${statusBarHeight};
                       background: #000000;
                       z-index: 10000;
                       display: flex;
                       justify-content: space-between;
                       align-items: center;
                       padding: 0 16px;
                       color: #fff;
                       font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                       font-size: 12px;
                   `;

                   // Left side of status bar (time)
                   const statusBarLeft = document.createElement('div');
                   statusBarLeft.textContent = '5:52';

                   // Center of status bar (notch area/camera)
                   const statusBarCenter = document.createElement('div');
                   statusBarCenter.style.cssText = `
                       width: 80px;
                       height: ${statusBarHeight};
                       background: #000000;
                   `;

                   // Right side of status bar (battery, wifi, etc)
                   const statusBarRight = document.createElement('div');
                   statusBarRight.style.cssText = `
                       display: flex;
                       gap: 4px;
                       align-items: center;
                   `;
                   statusBarRight.innerHTML = '🔋 74% 📶 ⚡';

                   // Create browser UI container
                   const browserUI = document.createElement('div');
                   browserUI.style.cssText = `
                       position: fixed;
                       top: ${statusBarHeight};
                       left: 0;
                       right: 0;
                       height: ${searchBarHeight};
                       background: #2A2A2A;
                       z-index: 9999;
                       display: flex;
                       align-items: center;
                       padding: 0 16px;
                       font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                   `;

                   // Create browser controls (left)
                   const browserControls = document.createElement('div');
                   browserControls.style.cssText = `
                       display: flex;
                       align-items: center;
                       gap: 8px;
                   `;

                   // Add lock icon
                   const lockIcon = document.createElement('span');
                   lockIcon.innerHTML = '🔒';
                   lockIcon.style.fontSize = '16px';

                   // Create search bar
                   const searchBar = document.createElement('div');
                   searchBar.style.cssText = `
                       flex: 1;
                       height: 36px;
                       background: #3A3A3A;
                       border-radius: 18px;
                       margin: 0 8px;
                       display: flex;
                       align-items: center;
                       padding: 0 16px;
                       color: #fff;
                       font-size: 14px;
                   `;
                   searchBar.textContent = window.location.hostname;

                   // Create browser actions (right)
                   const browserActions = document.createElement('div');
                   browserActions.style.cssText = `
                       display: flex;
                       align-items: center;
                       gap: 16px;
                   `;
                   browserActions.innerHTML = '⋮';

                   // Create bottom navigation
                   const bottomNav = document.createElement('div');
                   bottomNav.style.cssText = `
                       position: fixed;
                       bottom: 0;
                       left: 0;
                       right: 0;
                       height: ${bottomNavHeight};
                       background: #000;
                       display: flex;
                       justify-content: space-around;
                       align-items: center;
                       z-index: 9999;
                       padding: 0 16px;
                   `;

                   // Add navigation buttons
                   const navButtons = ['←', '→', '↓', '⌂', '⊡'];
                   navButtons.forEach(button => {
                       const navButton = document.createElement('button');
                       navButton.style.cssText = `
                           background: none;
                           border: none;
                           color: #fff;
                           font-size: 20px;
                           padding: 8px;
                           cursor: pointer;
                       `;
                       navButton.textContent = button;
                       bottomNav.appendChild(navButton);
                   });

                   // Assemble browser UI
                   browserControls.appendChild(lockIcon);
                   browserUI.appendChild(browserControls);
                   browserUI.appendChild(searchBar);
                   browserUI.appendChild(browserActions);

                   // Assemble status bar
                   statusBar.appendChild(statusBarLeft);
                   statusBar.appendChild(statusBarCenter);
                   statusBar.appendChild(statusBarRight);

                   // Wrap all existing body content in a container
                   const content = document.createElement('div');
                   while (document.body.firstChild) {
                       content.appendChild(document.body.firstChild);
                   }
                   document.body.appendChild(content);

                   // Add UI elements to page
                   document.body.appendChild(statusBar);
                   document.body.appendChild(browserUI);
                   document.body.appendChild(bottomNav);

                   // Position content below UI
                   content.style.cssText = `
                       position: relative;
                       top: calc(${statusBarHeight} + ${searchBarHeight});
                       margin-bottom: calc(${bottomNavHeight} + 20px);
                       min-height: calc(100vh - ${statusBarHeight} - ${searchBarHeight} - ${bottomNavHeight});
                   `;

                   // Hide scrollbars
                   document.documentElement.style.overflow = 'hidden';
                   document.body.style.overflow = 'hidden';

                   // Add CSS for Firefox and other browsers
                   const style = document.createElement('style');
                   style.textContent = `
                       * {
                           scrollbar-width: none !important;
                           -ms-overflow-style: none !important;
                       }
                       ::-webkit-scrollbar {
                           display: none !important;
                       }
                   `;
                   document.head.appendChild(style);

                   // Force layout recalculation
                   document.body.offsetHeight;
               """)

                # Wait for any remaining dynamic content
                time.sleep(3)

                # Reset to exact viewport size before screenshot
                driver.set_window_size(physical_width, physical_height)
                time.sleep(1)

                # Make temporary screenshot for checking
                temp_screenshot = os.path.join(
                    self.temp_dir,
                    f"temp_{viewport.name}_{attempt}.png"
                )
                driver.save_screenshot(temp_screenshot)

                # Check content
                if not self.check_screenshot_content(temp_screenshot):
                    raise WebDriverException(
                        f"Empty or blank screen detected for {viewport.name}"
                    )

                # If check passed, save final screenshot
                final_screenshot = os.path.join(
                    self.output_dir,
                    f"screenshot-{viewport.name}.png"
                )
                os.replace(temp_screenshot, final_screenshot)

                return {
                    "name": viewport.name,
                    "path": final_screenshot,
                    "width": viewport.width,
                    "height": viewport.height,
                    "dpr": viewport.dpr,
                    "physical_width": physical_width,
                    "physical_height": physical_height,
                    "user_agent": viewport.user_agent
                }

            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed for {viewport.name}: {str(e)}")
                if attempt == retry_count - 1:
                    logging.error(f"Failed to capture {viewport.name} after {retry_count} attempts")
                    return None
                time.sleep(3)

            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    # Clean up temp file
                    if temp_screenshot and os.path.exists(temp_screenshot):
                        try:
                            os.remove(temp_screenshot)
                        except:
                            pass

    def verify_page_content(self, driver: webdriver.Chrome) -> bool:
        """Verify that the page has loaded meaningful content"""
        try:
            # Check for minimum content
            content_check = driver.execute_script("""
                return {
                    elementCount: document.querySelectorAll('*').length,
                    textLength: document.body.textContent.trim().length,
                    hasImages: document.querySelectorAll('img').length > 0,
                    hasContent: document.body.innerHTML.length > 100
                }
            """)

            # Verify minimum requirements
            return (content_check['elementCount'] > 10 and
                    content_check['textLength'] > 50 and
                    (content_check['hasImages'] or content_check['hasContent']))
        except:
            return False

    def create_category_collages(self, screenshots: List[Dict]) -> None:
        try:
            screenshots = [s for s in screenshots if s is not None]
            if not screenshots:
                logging.error("No valid screenshots to create collages")
                return

            # Device categorization and naming
            categories = {
                'Desktop_Monitors': {
                    'title': 'Desktop Monitors',
                    'subtitle': 'Modern Display Resolutions',
                    'devices': ['desktop-fhd', 'desktop-2k', 'desktop-4k', 'desktop-laptop', 'desktop-laptop-hd']
                },
                'MacBooks': {
                    'title': 'MacBook Collection',
                    'subtitle': 'Pro & Air Retina Displays',
                    'devices': ['macbook-pro-15', 'macbook-pro-13', 'macbook-air-15', 'macbook-air-13']
                },
                'iPads': {
                    'title': 'iPad Collection',
                    'subtitle': 'Pro & Air Liquid Retina',
                    'devices': ['ipad-pro-12.9', 'ipad-pro-11', 'ipad-10.9', 'ipad-air-5']
                },
                'Android_Tablets': {
                    'title': 'Android Tablets',
                    'subtitle': 'Premium Display Gallery',
                    'devices': ['samsung-tab-s9', 'lenovo-tab-p12', 'xiaomi-pad-6']
                },
                'Modern_iPhones': {
                    'title': 'Modern iPhones (2024-2023)',
                    'subtitle': 'iPhone 15 Series - Super Retina XDR Displays',
                    'devices': ['iphone-15-pro-max', 'iphone-15-pro', 'iphone-15-plus', 'iphone-15']
                },
                'iPhones_2022_2023': {
                    'title': 'iPhones 2022-2023',
                    'subtitle': 'iPhone 14 Series - Super Retina XDR Displays',
                    'devices': ['iphone-14-pro-max', 'iphone-14-pro', 'iphone-14-plus', 'iphone-14']
                },
                'iPhones_2021_2022': {
                    'title': 'iPhones 2021-2022',
                    'subtitle': 'iPhone 13 Series - Super Retina XDR Displays',
                    'devices': ['iphone-13-pro-max', 'iphone-13-pro', 'iphone-13', 'iphone-13-mini']
                },
                'iPhones_2020_2021': {
                    'title': 'iPhones 2020-2021',
                    'subtitle': 'iPhone 12 Series - Super Retina XDR Displays',
                    'devices': ['iphone-12-pro-max', 'iphone-12-pro', 'iphone-12', 'iphone-12-mini']
                },
                'iPhones_2019_2020': {
                    'title': 'iPhones 2019-2020',
                    'subtitle': 'iPhone 11 Series - Liquid Retina HD & Super Retina XDR',
                    'devices': ['iphone-11-pro-max', 'iphone-11-pro', 'iphone-11']
                },
                'iPhones_2018_2019': {
                    'title': 'iPhones 2018-2019',
                    'subtitle': 'iPhone XS/XR Series - Super Retina HD & Liquid Retina HD',
                    'devices': ['iphone-xs-max', 'iphone-xs', 'iphone-xr']
                },
                'iPhone_X_2017': {
                    'title': 'iPhone X (2017)',
                    'subtitle': 'Super Retina HD Display',
                    'devices': ['iphone-x']
                },
                'iPhones_2017': {
                    'title': 'iPhone 8 Series (2017)',
                    'subtitle': 'Retina HD Displays',
                    'devices': ['iphone-8-plus', 'iphone-8']
                },
                'iPhones_2016': {
                    'title': 'iPhone 7 Series (2016)',
                    'subtitle': 'Retina HD Displays',
                    'devices': ['iphone-7-plus', 'iphone-7']
                },
                'iPhones_2014_2015': {
                    'title': 'iPhone 6 Series (2014-2015)',
                    'subtitle': 'Retina HD Displays',
                    'devices': ['iphone-6s-plus', 'iphone-6s', 'iphone-6-plus', 'iphone-6']
                },
                'iPhones_2012_2013': {
                    'title': 'iPhone 5 Series (2012-2013)',
                    'subtitle': 'Retina Displays',
                    'devices': ['iphone-5s', 'iphone-5c', 'iphone-5']
                },

                'Android_Phones': {
                    'title': 'Android Phones',
                    'subtitle': 'Flagship & Mid-Range Collection',
                    'devices': ['samsung-s24-ultra', 'samsung-s24', 'samsung-a54', 'pixel-8-pro', 'oneplus-12']
                },
                'POCO_Phones': {
                    'title': 'POCO Smartphones',
                    'subtitle': 'Latest POCO Models (2024-2023)',
                    'devices': [
                        'poco-x6-pro',
                        'poco-x6',
                        'poco-m6-pro',
                        'poco-m6',
                        'poco-m5s',
                        'poco-f5-pro',
                        'poco-f5',
                        'poco-x5-pro',
                        'poco-x5'
                    ]
                },
                'Design_Presentations': {
                    'title': 'Design Presentations',
                    'subtitle': 'Portfolio & Showcase Formats',
                    'devices': [
                        'presentation-standard',
                        'presentation-wide',
                        'dribbble-shot',
                        'behance-project',
                        'hd-preview',
                        'fullhd-preview',
                        '3-2-ratio',
                        '16-9-ratio'
                    ]
                },
            }

            # Friendly device names
            device_names = {
                # Desktop Monitors
                'desktop-fhd': 'Full HD Display',
                'desktop-2k': 'QHD Display',
                'desktop-4k': '4K UHD Display',
                'desktop-laptop': 'Standard Laptop',
                'desktop-laptop-hd': 'HD+ Laptop',

                # MacBooks
                'macbook-pro-15': 'MacBook Pro 15"',
                'macbook-pro-13': 'MacBook Pro 13"',

                # iPads
                'ipad-pro-12.9': 'iPad Pro 12.9"',
                'ipad-pro-11': 'iPad Pro 11"',
                'ipad-10.9': 'iPad Air',

                # Android Tablets
                'samsung-tab-s9': 'Galaxy Tab S9',
                'lenovo-tab-p12': 'Tab P12 Pro',
                'xiaomi-pad-6': 'Pad 6',

                # iPhone 15 Series
                'iphone-15-pro-max': 'iPhone 15 Pro Max',
                'iphone-15-pro': 'iPhone 15 Pro',
                'iphone-15-plus': 'iPhone 15 Plus',
                'iphone-15': 'iPhone 15',

                # iPhone 14 Series
                'iphone-14-pro-max': 'iPhone 14 Pro Max',
                'iphone-14-pro': 'iPhone 14 Pro',
                'iphone-14-plus': 'iPhone 14 Plus',
                'iphone-14': 'iPhone 14',

                # iPhone 13 Series
                'iphone-13-pro-max': 'iPhone 13 Pro Max',
                'iphone-13-pro': 'iPhone 13 Pro',
                'iphone-13': 'iPhone 13',
                'iphone-13-mini': 'iPhone 13 Mini',

                # iPhone 12 Series
                'iphone-12-pro-max': 'iPhone 12 Pro Max',
                'iphone-12-pro': 'iPhone 12 Pro',
                'iphone-12': 'iPhone 12',
                'iphone-12-mini': 'iPhone 12 Mini',

                # iPhone 11 Series
                'iphone-11-pro-max': 'iPhone 11 Pro Max',
                'iphone-11-pro': 'iPhone 11 Pro',
                'iphone-11': 'iPhone 11',

                # iPhone XS/XR Series
                'iphone-xs-max': 'iPhone XS Max',
                'iphone-xs': 'iPhone XS',
                'iphone-xr': 'iPhone XR',

                # iPhone X
                'iphone-x': 'iPhone X',

                # iPhone 8 Series
                'iphone-8-plus': 'iPhone 8 Plus',
                'iphone-8': 'iPhone 8',

                # iPhone 7 Series
                'iphone-7-plus': 'iPhone 7 Plus',
                'iphone-7': 'iPhone 7',

                # iPhone 6 Series
                'iphone-6s-plus': 'iPhone 6s Plus',
                'iphone-6s': 'iPhone 6s',
                'iphone-6-plus': 'iPhone 6 Plus',
                'iphone-6': 'iPhone 6',

                # iPhone 5 Series
                'iphone-5s': 'iPhone 5s',
                'iphone-5c': 'iPhone 5c',
                'iphone-5': 'iPhone 5',

                # POCO Phones
                'poco-x6-pro': 'POCO X6 Pro 5G',
                'poco-x6': 'POCO X6 5G',
                'poco-m6-pro': 'POCO M6 Pro 5G',
                'poco-m6': 'POCO M6',
                'poco-m5s': 'POCO M5s',
                'poco-f5-pro': 'POCO F5 Pro 5G',
                'poco-f5': 'POCO F5 5G',
                'poco-x5-pro': 'POCO X5 Pro 5G',
                'poco-x5': 'POCO X5 5G',

                # Android Phones
                'samsung-s24-ultra': 'Galaxy S24 Ultra',
                'samsung-s24': 'Galaxy S24',
                'pixel-8-pro': 'Pixel 8 Pro',
                'oneplus-12': 'OnePlus 12',

                'macbook-air-15': 'MacBook Air 15"',
                'macbook-air-13': 'MacBook Air 13"',
                'ipad-air-5': 'iPad Air 5',
                'samsung-a54': 'Galaxy A54 5G',

                'presentation-standard': 'Standard Presentation',
                'presentation-wide': 'Wide Presentation',
                'dribbble-shot': 'Dribbble Shot',
                'behance-project': 'Behance Project',
                'hd-preview': 'HD Preview',
                'fullhd-preview': 'Full HD Preview',
                '3-2-ratio': '3:2 Aspect Ratio',
                '16-9-ratio': '16:9 Aspect Ratio',
            }

            # Behance-inspired design system
            DESIGN = {
                'colors': {
                    'background': '#FFFFFF',  # Clean white background like Behance
                    'card': '#FFFFFF',
                    'text': {
                        'primary': '#000000',  # More contrasting black for titles
                        'secondary': '#444444',  # Dark grey for subtitles
                        'tertiary': '#666666'  # Grey for other text
                    },
                    'border': '#EAEAEA',
                    'shadow': (0, 0, 0, 15)  # Slightly reduced shadow
                },
                'spacing': {
                    'margin': 100,  # Increased margins
                    'gutter': 40,
                    'header': 300,  # More space for header
                    'card_padding': 40
                },
                'typography': {
                    'title': 96,  # Larger title size
                    'subtitle': 32,  # Larger subtitle size
                    'device_name': 24,
                    'specs': 16
                }
            }

            # Font configuration with system fallbacks
            import platform
            system = platform.system().lower()

            FONTS = {
                'windows': {
                    'regular': 'C:/Windows/Fonts/segoeui.ttf',
                    'bold': 'C:/Windows/Fonts/segoeuib.ttf',
                    'light': 'C:/Windows/Fonts/segoeuil.ttf'  # Added light variant
                },
                'darwin': {
                    'regular': '/System/Library/Fonts/SFPro-Regular.ttf',
                    'bold': '/System/Library/Fonts/SFPro-Bold.ttf',
                    'light': '/System/Library/Fonts/SFPro-Light.ttf'
                },
                'linux': {
                    'regular': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    'light': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Light.ttf'
                }
            }

            try:
                fonts = FONTS.get(system, FONTS['windows'])
                title_font = ImageFont.truetype(fonts['light'], DESIGN['typography']['title'])  # Light weight for title
                subtitle_font = ImageFont.truetype(fonts['light'],
                                                   DESIGN['typography']['subtitle'])  # Light weight for subtitle
                device_font = ImageFont.truetype(fonts['bold'], DESIGN['typography']['device_name'])
                specs_font = ImageFont.truetype(fonts['regular'], DESIGN['typography']['specs'])
            except Exception as e:
                logging.warning(f"Font loading failed: {e}. Using default font.")
                title_font = subtitle_font = device_font = specs_font = ImageFont.load_default()

            def create_shadow(size, radius=8):
                shadow = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(shadow)
                draw.rectangle((radius, radius, size[0] - radius, size[1] - radius),
                               fill=(0, 0, 0, DESIGN['colors']['shadow'][3]))
                return shadow.filter(ImageFilter.GaussianBlur(radius))

            def draw_text(draw, pos, text, font, color, align='center', width=None):
                """
                Draw text with alignment support

                Args:
                    draw: ImageDraw object
                    pos: (x, y) position tuple
                    text: text to draw
                    font: font to use
                    color: text color
                    align: alignment ('left', 'center', 'right')
                    width: total width for alignment calculation
                """
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                x, y = pos

                if align == 'center' and width:
                    x += (width - text_width) // 2
                elif align == 'right' and width:
                    x += width - text_width

                draw.text((x, y), text, font=font, fill=color)
                return bbox[3] - bbox[1]

            # Process each category
            for category_name, category_info in categories.items():
                category_shots = [s for s in screenshots if s['name'] in category_info['devices']]
                if not category_shots:
                    continue

                # Layout calculations
                spacing = DESIGN['spacing']
                cols = min(2, len(category_shots))

                # Card dimensions
                card_width = int((3000 - (2 * spacing['margin']) - ((cols - 1) * spacing['gutter'])) / cols)
                image_width = card_width - (spacing['card_padding'] * 2)

                # Calculate maximum aspect ratio and card height
                max_ratio = max(s["height"] / s["width"] for s in category_shots)
                image_height = int(image_width * max_ratio)
                card_height = spacing['card_padding'] * 2 + image_height + 120

                # Canvas dimensions
                rows = (len(category_shots) + cols - 1) // cols
                canvas_width = spacing['margin'] * 2 + card_width * cols + spacing['gutter'] * (cols - 1)
                canvas_height = (
                        spacing['margin'] +
                        spacing['header'] +
                        (card_height * rows) +
                        (spacing['gutter'] * (rows - 1)) +
                        spacing['margin']
                )

                # Create canvas
                canvas = Image.new('RGB', (canvas_width, canvas_height), DESIGN['colors']['background'])
                draw = ImageDraw.Draw(canvas)

                # Draw header
                header_y = spacing['margin'] + 40  # Additional top padding
                title_height = draw_text(
                    draw,
                    (spacing['margin'], header_y),
                    category_info['title'].upper(),  # Title in uppercase
                    title_font,
                    DESIGN['colors']['text']['primary'],
                    'center',
                    canvas_width - (spacing['margin'] * 2)
                )

                # Draw subtitle
                subtitle_y = header_y + title_height + 30  # Increased spacing between title and subtitle
                draw_text(
                    draw,
                    (spacing['margin'], subtitle_y),
                    category_info['subtitle'],
                    subtitle_font,
                    DESIGN['colors']['text']['secondary'],
                    'center',
                    canvas_width - (spacing['margin'] * 2)
                )

                # Draw device cards
                for idx, screenshot in enumerate(category_shots):
                    row = idx // cols
                    col = idx % cols

                    x = spacing['margin'] + (card_width + spacing['gutter']) * col
                    y = spacing['margin'] + spacing['header'] + (card_height + spacing['gutter']) * row

                    try:
                        with Image.open(screenshot["path"]) as img:
                            # Create and apply card shadow
                            shadow = create_shadow((card_width + 20, card_height + 20))
                            canvas.paste(shadow, (x - 10, y - 10), shadow)

                            # Create card background
                            card = Image.new('RGB', (card_width, card_height), DESIGN['colors']['card'])
                            canvas.paste(card, (x, y))

                            # Calculate image dimensions and position
                            display_width = image_width
                            scale = display_width / screenshot["width"]
                            display_height = int(screenshot["height"] * scale)

                            # Resize and paste screenshot
                            img_resized = img.resize(
                                (display_width, display_height),
                                Image.Resampling.LANCZOS
                            )

                            img_x = x + spacing['card_padding']
                            img_y = y + spacing['card_padding']
                            canvas.paste(img_resized, (img_x, img_y))

                            # Draw device information
                            info_y = img_y + display_height + 25

                            # Device name
                            device_name = device_names.get(screenshot['name'], screenshot['name'])
                            draw_text(
                                draw,
                                (img_x, info_y),
                                device_name,
                                device_font,
                                DESIGN['colors']['text']['primary'],
                                'center',
                                display_width
                            )

                            # Technical specifications
                            specs_text = f"{screenshot['width']}×{screenshot['height']} @ {screenshot['dpr']}x"
                            draw_text(
                                draw,
                                (img_x, info_y + 35),
                                specs_text,
                                specs_font,
                                DESIGN['colors']['text']['secondary'],
                                'center',
                                display_width
                            )

                    except Exception as e:
                        logging.error(f"Error processing {screenshot['name']}: {str(e)}")
                        continue

                # Save the collage
                collage_path = os.path.join(
                    self.output_dir,
                    f"collage_{category_name}.png"
                )
                canvas.save(collage_path, optimize=True, quality=95)
                logging.info(f"Saved {category_name} collage to: {collage_path}")

        except Exception as e:
            logging.error(f"Collage creation failed: {str(e)}")

    def process_website(self, url: str) -> None:
        logging.info(f"Starting capture for: {url}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_viewport = {
                executor.submit(self.capture_screenshot, url, viewport): viewport
                for viewport in self.VIEWPORTS
            }

            screenshots = []
            for future in future_to_viewport:
                viewport = future_to_viewport[future]
                try:
                    screenshot = future.result()
                    if screenshot:
                        screenshots.append(screenshot)
                        logging.info(f"Captured {viewport.name}")
                except Exception as e:
                    logging.error(f"Error processing {viewport.name}: {str(e)}")

            if screenshots:
                # Create category collages
                self.create_category_collages(screenshots)
                logging.info("Process completed successfully")
            else:
                logging.error("No screenshots were captured successfully")


def main():
    OUTPUT_DIR = r"C:\Users\user\Downloads\testScript"  # Change this to your desired output directory
    URL = "https://splice.com/"  # Change this to your target URL
    MAX_WORKERS = 8  # Adjust based on your system's capabilities

    screenshotter = WebsiteScreenshotter(
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS
    )
    screenshotter.process_website(URL)


if __name__ == "__main__":
    main()
