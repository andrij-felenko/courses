# -*- coding: utf-8 -*-
"""Фігури до теми «Електромагнітний спектр».
Запуск: python figs.py -> створює SVG у ./img/
Використовує svgkit з теки scripts/"""
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

ACCENT_RF   = "#2563eb"  # Синій (Радіо / НВЧ)
ACCENT_IR   = "#d97706"  # Помаранчевий (ІЧ)
ACCENT_VIS  = "#16a34a"  # Зелений (Видиме)
ACCENT_UV   = "#7c3aed"  # Фіолетовий (УФ)
ACCENT_XRAY = "#dc2626"  # Червоний (Рентген / Гамма)
DARK        = "#0f172a"  # Темний колір для тексту й осей
WHITE       = "#ffffff"

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Шкала електромагнітного спектра ─────────────────────────────────
def fig_spectrum_scale():
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Електромагнітний спектр: від радіохвиль до гамма-променів", size=16, bold=True))

    # Спектральна смуга (основна горизонтальна вісь)
    x0, y0 = 60, 160
    band_w = 700
    band_h = 44

    # Діапазони: (назва, x_start, width, color, fill_color)
    bands = [
        ("Радіохвилі", 0, 140, ACCENT_RF, "#dbeafe"),
        ("Мікрохвилі", 140, 100, "#0284c7", "#e0f2fe"),
        ("Інфрачервоне", 240, 110, ACCENT_IR, "#fef3c7"),
        ("Оптика", 350, 60, ACCENT_VIS, "#dcfce7"),
        ("Ультрафіолет", 410, 90, ACCENT_UV, "#f3e8ff"),
        ("Рентген", 500, 100, ACCENT_XRAY, "#fee2e2"),
        ("Гамма", 600, 100, "#991b1b", "#fce7f3"),
    ]

    for bname, bx, bw, bcol, bfill in bands:
        f.append(rect(x0 + bx, y0, bw, band_h, fill=bfill, stroke=bcol, sw=1.5, rx=3))
        f.append(text(x0 + bx + bw / 2, y0 + 26, bname, size=11, color=bcol, bold=True))

    # Окремий винос для видимого світла (оптичний веселковий розріз)
    rx0, ry0 = x0 + 350, y0 + band_h + 10
    f.append(line(rx0 + 30, y0 + band_h, rx0 - 20, ry0 + 30, color=ACCENT_VIS, sw=1, dash="3,3"))
    f.append(line(rx0 + 60, y0 + band_h, rx0 + 120, ry0 + 30, color=ACCENT_VIS, sw=1, dash="3,3"))

    # Панель розширення видимого світла
    f.append(rect(rx0 - 25, ry0 + 30, 150, 48, fill="#ffffff", stroke=ACCENT_VIS, sw=1.5, rx=6))
    f.append(text(rx0 + 50, ry0 + 46, "Видиме світло (380–780 нм)", size=11, color=ACCENT_VIS, bold=True))

    # Градієнт кольорів очі/веселка
    rainbow_colors = ["#7c3aed", "#2563eb", "#0284c7", "#16a34a", "#eab308", "#d97706", "#dc2626"]
    rw = 135 / len(rainbow_colors)
    for i, rc in enumerate(rainbow_colors):
        f.append(rect(rx0 - 18 + i * rw, ry0 + 56, rw, 14, fill=rc, stroke='none'))

    # Шкала частоти f (Гц) зверху
    f.append(arrow(x0, y0 - 30, x0 + band_w + 20, y0 - 30, color=DARK, sw=1.8))
    f.append(text(x0 + band_w + 30, y0 - 26, "f (Гц)", size=12, color=DARK, bold=True))

    freq_marks = [
        ("10³", 0), ("10⁶", 100), ("10⁹", 200), ("10¹²", 300),
        ("10¹⁵", 420), ("10¹⁸", 520), ("10²¹", 640)
    ]
    for label, fx in freq_marks:
        f.append(line(x0 + fx, y0 - 35, x0 + fx, y0 - 25, color=DARK, sw=1.5))
        f.append(text(x0 + fx, y0 - 42, label, size=11, color=DARK))

    # Шкала довжини хвилі λ (м) знизу
    f.append(arrow(x0 + band_w + 20, y0 + 135, x0, y0 + 135, color=DARK, sw=1.8))
    f.append(text(x0 - 25, y0 + 139, "λ (м)", size=12, color=DARK, bold=True))

    wave_marks = [
        ("10³ м", 0), ("1 м", 100), ("1 мм", 200), ("1 мкм", 300),
        ("1 нм", 430), ("1 пм", 540), ("1 фм", 650)
    ]
    for label, wx in wave_marks:
        f.append(line(x0 + wx, y0 + 130, x0 + wx, y0 + 140, color=DARK, sw=1.5))
        f.append(text(x0 + wx, y0 + 154, label, size=11, color=DARK))

    # Шкала енергії фотона E = hf (еВ) на самій низу
    f.append(text(W / 2, y0 + 195, "Енергія фотона E = hf:  10⁻⁹ еВ (радіо)  →  1 еВ (оптика)  →  10⁶ еВ (гамма)", size=12, color=MUTED, bold=True))

    # Об'єкти порівняння масштабу (іконки/текстові підписи над/під смугою)
    scales = [
        ("Будинки / Комахи", 70, y0 - 75),
        ("Молекули", 310, y0 - 75),
        ("Атоми", 510, y0 - 75),
        ("Ядра атомів", 640, y0 - 75)
    ]
    for stext, sx, sy in scales:
        b, bw, bh = textbox(sx, sy, stext, size=10, pad=4, fill="#f8fafc", stroke=MUTED, sw=1)
        f.append(b)

    return render(os.path.join(IMG_DIR, "spectrum-scale.svg"), W, H, *f)


# ── Фігура 2: Зміна фізичних механізмів уздовж спектра ────────────────────────
def fig_band_mechanisms():
    W, H = 780, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Зміна фізичних механізмів взаємодії випромінювання з речовиною", size=16, bold=True))

    # Стрілка наростання частоти й квантових ефектів
    f.append(arrow(60, 65, 720, 65, color=DARK, sw=2.5))
    f.append(text(390, 50, "Частота f  /  Енергія фотона E = hf  ▲", size=12, color=DARK, bold=True))

    # 4 основних блоки механізмів
    col_w = 155
    cols = [
        ("Класичне радіо\n(E < 1 meV)", "Макроскопічні струми\nв антенах, огинання\nперешкод, класична\nелектродинаміка", ACCENT_RF, "#eff6ff"),
        ("Теплове й молекулярне\n(1 meV – 1.5 eV)", "Обертання й коливання\nмолекул, випромінювання\nнагрітих тіл, ІЧ-зв'язок", ACCENT_IR, "#fffbeb"),
        ("Атомні переходи\n(1.5 eV – 100 eV)", "Збудження валентних\nелектронів, фотоефект,\nхімічні реакції, UV-C", ACCENT_UV, "#f3e8ff"),
        ("Іонізуюче & ядерне\n(E > 100 eV)", "Вибивання K-електронів,\nгальмівне рентгенівське,\nядерні розпади, гамма", ACCENT_XRAY, "#fef2f2")
    ]

    for i, (htitle, hdesc, ccol, cfill) in enumerate(cols):
        cx = 60 + i * (col_w + 15)
        cy = 90
        # Контейнер для колонки
        f.append(rect(cx, cy, col_w, 240, fill=cfill, stroke=ccol, sw=1.8, rx=8))
        # Заголовок колонки
        f.append(rect(cx, cy, col_w, 55, fill=ccol, stroke='none', rx=8))
        # Сплатимо кути знизу
        f.append(rect(cx, cy + 30, col_w, 25, fill=ccol, stroke='none'))

        # Текст заголовка (білий)
        lines = htitle.split('\n')
        f.append(text(cx + col_w / 2, cy + 22, lines[0], size=11, color=WHITE, bold=True))
        if len(lines) > 1:
            f.append(text(cx + col_w / 2, cy + 40, lines[1], size=10, color=WHITE))

        # Опис механізму
        dlines = hdesc.split('\n')
        for dy_idx, dline in enumerate(dlines):
            f.append(text(cx + col_w / 2, cy + 85 + dy_idx * 20, dline, size=11, color=DARK))

    # Нижній орієнтир: Неіонізуюче проти Іонізуючого
    f.append(rect(60, 345, 325, 45, fill="#e0f2fe", stroke=ACCENT_RF, sw=1.5, rx=6))
    f.append(text(222, 372, "Неіонізуюче випромінювання (безпечне)", size=12, color=ACCENT_RF, bold=True))

    f.append(rect(400, 345, 320, 45, fill="#fee2e2", stroke=ACCENT_XRAY, sw=1.5, rx=6))
    f.append(text(560, 372, "Іонізуюче випромінювання (руйнує ДНК)", size=12, color=ACCENT_XRAY, bold=True))

    return render(os.path.join(IMG_DIR, "band-mechanisms.svg"), W, H, *f)


# ── Фігура 3: Прозорість атмосфери Землі ──────────────────────────────────────
def fig_atmosphere_windows():
    W, H = 780, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Профіль непрозорості атмосфери Землі для електромагнітних хвиль", size=16, bold=True))

    # Осі
    gx0, gy0 = 70, 80
    gw, gh = 660, 230

    # Задній фон графіка
    f.append(rect(gx0, gy0, gw, gh, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=4))

    # Крива непрозорості (0% = повністю прозоро, 100% = непрозоро)
    # Побудуємо плавну лінію через ключові точки:
    # Гамма/Рентген (100% непрозоро), УФ (50-100%), Оптика (0% прозоро!), ІЧ (сильні смуги H2O/CO2 50-100%), НВЧ/Радіо (0% прозоро!), НЧ Радіо (100% іоносфера)
    path_d = [
        f"M {gx0},{gy0 + 10}",  # Гамма/Рентген: 100% непрозоро
        f"L {gx0 + 100},{gy0 + 10}",
        f"L {gx0 + 150},{gy0 + 80}",  # УФ-ближній: спад
        f"L {gx0 + 180},{gy0 + gh - 10}",  # Оптичне вікно (0% непрозоро)
        f"L {gx0 + 240},{gy0 + gh - 10}",
        f"L {gx0 + 270},{gy0 + 60}",  # ІЧ поглинання H2O/CO2
        f"L {gx0 + 300},{gy0 + 160}",
        f"L {gx0 + 330},{gy0 + 40}",
        f"L {gx0 + 380},{gy0 + gh - 10}",  # Радіовікно починається (0% непрозоро)
        f"L {gx0 + 550},{gy0 + gh - 10}",  # Радіовікно простягається
        f"L {gx0 + 600},{gy0 + 30}",  # Іоносферне відбивання (>100м)
        f"L {gx0 + gw},{gy0 + 10}"
    ]
    path_str = " ".join(path_d)

    # Заповнення області непрозорості
    fill_path = path_str + f" L {gx0 + gw},{gy0 + gh} L {gx0},{gy0 + gh} Z"
    f.append(f'<path d="{fill_path}" fill="#94a3b8" fill-opacity="0.25" stroke="none"/>')
    f.append(f'<path d="{path_str}" fill="none" stroke="{DARK}" stroke-width="2.8"/>')

    # Підписи вікон прозорості
    # 1. Оптичне вікно
    f.append(rect(gx0 + 172, gy0 + gh - 90, 76, 75, fill="#dcfce7", stroke=ACCENT_VIS, sw=1.5, rx=4))
    f.append(text(gx0 + 210, gy0 + gh - 65, "Оптичне\nвікно", size=11, color=ACCENT_VIS, bold=True))

    # 2. Радіовікно
    f.append(rect(gx0 + 390, gy0 + gh - 90, 150, 75, fill="#dbeafe", stroke=ACCENT_RF, sw=1.5, rx=4))
    f.append(text(gx0 + 465, gy0 + gh - 65, "Радіовікно\n(15 МГц – 30 ГГц)", size=11, color=ACCENT_RF, bold=True))

    # Позначки причин поглинання
    f.append(text(gx0 + 50, gy0 + 45, "Поглинання\nN₂, O₂, O₃", size=10, color=ACCENT_XRAY))
    f.append(text(gx0 + 300, gy0 + 30, "Поглинання\nH₂O та CO₂", size=10, color=ACCENT_IR))
    f.append(text(gx0 + 600, gy0 + 45, "Відбивання\nіоносферою", size=10, color="#7c3aed"))

    # Осі координат підписи
    f.append(text(gx0 - 15, gy0 + 20, "100%", size=10, color=MUTED))
    f.append(text(gx0 - 15, gy0 + gh - 10, "0%", size=10, color=MUTED))
    f.append(text(gx0 - 45, gy0 + gh / 2, "Непрозорість", size=11, color=DARK, bold=True))

    # Шкала довжин хвиль під графіком
    band_labels = [
        ("Гамма / Рентген", gx0 + 40),
        ("УФ", gx0 + 140),
        ("Видиме", gx0 + 210),
        ("ІЧ", gx0 + 300),
        ("Мікрохвилі / Радіо", gx0 + 465),
        ("НЧ Радіо", gx0 + 610)
    ]
    for blabel, bx in band_labels:
        f.append(line(bx, gy0 + gh, bx, gy0 + gh + 6, color=MUTED, sw=1))
        f.append(text(bx, gy0 + gh + 22, blabel, size=10, color=DARK))

    return render(os.path.join(IMG_DIR, "atmosphere-windows.svg"), W, H, *f)


# ── Фігура 4: Проникна здатність та скін-ефект ────────────────────────────────
def fig_scattering_penetration():
    W, H = 780, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Проникність матеріалів та скін-ефект залежно від частоти", size=16, bold=True))

    # Ліва панель: Скін-ефект у провідниках (Метали)
    f.append(rect(40, 60, 335, 310, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(207, 85, "Скін-ефект у провіднику (Мідь)", size=13, color=DARK, bold=True))

    # Провідник квадратний переріз
    f.append(rect(100, 115, 215, 180, fill="#fed7aa", stroke="#c2410c", sw=2, rx=4))
    # Скін-шар високої частоти (повільно затухає вглиб)
    f.append(rect(100, 115, 215, 180, fill="none", stroke=ACCENT_RF, sw=12, rx=4))
    f.append(text(207, 140, "Струм протікає лише у тонкому\nповерхневому шарі δ", size=11, color=ACCENT_RF, bold=True))

    # Формула скін-шару
    b1, w1, h1 = textbox(207, 240, "Формула скін-шару:\nδ = √( 2 / (ω·μ·σ) )\n50 Гц: δ ≈ 9.3 мм\n1 ГГц: δ ≈ 2 мкм\nОптика: повністю непрозоре дзеркало", size=10, pad=5, fill="#fff7ed", stroke="#c2410c", sw=1.2)
    f.append(b1)

    # Права панель: Проникність у діелектриках та тканинах (Рентген / Гамма)
    f.append(rect(405, 60, 335, 310, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(572, 85, "Проникність для іонізуючих квантів", size=13, color=DARK, bold=True))

    # Об'єкт (м'які тканини + кістка)
    f.append(rect(460, 115, 220, 180, fill="#e2e8f0", stroke=DARK, sw=1.5, rx=6))
    f.append(rect(530, 135, 80, 140, fill="#94a3b8", stroke=DARK, sw=1.5, rx=4))
    f.append(text(570, 205, "Кістка\n(Z високе)", size=10, color=WHITE, bold=True))
    f.append(text(490, 205, "М'які\nтканини", size=10, color=DARK))

    # Проходження променів
    # Рентген проходить м'які тканини, затримується кісткою
    f.append(arrow(420, 145, 695, 145, color=ACCENT_XRAY, sw=2))
    f.append(text(440, 132, "Рентген", size=10, color=ACCENT_XRAY, bold=True))

    # Поглинання в кістці
    f.append(line(420, 205, 530, 205, color=ACCENT_XRAY, sw=2, dash="4,4"))
    f.append(text(440, 192, "Поглинається", size=10, color=ACCENT_XRAY))

    # Гамма проходить усе
    f.append(arrow(420, 265, 715, 265, color="#991b1b", sw=2.5))
    f.append(text(440, 252, "Гамма (висока E)", size=10, color="#991b1b", bold=True))

    # Пояснення фотоефекту
    b2, w2, h2 = textbox(572, 325, "Фотоефект поглинання: σ ∝ Z⁴ / E³\nРентген відображає кістки (кальцій, Z=20)\nГамма пробиває бетон та сталь", size=10, pad=5, fill="#fee2e2", stroke=ACCENT_XRAY, sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG_DIR, "scattering-penetration.svg"), W, H, *f)


def main():
    fig_spectrum_scale()
    fig_band_mechanisms()
    fig_atmosphere_windows()
    fig_scattering_penetration()
    print("Всі 4 фігури успішно згенеровано у ./img/")


if __name__ == "__main__":
    main()
