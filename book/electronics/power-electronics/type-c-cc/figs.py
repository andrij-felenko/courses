# -*- coding: utf-8 -*-
"""Фігури теми «Type-C без PD» та вставки comp-cc-resistors (резистори CC у USB-C).
Імпортує svgkit зі scripts/ (НЕ копіює). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігури статті (slug-нейминг, без номерів) ───────────────────────────────

def fig_cc_divider():
    """Дільник Rp/Rd на лінії CC: джерело тягне вгору, пристрій — вниз 5.1 кОм."""
    W, H = 720, 320
    parts = []
    # рамки сторін
    sx, sy, sw_, sh = 70, 70, 180, 210
    parts.append(rect(sx, sy, sw_, sh, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(sx + sw_ / 2, sy + 24, "джерело (дає)", size=13, bold=True, color=POS))
    dx, dy = 480, 70
    parts.append(rect(dx, dy, sw_, sh, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(dx + sw_ / 2, dy + 24, "пристрій (бере)", size=13, bold=True, color=FIELD))

    # лінія CC між сторонами
    yc = 175
    parts.append(line(sx + sw_, yc, dx, yc, color=INK, sw=2.2))
    parts.append(text((sx + sw_ + dx) / 2, yc - 14, "лінія CC", size=13, bold=True, color=INK))
    parts.append(text((sx + sw_ + dx) / 2, yc + 22,
                      "V(CC) = Vоп · Rd/(Rp+Rd)", size=12, color=MUTED))

    # Rp вгору всередині джерела
    parts.append(line(sx + sw_ - 60, yc, sx + sw_ - 60, sy + 52, color=POS, sw=1.8))
    parts.append(line(sx + sw_ - 60, yc, sx + sw_, yc, color=INK, sw=2.2))
    b, w, h = textbox(sx + sw_ - 60, sy + 70, "Rp\n(вгору)", size=12, fill="#fdecea", stroke=POS)
    parts.append(b)
    parts.append(text(sx + sw_ - 60, sy + 44, "Vоп", size=11, color=POS))

    # Rd вниз усередині пристрою
    parts.append(line(dx + 60, yc, dx + 60, dy + sh - 52, color=FIELD, sw=1.8))
    parts.append(line(dx, yc, dx + 60, yc, color=INK, sw=2.2))
    b, w, h = textbox(dx + 60, dy + sh - 34, "Rd 5.1 кОм\n(вниз)", size=12, fill="#eaf3ea", stroke=FIELD)
    parts.append(b)
    parts.append(text(dx + 60, dy + sh - 6, "земля", size=10, color=MUTED))

    box, w, h = textbox(W / 2, 296,
                        ["Пристрій просто міряє цю напругу — і дізнається дозволений струм.",
                         "Без Rd лінія висить, VBUS лишається вимкненим."],
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-divider.svg"), W, H, *parts,
           title="Дільник на лінії CC: Rp на джерелі, Rd на пристрої")


def fig_cc_levels():
    """Три значення Rp кодують три рівні дозволеного струму через напругу на CC."""
    W, H = 720, 300
    parts = []
    rows = [
        ("56 кОм", "≈0.41 В", "0.5 / 0.9 А", "#e3f0fb"),
        ("22 кОм", "≈0.92 В", "1.5 А", "#fdf2e0"),
        ("10 кОм", "≈1.68 В", "3.0 А  (15 Вт)", "#fdecea"),
    ]
    # заголовки колонок
    cx = [150, 360, 560]
    hdr = ["Rp на джерелі", "напруга на CC", "дозволено пристрою"]
    y0 = 70
    for x, htxt in zip(cx, hdr):
        parts.append(text(x, y0, htxt, size=12.5, bold=True, color=INK))
    # рядки
    for i, (rp, v, cur, col) in enumerate(rows):
        y = y0 + 36 + i * 56
        parts.append(rect(70, y - 22, 580, 44, fill=col, stroke=LINE, sw=1.2))
        parts.append(text(cx[0], y + 4, rp, size=13, bold=True))
        parts.append(text(cx[1], y + 4, v, size=13))
        parts.append(text(cx[2], y + 4, cur, size=13, bold=True))
    box, w, h = textbox(W / 2, 266,
                        ["Менший Rp → сильніша підтяжка → вища напруга на CC → більший струм.",
                         "Пристрій не просить — він читає."],
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-levels.svg"), W, H, *parts,
           title="Джерело вибирає Rp — і тим оголошує дозволений струм")


def fig_cc_roles():
    """Хто яку підтяжку вішає — той і визначає роль; DRP чергує."""
    W, H = 720, 300
    parts = []
    cards = [
        (60, "Rp вгору", "джерело\n(DFP, дає)", "#fdecea", POS),
        (290, "Rd вниз", "пристрій\n(UFP, бере)", "#eaf3ea", FIELD),
        (520, "Rp ⇄ Rd", "дворольовий\n(DRP, чергує)", "#eef1f4", MUTED),
    ]
    cw, ch, cy = 150, 130, 80
    for x, top, role, col, stroke in cards:
        parts.append(rect(x, cy, cw, ch, fill=col, stroke=stroke, sw=2))
        parts.append(text(x + cw / 2, cy + 34, top, size=14, bold=True, color=stroke))
        parts.append(mtext(x + cw / 2, cy + 70, role, size=12.5, color=INK))
    box, w, h = textbox(W / 2, 258,
                        ["Роль не зашита в залізо: той самий роз'єм павербанка вранці заряджає",
                         "телефон, а ввечері заряджається сам — її задає резистор у кожній парі."],
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-roles.svg"), W, H, *parts,
           title="Підтяжка задає роль у парі")


def fig_cc_orientation():
    """Два піни CC; з'єднаний наскрізь лише один — за ним система впізнає бік."""
    W, H = 720, 320
    parts = []
    sx, sy, sw_, sh = 70, 70, 170, 200
    parts.append(rect(sx, sy, sw_, sh, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(sx + sw_ / 2, sy + 24, "джерело", size=13, bold=True, color=POS))
    dx = 480
    parts.append(rect(dx, sy, sw_, sh, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(dx + sw_ / 2, sy + 24, "пристрій", size=13, bold=True, color=FIELD))

    # CC1 — з'єднаний наскрізь
    y1 = 140
    parts.append(line(sx + sw_, y1, dx, y1, color=INK, sw=2.2))
    parts.append(text((sx + sw_ + dx) / 2, y1 - 12, "CC1 — з'єднаний наскрізь (несе Rp/Rd)", size=11, color=INK))
    # CC2 — обірваний у штекері
    y2 = 215
    parts.append(line(sx + sw_, y2, (sx + sw_ + dx) / 2 - 18, y2, color=MUTED, sw=2, dash="5 4"))
    parts.append(line((sx + sw_ + dx) / 2 + 18, y2, dx, y2, color=MUTED, sw=2, dash="5 4"))
    parts.append(text((sx + sw_ + dx) / 2, y2 + 4, "✕", size=15, bold=True, color=POS))
    parts.append(text((sx + sw_ + dx) / 2, y2 - 12, "CC2 — розірваний → стане VCONN", size=11, color=MUTED))

    box, w, h = textbox(W / 2, 296,
                        ["За тим, який із двох CC «ожив», система впізнає бік штекера й скеровує дані.",
                         "Живлення (VBUS, земля) симетричне й до повороту байдуже."],
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-orientation.svg"), W, H, *parts,
           title="Два піни CC: котрий з'єднаний — той і показує орієнтацію")


def fig_cc_emarker():
    """Незадіяний пін стає VCONN і живить e-marker; без нього стеля 3 А."""
    W, H = 720, 300
    parts = []
    # кабель посередині
    kx, ky, kw, kh = 250, 90, 220, 110
    parts.append(rect(kx, ky, kw, kh, fill="#eef1f4", stroke=MUTED, sw=2))
    parts.append(text(kx + kw / 2, ky + 24, "кабель", size=13, bold=True, color=MUTED))
    b, w, h = textbox(kx + kw / 2, ky + 70, "e-marker\n(чип у штекері)", size=12, fill=BG, stroke=INK)
    parts.append(b)
    # VCONN зліва
    parts.append(arrow(120, 145, kx, 145, color=FIELD))
    parts.append(text(60, 140, "VCONN", size=12.5, bold=True, color=FIELD))
    parts.append(text(60, 158, "(2-й CC)", size=11, color=MUTED))
    # доповідь справа
    parts.append(arrow(kx + kw, 145, 660, 145, color=INK))
    parts.append(mtext(640, 130, "тримає\n3 чи 5 А\nдовжина,\nшвидкість", size=11, color=INK))
    box, w, h = textbox(W / 2, 258,
                        ["Без e-marker система не ризикне пустити 5 А — обмежиться 3.",
                         "Звідси буденне «чому цим шнуром заряджає повільно»."],
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-emarker.svg"), W, H, *parts,
           title="Незадіяний пін CC стає VCONN — живить чип кабелю")


def fig_cc_minimal_sink():
    """Рецепт найпростішого 5-В sink і дзеркальні граблі."""
    W, H = 720, 330
    parts = []
    # ліва колонка — рецепт
    parts.append(text(195, 64, "Рецепт", size=14, bold=True, color=FIELD))
    steps = [
        "Rd 5.1 кОм: CC1 → земля",
        "Rd 5.1 кОм: CC2 → земля",
        "VBUS → ваші 5 В",
        "(опц.) CC → АЦП: дізнатись струм",
        "не брати більше дозволеного",
    ]
    for i, s in enumerate(steps):
        y = 92 + i * 40
        parts.append(rect(40, y - 18, 310, 32, fill="#eaf3ea", stroke=FIELD, sw=1.2))
        parts.append(text(195, y + 3, s, size=12))
    # права колонка — граблі
    parts.append(text(545, 64, "Граблі", size=14, bold=True, color=POS))
    traps = [
        "забув Rd → нема VBUS",
        "Rd лише на одному CC → один бік",
        "4.7 кОм замість 5.1 → ігнор",
        "3 А там, де порт дає 0.9 → просадка",
    ]
    for i, s in enumerate(traps):
        y = 92 + i * 40
        parts.append(rect(390, y - 18, 310, 32, fill="#fdecea", stroke=POS, sw=1.2))
        parts.append(text(545, y + 3, s, size=11.5))
    box, w, h = textbox(W / 2, 308,
                        "У USB-C навіть «нічого не робити» означає поставити правильні резистори.",
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-minimal-sink.svg"), W, H, *parts,
           title="Найпростіший sink: два резистори — і дзеркальні граблі")


# ── Фігури вставки comp-cc-resistors ────────────────────────────────────────


def fig_decode():
    """Шкала напруги на CC, яку міряє sink, з трьома порогами декодування."""
    W, H = 720, 300
    parts = []
    # вісь
    x0, x1, y = 90, 640, 150
    vmax = 1.8
    def vx(v):
        return x0 + (x1 - x0) * (v / vmax)
    parts.append(line(x0, y, x1 + 14, y, color=INK, sw=2))
    parts.append(arrow(x1, y, x1 + 22, y, color=INK))
    # зони
    zones = [
        (0.00, 0.20, "#eceff1", "нема\nпристрою"),
        (0.20, 0.66, "#e3f0fb", "Default\n0.5 / 0.9 A"),
        (0.66, 1.23, "#fdf2e0", "1.5 A"),
        (1.23, vmax, "#fdecea", "3.0 A\n(15 Вт)"),
    ]
    for a, b, col, lab in zones:
        xa, xb = vx(a), vx(b)
        parts.append(rect(xa, y - 30, xb - xa, 30, fill=col, stroke=LINE, sw=1.2, rx=0))
        parts.append(mtext((xa + xb) / 2, y - 46, lab, size=12, color=INK))
    # пороги
    for v in (0.20, 0.66, 1.23):
        parts.append(line(vx(v), y - 34, vx(v), y + 10, color=POS, sw=1.8, dash="4 3"))
        parts.append(text(vx(v), y + 26, ("%.2f В" % v), size=12, color=POS, bold=True))
    parts.append(text(x1 + 22, y + 26, "→ В", size=12, color=MUTED))
    # підпис осі
    parts.append(text((x0 + x1) / 2, y + 64,
                      "напруга на активному CC (вхід sink, через його Rd)", size=12, color=MUTED))
    # пояснення
    box, w, h = textbox(W / 2, 250,
                        ["Sink читає одну напругу й потрапляє в одну зону.",
                         "Жодних команд: рівень уже стоїть на лінії."],
                        size=12.5, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-decode.svg"), W, H, *parts,
           title="Що бачить пристрій на лінії CC")


def fig_pins():
    """Два піни CC: активний несе дільник, другий стає VCONN; розрізнення Rd / Ra."""
    W, H = 720, 340
    parts = []
    # рамка sink
    sx, sy, sw_, sh = 470, 70, 200, 220
    parts.append(rect(sx, sy, sw_, sh, fill="#f0f7f0", stroke=FIELD, sw=2))
    parts.append(text(sx + sw_ / 2, sy + 24, "пристрій (sink)", size=13, bold=True, color=FIELD))
    # рамка source
    px, py = 50, 70
    parts.append(rect(px, py, 170, sh, fill="#fbf3f3", stroke=POS, sw=2))
    parts.append(text(px + 85, py + 24, "джерело (source)", size=13, bold=True, color=POS))

    # CC1 — активна лінія: Rp ... Rd
    yc1 = 150
    parts.append(line(px + 170, yc1, sx, yc1, color=INK, sw=2))
    parts.append(text((px + 170 + sx) / 2, yc1 - 12, "CC1  (з'єднана наскрізь у штекері)", size=11, color=INK))
    b, w, h = textbox(px + 130, yc1, "Rp", size=12, fill="#fdecea", stroke=POS); parts.append(b)
    b, w, h = textbox(sx + 40, yc1, "Rd 5.1k", size=12, fill="#eaf3ea", stroke=FIELD); parts.append(b)

    # CC2 — другий пін: стає VCONN; у кабелі — Ra
    yc2 = 245
    parts.append(line(px + 170, yc2, sx, yc2, color=MUTED, sw=2, dash="5 4"))
    parts.append(text((px + 170 + sx) / 2, yc2 - 12, "CC2  →  VCONN (живить кабель)", size=11, color=MUTED))
    b, w, h = textbox(sx + 48, yc2, "Ra 0.8–1.2k\n(e-marker)", size=11, fill="#eef1f4", stroke=MUTED); parts.append(b)

    # підказка про розрізнення
    box, w, h = textbox(W / 2, 318,
                        "Source розрізняє за опором: Rd (5.1k) = пристрій · Ra (0.8–1.2k) = кабель · нічого = відкрито.",
                        size=12, fill="#f4f6f8")
    parts.append(box)
    render(os.path.join(IMG, "cc-pins.svg"), W, H, *parts,
           title="Два піни CC: котрий ожив — і ким він став")


if __name__ == "__main__":
    # стаття
    fig_cc_divider()
    fig_cc_levels()
    fig_cc_roles()
    fig_cc_orientation()
    fig_cc_emarker()
    fig_cc_minimal_sink()
    # вставка
    fig_decode()
    fig_pins()
    print("done")
