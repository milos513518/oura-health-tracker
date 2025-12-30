"""
HeartCloud Web Scraper
Logs into HeartCloud and extracts coherence training data

IMPORTANT: This script contains PLACEHOLDER selectors that you MUST customize
based on HeartCloud's actual HTML structure. Follow the setup instructions below.
"""

import os
import time
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# CONFIGURATION
# ==========================================

# HeartCloud credentials (from environment variables)
HEARTCLOUD_EMAIL = os.environ.get("HEARTCLOUD_EMAIL")
HEARTCLOUD_PASSWORD = os.environ.get("HEARTCLOUD_PASSWORD")

# Google Sheets configuration
SHEET_KEY = "1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc"
WORKSHEET_NAME = "daily_manual_entry"

# ==========================================
# STEP 1: FIND YOUR CSS SELECTORS
# ==========================================
"""
BEFORE RUNNING THIS SCRIPT, YOU MUST:

1. Login to heartcloud.com in Chrome/Firefox
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Navigate to your sessions/history page
4. Find the HTML elements that contain:
   - Session dates
   - Coherence scores
   - Session durations
   - Achievement scores

5. Note the CSS selectors (classes, IDs, or attributes)

Example of what you're looking for:
<div class="session-item">
  <span class="date">2024-12-30</span>
  <span class="coherence-score">5.8</span>
  <span class="duration">15:30</span>
</div>

Then update the SELECTORS dictionary below with your findings.
"""

SELECTORS = {
    # Login page selectors - VERIFIED from HeartCloud
    "email_field": "#email",
    "password_field": "#password",
    "login_button": "button[type='submit']",
    
    # After login - sessions page (History tab)
    # HeartCloud uses a table structure for Training History
    "sessions_container": "table",  # The table containing all sessions
    "session_row": "tr",  # Each table row is a session
    
    # Within each session row (table columns)
    "date": "td:nth-child(1)",  # First column = Date
    "session_length": "td:nth-child(2)",  # Second column = Length
    "coherence_score": "td:nth-child(3)",  # Third column = Coherence
    "achievement_score": "td:nth-child(4)",  # Fourth column = Achievement
}

# ==========================================
# GOOGLE SHEETS CONNECTION
# ==========================================

def get_google_sheets_client():
    """Initialize Google Sheets client with service account credentials"""
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Try Render secret file first
        secret_file = "/etc/secrets/gcp-key.pem"
        if os.path.exists(secret_file):
            with open(secret_file, 'r') as f:
                creds_json = json.loads(f.read())
            
            # Fix private key formatting
            pk = creds_json.get("private_key", "")
            if isinstance(pk, str):
                creds_json["private_key"] = pk.replace("\\n", "\n")
            
            creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        
        # Fallback to environment variables
        else:
            creds = Credentials.from_service_account_info(
                {
                    "type": os.environ.get("GCP_TYPE"),
                    "project_id": os.environ.get("GCP_PROJECT_ID"),
                    "private_key_id": os.environ.get("GCP_PRIVATE_KEY_ID"),
                    "private_key": os.environ.get("GCP_PRIVATE_KEY").replace('\\n', '\n'),
                    "client_email": os.environ.get("GCP_CLIENT_EMAIL"),
                    "client_id": os.environ.get("GCP_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.environ.get("GCP_CERT_URL"),
                    "universe_domain": "googleapis.com"
                },
                scopes=scopes
            )
        
        return gspread.authorize(creds)
    
    except Exception as e:
        print(f"✗ Error connecting to Google Sheets: {str(e)}")
        return None

# ==========================================
# CHROME DRIVER SETUP
# ==========================================

def setup_chrome_driver():
    """Setup headless Chrome driver for web scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# ==========================================
# HEARTCLOUD LOGIN
# ==========================================

def login_to_heartcloud(driver):
    """Login to HeartCloud website"""
    try:
        print("🔐 Logging into HeartCloud...")
        driver.get("https://heartcloud.com/login")
        
        wait = WebDriverWait(driver, 20)
        
        # Wait for login form to load
        print("  ⏳ Waiting for login form...")
        time.sleep(2)
        
        # Find and fill email field
        try:
            email_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["email_field"]))
            )
            email_field.clear()
            email_field.send_keys(HEARTCLOUD_EMAIL)
            print(f"  ✓ Entered email: {HEARTCLOUD_EMAIL}")
        except TimeoutException:
            print(f"  ✗ Could not find email field with selector: {SELECTORS['email_field']}")
            print("  📝 Please update SELECTORS['email_field'] in the script")
            return False
        
        # Find and fill password field
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, SELECTORS["password_field"])
            password_field.clear()
            password_field.send_keys(HEARTCLOUD_PASSWORD)
            print("  ✓ Entered password")
        except NoSuchElementException:
            print(f"  ✗ Could not find password field with selector: {SELECTORS['password_field']}")
            print("  📝 Please update SELECTORS['password_field'] in the script")
            return False
        
        # Click login button
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, SELECTORS["login_button"])
            login_button.click()
            print("  ✓ Clicked login button")
        except NoSuchElementException:
            print(f"  ✗ Could not find login button with selector: {SELECTORS['login_button']}")
            print("  📝 Please update SELECTORS['login_button'] in the script")
            return False
        
        # Wait for redirect after login
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        if "login" in current_url.lower():
            print("  ✗ Still on login page - login may have failed")
            # Take screenshot for debugging
            driver.save_screenshot("/tmp/heartcloud_login_failed.png")
            print("  📸 Screenshot saved to /tmp/heartcloud_login_failed.png")
            return False
        
        print("✅ Successfully logged into HeartCloud")
        return True
        
    except Exception as e:
        print(f"✗ Login failed with error: {str(e)}")
        driver.save_screenshot("/tmp/heartcloud_error.png")
        return False

# ==========================================
# SCRAPE SESSION DATA
# ==========================================

def scrape_latest_session(driver):
    """
    Scrape the most recent coherence session data from HeartCloud
    Returns: dict with date, coherence_score, session_length, achievement_score
    """
    try:
        print("\n📊 Scraping latest session data...")
        
        # Try to find the sessions page
        # HeartCloud might redirect to home/dashboard after login
        possible_urls = [
            "https://heartcloud.com/",
            "https://heartcloud.com/home",
            "https://heartcloud.com/dashboard",
            "https://heartcloud.com/sessions",
            "https://heartcloud.com/history",
            "https://heartcloud.com/review"
        ]
        
        # Try each URL to find where sessions are displayed
        for url in possible_urls:
            print(f"  🔍 Trying {url}...")
            driver.get(url)
            time.sleep(3)
            
            # Check if we can find session data here
            try:
                driver.find_element(By.CSS_SELECTOR, SELECTORS["sessions_container"])
                print(f"  ✓ Found sessions at {url}")
                break
            except NoSuchElementException:
                continue
        
        # Wait for sessions to load
        wait = WebDriverWait(driver, 15)
        
        # Find all session rows
        try:
            session_rows = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS["session_row"]))
            )
            print(f"  ✓ Found {len(session_rows)} session(s)")
        except TimeoutException:
            print(f"  ✗ Could not find sessions with selector: {SELECTORS['session_row']}")
            print("  📝 Please update SELECTORS['session_row'] in the script")
            
            # Save page source for debugging
            with open("/tmp/heartcloud_page_source.html", "w") as f:
                f.write(driver.page_source)
            print("  📝 Page source saved to /tmp/heartcloud_page_source.html")
            
            return None
        
        if len(session_rows) == 0:
            print("  ℹ️ No sessions found")
            return None
        
        # Get the first (most recent) session
        latest_session = session_rows[0]
        
        # Extract data from the session
        session_data = {}
        
        # Extract date
        try:
            date_elem = latest_session.find_element(By.CSS_SELECTOR, SELECTORS["date"])
            session_data['date'] = parse_date(date_elem.text)
            print(f"  ✓ Date: {session_data['date']}")
        except NoSuchElementException:
            print(f"  ⚠️  Could not find date with selector: {SELECTORS['date']}")
            session_data['date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Extract coherence score
        try:
            coherence_elem = latest_session.find_element(By.CSS_SELECTOR, SELECTORS["coherence_score"])
            session_data['coherence_score'] = parse_coherence_score(coherence_elem.text)
            print(f"  ✓ Coherence: {session_data['coherence_score']}")
        except NoSuchElementException:
            print(f"  ⚠️  Could not find coherence with selector: {SELECTORS['coherence_score']}")
            session_data['coherence_score'] = None
        
        # Extract session length (optional)
        try:
            length_elem = latest_session.find_element(By.CSS_SELECTOR, SELECTORS["session_length"])
            session_data['session_length'] = parse_session_length(length_elem.text)
            print(f"  ✓ Duration: {session_data['session_length']} min")
        except NoSuchElementException:
            print(f"  ℹ️  Session length not found (optional)")
            session_data['session_length'] = None
        
        # Extract achievement score (optional)
        try:
            achievement_elem = latest_session.find_element(By.CSS_SELECTOR, SELECTORS["achievement_score"])
            session_data['achievement_score'] = parse_achievement_score(achievement_elem.text)
            print(f"  ✓ Achievement: {session_data['achievement_score']}")
        except NoSuchElementException:
            print(f"  ℹ️  Achievement score not found (optional)")
            session_data['achievement_score'] = None
        
        return session_data
        
    except Exception as e:
        print(f"✗ Failed to scrape session data: {str(e)}")
        driver.save_screenshot("/tmp/heartcloud_scrape_error.png")
        return None

# ==========================================
# DATA PARSING HELPERS
# ==========================================

def parse_date(date_text):
    """Parse date from various formats"""
    try:
        # Try common formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
            try:
                dt = datetime.strptime(date_text.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If all fail, return today
        return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

def parse_coherence_score(score_text):
    """Extract coherence score from text"""
    try:
        import re
        # Extract first number (with optional decimal)
        match = re.search(r'\d+\.?\d*', score_text)
        if match:
            return float(match.group())
        return None
    except:
        return None

def parse_session_length(length_text):
    """Parse session length to minutes"""
    try:
        import re
        # Look for MM:SS format
        match = re.search(r'(\d+):(\d+)', length_text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return round(minutes + seconds / 60, 1)
        
        # Look for just minutes
        match = re.search(r'(\d+)', length_text)
        if match:
            return int(match.group(1))
        
        return None
    except:
        return None

def parse_achievement_score(achievement_text):
    """Extract achievement score from text"""
    try:
        import re
        match = re.search(r'\d+', achievement_text)
        if match:
            return int(match.group())
        return None
    except:
        return None

# ==========================================
# WRITE TO GOOGLE SHEETS
# ==========================================

def write_to_google_sheets(session_data):
    """Write coherence data to Google Sheets"""
    try:
        print("\n📝 Writing to Google Sheets...")
        
        gc = get_google_sheets_client()
        if not gc:
            return False
        
        sheet = gc.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME)
        
        # Get the date to update
        target_date = session_data['date']
        print(f"  🗓️  Target date: {target_date}")
        
        # Find the row for this date
        all_values = sheet.get_all_values()
        headers = [h.lower().strip() for h in all_values[0]]
        
        # Find date and coherence columns
        try:
            date_col = headers.index('date') + 1
            coherence_col = headers.index('coherence') + 1
        except ValueError as e:
            print(f"  ✗ Missing required column: {e}")
            return False
        
        # Search for existing row with this date
        target_row = None
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) >= date_col and row[date_col - 1] == target_date:
                target_row = i
                break
        
        # If no row exists, create new one
        if target_row is None:
            target_row = len(all_values) + 1
            sheet.update_cell(target_row, date_col, target_date)
            print(f"  ✓ Created new row {target_row} for {target_date}")
        else:
            print(f"  ✓ Found existing row {target_row} for {target_date}")
        
        # Write coherence score
        coherence = session_data['coherence_score']
        if coherence is not None:
            sheet.update_cell(target_row, coherence_col, coherence)
            print(f"  ✓ Updated coherence: {coherence}")
        
        print("✅ Successfully wrote to Google Sheets")
        return True
        
    except Exception as e:
        print(f"✗ Failed to write to Google Sheets: {str(e)}")
        return False

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("HeartCloud Coherence Data Sync")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check credentials
    if not HEARTCLOUD_EMAIL or not HEARTCLOUD_PASSWORD:
        print("✗ Error: HEARTCLOUD_EMAIL and HEARTCLOUD_PASSWORD must be set")
        print("  Set them as environment variables before running")
        return False
    
    driver = None
    
    try:
        # Setup Chrome driver
        print("\n🌐 Setting up Chrome driver...")
        driver = setup_chrome_driver()
        print("✓ Chrome driver ready")
        
        # Login to HeartCloud
        if not login_to_heartcloud(driver):
            return False
        
        # Scrape latest session data
        session_data = scrape_latest_session(driver)
        
        if not session_data:
            print("✗ No session data retrieved")
            return False
        
        if session_data['coherence_score'] is None:
            print("⚠️  Warning: No coherence score found in session data")
            print("  Check if selectors are correct")
            return False
        
        # Write to Google Sheets
        if not write_to_google_sheets(session_data):
            return False
        
        print("\n" + "=" * 60)
        print("✅ HeartCloud sync completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
