import networkx as nx
import pandas as pd


def get_all_stations(stations_df):
    """Return sorted list of all station names."""
    if 'Station' in stations_df.columns:
        station_col = 'Station'
    elif 'Station_Name' in stations_df.columns:
        station_col = 'Station_Name'
    else:
        station_col = stations_df.columns[0]
    return sorted(stations_df[station_col].unique())


def calculate_fare(route, connections_df, stations_df):
    """
    Calculate fare based on total distance (2026 Namma Metro Bengaluru rates).
    Effective from February 9, 2026.
    Uses connections_df with columns: Station1, Station2, Distance_km.
    """
    total_distance = 0.0

    for i in range(len(route) - 1):
        station1 = route[i]
        station2 = route[i + 1]

        row = connections_df[
            ((connections_df['Station1'] == station1) & (connections_df['Station2'] == station2)) |
            ((connections_df['Station1'] == station2) & (connections_df['Station2'] == station1))
        ]

        if not row.empty:
            total_distance += float(row['Distance_km'].values[0])

    # 2026 Namma Metro Bengaluru Fare Structure (Effective Feb 9, 2026)
    if total_distance <= 2:
        fare = 11
    elif total_distance <= 4:
        fare = 21
    elif total_distance <= 6:
        fare = 32
    elif total_distance <= 8:
        fare = 42
    elif total_distance <= 10:
        fare = 53
    elif total_distance <= 15:
        fare = 63
    elif total_distance <= 20:
        fare = 74
    elif total_distance <= 25:
        fare = 84
    elif total_distance <= 30:
        fare = 90
    else:
        fare = 95

    return total_distance, fare


def create_metro_graph(stations_df, connections_df):
    """
    Create a NetworkX graph from stations and connections.
    Stations have: Station, Station_ID, Line, lat, lon.
    Connections have: Station1, Station2, Distance_km.
    """
    G = nx.Graph()

    for _, row in stations_df.iterrows():
        G.add_node(
            row["Station"],
            id=row["Station_ID"],
            line=row["Line"],
            latitude=row["lat"],
            longitude=row["lon"]
        )

    for _, row in connections_df.iterrows():
        G.add_edge(
            row["Station1"],
            row["Station2"],
            distance=row["Distance_km"]
        )

    return G


def find_route(source, destination, stations_df, connections_df):
    """
    Find the shortest path between source and destination stations.
    Returns: (path list, lines_used list) or (None, None) if no path.
    """
    G = create_metro_graph(stations_df, connections_df)

    if source not in G.nodes or destination not in G.nodes:
        return None, None

    try:
        path = nx.shortest_path(G, source, destination, weight="distance")

        lines_used = []
        current_line = None
        line_start = None

        for i in range(len(path) - 1):
            node_line = G.nodes[path[i]].get("line")
            
            if current_line is None:
                current_line = node_line
                line_start = path[i]
            elif node_line != current_line:
                lines_used.append((current_line, line_start, path[i]))
                current_line = node_line
                line_start = path[i]

        if current_line:
            lines_used.append((current_line, line_start, path[-1]))

        return path, lines_used

    except nx.NetworkXNoPath:
        return None, None
    except Exception as e:
        print(f"Route finding error: {e}")
        return None, None


def find_alternative_routes(source, destination, stations_df, connections_df, passenger_df=None):
    """
    Find multiple alternative routes with different optimization criteria.
    
    Returns 3 routes:
    1. Shortest Route: Fewest stations
    2. Less Crowded: Avoids peak hour routes based on passenger data
    3. Fastest: Prioritizes distance (assumes faster travel)
    """
    G = create_metro_graph(stations_df, connections_df)
    
    if source not in G.nodes or destination not in G.nodes:
        return None
    
    routes = {}
    
    try:
        # Route 1: Shortest path (by stations)
        shortest_route = nx.shortest_path(G, source, destination, weight=None)
        distance_1, fare_1 = calculate_fare(shortest_route, connections_df, stations_df)
        routes['Shortest'] = {
            'path': shortest_route,
            'stops': len(shortest_route),
            'distance': distance_1,
            'fare': fare_1,
            'description': f'{len(shortest_route)} stops, {distance_1:.2f} km'
        }
        
        # Route 2: Alternative path by minimizing weights (distance-based)
        try:
            distance_weight_route = nx.shortest_path(G, source, destination, weight='weight')
            distance_2, fare_2 = calculate_fare(distance_weight_route, connections_df, stations_df)
            routes['Fastest'] = {
                'path': distance_weight_route,
                'stops': len(distance_weight_route),
                'distance': distance_2,
                'fare': fare_2,
                'description': f'{len(distance_weight_route)} stops, {distance_2:.2f} km'
            }
        except:
            # Fallback if weighted path fails
            routes['Fastest'] = routes['Shortest'].copy()
            routes['Fastest']['description'] += ' (fallback)'
        
        # Route 3: Less crowded (avoid high-traffic stations if data available)
        if passenger_df is not None and not passenger_df.empty:
            # Create alternative graph penalizing busy stations
            G_alt = G.copy()
            
            # Identify busy stations (those appearing in high-traffic data)
            year_data = passenger_df[passenger_df['Year'] == passenger_df['Year'].max()]
            if not year_data.empty:
                # Add penalty weights to high-passenger stations
                for node in G_alt.nodes():
                    if node in stations_df['Station'].values:
                        station_traffic = stations_df[stations_df['Station'] == node]['Traffic'].values
                        if len(station_traffic) > 0 and station_traffic[0] > 30000:
                            # Penalize busy stations
                            for neighbor in G_alt.neighbors(node):
                                G_alt[node][neighbor]['weight'] = G_alt[node][neighbor].get('weight', 1) * 1.3
            
            try:
                less_crowded_route = nx.shortest_path(G_alt, source, destination, weight='weight')
                distance_3, fare_3 = calculate_fare(less_crowded_route, connections_df, stations_df)
                routes['Less Crowded'] = {
                    'path': less_crowded_route,
                    'stops': len(less_crowded_route),
                    'distance': distance_3,
                    'fare': fare_3,
                    'description': f'{len(less_crowded_route)} stops, {distance_3:.2f} km (less busy)'
                }
            except:
                routes['Less Crowded'] = routes['Shortest'].copy()
                routes['Less Crowded']['description'] += ' (less crowded variant)'
        else:
            routes['Less Crowded'] = routes['Shortest'].copy()
            routes['Less Crowded']['description'] = routes['Shortest']['description'] + ' (alternative)'
        
        return routes
        
    except nx.NetworkXNoPath:
        return None
    except Exception as e:
        print(f"Alternative routes error: {e}")
        return None


from route_finder_fixed import (
    calculate_fare,
    create_metro_graph,
    find_alternative_routes,
    find_route,
    get_all_stations,
)
