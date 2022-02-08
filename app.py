from enum import auto
from turtle import title, width
from click import style
import dash
import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from dash import html, dcc, callback_context
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Scraping Tech Companies name and Ticker
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
url = 'https://companiesmarketcap.com/tech/largest-tech-companies-by-market-cap/'

result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")

companies_name = [name.text for name in doc.find_all('div', class_='company-name')]
tickers = [ticker.text for ticker in doc.find_all('div', class_='company-code')]

ticker_list = []
for name in range(len(companies_name)):
    ticker_list.append({'label':companies_name[name], 'value':tickers[name]})

# Creating our Graph
fig = go.Figure(
    layout={'template':'plotly_dark', 'xaxis_title':'Date', 'yaxis_title':'USD',})

app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1('Tech Companies Stock Chart', style={'textAlign':'center', 'color':'#00ffff', 'font':'san-serif'}))),
    
    dbc.Row(dbc.Col(html.Div([dcc.Dropdown(id='drop_down', 
                                        value='aapl', 
                                        placeholder='Search Company',
                                        options=ticker_list,
                                        style={'color':'#7f8c8d'})]),
                            width={'size':6, 'offset':3}, style={'padding':20})),
    dbc.Row(dbc.Col(html.Div([
                            html.Button('1D', className='btn btn-white', id='1d', n_clicks=0),
                            html.Button('5D', className='btn btn-white', id='5d', n_clicks=0),
                            html.Button('1M', className='btn btn-white', id='1m', n_clicks=0),
                            html.Button('6M', className='btn btn-white', id='6m', n_clicks=0),
                            html.Button('1Y', className='btn btn-white', id='1y', n_clicks=0),
                            html.Button('5Y', className='btn btn-white', id='5y', n_clicks=0),
                            html.Button('Max', className='btn btn-white', id='max', n_clicks=0)]), 
    
                    width={'size':6, 'offset':2})),
    dbc.Row(dbc.Col(html.Div([
        dcc.Graph(id='graph', figure=fig, style={'paddingTop':10}),
        dcc.Checklist(id='toggle_rangeslider', 
                    options=[{'label':' Include Rangeslider', 'value':'slider'}], 
                    value=['slider'], 
                    labelStyle={'display':'inline-block'}),
        
        
    ]),
    width={'size':8, 'offset':2}
    ))

])

@app.callback(
    Output('graph', 'figure'),
    Input('drop_down', 'value'),
    Input('toggle_rangeslider', 'value'),
    Input('1d', 'n_clicks'),
    Input('5d', 'n_clicks'),
    Input('1m', 'n_clicks'),
    Input('6m', 'n_clicks'),
    Input('1y', 'n_clicks'),
    Input('5y', 'n_clicks'),
    Input('max', 'n_clicks')

)
def update_graph(value, check, btn1, btn2, btn3, btn4, btn5, btn6, btn7):
    
    for ticker in ticker_list:
        #If User selects and input from the dropdown
        if value == ticker['value']:
            #Update the title of the graph to that company
            fig.update_layout({'title':ticker['label']})
            #Get that company data from Yahoo finace api
            ticker_df = yf.Ticker(ticker['value'])
            th = ticker_df.history(period='10y')
            
            changed_ids = []
            for p in callback_context.triggered:
                changed_ids.append(p['prop_id'])

            changed_id = changed_ids[0]
            if '1d' in changed_id:
                th = ticker_df.history(period='1d', interval='1m')
            elif '5d' in changed_id:
                th = ticker_df.history(period='5d', interval='1d')
            elif '1m' in changed_id:
                th = ticker_df.history(period='1mo', interval='1d')
            elif '6m' in changed_id:
                th = ticker_df.history(period='6mo', interval='1d')
            elif '1y' in changed_id:
                th = ticker_df.history(period='1y', interval='1d')
            elif '5y' in changed_id:
                th = ticker_df.history(period='5y', interval='1d')
            else:
                th = ticker_df.history(period='10y')
            
            df = [go.Candlestick(x=th.index,
                        open=th['Open'], high=th['High'],
                        low=th['Low'], close=th['Close'],
                        increasing_line_color='aqua', decreasing_line_color='gray')]

            fig.update(data=df)

    fig.update_layout(
        xaxis_rangeslider_visible='slider' in check
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)