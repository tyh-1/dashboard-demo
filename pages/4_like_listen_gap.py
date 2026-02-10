import streamlit as st
import sys, pandas as pd, random
from pathlib import Path
from visualizations.like_listen_gap import (
    get_rate,
    filter_by_liked_date,
    filter_by_long_days
)
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Like Listen Gap - Spotify Dashboard", 
    page_icon="🎵",
    layout="wide"
)

start_date = pd.to_datetime('2025-10-25 00:00')
end_date = pd.to_datetime('2026-01-23 23:59')

# ===== Session State 初始化 =====
if 'forgotten_idx' not in st.session_state:
    st.session_state['forgotten_idx'] = 0
if 'frequent_idx' not in st.session_state:
    st.session_state['frequent_idx'] = 0
if 'long_idx' not in st.session_state:
    st.session_state['long_idx'] = 0

if 'displayed_forgotten' not in st.session_state:
    st.session_state['displayed_forgotten'] = pd.DataFrame()
if 'displayed_frequent' not in st.session_state:
    st.session_state['displayed_frequent'] = pd.DataFrame()
if 'displayed_long' not in st.session_state:
    st.session_state['displayed_long'] = pd.DataFrame()

st.title("What you like vs. What you listen")
with st.expander("關於這頁"):
    st.markdown("""
    ### 這一頁在做什麼？
    
    你按讚的 ≠ 你真正在聽的，這頁嘗試找出這些有趣的落差。
    
    ---
    
    ### 三個區塊在看什麼？
    
    **按讚但少聽**  
    那些你在特定時間內按了讚，但播放次數卻落在「少聽」區塊（後 X%）的歌。
    - 可能是：當下很喜歡，但後來忘記了
    - 可調整：按讚時間範圍、少聽門檻
                
    **常聽但未按讚**  
    播放次數在「常聽」區塊（前 X%），但你從來沒按過讚的歌。
    - 可能是：沒發現自己這麼愛、很適合當背景音樂
    - 可調整：常聽門檻
    
    **回味經典**
    很久以前（距今 X 天）按讚的歌，現在還在你的「常聽」清單裡。
    - 可能是：經典不敗
    - 可調整：「很久」的定義、常聽門檻
    
    ---
    
    *如果某些區塊沒有結果，代表你的按讚跟播放很一致*
    """)

# ===== Sidebar: 全域參數 =====
with st.sidebar:
    st.info("demo 用，所以名稱 (e.g., 歌名) 都做了去識別化")
    st.subheader("門檻設定")
    top = st.number_input("常聽門檻 (Top %)", 0.0, 50.0, 1.0, 0.5, format="%.1f")/100.0
    bottom = st.number_input("少聽門檻 (Bottom %)", 0.0, 50.0, 5.0, 0.5, format="%.1f")/100.0

    st.divider()
    
    st.subheader("按讚時間篩選")
    st.caption(f"只影響「按讚但少聽」分析") 
    st.caption(f"資料蒐集期間：{start_date} ~ {end_date}")

    col1, col2 = st.columns(2)
    with col1:
        analysis_start = st.date_input(
            "開始",
            value = pd.to_datetime(start_date) - pd.Timedelta(days=90),
            min_value = pd.to_datetime(start_date) - pd.Timedelta(days=365),
            max_value = pd.to_datetime(start_date)
        )
    with col2:
        analysis_end = st.date_input(
            "結束",
            value = pd.to_datetime(end_date) - pd.Timedelta(days=5),
            min_value = pd.to_datetime(start_date),
            max_value = pd.to_datetime(end_date)
        )
    
    # st.caption(f"分析範圍：{analysis_start} ~ {analysis_end}")
    
    with st.expander("為什麼要設定按讚時間範圍？"):
        st.markdown("""
        - **排除太新的按讚**：最近才按讚的歌，播放次數少可能會偏少 (根據個人習慣有所不同)
        - **排除太舊的按讚**：資料蒐集前按讚的歌，無法追蹤完整聆聽紀錄
        """)


top = 1 - top  # 轉換成百分位
bottom = bottom

# ===== 載入所有資料 =====
df_forgotten_raw = pd.read_parquet("./data/page4/df_forgotten.parquet")
df_frequent_not_liked_raw = pd.read_parquet("./data/page4/df_frequent_not_liked.parquet")
df = pd.read_parquet("./data/page4/df.parquet")
bottom_threshold = df['count'].quantile(bottom, interpolation='lower')
top_threshold = df['count'].quantile(top, interpolation='lower')

df_forgotten = df_forgotten_raw.loc[df_forgotten_raw['count']<=bottom_threshold, :]
df_frequent_not_liked = df_frequent_not_liked_raw.loc[df_frequent_not_liked_raw['count']>=top_threshold, :]

df_forgotten_filtered = filter_by_liked_date(df_forgotten, analysis_start, analysis_end)
df_forgotten_sorted = df_forgotten_filtered.sort_values('count', ascending=False).reset_index(drop=True)
df_frequent_sorted = df_frequent_not_liked.sort_values('count', ascending=False).reset_index(drop=True)


# ===== 計算 Metrics =====
liked_count, liked_count_a = get_rate(start_date, end_date, analysis_start, analysis_end)
total_count = 1532
top_region_count = (df['count']>=top_threshold).sum()

col1, col2, col3 = st.columns(3)
col1.metric(label="按讚但少聽比例", value=f"{(len(df_forgotten_filtered)/liked_count_a)*100:.1f}%")
col2.metric(label="常聽未按讚比例", value=f"{(len(df_frequent_not_liked)/top_region_count)*100:.1f}%")
col3.metric(label="按讚的比例", value=f"{(liked_count/total_count)*100:.1f}%", help="基於聆聽資料蒐集時間計算，不隨側欄篩選變動")

# ===== CSS Styling =====
st.markdown("""
<style>
    .hover-card {
        height: 160px;
        padding: 15px;
        margin: 10px 0;
        display: flex;
        border-radius: 10px;
        flex-direction: column;
        color: black;
        text-align: left;
        background: white;
        border: 1px solid #e0e0e0;
    }
    .hover-card:hover {
        background: rgba(122, 175, 222, 0.1);  
        border: 1px solid rgba(122, 175, 222, 0.5);
        transform: translateY(-3px);
        transition: all 0.2s;
    }
    .card-artist {
        font-size: 14px;
        opacity: 0.7;
        margin-bottom: 5px;
    }
    .card-title {
        font-weight: 600;
        font-size: 24px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 10px;
    }
    .card-detail {
        font-size: 14px;
        color: #666;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)

# ===== Helper Functions =====
def display_cards(df, count=3):
    """顯示 cards"""
    if len(df) == 0:
        st.warning("沒有符合條件的歌曲")
        return
    
    for _, row in df.head(count).iterrows():
        # 格式化 added_at
        added_date = pd.to_datetime(row['added_at']).strftime('%Y-%m-%d') if 'added_at' in row else "N/A"
        
        st.markdown(f"""
        <div class='hover-card'>
            <div class='card-artist'>{row['artist']}</div>
            <div class='card-title'>{row['track']}</div>
            <div class='card-detail'>按讚於 {added_date} · 播放 {row['count']} 次</div>
        </div>
        """, unsafe_allow_html=True)

def display_cards_frequent(df, count=3):
    """顯示 frequent not liked cards (無 added_at)"""
    if len(df) == 0:
        st.warning("沒有符合條件的歌曲")
        return
    
    for _, row in df.head(count).iterrows():
        st.markdown(f"""
        <div class='hover-card'>
            <div class='card-artist'>{row['artist']}</div>
            <div class='card-title'>{row['track']}</div>
            <div class='card-detail'>播放 {row['count']} 次 · 尚未按讚</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
col1, col2, col3 = st.columns(3)

# ===== Section 1: Forgotten Like =====
with col1:
    st.header("按讚但少聽")
    st.caption(f"{analysis_start} ~ {analysis_end} 按讚的歌 & 聆聽量整體後 {(bottom*100):.1f} %")

    col_btn1, col_btn2 = st.columns([1, 2.5])

    button_label = f"再顯示 3 首" if st.session_state['forgotten_idx'] > 0 else "顯示 3 首"
    
    if col_btn1.button(button_label, key="btn_forgotten_refresh"):
        start_idx = st.session_state['forgotten_idx']
        end_idx = start_idx + 3
        
        if start_idx >= len(df_forgotten_sorted):
            st.session_state['remaining_count_forgotten'] = 0
            st.session_state['show_no_more_forgotten'] = True
        else:
            cards = df_forgotten_sorted.iloc[start_idx:end_idx]
            st.session_state['displayed_forgotten'] = cards
            st.session_state['forgotten_idx'] = end_idx
            
            remaining = len(df_forgotten_sorted) - end_idx
            st.session_state['remaining_count_forgotten'] = remaining 
            st.session_state['show_no_more_forgotten'] = False
            
        st.rerun()

    else:
        # 顯示卡片
        if not st.session_state['displayed_forgotten'].empty:
            display_cards(st.session_state['displayed_forgotten'])
        
        # 顯示剩餘數量
        if st.session_state.get('show_no_more_forgotten', False):
            st.info("已經沒有更多歌曲了！")
        elif st.session_state.get('remaining_count_forgotten', 0) > 0:
            st.caption(f"剩餘 {st.session_state['remaining_count_forgotten']} 首")

    if col_btn2.button("重置", key="btn_forgotten_reset"):
        st.session_state['forgotten_idx'] = 0
        st.session_state['displayed_forgotten'] = pd.DataFrame()
        st.session_state['remaining_count_forgotten'] = 0
        st.session_state['show_no_more_forgotten'] = False
        st.rerun()
    


# ===== Section 2: Frequent Not Liked =====
with col2:
    st.header("常聽但未按讚")
    st.caption(f"未按讚的歌 & 聆聽量整體前 {(1-top)*100:.1f} %")
    col_btn3, col_btn4 = st.columns([1, 2.5])

    button_label = f"再顯示 3 首" if st.session_state['frequent_idx'] > 0 else "顯示 3 首"
    
    if col_btn3.button(button_label, key="btn_frequent_refresh"):
        start_idx = st.session_state['frequent_idx']
        end_idx = start_idx + 3
        
        if start_idx >= len(df_frequent_sorted):
            st.session_state['remaining_count_frequent'] = 0
            st.session_state['show_no_more_frequent'] = True
        else:
            cards = df_frequent_sorted.iloc[start_idx:end_idx]
            st.session_state['displayed_frequent'] = cards  
            st.session_state['frequent_idx'] = end_idx

            remaining = len(df_frequent_sorted) - end_idx
            st.session_state['remaining_count_frequent'] = remaining  # ← 存起來
            st.session_state['show_no_more_frequent'] = False            

        st.rerun()
    
    else:
        if not st.session_state['displayed_frequent'].empty:
            display_cards_frequent(st.session_state['displayed_frequent'])

        # 顯示剩餘數量
        if st.session_state.get('show_no_more_frequent', False):
            st.info("已經沒有更多歌曲了！")
        elif st.session_state.get('remaining_count_frequent', 0) > 0:
            st.caption(f"剩餘 {st.session_state['remaining_count_frequent']} 首")
    
    if col_btn4.button("重置", key="btn_frequent_reset"):
        st.session_state['frequent_idx'] = 0
        st.session_state['displayed_frequent'] = pd.DataFrame()
        st.session_state['remaining_count_frequent'] = 0
        st.session_state['show_no_more_frequent'] = False
        st.rerun()
    

# ===== Section 3: Long Love =====
with col3: 
    st.header("回味經典")
    
    col_top, col_bottom = st.columns(2)
    top_sec3 = col_top.number_input("常聽門檻 - Top %", 0.0, 50.0, 5.0, 0.5, format="%.1f", key='top_percent_sec3')/100.0
    top_sec3 = 1-top_sec3
    long_days = col_bottom.number_input("定義「很久」= 距今幾天", min_value=30, max_value=1500, value=180, step=5)
    st.caption(f"{long_days} 天前按讚 & 聆聽量佔整體 {(1-top_sec3)*100:.1f} %")

    # Filter
    df_long_raw = pd.read_parquet("./data/page4/df_long.parquet")
    top_sec3_threshold = df['count'].quantile(top_sec3, interpolation='lower')
    df_long = df_long_raw.loc[df_long_raw['count']>=top_sec3_threshold, :]
    df_long_filtered = filter_by_long_days(df_long, long_days)
    df_long_sorted = df_long_filtered.sort_values('added_at').reset_index(drop=True)

    col_btn5, col_btn6 = st.columns([1, 2.5])

    button_label = f"再顯示 3 首" if st.session_state['long_idx'] > 0 else "顯示 3 首"
    
    if col_btn5.button(button_label, key="btn_long_refresh"):
        start_idx = st.session_state['long_idx']
        end_idx = start_idx + 3        
        
        if start_idx >= len(df_long_sorted):
            st.session_state['remaining_count_long'] = 0
            st.session_state['show_no_more_long'] = True
        else:
            cards = df_long_sorted.iloc[start_idx:end_idx]
            st.session_state['displayed_long'] = cards  
            st.session_state['long_idx'] = end_idx

            remaining = len(df_long_sorted) - end_idx
            st.session_state['remaining_count_long'] = remaining  
            st.session_state['show_no_more_long'] = False
            
        st.rerun()
    
    else:
        if not st.session_state['displayed_long'].empty:
            display_cards(st.session_state['displayed_long'])

        if st.session_state.get('show_no_more_long', False):
            st.info("已經沒有更多歌曲了！")
        elif st.session_state.get('remaining_count_long', 0) > 0:
            st.caption(f"剩餘 {st.session_state['remaining_count_long']} 首")
    
    if col_btn6.button("重置", key="btn_long_reset"):
        st.session_state['long_idx'] = 0
        st.session_state['displayed_long'] = pd.DataFrame()
        st.session_state['remaining_count_long'] = 0
        st.session_state['show_no_more_long'] = False
        st.rerun()