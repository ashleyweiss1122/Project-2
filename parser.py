import csv
from pathlib import Path

DATA_FOLDER = Path(__file__).resolve().parent / "data" / "gtfs_subway"


def load_stops():
    # read NYC subway station info
    # each stop potential graph vertex

    stops_file = DATA_FOLDER / "stops.txt"
    stops = {}

    with open(stops_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            stop_id = row["stop_id"]
            latitude = row["stop_lat"]
            longitude = row["stop_lon"]

            if not latitude or not longitude:
                continue

            stops[stop_id] = {
                "name": row["stop_name"],
                "latitude": float(latitude),
                "longitude": float(longitude),
                "parent_station": row.get("parent_station", "")
            }
    return stops


def time_to_seconds(time_string):
    # convert gtfs time (HH:MM:SS) into seconds
    # supports time greater than 24 hours

    if not time_string:
        return None

    hours, minutes, seconds = map(int, time_string.split(":"))

    return hours * 3600 + minutes * 60 + seconds


def load_connections():
    # read subway trips and create connections between consective stops

    connections = {}

    trips_file = DATA_FOLDER / "stop_times.txt"

    with open(trips_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        trips = {}

        for row in reader:
            trip_id = row["trip_id"]
            stop_id = row["stop_id"]

            arrival = time_to_seconds(row["arrival_time"])
            departure = time_to_seconds(row["departure_time"])

            if arrival is None or departure is None:
                continue

            trips.setdefault(trip_id, []).append({
                "stop_id": stop_id,
                "arrival": arrival,
                "departure": departure,
                "sequence": int(row["stop_sequence"])
            })

    for trip_id, stops in trips.items():
        stops.sort(key=lambda stop: stop["sequence"])

        for i in range(len(stops) - 1):
            current_stop = stops[i]
            next_stop = stops[i + 1]

            travel_time = next_stop["arrival"] - current_stop["departure"]

            if travel_time < 0:
                continue

            start = current_stop["stop_id"]
            end = next_stop["stop_id"]

            connections.setdefault(start, []).append({
                "destination": end,
                "travel_time": travel_time,
                "trip_id": trip_id
            })

    return connections

def inspect_trip_data():
    trips_file = DATA_FOLDER / "stop_times.txt"

    with open(trips_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        trip_stops = {}

        for row in reader:
            trip_id = row["trip_id"]

            trip_stops.setdefault(trip_id, []).append({
                "stop_id": row["stop_id"],
                "sequence": int(row["stop_sequence"])
            })

    print("\n===== TRIP DATA INSPECTION =====")
    print("Total unique trips:", len(trip_stops))

    for trip_id, stops in list(trip_stops.items())[:5]:
        stops.sort(key=lambda stop: stop["sequence"])

        print("\nTrip:", trip_id)
        print("Number of stops:", len(stops))
        print("First five stops:")

        for stop in stops[:5]:
            print(stop)


def inspect_parent_stations():
    stops = load_stops()

    parent_groups = {}

    for stop_id, info in stops.items():
        parent = info["parent_station"]

        if parent:
            parent_groups.setdefault(parent, []).append(stop_id)

    multi_platform = {
        parent: children
        for parent, children in parent_groups.items()
        if len(children) > 1
    }

    print("\n===== TRANSFER STATION INSPECTION =====")
    print("Total parent stations:", len(parent_groups))
    print("Stations with multiple child stops:", len(multi_platform))

    for parent, children in list(multi_platform.items())[:10]:
        print(parent, "->", children)


def inspect_stop_types():
    stops_file = DATA_FOLDER / "stops.txt"

    counts = {}

    with open(stops_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            location_type = row["location_type"]
            counts[location_type] = counts.get(location_type, 0) + 1

    print("\n===== STOP LOCATION TYPES =====")

    for location_type, count in sorted(counts.items()):
        print("Location type", location_type, ":", count)


def inspect_transfers():
    transfers_file = DATA_FOLDER / "transfers.txt"

    transfer_counts = {}
    total_transfers = 0

    with open(transfers_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        print("\n===== TRANSFER DATA INSPECTION =====")

        for row in reader:
            transfer_type = row["transfer_type"]

            transfer_counts[transfer_type] = (
                    transfer_counts.get(transfer_type, 0) + 1
            )

            total_transfers += 1

            if total_transfers <= 10:
                print(row)

    print("\nTotal transfer records:", total_transfers)
    print("Transfer types:")

    for transfer_type, count in sorted(transfer_counts.items()):
        print("Type", transfer_type, ":", count)


def inspect_transfer_examples():
    transfers_file = DATA_FOLDER / "transfers.txt"

    with open(transfers_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        print("\n===== TRANSFER EXAMPLES =====")

        count = 0

        for row in reader:
            if row["from_stop_id"] != row["to_stop_id"]:
                print("Platform-to-platform transfer:", row)
                count += 1

            if count == 10:
                break

        if count == 0:
            print("No platform-to-platform transfer records found.")


def load_transfers(stops):
    transfers_file = DATA_FOLDER / "transfers.txt"

    parent_groups = {}

    # Group platforms under their parent stations
    for stop_id, info in stops.items():
        parent = info["parent_station"]

        if parent:
            parent_groups.setdefault(parent, []).append(stop_id)

    transfers = []

    with open(transfers_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = row["from_stop_id"]
            destination = row["to_stop_id"]

            # Ignore self-transfer records
            if start == destination:
                continue

            if row["transfer_type"] != "2":
                continue

            if not row["min_transfer_time"]:
                continue

            transfer_time = int(row["min_transfer_time"])

            start_platforms = parent_groups.get(start, [])
            destination_platforms = parent_groups.get(destination, [])

            for start_platform in start_platforms:
                for destination_platform in destination_platforms:
                    transfers.append({
                        "source": start_platform,
                        "destination": destination_platform,
                        "travel_time": transfer_time,
                        "type": "transfer"
                    })

    return transfers


def inspect_raw_transfers():
    transfers_file = DATA_FOLDER / "transfers.txt"

    with open(transfers_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        print("\n===== RAW TRANSFER RECORDS =====")

        count = 0
        for row in reader:
            if row["from_stop_id"] != row["to_stop_id"]:
                print(row)
                count += 1

            if count == 15:
                break


def check_transfer_station_types(stops):
    transfers_file = DATA_FOLDER / "transfers.txt"

    parent_count = 0
    platform_count = 0

    with open(transfers_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = row["from_stop_id"]
            destination = row["to_stop_id"]

            for stop_id in (start, destination):
                if stop_id not in stops:
                    continue

                if stops[stop_id]["parent_station"]:
                    platform_count += 1
                else:
                    parent_count += 1

    print("\n===== TRANSFER STOP TYPE CHECK =====")
    print("Parent station references:", parent_count)
    print("Platform references:", platform_count)


def inspect_transfer_platforms(stops, transfers):
    print("\n===== TRANSFER PLATFORM INSPECTION =====")

    for transfer in transfers[:5]:
        start = transfer["source"]
        destination = transfer["destination"]

        print(f"\nTransfer: {start} -> {destination}")

        print("Starting station:", stops.get(start, {}).get("name", "Not found"))
        print("Destination station:", stops.get(destination, {}).get("name", "Not found"))

        print("Starting station platforms:")
        for stop_id, info in stops.items():
            if info["parent_station"] == start:
                print(" ", stop_id, info["name"])

        print("Destination station platforms:")
        for stop_id, info in stops.items():
            if info["parent_station"] == destination:
                print(" ", stop_id, info["name"])

'''
if __name__ == "__main__":
    stops = load_stops()
    connections = load_connections()
    transfers = load_transfers(stops)

    total_connections = sum(len(edges) for edges in connections.values())

    print("===== NYC SUBWAY DATASET =====")
    print("Total stops:", len(stops))
    print("Stops with train connections:", len(connections))
    print("Total train connections:", total_connections)
    print("Expanded transfer connections:", len(transfers))
'''