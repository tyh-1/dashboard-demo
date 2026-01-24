import streamlit as st
import sys, pandas as pd
from pathlib import Path
from utils import apply_pills_style
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizations.album_completion import (
    create_album_treemap,
    create_marathon_listen
)

st.set_page_config(
    page_title="Album Completion - Spotify Dashboard", 
    page_icon="🎵",
    layout="wide"
)
start_date = pd.to_datetime('2025-10-25 00:00')
end_date = pd.to_datetime('2026-01-23 23:59')

st.title("Album Completion Analysis")
st.markdown(f"時間區間: {start_date} ~ {end_date}")

with st.sidebar:
    st.info("demo 用，所以名稱 (e.g., 歌名) 都做了去識別化")
    prop = st.sidebar.slider("完成度門檻 [完成專輯]", min_value=0.0, max_value=1.0, value=1.0, step=0.05, format="%.2f", 
                             help="計算為已完成專輯所需的最低播放曲目比例")
    prop2 = st.sidebar.slider("完成度門檻 [馬拉松聆聽]", min_value=0.0, max_value=1.0, value=1.0, step=0.05, format="%.2f")

if start_date is None or end_date is None:
    st.info("⚠️ 請先去 Home page 選擇日期範圍")
    st.stop()

df_duration_raw = pd.read_parquet("./data/page3/df_duration.parquet")
df_duration = df_duration_raw.loc[df_duration_raw['prop'] >= prop, :]
df_marathon_raw = pd.read_parquet("./data/page3/df_marathon.parquet")
df_marathon = df_marathon_raw.loc[df_marathon_raw['unique_tracks'] >= df_marathon_raw['total_tracks']*prop2, :]
fig1 = create_album_treemap(df_duration)

with st.expander("關於這頁"):
    st.markdown("""               

    這個頁面顯示你完整聽完專輯的紀錄。
    
    **兩個分頁：**
    
    **1. 完成專輯（treemap）：**
    - 顯示你已完成的專輯（可在側邊欄調整「完成」的定義）
    - 預設：播放完專輯所有曲目即視為完成
    - 區塊越大 = 該專輯聆聽時間越長
    - 可在下方表格查看詳細資訊
    
    **2. 馬拉松聆聽（scatter plot）：**
    - 在單次連續聆聽中從頭到尾播放完的專輯
    - 每個點代表一次完整播放
    
    **自訂設定：**
    - 使用側邊欄滑桿調整多少比例算「完成」
    - 調整馬拉松聆聽顯示的專輯數量

    """)

apply_pills_style()
pills_tab = ["完成專輯", "馬拉松聆聽"]
selected_tabs = st.pills(" ", pills_tab,
                         selection_mode="single", default=pills_tab[0], key="main_tabs")
st.markdown("""<hr style='margin-top: -20px; margin-bottom: 5px; border: none; border-top: 2px solid #e8e5e5;'>""", unsafe_allow_html=True)


if selected_tabs == pills_tab[0]:
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': True})
    with st.expander("View Detailed Data"):
        st.dataframe(
            df_duration[['album', 'main_artists', 'total_duration']].rename(columns={
                'main_artists': 'artist(s)',
                'total_duration': 'listening time'
            }),
            use_container_width=True,
            hide_index=True
        )

if selected_tabs == pills_tab[1]:
    top_n = st.slider(
        "顯示專輯數量上限",
        min_value=10,
        max_value=40,
        value=20,
        key='marathon_top_n' 
    )

    st.markdown(f"**連續聆聽紀錄** (專輯完播率 ≥ {prop2*100:.0f}%)  \n*顏色代表完成次數*")
    album_counts = df_marathon.groupby('album').size().reset_index(name='count')
    top_albums = album_counts.nlargest(top_n, 'count')['album']
    df_display = df_marathon[df_marathon['album'].isin(top_albums)]

    # 截斷名稱
    df_display['album_short'] = df_display['album'].apply(
        lambda x: x if len(x) <= 20 else x[:19] + '...'
    )

    df_display['play_count'] = df_display.groupby('album')['album'].transform('count')
    fig2 = create_marathon_listen(df_display)
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': True})