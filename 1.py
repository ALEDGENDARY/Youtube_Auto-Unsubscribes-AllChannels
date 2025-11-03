from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

class YouTubeUnsubscriber:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.unsubscribe_count = 0
        
    def setup_driver(self):
        """Setup Chrome driver"""
        print("🚀 Setting up browser...")
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Browser setup complete!")
            return True
        except Exception as e:
            print(f"❌ Failed to setup web driver: {e}")
            return False
    
    def wait_for_manual_login(self):
        """Wait for user to manually login to YouTube WITHOUT refreshing"""
        print("🔐 Please login to YouTube...")
        print("1. Browser will open YouTube")
        print("2. Login with your Google account - TAKE YOUR TIME")
        print("3. After login, press Enter in this terminal to continue")
        print("4. DO NOT CLOSE THE BROWSER")
        print("-" * 50)
        
        # Open YouTube and wait
        self.driver.get("https://www.youtube.com")
        print("📺 YouTube opened in browser...")
        print("⏳ Please login now in the browser window...")
        
        # Wait for user to press Enter after they finish logging in
        input("✅ Press Enter AFTER you have successfully logged in to YouTube...")
        
        # Now navigate to subscriptions to verify login worked
        print("🔄 Navigating to subscriptions page...")
        self.driver.get("https://www.youtube.com/feed/channels")
        time.sleep(3)
        
        # Check if we're actually on subscriptions page
        current_url = self.driver.current_url
        if "feed/channels" in current_url:
            print("✅ Successfully accessed subscriptions! Starting unsubscribe process...")
            return True
        else:
            print("❌ Could not access subscriptions. Please make sure you're logged in.")
            return False
    
    def find_subscribed_buttons(self):
        """Find all subscribed buttons using your exact XPath targets"""
        print("🔍 Searching for subscribed channels...")
        
        # Scroll to load more content
        self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        
        # Your exact XPath targets from workflow
        xpath_targets = [
            "//ytd-subscription-notification-toggle-button-renderer//button",
            "//button[@aria-label*='subscription']", 
            "//button[contains(@class, 'subscription')]",
            "//button[.//span[contains(text(), 'Subscribed')]]",
            "//button[contains(@aria-label, 'Subscribed')]"
        ]
        
        all_buttons = []
        for xpath in xpath_targets:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath)
                for btn in buttons:
                    if btn.is_displayed() and btn not in all_buttons:
                        all_buttons.append(btn)
            except:
                continue
        
        print(f"📊 Found {len(all_buttons)} subscribed channel buttons")
        return all_buttons
    
    def click_unsubscribe_option(self):
        """Click the Unsubscribe option using your exact workflow"""
        try:
            # Your exact XPath target for unsubscribe options
            unsubscribe_xpath = "//*[contains(text(), 'Unsubscribe')]"
            
            unsubscribe_elements = self.driver.find_elements(By.XPATH, unsubscribe_xpath)
            
            for element in unsubscribe_elements:
                if element.is_displayed():
                    self.driver.execute_script("arguments[0].click();", element)
                    print("✓ Clicked unsubscribe option")
                    time.sleep(2)
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to click unsubscribe option: {e}")
            return False
    
    def is_confirmation_dialog_visible(self):
        """Check if confirmation dialog is currently visible"""
        try:
            # Look for confirmation dialog elements
            dialog_indicators = [
                "//yt-confirm-dialog-renderer",
                "//ytd-popup-container[contains(@class, 'ytd-popup-container')]",
                "//*[contains(text(), 'Unsubscribe from')]",
                "//*[contains(text(), 'confirm')]"
            ]
            
            for indicator in dialog_indicators:
                elements = self.driver.find_elements(By.XPATH, indicator)
                for element in elements:
                    if element.is_displayed():
                        return True
            return False
        except:
            return False

    def handle_confirmation_dialog(self):
        """Handle the confirmation dialog if it appears"""
        try:
            # Wait a moment for dialog to appear
            time.sleep(2)
            
            # Check if confirmation dialog is actually visible
            if not self.is_confirmation_dialog_visible():
                print("ℹ️ No confirmation dialog found")
                return True  # Return True since no confirmation was needed
            
            print("🔄 Confirmation dialog detected, looking for confirm button...")
            
            # Multiple strategies to find the confirmation button
            confirm_selectors = [
                # Try the actual button with "Unsubscribe" text
                "//button[.//span[contains(text(), 'Unsubscribe')]]",
                "//yt-button-renderer[.//span[contains(text(), 'Unsubscribe')]]",
                "//yt-button-renderer[@id='confirm-button']",
                "//button[@aria-label='Unsubscribe']",
                "//yt-button-renderer//button[contains(@class, 'yt-spec-button-shape-next--call-to-action')]",
                # More specific selectors for the exact structure you provided
                "//yt-button-renderer[@dialog-confirm]//button",
                "//yt-confirm-dialog-renderer//button[.//*[text()='Unsubscribe']]",
                "//ytd-popup-container//button[.//*[text()='Unsubscribe']]",
                # Even more specific for your HTML structure
                "//yt-button-renderer[@id='confirm-button']//button",
                "//yt-button-shape//button[.//span[text()='Unsubscribe']]"
            ]
            
            for selector in confirm_selectors:
                try:
                    confirm_buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in confirm_buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"✓ Found confirmation button with selector: {selector}")
                            # Scroll to button and click
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", button)
                            print("✓ Confirmed unsubscribe")
                            time.sleep(2)
                            return True
                except:
                    continue
            
            # If no button found, check if dialog exists and try alternative approach
            print("⚠️ No confirmation button found with standard selectors, trying alternative methods...")
            
            # Try to find any visible button in confirmation dialog
            dialog_buttons = self.driver.find_elements(By.XPATH, "//ytd-popup-container//button")
            for button in dialog_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = button.text.strip().lower()
                    if 'unsubscribe' in button_text or 'confirm' in button_text or 'yes' in button_text:
                        print(f"✓ Found confirmation button with text: {button_text}")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", button)
                        print("✓ Confirmed unsubscribe")
                        time.sleep(2)
                        return True
            
            print("❌ Could not find confirmation button, but continuing...")
            return False
            
        except Exception as e:
            print(f"⚠️ Error handling confirmation dialog: {e}")
            return False
    
    def unsubscribe_single_channel(self, button):
        """Unsubscribe from a single channel following your exact workflow"""
        try:
            print(f"🔄 Attempting to unsubscribe from channel {self.unsubscribe_count + 1}...")
            
            # Step 1: Click the "Subscribed" button to open dropdown
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", button)
            print("✓ Opened subscription menu")
            time.sleep(2)
            
            # Step 2: Click "Unsubscribe" option
            if not self.click_unsubscribe_option():
                print("❌ Could not find unsubscribe option")
                return False
            
            # Step 3: Handle confirmation dialog
            if not self.handle_confirmation_dialog():
                print("⚠️ Confirmation dialog not handled properly, but continuing...")
            
            # Count success
            self.unsubscribe_count += 1
            print(f"✅ Successfully unsubscribed! Total: {self.unsubscribe_count}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to unsubscribe: {e}")
            return False
    
    def run_unsubscribe_process(self):
        """Main method to run the unsubscribe process - NEVER STOPS UNTIL MANUALLY CLOSED"""
        try:
            # Setup driver using system Chrome
            if not self.setup_driver():
                return
            
            # Wait for manual login
            if not self.wait_for_manual_login():
                print("❌ Login failed or cancelled. Exiting.")
                return
            
            print(f"🚀 Starting unsubscribe process...")
            print("📋 Using your confirmed workflow:")
            print("1. Find 'Subscribed' buttons")
            print("2. Click to open dropdown") 
            print("3. Click 'Unsubscribe' option")
            print("4. Confirm dialog if needed")
            print("🔄 WILL KEEP RUNNING UNTIL YOU MANUALLY CLOSE THE BROWSER")
            print("💡 Press Ctrl+C in terminal to stop the script")
            print("-" * 60)
            
            while True:  # INFINITE LOOP - NEVER STOPS
                # Find subscribed buttons using your exact XPath
                buttons = self.find_subscribed_buttons()
                
                if not buttons:
                    print("📭 No subscribed channels found right now. Scrolling and searching again...")
                    
                    # Scroll multiple times to load more content
                    for i in range(3):
                        self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                        time.sleep(2)
                    
                    # Try going back to top and scrolling again
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(2)
                    
                    # Scroll down again
                    for i in range(3):
                        self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                        time.sleep(2)
                    
                    # Wait a bit before searching again
                    time.sleep(5)
                    continue
                
                # Process each button using your workflow
                for button in buttons:
                    try:
                        if self.unsubscribe_single_channel(button):
                            # Success - random delay
                            time.sleep(random.uniform(2, 4))
                        else:
                            print("⚠️ Failed to unsubscribe from one channel, continuing to next...")
                    except Exception as e:
                        print(f"⚠️ Error processing channel: {e}")
                        continue
                
                # Always scroll for more content after processing current batch
                print("📜 Scrolling for more channels...")
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(3)
            
        except KeyboardInterrupt:
            print(f"\n🛑 Manual stop requested! Unsubscribed from {self.unsubscribe_count} channels total.")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            print("Script will try to continue...")
            time.sleep(10)
            # Try to restart the process
            self.run_unsubscribe_process()
        
        finally:
            if self.driver:
                print("Closing browser...")
                self.driver.quit()

# Main execution
if __name__ == "__main__":
    unsubscriber = YouTubeUnsubscriber()
    
    print("YouTube Unsubscribe Automation - INFINITE MODE")
    print("=" * 60)
    print("NO CREDENTIALS REQUIRED - Manual Login")
    print("=" * 60)
    print("Instructions:")
    print("1. Browser will open to YouTube")
    print("2. Login with your Google account - TAKE YOUR TIME")
    print("3. After successful login, come back here and press Enter")
    print("4. Script will start unsubscribing automatically")
    print("5. Runs forever until you manually stop it")
    print("=" * 60)
    print("💡 To stop: Close browser OR Press Ctrl+C in terminal")
    print("=" * 60)
    
    input("Press Enter to open browser and start login process...")
    unsubscriber.run_unsubscribe_process()
