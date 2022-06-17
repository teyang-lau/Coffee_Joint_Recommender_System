# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# Use callbacks to filter sg_cities?
sg_cities = pd.read_csv("./data/processed/sg_coffee_shops_final.csv")

# https://plotly.com/python-api-reference/plotly.express.html
# https://plotly.com/python-api-reference/generated/plotly.express.scatter_mapbox.html#plotly.express.scatter_mapbox
fig = px.scatter_mapbox(sg_cities,
                        lat="latitude",
                        lon="longitude",
                        hover_name="name",
                        hover_data=["address", "price"],
                        color="rating",
                        size="review_count",
                        size_max=40,
                        center={"lat": 1.3521, "lon": 103.8198},
                        zoom=11,
                        height=900)

# ["open-street-map", "white-bg", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-watercolor", "stamen-toner",]
fig.update_layout(mapbox_style="carto-darkmatter",
                  margin={"r": 0, "t": 0, "l": 0, "b": 0})

app.layout = html.Div(children=[
    html.H1(children='Dash maps'),

    html.Div(children='''
        Recommended coffeeshops
    '''),

    dcc.Graph(
        id='map',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
