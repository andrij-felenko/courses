# -*- coding: utf-8 -*-
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def make_spectrum_dsb():
    w, h = 760, 420
    elements = []
    
    elements.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    
    pw, ph = 680, 105
    px1, py1 = 40, 25
    elements.append(rect(px1, py1, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px1 + 15, py1 + 20, "1. Низькочастотний спектр повідомлення M(f)", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y = py1 + 80
    elements.append(line(px1 + 50, ax_y, px1 + 630, ax_y, color="#64748b", sw=1.5))
    elements.append(arrow(px1 + 620, ax_y, px1 + 645, ax_y, color="#64748b", sw=1.5))
    elements.append(text(px1 + 655, ax_y + 4, "f", size=12, bold=True, anchor="start", color="#475569"))
    
    cx1 = px1 + 340
    elements.append(line(cx1, ax_y, cx1, py1 + 35, color="#94a3b8", sw=1, dash="3,3"))
    elements.append(text(cx1, ax_y + 16, "0", size=11, color="#475569"))
    
    tri1_pts = "%f,%f %f,%f %f,%f" % (cx1 - 80, ax_y, cx1, py1 + 35, cx1 + 80, ax_y)
    elements.append('<polygon points="%s" fill="#2457d6" fill-opacity="0.25" stroke="#2457d6" stroke-width="2"/>' % tri1_pts)
    elements.append(text(cx1 - 85, ax_y + 16, "−B_m", size=10, color="#475569"))
    elements.append(text(cx1 + 85, ax_y + 16, "+B_m", size=10, color="#475569"))
    elements.append(text(cx1 + 20, py1 + 45, "M(f)", size=11, bold=True, color="#2457d6"))
    
    px2, py2 = 40, 155
    elements.append(rect(px2, py2, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px2 + 15, py2 + 20, "2. Спектр стандартної AM (DSB-LC) — несуча споживає 67%+ потужності", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y2 = py2 + 80
    elements.append(line(px2 + 50, ax_y2, px2 + 630, ax_y2, color="#64748b", sw=1.5))
    elements.append(arrow(px2 + 620, ax_y2, px2 + 645, ax_y2, color="#64748b", sw=1.5))
    elements.append(text(px2 + 655, ax_y2 + 4, "f", size=12, bold=True, anchor="start", color="#475569"))
    
    fc2 = px2 + 340
    elements.append(arrow(fc2, ax_y2, fc2, py2 + 30, color="#c0392b", sw=2.5))
    elements.append(text(fc2 + 50, py2 + 30, "Несуча f_c (A)", size=10, bold=True, color="#c0392b"))
    elements.append(text(fc2, ax_y2 + 16, "f_c", size=11, bold=True, color="#1e293b"))
    
    lsb2_pts = "%f,%f %f,%f %f,%f" % (fc2 - 100, ax_y2, fc2, py2 + 42, fc2, ax_y2)
    usb2_pts = "%f,%f %f,%f %f,%f" % (fc2, ax_y2, fc2, py2 + 42, fc2 + 100, ax_y2)
    elements.append('<polygon points="%s" fill="#27ae60" fill-opacity="0.25" stroke="#27ae60" stroke-width="1.8"/>' % lsb2_pts)
    elements.append('<polygon points="%s" fill="#2457d6" fill-opacity="0.25" stroke="#2457d6" stroke-width="1.8"/>' % usb2_pts)
    elements.append(text(fc2 - 30, py2 + 62, "LSB", size=10, bold=True, color="#27ae60"))
    elements.append(text(fc2 + 30, py2 + 62, "USB", size=10, bold=True, color="#2457d6"))
    elements.append(text(fc2 - 100, ax_y2 + 16, "f_c−B_m", size=10, color="#475569"))
    elements.append(text(fc2 + 100, ax_y2 + 16, "f_c+B_m", size=10, color="#475569"))

    px3, py3 = 40, 285
    elements.append(rect(px3, py3, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px3 + 15, py3 + 20, "3. Спектр DSB-SC — несуча пригнічена (0 Вт), 100% потужності у бічних смугах", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y3 = py3 + 80
    elements.append(line(px3 + 50, ax_y3, px3 + 630, ax_y3, color="#64748b", sw=1.5))
    elements.append(arrow(px3 + 620, ax_y3, px3 + 645, ax_y3, color="#64748b", sw=1.5))
    elements.append(text(px3 + 655, ax_y3 + 4, "f", size=12, bold=True, anchor="start", color="#475569"))
    
    fc3 = px3 + 340
    elements.append(line(fc3, ax_y3, fc3, py3 + 35, color="#c0392b", sw=1.5, dash="3,3"))
    elements.append(text(fc3 + 55, py3 + 32, "Пригнічена несуча (0)", size=10, italic=True, color="#c0392b"))
    elements.append(text(fc3, ax_y3 + 16, "f_c", size=11, bold=True, color="#1e293b"))
    
    lsb3_pts = "%f,%f %f,%f %f,%f" % (fc3 - 100, ax_y3, fc3, py3 + 40, fc3, ax_y3)
    usb3_pts = "%f,%f %f,%f %f,%f" % (fc3, ax_y3, fc3, py3 + 40, fc3 + 100, ax_y3)
    elements.append('<polygon points="%s" fill="#27ae60" fill-opacity="0.35" stroke="#27ae60" stroke-width="2"/>' % lsb3_pts)
    elements.append('<polygon points="%s" fill="#2457d6" fill-opacity="0.35" stroke="#2457d6" stroke-width="2"/>' % usb3_pts)
    elements.append(text(fc3 - 30, py3 + 62, "LSB", size=10, bold=True, color="#27ae60"))
    elements.append(text(fc3 + 30, py3 + 62, "USB", size=10, bold=True, color="#2457d6"))
    elements.append(text(fc3 - 100, ax_y3 + 16, "f_c−B_m", size=10, color="#475569"))
    elements.append(text(fc3 + 100, ax_y3 + 16, "f_c+B_m", size=10, color="#475569"))

    content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (w, h, w, h)
    content += '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    content += '<path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker></defs>\n'
    content += "\n".join(elements)
    content += '\n</svg>'
    
    with open(os.path.join(IMG_DIR, 'spectrum-dsb.svg'), 'w', encoding='utf-8') as f:
        f.write(content)

def make_waveforms_dsb():
    w, h = 760, 420
    elements = []
    
    elements.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    
    pw, ph = 680, 115
    px = 40
    
    py1 = 15
    elements.append(rect(px, py1, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px + 15, py1 + 20, "1. Інформаційне повідомлення m(t)", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y1 = py1 + 65
    elements.append(line(px + 40, ax_y1, px + 620, ax_y1, color="#94a3b8", sw=1, dash="4,4"))
    
    pts_m = []
    num_pts = 300
    x_start, x_end = px + 50, px + 620
    dx = (x_end - x_start) / num_pts
    for i in range(num_pts + 1):
        x = x_start + i * dx
        t = (i / num_pts) * 2 * math.pi
        val = math.sin(t)
        y = ax_y1 - val * 35
        pts_m.append("%.1f,%.1f" % (x, y))
    
    elements.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.2"/>' % (" ".join(pts_m)))
    x_zero = x_start + (num_pts / 2) * dx
    elements.append(line(x_zero, py1 + 35, x_zero, py1 + 105, color="#c0392b", sw=1.5, dash="3,3"))
    elements.append(text(px + 520, py1 + 20, "Перехід через 0", size=10, bold=True, anchor="start", color="#c0392b"))
    
    py2 = 145
    elements.append(rect(px, py2, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px + 15, py2 + 20, "2. Високочастотна несуча cos(ω_c t)", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y2 = py2 + 65
    elements.append(line(px + 40, ax_y2, px + 620, ax_y2, color="#94a3b8", sw=1, dash="4,4"))
    
    pts_c = []
    for i in range(num_pts + 1):
        x = x_start + i * dx
        t = (i / num_pts) * 2 * math.pi
        val = math.cos(24 * t)
        y = ax_y2 - val * 30
        pts_c.append("%.1f,%.1f" % (x, y))
    elements.append('<polyline points="%s" fill="none" stroke="#64748b" stroke-width="1.2"/>' % (" ".join(pts_c)))
    elements.append(line(x_zero, py2 + 25, x_zero, py2 + 105, color="#c0392b", sw=1.5, dash="3,3"))

    py3 = 275
    elements.append(rect(px, py3, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(px + 15, py3 + 20, "3. Сигнал DSB-SC s(t) = m(t)·cos(ω_c t)", size=12, bold=True, anchor="start", color="#1e293b"))
    ax_y3 = py3 + 65
    elements.append(line(px + 40, ax_y3, px + 620, ax_y3, color="#94a3b8", sw=1, dash="4,4"))
    
    pts_s = []
    pts_env_pos = []
    pts_env_neg = []
    for i in range(num_pts + 1):
        x = x_start + i * dx
        t = (i / num_pts) * 2 * math.pi
        m_t = math.sin(t)
        c_t = math.cos(24 * t)
        val = m_t * c_t
        y = ax_y3 - val * 35
        pts_s.append("%.1f,%.1f" % (x, y))
        
        env = abs(m_t)
        pts_env_pos.append("%.1f,%.1f" % (x, ax_y3 - env * 35))
        pts_env_neg.append("%.1f,%.1f" % (x, ax_y3 + env * 35))

    elements.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(pts_env_pos)))
    elements.append('<polyline points="%s" fill="none" stroke="#27ae60" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(pts_env_neg)))
    elements.append('<polyline points="%s" fill="none" stroke="#c0392b" stroke-width="2.0"/>' % (" ".join(pts_s)))
    
    elements.append(line(x_zero, py3 + 25, x_zero, py3 + 105, color="#c0392b", sw=1.8, dash="3,3"))
    elements.append(text(px + 480, py3 + 20, "Стрибок фази на 180°", size=10, bold=True, anchor="start", color="#c0392b"))
    elements.append(text(px + 625, ax_y3 - 20, "|m(t)|", size=11, bold=True, anchor="start", color="#27ae60"))

    content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (w, h, w, h)
    content += "\n".join(elements)
    content += '\n</svg>'
    
    with open(os.path.join(IMG_DIR, 'waveforms-dsb.svg'), 'w', encoding='utf-8') as f:
        f.write(content)

def make_ring_modulator():
    w, h = 760, 420
    elements = []
    
    elements.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    
    elements.append(rect(20, 20, 720, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(40, 45, "Схема кільцевого модулятора (Cowan Ring Modulator)", size=14, bold=True, anchor="start", color="#1e293b"))
    
    elements.append(text(70, 85, "Вхід m(t)", size=12, bold=True, anchor="middle", color="#2457d6"))
    elements.append(line(70, 95, 70, 115, color="#2457d6", sw=2))
    elements.append(textbox(70, 135, "m(t)\nсигнал", size=11, fill="#e0e7ff", stroke="#2457d6")[0])
    elements.append(line(70, 155, 70, 290, color="#2457d6", sw=2))

    elements.append(line(120, 160, 120, 240, color="#1e293b", sw=2.5))
    elements.append(line(126, 160, 126, 240, color="#64748b", sw=1.5, dash="2,2"))
    elements.append(line(132, 160, 132, 240, color="#1e293b", sw=2.5))
    
    elements.append(line(132, 160, 210, 160, color="#1e293b", sw=2))
    elements.append(line(132, 240, 210, 240, color="#1e293b", sw=2))
    elements.append(circle(132, 200, 3, fill="#1e293b", stroke="#1e293b"))
    elements.append(line(132, 200, 180, 200, color="#c0392b", sw=2))
    elements.append(text(120, 260, "Трансформатор T1", size=10, bold=True, color="#475569"))

    elements.append(line(620, 160, 540, 160, color="#1e293b", sw=2))
    elements.append(line(620, 240, 540, 240, color="#1e293b", sw=2))
    elements.append(line(620, 160, 620, 240, color="#1e293b", sw=2.5))
    elements.append(line(626, 160, 626, 240, color="#64748b", sw=1.5, dash="2,2"))
    elements.append(line(632, 160, 632, 240, color="#1e293b", sw=2.5))
    
    elements.append(circle(620, 200, 3, fill="#1e293b", stroke="#1e293b"))
    elements.append(line(620, 200, 580, 200, color="#c0392b", sw=2))
    elements.append(line(580, 200, 580, 340, color="#c0392b", sw=2))
    elements.append(line(180, 200, 180, 340, color="#c0392b", sw=2))
    
    elements.append(line(180, 340, 310, 340, color="#c0392b", sw=2))
    elements.append(line(450, 340, 580, 340, color="#c0392b", sw=2))
    elements.append(textbox(380, 340, "Генератор несучої\nc(t) = cos(ω_c t)", size=11, fill="#fee2e2", stroke="#c0392b", bold=True)[0])
    
    elements.append(line(632, 160, 670, 160, color="#27ae60", sw=2))
    elements.append(line(632, 240, 670, 240, color="#27ae60", sw=2))
    elements.append(textbox(685, 200, "Вихід DSB-SC\ns(t)", size=10, fill="#dcfce7", stroke="#27ae60", bold=True)[0])
    elements.append(text(620, 260, "Трансформатор T2", size=10, bold=True, color="#475569"))

    elements.append(line(210, 160, 300, 200, color="#1e293b", sw=2))
    elements.append(line(210, 240, 300, 200, color="#1e293b", sw=2))
    
    elements.append(line(540, 160, 460, 200, color="#1e293b", sw=2))
    elements.append(line(540, 240, 460, 200, color="#1e293b", sw=2))

    nx_top, ny_top = 380, 140
    nx_bot, ny_bot = 380, 260
    nx_left, ny_left = 300, 200
    nx_right, ny_right = 460, 200
    
    elements.append(circle(nx_top, ny_top, 4, fill="#1e293b", stroke="#1e293b"))
    elements.append(circle(nx_bot, ny_bot, 4, fill="#1e293b", stroke="#1e293b"))
    elements.append(circle(nx_left, ny_left, 4, fill="#1e293b", stroke="#1e293b"))
    elements.append(circle(nx_right, ny_right, 4, fill="#1e293b", stroke="#1e293b"))

    elements.append(line(nx_left, ny_left, nx_top, ny_top, color="#0f766e", sw=2))
    elements.append(textbox(330, 160, "D1", size=10, fill="#ccfbf1", stroke="#0f766e", bold=True)[0])
    
    elements.append(line(nx_top, ny_top, nx_right, ny_right, color="#0f766e", sw=2))
    elements.append(textbox(430, 160, "D2", size=10, fill="#ccfbf1", stroke="#0f766e", bold=True)[0])
    
    elements.append(line(nx_right, ny_right, nx_bot, ny_bot, color="#0f766e", sw=2))
    elements.append(textbox(430, 240, "D3", size=10, fill="#ccfbf1", stroke="#0f766e", bold=True)[0])

    elements.append(line(nx_bot, ny_bot, nx_left, ny_left, color="#0f766e", sw=2))
    elements.append(textbox(330, 240, "D4", size=10, fill="#ccfbf1", stroke="#0f766e", bold=True)[0])

    elements.append(text(380, 80, "Кільцеве перемикання діодів D1-D4", size=11, bold=True, color="#0f766e"))

    content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (w, h, w, h)
    content += "\n".join(elements)
    content += '\n</svg>'
    
    with open(os.path.join(IMG_DIR, 'ring-modulator.svg'), 'w', encoding='utf-8') as f:
        f.write(content)

def make_costas_loop():
    w, h = 760, 440
    elements = []
    
    elements.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0))
    
    elements.append(rect(20, 20, 720, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1))
    elements.append(text(40, 45, "Структурна схема петлі Костаса (Costas Loop)", size=14, bold=True, anchor="start", color="#1e293b"))

    elements.append(textbox(75, 200, "Вхід DSB-SC\ns(t)", size=11, fill="#e0e7ff", stroke="#2457d6", bold=True)[0])
    elements.append(arrow(120, 200, 160, 200, color="#2457d6", sw=2))
    elements.append(circle(160, 200, 4, fill="#1e293b", stroke="#1e293b"))
    
    elements.append(line(160, 200, 160, 110, color="#1e293b", sw=2))
    elements.append(line(160, 200, 160, 290, color="#1e293b", sw=2))
    
    elements.append(arrow(160, 110, 220, 110, color="#1e293b", sw=2))
    elements.append(textbox(240, 110, "×", size=16, fill="#ffffff", stroke="#1e293b", bold=True, min_w=35)[0])
    elements.append(text(240, 80, "Змішувач I", size=10, bold=True, color="#475569"))
    elements.append(arrow(260, 110, 330, 110, color="#1e293b", sw=2))
    elements.append(textbox(380, 110, "ФНЧ I", size=11, fill="#dcfce7", stroke="#27ae60", bold=True, min_w=65)[0])
    elements.append(arrow(420, 110, 490, 110, color="#27ae60", sw=2))
    elements.append(circle(490, 110, 4, fill="#27ae60", stroke="#27ae60"))
    elements.append(arrow(490, 110, 610, 110, color="#27ae60", sw=2))
    elements.append(textbox(665, 110, "Вихід аудіо\nm(t) ∝ ½m(t)cos(ϕ)", size=10, fill="#dcfce7", stroke="#27ae60", bold=True)[0])
    
    elements.append(arrow(160, 290, 220, 290, color="#1e293b", sw=2))
    elements.append(textbox(240, 290, "×", size=16, fill="#ffffff", stroke="#1e293b", bold=True, min_w=35)[0])
    elements.append(text(240, 320, "Змішувач Q", size=10, bold=True, color="#475569"))
    elements.append(arrow(260, 290, 330, 290, color="#1e293b", sw=2))
    elements.append(textbox(380, 290, "ФНЧ Q", size=11, fill="#dcfce7", stroke="#27ae60", bold=True, min_w=65)[0])
    elements.append(arrow(420, 290, 490, 290, color="#27ae60", sw=2))
    elements.append(circle(490, 290, 4, fill="#27ae60", stroke="#27ae60"))

    elements.append(line(490, 110, 490, 175, color="#1e293b", sw=2))
    elements.append(line(490, 290, 490, 225, color="#1e293b", sw=2))
    elements.append(arrow(490, 175, 490, 180, color="#1e293b", sw=2))
    elements.append(arrow(490, 225, 490, 220, color="#1e293b", sw=2))
    elements.append(textbox(490, 200, "×", size=16, fill="#fee2e2", stroke="#c0392b", bold=True, min_w=35)[0])
    elements.append(text(585, 200, "Фазовий детектор (I·Q)", size=10, bold=True, anchor="start", color="#c0392b"))

    elements.append(line(490, 220, 490, 360, color="#c0392b", sw=2))
    elements.append(arrow(490, 360, 430, 360, color="#c0392b", sw=2))
    elements.append(textbox(370, 360, "Петльовий фільтр F(s)", size=10, fill="#fef3c7", stroke="#d97706", bold=True, min_w=100)[0])
    elements.append(arrow(315, 360, 230, 360, color="#d97706", sw=2))
    
    elements.append(textbox(170, 360, "Керований генератор\nVCO / NCO", size=10, fill="#e0e7ff", stroke="#2457d6", bold=True, min_w=100)[0])
    
    elements.append(line(170, 310, 170, 250, color="#2457d6", sw=2))
    elements.append(line(170, 250, 240, 250, color="#2457d6", sw=2))
    elements.append(arrow(240, 250, 240, 130, color="#2457d6", sw=2))
    elements.append(text(125, 170, "cos(ω_c t+ϕ)", size=10, bold=True, color="#2457d6"))

    elements.append(arrow(215, 310, 240, 310, color="#2457d6", sw=2))
    elements.append(text(215, 275, "−90° [sin]", size=9, bold=True, color="#2457d6"))

    content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (w, h, w, h)
    content += "\n".join(elements)
    content += '\n</svg>'
    
    with open(os.path.join(IMG_DIR, 'spectrum-dsb.svg'), 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    make_spectrum_dsb()
    make_waveforms_dsb()
    make_ring_modulator()
    make_costas_loop()
    print("SVGs updated!")
