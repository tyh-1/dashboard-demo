import pandas as pd, numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

COLORS = ['#d1dbe4', '#d1dbe4', '#7593af', '#476f95', '#194a7a',
          '#d9d0b4', '#7d6b57', '#879e82', '#666b5e',
          "#db8d73", '#e5c185', '#fbf2c4', "#6CAB91", '#008585']

def calculate_rankings(df):
    df_detail = df[df['day_of_week'].notna() & df['time_period'].notna()]

    # 計算排名
    df_detail['total_time_rank'] = df_detail['total_time'].rank(ascending=False, method='dense')
    df_detail['skip_rate_rank'] = df_detail['avg_skip_rate'].rank(ascending=True, method='dense')
    df_detail['new_track_rank'] = df_detail['new_track_ratio'].rank(ascending=False, method='dense')
    df_detail['session_time_rank'] = df_detail['avg_session_time'].rank(ascending=False, method='dense')
    df_detail['artist_concentration_rank'] = df_detail['artist_concentration'].rank(ascending=True, method='dense')

    # 4. 排序（按時間連續）
    time_order = {'Late Night': 1, 'Morning': 2, 'Afternoon': 3, 'Evening': 4}
    df_detail['time_order'] = df_detail['time_period'].map(time_order)
    df_detail = df_detail.sort_values(['day_of_week', 'time_order']).reset_index(drop=True)

    return df_detail


def create_sparkline(avg_value, data, labels, color, fillcolor, title=''):
    """
    建立 Plotly sparkline
    
    Parameters:
    - data: 數值列表（28 個點）
    - labels: 標籤列表（用於 hover）
    - color: 線條顏色
    - title: 圖表標題（用於 hover）
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=[avg_value] * 28,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip',
        name=''
    ))

    # 實際資料
    fig.add_trace(go.Scatter(
        y=[x for x in data],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tonexty',
        fillcolor=fillcolor,
        text=labels,
        hovertemplate='<b>%{text}</b><br>' + title + ': %{y}<extra></extra>',
        showlegend=False
    ))

    fig.update_layout(
        height=100,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(visible=False, showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        hovermode='closest'
    )
    return fig

def format_time_slot_label(row):
    """格式化時段標籤（用於 hover）"""
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return f"{days[int(row['day_of_week'])]} {row['time_period']}"

def create_full_heatmap(df, var, var_config):
    """
    var: 要顯示的欄位名稱
    var_config: dict 包含 {
        'title': 圖表標題,
        'colorbar_title': colorbar 標題,
        'unit': 單位 (如 'hrs', '%'),
        'text_format': 文字格式 (如 '{:.1f}', '{:.1%}'),
        'hover_label': hover 時顯示的標籤
        'colorscale': 色階 (optional)
    }
    """
    df['total_time'] = df['total_time']/3600
    heatmap_data = df.pivot(index='day_of_week', columns='time_period', values=var)

    # 定義時段順序
    time_order = ['Late Night', 'Morning', 'Afternoon', 'Evening']
    time_order_chinese = ['深夜', '早晨', '下午', '晚上']
    heatmap_data = heatmap_data[time_order]

    # 定義星期順序
    day_labels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_labels_chinese = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
    heatmap_data = heatmap_data.sort_index()

    # 格式化顯示文字
    if var_config['unit'] == '%':
        display_text = (heatmap_data * 100).round(1).astype(str) + '%'
    else:
        display_text = heatmap_data.round(1).astype(str) + f" {var_config['unit']}"

    # 建立 Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=time_order_chinese,
        y=day_labels_chinese,
        colorscale=var_config.get('colorscale', [[0.0, "#CED6DE"], [1.0, '#476f95']]),
        hovertemplate=f'<b>%{{y}}</b>%{{x}}<br>{var_config["hover_label"]}: %{{z{var_config["hover_format"]}}}<extra></extra>',
        colorbar=dict(
            ticksuffix=f" {var_config['unit']}" if var_config['unit'] != '%' else '',
            tickformat='.0%' if var_config['unit'] == '%' else '.1f'
        )
    ))

    # 調整樣式
    fig.update_layout(
        xaxis_title='時段',
        yaxis_title='星期',
        yaxis=dict(autorange='reversed'),
        height=300,
        font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=60, l=60, r=20)
    )
    fig.update_traces(xgap=3, ygap=3)

    return fig

def get_mode_data(df, mode, comparison_mode):
    """
    根據 mode 和 comparison_mode 篩選資料並計算加權平均
    回傳: dict with keys ['repeat_rate', 'avg_skip_rate', 'new_track_ratio', 'artist_concentration']
    """
    metric_cols = ['repeat_rate', 'avg_skip_rate', 'new_track_ratio', 'artist_concentration']
    
    if comparison_mode == "平日/週末":
        if mode == "Weekday":
            rows = df[(df['day_of_week'].isin([1,2,3,4,5])) & (df['time_period'].isna())]
        else:  # Weekend
            rows = df[(df['day_of_week'].isin([0,6])) & (df['time_period'].isna())]
    
    elif comparison_mode == "時段":
        if mode == "Other periods (avg)":
            # 需要知道 mode1 是什麼，才能排除
            # 這裡先回傳 None，後面特別處理
            return None
        else:
            rows = df[(df['day_of_week'].isna()) & (df['time_period'] == mode)]
    
    elif comparison_mode == "指定星期幾":
        if mode == "Other days (avg)":
            return None
        else:
            day_map = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
            rows = df[(df['day_of_week'] == day_map[mode]) & (df['time_period'].isna())]
    
    # 計算加權平均
    if len(rows) == 0:
        return {col: 0 for col in metric_cols}
    elif len(rows) == 1:
        return rows.iloc[0][metric_cols].to_dict()
    else:
        return {
            col: np.average(rows[col], weights=rows['total_time'])
            for col in metric_cols
        }

def get_other_avg(df, exclude_mode, comparison_mode):
    """計算 Other periods/days 的加權平均（排除 exclude_mode）"""
    metric_cols = ['repeat_rate', 'avg_skip_rate', 'new_track_ratio', 'artist_concentration']
    
    if comparison_mode == "時段":
        time_periods = ["Morning", "Afternoon", "Evening", "Late Night"]
        other_periods = [p for p in time_periods if p != exclude_mode]
        rows = df[(df['day_of_week'].isna()) & (df['time_period'].isin(other_periods))]
    
    elif comparison_mode == "指定星期幾":
        day_map = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
        exclude_day = day_map[exclude_mode]
        other_days = [d for d in range(7) if d != exclude_day]
        rows = df[(df['day_of_week'].isin(other_days)) & (df['time_period'].isna())]
    
    if len(rows) == 0:
        return {col: 0 for col in metric_cols}
    
    return {
        col: np.average(rows[col], weights=rows['total_time'])
        for col in metric_cols
    }


def create_grouped_bar(data1, data2, label1, label2):
    """
    建立 grouped bar chart 比較兩組資料
    data1, data2: dict with keys ['repeat_rate', 'avg_skip_rate', 'new_track_ratio', 'artist_concentration']
    """
    categories = ['重複播放率', '未完成率', '新歌比例', '藝人集中度']
    label_map = {
        "Morning": "早晨", "Afternoon": "下午", "Evening": "晚上", "Late Night": "深夜",
        "Sun": "週日", "Mon": "週一", "Tue": "週二", "Wed": "週三", 
        "Thu": "週四", "Fri": "週五", "Sat": "週六",
        "Weekday": "平日", "Weekend": "週末",
        "Other periods (avg)": "其他時段(平均)",
        "Other days (avg)": "其他天(平均)"
    }
    display_label1 = label_map.get(label1, label1)
    display_label2 = label_map.get(label2, label2)
    
    fig = go.Figure()
    
    # Mode 1
    fig.add_trace(go.Bar(
        name=display_label1,
        x=categories,
        y=[data1['repeat_rate'], data1['avg_skip_rate'], 
           data1['new_track_ratio'], data1['artist_concentration']],
        marker_color="#91A2B3",
        text=[f"{data1['repeat_rate']:.1%}", f"{data1['avg_skip_rate']:.1%}", 
              f"{data1['new_track_ratio']:.1%}", f"{data1['artist_concentration']:.1%}"],
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    # Mode 2
    fig.add_trace(go.Bar(
        name=display_label2,
        x=categories,
        y=[data2['repeat_rate'], data2['avg_skip_rate'], 
           data2['new_track_ratio'], data2['artist_concentration']],
        marker_color="#BADABA",
        text=[f"{data2['repeat_rate']:.1%}", f"{data2['avg_skip_rate']:.1%}", 
              f"{data2['new_track_ratio']:.1%}", f"{data2['artist_concentration']:.1%}"],
        textposition='outside',
        textfont=dict(size=11)
    ))
    
    fig.update_layout(
        barmode='group',
        yaxis=dict(
            title='%',
            tickformat='.0%',
            range=[0, max(
                data1['repeat_rate'], data1['new_track_ratio'], data1['artist_concentration'],
                data2['repeat_rate'], data2['new_track_ratio'], data2['artist_concentration']
            ) * 1.15]  # 留空間給 text labels
        ),
        xaxis=dict(title=''),
        showlegend=True,
        height=400,
        margin=dict(t=20, b=60)
    )
    
    return fig

if __name__ == "__main__":
    # df = (get_time_pattern_summary('2025-10-01', '2026-01-24'))
    # df.to_parquet('../dashboard-demo/data/page2/df.parquest')
    pass