# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors matching style guide
CLK   = "#2457d6"   # Clock / Ref (blue)
PFD   = "#8e44ad"   # Detector / CP (purple)
VCO   = "#27ae60"   # VCO / RF (green)
DIV   = "#d35400"   # Dividers (orange)
SDM   = "#c0392b"   # Sigma-Delta / Fractional (red)
DAC   = "#16a085"   # DAC / Analog (teal)
NOISE = "#e67e22"   # Phase noise (orange)

def tick(x, base_y, lbl, color=MUTED, up=False):
    dy = -6 if up else 18
    return line(x, base_y - 4, x, base_y + 4, color=MUTED, sw=1.2) + text(x, base_y + dy, lbl, size=12, color=color)

# ── Fig 1: Integer-N PLL Synthesizer Block Diagram ─────────────────────────
def fig_pll_block_diagram():
    W, H = 820, 380
    p = []

    # Title box
    tb, tw, th = textbox(W / 2, 45,
                         "Структурна схема цілочисельного синтезатора ФАПЧ (Integer-N PLL)",
                         size=14, bold=True, fill="#f8f9fa", stroke="#bdc3c7", min_w=600)
    p.append(tb)

    # Blocks positions
    y_main = 150
    y_fb   = 270

    x_ref = 80
    x_r   = 200
    x_pfd = 340
    x_cp  = 460
    x_lf  = 570
    x_vco = 680
    x_out = 780
    x_n   = 460

    # 1. Ref Crystal Osc
    b1, w1, h1 = textbox(x_ref, y_main, "Опорний\nкварц\nf_osc", size=12, fill="#ebf5fb", stroke=CLK, bold=True, min_w=85)
    p.append(b1)

    # 2. Divider /R
    b2, w2, h2 = textbox(x_r, y_main, "Дільник\n/ R", size=12, fill="#ebf5fb", stroke=DIV, bold=True, min_w=75)
    p.append(b2)

    # 3. PFD (Phase Detector)
    b3, w3, h3 = textbox(x_pfd, y_main, "Фазовий\nдетектор\nPFD", size=12, fill="#f4ecf7", stroke=PFD, bold=True, min_w=85)
    p.append(b3)

    # 4. Charge Pump (CP)
    b4, w4, h4 = textbox(x_cp, y_main, "Помпа\nзаряду\nCP", size=12, fill="#f4ecf7", stroke=PFD, bold=True, min_w=75)
    p.append(b4)

    # 5. Loop Filter (LF)
    b5, w5, h5 = textbox(x_lf, y_main, "Петльовий\nфільтр\nLF", size=12, fill="#e8f8f5", stroke=DAC, bold=True, min_w=75)
    p.append(b5)

    # 6. VCO
    b6, w6, h6 = textbox(x_vco, y_main, "Генератор\nVCO (ГВЧ)\nf_out", size=12, fill="#e8f8f5", stroke=VCO, bold=True, min_w=95)
    p.append(b6)

    # Feedback Divider /N
    b7, w7, h7 = textbox(x_n, y_fb, "Дільник у зворотному зв'язку\n/ N", size=12, fill="#fdf2e9", stroke=DIV, bold=True, min_w=180)
    p.append(b7)

    # Arrows main path
    p.append(arrow(x_ref + w1/2, y_main, x_r - w2/2, y_main, color=CLK, sw=2.0))
    p.append(arrow(x_r + w2/2, y_main, x_pfd - w3/2, y_main, color=CLK, sw=2.0))
    p.append(text((x_r + w2/2 + x_pfd - w3/2)/2, y_main - 12, "f_ref", size=11, color=CLK, bold=True))

    p.append(arrow(x_pfd + w3/2, y_main, x_cp - w4/2, y_main, color=PFD, sw=2.0))
    p.append(arrow(x_cp + w4/2, y_main, x_lf - w5/2, y_main, color=PFD, sw=2.0))
    p.append(text((x_cp + w4/2 + x_lf - w5/2)/2, y_main - 12, "I_cp", size=11, color=PFD, bold=True))

    p.append(arrow(x_lf + w5/2, y_main, x_vco - w6/2, y_main, color=DAC, sw=2.0))
    p.append(text((x_lf + w5/2 + x_vco - w6/2)/2, y_main - 12, "V_tune", size=11, color=DAC, bold=True))

    p.append(arrow(x_vco + w6/2, y_main, x_out, y_main, color=VCO, sw=2.2))
    p.append(text(x_out - 15, y_main - 12, "f_out = N · f_ref", size=12, color=VCO, bold=True, anchor="end"))

    # Feedback path
    p.append(line(x_vco + 10, y_main, x_vco + 10, y_fb, color=VCO, sw=1.8))
    p.append(arrow(x_vco + 10, y_fb, x_n + w7/2, y_fb, color=DIV, sw=1.8))

    p.append(line(x_n - w7/2, y_fb, x_pfd, y_fb, color=DIV, sw=1.8))
    p.append(arrow(x_pfd, y_fb, x_pfd, y_main + h3/2, color=DIV, sw=1.8))
    p.append(text(x_pfd - 25, y_fb - 12, "f_fb = f_out / N", size=11, color=DIV, bold=True))

    # Equation summary at bottom
    eb, ew, eh = textbox(W / 2, 340,
                         "Основна умова рівноваги:  f_fb = f_ref  ⇒  f_out = N · (f_osc / R)",
                         size=12, bold=True, fill="#ffffff", stroke=LINE, min_w=450)
    p.append(eb)

    render(os.path.join(OUT, "pll-synthesizer-block-diagram.svg"), W, H, *p,
           title="Структурна схема цілочисельного синтезатора ФАПЧ")


# ── Fig 2: Fractional-N Synthesizer with Sigma-Delta Modulator ───────────────
def fig_fractional_n_sdm():
    W, H = 840, 380
    p = []

    tb, tw, th = textbox(W / 2, 40,
                         "Дробовий синтезатор ФАПЧ (Fractional-N) із Сигма-Дельта модулятором",
                         size=14, bold=True, fill="#f8f9fa", stroke="#bdc3c7", min_w=620)
    p.append(tb)

    y_main = 145
    y_sdm  = 275

    x_pfd = 140
    x_cp  = 260
    x_lf  = 380
    x_vco = 510
    x_out = 630

    x_prescaler = 510
    x_sdm       = 260

    # Main PLL loop
    b_pfd, w_pfd, h_pfd = textbox(x_pfd, y_main, "PFD / CP", size=12, fill="#f4ecf7", stroke=PFD, bold=True, min_w=90)
    p.append(b_pfd)

    b_lf, w_lf, h_lf = textbox(x_lf, y_main, "Петльовий\nфільтр (LF)", size=12, fill="#e8f8f5", stroke=DAC, bold=True, min_w=90)
    p.append(b_lf)

    b_vco, w_vco, h_vco = textbox(x_vco, y_main, "VCO (ГВЧ)", size=12, fill="#e8f8f5", stroke=VCO, bold=True, min_w=90)
    p.append(b_vco)

    # Dual-modulus prescaler & Divider
    b_pres, w_pres, h_pres = textbox(x_prescaler, y_sdm, "Двомодульний дільник\n/ N або / (N+1)", size=12, fill="#fdf2e9", stroke=DIV, bold=True, min_w=170)
    p.append(b_pres)

    # Sigma Delta Modulator
    b_sdm, w_sdm, h_sdm = textbox(x_sdm, y_sdm, "ΣΔ-модулятор\n(формування шуму квантування)", size=12, fill="#fadbd8", stroke=SDM, bold=True, min_w=200)
    p.append(b_sdm)

    # Connections
    # Input f_ref
    p.append(arrow(40, y_main, x_pfd - w_pfd/2, y_main, color=CLK, sw=2.0))
    p.append(text(75, y_main - 12, "f_ref", size=11, color=CLK, bold=True))

    p.append(arrow(x_pfd + w_pfd/2, y_main, x_lf - w_lf/2, y_main, color=PFD, sw=2.0))
    p.append(arrow(x_lf + w_lf/2, y_main, x_vco - w_vco/2, y_main, color=DAC, sw=2.0))
    p.append(text((x_lf + w_lf/2 + x_vco - w_vco/2)/2, y_main - 12, "V_tune", size=11, color=DAC, bold=True))

    p.append(arrow(x_vco + w_vco/2, y_main, x_out, y_main, color=VCO, sw=2.2))
    p.append(text(x_out + 10, y_main + 4, "f_out = (N + F/M) · f_ref", size=12, color=VCO, bold=True, anchor="start"))

    # Feedback to prescaler
    p.append(line(x_vco, y_main + h_vco/2, x_vco, y_sdm - h_pres/2, color=VCO, sw=1.8))
    p.append(arrow(x_vco, y_sdm - h_pres/2, x_prescaler + w_pres/2, y_sdm, color=VCO, sw=1.8))

    # Prescaler to PFD
    p.append(line(x_prescaler - w_pres/2, y_sdm, x_pfd, y_sdm, color=DIV, sw=1.8))
    p.append(arrow(x_pfd, y_sdm, x_pfd, y_main + h_pfd/2, color=DIV, sw=1.8))
    p.append(text(x_pfd - 20, y_sdm - 15, "f_fb", size=11, color=DIV, bold=True))

    # Fractional Control input
    p.append(arrow(x_sdm - w_sdm/2 - 60, y_sdm, x_sdm - w_sdm/2, y_sdm, color=SDM, sw=2.0))
    p.append(text(x_sdm - w_sdm/2 - 30, y_sdm - 12, "Дробовий код F/M", size=11, color=SDM, bold=True))

    # SDM to Prescaler control
    p.append(arrow(x_sdm + w_sdm/2, y_sdm, x_prescaler - w_pres/2, y_sdm, color=SDM, sw=2.0))
    p.append(text((x_sdm + w_sdm/2 + x_prescaler - w_pres/2)/2, y_sdm - 12, "Перемикання N/N+1", size=10, color=SDM, bold=True))

    # Explanation box
    eb, ew, eh = textbox(W / 2, 345,
                         "ΣΔ-модулятор динамічно перемикає дільник між N та N+1, формуючи дробовий коефіцієнт (N + F/M)\n"
                         "та витісняючи шум квантування у високочастотну область, де його зрізає петльовий фільтр.",
                         size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=650)
    p.append(eb)

    render(os.path.join(OUT, "fractional-n-sdm-synthesizer.svg"), W, H, *p,
           title="Дробовий синтезатор ФАПЧ із Сигма-Дельта модулятором")


# ── Fig 3: Direct Digital Synthesis (DDS) Architecture ───────────────────────
def fig_dds_architecture():
    W, H = 820, 350
    p = []

    tb, tw, th = textbox(W / 2, 40,
                         "Принцип прямого цифрового синтезу (Direct Digital Synthesis — DDS)",
                         size=14, bold=True, fill="#f8f9fa", stroke="#bdc3c7", min_w=600)
    p.append(tb)

    y_main = 150

    x_acc = 140
    x_rom = 310
    x_dac = 480
    x_lpf = 650
    x_out = 770

    # Blocks
    b_acc, w_acc, h_acc = textbox(x_acc, y_main, "Акумулятор\nфази\n(N біт)", size=12, fill="#ebf5fb", stroke=CLK, bold=True, min_w=100)
    p.append(b_acc)

    b_rom, w_rom, h_rom = textbox(x_rom, y_main, "Перетворювач\nфаза-амплітуда\n(Таблиця ПЗУ / LUT)", size=12, fill="#f4ecf7", stroke=PFD, bold=True, min_w=130)
    p.append(b_rom)

    b_dac, w_dac, h_dac = textbox(x_dac, y_main, "Цифро-аналоговий\nперетворювач\n(ЦАП / DAC)", size=12, fill="#e8f8f5", stroke=DAC, bold=True, min_w=120)
    p.append(b_dac)

    b_lpf, w_lpf, h_lpf = textbox(x_lpf, y_main, "Фільтр нижніх\nчастот (ФНЧ)\nReconstruction LPF", size=12, fill="#fef9e7", stroke=VCO, bold=True, min_w=120)
    p.append(b_lpf)

    # Connections
    # Tuning word
    p.append(arrow(x_acc, y_main - h_acc/2 - 40, x_acc, y_main - h_acc/2, color=CLK, sw=2.0))
    p.append(text(x_acc, y_main - h_acc/2 - 48, "Код частоти (FTW)", size=11, color=CLK, bold=True))

    # Clock input
    p.append(arrow(x_acc - w_acc/2 - 50, y_main, x_acc - w_acc/2, y_main, color=CLK, sw=2.0))
    p.append(text(x_acc - w_acc/2 - 25, y_main - 12, "f_clk", size=11, color=CLK, bold=True))

    # Acc to ROM
    p.append(arrow(x_acc + w_acc/2, y_main, x_rom - w_rom/2, y_main, color=CLK, sw=2.0))
    p.append(text((x_acc + w_acc/2 + x_rom - w_rom/2)/2, y_main - 12, "Фаза θ(t)", size=11, color=CLK))

    # ROM to DAC
    p.append(arrow(x_rom + w_rom/2, y_main, x_dac - w_dac/2, y_main, color=PFD, sw=2.0))
    p.append(text((x_rom + w_rom/2 + x_dac - w_dac/2)/2, y_main - 12, "Код sin(θ)", size=11, color=PFD))

    # DAC to LPF
    p.append(arrow(x_dac + w_dac/2, y_main, x_lpf - w_lpf/2, y_main, color=DAC, sw=2.0))
    p.append(text((x_dac + w_dac/2 + x_lpf - w_lpf/2)/2, y_main - 12, "Східчастий sin", size=10, color=DAC))

    # LPF to Output
    p.append(arrow(x_lpf + w_lpf/2, y_main, x_out, y_main, color=VCO, sw=2.2))
    p.append(text(x_out - 10, y_main - 12, "Аналоговий sin(2π·f_out·t)", size=11, color=VCO, bold=True, anchor="end"))

    # Formula box
    eb, ew, eh = textbox(W / 2, 295,
                         "Розрахунок вихідної частоти:  f_out = (FTW · f_clk) / 2ᴺ\n"
                         "Роздільна здатність: Δf = f_clk / 2ᴺ (для N = 32 біт та f_clk = 100 МГц: Δf ≈ 0.023 Гц)",
                         size=12, bold=True, fill="#ffffff", stroke=LINE, min_w=580)
    p.append(eb)

    render(os.path.join(OUT, "direct-digital-synthesis-dds.svg"), W, H, *p,
           title="Прямий цифровий синтез DDS")


# ── Fig 4: Phase Noise Profile & Loop Filter Crossover ───────────────────────
def fig_phase_noise_profile():
    W, H = 780, 390
    ax, ay = 80, 290
    axw = 640
    p = []

    tb, tw, th = textbox(W / 2, 40,
                         "Спектральний профіль фазового шуму ФАПЧ-синтезатора L(Δf)",
                         size=14, bold=True, fill="#f8f9fa", stroke="#bdc3c7", min_w=580)
    p.append(tb)

    # Axes
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 20, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 8, ay + 5, "Δf (відбудова, логарифмічна шкала)", size=12, color=INK, bold=True, anchor="start"))

    p.append(line(ax, ay, ax, ay - 210, color=INK, sw=1.6))
    p.append(arrow(ax, ay - 190, ax, ay - 210, color=INK, sw=1.6))
    p.append(text(ax - 10, ay - 218, "L(Δf) [дБн/Гц]", size=12, color=INK, bold=True, anchor="middle"))

    # Critical points
    x_inband = ax + 50
    x_fc     = ax + 300  # Loop bandwidth corner
    x_vco    = ax + 550

    y_inband = ay - 130  # Flat in-band noise floor

    # Draw VCO open-loop noise curve (dashed green)
    vco_path = f"M {ax + 50} {ay - 210} L {x_fc} {ay - 140} L {ax + 580} {ay - 30}"
    p.append(f'<path d="{vco_path}" fill="none" stroke="{VCO}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    p.append(text(ax + 500, ay - 70, "Власний шум VCO (відкрита петля)", size=11, color=VCO, italic=True))

    # Draw Reference / In-band Noise (dashed blue)
    ref_path = f"M {ax + 30} {y_inband} L {x_fc} {y_inband} L {ax + 500} {ay - 10}"
    p.append(f'<path d="{ref_path}" fill="none" stroke="{CLK}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    p.append(text(ax + 140, y_inband - 12, "Внутрішньосмуговий шум ФАПЧ (PFD + N)", size=11, color=CLK, italic=True))

    # Total closed-loop phase noise curve (solid orange/red line)
    total_path = (
        f"M {ax + 30} {y_inband} "
        f"L {x_fc - 30} {y_inband} "
        f"Q {x_fc} {y_inband}, {x_fc + 30} {y_inband + 20} "
        f"L {ax + 550} {ay - 35} "
        f"L {ax + 600} {ay - 30}"
    )
    p.append(f'<path d="{total_path}" fill="none" stroke="{NOISE}" stroke-width="3.0"/>')

    # Mark Loop Bandwidth f_c
    p.append(line(x_fc, ay, x_fc, ay - 200, color=MUTED, sw=1.2, dash="3 3"))
    p.append(circle(x_fc, y_inband, 5, fill=NOISE, stroke=INK))
    p.append(text(x_fc, ay + 20, "f_c (Смуга петлі LF)", size=12, color=INK, bold=True))

    # Callouts
    p.append(text(ax + 120, y_inband + 25, "1) Зона придушення шуму VCO\n(домінує шум PFD · N)", size=11, color=CLK, bold=True))
    p.append(text(ax + 420, ay - 110, "2) За смугою f_c домінує\nвласний шум VCO (-20 дБ/дек)", size=11, color=VCO, bold=True))

    # Grid ticks
    p.append(tick(ax + 80, ay, "100 Гц", up=False))
    p.append(tick(ax + 200, ay, "10 кГц", up=False))
    p.append(tick(x_fc, ay, "f_c (100 кГц)", up=False))
    p.append(tick(ax + 450, ay, "1 МГц", up=False))
    p.append(tick(ax + 580, ay, "10 МГц", up=False))

    render(os.path.join(OUT, "synthesizer-phase-noise-profile.svg"), W, H, *p,
           title="Спектральний профіль фазового шуму ФАПЧ-синтезатора")


# ── Fig 5: Hybrid DDS + PLL Synthesizer Architecture ────────────────────────
def fig_hybrid_dds_pll():
    W, H = 840, 350
    p = []

    tb, tw, th = textbox(W / 2, 40,
                         "Гібридна топологія: DDS як високочастотна опора для ФАПЧ-помножувача",
                         size=14, bold=True, fill="#f8f9fa", stroke="#bdc3c7", min_w=620)
    p.append(tb)

    y_main = 150

    x_ref = 80
    x_dds = 220
    x_lpf = 370
    x_pll = 540
    x_out = 760

    # Blocks
    b_ref, w_ref, h_ref = textbox(x_ref, y_main, "Опорний\nкварц / TCXO\nf_osc", size=12, fill="#ebf5fb", stroke=CLK, bold=True, min_w=90)
    p.append(b_ref)

    b_dds, w_dds, h_dds = textbox(x_dds, y_main, "Ядро DDS\n(субгерцовий\nкрок)", size=12, fill="#f4ecf7", stroke=PFD, bold=True, min_w=110)
    p.append(b_dds)

    b_lpf, w_lpf, h_lpf = textbox(x_lpf, y_main, "ФНЧ + ЦАП\n(очищення\nDDS)", size=12, fill="#e8f8f5", stroke=DAC, bold=True, min_w=100)
    p.append(b_lpf)

    b_pll, w_pll, h_pll = textbox(x_pll, y_main, "Синтезатор ФАПЧ (PLL)\n(помножувач частоти ×N\nдо надвисоких ГГц)", size=12, fill="#fef9e7", stroke=VCO, bold=True, min_w=170)
    p.append(b_pll)

    # Connections
    p.append(arrow(x_ref + w_ref/2, y_main, x_dds - w_dds/2, y_main, color=CLK, sw=2.0))
    p.append(text((x_ref + w_ref/2 + x_dds - w_dds/2)/2, y_main - 12, "f_clk", size=11, color=CLK))

    p.append(arrow(x_dds + w_dds/2, y_main, x_lpf - w_lpf/2, y_main, color=PFD, sw=2.0))

    p.append(arrow(x_lpf + w_lpf/2, y_main, x_pll - w_pll/2, y_main, color=DAC, sw=2.0))
    p.append(text((x_lpf + w_lpf/2 + x_pll - w_pll/2)/2, y_main - 12, "f_dds (гнучка опора)", size=11, color=DAC, bold=True))

    p.append(arrow(x_pll + w_pll/2, y_main, x_out, y_main, color=VCO, sw=2.2))
    p.append(text(x_out - 10, y_main - 12, "f_out = N · f_dds", size=12, color=VCO, bold=True, anchor="end"))

    # Highlights
    b_h1, wh1, hh1 = textbox(220, 270, "Переваги DDS:\n- Крок < 0.001 Гц\n- Наносекундна швидкість", size=11, fill="#f4ecf7", stroke=PFD, min_w=180)
    p.append(b_h1)

    b_h2, wh2, hh2 = textbox(540, 270, "Переваги PLL:\n- Робота на 1–20+ ГГц\n- Придушення супутніх завад DDS", size=11, fill="#fef9e7", stroke=VCO, min_w=220)
    p.append(b_h2)

    p.append(arrow(220, 240, 220, y_main + h_dds/2, color=PFD, sw=1.5))
    p.append(arrow(540, 240, 540, y_main + h_pll/2, color=VCO, sw=1.5))

    render(os.path.join(OUT, "hybrid-dds-pll-architecture.svg"), W, H, *p,
           title="Гібридний синтезатор DDS + PLL")

if __name__ == "__main__":
    fig_pll_block_diagram()
    fig_fractional_n_sdm()
    fig_dds_architecture()
    fig_phase_noise_profile()
    fig_hybrid_dds_pll()
    print("All 5 figures generated successfully!")
