import PySimpleGUI as sg

# 先程確認して決めたテーマカラーをsg.themeで設定
sg.theme("Purple")

# sg.Frameでフレームを定義
# フレーム1(中はからっぽ、フレームサイズだけ指定)
frame1 = sg.Frame("", [], size=(500, 700))  # 幅,高さ

# フレーム2(中はからっぽ、フレームサイズだけ指定)
frame2 = sg.Frame("", [], size=(400, 700))  # 幅,高さ

# 全体レイアウト
"""
レイアウトの中に記述する[]が「1行」を表している
今回はframe1と2を横に並べるので、同じ[]の中に記述する
"""
# フレーム2
frame2 = sg.Frame(
    "",
    [
        # テキストレイアウト
        [
            sg.Text("入退室ログ", font=("Arial", 15), expand_x=True, justification="center"),
        ],
    ],
    size=(400, 700),
)

layout = [
    # 以下[]で1行の扱いになる。カンマ区切りで横に部品を並べられる
    [frame1, frame2]
]

# GUIタイトルと全体レイアウトをのせたWindowを定義する。画面サイズは省略OK
# resizableでWindowサイズをマウスで変更できるようになる
window = sg.Window("ロボ団 出欠システム", layout, resizable=False)

# GUI表示実行部分
while True:
    # ウィンドウ表示
    event, values = window.read()

    # クローズボタンの処理
    if event is None:
        print("exit")
        break

window.close()
