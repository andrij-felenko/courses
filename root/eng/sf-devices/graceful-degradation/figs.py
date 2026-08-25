# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── degradation-strategies: спектр відповіді, а не «все або нічого» ────────────
# Ідея: між повною роботою і крахом є сходинки — резерв, last-known-good,
# розумний дефолт, вимкнення лише ураженої функції, нижча якість. Крихкий
# дизайн стрибає одразу з вершини в крах.
def fig_degradation_strategies():
    W, H = 720, 360
    p = []
    # вертикальна вісь «повнота функції» згори вниз
    ax = 150
    top, bot = 70, 320
    p.append(arrow(ax, bot, ax, top - 6, color=INK, sw=1.8))
    p.append(text(ax - 12, top - 12, "повнота функції", size=11, color=INK, anchor="middle", bold=True))

    # сходинки деградації — від повної функції до безпечного стану
    steps = [
        (88,  "повна функція",            FIELD, "#eafaf0"),
        (135, "запасне джерело / канал",   FIELD, "#eafaf0"),
        (182, "last-known-good",           "#caa23a", "#fbf3da"),
        (229, "розумний дефолт",           "#caa23a", "#fbf3da"),
        (276, "лише уражену — вимкнути",    POS, "#fdecea"),
        (320, "безпечний стан / зупинка",   POS, "#fdecea"),
    ]
    bx = ax + 60
    prev = None
    for sy, lab, col, fill in steps:
        b, bw, bh = textbox(bx + 130, sy, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        # позначка рівня на осі
        p.append(circle(ax, sy, 3.4, fill=col, stroke=col, sw=1))
        p.append(line(ax, sy, bx + 130 - bw / 2, sy, color=col, sw=1.3, dash="3 3"))
        if prev is not None:
            # коротка стрілка-сходинка вниз між сусідніми рівнями
            p.append(arrow(bx + 130 - bw / 2 - 16, prev, bx + 130 - bw / 2 - 16, sy, color=MUTED, sw=1.4))
        p.append(b)
        prev = sy

    # крихкий дизайн — одна стрілка з вершини прямо в крах
    cx = W - 70
    p.append(line(cx, top + 4, cx, bot, color="#bbbbbb", sw=1.2, dash="2 4"))
    p.append(arrow(cx, top + 8, cx, bot - 2, color=POS, sw=2.6))
    p.append(mtext(cx + 4, top + 40, "крихкий\nдизайн:\nодин крок\nу крах",
                   size=10, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "degradation-strategies.svg"), W, H, *p,
           title="Деградація — це спектр, а не «все або нічого»")


# ── fallback-chain: ланцюг спроб із чесним прапорцем ──────────────────────────
# Ідея: основний → запасний → last-known-good; на кожній сходинці статус
# падає (OK → DEGRADED → FAILED) і деградація стає видимою. Бічна гілка
# «мовчазний дефолт» перекреслена — це тихий збій.
def fig_fallback_chain():
    W, H = 720, 380
    p = []
    midx = 250
    bw, bh = 220, 50
    ys = [70, 170, 270]
    labels = [
        ("основний давач", FIELD, "#eafaf0", "статус: OK"),
        ("запасний давач", "#caa23a", "#fbf3da", "статус: DEGRADED"),
        ("last-known-good із NVS", POS, "#fdecea", "статус: FAILED"),
    ]
    cx = midx
    for i, (lab, col, fill, status) in enumerate(labels):
        y = ys[i]
        p.append(fitbox(cx - bw / 2, y - bh / 2, bw, bh, lab, size=12, bold=True,
                        fill=fill, stroke=col, sw=1.8, color=INK))
        # статус праворуч
        p.append(text(cx + bw / 2 + 14, y - 4, status, size=11, color=col, anchor="start", bold=True))
        # «видимо: лог + індикатор + телеметрія» для деградованих рівнів
        if i > 0:
            p.append(text(cx + bw / 2 + 14, y + 14, "видимо: лог · LED · MQTT",
                          size=10, color=MUTED, anchor="start"))
        if i < len(labels) - 1:
            ny = ys[i + 1]
            p.append(arrow(cx, y + bh / 2, cx, ny - bh / 2, color=INK, sw=1.8))
            p.append(text(cx + 10, (y + bh / 2 + ny - bh / 2) / 2 + 4,
                          "відмова", size=10, color=POS, anchor="start"))

    # заборонена гілка: мовчазний дефолт
    fy = ys[0]
    fx = cx - bw / 2 - 70
    fb, fbw, fbh = textbox(fx, 330, "мовчазний\nдефолт", size=11, bold=True,
                           color="#999999", fill="#f3f3f3", stroke="#bbbbbb", sw=1.6)
    p.append(fb)
    # перекреслення (заборонено)
    p.append(line(fx - fbw / 2, 330 - fbh / 2, fx + fbw / 2, 330 + fbh / 2, color=POS, sw=2.4))
    p.append(line(fx - fbw / 2, 330 + fbh / 2, fx + fbw / 2, 330 - fbh / 2, color=POS, sw=2.4))
    p.append(text(fx, 330 + fbh / 2 + 18, "тихий збій — заборонено", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "fallback-chain.svg"), W, H, *p,
           title="Ланцюг fallback: статус падає, але деградація завжди видима")


# ── classify-fmea: деградовне проти критичного ────────────────────────────────
# Ідея: рішення за підсистемою — два кошики. Якщо часткова робота безпечна →
# деградовне (резерв/дефолт). Якщо без підсистеми робота небезпечна →
# критичне (безпечний стан / зупинка).
def fig_classify_fmea():
    W, H = 720, 320
    p = []
    # питання-розгалуження вгорі
    q, qw, qh = textbox(W / 2, 60, "Що буде, якщо ЦЕ відмовить?",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=2, pad=14)
    p.append(q)
    p.append(text(W / 2, 96, "робота без підсистеми лишається безпечною?", size=11, color=MUTED))

    # ліва гілка — деградовне
    lx = 200
    p.append(arrow(W / 2 - 40, 110, lx, 150, color=FIELD, sw=1.8))
    p.append(text((W / 2 - 40 + lx) / 2 - 30, 132, "так", size=12, color=FIELD, bold=True))
    lb, lbw, lbh = textbox(lx, 180, "ДЕГРАДОВНЕ", size=13, bold=True,
                           color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2, pad=12)
    p.append(lb)
    p.append(mtext(lx, 230, "резерв · last-known-good\nрозумний дефолт\nнижча якість",
                   size=11, color=INK))

    # права гілка — критичне
    rx = W - 200
    p.append(arrow(W / 2 + 40, 110, rx, 150, color=POS, sw=1.8))
    p.append(text((W / 2 + 40 + rx) / 2 + 30, 132, "ні", size=12, color=POS, bold=True))
    rb, rbw, rbh = textbox(rx, 180, "КРИТИЧНЕ", size=13, bold=True,
                           color=POS, fill="#fdecea", stroke=POS, sw=2, pad=12)
    p.append(rb)
    p.append(mtext(rx, 230, "безпечний стан\nабо зупинка\n(не «продовжуй із дефолтом»)",
                   size=11, color=INK))

    p.append(text(W / 2, H - 16,
                  "список складають при проєктуванні — не при першій аварії в полі",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "classify-fmea.svg"), W, H, *p,
           title="FMEA-сортування: деградовне чи критичне")


if __name__ == "__main__":
    fig_degradation_strategies()
    fig_fallback_chain()
    fig_classify_fmea()
    print("OK: figures written to", OUT)
