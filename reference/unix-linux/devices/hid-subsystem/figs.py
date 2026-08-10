import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import textbox, arrow, render, FIELD

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def draw_flow():
    # boxes
    b1, w1, h1 = textbox(150, 100, "USB HID Report\n(Байт-масив)", pad=15)
    b2, w2, h2 = textbox(400, 100, "HID Parser\n(hid-core)", pad=15)
    b3, w3, h3 = textbox(650, 50, "input subsystem\n/dev/input/eventX", pad=15)
    b4, w4, h4 = textbox(650, 150, "hidraw\n/dev/hidrawX", pad=15, fill=FIELD, color="#fff", bold=True)
    
    # arrows
    arr1 = arrow(150 + w1/2 + 2, 100, 400 - w2/2 - 2, 100)
    arr2 = arrow(400 + w2/2 + 2, 100 - 15, 650 - w3/2 - 2, 50)
    arr3 = arrow(400 + w2/2 + 2, 100 + 15, 650 - w4/2 - 2, 150)

    render(os.path.join(IMG, 'hid-flow.svg'), 800, 200, b1, b2, b3, b4, arr1, arr2, arr3)

if __name__ == '__main__':
    draw_flow()
