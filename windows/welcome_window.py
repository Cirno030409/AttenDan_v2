import os
import subprocess

import PySimpleGUI as sg


def get_driver_install_window():
    layout = [
        [
            sg.Text(
                "ICカードリーダドライバのインストール",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (20, 80)),
                text_color="pink",
            )
        ],
        [
            sg.Text(
                "ICカードリーダのドライバのインストールを行います。\n\nこの作業を行わないとカードリーダは使用できません。\n\nカードリーダがない場合は，セットアップができません。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Text(
                "使用するカードリーダをPCに接続してください。",
                font=("Arial", 16, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (20, 0)),
            )
        ],
        [
            sg.Button(
                "接続しました",
                size=(10, 1),
                font=("Arial", 15),
                pad=((0, 0), (160, 0)),
                key="-next_to_driver2-",
                expand_x=True,
            )
        ],
    ]
    return layout


def get_driver_install_window2():
    subprocess.Popen("driver_installer.exe", shell=True)
    layout = [
        [
            sg.Text(
                "ICカードリーダドライバのインストール",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
                text_color="pink",
            )
        ],
        [
            sg.Text(
                "以下の手順を行い，ドライバーのインストールを行います。",
                font=("Arial", 15, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Text(
                """1. 「このアプリがデバイスに変更を加えることを許可しますか？」というアクセス許可の確認が表示されます。「はい」を選択して許可してください。
                表示されない場合，バックグラウンドで起動している可能性があるので，タスクバーを確認してください。""",
                font=("Arial", 12),
                justification="left",
                expand_x=True,
                pad=((20, 0), (30, 0)),
            )
        ],
        [
            sg.Text(
                """2. 「Zadig」というウィンドウが表示されたら，上部のリストボックスで「RC-S380/S」が選択されていることを確認します。
                選択されていなければ，リストから手動で選択します。""",
                font=("Arial", 12),
                justification="left",
                expand_x=True,
                pad=((20, 0), (30, 0)),
            )
        ],
        [
            sg.Text(
                """3. 下部にある「Install Driver」ボタンを選択してドライバーをインストールします。
                少しの間，「Installing Driver...」ウィンドウが表示され，ドライバーがインストールされます。
                「The driver was installed successfully」と表示されたら，ドライバーのインストールが完了です。""",
                font=("Arial", 12),
                justification="left",
                expand_x=True,
                pad=((20, 0), (30, 0)),
            )
        ],
        [
            sg.Text(
                """4. 「The driver was installed successfully」と表示されたら，ドライバーのインストールが完了です。""",
                font=("Arial", 12),
                justification="left",
                expand_x=True,
                pad=((20, 0), (30, 0)),
            )
        ],
        [
            sg.Image(
                "./resources/images/zadig.png",
                size=(500, 300),
                pad=((0, 0), (0, 0)),
                expand_x=True,
            )
        ],
        [
            sg.Button(
                "手順を完了しました",
                size=(50, 1),
                font=("Arial", 15),
                pad=((0, 0), (0, 0)),
                key="-next_to_1-",
                expand_x=True,
            )
        ],
    ]
    return layout


def get_window():
    layout = [
        [
            sg.Text(
                "アテンダンへようこそ",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (190, 80)),
                text_color="pink",
            )
        ],
        [
            sg.Text(
                "アテンダンは，生徒の出席状況を管理し，生徒の到着や出発を保護者に連絡するシステムです。\n\nまず，アテンダンを使用するために必要な設定や準備を行います。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Button(
                "次へ",
                size=(10, 1),
                font=("Arial", 15),
                pad=((750, 0), (320, 0)),
                key="-next_to_driver-",
                expand_x=True,
            )
        ],
    ]
    window = sg.Window("アテンダンへようこそ", layout, finalize=True, size=(1000, 750))
    return window


def get_layout1():
    layout = [
        [
            sg.Text(
                "1",
                text_color="black",
                font=("Arial", 50, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (50, 0)),
            )
        ],
        [
            sg.Text(
                "Googleアカウントの作成",
                text_color="pink",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (15, 80)),
            )
        ],
        [
            sg.Text(
                "次に，アテンダンを使用するための初期設定と準備を行います。\n\n保護者にメールを送信する際に使用するGoogleアカウントを作成してください。\nGoogleアカウントの作成には，以下の点を注意してください。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Text(
                "※ 作成するGoogleアカウントは，アテンダンのみで使用するアカウントにしてください。\n※ Googleアカウントは，教室固有のアカウントとして作成してください。複数教室で運用しないでください。",
                font=("Arial", 12),
                justification="left",
                expand_x=True,
                pad=((80, 0), (80, 0)),
            )
        ],
        [
            sg.Text(
                "上記を満たすGoogleアカウントが用意出来たら，次へをクリックして次の画面へ進んでください。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (80, 0)),
            )
        ],
        [
            sg.Button(
                "次へ",
                size=(10, 1),
                font=("Arial", 15),
                pad=((750, 0), (130, 0)),
                key="-next_to_2-",
                expand_x=True,
            )
        ],
    ]
    return layout


def get_layout2():
    layout = [
        [
            sg.Text(
                "2",
                text_color="black",
                font=("Arial", 50, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (50, 0)),
            )
        ],
        [
            sg.Text(
                "Googleアカウントのアプリパスワードの作成",
                text_color="pink",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (15, 80)),
            )
        ],
        [
            sg.Text(
                "作成したGoogleアカウントの「アプリパスワード」を作成してください。\nアプリパスワードとは，アプリに対して固有のパスワードを割り当てる機能です。作成方法は以下を参照してください。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Text(
                "アプリパスワードを作成する方法",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (20, 140)),
                enable_events=True,
                text_color="blue",
                key="-LINK-",
            )
        ],
        [
            sg.Text(
                "アプリパスワードを作成したら，次へをクリックして次の画面へ進んでください。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            )
        ],
        [
            sg.Button(
                "戻る",
                size=(10, 1),
                font=("Arial", 15),
                pad=((0, 0), (180, 0)),
                key="-back_to_1-",
                expand_x=True,
            ),
            sg.Button(
                "次へ",
                size=(10, 1),
                font=("Arial", 15),
                pad=((750, 0), (180, 0)),
                key="-next_to_3-",
                expand_x=True,
            ),
        ],
    ]
    return layout


def get_layout3():
    layout = [
        [
            sg.Text(
                "3",
                text_color="black",
                font=("Arial", 50, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (50, 0)),
            )
        ],
        [
            sg.Text(
                "Googleアカウント情報の入力",
                text_color="pink",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (15, 80)),
            )
        ],
        [
            sg.Text(
                "メールの送信に使用するGoogleアカウントのメールアドレスと，アプリパスワードを入力してください。\nアプリパスワードは，通常のGoogleアカウントのパスワードとは異なります。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 50)),
            )
        ],
        [
            sg.Text(
                "メールアドレス: ",
                font=("Arial", 12),
                justification="left",
                pad=((105, 10), (20, 30)),
            ),
            sg.InputText(
                font=("Arial", 12),
                size=(70, 1),
                pad=((0, 0), (20, 30)),
                key="-gmail-",
            ),
        ],
        [
            sg.Text(
                "アプリパスワード: ",
                font=("Arial", 12),
                justification="left",
                pad=((90, 10), (20, 140)),
            ),
            sg.InputText(
                font=("Arial", 12),
                size=(70, 1),
                pad=((0, 0), (20, 140)),
                key="-password-",
            ),
        ],
        [
            sg.Button(
                "戻る",
                size=(10, 1),
                font=("Arial", 15),
                pad=((0, 0), (80, 0)),
                key="-back_to_2-",
                expand_x=True,
            ),
            sg.Button(
                "次へ",
                size=(10, 1),
                font=("Arial", 15),
                pad=((750, 0), (80, 0)),
                key="-next_to_4-",
                expand_x=True,
            ),
        ],
    ]
    return layout


def get_layout4():
    layout = [
        [
            sg.Text(
                "4",
                text_color="black",
                font=("Arial", 50, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (50, 0)),
            )
        ],
        [
            sg.Text(
                "通知用メールアドレスの入力",
                text_color="pink",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (15, 80)),
            )
        ],
        [
            sg.Text(
                "アテンダンで何かエラーや通知すべき事案が発生した際に，通知するメールアドレスを設定します。\n導入する教室の管理者がメールをいつでも受信でき，受信に気づくようなアドレスを入力してください。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 50)),
            )
        ],
        [
            sg.Text(
                "メールアドレス: ",
                font=("Arial", 12),
                justification="left",
                pad=((105, 10), (20, 30)),
            ),
            sg.InputText(
                font=("Arial", 12),
                size=(70, 1),
                pad=((0, 0), (20, 30)),
                key="-emergency_mail-",
            ),
        ],
        [
            sg.Button(
                "戻る",
                size=(10, 1),
                font=("Arial", 15),
                pad=((0, 0), (240, 0)),
                key="-back_to_3-",
                expand_x=True,
            ),
            sg.Button(
                "次へ",
                size=(10, 1),
                font=("Arial", 15),
                pad=((750, 0), (240, 0)),
                key="-next_to_finish-",
                expand_x=True,
            ),
        ],
    ]
    return layout


def get_layout_finish():
    layout = [
        [
            sg.Text(
                "アテンダンを使用する準備ができました！",
                text_color="pink",
                font=("Arial", 30, "bold"),
                justification="center",
                expand_x=True,
                pad=((0, 0), (50, 80)),
            )
        ],
        [
            sg.Text(
                "アテンダンを使用するために必要な設定が完了しました。\n\n「アテンダンを起動」をクリックすると，アップデートが確認され，アテンダンが最新版に更新されます。",
                font=("Arial", 12),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 50)),
            )
        ],
        [
            sg.Button(
                "戻る",
                size=(10, 1),
                font=("Arial", 15),
                pad=((0, 0), (400, 0)),
                key="-back_to_4-",
                expand_x=True,
            ),
            sg.Button(
                "アテンダンを起動",
                size=(30, 1),
                font=("Arial", 15),
                pad=((680, 0), (400, 0)),
                key="-close-",
                expand_x=True,
            ),
        ],
    ]
    return layout


if __name__ == "__main__":
    pass
