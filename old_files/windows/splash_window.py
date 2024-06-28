import PySimpleGUI as sg
from PIL import Image

import config.values as const


def get_window():
    # Get the size of the image
    image = Image.open(const.SPLASH_IMAGE_PATH)
    width, height = image.size

    layout = [
        [
            sg.Image(
                filename=const.SPLASH_IMAGE_PATH,
                size=(width, height),
                pad=((0, 0), (0, 0)),
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]

    window = sg.Window(
        "splash screen",
        layout,
        no_titlebar=True,
        keep_on_top=True,
        size=(width, height),
        margins=(0, 0),
    )

    return window


if __name__ == "__main__":  # テスト用
    window = get_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
