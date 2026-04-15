import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ModuleNotFoundError:
    px = None
    go = None
    PLOTLY_AVAILABLE = False

from route_finder import calculate_fare
from metro_data import load_station_data, load_connection_data, load_passenger_data, load_hourly_breakdown
from route_finder import find_route, get_all_stations, create_metro_graph, find_alternative_routes

from visualization import (
    plot_selected_route,
    plot_monthly_passengers,
    plot_yearly_passengers,
    plot_line_utilization,
    plot_peak_hours,
    plot_passenger_growth,
    plot_station_traffic,
    plot_crowding_heatmap,
    plot_crowding_timeline
)

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Namma Metro • Analytics Pro",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------------
# PRO MAX GLOBAL CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary-purple: #6a1b9a;
        --primary-green: #2e7d32;
        --accent-gold: #f9a825;
        --bg-gradient: linear-gradient(145deg, #f5f7fa 0%, #e9ecf2 100%);
        --card-bg: rgba(255, 255, 255, 0.75);
        --glass-border: 1px solid rgba(255, 255, 255, 0.3);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-gradient: linear-gradient(145deg, #1a1f2c 0%, #0f141e 100%);
            --card-bg: rgba(20, 25, 35, 0.85);
            --glass-border: 1px solid rgba(255, 255, 255, 0.08);
        }
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        scroll-behavior: smooth;
    }

    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 1.8rem 1.5rem;
        border: var(--glass-border);
        box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
        transition: all 0.25s cubic-bezier(0.2, 0, 0, 1);
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 28px 48px -12px rgba(106, 27, 154, 0.15);
        border-color: rgba(106, 27, 154, 0.2);
    }

    .kpi-value {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-purple) 0%, #ab47bc 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        line-height: 1.2;
    }

    .hero-gradient {
        background: linear-gradient(-45deg, #6a1b9a, #2e7d32, #f9a825, #6a1b9a);
        background-size: 400% 400%;
        animation: gradientFlow 12s ease infinite;
        border-radius: 32px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .nav-pill-container {
        display: flex;
        gap: 8px;
        background: var(--card-bg);
        padding: 6px;
        border-radius: 60px;
        backdrop-filter: blur(12px);
        flex-wrap: wrap;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #b0bec5; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #6a1b9a; }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    section[data-testid="stSidebar"] {
        width: 280px !important;
        background: transparent;
        backdrop-filter: blur(12px);
    }
    .st-emotion-cache-1cypcdb { background: transparent; }
    
    /* ========== MOBILE RESPONSIVE ========== */
    @media (max-width: 768px) {
        .glass-card {
            padding: 1rem 0.8rem;
            border-radius: 16px;
        }
        
        .kpi-value {
            font-size: 2rem;
        }
        
        .hero-gradient {
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
        }
        
        .nav-pill-container {
            flex-direction: column;
            gap: 4px;
            padding: 4px;
        }
        
        .stMetric {
            min-width: 100%;
        }
    }
    
    @media (max-width: 480px) {
        .glass-card {
            padding: 0.75rem 0.6rem;
            border-radius: 12px;
        }
        
        .kpi-value {
            font-size: 1.5rem;
        }
        
        h1 {
            font-size: 1.2rem !important;
        }
        
        h2 {
            font-size: 1rem !important;
        }
        
        p, span {
            font-size: 0.9rem;
        }
        
        .hero-gradient {
            padding: 0.75rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# LOAD DATA (CACHED)
# ----------------------------------------------------------------------
@st.cache_data
def load_all_data():
    stations_df = load_station_data()
    connections_df = load_connection_data()
    passenger_df = load_passenger_data()
    hourly_df = load_hourly_breakdown()
    all_stations = get_all_stations(stations_df)
    return stations_df, connections_df, passenger_df, hourly_df, all_stations

try:
    stations_df, connections_df, passenger_df, hourly_df, all_stations = load_all_data()
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}")
    st.stop()

# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------
def pro_max_kpi(title, value, delta=None, icon="🚇"):
    delta_html = ""
    if delta:
        color = "#2e7d32" if delta >= 0 else "#c62828"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<span style="color:{color}; font-size:1rem; margin-left:8px;">{arrow} {abs(delta)}%</span>'
    
    return f"""
    <div class="glass-card" style="padding: 1.5rem 1.2rem;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <span style="font-size: 2.4rem;">{icon}</span>
            <div>
                <div style="font-weight: 500; color: #64748b; letter-spacing: 0.5px;">{title}</div>
                <div style="display: flex; align-items: baseline;">
                    <span class="kpi-value">{value:,}</span>
                    {delta_html}
                </div>
            </div>
        </div>
        <div style="height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden;">
            <div style="width: 78%; height: 100%; background: linear-gradient(90deg, #6a1b9a, #ab47bc);"></div>
        </div>
    </div>
    """

def plot_yearly_passengers_pro(passenger_df):
    if not PLOTLY_AVAILABLE:
        return None
    yearly = passenger_df.groupby("Year")["Passengers"].sum().reset_index()
    fig = px.area(yearly, x="Year", y="Passengers", 
                  title="Annual Ridership Growth",
                  labels={"Passengers": "Total Passengers"},
                  color_discrete_sequence=["#6a1b9a"])
    fig.update_traces(line_shape='spline', fill='tozeroy', opacity=0.4)
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=13),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def pro_max_navigation():
    col_nav, col_spacer, col_version = st.columns([5, 1, 1])
    with col_nav:
        st.markdown('<div class="nav-pill-container">', unsafe_allow_html=True)
        pages = ["🏠 Dashboard", "📍 Route Finder", "📊 Analytics", "📈 Station Stats"]
        page_keys = ["Home Dashboard", "Route Finder", "Passenger Analysis", "Station Statistics"]
        
        current_page = st.session_state.get("page", "Home Dashboard")
        
        cols = st.columns(len(pages))
        for i, (label, key) in enumerate(zip(pages, page_keys)):
            with cols[i]:
                if st.button(label, key=f"nav_{key}", use_container_width=True,
                             type="primary" if current_page == key else "secondary"):
                    st.session_state.page = key
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_version:
        st.caption("")

# ----------------------------------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home Dashboard"

if "route_result" not in st.session_state:
    st.session_state.route_result = None
    st.session_state.lines_used = None
    st.session_state.source_station = None
    st.session_state.destination_station = None
    st.session_state.alternative_routes = None
    st.session_state.show_alternatives = False

# ----------------------------------------------------------------------
# MAIN LAYOUT
# ----------------------------------------------------------------------
pro_max_navigation()
st.markdown("<br>", unsafe_allow_html=True)

page = st.session_state.page

# ----------------------------------------------------------------------
# HOME DASHBOARD
# ----------------------------------------------------------------------
if page == "Home Dashboard":
    # Animated train header
    st.markdown("""
    <div class="train-container" style="width:100%; overflow:hidden; height:70px; position:relative;">
        <div style="font-size:3rem; animation: moveTrain 10s linear infinite; position:absolute;">
            🚂🚋🚋🚋🚋🚋🚋
        </div>
    </div>
    <style>
        @keyframes moveTrain {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
    </style>
    """, unsafe_allow_html=True)

    # Colored Title Label (below train)
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 10px 0 20px 0;">
        <div style="background: linear-gradient(135deg, #6a1b9a 0%, #2e7d32 100%);
                    padding: 12px 40px;
                    border-radius: 60px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                    display: inline-block;">
            <h1 style="color: white;
                       font-size: 2rem;
                       margin: 0;
                       text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
                       letter-spacing: 0.5px;">
                🚇 Bengaluru Metro Transit Tracking and Analytics
            </h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero gradient with subtitle only
    st.markdown('<div class="hero-gradient">', unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(0,0,0,0.8); font-size:1.2rem; font-weight:500; text-align:center; margin:0;'>Real-time analytics and intelligent route planning</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # KPI Row (unchanged)
    col1, col2, col3 = st.columns(3)
    col1.markdown(pro_max_kpi("Active Stations", len(stations_df), delta=5.2, icon="🚉"), unsafe_allow_html=True)
    col2.markdown(pro_max_kpi("Network Connections", len(connections_df), delta=12, icon="🔗"), unsafe_allow_html=True)
    col3.markdown(pro_max_kpi("Monthly Ridership", passenger_df["Passengers"].sum(), delta=-2.1, icon="👥"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Yearly trend chart (Plotly)
    st.subheader("📈 Yearly Passenger Trend")
    yearly_plot = plot_yearly_passengers_pro(passenger_df)
    if yearly_plot is not None:
        st.plotly_chart(yearly_plot, use_container_width=True)
    else:
        st.pyplot(plot_yearly_passengers(passenger_df))

# ----------------------------------------------------------------------
# ROUTE FINDER
# ----------------------------------------------------------------------
elif page == "Route Finder":
    st.header("📍 Intelligent Route Finder")
    
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Select Source Station", all_stations)
    with col2:
        destination = st.selectbox("Select Destination", [s for s in all_stations if s != source])
    
    col_find, col_alt = st.columns([3, 1])
    with col_find:
        find_route_btn = st.button("🚆 Find Best Route", type="primary", use_container_width=True)
    with col_alt:
        show_alternatives = st.checkbox("🔄 Compare Routes", value=False)
    
    if find_route_btn:
        with st.spinner("Calculating optimal route..."):
            if show_alternatives:
                # Find 3 alternatives
                routes_dict = find_alternative_routes(source, destination, stations_df, connections_df, passenger_df)
                if routes_dict:
                    st.session_state.alternative_routes = routes_dict
                    st.session_state.show_alternatives = True
                else:
                    st.error("❌ No routes found")
            else:
                # Find single best route
                route, lines_used = find_route(source, destination, stations_df, connections_df)
                st.session_state.route_result = route
                st.session_state.lines_used = lines_used
                st.session_state.source_station = source
                st.session_state.destination_station = destination
                st.session_state.show_alternatives = False
            st.rerun()
    
    # Display alternative routes
    if st.session_state.get("show_alternatives") and st.session_state.get("alternative_routes"):
        routes_dict = st.session_state.alternative_routes
        
        st.subheader("🗺️ Available Route Options")
        st.info("🎯 Choose the route that best fits your preferences!")
        
        # Create tabs for each route
        tab1, tab2, tab3 = st.tabs(["⚡ Shortest", "🚶 Less Crowded", "🚄 Fastest"])
        
        route_options = [
            (tab1, "Shortest", "⚡", routes_dict.get("Shortest")),
            (tab2, "Less Crowded", "🚶", routes_dict.get("Less Crowded")),
            (tab3, "Fastest", "🚄", routes_dict.get("Fastest"))
        ]
        
        for tab, route_type, emoji, route_info in route_options:
            if route_info:
                with tab:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📍 Stops", route_info['stops'])
                    col2.metric("🛤️ Distance", f"{route_info['distance']:.2f} km")
                    col3.metric("💰 Fare", f"₹{route_info['fare']}")
                    
                    st.markdown("### 🛤️ Route Details")
                    st.markdown(" → ".join([f"**{s}**" for s in route_info['path']]))
                    
                    if st.button(f"View Map for {emoji} {route_type}", key=f"view_{route_type}"):
                        st.session_state.route_result = route_info['path']
                        st.session_state.show_map_only = True
                    
                    st.markdown(f"<small>{route_info['description']}</small>", unsafe_allow_html=True)
    
    # Display selected route map
    if st.session_state.route_result:
        route = st.session_state.route_result
        st.success(f"✅ Route selected with {len(route)-1} stops")
        
        # Display route map if available
        if 'lat' in stations_df.columns and 'lon' in stations_df.columns:
            try:
                import folium
                from streamlit_folium import st_folium
                
                # Define line colors for Namma Metro
                def hex_to_folium_color(hex_color):
                    color_map = {
                        '#9b59b6': 'purple',
                        '#27ae60': 'darkgreen',
                        '#f39c12': 'orange',
                        '#e74c3c': 'red',
                        '#3498db': 'blue',
                        '#e67e22': 'darkorange'
                    }
                    return color_map.get(hex_color.lower(), 'blue')
                
                line_colors = {
                    'Purple': '#9b59b6',
                    'Green': '#27ae60',
                    'Yellow': '#f39c12',
                    'Red': '#e74c3c',
                    'Blue': '#3498db',
                    'Orange': '#e67e22'
                }
                
                # Get route coordinates
                route_coords = []
                route_info_list = []
                current_line = None
                
                for i, station in enumerate(route):
                    station_rows = stations_df[stations_df['Station'] == station]
                    
                    if len(station_rows) > 1:
                        if current_line and current_line in station_rows['Line'].values:
                            row = station_rows[station_rows['Line'] == current_line].iloc[0]
                        else:
                            row = station_rows.iloc[0]
                    else:
                        row = station_rows.iloc[0]
                    
                    route_coords.append([row['lat'], row['lon']])
                    line = row.get('Line', 'Unknown')
                    current_line = line
                    
                    route_info_list.append({
                        'station': station,
                        'stop': i + 1,
                        'lat': row['lat'],
                        'lon': row['lon'],
                        'line': line
                    })
                
                # Calculate center
                lats = [c[0] for c in route_coords]
                lons = [c[1] for c in route_coords]
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)
                
                # Create map
                m = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=13,
                    tiles='OpenStreetMap'
                )
                
                # Draw route with color coding
                for i in range(len(route_info_list) - 1):
                    curr_lat = route_info_list[i]['lat']
                    curr_lon = route_info_list[i]['lon']
                    next_lat = route_info_list[i + 1]['lat']
                    next_lon = route_info_list[i + 1]['lon']
                    line_name = route_info_list[i]['line']
                    segment_color = line_colors.get(line_name, '#95a5a6')
                    
                    folium.PolyLine(
                        [[curr_lat, curr_lon], [next_lat, next_lon]],
                        color=segment_color,
                        weight=5,
                        opacity=0.8
                    ).add_to(m)
                
                # Add markers
                for info in route_info_list:
                    stop_num = info['stop']
                    is_first = (stop_num == 1)
                    is_last = (stop_num == len(route))
                    
                    if is_first:
                        folium.Marker(
                            [info['lat'], info['lon']],
                            popup=f"START: {info['station']}",
                            tooltip=f"{info['station']} (Start)",
                            icon=folium.Icon(color='green', icon='play', prefix='fa')
                        ).add_to(m)
                    elif is_last:
                        folium.Marker(
                            [info['lat'], info['lon']],
                            popup=f"END: {info['station']}",
                            tooltip=f"{info['station']} (End)",
                            icon=folium.Icon(color='red', icon='stop', prefix='fa')
                        ).add_to(m)
                    else:
                        folium.Marker(
                            [info['lat'], info['lon']],
                            popup=f"Stop {stop_num}: {info['station']}",
                            tooltip=f"{info['station']} ({info['line']})",
                            icon=folium.Icon(color='purple', icon='circle', prefix='fa')
                        ).add_to(m)
                
                m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
                
                st.subheader("🌍 Your Route Map")
                st_folium(m, width=1200, height=500)
                
            except ImportError:
                st.info("⚠️ Install folium: `pip install folium streamlit-folium`")
        
        # Show route summary
        st.subheader("📊 Route Summary")
        distance, fare = calculate_fare(route, connections_df, stations_df)
        col1, col2, col3 = st.columns(3)
        col1.metric("📍 Total Stops", max(len(route) - 1, 0))
        col2.metric("🛤️ Distance", f"{distance:.2f} km")
        col3.metric("💰 Fare", f"₹{fare}")
        
        if st.button("🔄 Search Again"):
            st.session_state.route_result = None
            st.session_state.alternative_routes = None
            st.session_state.show_alternatives = False
            st.rerun()
    else:
        if st.session_state.get("source_station") and st.session_state.get("destination_station"):
            st.error("❌ No route found between these stations.")

# ----------------------------------------------------------------------
# PASSENGER ANALYSIS
# ----------------------------------------------------------------------
elif page == "Passenger Analysis":
    st.header("📊 Passenger Analytics Dashboard")
    
    analysis_type = st.selectbox("Select Analysis View", ["Monthly Breakdown", "Yearly Trends", "Growth Rate", "Line Comparison"])
    
    if analysis_type == "Monthly Breakdown":
        year = st.selectbox("Select Year", sorted(passenger_df["Year"].unique()))
        st.pyplot(plot_monthly_passengers(passenger_df, year))
        
    elif analysis_type == "Yearly Trends":
        yearly_plot = plot_yearly_passengers_pro(passenger_df)
        if yearly_plot is not None:
            st.plotly_chart(yearly_plot, use_container_width=True)
        else:
            st.pyplot(plot_yearly_passengers(passenger_df))
        
    elif analysis_type == "Growth Rate":
        st.subheader("📈 Year-over-Year Passenger Growth Analysis")
        
        # Calculate yearly statistics
        yearly_stats = passenger_df.groupby("Year").agg({
            "Passengers": "sum",
            "Purple_Line_Passengers": "sum",
            "Green_Line_Passengers": "sum"
        }).reset_index()
        
        yearly_stats["Total_Growth_Rate"] = yearly_stats["Passengers"].pct_change() * 100
        yearly_stats["Purple_Growth"] = yearly_stats["Purple_Line_Passengers"].pct_change() * 100
        yearly_stats["Green_Growth"] = yearly_stats["Green_Line_Passengers"].pct_change() * 100
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_year = yearly_stats["Year"].max()
            latest_passengers = yearly_stats[yearly_stats["Year"] == latest_year]["Passengers"].values[0]
            st.metric("📊 Latest Year", latest_year, f"{latest_passengers:,} passengers")
        
        with col2:
            if len(yearly_stats) > 1:
                growth_rate = yearly_stats.iloc[-1]["Total_Growth_Rate"]
                color = "🟢" if growth_rate >= 0 else "🔴"
                st.metric(f"{color} Latest Growth Rate", f"{growth_rate:.2f}%", 
                         "Increase" if growth_rate >= 0 else "Decrease")
        
        with col3:
            avg_growth = yearly_stats["Total_Growth_Rate"].mean()
            st.metric("📈 Avg Annual Growth", f"{avg_growth:.2f}%", 
                     "Well-performing" if avg_growth >= 5 else "Needs improvement")
        
        with col4:
            total_growth_5yr = ((yearly_stats["Passengers"].iloc[-1] / yearly_stats["Passengers"].iloc[0]) - 1) * 100
            st.metric("🚀 5-Year Total Growth", f"{total_growth_5yr:.1f}%", 
                     f"From {yearly_stats['Passengers'].iloc[0]:,} to {yearly_stats['Passengers'].iloc[-1]:,}")
        
        st.divider()
        
        # Display growth rate chart
        st.subheader("📊 Growth Rate Comparison")
        st.pyplot(plot_passenger_growth(passenger_df))
        
        st.divider()
        
        # Display detailed growth table
        st.subheader("📋 Detailed Year-over-Year Growth")
        
        growth_table = yearly_stats[["Year", "Passengers", "Total_Growth_Rate", 
                                    "Purple_Line_Passengers", "Purple_Growth",
                                    "Green_Line_Passengers", "Green_Growth"]].copy()
        
        growth_table.columns = ["Year", "Total Passengers", "Growth %", 
                               "Purple Line", "Purple Growth %", 
                               "Green Line", "Green Growth %"]
        
        # Format for display
        growth_table["Total Passengers"] = growth_table["Total Passengers"].apply(lambda x: f"{x:,.0f}")
        growth_table["Growth %"] = growth_table["Growth %"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        growth_table["Purple Line"] = growth_table["Purple Line"].apply(lambda x: f"{x:,.0f}")
        growth_table["Purple Growth %"] = growth_table["Purple Growth %"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        growth_table["Green Line"] = growth_table["Green Line"].apply(lambda x: f"{x:,.0f}")
        growth_table["Green Growth %"] = growth_table["Green Growth %"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        st.dataframe(growth_table, use_container_width=True)
        
        st.divider()
        
        # Growth insights
        st.subheader("💡 Growth Insights & Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **📊 Overall Performance:**
            - Total Years Tracked: {len(yearly_stats)} years
            - Starting Year: {yearly_stats['Year'].min()} with {yearly_stats['Passengers'].iloc[0]:,} passengers
            - Latest Year: {yearly_stats['Year'].max()} with {yearly_stats['Passengers'].iloc[-1]:,} passengers
            - Cumulative Growth: {total_growth_5yr:.1f}%
            """)
        
        with col2:
            purple_latest = yearly_stats.iloc[-1]["Purple_Growth"]
            green_latest = yearly_stats.iloc[-1]["Green_Growth"]
            
            st.success(f"""
            **🚇 Line-wise Performance:**
            - Purple Line Latest Growth: {purple_latest:.2f}% {'📈 Up' if purple_latest > 0 else '📉 Down'}
            - Green Line Latest Growth: {green_latest:.2f}% {'📈 Up' if green_latest > 0 else '📉 Down'}
            - Purple Line Total: {yearly_stats['Purple_Line_Passengers'].iloc[-1]:,} passengers
            - Green Line Total: {yearly_stats['Green_Line_Passengers'].iloc[-1]:,} passengers
            """)
        
        # Best and worst years
        best_year_idx = yearly_stats["Total_Growth_Rate"].idxmax()
        worst_year_idx = yearly_stats["Total_Growth_Rate"].idxmin()
        
        if pd.notna(best_year_idx) and pd.notna(worst_year_idx):
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                best_year = yearly_stats.iloc[best_year_idx]
                st.success(f"""
                **🏆 Best Growth Year:**
                - Year: {int(best_year['Year'])}
                - Growth Rate: {best_year['Total_Growth_Rate']:.2f}%
                - Passengers: {best_year['Passengers']:,}
                """)
            
            with col2:
                worst_year = yearly_stats.iloc[worst_year_idx]
                st.warning(f"""
                **⚠️ Lowest Growth Year:**
                - Year: {int(worst_year['Year'])}
                - Growth Rate: {worst_year['Total_Growth_Rate']:.2f}%
                - Passengers: {worst_year['Passengers']:,}
                """)
    
    elif analysis_type == "Line Comparison":
        st.subheader("🚇 Metro Line Comparison")
        
        # Get available years
        available_years = sorted(passenger_df["Year"].unique())
        selected_year = st.selectbox("Select Year for Line Comparison", available_years, 
                                    index=len(available_years)-1)
        
        year_data = passenger_df[passenger_df["Year"] == selected_year]
        
        # Calculate totals
        total_passengers = year_data["Passengers"].sum()
        purple_total = year_data["Purple_Line_Passengers"].sum()
        green_total = year_data["Green_Line_Passengers"].sum()
        yellow_total = year_data["Yellow_Line_Passengers"].sum() if "Yellow_Line_Passengers" in year_data.columns else max(total_passengers - purple_total - green_total, 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🟣 Purple Line", f"{purple_total:,}", 
                     f"{(purple_total/total_passengers)*100:.1f}% of total")
        
        with col2:
            st.metric("🟢 Green Line", f"{green_total:,}", 
                     f"{(green_total/total_passengers)*100:.1f}% of total")
        
        with col3:
            st.metric("🟡 Other Lines", f"{yellow_total:,}", 
                     f"{(yellow_total/total_passengers)*100:.1f}% of total")
        
        st.divider()
        
        # Line distribution chart
        if PLOTLY_AVAILABLE:
            fig = px.pie(
                values=[purple_total, green_total, yellow_total],
                names=["Purple Line", "Green Line", "Other Lines"],
                color_discrete_sequence=["#6a1b9a", "#2e7d32", "#f9a825"],
                title=f"Passenger Distribution by Line - {selected_year}"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.pie(
                [purple_total, green_total, yellow_total],
                labels=["Purple Line", "Green Line", "Other Lines"],
                colors=["#6a1b9a", "#2e7d32", "#f9a825"],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.set_title(f"Passenger Distribution by Line - {selected_year}")
            st.pyplot(fig)
        
        st.divider()
        
        # Monthly comparison
        st.subheader("📊 Monthly Comparison by Line")
        monthly_by_line = year_data[["Month", "Purple_Line_Passengers", "Green_Line_Passengers"]].copy()
        
        if PLOTLY_AVAILABLE:
            fig2 = px.bar(
                monthly_by_line,
                x="Month",
                y=["Purple_Line_Passengers", "Green_Line_Passengers"],
                barmode="group",
                title=f"Monthly Passengers by Line - {selected_year}",
                color_discrete_map={
                    "Purple_Line_Passengers": "#6a1b9a",
                    "Green_Line_Passengers": "#2e7d32"
                },
                labels={
                    "Purple_Line_Passengers": "Purple Line",
                    "Green_Line_Passengers": "Green Line"
                }
            )
            fig2.update_layout(
                xaxis_title="Month",
                yaxis_title="Passengers",
                hovermode="x unified"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            months = monthly_by_line["Month"].astype(str).tolist()
            x_axis = np.arange(len(months))
            width = 0.35
            fig2, ax2 = plt.subplots(figsize=(12, 5))
            ax2.bar(x_axis - width / 2, monthly_by_line["Purple_Line_Passengers"], width, color="#6a1b9a", label="Purple Line")
            ax2.bar(x_axis + width / 2, monthly_by_line["Green_Line_Passengers"], width, color="#2e7d32", label="Green Line")
            ax2.set_xticks(x_axis)
            ax2.set_xticklabels(months, rotation=45, ha="right")
            ax2.set_xlabel("Month")
            ax2.set_ylabel("Passengers")
            ax2.set_title(f"Monthly Passengers by Line - {selected_year}")
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig2)

# ----------------------------------------------------------------------
# STATION STATISTICS
# ----------------------------------------------------------------------
elif page == "Station Statistics":
    st.header("📈 Station Performance Metrics")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        station = st.selectbox("Select Station", all_stations)
    with col2:
        available_years = sorted(passenger_df["Year"].unique())
        year = st.selectbox("Select Year", available_years, index=len(available_years)-1,
                           help=f"Data available: {available_years[0]}-{available_years[-1]}.")
    with col3:
        show_all_stations = st.checkbox("All Stations", value=False)
    
    # Create tabs for different analytics
    tab_peak, tab_traffic, tab_crowding, tab_timeline = st.tabs(
        ["⏰ Peak Hours", "🚦 Traffic", "🔥 Crowding Heatmap", "⏳ Crowding Timeline"]
    )
    
    with tab_peak:
        st.subheader(f"⏰ Peak Hours Analysis - {station}")
        st.pyplot(plot_peak_hours(station, year, passenger_df, stations_df))
    
    with tab_traffic:
        st.subheader("🚦 Station Traffic Comparison")
        try:
            st.pyplot(plot_station_traffic(passenger_df, stations_df, year, top_n=10, show_all=show_all_stations))
        except Exception as e:
            st.error(f"Error generating traffic chart: {e}")
    
    with tab_crowding:
        st.subheader("🔥 Crowding Heatmap - Top 15 Stations")
        st.caption("Red areas indicate higher crowding. Best times to travel: early morning (6-7 AM) or late evening (9+ PM)")
        try:
            st.pyplot(plot_crowding_heatmap(stations_df, passenger_df, year, top_n=15))
        except Exception as e:
            st.error(f"Heatmap error: {e}")
    
    with tab_timeline:
        st.subheader(f"⏳ Crowding Timeline - {station}")
        st.caption("24-hour crowding pattern with recommendations")
        try:
            st.pyplot(plot_crowding_timeline(station, year))
        except Exception as e:
            st.error(f"Timeline error: {e}")
    
    # Smart recommendations section
    st.divider()
    st.subheader("💡 Smart Commute Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🟢 Best Times to Travel:**
        - Early Morning: 6:00 - 7:00 AM
        - Mid-day: 11:00 AM - 4:00 PM  
        - Late Evening: 9:00 PM - 10:00 PM
        """)
    
    with col2:
        st.warning("""
        **🔴 Times to Avoid:**
        - Morning Rush: 8:00 - 9:00 AM
        - Evening Rush: 5:00 - 8:00 PM
        - Peak hours have 5-7x more crowding!
        """)

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.markdown("""
<hr style="margin-top:40px; opacity:0.3;">
<div style="text-align:center; animation: fadeInUp 0.6s;">
    <p style="font-size:14px; margin-bottom:4px;">
        🚇 <b>Developed by Varun G S</b>
    </p>
    <p style="font-size:12px; margin-top:2px;">
        <a class="footer-link" href="https://github.com/VARUNGSV" target="_blank">GitHub</a> 
        &nbsp;|&nbsp;
        <a class="footer-link" href="https://www.linkedin.com/in/varun-gs-9b76a6286" target="_blank">LinkedIn</a>
    </p>
    <p style="font-size:10px; color:#aaa;">
        © 2026 Bengaluru Metro Interactive Analytics • 
    </p>
</div>
""", unsafe_allow_html=True)
