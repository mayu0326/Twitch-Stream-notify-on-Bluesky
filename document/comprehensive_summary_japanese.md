## アプリケーション概要
このアプリケーションは、Twitchストリームの開始を自動的に検出し、リアルタイムでBlueskyに通知を投稿するように設計されたPythonボットです。Twitch EventSubウェブフックを利用してストリーム開始を検出し、Cloudflare Tunnelを使用してローカル環境でもウェブフックを受信します。

## 主な機能
*   **Twitch EventSub連携:** Twitch EventSubウェブフックを使用してストリーム開始を自動的に検出します。
*   **Bluesky通知:** カスタマイズ可能な通知をBlueskyに投稿します。画像添付オプションも含まれます。通知内容はテンプレートを使用して管理できます。
*   **Cloudflare Tunnel:** ローカルマシンをインターネットに公開することにより、ウェブフックの受信を可能にします。
*   **設定:** ユーザーは`settings.env`ファイル（APIキー、通知設定、ログレベル、画像パス、テンプレートパス、Discordウェブフックなど）を介して設定をカスタマイズできます。
*   **エラー処理とロギング:**
    *   重大なエラーに対するDiscord通知
    *   APIエラーの自動リトライ（制限と待機時間は設定可能）
    *   アプリケーションアクティビティの包括的なロギング
    *   Bluesky投稿履歴（`logs/post_history.csv`内）
    *   監査ログ（`logs/audit.log`内）
*   **サブスクリプション管理:** 不要になったTwitch EventSubサブスクリプションを自動的にクリーンアップします。
*   **セキュリティ:** ウェブフック署名検証によるリプレイ攻撃対策を実装しています。

## 使用されている主要なテクノロジー
*   Python（コア言語）
*   Flask（ウェブフック用ウェブフレームワーク）
*   Twitch API（EventSub）
*   Bluesky API
*   Cloudflare Tunnel（`cloudflared`）
*   Discord API（ウェブフック）
*   Git（バージョン管理）
*   `pytest`（自動テスト）
*   CSV（投稿履歴ロギング用）
*   YAML（Cloudflare Tunnel設定用）
*   `.env`ファイル（設定管理用）

## セットアップ方法
アプリケーションをセットアップするには、まずリポジトリをクローンし、`pip install -r requirements.txt`を使用して必要なPythonパッケージをインストールします。

### 前提条件
*   Python 3.10以降
*   Git
*   `cloudflared`

### 必要なアカウント
*   Twitch（EventSubおよびAPI認証情報用）
*   Bluesky（投稿用）
*   Cloudflare（Tunnel用）

### 設定手順
重要なステップは、`settings.env`ファイル（`settings.env.example`からコピー）に以下の情報を記述することです。
*   APIキー
*   ユーザーID
*   Blueskyの画像/テンプレートパス
*   DiscordウェブフックURL
*   ログレベルなどの設定

Cloudflare Tunnelも`config.yml`ファイルでセットアップする必要があります。

ボットは`python main.py`で起動します。通知レベルやBluesky投稿テンプレートの変更などのカスタマイズは、`settings.env`ファイルを介して管理されます。
