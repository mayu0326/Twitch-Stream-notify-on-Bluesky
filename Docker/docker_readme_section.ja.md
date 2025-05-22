## Dockerでの実行 (Windowsコンテナ)

このアプリケーションは、Windowsコンテナを使用してDockerコンテナ内で実行できます。これは、アプリケーションとその依存関係を分離するのに特に便利です。

### 前提条件

*   **Docker Desktop for Windows:** Docker Desktopをインストールし、**Windowsコンテナ**を使用するように設定していることを確認してください。

### セットアップ

1.  **`settings.env`の設定:**
    *   Dockerコンテナをビルドまたは実行する前に、プロジェクトのルートディレクトリにある`settings.env.example`ファイルを`settings.env`にコピーしてください。
    *   `settings.env`を編集し、必要なすべての認証情報と設定詳細（Twitch APIキー、Bluesky認証情報など）を記入してください。このファイルはコンテナにマウントされます。

### 推奨: Docker Composeの使用

Docker Composeは、コンテナのライフサイクルを簡単に管理する方法を提供します。プロジェクトルートに`docker-compose.yml`ファイルが提供されています。

*   **アプリケーションの起動 (デタッチモード):**
    ```bash
    docker-compose up -d
    ```
*   **ログの表示:**
    ```bash
    docker-compose logs -f twitch-bluesky-bot
    ```
    （実行中のサービスがこれだけの場合は`docker-compose logs -f`も使用できます）
*   **アプリケーションの停止:**
    ```bash
    docker-compose down
    ```
*   **アプリケーションの再ビルドと更新 (例: コード変更やDockerfile更新後):**
    ```bash
    docker-compose build && docker-compose up -d --force-recreate
    ```

### 代替案: `docker run`の使用

Dockerコマンドを使用して手動でコンテナをビルドおよび実行することもできます。

1.  **Dockerイメージのビルド:**
    イメージにカスタム名をタグ付けしたり、最初からビルドすることを確認したい場合:
    ```bash
    docker build -t your-custom-name/twitch-bluesky-bot .
    ```
    （カスタム名を指定しない場合は、`docker-compose.yml`で使用されているタグに依存するか、特定のタグなしでビルドし、その後イメージIDを使用する可能性があります）。

2.  **Dockerコンテナの実行:**
    このコマンドは、ローカルの`settings.env`と`logs`ディレクトリをコンテナにマウントします。
    ```bash
    docker run --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
    ```
    *   **注意:** `your-custom-name/twitch-bluesky-bot`を`docker build`コマンド中に使用したタグ（またはタグ付けしなかった場合はイメージID）に置き換えてください。
    *   `%CD%`はWindowsコマンドプロンプトの現在のディレクトリを指します。PowerShellを使用している場合は、`$(pwd)`を使用するか、絶対パスを指定する必要がある場合があります。
    *   デタッチモード（バックグラウンド）で実行するには、`-d`フラグを追加します:
        ```bash
        docker run -d --name twitch-bluesky-bot-manual -v "%CD%\settings.env:C:\app\settings.env" -v "%CD%\logs:C:\app\logs" your-custom-name/twitch-bluesky-bot
        ```

### ログへのアクセス

*   Docker Composeまたは指定されたボリュームマウントで`docker run`を使用する場合、アプリケーションログはローカルマシンのプロジェクトルートにある`./logs`ディレクトリに永続化されます。これにより、コンテナが停止した後でもログファイルにアクセスできます。
