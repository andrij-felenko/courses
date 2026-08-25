# -*- coding: utf-8 -*-
"""Фігури до теми «Надійний обмін».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── heartbeat: рівні «удари» живого зв'язку, тиша = втрата ─────────────────────
# Ідея: радіо не дає події «від'єднано»; живий бік періодично шле короткий
# сигнал, і саме його ВІДСУТНІСТЬ задовго стає ознакою втрати.
def fig_heartbeat():
    W, H = 720, 250
    p = []
    ax_y = 150
    x0, x1 = 70, 650
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=1.6))
    p.append(arrow(x1 - 2, ax_y, x1 + 14, ax_y, color=INK, sw=1.6))
    p.append(text(x1 + 18, ax_y + 4, "час", size=11, color=MUTED, anchor="start", italic=True))

    # рівні удари «живий»
    beats = [110, 200, 290, 380]
    for bx in beats:
        p.append(line(bx, ax_y, bx, ax_y - 42, color=FIELD, sw=2.8))
        p.append(text(bx, ax_y - 48, "♥", size=13, color=FIELD, bold=True))
    p.append(text((beats[0] + beats[-1]) / 2, ax_y + 22,
                  "рівні удари: «живий, живий…»", size=11, color=FIELD, bold=True))

    # зона тиші
    p.append(rect(440, ax_y - 44, 200, 44, fill="#fdecea", stroke=POS, sw=1.4))
    p.append(text(540, ax_y - 18, "ударів нема", size=11, color=POS, bold=True))
    p.append(line(620, ax_y, 620, ax_y - 64, color=POS, sw=2.0, dash="3 3"))
    p.append(text(620, ax_y - 70, "тиша задовга → втрата", size=10.5, color=POS, bold=True))

    p.append(text(W / 2, H - 24,
                  "радіо не дає події «від'єднано» — втрату ловлять за відсутністю серцебиття",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "heartbeat.svg"), W, H, *p,
           title="Серцебиття: «я живий» через рівні проміжки")


# ── timeout: лічильник часу від останнього пакета проти порога ─────────────────
# Ідея: втрату виявляють не «подією», а таймаутом — час від останнього
# отриманого повідомлення переріс поріг.
def fig_timeout():
    W, H = 720, 250
    p = []
    ax_y = 150
    x0, x1 = 70, 650
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=1.6))
    p.append(arrow(x1 - 2, ax_y, x1 + 14, ax_y, color=INK, sw=1.6))
    p.append(text(x1 + 18, ax_y + 4, "час", size=11, color=MUTED, anchor="start", italic=True))

    # прийняті пакети оновлюють lastMsg
    msgs = [110, 190, 270, 350]
    for mx in msgs:
        p.append(line(mx, ax_y, mx, ax_y - 34, color=INK, sw=2.4))
        p.append(text(mx, ax_y - 40, "пакет", size=9, color=INK))
    last = msgs[-1]
    p.append(circle(last, ax_y - 34, 3.4, fill=INK, stroke=INK, sw=1))
    p.append(text(last, ax_y + 20, "lastMsg", size=10, color=INK, bold=True))

    # вікно очікування до порога
    thr = last + 220
    p.append(line(last, ax_y - 70, thr, ax_y - 70, color=NEG, sw=1.6))
    p.append(line(last, ax_y - 76, last, ax_y - 64, color=NEG, sw=1.6))
    p.append(line(thr, ax_y - 76, thr, ax_y - 64, color=NEG, sw=1.6))
    p.append(text((last + thr) / 2, ax_y - 78, "millis() − lastMsg", size=10, color=NEG, bold=True))

    # поріг і спрацювання
    p.append(line(thr, ax_y + 8, thr, ax_y - 96, color=POS, sw=2.0, dash="4 3"))
    p.append(text(thr, ax_y - 102, "поріг TIMEOUT", size=10.5, color=POS, bold=True))
    p.append(text(thr + 8, ax_y + 22, "→ failsafe()", size=11, color=POS, anchor="start", bold=True))

    p.append(text(W / 2, H - 24,
                  "кожен пакет оновлює lastMsg; перевищив поріг — спрацьовує реакція",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeout.svg"), W, H, *p,
           title="Виявлення втрати: не подія, а таймаут тиші")


# ── failsafe: безпечна дія проти «лети як летів» ──────────────────────────────
# Ідея: на втрату зв'язку правильна реакція — заздалегідь продумана безпечна
# дія; «продовжувати останню команду» — найгірший результат.
def fig_failsafe():
    W, H = 720, 320
    p = []
    cx = W / 2
    core, cw, ch = textbox(cx, 90, "зв'язок утрачено", size=13, bold=True,
                           fill="#fdecea", stroke=POS, sw=2, pad=14)
    p.append(core)

    # три безпечні гілки
    good = [
        (150, "дрон:\nзависнути / RTL / сісти", FIELD),
        (cx, "робот, ровер:\nзупинити мотори", FIELD),
        (W - 150, "виконавчий механізм:\nбезпечне положення", FIELD),
    ]
    gy = 215
    for gx, lab, col in good:
        b, bw, bh = textbox(gx, gy, lab, size=11, bold=True, color=col,
                            fill="#eafaf0", stroke=col, sw=1.8)
        p.append(line(cx, 90 + ch / 2, gx, gy - bh / 2, color=col, sw=1.6))
        p.append(b)

    # заборонене
    bad, bw, bh = textbox(cx, 290, "НІКОЛИ: «продовжувати останню команду»",
                          size=11.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2)
    p.append(bad)

    render(os.path.join(OUT, "failsafe.svg"), W, H, *p,
           title="Реакція на втрату: безпечна дія, а не «лети як летів»")


# ── state-vs-cmd: абсолютний стан самовиправляється, приріст накопичує помилку ──
# Ідея: загублений абсолютний стан лагодить наступне оновлення; загублений
# приріст зникає назавжди й зсуває приймач.
def fig_state_vs_cmd():
    W, H = 720, 320
    p = []
    bw, bh, step = 110, 32, 180
    x0 = 110

    def row(y, vals, lost_idx, good):
        col = FIELD if good else POS
        for i, v in enumerate(vals):
            x = x0 + i * step
            lost = (i == lost_idx)
            fill = "#f4f4f4" if lost else ("#eafaf0" if good else "#eef4ff")
            sc = POS if lost else col
            p.append(rect(x, y, bw, bh, fill=fill, stroke=sc, sw=1.8 if not lost else 1.4))
            p.append(text(x + bw / 2, y + bh / 2 + 4, v, size=11,
                          color=sc, bold=True))
            if i > 0:
                p.append(arrow(x0 + (i - 1) * step + bw, y + bh / 2, x - 2, y + bh / 2,
                               color=MUTED, sw=1.4))

    # добре: стан
    p.append(text(x0, 92, "стан (добре): шлемо точне значення", size=12,
                  color=FIELD, anchor="start", bold=True))
    row(108, ["газ=30", "газ=50", "газ=70"], 1, True)
    p.append(text(W / 2, 168, "загубили «50» — «70» одразу все виправило",
                  size=10.5, color=FIELD, bold=True))

    # погано: приріст
    p.append(text(x0, 222, "приріст (погано): шлемо зміну", size=12,
                  color=POS, anchor="start", bold=True))
    row(238, ["+10", "+10", "+10"], 1, False)
    p.append(text(W / 2, 298, "загубили один «+10» — приймач назавжди на 10 нижче",
                  size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "state-vs-cmd.svg"), W, H, *p,
           title="Шли стан, а не приріст: втрата сама виправляється")


# ── sequence: відкидати застарілі за номером послідовності ─────────────────────
# Ідея: радіо тасує порядок; запізніла команда зі старішим номером має бути
# відкинута, інакше стан відкотиться назад.
def fig_sequence():
    W, H = 720, 270
    p = []
    ax_y = 150
    x0, x1 = 70, 650
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=1.6))
    p.append(arrow(x1 - 2, ax_y, x1 + 14, ax_y, color=INK, sw=1.6))
    p.append(text(x1 + 18, ax_y + 4, "прихід", size=11, color=MUTED, anchor="start", italic=True))

    # послідовність приходу: #5 #6 #8 (потім запізніла #7)
    seq = [("#5", 120, True), ("#6", 220, True), ("#8", 320, True)]
    for lab, sx, ok in seq:
        col = FIELD
        p.append(circle(sx, ax_y, 18, fill="#eafaf0", stroke=col, sw=2))
        p.append(text(sx, ax_y + 5, lab, size=12, color=col, bold=True))
    # запізніла #7
    lx = 460
    p.append(circle(lx, ax_y, 18, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(lx, ax_y + 5, "#7", size=12, color=POS, bold=True))
    p.append(line(lx - 13, ax_y - 13, lx + 13, ax_y + 13, color=POS, sw=2.4))
    p.append(line(lx - 13, ax_y + 13, lx + 13, ax_y - 13, color=POS, sw=2.4))
    p.append(text(lx, ax_y - 30, "запізніла", size=10, color=POS, bold=True))
    p.append(text(lx, ax_y + 42, "< останнього → відкинути", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 26,
                  "бери лише номер БІЛЬШИЙ за останній прийнятий; менший — застарілий",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "sequence.svg"), W, H, *p,
           title="Номери послідовності: відкидати застарілі команди")


# ── ack-besteffort: критичне з підтвердженням, потік — як вийде ────────────────
# Ідея: платити за надійність вибірково — рідкісні важливі команди з ACK і
# повтором; часта телеметрія best-effort.
def fig_ack_besteffort():
    W, H = 720, 300
    p = []

    # ліва колонка: критичне з ACK
    lx = 190
    p.append(text(lx, 80, "критичне: ACK + повтор", size=12, color=POS, bold=True))
    a, aw, ah = textbox(lx, 130, "«вимкнути мотори»", size=11, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.8)
    p.append(a)
    b, bw2, bh2 = textbox(lx, 210, "приймач", size=11, bold=True,
                          fill=FILL, stroke=INK, sw=1.6)
    p.append(b)
    p.append(arrow(lx - 20, 130 + ah / 2, lx - 20, 210 - bh2 / 2, color=POS, sw=1.8))
    p.append(text(lx - 26, 175, "шлю", size=9, color=POS, anchor="end"))
    p.append(arrow(lx + 20, 210 - bh2 / 2, lx + 20, 130 + ah / 2, color=FIELD, sw=1.8))
    p.append(text(lx + 26, 175, "ACK", size=9, color=FIELD, anchor="start", bold=True))
    p.append(text(lx, 250, "повторюю, поки нема ACK", size=10, color=POS))

    # розділювач
    p.append(line(W / 2, 70, W / 2, 260, color=MUTED, sw=1.2, dash="4 4"))

    # права колонка: потік best-effort
    rx = W - 190
    p.append(text(rx, 80, "потік: best-effort", size=12, color=NEG, bold=True))
    yb = 130
    for i, dx in enumerate([-78, -12, 54]):
        p.append(rect(rx + dx - 26, yb - 15, 52, 30, fill="#eef4ff", stroke=NEG, sw=1.4))
        p.append(text(rx + dx, yb + 4, "висота", size=10, color=NEG))
    # одна загублена
    p.append(line(rx - 12 - 16, yb - 15, rx - 12 + 16, yb + 15, color=POS, sw=2.0))
    p.append(text(rx, 175, "загубилось — байдуже,", size=10, color=NEG))
    p.append(text(rx, 192, "наступне свіже за мить", size=10, color=NEG))

    p.append(text(W / 2, H - 22,
                  "не плати за надійність там, де команда не критична",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "ack-besteffort.svg"), W, H, *p,
           title="Розділяй: критичні команди з ACK, потік — best-effort")


# ── layers: три шари надійності, кожен ловить свій клас бід ────────────────────
# Ідея: окремі втрати бере стек; стійкість до плутанини — твій протокол; повну
# втрату — твій застосунок.
def fig_layers():
    W, H = 720, 290
    p = []
    bx, bw = 90, 540
    rows = [
        ("стек радіо", "перешле ОКРЕМІ загублені пакети (CRC, ACK)", NEG, "#eef4ff"),
        ("твій протокол", "номери послідовності + слати стан, не приріст", "#b9770e", "#fdf6e3"),
        ("твій застосунок", "серцебиття, таймаут і failsafe на повну втрату", FIELD, "#eafaf0"),
    ]
    y = 70
    bh = 58
    gap = 18
    cxs = []
    for name, desc, col, fill in rows:
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(text(bx + 18, y + bh / 2 - 4, name, size=12.5, color=col, anchor="start", bold=True))
        p.append(text(bx + 18, y + bh / 2 + 16, desc, size=10.5, color=INK, anchor="start"))
        cxs.append((y, y + bh))
        y += bh + gap
    for i in range(len(rows) - 1):
        ay = cxs[i][1]
        p.append(arrow(bx + bw / 2, ay, bx + bw / 2, ay + gap - 2, color=MUTED, sw=1.6))

    p.append(text(W / 2, H - 20,
                  "кожен шар ловить свій клас бід — окремі втрати, плутанину, повний обрив",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "layers.svg"), W, H, *p,
           title="Три шари надійності бездротового обміну")


if __name__ == "__main__":
    fig_heartbeat()
    fig_timeout()
    fig_failsafe()
    fig_state_vs_cmd()
    fig_sequence()
    fig_ack_besteffort()
    fig_layers()
    print("OK: figures written to", OUT)
