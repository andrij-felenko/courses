# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1: Тунелювання Фаулера — Нордгейма та генерація пасток (FN Tunneling & Trapping)
# ════════════════════════════════════════════════════════════════════════════
def fig_fn_tunneling():
    W, H = 860, 450
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d0d0", sw=1, rx=0))
    f.append(text(W/2, 30, "Енергетична діаграма тунелювання FN та генерація пасток у SiO₂", size=15, bold=True, color=INK))
    f.append(text(W/2, 50, "Сильне електричне поле E_ox > 8 МВ/см під час програмування/стирання", size=12, color=MUTED))

    # Si Substrate
    f.append(rect(60, 80, 140, 290, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    f.append(text(130, 105, "Кремнієвий канал", size=13, bold=True, color="#1b4f72"))
    f.append(text(130, 125, "(Si Substrate)", size=11, color="#2980b9"))

    # Tunnel SiO2
    f.append(rect(200, 80, 320, 290, fill="#fdfefe", stroke="#b2babb", sw=1.5, rx=0))
    f.append(text(360, 105, "Тунельний діелектрик (SiO₂ ~ 8 нм)", size=13, bold=True, color="#424949"))

    # Charge Storage Layer
    f.append(rect(520, 80, 280, 290, fill="#fdebd0", stroke="#d35400", sw=1.5, rx=4))
    f.append(text(660, 105, "Затвор / Пастка заряду", size=13, bold=True, color="#7e5109"))
    f.append(text(660, 125, "(Poly-Si / Si₃N₄)", size=11, color="#d35400"))

    # Energy bands
    f.append(svg_path("M 80 180 L 200 180 L 520 310 L 800 310", stroke="#27ae60", sw=2.5))
    f.append(text(100, 170, "E_c (Si)", size=11, bold=True, color="#27ae60"))
    f.append(text(500, 335, "E_c (SiO₂)", size=11, bold=True, color="#27ae60"))

    f.append(svg_path("M 200 180 L 200 80 L 520 310", stroke="#c0392b", sw=1.5, dash="4 4"))
    f.append(text(250, 120, "Бар'єр Φ_b = 3.15 еВ", size=11, bold=True, color="#c0392b"))

    # Electron tunneling
    f.append(arrow(140, 195, 290, 195, color="#2457d6", sw=2.5))
    f.append(circle(140, 195, 6, fill="#2457d6", stroke="#1b4f72", sw=1))
    f.append(text(140, 195, "e⁻", size=9, color="#ffffff", bold=True))
    f.append(text(215, 215, "FN Тунелювання", size=11, bold=True, color="#2457d6"))

    # Hot electron line
    f.append(line(290, 195, 540, 320, color="#2457d6", sw=2, dash="3 3"))
    f.append(text(410, 230, "Гарячий електрон", size=10.5, color="#2457d6"))

    # Anode Hole Injection
    f.append(circle(540, 320, 6, fill="#c0392b", stroke="#7b241c", sw=1))
    f.append(text(540, 320, "h⁺", size=9, color="#ffffff", bold=True))
    f.append(arrow(540, 320, 390, 280, color="#c0392b", sw=2))
    f.append(text(480, 345, "AHI: інжекція дірки", size=10.5, bold=True, color="#c0392b"))

    # Traps
    f.append(circle(200, 190, 5, fill="#f39c12", stroke="#b9770e", sw=1))
    f.append(circle(200, 230, 5, fill="#f39c12", stroke="#b9770e", sw=1))
    f.append(text(150, 245, "Поверхневі стани N_it", size=10.5, bold=True, color="#b9770e"))

    f.append(circle(320, 220, 5, fill="#e74c3c", stroke="#78281f", sw=1))
    f.append(circle(410, 260, 5, fill="#e74c3c", stroke="#78281f", sw=1))
    f.append(circle(360, 180, 5, fill="#e74c3c", stroke="#78281f", sw=1))
    f.append(text(340, 155, "Об'ємні пастки N_ot", size=10.5, bold=True, color="#e74c3c"))

    # Footer
    f.append(rect(60, 380, 740, 50, fill="#f4f6f8", stroke="#d5dbdb", sw=1, rx=4))
    f.append(text(W/2, 400, "Механізм зносу: 1) FN-тунелювання електронів → 2) розрив зв'язків Si-H / Si-O →", size=11, bold=True, color=INK))
    f.append(text(W/2, 418, "3) утворення пасток N_ot і N_it → 4) захоплення негативного заряду та зсув V_th", size=11, color=MUTED))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.extend(f)
    out.append('</svg>')
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2: Звуження вікна програмування (Vth window closure)
# ════════════════════════════════════════════════════════════════════════════
def fig_vth_closure():
    W, H = 860, 430
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d0d0", sw=1, rx=0))
    f.append(text(W/2, 28, "Деградація вікна порогової напруги (V_th) від P/E-циклів", size=15, bold=True, color=INK))
    f.append(text(W/2, 48, "Зсув стану стирання Erase (N_ot) та зниження стану програмування Program", size=12, color=MUTED))

    ox, oy = 80, 360
    w_w, w_h = 720, 280
    f.append(arrow(ox, oy, ox + w_w, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - w_h, color=LINE, sw=1.8))
    f.append(text(ox + w_w - 20, oy + 25, "Порогова напруга V_th (В)", size=12, bold=True, color=INK))
    f.append(text(ox + 10, oy - w_h + 15, "Густина імовірності P(V_th)", size=11, anchor="start", bold=True, color=INK))

    v_ticks = [(-2, "Erase (-2V)", 180), (0, "0 V", 320), (3, "Read V_r", 480), (6, "Program (+6V)", 680)]
    for val, label, px in v_ticks:
        f.append(line(px, oy - 5, px, oy + 5, color=LINE, sw=1))
        f.append(text(px, oy + 20, label, size=10.5, color=MUTED))

    f.append(svg_path("M 100 360 Q 180 120 260 360", stroke="#2457d6", sw=2.5))
    f.append(text(180, 140, "Erase (1 цикл)", size=11, bold=True, color="#2457d6"))

    f.append(svg_path("M 600 360 Q 680 120 760 360", stroke="#27ae60", sw=2.5))
    f.append(text(680, 140, "Program (1 цикл)", size=11, bold=True, color="#27ae60"))

    f.append(line(180, 110, 680, 110, color=INK, sw=1.5, dash="3 3"))
    f.append(text(430, 100, "Початкове вікно пам'яті ΔV_mw ≈ 8 В", size=11.5, bold=True, color=INK))

    f.append(svg_path("M 170 360 Q 280 210 390 360", stroke="#c0392b", sw=2.5, dash="6 3"))
    f.append(text(300, 230, "Erase (10⁵ циклів)", size=11, bold=True, color="#c0392b"))
    f.append(arrow(180, 250, 270, 250, color="#c0392b", sw=2))
    f.append(text(225, 270, "+ΔV_th (захоплення e⁻)", size=10, bold=True, color="#c0392b"))

    f.append(svg_path("M 470 360 Q 580 210 690 360", stroke="#d35400", sw=2.5, dash="6 3"))
    f.append(text(580, 230, "Program (10⁵ циклів)", size=11, bold=True, color="#d35400"))
    f.append(arrow(680, 250, 590, 250, color="#d35400", sw=2))
    f.append(text(635, 270, "-ΔV_th (екранування)", size=10, bold=True, color="#d35400"))

    f.append(line(280, 200, 580, 200, color="#c0392b", sw=1.5))
    f.append(text(430, 190, "Звужене вікно ΔV_mw(N_PE) < 3 В", size=11, bold=True, color="#c0392b"))

    f.append(rect(430, 290, 100, 65, fill="#fadbd8", stroke="#e74c3c", sw=1, rx=4))
    f.append(text(480, 310, "Зона помилок", size=10.5, bold=True, color="#c0392b"))
    f.append(text(480, 328, "зчитування (BER)", size=10, color="#c0392b"))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.extend(f)
    out.append('</svg>')
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3: Модель перколяції SILC (Percolation Breakdown Model)
# ════════════════════════════════════════════════════════════════════════════
def fig_silc_percolation():
    W, H = 860, 420
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d0d0", sw=1, rx=0))
    f.append(text(W/2, 28, "Модель перколяції витоку SILC та тунельного пробою діелектрика", size=15, bold=True, color=INK))
    f.append(text(W/2, 48, "Еволюція пасток у SiO₂: від поодиноких дефектів до провідного містка", size=12, color=MUTED))

    pw, ph = 240, 260
    p_y = 85

    # Panel A
    ax = 40
    f.append(rect(ax, p_y, pw, ph, fill="#f8f9f9", stroke="#7f8c8d", sw=1.5, rx=4))
    f.append(text(ax + pw/2, p_y + 25, "А) Свіжий діелектрик", size=12.5, bold=True, color=INK))
    f.append(text(ax + pw/2, p_y + 42, "N_PE = 0 (Ідеальний оксид)", size=10.5, color=MUTED))
    f.append(rect(ax + 15, p_y + 55, pw - 30, 20, fill="#d6eaf8", stroke="#2980b9", sw=1))
    f.append(text(ax + pw/2, p_y + 69, "Плаваючий затвор (FG)", size=10, bold=True, color="#1b4f72"))
    f.append(rect(ax + 15, p_y + 215, pw - 30, 20, fill="#ebf5fb", stroke="#2980b9", sw=1))
    f.append(text(ax + pw/2, p_y + 229, "Кремнієвий канал (Si)", size=10, bold=True, color="#1b4f72"))

    f.append(circle(ax + 80, p_y + 110, 4.5, fill="#f39c12", stroke="#b9770e", sw=1))
    f.append(circle(ax + 170, p_y + 170, 4.5, fill="#f39c12", stroke="#b9770e", sw=1))
    f.append(text(ax + pw/2, p_y + 250, "Струм витоку I_SILC ≈ 0", size=11, bold=True, color="#27ae60"))

    # Panel B
    bx = 310
    f.append(rect(bx, p_y, pw, ph, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=4))
    f.append(text(bx + pw/2, p_y + 25, "Б) Індукований витік SILC", size=12.5, bold=True, color=INK))
    f.append(text(bx + pw/2, p_y + 42, "N_PE ≈ 10⁴ (Двопасткове тунелювання)", size=10.5, color=MUTED))
    f.append(rect(bx + 15, p_y + 55, pw - 30, 20, fill="#d6eaf8", stroke="#2980b9", sw=1))
    f.append(text(bx + pw/2, p_y + 69, "Плаваючий затвор (FG)", size=10, bold=True, color="#1b4f72"))
    f.append(rect(bx + 15, p_y + 215, pw - 30, 20, fill="#ebf5fb", stroke="#2980b9", sw=1))
    f.append(text(bx + pw/2, p_y + 229, "Кремнієвий канал (Si)", size=10, bold=True, color="#1b4f72"))

    traps_b = [(70, 100), (90, 140), (140, 110), (160, 150), (180, 190), (110, 185)]
    for tx, ty in traps_b:
        f.append(circle(bx + tx, p_y + ty, 4.5, fill="#e67e22", stroke="#a04000", sw=1))

    f.append(line(bx + 90, p_y + 75, bx + 90, p_y + 140, color="#d35400", sw=1.5, dash="2 2"))
    f.append(line(bx + 90, p_y + 140, bx + 110, p_y + 185, color="#d35400", sw=1.5, dash="2 2"))
    f.append(line(bx + 110, p_y + 185, bx + 110, p_y + 215, color="#d35400", sw=1.5, dash="2 2"))
    f.append(text(bx + pw/2, p_y + 250, "Втрата заряду (Retention loss)", size=11, bold=True, color="#d35400"))

    # Panel C
    cx = 580
    f.append(rect(cx, p_y, pw, ph, fill="#fadbd8", stroke="#e74c3c", sw=1.5, rx=4))
    f.append(text(cx + pw/2, p_y + 25, "В) Пробій (Percolation)", size=12.5, bold=True, color=INK))
    f.append(text(cx + pw/2, p_y + 42, "N_PE > 10⁵ (Неперервний місток)", size=10.5, color=MUTED))
    f.append(rect(cx + 15, p_y + 55, pw - 30, 20, fill="#d6eaf8", stroke="#2980b9", sw=1))
    f.append(text(cx + pw/2, p_y + 69, "Плаваючий затвор (FG)", size=10, bold=True, color="#1b4f72"))
    f.append(rect(cx + 15, p_y + 215, pw - 30, 20, fill="#ebf5fb", stroke="#2980b9", sw=1))
    f.append(text(cx + pw/2, p_y + 229, "Кремнієвий канал (Si)", size=10, bold=True, color="#1b4f72"))

    chain_c = [(120, 90), (115, 120), (125, 150), (118, 180), (122, 205)]
    for tx, ty in chain_c:
        f.append(circle(cx + tx, p_y + ty, 5.5, fill="#c0392b", stroke="#78281f", sw=1.5))

    f.append(svg_path("M %d %d L %d %d L %d %d L %d %d L %d %d" %
                      (cx+120, p_y+75, cx+115, p_y+120, cx+125, p_y+150, cx+118, p_y+180, cx+122, p_y+215),
                      stroke="#c0392b", sw=3))
    f.append(text(cx + pw/2, p_y + 250, "Омичний короткий пробій", size=11, bold=True, color="#c0392b"))

    f.append(rect(40, 360, 780, 45, fill="#f4f6f8", stroke="#d5dbdb", sw=1, rx=4))
    f.append(text(W/2, 385, "Критична умова пробою: коли середня відстань між пастками r_trap < 0.8 нм,", size=11, bold=True, color=INK))
    f.append(text(W/2, 400, "виникає квантове тунелювання вздовж усього ланцюжка дефектів (TDDB).", size=10.5, color=MUTED))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.extend(f)
    out.append('</svg>')
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4: Порівняння ресурсу P/E циклів (P/E Endurance Comparison)
# ════════════════════════════════════════════════════════════════════════════
def fig_pe_endurance():
    W, H = 860, 440
    f = []

    f.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d0d0", sw=1, rx=0))
    f.append(text(W/2, 28, "Залежність початкової частоти помилок (RBER) від P/E-циклів", size=15, bold=True, color=INK))
    f.append(text(W/2, 48, "Порівняння планарних (2D) та об'ємних (3D Charge Trap) архітектур Flash", size=12, color=MUTED))

    ox, oy = 90, 360
    w_w, w_h = 710, 270

    f.append(arrow(ox, oy, ox + w_w, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - w_h, color=LINE, sw=1.8))
    f.append(text(ox + w_w - 30, oy + 25, "Кількість P/E циклів (N_PE)", size=12, bold=True, color=INK))
    f.append(text(ox + 10, oy - w_h + 15, "Частота помилок RBER", size=11, anchor="start", bold=True, color=INK))

    x_ticks = [(100, "10²", 150), (1000, "10³", 300), (10000, "10⁴", 450), (100000, "10⁵", 600), (1000000, "10⁶", 750)]
    for val, label, px in x_ticks:
        f.append(line(px, oy - 5, px, oy + 5, color=LINE, sw=1))
        f.append(text(px, oy + 20, label, size=10.5, color=MUTED))

    y_ticks = [(-6, "10⁻⁶", 330), (-4, "10⁻⁴", 250), (-2, "10⁻²", 170), (-1, "10⁻¹", 120)]
    for val, label, py in y_ticks:
        f.append(line(ox - 5, py, ox + 5, py, color=LINE, sw=1))
        f.append(text(ox - 45, py + 4, label, size=10, color=MUTED if val != -2 else "#c0392b"))

    f.append(line(ox, 170, ox + w_w - 20, 170, color="#c0392b", sw=2, dash="5 4"))

    # Use textbox for LDPC limit label
    tb_ldpc, _, _ = textbox(250, 140, "Межа LDPC ECC (RBER = 10⁻²)", size=11, pad=5, fill="#fdfefe", stroke="#c0392b", sw=1, color="#c0392b", bold=True)
    f.append(tb_ldpc)

    # Use textbox for legend
    legend_text = "Технологічні межі endurance:\n• 2D SLC: 50,000 – 100,000 P/E\n• 3D TLC CT: 3,000 – 5,000 P/E\n• 2D TLC FG: 500 – 1,000 P/E\n• 3D QLC CT: 500 – 1,500 P/E"
    tb_leg, _, _ = textbox(650, 110, legend_text, size=10.5, pad=8, fill="#fdfefe", stroke="#bdc3c7", sw=1, color=INK)
    f.append(tb_leg)

    # Curves
    f.append(svg_path("M 150 340 Q 450 320 600 170", stroke="#27ae60", sw=2.5))
    tb1, _, _ = textbox(680, 210, "2D SLC FG (~10⁵)", size=10, pad=4, fill="#e8f8f5", stroke="#27ae60", sw=1, color="#27ae60", bold=True)
    f.append(tb1)

    f.append(svg_path("M 150 330 Q 300 280 380 170", stroke="#2457d6", sw=2.5))
    tb2, _, _ = textbox(430, 210, "3D TLC CT (~3·10³)", size=10, pad=4, fill="#eaf2f8", stroke="#2457d6", sw=1, color="#2457d6", bold=True)
    f.append(tb2)

    f.append(svg_path("M 150 310 Q 240 260 300 170", stroke="#d35400", sw=2.5))
    tb3, _, _ = textbox(330, 275, "2D TLC FG (~10³)", size=10, pad=4, fill="#fef5e7", stroke="#d35400", sw=1, color="#d35400", bold=True)
    f.append(tb3)

    f.append(svg_path("M 150 280 Q 210 230 270 170", stroke="#8e44ad", sw=2.5))
    tb4, _, _ = textbox(200, 225, "3D QLC CT (~10³)", size=10, pad=4, fill="#f5eeed", stroke="#8e44ad", sw=1, color="#8e44ad", bold=True)
    f.append(tb4)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.extend(f)
    out.append('</svg>')
    return "\n".join(out)

def main():
    generators = [
        ("fn-tunneling-and-trapping.svg", fig_fn_tunneling),
        ("vth-window-closure.svg", fig_vth_closure),
        ("silc-percolation-model.svg", fig_silc_percolation),
        ("pe-endurance-comparison.svg", fig_pe_endurance),
    ]
    for fname, func in generators:
        path = os.path.join(OUT, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(func())
        print(f"Generated {fname}")

if __name__ == "__main__":
    main()
