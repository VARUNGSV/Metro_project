from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

LINE_NAME_ALIASES = {
    "Purple": "Purple",
    "Purple Line": "Purple",
    "Green": "Green",
    "Green Line": "Green",
    "Yellow": "Yellow",
    "Yellow Line": "Yellow",
    "Interchange": "Interchange",
}

STATION_NAME_ALIASES = {
    "Mahatma Gandhi Road": "MG Road",
    "Sir M. Visvesvaraya": "Sir M Visvesvaraya",
    "Sir M. Vishveshwaraiah": "Sir M Visvesvaraya",
    "City Railway Station": "KSR City Railway Station",
    "KSR Metro Station (Brcs)": "KSR City Railway Station",
    "Krishna Rajendra Market": "KR Market",
    "Rashtreeya Vidyalaya Road": "RV Road",
    "Sampige Road": "Mantri Square",
    "Hopefarm": "Hopefarm Channasandra",
    "Seetharampalya": "Seetharamapalya",
    "Whitefield": "Whitefield (Kadugodi)",
    "Yeshvanthpur": "Yeshwanthpur",
}


def _normalize_line_name(value):
    text = str(value).strip()
    return LINE_NAME_ALIASES.get(text, text.replace(" Line", ""))


def _canonical_station_name(value):
    text = str(value).strip()
    return STATION_NAME_ALIASES.get(text, text)


def _haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    return 2 * radius_km * asin(sqrt(a))


def _load_station_records_from_csv():
    csv_path = DATA_DIR / "bengaluru_metro_stations.csv"
    if not csv_path.exists():
        return None

    stations_df = pd.read_csv(csv_path)
    stations_df = stations_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
    stations_df["Station_ID"] = pd.to_numeric(stations_df["Station_ID"], errors="coerce")
    stations_df["lat"] = pd.to_numeric(stations_df["lat"], errors="coerce")
    stations_df["lon"] = pd.to_numeric(stations_df["lon"], errors="coerce")
    stations_df = stations_df.dropna(subset=["Station_ID", "lat", "lon"]).copy()
    stations_df["Station_ID"] = stations_df["Station_ID"].astype(int)
    stations_df["Station_Name"] = stations_df["Station_Name"].map(_canonical_station_name)
    stations_df["Station"] = stations_df["Station_Name"]
    stations_df["Line"] = stations_df["Line"].map(_normalize_line_name)
    return stations_df[["Station", "Station_Name", "Station_ID", "Line", "lat", "lon"]]


def _build_fallback_station_data():
    data = {
        "Station": [
            "Challaghatta", "Kengeri", "Kengeri Bus Terminal", "Pattanagere",
            "Jnanabharathi", "Rajarajeshwari Nagar", "Nayandahalli", "Mysuru Road",
            "Deepanjali Nagar", "Attiguppe", "Vijayanagar", "Hosahalli",
            "Magadi Road", "City Railway Station", "Majestic", "Sir M. Visvesvaraya",
            "Vidhana Soudha", "Cubbon Park", "Mahatma Gandhi Road", "Trinity",
            "Halasuru", "Indiranagar", "Swami Vivekananda Road", "Baiyappanahalli",
            "Benniganahalli", "Krishnarajapura", "Mahadevapura", "Garudacharpalya",
            "Hoodi", "Seetharampalya", "Kundalahalli", "Nallurhalli",
            "Sadaramangala", "Pattandur Agrahara", "Kadugodi Tree Park", "Hopefarm",
            "Whitefield (Kadugodi)",
            "Madavara", "Chikkabidarakallu", "Manjunathanagar", "Nagasandra",
            "Dasarahalli", "Jalahalli", "Peenya Industry", "Peenya",
            "Goraguntepalya", "Yeshwanthpur", "Sandal Soap Factory", "Mahalakshmi",
            "Rajajinagar", "Kuvempu Road", "Srirampura", "Sampige Road",
            "Majestic", "Chickpete", "Krishna Rajendra Market", "National College",
            "Lalbagh", "South End Circle", "Jayanagar", "Rashtreeya Vidyalaya Road",
            "Banashankari", "Jaya Prakash Nagar", "Yelachenahalli", "Konanakunte Cross",
            "Doddakallasandra", "Vajarahalli", "Thalaghattapura", "Silk Institute",
            "Ragigudda", "Jayadeva Hospital", "BTM Layout", "Central Silk Board",
            "Bommanahalli", "Hongasandra", "Kudlu Gate", "Singasandra", "Hosa Road",
            "Beratena Agrahara", "Electronic City", "Infosys Foundation Konappana Agrahara",
            "Huskur Road", "Bommasandra",
        ],
        "Line": ["Purple"] * 37 + ["Green"] * 32 + ["Yellow"] * 14,
        "lat": [
            12.8735, 12.8826, 12.8917, 12.9008, 12.9099, 12.9190, 12.9281, 12.9372,
            12.9463, 12.9548, 12.9633, 12.9697, 12.9758, 12.9775, 12.9759, 12.9759,
            12.9796, 12.9771, 12.9756, 12.9722, 12.9758, 12.9784, 12.9856, 12.9908,
            13.0000, 13.0100, 13.0200, 13.0250, 13.0300, 13.0350, 13.0400, 13.0450,
            13.0500, 13.0550, 13.0600, 13.0650, 13.0700,
            13.0800, 13.0750, 13.0700, 13.0660, 13.0523, 13.0386, 13.0249, 13.0112,
            12.9975, 12.9838, 12.9701, 12.9564, 12.9427, 12.9290, 12.9153, 12.9016,
            12.9759, 12.9650, 12.9541, 12.9432, 12.9323, 12.9214, 12.9105, 12.8996,
            12.8887, 12.8778, 12.8669, 12.8560, 12.8451, 12.8342, 12.8233, 12.8124,
            12.9100, 12.9150, 12.9200, 12.9250, 12.9300, 12.9350, 12.9400, 12.9450,
            12.9500, 12.9550, 12.9600, 12.9650, 12.9700, 12.9750,
        ],
        "lon": [
            77.4585, 77.4669, 77.4753, 77.4837, 77.4921, 77.5005, 77.5089, 77.5173,
            77.5257, 77.5341, 77.5425, 77.5509, 77.5593, 77.5677, 77.5761, 77.5845,
            77.5929, 77.6013, 77.6097, 77.6181, 77.6265, 77.6349, 77.6433, 77.6517,
            77.6600, 77.6700, 77.6800, 77.6850, 77.6900, 77.6950, 77.7000, 77.7050,
            77.7100, 77.7150, 77.7200, 77.7250, 77.7300,
            77.5200, 77.5150, 77.5100, 77.5050, 77.4966, 77.4882, 77.4798, 77.4714,
            77.4630, 77.4546, 77.4462, 77.4378, 77.4294, 77.4210, 77.4126, 77.4042,
            77.5761, 77.5677, 77.5593, 77.5509, 77.5425, 77.5341, 77.5257, 77.5173,
            77.5089, 77.5005, 77.4921, 77.4837, 77.4753, 77.4669, 77.4585, 77.4501,
            77.5250, 77.5300, 77.5350, 77.5400, 77.5450, 77.5500, 77.5550, 77.5600,
            77.5650, 77.5700, 77.5750, 77.5800, 77.5850, 77.5900,
        ],
    }
    stations_df = pd.DataFrame(data)
    stations_df["Station_ID"] = stations_df.index + 1
    stations_df["Station"] = stations_df["Station"].map(_canonical_station_name)
    stations_df["Station_Name"] = stations_df["Station"]
    return stations_df[["Station", "Station_Name", "Station_ID", "Line", "lat", "lon"]]


def load_hourly_breakdown():
    try:
        hourly_df = pd.read_csv(DATA_DIR / "station_hourly_breakdown.csv")
    except FileNotFoundError:
        return None

    hourly_df["Year"] = pd.to_numeric(hourly_df["Year"], errors="coerce")
    hourly_df["Hour"] = pd.to_numeric(hourly_df["Hour"], errors="coerce")
    hourly_df["Passengers"] = pd.to_numeric(hourly_df["Passengers"], errors="coerce")
    hourly_df = hourly_df.dropna(subset=["Year", "Hour", "Passengers", "Station"]).copy()
    hourly_df["Year"] = hourly_df["Year"].astype(int)
    hourly_df["Hour"] = hourly_df["Hour"].astype(int)
    hourly_df["Passengers"] = hourly_df["Passengers"].astype(float)
    hourly_df["Station"] = hourly_df["Station"].astype(str).str.strip().map(_canonical_station_name)
    if "Line" in hourly_df.columns:
        hourly_df["Line"] = hourly_df["Line"].astype(str).str.strip().map(_normalize_line_name)
    if "Is_Weekend" in hourly_df.columns:
        hourly_df["Is_Weekend"] = (
            hourly_df["Is_Weekend"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({"true": True, "false": False})
            .fillna(False)
        )
    return hourly_df


def _attach_station_traffic(stations_df):
    enriched = stations_df.copy()
    hourly_df = load_hourly_breakdown()

    station_traffic = pd.Series(dtype=float)
    if hourly_df is not None and not hourly_df.empty:
        latest_year = hourly_df["Year"].max()
        station_traffic = (
            hourly_df[hourly_df["Year"] == latest_year]
            .groupby("Station")["Passengers"]
            .sum()
        )

    enriched["Traffic"] = enriched["Station"].map(station_traffic)
    overall_median = station_traffic.median() if not station_traffic.empty else 20000.0
    if pd.isna(overall_median) or overall_median <= 0:
        overall_median = 20000.0

    for _, line_rows in enriched.groupby("Line"):
        line_rows = line_rows.sort_values("Station_ID")
        line_traffic = line_rows["Traffic"].dropna()
        line_median = line_traffic.median() if not line_traffic.empty else overall_median
        if pd.isna(line_median) or line_median <= 0:
            line_median = overall_median

        denom = max(len(line_rows) - 1, 1)
        for position, row_index in enumerate(line_rows.index):
            normalized_position = position / denom
            centrality_bonus = 1.0 + (1.0 - abs((normalized_position * 2) - 1.0)) * 0.35
            if pd.isna(enriched.at[row_index, "Traffic"]) or enriched.at[row_index, "Traffic"] <= 0:
                enriched.at[row_index, "Traffic"] = line_median * centrality_bonus

    interchange_mask = enriched.duplicated("Station", keep=False)
    enriched.loc[interchange_mask, "Traffic"] = enriched.loc[interchange_mask, "Traffic"] * 1.4
    enriched["Traffic"] = enriched["Traffic"].round().astype(int)
    return enriched


def load_station_data():
    stations_df = _load_station_records_from_csv()
    if stations_df is None:
        stations_df = _build_fallback_station_data()
    stations_df["Line"] = stations_df["Line"].map(_normalize_line_name)
    return _attach_station_traffic(stations_df)


def load_connection_data():
    stations_df = load_station_data()
    connections = []

    def add_connection(row1, row2, line_name, distance_km=None):
        distance = distance_km
        if distance is None:
            distance = _haversine_km(row1["lat"], row1["lon"], row2["lat"], row2["lon"])
        distance = round(max(float(distance), 0.05), 2)

        connections.append({
            "Station1": row1["Station"],
            "Station2": row2["Station"],
            "Distance_km": distance,
            "Station1_ID": int(row1["Station_ID"]),
            "Station2_ID": int(row2["Station_ID"]),
            "Line": line_name,
        })
        connections.append({
            "Station1": row2["Station"],
            "Station2": row1["Station"],
            "Distance_km": distance,
            "Station1_ID": int(row2["Station_ID"]),
            "Station2_ID": int(row1["Station_ID"]),
            "Line": line_name,
        })

    for line_name in stations_df["Line"].drop_duplicates():
        line_stations = stations_df[stations_df["Line"] == line_name].sort_values("Station_ID").reset_index(drop=True)
        for idx in range(len(line_stations) - 1):
            add_connection(line_stations.iloc[idx], line_stations.iloc[idx + 1], line_name)

    interchange_pairs = [
        ("RV Road", "RV Road Junction", 0.05),
    ]
    for station_a, station_b, distance in interchange_pairs:
        station_a_rows = stations_df[stations_df["Station"] == station_a]
        station_b_rows = stations_df[stations_df["Station"] == station_b]
        if not station_a_rows.empty and not station_b_rows.empty:
            add_connection(station_a_rows.iloc[0], station_b_rows.iloc[0], "Interchange", distance)

    return pd.DataFrame(connections)


def load_passenger_data():
    try:
        passenger_df = pd.read_csv(DATA_DIR / "passenger_data.csv")
    except FileNotFoundError:
        np.random.seed(42)
        years = range(2019, 2027)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        data = []
        base_purple = 600000
        base_green = 400000
        growth_rate = 1.08
        for year_idx, year in enumerate(years):
            for month in months:
                seasonal = 1.0
                if month in ["May", "Jun"]:
                    seasonal = 0.85
                elif month == "Dec":
                    seasonal = 1.2
                elif month in ["Jul", "Aug"]:
                    seasonal = 0.9

                purple_passengers = int(base_purple * (growth_rate ** year_idx) * seasonal * np.random.uniform(0.95, 1.05))
                green_passengers = int(base_green * (growth_rate ** year_idx) * seasonal * np.random.uniform(0.95, 1.05))
                total_passengers = purple_passengers + green_passengers
                data.append({
                    "Year": year,
                    "Month": month,
                    "Passengers": total_passengers,
                    "Purple_Line_Passengers": purple_passengers,
                    "Green_Line_Passengers": green_passengers,
                    "Yellow_Line_Passengers": 0,
                })
        passenger_df = pd.DataFrame(data)

    passenger_df["Year"] = pd.to_numeric(passenger_df["Year"], errors="coerce")
    passenger_df = passenger_df.dropna(subset=["Year"]).copy()
    passenger_df["Year"] = passenger_df["Year"].astype(int)
    if "Yellow_Line_Passengers" not in passenger_df.columns:
        purple = pd.to_numeric(passenger_df.get("Purple_Line_Passengers", 0), errors="coerce").fillna(0)
        green = pd.to_numeric(passenger_df.get("Green_Line_Passengers", 0), errors="coerce").fillna(0)
        total = pd.to_numeric(passenger_df.get("Passengers", 0), errors="coerce").fillna(0)
        passenger_df["Yellow_Line_Passengers"] = (total - purple - green).clip(lower=0)
    return passenger_df


def get_all_stations(stations_df=None):
    if stations_df is None:
        stations_df = load_station_data()
    station_col = "Station" if "Station" in stations_df.columns else "Station_Name"
    return sorted(stations_df[station_col].dropna().unique().tolist())


def get_hourly_traffic_for_station(station, year, hourly_df):
    if hourly_df is None or hourly_df.empty:
        return None

    station_name = _canonical_station_name(station)
    station_data = hourly_df[
        (hourly_df["Station"] == station_name) &
        (hourly_df["Year"] == year)
    ]
    if station_data.empty:
        return None

    return station_data.groupby("Hour")["Passengers"].sum().reset_index()
