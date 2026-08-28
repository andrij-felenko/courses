# -*- coding: utf-8 -*-
"""Фігури для теми esd-sensitivity-levels:
1. img/hbm-vs-cdm-current-waveforms.svg — порівняння часових та амплітудних характеристик струму розрядів HBM, CDM та системного IEC 61000-4-2.
2. img/tvs-diode-clamping-dynamic-resistance.svg — ВАХ TVS-діода (TLP), динамічний опір R_dyn, ефект snapback та обмеження напруги Clamping Voltage."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама
CLR_HBM    = "#2563eb"  # Синій: HBM (помірний струм, довгий імпульс)
CLR_CDM    = "#d97706"  # Помаранчевий: CDM (надшвидкий субнаносекундний сплеск)
CLR_IEC    = "#dc2626"  # Червоний: IEC 61000-4-2 (руйнівний пік 30 А)
CLR_IC     = "#7c3aed"  # Фіолетовий: Вразливий кристал / лінія IC
CLR_SAFE   = "#16a34a"  # Зелений: Безпечна зона
TEXT_DARK  = "#0f172a"
TEXT_MUTED = "#475569"


def fig_hbm_vs_cdm_waveforms():
    W, H = 860, 440
    frags = []

    # Головне тло та рамка
    frags.append(rect(15, 15, 830, 410, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(430, 38, "Порівняння імпульсів струму ESD: HBM, CDM та IEC 61000-4-2", size=14, color=TEXT_DARK, bold=True))

    # Ліва область: Осцилограма форми струму I(t)
    ox, oy = 85, 345
    gw, gh = 430, 260
    frags.append(rect(35, 60, 495, 345, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(282, 80, "Часова форма розрядного струму I(t)", size=11, color=TEXT_DARK, bold=True))

    # Сітка та осі
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    frags.append(text(ox + gw - 10, oy + 22, "Час t, нс", size=9, color=TEXT_MUTED, bold=True))
    frags.append(text(ox - 8, oy - gh + 15, "Струм I, А", size=9, color=TEXT_MUTED, bold=True, anchor="end"))

    # Позначки на осі Y (струм до 35 А)
    for amp, lbl in [(5, "5"), (10, "10"), (15, "15"), (20, "20"), (30, "30 A")]:
        y_pos = oy - (amp / 35.0) * 220
        frags.append(line(ox - 3, y_pos, ox + gw, y_pos, color="#e2e8f0", sw=1, dash="3,3"))
        frags.append(text(ox - 6, y_pos + 3, lbl, size=9, color=TEXT_MUTED, anchor="end"))

    # Позначки на осі X (нелінійна шкала для наочності: 1, 2, 10, 30, 60, 120 нс)
    for x_pos, lbl in [(ox + 25, "1"), (ox + 55, "2"), (ox + 120, "10"), (ox + 220, "30"), (ox + 330, "60"), (ox + 410, "120")]:
        frags.append(line(x_pos, oy, x_pos, oy + 4, color=LINE, sw=1.2))
        frags.append(text(x_pos, oy + 16, lbl, size=9, color=TEXT_MUTED))

    # 1. IEC 61000-4-2 (8 кВ контактний розряд: пік 30 А при 0.8 нс, спад, другий пік 16 А при 30 нс, хвіст до 100+ нс)
    frags.append('<path d="M 85 345 C 90 320 98 157 105 157 C 115 157 140 250 175 265 C 230 280 280 255 305 255 C 360 255 440 315 495 338" fill="none" stroke="%s" stroke-width="2.6"/>' % CLR_IEC)

    # 2. CDM (Charged Device Model: 500 В, пік 12 А, тривалість < 2 нс)
    frags.append('<path d="M 85 345 C 87 310 90 270 92 270 C 94 270 97 325 105 345" fill="none" stroke="%s" stroke-width="2.4"/>' % CLR_CDM)

    # 3. HBM (Human Body Model: 2 кВ, 100 пФ + 1500 Ом, пік 1.33 А при 10 нс, тривалість ~150 нс)
    frags.append('<path d="M 85 345 C 105 337 135 336 170 336 C 250 336 370 340 495 344" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' % CLR_HBM)

    # Виносні покажчики на графіку
    frags.append(text(122, 142, "IEC 61000-4-2 (8 кВ): I_pk = 30 А (t_r < 1 нс)", size=9, color=CLR_IEC, bold=True, anchor="start"))
    frags.append(text(108, 245, "CDM (500 В): I_pk = 12 А (t_r < 0.3 нс)", size=9, color=CLR_CDM, bold=True, anchor="start"))
    frags.append(text(210, 328, "HBM (2 кВ): I_pk = 1.33 А (t_r = 10 нс, τ ≈ 150 нс)", size=9, color=CLR_HBM, bold=True, anchor="start"))

    # Права область: Зведена таблиця та порівняльна декомпозиція моделей
    frags.append(rect(545, 60, 285, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(687, 82, "Порівняльні параметри моделей", size=12, color=TEXT_DARK, bold=True))

    rows_data = [
        ("Human Body Model (HBM)", True, CLR_HBM),
        ("• Стандарт: ANSI/ESDA/JEDEC JS-001", False, TEXT_MUTED),
        ("• R-C ланцюг: 100 пФ / 1500 Ом", False, TEXT_DARK),
        ("• Фронт t_r: 2–10 нс | Пік: 1.33 А (при 2 кВ)", False, TEXT_DARK),
        ("• Механізм: теплове вигоряння p-n переходу", False, TEXT_MUTED),
        ("", False, TEXT_MUTED),
        ("Charged Device Model (CDM)", True, CLR_CDM),
        ("• Стандарт: ANSI/ESDA/JEDEC JS-002", False, TEXT_MUTED),
        ("• R-C ланцюг: 1–30 пФ / < 1 Ом (без резистора)", False, TEXT_DARK),
        ("• Фронт t_r: 0.15–0.4 нс | Пік: до 15 А", False, TEXT_DARK),
        ("• Механізм: пробій підзатворного оксиду SiO2", False, TEXT_MUTED),
        ("", False, TEXT_MUTED),
        ("Системний рівень (IEC 61000-4-2)", True, CLR_IEC),
        ("• R-C ланцюг: 150 пФ / 330 Ом", False, TEXT_DARK),
        ("• Фронт t_r: 0.7–1.0 нс | Пік: 30 А (при 8 кВ)", False, TEXT_DARK),
        ("• Енергія: у 24 рази більша за HBM (4.8 мДж)", False, CLR_IEC)
    ]

    curr_y = 104
    for title, is_head, col in rows_data:
        if not title:
            curr_y += 6
            continue
        sz = 10 if is_head else 9
        frags.append(text(555, curr_y, title, size=sz, color=col, anchor="start", bold=is_head))
        curr_y += 16

    render(os.path.join(OUT, "hbm-vs-cdm-current-waveforms.svg"), W, H, *frags)


def fig_tvs_clamping_dynamics():
    W, H = 860, 440
    frags = []

    # Головне тло та рамка
    frags.append(rect(15, 15, 830, 410, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(430, 38, "ВАХ TVS-діода: ефект Snapback, динамічний опір R_dyn та Clamping", size=14, color=TEXT_DARK, bold=True))

    # Лівий блок: Вольт-амперна характеристика TLP (Transmission Line Pulse)
    frags.append(rect(35, 60, 420, 345, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    frags.append(text(245, 82, "TLP-крива TVS-діода (лавинний пробій та Snapback)", size=11, color=TEXT_DARK, bold=True))

    # Осі ВАХ
    ox, oy = 75, 350
    gw, gh = 360, 240
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    frags.append(text(ox + gw - 10, oy + 22, "Напруга V, В", size=9, color=TEXT_MUTED, bold=True))
    frags.append(text(ox - 8, oy - gh + 15, "Струм I_PP, А", size=9, color=TEXT_MUTED, bold=True, anchor="end"))

    # Позначки напруги на осі X: V_RWM, V_BR, V_hold, V_trig, V_clamp, V_fail
    x_rwm   = 145  # V_RWM = 3.3 В
    x_br    = 195  # V_BR = 5.0 В
    x_hold  = 165  # V_hold = 4.0 В (для snapback)
    x_trig  = 235  # V_trig = 7.5 В (тригерна напруга)
    x_clamp = 265  # V_clamp = 9.0 В при 16 А
    x_fail  = 340  # V_fail_IC = 12.0 В (межа виходу з ладу входу IC)

    # Вертикальна червона зона небезпеки (руйнування IC)
    frags.append(rect(x_fail, oy - gh + 25, (ox + gw) - x_fail, gh - 25, fill="#fee2e2", stroke="none"))
    frags.append(line(x_fail, oy, x_fail, oy - gh + 25, color=CLR_IEC, sw=1.5, dash="4,3"))
    frags.append(text(x_fail + 4, oy - gh + 38, "Поріг пробою IC (V_fail)", size=9, color=CLR_IEC, anchor="start", bold=True))

    # 1. Традиційний Zener TVS (без snapback)
    frags.append('<path d="M 75 350 L 195 350 L 290 145" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,3"/>')
    frags.append(text(295, 140, "Non-snapback TVS", size=9, color="#2563eb", anchor="start", bold=True))

    # 2. Snapback TVS
    frags.append('<path d="M 75 350 L 235 350 L 235 320 L 165 300 L 255 145" fill="none" stroke="%s" stroke-width="2.8"/>' % CLR_SAFE)
    frags.append(text(215, 135, "Snapback TVS", size=9, color=CLR_SAFE, anchor="end", bold=True))

    # Позначення точок на Snapback кривій
    frags.append(circle(x_trig, 320, 3.5, fill="#dc2626", stroke=LINE, sw=1))
    frags.append(text(x_trig + 5, 318, "V_t1 (Trigger)", size=9, color=CLR_IEC, anchor="start", bold=True))

    frags.append(circle(x_hold, 300, 3.5, fill="#16a34a", stroke=LINE, sw=1))
    frags.append(text(x_hold - 5, 298, "V_h (Holding)", size=9, color=CLR_SAFE, anchor="end", bold=True))

    # Трикутник динамічного опору R_dyn
    frags.append(line(210, 220, 240, 220, color="#d97706", sw=1.2, dash="2,2"))
    frags.append(line(240, 220, 240, 170, color="#d97706", sw=1.2, dash="2,2"))
    frags.append(text(248, 195, "R_dyn = ΔV / ΔI", size=9, color="#d97706", anchor="start", bold=True))

    # Позначки напруг на осі X
    frags.append(text(x_rwm, oy + 15, "V_RWM", size=9, color=TEXT_MUTED))
    frags.append(text(x_hold, oy + 26, "V_h", size=9, color=CLR_SAFE, bold=True))
    frags.append(text(x_trig, oy + 15, "V_t1", size=9, color=CLR_IEC, bold=True))
    frags.append(text(x_clamp, oy + 26, "V_clamp", size=9, color=TEXT_DARK, bold=True))

    # Правий блок: Розрахунок Clamping Voltage та формули
    frags.append(rect(470, 60, 360, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(650, 82, "Анатомія обмеження напруги (Clamping)", size=12, color=TEXT_DARK, bold=True))

    # Формула розрахунку V_clamp
    frags.append(rect(485, 100, 330, 65, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(650, 118, "Залишкова напруга на захищуваній лінії:", size=9, color=TEXT_MUTED))
    frags.append(text(650, 138, "V_clamp(t) = V_hold + I_PP(t) · R_dyn + L_par · (di/dt)", size=10, color=CLR_IEC, bold=True))
    frags.append(text(650, 153, "де L_par · (di/dt) — індуктивний стрибок паразитної траси", size=9, color=TEXT_MUTED))

    # Порівняння Snapback vs Non-Snapback
    frags.append(rect(485, 175, 330, 215, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(650, 195, "Чому Snapback критичний для сучасної логіки:", size=10, color=TEXT_DARK, bold=True))

    details = [
        ("• Менша напруга V_clamp:", "V_hold (3.5 В) замість V_BR (6.5 В)", True),
        ("• Нижчий опір R_dyn:", "0.15–0.3 Ом проти 0.8–1.5 Ом у звичайних", False),
        ("• Захист ультратонкого оксиду:", "V_clamp < V_breakdown кристала IC", False),
        ("• Головне застереження:", "V_hold мусить бути > V_supply_max,", True),
        ("", "інакше виникає Latch-up (коротке замикання)", False),
        ("• Паразитна індуктивність L_par:", "кожен 1 мм доріжки = ~1 нГн,", True),
        ("", "при di/dt = 30 А/нс дає викид +30 В на кристал!", False)
    ]

    dy_c = 216
    for title, desc, is_b in details:
        if title:
            frags.append(text(495, dy_c, title, size=9, color=CLR_IEC if "застереження" in title else TEXT_DARK, anchor="start", bold=True))
            frags.append(text(635, dy_c, desc, size=9, color=TEXT_MUTED, anchor="start"))
        else:
            frags.append(text(505, dy_c, desc, size=9, color=CLR_IEC if "Latch-up" in desc else TEXT_MUTED, anchor="start", italic=True))
        dy_c += 17

    render(os.path.join(OUT, "tvs-diode-clamping-dynamic-resistance.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hbm_vs_cdm_waveforms()
    fig_tvs_clamping_dynamics()
    print("OK: generated figures for esd-sensitivity-levels")
