# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «MEMS-мікрофон».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (AUTHORING §2/§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── cross-section: серце — мембрана над продірявленою пластиною ──────────────
# Заряджена мембрана + нерухома продірявлена пластина = змінний конденсатор.
# Звук прогинає мембрану → зазор меншає → ємність росте. Дірки випускають повітря.
def fig_cross_section():
    W, H = 820, 400
    parts = []

    cx = W / 2
    top = 70

    # звукова хвиля згори
    for i, dx in enumerate((-120, 0, 120)):
        y = top + 6
        parts.append('<path d="M %.1f %.1f q 18 -16 36 0 q 18 16 36 0" fill="none" '
                     'stroke="%s" stroke-width="2"/>' % (cx + dx - 36, y, MUTED))
    parts.append(arrow(cx, top + 22, cx, top + 62, color=POS, sw=2.4))
    parts.append(text(cx, top + 6, "звук — коливання тиску повітря", size=13, bold=True, color=POS))

    # мембрана (прогнута вниз) — синя
    mL, mR = cx - 190, cx + 190
    my = top + 96
    parts.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="4"/>' % (mL, my, cx, my + 34, mR, my, NEG))
    parts.append(text(mR + 8, my - 2, "мембрана (заряджена)", size=12, bold=True,
                      color=NEG, anchor="start"))

    # нерухома пластина з дірками — сіра, нижче
    bpy = my + 78
    parts.append(rect(mL, bpy, mR - mL, 16, fill="#d7dde3", stroke="#8a8a8a", sw=2, rx=3))
    # дірки в пластині
    for i in range(9):
        hx = mL + 30 + i * ((mR - mL - 60) / 8)
        parts.append(circle(hx, bpy + 8, 4, fill=BG, stroke="#8a8a8a", sw=1.4))
    parts.append(text(mR + 8, bpy + 12, "нерухома пластина\n(з дірками)", size=12,
                      color="#6b7280", anchor="start"))
    parts.pop()
    parts.append(mtext(mR + 8, bpy + 6, "нерухома пластина\n(з дірками)", size=12,
                       color="#6b7280", anchor="start"))

    # зазор — це і є конденсатор
    parts.append(line(mL - 24, my + 34, mL - 24, bpy, color=FIELD, sw=1.6))
    parts.append(text(mL - 30, (my + 34 + bpy) / 2, "зазор d", size=12, bold=True,
                      color=FIELD, anchor="end"))
    parts.append(text(mL - 30, (my + 34 + bpy) / 2 + 18, "= конденсатор", size=11,
                      italic=True, color=FIELD, anchor="end"))

    # повітря виходить крізь дірки (маленькі стрілки вниз крізь пластину)
    for dx in (-70, 0, 70):
        parts.append(arrow(cx + dx, bpy - 10, cx + dx, bpy + 30, color=MUTED, sw=1.3))
    parts.append(text(cx, bpy + 48, "повітря тікає крізь дірки — пластина не заважає мембрані рухатися",
                      size=11, italic=True, color=MUTED))

    box, bw, bh = textbox(W / 2, H - 34,
                          "звук прогинає мембрану → зазор d меншає → ємність C росте (C ∝ 1/d)",
                          size=13, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/cross-section.svg", W, H, *parts,
           title="Серце MEMS-мікрофона: змінний конденсатор зі звуку")


# ── charge-bias: чому постійний ЗАРЯД, а не постійна напруга ─────────────────
# Q фіксований помпою заряду → V = Q/C. Рух міняє C → напруга йде за 1/C лінійно.
def fig_charge_bias():
    W, H = 820, 360
    parts = []

    # ліворуч: помпа заряду накачує фіксований заряд Q
    px, py = 90, 150
    parts.append(fitbox(px, py - 45, 170, 90,
                        "помпа заряду\nкладе фіксований\nзаряд Q (~10 В)", size=12.5,
                        fill="#e9f7ef", stroke=FIELD, sw=2, bold=True))
    parts.append(arrow(px + 170 + 6, py, px + 170 + 70, py, color=INK, sw=1.8))

    # центр: конденсатор мікрофона (мембрана + пластина)
    cxx = px + 170 + 76
    parts.append(line(cxx + 40, py - 34, cxx + 120, py - 34, color=NEG, sw=4))   # мембрана
    parts.append(line(cxx + 40, py + 6, cxx + 120, py + 6, color="#8a8a8a", sw=4))  # пластина
    parts.append(text(cxx + 80, py - 44, "Q = const", size=13, bold=True, color=FIELD))
    parts.append(text(cxx + 80, py + 30, "C змінюється\n(рух мембрани)", size=11, color=INK))
    parts.pop()
    parts.append(mtext(cxx + 80, py + 24, "C змінюється\n(рух мембрани)", size=11, color=INK))

    # праворуч: напруга V = Q/C
    parts.append(arrow(cxx + 130, py, cxx + 200, py, color=INK, sw=1.8))
    vx = cxx + 206
    parts.append(fitbox(vx, py - 45, 190, 90,
                        "напруга\nV = Q / C\n→ іде за рухом", size=14,
                        fill="#eaf0fd", stroke=NEG, sw=2, bold=True))

    box, bw, bh = textbox(W / 2, H - 34,
                          "заряд тримають сталим, тож напруга V = Q/C прямо повторює зміну ємності — сигнал",
                          size=13, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/charge-bias.svg", W, H, *parts,
           title="Хитрість: сталий заряд робить напругу дзеркалом руху")


# ── two-chips: MEMS + ASIC в одному корпусі, порт крізь плату ────────────────
# Механіка (перетворювач) і електроніка (ASIC) — два окремі кристали в корпусі;
# звук заходить крізь акустичний отвір; вихід — аналоговий або цифровий (PDM).
def fig_two_chips():
    W, H = 900, 400
    parts = []

    # корпус
    hx, hy, hw, hh = 120, 90, 500, 190
    parts.append(rect(hx, hy, hw, hh, fill="#eef2f7", stroke=INK, sw=2, rx=10))
    parts.append(text(hx + hw / 2, hy - 12, "один корпус (менший за рисове зерно)",
                      size=13, bold=True, color=MUTED))

    # плата під корпусом з акустичним отвором (нижній порт)
    py = hy + hh
    parts.append(rect(hx - 20, py, hw + 40, 26, fill="#c9a24a", stroke="#8a6b1e", sw=2, rx=3))
    portx = hx + 130
    parts.append(rect(portx - 12, py, 24, 26, fill=BG, stroke="#8a6b1e", sw=2, rx=2))
    parts.append(text(hx + hw / 2 + 40, py + 44, "друкована плата", size=11,
                      color="#6b7280", anchor="start"))
    # звук заходить знизу крізь отвір
    parts.append(arrow(portx, py + 54, portx, py + 6, color=POS, sw=2.4))
    parts.append(text(portx, py + 70, "звук у отвір", size=11, bold=True, color=POS))

    # MEMS-перетворювач (механіка) над портом
    mx = portx - 55
    parts.append(rect(mx, hy + 40, 130, 90, fill="#cfe0f5", stroke=NEG, sw=2, rx=6))
    parts.append(mtext(mx + 65, hy + 74, "MEMS-\nперетворювач\n(мембрана)", size=11.5,
                       bold=True, color=NEG))
    # зазор до порту
    parts.append(line(mx + 65, hy + 130, portx, py, color=MUTED, sw=1.2, dash="3,3"))

    # ASIC праворуч
    ax = hx + 300
    parts.append(rect(ax, hy + 40, 170, 90, fill="#e9f7ef", stroke=FIELD, sw=2, rx=6))
    parts.append(mtext(ax + 85, hy + 70, "ASIC:\nпомпа заряду +\nпідсилювач (+ АЦП)", size=11.5,
                       bold=True, color=FIELD))
    # зв'язок механіка → ASIC
    parts.append(arrow(mx + 130 + 4, hy + 85, ax - 4, hy + 85, color=INK, sw=1.8))
    parts.append(text((mx + 130 + ax) / 2, hy + 78, "Δ ємність", size=10.5,
                      italic=True, color=INK))

    # вихід — дві гілки
    parts.append(arrow(hx + hw + 4, hy + 70, hx + hw + 74, hy + 70, color=NEG, sw=2))
    parts.append(fitbox(hx + hw + 78, hy + 46, 190, 48,
                        "аналог: напруга\n(мВ/Па)", size=12, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(arrow(hx + hw + 4, hy + 140, hx + hw + 74, hy + 140, color=FIELD, sw=2))
    parts.append(fitbox(hx + hw + 78, hy + 116, 190, 48,
                        "цифра: бітів потік\n(PDM)", size=12, fill="#e9f7ef", stroke=FIELD, sw=1.8, bold=True))

    box, bw, bh = textbox(W / 2, H - 26,
                          "механіка й електроніка — два кристали в корпусі; вихід аналоговий АБО вже цифровий",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/two-chips.svg", W, H, *parts,
           title="Два кристали в одному корпусі: перетворювач і ASIC")


# ── specs: шкала гучності — шум, опора 94 дБ, перевантаження ─────────────────
# Вертикальна шкала SPL: EIN (шумова підлога) внизу, 94 дБ опора, AOP угорі.
# SNR = від підлоги до опори; динамічний діапазон = від підлоги до AOP.
def fig_specs():
    W, H = 780, 430
    parts = []

    ax = 300
    ytop, ybot = 80, 340
    parts.append(arrow(ax, ybot, ax, ytop - 8, color=INK, sw=1.8))
    parts.append(text(ax, ytop - 18, "гучність (дБ SPL)", size=12, bold=True))

    # три рівні на шкалі
    def lvl(frac):
        return ybot - frac * (ybot - ytop)

    y_floor = lvl(0.08)     # EIN
    y_ref = lvl(0.52)       # 94 дБ
    y_aop = lvl(0.92)       # AOP

    for y, lab in ((y_floor, ""), (y_ref, ""), (y_aop, "")):
        parts.append(line(ax - 8, y, ax + 8, y, color=INK, sw=2))

    # підписи рівнів праворуч
    parts.append(text(ax + 16, y_floor + 4, "шумова підлога (EIN) — тихіше давач не чує",
                      size=12, color=MUTED, anchor="start"))
    parts.append(text(ax + 16, y_ref + 4, "94 дБ SPL — опорний звук (1 Па, гучна розмова)",
                      size=12, bold=True, color=INK, anchor="start"))
    parts.append(text(ax + 16, y_aop + 4, "AOP — гучніше сигнал спотворюється (10% THD)",
                      size=12, color=POS, anchor="start"))

    # SNR: підлога → опора (ліворуч)
    parts.append(line(ax - 60, y_floor, ax - 60, y_ref, color=FIELD, sw=2))
    parts.append(line(ax - 66, y_floor, ax - 54, y_floor, color=FIELD, sw=2))
    parts.append(line(ax - 66, y_ref, ax - 54, y_ref, color=FIELD, sw=2))
    parts.append(text(ax - 72, (y_floor + y_ref) / 2, "SNR", size=13, bold=True,
                      color=FIELD, anchor="end"))
    parts.append(text(ax - 72, (y_floor + y_ref) / 2 + 18, "= 94 − EIN", size=10.5,
                      italic=True, color=FIELD, anchor="end"))

    # динамічний діапазон: підлога → AOP (далі ліворуч)
    parts.append(line(ax - 150, y_floor, ax - 150, y_aop, color=NEG, sw=2))
    parts.append(line(ax - 156, y_floor, ax - 144, y_floor, color=NEG, sw=2))
    parts.append(line(ax - 156, y_aop, ax - 144, y_aop, color=NEG, sw=2))
    parts.append(text(ax - 162, (y_floor + y_aop) / 2, "динамічний\nдіапазон", size=11.5,
                      bold=True, color=NEG, anchor="end"))
    parts.pop()
    parts.append(mtext(ax - 162, (y_floor + y_aop) / 2 - 6, "динамічний\nдіапазон", size=11.5,
                       bold=True, color=NEG, anchor="end"))

    box, bw, bh = textbox(W / 2, H - 34,
                          "три числа задають давач: як тихо чує (EIN), запас до опори (SNR), доки не спотворить (AOP)",
                          size=12.5, pad=12, fill=FILL)
    parts.append(box)

    render("img/specs.svg", W, H, *parts,
           title="Чути числами: шум, опора 94 дБ, перевантаження")


if __name__ == "__main__":
    fig_cross_section()
    fig_charge_bias()
    fig_two_chips()
    fig_specs()
    print("OK: cross-section, charge-bias, two-chips, specs")
