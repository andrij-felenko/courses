# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Модем і AT-команди»."""

import os
import xml.etree.ElementTree as ET

IMG_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_FOLDER = os.path.join(IMG_DIR, "img")
os.makedirs(IMG_FOLDER, exist_ok=True)


def fig_hardware_interconnect():
    """Схема апаратного стику мікроконтролера та стільникового модема."""
    w, h = 1040, 530
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #ffffff; }
        .box-mcu { fill: #f8fafc; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-modem { fill: #f8fafc; stroke: #dc2626; stroke-width: 2; rx: 8px; }
        .box-pwr { fill: #fefce8; stroke: #ca8a04; stroke-width: 1.5; rx: 6px; }
        .box-shifter { fill: #f1f5f9; stroke: #64748b; stroke-width: 1.5; stroke-dasharray: 4,4; rx: 6px; }
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; }
        .hdr-mcu { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #1d4ed8; }
        .hdr-modem { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #b91c1c; }
        .sig-lbl { font-family: 'Consolas', 'Courier New', monospace; font-size: 11px; font-weight: bold; fill: #1e293b; }
        .sig-desc { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; fill: #475569; }
        .line-data { stroke: #2563eb; stroke-width: 1.8; }
        .line-ctrl { stroke: #059669; stroke-width: 1.5; }
        .line-pwr { stroke: #dc2626; stroke-width: 2.2; }
        .line-pwr-dim { stroke: #ea580c; stroke-width: 1.5; }
        .arrow-data { fill: #2563eb; }
        .arrow-ctrl { fill: #059669; }
        .arrow-pwr { fill: #dc2626; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    # Headers
    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '24', 'class': 'title', 'text-anchor': 'middle', 'font-size': '15'}).text = "Апаратний інтерфейс зв'язку хост-мікроконтролера зі стільниковим модемом"
    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '42', 'class': 'subtitle', 'text-anchor': 'middle', 'font-size': '11'}).text = "Розподіл живлення VBAT, рівнів 3.3V / 1.8V, повнодуплексного UART та сигналів керування"

    # MCU Box
    mcu_x, mcu_y, mcu_w, mcu_h = 30, 65, 230, 440
    ET.SubElement(g, 'rect', {'x': str(mcu_x), 'y': str(mcu_y), 'width': str(mcu_w), 'height': str(mcu_h), 'class': 'box-mcu'})
    ET.SubElement(g, 'text', {'x': str(mcu_x + mcu_w // 2), 'y': str(mcu_y + 24), 'class': 'hdr-mcu', 'text-anchor': 'middle', 'font-size': '13'}).text = "Хост-мікроконтролер (MCU)"
    ET.SubElement(g, 'text', {'x': str(mcu_x + mcu_w // 2), 'y': str(mcu_y + 40), 'class': 'sig-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Логічні рівні: 3.3V CMOS"

    # Modem Box
    mod_x, mod_y, mod_w, mod_h = 780, 65, 230, 440
    ET.SubElement(g, 'rect', {'x': str(mod_x), 'y': str(mod_y), 'width': str(mod_w), 'height': str(mod_h), 'class': 'box-modem'})
    ET.SubElement(g, 'text', {'x': str(mod_x + mod_w // 2), 'y': str(mod_y + 24), 'class': 'hdr-modem', 'text-anchor': 'middle', 'font-size': '13'}).text = "Стільниковий модем (DCE)"
    ET.SubElement(g, 'text', {'x': str(mod_x + mod_w // 2), 'y': str(mod_y + 40), 'class': 'sig-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Baseband I/O: 1.8V (V_GLOBAL_IO)"

    # Level Shifter Box
    sh_x, sh_y, sh_w, sh_h = 380, 135, 280, 370
    ET.SubElement(g, 'rect', {'x': str(sh_x), 'y': str(sh_y), 'width': str(sh_w), 'height': str(sh_h), 'class': 'box-shifter'})
    ET.SubElement(g, 'text', {'x': str(sh_x + sh_w // 2), 'y': str(sh_y + 20), 'class': 'title', 'text-anchor': 'middle', 'font-size': '12'}).text = "Зсувач рівнів (3.3V ⇄ 1.8V)"
    ET.SubElement(g, 'text', {'x': str(sh_x + sh_w // 2), 'y': str(sh_y + 35), 'class': 'sig-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "TXS0108E / SN74AVC4T245 (без автовизначення на RTS/CTS)"

    # Power Section (Top)
    pwr_x, pwr_y, pwr_w, pwr_h = 380, 65, 280, 55
    ET.SubElement(g, 'rect', {'x': str(pwr_x), 'y': str(pwr_y), 'width': str(pwr_w), 'height': str(pwr_h), 'class': 'box-pwr'})
    ET.SubElement(g, 'text', {'x': str(pwr_x + pwr_w // 2), 'y': str(pwr_y + 20), 'class': 'hdr-modem', 'text-anchor': 'middle', 'font-size': '12'}).text = "Джерело VBAT (3.8V, I_peak = 2.0A)"
    ET.SubElement(g, 'text', {'x': str(pwr_x + pwr_w // 2), 'y': str(pwr_y + 38), 'class': 'sig-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "1000 µF Low-ESR + 100 nF кераміка біля пінів"

    # Power Line to Modem
    ET.SubElement(g, 'line', {'x1': str(pwr_x + pwr_w), 'y1': str(pwr_y + 27), 'x2': str(mod_x), 'y2': str(pwr_y + 27), 'class': 'line-pwr'})
    ET.SubElement(g, 'polygon', {'points': f'{mod_x-6},{pwr_y+23} {mod_x},{pwr_y+27} {mod_x-6},{pwr_y+31}', 'class': 'arrow-pwr'})
    ET.SubElement(g, 'text', {'x': str(mod_x + 10), 'y': str(pwr_y + 31), 'class': 'sig-lbl', 'fill': '#dc2626', 'font-size': '11'}).text = "VBAT"

    # Power line to MCU
    ET.SubElement(g, 'line', {'x1': str(pwr_x), 'y1': str(pwr_y + 27), 'x2': str(mcu_x + mcu_w), 'y2': str(pwr_y + 27), 'class': 'line-pwr-dim'})
    ET.SubElement(g, 'text', {'x': str(mcu_x + mcu_w - 70), 'y': str(pwr_y + 31), 'class': 'sig-lbl', 'fill': '#ea580c', 'font-size': '11'}).text = "VCC 3.3V"

    # Signals configuration
    signals = [
        ("TXD (UART TX)", "RXD (UART RX)", 195, True, "data", "Команди хоста (DTE → DCE)"),
        ("RXD (UART RX)", "TXD (UART TX)", 230, False, "data", "Відповіді й URC (DCE → DTE)"),
        ("RTS (Out)", "RTS (In)", 265, True, "data", "Хост готовий приймати"),
        ("CTS (In)", "CTS (Out)", 300, False, "data", "Модем готовий приймати"),
        ("DTR (Sleep/Esc)", "DTR (In)", 335, True, "ctrl", "Керування сном і вихід із Data Mode"),
        ("RI (Ring/Wake)", "RI (Out)", 370, False, "ctrl", "Імпульс URC для пробудження MCU"),
        ("PWRKEY (Open-Drn)", "PWRKEY (In)", 405, True, "ctrl", "Імпульс увімкнення/вимкнення"),
        ("RESET_N (Open-Drn)", "RESET_N (In)", 440, True, "ctrl", "Аварійне апаратне скидання"),
        ("STATUS (In)", "STATUS (Out)", 475, False, "ctrl", "Індикація активності Baseband"),
    ]

    for mcu_lbl, mod_lbl, sy, to_modem, sig_type, desc in signals:
        ET.SubElement(g, 'text', {'x': str(mcu_x + 10), 'y': str(sy + 4), 'class': 'sig-lbl', 'font-size': '11'}).text = mcu_lbl
        ET.SubElement(g, 'text', {'x': str(mod_x + mod_w - 10), 'y': str(sy + 4), 'class': 'sig-lbl', 'text-anchor': 'end', 'font-size': '11'}).text = mod_lbl

        line_class = 'line-data' if sig_type == 'data' else 'line-ctrl'
        arrow_class = 'arrow-data' if sig_type == 'data' else 'arrow-ctrl'

        ET.SubElement(g, 'line', {'x1': str(mcu_x + mcu_w), 'y1': str(sy), 'x2': str(sh_x), 'y2': str(sy), 'class': line_class})
        ET.SubElement(g, 'line', {'x1': str(sh_x), 'y1': str(sy), 'x2': str(sh_x + sh_w), 'y2': str(sy), 'class': line_class, 'stroke-dasharray': '2,2'})
        ET.SubElement(g, 'line', {'x1': str(sh_x + sh_w), 'y1': str(sy), 'x2': str(mod_x), 'y2': str(sy), 'class': line_class})

        if to_modem:
            ET.SubElement(g, 'polygon', {'points': f'{mod_x-6},{sy-4} {mod_x},{sy} {mod_x-6},{sy+4}', 'class': arrow_class})
        else:
            ET.SubElement(g, 'polygon', {'points': f'{mcu_x+mcu_w+6},{sy-4} {mcu_x+mcu_w},{sy} {mcu_x+mcu_w+6},{sy+4}', 'class': arrow_class})

        ET.SubElement(g, 'text', {'x': str(sh_x + sh_w // 2), 'y': str(sy - 4), 'class': 'sig-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = desc

    with open(os.path.join(IMG_FOLDER, "modem-hardware-interconnect.svg"), "w", encoding="utf-8") as f:
        f.write(ET.tostring(svg, encoding='unicode'))


def fig_at_parser_fsm():
    """Скінченний автомат (FSM) неблокуючого парсера AT-команд та диспетчеризації URC."""
    w, h = 1040, 500
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #ffffff; }
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; }
        .box-state { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-state-wait { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .box-state-raw { fill: #fef2f2; stroke: #dc2626; stroke-width: 2; rx: 8px; }
        .box-classifier { fill: #f8fafc; stroke: #475569; stroke-width: 1.5; rx: 6px; }
        .state-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0f172a; }
        .state-desc { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; fill: #334155; }
        .trans-line { stroke: #334155; stroke-width: 1.5; fill: none; }
        .trans-line-err { stroke: #dc2626; stroke-width: 1.5; stroke-dasharray: 4,3; fill: none; }
        .trans-arrow { fill: #334155; }
        .trans-lbl { font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; fill: #1e293b; }
        .trans-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; fill: #64748b; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '24', 'class': 'title', 'text-anchor': 'middle', 'font-size': '15'}).text = "Архітектура та кінцевий автомат (FSM) неблокуючого AT-парсера"
    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '42', 'class': 'subtitle', 'text-anchor': 'middle', 'font-size': '11'}).text = "Розділення потоку відповідей на фінальні коди, проміжні дані, промпти ('> ') та асинхронні URC"

    # State 1: IDLE / RECEIVE LINE
    s1_x, s1_y, s1_w, s1_h = 50, 95, 210, 80
    ET.SubElement(g, 'rect', {'x': str(s1_x), 'y': str(s1_y), 'width': str(s1_w), 'height': str(s1_h), 'class': 'box-state'})
    ET.SubElement(g, 'text', {'x': str(s1_x + s1_w // 2), 'y': str(s1_y + 26), 'class': 'state-title', 'text-anchor': 'middle', 'font-size': '13'}).text = "STATE_IDLE"
    ET.SubElement(g, 'text', {'x': str(s1_x + s1_w // 2), 'y': str(s1_y + 46), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Очікування першого байта"
    ET.SubElement(g, 'text', {'x': str(s1_x + s1_w // 2), 'y': str(s1_y + 64), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "UART RX DMA → Ring Buffer"

    # State 2: COLLECTING_LINE
    s2_x, s2_y, s2_w, s2_h = 370, 95, 230, 80
    ET.SubElement(g, 'rect', {'x': str(s2_x), 'y': str(s2_y), 'width': str(s2_w), 'height': str(s2_h), 'class': 'box-state'})
    ET.SubElement(g, 'text', {'x': str(s2_x + s2_w // 2), 'y': str(s2_y + 26), 'class': 'state-title', 'text-anchor': 'middle', 'font-size': '13'}).text = "STATE_COLLECT_LINE"
    ET.SubElement(g, 'text', {'x': str(s2_x + s2_w // 2), 'y': str(s2_y + 46), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Накопичення символів у буфер"
    ET.SubElement(g, 'text', {'x': str(s2_x + s2_w // 2), 'y': str(s2_y + 64), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Пошук розділювача <CR><LF>"

    # Transition 1 -> 2
    ET.SubElement(g, 'line', {'x1': str(s1_x + s1_w), 'y1': str(s1_y + 40), 'x2': str(s2_x), 'y2': str(s2_y + 40), 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{s2_x-6},{s1_y+36} {s2_x},{s1_y+40} {s2_x-6},{s1_y+44}', 'class': 'trans-arrow'})
    ET.SubElement(g, 'text', {'x': str((s1_x + s1_w + s2_x) // 2), 'y': str(s1_y + 28), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "Новий байт"

    # State 3: LINE_CLASSIFIER
    s3_x, s3_y, s3_w, s3_h = 710, 95, 270, 80
    ET.SubElement(g, 'rect', {'x': str(s3_x), 'y': str(s3_y), 'width': str(s3_w), 'height': str(s3_h), 'class': 'box-classifier'})
    ET.SubElement(g, 'text', {'x': str(s3_x + s3_w // 2), 'y': str(s3_y + 25), 'class': 'state-title', 'text-anchor': 'middle', 'font-size': '13'}).text = "КЛАСИФІКАТОР РЯДКА"
    ET.SubElement(g, 'text', {'x': str(s3_x + s3_w // 2), 'y': str(s3_y + 45), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Порівняння з таблицею URC"
    ET.SubElement(g, 'text', {'x': str(s3_x + s3_w // 2), 'y': str(s3_y + 62), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "та очікуваною командою"

    # Transition 2 -> 3
    ET.SubElement(g, 'line', {'x1': str(s2_x + s2_w), 'y1': str(s2_y + 40), 'x2': str(s3_x), 'y2': str(s3_y + 40), 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{s3_x-6},{s2_y+36} {s3_x},{s2_y+40} {s3_x-6},{s2_y+44}', 'class': 'trans-arrow'})
    ET.SubElement(g, 'text', {'x': str((s2_x + s2_w + s3_x) // 2), 'y': str(s2_y + 28), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "<CR><LF>"

    # Bottom boxes
    b1_x, b1_y, b1_w, b1_h = 50, 270, 210, 95
    ET.SubElement(g, 'rect', {'x': str(b1_x), 'y': str(b1_y), 'width': str(b1_w), 'height': str(b1_h), 'class': 'box-state-wait'})
    ET.SubElement(g, 'text', {'x': str(b1_x + b1_w // 2), 'y': str(b1_y + 24), 'class': 'state-title', 'fill': '#1d4ed8', 'text-anchor': 'middle', 'font-size': '13'}).text = "Фінальна відповідь"
    ET.SubElement(g, 'text', {'x': str(b1_x + b1_w // 2), 'y': str(b1_y + 44), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "OK / ERROR / CME/CMS"
    ET.SubElement(g, 'text', {'x': str(b1_x + b1_w // 2), 'y': str(b1_y + 65), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Зняття блокування транзакції,"
    ET.SubElement(g, 'text', {'x': str(b1_x + b1_w // 2), 'y': str(b1_y + 82), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "зупинка тайм-ауту"

    b2_x, b2_y, b2_w, b2_h = 285, 270, 210, 95
    ET.SubElement(g, 'rect', {'x': str(b2_x), 'y': str(b2_y), 'width': str(b2_w), 'height': str(b2_h), 'class': 'box-state-wait'})
    ET.SubElement(g, 'text', {'x': str(b2_x + b2_w // 2), 'y': str(b2_y + 24), 'class': 'state-title', 'fill': '#1d4ed8', 'text-anchor': 'middle', 'font-size': '13'}).text = "Проміжні дані"
    ET.SubElement(g, 'text', {'x': str(b2_x + b2_w // 2), 'y': str(b2_y + 44), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "+CSQ: 24,99 / +QIRD: ..."
    ET.SubElement(g, 'text', {'x': str(b2_x + b2_w // 2), 'y': str(b2_y + 65), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Копіювання у буфер результату"
    ET.SubElement(g, 'text', {'x': str(b2_x + b2_w // 2), 'y': str(b2_y + 82), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "поточної команди"

    b3_x, b3_y, b3_w, b3_h = 520, 270, 220, 95
    ET.SubElement(g, 'rect', {'x': str(b3_x), 'y': str(b3_y), 'width': str(b3_w), 'height': str(b3_h), 'class': 'box-state'})
    ET.SubElement(g, 'text', {'x': str(b3_x + b3_w // 2), 'y': str(b3_y + 24), 'class': 'state-title', 'fill': '#15803d', 'text-anchor': 'middle', 'font-size': '13'}).text = "Асинхронний URC"
    ET.SubElement(g, 'text', {'x': str(b3_x + b3_w // 2), 'y': str(b3_y + 44), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "+CREG: / +QIURC: / RING"
    ET.SubElement(g, 'text', {'x': str(b3_x + b3_w // 2), 'y': str(b3_y + 65), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Виклик зареєстрованого callback"
    ET.SubElement(g, 'text', {'x': str(b3_x + b3_w // 2), 'y': str(b3_y + 82), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "НЕ впливає на очікування OK"

    b4_x, b4_y, b4_w, b4_h = 765, 270, 215, 95
    ET.SubElement(g, 'rect', {'x': str(b4_x), 'y': str(b4_y), 'width': str(b4_w), 'height': str(b4_h), 'class': 'box-state-raw'})
    ET.SubElement(g, 'text', {'x': str(b4_x + b4_w // 2), 'y': str(b4_y + 24), 'class': 'state-title', 'fill': '#b91c1c', 'text-anchor': 'middle', 'font-size': '13'}).text = "Промпт / Сирі дані"
    ET.SubElement(g, 'text', {'x': str(b4_x + b4_w // 2), 'y': str(b4_y + 44), 'class': 'trans-lbl', 'text-anchor': 'middle', 'font-size': '10'}).text = "'> ' / Binary Payload"
    ET.SubElement(g, 'text', {'x': str(b4_x + b4_w // 2), 'y': str(b4_y + 65), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Пряме пересилання N байт"
    ET.SubElement(g, 'text', {'x': str(b4_x + b4_w // 2), 'y': str(b4_y + 82), 'class': 'state-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "без пошуку <CR><LF>"

    # Dispatch lines from Classifier to Branches
    ET.SubElement(g, 'path', {'d': f'M {s3_x+30} {s3_y+s3_h} L {s3_x+30} 210 L {b1_x+b1_w//2} 210 L {b1_x+b1_w//2} {b1_y}', 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{b1_x+b1_w//2-4},{b1_y-6} {b1_x+b1_w//2},{b1_y} {b1_x+b1_w//2+4},{b1_y-6}', 'class': 'trans-arrow'})

    ET.SubElement(g, 'path', {'d': f'M {s3_x+70} {s3_y+s3_h} L {s3_x+70} 225 L {b2_x+b2_w//2} 225 L {b2_x+b2_w//2} {b2_y}', 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{b2_x+b2_w//2-4},{b2_y-6} {b2_x},{b2_y} {b2_x+b2_w//2+4},{b2_y-6}', 'class': 'trans-arrow'})

    ET.SubElement(g, 'path', {'d': f'M {s3_x+110} {s3_y+s3_h} L {s3_x+110} 240 L {b3_x+b3_w//2} 240 L {b3_x+b3_w//2} {b3_y}', 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{b3_x+b3_w//2-4},{b3_y-6} {b3_x},{b3_y} {b3_x+b3_w//2+4},{b3_y-6}', 'class': 'trans-arrow'})

    ET.SubElement(g, 'path', {'d': f'M {s3_x+180} {s3_y+s3_h} L {s3_x+180} {b4_y}', 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{s3_x+180-4},{b4_y-6} {s3_x+180},{b4_y} {s3_x+180+4},{b4_y-6}', 'class': 'trans-arrow'})

    # Loop back from bottom to IDLE
    loop_y = 430
    ET.SubElement(g, 'path', {'d': f'M {b1_x+b1_w//2} {b1_y+b1_h} L {b1_x+b1_w//2} {loop_y} L {s1_x+s1_w//2} {loop_y} L {s1_x+s1_w//2} {s1_y+s1_h}', 'class': 'trans-line'})
    ET.SubElement(g, 'polygon', {'points': f'{s1_x+s1_w//2-4},{s1_y+s1_h+6} {s1_x+s1_w//2},{s1_y+s1_h} {s1_x+s1_w//2+4},{s1_y+s1_h+6}', 'class': 'trans-arrow'})
    ET.SubElement(g, 'text', {'x': str(s1_x + s1_w // 2 + 60), 'y': str(loop_y - 8), 'class': 'trans-sub', 'text-anchor': 'middle', 'font-size': '10'}).text = "Повернення до очікування"

    # Timeout transition
    ET.SubElement(g, 'path', {'d': f'M {s2_x+s2_w//2} {s2_y+s2_h} L {s2_x+s2_w//2} {loop_y} L {s1_x+s1_w//2+20} {loop_y}', 'class': 'trans-line-err'})
    ET.SubElement(g, 'text', {'x': str(s2_x + s2_w // 2 + 10), 'y': str(s2_y + s2_h + 26), 'class': 'trans-lbl', 'fill': '#dc2626', 'font-size': '10'}).text = "Тайм-аут (T > 3000ms)"
    ET.SubElement(g, 'text', {'x': str(s2_x + s2_w // 2 + 10), 'y': str(s2_y + s2_h + 42), 'class': 'trans-sub', 'fill': '#dc2626', 'font-size': '10'}).text = "Скидання буфера й синхронізація"

    with open(os.path.join(IMG_FOLDER, "at-parser-fsm.svg"), "w", encoding="utf-8") as f:
        f.write(ET.tostring(svg, encoding='unicode'))


def fig_cmux_virtual_channels():
    """Схема мультиплексування GSM 07.10 (CMUX) та віртуальних каналів."""
    w, h = 1040, 450
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #ffffff; }
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; }
        .box-frame { fill: #f8fafc; stroke: #334155; stroke-width: 1.5; rx: 4px; }
        .box-field { fill: #eff6ff; stroke: #2563eb; stroke-width: 1.2; rx: 3px; }
        .box-payload { fill: #fefce8; stroke: #ca8a04; stroke-width: 1.2; rx: 3px; }
        .box-fcs { fill: #fdf2f8; stroke: #db2777; stroke-width: 1.2; rx: 3px; }
        .box-dlc { fill: #f0fdf4; stroke: #16a34a; stroke-width: 1.5; rx: 6px; }
        .lbl-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .lbl-field { font-family: 'Consolas', monospace; font-size: 11px; font-weight: bold; fill: #1e293b; }
        .lbl-desc { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.5px; fill: #475569; }
        .line-mux { stroke: #2563eb; stroke-width: 1.5; }
        .arrow-mux { fill: #2563eb; }
        .line-bus { stroke: #0f172a; stroke-width: 3; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '24', 'class': 'title', 'text-anchor': 'middle', 'font-size': '15'}).text = "Мультиплексування GSM 07.10 (3GPP TS 27.010 CMUX)"
    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '42', 'class': 'subtitle', 'text-anchor': 'middle', 'font-size': '11'}).text = "Одночасна передача IP-трафіку, AT-команд та GPS через один фізичний послідовний UART"

    # Frame Layout Section (Top)
    fx, fy = 40, 75
    ET.SubElement(g, 'text', {'x': str(fx), 'y': str(fy + 10), 'class': 'lbl-title', 'text-anchor': 'start', 'font-size': '12'}).text = "Структура фрейму CMUX (Basic Mode):"

    fields = [
        ("Flag", "0xF9 (1B)", 85, "box-field"),
        ("Address", "DLCI + C/R (1B)", 140, "box-field"),
        ("Control", "UIH / SABM (1B)", 145, "box-field"),
        ("Length", "1 або 2 Байти", 130, "box-field"),
        ("Information (Payload)", "Дані віртуального каналу (N Байт)", 285, "box-payload"),
        ("FCS", "CRC-8 (1B)", 90, "box-fcs"),
        ("Flag", "0xF9 (1B)", 85, "box-field"),
    ]

    cur_x = fx
    for fname, fsize, fwidth, fclass in fields:
        ET.SubElement(g, 'rect', {'x': str(cur_x), 'y': str(fy + 20), 'width': str(fwidth), 'height': '54', 'class': fclass})
        ET.SubElement(g, 'text', {'x': str(cur_x + fwidth // 2), 'y': str(fy + 41), 'class': 'lbl-field', 'text-anchor': 'middle', 'font-size': '11'}).text = fname
        ET.SubElement(g, 'text', {'x': str(cur_x + fwidth // 2), 'y': str(fy + 59), 'class': 'lbl-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = fsize
        cur_x += fwidth + 5

    # Virtual Channels Section (Bottom)
    dlcs = [
        ("DLC 0: Control Channel", "Керування сесією CMUX, узгодження параметрів (PN, PSC, CLD)", 190),
        ("DLC 1: AT Commands & URC", "Синхронні AT-запити, читання RSSI (+CSQ), мережеві статуси", 250),
        ("DLC 2: High-Speed IP Data", "Прозорий потік TCP/UDP або PPP (без переривання через '+++')", 310),
        ("DLC 3: GNSS / NMEA Stream", "Асинхронні координати $GPRMC, $GPGGA у фоновому режимі", 370),
    ]

    bus_x1, bus_x2 = 40, 440
    bus_y = 280

    ET.SubElement(g, 'line', {'x1': str(bus_x1), 'y1': str(bus_y), 'x2': str(bus_x2), 'y2': str(bus_y), 'class': 'line-bus'})
    ET.SubElement(g, 'text', {'x': str((bus_x1 + bus_x2) // 2), 'y': str(bus_y - 12), 'class': 'lbl-title', 'text-anchor': 'middle', 'font-size': '12'}).text = "Фізичний UART (TXD / RXD, 921600 біт/с)"

    # Mux Engine Box
    mux_x, mux_y, mux_w, mux_h = 460, 180, 120, 240
    ET.SubElement(g, 'rect', {'x': str(mux_x), 'y': str(mux_y), 'width': str(mux_w), 'height': str(mux_h), 'class': 'box-frame', 'fill': '#f1f5f9'})
    ET.SubElement(g, 'text', {'x': str(mux_x + mux_w // 2), 'y': str(mux_y + 115), 'class': 'lbl-title', 'text-anchor': 'middle', 'font-size': '12'}).text = "CMUX"
    ET.SubElement(g, 'text', {'x': str(mux_x + mux_w // 2), 'y': str(mux_y + 135), 'class': 'lbl-desc', 'text-anchor': 'middle', 'font-size': '10'}).text = "Демультиплексор"

    ET.SubElement(g, 'line', {'x1': str(bus_x2), 'y1': str(bus_y), 'x2': str(mux_x), 'y2': str(bus_y), 'class': 'line-bus'})

    dlc_box_x = 620
    dlc_box_w = 380
    dlc_box_h = 46

    for title, desc, dy in dlcs:
        ET.SubElement(g, 'rect', {'x': str(dlc_box_x), 'y': str(dy), 'width': str(dlc_box_w), 'height': str(dlc_box_h), 'class': 'box-dlc'})
        ET.SubElement(g, 'text', {'x': str(dlc_box_x + 15), 'y': str(dy + 19), 'class': 'lbl-title', 'font-size': '11', 'text-anchor': 'start'}).text = title
        ET.SubElement(g, 'text', {'x': str(dlc_box_x + 15), 'y': str(dy + 35), 'class': 'lbl-desc', 'font-size': '10', 'text-anchor': 'start'}).text = desc

        ET.SubElement(g, 'line', {'x1': str(mux_x + mux_w), 'y1': str(dy + dlc_box_h // 2), 'x2': str(dlc_box_x), 'y2': str(dy + dlc_box_h // 2), 'class': 'line-mux'})
        ET.SubElement(g, 'polygon', {'points': f'{dlc_box_x-6},{dy+dlc_box_h//2-4} {dlc_box_x},{dy+dlc_box_h//2} {dlc_box_x-6},{dy+dlc_box_h//2+4}', 'class': 'arrow-mux'})

    with open(os.path.join(IMG_FOLDER, "cmux-virtual-channels.svg"), "w", encoding="utf-8") as f:
        f.write(ET.tostring(svg, encoding='unicode'))


def fig_recovery_ladder():
    """Ескалаційна драбина аварійного відновлення та часові діаграми скидання."""
    w, h = 1040, 520
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #ffffff; }
        .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; }
        .subtitle { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; }
        .box-lvl0 { fill: #f0fdf4; stroke: #16a34a; stroke-width: 1.5; rx: 6px; }
        .box-lvl1 { fill: #eff6ff; stroke: #2563eb; stroke-width: 1.5; rx: 6px; }
        .box-lvl2 { fill: #fefce8; stroke: #ca8a04; stroke-width: 1.5; rx: 6px; }
        .box-lvl3 { fill: #fff7ed; stroke: #ea580c; stroke-width: 1.5; rx: 6px; }
        .box-lvl4 { fill: #fef2f2; stroke: #dc2626; stroke-width: 2; rx: 6px; }
        .box-timing { fill: #f8fafc; stroke: #64748b; stroke-width: 1.2; rx: 6px; }
        .lvl-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .lvl-desc { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; fill: #475569; }
        .timing-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; }
        .sig-name { font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; fill: #1e293b; }
        .sig-wave { stroke: #2563eb; stroke-width: 2; fill: none; }
        .sig-wave-pwr { stroke: #dc2626; stroke-width: 2; fill: none; }
        .sig-time { font-family: 'Consolas', monospace; font-size: 9px; fill: #64748b; }
        .arrow-down { fill: #64748b; }
        .line-down { stroke: #64748b; stroke-width: 1.5; stroke-dasharray: 3,3; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '24', 'class': 'title', 'text-anchor': 'middle', 'font-size': '15'}).text = "Ескалаційна драбина відновлення модема та часові діаграми скидання"
    ET.SubElement(g, 'text', {'x': str(w // 2), 'y': '42', 'class': 'subtitle', 'text-anchor': 'middle', 'font-size': '11'}).text = "Послідовність відновлення від програмного повтору до аварійного знеструмлення VBAT"

    # Left: The Escalation Ladder (Steps 0 to 4)
    lx, ly = 30, 70
    lw, lh = 440, 70

    levels = [
        ("Рівень 0: Програмний повтор і AT-пінг", "Тайм-аут (3000 мс) → Очищення буфера UART → Повтор команди (до 3 разів)", "box-lvl0"),
        ("Рівень 1: Програмний перезапуск (Soft Reset)", "Команда AT+CFUN=1,1 або AT+QRST=1 → Коректне від'єднання від мережі", "box-lvl1"),
        ("Рівень 2: Контрольований цикл PWRKEY", "Імпульс PWRKEY Low (2.0 с) → Очікування STATUS=0 → Імпульс PWRKEY Low (1.5 с)", "box-lvl2"),
        ("Рівень 3: Аварійне скидання (RESET Pin)", "Імпульс RESET_N Low (150–500 мс) → Апаратний перезапуск процесора Baseband", "box-lvl3"),
        ("Рівень 4: Повне знеструмлення (Cold Power Cut)", "Розмикання P-MOSFET на VBAT на 5.0 с → Повний розряд конденсаторів 1000 µF", "box-lvl4"),
    ]

    for i, (ltitle, ldesc, lclass) in enumerate(levels):
        cur_y = ly + i * (lh + 16)
        ET.SubElement(g, 'rect', {'x': str(lx), 'y': str(cur_y), 'width': str(lw), 'height': str(lh), 'class': lclass})
        ET.SubElement(g, 'text', {'x': str(lx + 15), 'y': str(cur_y + 26), 'class': 'lvl-title', 'font-size': '12'}).text = ltitle
        ET.SubElement(g, 'text', {'x': str(lx + 15), 'y': str(cur_y + 48), 'class': 'lvl-desc', 'font-size': '10'}).text = ldesc

        if i < len(levels) - 1:
            arrow_y1 = cur_y + lh
            arrow_y2 = cur_y + lh + 16
            ET.SubElement(g, 'line', {'x1': str(lx + lw // 2), 'y1': str(arrow_y1), 'x2': str(lx + lw // 2), 'y2': str(arrow_y2), 'class': 'line-down'})
            ET.SubElement(g, 'polygon', {'points': f'{lx+lw//2-4},{arrow_y2-4} {lx+lw//2},{arrow_y2} {lx+lw//2+4},{arrow_y2-4}', 'class': 'arrow-down'})

    # Right: Timing Diagrams Box
    tx, ty, tw, th = 500, 70, 500, 420
    ET.SubElement(g, 'rect', {'x': str(tx), 'y': str(ty), 'width': str(tw), 'height': str(th), 'class': 'box-timing'})
    ET.SubElement(g, 'text', {'x': str(tx + tw // 2), 'y': str(ty + 25), 'class': 'timing-title', 'text-anchor': 'middle', 'font-size': '12'}).text = "Часові діаграми апаратного керування (Timing)"

    # Diagram 1: PWRKEY Power-On Sequence
    d1_y = ty + 45
    ET.SubElement(g, 'text', {'x': str(tx + 20), 'y': str(d1_y + 15), 'class': 'lvl-title', 'font-size': '11'}).text = "1. Запуск через PWRKEY (Power ON):"

    # VBAT Wave
    ET.SubElement(g, 'text', {'x': str(tx + 25), 'y': str(d1_y + 40), 'class': 'sig-name', 'font-size': '10'}).text = "VBAT (3.8V)"
    ET.SubElement(g, 'path', {'d': f'M {tx+110} {d1_y+36} L {tx+470} {d1_y+36}', 'class': 'sig-wave-pwr'})

    # PWRKEY Wave
    ET.SubElement(g, 'text', {'x': str(tx + 25), 'y': str(d1_y + 70), 'class': 'sig-name', 'font-size': '10'}).text = "PWRKEY"
    ET.SubElement(g, 'path', {'d': f'M {tx+110} {d1_y+58} L {tx+150} {d1_y+58} L {tx+150} {d1_y+76} L {tx+280} {d1_y+76} L {tx+280} {d1_y+58} L {tx+470} {d1_y+58}', 'class': 'sig-wave'})
    ET.SubElement(g, 'text', {'x': str(tx + 215), 'y': str(d1_y + 92), 'class': 'sig-time', 'text-anchor': 'middle', 'font-size': '9'}).text = "t > 1500 мс (Pull-Down)"

    # STATUS Wave
    ET.SubElement(g, 'text', {'x': str(tx + 25), 'y': str(d1_y + 120), 'class': 'sig-name', 'font-size': '10'}).text = "STATUS"
    ET.SubElement(g, 'path', {'d': f'M {tx+110} {d1_y+126} L {tx+310} {d1_y+126} L {tx+310} {d1_y+110} L {tx+470} {d1_y+110}', 'class': 'sig-wave'})
    ET.SubElement(g, 'text', {'x': str(tx + 390), 'y': str(d1_y + 138), 'class': 'sig-time', 'text-anchor': 'middle', 'font-size': '9'}).text = "Модем активний"

    # Diagram 2: Emergency Hardware RESET Sequence
    d2_y = ty + 225
    ET.SubElement(g, 'text', {'x': str(tx + 20), 'y': str(d2_y + 15), 'class': 'lvl-title', 'font-size': '11'}).text = "2. Аварійне скидання (Hardware RESET):"

    # RESET Pin Wave
    ET.SubElement(g, 'text', {'x': str(tx + 25), 'y': str(d2_y + 45), 'class': 'sig-name', 'font-size': '10'}).text = "RESET_N"
    ET.SubElement(g, 'path', {'d': f'M {tx+110} {d2_y+36} L {tx+160} {d2_y+36} L {tx+160} {d2_y+54} L {tx+240} {d2_y+54} L {tx+240} {d2_y+36} L {tx+470} {d2_y+36}', 'class': 'sig-wave'})
    ET.SubElement(g, 'text', {'x': str(tx + 200), 'y': str(d2_y + 70), 'class': 'sig-time', 'text-anchor': 'middle', 'font-size': '9'}).text = "150–500 мс"

    # STATUS Drops and Rises
    ET.SubElement(g, 'text', {'x': str(tx + 25), 'y': str(d2_y + 100), 'class': 'sig-name', 'font-size': '10'}).text = "STATUS"
    ET.SubElement(g, 'path', {'d': f'M {tx+110} {d2_y+88} L {tx+165} {d2_y+88} L {tx+165} {d2_y+104} L {tx+350} {d2_y+104} L {tx+350} {d2_y+88} L {tx+470} {d2_y+88}', 'class': 'sig-wave'})
    ET.SubElement(g, 'text', {'x': str(tx + 260), 'y': str(d2_y + 118), 'class': 'sig-time', 'text-anchor': 'middle', 'font-size': '9'}).text = "Перезапуск Baseband (~2-5 с)"

    # Caution note at bottom of timing box
    ET.SubElement(g, 'text', {'x': str(tx + 20), 'y': str(d2_y + 155), 'class': 'lvl-desc', 'fill': '#b91c1c', 'font-weight': 'bold', 'font-size': '10'}).text = "УВАГА: RESET_N не скидає буфери флеш-пам'яті (ризик пошкодження NVRAM)."
    ET.SubElement(g, 'text', {'x': str(tx + 20), 'y': str(d2_y + 172), 'class': 'lvl-desc', 'fill': '#b91c1c', 'font-size': '10'}).text = "Застосовувати лише у разі повної відсутності реакції на UART та PWRKEY."

    with open(os.path.join(IMG_FOLDER, "modem-recovery-ladder.svg"), "w", encoding="utf-8") as f:
        f.write(ET.tostring(svg, encoding='unicode'))


if __name__ == "__main__":
    fig_hardware_interconnect()
    fig_at_parser_fsm()
    fig_cmux_virtual_channels()
    fig_recovery_ladder()
    print("Всі SVG-фігури успішно згенеровано у папку img/")
