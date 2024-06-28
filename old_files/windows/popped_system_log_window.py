import PySimpleGUI as sg


def get_window():
    
    layout = [
        [
            [
                sg.Multiline(
                    font=("Arial", 10),
                    key="-log2-",
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
        ],
    ]

    window = sg.Window(
        "システム出力（ポップアウト）",
        layout,
        finalize=True,
        resizable=True,
        size=(1000, 800),
        # disable_close=True,
        enable_close_attempted_event=True,
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
