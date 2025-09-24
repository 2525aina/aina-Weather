import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

# --- Firebase 初期化 ---
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- Firebase Authentication (匿名ログイン) ---
@st.cache_resource
def get_current_user():
    # StreamlitのセッションステートでユーザーIDを管理
    if "user_id" not in st.session_state:
        try:
            # 匿名ユーザーを作成または既存のセッションを再利用
            user = auth.create_user(uid=None) # uid=Noneで匿名ユーザーを作成
            st.session_state.user_id = user.uid
            st.session_state.is_new_user = True
            st.sidebar.success(f"新しい匿名ユーザーとしてログインしました！UID: {user.uid}")
        except Exception as e:
            # 既存の匿名セッションがある場合、それを再利用
            # Streamlitの再実行でユーザーが再作成されないようにする
            # ここでは簡易的にエラーとして表示するが、実際はセッション管理をより厳密に行う
            st.session_state.user_id = "anonymous_user_fallback"
            st.sidebar.warning(f"匿名ユーザーの作成に失敗しました。既存のセッションを使用します。エラー: {e}")
            # 実際のアプリでは、ここで既存の匿名ユーザーをロードするロジックが必要
            # 例: auth.get_user_by_email('anonymous@example.com') など
    return st.session_state.user_id

current_user_id = get_current_user()
st.sidebar.write(f"現在のユーザーID: {current_user_id}")

# --- Firestoreからユーザーデータを取得または作成する関数 ---
def get_or_create_user_profile(user_id):
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    else:
        # 新規ユーザーの場合、プロフィールを作成
        initial_profile = {
            "name": f"User_{user_id[:5]}", # 簡易的なユーザー名
            "points": 0,
            "last_login": datetime.now()
        }
        user_ref.set(initial_profile)
        return initial_profile

current_user_profile = get_or_create_user_profile(current_user_id)

# --- OpenWeatherMap API 設定 ---
OPENWEATHERMAP_API_KEY = st.secrets["openweathermap"]["api_key"]
OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- 天気データ取得関数 ---
def get_weather_data(city_name):
    params = {
        "q": city_name,
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

# --- Firestoreへのデータ保存関数 ---
def save_weather_to_firestore(city_name, weather_data):
    try:
        # citiesコレクションに最新データを保存（上書き）
        doc_ref = db.collection("cities").document(city_name)
        doc_ref.set(weather_data)

        # historical_weatherコレクションに履歴データを追加
        # ドキュメントIDは自動生成
        historical_data = weather_data.copy()
        historical_data["city_name"] = city_name
        db.collection("historical_weather").add(historical_data)

        st.success(f"{city_name}の天気データをFirestoreに保存しました。")
    except Exception as e:
        st.error(f"Firestoreへのデータ保存中にエラーが発生しました: {e}")

# --- Firestoreから全都市のデータを取得する関数 ---
def get_all_cities_from_firestore():
    cities_ref = db.collection("cities")
    docs = cities_ref.stream()
    cities_data = {}
    for doc in docs:
        cities_data[doc.id] = doc.to_dict()
    return cities_data

# --- Firestoreから過去の天気データを取得する関数 ---
def get_historical_weather_data(city_name, days=3):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    historical_ref = db.collection("historical_weather")\
        .where("city_name", "==", city_name)\
        .where("last_update", ">=", start_date)\
        .order_by("last_update")

    docs = historical_ref.stream()
    data_list = []
    for doc in docs:
        data_list.append(doc.to_dict())

    if data_list:
        df = pd.DataFrame(data_list)
        df["last_update"] = pd.to_datetime(df["last_update"])
        df = df.sort_values("last_update")
        return df
    return pd.DataFrame()

# --- Streamlit UI ---
st.set_page_config(layout="wide")

# --- カスタムCSSの読み込み ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")


st.title("Aina Weather アプリ")

# サイドバー
st.sidebar.title("ナビゲーション")
page = st.sidebar.radio("ページを選択", ["ダッシュボード", "データ可視化", "天気予想ゲーム"])

# --- テスト用: 天気取得と保存 ---
with st.sidebar.expander("テスト機能"):
    test_city = st.text_input("テスト都市名を入力", "Tokyo")
    if st.button("天気取得＆保存"):
        with st.spinner(f"{test_city}の天気データを取得中..."):
            weather = get_weather_data(test_city)
            if weather:
                st.write("取得データ:", weather)
                save_weather_to_firestore(test_city, weather)

if page == "ダッシュボード":
    # --- ダッシュボードページ ---
    st.header("現在の天気ダッシュボード")

    all_cities_data = get_all_cities_from_firestore()

    if not all_cities_data:
        st.info("まだ都市の天気データがありません。「テスト機能」で都市の天気データを取得・保存してください。")
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

elif page == "データ可視化":
    st.header("過去の天気データ可視化")

    all_cities_data = get_all_cities_from_firestore()
    if not all_cities_data:
        st.info("まだ都市の天気データがありません。「テスト機能」で都市の天気データを取得・保存してください。")
    else:
        city_names = list(all_cities_data.keys())
        selected_city_viz = st.selectbox("都市を選択してください", city_names, key="viz_city_select")

        if selected_city_viz:
            df_historical = get_historical_weather_data(selected_city_viz)

            if not df_historical.empty:
                st.subheader(f"{selected_city_viz}の過去3日間の天気データ")

                # 気温の折れ線グラフ
                fig_temp = go.Figure()
                fig_temp.add_trace(go.Scatter(x=df_historical["last_update"], y=df_historical["temperature"], mode='lines+markers', name='気温 (°C)'))
                fig_temp.update_layout(title='気温の推移', xaxis_title='日時', yaxis_title='気温 (°C)')
                st.plotly_chart(fig_temp, use_container_width=True)

                # 降水量の棒グラフ
                fig_rain = go.Figure()
                fig_rain.add_trace(go.Bar(x=df_historical["last_update"], y=df_historical["rain_1h"], name='降水量 (mm)'))
                fig_rain.update_layout(title='降水量の推移 (1時間あたり)', xaxis_title='日時', yaxis_title='降水量 (mm)')
                st.plotly_chart(fig_rain, use_container_width=True)
            else:
                st.info(f"{selected_city_viz}の過去3日間のデータはありません。「テスト機能」でデータを取得・保存してください。")

elif page == "天気予想ゲーム":
    st.header("天気予想ゲーム")
    st.write(f"現在のユーザー: {current_user_profile['name']} (ポイント: {current_user_profile['points']})")

    all_cities_data = get_all_cities_from_firestore()
    if not all_cities_data:
        st.info("まだ都市の天気データがありません。「テスト機能」で都市の天気データを取得・保存してください。")
    else:
        city_names = list(all_cities_data.keys())
        selected_city_game = st.selectbox("予想する都市を選択してください", city_names, key="game_city_select")

        st.subheader(f"{selected_city_game}の今日の天気を予想しよう！")
        prediction_options = ["晴れ", "曇り", "雨"]
        user_prediction = st.radio("あなたの予想", prediction_options)

        if st.button("予想を送信"):
            # ここにゲームロジックを実装
            st.write("予想を送信しました！結果判定中...")
            # 実際の天気取得
            actual_weather_data = get_weather_data(selected_city_game)
            if actual_weather_data:
                actual_weather_main = actual_weather_data["weather_main"]

                # 日本語の予想をOpenWeatherMapの英語表記にマッピング
                prediction_mapping = {
                    "晴れ": "Clear",
                    "曇り": "Clouds",
                    "雨": "Rain",
                    # 必要に応じて他の天気も追加
                }
                mapped_user_prediction = prediction_mapping.get(user_prediction, user_prediction) # マッピングがなければそのまま使用

                is_correct = (mapped_user_prediction == actual_weather_main)

                if is_correct:
                    st.success(f"正解！{selected_city_game}は{actual_weather_main}でした！")
                    points_earned = 10
                    current_user_profile["points"] += points_earned
                    db.collection("users").document(current_user_id).update({"points": current_user_profile["points"]})
                    st.balloons()
                    st.write(f"+{points_earned}ポイント獲得！現在のポイント: {current_user_profile['points']}")
                else:
                    st.error(f"残念！{selected_city_game}は{actual_weather_main}でした。")
                    st.write(f"現在のポイント: {current_user_profile['points']}")

                # 予想結果をpredictionsコレクションに保存
                prediction_record = {
                    "user_id": current_user_id,
                    "city_name": selected_city_game,
                    "date": datetime.now().strftime("%Y-%m-%d"), # 日付のみ保存
                    "prediction": user_prediction,
                    "actual_weather": actual_weather_main,
                    "is_correct": is_correct,
                    "timestamp": datetime.now()
                }
                db.collection("predictions").add(prediction_record)

            else:
                st.warning("実際の天気データを取得できませんでした。")

    # --- ランキング表示 ---
    st.subheader("ポイントランキング")
    users_ref = db.collection("users").order_by("points", direction=firestore.Query.DESCENDING).limit(10)
    ranking_docs = users_ref.stream()
    ranking_data = []
    for doc in ranking_docs:
        user_data = doc.to_dict()
        ranking_data.append({"ユーザー名": user_data.get("name", "匿名ユーザー"), "ポイント": user_data["points"]})

    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data)
        df_ranking.index = df_ranking.index + 1 # 1から始まるランキング
        st.table(df_ranking)
    else:
        st.info("まだランキングデータがありません。ゲームをプレイしてポイントを獲得しましょう！")

elif page == "天気予想ゲーム":
    st.header("天気予想ゲーム")
    st.write("ここに天気予想ゲームのコンテンツが入ります。")

st.write("左側のサイドバーから各ページにアクセスできるようになります。")
