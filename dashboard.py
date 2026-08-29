import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import date
import os

sns.set_theme(style='dark')

# Helper functions
def create_monthly_pm25_df(df):
    monthly_df = df.resample(rule='ME', on='datetime').agg({
        "PM2.5": "mean",
        "PM10": "mean"
    })
    monthly_df = monthly_df.reset_index()
    return monthly_df

def create_by_station_df(df):
    by_station_df = df.groupby(by="station").agg({
        "PM2.5": "mean"
    }).reset_index()
    by_station_df.sort_values(by="PM2.5", ascending=False, inplace=True)
    return by_station_df

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('main_data.csv')
    except FileNotFoundError:
        st.error("Error: File main_data.csv tidak ditemukan. Silakan jalankan seluruh cell di notebook terlebih dahulu.")
        st.stop()
    if 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

all_df = load_data()
all_df.sort_values(by="datetime", inplace=True)
all_df.reset_index(inplace=True)

min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].min().date()
if not pd.isnull(all_df["datetime"].max()):
    max_date = all_df["datetime"].max().date()

with st.sidebar:
    st.header("Air Quality Dashboard")
    # Date range input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["datetime"].dt.date >= start_date) & 
                (all_df["datetime"].dt.date <= end_date)]

monthly_pm25_df = create_monthly_pm25_df(main_df)
by_station_df = create_by_station_df(main_df)

st.header('Air Quality Dashboard :cloud:')

st.subheader('Monthly PM2.5 & PM10 Levels')
col1, col2 = st.columns(2)
with col1:
    avg_pm25 = round(monthly_pm25_df["PM2.5"].mean(), 2)
    st.metric("Average PM2.5", value=avg_pm25)
with col2:
    avg_pm10 = round(monthly_pm25_df["PM10"].mean(), 2)
    st.metric("Average PM10", value=avg_pm10)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_pm25_df["datetime"],
    monthly_pm25_df["PM2.5"],
    marker='o', 
    linewidth=2,
    color="#90CAF9",
    label="PM2.5"
)
ax.plot(
    monthly_pm25_df["datetime"],
    monthly_pm25_df["PM10"],
    marker='o', 
    linewidth=2,
    color="#FFAB91",
    label="PM10"
)
ax.legend()
ax.set_title("Monthly Trend of PM2.5 and PM10", loc="center", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15, rotation=45)
st.pyplot(fig)

st.subheader("Average PM2.5 by Station")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="PM2.5", 
    y="station",
    data=by_station_df,
    ax=ax,
    palette="viridis",
    hue="station",
    legend=False
)
ax.set_title("Average PM2.5 Levels Across Stations", loc="center", fontsize=20)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.caption('Copyright (C) 2026')
