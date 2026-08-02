# -*- coding: utf-8 -*-
"""Фігури до теми «Менеджер каналів: облік і життєвий цикл з'єднань»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Дві сутності: опис і живе з'єднання ─────────────────────────────────
def fig_two_entities():
    W, H = 1000, 560
    f = []

    # ліворуч — диск
    f.append(fitbox(50, 120, 190, 96,
                    ["Налаштування", "на диску", "(переживають", "перезапуск)"],
                    size=15, fill="#eef4ff", stroke=NEG))
    f.append(text(145, 240, "зберігається лише опис", size=13, color=MUTED))

    # менеджер — велика рамка з двома списками
    f.append(rect(300, 70, 640, 400, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(620, 100, "LinkManager — один на застосунок", size=16, bold=True))

    # список описів
    f.append(rect(340, 130, 250, 150, fill="#f7fbff", stroke=NEG, sw=1.5))
    f.append(text(465, 156, "список описів", size=14, bold=True, color=NEG))
    f.append(fitbox(360, 172, 210, 42, ["LinkConfiguration", "«UDP 14550»"], size=13))
    f.append(fitbox(360, 222, 210, 42, ["LinkConfiguration", "«/dev/ttyACM0»"], size=13))

    # список живих зʼєднань
    f.append(rect(650, 130, 250, 150, fill="#fff7f5", stroke=POS, sw=1.5))
    f.append(text(775, 156, "список живих з'єднань", size=14, bold=True, color=POS))
    f.append(fitbox(670, 172, 210, 42, ["UDPLink", "сокет відкрито"], size=13))
    f.append(fitbox(670, 222, 210, 42, ["SerialLink", "порт відкрито"], size=13))

    # стрілки володіння між парами
    f.append(arrow(575, 193, 668, 193, color=POS))
    f.append(text(621, 182, "слабко", size=12, color=POS))
    f.append(arrow(668, 243, 575, 243, color=NEG))
    f.append(text(621, 262, "міцно", size=12, color=NEG))

    # диск -> список описів
    f.append(arrow(243, 168, 336, 175, color=NEG))

    # пояснення внизу, у два широкі рядки з великим полем
    f.append(fitbox(340, 320, 250, 120,
                    ["Опис довговічний:", "живе між запусками,", "з нього народжується", "багато з'єднань"],
                    size=14, fill="#f7fbff", stroke=NEG))
    f.append(fitbox(650, 320, 250, 120,
                    ["З'єднання коротке:", "гине разом із портом", "і не зберігається", "ніде"],
                    size=14, fill="#fff7f5", stroke=POS))

    f.append(text(500, 510, "міцне посилання не дає обʼєкту померти · слабке лише питає «ти ще там?»",
                  size=14, color=MUTED))
    render(os.path.join(OUT, 'two-entities.svg'), W, H, *f)


# ── 2. Життєвий цикл зʼєднання ─────────────────────────────────────────────
def fig_lifecycle():
    W, H = 1060, 720
    f = []

    steps = [
        ("1 · фабрика за типом", "обрано клас з'єднання"),
        ("2 · видача каналу", "номер для розбирача"),
        ("3 · підписка на сигнали", "байти вже не загубляться"),
        ("4 · спроба відкрити порт", "точка неповернення"),
        ("5 · у список живих", "під м'ютексом"),
        ("6 · звʼязати з описом", "інтерфейс бачить «під'єднано»"),
    ]

    x, w, h, gap = 60, 380, 66, 22
    y0 = 80
    for i, (a, b) in enumerate(steps):
        y = y0 + i * (h + gap)
        col = POS if i == 3 else FILL
        stroke = POS if i == 3 else LINE
        f.append(fitbox(x, y, w, h, [a, b], size=15,
                        fill="#fff7f5" if i == 3 else FILL, stroke=stroke))
        if i < len(steps) - 1:
            f.append(arrow(x + w / 2, y + h, x + w / 2, y + h + gap))

    # гілка відкату праворуч
    bx = 590
    f.append(rect(bx, 80, 410, 348, fill="#fdf4f3", stroke=POS, sw=1.5))
    f.append(text(bx + 205, 110, "невдача на кроці 4 → повний відкат", size=15, bold=True, color=POS))
    undo = [
        "відписатися від усіх сигналів",
        "повернути номер каналу в маску",
        "зняти з опису вказівник на з'єднання",
        "у списку живих з'єднань нічого нема",
    ]
    for i, s in enumerate(undo):
        f.append(fitbox(bx + 25, 140 + i * 68, 360, 52, s, size=14, fill="#ffffff", stroke=POS))

    f.append(arrow(x + w + 10, 80 + 3 * (h + gap) + h / 2, bx - 10, 300, color=POS))

    # смерть
    f.append(rect(590, 470, 410, 190, fill="#f2f7ff", stroke=NEG, sw=1.5))
    f.append(text(795, 500, "смерть: сигнал «розірвано»", size=15, bold=True, color=NEG))
    die = [
        "забрати копію вказівника, потім erase",
        "відв'язати опис, відписатися",
        "повернути номер каналу в маску",
    ]
    for i, s in enumerate(die):
        f.append(fitbox(615, 520 + i * 46, 360, 38, s, size=13, fill="#ffffff", stroke=NEG))

    f.append(arrow(x + w / 2, y0 + 5 * (h + gap) + h + 6, x + w / 2, 600))
    f.append(arrow(x + w / 2 + 10, 600, 585, 600, color=NEG))
    f.append(text(430, 634, "кабель смикнули", size=13, color=NEG, anchor="middle"))

    render(os.path.join(OUT, 'lifecycle.svg'), W, H, *f)


# ── 3. Канали MAVLink як бітова маска ──────────────────────────────────────
def fig_channels():
    W, H = 1020, 520
    f = []

    n = 16
    cw, ch = 52, 52
    x0, y0 = 60, 110
    used = {0: "рез.", 1: None, 2: None, 5: None}
    f.append(text(W / 2, 60, "маска зайнятих каналів (до 16 на настільних системах)",
                  size=16, bold=True))

    for i in range(n):
        x = x0 + i * (cw + 4)
        busy = i in used
        f.append(rect(x, y0, cw, ch,
                      fill="#fdecea" if busy else "#eef7f0",
                      stroke=POS if busy else FIELD, sw=1.5))
        f.append(text(x + cw / 2, y0 + 34, "1" if busy else "0", size=20, bold=True,
                      color=POS if busy else FIELD))
        f.append(text(x + cw / 2, y0 + 76, str(i), size=12, color=MUTED))

    f.append(text(x0 + 20, y0 - 16, "біт 0", size=12, color=MUTED, anchor="start"))

    # три звʼязки: канал -> зʼєднання -> стан розбирача
    boxes = [
        (0, "нульовий канал\nзарезервовано", MUTED, "#f4f6f8"),
        (1, "UDPLink\nстан розбирача №1", NEG, "#f2f7ff"),
        (2, "SerialLink\nстан розбирача №2", NEG, "#f2f7ff"),
        (5, "LogReplayLink\nстан розбирача №5", NEG, "#f2f7ff"),
    ]
    bw, bh = 225, 74
    for k, (idx, label, col, fill) in enumerate(boxes):
        bx = 60 + k * (bw + 20)
        by = 300
        f.append(fitbox(bx, by, bw, bh, label.split("\n"), size=14, fill=fill, stroke=col))
        f.append(arrow(x0 + idx * (cw + 4) + cw / 2, y0 + ch + 22, bx + bw / 2, by - 6, color=col))

    f.append(text(W / 2, 440, "кожен номер — окремий стан розбору, версія протоколу, підпис і лічильники втрат",
                  size=14, color=MUTED))
    f.append(text(W / 2, 472, "звільнений номер повертається в маску й дістанеться наступному з'єднанню",
                  size=14, color=MUTED))

    render(os.path.join(OUT, 'channels.svg'), W, H, *f)


# ── 4. Пошук першого вільного біта ─────────────────────────────────────────
def fig_alloc_scan():
    W, H = 1080, 520
    f = []

    f.append(text(W / 2, 46, "видача номера: перший нуль у масці — і є номер каналу",
                  size=17, bold=True))

    n = 16
    cw, gap = 56, 6
    x0, y0, ch = 50, 120, 54
    busy = {0, 1, 2, 4}
    first_free = 3

    for i in range(n):
        x = x0 + i * (cw + gap)
        b = i in busy
        f.append(text(x + cw / 2, y0 - 12, str(i), size=12, color=MUTED))
        f.append(rect(x, y0, cw, ch,
                      fill="#fdecea" if b else "#eef7f0",
                      stroke=POS if b else FIELD, sw=1.5))
        f.append(text(x + cw / 2, y0 + 36, "1" if b else "0", size=22, bold=True,
                      color=POS if b else FIELD))

    # рамка навколо знайденого біта
    xf = x0 + first_free * (cw + gap)
    f.append(rect(xf - 6, y0 - 6, cw + 12, ch + 12, fill="none", stroke=FIELD, sw=3))

    # хід перебору під клітинками
    for i in range(first_free):
        x = x0 + i * (cw + gap)
        f.append(text(x + cw / 2, y0 + ch + 24, "зайн.", size=11, color=POS))
    f.append(arrow(x0 + 8, y0 + ch + 40, xf + cw / 2, y0 + ch + 40, color=MUTED, sw=1.5))
    f.append(arrow(xf + cw / 2, y0 + ch + 62, xf + cw / 2, y0 + ch + 16, color=FIELD))
    f.append(text(xf + cw / 2 + 190, y0 + ch + 86,
                  "перебір іде знизу вгору й спиняється на першому нулі",
                  size=14, color=MUTED))

    # три операції
    ops = [
        ["перевірити зайнятість", "mask & (1u << i)", "не нуль — номер зайнято"],
        ["взяти номер", "mask |= (1u << i)", "біт стає одиницею"],
        ["повернути номер", "mask &= ~(1u << i)", "біт стає нулем"],
    ]
    bw, bh, bx0 = 320, 96, 50
    for k, lines in enumerate(ops):
        bx = bx0 + k * (bw + 25)
        f.append(fitbox(bx, 300, bw, bh, lines, size=15,
                        fill="#ffffff", stroke=NEG))

    f.append(text(W / 2, 438,
                  "уся зайнятість шістнадцяти каналів — одне 32-бітове число, без купи й без списку",
                  size=14, color=MUTED))
    f.append(text(W / 2, 470,
                  "жодного нуля не знайшлося → повертаємо 0xFF, а не якийсь «поганий» номер",
                  size=14, color=MUTED))

    render(os.path.join(OUT, 'alloc-scan.svg'), W, H, *f)


# ── 5. Що тягне за собою номер каналу при передачі ─────────────────────────
def fig_handover():
    W, H = 1120, 660
    f = []

    f.append(text(W / 2, 44, "номер каналу передають новому орендарю разом зі станом",
                  size=17, bold=True))

    # ліворуч — запис стану
    f.append(rect(45, 80, 450, 460, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(270, 112, "mavlink_status_t каналу №3", size=15, bold=True))

    rows = [
        (["parse_state", "де ми посеред пакета"], NEG),
        (["flags", "версія протоколу на вихід і на вхід"], NEG),
        (["signing", "вказівник на ключ підпису"], NEG),
        (["signing_streams", "вказівник на таблицю потоків"], NEG),
        (["current_rx_seq / current_tx_seq", "наскрізні номери пакетів"], POS),
        (["packet_rx_success_count / drop_count", "лічильники втрат"], POS),
    ]
    rw, rh = 410, 54
    for i, (lines, col) in enumerate(rows):
        ry = 140 + i * 62
        f.append(fitbox(65, ry, rw, rh, lines, size=13,
                        fill="#f7fbff" if col is NEG else "#fdf4f3", stroke=col))

    # праворуч — три вердикти
    f.append(fitbox(545, 116, 525, 104,
                    ["mavlink_reset_channel_status(3)",
                     "скидає РІВНО одне поле: parse_state"],
                    size=15, fill="#eef7f0", stroke=FIELD))

    f.append(fitbox(545, 268, 525, 150,
                    ["решту версії й підпису доводять руками:",
                     "flags — виставити потрібну версію протоколу",
                     "signing = nullptr, signing_streams = nullptr",
                     "інакше новий орендар підпише чужим ключем"],
                    size=14, fill="#f2f7ff", stroke=NEG))

    f.append(fitbox(545, 452, 525, 104,
                    ["а лічильники не чистить ніхто —",
                     "новий орендар успадковує чужу статистику"],
                    size=15, fill="#fdf4f3", stroke=POS))

    # звʼязки
    f.append(arrow(480, 167, 540, 168, color=FIELD))
    f.append(arrow(480, 229, 540, 300, color=NEG))
    f.append(arrow(480, 291, 540, 330, color=NEG))
    f.append(arrow(480, 353, 540, 360, color=NEG))
    f.append(arrow(480, 415, 540, 480, color=POS))
    f.append(arrow(480, 477, 540, 520, color=POS))

    f.append(text(W / 2, 600,
                  "назва функції обіцяє повне очищення — насправді вона забуває лише позицію в потоці",
                  size=14, color=MUTED))
    f.append(text(W / 2, 630,
                  "тому видача каналу — це не «дати число», а «дати число й прибрати за попереднім»",
                  size=14, color=MUTED))

    render(os.path.join(OUT, 'handover.svg'), W, H, *f)


fig_two_entities()
fig_lifecycle()
fig_channels()
fig_alloc_scan()
fig_handover()
print("ok")
