# -*- coding: utf-8 -*-
"""Фігури до оглядової статті «Родина MQ» (catalog/sensors/series/mq-family).
Вивід — ./img/*.svg. Запуск: python figs.py
Ці фігури РОДИННОГО рівня (родовід, карта варіантів, температурні цикли) —
навмисно НЕ дублюють фігур конкретного модуля (mq-gas: принцип, розводка, крива)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WARM = "#d6a419"   # «гаряче» — нагрівач / SnO2


# ── 1. Родовід: винахід Тагучі (TGS) → SnO2-принцип → китайська родина MQ ──────
def fig_lineage():
    W, H = 860, 430
    f = []
    f.append(text(430, 30, "Звідки взялася родина MQ: одна ідея, багато виробників", size=16, bold=True))

    # Вузол 1 — винахід
    b1, w1, h1 = textbox(160, 130, "1968 — Наойосі Тагучі\n(Японія): перший\nсерійний давач газу\nна SnO₂ (TGS,\nфірма Figaro)",
                         size=12, pad=11, fill="#eef4ff", stroke=NEG, color=NEG, bold=False)
    f.append(b1)

    # Вузол 2 — фізичний принцип (спільний для всіх)
    b2, w2, h2 = textbox(430, 130, "Спільний принцип:\nнагріта плівка SnO₂,\nчий опір падає\nвід горючого газу",
                         size=12, pad=11, fill="#fff8e6", stroke=WARM, bold=True)
    f.append(b2)

    # Вузол 3 — китайська родина MQ
    b3, w3, h3 = textbox(710, 130, "Китайські MQ\n(Hanwei, Zhengzhou;\nнині масово Winsen):\nдешева родина\nна тому ж принципі",
                         size=12, pad=11, fill="#eafaf0", stroke=FIELD, color="#1e7a46")
    f.append(b3)

    # стрілки між вузлами
    f.append(arrow(160 + w1 / 2, 130, 430 - w2 / 2, 130, color=INK, sw=2))
    f.append(arrow(430 + w2 / 2, 130, 710 - w3 / 2, 130, color=INK, sw=2))
    f.append(text(295, 112, "той самий", size=10, color=MUTED))
    f.append(text(295, 126, "фізичний ефект", size=10, color=MUTED))
    f.append(text(570, 112, "здешевили", size=10, color=MUTED))
    f.append(text(570, 126, "й розмножили", size=10, color=MUTED))

    # нижня рамка — головний висновок
    b, bw, bh = textbox(430, 300,
                        "«MQ» — лише префікс серії, не абревіатура-слово. Номер після нього (MQ-2, MQ-7, MQ-135)\n"
                        "каже, до якого газу елемент найчутливіший. Плата, обв'язка й код у варіантів майже однакові —\n"
                        "різниться склад чутливого шару й температура нагрівача.",
                        size=12, pad=12, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "mq-lineage.svg"), W, H, *f)


# ── 2. Карта варіантів: яку букву під що брати (дві осі — газ і режим) ─────────
def fig_variants():
    W, H = 900, 560
    f = []
    f.append(text(450, 30, "Карта родини MQ: яку букву обрати під свій газ", size=16, bold=True))

    # заголовки колонок
    col_x = 40
    name_w = 92
    gas_w = 430
    mode_x = col_x + name_w + gas_w + 16
    y0 = 66
    rh = 44

    f.append(text(col_x + name_w / 2, y0 - 8, "варіант", size=12, bold=True, color=MUTED))
    f.append(text(col_x + name_w + gas_w / 2, y0 - 8, "до чого найчутливіший", size=12, bold=True, color=MUTED))
    f.append(text(mode_x + 120, y0 - 8, "нагрівач", size=12, bold=True, color=MUTED))

    rows = [
        ("MQ-2",   "дим, зріджений газ (LPG), метан, пропан, водень, спирт — універсал", "стало", FIELD),
        ("MQ-3",   "пари спирту (алкотестери); навмисне глухий до бензину й диму",       "стало", FIELD),
        ("MQ-4",   "метан, природний/стиснений газ (CNG)",                                "стало", FIELD),
        ("MQ-5",   "зріджений (LPG) і природний газ — побутовий витік",                   "стало", FIELD),
        ("MQ-6",   "пропан-бутан, LPG",                                                   "стало", FIELD),
        ("MQ-7",   "чадний газ (CO)",                                                     "цикли", POS),
        ("MQ-8",   "водень (H₂)",                                                         "стало", FIELD),
        ("MQ-9",   "чадний газ (CO) + горючі гази",                                       "цикли", POS),
        ("MQ-135", "«якість повітря»: аміак, оксиди азоту, бензол, дим — широкий, розмитий", "стало", FIELD),
    ]

    for i, (name, gas, mode, mcol) in enumerate(rows):
        y = y0 + i * rh
        bg = "#f7f9fb" if i % 2 == 0 else "#eef2f6"
        f.append(rect(col_x, y, name_w + gas_w + 246, rh - 6, fill=bg, stroke="none", sw=0, rx=5))
        # назва
        f.append(text(col_x + name_w / 2, y + (rh - 6) / 2 + 5, name, size=13.5, bold=True, color=INK))
        # газ
        f.append(text(col_x + name_w + 10, y + (rh - 6) / 2 + 5, gas, size=11.5, color=INK, anchor="start"))
        # режим — таблетка
        pill_cx = mode_x + 120
        pill_w = 96
        pfill = "#fdecea" if mode == "цикли" else "#eafaf0"
        f.append(rect(pill_cx - pill_w / 2, y + 5, pill_w, rh - 16, fill=pfill, stroke=mcol, sw=1.4, rx=12))
        lab = "два цикли t°" if mode == "цикли" else "постійні 5 В"
        f.append(text(pill_cx, y + (rh - 6) / 2 + 5, lab, size=10.5, bold=True, color=mcol))

    # підсумкова рамка внизу (двоколірний зміст пояснено)
    yb = y0 + len(rows) * rh + 14
    b, bw, bh = textbox(450, yb + 26,
                        "Зелене — увімкнув на 5 В і читай. Червоне (MQ-7, MQ-9) — нагрівач треба гойдати між\n"
                        "гарячою й холодною фазою за розкладом: чадний газ читається лише в холоднішій.\n"
                        "MQ-135 — не «вимірювач CO₂»: без калібрування це розмита суміш газів.",
                        size=12, pad=12, fill="#fff8e6", stroke=WARM)
    f.append(b)

    render(os.path.join(IMG, "mq-variants.svg"), W, H, *f)


# ── 3. Температурні цикли MQ-7/MQ-9: напруга нагрівача vs час, дві фази ────────
def fig_cycle():
    W, H = 820, 440
    f = []
    f.append(text(410, 30, "Чому MQ-7 і MQ-9 не просто вмикають: два цикли нагрівача", size=15.5, bold=True))

    # осі
    ox, oy = 90, 300
    ax_w, ax_h = 620, 210
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))          # X (час)
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))          # Y (напруга нагрівача)
    f.append(text(ox + ax_w / 2, oy + 54, "час (цикл повторюється безкінечно)", size=11.5, color=MUTED))
    f.append(text(ox - 60, oy - ax_h - 6, "Uнагр", size=12, color=MUTED, bold=True, anchor="start"))

    # рівні напруги на Y
    y_hi = oy - ax_h + 24     # 5.0 В
    y_lo = oy - 46            # 1.4 В
    f.append(line(ox - 5, y_hi, ox, y_hi, color=INK, sw=1.4))
    f.append(text(ox - 12, y_hi + 4, "5.0 В", size=10.5, color=POS, bold=True, anchor="end"))
    f.append(line(ox - 5, y_lo, ox, y_lo, color=INK, sw=1.4))
    f.append(text(ox - 12, y_lo + 4, "1.4 В", size=10.5, color=NEG, bold=True, anchor="end"))

    # ділянки за часом: 60 с гаряче, 90 с холодне, тоді знову
    # масштаб: 150 с на ~ 0.82*ax_w, лишаємо хвіст на повтор
    def tx(t):   # t у секундах від 0
        return ox + (t / 300.0) * ax_w
    seg = [(0, 60, y_hi, POS), (60, 150, y_lo, NEG), (150, 210, y_hi, POS), (210, 300, y_lo, NEG)]
    prev = None
    for (t0, t1, yv, col) in seg:
        f.append(line(tx(t0), yv, tx(t1), yv, color=col, sw=3))
        if prev is not None:
            f.append(line(tx(t0), prev, tx(t0), yv, color=INK, sw=1.6, dash="4 3"))
        prev = yv

    # підписи фаз (перший цикл)
    f.append(text((tx(0) + tx(60)) / 2, y_hi - 12, "60 с при 5 В", size=10.5, color=POS, bold=True))
    f.append(text((tx(0) + tx(60)) / 2, oy - ax_h - 2, "гаряча фаза", size=10, color=POS))
    f.append(text((tx(60) + tx(150)) / 2, y_lo - 12, "90 с при 1.4 В", size=10.5, color=NEG, bold=True))

    # де читати
    f.append(circle(tx(60), y_hi, 5, fill="#fff", stroke=POS, sw=2))
    f.append(text(tx(60), y_hi + 20, "тут читаєш:\nгорючий газ", size=9.5, color=POS))
    f.append(circle(tx(150), y_lo, 5, fill="#fff", stroke=NEG, sw=2))
    f.append(text(tx(150), y_lo + 22, "тут читаєш:\nчадний газ (CO)", size=9.5, color=NEG))

    # рамка-висновок
    b, bw, bh = textbox(410, 388,
                        "Гаряча фаза «чистить» поверхню й ловить горючі гази; у холоднішій фазі краще читається CO.\n"
                        "Тому просто подати 5 В і читати AO — замало: нагрівачем треба керувати за розкладом.",
                        size=11.5, pad=10, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "mq-cycle.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lineage()
    fig_variants()
    fig_cycle()
    print("OK: mq-lineage.svg, mq-variants.svg, mq-cycle.svg")
