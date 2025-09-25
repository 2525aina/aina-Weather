import streamlit as st
import time
from services.weather_service import get_weather_data
from services.firebase_service import save_weather_to_firestore, get_all_cities_from_firestore, delete_city_from_firestore
from services.sidebar_utils import normalize_city_name_for_storage

# ... (省略) ...

st.title("お天気取得")

st.write("指定した都市の天気データを取得し、Firestoreに保存します。")

# --- 都市の追加/更新 ---
all_cities_data = get_all_cities_from_firestore()
existing_cities = sorted(list(all_cities_data.keys()))

selected_city_option = st.selectbox(
    "既存の都市を選択",
    ["新しい都市を入力"] + existing_cities,
    index=0 # デフォルトで「新しい都市を入力」を選択
)

if selected_city_option == "新しい都市を入力":
    new_city_input = st.text_input("新しい都市名を入力", "Tokyo")
    city_to_process = normalize_city_name_for_storage(new_city_input)
else:
    city_to_process = normalize_city_name_for_storage(selected_city_option)

if st.button("天気取得＆保存"):
    if not city_to_process:
        st.session_state.message = {"type": "warning", "content": "都市名を入力してください。"}
        st.rerun()
    else:
        with st.spinner(f"{city_to_process}の天気データを取得中..."):
            weather = get_weather_data(city_to_process)
            if weather:
                st.write("取得データ:", weather)
                save_weather_to_firestore(city_to_process, weather)

# --- 都市の削除 ---
st.markdown("--- ")
st.subheader("都市データの削除")

if existing_cities:
    city_to_delete = st.selectbox("削除する都市を選択", existing_cities)
    if st.button("選択した都市を削除", type="secondary"):
        message_result = delete_city_from_firestore(city_to_delete)
        st.session_state.message = message_result
        st.rerun() # 削除後にページを再読み込みしてリストを更新
else:
    st.info("削除できる都市データがありません。")

# メッセージ表示ロジック
if "message" in st.session_state and st.session_state.message:
    message_type = st.session_state.message["type"]
    message_content = st.session_state.message["content"]
    if message_type == "success":
        st.success(message_content)
    elif message_type == "error":
        st.error(message_content)
    elif message_type == "warning":
        st.warning(message_content)
    st.session_state.message = None # メッセージを表示したらクリア
