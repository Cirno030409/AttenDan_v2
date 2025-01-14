"""
Attendance system for RoboDone main program
Author@ yuta tanimura
"""

import csv
import ctypes
import datetime
import json
import os
import subprocess
import sys
import threading
import time
import uuid

import PySimpleGUI as sg
import requests

import config.values as const
import functions.database_func as db
import functions.nfc_func as nfc
import updator.updator as updator
import Use_Mail as mm
import windows.add_student_window as add_student_window
import windows.allocate_card_to_student_window as allocate_card_to_student_window
import windows.full_screen_window as full_screen_window
import windows.main_window as main_window
import windows.popped_system_log_window as popped_system_log_window
import windows.register_student_from_csv_window as register_student_from_csv_window
import windows.remove_student_window as remove_student_window
import windows.remove_student_without_card_window as remove_student_without_card_window
import windows.splash_window as splash_window
import windows.welcome_window as welcome_window

ml = mm.Mail()

windows = {}

init_error = {
    "database": "",
    "smtp": "",
    "nfc": "",
}  # "" = no error, "error message" = error


def main():
    init_system()  # 初期化
    showgui_main()  # GUIを表示

    end_process()  # 終了処理


def is_network_connected():
    """
    ネットワーク接続があるかどうかを確認する関数。

    Returns:
        bool: ネットワーク接続がある場合はTrue、ない場合はFalse
    """
    try:
        response = requests.get("http://www.google.com", timeout=5)
        # HTTPステータスコードが200（OK）ならネットワーク接続あり
        return response.status_code == 200
    except requests.ConnectionError:
        # 接続エラーが発生した場合はネットワーク接続なし
        return False


def is_admin():  # 管理者権限を持っているかどうかを確認する
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_for_update():  # アップデートがあるかどうかを確認する
    """
    アップデートがあるかどうかを確認する。存在すれば，更新を行う。

    Returns:
        bool: アップデートがある場合はTrue，ない場合はFalse
    """
    ret = updator.is_exist_update()  # アップデートがあるかどうかを確認
    if ret != -1:
        if ret:  # アップデートがあるかどうかを確認
            latest_ver, release_title, release_body, _ = (
                updator.get_latest_release_info()
            )
            latest_ver_str = str(latest_ver)
            latest_ver_str = (
                "v"
                + latest_ver_str[0]
                + "."
                + latest_ver_str[1]
                + "."
                + latest_ver_str[2]
            )
            sg.Popup(
                f"新しいバージョン {latest_ver_str} が利用可能になりました。\nアップデートには，バグ修正，機能追加などの重要な要素が含まれています。\nアップデートの内容は以下の通りです。\n\n\n{release_title}\n\n{release_body}\n\n\nOKボタンをクリックすると，アップデーターが起動されます。アップデーターが起動したら，Yesボタンをクリックしてアップデートを実行してください.\n",
                title=f"{latest_ver_str} が利用可能",
                keep_on_top=True,
            )
            os.system("start ./resources/updator.exe")
            sys.exit()
    else:
        return ret


def is_shift_pressed():
    """
    シフトキーが押されているかどうかをチェックする

    Returns:
        bool: シフトキーが押されている場合はTrue、そうでない場合はFalse
    """
    return ctypes.windll.user32.GetKeyState(0x10) & 0x8000 != 0


def init_system():  # 初期化
    global init_error
    print("[Info] system initializing...")

    window = splash_window.get_window()  # スプラッシュウィンドウを取得
    window.read(timeout=0)

    update_values_from_default()  # default_values.jsonからvalues.jsonへ値をコピー

    if not is_network_connected():  # ネットワークに接続されているかを確認
        sg.popup_ok(
            "このコンピュータはインターネットに接続されていません。アテンダンを使用するには，インターネットに接続してください。",
            title="インターネット未接続",
            keep_on_top=True,
            modal=True,
        )
        sys.exit()

    ml.connect_to_smtp()  # SMTPサーバに接続

    # 変数のロード
    if os.path.exists(const.SAVES_PATH):
        with open(const.SAVES_PATH, "r", encoding="utf-8") as f:
            const.saves = json.load(f)

    check_for_update()  # アップデートがあるかどうかを確認

    if const.saves["system_unused"] == True or is_shift_pressed():  # 初回起動時の処理
        window.close()
        window = welcome_window.get_window()
        while True:
            event, values = window.read()
            if event == "-next_to_driver-":
                window.close()
                layout = welcome_window.get_driver_install_window()
                window = sg.Window(
                    "ICカードリーダドライバのインストール", layout, size=(800, 500)
                )
            elif event == "-next_to_driver2-":
                window.close()
                layout = welcome_window.get_driver_install_window2()
                window = sg.Window(
                    "ICカードリーダドライバのインストール", layout, size=(1200, 700)
                )
            elif event == "-next_to_1-":
                window.close()
                layout = welcome_window.get_layout1()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-next_to_2-":
                window.close()
                layout = welcome_window.get_layout2()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-next_to_3-":
                window.close()
                layout = welcome_window.get_layout3()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-next_to_4-":
                if values["-gmail-"] == "" or values["-password-"] == "":
                    sg.popup_ok(
                        "Gmailアドレスとパスワードを両方入力してください。",
                        title="エラー",
                        keep_on_top=True,
                        modal=True,
                    )
                    continue
                elif (
                    values["-gmail-"].find("@") == -1
                    or values["-gmail-"].find(".") == -1
                ):
                    sg.popup_ok(
                        "通知用メールアドレスを正しく入力してください",
                        title="エラー",
                        keep_on_top=True,
                        modal=True,
                    )
                    continue
                else:
                    const.saves["mail"]["from"] = values["-gmail-"]
                    const.saves["mail"]["password"] = values["-password-"]
                window.close()

                layout = welcome_window.get_layout4()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-next_to_finish-":
                if values["-emergency_mail-"] == "":
                    sg.popup_ok(
                        "通知用メールアドレスを入力してください",
                        title="エラー",
                        keep_on_top=True,
                        modal=True,
                    )
                    continue
                elif (
                    values["-emergency_mail-"].find("@") == -1
                    or values["-emergency_mail-"].find(".") == -1
                ):
                    sg.popup_ok(
                        "通知用メールアドレスを正しく入力してください",
                        title="エラー",
                        keep_on_top=True,
                        modal=True,
                    )
                    continue
                else:
                    const.saves["mail"]["notify_address"] = values["-emergency_mail-"]
                window.close()
                layout = welcome_window.get_layout_finish()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-close-":
                const.saves["system_unused"] = False
                window.close()
                break

            elif event == "-back_to_1-":
                window.close()
                layout = welcome_window.get_layout1()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-back_to_2-":
                window.close()
                layout = welcome_window.get_layout2()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-back_to_3-":
                window.close()
                layout = welcome_window.get_layout3()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-back_to_4-":
                window.close()
                layout = welcome_window.get_layout4()
                window = sg.Window("アテンダンへようこそ", layout, size=(1000, 750))
            elif event == "-LINK-":
                import webbrowser

                webbrowser.open(
                    "https://support.google.com/accounts/answer/185833?hl=ja"
                )

            elif event == sg.WINDOW_CLOSED:
                window.close()
                sys.exit()

        window.close()

    if db.connect_to_database() == -1:  # データベースに接続する
        print("[Error] Couldn't connect to database.")
        init_error["database"] = "error"
        sg.popup_ok(
            "データベースに接続できませんでした。データベースファイルが存在することを確認してください。また，システム管理者に問い合わせてください。",
            title="システム初期化エラー",
            keep_on_top=True,
            modal=True,
        )

    if (
        ml.login_smtp(const.saves["mail"]["from"], const.saves["mail"]["password"])
        == -1
    ):  # SMTPサーバーにログイン
        print("[Error] Couldn't login to SMTP server.")
        init_error["smtp"] = "error"
        sg.popup_ok(
            ""
            "SMTPサーバーにログインできませんでした。ネットワーク接続または，ログインするアカウント設定が正しく設定されているか，確認してください。",
            title="システム初期化エラー",
            keep_on_top=True,
            modal=True,
        )

    ret = nfc.connect_reader()  # NFCリーダーに接続する

    if (not const.ignore_nfc_error) and (ret != 0):  # エラーハンドル
        const.states["nfc"] = const.DISCONNECTED
        const.states["system"] = const.DISABLED
        init_error["nfc"] = ret
        print("[Error] Couldn't connect to NFC reader.")
        sg.popup_ok(
            "NFCカードリーダに接続できませんでした。NFCカードリーダが正常に接続されていることを確認してから，システムを再起動してください。",
            title="システム初期化エラー",
            keep_on_top=True,
            modal=True,
        )
    else:
        const.states["nfc"] = const.CONNECTED
        threading.Thread(
            target=nfc.nfc_update_sub_thread, daemon=True
        ).start()  # NFCの更新を行うスレッドを起動

    db.add_systemlog_to_database("システム起動")  # システムログに記録
    print("[Info] system initialized.")
    window.close()
    return init_error


def update_values_from_default():
    """
    default_values.jsonからvalues.jsonへ値をコピーする。
    既にvalues.jsonに値が存在している場合はスキップし、存在していない場合は追加する。
    """

    def merge_dicts(source, destination):
        """
        sourceの辞書をdestinationに再帰的にマージする。
        sourceのキーがdestinationに存在しない場合は追加し、
        存在するが辞書の場合は再帰的にマージする。
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # このキーの値が辞書の場合、再帰的にマージ
                node = destination.setdefault(key, {})
                merge_dicts(value, node)
            else:
                # このキーの値が辞書でない場合、値を追加
                if key not in destination:
                    destination[key] = value
        return destination

    try:
        with open(
            "resources/default_values.json", "r", encoding="utf-8"
        ) as default_file:
            default_values = json.load(default_file)

        with open("saves/values.json", "r+", encoding="utf-8") as values_file:
            values = json.load(values_file)
            # default_valuesをvaluesにマージ
            updated_values = merge_dicts(default_values, values)

            values_file.seek(0)
            json.dump(updated_values, values_file, ensure_ascii=False, indent=4)
            values_file.truncate()

    except FileNotFoundError as e:
        print(f"[Error] ファイルが見つかりません: {e}")
    except json.JSONDecodeError as e:
        print(f"[Error] JSONファイルの解析に失敗しました: {e}")


def showgui_main():  # GUIを表示
    global init_error

    # トグルボタンの初期化
    toggles = {
        "power": True,  # 入退室処理の有効化トグル
        "fullscreen": False,  # フルスクリーンモードの有効化トグル
    }

    sg.theme("BluePurple")  # テーマをセット

    windows["main"] = main_window.get_window()  # メインwindowを取得

    # saves変数をウィジェットの変数に反映
    load_settings(windows)

    windows["poppped_system_log_window"] = (
        popped_system_log_window.get_window()
    )  # システムログポップアウトウィンドウを取得
    windows["poppped_system_log_window"].hide()

    # 起動時のメッセージ
    print(
        "========================================\n\n"
        + "Welcome to "
        + const.SYSTEM_NAME
        + " ver. "
        + const.VERSION
        + "\n copyright© 2024 yuta tanimura All rights reserved."
        + "\n\n========================================"
    )

    check_init_error(init_error)  # 起動時のエラーチェック

    #! メインループ ====================================================================================================
    while True:
        # ウィンドウ表示

        sg.theme("BluePurple")  # テーマをセット

        # 更新処理

        ## 現在時刻を取得
        const.year = datetime.datetime.now().year
        const.month = datetime.datetime.now().month
        const.day = datetime.datetime.now().day
        const.hour = datetime.datetime.now().hour
        const.minute = datetime.datetime.now().minute
        const.second = datetime.datetime.now().second

        ## 日付が変わったら，生徒の出席状況をリセット
        threading.Thread(target=reset_attendance_status).start()

        ## 別スレッドで発生した例外をキャッチ
        if len(const.exceptions) > 0:
            for i, e in enumerate(const.exceptions):
                print(e)
                const.exceptions.pop(i)
                const.wav["error_normal"].play()  # エラー音を再生

        ## NFCのカードのタッチを確認
        if (
            const.states["nfc"] == const.CONNECTED  # NFCカードリーダが接続されている
            and const.states["system"] == const.ENABLED  # システムが有効化されている
        ):
            if (
                id := nfc.check_nfc_was_touched()
            ) != -1:  # NFCカードがタッチされたかどうかを確認
                print("[Info] 入退室プロセスを実行しています...")
                if run_attendance_process(id, windows) == -1:  # 入退室処理
                    print("[Error] 入退室処理に失敗しました")
                    const.wav["error"].play()  # エラー音を再生
                else:
                    if const.saves["sys_setting"]["touch_sound"]:
                        const.wav["touched"].play()  # タッチ音を再生
        else:
            const.nfc_data["touched_flag"] = (
                False  # システムが無効化中は，常にフラグをFalseにしておく
            )

        ##! システムの状態をトグルボタンに反映
        if const.states["system"] == const.ENABLED:
            toggles["power"] = True
        elif const.states["system"] == const.DISABLED:
            toggles["power"] = False

        for i, win in enumerate(
            list(windows.values())
        ):  # すべてのウィンドウに対して更新
            event, values = win.read(timeout=0)

            ## メインウィンドウ以外のウィンドウの終了処理
            if win != windows["main"]:
                if event == sg.WIN_CLOSED or event is None:
                    if (
                        "full_screen_window" in windows
                        and win == windows["full_screen_window"]
                    ):
                        toggles["fullscreen"] = False
                        windows.pop("full_screen_window")
                    else:
                        win.close()  # ウィンドウを閉じる
                        windows.pop(list(windows.keys())[i])  # ウィンドウを削除
                        continue

                if (
                    "full_screen_window" in windows
                    and win == windows["full_screen_window"]
                ):
                    if win["-greeting-"].get() != "こんにちは！":
                        if "greeting" not in const.timers:
                            const.timers["greeting"] = int(time.time())
                        else:
                            if int(time.time()) - const.timers["greeting"] > 20:
                                win["-greeting-"].update("こんにちは！")
                                const.timers.pop("greeting")

            ##! メインウィンドウ
            if win == windows["main"]:
                ### クローズボタンの処理
                if event == sg.WIN_CLOSED or event is None:
                    end_process()  # 終了処理
                    sys.exit()

                ### 現在時刻表示の更新
                win["-time-"].update(
                    "%02d:%02d:%02d" % (const.hour, const.minute, const.second)
                )

                ###! トグル状態に応じてボタンを変更
                if toggles["power"]:  # 入退室処理の有効化トグル
                    win["-power-"].update(
                        text="入退室処理 有効", button_color="white on green"
                    )
                else:
                    win["-power-"].update(
                        text="入退室処理 無効", button_color="white on red"
                    )

                if toggles["fullscreen"]:  # フルスクリーンモードの有効化トグル
                    win["-toggle_fullscreen-"].update(
                        text="待ち受け画面を非表示", button_color="black on pink"
                    )
                else:
                    win["-toggle_fullscreen-"].update(
                        text="待ち受け画面を表示", button_color="white on black"
                    )

                ### 生徒にカードを割り当てるボタンの色を変更する
                if how_many_unassigned_cards() > 0:
                    win["-assign_card_to_unassigned_student-"].update(
                        button_color="white on red"
                    )

                ### NFCの状態表示を更新
                if const.states["nfc"] == const.DISCONNECTED:
                    win["-nfcstate-"].update(
                        "NFCカードリーダが接続されていません",
                        background_color="yellow",
                        text_color="black",
                    )
                elif (
                    const.states["nfc"] == const.CONNECTED
                    and const.states["system"] == const.ENABLED
                ):
                    win["-nfcstate-"].update(
                        "現在カードをタッチすると，生徒の入退室処理が実行されます",
                        background_color="green",
                        text_color="white",
                    )
                elif (
                    const.states["nfc"] == const.CONNECTED
                    and const.states["system"] == const.DISABLED
                ):
                    win["-nfcstate-"].update(
                        "現在カードをタッチしても，入退室処理を行いません",
                        background_color="red",
                        text_color="white",
                    )

                ###! システム状態切り替えトグルボタン
                if event == "-power-":
                    toggles = toggle_power(
                        toggles
                    )  # システムの有効化・無効化を切り替える
                ###! 主な操作パネルのボタン
                ### 待ち受け画面の表示・非表示
                elif event == "-toggle_fullscreen-":
                    if not toggles["fullscreen"]:
                        if const.states["system"] == const.DISABLED:
                            sg.popup_ok(
                                "待ち受け画面を表示するには，入退室処理を有効化してください。",
                                title="エラー",
                                keep_on_top=True,
                                modal=True,
                            )
                            continue
                        else:
                            if "full_screen_window" in windows:
                                windows["full_screen_window"].un_hide()
                            else:
                                windows["full_screen_window"] = (
                                    full_screen_window.get_window()
                                )
                    else:
                        windows["full_screen_window"].hide()
                        windows.pop("full_screen_window")
                    toggles["fullscreen"] = not toggles[
                        "fullscreen"
                    ]  # トグルの状態を反転

                ### データベース管理パネルのボタン
                elif event == "-show_all_students-" or event == "生徒の一覧の表示":
                    print("---- 生徒一覧 ----")
                    print_formatted_list(
                        db.execute_database(
                            "SELECT * FROM student join parent on student.id = parent.id"
                        )
                    )
                elif event == "-show_all_system_logs-" or event == "システムログの表示":
                    print("---- システムログ ----")
                    print_formatted_list(
                        db.execute_database("SELECT * FROM system_log")
                    )
                elif event == "-show_all_logs-" or event == "入退室ログの表示":
                    print("---- 入退室ログ ----")
                    print_formatted_list(db.execute_database("SELECT * FROM log"))
                elif event == "-add_student-" or event == "生徒の新規登録":
                    if const.states["system"] == const.DISABLED:
                        if not is_ok_to_open_window(windows):
                            continue
                        windows["add_student"] = add_student_window.get_window()
                    else:
                        sg.popup_ok(
                            "生徒を登録するには，入退室処理を無効化してください。有効化中にこの操作は行えません。",
                            title="エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                elif event == "-remove_student-" or event == "生徒の除名":
                    if const.states["system"] == const.DISABLED:
                        if not is_ok_to_open_window(windows):
                            continue
                        windows["remove_student"] = remove_student_window.get_window()
                    else:
                        sg.popup_ok(
                            "生徒を除名するには，入退室処理を無効化してください。有効化中にこの操作は行えません。",
                            title="エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                elif event == "-assign_card_to_unassigned_student-":
                    if const.states["system"] == const.DISABLED:
                        windows["assign_card_to_student"] = (
                            allocate_card_to_student_window.get_window()
                        )
                    else:
                        sg.popup_ok(
                            "生徒にカードを割り当てるには，入退室処理を無効化してください。有効化中にこの操作は行えません。",
                            title="エラー",
                            keep_on_top=True,
                            modal=True,
                        )

                ### SQLの操作パネルのボタン
                elif event == "-execute-":
                    if values["-sql-"] == "":
                        print("[Error] SQL command is empty.")
                    else:
                        print("[Info] Executing SQL: " + values["-sql-"])
                        ret = db.execute_database(values["-sql-"])
                        if ret != -1:
                            print_formatted_list(ret)
                        print("[Info] SQL execution completed.")
                elif event == "-commit-":
                    db.commit_database()
                elif event == "-rollback-":
                    db.rollback_database()

                ### システムログポップアウトボタン
                elif event == "-pop_log_win-":
                    if "poppped_system_log_window" in windows:
                        windows["poppped_system_log_window"].un_hide()
                        continue
                    else:
                        windows["poppped_system_log_window"] = (
                            popped_system_log_window.get_window()
                        )

                ### メールの設定タブ
                elif event == "-send_test_mail-":
                    if const.saves["mail"]["test_address"] == "":
                        sg.popup_ok(
                            "テストメールを送信するには，テストメールアドレスを設定してください。",
                            title="エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    if (
                        sg.popup_yes_no(
                            "下記メールアドレスにテストメールを送信します。よろしいですか？なお，生徒の名前は「山田太郎」に置き換えて送信します。\n\n"
                            + const.saves["mail"]["test_address"],
                            title="テストメールの送信",
                            keep_on_top=True,
                            modal=True,
                        )
                        == "Yes"
                    ):
                        if (
                            send_mail(
                                "山田太郎",
                                const.saves["mail"]["test_address"],
                                mode="test",
                            )
                            == -1
                        ):
                            sg.popup_ok(
                                "テストメールの送信に失敗しました。",
                                title="エラー",
                                keep_on_top=True,
                                modal=True,
                            )
                        else:
                            sg.popup_ok(
                                "テストメールを送信しました。",
                                title="完了",
                                keep_on_top=True,
                                modal=True,
                            )
                ###! メニューバー
                ### バージョン情報
                elif event == "バージョン情報":
                    sg.popup_ok(
                        const.SYSTEM_NAME
                        + " v"
                        + const.VERSION
                        + "\ncopyright© 2024 yuta tanimura All rights reserved."
                        + "\n\n"
                        + const.RELEASE_NOTES
                        + "\n\n何か問題があれば，下記連絡先までご連絡ください。\n\n"
                        + "開発者: 谷村悠太\ntaniymail@icloud.com",
                        title="バージョン情報",
                        keep_on_top=True,
                        modal=True,
                    )

                elif event == "生徒の情報をCSV形式で出力":
                    output_students_list_as_csv()

                elif event == "生徒とその保護者の情報をCSV形式で出力":
                    output_students_and_parents_list_as_csv()

                elif event == "入退室ログをCSV形式で出力":
                    output_attendance_log_as_csv()

                elif event == "システムログをCSV形式で出力":
                    output_system_log_as_csv()

                elif event == "アップデートの確認":
                    if not check_for_update():
                        sg.popup_ok(
                            const.SYSTEM_NAME + "は，最新版です。",
                            title="アップデートの確認",
                            keep_on_top=True,
                            modal=True,
                        )

                elif event == "入退出処理の有効化/無効化を切り替え":
                    toggles = toggle_power(toggles)

                elif event == "アテンダンを終了":
                    end_process()

                elif event == "ライセンス表示":
                    with open("license.txt", "r", encoding="utf-8") as f:
                        license_text = f.read()
                    sg.popup_ok(
                        'このソフトウェアは，GNU Lesser General Public License v3.0に基づいて配布されています。\nライセンス文は，本ソフトウェアのディレクトリ内の"license.txt"に記載しています。\nソースコードは，https://github.com/Cirno030409/AttenDan.gitにて閲覧することができます。',
                        title="ライセンス",
                        keep_on_top=True,
                        modal=True,
                    )

                ### メールの設定を保存
                const.saves["mail"]["enter"]["subject"] = values[
                    "-entered_mail_subject-"
                ]
                const.saves["mail"]["enter"]["body"] = values["-entered_mail_body-"]
                const.saves["mail"]["exit"]["subject"] = values["-exited_mail_subject-"]
                const.saves["mail"]["exit"]["body"] = values["-exited_mail_body-"]
                const.saves["mail"]["test_address"] = values["-test_mail_address-"]

            ##! ウィンドウ処理
            ## 生徒登録ウィンドウ
            elif "add_student" in windows and win == windows["add_student"]:
                if event == "-register-":
                    if (
                        values["-st_name-"] == ""
                        or values["-st_age-"] == ""
                        or values["-st_gender-"] == "未選択"
                        or values["-st_parentsname-"] == ""
                        or values["-st_mail_address-"] == ""
                    ):
                        sg.PopupOK(
                            "登録するには，生徒の情報をすべて入力する必要があります。",
                            title="生徒登録エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    try:
                        age = int(values["-st_age-"])
                    except ValueError:
                        sg.PopupOK(
                            "年齢は数値で入力してください。",
                            title="入力エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    if (
                        register_student(
                            values["-st_name-"],
                            values["-st_age-"],
                            values["-st_gender-"],
                            values["-st_parentsname-"],
                            values["-st_mail_address-"],
                        )
                        == 0
                    ):
                        db.commit_database()
                        sg.PopupOK(
                            "生徒を登録しました。",
                            title="完了",
                            keep_on_top=True,
                            modal=True,
                        )
                elif event == "-register_from_csv-":
                    windows["add_student"].close()
                    windows.pop("add_student")
                    windows["register_student_from_csv"] = (
                        register_student_from_csv_window.get_window()
                    )

                elif event == "-register_without_card-":
                    if (
                        values["-st_name-"] == ""
                        or values["-st_age-"] == ""
                        or values["-st_gender-"] == "未選択"
                        or values["-st_parentsname-"] == ""
                        or values["-st_mail_address-"] == ""
                    ):
                        sg.PopupOK(
                            "登録するには，生徒の情報をすべて入力する必要があります。",
                            title="生徒登録エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    try:
                        age = int(values["-st_age-"])
                    except ValueError:
                        sg.PopupOK(
                            "年齢は数値で入力してください。",
                            title="入力エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    if (
                        sg.popup_yes_no(
                            "カードを使用せずに，生徒を登録しますか？\nカードを使用せずに登録した生徒は，後からカードの割り当てを行う必要があります。",
                            title="生徒登録",
                            keep_on_top=True,
                            modal=True,
                        )
                        == "Yes"
                    ):
                        register_student(
                            values["-st_name-"],
                            values["-st_age-"],
                            values["-st_gender-"],
                            values["-st_parentsname-"],
                            values["-st_mail_address-"],
                            without_card=True,
                        )
                        db.commit_database()
                        sg.popup_ok(
                            "生徒を登録しました。",
                            title="完了",
                            keep_on_top=True,
                            modal=True,
                        )
                    else:
                        continue

            ## CSVから生徒を登録ウィンドウ
            elif (
                "register_student_from_csv" in windows
                and win == windows["register_student_from_csv"]
            ):
                if event == "-load_csv-":
                    path = sg.popup_get_file(
                        "CSVファイルを選択してください",
                        file_types=(("CSVファイル", "*.csv"),),
                    )
                    if path is None or path == "":
                        continue
                    else:
                        csv_error = False
                        with open(path, "r", encoding="utf-8") as f:
                            reader = csv.reader(f)
                            students = list(reader)
                            if (
                                students[0][0] == "生徒の氏名"
                            ):  # ヘッダーがある場合は削除
                                students.pop(0)  # ヘッダーを削除
                            for student in students:
                                if student[2] not in ["男", "女"]:
                                    print(
                                        "CSV loading error: 性別が不正です。性別は「男」または「女」のいずれかである必要があります。"
                                    )
                                    csv_error = True
                                    break
                                for student in students:
                                    if len(student) != 5:
                                        print(
                                            "CSV loading error: フィールド数が不正です。"
                                        )
                                        csv_error = True
                                        break
                                try:
                                    for student in students:
                                        int(student[1])
                                except ValueError as e:
                                    print(
                                        "CSV loading error: 年齢が不正です。年齢は数字である必要があります。"
                                    )
                                    csv_error = True
                                    break
                                if csv_error:
                                    break

                            if len(students) == 0:
                                sg.popup_ok(
                                    "このCSVファイルには生徒の情報がありません。CSVファイルを確認してください。",
                                    title="エラー",
                                    keep_on_top=True,
                                    modal=True,
                                )
                                continue

                            if csv_error:  # CSVファイルのデータ形式が正しくない場合
                                sg.popup_ok(
                                    "CSVファイルのデータ形式が正しくありません。CSVファイルは以下のような形式である必要があります。\n\n\n生徒の氏名1,年齢(数字),性別(男 or 女),保護者名,保護者のメールアドレス\n生徒の氏名2,年齢(数字),性別(男 or 女),保護者名,保護者のメールアドレス\n.\n.\n.\n\n\nなお，性別は「男」または「女」のいずれかである必要があります。また，年齢は数字である必要があります。CSVファイルを確認してください。エラーの詳細は，システム出力を確認してください。",
                                    title="エラー",
                                    keep_on_top=True,
                                    modal=True,
                                )
                                continue
                            win["-csv_file_path-"].update("CSVファイル:" + path)
                            win["-do_register_from_csv-"].update(disabled=False)
                elif event == "-do_register_from_csv-":
                    if (
                        sg.popup_yes_no(
                            "CSVファイルから%d人の生徒を登録します。一人目の生徒データを例として以下に表示します。\n\n\n生徒の氏名: %s\n年齢: %d\n性別: %s\n保護者名: %s\n保護者のメールアドレス: %s\n\n\n上記の内容が正しいか確認してください。フィールド名と内容が一致しない(例:生徒の氏名に年齢が表示されている)場合，読み込むCSVファイルの内容を修正してからもう一度読み込んでください。\n\n登録してもよろしいですか？"
                            % (
                                len(students),
                                students[0][0],
                                int(students[0][1]),
                                students[0][2],
                                students[0][3],
                                students[0][4],
                            ),
                            title="登録の確認",
                            keep_on_top=True,
                            modal=True,
                        )
                        == "Yes"
                    ):
                        reg_error = False  # 登録エラーが発生したかどうか
                        print("[Info] CSVファイルから生徒を登録しています...")
                        for student in students:
                            print("[Info] 登録中: %s" % student[0])
                            if (
                                register_student(
                                    student[0],
                                    int(student[1]),
                                    student[2],
                                    student[3],
                                    student[4],
                                    without_card=True,
                                )
                                != 0
                            ):  # 生徒を登録
                                sg.popup_ok(
                                    "生徒の登録に失敗しました。このCSVファイルの生徒の登録は中止されました。",
                                    title="エラー",
                                    keep_on_top=True,
                                    modal=True,
                                )
                                reg_error = True
                                break
                        if not reg_error:
                            db.commit_database()
                            print("[Info] CSVファイルからの生徒登録を完了しました。")
                            sg.popup_ok(
                                "%d名の生徒の登録を完了しました。\n現在登録された生徒には，ICカードがまだ割り当てられていません。これらの生徒にICカードを割り当てるには，メインウィンドウの「生徒を管理」セクションの「生徒にカードを割り当てる」を選択し，ICカードの割り当てを行ってください。"
                                % len(students),
                                title="完了",
                                keep_on_top=True,
                                modal=True,
                            )
                        else:
                            continue

            ## 生徒除名ウィンドウ
            elif "remove_student" in windows and win == windows["remove_student"]:
                if event == "-remove-":
                    if values["-st_name-"] == "":
                        sg.PopupOK(
                            "除名する生徒の名前を入力してください。",
                            title="生徒除名エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue

                    remove_student(values["-st_name-"])

                elif event == "-remove_without_card-":
                    windows["remove_student"].close()
                    windows.pop("remove_student")
                    windows["remove_student_without_card"] = (
                        remove_student_without_card_window.get_window()
                    )

            ## 生徒除名（カードなし）ウィンドウ
            elif (
                "remove_student_without_card" in windows
                and win == windows["remove_student_without_card"]
            ):
                if event == "-remove-":
                    if (
                        values["-st_name-"] == ""
                        or values["-st_age-"] == ""
                        or values["-st_gender-"] == "未選択"
                        or values["-st_parentsname-"] == ""
                        or values["-st_mail_address-"] == ""
                    ):
                        sg.PopupOK(
                            "除名する生徒の情報をすべて入力してください。",
                            title="生徒除名エラー",
                            keep_on_top=True,
                            modal=True,
                        )
                        continue
                    now_processing_window = (
                        now_processing_popup()
                    )  # 処理中のポップアップを表示
                    now_processing_window.read(timeout=0)
                    remove_student_without_card(
                        values["-st_name-"],
                        values["-st_age-"],
                        values["-st_gender-"],
                        values["-st_parentsname-"],
                        values["-st_mail_address-"],
                    )
                    now_processing_window.close()

            ## ICカード割り当てウィンドウ
            elif (
                "assign_card_to_student" in windows
                and win == windows["assign_card_to_student"]
            ):
                if len(values["-st_list-"]) == 0:
                    win["-allocate_cards_to_students-"].update(disabled=True)
                else:
                    win["-allocate_cards_to_students-"].update(disabled=False)

                if event == "-allocate_cards_to_students-":
                    student = db.execute_database(
                        f"SELECT * FROM student WHERE name='{values['-st_list-'][0]}'"
                    )
                    id = student[0][0]
                    name = student[0][1]
                    gender = student[0][2]
                    age = student[0][3]
                    if (
                        sg.popup_yes_no(
                            f"以下の生徒にカードを割り当てます。よろしいですか？\n\n生徒の氏名: {name}\n性別: {gender}\n年齢: {age}\n",
                            title="カード割り当ての確認",
                            keep_on_top=True,
                            modal=True,
                        )
                        == "Yes"
                    ):
                        if assign_card_to_student(id) != -1:
                            db.commit_database()
                            win.close()

            ## ポップアウトされたシステム出力ウィンドウ
            elif (
                "poppped_system_log_window" in windows
                and win == windows["poppped_system_log_window"]
            ):
                if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                    win.hide()

                elif event == "-close-":
                    win.hide()


def check_init_error(init_error):
    if (num := how_many_unassigned_cards()) != 0:
        print(
            "[Warning] カード未割り当ての生徒が "
            + str(num)
            + " 名います。「生徒にカードを割り当てる」ボタンより，カードの割り当てを行ってください。"
        )

    if init_error["database"] != "":
        print(
            "[Warning] データベースに接続できませんでした。データベースファイルが存在することを確認してください。また，システム管理者に問い合わせてください。: ",
            init_error["database"],
        )

    if init_error["smtp"] != "":
        print(
            "[Warning] SMTPサーバーにログインできませんでした。ネットワーク接続または，ログインするアカウント設定を確認してください。また，システム管理者に問い合わせてください。: ",
            init_error["smtp"],
        )

    if init_error["nfc"] != "":
        print(
            "[Warning] NFCカードリーダに接続できませんでした。NFCカードリーダが正常に接続されていることを確認してから，システムを再起動してください。: ",
            init_error["nfc"],
        )

    if const.states["nfc"] == const.DISCONNECTED:
        print(
            "[Info] NFCカードリーダが接続されていません。入退室処理を有効化するには，NFCカードリーダが正常に接続されていることを確認し，システムを再起動してください。: ",
            init_error["nfc"],
        )


def load_settings(windows):
    """
    設定をGUI上のウィジェットに反映させます。

    Args:
        windows (dict): ウィンドウを保持する辞書
    """

    try:
        # メール        設定
        windows["main"]["-entered_mail_subject-"].update(
            const.saves["mail"]["enter"]["subject"]
        )
        windows["main"]["-entered_mail_body-"].update(
            const.saves["mail"]["enter"]["body"]
        )
        windows["main"]["-exited_mail_subject-"].update(
            const.saves["mail"]["exit"]["subject"]
        )
        windows["main"]["-exited_mail_body-"].update(
            const.saves["mail"]["exit"]["body"]
        )
        windows["main"]["-test_mail_address-"].update(
            const.saves["mail"]["test_address"]
        )

        # システム設定
        windows["main"]["-sysset_from-"].update(const.saves["mail"]["from"])
        windows["main"]["-sysset_password-"].update(const.saves["mail"]["password"])
        windows["main"]["-sysset_notify_address-"].update(
            const.saves["mail"]["notify_address"]
        )
        windows["main"]["-sysset_touch_sound-"].update(
            const.saves["sys_setting"]["touch_sound"]
        )
        windows["main"]["-sysset_greeting_sound-"].update(
            const.saves["sys_setting"]["greeting_sound"]
        )

    except (
        Exception
    ) as e:  # アップデート等でロードする設定項目が追加されたときにおこる可能性あり
        print(
            "[Error] 設定のロード中にエラーが発生しました。設定ファイルを確認してください。"
        )
        return -1


def reset_fullscreen_window_mes(window):
    window["-greeting-"].update("こんにちは！")


def reset_attendance_status():
    """
    日付が変わったら，すべての生徒の出席状態を '退席' に変更します。
    """
    current_day = datetime.datetime.now().day
    while True:
        time.sleep(60)  # 60秒ごとに日付をチェック
        new_day = datetime.datetime.now().day
        if new_day != current_day:
            print("日付が変わりました。")
            db.execute_database("UPDATE student SET attendance = '退席'")
            db.commit_database()
            print(
                "[Info] 日付が変わったので，全生徒の出席状態を '退席' に変更しました。"
            )
            current_day = new_day


def toggle_power(toggles):
    """
    システムの有効化/無効化を切り替えます。

    Args:
        toggles (dict): トグル状態を保持する変数

    Returns:
        toggles (dict): トグル状態を保持する変数
    """
    toggles["power"] = not toggles["power"]  # トグルの状態を反転
    if toggles["power"]:
        if const.states["nfc"] == const.DISCONNECTED:
            sg.popup_ok(
                "入退室処理を有効化できません。有効化するには，NFCカードリーダが正常に接続されていることを確認し，システムを再起動してください。",
                title="システムエラー",
                keep_on_top=True,
                modal=True,
            )
            toggles["power"] = not toggles["power"]  # トグルの状態を元に戻す
            return toggles
        if (
            sg.popup_yes_no(
                "入退室処理を有効化すると，カードがタッチされると生徒の入退室処理が実行され，保護者へのメール送信等の操作が実行される状態になります。カードリーダの近くにカードがないことを確認してください。有効化してもよろしいですか？",
                title="システム有効化の確認",
                keep_on_top=True,
                modal=True,
            )
            == "Yes"
        ):
            const.states["system"] = const.ENABLED  # 入退室処理を有効化
            print("[Info] 入退室処理が有効化されました")
            if const.states["nfc"] == const.CONNECTED:
                print(
                    "[Attention] 現在の状態でNFCカードリーダにカードをタッチすると，生徒の入退室処理が実行されます。これは，タッチされたカードの生徒の保護者へのメール送信などが行われることを意味します。不用意にカード操作を行わないようにしてください。"
                )
    else:
        const.states["system"] = const.DISABLED  # システムを無効化
        toggles["fullscreen"] = False  # フルスクリーンモードを無効化
        if "full_screen_window" in windows:
            windows["full_screen_window"].hide()
            windows.pop("full_screen_window")
        print("[Info] 入退室処理が無効化されました")
        if const.states["nfc"] == const.CONNECTED:
            print(
                "[Info] 現在の状態でNFCカードリーダにカードをタッチしても，入退室処理を行いません。カードをタッチしても安全です。"
            )
    return toggles


def output_students_list_as_csv():
    """
    生徒の情報をCSVファイルとして出力します。

    Returns:
        ret (bool): 保存が成功したかどうか
    """
    st_list = db.execute_database("SELECT * FROM student")
    data = ""
    for student in st_list:
        for n, i in enumerate(student):
            if n == 0:
                data = data + str(i)
            else:
                data = data + "," + str(i)
        data = data + "\n"

    if save_as_csv(data):
        return True
    else:
        return False


def output_students_and_parents_list_as_csv():
    """
    生徒と保護者の情報をCSVファイルとして出力します。

    Returns:
        ret (bool): 保存が成功したかどうか
    """
    st_list = db.execute_database(
        "SELECT * FROM student join parent on student.id = parent.id"
    )
    data = ""
    for student in st_list:
        for n, i in enumerate(student):
            if n == 0:
                data = data + str(i)
            else:
                data = data + "," + str(i)
        data = data + "\n"

    if save_as_csv(data):
        return True
    else:
        return False


def output_attendance_log_as_csv():
    """
    入退室ログをCSVファイルとして出力します。

    Returns:
        ret (bool): 保存が成功したかどうか
    """
    log_list = db.execute_database("SELECT * FROM log")
    data = ""
    for log in log_list:
        for n, i in enumerate(log):
            if n == 0:
                data = data + str(i)
            else:
                data = data + "," + str(i)
        data = data + "\n"

    if save_as_csv(data):
        return True
    else:
        return False


def output_system_log_as_csv():
    """
    システムログをCSVファイルとして出力します。

    Returns:
        ret (bool): 保存が成功したかどうか
    """
    log_list = db.execute_database("SELECT * FROM system_log")
    data = ""
    for log in log_list:
        for n, i in enumerate(log):
            if n == 0:
                data = data + str(i)
            else:
                data = data + "," + str(i)
        data = data + "\n"

    if save_as_csv(data):
        return True
    else:
        return False


def save_as_csv(data: str):
    """
    データをCSVファイルとして保存します。保存場所を選択するダイアログを表示し，選択された場所に保存します。途中で保存がキャンセルされた場合は，Falseを返します。

    Args:
        data (str): csv形式のデータ

    Returns:
        ret (bool): 保存が成功したかどうか
    """
    path = sg.popup_get_file(
        "CSVファイルを保存する場所を選択してください",
        save_as=True,
        file_types=(("CSVファイル", "*.csv"),),
    )
    if path is None or path == "":
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    sg.popup_ok(
        "CSVファイルとして保存しました。",
        title="完了",
        keep_on_top=True,
        modal=True,
    )
    return True


def how_many_unassigned_cards():
    """
    未割り当てのカードが何枚あるかを返します。

    Returns:
        ret (int): 未割り当てのカードの枚数

    """
    st_list = db.execute_database("SELECT name FROM student WHERE id LIKE 'temp%'")
    st_list = [i[0] for i in st_list]

    return len(st_list)


def end_process():  # 終了処理
    with open(const.SAVES_PATH, "w") as f:
        json.dump(const.saves, f)
    # システム終了処理
    db.add_systemlog_to_database("システム終了")  # システムログに記録
    db.commit_database()  # データベースにコミットする
    db.disconnect_from_database()  # データベースを切断する

    if const.states["nfc"] == const.CONNECTED:
        nfc.disconnect_reader()  # NFCリーダーを切断する
    ml.logout_smtp()  # SMTPサーバーからログアウトする
    os._exit(0)


def is_ok_to_open_window(windows: dict):
    """
    ウィンドウを開くことができるかどうかを判定します。同時表示してはいけないウィンドウがすでに開いている場合は，popupを表示して，Falseを返します。

    Args:
        windows (dict): ウィンドウの辞書

    Returns:
        ret (bool): ウィンドウを開くことができるかどうか
    """
    win_num = len(windows)  # 開いているウィンドウの数
    if "poppped_system_log_window" in windows:
        win_num -= 1
    if win_num > 1:
        sg.popup_ok(
            "このウィンドウは複数同時に開けません。既に開いている別のウィンドウを閉じてから，この操作を行ってください。",
            title="エラー",
            keep_on_top=True,
            modal=True,
        )
        return False
    else:
        return True


def send_mail(name, address, mode="test"):
    """
    入退室メールを送信します。

    Args:
        id (str): 入退室した生徒のID
        mode (str): 送信するメールの種類。"enter"，"exit"または"test"のいずれかを指定します。"test"を指定すると，テストメールアドレスにテストメールを送信します。
    """
    if mode == "enter":
        ret = ml.send(
            address,
            const.saves["mail"]["enter"]["subject"].format(name=name),
            const.saves["mail"]["enter"]["body"].format(name=name),
        )
        if ret != 0:
            const.exceptions.append(
                "[Error] メールの送信に失敗しました.送信アカウントの設定とネットワーク環境を確認してください.: "
                + str(ret)
            )
            print("[Error] メールの送信に失敗しました.")
            return -1
    elif mode == "exit":
        ret = ml.send(
            address,
            const.saves["mail"]["exit"]["subject"].format(name=name),
            const.saves["mail"]["exit"]["body"].format(name=name),
        )
        if ret != 0:
            const.exceptions.append(
                "[Error] メールの送信に失敗しました.送信アカウントの設定とネットワーク環境を確認してください.: "
                + str(ret)
            )
            print("[Error] メールの送信に失敗しました。")
            return -1
    elif mode == "test":
        ret = ml.send(
            address,
            const.saves["mail"]["enter"]["subject"].format(name=name),
            const.saves["mail"]["enter"]["body"].format(name=name),
        )
        if ret != 0:
            const.exceptions.append(
                "[Error] メールの送信に失敗しました.送信アカウントの設定とネットワーク環境を確認してください.: "
                + str(ret)
            )
            print("[Error] メールの送信に失敗しました.")
            return -1
        ret = ml.send(
            address,
            const.saves["mail"]["exit"]["subject"].format(name=name),
            const.saves["mail"]["exit"]["body"].format(name=name),
        )
        if ret != 0:
            const.exceptions.append(
                "[Error] メールの送信に失敗しました.送信アカウントの設定とネットワーク環境を確認してください.: "
                + str(ret)
            )
            print("[Error] メールの送信に失敗しました.")
            return -1
    else:
        const.exceptions.append(
            "[Error] 内部エラーです.send_mail()のmode引数が不正です."
        )
        print("[Error] send_mail()のmode引数が不正です.")
        return -1


#! 入退室処理実行関数
def run_attendance_process(id: str, windows):
    """
    生徒の入退室処理を行います。出席状態を反転し，メールを送信します。
    この関数は，システムが無効化されている状態で呼び出されてはなりません。

    Args:
        id (str): 入退室処理を行う生徒のID

    Returns:
        ret (bool): 成功したら -1以外, 失敗したら -1
    """

    # 念のためシステム状態をチェック
    if const.states["system"] == const.DISABLED:
        sg.popup_ok(
            "致命的なエラーです。システム無効化中に，入退室プロセスが実行されようとしました。これはプロうグラム内で致命的なバグが発生したことを知らせるメッセージです。この問題は速やかに対処されるべきです。速やかに開発者に連絡してください。",
            title="致命的なエラー！",
            keep_on_top=True,
            modal=True,
        )
        print(
            "[!!警告!!] 致命的なエラーです。システム無効化中に，入退室プロセスが実行されようとしました。これはプロうグラム内で致命的なバグが発生したことを知らせるメッセージです。速やかに開発者に連絡してください。"
        )
        return -1

    if not db.is_id_exists(id):
        print(
            "[Error] このカードは登録されていないため，入退室処理は行われませんでした。"
        )
        return -1

    attendance = db.execute_database(
        "SELECT attendance FROM student WHERE id = '%s'" % id
    )[0][0]

    name = db.execute_database("SELECT name FROM student WHERE id = '%s'" % id)[0][0]

    gender = db.execute_database("SELECT gender FROM student WHERE id = '%s'" % id)[0][
        0
    ]

    address = db.execute_database(
        "SELECT mail_address FROM parent WHERE id = '%s'" % id
    )[0][0]

    if attendance == "出席":
        if db.exit_room(id) == -1:  # 退室処理
            print("[Error] 退室処理に失敗しました。メールは送信されませんでした。")
        else:
            const.wav["goodbye"].play()  # 挨拶
            if (
                "full_screen_window" in windows
            ):  # フルスクリーンウィンドウが開いている場合
                windows["full_screen_window"]["-greeting-"].update(
                    name + "くん，さようなら！"
                    if gender == "男"
                    else name + "ちゃん，さようなら！"
                )
            threading.Thread(
                target=send_mail, args=(name, address, "exit")
            ).start()  # メール送信
    elif attendance == "退席":
        if db.enter_room(id) == -1:  # 入室処理
            print("[Error] 入室処理に失敗しました。メールは送信されませんでした。")
        else:
            if const.hour < 10:
                if const.saves["sys_setting"]["greeting_sound"]:
                    const.wav["goodmorning"].play()  # おはよう
                if (
                    "full_screen_window" in windows
                ):  # フルスクリーンウィンドウが開いている場合
                    windows["full_screen_window"]["-greeting-"].update(
                        name + "くん，おはよう!"
                        if gender == "男"
                        else name + "ちゃん，おはよう!"
                    )
            else:
                if const.saves["sys_setting"]["greeting_sound"]:
                    const.wav["hello"].play()  # こんにちは
                if (
                    "full_screen_window" in windows
                ):  # フルスクリーンウィンドウが開いている場合
                    windows["full_screen_window"]["-greeting-"].update(
                        name + "くん，こんにちは!"
                        if gender == "男"
                        else name + "ちゃん，こんにちは!"
                    )
            threading.Thread(
                target=send_mail, args=(name, address, "enter")
            ).start()  # メール送信
    else:
        print("[Error] データベース上の生徒の出席状態が不正です。")
        return -1
    return 0


def popup_window(layout, duration=0):
    """
    ポップアップウィンドウを作成します。

    Args:
        layout (list): pysimpleguiのレイアウト
        duration (int, optional): ウィンドウを表示する時間（秒）. Defaults to 0.
    Returns:
        window (sg.Window): ウィンドウ
    """
    window = sg.Window(
        "Message",
        layout,
        no_titlebar=True,
        keep_on_top=True,
        finalize=True,
        auto_close=False if duration == 0 else True,
        auto_close_duration=duration,
        modal=True,
        border_depth=2,
    )
    window.force_focus()
    return window


def now_processing_popup(message="処理中です..."):
    """
    処理中のポップアップを表示します。

    Args:
        message (str, optional): ポップアップに表示するメッセージ. Defaults to "処理中です...".

    Returns:
        window: sg.Window
    """
    sg.theme("LightGrey1")
    layout = [
        [
            sg.Text(
                message,
                text_color="black",
                font=("Arial", 20, "bold"),
                key="-nfcstate-",
                justification="center",
                expand_x=True,
            )
        ],
    ]
    window = popup_window(layout)
    window.read(timeout=0)
    return window


def wait_card_popup(message="カードをタッチしてください"):
    """
    NFCカードのタッチを待ちます。カードがタッチされた場合は，そのカードのIDを返します。カードがタッチされない場合は，-1を返します。

    Args:
        message (str, optional): ポップアップウィンドウに表示されるメッセージを指定します. Defaults to "カードをタッチしてください".

    Returns:
        id (str): NFCカードのID
    """
    if const.states["nfc"] == const.DISCONNECTED:
        sg.popup_ok(
            "NFCカードリーダに接続できませんでした。NFCカードリーダが正常に接続されていることを確認してから，システムを再起動してください。",
            title="NFCカードリーダ接続エラー",
            keep_on_top=True,
            modal=True,
        )
        return -1
    sg.theme("LightGrey1")
    layout = [
        [
            sg.Text(
                message,
                text_color="black",
                font=("Arial", 20, "bold"),
                key="-nfcstate-",
                justification="center",
                expand_x=True,
            )
        ],
        [
            sg.Image(
                filename="images/touching_card.png", key="-nfcimage-", expand_x=True
            )
        ],
        [
            sg.Button(
                "キャンセル", font=("Arial", 20, "bold"), key="-exit-", expand_x=True
            )
        ],
    ]
    window = popup_window(layout)
    window.force_focus()
    while True:
        event, _ = window.read(timeout=0)
        if event == "-exit-":
            window.close()
            return -1
        elif (
            id := nfc.check_nfc_was_touched(dismiss_time=2)
        ) != -1:  # NFCカードがタッチされた場合
            print("[Info] NFC card touched.", id)
            window.close()
            return id
        else:  # NFCカードがタッチされていない場合
            continue


def print_formatted_list(data: list):  # リストを整形して表示
    ret = ""
    for i in range(len(data)):
        for j in range(len(data[i])):
            ret = ret + str(data[i][j]) + " | "
        ret = ret + "\n"
    print(ret)


#! 生徒関連関数 ---------------------------------------------------------------------------------------------------------------------------
def assign_card_to_student(tmp_id: str):
    """
    未割当の生徒にカードを割り当てます。

    Args:
        id (str): 割り当てるカードのID
    """
    if (id := wait_card_popup("登録する生徒のカードをタッチしてください")) == -1:
        sg.popup_ok(
            "生徒の登録がキャンセルされました。",
            title="キャンセル",
            keep_on_top=True,
            modal=True,
        )
        return -1
    if db.is_id_exists(id):
        name = db.get_student_name(id)
        sg.popup_ok(
            f"このカードは既に登録されています。このカードに登録するには，既に登録されている生徒を除名してください。\n\n登録されている生徒: {name}",
            title="エラー",
            keep_on_top=True,
            modal=True,
        )
        return -1
    else:
        if (
            db.execute_database(f"UPDATE student SET id = '{id}' WHERE id = '{tmp_id}'")
            != 1
        ):
            if (
                db.execute_database(
                    f"UPDATE parent SET id = '{id}' WHERE id = '{tmp_id}'"
                )
                != 1
            ):
                sg.popup_ok(
                    "カードの割り当てを完了しました。",
                    title="完了",
                    keep_on_top=True,
                    modal=True,
                )
                return 0
        else:
            sg.popup_ok(
                "カードの割り当てに失敗しました。",
                title="エラー",
                keep_on_top=True,
                modal=True,
            )

    return -1


def register_student(
    name: str,
    age: int,
    gender: str,
    parent_name: str,
    mail_address: str,
    without_card: bool = False,
):  # 生徒を登録
    """
    生徒を登録します。カードなしで登録する場合は，IDには "temp_" から始まる一時的なIDが割り当てられます。

    Args:
        name (str): 登録する生徒の名前
        age (int): 登録する生徒の年齢
        gender (str): 登録する生徒の性別
        parent_name (str): 登録する生徒の保護者の名前
        mail_address (str): 登録する生徒の保護者のメールアドレス
        without_card (bool): カードなしで登録するかどうか

    Returns:
        ret (int): 成功した場合は 0，失敗した場合はそれ以外を返す。
    """
    if not without_card:  # カードありで登録する場合
        if (id := wait_card_popup("登録する生徒のカードをタッチしてください")) == -1:
            sg.popup_ok(
                "生徒の登録がキャンセルされました。",
                title="キャンセル",
                keep_on_top=True,
                modal=True,
            )
            return -1
    else:  # カードなしで登録する場合
        id = "temp_" + str(uuid.uuid4())  # 一時的なIDを割り当てる

    window = now_processing_popup()  # 処理中のポップアップを表示

    data = {
        "name": name,
        "age": age,
        "gender": gender,
        "parent_name": parent_name,
        "mail_address": mail_address,
        "id": id,
        "attendance": "退席",
    }
    ret = db.add_student_to_database(data)
    window.close()
    if ret == -1:
        sg.popup_ok(
            "生徒の登録に失敗しました。このカードは既に登録されています。このカードを別の生徒に割り当てるには，まずこのカードを所有する生徒の除名を行ってください。詳細は，システム出力を参照してください。",
            title="登録エラー",
            keep_on_top=True,
            modal=True,
        )
    elif ret == -2:
        sg.popup_ok(
            "生徒の登録に失敗しました。詳細は，システム出力を参照してください。",
            title="登録エラー",
            keep_on_top=True,
            modal=True,
        )
    return ret


def remove_student(name: str):
    """
    生徒の名前とカード情報を使用して，生徒を除名します。入力された名前とカードの名前を照合して，一致すれば除名を行います。

    Args:
        name (str): 除名する生徒の名前
    Returns:
        ret (int): 成功した場合は 0，失敗した場合は -1 を返す。
    """
    if (id := wait_card_popup("除名する生徒のカードをタッチしてください")) == -1:
        sg.popup_ok(
            "生徒の除名がキャンセルされました。",
            title="キャンセル",
            keep_on_top=True,
            modal=True,
        )
    else:
        window = now_processing_popup()  # 処理中のポップアップを表示

        ret = db.remove_student_from_database(id, name)

        window.close()
        if ret == -1:
            sg.popup_ok(
                "生徒の除名に失敗しました。このカードはデータベースに登録されていません。別のカードを試してください。詳細は，システム出力を参照してください。",
                title="エラー",
                keep_on_top=True,
                modal=True,
            )
        elif ret == -2:
            sg.popup_ok(
                "生徒の除名に失敗しました。入力された生徒の名前と，ICカードの登録されている名前が一致しません。別のカードを試してください。詳細は，システム出力を参照してください。",
                title="エラー",
                keep_on_top=True,
                modal=True,
            )
            return -1
        else:
            sg.popup_ok(
                "生徒の除名を完了しました。: " + name,
                title="完了",
                keep_on_top=True,
                modal=True,
            )


def remove_student_without_card(
    name: str, age: int, gender: str, parents_name: str, mail_address: str
):
    """
    生徒の情報データのみを使って，生徒を除名します。全て一致するデータが見つかれば，除名を行います。

    Args:
        name (str): 除名する生徒の名前
        age (int): 除名する生徒の年齢
        gender (str): 除名する生徒の性別
        parents_name (str): 除名する生徒の保護者の名前
        mail_address (str): 除名する生徒の保護者のメールアドレス
    """
    students = db.execute_database(
        "SELECT * FROM student join parent on student.id = parent.id"
    )
    if len(students) == 0:
        sg.popup_ok(
            "データベースに生徒の情報が登録されていません。",
            title="除名エラー",
            keep_on_top=True,
            modal=True,
        )
        return -1
    for student in students:
        if (
            student[1] == name
            and student[2] == gender
            and int(student[3]) == int(age)
            and student[6] == parents_name
            and student[7] == mail_address
        ):
            if (
                sg.popup_yes_no(
                    "入力された情報に一致する生徒が見つかりました。: \n\n氏名: %s\n年齢: %s\n性別: %s\n保護者の氏名: %s\n保護者のメールアドレス: %s\n\nこの生徒を除名を実行してよろしいですか？"
                    % (name, age, gender, parents_name, mail_address),
                    title="除名の確認",
                    keep_on_top=True,
                    modal=True,
                )
                == "Yes"
            ):
                if db.remove_student_from_database(id, name) == -1:
                    sg.popup_ok(
                        "生徒の除名に失敗しました。このカードはデータベースに登録されていません。別のカードを試してください。詳細は，システム出力を参照してください。",
                        title="エラー",
                        keep_on_top=True,
                        modal=True,
                    )
                    return -1
                else:
                    sg.popup_ok(
                        "生徒の除名を完了しました。: " + name,
                        title="完了",
                        keep_on_top=True,
                        modal=True,
                    )
        else:
            sg.popup_ok(
                "入力された情報に一致する生徒が見つかりませんでした。入力した情報が正しいか，もう一度確認してください",
                title="除名エラー",
                keep_on_top=True,
                modal=True,
            )


if __name__ == "__main__":
    main()
    # if is_admin():
    #     main()
    # else:
    #     ctypes.windll.shell32.ShellExecuteW(
    #         None, "runas", sys.executable, " ".join(sys.argv), None, 1
    #     )
    for thread in threading.enumerate():
        if thread.is_alive() and thread is not threading.current_thread():
            thread.join()
    sys.exit()
