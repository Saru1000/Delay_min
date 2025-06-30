# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import base64

# Set Streamlit page config
st.set_page_config(layout="wide", page_title="Logistics Performance Dashboard")

# Load data
@st.cache_data

def load_data():
    df = pd.read_excel("Transportation and Logistics Tracking Dataset..xlsx", sheet_name=0)
    df['delay_mins'] = (df['actual_eta'] - df['Planned_ETA']).dt.total_seconds() / 60
    df['delay_mins'] = df['delay_mins'].fillna(0)
    df['Month'] = df['BookingID_Date'].dt.to_period("M").astype(str)
    return df

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.title("🔍 Filter Data")
selected_origin = st.sidebar.multiselect("Select Origin Location", df['Origin_Location'].unique())
selected_destination = st.sidebar.multiselect("Select Destination Location", df['Destination_Location'].unique())
selected_item = st.sidebar.multiselect("Select Item Shipped", df['Material Shipped'].unique())
selected_route = st.sidebar.multiselect("Select Route", df['Origin_Location'] + ' ➝ ' + df['Destination_Location'])
selected_delay_type = st.sidebar.selectbox("Delay Type", ["All", "Delayed Only"])

# Apply filters
if selected_origin:
    df = df[df['Origin_Location'].isin(selected_origin)]
if selected_destination:
    df = df[df['Destination_Location'].isin(selected_destination)]
if selected_item:
    df = df[df['Material Shipped'].isin(selected_item)]
if selected_route:
    routes = selected_route
    df['Route'] = df['Origin_Location'] + ' ➝ ' + df['Destination_Location']
    df = df[df['Route'].isin(routes)]
if selected_delay_type == "Delayed Only":
    df = df[df['delay_mins'] > 0]

# KPI metrics
st.title("🚚 Logistics Performance Dashboard")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(label="Avg Delay (mins)", value=round(df['delay_mins'].mean(), 2))
with kpi2:
    st.metric(label="% Delayed Trips", value=f"{round((df['delay_mins'] > 0).mean() * 100, 2)}%")
with kpi3:
    st.metric(label="Total Trips", value=df.shape[0])

# Tabs for sections
tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "📈 Trends & Distributions", "📥 Download"])

with tab1:
    st.subheader("🔹 Delay by Route")
    st.markdown("This bar chart shows average delay (in minutes) across different routes.")
    fig = px.bar(df.groupby('Route')['delay_mins'].mean().sort_values(ascending=False).head(10),
                 orientation='v', labels={'value': 'Avg Delay (mins)', 'Route': 'Route'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔹 Delay by Supplier")
    st.markdown("This pie chart visualizes the share of total delay (in minutes) by supplier.")
    fig = px.pie(df, names='supplierNameCode', values='delay_mins', title='Delay Distribution by Supplier')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔹 Delay by Vehicle Type")
    st.markdown("Bar chart showing average delay per vehicle type.")
    fig = px.bar(df.groupby('vehicleType')['delay_mins'].mean().sort_values(ascending=False).head(10))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📦 Delay Distribution Histogram")
    st.markdown("This histogram shows the frequency distribution of delays in minutes.")
    fig = px.histogram(df, x='delay_mins', nbins=50, title='Delay Distribution')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Monthly Trend of Average Delay")
    st.markdown("This line chart shows how average delay changes over months.")
    trend_df = df.groupby('Month')['delay_mins'].mean().reset_index()
    fig = px.line(trend_df, x='Month', y='delay_mins', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Boxplot of Delays by Supplier")
    st.markdown("This boxplot helps detect variability in delay times across suppliers.")
    fig = px.box(df[df['delay_mins'] < 500], x='supplierNameCode', y='delay_mins')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Correlation Heatmap")
    st.markdown("Heatmap showing relationships between numerical features.")
    numeric_df = df.select_dtypes(include=['float64'])
    corr = numeric_df.corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

with tab3:
    st.subheader("📥 Export Filtered Data")
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_logistics_data.csv',
        mime='text/csv',
    )

    st.dataframe(df.head(100))
