import pandas as pd
import numpy as np

def load_station_data():
    """
    Returns a DataFrame with Bengaluru Metro station information.
    Columns: Station, Station_Name, Station_ID, Line, lat, lon
    """
    data = {
        'Station': [
            # ========== PURPLE LINE (East-West) ==========
            'Challaghatta', 'Kengeri', 'Kengeri Bus Terminal', 'Pattanagere',
            'Jnanabharathi', 'Rajarajeshwari Nagar', 'Nayandahalli', 'Mysuru Road',
            'Deepanjali Nagar', 'Attiguppe', 'Vijayanagar', 'Hosahalli',
            'Magadi Road', 'City Railway Station', 'Majestic', 'Sir M. Visvesvaraya',
            'Vidhana Soudha', 'Cubbon Park', 'Mahatma Gandhi Road', 'Trinity',
            'Halasuru', 'Indiranagar', 'Swami Vivekananda Road', 'Baiyappanahalli',
            'Benniganahalli', 'Krishnarajapura', 'Mahadevapura', 'Garudacharpalya',
            'Hoodi', 'Seetharampalya', 'Kundalahalli', 'Nallurhalli',
            'Sadaramangala', 'Pattandur Agrahara', 'Kadugodi Tree Park', 'Hopefarm',
            'Whitefield (Kadugodi)',
            
            # ========== GREEN LINE (North-South) - Madavara to Silk Institute (32 stations) ==========
            'Madavara', 'Chikkabidarakallu', 'Manjunathanagar', 'Nagasandra',
            'Dasarahalli', 'Jalahalli', 'Peenya Industry', 'Peenya',
            'Goraguntepalya', 'Yeshwanthpur', 'Sandal Soap Factory', 'Mahalakshmi',
            'Rajajinagar', 'Kuvempu Road', 'Srirampura', 'Sampige Road',
            'Majestic', 'Chickpete', 'Krishna Rajendra Market', 'National College',
            'Lalbagh', 'South End Circle', 'Jayanagar', 'Rashtreeya Vidyalaya Road',
            'Banashankari', 'Jaya Prakash Nagar', 'Yelachenahalli', 'Konanakunte Cross',
            'Doddakallasandra', 'Vajarahalli', 'Thalaghattapura', 'Silk Institute',
            
            # ========== YELLOW LINE (RV Road - Bommasandra) ==========
            'Ragigudda', 'Jayadeva Hospital', 'BTM Layout', 'Central Silk Board',
            'Bommanahalli', 'Hongasandra', 'Kudlu Gate', 'Singasandra', 'Hosa Road',
            'Beratena Agrahara', 'Electronic City', 'Infosys Foundation Konappana Agrahara',
            'Huskur Road', 'Bommasandra'
        ],
        'Line': [
            'Purple']*37 + ['Green']*32 + ['Yellow']*14,
        'lat': [
            # Purple Line (37 stations)
            12.8735, 12.8826, 12.8917, 12.9008,
            12.9099, 12.9190, 12.9281, 12.9372,
            12.9463, 12.9548, 12.9633, 12.9697,
            12.9758, 12.9775, 12.9759, 12.9759,
            12.9796, 12.9771, 12.9756, 12.9722,
            12.9758, 12.9784, 12.9856, 12.9908,
            13.0000, 13.0100, 13.0200, 13.0250,
            13.0300, 13.0350, 13.0400, 13.0450,
            13.0500, 13.0550, 13.0600, 13.0650,
            13.0700,
            # Green Line (32 stations)
            13.0800, 13.0750, 13.0700, 13.0660,
            13.0523, 13.0386, 13.0249, 13.0112,
            12.9975, 12.9838, 12.9701, 12.9564,
            12.9427, 12.9290, 12.9153, 12.9016,
            12.9759, 12.9650, 12.9541, 12.9432,
            12.9323, 12.9214, 12.9105, 12.8996,
            12.8887, 12.8778, 12.8669, 12.8560,
            12.8451, 12.8342, 12.8233, 12.8124,
            # Yellow Line (14 stations)
            12.9100, 12.9150, 12.9200, 12.9250,
            12.9300, 12.9350, 12.9400, 12.9450,
            12.9500, 12.9550, 12.9600, 12.9650,
            12.9700, 12.9750
        ],
        'lon': [
            # Purple Line (37 stations)
            77.4585, 77.4669, 77.4753, 77.4837,
            77.4921, 77.5005, 77.5089, 77.5173,
            77.5257, 77.5341, 77.5425, 77.5509,
            77.5593, 77.5677, 77.5761, 77.5845,
            77.5929, 77.6013, 77.6097, 77.6181,
            77.6265, 77.6349, 77.6433, 77.6517,
            77.6600, 77.6700, 77.6800, 77.6850,
            77.6900, 77.6950, 77.7000, 77.7050,
            77.7100, 77.7150, 77.7200, 77.7250,
            77.7300,
            # Green Line (32 stations)
            77.5200, 77.5150, 77.5100, 77.5050,
            77.4966, 77.4882, 77.4798, 77.4714,
            77.4630, 77.4546, 77.4462, 77.4378,
            77.4294, 77.4210, 77.4126, 77.4042,
            77.5761, 77.5677, 77.5593, 77.5509,
            77.5425, 77.5341, 77.5257, 77.5173,
            77.5089, 77.5005, 77.4921, 77.4837,
            77.4753, 77.4669, 77.4585, 77.4501,
            # Yellow Line (14 stations)
            77.5250, 77.5300, 77.5350, 77.5400,
            77.5450, 77.5500, 77.5550, 77.5600,
            77.5650, 77.5700, 77.5750, 77.5800,
            77.5850, 77.5900
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Add Station_ID column (unique integer for each station, resetting for duplicate Majestic)
    # Since Majestic appears twice, we'll assign unique IDs based on index, but if you need same ID for duplicate names, we can map.
    # For simplicity, just use index as ID.
    df['Station_ID'] = df.index + 1  # IDs from 1 to 82
    
    # Add duplicate Station_Name column for compatibility
    df['Station_Name'] = df['Station']
    
    return df

def load_connection_data():
    """
    Returns a DataFrame with station connections and distances.
    Includes Station1_ID and Station2_ID if needed by route_finder.
    """
    stations = load_station_data()
    connections = []
    
    def add_connection(s1, s2, dist):
        # Find IDs for the station names (using the first occurrence if duplicates exist)
        id1 = stations[stations['Station'] == s1]['Station_ID'].iloc[0]
        id2 = stations[stations['Station'] == s2]['Station_ID'].iloc[0]
        connections.append({
            'Station1': s1,
            'Station2': s2,
            'Distance_km': dist,
            'Station1_ID': id1,
            'Station2_ID': id2
        })
        connections.append({
            'Station1': s2,
            'Station2': s1,
            'Distance_km': dist,
            'Station1_ID': id2,
            'Station2_ID': id1
        })
    
    # Purple Line connections (sequential)
    purple_stations = stations[stations['Line'] == 'Purple']['Station'].tolist()
    for i in range(len(purple_stations)-1):
        add_connection(purple_stations[i], purple_stations[i+1], 1.2 + np.random.uniform(-0.2, 0.3))
    
    # Green Line connections (sequential)
    green_stations = stations[stations['Line'] == 'Green']['Station'].tolist()
    for i in range(len(green_stations)-1):
        add_connection(green_stations[i], green_stations[i+1], 1.0 + np.random.uniform(-0.1, 0.4))
    
    # Yellow Line connections (sequential)
    yellow_stations = stations[stations['Line'] == 'Yellow']['Station'].tolist()
    for i in range(len(yellow_stations)-1):
        add_connection(yellow_stations[i], yellow_stations[i+1], 1.1 + np.random.uniform(-0.2, 0.3))
    
    # Interchange connections (walking transfers between lines)
    # Majestic is an interchange between Purple and Green lines
    add_connection('Majestic', 'Majestic', 0.05)  # self-transfer for line change at same station
    
    # BTM Layout area - Yellow Line connects with Green Line network
    # Yellow to Green interchange (BTM Layout to nearby stations)
    add_connection('BTM Layout', 'Jayanagar', 2.0)  # Walking distance between lines
    add_connection('Ragigudda', 'Rashtreeya Vidyalaya Road', 1.5)  # Yellow to Green at south end
    
    # Other interchanges
    add_connection('Rashtreeya Vidyalaya Road', 'Ragigudda', 0.5)
    
    return pd.DataFrame(connections)

def load_passenger_data():
    """
    Returns a DataFrame with monthly passenger data for Purple and Green lines.
    Data loaded from CSV file (2019-2026).
    Columns: Year, Month, Passengers, Purple_Line_Passengers, Green_Line_Passengers
    """
    try:
        df = pd.read_csv('data/passenger_data.csv')
        return df
    except FileNotFoundError:
        # Fallback: generate synthetic data if CSV not found
        print("⚠️ Warning: passenger_data.csv not found. Using synthetic data.")
        np.random.seed(42)
        years = range(2019, 2027)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        data = []
        base_purple = 600000
        base_green = 400000
        growth_rate = 1.08
        
        for year_idx, year in enumerate(years):
            for month in months:
                seasonal = 1.0
                if month in ['May', 'Jun']:
                    seasonal = 0.85
                elif month in ['Dec']:
                    seasonal = 1.2
                elif month in ['Jul', 'Aug']:
                    seasonal = 0.9
                
                noise_p = np.random.uniform(0.95, 1.05)
                noise_g = np.random.uniform(0.95, 1.05)
                
                purple_pass = int(base_purple * (growth_rate ** year_idx) * seasonal * noise_p)
                green_pass = int(base_green * (growth_rate ** year_idx) * seasonal * noise_g)
                total = purple_pass + green_pass
                
                data.append({
                    'Year': year,
                    'Month': month,
                    'Passengers': total,
                    'Purple_Line_Passengers': purple_pass,
                    'Green_Line_Passengers': green_pass
                })
        
        return pd.DataFrame(data)

def get_all_stations(stations_df=None):
    """Return sorted list of all station names."""
    if stations_df is None:
        stations_df = load_station_data()
    # Use 'Station' column primarily
    if 'Station' in stations_df.columns:
        station_col = 'Station'
    elif 'Station_Name' in stations_df.columns:
        station_col = 'Station_Name'
    else:
        station_col = stations_df.columns[0]
    return sorted(stations_df[station_col].unique().tolist())


def load_hourly_breakdown():
    """
    Returns a DataFrame with station-wise hourly passenger data.
    Columns: Year, Month, Day, Hour, Station, Line, Passengers, Is_Weekend
    
    This data provides realistic hourly patterns for accurate peak hour analysis
    and crowding predictions.
    """
    try:
        df = pd.read_csv('data/station_hourly_breakdown.csv')
        return df
    except FileNotFoundError:
        print("⚠️ Warning: station_hourly_breakdown.csv not found. Peak hours analysis will use aggregated data.")
        return None


def get_hourly_traffic_for_station(station, year, hourly_df):
    """
    Get hourly traffic pattern for a specific station and year.
    Returns aggregated hourly passenger counts.
    """
    if hourly_df is None:
        return None
    
    station_data = hourly_df[
        (hourly_df['Station'] == station) & 
        (hourly_df['Year'] == year)
    ]
    
    if len(station_data) == 0:
        return None
    
    # Aggregate all days for the year
    hourly_agg = station_data.groupby('Hour')['Passengers'].sum().reset_index()
    
    return hourly_agg


from metro_data_records import (
    get_all_stations,
    get_hourly_traffic_for_station,
    load_connection_data,
    load_hourly_breakdown,
    load_passenger_data,
    load_station_data,
)
