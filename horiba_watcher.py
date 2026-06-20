import urllib.request
import json
import time
from datetime import datetime

URL = 'http://192.168.1.3:8080/queries'
POLL_INTERVAL = 10 # Seconds to wait between checks

def fetch_data():
    # Get current date
    now = datetime.now()
    end_date = now.strftime("%Y-%m-%dT23:59:59.999+05:30")
    
    payload = {
        "query": {
            "type": "GetHistoricalData",
            "payload": {
                "readingType": ["Sample"], # Patient samples only
                "sampleId": None,
                "techniqueId": None,
                "startDate": None,
                "endDate": end_date,
                "timePeriod": "ONE_DAY"
            }
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(URL, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    
    try:
        # Request data from the machine
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read())
        return result.get('historicalData', [])
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Connection Error: {e}")
        return None

def print_record(record):
    """Formats and prints a single new test result"""
    sample_id = record.get('sampleId', 'Unknown')
    test_name = record.get('techniqueName', 'Unknown Test')
    
    try:
        value = record['measure']['replicas'][0]['result']
        units = record.get('sampleUnits', '')
        time_raw = record.get('occurredAt', '')
        time_formatted = time_raw.split('T')[1] if 'T' in time_raw else time_raw
        
        print(f"🚨 [NEW RESULT] Time: {time_formatted} | Sample ID: {sample_id:<6} | Test: {test_name:<15} | Result: {value} {units}")
    except (KeyError, IndexError):
        print(f"🚨 [NEW RESULT] Sample: {sample_id} | Test: {test_name} | (Could not extract value)")

def watch_machine():
    print(f"Starting Horiba Watcher. Connecting to {URL}...")
    
    # This set will remember the unique IDs of all records we have already seen
    seen_ids = set()
    
    # 1. INITIAL SYNC: Download everything currently on the machine so we don't print old data
    print("Performing initial sync to memorize existing records...")
    initial_records = fetch_data()
    
    if initial_records is not None:
        for record in initial_records:
            if 'id' in record:
                seen_ids.add(record['id'])
        print(f"✅ Memorized {len(seen_ids)} existing records. Now watching for NEW results...")
    else:
        print("⚠️ Could not connect on initial sync. Will keep trying...")
    
    print("-" * 75)
    print("Monitoring... (Leave this window open)")
    
    # 2. INFINITE LOOP: Check every 10 seconds forever
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            
            records = fetch_data()
            if records is None:
                continue # Skip this loop if there was a connection error
                
            for record in records:
                record_id = record.get('id')
                
                # If the machine gives us a record ID we haven't seen yet...
                if record_id and record_id not in seen_ids:
                    print_record(record)    # Print it to the screen!
                    seen_ids.add(record_id) # Add it to our memory so we don't print it again
                
    except KeyboardInterrupt:
        print("\nWatcher stopped by user.")

if __name__ == "__main__":
    watch_machine()
