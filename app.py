import streamlit as st

# --- Streamlit UI ---
st.set_page_config(
    page_title="Aina Weather App",
    page_icon="🌦️",
    layout="wide"
)

# --- カスタムCSSの読み込み ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# --- メインページのコンテンツ ---
st.title("🌦️ Aina Weather Appへようこそ！")
st.sidebar.success("上のメニューからページを選択してください。")

st.markdown(
    """
    このアプリケーションは、気象データを活用した様々な機能を提供します。
    
    **主な機能:**
    - **天気取得:** 指定した都市の現在の天気情報を取得し、保存します。
    - **ダッシュボード:** 保存した各都市の最新の天気情報を一覧で表示します。
    - **データ可視化:** 蓄積された過去の天気データをグラフで可視化します。
    - **お天気ゲーム:** 天気に関する簡単なゲームを楽しめます。
    
    左のサイドバーから利用したい機能を選択してください。
    """
)