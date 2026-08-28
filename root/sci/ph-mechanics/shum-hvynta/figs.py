# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def my_ellipse(cx, cy, rx, ry, fill='none', stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"/>' %
            (cx, cy, rx, ry, fill, stroke, sw))

# ═══════════════════════════════════════════════════════════════════════════
# Фігура 1 — Спектральний склад шуму повітряного гвинта
# ═══════════════════════════════════════════════════════════════════════════
def gen_noise_spectrum():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 28, 'Акустичний спектр повітряного гвинта: тональні піки та широкосмуговий шум',
                  15, INK, 'middle', bold=True))

    ox, oy = 80, 310
    pw, ph = 620, 240

    # Сітка та осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.5))
    f.append(text(ox + pw - 10, oy + 32, 'Частота f (Гц, логарифмічна шкала) →', 12, INK, 'end', bold=True))
    f.append(text(ox - 45, oy - ph + 20, 'SPL (дБ)', 12, INK, 'middle', bold=True))

    # Горизонтальні лінії сітки
    for i, spl in enumerate([30, 50, 70, 90]):
        y = oy - (i + 1) * (ph / 4.5)
        f.append(line(ox, y, ox + pw, y, color='#e5e7eb', sw=1, dash='4,4'))
        f.append(text(ox - 10, y + 4, str(spl), 10, MUTED, 'end'))

    # Широкосмуговий п'єдестал (Broadband noise)
    pts_bb = []
    for px in range(0, int(pw) + 1, 5):
        norm_x = px / pw
        bb_val = 38 + 24 * math.exp(-((norm_x - 0.52) ** 2) / 0.06) - 15 * norm_x
        fluct = 1.8 * math.sin(px * 0.4) + 1.2 * math.cos(px * 0.85)
        y = oy - (bb_val + fluct) * (ph / 95)
        pts_bb.append((ox + px, y))

    d_bb = 'M ' + ' L '.join('%.1f %.1f' % (pt[0], pt[1]) for pt in pts_bb)
    d_area = d_bb + (' L %.1f %.1f L %.1f %.1f Z' % (ox + pw, oy, ox, oy))
    f.append('<path d="%s" fill="#eff6ff" stroke="none"/>' % d_area)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_bb, NEG))

    # Тональні гармоніки (BPF, 2*BPF, 3*BPF, 4*BPF, 5*BPF)
    harmonics = [
        (0.18, 88, '1×BPF', 'основний тон'),
        (0.29, 78, '2×BPF', '2-а гармоніка'),
        (0.38, 70, '3×BPF', '3-я гармоніка'),
        (0.46, 62, '4×BPF', '4-а гармоніка'),
        (0.53, 54, '5×BPF', '5-а гармоніка')
    ]

    for rel_x, spl, label, desc in harmonics:
        hx = ox + rel_x * pw
        hy = oy - spl * (ph / 95)
        f.append(line(hx, oy, hx, hy, color=POS, sw=3))
        f.append(circle(hx, hy, 4, fill=POS, stroke=BG, sw=1.5))
        f.append(text(hx, hy - 8, label, 11, POS, 'middle', bold=True))

    # Підписи зон спектра
    f.append(rect(100, 52, 230, 48, fill='#fef2f2', stroke=POS, sw=1, rx=4))
    f.append(text(215, 69, 'Тональний шум (дискретний)', 11, POS, 'middle', bold=True))
    f.append(text(215, 87, 'BPF = B · n (гармоніки Гутіна)', 10, INK, 'middle'))

    f.append(rect(460, 52, 270, 62, fill='#eff6ff', stroke=NEG, sw=1, rx=4))
    f.append(text(595, 68, 'Широкосмуговий шум (стохастичний)', 11, NEG, 'middle', bold=True))
    f.append(text(595, 84, '• Схід примежового шару з кромки', 9.5, INK, 'middle'))
    f.append(text(595, 99, '• Вихори на кінцях лопатей (Tip Vortex)', 9.5, INK, 'middle'))

    render(os.path.join(IMG, 'noise-spectrum-bpf.svg'), W, H, "".join(f))


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 2 — Фізичні джерела звуку за рівнянням FW-H
# ═══════════════════════════════════════════════════════════════════════════
def gen_acoustic_sources():
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 26, 'Три типи акустичних джерел обертової лопаті (FW-H)',
                  15, INK, 'middle', bold=True))

    col_w = 226
    col_gap = 18
    col_h = 245
    top_y = 50

    # 1. Монополь: шум товщини
    x1 = 20
    f.append(rect(x1, top_y, col_w, col_h, fill='#fdf8f6', stroke='#ea580c', sw=1.5, rx=6))
    f.append(text(x1 + col_w / 2, top_y + 24, '1. Монополь (Товщина)', 13, '#ea580c', 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 40, 'Thickness Noise (розсування об\'єму)', 10, MUTED, 'middle'))

    cx1, cy1 = x1 + col_w / 2, top_y + 105
    for r_i in [20, 36, 52]:
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#ea580c" stroke-width="1" stroke-dasharray="3,3"/>' % (cx1, cy1, r_i))
    f.append(rect(cx1 - 25, cy1 - 8, 50, 16, fill='#fed7aa', stroke='#ea580c', sw=1.5, rx=8))
    f.append(text(cx1, cy1 + 4, 'Лопать', 10, INK, 'middle', bold=True))
    f.append(arrow(cx1, cy1 - 12, cx1, cy1 - 32, color='#ea580c', sw=1.5))
    f.append(arrow(cx1, cy1 + 12, cx1, cy1 + 32, color='#ea580c', sw=1.5))

    f.append(text(x1 + col_w / 2, top_y + 175, 'Джерело: витіснення маси q', 10.5, INK, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 193, 'Акустичний тиск: p ~ ρ · ů', 10, INK, 'middle'))
    f.append(text(x1 + col_w / 2, top_y + 210, 'Акустична потужність: W ~ M⁴', 10, INK, 'middle'))
    f.append(text(x1 + col_w / 2, top_y + 228, 'Домінує в площині обертання', 10, '#ea580c', 'middle', bold=True))

    # 2. Диполь: шум навантаження
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, top_y, col_w, col_h, fill='#fef2f2', stroke=POS, sw=1.5, rx=6))
    f.append(text(x2 + col_w / 2, top_y + 24, '2. Диполь (Навантаження)', 13, POS, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 40, 'Loading Noise (сили тяги й опору)', 10, MUTED, 'middle'))

    cx2, cy2 = x2 + col_w / 2, top_y + 105
    f.append('<circle cx="%.1f" cy="%.1f" r="26" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx2, cy2 - 22, POS))
    f.append('<circle cx="%.1f" cy="%.1f" r="26" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx2, cy2 + 22, NEG))
    f.append(rect(cx2 - 25, cy2 - 6, 50, 12, fill='#fecaca', stroke=POS, sw=1.5, rx=4))
    f.append(arrow(cx2, cy2 - 8, cx2, cy2 - 38, color=POS, sw=2))
    f.append(text(cx2 + 20, cy2 - 24, '+F (тяга)', 9.5, POS, 'start', bold=True))

    f.append(text(x2 + col_w / 2, top_y + 175, 'Джерело: коливання сили F', 10.5, INK, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 193, 'Акустичний тиск: p ~ Ḟ / c₀', 10, INK, 'middle'))
    f.append(text(x2 + col_w / 2, top_y + 210, 'Акустична потужність: W ~ M⁶', 10, INK, 'middle'))
    f.append(text(x2 + col_w / 2, top_y + 228, 'Головний шум для дронів (M < 0.6)', 10, POS, 'middle', bold=True))

    # 3. Квадруполь: шум турбулентного сліду
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, top_y, col_w, col_h, fill='#f8fafc', stroke='#475569', sw=1.5, rx=6))
    f.append(text(x3 + col_w / 2, top_y + 24, '3. Квадруполь (Стисливість)', 13, '#475569', 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 40, 'Quadrupole Noise (напруження Tij)', 10, MUTED, 'middle'))

    cx3, cy3 = x3 + col_w / 2, top_y + 105
    f.append(circle(cx3 - 16, cy3 - 16, 14, fill='#e2e8f0', stroke='#64748b', sw=1))
    f.append(circle(cx3 + 16, cy3 - 16, 14, fill='#cbd5e1', stroke='#64748b', sw=1))
    f.append(circle(cx3 - 16, cy3 + 16, 14, fill='#cbd5e1', stroke='#64748b', sw=1))
    f.append(circle(cx3 + 16, cy3 + 16, 14, fill='#e2e8f0', stroke='#64748b', sw=1))
    f.append(text(cx3, cy3 + 4, 'Tij', 11, '#334155', 'middle', bold=True))

    f.append(text(x3 + col_w / 2, top_y + 175, 'Джерело: вихори й напруження', 10.5, INK, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 193, 'Акустичний тиск: p ~ ∂²Tij / c₀²', 10, INK, 'middle'))
    f.append(text(x3 + col_w / 2, top_y + 210, 'Акустична потужність: W ~ M⁸', 10, INK, 'middle'))
    f.append(text(x3 + col_w / 2, top_y + 228, 'Важливий лише при M > 0.8', 10, '#475569', 'middle', bold=True))

    render(os.path.join(IMG, 'acoustic-sources-fwh.svg'), W, H, "".join(f))


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 3 — Діаграма спрямованості акустичного тиску формули Гутіна
# ═══════════════════════════════════════════════════════════════════════════
def gen_gutin_directivity():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 26, 'Діаграма спрямованості шуму гвинта (формула Гутіна)',
                  15, INK, 'middle', bold=True))

    cx, cy = 310, 190
    max_r = 130

    for r_norm in [0.25, 0.5, 0.75, 1.0]:
        r_px = r_norm * max_r
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="2,2"/>' % (cx, cy, r_px))

    f.append(line(cx, cy - max_r - 20, cx, cy + max_r + 20, color=INK, sw=1.5))
    f.append(line(cx - max_r - 25, cy, cx + max_r + 25, cy, color=INK, sw=1.5))

    f.append(arrow(cx, cy - 10, cx, cy - 80, color=POS, sw=2.5))
    f.append(text(cx + 8, cy - 50, 'Вектор тяги T (θ = 0°)', 10.5, POS, 'start', bold=True))

    f.append(rect(cx - 35, cy - 4, 70, 8, fill='#cbd5e1', stroke=INK, sw=1.5, rx=3))
    f.append(text(cx + max_r + 30, cy + 4, 'Площина обертання (θ = 90°)', 10, MUTED, 'start'))
    f.append(text(cx, cy + max_r + 28, 'Слід за гвинтом (θ = 180°)', 10, MUTED, 'middle'))

    pts_direct = []
    n_pts = 180
    for i in range(n_pts + 1):
        angle_rad = i * (2 * math.pi / n_pts)
        theta = angle_rad
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        val = abs(-cos_t * 0.85 + 0.35) * (abs(sin_t) ** 1.3)
        r_val = val * max_r * 1.05
        px = cx + r_val * math.sin(angle_rad)
        py = cy - r_val * math.cos(angle_rad)
        pts_direct.append((px, py))

    d_dir = 'M ' + ' L '.join('%.1f %.1f' % (pt[0], pt[1]) for pt in pts_direct) + ' Z'
    f.append('<path d="%s" fill="#fee2e2" stroke="%s" stroke-width="2.2"/>' % (d_dir, POS))

    peak_angle = math.radians(115)
    pk_r = max_r * 0.95
    pk_x = cx + pk_r * math.sin(peak_angle)
    pk_y = cy - pk_r * math.cos(peak_angle)
    f.append(circle(pk_x, pk_y, 4, fill=POS, stroke=BG, sw=1.5))
    f.append(line(pk_x, pk_y, pk_x + 35, pk_y + 15, color=POS, sw=1.2))
    f.append(text(pk_x + 40, pk_y + 20, 'Максимум шуму: θ ≈ 105°–120°', 11, POS, 'start', bold=True))

    lx = 500
    f.append(rect(lx, 70, 240, 210, fill='#f8fafc', stroke='#cbd5e1', sw=1.2, rx=6))
    f.append(text(lx + 120, 92, 'Фізика спрямованості', 12, INK, 'middle', bold=True))
    f.append(text(lx + 12, 118, '• На осі (θ = 0°, 180°):', 10.5, INK, 'start', bold=True))
    f.append(text(lx + 20, 134, 'J_mB(0) = 0 → шум зникає', 10, MUTED, 'start'))
    f.append(text(lx + 12, 158, '• У площині (θ = 90°):', 10.5, INK, 'start', bold=True))
    f.append(text(lx + 20, 174, 'диполь тяги зникає (cos θ = 0)', 10, MUTED, 'start'))
    f.append(text(lx + 20, 189, 'лишається крутний момент', 10, MUTED, 'start'))
    f.append(text(lx + 12, 213, '• За диском (θ = 105°–120°):', 10.5, POS, 'start', bold=True))
    f.append(text(lx + 20, 229, 'конструктивна інтерференція', 10, POS, 'start'))
    f.append(text(lx + 20, 244, 'тяги й моменту → головний пік', 10, POS, 'start'))

    render(os.path.join(IMG, 'gutin-directivity.svg'), W, H, "".join(f))


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 4 — Механізми широкосмугового шуму (Broadband Noise)
# ═══════════════════════════════════════════════════════════════════════════
def gen_broadband_mechanisms():
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 26, 'Три механізми генерації широкосмугового шуму',
                  15, INK, 'middle', bold=True))

    col_w = 226
    col_gap = 18
    col_h = 245
    top_y = 50

    # 1. Шум задньої кромки (TBL-TE)
    x1 = 20
    f.append(rect(x1, top_y, col_w, col_h, fill='#f0fdf4', stroke=FIELD, sw=1.5, rx=6))
    f.append(text(x1 + col_w / 2, top_y + 24, '1. Схід із задньої кромки', 12.5, FIELD, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 40, 'Trailing Edge Noise (TBL-TE)', 10, MUTED, 'middle'))

    cx1, cy1 = x1 + col_w / 2, top_y + 105
    d_prof = 'M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d Z' % (
        cx1 - 70, cy1,
        cx1 - 50, cy1 - 20, cx1 + 20, cy1 - 18, cx1 + 45, cy1,
        cx1 + 20, cy1 + 8, cx1 - 50, cy1 + 10, cx1 - 70, cy1
    )
    f.append('<path d="%s" fill="#dcfce7" stroke="%s" stroke-width="1.5"/>' % (d_prof, FIELD))
    for vx, vy, vr in [(cx1 + 52, cy1 - 5, 4), (cx1 + 62, cy1 + 2, 5), (cx1 + 74, cy1 - 2, 6)]:
        f.append(circle(vx, vy, vr, fill='none', stroke=POS, sw=1.2))
    for rad in [14, 24, 34]:
        f.append('<path d="M %d %d A %d %d 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2,2"/>' % (
            cx1 + 45, cy1 - rad, rad, rad, cx1 + 45 + rad, cy1, FIELD
        ))

    f.append(text(x1 + col_w / 2, top_y + 170, 'Дифракція вихорів на кромці', 10.5, INK, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 188, 'Теорія Ффіліпс Вільямса — Голла', 9.5, INK, 'middle'))
    f.append(text(x1 + col_w / 2, top_y + 204, 'Інтенсивність: I ~ U⁵ · δ*', 10, FIELD, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 224, 'Створює неперервне шипіння', 9.5, MUTED, 'middle'))

    # 2. Шум кінцевого вихору (Tip Vortex)
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, top_y, col_w, col_h, fill='#eff6ff', stroke=NEG, sw=1.5, rx=6))
    f.append(text(x2 + col_w / 2, top_y + 24, '2. Вихори на кінцях', 12.5, NEG, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 40, 'Tip Vortex Shedding Noise', 10, MUTED, 'middle'))

    cx2, cy2 = x2 + col_w / 2, top_y + 105
    f.append(rect(cx2 - 60, cy2 - 12, 65, 24, fill='#dbeafe', stroke=NEG, sw=1.5, rx=4))
    f.append(text(cx2 - 30, cy2 + 4, 'Лопать', 10, INK, 'middle'))
    for i in range(4):
        sx = cx2 + 15 + i * 14
        sy = cy2
        rx_v, ry_v = 8 + i * 2, 16 + i * 2
        f.append(my_ellipse(sx, sy, rx_v, ry_v, fill='none', stroke=NEG, sw=1.4))
    f.append(arrow(cx2 - 15, cy2 + 18, cx2 + 10, cy2 - 18, color=POS, sw=1.5))
    f.append(text(cx2 + 2, cy2 + 30, 'перетік Δp', 9, POS, 'middle'))

    f.append(text(x2 + col_w / 2, top_y + 170, 'Перетік високого тиску на торець', 10.5, INK, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 188, 'Потужне вихорове ядро сліду', 9.5, INK, 'middle'))
    f.append(text(x2 + col_w / 2, top_y + 204, 'Пульсації тиску в ядрі вихору', 10, NEG, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 224, 'Високочастотний свист кінців', 9.5, MUTED, 'middle'))

    # 3. Взаємодія з вихором (BVI)
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, top_y, col_w, col_h, fill='#fef2f2', stroke=POS, sw=1.5, rx=6))
    f.append(text(x3 + col_w / 2, top_y + 24, '3. Взаємодія з вихором (BVI)', 12.5, POS, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 40, 'Blade-Vortex Interaction', 10, MUTED, 'middle'))

    cx3, cy3 = x3 + col_w / 2, top_y + 105
    f.append(rect(cx3 - 50, cy3 - 6, 60, 12, fill='#fecaca', stroke=POS, sw=1.5, rx=3))
    f.append(arrow(cx3 - 50, cy3, cx3 - 20, cy3, color=POS, sw=1.5))
    f.append(circle(cx3 + 30, cy3, 16, fill='#fed7aa', stroke='#ea580c', sw=1.5))
    f.append(text(cx3 + 30, cy3 + 4, 'Г', 12, '#ea580c', 'middle', bold=True))
    for wr in [24, 34, 44]:
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx3 + 30, cy3, wr, POS))

    f.append(text(x3 + col_w / 2, top_y + 170, 'Удар об вихор попередньої лопаті', 10.5, INK, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 188, 'Стрибок кута атаки Δα', 9.5, INK, 'middle'))
    f.append(text(x3 + col_w / 2, top_y + 204, 'Імпульсний сплеск тиску (ляскіт)', 10, POS, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 224, 'Типовий при спуску та маневрах', 9.5, MUTED, 'middle'))

    render(os.path.join(IMG, 'broadband-mechanisms.svg'), W, H, "".join(f))


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 5 — Методи акустичної оптимізації гвинтів
# ═══════════════════════════════════════════════════════════════════════════
def gen_acoustic_mitigation():
    W, H = 760, 330
    f = []
    f.append(text(W / 2, 26, 'Конструктивні методи зниження шуму гвинта',
                  15, INK, 'middle', bold=True))

    col_w = 168
    col_gap = 14
    col_h = 255
    top_y = 50

    # Метод 1: Зниження швидкості кінців (M_tip)
    x1 = 20
    f.append(rect(x1, top_y, col_w, col_h, fill='#f8fafc', stroke='#64748b', sw=1.5, rx=6))
    f.append(text(x1 + col_w / 2, top_y + 22, '1. Менша швидкість', 11.5, INK, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 37, 'M_tip < 0.5 (нижчі RPM)', 9.5, MUTED, 'middle'))

    cx1, cy1 = x1 + col_w / 2, top_y + 90
    f.append(circle(cx1, cy1, 32, fill='#f1f5f9', stroke='#94a3b8', sw=1))
    for ang in [0, 90, 180, 270]:
        rad = math.radians(ang)
        f.append(line(cx1, cy1, cx1 + 28 * math.cos(rad), cy1 + 28 * math.sin(rad), color='#475569', sw=2))
    f.append(circle(cx1, cy1, 5, fill='#334155', stroke=BG, sw=1))
    f.append(text(cx1, cy1 + 46, 'Багатолопатева схема', 9.5, INK, 'middle', bold=True))

    f.append(text(x1 + col_w / 2, top_y + 160, 'Тяга та сама:', 10, INK, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 176, 'більше лопатей B', 9.5, INK, 'middle'))
    f.append(text(x1 + col_w / 2, top_y + 192, 'менші оберти n', 9.5, INK, 'middle'))
    f.append(text(x1 + col_w / 2, top_y + 214, 'Шум навантаження ~ n⁶', 9.5, POS, 'middle', bold=True))
    f.append(text(x1 + col_w / 2, top_y + 232, 'Ефект: −4...−8 дБ', 10, FIELD, 'middle', bold=True))

    # Метод 2: Тороїдальний гвинт
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, top_y, col_w, col_h, fill='#eff6ff', stroke=NEG, sw=1.5, rx=6))
    f.append(text(x2 + col_w / 2, top_y + 22, '2. Тороїдальна петля', 11.5, NEG, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 37, 'Toroidal Propeller', 9.5, MUTED, 'middle'))

    cx2, cy2 = x2 + col_w / 2, top_y + 90
    f.append(my_ellipse(cx2 - 14, cy2, 14, 28, fill='none', stroke=NEG, sw=2.2))
    f.append(my_ellipse(cx2 + 14, cy2, 14, 28, fill='none', stroke=NEG, sw=2.2))
    f.append(circle(cx2, cy2, 5, fill=NEG, stroke=BG, sw=1))
    f.append(text(cx2, cy2 + 46, 'Замкнений контур кінця', 9.5, NEG, 'middle', bold=True))

    f.append(text(x2 + col_w / 2, top_y + 160, 'Немає відкритого торця:', 10, INK, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 176, 'вихідний вихор ділиться', 9.5, INK, 'middle'))
    f.append(text(x2 + col_w / 2, top_y + 192, 'спектр зміщується вгору', 9.5, INK, 'middle'))
    f.append(text(x2 + col_w / 2, top_y + 214, 'Швидке згасання в повітрі', 9.5, NEG, 'middle', bold=True))
    f.append(text(x2 + col_w / 2, top_y + 232, 'Ефект: −3...−6 dBA', 10, FIELD, 'middle', bold=True))

    # Метод 3: Пилкоподібна кромка (Serrations)
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, top_y, col_w, col_h, fill='#f0fdf4', stroke=FIELD, sw=1.5, rx=6))
    f.append(text(x3 + col_w / 2, top_y + 22, '3. Пилкоподібний край', 11.5, FIELD, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 37, 'Serrations (шеврони)', 9.5, MUTED, 'middle'))

    cx3, cy3 = x3 + col_w / 2, top_y + 90
    f.append(rect(cx3 - 28, cy3 - 20, 26, 40, fill='#dcfce7', stroke=FIELD, sw=1.5, rx=3))
    pts_serr = [(cx3 - 2, cy3 - 20)]
    for sy_i in range(-20, 21, 10):
        pts_serr.append((cx3 + 12, sy_i + 5))
        pts_serr.append((cx3 - 2, sy_i + 10))
    d_s = 'M ' + ' L '.join('%.1f %.1f' % (pt[0], pt[1]) for pt in pts_serr)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d_s, FIELD))
    f.append(text(cx3, cy3 + 46, 'Зубчаста задня кромка', 9.5, FIELD, 'middle', bold=True))

    f.append(text(x3 + col_w / 2, top_y + 160, 'Руйнування когерентності:', 10, INK, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 176, 'деструктивна інтерференція', 9.5, INK, 'middle'))
    f.append(text(x3 + col_w / 2, top_y + 192, 'вихорів сходу шару', 9.5, INK, 'middle'))
    f.append(text(x3 + col_w / 2, top_y + 214, 'Зниження дифракції хвилі', 9.5, FIELD, 'middle', bold=True))
    f.append(text(x3 + col_w / 2, top_y + 232, 'Ефект: −2...−4 дБ', 10, FIELD, 'middle', bold=True))

    # Метод 4: Стрілоподібність (Swept tip)
    x4 = x3 + col_w + col_gap
    f.append(rect(x4, top_y, col_w, col_h, fill='#fdf4ff', stroke='#a855f7', sw=1.5, rx=6))
    f.append(text(x4 + col_w / 2, top_y + 22, '4. Стрілоподібність', 11.5, '#a855f7', 'middle', bold=True))
    f.append(text(x4 + col_w / 2, top_y + 37, 'Swept Tip (шаблеподібність)', 9.5, MUTED, 'middle'))

    cx4, cy4 = x4 + col_w / 2, top_y + 90
    d_sw = 'M %d %d C %d %d %d %d %d %d C %d %d %d %d %d %d Z' % (
        cx4 - 15, cy4 + 25,
        cx4 - 10, cy4, cx4 - 5, cy4 - 15, cx4 + 22, cy4 - 28,
        cx4 + 10, cy4 - 12, cx4 + 2, cy4, cx4 + 5, cy4 + 25
    )
    f.append('<path d="%s" fill="#f3e8ff" stroke="#a855f7" stroke-width="1.8"/>' % d_sw)
    f.append(text(cx4, cy4 + 46, 'Скошений кінець лопаті', 9.5, '#a855f7', 'middle', bold=True))

    f.append(text(x4 + col_w / 2, top_y + 160, 'Зниження місцевого Mach:', 10, INK, 'middle', bold=True))
    f.append(text(x4 + col_w / 2, top_y + 176, 'M_eff = M · cos(Λ)', 9.5, INK, 'middle'))
    f.append(text(x4 + col_w / 2, top_y + 192, 'розмазування BPF фази', 9.5, INK, 'middle'))
    f.append(text(x4 + col_w / 2, top_y + 214, 'Менший градієнт тиску', 9.5, '#a855f7', 'middle', bold=True))
    f.append(text(x4 + col_w / 2, top_y + 232, 'Ефект: −2...−5 дБ', 10, FIELD, 'middle', bold=True))

    render(os.path.join(IMG, 'acoustic-mitigation.svg'), W, H, "".join(f))


if __name__ == '__main__':
    gen_noise_spectrum()
    gen_acoustic_sources()
    gen_gutin_directivity()
    gen_broadband_mechanisms()
    gen_acoustic_mitigation()
    print("Всі 5 фігур успішно згенеровано.")
