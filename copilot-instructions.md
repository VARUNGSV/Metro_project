# Bengaluru Metro Tracker - AI Agent Instructions

## Project Overview
A Streamlit-based analytics dashboard for Bengaluru Metro system, providing route finding, fare calculations, passenger analytics, visualizations, and Google Maps integration.

**Tech Stack**: Python 3.11+, Streamlit 1.28+, Pandas, NetworkX, Plotly, Folium

## Quick Start

### Running the Application
```bash
streamlit run app.py
```
The app runs on `http://localhost:8501` by default.

### Environment Setup
- **Python Version**: 3.11+ (required)
- **Dependencies**: Install from `pyproject.toml` or `requirements.txt.txt`
  ```bash
  pip install -r requirements.txt.txt
  # OR
  pip install -e .
  ```
- **Secrets**: Google Maps API key stored in `.streamlit/secrets.toml` (see GOOGLE_MAPS_SETUP.md)

## Architecture & Key Components

### Core Modules
- **`app.py`** (main UI)  
  Streamlit interface with custom CSS styling, page sections for route finding, analytics, visualizations. Uses shared imports from other modules.

- **`metro_data.py`** (data loading)  
  - `load_station_data()`: Returns DataFrame with station info (Station, Line, lat, lon)
  - `load_connection_data()`: Returns DataFrame with connections between stations
  - `load_passenger_data()`: Returns passenger statistics

- **`route_finder.py`** (core logic)  
  - `create_metro_graph()`: Creates NetworkX graph from connections
  - `find_route()`: Uses graph traversal to find shortest path between stations
  - `calculate_fare()`: Uses 2026 fare structure (rates updated Feb 9, 2026)
  - `get_all_stations()`: Returns sorted unique station list

- **`visualization.py`** (analytics charts)  
  Functions for Plotly/Matplotlib visualizations: route plots, passenger trends, utilization heatmaps, peak hour analysis.

- **`google_maps_integration.py`**  
  Street View, walking directions, distance matrix, Places autocomplete - requires Google Maps API key.

- **`monthly_stats.py`**  
  Monthly/yearly passenger statistics aggregation.

### Data Files
- `data/bengaluru_metro_stations.csv` - Station metadata (Station, Line, lat, lon, Station_ID)
- `data/bengaluru_metro_connections.csv` - Station pairs with distances (Station1, Station2, Distance_km)
- `data/passenger_data.csv` - Historical passenger counts

### Project Lines
- **Purple Line** (East-West): 37 stations (Challaghatta to Whitefield)
- **Green Line** (North-South): 32 stations (Madavara to Silk Institute)
- **Yellow Line** (RV Road-Bommasandra): 14 stations

## Development Conventions

### Code Style
- **Python**: PEP 8 compliant, type hints encouraged
- **Naming**: Descriptive function/variable names, lowercase_with_underscores
- **Comments**: Docstrings for functions using triple-quoted format

### Fare Calculation
- Uses 2026 Namma Metro rates (Effective Feb 9, 2026)
- Distance-based pricing (≤2km: 11₹, ≤4km: 21₹, etc.)
- Always calculate from route list and connections_df

### Data Column Names
- Stations: `Station` or `Station_Name` (check both)
- Connections: `Station1`, `Station2`, `Distance_km` (case-sensitive)
- Graph operations: Use NetworkX bidirectional edges for consistency

### Visualization Patterns
- Use Plotly for interactive charts (preferred over Matplotlib)
- Implement Streamlit's memoization (`@st.cache_data`) for expensive operations
- Color scheme: Purple (#6a1b9a), Green (#2e7d32), Gold (#f9a825) for lines

## Common Tasks

### Adding New Visualization
1. Create function in `visualization.py` (accepts data, returns Plotly/Matplotlib figure)
2. Import and call in `app.py` with appropriate section
3. Follow existing naming: `plot_[metric]()` pattern

### Adding Route Finding Features
1. Extend graph operations in `route_finder.py`
2. Use `create_metro_graph()` to get NetworkX graph
3. Ensure bidirectional edges for realistic metro navigation
4. Update fare calculation if needed (reference 2026 rates)

### Extending Google Maps Integration
- API key required in `.streamlit/secrets.toml`
- See [GOOGLE_MAPS_SETUP.md](GOOGLE_MAPS_SETUP.md) for required APIs
- Follow pattern in `google_maps_integration.py`

### Working with Passenger Data
- Load via `metro_data.load_passenger_data()`
- Aggregate in `monthly_stats.py` functions
- Handle missing data gracefully (use Pandas fillna/dropna)

## Potential Pitfalls
- **Station name mismatches**: Some stations appear in multiple lines (e.g., Majestic) - verify Line column when filtering
- **Distance precision**: Connections_df distances may have rounding; use rounded comparisons
- **API quota**: Google Maps calls are rate-limited; cache results
- **Graph traversal**: Ensure connections are bidirectional; use `nx.Graph()` not `nx.DiGraph()`
- **Streamlit reruns**: Optimize with `@st.cache_data` to avoid recalculating data on every interaction

## File Locations & Quick Reference
| Purpose | File |
|---------|------|
| Main app | [app.py](app.py) |
| Data loading | [metro_data.py](metro_data.py) |
| Route & fare logic | [route_finder.py](route_finder.py) |
| Charts & visuals | [visualization.py](visualization.py) |
| Google Maps API | [google_maps_integration.py](google_maps_integration.py) |
| Station data | [data/bengaluru_metro_stations.csv](data/bengaluru_metro_stations.csv) |
| API setup guide | [GOOGLE_MAPS_SETUP.md](GOOGLE_MAPS_SETUP.md) |

## Related Documentation
- [GOOGLE_MAPS_SETUP.md](GOOGLE_MAPS_SETUP.md) - Google Maps API configuration
- [GOOGLE_MAPS_QUICK_START.md](GOOGLE_MAPS_QUICK_START.md) - Quick reference for Maps features
