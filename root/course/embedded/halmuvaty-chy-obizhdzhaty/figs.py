# -*- coding: utf-8 -*-
"""Фігури теми «Гальмувати чи об'їжджати: реактивний шар проти планувальника»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)

def vec(x1, y1, x2, y2, color, sw=2.0, hl=8.0, hw=4.0):
    """Стрілка з кольоровим трикутним вістрям."""
    ang = math.atan2(y2 - y1, x2 - x1)
    bx = x2 - hl * math.cos(ang)
    by = y2 - hl * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    p1 = (bx + hw * px, by + hw * py)
    p2 = (bx - hw * px, by - hw * py)
    s = line(x1, y1, bx, by, color=color, sw=sw)
    s += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
          % (x2, y2, p1[0], p1[1], p2[0], p2[1], color))
    return s


# ── 1) two-time-scales.svg — два часові масштаби керування ──────────────────
def fig_two_time_scales():
    W, H = 760, 430
    frags = [
        text(W / 2, 24, "Два часові масштаби рішень: планувальник і реактивний шар", size=15, bold=True)
    ]

    # ── Верхній блок: Повільний глобальний планувальник (1-10 Гц) ──
    px, py, pw, ph = 40, 46, 680, 110
    frags.append(rect(px, py, pw, ph, fill="#f4f7fb", stroke=NEG, sw=1.6, rx=6))
    frags.append(text(px + 16, py + 22, "ПОВІЛЬНИЙ ШАР (ПЛАНУВАЛЬНИК ТРАЄКТОРІЇ) — 1–10 Гц (T = 100–1000 мс)",
                      size=12, color=NEG, anchor="start", bold=True))
    frags.append(text(px + 16, py + 48, "• Вхід: карта зайнятості (OctoMap / Costmap 2.5D), глобальна місія, цільові вейпойнти",
                      size=11, color=INK, anchor="start"))
    frags.append(text(px + 16, py + 68, "• Алгоритми: A*, D* Lite, RRT*, TEB / MPC оптимізація сплайнів з урахуванням динаміки",
                      size=11, color=INK, anchor="start"))
    frags.append(text(px + 16, py + 88, "• Мета: глобальна оптимальність, енергоефективність, гладкість кривини траєкторії",
                      size=11, color=MUTED, anchor="start"))

    # Стрілка вниз від планувальника: бажаний вектор / сплайн
    frags.append(vec(240, py + ph, 240, py + ph + 34, NEG, sw=2.2))
    frags.append(text(310, py + ph + 22, "v_plan (плановий намір)", size=10.5, color=NEG, anchor="middle", italic=True))

    # Стрілка вгору до планувальника: оновлення карти та відстеження фактичного стану
    frags.append(vec(520, py + ph + 34, 520, py + ph, MUTED, sw=1.6))
    frags.append(text(595, py + ph + 22, "стан / карта перешкод", size=10.5, color=MUTED, anchor="middle", italic=True))

    # ── Середній блок: Арбітр та змішувач безпеки ──
    ax, ay, aw, ah = 40, 196, 680, 56
    frags.append(rect(ax, ay, aw, ah, fill="#fdfbf7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(W / 2, ay + 22, "АРБІТР БЕЗПЕКИ ТА БЕЗУДАРНИЙ ЗМІШУВАЧ ШВИДКОСТЕЙ",
                      size=12, color="#b45309", anchor="middle", bold=True))
    frags.append(text(W / 2, ay + 42, "Вибір зони: Спостереження (план) → Застереження (змішування) → Екстрений стоп (Override)",
                      size=11, color=INK, anchor="middle"))

    # Стрілка вниз від реактивного шару до арбітра
    frags.append(vec(240, 310, 240, ay + ah + 6, POS, sw=2.2))
    frags.append(text(310, 280, "v_react (вектор ухиляння)", size=10.5, color=POS, anchor="middle", italic=True))

    # Стрілка від арбітра вниз до приводів (праворуч від центру)
    frags.append(vec(520, ay + ah, 520, 376, FIELD, sw=2.4))
    frags.append(text(595, 280, "v_cmd (фінальна уставка)", size=10.5, color=FIELD, anchor="middle", bold=True))

    # ── Нижній блок: Швидкий реактивний шар (50-200 Гц) ──
    rx, ry, rw, rh = 40, 310, 380, 106
    frags.append(rect(rx, ry, rw, rh, fill="#fff5f5", stroke=POS, sw=1.6, rx=6))
    frags.append(text(rx + 14, ry + 20, "ШВИДКИЙ РЕАКТИВНИЙ ШАР — 50–200 Гц",
                      size=12, color=POS, anchor="start", bold=True))
    frags.append(text(rx + 14, ry + 42, "• Вхід: сирі промені ToF / лідара / сонара", size=11, color=INK, anchor="start"))
    frags.append(text(rx + 14, ry + 62, "• Алгоритми: TTC, VFH+, потенційні сили", size=11, color=INK, anchor="start"))
    frags.append(text(rx + 14, ry + 82, "• Мета: негайне збереження цілісності тіла", size=11, color=MUTED, anchor="start"))

    # Блок виконавчих приводів
    mx, my, mw, mh = 450, 310, 270, 106
    frags.append(rect(mx, my, mw, mh, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(mx + 14, my + 20, "ВИКОНАВЧІ ПРИВОДИ — 200–400 Гц",
                      size=12, color=FIELD, anchor="start", bold=True))
    frags.append(text(mx + 14, my + 42, "• Контури струму, швидкості, кута", size=11, color=INK, anchor="start"))
    frags.append(text(mx + 14, my + 62, "• ESC мотори, кермові сервоприводи", size=11, color=INK, anchor="start"))
    frags.append(text(mx + 14, my + 82, "• Обмеження прискорення та джерку", size=11, color=MUTED, anchor="start"))

    render(out("two-time-scales.svg"), W, H, *frags)


# ── 2) layer-conflicts.svg — три архетипи конфлікту між шарами ───────────────
def fig_layer_conflicts():
    W, H = 760, 320
    frags = [
        text(W / 2, 22, "Три типові конфлікти між реактивним ухилянням і планувальником", size=15, bold=True)
    ]

    pw = 226
    ph = 260
    gap = 14
    start_x = 24
    top_y = 44

    # ── Панель 1: Локальний мінімум у U-подібній пастці ──
    x1 = start_x
    frags.append(rect(x1, top_y, pw, ph, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(x1 + pw / 2, top_y + 20, "1. Пастка глухого кута", size=12, color=POS, bold=True))
    frags.append(text(x1 + pw / 2, top_y + 36, "F_att + Σ F_rep = 0", size=11, color=MUTED, italic=True))

    # U-подібна перешкода
    frags.append(rect(x1 + 40, top_y + 60, 14, 90, fill="#e2e8f0", stroke="#64748b", sw=1.4))
    frags.append(rect(x1 + 40, top_y + 136, 146, 14, fill="#e2e8f0", stroke="#64748b", sw=1.4))
    frags.append(rect(x1 + 172, top_y + 60, 14, 90, fill="#e2e8f0", stroke="#64748b", sw=1.4))

    # Апарат усередині U
    ax1, ay1 = x1 + 113, top_y + 105
    frags.append(circle(ax1, ay1, 9, fill="#eaf0fd", stroke=NEG, sw=1.8))
    # Вектор цілі вперед
    frags.append(vec(ax1, ay1, ax1, ay1 + 26, NEG, sw=2.0))
    frags.append(text(ax1 + 22, ay1 + 20, "ціль ↓", size=10, color=NEG))
    # Вектори відштовхування від стін
    frags.append(vec(ax1, ay1, ax1, ay1 - 22, POS, sw=1.8))
    frags.append(vec(ax1, ay1, ax1 - 18, ay1, POS, sw=1.8))
    frags.append(vec(ax1, ay1, ax1 + 18, ay1, POS, sw=1.8))

    frags.append(text(x1 + pw / 2, top_y + 195, "Реактивний шар застрягає:", size=10.5, color=INK, bold=True))
    frags.append(text(x1 + pw / 2, top_y + 215, "сили врівноважилися,", size=10, color=MUTED))
    frags.append(text(x1 + pw / 2, top_y + 233, "апарат не бачить виходу назад", size=10, color=MUTED))

    # ── Панель 2: Осциляції та тремтіння (chattering) ──
    x2 = start_x + pw + gap
    frags.append(rect(x2, top_y, pw, ph, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(x2 + pw / 2, top_y + 20, "2. Осциляції та ривки", size=12, color=POS, bold=True))
    frags.append(text(x2 + pw / 2, top_y + 36, "Конфлікт пріоритетів", size=11, color=MUTED, italic=True))

    # Перешкода праворуч
    frags.append(rect(x2 + 140, top_y + 60, 60, 90, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    frags.append(text(x2 + 170, top_y + 105, "Стіна", size=11, color=POS))

    # Цільова лінія шляху (вертикальна штрихова)
    frags.append(line(x2 + 120, top_y + 55, x2 + 120, top_y + 175, color=NEG, sw=1.4, dash="4 3"))
    frags.append(text(x2 + 110, top_y + 58, "план", size=9.5, color=NEG, anchor="end"))

    # Зигзагоподібна траєкторія
    zig = [
        (x2 + 70, top_y + 165),
        (x2 + 110, top_y + 140),
        (x2 + 75, top_y + 115),
        (x2 + 105, top_y + 90),
        (x2 + 70, top_y + 65)
    ]
    for i in range(len(zig) - 1):
        frags.append(line(zig[i][0], zig[i][1], zig[i + 1][0], zig[i + 1][1], color="#f59e0b", sw=2.0))
        frags.append(circle(zig[i][0], zig[i][1], 3.0, fill="#f59e0b", stroke="#f59e0b", sw=0.5))

    frags.append(text(x2 + pw / 2, top_y + 195, "Битва двох регуляторів:", size=10.5, color=INK, bold=True))
    frags.append(text(x2 + pw / 2, top_y + 215, "план повертає до цілі →", size=10, color=MUTED))
    frags.append(text(x2 + pw / 2, top_y + 233, "← рефлекс б'є вбік від стіни", size=10, color=MUTED))

    # ── Панель 3: Затримка реакції та сліпий політ ──
    x3 = start_x + (pw + gap) * 2
    frags.append(rect(x3, top_y, pw, ph, fill="#fafafa", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(x3 + pw / 2, top_y + 20, "3. Затримка розрахунку", size=12, color=POS, bold=True))
    frags.append(text(x3 + pw / 2, top_y + 36, "T_plan = 500 мс, v = 15 м/с", size=11, color=MUTED, italic=True))

    # Апарат на початку
    ax3, ay3 = x3 + 35, top_y + 105
    frags.append(circle(ax3, ay3, 9, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(ax3, ay3 - 15, "t = 0", size=10, color=NEG))

    # Перешкода попереду
    ox3, oy3 = x3 + 180, top_y + 85
    frags.append(rect(ox3, oy3, 30, 40, fill="#fee2e2", stroke=POS, sw=1.4, rx=3))
    frags.append(text(ox3 + 15, oy3 + 24, "!", size=14, color=POS, bold=True))

    # Стрілка сліпого польоту
    frags.append(vec(ax3 + 12, ay3, ox3 - 22, ay3, POS, sw=2.2))
    frags.append(text(ax3 + 65, ay3 - 10, "Δx = 7.5 м", size=10.5, color=POS, bold=True))
    frags.append(text(ax3 + 65, ay3 + 16, "(сліпий проліт)", size=9.5, color=MUTED))

    frags.append(text(x3 + pw / 2, top_y + 195, "Планувальник запізнюється:", size=10.5, color=INK, bold=True))
    frags.append(text(x3 + pw / 2, top_y + 215, "поки граф рахується 500 мс,", size=10, color=MUTED))
    frags.append(text(x3 + pw / 2, top_y + 233, "апарат уже врізається в об'єкт", size=10, color=MUTED))

    render(out("layer-conflicts.svg"), W, H, *frags)


# ── 3) safety-zones-arbitration.svg — вкладені зони безпеки ──────────────────
def fig_safety_zones():
    W, H = 760, 360
    frags = [
        text(W / 2, 22, "Три вкладені зони безпеки та динамічний арбітраж", size=15, bold=True)
    ]

    # Центр апарата
    cx, cy = 190, 185

    # 1. Зовнішня зона: Спостереження (Зелена)
    r_obs = 155
    frags.append(circle(cx, cy, r_obs, fill="#f0fdf4", stroke=FIELD, sw=1.6))
    # 2. Середня зона: Застереження та змішування (Жовта)
    r_warn = 95
    frags.append(circle(cx, cy, r_warn, fill="#fffbeb", stroke="#f59e0b", sw=1.6))
    # 3. Внутрішня зона: Екстрений стоп (Червона)
    r_stop = 42
    frags.append(circle(cx, cy, r_stop, fill="#fee2e2", stroke=POS, sw=1.8))

    # Сам апарат у центрі
    frags.append(circle(cx, cy, 12, fill="#2457d6", stroke="#1e40af", sw=2.0))
    frags.append(vec(cx, cy, cx + 24, cy, "#ffffff", sw=2.0))
    frags.append(text(cx - 22, cy + 4, "робот", size=10.5, color=INK, anchor="end", bold=True))

    # Радіуси-мітки
    frags.append(line(cx, cy, cx + r_obs, cy, color=FIELD, sw=1.0, dash="3 3"))
    frags.append(text(cx + 125, cy - 8, "R_obs", size=10.5, color=FIELD, bold=True))
    frags.append(text(cx + 68, cy - 8, "R_warn", size=10.5, color="#d97706", bold=True))
    frags.append(text(cx + 25, cy - 14, "R_stop", size=10, color=POS, bold=True))

    # ── Права панель: опис режимів арбітражу ──
    rx, ry, rw = 380, 48, 345

    # Картка 1: Зона спостереження
    h1 = 80
    frags.append(rect(rx, ry, rw, h1, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=5))
    frags.append(text(rx + 12, ry + 20, "1. ЗОНА СПОСТЕРЕЖЕННЯ (d > R_warn)", size=11.5, color=FIELD, anchor="start", bold=True))
    frags.append(text(rx + 12, ry + 40, "• Режим: вільне слідування глобальному плану", size=10.5, color=INK, anchor="start"))
    frags.append(text(rx + 12, ry + 58, "• Дія: перешкоди йдуть у карту; перепланування на ходу", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(rx + 12, ry + 72, "• Керування: v_cmd = v_plan", size=10.5, color=FIELD, anchor="start", bold=True))

    # Картка 2: Зона застереження
    ry2 = ry + h1 + 12
    h2 = 98
    frags.append(rect(rx, ry2, rw, h2, fill="#fffbeb", stroke="#f59e0b", sw=1.4, rx=5))
    frags.append(text(rx + 12, ry2 + 20, "2. ЗОНА ЗАСТЕРЕЖЕННЯ (R_stop < d ≤ R_warn)", size=11.5, color="#d97706", anchor="start", bold=True))
    frags.append(text(rx + 12, ry2 + 40, "• Режим: плавне безударне змішування швидкостей", size=10.5, color=INK, anchor="start"))
    frags.append(text(rx + 12, ry2 + 58, "• Вага: α(d) = (R_warn - d) / (R_warn - R_stop)", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(rx + 12, ry2 + 76, "• Керування: v_cmd = (1-α)·v_plan + α·v_react", size=10.5, color="#b45309", anchor="start", bold=True))
    frags.append(text(rx + 12, ry2 + 92, "• Обмеження: v_max(d) = √(2·a_max·(d - R_stop))", size=10, color=MUTED, anchor="start"))

    # Картка 3: Зона екстреного стопу
    ry3 = ry2 + h2 + 12
    h3 = 80
    frags.append(rect(rx, ry3, rw, h3, fill="#fee2e2", stroke=POS, sw=1.4, rx=5))
    frags.append(text(rx + 12, ry3 + 20, "3. ЗОНА ЕКСТРЕНОГО СТОПУ (d ≤ R_stop)", size=11.5, color=POS, anchor="start", bold=True))
    frags.append(text(rx + 12, ry3 + 40, "• Режим: повний перехоплення керування (Safety Override)", size=10.5, color=INK, anchor="start"))
    frags.append(text(rx + 12, ry3 + 58, "• Дія: анулювання плану, гальмування з темпом a_max", size=10.5, color=MUTED, anchor="start"))
    frags.append(text(rx + 12, ry3 + 72, "• Керування: v_cmd = 0 (E-Stop Active)", size=10.5, color=POS, anchor="start", bold=True))

    render(out("safety-zones-arbitration.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_two_time_scales()
    fig_layer_conflicts()
    fig_safety_zones()
    print("All figures generated successfully.")
