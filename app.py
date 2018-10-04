# Import required libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# Initialize app with desired style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'San Diego Burrito Dashboard'

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
        html.H4('San Diego Burrito Dashboard',
                style={'width': '40%', 'display': 'inline-block'}),

        html.H6(html.A('See raw data', href='https://docs.google.com/spreadsheets/d/18HkrklYz1bKpDLeL-kaMrGjAhUM6LeJMIACwEljCgaw/edit?usp=sharing'),
                style={'width': '50%', 'float': 'right', 'display': 'inline-block'})
    
    ]),
    
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='feature_rank',
                options=[{'label': i, 'value': i} for i in feature_list],
                value='overall'
            )
        ],
        style={'width': '20%', 'display': 'inline-block'}),

        html.Div(['Choose a burrito feature and see the top taco shops!'],
                 style={'width': '76%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='bar_rank',
                  style={'width': '48%', 'display': 'inline-block'}),

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
            style={'width': '48%', 'float': 'right',
                   'display': 'inline-block'}),

    ])
])

@app.callback(
    dash.dependencies.Output('bar_rank', 'figure'),
    [dash.dependencies.Input('bar_rank', 'clickData'),
     dash.dependencies.Input('feature_rank', 'value')])
def update_graph(clickData, feature_name):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['y']

    # Get the top 10 restaurants
    dff = df.sort_values(by=feature_name).reset_index()[['Location', feature_name]]
    dff = dff.loc[len(dff)-20:]

    return {
        'data': [{'x': dff[feature_name],
                  'y': dff['Location'],
                  'type': 'bar',
                  'orientation': 'h',
                  'selectedpoints': [list(dff['Location']).index(rest_chose)]}],
        'layout': go.Layout(
            yaxis={'title': ''},
            xaxis={'title': 'Average ' + feature_name + ' rating'},
            margin={'l': 200, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            height=600
        )
    }

@app.callback(
    dash.dependencies.Output('bar_features', 'figure'),
    [dash.dependencies.Input('bar_rank', 'clickData'),
     dash.dependencies.Input('feature_rank', 'value')])
def make_bar_features(clickData, feature_selected):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['y']

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
                  'selectedpoints': [list(feature_dict.keys()).index(feature_selected)]}],
        'layout': go.Layout(
            yaxis={'title': ''},
            xaxis={'title': 'Average rating',
                   'titlefont': {'size': 24},
                   'tickfont': {'size': 16},
                   'range': [0, 5]},
            margin={'l': 100, 'b': 40, 't': 50, 'r': 20},
            hovermode='closest',
            height=300,
            annotations=[{
                'x': .5, 'y': 1, 'xanchor': 'center', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': '<a href="' + rest_url + '">' + rest_chose + '</a>',
                'font': {'size': 24}},
                {
                'x': 1, 'y': 1, 'xanchor': 'right', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': '# burritos: {:d}'.format(N_burritos),
                'font': {'size': 14}}]
        )
    }

@app.callback(
    dash.dependencies.Output('scatter_features', 'figure'),
    [dash.dependencies.Input('bar_rank', 'clickData'),
     dash.dependencies.Input('feature_scatterx', 'value'),
     dash.dependencies.Input('feature_scattery', 'value')])
def make_scatter(clickData, featx, featy):
    # Determine restaurant selected
    # Set default for chosen restaurant
    if clickData is None:
        rest_chose = 'taco stand'
    else:
        rest_chose = clickData['points'][0]['y']

    # Get features for restaurant of interest
    df_rest = df.loc[df['Location'] == rest_chose]
    feature_dict = df_rest[feature_plt_list].to_dict(orient='records')[0]

    return {
        'data': [go.Scatter(
            x=df[featx],
            y=df[featy],
            text=['{:s}<br>${:.2f}'.format(loc, price) for loc, price in zip(df['Location'], df[featx])],
            mode='markers',
            selectedpoints=[df_rest.index[0]])],

        'layout': go.Layout(
            yaxis={'title': featy},
            xaxis={'title': featx},
            margin={'l': 100, 'b': 40, 't': 50, 'r': 20},
            hovermode='closest',
            height=300,
            width=350
        )
    }

# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True)
