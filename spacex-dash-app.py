
#%%
# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

import math

#%%

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()
# print(spacex_df)
# print("min: ", min_payload, " max: ", max_payload)
#%%

# Set marks for the slider (using the max and min payload range)

# Set marks for the slider (using fixed range range)
slider_min=0
slider_incr=1000
slider_max=math.ceil(max_payload/slider_incr)*slider_incr
slider_marks={i:str(i) for i in range(slider_min,slider_max+1,slider_incr)}
slider_marks

#%%
# Set dropdown_options
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': name, 'value': name} for name in spacex_df['Launch Site'].unique()]
# dropdown_options

#%%
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-family': 'Arial', 'font-size': 40}),
        dcc.Dropdown(
            options=dropdown_options,
            id='site-dropdown',
            value='ALL',
            placeholder='Select a Launch Site',
            style={'width': '80%', 
                   'padding': '3px', 
                   'font-family': 'Arial',
                   'font-size': 16}),
        html.Br(),
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(id='payload-slider',
                min=slider_min, max=slider_max, step=slider_incr,
                marks=slider_marks,
                value=[slider_min, slider_max]),
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# Pie plot, wired to drop down
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
                spacex_df, 
                values='class', 
                names='Launch Site', 
                labels='class',
                title='Successful Launches by Site'
              )
        return fig
    else:
        fig = px.pie(
                spacex_df[spacex_df['Launch Site']==entered_site], 
                names='class', 
                labels='class',
                title='Success Launch Rate for site: ' + entered_site
            )
        return fig


# Scatter plot, wired to slider
@app.callback(
            Output(component_id='success-payload-scatter-chart', component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), 
             Input(component_id="payload-slider", component_property="value")]
)
def get_scatter(entered_site,entered_payload):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.scatter(
                spacex_df[
                    (spacex_df['Payload Mass (kg)'] >= entered_payload[0]) &
                    (spacex_df['Payload Mass (kg)'] <= entered_payload[1])
                ], 
                x='Payload Mass (kg)',
                y='class',
                color='Booster Version Category',
                title='Correlation between Payload and Success for All Sites'
              )
        return fig
    else:
        fig = px.scatter(
                spacex_df[(
                    spacex_df['Launch Site']==entered_site) & 
                    (spacex_df['Payload Mass (kg)'] >= entered_payload[0]) &
                    (spacex_df['Payload Mass (kg)'] <= entered_payload[1])
                ], 
                x='Payload Mass (kg)',
                y='class',
                color='Booster Version Category',
                title='Correlation between Payload and Success for Site '+entered_site
              )        

        return fig

# Run the app
if __name__ == '__main__':
    app.run()

# %%
entered_site='ALL'
entered_payload=(0,10000)
get_scatter(entered_site,entered_payload)

'''(html)

<b>Which site has the largest successful launches?</b>

KSC-LC-39A (10)

<b>Which site has the highest launch success rate</b>

KSC-LC-39A (76.9%)


<b>Which payload range(s) has the highest launch success rate?</b>

3,000 - 4,000 (7 successes, 3 failures)
If one considers individual Launch Sites, then

KSCLC-39A has a 100% success rate for payloads 0 - 5,000
CCAFS SLC-40 has 100% for payloads 0 - 2,000 and 3,000 - 4,000

<b>Which payload range(s) has the lowest launch success rate?</b>

6,000 - 9,000 has a 0% success rate


<b>Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest
launch success rate?</b>

B5 has a 100% success rate (but only one launch)
'''