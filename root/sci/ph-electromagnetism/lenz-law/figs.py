# -*- coding: utf-8 -*-
"""Фігури до теми «Правило Ленца».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"
COLOR_GRAY = "#7f8c8d"

def ellipse(cx, cy, rx, ry, fill="none", stroke=LINE, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d}/>'


# ── Фігура 1: Приближення та віддалення магніту до замкненого витка ────────────
def fig_magnet_loop():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    midx = W / 2
    f.append(line(midx, 40, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- Ліва частина (А): Наближення N-полюса (потік збільшується) ---
    f.append(fitbox(20, 20, midx - 40, 28, "А: N-полюс наближається (ΔΦ/Δt > 0)", size=13, bold=True, color=COLOR_BLUE, fill="#eef6ff", stroke=COLOR_BLUE))

    # Магніт N-S рухається вниз
    mx1, my1 = 190, 80
    f.append(rect(mx1 - 25, my1, 50, 40, fill=COLOR_RED, stroke=COLOR_DARK, sw=1.5, rx=3))
    f.append(text(mx1, my1 + 25, "N", size=16, bold=True, color="#ffffff", anchor="middle"))
    f.append(rect(mx1 - 25, my1 - 40, 50, 40, fill=COLOR_BLUE, stroke=COLOR_DARK, sw=1.5, rx=3))
    f.append(text(mx1, my1 - 15, "S", size=16, bold=True, color="#ffffff", anchor="middle"))

    # Стрілка руху магніту (вниз)
    f.append(arrow(mx1 + 45, my1 - 10, mx1 + 45, my1 + 30, color=COLOR_RED, sw=2.5))
    f.append(text(mx1 + 53, my1 + 14, "v (вниз)", size=11, bold=True, color=COLOR_RED, anchor="start"))

    # Вектор зовнішнього поля B_ext (вниз)
    f.append(line(mx1 - 45, my1 - 20, mx1 - 45, my1 + 40, color=COLOR_PURPLE, sw=2.0, dash="4,3"))
    f.append(text(mx1 - 53, my1 + 14, "B_зовн", size=11, bold=True, color=COLOR_PURPLE, anchor="end"))

    # Провідне кільце (еліпс у перспективі)
    cy1 = 230
    f.append(ellipse(mx1, cy1, 80, 25, fill="none", stroke=COLOR_DARK, sw=3.5))

    # Індуковане поле B_ind (вгору — протидіє збільшенню потоку)
    f.append(arrow(mx1, cy1 - 5, mx1, cy1 - 75, color=COLOR_GREEN, sw=3.0))
    f.append(text(mx1 + 12, cy1 - 45, "B_інд (проти росту Φ)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    # Індукований струм I_ind (проти годинникової стрілки зверху)
    f.append(arrow(mx1 + 75, cy1, mx1 + 70, cy1 - 10, color=COLOR_ORANGE, sw=3.0))
    f.append(text(mx1 + 88, cy1 + 5, "I_інд", size=12, bold=True, color=COLOR_ORANGE, anchor="start"))

    # Текстова картка підсумку
    f.append(fitbox(20, 310, midx - 40, 85, "• Потік B_зовн зростає вниз\n• B_інд спрямоване ВГОРУ, щоб зменшити потік\n• Магніт відчуває ВІДШТОВХУВАННЯ (N проти N)", size=11, color=COLOR_DARK, fill="#f9f9f9", stroke="#cccccc"))

    # --- Права частина (Б): Віддалення N-полюса (потік зменшується) ---
    f.append(fitbox(midx + 20, 20, midx - 40, 28, "Б: N-полюс віддаляється (ΔΦ/Δt < 0)", size=13, bold=True, color=COLOR_RED, fill="#fdeea9", stroke=COLOR_ORANGE))

    # Магніт N-S рухається вгору
    mx2, my2 = midx + 190, 80
    f.append(rect(mx2 - 25, my2, 50, 40, fill=COLOR_RED, stroke=COLOR_DARK, sw=1.5, rx=3))
    f.append(text(mx2, my2 + 25, "N", size=16, bold=True, color="#ffffff", anchor="middle"))
    f.append(rect(mx2 - 25, my2 - 40, 50, 40, fill=COLOR_BLUE, stroke=COLOR_DARK, sw=1.5, rx=3))
    f.append(text(mx2, my2 - 15, "S", size=16, bold=True, color="#ffffff", anchor="middle"))

    # Стрілка руху магніту (вгору)
    f.append(arrow(mx2 + 45, my2 + 30, mx2 + 45, my2 - 10, color=COLOR_BLUE, sw=2.5))
    f.append(text(mx2 + 53, my2 + 14, "v (вгору)", size=11, bold=True, color=COLOR_BLUE, anchor="start"))

    # Вектор зовнішнього поля B_ext (вниз)
    f.append(line(mx2 - 45, my2 - 20, mx2 - 45, my2 + 40, color=COLOR_PURPLE, sw=2.0, dash="4,3"))
    f.append(text(mx2 - 53, my2 + 14, "B_зовн", size=11, bold=True, color=COLOR_PURPLE, anchor="end"))

    # Провідне кільце
    cy2 = 230
    f.append(ellipse(mx2, cy2, 80, 25, fill="none", stroke=COLOR_DARK, sw=3.5))

    # Індуковане поле B_ind (вниз — підтримує спадаючий потік)
    f.append(arrow(mx2, cy2 + 5, mx2, cy2 + 75, color=COLOR_GREEN, sw=3.0))
    f.append(text(mx2 + 12, cy2 + 45, "B_інд (підтримує Φ)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    # Індукований струм I_ind (за годинниковою стрілкою зверху)
    f.append(arrow(mx2 - 75, cy2, mx2 - 70, cy2 + 10, color=COLOR_ORANGE, sw=3.0))
    f.append(text(mx2 - 110, cy2 + 5, "I_інд", size=12, bold=True, color=COLOR_ORANGE, anchor="end"))

    # Текстова картка підсумку
    f.append(fitbox(midx + 20, 310, midx - 40, 85, "• Потік B_зовн зменшується вниз\n• B_інд спрямоване ВНИЗ, щоб підтримати потік\n• Магніт відчуває ПРИТЯГАННЯ (S проти N)", size=11, color=COLOR_DARK, fill="#f9f9f9", stroke="#cccccc"))

    render(os.path.join(IMG, "lenz-law-magnet-loop.svg"), W, H, *f, title="Правило Ленца: напрям індукованого поля при зміні магнітного потоку")


# ── Фігура 2: Збереження енергії vs парадокс перпетуум-мобіле ────────────────
def fig_energy_conservation():
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    midx = W / 2
    f.append(line(midx, 40, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- Ліва частина: Реальний закон (знак "мінус") ---
    f.append(fitbox(20, 20, midx - 40, 28, "Реальний фізичний світ (E = -dΦ/dt)", size=12, bold=True, color=COLOR_GREEN, fill="#eafaf1", stroke=COLOR_GREEN))

    # Схема енергетичного перетворення
    y0 = 70
    f.append(fitbox(30, y0, 300, 36, "1. Механічна робота зовні (F_рух · Δx)", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))
    f.append(arrow(180, y0 + 36, 180, y0 + 60, color=COLOR_DARK, sw=2.0))

    f.append(fitbox(30, y0 + 60, 300, 36, "2. Індукційна ЕРС та струм I_інд у витку", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))
    f.append(arrow(180, y0 + 96, 180, y0 + 120, color=COLOR_DARK, sw=2.0))

    f.append(fitbox(30, y0 + 120, 300, 36, "3. Гальмівна сила Ампера (F_гальм проти v)", size=11, bold=True, color=COLOR_RED, fill="#fcedec", stroke=COLOR_RED))
    f.append(arrow(180, y0 + 156, 180, y0 + 180, color=COLOR_DARK, sw=2.0))

    f.append(fitbox(30, y0 + 180, 300, 36, "4. Джоулеве тепло Q = I²·R·t (дисипація)", size=11, bold=True, color=COLOR_GREEN, fill="#e8f8f5", stroke=COLOR_GREEN))

    # --- Права частина: Гіпотетичний світ без мінуса (E = +dΦ/dt) ---
    f.append(fitbox(midx + 20, 20, midx - 40, 28, "Гіпотетична катастрофа (якби E = +dΦ/dt)", size=12, bold=True, color=COLOR_RED, fill="#fcedec", stroke=COLOR_RED))

    f.append(fitbox(midx + 30, y0, 300, 36, "1. Легкий поштовх магніту до витку", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))
    f.append(arrow(midx + 180, y0 + 36, midx + 180, y0 + 60, color=COLOR_RED, sw=2.0))

    f.append(fitbox(midx + 30, y0 + 60, 300, 36, "2. Струм створює ПРИТЯГАЛЬНЕ поле", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))
    f.append(arrow(midx + 180, y0 + 96, midx + 180, y0 + 120, color=COLOR_RED, sw=2.0))

    f.append(fitbox(midx + 30, y0 + 120, 300, 36, "3. Самоприскорення магніту (v → ∞)", size=11, bold=True, color=COLOR_RED, fill="#fdeea9", stroke=COLOR_ORANGE))
    f.append(arrow(midx + 180, y0 + 156, midx + 180, y0 + 180, color=COLOR_RED, sw=2.0))

    f.append(fitbox(midx + 30, y0 + 180, 300, 42, "4. Генерація нескінченної енергії з нічого!\n(ПОРУШЕННЯ ЗАКНУ ЗБЕРЕЖЕННЯ ЕНЕРГІЇ)", size=10, bold=True, color="#ffffff", fill=COLOR_RED, stroke=COLOR_RED))

    render(os.path.join(IMG, "lenz-law-energy-conservation.svg"), W, H, *f, title="Правило Ленца гарантує збереження енергії")


# ── Фігура 3: Вихрові струми (струми Фуко) та індукційне гальмування ─────────
def fig_eddy_current_braking():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    midx = W / 2
    f.append(line(midx, 40, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- Ліва частина: Суцільна пластина у магнітному полі ---
    f.append(fitbox(20, 20, midx - 40, 28, "Суцільна мідна пластина: Сильне гальмування", size=12, bold=True, color=COLOR_BLUE, fill="#eef6ff", stroke=COLOR_BLUE))

    # Зона магнітного поля (квадрат)
    bx1, by1 = 120, 80
    f.append(rect(bx1, by1, 120, 120, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5, rx=4))
    f.append(text(bx1 + 60, by1 + 20, "Поле B", size=11, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Хрестики поля B (від нас)
    for r in range(2):
        for c in range(3):
            cx = bx1 + 30 + c * 30
            cy = by1 + 55 + r * 35
            f.append(line(cx - 4, cy - 4, cx + 4, cy + 4, color=COLOR_GREEN, sw=1.4))
            f.append(line(cx - 4, cy + 4, cx + 4, cy - 4, color=COLOR_GREEN, sw=1.4))

    # Вихровий струм (замкнене кільце у пластині)
    f.append(ellipse(bx1 + 60, by1 + 75, 45, 30, fill="none", stroke=COLOR_ORANGE, sw=2.5, dash="6,3"))
    f.append(arrow(bx1 + 105, by1 + 75, bx1 + 105, by1 + 65, color=COLOR_ORANGE, sw=2.5))
    f.append(text(bx1 + 60, by1 + 78, "Струми Фуко", size=10, bold=True, color=COLOR_ORANGE, anchor="middle"))

    # Рух пластини (праворуч)
    f.append(arrow(bx1 + 140, by1 + 60, bx1 + 190, by1 + 60, color=COLOR_BLUE, sw=2.5))
    f.append(text(bx1 + 165, by1 + 48, "v (рух)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Сила гальмування Лоренца/Ампера (ліворуч)
    f.append(arrow(bx1 + 40, by1 + 60, bx1 - 20, by1 + 60, color=COLOR_RED, sw=3.0))
    f.append(text(bx1 + 10, by1 + 48, "F_гальм", size=12, bold=True, color=COLOR_RED, anchor="middle"))

    f.append(fitbox(20, 240, midx - 40, 90, "• Великі замкнені контури вихрових струмів\n• Малий електричний опір R → великий струм I\n• Потужне індукційне гальмування (F ~ σ·B²·v)", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))

    # --- Права частина: Розрізана пластина (гребінка) ---
    f.append(fitbox(midx + 20, 20, midx - 40, 28, "Розрізана пластина: Слабке гальмування", size=12, bold=True, color=COLOR_GREEN, fill="#eafaf1", stroke=COLOR_GREEN))

    # Зона магнітного поля
    bx2, by2 = midx + 120, 80
    f.append(rect(bx2, by2, 120, 120, fill="#e8f8f5", stroke=COLOR_GREEN, sw=1.5, rx=4))
    f.append(text(bx2 + 60, by2 + 20, "Поле B", size=11, bold=True, color=COLOR_GREEN, anchor="middle"))

    # Прорізи у пластині (вертикальні лінії розрізів)
    for i in range(4):
        sx = bx2 + 25 + i * 24
        f.append(line(sx, by2 + 35, sx, by2 + 110, color=BG, sw=4.0))
        f.append(line(sx, by2 + 35, sx, by2 + 110, color=COLOR_DARK, sw=1.0))

    # Дрібні вихрові струми у смужках
    for i in range(3):
        cx = bx2 + 37 + i * 24
        f.append(ellipse(cx, by2 + 75, 8, 20, fill="none", stroke=COLOR_ORANGE, sw=1.5))

    # Рух пластини (праворуч)
    f.append(arrow(bx2 + 140, by2 + 60, bx2 + 190, by2 + 60, color=COLOR_BLUE, sw=2.5))
    f.append(text(bx2 + 165, by2 + 48, "v (рух)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Мала сила гальмування
    f.append(arrow(bx2 + 40, by2 + 60, bx2 + 10, by2 + 60, color=COLOR_RED, sw=1.8))
    f.append(text(bx2 + 25, by2 + 48, "F_гальм", size=10, bold=True, color=COLOR_RED, anchor="middle"))

    f.append(fitbox(midx + 20, 240, midx - 40, 90, "• Прорізи розривають контури вихрових струмів\n• Високий опір вузьких смужок → малий струм I\n• Мінімальне гальмування (трансформаторне залізо)", size=11, color=COLOR_DARK, fill="#ffffff", stroke="#bdc3c7"))

    render(os.path.join(IMG, "lenz-law-eddy-current-braking.svg"), W, H, *f, title="Вихрові струми та зменшення гальмування прорізами")


if __name__ == '__main__':
    fig_magnet_loop()
    fig_energy_conservation()
    fig_eddy_current_braking()
    print("Фігури успішно створено!")
