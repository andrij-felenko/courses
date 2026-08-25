# -*- coding: utf-8 -*-
import sys
import os
import math

# Four levels up to reach scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_osd_waveform(path):
    w, h = 800, 420
    out = []
    
    # Title
    out.append(text(w/2, 28, "Осцилограма накладання OSD-пікселів на відеорядок PAL (64 мкс)", size=15, bold=True, color="#1a1a1a"))
    
    # Voltage levels grid (Y axis)
    def yv(v):
        return 340.0 - v * 250.0

    # Grid horizontal lines
    levels = [
        (1.0, "1.0 В (Рівень білого)", "#27ae60", "--"),
        (0.7, "0.7 В (Сірий рівень)", "#6b7280", ":"),
        (0.3, "0.3 В (Рівень чорного / гасіння)", "#1a1a1a", "--"),
        (0.0, "0.0 В (Синхроімпульс HSYNC)", "#c0392b", "-.")
    ]
    
    x_start = 90
    x_end = 760
    
    for val, label, col, dstyle in levels:
        yp = yv(val)
        out.append(line(x_start, yp, x_end, yp, color=col, sw=1, dash="4,4" if dstyle=="--" else ("2,2" if dstyle==":" else None)))
        out.append(text(x_start - 8, yp + 4, label, size=11, color=col, anchor="end", bold=(val in [0.0, 0.3, 1.0])))

    # X axis: Time (µs)
    def xt(t_us):
        return x_start + (t_us / 64.0) * (x_end - x_start)

    # Time markers
    t_ticks = [
        (0.0, "0"),
        (4.7, "4.7"),
        (10.5, "10.5"),
        (25.0, "25.0"),
        (45.0, "45.0"),
        (62.5, "62.5"),
        (64.0, "64.0 мкс")
    ]
    
    for tt, tl in t_ticks:
        xp = xt(tt)
        out.append(line(xp, 340, xp, 348, color="#6b7280", sw=1.2))
        out.append(text(xp, 365, tl, size=11, color="#6b7280", anchor="middle"))

    out.append(line(x_start, 340, x_end, 340, color="#1a1a1a", sw=1.5))
    out.append(text(w/2, 395, "Час уздовж одного рядка (мікросекунди)", size=12, bold=True, color="#1a1a1a"))

    path_pts = []
    
    # 0 to 4.7: HSYNC
    path_pts.append((xt(0.0), yv(0.0)))
    path_pts.append((xt(4.7), yv(0.0)))
    path_pts.append((xt(4.7), yv(0.3)))
    
    # Back porch (4.7 to 10.5) with color burst
    path_pts.append((xt(5.3), yv(0.3)))
    
    # Color burst oscillations
    burst_steps = 16
    for i in range(burst_steps + 1):
        t = 5.3 + (7.8 - 5.3) * (i / float(burst_steps))
        v = 0.3 + 0.14 * math.sin(i * math.pi * 1.2)
        path_pts.append((xt(t), yv(v)))
        
    path_pts.append((xt(7.8), yv(0.3)))
    path_pts.append((xt(10.5), yv(0.3)))
    
    # Active video (10.5 to 22.0): camera signal
    cam1_steps = [
        (10.5, 0.45), (13.0, 0.65), (16.0, 0.40), (19.0, 0.75), (22.0, 0.50)
    ]
    for t, v in cam1_steps:
        path_pts.append((xt(t), yv(v)))
        
    # OSD Injection zone:
    path_pts.append((xt(22.0), yv(0.3)))
    path_pts.append((xt(24.0), yv(0.3)))
    path_pts.append((xt(24.0), yv(1.0)))
    path_pts.append((xt(36.0), yv(1.0)))
    path_pts.append((xt(36.0), yv(0.3)))
    path_pts.append((xt(38.0), yv(0.3)))
    
    # Resume camera video (38.0 to 62.5)
    cam2_steps = [
        (38.0, 0.55), (42.0, 0.80), (48.0, 0.45), (55.0, 0.70), (62.5, 0.35)
    ]
    for t, v in cam2_steps:
        path_pts.append((xt(t), yv(v)))
        
    # Front porch (62.5 to 64.0)
    path_pts.append((xt(62.5), yv(0.3)))
    path_pts.append((xt(64.0), yv(0.3)))
    
    pts_str = " ".join(["%.1f,%.1f" % (p[0], p[1]) for p in path_pts])
    out.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.5"/>' % pts_str)

    # Highlight regions
    out.append('<rect x="%.1f" y="70" width="%.1f" height="270" fill="#c0392b" fill-opacity="0.08" stroke="none"/>' % (xt(0), xt(4.7)-xt(0)))
    out.append(text((xt(0)+xt(4.7))/2, 56, "HSYNC", size=10, bold=True, color="#c0392b"))

    out.append('<rect x="%.1f" y="70" width="%.1f" height="270" fill="#f39c12" fill-opacity="0.10" stroke="none"/>' % (xt(4.7), xt(10.5)-xt(4.7)))
    out.append(mtext((xt(4.7)+xt(10.5))/2, 48, "Спалах кольору\n(ЗАБОРОНА OSD!)", size=9, bold=True, color="#d35400"))

    out.append(text((xt(10.5)+xt(22.0))/2, 115, "Відео камери", size=11, italic=True, color="#1a1a1a"))

    # Highlight zone rect fully containing the textbox
    out.append('<rect x="%.1f" y="70" width="%.1f" height="270" fill="#27ae60" fill-opacity="0.12" stroke="none"/>' % (xt(21.0), xt(39.0)-xt(21.0)))
    out.append(textbox((xt(22)+xt(38))/2, 135, "ВПРЕСКУВАННЯ OSD\nЧорна обводка + білий піксель", size=10, pad=4, fill="#ffffff", stroke="#27ae60", color="#27ae60", bold=True)[0])

    return render(path, w, h, "\n".join(out))

def build_osd_block_diagram(path):
    w, h = 840, 460
    out = []
    
    out.append(text(w/2, 28, "Структурна схема аналогового OSD-оверлея (накладання телеметрії)", size=15, bold=True, color="#1a1a1a"))

    b1, w1, h1 = textbox(80, 140, "Вхід CVBS\n(Камера 75 Ом)", size=11, pad=10, fill="#f4f6f8", stroke="#1a1a1a")
    b2, w2, h2 = textbox(250, 140, "Прив'язка рівня\n(DC Restorer / Clamp)\nФіксація чорного = 0.3В", size=10, pad=10, fill="#eef2ff", stroke="#2457d6")
    b3, w3, h3 = textbox(470, 140, "Швидкісний аналоговий\nперемикач (Keyer MUX)\nt_sw < 15 нс", size=10, pad=12, fill="#e6f9ed", stroke="#27ae60", bold=True)
    b4, w4, h4 = textbox(680, 140, "Підсилювач виходу\n(75 Ом Buffer Driver)\n2.0 Vp-p -> 1.0 Vp-p", size=10, pad=10, fill="#f4f6f8", stroke="#1a1a1a")

    out.extend([b1, b2, b3, b4])

    out.append(arrow(135, 140, 185, 140, color="#1a1a1a", sw=2))
    out.append(arrow(315, 140, 395, 140, color="#2457d6", sw=2))
    out.append(arrow(545, 140, 615, 140, color="#27ae60", sw=2))
    out.append(arrow(745, 140, 795, 140, color="#1a1a1a", sw=2))
    out.append(text(795, 120, "Вихід CVBS", size=11, bold=True, color="#1a1a1a", anchor="middle"))

    b5, w5, h5 = textbox(250, 300, "Синхросепаратор\n(LM1881 / Компаратор)\nВиділення HSYNC / VSYNC", size=10, pad=10, fill="#fff5f5", stroke="#c0392b")
    out.append(b5)
    out.append(arrow(250, 180, 250, 260, color="#c0392b", sw=2))
    out.append(text(255, 220, "Аналогове відео", size=10, color="#c0392b", anchor="start"))

    b6, w6, h6 = textbox(470, 300, "OSD-контролер / MCU\n(STM32 SPI DMA / MAX7456)\nГенератор пікселів + OSD RAM", size=10, pad=12, fill="#fef9e7", stroke="#f39c12", bold=True)
    out.append(b6)
    out.append(arrow(320, 300, 395, 300, color="#c0392b", sw=2))
    out.append(text(357, 285, "HSYNC / VSYNC", size=10, bold=True, color="#c0392b", anchor="middle"))

    out.append(arrow(470, 250, 470, 185, color="#27ae60", sw=2))
    out.append(text(480, 220, "Управління MUX:\n0=Відео, 1=Чорний, 2=Білий", size=9, bold=True, color="#27ae60", anchor="start"))

    b7, w7, h7 = textbox(680, 300, "Генератор опорних рівнів\nБілий = 1.0 В\nЧорний = 0.3 В", size=10, pad=10, fill="#f4f6f8", stroke="#6b7280")
    out.append(b7)
    out.append(arrow(615, 300, 545, 300, color="#6b7280", sw=1.8))
    out.append(text(580, 285, "Напруги 0.3В / 1.0В", size=10, color="#6b7280", anchor="middle"))

    out.append(line(50, 390, 790, 390, color="#e5e7eb", sw=1))
    out.append(mtext(420, 410, "Синхронізація: HSYNC запускає таймер/DMA мікроконтролера, який видає біти телеметрії точно у вікно активного рядка (10.5..62.5 мкс).\nПри втраті сигналу камери OSD-контролер автоматично генерує власні синхроімпульси (режим Stand-alone OSD).", size=11, color="#6b7280", anchor="middle"))

    return render(path, w, h, "\n".join(out))

def build_keyer_circuit(path):
    w, h = 800, 400
    out = []
    
    out.append(text(w/2, 28, "Принцип роботи аналогового ключа (Keyer) для накладання пікселів", size=15, bold=True, color="#1a1a1a"))

    b_cam, _, _ = textbox(110, 110, "Відео камери\n(CVBS in)", size=11, pad=8, fill="#f4f6f8", stroke="#1a1a1a")
    out.append(b_cam)

    out.append(line(170, 110, 210, 110, color="#1a1a1a", sw=1.8))
    out.append(line(210, 95, 210, 125, color="#1a1a1a", sw=2.5))
    out.append(line(218, 95, 218, 125, color="#1a1a1a", sw=2.5))
    out.append(text(214, 85, "C_ac 220uF", size=10, color="#6b7280", anchor="middle"))
    out.append(line(218, 110, 270, 110, color="#1a1a1a", sw=1.8))

    out.append(line(240, 110, 240, 150, color="#2457d6", sw=1.5))
    out.append(rect(225, 150, 30, 20, fill="#eef2ff", stroke="#2457d6", sw=1.5))
    out.append(text(240, 164, "Clamp", size=9, bold=True, color="#2457d6"))
    out.append(line(240, 170, 240, 190, color="#2457d6", sw=1.5))
    out.append(text(240, 205, "Опора чорного (0.3 В)", size=10, color="#2457d6"))

    b_black, _, _ = textbox(110, 190, "Рівень чорного\n(0.3 В rail)", size=10, pad=8, fill="#eef2ff", stroke="#2457d6")
    b_white, _, _ = textbox(110, 270, "Рівень білого\n(1.0 В rail)", size=10, pad=8, fill="#e6f9ed", stroke="#27ae60")
    out.extend([b_black, b_white])

    out.append(line(170, 190, 340, 190, color="#2457d6", sw=1.8))
    out.append(line(170, 270, 340, 270, color="#27ae60", sw=1.8))

    out.append(rect(340, 80, 180, 220, fill="#f4f6f8", stroke="#1a1a1a", sw=2, rx=8))
    out.append(text(430, 105, "Аналоговий MUX (3:1)", size=12, bold=True, color="#1a1a1a"))

    out.append(circle(360, 110, 4, fill="#1a1a1a", stroke="#1a1a1a"))
    out.append(text(375, 114, "0: Прозоро (Камера)", size=10, color="#1a1a1a", anchor="start"))

    out.append(circle(360, 190, 4, fill="#2457d6", stroke="#2457d6"))
    out.append(text(375, 194, "1: Чорна обводка", size=10, color="#2457d6", anchor="start"))

    out.append(circle(360, 270, 4, fill="#27ae60", stroke="#27ae60"))
    out.append(text(375, 274, "2: Білий текст", size=10, color="#27ae60", anchor="start"))

    out.append(line(480, 190, 364, 115, color="#c0392b", sw=2.5))
    out.append(circle(480, 190, 5, fill="#c0392b", stroke="#c0392b"))

    out.append(arrow(430, 360, 430, 305, color="#f39c12", sw=2))
    out.append(textbox(430, 375, "Сигнал вибору від MCU:\nOSD_SEL [1:0] (SPI / Timer)", size=10, pad=6, fill="#fef9e7", stroke="#f39c12", bold=True)[0])

    out.append(arrow(485, 190, 575, 190, color="#c0392b", sw=2))

    b_drv, _, _ = textbox(660, 190, "Вихідний буфер\n(Video Op-Amp)\nGain = +2 (75 Ом match)", size=10, pad=10, fill="#f4f6f8", stroke="#1a1a1a", bold=True)
    out.append(b_drv)

    out.append(arrow(745, 190, 790, 190, color="#1a1a1a", sw=2))
    out.append(text(790, 175, "CVBS Out (75 Ом)", size=10, bold=True, color="#1a1a1a", anchor="middle"))

    return render(path, w, h, "\n".join(out))

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    build_osd_waveform(os.path.join(img_dir, 'osd-waveform.svg'))
    build_osd_block_diagram(os.path.join(img_dir, 'osd-block-diagram.svg'))
    build_keyer_circuit(os.path.join(img_dir, 'keyer-circuit.svg'))

    print("Successfully generated 3 SVG figures in ./img/")

if __name__ == '__main__':
    main()
