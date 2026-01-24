import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path


liked_songs = pd.read_csv(Path(__file__).parent.parent / "data" / "liked.csv")


def transform_artists(df):
    """
    合併同一首歌的多個歌手，並去重
    輸入: track_id 可能重複的 df
    輸出: track_id 唯一，artist 用逗號連接
    """
    # 處理沒有 added_at 的情況 (frequent_not_liked)
    group_cols = ['id', 'track', 'count']
    if 'added_at' in df.columns:
        group_cols.append('added_at')
    
    return (df.groupby(group_cols, dropna=False)
              .agg({'artist': lambda x: ', '.join(x.dropna())})
              .reset_index()
              .rename(columns={'id': 'track_id'}))


@st.cache_data(ttl=3600)
def get_rate(start_date, end_date, analysis_start, analysis_end):
    """
    計算時間區間內的按讚率、frequent_not_liked rate
    
    Parameters:
    - start_date, end_date: supabase 資料收集範圍
    - analysis_start, analysis_end: 喜歡但少聽
    Returns: (liked_count, total_count)
    """
    liked_songs['added_at'] = pd.to_datetime(liked_songs['added_at'])
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')
    liked_count = liked_songs['added_at'].between(start_date, end_date).sum()

    analysis_start = pd.to_datetime(analysis_start).tz_localize('UTC')  # 自動變成 00:00:00
    analysis_end = pd.to_datetime(analysis_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # 變成 23:59:59
    analysis_end = analysis_end.tz_localize('UTC')
    liked_count_a = liked_songs['added_at'].between(analysis_start, analysis_end).sum()

    return liked_count, liked_count_a



def filter_by_liked_date(df, analysis_start, analysis_end):
    """
    根據 added_at 篩選時間範圍
    """

    df['added_at'] = pd.to_datetime(df['added_at'])
    analysis_start = pd.to_datetime(analysis_start)  # 自動變成 00:00:00
    analysis_end = pd.to_datetime(analysis_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # 變成 23:59:59

    return df[df['added_at'].between(analysis_start, analysis_end)]


def filter_by_long_days(df, long_days):
    """
    篩選「很久以前按讚」的歌
    
    Parameters:
    - df: 包含 added_at 欄位的 df
    - long_days: 定義「很久」= 距今幾天
    """
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=long_days)
    df['added_at'] = pd.to_datetime(df['added_at'])
    return df[df['added_at'] < cutoff_date]


if __name__=="__main__":
    # df_forgotten, df_frequent_not_liked, df = get_all_data(0.5, 0.5)
    # df_forgotten.to_parquet("./data/page4/df_forgotten.parquet")
    # df_frequent_not_liked.to_parquet("./data/page4/df_frequent_not_liked.parquet")
    # df.to_parquet("./data/page4/df.parquet")

    # df_forgotten = pd.read_parquet("./data/page4/df_forgotten.parquet")
    # df_frequent_not_liked = pd.read_parquet("./data/page4/df_frequent_not_liked.parquet")
    # df = pd.read_parquet("./data/page4/df.parquet")

    # bottom = 0.05
    # top = 0.95
    # bottom_threshold = df['count'].quantile(bottom, interpolation='lower')
    # top_threshold = df['count'].quantile(top, interpolation='lower')

    # print(df_forgotten.loc[df_forgotten['count']<=bottom_threshold, :])
    # print(df_frequent_not_liked.loc[df_frequent_not_liked['count']>=top_threshold, :])
    
    pass
