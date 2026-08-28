# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. visual-degradation-stages: 3 стадії візуального старіння ───────────────
def fig_visual_degradation_stages():
    W, H = 880, 420
    p = []

    p.append(text(W / 2, 28, "Три стадії візуальної деградації та старіння телеметрії (Data Ageing)", size=15, bold=True))

    pw, ph = 260, 345
    py = 55
    xs = [30, 310, 590]

    # ── Панель 1: Свіжі дані (0..500 мс) ──
    p1_x = xs[0]
    p.append(rect(p1_x, py, pw, ph, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(p1_x + pw / 2, py + 26, "1. Свіжі дані (0 .. 500 мс)", size=12.5, color=FIELD, bold=True))
    p.append(text(p1_x + pw / 2, py + 45, "Штатний потік оновлення", size=10, color=MUTED))

    # Візуальний віджет
    p.append(rect(p1_x + 15, py + 60, pw - 30, 160, fill="#ffffff", stroke="#a3d9b1", sw=1.2, rx=6))
    p.append(rect(p1_x + 25, py + 72, 85, 22, fill="#eaf7ed", stroke=FIELD, sw=1, rx=4))
    p.append(text(p1_x + 67, py + 87, "● СВІЖО", size=10, color=FIELD, bold=True))
    p.append(text(p1_x + pw - 35, py + 87, "10 Гц", size=10, color=MUTED, anchor="end"))

    p.append(text(p1_x + 30, py + 120, "ВИСОТА:", size=11, color=MUTED, anchor="start"))
    p.append(text(p1_x + pw - 30, py + 120, "120.4 м", size=14, color=INK, anchor="end", bold=True))

    p.append(text(p1_x + 30, py + 150, "ШВИДКІСТЬ:", size=11, color=MUTED, anchor="start"))
    p.append(text(p1_x + pw - 30, py + 150, "22.1 м/с", size=14, color=INK, anchor="end", bold=True))

    p.append(text(p1_x + 30, py + 180, "БАТАРЕЯ:", size=11, color=MUTED, anchor="start"))
    p.append(text(p1_x + pw - 30, py + 180, "86 %", size=14, color=FIELD, anchor="end", bold=True))

    # Опис правил
    p.append(rect(p1_x + 15, py + 235, pw - 30, 95, fill="#ffffff", stroke="#d1e7dd", sw=1, rx=5))
    p.append(text(p1_x + pw / 2, py + 255, "Правила відображення:", size=10.5, color=FIELD, bold=True))
    p.append(text(p1_x + pw / 2, py + 275, "• Повний 100% контраст шрифтів", size=9.5, color=INK))
    p.append(text(p1_x + pw / 2, py + 295, "• Штатні нейтральні кольори", size=9.5, color=INK))
    p.append(text(p1_x + pw / 2, py + 315, "• Пряма довіра оператора", size=9.5, color=INK))


    # ── Панель 2: Попередня втрата (500..2000 мс) ──
    p2_x = xs[1]
    p.append(rect(p2_x, py, pw, ph, fill="#fffdf5", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(p2_x + pw / 2, py + 26, "2. Деградація (500 .. 2000 мс)", size=12.5, color="#d97706", bold=True))
    p.append(text(p2_x + pw / 2, py + 45, "Пропуск пакетів або затримка", size=10, color=MUTED))

    # Візуальний віджет
    p.append(rect(p2_x + 15, py + 60, pw - 30, 160, fill="#ffffff", stroke="#fcd34d", sw=1.5, rx=6))
    p.append(rect(p2_x + 25, py + 72, 95, 22, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(p2_x + 72, py + 87, "⏱ ВІК +1.4с", size=10, color="#b45309", bold=True))
    p.append(text(p2_x + pw - 35, py + 87, "STALE?", size=10, color="#d97706", anchor="end", bold=True))

    # Зблідлий текст (50% ghosting)
    p.append(text(p2_x + 30, py + 120, "ВИСОТА:", size=11, color="#9ca3af", anchor="start"))
    p.append(text(p2_x + pw - 30, py + 120, "120.4 м", size=14, color="#9ca3af", anchor="end", bold=True))

    p.append(text(p2_x + 30, py + 150, "ШВИДКІСТЬ:", size=11, color="#9ca3af", anchor="start"))
    p.append(text(p2_x + pw - 30, py + 150, "22.1 м/с", size=14, color="#9ca3af", anchor="end", bold=True))

    p.append(text(p2_x + 30, py + 180, "БАТАРЕЯ:", size=11, color="#9ca3af", anchor="start"))
    p.append(text(p2_x + pw - 30, py + 180, "86 %", size=14, color="#9ca3af", anchor="end", bold=True))

    # Опис правил
    p.append(rect(p2_x + 15, py + 235, pw - 30, 95, fill="#ffffff", stroke="#fde68a", sw=1, rx=5))
    p.append(text(p2_x + pw / 2, py + 255, "Правила відображення:", size=10.5, color="#d97706", bold=True))
    p.append(text(p2_x + pw / 2, py + 275, "• Збліднення (Ghosting 50% opacity)", size=9.5, color=INK))
    p.append(text(p2_x + pw / 2, py + 295, "• Жовта рамка навколо блоку", size=9.5, color=INK))
    p.append(text(p2_x + pw / 2, py + 315, "• Рухомий таймер віку «+1.4s»", size=9.5, color=INK))


    # ── Панель 3: Недійсні дані (> 2000 мс) ──
    p3_x = xs[2]
    p.append(rect(p3_x, py, pw, ph, fill="#fdf6f5", stroke=POS, sw=1.8, rx=8))
    p.append(text(p3_x + pw / 2, py + 26, "3. Недійсність (> 2000 мс)", size=12.5, color=POS, bold=True))
    p.append(text(p3_x + pw / 2, py + 45, "Обрив лінка або відмова датчика", size=10, color=MUTED))

    # Візуальний віджет
    p.append(rect(p3_x + 15, py + 60, pw - 30, 160, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=6))
    p.append(rect(p3_x + 25, py + 72, 105, 22, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(p3_x + 77, py + 87, "✖ НЕМА ДАНИХ", size=9.5, color=POS, bold=True))
    p.append(text(p3_x + pw - 35, py + 87, "> 2.0с", size=10, color=POS, anchor="end", bold=True))

    # Перекреслені або замінені значення
    p.append(text(p3_x + 30, py + 120, "ВИСОТА:", size=11, color="#b91c1c", anchor="start"))
    p.append(text(p3_x + pw - 30, py + 120, "- - -  м", size=14, color="#b91c1c", anchor="end", bold=True))

    p.append(text(p3_x + 30, py + 150, "ШВИДКІСТЬ:", size=11, color="#b91c1c", anchor="start"))
    p.append(text(p3_x + pw - 30, py + 150, "- - -  м/с", size=14, color="#b91c1c", anchor="end", bold=True))

    p.append(text(p3_x + 30, py + 180, "БАТАРЕЯ:", size=11, color="#b91c1c", anchor="start"))
    p.append(text(p3_x + pw - 30, py + 180, "? ? ?", size=14, color="#b91c1c", anchor="end", bold=True))

    # Червоний хрест перекреслення віджета
    p.append(line(p3_x + 20, py + 65, p3_x + pw - 20, py + 215, color=POS, sw=2, dash="5,5"))
    p.append(line(p3_x + pw - 20, py + 65, p3_x + 20, py + 215, color=POS, sw=2, dash="5,5"))

    # Опис правил
    p.append(rect(p3_x + 15, py + 235, pw - 30, 95, fill="#ffffff", stroke="#fecaca", sw=1, rx=5))
    p.append(text(p3_x + pw / 2, py + 255, "Правила відображення:", size=10.5, color=POS, bold=True))
    p.append(text(p3_x + pw / 2, py + 275, "• Червоне перекреслення приладу", size=9.5, color=INK))
    p.append(text(p3_x + pw / 2, py + 295, "• Заміна значень на «- - -» або «???»", size=9.5, color=INK))
    p.append(text(p3_x + pw / 2, py + 315, "• Приховування стрілок курсу (Fail-Silent)", size=9.5, color=INK))

    render(os.path.join(OUT, "visual-degradation-stages.svg"), W, H, *p,
           title="Три стадії візуального старіння телеметрії")


# ── 2. stale-data-hazard-timeline: порівняння реакції оператора ───────────────
def fig_stale_data_hazard_timeline():
    W, H = 880, 440
    p = []

    p.append(text(W / 2, 26, "Небезпека застиглих даних: порівняння поведінки оператора та наслідків", size=15, bold=True))

    # Панель А: Без детекції старіння
    by1 = 55
    bw = 820
    bh = 165
    bx = 30
    p.append(rect(bx, by1, bw, bh, fill="#fdf6f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(bx + 20, by1 + 24, "Сценарій А: Звичайний GUI без перевірки віку (Latch / Last Known Value)", size=12.5, color=POS, anchor="start", bold=True))

    # Часова вісь А
    ty1 = by1 + 75
    p.append(line(bx + 40, ty1, bx + bw - 40, ty1, color="#94a3b8", sw=2))

    points_a = [
        (bx + 60, "t = 0.0с", "Зв'язок ОК (120 м)", FIELD),
        (bx + 230, "t = 2.0с", "ОБРИВ ЛІНКА", POS),
        (bx + 450, "t = 6.0с", "Пікірування (факт 40 м)", POS),
        (bx + 730, "t = 10.0с", "КАТАСТРОФА (0 м)", POS),
    ]

    for px, label_t, desc, col in points_a:
        p.append(circle(px, ty1, 6, fill="#ffffff", stroke=col, sw=2.5))
        p.append(text(px, ty1 - 14, label_t, size=10.5, color=INK, bold=True))
        p.append(text(px, ty1 + 22, desc, size=9.5, color=col, bold=True))

    # Що показує екран А
    p.append(rect(bx + 40, by1 + 115, bw - 80, 36, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=5))
    p.append(text(bx + 55, by1 + 138, "Екран оператора:", size=10.5, color=MUTED, anchor="start", bold=True))
    p.append(text(bx + 190, by1 + 138, "«Висота 120.4 м, Батарея 86%» (ЗАСТИГЛО)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(bx + bw - 55, by1 + 138, "Оператор спокійний, бездіяльний → аварія", size=10.5, color=POS, anchor="end", bold=True))


    # Панель Б: Із системою Stale Data Indication
    by2 = 235
    p.append(rect(bx, by2, bw, bh, fill="#f6fbf7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(bx + 20, by2 + 24, "Сценарій Б: Інтерфейс із градацією старіння (Stale Data Indication + Fail-Silent)", size=12.5, color=FIELD, anchor="start", bold=True))

    # Часова вісь Б
    ty2 = by2 + 75
    p.append(line(bx + 40, ty2, bx + bw - 40, ty2, color="#94a3b8", sw=2))

    points_b = [
        (bx + 60, "t = 0.0с", "Зв'язок ОК (120 м)", FIELD),
        (bx + 230, "t = 0.5с", "Збліднення + «+0.5s»", "#d97706"),
        (bx + 450, "t = 2.0с", "Червоний хрест + зумер", POS),
        (bx + 730, "t = 3.5с", "Резервний лінк / RTL", FIELD),
    ]

    for px, label_t, desc, col in points_b:
        p.append(circle(px, ty2, 6, fill="#ffffff", stroke=col, sw=2.5))
        p.append(text(px, ty2 - 14, label_t, size=10.5, color=INK, bold=True))
        p.append(text(px, ty2 + 22, desc, size=9.5, color=col, bold=True))

    # Що показує екран Б
    p.append(rect(bx + 40, by2 + 115, bw - 80, 36, fill="#ffffff", stroke="#a3d9b1", sw=1.2, rx=5))
    p.append(text(bx + 55, by2 + 138, "Екран оператора:", size=10.5, color=MUTED, anchor="start", bold=True))
    p.append(text(bx + 190, by2 + 138, "Збліднення на 0.5с → Хрест і «- - -» на 2.0с", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(bx + bw - 55, by2 + 138, "Оператор миттєво бачить втрату → апарат врятовано", size=10.5, color=FIELD, anchor="end", bold=True))

    render(os.path.join(OUT, "stale-data-hazard-timeline.svg"), W, H, *p,
           title="Хронологія небезпеки застиглих даних")


# ── 3. per-field-vs-global-heartbeat: пастка глобального серцебиття ───────────
def fig_per_field_vs_global_heartbeat():
    W, H = 880, 430
    p = []

    p.append(text(W / 2, 26, "Пастка єдиного серцебиття: чому MAVLink Heartbeat не гарантує свіжість датчиків", size=15, bold=True))

    # Лівий блок: Польотний контролер
    bx1 = 30
    by = 60
    bw1 = 250
    bh1 = 335
    p.append(rect(bx1, by, bw1, bh1, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(bx1 + bw1 / 2, by + 26, "Польотний контролер (FC)", size=12.5, color=NEG, bold=True))

    # Підсистеми всередині FC
    sensors = [
        ("IMU (Гіроскоп/Аксель)", "I2C шина: OK (500 Гц)", "#27ae60", "#eaf7ed"),
        ("GPS-модуль (UART)", "UART завис: старі координати!", "#c0392b", "#fdecea"),
        ("Барометр / Висотомір", "SPI шина: OK (50 Гц)", "#27ae60", "#eaf7ed"),
        ("Серцебиття (Heartbeat)", "Цикл FreeRTOS: OK (1 Гц)", "#27ae60", "#eaf7ed"),
    ]

    for i, (s_name, s_status, s_col, s_fill) in enumerate(sensors):
        sy = by + 50 + i * 66
        p.append(rect(bx1 + 15, sy, bw1 - 30, 56, fill=s_fill, stroke=s_col, sw=1.2, rx=5))
        p.append(text(bx1 + 25, sy + 22, s_name, size=11, color=INK, anchor="start", bold=True))
        p.append(text(bx1 + 25, sy + 42, s_status, size=9.5, color=s_col, anchor="start", bold=True))

    # Центральні стрілки транспорту
    cx = 310
    p.append(arrow(bx1 + bw1, by + 78, cx + 180, by + 78, color=FIELD, sw=2))
    p.append(text(cx + 90, by + 68, "ATTITUDE (свіжий)", size=10, color=FIELD, bold=True))

    p.append(arrow(bx1 + bw1, by + 144, cx + 180, by + 144, color=POS, sw=2))
    p.append(text(cx + 90, by + 134, "GLOBAL_POSITION (ЗАСТИГ)", size=10, color=POS, bold=True))

    p.append(arrow(bx1 + bw1, by + 210, cx + 180, by + 210, color=FIELD, sw=2))
    p.append(text(cx + 90, by + 200, "VFR_HUD (свіжий)", size=10, color=FIELD, bold=True))

    p.append(arrow(bx1 + bw1, by + 276, cx + 180, by + 276, color=NEG, sw=2))
    p.append(text(cx + 90, by + 266, "HEARTBEAT (активний 1 Гц)", size=10, color=NEG, bold=True))


    # Правий блок: Наземна станція керування (GCS)
    bx2 = 520
    bw2 = 330
    p.append(rect(bx2, by, bw2, bh1, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    p.append(text(bx2 + bw2 / 2, by + 26, "Наземна станція (GCS)", size=12.5, color=INK, bold=True))

    # Стан 1: Глобальний лінк
    p.append(rect(bx2 + 15, by + 48, bw2 - 30, 48, fill="#eaf7ed", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(bx2 + 25, by + 68, "Глобальний індикатор зв'язку:", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + 25, by + 86, "● ЗВ'ЯЗОК Є (Heartbeat 1 Гц)", size=11, color=FIELD, anchor="start", bold=True))

    # Стан 2: Посекційний трекер
    p.append(rect(bx2 + 15, by + 106, bw2 - 30, 150, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(bx2 + 25, by + 126, "Посекційний трекер віку (Per-Field Tracker):", size=10.5, color=INK, anchor="start", bold=True))

    p.append(text(bx2 + 25, by + 150, "• Горизонт (IMU):", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + bw2 - 25, by + 150, "Вік 20 мс [ СВІЖО ]", size=10, color=FIELD, anchor="end", bold=True))

    p.append(text(bx2 + 25, by + 180, "• GPS координати:", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + bw2 - 25, by + 180, "Вік 14.8 с [ ✖ STALE ]", size=10, color=POS, anchor="end", bold=True))

    p.append(text(bx2 + 25, by + 210, "• Висота (Баро):", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + bw2 - 25, by + 210, "Вік 35 мс [ СВІЖО ]", size=10, color=FIELD, anchor="end", bold=True))

    p.append(text(bx2 + 25, by + 240, "• Оберти ESC:", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + bw2 - 25, by + 240, "Вік 2.1 с [ ⏱ +2.1s ]", size=10, color="#d97706", anchor="end", bold=True))

    # Висновок внизу
    p.append(rect(bx2 + 15, by + 266, bw2 - 30, 60, fill="#eff6ff", stroke=NEG, sw=1.2, rx=5))
    p.append(text(bx2 + bw2 / 2, by + 286, "Висновок архітектури:", size=10.5, color=NEG, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 308, "Кожне поле має власний таймер віку!", size=10.5, color=INK, bold=True))

    render(os.path.join(OUT, "per-field-vs-global-heartbeat.svg"), W, H, *p,
           title="Глобальне серцебиття проти посекційного контролю")


if __name__ == "__main__":
    fig_visual_degradation_stages()
    fig_stale_data_hazard_timeline()
    fig_per_field_vs_global_heartbeat()
    print("All figures generated successfully.")
