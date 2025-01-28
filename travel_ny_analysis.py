import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Input, Output
import plotly.graph_objects as go
import yfinance as yf
from datetime import date
## Base de dados
# albany = 'https://data.insideairbnb.com/united-states/ny/albany/2024-11-05/data/listings.csv.gz'
URLS = {
    'ALBANY': 'https://data.insideairbnb.com/united-states/ny/albany/2024-11-05/data/listings.csv.gz',
    'NEW YORK CITY' : 'https://data.insideairbnb.com/united-states/ny/new-york-city/2024-11-04/data/listings.csv.gz',
    'ROCHESTER' : 'https://data.insideairbnb.com/united-states/ny/rochester/2024-11-25/data/listings.csv.gz'
}

df_city = pd.read_csv(URLS['NEW YORK CITY']).dropna(axis=0, subset=['price'])
df_city['price'] = df_city['price'].str.replace('$','').str.replace(',','').astype('float')

#### Base de dados Acoes
# stock = yf.download('AAPL', 
#                     start='2023-01-01',
#                     end='2023-12-31',
#                     interval='1d')
# stock_df = pd.DataFrame(stock)
# stock_df = stock_df.droplevel([1],axis=1)

## Grafico Acoes

# candlestick_chart = go.Figure(data=[go.Candlestick(x=stock_df.index,
#                 open=stock_df['Open'],
#                 high=stock_df['High'],
#                 low=stock_df['Low'],
#                 close=stock_df['Close'])])

# candlestick_chart.update_layout(xaxis_rangeslider_visible=False)



##listas DCC
numeric_columns = df_city.select_dtypes(include='float').columns
cities = list(URLS.keys())

## Grafico
fig = px.scatter_map(df_city, 
                     lat="latitude", 
                     lon="longitude",     
                     color="review_scores_rating", 
                     size="price",
                     color_continuous_scale='reds', #px.colors.cyclical.IceFire, 
                     size_max=15, 
                     zoom=10,map_style='open-street-map')
app = Dash()
server = app.server

app.layout = html.Div([
    html.H1("Análise Estadia em NY"),
    dcc.RadioItems(cities, cities[0], id='radio_cities', inline=True),
    html.Div([html.Label('Escolha qual informação será o tamanho do ponto: '),
              dcc.Dropdown(numeric_columns, numeric_columns[0], clearable=False, id='dropdown_size')],  
                         style={'display':'inline-block', 
                                'width':'45vw'}),
    html.Div([html.Label('Escolha qual informação será o cor do ponto: '),
              dcc.Dropdown(numeric_columns, numeric_columns[0], clearable=False, id='dropdown_color')],  
                         style={'display':'inline-block', 
                                'width':'45vw'}),
                                
    dcc.Graph(figure=fig, id='scatter_map_airbnb'),
    html.H1('Analise de Ações'),
    dcc.DatePickerRange(
        id='date_range_stock',
        min_date_allowed=date(2020, 1, 1),
        max_date_allowed=date(2024, 12, 31),
        initial_visible_month=date(2024, 1, 1),
        start_date= date(2024,12,1),
        end_date=date(2024, 12, 31)

    ),
    html.Div([
        html.Label('Grafico das acoes da Apple:'),
        dcc.Graph(id='candlestick_chart_apple')
    ]),
        html.Div([
        html.Label('Grafico das acoes da Amazon:'),
        dcc.Graph(id='candlestick_chart_amazon')
    ])
    
])

@callback(
    Output('scatter_map_airbnb','figure'),
    Input('radio_cities','value'),
    Input('dropdown_size','value'),
    Input('dropdown_color','value')
)
def update_scatter_map(city, size_value,color_value):
    df_city = pd.read_csv(URLS[city]).dropna(axis=0, subset=[size_value,color_value])
    df_city['price'] = df_city['price'].str.replace('$','').str.replace(',','').astype('float')

    fig = px.scatter_map(df_city, 
                     lat="latitude", 
                     lon="longitude",     
                     color=color_value, 
                     size=size_value,
                     color_continuous_scale='reds', #px.colors.cyclical.IceFire, 
                     size_max=15, 
                     zoom=10,map_style='open-street-map')
    return fig

@callback(
    Output('candlestick_chart_apple', 'figure'),
    Output('candlestick_chart_amazon', 'figure'),
    Input('date_range_stock','start_date'),
    Input('date_range_stock', 'end_date')
)
def update_candles_chart(start_date,end_date):
    #apple chart
    stock = yf.download('AAPL', 
                    start=start_date,
                    end=end_date,
                    interval='1d')
    stock_df = pd.DataFrame(stock)
    stock_df = stock_df.droplevel([1],axis=1)

    candlestick_chart_apple = go.Figure(data=[go.Candlestick(x=stock_df.index,
                open=stock_df['Open'],
                high=stock_df['High'],
                low=stock_df['Low'],
                close=stock_df['Close'])])

    candlestick_chart_apple.update_layout(xaxis_rangeslider_visible=False)

    ##amazon chart
    stock = yf.download('AMZN', 
                    start=start_date,
                    end=end_date,
                    interval='1d')
    stock_df = pd.DataFrame(stock)
    stock_df = stock_df.droplevel([1],axis=1)

    candlestick_chart_amazon = go.Figure(data=[go.Candlestick(x=stock_df.index,
                open=stock_df['Open'],
                high=stock_df['High'],
                low=stock_df['Low'],
                close=stock_df['Close'])])

    candlestick_chart_amazon.update_layout(xaxis_rangeslider_visible=False)
    return candlestick_chart_apple, candlestick_chart_amazon





if __name__ =='__main__':
    app.run(debug=True)