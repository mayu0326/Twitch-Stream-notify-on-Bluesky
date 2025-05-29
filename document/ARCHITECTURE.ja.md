## プロジェクトレビュー: Stream notify on Bluesky

### 1. コアアプリケーションロジック

#### main.py
- **役割:** アプリケーションのメインエントリーポイント。全体の機能を調整。
- **機能:**
    - Flaskウェブサーバーを初期化・実行（本番はwaitress）。
    - 設定の読み込み、ロギング設定、設定検証。
    - tunnel.py経由でCloudflareやその他のトンネルサービスの開始/停止を管理。
    - Twitch EventSubウェブフックのインタラクション（/webhookエンドポイント: GET=ヘルスチェック, POST=通知）。
    - eventsub.verify_signatureで署名検証。
    - Twitch webhook_callback_verificationチャレンジ処理。
    - stream.online/stream.offlineイベントの処理（詳細抽出→BlueskyPosterでBluesky投稿）。
    - settings.envで各サービスごとの通知ON/OFF・テンプレート・画像パス等を個別管理（Twitch/YouTube/ニコニコ/Bluesky/Discord等）。
    - Twitchからの失効メッセージのロギング。
    - EventSubサブスクリプションの管理（クリーンアップ/作成）。
    - WEBHOOK_SECRETのローテーション。
    - TWITCH_BROADCASTER_IDをユーザーIDから変換して使用。
    - GUI（Tkinter）との連携（settings.env同期・プロセス制御）。
- **主要技術:** Flask, Waitress, Tkinter（GUI連携）

#### eventsub.py
- **役割:** Twitch EventSub・API認証管理。
- **機能:**
    - OAuthクライアント認証フローでアクセストークン取得。
    - ユーザー名→ブロードキャスターID変換。
    - HMAC SHA256署名検証（タイムスタンプ検証含む）。
    - EventSubサブスクリプション管理（取得/作成/削除/クリーンアップ）。
    - API呼び出しのリトライ。
    - タイムゾーン管理。
- **主要技術:** Twitch API, HMAC, SHA256

#### bluesky.py
- **役割:** Bluesky連携。
- **機能:**
    - BlueskyPosterクラス: ログイン、画像アップロード、Jinja2テンプレートで通知投稿（オンライン/オフライン/新着動画）。
    - 各サービスごとのテンプレート・画像パス対応（Twitch/YouTube/ニコニコ等）。
    - テンプレートパス未設定・ファイル未存在時はエラーハンドリング（エラーログ＋Discord通知＋投稿中止）。
    - 投稿履歴をlogs/post_history.csvに記録。
    - APIリトライ。
- **主要技術:** atproto, Jinja2

#### tunnel.py
- **役割:** Cloudflare/ngrok/localtunnel/custom 各種トンネルサービスの起動・管理。
- **機能:**
    - start_tunnel(): settings.envのTUNNEL_SERVICEで選択されたサービス（cloudflare/ngrok/localtunnel/custom）に応じて、各種コマンド（TUNNEL_CMD/NGROK_CMD/LOCALTUNNEL_CMD/CUSTOM_TUNNEL_CMD）でトンネルプロセスを起動。
    - stop_tunnel(): プロセスをterminate()→wait()で正常終了、タイムアウト時はkill()で強制終了。例外時もkill()を試みる。
    - ログ出力はlogger引数で指定可能（未指定時は"tunnel.logger"）。
    - コマンド未設定時は警告ログを出し、起動しない。
    - コマンド実行時はshlex.splitで安全に分割し、FileNotFoundErrorや一般例外も個別にログ。
    - TUNNEL_SERVICEが未設定・未知の場合はTUNNEL_CMDを利用。
- **主要技術:** subprocess, shlex, logging, 環境変数によるサービス切替

#### utils.py
- **役割:** 共通ユーティリティ。
- **機能:**
    - Jinja2日付フィルタ、.envファイル更新（コメント保持）、リトライデコレータ、シークレット生成、.env読込、シークレットローテーション、URL検証。
- **主要技術:** secrets, datetime, pytz, tzlocal

### 2. 設定とセッティング

#### settings.env.example
- **役割:** settings.envのテンプレート。全設定・シークレットを管理。
- **主要設定:**
    - Twitch: TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_BROADCASTER_ID
    - Bluesky: BLUESKY_USERNAME, BLUESKY_APP_PASSWORD, BLUESKY_IMAGE_PATH, BLUESKY_TEMPLATE_PATH, BLUESKY_OFFLINE_TEMPLATE_PATH, BLUESKY_YT_ONLINE_TEMPLATE_PATH, BLUESKY_YT_OFFLINE_TEMPLATE_PATH, BLUESKY_NICO_ONLINE_TEMPLATE_PATH, BLUESKY_NICO_OFFLINE_TEMPLATE_PATH など
    - Webhook: WEBHOOK_SECRET, SECRET_LAST_ROTATED, WEBHOOK_CALLBACK_URL
    - Discord: discord_error_notifier_url, discord_notify_level
    - 一般: TIMEZONE, LOG_LEVEL, LOG_RETENTION_DAYS
    - トンネル: TUNNEL_CMD
    - APIリトライ: RETRY_MAX, RETRY_WAIT

#### logging_config.py
- **役割:** ロギング設定。
- **機能:**
    - AuditLogger（logs/audit.log）、AppLogger（logs/app.log, logs/error.log, コンソール）。
    - TimedRotatingFileHandlerでローテーション・保持。
    - Discordエラー通知（任意）。
    - Flaskロガー統合。
- **主要ライブラリ:** logging, discord_logging.handler

#### Cloudflared/config.yml.example
- **役割:** cloudflaredの設定例。
- **機能:**
    - トンネルUUID、認証情報、イングレスルール、noTLSVerify。

### 3. サポートファイル・ディレクトリ

- requirements.txt: 依存パッケージ（Flask, requests, atproto, python-dotenv, Jinja2, waitress, pytz, tzlocal, python-logging-discord-handler等）
- development-requirements.txt: 開発用依存（pytest, black, autopep8, pre-commit, ggshield）
- templates/: Bluesky投稿用Jinja2テンプレート（Twitch/YouTube/ニコニコ等サービスごと）
- images/: 投稿用画像（noimage.png等）
- logs/: ログファイル（app.log, error.log, audit.log, post_history.csv）
- Docker/: Dockerfile, docker-compose.yml, docker_readme_section.md

### 4. 開発・CI/CDセットアップ

- .github/: GitHubテンプレート・ワークフロー（バグ報告、GitGuardianシークレットスキャン等）
- .pre-commit-config.yaml: pre-commitフック（ggshield）
- pytest.ini: pytest設定
- tests/: 自動テスト（pytest）

### 5. ドキュメントファイル

- README.md: メインドキュメント（機能・セットアップ・使い方・FAQ・Docker・貢献）
- document/CONTRIBUTING.md: 貢献ガイド
- document/comprehensive_summary_japanese.md: 日本語要約
- document/consolidated_summary_japanese.md: 内部メモ・推奨事項
- document/contributing_readme_section.md: 貢献セクションスニペット
- LICENSE: GPLv2

### 全体概要

本プロジェクトは、Twitch/YouTube/ニコニコのイベントをBlueskyへ通知するPythonボットで、各サービスごとのテンプレート・画像・Webhook・APIキー個別管理、GUI（Tkinter）連携、強力なエラーハンドリング、包括的なドキュメント・テストを備え、拡張性・安全性に優れた設計です。
