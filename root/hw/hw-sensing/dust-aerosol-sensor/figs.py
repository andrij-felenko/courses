# -*- coding: utf-8 -*-
"""Генератор векторних SVG-ілюстрацій для теми dust-aerosol-sensor."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_mie_regimes():
    w, h = 840, 360
    frags = []

    cols = [
        {'x': 150, 'title': 'Релей (d << λ)', 'sub': 'Частинки d < 0.05 мкм', 'scale': 'I ∝ d⁶ / λ⁴', 'sym': 'Симетрично вперед/назад'},
        {'x': 420, 'title': 'Мі (d ≈ λ)', 'sub': 'Аерозолі d ~ 0.1–3 мкм (PM2.5)', 'scale': 'I ∝ d² .. d⁴ (пелюсток)', 'sym': 'Переважає розсіювання вперед'},
        {'x': 690, 'title': 'Геометричний (d >> λ)', 'sub': 'Великий пил d > 10 мкм', 'scale': 'I ∝ d² (тінь/відбиття)', 'sym': 'Геометрична оптика'}
    ]

    for c in cols:
        cx = c['x']
        b, bw, bh = textbox(cx, 40, c['title'], size=14, bold=True, fill='#eef2f7', stroke='#4a5568')
        frags.append(b)
        frags.append(text(cx, 75, c['sub'], size=11, color='#4a5568'))

        frags.append(rect(cx - 120, 95, 240, 190, fill='#fafbfc', stroke='#cbd5e1', rx=8))

        frags.append(line(cx - 110, 190, cx - 40, 190, color=POS, sw=2.5))
        frags.append(arrow(cx - 110, 190, cx - 40, 190, color=POS, sw=2.5))
        frags.append(text(cx - 75, 178, 'Лазер λ', size=10, color=POS, bold=True))

        frags.append(text(cx, 305, c['scale'], size=12, color=INK, bold=True))
        frags.append(text(cx, 325, c['sym'], size=11, color='#4a5568'))

    # 1: Релей
    c1 = 150
    frags.append(circle(c1, 190, 4, fill=INK, stroke=LINE, sw=1))
    frags.append('<circle cx="%d" cy="190" r="22" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (c1 - 25, NEG))
    frags.append(circle(c1 + 25, 190, 22, fill='none', stroke=NEG, sw=1.5))
    frags.append(arrow(c1, 190, c1 + 45, 190, color=NEG, sw=1.5))
    frags.append(arrow(c1, 190, c1 - 45, 190, color=NEG, sw=1.5))

    # 2: Мі
    c2 = 420
    frags.append(circle(c2, 190, 9, fill='#718096', stroke=LINE, sw=1.5))
    frags.append('<path d="M %d 190 C %d 140, %d 160, %d 190 C %d 220, %d 240, %d 190 Z" fill="#ebf4ff" stroke="%s" stroke-width="2"/>' % (
        c2, c2 + 60, c2 + 105, c2 + 105, c2 + 105, c2 + 60, c2, NEG))
    frags.append('<path d="M %d 190 C %d 175, %d 180, %d 190 C %d 200, %d 205, %d 190 Z" fill="#f1f5f9" stroke="%s" stroke-width="1.5"/>' % (
        c2, c2 - 20, c2 - 35, c2 - 35, c2 - 35, c2 - 20, c2, NEG))
    frags.append(arrow(c2, 190, c2 + 95, 190, color=NEG, sw=2))
    frags.append(arrow(c2, 190, c2 + 45, 150, color=FIELD, sw=1.5))
    frags.append(arrow(c2, 190, c2 + 45, 230, color=FIELD, sw=1.5))
    frags.append(text(c2 + 60, 138, 'Кут 90°/60°', size=10, color=FIELD, bold=True))

    # 3: Геометричний
    c3 = 690
    frags.append(circle(c3, 190, 22, fill='#a0aec0', stroke=LINE, sw=1.8))
    frags.append(rect(c3 + 24, 168, 60, 44, fill='#edf2f7', stroke='none'))
    frags.append(text(c3 + 50, 194, 'Тінь', size=11, color='#718096', italic=True))
    frags.append(line(c3 - 35, 175, c3 - 18, 175, color=POS, sw=1.5))
    frags.append(arrow(c3 - 18, 175, c3 - 35, 150, color=POS, sw=1.5))
    frags.append(line(c3 - 35, 205, c3 - 18, 205, color=POS, sw=1.5))
    frags.append(arrow(c3 - 18, 205, c3 - 35, 230, color=POS, sw=1.5))
    frags.append(text(c3 - 40, 140, 'Відбивання', size=10, color=POS))

    render(os.path.join(IMG_DIR, 'mie-scattering-regimes.svg'), w, h, *frags)


def fig_opc_chamber():
    w, h = 860, 420
    frags = []

    frags.append(rect(30, 40, 800, 340, fill='#f8fafc', stroke='#334155', sw=2, rx=12))
    frags.append(text(160, 65, 'Оптична камера лічильника частинок (OPC)', size=14, bold=True, color='#1e293b'))

    frags.append(rect(370, 40, 60, 340, fill='#f1f5f9', stroke='#94a3b8', sw=1.5, rx=0))
    frags.append(arrow(400, 50, 400, 110, color=FIELD, sw=2))
    frags.append(text(400, 75, 'Вхід повітря', size=11, color=FIELD, bold=True))
    frags.append(arrow(400, 280, 400, 365, color=FIELD, sw=2))
    frags.append(text(400, 355, 'Вихід (до вентилятора)', size=11, color=FIELD, bold=True))

    b_laser, _, _ = textbox(110, 190, 'Лазерний діод\nλ = 650 нм\n+ коліматор', size=11, fill='#fee2e2', stroke=POS, bold=True)
    frags.append(b_laser)

    frags.append(rect(190, 185, 180, 10, fill='#fca5a5', stroke=POS, sw=1))
    frags.append(rect(370, 185, 60, 10, fill='#ef4444', stroke=POS, sw=1.5))
    frags.append(rect(430, 185, 140, 10, fill='#fca5a5', stroke=POS, sw=1))
    frags.append(text(280, 175, 'Сфокусований лазерний промінь', size=10, color=POS, bold=True))

    frags.append('<circle cx="400" cy="190" r="18" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,3"/>' % POS)
    frags.append(circle(396, 188, 3, fill=INK, stroke=LINE, sw=1))
    frags.append(text(330, 220, 'Частинка аерозолю', size=10, color=INK, bold=True))
    frags.append(line(355, 212, 392, 192, color=LINE, sw=1))

    frags.append(rect(570, 155, 70, 70, fill='#1e293b', stroke='#0f172a', sw=2, rx=4))
    frags.append('<path d="M 570 160 L 610 175 L 570 190 L 610 205 L 570 220" fill="none" stroke="#64748b" stroke-width="1.5"/>')
    frags.append(text(605, 145, 'Світлова пастка', size=11, bold=True, color='#1e293b'))
    frags.append(text(605, 240, 'Поглинає прямий промінь', size=9, color='#64748b'))

    frags.append(line(400, 180, 480, 110, color=NEG, sw=1.5, dash='2,2'))
    frags.append(line(400, 200, 480, 270, color=NEG, sw=1.5, dash='2,2'))
    frags.append(arrow(400, 190, 460, 260, color=NEG, sw=2))
    frags.append(text(480, 230, 'Розсіяне світло (кут 90°)', size=11, color=NEG, bold=True))

    frags.append(rect(510, 260, 14, 50, fill='#dbeafe', stroke=NEG, sw=1.5, rx=7))
    frags.append(text(517, 248, 'Лінза', size=10, color=NEG))

    b_pd, _, _ = textbox(630, 285, 'PIN-фотодіод\n+ екран Фарадея', size=11, fill='#eff6ff', stroke=NEG, bold=True)
    frags.append(b_pd)

    b_tia, _, _ = textbox(750, 285, 'Трансімпедансний\nпідсилювач (TIA)\n+ ФВЧ базової лінії', size=10, fill='#f8fafc', stroke=LINE)
    frags.append(b_tia)

    frags.append(arrow(525, 285, 570, 285, color=NEG, sw=1.5))
    frags.append(arrow(690, 285, 705, 285, color=LINE, sw=1.5))
    frags.append(arrow(750, 325, 750, 360, color=LINE, sw=1.5))
    frags.append(text(750, 375, 'До АЦП / компараторів МК', size=10, color=INK, bold=True))

    render(os.path.join(IMG_DIR, 'opc-chamber-optics.svg'), w, h, *frags)


def fig_pulse_binning():
    w, h = 840, 390
    frags = []

    frags.append(rect(40, 30, 760, 330, fill='#ffffff', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(220, 55, 'Часовий сигнал фотоструму V_out(t) на виході підсилювача', size=13, bold=True, color='#1e293b'))

    frags.append(arrow(80, 290, 750, 290, color='#64748b', sw=1.5))
    frags.append(text(730, 308, 'Час t (мкс)', size=11, color='#64748b'))
    frags.append(arrow(80, 290, 80, 60, color='#64748b', sw=1.5))
    frags.append(text(65, 75, 'V (В)', size=11, color='#64748b', anchor='end'))

    frags.append(line(80, 275, 740, 275, color='#94a3b8', sw=1, dash='4,4'))
    frags.append(text(745, 278, 'Шумовий поріг', size=10, color='#94a3b8', anchor='start'))

    thresholds = [
        {'y': 245, 'lbl': 'Поріг 0.3 мкм', 'col': '#0284c7'},
        {'y': 205, 'lbl': 'Поріг 0.5 мкм', 'col': '#16a34a'},
        {'y': 160, 'lbl': 'Поріг 1.0 мкм', 'col': '#d97706'},
        {'y': 105, 'lbl': 'Поріг 2.5 мкм', 'col': '#dc2626'},
    ]

    for th in thresholds:
        frags.append(line(80, th['y'], 740, th['y'], color=th['col'], sw=1, dash='2,2'))
        frags.append(text(85, th['y'] - 5, th['lbl'], size=10, color=th['col'], bold=True, anchor='start'))

    p1 = 'M 130 275 Q 145 235 155 235 Q 165 235 180 275'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p1, '#0284c7'))
    frags.append(text(155, 220, 'd = 0.35 мкм', size=10, color='#0284c7', bold=True))

    p2 = 'M 230 275 Q 255 180 270 180 Q 285 180 310 275'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p2, '#16a34a'))
    frags.append(text(270, 165, 'd = 0.8 мкм', size=10, color='#16a34a', bold=True))

    p3 = 'M 370 275 Q 400 130 420 130 Q 440 130 470 275'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p3, '#d97706'))
    frags.append(text(420, 115, 'd = 1.8 мкм', size=10, color='#d97706', bold=True))

    p4 = 'M 530 275 Q 565 80 590 80 Q 615 80 650 275'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p4, '#dc2626'))
    frags.append(text(590, 68, 'd = 3.2 мкм (PM10)', size=10, color='#dc2626', bold=True))

    b_rule, _, _ = textbox(440, 335, 'Амплітуда піка V_peak ∝ переріз розсіювання σ(d) → діаметр частинки d\nКількість імпульсів за секунду N/Δt → числова концентрація', size=11, fill='#f8fafc', stroke=LINE)
    frags.append(b_rule)

    render(os.path.join(IMG_DIR, 'pulse-detection-binning.svg'), w, h, *frags)


def fig_calibration_hygroscopic():
    w, h = 840, 370
    frags = []

    # Ліва панель: Монотонність та осциляції калібрувальної кривої V(d)
    frags.append(rect(30, 30, 375, 310, fill='#ffffff', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(217, 55, 'Калібрувальний відгук V(d)', size=13, bold=True, color='#1e293b'))

    frags.append(arrow(65, 290, 375, 290, color='#64748b', sw=1.5))
    frags.append(text(350, 308, 'Розмір d (мкм)', size=10, color='#64748b'))
    frags.append(arrow(65, 290, 65, 75, color='#64748b', sw=1.5))
    frags.append(text(55, 85, 'Сигнал V', size=10, color='#64748b', anchor='end'))

    curve_mie = 'M 75 285 C 110 280, 140 260, 170 230 C 190 210, 210 220, 230 190 C 250 160, 270 170, 290 130 C 320 90, 345 85, 365 80'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (curve_mie, POS))
    frags.append(text(245, 255, 'Резонансні осциляції Мі\nв діапазоні 0.6–1.5 мкм', size=10, color=POS))

    frags.append(circle(170, 230, 4, fill=NEG, stroke=LINE, sw=1))
    frags.append(circle(290, 130, 4, fill=NEG, stroke=LINE, sw=1))
    frags.append(text(170, 218, 'PSL 0.5', size=9, color=NEG, bold=True))
    frags.append(text(290, 118, 'PSL 2.0', size=9, color=NEG, bold=True))

    # Права панель: Фактор гігроскопічного набрякання f(RH)
    frags.append(rect(435, 30, 375, 310, fill='#ffffff', stroke='#cbd5e1', sw=1.5, rx=8))
    frags.append(text(622, 55, 'Гігроскопічний ріст f(RH)', size=13, bold=True, color='#1e293b'))

    frags.append(arrow(470, 290, 780, 290, color='#64748b', sw=1.5))
    frags.append(text(745, 308, 'RH (%)', size=10, color='#64748b'))
    frags.append(arrow(470, 290, 470, 75, color='#64748b', sw=1.5))
    frags.append(text(460, 85, 'f(RH) = PM / PM_dry', size=10, color='#64748b', anchor='end'))

    frags.append(line(470, 240, 770, 240, color='#cbd5e1', sw=1, dash='2,2'))
    frags.append(text(455, 244, '1.0', size=9, color='#64748b'))
    frags.append(line(680, 290, 680, 85, color='#fed7aa', sw=1, dash='3,3'))
    frags.append(text(680, 308, '70%', size=10, color='#c2410c', bold=True))

    curve_growth = 'M 480 240 C 560 240, 640 235, 680 220 C 710 200, 735 160, 765 95'
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (curve_growth, '#2563eb'))

    frags.append(text(540, 260, 'Сухі частинки: f(RH) ≈ 1', size=10, color='#475569'))
    frags.append(text(620, 115, 'Водна оболонка:\nпомилка оптичної маси\nдо +300% при 90% RH', size=10, color='#2563eb', bold=True))

    render(os.path.join(IMG_DIR, 'calibration-curve-hygroscopic.svg'), w, h, *frags)


if __name__ == '__main__':
    fig_mie_regimes()
    fig_opc_chamber()
    fig_pulse_binning()
    fig_calibration_hygroscopic()
    print('Всі фігури успішно згенеровано.')
