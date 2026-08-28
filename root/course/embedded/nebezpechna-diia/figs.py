# -*- coding: utf-8 -*-
"""Фігури для статті nebezpechna-diia («Небезпечна дія: підтвердження, дві дії, відлік»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. safety-ui-patterns: Порівняння 4 архітектурних патернів підтвердження ───
def fig_safety_ui_patterns():
    W, H = 880, 480
    p = []

    col_w = 195
    pad_x = 20
    top_y = 60
    col_h = 390

    # 4 колонки
    cols = [
        {
            "x": pad_x,
            "title": "1. Модальне OK / Cancel",
            "badge": "НЕБЕЗПЕЧНО",
            "badge_color": POS,
            "desc": "Класичне діалогове вікно.\nВикликає звикання (habituation)\nта автоматичний рефлекс кліку.",
            "ui_bg": "#fff5f5",
            "ui_border": POS,
            "items": [
                ("Дія:", "Клік на «Disarm»"),
                ("Бар'єр:", "Вікно: «Підтвердити?»"),
                ("Помилка:", "М'язова пам'ять тисне OK"),
                ("Результат:", "Аварія при стресі")
            ]
        },
        {
            "x": pad_x + col_w + 15,
            "title": "2. Дві дії (Arm-then-Fire)",
            "badge": "НАДІЙНО",
            "badge_color": FIELD,
            "desc": "Розділення у просторі й часі:\nтумблер зведення (Arm) +\nокрема кнопка спуску (Fire).",
            "ui_bg": "#f4faf6",
            "ui_border": FIELD,
            "items": [
                ("Крок 1:", "Підйом ковпачка / тумблер"),
                ("Крок 2:", "Таймер зведення (5..10 с)"),
                ("Крок 3:", "Натискання кнопки спуску"),
                ("Скидання:", "Авто-скид при бездіяльності")
            ]
        },
        {
            "x": pad_x + (col_w + 15) * 2,
            "title": "3. Затискання (Hold 3s)",
            "badge": "ДЛЯ ЕКРАНІВ",
            "badge_color": NEG,
            "desc": "Неперервне утримання 3 с.\nКруговий прогрес, цокання.\nВідпускання — миттєвий скид.",
            "ui_bg": "#f5f8ff",
            "ui_border": NEG,
            "items": [
                ("Дія:", "Натиснути й утримувати"),
                ("Зворотний зв'язок:", "Анімація заповнення кола"),
                ("Скидання:", "Відрив пальця = abort"),
                ("Результат:", "Випадковий дотик виключено")
            ]
        },
        {
            "x": pad_x + (col_w + 15) * 3,
            "title": "4. Свайп (Slide-to-Confirm)",
            "badge": "ДЛЯ ТАЧПАДІВ",
            "badge_color": "#d35400",
            "desc": "Проведення повзунка по треку\nна 70% ширини екрана.\nЗахист від фантомних крапель.",
            "ui_bg": "#fffbf5",
            "ui_border": "#d35400",
            "items": [
                ("Траєкторія:", "Тягнути слайдер управо"),
                ("Геометрія:", "Довгий шлях (≥ 200 px)"),
                ("Фізика:", "Повернення пружиною назад"),
                ("Результат:", "Краплі/вібрація не зсунуть")
            ]
        }
    ]

    for c in cols:
        cx = c["x"]
        p.append(rect(cx, top_y, col_w, col_h, fill=c["ui_bg"], stroke=c["ui_border"], sw=1.5, rx=8))
        p.append(text(cx + col_w / 2, top_y + 24, c["title"], size=12, color=INK, bold=True))

        b_w = 110
        p.append(rect(cx + (col_w - b_w) / 2, top_y + 36, b_w, 22, fill=c["badge_color"], stroke=c["badge_color"], sw=1, rx=4))
        p.append(text(cx + col_w / 2, top_y + 51, c["badge"], size=11, color="#ffffff", bold=True))

        p.append(mtext(cx + col_w / 2, top_y + 80, c["desc"], size=10.5, color=MUTED, lh=1.35))
        p.append(line(cx + 10, top_y + 130, cx + col_w - 10, top_y + 130, color=MUTED, sw=0.8, dash="3 3"))

        ui_y = top_y + 145
        if c["title"].startswith("1."):
            p.append(rect(cx + 15, ui_y, col_w - 30, 80, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
            p.append(text(cx + col_w / 2, ui_y + 20, "Disarm Motors?", size=10, color=POS, bold=True))
            p.append(rect(cx + 25, ui_y + 40, 60, 26, fill=POS, stroke=POS, rx=3))
            p.append(text(cx + 55, ui_y + 57, "OK", size=10, color="#ffffff", bold=True))
            p.append(rect(cx + 95, ui_y + 40, 65, 26, fill="#e0e0e0", stroke="#ccc", rx=3))
            p.append(text(cx + 127, ui_y + 57, "Cancel", size=10, color=INK))
            p.append(arrow(cx + col_w / 2 + 10, ui_y + 90, cx + 55, ui_y + 68, color=POS, sw=1.4))
            p.append(text(cx + col_w / 2, ui_y + 106, "Автоматичний клік!", size=10, color=POS, bold=True))
        elif c["title"].startswith("2."):
            p.append(rect(cx + 15, ui_y, col_w - 30, 80, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
            p.append(rect(cx + 25, ui_y + 12, 65, 26, fill="#27ae60", stroke="#27ae60", rx=3))
            p.append(text(cx + 57, ui_y + 29, "1. ARM [On]", size=9, color="#ffffff", bold=True))
            p.append(arrow(cx + 93, ui_y + 25, cx + 103, ui_y + 50, color=FIELD, sw=1.3))
            p.append(rect(cx + 105, ui_y + 42, 60, 26, fill="#c0392b", stroke="#c0392b", rx=3))
            p.append(text(cx + 135, ui_y + 59, "2. FIRE", size=9, color="#ffffff", bold=True))
            p.append(text(cx + col_w / 2, ui_y + 106, "Вікно зведення: 5.0 с", size=10, color=FIELD, bold=True))
        elif c["title"].startswith("3."):
            p.append(rect(cx + 15, ui_y, col_w - 30, 80, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
            p.append(circle(cx + col_w / 2, ui_y + 38, 26, fill="#eef3fc", stroke="#d0dbee", sw=3))
            p.append(circle(cx + col_w / 2, ui_y + 38, 26, fill="none", stroke=NEG, sw=3.5))
            p.append(text(cx + col_w / 2, ui_y + 43, "2.1 s", size=11, color=NEG, bold=True))
            p.append(text(cx + col_w / 2, ui_y + 106, "Утримуйте 3.0 с...", size=10, color=NEG, bold=True))
        else:
            p.append(rect(cx + 15, ui_y, col_w - 30, 80, fill="#ffffff", stroke="#d35400", sw=1.2, rx=4))
            p.append(rect(cx + 25, ui_y + 26, col_w - 50, 30, fill="#fbeee6", stroke="#e59866", sw=1.2, rx=15))
            p.append(circle(cx + 42, ui_y + 41, 12, fill="#d35400", stroke="#d35400"))
            p.append(arrow(cx + 60, ui_y + 41, cx + 130, ui_y + 41, color="#d35400", sw=1.4))
            p.append(text(cx + 110, ui_y + 44, "Slide >>", size=9, color="#d35400", bold=True))
            p.append(text(cx + col_w / 2, ui_y + 106, "Свайп до кінця треку", size=10, color="#d35400", bold=True))

        list_y = top_y + 268
        for k, (lbl, val) in enumerate(c["items"]):
            iy = list_y + k * 28
            p.append(text(cx + 14, iy, lbl, size=10, color=INK, bold=True, anchor="start"))
            p.append(text(cx + 14, iy + 13, val, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "safety-ui-patterns.svg"), W, H, *p,
           title="Порівняння інтерфейсних патернів критичних операцій")


# ── 2. safety-interlock-fsm: Скінченний автомат захищеної дії ─────────────────
def fig_safety_interlock_fsm():
    W, H = 840, 480
    p = []

    # Стан 1: SAFE_IDLE (Спокій)
    b_idle, _, _ = textbox(120, 150, "SAFE_IDLE\n(Безпечний стан)\nВиконавчі ланцюги розірвані\nТокен захисту: 0x0000", size=11, fill="#f4f6f8", stroke=LINE, bold=True)
    p.append(b_idle)

    # Стан 2: ARMED (Зведено)
    b_armed, _, _ = textbox(420, 150, "ARMED_LATCH\n(Зведено, очікування)\nТаймер зведення t < 5.0 с\nТокен зведення: 0x5A5A", size=11, fill="#fef9e7", stroke="#f39c12", bold=True, color="#7d6608")
    p.append(b_armed)

    # Стан 3: HOLD_ACCUMULATING (Накопичення затискання)
    b_hold, _, _ = textbox(420, 330, "HOLD_PROGRESS\n(Затискання кнопки/тачу)\nІнтегрування: t_hold += dt\nВізуалізація 0..100%", size=11, fill="#ebf5fb", stroke=NEG, bold=True, color=NEG)
    p.append(b_hold)

    # Стан 4: COUNTDOWN_ABORTABLE (Вікно скасування)
    b_abort, _, _ = textbox(720, 330, "COUNTDOWN_GRACE\n(Вікно скасування)\nВідлік 3.. 2.. 1.. (siren)\nКнопка ABORT активна", size=11, fill="#fdf2e9", stroke="#d35400", bold=True, color="#a04000")
    p.append(b_abort)

    # Стан 5: EXECUTED (Спрацювання)
    b_exec, _, _ = textbox(720, 150, "TRIGGERED_EXEC\n(Виконання дії)\nІмпульс на привід\nЗапис у лог польоту", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD)
    p.append(b_exec)

    # Переходи
    # 1 -> 2: Arm trigger
    p.append(arrow(210, 150, 320, 150, color=FIELD, sw=1.8))
    p.append(text(265, 138, "Подія ARM", size=10, color=FIELD, bold=True))

    # 2 -> 1: Timeout зведення
    p.append(arrow(350, 120, 190, 120, color=POS, sw=1.5))
    p.append(text(270, 110, "Таймаут (t > 5.0 с) / CANCEL", size=9.5, color=POS, italic=True))

    # 2 -> 3: Press Fire
    p.append(arrow(420, 205, 420, 275, color=NEG, sw=1.8))
    p.append(text(495, 240, "PRESS_DOWN (початок утримання)", size=10, color=NEG, bold=True))

    # 3 -> 1: Early Release (скид)
    p.append(arrow(340, 350, 150, 215, color=POS, sw=1.6))
    p.append(text(210, 305, "RELEASE (t_hold < 3.0 с)", size=10, color=POS, bold=True))
    p.append(text(210, 320, "Миттєве скидання в Safe", size=9, color=MUTED))

    # 3 -> 4: Hold Complete
    p.append(arrow(515, 330, 615, 330, color="#d35400", sw=1.8))
    p.append(text(565, 318, "t_hold ≥ 3.0 с", size=10, color="#d35400", bold=True))

    # 4 -> 1: Abort Click
    p.append(arrow(670, 385, 140, 220, color=POS, sw=1.8))
    p.append(text(390, 440, "Клік «ABORT» під час відліку → Скасування та Safe", size=10.5, color=POS, bold=True))

    # 4 -> 5: Countdown Complete
    p.append(arrow(720, 275, 720, 205, color=FIELD, sw=2.0))
    p.append(text(780, 240, "t_grace == 0.0 с\n(Фінальний спуск)", size=10, color=FIELD, bold=True))

    # 5 -> 1: Auto reset after pulse
    p.append(arrow(630, 150, 215, 150, color=MUTED, sw=1.2))
    p.append(text(420, 80, "Завершення імпульсу → Автоповернення в SAFE_IDLE", size=10, color=MUTED, bold=True))

    render(os.path.join(OUT, "safety-interlock-fsm.svg"), W, H, *p,
           title="Скінченний автомат захисту небезпечних операцій")


# ── 3. hold-countdown-timing: Часові діаграми затискання, прогресу та вікна відліку ──
def fig_hold_countdown_timing():
    W, H = 860, 480
    ox = 90
    aw = 720
    p = []

    # Розмітка смуг
    y1 = 115
    y2 = 215
    y3 = 315
    y4 = 415

    # Часова вісь знизу
    p.append(arrow(ox, y4 + 30, ox + aw, y4 + 30, color=INK, sw=1.4))
    p.append(text(ox + aw - 10, y4 + 48, "Час t", size=11, color=INK, italic=True))

    # Вертикальні мітки часу
    t_press = ox + 40
    t_abort_drop = ox + 180   # Сценарій 1: раннє відпускання (1.2 с)
    t_press2 = ox + 240       # Сценарій 2: повне затискання
    t_hold_done = ox + 460    # Досягнуто 3.0 с
    t_fire = ox + 610         # Завершено вікно 2.0 с

    # Сценарій 1 (зрив)
    p.append(line(t_abort_drop, 68, t_abort_drop, y4 + 25, color=POS, sw=1.0, dash="2 2"))
    b_sc1, _, _ = textbox((t_press + t_abort_drop) / 2, 54, "Сценарій А: Зрив пальця\n(скид прогресу)", size=9.5, fill="#fff5f5", stroke=POS, color=POS)
    p.append(b_sc1)

    # Сценарій 2 (успіх)
    p.append(line(t_hold_done, 68, t_hold_done, y4 + 25, color="#d35400", sw=1.0, dash="2 2"))
    p.append(line(t_fire, 68, t_fire, y4 + 25, color=FIELD, sw=1.0, dash="2 2"))
    b_sc2, _, _ = textbox((t_press2 + t_hold_done) / 2, 54, "Сценарій Б: Повне затискання\n(3.0 с утримання)", size=9.5, fill="#ebf5fb", stroke=NEG, color=NEG)
    p.append(b_sc2)
    b_sc3, _, _ = textbox((t_hold_done + t_fire) / 2, 54, "Вікно Abort (2.0 с)\n(можна скасувати)", size=9.5, fill="#fef9e7", stroke="#f39c12", color="#7d6608")
    p.append(b_sc3)

    # 1. Сигнал кнопки
    p.append(text(ox - 12, y1 - 12, "Кнопка / Touch", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(ox, y1, t_press, y1, color=MUTED, sw=2))
    p.append(line(t_press, y1, t_press, y1 - 26, color=NEG, sw=2))
    p.append(line(t_press, y1 - 26, t_abort_drop, y1 - 26, color=NEG, sw=2))
    p.append(line(t_abort_drop, y1 - 26, t_abort_drop, y1, color=POS, sw=2))
    p.append(line(t_abort_drop, y1, t_press2, y1, color=MUTED, sw=2))
    p.append(line(t_press2, y1, t_press2, y1 - 26, color=NEG, sw=2))
    p.append(line(t_press2, y1 - 26, t_hold_done + 30, y1 - 26, color=NEG, sw=2))
    p.append(line(t_hold_done + 30, y1 - 26, t_hold_done + 30, y1, color=MUTED, sw=2))
    p.append(line(t_hold_done + 30, y1, ox + aw - 20, y1, color=MUTED, sw=2))
    p.append(text((t_press + t_abort_drop) / 2, y1 + 16, "HOLD (1.2 с)", size=9, color=NEG, anchor="middle"))
    p.append(text((t_press2 + t_hold_done) / 2, y1 + 16, "HOLD (3.0 с неперервно)", size=9, color=NEG, anchor="middle"))

    # 2. Прогрес Hold
    p.append(text(ox - 12, y2 - 12, "Прогрес Hold (0..100%)", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(ox, y2, ox + aw - 20, y2, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(ox, y2 - 35, ox + aw - 20, y2 - 35, color="#d0d0d0", sw=1.0, dash="2 2"))
    p.append(text(ox - 8, y2 - 33, "100%", size=9, color=MUTED, anchor="end"))
    p.append(text(ox - 8, y2 + 4, "0%", size=9, color=MUTED, anchor="end"))

    # Крива прогресу 1
    p.append(line(ox, y2, t_press, y2, color=MUTED, sw=2))
    p.append(line(t_press, y2, t_abort_drop, y2 - 16, color=NEG, sw=2.5))
    p.append(line(t_abort_drop, y2 - 16, t_abort_drop + 8, y2, color=POS, sw=2.5)) # Миттєвий спад
    p.append(text(t_abort_drop + 14, y2 - 18, "Спад на 0%!", size=9, color=POS, bold=True, anchor="start"))

    # Крива прогресу 2
    p.append(line(t_abort_drop + 8, y2, t_press2, y2, color=MUTED, sw=2))
    p.append(line(t_press2, y2, t_hold_done, y2 - 35, color=NEG, sw=2.5))
    p.append(circle(t_hold_done, y2 - 35, 4, fill=FIELD, stroke=FIELD))
    p.append(line(t_hold_done, y2 - 35, t_hold_done + 8, y2, color=MUTED, sw=2))
    p.append(line(t_hold_done + 8, y2, ox + aw - 20, y2, color=MUTED, sw=2))

    # 3. Відлік Abort Window
    p.append(text(ox - 12, y3 - 12, "Таймер Abort Window", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(ox, y3, ox + aw - 20, y3, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(t_hold_done, y3 - 35, t_fire, y3, color="#d35400", sw=2.5))
    p.append(line(t_hold_done, y3, t_hold_done, y3 - 35, color="#d35400", sw=2))
    p.append(text(t_hold_done + 12, y3 - 38, "3.. 2.. 1.. відлік", size=9.5, color="#d35400", bold=True, anchor="start"))

    # 4. Імпульс на привід
    p.append(text(ox - 12, y4 - 12, "Імпульс спуску (FIRE)", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(ox, y4, t_fire, y4, color=MUTED, sw=2))
    p.append(line(t_fire, y4, t_fire, y4 - 35, color=FIELD, sw=2.5))
    p.append(line(t_fire, y4 - 35, t_fire + 50, y4 - 35, color=FIELD, sw=2.5))
    p.append(line(t_fire + 50, y4 - 35, t_fire + 50, y4, color=FIELD, sw=2.5))
    p.append(line(t_fire + 50, y4, ox + aw - 20, y4, color=MUTED, sw=2))
    p.append(text(t_fire + 25, y4 - 42, "FIRE PULSE (500 мс)", size=9.5, color=FIELD, bold=True, anchor="middle"))

    render(os.path.join(OUT, "hold-countdown-timing.svg"), W, H, *p,
           title="Часова діаграма затискання, прогресу та вікна відліку")


if __name__ == "__main__":
    fig_safety_ui_patterns()
    fig_safety_interlock_fsm()
    fig_hold_countdown_timing()
    print("Всі 3 фігури згенеровано успішно.")
