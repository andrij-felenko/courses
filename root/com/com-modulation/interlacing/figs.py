# -*- coding: utf-8 -*-
"""Фігури до теми «Черезрядкова розгортка (interlacing)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.4):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


def hline(x1, x2, y, color=MUTED, sw=1.0, dash="5,4"):
    return line(x1, y, x2, y, color=color, sw=sw, dash=dash)


# ── фіг. 1: геометрія полів та черезрядкова розгортка ─────────────────────────
def fig_fields_raster():
    W, H = 780, 360
    oy, h = 75, 210
    w = 210
    rows = 10

    def draw_screen(ox, title, mode, main_color):
        parts = [
            rect(ox, oy, w, h, fill=BG, stroke=LINE, sw=1.8),
            text(ox + w / 2, oy - 14, title, size=12, color=main_color, bold=True)
        ]
        for r in range(rows):
            y = oy + (r + 0.5) * h / rows
            is_odd = (r % 2 == 0)
            if mode == 'odd' and is_odd:
                parts.append(line(ox + 8, y, ox + w - 8, y, color=FIELD, sw=2.5))
            elif mode == 'even' and not is_odd:
                parts.append(line(ox + 8, y, ox + w - 8, y, color=POS, sw=2.5))
            elif mode == 'full':
                c = FIELD if is_odd else POS
                parts.append(line(ox + 8, y, ox + w - 8, y, color=c, sw=2.2))
        return parts

    parts = []
    # Три екрани: Поле 1 (непарне), Поле 2 (парне), Повний кадр
    parts += draw_screen(40, "Поле 1: непарні рядки", "odd", FIELD)
    parts += draw_screen(285, "Поле 2: парні рядки", "even", POS)
    parts += draw_screen(530, "Повний кадр: переплетення", "full", FIELD)

    # Стрілки поєднання
    parts.append(line(255, oy + h / 2, 280, oy + h / 2, color=MUTED, sw=1.5))
    parts.append(polyline([(273, oy + h / 2 - 4), (280, oy + h / 2), (273, oy + h / 2 + 4)], color=MUTED, sw=1.5))
    parts.append(line(500, oy + h / 2, 525, oy + h / 2, color=MUTED, sw=1.5))
    parts.append(polyline([(518, oy + h / 2 - 4), (525, oy + h / 2), (518, oy + h / 2 + 4)], color=MUTED, sw=1.5))

    parts += [
        text(40 + w / 2, oy + h + 24, "Таймінг t = 0 мкс", size=11, color=MUTED),
        text(40 + w / 2, oy + h + 40, "рядки 1, 3, 5, 7...", size=11, color=FIELD),
        text(285 + w / 2, oy + h + 24, "Таймінг t = +20 мкс", size=11, color=MUTED),
        text(285 + w / 2, oy + h + 40, "рядки 2, 4, 6, 8...", size=11, color=POS),
        text(530 + w / 2, oy + h + 24, "Відтворення на екрані", size=11, color=MUTED),
        text(530 + w / 2, oy + h + 40, "2 поля = 1 кадр (50 Гц)", size=11, color=FIELD, bold=True),
    ]

    render(os.path.join(IMG, "fields-raster.svg"), W, H, *parts)


# ── фіг. 2: зубчастий кадровий синхроімпульс та інтегратор ─────────────────────
def fig_serrated_vsync():
    W, H = 780, 380
    x0, x1 = 70, 720
    y_sig_hi, y_sig_lo = 80, 160
    y_int_0, y_int_max = 330, 210

    parts = [
        # Написи вісей
        text(x0 - 8, y_sig_hi - 10, "Сигнал VSYNC", size=11, color=MUTED, anchor="end", bold=True),
        text(x0 - 8, y_int_max - 10, "Напруга RC-інтегратора V_c", size=11, color=MUTED, anchor="end", bold=True),
        hline(x0, x1, y_sig_hi),
        hline(x0, x1, y_sig_lo),
        hline(x0, x1, y_int_0),
    ]

    # Поріг спрацьовування кадрового генератора
    y_thresh = 250
    parts.append(hline(x0, x1, y_thresh, color=NEG, dash="4,4"))
    parts.append(text(x1 + 6, y_thresh + 4, "поріг V_th", size=10, color=NEG, anchor="start", bold=True))

    # Сигнал VSYNC з зубцями (Serrated VSYNC)
    pts_sig = [(x0, y_sig_hi)]
    curr_x = x0 + 20

    # 2 звичайних HSYNC (частота f_H)
    for _ in range(2):
        pts_sig += [(curr_x, y_sig_hi), (curr_x, y_sig_lo), (curr_x + 12, y_sig_lo), (curr_x + 12, y_sig_hi)]
        curr_x += 45

    # 5 урівнювальних коротких імпульсів (2f_H)
    x_pre_start = curr_x
    for _ in range(4):
        pts_sig += [(curr_x, y_sig_hi), (curr_x, y_sig_lo), (curr_x + 6, y_sig_lo), (curr_x + 6, y_sig_hi)]
        curr_x += 22.5
    x_pre_end = curr_x

    # Кадровий синхроімпульс з зубцями (Serrated VSYNC)
    x_vsync_start = curr_x
    for _ in range(4):
        pts_sig += [(curr_x, y_sig_lo), (curr_x + 165 / 4 - 6, y_sig_lo), (curr_x + 165 / 4 - 6, y_sig_hi), (curr_x + 165 / 4, y_sig_hi)]
        curr_x += 165 / 4
    x_vsync_end = curr_x

    # 5 пост-урівнювальних
    for _ in range(4):
        pts_sig += [(curr_x, y_sig_hi), (curr_x, y_sig_lo), (curr_x + 6, y_sig_lo), (curr_x + 6, y_sig_hi)]
        curr_x += 22.5

    pts_sig.append((x1, y_sig_hi))
    parts.append(polyline(pts_sig, color=POS, sw=2.2))

    # Вихід RC-інтегратора
    pts_int = [(x0, y_int_0)]
    n_pts = 60
    for i in range(n_pts):
        t = i / n_pts
        cx = x0 + (x_vsync_start - x0) * t
        cy = y_int_0 - 4 * (1.0 if (i % 4 == 0) else 0.0)
        pts_int.append((cx, cy))

    n_vsync = 50
    x_trigger = x_vsync_start + 85
    for i in range(n_vsync):
        t = i / n_vsync
        cx = x_vsync_start + (x_vsync_end - x_vsync_start) * t
        val = 1.0 - math.exp(-3.2 * t)
        cy = y_int_0 - val * (y_int_0 - y_int_max)
        pts_int.append((cx, cy))

    n_post = 30
    for i in range(n_post):
        t = i / n_post
        cx = x_vsync_end + (x1 - x_vsync_end) * t
        val = (1.0 - math.exp(-3.2)) * math.exp(-4.0 * t)
        cy = y_int_0 - val * (y_int_0 - y_int_max)
        pts_int.append((cx, cy))

    parts.append(polyline(pts_int, color=FIELD, sw=2.6))

    # Точка тригера VSYNC
    parts.append(circle(x_trigger, y_thresh, 5, fill=NEG, stroke=INK, sw=1.5))
    parts.append(line(x_trigger, y_thresh, x_trigger, y_sig_hi - 15, color=NEG, sw=1.2, dash="3,3"))
    parts.append(text(x_trigger, y_sig_hi - 20, "момент V-тригера", size=10, color=NEG, bold=True))

    parts += [
        text((x_pre_start + x_pre_end) / 2, y_sig_hi - 22, "пре-урівнювальні", size=9, color=MUTED),
        text((x_vsync_start + x_vsync_end) / 2, y_sig_lo + 22, "кадровий синхро з зубцями (2f_H)", size=10, color=POS, bold=True),
        text(x1 - 40, H - 15, "час →", size=11, color=MUTED),
    ]

    render(os.path.join(IMG, "serrated-vsync.svg"), W, H, *parts)


# ── фіг. 3: артефакти Interline Twitter та Combing (Гребінка) ────────────────
def fig_twitter_combing():
    W, H = 780, 360
    w_panel, h_panel = 320, 220
    oy = 75
    lx, rx = 50, 410

    parts = []

    # Панель 1: Interline Twitter
    parts += [
        rect(lx, oy, w_panel, h_panel, fill=BG, stroke=LINE, sw=1.8),
        text(lx + w_panel / 2, oy - 14, "1. Interline Twitter (твіттер)", size=13, color=FIELD, bold=True),
    ]
    rows = 10
    for r in range(rows):
        y = oy + (r + 0.5) * h_panel / rows
        is_odd = (r % 2 == 0)
        c = FIELD if is_odd else MUTED
        parts.append(line(lx + 20, y, lx + w_panel - 20, y, color=c, sw=1.2, dash="2,2" if not is_odd else None))

    y_line = oy + (3 + 0.5) * h_panel / rows
    parts.append(line(lx + 40, y_line, lx + w_panel - 40, y_line, color=NEG, sw=4))
    parts.append(text(lx + w_panel / 2, y_line - 10, "тонка детальна лінія (1 піксель)", size=10, color=NEG, bold=True))

    parts += [
        text(lx + w_panel / 2, oy + h_panel + 24, "Лінія є у Полі 1, але відсутня у Полі 2", size=11, color=MUTED),
        text(lx + w_panel / 2, oy + h_panel + 40, "Результат: миготіння з частотою 25/30 Гц", size=11, color=FIELD, bold=True),
    ]

    # Панель 2: Combing (Гребінка при русі)
    parts += [
        rect(rx, oy, w_panel, h_panel, fill=BG, stroke=LINE, sw=1.8),
        text(rx + w_panel / 2, oy - 14, "2. Combing (гребінка при русі)", size=13, color=POS, bold=True),
    ]

    x_field1 = rx + 80
    x_field2 = rx + 140
    rect_w = 90

    for r in range(rows):
        y = oy + (r + 0.5) * h_panel / rows
        is_odd = (r % 2 == 0)
        if 2 <= r <= 7:
            x_pos = x_field1 if is_odd else x_field2
            c = FIELD if is_odd else POS
            parts.append(line(x_pos, y, x_pos + rect_w, y, color=c, sw=6))

    parts += [
        text(rx + w_panel / 2, oy + h_panel + 24, "Поле 1 (t) та Поле 2 (t+20 мкс) зсунуті", size=11, color=MUTED),
        text(rx + w_panel / 2, oy + h_panel + 40, "Зібчастий край рухомого об'єкта", size=11, color=POS, bold=True),
    ]

    render(os.path.join(IMG, "twitter-combing.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_fields_raster()
    fig_serrated_vsync()
    fig_twitter_combing()
    print("SVG figures generated successfully in ./img/")
