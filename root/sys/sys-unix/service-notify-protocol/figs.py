# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"

def fig_notify_socket():
    W, H = 1040, 540
    p = []

    # Title
    p.append(text(W / 2, 35, "Протокол NOTIFY_SOCKET: передача стану та автентифікація в systemd", size=16, bold=True))

    # Left box: systemd (PID 1)
    lx, ly, lw, lh = 40, 65, 430, 450
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=NEG, sw=1.5, rx=10))
    p.append(text(lx + lw / 2, 92, "systemd (PID 1 / системний менеджер)", size=15, bold=True, color=NEG))

    p.append(fitbox(lx + 20, 115, 390, 65, "UNIX Datagram Socket\n/run/systemd/notify (або @abstract)", size=13, fill=BLUE_FILL, stroke=MUTED))
    p.append(fitbox(lx + 20, 195, 390, 95, "Перевірка відправника (Kernel ucred):\n1. getsockopt(SO_PEERCRED) -> PID 4120\n2. Читання /proc/4120/cgroup\n3. Перевірка політики NotifyAccess=main", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(lx + 20, 305, 390, 90, "Автомат станів юніта:\nactivating -> active (при READY=1)\nОновлення Status Text (при STATUS=...)\nСкидання Watchdog Timer (при WATCHDOG=1)", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(lx + 20, 410, 390, 85, "Розблокування залежностей:\nЗапуск служб, що чекають на After=myservice.service", size=12, fill=GREY_FILL, stroke=MUTED))

    # Right box: Service process
    rx, ry, rw, rh = 570, 65, 430, 450
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=POS, sw=1.5, rx=10))
    p.append(text(rx + rw / 2, 92, "Служба користувача (PID 4120)", size=15, bold=True, color=POS))

    p.append(fitbox(rx + 20, 115, 390, 65, "Змінні оточення при старті:\nNOTIFY_SOCKET=/run/systemd/notify\nWATCHDOG_USEC=30000000", size=13, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(rx + 20, 195, 390, 95, "Етап ініціалізації:\n- Завантаження конфігурації\n- Відкриття сокетів/БД\n- Підготовка ресурсів", size=13, fill=GREY_FILL, stroke=MUTED))
    p.append(fitbox(rx + 20, 305, 390, 90, "Головний цикл подій (Main Event Loop):\nРегулярна обробка запитів\n+ Таймер періодичного надсилання WATCHDOG=1", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(rx + 20, 410, 390, 85, "Надсилання FD / перезавантаження:\nFDSTORE=1 + SCM_RIGHTS при оновленні\nRELOADING=1 при SIGHUP", size=12, fill=BLUE_FILL, stroke=MUTED))

    # Arrows between boxes
    p.append(arrow(rx, 240, lx + lw, 150, color=NEG))
    p.append(text((lx + lw + rx) / 2, 185, "READY=1\nSTATUS=Ready", size=11, color=NEG, bold=True))

    p.append(arrow(rx, 350, lx + lw, 350, color=FIELD))
    p.append(text((lx + lw + rx) / 2, 335, "WATCHDOG=1 (кожні N/2 сек)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'notify-socket.svg'), W, H, *p)

if __name__ == "__main__":
    fig_notify_socket()
    print("figs.py finished successfully")
