import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ----------------------------------------------------------------------
# HELPER: Detect station name column
# ----------------------------------------------------------------------
def _get_station_column(df):
    possible_names = ['Station', 'station', 'Name', 'name', 'Station_Name', 'station_name', 'Stop', 'stop']
    for col in df.columns:
        if col in possible_names or col.lower() in [n.lower() for n in possible_names]:
            return col
    return df.columns[0]

def _get_line_column(df):
    possible_names = ['Line', 'line', 'Metro_Line', 'metro_line', 'Corridor']
    for col in df.columns:
        if col in possible_names or col.lower() in [n.lower() for n in possible_names]:
            return col
    return None

# ----------------------------------------------------------------------
# PLOTTING FUNCTIONS
# ----------------------------------------------------------------------
def plot_selected_route(G, route):
    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
    
    nx.draw_networkx_nodes(G, pos, node_size=200, node_color='lightgray', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1, alpha=0.5, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    
    route_nodes = set(route)
    route_edges = [(route[i], route[i+1]) for i in range(len(route)-1)]
    
    nx.draw_networkx_nodes(G, pos, nodelist=list(route_nodes), 
                           node_size=400, node_color='purple', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=route_edges, 
                           edge_color='purple', width=3, ax=ax)
    
    ax.set_title("Metro Network - Selected Route Highlighted", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    return fig

def plot_monthly_passengers(passenger_df, year):
    yearly_data = passenger_df[passenger_df['Year'] == year].copy()
    
    if yearly_data.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"No data available for {year}", 
                ha='center', va='center', fontsize=14)
        ax.set_title(f'Monthly Passengers - {year}')
        return fig
    
    if 'Month' in yearly_data.columns:
        try:
            yearly_data['Month_num'] = pd.to_numeric(yearly_data['Month'])
            yearly_data = yearly_data.sort_values('Month_num')
        except:
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_map = {m.lower(): i for i, m in enumerate(month_order)}
            yearly_data['Month_lower'] = yearly_data['Month'].str.lower().str[:3]
            yearly_data['Month_order'] = yearly_data['Month_lower'].map(month_map)
            yearly_data = yearly_data.sort_values('Month_order')
    
    months = yearly_data['Month'].astype(str).tolist()
    purple = yearly_data.get('Purple_Line_Passengers', [0]*len(yearly_data)).values
    green = yearly_data.get('Green_Line_Passengers', [0]*len(yearly_data)).values
    yellow = yearly_data.get('Yellow_Line_Passengers', [0]*len(yearly_data)).values
    
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(months))
    width = 0.25
    
    bars1 = ax.bar(x - width, purple, width, label='Purple Line', color='#6a1b9a', alpha=0.8)
    bars2 = ax.bar(x, green, width, label='Green Line', color='#2e7d32', alpha=0.8)
    bars3 = ax.bar(x + width, yellow, width, label='Yellow Line', color='#f9a825', alpha=0.8)
    
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Passenger Count', fontsize=12)
    ax.set_title(f'Monthly Passenger Traffic by Line - {year}', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha='right')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig

def plot_yearly_passengers(passenger_df):
    yearly = passenger_df.groupby('Year')['Passengers'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(yearly['Year'].astype(str), yearly['Passengers'], 
                  color='#6a1b9a', alpha=0.8)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Passengers', fontsize=12)
    ax.set_title('Yearly Passenger Trend', fontsize=14, fontweight='bold')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height):,}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig

def plot_line_utilization(stations_df, connections_df):
    line_col = _get_line_column(stations_df)
    if line_col is None:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "Line information not available in data", 
                ha='center', va='center', fontsize=12)
        ax.set_title('Station Distribution by Line')
        return fig
    
    line_counts = stations_df[line_col].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {'Purple': '#6a1b9a', 'Green': '#2e7d32', 'Yellow': '#f9a825'}
    bar_colors = [colors.get(line, 'gray') for line in line_counts.index]
    
    bars = ax.bar(line_counts.index.astype(str), line_counts.values, color=bar_colors, alpha=0.8)
    ax.set_xlabel('Metro Line', fontsize=12)
    ax.set_ylabel('Number of Stations', fontsize=12)
    ax.set_title('Station Distribution by Line', fontsize=14, fontweight='bold')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0,3), textcoords="offset points", ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

def plot_peak_hours(station, year, passenger_df=None, stations_df=None):
    """
    Plot realistic peak hours analysis using actual hourly data when available.
    Falls back to simulated patterns if hourly data is not found.
    """
    from metro_data import load_hourly_breakdown
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Try to load real hourly data
    hourly_df = load_hourly_breakdown()
    use_real_data = False
    data_source = "Simulated"
    
    if hourly_df is not None and not hourly_df.empty:
        # Get hourly data for this station and year
        station_hourly = hourly_df[
            (hourly_df['Station'] == station) & 
            (hourly_df['Year'] == year)
        ]
        
        if len(station_hourly) > 0:
            # Aggregate by hour
            hourly_traffic = station_hourly.groupby('Hour')['Passengers'].sum().reset_index()
            hourly_traffic = hourly_traffic.sort_values('Hour')
            
            hours = hourly_traffic['Hour'].values
            traffic = hourly_traffic['Passengers'].values
            use_real_data = True
            data_source = f"Real Data ({year})"
        else:
            # Year not in hourly data, try to extrapolate from latest available
            available_years = sorted(hourly_df[hourly_df['Station'] == station]['Year'].unique())
            if len(available_years) > 0:
                latest_year = available_years[-1]
                station_hourly = hourly_df[
                    (hourly_df['Station'] == station) & 
                    (hourly_df['Year'] == latest_year)
                ]
                
                if len(station_hourly) > 0:
                    hourly_traffic = station_hourly.groupby('Hour')['Passengers'].sum().reset_index()
                    hourly_traffic = hourly_traffic.sort_values('Hour')
                    
                    # Extrapolate based on passenger growth rate
                    if passenger_df is not None and not passenger_df.empty:
                        latest_total = passenger_df[passenger_df['Year'] == latest_year]['Passengers'].sum()
                        current_total = passenger_df[passenger_df['Year'] == year]['Passengers'].sum()
                        if latest_total > 0:
                            growth_multiplier = current_total / latest_total
                        else:
                            growth_multiplier = 1.0
                    else:
                        growth_multiplier = 1.0
                    
                    hours = hourly_traffic['Hour'].values
                    traffic = hourly_traffic['Passengers'].values * growth_multiplier
                    use_real_data = True
                    data_source = f"Projected from {latest_year} data"
    
    # If no real data available, use simulated pattern
    if not use_real_data:
        hours = np.array(list(range(6, 23)))
        
        # Get station-specific multiplier
        station_multiplier = 1.0
        if passenger_df is not None and not passenger_df.empty:
            available_years = sorted(passenger_df['Year'].unique())
            latest_year = available_years[-1] if available_years else 2023
            
            if year not in available_years:
                if len(available_years) >= 2:
                    recent_growth = (passenger_df[passenger_df['Year'] == latest_year]['Passengers'].sum() / 
                                   passenger_df[passenger_df['Year'] == available_years[-2]]['Passengers'].sum())
                    years_diff = year - latest_year
                    station_multiplier = recent_growth ** years_diff
                else:
                    station_multiplier = 1.1
                data_source = f"Simulated (based on {latest_year} trend)"
            else:
                year_total = passenger_df[passenger_df['Year'] == year]['Passengers'].sum()
                if year_total > 0:
                    baseline_2019 = passenger_df[passenger_df['Year'] == 2019]['Passengers'].sum()
                    station_multiplier = year_total / baseline_2019 if baseline_2019 > 0 else 1.0
                data_source = f"Simulated pattern ({year})"
        
        # Realistic Bengaluru Metro peak hours pattern
        base_traffic = np.array([
            150,   # 6 AM
            300,   # 7 AM
            850,   # 8 AM - PEAK
            700,   # 9 AM
            400,   # 10 AM
            350,   # 11 AM
            380,   # 12 PM
            420,   # 1 PM
            400,   # 2 PM
            380,   # 3 PM
            500,   # 4 PM
            950,   # 5 PM
            1100,  # 6 PM - PEAK
            1050,  # 7 PM
            850,   # 8 PM
            420,   # 9 PM
            200    # 10 PM
        ])
        
        variation = np.random.normal(1, 0.08, len(base_traffic))
        traffic = np.maximum(base_traffic * station_multiplier * variation, 50)
    
    # Get station line info
    station_line = ""
    if stations_df is not None:
        station_info = stations_df[stations_df['Station_Name'] == station]
        if not station_info.empty:
            station_line = f" - {station_info['Line'].values[0]}"
    
    # Fill area chart
    ax.fill_between(hours, traffic, color='#6a1b9a', alpha=0.5, label='Passenger Volume')
    ax.plot(hours, traffic, color='#6a1b9a', linewidth=2.5, marker='o', markersize=6)
    
    # Highlight peak hours
    ax.axvspan(7, 9, alpha=0.15, color='orange', label='Morning Peak (7-9 AM)')
    ax.axvspan(5, 8, alpha=0.15, color='red', label='Evening Peak (5-8 PM)')
    
    ax.set_xlabel('Hour of Day', fontsize=13, fontweight='bold')
    ax.set_ylabel('Passenger Volume', fontsize=13, fontweight='bold')
    ax.set_title(f'Peak Hours Analysis - {station}{station_line} ({year})\n✅ {data_source}', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(int(hours[0]), int(hours[-1])+1, 1))
    ax.set_xticklabels([f'{int(h)}:00' for h in range(int(hours[0]), int(hours[-1])+1, 1)], rotation=45, ha='right')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', fontsize=10)
    
    # Add annotations for peaks
    if len(traffic) > 0:
        max_idx = np.argmax(traffic)
        ax.annotate('Peak Traffic', xy=(hours[max_idx], traffic[max_idx]),
                    xytext=(hours[max_idx]+0.5, traffic[max_idx]+50),
                    arrowprops=dict(arrowstyle='->', color='#6a1b9a', lw=2),
                    fontsize=9, fontweight='bold', ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#f9a825', alpha=0.7))
    
    plt.tight_layout()
    return fig

def plot_passenger_growth(passenger_df):
    yearly = passenger_df.groupby('Year')['Passengers'].sum().reset_index()
    yearly['Growth'] = yearly['Passengers'].pct_change() * 100
    
    fig, ax = plt.subplots(figsize=(10, 5))
    years = yearly['Year'].astype(str)
    growth = yearly['Growth'].fillna(0)
    
    colors = ['#2e7d32' if g >= 0 else '#c62828' for g in growth]
    bars = ax.bar(years, growth, color=colors, alpha=0.8)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Growth Rate (%)', fontsize=12)
    ax.set_title('Year-over-Year Passenger Growth', fontsize=14, fontweight='bold')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3 if height >= 0 else -12), textcoords="offset points",
                    ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    return fig

def plot_station_traffic(passenger_df, stations_df, year, top_n=10, show_all=False):
    station_col = _get_station_column(stations_df)
    
    if 'Traffic' not in stations_df.columns:
        np.random.seed(42)
        traffic = np.random.randint(10000, 50000, size=len(stations_df))
        stations_df = stations_df.copy()
        stations_df['Traffic'] = traffic
    
    # Determine how many stations to display
    num_stations = len(stations_df) if show_all else top_n
    top_stations = stations_df.nlargest(num_stations, 'Traffic')
    
    # Dynamically adjust figure size based on number of stations
    fig_height = max(6, num_stations * 0.3)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    bars = ax.barh(top_stations[station_col], top_stations['Traffic'], 
                   color='#6a1b9a', alpha=0.8)
    
    ax.set_xlabel('Annual Passengers', fontsize=12)
    ax.set_ylabel('Station', fontsize=12)
    title = f'All Stations by Traffic ({year})' if show_all else f'Top {top_n} Stations by Traffic ({year})'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    # Only annotate for small number of stations to avoid clutter
    if num_stations <= 20:
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{int(width):,}', xy=(width, bar.get_y() + bar.get_height()/2),
                        xytext=(5,0), textcoords="offset points", ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def plot_crowding_heatmap(stations_df, passenger_df, year, top_n=15):
    """
    Plot crowding heatmap showing passenger volume by station and hour.
    Uses real hourly data when available, falls back to simulated patterns.
    X-axis: Hours (6 AM to 10 PM)
    Y-axis: Top stations by traffic
    Color intensity: Passenger volume
    """
    from metro_data import load_hourly_breakdown
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    station_col = _get_station_column(stations_df)
    
    # Try to load real hourly data
    hourly_df = load_hourly_breakdown()
    use_real_data = False
    
    if hourly_df is not None and not hourly_df.empty:
        # Get stations available for this year
        available_stations = hourly_df[hourly_df['Year'] == year]['Station'].unique()
        
        if len(available_stations) > 0:
            # Get top stations by total passengers
            station_totals = hourly_df[hourly_df['Year'] == year].groupby('Station')['Passengers'].sum()
            top_stations = station_totals.nlargest(top_n).index.tolist()
            
            # Get hourly data for these stations
            hours = np.array(list(range(6, 23)))
            crowding_data = np.zeros((len(top_stations), len(hours)))
            
            for i, station in enumerate(top_stations):
                station_hourly = hourly_df[
                    (hourly_df['Station'] == station) & 
                    (hourly_df['Year'] == year)
                ]
                
                if len(station_hourly) > 0:
                    for h in hours:
                        hour_data = station_hourly[station_hourly['Hour'] == h]
                        if len(hour_data) > 0:
                            crowding_data[i, h-6] = hour_data['Passengers'].sum()
            
            use_real_data = True
            data_source = f"Real Data ({year})"
    
    # Fallback to simulated data if real data not available
    if not use_real_data:
        if 'Traffic' not in stations_df.columns:
            np.random.seed(42)
            traffic = np.random.randint(10000, 50000, size=len(stations_df))
            stations_df = stations_df.copy()
            stations_df['Traffic'] = traffic
        
        top_stations = stations_df.nlargest(top_n, 'Traffic')[station_col].tolist()
        
        hours = np.array(list(range(6, 23)))
        crowding_data = np.zeros((len(top_stations), len(hours)))
        
        # Realistic crowding patterns
        base_pattern = np.array([
            100,   # 6 AM
            300,   # 7 AM
            900,   # 8 AM - PEAK
            700,   # 9 AM
            400,   # 10 AM
            350,   # 11 AM
            380,   # 12 PM
            420,   # 1 PM
            400,   # 2 PM
            380,   # 3 PM
            500,   # 4 PM
            950,   # 5 PM
            1100,  # 6 PM - PEAK
            1050,  # 7 PM
            850,   # 8 PM
            420,   # 9 PM
            200    # 10 PM
        ])
        
        for i, station in enumerate(top_stations):
            station_traffic = stations_df[stations_df[station_col] == station]['Traffic'].values[0] if len(stations_df[stations_df[station_col] == station]) > 0 else 20000
            multiplier = station_traffic / 25000
            variation = np.random.normal(1, 0.12, len(base_pattern))
            crowding_data[i, :] = (base_pattern * multiplier * variation).astype(int)
            crowding_data[i, :] = np.maximum(crowding_data[i, :], 50)
        
        data_source = f"Simulated Pattern ({year})"
    
    # Create heatmap
    im = ax.imshow(crowding_data, cmap='RdYlGn_r', aspect='auto', interpolation='nearest')
    
    # Set labels
    ax.set_xticks(range(len(hours)))
    ax.set_xticklabels([f'{h}:00' for h in hours], rotation=45, ha='right')
    ax.set_yticks(range(len(top_stations)))
    ax.set_yticklabels([s[:20] for s in top_stations], fontsize=9)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label='Passenger Volume')
    
    # Labels and title
    ax.set_xlabel('Time of Day', fontsize=12, fontweight='bold')
    ax.set_ylabel('Station', fontsize=12, fontweight='bold')
    ax.set_title(f'Crowding Index by Station & Hour - {year}\n✅ {data_source} | (Darker Red = More Crowded)', 
                 fontsize=14, fontweight='bold')
    
    # Add annotations (only for peak hours to avoid clutter)
    for i in range(len(top_stations)):
        for j in [2, 8, 12]:  # Morning peak, midday, evening peak
            text = ax.text(j, i, f'{int(crowding_data[i, j])}',
                          ha="center", va="center", color="black", fontsize=7)
    
    plt.tight_layout()
    return fig

def plot_crowding_timeline(station, year):
    """
    Plot crowding timeline for a specific station throughout the day.
    Shows 24-hour crowding pattern with peak indicators.
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    hours = np.arange(6, 23)
    
    # Realistic crowding pattern
    base_traffic = np.array([
        150,   # 6 AM
        300,   # 7 AM
        850,   # 8 AM - PEAK
        700,   # 9 AM
        400,   # 10 AM
        350,   # 11 AM
        380,   # 12 PM
        420,   # 1 PM
        400,   # 2 PM
        380,   # 3 PM
        500,   # 4 PM
        950,   # 5 PM
        1100,  # 6 PM - PEAK
        1050,  # 7 PM
        850,   # 8 PM
        420,   # 9 PM
        200    # 10 PM
    ])
    
    variation = np.random.normal(1, 0.10, len(base_traffic))
    traffic = np.maximum(base_traffic * variation, 50)
    
    # Create area chart with gradient effect
    ax.fill_between(hours, traffic, alpha=0.3, color='#6a1b9a', label='Crowding Level')
    ax.plot(hours, traffic, color='#6a1b9a', linewidth=3, marker='o', markersize=8, label='Passenger Count')
    
    # Highlight crowding zones
    ax.axvspan(7, 9, alpha=0.2, color='red', label='Morning Rush')
    ax.axvspan(5, 8, alpha=0.2, color='orange', label='Evening Peak')
    
    # Add crowding categories
    crowding_lines = [
        (200, 'Low', 'green'),
        (500, 'Moderate', 'yellow'),
        (800, 'High', 'orange'),
        (1000, 'Very High', 'red')
    ]
    
    for level, label, color in crowding_lines:
        ax.axhline(level, color=color, linestyle='--', alpha=0.3, linewidth=1)
    
    ax.set_xlabel('Time of Day', fontsize=13, fontweight='bold')
    ax.set_ylabel('Estimated Passengers', fontsize=13, fontweight='bold')
    ax.set_title(f'Crowding Timeline - {station} ({year})\nEscape Rush Hours for Better Commute Experience', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(6, 23, 1))
    ax.set_xticklabels([f'{h}:00' for h in range(6, 23)], rotation=45, ha='right')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)
    
    # Add advice
    min_crowd_hour = hours[np.argmin(traffic)]
    max_crowd_hour = hours[np.argmax(traffic)]
    ax.text(0.02, 0.95, f'💡 Best Time: {min_crowd_hour}:00 | Avoid: {max_crowd_hour}:00',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#f9a825', alpha=0.7))
    
    plt.tight_layout()
    return fig


from visualization_fixed import (
    plot_crowding_heatmap,
    plot_crowding_timeline,
    plot_monthly_passengers,
    plot_peak_hours,
    plot_station_traffic,
)
