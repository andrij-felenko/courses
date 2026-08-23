# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Стратегії ARQ» (root/course/embedded/zvyazok/arq-strategies).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Stop-and-Wait: три блоки ARQ і чому потрібен номер ──────────────────────
# Ідея, яку важко передати словами: один кадр летить туди, ACK назад; якщо кадр
# або ACK губиться — спрацьовує таймер і кадр шлють знову. А загублений ACK
# породжує ДУБЛІКАТ, який приймач мусить відрізнити за одним бітом-номером.
def fig_stopwait():
    W, H = 880, 470
    f = []
    f.append(text(W / 2, 30, "Stop-and-Wait: послати — чекати ACK — повторити за таймером",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "загублений кадр ловить таймер; загублений ACK породжує дублікат, який ловить біт-номер",
                  11.5, MUTED, "middle", italic=True))

    # дві вертикальні «лінії життя»
    xs, xr = 150, 730                       # колонки: відправник / приймач
    top, bot = 86, H - 40
    f.append(text(xs, top - 12, "відправник", 13, INK, "middle", bold=True))
    f.append(text(xr, top - 12, "приймач", 13, INK, "middle", bold=True))
    f.append(line(xs, top, xs, bot, color=MUTED, sw=1.6, dash="3,4"))
    f.append(line(xr, top, xr, bot, color=MUTED, sw=1.6, dash="3,4"))

    def frame(y0, y1, label, col, ok=True, anchor_left=True):
        # похила стрілка зліва-направо (кадр) або справа-наліво (ACK)
        if anchor_left:
            x0, x1 = xs + 8, xr - 8
        else:
            x0, x1 = xr - 8, xs + 8
        if ok:
            f.append(arrow(x0, y0, x1, y1, color=col, sw=2.2))
        else:
            # обрив посередині — «×»
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            f.append(line(x0, y0, xm, ym, color=col, sw=2.2, dash="5,4"))
            f.append(text(xm + 6, ym - 6, "✕", 17, POS, "middle", bold=True))
        # підпис над стрілкою біля старту
        lx = x0 + (28 if anchor_left else -28)
        f.append(text(lx, y0 - 6, label, 11.5, col, "start" if anchor_left else "end", bold=True))

    y = top + 16
    step = 56
    # кадр 0 → ACK0
    frame(y, y + 20, "кадр №0", NEG); frame(y + 24, y + 44, "ACK №0", FIELD, anchor_left=False)
    y += step + 8
    # кадр 1 ГУБИТЬСЯ → таймаут → повтор кадр 1 → ACK1
    frame(y, y + 20, "кадр №1", NEG, ok=False)
    f.append(text(xs - 14, y + 30, "⏱ таймаут", 11, POS, "end", italic=True))
    f.append(line(xs - 6, y + 8, xs - 6, y + 40, color=POS, sw=1.4, dash="2,3"))
    y += step
    frame(y, y + 20, "кадр №1 (повтор)", NEG); frame(y + 24, y + 44, "ACK №1", FIELD, anchor_left=False)
    y += step + 8
    # кадр 0 → ACK0 ГУБИТЬСЯ → таймаут → повтор кадр 0 → приймач бачить ДУБЛІКАТ
    frame(y, y + 20, "кадр №0", NEG); frame(y + 24, y + 44, "ACK №0", FIELD, ok=False, anchor_left=False)
    f.append(text(xs - 14, y + 54, "⏱ таймаут", 11, POS, "end", italic=True))
    y += step + 16
    frame(y, y + 20, "кадр №0 (повтор)", NEG)
    f.append(text(xr - 8, y + 38, "номер той самий → ДУБЛІКАТ,", 11, POS, "end", bold=True))
    f.append(text(xr - 8, y + 54, "приймач відкидає, шле ACK №0", 11, MUTED, "end"))

    f.append(text(W / 2, H - 14,
                  "Три цеглинки: підтвердження (ACK), таймер на повтор і номер кадру, що відрізняє свіже від дубліката.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "stop-and-wait.svg"), W, H, *f)


# ── 2. Чому Stop-and-Wait марнує канал, а вікно його наповнює ──────────────────
# Ідея: на довгому/швидкому лінку один кадр займає крихту часу, а потім лінк
# СТОЇТЬ цілий пинг-понг, чекаючи ACK. Вікно з N кадрів тримає «трубу» повною.
def fig_pipe():
    W, H = 860, 360
    f = []
    f.append(text(W / 2, 30, "Чому чекати по одному — марнотратство: наповнити «трубу» вікном",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "за час одного оберту (RTT) у дорогу влазить багато кадрів — Stop-and-Wait шле лише один",
                  11.5, MUTED, "middle", italic=True))

    # вісь часу
    x0, x1 = 70, W - 30
    def axis(y, title):
        f.append(text(x0 - 4, y - 26, title, 12.5, INK, "start", bold=True))
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.4))
        f.append(text(x1, y + 16, "час →", 10.5, MUTED, "end", italic=True))

    # верх: Stop-and-Wait — один кадр, потім велика пауза
    yA = 120
    axis(yA, "Stop-and-Wait — один кадр за RTT")
    cw = 26
    f.append(rect(x0 + 6, yA - 18, cw, 16, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(x0 + 6 + cw / 2, yA - 5, "0", 10.5, NEG, "middle", bold=True))
    # довга порожнеча = чекання ACK
    f.append(line(x0 + 6 + cw, yA - 10, x0 + 6 + cw + 300, yA - 10, color=POS, sw=1.4, dash="4,4"))
    f.append(text(x0 + 6 + cw + 150, yA - 18, "лінк СТОЇТЬ — чекаємо ACK (RTT)", 10.5, POS, "middle", italic=True))
    f.append(rect(x0 + 6 + cw + 300, yA - 18, cw, 16, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(x0 + 6 + cw + 300 + cw / 2, yA - 5, "1", 10.5, NEG, "middle", bold=True))

    # низ: вікно — кадри впритул один за одним
    yB = 250
    axis(yB, "Вікно — N кадрів у дорозі за той самий RTT")
    x = x0 + 6
    for i in range(11):
        f.append(rect(x, yB - 18, cw, 16, fill="#e9f7ef", stroke=FIELD, sw=1.8, rx=3))
        f.append(text(x + cw / 2, yB - 5, str(i), 10.5, FIELD, "middle", bold=True))
        x += cw + 3
    f.append(text((x0 + 6 + x) / 2, yB + 18,
                  "перший ACK ще не повернувся, а труба вже повна — пропускна здатність зросла в N разів",
                  10.5, FIELD, "middle", italic=True))

    f.append(text(W / 2, H - 14,
                  "Скільки кадрів влазить у трубу = добуток смуги на затримку (швидкість × RTT); саме він задає розмір вікна.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "pipe-window.svg"), W, H, *f)


# ── 3. Go-Back-N проти Selective Repeat: що саме перешлемо після втрати ────────
# Ідея: загублено кадр №2. GBN відкидає все після нього й шле ЗАНОВО 2,3,4,5…
# (простий приймач, але дублює добре прийняте). SR шле ЛИШЕ №2 (складніший
# приймач із буфером, зате не марнує ефір).
def fig_gbn_sr():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 30, "Після втрати кадру №2: Go-Back-N перешле все, Selective Repeat — лише №2",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "та сама втрата — два підходи: дублювати з місця втрати чи долатати точково",
                  11.5, MUTED, "middle", italic=True))

    cw, gap = 60, 10
    x0 = 150

    def row(y, title, sub, sent, marks, col):
        f.append(text(x0 - 16, y + cw / 2 + 5, title, 12.5, INK, "end", bold=True))
        for i, n in enumerate(sent):
            x = x0 + i * (cw + gap)
            m = marks[i]
            if m == "ok":
                fill, stroke, tc = "#e9f7ef", FIELD, FIELD
            elif m == "lost":
                fill, stroke, tc = "#fdecea", POS, POS
            elif m == "drop":
                fill, stroke, tc = "#f4f6f8", MUTED, MUTED
            else:  # resend
                fill, stroke, tc = "#eaf0fd", NEG, NEG
            f.append(rect(x, y, cw, cw, fill=fill, stroke=stroke, sw=2.0, rx=6))
            f.append(text(x + cw / 2, y + cw / 2 + 6, str(n), 18, tc, "middle", bold=True))
            if m == "lost":
                f.append(text(x + cw / 2, y - 6, "✕ втрата", 10.5, POS, "middle", bold=True))
            elif m == "drop":
                f.append(text(x + cw / 2, y - 6, "відкинуто", 10, MUTED, "middle", italic=True))
            elif m == "resend":
                f.append(text(x + cw / 2, y - 6, "повтор", 10, NEG, "middle", bold=True))
        f.append(text(x0, y + cw + 20, sub, 11, col, "start", italic=True))

    # Go-Back-N: 0,1 ok; 2 lost; 3,4 прийшли але ВІДКИНУТО (не за порядком);
    # далі повтор 2,3,4
    row(96, "Go-Back-N",
        "приймач простий (без буфера), але добре прийняті 3, 4 викинуто й переслано даремно",
        [0, 1, 2, 3, 4, 2, 3, 4],
        ["ok", "ok", "lost", "drop", "drop", "resend", "resend", "resend"], POS)

    # Selective Repeat: 0,1 ok; 2 lost; 3,4 прийняті в БУФЕР; повтор лише 2
    row(256, "Selective Repeat",
        "приймач складніший (буфер на 3, 4), зате в ефір іде лише втрачений №2 — нічого зайвого",
        [0, 1, 2, 3, 4, 2],
        ["ok", "ok", "lost", "ok", "ok", "resend"], FIELD)

    f.append(text(W / 2, H - 14,
                  "Зелене — прийнято, червоне — втрачено, синє — переслано, сіре — викинуто. Вибір: простий приймач чи ощадний ефір.",
                  11.0, INK, "middle", italic=True))
    render(os.path.join(IMG, "gbn-vs-sr.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stopwait()
    fig_pipe()
    fig_gbn_sr()
    print("OK: figures written to", IMG)
