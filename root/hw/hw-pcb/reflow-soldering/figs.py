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
COLOR_FLUX   = "#f39c12"


# ── 1. Чотири зони стандартного термопрофілю (SAC305) ─────────────────────────
def fig_thermal_profile():
    W, H = 760, 420
    f = [text(W / 2, 26, "Чотири зони термопрофілю оплавлення (безсвинцевий SAC305)", size=16, bold=True)]
    f.append(text(W / 2, 46, "температурно-часові вікна запобігають термічному удару, вигоранню флюсу та дефектам",
                  size=11, color=MUTED, italic=True))

    ox, oy = 80, 350
    ax, ay = 710, 80

    # Зони фону
    z1_x = ox + (ax - ox) * 0.28   # 0..70 с (Preheat)
    z2_x = ox + (ax - ox) * 0.60   # 70..150 с (Soak)
    z3_x = ox + (ax - ox) * 0.82   # 150..210 с (Reflow)
    z4_x = ax                      # 210..260 с (Cooling)

    f.append(rect(ox, ay, z1_x - ox, oy - ay, fill="#fdfaf6", stroke="none", rx=0))
    f.append(rect(z1_x, ay, z2_x - z1_x, oy - ay, fill="#fefdfa", stroke="none", rx=0))
    f.append(rect(z2_x, ay, z3_x - z2_x, oy - ay, fill="#fef8f8", stroke="none", rx=0))
    f.append(rect(z3_x, ay, z4_x - z3_x, oy - ay, fill="#f6f9fc", stroke="none", rx=0))

    # Вертикальні розділювачі зон
    f.append(line(z1_x, oy, z1_x, ay, color="#e0e0e0", sw=1, dash="4,4"))
    f.append(line(z2_x, oy, z2_x, ay, color="#e0e0e0", sw=1, dash="4,4"))
    f.append(line(z3_x, oy, z3_x, ay, color="#e0e0e0", sw=1, dash="4,4"))

    # Підписи зон зверху
    f.append(text((ox + z1_x) / 2, ay + 18, "1. Нагрів (Preheat)", size=11, bold=True, color=POS))
    f.append(text((ox + z1_x) / 2, ay + 32, "1–3 °C/с", size=10, color=MUTED))

    f.append(text((z1_x + z2_x) / 2, ay + 18, "2. Витримка (Soak)", size=11, bold=True, color="#d35400"))
    f.append(text((z1_x + z2_x) / 2, ay + 32, "150–180 °C (60–100 с)", size=10, color=MUTED))

    f.append(text((z2_x + z3_x) / 2, ay + 18, "3. Оплавлення (Reflow)", size=11, bold=True, color=POS))
    f.append(text((z2_x + z3_x) / 2, ay + 32, "TAL: 45–90 с, Tmax: 245 °C", size=10, color=MUTED))

    f.append(text((z3_x + z4_x) / 2, ay + 18, "4. Охолодження", size=11, bold=True, color=NEG))
    f.append(text((z3_x + z4_x) / 2, ay + 32, "2–4 °C/с", size=10, color=MUTED))

    # Горизонтальні рівні температур
    # Y-scale: 0 °C @ oy, 260 °C @ ay
    def y_temp(t):
        return oy - (oy - ay) * (t / 260.0)

    # 217 °C ліквідус
    y_liq = y_temp(217)
    f.append(line(ox, y_liq, ax, y_liq, color=POS, sw=1.2, dash="6,4"))
    f.append(text(ax + 5, y_liq + 4, "T_L = 217 °C (ліквідус)", size=10, color=POS, anchor="start", bold=True))

    # 150 °C та 180 °C soak
    y_150 = y_temp(150)
    y_180 = y_temp(180)
    f.append(line(ox, y_150, ax, y_150, color="#d35400", sw=0.8, dash="3,3"))
    f.append(line(ox, y_180, ax, y_180, color="#d35400", sw=0.8, dash="3,3"))

    # Осі
    f.append(line(ox, oy, ox, ay - 10, color=INK, sw=1.8))
    f.append(line(ox, oy, ax + 20, oy, color=INK, sw=1.8))

    # Y-мітки (температура)
    for t_val in (0, 50, 100, 150, 180, 217, 245):
        yy = y_temp(t_val)
        f.append(line(ox - 4, yy, ox, yy, color=INK, sw=1.2))
        f.append(text(ox - 8, yy + 4, "%d °C" % t_val, size=10, color=INK if t_val in (217, 245) else MUTED,
                      anchor="end", bold=(t_val in (217, 245))))

    # X-мітки (час, с)
    for s_val, s_lbl in ((0, "0"), (60, "60"), (120, "120"), (180, "180"), (240, "240")):
        xx = ox + (ax - ox) * (s_val / 260.0)
        f.append(line(xx, oy, xx, oy + 4, color=INK, sw=1.2))
        f.append(text(xx, oy + 18, s_lbl + " с", size=10, color=MUTED))

    f.append(text(ox - 45, (oy + ay) / 2, "Температура (°C)", size=11, bold=True, anchor="middle"))
    f.append(text((ox + ax) / 2, oy + 36, "Час процесу (секунди)", size=11, bold=True))

    # Крива термопрофілю
    # Точки: (t_sec, T_C)
    pts_profile = [
        (0, 25),
        (30, 90),
        (65, 150),
        (100, 165),
        (145, 180),
        (165, 217),
        (185, 245),
        (198, 235),
        (210, 217),
        (235, 120),
        (255, 45)
    ]
    svg_pts = []
    for s_sec, t_c in pts_profile:
        px = ox + (ax - ox) * (s_sec / 260.0)
        py = y_temp(t_c)
        svg_pts.append((px, py))

    path_d = "M " + " L ".join("%.1f,%.1f" % p for p in svg_pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_d, POS))

    # Позначення піку T_peak
    pk_x = ox + (ax - ox) * (185 / 260.0)
    pk_y = y_temp(245)
    f.append(circle(pk_x, pk_y, 4, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(pk_x, pk_y - 12, "T_peak = 245 °C", size=11, color=POS, bold=True))

    # Позначення TAL (Time Above Liquidus)
    tal_x1 = ox + (ax - ox) * (165 / 260.0)
    tal_x2 = ox + (ax - ox) * (210 / 260.0)
    tal_y = y_liq
    f.append(line(tal_x1, tal_y - 18, tal_x2, tal_y - 18, color=POS, sw=1.5))
    f.append(line(tal_x1, tal_y - 23, tal_x1, tal_y - 13, color=POS, sw=1.5))
    f.append(line(tal_x2, tal_y - 23, tal_x2, tal_y - 13, color=POS, sw=1.5))
    f.append(text((tal_x1 + tal_x2) / 2, tal_y - 26, "TAL: 45–90 с", size=10.5, color=POS, bold=True))

    render(os.path.join(IMG, 'thermal-profile-zones.svg'), W, H, *f)


# ── 2. Металургія змочування та ріст інтерметаліду (IMC) ──────────────────────
def fig_wetting_and_imc():
    W, H = 760, 360
    f = [text(W / 2, 26, "Змочування припоєм та інтерметалідний шар (IMC)", size=16, bold=True)]
    f.append(text(W / 2, 46, "баланс поверхневого натягу (Юнг) та дифузійний бар'єр Cu6Sn5 на межі поділу",
                  size=11, color=MUTED, italic=True))

    # ── Ліва панель: Рівновага змочування за Юнгом ──
    lx, ly, lw, lh = 30, 70, 335, 265
    f.append(rect(lx, ly, lw, lh, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "Крапля припою: баланс сил Юнга", size=12.5, bold=True))

    # Підкладка (Cu)
    f.append(rect(lx + 25, ly + 180, lw - 50, 30, fill="#f9e79f", stroke=COLOR_COPPER, sw=1.5, rx=2))
    f.append(text(lx + lw / 2, ly + 200, "Мідний контактний майданчик (Cu)", size=10.5, color=COLOR_COPPER, bold=True))

    # Крапля рідкого припою з кутом θ
    # Дуга краплі
    drop_d = "M %d %d A 110 75 0 0 1 %d %d Z" % (lx + 60, ly + 180, lx + lw - 60, ly + 180)
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (drop_d, "#d5dbdb", COLOR_SOLDER))
    f.append(text(lx + lw / 2, ly + 145, "Рідкий припій (SAC305)", size=11, color=INK, bold=True))

    # Кут змочування θ зліва
    f.append(line(lx + 60, ly + 180, lx + 115, ly + 140, color=POS, sw=1.6))
    f.append(line(lx + 60, ly + 180, lx + 120, ly + 180, color=MUTED, sw=1, dash="3,2"))
    f.append(text(lx + 85, ly + 172, "θ < 30°", size=11, color=POS, bold=True))

    # Вектори сил
    # γ_sv тягне вліво (поверхнева енергія чистої міді під флюсом)
    f.append(arrow(lx + 60, ly + 180, lx + 15, ly + 180, color="#27ae60", sw=2))
    f.append(text(lx + 32, ly + 170, "γ_sv", size=11, color="#27ae60", bold=True))

    # γ_sl тягне вправо (межа метал-припій)
    f.append(arrow(lx + 60, ly + 180, lx + 105, ly + 180, color="#d35400", sw=1.8))
    f.append(text(lx + 90, ly + 192, "γ_sl", size=10, color="#d35400", bold=True))

    # γ_lv тягне по дотичній
    f.append(arrow(lx + 60, ly + 180, lx + 115, ly + 140, color=NEG, sw=2))
    f.append(text(lx + 122, ly + 136, "γ_lv (поверхневий натяг)", size=10.5, color=NEG, bold=True))

    f.append(text(lx + lw / 2, ly + 235, "γ_sv = γ_sl + γ_lv · cos(θ)", size=11.5, bold=True))
    f.append(text(lx + lw / 2, ly + 250, "Флюс знижує γ_sl та γ_lv → розтікання краплі", size=10, color=MUTED))

    # ── Права панель: Інтерметалідний шар (IMC) ──
    rx_p, ry_p, rw_p, rh_p = 395, 70, 335, 265
    f.append(rect(rx_p, ry_p, rw_p, rh_p, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(rx_p + rw_p / 2, ry_p + 22, "Мікроструктура контакту (IMC)", size=12.5, bold=True))

    # Шар припою (вгорі)
    f.append(rect(rx_p + 20, ry_p + 50, rw_p - 40, 70, fill="#eaeded", stroke=COLOR_SOLDER, sw=1.5))
    f.append(text(rx_p + rw_p / 2, ry_p + 75, "Об'ємний припій (β-Sn матриця)", size=11, color=INK, bold=True))
    f.append(text(rx_p + rw_p / 2, ry_p + 95, "дрібні голки Ag3Sn + Cu6Sn5", size=9.5, color=MUTED))

    # Інтерметалідний шар Cu6Sn5 («гребінці» / кристали)
    imc_y = ry_p + 115
    f.append(rect(rx_p + 20, imc_y, rw_p - 40, 30, fill="#e8daef", stroke=COLOR_IMC, sw=1.5))
    # Нерівні кристали IMC
    for k in range(9):
        kx = rx_p + 35 + k * 30
        f.append(circle(kx, imc_y + 12, 10, fill="#d2b4de", stroke=COLOR_IMC, sw=1))
    f.append(text(rx_p + rw_p / 2, imc_y + 18, "Інтерметалід Cu6Sn5 (0.5–1.5 мкм)", size=11, color=COLOR_IMC, bold=True))

    # Тонкий шар Cu3Sn
    f.append(rect(rx_p + 20, imc_y + 30, rw_p - 40, 16, fill="#bb8fce", stroke=COLOR_IMC, sw=1))
    f.append(text(rx_p + rw_p / 2, imc_y + 42, "Cu3Sn (дифузійний шар при старінні)", size=9.5, color="#ffffff", bold=True))

    # Мідний шар плати
    f.append(rect(rx_p + 20, imc_y + 46, rw_p - 40, 48, fill="#f9e79f", stroke=COLOR_COPPER, sw=1.5))
    f.append(text(rx_p + rw_p / 2, imc_y + 75, "Мідна площадка плати (Cu)", size=11, color=COLOR_COPPER, bold=True))

    f.append(text(rx_p + rw_p / 2, ry_p + 242, "Норма IMC: 0.5–1.5 мкм (міцний шов)", size=10.5, color=POS, bold=True))
    f.append(text(rx_p + rw_p / 2, ry_p + 256, "> 3–5 мкм: крихкість та тріщини від вібрації", size=10, color=MUTED))

    render(os.path.join(IMG, 'wetting-and-imc.svg'), W, H, *f)


# ── 3. Анатомія дефектів оплавлення ────────────────────────────────────────────
def fig_defects():
    W, H = 760, 390
    f = [text(W / 2, 26, "Ключові дефекти паяння оплавленням", size=16, bold=True)]
    f.append(text(W / 2, 46, "механічні причини: тепловий дисбаланс, надлишок пасти, кипіння розчинників та вигин",
                  size=11, color=MUTED, italic=True))

    pw, ph = 345, 145

    # ── Панель 1: Надгробок (Tombstoning) ──
    p1_x, p1_y = 25, 65
    f.append(rect(p1_x, p1_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p1_x + pw / 2, p1_y + 18, "1. Ефект надгробка (Tombstoning)", size=11.5, color=POS, bold=True))

    # Плата FR4
    f.append(rect(p1_x + 20, p1_y + 115, pw - 40, 16, fill="#d5f5e3", stroke=COLOR_FR4, sw=1.2))
    # Лівий майданчик (розплавлений)
    f.append(rect(p1_x + 45, p1_y + 108, 45, 7, fill="#f9e79f", stroke=COLOR_COPPER, sw=1))
    f.append(rect(p1_x + 45, p1_y + 98, 45, 10, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))
    # Правий майданчик (тверда паста)
    f.append(rect(p1_x + 245, p1_y + 108, 45, 7, fill="#f9e79f", stroke=COLOR_COPPER, sw=1))
    f.append(rect(p1_x + 245, p1_y + 100, 45, 8, fill="#a6acaf", stroke=MUTED, sw=1))

    # Чіп, піднятий вертикально (кут ~55°)
    cx0, cy0 = p1_x + 80, p1_y + 100
    f.append('<g transform="rotate(-55 %d %d)">' % (cx0, cy0))
    f.append('<rect x="%d" y="%d" width="130" height="30" rx="3" fill="#34495e" stroke="#1a252f" stroke-width="1.2"/>' % (cx0 - 15, cy0 - 15))
    f.append('<rect x="%d" y="%d" width="22" height="30" rx="2" fill="#bdc3c7" stroke="#7f8c8d" stroke-width="1"/>' % (cx0 - 15, cy0 - 15))
    f.append('<rect x="%d" y="%d" width="22" height="30" rx="2" fill="#bdc3c7" stroke="#7f8c8d" stroke-width="1"/>' % (cx0 + 93, cy0 - 15))
    f.append('</g>')

    # Стрілка поверхневого натягу
    f.append(arrow(p1_x + 95, p1_y + 85, p1_x + 95, p1_y + 55, color=POS, sw=2))
    f.append(text(p1_x + 105, p1_y + 65, "F_тяг", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(p1_x + pw / 2, p1_y + 138, "Лівий контакт розплавився раніше → затягнув чіп", size=9.5, color=MUTED))

    # ── Панель 2: Бусини припою (Solder Beading) ──
    p2_x, p2_y = 390, 65
    f.append(rect(p2_x, p2_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p2_x + pw / 2, p2_y + 18, "2. Бусини припою (Solder Beading)", size=11.5, color=POS, bold=True))

    # Плата
    f.append(rect(p2_x + 20, p2_y + 115, pw - 40, 16, fill="#d5f5e3", stroke=COLOR_FR4, sw=1.2))
    # Майданчики
    f.append(rect(p2_x + 50, p2_y + 108, 45, 7, fill="#f9e79f", stroke=COLOR_COPPER, sw=1))
    f.append(rect(p2_x + 250, p2_y + 108, 45, 7, fill="#f9e79f", stroke=COLOR_COPPER, sw=1))
    # Припій
    f.append(rect(p2_x + 50, p2_y + 98, 45, 10, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))
    f.append(rect(p2_x + 250, p2_y + 98, 45, 10, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))

    # Чіп горизонтально
    f.append(rect(p2_x + 75, p2_y + 78, 195, 25, fill="#34495e", stroke="#1a252f", sw=1.2, rx=3))
    # Металізація
    f.append(rect(p2_x + 75, p2_y + 78, 25, 25, fill="#bdc3c7", stroke="#7f8c8d", sw=1, rx=2))
    f.append(rect(p2_x + 245, p2_y + 78, 25, 25, fill="#bdc3c7", stroke="#7f8c8d", sw=1, rx=2))

    # Бусина припою під чіпом посередині
    f.append(circle(p2_x + 172, p2_y + 105, 9, fill="#95a5a6", stroke=POS, sw=1.8))
    f.append(text(p2_x + 172, p2_y + 68, "Кулька під чіпом", size=10, color=POS, bold=True))
    f.append(text(p2_x + pw / 2, p2_y + 138, "Витискання пасти під корпус + швидкий preheat", size=9.5, color=MUTED))

    # ── Панель 3: Пустоти (Voids) під Thermal Pad ──
    p3_x, p3_y = 25, 225
    f.append(rect(p3_x, p3_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p3_x + pw / 2, p3_y + 18, "3. Пустоти (Voids) у паяному шві", size=11.5, color=POS, bold=True))

    # Плата
    f.append(rect(p3_x + 20, p3_y + 115, pw - 40, 16, fill="#d5f5e3", stroke=COLOR_FR4, sw=1.2))
    # Широкий Thermal Pad
    f.append(rect(p3_x + 60, p3_y + 108, pw - 120, 7, fill="#f9e79f", stroke=COLOR_COPPER, sw=1))
    # Шар припою
    f.append(rect(p3_x + 60, p3_y + 92, pw - 120, 16, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))
    # Пустоти (газові каверни)
    f.append(circle(p3_x + 110, p3_y + 100, 5, fill="#ffffff", stroke=POS, sw=1.5))
    f.append(circle(p3_x + 170, p3_y + 99, 7, fill="#ffffff", stroke=POS, sw=1.5))
    f.append(circle(p3_x + 225, p3_y + 101, 6, fill="#ffffff", stroke=POS, sw=1.5))

    # Корпус QFN зверху
    f.append(rect(p3_x + 50, p3_y + 60, pw - 100, 32, fill="#2c3e50", stroke="#1a252f", sw=1.2, rx=3))
    f.append(text(p3_x + pw / 2, p3_y + 78, "Корпус QFN / PowerPAD", size=10.5, color="#ffffff", bold=True))
    f.append(text(p3_x + pw / 2, p3_y + 138, "Пари флюсу замкнені під великою площадкою (>25% void)", size=9.5, color=MUTED))

    # ── Панель 4: Деформація (Warpage & Head-in-Pillow) ──
    p4_x, p4_y = 390, 225
    f.append(rect(p4_x, p4_y, pw, ph, fill="#fdfefe", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(p4_x + pw / 2, p4_y + 18, "4. Вигин (Warpage) і Head-in-Pillow", size=11.5, color=POS, bold=True))

    # Вигнута плата (дуга)
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="8"/>' %
             (p4_x + 30, p4_y + 125, p4_x + pw / 2, p4_y + 115, p4_x + pw - 30, p4_y + 125, COLOR_FR4))

    # Вигнутий BGA чіп (дуга в інший бік через різницю CTE)
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="12"/>' %
             (p4_x + 40, p4_y + 65, p4_x + pw / 2, p4_y + 75, p4_x + pw - 40, p4_y + 65, COLOR_CHIP))
    f.append(text(p4_x + pw / 2, p4_y + 60, "BGA мікросхема (вигин вгору)", size=10, color="#ffffff", bold=True))

    # Кульки BGA: крайні відірвані, середні сплющені
    # Крайня ліва (Head-in-pillow: кулька окремо від пасти)
    f.append(circle(p4_x + 60, p4_y + 80, 5, fill="#bdc3c7", stroke=COLOR_SOLDER, sw=1))
    f.append(circle(p4_x + 60, p4_y + 116, 4, fill=COLOR_SOLDER_LIQ, stroke=POS, sw=1.2))

    # Середні кульки (замкнені/нормальні)
    f.append(circle(p4_x + 135, p4_y + 94, 6, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))
    f.append(circle(p4_x + 172, p4_y + 96, 6, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))
    f.append(circle(p4_x + 210, p4_y + 94, 6, fill=COLOR_SOLDER_LIQ, stroke=COLOR_SOLDER, sw=1))

    # Крайня права (відрив)
    f.append(circle(p4_x + 285, p4_y + 80, 5, fill="#bdc3c7", stroke=COLOR_SOLDER, sw=1))
    f.append(circle(p4_x + 285, p4_y + 116, 4, fill=COLOR_SOLDER_LIQ, stroke=POS, sw=1.2))

    f.append(text(p4_x + 60, p4_y + 102, "відрив", size=9, color=POS, bold=True))
    f.append(text(p4_x + 285, p4_y + 102, "відрив", size=9, color=POS, bold=True))

    f.append(text(p4_x + pw / 2, p4_y + 138, "Різниця CTE вигинає чіп і плату → дефект «голова на подушці»", size=9.5, color=MUTED))

    render(os.path.join(IMG, 'reflow-defects-anatomy.svg'), W, H, *f)


if __name__ == "__main__":
    fig_thermal_profile()
    fig_wetting_and_imc()
    fig_defects()
    print("OK: 3 фігури у", IMG)
