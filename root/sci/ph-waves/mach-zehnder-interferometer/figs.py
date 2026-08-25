# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path(d, fill='none', stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Оптична схема інтерферометра Маха — Цендера
# ═══════════════════════════════════════════════════════════════════════════
def fig_mach_zehnder_scheme():
    W, H = 740, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Оптична схема інтерферометра Маха — Цендера', 16, INK, 'middle', bold=True))

    # Джерело світла (лазер)
    lx, ly = 40, 260
    f.append(rect(lx, ly - 22, 90, 44, fill='#fee2e2', stroke=POS, sw=1.8, rx=4))
    f.append(text(lx + 45, ly + 5, 'Лазер', 13, POS, 'middle', bold=True))

    # Координати елементів
    bs1_x, bs1_y = 200, 260
    m1_x, m1_y   = 200, 100
    m2_x, m2_y   = 520, 260
    bs2_x, bs2_y = 520, 100
    d1_x, d1_y   = 670, 100
    d2_x, d2_y   = 520, 30

    # Промені світла (червоні для лазерного випромінювання)
    # 1. Від лазера до BS1
    f.append(arrow(lx + 90, ly, bs1_x, bs1_y, color=POS, sw=2.5))
    f.append(text(145, ly - 8, 'E₀', 12, POS, 'middle', bold=True, italic=True))

    # 2. Плече A (верхнє): BS1 -> M1 -> BS2
    f.append(arrow(bs1_x, bs1_y, m1_x, m1_y, color=POS, sw=2.2))
    f.append(text(bs1_x - 14, 180, 'Плече A', 11, INK, 'end', bold=True))
    f.append(arrow(m1_x, m1_y, bs2_x, bs2_y, color=POS, sw=2.2))

    # 3. Плече B (нижнє): BS1 -> M2 -> BS2
    f.append(arrow(bs1_x, bs1_y, m2_x, m2_y, color=FIELD, sw=2.2))
    f.append(text(360, m2_y + 16, 'Плече B (еталон)', 11, FIELD, 'middle', bold=True))
    f.append(arrow(m2_x, m2_y, bs2_x, bs2_y, color=FIELD, sw=2.2))

    # 4. Виходи з BS2 до Детекторів D1 та D2
    f.append(arrow(bs2_x, bs2_y, d1_x, d1_y, color=POS, sw=2.5))
    f.append(text(600, d1_y - 8, 'Канал 1 (I₁)', 11, POS, 'middle', bold=True))

    f.append(arrow(bs2_x, bs2_y, d2_x, d2_y + 20, color=NEG, sw=2.5))
    f.append(text(d2_x + 14, 55, 'Канал 2 (I₂)', 11, NEG, 'start', bold=True))

    # Елементи оптики
    # Дзеркала M1 та M2 (похилі пластини під 45°)
    f.append(line(m1_x - 18, m1_y + 18, m1_x + 18, m1_y - 18, color=INK, sw=4))
    f.append(rect(m1_x - 22, m1_y - 25, 44, 14, fill=FILL, stroke=LINE, sw=1, rx=2))
    f.append(text(m1_x, m1_y - 14, 'Дзеркало M₁', 10, INK, 'middle', bold=True))

    f.append(line(m2_x - 18, m2_y + 18, m2_x + 18, m2_y - 18, color=INK, sw=4))
    f.append(rect(m2_x - 22, m2_y + 12, 44, 14, fill=FILL, stroke=LINE, sw=1, rx=2))
    f.append(text(m2_x, m2_y + 23, 'Дзеркало M₂', 10, INK, 'middle', bold=True))

    # Світлодільники BS1 та BS2 (напівпрозорі пластини)
    f.append(line(bs1_x - 20, bs1_y + 20, bs1_x + 20, bs1_y - 20, color=NEG, sw=3, dash='4,2'))
    f.append(rect(bs1_x - 25, bs1_y + 12, 50, 14, fill='#dbeafe', stroke=NEG, sw=1, rx=2))
    f.append(text(bs1_x, bs1_y + 23, 'Світлодільник BS₁', 10, NEG, 'middle', bold=True))

    f.append(line(bs2_x - 20, bs2_y + 20, bs2_x + 20, bs2_y - 20, color=NEG, sw=3, dash='4,2'))
    f.append(rect(bs2_x - 25, bs2_y + 12, 50, 14, fill='#dbeafe', stroke=NEG, sw=1, rx=2))
    f.append(text(bs2_x, bs2_y + 23, 'Світлодільник BS₂', 10, NEG, 'middle', bold=True))

    # Об'єкт дослідження в плечі A (кювета з газом / зразок)
    f.append(rect(300, m1_y - 20, 120, 40, fill='#fef3c7', stroke='#d97706', sw=1.5, rx=3))
    f.append(text(360, m1_y - 3, 'Досліджуване середовище', 11, '#b45309', 'middle', bold=True))
    f.append(text(360, m1_y + 12, 'зсув фази Δφ', 10, '#b45309', 'middle', italic=True))

    # Детектори D1 та D2
    f.append(rect(d1_x, d1_y - 20, 24, 40, fill='#1e293b', stroke='none', rx=3))
    f.append(text(d1_x + 12, d1_y + 35, 'Детектор D₁', 11, INK, 'middle', bold=True))

    f.append(rect(d2_x - 20, d2_y - 10, 40, 20, fill='#1e293b', stroke='none', rx=3))
    f.append(text(d2_x, d2_y - 15, 'Детектор D₂', 11, INK, 'middle', bold=True))

    # Інформаційна панель знизу
    f.append(fitbox(40, 340, 660, 75,
                    'Принцип роботи:\n1. BS₁ розщеплює промінь на дві незалежні вітки A та B.\n2. Досліджуваний об\'єкт змінює оптичний шлях n·L у плечі A, створюючи різницю фаз Δφ.\n3. BS₂ зводить пучки: на виході виникає інтерференція (D₁ та D₂ працюють у протифазі).',
                    size=11, color=INK, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'mach-zehnder-scheme.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Фазові співвідношення на напівпрозорому світлодільнику
# ═══════════════════════════════════════════════════════════════════════════
def fig_beam_splitter_phase():
    W, H = 680, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Фазові співвідношення на напівпрозорому світлодільнику', 16, INK, 'middle', bold=True))

    cx, cy = 240, 180
    # Світлодільна пластина з покриттям
    f.append(rect(cx - 10, cy - 100, 20, 200, fill='#e0f2fe', stroke='#0284c7', sw=1.5, rx=2))
    f.append(line(cx - 10, cy - 100, cx - 10, cy + 100, color=NEG, sw=3)) # Д діелектрична плівка

    f.append(text(cx - 20, cy - 80, 'Диелектричне', 10, NEG, 'end', bold=True))
    f.append(text(cx - 20, cy - 68, 'покриття', 10, NEG, 'end'))
    f.append(text(cx + 20, cy - 80, 'Скляна', 10, MUTED, 'start'))
    f.append(text(cx + 20, cy - 68, 'підкладка', 10, MUTED, 'start'))

    # Падаючі промені E1 та E2
    f.append(arrow(60, cy - 40, cx - 10, cy - 40, color=POS, sw=2.2))
    f.append(text(120, cy - 48, 'Падаючий пучок E₁', 11, POS, 'middle', bold=True))

    f.append(arrow(cx - 40, cy + 130, cx - 40, cy + 10, color=FIELD, sw=2.2))
    f.append(text(cx - 48, cy + 80, 'Падаючий пучок E₂', 11, FIELD, 'end', bold=True))

    # Вихідні промені
    # 1. Відбиття E1 від покриття (повітря -> покриття: зсув фази π)
    f.append(arrow(cx - 10, cy - 40, cx - 40, cy - 130, color=POS, sw=2))
    f.append(text(cx - 50, cy - 90, 'r₁·E₁ (зсув фази π)', 10, POS, 'end', bold=True))

    # 2. Проходження E1 (повітря -> скло: зсув 0 або π/2)
    f.append(arrow(cx + 10, cy - 40, 440, cy - 40, color=POS, sw=2))
    f.append(text(350, cy - 48, 't₁·E₁ (зсув фази 0)', 10, POS, 'middle', bold=True))

    # 3. Відбиття E2 усередині (скло -> покриття: зсув фази 0)
    f.append(arrow(cx + 10, cy + 10, 440, cy + 10, color=FIELD, sw=2))
    f.append(text(350, cy + 22, 'r₂·E₂ (зсув фази 0)', 10, FIELD, 'middle', bold=True))

    # Пояснювальна таблиця праворуч
    tx = 470
    f.append(rect(tx, 70, 190, 220, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    f.append(text(tx + 95, 92, 'Фазовий матричний зв\'язок', 11, INK, 'middle', bold=True))
    f.append(line(tx + 10, 102, tx + 180, 102, color=MUTED, sw=1))

    lines = [
        "Матриця світлодільника:",
        "M = 1/√2 · [ 1   i ]",
        "          [ i   1 ]",
        "",
        "Властивість унітарності:",
        "|r|² + |t|² = 1",
        "r·t* + t·r* = 0",
        "",
        "Різниця фаз між відбитим",
        "і пройденим променем",
        "завжди дорівнює Δθ = π/2."
    ]
    f.append(mtext(tx + 15, 122, lines, size=10, color=INK, anchor="start", lh=1.25))

    render(os.path.join(IMG, 'beam-splitter-phase.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Графік залежності інтенсивності від фазового зсуву Δφ
# ═══════════════════════════════════════════════════════════════════════════
def fig_intensity_curve():
    W, H = 700, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Залежність інтенсивностей світла I₁ та I₂ від різниці фаз Δφ', 16, INK, 'middle', bold=True))

    ox, oy = 90, 300
    gw, gh = 520, 230

    # Сітка та осі
    f.append(line(ox, oy - gh, ox, oy + 15, color=LINE, sw=1.5))
    f.append(line(ox - 15, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    f.append(text(ox - 12, oy - gh, 'Інтенсивність I', 11, INK, 'end', bold=True))
    f.append(text(ox + gw + 15, oy + 18, 'Δφ (рад)', 11, INK, 'start', bold=True))

    # Горизонтальні пунктири (I0 та I0/2)
    f.append(line(ox, oy - gh + 20, ox + gw, oy - gh + 20, color=MUTED, sw=1, dash='4,4'))
    f.append(text(ox - 10, oy - gh + 24, 'I₀', 11, INK, 'end', bold=True))

    f.append(line(ox, oy - gh / 2 - 5, ox + gw, oy - gh / 2 - 5, color=MUTED, sw=1, dash='4,4'))
    f.append(text(ox - 10, oy - gh / 2 - 1, 'I₀/2', 11, MUTED, 'end'))

    # Позначки фази на осі X (-π, -π/2, 0, π/2, π, 3π/2, 2π)
    ticks = [
        (-math.pi, '-π'),
        (-math.pi / 2, '-π/2'),
        (0, '0'),
        (math.pi / 2, 'π/2 (квадратура)'),
        (math.pi, 'π'),
        (3 * math.pi / 2, '3π/2'),
        (2 * math.pi, '2π')
    ]

    phi_min, phi_max = -math.pi, 2 * math.pi
    def map_x(phi):
        return ox + (phi - phi_min) / (phi_max - phi_min) * gw

    def map_y(val): # val in [0, 1]
        return oy - val * (gh - 40)

    for phi_val, label in ticks:
        x = map_x(phi_val)
        f.append(line(x, oy - 4, x, oy + 4, color=LINE, sw=1))
        if label != '0':
            f.append(text(x, oy + 18, label, 10, INK, 'middle'))
        else:
            f.append(text(x, oy + 18, '0', 10, INK, 'middle'))

    # Побудова точок для кривих
    # I1 = I0/2 * (1 + cos(phi))
    # I2 = I0/2 * (1 - cos(phi))
    pts1 = []
    pts2 = []
    N = 100
    for i in range(N + 1):
        phi = phi_min + i * (phi_max - phi_min) / N
        x = map_x(phi)
        y1 = map_y(0.5 * (1 + math.cos(phi)))
        y2 = map_y(0.5 * (1 - math.cos(phi)))
        pts1.append((x, y1))
        pts2.append((x, y2))

    # Крива I1 (червона)
    d1_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts1])
    f.append(path(d1_str, fill='none', stroke=POS, sw=2.5))

    # Крива I2 (синя)
    d2_str = "M " + " L ".join(["%.1f,%.1f" % p for p in pts2])
    f.append(path(d2_str, fill='none', stroke=NEG, sw=2.5, dash='6,3'))

    # Виділення робочої точки квадратури (π/2)
    qx = map_x(math.pi / 2)
    qy = map_y(0.5)
    f.append(circle(qx, qy, 6, fill='#f59e0b', stroke=INK, sw=1.5))
    f.append(line(qx, oy, qx, oy - gh + 20, color='#d97706', sw=1.2, dash='3,3'))

    # Підписи кривих
    f.append(text(map_x(0), map_y(0.95) - 12, 'I₁ = I₀/2 · (1 + cos Δφ)', 11, POS, 'middle', bold=True))
    f.append(text(map_x(math.pi), map_y(0.95) - 12, 'I₂ = I₀/2 · (1 - cos Δφ)', 11, NEG, 'middle', bold=True))

    render(os.path.join(IMG, 'intensity-curve.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Інтегрально-оптичний модулятор Маха — Цендера
# ═══════════════════════════════════════════════════════════════════════════
def fig_integrated_modulator():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Інтегрально-оптичний модулятор Маха — Цендера (MZM)', 16, INK, 'middle', bold=True))

    # Підкладка з LiNbO3
    f.append(rect(40, 70, 640, 200, fill='#f1f5f9', stroke='#64748b', sw=1.5, rx=6))
    f.append(text(60, 92, 'Кристалічна підкладка LiNbO₃ (ніобат літію)', 11, MUTED, 'start', bold=True))

    # Оптичний хвилевод (Y-розгалужувач -> два плечі -> Y-зводжувач)
    # Вхідний хвилевод
    f.append(line(40, 170, 140, 170, color=POS, sw=5))
    f.append(text(85, 155, 'Вхідний промінь (I₀)', 10, POS, 'middle', bold=True))

    # Y-розгалуження
    f.append(line(140, 170, 200, 120, color=POS, sw=4))
    f.append(line(140, 170, 200, 220, color=POS, sw=4))

    # Паралельні плечі хвилеводу
    f.append(line(200, 120, 480, 120, color=POS, sw=4))
    f.append(text(340, 104, 'Плече 1 (+Δn)', 10, POS, 'middle', bold=True))

    f.append(line(200, 220, 480, 220, color=POS, sw=4))
    f.append(text(340, 238, 'Плече 2 (-Δn)', 10, FIELD, 'middle', bold=True))

    # Y-зведення
    f.append(line(480, 120, 540, 170, color=POS, sw=4))
    f.append(line(480, 220, 540, 170, color=POS, sw=4))

    # Вихідний хвилевод
    f.append(line(540, 170, 680, 170, color=POS, sw=5))
    f.append(text(610, 155, 'Модульований вихід I(t)', 10, POS, 'middle', bold=True))

    # Керуючі електроди (Push-Pull структура)
    # Верхній електрод (GND)
    f.append(rect(240, 80, 200, 22, fill='#cbd5e1', stroke=LINE, sw=1, rx=2))
    f.append(text(340, 95, 'Електрод «Земля» (GND)', 10, INK, 'middle'))

    # Середній електрод (Signal V(t))
    f.append(rect(240, 155, 200, 30, fill='#fde047', stroke='#ca8a04', sw=1.5, rx=2))
    f.append(text(340, 174, 'ВЧ-електрод сигналу V(t)', 11, '#854d0e', 'middle', bold=True))

    # Нижній електрод (GND)
    f.append(rect(240, 238, 200, 22, fill='#cbd5e1', stroke=LINE, sw=1, rx=2))
    f.append(text(340, 253, 'Електрод «Земля» (GND)', 10, INK, 'middle'))

    # Формула півхвильової напруги V_pi знизу
    f.append(fitbox(40, 285, 640, 55,
                    'Диференційне push-pull керування:\nНапруга V(t) створює протилежні електричні поля в плечах 1 та 2 завдяки поккельс-ефекту.\nПівхвильова напруга V_π забезпечує повний фазовий зсув Δφ = π та перемикання оптичної інтенсивності 0 ↔ I₀.',
                    size=10, color=INK, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'integrated-modulator.svg'), W, H, *f)

if __name__ == '__main__':
    fig_mach_zehnder_scheme()
    fig_beam_splitter_phase()
    fig_intensity_curve()
    fig_integrated_modulator()
    print("All figures successfully rendered!")
