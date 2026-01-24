import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

COLORS = ['#d1dbe4', '#d1dbe4', '#7593af', "#5B7084", "#445C73",
          '#d9d0b4', '#7d6b57', '#879e82', '#666b5e', "#656668",
          "#db8d73", '#e5c185', '#fbf2c4', "#6CAB91", '#008585']




def create_album_treemap(df_treemap: pd.DataFrame)-> go.Figure:
    """圖1: 聽完的專輯的，treemap，value by 時長"""
    df_treemap['hours'] = df_treemap['sum'] / 3600

    # 建立 treemap
    fig = px.treemap(
        df_treemap,
        path=['album'],  
        values='hours',     # 面積大小
        color='hours',      # 顏色深淺
        color_continuous_scale= [COLORS[-2], COLORS[4]],  
        hover_data={
            'hours': ':.2f',              
            'total_duration': True      
        },
        custom_data=['total_duration', 'main_artists']    # 用於自訂 hover
    )

    # 自訂 hover template
    fig.update_traces(
        textinfo='label',
        textfont=dict(size=20, color='white', family='sans-serif'),
        textposition='middle center',
        hovertemplate='<b>專輯：%{label}</b><br>' +
                    '藝人：%{customdata[1]}<br>' +
                    '聆聽時長：%{customdata[0]}<br>' +
                    '<extra></extra>',
        marker=dict(
            line=dict(width=2.5, color=COLORS[4])  # 增加邊框讓區塊更明顯
        )
    )

    # 調整版面
    fig.update_layout(
        height=600,
        margin=dict(t=0, l=0, r=0, b=0),
        showlegend=False
    )
    return fig


def create_marathon_listen(df: pd.DataFrame)-> go.Figure:
    df["session"] = pd.to_datetime(df["session_start"])
    df['play_count'] = df.groupby('album')['album'].transform('count')
    df['start_time_str'] = pd.to_datetime(df['session_start']).dt.strftime('%m/%d %H:%M')
    df['end_time_str'] = pd.to_datetime(df['session_end']).dt.strftime('%m/%d %H:%M')
    fig = px.scatter(
        df,
        x='session',  # 你的日期欄位
        y='album_short',
        color='play_count',
        color_continuous_scale=[COLORS[-2], COLORS[4]],
        custom_data=['main_artists', 'album', 'start_time_str', 'end_time_str'],
        # title='Marathon Listening Sessions'
    )
    fig.update_traces(marker=dict(size=8),
                      hovertemplate = '<b>artist(s): %{customdata[0]}<br>album: %{customdata[1]}<br>%{customdata[2]} ~ %{customdata[3]}</b>')
    fig.update_layout(
        height=600,
        xaxis_title='Time',
        yaxis_title='Album',
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=50, l=0, r=0, b=0)
    )

    return fig

if __name__ == "__main__":
    start_date = pd.to_datetime('2025-10-25').date()
    end_date = pd.to_datetime('2026-01-24').date()
    prop = 1
    # df_duration = get_album_duration(start_date, end_date, prop)
    # df_marathon = get_marathon_listen(start_date, end_date, prop)
    # df_duration.to_parquet('../dashboard-demo/data/page3/df_duration.parquet')
    # df_marathon.to_parquet('../dashboard-demo/data/page3/df_marathon.parquet')

    df_marathon_raw = (pd.read_parquet('../dashboard-demo/data/page3/df_marathon.parquet'))
    # print(df_marathon)
    prop2 = 1
    df = df_marathon_raw.loc[df_marathon_raw['unique_tracks'] >= df_marathon_raw['total_tracks']*prop2, :]
    print(df)
    # COUNT(DISTINCT track_number) >= MAX(total_tracks)*{prop}