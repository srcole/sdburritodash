import pandas as pd
import geocoder
import numpy as np

# Get data from Google Sheet
url = 'https://docs.google.com/spreadsheet/ccc?key=18HkrklYz1bKpDLeL-kaMrGjAhUM6LeJMIACwEljCgaw&output=csv'
df = pd.read_csv(url)

# Make lower
df.Location = df.Location.str.lower().str.strip()
df.Reviewer = df.Reviewer.str.lower().str.strip()
df.Burrito = df.Burrito.str.lower().str.strip()

# Delete unreliable ratings
df = df[(df.Unreliable != 'x') & (df.Unreliable != 'X')]

# Delete ratings outside of San Diego
df = df[(df.NonSD != 'x') & (df.NonSD != 'X')]
df.reset_index(drop=True, inplace=True)

# Only keep columns of interest
cols_keep = ['Location', 'Burrito', 'Date', 'URL', 'Yelp', 'Google', 'Address', 'Neighborhood',
             'Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
             'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
             'Synergy', 'Wrap', 'overall', 'Reviewer']
df_burritos = df[cols_keep]

# Get average ratings for each restaurant
avg_cols = ['Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
            'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
            'Synergy', 'Wrap', 'overall']
df_rest_avg = df_burritos.groupby('Location').mean()[avg_cols].reset_index()

# Get address about each restaurant
add_cols = ['Address', 'Neighborhood']
df_rest_add = df_burritos.groupby('Location').first()[add_cols].reset_index()

# Get info about each restaurant
info_cols = ['URL', 'Yelp', 'Google']
df_rest_info = df_burritos.groupby('Location').first()[info_cols].reset_index()

# Get count of number of burritos rated
df_rest_count = pd.DataFrame(df_burritos.groupby('Location')['Burrito'].count()).reset_index().rename({'Burrito': 'N'}, axis=1)

# Optional future features:
# Get most popular burrito
# Get date most recently rated
# Get most favorable reviewer

# Get lat and long
addresses = df_rest_add['Address'] + ', ' + \
    df_rest_add['Neighborhood'] + ', San Diego, CA'
lats = np.zeros(len(addresses))
longs = np.zeros(len(addresses))
for i, address in enumerate(addresses):
    g = geocoder.google(address)
    Ntries = 1
    while g.latlng == []:
        if 'Marshall College' in address:
            address = '9500 Gilman Drive, La Jolla, CA'
        g = geocoder.google(address)
        print(str(i) + '/' + str(len(lats)) + ' Attempt: ' + str(Ntries) + ' Address:' + address)
        Ntries += 1
             
    lats[i], longs[i] = g.latlng

# # Check for nonsense lats and longs
# if sum(np.logical_or(lats > 34, lats < 32)):
#     raise ValueError('Address not in san diego')
# if sum(np.logical_or(longs < -118, longs > -117)):
#     raise ValueError('Address not in san diego')

# Incorporate lats and longs into restaurants data
df_rest_add['Latitude'] = lats
df_rest_add['Longitude'] = longs

# Merge restaurant df
df_rest = df_rest_avg.merge(df_rest_info, on='Location').merge(df_rest_count, on='Location').merge(df_rest_add[['Location','Latitude','Longitude']], on='Location')
df_rest.to_csv('burrito_data_shops.csv')
