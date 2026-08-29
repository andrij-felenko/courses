# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def fig_n_type():
    W, H = 760, 380
    f = []
    f.append(text(380, 30, 'Донорне легування (n-тип провідності)', size=15, bold=True))
    f.append(rect(40, 60, 680, 290, fill='#f8fafc', stroke=MUTED, rx=8))
    for i in range(4):
        for j in range(3):
            cx, cy = 120 + i*160, 110 + j*90
            is_p = (i == 2 and j == 1)
            fill_c = '#dbeafe' if not is_p else '#fee2e2'
            stroke_c = '#3b82f6' if not is_p else '#ef4444'
            label = 'Si' if not is_p else 'P'
            f.append(circle(cx, cy, 24, fill=fill_c, stroke=stroke_c, sw=2))
            f.append(text(cx, cy + 5, label, size=13, bold=True))
    f.append(circle(500, 200, 10, fill='#ef4444', stroke='#991b1b', sw=1.5))
    f.append(text(500, 204, 'e-', size=10, color='#ffffff', bold=True))
    f.append(text(500, 235, 'Вільний електрон', size=12, color='#b91c1c', bold=True))
    render(os.path.join(OUT, 'n-type.svg'), W, H, '\n'.join(f))

def fig_p_type():
    W, H = 760, 380
    f = []
    f.append(text(380, 30, 'Акцепторне легування (p-тип провідності)', size=15, bold=True))
    f.append(rect(40, 60, 680, 290, fill='#f8fafc', stroke=MUTED, rx=8))
    for i in range(4):
        for j in range(3):
            cx, cy = 120 + i*160, 110 + j*90
            is_b = (i == 2 and j == 1)
            fill_c = '#dbeafe' if not is_b else '#fef3c7'
            stroke_c = '#3b82f6' if not is_b else '#f59e0b'
            label = 'Si' if not is_b else 'B'
            f.append(circle(cx, cy, 24, fill=fill_c, stroke=stroke_c, sw=2))
            f.append(text(cx, cy + 5, label, size=13, bold=True))
    f.append(circle(500, 200, 10, fill='#ffffff', stroke='#d97706', sw=2))
    f.append(text(500, 204, 'h+', size=10, color='#b45309', bold=True))
    f.append(text(500, 235, 'Дірка (вакансія)', size=12, color='#b45309', bold=True))
    render(os.path.join(OUT, 'p-type.svg'), W, H, '\n'.join(f))

def fig_electron_hole():
    W, H = 720, 320
    f = []
    f.append(text(360, 30, 'Теплове народження пари електрон-дірка', size=15, bold=True))
    f.append(rect(40, 60, 640, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(line(80, 110, 640, 110, color='#3b82f6', sw=3))
    f.append(text(360, 95, 'Зона провідності (Ec)', size=13, color='#1d4ed8', bold=True))
    f.append(line(80, 230, 640, 230, color='#10b981', sw=3))
    f.append(text(360, 255, 'Валентна зона (Ev)', size=13, color='#047857', bold=True))
    f.append(line(360, 220, 360, 125, color='#ef4444', sw=2))
    f.append(circle(360, 110, 8, fill='#ef4444'))
    f.append(circle(360, 230, 8, fill='#ffffff', stroke='#10b981', sw=2))
    f.append(text(410, 175, 'Енергія збудження', size=12, color=MUTED))
    render(os.path.join(OUT, 'electron-hole-pair.svg'), W, H, '\n'.join(f))

def fig_hole_motion():
    W, H = 760, 280
    f = []
    f.append(text(380, 30, 'Естафетний рух дірки під дією електричного поля', size=15, bold=True))
    f.append(rect(40, 60, 680, 190, fill='#f8fafc', stroke=MUTED, rx=8))
    for i in range(5):
        cx = 100 + i*140
        f.append(circle(cx, 120, 22, fill='#dbeafe', stroke='#3b82f6', sw=2))
        f.append(text(cx, 125, 'Si', size=12, bold=True))
        if i == 1:
            f.append(circle(cx + 35, 120, 7, fill='#ffffff', stroke='#f59e0b', sw=2))
            f.append(text(cx + 35, 160, 'дірка', size=11, color='#b45309'))
        elif i == 2:
            f.append(circle(cx - 35, 120, 7, fill='#ef4444'))
            f.append(text(cx - 35, 80, 'електрон', size=11, color='#b91c1c'))
    f.append(line(50, 215, 710, 215, color='#6b7280', sw=1.5))
    f.append(text(380, 235, 'Електричне поле E (дірка праворуч, електрони ліворуч)', size=12, color=MUTED))
    render(os.path.join(OUT, 'hole-motion.svg'), W, H, '\n'.join(f))

def fig_majority_minority():
    W, H = 720, 340
    f = []
    f.append(text(360, 30, 'Основні та неосновні носії заряду', size=15, bold=True))
    f.append(rect(50, 60, 290, 240, fill='#eff6ff', stroke='#3b82f6', rx=8))
    f.append(text(195, 90, 'n-тип', size=14, bold=True, color='#1e40af'))
    f.append(text(195, 130, 'Основні: Електрони', size=12, color='#1e3a8a', bold=True))
    f.append(text(195, 160, 'Неосновні: Дірки', size=12, color='#475569'))
    f.append(rect(380, 60, 290, 240, fill='#fefce8', stroke='#eab308', rx=8))
    f.append(text(525, 90, 'p-тип', size=14, bold=True, color='#854d0e'))
    f.append(text(525, 130, 'Основні: Дірки', size=12, color='#713f12', bold=True))
    f.append(text(525, 160, 'Неосновні: Електрони', size=12, color='#475569'))
    render(os.path.join(OUT, 'majority-minority.svg'), W, H, '\n'.join(f))

def fig_doping_amount():
    W, H = 720, 320
    f = []
    f.append(text(360, 30, 'Рівні легування кремнію: від слабкого до виродженого', size=15, bold=True))
    f.append(rect(40, 60, 640, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    levels = [
        ('Власний Si', 'n_i 10^10', '1 до 5e12', '#94a3b8'),
        ('Слабке n-/p-', '10^14-10^15', '1 до 10^7', '#60a5fa'),
        ('Помірне n/p', '10^16-10^17', '1 до 10^5', '#3b82f6'),
        ('Сильне n+/p+', '10^18-10^19', '1 до 10^3', '#1d4ed8'),
        ('Вироджене', '> 10^20', '1 до 10^2', '#1e1b4b')
    ]
    for i, (name, conc, ratio, col) in enumerate(levels):
        x = 60 + i*125
        f.append(rect(x, 90, 115, 170, fill='#ffffff', stroke=col, sw=2, rx=6))
        f.append(text(x + 57, 120, name, size=11, bold=True, color=col))
        f.append(text(x + 57, 160, conc, size=10, color=INK))
        f.append(text(x + 57, 200, ratio, size=10, color=MUTED))
    render(os.path.join(OUT, 'doping-amount.svg'), W, H, '\n'.join(f))

if __name__ == '__main__':
    fig_n_type()
    fig_p_type()
    fig_electron_hole()
    fig_hole_motion()
    fig_majority_minority()
    fig_doping_amount()
