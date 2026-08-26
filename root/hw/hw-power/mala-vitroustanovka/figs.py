# -*- coding: utf-8 -*-
"""Фігури для теми «Мала вітроустановка: ротор, межа Бетца, крива потужності».
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def pline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── 1. Струминна трубка та модель диска Бетца ─────────────────────────────────
def fig_betz_streamtube():
    """Струминна трубка повітряного потоку крізь активний диск ротора (теорія Бетца)."""
    W, H = 940, 470
    f = []

    f.append(text(W / 2, 28, "Струминна трубка та розширення потоку крізь вітроротор", size=15, bold=True))

    # Вісь симетрії
    f.append(line(50, 230, 890, 230, color=MUTED, sw=1.2, dash="6 6"))
    f.append(text(870, 222, "вісь потоку", size=11, color=MUTED, anchor="end", italic=True))

    # Струминна трубка (межі потоку: звуження швидкості -> розширення площі)
    # Верхня межа
    top_pts = [(70, 150), (220, 160), (470, 110), (720, 75), (870, 65)]
    # Нижня межа
    bot_pts = [(70, 310), (220, 300), (470, 350), (720, 385), (870, 395)]

    # Заливка струминної трубки
    poly_pts = top_pts + list(reversed(bot_pts))
    poly_str = " ".join("%.1f,%.1f" % p for p in poly_pts)
    f.append('<polygon points="%s" fill="#eaf2f8" stroke="none" opacity="0.6"/>' % poly_str)

    # Лінії меж
    f.append(pline(top_pts, color=NEG, sw=2.2))
    f.append(pline(bot_pts, color=NEG, sw=2.2))

    # Струмені повітря всередині (стрілки течії)
    for y_rel in (-50, 0, 50):
        y_in = 230 + y_rel * 0.7
        y_disk = 230 + y_rel * 1.1
        y_out = 230 + y_rel * 1.5
        f.append(arrow(80, y_in, 200, y_in + (y_disk - y_in) * 0.4, color=NEG, sw=1.4))
        f.append(arrow(260, y_disk - (y_disk - y_in) * 0.2, 430, y_disk, color=NEG, sw=1.4))
        f.append(arrow(510, y_disk, 680, y_out - (y_out - y_disk) * 0.3, color=NEG, sw=1.4))
        f.append(arrow(720, y_out - (y_out - y_disk) * 0.2, 850, y_out, color=NEG, sw=1.4))

    # Переріз 1: Набігаючий потік (вхід)
    f.append(line(160, 155, 160, 305, color=LINE, sw=1.8, dash="4 4"))
    f.append(textbox(160, 95, "Набігаючий потік\nШвидкість: v₁\nПлоща: A₁\nТиск: p₀", size=11.5, pad=6)[0])

    # Диск ротора (активна площина)
    f.append(line(470, 90, 470, 370, color=POS, sw=4.5))
    f.append(circle(470, 230, 8, fill=POS, stroke=INK, sw=2))
    f.append(textbox(470, 420, "Площина ротора (диск)\nШвидкість: v_rotor = ½·(v₁ + v₂)\nПлоща обметання: A\nСтрибок тиску: Δp = p⁺ − p⁻", size=11.5, pad=6, fill="#fdecea", stroke=POS)[0])

    # Переріз 2: Слід за ротором (вихід)
    f.append(line(780, 68, 780, 88, color=LINE, sw=1.8, dash="4 4"))
    f.append(line(780, 162, 780, 392, color=LINE, sw=1.8, dash="4 4"))
    f.append(textbox(780, 125, "Збурений слід (wake)\nШвидкість: v₂ = v₁·(1 − 2a)\nПлоща: A₂ > A₁\nТиск: p₀", size=11.5, pad=6)[0])

    # Пояснення оптимуму Бетца внизу зліва
    f.append(textbox(200, 420, "Оптимум уповільнення (a = 1/3):\n• v_rotor = 2/3 · v₁\n• v₂ = 1/3 · v₁\n• C_p,max = 16/27 ≈ 59.3%", size=11.5, pad=7, fill="#e8f8f5", stroke=FIELD)[0])

    render(os.path.join(IMG, "betz-streamtube.svg"), W, H, *f)


# ── 2. Порівняння конструкцій HAWT проти VAWT ────────────────────────────────
def fig_hawt_vs_vawt():
    """Конструктивні типи роторів: HAWT (горизонтальний) та VAWT (Савоніус, Дар'є)."""
    W, H = 960, 490
    f = []

    f.append(text(W / 2, 28, "Основні типи вітророторів: горизонтальні та вертикальні осі", size=15, bold=True))

    # Секція 1: HAWT (Горизонтально-осьовий трилопатевий)
    f.append(rect(30, 60, 280, 410, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(170, 85, "HAWT (Трилопатевий)", size=13.5, bold=True))
    f.append(text(170, 105, "Горизонтальна вісь (Lift-based)", size=11, color=MUTED))

    # Щогла HAWT
    f.append(line(170, 240, 170, 390, color=LINE, sw=4))
    f.append(line(140, 390, 200, 390, color=LINE, sw=3))
    # Гондола
    f.append(rect(145, 225, 50, 25, fill="#d5dbdb", stroke=LINE, sw=1.8, rx=4))
    # Маточина й лопаті
    f.append(circle(145, 237, 7, fill=POS, stroke=INK, sw=1.5))
    # Лопать 1 (вгору)
    f.append(line(145, 237, 145, 140, color=POS, sw=3.5))
    # Лопать 2 (вниз-вліво)
    f.append(line(145, 237, 85, 290, color=POS, sw=3.5))
    # Лопать 3 (вниз-вправо)
    f.append(line(145, 237, 195, 285, color=POS, sw=3.5))
    # Флюгер / хвостове оперення
    f.append(line(195, 237, 235, 237, color=LINE, sw=2))
    f.append(rect(235, 222, 18, 30, fill="#aeb6bf", stroke=LINE, sw=1.5, rx=2))

    # Опис HAWT
    f.append(textbox(170, 435, "Cp ≈ 0.40–0.48 | λ ≈ 6–8\n+ Найвища ефективність\n− Потрібна орієнтація (yaw)", size=10.5, pad=5, fill=FILL)[0])

    # Секція 2: VAWT Савоніуса (Drag-based)
    f.append(rect(340, 60, 280, 410, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(480, 85, "VAWT (Ротор Савоніуса)", size=13.5, bold=True))
    f.append(text(480, 105, "Вертикальна вісь (Drag-based)", size=11, color=MUTED))

    # Вал і опора
    f.append(line(480, 135, 480, 390, color=LINE, sw=3.5))
    f.append(line(450, 390, 510, 390, color=LINE, sw=3))
    # Генератор унизу
    f.append(rect(460, 350, 40, 35, fill="#d5dbdb", stroke=LINE, sw=1.8, rx=4))
    f.append(text(480, 372, "Ген.", size=10, bold=True))

    # Напівциліндричні лопаті Савоніуса (S-подібна форма)
    f.append('<path d="M 480 160 C 430 160, 430 240, 480 240" fill="#fdecea" stroke="%s" stroke-width="3.5"/>' % POS)
    f.append('<path d="M 480 240 C 530 240, 530 320, 480 320" fill="#fdecea" stroke="%s" stroke-width="3.5"/>' % POS)
    f.append(line(430, 200, 530, 280, color=MUTED, sw=1.2, dash="3 3"))

    # Стрілки обертання
    f.append(arrow(430, 145, 470, 135, color=FIELD, sw=2))

    # Опис Савоніуса
    f.append(textbox(480, 435, "Cp ≈ 0.15–0.20 | λ < 1\n+ Самовідцентрований пуск\n− Низький ККД, важкий ротор", size=10.5, pad=5, fill=FILL)[0])

    # Секція 3: VAWT Дар'є (H-ротор / Lift-based)
    f.append(rect(650, 60, 280, 410, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(790, 85, "VAWT (H-ротор Дар'є)", size=13.5, bold=True))
    f.append(text(790, 105, "Вертикальна вісь (Lift-based)", size=11, color=MUTED))

    # Центральний вал
    f.append(line(790, 135, 790, 390, color=LINE, sw=3.5))
    f.append(line(760, 390, 820, 390, color=LINE, sw=3))
    # Генератор унизу
    f.append(rect(770, 350, 40, 35, fill="#d5dbdb", stroke=LINE, sw=1.8, rx=4))
    f.append(text(790, 372, "Ген.", size=10, bold=True))

    # Горизонтальні траверси (спиці)
    f.append(line(710, 180, 870, 180, color=LINE, sw=2.5))
    f.append(line(710, 300, 870, 300, color=LINE, sw=2.5))

    # Вертикальні аеродинамічні лопаті крилового профілю
    f.append(rect(702, 150, 16, 180, fill="#fdecea", stroke=POS, sw=2.5, rx=3))
    f.append(rect(862, 150, 16, 180, fill="#fdecea", stroke=POS, sw=2.5, rx=3))

    # Опис Дар'є
    f.append(textbox(790, 435, "Cp ≈ 0.30–0.38 | λ ≈ 3–5\n+ Генератор на землі, без yaw\n− Нема самозапуску, пульсації", size=10.5, pad=5, fill=FILL)[0])

    render(os.path.join(IMG, "hawt-vs-vawt.svg"), W, H, *f)


# ── 3. Графіки аеродинамічного ККД Cp(lambda) ─────────────────────────────────
def fig_cp_tsr_curves():
    """Залежність коефіцієнта використання енергії вітру Cp від швидкохідності lambda."""
    W, H = 940, 500
    f = []

    ox, oy = 90, 420
    axW, axH = 780, 340

    f.append(text(W / 2, 26, "Коефіцієнт потужності Cp залежно від швидкохідності λ", size=15, bold=True))

    # Осі координат
    f.append(arrow(ox, oy, ox, oy - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 25, oy, color=INK, sw=1.8))
    f.append(text(ox - 15, oy - axH - 10, "Cp (коефіцієнт потужності)", size=12.5, bold=True, anchor="start"))
    f.append(text(ox + axW + 20, oy + 25, "Швидкохідність λ = (ω·R)/v", size=12.5, bold=True, anchor="end"))

    def X(lmb):
        return ox + (lmb / 10.0) * axW

    def Y(cp):
        return oy - (cp / 0.7) * axH

    # Горизонтальна сітка
    for cp_val in (0.1, 0.2, 0.3, 0.4, 0.5, 0.593):
        y_p = Y(cp_val)
        is_betz = (cp_val == 0.593)
        col = POS if is_betz else MUTED
        dash_str = "6 4" if is_betz else "3 3"
        f.append(line(ox, y_p, ox + axW, y_p, color=col, sw=1.4 if is_betz else 0.8, dash=dash_str))
        lbl = "Межа Бетца: 16/27 ≈ 0.593 (59.3%)" if is_betz else "%.1f" % cp_val
        f.append(text(ox - 10, y_p + 4, lbl, size=11, color=col, anchor="end", bold=is_betz))

    # Вертикальна сітка (lambda від 1 до 10)
    for lmb_val in range(1, 11):
        x_p = X(lmb_val)
        f.append(line(x_p, oy, x_p, oy - axH, color=MUTED, sw=0.7, dash="2 3"))
        f.append(text(x_p, oy + 18, str(lmb_val), size=11, color=INK, anchor="middle"))

    # Крива 1: 3-лопатевий сучасний HAWT (пік біля lambda=7, Cp=0.48)
    hawt3_pts = []
    for step in range(0, 101):
        l = step * 0.1
        if l < 2.0:
            cp = 0.05 * (l / 2.0)
        elif l <= 7.0:
            cp = 0.05 + 0.43 * math.sin((l - 2.0) / 5.0 * (math.pi / 2.0))
        elif l <= 10.0:
            cp = 0.48 * math.cos((l - 7.0) / 3.0 * (math.pi / 2.2))
            cp = max(0.0, cp)
        else:
            cp = 0.0
        hawt3_pts.append((X(l), Y(cp)))
    f.append(pline(hawt3_pts, color=POS, sw=3.0))
    f.append(text(X(7.2), Y(0.48) - 12, "3-лопатевий HAWT (пік 0.48)", size=11.5, color=POS, bold=True))

    # Крива 2: 2-лопатевий HAWT (пік біля lambda=8.5, Cp=0.42)
    hawt2_pts = []
    for step in range(0, 101):
        l = step * 0.1
        if l < 3.0:
            cp = 0.03 * (l / 3.0)
        elif l <= 8.5:
            cp = 0.03 + 0.39 * math.sin((l - 3.0) / 5.5 * (math.pi / 2.0))
        elif l <= 10.0:
            cp = 0.42 * math.cos((l - 8.5) / 1.5 * (math.pi / 2.5))
            cp = max(0.0, cp)
        else:
            cp = 0.0
        hawt2_pts.append((X(l), Y(cp)))
    f.append(pline(hawt2_pts, color=NEG, sw=2.2, dash="5 3"))
    f.append(text(X(8.6), Y(0.42) - 10, "2-лопатевий HAWT", size=11, color=NEG, bold=True))

    # Крива 3: H-ротор Дар'є (VAWT lift-based, пік біля lambda=4.0, Cp=0.35)
    darrieus_pts = []
    for step in range(0, 71):
        l = step * 0.1
        if l < 1.5:
            cp = 0.0
        elif l <= 4.0:
            cp = 0.35 * math.sin((l - 1.5) / 2.5 * (math.pi / 2.0))
        elif l <= 7.0:
            cp = 0.35 * math.cos((l - 4.0) / 3.0 * (math.pi / 2.0))
            cp = max(0.0, cp)
        else:
            cp = 0.0
        darrieus_pts.append((X(l), Y(cp)))
    f.append(pline(darrieus_pts, color=FIELD, sw=2.2))
    f.append(text(X(4.1), Y(0.35) - 10, "Дар'є (H-ротор)", size=11, color=FIELD, bold=True))

    # Крива 4: Багатолопатевий вітряк (млиновий/насосний, пік біля lambda=1.5, Cp=0.30)
    multi_pts = []
    for step in range(0, 41):
        l = step * 0.1
        if l <= 1.5:
            cp = 0.15 + 0.15 * math.sin(l / 1.5 * (math.pi / 2.0))
        elif l <= 3.5:
            cp = 0.30 * math.cos((l - 1.5) / 2.0 * (math.pi / 2.0))
            cp = max(0.0, cp)
        else:
            cp = 0.0
        multi_pts.append((X(l), Y(cp)))
    f.append(pline(multi_pts, color="#8e44ad", sw=2.0, dash="4 2"))
    f.append(text(X(1.6), Y(0.30) - 10, "Багатолопатевий (насос)", size=10.5, color="#8e44ad", bold=True))

    # Крива 5: Ротор Савоніуса (drag-based, пік біля lambda=0.8, Cp=0.18)
    sav_pts = []
    for step in range(0, 21):
        l = step * 0.1
        if l <= 0.8:
            cp = 0.08 + 0.10 * math.sin(l / 0.8 * (math.pi / 2.0))
        elif l <= 1.8:
            cp = 0.18 * math.cos((l - 0.8) / 1.0 * (math.pi / 2.0))
            cp = max(0.0, cp)
        else:
            cp = 0.0
        sav_pts.append((X(l), Y(cp)))
    f.append(pline(sav_pts, color="#d35400", sw=2.0))
    f.append(text(X(0.85), Y(0.18) - 10, "Савоніус", size=10.5, color="#d35400", bold=True))

    render(os.path.join(IMG, "cp-tsr-curves.svg"), W, H, *f)


# ── 4. Крива вихідної електричної потужності P(v) ──────────────────────────────
def fig_power_curve_zones():
    """Чотири робочі зони вітроустановки на кривій генерації P(v)."""
    W, H = 940, 510
    f = []

    ox, oy = 90, 420
    axW, axH = 780, 340

    f.append(text(W / 2, 26, "Крива вихідної потужності малої вітроустановки P(v)", size=15, bold=True))

    # Осі
    f.append(arrow(ox, oy, ox, oy - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 25, oy, color=INK, sw=1.8))
    f.append(text(ox - 15, oy - axH - 10, "Електрична потужність P (Вт)", size=12.5, bold=True, anchor="start"))
    f.append(text(ox + axW + 20, oy + 25, "Швидкість вітру v (м/с)", size=12.5, bold=True, anchor="end"))

    def X(v):
        return ox + (v / 30.0) * axW

    def Y(p):
        return oy - (p / 1200.0) * axH

    # Швидкості меж зон
    v_ci = 3.0     # Cut-in
    v_rat = 11.0   # Rated
    v_co = 24.0    # Cut-out

    # Вертикальні лінії меж
    for v_val, lbl, col in ((v_ci, "v_ci = 3 м/с\n(Cut-in)", NEG),
                            (v_rat, "v_rated = 11 м/с\n(Номінал)", FIELD),
                            (v_co, "v_cut-out = 24 м/с\n(Вимкнення)", POS)):
        xp = X(v_val)
        f.append(line(xp, oy, xp, oy - axH, color=col, sw=1.5, dash="4 4"))
        f.append(textbox(xp, oy + 42, lbl, size=10.5, pad=4, fill="#ffffff", stroke=col)[0])

    # Горизонтальна лінія номінальної потужності P_rated = 1000 Вт
    y_rated = Y(1000)
    f.append(line(ox, y_rated, ox + axW, y_rated, color=MUTED, sw=1.2, dash="5 4"))
    f.append(text(ox - 10, y_rated + 4, "P_rated = 1000 Вт", size=11, color=MUTED, anchor="end", bold=True))

    # Крива потужності P(v)
    pts = []
    # Зона 1: 0 .. 3 м/с -> P = 0
    for step in range(0, 31):
        v = step * 0.1
        pts.append((X(v), Y(0.0)))
    # Зона 2: 3 .. 11 м/с -> кубічна характеристика
    for step in range(30, 111):
        v = step * 0.1
        ratio = (v - 3.0) / (11.0 - 3.0)
        p = 1000.0 * (ratio ** 2.6)
        pts.append((X(v), Y(p)))
    # Зона 3: 11 .. 24 м/с -> плато обмеження потужності 1000 Вт
    for step in range(110, 241):
        v = step * 0.1
        pts.append((X(v), Y(1000.0)))
    # Стрибок вниз при v_cut-out
    pts.append((X(24.0), Y(0.0)))
    # Зона 4: 24 .. 30 м/с -> P = 0
    for step in range(240, 301):
        v = step * 0.1
        pts.append((X(v), Y(0.0)))

    f.append(pline(pts, color=POS, sw=3.5))

    # Підписи зон угорі
    f.append(textbox(X(1.5), oy - axH + 30, "I. Зона спокою\nv < v_ci\nгенератор відімкнено", size=10.5, pad=5)[0])
    f.append(textbox(X(7.0), oy - axH + 30, "II. Зона MPPT (Cp,max)\nP ~ v³\nстеження за максимумом", size=10.5, pad=5, stroke=FIELD)[0])
    f.append(textbox(X(17.5), oy - axH + 30, "III. Обмеження потужності\nP = P_rated (постійна)\nскидання надлишку / furling", size=10.5, pad=5, stroke="#f39c12")[0])
    f.append(textbox(X(27.0), oy - axH + 30, "IV. Захист\nv > v_co\nаварійне гальмо", size=10.5, pad=5, stroke=POS)[0])

    render(os.path.join(IMG, "power-curve-zones.svg"), W, H, *f)


# ── 5. Профіль вітрового зсуву та висота щогли ────────────────────────────────
def fig_wind_shear_profile():
    """Епюра вітрового градієнта швидкості біля поверхні землі (Power Law Wind Shear)."""
    W, H = 960, 480
    f = []

    ox, oy = 100, 410
    axW, axH = 720, 330

    f.append(text(W / 2, 26, "Вітровий зсув: залежність швидкості вітру від висоти щогли", size=15, bold=True))

    # Осі
    f.append(arrow(ox, oy, ox + axW + 25, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axH - 20, color=INK, sw=1.8))
    f.append(text(ox + axW + 20, oy + 25, "Швидкість вітру v (м/с)", size=12.5, bold=True, anchor="end"))
    f.append(text(ox - 15, oy - axH - 10, "Висота щогли h (м)", size=12.5, bold=True, anchor="start"))

    def X(v):
        return ox + (v / 12.0) * axW

    def Y(h):
        return oy - (h / 25.0) * axH

    # Позначки висоти (5, 10, 15, 20 м)
    for h_val in (5, 10, 15, 20):
        yp = Y(h_val)
        f.append(line(ox - 6, yp, ox, yp, color=INK, sw=1.2))
        f.append(text(ox - 12, yp + 4, "%d м" % h_val, size=11, color=INK, anchor="end"))

    # Позначки швидкості вітру (2, 4, 6, 8, 10 м/с)
    for v_val in range(2, 13, 2):
        xp = X(v_val)
        if v_val <= 8:
            f.append(line(xp, oy, xp, oy - axH, color=MUTED, sw=0.7, dash="3 3"))
        else:
            f.append(line(xp, oy, xp, oy - 6, color=INK, sw=1.2))
        f.append(text(xp, oy + 18, "%d" % v_val, size=11, color=INK, anchor="middle"))

    # Межа зони приземних завихрень (h = 8м)
    f.append(line(ox, Y(8), ox + axW, Y(8), color=POS, sw=1.5, dash="6 4"))
    f.append(text(ox + axW - 10, Y(8) - 8, "Межа приземних перешкод (h = 8 м)", size=11, color=POS, anchor="end", bold=True))
    f.append(textbox(ox + 220, Y(4), "Приземна зона завихрень і високої турбулентності\n(будівлі, дерева, паркани) — монтаж вітряка заборонено!", size=11, pad=6, fill="#fdecea", stroke=POS)[0])

    # Крива вітрового зсуву за степеневим законом v(h) = v_10 * (h/10)^alpha (alpha=0.25 для передмістя)
    v_10 = 6.0
    alpha = 0.25
    pts = []
    for step in range(1, 251):
        h = step * 0.1
        v = v_10 * ((h / 10.0) ** alpha)
        pts.append((X(v), Y(h)))
    f.append(pline(pts, color=POS, sw=3.5))

    # Стрілки швидкості вітру на різних висотах (профіль швидкості)
    for h_check in (10, 16):
        v_c = v_10 * ((h_check / 10.0) ** alpha)
        yp = Y(h_check)
        f.append(arrow(ox, yp, X(v_c), yp, color=NEG, sw=2.0))
        p_ratio = (v_c / v_10) ** 3
        lbl = "h=%dм: v=%.1f м/с (потужність: %.0f%%)" % (h_check, v_c, p_ratio * 100)
        f.append(text(X(v_c) + 12, yp - 7, lbl, size=10.5, color=INK, anchor="start", bold=True))

    # Формула степеневого закону в рамці праворуч вгорі
    f.append(textbox(ox + axW - 100, Y(20), "Степеневий закон зсуву:\nv(h) = v_ref · (h / h_ref)^α\n\nПодвоєння висоти щогли\n(з 8 до 16 м) збільшує\nпотужність вітру майже вдвічі!", size=11, pad=7, fill="#eafaf1", stroke=FIELD)[0])

    render(os.path.join(IMG, "wind-shear-profile.svg"), W, H, *f)


def main():
    fig_betz_streamtube()
    fig_hawt_vs_vawt()
    fig_cp_tsr_curves()
    fig_power_curve_zones()
    fig_wind_shear_profile()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
