import streamlit as st
from services.firebase_service import get_all_cities_from_firestore

st.title("📊 ダッシュボード")

all_cities_data = get_all_cities_from_firestore()

if not all_cities_data:
    st.info("まだ都市の天気データがありません。「お天気取得」ページで都市の天気データを取得・保存してください。")
else:
    city_names = list(all_cities_data.keys())
    selected_city = st.selectbox("都市を選択してください", city_names)

    if selected_city:
        weather_data = all_cities_data[selected_city]
        st.subheader(f"{selected_city}の現在の天気")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("気温", f"{weather_data['temperature']:.1f}°C")
            st.metric("湿度", f"{weather_data['humidity']}% ")
        with col2:
            st.metric("風速", f"{weather_data['wind_speed']:.1f} m/s")
            st.metric("降水量 (1h)", f"{weather_data['rain_1h']:.1f} mm")
        with col3:
            # 天気アイコン表示 (OpenWeatherMapのアイコンURLを使用)
            icon_url = f"http://openweathermap.org/img/wn/{weather_data['weather_icon']}@2x.png"
            st.image(icon_url, caption=weather_data['weather_main'])
