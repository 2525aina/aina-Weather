# aina-Weather

aina-Weatherは、指定した都市の現在の天気と予報を表示するシンプルなWebアプリケーションです。

## 主な機能

*   任意の都市の現在の天気を取得します。
*   気温、湿度、風速、気象状況を表示します。
*   （将来的に）Firebaseを使用したユーザー固有の機能。

## 技術スタック

*   **フロントエンド:** [Streamlit](https://streamlit.io/)
*   **バックエンド:** Python
*   **データソース:** [OpenWeatherMap API](https://openweathermap.org/api)
*   **バックエンドサービス:** [Firebase](https://firebase.google.com/)

## セットアップとインストール

以下の手順で、プロジェクトをローカルにセットアップします。

### 1. 前提条件

*   Python 3.8以降
*   APIキーを取得するための[OpenWeatherMap](https://openweathermap.org/)アカウント。
*   サービスアカウントキーファイルを持つ[Firebase](https://firebase.google.com/)プロジェクト。

### 2. インストール

リポジトリをクローンし、必要なPythonパッケージをインストールします。

```bash
# 最初に仮想環境を作成することをお勧めします
# お使いの環境によっては、pythonの代わりにpython3を使用する必要があります
python3 -m venv venv
source venv/bin/activate  # Windowsでは `venv\Scripts\activate` を使用します

# 依存関係をインストールします
pip install -r requirements.txt
```

### 3. シークレットの構成

このプロジェクトでは、Streamlitのシークレット管理を使用します。`.streamlit`ディレクトリ内に`secrets.toml`という名前のファイルを作成する必要があります。

1.  ディレクトリとファイルを作成します:
    ```bash
    mkdir .streamlit
    touch .streamlit/secrets.toml
    ```

2.  APIキーとFirebaseサービスアカウントの認証情報を`.streamlit/secrets.toml`ファイルに追加します。

    ```toml
    # .streamlit/secrets.toml

    # OpenWeatherMap APIキー
    openweathermap_api_key = "YOUR_OPENWEATHERMAP_API_KEY"

    # Firebaseサービスアカウントの認証情報
    # FirebaseサービスアカウントのJSONファイル（例: aina-weather-firebase-adminsdk-fbsvc-5e1732e984.json）
    # の内容をコピーして、以下のようにフォーマットします。
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
    **注:** `private_key`は、TOMLファイルに一行で記述する場合、改行文字(`\n`)をエスケープする必要があります。

## 実行方法

依存関係をインストールし、シークレットを設定したら、アプリケーションを実行できます。

```bash
streamlit run app.py
```

アプリケーションは、Webブラウザの`http://localhost:8501`で利用可能になります。