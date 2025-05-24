## プロジェクトレビュー: Stream notify on Bluesky

### 1. コアアプリケーションロジック

#### `main.py`

*   **役割:** アプリケーションのメインエントリーポイント。全体の機能を調整します。
*   **機能:**
    *   Flaskウェブサーバーを初期化し実行します（本番環境では`waitress`を使用）。
    *   アプリケーションのセットアップを処理します: 設定の読み込み、ロギングの設定、設定の検証。
    *   `tunnel.py` を介してCloudflareトンネルのライフサイクル（開始/停止）を管理します。
    *   Twitch EventSubウェブフックのインタラクションを処理します:
        *   GET（ヘルスチェック）およびPOST（通知）用の `/webhook` エンドポイントを定義します。
        *   受信ウェブフック署名を検証します (`eventsub.verify_signature`)。
        *   Twitchからの `webhook_callback_verification` チャレンジを処理します。
        *   `stream.online` および `stream.offline` イベントの通知メッセージを処理します。
        *   `stream.online` の場合: ストリーム詳細（タイトル、カテゴリ）を抽出し、`BlueskyPoster` を使用してBlueskyに投稿します。
        *   `stream.offline` の場合: `BlueskyPoster` を使用してオフライン通知をBlueskyに投稿します。
        *   `NOTIFY_ON_ONLINE`/`NOTIFY_ON_OFFLINE` 環境変数を介してオンライン/オフライン通知の有効化/無効化をサポートします。
    *   Twitchからの失効メッセージをログに記録します。
    *   Twitch EventSubサブスクリプションを管理します: 古いものをクリーンアップし、目的のイベント用に新しいものを作成します (`eventsub.cleanup_eventsub_subscriptions`, `eventsub.create_eventsub_subscription`)。
    *   `WEBHOOK_SECRET` のローテーションを処理します (`utils.rotate_secret_if_needed`)。
    *   `TWITCH_BROADCASTER_ID` が数値IDであることを保証します (`eventsub.setup_broadcaster_id`)。
*   **主要技術:** `Flask`, `Waitress`

#### `eventsub.py`

*   **役割:** Twitch EventSubシステムおよび認証用のTwitch APIとのすべてのインタラクションを管理します。
*   **機能:**
    *   OAuthクライアント資格情報フローを処理して、Twitchアプリのアクセストークンを取得/更新します (`get_app_access_token`, `get_valid_app_access_token`)。
    *   必要に応じてTwitchユーザー名をブロードキャスターIDに変換します (`get_broadcaster_id`, `setup_broadcaster_id`)。
    *   受信したTwitchウェブフックメッセージのHMAC SHA256署名を検証します (`verify_signature`)。これにはリプレイ攻撃防止のためのタイムスタンプ検証も含まれます。
    *   EventSubサブスクリプションを管理します:
        *   既存のサブスクリプションを取得します (`get_existing_eventsub_subscriptions`)。
        *   指定されたイベントタイプの新しいサブスクリプションを作成します (`create_eventsub_subscription`)。
        *   サブスクリプションを削除します (`delete_eventsub_subscription`)。
        *   無効または古いサブスクリプションをクリーンアップします (`cleanup_eventsub_subscriptions`)。
    *   API呼び出しにリトライメカニズムを使用します (`utils.retry_on_exception`)。
    *   タイムスタンプ操作のためのタイムゾーン設定を管理します。
*   **主要技術:** Twitch API, HMAC, SHA256

#### `bluesky.py`

*   **役割:** Blueskyソーシャルネットワークとのすべてのインタラクションを処理します。
*   **機能:**
    *   `BlueskyPoster` クラス:
        *   提供された認証情報を使用してBlueskyにログインします。
        *   投稿に埋め込むために画像をBlueskyにアップロードします (`upload_image`)。
        *   Jinja2テンプレートとイベントデータを使用して、「ストリームオンライン」通知をフォーマットし投稿します (`post_stream_online`)。画像添付をサポートします。
        *   Jinja2テンプレートを使用して、「ストリームオフライン」通知をフォーマットし投稿します (`post_stream_offline`)。
        *   すべての投稿試行（成功/失敗）を `logs/post_history.csv` に記録します (`_write_post_history`)。
    *   `load_template()`: 指定されたパスからJinja2テンプレートをロードし、エラー時のフォールバックを備えます。カスタム `datetimeformat` フィルターをアタッチします。
    *   Bluesky API呼び出しにリトライメカニズムを使用します。
*   **主要技術:** AT Protocol (`atproto` ライブラリ), `Jinja2`

#### `tunnel.py`

*   **役割:** Cloudflare Tunnel (`cloudflared`) クライアントの実行を管理します。
*   **機能:**
    *   `start_tunnel()`: `TUNNEL_CMD` 環境変数で指定されたコマンドを使用して `cloudflared` プロセスを開始します。`shlex.split` を使用してコマンドを解析し、プロセス出力をリダイレクトします。
    *   `stop_tunnel()`: `cloudflared` プロセスを正常に終了させます。必要に応じて強制終了するフォールバックを備えます。
*   **主要技術:** `subprocess`, `shlex`

#### `utils.py`

*   **役割:** アプリケーション全体で使用される共通のユーティリティ関数とデコレータを提供します。
*   **機能:**
    *   `format_datetime_filter()`: ISO日時文字列をローカライズされた人間が読める形式にフォーマットするためのJinja2フィルター。
    *   `update_env_file_preserve_comments()`: コメントと構造を保持しながら `.env` ファイルを変更します。
    *   `retry_on_exception()`: 指定された例外を発生させる関数を自動的にリトライするデコレータ。
    *   `generate_secret()`: シークレット用の安全なランダム16進文字列を作成します。
    *   `read_env()`: `.env` ファイルからキーと値のペアを読み取ります。
    *   `rotate_secret_if_needed()`: `WEBHOOK_SECRET` が30日ごと、または欠落している場合に自動ローテーションを管理します。
    *   `is_valid_url()`: 基本的なURL検証。
*   **主要技術:** `secrets`, `datetime`, `pytz`, `tzlocal`

### 2. 設定とセッティング

#### `settings.env.example`

*   **役割:** すべての特定の設定とシークレットを保持する `settings.env` ファイルのテンプレート。
*   **主要設定:**
    *   Twitch: `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `TWITCH_BROADCASTER_ID`
    *   Bluesky: `BLUESKY_USERNAME`, `BLUESKY_PASSWORD`, `BLUESKY_IMAGE_PATH`, `BLUESKY_TEMPLATE_PATH`, `BLUESKY_OFFLINE_TEMPLATE_PATH`
    *   Webhook: `WEBHOOK_SECRET` (自動管理), `SECRET_LAST_ROTATED` (自動管理), `WEBHOOK_CALLBACK_URL`
    *   Discord通知: `discord_error_notifier_url`, `discord_notify_level`
    *   一般: `TIMEZONE`, `LOG_LEVEL`, `LOG_RETENTION_DAYS`
    *   トンネル: `TUNNEL_CMD`
    *   APIリトライ: `RETRY_MAX`, `RETRY_WAIT`

#### `logging_config.py`

*   **役割:** アプリケーションのロギングシステムを設定します。
*   **機能:**
    *   重要な監査証跡用の "AuditLogger" を設定します (`logs/audit.log`)。
    *   一般的なアプリケーションおよびエラーロギング用の "AppLogger" を設定します:
        *   一般ログは `logs/app.log` へ。
        *   エラー固有のログは `logs/error.log` へ。
        *   コンソール出力。
    *   すべてのログファイルは、毎日のローテーションと設定可能な保持期間（`LOG_RETENTION_DAYS`）のために `TimedRotatingFileHandler` を使用します。
    *   オプションで、`discord_error_notifier_url` と `discord_notify_level` に基づいて、Discordウェブフック経由でエラー通知を送信します。
    *   Flaskアプリインスタンスが提供されている場合、Flaskのロガーと統合します。
*   **主要ライブラリ:** `logging`, `discord_logging.handler`

#### `Cloudflared/config.yml.example`

*   **役割:** `cloudflared` クライアントの構成例。
*   **機能:**
    *   Cloudflare Tunnelの動作方法を定義します:
        *   トンネルUUIDと認証情報ファイルのパスを指定します。
        *   イングレスルールを設定します: パブリックホスト名のトラフィックをローカルFlaskアプリ（ポート3000）にルーティングし、他のリクエストには404を返します。
        *   CloudflareがパブリックTLSを処理するため、ローカルサービスには `noTLSVerify: true` を含めます。

### 3. サポートファイルとディレクトリ

#### `requirements.txt`

*   **役割:** アプリケーションの実行に必要なすべてのPython依存関係をリストします。
*   **主要パッケージ:** `Flask`, `requests`, `atproto`, `python-dotenv`, `Jinja2`, `waitress`, `pytz`, `tzlocal`, `python-logging-discord-handler`

#### `development-requirements.txt`

*   **役割:** 開発目的の追加のPython依存関係をリストします。`requirements.txt` を含みます。
*   **主要パッケージ:** `pytest`, `black`, `autopep8`, `pre-commit`, `ggshield`

#### `templates/`

*   **役割:** Bluesky投稿をフォーマットするためのJinja2テンプレートを含みます。
*   **ファイル:**
    *   `default_template.txt`: 「ストリームオンライン」通知用。
    *   `offline_template.txt`: 「ストリームオフライン」通知用。

#### `images/`

*   **役割:** Bluesky投稿に添付できる画像を保存します。
*   **ファイル:** `noimage.png` (デフォルト/プレースホルダー画像)。

#### `logs/`

*   **役割:** ランタイムログファイルが保存されるディレクトリ。
*   **ファイル (リポジトリ内):** `.gitkeep` (ディレクトリがGitによって追跡されるようにするため)。
*   **ファイル (ランタイム):** `app.log`, `error.log`, `audit.log`, `post_history.csv` (アプリケーションによって生成)。

#### `Docker/`

*   **役割:** Dockerを使用してアプリケーションをビルドおよび実行するためのファイルを含みます。
*   **ファイル:**
    *   `Dockerfile`: Dockerイメージをビルドするための指示（README.mdによると特にWindowsコンテナ用）。
    *   `docker-compose.yml`: Dockerコンテナでのアプリケーションの実行を簡素化します。
    *   `docker_readme_section.md`: メインREADME.mdのDockerセクション用のMarkdownコンテンツ。

### 4. 開発とCI/CDセットアップ

#### `.github/`

*   **役割:** コミュニティの健全性と自動化のためのGitHub固有ファイル。
*   **`ISSUE_TEMPLATE/バグ報告-改善要望.md`:** バグレポートと機能強化リクエスト用の日本語テンプレート。
*   **`workflows/gitguardian.yml`:** `dev`ブランチへのプッシュ/PR時にGitGuardianを使用してシークレットをスキャンするGitHub Actionsワークフロー。(注意: ワークフローファイル自体には、`ggshield` の実際の実行ステップの追加が必要な場合があります)。

#### `.pre-commit-config.yaml`

*   **役割:** pre-commitフックを設定します。
*   **機能:** 各コミット前にシークレットを自動的にスキャンするために `ggshield` を統合します。

#### `pytest.ini`

*   **役割:** `pytest` の設定ファイル。
*   **機能:** 現在、アクティブな `pytest` 設定は含まれていません（コメントのみ）。そのため、`pytest` はデフォルト設定で実行されます。

#### `tests/`

*   **役割:** アプリケーションの自動テストを含みます。
*   **構造:**
    *   `__init__.py`: ディレクトリをPythonパッケージとしてマークします。
    *   `test_bluesky.py`: `bluesky.py` のテスト。
    *   `test_eventsub.py`: `eventsub.py` のテスト。
    *   `test_main.py`: `main.py` のテスト。
    *   `test_utils.py`: `utils.py` のテスト。
*   **フレームワーク:** `pytest`

### 5. ドキュメントファイル

#### `README.md`

*   **役割:** メインのドキュメントファイル。概要、機能、セットアップ手順、使用方法、FAQ、Docker手順、および貢献情報を提供します。
*   **主要情報:** Windows、Cloudflare Tunnel、`settings.env` の詳細なセットアップ手順。通知とテンプレートのカスタマイズ方法を説明します。

#### `document/CONTRIBUTING.md`

*   **役割:** 貢献者向けの詳細なガイドラインを提供します。
*   **主要情報:** 環境設定（Docker、手動）、バグ報告、機能強化の提案、PRプロセス、コーディング規約、テストの実行、pre-commitフック。

#### `document/comprehensive_summary_japanese.md` (以前は `document/comprehensive_summary_japanese.txt`)

*   **役割:** アプリケーションの詳細な日本語の要約。
*   **主要情報:** 目的、主要機能、技術スタック、およびセットアップ概要をカバーしています。

#### `document/consolidated_summary_japanese.md` (以前は `document/consolidated_summary_japanese.txt`)

*   **役割:** 日本語での内部メモ/推奨事項のようです。
*   **主要情報:** `pytest`/`autopep8` の潜在的な改善点、WindowsのCI設定、GUIの必要性（現在は不可欠ではないと結論）、およびトンネリング機能の強化（`ngrok` のサポート、開発者提供トンネルの実現可能性）について議論しています。

#### `document/contributing_readme_section.md` (日本語版は `document/contributing_readme_section.ja.md`)

*   **役割:** メインREADME.mdの貢献セクション用の小さなMarkdownスニペットで、`CONTRIBUTING.md` (日本語版では `CONTRIBUTING.ja.md`) にリンクしています。

#### `LICENSE`

*   **役割:** ソフトウェアが配布される法的条件を指定します。
*   **ライセンス:** GNU General Public License v2 (GPL-2.0)。

### 全体概要

このプロジェクト「Stream notify on Bluesky」は、指定されたTwitchチャンネルがライブになったとき、またはオフラインになったときにBlueskyに自動的に通知するように設計された、よく構造化されたPythonボットです。リアルタイムのイベント検出のためにTwitchのEventSubシステムを活用し、ローカルマシンでこれらのイベントを受信するためにCloudflare Tunnelを利用しています。

プロジェクトの主な強みは次のとおりです:

*   **モジュール性:** コードは明確な責任を持つ個別のモジュールによく整理されています。
*   **設定:** `settings.env` を介して広範な設定オプションが利用可能です。
*   **堅牢性:** API呼び出しのリトライ、ウェブフック署名検証、詳細なロギングなどの機能を備えています。
*   **セキュリティ:** ウェブフック署名検証とシークレットローテーションが含まれています。GitGuardianが統合されています。
*   **自動化:** CIにGitHub Actionsを使用し、pre-commitフックを利用しています。
*   **テスト:** 優れたテストスイートが存在します。
*   **ドキュメント:** 英語と日本語の包括的なドキュメント。
*   **コンテナ化:** Dockerサポートによりデプロイが簡素化されます。

アプリケーションはGPLv2でライセンスされています。
