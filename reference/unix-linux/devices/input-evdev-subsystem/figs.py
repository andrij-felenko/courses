import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import render, rect, text, arrow, mtext, line, circle, textbox

IMG = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG, exist_ok=True)

def draw_subsystem():
    frags = []

    # Canvas 800 x 480
    # Layer 4: Userspace (Top)
    frags.append(rect(40, 20, 720, 70, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(400, 42, "Простір користувача (Userspace)", size=15, bold=True, color="#1e293b"))
    frags.append(text(160, 68, "Wayland / Xorg", size=13, color="#334155"))
    frags.append(text(400, 68, "libinput", size=13, bold=True, color="#0f766e"))
    frags.append(text(640, 68, "evtest / uinput клієнти", size=13, color="#334155"))

    # Interfaces / Device Nodes
    frags.append(rect(100, 125, 160, 36, fill="#ccfbf1", stroke="#0d9488", sw=1.5, rx=4))
    frags.append(text(180, 148, "/dev/input/eventX", size=13, bold=True, color="#0f766e"))

    frags.append(rect(320, 125, 160, 36, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=4))
    frags.append(text(400, 148, "/dev/input/mice", size=13, color="#3730a3"))

    frags.append(rect(540, 125, 160, 36, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(620, 148, "/dev/input/jsX", size=13, color="#92400e"))

    # Layer 3: Event Handlers (evdev, mousedev, joydev)
    frags.append(rect(40, 195, 720, 75, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(400, 217, "Обробники подій (Event Handlers)", size=15, bold=True, color="#14532d"))

    frags.append(rect(80, 230, 200, 32, fill="#dcfce7", stroke="#15803d", sw=1.2, rx=4))
    frags.append(text(180, 251, "evdev (універсальний)", size=13, bold=True, color="#166534"))

    frags.append(rect(300, 230, 200, 32, fill="#f1f5f9", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(400, 251, "mousedev (PS/2 емуляція)", size=13, color="#334155"))

    frags.append(rect(520, 230, 200, 32, fill="#f1f5f9", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(620, 251, "joydev (старий джойстик)", size=13, color="#334155"))

    # Layer 2: Input Core
    frags.append(rect(40, 305, 720, 60, fill="#ffedd5", stroke="#ea580c", sw=2, rx=8))
    frags.append(text(400, 332, "Ядро підсистеми введення: Input Core (drivers/input/input.c)", size=15, bold=True, color="#9a3412"))
    frags.append(text(400, 353, "Маршрутизація подій, input_match_device(), bitmask matching (evbit, keybit)", size=12, color="#c2410c"))

    # Layer 1: Drivers & Hardware (Bottom)
    frags.append(rect(40, 400, 720, 60, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=8))
    frags.append(text(400, 423, "Драйвери та обладнання (Device Drivers & Hardware)", size=14, bold=True, color="#1e293b"))
    frags.append(text(400, 445, "usbhid, i2c-hid, psmouse, hid-multitouch → USB, I2C, PS/2, Bluetooth", size=12, color="#475569"))

    # Connective Arrows
    # Drivers -> Input Core
    frags.append(arrow(400, 400, 400, 365, color="#ea580c", sw=2))

    # Input Core -> Event Handlers
    frags.append(arrow(180, 305, 180, 262, color="#16a34a", sw=1.8))
    frags.append(arrow(400, 305, 400, 262, color="#475569", sw=1.5))
    frags.append(arrow(620, 305, 620, 262, color="#475569", sw=1.5))

    # Event Handlers -> Dev Nodes
    frags.append(arrow(180, 230, 180, 161, color="#0d9488", sw=1.8))
    frags.append(arrow(400, 230, 400, 161, color="#4338ca", sw=1.5))
    frags.append(arrow(620, 230, 620, 161, color="#d97706", sw=1.5))

    # Dev Nodes -> Userspace
    frags.append(arrow(180, 125, 180, 90, color="#0d9488", sw=1.8))
    frags.append(arrow(400, 125, 400, 90, color="#4338ca", sw=1.5))
    frags.append(arrow(620, 125, 620, 90, color="#d97706", sw=1.5))

    render(os.path.join(IMG, 'input-subsystem.svg'), 800, 480, *frags)

def draw_event_flow():
    frags = []

    # Canvas 800 x 360
    # Left: Event source (Input Driver)
    frags.append(rect(30, 40, 160, 280, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(110, 70, "Драйвер пристрою", size=14, bold=True, color="#92400e"))
    frags.append(text(110, 95, "(напр. usbhid)", size=12, color="#b45309"))
    frags.append(text(110, 140, "input_event()", size=13, bold=True, color="#78350f"))
    frags.append(text(110, 165, "1. EV_REL REL_X", size=11, color="#451a03"))
    frags.append(text(110, 185, "2. EV_REL REL_Y", size=11, color="#451a03"))
    frags.append(text(110, 205, "3. EV_SYN SYN_REPORT", size=11, bold=True, color="#b45309"))
    frags.append(text(110, 250, "Потік сирих подій", size=12, italic=True, color="#78350f"))

    # Middle: Kernel evdev client Ring Buffer (struct evdev_client)
    frags.append(rect(240, 40, 320, 280, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(400, 70, "Кільцевий буфер evdev (struct evdev_client)", size=14, bold=True, color="#14532d"))
    frags.append(text(400, 95, "Розмір: client->bufsize (напр. 64 / 128 подій)", size=12, color="#15803d"))

    # Ring buffer slots
    colors = ["#dcfce7", "#dcfce7", "#dcfce7", "#fef2f2", "#f1f5f9", "#f1f5f9"]
    labels = ["EV_REL REL_X", "EV_REL REL_Y", "EV_SYN (COMMIT)", "SYN_DROPPED!", "Вільна комірка", "Вільна комірка"]
    for i in range(6):
        y_pos = 120 + i * 30
        frags.append(rect(260, y_pos, 280, 26, fill=colors[i], stroke="#86efac" if i < 3 else "#fca5a5" if i == 3 else "#cbd5e1", sw=1, rx=4))
        frags.append(text(400, y_pos + 18, labels[i], size=12, bold=(i == 2 or i == 3), color="#166534" if i < 3 else "#991b1b" if i == 3 else "#64748b"))

    frags.append(text(400, 308, "SYN_DROPPED надсилається при переповненні буфера", size=11, italic=True, color="#dc2626"))

    # Right: Userspace Reader (libinput / Application)
    frags.append(rect(610, 40, 160, 280, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=8))
    frags.append(text(690, 70, "Userspace", size=14, bold=True, color="#3730a3"))
    frags.append(text(690, 95, "libinput / evtest", size=12, color="#4338ca"))

    frags.append(text(690, 140, "read() / epoll()", size=13, bold=True, color="#1e1b4b"))
    frags.append(text(690, 170, "Накопичення до", size=12, color="#312e81"))
    frags.append(text(690, 190, "SYN_REPORT", size=12, bold=True, color="#1e1b4b"))
    frags.append(text(690, 230, "Оновлення стану", size=12, color="#312e81"))
    frags.append(text(690, 250, "курсора / фрейму", size=12, color="#312e81"))

    # Arrows
    frags.append(arrow(190, 180, 240, 180, color="#d97706", sw=2))
    frags.append(arrow(560, 180, 610, 180, color="#16a34a", sw=2))

    render(os.path.join(IMG, 'evdev-event-flow.svg'), 800, 360, *frags)

if __name__ == '__main__':
    draw_subsystem()
    draw_event_flow()
