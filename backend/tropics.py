import os
import json
from backend.data_fetcher import Data_Fetcher
from backend.summarizer import Summarizer
from filelock import FileLock

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'WeatherBear', 'mnt', 'data')
SUMMARY_PATH = os.path.join(DATA_DIR, 'tropics_data.json')
LOCK_PATH = SUMMARY_PATH + '.lock'

def main_tropics_loop():
    '''
    Loops thru list of storms and downloads all of their shape files from the nhc, also generates summarizations at each level for the atlantic, east pac, and cent pac regions
    '''
    df = Data_Fetcher(None, "metric")
    tropical_data, storm_codes = df.get_tropical_data()

    # Download shape files
    df.download_shape_files(storm_codes=storm_codes)

    # Build summaries
    atl_issued = tropical_data['Atlantic']['twd_discussion']['issued']
    cp_issued = tropical_data['Central_Pacific']['twd_discussion']['issued']
    ep_issued = tropical_data['Eastern_Pacific']['twd_discussion']['issued']

    # need to generate 4 summaries for each region.     
    regions = ["Atlantic", "Central_Pacific", "Eastern_Pacific"]
    knowledge_levels = ["no_summary", "none", "moderate", "expert"]

    region_data = {
        region: {
            "discussion": tropical_data[region]['twd_discussion']['discussion'],
            "issued": tropical_data[region]['twd_discussion']['issued']
        }
        for region in regions
    }

    # Container for all results
    all_data = []

    for region in regions:
        discussion = region_data[region]["discussion"]
        issued = region_data[region]["issued"]

        for level in knowledge_levels:
            summarizer = Summarizer(level, afd=None, twd_discussion=discussion, storm_discussion=None)
            summary_text = summarizer.generate_Region_Summary()

            if level != "no_summary":
                summary_text = f"Issued at {issued}\n\n" + summary_text

            all_data.append({
                "region": region,
                "knowledge_level": level,
                "issued": issued,
                "summary": summary_text
            })

    print(f"Prepared {len(all_data)} summaries, saving now...")
    save_summaries(all_data)
    print("Save complete.")


def save_summaries(summaries):
    '''
    Save a list of summary dicts to JSON with file lock
    '''
    print(f"Attempting to save to: {SUMMARY_PATH}")
    try:
        os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
        print(f"Directory exists or created: {os.path.dirname(SUMMARY_PATH)}")

        lock = FileLock(LOCK_PATH)
        with lock:
            with open(SUMMARY_PATH, "w") as f:
                json.dump(summaries, f, indent=2)
        print("File written successfully.")
    except Exception as e:
        print(f"Exception during save_summaries: {e}")

def load_summaries():
    '''
    Load list of summary dicts from JSON with file lock
    '''
    lock = FileLock(LOCK_PATH)
    with lock:
        if not os.path.exists(SUMMARY_PATH):
            # Ensure directory exists and create empty file on first use
            os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
            with open(SUMMARY_PATH, "w") as f:
                json.dump([], f)
            return []
        with open(SUMMARY_PATH, "r") as f:
            return json.load(f)