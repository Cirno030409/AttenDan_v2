import PySimpleGUI as sg


def get_window():
    layout = [
        
        [
            sg.Text(
                "生徒を除名します。除名すると，データベースから生徒の情報がすべて消去されます。",
                font=("Arial", 10),
                justification="center",
                expand_x=True,
                tooltip="生徒の名前",
                pad=((0, 20), (0, 0)),
            ),
        ],
        [
            sg.Text(
                "確認のため，除名する生徒の氏名を入力してください:",
                font=("Arial", 10),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 20)),
            ),
        ],
        [
            sg.Text(
                "氏名:",
                font=("Arial", 15),
                justification="left",
                pad=((0, 0), (0, 0)),
                tooltip="生徒の名前",
            ),
            sg.InputText(
                size=(50, 1),
                font=("Arial", 15),
                key="-st_name-",
                pad=((0, 0), (0, 0)),
                tooltip="生徒の名前を入力します",
                expand_x=True,
            ),
        ],
        [
            sg.Button(
                "カードをタッチして除名",
                size=(50, 2),
                key="-remove-",
                tooltip="除名します。",
                expand_x=True,
                pad=((40, 20), (20, 0)),
            ),
        ],
        [
            sg.Button(
                "カードを使わずに除名...",
                size=(20, 2),
                key="-remove_without_card-",
                tooltip="カードを使わずに除名します。",
                expand_x=True,
                pad=((40, 20), (0, 0)),
            ),
        ]
    ]

    window = sg.Window(
        "生徒の除名",
        layout,
        finalize=True,
        # keep_on_top=True,
        # modal=True,
    )

    return window


if __name__ == "__main__":
    window = get_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
