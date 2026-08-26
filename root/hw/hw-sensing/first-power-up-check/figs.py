# -*- coding: utf-8 -*-
"""Фігури до теми «Перша перевірка (First Power-Up & Bring-Up)».
Запуск: python figs.py -> генерує SVG у ./img/
Спільні помічники: scripts/svgkit.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Холодний візуальний контроль під мікроскопом: 4 типові дефекти ────────
def fig_cold_defects():
    W, H = 960, 480
    f = [text(W / 2, 28, "Холодний візуальний контроль: чотири типові дефекти монтажу",
              size=16, bold=True)]

    panels = [
        ("Місток припою (QFN/LQFP)",
         "Злипання сусідніх виводів:\nкоротке замикання шини живлення\nна землю або сигнальну лінію.",
         POS),
        ("Полярність танталового C",
         "Смужка на танталі — АНОД (+).\nЗворотне ввімкнення веде до\nпробою, спалаху й закоротки.",
         POS),
        ("«Надгробний камінь» (0402)",
         "Нерівномірний прогрів пасти:\nелемент підвівся на один вивід,\nланцюг розірвано (обрив).",
         "#b8860b"),
        ("Кулька припою під IC",
         "Залишок пасти під черевом QFN:\nвипадкове замикання підкладки\n(Thermal Pad) на сусідній пін.",
         POS),
    ]

    pw, ph = 210, 370
    gap = 20
    x0 = (W - (4 * pw + 3 * gap)) / 2
    y0 = 60

    for i, (title_text, desc, accent) in enumerate(panels):
        px = x0 + i * (pw + gap)
        # Фон панелі
        f.append(rect(px, y0, pw, ph, fill="#fafbfc", stroke=LINE, sw=1.4, rx=8))
        # Заголовок панелі
        f.append(rect(px, y0, pw, 38, fill="#edf2f7", stroke=LINE, sw=1.4, rx=8))
        f.append(rect(px, y0 + 26, pw, 12, fill="#edf2f7", stroke="#edf2f7", sw=0))
        f.append(line(px, y0 + 38, px + pw, y0 + 38, color=LINE, sw=1.4))
        f.append(text(px + pw / 2, y0 + 24, title_text, size=11, bold=True, color=INK))

        # Графічна ілюстрація всередині панелі
        cx = px + pw / 2
        cy = y0 + 130

        if i == 0:
            # Місток припою
            f.append(rect(cx - 70, cy - 35, 140, 50, fill="#2c3e50", stroke=INK, sw=1.5, rx=4))
            f.append(text(cx, cy - 10, "Корпус QFN", size=10.5, color="#ffffff", bold=True))
            # Ніжки
            for pin_x in [cx - 45, cx - 15, cx + 15, cx + 45]:
                f.append(rect(pin_x - 7, cy + 15, 14, 20, fill="#d4af37", stroke=INK, sw=1.2))
            # Сопля припою між ніжками 2 і 3
            f.append(rect(cx - 15, cy + 20, 30, 10, fill="#bdc3c7", stroke=POS, sw=1.8, rx=3))
            f.append(circle(cx, cy + 25, 4, fill=POS, stroke=POS, sw=1))
            f.append(text(cx, cy + 58, "Solder Bridge", size=10.5, bold=True, color=POS))

        elif i == 1:
            # Танталовий конденсатор
            f.append(rect(cx - 50, cy - 25, 100, 50, fill="#d35400", stroke=INK, sw=1.6, rx=4))
            # Смуга анода ліворуч
            f.append(rect(cx - 50, cy - 25, 20, 50, fill="#2c3e50", stroke=INK, sw=1.2, rx=2))
            f.append(text(cx - 40, cy + 4, "+", size=14, bold=True, color="#ffffff"))
            f.append(text(cx + 15, cy + 4, "100μ 16V", size=9.5, bold=True, color="#ffffff"))
            # Підписи виводів
            f.append(line(cx - 50, cy + 38, cx - 50, cy + 52, color=POS, sw=1.8))
            f.append(text(cx - 50, cy + 62, "АНОД (+)", size=9.5, bold=True, color=POS))
            f.append(line(cx + 50, cy + 38, cx + 50, cy + 52, color=NEG, sw=1.8))
            f.append(text(cx + 50, cy + 62, "КАТОД (−)", size=9.5, bold=True, color=NEG))

        elif i == 2:
            # Tombstone
            # Контактні площадки на PCB
            f.append(rect(cx - 60, cy + 30, 40, 10, fill="#27ae60", stroke=INK, sw=1.2))
            f.append(rect(cx + 20, cy + 30, 40, 10, fill="#27ae60", stroke=INK, sw=1.2))
            # Піднятий конденсатор 0402
            f.append(rect(cx - 50, cy - 30, 24, 60, fill="#a0522d", stroke=INK, sw=1.5, rx=2))
            f.append(rect(cx - 50, cy + 18, 24, 12, fill="#bdc3c7", stroke=INK, sw=1.2))
            f.append(rect(cx - 50, cy - 30, 24, 12, fill="#bdc3c7", stroke=INK, sw=1.2))
            # Пайка тільки з одного боку
            f.append(circle(cx - 38, cy + 28, 6, fill="#7f8c8d", stroke=INK, sw=1.2))
            f.append(line(cx + 35, cy - 10, cx + 35, cy + 25, color=POS, sw=1.5, dash="3,3"))
            f.append(text(cx + 35, cy + 8, "Обрив!", size=10, bold=True, color=POS))
            f.append(text(cx, cy + 62, "Tombstoning", size=10, bold=True, color="#b8860b"))

        elif i == 3:
            # Кулька під QFN
            f.append(rect(cx - 65, cy - 30, 130, 40, fill="#2c3e50", stroke=INK, sw=1.5, rx=4))
            f.append(text(cx, cy - 10, "Корпус QFN (вид збоку)", size=9.5, color="#ffffff"))
            # PCB основа
            f.append(rect(cx - 75, cy + 30, 150, 8, fill="#1e824c", stroke=INK, sw=1.2))
            # Ніжки та кулька
            f.append(rect(cx - 55, cy + 10, 14, 20, fill="#bdc3c7", stroke=INK, sw=1.2))
            f.append(rect(cx + 41, cy + 10, 14, 20, fill="#bdc3c7", stroke=INK, sw=1.2))
            # Паразитна кулька
            f.append(circle(cx - 15, cy + 20, 6, fill="#e74c3c", stroke=INK, sw=1.4))
            f.append(text(cx - 15, cy + 58, "Solder Ball", size=10, bold=True, color=POS))

        # Опис унизу
        f.append(mtext(px + pw / 2, y0 + 260, desc, size=9.5, color=INK, lh=1.35))

    return render(os.path.join(IMG, "cold-defects.svg"), W, H, *f)


# ── 2. Прозвонка шин живлення та локалізація закоротки Кельвіном ──────────────
def fig_power_probing():
    W, H = 940, 440
    f = [text(W / 2, 28, "Перевірка шин живлення до подачі напруги (Cold Resistance & Kelvin Probing)",
              size=15, bold=True)]

    # Ліва половина: мультиметр у режимі вимірювання опору / перевірки діодів
    f.append(rect(30, 60, 420, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(240, 85, "1. Вимірювання опору VCC ↔ GND", size=13, bold=True, color=INK))

    # Мультиметр
    f.append(rect(60, 110, 160, 200, fill="#2c3e50", stroke=INK, sw=1.8, rx=10))
    # Дисплей
    f.append(rect(75, 125, 130, 50, fill="#95a5a6", stroke=INK, sw=1.5, rx=4))
    f.append(text(140, 158, "12.48 kΩ", size=16, bold=True, color="#111111"))
    f.append(text(190, 140, "AUTO", size=9.5, color="#222222"))
    # Перемикач
    f.append(circle(140, 220, 24, fill="#34495e", stroke="#ecf0f1", sw=1.5))
    f.append(line(140, 220, 140, 200, color=POS, sw=3))
    # Гнізда
    f.append(circle(105, 275, 8, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(175, 275, 8, fill=INK, stroke=INK, sw=1.5))

    # Дроти до плати
    f.append(line(105, 283, 105, 340, color=POS, sw=2))
    f.append(line(105, 340, 270, 340, color=POS, sw=2))
    f.append(arrow(270, 340, 310, 200, color=POS, sw=2))

    f.append(line(175, 283, 175, 360, color=NEG, sw=2))
    f.append(line(175, 360, 270, 360, color=NEG, sw=2))
    f.append(arrow(270, 360, 310, 270, color=NEG, sw=2))

    # Тестові точки на платі
    f.append(rect(290, 150, 140, 160, fill="#1e824c", stroke=INK, sw=1.5, rx=6))
    f.append(text(360, 175, "Тестова плата", size=11, color="#ffffff", bold=True))
    f.append(circle(360, 205, 10, fill="#d4af37", stroke=INK, sw=1.5))
    f.append(text(395, 209, "TP: 3.3V", size=10, bold=True, color="#ffffff"))
    f.append(circle(360, 270, 10, fill="#d4af37", stroke=INK, sw=1.5))
    f.append(text(395, 274, "TP: GND", size=10, bold=True, color="#ffffff"))

    f.append(mtext(240, 390,
                   ["Норма: ємнісний заряд C_block -> опір плавно росте від сотен Ом до кОм/МОм.",
                    "Коротке замикання: стабільні 0.0–0.8 Ω (звуковий сигнал зумера)."],
                   size=9.5, color=INK, lh=1.3))

    # Права половина: 4-провідна локалізація закоротки Кельвіном
    f.append(rect(480, 60, 430, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(695, 85, "2. Локалізація закоротки (Kelvin Gradient)", size=13, bold=True, color=INK))

    # Доріжка живлення
    f.append(rect(510, 190, 370, 16, fill="#d4af37", stroke=INK, sw=1.5, rx=2))
    f.append(text(550, 175, "Мідна доріжка живлення (VCC Trace, 35 мкм)", size=9.5, color=MUTED))

    # Струм вдування (I_inject = 100 мА від БЖ)
    f.append(arrow(520, 130, 520, 185, color=POS, sw=2.2))
    f.append(text(520, 120, "Вдування I = 100 мА", size=10, bold=True, color=POS))

    # Точка закоротки
    f.append(circle(820, 198, 8, fill=POS, stroke=INK, sw=1.5))
    f.append(line(820, 206, 820, 255, color=POS, sw=2))
    f.append(rect(780, 255, 80, 25, fill="#e74c3c", stroke=INK, sw=1.2, rx=4))
    f.append(text(820, 271, "ЗАКОРОТКА", size=9.5, bold=True, color="#ffffff"))

    # Зонди мілівольтметра
    f.append(circle(590, 198, 5, fill="#3498db", stroke=INK, sw=1.2))
    f.append(circle(730, 198, 5, fill="#3498db", stroke=INK, sw=1.2))
    f.append(line(590, 198, 640, 240, color="#2980b9", sw=1.5))
    f.append(line(730, 198, 680, 240, color="#2980b9", sw=1.5))

    b, _, _ = textbox(660, 255, "Мілівольтметр (ΔV)", size=10, bold=True, fill="#ebf5fb", stroke="#2980b9", sw=1.5, pad=6)
    f.append(b)

    f.append(mtext(695, 335,
                   ["При постійному струмі I = 100 мА кожен сантиметр доріжки дає спад напруги.",
                    "Рухаємося щупами: напруга ПАДАЄ до мінімуму (0 мВ) точно в точці закоротки!"],
                   size=9.5, color=INK, lh=1.35))

    return render(os.path.join(IMG, "power-probing.svg"), W, H, *f)


# ── 3. Осцилограма старту: Inrush струм та поведінка БЖ (CV vs CC) ────────────
def fig_inrush_curve():
    W, H = 940, 430
    f = [text(W / 2, 28, "Пусковий струм (Inrush Current) та реакція лабораторного БЖ",
              size=15, bold=True)]

    # Лівий екран: нормальний пуск (CV режим)
    f.append(rect(40, 60, 410, 340, fill="#1c2833", stroke=INK, sw=1.8, rx=8))
    f.append(text(245, 88, "Нормальний пуск (Режим CV, I < I_limit)", size=12, bold=True, color="#2ecc71"))

    # Сітка осцилографа
    for gy in range(110, 360, 30):
        f.append(line(60, gy, 430, gy, color="#2c3e50", sw=0.8, dash="2,3"))
    for gx in range(60, 440, 45):
        f.append(line(gx, 110, gx, 350, color="#2c3e50", sw=0.8, dash="2,3"))

    # Крива напруги V(t) — жовта
    f.append(line(60, 320, 100, 320, color="#f1c40f", sw=2.5))
    # плавний ріст напруги до 3.3 В
    f.append(line(100, 320, 160, 160, color="#f1c40f", sw=2.5))
    f.append(line(160, 160, 430, 160, color="#f1c40f", sw=2.5))
    f.append(text(380, 148, "V_out = 3.3 В", size=10, bold=True, color="#f1c40f"))

    # Крива струму I(t) — блакитна: пік заряду ємностей (Inrush), спад до 45 мА
    f.append(line(60, 340, 100, 340, color="#3498db", sw=2.2))
    f.append(line(100, 340, 120, 190, color="#3498db", sw=2.2)) # пік
    f.append(line(120, 190, 170, 310, color="#3498db", sw=2.2)) # спад
    f.append(line(170, 310, 430, 310, color="#3498db", sw=2.2)) # струм спокою 45 мА
    f.append(text(150, 185, "Inrush пік (C · dV/dt)", size=9, color="#3498db"))
    f.append(text(360, 298, "I_спокою = 45 мА", size=10, bold=True, color="#3498db"))

    # Рівень ліміту струму (червоний пунктир)
    f.append(line(60, 175, 430, 175, color=POS, sw=1.5, dash="4,4"))
    f.append(text(80, 170, "I_limit = 100 мА", size=9.5, bold=True, color=POS, anchor="start"))
    f.append(text(245, 385, "Блок живлення лишається в режимі CV (Constant Voltage)", size=10, color="#ecf0f1"))

    # Правий екран: коротке замикання (колапс у CC режим)
    f.append(rect(490, 60, 410, 340, fill="#1c2833", stroke=INK, sw=1.8, rx=8))
    f.append(text(695, 88, "Коротке замикання (Колапс у режим CC)", size=12, bold=True, color=POS))

    # Сітка осцилографа
    for gy in range(110, 360, 30):
        f.append(line(510, gy, 880, gy, color="#2c3e50", sw=0.8, dash="2,3"))
    for gx in range(510, 890, 45):
        f.append(line(gx, 110, gx, 350, color="#2c3e50", sw=0.8, dash="2,3"))

    # Крива напруги V(t) — колапс до 0.1 В
    f.append(line(510, 320, 550, 320, color="#f1c40f", sw=2.5))
    f.append(line(550, 320, 580, 280, color="#f1c40f", sw=2.5))
    f.append(line(580, 280, 610, 335, color="#f1c40f", sw=2.5)) # просідання
    f.append(line(610, 335, 880, 335, color="#f1c40f", sw=2.5))
    f.append(text(780, 325, "V_out просіла до 0.1 В", size=10, bold=True, color="#f1c40f"))

    # Крива струму I(t) — стрибок до стелі 100 мА й утримання
    f.append(line(510, 340, 550, 340, color="#3498db", sw=2.2))
    f.append(line(550, 340, 570, 175, color="#3498db", sw=2.2))
    f.append(line(570, 175, 880, 175, color="#3498db", sw=2.2))
    f.append(text(760, 162, "Струм уперся в ліміт 100 мА", size=10, bold=True, color="#3498db"))

    # Рівень ліміту
    f.append(line(510, 175, 880, 175, color=POS, sw=1.5, dash="4,4"))
    f.append(text(530, 170, "I_limit = 100 мА", size=9.5, bold=True, color=POS, anchor="start"))
    f.append(text(695, 385, "Блок перейшов у CC (Constant Current) — схема врятована!", size=10, color="#f39c12"))

    return render(os.path.join(IMG, "inrush-curve.svg"), W, H, *f)


# ── 4. Тепловий контроль: ізопропіловий спирт та термографія ─────────────────
def fig_thermal_detection():
    W, H = 940, 420
    f = [text(W / 2, 28, "Локалізація несправності: випаровування ізопропілового спирту (IPA) та тепловізор",
              size=15, bold=True)]

    # Ліва панель: Метод спирту (IPA)
    f.append(rect(40, 60, 410, 330, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(245, 88, "Метод швидкого випаровування спирту (IPA)", size=12.5, bold=True, color=INK))

    # Плата з нанесеною плівкою спирту
    f.append(rect(70, 120, 350, 180, fill="#1e824c", stroke=INK, sw=1.6, rx=6))
    # Плівка спирту (волога зона)
    f.append(rect(80, 130, 330, 160, fill="#5dade2", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(170, 150, "Плівка ізопропілового спирту (волога)", size=9.5, color="#ffffff", italic=True))

    # Звичайні холодні компоненти (мокрі)
    f.append(rect(100, 180, 45, 30, fill="#2c3e50", stroke=INK, sw=1.2, rx=2))
    f.append(rect(160, 180, 30, 20, fill="#7f8c8d", stroke=INK, sw=1.2, rx=2))
    f.append(rect(100, 230, 50, 25, fill="#7f8c8d", stroke=INK, sw=1.2, rx=2))

    # Гарячий пробитий керамічний конденсатор (MLCC)
    f.append(circle(290, 210, 42, fill="#ffffff", stroke=POS, sw=2))
    f.append(rect(275, 195, 30, 30, fill="#c0392b", stroke=INK, sw=1.5, rx=2))
    f.append(text(290, 175, "Суха пляма!", size=10, bold=True, color=POS))
    f.append(text(290, 240, "P = I²·R > 0.5 Вт", size=9, bold=True, color=POS))

    f.append(mtext(245, 335,
                   ["Тонкий шар IPA наноситься пензликом. При подачі струму 100–300 мА",
                    "дефектний елемент розігрівається (>50 °C) і спирт над ним миттєво висихає."],
                   size=9.5, color=INK, lh=1.35))

    # Права панель: Тепловізор (LWIR карта)
    f.append(rect(490, 60, 410, 330, fill="#111111", stroke=INK, sw=1.8, rx=8))
    f.append(text(695, 88, "Тепловізійний контроль (LWIR Infrared)", size=12.5, bold=True, color="#ffffff"))

    # Імітація теплової карти (холодний синій фон)
    f.append(rect(520, 120, 350, 180, fill="#1b2631", stroke="#34495e", sw=1.5, rx=6))
    # Теплові градієнти навколо гарячої точки
    f.append(circle(740, 210, 75, fill="#1f3a93", stroke="none"))
    f.append(circle(740, 210, 55, fill="#8e44ad", stroke="none"))
    f.append(circle(740, 210, 38, fill="#d35400", stroke="none"))
    f.append(circle(740, 210, 22, fill="#f1c40f", stroke="none"))
    f.append(circle(740, 210, 10, fill="#ffffff", stroke="none"))

    # Приціл термометра
    f.append(line(740, 180, 740, 240, color="#ffffff", sw=1.2))
    f.append(line(710, 210, 770, 210, color="#ffffff", sw=1.2))
    f.append(text(740, 160, "Hotspot: 78.4 °C", size=11, bold=True, color="#ffffff"))

    # Шкала температур праворуч
    f.append(rect(840, 135, 16, 150, fill="#2c3e50", stroke="#7f8c8d", sw=1))
    f.append(text(865, 145, "85°C", size=9.5, color="#f1c40f"))
    f.append(text(865, 210, "50°C", size=9.5, color="#e67e22"))
    f.append(text(865, 280, "22°C", size=9.5, color="#3498db"))

    f.append(mtext(695, 335,
                   ["Мікроболометрична матриця фіксує перегрів мікросхеми в стані latch-up,",
                    "пробитого діода чи помилково запаяного LDO стабілізатора."],
                   size=9.5, color="#d5dbdb", lh=1.35))

    return render(os.path.join(IMG, "thermal-detection.svg"), W, H, *f)


# ── 5. Вплив ємності щупа осцилографа на кварцовий резонатор ─────────────────
def fig_crystal_probing():
    W, H = 940, 440
    f = [text(W / 2, 28, "Вимірювання тактового сигналу кварцу: пасивний щуп 10X проти активного FET-щупа",
              size=15, bold=True)]

    # Ліва частина: схема генератора Пірса з підключенням пасивного щупа (зрив)
    f.append(rect(40, 60, 410, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(245, 88, "Пасивний щуп 10X: C_probe = 12–15 пФ (Зрив)", size=12, bold=True, color=POS))

    # Мікроконтролерний інвертор Пірса
    f.append(rect(70, 120, 120, 150, fill="#2c3e50", stroke=INK, sw=1.6, rx=6))
    f.append(text(130, 145, "MCU Inverter", size=10, bold=True, color="#ffffff"))
    f.append(circle(190, 175, 5, fill="#d4af37", stroke=INK, sw=1))
    f.append(text(155, 170, "OSC_IN", size=9.5, color="#ffffff"))
    f.append(circle(190, 225, 5, fill="#d4af37", stroke=INK, sw=1))
    f.append(text(150, 220, "OSC_OUT", size=9.5, color="#ffffff"))

    # Кварцовий резонатор
    f.append(rect(260, 180, 50, 40, fill="#ecf0f1", stroke=INK, sw=1.5, rx=4))
    f.append(line(275, 185, 275, 215, color=INK, sw=2))
    f.append(line(295, 185, 295, 215, color=INK, sw=2))
    f.append(rect(280, 188, 10, 24, fill="#bdc3c7", stroke=INK, sw=1))
    f.append(text(285, 170, "Кварц 16 МГц", size=9.5, bold=True, color=INK))

    # З'єднання
    f.append(line(195, 175, 260, 190, color=INK, sw=1.5))
    f.append(line(195, 225, 260, 210, color=INK, sw=1.5))

    # Конденсатори навантаження C1, C2 (12 пФ)
    f.append(line(220, 180, 220, 250, color=INK, sw=1.2))
    f.append(rect(212, 250, 16, 12, fill="#e67e22", stroke=INK, sw=1, rx=2))
    f.append(text(220, 275, "C1=12 пФ", size=9.5, color=MUTED))

    # Підключення пасивного щупа 10X до OSC_IN
    f.append(line(220, 180, 350, 140, color=POS, sw=2))
    b, _, _ = textbox(360, 140, "Пасивний щуп 10X\nC_in ≈ 15 пФ\nR_in = 10 MΩ",
                      size=9.5, bold=True, fill="#fdecea", stroke=POS, sw=1.5, pad=6)
    f.append(b)

    f.append(mtext(245, 340,
                   ["Ємність щупа (15 пФ) додається паралельно C1 (12 пФ) -> C_total = 27 пФ.",
                    "Коефіцієнт підсилення петлі падає нижче 1 -> генерація ПОВНІСТЮ ЗРИВАЄТЬСЯ!"],
                   size=9.5, color=POS, lh=1.35))

    # Права частина: активний FET-щуп / Near-Field зонд
    f.append(rect(490, 60, 410, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(695, 88, "Активний FET-щуп: C_probe < 0.8 пФ (Успіх)", size=12, bold=True, color="#27ae60"))

    # Мікроконтролерний інвертор
    f.append(rect(520, 120, 120, 150, fill="#2c3e50", stroke=INK, sw=1.6, rx=6))
    f.append(text(580, 145, "MCU Inverter", size=10, bold=True, color="#ffffff"))
    f.append(circle(640, 175, 5, fill="#d4af37", stroke=INK, sw=1))
    f.append(text(605, 170, "OSC_IN", size=9.5, color="#ffffff"))
    f.append(circle(640, 225, 5, fill="#d4af37", stroke=INK, sw=1))
    f.append(text(600, 220, "OSC_OUT", size=9.5, color="#ffffff"))

    # Кварц
    f.append(rect(710, 180, 50, 40, fill="#ecf0f1", stroke=INK, sw=1.5, rx=4))
    f.append(line(725, 185, 725, 215, color=INK, sw=2))
    f.append(line(745, 185, 745, 215, color=INK, sw=2))
    f.append(rect(730, 188, 10, 24, fill="#bdc3c7", stroke=INK, sw=1))
    f.append(text(735, 170, "Кварц 16 МГц", size=9.5, bold=True, color=INK))

    f.append(line(645, 175, 710, 190, color=INK, sw=1.5))
    f.append(line(645, 225, 710, 210, color=INK, sw=1.5))

    # C1, C2
    f.append(line(670, 180, 670, 250, color=INK, sw=1.2))
    f.append(rect(662, 250, 16, 12, fill="#e67e22", stroke=INK, sw=1, rx=2))
    f.append(text(670, 275, "C1=12 пФ", size=9.5, color=MUTED))

    # Підключення активного щупа до OSC_OUT
    f.append(line(670, 225, 800, 225, color="#27ae60", sw=2))
    b, _, _ = textbox(810, 225, "Активний FET-щуп\nC_in ≈ 0.6 пФ\n(або MCO пін)",
                      size=9.5, bold=True, fill="#eef6ef", stroke="#27ae60", sw=1.5, pad=6)
    f.append(b)

    f.append(mtext(695, 340,
                   ["Активний FET-щуп має мізерну ємність (<0.8 пФ) і підключається до OSC_OUT",
                    "(низькоомний вихід). Або тактування виводиться на буферизований тестовий пін MCO."],
                   size=9.5, color="#1e824c", lh=1.35))

    return render(os.path.join(IMG, "crystal-probing.svg"), W, H, *f)


# ── 6. Граф-алгоритм покрокового оживлення плати ──────────────────────────────
def fig_bringup_flowchart():
    W, H = 940, 520
    f = [text(W / 2, 26, "Покроковий алгоритм початкового оживлення друкованої плати (Bring-Up Flow)",
              size=15, bold=True)]

    steps = [
        ("1. Холодний візуальний огляд", "Мікроскоп: полярність діодів/танталів,\nвідсутність містків і кульок припою", "#eef1f5", INK),
        ("2. Продзвонка шин живлення", "Опір VCC ↔ GND у режимі Ом/діод:\nзаряд конденсаторів, відсутність КЗ", "#eef1f5", INK),
        ("3. Подача V_in з лімітом струму", "БЖ у режимі CC/CV (ліміт 50–100 мА):\nмоніторинг струму спокою (I < I_lim)", "#fef6e7", "#b8860b"),
        ("4. Тепловий контроль (IPA/LWIR)", "Швидка перевірка на гарячі точки:\nнормальна температура всіх IC", "#eef6ef", FIELD),
        ("5. Замір шин LDO / DC-DC", "Мультиметр/осцилограф на Test Points:\nрівень напруг та відсутність пульсацій", "#eef6ef", FIELD),
        ("6. Перевірка NRST і кварцу", "Рівень Reset (>0.8·VDD) та стабільна\nгенерація годинника (Active probe / MCO)", "#eef6ef", FIELD),
        ("7. Зв'язок з SWD / JTAG", "Підключення налагоджувача: зчитування\nIDCODE та перший тестовий Blink", "#fdecea", POS),
    ]

    bw, bh = 240, 68
    col1_x = 180
    col2_x = 680

    coords = [
        (col1_x, 75),
        (col1_x, 185),
        (col1_x, 295),
        (col1_x, 405),
        (col2_x, 75),
        (col2_x, 185),
        (col2_x, 295),
    ]

    for i, ((t, desc, fill, stroke), (cx, cy)) in enumerate(zip(steps, coords)):
        f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=8))
        f.append(text(cx, cy - 14, t, size=11, bold=True, color=stroke))
        f.append(mtext(cx, cy + 6, desc, size=9.2, color=INK, lh=1.3))

        # Стрілки переходу
        if i < 3:
            f.append(arrow(cx, cy + bh / 2, cx, coords[i + 1][1] - bh / 2, color=MUTED, sw=1.8))
        elif i == 3:
            # Перехід з лівої колонки в праву
            f.append(line(cx + bw / 2, cy, cx + bw / 2 + 130, cy, color=MUTED, sw=1.8))
            f.append(line(cx + bw / 2 + 130, cy, cx + bw / 2 + 130, coords[4][1], color=MUTED, sw=1.8))
            f.append(arrow(cx + bw / 2 + 130, coords[4][1], col2_x - bw / 2, coords[4][1], color=MUTED, sw=1.8))
        elif i < 6:
            f.append(arrow(cx, cy + bh / 2, cx, coords[i + 1][1] - bh / 2, color=MUTED, sw=1.8))

    # Фінальний успішний стан
    f.append(rect(col2_x - bw / 2, 405 - bh / 2, bw, bh, fill="#27ae60", stroke=INK, sw=2, rx=8))
    f.append(text(col2_x, 395, "ПЛАТА ОЖИВЛЕНА!", size=13, bold=True, color="#ffffff"))
    f.append(text(col2_x, 415, "Перехід до функціональних тестів", size=9.5, color="#ffffff"))
    f.append(arrow(col2_x, 295 + bh / 2, col2_x, 405 - bh / 2, color="#27ae60", sw=2.2))

    return render(os.path.join(IMG, "bringup-flowchart.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cold_defects()
    fig_power_probing()
    fig_inrush_curve()
    fig_thermal_detection()
    fig_crystal_probing()
    fig_bringup_flowchart()
    print("OK: all bringup SVGs generated successfully.")
