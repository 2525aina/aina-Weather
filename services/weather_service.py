import streamlit as st
import requests
from datetime import datetime

# --- OpenWeatherMap API 設定 ---
OPENWEATHERMAP_API_KEY = st.secrets["openweathermap"]["api_key"]
OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- 天気データ取得関数 ---
def get_weather_data(city_name):
    city_name_normalized = city_name.lower()
    params = {
        "q": city_name_normalized,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric", # 摂氏で取得
        "lang": "ja" # 日本語で取得
    }
    try:
        response = requests.get(OPENWEATHERMAP_BASE_URL, params=params)
        response.raise_for_status() # HTTPエラーがあれば例外を発生させる
        data = response.json()

        if data["cod"] != 200:
            st.error(f"天気データの取得に失敗しました: {data['message']}")
            return None

        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather_main": data["weather"][0]["main"],
            "weather_icon": data["weather"][0]["icon"],
            "rain_1h": data.get("rain", {}).get("1h", 0), # 1時間降水量、なければ0
            "last_update": datetime.now()
        }
        return weather_info
    except requests.exceptions.RequestException as e:
        st.error(f"API通信エラーが発生しました: {e}")
        return None
    except KeyError as e:
        st.error(f"APIレスポンスの解析エラーが発生しました: {e}. レスポンス: {data}")
        return None
