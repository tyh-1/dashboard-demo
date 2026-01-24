import streamlit as st
import pandas as pd
pd.options.mode.copy_on_write = True 

# ===== 頁面設定 =====
st.set_page_config(
    page_title="Spotify Dashboard", page_icon="🎵",
    layout="wide"  # 寬版面
)


# min_date, max_date = get_date_range()    
min_date = pd.to_datetime('2025-10-25').date()
max_date = pd.to_datetime('2026-01-23').date()


# ===== 首頁內容 =====
st.title("Spotify Listening Analysis Dashboard - demo")

st.info("demo 版本為了快速顯示結果，不支援時間篩選")

st.markdown("---")

st.markdown(f"""
**可用分析**

- **總覽**：聆聽活動概況、每日熱力圖、熱門藝人/歌曲/專輯
- **時段聆聽模式**：平日 vs 週末、早上 vs 晚上，你的聆聽習慣有何不同？ 
- **專輯完成度**：找出你聽完的專輯與完整聆聽時段
- **按讚 vs 播放落差**：按讚的 = 真正在聽的？找出可能的有趣落差

""")

st.markdown("---")


# ===== Sidebar 全域設定（所有頁面共用）=====
with st.sidebar:

    st.markdown(f"### 📅 分析時間區間：`{min_date}` — `{max_date}`")
    
    # if len(date_range) == 2:
    #     start_date, end_date = date_range
        
        # 儲存到 session_state
    st.session_state['start_date'] = min_date
    st.session_state['end_date'] = max_date
    
    st.sidebar.markdown("*All times in UTC+8 (Taipei)*")
    
