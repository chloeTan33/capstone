import pandas as pd
import streamlit as st
import plotly.express as px

# Title
st.title("COVID-19 Data Dashboard")

st.write("""
Interactive dashboard showing COVID-19 trends.
Data source: Johns Hopkins CSSE.
""")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/" \
          "csse_covid_19_data/csse_covid_19_time_series/" \
          "time_series_covid19_confirmed_global.csv"

    df = pd.read_csv(url)

    df = df.drop(columns=["Province/State", "Lat", "Long"])
    df = df.groupby("Country/Region").sum()

    return df

data = load_data()

# Sidebar controls
st.sidebar.header("Controls")

countries = st.sidebar.multiselect(
    "Select countries",
    options=data.index.tolist(),
    default=["US"]
)

data_type = st.sidebar.radio(
    "Data type",
    ["Cumulative Cases", "Daily New Cases"]
)

# Process and visualize data
if countries:
    df_selected = data.loc[countries].T
    df_selected.index = pd.to_datetime(df_selected.index)

    if data_type == "Daily New Cases":
        df_selected = df_selected.diff().fillna(0)

    # Convert to long format for Plotly
    df_long = df_selected.reset_index().melt(
        id_vars="index",
        var_name="Country",
        value_name="Cases"
    )

    df_long = df_long.rename(columns={"index": "Date"})

    # Plot line chart
    fig = px.line(
        df_long,
        x="Date",
        y="Cases",
        color="Country",
        title=data_type
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Please select at least one country.")

# Prepare data for animated map
df_time = data.T.copy()
df_time.index = pd.to_datetime(df_time.index)

# Convert to long format
df_time = df_time.reset_index().melt(
    id_vars="index",
    var_name="Country",
    value_name="Cases"
)

df_time = df_time.rename(columns={"index": "Date"})

# Optional: choose cumulative or daily
map_type = st.sidebar.radio(
    "Map Data Type",
    ["Cumulative Cases", "Daily New Cases"]
)

if map_type == "Daily New Cases":
    df_time["Cases"] = df_time.groupby("Country")["Cases"].diff().fillna(0)

# Convert date to string (important for animation)
df_time["Date_str"] = df_time["Date"].dt.strftime("%Y-%m-%d")

# Animated choropleth map
fig_map = px.choropleth(
    df_time,
    locations="Country",
    locationmode="country names",
    color="Cases",
    animation_frame="Date_str",
    title="Global COVID-19 Over Time",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_map, use_container_width=True)