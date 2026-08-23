# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"

def fig_tco_structure():
    """Порівняння структури TCO: Хмарний OpEx проти Bare Metal CapEx+OpEx."""
    W, H = 980, 420
    f = []

    # Заголовок блоків
    f.append(fitbox(45, 45, 420, 36, "Хмара (AWS / GCP / Azure)", size=15, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(515, 45, 420, 36, "Власне залізо (Co-location / Bare Metal)", size=15, bold=True, fill=NEUT, stroke=INK))

    # Ліва колонка — Хмара (OpEx)
    f.append(fitbox(45, 95, 420, 65, "Обчислення (vCPU / RAM)\nГнучкість, але націнка 3×–5× до ціни заліза", size=13, fill=RED_T, stroke=NEG))
    f.append(fitbox(45, 170, 420, 65, "Трафік назовні (Egress)\nОсновна пастка: $0.08–$0.12 за кожен ГБ", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(45, 245, 420, 65, "Керовані сервіси (Managed DB, K8s, Logs)\nПлата за відсутність адміністрування", size=13, fill=BLUE_T, stroke=POS))
    f.append(fitbox(45, 320, 420, 55, "Разом: Переважно OpEx · Низький старт · Дорогий масштаб", size=13, bold=True, fill=BG, stroke=INK))

    # Права колонка — Bare Metal
    f.append(fitbox(515, 95, 420, 65, "Амортизація серверів (CapEx)\nКупівля на 3–5 років · Низька питома вартість ядра", size=13, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(515, 170, 420, 65, "Стійка, Електрика та PUE (OpEx)\nФіксована плата за юніт та споживання", size=13, fill=BLUE_T, stroke=POS))
    f.append(fitbox(515, 245, 420, 65, "Трафік та Канал (10–100 Gbps Transit)\nФіксована безлімітна смуга · Дріб'язковий $ / ГБ", size=13, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(515, 320, 420, 55, "Разом: CapEx + Фіксований OpEx · Високий поріг · Дешевий масштаб", size=13, bold=True, fill=BG, stroke=INK))

    render(os.path.join(OUT, 'tco-structure-comparison.svg'), W, H, *f,
           title="Порівняння структури витрат TCO: Хмара проти Bare Metal")


def fig_repatriation_crossover():
    """Точка інфлексії витрат (Crossover point) — де хмара програє залізу за масштабного стабільного навантаження."""
    W, H = 960, 440
    f = []

    # Осі координат
    f.append(arrow(80, 360, 900, 360, color=INK, sw=2)) # X axis
    f.append(arrow(80, 360, 80, 50, color=INK, sw=2))   # Y axis

    f.append(text(910, 365, "Масштаб та прогнозованість навантаження →", size=12, color=INK, anchor="end"))
    f.append(text(75, 40, "Сукупні витрати TCO ($) ↑", size=12, color=INK, anchor="start"))

    # Крива Хмари (Cloud) — старт з 0, але стрімкий підйом (послідовність ліній)
    cloud_pts = [(80, 340), (250, 310), (450, 240), (650, 150), (880, 60)]
    for i in range(len(cloud_pts)-1):
        f.append(line(cloud_pts[i][0], cloud_pts[i][1], cloud_pts[i+1][0], cloud_pts[i+1][1], color=NEG, sw=3.5))
    f.append(text(860, 80, "Хмара (Cloud OpEx)", size=13, bold=True, color=NEG, anchor="end"))

    # Крива Bare Metal — високий старт (CapEx setup), але дуже плаский підйом
    bm_pts = [(80, 210), (250, 210), (450, 210), (650, 205), (880, 195)]
    for i in range(len(bm_pts)-1):
        f.append(line(bm_pts[i][0], bm_pts[i][1], bm_pts[i+1][0], bm_pts[i+1][1], color=FIELD, sw=3.5))
    f.append(text(860, 180, "Bare Metal / Co-location", size=13, bold=True, color=FIELD, anchor="end"))

    # Точка перетину (Crossover point ~ X=550, Y=208)
    f.append(circle(550, 208, 7, fill=AMBER, stroke=INK, sw=1.5))
    f.append(line(550, 208, 550, 360, color=AMBER, sw=1.5, dash="5 4"))
    f.append(fitbox(460, 110, 200, 75, "Точка інфлексії\n(Crossover Point)\nХвиля репатріації", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(560, 185, 553, 201, color=AMBER, sw=1.5))

    # Зони
    f.append(fitbox(120, 250, 260, 60, "Зона переваги хмари:\nневідомий масштаб, стартап,\nпікові сплески навантаження", size=12, fill=BLUE_T, stroke=POS))
    f.append(fitbox(640, 250, 250, 60, "Зона репатріації (Bare Metal):\nстабільна база, прогнозований ріст,\nвисокий Egress / Compute", size=12, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'repatriation-crossover.svg'), W, H, *f,
           title="Крива інфлексії витрат Cloud vs Bare Metal")


def fig_egress_trap():
    """Гравітація даних і пастка Egress-трафіку."""
    W, H = 960, 420
    f = []

    # Ліва частина — Хмарний острів
    f.append(fitbox(50, 60, 380, 320, "", fill=RED_T, stroke=NEG))
    f.append(text(240, 90, "Хмарна інфраструктура", size=15, bold=True, color=NEG, anchor="middle"))
    f.append(fitbox(80, 120, 320, 70, "База даних / S3 Сховище\n500 ТБ відео та метрик", size=13, fill=BG, stroke=INK))
    f.append(fitbox(80, 210, 320, 70, "Обчислювальні вузли (EC2)\nОбробка даних усередині = $0/ГБ", size=13, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(80, 295, 320, 65, "Egress назовні до користувачів / On-Prem\n$0.08–$0.12 за ГБ → $40,000–$60,000/міс!", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Стрілка гравітації між ними
    f.append(fitbox(455, 160, 150, 120, "Гравітація\nданих\n(Data Gravity)\n\nВивід даних\nдорожчий за\nобчислення", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(430, 220, 455, 220, color=AMBER, sw=2))
    f.append(arrow(605, 220, 630, 220, color=AMBER, sw=2))

    # Права частина — Co-location / Bare Metal
    f.append(fitbox(630, 60, 280, 320, "", fill=GREEN_T, stroke=FIELD))
    f.append(text(770, 90, "Власний ЦОД / Co-lo", size=15, bold=True, color=FIELD, anchor="middle"))
    f.append(fitbox(650, 130, 240, 80, "Плоскі транзитні канали\n10 Gbps unmetered port\n~$1,500/місяць фіксовано", size=13, fill=BG, stroke=INK))
    f.append(fitbox(650, 230, 240, 120, "Результат:\nПитома вартість ГБ в 20–50 разів нижча за хмарний Egress", size=13, bold=True, fill=BLUE_T, stroke=POS))

    render(os.path.join(OUT, 'egress-data-gravity-trap.svg'), W, H, *f,
           title="Гравітація даних та пастка хмарного Egress-трафіку")


if __name__ == '__main__':
    fig_tco_structure()
    fig_repatriation_crossover()
    fig_egress_trap()
    print("Figures generated successfully.")
