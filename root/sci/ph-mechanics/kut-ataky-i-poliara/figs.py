# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def airfoil_pts(cx, cy, chord, thick, aoa_deg, camber=0.04):
    """Повертає список точок (x, y) для аеродинамічного профілю."""
    a = math.radians(-aoa_deg)
    ca, sa = math.cos(a), math.sin(a)
    top, bot = [], []
    N = 32
    for i in range(N + 1):
        t = i / float(N)
        x = (t - 0.5) * chord
        th = thick * chord * (0.2969 * math.sqrt(max(0.0, t)) - 0.1260 * t - 0.3516 * (t**2) + 0.2843 * (t**3) - 0.1015 * (t**4))
        cam = camber * chord * 4.0 * t * (1.0 - t)
        yt = -cam - th / 2.0
        yb = -cam + th / 2.0
        top.append((x, yt))
        bot.append((x, yb))
    pts = top + bot[::-1]
    res = []
    for x, y in pts:
        xr = cx + x * ca - y * sa
        yr = cy + x * sa + y * ca
        res.append((xr, yr))
    return res


def airfoil_path_str(cx, cy, chord, thick, aoa_deg, camber=0.04):
    pts = airfoil_pts(cx, cy, chord, thick, aoa_deg, camber)
    d = []
    for k, (x, y) in enumerate(pts):
        d.append(("M" if k == 0 else "L") + "%.1f %.1f" % (x, y))
    return " ".join(d) + " Z"


# ── Фігура 1: Кут атаки та розклад аеродинамічних сил ──────────────────────────
def fig_airfoil_angles_forces():
    W, H = 820, 520
    cx, cy = 360, 270
    chord = 320
    aoa = 12.0
    body = []

    # Тло та межі
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Набігаючий потік v_inf (горизонтальні лінії зліва)
    for y_off in (-140, -90, -40, 40, 90, 140):
        y_pos = cy + y_off
        body.append(arrow(30, y_pos, 160, y_pos, color=NEG, sw=1.6))
    body.append(text(95, cy - 155, "Набігаючий потік v_inf", size=13, color=NEG, bold=True))

    # Профіль крила
    d_foil = airfoil_path_str(cx, cy, chord, 0.12, aoa, camber=0.04)
    body.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="2.2"/>' % (d_foil, INK))

    # Хорда (лінія від передньої кромки до задньої)
    a_rad = math.radians(-aoa)
    le_x = cx - 0.5 * chord * math.cos(a_rad)
    le_y = cy - 0.5 * chord * math.sin(a_rad)
    te_x = cx + 0.5 * chord * math.cos(a_rad)
    te_y = cy + 0.5 * chord * math.sin(a_rad)
    body.append(line(le_x - 40, le_y - 40 * math.tan(a_rad), te_x + 60, te_y + 60 * math.tan(a_rad), color=MUTED, sw=1.4, dash="6 4"))

    # Горизонтальна опорна лінія через LE для показу кута атаки alpha
    body.append(line(le_x - 30, le_y, le_x + 220, le_y, color=NEG, sw=1.4, dash="5 4"))
    
    # Дуга кута атаки alpha
    r_arc = 120
    arc_end_x = le_x + r_arc * math.cos(a_rad)
    arc_end_y = le_y + r_arc * math.sin(a_rad)
    body.append('<path d="M %.1f %.1f A %d %d 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0"/>' %
                (le_x + r_arc, le_y, r_arc, r_arc, arc_end_x, arc_end_y, POS))
    body.append(text(le_x + r_arc + 18, le_y - 12, "α (кут атаки)", size=13, color=POS, bold=True))

    # Центр тиску / аеродинамічний фокус (точка прикладання сил, x ≈ 0.25c)
    cp_x = cx - 0.25 * chord * math.cos(a_rad)
    cp_y = cy - 0.25 * chord * math.sin(a_rad)
    body.append(circle(cp_x, cp_y, 4.5, fill=POS, stroke=INK, sw=1.5))
    body.append(text(cp_x - 12, cp_y + 24, "x_ac (c/4)", size=12, color=INK, bold=True))

    # Вектори сил:
    # 1. Швидкісна система координат (Пов'язана з потоком):
    # Підйомна сила L (перпендикулярно v_inf, строго вгору)
    body.append(arrow(cp_x, cp_y, cp_x, cp_y - 170, color=POS, sw=2.8))
    tb_l, _, _ = textbox(cp_x - 90, cp_y - 170, "L (підіймальна сила)\nL ⟂ v_inf", size=12, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_l)

    # Сила опору D (вздовж v_inf, вправо)
    body.append(arrow(cp_x, cp_y, cp_x + 90, cp_y, color=NEG, sw=2.4))
    tb_d, _, _ = textbox(cp_x + 135, cp_y + 28, "D (лобовий опір)\nD ∥ v_inf", size=12, fill="#eff6ff", stroke=NEG, sw=1.2)
    body.append(tb_d)

    # Повна аеродинамічна сила R (сума L і D)
    r_vec_x = cp_x + 90
    r_vec_y = cp_y - 170
    body.append(line(cp_x, cp_y - 170, r_vec_x, r_vec_y, color=MUTED, sw=1.2, dash="3 3"))
    body.append(line(cp_x + 90, cp_y, r_vec_x, r_vec_y, color=MUTED, sw=1.2, dash="3 3"))
    body.append(arrow(cp_x, cp_y, r_vec_x, r_vec_y, color=FIELD, sw=2.6))
    body.append(text(r_vec_x + 22, r_vec_y - 8, "R (повна аеродинамічна сила)", size=13, color=FIELD, bold=True))

    # 2. Зв'язана система координат (нормальна N та тангенціальна/осьова A сили)
    # Нормаль до хорди (перпендикулярно хорді)
    norm_ang = a_rad - math.pi / 2.0
    n_len = 145
    nx = cp_x + n_len * math.cos(norm_ang)
    ny = cp_y + n_len * math.sin(norm_ang)
    body.append(arrow(cp_x, cp_y, nx, ny, color="#7c3aed", sw=2.0))
    tb_n, _, _ = textbox(nx - 75, ny + 35, "N (нормальна сила)\nN ⟂ хорді", size=11, fill="#f5f3ff", stroke="#7c3aed", sw=1.1)
    body.append(tb_n)

    # Поздовжній момент тангажу M_z (дугова стрілка навколо cp)
    body.append('<path d="M %.1f %.1f A 26 26 0 1 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>' %
                (cp_x + 24, cp_y - 10, cp_x + 10, cp_y - 24, "#b45309"))
    body.append(text(cp_x + 48, cp_y - 32, "M_ac (момент)", size=12, color="#b45309", bold=True))

    # Пояснювальна табличка внизу
    tb_bot, _, _ = textbox(cx + 40, H - 42,
                           "Швидкісна система: L = ½ρv²S·C_L,  D = ½ρv²S·C_D  |  Зв'язана: C_L = C_N·cos α − C_A·sin α",
                           size=12.5, fill="#f8fafc", stroke=LINE, sw=1.2)
    body.append(tb_bot)

    render(os.path.join(OUT, "airfoil-angles-forces.svg"), W, H, *body,
           title="Кут атаки α та розклад повної аеродинамічної сили R")


# ── Фігура 2: Залежності C_L(α) та C_D(α), критичний кут α_crit ────────────────
def fig_cl_cd_alpha_curves():
    W, H = 820, 480
    body = []
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Графік 1: C_L(α) зліва
    ox1, oy1 = 140, 340
    gw, gh = 230, 260
    # Осі
    body.append(arrow(ox1 - 40, oy1, ox1 + gw + 20, oy1, color=LINE, sw=1.5))
    body.append(arrow(ox1, oy1 + 30, ox1, oy1 - gh - 20, color=LINE, sw=1.5))
    body.append(text(ox1 + gw + 26, oy1 + 4, "α (°)", size=13, color=INK, bold=True))
    body.append(text(ox1 - 10, oy1 - gh - 26, "C_L", size=13, color=POS, bold=True))

    # Сітка та поділки
    for a_val in (-4, 0, 5, 10, 15, 20):
        px = ox1 + a_val * 11.5
        body.append(line(px, oy1 - 4, px, oy1 + 4, color=MUTED, sw=1.0))
        body.append(text(px, oy1 + 18, str(a_val), size=11, color=MUTED))
    for cl_val in (0.5, 1.0, 1.5):
        py = oy1 - cl_val * 140
        body.append(line(ox1 - 4, py, ox1 + 4, py, color=MUTED, sw=1.0))
        body.append(text(ox1 - 22, py + 4, "%.1f" % cl_val, size=11, color=MUTED))

    # Крива C_L(α): лінійна ділянка, потім купол, зрив (звалювання)
    pts_cl = []
    for deg in range(-5, 25):
        if deg <= 12:
            cl = 0.25 + 0.105 * deg  # dCL/da ~ 2*pi
        elif deg <= 15:
            cl = 1.51 + 0.03 * (deg - 12) - 0.015 * ((deg - 12)**2)
        else:
            cl = 1.45 - 0.08 * (deg - 15) - 0.003 * ((deg - 15)**2)
        px = ox1 + deg * 11.5
        py = oy1 - cl * 140
        pts_cl.append((px, py))
    d_cl = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_cl)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_cl, POS))

    # Точки на C_L:
    # 1. alpha_0 (нульова підйомна сила)
    a0_x = ox1 - 2.4 * 11.5
    body.append(circle(a0_x, oy1, 4, fill=POS, stroke=INK))
    body.append(text(a0_x - 18, oy1 - 12, "α₀", size=12, color=POS, bold=True))

    # 2. alpha_crit та CL_max
    crit_x = ox1 + 14.5 * 11.5
    crit_y = oy1 - 1.54 * 140
    body.append(circle(crit_x, crit_y, 5, fill=POS, stroke=INK))
    body.append(line(crit_x, crit_y, crit_x, oy1, color=POS, sw=1.2, dash="4 4"))
    body.append(line(crit_x, crit_y, ox1, crit_y, color=POS, sw=1.2, dash="4 4"))
    body.append(text(crit_x, oy1 + 34, "α_crit", size=12, color=POS, bold=True))
    body.append(text(ox1 - 32, crit_y + 4, "C_L,max", size=12, color=POS, bold=True))

    # Підпис зони зриву потоку
    tb_stall, _, _ = textbox(crit_x + 50, crit_y + 45, "Зрив потоку\n(Stall)", size=11, fill="#fef2f2", stroke=POS, sw=1.1)
    body.append(tb_stall)

    # Підпис нахилу кривої
    body.append(text(ox1 + 45, oy1 - 100, "dC_L/dα ≈ 2π", size=12, color=MUTED, italic=True))


    # Графік 2: C_D(α) справа
    ox2, oy2 = 540, 340
    body.append(arrow(ox2 - 40, oy2, ox2 + gw + 20, oy2, color=LINE, sw=1.5))
    body.append(arrow(ox2, oy2 + 30, ox2, oy2 - gh - 20, color=LINE, sw=1.5))
    body.append(text(ox2 + gw + 26, oy2 + 4, "α (°)", size=13, color=INK, bold=True))
    body.append(text(ox2 - 10, oy2 - gh - 26, "C_D", size=13, color=NEG, bold=True))

    for a_val in (-4, 0, 5, 10, 15, 20):
        px = ox2 + a_val * 11.5
        body.append(line(px, oy2 - 4, px, oy2 + 4, color=MUTED, sw=1.0))
        body.append(text(px, oy2 + 18, str(a_val), size=11, color=MUTED))
    for cd_val in (0.05, 0.10, 0.15, 0.20):
        py = oy2 - cd_val * 1100
        body.append(line(ox2 - 4, py, ox2 + 4, py, color=MUTED, sw=1.0))
        body.append(text(ox2 - 24, py + 4, "%.2f" % cd_val, size=11, color=MUTED))

    # Крива C_D(α): полога парабола, потім різкий вибух опору при зриві
    pts_cd = []
    for deg in range(-5, 25):
        if deg <= 12:
            cd = 0.008 + 0.0003 * ((deg - 2)**2)
        elif deg <= 15:
            cd = 0.038 + 0.012 * (deg - 12) + 0.004 * ((deg - 12)**2)
        else:
            cd = 0.11 + 0.022 * (deg - 15) + 0.002 * ((deg - 15)**2)
        px = ox2 + deg * 11.5
        py = oy2 - cd * 1100
        pts_cd.append((px, py))
    d_cd = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts_cd)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_cd, NEG))

    # Мінімум опору C_D0
    cd0_x = ox2 + 2 * 11.5
    cd0_y = oy2 - 0.008 * 1100
    body.append(circle(cd0_x, cd0_y, 4, fill=NEG, stroke=INK))
    body.append(text(cd0_x + 26, cd0_y + 14, "C_D,min", size=12, color=NEG, bold=True))

    # Стрибок опору при критичному куті
    crit2_x = ox2 + 14.5 * 11.5
    crit2_y = oy2 - 0.095 * 1100
    body.append(circle(crit2_x, crit2_y, 5, fill=NEG, stroke=INK))
    body.append(line(crit2_x, crit2_y, crit2_x, oy2, color=NEG, sw=1.2, dash="4 4"))
    tb_drag_jump, _, _ = textbox(crit2_x - 55, crit2_y - 45, "Стрибок опору\nчерез відрив", size=11, fill="#eff6ff", stroke=NEG, sw=1.1)
    body.append(tb_drag_jump)

    # Заголовок блоку внизу
    tb_info, _, _ = textbox(W / 2, H - 40,
                            "Лінійний приріст C_L змінюється зривом при α_crit; опір C_D зростає лавиноподібно",
                            size=13, fill="#f8fafc", stroke=LINE, sw=1.2)
    body.append(tb_info)

    render(os.path.join(OUT, "cl-cd-alpha-curves.svg"), W, H, *body,
           title="Залежності коефіцієнтів C_L(α) та C_D(α)")


# ── Фігура 3: Поляра Лілієнталя C_L(C_D) та дотичні ───────────────────────────
def fig_lilienthal_polar():
    W, H = 840, 560
    ox, oy = 120, 430
    body = []
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Осі
    body.append(arrow(ox - 30, oy, ox + 640, oy, color=LINE, sw=1.6))
    body.append(arrow(ox, oy + 40, ox, oy - 380, color=LINE, sw=1.6))
    body.append(text(ox + 655, oy + 4, "C_D", size=14, color=NEG, bold=True))
    body.append(text(ox - 14, oy - 390, "C_L", size=14, color=POS, bold=True))

    # Поділки C_D
    for cd_val in (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16):
        px = ox + cd_val * 3800
        body.append(line(px, oy - 4, px, oy + 4, color=MUTED, sw=1.0))
        body.append(text(px, oy + 18, "%.2f" % cd_val, size=11, color=MUTED))

    # Поділки C_L
    for cl_val in (0.4, 0.8, 1.2, 1.6):
        py = oy - cl_val * 220
        body.append(line(ox - 4, py, ox + 4, py, color=MUTED, sw=1.0))
        body.append(text(ox - 24, py + 4, "%.1f" % cl_val, size=11, color=MUTED))

    # Точки поляри (cd, cl, alpha_deg, name)
    polar_data = [
        (-4.0, 0.016, -0.15, "α = −4°"),
        (-2.0, 0.010,  0.05, "α₀ (C_L=0)"),
        ( 0.0, 0.008,  0.25, "α = 0°"),
        ( 2.0, 0.009,  0.46, "α_minD"),
        ( 4.0, 0.012,  0.67, "α = 4°"),
        ( 6.0, 0.016,  0.88, "K_max (найвигідніший)"),
        ( 8.0, 0.022,  1.09, "α = 8°"),
        (10.0, 0.030,  1.28, "E_max (економічний)"),
        (12.0, 0.042,  1.45, "α = 12°"),
        (14.5, 0.068,  1.56, "C_L,max (α_crit)"),
        (16.5, 0.105,  1.42, "Звалювання"),
        (19.0, 0.150,  1.20, "Закритичний режим"),
    ]

    pts_scr = []
    for a_deg, cd, cl, lbl in polar_data:
        px = ox + cd * 3800
        py = oy - cl * 220
        pts_scr.append((px, py, a_deg, cd, cl, lbl))

    d_pol = "M " + " L ".join("%.1f %.1f" % (p[0], p[1]) for p in pts_scr)
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d_pol, "#0f766e"))

    # Дотична з початку координат — режим K_max
    # Точка K_max (6 град): cd=0.016, cl=0.88 -> K = 55
    k_pt = pts_scr[5]
    tan_len = 1.6
    body.append(line(ox, oy, ox + k_pt[3] * 3800 * tan_len, oy - k_pt[4] * 220 * tan_len, color=POS, sw=1.8, dash="5 4"))
    body.append(circle(k_pt[0], k_pt[1], 5.5, fill=POS, stroke=INK))
    tb_kmax, _, _ = textbox(k_pt[0] - 120, k_pt[1] - 30,
                            "K_max = (C_L/C_D)_max\nНайвигідніший кут (макс. дальність)",
                            size=12, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_kmax)

    # Дотична для економічного режиму (C_L^1.5 / C_D)_max
    e_pt = pts_scr[7]
    body.append(circle(e_pt[0], e_pt[1], 5.5, fill=FIELD, stroke=INK))
    tb_emax, _, _ = textbox(e_pt[0] + 130, e_pt[1] - 18,
                            "Економічний режим: (C_L^{3/2}/C_D)_max\nМінімальна потужність (макс. тривалість)",
                            size=12, fill="#ecfdf5", stroke=FIELD, sw=1.2)
    body.append(tb_emax)

    # Критична точка C_L,max
    crit_pt = pts_scr[9]
    body.append(circle(crit_pt[0], crit_pt[1], 6, fill="#b91c1c", stroke=INK))
    tb_crit, _, _ = textbox(crit_pt[0] + 130, crit_pt[1] + 18,
                            "C_L,max при α_crit\nМінімальна швидкість v_min (Stall)",
                            size=12, fill="#fee2e2", stroke="#b91c1c", sw=1.2)
    body.append(tb_crit)

    # Точка мінімального опору
    dmin_pt = pts_scr[3]
    body.append(circle(dmin_pt[0], dmin_pt[1], 4.5, fill=NEG, stroke=INK))
    body.append(text(dmin_pt[0] + 48, dmin_pt[1] + 14, "C_D,min (швидкісний)", size=11, color=NEG, bold=True))

    # Пояснення зон: 1-й та 2-й режими польоту
    body.append(rect(ox + 320, oy - 290, 290, 80, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    body.append(text(ox + 465, oy - 268, "Режими за швидкістю польоту:", size=12.5, color=INK, bold=True))
    body.append(text(ox + 465, oy - 246, "• 1-й режим (зліва від K_max): стійкий за тягою", size=11.5, color=FIELD))
    body.append(text(ox + 465, oy - 226, "• 2-й режим (справа від K_max): нестійкий (другий режим)", size=11.5, color=POS))

    render(os.path.join(OUT, "lilienthal-polar.svg"), W, H, *body,
           title="Поляра Лілієнталя C_L(C_D) та характерні аеродинамічні точки")


# ── Фігура 4: Анатомія зриву потоку (три фази обтікання) ──────────────────────
def fig_stall_mechanisms():
    W, H = 820, 520
    body = []
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    rows = [
        ("1. Безодривне обтікання (α = 4°): примежовий шар ламінарний → турбулентний, плавний схід", 4.0, 100, False),
        ("2. Початок відриву (α = 12°): несприятливий градієнт тиску dp/dx > 0 гальмує потік біля задньої кромки", 12.0, 250, True),
        ("3. Повний зрив (α = 18° > α_crit): каверна вихорів над спинкою, обвал C_L, стрибок опору D", 18.0, 400, "full"),
    ]

    for title_text, a_deg, cy, sep_mode in rows:
        body.append(text(40, cy - 42, title_text, size=12.5, color=INK, bold=True, anchor="start"))
        cx = 260
        chord = 240
        d_f = airfoil_path_str(cx, cy, chord, 0.12, a_deg, camber=0.04)
        body.append('<path d="%s" fill="#f1f5f9" stroke="%s" stroke-width="1.8"/>' % (d_f, INK))

        # Лінії потоку
        a_rad = math.radians(-a_deg)
        te_x = cx + 0.5 * chord * math.cos(a_rad)
        te_y = cy + 0.5 * chord * math.sin(a_rad)
        le_x = cx - 0.5 * chord * math.cos(a_rad)
        le_y = cy - 0.5 * chord * math.sin(a_rad)

        if sep_mode is False:
            # Плавні лінії над профілем
            for off in (-24, -12, -4):
                body.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                            (le_x - 70, le_y + off, cx, cy - 30 + off, te_x + 80, te_y + off * 0.5 + 10, FIELD))
            body.append(text(cx + 250, cy - 2, "Притиснутий потік\n(C_L зростає лінійно)", size=11.5, color=FIELD, bold=True))
        elif sep_mode is True:
            # Відрив від задньої кромки
            for off in (-28, -16):
                body.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                            (le_x - 70, le_y + off, cx - 30, cy - 32 + off, te_x + 80, te_y - 20 + off, "#b45309"))
            # Вихорець біля TE
            body.append('<circle cx="%d" cy="%d" r="12" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3 3"/>' %
                        (te_x - 20, te_y - 16, POS))
            body.append(text(cx + 250, cy - 2, "Відрив задньої кромки\n(Trailing-edge stall)", size=11.5, color="#b45309", bold=True))
        else:
            # Повний зрив — масивна вихрова область
            for off in (-40, -25):
                body.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                            (le_x - 70, le_y + off, le_x + 30, cy - 65 + off, te_x + 90, cy - 70 + off, POS))
            # Кілька вихорів
            for vx, vy, vr in ((cx - 30, cy - 35, 14), (cx + 35, cy - 32, 18), (te_x - 25, te_y - 28, 20)):
                body.append('<circle cx="%d" cy="%d" r="%d" fill="#fee2e2" stroke="%s" stroke-width="1.5"/>' % (vx, vy, vr, POS))
            body.append(text(cx + 250, cy - 2, "Глибоке звалювання!\n(Deep Stall / Обвал C_L)", size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "stall-mechanisms.svg"), W, H, *body,
           title="Анатомія розвитку відриву потоку на профілі")


# ── Фігура 5: Ламінарна бульбашка відриву (LSB) при Re < 10^5 ──────────────────
def fig_low_re_lsb():
    W, H = 820, 460
    body = []
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    cx, cy = 380, 250
    chord = 540
    # Профіль (верхня поверхня детально)
    pts = airfoil_pts(cx, cy, chord, 0.10, 6.0, camber=0.03)
    d_foil = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts) + " Z"
    body.append('<path d="%s" fill="#f8fafc" stroke="%s" stroke-width="2.2"/>' % (d_foil, INK))

    # Координати на спинці профілю
    # S - точка ламінарного відриву (x ~ 0.20c)
    # T - точка переходу (x ~ 0.45c)
    # R - точка турбулентного приєднання (x ~ 0.65c)
    sx, sy = 230, 208
    tx, ty = 360, 192
    rx, ry = 480, 218

    # Ламінарний примежовий шар до точки S (тонкий зелений)
    body.append('<path d="M 125 240 Q 170 216 230 208" fill="none" stroke="%s" stroke-width="2.4"/>' % FIELD)
    tb_lam, _, _ = textbox(165, 175, "1. Ламінарний шар\n(стійкий до S)", size=11, fill="#ecfdf5", stroke=FIELD, sw=1.1)
    body.append(tb_lam)

    # Бульбашка (LSB): замкнена область рециркуляції
    body.append('<path d="M 230 208 Q 350 170 480 218 Q 350 202 230 208 Z" fill="#fef3c7" stroke="%s" stroke-width="2.0" stroke-dasharray="5 3"/>' % "#d97706")

    # Відірваний шар змішування над бульбашкою (хвилі нестійкості Кельвіна-Гельмгольца)
    body.append('<path d="M 230 208 Q 300 178 360 176 T 420 182 T 480 218" fill="none" stroke="%s" stroke-width="2.2"/>' % POS)

    # Турбулентний приєднаний шар після точки R (товстий червоний)
    body.append('<path d="M 480 218 Q 560 252 640 286" fill="none" stroke="%s" stroke-width="3.2"/>' % POS)
    tb_turb, _, _ = textbox(570, 230, "4. Турбулентне приєднання\n(енергійне перемішування)", size=11, fill="#fef2f2", stroke=POS, sw=1.1)
    body.append(tb_turb)

    # Точки на бульбашці
    body.append(circle(sx, sy, 4.5, fill=FIELD, stroke=INK))
    body.append(text(sx, sy + 22, "S (відрив)", size=11.5, color=FIELD, bold=True))

    body.append(circle(tx, 176, 4.5, fill="#d97706", stroke=INK))
    body.append(text(tx, 155, "T (перехід)", size=11.5, color="#d97706", bold=True))

    body.append(circle(rx, ry, 4.5, fill=POS, stroke=INK))
    body.append(text(rx, ry + 22, "R (приєднання)", size=11.5, color=POS, bold=True))

    # Вихор усередині бульбашки
    body.append('<ellipse cx="350" cy="192" rx="35" ry="9" fill="none" stroke="#b45309" stroke-width="1.4" stroke-dasharray="3 3"/>')
    body.append(text(350, 196, "Застійна зона (LSB)", size=11, color="#b45309", bold=True))

    # Нижній блок: Чому це критично для дронів
    tb_drone, _, _ = textbox(W / 2, H - 46,
                             "При Re < 10⁵ відрив відбувається легко; якщо шар не приєднається (розрив бульбашки) — настає раптовий Stall",
                             size=12.5, fill="#f8fafc", stroke=LINE, sw=1.2)
    body.append(tb_drone)

    render(os.path.join(OUT, "low-re-lsb-bubble.svg"), W, H, *body,
           title="Ламінарна бульбашка відриву (LSB) на профілі лопаті дрона при малих Re")


def main():
    fig_airfoil_angles_forces()
    fig_cl_cd_alpha_curves()
    fig_lilienthal_polar()
    fig_stall_mechanisms()
    fig_low_re_lsb()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
