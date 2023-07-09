#importing the necessary libraries
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import datetime as dt
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from IPython.display import HTML

#reading the dataset and storing it as a dataframe
df = pd.read_csv('data.csv')

#changing column names so that they don't have white-spaces, numbers, or any special-characters
df.columns =['States','Date','Frequency','Estimated Unemployment Rate','Estimated Employed','Estimated Labour Participation Rate','Region','longitude','latitude']

#converting the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

#converting the 'Frequency' column to categorical data type
df['Frequency'] = df['Frequency'].astype('category')

#extracting the 'Month' from the Date
df['Month'] = df['Date'].dt.month

#creating a new column 'MonthNumber' by converting the 'Month' column values to integers
df['MonthNumber'] = df['Month'].apply(lambda x: int(x))

#creating a new column 'MonthName' by converting the 'MonthNumber' column values to the monthNames
df['MonthName'] = df['MonthNumber'].apply(lambda x: calendar.month_abbr[x])

#ensuring the categorical variable
df['Region'] = df['Region'].astype('category')

#dropping the Month column as it is irrelevant now
#we have extracted the monthNumbers and monthNames individually
df.drop(columns='Month', inplace=True)
df.head(3)

#5-number summary
st.write(df.describe())

#5-number summary of the numerical variables which give some information
st.write(round(df[['Estimated Unemployment Rate', 'Estimated Employed', 'Estimated Labour Participation Rate']].describe().T, 2))

#grouping by 'Region' and finding mean values for the numerical columns
regionStats = df.groupby(['Region'])[['Estimated Unemployment Rate', 'Estimated Employed', 'Estimated Labour Participation Rate']].mean().reset_index()

#rounding the values to 2 decimal points
st.write(round(regionStats, 2))

#constructing a 'heatMap' to find the 'pair-wise correlation' values

#dataframe of all the numerical columns
heatMap = df[['Estimated Unemployment Rate', 'Estimated Employed', 'Estimated Labour Participation Rate', 'longitude', 'latitude', 'MonthNumber']]

#constructing on heatMap with correlation values
heatMap = heatMap.corr()

#plotting the figure
plt.figure(figsize=(23,8))
sns.heatmap(heatMap, annot=True, cmap='twilight_shifted', fmt='.3f', linewidths=1)
plt.title('heatMap')
st.pyplot()

## EDA - Exploratory Data Analysis

#plotting a box-plot to show unemployment rate in each state
fig = px.box(
    df,
    x='States',
    y='Estimated Unemployment Rate',
    color='States',
    title='unemploymentRate',
    template='plotly'
)
st.plotly_chart(fig)

#creating a scatter matrix plot to denote relationship
fig = px.scatter_matrix(df,
    dimensions=['Estimated Unemployment Rate','Estimated Employed', 'Estimated Labour Participation Rate'],
    color='Region')
st.plotly_chart(fig)

#plotting a "Bar-plot" to find the "average unemployment rate in each state"
newDF = df[['Estimated Unemployment Rate','States']]

#grouping the dataframe by 'States' and finding the corresponding 'mean'
newDF = newDF.groupby('States').mean().reset_index()

#sorting the values in the dataframe
newDF = newDF.sort_values('Estimated Unemployment Rate')

fig = px.bar(newDF, 
             x='States',
             y='Estimated Unemployment Rate',
             color='States',
             title='State-wise Average Employment Rate')
st.plotly_chart(fig)

#plotting a "Bar-plot" to find the "unemployment rate" for each "Region" month-wise
fig = px.bar(df, 
             x='Region',
             y='Estimated Unemployment Rate',
             animation_frame='MonthName',
             color='States',
             title='Region-wise Unemployment Rate',
             height=800)

fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500

st.plotly_chart(fig)

#creating a new dataframe with 'State-wise' & 'Region-wise' Estimated Unemployment Rate
unempDF = df[['States','Region','Estimated Unemployment Rate','Estimated Employed','Estimated Labour Participation Rate']]

unempDF = unempDF.groupby(['Region','States'])['Estimated Unemployment Rate'].mean().reset_index()

#printing the new dataframe
st.write(unempDF.head(4))

#a sunburst chart (hierarchical chart) for unemployment rate region-wise and state-wise
fig = px.sunburst(unempDF, 
                  path=['Region','States'], 
                  values='Estimated Unemployment Rate',
                  title='unemployment rate in each region and state',
                  height=650)
st.plotly_chart(fig)

## Impact of Lockdown on States Estimated Employed

#creating a scatter geospatial plot
fig = px.scatter_geo(df,'longitude', 'latitude', 
                     color="Region",
                     hover_name="States", 
                     size="Estimated Unemployment Rate",
                     animation_frame="MonthName",
                     scope='asia',
                     title='Lockdown Impact throughout India')

fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1200

#updating the geospatial axes ranges and ocean color
fig.update_geos(lataxis_range=[5,35], 
                lonaxis_range=[65, 100],
                oceancolor="#6dd5ed",
                showocean=True)

st.plotly_chart(fig)

#filtering dataset between month 4 and 7 (inclusive) - after lockdown
df47 = df[(df['MonthNumber'] >= 4) & (df['MonthNumber'] <=7)]

#filtering dataset between month 1 and 4 (inclusive) - before lockdown
df14 = df[(df['MonthNumber'] >= 1) & (df['MonthNumber'] <=4)]

#grouping the dataframe on the basis of "States" and finding the corresponding mean values
df47g = df47.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()

#grouping the dataframe on the basis of "States" and finding the corresponding mean values
df14g = df14.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()

#clubbing the 2 dataframe values
df47g['Unemployment Rate before lockdown'] = df14g['Estimated Unemployment Rate']

#renaming the column values for better understanding
df47g.columns = ['States','unemploymentRate A/ lockdown','unemploymentRate B/ lockdown']

#displaying the top results
st.write(df47g.head())

#computing the % change in unemployment rate
df47g['% change in unemployment'] = round(df47g['unemploymentRate A/ lockdown'] - df47g['unemploymentRate B/ lockdown'] / df47g['unemploymentRate B/ lockdown'], 2)

#sorting the values in the "after lockdown dataframe" on the basis of "%change in unemployment"
df47g = df47g.sort_values('% change in unemployment')

#plotting a 'bar-chart' for the "%change in unemployment A/ lockdown"
fig = px.bar(df47g, x='States',y='% change in unemployment',
             color='% change in unemployment',
             title='% change in Unemployment A/ Lockdown')

st.plotly_chart(fig)

#defining a function to sort the values based on impact
#from the above 'box-plot', the values are ranging between 0 and 40
def sort_impact(x):
    if x <= 10:
        #impactedState
        return '🥲'
    elif x <= 20:
        #hardImpactedState
        return '🥲😥'
    elif x <= 30:
        #harderImpactedState
        return '🥲😥😖'
    elif x <= 40:
        #hardestImpactedState
        return '🥲😥😖🤯'
    return x    

#adding a new column to the 'dataframe', classifying the "%change in employment" on the basis of impactStatus
df47g['impactStatus'] = df47g['% change in unemployment'].apply(lambda x:sort_impact(x))

#plotting a "bar-graph" to classify and denote the impact of lockdown on employment for different states
fig = px.bar(df47g, 
             y='States',
             x='% change in unemployment',
             color='impactStatus',
             title='Lockdown Impact on Employment in India')

st.plotly_chart(fig)
