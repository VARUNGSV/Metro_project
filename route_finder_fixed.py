import networkx as nx
import pandas as pd


def get_all_stations(stations_df):
    """Return sorted list of all station names."""
    if "Station" in stations_df.columns:
        station_col = "Station"
    elif "Station_Name" in stations_df.columns:
        station_col = "Station_Name"
    else:
        station_col = stations_df.columns[0]
    return sorted(stations_df[station_col].dropna().unique())


def _edge_key(station1, station2):
    return tuple(sorted((station1, station2)))


def _fare_from_distance(total_distance):
    if total_distance <= 2:
        return 11
    if total_distance <= 4:
        return 21
    if total_distance <= 6:
        return 32
    if total_distance <= 8:
        return 42
    if total_distance <= 10:
        return 53
    if total_distance <= 15:
        return 63
    if total_distance <= 20:
        return 74
    if total_distance <= 25:
        return 84
    if total_distance <= 30:
        return 90
    return 95


def calculate_fare(route, connections_df, stations_df):
    """
    Calculate fare based on total distance using the resolved graph edge distances.
    """
    edge_distances = {}
    for _, row in connections_df.iterrows():
        edge_distances[_edge_key(row["Station1"], row["Station2"])] = float(row["Distance_km"])

    total_distance = 0.0
    for idx in range(len(route) - 1):
        total_distance += edge_distances.get(_edge_key(route[idx], route[idx + 1]), 0.0)

    return total_distance, _fare_from_distance(total_distance)


def create_metro_graph(stations_df, connections_df):
    """
    Create a NetworkX graph from stations and connections.
    """
    graph = nx.Graph()

    for _, row in stations_df.iterrows():
        station = row["Station"]
        if station not in graph:
            graph.add_node(
                station,
                station_ids={row["Station_ID"]},
                lines={row["Line"]},
                latitude=row["lat"],
                longitude=row["lon"],
            )
        else:
            graph.nodes[station].setdefault("station_ids", set()).add(row["Station_ID"])
            graph.nodes[station].setdefault("lines", set()).add(row["Line"])

    for _, row in connections_df.iterrows():
        graph.add_edge(
            row["Station1"],
            row["Station2"],
            distance=float(row["Distance_km"]),
            line=row.get("Line", "Unknown"),
        )

    return graph


def _build_line_segments(graph, path):
    lines_used = []
    current_line = None
    line_start = None

    for idx in range(len(path) - 1):
        edge_line = graph[path[idx]][path[idx + 1]].get("line")

        if edge_line == "Interchange":
            if current_line is not None:
                lines_used.append((current_line, line_start, path[idx]))
                current_line = None
                line_start = None
            continue

        if current_line is None:
            current_line = edge_line
            line_start = path[idx]
        elif edge_line != current_line:
            lines_used.append((current_line, line_start, path[idx]))
            current_line = edge_line
            line_start = path[idx]

    if current_line is not None:
        lines_used.append((current_line, line_start, path[-1]))

    return lines_used


def find_route(source, destination, stations_df, connections_df):
    """
    Find the shortest distance path between source and destination stations.
    Returns: (path list, lines_used list) or (None, None) if no path.
    """
    graph = create_metro_graph(stations_df, connections_df)

    if source not in graph.nodes or destination not in graph.nodes:
        return None, None

    try:
        path = nx.shortest_path(graph, source, destination, weight="distance")
        return path, _build_line_segments(graph, path)
    except nx.NetworkXNoPath:
        return None, None
    except Exception as exc:
        print(f"Route finding error: {exc}")
        return None, None


def _route_payload(route_name, route, connections_df, stations_df):
    distance, fare = calculate_fare(route, connections_df, stations_df)
    stops = max(len(route) - 1, 0)
    return {
        "path": route,
        "stops": stops,
        "distance": distance,
        "fare": fare,
        "description": f"{stops} stops, {distance:.2f} km",
        "name": route_name,
    }


def _build_station_traffic_lookup(stations_df):
    if "Traffic" not in stations_df.columns:
        return {}

    traffic_df = stations_df[["Station", "Traffic"]].copy()
    traffic_df["Traffic"] = pd.to_numeric(traffic_df["Traffic"], errors="coerce")
    traffic_df = traffic_df.dropna(subset=["Traffic"])
    if traffic_df.empty:
        return {}

    return traffic_df.groupby("Station")["Traffic"].max().to_dict()


def find_alternative_routes(source, destination, stations_df, connections_df, passenger_df=None):
    """
    Find multiple route options using different optimization criteria.
    """
    graph = create_metro_graph(stations_df, connections_df)
    if source not in graph.nodes or destination not in graph.nodes:
        return None

    try:
        shortest_route = nx.shortest_path(graph, source, destination, weight=None)
        fastest_route = nx.shortest_path(graph, source, destination, weight="distance")

        routes = {
            "Shortest": _route_payload("Shortest", shortest_route, connections_df, stations_df),
            "Fastest": _route_payload("Fastest", fastest_route, connections_df, stations_df),
        }

        traffic_lookup = _build_station_traffic_lookup(stations_df)
        if traffic_lookup:
            traffic_values = list(traffic_lookup.values())
            baseline = max(pd.Series(traffic_values).median(), 1.0)
            crowded_graph = graph.copy()

            for station1, station2, edge_data in crowded_graph.edges(data=True):
                base_distance = float(edge_data.get("distance", 1.0))
                if edge_data.get("line") == "Interchange":
                    edge_data["crowding_weight"] = base_distance * 1.75
                    continue

                station_traffic = max(
                    traffic_lookup.get(station1, baseline),
                    traffic_lookup.get(station2, baseline),
                )
                penalty_scale = max((station_traffic / baseline) - 1.0, 0.0)
                edge_data["crowding_weight"] = base_distance * (1.0 + min(penalty_scale, 2.0) * 0.35)

            less_crowded_route = nx.shortest_path(crowded_graph, source, destination, weight="crowding_weight")
            routes["Less Crowded"] = _route_payload("Less Crowded", less_crowded_route, connections_df, stations_df)
            routes["Less Crowded"]["description"] += " (lower crowding penalty)"
        else:
            routes["Less Crowded"] = _route_payload("Less Crowded", shortest_route, connections_df, stations_df)
            routes["Less Crowded"]["description"] += " (fallback)"

        return routes
    except nx.NetworkXNoPath:
        return None
    except Exception as exc:
        print(f"Alternative routes error: {exc}")
        return None
