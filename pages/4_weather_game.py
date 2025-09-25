import streamlit as st
import pandas as pd
from datetime import datetime

from services.firebase_service import db, get_current_user, get_or_create_user_profile, get_all_cities_from_firestore, DESCENDING
from services.weather_service import get_weather_data

st.title("🎮 天気予想ゲーム")

current_user_id = get_current_user()
current_user_profile = get_or_create_user_profile(current_user_id)

st.write(f"現在のユーザー: {current_user_profile['name']} (ポイント: {current_user_profile['points']})")

all_cities_data = get_all_cities_from_firestore()
if not all_cities_data:
    st.info("まだ都市の天気データがありません。「お天気取得」ページで都市の天気データを取得・保存してください。")
else:
    city_names = list(all_cities_data.keys())
    selected_city_game = st.selectbox("予想する都市を選択してください", city_names, key="game_city_select")

    st.subheader(f"{selected_city_game}の今日の天気を予想しよう！")
    prediction_options = ["晴れ", "曇り", "雨"]
    user_prediction = st.radio("あなたの予想", prediction_options)

    if st.button("予想を送信"):
        st.write("予想を送信しました！結果判定中...")
        actual_weather_data = get_weather_data(selected_city_game)
        if actual_weather_data:
            actual_weather_main = actual_weather_data["weather_main"]

            prediction_mapping = {
                "晴れ": "Clear",
                "曇り": "Clouds",
                "雨": "Rain",
            }
            mapped_user_prediction = prediction_mapping.get(user_prediction, user_prediction)

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

            prediction_record = {
                "user_id": current_user_id,
                "city_name": selected_city_game,
                "date": datetime.now().strftime("%Y-%m-%d"),
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
users_ref = db.collection("users").order_by("points", direction=DESCENDING).limit(10)
ranking_docs = users_ref.stream()
ranking_data = []
for doc in ranking_docs:
    user_data = doc.to_dict()
    ranking_data.append({"ユーザー名": user_data.get("name", "匿名ユーザー"), "ポイント": user_data["points"]})

if ranking_data:
    df_ranking = pd.DataFrame(ranking_data)
    df_ranking.index = df_ranking.index + 1
    st.table(df_ranking)
else:
    st.info("まだランキングデータがありません。ゲームをプレイしてポイントを獲得しましょう！")
