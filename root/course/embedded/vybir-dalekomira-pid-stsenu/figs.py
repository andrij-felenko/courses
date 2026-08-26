# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. sensor-cone-comparison: Діаграми спрямованості та просторова геометрія ──
def fig_sensor_cone_comparison():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 32, "Геометрія випромінювання: від широкого акустичного конуса до лазерної голки",
                  size=13, color=MUTED))

    cols = [
        {"title": "Ультразвук (40 кГц)", "tech": "HC-SR04 / JSN-SR04T", "beam": "Конус 25°–30°",
         "pros": "Бачить площини й скло", "cons": "Розмита позиція в конусі", "col": NEG},
        {"title": "Оптичний ToF (940 нм)", "tech": "VL53L0X / VL53L5CX", "beam": "Піраміда FOV 25°–45°",
         "pros": "Матриця 8x8 зон", "cons": "Сліпне від сонця й чорного", "col": POS},
        {"title": "LiDAR (905 нм)", "tech": "TFmini / RPLIDAR A2", "beam": "Лазерний промінь 0.2°",
         "pros": "Кутова точність < 0.5°", "cons": "Сліпне на склі й дощі", "col": FIELD},
        {"title": "mmWave Радар (60 ГГц)", "tech": "IWR6843 / LD2410", "beam": "Пелюстка 60° + Doppler",
         "pros": "Проникає крізь пластик", "cons": "Перевідбиття від металу", "col": "#8e44ad"}
    ]

    col_w = 190
    start_x = 22
    y_top = 56
    card_h = 344

    for i, c in enumerate(cols):
        cx = start_x + i * (col_w + 12)
        # Background card
        p.append(rect(cx, y_top, col_w, card_h, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
        
        # Header banner
        p.append(rect(cx, y_top, col_w, 44, fill=FILL, stroke="#d0d7de", sw=1.0, rx=8))
        p.append(rect(cx, y_top + 36, col_w, 8, fill=FILL, stroke="none", sw=0)) # flatten bottom corners of header
        p.append(text(cx + col_w/2, y_top + 18, c["title"], size=12, color=c["col"], bold=True))
        p.append(text(cx + col_w/2, y_top + 35, c["tech"], size=10, color=MUTED))

        # Sensor visual area (center of card)
        sym_cy = y_top + 122
        sym_cx = cx + col_w/2

        # Draw sensor body
        p.append(rect(sym_cx - 28, sym_cy - 48, 56, 18, fill="#2c3e50", stroke=LINE, sw=1.2, rx=3))
        p.append(text(sym_cx, sym_cy - 35, "SENSOR", size=9.5, color="#ffffff", bold=True))

        # Draw emitted beam
        if i == 0: # Ultrasound cone
            p.append(f'<path d="M {sym_cx-8} {sym_cy-30} L {sym_cx-48} {sym_cy+42} A 60 60 0 0 0 {sym_cx+48} {sym_cy+42} L {sym_cx+8} {sym_cy-30} Z" fill="{NEG}" fill-opacity="0.15" stroke="{NEG}" stroke-width="1.2" stroke-dasharray="3,2"/>')
            p.append(circle(sym_cx - 18, sym_cy + 18, 3.5, fill=POS, stroke=LINE, sw=1))
            p.append(text(sym_cx + 2, sym_cy + 20, "луна від кута", size=9.5, color=POS, bold=True, anchor="start"))
        elif i == 1: # ToF multi-zone grid
            p.append(f'<polygon points="{sym_cx-6},{sym_cy-30} {sym_cx-38},{sym_cy+40} {sym_cx+38},{sym_cy+40} {sym_cx+6},{sym_cy-30}" fill="{POS}" fill-opacity="0.15" stroke="{POS}" stroke-width="1.2"/>')
            for gx in range(-2, 3):
                p.append(line(sym_cx, sym_cy-30, sym_cx + gx*15, sym_cy+40, color=POS, sw=0.8, dash="2,2"))
        elif i == 2: # LiDAR thin beam
            p.append(line(sym_cx, sym_cy-30, sym_cx, sym_cy+42, color=FIELD, sw=2.5))
            p.append(line(sym_cx, sym_cy-30, sym_cx - 30, sym_cy+38, color=FIELD, sw=1.0, dash="3,2"))
            p.append(line(sym_cx, sym_cy-30, sym_cx + 30, sym_cy+38, color=FIELD, sw=1.0, dash="3,2"))
            p.append(circle(sym_cx, sym_cy+42, 3.5, fill=FIELD, stroke=LINE, sw=1))
        elif i == 3: # mmWave radar
            for r_val in [25, 45, 65]:
                p.append(f'<path d="M {sym_cx - r_val*0.6} {sym_cy - 28 + r_val} A {r_val} {r_val} 0 0 0 {sym_cx + r_val*0.6} {sym_cy - 28 + r_val}" fill="none" stroke="#8e44ad" stroke-width="1.5"/>')
            p.append(arrow(sym_cx, sym_cy + 10, sym_cx, sym_cy + 38, color=POS, sw=2.0))
            p.append(text(sym_cx + 6, sym_cy + 25, "v (Doppler)", size=9.5, color=POS, bold=True, anchor="start"))

        # Details box
        box_y = y_top + 185
        p.append(rect(cx + 8, box_y, col_w - 16, 144, fill="#ffffff", stroke="#e1e4e8", sw=1.0, rx=4))
        p.append(text(cx + col_w/2, box_y + 18, c["beam"], size=10.5, color=INK, bold=True))
        p.append(line(cx + 16, box_y + 26, cx + col_w - 16, box_y + 26, color="#e1e4e8", sw=1.0))
        
        p.append(text(cx + 12, box_y + 45, "+ " + c["pros"], size=9.5, color=FIELD, anchor="start", bold=True))
        p.append(text(cx + 12, box_y + 72, "− " + c["cons"], size=9.5, color=POS, anchor="start", bold=True))
        
        if i == 0:
            p.append(text(cx + 12, box_y + 104, "Частота: 20–40 Гц", size=9.5, color=MUTED, anchor="start"))
            p.append(text(cx + 12, box_y + 124, "Сліпа зона: 2–20 см", size=9.5, color=MUTED, anchor="start"))
        elif i == 1:
            p.append(text(cx + 12, box_y + 104, "Частота: 30–60 Гц", size=9.5, color=MUTED, anchor="start"))
            p.append(text(cx + 12, box_y + 124, "Сліпа зона: 0 см", size=9.5, color=MUTED, anchor="start"))
        elif i == 2:
            p.append(text(cx + 12, box_y + 104, "Частота: 1–15 кГц", size=9.5, color=MUTED, anchor="start"))
            p.append(text(cx + 12, box_y + 124, "Сліпа зона: 5–10 см", size=9.5, color=MUTED, anchor="start"))
        elif i == 3:
            p.append(text(cx + 12, box_y + 104, "Частота: 10–50 Гц", size=9.5, color=MUTED, anchor="start"))
            p.append(text(cx + 12, box_y + 124, "Сліпа зона: 10–15 см", size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "sensor-cone-comparison.svg"), W, H, *p,
           title="Порівняння геометрії променя та робочих зон сенсорів відстані")


# ── 2. scene-physics-traps: Фізичні пастки реального середовища ────────────────
def fig_scene_physics_traps():
    W, H = 840, 380
    p = []
    p.append(text(W / 2, 30, "Фізика сцени: де і чому окремі сенсори катастрофічно брешуть",
                  size=13, color=MUTED))

    sub_w = 190
    start_x = 22
    y0 = 55
    h0 = 305

    traps = [
        {"title": "Акустичне дзеркало", "sub": "Ультразвук", "col": NEG,
         "desc": "Кут > 15° відводить луну повз приймач. Стіна невидима!"},
        {"title": "Сонячне засвічення", "sub": "Оптичний ToF", "col": POS,
         "desc": "Сонце заливає SPAD фотонами; 5% чорний не дає сигналу."},
        {"title": "Прозоре скло й дощ", "sub": "Оптичний LiDAR", "col": FIELD,
         "desc": "Лазер проходить крізь скло або розсіюється на краплях."},
        {"title": "Радіопрозорість", "sub": "mmWave Радар", "col": "#8e44ad",
         "desc": "Бачить крізь бампер, але плутається у відлуннях металу."}
    ]

    for i, t in enumerate(traps):
        bx = start_x + i * (sub_w + 12)
        p.append(rect(bx, y0, sub_w, h0, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
        
        # Header
        p.append(text(bx + sub_w/2, y0 + 20, t["title"], size=11, color=t["col"], bold=True))
        p.append(text(bx + sub_w/2, y0 + 36, t["sub"], size=10, color=MUTED))
        p.append(line(bx + 12, y0 + 44, bx + sub_w - 12, y0 + 44, color="#e1e4e8", sw=1.0))

        # Scene illustration box
        sc_x = bx + 12
        sc_y = y0 + 52
        sc_w = sub_w - 24
        sc_h = 145
        p.append(rect(sc_x, sc_y, sc_w, sc_h, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))

        if i == 0: # Ultrasonic specular reflection
            # Transducer
            p.append(rect(sc_x + 6, sc_y + 82, 28, 32, fill="#2c3e50", stroke=LINE, sw=1.0, rx=2))
            p.append(text(sc_x + 20, sc_y + 102, "УЗ", size=10, color="#ffffff", bold=True))
            # Slanted wall
            p.append(line(sc_x + sc_w - 10, sc_y + 15, sc_x + sc_w - 55, sc_y + sc_h - 15, color=LINE, sw=4.0))
            # Beams
            p.append(arrow(sc_x + 34, sc_y + 92, sc_x + sc_w - 35, sc_y + 62, color=NEG, sw=1.8))
            p.append(arrow(sc_x + sc_w - 35, sc_y + 62, sc_x + 45, sc_y + 22, color=POS, sw=1.8))
            p.append(text(sc_x + sc_w/2, sc_y + 134, "Луна летить повз!", size=10, color=POS, bold=True))

        elif i == 1: # Sun glare + black target
            # Sun icon
            p.append(circle(sc_x + sc_w - 24, sc_y + 26, 12, fill="#f39c12", stroke="#d35400", sw=1.2))
            p.append(line(sc_x + sc_w - 38, sc_y + 36, sc_x + 48, sc_y + 82, color="#f39c12", sw=1.5, dash="2,2"))
            # Sensor
            p.append(rect(sc_x + 6, sc_y + 72, 32, 24, fill="#2c3e50", stroke=LINE, sw=1.0, rx=2))
            p.append(text(sc_x + 22, sc_y + 88, "ToF", size=9.5, color="#ffffff", bold=True))
            # Black target
            p.append(rect(sc_x + sc_w - 20, sc_y + 62, 12, 54, fill="#1a1a1a", stroke=LINE, sw=1.2, rx=1))
            p.append(arrow(sc_x + 38, sc_y + 84, sc_x + sc_w - 22, sc_y + 84, color=POS, sw=1.5))
            p.append(text(sc_x + sc_w/2, sc_y + 134, "SPAD залитий шумом", size=10, color=POS, bold=True))

        elif i == 2: # Glass & rain droplets
            # Sensor
            p.append(rect(sc_x + 6, sc_y + 68, 32, 26, fill="#2c3e50", stroke=LINE, sw=1.0, rx=2))
            p.append(text(sc_x + 22, sc_y + 84, "LiDAR", size=9.5, color="#ffffff", bold=True))
            # Glass pane
            p.append(rect(sc_x + 68, sc_y + 18, 6, 88, fill="#a5d8ff", stroke="#339af0", sw=1.2, rx=1))
            p.append(text(sc_x + 71, sc_y + 118, "Скло", size=9.5, color="#1971c2", bold=True))
            # Beam passes through glass to far wall
            p.append(line(sc_x + 38, sc_y + 62, sc_x + sc_w - 15, sc_y + 62, color=FIELD, sw=1.8))
            p.append(rect(sc_x + sc_w - 15, sc_y + 30, 8, 65, fill="#95a5a6", stroke=LINE, sw=1.0))
            p.append(text(sc_x + sc_w/2, sc_y + 134, "Скло проігноровано", size=10, color=POS, bold=True))

        elif i == 3: # mmWave through bumper
            # Radar
            p.append(rect(sc_x + 6, sc_y + 68, 30, 26, fill="#2c3e50", stroke=LINE, sw=1.0, rx=2))
            p.append(text(sc_x + 21, sc_y + 84, "FMCW", size=9.5, color="#ffffff", bold=True))
            # Plastic bumper
            p.append(rect(sc_x + 52, sc_y + 18, 8, 90, fill="#95a5a6", stroke=LINE, sw=1.0, rx=2))
            p.append(text(sc_x + 56, sc_y + 120, "Пластик", size=9.5, color=MUTED))
            # Radar waves passing through
            for rw_off in [15, 30, 45]:
                p.append(f'<path d="M {sc_x + 68 + rw_off*0.8} {sc_y + 40} A 30 30 0 0 1 {sc_x + 68 + rw_off*0.8} {sc_y + 90}" fill="none" stroke="#8e44ad" stroke-width="1.4"/>')
            p.append(text(sc_x + sc_w/2, sc_y + 134, "Хвиля проходить крізь", size=10, color=FIELD, bold=True))

        # Text explanation
        desc_lines = t["desc"].split(". ")
        p.append(text(bx + sub_w/2, y0 + 216, desc_lines[0] + ".", size=10, color=INK))
        if len(desc_lines) > 1:
            p.append(text(bx + sub_w/2, y0 + 236, desc_lines[1], size=10, color=POS if i < 3 else FIELD, bold=True))

        # Bottom verdict badge
        p.append(rect(bx + 12, y0 + 262, sub_w - 24, 28, fill=FILL, stroke="#d0d7de", sw=1.0, rx=4))
        if i == 0:
            p.append(text(bx + sub_w/2, y0 + 280, "Лікується: мультисенсором", size=9.5, color=INK, bold=True))
        elif i == 1:
            p.append(text(bx + sub_w/2, y0 + 280, "Лікується: УЗ / радаром", size=9.5, color=INK, bold=True))
        elif i == 2:
            p.append(text(bx + sub_w/2, y0 + 280, "Лікується: УЗ сонаром", size=9.5, color=INK, bold=True))
        elif i == 3:
            p.append(text(bx + sub_w/2, y0 + 280, "Ідеально: для авто/вулиці", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "scene-physics-traps.svg"), W, H, *p,
           title="Фізичні пастки сцени для ультразвуку, оптичного ToF, LiDAR і радара")


# ── 3. ranging-fusion-pipeline: Пайплайн агрегації вимірів ──────────────────────
def fig_ranging_fusion_pipeline():
    W, H = 840, 340
    p = []
    p.append(text(W / 2, 28, "Тракт злиття вимірів: від сирих фізичних сигналів до безпечного гальмівного коридору",
                  size=13, color=MUTED))

    # 4 stage columns
    stages = [
        {"x": 25, "w": 170, "title": "1. Сирі давачі", "items": ["HC-SR04 (час імпульсу)", "VL53L1X (SPAD ToF)", "mmWave (IF чирп)", "Термометр NTC (°C)"], "col": "#2c3e50"},
        {"x": 235, "w": 175, "title": "2. Фізична корекція", "items": ["c(T) = 331.3 + 0.606·T", "Відсів сонячного шуму", "Doppler фільтрація", "Бланкування сліпих зон"], "col": NEG},
        {"x": 450, "w": 170, "title": "3. Оцінка довіри (W)", "items": ["SNR / Ambient валідація", "Ваги довіри w_i ∈ [0, 1]", "Виявлення конфліктів", "Крос-перевірка цілей"], "col": "#f39c12"},
        {"x": 660, "w": 155, "title": "4. Безпечний вихід", "items": ["Мін. достовірна d_safe", "Оцінка швидкості v_rel", "Fail-safe прапорець", "Коридор зупинки"], "col": FIELD}
    ]

    for s in stages:
        p.append(rect(s["x"], 52, s["w"], 260, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
        p.append(rect(s["x"], 52, s["w"], 38, fill=FILL, stroke="#d0d7de", sw=1.0, rx=8))
        p.append(rect(s["x"], 52 + 30, s["w"], 8, fill=FILL, stroke="none", sw=0))
        p.append(text(s["x"] + s["w"]/2, 52 + 24, s["title"], size=11.5, color=s["col"], bold=True))

        for j, itm in enumerate(s["items"]):
            iy = 110 + j * 48
            p.append(rect(s["x"] + 8, iy - 14, s["w"] - 16, 38, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
            p.append(text(s["x"] + s["w"]/2, iy + 10, itm, size=10, color=INK))

    # Flow arrows between stages
    p.append(arrow(195, 180, 231, 180, color=LINE, sw=2.0))
    p.append(arrow(410, 180, 446, 180, color=LINE, sw=2.0))
    p.append(arrow(620, 180, 656, 180, color=LINE, sw=2.0))

    render(os.path.join(OUT, "ranging-fusion-pipeline.svg"), W, H, *p,
           title="Архітектурний конвеєр злиття та валідації показів далекомірів")


if __name__ == "__main__":
    fig_sensor_cone_comparison()
    fig_scene_physics_traps()
    fig_ranging_fusion_pipeline()
    print("All figures generated successfully.")
