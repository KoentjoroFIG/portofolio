import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

#Mendefinisikan semua fungsi yang diperlukan
#-------------------------------------------------------------
#Membuat tren rental harian
def create_daily_tren_df(df):
    daily_tren_df = df.resample(rule='D', on='dteday').agg({
        "casual":'sum',
        'registered':'sum',
        'cnt':'sum'
    })
    daily_tren_df.reset_index(inplace=True)
    daily_tren_df.rename(
        columns={
            'cnt':'total_rental'
        },
        inplace=True
    )

    return daily_tren_df

#Membuat tren perjam
def creat_hourly_tren_df(df):
    hourly_tren_df = df.groupby(by='hr').agg({
        "casual":'sum',
        'registered':'sum',
        'cnt':'sum'
    })
    hourly_tren_df.reset_index(inplace=True)
    hourly_tren_df.rename(
        columns={
            'cnt':'total_rental',
        },
        inplace=True
    )

    return hourly_tren_df
#-------------------------------------------------------------



#Mempersiapkan dataset
#---------------------------------------------
hour_df = pd.read_csv('hour.csv')
day_df = pd.read_csv('day.csv')

#Mengubah dtype kolom dteday menjadi datetime
hour_df["dteday"] = pd.to_datetime(hour_df['dteday'])
day_df["dteday"] = pd.to_datetime(day_df['dteday'])
#---------------------------------------------


#Membuat filter
#----------------------------------------------------------------
min_hour = hour_df.hr.min()
max_hour = hour_df.hr.max()
min_date = hour_df.dteday.min()
max_date = hour_df.dteday.max()

with st.sidebar:
    st.header(":blue[Bike Rental Analysis] :bike:", divider='green')
    
    dates = st.date_input(
        label='Time Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if len(dates) == 2:
        start_date, end_date = dates
    else:
        st.error(
            'Pleae, Choose the End Date'
        )
        start_date = dates[0]
        end_date = None

    if start_date == end_date:
        start_hour, end_hour = st.slider(
            label = 'Hour Range',
            min_value=min_hour,
            max_value=max_hour,
            value=(min_hour, max_hour),
        )
#----------------------------------------------------------------


#Memfilter dataset
#---------------------------------------------------------------------------    
try:
    main_df = hour_df[
        (hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))
    ]
    if start_date == end_date:
        main_df = main_df[
            (main_df["hr"] >= start_hour) & (main_df["hr"] <= end_hour)
        ]
    else:
        pass
except TypeError:
    main_df = hour_df
#---------------------------------------------------------------------------

#Membuat Header
st.header(':blue[Bike Rental Analysis] :bike:', divider='orange')
st.write("""Author: Fajrul Iman Giat Koentjoro \n
Source Code: https://github.com/KoentjoroFIG/dashboard_dicoding
""")
st.divider()


#Menampilkam Daily/Hourly Tren
#----------------------------------------------
if start_date == end_date:
    tren_df = creat_hourly_tren_df(main_df)
    st.subheader('Hourly Tren')
else:
    tren_df = create_daily_tren_df(main_df)
    st.subheader('Daily Tren')

col1, col2, col3 = st.columns(3)

#Menampilkan jumlah rental maximal
with col1:
    max_rent = tren_df.total_rental.max()
    st.metric('Max Rental', value=max_rent)

#Menampilkan jumlah rental minimal
with col2:
    min_rent = tren_df.total_rental.min()
    st.metric('Min Rental', value=min_rent)

#Menampilkan total rental
with col3:
    total_rent = tren_df.total_rental.sum()
    st.metric('Total Rental', value=total_rent)

#Menampilkan line chart dari tren harian/jam
fig, ax = plt.subplots(figsize=(16, 8))

x_axis = 'hr' if start_date == end_date else 'dteday'
for column in tren_df.drop(x_axis, axis='columns').columns:
    if column == 'total_rental':
        sns.lineplot(
            data=tren_df, 
            y=column,
            x=x_axis, 
            ax=ax,
            marker='o',
            label=column,
        )
    else:
        sns.lineplot(
            data=tren_df, 
            y=column,
            x=x_axis, 
            ax=ax,
            linestyle='--',
            marker='o',
            label=column
        )

ax.set_ylabel(
    'Total Rental', 
    fontsize=15
)
ax.set_xlabel(
    xlabel='Hour' if start_date == end_date else 'Date', 
    fontsize=15
)
ax.tick_params(
    axis='y', 
    labelsize=15
)
ax.tick_params(
    axis='x', 
    labelsize=15
)
ax.legend(fontsize='x-large')

st.pyplot(fig)
st.divider()
#---------------------------------------------


#Menampilkan pengaruh musim terhadap jumlah rental
#------------------------------------------------------------
st.subheader('The effect of Season on Rental Amount')
st.write(
    pd.DataFrame(
        {
            'Code':[1, 2, 3, 4],
            'Season': ['Spring', 'Summer', 'Fall', 'Winter']
        }
    ).set_index('Code')
)

season_cnt_df = day_df[['season', 'cnt']]
season_gb = day_df.groupby(by=['season']).agg({
    'cnt':'sum',
})
season_year_gb = day_df.groupby(by=['season', 'yr']).agg({
    'cnt':'sum',
})

#Menampilkan scatterplot
fig, ax = plt.subplots()
sns.scatterplot(
    x='season',
    y='cnt', 
    data=season_cnt_df
)

ax.set_xticks(season_cnt_df['season'].unique())
ax.set_xlabel(
    'Season',
    fontsize = 8
)
ax.set_ylabel(
    'Number of Rental (cnt)',
    fontsize = 8
)
ax.set_title(
    'Bike Rental Trends During the Four Seasons', 
    loc = 'center',
    fontsize = 12
)
ax.tick_params(
    axis='y', 
    labelsize=8
)
ax.tick_params(
    axis='x', 
    labelsize=8
)

st.pyplot(fig)

#Menampilkan total rental per musim
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 15))

    colors = ['b' if x < max(season_gb.cnt) else 'r' for x in season_gb.cnt]
    sns.barplot(
        data=season_gb.reset_index(), 
        x='season', 
        y='cnt', 
        palette=colors,
    )
    ax.set_xlabel(
        'Season',
        fontsize = 30
    )
    ax.set_ylabel(
        'Total Rental', 
        fontsize = 30
    )
    ax.set_title(
        'Total Rentals per Season',
        loc='center',
        fontsize=50
    )
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 15))

    plot = sns.barplot(x='season', y='cnt', hue='yr', data=season_year_gb.reset_index())
    handles, labels = plot.get_legend_handles_labels()
    labels = ['2011', '2012']
    ax.legend(handles, labels, fontsize='30')
    ax.set_xlabel(
        'Season',
        fontsize = 30
    )
    ax.set_ylabel(
        'Total Rental', 
        fontsize = 30
    )
    ax.set_title(
        'Total Rental per Season and Year',
        loc='center',
        fontsize=50
    )
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    
    st.pyplot(fig)

st.divider()
#------------------------------------------------------------


#Pengaruh weathersit terhadap rata-rata jumlah rental per musim
#--------------------------------------------------------------------------
st.subheader('The effect of weathersit on the average number of rentals per season')
st.write(
    pd.DataFrame(
        {
            'Code':[1, 2, 3, 4],
            'Season': ['Spring', 'Summer', 'Fall', 'Winter'],
            'Weathersit':[
                "Clear, Few clouds, Partly cloudy, Partly cloudy",
                "Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist",
                "Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds",
                "Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog"
            ]
        }
    ).set_index('Code')
)

weathersit_gb = hour_df.groupby(by=['season', 'weathersit']).agg({
    'cnt':'mean'
})

#Menampilkan barplot
fig, ax = plt.subplots()

plot = sns.barplot(
    x='season', 
    y='cnt', 
    hue='weathersit', 
    data=weathersit_gb.reset_index()
)
handles, labels = plot.get_legend_handles_labels()
ax.legend(handles, labels)
ax.set_xlabel(
    'Season', 
    fontsize=10
)
ax.set_ylabel(
    'Rental Average', 
    fontsize=10
)
ax.set_title(
    'The Effect of Weathersit on the Average Number of Rentals per Season', 
    fontsize=11
)
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)

st.pyplot(fig)
st.divider()
#--------------------------------------------------------------------------


#Korelasi faktor alam terhadap jumlah rental
#-----------------------------------------------------------------------
st.subheader('Correlation between natural factors and the number of rentals')
st.write(
    pd.DataFrame(
        {
            'Columns':['weathersit', 'temp', 'atemp', 'hum', 'windspeed', 'cnt'],
            'Meaning': ['Weather situation', 'Temperature in Celsius', 'Feeling temperature in Celsius', 'Humidity', 'Wind speed', 'count of total rental bikes']
        }
    ).set_index('Columns')
)

kolom_faktor_alam = ['weathersit', 'temp', 'atemp', 'hum', 'windspeed', 'cnt']
faktor_alam_df = day_df[kolom_faktor_alam]
correlation = faktor_alam_df.corr()

temp_df = day_df[['temp', 'cnt']]
temp_df['temp'] = temp_df['temp']*41

atemp_df = day_df[['atemp', 'cnt']]
atemp_df['atemp'] = atemp_df['atemp']*50

#Menampilkan Heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
ax.set_title('Heatmap of Correlation between Natural Factors and Number of Rentals')

st.pyplot(fig)

#Menampilkan scatterplot
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.regplot(
        x='temp', 
        y='cnt', 
        data=temp_df
    )
    plt.ylabel(
        'Total Rental (cnt)',
        fontsize=8
    )
    plt.xlabel(
        'Measured Temperature (temp)',
        fontsize=8
    )
    plt.title(
        'Number of Rentals (cnt) vs Temperature (temp)',
        loc='center',
        fontsize=15
    )
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.regplot(
        x='atemp', 
        y='cnt', 
        data=atemp_df
    )
    plt.ylabel(
        'Total Rental (cnt)',
        fontsize=8
    )
    plt.xlabel(
        'Feeling Temperature (atemp)',
        fontsize=8
    )
    plt.title(
        'Number of Rentals (cnt) vs Feeling Temperature (atemp)',
        loc='center',
        fontsize=15
    )
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    
    st.pyplot(fig)
#-----------------------------------------------------------------------
