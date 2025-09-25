import streamlit as st
from services.weather_service import get_weather_data
from services.firebase_service import save_weather_to_firestore

st.title("お天気取得")

st.write("指定した都市の天気データを取得し、Firestoreに保存します。")

test_city = st.text_input("都市名を入力", "Tokyo")
if st.button("天気取得＆保存"):
    with st.spinner(f"{test_city}の天気データを取得中..."):
        weather = get_weather_data(test_city)
        if weather:
            st.write("取得データ:", weather)
            save_weather_to_firestore(test_city, weather)
