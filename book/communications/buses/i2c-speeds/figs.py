# -*- coding: utf-8 -*-
"""Фігури до теми «Режими швидкості I2C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Фізика RC-заряджання проти активного спадання ────────────────────────
def fig_rc_charging():
    W, H = 840, 380
    f = [text(W / 2, 28, "Асиметрія фронтів I2C: активний спад проти пасивного RC-наростання", size=15, bold=True)]

    # Координатна сітка
    x0, y0, gw, gh = 80, 70, 680, 220
    f.append(rect(x0, y0, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Рівні напруги
    y_vdd = y0 + 20
    y_vih = y0 + gh * 0.30     # 0.7 VDD = 2.31V
    y_vil = y0 + gh * 0.70     # 0.3 VDD = 0.99V
    y_vol = y0 + gh * 0.88     # 0.4V
    y_gnd = y0 + gh - 10

    f.append(line(x0, y_vdd, x0 + gw, y_vdd, color="#c0392b", sw=1.2, dash="4,4"))
    f.append(text(x0 - 8, y_vdd + 4, "VDD (3.3V)", size=11, color="#c0392b", anchor="end", bold=True))

    f.append(line(x0, y_vih, x0 + gw, y_vih, color="#27ae60", sw=1.2, dash="3,3"))
    f.append(text(x0 - 8, y_vih + 4, "VIH = 0.7 VDD", size=11, color="#27ae60", anchor="end", bold=True))

    f.append(line(x0, y_vil, x0 + gw, y_vil, color="#2457d6", sw=1.2, dash="3,3"))
    f.append(text(x0 - 8, y_vil + 4, "VIL = 0.3 VDD", size=11, color="#2457d6", anchor="end", bold=True))

    f.append(line(x0, y_vol, x0 + gw, y_vol, color="#e67e22", sw=1.0, dash="2,2"))
    f.append(text(x0 - 8, y_vol + 4, "VOL = 0.4V", size=10, color="#e67e22", anchor="end"))

    # Крива 1: Активний спад (Low-side MOSFET, швидкий спад tf < 20 ns)
    f.append(line(x0 + 40, y_vdd, x0 + 110, y_vdd, color="#1a1a1a", sw=2.5))
    # Спад
    f.append(line(x0 + 110, y_vdd, x0 + 125, y_vol, color="#e67e22", sw=2.8))
    f.append(line(x0 + 125, y_vol, x0 + 200, y_vol, color="#1a1a1a", sw=2.5))

    # Крива 2: Оптимальна підтяжка Rp = 2.2 kOm (Fm, tr = 260 ns)
    # Експоненційне наростання
    pts_fast = []
    for i in range(30):
        t = i / 29.0
        x = x0 + 200 + t * 140
        # Експонента: v(t) = vol + (vdd - vol) * (1 - exp(-3.0 * t))
        v_norm = 1.0 - math.exp(-3.2 * t)
        y = y_vol - v_norm * (y_vol - y_vdd)
        pts_fast.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_fast)}" fill="none" stroke="#27ae60" stroke-width="2.5"/>')
    f.append(line(x0 + 340, y_vdd, x0 + 410, y_vdd, color="#27ae60", sw=2.5))

    # Крива 3: Завелика підтяжка Rp = 10 kOm (Затягнутий фронт, tr > 1000 ns — зрив таймінгу)
    pts_slow = []
    for i in range(50):
        t = i / 49.0
        x = x0 + 410 + t * 240
        v_norm = 1.0 - math.exp(-1.1 * t)
        y = y_vol - v_norm * (y_vol - y_vdd)
        pts_slow.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_slow)}" fill="none" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="5,4"/>')

    # Позначки часових інтервалів tr
    # tr оптимальне
    f.append(line(x0 + 225, y_vil, x0 + 225, y0 + gh + 18, color="#27ae60", sw=1.0, dash="2,2"))
    f.append(line(x0 + 300, y_vih, x0 + 300, y0 + gh + 18, color="#27ae60", sw=1.0, dash="2,2"))
    f.append(line(x0 + 225, y0 + gh + 14, x0 + 300, y0 + gh + 14, color="#27ae60", sw=1.4))
    f.append(text(x0 + 262, y0 + gh + 28, "tr (норма ≤ 300 нс)", size=10.5, color="#27ae60", bold=True))

    # Спад tf
    f.append(text(x0 + 120, y0 + 36, "Активне спадання (tf)", size=10.5, color="#e67e22", bold=True))

    # Пояснювальні підписи
    f.append(text(x0 + 285, y_vih - 18, "Rp = 2.2 кОм (Fm)", size=11, color="#27ae60", bold=True))
    f.append(text(x0 + 530, y_vih + 24, "Rp = 10 кОм (деформація фронту)", size=11, color="#c0392b", bold=True))

    b = fitbox(60, H - 54, W - 120, 42,
               ["Активний транзистор відкривається миттєво (спад tf < 20 нс), але заряджання ємності шини",
                "відбувається пасивно через резистор Rp (наростання tr між 0.3 VDD та 0.7 VDD експоненційне)."],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "rc-charging.svg"), W, H, *f)


# ── 2. Еволюція швидкісних режимів I2C ───────────────────────────────────────
def fig_modes_evolution():
    W, H = 880, 390
    f = [text(W / 2, 28, "Специфікація швидкісних режимів I2C: таймінги, ємність та вихідні каскади", size=15, bold=True)]

    headers = ["Режим", "Швидкість", "Макс. Cb", "Макс. tr", "I_OL (VOL=0.4V)", "Тип виходу", "Фільтр сплесків"]
    modes = [
        ("Standard-mode (Sm)", "100 кбіт/с", "400 пФ", "1000 нс", "3 мА", "Open-Drain", "Не регламентовано"),
        ("Fast-mode (Fm)", "400 кбіт/с", "400 пФ", "300 нс", "3 мА", "Open-Drain", "≤ 50 нс (аналоговий)"),
        ("Fast-mode Plus (Fm+)", "1 Мбіт/с", "550 пФ", "120 нс", "20 мА", "Open-Drain (посилений)", "≤ 50 нс (аналог/цифра)"),
        ("High-speed mode (Hs)", "3.4 Мбіт/с", "100 / 400 пФ", "40 / 80 нс", "Active Pull-up", "Push-Pull SCL / RTA", "≤ 10 нс (перемикний)"),
        ("Ultra Fast-mode (UFm)", "5 Мбіт/с", "Push-Pull Cb", "20 нс", "Push-Pull CMOS", "Push-Pull (односпрям.)", "Немає (без зворотного)")
    ]

    # Таблиця
    col_w = [170, 95, 95, 85, 115, 175, 125]
    x_start = 10
    y_start = 55
    row_h = 42

    # Заголовок таблиці
    cx = x_start
    for i, (h, w) in enumerate(zip(headers, col_w)):
        f.append(rect(cx, y_start, w, 32, fill="#e9eefb", stroke="#2457d6", sw=1.2, rx=4))
        f.append(text(cx + w / 2, y_start + 20, h, size=11, bold=True, color="#2457d6"))
        cx += w + 3

    # Рядки
    colors = ["#f8fafc", "#eef6ef", "#fef9e7", "#fbecec", "#f4ecfb"]
    borders = ["#d0d7de", "#27ae60", "#f39c12", "#c0392b", "#8e44ad"]

    for r_idx, row in enumerate(modes):
        ry = y_start + 38 + r_idx * (row_h + 6)
        cx = x_start
        bg_col = colors[r_idx]
        b_col = borders[r_idx]
        for c_idx, (val, w) in enumerate(zip(row, col_w)):
            f.append(rect(cx, ry, w, row_h, fill=bg_col, stroke=b_col, sw=1.1, rx=4))
            f_size = 11 if c_idx == 0 else 10.5
            is_b = (c_idx <= 1)
            t_col = INK if c_idx > 1 else b_col
            f.append(text(cx + w / 2, ry + row_h / 2 + 4, val, size=f_size, bold=is_b, color=t_col))
            cx += w + 3

    b = fitbox(40, H - 52, W - 80, 40,
               ["Зростання швидкості вимагало радикальної зміни схемотехніки: від посилення струму розряду (20 мА у Fm+)",
                "до активних генераторів струму підтяжки (Hs-mode) та повного переходу на Push-Pull (UFm)."],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "modes-evolution.svg"), W, H, *f)


# ── 3. Рукостискання та Master Code у High-speed mode ───────────────────────
def fig_hs_mode_handshake():
    W, H = 880, 360
    f = [text(W / 2, 28, "Вхід у High-speed mode (3.4 Мбіт/с): Master Code та перемикання фільтрів", size=15, bold=True)]

    y, h = 80, 60
    # Фаза 1: Fast-mode / Standard-mode
    f.append(rect(30, y - 22, 380, h + 50, fill="none", stroke="#2457d6", sw=1.4, rx=8))
    f.append(text(220, y - 30, "Фаза 1: Відкритий стік (Fm ≤ 400 кбіт/с, фільтр 50 нс)", size=11.5, bold=True, color="#2457d6"))

    p1 = [
        ("S", "СТАРТ", "#27ae60", "#eef6ef", 44),
        ("0000 1XXX", "Master Code (Fm)", "#2457d6", "#e9eefb", 120),
        ("NACK", "SDA високий", "#c0392b", "#fbecec", 80),
        ("Sr", "Повторний старт", "#27ae60", "#eef6ef", 96)
    ]
    x = 42
    for lab, sub, col, fill, w in p1:
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.5, rx=5))
        f.append(text(x + w / 2, y + 26, lab, size=11.5, bold=True, color=col))
        f.append(text(x + w / 2, y + 46, sub, size=9.5, color=MUTED))
        x += w + 8

    # Стрілка перемикання фільтрів
    f.append(arrow(x + 4, y + h / 2, x + 36, y + h / 2, color="#e67e22", sw=2.2))
    f.append(text(x + 20, y - 8, "Перемикання", size=10, bold=True, color="#e67e22"))
    f.append(text(x + 20, y + h + 18, "50 нс → 10 нс", size=10, bold=True, color="#e67e22"))

    # Фаза 2: High-speed mode
    x_hs = x + 44
    f.append(rect(x_hs - 8, y - 22, 396, h + 50, fill="none", stroke="#c0392b", sw=1.4, rx=8))
    f.append(text(x_hs + 190, y - 30, "Фаза 2: Hs-mode (до 3.4 Мбіт/с, Push-Pull / Active Pull-up)", size=11.5, bold=True, color="#c0392b"))

    p2 = [
        ("Slave Addr", "Адреса веденого", "#8e44ad", "#f4ecfb", 96),
        ("ACK", "Відгук Hs", "#27ae60", "#eef6ef", 64),
        ("Data Byte", "Hs-дані (3.4M)", "#c0392b", "#fbecec", 96),
        ("ACK", "", "#27ae60", "#eef6ef", 54),
        ("P", "СТОП", "#27ae60", "#eef6ef", 44)
    ]
    x = x_hs
    for lab, sub, col, fill, w in p2:
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.5, rx=5))
        f.append(text(x + w / 2, y + 26, lab, size=11.5, bold=True, color=col))
        if sub:
            f.append(text(x + w / 2, y + 46, sub, size=9.5, color=MUTED))
        x += w + 8

    # Нижня стрілка повернення до Fm
    f.append(line(x - 30, y + h + 34, 50, y + h + 34, color="#6b7280", sw=1.2, dash="4,4"))
    f.append(text(W / 2, y + h + 48, "Сигнал СТОП (P) скидає всі пристрої назад у режим Fm/Sm", size=11, italic=True, color=MUTED))

    b = fitbox(40, H - 56, W - 80, 44,
               ["Ведучий транслює Master Code (0000 1XXX) на стандартній швидкості Fm. Hs-сумісні ведені",
                "вимикають 50-нс фільтр завад (вмикають 10-нс) і переходять на 3.4 Мбіт/с після повторного старту (Sr)."],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "hs-mode-handshake.svg"), W, H, *f)


# ── 4. Схемотехніка та робота Rise Time Accelerator (RTA) ───────────────────
def fig_active_accelerator():
    W, H = 840, 360
    f = [text(W / 2, 28, "Принцип роботи активного прискорювача фронту (Rise Time Accelerator)", size=15, bold=True)]

    # Схема зліва
    sx, sy, sw, sh = 60, 65, 340, 215
    f.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke="#2457d6", sw=1.4, rx=8))
    f.append(text(sx + sw / 2, sy + 22, "Апаратний прискорювач (RTA)", size=13, bold=True, color="#2457d6"))

    # Живлення VDD
    f.append(line(sx + 170, sy + 40, sx + 170, sy + 65, color="#c0392b", sw=2.0))
    f.append(text(sx + 170, sy + 36, "VDD", size=11, bold=True, color="#c0392b"))

    # PMOS ключ
    f.append(rect(sx + 140, sy + 65, 60, 36, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=4))
    f.append(text(sx + 170, sy + 88, "PMOS", size=11, bold=True, color="#c0392b"))

    # Компаратор швидкості наростання dV/dt
    f.append(rect(sx + 40, sy + 120, 110, 50, fill="#eef6ef", stroke="#27ae60", sw=1.4, rx=4))
    f.append(text(sx + 95, sy + 142, "Детектор dV/dt", size=11, bold=True, color="#27ae60"))
    f.append(text(sx + 95, sy + 158, "і порогу VIL", size=10, color=MUTED))

    # Зв'язки
    f.append(line(sx + 95, sy + 120, sx + 95, sy + 83, color="#27ae60", sw=1.4))
    f.append(arrow(sx + 95, sy + 83, sx + 140, sy + 83, color="#27ae60", sw=1.4))

    # Вихід на шину
    f.append(line(sx + 170, sy + 101, sx + 170, sy + 180, color="#1a1a1a", sw=2.0))
    f.append(line(sx + 170, sy + 180, sx + sw - 20, sy + 180, color="#1a1a1a", sw=2.0))
    f.append(arrow(sx + 95, sy + 180, sx + 95, sy + 170, color="#27ae60", sw=1.4))
    f.append(circle(sx + 95, sy + 180, 3.5, fill="#1a1a1a", stroke="#1a1a1a"))

    f.append(text(sx + sw - 12, sy + 184, "SDA / SCL", size=11.5, bold=True, anchor="start"))
    f.append(text(sx + 235, sy + 140, "Імпульс струму", size=10.5, color="#c0392b", bold=True))
    f.append(text(sx + 235, sy + 156, "10–20 мА (30 нс)", size=10, color=MUTED))

    # Осцилограма справа
    ox, oy, ow, oh = 440, 65, 340, 215
    f.append(rect(ox, oy, ow, oh, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=6))
    f.append(text(ox + ow / 2, oy + 22, "Форма сигналу з прискорювачем", size=13, bold=True))

    # Рівні
    f.append(line(ox + 20, oy + 70, ox + ow - 20, oy + 70, color="#27ae60", sw=1.0, dash="3,3"))
    f.append(text(ox + ow - 15, oy + 74, "VIH", size=10, color="#27ae60", anchor="start"))

    f.append(line(ox + 20, oy + 140, ox + ow - 20, oy + 140, color="#2457d6", sw=1.0, dash="3,3"))
    f.append(text(ox + ow - 15, oy + 144, "VIL", size=10, color="#2457d6", anchor="start"))

    # Траєкторія сигналу: пасивний старт -> прискорення -> пасивне дотягування
    f.append(line(ox + 30, oy + 180, ox + 80, oy + 180, color="#1a1a1a", sw=2.2))
    # Початок наростання до VIL
    f.append(line(ox + 80, oy + 180, ox + 115, oy + 140, color="#2457d6", sw=2.2))
    # Активний буст (крутий вертикальний фронт)
    f.append(line(ox + 115, oy + 140, ox + 145, oy + 70, color="#c0392b", sw=3.0))
    # Пасивне утримання
    f.append(line(ox + 145, oy + 70, ox + 180, oy + 50, color="#27ae60", sw=2.0))
    f.append(line(ox + 180, oy + 50, ox + 290, oy + 50, color="#1a1a1a", sw=2.2))

    # Стрілки фаз
    f.append(text(ox + 85, oy + 168, "Пасивно", size=9.5, color="#2457d6"))
    f.append(text(ox + 175, oy + 105, "Буст RTA!", size=11, bold=True, color="#c0392b"))
    f.append(text(ox + 230, oy + 42, "Утримання VDD", size=9.5, color="#27ae60"))

    b = fitbox(40, H - 56, W - 80, 44,
               ["Детектор фіксує перетин порогу VIL і вмикає потужний PMOS-генератор струму на ~30 нс.",
                "Лінія миттєво долає ємність до рівня VIH, після чого прискорювач вимикається без статичних втрат."],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "active-accelerator.svg"), W, H, *f)


if __name__ == '__main__':
    import math
    fig_rc_charging()
    fig_modes_evolution()
    fig_hs_mode_handshake()
    fig_active_accelerator()
    print("Всі 4 фігури успішно згенеровано у ./img/")
