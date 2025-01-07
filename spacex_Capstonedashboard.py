# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('🚀 SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # Dropdown list for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',
                 placeholder='🌍 Select a Launch Site',
                 style={'font-size': '18px', 'width': '80%', 'margin': 'auto'},
                 searchable=True),
    html.Br(),

    # Pie chart for total successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Select Payload Range (Kg):", style={'font-size': '16px', 'textAlign': 'center'}),

    # Slider for payload range selection
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=500,
                    value=[min_payload, max_payload],
                    marks={0: '0', 2500: '2.5K', 5000: '5K', 7500: '7.5K', 10000: '10K'},
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Br(),

    # Scatter chart for payload and success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating the pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        df = spacex_df[spacex_df["class"] == 1]
        title = "🌍 Total Successful Launches by All Sites"
        names = "Launch Site"
    else:
        df = spacex_df.loc[spacex_df["Launch Site"] == entered_site]
        title = f"🚀 Success vs Failure for {entered_site}"
        names = "class"

    fig = px.pie(df, names=names, title=title, color_discrete_sequence=px.colors.sequential.RdBu)
    return fig

# Callback for updating the scatter chart
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload):
    min_payload, max_payload = payload
    if entered_site == 'ALL':
        df = spacex_df
    else:
        df = spacex_df.loc[spacex_df['Launch Site'] == entered_site]

    filtered_df = df[(df["Payload Mass (kg)"] >= min_payload) & (df["Payload Mass (kg)"] <= max_payload)]
    
    fig = px.scatter(
        filtered_df, x="Payload Mass (kg)", y="class",
        color="Booster Version",
        size="Payload Mass (kg)",
        hover_data=["Launch Site", "Payload Mass (kg)", "Booster Version"],
        title="📊 Payload vs. Launch Success Correlation",
        labels={"class": "Launch Outcome"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

