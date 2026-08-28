# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (cx, cy, rx, ry, fill, stroke, sw))


# ── 1. moisture-ingress-mechanisms: Три механізми проникнення вологи ─────────
def fig_moisture_ingress():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Три фізичні механізми проникнення вологи в закритий корпус", size=15, color=INK, bold=True))

    col_w = 280
    gap = 25
    y0 = 55
    bh = 395

    # Блок 1: Капілярний ефект по жилах
    x1 = 30
    p.append(rect(x1, y0, col_w, bh, fill="#fdfbf7", stroke="#d35400", sw=1.8, rx=8))
    p.append(text(x1 + col_w / 2, y0 + 26, "1. Капілярний ефект (Wicking)", size=13, color="#d35400", bold=True))
    p.append(text(x1 + col_w / 2, y0 + 44, "Перетік вздовж жил кабелю", size=10.5, color=MUTED))

    # Схема кабелю
    cx1 = x1 + col_w / 2
    p.append(rect(cx1 - 100, y0 + 65, 200, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(rect(cx1 - 90, y0 + 75, 180, 50, fill="#fadbd8", stroke=POS, sw=1.2, rx=3))
    # Жили
    for dy in [-12, -4, 4, 12]:
        p.append(line(cx1 - 85, y0 + 100 + dy, cx1 + 85, y0 + 100 + dy, color="#b9770e", sw=2.5))
    # Вода заходить під ізоляцію
    p.append(arrow(cx1 - 120, y0 + 100, cx1 - 92, y0 + 100, color=NEG, sw=3))
    p.append(text(cx1 - 122, y0 + 90, "Вода", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(cx1, y0 + 155, "Капілярний тиск у жилах:", size=10.5, color=INK, bold=True))
    p.append(text(cx1, y0 + 175, "h = (2 · γ · cos θ) / (ρ · g · r)", size=11, color="#d35400", bold=True))

    p.append(text(cx1, y0 + 215, "• Сальник обтискає оболонку,", size=10, color=INK))
    p.append(text(cx1, y0 + 233, "  але зазори r ≈ 5–20 мкм", size=10, color=INK))
    p.append(text(cx1, y0 + 251, "  між жилами лишаються вільними", size=10, color=INK))
    p.append(text(cx1, y0 + 275, "• Вода піднімається на висоту", size=10, color=INK))
    p.append(text(cx1, y0 + 293, "  до 0.5–1.5 м прямо на плату", size=10, color=POS, bold=True))
    p.append(text(cx1, y0 + 325, "Захист: water-block заливка,", size=10, color=FIELD, bold=True))
    p.append(text(cx1, y0 + 343, "розтин ізоляції у гермовводі,", size=10, color=FIELD))
    p.append(text(cx1, y0 + 361, "прохідні болти (penetrators)", size=10, color=FIELD))

    # Блок 2: Динамічний тиск
    x2 = x1 + col_w + gap
    p.append(rect(x2, y0, col_w, bh, fill="#f4f8fb", stroke=NEG, sw=1.8, rx=8))
    p.append(text(x2 + col_w / 2, y0 + 26, "2. Динамічний напір води", size=13, color=NEG, bold=True))
    p.append(text(x2 + col_w / 2, y0 + 44, "Швидкість човна / удари хвиль", size=10.5, color=MUTED))

    # Схема напору
    cx2 = x2 + col_w / 2
    p.append(rect(cx2 - 80, y0 + 65, 160, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    # Стик корпусу
    p.append(line(cx2, y0 + 65, cx2, y0 + 135, color=POS, sw=2))
    p.append(arrow(cx2 - 110, y0 + 85, cx2 - 5, y0 + 85, color=NEG, sw=3))
    p.append(arrow(cx2 - 110, y0 + 115, cx2 - 5, y0 + 115, color=NEG, sw=3))
    p.append(text(cx2 - 112, y0 + 100, "v = 15 м/с", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(cx2, y0 + 155, "Швидкісний тиск гальмування:", size=10.5, color=INK, bold=True))
    p.append(text(cx2, y0 + 175, "q = 0.5 · ρ · v² ≈ 112.5 кПа", size=11, color=NEG, bold=True))

    p.append(text(cx2, y0 + 215, "• Статичний IP67 = 1 м (10 кПа)", size=10, color=INK))
    p.append(text(cx2, y0 + 233, "• Швидкісний напір на 54 км/год", size=10, color=INK))
    p.append(text(cx2, y0 + 251, "  еквівалентний глибині 11.5 м!", size=10, color=POS, bold=True))
    p.append(text(cx2, y0 + 275, "• Струмінь відгинає плоскі", size=10, color=INK))
    p.append(text(cx2, y0 + 293, "  кромки та ковпачки сальників", size=10, color=INK))
    p.append(text(cx2, y0 + 325, "Захист: замкнені пази O-ring,", size=10, color=FIELD, bold=True))
    p.append(text(cx2, y0 + 343, "жорсткі фланці, захисні", size=10, color=FIELD))
    p.append(text(cx2, y0 + 361, "дефлектори та лабіринти", size=10, color=FIELD))

    # Блок 3: Термодинамічне дихання
    x3 = x2 + col_w + gap
    p.append(rect(x3, y0, col_w, bh, fill="#fbf5f5", stroke=POS, sw=1.8, rx=8))
    p.append(text(x3 + col_w / 2, y0 + 26, "3. Термічне «дихання»", size=13, color=POS, bold=True))
    p.append(text(x3 + col_w / 2, y0 + 44, "Цикл нагріву й охолодження", size=10.5, color=MUTED))

    # Схема насоса
    cx3 = x3 + col_w / 2
    p.append(rect(cx3 - 80, y0 + 65, 160, 70, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx3, y0 + 90, "+65 °C → +10 °C у воді", size=10, color=POS, bold=True))
    p.append(text(cx3, y0 + 115, "ΔP ≈ −16 кПа (вакуум)", size=10.5, color=NEG, bold=True))
    p.append(arrow(cx3 + 95, y0 + 100, cx3 + 70, y0 + 100, color=NEG, sw=3))
    p.append(text(cx3 + 100, y0 + 100, "Всмоктування", size=9.5, color=NEG, anchor="start", bold=True))
    p.append(text(cx3, y0 + 155, "Закон стану ідеального газу:", size=10.5, color=INK, bold=True))
    p.append(text(cx3, y0 + 175, "P₁ / T₁ = P₂ / T₂", size=11, color=POS, bold=True))

    p.append(text(cx3, y0 + 215, "• При нагріві повітря виходить", size=10, color=INK))
    p.append(text(cx3, y0 + 233, "  крізь мікрощілини назовні", size=10, color=INK))
    p.append(text(cx3, y0 + 251, "• При різкому охолодженні", size=10, color=INK))
    p.append(text(cx3, y0 + 275, "  утворюється глибокий вакуум,", size=10, color=POS, bold=True))
    p.append(text(cx3, y0 + 293, "  що засмоктує воду крізь шви", size=10, color=POS, bold=True))
    p.append(text(cx3, y0 + 325, "Захист: ePTFE Gore-Tex", size=10, color=FIELD, bold=True))
    p.append(text(cx3, y0 + 343, "дихальні клапани (Vents),", size=10, color=FIELD))
    p.append(text(cx3, y0 + 361, "вирівнювання тиску ΔP = 0", size=10, color=FIELD))

    render(os.path.join(OUT, "moisture-ingress-mechanisms.svg"), W, H, *p,
           title="Три фізичні механізми проникнення вологи в закритий корпус")


# ── 2. oring-groove-design: Конструкція паза O-Ring за ISO 3601-2 ────────────
def fig_oring():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 28, "Канонічний розрахунок прямокутного паза O-Ring (ISO 3601-2)", size=15, color=INK, bold=True))

    # Ліва частина: Геометрія та стиснення
    bx1, by, bw, bh = 40, 55, 420, 380
    p.append(rect(bx1, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(bx1 + bw / 2, by + 26, "Геометрія паза та стиснення шнура", size=13, color=INK, bold=True))

    # Схема перерізу
    cx1 = bx1 + bw / 2
    cy1 = by + 140

    # Нижня основа з пазом
    p.append(rect(cx1 - 150, cy1 - 10, 300, 110, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    # Виріз паза
    gw, gh = 120, 60
    p.append(rect(cx1 - gw / 2, cy1 - 10, gw, gh, fill="#ffffff", stroke="#334155", sw=2))
    # Верхня кришка
    p.append(rect(cx1 - 150, cy1 - 40, 300, 25, fill="#cbd5e1", stroke="#64748b", sw=1.5))

    # Деформоване кільце (еліпс у стисненому стані)
    p.append(ellipse(cx1, cy1 + gh / 2 - 10, 48, 24, fill="#fecaca", stroke=POS, sw=2))
    # Контур початкового круглого перерізу пунктиром
    p.append(circle(cx1, cy1 + gh / 2 - 10, 30, fill="none", stroke=MUTED, sw=1.5))

    # Розмірні лінії
    # Глибина h
    p.append(line(cx1 + gw / 2 + 15, cy1 - 10, cx1 + gw / 2 + 15, cy1 - 10 + gh, color=INK, sw=1.2))
    p.append(text(cx1 + gw / 2 + 25, cy1 + 22, "h (глибина)", size=10.5, color=INK, anchor="start"))
    # Ширина b
    p.append(line(cx1 - gw / 2, cy1 + gh + 10, cx1 + gw / 2, cy1 + gh + 10, color=INK, sw=1.2))
    p.append(text(cx1, cy1 + gh + 26, "b (ширина паза)", size=10.5, color=INK))
    # Діаметр вільного перерізу d2
    p.append(text(cx1 - 55, cy1 + 6, "d₂", size=11, color=MUTED, bold=True))

    # Пояснення параметрів
    p.append(text(cx1, by + 260, "Ключові розрахункові інваріанти:", size=11, color=FIELD, bold=True))
    p.append(text(cx1, by + 285, "1. Стиснення (Squeeze): S = (d₂ − h) / d₂ = 18–28%", size=10.5, color=INK, bold=True))
    p.append(text(cx1, by + 308, "2. Заповнення (Groove Fill): GF = A_oring / A_groove = 70–82%", size=10.5, color=INK, bold=True))
    p.append(text(cx1, by + 331, "3. Розтяг по ID (Stretch): ID_str = 1.5–4% (макс 6%)", size=10.5, color=INK))
    p.append(text(cx1, by + 354, "4. Радіуси скруглення кутів: R₁ = 0.4–0.8 мм, R₂ = 0.2 мм", size=10, color=MUTED))

    # Права частина: Фізика самоущільнення та ризики
    bx2 = bx1 + bw + 20
    p.append(rect(bx2, by, bw, bh, fill="#fffaf5", stroke="#d97706", sw=1.5, rx=8))
    p.append(text(bx2 + bw / 2, by + 26, "Ефект самоущільнення та типові аварії", size=13, color="#d97706", bold=True))

    cx2 = bx2 + bw / 2
    # Схема тиску рідини
    cy2 = by + 140
    p.append(rect(cx2 - 150, cy2 - 10, 300, 110, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    p.append(rect(cx2 - gw / 2, cy2 - 10, gw, gh, fill="#ffffff", stroke="#334155", sw=2))
    p.append(rect(cx2 - 150, cy2 - 40, 300, 25, fill="#cbd5e1", stroke="#64748b", sw=1.5))

    # Кільце, зміщене в правий кут під тиском
    p.append(ellipse(cx2 + 15, cy2 + gh / 2 - 10, 42, 24, fill="#bbf7d0", stroke=FIELD, sw=2))
    # Стрілки тиску зліва
    p.append(arrow(cx2 - gw / 2 + 5, cy2 + 15, cx2 - 10, cy2 + 15, color=NEG, sw=2.5))
    p.append(arrow(cx2 - gw / 2 + 5, cy2 + 30, cx2 - 10, cy2 + 30, color=NEG, sw=2.5))
    p.append(text(cx2 - 35, cy2 - 18, "Тиск води P", size=10.5, color=NEG, bold=True))

    p.append(text(cx2, by + 260, "Чому паз не можна заповнювати на 100%:", size=11, color=POS, bold=True))
    p.append(text(cx2, by + 285, "• Гума нестислива за об'ємом (коефіцієнт Пуассона ν ≈ 0.5)", size=10, color=INK))
    p.append(text(cx2, by + 305, "• Теплове розширення гуми у 10× більше за алюміній", size=10, color=INK))
    p.append(text(cx2, by + 325, "• Набухання в мастилі додає 3–8% об'єму", size=10, color=INK))
    p.append(text(cx2, by + 350, "Переповнений паз (>90%) вигинає кришку або зрізає O-ring!", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "oring-groove-design.svg"), W, H, *p,
           title="Канонічний розрахунок прямокутного паза O-Ring за стандартом ISO 3601-2")


# ── 3. board-protection-methods: Покриття (Conformal Coating) vs Заливка (Potting)
def fig_protection():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 28, "Захист електроніки на рівні плати: Conformal Coating проти Potting", size=15, color=INK, bold=True))

    col_w = 420
    by = 55
    bh = 380

    # Ліва колонка: Конформне покриття
    bx1 = 40
    p.append(rect(bx1, by, col_w, bh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx1 + col_w / 2, by + 26, "Конформне покриття (Conformal Coating)", size=13.5, color=FIELD, bold=True))
    p.append(text(bx1 + col_w / 2, by + 46, "Тонка полімерна плівка товщиною 25–75 мкм", size=10.5, color=MUTED))

    # Схема плати з лаком
    cx1 = bx1 + col_w / 2
    cy1 = by + 120
    # PCB
    p.append(rect(cx1 - 160, cy1, 320, 18, fill="#15803d", stroke="#166534", sw=1.5, rx=2))
    # Компоненти
    p.append(rect(cx1 - 120, cy1 - 25, 60, 25, fill="#334155", stroke="#0f172a", sw=1.2, rx=2))
    p.append(text(cx1 - 90, cy1 - 8, "MCU", size=9.5, color="#ffffff", bold=True))
    p.append(rect(cx1 - 30, cy1 - 15, 35, 15, fill="#94a3b8", stroke="#475569", sw=1, rx=1))
    p.append(text(cx1 - 12, cy1 - 3, "LDO", size=9.5, color="#ffffff"))
    # Барометр (не покритий!)
    p.append(rect(cx1 + 40, cy1 - 20, 45, 20, fill="#f59e0b", stroke="#b45309", sw=1.2, rx=2))
    p.append(text(cx1 + 62, cy1 - 6, "Baro", size=9.5, color="#ffffff", bold=True))
    # Тонка плівка покриття
    p.append(line(cx1 - 160, cy1 - 3, cx1 - 125, cy1 - 3, color="#4ade80", sw=4))
    p.append(line(cx1 - 125, cy1 - 28, cx1 - 55, cy1 - 28, color="#4ade80", sw=4))
    p.append(line(cx1 - 55, cy1 - 3, cx1 - 35, cy1 - 3, color="#4ade80", sw=4))
    p.append(line(cx1 - 35, cy1 - 18, cx1 + 10, cy1 - 18, color="#4ade80", sw=4))
    p.append(line(cx1 + 10, cy1 - 3, cx1 + 35, cy1 - 3, color="#4ade80", sw=4))
    # Без покриття на барометрі!
    p.append(line(cx1 + 90, cy1 - 3, cx1 + 160, cy1 - 3, color="#4ade80", sw=4))
    p.append(text(cx1 + 62, cy1 - 30, "Маскування!", size=9.5, color=POS, bold=True))

    p.append(text(cx1, by + 190, "Матеріали за IPC-CC-830:", size=11, color=INK, bold=True))
    p.append(text(cx1, by + 212, "• Акрил (AR) — легко наносити і змивати при пайці", size=10, color=INK))
    p.append(text(cx1, by + 232, "• Поліуретан (UR) — висока хімічна стійкість", size=10, color=INK))
    p.append(text(cx1, by + 252, "• Силікон (SR) — еластичний, термостійкий (−50..+200 °C)", size=10, color=INK))
    p.append(text(cx1, by + 272, "• Парилен (XY) — безпорова плівка з вакуумної фази", size=10, color=INK))

    p.append(text(cx1, by + 305, "Переваги та обмеження:", size=11, color=FIELD, bold=True))
    p.append(text(cx1, by + 327, "✓ Мінімальна додаткова маса (грами)", size=10, color=FIELD))
    p.append(text(cx1, by + 345, "✓ Зберігає можливість діагностики й ремонту", size=10, color=FIELD))
    p.append(text(cx1, by + 363, "✗ Не захищає від тиску води при тривалому зануренні", size=10, color=POS))

    # Права колонка: Заливка компаундом (Potting)
    bx2 = bx1 + col_w + 20
    p.append(rect(bx2, by, col_w, bh, fill="#f8fafc", stroke="#3b82f6", sw=1.8, rx=8))
    p.append(text(bx2 + col_w / 2, by + 26, "Компаундування (Potting / Encapsulation)", size=13.5, color="#2563eb", bold=True))
    p.append(text(bx2 + col_w / 2, by + 46, "Монолітна заливка всього об'єму смолою", size=10.5, color=MUTED))

    # Схема плати у смолі
    cx2 = bx2 + col_w / 2
    # Корпус боксу
    p.append(rect(cx2 - 160, cy1 - 45, 320, 80, fill="#bfdbfe", stroke="#3b82f6", sw=1.5, rx=4))
    # PCB
    p.append(rect(cx2 - 140, cy1 + 10, 280, 15, fill="#15803d", stroke="#166534", sw=1.2, rx=2))
    p.append(rect(cx2 - 80, cy1 - 15, 60, 25, fill="#334155", stroke="#0f172a", sw=1.2, rx=2))
    p.append(text(cx2 - 50, cy1 + 2, "ESC", size=10, color="#ffffff", bold=True))
    p.append(text(cx2, cy1 - 25, "Суцільний шар компаунду (PU / Epoxy)", size=10, color="#1e40af", bold=True))

    p.append(text(cx2, by + 190, "Матеріали компаундів:", size=11, color=INK, bold=True))
    p.append(text(cx2, by + 212, "• Поліуретан (PU) — гнучкий, гасить ударні навантаження", size=10, color=INK))
    p.append(text(cx2, by + 232, "• Епоксид (Epoxy) — максимальна міцність, адгезія", size=10, color=INK))
    p.append(text(cx2, by + 252, "• Теплопровідний силікон — краще відводить тепло", size=10, color=INK))
    p.append(text(cx2, by + 272, "• Вакуумна дегазація усуває бульбашки повітря", size=10, color=INK))

    p.append(text(cx2, by + 305, "Переваги та обмеження:", size=11, color="#2563eb", bold=True))
    p.append(text(cx2, by + 327, "✓ Абсолютний захист від води, тиску й вібрацій", size=10, color=FIELD))
    p.append(text(cx2, by + 345, "✗ Неможливість ремонту (одноразовий модуль)", size=10, color=POS))
    p.append(text(cx2, by + 363, "✗ Ризик відриву пайок через різницю розширення (CTE)", size=10, color=POS))

    render(os.path.join(OUT, "board-protection-methods.svg"), W, H, *p,
           title="Порівняння конформного покриття та компаундування друкованої плати")


# ── 4. sealed-thermal-management: Тепловідведення в герметичному корпусі ─────
def fig_thermal():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 28, "Шлях тепловідведення в герметичному металевому корпусі", size=15, color=INK, bold=True))

    # Ліва частина: Повітряний бар'єр (як ламається)
    bx1, by, bw, bh = 40, 55, 420, 380
    p.append(rect(bx1, by, bw, bh, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(bx1 + bw / 2, by + 26, "Помилка: Повітряний зазор у боксі", size=13.5, color=POS, bold=True))
    p.append(text(bx1 + bw / 2, by + 46, "Повітря як ефективний теплоізолятор", size=10.5, color=MUTED))

    cx1 = bx1 + bw / 2
    cy1 = by + 130
    # Корпус боксу
    p.append(rect(cx1 - 150, cy1 - 40, 300, 90, fill="#ffffff", stroke="#991b1b", sw=2, rx=4))
    # Плата з гарячим чипом
    p.append(rect(cx1 - 110, cy1 + 15, 220, 12, fill="#15803d", stroke="#166534", sw=1.2, rx=2))
    p.append(rect(cx1 - 40, cy1 - 15, 80, 30, fill="#fca5a5", stroke=POS, sw=1.5, rx=3))
    p.append(text(cx1, cy1 + 4, "SoC / ESC (15 Вт)", size=10, color=POS, bold=True))

    p.append(text(cx1, cy1 - 24, "Повітряний зазор: k = 0.026 Вт/(м·К)", size=10, color=POS, bold=True))
    p.append(text(cx1, cy1 + 40, "T_кристал > +110 °C (Тротлінг / Перегрів)", size=10.5, color=POS, bold=True))

    p.append(text(cx1, by + 225, "Термодинамічна пастка замкненого об'єму:", size=11, color=POS, bold=True))
    p.append(text(cx1, by + 250, "• Природна конвекція у вузькому зазорі придушена", size=10, color=INK))
    p.append(text(cx1, by + 270, "• Тепловий опір повітря: R_th > 12–18 °C/Вт", size=10, color=POS, bold=True))
    p.append(text(cx1, by + 290, "• Тепло акумулюється всередині гермоблоку", size=10, color=INK))
    p.append(text(cx1, by + 310, "• Батареї та кристали перегріваються за 10–15 хв", size=10, color=INK))
    p.append(text(cx1, by + 345, "Висновок: герметичний бокс не можна", size=10.5, color=POS, bold=True))
    p.append(text(cx1, by + 363, "залишати з порожнім повітряним прошарком!", size=10.5, color=POS, bold=True))

    # Права частина: Прямий тепловий міст на алюміній
    bx2 = bx1 + bw + 20
    p.append(rect(bx2, by, bw, bh, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx2 + bw / 2, by + 26, "Правильно: Прямий тепловий міст (Thermal Bridge)", size=13.5, color=FIELD, bold=True))
    p.append(text(bx2 + bw / 2, by + 46, "Thermal Pad + Алюмінієвий корпус + Вода", size=10.5, color=MUTED))

    cx2 = bx2 + bw / 2
    # Алюмінієвий корпус зі стінкою
    p.append(rect(cx2 - 150, cy1 - 40, 300, 90, fill="#f1f5f9", stroke="#334155", sw=2, rx=4))
    # Верхня товста стінка з ребрами
    p.append(rect(cx2 - 150, cy1 - 40, 300, 20, fill="#94a3b8", stroke="#475569", sw=1.5))
    for rx in [-120, -80, -40, 0, 40, 80, 120]:
        p.append(line(cx2 + rx, cy1 - 40, cx2 + rx, cy1 - 55, color="#475569", sw=3))
    # Плата
    p.append(rect(cx2 - 110, cy1 + 25, 220, 12, fill="#15803d", stroke="#166534", sw=1.2, rx=2))
    # Гарячий чип
    p.append(rect(cx2 - 40, cy1 - 5, 80, 30, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=3))
    p.append(text(cx2, cy1 + 14, "SoC / ESC", size=10, color="#c2410c", bold=True))
    # Thermal Pad між чипом і корпусом
    p.append(rect(cx2 - 42, cy1 - 22, 84, 17, fill="#86efac", stroke=FIELD, sw=1.5))
    p.append(text(cx2, cy1 - 9, "Thermal Pad (k=6 Вт/мК)", size=9.5, color="#14532d", bold=True))

    p.append(text(cx2, cy1 + 45, "T_кристал < +55 °C (Стабільна робота)", size=10.5, color=FIELD, bold=True))
    p.append(text(cx2, cy1 - 65, "Зовнішній теплообмін у воді: h = 1000–2500 Вт/(м²·К)", size=9.5, color=NEG, bold=True))

    p.append(text(cx2, by + 225, "Переваги прямого теплового контакту:", size=11, color=FIELD, bold=True))
    p.append(text(cx2, by + 250, "• Thermal Pad стискається на 25–40% без тиску на кристал", size=10, color=INK))
    p.append(text(cx2, by + 270, "• Сумарний опір R_th ланцюга: < 1.2 °C/Вт", size=10, color=FIELD, bold=True))
    p.append(text(cx2, by + 290, "• Алюмінієвий сплав (6061) k ≈ 160–180 Вт/(м·К)", size=10, color=INK))
    p.append(text(cx2, by + 310, "• Вода зовні має гігантську тепловіддачу h_вода", size=10, color=INK))
    p.append(text(cx2, by + 345, "Корпус катера/ровера розсіює десятки ватів", size=10.5, color=FIELD, bold=True))
    p.append(text(cx2, by + 363, "тепла прямо у водойму або забортне повітря!", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "sealed-thermal-management.svg"), W, H, *p,
           title="Шлях тепловідведення в герметичному металевому корпусі")


if __name__ == "__main__":
    fig_moisture_ingress()
    fig_oring()
    fig_protection()
    fig_thermal()
    print("All 4 figures rendered successfully.")
