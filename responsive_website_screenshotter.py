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
            # Конвертируем в RGB если изображение в другом формате
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Уменьшаем изображение для быстрого анализа
            thumb = img.resize((100, 100))

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

                # Enhanced waiting for modern frameworks
                self.wait_for_page_load(driver, viewport)
                self.inject_hydration_handling(driver)

                # Inject CSS to hide scrollbars
                driver.execute_script("""
                   document.documentElement.style.overflow = 'hidden';
                   document.body.style.overflow = 'hidden';

                   // Hide WebKit scrollbars
                   document.documentElement.style.setProperty(
                       '::-webkit-scrollbar', 
                       'display: none', 
                       'important'
                   );

                   // Add CSS for Firefox and other browsers
                   var style = document.createElement('style');
                   style.textContent = `
                       * {
                           scrollbar-width: none !important;
                           -ms-overflow-style: none !important;
                       }
                   `;
                   document.head.appendChild(style);
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

            # Define categories and device names inside the method
            categories = {
                'Desktop_Monitors': {
                    'title': 'Desktop Monitors',
                    'devices': ['desktop-fhd', 'desktop-2k', 'desktop-4k', 'desktop-laptop', 'desktop-laptop-hd']
                },
                'MacBooks': {
                    'title': 'Apple MacBooks',
                    'devices': ['macbook-pro-15', 'macbook-pro-13']
                },
                'iPads': {
                    'title': 'Apple iPads',
                    'devices': ['ipad-pro-12.9', 'ipad-pro-11', 'ipad-10.9']
                },
                'Android_Tablets': {
                    'title': 'Android Tablets',
                    'devices': ['samsung-tab-s9', 'lenovo-tab-p12', 'xiaomi-pad-6']
                },
                'iPhones': {
                    'title': 'Apple iPhones',
                    'devices': ['iphone-15-pro-max', 'iphone-15-pro', 'iphone-15']
                },
                'Android_Phones': {
                    'title': 'Android Phones',
                    'devices': ['samsung-s24-ultra', 'samsung-s24', 'pixel-8-pro', 'oneplus-12']
                }
            }

            device_names = {
                # Desktop Monitors
                'desktop-fhd': 'Full HD (1920×1080)',
                'desktop-2k': 'QHD (2560×1440)',
                'desktop-4k': '4K UHD (3840×2160)',
                'desktop-laptop': 'Laptop (1366×768)',
                'desktop-laptop-hd': 'Laptop HD+ (1536×864)',

                # MacBooks
                'macbook-pro-15': 'MacBook Pro 15" (2880×1800)',
                'macbook-pro-13': 'MacBook Pro 13" (2560×1600)',

                # iPads
                'ipad-pro-12.9': 'iPad Pro 12.9" (2732×2048)',
                'ipad-pro-11': 'iPad Pro 11" (2388×1668)',
                'ipad-10.9': 'iPad Air 10.9" (2048×1536)',

                # Android Tablets
                'samsung-tab-s9': 'Samsung Tab S9 (2560×1600)',
                'lenovo-tab-p12': 'Lenovo Tab P12 Pro (2000×1200)',
                'xiaomi-pad-6': 'Xiaomi Pad 6 (2160×1620)',

                # iPhones
                'iphone-15-pro-max': 'iPhone 15 Pro Max (1290×2796)',
                'iphone-15-pro': 'iPhone 15 Pro (1179×2556)',
                'iphone-15': 'iPhone 15 (1170×2532)',

                # Android Phones
                'samsung-s24-ultra': 'Samsung S24 Ultra (1440×3088)',
                'samsung-s24': 'Samsung S24 (1080×2340)',
                'pixel-8-pro': 'Google Pixel 8 Pro (1080×2400)',
                'oneplus-12': 'OnePlus 12 (1080×2400)'
            }

            # Modern color scheme
            COLORS = {
                'background': '#FFFFFF',
                'text_primary': '#191919',
                'text_secondary': '#666666',
                'accent': '#0057FF',
                'divider': '#E8E8E8'
            }

            # Enhanced typography and spacing
            TYPOGRAPHY = {
                'title_size': 48,
                'subtitle_size': 24,
                'caption_size': 16,
                'spacing': 40
            }

            # Font paths for different operating systems
            FONT_PATHS = {
                'windows': {
                    'regular': 'C:/Windows/Fonts/arial.ttf',
                    'bold': 'C:/Windows/Fonts/arialbd.ttf'
                },
                'darwin': {  # macOS
                    'regular': '/System/Library/Fonts/Helvetica.ttc',
                    'bold': '/System/Library/Fonts/Helvetica-Bold.ttf'
                },
                'linux': {
                    'regular': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    'bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
                }
            }

            # Determine OS and set font paths
            import platform
            system = platform.system().lower()
            if system in FONT_PATHS:
                font_paths = FONT_PATHS[system]
            else:
                font_paths = FONT_PATHS['windows']  # Default to Windows paths

            # Load fonts with error handling and fallbacks
            try:
                # First try loading system fonts
                title_font = ImageFont.truetype(font_paths['bold'], TYPOGRAPHY['title_size'])
                subtitle_font = ImageFont.truetype(font_paths['regular'], TYPOGRAPHY['subtitle_size'])
                caption_font = ImageFont.truetype(font_paths['regular'], TYPOGRAPHY['caption_size'])
            except Exception as e:
                logging.warning(f"Failed to load system fonts: {e}")
                try:
                    # Try loading from the current directory
                    title_font = ImageFont.truetype("Arial.ttf", TYPOGRAPHY['title_size'])
                    subtitle_font = ImageFont.truetype("Arial.ttf", TYPOGRAPHY['subtitle_size'])
                    caption_font = ImageFont.truetype("Arial.ttf", TYPOGRAPHY['caption_size'])
                except Exception as e:
                    logging.warning(f"Failed to load local fonts: {e}")
                    # Fall back to default font
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                    caption_font = ImageFont.load_default()

            def draw_text_with_encoding(draw, position, text, font, fill):
                """Helper function to draw text with proper encoding"""
                try:
                    # Try drawing with default encoding
                    draw.text(position, text, font=font, fill=fill)
                except UnicodeEncodeError:
                    # If default encoding fails, try UTF-8
                    encoded_text = text.encode('utf-8', 'ignore').decode('utf-8')
                    draw.text(position, encoded_text, font=font, fill=fill)

            for category_name, category_info in categories.items():
                category_shots = [s for s in screenshots if s['name'] in category_info['devices']]
                if not category_shots:
                    continue

                # Calculate Behance-style grid layout
                margin = 60
                gutter = 30
                card_width = 1200
                card_height = 900

                cols = min(2, len(category_shots))  # Behance typically uses 2 columns
                rows = (len(category_shots) + cols - 1) // cols

                # Create large canvas with room for header and description
                canvas_width = margin * 2 + card_width * cols + gutter * (cols - 1)
                canvas_height = (
                        margin * 2 +  # Top and bottom margins
                        150 +  # Header space
                        100 +  # Description space
                        (card_height * rows) + (gutter * (rows - 1))
                )

                # Create canvas with white background
                canvas = Image.new('RGB', (canvas_width, canvas_height), COLORS['background'])
                draw = ImageDraw.Draw(canvas)

                # Draw header section with Behance-style typography
                header_y = margin
                draw_text_with_encoding(
                    draw,
                    (margin, header_y),
                    category_info['title'],
                    title_font,
                    COLORS['text_primary']
                )

                # Add category description
                description_y = header_y + TYPOGRAPHY['title_size'] + 20
                draw_text_with_encoding(
                    draw,
                    (margin, description_y),
                    f"Responsive design showcase for {category_info['title']} devices",
                    subtitle_font,
                    COLORS['text_secondary']
                )

                # Draw subtle divider line
                divider_y = description_y + TYPOGRAPHY['subtitle_size'] + 30
                draw.line(
                    (margin, divider_y, canvas_width - margin, divider_y),
                    fill=COLORS['divider'],
                    width=2
                )

                # Place screenshots in grid with enhanced styling
                content_start_y = divider_y + 50
                for idx, screenshot in enumerate(category_shots):
                    row = idx // cols
                    col = idx % cols

                    x = margin + (card_width + gutter) * col
                    y = content_start_y + (card_height + gutter) * row

                    try:
                        with Image.open(screenshot["path"]) as img:
                            # Calculate dimensions maintaining aspect ratio
                            display_width = card_width - 60  # Padding inside card
                            scale = display_width / screenshot["width"]
                            display_height = int(screenshot["height"] * scale)

                            # Resize screenshot
                            img_resized = img.resize(
                                (display_width, display_height),
                                Image.Resampling.LANCZOS
                            )

                            # Create card background
                            card = Image.new('RGB', (card_width, card_height), COLORS['background'])
                            card_draw = ImageDraw.Draw(card)

                            # Center screenshot in card
                            img_x = (card_width - display_width) // 2
                            img_y = 30  # Top padding
                            card.paste(img_resized, (img_x, img_y))

                            # Add device info with enhanced typography
                            device_name = device_names.get(screenshot['name'], screenshot['name'])
                            info_y = img_y + display_height + 20

                            # Device name
                            draw_text_with_encoding(
                                card_draw,
                                (30, info_y),
                                device_name,
                                subtitle_font,
                                COLORS['text_primary']
                            )

                            # Technical specs
                            specs_text = f"Resolution: {screenshot['width']}×{screenshot['height']} • DPR: {screenshot['dpr']}x"
                            draw_text_with_encoding(
                                card_draw,
                                (30, info_y + TYPOGRAPHY['subtitle_size'] + 10),
                                specs_text,
                                caption_font,
                                COLORS['text_secondary']
                            )

                            # Add subtle border to card
                            card_draw.rectangle(
                                [0, 0, card_width - 1, card_height - 1],
                                outline=COLORS['divider'],
                                width=1
                            )

                            # Paste card onto main canvas
                            canvas.paste(card, (x, y))

                    except Exception as e:
                        logging.error(f"Error processing image {screenshot['name']}: {str(e)}")
                        continue

                # Save optimized collage
                collage_path = os.path.join(
                    self.output_dir,
                    f"collage_{category_name}.png"
                )
                canvas.save(collage_path, optimize=True, quality=95)
                logging.info(f"{category_name} collage saved to: {collage_path}")

        except Exception as e:
            logging.error(f"Error creating category collages: {str(e)}")

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
    URL = "https://www.wikipedia.org/"  # Change this to your target URL
    MAX_WORKERS = 8  # Adjust based on your system's capabilities

    screenshotter = WebsiteScreenshotter(
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS
    )
    screenshotter.process_website(URL)


if __name__ == "__main__":
    main()
