# -*- coding: utf-8 -*-
"""Фігури до теми «Смуга пропускання».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. bandwidth-definitions.svg ─────────────────────────────────────────────
def fig_bandwidth_definitions():
    W, H = 790, 360
    path = os.path.join(IMG, 'bandwidth-definitions.svg')
    f = []

    x0, y0 = 70, 300
    w_axis, h_axis = 660, 240

    # Осі
    f.append(line(x0, y0, x0 + w_axis, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, x0, y0 - h_axis, color=INK, sw=1.6))
    f.append(text(x0 + w_axis - 10, y0 + 22, "Частота f (Гц)", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 + 10, y0 - h_axis - 10, "Потужність (дБ)", size=11, color=MUTED, anchor="start"))

    def psd_dB(x_rel):
        if abs(x_rel) < 1e-5:
            val = 1.0
        else:
            val = (math.sin(math.pi * x_rel) / (math.pi * x_rel)) ** 2
        val_lin = max(val, 0.0003)
        db = 10 * math.log10(val_lin)
        return max(db, -32.0)

    def map_xy(x_rel, db):
        px = x0 + 330 + x_rel * 105
        py = y0 - 10 - (db + 32) * (200 / 32)
        return px, py

    # 99% Зайнята смуга (OBW)
    pts_obw = [(map_xy(-0.95, -32)[0], y0)]
    N_obw = 60
    for i in range(N_obw + 1):
        xr = -0.95 + 1.9 * (i / N_obw)
        db = psd_dB(xr)
        pts_obw.append(map_xy(xr, db))
    pts_obw.append((map_xy(0.95, -32)[0], y0))
    poly_obw = " ".join("%.1f,%.1f" % p for p in pts_obw)
    f.append(f'<polygon points="{poly_obw}" fill="#dbeafe" fill-opacity="0.6" stroke="none"/>')

    # Лінія кривої спектра
    pts_curve = []
    N_curve = 200
    for i in range(N_curve + 1):
        xr = -2.7 + 5.4 * (i / N_curve)
        db = psd_dB(xr)
        pts_curve.append(map_xy(xr, db))
    poly_curve = " ".join("%.1f,%.1f" % p for p in pts_curve)
    f.append(f'<polyline points="{poly_curve}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Рівні дБ
    px_peak, py_peak = map_xy(0, 0)
    px_3db_l, py_3db_l = map_xy(-0.443, -3.01)
    px_3db_r, py_3db_r = map_xy(0.443, -3.01)

    # Лінія 0 дБ (пік)
    f.append(line(x0 - 5, py_peak, x0 + w_axis, py_peak, color=MUTED, sw=1, dash="4,4"))
    f.append(text(x0 + 10, py_peak + 14, "0 дБ (P_max)", size=10, color=INK, anchor="start"))

    # Лінія -3 дБ
    f.append(line(x0 - 5, py_3db_l, x0 + w_axis, py_3db_l, color=POS, sw=1.2, dash="4,4"))
    f.append(text(x0 + 10, py_3db_l + 14, "-3 дБ", size=10, color=POS, bold=True, anchor="start"))

    # Пунктири вниз від -3 дБ точок
    f.append(line(px_3db_l, py_3db_l, px_3db_l, y0, color=POS, sw=1, dash="3,3"))
    f.append(line(px_3db_r, py_3db_r, px_3db_r, y0, color=POS, sw=1, dash="3,3"))

    # Стрілка B_3dB
    y_arrow_3db = py_3db_l - 15
    f.append(line(px_3db_l, y_arrow_3db, px_3db_r, y_arrow_3db, color=POS, sw=1.8))
    f.append(line(px_3db_l, y_arrow_3db - 4, px_3db_l, y_arrow_3db + 4, color=POS, sw=1.8))
    f.append(line(px_3db_r, y_arrow_3db - 4, px_3db_r, y_arrow_3db + 4, color=POS, sw=1.8))
    f.append(text(x0 + 330, y_arrow_3db - 6, "B_3dB (смуга половинної потужності)", size=11, color=POS, bold=True))

    # Стрілка Нульова смуга (Null-to-Null)
    px_n_l, _ = map_xy(-1.0, -25)
    px_n_r, _ = map_xy(1.0, -25)
    y_arrow_nn = y0 - 30
    f.append(line(px_n_l, y_arrow_nn, px_n_r, y_arrow_nn, color=FIELD, sw=1.6))
    f.append(line(px_n_l, y_arrow_nn - 4, px_n_l, y_arrow_nn + 4, color=FIELD, sw=1.6))
    f.append(line(px_n_r, y_arrow_nn - 4, px_n_r, y_arrow_nn + 4, color=FIELD, sw=1.6))
    f.append(text(x0 + 330, y_arrow_nn - 6, "B_nn (нульова смуга: перші нулі)", size=11, color=FIELD, bold=True))

    # Позначка OBW 99%
    f.append(text(x0 + 330, y0 - 80, "99% OBW (зайнята смуга)", size=11, color=NEG, bold=True))
    f.append(text(x0 + 330, y0 - 64, "99% повної енергії сигналу", size=10, color=MUTED))

    # Мітки частот на осі X
    f.append(text(x0 + 330, y0 + 18, "f_0", size=11, color=INK, bold=True))
    f.append(text(px_3db_l, y0 + 18, "f_1", size=10, color=POS))
    f.append(text(px_3db_r, y0 + 18, "f_2", size=10, color=POS))
    f.append(text(px_n_l, y0 + 18, "f_0 - R_s", size=10, color=FIELD))
    f.append(text(px_n_r, y0 + 18, "f_0 + R_s", size=10, color=FIELD))

    render(path, W, H, *f, title="Визначення смуги пропускання на спектральній щільності потужності")


# ── 2. baseband-vs-passband.svg ───────────────────────────────────────────────
def fig_baseband_vs_passband():
    W, H = 790, 270
    path = os.path.join(IMG, 'baseband-vs-passband.svg')
    f = []

    # Верхній блок — Baseband
    y1 = 105
    f.append(text(80, y1 - 40, "Низькочастотна смуга (Baseband): centred around 0 Hz", size=12, color=INK, bold=True, anchor="start"))
    f.append(line(70, y1, 350, y1, color=INK, sw=1.6))
    f.append(line(70, y1, 70, y1 - 45, color=INK, sw=1.6))
    f.append(text(340, y1 + 14, "f (Гц)", size=10, color=MUTED, anchor="end"))

    # Спектр Baseband (0 .. B)
    pts_bb = [(70, y1)]
    for i in range(31):
        x_rel = i / 30.0
        val = math.cos(x_rel * math.pi / 2.2) ** 1.8
        pts_bb.append((70 + x_rel * 160, y1 - val * 38))
    pts_bb.append((70 + 160, y1))
    poly_bb = " ".join("%.1f,%.1f" % p for p in pts_bb)
    f.append(f'<polygon points="{poly_bb}" fill="#dcfce7" stroke="{FIELD}" stroke-width="1.8"/>')
    f.append(text(70, y1 + 14, "0 Гц", size=10, color=INK, bold=True))
    f.append(text(230, y1 + 14, "B", size=10, color=FIELD, bold=True))
    f.append(line(70, y1 - 48, 230, y1 - 48, color=FIELD, sw=1.4))
    f.append(text(150, y1 - 54, "Смуга B", size=11, color=FIELD, bold=True))

    # Нижній блок — Passband
    y2 = 220
    f.append(text(80, y2 - 40, "Смугова область (Passband): модульована несуча f_c", size=12, color=INK, bold=True, anchor="start"))
    f.append(line(370, y2, 750, y2, color=INK, sw=1.6))
    f.append(line(560, y2, 560, y2 - 45, color=INK, sw=1.2, dash="3,3"))
    f.append(text(740, y2 + 14, "f (Гц)", size=10, color=MUTED, anchor="end"))

    # Спектр Passband (f_c - B .. f_c + B)
    pts_pb = []
    for i in range(51):
        x_rel = (i - 25) / 25.0
        val = math.cos(x_rel * math.pi / 2.2) ** 1.8
        pts_pb.append((560 + x_rel * 120, y2 - val * 38))
    pts_pb.append((560 + 120, y2))
    pts_pb.insert(0, (560 - 120, y2))
    poly_pb = " ".join("%.1f,%.1f" % p for p in pts_pb)
    f.append(f'<polygon points="{poly_pb}" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.8"/>')
    f.append(text(560, y2 + 14, "f_c", size=10, color=INK, bold=True))
    f.append(text(440, y2 + 14, "f_c - B", size=10, color="#7c3aed"))
    f.append(text(680, y2 + 14, "f_c + B", size=10, color="#7c3aed"))
    f.append(line(440, y2 - 48, 680, y2 - 48, color="#7c3aed", sw=1.4))
    f.append(text(560, y2 - 54, "Смуга RF = 2B", size=11, color="#7c3aed", bold=True))

    # Стрілка перенесення частоти (модуляція)
    f.append(line(250, y1 - 10, 290, 135, color=NEG, sw=1.8))
    f.append(line(400, 165, 430, y2 - 25, color=NEG, sw=1.8))
    f.append(rect(290, 140, 110, 24, fill="#eff6ff", stroke=NEG, sw=1))
    f.append(text(345, 156, "Модуляція × cos(2π f_c t)", size=9, color=NEG, bold=True))

    render(path, W, H, *f, title="Низькочастотний спектр (Baseband) проти смугового (Passband)")


# ── 3. time-frequency-uncertainty.svg ─────────────────────────────────────────
def fig_time_frequency_uncertainty():
    W, H = 790, 280
    path = os.path.join(IMG, 'time-frequency-uncertainty.svg')
    f = []

    # Ліва частина — Довгий імпульс у часі -> Вузька смуга
    x_l = 200
    y_t1, y_f1 = 90, 210
    f.append(text(x_l, 48, "Широкий імпульс у часі (Δt велика)", size=12, color=INK, bold=True))

    # Часова область 1
    f.append(line(60, y_t1, 340, y_t1, color=INK, sw=1.4))
    f.append(rect(130, y_t1 - 32, 140, 32, fill="#e0f2fe", stroke="#0284c7", sw=1.6))
    f.append(line(130, y_t1 - 40, 270, y_t1 - 40, color="#0284c7", sw=1.2))
    f.append(text(200, y_t1 - 46, "Тривалість T_1", size=10, color="#0284c7", bold=True))

    # Частотна область 1
    f.append(line(60, y_f1, 340, y_f1, color=INK, sw=1.4))
    pts_s1 = []
    for i in range(41):
        xr = (i - 20) / 20.0
        val = math.cos(xr * math.pi / 2.1) ** 3
        pts_s1.append((200 + xr * 45, y_f1 - val * 35))
    pts_s1.append((200 + 45, y_f1))
    pts_s1.insert(0, (200 - 45, y_f1))
    poly_s1 = " ".join("%.1f,%.1f" % p for p in pts_s1)
    f.append(f'<polygon points="{poly_s1}" fill="#dcfce7" stroke="{FIELD}" stroke-width="1.6"/>')
    f.append(line(155, y_f1 - 40, 245, y_f1 - 40, color=FIELD, sw=1.2))
    f.append(text(200, y_f1 - 46, "Вузька смуга B_1 ≈ 1 / T_1", size=10, color=FIELD, bold=True))

    # Вертикальний розділювач
    f.append(line(400, 45, 400, 250, color=MUTED, sw=1, dash="4,4"))

    # Права частина — Короткий імпульс у часі -> Широка смуга
    x_r = 590
    f.append(text(x_r, 48, "Вузький імпульс у часі (Δt мала)", size=12, color=INK, bold=True))

    # Часова область 2
    f.append(line(450, y_t1, 730, y_t1, color=INK, sw=1.4))
    f.append(rect(565, y_t1 - 32, 50, 32, fill="#fee2e2", stroke=POS, sw=1.6))
    f.append(line(565, y_t1 - 40, 615, y_t1 - 40, color=POS, sw=1.2))
    f.append(text(590, y_t1 - 46, "Тривалість T_2", size=10, color=POS, bold=True))

    # Частотна область 2
    f.append(line(450, y_f1, 730, y_f1, color=INK, sw=1.4))
    pts_s2 = []
    for i in range(41):
        xr = (i - 20) / 20.0
        val = math.cos(xr * math.pi / 2.1) ** 1.2
        pts_s2.append((590 + xr * 110, y_f1 - val * 35))
    pts_s2.append((590 + 110, y_f1))
    pts_s2.insert(0, (590 - 110, y_f1))
    poly_s2 = " ".join("%.1f,%.1f" % p for p in pts_s2)
    f.append(f'<polygon points="{poly_s2}" fill="#fef3c7" stroke="#d97706" stroke-width="1.6"/>')
    f.append(line(480, y_f1 - 40, 700, y_f1 - 40, color="#d97706", sw=1.2))
    f.append(text(590, y_f1 - 46, "Широка смуга B_2 ≈ 1 / T_2", size=10, color="#d97706", bold=True))

    render(path, W, H, *f, title="Співвідношення між тривалістю сигналу в часі та його смугою в частоті")


if __name__ == '__main__':
    fig_bandwidth_definitions()
    fig_baseband_vs_passband()
    fig_time_frequency_uncertainty()
    print("SVG figures generated successfully in ./img/")
