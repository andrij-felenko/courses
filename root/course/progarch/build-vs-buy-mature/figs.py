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
MUTED   = "#6b7280"
INK     = "#111827"
NEG     = "#dc2626"
POS     = "#16a34a"

def fig_wardley_commodity_drift():
    """Спектр еволюції компонентів: від унікальної розробки до товарного коммодіті."""
    W, H = 840, 440
    f = []

    # Фон і сітка
    f.append(fitbox(20, 45, 800, 365, "", fill="#fafafa", stroke="#e5e7eb"))

    # Осі
    f.append(arrow(60, 375, 800, 375, color=INK, sw=2)) # Горизонтальна вісь Еволюції
    f.append(arrow(60, 375, 60, 55, color=INK, sw=2))   # Вертикальна вісь Вирізняльності

    # Підписи осей
    f.append(text(790, 395, "Еволюція (зрілість ринку) →", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(75, 68, "↑ Вирізняльність (Core / Цінність)", size=11, bold=True, color=INK, anchor="start"))

    # Стадії еволюції (4 вертикальні смуги)
    stages = [
        ("Genesis\n(Зародження)", 60, 240),
        ("Custom Built\n(Своя розробка)", 240, 420),
        ("Product / SaaS\n(Готовий продукт)", 420, 600),
        ("Commodity\n(Базовий товар)", 600, 780)
    ]
    for name, x1, x2 in stages:
        f.append(line(x2, 75, x2, 370, color="#e5e7eb", sw=1, dash="4 4"))
        f.append(text((x1 + x2) / 2, 360, name, size=10, bold=True, color=MUTED, anchor="middle"))

    # Блоки компонентів та їхній дрейф
    # Core (угорі)
    f.append(fitbox(260, 85, 150, 45, "Ядро продукту\n(Алгоритм / Дім)", size=11, bold=True, fill=GREEN_T, stroke=POS))

    # Generic components drift (зліва направо внизу)
    f.append(fitbox(100, 250, 120, 45, "Власний Auth\n(2010)", size=10, fill=NEUT, stroke="#9ca3af"))
    f.append(line(225, 272, 440, 272, color=AMBER, sw=2, dash="5 3"))
    f.append(arrow(440, 272, 445, 272, color=AMBER, sw=2))
    f.append(fitbox(450, 250, 130, 45, "Auth0 / SaaS IDP\n(2018)", size=10, fill=AMBER_T, stroke=AMBER))
    f.append(line(585, 272, 620, 272, color=POS, sw=2, dash="5 3"))
    f.append(arrow(620, 272, 625, 272, color=POS, sw=2))
    f.append(fitbox(630, 250, 140, 45, "OAuth2 / OIDC Standard\n(Commodity)", size=10, fill=BLUE_T, stroke="#2563eb"))

    # Дрейф черговика
    f.append(fitbox(270, 170, 130, 45, "Свій брокер\n(2012)", size=10, fill=NEUT, stroke="#9ca3af"))
    f.append(line(405, 192, 620, 192, color=POS, sw=2, dash="5 3"))
    f.append(arrow(620, 192, 625, 192, color=POS, sw=2))
    f.append(fitbox(630, 170, 140, 45, "AWS SQS / Kafka SaaS\n(Commodity)", size=10, fill=BLUE_T, stroke="#2563eb"))

    # Пояснювальний підпис під графіком
    f.append(text(420, 420, "Дрейф товарності: Generic-компоненти з часом зміщуються вправо у зону Commodity", size=11, italic=True, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'wardley-commodity-drift.svg'), W, H, *f,
           title="Дрейф товарності компонентів у часі")

def fig_tco_iceberg():
    """Айсберг прихованих операційних витрат SaaS."""
    W, H = 820, 460
    f = []

    # Небо та Вода
    f.append(fitbox(20, 50, 780, 120, "", fill="#f0f9ff", stroke="none"))  # Повітря
    f.append(fitbox(20, 170, 780, 260, "", fill="#e0f2fe", stroke="none")) # Вода

    # Лінія води
    f.append(line(20, 170, 800, 170, color="#0284c7", sw=2.5, dash="8 4"))
    f.append(text(790, 160, "Рівень видимості (Плата за ліцензії)", size=10, bold=True, color="#0284c7", anchor="end"))

    # Верхівка айсберга (Видима частина)
    f.append('<polygon points="340,170 420,70 500,170" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>')
    f.append(fitbox(360, 95, 120, 50, "Офіційний рахунок\nSaaS / Підписка\n($ / seat / GB)", size=10, bold=True, fill=AMBER_T, stroke=AMBER))

    # Занурена частина айсберга (Приховані операційні витрати)
    f.append('<polygon points="340,170 500,170 620,400 220,400" fill="#bae6fd" stroke="#0284c7" stroke-width="2"/>')

    # Блоки прихованих витрат усередині зануреної частини
    f.append(fitbox(260, 190, 320, 36, "Egress & Data Gravity Tax (Мережевий трафік)", size=10, bold=True, fill=RED_T, stroke=NEG))
    f.append(fitbox(240, 235, 360, 36, "Governance & Compliance (SOC2, ротація ключів, аудит)", size=10, fill=NEUT, stroke=INK))
    f.append(fitbox(250, 280, 340, 36, "Integration & Deprecation Maintenance (Оновлення SDK)", size=10, fill=NEUT, stroke=INK))
    f.append(fitbox(270, 325, 300, 36, "Vendor Escalation (15-30% щорічного зростання ціни)", size=10, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(290, 370, 260, 26, "Workaround Overhead (Обхід обмежень API)", size=9, fill=NEUT, stroke=INK))

    # Згадка відсотка
    f.append(text(120, 110, "Видимі витрати: ~20-30%", size=12, bold=True, color=AMBER, anchor="middle"))
    f.append(arrow(120, 125, 350, 125, color=AMBER, sw=1.5))

    f.append(text(120, 280, "Приховані операційні\nвитрати: ~70-80%", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(arrow(120, 300, 235, 300, color=NEG, sw=1.5))

    render(os.path.join(OUT, 'tco-iceberg.svg'), W, H, *f,
           title="Айсберг прихованих операційних витрат SaaS")

def fig_repatriation_crossover():
    """Точки беззбитковості та зони репатріації (SaaS vs Self-Hosted vs Custom)."""
    W, H = 840, 440
    f = []

    # Рамка та осі
    f.append(fitbox(20, 45, 800, 375, "", fill="#fafafa", stroke="#e5e7eb"))
    f.append(arrow(60, 380, 800, 380, color=INK, sw=2)) # X: Масштаб
    f.append(arrow(60, 380, 60, 60, color=INK, sw=2))   # Y: Сукупна вартість TCO

    f.append(text(790, 400, "Масштаб (N запитів/сек або ТБ даних) →", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(75, 75, "↑ Річні витрати TCO ($)", size=11, bold=True, color=INK, anchor="start"))

    # Крива 1: Managed SaaS (дешево на старті, круто вгору)
    f.append('<path d="M 60 360 C 200 350, 400 260, 760 80" fill="none" stroke="%s" stroke-width="3"/>' % NEG)
    f.append(text(765, 70, "Managed SaaS / PaaS", size=10, bold=True, color=NEG, anchor="start"))

    # Крива 2: Self-Hosted Open Source на Compute (фіксований старт, помірний ріст)
    f.append('<path d="M 60 270 L 300 260 L 760 200" fill="none" stroke="#2563eb" stroke-width="3"/>')
    f.append(text(765, 195, "Self-Hosted Open Source", size=10, bold=True, color="#2563eb", anchor="start"))

    # Крива 3: Custom In-House (дуже високий старт R&D, найпологіший ріст) - опущена до y=290
    f.append('<path d="M 60 200 L 760 170" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6 3"/>' % POS)
    f.append(text(765, 165, "Custom In-House", size=10, bold=True, color=POS, anchor="start"))

    # Точка перетину (Crossover Point N*) між SaaS і Self-Hosted
    f.append(circle(440, 238, 6, fill=AMBER, stroke=INK, sw=1.5))
    f.append(line(440, 238, 440, 380, color=AMBER, sw=1.5, dash="4 4"))
    f.append(text(440, 395, "N* (Точка перелому)", size=11, bold=True, color=AMBER, anchor="middle"))

    # Зона репатріації (поміщена у вищій вільній зоні x=460, y=55)
    f.append(fitbox(460, 55, 280, 80, "Зона репатріації\n\nSelf-hosted дешевше за SaaS,\nціна підписки перевищує ФОП SRE", size=10, bold=True, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'repatriation-crossover.svg'), W, H, *f,
           title="Графік точок перелому та зона репатріації")

def fig_decision_flow_mature():
    """Блок-схема зрілого фреймворку прийняття рішень Build vs Buy."""
    W, H = 920, 440
    f = []

    # Крок 1: Ядро?
    f.append(fitbox(40, 180, 160, 80, "1. Чи є це\nдиференціювальним\nCore-ядром?", size=11, bold=True, fill=BLUE_T, stroke="#2563eb"))
    f.append(arrow(200, 220, 260, 220))
    f.append(text(230, 210, "Ні", size=11, bold=True, color=INK, anchor="middle"))

    # Гілка ТАК для Ядра -> Build
    f.append(arrow(120, 180, 120, 100))
    f.append(text(135, 140, "Так", size=11, bold=True, color=POS, anchor="start"))
    f.append(fitbox(40, 40, 160, 60, "BUILD IN-HOUSE\nВласна розробка\n(Максимум контролю)", size=10, bold=True, fill=GREEN_T, stroke=POS))

    # Крок 2: Наявність рішення
    f.append(fitbox(260, 180, 170, 80, "2. Чи є зріле готове\nрішення на ринку\n(SaaS / Open Source)?", size=11, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(430, 220, 490, 220))
    f.append(text(460, 210, "Так", size=11, bold=True, color=INK, anchor="middle"))

    # Гілка НІ для рішення -> Build Minimal
    f.append(arrow(345, 260, 345, 340))
    f.append(text(360, 300, "Ні", size=11, bold=True, color=NEG, anchor="start"))
    f.append(fitbox(265, 340, 160, 60, "BUILD MINIMAL\nМінімальний шов\nі власна проста труба", size=10, fill=AMBER_T, stroke=AMBER))

    # Крок 3: Масштаб та суверенітет
    f.append(fitbox(490, 180, 180, 80, "3. Масштаб > N* або\nстрогий суверенітет\nданих / SLA?", size=11, bold=True, fill=AMBER_T, stroke=AMBER))

    # Гілка ТАК -> Self-Hosted Open Source
    f.append(arrow(580, 260, 580, 340))
    f.append(text(595, 300, "Так", size=11, bold=True, color=POS, anchor="start"))
    f.append(fitbox(490, 340, 180, 60, "SELF-HOSTED OPEN-SOURCE\nВласна інфраструктура\n(Репатріація)", size=10, bold=True, fill=GREEN_T, stroke=POS))

    # Гілка НІ -> Managed SaaS з шов-адаптером
    f.append(arrow(670, 220, 730, 220))
    f.append(text(700, 210, "Ні", size=11, bold=True, color=INK, anchor="middle"))
    f.append(fitbox(730, 180, 160, 80, "MANAGED SAAS / PAAS\nЗ ізоляцією через\nPort-Adapter (Шов)", size=10, bold=True, fill=BLUE_T, stroke="#2563eb"))

    render(os.path.join(OUT, 'decision-flow-mature.svg'), W, H, *f,
           title="Фреймворк прийняття рішень Build vs Buy у зрілій оптиці")

if __name__ == '__main__':
    fig_wardley_commodity_drift()
    fig_tco_iceberg()
    fig_repatriation_crossover()
    fig_decision_flow_mature()
    print("Figures generated successfully.")
