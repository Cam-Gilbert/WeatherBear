import os
import json
from backend.data_fetcher import Data_Fetcher
from backend.storm import Storm
from backend.region import Region
from backend.summarizer import Summarizer
from filelock import FileLock

## this is going to need to change once moved to hosted platform.
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

    # make region objects
    region_map = {
        "Atlantic": Region("Atlantic"),
        "Eastern_Pacific": Region("Eastern_Pacific"),
        "Central_Pacific": Region("Central_Pacific"),
    }

    # load discussions into the region object
    for region in region_map:
        twd = tropical_data.get(region, {}).get("twd_discussion", {})
        region_map[region].discussion = twd.get("discussion")

    # create storms and save to regions storm list
    for storm_meta in storm_codes:
        region_name = storm_meta["region"]
        storm_name = storm_meta["name"]
        storm_id = storm_meta["code"]
        region_dict = tropical_data.get(region_name, {})
        storm_dict = region_dict.get(storm_name, {})

        storm_obj = Storm(
            name=storm_name,
            id=storm_id,
            region=region_name,
            storm_center=storm_dict.get("summary", {}).get("nhc:position", ""),
            movement=storm_dict.get("summary", {}).get("nhc:motion", ""),
            pressure=storm_dict.get("summary", {}).get("nhc:pressure", ""),
            type=storm_dict.get("summary", {}).get("nhc:stormType", ""),
            wind_speed=storm_dict.get("summary", {}).get("nhc:wind", ""),
            discussion=storm_dict.get("discussions"),
            shapefile_path=storm_dict.get("shapefile_path"),
            advisories=storm_dict.get("advisories"),
            local_statements=storm_dict.get("local_statements")
        )

        region_map[region_name].add_storm(storm_obj)

    # Generate summariews
    knowledge_levels = ["no_summary", "none", "moderate", "expert"]
    all_data = []

    for region in region_map.values():
        for level in knowledge_levels:
            summarizer = Summarizer(level, afd=None, twd_discussion=region.discussion)
            summary_text = summarizer.generate_Region_Summary()

            if level != "no_summary":
                summary_text = f"Issued for {region.name}\n\n" + summary_text

            all_data.append({
                "region": region.name,
                "knowledge_level": level,
                "issued": None,  # You can restore this if TWD includes an "issued" time
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