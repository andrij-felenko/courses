# -*- coding: utf-8 -*-
"""Фігури до теми «Колірний простір YCbCr».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Трансформація колірного простору RGB у YCbCr ───────────────────────
def fig_ycbcr_cube():
    W, H = 760, 340
    f = [text(W / 2, 22, "Трансформація колірного простору RGB у геометрію YCbCr", size=15, bold=True)]

    # Ліва панель — Куб RGB
    f.append(rect(20, 45, 345, 275, fill="#f8fafc", stroke=MUTED, sw=1, rx=6))
    f.append(text(192, 68, "Простір RGB (Корельовані канали)", size=13, bold=True, color=INK))

    # Осі RGB
    ox, oy = 80, 260
    f.append(line(ox, oy, ox + 140, oy, color="#dc2626", sw=2))      # R-axis
    f.append(line(ox, oy, ox, oy - 140, color="#16a34a", sw=2))      # G-axis
    f.append(line(ox, oy, ox - 45, oy + 35, color="#2563eb", sw=2))  # B-axis

    f.append(text(ox + 155, oy + 4, "R (Червоний)", size=11, color="#dc2626", bold=True, anchor="start"))
    f.append(text(ox, oy - 148, "G (Зелений)", size=11, color="#16a34a", bold=True, anchor="middle"))
    f.append(text(ox - 52, oy + 48, "B (Синій)", size=11, color="#2563eb", bold=True, anchor="start"))

    # Грані куба RGB (аксонометрія)
    f.append(line(ox + 100, oy, ox + 100, oy - 100, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox, oy - 100, ox + 100, oy - 100, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox - 30, oy + 25, ox + 70, oy + 25, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox + 100, oy, ox + 70, oy + 25, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox - 30, oy + 25, ox - 30, oy - 75, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox, oy - 100, ox - 30, oy - 75, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox - 30, oy - 75, ox + 70, oy - 75, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox + 100, oy - 100, ox + 70, oy - 75, color=MUTED, sw=1, dash="3,3"))
    f.append(line(ox + 70, oy + 25, ox + 70, oy - 75, color=MUTED, sw=1, dash="3,3"))

    # Діагональ яркості Y
    f.append(line(ox, oy, ox + 70, oy - 75, color="#d97706", sw=2.5))
    f.append(circle(ox, oy, 4, fill="#000000", stroke=INK, sw=1))
    f.append(circle(ox + 70, oy - 75, 4, fill="#ffffff", stroke=INK, sw=1))
    f.append(text(ox - 8, oy + 15, "Чорний (0,0,0)", size=10, color=INK))
    f.append(text(ox + 75, oy - 82, "Білий (1,1,1)", size=10, color=INK, anchor="start"))

    f.append(text(192, 302, "Діагональ яркості Y збігається з векторним напрямком (1,1,1)", size=10, color=MUTED))

    # Стрілка перетворення
    f.append(arrow(373, 180, 392, 180, color=INK, sw=2))

    # Права панель — Система YCbCr
    f.append(rect(395, 45, 345, 275, fill="#f8fafc", stroke=MUTED, sw=1, rx=6))
    f.append(text(567, 68, "Простір YCbCr (Декорельовані канали)", size=13, bold=True, color=INK))

    cx, cy = 567, 210
    # Ось Y
    f.append(line(cx, cy + 45, cx, cy - 115, color="#d97706", sw=2.5))
    f.append(text(cx + 8, cy - 110, "Y' (Luma, 0..255)", size=11, color="#d97706", bold=True, anchor="start"))

    # Площина Cb-Cr
    f.append(line(cx - 100, cy, cx + 100, cy, color="#2563eb", sw=2))
    f.append(line(cx - 45, cy + 30, cx + 45, cy - 30, color="#dc2626", sw=2))

    f.append(text(cx + 105, cy + 4, "Cb (Chroma Blue)", size=11, color="#2563eb", bold=True, anchor="start"))
    f.append(text(cx - 50, cy + 42, "Cr (Chroma Red)", size=11, color="#dc2626", bold=True, anchor="end"))

    f.append(circle(cx, cy, 5, fill="#94a3b8", stroke=INK, sw=1))
    f.append(text(cx + 12, cy + 16, "Центр (Cb=128, Cr=128)", size=10, color=MUTED, anchor="start"))

    f.append(f'<ellipse cx="{cx}" cy="{cy}" rx="75" ry="32" fill="#3b82f6" fill-opacity="0.12" stroke="#2563eb" stroke-dasharray="4,3" stroke-width="1.5"/>')
    f.append(text(cx, cy - 40, "Площина хроматичності Cb-Cr", size=10, color=MUTED))

    f.append(text(567, 302, "Яскравість Y відокремлена від колірних різниць Cb та Cr", size=10, color=MUTED))

    render(os.path.join(IMG, 'ycbcr-cube.svg'), W, H, *f)


# ── 2. Конвеєр обробки колірного сигналу ──────────────────────────────────
def fig_ycbcr_pipeline():
    W, H = 780, 260
    f = [text(W / 2, 22, "Цифровий конвеєр обробки та квантування сигналу YCbCr", size=15, bold=True)]

    bx = 20
    bw = 130
    bh = 110
    by = 75
    gap = 24

    blocks = [
        ("Сенсор / RGB", "R, G, B\n(Лінійний світловий\nпотік)", "#fee2e2", "#ef4444"),
        ("Гама-корекція", "R', G', B'\n(Нелінійне RGB)", "#fef3c7", "#f59e0b"),
        ("Матриця YCbCr", "Y', Cb, Cr\n(BT.601 / BT.709\nBT.2020)", "#dcfce7", "#10b981"),
        ("Квантування", "Full (0-255) / \nLimited (16-235)\n8/10/12-біт", "#e0e7ff", "#6366f1"),
        ("Буфер пам'яті", "I420 / NV12 /\nYUYV\n(Chroma Subsampling)", "#f3e8ff", "#a855f7")
    ]

    for i, (title_str, desc_str, bg_col, stroke_col) in enumerate(blocks):
        x = bx + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        f.append(text(x + bw / 2, by + 24, title_str, size=12, bold=True, color=INK))
        f.append(line(x + 10, by + 34, x + bw - 10, by + 34, color=stroke_col, sw=1))
        f.append(mtext(x + bw / 2, by + 50, desc_str, size=10, color=INK))

        if i < len(blocks) - 1:
            ax1 = x + bw + 2
            ax2 = x + bw + gap - 2
            ay = by + bh / 2
            f.append(arrow(ax1, ay, ax2, ay, color=INK, sw=1.8))

    f.append(rect(20, 202, 740, 42, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    f.append(text(W / 2, 226, "Оптимізована обробка: відокремлена яскравість стискається без втрати чіткості деталей", size=11, color=INK, bold=True))

    render(os.path.join(IMG, 'ycbcr-pipeline.svg'), W, H, *f)


# ── 3. Full Range проти Limited Range ─────────────────────────────────────
def fig_range_quantization():
    W, H = 760, 300
    f = [text(W / 2, 22, "Порівняння рівнів квантування: Full Range проти Limited/Studio Range", size=15, bold=True)]

    # Верхня шкала: Full Range (0..255)
    f.append(text(40, 60, "Full Range (0..255) — ПК / JPEG / RGB", size=12, bold=True, anchor="start", color=INK))
    f.append(rect(40, 70, 680, 32, fill="#1e293b", stroke=INK, sw=1.5, rx=4))

    f.append(line(40, 70, 40, 102, color="#dc2626", sw=2))
    f.append(text(40, 118, "0 (Абсолютно чорний)", size=10, color="#dc2626", bold=True, anchor="start"))

    f.append(line(380, 70, 380, 102, color="#2563eb", sw=1.5, dash="3,3"))
    f.append(text(380, 118, "128 (Нейтральна колірність Cb/Cr)", size=10, color="#2563eb", anchor="middle"))

    f.append(line(720, 70, 720, 102, color="#dc2626", sw=2))
    f.append(text(720, 118, "255 (Абсолютно білий)", size=10, color="#dc2626", bold=True, anchor="end"))

    # Нижня шкала: Limited Range (16..235 для Y, 16..240 для Cb/Cr)
    f.append(text(40, 150, "Limited / Studio Range (16..235) — TV / BT.601 / BT.709 / HDMI", size=12, bold=True, anchor="start", color=INK))
    
    x_start = 40
    w_full = 680
    w_foot = w_full * (16 / 255)
    w_act = w_full * (219 / 255)
    w_head = w_full * (20 / 255)

    # Footroom box
    f.append(rect(x_start, 160, w_foot, 32, fill="#fee2e2", stroke="#ef4444", sw=1, rx=0))
    # Active range box
    f.append(rect(x_start + w_foot, 160, w_act, 32, fill="#dcfce7", stroke="#10b981", sw=1.5, rx=0))
    # Headroom box
    f.append(rect(x_start + w_foot + w_act, 160, w_head, 32, fill="#fee2e2", stroke="#ef4444", sw=1, rx=0))

    # Засічки та підписи Limited Range
    f.append(line(x_start, 160, x_start, 192, color=MUTED, sw=1.5))
    f.append(text(x_start, 208, "0", size=10, color=MUTED, anchor="middle"))

    f.append(line(x_start + w_foot, 160, x_start + w_foot, 192, color="#16a34a", sw=2))
    f.append(text(x_start + w_foot, 208, "16 (Чорний)", size=10, color="#16a34a", bold=True, anchor="middle"))

    # Розділені пунктирні лінії зверху і знизу від тексту у прямокутнику
    mid_x = x_start + w_foot + w_act / 2
    f.append(line(mid_x, 160, mid_x, 168, color="#2563eb", sw=1.5, dash="2,2"))
    f.append(line(mid_x, 184, mid_x, 192, color="#2563eb", sw=1.5, dash="2,2"))
    f.append(text(mid_x, 208, "128 (Центр Cb/Cr)", size=10, color="#2563eb", anchor="middle"))

    f.append(line(x_start + w_foot + w_act, 160, x_start + w_foot + w_act, 192, color="#16a34a", sw=2))
    f.append(text(x_start + w_foot + w_act, 208, "235 (Білий)", size=10, color="#16a34a", bold=True, anchor="middle"))

    f.append(line(x_start + w_full, 160, x_start + w_full, 192, color=MUTED, sw=1.5))
    f.append(text(x_start + w_full, 208, "255", size=10, color=MUTED, anchor="middle"))

    # Пояснення в блоках
    f.append(text(x_start + w_foot / 2, 180, "Foot", size=9, color="#991b1b", bold=True, anchor="middle"))
    f.append(text(mid_x, 178, "Робочий діапазон яркості Y (220 рівнів)", size=10, color="#166534", bold=True, anchor="middle"))
    f.append(text(x_start + w_foot + w_act + w_head / 2, 180, "Head", size=9, color="#991b1b", bold=True, anchor="middle"))

    # Нижня попереджувальна плашка про помилки неузгодження
    f.append(rect(40, 246, 680, 40, fill="#fffbe6", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(W / 2, 270, "Помилка узгодження: Limited джерело на Full дисплеї викликає тьмяний сірий колір замість чорного", size=11, color="#b45309", bold=True))

    render(os.path.join(IMG, 'range-quantization.svg'), W, H, *f)


if __name__ == '__main__':
    fig_ycbcr_cube()
    fig_ycbcr_pipeline()
    fig_range_quantization()
    print("SVG figures generated successfully in ./img/")
