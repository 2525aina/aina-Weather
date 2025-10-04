# 🌦️ Aina Weather App

Aina Weatherは、気象データを多角的に楽しむための多機能Webアプリケーションです。リアルタイムの天気取得から、データの可視化、インタラクティブなゲームまで、天気に関するさまざまな機能を提供します。

## ✨ 主な機能

このアプリケーションには、以下の機能が含まれています。

*   **📡 天気取得:**
    *   指定した都市の現在の天気情報（気温、湿度、風速など）をOpenWeatherMap APIから取得し、データベースに保存します。

*   **📊 ダッシュボード:**
    *   データベースに保存された各都市の最新の天気情報をカード形式で分かりやすく表示します。

*   **📈 データ可視化:**
    *   蓄積された過去の天気データ（気温、降水量）を、Plotlyを使用してインタラクティブなグラフで可視化します。

*   **🎮 天気予想ゲーム:**
    *   都市を選択し、その日の天気を予想する簡単なゲームです。
    *   正解するとポイントが貯まり、全ユーザーでのランキングが表示されます。

*   **👤 ユーザー管理:**
    *   Firebase Authenticationによる匿名認証でユーザーを識別し、ゲームのポイントをユーザーごとに管理します。

## 🛠️ 技術スタック

*   **フロントエンド:** [Streamlit](https://streamlit.io/)
*   **バックエンド:** Python
*   **データベース:** [Firebase Firestore](https://firebase.google.com/products/firestore)
*   **認証:** [Firebase Authentication](https://firebase.google.com/products/auth)
*   **データソース:** [OpenWeatherMap API](https://openweathermap.org/api)
*   **主要ライブラリ:** `pandas`, `plotly`, `requests`

## ⚙️ セットアップとインストール

以下の手順で、プロジェクトをローカルにセットアップします。

### 1. 前提条件

*   Python 3.8以降
*   [OpenWeatherMap](https://openweathermap.org/)のアカウントとAPIキー
*   [Firebase](https://firebase.google.com/)プロジェクトとサービスアカウントキー（JSONファイル）

### 2. インストール

リポジトリをクローンし、仮想環境を作成して、必要なPythonパッケージをインストールします。

```bash
# リポジトリをクローン
git clone https://github.com/2525aina/aina-Weather.git
cd aina-Weather

# 仮想環境を作成して有効化
# (Windowsでは `venv\Scripts\activate` を使用)
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 3. シークレットの構成

プロジェクトのルートに `.streamlit` ディレクトリと、その中に `secrets.toml` ファイルを作成します。

```bash
mkdir .streamlit
touch .streamlit/secrets.toml
```

作成した `secrets.toml` に、APIキーとFirebaseの認証情報を以下のように記述します。

```toml
# .streamlit/secrets.toml

# OpenWeatherMap APIキー
[openweathermap]
api_key = "YOUR_OPENWEATHERMAP_API_KEY"

# Firebaseサービスアカウントの認証情報
# 取得したJSONファイルの内容をここに貼り付けます
[firebase_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-client-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-x509-cert-url"
```

## 🚀 実行方法

依存関係のインストールとシークレットの設定が完了したら、以下のコマンドでアプリケーションを実行します。

```bash
streamlit run app.py
```

Webブラウザで `http://localhost:8501` を開くと、アプリケーションが表示されます。

## 📂 アプリケーションの構成

*   `app.py`: アプリケーションのメインエントリーポイント。ホームページ（玄関）の役割を果たします。
*   `pages/`: 各ページのスクリプトが格納されています。Streamlitによって自動的にサイドバーのナビゲーションが生成されます。
*   `services/`: FirebaseやOpenWeatherMap APIとの通信など、バックエンドのロジックをまとめたモジュールが格納されています。
*   `style.css`: アプリケーションのカスタムスタイルシートです。
