import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

def groupby_and_agg(df, groupby_column, agg_column, agg_func):
    """Generic function to groupby and aggregate data"""
    result_df = df.groupby(groupby_column).agg({agg_column: agg_func})
    result_df = result_df.reset_index()
    return result_df

def get_total_count_by_hour_df(hour_df):
    return groupby_and_agg(hour_df, "hours", "count_cr", "sum")

def count_by_day_df(day_df):
    return day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))

def total_registered_df(day_df):
    return groupby_and_agg(day_df, "dteday", "registered", "sum").rename(columns={"registered": "register_sum"})

def total_casual_df(day_df):
    return groupby_and_agg(day_df, "dteday", "casual", "sum").rename(columns={"casual": "casual_sum"})

def sum_order(hour_df):
    return hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()

def macem_season(day_df):
    return day_df.groupby("season").count_cr.sum().reset_index()

days_df = pd.read_csv("day_clean.csv")
hours_df = pd.read_csv("hour_clean.csv")

datetime_columns = ["dteday"]

def prepare_df(df):
    df.sort_values(by="dteday", inplace=True)
    df.reset_index(inplace=True)
    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column])
    return df

days_df = prepare_df(days_df)
hours_df = prepare_df(hours_df)

min_date = days_df["dteday"].min()
max_date = days_df["dteday"].max()

with st.sidebar:
    st.write("")  # Add an empty line to move the date input down
    st.write("")  # Add another empty line to move the date input down
    st.header("Pilih Rentang Waktu")  # Make the text larger and centered
    st.write("")  # Add an empty line to move the date input down
    start_date, end_date = st.date_input(
        label='',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date])

def filter_df(df, start_date, end_date):
    return df[(df["dteday"] >= str(start_date)) & (df["dteday"] <= str(end_date))]

main_df_days = filter_df(days_df, start_date, end_date)
main_df_hour = filter_df(hours_df, start_date, end_date)

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)

#Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.title('Bike Sharing-Proyek Analisis Data')

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.count_cr.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_sum)

st.subheader("Bagaimana perbandingan penyewaan sepeda pada hari kerja dengan hari weekend?")

# Define a function to create the pie chart

def create_pie_chart(hour_df):
    values = hour_df.groupby('category_days')['count_cr'].sum()
    fig, ax = plt.subplots(figsize=(8,6))
    ax.pie(values, labels=['Weekdays', 'Weekend'], autopct='%1.1f%%')
    ax.set_title('Perbandingan Penyewaan Sepeda pada Weekdays dan Weekend')
    ax.legend(title='Kategori', labels=[f'Weekdays ({values[0]})', f'Weekend ({values[1]})'], bbox_to_anchor=(1.2, 0.5), loc='center right')
    st.pyplot(fig)

hour_df = pd.read_csv('hour_clean.csv')
create_pie_chart(hour_df)

st.write(
    """
    \n
    \n
    """
)

st.write(
    "**Dari grafik tersebut kita bisa melihat ada perbedaan yang sangat besar berkaitan dengan hari-hari dimana orang biasa menyewa sepeda. Sebanyak 72% transaksi penyewaan yang terjadi dilakukan pada hari kerja (Weekdays) dan sisanya yakni 28% dilakukan pada hari akhir pekan (Weekend)**"
    )

st.subheader("Bagaimana pengaruh cuaca terhadap banyaknya penyewa sepeda?")

import streamlit as st
import matplotlib.pyplot as plt

# Create a function to create the bar chart
def create_bar_chart(hour_df):
    fig, ax = plt.subplots(figsize=(8,6))
    hour_df.groupby('weather_situation')['count_cr'].sum().plot(kind='bar', ax=ax, color=['blue', 'green', 'red', 'yellow', 'purple'])

    # Tambahkan label untuk setiap bar
    labels = [f"{k}: {v:,}" for k, v in zip(hour_df.groupby('weather_situation')['count_cr'].sum().index, hour_df.groupby('weather_situation')['count_cr'].sum().values)]
    for i, label in enumerate(labels):
        ax.bar(hour_df.groupby('weather_situation')['count_cr'].sum().index[i], hour_df.groupby('weather_situation')['count_cr'].sum().values[i], label=label)

    ax.set_xlabel('Cuaca')
    ax.set_ylabel('Jumlah Penyewa Sepeda')
    ax.set_title('Pengaruh Cuaca terhadap Banyaknya Penyewa Sepeda')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    # Tambahkan legenda
    ax.legend(bbox_to_anchor=(1.2, 0.5), loc='center right', title='Keterangan')

    st.pyplot(fig)

# Create a Streamlit app
hour_df = pd.read_csv('hour_clean.csv')  # Load your data here
create_bar_chart(hour_df)

st.write("**Dari grafik tersebut kita bisa melihat bahwa cuaca yang terjadi disetiap harinya berpengaruh terhadap banyaknya penyewaan sepeda yang terjadi. Penyewaan sepeda sangat tinggi saat cuaca sedang cerah, disusul dengan saat cuaca berawan dan paling sedikit saat hujan lebat atau sangat bersalju.**")