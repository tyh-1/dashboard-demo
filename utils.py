import streamlit as st

def apply_pills_style():
    """Apply custom CSS for pills to look like tabs"""
    st.markdown("""
    <style>       
        /* 容器下加底線(非滿版) */
        div[data-baseweb="button-group"] {
            /*border-bottom: 2.5px solid #e0e0e0;*/
            /*padding-bottom: 0;*/
            margin-top: -40px !important;
        } 
            
        /* Pills 按鈕 */
        button[data-testid="stBaseButton-pills"] {
            border-radius: 0 !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            background: transparent !important;
            color: #666 !important;
            padding: 12px 24px !important;
            margin-bottom: 0 !important;
        }
        button[data-testid="stBaseButton-pills"] p {
            font-size: 16px !important;
        }
            
        /* Hover 效果 */
        button[data-testid="stBaseButton-pills"]:hover {
            background: transparent !important;
            color: #FF4B4B !important;
        }
        
        /* 選中的 pill */
        button[kind="pillsActive"] {
            border: none !important;
            /*padding-bottom: 12px !important; */
            border-radius: 0 !important;
            color: #FF4B4B !important;
            background: transparent !important;
            font-weight: 1000 !important;

            transform: none !important;
            box-shadow: none !important;
        }
            
        button[data-testid="stBaseButton-pillsActive"] p {
            font-weight: 800 !important;
            font-size: 16px !important;
        }

        button[kind="pillsActive"]:hover {
            color: #FF4B4B !important;
            background: transparent !important;
        }

        /* 移除按下去的位移效果*/
        button[data-testid="stBaseButton-pills"]:active {
            transform: none !important;
            box-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)