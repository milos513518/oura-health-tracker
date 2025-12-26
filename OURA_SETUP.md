# Oura to Google Sheets - Automated Daily Sync

Automatically fetches your Oura ring data every day at 9 AM and adds it to Google Sheets.

## What Gets Tracked

**Sleep Metrics:**
- Sleep score, Total sleep time, Deep sleep, REM sleep, Light sleep
- Awake time, Sleep efficiency, Restless periods, Sleep latency

**Readiness Metrics:**
- Readiness score, HRV average, Resting heart rate, Body temperature

**Activity Metrics:**
- Activity score, Steps, Total calories, Active calories
- MET minutes (high/medium/low intensity)

**Heart Rate:**
- Average HR, Lowest HR throughout the day

## Setup Instructions (5 minutes)

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `oura-health-tracker`
3. Make it **Private** (to keep your health data secure)
4. Click "Create repository"

### 2. Upload Files

1. Download these 2 files:
   - `oura_to_sheets.py`
   - `oura_sync.yml`

2. In your GitHub repo, click "Add file" → "Upload files"
3. Upload both files
4. **IMPORTANT:** Create this folder structure:
   - `oura_to_sheets.py` goes in the root
   - `oura_sync.yml` goes in `.github/workflows/` folder
   
   To create the folder: Click "Add file" → "Create new file", type `.github/workflows/oura_sync.yml`, paste the content

5. Click "Commit changes"

### 3. Add Secrets to GitHub

1. In your repo, click "Settings" → "Secrets and variables" → "Actions"
2. Click "New repository secret"

**Secret 1:**
- Name: `OURA_TOKEN`
- Value: `M2YXJS7XYMQBOTI5DF5JWZRQPIL3EVHG`

**Secret 2:**
- Name: `GOOGLE_CREDENTIALS_JSON`
- Value: (paste your complete service account JSON - the same one from before)

```json
{
  "type": "service_account",
  "project_id": "health-tracker-481311",
  "private_key_id": "39e63a6cef61c13560cb36f87e89ef17119d865d",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...YOUR FULL KEY...\n-----END PRIVATE KEY-----\n",
  "client_email": "health-tracker-bot@health-tracker-481311.iam.gserviceaccount.com",
  "client_id": "105707944059291015405",
  ...
}
```

3. Click "Add secret" for each one

### 4. Set Your Timezone

The workflow is currently set for **9 AM Pacific Time**.

If you're in a different timezone:
1. Edit `.github/workflows/oura_sync.yml`
2. Change the cron schedule:
   - `0 17 * * *` = 9 AM Pacific (PST/PDT)
   - `0 14 * * *` = 9 AM Eastern (EST/EDT)
   - `0 13 * * *` = 9 AM Central
   - `0 12 * * *` = 9 AM Mountain

### 5. Enable GitHub Actions

1. Go to your repo → "Actions" tab
2. Click "I understand my workflows, go ahead and enable them"

### 6. Test It Manually

1. Go to "Actions" tab
2. Click "Daily Oura Data Sync" on the left
3. Click "Run workflow" → "Run workflow"
4. Wait 30 seconds, refresh the page
5. You should see a green checkmark ✅

### 7. Check Your Google Sheet

1. Open your sheet: https://docs.google.com/spreadsheets/d/1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc
2. You should see a new worksheet called "oura_data"
3. It should have yesterday's Oura data

## What Happens Now

Every day at 9 AM, GitHub Actions will:
1. Fetch yesterday's Oura data
2. Add it to your Google Sheet
3. If data for that date already exists, it updates it

## Troubleshooting

**No data appearing?**
- Check Actions tab for error messages
- Make sure secrets are set correctly
- Verify your Oura token is still valid

**Wrong timezone?**
- Update the cron schedule in the workflow file

**Want to run it now?**
- Go to Actions → Daily Oura Data Sync → Run workflow

## Next Steps

Once this is working, we can add:
- ResMed CPAP data
- Continuous glucose monitor data  
- Wahoo workout data

All in the same master Google Sheet for correlation analysis!
