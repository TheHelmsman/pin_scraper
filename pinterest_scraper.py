#!/usr/bin/env python3
"""
Pinterest Board Image Downloader - macOS Version with User Profile
Downloads all images from a Pinterest board to a local directory using your existing Chrome session.

Requirements:
- selenium
- pillow
- requests

Install with:
pip install selenium pillow requests
"""

import os
import sys
import time
import requests
import subprocess
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
import io
import hashlib

class PinterestScraper:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.downloaded_urls = set()
        
    def get_chrome_profile_path(self):
        """Get the path to Chrome's default profile on macOS"""
        # Common Chrome profile paths on macOS
        username = os.getenv('USER')
        chrome_profiles = [
            f"/Users/{username}/Library/Application Support/Google/Chrome/Default",
            f"/Users/{username}/Library/Application Support/Google/Chrome/Profile 1",
        ]
        
        for profile_path in chrome_profiles:
            if os.path.exists(profile_path):
                print(f"✓ Found Chrome profile: {profile_path}")
                return profile_path
        
        print("⚠️  Default Chrome profile not found, using temporary profile")
        return None
        
    def setup_driver(self, headless):
        """Setup Chrome driver with user profile"""
        print("Setting up Chrome driver with user profile...")
        
        chrome_options = Options()
        
        # Get and use Chrome profile
        profile_path = self.get_chrome_profile_path()
        if profile_path:
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            print("✓ Using your existing Chrome profile with active sessions")
        else:
            chrome_options.add_argument("--user-data-dir=/tmp/chrome_profile")
            print("⚠️  Using temporary profile - you may need to log in to Pinterest")
        
        if headless:
            chrome_options.add_argument("--headless=new")
            
        # macOS specific options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional options to make browsing more natural
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Let Selenium find Chrome automatically
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✓ Chrome driver initialized successfully with your profile")
            
        except Exception as e:
            print(f"Initial method failed: {e}")
            self.setup_driver_alternative(chrome_options)
    
    def setup_driver_alternative(self, chrome_options):
        """Alternative methods for macOS"""
        try:
            # Try common chromedriver paths
            possible_paths = [
                '/usr/local/bin/chromedriver',
                '/opt/homebrew/bin/chromedriver',
                '/Applications/Google Chrome.app/Contents/MacOS/chromedriver'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"Trying chromedriver at: {path}")
                    self.driver = webdriver.Chrome(executable_path=path, options=chrome_options)
                    return
            
            # Final attempt
            self.driver = webdriver.Chrome(options=chrome_options)
            
        except Exception as e:
            print(f"All methods failed: {e}")
            print("\nPlease install ChromeDriver: brew install chromedriver")
            raise
        
    def check_login_status(self):
        """Check if we're logged into Pinterest"""
        print("Checking Pinterest login status...")
        
        try:
            # Try to access Pinterest home page
            self.driver.get("https://www.pinterest.com")
            time.sleep(3)
            
            # Look for login indicators or profile elements
            logged_in_indicators = [
                "//div[@data-test-id='header-profile']",
                "//div[contains(@class, 'profile')]",
                "//a[contains(@href, '/settings/')]",
                "//button[contains(@aria-label, 'Profile')]"
            ]
            
            for indicator in logged_in_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        print("✓ Successfully logged into Pinterest!")
                        return True
                except:
                    continue
            
            # Check for login page indicators
            login_indicators = [
                "//button[contains(text(), 'Log in')]",
                "//div[contains(text(), 'Welcome to Pinterest')]",
                "//input[@type='email']"
            ]
            
            for indicator in login_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        print("❌ Not logged into Pinterest")
                        print("💡 Please log in manually in the browser window that opened")
                        input("Press Enter after you've logged in to Pinterest...")
                        return self.verify_login_after_manual()
                except:
                    continue
                    
            print("⚠️  Could not determine login status")
            return True
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    def verify_login_after_manual(self):
        """Verify login after manual intervention"""
        print("Verifying login...")
        time.sleep(3)
        return self.check_login_status()
        
    def scroll_to_bottom(self, max_scrolls=30):
        """Scroll to bottom of page to load all images"""
        print("Scrolling to load all images...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0
        
        for i in range(max_scrolls):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= 3:
                    print("Reached bottom of page")
                    break
            else:
                no_change_count = 0
                last_height = new_height
            
            print(f"Scroll {i+1}/{max_scrolls} - Height: {new_height}px")

    def extract_image_urls(self):
        """Extract high-quality image URLs from the board"""
        print("Extracting image URLs...")
        image_urls = set()
        
        try:
            # Wait for pins to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'pinimg.com')]"))
            )
            
            # Find Pinterest images
            images = self.driver.find_elements(By.XPATH, "//img[contains(@src, 'pinimg.com')]")
            print(f"Found {len(images)} Pinterest images")
            
            for img in images:
                try:
                    src = img.get_attribute('src')
                    if src:
                        # Get higher resolution if possible
                        if '236x' in src:
                            high_res = src.replace('236x', '736x')
                            image_urls.add(high_res)
                        elif '564x' in src:
                            high_res = src.replace('564x', '736x')
                            image_urls.add(high_res)
                        else:
                            image_urls.add(src)
                except:
                    continue
                    
        except TimeoutException:
            print("Timeout waiting for images to load")
            # Try alternative approach
            images = self.driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                src = img.get_attribute('src')
                if src and 'pinimg.com' in src:
                    image_urls.add(src)
            
        # Convert to list and filter
        urls = [url for url in image_urls if url]
        print(f"Extracted {len(urls)} unique image URLs")
        return urls

    def download_image(self, img_url, folder_path, img_num):
        """Download and save individual image"""
        try:
            if img_url in self.downloaded_urls:
                return False
                
            # Create filename
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            filename = f"pinterest_{img_num:04d}_{url_hash}.jpg"
            filepath = os.path.join(folder_path, filename)
            
            if os.path.exists(filepath):
                print(f"✓ Already exists: {filename}")
                self.downloaded_urls.add(img_url)
                return True
            
            # Download headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.pinterest.com/',
            }
            
            # Download image
            response = requests.get(img_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Verify it's an image
            try:
                image = Image.open(io.BytesIO(response.content))
                image.verify()
            except:
                print(f"✗ Invalid image format: {filename}")
                return False
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            self.downloaded_urls.add(img_url)
            print(f"✓ Downloaded: {filename} ({len(response.content)//1024} KB)")
            return True
            
        except Exception as e:
            print(f"✗ Failed to download image {img_num}: {str(e)}")
            return False

    def scrape_board(self, board_url, output_folder):
        """Main method to scrape images from Pinterest board"""
        print(f"🎯 Starting Pinterest scrape")
        print(f"📋 Board URL: {board_url}")
        print(f"💾 Output folder: {output_folder}")
        print("-" * 50)
        
        # Create output directory
        os.makedirs(output_folder, exist_ok=True)
        
        try:
            # First check login status
            if not self.check_login_status():
                print("❌ Login check failed. Please ensure you're logged into Pinterest in Chrome.")
                return
                
            # Navigate to board
            print(f"🌐 Loading board: {board_url}")
            self.driver.get(board_url)
            time.sleep(5)
            
            # Check if board loaded successfully
            if "pinterest.com" not in self.driver.current_url or "login" in self.driver.current_url:
                print("❌ Redirected to login page. Please log in manually and try again.")
                return
            
            # Scroll to load all content
            self.scroll_to_bottom()
            
            # Extract URLs
            image_urls = self.extract_image_urls()
            
            if not image_urls:
                print("❌ No images found on this board!")
                return
                
            # Download images
            print(f"\n⬇️  Downloading {len(image_urls)} images...")
            successful = 0
            
            for i, img_url in enumerate(image_urls, 1):
                if self.download_image(img_url, output_folder, i):
                    successful += 1
                
                time.sleep(0.5)
                
                if i % 10 == 0:
                    print(f"📊 Progress: {i}/{len(image_urls)}")
            
            # Results
            print("\n" + "="*50)
            print(f"🎉 DOWNLOAD COMPLETED!")
            print(f"✅ Successful: {successful}/{len(image_urls)}")
            print(f"📁 Location: {os.path.abspath(output_folder)}")
            print("="*50)
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            raise
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("🔚 Browser closed")

def main():
    if len(sys.argv) != 3:
        print("Usage: python pinterest_mac_profile.py <pinterest_board_url> <output_folder>")
        print("Example: python pinterest_mac_profile.py https://ru.pinterest.com/user/board-name/ ./pinterest_images")
        sys.exit(1)
    
    board_url = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Validate URL
    if not board_url.startswith('https://jp.pinterest.com/'):
        print("❌ Error: Please provide a valid Pinterest board URL")
        print("   URL should start with: https://jp.pinterest.com/")
        sys.exit(1)
    
    try:
        # Start with visible browser to allow manual login if needed
        scraper = PinterestScraper(headless=False)
        scraper.scrape_board(board_url, output_folder)
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()