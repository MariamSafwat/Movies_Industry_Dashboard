import dash
from dash import html
from dash import dcc
from dash.html.Button import Button
import plotly.express as px
from dash.dependencies import Input, Output,State
import numpy as np
from traitlets.traitlets import Int
import pandas as pd
import plotly.graph_objs as go
import pycountry
import plotly.io as pio
pio.templates.default = "plotly_dark"

app=dash.Dash( external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css'])

#read dataframe
df = pd.read_csv("movies.csv")
#drop null and duplicates
df.dropna(inplace = True)
df.drop_duplicates(inplace = True)


#start Rating Distribution with Genres
movie_genre_gross = df.groupby(['genre'])['gross'].sum().to_frame().reset_index().sort_values('gross', ascending = False).head(8)
movie_genre_gross['genre'].to_list()
list_movie_genre_gross = sorted(movie_genre_gross['genre'].to_list())
list_movie_genre_gross
# movie_genre_gross

genre_trend = df.groupby(['year','genre'])['gross'].sum().unstack().fillna(0)
genre_trend = genre_trend[['Action',
 'Adventure',
 'Animation',
 'Biography',
 'Comedy',
 'Crime',
 'Drama',
 'Horror']]


df['count'] = 1
#get a list of all genres
genres = df['genre'].unique()

order = pd.DataFrame(df.groupby('score')['count'].sum().sort_values(ascending=False).reset_index())
rating_order = list(order['score'])
mf = df.groupby('genre')['score'].value_counts().unstack().sort_index().fillna(0).astype(int)[rating_order]
data = []
for i in genres:
    genre = mf.loc[i]
    data.append(go.Bar(x=genre.index, y=genre, name=i))

fig = go.Figure(data=data)
fig.update_layout(barmode='stack')

#end Rating Distribution with Genres
#start map graph 
input_countries = df['country'].unique()

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3

df['country_code'] = [countries.get(country, 'Unknown code') for country in df['country']]

fig_map = px.choropleth(df, color='budget', locations='country_code', hover_name='country')

#end map graph 



app.layout = html.Div([
    # Title Dashboard
    html.H1('Movie Industry DashBoard',  
            style = {'color':'White','fontsize':40,'textAlign':'center','border-width': 1, 'border': 'solid'}),
    
    #  First div contains two main parts , the first for a line chart and the other for the big numbers
    html.Div([
        html.Div([
            html.H3("IMDB Score Distribution Per Genre",
            style = {'color':'white','fontsize':20,'textAlign':'center','border-width': 1, 'border': 'solid', 'backgroundColor': 'DarkCyan'}),
            dcc.Graph(id='barChart', figure=fig)
            ], className='six columns'),
        
        
        # div for pie chart
    html.Div([
    dcc.Dropdown(
        id='names', 
        value='genre', 
        options=[{'value': x, 'label': x} 
                 for x in ['genre', 'rating']],
        clearable=False,
        style={'color': '#386CB0', "text-align": "center",'width':'50%'}
    ),
    dcc.Dropdown(
        id='values', 
        value='budget', 
        options=[{'value': x, 'label': x} 
                 for x in ['budget', 'score', 'runtime', 'gross', 'votes']],
        clearable=False
        ,
        style={'color': '#386CB0', "text-align": "center",'width': '50%'}
    ),
    dcc.Graph(id="pie-chart"),
    ], className='five columns'),
        
    ]),

    #map
    html.Div([
            html.H3("Countries Budget for Movies Industry",
            style = {'color':'white','fontsize':20,'textAlign':'center','border-width': 1, 'border': 'solid', 'backgroundColor': 'DarkCyan'}),
            dcc.Graph(id='mapChart', figure=fig_map, style={'margin-left' : '-110px'})
            ], className='nine columns')
    

],style={'backgroundColor':'DarkCyan'})

#start pie chart
@app.callback(
    Output("pie-chart", "figure"), 
    [Input("names", "value"), 
     Input("values", "value")])
def generate_chart(names, values):
    if names == None or values == None:
        fig = px.pie(df, values='budget', names='genre')
    
    else:
        fig = px.pie(df, values=values, names=names)

    return fig

#end pie chart

app.run_server()
