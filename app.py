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

# Load data
df = pd.read_csv('burrito_data_shops.csv', index_col=0)
feature_list = ['Cost', 'Volume', 'Tortilla', 'Temp', 'Meat',
                'Fillings', 'Meat:filling', 'Uniformity', 'Salsa',
                'Synergy', 'Wrap', 'overall']

app.layout = html.Div([html.H4(children='San Diego Burrito Dashboard'),
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='feature_rank',
                options=[{'label': i, 'value': i} for i in feature_list],
                value='overall'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div(['FILLER'
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='bar_rank')
])

# figure={
#             'data': [
#                 {'x': [1, 2, 3], 'y': [4, 1, 4],
#                 'type': 'bar', 'name': 'SF'},
#                 {'x': [1, 2, 3], 'y': [3, 5, 2],
#                 'type': 'bar', 'name': u'Montréal'},
#             ],
#             'layout': {
#                 'title': 'My stupid bar chart',
#                 'plot_bgcolor': colors['background'],
#                 'paper_bgcolor': colors['background'],
#                 'font': {
#                     'color': colors['text']
#                 }
#             }
#         }

@app.callback(
    dash.dependencies.Output('bar_rank', 'figure'),
    [dash.dependencies.Input('feature_rank', 'value')])
def update_graph(feature_name):
    # Get the top 10 restaurants
    dff = df.sort_values(by=feature_name, ascending=False).reset_index()[['Location', feature_name]]
    dff = dff.loc[:5]

    return {
        'data': [{'x': dff['Location'], 'y': dff[feature_name], 'type': 'bar'}],
        'layout': go.Layout(
            xaxis={'title': 'Taco Shop'},
            yaxis={'title': 'Average ' + feature_name},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True)
