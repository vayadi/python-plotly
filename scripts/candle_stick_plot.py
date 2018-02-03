import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import pandas as pd

def plot_advanced_candle_stick(stock, start_date, end_date):
    stock = 'BTC-USD'
    df = data_retrievers.load_stock_to_data_frame(stock, start_date, end_date)

    INCREASING_COLOR = '#17BECF'
    DECREASING_COLOR = '#7F7F7F'

    trace = go.Candlestick(x=df.index,
                           open=df.Open,
                           high=df.High,
                           low=df.Low,
                           close=df.Close,
                           name=stock,
                           yaxis='y2',
                           increasing=dict(line=dict(color=INCREASING_COLOR)),
                           decreasing=dict(line=dict(color=DECREASING_COLOR)))

    layout = {
        'plot_bgcolor': 'rgb(250, 250, 250)',
        'title': '{}'.format(stock),
        'xaxis': {'rangeselector': dict(visible=True)},
        'yaxis': {'title': 'h'.format(stock), 'domain': [0, 0.2], 'showticklabels': False},
        'yaxis2': {'title': '{} Stock'.format(stock), 'domain': [0.2, 1.05]},
        'legend': {'orientation': 'h', 'y': 0.95, 'x': 0.25, 'yanchor': 'bottom'},
        'margin': dict(t=15, b=10, r=40, l=40)
    }

    data = [trace]

    fig = dict(data=data, layout=layout)

    rangeselector = dict(
        x=0, y=0.9,
        bgcolor='rgba(150, 200, 250, 0.4)',
        font=dict(size=13),
        buttons=list([
            dict(count=1,
                 label='reset',
                 step='all'),
            dict(count=1,
                 label='1 yr',
                 step='year',
                 stepmode='backward'),
            dict(count=6,
                 label='6 mo',
                 step='month',
                 stepmode='backward'),
            dict(count=3,
                 label='3 mo',
                 step='month',
                 stepmode='backward'),
            dict(count=1,
                 label='1 mo',
                 step='month',
                 stepmode='backward'),
            dict(step='all')
        ])
    )

    fig['layout']['xaxis']['rangeselector'] = rangeselector

    sma_day_count = [10, 30]
    sma_colors = ['#1370C0', '#13E050']  # '#E37702',
    for d, c in zip(sma_day_count, sma_colors):
        sma = df['Close'].rolling(d).mean()
        fig['data'].append(dict(x=sma.index, y=sma.values,
                                type='scatter', mode='lines',
                                line=dict(width=2),
                                marker=dict(color=c),
                                yaxis='y2', name='{} d SMA'.format(d)))

    colors = [INCREASING_COLOR if increase else DECREASING_COLOR for increase in np.array(df.Close > df.Close.shift(1))]

    fig['data'].append(dict(x=df.index, y=df.Volume,
                            marker=dict(color=colors),
                            type='bar', yaxis='y', name='Volume'))

    bb_avg, bb_upper, bb_lower = bollinger_bands(df.Close)

    fig['data'].append(dict(x=df.index, y=bb_upper, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#aaa'), hoverinfo='none',
                            legendgroup='Bollinger Bands', name='Bollinger Bands'))

    fig['data'].append(dict(x=df.index, y=bb_lower, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#aaa'), hoverinfo='none',
                            legendgroup='Bollinger Bands', showlegend=False))

    iplot(fig, filename='candlestick_{}_with_bands'.format(stock))
