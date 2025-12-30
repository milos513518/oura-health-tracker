# HeartCloud Scraper Setup Guide

## 🎯 Goal
Create a web scraper that logs into HeartCloud and automatically pulls your coherence training data into Google Sheets.

## 📋 Prerequisites
- ✅ HeartCloud account with login credentials
- ✅ Inner Balance app syncing to HeartCloud
- ✅ Chrome or Firefox browser
- ✅ Basic familiarity with web browsers

## 🔍 Step 1: Find the Correct CSS Selectors

This is the **most important step**. The scraper needs to know exactly where on the HeartCloud website to find your data.

### What are CSS Selectors?

CSS selectors are patterns that identify HTML elements on a webpage. For example:
- `#email` = element with ID "email"
- `.session-item` = elements with class "session-item"
- `button[type='submit']` = button with type="submit" attribute

### How to Find Selectors

**Step 1.1: Open HeartCloud in Your Browser**
1. Go to https://heartcloud.com/login
2. Login with your credentials
3. Navigate to where your sessions/history are displayed

**Step 1.2: Open Developer Tools**
- **Chrome/Edge**: Press `F12` or Right-click → "Inspect"
- **Firefox**: Press `F12` or Right-click → "Inspect Element"
- **Safari**: Enable Developer menu first, then use Develop → Show Web Inspector

**Step 1.3: Inspect the Login Form**

Before logging in, inspect these elements:

1. **Email Field**:
   - Right-click on the email input box → Inspect
   - Look for something like:
   ```html
   <input id="email" name="email" type="email">
   ```
   - Note the ID or name: `#email` or `input[name='email']`

2. **Password Field**:
   - Right-click on password input → Inspect
   - Look for:
   ```html
   <input id="password" name="password" type="password">
   ```
   - Note: `#password` or `input[name='password']`

3. **Login Button**:
   - Right-click on the login button → Inspect
   - Look for:
   ```html
   <button type="submit" class="login-btn">Sign In</button>
   ```
   - Note: `button[type='submit']` or `.login-btn`

**Step 1.4: Inspect the Sessions Page**

After logging in, find your sessions list:

1. **Sessions Container**:
   - Find the main div/section that contains all your sessions
   - Right-click on the area → Inspect
   - Look for:
   ```html
   <div class="sessions-list">
     <!-- sessions here -->
   </div>
   ```
   - Note: `.sessions-list` or whatever class/ID it has

2. **Individual Session Rows**:
   - Right-click on a single session entry → Inspect
   - Look for:
   ```html
   <div class="session-item">
     <span class="date">Dec 30, 2024</span>
     <span class="coherence">5.8</span>
     <span class="duration">15:30</span>
   </div>
   ```
   - Note the class of each row: `.session-item`

3. **Coherence Score**:
   - Within a session row, find where the coherence number appears
   - Look for:
   ```html
   <span class="coherence-score">5.8</span>
   ```
   - Note: `.coherence-score` or whatever it's called

4. **Session Date**:
   - Find where the date is displayed
   - Note the selector

5. **Session Duration** (optional):
   - Find where duration is shown (e.g., "15:30")
   - Note the selector

### Example: What You Might Find

Here's an example of what HeartCloud's HTML might look like:

```html
<!-- Login Page -->
<form class="login-form">
  <input id="userEmail" type="email" placeholder="Email">
  <input id="userPassword" type="password" placeholder="Password">
  <button class="btn-login" type="submit">Login</button>
</form>

<!-- Sessions Page -->
<div class="main-content">
  <div class="session-history">
    <div class="session-row">
      <div class="session-date">2024-12-30</div>
      <div class="session-coherence">
        <span class="score-value">5.8</span>
      </div>
      <div class="session-time">15:30</div>
      <div class="achievement-points">245</div>
    </div>
    <!-- more sessions... -->
  </div>
</div>
```

Based on this, your selectors would be:
```python
SELECTORS = {
    "email_field": "#userEmail",
    "password_field": "#userPassword",
    "login_button": ".btn-login",
    "sessions_container": ".session-history",
    "session_row": ".session-row",
    "date": ".session-date",
    "coherence_score": ".score-value",
    "session_length": ".session-time",
    "achievement_score": ".achievement-points",
}
```

## 📝 Step 2: Update the Scraper Script

Once you have your selectors, update the `SELECTORS` dictionary in `sync_heartcloud_scraper.py`:

```python
SELECTORS = {
    # Replace these with YOUR actual selectors from Step 1
    "email_field": "#YOUR_EMAIL_SELECTOR",
    "password_field": "#YOUR_PASSWORD_SELECTOR",
    "login_button": "YOUR_LOGIN_BUTTON_SELECTOR",
    "sessions_container": ".YOUR_SESSIONS_CONTAINER",
    "session_row": ".YOUR_SESSION_ROW",
    "date": ".YOUR_DATE_SELECTOR",
    "coherence_score": ".YOUR_COHERENCE_SELECTOR",
    "session_length": ".YOUR_LENGTH_SELECTOR",
    "achievement_score": ".YOUR_ACHIEVEMENT_SELECTOR",
}
```

## 🧪 Step 3: Test Locally First

Before deploying to GitHub Actions, test the scraper on your computer:

### 3.1: Install Dependencies

```bash
pip install selenium gspread google-auth webdriver-manager
```

### 3.2: Download ChromeDriver

**Option A: Automatic (easier)**
```bash
pip install webdriver-manager
```

Then modify the script to use:
```python
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
```

**Option B: Manual**
1. Check Chrome version: chrome://version
2. Download matching ChromeDriver from: https://chromedriver.chromium.org/
3. Place in your PATH or specify location in script

### 3.3: Set Environment Variables

**Mac/Linux:**
```bash
export HEARTCLOUD_EMAIL="your-email@example.com"
export HEARTCLOUD_PASSWORD="your-password"
export GCP_TYPE="service_account"
export GCP_PROJECT_ID="your-project-id"
# ... (all other GCP_ variables)
```

**Windows:**
```cmd
set HEARTCLOUD_EMAIL=your-email@example.com
set HEARTCLOUD_PASSWORD=your-password
set GCP_TYPE=service_account
# ... (all other GCP_ variables)
```

### 3.4: Run the Script

```bash
python sync_heartcloud_scraper.py
```

**What to watch for:**
- ✅ "Successfully logged into HeartCloud"
- ✅ "Found X session(s)"
- ✅ "Coherence: 5.8" (or your actual score)
- ✅ "Successfully wrote to Google Sheets"

**If it fails:**
- Check the screenshot: `/tmp/heartcloud_error.png`
- Check the page source: `/tmp/heartcloud_page_source.html`
- Review the selectors and update them

## 🔧 Step 4: Debugging Common Issues

### Issue 1: "Could not find email field"
**Solution:**
- Your selector is wrong
- Inspect the element again
- Try different selectors:
  - `#email`
  - `input[name='email']`
  - `input[type='email']`
  - `.email-input`

### Issue 2: "Still on login page"
**Causes:**
- Wrong email/password
- Selector is correct but credentials are wrong
- HeartCloud requires 2FA or CAPTCHA
- HeartCloud detects automation

**Solutions:**
- Verify credentials by manual login
- Check if 2FA is enabled (may not be scrapable)
- Add `time.sleep(10)` after login to wait longer
- Try adding cookies from a manual session

### Issue 3: "Could not find sessions"
**Causes:**
- You're on the wrong page
- Session selector is incorrect
- Sessions are loaded via JavaScript (need to wait longer)

**Solutions:**
- Print `driver.current_url` to see where you landed
- Try different URLs: `/home`, `/sessions`, `/history`, `/dashboard`
- Increase wait time: `time.sleep(5)`
- Look at the page source saved to `/tmp/heartcloud_page_source.html`

### Issue 4: "Coherence score not found"
**Solution:**
- The selector is wrong
- Inspect the exact element containing the score
- Try these selectors:
  - `.coherence`
  - `.score`
  - `[data-coherence]`
  - `span.value`

## 🚀 Step 5: Deploy to GitHub Actions

Once the script works locally, add it to your health-tracker repo:

### 5.1: Add Script to Repo

```bash
cd health-tracker
# Copy the working script
cp /path/to/sync_heartcloud_scraper.py .
git add sync_heartcloud_scraper.py
git commit -m "Add HeartCloud scraper"
git push
```

### 5.2: Create GitHub Actions Workflow

Create `.github/workflows/sync_heartcloud.yml`:

```yaml
name: Daily HeartCloud Sync

on:
  schedule:
    - cron: '15 9 * * *'  # 9:15 AM UTC daily
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install selenium gspread google-auth
      
      - name: Install Chrome
        run: |
          wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable
      
      - name: Install ChromeDriver
        run: |
          CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
          DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
          wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
          unzip chromedriver_linux64.zip
          sudo mv chromedriver /usr/local/bin/
          sudo chmod +x /usr/local/bin/chromedriver
      
      - name: Run scraper
        env:
          HEARTCLOUD_EMAIL: ${{ secrets.HEARTCLOUD_EMAIL }}
          HEARTCLOUD_PASSWORD: ${{ secrets.HEARTCLOUD_PASSWORD }}
          GCP_TYPE: ${{ secrets.GCP_TYPE }}
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          GCP_PRIVATE_KEY_ID: ${{ secrets.GCP_PRIVATE_KEY_ID }}
          GCP_PRIVATE_KEY: ${{ secrets.GCP_PRIVATE_KEY }}
          GCP_CLIENT_EMAIL: ${{ secrets.GCP_CLIENT_EMAIL }}
          GCP_CLIENT_ID: ${{ secrets.GCP_CLIENT_ID }}
          GCP_CERT_URL: ${{ secrets.GCP_CERT_URL }}
        run: |
          python sync_heartcloud_scraper.py
```

### 5.3: Add GitHub Secrets

Go to your repo → Settings → Secrets → Actions → New repository secret:

```
Name: HEARTCLOUD_EMAIL
Value: your-email@example.com

Name: HEARTCLOUD_PASSWORD
Value: your-password
```

### 5.4: Test the Workflow

1. Go to Actions tab in your repo
2. Find "Daily HeartCloud Sync"
3. Click "Run workflow" → "Run workflow"
4. Watch it run and check for errors

## 📊 Step 6: Verify Data in Dashboard

1. Wait for the workflow to complete
2. Check your Google Sheets - should see coherence data
3. Open your dashboard: health-tracker-0lrm.onrender.com
4. Navigate to the coherence chart
5. Verify the data appears!

## 🛠️ Advanced: Alternative Selector Strategies

If standard CSS selectors don't work, try:

### 1. XPath Selectors

```python
# Instead of CSS selector
element = driver.find_element(By.CSS_SELECTOR, ".score")

# Use XPath
element = driver.find_element(By.XPATH, "//span[@class='score']")
```

### 2. Text Content

```python
# Find element by its text
element = driver.find_element(By.XPATH, "//span[contains(text(), 'Coherence')]")
```

### 3. Attribute Selectors

```python
# Find by data attribute
element = driver.find_element(By.CSS_SELECTOR, "[data-metric='coherence']")
```

### 4. Parent/Child Relationships

```python
# Find coherence within a specific parent
parent = driver.find_element(By.CSS_SELECTOR, ".session-metrics")
coherence = parent.find_element(By.CSS_SELECTOR, ".coherence-value")
```

## 🆘 Still Stuck?

If you're having trouble finding selectors:

1. **Take screenshots** of the HeartCloud pages
2. **Save the HTML source** (Right-click → View Page Source)
3. **Share with me** and I can help identify the selectors
4. **Check if HeartCloud has an API** (contact their support)

## 📋 Summary Checklist

- [ ] Opened HeartCloud in browser
- [ ] Used Inspector to find email field selector
- [ ] Found password field selector
- [ ] Found login button selector
- [ ] Found sessions container selector
- [ ] Found individual session row selector
- [ ] Found coherence score selector
- [ ] Updated SELECTORS dictionary in script
- [ ] Tested script locally
- [ ] Script successfully logs in
- [ ] Script successfully scrapes coherence
- [ ] Script writes to Google Sheets
- [ ] Added script to GitHub repo
- [ ] Created GitHub Actions workflow
- [ ] Added HEARTCLOUD secrets to GitHub
- [ ] Tested workflow manually
- [ ] Workflow runs successfully
- [ ] Data appears in Google Sheets
- [ ] Data appears in dashboard

Once all checkboxes are complete, your HeartCloud data will sync automatically every day at 9:15 AM! 🎉
