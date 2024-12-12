"""
Name:       Adrian Marcell
CS230:      Section 3
Data:       Nuclear Explosions 1945-1998

Description:
This program provides an interactive data explorer for the Nuclear Explosions dataset.
It allows users to filter data, visualize trends, and explore geospatial contributions.
Features include interactive plots, charts, and maps.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import plotly.express as px

# Load Data
@st.cache
def load_data():
    file_path = "nuclear_explosions.csv"
    data = pd.read_csv(file_path, encoding='latin1')

    data.rename(columns={
        "WEAPON SOURCE COUNTRY": "Source Country",
        "WEAPON DEPLOYMENT LOCATION": "Deployment Location",
        "Data.Source": "Source",
        "Location.Cordinates.Latitude": "Latitude",
        "Location.Cordinates.Longitude": "Longitude",
        "Data.Magnitude.Body": "Body Wave Magnitude",
        "Data.Magnitude.Surface": "Surface Wave Magnitude",
        "Location.Cordinates.Depth": "Depth",
        "Data.Yeild.Lower": "Explosion Yield L",
        "Data.Yeild.Upper": "Explosion Yield U",
        "Data.Purpose": "Purpose",
        "Data.Name": "Name",
        "Data.Type": "Type",
        "Date.Day": "Day",
        "Date.Month": "Month",
        "Date.Year": "Year"
    }, inplace=True)

    data["Name"] = data["Name"].fillna("Unnamed")
    data["Explosion Yield Average"] = (data["Explosion Yield L"] + data["Explosion Yield U"]) / 2

    return data

data = load_data()

st.sidebar.title("Filter Options")
selected_country = st.sidebar.multiselect("Select Country", data["Source Country"].unique(), default=data["Source Country"].unique())
selected_year = st.sidebar.slider("Select Year Range", int(data["Year"].min()), int(data["Year"].max()), (1960, 1980))

filtered_data = data[(data["Source Country"].isin(selected_country)) &
                     (data["Year"].between(*selected_year))]

st.title("Nuclear Explosions: Data Explorer")
st.dataframe(filtered_data)

# Visualization 1: Scatter Plot
st.subheader("Explosion Yields of Different Nuclear Weapons")
plt.figure(figsize=(10, 6))
sns.scatterplot(x=filtered_data["Name"][:10], y=filtered_data["Explosion Yield Average"][:10])
plt.title("Explosion Yields")
plt.xlabel("Name")
plt.ylabel("Yield (Kilotons)")
st.pyplot(plt)

# Visualization 2: Bar Chart
st.subheader("Most Explosive Nuclear Weapons")
top_explosions = filtered_data.sort_values(by="Explosion Yield Average", ascending=False).head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_explosions["Name"], y=top_explosions["Explosion Yield Average"], palette="viridis")
plt.title("Top 10 Most Explosive Nuclear Weapons")
plt.xlabel("Name")
plt.ylabel("Yield (Kilotons)")
st.pyplot(plt)

# Visualization 3: Choropleth Map
st.subheader("Geospatial Contribution by Source Country")

source_country_counts = filtered_data["Source Country"].value_counts().reset_index()
source_country_counts.columns = ["Source Country", "Count"]  # Rename columns for clarity

fig = px.choropleth(
    data_frame=source_country_counts,
    locations="Source Country",  # Column with country names
    locationmode="country names",  # Match country names
    color="Count",  # Column to determine the color intensity
    title="Number of Nuclear Tests by Country",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={"Count": "Number of Tests"},  # Label for the color bar
)

st.plotly_chart(fig)

# Visualization 4: PyDeck Map - Map of Nuclear Test Locations
st.subheader("Map of Nuclear Test Locations")

map_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_data,
    get_position=["Longitude", "Latitude"],
    get_radius="Explosion Yield Average * 1000000",  # Increased radius multiplier
    get_fill_color="[200, 30, 0, 160]",  # Red color
    pickable=True,  # Enable hover interaction
)

view_state = pdk.ViewState(
    latitude=filtered_data["Latitude"].mean(),
    longitude=filtered_data["Longitude"].mean(),
    zoom=3,
    pitch=0,
)

map_deck = pdk.Deck(layers=[map_layer], initial_view_state=view_state, tooltip={"text": "{Name}"})

st.pydeck_chart(map_deck, use_container_width=True)

st.subheader("Data Summary")
st.write("**Top Source Countries**")
st.write(filtered_data["Source Country"].value_counts())

st.write("**Average Explosion Yield**")
avg_yield = filtered_data["Explosion Yield Average"].mean()
st.write(f"Average Yield: {avg_yield:.2f} Kilotons")

# Footer
st.markdown("---")
st.markdown("Developed by Adrian, CS230 Final Project")
