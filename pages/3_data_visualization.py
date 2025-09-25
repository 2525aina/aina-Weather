import streamlit as st
import plotly.graph_objects as go
from services.firebase_service import get_all_cities_from_firestore, get_historical_weather_data

st.title("データ可視化")

all_cities_data = get_all_cities_from_firestore()
if not all_cities_data:
    st.info("まだ都市の天気データがありません。「お天気取得」ページで都市の天気データを取得・保存してください。")
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
            st.info(f"{selected_city_viz}の過去3日間のデータはありません。「お天気取得」ページでデータを取得・保存してください。")
