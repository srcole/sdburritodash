# Import required libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# Initialize app with desired style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'San Diego Burrito Dashboard'

mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'

# Load data
df = pd.read_csv('burrito_data_shops.csv', index_col=0)
feature_list = ['Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
                'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
                'Synergy', 'Wrap', 'overall']
feature_plt_list = ['Tortilla', 'Temp', 'Meat', 'Fillings',
                    'Meat:filling', 'Uniformity', 'Salsa',
                    'Synergy', 'Wrap', 'overall']

# Make app layour
app.layout = html.Div([
    html.Div([

        html.Div(['Burrito feature:'],
                 style={'width': '12%', 'display': 'inline-block', 'fontSize': 24}),

        html.Div([dcc.Dropdown(
                id='feature_rank',
                options=[{'label': i, 'value': i} for i in feature_list],
                value='overall')],
            style={'width': '10%', 'display': 'inline-block'}),

        html.Div([''],
            style={'width': '5%', 'display': 'inline-block'}),


        html.H1('San Diego Burrito Dashboard',
                style={'width': '50%', 'display': 'inline-block'}),

        html.Div(html.A('See raw data', href='https://docs.google.com/spreadsheets/d/18HkrklYz1bKpDLeL-kaMrGjAhUM6LeJMIACwEljCgaw/edit?usp=sharing'),
                style={'width': '15%', 'float': 'right', 'display': 'inline-block', 'fontSize': 24})
    
    ]),

    html.Div([
        dcc.Graph(id='burrito_map',
                  style={'width': '32%', 'display': 'inline-block'}),

        dcc.Graph(id='bar_rank',
                  style={'width': '36%', 'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.Div([
                    'Select features to compare'],
                    style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Dropdown(
                    id='feature_scatterx',
                    options=[{'label': i, 'value': i} for i in feature_list],
                    value='Cost')],
                    style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Dropdown(
                    id='feature_scattery',
                    options=[{'label': i, 'value': i} for i in feature_list],
                    value='overall')],
                    style={'width': '30%', 'display': 'inline-block'})
                ]),
            dcc.Graph(id='scatter_features'),
            dcc.Graph(id='bar_features')],
            style={'width': '28%', 'float': 'right',
                   'display': 'inline-block'}),

    ])
])

@app.callback(
    dash.dependencies.Output('burrito_map', 'figure'),
    [dash.dependencies.Input('burrito_map', 'clickData'),
     dash.dependencies.Input('feature_rank', 'value')])
def update_map(clickData, feature_name):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['id']

    norm_feature = np.exp(df[feature_name])
    norm_feature = norm_feature - np.min(norm_feature)
    norm_feature = 6 + 10*(norm_feature / np.max(norm_feature))

    return {'data': [go.Scattermapbox(
                        lat=df['Latitude'],
                        lon=df['Longitude'],
                        ids=df['Location'],
                        mode='markers',
                        marker={'size': norm_feature},
                        hoverinfo='text',
                        selectedpoints=[list(df['Location']).index(rest_chose)],
                        unselected={'marker': {'color': 'black'}},
                        text=['{:s}<br>Average {:s} rating: {:.2f}'.format(loca, feature_name, n) for loca, n in zip(df['Location'], df[feature_name])],
                        )],

            'layout': go.Layout(
                        autosize=True,
                        hovermode='closest',
                        margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
                        height=700,
                        mapbox=dict(
                            accesstoken=mapbox_access_token,
                            bearing=0,
                            center=dict(
                                lat=32.96,
                                lon=-117.2
                            ),
                            pitch=0,
                            zoom=9.4
                        ),
            )}

@app.callback(
    dash.dependencies.Output('bar_rank', 'figure'),
    [dash.dependencies.Input('burrito_map', 'clickData'),
     dash.dependencies.Input('feature_rank', 'value')])
def update_bar_rank(clickData, feature_name):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['id']

    # Get the top 10 restaurants
    dff = df.sort_values(by=feature_name).reset_index()[['Location', feature_name]]

    return {
        'data': [{'x': dff[feature_name],
                  'y': dff['Location'],
                  'type': 'bar',
                  'orientation': 'h',
                  'hoverinfo': 'text',
                  'text': ['{:s}: {:.2f} average {:s} rating'.format(loca, n, feature_name) for loca, n in zip(dff['Location'], dff[feature_name])],
                  'unselected': {'marker': {'opacity': 0.5, 'color': 'black'}},
                  'selectedpoints': [list(dff['Location']).index(rest_chose)]}],
        'layout': go.Layout(
            yaxis={'title': ''},
            xaxis={'title': 'Average ' + feature_name + ' rating'},
            margin={'l': 200, 'b': 40, 't': 30, 'r': 0},
            hovermode='closest',
            height=700
        )
    }

@app.callback(
    dash.dependencies.Output('bar_features', 'figure'),
    [dash.dependencies.Input('burrito_map', 'clickData'),
     dash.dependencies.Input('feature_rank', 'value')])
def make_bar_features(clickData, feature_selected):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['id']

    # Get features for restaurant of interest
    df_rest = df.loc[df['Location'] == rest_chose]
    N_burritos = df_rest['N'].values[0]
    rest_url = df_rest['URL'].values[0]
    feature_dict = df_rest[feature_plt_list].to_dict(orient='records')[0]

    return {
        'data': [{'x': list(feature_dict.values()),
                  'y': list(feature_dict.keys()),
                  'title': rest_chose,
                  'type': 'bar',
                  'orientation': 'h',
                  'hoverinfo': 'text',
                  'text': ['Average {:s} rating: {:.2f}'.format(s, n) for s, n in zip(feature_dict.keys(), feature_dict.values())],
                  'unselected': {'marker': {'opacity': 0.5, 'color': 'black'}},
                  'selectedpoints': [list(feature_dict.keys()).index(feature_selected)]}],
        'layout': go.Layout(
            yaxis={'title': ''},
            xaxis={'title': 'Average rating',
                   'titlefont': {'size': 24},
                   'tickfont': {'size': 16},
                   'range': [0, 5]},
            margin={'l': 90, 'b': 60, 't': 40, 'r': 20},
            hovermode='closest',
            height=300,
            annotations=[{
                'x': .5, 'y': 1, 'xanchor': 'center', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': '<a href="' + rest_url + '">' + rest_chose + '</a>',
                'font': {'size': 24}},
                {
                'x': 1, 'y': -.2, 'xanchor': 'right', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': '# burritos: {:d}'.format(N_burritos),
                'font': {'size': 14}}]
        )
    }

@app.callback(
    dash.dependencies.Output('scatter_features', 'figure'),
    [dash.dependencies.Input('burrito_map', 'clickData'),
     dash.dependencies.Input('feature_scatterx', 'value'),
     dash.dependencies.Input('feature_scattery', 'value')])
def make_scatter(clickData, featx, featy):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['id']

    # Get features for restaurant of interest
    df_rest = df.loc[df['Location'] == rest_chose]
    feature_dict = df_rest[feature_plt_list].to_dict(orient='records')[0]

    return {
        'data': [go.Scatter(
            x=df[featx],
            y=df[featy],
            hoverinfo='text',
            text=['{:s}<br>${:.2f}'.format(loc, price) for loc, price in zip(df['Location'], df[featx])],
            mode='markers',
            marker={'size': 6 + 5 * np.log10(df['N'])},
            unselected={'marker': {'opacity': 0.5, 'color': 'black'}},
            selectedpoints=[df_rest.index[0]])],

        'layout': go.Layout(
            yaxis={'title': featy},
            xaxis={'title': featx},
            margin={'l': 50, 'b': 40, 't': 20, 'r': 20},
            hovermode='closest',
            height=300,
            width=350
        )
    }

# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True)
