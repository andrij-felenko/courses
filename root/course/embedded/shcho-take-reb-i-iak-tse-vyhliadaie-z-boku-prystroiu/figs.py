# -*- coding: utf-8 -*-
"""Фігури до теми «Що таке РЕБ і як це виглядає з боку пристрою».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math

# scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Види РЕБ: загороджувальне, прицільне, ковзне та імпульсне глушіння ───
def fig_reb_taxonomies():
    W, H = 840, 430
    f = []

    col_w = 186
    gap = 14
    start_x = 24
    top_y = 25
    card_h = 380

    types = [
        {
            "title": "Прицільне (Spot)",
            "sub": "Вся енергія в один канал",
            "fill": "#fdecea",
            "stroke": POS,
            "badge_bg": "#f8d7da",
            "desc": "Концентрація потужності\nв смузі каналу (100–500 кГц).\nГігантське J/S, випалює\nодин фіксований лінк.",
            "mode": "spot"
        },
        {
            "title": "Загороджувальне (Barrage)",
            "sub": "Шумова стіна на сотні МГц",
            "fill": "#fef5e7",
            "stroke": "#d35400",
            "badge_bg": "#fdebd0",
            "desc": "Розмиття енергії по смузі\n(100–500 МГц). Піднімає шум,\nзнижує SNR на всіх каналах,\nзасліплює сусідні приймачі.",
            "mode": "barrage"
        },
        {
            "title": "Ковзне (Sweep / Chirp)",
            "sub": "Швидкий біг по частоті",
            "fill": "#eaf2f8",
            "stroke": NEG,
            "badge_bg": "#d4e6f1",
            "desc": "Генератор циклічно сканує\nдіапазон за мікросекунди.\nРве пакети, збиває трекінг\nкореляторів і частотні петлі.",
            "mode": "sweep"
        },
        {
            "title": "Імпульсне (Pulse)",
            "sub": "Короткі удари кіловатами",
            "fill": "#f4ecf7",
            "stroke": "#8e44ad",
            "badge_bg": "#e8daef",
            "desc": "Потужні спалахи мікросекундної\nтривалості. Насичує LNA,\nвикликає переповнення АЦП\nі масові збої CRC.",
            "mode": "pulse"
        }
    ]

    for i, t in enumerate(types):
        cx = start_x + i * (col_w + gap)
        cy = top_y
        f.append(rect(cx, cy, col_w, card_h, fill=t["fill"], stroke=t["stroke"], sw=1.8, rx=8))
        
        f.append(fitbox(cx + 8, cy + 10, col_w - 16, 28, t["title"], size=13, fill=t["badge_bg"], stroke=t["stroke"], color=t["stroke"], bold=True))
        f.append(text(cx + col_w / 2, cy + 54, t["sub"], 11, MUTED, "middle", italic=True))

        mx = cx + 12
        my = cy + 70
        mw = col_w - 24
        mh = 145
        f.append(rect(mx, my, mw, mh, fill="#ffffff", stroke="#bdc3c7", sw=1.0, rx=4))

        # Mini-axes
        f.append(line(mx + 8, my + mh - 14, mx + mw - 8, my + mh - 14, color=MUTED, sw=1.0))
        f.append(line(mx + 12, my + mh - 8, mx + 12, my + 10, color=MUTED, sw=1.0))

        if t["mode"] == "spot":
            # Noise floor
            f.append(line(mx + 12, my + mh - 25, mx + mw - 8, my + mh - 25, color=MUTED, sw=1.0, dash="2 2"))
            # High sharp peak
            f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f8d7da" stroke="%s" stroke-width="2.2"/>' %
                     (mx + 45, my + mh - 25, mx + 55, my + 24, mx + 65, my + 24, mx + 75, my + mh - 25, POS))
            f.append(text(mx + 60, my + 18, "Завада", 10, POS, "middle", bold=True))
            # Desired signal buried
            f.append('<rect x="%.1f" y="%.1f" width="14" height="20" fill="#d4efdf" stroke="%s" stroke-width="1.2"/>' %
                     (mx + 53, my + mh - 45, FIELD))
            f.append(text(mx + mw / 2, my + mh - 4, "Частота f", 10, MUTED, "middle"))

        elif t["mode"] == "barrage":
            # High broadband noise plateau
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="52" fill="#fdebd0" stroke="#d35400" stroke-width="1.8"/>' %
                     (mx + 18, my + 45, mw - 28))
            f.append(text(mx + mw / 2, my + 38, "Шумовий рівень", 10, "#d35400", "middle", bold=True))
            # Desired signal drowned
            f.append('<rect x="%.1f" y="%.1f" width="18" height="28" fill="#d4efdf" stroke="%s" stroke-width="1.2"/>' %
                     (mx + 45, my + 68, FIELD))
            f.append(text(mx + mw / 2, my + mh - 4, "Широка смуга ΔF", 10, MUTED, "middle"))

        elif t["mode"] == "sweep":
            f.append(line(mx + 20, my + mh - 25, mx + mw - 20, my + 25, color=NEG, sw=2.5))
            f.append(arrow(mx + mw - 28, my + 35, mx + mw - 20, my + 25, color=NEG, sw=2.5))
            f.append(line(mx + 30, my + mh - 20, mx + mw - 10, my + 30, color=NEG, sw=1.5, dash="3 3"))
            f.append(text(mx + mw / 2, my + 22, "f(t) = f₀ + k·t", 10, NEG, "middle", bold=True))
            f.append(text(mx + mw / 2, my + mh - 4, "Час t → Частота", 10, MUTED, "middle"))

        elif t["mode"] == "pulse":
            for p_x in [mx + 25, mx + 58, mx + 91]:
                f.append('<rect x="%.1f" y="%.1f" width="16" height="75" fill="#e8daef" stroke="#8e44ad" stroke-width="1.8"/>' %
                         (p_x, my + 35))
            f.append(text(mx + mw / 2, my + 25, "Імпульси P_peak", 10, "#8e44ad", "middle", bold=True))
            f.append(text(mx + mw / 2, my + mh - 4, "Час t (сплески)", 10, MUTED, "middle"))

        f.append(fitbox(cx + 8, cy + 230, col_w - 16, 135, t["desc"], size=11, fill=t["fill"], stroke=t["stroke"], color=INK))

    render(os.path.join(IMG, "reb-taxonomies.svg"), W, H, *f,
           title="Види радіоелектронного придушення")


# ── 2. Насичення LNA: компресія 1 дБ та блокування вхідного каскаду ─────────
def fig_lna_saturation():
    W, H = 820, 440
    f = []

    ox, oy = 80, 360
    gw, gh = 410, 280

    # Axes
    f.append(line(ox, oy, ox + gw + 20, oy, color=MUTED, sw=1.4))
    f.append(arrow(ox + gw + 10, oy, ox + gw + 24, oy, color=MUTED, sw=1.4))
    f.append(text(ox + gw + 30, oy + 4, "P_in (дБм)", 12, INK, "start", bold=True))

    f.append(line(ox, oy, ox, oy - gh - 20, color=MUTED, sw=1.4))
    f.append(arrow(ox, oy - gh - 10, ox, oy - gh - 24, color=MUTED, sw=1.4))
    f.append(text(ox - 10, oy - gh - 15, "P_out (дБм)", 12, INK, "end", bold=True))

    # Grid ticks and labels
    pins = [(-90, 0.1), (-70, 0.3), (-50, 0.5), (-30, 0.7), (-10, 0.9)]
    for dbm, frac in pins:
        x = ox + frac * gw
        f.append(line(x, oy, x, oy + 5, color=MUTED, sw=1.0))
        f.append(text(x, oy + 18, "%d" % dbm, 10, MUTED, "middle"))
        f.append(line(x, oy, x, oy - gh, color="#f0f2f5", sw=1.0, dash="3 3"))

    # Ideal linear response (slope = 1)
    f.append(line(ox + 0.05 * gw, oy - 0.05 * gh, ox + 0.78 * gw, oy - 0.78 * gh, color="#95a5a6", sw=1.6, dash="5 4"))
    f.append(text(ox + 0.38 * gw, oy - 0.52 * gh, "Лінійний підсилювач G₀", 10.5, "#7f8c8d", "start", italic=True))

    # Actual non-linear curve with 1dB compression and saturation
    pts = [
        (ox + 0.05 * gw, oy - 0.05 * gh),
        (ox + 0.30 * gw, oy - 0.30 * gh),
        (ox + 0.50 * gw, oy - 0.50 * gh),
        (ox + 0.65 * gw, oy - 0.63 * gh),  # P1dB point
        (ox + 0.75 * gw, oy - 0.69 * gh),
        (ox + 0.88 * gw, oy - 0.72 * gh),  # Hard saturation Psat
        (ox + 0.98 * gw, oy - 0.725 * gh)
    ]
    path_d = "M %.1f,%.1f" % pts[0]
    for p in pts[1:]:
        path_d += " L %.1f,%.1f" % p
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path_d, POS))

    # P_1dB marker
    p1x = ox + 0.65 * gw
    p1y_act = oy - 0.63 * gh
    p1y_id = oy - 0.65 * gh

    f.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="#ffffff" stroke-width="1.5"/>' % (p1x, p1y_act, POS))
    # 1 dB delta indicator
    f.append(line(p1x, p1y_id, p1x, p1y_act, color=POS, sw=1.8))
    f.append(text(p1x + 8, (p1y_id + p1y_act) / 2 + 4, "Δ = 1 дБ", 10.5, POS, "start", bold=True))

    # P1dB callout
    f.append(line(p1x, p1y_act, p1x, oy, color=POS, sw=1.2, dash="3 3"))
    f.append(text(p1x, oy + 32, "P_1dB (вхідна)", 11, POS, "middle", bold=True))

    # Psat horizontal line
    psat_y = oy - 0.725 * gh
    f.append(line(ox, psat_y, ox + 0.98 * gw, psat_y, color="#c0392b", sw=1.2, dash="4 4"))
    f.append(text(ox - 10, psat_y + 4, "P_sat", 11, POS, "end", bold=True))

    # Explanation boxes on the right (x = 525)
    bx = 525
    by = 35
    f.append(fitbox(bx, by, 270, 110,
                    "Лінійна зона:\nP_out = P_in + G₀\nПідсилювач зберігає\nформу сигналу та SNR.",
                    size=11, fill="#eafaf1", stroke=FIELD, color=INK))

    f.append(fitbox(bx, by + 125, 270, 115,
                    "Точка компресії 1 дБ:\nКоефіцієнт підсилення\nпадає на 1 дБ (G = G₀ - 1).\nПочаток жорсткої\nнелінійності транзисторів.",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    f.append(fitbox(bx, by + 255, 270, 115,
                    "Насичення (P_sat) і блокування:\nLNA не реагує на корисний\nсигнал. Зниження підсилення\n(gain compression) засліплює\nвесь радіотракт.",
                    size=11, fill="#fef5e7", stroke="#d35400", color=INK))

    render(os.path.join(IMG, "lna-saturation-curve.svg"), W, H, *f,
           title="Характеристика компресії та насичення LNA")


# ── 3. Інтермодуляційні спотворення третього порядку (IP3) ─────────────────
def fig_intermodulation_ip3():
    W, H = 780, 400
    f = []

    ox, oy = 70, 310
    gw, gh = 640, 230

    f.append(line(ox, oy, ox + gw + 20, oy, color=MUTED, sw=1.4))
    f.append(arrow(ox + gw + 10, oy, ox + gw + 24, oy, color=MUTED, sw=1.4))
    f.append(text(ox + gw + 30, oy + 4, "Частота f", 12, INK, "start", bold=True))

    f.append(line(ox, oy, ox, oy - gh - 20, color=MUTED, sw=1.4))
    f.append(arrow(ox, oy - gh - 10, ox, oy - gh - 24, color=MUTED, sw=1.4))
    f.append(text(ox - 8, oy - gh - 15, "Рівень спектра (дБм)", 11.5, INK, "end", bold=True))

    nf_y = oy - 25
    f.append(line(ox, nf_y, ox + gw, nf_y, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(ox + 8, nf_y - 6, "Шумовий рівень", 10.5, MUTED, "start"))

    f1_x = ox + 0.46 * gw
    f2_x = ox + 0.62 * gw
    delta = f2_x - f1_x

    # f1 Jammer
    f.append('<rect x="%.1f" y="%.1f" width="22" height="175" rx="3" fill="#fdecea" stroke="%s" stroke-width="2.2"/>' %
             (f1_x - 11, oy - 200, POS))
    f.append(text(f1_x, oy - 208, "Завада f₁", 11.5, POS, "middle", bold=True))
    f.append(text(f1_x, oy + 18, "f₁", 11, INK, "middle", bold=True))

    # f2 Jammer
    f.append('<rect x="%.1f" y="%.1f" width="22" height="175" rx="3" fill="#fdecea" stroke="%s" stroke-width="2.2"/>' %
             (f2_x - 11, oy - 200, POS))
    f.append(text(f2_x, oy - 208, "Завада f₂", 11.5, POS, "middle", bold=True))
    f.append(text(f2_x, oy + 18, "f₂", 11, INK, "middle", bold=True))

    # Spacing delta annotation between f1 and f2
    f.append(line(f1_x, oy - 120, f2_x, oy - 120, color=MUTED, sw=1.2))
    f.append(arrow(f1_x + 12, oy - 120, f1_x, oy - 120, color=MUTED, sw=1.2))
    f.append(arrow(f2_x - 12, oy - 120, f2_x, oy - 120, color=MUTED, sw=1.2))
    f.append(text((f1_x + f2_x) / 2, oy - 126, "Δf = f₂ - f₁", 10.5, MUTED, "middle"))

    # IMD3 products at (2*f1 - f2) and (2*f2 - f1)
    im3_left_x = f1_x - delta
    im3_right_x = f2_x + delta

    # Left IM3 product (hits our desired channel f0!)
    f.append('<rect x="%.1f" y="%.1f" width="20" height="95" rx="3" fill="#fef5e7" stroke="#d35400" stroke-width="2.0"/>' %
             (im3_left_x - 10, oy - 120))
    f.append(text(im3_left_x, oy - 128, "IMD3: 2f₁ - f₂", 11, "#d35400", "middle", bold=True))
    f.append(text(im3_left_x, oy + 18, "f₀ (канал прийому)", 11, FIELD, "middle", bold=True))

    # Desired signal at f0 (buried beneath IMD3)
    f.append('<rect x="%.1f" y="%.1f" width="14" height="40" rx="2" fill="#d4efdf" stroke="%s" stroke-width="1.5"/>' %
             (im3_left_x - 7, oy - 65, FIELD))
    f.append(text(im3_left_x - 48, oy - 50, "Корисний\nсигнал", 10, FIELD, "middle"))
    f.append(arrow(im3_left_x - 22, oy - 48, im3_left_x - 8, oy - 48, color=FIELD, sw=1.2))

    # Right IM3 product
    f.append('<rect x="%.1f" y="%.1f" width="20" height="95" rx="3" fill="#fef5e7" stroke="#d35400" stroke-width="2.0"/>' %
             (im3_right_x - 10, oy - 120))
    f.append(text(im3_right_x, oy - 128, "IMD3: 2f₂ - f₁", 10.5, "#d35400", "middle", bold=True))
    f.append(text(im3_right_x, oy + 18, "2f₂ - f₁", 10.5, MUTED, "middle"))

    # Summary box
    f.append(fitbox(ox + 10, 25, 300, 85,
                    "Нелінійність третього порядку y(t) = a₁x + a₂x² + a₃x³:\n"
                    "Дві потужні завади поза робочим каналом\n"
                    "породжують комбінаційну частоту 2f₁ - f₂,\n"
                    "яка потрапляє прямо в робочу смугу f₀!",
                    size=10.5, fill="#fdfefe", stroke=LINE, color=INK))

    render(os.path.join(IMG, "intermodulation-ip3.svg"), W, H, *f,
           title="Інтермодуляційні спотворення третього порядку IP3")


# ── 4. Спуфінг GNSS: справжнє сузір'я проти фейкового генератора ───────────
def fig_gnss_spoofing():
    W, H = 820, 400
    f = []

    half_w = 370
    card_h = 340
    top_y = 35

    # Left: Authentic GNSS
    lx = 25
    f.append(rect(lx, top_y, half_w, card_h, fill="#f4fbf7", stroke=FIELD, sw=1.8, rx=8))
    f.append(fitbox(lx + 10, top_y + 12, half_w - 20, 30, "Справжній GNSS (Космічний простір)", size=13, fill="#d4efdf", stroke=FIELD, color=FIELD, bold=True))

    auth_rows = [
        ("Супутник PRN 03", "38 дБ-Гц", "+1.8 кГц", "Кут 42°", "#27ae60"),
        ("Супутник PRN 12", "44 дБ-Гц", "-2.4 кГц", "Кут 68°", "#27ae60"),
        ("Супутник PRN 21", "34 дБ-Гц", "+3.1 кГц", "Кут 18°", "#27ae60"),
        ("Супутник PRN 28", "41 дБ-Гц", "-0.7 кГц", "Кут 55°", "#27ae60"),
        ("Супутник PRN 31", "31 дБ-Гц", "+4.2 кГц", "Кут 12°", "#27ae60")
    ]

    for idx, (sat, cnr, dop, el, col) in enumerate(auth_rows):
        ry = top_y + 60 + idx * 36
        f.append(rect(lx + 15, ry, half_w - 30, 30, fill="#ffffff", stroke="#a9dfbf", sw=1.0, rx=4))
        f.append(text(lx + 25, ry + 19, sat, 11, INK, "start", bold=True))
        f.append(text(lx + 150, ry + 19, cnr, 11, col, "start", bold=True))
        f.append(text(lx + 230, ry + 19, dop, 10.5, MUTED, "start"))
        f.append(text(lx + 310, ry + 19, el, 10.5, MUTED, "start"))

    f.append(fitbox(lx + 15, top_y + 250, half_w - 30, 75,
                    "Фізичні маркери автентичності:\n"
                    "• CNR у діапазоні 30–45 дБ-Гц (залежно від висоти);\n"
                    "• Різні доплерівські зсуви через власний рух супутників;\n"
                    "• Відповідність фазового центру діаграмі спрямованості.",
                    size=10.5, fill="#e8f8f5", stroke=FIELD, color=INK))

    # Right: Spoofed GNSS
    rx = 425
    f.append(rect(rx, top_y, half_w, card_h, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(fitbox(rx + 10, top_y + 12, half_w - 20, 30, "Штучний Спуфінг (Наземний SDR-випромінювач)", size=13, fill="#f8d7da", stroke=POS, color=POS, bold=True))

    spk_rows = [
        ("Фейковий PRN 03", "54 дБ-Гц", "+0.1 кГц", "Кут 42°", POS),
        ("Фейковий PRN 12", "54 дБ-Гц", "+0.1 кГц", "Кут 68°", POS),
        ("Фейковий PRN 21", "55 дБ-Гц", "+0.1 кГц", "Кут 18°", POS),
        ("Фейковий PRN 28", "54 дБ-Гц", "+0.1 кГц", "Кут 55°", POS),
        ("Фейковий PRN 31", "54 дБ-Гц", "+0.1 кГц", "Кут 12°", POS)
    ]

    for idx, (sat, cnr, dop, el, col) in enumerate(spk_rows):
        ry = top_y + 60 + idx * 36
        f.append(rect(rx + 15, ry, half_w - 30, 30, fill="#ffffff", stroke="#f5b7b1", sw=1.0, rx=4))
        f.append(text(rx + 25, ry + 19, sat, 11, INK, "start", bold=True))
        f.append(text(rx + 150, ry + 19, cnr, 11, col, "start", bold=True))
        f.append(text(rx + 230, ry + 19, dop, 10.5, POS, "start"))
        f.append(text(rx + 310, ry + 19, el, 10.5, MUTED, "start"))

    f.append(fitbox(rx + 15, top_y + 250, half_w - 30, 75,
                    "Аномальні ознаки підміни (Spoofing):\n"
                    "• Неприродно високий CNR (> 50–55 дБ-Гц) для всіх супутників;\n"
                    "• Ідентичний рівень сигналу (випромінюються з однієї антени);\n"
                    "• Майже нульовий або однаковий Доплер на всіх каналах.",
                    size=10.5, fill="#fdf2e9", stroke=POS, color=INK))

    render(os.path.join(IMG, "gnss-spoofing-signature.svg"), W, H, *f,
           title="Телеметричний профіль супутникового спуфінгу")


# ── 5. Діагностична матриця внутрішньої телеметрії радіотракту ──────────────
def fig_telemetry_matrix():
    W, H = 820, 430
    f = []

    top_y = 30
    tbl_x = 25
    tbl_w = 770
    tbl_h = 370

    f.append(rect(tbl_x, top_y, tbl_w, tbl_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))

    cols = [
        ("Стан ефіру / загроза", 150),
        ("RSSI", 100),
        ("AGC Підсилення", 110),
        ("Синхронізація", 110),
        ("Помилки CRC", 110),
        ("Вердикт класифікатора", 190)
    ]

    cur_x = tbl_x
    f.append(rect(tbl_x, top_y, tbl_w, 36, fill="#2c3e50", stroke="#2c3e50", sw=1.0, rx=0))
    for name, cw in cols:
        f.append(text(cur_x + cw / 2, top_y + 22, name, 11, "#ffffff", "middle", bold=True))
        cur_x += cw

    rows = [
        {
            "state": "Чистий ефір (Норма)",
            "rssi": "Низький (-95 дБм)",
            "agc": "Максимальне",
            "sync": "100% захоплення",
            "crc": "0% втрат",
            "verdict": "LINK_OK: Штатна робота",
            "bg": "#eafaf1",
            "stroke": FIELD,
            "v_col": FIELD
        },
        {
            "state": "Природне згасання",
            "rssi": "Критично низький",
            "agc": "Максимальне",
            "sync": "Зриви синхро",
            "crc": "Помірні втрати",
            "verdict": "LINK_WEAK: Віддалення вузла",
            "bg": "#fcf3cf",
            "stroke": "#b7950b",
            "v_col": "#b7950b"
        },
        {
            "state": "Прицільний РЕБ",
            "rssi": "Високий (-50 дБм)",
            "agc": "Мінімальне",
            "sync": "0% (немає слів)",
            "crc": "100% відмов",
            "verdict": "JAMMING_SPOT: Зміна каналу",
            "bg": "#fdecea",
            "stroke": POS,
            "v_col": POS
        },
        {
            "state": "Загороджувальний РЕБ",
            "rssi": "Максимальний",
            "agc": "Мінімальне (0 дБ)",
            "sync": "Повна тиша",
            "crc": "100% відмов",
            "verdict": "JAMMING_BARRAGE: Блокування LNA",
            "bg": "#fadbd8",
            "stroke": "#922b21",
            "v_col": "#922b21"
        },
        {
            "state": "Імпульсна завада",
            "rssi": "Стрибки (-40↔-95)",
            "agc": "Коливання AGC",
            "sync": "Часткове",
            "crc": "Сплески CRC",
            "verdict": "JAMMING_PULSE: Короткі спалахи",
            "bg": "#f4ecf7",
            "stroke": "#8e44ad",
            "v_col": "#8e44ad"
        },
        {
            "state": "GNSS Спуфінг",
            "rssi": "CNR > 52 дБ-Гц",
            "agc": "Низьке (GNSS LNA)",
            "sync": "100% фейкових слів",
            "crc": "0% (валідна навігація)",
            "verdict": "GNSS_SPOOFING: Інерціальний перехід",
            "bg": "#fef5e7",
            "stroke": "#d35400",
            "v_col": "#d35400"
        }
    ]

    row_h = 52
    for r_idx, r in enumerate(rows):
        ry = top_y + 36 + r_idx * row_h
        f.append(rect(tbl_x, ry, tbl_w, row_h, fill=r["bg"], stroke="#e5e7eb", sw=1.0, rx=0))
        
        vals = [r["state"], r["rssi"], r["agc"], r["sync"], r["crc"], r["verdict"]]
        cx = tbl_x
        for v_idx, (v, (col_name, cw)) in enumerate(zip(vals, cols)):
            bold_flag = (v_idx == 0 or v_idx == 5)
            text_color = r["v_col"] if v_idx == 5 else (POS if (v_idx == 0 and "РЕБ" in v) else INK)
            f.append(fitbox(cx + 4, ry + 4, cw - 8, row_h - 8, v, size=10, fill=r["bg"], stroke=r["bg"], color=text_color, bold=bold_flag))
            cx += cw

    render(os.path.join(IMG, "telemetry-ew-matrix.svg"), W, H, *f,
           title="Діагностична матриця телеметрії радіотракту")


if __name__ == "__main__":
    fig_reb_taxonomies()
    fig_lna_saturation()
    fig_intermodulation_ip3()
    fig_gnss_spoofing()
    fig_telemetry_matrix()
    print("Всі SVG фігури успішно згенеровано.")
