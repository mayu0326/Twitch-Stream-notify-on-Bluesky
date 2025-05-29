## アプリケーション概要
このアプリケーションは、Twitch/YouTube/ニコニコの配信開始・新着動画投稿を自動検知し、リアルタイムでBlueskyに通知を投稿するPythonボットです。Twitch EventSubウェブフックやYouTube/Niconicoの監視機能を利用し、Cloudflare Tunnelやngrok/localtunnel/customトンネルを使ってローカル環境でもWebhookを受信できます。GUI（Tkinter）による設定・管理にも対応し、各種設定の自動反映や保存完了メッセージ表示など、ユーザビリティも強化されています。

## 主な機能
*   **Twitch/YouTube/ニコニコ連携:** 各サービスの配信開始・新着動画投稿を自動検知し、Blueskyへ通知（配信終了通知はTwitchのみ対応、今後拡張予定）。
*   **Bluesky通知:** サービスごとにカスタマイズ可能なテンプレート・画像でBlueskyに投稿。テンプレート・画像・Webhook・APIキー等は各サービスごとに個別管理可能。
    * テンプレート・画像パスは `templates/`・`images/` 以降の相対パスで保存・管理。
*   **トンネル機能:** Cloudflare Tunnel/ngrok/localtunnel/customコマンドに対応し、TUNNEL_SERVICE環境変数でサービスを切り替え、各種コマンド（TUNNEL_CMD/NGROK_CMD/LOCALTUNNEL_CMD/CUSTOM_TUNNEL_CMD）でトンネルの自動起動・監視・URL自動反映・再接続を実装。WebhookコールバックURLは恒久用/一時用を自動切替。コマンド未設定時は警告ログを出し、起動しない。終了時はterminate/waitで正常終了、タイムアウトや例外時はkillで強制終了し、詳細なログを出力。
*   **GUI管理:** TkinterベースのGUIで、settings.envと双方向連携し、各種設定・テンプレート・画像・Webhook・APIキー等を統合管理。タブ構成・レイアウト・UI/UX改善済み。保存時は完了メッセージを表示し、タブ切替時に最新設定を自動反映。
*   **設定:** settings.envファイルでAPIキー、通知ON/OFF、テンプレート・画像パス、Discord Webhook、ログレベル等を柔軟にカスタマイズ。
*   **エラー処理とロギング:**
    * 重大なエラー時のDiscord通知
    * APIエラーの自動リトライ（回数・待機時間は設定可能）
    * アプリケーションアクティビティの包括的なロギング
    * Bluesky投稿履歴（logs/post_history.csv）
    * 監査ログ（logs/audit.log）
    * テンプレート・画像パス未設定・ファイル未存在時はエラーハンドリング（エラーログ＋Discord通知＋投稿中止）
*   **サブスクリプション管理:** 不要なTwitch EventSubサブスクリプションの自動クリーンアップ。
*   **セキュリティ:** Webhook署名検証によるリプレイ攻撃対策、WEBHOOK_SECRETの自動ローテーション。

## 使用されている主要なテクノロジー
*   Python（コア言語）
*   Flask（Webhook用Webフレームワーク）
*   Tkinter（GUI）
*   Twitch/YouTube/Niconico API
*   Bluesky API
*   Cloudflare Tunnel/ngrok/localtunnel/custom
*   Discord API（Webhook）
*   Git（バージョン管理）
*   pytest（自動テスト）
*   CSV（投稿履歴ロギング用）
*   YAML（Cloudflare Tunnel設定用）
*   .envファイル（設定管理用）

## セットアップ方法
1. リポジトリをクローンし、`pip install -r requirements.txt`で必要なPythonパッケージをインストール。
2. Cloudflare Tunnel（cloudflared）やngrok/localtunnel等をインストールし、必要に応じてconfig.ymlやコマンドを設定。
3. `settings.env.example`をコピーして`settings.env`を作成し、以下を記入：
    * 各サービスのAPIキー・ユーザーID
    * Blueskyの画像/テンプレートパス（各サービスごとに個別指定可能。`templates/`・`images/`以降の相対パスで記載）
    * Discord Webhook URL
    * ログレベル等
    * トンネルコマンド・WebhookコールバックURL（恒久用/一時用）
4. 必要に応じてGUI（`python gui/app_gui.py`）で設定・管理。
    * GUIではテンプレート・画像・Webhook・APIキー等を直感的に編集可能。
    * 設定保存時は完了メッセージが表示され、タブ切替時に最新設定が自動反映されます。
5. ボットは`python main.py`で起動。通知レベルやテンプレート切り替え等はsettings.envまたはGUIから管理。
