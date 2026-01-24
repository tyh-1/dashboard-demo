import pandas as pd, calendar
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


COLORS = ['#d1dbe4', '#d1dbe4', '#7593af', "#5B7084", "#445C73",
          '#d9d0b4', '#7d6b57', '#879e82', '#666b5e', "#656668",
          "#db8d73", '#e5c185', '#fbf2c4', "#6CAB91", '#008585']


def convert_time(s:float):
    if s < 60: return f"{round(s)} s"
    if s < 3600: return f"{round(s/60)} mins"
    return f"{round((s/3600), 1)} hrs"





def get_heatmap_date_range(start_date, end_date):
    """
    決定 heatmap 的日期範圍
    - 如果範圍 < 1 年：補滿整年
    - 如果範圍 >= 1 年：保持原樣\n
    start_date, end_date 可以是 datetime.date 或 datetime.datetime
    """
    duration = (end_date - start_date).days
    same_year = (start_date.year == end_date.year)
    
    if (duration < 365) and same_year:
        heatmap_start = date(start_date.year, 1, 1)
        heatmap_end = date(end_date.year, 12, 31)

    elif (duration < 365):
        last_day = calendar.monthrange(end_date.year, end_date.month)[1]
        heatmap_end = date(end_date.year, end_date.month, last_day)
        heatmap_start = heatmap_end - timedelta(days=365)
        if heatmap_start > start_date: heatmap_start = start_date

    else:
        heatmap_start = start_date
        heatmap_end = end_date
    
    return heatmap_start, heatmap_end



def create_topn(df, genre, n=10):
    top_n = df.iloc[0:n,:]
    top_n['hours'] = round(top_n['duration'] / 3600, 2)
    top_n = top_n[::-1]
    height = 400 + 20*n

    if genre == 'artist': col = "#605B84"
    if genre == 'track': col = "#5B7184"
    if genre == 'album': col = "#84785B"
    fig = px.bar(
        top_n,
        x='hours', y=genre,
        orientation='h',
        text=genre,  # 把名字顯示在 bar 裡面！
        color_discrete_sequence=[col]
    )

    fig.update_traces(
        textposition ='inside',  # 文字在 bar 裡面
        texttemplate ='  %{y}',
        textfont = dict(size=16, color='white', family='Arial Black'),
        insidetextanchor ='start',  # 文字靠左對齊
        hovertemplate = '<b>%{y}<br>Listening time: %{x} hours</b>'
    )

    fig.update_layout(
        yaxis=dict(visible=False),
        xaxis_title='Listening Hours',
        showlegend=False,
        plot_bgcolor='white',
        height=height
    )
    return fig

def create_listening_heatmap(full_df: pd.DataFrame, size, color_light, color_dark) -> go.Figure:

    month_positions = full_df.groupby(['year', 'month'])['week'].first().reset_index()
    month_positions = month_positions.drop_duplicates(['week'], keep='last')

    fig = go.Figure(data=go.Scatter(
        x=full_df['week'],
        y=full_df['weekday'],
        mode='markers',
        marker=dict(
            size = size,
            color = full_df['hours'],
            colorscale = (color_light, color_dark),
            showscale=True,
            colorbar=dict(title="Hours"),
            line=dict(width=0)  # 圓點不要邊框
        ),
        text=full_df['day'].dt.strftime('%Y-%m-%d'),
        hovertemplate='<b>%{text}</b><br>Duration: %{marker.color:.1f} hrs<extra></extra>'
    ))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for _, row in month_positions.iterrows():
        fig.add_annotation(
            x=row['week'],
            y= -1.5,
            text=month_names[row['month'] - 1],
            showarrow=False,
            font=dict(size=15, weight='bold'),
            xanchor='left'
        )

    # 調整 layout
    fig.update_layout(
        title='Listening Calendar Heatmap',
        yaxis_title='',
        xaxis=dict(showticklabels=False),
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],  
            autorange='reversed',
            showgrid=False, 
            zeroline=False  
        ),
        height=280,
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


def create_context_pie(df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        df,
        values='count', 
        names='context_type', 
        color_discrete_sequence=px.colors.sequential.Blues, 
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',  # 文字在內部
        textinfo='percent+label',  # 顯示百分比 + 名稱
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),  # 圖例在下方
        height=400
    )

    return fig

def create_context_bar(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df,
        x='count',
        y=[1] * len(df),  # 單一橫條
        orientation='h',
        color='context_type',
        color_discrete_sequence=px.colors.sequential.Blues,
        text='count'
    )
    
    fig.update_traces(
        texttemplate='%{label} %{percent}',  # 顯示名稱 + 百分比
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        height=200,  # 橫條比較矮
        xaxis_title='',
        yaxis_title='',
        yaxis_showticklabels=False,  # 隱藏 y 軸標籤
        barmode='stack'
    )
    
    return fig

if __name__ == "__main__":
    pass
