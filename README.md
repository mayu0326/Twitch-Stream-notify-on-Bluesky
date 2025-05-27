# Stream notify on Bluesky

- Twitch/YouTube/ニコニコ生放送の配信開始を自動検知し、\
Bluesky へリアルタイムにお知らせ投稿する Python 製 Bot です。
- Youtubeとニコニコについては、放送だけでなく動画投稿の通知にも対応します。    
- Cloudflare Tunnel **または他のトンネル（ngrok, localtunnel, customコマンド）**による Webhook 受信、エラー通知、履歴記録など\
運用に便利な機能を多数備えています。
- **トンネル（Cloudflare/ngrok/localtunnel/custom）自動管理・URL自動反映・GUI連携に対応**
- **テンプレート・画像パスはtemplates/・images/配下の場合、相対パスでsettings.envに保存されます**

---

## 主な特徴
### 基本機能
- **Twitch EventSub Webhook**で配信開始/終了を自動検知
- 不要な**Twitch EventSub サブスクリプション**の自動クリーンアップ
- **YouTubeLive/ニコニコ生放送**の放送開始の検知に対応(終了は非対応)
- **Youtube動画/ニコニコ動画**のアップロード検知(App起動後の新着のみ)に対応
- **Cloudflare Tunnel/他トンネル（ngrok, localtunnel, customコマンド）**でローカル環境でも Webhook 受信
- **トンネルの自動起動・URL自動反映・GUI連携**（main.pyで自動管理、GUIに即時反映）
- **Webhook/URLタブ分離・自動反映・編集可否**（GUIでURLの自動取得・編集可否切替）
- **設定保存時は「保存完了」メッセージを表示し、GUIに即時反映**
- **設定ファイル**で設定を細かくカスタマイズ可能
- **Discord へのエラー通知**・通知レベルの管理や機能オフも可能
- **ログファイル・コンソール出力**のログレベルは設定ファイルで調整可能
- **APIエラー時**の自動リトライ機能(回数や間隔も調整可能)

### 投稿関連
- **Bluesky**へ自動で配信開始/終了通知を投稿(各サービスごとに個別On/Off可能)
- **Bluesky**へ投稿する内容は各サービスごとにテンプレートで切り替え可能
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
- Windows10以降（11を推奨）\
**※このアプリはWindows専用です**\
**※LinuxやMacには対応していません。**
- Python 3.10 以上 推奨
- Git 2.49 以上 推奨
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) または他のトンネル（ngrok, localtunnel, customコマンド）
  （いずれかのトンネルの事前インストール必須）

### アカウント関連
- Twitch のユーザーID（EventSub 用）
- Twitch APIのクライアントIDとクライアントシークレット(デベロッパーコンソールから取得)
- Bluesky アカウント（投稿用）
- Cloudflareのアカウント（Cloudflare Tunnel用、Cloudflare利用時のみ）

### その他に必要なもの
- CloudflareでDNS管理されている独自ドメイン（推奨）\
または[ngrokなど]他のトンネルソフト(サポート対象外)
---
## ファイル構成
このプログラムは以下のファイル構成/フォルダで構成されています。

```
プロジェクトルート/
├── bluesky.py
├── eventsub.py
├── logging_config.py
├── main.py
├── niconico_monitor.py
├── tunnel.py
├── utils.py
├── version.py
├── youtube_monitor.py
├── requirements.txt
├── development-requirements.txt
├── settings.env.example
├── LICENSE
├── pytest.ini
├── README.md
├── logs/
│   └── ...(ログや投稿履歴はこちらに保存されます)
├── images/
│   └── noimage.png
├── document/
│   ├── ARCHITECTURE.ja.md
│   ├── ARCHITECTURE.md
│   ├── comprehensive_summary_japanese.md
│   ├── consolidated_summary_japanese.md
│   ├── CONTRIBUTING.ja.md
│   └── CONTRIBUTING.md
├── templates/
│   ├── default_offline_template.txt
│   ├── default_online_template.txt
│   ├── nico_new_video_template.txt
│   ├── nico_online_template.txt
│   ├── twitch_offline_template.txt
│   ├── twitch_online_template.txt
│   ├── yt_new_video_template.txt
│   └── yt_online_template.txt
├── tests/
│   ├── __init__.py
│   ├── test_bluesky.py
│   ├── test_eventsub.py
│   ├── test_integration.py
│   ├── test_main.py
│   ├── test_performance.py
│   ├── test_utils.py
│   ├── test_youtube_niconico_monitor.py
│   └── tunnel_tests.py
├── gui/
│   ├── account_settings_frame.py
│   ├── app_gui.py
│   ├── bluesky_notification_frame.py
│   ├── bluesky_post_settings_frame.py
│   ├── console_output_viewer.py
│   ├── discord_notification_frame.py
│   ├── logging_console_frame.py
│   ├── log_viewer.py
│   ├── main_control_frame.py
│   ├── niconico_notice_frame.py
│   ├── notification_customization_frame.py
│   ├── settings_editor_dialog.py
│   ├── setup_wizard.py
│   ├── timezone_settings.py
│   ├── tunnel_connection.py
│   ├── twitch_notice_frame.py
│   ├── youtube_notice_frame.py
│   └── ユーザーマニュアル_StreamNotifyonBluesky_GUI設定エディタ.txt
├── Cloudflared/
│   └── config.yml.example
├── Docker/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── docker_readme_section.ja.md
    └── docker_readme_section.md
```

---
## セットアップ手順
- **※このアプリはWindows専用です。LinuxやMacには対応していません。**
- もし仮にWindows以外の環境で動いたとしてもサポート対象外です。

### 1. **リポジトリをクローン**

   ```
   git clone https://github.com/mayu0326/Twitch-Stream-notify-on-Bluesky.git
   cd Twitch-Stream-notify-on-Bluesky
   ```

### 2. **Python パッケージをインストール**

   ```
   pip install -r requirements.txt
   ```
  - 開発者の方はdevelopment-requirements.txtのほうをお使いください。

### 3. **Cloudflare Tunnel または他のトンネル（ngrok, localtunnelなど）をインストール**  
- CloudflareTunnelをご利用の場合は、[公式手順](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)に従い、 cloudflared（cloudflared.exe 等）をインストールしてください。\
- ngrokやlocaltunnelを利用する場合は、各公式手順に従いインストールしてください。 
- その他、本アプリケーションおよびGUIに対応していないトンネルサービスはcustomコマンドでご利用いただけます。\
※場合によっては**Pathの設定**が必要な場合があります。

### 4. **Cloudflare Tunnel または他のトンネルをセットアップ**

- CloudflareTunnelをご利用の場合は、Cloudflare Zero Trust でトンネルを作成し、\
設定ファイル(config.yml)を準備してください。\
※詳細は[Cloudflare Tunnel 公式ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)を参照。
- **Cloudflaredの設定ファイル config.yml のサンプル**は、\
本アプリケーションの「Cloudflared」フォルダ内にあります。
- 必要に応じてコピーを作成して、ファイル名を以下のように変更してください。
  ```
  config.yml.example → config.yml に変更する
  ``` 
- 上の手順で作成したcloudflaredの設定ファイル(config.yml)は以下の場所に置いてください。\
※すでにトンネルuuidのjsonとcert.pemがあるフォルダです。
  ```
  C:\Users\[お使いのパソコンのuser名]\.cloudflared\config.yml
  ``` 
#### Cloudflare Tunnelや他のトンネルを使わない運用について
- 本アプリケーション(GUIを含む)は、CloudflareTunnel以外にngrokとlocaltunnelに対応しています。
それ以外のトンネルソフトやアプリケーションもCustomで設定していただくことにより利用可能だと思われますが、
動作確認およびサポートの対象外とさせていただいています。

### 5. **セットアップウィザードで初期設定を行う**

- 初回起動時、`settings.env` が存在しない場合は「初期設定ウィザード」が自動的に起動します。
- ウィザードはGUIで、Twitch/YouTube/ニコニコ/Blueskyアカウント・Webhook設定\
各種サイトへの通知可否・トンネル設定などをステップごとに分かりやすく案内します。
- 各ステップは「スキップ」も可能で、未入力やスキップした項目は後からGUIの設定画面で編集できます。
- 入力内容の確認・保存後、`settings.env` が自動生成されます。
- ウィザード完了後はメイン画面が自動で開きます。
- 途中でキャンセルやバツで閉じた場合はアプリが終了します。

#### ウィザードで設定できる主な項目
- Twitchアカウント・APIキー
- Webhook URL（トンネル起動時は自動取得・自動反映）
- Blueskyアカウント・アプリパスワード
- YouTube/ニコニコの監視設定
- 通知ON/OFF（6項目：Twitch/YouTube/ニコニコの放送開始/終了/動画投稿）
- トンネルコマンド（Cloudflare/ngrok/localtunnel/customコマンド対応）

> 詳細なウィザードの流れは\
`gui/ユーザーマニュアル_StreamNotifyonBluesky_GUI設定エディタ.txt` も参照してください。

---

## 使い方・カスタマイズ

### **通知レベルの変更**
**settings.env**または**設定GUI** で\
`discord_notify_level`（例：DEBUG, INFO, WARNING, ERROR, CRITICAL）を変更できます。
### **ログレベルの一括変更**
**settings.env**または**設定GUI** で\
`LOG_LEVEL`（例：DEBUG, INFO, WARNING, ERROR, CRITICAL）を変更できます。\
  ※コンソール表示とログ保存の２つをまとめて変更します。
### **Bluesky 投稿履歴**
すべての投稿履歴は`logs/post_history.csv`に自動記録されます。\
※GUIのログビューアからも投稿履歴をご確認いただけます。
### **トンネル設定のカスタマイズ**
  CloudflareTunnel,ngrok,localtonnelの設定をサポートしています。他のトンネルサービスにも\
  `TUNNEL_CMD`を書き換えることで対応可能です(ただしサポート対象外)。
### **投稿テンプレートの切り替え**
- テンプレートを切り替える場合、\
  **settings.env**または**設定GUI**の各サービス用の設定項目から、\
使用するテンプレートのファイル名を指定（書き替える）とテンプレートの切り替えができます。


- **テンプレートファイルが見つからない場合**は、エラーログが記録され、\
  下記のデフォルトテンプレートが利用されます。
- **default_から始まるテンプレートは削除・ファイル名の変更をしないでください。**
```
 【放送開始または動画投稿告知】
以下の放送が開始されたか動画が投稿されました。
※放送プラットフォームが特定できなかったため、
最小限の内容で投稿しております。
タイトル: {{ title }}
配信者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
カテゴリ: {{ category_name }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}
  ```
  ```
  【放送終了】
以下の放送は終了しました。
※放送プラットフォームが特定できなかったため、
最小限の内容で投稿しております。
配信者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
チャンネルURL: {{ channel_url }}
  ```
- テンプレートを編集しない場合は以下の内容が投稿されます。
## Twitchの場合
  ```
Twitch 放送開始 🎉

配信者: {{ broadcaster_user_name }} ({{ broadcaster_user_login }})
タイトル: {{ title }}
カテゴリ: {{ category_name }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

ぜひ遊びに来てください！
#Twitch配信通知📺
  ```
  ```
🛑 Twitch 配信終了

{{ broadcaster_user_name | default('配信者名不明') }} さんのTwitch配信が終わりました。
チャンネル: {{ channel_url | default('チャンネルURL不明') }}

またの配信をお楽しみに！
#Twitch #配信終了 
  ```
## YouTubeLiveの場合 
  ```
▶️ YouTube Live 配信開始 🚀

チャンネル: {{ broadcaster_user_name }}
タイトル: {{ title }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

みなさんの視聴をお待ちしています！
  ```
## ニコニコ生放送の場合 
  ```
📡 ニコニコ生放送 開始 🎉

放送者: {{ broadcaster_user_name }}
タイトル: {{ title }}
開始日時: {{ start_time | datetimeformat }}
視聴URL: {{ stream_url }}

コメントお待ちしています！
  ```
## YouTube動画の場合
  ```
🎬 YouTube に新着動画投稿！

タイトル: {{ title }}
動画ID: {{ video_id }}
視聴URL: {{ video_url }}

チェックお願いします！👍
  ```
## ニコニコ動画の場合
  ```
📽 ニコニコ動画 新着投稿！

タイトル: {{ title }}
動画URL: {{ video_url }}

ぜひご覧ください！
  ```
---

## よくある質問（FAQ）

### パス・トンネル・Webhook/URL自動反映に関するFAQ
<details>

### Q. テンプレートや画像ファイルのパスはどのように指定すればよいですか？

A. templates/ や images/ フォルダ内のファイルは、**相対パス（例: templates/xxx.txt, images/xxx.png）で指定してください。**
- GUIでファイル選択した場合も自動で相対パスに変換されます。
- プロジェクト外や絶対パスの場合はそのまま絶対パスで保存されます。

### Q. トンネル（Cloudflare/ngrok/localtunnel/custom）はどのように管理されていますか？

A. main.pyがトンネルの起動・停止・URL取得を自動で管理します。\
トンネル起動後、Webhook URLは自動で取得され、GUIのURL欄に即時反映されます。

### Q. Webhook/URLタブの編集や自動反映はどのような仕様ですか？

A. Webhook設定とURL設定はGUIでタブ分離され、URLはトンネル起動時に自動取得・自動反映されます。\
自動反映時は編集不可ですが、手動切替で編集可能です。\
設定保存時は「保存完了」メッセージが必ず表示され、GUIに即時反映されます。

</details>

### ドメイン・トンネル関連
<details>

### Q. ドメインをもっていなくても利用できますか？

A. **アプリ自体は起動するのか**という意味であれば、利用は可能です。
- 現時点では、ドメインを持っていない場合はCloudflare Tunnel**または他のトンネル**を使用できませんので、\
本アプリケーションの全機能の動作について保証およびサポートの対象外とさせていただいています。
- 今後の機能追加で、ドメインを持っていない場合やCloudflare DNSが使えない場合にも、\
本アプリケーションの全機能が利用可能となる「エンドポイント貸出機能」の提供を予定しています。

### Q. Cloudflare以外でDNS管理をしていない場合でもこのアプリを利用できますか？

A. アプリ自体は**他のサービスを使う事によって使用できます。**
- ただし、公式でのサポート対象は、\
Cloudflare DNSにより管理されたドメインを用いてCloudflare Tunnel**または他のトンネル**を使うこととなっています。\
そのため、Cloudflare DNSが使えない場合は公式サポートの対象外とさせていただいています。

- Cloudflare Tunnel**または他のトンネル**は、\
独自ドメインの所有やCloudflareによるDNS管理が前提となるため、\
**ドメインを持っていない場合**や**CloudflareでDNSを管理していない場合**には利用できません。

- ドメインをCloudflareのDNSで管理していない場合は、\
Cloudflare DNSが使えない場合は、**ngrokなど代替トンネルを使うことも可能**ですが、\
公式サポート対象の対象外とさせていただいています。
</details>

### エラー関連
<details>

### Q. cloudflared がインストールされていませんと出ます

A. 事前に[公式ページ](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)から cloudflared をダウンロードし、\
settings.env の TUNNEL_CMD でパスを正しく指定してください。\
※運用環境によってはPathをダブルクォーテーションで囲って記載する必要がある場合があります。
- (例：)wingetコマンドでインストールした場合の記載例。※[ ]内がコマンドです。
  ```
  TUNNEL_CMD=["C:\Program Files (x86)\cloudflared\cloudflared.exe tunnel --config C:\Users\[パソコンのユーザーID]\.cloudflared\config.yml run <トンネル名>]"
  ```
※例えば上の記載例のように、**ファイルパス内に空白がある場合**は、\
**ダブルクォーテーションで囲って記載する**必要がありますので注意してください。

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
- コンソールやログファイルの出力に **Webhookエンドポイントは正常に稼働しています**というinfoログがある。

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
**settings.env**または**設定GUI**からテンプレートファイルを切り替えてください。

### Q. 配信終了時にも Bluesky に投稿したい

A. 現時点では配信終了投稿機能はTwitchのみに対応していますが、\
YouTube/ニコニコの配信終了通知についても今後のアップデートで対応すべく\
現在実装方法の検討を行っております。

### Q. Blueskyに投稿する時に画像を添付したい

A. imagesフォルダに画像を置いて、\
**settings.env**または**設定GUI**からファイルを設定してください。
- Blueskyに投稿できる画像形式はJPEG（.jpg/.jpeg）、PNG（.png）、静止画GIFです。\
アニメーションGIF投稿できません。
- Blueskyへの動画投稿には対応していません。
- 画像サイズは1MB以下を推奨します
- 初期設定ではimages/noimage.pngが設定されています。\
また、現状では画像は１枚だけ添付できます。

- **ファイル名の指定**が間違っている場合、デフォルト画像が使用されます。

- **正しいファイル名の指定形式**は以下のとおりです。
  ```
  BLUESKY_IMAGE_PATH=images/noimage.png
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

## 運用上の注意

- この Bot は個人運用・検証を想定しています。\
商用利用や大規模運用時は自己責任でお願いします。
- セキュリティのため、**APIキーやパスワード**は**絶対に公開リポジトリに含めない**でください。
- 依存パッケージの脆弱性は `pip-audit` や `safety` で定期的にチェックしてください。
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

## このアプリを開発・改変されたい方へ
- mainブランチは「直push禁止＆PR必須」になっています。\
そのため、mainブランチにMerge希望の場合はブランチ作成→PRでお願いします。
- 安全のためGitGuardianを導入しています。\
導入されていない方は以下の方法で導入してください。
 ```
 pip install ggshield pre-commit
 ```

## 貢献
このアプリケーションを改善し、拡張するための貢献を歓迎します！\
バグの報告、機能強化の提案、プルリクエストの提出方法の詳細については、\
[貢献ガイドライン](CONTRIBUTING.ja.md)をご覧ください。

## 自動テストの実行方法

本アプリケーションは主要な機能やバリデーションの自動テストを備えています。  
テストは [pytest](https://docs.pytest.org/) で簡単に実行できます。

### テストの実行手順

<details>

必要なパッケージをインストール（未インストールの場合）

 ```
 pip install pytest
 ```
プロジェクトルートで以下のコマンドを実行
 ```
python -m pytest
 ```
- 特定のテストファイルだけを実行したい場合は
 ```
 pytest test/test_utils.py
 ```

テスト結果が表示され、すべてのテストがパスすればOKです。

</details>

### テストの補足

- テストコードは `test/` ディレクトリにあります。
- テストの追加や修正はこのディレクトリ内の各ファイルに記述してください。
- 詳細な使い方は [pytest公式ドキュメント](https://docs.pytest.org/) を参照してください。
---
### 今後の開発予定
- ここに書かれてある内容は将来的に実装を計画している、または検討している項目であり、\
具体的な実装時期等は未定です。決まり次第作者のSNSなどでお知らせします。

- **独自ドメイン未所持ユーザー向けのトンネル利用機能**
  - 管理者所有ドメインのサブドメインを貸し出し、\
  独自ドメインがなくてもCloudflare Tunnel**または他のトンネル**経由でWebhookを受信できる仕組みを提供予定です。

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
