#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import random
import os


# In[2]:


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Coordinates for the cities
city_coords = {
    "San Carlos, CA": {"lat": 37.5072, "lon": -122.2621},
    "Madison, WI": {"lat": 43.0731, "lon": -89.4012}
}

# Scores for restaurants and entertainment
scores = {
    "San Carlos, CA": {
        "restaurants": {"Town": 80, "Refuge": 70, "Johnston's Saltbox": 90},
        "entertainment": {"Alcatraz": 85, "Golden Gate Bridge": 95, "Devil's Canyon Brewing Company": 60}
    },
    "Madison, WI": {
        "restaurants": {"Ahan": 75, "Nattspil": 85, "Estacion Inka": 65},
        "entertainment": {"James Madison Park": 70, "The Cardinal": 80, "Memorial Union": 90}
    }
}


# In[3]:


# Helper function to generate the city map
def generate_map(city):
    coords = city_coords[city]
    fig = px.scatter_mapbox(
        lat=[coords["lat"]],
        lon=[coords["lon"]],
        zoom=12,
        height=400
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Helper function to generate the Cool-o-Meter gauge
def generate_gauge(score):
    fig = px.bar_polar(
        r=[score], theta=["Cool-o-Meter"],
        range_r=[0, 100],
        height=400, width=400,
        template="plotly_dark"
    )
    fig.update_traces(marker_color="cyan", marker_line_color="white", marker_line_width=2)
    return fig


# In[4]:


# App layout
app.layout = dbc.Container([
    dcc.Store(id='current-step', data=1),  # Track the current step
    dcc.Store(id='selected-city'),  # Store the selected city
    dcc.Store(id='selected-restaurant'),  # Store the selected restaurant
    dcc.Store(id='selected-entertainment'),  # Store the selected entertainment

    # Step 1: City Selection
    html.Div(id='step-1', children=[
        html.H1("Choose Your City", style={'text-align': 'center'}),
        html.Div([
            dbc.Button(
                "San Carlos, CA", id='city-san-carlos', 
                color="primary", style={
                    'width': '300px', 'height': '120px', 
                    'margin': '10px', 'font-size': '24px', 'font-weight': 'bold',
                    'background-color': 'blue', 'color': 'white'
                }
            ),
            dbc.Button(
                "Madison, WI", id='city-madison', 
                color="danger", style={
                    'width': '300px', 'height': '120px', 
                    'margin': '10px', 'font-size': '24px', 'font-weight': 'bold',
                    'background-color': 'red', 'color': 'white'
                }
            )
        ], style={'text-align': 'center'}),
    ], style={'display': 'block'}),

# Step 2: Map Screen
    html.Div(id='step-2', children=[
        html.H1(id='selected-city-title', style={'text-align': 'center'}),  # Added this line
        dcc.Graph(id='city-map'),
        dbc.Button("Continue Adventure", id='next-2', n_clicks=0, color="primary", style={'margin-top': '20px'})
    ], style={'display': 'none'}),


    # Step 3: Choose a Restaurant
    html.Div(id='step-3', children=[
        html.H1("Choose Your Restaurant", style={'text-align': 'center'}),
        html.Div(id='restaurant-options', style={'text-align': 'center'}),
    ], style={'display': 'none'}),

    # Step 4: Choose Entertainment
    html.Div(id='step-4', children=[
        html.H1("Choose Your Entertainment", style={'text-align': 'center'}),
        html.Div(id='entertainment-options', style={'text-align': 'center'}),
    ], style={'display': 'none'}),

    # Step 5: Adventure Poem
    html.Div(id='step-5', children=[
        html.H1("Your Adventure Poem", style={'text-align': 'center'}),
        html.Div(id='adventure-poem', style={'text-align': 'center', 'font-size': '20px', 'margin-top': '20px'})
    ], style={'display': 'none'})
])


# In[5]:


@app.callback(
    [
        Output('current-step', 'data'),
        Output('selected-city', 'data'),
        Output('selected-restaurant', 'data'),
        Output('selected-entertainment', 'data')
    ],
    [
        Input('city-san-carlos', 'n_clicks'),
        Input('city-madison', 'n_clicks'),
        Input('next-2', 'n_clicks'),
        Input({'type': 'restaurant', 'index': ALL}, 'n_clicks'),
        Input({'type': 'entertainment', 'index': ALL}, 'n_clicks')
    ],
    [
        State('current-step', 'data'),
        State('selected-city', 'data'),
        State('selected-restaurant', 'data')
    ]
)
def update_step_and_selection(san_carlos_clicks, madison_clicks, next_2_clicks, restaurant_clicks, entertainment_clicks, current_step, city, restaurant):
    # Step 1 -> Step 2: City selected
    if current_step == 1:
        if san_carlos_clicks:
            return 2, "San Carlos, CA", dash.no_update, dash.no_update
        elif madison_clicks:
            return 2, "Madison, WI", dash.no_update, dash.no_update

    # Step 2 -> Step 3: "Continue Adventure" button clicked
    elif current_step == 2 and next_2_clicks:
        return 3, city, dash.no_update, dash.no_update

    # Step 3 -> Step 4: Restaurant selected
    elif current_step == 3 and any(restaurant_clicks):
        selected_index = restaurant_clicks.index(1)
        selected_restaurant = list(scores[city]['restaurants'].keys())[selected_index]
        return 4, city, selected_restaurant, dash.no_update

    # Step 4 -> Step 5: Entertainment selected
    elif current_step == 4 and any(entertainment_clicks):
        selected_index = entertainment_clicks.index(1)
        selected_entertainment = list(scores[city]['entertainment'].keys())[selected_index]
        return 5, city, restaurant, selected_entertainment

    return current_step, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output('adventure-poem', 'children'),
    [Input('selected-city', 'data'), Input('selected-restaurant', 'data'), Input('selected-entertainment', 'data')]
)
def generate_adventure_poem(city, restaurant, entertainment):
    if city and restaurant and entertainment:
        # Define multiple Tanka-style poem templates
        poems = [
            f"""
            {city} streets, bright lights,
            Food at {restaurant} was hot,
            Not as hot as you,
            Sit on my face tonight,
            Ended up at {entertainment}, damn.
            """,
            f"""
            Met up in {city},
            {restaurant} filled us up,
            But I want more—
            You're smoking hot,
            {entertainment} couldn't cool you down.
            """,
            f"""
            In {city}, we started,
            Sexy motherfucker, you,
            Ate at {restaurant},
            You're delicious—
            Ended up fucking at {entertainment}.
            """,
            f"""
            {city} started classy,
            {restaurant} was fun—
            But let’s be real,
            I’d rather taste you—
            I did right there at {entertainment}.
            """,
            f"""
            {city} was cute,
            But not as cute as you bent over at {restaurant}—
            We smashed at {entertainment},
            Damn girl, you bad.
            """,
            f"""
            {city}, you and me,
            {restaurant} had a vibe,
            Your eyes screamed "take me",
            {entertainment} just witnessed it all.
            """,
            f"""
            {city} was cool,
            {restaurant} was just to kill time,
            Then {entertainment} hit, and so did we.
            """,
            f"""
            Linked in {city},
            Dined at {restaurant},
            Vibed at {entertainment},
            Tryna fuck?
            """
        ]

        # Select a random poem template
        poem = random.choice(poems)

        return html.P(poem, style={'white-space': 'pre-wrap'})

    return ""

# Step 2: Update title and map for selected city
@app.callback(
    [Output('selected-city-title', 'children'), Output('city-map', 'figure')],
    Input('selected-city', 'data')
)
def update_title_and_map(city):
    if city:
        return f"Isabelle's Selected City: {city}", generate_map(city)
    return "", {}

# Update restaurant options when city is selected
@app.callback(
    Output('restaurant-options', 'children'),
    Input('selected-city', 'data')
)
def update_restaurant_options(city):
    if city:
        restaurants = scores[city]['restaurants']
        button_colors = ["primary", "success", "warning"]

        return [
            dbc.Button(
                name,
                id={'type': 'restaurant', 'index': name},
                n_clicks=0,
                color=button_colors[i % len(button_colors)],
                style={
                    'width': '300px', 'height': '120px',
                    'margin': '10px', 'font-size': '24px', 'font-weight': 'bold'
                }
            ) for i, name in enumerate(restaurants)
        ]
    return []

# Update entertainment options when city is selected
@app.callback(
    Output('entertainment-options', 'children'),
    Input('selected-city', 'data')
)
def update_entertainment_options(city):
    if city:
        entertainment = scores[city]['entertainment']
        button_colors = ["info", "danger", "secondary"]

        return [
            dbc.Button(
                name,
                id={'type': 'entertainment', 'index': name},
                n_clicks=0,
                color=button_colors[i % len(button_colors)],
                style={
                    'width': '300px', 'height': '120px',
                    'margin': '10px', 'font-size': '24px', 'font-weight': 'bold'
                }
            ) for i, name in enumerate(entertainment)
        ]
    return []

# Manage which step is visible
@app.callback(
    [Output(f'step-{i}', 'style') for i in range(1, 6)],
    Input('current-step', 'data')
)
def update_step_visibility(step):
    return [{'display': 'block' if i == step else 'none'} for i in range(1, 6)]

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=True)

