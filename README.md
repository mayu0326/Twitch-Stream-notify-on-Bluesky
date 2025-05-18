# Twitch Stream notify on Bluesky

Twitch 配信開始を自動検知し、Bluesky へリアルタイムにお知らせ投稿する Python 製 Bot です。  
Cloudflare Tunnel による Webhook 受信、エラー通知、履歴記録など運用に便利な機能を多数備えています。

---

## 主な特徴
### 基本機能
- **Twitch EventSub Webhook**で配信開始を自動検知
- 不要な**Twitch EventSub サブスクリプション**の自動クリーンアップ
- **Cloudflare Tunnel**でローカル環境でも Webhook 受信
- **設定ファイル**で設定を細かくカスタマイズ可能
- **Discord へのエラー通知**・通知レベルの管理や機能オフも可能
- **ログファイル・コンソール出力**のログレベルは設定ファイルで調整可能
- **APIエラー時**の自動リトライ機能(回数や間隔も調整可能)

### 投稿関連
- **Bluesky**へ自動で配信開始通知を投稿
- **Bluesky**へ投稿する内容はテンプレートで切り替え可能
- **Bluesky**へ投稿するとき特定の画像を添付することも可能
- **Bluesky**投稿した内容をCSVで投稿履歴として記録

### 安全・保守機能
- **Webhook署名**のタイムスタンプ検証による**リプレイ攻撃対策**
- **監査ログ**の保存機能を実装しているので、操作履歴の確認に活用可能
- **自動テスト**機能による品質管理を実装（tests/ディレクトリ）

- 拡張性・保守性を考慮したモジュール分割設計

---

## 必要な環境
### パソコン環境
- Windows10以降（11を推奨）
**※LinuxやMacには対応していません。**
- Python 3.10 以上 推奨
- Git 2.49 以上 推奨
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) （事前インストール必須）

### アカウント関連
- Twitch のユーザーID（EventSub 用）
- Twitch APIのクライアントIDとクライアントシークレット(デベロッパーコンソールから取得)
- Bluesky アカウント（投稿用）
- Cloudflareのアカウント（Cloudflare Tunnel用）

### その他に必要なもの
- CloudflareでDNS管理されている独自ドメイン（推奨）
---
## ファイル構成
このプログラムは以下のファイル構成/フォルダで構成されています。

```
プロジェクトルート/
├── bluesky.py          ← Blueskyへの投稿処理を担当
├── eventsub.py         ← Twitch EventSub関連の機能を担当
├── logging_config.py   ← ログ設定、Discord通知設定を担当
├── main.py             ← Flaskサーバーの起動・ルーティング・主要な機能の呼び出し
├── tunnel.py           ← Cloudflare Tunnel の起動終了の管理
├── utils.py            ← 汎用的な処理をまとめたユーティリティ
├── settings.env.example ← 認証情報・設定ファイルのサンプル
├── requirements.txt     ← Pythonパッケージのインストール用リスト
├── README.md
├── images/              ← 投稿用画像やサムネイル等を格納
│   └── …  
├── templates/           ← Bluesky投稿テンプレートを格納
│   └── …  
├── logs/                ← アプリ実行時のログファイル出力先
│   └── …  
├── Cloudflared/
│   └── config.yml.example  ← Cloudflare Tunnel 設定ファイルのサンプル
└── tests/               ← pytestテストコードを格納
    ├── test_bluesky.py
    ├── test_eventsub.py
    ├── test_main.py
    └── test_utils.py

```

---
## セットアップ手順

### 1. **リポジトリをクローン**

   ```
   git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git
   cd Twitch-Stream-notify-on-Bluesky
   ```

### 2. **Python パッケージをインストール**

   ```
   pip install -r requirements.txt
   ```

### 3. **Cloudflare Tunnel をインストール**  
   [公式手順](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)に従い、 cloudflared（cloudflared.exe 等）をインストールしてください。\
   ※簡単なのは**公式のwingetコマンド**でインストールすることです。\
   ※場合によっては**Pathの設定**が必要な場合があります。

### 4. **Cloudflare Tunnel をセットアップ**

- Cloudflare Zero Trust でトンネルを作成し、設定ファイル(config.yml)を準備してください。\
※詳細は[Cloudflare Tunnel 公式ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)を参照。
- **Cloudflaredの設定ファイル config.yml のサンプル**は「Cloudflared」フォルダにあります。\
必要に応じてコピーしてファイル名を以下のように変更し、\
Cloudflaredインストール先のフォルダに置いてください。
  ```
  config.yml.example → config.yml に変更する
  ``` 
- cloudflaredのインストール先は以下の場所です。
  ```
  C:\Program Files (x86)\cloudflared\cloudflared.exe 
  ``` 

### 5. **settings.env を編集**  
  - settings.env.example をコピーして settings.env を作成し、必要な値を記入してください。\
   ※WEBHOOK_SECRETは初回起動時に自動生成されます。\
   ※シークレットの最終生成日時はSECRET_LAST_ROTATEDに自動で入力されます。\
  ### settings.envの設定例

   ```
   # Twitch設定
   TWITCH_CLIENT_ID=デベロッパーコンソールで取得したクライアントID
   TWITCH_CLIENT_SECRET=デベロッパーコンソールで取得したクライアントシークレット
   TWITCH_BROADCASTER_ID=あなたのTwitchユーザーID

   # Bluesky設定
   BLUESKY_USERNAME=xxxxxxx.bsky.social または 独自ドメイン等ご利用中のID
   BLUESKY_PASSWORD=Blueskyのアプリパスワード
   BLUESKY_IMAGE_PATH=images/noimage.png
   BLUESKY_TEMPLATE_PATH=templates/default_template.txt

   # Webhook設定
   WEBHOOK_SECRET=
   SECRET_LAST_ROTATED=
   WEBHOOK_CALLBACK_URL=Webhookを受け取り可能なドメインのURL
   例えば、https://example.net/webhook

   # Discord通知設定
   discord_error_notifier_url=https://discord.com/api/webhooks/xxxxxx/xxxxxx
   discord_notify_level=CRITICAL

   # ログ関連機能の設定
   LOG_LEVEL=INFO
   LOG_RETENTION_DAYS=14

   # Cloudflareトンネルの設定
  TUNNEL_CMD=トンネルの起動コマンドを指定する。

   # APIエラー時のリトライ
   RETRY_MAX=3
   RETRY_WAIT=2
   ```

### 6. **Blueskyへ投稿する際の投稿テンプレートの作成・編集(オプション)**

- templates/ ディレクトリにある**default_template.txt**をコピーして、\
内容を書き換えてください。
- テンプレートを編集しない場合はデフォルトを使用して投稿します。
- **settings.env** の **BLUESKY_TEMPLATE_PATH** を、\
使用するテンプレートのファイル名に書き替えるとテンプレートの切り替えができます。

### 7. **Bot を起動**

   ```
   python main.py
   ```

---

## 使い方・カスタマイズ

### **通知レベルの変更**
  settings.env で`discord_notify_level`（例：CRITICAL, ERROR, INFO）を変更できます。
### **ログレベルの一括変更**
  settings.env で`LOG_LEVEL`（例：CRITICAL, ERROR, INFO）を変更できます。\
  ※コンソール表示とログ保存の２つをまとめて変更します。
### **Bluesky 投稿履歴**
  すべての投稿履歴は`logs/post_history.csv`に自動記録されます。
### **トンネルコマンドのカスタマイズ**
  ngrok 等、他のトンネルサービスにも\
  `TUNNEL_CMD`を書き換えることで対応可能です(ただしサポート対象外)。
### **投稿テンプレートの切り替え**
テンプレートを編集しない場合は以下の内容が投稿されます。
  ```
  🔴 放送を開始しました！
  {display_name} has started streaming on Twitch now! 
  タイトル: {title}
  カテゴリ: {category}
  URL: {url} 
  #Twitch配信通知
  ```
 ##### **テンプレートに使用できる変数は以下のとおりです。**
  ```
  {title} ：配信タイトルです
  {category}：配信カテゴリです
  {url}：配信場所のURLです
  {username}：ユーザー名です
  {display_name}：ユーザー名(表示名)です
  ```
- テンプレートを切り替える場合、\
**settings.env** の **BLUESKY_TEMPLATE_PATH** を使用するテンプレートの\
ファイル名に書き換えてください。
- **テンプレートファイルが見つからない場合**は、エラーログが記録され、\
デフォルトテンプレートが利用されます。
---

## よくある質問（FAQ）

### ドメイン・トンネル関連
<details>

### Q. ドメインをもっていなくても利用できますか？

A. アプリ自体は、ngrokなど他のサービスを使う事によって使用できます。\
ただし、**具体的な設定方法の説明や動作保証、およびサポート対象の範囲外**とさせていただいています。

### Q. Cloudflare以外でDNS管理をしていない場合でもこのアプリを利用できますか？

A. アプリ自体は、ngrokなど他のサービスを使う事によって使用できます。\
ただし、以下の制約があります。
- Cloudflare Tunnelは、\
独自ドメインの所有やCloudflareによるDNS管理が前提となるため、\
**ドメインを持っていない場合**や**CloudflareでDNSを管理していない場合**には利用できません。

- ドメインをCloudflareのDNSで管理していない場合は、\
**ngrokなどほかの方法で接続を行う必要があります**が、具体的な設定方法の説明や動作保証、\
およびサポート対象の範囲外とさせていただいています。
</details>

### エラー関連
<details>

### Q. cloudflared がインストールされていませんと出ます

A. 事前に[公式ページ](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)から cloudflared をダウンロードし、\
settings.env の TUNNEL_CMD でパスを正しく指定してください。\
※運用環境によってはPathをダブルクォーテーションで囲って記載する必要がある場合があります。
- (例：)wingetコマンドでインストールした場合の記載例
  ```
  TUNNEL_CMD="C:\Program Files (x86)\cloudflared\cloudflared.exe tunnel --config C:\Program Files (x86)\cloudflared\config.yml run <トンネル名>"
  ```

### Q. テンプレートファイルが見つからないというエラーがでます。

A. **ファイル名の指定**が間違っている可能性があるので確認してください。\
指定した**ファイルが存在するかどうか**も確認してください。

**正しいファイル名の指定形式**は以下のとおりです。
  ```
  BLUESKY_TEMPLATE_PATH=templates/default_template.txt
  ```

ファイル名指定の際、**/から書いてしまうと認識できない**ことがあります。\
また、**拡張子を記載しない場合も認識できない**ことがあるので注意してください。
</details>

### アプリの通信関連
<details>

### Q. アプリの疎通確認方法がわかりません。

A. アプリを起動後、設定したWebhookエンドポイントのURLにブラウザでアクセスしてください。\
下記の状態であれば、外部との通信ができる状態になっています。
- ブラウザの表示が **Webhook endpoint is working! POST requests only.** である。
- コンソールの出力に **Webhookエンドポイントは正常に稼働しています**というinfoログがある。

### Q. アプリにはエラーが出力されていないのに疎通確認が取れません。

A. 次のどれかが原因の可能性があります。
- Cloudflare側でドメインとトンネルの紐付けができていない\
→ **DNSのCNAMEレコードが正しい値であるか**、Cloudflareダッシュボードで確認してください。

- CNAMEレコードがトンネルのUUID.cfargotunnel.comに向いていない、またはAレコードになっている\
→ **必ずCNAMEでUUID.cfargotunnel.comに向けてください**。

- Cloudflare DNSでドメインを管理していない（外部DNSや未設定）\
→ Cloudflare DNSで管理していない場合、**独自ドメインでのトンネル公開はできません**。

- トンネル名やUUIDの設定ミス\
→ cloudflared tunnel listで表示されるUUIDと、DNS設定のCNAME先が**一致しているか確認してください**。\
一致していない場合は、DNS設定を一致するように書き換えてください。
</details>

### 認証情報関連
<details>

### Q. Twitch/Bluesky/Discord の認証情報はどこで取得しますか？

A. 各サービスの公式サイトから必要な API キーやパスワードを取得してください。\
Bluesky：アプリパスワード(Blueskyの設定→プライバシーとセキュリティー→アプリパスワード)\
Twitch：ユーザーID(アカウント)、クライアントID(Devポータル)、クライアントシークレット(Devポータル)\
Discord：WebhookURL(Discordサーバーの設定→連携サービス→Webhook)
</details>

### Bluesky投稿関連
<details>

### Q. 投稿文のテンプレートを変更したい／多言語対応したい

A. templates/ ディレクトリにテンプレートを追加し、\
**settings.env** の **BLUESKY_TEMPLATE_PATH**を切り替えてください。

### Q. 配信終了時にも Bluesky に投稿したい

A. 現状は配信開始のみ対応ですが、今後のアップデートで追加予定です。

### Q. Blueskyに投稿する時に画像を添付したい

A. imagesフォルダに画像を置いて、settings.envの`BLUESKY_IMAGE_PATH`にファイル名を設定してください。
- Blueskyに投稿できる画像形式はJPEG（.jpg/.jpeg）、PNG（.png）、静止画GIFです。\
アニメーションGIF投稿できません。
- Blueskyへの動画投稿には対応していません。
- 画像サイズは1MB以下を推奨します
- 初期設定ではimages/noimage.pngが設定されています。\
また、現状では画像は１枚だけ添付できます。

- **ファイル名の指定**が間違っている場合、デフォルト画像が使用されます。

- **正しいファイル名の指定形式**は以下のとおりです。
  ```
  BLUESKY_IMAGE_PATH=images\noimage.png
  ```
ファイル名指定の際、**/から書いてしまうと認識できない**ことがあります。\
また、**拡張子を記載しない場合も認識できない**ことがあるので注意してください。

</details>

### セキュリティ・保守関連
<details>

### Q. セキュリティ対策はどうなっていますか？

A. このBotはWebhook署名のタイムスタンプ検証によるリプレイ攻撃防止や、\
APIエラー時の自動リトライ機能を備えています。\
また、リトライの回数や間隔は設定ファイルから変更が可能です。

### Q. 監査ログはどこに記録されますか？

A. logs/audit.log に主要な操作履歴が記録されます。

### Q. WEBHOOK_SECRETを変更したいときはどうしたらいいですか？

A. もし運用中に手動でシークレットを変更したい場合は、\
settings.envの**WEBHOOK_SECRETとSECRET_LAST_ROTATEDを空欄にして**再起動してください。\
そうすれば、次回起動時に再生成されます。
</details>

## 開発・運用上の注意

- この Bot は個人運用・検証を想定しています。商用利用や大規模運用時は自己責任でお願いします。
- セキュリティのため、API キーやパスワードは絶対に公開リポジトリに含めないでください。
- **APIエラー発生時**は自動でリトライ処理を行います。\
また、Webhook署名のタイムスタンプを検証するようになっているため、\
リプレイ攻撃の防止にも効果があります。
- TwitchAPI の利用規約により**API キーの使い回し**や**複数人利用は禁止**されております。\
  利用者側で[Twitch デベロッパーポータル](https://dev.twitch.tv/)にアクセスし、\
  **アプリケーションの登録**と**API キーを生成**してお使いください。
- WEBHOOK_SECRETは30日ごとに自動でローテーションされるため**通常は編集不要**です。
- 監査ログ（logs/audit.log）には重要な操作履歴が記録されます。\
運用時はアクセス権限や保管期間に注意してください。
- 不要なEventSubサブスクリプションはBot起動時に自動削除されます。

---

## 自動テストの実行方法

本アプリケーションは主要な機能やバリデーションの自動テストを備えています。  
テストは [pytest](https://docs.pytest.org/) で簡単に実行できます。

### テストの実行手順

<details>

1. 必要なパッケージをインストール（未インストールの場合）

 ```
 pip install pytest
 ```
2. プロジェクトルートで以下のコマンドを実行
 ```
python -m pytest
 ```
- 特定のテストファイルだけを実行したい場合は
 ```
 pytest test/test_utils.py
 ```

3. テスト結果が表示され、すべてのテストがパスすればOKです。

</details>

### テストの補足

- テストコードは `test/` ディレクトリにあります。
- テストの追加や修正はこのディレクトリ内の各ファイルに記述してください。
- 詳細な使い方は [pytest公式ドキュメント](https://docs.pytest.org/) を参照してください。
---
### 今後の開発予定

---
## ライセンス

GPL License v2

---

## 開発・メンテナンス

- 作者: まゆにゃ（@mayu0326）
- 連絡先：下記のいずれかへ。\
BlueSky:neco.mayunyan.tokyo\
Web:https://mayunyan.tokyo/contact/personal/
- 本アプリケーションはオープンソースです。Issue・PR 歓迎！

---
