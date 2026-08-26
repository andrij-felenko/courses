# -*- coding: utf-8 -*-
"""Фігури для статті roboche-mistse-i-instrument («Робоче місце й інструмент»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── instruments-trio: Тріада вимірювальних приладів лабораторії ─────────────
def fig_instruments_trio():
    W, H = 820, 290
    p = []

    # Три колонки приладів
    cards = [
        {
            "x": 30, "y": 30, "w": 230, "h": 230,
            "title": "Мультиметр (DMM)",
            "sub": "Статика та квазістатика",
            "accent": NEG,
            "bg": "#f0f4fc",
            "lines": [
                "• Напруга постійна й змінна (DC/AC)",
                "• Вхідний опір: 10 МОм",
                "• Прозвонка з компаратором (<30 Ом)",
                "• Падіння на діодах і p-n переходах",
                "• Струм (падіння на шунті)"
            ],
            "role": "Точне число в окремій точці"
        },
        {
            "x": 295, "y": 30, "w": 230, "h": 230,
            "title": "Лабораторний БЖ",
            "sub": "Керована енергія та захист",
            "accent": POS,
            "bg": "#fdf2f0",
            "lines": [
                "• Режими: CV (напруга) та CC (струм)",
                "• Миттєве обмеження струму при КЗ",
                "• Захист: OVP, OCP, переполюсовка",
                "• Безпечний «холодний пуск» (50 мА)",
                "• Контроль споживання всієї плати"
            ],
            "role": "Безпечне живлення схеми"
        },
        {
            "x": 560, "y": 30, "w": 230, "h": 230,
            "title": "Осцилограф (DSO)",
            "sub": "Динаміка в часі (форма хвиль)",
            "accent": FIELD,
            "bg": "#f0faf3",
            "lines": [
                "• Графік U(t): фронти, шуми, викиди",
                "• Смуга (BW) та частота семплування (Fs)",
                "• Захоплення одиничних імпульсів (Trigger)",
                "• Виявлення паразитного дзвону й пульсацій",
                "• Щупи 1X / 10X з RC-компенсацією"
            ],
            "role": "Форма сигналу в реальному часі"
        }
    ]

    for c in cards:
        # Зовнішня картка
        p.append(rect(c["x"], c["y"], c["w"], c["h"], fill=c["bg"], stroke=c["accent"], sw=1.8, rx=8))
        # Заголовок картки
        p.append(text(c["x"] + c["w"] / 2, c["y"] + 24, c["title"], size=14, color=c["accent"], bold=True))
        p.append(text(c["x"] + c["w"] / 2, c["y"] + 42, c["sub"], size=10, color=MUTED, italic=True))
        p.append(line(c["x"] + 15, c["y"] + 52, c["x"] + c["w"] - 15, c["y"] + 52, color=c["accent"], sw=1.0))

        # Пункти списку
        curr_y = c["y"] + 72
        for ln in c["lines"]:
            p.append(text(c["x"] + 12, curr_y, ln, size=10, color=INK, anchor="start"))
            curr_y += 24

        # Підсумок ролі внизу
        p.append(rect(c["x"] + 10, c["y"] + c["h"] - 34, c["w"] - 20, 24, fill="#ffffff", stroke=c["accent"], sw=1.0, rx=4))
        p.append(text(c["x"] + c["w"] / 2, c["y"] + c["h"] - 18, c["role"], size=10, color=c["accent"], bold=True))

    render(os.path.join(OUT, "instruments-trio.svg"), W, H, *p,
           title="Тріада вимірювальних приладів лабораторії розробника")


# ── probe-rc-compensation: Дільник 10X та форми меандру ────────────────────
def fig_probe_rc_compensation():
    W, H = 840, 310
    p = []

    # Ліва частина: Електрична схема дільника щупа 10X
    sx, sy = 25, 25
    sw_box, sh_box = 370, 260
    p.append(rect(sx, sy, sw_box, sh_box, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(sx + sw_box / 2, sy + 22, "Схема пасивного щупа 10X", size=13, color=INK, bold=True))

    # Зона щупа
    probe_x, probe_y, probe_w, probe_h = sx + 15, sy + 45, 155, 150
    p.append(rect(probe_x, probe_y, probe_w, probe_h, fill="#f4f8fb", stroke=NEG, sw=1.2, rx=6))
    p.append(text(probe_x + probe_w / 2, probe_y + 18, "Головка щупа (10X)", size=10, color=NEG, bold=True))

    # R1 та C1 у щупі
    p.append(rect(probe_x + 20, probe_y + 40, 115, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(probe_x + 77, probe_y + 63, "R₁ = 9 МОм", size=11, color=INK, bold=True))
    p.append(rect(probe_x + 20, probe_y + 90, 115, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(probe_x + 77, probe_y + 113, "C₁ (підлаштовний)", size=10, color=NEG, bold=True))

    # Зона осцилографа й кабелю
    scope_x, scope_y, scope_w, scope_h = sx + 195, sy + 45, 160, 150
    p.append(rect(scope_x, scope_y, scope_w, scope_h, fill="#fef9f3", stroke=POS, sw=1.2, rx=6))
    p.append(text(scope_x + scope_w / 2, scope_y + 18, "Кабель + Вхід BNC", size=10, color=POS, bold=True))

    # R2 та C2 у вході
    p.append(rect(scope_x + 20, scope_y + 40, 120, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(scope_x + 80, scope_y + 63, "R_in = 1 МОм", size=11, color=INK, bold=True))
    p.append(rect(scope_x + 20, scope_y + 90, 120, 36, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(scope_x + 80, scope_y + 113, "C_кабель + C_in ≈ 100 пФ", size=9, color=POS, bold=True))

    # З'єднувальні лінії
    p.append(line(probe_x + probe_w, probe_y + 58, scope_x, scope_y + 58, color=LINE, sw=1.5))
    p.append(line(probe_x + probe_w, probe_y + 108, scope_x, scope_y + 108, color=LINE, sw=1.5))

    # Формула компенсації внизу зліва
    p.append(rect(sx + 15, sy + 205, sw_box - 30, 42, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(sx + sw_box / 2, sy + 224, "Умова ідеальної компенсації: R₁ · C₁ = R_in · C_total", size=10, color=FIELD, bold=True))
    p.append(text(sx + sw_box / 2, sy + 238, "Коефіцієнт ділення: K = 1/10 на всіх частотах", size=9, color=INK))

    # Права частина: Три форми тестового меандру 1 кГц
    rx_base, ry_base = 415, 25
    rw_box, rh_box = 400, 260
    p.append(rect(rx_base, ry_base, rw_box, rh_box, fill="#1c2128", stroke=LINE, sw=1.2, rx=8))
    p.append(text(rx_base + rw_box / 2, ry_base + 22, "Калібрувальний сигнал 1 кГц на екрані осцилографа", size=12, color="#ffffff", bold=True))

    wave_cards = [
        {
            "y": ry_base + 40, "h": 62,
            "title": "Недокомпенсація (C₁ замала)",
            "desc": "Завалені фронти, заниження ВЧ",
            "color": NEG,
            "path": "M 20,44 L 50,44 L 50,22 Q 62,14 85,14 L 115,14 L 115,36 Q 127,44 150,44 L 180,44"
        },
        {
            "y": ry_base + 110, "h": 62,
            "title": "Ідеальна компенсація (R₁C₁ = R₂C₂)",
            "desc": "Строгий прямокутник, плоска вершина",
            "color": FIELD,
            "path": "M 20,44 L 50,44 L 50,14 L 115,14 L 115,44 L 180,44"
        },
        {
            "y": ry_base + 180, "h": 62,
            "title": "Перекомпенсація (C₁ завелика)",
            "desc": "Викиди на фронтах (хибний дзвін)",
            "color": POS,
            "path": "M 20,44 L 50,44 L 50,8 L 65,14 L 115,14 L 115,50 L 130,44 L 180,44"
        }
    ]

    for wc in wave_cards:
        box_y = wc["y"]
        p.append(rect(rx_base + 12, box_y, rw_box - 24, wc["h"], fill="#252c35", stroke="#3b4451", sw=1.0, rx=4))
        p.append(text(rx_base + 25, box_y + 22, wc["title"], size=10, color=wc["color"], bold=True, anchor="start"))
        p.append(text(rx_base + 25, box_y + 44, wc["desc"], size=9, color="#8b949e", anchor="start"))

        # Міні-осцилограма праворуч у картці
        ox_w = rx_base + rw_box - 175
        oy_w = box_y + 6
        p.append(rect(ox_w, oy_w, 150, 50, fill="#12161b", stroke="#30363d", sw=1.0, rx=3))
        # Сітка
        p.append(line(ox_w + 75, oy_w, ox_w + 75, oy_w + 50, color="#21262d", sw=0.8, dash="2 2"))
        p.append(line(ox_w, oy_w + 25, ox_w + 150, oy_w + 25, color="#21262d", sw=0.8, dash="2 2"))
        # Хвиля через path
        raw_pts = wc["path"]
        p.append('<g transform="translate(%.1f, %.1f)"><path d="%s" fill="none" stroke="%s" stroke-width="2.0"/></g>' %
                 (ox_w - 20, oy_w + 2, raw_pts, wc["color"]))

    render(os.path.join(OUT, "probe-rc-compensation.svg"), W, H, *p,
           title="RC-компенсація дільника щупа 10X та форми сигналу")


# ── ground-lead-inductance: Вплив індуктивності земляного крокодила ─────────
def fig_ground_lead_inductance():
    W, H = 820, 270
    p = []

    # Лівий блок: Довгий земляний крокодил (15 см)
    b1_x, b1_y, b1_w, b1_h = 30, 25, 360, 220
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fff5f5", stroke=POS, sw=1.4, rx=8))
    p.append(text(b1_x + b1_w / 2, b1_y + 22, "Довгий земляний дріт (10–15 см)", size=12, color=POS, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 38, "Паразитна індуктивність L ≈ 100–150 нГн", size=10, color=MUTED))

    # Схема LC контуру
    p.append(rect(b1_x + 20, b1_y + 52, b1_w - 40, 48, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(b1_x + b1_w / 2, b1_y + 70, "L_земля (120 нГн) + C_щупа (15 пФ)", size=10, color=INK, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 88, "Резонансна частота контуру: f₀ ≈ 120 МГц", size=10, color=POS))

    # Осцилограма з дзвоном
    p.append(rect(b1_x + 20, b1_y + 110, b1_w - 40, 75, fill="#1c2128", stroke="#30363d", sw=1.0, rx=4))
    # Сітка
    p.append(line(b1_x + b1_w / 2, b1_y + 110, b1_x + b1_w / 2, b1_y + 185, color="#252d38", sw=0.8, dash="2 2"))
    p.append(line(b1_x + 20, b1_y + 147, b1_x + b1_w - 20, b1_y + 147, color="#252d38", sw=0.8, dash="2 2"))
    # Крива з викидом і загасаючим дзвоном
    pts1 = [
        (b1_x + 35, b1_y + 170), (b1_x + 75, b1_y + 170),
        (b1_x + 85, b1_y + 120),  # різкий викид вгору
        (b1_x + 105, b1_y + 145), # провал
        (b1_x + 125, b1_y + 130), # викид 2
        (b1_x + 145, b1_y + 138), # провал 2
        (b1_x + 165, b1_y + 134), # затухання
        (b1_x + 325, b1_y + 135)  # стабільна лінія
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts1), POS))
    p.append(text(b1_x + b1_w / 2, b1_y + 204, "✖ Фальшивий дзвін та перерегулювання (ringing)", size=10, color=POS, bold=True))

    # Правий блок: Коротка земляна пружинка (< 5 мм)
    b2_x, b2_y, b2_w, b2_h = 430, 25, 360, 220
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f2faf4", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(b2_x + b2_w / 2, b2_y + 22, "Коротка земляна пружинка (< 5 мм)", size=12, color=FIELD, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 38, "Мінімальна індуктивність L < 5 нГн", size=10, color=MUTED))

    # Схема мінімальної індуктивності
    p.append(rect(b2_x + 20, b2_y + 52, b2_w - 40, 48, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    p.append(text(b2_x + b2_w / 2, b2_y + 70, "L_земля (< 5 нГн) + C_щупа (15 пФ)", size=10, color=INK, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 88, "Резонанс витіснений далеко за межі смуги (>600 МГц)", size=9, color=FIELD))

    # Осцилограма чиста
    p.append(rect(b2_x + 20, b2_y + 110, b2_w - 40, 75, fill="#1c2128", stroke="#30363d", sw=1.0, rx=4))
    p.append(line(b2_x + b2_w / 2, b2_y + 110, b2_x + b2_w / 2, b2_y + 185, color="#252d38", sw=0.8, dash="2 2"))
    p.append(line(b2_x + 20, b2_y + 147, b2_x + b2_w - 20, b2_y + 147, color="#252d38", sw=0.8, dash="2 2"))
    # Чистий прямокутний фронт
    pts2 = [
        (b2_x + 35, b2_y + 170), (b2_x + 75, b2_y + 170),
        (b2_x + 85, b2_y + 135),  # крутий фронт
        (b2_x + 325, b2_y + 135)  # ідеальна плоска поличка
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts2), FIELD))
    p.append(text(b2_x + b2_w / 2, b2_y + 204, "✓ Справжній чистий фронт цифрового сигналу", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "ground-lead-inductance.svg"), W, H, *p,
           title="Вплив довжини земляного проводу на форму вимірюваного сигналу")


# ── cartridge-vs-traditional-iron: Традиційний паяльник проти картриджа ────
def fig_cartridge_vs_traditional_iron():
    W, H = 820, 280
    p = []

    # Ліва половина: Класичний паяльник (900M)
    x1, y1, w1, h1 = 30, 25, 365, 230
    p.append(rect(x1, y1, w1, h1, fill="#fdfbf7", stroke=POS, sw=1.4, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 22, "Традиційний паяльник (наприклад, 900M)", size=12, color=POS, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 38, "Роздільний нагрівач і насадне жало", size=10, color=MUTED))

    # Схема шарів 900M
    p.append(rect(x1 + 20, y1 + 52, 90, 70, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    p.append(text(x1 + 65, y1 + 80, "Керамічний", size=9, color=POS, bold=True))
    p.append(text(x1 + 65, y1 + 95, "нагрівач + ТП", size=9, color=POS))

    # Повітряний зазор
    p.append(rect(x1 + 115, y1 + 52, 38, 70, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=2))
    p.append(text(x1 + 134, y1 + 80, "Зазор", size=9, color="#b45309", bold=True))
    p.append(text(x1 + 134, y1 + 96, "повітря", size=9, color="#b45309"))

    # Мідне жало
    p.append(rect(x1 + 158, y1 + 52, 182, 70, fill="#fed7aa", stroke="#c2410c", sw=1.0, rx=4))
    p.append(text(x1 + 249, y1 + 80, "Масивне знімне жало", size=10, color="#9a3412", bold=True))
    p.append(text(x1 + 249, y1 + 98, "Кінчик жала (точка пайки)", size=9, color=INK))

    # Список недоліків
    p.append(text(x1 + 20, y1 + 145, "• Термопара всередині нагрівача, далеко від кінчика", size=9, color=INK, anchor="start"))
    p.append(text(x1 + 20, y1 + 165, "• Величезний тепловий опір повітряного зазору", size=9, color=INK, anchor="start"))
    p.append(text(x1 + 20, y1 + 185, "• Температура кінчика просідає на 40–80 °C на полігонах", size=9, color=POS, anchor="start", bold=True))
    p.append(text(x1 + 20, y1 + 205, "• Повільна реакція зворотного зв'язку (5–15 секунд)", size=9, color=INK, anchor="start"))

    # Права половина: Картриджні системи (T12 / C245)
    x2, y2, w2, h2 = 425, 25, 365, 230
    p.append(rect(x2, y2, w2, h2, fill="#f2faf4", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 22, "Картриджна система (T12 / C245)", size=12, color=FIELD, bold=True))
    p.append(text(x2 + w2 / 2, y2 + 38, "Монолітний картридж «все-в-одному»", size=10, color=MUTED))

    # Схема монолітного картриджа
    p.append(rect(x2 + 20, y2 + 52, 320, 70, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x2 + 180, y2 + 75, "Монолітний картридж із прямим контактом", size=10, color=FIELD, bold=True))
    p.append(rect(x2 + 30, y2 + 88, 140, 24, fill="#ffffff", stroke=FIELD, sw=0.8, rx=3))
    p.append(text(x2 + 100, y2 + 104, "Нагрівач + термопара", size=9, color=INK))
    p.append(rect(x2 + 180, y2 + 88, 150, 24, fill="#bbf7d0", stroke=FIELD, sw=0.8, rx=3))
    p.append(text(x2 + 255, y2 + 104, "Жало (в 2–3 мм від ТП)", size=9, color=FIELD, bold=True))

    # Список переваг
    p.append(text(x2 + 20, y2 + 145, "• Термопара розміщена впритул до робочої зони жала", size=9, color=INK, anchor="start"))
    p.append(text(x2 + 20, y2 + 165, "• Відсутність повітряного зазору (пряма теплопередача)", size=9, color=INK, anchor="start"))
    p.append(text(x2 + 20, y2 + 185, "• Миттєве форсування потужності при контакті з міддю", size=9, color=FIELD, anchor="start", bold=True))
    p.append(text(x2 + 20, y2 + 205, "• Відновлення температури за 1–2 секунди", size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "cartridge-vs-traditional-iron.svg"), W, H, *p,
           title="Порівняння традиційного паяльника та картриджного жала")


# ── epa-grounding-circuit: Схема заземлення робочого місця (EPA) ────────────
def fig_epa_grounding_circuit():
    W, H = 820, 300
    p = []

    # Загальний контур робочого простору
    p.append(rect(25, 20, 770, 260, fill="#fcfdfe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(W / 2, 42, "Антистатична зона (EPA) та єдина точка заземлення", size=13, color=INK, bold=True))

    # Антистатичний килимок на столі
    mat_x, mat_y, mat_w, mat_h = 50, 65, 430, 110
    p.append(rect(mat_x, mat_y, mat_w, mat_h, fill="#dbeafe", stroke=NEG, sw=1.5, rx=6))
    p.append(text(mat_x + mat_w / 2, mat_y + 24, "Антистатичний килимок (двошаровий каучук)", size=11, color=NEG, bold=True))
    p.append(text(mat_x + mat_w / 2, mat_y + 44, "Верхній шар: розсіювальний (10⁶–10⁸ Ом/кв)", size=9, color=INK))
    p.append(text(mat_x + mat_w / 2, mat_y + 60, "Нижній шар: провідний (10³–10⁵ Ом/кв)", size=9, color=INK))

    # Плата на килимку
    p.append(rect(mat_x + 140, mat_y + 72, 150, 30, fill="#22c55e", stroke="#15803d", sw=1.0, rx=3))
    p.append(text(mat_x + 215, mat_y + 91, "Тестована плата (DUT)", size=9, color="#ffffff", bold=True))

    # Антистатичний браслет
    br_x, br_y, br_w, br_h = 520, 65, 250, 110
    p.append(rect(br_x, br_y, br_w, br_h, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(br_x + br_w / 2, br_y + 24, "Антистатичний браслет", size=11, color="#b45309", bold=True))
    p.append(text(br_x + br_w / 2, br_y + 42, "Контакт із тілом людини", size=9, color=MUTED))

    # Захисний резистор 1 МОм всередині браслета
    p.append(rect(br_x + 20, br_y + 55, br_w - 40, 42, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(br_x + br_w / 2, br_y + 73, "Вбудований резистор 1 МОм", size=10, color=POS, bold=True))
    p.append(text(br_x + br_w / 2, br_y + 88, "Захист людини від фази 230 В (I < 0.25 мА)", size=9, color=INK))

    # Єдина шина / точка заземлення (Common Ground Point)
    cgp_x, cgp_y, cgp_w, cgp_h = 240, 215, 340, 50
    p.append(rect(cgp_x, cgp_y, cgp_w, cgp_h, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=6))
    p.append(text(cgp_x + cgp_w / 2, cgp_y + 22, "Головна точка заземлення столу (Common Ground Point)", size=11, color="#1e293b", bold=True))
    p.append(text(cgp_x + cgp_w / 2, cgp_y + 38, "Пряме з'єднання з захисним PE-провідником будівлі", size=9, color=MUTED))

    # Лінії заземлення до CGP
    # 1. Від килимка
    p.append(line(mat_x + 80, mat_y + mat_h, cgp_x + 50, cgp_y, color=NEG, sw=1.6))
    p.append(circle(mat_x + 80, mat_y + mat_h, 3.5, fill=NEG, stroke=NEG))
    p.append(circle(cgp_x + 50, cgp_y, 3.5, fill=NEG, stroke=NEG))
    p.append(text(mat_x + 40, mat_y + mat_h + 20, "1 МОм", size=9, color=NEG, bold=True))

    # 2. Від браслета
    p.append(line(br_x + 125, br_y + br_h, cgp_x + 280, cgp_y, color="#d97706", sw=1.6))
    p.append(circle(br_x + 125, br_y + br_h, 3.5, fill="#d97706", stroke="#d97706"))
    p.append(circle(cgp_x + 280, cgp_y, 3.5, fill="#d97706", stroke="#d97706"))

    # 3. Від захисного заземлення паяльника й приладів
    p.append(line(cgp_x + 170, cgp_y + cgp_h, cgp_x + 170, cgp_y + cgp_h + 15, color=FIELD, sw=2.0))
    p.append(text(cgp_x + 170, cgp_y + cgp_h + 12, "⏚ Захисне заземлення (PE)", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "epa-grounding-circuit.svg"), W, H, *p,
           title="Схема антистатичного захисту робочого місця інженера")


if __name__ == "__main__":
    fig_instruments_trio()
    fig_probe_rc_compensation()
    fig_ground_lead_inductance()
    fig_cartridge_vs_traditional_iron()
    fig_epa_grounding_circuit()
    print("Всі фігури згенеровано успішно.")
