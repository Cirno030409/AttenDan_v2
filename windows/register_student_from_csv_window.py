import PySimpleGUI as sg


def get_window():
    
    layout = [
        
        [
            sg.Text(
                "CSVファイルから生徒の情報を読み込んで生徒を登録します。\nCSVファイルは以下のような形式である必要があります。\n\n\n生徒の氏名1,年齢(数字),性別(男 or 女),保護者名,保護者のメールアドレス\n生徒の氏名2,年齢(数字),性別(男 or 女),保護者名,保護者のメールアドレス\n.\n.\n.\n\n\nなお，性別は「男」または「女」のいずれかである必要があります。また，年齢は数字である必要があります。\n\n",
                font=("Arial", 10),
                justification="center",
                expand_x=True,
                tooltip="生徒の名前",
                pad=((0, 20), (0, 0)),
            ),
        ],
        [
            sg.Text(
                "CSVファイル:なし",
                font=("Arial", 15),
                justification="center",
                expand_x=True,
                tooltip="生徒の名前",
                key="-csv_file_path-",
                pad=((0, 20), (0, 0)),
            ),
        ],
        [
            sg.Button(
                "CSVファイルを開く",
                size=(20, 1),
                key="-load_csv-",
                tooltip="読み込むCSVファイルを選択します",
                expand_x=True,
                pad=((150, 150), (0, 0)),
            ),
        ],
        [
            sg.Button(
                "CSVファイルから生徒を登録",
                size=(50, 2),
                key="-do_register_from_csv-",
                tooltip="読み込むCSVファイルを選択します",
                expand_x=True,
                pad=((20, 20), (30, 0)),
                disabled=True,
            ),
        ],
    ]

    window = sg.Window(
        "CSVファイルから生徒を登録",
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
