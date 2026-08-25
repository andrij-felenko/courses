# -*- coding: utf-8 -*-
"""Фігури до теми «Лавинна робота MOSFET».
Генерує 4 SVG-діаграми у ./img/:
  1. avalanche-physics.svg          — Фізика лавинного пробою та паразитний BJT
  2. uis-test-circuit-waveforms.svg — Схема випробування UIS та осцилограми
  3. planar-trench-superjunction.svg— Порівняння структур: Planar, Trench, Superjunction
  4. clamping-alternatives.svg      — Порівняння способів гасіння індуктивного викиду
Запуск: python figs.py
"""
import sys, os

# Додаємо шлях до svgkit у scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. avalanche-physics.svg ──────────────────────────────────────────────
def make_avalanche_physics(path):
    w, h = 860, 530
    out = []

    # Заголовки блоків
    out.append(fitbox(20, 15, 380, 40, "Кристал MOSFET під час лавини", fill=FILL, stroke=LINE, bold=True, size=14))
    out.append(fitbox(440, 15, 400, 40, "Еквівалентна схема паразитного BJT", fill=FILL, stroke=LINE, bold=True, size=14))

    # ── Ліва частина: розріз напівпровідникової структури ──
    # Метал витоку (Source Metal)
    out.append(rect(40, 70, 340, 24, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(210, 86, "Метал витоку (Source / Body Contact)", size=12, color=INK, bold=True))

    # Витік n+ (Source n+)
    out.append(rect(60, 94, 90, 35, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(105, 116, "n+ Source", size=11, color=INK, bold=True))

    out.append(rect(250, 94, 90, 35, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(295, 116, "n+ Source", size=11, color=INK, bold=True))

    # Тіло p-body
    out.append(rect(40, 94, 20, 95, fill="#ce93d8", stroke=INK, sw=1.4))
    out.append(rect(150, 94, 100, 95, fill="#ba68c8", stroke=INK, sw=1.4))
    out.append(rect(340, 94, 40, 95, fill="#ce93d8", stroke=INK, sw=1.4))
    out.append(rect(60, 129, 90, 60, fill="#ce93d8", stroke=INK, sw=1.4))
    out.append(rect(250, 129, 90, 60, fill="#ce93d8", stroke=INK, sw=1.4))

    out.append(text(200, 125, "p+ Body", size=11, color="#ffffff", bold=True))
    out.append(text(200, 155, "p-Body", size=12, color="#ffffff", bold=True))
    out.append(text(105, 160, "R_body", size=11, color=INK, bold=True))
    out.append(text(295, 160, "R_body", size=11, color=INK, bold=True))

    # Дрейфова зона n- (Drift region)
    out.append(rect(40, 189, 340, 170, fill="#fff9c4", stroke=INK, sw=1.4))
    out.append(text(210, 230, "n- Дрейфова область (n- Drift)", size=13, color=INK, bold=True))

    # Збіднена область та область лавинного розмноження
    out.append(f'<rect x="46" y="191" width="328" height="55" rx="4" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,4"/>')
    out.append(text(210, 208, "Область сильного поля E > E_crit", size=11, color=POS, bold=True))

    # Ударна іонізація: стрілки генерації e- і h+
    out.append(text(120, 260, "e- (електрони → Стік)", size=11, color="#1565c0", bold=True))
    out.append(arrow(120, 270, 120, 310, color="#1565c0", sw=2))

    out.append(text(285, 260, "h+ (дірки → Витік)", size=11, color=POS, bold=True))
    out.append(arrow(285, 250, 285, 175, color=POS, sw=2))

    # Підкладка n+ і метал стоку
    out.append(rect(40, 359, 340, 45, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(210, 386, "n+ Підкладка (Substrate)", size=12, color=INK, bold=True))

    out.append(rect(40, 404, 340, 25, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(210, 420, "Метал стоку (Drain Metal, V_DS = BV_DSS)", size=12, color=INK, bold=True))

    # Пояснювальний бокс знизу ліворуч
    out.append(fitbox(40, 445, 340, 70,
                      "1. При V_DS = BV_DSS виникає ударна іонізація.\n"
                      "2. Дірковий струм тече вбік під n+ витоком крізь R_body.\n"
                      "3. Якщо I_hole · R_body > 0.7 В → відкривається NPN BJT!",
                      fill="#fff3e0", stroke="#ff9800", size=11, color=INK))

    # ── Права частина: схема паразитного BJT ──
    # Стік зверху
    out.append(line(625, 75, 625, 120, color=INK, sw=2))
    out.append(circle(625, 75, 4, fill=INK))
    out.append(text(625, 65, "Стік (Drain)", size=12, color=INK, bold=True))

    # MOSFET символ (спрощений блок)
    out.append(rect(595, 120, 60, 45, fill="#e8f5e9", stroke=INK, sw=1.6, rx=4))
    out.append(text(625, 145, "MOSFET", size=11, color=INK, bold=True))

    # Паразитний BJT паралельно
    out.append(line(625, 95, 735, 95, color=INK, sw=1.8))
    out.append(line(735, 95, 735, 180, color=INK, sw=1.8))

    # Символ NPN
    out.append(line(705, 185, 705, 235, color=INK, sw=3))
    out.append(line(705, 195, 735, 180, color=INK, sw=2))
    out.append(line(705, 225, 735, 240, color=INK, sw=2))
    out.append(arrow(715, 230, 733, 239, color=INK, sw=2))

    out.append(text(760, 210, "Паразитний\nNPN BJT", size=12, color=POS, bold=True, anchor="start"))

    # База BJT йде до R_body
    out.append(line(705, 210, 650, 210, color=INK, sw=1.8))
    out.append(line(650, 210, 650, 260, color=INK, sw=1.8))

    # Резистор R_body
    out.append(rect(640, 260, 20, 50, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    out.append(text(610, 290, "R_body", size=12, color=POS, bold=True))

    # З'єднання емітера BJT та R_body до Source
    out.append(line(735, 240, 735, 360, color=INK, sw=1.8))
    out.append(line(650, 310, 650, 360, color=INK, sw=1.8))
    out.append(line(625, 165, 625, 360, color=INK, sw=1.8))
    out.append(line(625, 360, 735, 360, color=INK, sw=2))

    # Витік знизу
    out.append(line(680, 360, 680, 410, color=INK, sw=2))
    out.append(circle(680, 410, 4, fill=INK))
    out.append(text(680, 428, "Витік (Source)", size=12, color=INK, bold=True))

    # Джерело лавинного струму (дірки в базу)
    out.append(line(735, 135, 650, 135, color=POS, sw=1.6, dash="3,3"))
    out.append(arrow(735, 135, 650, 200, color=POS, sw=2))
    out.append(text(545, 185, "Лавинний струм I_hole", size=11, color=POS, bold=True))

    # Пояснювальний бокс праворуч знизу
    out.append(fitbox(440, 445, 400, 70,
                      "Критичний поріг відмикання:\n"
                      "V_BE = I_hole · R_body ≥ 0.7 В (при 25°C) або ~0.5 В (при 150°C)\n"
                      "Відкриття BJT викликає вторинний пробій і тепловий колапс.",
                      fill="#ffebee", stroke=POS, size=11, color=INK))

    render(path, w, h, *out)


# ── 2. uis-test-circuit-waveforms.svg ──────────────────────────────────────
def make_uis_test_waveforms(path):
    w, h = 860, 520
    out = []

    out.append(fitbox(20, 15, 340, 35, "Схема випробування UIS (Unclamped)", fill=FILL, stroke=LINE, bold=True, size=13))
    out.append(fitbox(390, 15, 450, 35, "Осцилограми струму, напруги та енергії", fill=FILL, stroke=LINE, bold=True, size=13))

    # ── Ліворуч: Схема UIS ──
    out.append(line(70, 80, 180, 80, color=INK, sw=2))
    out.append(circle(70, 80, 4, fill=INK))
    out.append(text(70, 68, "+V_DD", size=12, color=INK, bold=True))

    # Дросель L
    out.append(line(180, 80, 180, 105, color=INK, sw=2))
    for i in range(4):
        cy = 115 + i * 20
        out.append(f'<path d="M 180 {cy-10} A 10 10 0 0 1 180 {cy+10}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(line(180, 185, 180, 215, color=INK, sw=2))
    out.append(text(215, 145, "L (дросель)", size=12, color=INK, bold=True, anchor="start"))

    # MOSFET (DUT)
    out.append(rect(145, 215, 70, 70, fill="#e8f5e9", stroke=INK, sw=1.8, rx=4))
    out.append(text(180, 245, "DUT", size=13, color=INK, bold=True))
    out.append(text(180, 265, "MOSFET", size=11, color=INK))

    # Затворне коло
    out.append(line(90, 250, 145, 250, color=INK, sw=2))
    out.append(rect(60, 240, 30, 20, fill="#ffffff", stroke=INK, sw=1.5, rx=2))
    out.append(text(75, 233, "R_G", size=11, color=INK, bold=True))
    out.append(line(30, 250, 60, 250, color=INK, sw=2))
    out.append(circle(30, 250, 3, fill=INK))
    out.append(text(30, 270, "V_in (t_on)", size=11, color=INK, bold=True, anchor="start"))

    # Витік на землю
    out.append(line(180, 285, 180, 330, color=INK, sw=2))
    out.append(line(160, 330, 200, 330, color=INK, sw=2.5))
    out.append(line(168, 336, 192, 336, color=INK, sw=2))
    out.append(line(174, 342, 186, 342, color=INK, sw=1.5))
    out.append(text(180, 360, "GND", size=11, color=INK, bold=True))

    out.append(arrow(195, 100, 195, 170, color=POS, sw=2))
    out.append(text(215, 115, "I_D", size=12, color=POS, bold=True, anchor="start"))

    out.append(fitbox(20, 385, 340, 115,
                      "Особливість тесту UIS:\n"
                      "• Діод паралельно L відсутній (unclamped).\n"
                      "• Уся магнітна енергія 0.5·L·I² гаситься\n"
                      "  безпосередньо в кристалі транзистора.\n"
                      "• Стік підскакує до V_DS = BV_DSS.",
                      fill="#fff8e1", stroke="#fbc02d", size=11, color=INK))

    # ── Осцилограми ──
    ox, t0, t1, t2, tend = 450, 500, 600, 760, 820

    # 1. V_GS
    gy = 70
    out.append(line(ox, gy + 35, tend, gy + 35, color=MUTED, sw=1))
    out.append(text(ox - 10, gy + 20, "V_GS", size=12, color=INK, bold=True, anchor="end"))
    out.append(f'<polyline points="{ox},{gy+35} {t0},{gy+35} {t0},{gy+5} {t1},{gy+5} {t1},{gy+35} {tend},{gy+35}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(text(550, gy - 2, "t_on (накопичення)", size=11, color=INK))

    # 2. I_D
    iy = 160
    out.append(line(ox, iy + 60, tend, iy + 60, color=MUTED, sw=1))
    out.append(text(ox - 10, iy + 30, "I_D", size=12, color=INK, bold=True, anchor="end"))
    out.append(f'<polygon points="{t0},{iy+60} {t1},{iy+5} {t2},{iy+60}" fill="#e3f2fd" stroke="none"/>')
    out.append(f'<polyline points="{ox},{iy+60} {t0},{iy+60} {t1},{iy+5} {t2},{iy+60} {tend},{iy+60}" fill="none" stroke="#1976d2" stroke-width="2.2"/>')
    out.append(text(t1 - 10, iy - 2, "I_AS (піковий струм)", size=11, color="#1976d2", bold=True, anchor="end"))
    out.append(line(t1, iy + 5, t1, iy + 60, color="#1976d2", sw=1, dash="3,3"))

    # 3. V_DS
    vy = 280
    out.append(line(ox, vy + 70, tend, vy + 70, color=MUTED, sw=1))
    out.append(text(ox - 10, vy + 30, "V_DS", size=12, color=INK, bold=True, anchor="end"))
    out.append(line(ox, vy + 45, tend, vy + 45, color=MUTED, sw=1, dash="4,4"))
    out.append(text(ox + 5, vy + 40, "V_DD", size=10, color=MUTED, anchor="start"))
    out.append(f'<polygon points="{t1},{vy+70} {t1},{vy+10} {t2},{vy+10} {t2},{vy+45} {t1},{vy+45}" fill="#ffebee" stroke="none"/>')
    out.append(f'<polyline points="{ox},{vy+45} {t0},{vy+45} {t0},{vy+68} {t1},{vy+68} {t1},{vy+10} {t2},{vy+10} {t2},{vy+45} {tend},{vy+45}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    out.append(text(t1 + 20, vy + 3, "BV_DSS (лавинна полиця)", size=11, color=POS, bold=True, anchor="start"))

    # Часові маркери
    my = 380
    out.append(line(t0, gy + 5, t0, my + 10, color="#cfd8dc", sw=1, dash="2,2"))
    out.append(line(t1, gy + 5, t1, my + 10, color="#cfd8dc", sw=1, dash="2,2"))
    out.append(line(t2, vy + 10, t2, my + 10, color="#cfd8dc", sw=1, dash="2,2"))

    out.append(line(t1, my, t2, my, color=INK, sw=1.5))
    out.append(arrow(t1 + 25, my, t1, my, color=INK, sw=1.5))
    out.append(arrow(t2 - 25, my, t2, my, color=INK, sw=1.5))
    out.append(text((t1 + t2) / 2, my - 6, "t_av (тривалість лавини)", size=11, color=INK, bold=True))

    out.append(fitbox(410, 415, 430, 85,
                      "Енергія одиночного лавинного імпульсу:\n"
                      "E_AS = 0.5 · L · I_AS² · [ BV_DSS / (BV_DSS - V_DD) ]\n"
                      "t_av = L · I_AS / (BV_DSS - V_DD)",
                      fill="#f3e5f5", stroke="#8e24aa", size=11, color=INK, bold=True))

    render(path, w, h, *out)


# ── 3. planar-trench-superjunction.svg ─────────────────────────────────────
def make_planar_trench_superjunction(path):
    w, h = 880, 490
    out = []

    out.append(fitbox(20, 15, 265, 35, "Planar VDMOS (Класична)", fill=FILL, stroke=LINE, bold=True, size=13))
    out.append(fitbox(305, 15, 265, 35, "Trench MOSFET (Низьковольтна)", fill=FILL, stroke=LINE, bold=True, size=13))
    out.append(fitbox(590, 15, 265, 35, "Superjunction (CoolMOS)", fill=FILL, stroke=LINE, bold=True, size=13))

    # 1. Planar
    x1 = 20
    out.append(rect(x1 + 10, 60, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x1 + 132, 73, "Source Metal", size=10, color=INK, bold=True))

    out.append(rect(x1 + 82, 82, 100, 16, fill="#90a4ae", stroke=INK, sw=1.2))
    out.append(text(x1 + 132, 94, "Poly Gate", size=10, color="#ffffff", bold=True))

    out.append(rect(x1 + 20, 80, 60, 50, fill="#ce93d8", stroke=INK, sw=1.2))
    out.append(rect(x1 + 185, 80, 60, 50, fill="#ce93d8", stroke=INK, sw=1.2))
    out.append(text(x1 + 50, 110, "p-body", size=10, color="#ffffff", bold=True))
    out.append(text(x1 + 215, 110, "p-body", size=10, color="#ffffff", bold=True))

    out.append(rect(x1 + 45, 80, 30, 20, fill="#ffe082", stroke=INK, sw=1.2))
    out.append(rect(x1 + 190, 80, 30, 20, fill="#ffe082", stroke=INK, sw=1.2))

    out.append(rect(x1 + 10, 130, 245, 160, fill="#fff9c4", stroke=INK, sw=1.4))
    out.append(text(x1 + 132, 190, "Товстий n- Drift шар", size=11, color=INK, bold=True))
    out.append(text(x1 + 132, 210, "Великий тепловий об'єм", size=10, color="#558b2f"))

    out.append(rect(x1 + 10, 290, 245, 30, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(rect(x1 + 10, 320, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x1 + 132, 333, "Drain Metal", size=10, color=INK, bold=True))

    out.append(fitbox(x1, 350, 265, 120,
                      "• Висока питома стійкість E_AS\n"
                      "• Товстий кремній розсіює тепло лавини\n"
                      "• Більший R_DS(on) на одиницю площі",
                      fill="#f1f8e9", stroke="#7cb342", size=10, color=INK))

    # 2. Trench
    x2 = 305
    out.append(rect(x2 + 10, 60, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x2 + 132, 73, "Source Metal", size=10, color=INK, bold=True))

    # p-Body блоки розділені траншеями
    out.append(rect(x2 + 10, 80, 60, 75, fill="#ce93d8", stroke=INK, sw=1.2))
    out.append(rect(x2 + 102, 80, 60, 75, fill="#ce93d8", stroke=INK, sw=1.2))
    out.append(rect(x2 + 194, 80, 61, 75, fill="#ce93d8", stroke=INK, sw=1.2))

    # n+ витоки всередині p-body
    out.append(rect(x2 + 25, 80, 30, 20, fill="#ffe082", stroke=INK, sw=1.2))
    out.append(rect(x2 + 117, 80, 30, 20, fill="#ffe082", stroke=INK, sw=1.2))
    out.append(rect(x2 + 209, 80, 30, 20, fill="#ffe082", stroke=INK, sw=1.2))

    # Вертикальні траншеї затвора (Trench Gates)
    out.append(rect(x2 + 70, 80, 32, 75, fill="#90a4ae", stroke=INK, sw=1.4, rx=2))
    out.append(rect(x2 + 162, 80, 32, 75, fill="#90a4ae", stroke=INK, sw=1.4, rx=2))
    out.append(text(x2 + 86, 118, "G", size=10, color="#ffffff", bold=True))
    out.append(text(x2 + 178, 118, "G", size=10, color="#ffffff", bold=True))

    out.append(rect(x2 + 10, 155, 245, 135, fill="#fff9c4", stroke=INK, sw=1.4))
    out.append(text(x2 + 132, 205, "Тонкий n- Drift шар", size=11, color=INK, bold=True))
    out.append(text(x2 + 132, 225, "Висока щільність комірок", size=10, color=POS))

    out.append(rect(x2 + 10, 290, 245, 30, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(rect(x2 + 10, 320, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x2 + 132, 333, "Drain Metal", size=10, color=INK, bold=True))

    out.append(fitbox(x2, 350, 265, 120,
                      "• Рекордно низький R_DS(on)\n"
                      "• Концентрація струму біля дна траншеї\n"
                      "• Ризик BJT turn-on при високих I_AS",
                      fill="#fff8e1", stroke="#ffa000", size=10, color=INK))

    # 3. Superjunction
    x3 = 590
    out.append(rect(x3 + 10, 60, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x3 + 132, 73, "Source Metal", size=10, color=INK, bold=True))

    out.append(rect(x3 + 10, 80, 245, 35, fill="#ce93d8", stroke=INK, sw=1.2))

    out.append(rect(x3 + 30, 115, 45, 175, fill="#ba68c8", stroke=INK, sw=1.2))
    out.append(rect(x3 + 110, 115, 45, 175, fill="#ba68c8", stroke=INK, sw=1.2))
    out.append(rect(x3 + 190, 115, 45, 175, fill="#ba68c8", stroke=INK, sw=1.2))
    out.append(text(x3 + 52, 195, "p-кол.", size=10, color="#ffffff", bold=True))
    out.append(text(x3 + 132, 195, "p-кол.", size=10, color="#ffffff", bold=True))
    out.append(text(x3 + 212, 195, "p-кол.", size=10, color="#ffffff", bold=True))

    out.append(rect(x3 + 75, 115, 35, 175, fill="#fff59d", stroke=INK, sw=1.2))
    out.append(rect(x3 + 155, 115, 35, 175, fill="#fff59d", stroke=INK, sw=1.2))
    out.append(text(x3 + 92, 195, "n-кол.", size=9, color=INK, bold=True))
    out.append(text(x3 + 172, 195, "n-кол.", size=9, color=INK, bold=True))

    out.append(rect(x3 + 10, 290, 245, 30, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(rect(x3 + 10, 320, 245, 18, fill="#b0bec5", stroke=INK, sw=1.4))
    out.append(text(x3 + 132, 333, "Drain Metal", size=10, color=INK, bold=True))

    out.append(fitbox(x3, 350, 265, 120,
                      "• Дрейфовий шар у 5–10× тонший\n"
                      "• Малий тепловий об'єм кремнію\n"
                      "• Чутливий до дисбалансу: суворий t_av",
                      fill="#ffebee", stroke=POS, size=10, color=INK))

    render(path, w, h, *out)


# ── 4. clamping-alternatives.svg ───────────────────────────────────────────
def make_clamping_alternatives(path):
    w, h = 890, 480
    out = []

    out.append(fitbox(20, 15, 200, 35, "1. Вбудована лавина", fill=FILL, stroke=LINE, bold=True, size=12))
    out.append(fitbox(240, 15, 200, 35, "2. Зворотний діод", fill=FILL, stroke=LINE, bold=True, size=12))
    out.append(fitbox(460, 15, 200, 35, "3. RC-снабер", fill=FILL, stroke=LINE, bold=True, size=12))
    out.append(fitbox(680, 15, 200, 35, "4. TVS-діод (Супресор)", fill=FILL, stroke=LINE, bold=True, size=12))

    # 1. Лавина
    c1 = 120
    out.append(line(c1, 65, c1, 95, color=INK, sw=2))
    out.append(text(c1, 60, "+V_DD", size=11, color=INK, bold=True))
    out.append(rect(c1 - 10, 95, 20, 45, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    out.append(text(c1 + 18, 120, "L", size=11, color=INK, bold=True, anchor="start"))
    out.append(line(c1, 140, c1, 170, color=INK, sw=2))
    out.append(rect(c1 - 25, 170, 50, 50, fill="#ffebee", stroke=POS, sw=1.8, rx=4))
    out.append(text(c1, 195, "MOSFET", size=10, color=INK, bold=True))
    out.append(text(c1, 210, "(Avalanche)", size=9, color=POS, bold=True))
    out.append(line(c1, 220, c1, 255, color=INK, sw=2))
    out.append(line(c1 - 15, 255, c1 + 15, 255, color=INK, sw=2))

    out.append(fitbox(20, 275, 200, 185,
                      "Плюси:\n"
                      "• 0 додаткових деталей\n"
                      "• Максимально швидке\n"
                      "  знеструмлення котушки\n\n"
                      "Мінуси:\n"
                      "• Все тепло гріє кристал\n"
                      "• Тільки для рідкісних або\n"
                      "  одиночних подій (E_AS)",
                      fill="#fff3e0", stroke="#ff9800", size=10, color=INK))

    # 2. Зворотний діод
    c2 = 340
    out.append(line(c2, 65, c2, 95, color=INK, sw=2))
    out.append(text(c2, 60, "+V_DD", size=11, color=INK, bold=True))
    out.append(rect(c2 - 10, 95, 20, 45, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    out.append(text(c2 - 18, 120, "L", size=11, color=INK, bold=True, anchor="end"))
    out.append(line(c2, 140, c2, 170, color=INK, sw=2))
    out.append(line(c2 + 35, 80, c2, 80, color=INK, sw=1.5))
    out.append(line(c2 + 35, 80, c2 + 35, 155, color=INK, sw=1.5))
    out.append(line(c2 + 35, 155, c2, 155, color=INK, sw=1.5))
    out.append(rect(c2 + 25, 107, 20, 22, fill="#e8f5e9", stroke=INK, sw=1.4, rx=2))
    out.append(text(c2 + 58, 120, "Діод", size=10, color="#2e7d32", bold=True, anchor="start"))
    out.append(rect(c2 - 25, 170, 50, 50, fill="#ffffff", stroke=INK, sw=1.6, rx=4))
    out.append(text(c2, 198, "MOSFET", size=10, color=INK, bold=True))
    out.append(line(c2, 220, c2, 255, color=INK, sw=2))
    out.append(line(c2 - 15, 255, c2 + 15, 255, color=INK, sw=2))

    out.append(fitbox(240, 275, 200, 185,
                      "Плюси:\n"
                      "• V_DS не перевищує V_DD+0.7В\n"
                      "• Кристал MOSFET не гріється\n\n"
                      "Мінуси:\n"
                      "• Повільний спад струму\n"
                      "  (повільне відпускання реле)\n"
                      "• Діод вимагає t_rr < 50 нс",
                      fill="#e8f5e9", stroke="#4caf50", size=10, color=INK))

    # 3. RC-снабер
    c3 = 560
    out.append(line(c3, 65, c3, 95, color=INK, sw=2))
    out.append(text(c3, 60, "+V_DD", size=11, color=INK, bold=True))
    out.append(rect(c3 - 10, 95, 20, 45, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    out.append(text(c3 - 18, 120, "L", size=11, color=INK, bold=True, anchor="end"))
    out.append(line(c3, 140, c3, 170, color=INK, sw=2))
    out.append(line(c3, 160, c3 + 35, 160, color=INK, sw=1.5))
    out.append(rect(c3 + 26, 170, 18, 18, fill="#ffffff", stroke=INK, sw=1.4, rx=2))
    out.append(text(c3 + 55, 180, "R_s", size=10, color=INK, anchor="start"))
    out.append(line(c3 + 35, 160, c3 + 35, 170, color=INK, sw=1.5))
    out.append(line(c3 + 35, 188, c3 + 35, 202, color=INK, sw=1.5))
    out.append(rect(c3 + 26, 202, 18, 18, fill="#ffffff", stroke=INK, sw=1.4, rx=2))
    out.append(text(c3 + 55, 212, "C_s", size=10, color=INK, anchor="start"))
    out.append(line(c3 + 35, 220, c3 + 35, 240, color=INK, sw=1.5))
    out.append(line(c3 + 35, 240, c3, 240, color=INK, sw=1.5))
    out.append(rect(c3 - 25, 170, 50, 50, fill="#ffffff", stroke=INK, sw=1.6, rx=4))
    out.append(text(c3, 198, "MOSFET", size=10, color=INK, bold=True))
    out.append(line(c3, 220, c3, 255, color=INK, sw=2))
    out.append(line(c3 - 15, 255, c3 + 15, 255, color=INK, sw=2))

    out.append(fitbox(460, 275, 200, 185,
                      "Плюси:\n"
                      "• Гасить дзвін і EMI dV/dt\n"
                      "• Переносить тепло з кристала\n"
                      "  на зовнішній резистор R_s\n\n"
                      "Мінуси:\n"
                      "• Додаткові втрати 0.5·C·V²·f\n"
                      "• Збільшує час перемикання",
                      fill="#e3f2fd", stroke="#2196f3", size=10, color=INK))

    # 4. TVS-діод
    c4 = 780
    out.append(line(c4, 65, c4, 95, color=INK, sw=2))
    out.append(text(c4, 60, "+V_DD", size=11, color=INK, bold=True))
    out.append(rect(c4 - 10, 95, 20, 45, fill="#ffffff", stroke=INK, sw=1.6, rx=2))
    out.append(text(c4 - 18, 120, "L", size=11, color=INK, bold=True, anchor="end"))
    out.append(line(c4, 140, c4, 170, color=INK, sw=2))
    out.append(line(c4, 155, c4 + 35, 155, color=INK, sw=1.5))
    out.append(line(c4 + 35, 155, c4 + 35, 180, color=INK, sw=1.5))
    out.append(rect(c4 + 25, 180, 20, 30, fill="#f3e5f5", stroke="#8e24aa", sw=1.5, rx=3))
    out.append(text(c4 + 56, 197, "TVS", size=10, color="#8e24aa", bold=True, anchor="start"))
    out.append(line(c4 + 35, 210, c4 + 35, 240, color=INK, sw=1.5))
    out.append(line(c4 + 35, 240, c4, 240, color=INK, sw=1.5))
    out.append(rect(c4 - 25, 170, 50, 50, fill="#ffffff", stroke=INK, sw=1.6, rx=4))
    out.append(text(c4, 198, "MOSFET", size=10, color=INK, bold=True))
    out.append(line(c4, 220, c4, 255, color=INK, sw=2))
    out.append(line(c4 - 15, 255, c4 + 15, 255, color=INK, sw=2))

    out.append(fitbox(680, 275, 200, 185,
                      "Плюси:\n"
                      "• Чітко фіксована напруга V_cl\n"
                      "• Швидке знеструмлення L\n"
                      "• Тепло поглинає окремий TVS\n\n"
                      "Мінуси:\n"
                      "• Вартість і габарити супресора\n"
                      "• Обмеження за частотою P_avg",
                      fill="#f3e5f5", stroke="#ab47bc", size=10, color=INK))

    render(path, w, h, *out)


def main():
    figs = {
        "avalanche-physics.svg": make_avalanche_physics,
        "uis-test-circuit-waveforms.svg": make_uis_test_waveforms,
        "planar-trench-superjunction.svg": make_planar_trench_superjunction,
        "clamping-alternatives.svg": make_clamping_alternatives
    }
    for name, func in figs.items():
        path = os.path.join(IMG, name)
        func(path)
        print(f"Generated {name}")


if __name__ == "__main__":
    main()
