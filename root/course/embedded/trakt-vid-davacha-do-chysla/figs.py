# -*- coding: utf-8 -*-
"""Фігури до кроку «Тракт від давача до числа».
Запуск: python figs.py  → генерує SVG у ./img/
Використовує svgkit із ../../../../scripts/svgkit.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ───────────────────── 1. Повний тракт AFE (5 ланок) ─────────────────────────
def fig_afe_pipeline():
    w, h = 860, 360
    f = []
    f.append(text(w / 2, 24, "Анатомія аналогово-цифрового тракту: 5 ланок перетворення", size=16, bold=True))

    stages = [
        ("1. Давач", "Тензоміст / RTD\nΔV: ±10 мВ\nЗсув: 2.5 В\nШум: 50 Гц", 30, "#eef2ff", NEG),
        ("2. Кондиціювання", "In-Amp + Level Shift\nПідсилення G=150\nCMRR > 90 дБ\nЗсув на Vref/2", 195, "#f0fdf4", FIELD),
        ("3. Фільтр (AAF)", "Аналоговий ФНЧ\nfc < fs / 2\nЗрізання завад\nЗахист спектра", 360, "#fefce8", "#ca8a04"),
        ("4. АЦП (ADC)", "SAR / Sigma-Delta\nВибірка-зберігання\nКвантування\nОпора Vref", 525, "#fff1f2", POS),
        ("5. Обробка в МК", "Калібрування\nФільтрація (EMA)\nМасштабування\nФізичне число", 690, "#f3f4f6", INK),
    ]

    bw, bh = 140, 110
    top_y = 60

    for i, (title, desc, x, bg_col, border_col) in enumerate(stages):
        f.append(rect(x, top_y, bw, bh, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        f.append(text(x + bw / 2, top_y + 20, title, size=12.5, bold=True, color=border_col))
        lines = desc.split("\n")
        for j, line_txt in enumerate(lines):
            f.append(text(x + bw / 2, top_y + 42 + j * 16, line_txt, size=10.5, color=INK))

        if i < len(stages) - 1:
            arrow_start_x = x + bw + 2
            arrow_end_x = stages[i+1][2] - 4
            arrow_y = top_y + bh / 2
            f.append(arrow(arrow_start_x, arrow_y, arrow_end_x, arrow_y, color=LINE, sw=1.8))

    # Нижній ряд: що відбувається з сигналом на кожному етапі
    f.append(text(w / 2, 200, "Трансформація форми сигналу на кожному етапі:", size=13, bold=True, color=LINE))

    sig_boxes = [
        ("Мікровольти на тлі 2.5 В", 30, [
            (0, 40), (20, 38), (40, 42), (60, 39), (80, 41), (100, 40), (120, 39), (140, 41)
        ], "±10 мВ + завада"),
        ("Підсилений 0.15..3.15 В", 195, [
            (0, 50), (20, 20), (40, 70), (60, 25), (80, 65), (100, 30), (120, 60), (140, 40)
        ], "G·ΔV навколо 1.65 В"),
        ("Згладжений без ВЧ", 360, [
            (0, 45), (20, 35), (40, 55), (60, 30), (80, 50), (100, 38), (120, 46), (140, 42)
        ], "Смуга < fs/2"),
        ("Сходинки квантування", 525, [
            (0, 45), (25, 45), (25, 35), (55, 35), (55, 55), (85, 55), (85, 40), (115, 40), (115, 42), (140, 42)
        ], "12/16/24 біти"),
        ("Чисте фізичне значення", 690, [
            (0, 42), (140, 42)
        ], "«25.40 кг» у пам'яті"),
    ]

    sig_y = 220
    sig_h = 90
    for title, x, pts, note in sig_boxes:
        f.append(rect(x, sig_y, bw, sig_h, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=4))
        f.append(text(x + bw / 2, sig_y + 16, title, size=10, bold=True, color=MUTED))

        poly_pts = []
        for px, py in pts:
            gx = x + 10 + px * ((bw - 20) / 140)
            gy = sig_y + 24 + py * 0.45
            poly_pts.append(f"{gx:.1f},{gy:.1f}")
        f.append(f'<polyline points="{" ".join(poly_pts)}" fill="none" stroke="{POS}" stroke-width="2"/>')
        f.append(text(x + bw / 2, sig_y + sig_h - 8, note, size=10, color=INK, bold=False))

    f.append(text(w / 2, 345, "Кожна ланка усуває фізичне обмеження попередньої: слабкість → шум → аліасинг → неперервність → похибки.", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "afe-pipeline.svg"), w, h, *f)


# ───────────────────── 2. In-Amp та зміщення рівня ────────────────────────────
def fig_inamp_levelshift():
    w, h = 820, 380
    f = []
    f.append(text(w / 2, 24, "Трьохопераційний інструментальний підсилювач зі зміщенням рівня", size=16, bold=True))

    f.append(rect(40, 60, 740, 270, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # ОП1 (Верхній)
    f.append(rect(180, 80, 100, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(230, 115, "ОП 1", size=13, bold=True))
    f.append(text(230, 133, "Буфер IN+", size=10.5, color=MUTED))

    # ОП2 (Нижній)
    f.append(rect(180, 220, 100, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(230, 255, "ОП 2", size=13, bold=True))
    f.append(text(230, 273, "Буфер IN−", size=10.5, color=MUTED))

    # Резистор Rg між ними
    f.append(line(230, 150, 230, 170, color=LINE, sw=1.5))
    f.append(rect(215, 170, 30, 30, fill="#fef08a", stroke=LINE, sw=1.5, rx=2))
    f.append(text(230, 190, "Rg", size=12, bold=True, color=POS))
    f.append(line(230, 200, 230, 220, color=LINE, sw=1.5))
    f.append(text(285, 190, "Задає G", size=10.5, color=POS, bold=True))

    # Входи зліва
    f.append(arrow(70, 115, 180, 115, color=POS, sw=2))
    f.append(text(120, 105, "IN+ (2.510 В)", size=11, bold=True, color=POS))
    f.append(arrow(70, 255, 180, 255, color=NEG, sw=2))
    f.append(text(120, 275, "IN− (2.490 В)", size=11, bold=True, color=NEG))
    f.append(text(120, 190, "ΔV = +20 мВ\nVcm = 2.5 В", size=11, bold=True, color=INK))

    # Зв'язок до вихідного ОП3
    f.append(arrow(280, 115, 470, 160, color=LINE, sw=1.5))
    f.append(text(370, 125, "R1", size=11, color=MUTED))
    f.append(arrow(280, 255, 470, 200, color=LINE, sw=1.5))
    f.append(text(370, 240, "R1", size=11, color=MUTED))

    # ОП3 (Віднімач)
    f.append(rect(470, 140, 120, 90, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    f.append(text(530, 175, "ОП 3", size=14, bold=True))
    f.append(text(530, 195, "Різницевий", size=11, color=MUTED))
    f.append(text(530, 212, "віднімач (R2/R1)", size=10, color=MUTED))

    # Вивід REF (зміщення рівня)
    f.append(arrow(530, 310, 530, 230, color=FIELD, sw=2))
    f.append(rect(470, 280, 120, 35, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(530, 298, "Вхід REF = Vref / 2", size=11, bold=True, color=FIELD))
    f.append(text(530, 325, "(Штучна середина 1.65 В)", size=10, color=FIELD))

    # Вихід на АЦП
    f.append(arrow(590, 185, 740, 185, color=POS, sw=2.5))
    f.append(rect(620, 130, 140, 45, fill="#eff6ff", stroke=POS, sw=1.5, rx=4))
    f.append(text(690, 148, "Vout = G·ΔV + Vref/2", size=11, bold=True, color=POS))
    f.append(text(690, 165, "1.65 В ± 1.5 В (0.15..3.15 В)", size=10, color=INK))

    f.append(text(w / 2, 355, "Синфазна напруга 2.5 В повністю віднімається, а різниця ±10 мВ підсилюється і центрується в діапазоні АЦП 0..3.3 В.", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "inamp-cmrr-levelshift.svg"), w, h, *f)


# ───────────────────── 3. Антиаліасинг у частотній області ────────────────────
def fig_aliasing_spectrum():
    w, h = 820, 390
    f = []
    f.append(text(w / 2, 24, "Накладання спектрів: чому аліасинг неможливо усунути програмно", size=16, bold=True))

    # Ліва панель: БЕЗ Фільтра
    pw = 360
    top_y = 60
    bot_y = 265
    f.append(rect(30, top_y, pw, 265, fill="#fffafb", stroke=POS, sw=1.5, rx=6))
    f.append(text(30 + pw / 2, top_y + 22, "1. Без антиаліасингового фільтра", size=13, bold=True, color=POS))

    # Осі лівої панелі
    lx0, ly0 = 50, bot_y - 25
    f.append(line(lx0, ly0, lx0 + 320, ly0, color=LINE, sw=1.5))
    f.append(line(lx0, ly0, lx0, top_y + 45, color=LINE, sw=1.5))
    f.append(text(lx0 + 320, ly0 + 18, "Частота f →", size=10.5, color=MUTED, anchor="end"))
    f.append(text(lx0 - 5, top_y + 50, "A", size=11, color=MUTED, anchor="end"))

    # Смуга корисного сигналу (0..fmax)
    # Малюємо як полігон без обводки, щоб не перетинати текст
    f.append(f'<polygon points="{lx0},{ly0} {lx0},{ly0-90} {lx0+65},{ly0-90} {lx0+65},{ly0}" fill="#22c55e" opacity="0.35"/>')
    f.append(text(lx0 + 32, ly0 - 45, "Сигнал\nf ≤ fmax", size=10.5, bold=True, color=FIELD))
    f.append(text(lx0 + 65, ly0 + 14, "fmax", size=10.5, color=FIELD))

    # Лінія Найквіста fs/2
    fn_x = lx0 + 140
    f.append(line(fn_x, ly0, fn_x, top_y + 80, color=POS, sw=2, dash="4,3"))
    f.append(text(fn_x, ly0 + 14, "fs / 2", size=10.5, bold=True, color=POS))

    # Високочастотна завада (біля fs)
    fnoise_x = lx0 + 240
    f.append(f'<polygon points="{fnoise_x-12},{ly0} {fnoise_x-12},{ly0-85} {fnoise_x+12},{ly0-85} {fnoise_x+12},{ly0}" fill="#ef4444" opacity="0.4"/>')
    f.append(text(fnoise_x, ly0 - 95, "ВЧ шум", size=10.5, bold=True, color=POS))
    f.append(text(fnoise_x, ly0 + 14, "f_noise", size=10.5, color=POS))

    # Стрілка відбиття (дзеркало)
    f.append(f'<path d="M {fnoise_x} {ly0 - 85} Q {fn_x} {top_y + 60} {lx0 + 40} {ly0 - 85}" fill="none" stroke="{POS}" stroke-width="2.2" stroke-dasharray="3,3" marker-end="url(#arrow)"/>')
    f.append(text(fn_x, top_y + 52, "Відбиття в робочу смугу!", size=10.5, bold=True, color=POS))

    f.append(fitbox(45, bot_y + 8, pw - 30, 44, "Шум став на частоту fin = fs − fnoise.\nУ пам'яті МК це фальшивий корисний сигнал.", size=10.5, fill="#fee2e2", stroke=POS))

    # Права панель: З Фільтром AAF
    rx = 430
    f.append(rect(rx, top_y, pw, 265, fill="#f9fdfa", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(rx + pw / 2, top_y + 22, "2. З аналоговим ФНЧ перед АЦП", size=13, bold=True, color=FIELD))

    # Осі правої панелі
    rx0, ry0 = rx + 20, bot_y - 25
    f.append(line(rx0, ry0, rx0 + 320, ry0, color=LINE, sw=1.5))
    f.append(line(rx0, ry0, rx0, top_y + 45, color=LINE, sw=1.5))
    f.append(text(rx0 + 320, ry0 + 18, "Частота f →", size=10.5, color=MUTED, anchor="end"))
    f.append(text(rx0 - 5, top_y + 50, "A", size=11, color=MUTED, anchor="end"))

    # Смуга корисного сигналу
    f.append(f'<polygon points="{rx0},{ry0} {rx0},{ry0-90} {rx0+65},{ry0-90} {rx0+65},{ry0}" fill="#22c55e" opacity="0.35"/>')
    f.append(text(rx0 + 32, ry0 - 45, "Сигнал\nпроходить", size=10.5, bold=True, color=FIELD))
    f.append(text(rx0 + 65, ry0 + 14, "fmax", size=10.5, color=FIELD))

    # Лінія Найквіста
    rfn_x = rx0 + 140
    f.append(line(rfn_x, ry0, rfn_x, top_y + 55, color=POS, sw=2, dash="4,3"))
    f.append(text(rfn_x, ry0 + 14, "fs / 2", size=10.5, bold=True, color=POS))

    # АЧХ фільтра ФНЧ (зелена спадна крива)
    pts_filter = [
        (rx0, ry0 - 100), (rx0 + 60, ry0 - 98), (rx0 + 90, ry0 - 80),
        (rx0 + 140, ry0 - 45), (rx0 + 200, ry0 - 12), (rx0 + 300, ry0 - 4)
    ]
    fpoly = " ".join([f"{px:.1f},{py:.1f}" for px, py in pts_filter])
    f.append(f'<polyline points="{fpoly}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    f.append(text(rx0 + 100, ry0 - 90, "АЧХ ФНЧ", size=11, bold=True, color=FIELD))

    # Ослаблений ВЧ шум
    rfnoise_x = rx0 + 240
    f.append(f'<polygon points="{rfnoise_x-12},{ry0} {rfnoise_x-12},{ry0-10} {rfnoise_x+12},{ry0-10} {rfnoise_x+12},{ry0}" fill="#9ca3af" opacity="0.6"/>')
    f.append(text(rfnoise_x, ry0 - 18, "Задушений шум", size=10, color=MUTED))
    f.append(text(rfnoise_x, ry0 + 14, "f_noise", size=10.5, color=MUTED))

    f.append(fitbox(rx + 15, bot_y + 8, pw - 30, 44, "Фільтр зрізає енергію завади ДО оцифрування.\nСпектр чистий, аліасингу немає.", size=10.5, fill="#dcfce7", stroke=FIELD))

    f.append(text(w / 2, 365, "Теорема Найквіста-Котельникова вимагає ослаблення завади до рівня молодшого розряду LSB на частоті fs/2.", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "aliasing-spectrum.svg"), w, h, *f)


# ───────────────────── 4. Двоточкове калібрування ────────────────────────────
def fig_two_point_calibration():
    w, h = 820, 380
    f = []
    f.append(text(w / 2, 24, "Двоточкове калібрування: компенсація нульового зсуву та похибки нахилу", size=16, bold=True))

    ox, oy = 90, 310
    gw, gh = 440, 240

    # Сітка та осі графіка
    f.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke="#e5e7eb", sw=1, rx=4))
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.8))
    f.append(text(ox + gw - 10, oy + 24, "Фізична величина (кг, °C, кПа) →", size=11, color=LINE, anchor="end"))
    f.append(text(ox - 10, oy - gh + 15, "Код АЦП (N_adc) ↑", size=11, color=LINE, anchor="end"))

    # Точки калібрування x1, x2 на осі X
    x1_px = ox + 80
    x2_px = ox + 360
    f.append(line(x1_px, oy, x1_px, oy - gh, color="#cbd5e1", sw=1, dash="3,3"))
    f.append(line(x2_px, oy, x2_px, oy - gh, color="#cbd5e1", sw=1, dash="3,3"))
    f.append(text(x1_px, oy + 16, "P1 (Нуль / Тара)", size=10.5, bold=True, color=LINE))
    f.append(text(x2_px, oy + 16, "P2 (Еталонна вага)", size=10.5, bold=True, color=LINE))

    # Ідеальна характеристика (зелена лінія з 0,0)
    f.append(line(ox, oy, ox + 400, oy - 200, color=FIELD, sw=2, dash="5,4"))
    f.append(text(ox + 405, oy - 195, "Ідеальна пряма (Y = k0·X)", size=10.5, color=FIELD, bold=True))

    # Реальна сира характеристика (червона лінія зі зсувом b0 і нахилом k_real)
    y1_raw = oy - 60
    y2_raw = oy - 220
    f.append(line(ox, oy - 30, ox + 400, oy - 235, color=POS, sw=2.5))
    f.append(text(ox + 405, oy - 235, "Реальна сира (N_raw = k·X + Offset)", size=10.5, color=POS, bold=True))

    # Зсув нуля (Offset) на осі Y
    f.append(arrow(ox - 30, oy, ox - 30, oy - 30, color=POS, sw=1.5))
    f.append(arrow(ox - 30, oy - 30, ox - 30, oy, color=POS, sw=1.5))
    f.append(text(ox - 35, oy - 15, "Зсув нуля (Offset)", size=10, bold=True, color=POS, anchor="end"))

    # Точки вимірювань (P1_raw, P2_raw)
    f.append(circle(x1_px, y1_raw, 5, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(x1_px - 8, y1_raw - 10, "Точка 1 (X1, N1)", size=10.5, bold=True, color=POS, anchor="end"))

    f.append(circle(x2_px, y2_raw, 5, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(x2_px - 8, y2_raw - 10, "Точка 2 (X2, N2)", size=10.5, bold=True, color=POS, anchor="end"))

    # Права панель з формулами та розрахунком
    rx = 560
    f.append(rect(rx, 60, 230, 260, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(rx + 115, 85, "Формули калібрування", size=13, bold=True, color=LINE))

    calc_lines = [
        "1. Чутливість (Gain / Slope):",
        "   k = (N2 − N1) / (X2 − X1)",
        "",
        "2. Зсув нуля (Offset):",
        "   N0 = N1 − k · X1",
        "",
        "3. Відновлення величини:",
        "   X = (N_raw − N0) / k",
        "   X = (N_raw − N1)·(X2−X1)",
        "       / (N2 − N1) + X1"
    ]
    for i, cl in enumerate(calc_lines):
        bold_flag = cl.startswith("1.") or cl.startswith("2.") or cl.startswith("3.")
        col = POS if bold_flag else INK
        f.append(text(rx + 15, 115 + i * 16, cl, size=10, color=col, bold=bold_flag, anchor="start"))

    f.append(text(w / 2, 355, "Дві калібрувальні точки повністю компенсують адитивну (Offset) та мультиплікативну (Gain) похибки вимірювального тракту.", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-point-calibration.svg"), w, h, *f)


if __name__ == "__main__":
    fig_afe_pipeline()
    fig_inamp_levelshift()
    fig_aliasing_spectrum()
    fig_two_point_calibration()
    print("Всі 4 фігури згенеровано успішно.")
