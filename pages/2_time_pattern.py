import streamlit as st
import sys, pandas as pd, numpy as np
from pathlib import Path
from utils import apply_pills_style
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizations.time_pattern import (
    calculate_rankings,
    format_time_slot_label,
    get_mode_data, get_other_avg,
    create_sparkline,
    create_full_heatmap,
    create_grouped_bar
)

st.set_page_config(
    page_title="Time Pattern - Spotify Dashboard", 
    page_icon="🎵",
    layout="wide"
)
start_date = pd.to_datetime('2025-10-25').date()
end_date = pd.to_datetime('2026-01-23').date()
st.title("Time Pattern Analysis")
st.markdown(f"時間區間: {start_date} ~ {end_date}")

if start_date is None or end_date is None:
    st.info("⚠️ 請先去 Home page 選擇日期範圍")
    st.stop()
    
df = pd.read_parquet("./data/page2/df.parquest")
df_detail = calculate_rankings(df)
df_detail['label'] = df_detail.apply(format_time_slot_label, axis=1)

# Total Duration
top_total = df_detail.loc[df_detail['total_time_rank'] == 1].iloc[0]
total_sparkline_data = df_detail['total_time'].tolist()
total_sparkline_labels = df_detail['label'].tolist()

# Skip Rate
top_skip = df_detail.loc[df_detail['skip_rate_rank'] == 1].iloc[0]
skip_sparkline_data = df_detail['avg_skip_rate'].tolist()
skip_sparkline_labels = df_detail['label'].tolist()

# New Track Ratio
top_new_track = df_detail.loc[df_detail['new_track_rank'] == 1].iloc[0]
new_track_sparkline_data = df_detail['new_track_ratio'].tolist()
new_track_sparkline_labels = df_detail['label'].tolist()

# Session Time
top_session = df_detail.loc[df_detail['session_time_rank'] == 1].iloc[0]
session_sparkline_data = df_detail['avg_session_time'].tolist()
session_sparkline_labels = df_detail['label'].tolist()

# Session Time
top_artist_concentration = df_detail.loc[df_detail['artist_concentration_rank'] == 1].iloc[0]
artist_sparkline_data = df_detail['artist_concentration'].tolist()
artist_sparkline_labels = df_detail['label'].tolist()

# 取 track level 的平均 (也就是找 group by cube() 兩個都是 none 的)
df_avg_total = df.loc[df['day_of_week'].isna() & df['time_period'].isna()].iloc[0]

# 24 個 slot 算加權平均 (權重=時長)
df2 = df[df['day_of_week'].notna() & df['time_period'].notna()]
weighted_avg = {
    'artist_concentration': np.average(df2['artist_concentration'], weights=df2['total_time']),
    'repeat_rate': np.average(df2['repeat_rate'], weights=df2['total_time'])
}

with st.expander("關於這頁"):
    st.markdown("""               

    此頁面顯示你在不同時段的聆聽模式。

    **上方指標卡片：**
    - 總聆聽時長：顯示你最常聽音樂的時段
    - 未完成率：歌曲未聽完的比例平均（每首歌個別計算後平均）
    - 新歌比例：第一次聽的新歌比例
    - 藝人集中度：聆聽時長集中在前 3 名藝人的比例

    **左下方 聆聽模式比較**：比較不同時段（平日/週末、時段、指定星期幾）的聆聽習慣差異
    - 重複播放率：同一首歌聽多次的比例
    - 未完成率：歌曲未聽完的比例
    - 新歌比例：新歌探索比例
    - 藝人集中度：聆聽集中度
    
    **右下方 Heatmap**：以熱力圖顯示每週各時段的聆聽分布
    - 顏色越深 = 該時段聆聽時間越長
    - 可切換不同變數觀察模式

    """)

col1, col2, col3, col4 = st.columns(4)

# Card 1: Total Duration
with col1:
    st.metric(
        label="總聆聽時長",
        value=f"{df_avg_total['total_time'] / 3600:.1f} hrs total",
    )
    
    fig1 = create_sparkline(
        sum(total_sparkline_data)/24/3600,
        [x / 3600 for x in total_sparkline_data],
        total_sparkline_labels,
        color="#67809A",fillcolor='rgba(119, 136, 193, 0.2)',
        title='Duration'
    )
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

# Card 2: Skip Rate
with col2:
    st.metric(
        label="未完成率",
        value=f"{ df_avg_total['avg_skip_rate'] * 100:.1f}% overall",
        help="歌曲未聽完的比例平均（每首歌個別計算後平均）"
    )
    
    fig2 = create_sparkline(
        df_avg_total['avg_skip_rate']*100,
        [x * 100 for x in skip_sparkline_data],  # 轉成百分比
        skip_sparkline_labels,
        color='#8FBC8F',fillcolor='rgba(143, 188, 143, 0.2)',
        title='Skip Rate %'
    )
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# Card 3: New Track Ratio
with col3:
    st.metric(
        label="新歌比例",
        value=f"{df_avg_total['new_track_ratio'] * 100:.1f}%",
        help = "第一次聽的新歌比例"
    )
    
    fig3 = create_sparkline(
        df_avg_total['new_track_ratio']*100,
        [x * 100 for x in new_track_sparkline_data],
        new_track_sparkline_labels,
        color='#8267B8', fillcolor='rgba(130, 103, 184, 0.2)',
        title='New Track %'
    )
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

# Card 4: Session Time
with col4:
    st.metric(
        label="藝人集中度",
        value=f"{df_avg_total['artist_concentration'] * 100} % overall",
        help = "聆聽時長集中在前 3 名藝人的比例"
    )

    fig4 = create_sparkline(
        weighted_avg['artist_concentration']*100,
        [x*100 for x in artist_sparkline_data],  # 轉成分鐘
        artist_sparkline_labels,
        color='#CD853F',fillcolor='rgba(205, 133, 63, 0.2)',
        title="Artist Concentration %"
    )
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})


st.markdown("<br>", unsafe_allow_html=True)
colL, colR = st.columns([1, 1])

with colL:
    st.subheader("模式比較")
    options = ["平日/週末", "時段", "指定星期幾"]
    comparison_mode = st.radio("比較選項:", options, horizontal=True)

    if comparison_mode == options[0]:
        mode1 = "Weekday"
        mode2 = "Weekend"
        
    elif comparison_mode == options[1]:
        col1, col2 = st.columns(2)
        time_periods = ["Morning", "Afternoon", "Evening", "Late Night"]
        time_labels = ["早晨", "下午", "晚上", "深夜"]
        
        with col1: 
            mode1_label = st.selectbox("第一時段：", time_labels, index=None)
            mode1 = time_periods[time_labels.index(mode1_label)] if mode1_label else None
        with col2: 
            mode2_label = st.selectbox("第二時段：", ["其他時段(平均)"] + time_labels, index=None)
            if mode2_label == "其他時段(平均)":
                mode2 = "Other periods (avg)"
            elif mode2_label:
                mode2 = time_periods[time_labels.index(mode2_label)]
            else:
                mode2 = None
        
        if mode1 == mode2 and mode1 is not None:
            st.info("ℹ️ 選擇了相同時段 - 顯示單一時段")
        
    elif comparison_mode == options[2]:
        col1, col2 = st.columns(2)
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        day_labels = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]
        
        with col1:
            mode1_label = st.selectbox("第一天：", day_labels, index=None)
            mode1 = days[day_labels.index(mode1_label)] if mode1_label else None
        with col2:
            mode2_label = st.selectbox("第二天：", ["其他天(平均)"] + day_labels, index=None)
            if mode2_label == "其他天(平均)":
                mode2 = "Other days (avg)"
            elif mode2_label:
                mode2 = days[day_labels.index(mode2_label)]
            else:
                mode2 = None

        if mode1 == mode2 and mode1 is not None:
            st.info("ℹ️ 選擇了相同日期 - 顯示單一日期")
    
    if mode1 is not None and mode2 is not None:
        # 取得資料
        data1 = get_mode_data(df, mode1, comparison_mode)
        
        if mode2 in ["Other periods (avg)", "Other days (avg)"]:
            data2 = get_other_avg(df, mode1, comparison_mode)
        else:
            data2 = get_mode_data(df, mode2, comparison_mode)
        
        # 畫 grouped bar
        fig = create_grouped_bar(data1, data2, mode1, mode2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("請選擇兩個時段/日期進行比較")
    

with colR:
    st.subheader("heatmap")
    selected_var_char = st.radio(
        "選擇一個變數:",
        ["播放時長", "未完成率", "新歌比例", "藝人集中度", '重複播放率'],
        horizontal=True
    )
    mapping = {"播放時長": 'total_time', "未完成率": 'avg_skip_rate', "新歌比例": 'new_track_ratio', "藝人集中度": 'artist_concentration', '重複播放率': 'repeat_rate'}
    selected_var = mapping[selected_var_char]
    configs = {
        'total_time': {
            'title': 'Listening Duration by Time Slot',
            'colorbar_title': 'Hours',
            'unit': 'hrs',
            'hover_label': 'Total Duration',
            'hover_format': ':.1f',
            'colorscale': [[0.0, "#D7E3F0"], [1.0, "#5C748D"]]
        },
        'avg_skip_rate': {
            'title': 'Skip Rate by Time Slot',
            'colorbar_title': 'Skip Rate',
            'unit': '%',
            'hover_label': 'Skip Rate',
            'hover_format': ':.1%',
            'colorscale': [[0.0, "#E0F1E0"], [1.0, "#689468"]]  
        },
        'new_track_ratio': {
            'title': 'New Track Exploration by Time Slot',
            'colorbar_title': 'New Track %',
            'unit': '%',
            'hover_label': 'New Track Ratio',
            'hover_format': ':.1%',
            'colorscale': [[0.0, "#D9D3E5"], [1.0, "#695395"]]  
        },
        'artist_concentration': {
            'title': 'Artist Concentration by Time Slot',
            'colorbar_title': 'Concentration',
            'unit': '%',
            'hover_label': 'Artist Concentration',
            'hover_format': ':.1%',
            'colorscale': [[0.0, "#EEE6DE"], [1.0, '#CD853F']]  
        },
        'repeat_rate': {
            'colorbar_title': 'Concentration',
            'unit': '%',
            'hover_label': 'Artist Concentration',
            'hover_format': ':.1%',
            'colorscale': [[0.0, "#EEE6DE"], [1.0, '#CD853F']]  
        }
    }

    fig = create_full_heatmap(df, selected_var, configs[selected_var])
    st.plotly_chart(fig, use_container_width=True)