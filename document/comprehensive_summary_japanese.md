## アプリケーション概要
このアプリケーションは、Twitch/YouTube/ニコニコの配信開始・新着動画投稿を自動検知し、リアルタイムでBlueskyに通知を投稿するPythonボットです。Twitch EventSubウェブフックやYouTube/Niconicoの監視機能を利用し、Cloudflare Tunnelを使ってローカル環境でもWebhookを受信できます。GUI（Tkinter）による設定・管理にも対応しています。

## 主な機能
*   **Twitch/YouTube/ニコニコ連携:** 各サービスの配信開始・新着動画投稿を自動検知し、Blueskyへ通知（配信終了通知はTwitchのみ対応、今後拡張予定）。
*   **Bluesky通知:** サービスごとにカスタマイズ可能なテンプレート・画像でBlueskyに投稿。テンプレート・画像・Webhook・APIキー等は各サービスごとに個別管理可能。
*   **Cloudflare Tunnel:** ローカルマシンをインターネットに公開し、Webhook受信を可能にします。
*   **GUI管理:** TkinterベースのGUIで、設定ファイル（settings.env）と双方向連携し、各種設定・テンプレート・画像・Webhook・APIキー等を統合管理。タブ構成・レイアウト・UI/UX改善済み。
*   **設定:** settings.envファイルでAPIキー、通知ON/OFF、テンプレート・画像パス、Discord Webhook、ログレベル等を柔軟にカスタマイズ。
*   **エラー処理とロギング:**
    *   重大なエラー時のDiscord通知
    *   APIエラーの自動リトライ（回数・待機時間は設定可能）
    *   アプリケーションアクティビティの包括的なロギング
    *   Bluesky投稿履歴（logs/post_history.csv）
    *   監査ログ（logs/audit.log）
    *   テンプレートパス未設定・ファイル未存在時はエラーハンドリング（エラーログ＋Discord通知＋投稿中止）
*   **サブスクリプション管理:** 不要なTwitch EventSubサブスクリプションの自動クリーンアップ。
*   **セキュリティ:** Webhook署名検証によるリプレイ攻撃対策、WEBHOOK_SECRETの自動ローテーション。

## 使用されている主要なテクノロジー
*   Python（コア言語）
*   Flask（Webhook用Webフレームワーク）
*   Tkinter（GUI）
*   Twitch/YouTube/Niconico API
*   Bluesky API
*   Cloudflare Tunnel（cloudflared）
*   Discord API（Webhook）
*   Git（バージョン管理）
*   pytest（自動テスト）
*   CSV（投稿履歴ロギング用）
*   YAML（Cloudflare Tunnel設定用）
*   .envファイル（設定管理用）

## セットアップ方法
1. リポジトリをクローンし、`pip install -r requirements.txt`で必要なPythonパッケージをインストール。
2. Cloudflare Tunnel（cloudflared）をインストールし、config.ymlを設定。
3. `settings.env.example`をコピーして`settings.env`を作成し、以下を記入：
    * 各サービスのAPIキー・ユーザーID
    * Blueskyの画像/テンプレートパス（各サービスごとに個別指定可能）
    * Discord Webhook URL
    * ログレベル等
4. 必要に応じてGUI（`python gui/app_gui.py`）で設定・管理。
5. ボットは`python main.py`で起動。通知レベルやテンプレート切り替え等はsettings.envまたはGUIから管理。
