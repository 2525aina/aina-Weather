import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
import pandas as pd

# --- Firebase 初期化 ---
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = initialize_firebase()

DESCENDING = firestore.Query.DESCENDING

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

from services.sidebar_utils import normalize_city_name_for_storage

# --- Firestoreへのデータ保存関数 ---
def save_weather_to_firestore(city_name, weather_data):
    city_name_normalized = normalize_city_name_for_storage(city_name)
    try:
        # citiesコレクションに最新データを保存（上書き）
        doc_ref = db.collection("cities").document(city_name_normalized)
        doc_ref.set(weather_data)

        # historical_weatherコレクションに履歴データを追加
        # ドキュメントIDは自動生成
        historical_data = weather_data.copy()
        historical_data["city_name"] = city_name_normalized
        db.collection("historical_weather").add(historical_data)

        st.success(f"{city_name}の天気データをFirestoreに保存しました。")
        return {"type": "success", "content": f"{city_name}の天気データをFirestoreに保存しました。"}
    except Exception as e:
        st.error(f"Firestoreへのデータ保存中にエラーが発生しました: {e}")
        return {"type": "error", "content": f"Firestoreへのデータ保存中にエラーが発生しました: {e}"}

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

# --- Firestoreから都市データを削除する関数 ---
def delete_city_from_firestore(city_name):
    try:
        # citiesコレクションから削除
        db.collection("cities").document(city_name).delete()

        # historical_weatherコレクションから関連データを削除
        # クエリで削除するため、バッチ処理またはトランザクションが必要になる場合がある
        # ここでは簡易的にストリームで削除するが、大量データの場合は注意
        historical_ref = db.collection("historical_weather").where("city_name", "==", city_name).stream()
        for doc in historical_ref:
            doc.reference.delete()

        st.success(f"{city_name}のデータをFirestoreから削除しました。")
        return {"type": "success", "content": f"{city_name}のデータをFirestoreから削除しました。"}
    except Exception as e:
        st.error(f"Firestoreからのデータ削除中にエラーが発生しました: {e}")
        return {"type": "error", "content": f"Firestoreからのデータ削除中にエラーが発生しました: {e}"}
