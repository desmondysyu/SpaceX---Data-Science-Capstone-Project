import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load data
data_url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(data_url)

# Create the Dash app
app = Dash(__name__)

# Dropdown options for launch sites
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),
    
    # Pie chart
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    
    html.P("Payload range (kg):"),
    
    # Payload mass slider
    dcc.RangeSlider(id='payload-slider',
                    min=spacex_df['Payload Mass (kg)'].min(),
                    max=spacex_df['Payload Mass (kg)'].max(),
                    step=1000,
                    marks={int(i): str(int(i)) for i in range(0, int(spacex_df['Payload Mass (kg)'].max())+1000, 2000)},
                    value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]),
    
    # Scatter plot
    dcc.Graph(id='success-payload-scatter-chart'),
])

# Callback for updating pie chart based on selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df,
                     names='Launch Site',
                     title='Total Success Launches by Site',
                     values='class')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().rename(index={0:'Failure',1:'Success'})
        fig = px.pie(names=success_counts.index, values=success_counts.values,
                     title=f'Success vs Failure for site {selected_site}')
    return fig

# Callback for updating scatter plot based on site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')])
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Payload vs Success for Launch Site(s)',
                     labels={'class':'Launch Outcome'})
    return fig

if __name__ == '__main__':
    app.run(debug=True)

