import os
import json
from datetime import datetime, timedelta
import requests
import gspread
from google.oauth2.service_account import Credentials

# Strava API configuration
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.environ.get("STRAVA_REFRESH_TOKEN")

# Google Sheets configuration
SHEET_ID = "1qc_8gnDFMkwnT3j2i_BFBWFqsLymroqVf-rrQuGzzOc"
WORKSHEET_NAME = "strava_workouts"

def get_strava_access_token():
    """Get fresh access token using refresh token"""
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "refresh_token": STRAVA_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    
    print(f"Requesting new access token from Strava...")
    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        print(f"ERROR: Failed to get access token. Status: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
    
    token_data = response.json()
    print(f"Successfully obtained access token")
    return token_data["access_token"]

def get_strava_activities(access_token, after_date):
    """Fetch activities from Strava after a specific date"""
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Convert date to Unix timestamp
    after_timestamp = int(datetime.strptime(after_date, "%Y-%m-%d").timestamp())
    
    params = {
        "after": after_timestamp,
        "per_page": 30
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_activity_details(access_token, activity_id):
    """Get detailed activity data including heart rate zones"""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def parse_strava_data(activities, access_token):
    """Parse Strava activities into structured data"""
    workouts = []
    
    for activity in activities:
        # Get detailed data for heart rate zones
        details = get_activity_details(access_token, activity["id"])
        
        # Parse heart rate zones
        hr_zones = details.get("heartrate_zones", {})
        zone_1 = zone_2 = zone_3 = zone_4 = zone_5 = None
        
        if hr_zones:
            zones = hr_zones.get("zones", [])
            if len(zones) >= 5:
                zone_1 = zones[0].get("time", 0) / 60  # Convert to minutes
                zone_2 = zones[1].get("time", 0) / 60
                zone_3 = zones[2].get("time", 0) / 60
                zone_4 = zones[3].get("time", 0) / 60
                zone_5 = zones[4].get("time", 0) / 60
        
        workout = {
            "date": activity["start_date_local"].split("T")[0],
            "time": activity["start_date_local"].split("T")[1].split("Z")[0],
            "workout_type": activity.get("type", "Unknown"),
            "name": activity.get("name", ""),
            "duration_min": round(activity.get("moving_time", 0) / 60, 1),
            "distance_km": round(activity.get("distance", 0) / 1000, 2),
            "avg_hr": activity.get("average_heartrate"),
            "max_hr": activity.get("max_heartrate"),
            "calories": activity.get("calories"),
            "avg_power": activity.get("average_watts"),
            "max_power": activity.get("max_watts"),
            "zone_1_min": round(zone_1, 1) if zone_1 else None,
            "zone_2_min": round(zone_2, 1) if zone_2 else None,
            "zone_3_min": round(zone_3, 1) if zone_3 else None,
            "zone_4_min": round(zone_4, 1) if zone_4 else None,
            "zone_5_min": round(zone_5, 1) if zone_5 else None,
        }
        
        workouts.append(workout)
    
    return workouts

def write_to_google_sheets(workouts):
    """Write Strava workout data to Google Sheets"""
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
            "date", "time", "workout_type", "name", "duration_min", "distance_km",
            "avg_hr", "max_hr", "calories", "avg_power", "max_power",
            "zone_1_min", "zone_2_min", "zone_3_min", "zone_4_min", "zone_5_min"
        ]
        worksheet.append_row(headers)
    
    # Get existing data to avoid duplicates
    all_values = worksheet.get_all_values()
    existing_workouts = set()
    for row in all_values[1:]:  # Skip header
        if len(row) >= 2:
            # Create unique key from date and time
            existing_workouts.add(f"{row[0]}_{row[1]}")
    
    # Add new workouts
    new_count = 0
    for workout in workouts:
        workout_key = f"{workout['date']}_{workout['time']}"
        
        if workout_key not in existing_workouts:
            row_data = [
                workout["date"],
                workout["time"],
                workout["workout_type"],
                workout["name"],
                workout["duration_min"],
                workout["distance_km"],
                workout["avg_hr"],
                workout["max_hr"],
                workout["calories"],
                workout["avg_power"],
                workout["max_power"],
                workout["zone_1_min"],
                workout["zone_2_min"],
                workout["zone_3_min"],
                workout["zone_4_min"],
                workout["zone_5_min"],
            ]
            
            # Convert None to empty string
            row_data = [str(x) if x is not None else "" for x in row_data]
            
            worksheet.append_row(row_data)
            new_count += 1
            print(f"Added workout: {workout['date']} {workout['time']} - {workout['workout_type']}")
    
    return new_count

def main():
    """Main function to fetch recent Strava activities and write to Google Sheets"""
    # Get activities from the last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Fetching Strava activities since {week_ago}...")
    
    # Get access token
    access_token = get_strava_access_token()
    
    # Get activities
    activities = get_strava_activities(access_token, week_ago)
    print(f"Found {len(activities)} activities")
    
    if not activities:
        print("No new activities found")
        return
    
    # Parse activity data
    workouts = parse_strava_data(activities, access_token)
    
    # Write to Google Sheets
    print("Writing to Google Sheets...")
    new_count = write_to_google_sheets(workouts)
    
    print(f"✅ Successfully added {new_count} new workouts")

if __name__ == "__main__":
    main()
