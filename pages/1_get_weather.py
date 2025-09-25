import streamlit as st
from services.weather_service import get_weather_data
from services.firebase_service import save_weather_to_firestore, get_all_cities_from_firestore

st.title("お天気取得")

st.write("指定した都市の天気データを取得し、Firestoreに保存します。")

all_cities_data = get_all_cities_from_firestore()
existing_cities = sorted(list(all_cities_data.keys()))

selected_city_option = st.selectbox(
    "既存の都市を選択",
    ["新しい都市を入力"] + existing_cities,
    index=0 # デフォルトで「新しい都市を入力」を選択
)

if selected_city_option == "新しい都市を入力":
    new_city_input = st.text_input("新しい都市名を入力", "Tokyo")
    city_to_process = new_city_input.lower()
else:
    city_to_process = selected_city_option.lower()

if st.button("天気取得＆保存"):
    if not city_to_process:
        st.warning("都市名を入力してください。")
    else:
        with st.spinner(f"{city_to_process}の天気データを取得中..."):
            weather = get_weather_data(city_to_process)
            if weather:
                st.write("取得データ:", weather)
                save_weather_to_firestore(city_to_process, weather)
