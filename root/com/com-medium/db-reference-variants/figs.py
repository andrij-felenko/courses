# -*- coding: utf-8 -*-
"""Фігури до теми «Варіанти децибельних одиниць: dBm, dBi, dBc, dBHz».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

ACCENT = "#2457d6"
WAVE = "#c0392b"
GOOD = FIELD
BAD = POS
WARN = "#e67e22"

def draw_path(pts, stroke=MUTED, sw=1.5, fill="none"):
    p_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<path d="{p_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def draw_ellipse(cx, cy, rx, ry, fill="#fdf2e9", stroke=WARN, sw=2):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ── 1. Дерево класифікації децибельних одиниць ───────────────────────────────
def fig_family_tree():
    W, H = 820, 400
    f = [text(W / 2, 26, "Класифікація варіантів децибельних одиниць", size=16, bold=True)]

    # Корінь
    f.append(rect(W / 2 - 120, 48, 240, 36, fill="#f4f6f8", stroke=INK, sw=2, rx=6))
    f.append(text(W / 2, 70, "Децибел (dB): відношення", size=13, bold=True))

    # 4 гілки
    col_w = 180
    xs = [70 + i * 190 for i in range(4)]
    y_branch = 125

    branches = [
        ("Абсолютна потужність", "dBm (1 мВт)\ndBW (1 Вт)", ACCENT),
        ("Напруга / Поле", "dBu (0.775 В, 600 Ω)\ndBV (1 В)\ndBμV (1 мкВ)\ndBμV/m (1 мкВ/м)", FIELD),
        ("Антени (Спрямованість)", "dBi (ізотроп)\ndBd (диполь)\ndBi = dBd + 2.15", WARN),
        ("Відносні / Спектр", "dBc (відносно несучої)\ndBHz (у смузі 1 Гц)\ndBFS (цифрова шкала)", WAVE),
    ]

    for (x, (title_str, items, col)) in zip(xs, branches):
        # Лінія від кореня
        f.append(draw_path([(W / 2, 84), (W / 2, 105), (x + col_w / 2, 105), (x + col_w / 2, y_branch)], stroke=MUTED, sw=1.5, fill="none"))
        # Картка гілки
        f.append(rect(x, y_branch, col_w, 42, fill="#ffffff", stroke=col, sw=2, rx=6))
        f.append(text(x + col_w / 2, y_branch + 25, title_str, size=12, color=col, bold=True))

        # Вміст гілки
        f.append(rect(x, y_branch + 48, col_w, 195, fill="#fbfdff", stroke=col, sw=1, rx=6))
        f.append(mtext(x + col_w / 2, y_branch + 68, items, size=11, color=INK, lh=1.45))

    render(os.path.join(IMG, "db-family-tree.svg"), W, H, *f)


# ── 2. Шкала абсолютних рівнів потужності та напруги ─────────────────────────
def fig_power_vs_voltage():
    W, H = 840, 400
    f = [text(W / 2, 26, "Шкала абсолютних рівнів: від кіловата до піковата", size=16, bold=True)]

    ox = 60
    oy = 280
    lw = 720

    # Головна лінійка
    f.append(line(ox, oy, ox + lw, oy, color=INK, sw=3))

    ticks = [
        (0.00, "-140 dBm", "10⁻¹⁷ Вт\nШум/GPS", MUTED, False),
        (0.18, "-100 dBm", "0.1 пВт\nLoRa чутливість", FIELD, True),
        (0.35, "-60 dBm", "1 нВт\nСлабкий Wi-Fi", FIELD, False),
        (0.52, "0 dBm", "1 мВт (0.775 В / 600 Ω)\nОпорна точка", ACCENT, True),
        (0.68, "+20 dBm", "100 мВт\nWi-Fi TX", WARN, False),
        (0.84, "+40 dBm", "10 Вт (+10 dBW)\nБаза LTE", WAVE, True),
        (1.00, "+60 dBm", "1 кВт (+30 dBW)\nРадар/Супутник", WAVE, False),
    ]

    for idx, (rel_x, db_lbl, desc, col, is_staggered) in enumerate(ticks):
        x = ox + rel_x * lw
        f.append(line(x, oy - 12, x, oy + 12, color=col, sw=2.5))
        f.append(text(x, oy - 22, db_lbl, size=12, color=col, bold=True))
        
        y_desc = oy + 70 if is_staggered else oy + 30
        if is_staggered:
            f.append(line(x, oy + 12, x, oy + 55, color=col, sw=1, dash="2,2"))
        
        f.append(mtext(x, y_desc, desc, size=10, color=INK, lh=1.35))

    # Висновок у рамці
    f.append(fitbox(ox, 50, lw, 60,
                    "dBm має опорну точку 1 мВт. Зміна на +10 dBm збільшує потужність у 10 разів, а на +30 dBm — у 1000 разів.\n1 Вт = +30 dBm = 0 dBW. Всі рівні нижче 1 мВт мають від'ємний знак у dBm.",
                    size=11, fill="#f4f6f8", stroke=ACCENT, color=INK))

    render(os.path.join(IMG, "power-vs-voltage-ref.svg"), W, H, *f)


# ── 3. Опорні антенні одиниці: dBi проти dBd ──────────────────────────────────
def fig_dbi_vs_dbd():
    W, H = 760, 340
    f = [text(W / 2, 26, "Опорні одиниці підсилення антен: dBi проти dBd", size=16, bold=True)]

    # Ліва частина: Ізотропний випромінювач (0 dBi)
    cxL = 200
    cy = 190
    f.append(circle(cxL, cy, 65, fill="#eaf2ff", stroke=ACCENT, sw=2))
    f.append(circle(cxL, cy, 5, fill=WAVE, stroke=WAVE))
    f.append(text(cxL, cy - 80, "Ізотропний випромінювач", size=13, color=ACCENT, bold=True))
    f.append(text(cxL, cy + 85, "0 dBi (ідеальна сфера)", size=11, color=MUTED))
    f.append(text(cxL, cy + 102, "Випромінює однаково в 3D", size=10, color=MUTED))

    # Центр: зсув +2.15 дБ
    f.append(arrow(310, cy, 420, cy, color=WARN, sw=2.5))
    f.append(text(365, cy - 14, "+2.15 dB", size=13, color=WARN, bold=True))
    f.append(text(365, cy + 18, "dBi = dBd + 2.15", size=11, color=INK, bold=True))

    # Права частина: Півхвильовий диполь (0 dBd = 2.15 dBi)
    cxR = 560
    # "Бублик" / вісімка
    f.append(draw_ellipse(cxR, cy, 95, 60, fill="#fdf2e9", stroke=WARN, sw=2))
    # Дріт диполя
    f.append(line(cxR, cy - 45, cxR, cy + 45, color=INK, sw=4))
    f.append(circle(cxR, cy, 4, fill=WAVE, stroke=WAVE))
    f.append(text(cxR, cy - 80, "Півхвильовий диполь", size=13, color=WARN, bold=True))
    f.append(text(cxR, cy + 85, "0 dBd = 2.15 dBi", size=11, color=MUTED))
    f.append(text(cxR, cy + 102, "Спрямовує енергію в бік", size=10, color=MUTED))

    render(os.path.join(IMG, "dbi-vs-dbd.svg"), W, H, *f)


# ── 4. Відносні спектральні одиниці: dBc ──────────────────────────────────────
def fig_dbc_spurious_noise():
    W, H = 760, 360
    f = [text(W / 2, 26, "Спектральні вимірювання в dBc: несуча як точка відліку", size=16, bold=True)]

    ox = 80
    oy = 310
    sw_w = 600
    sh_h = 220

    # Грати спектроаналізатора
    f.append(rect(ox, oy - sh_h, sw_w, sh_h, fill="#0d1117", stroke=MUTED, sw=1.5))
    for i in range(1, 5):
        f.append(line(ox, oy - i * (sh_h / 5), ox + sw_w, oy - i * (sh_h / 5), color="#21262d", sw=1))
    for i in range(1, 8):
        f.append(line(ox + i * (sw_w / 8), oy, ox + i * (sw_w / 8), oy - sh_h, color="#21262d", sw=1))

    # Спектральна лінія (несуча + гармоніка + завада + шум)
    pts = [
        (ox, oy - 25), (ox + 120, oy - 25),
        (ox + 180, oy - 200), (ox + 200, oy - 200), (ox + 260, oy - 25), # Несуча Peak
        (ox + 340, oy - 25),
        (ox + 380, oy - 110), (ox + 390, oy - 110), (ox + 400, oy - 25), # Гармоніка (-40 dBc)
        (ox + 470, oy - 25),
        (ox + 490, oy - 70), (ox + 495, oy - 70), (ox + 500, oy - 25),   # Спур (-65 dBc)
        (ox + sw_w, oy - 25)
    ]
    f.append(draw_path(pts, stroke="#3fb950", sw=2))

    # Відліки
    # 0 dBc на вершині несучої
    f.append(line(ox + 140, oy - 200, ox + 250, oy - 200, color=ACCENT, sw=1.5, dash="3,3"))
    f.append(text(ox + 190, oy - 212, "Несуча (Carrier): 0 dBc", size=11, color="#58a6ff", bold=True))

    # Рівень гармоніки -40 dBc
    f.append(arrow(ox + 395, oy - 200, ox + 395, oy - 110, color=WARN, sw=1.8))
    f.append(text(ox + 410, oy - 155, "-40 dBc (Гармоніка)", size=11, color=WARN, bold=True, anchor="start"))

    # Рівень спуру -65 dBc
    f.append(arrow(ox + 495, oy - 200, ox + 495, oy - 70, color=WAVE, sw=1.8))
    f.append(text(ox + 510, oy - 130, "-65 dBc (Побічна завада)", size=11, color=WAVE, bold=True, anchor="start"))

    # Фазовий шум на відбудові
    f.append(text(ox + 280, oy - 50, "Фазовий шум: -110 dBc/Hz", size=10, color="#d2a8ff", bold=True))

    render(os.path.join(IMG, "dbc-spurious-noise.svg"), W, H, *f)


# ── 5. Цифровий децибел dBFS у АЦП / ЦАП ──────────────────────────────────────
def fig_dbfs_digital_clip():
    W, H = 760, 340
    f = [text(W / 2, 26, "Цифрова шкала dBFS: 0 dBFS як абсолютна стеля", size=16, bold=True)]

    ox = 100
    oy = 70
    bh = 220
    bw = 240

    # Шкала dBFS
    f.append(rect(ox, oy, bw, bh, fill="#f8f9fa", stroke=INK, sw=2, rx=4))

    # Лінія 0 dBFS (Кліпінг)
    f.append(line(ox, oy, ox + bw, oy, color=WAVE, sw=3.5))
    f.append(text(ox + bw + 15, oy + 5, "0 dBFS — Стеля (Clipping!)", size=12, color=WAVE, bold=True, anchor="start"))

    # Сигнал піковий -6 dBFS
    y_p6 = oy + (6 / 96) * bh
    f.append(line(ox, y_p6, ox + bw, y_p6, color=WARN, sw=2, dash="4,4"))
    f.append(text(ox + bw + 15, y_p6 + 4, "-6 dBFS — Запас (Headroom)", size=11, color=WARN, bold=True, anchor="start"))

    # Номінальний рівень -18 dBFS
    y_n18 = oy + (18 / 96) * bh
    f.append(line(ox, y_n18, ox + bw, y_n18, color=FIELD, sw=2))
    f.append(text(ox + bw + 15, y_n18 + 4, "-18 dBFS — Робочий рівень", size=11, color=FIELD, bold=True, anchor="start"))

    # Заповнення робочого сигналу
    f.append(rect(ox + 40, y_n18, 160, bh - (y_n18 - oy), fill="#e6f4ea", stroke=FIELD, sw=1.5))

    # Дно шуму -96 dBFS
    f.append(line(ox, oy + bh, ox + bw, oy + bh, color=MUTED, sw=2))
    f.append(text(ox + bw + 15, oy + bh + 4, "-96 dBFS — Дно шуму (16 біт АЦП)", size=11, color=MUTED, bold=True, anchor="start"))

    # Пояснювальна картка
    f.append(fitbox(460, 160, 260, 130,
                    "У цифрових системах (SDR, DSP, Audio) всі значення dBFS від'ємні.\n0 dBFS відповідає максимальному числу відліку АЦП.\nПеревищення 0 dBFS спричиняє спотворення (цифрове зрізання сигналу).",
                    size=11, fill="#f4f6f8", stroke=ACCENT, color=INK))

    render(os.path.join(IMG, "dbfs-digital-clip.svg"), W, H, *f)


if __name__ == "__main__":
    fig_family_tree()
    fig_power_vs_voltage()
    fig_dbi_vs_dbd()
    fig_dbc_spurious_noise()
    fig_dbfs_digital_clip()
    print("OK: 5 figures ->", IMG)
