# -*- coding: utf-8 -*-
"""Фігури до теми «Захист входів GPIO від перенапруги» (цифрова електроніка).
Фігури теми:
  clamp-diodes.svg     — вивід GPIO із двома фіксувальними діодами на V_DD/V_SS;
                         показано шлях струму ін'єкції крізь верхній діод у шину.
  hbm-cdm.svg          — форма розряду: HBM (модель тіла людини) проти CDM
                         (модель зарядженого пристрою) на одній осі часу — чому CDM швидший.
  protection-chain.svg — ешелон захисту від роз'єма до кристала: TVS, послідовний R,
                         внутрішні фіксувальні діоди; порядок і що знімає кожен.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _diode(x, y, up=True, col=INK, sw=2.0, s=9):
    """Символ діода у вертикальному дроті; up=True — провідність угору (катодна риска зверху)."""
    out = []
    if up:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (x - s, y + s, x + s, y + s, x, y - s, col, sw))
        out.append(line(x - s, y - s, x + s, y - s, color=col, sw=sw))
    else:
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (x - s, y - s, x + s, y - s, x, y + s, col, sw))
        out.append(line(x - s, y + s, x + s, y + s, color=col, sw=sw))
    return out


# ── 1. Фіксувальні діоди й струм ін'єкції ────────────────────────────────────
def clamp_diodes():
    W, H = 720, 430
    p = []
    vtop, vbot = 82, 330
    railL, railR = 95, 575
    # шини живлення
    p.append(line(railL, vtop, railR, vtop, color=POS, sw=2.6))
    p.append(text(railL - 6, vtop + 5, "V_DD", size=15, bold=True, color=POS, anchor="end"))
    p.append(line(railL, vbot, railR, vbot, color=NEG, sw=2.6))
    p.append(text(railL - 6, vbot + 5, "V_SS", size=15, bold=True, color=NEG, anchor="end"))

    nx, ny = 335, 206
    # аварійний вхід ліворуч: 5 В на 3.3-вольтовий вивід
    p.append(arrow(150, ny, nx - 12, ny, color=POS, sw=2.4))
    p.append(text(150, ny - 26, "чужий рівень", size=13, anchor="start", color=POS, bold=True))
    p.append(text(150, ny - 10, "+5 В на вхід", size=13, anchor="start", color=POS))
    p.append(circle(nx, ny, 5, fill=INK, stroke=INK))
    p.append(text(nx - 8, ny + 24, "вивід GPIO", size=12, color=MUTED, anchor="end"))
    # дріт праворуч у вентиль
    ax = 445
    p.append(line(nx, ny, ax, ny, color=INK, sw=2))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, ny - 30, ax, ny + 30, ax + 58, ny, FILL, LINE))
    p.append(text(ax + 16, ny + 5, "вентиль", size=12, bold=True))
    p.append(text(ax + 30, ny - 42, "внутрішня логіка", size=12, color=MUTED))

    # верхній діод угору на V_DD — саме він відкрився (виділено червоним, товщий)
    p.append(line(nx, ny, nx, vtop + 42, color=POS, sw=2.6))
    p += _diode(nx, (ny + vtop) / 2 - 8, up=True, col=POS, sw=2.6)
    p.append(line(nx, vtop + 42, nx, vtop, color=POS, sw=2.6))
    p.append(text(nx + 20, (ny + vtop) / 2 - 12, "відкритий:", size=12, color=POS, anchor="start", bold=True))
    p.append(text(nx + 20, (ny + vtop) / 2 + 4, "вхід > V_DD + 0.6 В", size=12, color=POS, anchor="start"))
    p.append(text(nx + 20, (ny + vtop) / 2 + 20, "→ струм ін'єкції в шину", size=12, color=POS, anchor="start"))

    # нижній діод закритий (сірий)
    p.append(line(nx, ny, nx, vbot - 42, color=MUTED, sw=2))
    p += _diode(nx, (ny + vbot) / 2 + 8, up=True, col=MUTED, sw=2)
    p.append(line(nx, vbot - 42, nx, vbot, color=MUTED, sw=2))
    p.append(text(nx + 20, (ny + vbot) / 2 + 14, "закритий", size=12, color=MUTED, anchor="start"))

    # стрілка струму ін'єкції вздовж шини V_DD праворуч
    p.append(arrow(nx + 10, vtop - 14, railR - 30, vtop - 14, color=POS, sw=2))
    p.append(text((nx + railR) / 2, vtop - 20, "струм ін'єкції I_inj", size=12, color=POS, anchor="middle"))

    p.append(fitbox(40, 366, W - 80, 52,
                    "Поки сигнал між шинами — обидва діоди закриті. Виліз вище V_DD — верхній діод\n"
                    "відкривається й тримає напругу, але крізь нього тече струм ін'єкції. Діод обмежує\n"
                    "напругу, а не струм: цей струм і треба тримати послідовним резистором.",
                    size=12, fill="#f4f6f8", stroke=LINE))
    render(os.path.join(OUT, 'clamp-diodes.svg'), W, H, *p,
           title="Фіксувальні діоди GPIO: напругу тримають, струм ін'єкції — ні")


# ── 2. Форма розряду HBM vs CDM ──────────────────────────────────────────────
def hbm_cdm():
    W, H = 720, 400
    p = []
    # осі
    ox, oy = 110, 320          # початок координат
    axw, axh = 540, 240        # довжина осей
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))          # час →
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=2))         # струм ↑
    p.append(text(ox + axw, oy + 24, "час (нс)", size=13, anchor="end"))
    p.append(text(ox - 12, oy - axh + 6, "струм розряду", size=13, anchor="end", color=MUTED))

    # HBM: повільний фронт (~8 нс), спад ~160 нс, помірний пік — синім
    # будуємо як полілінію з небагатьох точок (без циклів-важких обчислень)
    def curve_points(pts):
        return " ".join("%.1f,%.1f" % (x, y) for x, y in pts)

    base = oy
    # масштаб часу: 0..180 нс на axw; але щоб CDM було видно, стиснемо шкалу нелінійно —
    # покажемо перші 12 нс у лівій половині, решту — стисло. Простіше: дві криві на спільній осі,
    # HBM низький і широкий, CDM високий і вузький.
    hbm_peak_y = base - 120
    hbm = [(ox, base), (ox + 60, hbm_peak_y), (ox + 130, base - 92),
           (ox + 260, base - 55), (ox + 430, base - 22), (ox + axw - 10, base - 8)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (curve_points(hbm), NEG))
    p.append(text(ox + 300, hbm_peak_y + 44, "HBM — модель тіла людини", size=13, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + 300, hbm_peak_y + 62, "фронт ~ нс, спад ~160 нс", size=12, color=NEG, anchor="start"))
    p.append(text(ox + 300, hbm_peak_y + 78, "100 пФ · 1.5 кОм, до кількох кВ", size=12, color=NEG, anchor="start"))

    # CDM: дуже вузький і високий пік коло нуля часу — червоним
    cdm_peak_y = base - axh + 12
    cdm = [(ox, base), (ox + 10, cdm_peak_y), (ox + 22, base - 40),
           (ox + 34, base - 10), (ox + 46, base)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (curve_points(cdm), POS))
    p.append(text(ox + 60, cdm_peak_y + 4, "CDM — модель зарядженого пристрою", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(ox + 60, cdm_peak_y + 22, "фронт < 0.4 нс, пік десятки А", size=12, color=POS, anchor="start"))
    p.append(text(ox + 60, cdm_peak_y + 38, "мала послідовна індуктивність → блискавично", size=12, color=POS, anchor="start"))

    p.append(fitbox(40, 350, W - 80, 40,
                    "Той самий заряд, різна форма. HBM (палець людини) — нижчий, ширший імпульс; TVS устигає зреагувати.\n"
                    "CDM (заряджена сама плата) — блискавичний і високий; вартовий мусить стояти просто коло виводу.",
                    size=12, fill="#f4f6f8", stroke=LINE))
    render(os.path.join(OUT, 'hbm-cdm.svg'), W, H, *p,
           title="Розряд статики: HBM повільний і широкий, CDM — блискавичний")


# ── 3. Ешелон захисту від роз'єма до кристала ────────────────────────────────
def protection_chain():
    W, H = 760, 400
    p = []
    y = 190
    gnd = 320
    # лінія сигналу зліва направо
    p.append(line(70, y, 690, y, color=INK, sw=2.4))
    # земляна шина знизу
    p.append(line(70, gnd, 690, gnd, color=NEG, sw=2.6))
    p.append(text(64, gnd + 5, "земля", size=12, color=NEG, anchor="end"))

    # роз'єм ліворуч
    p.append(rect(64, y - 22, 20, 44, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(74, y - 34, "роз'єм", size=12, bold=True, color=POS))
    p.append(arrow(30, y, 62, y, color=POS, sw=2.2))
    p.append(text(30, y - 12, "удар", size=12, color=POS, anchor="start"))

    # 1) TVS біля роз'єма — на землю
    tvsx = 175
    p.append(circle(tvsx, y, 4, fill=INK, stroke=INK))
    p.append(line(tvsx, y, tvsx, gnd - 40, color=FIELD, sw=2.6))
    # символ TVS: діод із двонапрямними «крилами» катода — спростимо як діод із засічками
    p += _diode(tvsx, (y + gnd) / 2, up=False, col=FIELD, sw=2.6)
    p.append(line(tvsx, gnd - 40, tvsx, gnd, color=FIELD, sw=2.6))
    p.append(text(tvsx, y - 40, "1. TVS", size=13, bold=True, color=FIELD))
    p.append(text(tvsx, y - 24, "зрізає удар", size=11, color=FIELD))

    # 2) послідовний резистор
    rx0, rx1 = 300, 400
    p.append(rect(rx0, y - 14, rx1 - rx0, 28, fill="#eef2ff", stroke=NEG, sw=2))
    p.append(text((rx0 + rx1) / 2, y - 26, "2. R послід.", size=13, bold=True, color=NEG))
    p.append(text((rx0 + rx1) / 2, y + 5, "тримає струм", size=11, bold=True, color=NEG))

    # 3) внутрішні діоди біля кристала — рамка кристала праворуч
    dnx = 500
    p.append(circle(dnx, y, 4, fill=INK, stroke=INK))
    # верхній діод на V_DD
    vdd = 96
    p.append(line(dnx, vdd, 660, vdd, color=POS, sw=2.4))
    p.append(text(666, vdd + 5, "V_DD", size=12, bold=True, color=POS, anchor="start"))
    p.append(line(dnx, y, dnx, vdd + 34, color=POS, sw=2))
    p += _diode(dnx, (y + vdd) / 2, up=True, col=POS, sw=2)
    p.append(line(dnx, vdd + 34, dnx, vdd, color=POS, sw=2))
    # нижній діод на землю
    p.append(line(dnx, y, dnx, gnd - 34, color=NEG, sw=2))
    p += _diode(dnx, (y + gnd) / 2, up=True, col=NEG, sw=2)
    p.append(line(dnx, gnd - 34, dnx, gnd, color=NEG, sw=2))
    p.append(text(dnx + 14, y - 30, "3. внутрішні", size=12, bold=True, anchor="start"))
    p.append(text(dnx + 14, y - 14, "діоди", size=12, anchor="start"))

    # кристал праворуч
    cx = 600
    p.append(line(dnx, y, cx, y, color=INK, sw=2))
    p.append(rect(cx, y - 40, 84, 80, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(cx + 42, y - 6, "крихкий", size=12, bold=True))
    p.append(text(cx + 42, y + 12, "вентиль", size=12))

    p.append(fitbox(40, 350, W - 80, 40,
                    "Порядок важить: TVS першим, повз плату на землю, зрізає верхівку; послідовний резистор обмежує струм рештки;\n"
                    "внутрішні діоди мікроконтролера добирають ослаблену дрібницю. Кіловольтний удар → кілька безпечних міліампер.",
                    size=12, fill="#f4f6f8", stroke=LINE))
    render(os.path.join(OUT, 'protection-chain.svg'), W, H, *p,
           title="Ешелон захисту GPIO: TVS → резистор → внутрішні діоди")


if __name__ == '__main__':
    clamp_diodes()
    hbm_cdm()
    protection_chain()
    print("OK: figs written to", OUT)
