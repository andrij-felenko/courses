# -*- coding: utf-8 -*-
"""Фігури до теми «Магнітний опір і магнітне коло».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
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


# ── Фігура 1: Аналогія між електричним та магнітним колами ─────────────────
def fig_magnetic_circuit_analogy():
    W, H = 780, 410
    f = []
    f.append(text(W / 2, 28, "Аналогія та різниця між електричним і магнітним колами", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Електричне коло ---
    f.append(text(midx / 2, 54, "Електричне коло (Закон Ома)", size=13, bold=True, color=COLOR_RED))

    # Джерело напруги V (ЕРС)
    f.append(circle(70, 150, 22, fill=FILL, stroke=COLOR_RED, sw=2))
    f.append(text(70, 145, "+", size=13, bold=True, color=COLOR_RED))
    f.append(text(70, 160, "V", size=13, bold=True, color=COLOR_RED))

    # Провідники електричного кола
    f.append(line(70, 128, 70, 100, color=LINE, sw=2))
    f.append(line(70, 100, 310, 100, color=LINE, sw=2))
    f.append(line(70, 172, 70, 200, color=LINE, sw=2))
    f.append(line(70, 200, 310, 200, color=LINE, sw=2))

    # Опір R
    f.append(line(310, 100, 310, 125, color=LINE, sw=2))
    f.append(line(310, 200, 310, 175, color=LINE, sw=2))
    f.append(rect(298, 125, 24, 50, fill='#fff0f0', stroke=COLOR_RED, sw=2, rx=4))
    f.append(text(310, 150, "R", size=13, bold=True, color=COLOR_RED))

    # Напрямок струму I
    f.append(arrow(140, 100, 200, 100, color=COLOR_RED, sw=2))
    f.append(text(170, 88, "Струм I", size=12, bold=True, color=COLOR_RED))

    # Пояснення закону Ома
    b1, w1, h1 = textbox(midx / 2, 275, 
                         "V = I · R  (ЕРС = Струм · Опір)\n"
                         "• Струм — рух зарядів (Ампери)\n"
                         "• Виділяється тепло Джоуля: P = I²·R\n"
                         "• σ міді / σ повітря ≈ 10²¹ (повітря — ізолятор)",
                         size=11, pad=8, fill="#fff8f8", stroke="#ffcccc", sw=1.2)
    f.append(b1)


    # --- ПРАВА ЧАСТИНА: Магнітне коло ---
    f.append(text(midx + midx / 2, 54, "Магнітне коло (Закон Гопкінсона)", size=13, bold=True, color=COLOR_BLUE))

    # Магнітопровід побудований окремими лініями / контуром без накладання рамок
    f.append(rect(440, 100, 270, 100, fill="#eef4ff", stroke=COLOR_BLUE, sw=2.5, rx=8))
    f.append(rect(475, 122, 200, 56, fill=BG, stroke=COLOR_BLUE, sw=1.8, rx=4))

    # Текст обмотки N·I без накладання зовнішнього прямокутника
    f.append(text(440, 150, "N·I", size=12, bold=True, color=COLOR_ORANGE))

    # Потік Φ (пунктирне коло всередині)
    f.append(line(457, 111, 695, 111, color=COLOR_BLUE, sw=1.8, dash="4,3"))
    f.append(arrow(550, 111, 610, 111, color=COLOR_BLUE, sw=2))
    f.append(text(580, 97, "Потік Φ", size=12, bold=True, color=COLOR_BLUE))

    # Магнітний опір осердя Rm
    f.append(text(575, 178, "Опір Rm", size=11, bold=True, color=COLOR_DARK))

    # Пояснення закону Гопкінсона
    b2, w2, h2 = textbox(midx + midx / 2, 275,
                         "F = Φ · Rm  (МРС = Потік · Магн. опір)\n"
                         "• Потік — стан поля (без руху частинок)\n"
                         "• Статичний потік НЕ витрачає енергію!\n"
                         "• μ сталі / μ повітря ≈ 10³...10⁴ (повітря пропускає потік)",
                         size=11, pad=8, fill="#f4f8ff", stroke="#cce0ff", sw=1.2)
    f.append(b2)

    # Нижній висновок
    b_bot, wb, hb = textbox(W / 2, 375,
                            "ГОЛОВНА ВІДМІННІСТЬ: Мобільність зарядів створює витік струму = 0, але магнітне поле завжди витікає у повітря!",
                            size=11, pad=6, fill="#f9f9f9", stroke="#d0d0d0", sw=1.0, bold=True, color=COLOR_DARK)
    f.append(b_bot)

    render(os.path.join(IMG, "magnetic-circuit-analogy.svg"), W, H, *f)


# ── Фігура 2: Повітряний зазор у магнітопроводі ───────────────────────────
def fig_air_gap_fringing():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 26, "Повітряний зазор у магнітопроводі та ефект випучування (Fringing)", size=16, bold=True))

    # Осердя складене з окремих прямокутників без перекриття
    # Ліва вертикальна ніжка
    f.append(rect(60, 70, 50, 200, fill="#eaf2ff", stroke=COLOR_DARK, sw=2, rx=4))
    # Верхня горизонтальна перемичка
    f.append(rect(110, 70, 160, 40, fill="#eaf2ff", stroke=COLOR_DARK, sw=2, rx=0))
    # Нижня горизонтальна перемичка
    f.append(rect(110, 230, 160, 40, fill="#eaf2ff", stroke=COLOR_DARK, sw=2, rx=0))
    # Права верхня ніжка
    f.append(rect(270, 70, 50, 80, fill="#eaf2ff", stroke=COLOR_DARK, sw=2, rx=4))
    # Права нижня ніжка (лишає зазор між Y=150 та Y=190)
    f.append(rect(270, 190, 50, 80, fill="#eaf2ff", stroke=COLOR_DARK, sw=2, rx=4))

    # Випучування магнітних ліній у зазорі (пунктирні стрілки між Y=150 та Y=190)
    f.append(arrow(280, 150, 280, 190, color=COLOR_BLUE, sw=1.6))
    f.append(arrow(295, 150, 295, 190, color=COLOR_BLUE, sw=1.6))
    f.append(arrow(310, 150, 310, 190, color=COLOR_BLUE, sw=1.6))

    # Випуклі стрілки з боків (fringing)
    f.append(arrow(265, 152, 262, 188, color=COLOR_GREEN, sw=1.4))
    f.append(arrow(325, 152, 328, 188, color=COLOR_GREEN, sw=1.4))

    # Позначення повітряного зазору lg
    f.append(line(340, 150, 340, 190, color=COLOR_RED, sw=1.2))
    f.append(line(335, 150, 345, 150, color=COLOR_RED, sw=1.2))
    f.append(line(335, 190, 345, 190, color=COLOR_RED, sw=1.2))
    f.append(text(370, 170, "lg (зазор)", size=12, bold=True, color=COLOR_RED))

    # Позначення обмотки N·I
    f.append(text(85, 170, "N·I", size=12, bold=True, color=COLOR_ORANGE))

    # Позначення потоку Φ
    f.append(arrow(150, 90, 220, 90, color=COLOR_BLUE, sw=2))
    f.append(text(185, 80, "Потік Φ", size=12, bold=True, color=COLOR_BLUE))

    # ПРАВА ЧАСТИНА: Формули та аналіз накопичення енергії
    b_energy, w_e, h_e = textbox(540, 135,
                                 "РОЗПОДІЛ МАГНІТНОГО ОПОРУ:\n"
                                 "• Rm_core = l_core / (μ0 · μr · A)\n"
                                 "• Rm_gap  = lg / (μ0 · A_eff)\n"
                                 "Хоч lg ≈ 1 мм, а l_core ≈ 150 мм, через μr = 2000:\n"
                                 "Rm_gap становить > 93% загального опору!",
                                 size=11, pad=10, fill="#fffef0", stroke="#ffe066", sw=1.4)
    f.append(b_energy)

    b_fringing, w_f, h_f = textbox(540, 260,
                                   "ЕФЕКТ ВИПУЧУВАННЯ (Fringing):\n"
                                   "Магнітні лінії розпираються вбік у зазорі.\n"
                                   "Ефективна площа зазору більша за площу осердя:\n"
                                   "A_eff = (a + lg) · (b + lg) > A_core\n"
                                   "Це трохи зменшує реальний опір зазору.",
                                   size=11, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b_fringing)

    # Нижній підсумок про енергію
    b_sum, ws, hs = textbox(W / 2, 355,
                            "НАКОПИЧЕННЯ ЕНЕРГІЇ: Густина енергії w = B² / (2μ). Оскільки μ_gap << μ_core, 95%+ енергії зберігається у зазорі!",
                            size=11, pad=8, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, bold=True, color=COLOR_PURPLE)
    f.append(b_sum)

    render(os.path.join(IMG, "air-gap-fringing.svg"), W, H, *f)


# ── Фігура 3: Послідовно-паралельне магнітне коло E-осердя ────────────────
def fig_series_parallel_magnetic_circuit():
    W, H = 780, 390
    f = []
    f.append(text(W / 2, 26, "Розгалужене магнітне коло E-подібного осердя", size=16, bold=True))

    # Контур E-подібного осердя без внутрішніх рамкових перекриттів
    f.append(rect(40, 70, 320, 210, fill="#eef4ff", stroke=COLOR_DARK, sw=2.5, rx=8))
    f.append(rect(85, 105, 80, 140, fill=BG, stroke=COLOR_DARK, sw=1.6, rx=3))
    f.append(rect(235, 105, 80, 140, fill=BG, stroke=COLOR_DARK, sw=1.6, rx=3))

    # Позначення обмотки в центрі
    f.append(text(200, 175, "N·I", size=12, bold=True, color=COLOR_ORANGE))

    # Напрямки потоків Φ_center, Φ_left, Φ_right
    f.append(arrow(200, 120, 200, 80, color=COLOR_RED, sw=2))
    f.append(text(200, 68, "Φ_total", size=11, bold=True, color=COLOR_RED))

    f.append(arrow(180, 80, 100, 80, color=COLOR_BLUE, sw=1.8))
    f.append(text(140, 68, "Φ_1", size=11, bold=True, color=COLOR_BLUE))

    f.append(arrow(220, 80, 300, 80, color=COLOR_BLUE, sw=1.8))
    f.append(text(260, 68, "Φ_2", size=11, bold=True, color=COLOR_BLUE))

    # ПРАВА ЧАСТИНА: Еквівалентна магнітна схема
    f.append(text(580, 54, "Еквівалентна магнітна схема", size=13, bold=True, color=COLOR_DARK))

    # Джерело МРС F в центрі
    f.append(circle(580, 170, 20, fill=FILL, stroke=COLOR_ORANGE, sw=2))
    f.append(text(580, 170, "F", size=13, bold=True, color=COLOR_ORANGE))

    # Опір центрального керна Rm_c
    f.append(rect(568, 105, 24, 36, fill="#fdf2e9", stroke=COLOR_ORANGE, sw=1.5, rx=3))
    f.append(text(580, 92, "Rm_c", size=10, bold=True, color=COLOR_ORANGE))
    f.append(line(580, 141, 580, 150, color=LINE, sw=1.8))
    f.append(line(580, 190, 580, 250, color=LINE, sw=1.8))

    # Верхня шина вузла А
    f.append(line(450, 92, 710, 92, color=LINE, sw=2))
    f.append(line(580, 105, 580, 92, color=LINE, sw=2))
    f.append(circle(580, 92, 4, fill=COLOR_DARK, stroke=COLOR_DARK, sw=1))
    f.append(text(595, 84, "Вузол A", size=10, color=MUTED))

    # Ліва вітка (Rm1)
    f.append(line(450, 92, 450, 145, color=LINE, sw=1.8))
    f.append(rect(438, 145, 24, 40, fill="#eef4ff", stroke=COLOR_BLUE, sw=1.6, rx=3))
    f.append(text(420, 165, "Rm1", size=11, bold=True, color=COLOR_BLUE))
    f.append(line(450, 185, 450, 250, color=LINE, sw=1.8))
    f.append(arrow(450, 110, 450, 135, color=COLOR_BLUE, sw=1.5))
    f.append(text(465, 125, "Φ1", size=10, color=COLOR_BLUE))

    # Права вітка (Rm2)
    f.append(line(710, 92, 710, 145, color=LINE, sw=1.8))
    f.append(rect(698, 145, 24, 40, fill="#eef4ff", stroke=COLOR_BLUE, sw=1.6, rx=3))
    f.append(text(732, 165, "Rm2", size=11, bold=True, color=COLOR_BLUE))
    f.append(line(710, 185, 710, 250, color=LINE, sw=1.8))
    f.append(arrow(710, 110, 710, 135, color=COLOR_BLUE, sw=1.5))
    f.append(text(695, 125, "Φ2", size=10, color=COLOR_BLUE))

    # Нижня шина
    f.append(line(450, 250, 710, 250, color=LINE, sw=2))

    # Текстове пояснення законів Кірхгофа
    b_kcl, w_k, h_k = textbox(W / 2, 335,
                              "ЗАКОНИ КІРХГОФА ДЛЯ МАГНІТНОГО КОЛА:\n"
                              "1. Для вузла A: Φ_total = Φ_1 + Φ_2  (Закон збереження потоку: ∇·B = 0)\n"
                              "2. Для замкненого контуру: F = Φ_total · Rm_c + Φ_1 · Rm1",
                              size=11, pad=8, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2)
    f.append(b_kcl)

    render(os.path.join(IMG, "series-parallel-magnetic-circuit.svg"), W, H, *f)


# ── Фігура 4: B-H крива та залежність магнітного опору ─────────────────────
def fig_bh_curve_reluctance():
    W, H = 760, 410
    f = []
    f.append(text(W / 2, 26, "Крива намагнічування B-H та зростання магнітного опору у насиченні", size=16, bold=True))

    # Осі координат для графіку B-H
    ox, oy = 80, 290
    gw, gh = 280, 220

    f.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    f.append(text(ox + gw + 10, oy + 20, "H (А/м)", size=12, bold=True, color=COLOR_DARK))

    f.append(line(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.8))
    f.append(text(ox - 25, oy - gh - 5, "B (Тл)", size=12, bold=True, color=COLOR_DARK))

    # Крива намагнічування B(H) (параболічна/сигмоїдальна лінія)
    path_bh = "M %d %d Q %d %d, %d %d T %d %d" % (
        ox, oy,
        ox + 40, oy - 120,
        ox + 120, oy - 180,
        ox + gw, oy - 200
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_bh, COLOR_BLUE))

    # Точки на кривій: лінійна, коліно, насичення
    f.append(circle(ox + 45, oy - 122, 4, fill=COLOR_GREEN, stroke=COLOR_GREEN, sw=1))
    f.append(text(ox + 60, oy - 132, "1. Лінійна зона (μ_r max)", size=10, bold=True, color=COLOR_GREEN))

    f.append(circle(ox + 120, oy - 180, 4, fill=COLOR_ORANGE, stroke=COLOR_ORANGE, sw=1))
    f.append(text(ox + 135, oy - 165, "2. Коліно", size=10, bold=True, color=COLOR_ORANGE))

    f.append(circle(ox + 230, oy - 196, 4, fill=COLOR_RED, stroke=COLOR_RED, sw=1))
    f.append(text(ox + 200, oy - 208, "3. Глибоке насичення (B_sat)", size=10, bold=True, color=COLOR_RED))

    # РІВЕНЬ B_sat (пунктир)
    f.append(line(ox, oy - 200, ox + gw, oy - 200, color=COLOR_RED, sw=1.2, dash="4,3"))
    f.append(text(ox - 30, oy - 196, "B_sat", size=11, bold=True, color=COLOR_RED))


    # ПРАВИЙ ГРАФІК: Залежність магнітного опору Rm(H)
    rox, roy = 460, 290
    f.append(line(rox, roy, rox + gw + 20, roy, color=LINE, sw=1.8))
    f.append(arrow(rox, roy, rox + gw + 20, roy, color=LINE, sw=1.8))
    f.append(text(rox + gw + 10, roy + 20, "H (А/м)", size=12, bold=True, color=COLOR_DARK))

    f.append(line(rox, roy, rox, roy - gh - 15, color=LINE, sw=1.8))
    f.append(arrow(rox, roy, rox, roy - gh - 15, color=LINE, sw=1.8))
    f.append(text(rox - 30, roy - gh - 5, "Rm (А/Вб)", size=12, bold=True, color=COLOR_DARK))

    # Крива Rm(H): спочатку мала й пласка, потім катастрофічно зростає у насиченні
    path_rm = "M %d %d C %d %d, %d %d, %d %d" % (
        rox, roy - 30,
        rox + 80, roy - 30,
        rox + 150, roy - 50,
        rox + gw, roy - 210
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_rm, COLOR_RED))

    f.append(text(rox + 100, roy - 140, "Катастрофічне\nзростання Rm!", size=11, bold=True, color=COLOR_RED))

    # Текстовий блок під графіками (вужчий, щоб не торкатися бокових меж)
    b_bh_summary = fitbox(60, 335, 640, 50,
                          "ФІЗИЧНИЙ ЕФЕКТ НАСИЧЕННЯ: При B -> B_sat диференціальна проникність μ_diff -> μ0.\n"
                          "Магнітний опір осердя зростає у тисячі разів, перетворюючи феромагнетик на повітря!",
                          size=11, pad=6, fill="#fff0f0", stroke="#ffb3b3", sw=1.2, color=COLOR_RED, bold=True)
    f.append(b_bh_summary)

    render(os.path.join(IMG, "bh-curve-reluctance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_magnetic_circuit_analogy()
    fig_air_gap_fringing()
    fig_series_parallel_magnetic_circuit()
    fig_bh_curve_reluctance()
    print("Figures generated successfully in ./img/")
