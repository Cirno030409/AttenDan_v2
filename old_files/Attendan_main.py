"""
Attendance system for RoboDone main program
Author@ yuta tanimura
"""

import csv
import datetime
import os
import sys
import threading
import uuid
import ctypes
import json

import PySimpleGUI as sg

import config.values as const
import functions.database_func as db
import functions.nfc_func as nfc
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
import updator.updator as updator

ml = mm.Mail()
windows = {}

init_error = {
    "database": "",
    "smtp": "",
    "nfc": "",
}  # "" = no error, "error message" = error


def main():
    window = splash_window.get_window()
    window.read(timeout=0)
    init_system()  # 初期化
    window.close()
    showgui_main()  # GUIを表示

    # システム終了処理
    db.add_systemlog_to_database("システム終了")  # システムログに記録
    db.commit_database()  # データベースにコミットする
    db.disconnect_from_database()  # データベースを切断する
    nfc.disconnect_reader()  # NFCリーダーを切断する
    ml.logout_smtp()  # SMTPサーバーからログアウトする
    
def is_admin(): # 管理者権限を持っているかどうかを確認する
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def check_for_update(): # アップデートがあるかどうかを確認する
    ret = updator.is_exist_update() # アップデートがあるかどうかを確認
    if ret != -1:
        if updator.is_exist_update(): # アップデートがあるかどうかを確認
            latest_ver, release_title, release_body, _ = updator.get_latest_release_info()
            latest_ver_str = str(latest_ver)
            latest_ver_str ="v" + latest_ver_str[0] + '.' + latest_ver_str[1] + '.' + latest_ver_str[2]
            if sg.PopupYesNo(f'新しいバージョン {latest_ver_str} が見つかりました。アップデートの内容は以下の通りです。\n\n\nアップデート名: {release_title}\n\nアップデート内容: {release_body}\n\n\nアップデートしますか？ Yesを選択すると，アテンダンは終了し，アップデーターが起動されます。', title='アテンダン アップデーター', keep_on_top=True) == 'Yes':
                pass


def init_system():  # 初期化
    global init_error
    print("[Info] system initializing...")
    
    # 変数のロード
    if os.path.exists(const.SAVES_PATH):
        with open(const.SAVES_PATH, "rb") as f:
            const.saves = json.load(f)
            
    if const.saves["system_unused"] == True: # 初回起動時の処理
        pass
    
    check_for_update() # アップデートがあるかどうかを確認

    
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
        ml.login_smtp("robotomiline@gmail.com", "gzmt tjim egtb fwad") == -1
    ):                                  # SMTPサーバーにログイン
        print("[Error] Couldn't login to SMTP server.")
        init_error["smtp"] = "error"
        sg.popup_ok(""
            "SMTPサーバーにログインできませんでした。ネットワーク接続または，ログインするアカウント設定を確認してください。また，システム管理者に問い合わせてください。",
            title="システム初期化エラー",
            keep_on_top=True,
            modal=True,
        )
    
    ret = nfc.connect_reader()
    if (not const.ignore_nfc_error) and (ret != 0): # NFCリーダーに接続する
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
    return init_error


def showgui_main():  # GUIを表示
    global init_error

    # トグルボタンの初期化
    toggles = {
        "power": True,  # 入退室処理の有効化トグル
        "fullscreen": False,  # フルスクリーンモードの有効化トグル
    }

    sg.theme("BluePurple")  # テーマをセット

    windows["main"] = main_window.get_window()  # メインwindowを取得

    # メールの設定を反映
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

    windows["poppped_system_log_window"] = popped_system_log_window.get_window()
    windows["poppped_system_log_window"].hide()

    #! 起動時のメッセージ
    print(
        "=======    Welcome to "
        + const.SYSTEM_NAME
        + " ver. "
        + const.VERSION
        + "   ======="
    )

    if (num := how_many_unassigned_cards()) != 0:
        print(
            "[Warning] カード未割り当ての生徒が "
            + str(num)
            + " 名います。「生徒にカードを割り当てる」ボタンより，カードの割り当てを行ってください。"
        )

    if init_error["database"] != "":
        print(
            "[Warning] データベースに接続できませんでした。データベースファイルが存在することを確認してください。また，システム管理者に問い合わせてください。: ", init_error["database"]
        )

    if init_error["smtp"] != "":
        print(
            "[Warning] SMTPサーバーにログインできませんでした。ネットワーク接続または，ログインするアカウント設定を確認してください。また，システム管理者に問い合わせてください。: ", init_error["smtp"]
        )

    if init_error["nfc"] != "":
        print(
            "[Warning] NFCカードリーダに接続できませんでした。NFCカードリーダが正常に接続されていることを確認してから，システムを再起動してください。: ", init_error["nfc"]
        )

    if const.states["nfc"] == const.DISCONNECTED:
        print(
            "[Info] NFCカードリーダが接続されていません。入退室処理を有効化するには，NFCカードリーダが正常に接続されていることを確認し，システムを再起動してください。: ", init_error["nfc"]
        )
        
    const.day = datetime.datetime.now().day  # 日付を取得

    # メインループ ====================================================================================================
    while True:
        # ウィンドウ表示

        sg.theme("BluePurple")  # テーマをセット

        # 更新
        ## 日付が変わったら，生徒の出席状況をリセット
        if const.day != datetime.datetime.now().day:
            db.execute_database("UPDATE student SET attendance = '退席'")
            db.commit_database()
            print("[Info] 日付が変わったので，全生徒の出席状態を '退席' に変更しました。")
        ## 現在時刻を取得
        const.year = datetime.datetime.now().year
        const.month = datetime.datetime.now().month
        const.day = datetime.datetime.now().day
        const.hour = datetime.datetime.now().hour
        const.minute = datetime.datetime.now().minute
        const.second = datetime.datetime.now().second
        
        ## NFCのカードのタッチを確認
        if (
            const.states["nfc"] == const.CONNECTED  # NFCカードリーダが接続されている
            and const.states["system"] == const.ENABLED  # システムが有効化されている
        ):
            if (id := nfc.check_nfc_was_touched()) != -1:  # NFCカードがタッチされたかどうかを確認
                print("[Info] 入退室プロセスを実行しています...")
                run_attendance_process(id)  #! 入退室処理を行う
        else:
            const.nfc_data[
                "touched_flag"
            ] = False  # システムが有効化されたときに，遅れてカードが反応しないように常にFalseにする

        ##! システムの状態をトグルボタンに反映
        if const.states["system"] == const.ENABLED:
            toggles["power"] = True
        elif const.states["system"] == const.DISABLED:
            toggles["power"] = False

        for i, win in enumerate(list(windows.values())):  # すべてのウィンドウに対して更新
            event, values = win.read(timeout=0)

            ## メインウィンドウ以外のウィンドウの終了処理
            if win != windows["main"]:
                if event == sg.WIN_CLOSED or event is None:
                    win.close()  # ウィンドウを閉じる
                    windows.pop(list(windows.keys())[i])  # ウィンドウを削除
                    continue

            ## メインウィンドウ
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
                    win["-power-"].update(text="入退室処理 無効", button_color="white on red")

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
                        background_color="red",
                        text_color="white",
                    )
                elif (
                    const.states["nfc"] == const.CONNECTED
                    and const.states["system"] == const.ENABLED
                ):
                    win["-nfcstate-"].update(
                        "カードをタッチすると，生徒の入退室処理が実行されます",
                        background_color="green",
                        text_color="white",
                    )
                elif (
                    const.states["nfc"] == const.CONNECTED
                    and const.states["system"] == const.DISABLED
                ):
                    win["-nfcstate-"].update(
                        "カードをタッチしても，入退室処理を行いません",
                        background_color="yellow",
                        text_color="black",
                    )

                ###! システム状態切り替えトグルボタン
                if event == "-power-":
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
                            continue
                        if (
                            sg.popup_yes_no(
                                "入退室処理を有効化すると，カードがタッチされると生徒の入退室処理が実行されるようになります。よろしいですか？",
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
                ### 主な操作パネルのボタン
                #### 待ち受け画面の表示・非表示
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
                                windows[
                                    "full_screen_window"
                                ] = full_screen_window.get_window()
                    else:
                        windows["full_screen_window"].hide()
                        windows.pop("full_screen_window")
                    toggles["fullscreen"] = not toggles["fullscreen"]  # トグルの状態を反転

                ### データベース管理パネルのボタン
                elif event == "-show_all_students-":
                    print("---- 生徒一覧 ----")
                    print_formatted_list(
                        db.execute_database(
                            "SELECT * FROM student join parent on student.id = parent.id"
                        )
                    )
                elif event == "-show_all_system_logs-":
                    print("---- システムログ ----")
                    print_formatted_list(
                        db.execute_database("SELECT * FROM system_log")
                    )
                elif event == "-show_all_logs-":
                    print("---- 入退室ログ ----")
                    print_formatted_list(db.execute_database("SELECT * FROM log"))
                elif event == "-add_student-":
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
                elif event == "-remove_student-":
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
                    windows[
                        "assign_card_to_student"
                    ] = allocate_card_to_student_window.get_window()

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
                        windows[
                            "poppped_system_log_window"
                        ] = popped_system_log_window.get_window()

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
                        if send_mail(mode="test") == -1:
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

                #### メールの設定を保存
                const.saves["mail"]["enter"]["subject"] = values[
                    "-entered_mail_subject-"
                ]
                const.saves["mail"]["enter"]["body"] = values["-entered_mail_body-"]
                const.saves["mail"]["exit"]["subject"] = values["-exited_mail_subject-"]
                const.saves["mail"]["exit"]["body"] = values["-exited_mail_body-"]
                const.saves["mail"]["test_address"] = values["-test_mail_address-"]

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
                    windows[
                        "register_student_from_csv"
                    ] = register_student_from_csv_window.get_window()

            ## CSVから生徒を登録ウィンドウ
            elif (
                "register_student_from_csv" in windows
                and win == windows["register_student_from_csv"]
            ):
                if event == "-load_csv-":
                    path = sg.popup_get_file(
                        "CSVファイルを選択してください", file_types=(("CSVファイル", "*.csv"),)
                    )
                    if path is None or path == "":
                        continue
                    else:
                        csv_error = False
                        with open(path, "r", encoding="utf-8") as f:
                            reader = csv.reader(f)
                            students = list(reader)
                            if students[0][0] == "生徒の氏名":  # ヘッダーがある場合は削除
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
                                        print("CSV loading error: フィールド数が不正です。")
                                        csv_error = True
                                        break
                                try:
                                    for student in students:
                                        int(student[1])
                                except ValueError as e:
                                    print("CSV loading error: 年齢が不正です。年齢は数字である必要があります。")
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
                    windows[
                        "remove_student_without_card"
                    ] = remove_student_without_card_window.get_window()

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
                    now_processing_window = now_processing_popup()  # 処理中のポップアップを表示
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
                if event == "-assign_card-":
                    while how_many_unassigned_cards() != 0:
                        register_student()

            ## ポップアウトされたシステム出力ウィンドウ
            elif (
                "poppped_system_log_window" in windows
                and win == windows["poppped_system_log_window"]
            ):
                if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                    win.hide()

                elif event == "-close-":
                    win.hide()


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
    with open(const.SAVES_PATH, 'w') as f:
        json.dump(const.saves, f)


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


def send_mail(id="", mode="test"):
    """
    入退室メールを送信します。

    Args:
        id (str): 入退室した生徒のID
        mode (str): 送信するメールの種類。"enter"，"exit"または"test"のいずれかを指定します。"test"を指定すると，テストメールアドレスにテストメールを送信します。
    """
    if const.states["system"] == const.DISABLED:
        print(
            "[!!警告!!] 致命的なエラーです。システム無効化中に，メール送信が実行されようとしました。これはプログラム内の致命的なバグが発生したことを知らせるメッセージです。速やかに開発者に連絡し，修正してください。"
        )
        return -1

    if mode == "enter":
        if (
            ml.send(
                db.execute_database(
                    "SELECT mail_address FROM parent WHERE id = '%s'" % id
                )[0][0],
                const.saves["mail"]["enter"]["subject"].format(
                    name=db.execute_database(
                        "SELECT name FROM student WHERE id = '%s'" % id
                    )[0][0]
                ),
                const.saves["mail"]["enter"]["body"].format(
                    name=db.execute_database(
                        "SELECT name FROM student WHERE id = '%s'" % id
                    )[0][0]
                ),
            )
            == -1
        ):
            print("[Error] メールの送信に失敗しました。")
            return -1
    elif mode == "exit":
        if (
            ml.send(
                db.execute_database(
                    "SELECT mail_address FROM parent WHERE id = '%s'" % id
                )[0][0],
                const.saves["mail"]["exit"]["subject"].format(
                    name=db.execute_database(
                        "SELECT name FROM student WHERE id = '%s'" % id
                    )[0][0]
                ),
                const.saves["mail"]["exit"]["body"].format(
                    name=db.execute_database(
                        "SELECT name FROM student WHERE id = '%s'" % id
                    )[0][0]
                ),
            )
            == -1
        ):
            print("[Error] メールの送信に失敗しました。")
            return -1
    elif mode == "test":
        if (
            ml.send(
                const.saves["mail"]["test_address"],
                const.saves["mail"]["enter"]["subject"].format(name="山田太郎"),
                const.saves["mail"]["enter"]["body"].format(name="山田太郎"),
            )
            == -1
        ):
            print("[Error] メールの送信に失敗しました。")
            return -1
        if (
            ml.send(
                const.saves["mail"]["test_address"],
                const.saves["mail"]["exit"]["subject"].format(name="山田太郎"),
                const.saves["mail"]["exit"]["body"].format(name="山田太郎"),
            )
            == -1
        ):
            print("[Error] メールの送信に失敗しました。")
            return -1
    else:
        print("[Error] send_mail()のmode引数が不正です。")
        return -1


#! 入退室処理実行関数
def run_attendance_process(id: str):
    """
    生徒の入退室処理を行います。出席状態を反転し，メールを送信します。

    Args:
        id (str): 入退室処理を行う生徒のID
    """
    # 念のためチェック
    if const.states["system"] == const.DISABLED:
        print(
            "[!!警告!!] 致命的なエラーです。システム無効化中に，入退室プロセスが実行されようとしました。これはプロうグラム内で致命的なバグが発生したことを知らせるメッセージです。速やかに開発者に連絡してください。"
        )
        return -1

    if not db.is_id_exists(id):
        print("[Error] このカードは登録されていないため，入退室処理は行われませんでした。")
        return -1

    const.wav_touched.play()  # タッチ音を再生

    attendance = db.execute_database(
        "SELECT attendance FROM student WHERE id = '%s'" % id
    )[0][0]

    if attendance == "出席":
        if db.exit_room(id) == -1:  # 退室処理
            print("[Error] 退室処理に失敗しました。メールは送信されませんでした。")
        else:
            send_mail(id, "exit")
    elif attendance == "退席":
        if db.enter_room(id) == -1:  # 入室処理
            print("[Error] 入室処理に失敗しました。メールは送信されませんでした。")
        else:
            send_mail(id, "enter")
    else:
        print("[Error] データベース上の生徒の出席状態が不正です。")
        return -1


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
        [sg.Button("キャンセル", font=("Arial", 20, "bold"), key="-exit-", expand_x=True)],
    ]
    window = popup_window(layout)
    window.force_focus()
    while True:
        event, _ = window.read(timeout=0)
        if event == "-exit-":
            window.close()
            return -1
        elif (id := nfc.check_nfc_was_touched(dismiss_time=2)) != -1:  # NFCカードがタッチされた場合
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
                "生徒の登録がキャンセルされました。", title="キャンセル", keep_on_top=True, modal=True
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
        sg.popup_ok("生徒の除名がキャンセルされました。", title="キャンセル", keep_on_top=True, modal=True)
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
                "生徒の除名を完了しました。: " + name, title="完了", keep_on_top=True, modal=True
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
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    for thread in threading.enumerate():
        if thread.is_alive() and thread is not threading.current_thread():
            thread.join()
    sys.exit()