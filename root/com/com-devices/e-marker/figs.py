# -*- coding: utf-8 -*-
"""Фігури для теми «E-Marker: чип автентифікації кабелю».
Генерує SVG-діаграми у теку ./img/.
Запуск: python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_emarker_paddle_card():
    """Будова штекера Type-C з монтажною платою paddle card та чипом E-Marker."""
    W, H = 820, 360
    parts = []

    # Зовнішній корпус штекера (overmold)
    parts.append(rect(40, 50, 740, 280, fill="#f8fafc", stroke="#64748b", sw=2, rx=12))
    parts.append(text(200, 78, "Металевий роз'єм Type-C", size=13, color=MUTED, bold=True))
    parts.append(text(560, 78, "Друкована плата Paddle Card усередині штекера", size=13, color=MUTED, bold=True))

    # Металева гільза штекера ліворуч
    parts.append(rect(60, 95, 260, 215, fill="#f1f5f9", stroke="#475569", sw=2, rx=6))
    
    # Піни роз'єму
    pin_y_list = [115, 145, 175, 215, 255, 285]
    pin_names = ["GND (A1, A12, B1, B12)", "VBUS (A4, A9, B4, B9)", "CC1 / CC (A5)", "VCONN / CC2 (B5)", "D+ / D- (A6, A7)", "RX/TX SuperSpeed (4 пари)"]
    pin_colors = ["#1e293b", POS, "#0284c7", "#7c3aed", "#d97706", "#059669"]
    
    for y, name, col in zip(pin_y_list, pin_names, pin_colors):
        parts.append(line(70, y, 310, y, color=col, sw=3))
        parts.append(circle(75, y, 4, fill=col, stroke="#ffffff", sw=1))
        parts.append(circle(305, y, 4, fill=col, stroke="#ffffff", sw=1))
        parts.append(text(190, y - 5, name, size=10, color=col, bold=True))

    # Плата Paddle Card праворуч
    parts.append(rect(340, 95, 420, 215, fill="#e2e8f0", stroke="#334155", sw=2, rx=6))

    # Чип E-Marker на платі
    chip_x, chip_y, chip_w, chip_h = 500, 130, 150, 130
    parts.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#1e293b", stroke="#0f172a", sw=2, rx=4))
    parts.append(text(chip_x + chip_w/2, chip_y + 22, "E-Marker IC", size=12, color="#ffffff", bold=True))
    parts.append(text(chip_x + chip_w/2, chip_y + 42, "DFN-6 / WLCSP-6", size=10, color="#94a3b8"))
    parts.append(text(chip_x + chip_w/2, chip_y + 64, "BMC Transceiver", size=10, color="#38bdf8"))
    parts.append(text(chip_x + chip_w/2, chip_y + 84, "OTP / ROM (VDO)", size=10, color="#4ade80"))
    parts.append(text(chip_x + chip_w/2, chip_y + 106, "Ra = 1 кОм до GND", size=10, color="#fb7185"))

    # З'єднання від пінів до плати і чипа
    # GND лінія вгорі
    parts.append(line(310, 115, 575, 115, color="#1e293b", sw=2.5))
    parts.append(line(575, 115, 575, 130, color="#1e293b", sw=2.5))
    parts.append(line(575, 115, 750, 115, color="#1e293b", sw=2.5))
    
    # VBUS (наскрізний товстий провідник)
    parts.append(line(310, 145, 480, 145, color=POS, sw=5))
    parts.append(line(480, 145, 480, 105, color=POS, sw=5))
    parts.append(line(480, 105, 750, 105, color=POS, sw=5))
    parts.append(text(700, 95, "VBUS (до 5 А / 48 В)", size=9, color=POS, bold=True))

    # CC наскрізний зв'язок і відвід до E-Marker
    parts.append(line(310, 175, 500, 175, color="#0284c7", sw=2.5))
    parts.append(line(310, 175, 470, 175, color="#0284c7", sw=2.5))
    parts.append(line(470, 175, 470, 270, color="#0284c7", sw=2))
    parts.append(line(470, 270, 750, 270, color="#0284c7", sw=2.5))
    parts.append(text(700, 260, "CC дріт", size=9, color="#0284c7", bold=True))

    # VCONN до піна живлення E-Marker (заходить зліва на пін чипа)
    parts.append(line(310, 215, 500, 215, color="#7c3aed", sw=2.5))
    
    # Конденсатор розв'язки VCONN
    parts.append(rect(410, 190, 30, 20, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    parts.append(text(425, 204, "C1", size=10, color="#854d0e", bold=True))
    parts.append(line(425, 215, 425, 210, color="#7c3aed", sw=1.5))
    parts.append(line(425, 190, 425, 115, color="#1e293b", sw=1.5))
    parts.append(text(425, 235, "100 нФ", size=9, color=MUTED))

    # D+/D- та SuperSpeed наскрізні
    parts.append(line(310, 255, 750, 255, color="#d97706", sw=2, dash="4,3"))
    parts.append(line(310, 285, 750, 285, color="#059669", sw=3))
    parts.append(text(695, 300, "Кабельний джгут", size=10, color=MUTED, bold=True))

    render(os.path.join(IMG, "emarker-paddle-card.svg"), W, H, *parts,
           title="Анатомія штекера Type-C з платою Paddle Card та чипом E-Marker")


def fig_vconn_ra_circuit():
    """Схема аналогового детектування опору Ra та комутації шини VCONN."""
    W, H = 820, 360
    parts = []

    # Блок Джерела (Source DFP)
    src_x, src_y, src_w, src_h = 40, 50, 310, 280
    parts.append(rect(src_x, src_y, src_w, src_h, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=8))
    parts.append(text(src_x + src_w/2, src_y + 24, "Джерело живлення (Source / DFP)", size=13, color="#1e40af", bold=True))

    # Внутрішній комутатор VCONN та компаратори
    parts.append(rect(60, 90, 140, 70, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(130, 115, "PD Контролер", size=11, color="#1e3a8a", bold=True))
    parts.append(text(130, 135, "АЦП / Компаратори CC", size=10, color="#1d4ed8"))
    parts.append(text(130, 150, "Rp = 10 кОм (3 А / 5 В)", size=9, color="#1e40af"))

    parts.append(rect(60, 180, 140, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    parts.append(text(130, 205, "Ключ VCONN (FET)", size=11, color="#b45309", bold=True))
    parts.append(text(130, 225, "VCONN = 5.0 В", size=10, color="#92400e"))
    parts.append(text(130, 240, "Струмовий захист OCP", size=9, color="#b45309"))

    # Виводи джерела CC1 та CC2
    parts.append(line(200, 120, 350, 120, color="#0284c7", sw=2.5))
    parts.append(text(275, 110, "CC1 (Активна лінія)", size=10, color="#0284c7", bold=True))
    parts.append(circle(350, 120, 4, fill="#0284c7", stroke="#ffffff", sw=1))

    parts.append(line(200, 215, 350, 215, color="#7c3aed", sw=2.5))
    parts.append(text(275, 205, "CC2 (VCONN лінія)", size=10, color="#7c3aed", bold=True))
    parts.append(circle(350, 215, 4, fill="#7c3aed", stroke="#ffffff", sw=1))

    # Кабельна збірка з E-Marker посередині
    cab_x, cab_y, cab_w, cab_h = 390, 50, 190, 280
    parts.append(rect(cab_x, cab_y, cab_w, cab_h, fill="#faf5ff", stroke="#a855f7", sw=2, rx=8))
    parts.append(text(cab_x + cab_w/2, cab_y + 24, "Кабель з E-Marker", size=13, color="#6b21a8", bold=True))

    # Наскрізна лінія CC
    parts.append(line(350, 120, 620, 120, color="#0284c7", sw=2.5))
    
    # E-Marker всередині кабелю підключений до CC2
    parts.append(line(350, 215, 440, 215, color="#7c3aed", sw=2.5))
    parts.append(rect(440, 175, 100, 80, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=4))
    parts.append(text(490, 198, "E-Marker IC", size=11, color="#581c87", bold=True))
    parts.append(text(490, 218, "Ra = 1.0 кОм", size=10, color="#7e22ce", bold=True))
    parts.append(text(490, 238, "(0.8–1.2 кОм)", size=9, color=MUTED))

    # З'єднання Ra з землею
    parts.append(line(490, 255, 490, 290, color="#1e293b", sw=2))
    parts.append(line(475, 290, 505, 290, color="#1e293b", sw=2))
    parts.append(line(480, 295, 500, 295, color="#1e293b", sw=1.5))
    parts.append(line(485, 300, 495, 300, color="#1e293b", sw=1))

    # Пристрій споживач праворуч (Sink UFP)
    snk_x, snk_y, snk_w, snk_h = 620, 50, 160, 280
    parts.append(rect(snk_x, snk_y, snk_w, snk_h, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=8))
    parts.append(text(snk_x + snk_w/2, snk_y + 24, "Споживач (Sink)", size=13, color="#15803d", bold=True))

    parts.append(circle(620, 120, 4, fill="#0284c7", stroke="#ffffff", sw=1))
    parts.append(rect(640, 95, 120, 60, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(700, 120, "Rd = 5.1 кОм", size=11, color="#14532d", bold=True))
    parts.append(text(700, 140, "(на обох CC)", size=10, color="#166534"))
    parts.append(line(620, 120, 640, 120, color="#0284c7", sw=2))

    # Пояснювальний блок унизу
    parts.append(rect(50, 300, 290, 25, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(195, 317, "CC1: V(Rd) = 1.7 В  |  CC2: V(Ra) = 0.45 В", size=10, color=INK, bold=True))

    render(os.path.join(IMG, "vconn-ra-circuit.svg"), W, H, *parts,
           title="Аналогова схема визначення кабелю з маркером за опором Ra")


def fig_sop_addressing_layers():
    """Адресація повідомлень у протоколі USB PD: SOP, SOP' та SOP''."""
    W, H = 820, 370
    parts = []

    # Джерело DFP ліворуч
    parts.append(rect(40, 60, 170, 230, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=8))
    parts.append(text(125, 90, "DFP / Хост", size=14, color="#1e40af", bold=True))
    parts.append(text(125, 115, "Порт-партнер", size=11, color=MUTED))
    parts.append(text(125, 145, "Генератор пакетів:", size=10, color=INK))
    parts.append(text(125, 165, "• SOP (до Sink)", size=10, color="#16a34a", bold=True))
    parts.append(text(125, 185, "• SOP' (до Штекера 1)", size=10, color="#9333ea", bold=True))
    parts.append(text(125, 205, "• SOP'' (до Штекера 2)", size=10, color="#c026d3", bold=True))
    parts.append(text(125, 240, "Подає VCONN (5 В)", size=10, color="#7c3aed", bold=True))

    # Штекер 1 (Plug 1 - ближній)
    parts.append(rect(250, 90, 150, 170, fill="#faf5ff", stroke="#a855f7", sw=2, rx=6))
    parts.append(text(325, 115, "Штекер 1 (Ближній)", size=12, color="#6b21a8", bold=True))
    parts.append(rect(265, 130, 120, 45, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=4))
    parts.append(text(325, 150, "E-Marker 1", size=11, color="#581c87", bold=True))
    parts.append(text(325, 165, "Адреса: SOP'", size=10, color="#7e22ce", bold=True))
    parts.append(text(325, 195, "Sync-1 Sync-1", size=10, color=MUTED))
    parts.append(text(325, 210, "Sync-1 Sync-2", size=10, color="#9333ea", bold=True))
    parts.append(text(325, 240, "Живиться від VCONN", size=9, color=MUTED))

    # Штекер 2 (Plug 2 - дальній)
    parts.append(rect(440, 90, 150, 170, fill="#fdf4ff", stroke="#d946ef", sw=2, rx=6))
    parts.append(text(515, 115, "Штекер 2 (Дальній)", size=12, color="#86198f", bold=True))
    parts.append(rect(455, 130, 120, 45, fill="#fae8ff", stroke="#c026d3", sw=1.5, rx=4))
    parts.append(text(515, 150, "E-Marker 2", size=11, color="#701a75", bold=True))
    parts.append(text(515, 165, "Адреса: SOP''", size=10, color="#a21caf", bold=True))
    parts.append(text(515, 195, "Sync-1 Sync-1", size=10, color=MUTED))
    parts.append(text(515, 210, "Sync-3 Sync-3", size=10, color="#c026d3", bold=True))
    parts.append(text(515, 240, "(Опціональний чип)", size=9, color=MUTED))

    # Споживач UFP праворуч
    parts.append(rect(630, 60, 150, 230, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=8))
    parts.append(text(705, 90, "UFP / Пристрій", size=14, color="#15803d", bold=True))
    parts.append(text(705, 115, "Порт-партнер (Sink)", size=11, color=MUTED))
    parts.append(text(705, 150, "Приймає пакети:", size=10, color=INK))
    parts.append(text(705, 175, "Тільки SOP", size=12, color="#16a34a", bold=True))
    parts.append(text(705, 200, "Sync-1 Sync-1", size=10, color=MUTED))
    parts.append(text(705, 215, "Sync-1 Sync-1", size=10, color="#16a34a", bold=True))
    parts.append(text(705, 250, "Ігнорує SOP'/SOP''", size=10, color=MUTED, italic=True))

    # Спільна фізична шина CC
    parts.append(line(210, 75, 630, 75, color="#0284c7", sw=3))
    parts.append(text(420, 65, "Спільна фізична лінія CC (напівдуплекс BMC 300 кбіт/с)", size=11, color="#0284c7", bold=True))

    # Відводи до чипів
    parts.append(line(325, 75, 325, 90, color="#0284c7", sw=2))
    parts.append(line(515, 75, 515, 90, color="#0284c7", sw=2))

    # Пояснювальна таблиця знизу
    parts.append(rect(40, 305, 740, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    parts.append(text(410, 323, "Преамбула (64 біти) однакова для всіх. Тип адресата задається 4 символами K-code Start-of-Packet:", size=11, color=INK))
    parts.append(text(410, 340, "SOP: [Sync-1, Sync-1, Sync-1, Sync-1]  |  SOP': [Sync-1, Sync-1, Sync-1, Sync-2]  |  SOP'': [Sync-1, Sync-1, Sync-3, Sync-3]", size=10, color="#475569", bold=True))

    render(os.path.join(IMG, "sop-addressing-layers.svg"), W, H, *parts,
           title="Ієрархія адресації пакетів USB PD: SOP, SOP' та SOP''")


def fig_vdm_discovery_sequence():
    """Діаграма послідовності опитування Discover Identity через Structured VDM."""
    W, H = 820, 400
    parts = []

    # Вертикальні осі учасників
    dfp_x, em_x, snk_x = 160, 410, 660
    
    parts.append(rect(dfp_x - 70, 45, 140, 35, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=4))
    parts.append(text(dfp_x, 67, "Джерело (DFP)", size=12, color="#1e40af", bold=True))
    parts.append(line(dfp_x, 80, dfp_x, 370, color="#94a3b8", sw=1.5, dash="4,4"))

    parts.append(rect(em_x - 70, 45, 140, 35, fill="#faf5ff", stroke="#a855f7", sw=2, rx=4))
    parts.append(text(em_x, 67, "E-Marker (SOP')", size=12, color="#6b21a8", bold=True))
    parts.append(line(em_x, 80, em_x, 370, color="#94a3b8", sw=1.5, dash="4,4"))

    parts.append(rect(snk_x - 70, 45, 140, 35, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=4))
    parts.append(text(snk_x, 67, "Споживач (Sink)", size=12, color="#15803d", bold=True))
    parts.append(line(snk_x, 80, snk_x, 370, color="#94a3b8", sw=1.5, dash="4,4"))

    # Подія 1: Детектування Ra та ввімкнення VCONN
    y1 = 110
    parts.append(circle(dfp_x, y1, 4, fill="#2563eb", stroke="#ffffff", sw=1))
    parts.append(arrow(dfp_x, y1, em_x, y1, color="#7c3aed", sw=2))
    parts.append(text(285, y1 - 8, "1. Подача VCONN (5 В, детектовано Ra)", size=10, color="#7c3aed", bold=True))

    # Подія 2: Запит Discover Identity
    y2 = 150
    parts.append(circle(dfp_x, y2, 4, fill="#2563eb", stroke="#ffffff", sw=1))
    parts.append(arrow(dfp_x, y2, em_x, y2, color="#0284c7", sw=2))
    parts.append(text(285, y2 - 8, "2. SOP' Discover Identity (SVID: 0xFF00)", size=10, color="#0284c7", bold=True))

    # Подія 3: Відповідь E-Marker ACK з VDO
    y3 = 200
    parts.append(circle(em_x, y3, 4, fill="#a855f7", stroke="#ffffff", sw=1))
    parts.append(arrow(em_x, y3, dfp_x, y3, color="#16a34a", sw=2))
    parts.append(text(285, y3 - 8, "3. SOP' Discover Identity ACK", size=10, color="#16a34a", bold=True))
    
    # Виносний блок з переліком VDO
    parts.append(rect(180, y3 + 5, 210, 45, fill="#f0fdf4", stroke="#86efac", sw=1, rx=4))
    parts.append(text(285, y3 + 20, "• ID Header VDO (Passive Cable)", size=9, color="#14532d"))
    parts.append(text(285, y3 + 33, "• Cert Stat VDO + Product VDO", size=9, color="#14532d"))
    parts.append(text(285, y3 + 46, "• Cable VDO 1/2: 50 В, 5 А, USB4 Gen3", size=9, color="#14532d", bold=True))

    # Подія 4: Відправка Source Capabilities до Sink
    y4 = 285
    parts.append(circle(dfp_x, y4, 4, fill="#2563eb", stroke="#ffffff", sw=1))
    parts.append(arrow(dfp_x, y4, snk_x, y4, color="#ea580c", sw=2))
    parts.append(text(410, y4 - 8, "4. SOP Source_Capabilities (включено 5 А / 48 В PDO)", size=10, color="#ea580c", bold=True))

    # Подія 5: Запит контракту Sink
    y5 = 330
    parts.append(circle(snk_x, y5, 4, fill="#16a34a", stroke="#ffffff", sw=1))
    parts.append(arrow(snk_x, y5, dfp_x, y5, color="#2563eb", sw=2))
    parts.append(text(410, y5 - 8, "5. SOP Request (48 В / 5 А — 240 Вт EPR контракт)", size=10, color="#2563eb", bold=True))

    render(os.path.join(IMG, "vdm-discovery-sequence.svg"), W, H, *parts,
           title="Послідовність опитування E-Marker через Structured VDM перед укладанням контракту")


def fig_cable_vdo_layout():
    """Структура бітових полів дескрипторів Passive Cable VDO 1 та Cable VDO 2."""
    W, H = 820, 360
    parts = []

    # Заголовок блоку Cable VDO 1
    parts.append(rect(40, 50, 740, 130, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    parts.append(text(160, 75, "Passive Cable VDO 1 (32 біти)", size=13, color="#1e293b", bold=True))

    # Поля Cable VDO 1
    # B31..B28: HW/FW Version
    parts.append(rect(50, 90, 80, 50, fill="#e2e8f0", stroke="#475569", sw=1, rx=3))
    parts.append(text(90, 110, "B31..B28", size=9, color=MUTED))
    parts.append(text(90, 128, "Версія HW/FW", size=9, color=INK, bold=True))

    # B27..B24: Зарезервовано
    parts.append(rect(135, 90, 65, 50, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(167, 110, "B27..B24", size=9, color=MUTED))
    parts.append(text(167, 128, "Резерв", size=9, color=MUTED))

    # B23..B21: Затримка кабелю (Latency)
    parts.append(rect(205, 90, 85, 50, fill="#e0e7ff", stroke="#6366f1", sw=1, rx=3))
    parts.append(text(247, 110, "B23..B21", size=9, color="#4338ca"))
    parts.append(text(247, 128, "Затримка (&lt;10ns)", size=9, color="#312e81", bold=True))

    # B20..B19: Тип виводів (Termination)
    parts.append(rect(295, 90, 85, 50, fill="#fce7f3", stroke="#ec4899", sw=1, rx=3))
    parts.append(text(337, 110, "B20..B19", size=9, color="#be185d"))
    parts.append(text(337, 128, "Термінація", size=9, color="#831843", bold=True))

    # B18..B17: Максимальна напруга VBUS (00b=20V, 01b=30V, 10b=40V, 11b=50V)
    parts.append(rect(385, 90, 120, 50, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    parts.append(text(445, 110, "B18..B17 [VBUS Volt]", size=9, color=POS, bold=True))
    parts.append(text(445, 128, "00b=20В | 11b=50В", size=9, color=POS, bold=True))

    # B6..B5: Граничний струм VBUS (01b=3A, 10b=5A)
    parts.append(rect(510, 90, 110, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    parts.append(text(565, 110, "B6..B5 [Current]", size=9, color="#b45309", bold=True))
    parts.append(text(565, 128, "01b=3 А | 10b=5 А", size=9, color="#92400e", bold=True))

    # B2..B0: Максимальна швидкість USB (USB2, Gen1, Gen2, USB4 Gen3/Gen4)
    parts.append(rect(625, 90, 145, 50, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=3))
    parts.append(text(697, 110, "B2..B0 [USB Speed]", size=9, color="#15803d", bold=True))
    parts.append(text(697, 128, "USB2 / Gen2 / USB4", size=9, color="#14532d", bold=True))

    parts.append(text(410, 162, "Cable VDO 1 декларує: граничний струм (до 5 А), напругу (20 В / 50 В) та смугу пропускання даних", size=10, color=MUTED))

    # Заголовок блоку Cable VDO 2
    parts.append(rect(40, 200, 740, 130, fill="#faf5ff", stroke="#a855f7", sw=2, rx=8))
    parts.append(text(160, 225, "Passive Cable VDO 2 (USB PD 3.1 EPR)", size=13, color="#6b21a8", bold=True))

    # Поля Cable VDO 2
    # B31..B24: Максимальна робоча температура
    parts.append(rect(50, 240, 160, 50, fill="#f3e8ff", stroke="#9333ea", sw=1, rx=3))
    parts.append(text(130, 260, "B31..B24 [Max Temp]", size=9, color="#6b21a8"))
    parts.append(text(130, 278, "Макс. темп. (°C)", size=9, color="#581c87", bold=True))

    # B23..B16: Резерв
    parts.append(rect(215, 240, 120, 50, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    parts.append(text(275, 260, "B23..B16", size=9, color=MUTED))
    parts.append(text(275, 278, "Резерв", size=9, color=MUTED))

    # B15..B12: Температурний сенсор
    parts.append(rect(340, 240, 130, 50, fill="#fef9c3", stroke="#ca8a04", sw=1, rx=3))
    parts.append(text(405, 260, "B15..B12 [Thermal Sensor]", size=9, color="#854d0e"))
    parts.append(text(405, 278, "Термодатчик у штекері", size=9, color="#713f12", bold=True))

    # B11..B8: Підтримка EPR напруги (50 В)
    parts.append(rect(475, 240, 150, 50, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    parts.append(text(550, 260, "B11..B8 [EPR Capable]", size=9, color=POS, bold=True))
    parts.append(text(550, 278, "50 В EPR Rating (240 Вт)", size=9, color=POS, bold=True))

    # B7..B0: Тип контактів та конструкція роз'єму
    parts.append(rect(630, 240, 140, 50, fill="#e0e7ff", stroke="#4f46e5", sw=1, rx=3))
    parts.append(text(700, 260, "B7..B0 [Connector]", size=9, color="#3730a3"))
    parts.append(text(700, 278, "Type-C / Captive", size=9, color="#312e81", bold=True))

    parts.append(text(410, 312, "Cable VDO 2 додає атрибути EPR: сертифікацію ізоляції на 50 В та наявність температурного моніторингу", size=10, color=MUTED))

    render(os.path.join(IMG, "cable-vdo-layout.svg"), W, H, *parts,
           title="Розподіл бітових полів дескрипторів Cable VDO 1 та Cable VDO 2")


def fig_vbus_short_hazard():
    """Небезпека короткого замикання пінів CC/VCONN на лінію 48 В VBUS при висмикуванні."""
    W, H = 820, 360
    parts = []

    # Рамка роз'єму
    parts.append(rect(40, 50, 740, 280, fill="#fff1f2", stroke="#e11d48", sw=2, rx=8))
    parts.append(text(410, 80, "Геометрія виводів Type-C та ризик замикання VBUS (48 В) на лінію CC / VCONN", size=13, color="#9f1239", bold=True))

    # Ряд контактів Receptacle
    pin_x = [80, 140, 200, 260, 320, 380, 440, 500, 560, 620, 680, 740]
    pin_lbl = ["A1\nGND", "A2\nTX1+", "A3\nTX1-", "A4\nVBUS", "A5\nCC1", "A6\nD+", "A7\nD-", "A8\nSBU1", "A9\nVBUS", "A10\nRX2-", "A11\nRX2+", "A12\nGND"]
    
    for x, lbl in zip(pin_x, pin_lbl):
        is_vbus = "VBUS" in lbl
        is_cc = "CC1" in lbl
        col = POS if is_vbus else ("#0284c7" if is_cc else "#64748b")
        bg_col = "#fee2e2" if is_vbus else ("#e0f2fe" if is_cc else "#f8fafc")
        sw_val = 2 if (is_vbus or is_cc) else 1
        
        parts.append(rect(x - 24, 115, 48, 55, fill=bg_col, stroke=col, sw=sw_val, rx=4))
        lines = lbl.split("\n")
        parts.append(text(x, 135, lines[0], size=10, color=col, bold=True))
        parts.append(text(x, 153, lines[1], size=9, color=col, bold=(is_vbus or is_cc)))

    # Зазор між A4 (VBUS) та A5 (CC1) всього 0.5 мм
    parts.append(line(260, 175, 320, 175, color=POS, sw=2))
    parts.append(arrow(290, 200, 260, 175, color=POS, sw=1.5))
    parts.append(arrow(290, 200, 320, 175, color=POS, sw=1.5))
    parts.append(text(290, 218, "Крок 0.5 мм: замикання", size=10, color=POS, bold=True))
    parts.append(text(290, 233, "при кутовому русі!", size=10, color=POS, bold=True))

    # Схема захисту в сучасному E-Marker чипі
    parts.append(rect(430, 195, 330, 115, fill="#f8fafc", stroke="#0f172a", sw=1.5, rx=6))
    parts.append(text(595, 218, "Внутрішній захист E-Marker (OVP)", size=11, color="#0f172a", bold=True))
    parts.append(text(595, 238, "• Витримує постійну напругу до 55 В на пінах CC/VCONN", size=9, color="#1e293b"))
    parts.append(text(595, 255, "• Швидкі TVS-структури відсікають перехідні процеси", size=9, color="#1e293b"))
    parts.append(text(595, 272, "• Захист від лавинного пробою трансивера BMC", size=9, color="#1e293b"))
    parts.append(text(595, 292, "Запобігає вигоранню чипа при гарячому від'єднанні 240 Вт", size=9, color="#15803d", bold=True))

    render(os.path.join(IMG, "vbus-short-hazard.svg"), W, H, *parts,
           title="Небезпека електричного замикання контактів CC на лінію 48 В VBUS")


def main():
    fig_emarker_paddle_card()
    fig_vconn_ra_circuit()
    fig_sop_addressing_layers()
    fig_vdm_discovery_sequence()
    fig_cable_vdo_layout()
    fig_vbus_short_hazard()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
