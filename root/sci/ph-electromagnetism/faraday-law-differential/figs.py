# -*- coding: utf-8 -*-
"""Фігури для теми «Закон Фарадея у диференціальній формі» (book/physics/electromagnetism/faraday-law-differential)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_vortex_electric_field():
    """vortex-electric-field.svg: Замкнені силові лінії вихрового електричного поля навколо області змінного магнітного поля."""
    W, H = 820, 480
    frags = []

    # Фон
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Заголовок
    frags.append(text(W / 2, 36, "Вихрове електричне поле E навколо зростаючого магнітного поля B", size=16, bold=True, color="#1e293b"))

    # Центральна область змінного магнітного поля (соленоїд у перерізі)
    cx, cy = 290, 235
    r_sol = 80

    frags.append(circle(cx, cy, r_sol, fill="#e6fffa", stroke="#0d9488", sw=2))
    frags.append(text(cx, cy - 35, "Область поля B", size=13, bold=True, color="#0d9488"))
    frags.append(text(cx, cy - 15, "dB/dt > 0 (направлене до нас ⊙)", size=11.5, color="#0d9488"))

    # Позначки точок магнітного поля (⊙ - до нас)
    dots_pos = [(-35, 15), (0, 15), (35, 15), (-20, 40), (20, 40)]
    for dx, dy in dots_pos:
        frags.append(circle(cx + dx, cy + dy, 9, fill="#ffffff", stroke="#0d9488", sw=1.5))
        frags.append(circle(cx + dx, cy + dy, 2.5, fill="#0d9488", stroke="#0d9488", sw=1))

    # Замкнені силові лінії вихрового електричного поля (концентричні кола)
    radii = [115, 145, 175]
    for r in radii:
        frags.append(circle(cx, cy, r, fill="none", stroke="#2563eb", sw=2))

    # Стрілки напрямку E (проти годинникової стрілки за законом Фарадея-Ленца)
    frags.append(line(cx, cy - 115, cx - 25, cy - 115, color="#2563eb", sw=2.5))
    frags.append(line(cx + 115, cy, cx + 115, cy - 25, color="#2563eb", sw=2.5))
    frags.append(line(cx, cy + 115, cx + 25, cy + 115, color="#2563eb", sw=2.5))
    frags.append(line(cx - 115, cy, cx - 115, cy + 25, color="#2563eb", sw=2.5))

    frags.append(line(cx, cy - 145, cx - 25, cy - 145, color="#2563eb", sw=2.5))
    frags.append(line(cx + 145, cy, cx + 145, cy - 25, color="#2563eb", sw=2.5))

    # Інформаційна панель праворуч
    px, py = 540, 110
    b1, _, _ = textbox(px + 100, py + 30, "Закон Фарадея у точці:\n∇ × E = − ∂B/∂t", size=14, bold=True, fill="#fff6e5", stroke="#e08a1e", pad=12)
    frags.append(b1)

    b2, _, _ = textbox(px + 100, py + 140, "Особливості вихрового поля E:\n• Силові лінії замкнені самі на себе\n• Не має джерел (зарядів): ∇ · E = 0\n• Циркуляція ∮ E · dl ≠ 0\n• Потенціал φ ввести неможливо", size=12, fill="#f8fafc", stroke="#64748b", pad=12)
    frags.append(b2)

    # Підпис знизу
    frags.append(text(W / 2, 452, "Зміна магнітного поля dB/dt у центрі породжує вихрове електричне поле E з ротором ∇ × E ≠ 0", size=12, italic=True, color="#475569"))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (W, H)]
    out.extend(frags)
    out.append('</svg>')
    with open(os.path.join(IMG, "vortex-electric-field.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def fig_stokes_infinitesimal_loop():
    """stokes-infinitesimal-loop.svg: Доведення закону Фарадея: перехід від макроскопічного контуру до ротора у точці через теорему Стокса."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 36, "Застосування теореми Стокса: від циркуляції до ротора", size=16, bold=True, color="#1e293b"))

    # Поверхня S з макро-контуром (ліворуч)
    sx, sy = 240, 240
    sw_w, sw_h = 320, 240
    frags.append(rect(sx - sw_w / 2, sy - sw_h / 2, sw_w, sw_h, fill="#f3e8ff", stroke="#7e22ce", sw=2, rx=20))
    frags.append(text(sx, sy - 95, "Макроскопічна поверхня S", size=13, bold=True, color="#7e22ce"))
    frags.append(text(sx, sy + 105, "Контур межі ∂S (циркуляція ∮ E · dl)", size=12, bold=True, color="#7e22ce"))

    # Сітка елементарних комірок ΔS_i
    rows, cols = 4, 5
    cw, ch = 50, 40
    start_x, start_y = sx - (cols * cw) / 2, sy - (rows * ch) / 2
    for r in range(rows):
        for c in range(cols):
            x0 = start_x + c * cw
            y0 = start_y + r * ch
            frags.append(rect(x0, y0, cw, ch, fill="#ffffff", stroke="#a855f7", sw=1))

            # Внутрішні протилежні стрілочки скасування на межах комірок
            if c < cols - 1:
                frags.append(line(x0 + cw, y0 + 10, x0 + cw, y0 + 30, color="#dc2626", sw=1.5))
                frags.append(line(x0 + cw + 3, y0 + 30, x0 + cw + 3, y0 + 10, color="#2563eb", sw=1.5))

    # Виділена мікро-комірка
    hx, hy = start_x + 2 * cw, start_y + 1 * ch
    frags.append(rect(hx, hy, cw, ch, fill="#fff6e5", stroke="#e08a1e", sw=2.5))
    frags.append(text(hx + cw / 2, hy + ch / 2 + 4, "ΔSₖ", size=11, bold=True, color="#e08a1e"))

    # Виносне збільшення мікро-комірки (праворуч)
    zx, zy = 620, 230
    zw, zh = 180, 160
    frags.append(rect(zx - zw / 2, zy - zh / 2, zw, zh, fill="#fff6e5", stroke="#e08a1e", sw=2, rx=10))
    frags.append(line(hx + cw, hy + ch / 2, zx - zw / 2, zy, color="#e08a1e", sw=1.5, dash="4,4"))

    frags.append(text(zx, zy - 50, "Елементарна комірка ΔSₖ", size=13, bold=True, color="#e08a1e"))
    frags.append(text(zx, zy - 20, "Границя: ΔS → 0", size=11, color="#64748b"))

    # Стрілка ротора у точці
    frags.append(line(zx - 40, zy + 20, zx + 40, zy + 20, color="#2563eb", sw=2))
    frags.append(line(zx + 40, zy + 20, zx + 40, zy - 10, color="#2563eb", sw=2))
    frags.append(line(zx + 40, zy - 10, zx - 40, zy - 10, color="#2563eb", sw=2))
    frags.append(line(zx - 40, zy - 10, zx - 40, zy + 20, color="#2563eb", sw=2))

    frags.append(text(zx, zy + 50, "ротор (∇ × E) · n", size=12, bold=True, color="#2563eb"))

    # Формульне обґрунтування внизу
    b_eq, _, _ = textbox(W / 2, 415, "∮[∂S] E · dl = ∬[S] (∇ × E) · dA = − ∬[S] (∂B/∂t) · dA   ⇒   ∇ × E = − ∂B/∂t", size=13, bold=True, fill="#e9f7ef", stroke="#16a34a", pad=10)
    frags.append(b_eq)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (W, H)]
    out.extend(frags)
    out.append('</svg>')
    with open(os.path.join(IMG, "stokes-infinitesimal-loop.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def fig_potentials_decomposition():
    """potentials-decomposition.svg: Теорема Гельмгольца: розклад повного електричного поля на потенціальну та вихрову компоненти."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 36, "Розклад Гельмгольца: E = E_потенц + E_вихр = −∇φ − ∂A/∂t", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Потенціальне (кулонівське) поле
    lx = 230
    frags.append(rect(30, 70, 370, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(lx, 95, "1. Потенціальна складова (E_потенц = −∇φ)", size=13, bold=True, color="#dc2626"))

    # Заряди
    frags.append(circle(lx - 80, 180, 18, fill="#fef2f2", stroke="#dc2626", sw=2))
    frags.append(text(lx - 80, 185, "+q", size=14, bold=True, color="#dc2626"))

    frags.append(circle(lx + 80, 180, 18, fill="#eaf0fd", stroke="#2563eb", sw=2))
    frags.append(text(lx + 80, 185, "−q", size=14, bold=True, color="#2563eb"))

    # Незамкнені силові лінії від + до -
    frags.append(line(lx - 60, 180, lx + 60, 180, color="#dc2626", sw=2))
    frags.append(line(lx - 60, 170, lx + 60, 140, color="#dc2626", sw=1.5))
    frags.append(line(lx - 60, 190, lx + 60, 220, color="#dc2626", sw=1.5))

    b_p, _, _ = textbox(lx, 310, "• Джерела: електричні заряди ρ\n• ∇ × E_потенц = 0 (безвихрове)\n• ∇ · E_потенц = ρ / ε₀\n• ∮ E · dl = 0 (консервативне)", size=11.5, fill="#ffffff", stroke="#dc2626", pad=10)
    frags.append(b_p)

    # Знак плюс між колонками
    frags.append(text(420, 230, "+", size=28, bold=True, color="#1e293b"))

    # Права колонка: Вихрове (індукційне) поле
    rx = 610
    frags.append(rect(440, 70, 370, 310, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(rx, 95, "2. Вихрова складова (E_вихр = −∂A/∂t)", size=13, bold=True, color="#2563eb"))

    # Змінний магнітний векторний потенціал A та замкнене поле E
    frags.append(circle(rx, 180, 45, fill="none", stroke="#2563eb", sw=2.5))
    frags.append(line(rx - 45, 180, rx - 45, 160, color="#2563eb", sw=2.5))

    frags.append(circle(rx, 180, 12, fill="#e6fffa", stroke="#0d9488", sw=1.5))
    frags.append(text(rx, 184, "A(t)", size=11, bold=True, color="#0d9488"))

    b_v, _, _ = textbox(rx, 310, "• Джерела: зміна поля ∂B/∂t чи ∂A/∂t\n• ∇ × E_вихр = − ∂B/∂t (вихрове)\n• ∇ · E_вихр = 0 (безджерельне)\n• ∮ E · dl ≠ 0 (неконсервативне)", size=11.5, fill="#ffffff", stroke="#2563eb", pad=10)
    frags.append(b_v)

    # Підпис внизу
    frags.append(text(W / 2, 425, "Повне електричне поле E у динаміці містить як кулонівську (джерельну), так і індукційну (вихрову) складові", size=12, italic=True, color="#475569"))

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (W, H)]
    out.extend(frags)
    out.append('</svg>')
    with open(os.path.join(IMG, "potentials-decomposition.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def fig_relativity_frame_transformation():
    """relativity-frame-transformation.svg: Релятивістська двоїстість індукції Фарадея та сили Лоренца у різних системах відліку."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W / 2, 36, "Релятивістська еквівалентність: індуковане поле E проти сили Лоренца v × B", size=16, bold=True, color="#1e293b"))

    # Система K (Нерухомий контур, змінне магнітне поле)
    k1_x = 220
    frags.append(rect(30, 70, 370, 310, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=10))
    frags.append(text(k1_x, 95, "Система K: Контур нерухомий, B(t) змінюється", size=13, bold=True, color="#7e22ce"))

    # Непорушний контур
    frags.append(rect(k1_x - 70, 140, 140, 90, fill="#ffffff", stroke="#7e22ce", sw=2, rx=6))
    frags.append(text(k1_x, 185, "Контур v = 0", size=12, color="#7e22ce"))

    # Поле B(t)
    frags.append(text(k1_x, 120, "dB/dt ≠ 0", size=12, bold=True, color="#0d9488"))

    b_k1, _, _ = textbox(k1_x, 305, "Пояснення у системі K:\nЗмінне магнітне поле створює вихрове\nелектричне поле: ∇ × E = − ∂B/∂t.\nСила на заряд: F = q · E", size=11.5, fill="#ffffff", stroke="#7e22ce", pad=10)
    frags.append(b_k1)

    # Система K' (Рухомий контур, постійне магнітне поле)
    k2_x = 620
    frags.append(rect(440, 70, 370, 310, fill="#fff6e5", stroke="#e08a1e", sw=1.5, rx=10))
    frags.append(text(k2_x, 95, "Система K': Контур рухається, B стаціонарне", size=13, bold=True, color="#e08a1e"))

    # Рухомий контур із вектором швидкості
    frags.append(rect(k2_x - 70, 140, 140, 90, fill="#ffffff", stroke="#e08a1e", sw=2, rx=6))
    frags.append(text(k2_x - 10, 185, "Контур", size=12, color="#e08a1e"))
    frags.append(line(k2_x + 20, 185, k2_x + 60, 185, color="#dc2626", sw=2.5))
    frags.append(text(k2_x + 40, 170, "v", size=12, bold=True, color="#dc2626"))

    # Поле B стале
    frags.append(text(k2_x, 120, "dB/dt = 0 (B стале)", size=12, bold=True, color="#0d9488"))

    b_k2, _, _ = textbox(k2_x, 305, "Пояснення у системі K':\nМагнітне поле стале, але на рухомі\nзаряди діє магнітна сила Лоренца.\nСила на заряд: F' = q · (v × B)", size=11.5, fill="#ffffff", stroke="#e08a1e", pad=10)
    frags.append(b_k2)

    # Релятивістське об'єднання внизу
    b_rel, _, _ = textbox(W / 2, 420, "Перетворення Лоренца: E' = E + v × B   — обидва описи є двома гранями єдиного тензора поля F_μν", size=12.5, bold=True, fill="#e9f7ef", stroke="#16a34a", pad=10)
    frags.append(b_rel)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" height="100%%">' % (W, H)]
    out.extend(frags)
    out.append('</svg>')
    with open(os.path.join(IMG, "relativity-frame-transformation.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    fig_vortex_electric_field()
    fig_stokes_infinitesimal_loop()
    fig_potentials_decomposition()
    fig_relativity_frame_transformation()
    print("Всі 4 фігури успішно згенеровано у folder img/")
