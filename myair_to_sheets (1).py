import os
import json
from datetime import datetime, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials

# myAir credentials
MYAIR_EMAIL = os.environ.get("MYAIR_EMAIL")
MYAIR_PASSWORD = os.environ.get("MYAIR_PASSWORD")

# Google Sheets configuration
SHEET_ID = "1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc"
WORKSHEET_NAME = "resmed_cpap"

def login_myair():
    """Login to myAir and get session"""
    session = requests.Session()
    
    # myAir login endpoint
    login_url = "https://myair.resmed.com/Default/Login"
    
    # Get login page first to get any tokens
    response = session.get(login_url)
    
    # Login payload
    login_data = {
        "username": MYAIR_EMAIL,
        "password": MYAIR_PASSWORD,
        "rememberMe": "false"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    print("Logging into myAir...")
    response = session.post(login_url, data=login_data, headers=headers, allow_redirects=True)
    
    if response.status_code != 200:
        print(f"Login failed. Status: {response.status_code}")
        return None
    
    print("Login successful")
    return session

def get_myair_data(session, date):
    """Get CPAP data for a specific date"""
    # Format date for myAir API
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    
    # myAir API endpoint for sleep records
    api_url = "https://myair.resmed.com/SleepData/GetSleepData"
    
    params = {
        "date": date_obj.strftime("%Y-%m-%d")
    }
    
    print(f"Fetching data for {date}...")
    response = session.get(api_url, params=params)
    
    if response.status_code != 200:
        print(f"Failed to get data. Status: {response.status_code}")
        return None
    
    data = response.json()
    
    # Parse the data
    sleep_record = {
        "date": date,
        "ahi": None,
        "leak": None,
        "hours_used": None,
        "mask_seal": None,
        "events": None,
        "myair_score": None
    }
    
    if data and len(data) > 0:
        record = data[0]
        sleep_record["ahi"] = record.get("ahi")
        sleep_record["leak"] = record.get("maskPairCount")
        sleep_record["hours_used"] = record.get("usageHours")
        sleep_record["mask_seal"] = record.get("maskPairScore")
        sleep_record["events"] = record.get("totalEvents")
        sleep_record["myair_score"] = record.get("myAirScore")
    
    return sleep_record

def write_to_google_sheets(cpap_data):
    """Write CPAP data to Google Sheets"""
    # Load credentials
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON not found")
    
    credentials_dict = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    
    # Connect to Google Sheets
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SHEET_ID)
    
    # Try to get or create worksheet
    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=10)
        headers = [
            "date", "ahi", "leak", "hours_used", "mask_seal", 
            "events", "myair_score"
        ]
        worksheet.append_row(headers)
    
    # Check if data exists for this date
    all_values = worksheet.get_all_values()
    date_str = cpap_data["date"]
    
    row_index = None
    for i, row in enumerate(all_values[1:], start=2):
        if row and row[0] == date_str:
            row_index = i
            break
    
    # Prepare row
    row_data = [
        cpap_data["date"],
        cpap_data["ahi"],
        cpap_data["leak"],
        cpap_data["hours_used"],
        cpap_data["mask_seal"],
        cpap_data["events"],
        cpap_data["myair_score"]
    ]
    
    row_data = [str(x) if x is not None else "" for x in row_data]
    
    if row_index:
        worksheet.update(f"A{row_index}:G{row_index}", [row_data])
        print(f"Updated data for {date_str}")
    else:
        worksheet.append_row(row_data)
        print(f"Added new data for {date_str}")

def main():
    """Main function"""
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Login to myAir
    session = login_myair()
    if not session:
        print("Failed to login to myAir")
        return
    
    # Get CPAP data
    cpap_data = get_myair_data(session, yesterday)
    
    if not cpap_data:
        print("No data found")
        return
    
    # Write to Google Sheets
    print("Writing to Google Sheets...")
    write_to_google_sheets(cpap_data)
    
    print(f"✅ Successfully updated CPAP data for {yesterday}")

if __name__ == "__main__":
    main()
