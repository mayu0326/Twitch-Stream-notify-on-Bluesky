# StreamNotifyonBluesky Flet新GUI ホットモック
# 実装: 空動作・画面遷移のみ
# 実行: python main.py

import flet as ft

# 多言語対応用ダミー辞書
LANGS = {
    "ja": {
        "wizard": "セットアップウィザード",
        "main": "メイン設定・管理画面",
        "next": "次へ",
        "back": "戻る",
        "save": "保存",
        "temp_save": "一時保存",
        "reset": "リセット",
        "import": "インポート",
        "export": "エクスポート",
        "server": "サーバー",
        "tunnel": "トンネル",
        "profile": "プロファイル",
        "lang": "言語",
        "jp": "日本語",
        "en": "English",
        "error": "エラー",
        "copy": "コピー",
        "show": "表示",
        "hide": "非表示",
        "log": "ログ",
        "retry": "再試行",
        "detail": "詳細ログ",
        "finish": "完了",
        "wizard_title": "StreamNotifyonBluesky セットアップウィザード",
        "main_title": "StreamNotifyonBluesky 設定・管理画面",
    },
    "en": {
        "wizard": "Setup Wizard",
        "main": "Main Settings",
        "next": "Next",
        "back": "Back",
        "save": "Save",
        "temp_save": "Temp Save",
        "reset": "Reset",
        "import": "Import",
        "export": "Export",
        "server": "Server",
        "tunnel": "Tunnel",
        "profile": "Profile",
        "lang": "Language",
        "jp": "Japanese",
        "en": "English",
        "error": "Error",
        "copy": "Copy",
        "show": "Show",
        "hide": "Hide",
        "log": "Log",
        "retry": "Retry",
        "detail": "Detail Log",
        "finish": "Finish",
        "wizard_title": "StreamNotifyonBluesky Setup Wizard",
        "main_title": "StreamNotifyonBluesky Settings",
    }
}

def main(page: ft.Page):
    # 状態管理
    if not hasattr(page.session, "lang"):
        page.session.lang = "ja"
    if not hasattr(page.session, "step"):
        page.session.step = 0
    if not hasattr(page.session, "show_main"):
        page.session.show_main = False
    max_step = 3

    def update_ui():
        L = LANGS[page.session.lang]
        def on_lang_change(e):
            page.session.lang = e.control.value
            update_ui()
        def on_back(e):
            if page.session.step > 0:
                page.session.step -= 1
                update_ui()
        def on_next(e):
            if page.session.step < max_step-1:
                page.session.step += 1
                update_ui()
            else:
                page.session.show_main = True
                update_ui()
        def on_reset(e):
            page.snack_bar = ft.SnackBar(ft.Text("リセット（未実装）"))
            page.snack_bar.open = True
            page.update()
        def on_temp_save(e):
            page.snack_bar = ft.SnackBar(ft.Text("一時保存（未実装）"))
            page.snack_bar.open = True
            page.update()
        def on_dummy(e):
            page.snack_bar = ft.SnackBar(ft.Text("未実装のダミー動作です"))
            page.snack_bar.open = True
            page.update()
        # ウィザード画面
        wizard = ft.Container(
            content=ft.Column([
                ft.Text(L["wizard_title"], size=20, weight="bold"),
                ft.ProgressBar(value=(page.session.step+1)/max_step, width=300),
                ft.Text(f"Step {page.session.step+1}/{max_step}"),
                ft.Text("(ここに各ウィザードステップの入力欄を配置)", color=ft.Colors.GREY),
                ft.Row([
                    ft.ElevatedButton(L["back"], on_click=on_back, disabled=page.session.step==0),
                    ft.ElevatedButton(L["reset"], on_click=on_reset),
                    ft.ElevatedButton(L["temp_save"], on_click=on_temp_save),
                    ft.ElevatedButton(L["next"] if page.session.step<max_step-1 else L["finish"], on_click=on_next),
                ], alignment="end"),
                ft.Text("(エラーバナー/バリデーション表示ダミー)", color=ft.Colors.RED_200),
            ], spacing=16, width=500),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )
        # メイン画面
        mainview = ft.Container(
            content=ft.Column([
                ft.Text(L["main_title"], size=20, weight="bold"),
                ft.Row([
                    ft.ElevatedButton(L["save"], on_click=on_dummy),
                    ft.ElevatedButton(L["import"], on_click=on_dummy),
                    ft.ElevatedButton(L["export"], on_click=on_dummy),
                ]),
                ft.Text("(ここに設定エディタ・状態表示・ログリスト等を配置)", color=ft.Colors.GREY),
                ft.Row([
                    ft.ElevatedButton(L["server"]+": 起動/停止", on_click=on_dummy),
                    ft.ElevatedButton(L["tunnel"]+": 起動/停止", on_click=on_dummy),
                    ft.ElevatedButton(L["log"], on_click=on_dummy),
                ]),
                ft.Text("(状態自動更新・プロファイル切替・言語切替・通知ログリスト等ダミー)", color=ft.Colors.GREY),
            ], spacing=16, width=500),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )
        page.controls.clear()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text("Flet新GUIホットモック", size=24, weight="bold"),
                    ft.Dropdown(
                        value=page.session.lang,
                        options=[ft.dropdown.Option("ja", LANGS["ja"]["jp"]), ft.dropdown.Option("en", LANGS["en"]["en"])],
                        on_change=on_lang_change,
                        width=120
                    ),
                ], alignment="spaceBetween"),
                ft.Divider(),
                wizard if not page.session.show_main else mainview,
            ])
        )
        page.update()
    page.title = "StreamNotifyonBluesky Flet新GUI ホットモック"
    update_ui()

if __name__ == "__main__":
    ft.app(target=main)
