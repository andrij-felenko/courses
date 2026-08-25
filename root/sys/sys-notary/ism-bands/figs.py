# -*- coding: utf-8 -*-
"""Фігури теми «ISM-діапазони». Запуск: python figs.py → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_spectrum_map():
    W, H = 760, 360
    parts = []
    
    # Заголовок осі
    ax_y = 70
    x0, x1 = 60, 700
    parts.append(arrow(x0, ax_y, x1, ax_y, color=INK, sw=2))
    parts.append(text(x1 + 10, ax_y + 4, "Частота", 12, INK, "start", bold=True))
    
    # Смуги на осі
    bands = [
        (90, "13.56 МГц", "Sub-GHz (NFC / HF RFID)", "Далеко біля тіла, індукція", NEG, 100),
        (220, "433 / 868 МГц", "Sub-GHz (LoRa / Sigfox / Z-Wave)", "Кілометри, проникає крізь стіни", POS, 130),
        (430, "2.4 ГГц", "Глобальний ISM (Wi-Fi / BLE / Zigbee)", "Переповнений, універсальний", FIELD, 140),
        (610, "5.8 ГГц", "5.8 ГГц (Wi-Fi 5/6 / FPV дрони)", "Швидко, згасає у перешкодах", FIELD, 100),
    ]
    
    for x, freq, label, subtext, color_val, width_val in bands:
        # Вертикальна засічка
        parts.append(line(x, ax_y - 10, x, ax_y + 10, color=color_val, sw=2.5))
        parts.append(text(x, ax_y - 18, freq, 12, color_val, "middle", bold=True))
        
        # Прямокутник зони застосування
        box_y = ax_y + 40
        b = fitbox(x - width_val // 2, box_y, width_val, 85,
                   f"{label}\n—\n{subtext}",
                   size=11, fill="#ffffff", stroke=color_val, sw=1.5, color=INK)
        parts.append(b)
        parts.append(line(x, ax_y + 10, x, box_y, color=color_val, sw=1, dash="3 3"))

    # Підсумкова стрілка порівняння внизу
    bot_y = 280
    parts.append(arrow(x0, bot_y, x1, bot_y, color=MUTED, sw=1.5))
    parts.append(text(x0, bot_y + 20, "← Більша дальність, довша хвиля", 11, INK, "start"))
    parts.append(text(x1, bot_y + 20, "Вища швидкість, менші антени →", 11, INK, "end"))

    # Центральна характеристика регуляції
    b_info = fitbox(x0, bot_y + 35, x1 - x0, 35,
                    "Усі ISM-діапазони є неліцензованими: не потрібен дозвіл на частоту, але обов'язкове дотримання норм EIRP та Duty Cycle.",
                    size=11, fill="#f8f9fa", stroke=LINE, sw=1, color=INK)
    parts.append(b_info)

    render(os.path.join(IMG, "ism-spectrum-map.svg"), W, H, *parts,
           title="Карта основних ISM-діапазонів та їхні ключові радіофізичні властивості")


def fig_wifi_bluetooth_zigbee():
    W, H = 760, 380
    parts = []
    
    # Вісь 2.4 ГГц (2400 - 2483.5 МГц)
    ax_y = 230
    x0, x1 = 70, 690
    parts.append(arrow(x0, ax_y, x1 + 20, ax_y, color=INK, sw=2))
    parts.append(text(x0, ax_y + 20, "2400 МГц", 11, MUTED, "middle"))
    parts.append(text(x1, ax_y + 20, "2483.5 МГц", 11, MUTED, "middle"))
    parts.append(text(x1 + 25, ax_y + 4, "Частота", 11, INK, "start", bold=True))
    
    # 3 канали Wi-Fi (20 МГц кожен)
    wifi_ch = [
        (x0 + 60, "Wi-Fi Ch 1", "2412 МГц"),
        (x0 + 280, "Wi-Fi Ch 6", "2437 МГц"),
        (x0 + 500, "Wi-Fi Ch 11", "2462 МГц"),
    ]
    for cx, name, freq in wifi_ch:
        w_width = 110
        # Дзвоноподібний або трапецієподібний контур каналу
        path_d = f"M {cx - w_width//2} {ax_y} Q {cx} {ax_y - 120} {cx + w_width//2} {ax_y}"
        parts.append(f'<path d="{path_d}" fill="#4a90e2" opacity="0.2" stroke="#2b6cb0" stroke-width="1.5"/>')
        parts.append(text(cx, ax_y - 65, name, 11, "#1a365d", "middle", bold=True))
        parts.append(text(cx, ax_y - 48, freq, 10, MUTED, "middle"))

    # Завада від мікрохвильовки (~2450 МГц)
    mw_x = x0 + 390
    mw_path = f"M {mw_x - 50} {ax_y} Q {mw_x} {ax_y - 160} {mw_x + 50} {ax_y}"
    parts.append(f'<path d="{mw_path}" fill="#e53e3e" opacity="0.35" stroke="#c53030" stroke-width="2" stroke-dasharray="4 2"/>')
    parts.append(text(mw_x, ax_y - 135, "Мікрохвильовка (700-1000 Вт)", 11, "#9b2c2c", "middle", bold=True))
    parts.append(text(mw_x, ax_y - 118, "Витік шуму ~2450 МГц", 10, "#9b2c2c", "middle"))

    # Bluetooth Frequency Hopping (FHSS)
    bt_y = ax_y - 15
    for i in range(15):
        bx = x0 + 30 + i * 42
        parts.append(rect(bx, bt_y - 18, 6, 18, fill="#38a169", stroke="none"))
    parts.append(text(x0 + 120, ax_y + 40, "Bluetooth (FHSS, 79 каналів по 1 МГц)", 11, "#276749", "start", bold=True))

    # Zigbee (IEEE 802.15.4) канали
    zb_y = ax_y + 65
    for i in range(8):
        zx = x0 + 40 + i * 80
        parts.append(circle(zx, zb_y, 7, fill="#dd6b20", stroke="#9c4221", sw=1))
    parts.append(text(x0 + 120, zb_y + 4, "Zigbee (16 каналів по 2 МГц у щілинах Wi-Fi)", 11, "#9c4221", "start", bold=True))

    render(os.path.join(IMG, "wifi-bluetooth-zigbee-24ghz.svg"), W, H, *parts,
           title="Конкуренція та накладання спектрів Wi-Fi, Bluetooth, Zigbee й завад у 2.4 ГГц")


def fig_power_and_dutycycle():
    W, H = 760, 340
    parts = []

    # Ліва панель: EIRP
    p1_x, p1_y, p1_w, p1_h = 40, 40, 320, 260
    parts.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(p1_x + p1_w//2, p1_y + 25, "1. Потужність випромінювання (EIRP)", 13, INK, "middle", bold=True))

    # Блоки додавання EIRP
    parts.append(fitbox(p1_x + 20, p1_y + 50, 120, 35, "Вихід Tx (P_tx)\nнапр. +14 dBm", size=10, fill="#ebf8ff", stroke="#3182ce", sw=1, color=INK))
    parts.append(text(p1_x + 155, p1_y + 68, "+", 16, INK, "middle", bold=True))
    parts.append(fitbox(p1_x + 175, p1_y + 50, 120, 35, "Антена (G_ant)\nнапр. +2.15 dBi", size=10, fill="#f0fff4", stroke="#38a169", sw=1, color=INK))
    
    parts.append(text(p1_x + p1_w//2, p1_y + 105, "− Кабель (L_cable)", 11, MUTED, "middle"))
    parts.append(arrow(p1_x + p1_w//2, p1_y + 115, p1_x + p1_w//2, p1_y + 140, color=INK, sw=1.5))

    parts.append(fitbox(p1_x + 40, p1_y + 145, 240, 45, "EIRP = P_tx + G_ant − L_cable\nОбмеження: ≤ +14 dBm (25 мВт)", size=11, fill="#fffaf0", stroke="#dd6b20", sw=1.5, color=INK))

    parts.append(fitbox(p1_x + 20, p1_y + 205, 280, 40, "Перевищення EIRP створює завади сусіднім каналам і є порушенням регламенту.", size=10, fill="#f8f9fa", stroke="none", sw=0, color=MUTED))

    # Права панель: Duty Cycle
    p2_x, p2_y, p2_w, p2_h = 400, 40, 320, 260
    parts.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(p2_x + p2_w//2, p2_y + 25, "2. Робочий цикл (Duty Cycle)", 13, INK, "middle", bold=True))

    # Часова вісь
    t_y = p2_y + 130
    tx0, tx1 = p2_x + 30, p2_x + 290
    parts.append(arrow(tx0, t_y, tx1, t_y, color=INK, sw=1.5))
    parts.append(text(tx1 - 10, t_y + 18, "Час (1 година)", 10, MUTED, "end"))

    # Пакети передачі (Tx імпульси)
    # 1% від 3600с = 36 секунд
    parts.append(rect(p2_x + 50, t_y - 35, 12, 35, fill="#e53e3e", stroke="#9b2c2c", sw=1))
    parts.append(rect(p2_x + 130, t_y - 35, 8, 35, fill="#e53e3e", stroke="#9b2c2c", sw=1))
    parts.append(rect(p2_x + 210, t_y - 35, 14, 35, fill="#e53e3e", stroke="#9b2c2c", sw=1))

    parts.append(text(p2_x + 56, t_y - 42, "Tx", 9, "#9b2c2c", "middle", bold=True))
    parts.append(text(p2_x + 134, t_y - 42, "Tx", 9, "#9b2c2c", "middle", bold=True))
    parts.append(text(p2_x + 217, t_y - 42, "Tx", 9, "#9b2c2c", "middle", bold=True))

    parts.append(fitbox(p2_x + 30, p2_y + 160, 260, 45, "Duty Cycle = (Σ t_on / T_total) × 100%\nНаприклад, 1% = максимум 36 с передачі на годину", size=10, fill="#f7fafc", stroke="#4a5568", sw=1, color=INK))

    parts.append(fitbox(p2_x + 20, p2_y + 215, 280, 35, "Після передачі передавач МОВЧИТЬ решту часу, звільняючи ефір іншим вузлам.", size=10, fill="#f8f9fa", stroke="none", sw=0, color=MUTED))

    render(os.path.join(IMG, "power-and-dutycycle.svg"), W, H, *parts,
           title="Обмеження випромінюваної потужності EIRP та робочого циклу Duty Cycle")


if __name__ == "__main__":
    fig_spectrum_map()
    fig_wifi_bluetooth_zigbee()
    fig_power_and_dutycycle()
    print("Figures generated successfully.")
