import os
import json
from datetime import datetime, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials

# Oura API configuration
OURA_TOKEN = os.environ.get("OURA_TOKEN")
OURA_API_BASE = "https://api.ouraring.com/v2/usercollection"

# Google Sheets configuration
SHEET_ID = "1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc"
WORKSHEET_NAME = "oura_data"

def get_oura_data(date):
    """Fetch all Oura data for a specific date"""
    headers = {"Authorization": f"Bearer {OURA_TOKEN}"}
    
    data = {
        "date": date,
        "sleep_score": None,
        "readiness_score": None,
        "activity_score": None,
        "total_sleep": None,
        "deep_sleep": None,
        "rem_sleep": None,
        "light_sleep": None,
        "awake_time": None,
        "sleep_efficiency": None,
        "restless_periods": None,
        "sleep_latency": None,
        "hrv_avg": None,
        "resting_hr": None,
        "lowest_hr": None,
        "avg_hr": None,
        "body_temp": None,
        "steps": None,
        "calories": None,
        "active_calories": None,
        "met_min_high": None,
        "met_min_medium": None,
        "met_min_low": None,
    }
    
    # Get Sleep data
    try:
        sleep_url = f"{OURA_API_BASE}/daily_sleep"
        sleep_params = {"start_date": date, "end_date": date}
        sleep_response = requests.get(sleep_url, headers=headers, params=sleep_params)
        sleep_response.raise_for_status()
        sleep_data = sleep_response.json().get("data", [])
        
        if sleep_data:
            sleep = sleep_data[0]["contributors"]
            data["sleep_score"] = sleep_data[0].get("score")
            data["total_sleep"] = sleep.get("total_sleep")
            data["deep_sleep"] = sleep.get("deep_sleep")
            data["rem_sleep"] = sleep.get("rem_sleep")
            data["light_sleep"] = sleep.get("light_sleep")
            data["awake_time"] = sleep.get("awake_time")
            data["sleep_efficiency"] = sleep.get("efficiency")
            data["restless_periods"] = sleep.get("restless_periods")
            data["sleep_latency"] = sleep.get("latency")
    except Exception as e:
        print(f"Error fetching sleep data: {e}")
    
    # Get Readiness data
    try:
        readiness_url = f"{OURA_API_BASE}/daily_readiness"
        readiness_params = {"start_date": date, "end_date": date}
        readiness_response = requests.get(readiness_url, headers=headers, params=readiness_params)
        readiness_response.raise_for_status()
        readiness_data = readiness_response.json().get("data", [])
        
        if readiness_data:
            data["readiness_score"] = readiness_data[0].get("score")
            contributors = readiness_data[0].get("contributors", {})
            data["hrv_avg"] = contributors.get("hrv_balance")
            data["resting_hr"] = contributors.get("resting_heart_rate")
            data["body_temp"] = contributors.get("body_temperature")
    except Exception as e:
        print(f"Error fetching readiness data: {e}")
    
    # Get Activity data
    try:
        activity_url = f"{OURA_API_BASE}/daily_activity"
        activity_params = {"start_date": date, "end_date": date}
        activity_response = requests.get(activity_url, headers=headers, params=activity_params)
        activity_response.raise_for_status()
        activity_data = activity_response.json().get("data", [])
        
        if activity_data:
            data["activity_score"] = activity_data[0].get("score")
            data["steps"] = activity_data[0].get("steps")
            data["calories"] = activity_data[0].get("total_calories")
            data["active_calories"] = activity_data[0].get("active_calories")
            
            contributors = activity_data[0].get("contributors", {})
            data["met_min_high"] = contributors.get("meet_daily_targets")
            data["met_min_medium"] = contributors.get("move_every_hour")
            data["met_min_low"] = contributors.get("training_frequency")
            data["avg_hr"] = activity_data[0].get("average_met_minutes")
    except Exception as e:
        print(f"Error fetching activity data: {e}")
    
    # Get Heart Rate data
    try:
        hr_url = f"{OURA_API_BASE}/heartrate"
        hr_params = {"start_date": date, "end_date": date}
        hr_response = requests.get(hr_url, headers=headers, params=hr_params)
        hr_response.raise_for_status()
        hr_data = hr_response.json().get("data", [])
        
        if hr_data:
            # Calculate average and lowest HR from the day's data
            heart_rates = [item["bpm"] for item in hr_data if item.get("bpm")]
            if heart_rates:
                data["avg_hr"] = sum(heart_rates) / len(heart_rates)
                data["lowest_hr"] = min(heart_rates)
    except Exception as e:
        print(f"Error fetching heart rate data: {e}")
    
    return data

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
        worksheet = sheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=30)
        headers = [
            "date", "sleep_score", "readiness_score", "activity_score",
            "total_sleep", "deep_sleep", "rem_sleep", "light_sleep",
            "awake_time", "sleep_efficiency", "restless_periods", "sleep_latency",
            "hrv_avg", "resting_hr", "lowest_hr", "avg_hr", "body_temp",
            "steps", "calories", "active_calories",
            "met_min_high", "met_min_medium", "met_min_low"
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
        data["awake_time"],
        data["sleep_efficiency"],
        data["restless_periods"],
        data["sleep_latency"],
        data["hrv_avg"],
        data["resting_hr"],
        data["lowest_hr"],
        data["avg_hr"],
        data["body_temp"],
        data["steps"],
        data["calories"],
        data["active_calories"],
        data["met_min_high"],
        data["met_min_medium"],
        data["met_min_low"],
    ]
    
    # Convert None to empty string for Google Sheets
    row_data = [str(x) if x is not None else "" for x in row_data]
    
    if row_index:
        # Update existing row
        worksheet.update(f"A{row_index}:W{row_index}", [row_data])
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
