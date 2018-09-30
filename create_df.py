import pandas as pd

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
cols_keep = ['Location', 'Burrito', 'Date', 'URL', 'Yelp', 'Google',
             'Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
             'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
             'Synergy', 'Wrap', 'overall', 'Reviewer']
df_burritos = df[cols_keep]

# Make the restaurants df

# Get average ratings for each restaurant
avg_cols = ['Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
            'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
            'Synergy', 'Wrap', 'overall']
df_rest_avg = df_burritos.groupby('Location').mean()[avg_cols].reset_index()

# Get info about each restaurant
info_cols = ['URL', 'Yelp', 'Google']
df_rest_info = df_burritos.groupby('Location').first()[info_cols].reset_index()

# Get count of number of burritos rated
df_rest_count = pd.DataFrame(df_burritos.groupby('Location')['Burrito'].count()).reset_index().rename({'Burrito': 'N'}, axis=1)

# Optional future features:
# Get most popular burrito
# Get date most recently rated
# Get most favorable reviewer

# Merge restaurant df
df_rest = df_rest_avg.merge(df_rest_info, on='Location').merge(df_rest_count, on='Location')
df_rest.to_csv('burrito_data_shops.csv')
