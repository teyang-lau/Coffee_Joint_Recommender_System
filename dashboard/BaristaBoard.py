from faulthandler import disable
from shutil import unregister_archive_format
import dash
from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px

import matplotlib.pyplot as plt
from wordcloud import WordCloud

import pandas as pd
import numpy as np
import time

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

##################################################################################################
# ETL 
##################################################################################################

with open('./data/recommendations/MostPop_lol.txt_recommendations.txt', encoding="utf-8") as f:
    most_pop = f.readlines()[0].split()

# shop information
shop_info = pd.read_csv("./data/shop/sg_coffee_shops_final.csv")

# customer recommendation
recc_mf = pd.read_csv("./data/recommendations/mf_tgs_recs.csv")
recc_fm = pd.read_csv("./data/recommendations/lightFM_LOL_recommendations_improved_features.csv")
recc_fm_expln = pd.read_csv("./data/recommendations/lightFM_LOL_explanations_improved_features.csv")

# function to filter out user's recommendation
def get_recommendationdata(df, userid, user_col, drop_index, mode = 'mf'):
    if mode == "mf":
        if drop_index:
            df = df.drop("Unnamed: 0", axis = 1)
        output = df.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
        return output
    else:
        output = df.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
        return output

# function to filter out user's explanation for FM model
def get_recommendationdata_explain(df, userid, user_col):
    output = df.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
    return output

# function to filter out user's recommendation
def get_recommendationdata_price(df, userid, user_col, drop_index, mode = None, price = "$"):
    if mode is None:
        if drop_index:
            df = df.drop("Unnamed: 0", axis = 1)
        output = df.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
        final_output = []
        for shop in output:
            if str(shop_info.loc[shop_info["alias"] == shop, "price"].values[0]) == price:
                final_output.append(shop)
        return final_output
    else:
        output = df.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
        output_expln = mode.loc[df[user_col] == userid, [col for col in df.columns if col != user_col]].values[0]
        final_output = []
        final_output_expln = []
        for shop_no in range(len(output)):
            if str(shop_info.loc[shop_info["alias"] == output[shop_no], "price"].values[0]) == price:
                final_output.append(output[shop_no])
                final_output_expln.append(output_expln[shop_no])
        return [final_output, final_output_expln]

##################################################################################################
# map components
##################################################################################################

# https://plotly.com/python-api-reference/plotly.express.html
# https://plotly.com/python-api-reference/generated/plotly.express.scatter_mapbox.html#plotly.express.scatter_mapbox
fig = px.scatter_mapbox(shop_info,
                        lat="latitude",
                        lon="longitude",
                        hover_name="name",
                        hover_data=["address", "price"],
                        color="rating",
                        size="review_count",
                        size_max=40,
                        center={"lat": 1.3521, "lon": 103.8198},
                        zoom=11,
                        height=500)

# ["open-street-map", "white-bg", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-watercolor", "stamen-toner",]
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

##################################################################################################
# carousel components
##################################################################################################

# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/carousel/
most_pop_list = [
    {
        "key": shop,
        "src": shop_info.loc[shop_info["alias"] == shop, "image_url"].values[0],
        "img_style":{"max-height": "400px", "width": "auto", "object-fit": "cover"},
        "header": shop_info.loc[shop_info["alias"] == shop, "name"].values[0],
        "caption": " | ".join([
            str(shop_info.loc[shop_info["alias"] == shop, "address"].values[0]),
            str(shop_info.loc[shop_info["alias"] == shop, "rating"].values[0]) + "☆",
            str(shop_info.loc[shop_info["alias"] == shop, "price"].values[0]),
        ]),
    }
    for shop in most_pop
]

##################################################################################################
# navbar component
##################################################################################################

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.Button("Open Offcanvas", id="user_id_offcanvas", n_clicks=0)),
        # dbc.DropdownMenu(
        #     children=[
        #         dbc.DropdownMenuItem("More pages", header=True),
        #         dbc.DropdownMenuItem("New User", href="#"),
        #     ],
        #     nav=True,
        #     in_navbar=True,
        #     label="More",
        # ),
    ],
    brand="BaristaBoard",
    brand_href="#",
    color="primary",
    dark=True,
    fixed="top",
)

##################################################################################################
# cards
##################################################################################################

cards = html.Div([
    dbc.Row(id = "cards_component", justify = "around")
])

cards_fm = html.Div([
    dbc.Row(id = "cards_fm_component", justify = "around")
])

##################################################################################################
# wordcloud
##################################################################################################

def export_wordcloud(userid):
    all_reviews = pd.read_csv("./data/reviews/all_reviews.csv")
    text = " ".join(all_reviews.loc[all_reviews["userid"] == userid, "text"].values)
    wordcloud = WordCloud(collocations = False, background_color = 'white').generate(text)
    wordcloud.to_file("./assets/wordcloud_temp.png")

##################################################################################################
# entry page layout
##################################################################################################

entry_page_layout = html.Div(
    dbc.Container(
        [
            html.H1("BaristaBoard", className="display-3", style={'color': 'white'}),
            html.P(
                "Where we get to know you, and you get to know more coffee",
                className="lead",
                style={'color': 'white'}
            ),
            html.Hr(className="my-2", style={'color': 'white'}),
            html.P(
                "Please provide your user id to continue.",
                style={'color': 'white'} 
            ),
            dbc.Row([
                dbc.Col(
                    html.P(
                        dbc.Input(
                            placeholder="User ID...", 
                            # valid=True,
                            id = "userid_input", 
                            className = "mb-3",
                            size = "sm",
                            style={"height": 37}
                            ), 
                        className="lead"
                    ), width = 4
                ),
                dbc.Col(
                    html.P(
                        dbc.Button("Enter", color="secondary", id="enter_button", disabled=True)
                    ), width = 1, style={"width":90, "margin-right":0}
                ),
                dbc.Col(
                    html.P(
                        dbc.Button("Create User", color="secondary", id="create_user_button", disabled=True)
                    ), width = 2
                ), 
                dbc.Row(id="cards_component"), dbc.Row(id="cards_fm_component"), dbc.Row(id="user_id_offcanvas")]
            ),
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-transparent rounded-3",
    id = "entry_page_layout"
)

def check_user(userid):
    if userid in recc_mf["userid"].values:
        return True
    return False

# entry page callback
@app.callback(
    [
        Output("userid_input", "valid"), 
        Output("userid_input", "invalid"),
        Output("enter_button", "disabled"),
        Output("create_user_button", "disabled"),
    ], [
        Input("userid_input", "value")
    ],
    prevent_initial_call = True
)
def output_entrypoint(value):
    if value == "":
        return False, False, True, True
    try:
        if check_user(value):
            return True, False, False, True
        return False, True, True, False
    except:
        return False, True, True, False

##################################################################################################
# main page layout
##################################################################################################

main_page_layout = html.Div(
    [
        dbc.Container([
            dbc.Row(navbar),
            dbc.Row([
                dbc.Col(html.H4("Welcome to your personalized recommendations!", className="display-10", style={'color': 'black', 'margin-top': 90}), width = 10),
                dbc.Col(dbc.ButtonGroup(
                    [dbc.Button("$", outline=True, color="primary", id ="button_price_1"), 
                    dbc.Button("$$", outline=True, color="primary", id ="button_price_2"), 
                    dbc.Button("$$$", outline=True, color="primary", id ="button_price_3"), 
                    dbc.Button("$$$$", outline=True, color="primary", id ="button_price_4"), 
                    dbc.Button("Any", outline=True, color="primary", id ="button_price_any")],
                    size="sm",
                ), align="end", width = 2)
            ], style = {"margin-bottom":5}),
            dbc.Row(
                dbc.Col(
                    dbc.Carousel(
                        items=most_pop_list[:10],
                        controls=True,
                        indicators=True,
                        interval=3000,
                        ride="carousel",
                        id="carousel_component"
                    ),
                )
            ),
            dbc.Row(html.H4("Recommendation from MF Model:", className="display-10", style={"margin-top":25, "margin-bottom":10})),
            cards,
            dbc.Row(html.H4("Recommendation from LightFM Model:", className="display-10", style={"margin-top":5, "margin-bottom":10})),
            cards_fm,
            dbc.Row(
                dcc.Graph(
                    id='map', 
                    figure=fig,
            )
            ),
            dbc.Offcanvas(
                html.P(
                    "This is the content of the Offcanvas. "
                    "Close it by clicking on the close button, or "
                    "the backdrop."
                ),
                id="offcanvas",
                title="User's Review WordCloud",
                is_open=False,
            ),
        ])
    ]
)

main_page_style = {
}

# main page navigation bar offcanvas
@app.callback(
    Output("offcanvas", "is_open"),
    Input("user_id_offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
    prevent_initial_call = True
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# main page card component callback
@app.callback(
    [
        Output("cards_component", "children"),
    ], [
        Input("main_page_container", "children"),
        Input("button_price_1", "n_clicks"),
        Input("button_price_2", "n_clicks"),
        Input("button_price_3", "n_clicks"),
        Input("button_price_4", "n_clicks"),
        Input("button_price_any", "n_clicks")
    ], [
        State("user_id_offcanvas", "children")
    ],
    prevent_initial_call = True
)
def output_changecards(child, button1, button2, button3, button4, button5, userid):
    button_clicked = dash.callback_context.triggered[0]['prop_id']
    if (button_clicked == "main_page_container.children") or (button_clicked == "button_price_any.n_clicks"):
        user_recommendation = get_recommendationdata(recc_mf, userid, "userid", True)[:4]
    else:
        price_dict = {
            "button_price_1.n_clicks":"$",
            "button_price_2.n_clicks":"$$",
            "button_price_3.n_clicks":"$$$",
            "button_price_4.n_clicks":"$$$$",
        }
        user_recommendation = get_recommendationdata_price(recc_mf, userid, "userid", True, price = price_dict[button_clicked])[:4]
    card_output = [
        [
            dbc.Col(dbc.Card([
                dbc.CardImg(
                    src=shop_info.loc[shop_info["alias"] == shop, "image_url"].values[0], top=True, 
                    style = {"height": "100px", "width": "auto", "object-fit": "cover"}),
                dbc.CardBody([
                        html.H4(shop_info.loc[shop_info["alias"] == shop, "name"].values[0], className="card-title"),
                        html.P(str(shop_info.loc[shop_info["alias"] == shop, "address"].values[0][:-11]), className="card-text",),
                        html.P(" | ".join([
                            str(shop_info.loc[shop_info["alias"] == shop, "rating"].values[0]) + "☆",
                            str(shop_info.loc[shop_info["alias"] == shop, "price"].values[0]),
                        ]), className="card-text",
                        ),
                        dbc.Button("View Map", color="primary", id="button_"+str(shop)),
                        dbc.Popover(
                            html.Iframe(
                                src="https://www.google.com/maps/embed/v1/place?key=AIzaSyCIIp4Wz-UC-Lx5XzHZQAp16dd4x8qbVgE&q="+str(shop_info.loc[shop_info["alias"] == shop, "address"].values[0][-17:-11]), 
                                style={"width":"300", "height":"450", "allowfullscreen":"", "loading":"lazy", "referrerpolicy":"no-referrer-when-downgrade", "border":"0"}
                            ),
                            # "",
                            target=f"button_"+str(shop),
                            trigger="click",
                            placement="bottom",
                        )
                    ]
                )],
                className="mb-3",
                style={"width": "18rem"},
            ), width="auto")
            for shop in user_recommendation
        ]
    ]

    return card_output

# main page card light fm component callback
@app.callback(
    [
        Output("cards_fm_component", "children"),
    ], [
        Input("main_page_container", "children"),
        Input("button_price_1", "n_clicks"),
        Input("button_price_2", "n_clicks"),
        Input("button_price_3", "n_clicks"),
        Input("button_price_4", "n_clicks"),
        Input("button_price_any", "n_clicks")
    ], [
        State("user_id_offcanvas", "children")
    ],
    prevent_initial_call = True
)
def output_changecards(child, button1, button2, button3, button4, button5, userid):
    button_clicked = dash.callback_context.triggered[0]['prop_id']
    if (button_clicked == "main_page_container.children") or (button_clicked == "button_price_any.n_clicks"):
        user_recommendation = get_recommendationdata(recc_fm, userid, "Unnamed: 0", True, "fm")[:4]
        user_recommendation_expln = get_recommendationdata_explain(recc_fm_expln, userid, "Unnamed: 0")
    else:
        price_dict = {
            "button_price_1.n_clicks":"$",
            "button_price_2.n_clicks":"$$",
            "button_price_3.n_clicks":"$$$",
            "button_price_4.n_clicks":"$$$$",
        }
        user_recommendation, user_recommendation_expln = get_recommendationdata_price(
            recc_fm, userid, "Unnamed: 0", True, mode = recc_fm_expln, price = price_dict[button_clicked])
        user_recommendation = user_recommendation[:4]
        
    card_output = [
        [
            dbc.Col(dbc.Card([
                dbc.CardImg(
                    src=shop_info.loc[shop_info["alias"] == shop, "image_url"].values[0], top=True, 
                    style = {"height": "100px", "width": "auto", "object-fit": "cover"}),
                dbc.CardBody([
                        html.H4(shop_info.loc[shop_info["alias"] == shop, "name"].values[0], className="card-title"),
                        html.P(str(shop_info.loc[shop_info["alias"] == shop, "address"].values[0][:-11]), className="card-text",),
                        html.P(" | ".join([
                            str(shop_info.loc[shop_info["alias"] == shop, "rating"].values[0]) + "☆",
                            str(shop_info.loc[shop_info["alias"] == shop, "price"].values[0]),
                        ]), className="card-text",
                        ),
                        dbc.Button("View Map", color="primary", id="button_"+str(shop)),
                        dbc.Button("View Attributes", color="primary", id="button_explain_"+str(shop), style={'margin-left': 15}),
                        dbc.Popover(
                            html.Iframe(
                                src="https://www.google.com/maps/embed/v1/place?key=AIzaSyCIIp4Wz-UC-Lx5XzHZQAp16dd4x8qbVgE&q="+str(shop_info.loc[shop_info["alias"] == shop, "address"].values[0][-17:-11]), 
                                style={"width":"300", "height":"450", "allowfullscreen":"", "loading":"lazy", "referrerpolicy":"no-referrer-when-downgrade", "border":"0"}
                            ),
                            # "",
                            target=f"button_"+str(shop),
                            trigger="click",
                            placement="bottom",
                        ),
                        dbc.Popover(
                            "Because you might be interested in " + user_recommendation_expln[list(user_recommendation).index(shop)],
                            target=f"button_explain_"+str(shop),
                            trigger="hover",
                            placement="bottom",
                        ),
                    ]
                )],
                className="mb-3",
                style={"width": "18rem"},
            ), width="auto")
            for shop in user_recommendation
        ]
    ]

    return card_output

# main page offcavas component callback
@app.callback(
    [
        Output("offcanvas", "children"),
    ], [
        Input("cards_component", "children")
    ], [
        State("user_id_offcanvas", "children")
    ],
    prevent_initial_call = True
)
def output_wordcloud(child, userid):
    return [html.Img(src='./assets/wordcloud_temp.png', height=180)]

# price filter changes
@app.callback(
    [
        Output("carousel_component", "items"),
    ], [
        Input("button_price_1", "n_clicks"),
        Input("button_price_2", "n_clicks"),
        Input("button_price_3", "n_clicks"),
        Input("button_price_4", "n_clicks"),
        Input("button_price_any", "n_clicks")
    ], [
        State("user_id_offcanvas", "children")
    ],
    prevent_initial_call = True
)
def price_filter(button1, button2, button3, button4, button5, userid):
    button_clicked = dash.callback_context.triggered[0]['prop_id']
    carousel = []
    cards = []
    cards_fm = []

    if button_clicked == "button_price_1.n_clicks":
        for shop_no in range(len(most_pop)):
            if str(shop_info.loc[shop_info["alias"] == most_pop[shop_no], "price"].values[0]) == "$":
                carousel.append(most_pop_list[shop_no])
            if len(carousel) == 10:
                break

    if button_clicked == "button_price_2.n_clicks":
        for shop_no in range(len(most_pop)):
            if str(shop_info.loc[shop_info["alias"] == most_pop[shop_no], "price"].values[0]) == "$$":
                carousel.append(most_pop_list[shop_no])
            if len(carousel) == 10:
                break

    if button_clicked == "button_price_3.n_clicks":
        for shop_no in range(len(most_pop)):
            if str(shop_info.loc[shop_info["alias"] == most_pop[shop_no], "price"].values[0]) == "$$$":
                carousel.append(most_pop_list[shop_no])
            if len(carousel) == 10:
                break

    if button_clicked == "button_price_4.n_clicks":
        for shop_no in range(len(most_pop)):
            if str(shop_info.loc[shop_info["alias"] == most_pop[shop_no], "price"].values[0]) == "$$$$":
                carousel.append(most_pop_list[shop_no])
            if len(carousel) == 10:
                break

    if button_clicked == "button_price_any.n_clicks":
        carousel = most_pop_list[:10]
    
    return [carousel]

##################################################################################################
# new user page layout
##################################################################################################

new_user_page_layout = html.Div(
    [
        dbc.Container([
            dbc.Row(navbar),
            dbc.Row([
                dbc.Col(html.H4("Welcome to your personalized recommendations!", className="display-10", style={'color': 'black', 'margin-top': 90}), width = 10),
                dbc.Col(dbc.ButtonGroup(
                    [dbc.Button("$", outline=True, color="primary", id ="button_price_1"), 
                    dbc.Button("$$", outline=True, color="primary", id ="button_price_2"), 
                    dbc.Button("$$$", outline=True, color="primary", id ="button_price_3"), 
                    dbc.Button("$$$$", outline=True, color="primary", id ="button_price_4"), 
                    dbc.Button("Any", outline=True, color="primary", id ="button_price_any")],
                    size="sm",
                ), align="end", width = 2)
            ], style = {"margin-bottom":5}),
            dbc.Row(
                dbc.Col(
                    dbc.Carousel(
                        items=most_pop_list[:10],
                        controls=True,
                        indicators=True,
                        interval=3000,
                        ride="carousel",
                        id="carousel_component"
                    ),
                )
            ),
            dbc.Row(
                dcc.Graph(
                    id='map', 
                    figure=fig,
                    style = {"margin-top":25},
            )
            ),
        ])
    ]
)

##################################################################################################
# overall layout
##################################################################################################

app.layout = dbc.Container(
    entry_page_layout,
    style={
            'background-image': 'url(/assets/welcome-background.jpg)',
            'background-repeat': 'no-repeat',
            'background-position': 'center',
            'background-size': 'cover',
            'position': 'fixed',
            'min-height': '100%',
            'min-width': '100%',
            },
    id = "main_page_container"
)

# main page entry point callback
@app.callback(
    [
        Output("main_page_container", "children"), 
        Output("main_page_container", "style"),
        Output("user_id_offcanvas", "children")
    ], [
        Input("enter_button", "n_clicks"),
        Input("create_user_button", "n_clicks")
    ], [
        State("userid_input", "value")
    ],
    prevent_initial_call = True
)
def ouput_changepage(nclicks, nclicks_newuser, userid):
    if (not nclicks) and (not nclicks_newuser):
        raise dash.exceptions.PreventUpdate
    button_clicked = dash.callback_context.triggered[0]['prop_id']
    if button_clicked == "enter_button.n_clicks":
        export_wordcloud(userid)
        time.sleep(1)
        return main_page_layout, main_page_style, userid
    else:
        return new_user_page_layout, main_page_style, userid

if __name__ == "__main__":
    app.run_server(
        # debug = True
    )

# -5YMIME_WEin_by41Bj-3Q