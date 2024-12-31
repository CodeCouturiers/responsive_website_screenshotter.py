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
    dpr: float
    user_agent: str


class WebsiteScreenshotter:
    VIEWPORTS = [
        # Desktop (Most common desktop resolutions in 2024)
        Viewport(1920, 1080, "desktop-fhd", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(2560, 1440, "desktop-2k", 1.5,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(3840, 2160, "desktop-4k", 2.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1366, 768, "desktop-laptop", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1536, 864, "desktop-laptop-hd", 1.25,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),

        # Apple Devices
        Viewport(2880, 1800, "macbook-pro-15", 2.0,
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        Viewport(2560, 1600, "macbook-pro-13", 2.0,
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        Viewport(2732, 2048, "ipad-pro-12.9", 2.0,
                 "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        Viewport(2388, 1668, "ipad-pro-11", 2.0,
                 "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        Viewport(2048, 1536, "ipad-10.9", 2.0,
                 "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),

        # Popular Android Tablets
        Viewport(2560, 1600, "samsung-tab-s9", 1.5,
                 "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(2000, 1200, "lenovo-tab-p12", 1.5,
                 "Mozilla/5.0 (Linux; Android 13; Tab P12 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(2160, 1620, "xiaomi-pad-6", 1.5,
                 "Mozilla/5.0 (Linux; Android 13; 23043RP34G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),

        # Popular Smartphones
        Viewport(1290, 2796, "iphone-15-pro-max", 3.0,
                 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        Viewport(1179, 2556, "iphone-15-pro", 3.0,
                 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        Viewport(1170, 2532, "iphone-15", 3.0,
                 "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),
        Viewport(1440, 3088, "samsung-s24-ultra", 3.0,
                 "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2340, "samsung-s24", 2.5,
                 "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "pixel-8-pro", 2.5,
                 "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),
        Viewport(1080, 2400, "oneplus-12", 2.5,
                 "Mozilla/5.0 (Linux; Android 14; CPH2573) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36")
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
                options = self.get_chrome_options()
                options.add_argument(f'user-agent={viewport.user_agent}')
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)

                # Calculate physical pixels
                physical_width = int(viewport.width / viewport.dpr)
                physical_height = int(viewport.height / viewport.dpr)

                # Set viewport size with additional padding
                driver.set_window_size(physical_width + 100, physical_height + 100)

                # Set device pixel ratio and mobile emulation
                driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                    'width': physical_width,
                    'height': physical_height,
                    'deviceScaleFactor': viewport.dpr,
                    'mobile': 'mobile' in viewport.name.lower() or 'iphone' in viewport.name.lower()
                })

                driver.get(url)

                # Wait for page load
                wait = WebDriverWait(driver, 20)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # Additional wait for dynamic content
                time.sleep(2)

                # Reset to exact viewport size before screenshot
                driver.set_window_size(physical_width, physical_height)
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
                    "height": viewport.height,
                    "dpr": viewport.dpr,
                    "physical_width": physical_width,
                    "physical_height": physical_height,
                    "user_agent": viewport.user_agent
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

                        text = f"{screenshot['name']} ({screenshot['physical_width']}x{screenshot['physical_height']}, DPR: {screenshot['dpr']}x)"
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
    MAX_WORKERS = 8

    screenshotter = WebsiteScreenshotter(
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS
    )
    screenshotter.process_website(URL)


if __name__ == "__main__":
    main()
