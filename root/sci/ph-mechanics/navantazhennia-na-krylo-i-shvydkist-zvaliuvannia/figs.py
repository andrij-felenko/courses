# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Спектр питомого навантаження на крило ──────────────────────────
def fig_wing_loading_spectrum():
    W, H = 840, 480
    body = []

    # Тло
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Заголовок зверху
    tb_hdr, _, _ = textbox(W / 2, 42, "Спектр питомого навантаження на крило W/S та експлуатаційний компроміс", size=14, bold=True, fill="#f8fafc", stroke=LINE)
    body.append(tb_hdr)

    # Горизонтальна вісь навантаження W/S (шкала)
    y_axis = 220
    x_start, x_end = 80, 760
    body.append(arrow(x_start - 20, y_axis, x_end + 30, y_axis, color=INK, sw=2.0))
    body.append(text(x_end + 35, y_axis - 12, "W/S (кг/м²)", size=12, color=INK, anchor="end", bold=True))

    # Категорії апаратів: (назва, w_s_str, x_pos, y_offset, колір, опис)
    categories = [
        ("Параплан /\nПланер F3J", "1.5 – 5", 100, -95, "#0284c7", "v_зв ≈ 20–30 км/год\nЧутливий до вітру"),
        ("Легкий БПЛА /\nПіноліт", "10 – 25", 210, 85, "#0d9488", "v_зв ≈ 35–50 км/год\nРучний старт"),
        ("Cessna 172 /\nЛегка авіація", "60 – 75", 340, -95, "#16a34a", "v_зв ≈ 85–95 км/год\nГрунтові ЗПС"),
        ("P-51 Mustang /\nПоршневий винищувач", "180 – 220", 470, 85, "#d97706", "v_зв ≈ 160–180 км/год\nВисока маневреність"),
        ("Boeing 737 / A320 /\nПасажирський лайнер", "500 – 650", 600, -95, "#ea580c", "v_зв ≈ 240–270 км/год\nПотужна механізація"),
        ("F-104 / Су-27 /\nНадзвуковий винищувач", "600 – 750", 720, 85, "#dc2626", "v_зв ≈ 280–320 км/год\nСтійкість у поривах")
    ]

    for title, ws_val, cx, y_off, col, desc in categories:
        y_box = y_axis + y_off
        body.append(line(cx, y_axis - 6, cx, y_axis + 6, color=INK, sw=2.0))
        body.append(line(cx, y_axis + (8 if y_off > 0 else -8), cx, y_box + (-45 if y_off > 0 else 45), color=col, sw=1.2, dash="3 3"))
        
        body.append(circle(cx, y_axis, 4.0, fill=col, stroke=INK, sw=1.2))
        body.append(text(cx, y_axis + (18 if y_off < 0 else -10), ws_val, size=11, color=col, bold=True))

        content = title + "\n" + desc
        tb, _, _ = textbox(cx, y_box, content, size=11, fill="#f8fafc", stroke=col, sw=1.4)
        body.append(tb)

    # Порівняльні блоки внизу (компроміс)
    w_block = 330
    tb_left, _, _ = textbox(215, 410, "Низьке навантаження (W/S < 40 кг/м²):\n+ Коротка дистанція зльоту та посадки\n+ Низька швидкість звалювання, круті віражі\n− Сильна бовтанка в турбулентності, обмежена швидкість", size=11, fill="#f0fdf4", stroke="#16a34a", min_w=w_block)
    body.append(tb_left)

    tb_right, _, _ = textbox(625, 410, "Високе навантаження (W/S > 300 кг/м²):\n+ Висока крейсерська швидкість, малий хвильовий опір\n+ Плавний рух у поривах вітру (високий комфорт)\n− Величезні швидкості посадки, довгі бетонні ЗПС", size=11, fill="#fef2f2", stroke="#dc2626", min_w=w_block)
    body.append(tb_right)

    render(os.path.join(OUT, 'wing-loading-spectrum.svg'), W, H, *body)


# ── Фігура 2: Динаміка сил та зростання швидкості звалювання у віражі ─────────
def fig_turn_stall_dynamics():
    W, H = 840, 470
    body = []

    # Тло
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Заголовок
    tb_hdr, _, _ = textbox(W / 2, 38, "Рівновага сил у координованому віражі та зростання швидкості звалювання", size=14, bold=True, fill="#f8fafc", stroke=LINE)
    body.append(tb_hdr)

    # ── Ліва частина: Схема сил літака у віражі з креном φ ──
    cx, cy = 200, 230
    phi_deg = 45.0
    phi_rad = math.radians(phi_deg)

    # Горизонт
    body.append(line(50, cy + 80, 350, cy + 80, color=MUTED, sw=1.2, dash="4 4"))
    body.append(text(75, cy + 72, "Горизонт", size=11, color=MUTED))

    # Силует літака (нахилений на кут phi)
    wing_len = 100
    wx1 = cx - wing_len * math.cos(phi_rad)
    wy1 = cy + wing_len * math.sin(phi_rad)
    wx2 = cx + wing_len * math.cos(phi_rad)
    wy2 = cy - wing_len * math.sin(phi_rad)
    body.append(line(wx1, wy1, wx2, wy2, color=INK, sw=4.0))

    fuse_len = 35
    fx1 = cx - fuse_len * math.sin(phi_rad)
    fy1 = cy - fuse_len * math.cos(phi_rad)
    fx2 = cx + fuse_len * math.sin(phi_rad)
    fy2 = cy + fuse_len * math.cos(phi_rad)
    body.append(line(fx1, fy1, fx2, fy2, color=INK, sw=2.5))
    body.append(circle(cx, cy, 5.0, fill=POS, stroke=INK, sw=1.5))

    # Дуга кута крену phi від вертикалі
    body.append(line(cx, cy, cx, cy - 130, color=MUTED, sw=1.2, dash="4 4"))
    r_arc = 75
    arc_x = cx + r_arc * math.sin(phi_rad)
    arc_y = cy - r_arc * math.cos(phi_rad)
    body.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>' %
                (cx, cy - r_arc, r_arc, r_arc, arc_x, arc_y, POS))
    body.append(text(cx + 26, cy - 82, "φ = 45°", size=12, color=POS, bold=True))

    # Вектор підйомної сили L (перпендикулярно крилу)
    lift_len = 145
    lx = cx + lift_len * math.sin(phi_rad)
    ly = cy - lift_len * math.cos(phi_rad)
    body.append(arrow(cx, cy, lx, ly, color=POS, sw=2.8))
    body.append(text(lx + 10, ly - 5, "L = W / cos φ", size=12, color=POS, bold=True))

    # Проекції підйомної сили:
    body.append(arrow(cx, cy, cx, cy - lift_len * math.cos(phi_rad), color="#16a34a", sw=2.0))
    body.append(text(cx - 10, cy - lift_len * math.cos(phi_rad) - 8, "L·cos φ = W", size=11, color="#16a34a", anchor="end", bold=True))

    body.append(arrow(cx, cy, cx + lift_len * math.sin(phi_rad), cy, color=NEG, sw=2.0))
    body.append(text(cx + lift_len * math.sin(phi_rad) + 8, cy + 15, "F_ц = m·v²/R", size=11, color=NEG, bold=True))

    body.append(arrow(cx, cy, cx, cy + 105, color=INK, sw=2.4))
    body.append(text(cx + 12, cy + 95, "W = m·g", size=12, color=INK, bold=True))

    # ── Права частина: Графік збільшення перевантаження та швидкості звалювання ──
    gx, gy = 440, 95
    gw, gh = 360, 260
    
    body.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    
    body.append(line(gx + 50, gy + gh - 40, gx + gw - 20, gy + gh - 40, color=LINE, sw=1.5))
    body.append(line(gx + 50, gy + gh - 40, gx + 50, gy + 20, color=LINE, sw=1.5))
    
    body.append(text(gx + gw - 15, gy + gh - 22, "Крен φ (°)", size=11, color=INK, anchor="end", bold=True))
    body.append(text(gx + 45, gy + 15, "Кратність", size=11, color=INK, anchor="end", bold=True))

    angles = [0, 30, 45, 60, 70, 75]
    for ang in angles:
        px = gx + 50 + (ang / 80.0) * (gw - 80)
        body.append(line(px, gy + gh - 40, px, gy + gh - 35, color=LINE, sw=1.2))
        body.append(text(px, gy + gh - 22, str(ang) + "°", size=11, color=INK))

    pts_nz, pts_v = [], []
    for deg in range(0, 76, 2):
        r = math.radians(deg)
        nz = 1.0 / math.cos(r)
        v_rat = math.sqrt(nz)
        px = gx + 50 + (deg / 80.0) * (gw - 80)
        
        y_scale = (gh - 70) / 3.0
        py_nz = (gy + gh - 40) - (nz - 1.0) * y_scale
        py_v = (gy + gh - 40) - (v_rat - 1.0) * y_scale
        
        pts_nz.append((px, max(gy + 25, py_nz)))
        pts_v.append((px, py_v))

    d_nz = "M " + " L ".join(["%.1f %.1f" % p for p in pts_nz])
    d_v = "M " + " L ".join(["%.1f %.1f" % p for p in pts_v])
    
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_nz, POS))
    body.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_v, NEG))

    p60_x = gx + 50 + (60.0 / 80.0) * (gw - 80)
    p60_ynz = (gy + gh - 40) - (2.0 - 1.0) * ((gh - 70) / 3.0)
    p60_yv = (gy + gh - 40) - (math.sqrt(2.0) - 1.0) * ((gh - 70) / 3.0)
    
    body.append(circle(p60_x, p60_ynz, 4.0, fill=POS, stroke=INK, sw=1.2))
    body.append(circle(p60_x, p60_yv, 4.0, fill=NEG, stroke=INK, sw=1.2))
    
    body.append(text(p60_x - 8, p60_ynz - 10, "n_z = 2.0 g", size=11, color=POS, anchor="end", bold=True))
    body.append(text(p60_x + 8, p60_yv + 15, "v_зв = 1.41·v₀", size=11, color=NEG, bold=True))

    body.append(line(gx + 70, gy + 45, gx + 95, gy + 45, color=POS, sw=2.6))
    body.append(text(gx + 102, gy + 49, "Перевантаження n_z = 1/cos φ", size=11, color=POS, anchor="start", bold=True))
    
    body.append(line(gx + 70, gy + 68, gx + 95, gy + 68, color=NEG, sw=2.6))
    body.append(text(gx + 102, gy + 72, "Швидкість звалювання v_зв/v₀ = √(n_z)", size=11, color=NEG, anchor="start", bold=True))

    tb_bot, _, _ = textbox(W / 2, 420, "При крені 60° нормальне перевантаження подвоюється (2.0 g), а швидкість звалювання зростає на 41%.\nУ крутому віражі літак звалюється на значно вищій швидкості, ніж у горизонтальному польоті!", size=11, fill="#fef2f2", stroke=POS, min_w=760)
    body.append(tb_bot)

    render(os.path.join(OUT, 'turn-stall-dynamics.svg'), W, H, *body)


# ── Фігура 3: Зона зародження звалювання на крилах різної форми ───────────────
def fig_wing_stall_progression():
    W, H = 840, 480
    body = []

    # Тло
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Заголовок
    tb_hdr, _, _ = textbox(W / 2, 38, "Вплив форми крила в плані на зону початкового зриву потоку", size=14, bold=True, fill="#f8fafc", stroke=LINE)
    body.append(tb_hdr)

    cards = [
        ("1. Пряме прямокутне крило", 220, 150, "root", "#16a34a",
         "Зрив починається з кореня крила.\n+ Елерони на кінцях лишаються обдуваними\n+ Слід зриву б'є по оперенню (бафтинг)"),
        
        ("2. Трапецієподібне (звуження > 2.5)", 620, 150, "tip", "#dc2626",
         "Зрив починається з кінцівок крила.\n− Раптова втрата реакції на елерони\n− Схильність до зриву в штопор"),
        
        ("3. Стрілоподібне крило", 220, 340, "swept", "#d97706",
         "Сповзання примежового шару до кінцівок.\n− Ранній кінцевий зрив і кабрирування\n− Потребує аеродинамічних гребенів"),
        
        ("4. Крило з круткою (Washout -3°)", 620, 340, "washout", "#0284c7",
         "Геометричне зменшення кута на кінцівках.\n+ Корінь досягає α_crit раніше за кінцівки\n+ Гарантована ефективність елеронів")
    ]

    for title, cx, cy, wtype, col, desc in cards:
        cw, ch = 380, 160
        # Контур картки без заливки, щоб уникнути конфліктів rect
        body.append(rect(cx - cw/2, cy - ch/2, cw, ch, fill="none", stroke="#cbd5e1", sw=1.0, rx=6))
        body.append(text(cx - cw/2 + 15, cy - ch/2 + 22, title, size=12, color=INK, anchor="start", bold=True))

        kx, ky = cx - 110, cy + 22
        span = 55
        chord = 34

        if wtype == "root":
            body.append(rect(kx - span, ky - chord/2, span * 2, chord, fill="#ffffff", stroke=INK, sw=1.4, rx=2))
            body.append(circle(kx, ky, 12, fill="#fee2e2", stroke=POS, sw=1.2))
            body.append(text(kx, ky + 3, "Зрив", size=10, color=POS, bold=True))
            body.append(rect(kx - span + 2, ky + chord/4, 18, chord/4, fill="#dcfce7", stroke="#16a34a", sw=1.0))
            body.append(rect(kx + span - 20, ky + chord/4, 18, chord/4, fill="#dcfce7", stroke="#16a34a", sw=1.0))
            
        elif wtype == "tip":
            pts_l = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 18, kx - span, ky - 7, kx - span, ky + 7, kx, ky + 18
            )
            pts_r = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 18, kx + span, ky - 7, kx + span, ky + 7, kx, ky + 18
            )
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_l, INK))
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_r, INK))
            body.append(circle(kx - span + 7, ky, 9, fill="#fee2e2", stroke=POS, sw=1.2))
            body.append(circle(kx + span - 7, ky, 9, fill="#fee2e2", stroke=POS, sw=1.2))
            body.append(text(kx - span + 7, ky + 3, "Зрив", size=9, color=POS, bold=True))
            body.append(text(kx + span - 7, ky + 3, "Зрив", size=9, color=POS, bold=True))

        elif wtype == "swept":
            sw_back = 26
            pts_l = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 16, kx - span, ky - 16 + sw_back, kx - span, ky + 6 + sw_back, kx, ky + 16
            )
            pts_r = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 16, kx + span, ky - 16 + sw_back, kx + span, ky + 6 + sw_back, kx, ky + 16
            )
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_l, INK))
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_r, INK))
            body.append(circle(kx - span + 7, ky + sw_back - 3, 9, fill="#fee2e2", stroke=POS, sw=1.2))
            body.append(circle(kx + span - 7, ky + sw_back - 3, 9, fill="#fee2e2", stroke=POS, sw=1.2))

        elif wtype == "washout":
            pts_l = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 18, kx - span, ky - 7, kx - span, ky + 7, kx, ky + 18
            )
            pts_r = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
                kx, ky - 18, kx + span, ky - 7, kx + span, ky + 7, kx, ky + 18
            )
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_l, INK))
            body.append('<polygon points="%s" fill="#ffffff" stroke="%s" stroke-width="1.4"/>' % (pts_r, INK))
            body.append(circle(kx, ky, 12, fill="#fee2e2", stroke=POS, sw=1.2))
            body.append(text(kx, ky + 3, "Зрив", size=10, color=POS, bold=True))
            body.append(text(kx - span + 8, ky - 12, "−3°", size=10, color="#0284c7", bold=True))
            body.append(text(kx + span - 8, ky - 12, "−3°", size=10, color="#0284c7", bold=True))

        tb_desc, _, _ = textbox(cx + 65, cy + 22, desc, size=10, fill="none", stroke="#cbd5e1", sw=1.0, min_w=190)
        body.append(tb_desc)

    render(os.path.join(OUT, 'wing-stall-progression.svg'), W, H, *body)


# ── Фігура 4: Повна діаграма маневреності V-n (Flight Envelope) ───────────────
def fig_vn_flight_envelope():
    W, H = 860, 520
    body = []

    # Тло
    body.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=8))

    # Заголовок
    tb_hdr, _, _ = textbox(W / 2, 35, "Діаграма маневреності V-n (експлуатаційний конверт перевантажень)", size=14, bold=True, fill="#f8fafc", stroke=LINE)
    body.append(tb_hdr)

    ox = 110
    oy = 340
    scale_y = 45.0
    scale_x = 1.35

    v_s0 = 100.0
    v_a = 195.0
    v_c = 280.0
    v_ne = 350.0
    v_d = 400.0

    n_max_pos = 3.8
    n_max_neg = -1.52

    # Осі координат
    body.append(line(ox - 30, oy, ox + 680, oy, color=MUTED, sw=1.2, dash="4 4"))  # 0 g
    body.append(line(ox, oy + 120, ox, oy - 230, color=LINE, sw=1.8))             # Вісь n
    body.append(line(ox - 20, oy - scale_y * 1.0, ox + 680, oy - scale_y * 1.0, color="#94a3b8", sw=1.0, dash="5 3")) # 1 g

    body.append(text(ox - 15, oy - 225, "n (перевантаження)", size=12, color=INK, anchor="start", bold=True))
    body.append(text(ox + 675, oy + 25, "Швидкість польоту v (км/год)", size=12, color=INK, anchor="end", bold=True))

    for n_val in [-1.5, -1.0, 0.0, 1.0, 2.0, 3.0, 3.8]:
        y_pos = oy - n_val * scale_y
        body.append(line(ox - 5, y_pos, ox + 5, y_pos, color=LINE, sw=1.2))
        lbl = "+%.1fg" % n_val if n_val > 0 else ("%.1fg" % n_val if n_val < 0 else "0g")
        body.append(text(ox - 12, y_pos + 4, lbl, size=11, color=INK, anchor="end", bold=(n_val in [1.0, 3.8, -1.5])))

    pts_pos_stall = []
    for v in range(0, int(v_a) + 1, 5):
        n = (v / v_s0) ** 2
        px = ox + v * scale_x
        py = oy - min(n, n_max_pos) * scale_y
        pts_pos_stall.append((px, py))

    v_a_neg = 148.0
    pts_neg_stall = []
    for v in range(int(v_a_neg), -1, -5):
        n = - (v / 120.0) ** 2
        px = ox + v * scale_x
        py = oy - max(n, n_max_neg) * scale_y
        pts_neg_stall.append((px, py))

    envelope_pts = pts_pos_stall + [
        (ox + v_ne * scale_x, oy - n_max_pos * scale_y),
        (ox + v_d * scale_x, oy),
        (ox + v_c * scale_x, oy - n_max_neg * scale_y),
        (ox + v_a_neg * scale_x, oy - n_max_neg * scale_y)
    ] + pts_neg_stall

    d_poly = "M " + " L ".join(["%.1f %.1f" % p for p in envelope_pts]) + " Z"
    body.append('<path d="%s" fill="#f0fdf4" stroke="#16a34a" stroke-width="2.2"/>' % d_poly)

    body.append(text(ox + 45, oy - 80, "Зона\nзвалювання\n(Stall)", size=11, color=NEG, anchor="middle", bold=True))

    # Зона залишкових деформацій (вище n_max)
    body.append(rect(ox + v_a * scale_x, oy - (n_max_pos + 1.1) * scale_y, (v_ne - v_a) * scale_x, 1.1 * scale_y, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    body.append(text(ox + (v_a + v_ne)/2 * scale_x, oy - (n_max_pos + 0.55) * scale_y + 4, "Зона пластичних деформацій конструкції", size=10, color="#b45309", bold=True))

    body.append(text(ox + (v_a + v_ne)/2 * scale_x, oy - 220, "Зона руйнування крила (n > n_граничне)", size=11, color=POS, bold=True))

    speeds = [
        (v_s0, "v_s0\n(100)", "#0284c7"),
        (v_a, "V_A (Corner)\n(195)", POS),
        (v_c, "V_C (Крейсер)\n(280)", "#16a34a"),
        (v_ne, "V_NE (Гранична)\n(350)", "#dc2626"),
        (v_d, "V_D (Пікір.)\n(400)", "#7c3aed")
    ]

    for sp_val, sp_lbl, sp_col in speeds:
        px = ox + sp_val * scale_x
        body.append(line(px, oy, px, oy + 70, color=sp_col, sw=1.0, dash="3 3"))
        body.append(circle(px, oy, 3.5, fill=sp_col, stroke=INK, sw=1.0))
        body.append(mtext(px, oy + 92, sp_lbl.split("\n"), size=10, color=sp_col, bold=True))

    # Особлива точка: V_A (Corner Speed)
    va_px = ox + v_a * scale_x
    va_py = oy - n_max_pos * scale_y
    body.append(circle(va_px, va_py, 6.0, fill=POS, stroke=INK, sw=2.0))
    tb_va, _, _ = textbox(va_px - 85, va_py - 45, "Швидкість маневрування V_A:\nПеретин C_L,max та n_max.\nБезпечне повне взяття керма!", size=10, fill="#fef2f2", stroke=POS, sw=1.2)
    body.append(tb_va)

    # Розміщення текстового блоку правил всередині вільного простору конверта
    tb_exp, _, _ = textbox(ox + 340, oy - 65, "Правила безпеки польотного конверта:\n• v < V_A: аеродинамічний зрив настає раніше за перевантаження n_max\n• v > V_A: різке взяття штурвала ламає лонжерон до настання зриву!\n• v > V_NE: небезпека флаттеру та руйнування обшивки динамічним напором", size=10, fill="#ffffff", stroke="#94a3b8", sw=1.2, min_w=280)
    body.append(tb_exp)

    render(os.path.join(OUT, 'vn-flight-envelope.svg'), W, H, *body)


if __name__ == '__main__':
    fig_wing_loading_spectrum()
    fig_turn_stall_dynamics()
    fig_wing_stall_progression()
    fig_vn_flight_envelope()
    print("All figures generated successfully.")
