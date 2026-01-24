import streamlit as st
import sys, pandas as pd
from pathlib import Path
from utils import apply_pills_style
sys.path.insert(0, str(Path(__file__).parent.parent))
from visualizations.overview import(
    create_listening_heatmap,
    create_topn
)

st.set_page_config(
    page_title="Overview - Spotify Dashboard", 
    page_icon="🎵",
    layout="wide"
)

start_date = pd.to_datetime('2025-10-25').date()
end_date = pd.to_datetime('2026-01-23').date()

if start_date is None or end_date is None:
    st.info("⚠️ 請先去 Home page 選擇日期範圍")
    st.stop()

df_unique_value = pd.read_parquet("./data/page1/df_unique_value.parquet")
df_duration_per_day = pd.read_parquet("./data/page1/df_duration_per_day.parquet")
df1 = pd.read_parquet("./data/page1/df1.parquet")
df2 = pd.read_parquet("./data/page1/df2.parquet")
df3 = pd.read_parquet("./data/page1/df3.parquet")
import json
with open('data/page1/texts.json', 'r', encoding='utf-8') as f:
    texts = json.load(f)
primary_des = texts["primary_des"]
full_des = texts["full_des"]


with st.expander("關於這頁"):
    st.markdown("""              

    這個頁面顯示所選時間範圍內的聆聽摘要。
    
    **上排：**
    - 總聆聽時數、不重複的歌曲/藝人/專輯數量
    - Context 顯示你從哪裡聽歌（播放清單、專輯頁面、藝人首頁）
    
    **下排：**
    - 單日最高：單日聆聽時數最長的日期
    - 循環播放最多：單首歌曲重複播放次數最多
    - 連續聆聽天數：最多連續幾天聆聽同一位藝人
    - 聆聽天數最多：聆聽天數最多的藝人（不需連續）
    - 單日最高藝人：單日花最多時間聆聽某位藝人的紀錄
    
    **聆聽時長：**
    - calendaer heatmap 呈現每天的聆聽量
    - 顏色越深 = 聽得越多
                
    **Top N 排行：**
    - 你最常聽的藝人、歌曲、專輯（依總時長）
    - 可調整顯示數量
    
    """)
with st.sidebar:
    st.info("demo 用，所以名稱 (e.g., 歌名) 都做了去識別化")
st.markdown(f"<h3 style='font-weight: 450;'>時間區間: {start_date} ~ {end_date}</h3>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("總聆聽時數", df_unique_value.loc[0, "total_duration"])
col2.metric("不重複歌曲", df_unique_value.loc[0, "unique_tracks"])
col3.metric("不重複藝人", df_unique_value.loc[0, "unique_artists"])
col4.metric("不重複專輯", df_unique_value.loc[0, "unique_albums"])
col5.metric("聆聽來源", primary_des, help=f"顯示你從哪裡聽歌： \n {full_des}")

# 取得 highlights 資料
path = 'data/page1/'

# 直接讀取並賦值給原有的變數名稱
artist_streak_consecutive = pd.read_parquet(f'{path}artist_streak_consecutive.parquet')
artist_total_days         = pd.read_parquet(f'{path}artist_total_days.parquet')
highest_duration_day      = pd.read_parquet(f'{path}highest_duration_day.parquet')
track_repeat_max          = pd.read_parquet(f'{path}track_repeat_max.parquet')
highest_artist_day        = pd.read_parquet(f'{path}highest_artist_day.parquet')

# 顯示 cards
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

st.markdown("""
<style>
    .hover-card {
        height: 160px;
        padding: 10px;
        display: flex;
        border-radius: 10px;
        flex-direction: column;
        color: black;
        text-align: left;
    }
    .hover-card:hover {
        background: rgba(122, 175, 222, 0.1);  
        border: 1px solid rgba(122, 175, 222, 0.3);
        transform: translateY(-5px);  /* 往上浮 */
        /*box-shadow: 0 4px 12px rgba(0,0,0,0.1);  陰影 */
    }
    .card-bold {
        font-weight: 500;
        font-size: 30px;  
        white-space: nowrap;  /* 強制不換行 */
        overflow: hidden;  /* 超出隱藏 */
        text-overflow: ellipsis;  /* 顯示 ... */
    }
    .card-detail {
        font-size: clamp(12px, 1vw, 18px);  /* 12-18px 自動調整 */
        white-space: nowrap;  /* 強制不換行 */
        overflow: hidden;  /* 超出隱藏 */
        text-overflow: ellipsis;  /* 顯示 ... */
    }
    </style>
""", unsafe_allow_html=True)

with col1:
    st.markdown(f"""
    <div class='hover-card'>
        <div style='font-size: 14px; opacity: 0.9;'> 單日最高 </div>
        <div class='card-bold'>
            {highest_duration_day.loc[0, 'play_date'].strftime('%Y-%m-%d')}
        </div>
        <div class='card-detail'>
            {highest_duration_day.loc[0, 'duration'] / 3600:.1f} hrs
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='hover-card'>
        <div style='font-size: 14px; opacity: 0.9;'> 循環播放最多 </div>
        <div class='card-bold'>
            {track_repeat_max.loc[0, 'repeat_count']} times
        </div>
        <div class='card-detail'>
            {track_repeat_max.loc[0, 'track']}<br>
            {track_repeat_max.loc[0, 'first_played'].strftime('%Y-%m-%d')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='hover-card'>
        <div style='font-size: 14px; opacity: 0.9;'> 連續聆聽天數 <span title='連續聆聽同一位藝人的最長天數' style='cursor: help;'>ⓘ</span></div>
        <div class='card-bold'>
            {artist_streak_consecutive.loc[0, 'consecutive_days']} days
        </div>
        <div class='card-detail'>
            {artist_streak_consecutive.loc[0, 'artist']} <br> 
            {artist_streak_consecutive.loc[0, 'streak_start'].strftime('%m/%d')} -
            {artist_streak_consecutive.loc[0, 'streak_end'].strftime('%m/%d')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""    
    <div class='hover-card'>
        <div style='font-size: 14px; opacity: 0.9;'> 聆聽天數最多 <span title='聆聽天數最多的藝人(不需連續)' style='cursor: help;'>ⓘ</span></div>
        <div class='card-bold'>
            {artist_total_days.loc[0, 'total_days']} days
        </div>
        <div class='card-detail'>
            {artist_total_days.loc[0, 'artist']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='hover-card'>
        <div style='font-size: 14px; opacity: 0.9;'> 單日最高藝人 <span title='單日花最多時間聆聽的藝人' style='cursor: help;'>ⓘ</span></div>
        <div class='card-bold'>
            {highest_artist_day.loc[0, 'play_date'].strftime('%Y-%m-%d')}
        </div>
        <div class='card-detail'>
            {highest_artist_day.loc[0, 'artist']}<br>
            {highest_artist_day.loc[0, 'duration'] / 3600:.1f} hrs
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<br><br>""", unsafe_allow_html=True)
apply_pills_style()
pills_tab = ["聆聽時長", "top n 排行"]
selected_tabs = st.pills(" ", pills_tab,
                         selection_mode="single", default=pills_tab[0], key="main_tabs")
st.markdown("""<hr style='margin-top: -20px; margin-bottom: 5px; border: none; border-top: 2px solid #e8e5e5;'>""", unsafe_allow_html=True)


if selected_tabs == pills_tab[0]:
    with st.expander("自訂顏色", expanded=False):
        col1, _, col2, col3, _ = st.columns([1, 0.2, 1, 1, 0.8])
        with col1:
            size = st.slider("圓點大小", 5, 25, 12)
        with col2:
            color_option = st.radio("顏色模式", ["預設配色", "自訂配色"])
        with col3:
            if color_option == "預設配色":
                scheme = st.selectbox("配色選項", ["藍色（預設）", "綠色", "紫色", "暖色"])
                colors = {
                    "藍色（預設）": ("#e9eff1", "#3B5D7D"),
                    "綠色": ("#dce6dd", "#466E48"),
                    "紫色": ("#e8dcea", "#6b487a"),
                    "暖色": ("#e6e3de", "#AC5C30")
                }
                color_light, color_dark = colors[scheme]
            else:
                col_a, col_b, _, _ = st.columns(4)
                with col_a:
                    color_light = st.color_picker("最淺", "#e9eff1")
                with col_b:
                    color_dark = st.color_picker("最深", "#3B5D7D")

    fig1 = create_listening_heatmap(df_duration_per_day, size, color_light, color_dark)
    st.plotly_chart(fig1, use_container_width=True)



if selected_tabs == pills_tab[1]:
    col1, col2, _ = st.columns(3)
    with col1: genre = st.radio('類型', ['藝人', '歌曲', '專輯'], horizontal=True)
    with col2: number = st.number_input("顯示數量", 5, 100, 10)
    if genre == '藝人': fig4 = create_topn(df1, genre='artist', n=number)
    if genre == '歌曲': fig4 = create_topn(df2, genre='track', n=number)
    if genre == '專輯': fig4 = create_topn(df3, genre='album', n=number)
    st.plotly_chart(fig4, use_container_width=True)


