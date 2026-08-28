# -*- coding: utf-8 -*-
"""Фігури до статті «Комплект для монтажу: паста, трафарет, pick&place, складальне креслення».
Дві фігури:
  pick-and-place-coordinate-alignment.svg — узгодження кутів орієнтації: CAD footprint, стрічка EIA-481 та P&P насадка
  assembly-drawing-callouts.svg           — анатомія складального креслення: репери, полярності, примітки й зони
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. pick-and-place-coordinate-alignment.svg
# ════════════════════════════════════════════════════════════════════════════
def fig_pick_and_place_alignment():
    W, H = 840, 420
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 28, "Узгодження нульових орієнтацій: CAD-бібліотека, стрічка EIA-481 та монтажний автомат",
                  size=15, bold=True, color=INK))

    # Секція 1: Футпринт у САПР (IPC-7351)
    x1, y1, w1, h1 = 30, 60, 240, 310
    f.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 26, "1. САПР-посадкова зона", size=13, bold=True, color=NEG))
    f.append(text(x1 + w1 / 2, y1 + 44, "Стандарт IPC-7351 (Кут 0°)", size=11, color=MUTED))

    # Рисуємо мікросхему в САПР: Вивід 1 зверху ліворуч
    ic1_cx, ic1_cy = x1 + w1 / 2, y1 + 130
    f.append(rect(ic1_cx - 45, ic1_cy - 45, 90, 90, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    # Виводи (піни)
    for dy in [-30, -10, 10, 30]:
        f.append(rect(ic1_cx - 58, ic1_cy + dy - 4, 12, 8, fill="#e2e8f0", stroke=LINE, sw=1))
        f.append(rect(ic1_cx + 46, ic1_cy + dy - 4, 12, 8, fill="#e2e8f0", stroke=LINE, sw=1))
    for dx in [-30, -10, 10, 30]:
        f.append(rect(ic1_cx + dx - 4, ic1_cy - 58, 8, 12, fill="#e2e8f0", stroke=LINE, sw=1))
        f.append(rect(ic1_cx + dx - 4, ic1_cy + 46, 8, 12, fill="#e2e8f0", stroke=LINE, sw=1))
    # Точка виводу 1 (Pin 1 dot)
    f.append(circle(ic1_cx - 30, ic1_cy - 30, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(ic1_cx - 30, ic1_cy - 16, "Pin 1", size=10, bold=True, color=POS))
    # Центроїд (X=0, Y=0)
    f.append(line(ic1_cx - 10, ic1_cy, ic1_cx + 10, ic1_cy, color=FIELD, sw=1.5))
    f.append(line(ic1_cx, ic1_cy - 10, ic1_cx, ic1_cy + 10, color=FIELD, sw=1.5))
    f.append(circle(ic1_cx, ic1_cy, 2.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(ic1_cx + 20, ic1_cy + 14, "(X, Y)", size=10, bold=True, color=FIELD))

    f.append(mtext(x1 + w1 / 2, y1 + 225,
                   ["Вивід 1 орієнтований", "вгору-ліворуч (Level A).", "Кут у САПР = 0°.", "Координата — центроїд."],
                   size=11, color=INK))

    # Стрілка переходу 1 -> 2
    f.append(arrow(x1 + w1 + 4, y1 + 140, x1 + w1 + 26, y1 + 140, color=MUTED, sw=2))

    # Секція 2: Стрічка живильника (EIA-481)
    x2, y2, w2, h2 = 300, 60, 240, 310
    f.append(rect(x2, y2, w2, h2, fill="#fffbf5", stroke="#d97706", sw=1.8, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 26, "2. Стрічка в живильнику", size=13, bold=True, color="#b45309"))
    f.append(text(x2 + w2 / 2, y2 + 44, "Стандарт EIA-481 (У кишені)", size=11, color=MUTED))

    # Рисуємо стрічку
    tp_cx, tp_cy = x2 + w2 / 2, y2 + 130
    f.append(rect(tp_cx - 55, tp_cy - 65, 110, 130, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    # Отвори перфорації стрічки
    for py in range(int(tp_cy - 55), int(tp_cy + 65), 24):
        f.append(circle(tp_cx - 43, py, 4, fill="#ffffff", stroke="#d97706", sw=1.2))
    # Кишеня
    f.append(rect(tp_cx - 25, tp_cy - 35, 70, 70, fill="#ffffff", stroke="#b45309", sw=1.2, rx=3))
    # Мікросхема всередині повернута на 90 градусів за годинниковою стрілкою (Pin 1 у верхньому правому кутку)
    f.append(rect(tp_cx - 18, tp_cy - 28, 56, 56, fill="#f8fafc", stroke=LINE, sw=1.2, rx=2))
    f.append(circle(tp_cx + 26, tp_cy - 18, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(tp_cx + 14, tp_cy - 5, "Pin 1", size=10, bold=True, color=POS))
    f.append(text(tp_cx + 10, tp_cy + 18, "Кут = 90°", size=10, bold=True, color="#b45309"))

    f.append(mtext(x2 + w2 / 2, y2 + 225,
                   ["У стрічці деталь може", "лежати з поворотом 90°", "щодо перфорації.", "Невідповідність = розбіг!"],
                   size=11, color=INK))

    # Стрілка переходу 2 -> 3
    f.append(arrow(x2 + w2 + 4, y2 + 140, x2 + w2 + 26, y2 + 140, color=MUTED, sw=2))

    # Секція 3: Вакуумна насадка та плата
    x3, y3, w3, h3 = 570, 60, 240, 310
    f.append(rect(x3, y3, w3, h3, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x3 + w3 / 2, y3 + 26, "3. Корекція автоматом", size=13, bold=True, color=FIELD))
    f.append(text(x3 + w3 / 2, y3 + 44, "CPL Rotation + Vision камера", size=11, color=MUTED))

    # Насадка P&P
    nz_cx, nz_cy = x3 + w3 / 2, y3 + 120
    # Плата під низом
    f.append(rect(nz_cx - 50, nz_cy + 15, 100, 28, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(nz_cx, nz_cy + 33, "Контактні майданчики", size=9, bold=True, color=FIELD))
    # Вакуумне сопло
    f.append(rect(nz_cx - 10, nz_cy - 55, 20, 35, fill="#94a3b8", stroke=LINE, sw=1.5, rx=2))
    f.append(line(nz_cx - 18, nz_cy - 20, nz_cx + 18, nz_cy - 20, color=LINE, sw=2))
    # Компонент на соплі з корекцією кута
    f.append(rect(nz_cx - 30, nz_cy - 18, 60, 26, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    f.append(circle(nz_cx - 20, nz_cy - 8, 3.5, fill=POS, stroke=POS, sw=1))
    f.append(text(nz_cx + 5, nz_cy - 5, "Δθ = -90°", size=10, bold=True, color=POS))

    # Кругова стрілка обертання
    f.append(text(nz_cx, nz_cy - 65, "Поворот голівки на кут Δθ", size=10, bold=True, color=FIELD))

    f.append(mtext(x3 + w3 / 2, y3 + 225,
                   ["Оптична камера центрує X,Y.", "Таблиця CPL задає кут θ.", "Автомат розвертає голівку", "на точний кут плати."],
                   size=11, color=INK))

    # Підсумок знизу
    f.append(text(W / 2, 395, "CPL файл транслює координати й кути CAD у реальний алгоритм забору та посадки",
                  size=12, bold=True, color=MUTED))

    render(os.path.join(IMG, "pick-and-place-coordinate-alignment.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. assembly-drawing-callouts.svg
# ════════════════════════════════════════════════════════════════════════════
def fig_assembly_drawing_callouts():
    W, H = 860, 480
    f = []

    f.append(text(W / 2, 28, "Складальне креслення друкованого вузла (Assembly Drawing)",
                  size=16, bold=True, color=INK))

    # Поле креслення друкованої плати (ліворуч)
    bx, by, bw, bh = 40, 60, 470, 360
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=2, rx=6))
    f.append(text(bx + 16, by + 22, "TOP ASSEMBLY VIEW", size=11, bold=True, color=MUTED, anchor="start"))

    # Контур плати
    pcb_x, pcb_y, pcb_w, pcb_h = bx + 40, by + 40, 390, 270
    f.append(rect(pcb_x, pcb_y, pcb_w, pcb_h, fill="#ffffff", stroke=FIELD, sw=2.5, rx=10))

    # Монтажні отвори плати (Mounting holes)
    for hx, hy in [(pcb_x + 18, pcb_y + 18), (pcb_x + pcb_w - 18, pcb_y + 18),
                   (pcb_x + 18, pcb_y + pcb_h - 18), (pcb_x + pcb_w - 18, pcb_y + pcb_h - 18)]:
        f.append(circle(hx, hy, 9, fill="#f1f5f9", stroke=LINE, sw=1.5))
        f.append(circle(hx, hy, 4, fill="#ffffff", stroke=LINE, sw=1))

    # Глобальні репери (Global Fiducials)
    f1_x, f1_y = pcb_x + 40, pcb_y + 20
    f2_x, f2_y = pcb_x + pcb_w - 35, pcb_y + 20
    f3_x, f3_y = pcb_x + 40, pcb_y + pcb_h - 20
    for fx, fy in [(f1_x, f1_y), (f2_x, f2_y), (f3_x, f3_y)]:
        f.append(circle(fx, fy, 7, fill="#fee2e2", stroke=POS, sw=1.5))
        f.append(circle(fx, fy, 2.5, fill=POS, stroke=POS, sw=1))

    # Компоненти на платі
    # Мікросхема U1 (QFP/QFN)
    u1_x, u1_y, u1_w, u1_h = pcb_x + 130, pcb_y + 70, 90, 90
    f.append(rect(u1_x, u1_y, u1_w, u1_h, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=4))
    # Зрізаний кут і точка Pin 1
    f.append(circle(u1_x + 14, u1_y + 14, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(u1_x + u1_w / 2, u1_y + u1_h / 2 - 6, "U1", size=13, bold=True, color=INK))
    f.append(text(u1_x + u1_w / 2, u1_y + u1_h / 2 + 10, "MCU LQFP-48", size=9, color=MUTED))
    # Локальний репер біля U1
    f.append(circle(u1_x - 14, u1_y - 14, 5, fill="#fee2e2", stroke=POS, sw=1.2))
    f.append(circle(u1_x - 14, u1_y - 14, 1.8, fill=POS, stroke=POS, sw=1))

    # Діод D1 (полярний)
    d1_x, d1_y = pcb_x + 60, pcb_y + 110
    f.append(rect(d1_x, d1_y, 40, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    f.append(rect(d1_x, d1_y, 8, 20, fill=POS, stroke=POS, sw=1, rx=1)) # Смужка катода
    f.append(text(d1_x + 24, d1_y + 14, "D1", size=10, bold=True, color=INK))

    # Танталовий конденсатор C1 (полярний)
    c1_x, c1_y = pcb_x + 60, pcb_y + 160
    f.append(rect(c1_x, c1_y, 40, 22, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    f.append(rect(c1_x, c1_y, 10, 22, fill=NEG, stroke=NEG, sw=1, rx=1)) # Смужка анода (+)
    f.append(text(c1_x + 5, c1_y + 15, "+", size=11, bold=True, color="#ffffff"))
    f.append(text(c1_x + 26, c1_y + 15, "C1", size=10, bold=True, color=INK))

    # Рознім J1 (Through-hole / SMT)
    j1_x, j1_y, j1_w, j1_h = pcb_x + 270, pcb_y + 60, 70, 110
    f.append(rect(j1_x, j1_y, j1_w, j1_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=3))
    f.append(text(j1_x + j1_w / 2, j1_y + 20, "J1 USB-C", size=10, bold=True, color="#b45309"))
    f.append(circle(j1_x + 12, j1_y + 40, 3, fill=POS, stroke=POS, sw=1))
    f.append(text(j1_x + 24, j1_y + 43, "Pin 1", size=9, bold=True, color=POS))

    # Зона заборони / Keepout під радіатор або лакування
    kz_x, kz_y, kz_w, kz_h = pcb_x + 110, pcb_y + 190, 140, 60
    f.append(rect(kz_x, kz_y, kz_w, kz_h, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(kz_x + kz_w / 2, kz_y + 24, "ЗОНА БЕЗ ЛАКУ", size=10, bold=True, color=POS))
    f.append(text(kz_x + kz_w / 2, kz_y + 42, "(Masking Keep-Out)", size=9, color=MUTED))

    # Панель виносок і приміток (Callouts & Notes праворуч)
    nx, ny, nw, nh = 530, 60, 300, 360
    f.append(rect(nx, ny, nw, nh, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(nx + nw / 2, ny + 24, "ВИРОБНИЧІ ВИМОГИ (NOTES)", size=12, bold=True, color=INK))

    notes = [
        "1. Монтаж згідно зі стандартом IPC-A-610 Class 2.",
        "2. Паяльна паста: SAC305, No-Clean, Type 4.",
        "3. Реперні знаки (Fiducials): 3 глобальні + локальні.",
        "4. D1: Смужка позначає КАТОД (Cathode).",
        "5. C1: Смужка позначає ПОЗИТИВНИЙ вивід (+).",
        "6. J1: Момент затяжки гвинтів кріплення = 0.35 Н·м.",
        "7. Пунктирна зона: захистити від захисного лаку.",
        "8. Не встановлювати компоненти з поміткою DNP."
    ]
    for i, n in enumerate(notes):
        f.append(text(nx + 14, ny + 58 + i * 36, n, size=10.5, color=INK, anchor="start"))

    # Виноски лініями (Callout lines)
    # До репера
    f.append(line(f1_x + 5, f1_y + 5, f1_x + 35, f1_y + 35, color=POS, sw=1.2))
    f.append(text(f1_x + 40, f1_y + 42, "Глобальний репер (Fiducial)", size=9, bold=True, color=POS, anchor="start"))

    # До U1 Pin 1
    f.append(line(u1_x + 14, u1_y + 10, u1_x + 14, u1_y - 20, color=POS, sw=1.2))
    f.append(text(u1_x + 14, u1_y - 24, "Вивід 1 мікросхеми", size=9, bold=True, color=POS, anchor="middle"))

    # До D1
    f.append(line(d1_x + 4, d1_y + 10, d1_x - 20, d1_y - 10, color=POS, sw=1.2))
    f.append(text(d1_x - 24, d1_y - 12, "Катод", size=9, bold=True, color=POS, anchor="end"))

    # Загальний підпис знизу
    f.append(text(W / 2, 452, "Складальне креслення — еталон верифікації для технолога, оператора P&P та інспекції AOI",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "assembly-drawing-callouts.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pick_and_place_alignment()
    fig_assembly_drawing_callouts()
    print("SVG figures generated successfully in ./img/")
