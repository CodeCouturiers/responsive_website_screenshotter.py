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


@dataclass
class Viewport:
    width: int
    height: int
    name: str


class WebsiteScreenshotter:
    VIEWPORTS = [
        # Desktop (Most common desktop resolutions in 2024)
        Viewport(1920, 1080, "desktop-fhd"),  # Full HD
        Viewport(2560, 1440, "desktop-2k"),  # 2K QHD
        Viewport(3840, 2160, "desktop-4k"),  # 4K UHD
        Viewport(1366, 768, "desktop-laptop"),  # Common laptop
        Viewport(1536, 864, "desktop-laptop-hd"),  # HD+ Laptop

        # Apple Devices
        Viewport(2880, 1800, "macbook-pro-15"),  # MacBook Pro 15"
        Viewport(2560, 1600, "macbook-pro-13"),  # MacBook Pro 13"
        Viewport(2732, 2048, "ipad-pro-12.9"),  # iPad Pro 12.9"
        Viewport(2388, 1668, "ipad-pro-11"),  # iPad Pro 11"
        Viewport(2048, 1536, "ipad-10.9"),  # iPad Air/iPad 10.9"

        # Popular Android Tablets
        Viewport(2560, 1600, "samsung-tab-s9"),  # Samsung Tab S9
        Viewport(2000, 1200, "lenovo-tab-p12"),  # Lenovo Tab P12
        Viewport(2160, 1620, "xiaomi-pad-6"),  # Xiaomi Pad 6

        # Popular Smartphones
        Viewport(1290, 2796, "iphone-15-pro-max"),  # iPhone 15 Pro Max
        Viewport(1179, 2556, "iphone-15-pro"),  # iPhone 15 Pro
        Viewport(1170, 2532, "iphone-15"),  # iPhone 15
        Viewport(1440, 3088, "samsung-s24-ultra"),  # Samsung S24 Ultra
        Viewport(1080, 2340, "samsung-s24"),  # Samsung S24
        Viewport(1080, 2400, "pixel-8-pro"),  # Google Pixel 8 Pro
        Viewport(1080, 2400, "oneplus-12")  # OnePlus 12
    ]
    def __init__(self, output_dir: str, max_workers: int = 3):
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.setup_logging()
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_chrome_options(self) -> Options:
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

    def capture_screenshot(self, url: str, viewport: Viewport, retry_count: int = 3) -> Dict:
        for attempt in range(retry_count):
            driver = None
            try:
                driver = webdriver.Chrome(options=self.get_chrome_options())
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)

                # Set viewport size with additional padding
                driver.set_window_size(viewport.width + 100, viewport.height + 100)
                driver.get(url)

                # Wait for page load
                wait = WebDriverWait(driver, 20)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # Additional wait for dynamic content
                time.sleep(2)

                # Reset to exact viewport size before screenshot
                driver.set_window_size(viewport.width, viewport.height)
                time.sleep(1)

                screenshot_path = os.path.join(
                    self.output_dir,
                    f"screenshot-{viewport.name}.png"
                )
                driver.save_screenshot(screenshot_path)

                return {
                    "name": viewport.name,
                    "path": screenshot_path,
                    "width": viewport.width,
                    "height": viewport.height
                }

            except WebDriverException as e:
                logging.warning(f"Attempt {attempt + 1} failed for {viewport.name}: {str(e)}")
                if attempt == retry_count - 1:
                    logging.error(f"Failed to capture {viewport.name} after {retry_count} attempts")
                    return None
                time.sleep(2)  # Wait before retry

            except Exception as e:
                logging.error(f"Unexpected error capturing {viewport.name}: {str(e)}")
                return None

            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

    def create_collage(self, screenshots: List[Dict]) -> None:
        try:
            # Filter out None values
            screenshots = [s for s in screenshots if s is not None]

            if not screenshots:
                logging.error("No valid screenshots to create collage")
                return

            collage_width = 3600
            collage_height = 2400
            collage = Image.new('RGB', (collage_width, collage_height), 'white')
            draw = ImageDraw.Draw(collage)

            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except OSError:
                font = ImageFont.load_default()

            for i, screenshot in enumerate(screenshots):
                row = i // 3
                col = i % 3
                x = col * 1200 + 100
                y = row * 800 + 50

                try:
                    with Image.open(screenshot["path"]) as img:
                        scale = min(
                            1000 / screenshot["width"],
                            700 / screenshot["height"]
                        )
                        new_width = int(screenshot["width"] * scale)
                        new_height = int(screenshot["height"] * scale)
                        img_resized = img.resize(
                            (new_width, new_height),
                            Image.Resampling.LANCZOS
                        )
                        collage.paste(img_resized, (x, y))

                        text = f"{screenshot['name']} ({screenshot['width']}x{screenshot['height']})"
                        draw.text((x, y + new_height + 10), text, fill='#333333', font=font)
                except Exception as e:
                    logging.error(f"Error processing image {screenshot['name']}: {str(e)}")
                    continue

            collage_path = os.path.join(
                self.output_dir,
                "website-responsive-collage.png"
            )
            collage.save(collage_path, optimize=True)
            logging.info(f"Collage saved to: {collage_path}")

        except Exception as e:
            logging.error(f"Error creating collage: {str(e)}")

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
            self.create_collage(screenshots)
            logging.info("Process completed successfully")
        else:
            logging.error("No screenshots were captured successfully")


def main():
    OUTPUT_DIR = r"C:\Users\user\Downloads\testScript"
    URL = "https://www.wikipedia.org/"  # Your target URL
    MAX_WORKERS = 3

    screenshotter = WebsiteScreenshotter(
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS
    )
    screenshotter.process_website(URL)


if __name__ == "__main__":
    main()
