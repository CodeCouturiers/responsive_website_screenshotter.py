from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageFilter
import logging
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import time
from selenium.common.exceptions import WebDriverException
import io


@dataclass
class Viewport:
    width: int
    height: int
    name: str
    dpr: float
    user_agent: str


class WebsiteScreenshotter:
    VIEWPORTS = [
        # Presentation & Portfolio Displays
        Viewport(1440, 1024, "presentation-standard", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1680, 1050, "presentation-wide", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1200, 900, "dribbble-shot", 2.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1600, 1200, "behance-project", 2.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),

        # Common Design Presentation Formats
        Viewport(1280, 720, "hd-preview", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1920, 1080, "fullhd-preview", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),

        # Popular Aspect Ratios
        Viewport(1500, 1000, "3-2-ratio", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
        Viewport(1600, 900, "16-9-ratio", 1.0,
                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),

        Viewport(2560, 1600, "macbook-air-15", 2.0,
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),
        Viewport(2304, 1440, "macbook-air-13", 2.0,
                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"),

        Viewport(2360, 1640, "ipad-air-5", 2.0,
                 "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"),

        Viewport(1080, 2340, "samsung-a54", 2.5,
                 "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"),

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

    def capture_gif_frames(
            self,
            driver: webdriver.Chrome,
            viewport: Viewport,
            frame_count: int = 15,  # 15 кадров
            delay: float = 0.2  # 0.2 секунды между кадрами
    ) -> List[bytes]:
        """Capture multiple frames for GIF creation"""
        frames = []
        try:
            for _ in range(frame_count):
                # Capture screenshot as bytes
                screenshot_bytes = driver.get_screenshot_as_png()
                frames.append(screenshot_bytes)

                # Scroll slightly and wait
                driver.execute_script("""
                    window.scrollBy({
                        top: Math.min(50, document.body.scrollHeight - window.innerHeight),
                        behavior: 'smooth'
                    });
                """)
                time.sleep(delay)

            return frames

        except Exception as e:
            logging.error(f"Error capturing frames: {str(e)}")
            return []

    def create_gif_from_frames(self, frames: List[bytes], output_path: str, duration: int = 500) -> Optional[str]:
        """Convert captured frames to GIF"""
        try:
            images = []
            for frame in frames:
                img = Image.open(io.BytesIO(frame))
                images.append(img.convert('RGB'))

            if images:
                images[0].save(
                    output_path,
                    save_all=True,
                    append_images=images[1:],
                    duration=duration,
                    loop=0,
                    optimize=True
                )
                return output_path
            return None
        except Exception as e:
            logging.error(f"Error creating GIF: {str(e)}")
            return None

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

    def check_screenshot_content(self, image_path: str) -> bool:
        """Check if the screenshot has real content"""
        with Image.open(image_path) as img:
            # Convert to RGB if in different format
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize for faster analysis
            thumb = img.resize((100, 100))

            pixels = thumb.getcolors(10000)
            if not pixels:
                return False

            total_pixels = sum(count for count, _ in pixels)

            # Check for white and near-white pixels
            white_pixels = sum(
                count for count, color in pixels
                if all(c > 250 for c in color)
            )

            # Check for very light pixels
            very_light_pixels = sum(
                count for count, color in pixels
                if all(c > 240 for c in color)
            )

            # Check for dark pixels (text, borders etc.)
            dark_pixels = sum(
                count for count, color in pixels
                if any(c < 200 for c in color)
            )

            # Calculate ratios
            white_ratio = white_pixels / total_pixels
            very_light_ratio = very_light_pixels / total_pixels
            dark_ratio = dark_pixels / total_pixels

            # Content checks
            if white_ratio > 0.98:
                return False
            if very_light_ratio > 0.95 and dark_ratio < 0.01:
                return False
            if dark_ratio > 0.02:
                return True

            return True

    def capture_screenshot(self, url: str, viewport: Viewport, retry_count: int = 3) -> Dict:
        """Modified to capture GIF instead of static screenshot"""
        for attempt in range(retry_count):
            driver = None
            try:
                options = self.get_chrome_options()
                options.add_argument(f'user-agent={viewport.user_agent}')
                driver = webdriver.Chrome(options=options)

                # Setup viewport and load page
                physical_width = int(viewport.width / viewport.dpr)
                physical_height = int(viewport.height / viewport.dpr)
                driver.set_window_size(physical_width + 100, physical_height + 100)

                driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                    'width': physical_width,
                    'height': physical_height,
                    'deviceScaleFactor': viewport.dpr,
                    'mobile': 'mobile' in viewport.name.lower() or 'iphone' in viewport.name.lower()
                })

                driver.get(url)
                self.wait_for_page_load(driver, viewport)
                self.inject_hydration_handling(driver)

                # Capture frames for GIF
                frames = self.capture_gif_frames(driver, viewport)

                if not frames:
                    raise WebDriverException("No frames captured")

                # Create GIF
                gif_path = os.path.join(
                    self.output_dir,
                    f"screenshot-{viewport.name}.gif"
                )

                if self.create_gif_from_frames(frames, gif_path):
                    return {
                        "name": viewport.name,
                        "path": gif_path,
                        "width": viewport.width,
                        "height": viewport.height,
                        "dpr": viewport.dpr,
                        "physical_width": physical_width,
                        "physical_height": physical_height,
                        "user_agent": viewport.user_agent
                    }

                return None

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
                'iPhones': {
                    'title': 'iPhone Series',
                    'subtitle': 'Super Retina XDR Displays',
                    'devices': ['iphone-15-pro-max', 'iphone-15-pro', 'iphone-15']
                },
                'Android_Phones': {
                    'title': 'Android Phones',
                    'subtitle': 'Flagship & Mid-Range Collection',
                    'devices': ['samsung-s24-ultra', 'samsung-s24', 'samsung-a54', 'pixel-8-pro', 'oneplus-12']
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
                'macbook-air-15': 'MacBook Air 15"',
                'macbook-air-13': 'MacBook Air 13"',

                # iPads
                'ipad-pro-12.9': 'iPad Pro 12.9"',
                'ipad-pro-11': 'iPad Pro 11"',
                'ipad-10.9': 'iPad Air',
                'ipad-air-5': 'iPad Air 5',

                # Android Tablets
                'samsung-tab-s9': 'Galaxy Tab S9',
                'lenovo-tab-p12': 'Tab P12 Pro',
                'xiaomi-pad-6': 'Pad 6',

                # iPhones
                'iphone-15-pro-max': 'iPhone 15 Pro Max',
                'iphone-15-pro': 'iPhone 15 Pro',
                'iphone-15': 'iPhone 15',

                # Android Phones
                'samsung-s24-ultra': 'Galaxy S24 Ultra',
                'samsung-s24': 'Galaxy S24',
                'pixel-8-pro': 'Pixel 8 Pro',
                'oneplus-12': 'OnePlus 12',
                'samsung-a54': 'Galaxy A54 5G',

                # Presentation Formats
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
                    'background': '#FFFFFF',
                    'card': '#FFFFFF',
                    'text': {
                        'primary': '#000000',
                        'secondary': '#444444',
                        'tertiary': '#666666'
                    },
                    'border': '#EAEAEA',
                    'shadow': (0, 0, 0, 15)
                },
                'spacing': {
                    'margin': 100,
                    'gutter': 40,
                    'header': 300,
                    'card_padding': 40
                },
                'typography': {
                    'title': 96,
                    'subtitle': 32,
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
                    'light': 'C:/Windows/Fonts/segoeuil.ttf'
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
                title_font = ImageFont.truetype(fonts['light'], DESIGN['typography']['title'])
                subtitle_font = ImageFont.truetype(fonts['light'], DESIGN['typography']['subtitle'])
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
                header_y = spacing['margin'] + 40
                title_height = draw_text(
                    draw,
                    (spacing['margin'], header_y),
                    category_info['title'].upper(),
                    title_font,
                    DESIGN['colors']['text']['primary'],
                    'center',
                    canvas_width - (spacing['margin'] * 2)
                )

                # Draw subtitle
                subtitle_y = header_y + title_height + 30
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
                            # For GIFs, use the first frame
                            if 'duration' in img.info:
                                img.seek(0)

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
                            img_resized = img.convert('RGB').resize(
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
                self.create_category_collages(screenshots)
                logging.info("Process completed successfully")
            else:
                logging.error("No screenshots were captured successfully")


def main():
    OUTPUT_DIR = r"C:\Users\user\Downloads\testScript"  # Change this to your desired output directory
    URL = "http://127.0.0.1:5000/login"  # Change this to your target URL
    MAX_WORKERS = 1  # Adjust based on your system's capabilities

    screenshotter = WebsiteScreenshotter(
        output_dir=OUTPUT_DIR,
        max_workers=MAX_WORKERS
    )
    screenshotter.process_website(URL)


if __name__ == "__main__":
    main()
