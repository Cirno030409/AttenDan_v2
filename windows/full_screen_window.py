import PySimpleGUI as sg


def get_window():
    sg.theme("DefaultNoMoreNagging")
    
    layout = [
        [
            sg.Text(
                "こんにちは！",
                font=("Arial", 100),
                justification="center",
                expand_x=True,
                expand_y=True,
                pad=((0, 0), (50, 0)),
                key="-greeting-",  # 挨拶
            ),
        ],
        [
            sg.Text(
                "カードをタッチしてね",
                font=("Arial", 100),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 50)),
            ),
        ],
    ]

    window = sg.Window(
        "生徒の新規登録",
        layout,
        finalize=True,
        no_titlebar=True,
        size=sg.Window.get_screen_size(),
    )

    return window

if __name__ == "__main__":
    window = get_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
