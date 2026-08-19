# -*- coding: utf-8 -*-
"""Фігури до теми «Типи діодів і їхні відмінності».
Генерує векторні ілюстрації:
  1. iv-curves-comparison.svg — порівняння вольт-амперних характеристик сімейств діодів
  2. reverse-recovery-dynamics.svg — процес зворотного відновлення (Standard vs Fast vs Schottky)
  3. zener-avalanche-tco.svg — фізика стабілітронів: тунельний Зенер проти лавинного пробою та ТКН
  4. pin-and-varactor-physics.svg — внутрішня будова та фізичні моделі варикапа і PIN-діода

Запуск: python figs.py
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: iv-curves-comparison.svg ────────────────────────────────────────
def fig_iv_curves():
    W, H = 880, 520
    f = [text(W / 2, 28, "Порівняльна вольт-амперна характеристика напівпровідникових діодів",
              size=16, bold=True)]

    # Координатні осі
    ox, oy = 380, 310
    w_left, w_right = 320, 440
    h_top, h_bot = 240, 160

    # Сітка / осі
    f.append(line(ox - w_left, oy, ox + w_right, oy, color=LINE, sw=1.6))
    f.append(line(ox, oy + h_bot, ox, oy - h_top, color=LINE, sw=1.6))
    f.append(text(ox + w_right + 15, oy + 4, "U_D (В)", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(ox - 10, oy - h_top - 12, "I_D (А / мА)", size=12, color=INK, bold=True, anchor="end"))

    # 1. Діод Шотткі (кремнієвий): поріг 0.25–0.35 В, круте наростання, вищий зворотний витік
    pts_sch = []
    for i in range(0, 101):
        v = i * 0.007  # 0 to 0.7 V
        if v < 0.2:
            i_val = 0.02 * (v / 0.2)
        else:
            i_val = 0.02 + 4.5 * math.pow((v - 0.2) / 0.4, 2.8)
        y = oy - min(h_top - 20, i_val * 38)
        x = ox + v * 280
        pts_sch.append("%.1f,%.1f" % (x, y))
    # Зворотна вітка Шотткі: помітний витік
    pts_sch_rev = ["%.1f,%.1f" % (ox - 160, oy + 24), "%.1f,%.1f" % (ox - 80, oy + 18), "%.1f,%.1f" % (ox, oy)]
    f.append('<path d="M %s L %s" fill="none" stroke="#2457d6" stroke-width="2.6"/>' %
             (" L ".join(pts_sch_rev), " L ".join(pts_sch)))

    # 2. Стандартний кремнієвий випрямляч (Standard Recovery PN): поріг ~0.7–0.8 В
    pts_std = []
    for i in range(0, 101):
        v = i * 0.012  # 0 to 1.2 V
        if v < 0.6:
            i_val = 0.005 * (v / 0.6)
        else:
            i_val = 0.005 + 4.5 * math.pow((v - 0.6) / 0.45, 2.5)
        y = oy - min(h_top - 20, i_val * 38)
        x = ox + v * 200
        pts_std.append("%.1f,%.1f" % (x, y))
    pts_std_rev = ["%.1f,%.1f" % (ox - 280, oy + 4), "%.1f,%.1f" % (ox, oy)]
    f.append('<path d="M %s L %s" fill="none" stroke="#c0392b" stroke-width="2.6"/>' %
             (" L ".join(pts_std_rev), " L ".join(pts_std)))

    # 3. Швидкодіючий діод (Ultra-Fast PN): поріг ~1.2–1.5 В через центри рекомбінації
    pts_fast = []
    for i in range(0, 101):
        v = i * 0.018  # 0 to 1.8 V
        if v < 1.0:
            i_val = 0.005 * (v / 1.0)
        else:
            i_val = 0.005 + 4.5 * math.pow((v - 1.0) / 0.6, 2.3)
        y = oy - min(h_top - 20, i_val * 38)
        x = ox + v * 160
        pts_fast.append("%.1f,%.1f" % (x, y))
    f.append('<path d="M %.1f,%.1f L %s" fill="none" stroke="#7a4e8a" stroke-width="2.4" stroke-dasharray="6,3"/>' %
             (ox, oy, " L ".join(pts_fast)))

    # 4. Стабілітрон (Zener / Avalanche): пряма вітка як у PN, зворотна — різкий пробій при V_Z
    pts_zen = []
    vz_x = ox - 110  # точка V_Z
    pts_zen.append("%.1f,%.1f" % (vz_x, oy + h_bot - 20))
    pts_zen.append("%.1f,%.1f" % (vz_x, oy + 12))
    pts_zen.append("%.1f,%.1f" % (ox - 20, oy + 2))
    pts_zen.append("%.1f,%.1f" % (ox, oy))
    f.append('<path d="M %s" fill="none" stroke="#27ae60" stroke-width="2.6"/>' % (" L ".join(pts_zen)))

    # 5. Тунельний діод: ділянка від'ємного опору при малих прямих напругах
    pts_tun = [
        (ox, oy),
        (ox + 16, oy - 70),   # Піковий струм I_P
        (ox + 35, oy - 24),   # Струм западини I_V
        (ox + 70, oy - 65),
        (ox + 105, oy - 180)
    ]
    tun_path = "M " + " L ".join(["%.1f,%.1f" % p for p in pts_tun])
    f.append('<path d="%s" fill="none" stroke="#d97706" stroke-width="2.4" stroke-dasharray="4,2"/>' % tun_path)

    # Підписи точок та кривих
    f.append(text(ox + 85, oy - 195, "Шотткі (Si): V_F ≈ 0.3 В", size=11, color="#2457d6", bold=True, anchor="start"))
    f.append(text(ox + 175, oy - 165, "Стандартний PN: V_F ≈ 0.7–0.9 В", size=11, color="#c0392b", bold=True, anchor="start"))
    f.append(text(ox + 250, oy - 120, "Ultra-Fast PN: V_F ≈ 1.3–1.7 В", size=11, color="#7a4e8a", bold=True, anchor="start"))
    f.append(text(ox + 20, oy - 80, "Тунельний (N-подібна ВАХ)", size=10, color="#d97706", bold=True, anchor="start"))
    f.append(text(vz_x - 12, oy + 90, "Стабілітрон (пробій V_Z)", size=11, color="#27ae60", bold=True, anchor="end"))
    f.append(text(ox - 120, oy + 38, "витік Шотткі (I_R >> 1 мкА)", size=10, color="#2457d6", italic=True))

    # Виноски та маркування осей
    f.append(line(ox + 70, oy - 5, ox + 70, oy + 5, color=LINE, sw=1.5))
    f.append(text(ox + 70, oy + 18, "+0.3 В", size=10, color=MUTED))

    f.append(line(ox + 145, oy - 5, ox + 145, oy + 5, color=LINE, sw=1.5))
    f.append(text(ox + 145, oy + 18, "+0.7 В", size=10, color=MUTED))

    f.append(line(ox + 230, oy - 5, ox + 230, oy + 5, color=LINE, sw=1.5))
    f.append(text(ox + 230, oy + 18, "+1.4 В", size=10, color=MUTED))

    f.append(line(vz_x, oy - 5, vz_x, oy + 5, color=LINE, sw=1.5))
    f.append(text(vz_x, oy - 12, "-V_Z", size=11, color="#27ae60", bold=True))

    # Легенда
    leg_x, leg_y = 50, 70
    f.append(rect(leg_x, leg_y, 250, 160, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=6))
    f.append(text(leg_x + 125, leg_y + 20, "Ключові компроміси", size=12, bold=True))
    f.append(text(leg_x + 15, leg_y + 45, "• Шотткі: мін. V_F, але макс. витік I_R", size=11, color="#2457d6", anchor="start"))
    f.append(text(leg_x + 15, leg_y + 70, "• PN Standard: низький витік, t_rr ~ мкс", size=11, color="#c0392b", anchor="start"))
    f.append(text(leg_x + 15, leg_y + 95, "• Ultra-Fast: t_rr ~ нс, плата — високий V_F", size=11, color="#7a4e8a", anchor="start"))
    f.append(text(leg_x + 15, leg_y + 120, "• Zener: нормована напруга пробою V_Z", size=11, color="#27ae60", anchor="start"))
    f.append(text(leg_x + 15, leg_y + 145, "• Тунельний: від'ємний опір dV/dI < 0", size=11, color="#d97706", anchor="start"))

    render(os.path.join(IMG, "iv-curves-comparison.svg"), W, H, *f)


# ── Фігура 2: reverse-recovery-dynamics.svg ──────────────────────────────────
def fig_reverse_recovery():
    W, H = 880, 480
    f = [text(W / 2, 28, "Динаміка зворотного відновлення: чому PN-діод не вимикається миттєво",
              size=16, bold=True)]

    # Вісь часу та струму
    ox, oy = 80, 240
    f.append(line(ox, oy, 820, oy, color=LINE, sw=1.6))
    f.append(line(ox + 40, 40, ox + 40, 430, color=LINE, sw=1.6))
    f.append(text(830, oy + 4, "t (час)", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(ox + 35, 30, "i_D (струм)", size=12, color=INK, bold=True, anchor="end"))

    # Прямий струм +I_F
    f.append(line(ox + 40, oy - 120, ox + 180, oy - 120, color="#c0392b", sw=2.6))
    f.append(text(ox + 25, oy - 120 + 4, "+I_F", size=12, color="#c0392b", bold=True, anchor="end"))

    # Спад струму з фіксованою швидкістю -di/dt
    t1 = ox + 180
    t0_cross = t1 + 60      # перетин нуля
    t_peak = t0_cross + 50  # пік зворотного струму I_RRM

    # PN Standard Recovery (повільне відновлення, великий заряд Q_rr)
    pts_pn = [
        (t1, oy - 120),
        (t0_cross, oy),
        (t_peak, oy + 120),
        (t_peak + 40, oy + 80),
        (t_peak + 120, oy + 20),
        (t_peak + 220, oy)
    ]
    f.append('<path d="M %s" fill="none" stroke="#c0392b" stroke-width="2.6"/>' %
             (" L ".join(["%.1f,%.1f" % p for p in pts_pn])))

    # PN Ultra-Fast (швидке відновлення завдяки центрам рекомбінації)
    pts_uf = [
        (t1, oy - 120),
        (t0_cross, oy),
        (t0_cross + 30, oy + 55),
        (t0_cross + 65, oy + 10),
        (t0_cross + 110, oy)
    ]
    f.append('<path d="M %s" fill="none" stroke="#7a4e8a" stroke-width="2.4" stroke-dasharray="6,3"/>' %
             (" L ".join(["%.1f,%.1f" % p for p in pts_uf])))

    # Діод Шотткі (немає накопичення неосновних носіїв, тільки ємнісний сплеск перезарядки)
    pts_sch = [
        (t1, oy - 120),
        (t0_cross, oy),
        (t0_cross + 12, oy + 16),
        (t0_cross + 25, oy)
    ]
    f.append('<path d="M %s" fill="none" stroke="#2457d6" stroke-width="2.4"/>' %
             (" L ".join(["%.1f,%.1f" % p for p in pts_sch])))

    # Штрихові лінії та зони заряду
    f.append(line(t0_cross, oy, t0_cross, oy + 140, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t_peak, oy, t_peak, oy + 140, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(t_peak + 220, oy, t_peak + 220, oy + 140, color=MUTED, sw=1.2, dash="3,3"))

    # Позначення часових інтервалів
    # t_s (фаза вимивання заряду)
    f.append(arrow(t0_cross, oy + 135, t_peak, oy + 135, color=INK, sw=1.4))
    f.append(arrow(t_peak, oy + 135, t0_cross, oy + 135, color=INK, sw=1.4))
    f.append(text((t0_cross + t_peak) / 2, oy + 155, "t_s (фаза схову)", size=11, bold=True))

    # t_f (фаза спаду)
    f.append(arrow(t_peak, oy + 135, t_peak + 220, oy + 135, color=INK, sw=1.4))
    f.append(arrow(t_peak + 220, oy + 135, t_peak, oy + 135, color=INK, sw=1.4))
    f.append(text((t_peak + t_peak + 220) / 2, oy + 155, "t_f (спад струму)", size=11, bold=True))

    # Загальний t_rr
    f.append(arrow(t0_cross, oy + 175, t_peak + 220, oy + 175, color=POS, sw=1.6))
    f.append(arrow(t_peak + 220, oy + 175, t0_cross, oy + 175, color=POS, sw=1.6))
    f.append(text((t0_cross + t_peak + 220) / 2, oy + 195, "t_rr = t_s + t_f (Standard: 1–5 мкс)", size=12, color=POS, bold=True))

    # Рівень -I_RRM
    f.append(line(ox + 40, oy + 120, t_peak, oy + 120, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(ox + 25, oy + 120 + 4, "-I_RRM", size=12, color=POS, bold=True, anchor="end"))

    # Підписи кривих
    f.append(text(t_peak + 135, oy + 65, "Standard PN (1N4007): t_rr ≈ 2 мкс, великий Q_rr", size=11, color="#c0392b", bold=True, anchor="start"))
    f.append(text(t0_cross + 75, oy + 35, "Ultra-Fast (MUR460): t_rr ≈ 35 нс", size=11, color="#7a4e8a", bold=True, anchor="start"))
    f.append(text(t0_cross + 30, oy - 20, "Schottky: t_rr ≈ 0 (лише заряд C_j)", size=11, color="#2457d6", bold=True, anchor="start"))

    # Блок пояснення фізики
    f.append(fitbox(520, 60, 330, 95,
                    "Фізика t_rr:\n1. При I_F база затоплена неосновними носіями.\n2. При зміні напруги носії мають витекти або рекомбінувати.\n3. Поки заряд Q_rr не зникне, діод проводить у ЗВОРОТНИЙ бік!",
                    size=11, fill="#fdf8e2", stroke="#d97706", color=INK))

    render(os.path.join(IMG, "reverse-recovery-dynamics.svg"), W, H, *f)


# ── Фігура 3: zener-avalanche-tco.svg ─────────────────────────────────────────
def fig_zener_avalanche():
    W, H = 880, 460
    f = [text(W / 2, 28, "Фізика стабілітронів: квантовий тунельний ефект проти лавинного множення",
              size=16, bold=True)]

    # Ліва панель: Тунельний пробій Зенера (V_Z < 5 В)
    pL_x, pL_y, pL_w, pL_h = 30, 55, 390, 380
    f.append(rect(pL_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pL_x + pL_w / 2, pL_y + 24, "Тунельний пробій Зенера (V_Z < 5.1 В)", size=13, color="#27ae60", bold=True))

    f.append(fitbox(pL_x + 15, pL_y + 40, pL_w - 30, 65,
                    "• Високе легування (N_A, N_D > 10¹⁸ см⁻³)\n• Збіднений шар ультратонкий: W < 10 нм\n• Напруженість поля величезна: E > 10⁶ В/см",
                    size=11, fill="#eef6ef", stroke="#27ae60", color=INK))

    # Зонна діаграма тунелювання
    bx, by = pL_x + 30, pL_y + 120
    f.append(rect(bx, by, 330, 140, fill="#f9fafb", stroke=LINE, sw=1.2, rx=4))
    f.append(text(bx + 165, by + 18, "Зонна діаграма під сильною зворотною напругою", size=10, color=MUTED, bold=True))

    # p-зона (валентна зона піднята вгору)
    f.append(rect(bx + 15, by + 35, 100, 35, fill="#dbeafe", stroke="#2457d6", sw=1.2))
    f.append(text(bx + 65, by + 57, "Валентна p-зона", size=10, color="#2457d6", bold=True))

    # n-зона (зона провідності опущена вниз)
    f.append(rect(bx + 215, by + 85, 100, 35, fill="#fee2e2", stroke="#c0392b", sw=1.2))
    f.append(text(bx + 265, by + 107, "Зона провідн. n", size=10, color="#c0392b", bold=True))

    # Стрілка тунелювання через тонкий бар'єр
    f.append(arrow(bx + 115, by + 52, bx + 215, by + 102, color="#27ae60", sw=2.4))
    f.append(text(bx + 165, by + 72, "Квантове", size=10, color="#27ae60", bold=True))
    f.append(text(bx + 165, by + 86, "тунелювання", size=10, color="#27ae60", bold=True))

    # ТКН
    f.append(fitbox(pL_x + 15, pL_y + 275, pL_w - 30, 85,
                    "Температурний коефіцієнт (ТКН < 0):\nЗ нагріванням заборонена зона E_g звужується,\nелектронам легше тунелювати → напруга V_Z ПАДАЄ.\nТКН ≈ -1.5 ... -2 мВ/°C",
                    size=11, fill="#fdf2f2", stroke="#c0392b", color=INK))

    # Права панель: Лавинний пробій (V_Z > 6 В)
    pR_x = 460
    f.append(rect(pR_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pR_x + pL_w / 2, pL_y + 24, "Лавинний пробій (Avalanche, V_Z > 5.6 В)", size=13, color="#2457d6", bold=True))

    f.append(fitbox(pR_x + 15, pL_y + 40, pL_w - 30, 65,
                    "• Помірне легування (N_A, N_D < 10¹⁷ см⁻³)\n• Збіднений шар ширший: W > 100 нм\n• Носії встигають розігнатися до енергії іонізації",
                    size=11, fill="#eff6ff", stroke="#2457d6", color=INK))

    # Схема ударної іонізації
    bx2 = pR_x + 30
    f.append(rect(bx2, by, 330, 140, fill="#f9fafb", stroke=LINE, sw=1.2, rx=4))
    f.append(text(bx2 + 165, by + 18, "Ударна іонізація кристалічної ґратки", size=10, color=MUTED, bold=True))

    # Електрон розганяється полем і вибиває нову пару e⁻/h⁺
    f.append(circle(bx2 + 40, by + 70, 7, fill="#2457d6", stroke=LINE, sw=1.2))
    f.append(text(bx2 + 40, by + 74, "e⁻", size=9, color="#ffffff", bold=True))
    f.append(arrow(bx2 + 50, by + 70, bx2 + 140, by + 70, color=LINE, sw=2.0))
    f.append(text(bx2 + 95, by + 60, "розгін полем E", size=10, color=MUTED))

    # Атом ґратки
    f.append(circle(bx2 + 160, by + 70, 12, fill="#fef3c7", stroke="#d97706", sw=1.6))
    f.append(text(bx2 + 160, by + 74, "Si", size=10, color="#d97706", bold=True))

    # Народжені носії лавини
    f.append(arrow(bx2 + 175, by + 65, bx2 + 250, by + 45, color="#2457d6", sw=1.8))
    f.append(circle(bx2 + 260, by + 43, 6, fill="#2457d6", stroke=LINE, sw=1.0))
    f.append(text(bx2 + 285, by + 47, "e⁻", size=10, color="#2457d6", bold=True))

    f.append(arrow(bx2 + 175, by + 75, bx2 + 250, by + 95, color="#c0392b", sw=1.8))
    f.append(circle(bx2 + 260, by + 97, 6, fill="#c0392b", stroke=LINE, sw=1.0))
    f.append(text(bx2 + 285, by + 101, "h⁺", size=10, color="#c0392b", bold=True))

    # ТКН лавинного пробою
    f.append(fitbox(pR_x + 15, pL_y + 275, pL_w - 30, 85,
                    "Температурний коефіцієнт (ТКН > 0):\nЗ нагріванням коливання ґратки розсіюють електрони,\nдовжина вільного пробігу падає → потрібна більша V_Z.\nТКН ≈ +2 ... +5 мВ/°C (ідеальний баланс біля 5.6 В!)",
                    size=11, fill="#eff6ff", stroke="#2457d6", color=INK))

    render(os.path.join(IMG, "zener-avalanche-tco.svg"), W, H, *f)


# ── Фігура 4: pin-and-varactor-physics.svg ────────────────────────────────────
def fig_pin_varactor():
    W, H = 880, 480
    f = [text(W / 2, 28, "Спеціальні діоди: варикапи (керована ємність) та PIN-діоди (ВЧ-комутація)",
              size=16, bold=True)]

    # Ліва панель: Варикап
    pL_x, pL_y, pL_w, pL_h = 30, 55, 390, 400
    f.append(rect(pL_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pL_x + pL_w / 2, pL_y + 24, "Варикап (Varactor Diode)", size=13, color="#7a4e8a", bold=True))

    # Будова кристала з бар'єрною ємністю C_j
    vx, vy = pL_x + 25, pL_y + 45
    f.append(rect(vx, vy, 100, 70, fill="#fee2e2", stroke="#c0392b", sw=1.4))
    f.append(text(vx + 50, vy + 40, "p⁺-шар", size=12, color="#c0392b", bold=True))

    # Збіднений шар (діелектрик конденсатора)
    f.append(rect(vx + 100, vy, 140, 70, fill="#f3f4f6", stroke=LINE, sw=1.4))
    f.append(text(vx + 170, vy + 32, "Збіднений шар W", size=11, color=INK, bold=True))
    f.append(text(vx + 170, vy + 50, "C_j = ε·A / W(V_R)", size=11, color="#7a4e8a", bold=True))

    f.append(rect(vx + 240, vy, 100, 70, fill="#dbeafe", stroke="#2457d6", sw=1.4))
    f.append(text(vx + 290, vy + 40, "n-шар", size=12, color="#2457d6", bold=True))

    # Зворотна напруга V_R керує шириною W
    f.append(arrow(vx + 170, vy + 85, vx + 105, vy + 85, color=POS, sw=1.6))
    f.append(arrow(vx + 170, vy + 85, vx + 235, vy + 85, color=POS, sw=1.6))
    f.append(text(vx + 170, vy + 105, "V_R зростає → W ширшає → C_j падає", size=11, color=POS, bold=True))

    # Графік C(V_R)
    gx, gy = pL_x + 40, pL_y + 185
    f.append(line(gx, gy + 80, gx + 280, gy + 80, color=LINE, sw=1.4))
    f.append(line(gx, gy + 80, gx, gy, color=LINE, sw=1.4))
    f.append(text(gx + 290, gy + 84, "V_R (В)", size=10, color=INK, bold=True, anchor="start"))
    f.append(text(gx - 8, gy - 4, "C_j (пФ)", size=10, color=INK, bold=True, anchor="end"))

    # Гіперболічна крива ємності C_j(V)
    pts_c = []
    for i in range(0, 51):
        v = i * 0.4  # 0..20 V
        c_val = 60.0 / math.sqrt(1 + v / 0.7)
        x = gx + v * 13.0
        y = gy + 80 - c_val * 1.1
        pts_c.append("%.1f,%.1f" % (x, y))
    f.append('<path d="M %s" fill="none" stroke="#7a4e8a" stroke-width="2.4"/>' % (" L ".join(pts_c)))
    f.append(text(gx + 120, gy + 30, "C_j ∝ 1 / √(V_R + V_bi)", size=11, color="#7a4e8a", bold=True))

    f.append(fitbox(pL_x + 15, pL_y + 290, pL_w - 30, 95,
                    "Застосування варикапів:\n• ГУН (VCO) у синтезаторах частоти PLL\n• Електронне перестроювання FM/ВЧ-фільтрів\n• Коефіцієнт перекриття: C_max/C_min ≈ 2...10\n• Висока добротність Q для мін. фазового шуму",
                    size=11, fill="#fdf4ff", stroke="#7a4e8a", color=INK))

    # Права панель: PIN-діод
    pR_x = 460
    f.append(rect(pR_x, pL_y, pL_w, pL_h, fill="#ffffff", stroke="#c9d3dc", sw=1.4, rx=8))
    f.append(text(pR_x + pL_w / 2, pL_y + 24, "PIN-діод (ВЧ/СВЧ атенюатори та ключі)", size=13, color="#2457d6", bold=True))

    # Структура PIN (p - i - n)
    px, py = pR_x + 25, pL_y + 45
    f.append(rect(px, py, 90, 70, fill="#fee2e2", stroke="#c0392b", sw=1.4))
    f.append(text(px + 45, py + 40, "p⁺ (анод)", size=11, color="#c0392b", bold=True))

    # Нелегований i-шар (intrinsic)
    f.append(rect(px + 90, py, 160, 70, fill="#fef9c3", stroke="#ca8a04", sw=1.6))
    f.append(text(px + 170, py + 30, "i-область (Intrinsic)", size=12, color="#ca8a04", bold=True))
    f.append(text(px + 170, py + 50, "широкий нелегований шар", size=10, color=MUTED))

    f.append(rect(px + 250, py, 90, 70, fill="#dbeafe", stroke="#2457d6", sw=1.4))
    f.append(text(px + 295, py + 40, "n⁺ (катод)", size=11, color="#2457d6", bold=True))

    # Фізичний механізм на ВЧ
    f.append(fitbox(pR_x + 15, pL_y + 130, pL_w - 30, 140,
                    "Два режими роботи PIN-діода:\n1. Постійний / НЧ струм: звичайний діод із накопиченням заряду в товстому i-шарі.\n2. ВЧ/СВЧ сигнал (f > 10 МГц): період сигналу Т << часу життя носіїв τ. Носії не встигають розсмоктатися!\n→ Діод поводиться як чистий лінійний резистор R_d без нелінійних спотворень сигналу!",
                    size=11, fill="#fefce8", stroke="#ca8a04", color=INK))

    # Формула ВЧ-опору
    f.append(rect(pR_x + 35, pL_y + 285, pL_w - 70, 45, fill="#eff6ff", stroke="#2457d6", sw=1.4, rx=6))
    f.append(text(pR_x + pL_w / 2, pL_y + 312, "R_ВЧ ≈ W_i² / (2 · μ · τ · I_DC)  ∝  1 / I_прямий", size=12, color="#2457d6", bold=True))

    f.append(fitbox(pR_x + 15, pL_y + 345, pL_w - 30, 50,
                    "Застосування PIN-діода:\n• Безінерційний керований ВЧ-атенюатор\n• Швидкі антенні перемикачі прийому/передачі (T/R Switch)",
                    size=10, fill="#ffffff", stroke="#c9d3dc", color=MUTED))

    render(os.path.join(IMG, "pin-and-varactor-physics.svg"), W, H, *f)


if __name__ == "__main__":
    fig_iv_curves()
    fig_reverse_recovery()
    fig_zener_avalanche()
    fig_pin_varactor()
    print("OK: generated 4 figures -> img/")
