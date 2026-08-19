# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Квантовий тунельний витік: SiO2 проти High-k ─────────────────────────
def fig_tunneling_leakage():
    W, H = 840, 420
    frags = []

    frags.append(text(W / 2, 28, "Квантове тунелювання: ультратонкий SiO2 проти High-k діелектрика",
                      size=16, color=INK, bold=True))

    panels = [
        (35, 55, 365, 345, "Традиційний оксид SiO2 (ультратонкий)", [
            "Фізична товщина t_phys = 1.2 нм (~4-5 атомних шарів)",
            "Діелектрична проникність k = 3.9",
            "Високий квантовий витік (> 100 А/см²)",
            "Неприйнятні статичні втрати потужності"
        ], "#fdecea", POS),
        (440, 55, 365, 345, "High-k діелектрик HfO2 + перехідний шар", [
            "Фізична товщина t_phys = 3.5 нм (3.0 нм HfO2 + 0.5 нм IL)",
            "Діелектрична проникність k ≈ 20–25",
            "Еквівалентна товщина EOT ≈ 1.0 нм",
            "Витік тунелювання знижено у 100–1000 разів"
        ], "#eafaf0", FIELD)
    ]

    for (px, py, pw, ph, title_text, bullets, bg_col, border_col) in panels:
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(px + pw / 2, py + 24, title_text, size=13, color=border_col, bold=True))

        if "SiO2" in title_text:
            bx, by, bw, bh = px + 25, py + 48, pw - 50, 160
            frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

            frags.append(rect(bx, by, 75, bh, fill="#e5e7eb", stroke=LINE, sw=1.0))
            frags.append(text(bx + 37, by + bh / 2, "Затвор\n(Poly-Si)", size=11, color=INK, bold=True))

            tox_w = 40
            frags.append(rect(bx + 75, by + 20, tox_w, bh - 40, fill="#fadbd8", stroke=POS, sw=1.5))
            frags.append(text(bx + 75 + tox_w / 2, by + 12, "SiO2", size=11, color=POS, bold=True))
            frags.append(text(bx + 75 + tox_w / 2, by + bh - 8, "1.2 нм", size=10, color=POS, bold=True))

            frags.append(rect(bx + 75 + tox_w, by, bw - (75 + tox_w), bh, fill="#e8f8f5", stroke=LINE, sw=1.0))
            frags.append(text(bx + 75 + tox_w + (bw - 75 - tox_w) / 2, by + bh / 2, "Кремнієвий\nканал (Si)", size=11, color=INK, bold=True))

            frags.append(arrow(bx + 45, by + 65, bx + 165, by + 65, color=POS, sw=2.5))
            frags.append(arrow(bx + 45, by + 95, bx + 165, by + 95, color=POS, sw=2.5))
            frags.append(text(bx + bw / 2 + 50, by + 80, "Пряме\nтунелювання!", size=10.5, color=POS, bold=True))

        else:
            bx, by, bw, bh = px + 25, py + 48, pw - 50, 160
            frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

            frags.append(rect(bx, by, 70, bh, fill="#d5dbdb", stroke=LINE, sw=1.0))
            frags.append(text(bx + 35, by + bh / 2, "Металевий\nзатвор", size=11, color=INK, bold=True))

            thk_w = 95
            frags.append(rect(bx + 70, by + 20, 20, bh - 40, fill="#fcf3cf", stroke="#b7950b", sw=1.2))
            frags.append(text(bx + 80, by + 12, "IL", size=9.5, color="#7d6608", bold=True))

            frags.append(rect(bx + 90, by + 20, thk_w - 20, bh - 40, fill="#d4efdf", stroke=FIELD, sw=1.5))
            frags.append(text(bx + 90 + (thk_w - 20) / 2, by + 12, "HfO2 (k≈22)", size=10.5, color=FIELD, bold=True))
            frags.append(text(bx + 70 + thk_w / 2, by + bh - 8, "t_phys = 3.5 нм", size=10, color=FIELD, bold=True))

            frags.append(rect(bx + 70 + thk_w, by, bw - (70 + thk_w), bh, fill="#e8f8f5", stroke=LINE, sw=1.0))
            frags.append(text(bx + 70 + thk_w + (bw - 70 - thk_w) / 2, by + bh / 2, "Кремнієвий\nканал (Si)", size=11, color=INK, bold=True))

            frags.append(arrow(bx + 40, by + 65, bx + 95, by + 65, color=NEG, sw=2.0))
            frags.append(line(bx + 95, by + 65, bx + 70, by + 90, color=NEG, sw=1.8, dash="3,3"))
            frags.append(text(bx + 115, by + 80, "Тунелювання\nпридушене", size=10.5, color=FIELD, bold=True))

        ty = py + 230
        for b in bullets:
            frags.append(text(px + 16, ty, "• " + b, size=11, color=INK, anchor="start"))
            ty += 24

    render(os.path.join(IMG, "tunneling-leakage-crisis.svg"), W, H, *frags)


# ── 2. Полікремнієве збіднення проти металевого затвора ───────────────────────
def fig_poly_depletion():
    W, H = 840, 420
    frags = []

    frags.append(text(W / 2, 28, "Ефект збіднення полікремнію (Poly-Depletion) та металевий затвор",
                      size=16, color=INK, bold=True))

    panels = [
        (35, 55, 365, 345, "Полікремнієвий затвор (Poly-Si)", [
            "Обмежена концентрація домішок (~10²⁰ см⁻³)",
            "Шар збіднення W_dep ≈ 0.3–0.5 нм біля межі",
            "Послідовна паразитна ємність 1/C_poly",
            "CET = EOT + 0.4 нм → втрата 20–30% струму каналу"
        ], "#fef9e7", "#b7950b"),
        (440, 55, 365, 345, "Металевий затвор (Metal Gate)", [
            "Величезна концентрація електронів (~10²³ см⁻³)",
            "Нульовий шар збіднення (W_dep = 0 нм)",
            "Немає паразитної послідовної ємності",
            "CET = EOT → повний ємнісний контроль каналу"
        ], "#eafaf0", FIELD)
    ]

    for (px, py, pw, ph, title_text, bullets, bg_col, border_col) in panels:
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(px + pw / 2, py + 24, title_text, size=13, color=border_col, bold=True))

        bx, by, bw, bh = px + 25, py + 50, pw - 50, 155
        frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

        if "Полікремнієвий" in title_text:
            frags.append(rect(bx, by, bw, 55, fill="#d6dbdf", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw / 2, by + 18, "Poly-Si (N+ легований кремній)", size=11, color=INK, bold=True))

            frags.append(rect(bx, by + 37, bw, 18, fill="#f9e79f", stroke="#d4ac0d", sw=1.2))
            frags.append(text(bx + bw / 2, by + 50, "Шар збіднення W_dep (паразитна ємність C_poly)", size=9.5, color="#7d6608", bold=True))

            frags.append(rect(bx, by + 55, bw, 35, fill="#d4efdf", stroke=FIELD, sw=1.2))
            frags.append(text(bx + bw / 2, by + 76, "High-k діелектрик (HfO2, C_diel)", size=11, color=FIELD, bold=True))

            frags.append(rect(bx, by + 90, bw, 65, fill="#ebf5fb", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw / 2, by + 115, "Інверсійний шар / Кремнієвий канал", size=11, color=INK, bold=True))
            frags.append(text(bx + bw / 2, by + 135, "1/C_total = 1/C_diel + 1/C_poly", size=10.5, color=POS, bold=True))

        else:
            frags.append(rect(bx, by, bw, 55, fill="#aed6f1", stroke="#2980b9", sw=1.2))
            frags.append(text(bx + bw / 2, by + 28, "Метал (TiN / TaN / TiAl)", size=11.5, color="#1b4f72", bold=True))
            frags.append(text(bx + bw / 2, by + 46, "Вільні електрони ~10²³ см⁻³ (W_dep = 0)", size=9.5, color="#1b4f72"))

            frags.append(rect(bx, by + 55, bw, 35, fill="#d4efdf", stroke=FIELD, sw=1.2))
            frags.append(text(bx + bw / 2, by + 76, "High-k діелектрик (HfO2, C_diel)", size=11, color=FIELD, bold=True))

            frags.append(rect(bx, by + 90, bw, 65, fill="#ebf5fb", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw / 2, by + 115, "Інверсійний шар / Кремнієвий канал", size=11, color=INK, bold=True))
            frags.append(text(bx + bw / 2, by + 135, "C_total = C_diel (максимальна ємність)", size=10.5, color=FIELD, bold=True))

        ty = py + 230
        for b in bullets:
            frags.append(text(px + 16, ty, "• " + b, size=11, color=INK, anchor="start"))
            ty += 24

    render(os.path.join(IMG, "poly-depletion-vs-metal-gate.svg"), W, H, *frags)


# ── 3. Зонні зміщення діелектриків: SiO2 та HfO2 на кремнії ─────────────────
def fig_band_offsets():
    W, H = 840, 420
    frags = []

    frags.append(text(W / 2, 28, "Енергетичні зони та розриви зон (Band Offsets) на межі з кремнієм",
                      size=16, color=INK, bold=True))

    bx, by, bw, bh = 50, 60, 740, 260
    frags.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))

    frags.append(arrow(bx + 30, by + bh - 20, bx + 30, by + 20, color=LINE, sw=1.8))
    frags.append(text(bx + 30, by + 12, "Енергія E (еВ)", size=11, color=INK, bold=True))

    col_w = 200
    c1_x = bx + 60   # Silicon
    c2_x = bx + 285  # SiO2
    c3_x = bx + 510  # HfO2

    # 1. Кремній (Eg = 1.12 еВ)
    frags.append(rect(c1_x, by + 40, col_w, bh - 60, fill="#ebedef", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(c1_x + col_w / 2, by + 28, "Кремній (Si, підкладка)", size=12, color=INK, bold=True))

    ec_si_y = by + 110
    ev_si_y = by + 190
    frags.append(line(c1_x + 10, ec_si_y, c1_x + col_w - 10, ec_si_y, color=POS, sw=2.0))
    frags.append(text(c1_x + col_w / 2, ec_si_y - 8, "Ec (Si) = 4.05 еВ", size=10.5, color=POS, bold=True))

    frags.append(line(c1_x + 10, ev_si_y, c1_x + col_w - 10, ev_si_y, color=NEG, sw=2.0))
    frags.append(text(c1_x + col_w / 2, ev_si_y + 16, "Ev (Si) = 5.17 еВ", size=10.5, color=NEG, bold=True))
    frags.append(text(c1_x + col_w / 2, (ec_si_y + ev_si_y) / 2 + 4, "Eg = 1.12 еВ", size=11, color=INK, bold=True))

    # 2. SiO2 (Eg = 8.9 еВ, ΔEc = 3.15 еВ, ΔEv = 4.63 еВ)
    frags.append(rect(c2_x, by + 40, col_w, bh - 60, fill="#fdedec", stroke=POS, sw=1.2, rx=4))
    frags.append(text(c2_x + col_w / 2, by + 28, "SiO2 (k = 3.9, Eg = 8.9 еВ)", size=12, color=POS, bold=True))

    ec_sio2_y = by + 50
    ev_sio2_y = by + 245
    frags.append(line(c2_x + 10, ec_sio2_y, c2_x + col_w - 10, ec_sio2_y, color=POS, sw=2.0))
    frags.append(text(c2_x + col_w / 2, ec_sio2_y + 15, "Ec (SiO2)", size=10.5, color=POS, bold=True))

    frags.append(line(c2_x + 10, ev_sio2_y, c2_x + col_w - 10, ev_sio2_y, color=NEG, sw=2.0))
    frags.append(text(c2_x + col_w / 2, ev_sio2_y - 8, "Ev (SiO2)", size=10.5, color=NEG, bold=True))

    frags.append(line(c1_x + col_w - 10, ec_si_y, c2_x + 10, ec_si_y, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(arrow(c2_x + 25, ec_si_y, c2_x + 25, ec_sio2_y + 2, color=POS, sw=1.5))
    frags.append(text(c2_x + 75, (ec_si_y + ec_sio2_y) / 2 + 4, "ΔEc = 3.15 еВ", size=10, color=POS, bold=True))

    frags.append(line(c1_x + col_w - 10, ev_si_y, c2_x + 10, ev_si_y, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(arrow(c2_x + 25, ev_si_y, c2_x + 25, ev_sio2_y - 2, color=NEG, sw=1.5))
    frags.append(text(c2_x + 75, (ev_si_y + ev_sio2_y) / 2 + 4, "ΔEv = 4.63 еВ", size=10, color=NEG, bold=True))

    # 3. HfO2 (Eg = 5.7 еВ, ΔEc = 1.5 еВ, ΔEv = 3.1 еВ)
    frags.append(rect(c3_x, by + 40, col_w, bh - 60, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(c3_x + col_w / 2, by + 28, "HfO2 (k ≈ 22, Eg = 5.7 еВ)", size=12, color=FIELD, bold=True))

    ec_hfo2_y = by + 80
    ev_hfo2_y = by + 225
    frags.append(line(c3_x + 10, ec_hfo2_y, c3_x + col_w - 10, ec_hfo2_y, color=POS, sw=2.0))
    frags.append(text(c3_x + col_w / 2, ec_hfo2_y + 15, "Ec (HfO2)", size=10.5, color=POS, bold=True))

    frags.append(line(c3_x + 10, ev_hfo2_y, c3_x + col_w - 10, ev_hfo2_y, color=NEG, sw=2.0))
    frags.append(text(c3_x + col_w / 2, ev_hfo2_y - 8, "Ev (HfO2)", size=10.5, color=NEG, bold=True))

    frags.append(line(c2_x + col_w - 10, ec_si_y, c3_x + 10, ec_si_y, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(arrow(c3_x + 25, ec_si_y, c3_x + 25, ec_hfo2_y + 2, color=POS, sw=1.5))
    frags.append(text(c3_x + 75, (ec_si_y + ec_hfo2_y) / 2 + 4, "ΔEc ≈ 1.5 еВ", size=10, color=POS, bold=True))

    frags.append(line(c2_x + col_w - 10, ev_si_y, c3_x + 10, ev_si_y, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(arrow(c3_x + 25, ev_si_y, c3_x + 25, ev_hfo2_y - 2, color=NEG, sw=1.5))
    frags.append(text(c3_x + 75, (ev_si_y + ev_hfo2_y) / 2 + 4, "ΔEv ≈ 3.1 еВ", size=10, color=NEG, bold=True))

    frags.append(rect(50, 335, 740, 65, fill="#f4f6f7", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(W / 2, 355, "Критерій вибору High-k: розриви зон ΔEc > 1.0 еВ та ΔEv > 1.0 еВ для надійного блокування струмів", size=11.5, color=INK, bold=True))
    frags.append(text(W / 2, 378, "HfO2 має достатню висоту бар'єрів для обох типів носіїв, що гарантує низький термоемісійний витік", size=11, color=MUTED))

    render(os.path.join(IMG, "band-offsets-highk.svg"), W, H, *frags)


# ── 4. Подвійна робота виходу металевого затвора для КМОН ─────────────────────
def fig_dual_work_function():
    W, H = 840, 420
    frags = []

    frags.append(text(W / 2, 28, "Підбір подвійної роботи виходу (Dual Work Function) для КМОН",
                      size=16, color=INK, bold=True))

    panels = [
        (35, 55, 365, 345, "nMOS металевий затвор", [
            "Цільова робота виходу: Φ_m,n ≈ 4.05–4.2 еВ",
            "Вирівнювання біля дна зони провідності Si (Ec)",
            "Матеріали: TiAl, TaAlC, TiN/Al сплави",
            "Порогова напруга V_th,n ≈ +0.25 В"
        ], "#ebf5fb", "#2980b9"),
        (440, 55, 365, 345, "pMOS металевий затвор", [
            "Цільова робота виходу: Φ_m,p ≈ 5.0–5.2 еВ",
            "Вирівнювання біля верху валентної зони Si (Ev)",
            "Матеріали: TiN, TaN, MoN, Pt, W/Ru покриття",
            "Порогова напруга V_th,p ≈ -0.25 В"
        ], "#fdf2e9", "#d35400")
    ]

    for (px, py, pw, ph, title_text, bullets, bg_col, border_col) in panels:
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(px + pw / 2, py + 24, title_text, size=13, color=border_col, bold=True))

        bx, by, bw, bh = px + 20, py + 48, pw - 40, 160
        frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

        frags.append(line(bx + 15, by + 20, bx + bw - 15, by + 20, color=MUTED, sw=1.5, dash="4,3"))
        frags.append(text(bx + bw / 2, by + 14, "Рівень вакууму (E_vac = 0 еВ)", size=10, color=MUTED, bold=True))

        if "nMOS" in title_text:
            ef_y = by + 65
            frags.append(rect(bx + 25, ef_y - 12, bw - 50, 24, fill="#d4e6f1", stroke="#2980b9", sw=1.5))
            frags.append(text(bx + bw / 2, ef_y + 4, "E_F (nMOS Metal) ≈ 4.1 еВ", size=11, color="#1b4f72", bold=True))

            frags.append(arrow(bx + 35, by + 20, bx + 35, ef_y - 14, color="#2980b9", sw=1.5))
            frags.append(text(bx + 85, (by + 20 + ef_y) / 2 - 4, "Φ_m,n ≈ 4.1 еВ", size=10.5, color="#2980b9", bold=True))

            frags.append(line(bx + 25, by + 75, bx + bw - 25, by + 75, color=POS, sw=2.0))
            frags.append(text(bx + bw / 2, by + 92, "Ec (Si) = 4.05 еВ [Дно зони провідності]", size=10, color=POS, bold=True))

            frags.append(line(bx + 25, by + 135, bx + bw - 25, by + 135, color=NEG, sw=2.0))
            frags.append(text(bx + bw / 2, by + 148, "Ev (Si) = 5.17 еВ", size=9.5, color=NEG))

        else:
            ef_y = by + 125
            frags.append(rect(bx + 25, ef_y - 12, bw - 50, 24, fill="#fad7a0", stroke="#d35400", sw=1.5))
            frags.append(text(bx + bw / 2, ef_y + 4, "E_F (pMOS Metal) ≈ 5.1 еВ", size=11, color="#7e3200", bold=True))

            frags.append(arrow(bx + 35, by + 20, bx + 35, ef_y - 14, color="#d35400", sw=1.5))
            frags.append(text(bx + 85, (by + 20 + ef_y) / 2 - 10, "Φ_m,p ≈ 5.1 еВ", size=10.5, color="#d35400", bold=True))

            frags.append(line(bx + 25, by + 65, bx + bw - 25, by + 65, color=POS, sw=2.0))
            frags.append(text(bx + bw / 2, by + 55, "Ec (Si) = 4.05 еВ", size=9.5, color=POS))

            frags.append(line(bx + 25, by + 135, bx + bw - 25, by + 135, color=NEG, sw=2.0))
            frags.append(text(bx + bw / 2, by + 148, "Ev (Si) = 5.17 еВ [Верх валентної зони]", size=10, color=NEG, bold=True))

        ty = py + 230
        for b in bullets:
            frags.append(text(px + 16, ty, "• " + b, size=11, color=INK, anchor="start"))
            ty += 24

    render(os.path.join(IMG, "dual-work-function-tuning.svg"), W, H, *frags)


# ── 5. Інтеграція: Gate-First проти Gate-Last (RMG) ───────────────────────────
def fig_integration_flows():
    W, H = 840, 430
    frags = []

    frags.append(text(W / 2, 28, "Технологічні схеми інтеграції: Gate-First проти Gate-Last (RMG)",
                      size=16, color=INK, bold=True))

    panels = [
        (35, 55, 365, 355, "Gate-First (MIPS / IBM Альянс)", [
            "1. Нанесення High-k та металів затвора",
            "2. Формування маски та травлення затворів",
            "3. Імплантація Source / Drain",
            "4. Високотемпературний відпал (RTA > 1000 °C)",
            "⚠ Термічний зсув роботи виходу та дефекти"
        ], "#fdedec", POS),
        (440, 55, 365, 355, "Gate-Last / RMG (Intel / Сучасний стандарт)", [
            "1. Формування фіктивного затвора (Dummy Poly)",
            "2. Імплантація S/D та відпал (RTA > 1000 °C)",
            "3. Нанесення діелектрика ILD та полірування CMP",
            "4. Хімічне витравлювання фіктивного затвора",
            "5. Низькотемпературне нанесення High-k та металів (<450°C)"
        ], "#eafaf1", FIELD)
    ]

    for (px, py, pw, ph, title_text, bullets, bg_col, border_col) in panels:
        frags.append(rect(px, py, pw, ph, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(px + pw / 2, py + 24, title_text, size=12.5, color=border_col, bold=True))

        bx, by, bw, bh = px + 20, py + 46, pw - 40, 145
        frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

        if "Gate-First" in title_text:
            frags.append(rect(bx + 15, by + 75, bw - 30, 60, fill="#ebedef", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw / 2, by + 115, "Кремнієва підкладка (Si)", size=11, color=INK))

            frags.append(rect(bx + 25, by + 75, 45, 30, fill="#fadbd8", stroke=POS, sw=1.2))
            frags.append(text(bx + 47, by + 94, "S", size=11, color=POS, bold=True))
            frags.append(rect(bx + bw - 70, by + 75, 45, 30, fill="#fadbd8", stroke=POS, sw=1.2))
            frags.append(text(bx + bw - 48, by + 94, "D", size=11, color=POS, bold=True))

            gx = bx + 95
            frags.append(rect(gx, by + 65, bw - 190, 10, fill="#d4efdf", stroke=FIELD, sw=1.0))
            frags.append(rect(gx, by + 45, bw - 190, 20, fill="#d5dbdb", stroke=LINE, sw=1.0))
            frags.append(rect(gx, by + 15, bw - 190, 30, fill="#aeb6bf", stroke=LINE, sw=1.0))
            frags.append(text(gx + (bw - 190) / 2, by + 34, "Metal+Poly", size=10, color=INK, bold=True))

            frags.append(text(bx + bw / 2, by + 12, "🔥 RTA Відпал > 1000 °C 🔥", size=11, color=POS, bold=True))

        else:
            frags.append(rect(bx + 15, by + 75, bw - 30, 60, fill="#ebedef", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw / 2, by + 115, "Кремнієва підкладка (Si)", size=11, color=INK))

            frags.append(rect(bx + 25, by + 75, 45, 30, fill="#d4efdf", stroke=FIELD, sw=1.2))
            frags.append(text(bx + 47, by + 94, "S", size=11, color=FIELD, bold=True))
            frags.append(rect(bx + bw - 70, by + 75, 45, 30, fill="#d4efdf", stroke=FIELD, sw=1.2))
            frags.append(text(bx + bw - 48, by + 94, "D", size=11, color=FIELD, bold=True))

            frags.append(rect(bx + 15, by + 15, 80, 60, fill="#f2f4f4", stroke=LINE, sw=1.0))
            frags.append(text(bx + 55, by + 45, "ILD Оксид", size=9.5, color=MUTED))
            frags.append(rect(bx + bw - 95, by + 15, 80, 60, fill="#f2f4f4", stroke=LINE, sw=1.0))
            frags.append(text(bx + bw - 55, by + 45, "ILD Оксид", size=9.5, color=MUTED))

            gx = bx + 95
            frags.append(rect(gx, by + 65, bw - 190, 10, fill="#d4efdf", stroke=FIELD, sw=1.0))
            frags.append(rect(gx, by + 35, bw - 190, 30, fill="#aed6f1", stroke="#2980b9", sw=1.0))
            frags.append(rect(gx, by + 15, bw - 190, 20, fill="#d5dbdb", stroke=LINE, sw=1.0))
            frags.append(text(gx + (bw - 190) / 2, by + 48, "RMG Метал", size=10.5, color="#1b4f72", bold=True))

            frags.append(text(bx + bw / 2, by + 10, "✨ Осадження металів < 450 °C ✨", size=10.5, color=FIELD, bold=True))

        ty = py + 208
        for b in bullets:
            col = POS if "⚠" in b else INK
            frags.append(text(px + 14, ty, b, size=10.5, color=col, anchor="start", bold=("⚠" in b)))
            ty += 23

    render(os.path.join(IMG, "gate-first-vs-gate-last-rmg.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_tunneling_leakage()
    fig_poly_depletion()
    fig_band_offsets()
    fig_dual_work_function()
    fig_integration_flows()
    print("All 5 HKMG figures generated successfully.")
