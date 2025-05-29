# Stream notify on Blueskyへの貢献

まずはじめに、貢献をご検討いただきありがとうございます！このプロジェクトを改善するためのどんな助けも歓迎します。\
バグの報告、新機能の提案、コードの記述など、あなたの貢献は価値があります。

## はじめに

### 開発環境のセットアップ

一貫した開発環境のために、Dockerの使用を強く推奨します。

*   **Dockerを利用する場合 (推奨):**
    1.  Windows用のDocker Desktopがインストールされ、Windowsコンテナ用に設定されていることを確認してください。
    2.  `README.md`の「Dockerでの実行 (Windowsコンテナ)」セクションの指示に従って、イメージをビルドし、コンテナを実行してください。
    3.  ローカルでファイルを編集することで開発が可能です。適切にボリュームマウントを設定していれば（例えばソースコード用。\
    ただし、提供されている`docker-compose.yml`は主に`settings.env`と`logs`をマウントします）、Dockerはこれらの更新されたファイルを使用します。\
    活発な開発のためには、`docker-compose.override.yml`や開発専用のcomposeファイルにソースコードのボリュームマウントを追加すると良いでしょう。
    4.  READMEで説明されているように、`settings.env`ファイルを作成し、設定することを忘れないでください。

*   **手動でのPythonセットアップ:**
    1.  お使いのWindowsマシンにPython 3.10以上がインストールされていることを確認してください。
    2.  リポジトリをクローンします: `git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git`
    3.  プロジェクトディレクトリに移動します: `cd Twitch-Stream-notify-on-Bluesky`
    4.  仮想環境を作成します: `python -m venv venv`
    5.  仮想環境をアクティベートします: `.\venv\Scripts\activate`
    6.  依存関係をインストールします: `pip install -r requirements.txt`
    7.  `development-requirements.txt`ファイルが存在する場合は、それらもインストールします: `pip install -r development-requirements.txt` (これには通常、`pytest`、`autopep8`、`pre-commit`のようなパッケージが含まれます)。
    8.  `settings.env.example`を`settings.env`にコピーし、あなたの認証情報を記入してください。

### `settings.env` の設定
セットアップ方法に関わらず、APIキーと設定を記述した`settings.env`ファイルを**必ず**作成し、設定する必要があります。\
詳細は`settings.env.example`を参照してください。

### トンネル要件について
- Cloudflare Tunnel「のみ」必須ではありません。ngrok、localtunnel、カスタムトンネルもサポートされています。
- TUNNEL_SERVICE環境変数でサービスを切り替え、各種コマンド（TUNNEL_CMD/NGROK_CMD/LOCALTUNNEL_CMD/CUSTOM_TUNNEL_CMD）でトンネルを起動・管理します。
- コマンド未設定時は警告ログを出し、トンネルは起動しません。終了時はterminate/waitで正常終了、タイムアウトや例外時はkillで強制終了し、詳細なログを出力します。
- 詳細はREADME.mdの「トンネル要件」セクションを参照してください。

### テンプレートファイルの扱い
- デフォルトテンプレートファイルは `.templates/` ディレクトリ配下の `_default_` で始まるファイルです。
- これらのファイルは**直接編集・削除しないでください**。カスタマイズは別名でコピーして行ってください。

### GUI仕様の注意
- 設定エディタはタブ構成で、各種設定は即時反映・保存完了メッセージが表示されます。
- 設定ファイルやテンプレートの変更はGUIから行うことを推奨します。

### 未使用ファイルの整理
- 未使用・古いGUIフレームや不要なファイルは、定期的に整理・削除してください。

## 貢献方法

### バグ報告

*   バグ報告を提出する前に、[GitHub Issues](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues)でバグが既に報告されていないか確認してください。
*   問題に対処するオープンなIssueが見つからない場合は、[新しいIssueを開いてください](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues/new)。
*   **タイトルと明確な説明**、関連する情報、そして問題を再現する手順を必ず含めてください。

### 機能強化の提案

*   新機能のアイデアや既存機能の改善案がある場合は、[GitHub Issues](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues)で既に提案されていないか確認してください。
*   提案されていない場合は、気軽に[新しいIssueを開いて](https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky/issues/new)あなたのアイデアを議論してください。

### プルリクエスト (PR) プロセス

1.  GitHubでリポジトリを**フォーク**します。
2.  あなたのフォークをローカルに**クローン**します: `git clone https://github.com/YOUR_USERNAME/Twitch-Stream-notify-on-Bluesky.git`
3.  変更のための新しい**ブランチを作成**します。`development`ブランチからブランチを作成するのが良い習慣です: `git checkout -b your-feature-branch development`
4.  **変更を行い**、明確で説明的なコミットメッセージと共にコミットします。
5.  **すべてのテストがパスすることを確認**します。(下記の「テストの実行」を参照)。
6.  変更が必要な場合は、**ドキュメントを更新**します (`README.md`、コメントなど)。
7.  あなたのブランチをGitHubのあなたのフォークに**プッシュ**します: `git push origin your-feature-branch`
8.  あなたのブランチから`mayu0326/Twitch-Stream-notify-on-Bluesky`リポジトリの`development`ブランチへ**プルリクエストを開き**ます。
9.  PRには変更内容の明確な説明を記載してください。関連するIssueがあれば参照してください。

## コーディング規約

*   すべてのPythonコードは**PEP 8**スタイルガイドラインに従うべきです。
*   自動フォーマットのために`autopep8`の使用を目指しています。もしpre-commitフックに統合されていれば、一貫性の維持に役立ちます。
*   明確で説明的な変数名と関数名を使用してください。
*   複雑なロジックを説明するために必要な場合はコメントを含めてください。

## テストの実行

*   テストスイートを実行するには (`pytest`を使用):
    ```bash
    python -m pytest tests/
    ```
*   **開発にDockerを使用している場合:**
    実行中のコンテナ内でテストを実行できます:
    ```bash
    # docker-composeサービス名が'twitch-bluesky-bot'の場合
    docker-compose exec twitch-bluesky-bot python -m pytest tests/
    ```
    または、コンテナ内でシェルを実行している場合:
    ```bash
    python -m pytest tests/
    ```

## Pre-commitフック

このプロジェクトでは、pre-commitフックの管理と維持のために`pre-commit`を使用しています。
現在のセットアップには以下が含まれます:
*   `ggshield` (シークレットスキャンのためのGitGuardian)。
*   (議論されているように`autopep8`が追加された場合はそれも)。

フックを使用するには:
1.  `pre-commit`をインストールします: `pip install pre-commit`
2.  gitフックスクリプトをセットアップします: `pre-commit install`
3.  これで、`git commit`時に`pre-commit`が自動的に実行されます！
4.  すべてのファイルに対して手動で実行するには: `pre-commit run --all-files`

## コードレビュープロセス

プルリクエストを提出すると、プロジェクトのメンテナーがあなたの変更をレビューします。修正を依頼したり、フィードバックを提供したりすることがあります。私たちはタイムリーにPRをレビューすることを目指しています。

## 質問はありますか？

質問がある場合は、GitHubで気軽にIssueを開いてください。
