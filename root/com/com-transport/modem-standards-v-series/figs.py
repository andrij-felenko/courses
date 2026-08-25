import os
import xml.etree.ElementTree as ET

IMG_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_FOLDER = os.path.join(IMG_DIR, "img")
os.makedirs(IMG_FOLDER, exist_ok=True)


def fig_vseries_timeline():
    w, h = 1020, 440
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #f8fafc; }
        .title { font-family: system-ui, -apple-system, sans-serif; font-size: 16px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .subtitle { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #475569; text-anchor: middle; }
        .axis-line { stroke: #94a3b8; stroke-width: 3; stroke-linecap: round; }
        .arrow { fill: #94a3b8; }
        .card-bg { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
        .card-bg-highlight { fill: #f0f9ff; stroke: #0284c7; stroke-width: 2; rx: 6px; }
        .std-name { font-family: system-ui, -apple-system, sans-serif; font-size: 13px; font-weight: bold; fill: #0369a1; text-anchor: middle; }
        .std-speed { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .std-detail { font-family: system-ui, -apple-system, sans-serif; font-size: 10px; fill: #475569; text-anchor: middle; }
        .node-dot { fill: #0284c7; stroke: #ffffff; stroke-width: 2; }
        .connector { stroke: #0284c7; stroke-width: 1.5; stroke-dasharray: 3,3; }
        .year-label { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: bold; fill: #334155; text-anchor: middle; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})
    
    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    t = ET.SubElement(g, 'text', {'x': str(w//2), 'y': '30', 'class': 'title'})
    t.text = "Еволюція швидкості та модуляції рекомендацій ITU-T серії V"
    sub = ET.SubElement(g, 'text', {'x': str(w//2), 'y': '50', 'class': 'subtitle'})
    sub.text = "Від аналогової ФЧМ (300 біт/с) до ІКМ на межі каналу (56 кбіт/с)"

    axis_y = 220
    ET.SubElement(g, 'line', {'x1': '50', 'y1': str(axis_y), 'x2': '960', 'y2': str(axis_y), 'class': 'axis-line'})
    ET.SubElement(g, 'polygon', {'points': f'960,{axis_y-6} 975,{axis_y} 960,{axis_y+6}', 'class': 'arrow'})

    nodes = [
        {"year": "1964", "std": "V.21", "speed": "300 біт/с", "tech": "ФЧМ (FSK)", "top": True, "x": 90},
        {"year": "1980", "std": "V.22", "speed": "1.2 кбіт/с", "tech": "ДФЧМ (DPSK)", "top": False, "x": 220},
        {"year": "1984", "std": "V.22bis", "speed": "2.4 кбіт/с", "tech": "16-QAM", "top": True, "x": 350},
        {"year": "1989", "std": "V.32", "speed": "9.6 кбіт/с", "tech": "32-TCM, Ехо", "top": False, "x": 480},
        {"year": "1991", "std": "V.32bis", "speed": "14.4 кбіт/с", "tech": "128-TCM", "top": True, "x": 610},
        {"year": "1994", "std": "V.34", "speed": "33.6 кбіт/с", "tech": "TCM, Probe", "top": False, "x": 740},
        {"year": "1998", "std": "V.90 / V.92", "speed": "56 кбіт/с", "tech": "ІКМ (PCM)", "top": True, "x": 880, "highlight": True},
    ]

    for n in nodes:
        x = n["x"]
        y_dot = axis_y
        is_top = n["top"]
        
        card_w, card_h = 110, 88
        if is_top:
            card_y = axis_y - 138
            conn_y1 = y_dot - 8
            conn_y2 = card_y + card_h
        else:
            card_y = axis_y + 54
            conn_y1 = y_dot + 8
            conn_y2 = card_y

        ET.SubElement(g, 'line', {
            'x1': str(x), 'y1': str(conn_y1),
            'x2': str(x), 'y2': str(conn_y2),
            'class': 'connector'
        })
        ET.SubElement(g, 'circle', {'cx': str(x), 'cy': str(y_dot), 'r': '6', 'class': 'node-dot'})

        bg_class = 'card-bg-highlight' if n.get('highlight') else 'card-bg'
        ET.SubElement(g, 'rect', {
            'x': str(x - card_w//2), 'y': str(card_y),
            'width': str(card_w), 'height': str(card_h),
            'class': bg_class
        })

        year_y = axis_y + 22 if is_top else axis_y - 12
        yr_el = ET.SubElement(g, 'text', {'x': str(x), 'y': str(year_y), 'class': 'year-label'})
        yr_el.text = n["year"]

        t_std = ET.SubElement(g, 'text', {'x': str(x), 'y': str(card_y + 24), 'class': 'std-name'})
        t_std.text = n["std"]

        t_spd = ET.SubElement(g, 'text', {'x': str(x), 'y': str(card_y + 46), 'class': 'std-speed'})
        t_spd.text = n["speed"]

        t_tch = ET.SubElement(g, 'text', {'x': str(x), 'y': str(card_y + 64), 'class': 'std-detail'})
        t_tch.text = n["tech"]

    filepath = os.path.join(IMG_FOLDER, "vseries-evolution-timeline.svg")
    tree = ET.ElementTree(svg)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    print(f"Generated {filepath}")


def fig_v90_pcm_architecture():
    w, h = 1020, 420
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #f8fafc; }
        .title { font-family: system-ui, -apple-system, sans-serif; font-size: 16px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .box-client { fill: #fff7ed; stroke: #f97316; stroke-width: 2; rx: 8px; }
        .box-co { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-isp { fill: #eff6ff; stroke: #2563eb; stroke-width: 2; rx: 8px; }
        .sub-box { fill: #ffffff; stroke: #94a3b8; stroke-width: 1.5; rx: 4px; }
        .box-title { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .label { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
        .label-bold { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .arrow-dn { stroke: #0284c7; stroke-width: 2.5; fill: none; }
        .arrow-up { stroke: #d97706; stroke-width: 2.5; stroke-dasharray: 5,4; fill: none; }
        .arrow-head-dn { fill: #0284c7; }
        .arrow-head-up { fill: #d97706; }
        .noise-badge { fill: #fee2e2; stroke: #ef4444; stroke-width: 1.5; rx: 4px; }
        .noise-text { font-family: system-ui, -apple-system, sans-serif; font-size: 10px; font-weight: bold; fill: #991b1b; text-anchor: middle; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    t = ET.SubElement(g, 'text', {'x': str(w//2), 'y': '30', 'class': 'title'})
    t.text = "Архітектура V.90 PCM: обхід шуму АЦП у напрямку Downstream"

    # Block 1: Client Modem
    ET.SubElement(g, 'rect', {'x': '40', 'y': '70', 'width': '230', 'height': '310', 'class': 'box-client'})
    t1 = ET.SubElement(g, 'text', {'x': '155', 'y': '95', 'class': 'box-title'})
    t1.text = "Клієнтський модем"
    t1_sub = ET.SubElement(g, 'text', {'x': '155', 'y': '114', 'class': 'label'})
    t1_sub.text = "(Аналогова абонентська лінія)"

    ET.SubElement(g, 'rect', {'x': '60', 'y': '130', 'width': '190', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '155', 'y': '154', 'class': 'label-bold'}, text="Приймач V.90 ІКМ")
    ET.SubElement(g, 'text', {'x': '155', 'y': '178', 'class': 'label'}, text="Декодування рівнів U/A-law")

    ET.SubElement(g, 'rect', {'x': '60', 'y': '270', 'width': '190', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '155', 'y': '294', 'class': 'label-bold'}, text="Передавач V.34/V.92")
    ET.SubElement(g, 'text', {'x': '155', 'y': '318', 'class': 'label'}, text="QAM / Upstream ІКМ")

    ET.SubElement(g, 'text', {'x': '350', 'y': '85', 'class': 'label-bold'}, text="Аналогова пара ТПЗК")

    # Block 2: PSTN CO
    ET.SubElement(g, 'rect', {'x': '430', 'y': '70', 'width': '210', 'height': '310', 'class': 'box-co'})
    t2 = ET.SubElement(g, 'text', {'x': '535', 'y': '95', 'class': 'box-title'})
    t2.text = "АТС (Телефонна станція)"
    t2_sub = ET.SubElement(g, 'text', {'x': '535', 'y': '114', 'class': 'label'})
    t2_sub.text = "Кодек G.711 / Гібрид"

    ET.SubElement(g, 'rect', {'x': '450', 'y': '130', 'width': '170', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '535', 'y': '154', 'class': 'label-bold'}, text="ЦАП (DAC) G.711")
    ET.SubElement(g, 'text', {'x': '535', 'y': '178', 'class': 'label'}, text="8000 відліків/с (без АЦП)")

    ET.SubElement(g, 'rect', {'x': '450', 'y': '270', 'width': '170', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '535', 'y': '294', 'class': 'label-bold'}, text="АЦП (ADC) G.711")
    ET.SubElement(g, 'text', {'x': '535', 'y': '318', 'class': 'label'}, text="Шум квантування (~38 dB)")

    ET.SubElement(g, 'rect', {'x': '300', 'y': '330', 'width': '110', 'height': '25', 'class': 'noise-badge'})
    ET.SubElement(g, 'text', {'x': '355', 'y': '346', 'class': 'noise-text'}, text="Межа 33.6 кбіт/с")

    # Block 3: ISP
    ET.SubElement(g, 'rect', {'x': '740', 'y': '70', 'width': '230', 'height': '310', 'class': 'box-isp'})
    t3 = ET.SubElement(g, 'text', {'x': '855', 'y': '95', 'class': 'box-title'})
    t3.text = "Сервер ISP (Провайдер)"
    t3_sub = ET.SubElement(g, 'text', {'x': '855', 'y': '114', 'class': 'label'})
    t3_sub.text = "Цифровий поток E1 / T1"

    ET.SubElement(g, 'rect', {'x': '760', 'y': '130', 'width': '190', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '855', 'y': '154', 'class': 'label-bold'}, text="Пряме надсилання ІКМ")
    ET.SubElement(g, 'text', {'x': '855', 'y': '178', 'class': 'label'}, text="Точні 8-бітні відліки")

    ET.SubElement(g, 'rect', {'x': '760', 'y': '270', 'width': '190', 'height': '70', 'class': 'sub-box'})
    ET.SubElement(g, 'text', {'x': '855', 'y': '294', 'class': 'label-bold'}, text="Цифровий приймач")
    ET.SubElement(g, 'text', {'x': '855', 'y': '318', 'class': 'label'}, text="Обробка потоку E1/T1")

    # Flow lines (routed between sub-boxes at y=225)
    # Downstream arrow line at y=215
    ET.SubElement(g, 'line', {'x1': '740', 'y1': '215', 'x2': '640', 'y2': '215', 'class': 'arrow-dn'})
    ET.SubElement(g, 'polygon', {'points': '640,215 650,210 650,220', 'class': 'arrow-head-dn'})
    ET.SubElement(g, 'line', {'x1': '430', 'y1': '215', 'x2': '270', 'y2': '215', 'class': 'arrow-dn'})
    ET.SubElement(g, 'polygon', {'points': '270,215 280,210 280,220', 'class': 'arrow-head-dn'})

    ET.SubElement(g, 'text', {'x': '350', 'y': '205', 'class': 'label-bold', 'style': 'fill:#0284c7;'}, text="Downstream: 56 кбіт/с (PCM)")

    # Upstream arrow line at y=245
    ET.SubElement(g, 'line', {'x1': '270', 'y1': '245', 'x2': '430', 'y2': '245', 'class': 'arrow-up'})
    ET.SubElement(g, 'polygon', {'points': '430,245 420,240 420,250', 'class': 'arrow-head-up'})
    ET.SubElement(g, 'line', {'x1': '640', 'y1': '245', 'x2': '740', 'y2': '245', 'class': 'arrow-up'})
    ET.SubElement(g, 'polygon', {'points': '740,245 730,240 730,250', 'class': 'arrow-head-up'})

    ET.SubElement(g, 'text', {'x': '350', 'y': '258', 'class': 'label-bold', 'style': 'fill:#d97706;'}, text="Upstream: 33.6k (V.34) / 48k (V.92)")

    filepath = os.path.join(IMG_FOLDER, "v90-pcm-architecture.svg")
    tree = ET.ElementTree(svg)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    print(f"Generated {filepath}")


def fig_v24_v28_dte_dce():
    w, h = 980, 420
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': f'0 0 {w} {h}',
        'width': '100%',
        'height': '100%'
    })

    style = ET.SubElement(svg, 'style')
    style.text = """
        .bg { fill: #f8fafc; }
        .title { font-family: system-ui, -apple-system, sans-serif; font-size: 16px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .subtitle { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #475569; text-anchor: middle; }
        .box-dte { fill: #eff6ff; stroke: #3b82f6; stroke-width: 2; rx: 8px; }
        .box-dce { fill: #f0fdf4; stroke: #16a34a; stroke-width: 2; rx: 8px; }
        .box-title { font-family: system-ui, -apple-system, sans-serif; font-size: 15px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .sig-line { stroke: #475569; stroke-width: 1.8; fill: none; }
        .sig-arrow { fill: #475569; }
        .sig-label { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: bold; fill: #1e293b; }
        .sig-desc { font-family: system-ui, -apple-system, sans-serif; font-size: 10px; fill: #64748b; }
        .voltage-card { fill: #ffffff; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
        .v-title { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .v-mark { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: bold; fill: #dc2626; text-anchor: middle; }
        .v-space { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: bold; fill: #16a34a; text-anchor: middle; }
    """

    ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'class': 'bg'})

    g = ET.SubElement(svg, 'g', {'transform': 'translate(0,0)'})

    t = ET.SubElement(g, 'text', {'x': str(w//2), 'y': '28', 'class': 'title'})
    t.text = "Функціональні кола V.24 та електричні рівні V.28 стику DTE–DCE"
    sub = ET.SubElement(g, 'text', {'x': str(w//2), 'y': '48', 'class': 'subtitle'})
    sub.text = "Зв'язок кінцевого термінала (DTE) та модема (DCE)"

    ET.SubElement(g, 'rect', {'x': '40', 'y': '70', 'width': '230', 'height': '320', 'class': 'box-dte'})
    ET.SubElement(g, 'text', {'x': '155', 'y': '98', 'class': 'box-title'}, text="DTE (Комп'ютер / ПК)")

    ET.SubElement(g, 'rect', {'x': '710', 'y': '70', 'width': '230', 'height': '320', 'class': 'box-dce'})
    ET.SubElement(g, 'text', {'x': '825', 'y': '98', 'class': 'box-title'}, text="DCE (Модем)")

    ET.SubElement(g, 'rect', {'x': '330', 'y': '315', 'width': '320', 'height': '75', 'class': 'voltage-card'})
    ET.SubElement(g, 'text', {'x': '490', 'y': '333', 'class': 'v-title'}, text="Електричні рівні V.28 (RS-232)")
    ET.SubElement(g, 'text', {'x': '490', 'y': '352', 'class': 'v-mark'}, text="Mark (1 / OFF): -3 В ... -15 В (Пасивний стан)")
    ET.SubElement(g, 'text', {'x': '490', 'y': '371', 'class': 'v-space'}, text="Space (0 / ON): +3 В ... +15 В (Активний стан)")

    signals = [
        {"num": "103", "name": "TXD", "desc": "Передача даних", "dir": "dte->dce", "y": 125},
        {"num": "104", "name": "RXD", "desc": "Прийом даних", "dir": "dce->dte", "y": 150},
        {"num": "105", "name": "RTS", "desc": "Запит відправки", "dir": "dte->dce", "y": 175},
        {"num": "106", "name": "CTS", "desc": "Готовність до прийому", "dir": "dce->dte", "y": 200},
        {"num": "107", "name": "DSR", "desc": "Модем готовий", "dir": "dce->dte", "y": 225},
        {"num": "108/2", "name": "DTR", "desc": "Термінал готовий", "dir": "dte->dce", "y": 250},
        {"num": "109", "name": "DCD", "desc": "Детектор несучої", "dir": "dce->dte", "y": 275},
    ]

    for s in signals:
        y = s["y"]
        ET.SubElement(g, 'line', {'x1': '270', 'y1': str(y), 'x2': '710', 'y2': str(y), 'class': 'sig-line'})
        
        if s["dir"] == "dte->dce":
            ET.SubElement(g, 'polygon', {'points': f'710,{y} 700,{y-4} 700,{y+4}', 'class': 'sig-arrow'})
        else:
            ET.SubElement(g, 'polygon', {'points': f'270,{y} 280,{y-4} 280,{y+4}', 'class': 'sig-arrow'})

        lbl_text = f"Коло {s['num']} ({s['name']})"
        desc_text = s['desc']
        
        ET.SubElement(g, 'text', {'x': '490', 'y': str(y - 3), 'class': 'sig-label', 'text-anchor': 'middle'}, text=lbl_text)
        ET.SubElement(g, 'text', {'x': '490', 'y': str(y + 10), 'class': 'sig-desc', 'text-anchor': 'middle'}, text=desc_text)

    filepath = os.path.join(IMG_FOLDER, "v24-v28-dte-dce-interface.svg")
    tree = ET.ElementTree(svg)
    ET.indent(tree, space="  ")
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    print(f"Generated {filepath}")


if __name__ == '__main__':
    fig_vseries_timeline()
    fig_v90_pcm_architecture()
    fig_v24_v28_dte_dce()
