import PySimpleGUI as sg

import config.values as const


def get_window():
    # 入退室切り替えボタンのフレーム
    frame_system_info = sg.Frame(
        "システム状態",
        [
            [
                sg.Button(
                    "状態確認中...",
                    font=("Arial", 30, "bold"),
                    button_color="gray",
                    key="-power-",
                    tooltip="システムの有効化/無効化を切り替えます",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
        ],
        expand_x=True,
        size=(100, 150),
        vertical_alignment="top",
    )  # 幅,高さ

    # 主な操作のフレーム
    frame_main_control = sg.Frame(
        "主な操作",
        [
            [
                sg.Button(
                    "待ち受け画面を表示",
                    size=(30, 2),
                    key="-toggle_fullscreen-",
                    tooltip="全画面待ち受けモードに切り替えます",
                    button_color="black",
                    expand_x=True,
                ),
            ],
        ],
        vertical_alignment="top",
        expand_x=True,
        expand_y=True,
    )  # 幅,高さ

    # データベース操作のフレーム
    frame_st_control = sg.Frame(
        "生徒の管理",
        [
            [
                sg.Text(
                    "生徒の追加・除名など，生徒の管理を行います",
                    font=("Arial", 10),
                    expand_x=True,
                    justification="center",
                ),
            ],
            [
                sg.Button(
                    "生徒の一覧の表示",
                    key="-show_all_students-",
                    tooltip="データベースにある生徒の一覧をすべて表示します",
                    expand_x=True,
                    auto_size_button=False,
                    size=(20, 1),
                ),
                sg.Button(
                    "生徒にカードを割り当てる...",
                    key="-assign_card_to_unassigned_student-",
                    tooltip="未割り当ての生徒にカードを割り当てます",
                    expand_x=True,
                    auto_size_button=False,
                    size=(20, 1),
                ),
            ],
            [
                sg.Button(
                    "生徒の新規登録...",
                    key="-add_student-",
                    tooltip="新規に生徒を登録します",
                    expand_x=True,
                    auto_size_button=False,
                    size=(15, 1),
                ),
                sg.Button(
                    "生徒の除名...",
                    key="-remove_student-",
                    tooltip="新規に生徒を登録します",
                    expand_x=True,
                    auto_size_button=False,
                    size=(15, 1),
                ),
            ],
        ],
        expand_x=True,
        expand_y=False,
    )

    frame_db_control = sg.Frame(
        "システムログ",
        [
            [
                sg.Text(
                    "システム関係のログを表示します",
                    font=("Arial", 10),
                    expand_x=True,
                    justification="center",
                ),
            ],
            [
                sg.Button(
                    "入退室ログの表示",
                    key="-show_all_logs-",
                    tooltip="データベースにある入退室ログをすべて表示します",
                    expand_x=True,
                    auto_size_button=False,
                    size=(15, 1),
                ),
                sg.Button(
                    "システムログの表示",
                    tooltip="システムログをすべて表示します",
                    key="-show_all_system_logs-",
                    expand_x=True,
                    auto_size_button=False,
                    size=(15, 1),
                ),
            ],
        ],
        expand_x=True,
        expand_y=False,
    )

    # SQL操作のフレーム
    frame_sql_control = sg.Frame(
        "SQLでのデータベース管理（高度）",
        [
            [
                sg.Text(
                    "SQLコマンドを使用して，データベースの管理を行います。",
                    font=("Arial", 10),
                    expand_x=True,
                    justification="center",
                ),
            ],
            [
                sg.Text(
                    "SQLの実行:",
                    font=("Arial", 15),
                    justification="left",
                    expand_x=True,
                    expand_y=True,
                    tooltip="データベースの管理",
                    key="-state-",
                ),
                sg.InputText(
                    font=("Arial", 15),
                    key="-sql-",
                    tooltip="実行するSQL文を入力します",
                    background_color="black",
                    text_color="light green",
                    expand_x=True,
                ),
            ],
            [
                sg.Button(
                    "実行",
                    font=("Arial", 13, "bold"),
                    size=(5, 1),
                    key="-execute-",
                    tooltip="入力されたSQL文を実行します",
                    expand_x=True,
                ),
            ],
            [
                sg.Button(
                    "コミット",
                    size=(10, 1),
                    key="-commit-",
                    tooltip="データベースの変更を確定します",
                    expand_x=True,
                ),
                sg.Button(
                    "ロールバック",
                    size=(10, 1),
                    key="-rollback-",
                    tooltip="データベースの変更を取り消します",
                    expand_x=True,
                ),
            ],
        ],
        expand_x=True,
        expand_y=False,
    )

    # システムログのフレーム
    frame_system_log = sg.Frame(
        "システム出力",
        [
            [
                sg.Multiline(
                    font=("Arial", 10),
                    key="-log-",
                    echo_stdout_stderr=True,
                    disabled=True,
                    autoscroll=True,
                    horizontal_scroll=True,
                    reroute_stdout=True,
                    reroute_cprint=True,
                    write_only=True,
                    do_not_clear=True,
                    expand_x=True,
                    expand_y=True,
                    background_color="black",
                    text_color="light green",
                )
            ],
            [
                sg.Button(
                    "システム出力を別ウィンドウで表示...",
                    size=(50, 1),
                    key="-pop_log_win-",
                    expand_x=True,
                ),
            ],
        ],
        vertical_alignment="top",
        element_justification="left",
        size=(750, 500),
        expand_y=True,
    )

    #! タブの定義
    tabs = {}
    tabs["main"] = [
        [
            sg.Column(
                [
                    [frame_system_info],
                    [frame_main_control],
                    [frame_st_control],
                    [frame_db_control],
                    [frame_sql_control],
                ],
                vertical_alignment="top",
                justification="left",
                expand_x=True,
                # size=(600, 500),
                expand_y=True,
            ),
            sg.Column([[frame_system_log]], expand_x=False, expand_y=True),
        ],
    ]

    #! 送信するメールを設定するタブ
    tabs["set_mail_content_entered"] = [
        [
            sg.Text(
                "件名:",
                font=("Arial", 15),
                justification="left",
                pad=((0, 0), (0, 0)),
            ),
            sg.InputText(
                size=(50, 1),
                font=("Arial", 15),
                key="-entered_mail_subject-",
                pad=((0, 0), (0, 0)),
                expand_x=True,
            ),
        ],
        [
            sg.Text(
                "本文:",
                font=("Arial", 15),
                justification="left",
                pad=((0, 0), (0, 0)),
            ),
            sg.Multiline(
                size=(50, 1),
                font=("Arial", 15),
                key="-entered_mail_body-",
                pad=((0, 0), (0, 0)),
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]
    tabs["set_mail_content_exited"] = [
        [
            sg.Text(
                "件名:",
                font=("Arial", 15),
                justification="left",
                pad=((0, 0), (0, 0)),
            ),
            sg.InputText(
                size=(50, 1),
                font=("Arial", 15),
                key="-exited_mail_subject-",
                pad=((0, 0), (0, 0)),
                expand_x=True,
            ),
        ],
        [
            sg.Text(
                "本文:",
                font=("Arial", 15),
                justification="left",
                pad=((0, 0), (0, 0)),
            ),
            sg.Multiline(
                size=(50, 1),
                font=("Arial", 15),
                key="-exited_mail_body-",
                pad=((0, 0), (0, 0)),
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]
    tabs["set_mail_content"] = [
        [
            sg.Text(
                "生徒が入退室したときに保護者に送信する通知メールの内容を設定します",
                justification="center",
                expand_x=True,
            ),
        ],
        [
            sg.Text(
                "「{name}」を入力すると，その部分が生徒の名前に置き換えられます",
                justification="center",
                expand_x=True,
            )
        ],
        [
            sg.TabGroup(
                [
                    [sg.Tab("入室時", tabs["set_mail_content_entered"])],
                    [sg.Tab("退室時", tabs["set_mail_content_exited"])],
                ],
                expand_x=True,
                expand_y=True,
            )
        ],
        [
            sg.InputText(
                size=(50, 1),
                font=("Arial", 15),
                key="-test_mail_address-",
                pad=((0, 0), (0, 0)),
                expand_x=True,
                tooltip="テストメールを送信するメールアドレスを入力します",
            ),
            sg.Button(
                "テストメールを送信",
                size=(20, 1),
                key="-send_test_mail-",
            ),
        ],
    ]

    frames = {}
    frames["set1"] = sg.Frame(
        "アカウント設定",
        [
            [
                sg.Text(
                    "通知メール送信に使用するメールアドレス：　　　",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (0, 0)),
                    tooltip="アテンダンから，保護者へ送信する入退室通知メールの送信に使用するメールアドレスを入力します",
                ),
                sg.InputText(
                    size=(50, 1),
                    font=("Arial", 10),
                    key="-sysset_from-",
                    pad=((10, 10), (0, 0)),
                    expand_x=True,
                    tooltip="アテンダンから，保護者へ送信する入退室通知メールの送信に使用するメールアドレスを入力します",
                ),
            ],
            [
                sg.Text(
                    "パスワード：　　　　　　　　　　　　　　　　　",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (5, 0)),
                    tooltip="上記のアカウントのパスワードを入力します。Googleアカウントの場合は，アプリパスワードを作成してそれを使用します。",
                ),
                sg.InputText(
                    size=(50, 1),
                    font=("Arial", 10),
                    key="-sysset_password-",
                    pad=((10, 10), (5, 0)),
                    expand_x=True,
                    tooltip="上記のアカウントのパスワードを入力します。Googleアカウントの場合は，アプリパスワードを作成してそれを使用します。",
                ),
            ],
            [
                sg.Text(
                    "通知メール送信に使用する予備メールアドレス：　",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (5, 0)),
                    tooltip="メインのアドレスがメール送信に使用できなかった場合，代替で使用するメールアドレスを入力します",
                ),
                sg.InputText(
                    size=(50, 1),
                    font=("Arial", 10),
                    key="-sysset_second_from-",
                    pad=((10, 10), (5, 0)),
                    expand_x=True,
                    tooltip="メインのアドレスがメール送信に使用できなかった場合，代替で使用するメールアドレスを入力します",
                ),
            ],
            [
                sg.Text(
                    "パスワード：　　　　　　　　　　　　　　　　　",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (5, 0)),
                    tooltip="上記のアカウントのパスワードを入力します。Googleアカウントの場合は，アプリパスワードを作成してそれを使用します。",
                ),
                sg.InputText(
                    size=(50, 1),
                    font=("Arial", 10),
                    key="-sysset_second_password-",
                    pad=((10, 10), (5, 0)),
                    expand_x=True,
                    tooltip="上記のアカウントのパスワードを入力します。Googleアカウントの場合は，アプリパスワードを作成してそれを使用します。",
                ),
            ],
            [
                sg.Text(
                    "アテンダンからの情報を受け取るメールアドレス：",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (15, 0)),
                    tooltip="アテンダンシステムで，何らかの問題が発生した際にその旨の通知を受け取るメールアドレスを入力します",
                ),
                sg.InputText(
                    size=(50, 1),
                    font=("Arial", 10),
                    key="-sysset_notify_address-",
                    pad=((10, 10), (15, 0)),
                    expand_x=True,
                    tooltip="アテンダンシステムで，何らかの問題が発生した際にその旨の通知を受け取るメールアドレスを入力します",
                ),
            ],
        ],
        vertical_alignment="left",
        expand_x=True,
        expand_y=True,
    )
    frames["set2"] = sg.Frame(
        "入退室処理",
        [
            [
                sg.Text(
                    "カードタッチ時にタッチ音を鳴らす",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (0, 0)),
                ),
                sg.Checkbox(
                    "",
                    font=("Arial", 10),
                    pad=((0, 0), (0, 0)),
                    key="-sysset_touch_sound-",
                ),
            ],
            [
                sg.Text(
                    "カードタッチ時に挨拶音声を鳴らす",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (0, 0)),
                ),
                sg.Checkbox(
                    "",
                    font=("Arial", 10),
                    pad=((0, 0), (0, 0)),
                    key="-sysset_greeting_sound-",
                ),
            ],
            [
                sg.Text(
                    "同一カードのタッチを次の秒数無視する:",
                    font=("Arial", 10),
                    justification="left",
                    pad=((10, 0), (0, 0)),
                ),
                sg.Combo(
                    values=["5", "10", "30", "60", "120"],
                    font=("Arial", 10),
                    key="-syset_ignore_same_card-",
                    pad=((0, 10), (0, 0)),
                    default_value=const.saves["sys_setting"]["ignore_card_time"],
                    expand_x=True,
                    readonly=True,
                ),
            ],
        ],
        vertical_alignment="left",
        expand_x=True,
        expand_y=True,
    )

    # scrollable_column = sg.Column(
    #     [
    #         [frames["set1"]],
    #         [frames["set2"]],
    #     ],
    #     vertical_scroll_only=True,
    #     # scrollable=True,
    #     expand_y=True,
    #     expand_x=True,
    #     size=(750, 500),
    #     justification="center",
    # )
    tabs["system_setting"] = [
        [
            sg.Text(
                "アテンダンの設定を行います", justification="center", expand_x=True
            ),
        ],
        [
            # scrollable_column,
            frames["set1"],
            frames["set2"],
        ],
    ]

    #! メニューの定義
    menu_def = [
        ["システム操作", ["入退出処理の有効化/無効化を切り替え", "アテンダンを終了"]],
        [
            "データベース操作",
            [
                "生徒の管理",
                [
                    "生徒の一覧の表示",
                    "生徒の新規登録",
                    "生徒の除名",
                ],
                "システムログ",
                [
                    "入退室ログの表示",
                    "システムログの表示",
                ],
            ],
        ],
        [
            "CSV出力",
            [
                "生徒の情報をCSV形式で出力",
                "生徒とその保護者の情報をCSV形式で出力",
                "入退室ログをCSV形式で出力",
                "システムログをCSV形式で出力",
            ],
        ],
        [
            "ヘルプ",
            [
                "バージョン情報",
                "ライセンス表示",
            ],
        ],
    ]

    layout = [
        [sg.Menu(menu_def, tearoff=False, key="-menu-")],
        [
            sg.Text(
                "状態を確認しています...",
                background_color="gray",
                text_color="white",
                font=("Arial", 20, "bold"),
                expand_x=True,
                justification="center",
                key="-nfcstate-",
                tooltip="NFCリーダーの状態",
            ),
            sg.Text(
                "%02d:%02d:%02d" % (const.hour, const.minute, const.second),
                font=("Arial", 20, "bold"),
                key="-time-",
            ),
        ],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("メインパネル", tabs["main"]),
                        sg.Tab("通知メール内容設定", tabs["set_mail_content"]),
                        sg.Tab("システム設定", tabs["system_setting"]),
                    ],
                ],
            ),
        ],
    ]

    window = sg.Window(
        const.SYSTEM_NAME + "  ver. " + const.VERSION,
        layout,
        resizable=False,
        finalize=True,
        size=(1270, 710),
        return_keyboard_events=True,
    )

    return window


if __name__ == "__main__":  # テスト用
    window = get_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
