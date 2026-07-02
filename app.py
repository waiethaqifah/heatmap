import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd

# Set up page configurations
st.set_page_config(page_title="Malaysia State Highlight", layout="wide")
st.title("🗺️ Interactive Malaysia State Highlighter")
st.write("Select a state from the dropdown menu to highlight it and zoom into its official GIS boundaries.")

# 1. Fetch the official, high-fidelity Malaysia boundaries file
@st.cache_data
def load_gis_data():
    url = "https://githubusercontent.com"
    return gpd.read_file(url)

malaysia_gdf = load_gis_data()

# 2. Extract list of valid state names from the dataset for the dropdown filter
state_list = sorted(malaysia_gdf['NAME_1'].unique())

# 3. Create the native Streamlit dropdown selection menu
selected_state = st.selectbox("Choose a state to focus on:", state_list, index=state_list.index("Selangor"))

# 4. Isolate the target state data to calculate centers and bounds
target_state_data = malaysia_gdf[malaysia_gdf['NAME_1'] == selected_state]
centroid = target_state_data.geometry.centroid.iloc[0]

# Determine an optimized zoom level depending on the size of the territory
zoom_level = 7 if selected_state in ["Sarawak", "Sabah"] else 9

# 5. Initialize the Leaflet map container centered directly over the chosen state
mymap = folium.Map(
    location=[centroid.y, centroid.x], 
    zoom_start=zoom_level, 
    tiles="CartoDB positron"
)

# 6. Apply dynamic styling rules
# The selected state gets a high-contrast crimson fill, others remain transparent grey
def style_function(feature):
    state_name = feature['properties']['NAME_1']
    if state_name == selected_state:
        return {
            'fillColor': '#FF2D55',   # Premium Crimson Red highlight
            'color': '#D32F2F',       # Sharp matching border
            'fillOpacity': 0.6,
            'weight': 3
        }
    else:
        return {
            'fillColor': '#ECEFF1',   # Neutral background grey
            'color': '#CFD8DC',       # Soft structural border lines
            'fillOpacity': 0.2,
            'weight': 1
        }

# 7. Add the perfect official vector layer onto your map canvas
folium.GeoJson(
    malaysia_gdf.to_json(),
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['NAME_1'], aliases=['State: '])
).add_to(mymap)

# 8. Render the interactive map seamlessly within the Streamlit app workspace
st_folium(mymap, width="100%", height=600, returned_objects=[])
