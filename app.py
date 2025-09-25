import streamlit as st

# --- Streamlit UI ---
st.set_page_config(layout="wide")

# --- カスタムCSSの読み込み ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")
st.switch_page("pages/1_get_weather.py")
