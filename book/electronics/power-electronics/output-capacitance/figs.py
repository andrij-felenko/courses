# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Вихідна ємність MOSFET (C_oss)»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

DIR = os.path.dirname(__file__)
IMG = os.path.join(DIR, "img")
os.makedirs(IMG, exist_ok=True)


def fig_coss_components():
    """Складові вихідної ємності: C_oss = C_ds + C_gd."""
    w, h = 760, 360
    f = []

    # Заголовок / підзаголовок усередині через text / fitbox
    # Ліва частина: еквівалентна схема транзистора
    f.append(rect(30, 40, 320, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(45, 52, 290, 28, "Еквівалентна схема ємностей", size=13, bold=True, fill="#e2e8f0", stroke="none"))

    # Виводи MOSFET: Затвор (G), Стік (D), Витік (S)
    # Стік зверху
    f.append(line(190, 85, 190, 120, color=LINE, sw=2))
    f.append(circle(190, 85, 4, fill=INK, stroke=LINE, sw=1))
    f.append(text(190, 75, "Стік (Drain, D)", size=12, bold=True))

    # Витік знизу
    f.append(line(190, 270, 190, 305, color=LINE, sw=2))
    f.append(circle(190, 305, 4, fill=INK, stroke=LINE, sw=1))
    f.append(text(190, 322, "Витік (Source, S)", size=12, bold=True))

    # Затвор зліва
    f.append(line(55, 195, 110, 195, color=LINE, sw=2))
    f.append(circle(55, 195, 4, fill=INK, stroke=LINE, sw=1))
    f.append(text(80, 185, "Затвор (G)", size=11, bold=True))

    # Канал транзистора (вертикальні лінії ключа)
    f.append(line(140, 160, 140, 230, color=LINE, sw=3))
    f.append(line(150, 150, 150, 240, color=LINE, sw=1.5, dash="4,3"))
    f.append(line(150, 160, 190, 160, color=LINE, sw=2))
    f.append(line(150, 230, 190, 230, color=LINE, sw=2))
    f.append(line(190, 120, 190, 160, color=LINE, sw=2))
    f.append(line(190, 230, 190, 270, color=LINE, sw=2))

    # Ємність C_gd (Міллера) між D і G
    f.append(line(190, 135, 230, 135, color=POS, sw=1.5))
    f.append(line(230, 135, 230, 180, color=POS, sw=1.5))
    f.append(line(230, 180, 110, 180, color=POS, sw=1.5))
    f.append(line(110, 180, 110, 195, color=POS, sw=1.5))
    # Обкладки C_gd
    f.append(rect(218, 150, 24, 16, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    f.append(text(230, 162, "C_gd", size=10, color=POS, bold=True))

    # Ємність C_ds (p-n перехід) паралельно каналу
    f.append(line(190, 145, 290, 145, color=NEG, sw=1.5))
    f.append(line(290, 145, 290, 185, color=NEG, sw=1.5))
    f.append(rect(275, 185, 30, 20, fill="#dbeafe", stroke=NEG, sw=1.5, rx=3))
    f.append(text(290, 199, "C_ds", size=10, color=NEG, bold=True))
    f.append(line(290, 205, 290, 245, color=NEG, sw=1.5))
    f.append(line(290, 245, 190, 245, color=NEG, sw=1.5))

    # Права частина: формульний підсумок та фізичне походження
    f.append(rect(380, 40, 350, 290, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(395, 52, 320, 28, "Визначення вихідної ємності", size=13, bold=True, fill="#f1f5f9", stroke="none"))

    f.append(fitbox(395, 95, 320, 48, "C_oss = C_ds + C_gd\n(вимірюється при замкненому затвор-витік V_gs = 0)", size=12, bold=True, fill="#eff6ff", stroke=NEG))

    tb1, _, _ = textbox(555, 185, "C_ds — ємність p-n переходу сток-витік\n(об'ємний заряд збідненої зони діода тіла)\n\nC_gd — міллерівська ємність перекриття\n(затвор над областю дрейфу стоку)", size=11, pad=10, fill="#f8fafc", stroke=LINE, min_w=310)
    f.append(tb1)

    f.append(fitbox(395, 255, 320, 60, "Обидві ємності підключені до стоку D.\nПри зміні напруги V_ds струм заряду\nпротікає через обидві паралельно.", size=11, fill="#fef3c7", stroke="#d97706"))

    render(os.path.join(IMG, "coss-components.svg"), w, h, *f)


def fig_depletion_width_coss():
    """Розширення збідненої зони та нелінійне падіння Coss."""
    w, h = 820, 380
    f = []

    # Лівий блок: фізична структура p-n переходу при 0 В та при високій напрузі
    f.append(rect(20, 30, 370, 330, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(35, 42, 340, 28, "Фізика збідненого шару (SCR)", size=12, bold=True, fill="#e2e8f0", stroke="none"))

    # Стан 1: Vds = 0 В (вузька збіднена зона -> гігантська ємність)
    f.append(rect(40, 85, 155, 145, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(117, 102, "V_ds = 0 В", size=11, bold=True, color=POS))
    f.append(rect(48, 112, 139, 32, fill="#fecaca", stroke="none"))
    f.append(text(117, 132, "p-body (дірки)", size=10, color="#991b1b"))
    # Збіднена зона W0
    f.append(rect(48, 144, 139, 14, fill="#fef08a", stroke="#ca8a04", sw=1))
    f.append(text(117, 155, "Збіднена зона W (вузька)", size=9, color="#854d0e", bold=True))
    f.append(rect(48, 158, 139, 62, fill="#bfdbfe", stroke="none"))
    f.append(text(117, 192, "n- дрейфовий шар", size=10, color="#1e40af"))
    f.append(fitbox(40, 238, 155, 42, "C = ε·A / W\nW мінімальна →\nC_oss досягає нФ!", size=10, fill="#fef2f2", stroke=POS))

    # Стан 2: Vds = 400 В (широка збіднена зона -> мізерна ємність)
    f.append(rect(215, 85, 155, 145, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(292, 102, "V_ds = 400 В", size=11, bold=True, color=NEG))
    f.append(rect(223, 112, 139, 20, fill="#fecaca", stroke="none"))
    f.append(text(292, 126, "p-body", size=10, color="#991b1b"))
    # Збіднена зона W_high
    f.append(rect(223, 132, 139, 78, fill="#fef08a", stroke="#ca8a04", sw=1))
    f.append(text(292, 168, "Збіднена зона W(V)\n(розширена на весь шар)", size=9, color="#854d0e", bold=True))
    f.append(rect(223, 210, 139, 12, fill="#bfdbfe", stroke="none"))
    f.append(text(292, 220, "n+ підкладка", size=9, color="#1e40af"))
    f.append(fitbox(215, 238, 155, 42, "W зростає в десятки разів →\nC_oss падає до\nдесятків пФ!", size=10, fill="#eff6ff", stroke=NEG))

    f.append(fitbox(35, 292, 340, 58, "У Superjunction MOSFET бічне збіднення стовпчиків\nспричиняє обвал ємності у 100-1000 разів уже при 20-50 В.", size=10, fill="#f1f5f9", stroke=LINE))

    # Правий блок: графік C_oss(V_ds) у логарифмічному масштабі
    f.append(rect(410, 30, 390, 330, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(425, 42, 360, 28, "Крива нелінійності C_oss від напруги стоку", size=12, bold=True, fill="#f1f5f9", stroke="none"))

    # Осі графіка
    # Y-вісь (log C_oss)
    f.append(arrow(460, 305, 460, 85, color=LINE, sw=1.8))
    f.append(text(460, 78, "C_oss (пФ, log)", size=11, bold=True))
    # X-вісь (V_ds)
    f.append(arrow(460, 305, 770, 305, color=LINE, sw=1.8))
    f.append(text(760, 322, "V_ds (В)", size=11, bold=True))

    # Позначки осі Y
    f.append(line(455, 110, 460, 110, color=LINE, sw=1.2))
    f.append(text(448, 114, "10000", size=9, anchor="end"))
    f.append(line(455, 160, 460, 160, color=LINE, sw=1.2))
    f.append(text(448, 164, "1000", size=9, anchor="end"))
    f.append(line(455, 210, 460, 210, color=LINE, sw=1.2))
    f.append(text(448, 214, "100", size=9, anchor="end"))
    f.append(line(455, 260, 460, 260, color=LINE, sw=1.2))
    f.append(text(448, 264, "10", size=9, anchor="end"))

    # Позначки осі X
    f.append(line(460, 305, 460, 310, color=LINE, sw=1.2))
    f.append(text(460, 322, "0", size=9))
    f.append(line(510, 305, 510, 310, color=LINE, sw=1.2))
    f.append(text(510, 322, "20", size=9))
    f.append(line(580, 305, 580, 310, color=LINE, sw=1.2))
    f.append(text(580, 322, "100", size=9))
    f.append(line(680, 305, 680, 310, color=LINE, sw=1.2))
    f.append(text(680, 322, "400", size=9))

    # Крива кремнієвого Superjunction MOSFET (різкий обвал при 20-40 В)
    curve_sj = "M 465 115 Q 495 125 510 160 T 530 240 Q 580 255 680 265 T 750 270"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (curve_sj, POS))
    f.append(text(640, 245, "Superjunction (обвал)", size=10, color=POS, bold=True))

    # Крива звичайного планарного Si MOSFET (1/sqrt(V))
    curve_planar = "M 465 140 Q 520 180 580 215 T 750 245"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' % (curve_planar, MUTED))
    f.append(text(680, 205, "Планарний Si", size=9, color=MUTED, italic=True))

    # Крива GaN HEMT (низька початкова ємність, плавний спад)
    curve_gan = "M 465 195 Q 520 220 580 245 T 750 260"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="2,2"/>' % (curve_gan, FIELD))
    f.append(text(580, 282, "GaN HEMT", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "depletion-width-coss.svg"), w, h, *f)


def fig_coss_energy_integral():
    """Інтегральна енергія E_oss та еквівалентні ємності Co(er) і Co(tr)."""
    w, h = 800, 360
    f = []

    # Ліва панель: графік C(v) та v*C(v) з поясненням площ
    f.append(rect(25, 30, 365, 305, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(40, 42, 335, 26, "Площа заряду Q_oss vs енергії E_oss", size=12, bold=True, fill="#e2e8f0", stroke="none"))

    # Графік C(V)
    f.append(arrow(65, 280, 65, 85, color=LINE, sw=1.5))
    f.append(arrow(65, 280, 360, 280, color=LINE, sw=1.5))
    f.append(text(65, 78, "C(v)", size=10, bold=True))
    f.append(text(355, 295, "v (В)", size=10, bold=True))

    # Заштрихована крива Coss(v)
    f.append('<path d="M 70 100 Q 90 120 110 200 Q 150 250 330 265 L 330 280 L 70 280 Z" fill="#dbeafe" opacity="0.6"/>')
    f.append('<path d="M 70 100 Q 90 120 110 200 Q 150 250 330 265" fill="none" stroke="%s" stroke-width="2"/>' % NEG)
    f.append(text(210, 210, "Q_oss = ∫ C_oss(v) dv", size=11, color=NEG, bold=True))
    f.append(text(210, 230, "(вся площа під кривою)", size=9, color=MUTED))

    # Крива v * C(v)
    f.append('<path d="M 70 280 Q 100 240 120 150 Q 160 210 330 240" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,2"/>' % POS)
    f.append(text(175, 145, "v · C_oss(v)", size=10, color=POS, bold=True))
    f.append(text(230, 160, "E_oss = ∫ v · C_oss(v) dv", size=11, color=POS, bold=True))

    f.append(fitbox(40, 290, 335, 36, "При низькій напрузі C(v) гігантська, але v ≈ 0,\nтому для енергії E_oss початковий пік важить мало!", size=9, fill="#fef3c7", stroke="#d97706"))

    # Права панель: порівняння Co(er) та Co(tr)
    f.append(rect(410, 30, 365, 305, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(425, 42, 335, 26, "Дві еквівалентні ємності", size=12, bold=True, fill="#f1f5f9", stroke="none"))

    # Блок C_o(er)
    f.append(rect(425, 78, 335, 95, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    f.append(text(592, 96, "C_o(er) — еквівалентна за енергією", size=11, color=POS, bold=True))
    f.append(text(592, 116, "E_oss = ½ · C_o(er) · V_ds²", size=11, bold=True))
    f.append(text(592, 134, "C_o(er) = (2 / V_ds²) · ∫ v · C_oss(v) dv", size=10, color=LINE))
    f.append(text(592, 155, "Призначення: розрахунок теплових втрат P = f · E_oss", size=9, color="#991b1b", bold=True))

    # Блок C_o(tr)
    f.append(rect(425, 185, 335, 95, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    f.append(text(592, 203, "C_o(tr) — еквівалентна за часом/зарядом", size=11, color=NEG, bold=True))
    f.append(text(592, 223, "Q_oss = C_o(tr) · V_ds", size=11, bold=True))
    f.append(text(592, 241, "C_o(tr) = (1 / V_ds) · ∫ C_oss(v) dv", size=10, color=LINE))
    f.append(text(592, 262, "Призначення: розрахунок dead-time (часу перезаряду)", size=9, color="#1e40af", bold=True))

    # Висновок унизу
    f.append(fitbox(425, 290, 335, 36, "Через пік ємності при 0 В завжди C_o(tr) > C_o(er)\n(у Superjunction різниця досягає 2-4 разів!)", size=9, fill="#f1f5f9", stroke=LINE))

    render(os.path.join(IMG, "coss-energy-integral.svg"), w, h, *f)


def fig_hard_switching_coss_dump():
    """Жорстке перемикання: розсіювання накопиченої в Coss енергії в каналі."""
    w, h = 780, 360
    f = []

    # Фаза 1: Вимкнений стан (накопичення енергії від шини V_bus)
    f.append(rect(25, 35, 345, 300, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(40, 48, 315, 28, "1. Ключ вимкнено (OFF): заряд ємності", size=12, bold=True, fill="#e2e8f0", stroke="none"))

    # Джерело V_bus та навантаження
    f.append(circle(80, 120, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(80, 124, "V_bus", size=10, bold=True))
    f.append(line(80, 104, 80, 90, color=LINE, sw=1.5))
    f.append(line(80, 90, 280, 90, color=LINE, sw=1.5))
    f.append(line(80, 136, 80, 270, color=LINE, sw=1.5))
    f.append(line(80, 270, 280, 270, color=LINE, sw=1.5))

    # Навантаження (дросель / резистор)
    f.append(rect(170, 80, 60, 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    f.append(text(200, 94, "Навант.", size=9))
    f.append(line(230, 90, 280, 90, color=LINE, sw=1.5))

    # Розімкнений ключ і заряджена Coss
    f.append(line(280, 90, 280, 130, color=LINE, sw=1.5))
    f.append(line(280, 130, 260, 165, color=LINE, sw=2))  # розімкнений контакт
    f.append(line(280, 180, 280, 270, color=LINE, sw=1.5))

    # Coss паралельно
    f.append(line(280, 115, 320, 115, color=POS, sw=1.5))
    f.append(line(320, 115, 320, 135, color=POS, sw=1.5))
    f.append(rect(308, 135, 24, 18, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    f.append(text(320, 148, "C_oss", size=9, color=POS, bold=True))
    f.append(line(320, 153, 320, 245, color=POS, sw=1.5))
    f.append(line(320, 245, 280, 245, color=POS, sw=1.5))
    f.append(text(320, 200, "+ Q_oss\nE_oss", size=9, color=POS, bold=True))

    f.append(fitbox(40, 225, 220, 52, "Напруга на ключі = V_bus (400 В)\nВихідна ємність заряджена:\nE_oss = ½ · C_o(er) · V_bus²", size=9, fill="#ffffff", stroke=LINE))

    # Фаза 2: Відмикання каналу (миттєвий розряд ємності у власний опір каналу)
    f.append(rect(395, 35, 360, 300, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(410, 48, 330, 28, "2. Ключ вмикається (ON): розряд у тепло", size=12, bold=True, fill="#fee2e2", stroke=POS))

    # Ключ замкнений, струм розряду зациклений
    f.append(rect(480, 130, 50, 100, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    f.append(text(505, 150, "Канал", size=10, bold=True, color=POS))
    f.append(text(505, 170, "R_ds(on)", size=9, color=POS))
    f.append(text(505, 195, "ТЕПЛО", size=11, bold=True, color=POS))

    # Струм розряду
    f.append(arrow(570, 140, 520, 140, color=POS, sw=2))
    f.append(arrow(520, 220, 570, 220, color=POS, sw=2))
    f.append(line(570, 140, 570, 160, color=POS, sw=1.5))
    f.append(rect(558, 160, 24, 18, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    f.append(text(570, 173, "C_oss", size=9, color=POS, bold=True))
    f.append(line(570, 178, 570, 220, color=POS, sw=1.5))

    f.append(fitbox(410, 245, 330, 75, "Канал закорочує власну заряджену ємність!\n100% енергії E_oss виділяється всередині кристала.\nВтрати перемикання:\nP_loss = f_sw · E_oss = ½ · f_sw · C_o(er) · V_bus²", size=10, bold=True, fill="#fff7ed", stroke="#ea580c"))

    render(os.path.join(IMG, "hard-switching-coss-dump.svg"), w, h, *f)


def fig_zvs_resonance():
    """М'яка комутація (ZVS): резонансний розряд Coss перед відкриттям каналу."""
    w, h = 800, 360
    f = []

    # Схема напівмоста з індуктивністю
    f.append(rect(20, 30, 380, 310, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(35, 42, 350, 28, "Резонансний перезаряд у мертвому часі (ZVS)", size=12, bold=True, fill="#e2e8f0", stroke="none"))

    # Шина живлення
    f.append(line(60, 90, 220, 90, color=POS, sw=2))
    f.append(text(50, 94, "V_bus", size=10, bold=True, color=POS))
    f.append(line(60, 310, 220, 310, color=NEG, sw=2))
    f.append(text(50, 314, "GND", size=10, bold=True, color=NEG))

    # Верхній ключ Q1 з ємністю Coss1
    f.append(rect(100, 110, 45, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(122, 134, "Q1", size=10, bold=True))
    f.append(line(165, 100, 165, 118, color=LINE, sw=1.2))
    f.append(rect(146, 118, 38, 20, fill="#eff6ff", stroke=NEG, sw=1.2, rx=2))
    f.append(text(165, 132, "C_oss1", size=9, color=NEG, bold=True))
    f.append(line(165, 138, 165, 160, color=LINE, sw=1.2))

    # Середня точка (Switch Node, SW)
    f.append(circle(122, 185, 4, fill=INK, stroke=LINE, sw=1))
    f.append(text(95, 189, "V_sw", size=10, bold=True))
    f.append(line(122, 90, 122, 110, color=LINE, sw=1.5))
    f.append(line(122, 150, 122, 220, color=LINE, sw=1.5))
    f.append(line(122, 260, 122, 310, color=LINE, sw=1.5))

    # Нижній ключ Q2 з ємністю Coss2
    f.append(rect(100, 220, 45, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(122, 244, "Q2", size=10, bold=True))
    f.append(line(165, 210, 165, 228, color=LINE, sw=1.2))
    f.append(rect(146, 228, 38, 20, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
    f.append(text(165, 242, "C_oss2", size=9, color=POS, bold=True))
    f.append(line(165, 248, 165, 270, color=LINE, sw=1.2))

    # Індуктивний струм витягує заряд
    f.append(line(122, 185, 270, 185, color=FIELD, sw=2))
    f.append(arrow(180, 185, 250, 185, color=FIELD, sw=2))
    f.append(rect(270, 172, 70, 26, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(305, 189, "L_res / I_mag", size=10, color=FIELD, bold=True))

    f.append(fitbox(35, 280, 350, 50, "Струм індуктивності розряджає C_oss2 до 0 В\nта заряджає C_oss1 до V_bus у мертвому часі (t_dead).\nКанал Q2 вмикається при V_ds = 0 → нульові втрати!", size=9, fill="#f1f5f9", stroke=LINE))

    # Права панель: часові діаграми напруги та струму затвора
    f.append(rect(420, 30, 360, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(435, 42, 330, 28, "Хронограма перемикання ZVS", size=12, bold=True, fill="#f1f5f9", stroke="none"))

    # Графік V_ds нижнього ключа
    f.append(arrow(450, 160, 450, 85, color=LINE, sw=1.2))
    f.append(arrow(450, 160, 760, 160, color=LINE, sw=1.2))
    f.append(text(450, 80, "V_ds(Q2)", size=10, bold=True))

    # Спад V_ds до нуля під час dead-time
    f.append(line(450, 95, 520, 95, color=POS, sw=2))
    f.append(line(520, 95, 600, 160, color=POS, sw=2))  # резонансний спад
    f.append(line(600, 160, 750, 160, color=POS, sw=2))
    f.append(text(560, 120, "Резонанс", size=9, color=POS))

    # Графік V_gs (імпульс затвора)
    f.append(arrow(450, 265, 450, 190, color=LINE, sw=1.2))
    f.append(arrow(450, 265, 760, 265, color=LINE, sw=1.2))
    f.append(text(450, 185, "V_gs(Q2)", size=10, bold=True))

    # Затвор відкривається ТІЛЬКИ після досягнення 0 В
    f.append(line(450, 265, 610, 265, color=NEG, sw=2))
    f.append(line(610, 265, 610, 210, color=NEG, sw=2))
    f.append(line(610, 210, 750, 210, color=NEG, sw=2))

    # Зона dead-time
    f.append(rect(520, 75, 90, 195, fill="#fef08a", stroke="#ca8a04", sw=1))
    f.append(text(565, 255, "t_dead", size=10, color="#854d0e", bold=True))

    f.append(fitbox(435, 275, 330, 55, "Критерій ZVS: енергії в L_res має вистачити на заряд 2·C_oss:\n½ · L · I_peak² > 2 · E_oss(V_bus)\nt_dead ≥ 2 · Q_oss / I_mag = 2 · C_o(tr) · V_bus / I_mag", size=9, fill="#eff6ff", stroke=NEG))

    render(os.path.join(IMG, "zvs-resonance.svg"), w, h, *f)


def fig_coss_hysteresis_loop():
    """Гістерезисні втрати заряду вихідної ємності (C_oss Hysteresis) у Superjunction MOSFET."""
    w, h = 760, 360
    f = []

    # Ліва панель: петля гістерезису Q-V
    f.append(rect(25, 30, 360, 305, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(40, 42, 330, 28, "Петля гістерезису заряду Q(v)", size=12, bold=True, fill="#e2e8f0", stroke="none"))

    # Осі Q vs V
    f.append(arrow(65, 275, 65, 85, color=LINE, sw=1.5))
    f.append(arrow(65, 275, 360, 275, color=LINE, sw=1.5))
    f.append(text(65, 78, "Q (нКл)", size=10, bold=True))
    f.append(text(355, 290, "V_ds (В)", size=10, bold=True))

    # Петля: траєкторія заряду (вгору) та розряду (вниз)
    f.append('<path d="M 70 270 Q 95 150 180 110 T 330 100 Q 200 135 110 210 Z" fill="#fee2e2" opacity="0.7"/>')
    f.append('<path d="M 70 270 Q 95 150 180 110 T 330 100" fill="none" stroke="%s" stroke-width="2"/>' % POS)
    f.append('<path d="M 330 100 Q 200 135 110 210 T 70 270" fill="none" stroke="%s" stroke-width="2"/>' % NEG)

    f.append(arrow(130, 135, 145, 128, color=POS, sw=2))
    f.append(text(150, 118, "Заряд (dv/dt > 0)", size=9, color=POS, bold=True))

    f.append(arrow(170, 155, 150, 170, color=NEG, sw=2))
    f.append(text(175, 175, "Розряд (dv/dt < 0)", size=9, color=NEG, bold=True))

    f.append(fitbox(40, 225, 330, 48, "Площа петлі = E_oss,hyst = ∮ v dq\nЦя енергія НЕ повертається в резонансний контур,\nа перетворюється на тепло в кристалі навіть при ідеальному ZVS!", size=9, fill="#fef2f2", stroke=POS))

    # Права панель: фізична природа та наслідки для технологій
    f.append(rect(405, 30, 330, 305, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(420, 42, 300, 28, "Причини та порівняння технологій", size=12, bold=True, fill="#f1f5f9", stroke="none"))

    tb, _, _ = textbox(570, 125, "Фізичні механізми гістерезису:\n• Захоплення носіїв на глибоких пастках\n  між p/n стовпчиками Superjunction.\n• Не-квазістатичний опір дрейфу (NQS)\n  під час надшвидкого збіднення.\n• Поляризація діелектричних шарів.", size=10, pad=8, fill="#f8fafc", stroke=LINE, min_w=290)
    f.append(tb)

    f.append(fitbox(420, 185, 300, 135, "Рівень гістерезисних втрат (при 400 В):\n\n• Si Superjunction: E_hyst ≈ 1.0–5.0 мкДж\n  (до 2–5 Вт тепла на частоті 500 кГц!)\n\n• SiC MOSFET: E_hyst < 0.1 мкДж (мізерний)\n\n• GaN HEMT: E_hyst ≈ 0 (гістерезис відсутній,\n  ідеально для високих частот МГц-діапазону)", size=9, fill="#eff6ff", stroke=NEG))

    render(os.path.join(IMG, "coss-hysteresis-loop.svg"), w, h, *f)


if __name__ == "__main__":
    fig_coss_components()
    fig_depletion_width_coss()
    fig_coss_energy_integral()
    fig_hard_switching_coss_dump()
    fig_zvs_resonance()
    fig_coss_hysteresis_loop()
    print("Всі 6 фігур згенеровано успішно.")
