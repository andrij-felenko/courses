# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/communications/measurements/rssi-signal-strength
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import *

def make_fig1():
    """Порівняння обхвату RSSI та RSRP у частотно-часовій ґратці OFDM."""
    w, h = 760, 400
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Title / Header text
    out.append(text(w/2, 25, "OFDM-структура ресурсної сітки (Час × Частота)", size=16, bold=True))
    
    # Frame for OFDM Grid
    gx, gy, gw, gh = 150, 60, 300, 280
    out.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=4))
    
    # Axes labels
    out.append(text(gx + gw/2, gy + gh + 25, "Часові символи OFDM →", size=13, color=MUTED, bold=True))
    out.append(text(gx - 15, gy + gh/2, "Піднесучі ↑", size=12, color=MUTED, anchor="end", bold=True))
    
    # Draw Subcarriers & Symbols grid
    rows = 7
    cols = 6
    cell_w = gw / cols
    cell_h = gh / rows
    
    # Reference Signals (CRS) locations: e.g. (row 1, col 0), (row 5, col 0), (row 3, col 3) etc.
    rs_cells = {(1, 0), (5, 0), (3, 3), (1, 5), (5, 5)}
    
    for r in range(rows):
        for c in range(cols):
            cx = gx + c * cell_w
            cy = gy + r * cell_h
            if (r, c) in rs_cells:
                # Highlighted Reference Signal element (RSRP measure target)
                out.append(rect(cx + 2, cy + 2, cell_w - 4, cell_h - 4, fill="#27ae60", stroke="#1e8449", sw=1.5, rx=3))
                out.append(text(cx + cell_w/2, cy + cell_h/2 + 4, "RS", size=11, color="#ffffff", bold=True))
            else:
                # Regular data element (contributes to RSSI, but ignored by RSRP)
                out.append(rect(cx + 2, cy + 2, cell_w - 4, cell_h - 4, fill="#ebf5fb", stroke="#aed6f1", sw=1, rx=3))
                if (r + c) % 3 == 0:
                    out.append(text(cx + cell_w/2, cy + cell_h/2 + 4, "Data", size=10, color="#7f8c8d"))
                elif (r + c) % 3 == 1:
                    out.append(text(cx + cell_w/2, cy + cell_h/2 + 4, "Noise", size=10, color="#e74c3c"))
                else:
                    out.append(text(cx + cell_w/2, cy + cell_h/2 + 4, "Interf", size=10, color="#d35400"))

    # Legend / Right Panel
    px = 470
    py = 60
    pw = 260
    ph = 280
    out.append(rect(px, py, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    
    out.append(text(px + pw/2, py + 25, "Зони вимірювання", size=15, bold=True))
    
    # RSSI box in legend
    out.append(rect(px + 15, py + 45, 230, 95, fill="#fef9e7", stroke="#f1c40f", sw=1.5, rx=4))
    out.append(text(px + 125, py + 65, "RSSI (Широкосмугова)", size=13, color="#b7950b", bold=True))
    out.append(text(px + 125, py + 85, "Сумарна енергія ВСІХ осередків:", size=11, color=INK))
    out.append(text(px + 125, py + 102, "RS + Data + Noise + Interf", size=11, color=POS, bold=True))
    out.append(text(px + 125, py + 122, "(Включає завади сусідам)", size=10, color=MUTED, italic=True))
    
    # RSRP box in legend
    out.append(rect(px + 15, py + 155, 230, 95, fill="#eafaf1", stroke="#27ae60", sw=1.5, rx=4))
    out.append(text(px + 125, py + 175, "RSRP (Вузькосмугова)", size=13, color="#1e8449", bold=True))
    out.append(text(px + 125, py + 195, "Енергія ЛИШЕ пилотажних RS:", size=11, color=INK))
    out.append(text(px + 125, py + 212, "Усереднена потужність RS", size=11, color=FIELD, bold=True))
    out.append(text(px + 125, py + 232, "(Очищено від трафіку соти)", size=10, color=MUTED, italic=True))

    out.append('</svg>')
    return "\n".join(out)

def make_fig2():
    """Взаємозв'язок метрик радіоканалу та їхній вплив на рішення модема."""
    w, h = 760, 360
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w/2, 25, "Ієрархія радіометричних оцінок LTE/5G", size=16, bold=True))

    # Top Level: Primary Input Signal
    b1, w1, h1 = textbox(380, 65, "Прийнятий радіочастотний сигнал (Смуга B)", size=14, fill="#e8f8f5", stroke="#1abc9c", bold=True)
    out.append(b1)

    # Level 2: RSSI and RSRP
    b_rssi, w_rssi, h_rssi = textbox(200, 150, "RSSI (дБм)\nЗагальна енергія смуги", size=12, fill="#fef9e7", stroke="#f1c40f", bold=True)
    b_rsrp, w_rsrp, h_rsrp = textbox(560, 150, "RSRP (дБм)\nПотужність одного RS", size=12, fill="#eafaf1", stroke="#27ae60", bold=True)
    out.append(b_rssi)
    out.append(b_rsrp)

    out.append(arrow(320, 85, 220, 125, color=LINE))
    out.append(arrow(440, 85, 540, 125, color=LINE))

    # Level 3: Derived Metrics RSRQ & SINR
    b_rsrq, w_rsrq, h_rsrq = textbox(380, 230, "RSRQ = N · RSRP / RSSI\nЯкість відносно навантаження (дБ)", size=12, fill="#ebf5fb", stroke="#3498db", bold=True)
    b_sinr, w_sinr, h_sinr = textbox(630, 230, "SINR (дБ)\nСигнал / (Шум + Завада)", size=12, fill="#f4ecf7", stroke="#9b59b6", bold=True)
    out.append(b_rsrq)
    out.append(b_sinr)

    out.append(arrow(220, 175, 330, 210, color=LINE))
    out.append(arrow(540, 175, 430, 210, color=LINE))
    out.append(arrow(580, 175, 630, 210, color=LINE))

    # Bottom Level: Actions / Outputs
    b_act1, _, _ = textbox(200, 310, "Рішення про Handover\n(Вибір базової станції)", size=12, fill="#fdedec", stroke="#e74c3c", bold=True)
    b_act2, _, _ = textbox(560, 310, "Адаптація AMC & CQI\n(Вибір QPSK ... 256QAM)", size=12, fill="#eaeded", stroke="#7f8c8d", bold=True)
    out.append(b_act1)
    out.append(b_act2)

    out.append(arrow(340, 250, 240, 290, color=LINE))
    out.append(arrow(420, 250, 520, 290, color=LINE))
    out.append(arrow(630, 250, 600, 290, color=LINE))

    out.append('</svg>')
    return "\n".join(out)

if __name__ == '__main__':
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    with open(os.path.join(img_dir, 'rssi-vs-rsrp-spectrum.svg'), 'w', encoding='utf-8') as f:
        f.write(make_fig1())
        
    with open(os.path.join(img_dir, 'signal-metrics-tree.svg'), 'w', encoding='utf-8') as f:
        f.write(make_fig2())

    print("Figures generated successfully.")
