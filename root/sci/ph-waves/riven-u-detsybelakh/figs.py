# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Рівень у децибелах» (ph-waves/riven-u-detsybelakh)."""

import os
import sys
import math

# Підключаємо спільні інструменти з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_decibel_power_amplitude():
    """Фігура 1: Порівняння лінійної та логарифмічної шкал для потужності та амплітуди."""
    w, h = 980, 520
    frags = []

    # Заголовок та підзаголовок
    frags.append(text(w / 2, 30, "Співвідношення лінійних множників та децибелів", size=18, bold=True))
    frags.append(text(w / 2, 52, "Квадратичний зв'язок потужності P ∝ A² перетворюється на подвоєння множника в децибелах", size=13, color=MUTED))

    # Ліва колонка: Енергетичні величини (Потужність P, Інтенсивність I, Енергія W)
    card_w, card_h = 445, 425
    x_left = 30
    y_top = 72

    frags.append(rect(x_left, y_top, card_w, card_h, fill="#fdfefe", stroke="#b0bec5", sw=1.5, rx=8))
    frags.append(rect(x_left, y_top, card_w, 40, fill="#e3f2fd", stroke="#90caf9", sw=1.5, rx=8))
    frags.append(text(x_left + card_w / 2, y_top + 25, "Енергетичні величини (Потужність, I, P, W)", size=14, bold=True, color="#1565c0"))

    frags.append(rect(x_left + 15, y_top + 50, card_w - 30, 34, fill="#e1f5fe", stroke="#81d4fa", sw=1.0, rx=4))
    frags.append(text(x_left + card_w / 2, y_top + 72, "L_p = 10 · log₁₀( P / P₀ )  [дБ]", size=13, bold=True, color="#0277bd"))

    # Рядки таблиці для потужності
    p_rows = [
        ("Відношення P/P₀", "Децибели L [дБ]", "Фізичний зміст"),
        ("1× (P = P₀)", "0 дБ", "Опорний рівень"),
        ("2×", "+3.01 дБ ≈ +3 дБ", "Подвоєння потужності"),
        ("4× = 2²", "+6.02 дБ ≈ +6 дБ", "Чотирикратна потужність"),
        ("10×", "+10.0 дБ", "Зростання на порядок (1 Бел)"),
        ("100× = 10²", "+20.0 дБ", "Зростання у 100 разів"),
        ("1 000× = 10³", "+30.0 дБ", "Зростання в 1000 разів"),
        ("1 000 000× = 10⁶", "+60.0 дБ", "Зростання в 10⁶ разів"),
        ("0.5× (1/2)", "−3.01 дБ ≈ −3 дБ", "Спад потужності вдвічі (−3 дБ)"),
        ("0.1× (1/10)", "−10.0 дБ", "Зменшення в 10 разів"),
    ]

    ty = y_top + 110
    for i, (col1, col2, col3) in enumerate(p_rows):
        row_bg = "#f5f5f5" if i == 0 else ("#f0f7ff" if i % 2 == 1 else "#ffffff")
        frags.append(rect(x_left + 12, ty - 13, card_w - 24, 25, fill=row_bg, stroke="#e0e0e0", sw=0.8, rx=3))
        bld = True if i == 0 else False
        col_c = INK if i > 0 else "#37474f"
        frags.append(text(x_left + 20, ty + 3, col1, size=11, bold=bld, color=col_c, anchor="start"))
        frags.append(text(x_left + 160, ty + 3, col2, size=11, bold=(bld or "дБ" in col2), color=POS if ("+" in col2) else (NEG if ("−" in col2) else col_c), anchor="start"))
        frags.append(text(x_left + 270, ty + 3, col3, size=10, italic=(i > 0), color=MUTED if i > 0 else col_c, anchor="start"))
        ty += 28

    # Права колонка: Амплітудні/польові величини (Напруга V, Струм I, Тиск p)
    x_right = 505
    frags.append(rect(x_right, y_top, card_w, card_h, fill="#fdfefe", stroke="#b0bec5", sw=1.5, rx=8))
    frags.append(rect(x_right, y_top, card_w, 40, fill="#fbe9e7", stroke="#ffab91", sw=1.5, rx=8))
    frags.append(text(x_right + card_w / 2, y_top + 25, "Амплітудні величини (Напруга V, Тиск p, Струм I)", size=14, bold=True, color="#d84315"))

    frags.append(rect(x_right + 15, y_top + 50, card_w - 30, 34, fill="#fff3e0", stroke="#ffcc80", sw=1.0, rx=4))
    frags.append(text(x_right + card_w / 2, y_top + 72, "L_v = 20 · log₁₀( V / V₀ )  [дБ]  (при Z₁ = Z₂)", size=13, bold=True, color="#e65100"))

    # Рядки таблиці для амплітуди
    v_rows = [
        ("Відношення V/V₀", "Децибели L [дБ]", "Зв'язок із потужністю P ∝ V²"),
        ("1× (V = V₀)", "0 дБ", "P = 1× P₀ (0 дБ)"),
        ("√2 ≈ 1.414×", "+3.01 дБ ≈ +3 дБ", "P = (√2)² = 2× P₀ (+3 дБ)"),
        ("2×", "+6.02 дБ ≈ +6 дБ", "P = 2² = 4× P₀ (+6 дБ)"),
        ("3.162× (√10)", "+10.0 дБ", "P = 10× P₀ (+10 дБ)"),
        ("10×", "+20.0 дБ", "P = 10² = 100× P₀ (+20 дБ)"),
        ("100× = 10²", "+40.0 дБ", "P = 10⁴ = 10 000× P₀ (+40 дБ)"),
        ("1 000× = 10³", "+60.0 дБ", "P = 10⁶ = 1 000 000× P₀ (+60 дБ)"),
        ("0.707× (1/√2)", "−3.01 дБ ≈ −3 дБ", "P = 0.5× P₀ (спад потужності вдвічі)"),
        ("0.5× (1/2)", "−6.02 дБ ≈ −6 дБ", "P = 0.25× P₀ (спад у 4 рази)"),
    ]

    ty = y_top + 110
    for i, (col1, col2, col3) in enumerate(v_rows):
        row_bg = "#f5f5f5" if i == 0 else ("#fff8f6" if i % 2 == 1 else "#ffffff")
        frags.append(rect(x_right + 12, ty - 13, card_w - 24, 25, fill=row_bg, stroke="#e0e0e0", sw=0.8, rx=3))
        bld = True if i == 0 else False
        col_c = INK if i > 0 else "#37474f"
        frags.append(text(x_right + 20, ty + 3, col1, size=11, bold=bld, color=col_c, anchor="start"))
        frags.append(text(x_right + 160, ty + 3, col2, size=11, bold=(bld or "дБ" in col2), color=POS if ("+" in col2) else (NEG if ("−" in col2) else col_c), anchor="start"))
        frags.append(text(x_right + 270, ty + 3, col3, size=10, italic=(i > 0), color=MUTED if i > 0 else col_c, anchor="start"))
        ty += 28

    return render(os.path.join(IMG_DIR, "decibel-power-amplitude.svg"), w, h, *frags)


def fig_reference_levels_scale():
    """Фігура 2: Опорні рівні напруги й потужності в аудіо та радіотехніці (dBu, dBV, dBm, dBFS)."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 30, "Стандартні опорні рівні в аудіо, радіозв'язку та цифровій обробці", size=17, bold=True))
    frags.append(text(w / 2, 50, "Опорні напруги 0 dBu (0.775 В) та 0 dBV (1.0 В) узгоджені зі студійними й споживчими стандартами", size=12, color=MUTED))

    y_axis_top = 90
    y_axis_bottom = 450
    axis_len = y_axis_bottom - y_axis_top

    db_max = 24.0
    db_min = -30.0

    def db_to_y(db):
        ratio = (db_max - db) / (db_max - db_min)
        return y_axis_top + ratio * axis_len

    ref_dbs = [20, 14, 8, 4, 0, -6, -10, -18, -24]
    for rdb in ref_dbs:
        ry = db_to_y(rdb)
        frags.append(line(70, ry, 870, ry, color="#eceff1", sw=1.0, dash="4,4"))

    # Центральні рівні інтересу з кольоровим підсвічуванням
    # 1) +4 dBu
    y_pro = db_to_y(4.0)
    frags.append(rect(70, y_pro - 14, 800, 28, fill="#e8f5e9", stroke="#81c784", sw=1.2, rx=4))
    frags.append(text(120, y_pro + 4, "+4 dBu — Професійний лінійний аудіорівень (V_rms = 1.228 В)", size=12, bold=True, color="#2e7d32", anchor="start"))

    # 2) 0 dBu / 0 dBm (600 Ом)
    y_0u = db_to_y(0.0)
    frags.append(rect(70, y_0u - 13, 800, 26, fill="#e1f5fe", stroke="#4fc3f7", sw=1.2, rx=4))
    frags.append(text(120, y_0u + 4, "0 dBu = 0 dBm (600 Ом) — Опорна точка телефонії (V_rms = 0.7746 В ≈ 0.775 В)", size=12, bold=True, color="#0277bd", anchor="start"))

    # 3) -10 dBV -> -7.78 dBu
    y_cons = db_to_y(-7.78)
    frags.append(rect(70, y_cons - 13, 800, 26, fill="#fff3e0", stroke="#ffb74d", sw=1.2, rx=4))
    frags.append(text(120, y_cons + 4, "−10 dBV — Побутовий лінійний рівень RCA / Hi-Fi (V_rms = 0.3162 В = −7.78 dBu)", size=12, bold=True, color="#e65100", anchor="start"))

    # 4) -18 dBFS
    y_dfs = db_to_y(4.0 - 18.0)
    frags.append(rect(70, y_dfs - 12, 800, 24, fill="#f3e5f5", stroke="#ba68c8", sw=1.0, rx=4))
    frags.append(text(120, y_dfs + 4, "−18 dBFS (EBU R128) / −20 dBFS (SMPTE) — Цифровий робочий запас (Headroom)", size=11, bold=True, color="#6a1b9a", anchor="start"))

    # Колонка 1: Шкала dBu (x = 80)
    frags.append(line(80, y_axis_top - 10, 80, y_axis_bottom + 10, color="#37474f", sw=2.0))
    frags.append(text(80, y_axis_top - 20, "Шкала dBu", size=13, bold=True, color="#1565c0"))
    for dbu_val in [20, 14, 8, 4, 0, -4, -8, -14, -20, -28]:
        y_pos = db_to_y(dbu_val)
        frags.append(line(74, y_pos, 86, y_pos, color="#37474f", sw=1.5))
        frags.append(text(68, y_pos + 4, ("+" if dbu_val > 0 else "") + str(dbu_val), size=11, bold=(dbu_val in [4, 0]), anchor="end"))

    # Колонка 2: Шкала dBV (x = 850)
    frags.append(line(850, y_axis_top - 10, 850, y_axis_bottom + 10, color="#37474f", sw=2.0))
    frags.append(text(850, y_axis_top - 20, "Шкала dBV", size=13, bold=True, color="#d84315"))
    for dbv_val in [18, 12, 6, 2.22, 0, -6, -10, -16, -22, -30]:
        dbu_equiv = dbv_val + 2.218
        if db_min <= dbu_equiv <= db_max:
            y_pos = db_to_y(dbu_equiv)
            frags.append(line(844, y_pos, 856, y_pos, color="#37474f", sw=1.5))
            lbl = ("+%.1f" if dbv_val not in [0, 6, 12, 18, -6, -10, -16, -22, -30] else ("+%d" if dbv_val > 0 else "%d")) % dbv_val
            frags.append(text(862, y_pos + 4, lbl, size=11, bold=(abs(dbv_val) < 0.1 or abs(dbv_val + 10) < 0.1), anchor="start"))

    frags.append(rect(80, 465, 780, 42, fill="#fafafa", stroke="#cfd8dc", sw=1.2, rx=6))
    frags.append(text(w / 2, 483, "Формула перерахунку між dBu та dBV:  L_dBu = L_dBV + 20 · log₁₀(1.0 / 0.7746) = L_dBV + 2.218 дБ", size=12, bold=True, color="#263238"))
    frags.append(text(w / 2, 498, "Різниця рівнів: +4 dBu відповідає 1.228 В, а −10 dBV відповідає 0.316 В. Зсув між ними складає 11.79 дБ.", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "reference-levels-scale.svg"), w, h, *frags)


def fig_sound_pressure_level_scale():
    """Фігура 3: Шкала рівнів звукового тиску (SPL), акустичної інтенсивності та прикладів у природі."""
    w, h = 960, 560
    frags = []

    frags.append(text(w / 2, 26, "Шкала рівнів звукового тиску (SPL) та фізичні еквіваленти", size=17, bold=True))
    frags.append(text(w / 2, 46, "Діапазон чутності людини охоплює 7 порядків за тиском (10⁷) і 14 порядків за потужністю (10¹⁴)", size=12, color=MUTED))

    y_header = 70
    y_top = 108
    y_bottom = 490
    h_axis = y_bottom - y_top

    levels = [
        (140, "140 дБ", "200 Па", "100 Вт/м²", "Реактивний літак на старті (30 м), піротехнічний вибух", "#b71c1c", True, "МИТТЄВА АКУСТИЧНА ТРАВМА"),
        (130, "130 дБ", "63.2 Па", "10 Вт/м²", "Больовий поріг слухової системи, пневматична клепка", "#c62828", True, "ПОРІГ БОЛЮ"),
        (120, "120 дБ", "20 Па", "1 Вт/м²", "Рок-концерт біля сцени, сирена повітряної тривоги (1 м)", "#d32f2f", False, "Небезпечно понад 1 хв"),
        (100, "100 дБ", "2 Па", "0.01 Вт/м²", "Відбійний молоток (1 м), вагон метро при гальмуванні", "#e65100", False, "Гранична норма 15 хв/добу"),
        (85, "85 дБ", "0.356 Па", "3.16 мВт/м²", "Важкий вантажний трафік, виробничий цех верстатів", "#f57c00", True, "САНІТАРНА МЕЖА (8 год)"),
        (70, "70 дБ", "0.063 Па", "0.1 мВт/м²", "Шумне офісне приміщення, гучна розмова людей", "#388e3c", False, "Комфортний максимум"),
        (60, "60 дБ", "0.02 Па", "1 мкВт/м²", "Спокійна розмова двох людей на відстані 1 м", "#2e7d32", False, "Норма мовлення"),
        (40, "40 дБ", "2 мПа", "10 нВт/м²", "Тиха кімната, читальна зала бібліотеки, нічний спокій", "#1976d2", False, "Комфортний фоновий шум"),
        (20, "20 дБ", "0.2 мПа", "0.1 нВт/м²", "Шелест листя на вітрі, людський шепіт на дистанції 2 м", "#0288d1", False, "Дуже тихо"),
        (0, "0 дБ", "20 мкПа", "1 пВт/м²", "Опорний поріг чутності людини на частоті 1 кГц (P₀, I₀)", "#455a64", True, "ПОРІГ ЧУТНОСТІ (1 кГц)"),
    ]

    def spl_to_y(spl):
        return y_bottom - (spl / 140.0) * h_axis

    x_spl = 75
    x_pa = 160
    x_w = 260
    x_desc = 380
    x_warn = 770

    # Шапка таблиці
    frags.append(rect(30, y_header - 2, 900, 28, fill="#eceff1", stroke="#b0bec5", sw=1.0, rx=4))
    frags.append(text(x_spl, y_header + 16, "Рівень SPL", size=11, bold=True, color="#37474f"))
    frags.append(text(x_pa, y_header + 16, "Тиск p_rms", size=11, bold=True, color="#37474f"))
    frags.append(text(x_w, y_header + 16, "Інтенсивність I", size=11, bold=True, color="#37474f"))
    frags.append(text(x_desc, y_header + 16, "Джерело звуку / Акустична подія", size=11, bold=True, color="#37474f", anchor="start"))
    frags.append(text(x_warn, y_header + 16, "Фізіологічний вплив", size=11, bold=True, color="#37474f", anchor="start"))

    for spl_val, spl_str, pa_str, w_str, desc_str, color_hex, is_key, warn_str in levels:
        y_pos = spl_to_y(spl_val)

        bg_col = "#ffffff"
        if spl_val >= 130:
            bg_col = "#ffebee"
        elif spl_val >= 85:
            bg_col = "#fff8e1"
        elif spl_val == 0:
            bg_col = "#f1f8e9"

        frags.append(rect(30, y_pos - 13, 900, 26, fill=bg_col, stroke="#e0e0e0" if not is_key else color_hex, sw=1.2 if is_key else 0.6, rx=4))

        frags.append(text(x_spl, y_pos + 4, spl_str, size=11, bold=True, color=color_hex))
        frags.append(text(x_pa, y_pos + 4, pa_str, size=11, color="#263238"))
        frags.append(text(x_w, y_pos + 4, w_str, size=11, color="#37474f"))
        frags.append(text(x_desc, y_pos + 4, desc_str, size=11, color=INK, anchor="start"))
        frags.append(text(x_warn, y_pos + 4, warn_str, size=10, bold=is_key, color=color_hex if is_key else MUTED, anchor="start"))

    frags.append(rect(30, 508, 900, 36, fill="#f5f5f5", stroke="#cfd8dc", sw=1.0, rx=4))
    frags.append(text(w / 2, 530, "Опорний звуковий тиск у повітрі: p₀ = 20 мкПа = 2·10⁻⁵ Па.  Опорна інтенсивність: I₀ = 10⁻¹² Вт/м² (1 пВт/м²)", size=12, bold=True, color="#263238"))

    return render(os.path.join(IMG_DIR, "sound-pressure-level-scale.svg"), w, h, *frags)


def fig_frequency_weighting_curves():
    """Фігура 4: Амплітудно-частотні характеристики вагових фільтрів A, C та Z (IEC 61672-1)."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 28, "Стандартизовані вагові криві сприйняття звуку (IEC 61672-1)", size=17, bold=True))
    frags.append(text(w / 2, 48, "Крива A (dBA) повторює чутливість вуха при 40 фонах, крива C (dBC) — при 100 фонах, Z — лінійна", size=12, color=MUTED))

    gx, gy, gw, gh = 80, 75, 780, 380

    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#90a4ae", sw=1.5, rx=4))

    f_min = 10.0
    f_max = 20000.0

    def f_to_x(f):
        return gx + (math.log10(f / f_min) / math.log10(f_max / f_min)) * gw

    db_min = -50.0
    db_max = 10.0

    def db_to_y(db):
        return gy + ((db_max - db) / (db_max - db_min)) * gh

    for db in [-50, -40, -30, -20, -10, 0, 5]:
        y = db_to_y(db)
        frags.append(line(gx, y, gx + gw, y, color="#cfd8dc" if db != 0 else "#455a64", sw=1.5 if db == 0 else 0.8, dash=None if db == 0 else "3,3"))
        frags.append(text(gx - 8, y + 4, ("+%d" if db > 0 else "%d") % db + " дБ", size=10, bold=(db == 0), color="#37474f", anchor="end"))

    freqs = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    freq_labels = {
        10: "10", 20: "20 Гц", 50: "50", 100: "100 Гц", 200: "200", 500: "500",
        1000: "1 кГц", 2000: "2 к", 5000: "5 к", 10000: "10 кГц", 20000: "20 кГц"
    }

    for f in freqs:
        x = f_to_x(f)
        frags.append(line(x, gy, x, gy + gh, color="#cfd8dc" if f != 1000 else "#455a64", sw=1.5 if f == 1000 else 0.8, dash=None if f == 1000 else "3,3"))
        frags.append(text(x, gy + gh + 16, freq_labels[f], size=10, bold=(f in [20, 100, 1000, 10000]), color="#37474f"))

    def calc_a_weighting(f):
        f2 = f * f
        num = (12194.0 ** 2) * (f2 ** 2)
        den = (f2 + 20.6 ** 2) * math.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194.0 ** 2)
        ra = num / den
        return 20.0 * math.log10(ra) + 2.00

    def calc_c_weighting(f):
        f2 = f * f
        num = (12194.0 ** 2) * f2
        den = (f2 + 20.6 ** 2) * (f2 + 12194.0 ** 2)
        rc = num / den
        return 20.0 * math.log10(rc) + 0.06

    frags.append(line(gx, db_to_y(0), gx + gw, db_to_y(0), color="#546e7a", sw=2.5, dash="6,4"))

    c_pts = []
    a_pts = []

    steps = 200
    for i in range(steps + 1):
        log_f = math.log10(f_min) + (i / float(steps)) * (math.log10(f_max) - math.log10(f_min))
        f = 10.0 ** log_f
        x = f_to_x(f)

        db_c = calc_c_weighting(f)
        y_c = db_to_y(max(db_min, min(db_max, db_c)))
        c_pts.append("%.1f,%.1f" % (x, y_c))

        db_a = calc_a_weighting(f)
        y_a = db_to_y(max(db_min, min(db_max, db_a)))
        a_pts.append("%.1f,%.1f" % (x, y_a))

    frags.append('<polyline points="%s" fill="none" stroke="#e65100" stroke-width="2.8"/>' % " ".join(c_pts))
    frags.append('<polyline points="%s" fill="none" stroke="#1565c0" stroke-width="3.2"/>' % " ".join(a_pts))

    frags.append(circle(f_to_x(1000), db_to_y(0.0), 4, fill="#1565c0", stroke="#ffffff", sw=1.5))
    frags.append(text(f_to_x(1000) + 15, db_to_y(0.0) - 10, "1 кГц (0 дБ)", size=11, bold=True, color="#1565c0", anchor="start"))

    frags.append(circle(f_to_x(2500), db_to_y(calc_a_weighting(2500)), 4, fill="#1565c0", stroke="#ffffff", sw=1.5))
    frags.append(text(f_to_x(2500) + 15, db_to_y(calc_a_weighting(2500)) - 10, "Пік +1.3 дБ (2.5 кГц)", size=11, bold=True, color="#1565c0", anchor="start"))

    lx, ly = gx + 20, gy + gh - 90
    frags.append(rect(lx, ly, 380, 80, fill="#ffffff", stroke="#cfd8dc", sw=1.2, rx=6))

    frags.append(line(lx + 15, ly + 20, lx + 45, ly + 20, color="#1565c0", sw=3.2))
    frags.append(text(lx + 55, ly + 24, "Крива A (dBA) — санітарний шум, поріг 40 фон", size=11, bold=True, color="#1565c0", anchor="start"))

    frags.append(line(lx + 15, ly + 42, lx + 45, ly + 42, color="#e65100", sw=2.8))
    frags.append(text(lx + 55, ly + 46, "Крива C (dBC) — пікові шуми, вибухи, гучність 100 фон", size=11, bold=True, color="#e65100", anchor="start"))

    frags.append(line(lx + 15, ly + 64, lx + 45, ly + 64, color="#546e7a", sw=2.5, dash="6,4"))
    frags.append(text(lx + 55, ly + 68, "Крива Z (dBZ) — нульова фільтрація (пласка 10 Гц–20 кГц)", size=11, bold=True, color="#546e7a", anchor="start"))

    frags.append(text(gx + gw / 2, gy + gh + 35, "Частота звуку f [Гц / кГц] (логарифмічна шкала)", size=12, bold=True, color="#263238"))

    return render(os.path.join(IMG_DIR, "frequency-weighting-curves.svg"), w, h, *frags)


def main():
    print("Генерація SVG-фігур для теми «Рівень у децибелах»...")
    fig_decibel_power_amplitude()
    fig_reference_levels_scale()
    fig_sound_pressure_level_scale()
    fig_frequency_weighting_curves()
    print("Усі 4 фігури успішно згенеровано у теці img/.")


if __name__ == "__main__":
    main()
