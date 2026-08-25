# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from reference/unix-linux/devices/input-event-codes-and-evdev
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def gen_architecture():
    path = os.path.join(IMG_DIR, 'evdev-architecture.svg')
    w, h = 820, 420
    frags = []
    
    # Layer 5: Userspace
    frags.append(fitbox(40, 40, 230, 48, "Wayland / Xorg Server\n(Display Server)", size=13, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(295, 40, 230, 48, "libinput / evdev App\n(Userspace Client)", size=13, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(550, 40, 230, 48, "uinput Daemon\n(Virtual Devices)", size=13, fill="#fdecea", stroke=POS))
    
    # Arrows 4 -> 5
    frags.append(arrow(155, 128, 155, 88, sw=1.5))
    frags.append(arrow(410, 128, 410, 88, sw=1.5))
    frags.append(arrow(665, 88, 665, 128, sw=1.5)) # uinput flows down
    
    # Layer 4: Event Handlers (VFS nodes)
    frags.append(fitbox(40, 128, 230, 52, "evdev (/dev/input/eventN)\nУніверсальний шар подій", size=13, fill="#e8f8f5", stroke=FIELD, bold=True))
    frags.append(fitbox(295, 128, 230, 52, "mousedev (/dev/input/mice)\nСумісність із PS/2 мишами", size=12, fill=FILL, stroke=LINE))
    frags.append(fitbox(550, 128, 230, 52, "uinput (/dev/uinput)\nЕмуляція пристроїв у ядрі", size=12, fill="#fdecea", stroke=POS))

    # Arrows 3 -> 4
    frags.append(arrow(410, 225, 155, 180, sw=1.5))
    frags.append(arrow(410, 225, 410, 180, sw=1.5))
    frags.append(arrow(665, 180, 410, 225, sw=1.5))

    # Layer 3: Input Core
    frags.append(fitbox(150, 225, 520, 45, "Input Core (drivers/input/input.c)\nМаршрутизатор подій та менеджер struct input_dev", size=13, fill="#f4f6f8", stroke=LINE, bold=True))

    # Arrows 2 -> 3
    frags.append(arrow(155, 310, 310, 270, sw=1.5))
    frags.append(arrow(410, 310, 410, 270, sw=1.5))
    frags.append(arrow(665, 310, 510, 270, sw=1.5))

    # Layer 2: Device Drivers
    frags.append(fitbox(40, 310, 230, 45, "usbhid / i2c-hid\nHID Драйвери", size=12, fill=FILL))
    frags.append(fitbox(295, 310, 230, 45, "psmouse / atkbd\nКласичні PS/2", size=12, fill=FILL))
    frags.append(fitbox(550, 310, 230, 45, "wacom / touch\nДрайвери планшетів", size=12, fill=FILL))

    # Arrows 1 -> 2
    frags.append(arrow(155, 375, 155, 355, sw=1.5))
    frags.append(arrow(410, 375, 410, 355, sw=1.5))
    frags.append(arrow(665, 375, 665, 355, sw=1.5))

    # Layer 1: Hardware
    frags.append(fitbox(40, 375, 230, 35, "USB Клавіатура / Миша", size=11, fill="#ffffff"))
    frags.append(fitbox(295, 375, 230, 35, "PS/2 Тачпад / Клавіатура", size=11, fill="#ffffff"))
    frags.append(fitbox(550, 375, 230, 35, "I2C Сенсорний екран", size=11, fill="#ffffff"))

    render(path, w, h, *frags, title="Архітектура підсистеми введення Linux (Input Subsystem)")

def gen_struct():
    path = os.path.join(IMG_DIR, 'input-event-struct.svg')
    w, h = 820, 340
    frags = []

    # Title label 64-bit
    frags.append(text(210, 50, "64-бітне ABI (24 байти / sizeof = 24)", size=14, bold=True, color=NEG))
    
    # 64-bit box layout
    # time: 16 bytes (0..15)
    frags.append(fitbox(30, 70, 190, 60, "time (16B)\ninput_event_sec (8B)\ninput_event_usec (8B)", size=11, fill="#eaf0fd", stroke=NEG))
    # type: 2 bytes (16..17)
    frags.append(fitbox(225, 70, 55, 60, "type\n(__u16)", size=11, fill="#e8f8f5", stroke=FIELD))
    # code: 2 bytes (18..19)
    frags.append(fitbox(285, 70, 55, 60, "code\n(__u16)", size=11, fill="#e8f8f5", stroke=FIELD))
    # value: 4 bytes (20..23)
    frags.append(fitbox(345, 70, 75, 60, "value\n(__s32)", size=11, fill="#fdecea", stroke=POS))

    # Offset markers 64-bit
    frags.append(text(30, 145, "0B", size=10, color=MUTED))
    frags.append(text(220, 145, "16B", size=10, color=MUTED))
    frags.append(text(280, 145, "18B", size=10, color=MUTED))
    frags.append(text(340, 145, "20B", size=10, color=MUTED))
    frags.append(text(420, 145, "24B", size=10, color=MUTED))

    # Title label 32-bit
    frags.append(text(620, 50, "32-бітне ABI (16 байтів / sizeof = 16)", size=14, bold=True, color=POS))

    # 32-bit box layout
    # time: 8 bytes (0..7)
    frags.append(fitbox(450, 70, 130, 60, "time (8B)\nsec (4B) / usec (4B)", size=11, fill="#eaf0fd", stroke=NEG))
    # type: 2 bytes (8..9)
    frags.append(fitbox(585, 70, 55, 60, "type\n(__u16)", size=11, fill="#e8f8f5", stroke=FIELD))
    # code: 2 bytes (10..11)
    frags.append(fitbox(645, 70, 55, 60, "code\n(__u16)", size=11, fill="#e8f8f5", stroke=FIELD))
    # value: 4 bytes (12..15)
    frags.append(fitbox(705, 70, 75, 60, "value\n(__s32)", size=11, fill="#fdecea", stroke=POS))

    # Offset markers 32-bit
    frags.append(text(450, 145, "0B", size=10, color=MUTED))
    frags.append(text(580, 145, "8B", size=10, color=MUTED))
    frags.append(text(640, 145, "10B", size=10, color=MUTED))
    frags.append(text(700, 145, "12B", size=10, color=MUTED))
    frags.append(text(780, 145, "16B", size=10, color=MUTED))

    # Explanation text boxes
    frags.append(fitbox(30, 175, 390, 130, 
                        "Поля структури struct input_event:\n"
                        "• time: позначка часу (input_event_sec / input_event_usec)\n"
                        "• type: тип події (EV_KEY=1, EV_REL=2, EV_ABS=3, EV_SYN=0)\n"
                        "• code: код органу (KEY_A=30, REL_X=0, ABS_X=0)\n"
                        "• value: значення (1=Down, 0=Up, 2=Repeat, delta/pos)", 
                        size=11, fill="#f4f6f8", stroke=LINE))

    frags.append(fitbox(440, 175, 350, 130,
                        "Особливості сумісності та Y2038:\n"
                        "• З ядра Linux 4.16: поля input_event_sec / input_event_usec\n"
                        "• Читання read() повертає ціле число структур\n"
                        "• Часткове читання (наприклад, 10B) -> повертає EINVAL\n"
                        "• 32-бітні програми на 64-бітному ядрі: шар CONFIG_COMPAT",
                        size=11, fill="#f4f6f8", stroke=LINE))

    render(path, w, h, *frags, title="Бінарне вирівнювання структури struct input_event")

def gen_event_flow():
    path = os.path.join(IMG_DIR, 'evdev-event-flow.svg')
    w, h = 840, 360
    frags = []

    # Timeline horizontal axis
    frags.append(line(50, 280, 790, 280, color=LINE, sw=2))
    frags.append(arrow(780, 280, 810, 280, color=LINE, sw=2))
    frags.append(text(810, 300, "Час (t)", size=12, bold=True))

    # Group 1: Key press 'A'
    frags.append(fitbox(60, 60, 160, 40, "EV_KEY: KEY_A\nvalue = 1 (Down)", size=11, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(60, 115, 160, 40, "EV_MSC: MSC_SCAN\nvalue = 0x1E (Scan)", size=11, fill=FILL, stroke=LINE))
    frags.append(fitbox(60, 170, 160, 45, "EV_SYN: SYN_REPORT\nvalue = 0 (Flush)", size=11, fill="#fdecea", stroke=POS, bold=True))
    frags.append(line(140, 215, 140, 280, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(140, 295, "t1: Натиск", size=11, color=INK))

    # Group 2: Key repeat
    frags.append(fitbox(260, 60, 160, 40, "EV_KEY: KEY_A\nvalue = 2 (Repeat)", size=11, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(260, 170, 160, 45, "EV_SYN: SYN_REPORT\nvalue = 0 (Flush)", size=11, fill="#fdecea", stroke=POS, bold=True))
    frags.append(line(340, 215, 340, 280, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(340, 295, "t2: Автоповтор", size=11, color=INK))

    # Group 3: Mouse Movement
    frags.append(fitbox(460, 60, 160, 40, "EV_REL: REL_X\nvalue = +12 (dx)", size=11, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(460, 115, 160, 40, "EV_REL: REL_Y\nvalue = -5 (dy)", size=11, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(460, 170, 160, 45, "EV_SYN: SYN_REPORT\nvalue = 0 (Flush)", size=11, fill="#fdecea", stroke=POS, bold=True))
    frags.append(line(540, 215, 540, 280, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(540, 295, "t3: Рух миші", size=11, color=INK))

    # Group 4: Key release 'A'
    frags.append(fitbox(660, 60, 160, 40, "EV_KEY: KEY_A\nvalue = 0 (Up)", size=11, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(660, 170, 160, 45, "EV_SYN: SYN_REPORT\nvalue = 0 (Flush)", size=11, fill="#fdecea", stroke=POS, bold=True))
    frags.append(line(740, 215, 740, 280, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(740, 295, "t4: Відпуск", size=11, color=INK))

    # Explanatory banner
    frags.append(fitbox(150, 320, 540, 30, "Атомарний кадр (Frame): усі події до SYN_REPORT обробляються клієнтом як єдиний пакет", size=11, fill="#ffffff", stroke=LINE))

    render(path, w, h, *frags, title="Групування атомарних кадрів у evdev за допомогою EV_SYN (SYN_REPORT)")

def gen_uinput():
    path = os.path.join(IMG_DIR, 'uinput-flow.svg')
    w, h = 800, 380
    frags = []

    # Userspace app
    frags.append(fitbox(40, 60, 220, 70, "Простір користувача\n(Демон / Емулятор / Macro)\n`fd = open(\"/dev/uinput\")`", size=12, fill="#eaf0fd", stroke=NEG, bold=True))

    # Arrows 1 -> 2
    frags.append(arrow(260, 80, 330, 80, sw=1.5))
    frags.append(text(295, 70, "ioctl()", size=11, color=INK))
    frags.append(text(295, 95, "write()", size=11, color=INK))

    # Kernel uinput module
    frags.append(fitbox(330, 60, 240, 70, "Модуль ядра uinput\n(drivers/input/misc/uinput.c)\n`UI_DEV_CREATE`", size=12, fill="#fdecea", stroke=POS, bold=True))

    # Arrows 2 -> 3
    frags.append(arrow(570, 95, 640, 95, sw=1.5))
    frags.append(text(605, 85, "Реєстрація", size=11, color=INK))

    # Input Core
    frags.append(fitbox(640, 60, 140, 70, "Input Core\n`struct input_dev`", size=12, fill=FILL, stroke=LINE))

    # Arrow 3 -> 4
    frags.append(arrow(710, 130, 710, 220, sw=1.5))

    # Evdev node
    frags.append(fitbox(520, 220, 260, 60, "Новий вузол пристрою evdev\n`/dev/input/eventN`\n(Створений для віртуального пристрою)", size=12, fill="#e8f8f5", stroke=FIELD, bold=True))

    # Arrow 4 -> 5
    frags.append(arrow(520, 250, 260, 250, sw=1.5))
    frags.append(text(390, 240, "Зчитування подій read()", size=11, color=INK))

    # Display server
    frags.append(fitbox(40, 220, 220, 60, "Клієнтський процес\n(Wayland / X11 / libinput)\nОтримує синтетичні події", size=12, fill="#eaf0fd", stroke=NEG))

    # Bottom workflow description box
    frags.append(fitbox(40, 305, 740, 50, 
                        "Етапи створення віртуального пристрою uinput:\n"
                        "1. UI_SET_EVBIT / UI_SET_KEYBIT (оголошення capabilities) → 2. ioctl(UI_DEV_SETUP) → 3. UI_DEV_CREATE → 4. write(input_event)",
                        size=11, fill="#f4f6f8", stroke=LINE))

    render(path, w, h, *frags, title="Схема роботи та інжекції подій через /dev/uinput")

if __name__ == '__main__':
    gen_architecture()
    gen_struct()
    gen_event_flow()
    gen_uinput()
    print("SVG diagrams generated successfully.")
