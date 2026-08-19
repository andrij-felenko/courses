# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1) Чотири квадранти: площина полярностей MT2 та Gate відносно MT1
# ════════════════════════════════════════════════════════════════════════════
def fig_quadrants_polarities():
    W, H = 760, 420
    cx, cy = 380, 215
    p = []

    # Фонова розмітка квадрантів
    p.append(rect(40, 40, W - 80, H - 70, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # Головні осі координат
    p.append(line(70, cy, W - 70, cy, color=INK, sw=1.8))
    p.append(line(cx, H - 45, cx, 55, color=INK, sw=1.8))

    # Стрілки осей
    p.append(arrow(W - 85, cy, W - 65, cy, color=INK, sw=1.8))
    p.append(arrow(cx, 75, cx, 50, color=INK, sw=1.8))

    # Підписи осей
    p.append(text(W - 60, cy - 12, "Полярність MT2", size=12, bold=True, anchor="end"))
    p.append(text(cx + 12, 60, "Струм затвора G", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx, H - 15, "Усі напруги і струми вимірюються ВІДНОСНО виводу MT1 (0 В)", size=11, color=MUTED, italic=True))

    # Полярності на кінцях осей
    p.append(text(W - 75, cy + 20, "MT2 (+)", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(85, cy + 20, "MT2 (−)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(cx + 12, 80, "+ I_G (втікає)", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(cx + 12, H - 55, "− I_G (витікає)", size=10, color=NEG, bold=True, anchor="start"))

    # Картки квадрантів
    # Q-I: верхній правий (MT2+, G+)
    p.append(rect(cx + 25, 80, 290, 115, fill="#edfbf2", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(cx + 40, 105, "КВАДРАНТ I (I+)", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 40, 125, "MT2 (+),  Затвор (+)", size=11, bold=True, anchor="start"))
    p.append(text(cx + 40, 145, "• Пряме відмикання p-n-p-n", size=10.5, color=INK, anchor="start"))
    p.append(text(cx + 40, 163, "• Найвища чутливість: I_GT ≈ 1.0×", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 40, 181, "• Найкраща динаміка di/dt", size=10, color=MUTED, anchor="start"))

    # Q-II: нижній правий (MT2+, G-)
    p.append(rect(cx + 25, cy + 20, 290, 115, fill="#f4f8fc", stroke="#2980b9", sw=1.4, rx=6))
    p.append(text(cx + 40, cy + 45, "КВАДРАНТ II (I−)", size=13, color="#2980b9", bold=True, anchor="start"))
    p.append(text(cx + 40, cy + 65, "MT2 (+),  Затвор (−)", size=11, bold=True, anchor="start"))
    p.append(text(cx + 40, cy + 85, "• Дистанційна інжекція електронів", size=10.5, color=INK, anchor="start"))
    p.append(text(cx + 40, cy + 103, "• Добра чутливість: I_GT ≈ 1.3×", size=10.5, color="#2980b9", bold=True, anchor="start"))
    p.append(text(cx + 40, cy + 121, "• Робочий режим негативного драйву", size=10, color=MUTED, anchor="start"))

    # Q-III: нижній лівий (MT2-, G-)
    p.append(rect(65, cy + 20, 290, 115, fill="#f4f8fc", stroke="#2980b9", sw=1.4, rx=6))
    p.append(text(80, cy + 45, "КВАДРАНТ III (III−)", size=13, color="#2980b9", bold=True, anchor="start"))
    p.append(text(80, cy + 65, "MT2 (−),  Затвор (−)", size=11, bold=True, anchor="start"))
    p.append(text(80, cy + 85, "• Допоміжний тиристорний канал", size=10.5, color=INK, anchor="start"))
    p.append(text(80, cy + 103, "• Добра чутливість: I_GT ≈ 1.4×", size=10.5, color="#2980b9", bold=True, anchor="start"))
    p.append(text(80, cy + 121, "• Робочий режим негативного драйву", size=10, color=MUTED, anchor="start"))

    # Q-IV: верхній лівий (MT2-, G+)
    p.append(rect(65, 80, 290, 115, fill="#fdf2f2", stroke=POS, sw=1.6, rx=6))
    p.append(text(80, 105, "КВАДРАНТ IV (III+)", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(80, 125, "MT2 (−),  Затвор (+)", size=11, bold=True, anchor="start"))
    p.append(text(80, 145, "• Віддалений омічний градієнт", size=10.5, color=INK, anchor="start"))
    p.append(text(80, 163, "• Найгірша чутливість: I_GT ≈ 2.5–4.0×", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(80, 181, "• УНИКАЮТЬ! Вилучений у 3Q симісторах", size=10, color=POS, bold=True, anchor="start"))

    return render(os.path.join(OUT, "quadrants-polarities.svg"), W, H, *p,
                  title="Чотири квадранти запуску симістора")


# ════════════════════════════════════════════════════════════════════════════
# 2) Внутрішня фізика кристала та інжекція носіїв
# ════════════════════════════════════════════════════════════════════════════
def fig_triac_die_physics():
    W, H = 820, 480
    p = []

    # 4 панелі для 4 квадрантів
    pw, ph = 360, 195
    coords = [
        (40, 40, "Квадрант I: MT2(+), G(+)", FIELD, "Пряма інжекція: G(+) інжектує дірки в P2,\nN2 інжектує електрони. Миттєвий ланцюг.", True),
        (420, 40, "Квадрант II: MT2(+), G(−)", "#2980b9", "Дистанційний затвор: G(−) зміщує P2-N4.\nЕлектрони з N4 летять через P2 в N1 база.", False),
        (40, 255, "Квадрант III: MT2(−), G(−)", "#2980b9", "Допоміжний пілот: G(−) вмикає секцію P2-N4,\nструм якої відмикає головну структуру P2-N1-P1-N3.", False),
        (420, 255, "Квадрант IV: MT2(−), G(+)", POS, "Патологічний обхід: G(+) створює падіння на опорі P2.\nСлабке збирання носіїв, високий I_GT.", False)
    ]

    for px, py, title_txt, col, desc_txt, is_q1 in coords:
        p.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=6))
        p.append(rect(px, py, pw, 28, fill="#f2f5f8", stroke="#c5d1dc", sw=1.0, rx=6))
        p.append(text(px + pw/2, py + 18, title_txt, size=11.5, color=col, bold=True))

        # Спрощена структура кристала всередині панелі
        kx = px + 20
        ky = py + 38
        kw = 160
        kh = 95

        # Шари напівпровідника
        # P2 шар (верх)
        p.append(rect(kx, ky, kw, 24, fill="#fde8d7", stroke="#d9822b", sw=1.1, rx=0))
        p.append(text(kx + 15, ky + 16, "P2", size=10, bold=True, color="#a04000"))

        # Вкраплення N2 (MT1 емітер)
        p.append(rect(kx + 40, ky, 45, 15, fill="#d4e6f1", stroke="#2980b9", sw=1.1, rx=0))
        p.append(text(kx + 62, ky + 11, "N2", size=9, bold=True, color="#1b4f72"))

        # Вкраплення N4 (Gate емітер)
        p.append(rect(kx + 110, ky, 38, 15, fill="#d4e6f1", stroke="#2980b9", sw=1.1, rx=0))
        p.append(text(kx + 129, ky + 11, "N4", size=9, bold=True, color="#1b4f72"))

        # N1 дрейфовий шар (центр)
        p.append(rect(kx, ky + 24, kw, 38, fill="#ebf5fb", stroke="#7fb3d5", sw=1.1, rx=0))
        p.append(text(kx + 15, ky + 46, "N1 (база)", size=10, bold=True, color="#2471a3"))

        # P1 шар (низ)
        p.append(rect(kx, ky + 62, kw, 24, fill="#fde8d7", stroke="#d9822b", sw=1.1, rx=0))
        p.append(text(kx + 15, ky + 78, "P1", size=10, bold=True, color="#a04000"))

        # Вкраплення N3 (MT2 емітер)
        p.append(rect(kx + 85, ky + 71, 55, 15, fill="#d4e6f1", stroke="#2980b9", sw=1.1, rx=0))
        p.append(text(kx + 112, ky + 82, "N3", size=9, bold=True, color="#1b4f72"))

        # Виводи: MT1, Gate, MT2
        # MT1 контакт (накриває P2 і N2)
        p.append(line(kx + 30, ky, kx + 85, ky, color=INK, sw=3.0))
        p.append(line(kx + 50, ky, kx + 50, ky - 8, color=INK, sw=1.6))
        p.append(text(kx + 50, ky - 10, "MT1", size=9, bold=True))

        # Gate контакт (накриває P2 або N4)
        p.append(line(kx + 120, ky, kx + 150, ky, color=FIELD, sw=3.0))
        p.append(line(kx + 135, ky, kx + 135, ky - 8, color=FIELD, sw=1.6))
        p.append(text(kx + 135, ky - 10, "G", size=9, color=FIELD, bold=True))

        # MT2 контакт (накриває P1 і N3)
        p.append(line(kx + 20, ky + 86, kx + 140, ky + 86, color=INK, sw=3.0))
        p.append(line(kx + 80, ky + 86, kx + 80, ky + 96, color=INK, sw=1.6))
        p.append(text(kx + 80, ky + 104, "MT2", size=9, bold=True))

        # Опис механізму праворуч від кристала
        lines = desc_txt.split("\n")
        p.append(text(px + 195, py + 55, lines[0], size=9.5, color=INK, anchor="start", bold=True))
        p.append(text(px + 195, py + 72, lines[1], size=9, color=MUTED, anchor="start"))
        if len(lines) > 2:
            p.append(text(px + 195, py + 89, lines[2], size=9, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "triac-die-physics.svg"), W, H, *p,
                  title="Фізика інжекції носіїв у чотирьох квадрантах")


# ════════════════════════════════════════════════════════════════════════════
# 3) Пряме керування від мікроконтролера: Negative Gate Drive (Q2 і Q3)
# ════════════════════════════════════════════════════════════════════════════
def fig_negative_mcu_drive():
    W, H = 800, 360
    p = []

    # Ліва частина: Схема включення
    p.append(rect(30, 30, 410, 300, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=8))
    p.append(text(235, 52, "Схема негативного керування (MCU VCC = MT1)", size=11.5, bold=True))

    # Шина VCC (+3.3V / +5V), вона ж MT1 і нейтраль N
    top_y = 80
    p.append(line(50, top_y, 420, top_y, color=POS, sw=2.2))
    p.append(text(55, top_y - 8, "VCC (+3.3V / +5V)  ==  MT1  ==  Нейтраль (N)", size=10, color=POS, bold=True, anchor="start"))

    # МК блок
    mcu_x, mcu_y = 110, 175
    b_mcu, _, _ = textbox(mcu_x, mcu_y, "МК\n(MCU)", size=11, bold=True, min_w=65, fill="#eef3f8", stroke="#2457d6")
    p.append(b_mcu)

    # Живлення МК: VCC до верхньої шини, GND до нижньої
    p.append(line(mcu_x - 15, mcu_y - 25, mcu_x - 15, top_y, color=POS, sw=1.6))
    p.append(text(mcu_x - 18, 105, "VCC", size=9.5, color=POS, bold=True, anchor="end"))

    bot_y = 280
    p.append(line(50, bot_y, 220, bot_y, color=NEG, sw=2.0))
    p.append(text(55, bot_y + 16, "MCU GND (0V відносно МК = −3.3V відносно MT1)", size=9.5, color=NEG, bold=True, anchor="start"))
    p.append(line(mcu_x - 15, mcu_y + 25, mcu_x - 15, bot_y, color=NEG, sw=1.6))
    p.append(text(mcu_x - 18, 260, "GND", size=9.5, color=NEG, bold=True, anchor="end"))

    # Вихід GPIO через резистор R_gate
    p.append(line(mcu_x + 32, mcu_y, 220, mcu_y, color=INK, sw=1.8))
    p.append(text(mcu_x + 40, mcu_y - 8, "GPIO", size=9.5, bold=True, anchor="start"))

    # Резистор R_gate
    p.append(rect(220, mcu_y - 8, 45, 16, fill="#ffffff", stroke=INK, sw=1.6, rx=0))
    p.append(text(242, mcu_y - 12, "R_gate", size=9.5, bold=True))
    p.append(line(265, mcu_y, 325, mcu_y, color=FIELD, sw=1.8))
    p.append(text(295, mcu_y - 8, "I_G (витікає)", size=9.5, color=FIELD, bold=True))

    # Симістор
    tx = 350
    # Верх MT1 до VCC
    p.append(line(tx, top_y, tx, mcu_y - 25, color=INK, sw=2.2))
    p.append(text(tx + 8, top_y + 20, "MT1", size=10, bold=True, anchor="start"))

    # Символ симістора
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (tx-12, mcu_y-25, tx+12, mcu_y-25, tx, mcu_y-5, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.8"/>'
             % (tx-12, mcu_y+15, tx+12, mcu_y+15, tx, mcu_y-5, INK))
    p.append(line(tx+12, mcu_y-25, tx+12, mcu_y-5, color=INK, sw=2.4))
    p.append(line(tx-12, mcu_y+15, tx-12, mcu_y-5, color=INK, sw=2.4))

    # Затвор
    p.append(line(tx-12, mcu_y-10, 325, mcu_y, color=FIELD, sw=2.0))
    p.append(text(tx - 20, mcu_y - 12, "G", size=10, color=FIELD, bold=True))

    # Низ MT2 до навантаження і фази L
    p.append(line(tx, mcu_y + 15, tx, 260, color=INK, sw=2.2))
    p.append(text(tx + 8, 245, "MT2", size=10, bold=True, anchor="start"))

    # Навантаження
    b_load, _, _ = textbox(tx, 295, "Навантаження", size=9.5, bold=True, min_w=85, fill="#fdfefe", stroke="#333333")
    p.append(b_load)
    p.append(line(tx, 315, tx, 330, color=INK, sw=2.0))
    p.append(text(tx + 8, 330, "Фаза (L)", size=10, color=POS, bold=True, anchor="start"))

    # Права частина: Часові діаграми квадрантів
    p.append(rect(460, 30, 310, 300, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=8))
    p.append(text(615, 52, "Робота в квадрантах II і III", size=11.5, bold=True))

    # Синусоїда мережі
    gx, gy = 485, 115
    gw, gh = 260, 40
    p.append(line(gx, gy, gx + gw, gy, color=MUTED, sw=1.2))
    p.append(text(gx - 5, gy - 25, "U (MT2)", size=10, bold=True, anchor="end"))

    # Крива синуса
    pts = []
    for i in range(101):
        frac = i / 100.0
        x = gx + frac * gw
        y = gy - 28 * math.sin(frac * 2 * math.pi)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="#2c3e50" stroke-width="2.0"/>' % " ".join(pts))
    p.append(text(gx + 65, gy - 16, "+ півхвиля", size=9, color=POS, bold=True))
    p.append(text(gx + 195, gy + 22, "− півхвиля", size=9, color=NEG, bold=True))

    # Імпульси затвора (завжди від'ємні)
    gy2 = 205
    p.append(line(gx, gy2, gx + gw, gy2, color=MUTED, sw=1.2))
    p.append(text(gx - 5, gy2 - 15, "I_gate (MCU LOW)", size=9.5, color=FIELD, bold=True, anchor="end"))

    # Два імпульси вниз
    # Імпульс 1 на додатній півхвилі
    p.append(rect(gx + 45, gy2, 25, 25, fill="#e8f8f0", stroke=FIELD, sw=1.6, rx=0))
    p.append(text(gx + 57, gy2 + 38, "−I_G", size=9, color=FIELD, bold=True))

    # Імпульс 2 на від'ємній півхвилі
    p.append(rect(gx + 175, gy2, 25, 25, fill="#e8f8f0", stroke=FIELD, sw=1.6, rx=0))
    p.append(text(gx + 187, gy2 + 38, "−I_G", size=9, color=FIELD, bold=True))

    # Підсумкові квадранти
    p.append(rect(gx + 20, 265, 100, 45, fill="#edf4fc", stroke="#2980b9", sw=1.4, rx=4))
    p.append(text(gx + 70, 282, "Квадрант II", size=10, color="#2980b9", bold=True))
    p.append(text(gx + 70, 298, "MT2(+), G(−)", size=9, color=MUTED))

    p.append(rect(gx + 150, 265, 100, 45, fill="#edf4fc", stroke="#2980b9", sw=1.4, rx=4))
    p.append(text(gx + 200, 282, "Квадрант III", size=10, color="#2980b9", bold=True))
    p.append(text(gx + 200, 298, "MT2(−), G(−)", size=9, color=MUTED))

    return render(os.path.join(OUT, "negative-mcu-drive.svg"), W, H, *p,
                  title="Негативне керування симістором від МК")


# ════════════════════════════════════════════════════════════════════════════
# 4) Оптосимісторне керування (MOC3021 / MOC3041): авто-вибір Q-I та Q-III
# ════════════════════════════════════════════════════════════════════════════
def fig_optotriac_quadrants():
    W, H = 820, 360
    p = []

    # Ліва панель: Позитивна півхвиля -> Квадрант I (MT2+, G+)
    p.append(rect(30, 30, 365, 300, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=8))
    p.append(rect(30, 30, 365, 30, fill="#eafaf1", stroke="#a3e4d7", sw=1.0, rx=8))
    p.append(text(212, 51, "Позитивна півхвиля: КВАДРАНТ I (MT2+, G+)", size=11, color=FIELD, bold=True))

    # Схема Q-I
    ox1 = 80
    p.append(text(ox1, 90, "Фаза L (+)", size=10, color=POS, bold=True, anchor="start"))
    p.append(line(ox1 + 65, 86, 340, 86, color=POS, sw=2.0))

    # Силовий MT2 згори
    p.append(line(230, 86, 230, 140, color=POS, sw=2.0))
    p.append(text(240, 115, "MT2 (+)", size=9.5, color=POS, bold=True, anchor="start"))

    # Оптосимісторний шлях струму
    p.append(line(310, 86, 310, 130, color=FIELD, sw=1.8))
    p.append(rect(295, 130, 30, 16, fill="#ffffff", stroke=FIELD, sw=1.4, rx=0))
    p.append(text(310, 122, "R_lim", size=9.5, color=FIELD, bold=True))
    p.append(line(310, 146, 310, 175, color=FIELD, sw=1.8))

    # Блок оптосимістора
    p.append(rect(285, 175, 50, 35, fill="#edf7ff", stroke="#2980b9", sw=1.4, rx=4))
    p.append(text(310, 196, "MOC", size=9.5, color="#2980b9", bold=True))

    # Від оптосимістора в Затвор
    p.append(line(310, 210, 310, 240, color=FIELD, sw=1.8))
    p.append(line(310, 240, 245, 240, color=FIELD, sw=1.8))
    p.append(text(325, 235, "I_G (+)", size=9.5, color=FIELD, bold=True, anchor="start"))

    # Силовий симістор
    sx = 230
    p.append(line(sx, 140, sx, 170, color=INK, sw=2.0))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (sx-10, 170, sx+10, 170, sx, 185, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (sx-10, 200, sx+10, 200, sx, 185, INK))
    p.append(line(sx+10, 170, sx+10, 185, color=INK, sw=2.2))
    p.append(line(sx-10, 200, sx-10, 185, color=INK, sw=2.2))
    p.append(line(sx-10, 195, 245, 240, color=FIELD, sw=1.8))  # затвор

    # MT1 донизу
    p.append(line(sx, 200, sx, 270, color=INK, sw=2.0))
    p.append(text(240, 265, "MT1 (0В)", size=9.5, bold=True, anchor="start"))
    p.append(line(ox1 + 65, 270, 340, 270, color=NEG, sw=2.0))
    p.append(text(ox1, 274, "Нейтраль N", size=10, color=NEG, bold=True, anchor="start"))

    p.append(text(212, 305, "Струм тече: Фаза L → MT2 → MOC → Затвор G → MT1", size=9.5, color=FIELD, bold=True))

    # Права панель: Негативна півхвиля -> Квадрант III (MT2-, G-)
    p.append(rect(425, 30, 365, 300, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=8))
    p.append(rect(425, 30, 365, 30, fill="#edf4fc", stroke="#aed6f1", sw=1.0, rx=8))
    p.append(text(607, 51, "Негативна півхвиля: КВАДРАНТ III (MT2−, G−)", size=11, color="#2980b9", bold=True))

    # Схема Q-III
    ox2 = 475
    p.append(text(ox2, 90, "Фаза L (−)", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(ox2 + 65, 86, 735, 86, color=NEG, sw=2.0))

    # Силовий MT2 згори (тепер він мінус)
    p.append(line(625, 86, 625, 140, color=NEG, sw=2.0))
    p.append(text(635, 115, "MT2 (−)", size=9.5, color=NEG, bold=True, anchor="start"))

    # Оптосимісторний шлях струму
    p.append(line(705, 86, 705, 130, color="#2980b9", sw=1.8))
    p.append(rect(690, 130, 30, 16, fill="#ffffff", stroke="#2980b9", sw=1.4, rx=0))
    p.append(text(705, 122, "R_lim", size=9.5, color="#2980b9", bold=True))
    p.append(line(705, 146, 705, 175, color="#2980b9", sw=1.8))

    # Блок оптосимістора
    p.append(rect(680, 175, 50, 35, fill="#edf7ff", stroke="#2980b9", sw=1.4, rx=4))
    p.append(text(705, 196, "MOC", size=9.5, color="#2980b9", bold=True))

    # Від Затвора в оптосимістор (струм витікає із затвора)
    p.append(line(705, 210, 705, 240, color="#2980b9", sw=1.8))
    p.append(line(705, 240, 640, 240, color="#2980b9", sw=1.8))
    p.append(text(720, 235, "I_G (−)", size=9.5, color="#2980b9", bold=True, anchor="start"))

    # Силовий симістор
    sx2 = 625
    p.append(line(sx2, 140, sx2, 170, color=INK, sw=2.0))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (sx2-10, 170, sx2+10, 170, sx2, 185, INK))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>'
             % (sx2-10, 200, sx2+10, 200, sx2, 185, INK))
    p.append(line(sx2+10, 170, sx2+10, 185, color=INK, sw=2.2))
    p.append(line(sx2-10, 200, sx2-10, 185, color=INK, sw=2.2))
    p.append(line(sx2-10, 195, 640, 240, color="#2980b9", sw=1.8))  # затвор

    # MT1 донизу (тепер він плюс відносно MT2)
    p.append(line(sx2, 200, sx2, 270, color=INK, sw=2.0))
    p.append(text(635, 265, "MT1 (0В)", size=9.5, bold=True, anchor="start"))
    p.append(line(ox2 + 65, 270, 735, 270, color=POS, sw=2.0))
    p.append(text(ox2, 274, "Нейтраль N", size=10, color=POS, bold=True, anchor="start"))

    p.append(text(607, 305, "Струм тече: MT1 → Затвор G → MOC → MT2 → Фаза L", size=9.5, color="#2980b9", bold=True))

    return render(os.path.join(OUT, "optotriac-quadrant-matching.svg"), W, H, *p,
                  title="Автоматичний вибір квадрантів I та III в оптосимісторному драйвері")


# ════════════════════════════════════════════════════════════════════════════
# 5) 3-квадрантний (Snubberless) симістор і комутація індуктивного навантаження
# ════════════════════════════════════════════════════════════════════════════
def fig_three_quadrant_commutation():
    W, H = 820, 380
    p = []

    # Верхня панель: Індуктивний зсув фази і стрибок dv/dt
    p.append(rect(30, 25, 760, 160, fill="#ffffff", stroke="#c5d1dc", sw=1.4, rx=8))
    p.append(text(410, 45, "Комутація на індуктивному навантаженні: струм I відстає від напруги U", size=11.5, bold=True))

    ax_x, ax_y = 70, 115
    aw = 680
    p.append(line(ax_x, ax_y, ax_x + aw, ax_y, color=MUTED, sw=1.2))
    p.append(text(ax_x + aw + 5, ax_y + 4, "t", size=11, bold=True, italic=True))

    # Напруга мережі (сіра пунктирна синусоїда)
    pts_u = []
    pts_i = []
    shift = 0.20  # індуктивний зсув 0.2 періоду
    for i in range(141):
        frac = i / 140.0 * 1.4
        x = ax_x + frac / 1.4 * aw
        yu = ax_y - 45 * math.sin(frac * 2 * math.pi)
        yi = ax_y - 38 * math.sin((frac - shift) * 2 * math.pi)
        pts_u.append("%.1f,%.1f" % (x, yu))
        pts_i.append("%.1f,%.1f" % (x, yi))

    p.append('<polyline points="%s" fill="none" stroke="#b0bec5" stroke-width="1.8" stroke-dasharray="4 3"/>' % " ".join(pts_u))
    p.append(text(ax_x + 90, ax_y - 48, "Напруга мережі U", size=9.5, color=MUTED, bold=True))

    # Струм (жирна синя лінія)
    p.append('<polyline points="%s" fill="none" stroke="#2457d6" stroke-width="2.4"/>' % " ".join(pts_i))
    p.append(text(ax_x + 220, ax_y - 25, "Струм I", size=10, color=NEG, bold=True))

    # Момент комутації: I переходить через 0, а U вже велика!
    comm_frac = shift + 0.5
    cx = ax_x + comm_frac / 1.4 * aw
    p.append(line(cx, ax_y - 55, cx, ax_y + 55, color=POS, sw=1.6, dash="4 3"))
    p.append(text(cx, ax_y - 58, "Комутація: I = 0", size=10, color=POS, bold=True))
    p.append(text(cx + 8, ax_y + 45, "Стрибок (dv/dt)_c!", size=10, color=POS, bold=True, anchor="start"))

    # Нижня панель: Порівняння 4Q vs 3Q (Snubberless)
    p.append(rect(30, 200, 365, 160, fill="#fdf4f4", stroke=POS, sw=1.4, rx=6))
    p.append(text(212, 222, "Звичайний 4-квадрантний симістор (4Q)", size=11, color=POS, bold=True))
    p.append(text(50, 248, "• Має чутливі зони для квадранта IV", size=10, color=INK, anchor="start"))
    p.append(text(50, 270, "• Накопичує неосновні носії під час струму", size=10, color=INK, anchor="start"))
    p.append(text(50, 292, "• Стрибок (dv/dt)_c змітає заряд → ХИБНЕ ВВІМКНЕННЯ", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(50, 314, "• (dv/dt)_c ліміт низький: 10–50 В/мкс → ПОТРІБЕН СНАБЕР", size=9.5, color=MUTED, bold=True, anchor="start"))
    p.append(text(50, 336, "• Ризик втрати керованості на моторах / дроселях", size=9.5, color=POS, anchor="start"))

    p.append(rect(425, 200, 365, 160, fill="#edfbf2", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(607, 222, "3-квадрантний симістор (Snubberless / Hi-Com)", size=11, color=FIELD, bold=True))
    p.append(text(445, 248, "• Структуру квадранта IV повністю ВИЛУЧЕНО з кристала", size=10, color=INK, anchor="start"))
    p.append(text(445, 270, "• Половини тиристорів ізольовані меза-канавками", size=10, color=INK, anchor="start"))
    p.append(text(445, 292, "• Немає паразитних кишень заряду → ЧИСТЕ ВИМИКАННЯ", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(445, 314, "• (dv/dt)_c ліміт високий: > 1000–2000 В/мкс (БЕЗ СНАБЕРА)", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(445, 336, "• Працює в Q-I, Q-II, Q-III; запуск у Q-IV заблоковано", size=9.5, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "three-quadrant-commutation.svg"), W, H, *p,
                  title="Комутація 4Q проти 3Q симістора на індуктивному навантаженні")


if __name__ == "__main__":
    fig_quadrants_polarities()
    fig_triac_die_physics()
    fig_negative_mcu_drive()
    fig_optotriac_quadrants()
    fig_three_quadrant_commutation()
    print("OK: all quadrant-triggering figures generated successfully ->", OUT)
