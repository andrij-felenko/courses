# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Добротність котушки індуктивності».
Використовує бібліотеку svgkit з теки scripts/.
Зображення записуються в ./img/.
"""
import sys
import os
import math

# Підключаємо svgkit зі scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Енергетичний зміст добротності котушки ───────────────────────────
def fig_energy_cycle():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 28, "Енергетичний баланс за один період коливань", size=16, bold=True))
    p.append(text(W / 2, 48, "Добротність Q = 2π · (максимальна запасена енергія) / (розсіяна енергія за період)",
                  size=12, color=MUTED, italic=True))

    # Ліва колонка: Запасена енергія магнітного поля
    lx, ly = 210, 195
    p.append(rect(lx - 160, ly - 115, 320, 240, fill="#f4f9f4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(lx, ly - 85, "Запасена енергія поля", size=14, color=FIELD, bold=True))
    
    # Спрощена ілюстрація синусоїди енергії W(t) = 1/2 * L * i^2(t)
    ox, oy = lx - 110, ly + 25
    p.append(line(ox, oy, ox + 220, oy, color=LINE, sw=1.2))
    p.append(line(ox, oy + 50, ox, oy - 70, color=LINE, sw=1.2))
    p.append(text(ox + 225, oy + 4, "t", size=11, color=INK, anchor="start"))
    p.append(text(ox, oy - 75, "W_L(t)", size=11, color=INK, bold=True))

    pts_w = []
    for i in range(101):
        t = i / 100.0 * 2 * math.pi
        px = ox + i * 2.0
        # sin^2(t) коливається від 0 до 1 з подвоєною частотою
        py = oy - (math.sin(t) ** 2) * 55
        pts_w.append((px, py))
    d_w = "M %.1f,%.1f " % pts_w[0] + " ".join("L %.1f,%.1f" % pt for pt in pts_w[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_w, FIELD))
    
    p.append(line(ox, oy - 55, ox + 200, oy - 55, color=FIELD, sw=1, dash="4,3"))
    p.append(text(ox + 100, oy - 62, "W_max = ½ · L · I_pk²", size=11.5, color=FIELD, bold=True))
    p.append(text(lx, ly + 85, "Енергія реактивно коливається", size=11, color=INK))
    p.append(text(lx, ly + 102, "між котушкою та зовнішнім колом", size=10.5, color=MUTED))

    # Права колонка: Втрачена енергія за період
    rx, ry = 570, 195
    p.append(rect(rx - 160, ry - 115, 320, 240, fill="#fdf4f4", stroke=POS, sw=1.8, rx=8))
    p.append(text(rx, ry - 85, "Втрати тепла за 1 період", size=14, color=POS, bold=True))

    # Графік накопичення тепла / розсіяння за період
    rox, roy = rx - 110, ry + 25
    p.append(line(rox, roy + 40, rox + 220, roy + 40, color=LINE, sw=1.2))
    p.append(line(rox, roy + 45, rox, roy - 70, color=LINE, sw=1.2))
    p.append(text(rox + 225, roy + 44, "t", size=11, color=INK, anchor="start"))
    p.append(text(rox, roy - 75, "E_втрат", size=11, color=INK, bold=True))

    pts_loss = []
    for i in range(101):
        frac = i / 100.0
        px = rox + i * 2.0
        # Лінійне зростання розсіяної енергії
        py = (roy + 40) - frac * 85
        pts_loss.append((px, py))
    d_loss = "M %.1f,%.1f " % pts_loss[0] + " ".join("L %.1f,%.1f" % pt for pt in pts_loss[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_loss, POS))

    p.append(line(rox + 200, roy + 40, rox + 200, roy - 45, color=POS, sw=1, dash="4,3"))
    p.append(text(rox + 100, roy - 55, "ΔW_період = P_втрат · T", size=11.5, color=POS, bold=True))
    p.append(text(rx, ry + 85, "Незворотне перетворення на тепло", size=11, color=INK))
    p.append(text(rx, ry + 102, "через активний опір та осердя", size=10.5, color=MUTED))

    # Центральна стрілка зв'язку
    p.append(arrow(380, 195, 400, 195, color=LINE, sw=2))

    render(os.path.join(IMG, "energy-cycle.svg"), W, H, *p)


# ── Фігура 2: Повна еквівалентна схема реальної котушки ───────────────────────
def fig_equivalent_circuit():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 26, "Високочастотна еквівалентна схема реальної котушки", size=16, bold=True))
    p.append(text(W / 2, 46, "Послідовні омічні й магнітні втрати та паралельні діелектричні й ємнісні паразитики",
                  size=12, color=MUTED, italic=True))

    # Виводи котушки
    p.append(circle(70, 190, 4.5, fill=LINE, stroke=LINE))
    p.append(circle(750, 190, 4.5, fill=LINE, stroke=LINE))
    p.append(text(50, 194, "Вхід A", size=12, bold=True, anchor="end"))
    p.append(text(770, 194, "Вхід B", size=12, bold=True, anchor="start"))

    # Основна лінія
    p.append(line(70, 190, 150, 190, color=LINE, sw=2))
    p.append(line(670, 190, 750, 190, color=LINE, sw=2))

    # Вузол розгалуження на паразитну ємність
    p.append(circle(150, 190, 3.5, fill=LINE, stroke=LINE))
    p.append(circle(670, 190, 3.5, fill=LINE, stroke=LINE))

    # Нижня гілка: Послідовний ланцюг R_s(f) та L
    p.append(line(150, 190, 210, 190, color=LINE, sw=2))

    # Резистор R_s(f)
    p.append(rect(210, 172, 130, 36, fill="#fdf4f4", stroke=POS, sw=1.8, rx=4))
    p.append(text(275, 195, "R_s(f)", size=13, color=POS, bold=True))
    p.append(text(275, 230, "Послідовні втрати", size=11, color=POS, bold=True))
    p.append(text(275, 246, "R_dc + R_skin + R_prox + R_core", size=10, color=MUTED))

    p.append(line(340, 190, 400, 190, color=LINE, sw=2))

    # Індуктивність L
    p.append(rect(400, 172, 120, 36, fill="#f4f9f4", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(460, 195, "L (номінал)", size=13, color=FIELD, bold=True))
    p.append(text(460, 230, "Головна індуктивність", size=11, color=FIELD, bold=True))
    p.append(text(460, 246, "Запас магнітної енергії", size=10, color=MUTED))

    p.append(line(520, 190, 670, 190, color=LINE, sw=2))

    # Верхня паралельна гілка: C_p та R_p (діелектричні втрати)
    p.append(line(150, 190, 150, 100, color=LINE, sw=1.8))
    p.append(line(150, 100, 260, 100, color=LINE, sw=1.8))

    # Паразитна ємність C_p
    p.append(rect(260, 82, 100, 36, fill="#eef3fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(310, 105, "C_p", size=13, color=NEG, bold=True))
    p.append(text(310, 68, "Паразитна ємність", size=11, color=NEG, bold=True))

    p.append(line(360, 100, 440, 100, color=LINE, sw=1.8))

    # Паразитний опір діелектричних втрат R_p
    p.append(rect(440, 82, 130, 36, fill="#fbf0fd", stroke="#8e44ad", sw=1.8, rx=4))
    p.append(text(505, 105, "R_p(f) діелектрик", size=12, color="#8e44ad", bold=True))
    p.append(text(505, 68, "Втрати в ізоляції/каркасі", size=11, color="#8e44ad", bold=True))

    p.append(line(570, 100, 670, 100, color=LINE, sw=1.8))
    p.append(line(670, 100, 670, 190, color=LINE, sw=1.8))

    # Нижня рамка висновку
    p.append(fitbox(150, 280, 520, 50,
                    "Добротність: Q(f) = Im{Z} / Re{Z} ≈ ω·L / R_s(f) · [1 − (f / f_SRF)²]\n"
                    "На резонансі f_SRF = 1 / (2π√(L·C_p)) реактивний опір зникає, і Q падає до нуля.",
                    size=11.5, fill="#f8f9fa", stroke="#d0d7de", color=INK))

    render(os.path.join(IMG, "equivalent-circuit.svg"), W, H, *p)


# ── Фігура 3: Чотири фізичні канали втрат у котушці ───────────────────────────
def fig_loss_mechanisms():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 26, "Чотири фізичні механізми розсіювання енергії", size=16, bold=True))
    p.append(text(W / 2, 46, "Кожен канал має свою частотну залежність та геометрію локалізації втрат",
                  size=12, color=MUTED, italic=True))

    cards = [
        ("1. Омічний опір (DCR)",
         "Постійний струм\nРівномірна густина по перерізу\nR_dc = ρ · l / A\nВнесок: переважає на низьких f",
         "#f4f6f8", LINE, 50, 75),
        ("2. Скін та Proximity",
         "Скін-шар δ ∝ 1/√f\nВихрові струми від сусідів\nСтрум тиснеться до країв витків\nR_ac зростає як √f та f²",
         "#fdf4f4", POS, 245, 75),
        ("3. Втрати в осерді",
         "Гістерезис: площа петлі B-H ∝ f\nВихрові струми в осерді ∝ f²\nP_core = k_h·f·Bⁿ + k_e·f²·B²\nВибір: NiZn ферит або повітря",
         "#fdf8ee", "#d35400", 440, 75),
        ("4. Діелектрик ізоляції",
         "Поляризація лаку та каркаса\nЗатримка диполів у полі\nКут втрат tan δ_d\nR_s,diel зростає як f³ біля SRF",
         "#fbf0fd", "#8e44ad", 635, 75)
    ]

    for title_c, desc_c, bg_c, stroke_c, cx, cy in cards:
        p.append(rect(cx, cy, 165, 230, fill=bg_c, stroke=stroke_c, sw=1.6, rx=6))
        p.append(text(cx + 82, cy + 24, title_c, size=11.5, color=stroke_c, bold=True))
        p.append(line(cx + 10, cy + 36, cx + 155, cy + 36, color=stroke_c, sw=0.8))
        
        lines = desc_c.split("\n")
        for idx, ln in enumerate(lines):
            p.append(text(cx + 12, cy + 62 + idx * 24, ln, size=10, color=INK, anchor="start"))

    # Нижня стрілка частотної шкали
    p.append(line(50, 345, 790, 345, color=LINE, sw=2))
    p.append(arrow(770, 345, 800, 345, color=LINE, sw=2))
    p.append(text(805, 349, "Частота f", size=12, color=INK, anchor="start", bold=True))

    p.append(text(132, 375, "Низькі частоти (DC..кГц)", size=11, color=LINE, bold=True))
    p.append(text(132, 392, "Переважає мідний DCR", size=10, color=MUTED))

    p.append(text(327, 375, "Середні частоти (кГц..МГц)", size=11, color=POS, bold=True))
    p.append(text(327, 392, "Скін + Проксиміті витків", size=10, color=MUTED))

    p.append(text(522, 375, "ВЧ діапазон (МГц..декоМГц)", size=11, color="#d35400", bold=True))
    p.append(text(522, 392, "Гістерезис та вихори осердя", size=10, color=MUTED))

    p.append(text(717, 375, "НадВЧ / біля SRF", size=11, color="#8e44ad", bold=True))
    p.append(text(717, 392, "Діелектрик каркаса і C_p", size=10, color=MUTED))

    render(os.path.join(IMG, "loss-mechanisms.svg"), W, H, *p)


# ── Фігура 4: Частотна залежність добротності Q(f) ─────────────────────────────
def fig_q_frequency_curve():
    W, H = 800, 440
    p = []
    p.append(text(W / 2, 26, "Частотна залежність добротності Q(f) реальної котушки", size=16, bold=True))
    p.append(text(W / 2, 46, "Зростання з ωL, досягнення піку Q_max та стрімкий спад до нуля при f → f_SRF",
                  size=12, color=MUTED, italic=True))

    ox, oy = 90, 350
    w_ax, h_ax = 640, 260

    # Осі координат
    p.append(line(ox, oy, ox + w_ax, oy, color=LINE, sw=1.8))
    p.append(line(ox, oy, ox, oy - h_ax, color=LINE, sw=1.8))
    p.append(arrow(ox + w_ax - 20, oy, ox + w_ax + 10, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy - h_ax + 20, ox, oy - h_ax - 10, color=LINE, sw=1.8))

    p.append(text(ox + w_ax + 15, oy + 4, "Частота f (log)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ox, oy - h_ax - 18, "Добротність Q", size=12, color=INK, bold=True))

    # Створення реалістичної кривої Q(f)
    pts_ideal = []
    pts_real = []

    for i in range(1, 101):
        fn = i / 100.0
        px = ox + math.log10(fn * 9 + 1) * w_ax * 0.85
        
        # Ідеальна котушка тільки з DCR: Q = k * f
        q_ideal = fn * 220
        py_ideal = oy - min(q_ideal, h_ax - 20)
        pts_ideal.append((px, py_ideal))

        # Реальна котушка
        r_eff = 1.0 + 2.5 * math.sqrt(fn) + 4.0 * (fn ** 2)
        q_true = (fn * 450) / r_eff
        srf_factor = max(0.0, 1.0 - (fn / 0.92) ** 2)
        q_meas = q_true * srf_factor
        py_real = oy - q_meas * 1.3
        pts_real.append((px, py_real))

    # Лінія ідеальної добротності (пунктир)
    d_ideal = "M %.1f,%.1f " % pts_ideal[0] + " ".join("L %.1f,%.1f" % pt for pt in pts_ideal[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4"/>' % (d_ideal, MUTED))
    p.append(text(ox + 350, oy - 220, "Ідеальна котушка без ВЧ-втрат (Q = ωL / R_dc)", size=11, color=MUTED))

    # Реальна крива Q(f)
    d_real = "M %.1f,%.1f " % pts_real[0] + " ".join("L %.1f,%.1f" % pt for pt in pts_real[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d_real, FIELD))

    # Точка максимуму Q_max
    max_pt = min(pts_real, key=lambda pt: pt[1])
    p.append(circle(max_pt[0], max_pt[1], 5, fill=POS, stroke=POS))
    p.append(line(max_pt[0], oy, max_pt[0], max_pt[1], color=POS, sw=1, dash="3,3"))
    p.append(line(ox, max_pt[1], max_pt[0], max_pt[1], color=POS, sw=1, dash="3,3"))
    
    p.append(text(max_pt[0], oy + 18, "f_opt", size=12, color=POS, bold=True))
    p.append(text(ox - 10, max_pt[1] + 4, "Q_max", size=12, color=POS, anchor="end", bold=True))
    p.append(text(max_pt[0] + 15, max_pt[1] - 12, "Оптимальна робоча зона", size=11, color=POS, bold=True))

    # Точка власного резонансу f_SRF
    srf_x = pts_real[-9][0]
    p.append(circle(srf_x, oy, 5, fill=NEG, stroke=NEG))
    p.append(text(srf_x, oy + 18, "f_SRF", size=12, color=NEG, bold=True))
    p.append(text(srf_x - 10, oy - 35, "Власний резонанс\n(Q = 0, C_p шунтує L)", size=10.5, color=NEG, bold=True))

    # Зони на графіку
    p.append(fitbox(ox + 40, oy - 110, 140, 50, "Зона 1: Q ∝ f\nПереважає мідний DCR", size=10.5, fill="#f4f6f8", stroke="#d0d7de"))
    p.append(fitbox(max_pt[0] - 80, oy - 180, 160, 50, "Зона 2: Пік Q_max\nБаланс реактивності\nта ВЧ втрат", size=10.5, fill="#f4f9f4", stroke=FIELD))
    p.append(fitbox(srf_x - 120, oy - 120, 140, 50, "Зона 3: Спад до 0\nДомінує паразитна\nємність C_p", size=10.5, fill="#fdf4f4", stroke=POS))

    render(os.path.join(IMG, "q-frequency-curve.svg"), W, H, *p)


# ── Фігура 5: Інженерні методи підвищення добротності ─────────────────────────
def fig_winding_techniques():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 26, "Конструктивні методи мінімізації втрат та ємності", size=16, bold=True))
    p.append(text(W / 2, 46, "Оптимізація форми провідника, просторового розміщення витків та матеріалу каркаса",
                  size=12, color=MUTED, italic=True))

    panels = [
        ("Літцендрат (Litz wire)",
         "Сотні тонких ізольованих жил\nПереплетені в об'ємі пучка\nЗнищує скін та проксиміті\nЕфективний: 10 кГц – 2 МГц",
         "#f4f9f4", FIELD, 40, 75),
        ("Секційне намотування",
         "Обмотка розбита на секції N\nПослідовне з'єднання C_sec\nC_total = C_sec / N\nЗнижує C_p у N² разів!",
         "#eef3fd", NEG, 235, 75),
        ("Кошикове / Універсаль",
         "Перехресне укладання витків\nСусідні витки не паралельні\nМінімум площі перекриття\nШироко у ВЧ радіоприймачах",
         "#fdf8ee", "#d35400", 430, 75),
        ("Крокове намотування (ВЧ)",
         "Крок між витками s ≈ d\nПовітряне або керамічне осердя\nМінімум ємності та tan δ\nПосріблені трубки на VHF/UHF",
         "#fbf0fd", "#8e44ad", 625, 75)
    ]

    for title_p, desc_p, bg_p, stroke_p, px, py in panels:
        p.append(rect(px, py, 175, 205, fill=bg_p, stroke=stroke_p, sw=1.6, rx=6))
        p.append(text(px + 87, py + 24, title_p, size=11, color=stroke_p, bold=True))
        p.append(line(px + 10, py + 36, px + 165, py + 36, color=stroke_p, sw=0.8))
        
        lines = desc_p.split("\n")
        for idx, ln in enumerate(lines):
            p.append(text(px + 12, py + 62 + idx * 24, ln, size=10, color=INK, anchor="start"))

    # Нижній порівняльний блок
    p.append(fitbox(40, 295, 760, 65,
                    "Головний закон високої добротності:\n"
                    "Для низьких/середніх частот (кГц..МГц) боротьба йде за площу міді та опір (літцендрат, ферит),\n"
                    "а на високих частотах (МГц..ГГц) — за мінімізацію ємності C_p та діелектричних втрат (крок, повітря, фторопласт).",
                    size=11, fill="#f8f9fa", stroke="#d0d7de", color=INK))

    render(os.path.join(IMG, "winding-techniques.svg"), W, H, *p)


def main():
    fig_energy_cycle()
    fig_equivalent_circuit()
    fig_loss_mechanisms()
    fig_q_frequency_curve()
    fig_winding_techniques()
    print("Всі 5 SVG-фігур успішно згенеровано у %s" % IMG)


if __name__ == "__main__":
    main()
