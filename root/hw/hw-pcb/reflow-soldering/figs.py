# -*- coding: utf-8 -*-
"""Фігури до теми «Паяння оплавленням».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_COPPER = "#d35400"
COLOR_SOLDER = "#7f8c8d"
COLOR_SOLDER_LIQ = "#95a5a6"
COLOR_IMC    = "#8e44ad"
COLOR_FR4    = "#27ae60"
COLOR_CHIP   = "#2c3e50"
COLOR_NICKEL = "#2980b9"
COLOR_GOLD   = "#f1c40f"


# ── 1. Чотири зони температурного профілю оплавлення (SAC305 за J-STD-020) ────
def fig_reflow_zones():
    W, H = 840, 490
    f = [text(W / 2, 26, "Температурний профіль безсвинцевого паяння оплавленням (SAC305 за J-STD-020)", size=15, bold=True)]
    f.append(text(W / 2, 46, "чотири технологічні зони: нагрів, витримка, оплавлення з вікном TAL та кероване охолодження",
                  size=11, color=MUTED, italic=True))

    ox, oy = 80, 390
    ax, ay = 740, 85

    # 4 зони часу: 0..65 с, 65..150 с, 150..210 с, 210..260 с
    z1_x = ox + (ax - ox) * (65.0 / 260.0)
    z2_x = ox + (ax - ox) * (150.0 / 260.0)
    z3_x = ox + (ax - ox) * (210.0 / 260.0)
    z4_x = ax

    # Фонова розмітка зон
    f.append(rect(ox, ay, z1_x - ox, oy - ay, fill="#fdfaf6", stroke="none", rx=0))
    f.append(rect(z1_x, ay, z2_x - z1_x, oy - ay, fill="#fefdfa", stroke="none", rx=0))
    f.append(rect(z2_x, ay, z3_x - z2_x, oy - ay, fill="#fef6f6", stroke="none", rx=0))
    f.append(rect(z3_x, ay, z4_x - z3_x, oy - ay, fill="#f6f9fc", stroke="none", rx=0))

    # Вертикальні розділювачі зон
    f.append(line(z1_x, oy, z1_x, ay, color="#d0d7de", sw=1.2, dash="4,4"))
    f.append(line(z2_x, oy, z2_x, ay, color="#d0d7de", sw=1.2, dash="4,4"))
    f.append(line(z3_x, oy, z3_x, ay, color="#d0d7de", sw=1.2, dash="4,4"))

    # Підписи зон зверху
    f.append(text((ox + z1_x) / 2, ay + 16, "1. Нагрів (Preheat)", size=11, bold=True, color="#d35400"))
    f.append(text((ox + z1_x) / 2, ay + 30, "1.0–3.0 °C/с", size=10, color=MUTED))

    f.append(text((z1_x + z2_x) / 2, ay + 16, "2. Витримка (Soak)", size=11, bold=True, color="#b9770e"))
    f.append(text((z1_x + z2_x) / 2, ay + 30, "150–200 °C (60–120 с)", size=10, color=MUTED))

    f.append(text((z2_x + z3_x) / 2, ay + 16, "3. Оплавлення (Reflow)", size=11, bold=True, color=POS))
    f.append(text((z2_x + z3_x) / 2, ay + 30, "TAL: 45–90 с, Tpeak", size=10, color=MUTED))

    f.append(text((z3_x + z4_x) / 2, ay + 16, "4. Охолодження", size=11, bold=True, color=NEG))
    f.append(text((z3_x + z4_x) / 2, ay + 30, "-2.0...-4.0 °C/с", size=10, color=MUTED))

    # Y-scale: 0 °C @ oy, 270 °C @ ay
    def y_temp(t):
        return oy - (oy - ay) * (t / 270.0)

    # Горизонтальні рівні
    # Ліквідус 217 °C
    y_liq = y_temp(217)
    f.append(line(ox, y_liq, ax, y_liq, color=POS, sw=1.2, dash="6,4"))
    f.append(text(ax + 6, y_liq + 4, "T_L = 217 °C", size=10, color=POS, anchor="start", bold=True))

    # 150 °C та 200 °C
    y_150 = y_temp(150)
    y_200 = y_temp(200)
    f.append(line(ox, y_150, ax, y_150, color="#b9770e", sw=0.8, dash="3,3"))
    f.append(line(ox, y_200, ax, y_200, color="#b9770e", sw=0.8, dash="3,3"))

    # Осі
    f.append(line(ox, oy, ox, ay - 12, color=INK, sw=1.8))
    f.append(line(ox, oy, ax + 15, oy, color=INK, sw=1.8))

    # Y-мітки
    for t_val in (0, 50, 100, 150, 200, 217, 245):
        yy = y_temp(t_val)
        f.append(line(ox - 4, yy, ox, yy, color=INK, sw=1.2))
        is_key = t_val in (217, 245)
        f.append(text(ox - 8, yy + 4, "%d °C" % t_val, size=10, color=INK if is_key else MUTED,
                      anchor="end", bold=is_key))

    # X-мітки (час, с)
    for s_val in (0, 50, 100, 150, 200, 250):
        xx = ox + (ax - ox) * (s_val / 260.0)
        f.append(line(xx, oy, xx, oy + 4, color=INK, sw=1.2))
        f.append(text(xx, oy + 18, "%d с" % s_val, size=10, color=MUTED))

    f.append(text(ox - 46, (oy + ay) / 2, "Температура (°C)", size=11, bold=True, anchor="middle"))
    f.append(text((ox + ax) / 2, oy + 38, "Час процесу (секунди)", size=11, bold=True))

    # Крива термопрофілю
    pts_profile = [
        (0, 25),
        (30, 95),
        (65, 155),
        (105, 175),
        (150, 195),
        (165, 217),
        (185, 246),
        (196, 238),
        (210, 217),
        (235, 120),
        (260, 45)
    ]
    svg_pts = []
    for s_sec, t_c in pts_profile:
        px = ox + (ax - ox) * (s_sec / 260.0)
        py = y_temp(t_c)
        svg_pts.append((px, py))

    path_d = "M " + " L ".join("%.1f,%.1f" % p for p in svg_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (path_d, POS))

    # Позначення піку T_peak
    pk_x = ox + (ax - ox) * (185.0 / 260.0)
    pk_y = y_temp(246)
    f.append(circle(pk_x, pk_y, 4.5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(pk_x, pk_y - 12, "T_peak = 246 °C", size=10.5, color=POS, bold=True))

    # Позначення TAL (Time Above Liquidus) під віссю ліквідусу
    tal_x1 = ox + (ax - ox) * (165.0 / 260.0)
    tal_x2 = ox + (ax - ox) * (210.0 / 260.0)
    tal_y = y_liq + 24
    f.append(line(tal_x1, tal_y, tal_x2, tal_y, color=POS, sw=1.5))
    f.append(line(tal_x1, tal_y - 5, tal_x1, tal_y + 5, color=POS, sw=1.5))
    f.append(line(tal_x2, tal_y - 5, tal_x2, tal_y + 5, color=POS, sw=1.5))
    f.append(text((tal_x1 + tal_x2) / 2, tal_y + 16, "TAL: 45–90 с", size=10, color=POS, bold=True))

    # Інформаційні мітки у вільній зоні (без перекриття фонів)
    f.append(text(ox + 130, oy - 65, "Критерії якості за J-STD-020:", size=10, bold=True, color=INK))
    f.append(text(ox + 130, oy - 48, "• ΔT між деталями: < 8 °C (max 10 °C)", size=9.5, color=FIELD, bold=True))
    f.append(text(ox + 130, oy - 32, "• Градієнт нагріву: 1.0–3.0 °C/с", size=9.5, color=INK))
    f.append(text(ox + 130, oy - 16, "• Швидкість спаду: max 4.0 °C/с", size=9.5, color=INK))

    render(os.path.join(IMG, 'lead-free-reflow-temperature-zones.svg'), W, H, *f)


# ── 2. Металургія росту інтерметалідів (IMC: Cu6Sn5, Cu3Sn, Ni3Sn4) ────────────
def fig_imc_growth():
    W, H = 820, 440
    f = [text(W / 2, 26, "Мікроструктура та еволюція інтерметалідних шарів (IMC)", size=15, bold=True)]
    f.append(text(W / 2, 46, "порівняння паяння на мідну основу (Cu-Sn) та бар'єрний шар хімічного нікелю (ENIG / Ni-Sn)",
                  size=11, color=MUTED, italic=True))

    pw, ph = 370, 350

    # ── Ліва панель: Мідний контакт (Cu-Sn система) ──
    p1_x, p1_y = 25, 70
    f.append(rect(p1_x, p1_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p1_x + pw / 2, p1_y + 20, "1. Мідний майданчик (Bare Cu / OSP / HASL)", size=11.5, color=COLOR_COPPER, bold=True))

    # Об'ємний припій SAC305
    solder_y = p1_y + 38
    f.append(rect(p1_x + 15, solder_y, pw - 30, 80, fill="#eaeded", stroke=COLOR_SOLDER, sw=1.2))
    f.append(text(p1_x + pw / 2, solder_y + 24, "Об'ємний припій SAC305 (β-Sn матриця)", size=10.5, color=INK, bold=True))
    f.append(text(p1_x + pw / 2, solder_y + 42, "Евтектичні виділення Ag3Sn + Cu6Sn5", size=9.5, color=MUTED))
    # Дрібні частинки Ag3Sn
    for ax_pt in (p1_x + 40, p1_x + 110, p1_x + 220, p1_x + 310, p1_x + 160, p1_x + 270):
        f.append(circle(ax_pt, solder_y + 60, 3, fill="#7f8c8d", stroke="none"))

    # Стовпчастий інтерметалід Cu6Sn5 (гребінці / scallops)
    imc1_y = solder_y + 80
    f.append(rect(p1_x + 15, imc1_y, pw - 30, 34, fill="#e8daef", stroke=COLOR_IMC, sw=1.2))
    for k in range(10):
        kx = p1_x + 30 + k * 34
        f.append(circle(kx, imc1_y + 12, 12, fill="#d2b4de", stroke=COLOR_IMC, sw=1))
    f.append(text(p1_x + pw / 2, imc1_y + 20, "η-фаза: Cu6Sn5 (0.5–1.5 мкм, паяння)", size=10, color=COLOR_IMC, bold=True))

    # Плоский шар Cu3Sn (ε-фаза) з мікропорами Кіркендалла
    imc2_y = imc1_y + 34
    f.append(rect(p1_x + 15, imc2_y, pw - 30, 24, fill="#bb8fce", stroke=COLOR_IMC, sw=1.2))
    f.append(text(p1_x + pw / 2, imc2_y + 16, "ε-фаза: Cu3Sn (дифузія при термоциклі)", size=9.5, color="#ffffff", bold=True))
    # Пори Кіркендалла
    for vx in (p1_x + 60, p1_x + 140, p1_x + 220, p1_x + 300):
        f.append(circle(vx, imc2_y + 12, 2.5, fill="#ffffff", stroke="#5b2c6f", sw=0.8))

    # Мідна основа
    cu_y = imc2_y + 24
    f.append(rect(p1_x + 15, cu_y, pw - 30, 65, fill="#fdebd0", stroke=COLOR_COPPER, sw=1.5))
    f.append(text(p1_x + pw / 2, cu_y + 36, "Мідна доріжка / площадка плати (Cu)", size=11, color=COLOR_COPPER, bold=True))

    # Примітки лівої панелі
    f.append(text(p1_x + pw / 2, p1_y + 285, "Пори Кіркендалла: D(Cu) > D(Sn) в шарі Cu3Sn", size=9.5, color=POS, bold=True))
    f.append(text(p1_x + pw / 2, p1_y + 305, "Товщина IMC > 3 мкм → деградація в'язкості", size=9.5, color=MUTED))
    f.append(text(p1_x + pw / 2, p1_y + 325, "Швидкість росту: d = d0 + sqrt(K(T) · t)", size=9.5, color=INK))

    # ── Права панель: Нікель-золото (ENIG система) ──
    p2_x, p2_y = 425, 70
    f.append(rect(p2_x, p2_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p2_x + pw / 2, p2_y + 20, "2. Покриття ENIG (Хімічний Ni-P + Золото)", size=11.5, color=COLOR_NICKEL, bold=True))

    # Об'ємний припій з розчиненим золотом
    solder2_y = p2_y + 38
    f.append(rect(p2_x + 15, solder2_y, pw - 30, 75, fill="#eaeded", stroke=COLOR_SOLDER, sw=1.2))
    f.append(text(p2_x + pw / 2, solder2_y + 22, "Об'ємний припій SAC305", size=10.5, color=INK, bold=True))
    f.append(text(p2_x + pw / 2, solder2_y + 40, "Золото (Au ~0.05 мкм) розчинилось у Sn", size=9.5, color=MUTED))
    f.append(text(p2_x + pw / 2, solder2_y + 56, "Формування часток AuSn4 у припої", size=9.5, color=MUTED))

    # Тонкий голчастий шар (Cu,Ni)6Sn5 / Ni3Sn4
    imc_ni_y = solder2_y + 75
    f.append(rect(p2_x + 15, imc_ni_y, pw - 30, 26, fill="#d4e6f1", stroke=COLOR_NICKEL, sw=1.2))
    for k in range(12):
        nx = p2_x + 25 + k * 28
        f.append(line(nx, imc_ni_y + 25, nx + 6, imc_ni_y + 4, color=COLOR_NICKEL, sw=1.5))
    f.append(text(p2_x + pw / 2, imc_ni_y + 16, "(Cu,Ni)6Sn5 / Ni3Sn4 (бар'єр 0.3–0.8 мкм)", size=9.5, color=COLOR_NICKEL, bold=True))

    # Збагачений фосфором шар (P-rich layer / Ni3P)
    prich_y = imc_ni_y + 26
    f.append(rect(p2_x + 15, prich_y, pw - 30, 18, fill="#2c3e50", stroke="none"))
    f.append(text(p2_x + pw / 2, prich_y + 13, "P-rich Ni3P шар (7–10% P) — ризик Black Pad", size=9, color="#ffffff", bold=True))

    # Шар хімічного нікелю (Electroless Nickel 3–6 мкм)
    ni_y = prich_y + 18
    f.append(rect(p2_x + 15, ni_y, pw - 30, 42, fill="#aed6f1", stroke=COLOR_NICKEL, sw=1.5))
    f.append(text(p2_x + pw / 2, ni_y + 26, "Шар хімічного нікелю (3–6 мкм Ni-P)", size=10.5, color=COLOR_NICKEL, bold=True))

    # Мідна основа
    cu2_y = ni_y + 42
    f.append(rect(p2_x + 15, cu2_y, pw - 30, 44, fill="#fdebd0", stroke=COLOR_COPPER, sw=1.5))
    f.append(text(p2_x + pw / 2, cu2_y + 26, "Мідна площадка плати (Cu)", size=10.5, color=COLOR_COPPER, bold=True))

    # Примітки правої панелі
    f.append(text(p2_x + pw / 2, p2_y + 285, "Нікель блокує розчинення міді (бар'єр)", size=9.5, color=FIELD, bold=True))
    f.append(text(p2_x + pw / 2, p2_y + 305, "Ni3Sn4 росте в 3–5 разів повільніше за Cu6Sn5", size=9.5, color=MUTED))
    f.append(text(p2_x + pw / 2, p2_y + 325, "Дефект Black Pad: гіперкорозія Ni", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, 'intermetallic-compound-growth.svg'), W, H, *f)


if __name__ == "__main__":
    fig_reflow_zones()
    fig_imc_growth()
    print("OK: 2 фігури згенеровано у", IMG)
