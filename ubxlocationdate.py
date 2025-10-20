import argparse
import gzip
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timezone
from pyubx2 import UBXReader


def collect_info_from_file(path: Path) -> List[Tuple[datetime, float, float]]:
    """Return list of (datetime, lat, lon) tuples from a single .ubz file.

    datetime is built from NAV-PVT fields year, month, day, hour, min, sec
    (nanoseconds -> microseconds when available). The datetime is timezone-naive
    but represents UTC time.
    """

    records: List[Tuple[datetime, float, float]] = []
    with gzip.open(path, "rb") as stream:
        ubr = UBXReader(stream, validate=False)
        for raw, parsed in ubr:
            # NAV-PVT contains lat, lon and date/time fields
            if getattr(parsed, "identity", None) == "NAV-PVT":
                lat = getattr(parsed, "lat", None)
                lon = getattr(parsed, "lon", None)
                year = getattr(parsed, "year", None)
                month = getattr(parsed, "month", None)
                day = getattr(parsed, "day", None)
                hour = getattr(parsed, "hour", None)
                minute = getattr(parsed, "min", None)
                second = getattr(parsed, "second", None)
                nano = getattr(parsed, "nano", None)

                if None in (lat, lon, year, month, day, hour, minute, second):
                    continue

                # lat/lon conversion
                try:
                    lat_deg = float(lat)
                except Exception:
                    try:
                        lat_deg = int(lat) / 1e7
                    except Exception:
                        continue
                try:
                    lon_deg = float(lon)
                except Exception:
                    try:
                        lon_deg = int(lon) / 1e7
                    except Exception:
                        continue

                # build datetime; convert nano -> microseconds if present
                try:
                    year_i = int(year)
                    month_i = int(month)
                    day_i = int(day)
                    hour_i = int(hour)
                    min_i = int(minute)
                    sec_i = int(second)
                    usec = 0
                    if nano is not None:
                        try:
                            # nano may be int nanoseconds
                            usec = int(nano) // 1000
                        except Exception:
                            usec = 0
                    dt = datetime(year_i, month_i, day_i, hour_i, min_i, sec_i, usec)
                except Exception:
                    # skip if date/time fields invalid
                    continue

                records.append((dt, lat_deg, lon_deg))
    return records


def collect_info_from_dir(src_dir: Path) -> Dict[str, List[Tuple[datetime, float, float]]]:
    """Scan directory for .ubz files and collect (datetime,lat,lon) tuples per file.

    Returns a dict mapping filename -> list of (datetime, lat, lon) tuples.
    """
    results: Dict[str, List[Tuple[datetime, float, float]]] = {}
    if not src_dir.exists() or not src_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    for path in sorted(src_dir.glob("*.ubz")):
        try:
            records = collect_info_from_file(path)
            results[str(path.name)] = records
        except Exception as e:
            results[str(path.name)] = []
            print(f"Warning: failed to process {path}: {e}")

    return results


def main() -> None:
    p = argparse.ArgumentParser(description="Collect latitudes and longitudes from .ubz UBX files in a directory")
    p.add_argument("src", nargs="?", default=None, help="Source directory containing .ubz files. If omitted, defaults to D:\\Workspace\\ubxlogs\\CH")
    args = p.parse_args()

    default_dir = Path(r"C:\Users\amina\workspace\ubxlogs\SG")
    src_dir = Path(args.src) if args.src else default_dir

    try:
        results = collect_info_from_dir(src_dir)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Print summary: filename and number of records
    for fname, records in results.items():
        # EXAMPLE of printing results
        #print(f"{fname}: {len(records)} records; first: {records[:5]}")
        print("datetime: " + str(records[0][0]))
        print("latitude: " + str(records[0][1]))
        print("longitude: " + str(records[0][2]))
        # WRITE YOUR CODE HERE
        # You can create function if needed
        lat = records[0][1]
        lon = records[0][2]

        location = "unknown"
        if lat > 59.83333 and lat < 68.90596 and lon > 21.37596 and lon < 30.93276:
            print ("Finland")
        elif lat > 45.83203 and lat < 47.69732 and lon > 6.07544 and lon < 9.83723:
            print ("Switzerland")
        elif lat > 18.24306 and lat < 52.33333 and lon > 75.98951 and lon < 134.28917:
            print ("China")
        elif lat > 24.34478 and lat < 45.40944 and lon > 124.15717 and lon < 145.575:
            print ("Japan")
        elif lat > 1.28967 and lat < 1.32808 and lon > 103.804641 and lon < 103.84:
            print ("Singapore")
        elif lat > 19.50139 and lat < 64.85694 and lon > -161.75583 and lon < -68.01197:
            print ("United States")

    


        start_time = datetime(2025, 9, 12, 0, 53, 40, 299)
        duration = 0.0 # in minutes
        print(fname + " location: " + location + " start time: " + str(start_time) + " duration: " + str(duration) + " minutes")
        pass
        # END OF YOUR CODE



if __name__ == "__main__":
    main()

