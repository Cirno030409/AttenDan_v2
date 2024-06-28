import PySimpleGUI as sg
from functions import database_func as db


def get_window():
    st_list = db.execute_database("SELECT name FROM student WHERE id LIKE 'temp%'")
    st_list = [str(i+1) + ". " + st[0] for i, st in enumerate(st_list)]

    
    layout = [
        [
            sg.Text(
                "カードがまだ割り当てられていない生徒に対して，カードを割り当てます。\n割り当てられていない生徒は %d 名で，以下の通りです。" % len(st_list),
                font=("Arial", 10),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            ),
        ],
        [
            sg.Listbox(
                values=st_list,
                font=("Arial", 10),
                expand_x=True,
                size=(50, 30),
                pad=((0, 0), (10, 10)),
                key="-st_list-",
                enable_events=True,
            ),
        ],
        [
            sg.Text(
                "割り当てたい生徒をリストから選択し，カードを生徒に割り当て ボタンを押してください。",
                font=("Arial", 10),
                justification="center",
                expand_x=True,
                pad=((0, 0), (0, 0)),
            ),
        ],
        [
            sg.Button(
                "カードを生徒に割り当て",
                size=(50, 2),
                key="-allocate_cards_to_students-",
                tooltip="割り当てられていない生徒がいないため，登録できません" if len(st_list) == 0 else "選択した生徒にカードを割り当てます",
                expand_x=True,
                pad=((0, 0), (20, 20)),
                disabled=True if len(st_list) == 0 else False,
            ),
        ],
    ]   

    window = sg.Window(
        "生徒へのカードの割り当て",
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
