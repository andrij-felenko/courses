# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
AMBER   = "#d97706"
AMBERBG = "#fef3c7"
REDBG   = "#fee2e2"
GRNBG   = "#dcfce7"
BLUEBG  = "#dbeafe"
VIOLET  = "#7c3aed"
VIOLETBG= "#ede9fe"
CYAN    = "#0891b2"
CYANBG  = "#cffafe"


# ── 1. bh-loops-comparison: Петлі гістерезису твердого і м'якого матеріалів ───
def fig_bh_loops():
    W, H = 760, 380
    p = []
    
    # Центр координат
    cx, cy = 340, 190
    
    # Осі
    p.append(line(80, cy, 600, cy, color=LINE, sw=1.5))
    p.append(arrow(598, cy, 600, cy, color=LINE, sw=1.5))
    p.append(text(615, cy + 4, "H (А/м)", size=12, color=INK, anchor="start", bold=True))
    
    p.append(line(cx, 350, cx, 30, color=LINE, sw=1.5))
    p.append(arrow(cx, 32, cx, 30, color=LINE, sw=1.5))
    p.append(text(cx, 20, "B (Тл)", size=12, color=INK, anchor="middle", bold=True))
    
    # Широка петля (магнітно-твердий матеріал)
    # Формуємо замкнений шлях
    hard_path = (
        f"M {cx-180} {cy} "
        f"C {cx-180} {cy-100}, {cx-100} {cy-110}, {cx} {cy-110} "
        f"C {cx+100} {cy-110}, {cx+180} {cy-100}, {cx+180} {cy} "
        f"C {cx+180} {cy+100}, {cx+100} {cy+110}, {cx} {cy+110} "
        f"C {cx-100} {cy+110}, {cx-180} {cy+100}, {cx-180} {cy} Z"
    )
    p.append(f'<path d="{hard_path}" fill="{REDBG}" fill-opacity="0.4" stroke="{POS}" stroke-width="2" stroke-dasharray="4,4"/>')
    
    # Вузька крута петля (магнітно-м'який матеріал)
    soft_path = (
        f"M {cx-25} {cy} "
        f"C {cx-25} {cy-90}, {cx-10} {cy-140}, {cx} {cy-140} "
        f"C {cx+10} {cy-140}, {cx+25} {cy-90}, {cx+25} {cy} "
        f"C {cx+25} {cy+90}, {cx+10} {cy+140}, {cx} {cy+140} "
        f"C {cx-10} {cy+140}, {cx-25} {cy+90}, {cx-25} {cy} Z"
    )
    p.append(f'<path d="{soft_path}" fill="{GRNBG}" fill-opacity="0.7" stroke="{FIELD}" stroke-width="2.5"/>')
    
    # Позначки параметрів
    # B_sat
    p.append(line(cx - 8, cy - 140, cx + 8, cy - 140, color=FIELD, sw=1.5))
    p.append(text(cx - 15, cy - 140, "B_sat", size=11, color=FIELD, anchor="end", bold=True))
    
    # B_r (залишкова індукція)
    p.append(circle(cx, cy - 100, 3.5, fill=FIELD, stroke=FIELD))
    p.append(text(cx + 12, cy - 100, "B_r", size=11, color=FIELD, anchor="start", bold=True))
    
    # H_c (коерцитивна сила м'якого)
    p.append(circle(cx - 25, cy, 3.5, fill=FIELD, stroke=FIELD))
    p.append(text(cx - 30, cy + 18, "−H_c", size=11, color=FIELD, anchor="end", bold=True))
    
    # H_c (твердого)
    p.append(circle(cx - 180, cy, 3.5, fill=POS, stroke=POS))
    p.append(text(cx - 185, cy + 18, "−H_c (твердий)", size=10, color=POS, anchor="end", bold=True))
    
    # Легенда / підписи блоків праворуч
    tb1, _, _ = textbox(620, 90, "Магнітно-твердий матеріал\n• Широка петля (великі втрати)\n• Велика H_c (> 10 кА/м)\n• Для постійних магнітів", size=10, pad=8, fill=REDBG, stroke=POS)
    p.append(tb1)
    
    tb2, _, _ = textbox(620, 240, "Магнітно-м'який матеріал\n• Вузька петля (малі втрати)\n• Низька H_c (< 1000 А/м)\n• Висока проникність μ\n• Для осердь і трансформаторів", size=10, pad=8, fill=GRNBG, stroke=FIELD)
    p.append(tb2)
    
    # Нахил кривої (проникність)
    p.append(text(cx + 60, cy - 110, "Крутий нахил: μ = dB/dH ≫ 1", size=10, color=FIELD, anchor="start", bold=True))
    
    render(os.path.join(OUT, "bh-loops-comparison.svg"), W, H, *p,
           title="Петлі гістерезису: магнітно-м'який проти магнітно-твердого матеріалу")


# ── 2. materials-spectrum: Карта магнітно-м'яких матеріалів (f проти B_sat) ───
def fig_materials_spectrum():
    W, H = 780, 420
    p = []
    
    # Межі графіка
    x0, y0 = 90, 60
    gw, gh = 640, 310
    
    # Сітка та осі
    p.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))
    
    # Вісь X: Частота (логарифмічна шкала)
    # 50 Гц, 1 кГц, 10 кГц, 100 кГц, 1 МГц, 10 МГц, 100 МГц
    freqs = [("50 Гц", 0.05), ("1 кГц", 0.20), ("10 кГц", 0.38), 
             ("100 кГц", 0.55), ("1 МГц", 0.72), ("10 МГц", 0.86), ("100 МГц", 0.98)]
    for lbl, frac in freqs:
        fx = x0 + frac * gw
        p.append(line(fx, y0, fx, y0 + gh, color="#e5e7eb", sw=1, dash="2,2"))
        p.append(text(fx, y0 + gh + 18, lbl, size=10, color=MUTED, anchor="middle"))
    p.append(text(x0 + gw / 2, y0 + gh + 35, "Робоча частота f", size=11, color=INK, anchor="middle", bold=True))
    
    # Вісь Y: B_sat (Тл) від 0.0 до 2.2 Тл
    b_levels = [(0.0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0 Тл")]
    for bval, lbl in b_levels:
        fy = y0 + gh - (bval / 2.2) * gh
        p.append(line(x0, fy, x0 + gw, fy, color="#e5e7eb", sw=1, dash="2,2"))
        p.append(text(x0 - 10, fy + 4, lbl, size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 45, y0 + gh / 2, "B_sat (Тл)", size=11, color=INK, anchor="middle", bold=True))
    
    # Блоки матеріалів (рознесені за діапазонами B_sat та частоти)
    # 1. Кремнієва сталь (CRGO/CRNGO): 50 Гц - 1 кГц, B_sat = 1.5 - 2.0 Тл
    sx1 = x0 + 0.02 * gw
    sx2 = x0 + 0.24 * gw
    sy1 = y0 + gh - (2.0 / 2.2) * gh
    sy2 = y0 + gh - (1.5 / 2.2) * gh
    p.append(rect(sx1, sy1, sx2 - sx1, sy2 - sy1, fill=BLUEBG, stroke=NEG, sw=1.5, rx=5))
    p.append(text((sx1 + sx2) / 2, sy1 + 18, "Електротехнічна сталь", size=10.5, color=NEG, anchor="middle", bold=True))
    p.append(text((sx1 + sx2) / 2, sy1 + 36, "CRGO / CRNGO (листи 0.2–0.5 мм)", size=9.5, color=INK, anchor="middle"))
    p.append(text((sx1 + sx2) / 2, sy1 + 52, "B_sat ≈ 1.7–2.0 Тл", size=9.5, color=NEG, anchor="middle", bold=True))
    
    # 2. Нанокристалічні сплави (Finemet): 5 кГц - 150 кГц, B_sat = 1.15 - 1.40 Тл
    nx1 = x0 + 0.28 * gw
    nx2 = x0 + 0.58 * gw
    ny1 = y0 + gh - (1.40 / 2.2) * gh
    ny2 = y0 + gh - (1.15 / 2.2) * gh
    p.append(rect(nx1, ny1, nx2 - nx1, ny2 - ny1, fill=VIOLETBG, stroke=VIOLET, sw=1.5, rx=5))
    p.append(text((nx1 + nx2) / 2, ny1 + 16, "Нанокристали (Finemet / Vitroperm)", size=10, color=VIOLET, anchor="middle", bold=True))
    p.append(text((nx1 + nx2) / 2, ny1 + 32, "Стрічка 18 мкм · B_sat ≈ 1.25 Тл · μ до 100 000", size=9.5, color=INK, anchor="middle"))
    
    # 3. Порошкові осердя (Sendust, High Flux, MPP): 20 кГц - 500 кГц, B_sat = 0.60 - 1.10 Тл
    px1 = x0 + 0.35 * gw
    px2 = x0 + 0.68 * gw
    py1 = y0 + gh - (1.10 / 2.2) * gh
    py2 = y0 + gh - (0.60 / 2.2) * gh
    p.append(rect(px1, py1, px2 - px1, py2 - py1, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=5))
    p.append(text((px1 + px2) / 2, py1 + 18, "Порошкові осердя (Powder Cores)", size=10.5, color=AMBER, anchor="middle", bold=True))
    p.append(text((px1 + px2) / 2, py1 + 36, "Sendust (1.0 Тл) · High Flux (1.5 Тл) · MPP", size=9.5, color=INK, anchor="middle"))
    p.append(text((px1 + px2) / 2, py1 + 54, "Розподілений зазор · Soft saturation під DC", size=9.5, color=AMBER, anchor="middle", bold=True))
    
    # 4. Ферити MnZn: 20 кГц - 2 МГц, B_sat = 0.35 - 0.52 Тл
    mx1 = x0 + 0.38 * gw
    mx2 = x0 + 0.74 * gw
    my1 = y0 + gh - (0.52 / 2.2) * gh
    my2 = y0 + gh - (0.35 / 2.2) * gh
    p.append(rect(mx1, my1, mx2 - mx1, my2 - my1, fill=GRNBG, stroke=FIELD, sw=1.5, rx=5))
    p.append(text((mx1 + mx2) / 2, my1 + 14, "MnZn Ферити (силові перетворювачі)", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text((mx1 + mx2) / 2, my1 + 28, "μ = 2000–10000 · B_sat ≈ 0.45 Тл", size=9.5, color=INK, anchor="middle"))
    
    # 5. Ферити NiZn: 1 МГц - 100+ МГц, B_sat = 0.20 - 0.35 Тл
    zx1 = x0 + 0.72 * gw
    zx2 = x0 + 0.98 * gw
    zy1 = y0 + gh - (0.35 / 2.2) * gh
    zy2 = y0 + gh - (0.20 / 2.2) * gh
    p.append(rect(zx1, zy1, zx2 - zx1, zy2 - zy1, fill=CYANBG, stroke=CYAN, sw=1.5, rx=5))
    p.append(text((zx1 + zx2) / 2, zy1 + 14, "NiZn Ферити (ВЧ / EMI)", size=10, color=CYAN, anchor="middle", bold=True))
    p.append(text((zx1 + zx2) / 2, zy1 + 28, "ρ > 10⁵ Ом·м · B_sat ≈ 0.3 Тл", size=9.5, color=INK, anchor="middle"))
    
    render(os.path.join(OUT, "materials-spectrum.svg"), W, H, *p,
           title="Спектр м'яких магнітних матеріалів: частотний діапазон проти індукції насичення")


# ── 3. soft-vs-hard-saturation: Плавне насичення проти різкого обриву ─────────
def fig_soft_vs_hard_saturation():
    W, H = 740, 360
    p = []
    
    # Координати осей
    x0, y0 = 90, 40
    gw, gh = 360, 260
    
    p.append(line(x0, y0 + gh, x0 + gw + 20, y0 + gh, color=LINE, sw=1.5))
    p.append(arrow(x0 + gw + 18, y0 + gh, x0 + gw + 20, y0 + gh, color=LINE, sw=1.5))
    p.append(text(x0 + gw + 25, y0 + gh + 4, "Струм підмагнічування I_dc", size=10, color=INK, anchor="start", bold=True))
    
    p.append(line(x0, y0 + gh, x0, y0 - 15, color=LINE, sw=1.5))
    p.append(arrow(x0, y0 - 13, x0, y0 - 15, color=LINE, sw=1.5))
    p.append(text(x0, y0 - 22, "Індуктивність L (% від номіналу)", size=10, color=INK, anchor="middle", bold=True))
    
    # Позначки осі Y
    for lvl, lbl in [(1.0, "100%"), (0.75, "75%"), (0.5, "50%"), (0.25, "25%"), (0.0, "0%")]:
        ly = y0 + gh - lvl * gh
        p.append(line(x0 - 5, ly, x0, ly, color=LINE, sw=1))
        p.append(text(x0 - 10, ly + 4, lbl, size=9.5, color=MUTED, anchor="end"))
        if lvl > 0:
            p.append(line(x0, ly, x0 + gw, ly, color="#f3f4f6", sw=1, dash="2,2"))
            
    # Крива 1: Ферит із дискретним зазором (Hard Saturation — різкий обрив)
    # Йде рівно на 100% до I_crit, потім різко падає майже до нуля
    ferrite_pts = []
    for i in range(101):
        t = i / 100.0
        x = x0 + t * gw
        if t < 0.55:
            y = y0 + gh - 0.98 * gh
        elif t < 0.65:
            # різкий спад
            k = (t - 0.55) / 0.10
            y = y0 + gh - (0.98 - k * 0.88) * gh
        else:
            y = y0 + gh - 0.08 * gh
        ferrite_pts.append(f"{x:.1f},{y:.1f}")
    p.append(f'<polyline points="{" ".join(ferrite_pts)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    
    # Крива 2: Порошкове осердя (Soft Saturation — плавний спад)
    # Поступово плавно знижується зі зростанням струму
    powder_pts = []
    for i in range(101):
        t = i / 100.0
        x = x0 + t * gw
        # плавна експоненційна/раціональна крива
        frac = 1.0 / (1.0 + 1.2 * (t ** 1.3))
        y = y0 + gh - (frac * 0.98) * gh
        powder_pts.append(f"{x:.1f},{y:.1f}")
    p.append(f'<polyline points="{" ".join(powder_pts)}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    
    # Пояснювальні картки праворуч
    tb1, _, _ = textbox(605, 110, "Ферит із дискретним зазором\n• Різке насичення (Hard saturation)\n• До I_нас індуктивність стабільна\n• При перевищенні I_нас — прірва:\n  струм злітає, ключ згорає", size=9.5, pad=8, fill=REDBG, stroke=POS)
    p.append(tb1)
    
    tb2, _, _ = textbox(605, 245, "Порошкове осердя (Sendust / HF)\n• Плавне насичення (Soft saturation)\n• Розподілений повітряний зазор\n• При перевантаженні L падає плавно\n• Схема витримує пікові кидки", size=9.5, pad=8, fill=GRNBG, stroke=FIELD)
    p.append(tb2)
    
    # Підпис критичної точки
    p.append(line(x0 + 0.60 * gw, y0 + 0.35 * gh, x0 + 0.60 * gw, y0 + gh, color=POS, sw=1.2, dash="3,3"))
    p.append(text(x0 + 0.60 * gw, y0 + 0.28 * gh, "Стіна насичення фериту", size=9.5, color=POS, anchor="middle", bold=True))
    
    render(os.path.join(OUT, "soft-vs-hard-saturation.svg"), W, H, *p,
           title="Поведінка під постійним струмом підмагнічування: різке насичення проти плавного")


# ── 4. eddy-current-mitigation: Механізми придушення вихрових струмів ─────────
def fig_eddy_mitigation():
    W, H = 760, 320
    p = []
    
    bw, bh = 155, 230
    y_box = 55
    
    # 4 блоки
    # Блок 1: Суцільний метал
    bx1 = 30
    p.append(rect(bx1, y_box, bw, bh, fill="#fafbfc", stroke=POS, sw=1.5, rx=6))
    p.append(text(bx1 + bw/2, y_box + 20, "1. Суцільний метал", size=10.5, color=POS, bold=True))
    p.append(rect(bx1 + 25, y_box + 40, 105, 100, fill="#e2e8f0", stroke=LINE, sw=1.5))
    # Вихори струму
    p.append(f'<circle cx="{bx1 + 77}" cy="{y_box + 90}" r="38" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="3,3"/>')
    p.append(f'<circle cx="{bx1 + 77}" cy="{y_box + 90}" r="20" fill="none" stroke="{POS}" stroke-width="1.5" stroke-dasharray="2,2"/>')
    p.append(text(bx1 + bw/2, y_box + 160, "Низький опір ρ\nВеличезні вихори струму\nКатастрофічний нагрів\nP_e ∝ f² · d²", size=9, color=INK))
    
    # Блок 2: Тонкі пластини (CRGO)
    bx2 = 215
    p.append(rect(bx2, y_box, bw, bh, fill="#fafbfc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(bx2 + bw/2, y_box + 20, "2. Листи з лаком", size=10.5, color=NEG, bold=True))
    # 5 тонких пластин з ізолятором
    for k in range(5):
        px = bx2 + 25 + k * 21
        p.append(rect(px, y_box + 40, 17, 100, fill="#e2e8f0", stroke=LINE, sw=1))
        p.append(f'<ellipse cx="{px + 8.5}" cy="{y_box + 90}" rx="6" ry="25" fill="none" stroke="{NEG}" stroke-width="1.2"/>')
    p.append(text(bx2 + bw/2, y_box + 160, "Товщина d = 0.2–0.35 мм\nСтрум затиснутий у листі\nВтрати зменшені в (D/d)² раз\nЧастота: 50–400 Гц", size=9, color=INK))
    
    # Блок 3: Порошкове осердя
    bx3 = 400
    p.append(rect(bx3, y_box, bw, bh, fill="#fafbfc", stroke=AMBER, sw=1.5, rx=6))
    p.append(text(bx3 + bw/2, y_box + 20, "3. Порошок у зв'язці", size=10.5, color=AMBER, bold=True))
    # Матриця мікрогранул
    p.append(rect(bx3 + 25, y_box + 40, 105, 100, fill=AMBERBG, stroke=LINE, sw=1))
    for gx in range(4):
        for gy in range(4):
            cx = bx3 + 38 + gx * 26
            cy = y_box + 53 + gy * 25
            p.append(circle(cx, cy, 9, fill="#cbd5e1", stroke=AMBER, sw=1.2))
            p.append(circle(cx, cy, 4, fill="none", stroke=POS, sw=0.8))
    p.append(text(bx3 + bw/2, y_box + 160, "Гранули d ≈ 10–50 мкм\nІзолююча діелектрична смола\nРозподілений зазор\nЧастота: 10–500 кГц", size=9, color=INK))
    
    # Блок 4: Ферит (кераміка)
    bx4 = 585
    p.append(rect(bx4, y_box, bw, bh, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx4 + bw/2, y_box + 20, "4. Ферит-кераміка", size=10.5, color=FIELD, bold=True))
    p.append(rect(bx4 + 25, y_box + 40, 105, 100, fill=GRNBG, stroke=FIELD, sw=1.5))
    p.append(text(bx4 + bw/2, y_box + 85, "Оксидна ґратка\nMO · Fe₂O₃", size=9.5, color=FIELD, bold=True))
    p.append(text(bx4 + bw/2, y_box + 115, "ρ = 10¹–10⁷ Ом·м", size=9.5, color=INK, bold=True))
    p.append(text(bx4 + bw/2, y_box + 160, "Власний діелектрик\nВихрових струмів немає\nВтрати лише на гістерезис\nЧастота: 100 кГц–100 МГц", size=9, color=INK))
    
    render(os.path.join(OUT, "eddy-current-mitigation.svg"), W, H, *p,
           title="Еволюція боротьби з вихровими струмами: від суцільного металу до кераміки")


# ── 5. loss-breakdown-bertotti: Розподіл втрат за Бертотті ─────────────────────
def fig_loss_breakdown():
    W, H = 720, 340
    p = []
    
    x0, y0 = 90, 45
    gw, gh = 380, 240
    
    # Осі
    p.append(line(x0, y0 + gh, x0 + gw + 20, y0 + gh, color=LINE, sw=1.5))
    p.append(arrow(x0 + gw + 18, y0 + gh, x0 + gw + 20, y0 + gh, color=LINE, sw=1.5))
    p.append(text(x0 + gw + 25, y0 + gh + 4, "Частота f", size=11, color=INK, anchor="start", bold=True))
    
    p.append(line(x0, y0 + gh, x0, y0 - 15, color=LINE, sw=1.5))
    p.append(arrow(x0, y0 - 13, x0, y0 - 15, color=LINE, sw=1.5))
    p.append(text(x0, y0 - 22, "Питомі втрати P_v (Вт/м³)", size=11, color=INK, anchor="middle", bold=True))
    
    # 3 зони втрат (стековий графік):
    # 1. P_hyst = k_h * f (лінійно)
    # 2. P_eddy = k_e * f^2 (квадратично)
    # 3. P_exc = k_exc * f^1.5 (надлишкові)
    
    # Точки кривих
    pts_base = []
    pts_h = []
    pts_e = []
    pts_tot = []
    
    for i in range(101):
        t = i / 100.0
        x = x0 + t * gw
        
        # Висоти трьох складових (у пікселях)
        yh = 70 * t
        ye = 120 * (t ** 2)
        yexc = 40 * (t ** 1.5)
        
        y_h_top = y0 + gh - yh
        y_e_top = y_h_top - ye
        y_tot_top = y_e_top - yexc
        
        pts_h.append((x, y_h_top))
        pts_e.append((x, y_e_top))
        pts_tot.append((x, y_tot_top))
        pts_base.append((x, y0 + gh))
        
    # Шляхи для заповнення областей
    path_h = f"M {x0} {y0+gh} " + " ".join([f"L {x:.1f} {y:.1f}" for x, y in pts_h]) + f" L {x0+gw} {y0+gh} Z"
    path_e = f"M {pts_h[0][0]} {pts_h[0][1]} " + " ".join([f"L {x:.1f} {y:.1f}" for x, y in pts_e]) + " " + " ".join([f"L {x:.1f} {y:.1f}" for x, y in reversed(pts_h)]) + " Z"
    path_exc = f"M {pts_e[0][0]} {pts_e[0][1]} " + " ".join([f"L {x:.1f} {y:.1f}" for x, y in pts_tot]) + " " + " ".join([f"L {x:.1f} {y:.1f}" for x, y in reversed(pts_e)]) + " Z"
    
    p.append(f'<path d="{path_h}" fill="{BLUEBG}" stroke="{NEG}" stroke-width="1.5"/>')
    p.append(f'<path d="{path_e}" fill="{REDBG}" stroke="{POS}" stroke-width="1.5"/>')
    p.append(f'<path d="{path_exc}" fill="{VIOLETBG}" stroke="{VIOLET}" stroke-width="1.5"/>')
    
    # Лінія повної суми
    tot_line = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts_tot])
    p.append(f'<polyline points="{tot_line}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    
    # Підписи зон на самому графіку
    p.append(text(x0 + 0.65 * gw, y0 + gh - 25, "Гістерезис: P_h ∝ f", size=10, color=NEG, bold=True))
    p.append(text(x0 + 0.70 * gw, y0 + gh - 95, "Вихрові струми: P_e ∝ f²", size=10, color=POS, bold=True))
    p.append(text(x0 + 0.75 * gw, y0 + gh - 185, "Надлишкові (P_exc)", size=9.5, color=VIOLET, bold=True))
    
    # Легенда / підсумок праворуч
    tb, _, _ = textbox(595, 140, "Розподіл втрат за Бертотті\n\nP_v = P_h + P_e + P_exc\n\n• P_h = W_h · f (площа петлі)\n• P_e = C_e · f² · B² / ρ\n• P_exc = C_exc · f¹·⁵ · B¹·⁵\n\nРівняння Штейнмеца:\nP_v = C_m · f^α · B^β\n(α ≈ 1.3–2.0, β ≈ 2.0–2.8)", size=9.5, pad=10, fill="#f8fafc", stroke=LINE)
    p.append(tb)
    
    render(os.path.join(OUT, "loss-breakdown-bertotti.svg"), W, H, *p,
           title="Розподіл втрат в осерді: гістерезис, вихрові струми та надлишкові втрати")


if __name__ == "__main__":
    fig_bh_loops()
    fig_materials_spectrum()
    fig_soft_vs_hard_saturation()
    fig_eddy_mitigation()
    fig_loss_breakdown()
    print("All figures generated successfully.")
