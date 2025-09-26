"""
Advanced interactive chart with multiple timeframes
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from indicators import TechnicalIndicators

TIMEFRAME_OPTIONS = {
    '1s': '1s',
    '5s': '5s', 
    '15s': '15s',
    '30s': '30s',
    '1m': '1m',
    '3m': '3m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '1h': '1h',
    '2h': '2h',
    '4h': '4h',
    '6h': '6h',
    '12h': '12h',
    '1d': '1d'
}

def create_advanced_chart(df: pd.DataFrame, current_price: float = None, 
                         show_rsi: bool = True, show_macd: bool = True,
                         show_volume: bool = True):
    """
    Create advanced interactive chart with zoom, pan, and multiple indicators
    """
    
    if df.empty:
        return None
    
    num_rows = 1
    row_heights = [0.6]
    subplot_titles = ['ASTER/USDT Price']
    
    if show_volume:
        num_rows += 1
        row_heights.append(0.15)
        subplot_titles.append('Volume')
    
    if show_rsi:
        num_rows += 1
        row_heights.append(0.15)
        subplot_titles.append('RSI (14)')
    
    if show_macd:
        num_rows += 1
        row_heights.append(0.15)
        subplot_titles.append('MACD')
    
    row_heights = [h / sum(row_heights) for h in row_heights]
    
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=subplot_titles
    )
    
    colors = ['green' if close > open_ else 'red' 
              for open_, close in zip(df['open'], df['close'])]
    
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='ASTER',
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000',
            increasing_fillcolor='rgba(0, 255, 0, 0.3)',
            decreasing_fillcolor='rgba(255, 0, 0, 0.3)'
        ),
        row=1, col=1
    )
    
    if current_price and len(df) > 0:
        fig.add_hline(
            y=current_price, 
            line_dash="dash", 
            line_color="yellow",
            line_width=2,
            annotation_text=f"Current: ${current_price:.6f}",
            annotation_position="right",
            row=1, col=1
        )
    
    support_resistance = TechnicalIndicators.detect_support_resistance(df)
    if support_resistance['support']:
        fig.add_hline(
            y=support_resistance['support'],
            line_dash="dot",
            line_color="green",
            line_width=1,
            annotation_text=f"Support: ${support_resistance['support']:.6f}",
            annotation_position="left",
            row=1, col=1
        )
    
    if support_resistance['resistance']:
        fig.add_hline(
            y=support_resistance['resistance'],
            line_dash="dot",
            line_color="red",
            line_width=1,
            annotation_text=f"Resistance: ${support_resistance['resistance']:.6f}",
            annotation_position="left",
            row=1, col=1
        )
    
    current_row = 1
    
    if show_volume:
        current_row += 1
        volume_colors = ['green' if df['close'].iloc[i] > df['open'].iloc[i] else 'red' 
                        for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='Volume',
                marker_color=volume_colors,
                showlegend=False
            ),
            row=current_row, col=1
        )
    
    if show_rsi:
        current_row += 1
        rsi = TechnicalIndicators.calculate_rsi(df)
        
        if not rsi.empty:
            rsi_colors = []
            for val in rsi:
                if val > 70:
                    rsi_colors.append('red')
                elif val < 30:
                    rsi_colors.append('green')
                else:
                    rsi_colors.append('purple')
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rsi,
                    name='RSI',
                    line=dict(color='purple', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(128, 0, 128, 0.1)'
                ),
                row=current_row, col=1
            )
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         line_width=1, row=current_row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                         line_width=1, row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         line_width=1, row=current_row, col=1)
            
            fig.update_yaxes(range=[0, 100], row=current_row, col=1)
    
    if show_macd:
        current_row += 1
        macd_line, macd_signal, macd_hist = TechnicalIndicators.calculate_macd(df)
        
        if not macd_hist.empty:
            hist_colors = ['green' if val > 0 else 'red' for val in macd_hist]
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=macd_hist,
                    name='MACD Histogram',
                    marker_color=hist_colors,
                    showlegend=True
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=macd_line,
                    name='MACD',
                    line=dict(color='blue', width=2)
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=macd_signal,
                    name='Signal',
                    line=dict(color='orange', width=2)
                ),
                row=current_row, col=1
            )
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         line_width=1, row=current_row, col=1)
    
    fig.update_layout(
        height=900,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        hovermode='x unified',
        template='plotly_dark',
        dragmode='zoom',
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='white',
            spikethickness=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='white',
            spikethickness=1
        )
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
    
    config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    }
    
    return fig, config

def fetch_timeframe_data(aster_api, symbol: str, timeframe: str, limit: int = 500):
    """Fetch data for specific timeframe"""
    try:
        df = aster_api.get_klines(symbol, interval=timeframe, limit=limit)
        return df
    except Exception as e:
        st.error(f"Error fetching {timeframe} data: {e}")
        return pd.DataFrame()