import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# Set up page configurations
st.set_page_config(page_title="Malaysia State Highlight", layout="wide")
st.title("🗺️ Interactive Malaysia State Highlighter")
st.write("Select a state from the dropdown menu to highlight it and zoom into its official GIS boundaries.")

# 1. Safely parse the high-fidelity boundaries locally from within your repository folder
@st.cache_data
def load_local_gis():
    with open("malaysia.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

malaysia_geojson = load_local_gis()

# 2. Extract valid state designations directly from the local properties layer
state_list = sorted([feature['properties']['NAME_1'] for feature in malaysia_geojson['features']])

# 3. Render the native Streamlit select box tool
selected_state = st.selectbox("Choose a state to focus on:", state_list, index=state_list.index("Selangor"))

# 4. Loop through to isolate targeted properties and calculate accurate view centers
target_coords = []
for feature in malaysia_geojson['features']:
    if feature['properties']['NAME_1'] == selected_state:
        # Extract geometry components to calculate spatial balance
        coords = feature['geometry']['coordinates']
        
        all_lats = []
        all_lngs = []
        
        def recursive_extract(c_list):
            for item in c_list:
                if isinstance(item, list):
                    recursive_extract(item)
                else:
                    all_lngs.append(item)
                    all_lats.append(item)
                    
        recursive_extract(coords)
        break

# Compute true spatial centers dynamically to align camera viewports perfectly
avg_lat = sum(all_lats) / len(all_lats) if all_lats else 4.2105
avg_lng = sum(all_lngs) / len(all_lngs) if all_lngs else 101.9758

# Choose an optimized frame scale to cover the target state cleanly
zoom_level = 7 if selected_state in ["Sarawak", "Sabah"] else 9

# 5. Build the primary interactive map frame centered exactly over your choice
mymap = folium.Map(
    location=[avg_lat, avg_lng], 
    zoom_start=zoom_level, 
    tiles="CartoDB positron"
)

# 6. Apply smooth dynamic vector layer styles
def style_function(feature):
    state_name = feature['properties']['NAME_1']
    if state_name == selected_state:
        return {
            'fillColor': '#FF2D55',   # Official Crimson highlight
            'color': '#D32F2F',       # Prominent boundary border stroke
            'fillOpacity': 0.6,
            'weight': 3
        }
    else:
        return {
            'fillColor': '#ECEFF1',   # Clean muted background layout
            'color': '#CFD8DC',       # Soft structural border lines
            'fillOpacity': 0.2,
            'weight': 1
        }

# 7. Render your complete structural mapping layer
folium.GeoJson(
    malaysia_geojson,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['NAME_1'], aliases=['State: '])
).add_to(mymap)

# 8. Output onto the user viewport container
st_folium(mymap, width="100%", height=600, returned_objects=[])
