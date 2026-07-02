# -*- coding: utf-8 -*-
# Фігури для вставки math-breakeven-volume.md (точка беззбитковості з кількома змінними).
# Імена файлів навмисно унікальні (be-*), щоб не збігтися з figs.py / figs-d.py.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MCU  = "#2457d6"   # варіант A (типово МК)
FPGA = "#1f8a3b"   # варіант B (типово FPGA)
WARM = "#c0392b"   # точка беззбитковості / вирок


# ── be-total: з чого насправді складається кожна пряма вартості ────────────────
# Ідея: NRE — не одне число, а стос доданків (праця, інструмент, ризик переробки);
# ціна за штуку — теж стос (чип, обв'язка, плата, монтаж, амортизація інструменту).
# Показуємо два «стовпчики-стоси» + як вони перетворюються на дві прямі.

def fig_total():
    W, H = 780, 470
    p = [text(W/2, 30, "Що насправді ховається у двох числах моделі", size=17, bold=True),
         text(W/2, 50, "NRE — стос разових витрат; ціна за штуку — стос повторюваних",
              size=11.5, color=MUTED, italic=True)]

    # ── лівий блок: розклад NRE (разове) ──
    lx, lw = 40, 340
    p.append(text(lx + lw/2, 84, "NRE — платиться ОДИН раз", size=13, bold=True))
    nre_rows = [
        ("праця інженера (години × ставка)",      MCU,  FPGA),
        ("освоєння потоку / інструменту",         None, FPGA),
        ("макет, плати-прототипи, налагодження",  MCU,  FPGA),
        ("ліцензії / інструмент (та частка, що",  None, FPGA),
        ("списується на цей проєкт)",             None, None),
        ("ризик переробки: P(fail) × вартість",   MCU,  FPGA),
    ]
    ry, rh = 98, 40
    for txt, a, b in nre_rows:
        p.append(rect(lx, ry, lw, rh, fill="#fafafa", stroke=INK, sw=1.0))
        p.append(fitbox(lx, ry, lw - 70, rh, txt, size=10, pad=7,
                        fill="none", stroke="none"))
        # позначки, кому доданок помітний
        if a: p.append(text(lx + lw - 52, ry + rh/2 + 4, "A", size=11, color=MCU, bold=True))
        if b: p.append(text(lx + lw - 26, ry + rh/2 + 4, "B", size=11, color=FPGA, bold=True))
        ry += rh
    p.append(fitbox(lx, ry + 6, lw, 34,
                    "Сума → NRE_A (низька) і NRE_B (висока)", size=11, pad=8,
                    fill="#eef0f4", stroke=INK, sw=1.2, bold=True))

    # ── правий блок: розклад ціни за штуку (повторюване) ──
    rx0, rw = 400, 340
    p.append(text(rx0 + rw/2, 84, "Ціна за штуку — на КОЖЕН виріб", size=13, bold=True))
    unit_rows = [
        ("активний чип (МК або FPGA)",             MCU,  FPGA),
        ("зовнішня флеш під бітстрім",             None, FPGA),
        ("живлення: кілька напруг + стабілізатори", MCU, FPGA),
        ("площа плати, шари, розведення",          MCU,  FPGA),
        ("монтаж і тест на кожен виріб",           MCU,  FPGA),
        ("амортизація інструменту / Q (спадає!)",  MCU,  FPGA),
    ]
    uy = 98
    for txt, a, b in unit_rows:
        p.append(rect(rx0, uy, rw, rh, fill="#fafafa", stroke=INK, sw=1.0))
        p.append(fitbox(rx0, uy, rw - 70, rh, txt, size=10, pad=7,
                        fill="none", stroke="none"))
        if a: p.append(text(rx0 + rw - 52, uy + rh/2 + 4, "A", size=11, color=MCU, bold=True))
        if b: p.append(text(rx0 + rw - 26, uy + rh/2 + 4, "B", size=11, color=FPGA, bold=True))
        uy += rh
    p.append(fitbox(rx0, uy + 6, rw, 34,
                    "Сума → ціна_A (вища) і ціна_B (нижча на обсязі)", size=11, pad=8,
                    fill="#eef0f4", stroke=INK, sw=1.2, bold=True))

    y = max(ry, uy) + 46
    box = fitbox(40, y, W - 80, 66,
                 "Кожна пряма Вартість(Q) = NRE + ціна_за_шт · Q — це сума двох стосів.\n"
                 "Рахувати треба СТОСИ, а не вгадувати два числа — тоді точка беззбитковості чесна.",
                 size=12, pad=10, fill="#f4f7f4", stroke=FPGA, sw=1.7, bold=True)
    p.append(box)
    render(os.path.join(OUT, "be-total.svg"), W, y + 82, *p)


# ── be-map: числова вісь тиражу — три зони й межовий випадок «вирок» ────────────
# Ідея: щойно точка порахована, рішення — це readout за віссю Q. І окремо — коли
# знаменник/чисельник дають від'ємну точку: перетину в дійсності немає, вирок.

def fig_map():
    W, H = 780, 430
    p = [text(W/2, 30, "Точка беззбитковості як шкала рішення", size=17, bold=True),
         text(W/2, 50, "порахував Q* — далі просто дивишся, з якого боку твій тираж",
              size=11.5, color=MUTED, italic=True)]

    # ── верхня вісь: нормальний випадок, є додатна точка ──
    ax, aw, ay = 70, 640, 120
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=2))
    p.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=2))
    p.append(text(ax + aw, ay + 22, "тираж Q ->", size=11, color=MUTED, anchor="end", italic=True))
    p.append(text(ax - 8, ay + 5, "0", size=11, color=MUTED, anchor="end"))

    qx = ax + aw * 0.52          # позиція Q*
    p.append(line(qx, ay - 46, qx, ay + 14, color=WARM, sw=2, dash="4 3"))
    p.append(circle(qx, ay, 6, fill=WARM, stroke=WARM, sw=1.5))
    p.append(mtext(qx, ay - 54, ["Q* = (NRE_B − NRE_A)", "/ (ціна_A − ціна_B)"],
                   size=10.5, color=WARM, bold=True))

    # зони
    p.append(fitbox(ax + 6, ay + 30, (qx - ax) - 12, 42,
                    "Q < Q*: дешевше A\n(розробку B не розкласти)",
                    size=10.5, pad=6, fill="#eef2fd", stroke=MCU, sw=1.4, bold=True, color=MCU))
    p.append(fitbox(qx + 6, ay + 30, (ax + aw - qx) - 12, 42,
                    "Q > Q*: дешевше B\n(висока NRE окупилась дешевою одиницею)",
                    size=10.5, pad=6, fill="#eef7ee", stroke=FPGA, sw=1.4, bold=True, color=FPGA))

    # ── нижня вісь: межовий випадок — від'ємна точка = вирок ──
    by = ay + 150
    p.append(text(W/2, by - 34, "Межовий випадок: точка виходить від'ємною",
                  size=13, bold=True, color=WARM))
    p.append(line(ax, by, ax + aw, by, color=INK, sw=2))
    p.append(arrow(ax, by, ax + aw, by, color=INK, sw=2))
    p.append(text(ax - 8, by + 5, "0", size=11, color=MUTED, anchor="end"))
    p.append(text(ax + aw, by + 22, "тираж Q ->", size=11, color=MUTED, anchor="end", italic=True))
    # «точка» ліворуч від нуля — недосяжна для реального Q≥0
    negx = ax - 34
    p.append(line(negx, by - 30, negx, by + 10, color=MUTED, sw=1.6, dash="3 3"))
    p.append(circle(negx, by, 5, fill="#ffffff", stroke=MUTED, sw=1.6))
    p.append(text(negx, by - 36, "Q* < 0", size=10.5, color=MUTED, bold=True))
    p.append(fitbox(ax + 6, by + 30, aw - 12, 48,
                    "Уся дійсна вісь Q ≥ 0 лежить по ОДИН бік точки: один варіант дорожчий\n"
                    "і по NRE, і по одиниці. Він програє на БУДЬ-ЯКОМУ тиражі — рахувати далі нема сенсу.",
                    size=11, pad=7, fill="#fdecea", stroke=WARM, sw=1.6, bold=True, color=WARM))

    render(os.path.join(OUT, "be-map.svg"), W, by + 92, *p)


if __name__ == "__main__":
    fig_total()
    fig_map()
    print("figs-math-breakeven done")
