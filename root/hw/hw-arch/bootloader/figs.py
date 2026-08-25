# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── reset: ядро в відомий стан, старт із вектора скидання ──────────────────────
# Ідея: кілька причин (живлення, кнопка, brownout, watchdog) сходяться в одну
# точку — «відомий стан» + єдина стартова адреса (вектор скидання).

def fig_reset():
    W, H = 700, 300
    p = []
    cx, cy = W / 2, 150

    causes = ["увімкнення живлення", "кнопка RESET", "просадка (brownout)", "сторожовий таймер"]
    ly = 70
    lx = 150
    box_w = 0
    centers = []
    for i, c in enumerate(causes):
        yy = ly + i * 48
        b, bw, bh = textbox(lx, yy, c, size=11, fill=FILL, stroke=MUTED, sw=1.3)
        p.append(b)
        centers.append((lx + bw / 2, yy))
        box_w = max(box_w, bw)

    # центральний вузол «відомий стан»
    node, nw, nh = textbox(cx + 150, cy, "відомий\nстан", size=13, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=2, pad=16)
    nx = cx + 150
    for sx, sy in centers:
        p.append(arrow(sx + box_w / 2 - (box_w / 2 - (sx - lx) - 0), sy, nx - nw / 2, cy,
                       color=MUTED, sw=1.5))
    p.append(node)

    # від вузла — до вектора скидання
    vec, vw, vh = textbox(cx + 150, cy + 95, "вектор скидання\n(фіксована адреса)",
                          size=11, bold=True, fill="#fdf6e3", stroke=POS, sw=1.6)
    p.append(arrow(nx, cy + nh / 2, nx, cy + 95 - vh / 2, color=INK, sw=1.8))
    p.append(vec)

    render(os.path.join(OUT, "reset.svg"), W, H, *p,
           title="Скидання: різні причини — одна стартова точка")


# ── bootloader-job: розпорядник обирає й запускає програму ─────────────────────
# Ідея: за вектором скидання — не ваш код, а маленький вибірник, що з кількох
# варіантів обирає один і передає керування.

def fig_bootloader_job():
    W, H = 700, 290
    p = []
    cx = W / 2

    # вектор скидання → завантажувач
    vec, vw, vh = textbox(140, 80, "вектор\nскидання", size=11, bold=True,
                          fill="#fdf6e3", stroke=POS, sw=1.5)
    p.append(vec)
    bl, bw, bh = textbox(cx, 80, "завантажувач\n(розпорядник)", size=12, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, pad=14)
    p.append(arrow(140 + vw / 2, 80, cx - bw / 2, 80, color=INK, sw=1.8))
    p.append(bl)

    # три варіанти вибору
    opts = [
        (170, 215, "звичайна\nпрошивка", FIELD, "#eafaf0"),
        (cx, 230, "режим\nоновлення", NEG, "#eef4ff"),
        (W - 170, 215, "запасна\nкопія", "#8a5fb0", "#f2ecf8"),
    ]
    for ox, oy, lab, col, fill in opts:
        b, ow, oh = textbox(ox, oy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        p.append(line(cx + (ox - cx) * 0.18, 80 + bh / 2, ox, oy - oh / 2, color=col, sw=1.6))
        p.append(b)

    p.append(text(cx, H - 16, "сам нічого «не робить» — він обирає й запускає інших",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bootloader-job.svg"), W, H, *p,
           title="Робота завантажувача: обрати, що запускати")


# ── two-stage: ROM → завантажувач у Flash → застосунок ─────────────────────────
# Ідея: незмінний простак (ROM) підхоплює завжди, передає гнучкому розумнику
# (Flash), той знаходить застосунок.

def fig_two_stage():
    W, H = 720, 300
    p = []
    y = 120
    bw, bh = 190, 88

    stages = [
        (130, "1-й щабель\nROM-завантажувач", "вшитий на заводі\nперевіряє GPIO0", "#f4f6f8", MUTED),
        (360, "2-й щабель\nзавантажувач у Flash", "таблиця розділів\nтакт на повну, app", "#eef4ff", NEG),
        (590, "ваш застосунок", "далі — ваш код", "#eafaf0", FIELD),
    ]
    cxs = []
    for cx, head, sub, fill, col in stages:
        p.append(rect(cx - bw / 2, y - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(mtext(cx, y - 12, head, size=12, color=INK, bold=True))
        p.append(mtext(cx, y + 20, sub, size=10, color=MUTED))
        cxs.append(cx)

    for i in range(len(cxs) - 1):
        p.append(arrow(cxs[i] + bw / 2, y, cxs[i + 1] - bw / 2, y, color=INK, sw=2.0))

    p.append(text(245, y + 78, "оновлюваний?  ні", size=10, color=MUTED))
    p.append(text(W / 2, H - 16, "незнищенний простак передає естафету гнучкому розумнику",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-stage.svg"), W, H, *p,
           title="Два щаблі завантаження ESP32")


# ── c-startup: .data, .bss, стек — тоді виклик точки входу ─────────────────────
# Ідея: три приготування пам'яті (копія .data, обнулення .bss, стек) мусять
# статися ПЕРЕД першим викликом, інакше глобальні змінні — сміття.

def fig_c_startup():
    W, H = 700, 300
    p = []
    cx = W / 2

    steps = [
        (110, "копіювати .data\nFlash → RAM", "#eef4ff", NEG),
        (cx, "обнулити .bss", "#eafaf0", FIELD),
        (W - 110, "поставити\nвказівник стека", "#fdf6e3", POS),
    ]
    y = 95
    for sx, lab, fill, col in steps:
        b, bw, bh = textbox(sx, y, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        p.append(b)

    # усі три сходяться донизу → виклик точки входу
    entry, ew, eh = textbox(cx, 220, "виклик точки входу\n(аж тепер змінні правильні)",
                            size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    for sx, lab, fill, col in steps:
        p.append(line(sx, y + 26, cx + (sx - cx) * 0.2, 220 - eh / 2, color=MUTED, sw=1.5))
    p.append(entry)

    p.append(text(cx, H - 16, "до цього кроку глобальні змінні — ще не їхні значення",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "c-startup.svg"), W, H, *p,
           title="Стартовий код C готує пам'ять перед першим викликом")


# ── full-chain: reset → завантажувачі → C-стартап → ваш код ────────────────────
# Ідея: лінійний ланцюг із шести ланок; кожна готує наступну, остання — звичні
# setup()/loop().

def fig_full_chain():
    W, H = 740, 360
    p = []
    links = [
        ("скидання", "вектор скидання", "#fdf6e3", POS),
        ("ROM-завантажувач", "прошивка? ні →", "#f4f6f8", MUTED),
        ("завантажувач у Flash", "розділи · такт · app", "#eef4ff", NEG),
        ("C-стартап", ".data · .bss · стек", "#eef4ff", NEG),
        ("main() фреймворку", "приготування", "#eafaf0", FIELD),
        ("setup() → loop()", "раз · потім вічно", "#eafaf0", FIELD),
    ]
    bx, bw, bh = 60, 300, 40
    gap = 12
    y = 60
    for i, (head, sub, fill, col) in enumerate(links):
        yy = y + i * (bh + gap)
        p.append(rect(bx, yy, bw, bh, fill=fill, stroke=col, sw=1.6))
        p.append(text(bx + 12, yy + bh / 2 + 5, head, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(bx + bw - 12, yy + bh / 2 + 5, sub, size=10, color=MUTED, anchor="end"))
        if i < len(links) - 1:
            p.append(arrow(bx + bw / 2, yy + bh, bx + bw / 2, yy + bh + gap, color=INK, sw=1.8))

    # бічні підписи «що готове»
    note_x = bx + bw + 30
    notes = ["такт RC, RAM сміття", "периферія мовчить",
             "PLL ✓, такт на повну", "RAM/глобальні ✓",
             "периферія налаштована", "ваш код ✓"]
    for i, n in enumerate(notes):
        yy = y + i * (bh + gap) + bh / 2 + 4
        p.append(text(note_x, yy, n, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "full-chain.svg"), W, H, *p,
           title="Уся reset-послідовність: кожна ланка готує наступну")


# ── setup-loop: ваш код усередині прихованого main() ──────────────────────────
# Ідея: фреймворковий main() — обгортка; setup() кличеться раз, loop() — у
# вічному циклі, керування щоразу ВИХОДИТЬ і повертається.

def fig_setup_loop():
    W, H = 700, 320
    p = []

    # зовнішня рамка — main() фреймворку
    ox, oy, ow, oh = 90, 60, 520, 210
    p.append(rect(ox, oy, ow, oh, fill="#f7f7fb", stroke=MUTED, sw=1.8))
    p.append(text(ox + 14, oy + 24, "main() фреймворку (прихований)", size=12, color=MUTED,
                  bold=True, anchor="start"))

    # setup() — раз
    su, sw_, sh = textbox(ox + 130, oy + 95, "setup()\n(раз)", size=12, bold=True,
                          color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    p.append(su)

    # loop() — у циклі
    lp, lw, lh = textbox(ox + 360, oy + 95, "loop()\n(знову й знову)", size=12, bold=True,
                         color=NEG, fill="#eef4ff", stroke=NEG, sw=1.6)
    p.append(arrow(ox + 130 + sw_ / 2, oy + 95, ox + 360 - lw / 2, oy + 95, color=INK, sw=1.8))
    p.append(lp)

    # дуга «вийшов — зайшов»: керування повертається до фреймворку
    ax, ay = ox + 360, oy + 95 + lh / 2
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (ax + lw / 2 - 20, ay, ax + 120, ay + 90, ax - 120, ay + 90, ax - lw / 2 + 20, ay,
                MUTED))
    p.append(text(ox + 360, ay + 86, "керування виходить і повертається", size=10,
                  color=MUTED, italic=True))

    p.append(text(W / 2, H - 16, "loop() — не вічний цикл усередині вас; його кличуть щоразу заново",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "setup-loop.svg"), W, H, *p,
           title="Ваш код — начинка чужого main()")


# ── strapping: при скиданні чіп читає IO0 і обирає режим ───────────────────────
# Ідея: рівень однієї ніжки в мить reset — це команда: висока → ваша програма,
# низька → режим завантаження.

def fig_strapping():
    W, H = 700, 280
    p = []
    cx = W / 2

    # момент скидання — читання IO0
    rd, rw, rh = textbox(cx, 80, "мить скидання:\nчитаємо рівень IO0", size=12, bold=True,
                         fill="#fdf6e3", stroke=POS, sw=1.8, pad=14)
    p.append(rd)

    # дві гілки
    hi, hw, hh = textbox(180, 200, "висока (1)\n→ ваша програма", size=11, bold=True,
                         color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.6)
    lo, lw, lh = textbox(W - 180, 200, "низька (0)\n→ режим завантаження", size=11, bold=True,
                         color=NEG, fill="#eef4ff", stroke=NEG, sw=1.6)
    p.append(arrow(cx - 30, 80 + rh / 2, 180, 200 - hh / 2, color=FIELD, sw=1.7))
    p.append(arrow(cx + 30, 80 + rh / 2, W - 180, 200 - lh / 2, color=NEG, sw=1.7))
    p.append(hi)
    p.append(lo)

    p.append(text(cx, H - 16, "рівень ніжки на старті — це команда чипу про режим",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "strapping.svg"), W, H, *p,
           title="Strapping: одна ніжка задає режим старту")


# ── autoprogram: два транзистори, перехресно зв'язані з DTR/RTS ────────────────
# Ідея: перехрест (емітер кожного — на ДРУГУ лінію) → транзистор реагує лише на
# РІЗНИЦЮ DTR і RTS; однаковий рівень (відкриття порту) тримає обидва закритими.

def fig_autoprogram():
    W, H = 720, 320
    p = []

    # дві керівні лінії зліва
    p.append(text(70, 90, "DTR", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(70, 170, "RTS", size=12, color=INK, bold=True, anchor="end"))
    p.append(line(74, 86, 200, 86, color=NEG, sw=1.8))
    p.append(line(74, 166, 200, 166, color=POS, sw=1.8))

    # два транзистори
    q2, q2w, q2h = textbox(280, 110, "Q2 → IO0", size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6)
    q1, q1w, q1h = textbox(280, 200, "Q1 → EN", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6)
    # перехрест: DTR керує Q2 (база), емітер Q2 на RTS; RTS керує Q1, емітер на DTR
    p.append(line(200, 86, 280 - q2w / 2, 110, color=NEG, sw=1.5))      # DTR → база Q2
    p.append(line(200, 166, 280 - q1w / 2, 200, color=POS, sw=1.5))     # RTS → база Q1
    p.append(line(280, 110 + q2h / 2, 240, 166, color=MUTED, sw=1.2, dash="4 3"))  # емітер Q2 → RTS
    p.append(line(280, 200 - q1h / 2, 240, 86, color=MUTED, sw=1.2, dash="4 3"))   # емітер Q1 → DTR
    p.append(q2)
    p.append(q1)

    # цілі праворуч
    io0, iw, ih = textbox(470, 110, "IO0\n(режим)", size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6)
    en, ew, eh = textbox(470, 200, "EN\n(скидання)", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6)
    p.append(arrow(280 + q2w / 2, 110, 470 - iw / 2, 110, color=NEG, sw=1.6))
    p.append(arrow(280 + q1w / 2, 200, 470 - ew / 2, 200, color=POS, sw=1.6))
    p.append(io0)
    p.append(en)

    # послідовність праворуч
    seq = ["DTR=0 RTS=1\nEN↓ (скидання)", "DTR=1 RTS=0\nIO0↓, EN↑", "відпустити\nобидві"]
    sx = 620
    for i, s in enumerate(seq):
        yy = 70 + i * 75
        b, bw, bh = textbox(sx, yy, s, size=9.5, fill=FILL, stroke=MUTED, sw=1.2)
        p.append(b)
        if i > 0:
            p.append(arrow(sx, yy - 75 + bh / 2 + 4, sx, yy - bh / 2 - 2, color=MUTED, sw=1.3))

    p.append(text(W / 2, H - 14, "DTR = RTS (відкриття порту) → обидва закриті, чіп біжить нормально",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "autoprogram.svg"), W, H, *p,
           title="Авто-прошивка: реакція лише на різницю DTR і RTS")


if __name__ == "__main__":
    fig_reset()
    fig_bootloader_job()
    fig_two_stage()
    fig_c_startup()
    fig_full_chain()
    fig_setup_loop()
    fig_strapping()
    fig_autoprogram()
    print("OK: figures written to", OUT)
