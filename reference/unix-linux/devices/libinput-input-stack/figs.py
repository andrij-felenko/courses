# -*- coding: utf-8 -*-
"""Фігури до теми «libinput: спільний шар обробки вводу для Wayland і X»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_input_stack_architecture():
    """Стек вводу Linux: від фізичного заліза до клієнтів Wayland та X11."""
    W, H = 1140, 520
    f = []

    f.append(text(40, 35, "Архітектура сучасного стека вводу Linux",
                  size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 55, "Єдиний шар libinput обслуговує і нативні композитори Wayland, і Xorg через уніфікований драйвер",
                  size=12, color=MUTED, anchor="start"))

    # Рівень 1: Апаратні пристрої та драйвери ядра
    f.append(text(40, 85, "АПАРАТНІ ПРИСТРОЇ ТА ДРАЙВЕРИ ЯДРА", size=11, color=MUTED, anchor="start", bold=True))
    hw_boxes = [
        ("USB / Bluetooth миша\nhid-generic", 40, 200),
        ("Тачпад ноутбука (I2C / RMI4)\ni2c-hid / rmi4_core", 260, 260),
        ("Графічний планшет / стилус\nwacom / hid-uclogic", 540, 260),
        ("Вбудований тачскрин\nhid-multitouch / goodix", 820, 280),
    ]
    for label, x, w in hw_boxes:
        f.append(fitbox(x, 100, w, 52, label, size=12, fill="#eaf7ee", stroke=FIELD))

    # Рівень 2: evdev підсистема ядра
    f.append(fitbox(40, 175, 1060, 48,
                    "Ядро Linux: підсистема введення evdev (/dev/input/event0 … eventN)\n"
                    "Уніфікований двійковий потік структур struct input_event (EV_REL, EV_ABS, EV_KEY, EV_SYN)",
                    size=13, fill=FILL, stroke=LINE))

    for label, x, w in hw_boxes:
        cx = x + w / 2
        f.append(arrow(cx, 153, cx, 173))

    # Рівень 3: libevdev + udev hwdb
    f.append(fitbox(40, 245, 1060, 44,
                    "libevdev (кешування бітових масок, розбір ioctl, захист від SYN_DROPPED) + udev hwdb (коригування осей)",
                    size=12, fill="#f4f6f8", stroke=LINE))
    f.append(arrow(570, 224, 570, 243))

    # Рівень 4: libinput
    f.append(fitbox(40, 310, 1060, 68,
                    "libinput (бібліотека простору користувача)\n"
                    "Балістичне прискорення курсора · Жести (Pinch, Swipe) · Tap-to-click · Клікпади (Clickfinger / Softbuttons)\n"
                    "Фільтрація долоні (Palm Detection) · Блокування при наборі (DWT) · Калібрування планшетів і матриць",
                    size=13, fill="#eaf0fd", stroke=NEG, bold=False))
    f.append(arrow(570, 290, 570, 308))

    # Рівень 5: Споживачі (Wayland композитори та Xorg)
    f.append(text(40, 400, "СПОЖИВАЧІ В ПРОСТОРІ КОРИСТУВАЧА", size=11, color=MUTED, anchor="start", bold=True))

    # Wayland гілка
    f.append(fitbox(40, 415, 620, 50,
                    "Композитор Wayland (Mutter / KWin / wlroots / Sway / Weston)\n"
                    "Пряма інтеграція через libinput API, власна обробка фокусу й розсилка клієнтам",
                    size=12, fill="#fdf3e7", stroke="#d35400"))
    f.append(arrow(350, 379, 350, 413))

    # Xorg гілка
    f.append(fitbox(700, 415, 400, 50,
                    "Xorg Server + xf86-input-libinput\n"
                    "Уніфікований драйвер трансляції подій libinput у X11",
                    size=12, fill="#fdf3e7", stroke="#d35400"))
    f.append(arrow(900, 379, 900, 413))

    # Рівень 6: Клієнти
    f.append(fitbox(40, 480, 400, 34, "Клієнти Wayland (GTK4, Qt6, Wayland-програми)", size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(470, 480, 190, 34, "Xwayland (міст X11)", size=12, fill=FILL, stroke=LINE))
    f.append(fitbox(700, 480, 400, 34, "Традиційні клієнти X11 (програми під Xlib / XCB)", size=12, fill=FILL, stroke=LINE))

    f.append(arrow(240, 466, 240, 478))
    f.append(arrow(565, 466, 565, 478))
    f.append(arrow(900, 466, 900, 478))

    render(os.path.join(IMG, 'input-stack-architecture.svg'), W, H, *f)


def fig_libinput_processing_pipeline():
    """Конвеєр внутрішньої обробки подій всередині libinput."""
    W, H = 1140, 460
    f = []

    f.append(text(40, 35, "Внутрішній конвеєр фільтрації та обробки подій у libinput",
                  size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 55, "Від сирих імпульсів ядра до високорівневих семантичних жестів і нормалізованих координат",
                  size=12, color=MUTED, anchor="start"))

    cols = [
        (40, 220, "1. Зчитування та база вад\n(Ingestion & Quirks)",
         "Зчитування з fd evdev\nВиправлення залізяччя\nчерез .quirks та hwdb\n(роздільність, шуми, осі)",
         "#eaf0fd", NEG),
        (280, 220, "2. Нормалізація координат\n(Normalization)",
         "Переведення відліків\nу міліметри (DPI-scaling)\nВідстеження слотів MT-B\nУсунення тремтіння (jitter)",
         "#eaf7ee", FIELD),
        (520, 340, "3. Спеціалізовані автомати станів\n(State Engines)",
         "• Тачпад: Tap, DWT, Clickpad, Palm, Скрол\n• Жести: Pinch (zoom/rotate), 3-4F Swipe\n• Вказівник: Адаптивне прискорення\n• Планшет: Натиск, нахил, дистанція, пера\n• Тачскрин: Афінна матриця калібрування",
         "#fdf3e7", "#d35400"),
        (880, 220, "4. Диспетчеризація подій\n(Public API Event Queue)",
         "LIBINPUT_EVENT_POINTER_*\nLIBINPUT_EVENT_GESTURE_*\nLIBINPUT_EVENT_TOUCH_*\nLIBINPUT_EVENT_TABLET_*",
         "#fdecea", POS),
    ]

    for x, w, title_str, body_str, fill_c, stroke_c in cols:
        f.append(fitbox(x, 90, w, 44, title_str, size=12, fill=fill_c, stroke=stroke_c, bold=True))
        f.append(fitbox(x, 142, w, 220, body_str, size=12, fill=FILL, stroke=LINE))

    f.append(arrow(262, 230, 278, 230))
    f.append(arrow(502, 230, 518, 230))
    f.append(arrow(862, 230, 878, 230))

    # Нижня плашка зворотного зв'язку / конфігурації
    f.append(fitbox(40, 385, 1060, 54,
                    "Динамічна конфігурація та блокування (DWT interlock):\n"
                    "Події клавіатури переводять тачпад у стан очікування; налаштування tap/scroll змінюють логіку автоматів без перезапуску",
                    size=12, fill="#f4f6f8", stroke=LINE))

    render(os.path.join(IMG, 'libinput-pipeline.svg'), W, H, *f)


def fig_touchpad_gesture_state_machine():
    """Автомат розпізнавання жестів та захисту від долоні (Palm Detection, Tap, Swipe)."""
    W, H = 1140, 480
    f = []

    f.append(text(40, 35, "Життєвий цикл контакту на тачпаді: від дотику до жесту",
                  size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 55, "Як libinput розрізняє випадковий дотик долонею, легкий тап, скрол двома пальцями та масштаб",
                  size=12, color=MUTED, anchor="start"))

    # Початковий стан
    f.append(fitbox(40, 95, 230, 60, "Палець торкнувся поверхні\n(TOUCH_DOWN / контакт у слоті)", size=12, fill="#eaf0fd", stroke=NEG, bold=True))

    # Перевірка на долоню
    f.append(fitbox(320, 95, 260, 60, "Перевірка Palm Detection:\nКрай тачпада / велика площа / DWT?", size=12, fill="#fdf3e7", stroke="#d35400"))
    f.append(arrow(272, 125, 318, 125))

    # Гілка відкидання долоні
    f.append(fitbox(640, 95, 460, 60, "Ігнорування контакту (PALM_STATE)\nПодії руху блокуються, тап пригнічується", size=12, fill="#fdecea", stroke=POS))
    f.append(arrow(582, 125, 638, 125))
    f.append(text(610, 115, "Так", size=11, color=POS, bold=True))

    # Гілка валідного контакту
    f.append(text(465, 175, "Ні (валідний ввід)", size=11, color=FIELD, bold=True))
    f.append(arrow(450, 157, 450, 195))

    f.append(fitbox(320, 197, 260, 50, "Оцінка кількості пальців\nта векторів руху (Δt, Δx, Δy)", size=12, fill="#eaf7ee", stroke=FIELD, bold=True))

    # 4 результати
    branches = [
        (40, 310, 240, 120, "1 палець\nЧас < 180мс, рух < 3мм:\n→ Tap-to-Click (LMB)\nРух триває:\n→ Рух вказівника (Pointer Motion)", "#eaf0fd", NEG),
        (310, 310, 240, 120, "2 пальці\nСпільний вектор:\n→ Прокрутка (Scroll 2-finger)\nПротилежні вектори / кут:\n→ Pinch / Rotate (масштаб/поворот)", "#eaf7ee", FIELD),
        (580, 310, 240, 120, "3 або 4 пальці\nСинхронний рух:\n→ Swipe-жест (перемикання робочих столів / огляд вікон)", "#fdf3e7", "#d35400"),
        (850, 310, 250, 120, "Фізичний клік (Clickpad)\nПеревірка зони кнопки:\n• Нижня права = RMB\n• Нижня середня = MMB\n• Clickfinger: 1F=LMB, 2F=RMB, 3F=MMB", "#f4f6f8", LINE),
    ]

    for x, y, w, h, text_str, fill_c, stroke_c in branches:
        f.append(fitbox(x, y, w, h, text_str, size=11, fill=fill_c, stroke=stroke_c))
        cx = x + w / 2
        f.append(arrow(450, 249, cx, 308))

    render(os.path.join(IMG, 'touchpad-state-machine.svg'), W, H, *f)


if __name__ == '__main__':
    fig_input_stack_architecture()
    fig_libinput_processing_pipeline()
    fig_touchpad_gesture_state_machine()
    print('ok')
