# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Ланцюжок фотонного бюджету оптичної системи
# ═══════════════════════════════════════════════════════════════════════════
def fig_pipeline():
    W, H = 760, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 25, 'Ланцюжок поширення світла та складові фотонного бюджету', 16, INK, 'middle', bold=True))
    
    blocks = [
        (45,  75, 125, 140, 'Джерело світла', 'Лазер / СД', 'P_tx = 10 мВт', 'Φ_tx = 7.8·10¹⁵ фотонів/с', POS, '#fdf2f2'),
        (190, 75, 125, 140, 'Передавач', 'Лінзи / Введення', 'L_in = 1.5 дБ', 'η_trans = 70.8%', FIELD, '#f0fbf4'),
        (335, 75, 125, 140, 'Канал зв\'язку', 'Волокно / Повітря', 'L_ch = 20.0 дБ', 'Поглинання + розсіяння', NEG, '#eff4fe'),
        (480, 75, 125, 140, 'Приймач', 'Апертура / Фільтр', 'L_rx = 2.5 дБ', 'η_opt = 56.2%', FIELD, '#f0fbf4'),
        (625, 75, 115, 140, 'Фотодетектор', 'APD / SPAD / PIN', 'η_QE = 80%', 'N_e = 4.4·10¹² e⁻/с', POS, '#fdf2f2')
    ]
    
    for x, y, bw, bh, title_str, sub_str, p1, p2, col, bg_col in blocks:
        f.append(rect(x, y, bw, bh, fill=bg_col, stroke=col, sw=1.8, rx=6))
        f.append(text(x + bw/2, y + 24, title_str, 12, col, 'middle', bold=True))
        f.append(text(x + bw/2, y + 44, sub_str, 11, INK, 'middle'))
        f.append(line(x + 10, y + 56, x + bw - 10, y + 56, color=MUTED, sw=0.8, dash='2,2'))
        f.append(text(x + bw/2, y + 78, p1, 11, INK, 'middle', bold=True))
        
        sz = fit_font(p2, bw - 12, size=10)
        f.append(text(x + bw/2, y + 104, p2, sz, MUTED, 'middle'))

    arrows_x = [170, 315, 460, 605]
    for ax in arrows_x:
        f.append(arrow(ax, 145, ax + 20, 145, color=INK, sw=2))
        
    f.append(rect(45, 235, 695, 50, fill='#f8fafc', stroke=MUTED, sw=1, rx=4))
    f.append(text(60, 256, 'Загальний баланс:', 12, INK, 'start', bold=True))
    f.append(text(190, 256, 'Втрати L_tot = 24.0 дБ (фактор 251×)', 11, NEG, 'start'))
    f.append(text(460, 256, 'Отримано: P_rx = 39.8 мкВт', 11, FIELD, 'start', bold=True))
    f.append(text(60, 274, 'Шумова стеля: N_noise = 1.2·10⁴ e⁻/с', 11, MUTED, 'start'))
    f.append(text(330, 274, 'Сигнал/Шум: SNR = 42.5 дБ', 11, POS, 'start', bold=True))
    f.append(text(540, 274, 'Запас ліній: Margin = +15.2 дБ', 11, FIELD, 'start', bold=True))
    
    render(os.path.join(IMG, 'photon-budget-pipeline.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Механізми оптичного згасання та втрат фотонів
# ═══════════════════════════════════════════════════════════════════════════
def fig_losses():
    W, H = 740, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 25, 'Основні фізичні механізми втрати фотонів в оптичному тракті', 16, INK, 'middle', bold=True))
    
    loss_types = [
        (40,  65, 310, 105, '1. Френелівське відбиття', 'Межа двох середовищ (n₁ ≠ n₂)', 'R = ((n₁ - n₂)/(n₁ + n₂))²', 'Втрата ~4% на кожній незахищеній межі скло-повітря', POS, '#fff5f5'),
        (390, 65, 310, 105, '2. Об\'ємне поглинання', 'Перетворення фотонів у тепло', 'I(x) = I₀ · e⁻ᵃˣ (Закон Бера)', 'Примішки OH⁻ у склі, молекулярне поглинання', NEG, '#f0f4fe'),
        (40, 185, 310, 105, '3. Релеївське розсіяння', 'Флуктуації щільності (∝ 1/λ⁴)', 'I_sc ∝ I₀ / λ⁴', 'Домінує на коротких хвилях, визначає поріг оптичного волокна', FIELD, '#f0fbf4'),
        (390, 185, 310, 105, '4. Геометричні та модові втрати', 'Виньєтування, обрізання апертури', 'G = A · Ω, NA = n · sin θ', 'Нерозбіжність променя та апертурне обрізання лінзою', INK, '#f8fafc')
    ]
    
    for x, y, bw, bh, title_str, sub_str, form_str, desc_str, col, bg_col in loss_types:
        f.append(rect(x, y, bw, bh, fill=bg_col, stroke=col, sw=1.5, rx=5))
        f.append(text(x + 12, y + 22, title_str, 12, col, 'start', bold=True))
        f.append(text(x + 12, y + 40, sub_str, 11, MUTED, 'start'))
        f.append(text(x + 12, y + 62, form_str, 11, INK, 'start', bold=True))
        
        sz = fit_font(desc_str, bw - 24, size=10)
        f.append(text(x + 12, y + 84, desc_str, sz, MUTED, 'start'))

    render(os.path.join(IMG, 'optical-attenuation-losses.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Шумові режими фотодетектора та відношення сигнал/шум (SNR)
# ═══════════════════════════════════════════════════════════════════════════
def fig_noise_snr():
    W, H = 720, 330
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 25, 'Залежність Signal-to-Noise Ratio (SNR) від фотонного потоку', 16, INK, 'middle', bold=True))
    
    ox, oy = 90, 260
    gx_w, gy_h = 580, 200
    
    f.append(line(ox, oy, ox + gx_w, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - gy_h, color=INK, sw=1.5))
    
    f.append(text(ox + gx_w / 2, oy + 38, 'Потік фотонів N_p (число фотонів на імпульс)', 12, INK, 'middle', bold=True))
    f.append(text(ox - 50, oy - gy_h / 2, 'SNR (дБ)', 12, INK, 'middle', bold=True))
    
    for i in range(1, 5):
        gx = ox + i * (gx_w / 4)
        f.append(line(gx, oy, gx, oy - gy_h, color='#e2e8f0', sw=1, dash='2,2'))
        f.append(text(gx, oy + 16, '10%d' % i, 10, MUTED, 'middle'))
        
    for j in range(1, 4):
        gy = oy - j * (gy_h / 3)
        f.append(line(ox, gy, ox + gx_w, gy, color='#e2e8f0', sw=1, dash='2,2'))
        f.append(text(ox - 12, gy + 4, '%d0' % (j*2), 10, MUTED, 'end'))

    f.append(rect(ox + 10, oy - gy_h + 10, 250, 170, fill='#eff4fe', stroke='none', sw=0, rx=0))
    f.append(text(ox + 130, oy - gy_h + 30, 'Зона теплового шуму', 11, NEG, 'middle', bold=True))
    f.append(text(ox + 130, oy - gy_h + 46, 'SNR ∝ N_p (лінійне зростання)', 10, MUTED, 'middle'))

    f.append(rect(ox + 270, oy - gy_h + 10, 290, 170, fill='#f0fbf4', stroke='none', sw=0, rx=0))
    f.append(text(ox + 415, oy - gy_h + 30, 'Квантова межа (Дробовий шум)', 11, FIELD, 'middle', bold=True))
    f.append(text(ox + 415, oy - gy_h + 46, 'SNR ∝ √N_p (дробова межа)', 10, MUTED, 'middle'))

    pts = []
    for step in range(101):
        t = step / 100.0
        np_val = 10**(1.0 + 3.0 * t)
        ne = 0.8 * np_val
        sigma_thermal = 20.0
        sigma_shot = math.sqrt(ne)
        snr_lin = ne / math.sqrt(sigma_shot**2 + sigma_thermal**2)
        snr_db = 10.0 * math.log10(max(1e-3, snr_lin**2))
        
        px = ox + t * gx_w
        py = oy - (snr_db / 60.0) * gy_h
        pts.append((px, py))
        
    path_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" />' % (path_str, POS))
    
    pts_limit = []
    for step in range(101):
        t = step / 100.0
        np_val = 10**(1.0 + 3.0 * t)
        ne = 0.8 * np_val
        snr_lim = math.sqrt(ne)
        snr_db = 10.0 * math.log10(max(1e-3, snr_lim**2))
        px = ox + t * gx_w
        py = oy - (snr_db / 60.0) * gy_h
        pts_limit.append((px, py))
    path_lim_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts_limit])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3" />' % (path_lim_str, FIELD))
    
    f.append(text(ox + 460, oy - 145, 'Ідеальна квантова межа (√N_e)', 10, FIELD, 'start', bold=True))
    f.append(text(ox + 460, oy - 95, 'Реальна крива SNR (з тепловим шумом)', 10, POS, 'start', bold=True))

    render(os.path.join(IMG, 'detector-noise-snr.svg'), W, H, *f)

if __name__ == '__main__':
    fig_pipeline()
    fig_losses()
    fig_noise_snr()
    print("Figures generated successfully!")
