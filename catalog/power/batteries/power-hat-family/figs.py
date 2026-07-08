# -*- coding: utf-8 -*-
"""Фігури до статті «Родина живильних HAT-ів Waveshare (SW6106)».
Дві SVG: (1) внутрішня архітектура SW6106 — спільне серце родини;
(2) двобічний тракт портів + карта варіантів за форматом елемента."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ACCENT = "#8e44ad"   # фіолетовий акцент для меж чипа


# ── Фігура 1: що всередині SW6106 (спільне серце всіх HAT-ів) ───────────────
def fig_chip():
    W, H = 790, 470
    f = []

    # межа мікросхеми
    f.append(rect(150, 70, 460, 360, fill="#faf6fc", stroke=ACCENT, sw=2, rx=10))
    f.append(text(380, 92, "SW6106  (QFN-40, 6×6 мм)", size=15, bold=True, color=ACCENT))

    # елемент зліва
    b, bw, bh = textbox(72, 250, "Літієвий\nелемент\n3.0–4.2 В", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(b)

    # чотири внутрішні блоки (2×2)
    blocks = [
        (250, 165, "Зарядник\n(імпульсний)\nдо 4 А · 96%"),
        (250, 320, "Паливомір\n12-біт АЦП\n5 світлодіодів"),
        (490, 165, "Boost\n(підвищувач)\nдо 18 Вт · 95%"),
        (490, 320, "Контролер\nшляху живлення\n+ захист"),
    ]
    for cx, cy, s in blocks:
        b, w, h = textbox(cx, cy, s, size=11.5, pad=11, min_w=150)
        f.append(b)

    # елемент -> зарядник (заряд, синій, у верхній блок) — чиста горизонталь
    f.append(arrow(72 + bw / 2, 220, 250 - 76, 220, color=NEG))
    f.append(line(250 - 76, 220, 250 - 76, 190, color=NEG))
    f.append(text(150, 210, "заряд →", size=10, color=NEG, anchor="middle"))
    # елемент <- boost/паливомір (розряд, червоний, з нижнього блоку) — чиста горизонталь
    f.append(arrow(250 - 76, 285, 72 + bw / 2, 285, color=POS))
    f.append(line(250 - 76, 320, 250 - 76, 285, color=POS))
    f.append(text(150, 300, "← розряд", size=10, color=POS, anchor="middle"))

    # зарядник -> boost (внутрішня шина VOUT/BST) — у порожньому проміжку між блоками
    f.append(arrow(328, 165, 412, 165))
    f.append(text(370, 152, "VOUT", size=9, color=MUTED))

    # виходи справа
    b, ow, oh = textbox(700, 165, "5 / 9 / 12 В\nType-A · Type-C", size=11.5,
                        fill="#eafaf0", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(arrow(565, 165, 700 - ow / 2, 165, color=FIELD))

    # NTC знизу до захисту
    f.append(text(490, 400, "NTC-терморезистор · кнопка · I²C 0x3C", size=10.5, color=MUTED))

    return render(os.path.join(OUT, "sw6106.svg"), W, H, *f,
                  title="Що всередині SW6106 — спільне серце всіх HAT-ів родини")


# ── Фігура 2: двобічний тракт портів + карта варіантів ──────────────────────
def fig_family():
    W, H = 780, 500
    f = []

    # --- верх: двобічний тракт (bidirectional) ---
    f.append(text(390, 52, "Двобічність: ті самі порти й у вхід, і у вихід", size=14, bold=True))

    # чип-вузол посередині
    b, cw, ch = textbox(390, 120, "SW6106", size=13, bold=True,
                        fill="#faf6fc", stroke=ACCENT, sw=2, min_w=120)
    f.append(b)

    # вхід зліва
    b, iw, ih = textbox(120, 120, "Заряд усередину\nType-C · micro-USB\nPD / AFC / FCP", size=11,
                        fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(b)
    f.append(arrow(120 + iw / 2, 120, 390 - cw / 2, 120, color=NEG))

    # вихід справа
    b, ow, oh = textbox(660, 120, "Віддача назовні\nType-A · Type-C\nQC / PD / SFCP", size=11,
                        fill="#eafaf0", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(arrow(390 + cw / 2, 120, 660 - ow / 2, 120, color=FIELD))

    # розділювач
    f.append(line(60, 205, 720, 205, color=MUTED, sw=1, dash="5 4"))

    # --- низ: карта варіантів за форматом елемента ---
    f.append(text(390, 240, "Одна архітектура — різні формати елемента", size=14, bold=True))

    col_x = [155, 390, 625]
    heads = ["Li-ion HAT", "Li-polymer HAT", "UPS HAT (E)"]
    cells = [
        "1× 14500\n~800–1200 мА·год\nкомпактно, короткий резерв",
        "1× LiPo-пакет\n3000 мА·год\nбільше автономності",
        "4× 21700\n5 В · 6 А\nдовга робота, потужне",
    ]
    for x, hd, cl in zip(col_x, heads, cells):
        f.append(fitbox(x - 105, 265, 210, 40, hd, size=13, bold=True,
                        fill="#f4f6f8", stroke=INK))
        f.append(fitbox(x - 105, 312, 210, 78, cl, size=11, fill=BG, stroke=MUTED))

    # спільна смуга під колонками
    f.append(fitbox(60, 410, 660, 46,
                    "Спільне (не міняється між варіантами): чип SW6106, трифазний заряд літію,\n"
                    "boost до 5 В, захист (over-V / over-I / КЗ / темп.), світлодіоди й кнопка",
                    size=11.5, fill="#faf6fc", stroke=ACCENT, sw=1.8))

    return render(os.path.join(OUT, "family.svg"), W, H, *f,
                  title="Родина Waveshare на SW6106: двобічний тракт і формати елемента")


# ── Фігура 3 (вставка proj): дві шини I²C на Pi ─────────────────────────────
def fig_i2c_paths():
    W, H = 800, 400
    f = []
    f.append(text(400, 40, "Дві різні шини I²C на одному Pi", size=15, bold=True))

    # Raspberry Pi зліва
    b, pw, ph = textbox(120, 210, "Raspberry\nPi\n/dev/i2c-1", size=12,
                        fill="#eafaf0", stroke=FIELD, sw=2, min_w=140)
    f.append(b)

    # верхня гілка: керування SW6106
    b, cw, ch = textbox(560, 130, "SW6106\nкерувальна шина\n0x3C · рег. 0xB0", size=12,
                        fill="#faf6fc", stroke=ACCENT, sw=2, min_w=230)
    f.append(b)
    f.append(arrow(120 + pw / 2, 175, 560 - cw / 2, 130, color=ACCENT))
    f.append(fitbox(300, 92, 210, 30, "керувати станом плати", size=10.5,
                    fill=BG, stroke=MUTED))

    # нижня гілка: паливомір INA219
    b, iw, ih = textbox(560, 290, "INA219\nокремий паливомір\n0x40 · напруга+струм", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=2, min_w=230)
    f.append(b)
    f.append(arrow(120 + pw / 2, 245, 560 - iw / 2, 290, color=NEG))
    f.append(fitbox(300, 300, 210, 30, "виміряти → відсоток", size=10.5,
                    fill=BG, stroke=MUTED))

    # виноска праворуч
    f.append(fitbox(700, 100, 88, 60, "відсотка\nтут НЕ\nвіддає", size=10.5,
                    fill="#fdecea", stroke=POS, sw=1.6))
    f.append(fitbox(700, 260, 88, 60, "звідси\nбереться\nвідсоток", size=10.5,
                    fill="#eafaf0", stroke=FIELD, sw=1.6))

    return render(os.path.join(OUT, "i2c-paths.svg"), W, H, *f,
                  title="Керувати платою — по SW6106; вимірювати заряд — по INA219")


# ── Фігура 4 (вставка proj): логіка ролей Type-C (try.SRC) ──────────────────
def fig_typec_roles():
    W, H = 800, 430
    f = []
    f.append(text(400, 40, "Ролі Type-C: один роз'єм — два напрямки", size=15, bold=True))

    # старт: try.SRC
    b, sw_, sh = textbox(400, 105, "Порт стартує: try.SRC\n(пробує роль джерела, виставляє Rp)",
                         size=12, fill="#faf6fc", stroke=ACCENT, sw=2, min_w=380)
    f.append(b)

    # ліва гілка: побачив Rd → SOURCE
    b, lw, lh = textbox(210, 250, "Бачить CC донизу (Rd):\nнавпроти СПОЖИВАЧ",
                        size=11.5, fill="#fdecea", stroke=POS, sw=1.8, min_w=250)
    f.append(b)
    f.append(arrow(400 - 90, 130, 210, 250 - lh / 2, color=POS))

    b, l2w, l2h = textbox(210, 355, "стає SOURCE →\nзарядник ON, елемент заряджається\nтранслює «до 3 А»",
                          size=11, fill=BG, stroke=POS, sw=1.6, min_w=250)
    f.append(b)
    f.append(arrow(210, 250 + lh / 2, 210, 355 - l2h / 2, color=POS))

    # права гілка: побачив Rp → SINK
    b, rw, rh = textbox(590, 250, "Бачить CC вгору (Rp):\nнавпроти ДЖЕРЕЛО",
                        size=11.5, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=250)
    f.append(b)
    f.append(arrow(400 + 90, 130, 590, 250 - rh / 2, color=NEG))

    b, r2w, r2h = textbox(590, 355, "стає SINK →\nboost ON, плата віддає живлення\n(або заряджається сама)",
                          size=11, fill=BG, stroke=NEG, sw=1.6, min_w=250)
    f.append(b)
    f.append(arrow(590, 250 + rh / 2, 590, 355 - r2h / 2, color=NEG))

    # підпис знизу: вибір апаратний
    f.append(text(400, 415, "Напрямок обирають резистори CC, не код", size=11, color=MUTED, italic=True))

    return render(os.path.join(OUT, "typec-roles.svg"), W, H, *f,
                  title="try.SRC: за реакцією CC порт стає входом заряду або виходом віддачі")


if __name__ == "__main__":
    p1 = fig_chip()
    p2 = fig_family()
    p3 = fig_i2c_paths()
    p4 = fig_typec_roles()
    print("OK:", p1)
    print("OK:", p2)
    print("OK:", p3)
    print("OK:", p4)
