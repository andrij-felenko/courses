# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми mavlink-terrain-protocol."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_terrain_geometry():
    """Геометрія польоту за рельєфом: висоти AMSL, AGL, висота рельєфу та вектор попередження."""
    w, h = 940, 580
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок зверху
    b, _, _ = textbox(w / 2, 28, "ГЕОМЕТРИЧНА МОДЕЛЬ ПОЛЬОТУ ЗА РЕЛЬЄФОМ (TERRAIN FOLLOWING)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Рівень геоїда / моря (MSL / AMSL = 0)
    y_sea = 480
    body += line(40, y_sea, 900, y_sea, color="#2980b9", sw=2, dash="6,4")
    b_sea, _, _ = textbox(140, y_sea + 22, "Рівень моря / Геоїд EGM96 (AMSL = 0 м)", size=11, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=4)
    body += b_sea

    # Складений профіль рельєфу (пагорби, низина, гора)
    pts = [
        (40, 420), (120, 400), (200, 350), (280, 360), (360, 390),
        (440, 370), (520, 270), (600, 210), (680, 240), (760, 290), (900, 330)
    ]
    path_d = ["M %d %d" % pts[0]]
    for p in pts[1:]:
        path_d.append("L %d %d" % p)
    
    # Заливка землі під рельєфом
    fill_d = path_d + ["L 900 %d" % y_sea, "L 40 %d" % y_sea, "Z"]
    body += '<path d="%s" fill="#f4efe6" stroke="none"/>' % " ".join(fill_d)
    body += '<path d="%s" fill="none" stroke="#795548" stroke-width="3"/>' % " ".join(path_d)

    # Підпис рельєфу
    b_terr, _, _ = textbox(830, 360, "Поверхня рельєфу\n(SRTM / DEM)", size=11, bold=True, fill="#efebe9", stroke="#795548", pad=4)
    body += b_terr

    # Вузли сітки DEM (дискретні точки 4x4 матриць)
    for px, py in pts:
        body += circle(px, py, 4, fill="#c0392b", stroke="#922b21", sw=1.5)
        body += line(px, py + 5, px, y_sea - 2, color="#bdc3c7", sw=1, dash="2,3")

    # Індикатор кроку сітки
    b_grid_lbl, _, _ = textbox(520, y_sea + 22, "Крок сітки DEM (grid_spacing = 100 м)", size=10, fill="#ffffff", stroke="#95a5a6", pad=4)
    body += b_grid_lbl
    body += arrow(360, y_sea + 45, 440, y_sea + 45, color="#7f8c8d", sw=1.3)
    body += arrow(440, y_sea + 45, 360, y_sea + 45, color="#7f8c8d", sw=1.3)
    b_step_lbl, _, _ = textbox(400, y_sea + 45, "Δx = 100 м", size=9, bold=True, fill="#ffffff", stroke="#7f8c8d", pad=2)
    body += b_step_lbl

    # Безпілотник (точка x=280, y=210)
    drone_x, drone_y = 280, 210
    body += rect(drone_x - 18, drone_y - 8, 36, 16, fill="#2c3e50", stroke="#1a252f", sw=1.5, rx=3)
    body += line(drone_x - 24, drone_y, drone_x + 24, drone_y, color="#34495e", sw=3)
    body += circle(drone_x, drone_y, 4, fill="#e74c3c", stroke="#c0392b", sw=1)

    # Проєкція дрона на рельєф (x=280, y_terr=360)
    terr_y_under_drone = 360
    body += line(drone_x, drone_y + 10, drone_x, terr_y_under_drone - 6, color="#e67e22", sw=2, dash="4,3")
    body += circle(drone_x, terr_y_under_drone, 5, fill="#e67e22", stroke="#d35400", sw=1.5)

    # Висота рельєфу під дроном (terrain_height AMSL)
    mid_terr = (terr_y_under_drone + y_sea) / 2
    b_h_terr, _, _ = textbox(drone_x - 105, mid_terr, "terrain_height\n(AMSL = 120 м)", size=10, bold=True, fill="#eafaf1", stroke="#27ae60", pad=4)
    body += b_h_terr
    body += line(drone_x - 35, terr_y_under_drone, drone_x - 35, mid_terr - 18, color="#27ae60", sw=1.8)
    body += line(drone_x - 35, mid_terr + 18, drone_x - 35, y_sea, color="#27ae60", sw=1.8)
    body += arrow(drone_x - 35, mid_terr - 18, drone_x - 35, terr_y_under_drone, color="#27ae60", sw=1.5)
    body += arrow(drone_x - 35, mid_terr + 18, drone_x - 35, y_sea, color="#27ae60", sw=1.5)

    # Висота дрона над рельєфом (current_height AGL)
    mid_agl = (drone_y + terr_y_under_drone) / 2
    b_h_agl, _, _ = textbox(drone_x + 95, mid_agl, "current_height\n(AGL = 150 м)", size=10, bold=True, fill="#fef5e7", stroke="#d35400", pad=4)
    body += b_h_agl
    body += line(drone_x + 35, drone_y, drone_x + 35, mid_agl - 18, color="#d35400", sw=1.8)
    body += line(drone_x + 35, mid_agl + 18, drone_x + 35, terr_y_under_drone, color="#d35400", sw=1.8)
    body += arrow(drone_x + 35, mid_agl - 18, drone_x + 35, drone_y, color="#d35400", sw=1.5)
    body += arrow(drone_x + 35, mid_agl + 18, drone_x + 35, terr_y_under_drone, color="#d35400", sw=1.5)

    # Загальна барометрична/GNSS висота дрона (AMSL = 270 м)
    mid_amsl = (drone_y + y_sea) / 2
    b_h_amsl, _, _ = textbox(drone_x - 200, mid_amsl, "Повна висота БПЛА\n(AMSL = 270 м)", size=10, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=4)
    body += b_h_amsl
    body += line(drone_x - 145, drone_y, drone_x - 145, mid_amsl - 18, color="#2980b9", sw=1.8)
    body += line(drone_x - 145, mid_amsl + 18, drone_x - 145, y_sea, color="#2980b9", sw=1.8)
    body += arrow(drone_x - 145, mid_amsl - 18, drone_x - 145, drone_y, color="#2980b9", sw=1.5)
    body += arrow(drone_x - 145, mid_amsl + 18, drone_x - 145, y_sea, color="#2980b9", sw=1.5)

    # Вектор попередження (Lookahead Vector)
    look_x, look_y = 520, 160
    body += arrow(drone_x + 25, drone_y - 8, look_x, look_y, color="#c0392b", sw=2.5)
    b_look, _, _ = textbox(440, 240, "Вектор випередження (TERRAIN_LOOKAHEAD = 20 с)\nДистанція = V_gps · t_lookahead (наприклад 400 м)", size=10, bold=True, fill="#fdedec", stroke="#c0392b", pad=5)
    body += b_look

    # Траєкторія огинання пагорба (Terrain Following Path)
    body += line(drone_x, drone_y, 440, 95, color="#8e44ad", sw=2, dash="4,3")
    body += line(440, 95, 580, 60, color="#8e44ad", sw=2, dash="4,3")
    body += line(580, 60, 680, 85, color="#8e44ad", sw=2, dash="4,3")
    body += line(680, 85, 780, 130, color="#8e44ad", sw=2, dash="4,3")
    b_path, _, _ = textbox(720, 50, "Бажана траєкторія\n(Target AMSL = AGL + SRTM)", size=10, bold=True, fill="#f4ecf7", stroke="#8e44ad", pad=4)
    body += b_path

    render(os.path.join(OUT_DIR, "terrain-following-geometry.svg"), w, h, body)


def fig_terrain_grid_bitmask():
    """Структура кластера 8x8 блоків, 64-бітної маски та 4x4 матриці висот TERRAIN_DATA."""
    w, h = 900, 500
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок
    b, _, _ = textbox(w / 2, 25, "СТРУКТУРА ЗАПИТУ TERRAIN_REQUEST ТА БЛОКУ TERRAIN_DATA", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Ліва частина: Кластер 8x8 блоків (uint64_t mask)
    cx_left = 230
    b_cl_title, _, _ = textbox(cx_left, 65, "1. Кластер 8x8 блоків (TERRAIN_REQUEST, uint64_t mask)\nЦентр (lat, lon), біти від 0 (SW) до 63 (NE)", size=11, bold=True, fill="#fdf2e9", stroke="#e67e22", pad=5)
    body += b_cl_title

    # Малюємо сітку 8x8
    cell_s = 32
    start_x = cx_left - 4 * cell_s
    start_y = 105
    for r in range(8):
        for c in range(8):
            bit_idx = r * 8 + c
            x_c = start_x + c * cell_s
            y_c = start_y + (7 - r) * cell_s
            if bit_idx == 27:
                fill_col = "#e74c3c"
                stroke_col = "#922b21"
                sw_c = 2.5
            elif bit_idx in [18, 19, 20, 26, 28, 34, 35, 36]:
                fill_col = "#fef9e7"
                stroke_col = "#f39c12"
                sw_c = 1
            else:
                fill_col = "#eafaf1"
                stroke_col = "#27ae60"
                sw_c = 1
            body += rect(x_c, y_c, cell_s, cell_s, fill=fill_col, stroke=stroke_col, sw=sw_c, rx=2)
            txt_col = "#ffffff" if bit_idx == 27 else "#2c3e50"
            body += text(x_c + cell_s/2, y_c + cell_s/2 + 3.5, str(bit_idx), size=9, color=txt_col, anchor="middle", bold=(bit_idx==27))

    # Стрілки осей кластера
    body += arrow(start_x, start_y + 8 * cell_s + 15, start_x + 8 * cell_s + 10, start_y + 8 * cell_s + 15, color="#2980b9", sw=1.5)
    b_axis_lon, _, _ = textbox(start_x + 4 * cell_s, start_y + 8 * cell_s + 28, "Схід (Longitude, c = 0..7)", size=10, fill="#ffffff", stroke="#ffffff", color="#2980b9", pad=1)
    body += b_axis_lon

    body += arrow(start_x - 15, start_y + 8 * cell_s, start_x - 15, start_y - 10, color="#2980b9", sw=1.5)
    b_axis_lat, _, _ = textbox(start_x - 45, start_y + 4 * cell_s, "Північ\n(Latitude,\nr = 0..7)", size=9, fill="#ffffff", stroke="#ffffff", color="#2980b9", pad=1)
    body += b_axis_lat

    # Легенда бітів кластера
    b_leg1, _, _ = textbox(cx_left - 80, start_y + 8 * cell_s + 50, "Блок завантажений (біт = 0)", size=9, fill="#eafaf1", stroke="#27ae60", pad=3)
    b_leg2, _, _ = textbox(cx_left + 80, start_y + 8 * cell_s + 50, "Блок потрібен (біт = 1)", size=9, fill="#fef9e7", stroke="#f39c12", pad=3)
    body += b_leg1 + b_leg2

    # Зв'язувальні лінії від виділеного блоку bit=27 до правої частини
    bx27 = start_x + 3 * cell_s + cell_s/2
    by27 = start_y + (7 - 3) * cell_s + cell_s/2
    body += line(bx27 + cell_s/2 + 2, by27 - cell_s/2, 540, 120, color="#e74c3c", sw=1.5, dash="3,3")
    body += line(bx27 + cell_s/2 + 2, by27 + cell_s/2, 540, 390, color="#e74c3c", sw=1.5, dash="3,3")

    # Права частина: 4x4 матриця TERRAIN_DATA (gridbit=27)
    cx_right = 690
    b_data_title, _, _ = textbox(cx_right, 65, "2. Блок TERRAIN_DATA (gridbit=27, 4x4 висоти int16_t)\nПівденно-західний кут (lat_sw, lon_sw), data[0..15]", size=11, bold=True, fill="#fadbd8", stroke="#c0392b", pad=5)
    body += b_data_title

    # Малюємо 4x4 матрицю вузлів
    node_dx = 65
    node_dy = 65
    grid_ox = cx_right - 1.5 * node_dx
    grid_oy = 135

    # Сітка ліній між вузлами
    for r in range(4):
        y_r = grid_oy + (3 - r) * node_dy
        body += line(grid_ox, y_r, grid_ox + 3 * node_dx, y_r, color="#bdc3c7", sw=1.2)
    for c in range(4):
        x_c = grid_ox + c * node_dx
        body += line(x_c, grid_oy, x_c, grid_oy + 3 * node_dy, color="#bdc3c7", sw=1.2)

    sample_elevations = [
        [120, 125, 132, 140],
        [124, 130, 138, 148],
        [135, 142, 150, 162],
        [145, 155, 168, 180]
    ]

    for r in range(4):
        for c in range(4):
            idx = r * 4 + c
            nx = grid_ox + c * node_dx
            ny = grid_oy + (3 - r) * node_dy
            elev = sample_elevations[r][c]
            is_sw = (idx == 0)
            node_fill = "#e74c3c" if is_sw else "#3498db"
            body += circle(nx, ny, 6, fill=node_fill, stroke="#2c3e50", sw=1.5)
            body += text(nx, ny - 10, "d[%d]" % idx, size=9, color="#7f8c8d", anchor="middle")
            body += text(nx, ny + 17, "%dм" % elev, size=10, color="#2c3e50", anchor="middle", bold=True)

    b_sw_lbl, _, _ = textbox(grid_ox - 35, grid_oy + 3 * node_dy + 35, "SW кут: (lat, lon)\nІндекс d[0] = 120м", size=9, bold=True, fill="#fdedec", stroke="#e74c3c", pad=4)
    body += b_sw_lbl

    b_ne_lbl, _, _ = textbox(grid_ox + 3 * node_dx + 35, grid_oy - 15, "NE кут: d[15] = 180м", size=9, bold=True, fill="#ebf5fb", stroke="#3498db", pad=4)
    body += b_ne_lbl

    b_dim_lbl, _, _ = textbox(cx_right, grid_oy + 3 * node_dy + 55, "Розмір комірки = grid_spacing (100 м) · Охоплення блоку = 300 м × 300 м", size=10, fill="#f4f6f7", stroke="#7f8c8d", pad=4)
    body += b_dim_lbl

    render(os.path.join(OUT_DIR, "terrain-grid-bitmask.svg"), w, h, body)


def fig_terrain_exchange_flow():
    """Діаграма послідовності обміну MAVLink Terrain Protocol: запит, передача блоків, звіт."""
    w, h = 880, 540
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок зверху
    b, _, _ = textbox(w / 2, 26, "ПОСЛІДОВНІСТЬ ОБМІНУ ДАНИМИ РЕЛЬЄФУ (TERRAIN PROTOCOL FLOW)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    x_fc = 160
    x_gcs = 500
    x_dem = 760

    b1, _, _ = textbox(x_fc, 70, "Польотний контролер (FCU)\n[Підсистема AP_Terrain]", size=12, bold=True, fill="#fdf2e9", stroke="#d35400", pad=6)
    b2, _, _ = textbox(x_gcs, 70, "Наземна станція (GCS)\n[Mission Planner / QGC]", size=12, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=6)
    b3, _, _ = textbox(x_dem, 70, "Сховище рельєфу\n[SRTM / ASTER DEM]", size=12, bold=True, fill="#eafaf1", stroke="#27ae60", pad=6)
    body += b1 + b2 + b3

    body += line(x_fc, 100, x_fc, 510, color="#7f8c8d", sw=1.5, dash="5,4")
    body += line(x_gcs, 100, x_gcs, 510, color="#7f8c8d", sw=1.5, dash="5,4")
    body += line(x_dem, 100, x_dem, 510, color="#7f8c8d", sw=1.5, dash="5,4")

    # 1. Подія: промах кешу на борту
    y1 = 130
    b_ev1, _, _ = textbox(x_fc, y1, "Промах кешу RAM/SD:\nвиявлено відсутні блоки в радіусі lookahead", size=9, fill="#fef9e7", stroke="#f39c12", pad=4)
    body += b_ev1

    # 2. TERRAIN_REQUEST (#133)
    y2 = 175
    body += arrow(x_fc, y2, x_gcs, y2, color="#d35400", sw=2)
    b_req, _, _ = textbox(330, y2 - 14, "TERRAIN_REQUEST (#133) [lat, lon, spacing=100, mask=0x0000000000000003]", size=10, bold=True, fill="#ffffff", stroke="#d35400", pad=3)
    body += b_req

    # 3. GCS вибірка з DEM
    y3 = 220
    body += arrow(x_gcs, y3, x_dem, y3, color="#2457d6", sw=1.5)
    b_dem_q, _, _ = textbox(630, y3 - 12, "Читання тайлів SRTM (.hgt)", size=9, fill="#ffffff", stroke="#2457d6", pad=2)
    body += b_dem_q

    y4 = 250
    body += arrow(x_dem, y4, x_gcs, y4, color="#27ae60", sw=1.5)
    b_dem_ans, _, _ = textbox(630, y4 - 12, "Масив висот 4x4 (int16_t)", size=9, fill="#ffffff", stroke="#27ae60", pad=2)
    body += b_dem_ans

    # 4. TERRAIN_DATA (#134) блок 0
    y5 = 295
    body += arrow(x_gcs, y5, x_fc, y5, color="#2457d6", sw=2)
    b_d0, _, _ = textbox(330, y5 - 14, "TERRAIN_DATA (#134) [gridbit=0, lat_sw, lon_sw, data[16]]", size=10, bold=True, fill="#ffffff", stroke="#2457d6", pad=3)
    body += b_d0

    # 5. TERRAIN_DATA (#134) блок 1
    y6 = 340
    body += arrow(x_gcs, y6, x_fc, y6, color="#2457d6", sw=2)
    b_d1, _, _ = textbox(330, y6 - 14, "TERRAIN_DATA (#134) [gridbit=1, lat_sw, lon_sw, data[16]]", size=10, bold=True, fill="#ffffff", stroke="#2457d6", pad=3)
    body += b_d1

    # 6. Фіксація на борту
    y7 = 385
    b_save, _, _ = textbox(x_fc, y7, "Запис у RAM-кеш та збереження\nна MicroSD (/TERRAIN/xxxx.DAT)", size=9, fill="#eafaf1", stroke="#27ae60", pad=4)
    body += b_save

    # 7. Звіт TERRAIN_REPORT (#136)
    y8 = 435
    body += arrow(x_fc, y8, x_gcs, y8, color="#27ae60", sw=2)
    b_rep, _, _ = textbox(330, y8 - 14, "TERRAIN_REPORT (#136) [terrain_h=120м, current_h=150м, pending=0, loaded=64]", size=10, bold=True, fill="#eafaf1", stroke="#27ae60", pad=4)
    body += b_rep

    # 8. Запит перевірки TERRAIN_CHECK (#135)
    y9 = 485
    body += arrow(x_gcs, y9, x_fc, y9, color="#8e44ad", sw=1.5)
    b_chk, _, _ = textbox(330, y9 - 14, "TERRAIN_CHECK (#135) [lat, lon майбутньої точки місії] -> автопілот відповідає REPORT", size=9, fill="#f4ecf7", stroke="#8e44ad", pad=3)
    body += b_chk

    render(os.path.join(OUT_DIR, "terrain-exchange-flow.svg"), w, h, body)


def fig_terrain_cache_architecture():
    """Архітектура підсистеми AP_Terrain в автопілоті: пам'ять, інтерполяція, failsafe."""
    w, h = 920, 520
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок
    b, _, _ = textbox(w / 2, 26, "БОРТОВА АРХІТЕКТУРА ОБРОБКИ РЕЛЬЄФУ В АВТОПІЛОТІ", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Блоки вхідних даних (зліва)
    b_gnss, _, _ = textbox(110, 85, "GNSS / Інерціальна система\nПоточні (lat, lon, alt_amsl, V)", size=10, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=6)
    b_wp, _, _ = textbox(110, 175, "Менеджер місій (AP_Mission)\nЦіль MAV_FRAME_GLOBAL_TERRAIN_ALT", size=10, bold=True, fill="#f4ecf7", stroke="#8e44ad", pad=6)
    body += b_gnss + b_wp

    # Центральний модуль: Генератор траєкторії та прогнозу
    b_lookahead, _, _ = textbox(340, 130, "Предиктор траєкторії та черги запитів\n(Lookahead = V_gps · TERRAIN_LOOKAHEAD)\nРозрахунок необхідних секторів сітки", size=10, bold=True, fill="#fef9e7", stroke="#f39c12", pad=6)
    body += b_lookahead

    body += arrow(215, 85, 235, 120, color="#2980b9", sw=1.5)
    body += arrow(215, 175, 235, 140, color="#8e44ad", sw=1.5)

    # Дворівневе сховище рельєфу (RAM LRU + SD Card)
    b_ram, _, _ = textbox(340, 275, "Оперативний LRU-кеш блоків у RAM\n(Кільцевий пул 32..64 блоків 4x4)", size=10, bold=True, fill="#eafaf1", stroke="#27ae60", pad=6)
    b_sd, _, _ = textbox(340, 395, "Енергонезалежне сховище MicroSD\nФайли /TERRAIN/xxxx.DAT (тайли 1°×1°)", size=10, bold=True, fill="#efebe9", stroke="#795548", pad=6)
    body += b_sd + b_ram

    # Зв'язки між пам'яттю
    body += arrow(300, 310, 300, 360, color="#795548", sw=1.5)
    b_sd_rw, _, _ = textbox(370, 335, "Запис / Читання тайлу", size=9, fill="#ffffff", stroke="#ffffff", color="#795548", pad=1)
    body += b_sd_rw

    body += arrow(340, 175, 340, 240, color="#d35400", sw=1.8)

    # Зовнішній лінк MAVLink (праворуч від RAM кешу)
    b_mavlink, _, _ = textbox(690, 275, "Трансивер MAVLink (GCS)\nTERRAIN_REQUEST <-> TERRAIN_DATA\nЗавантаження по радіолінку при промаху", size=10, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=6)
    body += b_mavlink

    body += arrow(460, 268, 545, 268, color="#2457d6", sw=1.8)
    body += arrow(545, 282, 460, 282, color="#27ae60", sw=1.8)

    # Модуль 2D білінійної інтерполяції
    b_interp, _, _ = textbox(620, 130, "Модуль білінійної інтерполяції\nРозрахунок h(lat, lon) між 4 вузлами\nОбчислення точної висоти поверхні", size=10, bold=True, fill="#eafaf1", stroke="#27ae60", pad=6)
    body += b_interp

    body += arrow(380, 240, 520, 150, color="#27ae60", sw=1.8)
    b_nodes_lbl, _, _ = textbox(445, 185, "4 вузли сітки", size=9, bold=True, fill="#ffffff", stroke="#27ae60", pad=2)
    body += b_nodes_lbl

    # Контур польотного контролера (праворуч)
    b_alt_ctrl, _, _ = textbox(815, 130, "Контур висоти\nTarget_AMSL = WP_AGL + SRTM\nСтабілізація кліренсу", size=10, bold=True, fill="#fdf2e9", stroke="#d35400", pad=6)
    body += b_alt_ctrl
    body += arrow(725, 130, 735, 130, color="#27ae60", sw=1.8)

    # Монітор безпеки Terrain Failsafe (внизу праворуч)
    b_fs, _, _ = textbox(730, 410, "Монітор безпеки (Terrain Failsafe)\nЯкщо блок відсутній у радіусі lookahead:\n1. Екстрений набір висоти до RTL_ALT\n2. Режим Loiter / Очікування даних\n3. Повернення на базу (RTL)", size=10, bold=True, fill="#fdedec", stroke="#c0392b", pad=7)
    body += b_fs

    body += arrow(460, 130, 620, 365, color="#c0392b", sw=1.5)
    b_fs_lbl, _, _ = textbox(540, 235, "Промах кешу > таймаут", size=9, bold=True, fill="#ffffff", stroke="#c0392b", pad=2)
    body += b_fs_lbl

    render(os.path.join(OUT_DIR, "terrain-cache-architecture.svg"), w, h, body)


if __name__ == '__main__':
    fig_terrain_geometry()
    fig_terrain_grid_bitmask()
    fig_terrain_exchange_flow()
    fig_terrain_cache_architecture()
    print("Усі SVG-фігури для mavlink-terrain-protocol успішно згенеровано.")
