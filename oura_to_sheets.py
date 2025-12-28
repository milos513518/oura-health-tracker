import os
import json
from datetime import datetime, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials

# Oura API configuration
OURA_TOKEN = os.environ.get("OURA_TOKEN")

# Google Sheets configuration
SHEET_ID = "1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc"
WORKSHEET_NAME = "oura_data"

def get_oura_sleep(date, headers):
    """Get sleep data from Oura API v2"""
    url = "https://api.ouraring.com/v2/usercollection/daily_sleep"
    params = {"start_date": date, "end_date": date}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json().get("data", [])
    return data[0] if data else None

def get_oura_readiness(date, headers):
    """Get readiness data from Oura API v2"""
    url = "https://api.ouraring.com/v2/usercollection/daily_readiness"
    params = {"start_date": date, "end_date": date}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json().get("data", [])
    return data[0] if data else None

def get_oura_activity(date, headers):
    """Get activity data from Oura API v2"""
    url = "https://api.ouraring.com/v2/usercollection/daily_activity"
    params = {"start_date": date, "end_date": date}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json().get("data", [])
    return data[0] if data else None

def get_oura_data(date):
    """Fetch all Oura data for a specific date"""
    headers = {"Authorization": f"Bearer {OURA_TOKEN}"}
    
    result = {
        "date": date,
        "sleep_score": None,
        "readiness_score": None,
        "activity_score": None,
        "total_sleep": None,
        "deep_sleep": None,
        "rem_sleep": None,
        "light_sleep": None,
        "sleep_efficiency": None,
        "hrv_avg": None,
        "resting_hr": None,
        "body_temp": None,
        "steps": None,
        "calories": None,
    }
    
    try:
        sleep_data = get_oura_sleep(date, headers)
        if sleep_data:
            result["sleep_score"] = sleep_data.get("score")
            contributors = sleep_data.get("contributors", {})
            result["total_sleep"] = contributors.get("total_sleep")
            result["deep_sleep"] = contributors.get("deep_sleep")
            result["rem_sleep"] = contributors.get("rem_sleep")
            result["light_sleep"] = contributors.get("light_sleep")
            result["sleep_efficiency"] = contributors.get("efficiency")
    except Exception as e:
        print(f"Error fetching sleep data: {e}")
    
    try:
        readiness_data = get_oura_readiness(date, headers)
        if readiness_data:
            result["readiness_score"] = readiness_data.get("score")
            contributors = readiness_data.get("contributors", {})
            result["hrv_avg"] = contributors.get("hrv_balance")
            result["resting_hr"] = contributors.get("resting_heart_rate")
            result["body_temp"] = contributors.get("body_temperature")
    except Exception as e:
        print(f"Error fetching readiness data: {e}")
    
    try:
        activity_data = get_oura_activity(date, headers)
        if activity_data:
            result["activity_score"] = activity_data.get("score")
            result["steps"] = activity_data.get("steps")
            result["calories"] = activity_data.get("total_calories")
    except Exception as e:
        print(f"Error fetching activity data: {e}")
    
    return result

def write_to_google_sheets(data):
    """Write Oura data to Google Sheets"""
    # Load credentials from environment variable
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON not found in environment")
    
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
    
    # Try to get or create the worksheet
    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        # Create worksheet with headers if it doesn't exist
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=20)
        headers = [
            "date", "sleep_score", "readiness_score", "activity_score",
            "total_sleep", "deep_sleep", "rem_sleep", "light_sleep",
            "sleep_efficiency", "hrv_avg", "resting_hr", "body_temp",
            "steps", "calories"
        ]
        worksheet.append_row(headers)
    
    # Check if data for this date already exists
    all_values = worksheet.get_all_values()
    date_str = data["date"]
    
    # Find if row exists for this date
    row_index = None
    for i, row in enumerate(all_values[1:], start=2):  # Skip header
        if row and row[0] == date_str:
            row_index = i
            break
    
    # Prepare row data
    row_data = [
        data["date"],
        data["sleep_score"],
        data["readiness_score"],
        data["activity_score"],
        data["total_sleep"],
        data["deep_sleep"],
        data["rem_sleep"],
        data["light_sleep"],
        data["sleep_efficiency"],
        data["hrv_avg"],
        data["resting_hr"],
        data["body_temp"],
        data["steps"],
        data["calories"],
    ]
    
    # Convert None to empty string for Google Sheets
    row_data = [str(x) if x is not None else "" for x in row_data]
    
    if row_index:
        # Update existing row
        worksheet.update(f"A{row_index}:N{row_index}", [row_data])
        print(f"Updated existing data for {date_str}")
    else:
        # Append new row
        worksheet.append_row(row_data)
        print(f"Added new data for {date_str}")

def main():
    """Main function to fetch yesterday's Oura data and write to Google Sheets"""
    # Get yesterday's date (Oura data is typically available for the previous day)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Fetching Oura data for {yesterday}...")
    oura_data = get_oura_data(yesterday)
    
    print(f"Writing data to Google Sheets...")
    write_to_google_sheets(oura_data)
    
    print(f"✅ Successfully updated Oura data for {yesterday}")

if __name__ == "__main__":
    main()
