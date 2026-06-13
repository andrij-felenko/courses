# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.15 — Відмовостійка прошивка.
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r15-1-1-swallowed-error.svg    — Проковтнута помилка: причина і симптом рознесені
  fig-r15-1-2-error-ladder.svg       — Щаблі гучності: від коду повернення до паніки
  fig-r15-2-1-three-levels.svg       — Три рівні реакції і коли який
  fig-r15-2-2-assert-pitfall.svg     — Пастка assert: побічний ефект зникає в релізі
  fig-r15-3-1-where-to-check.svg     — Де перевіряти варто, а де — параноя
  fig-r15-3-2-validate-packet.svg    — Розбір кадру: кожна перевірка ловить свою біду
  fig-r15-4-1-safe-state-actuators.svg — Безпечний стан: найменш шкідливий вихід актуатора
  fig-r15-4-2-reset-glitch.svg       — Чому безпечний стан виходу забезпечують апаратно
  fig-r15-5-1-reset-vs-repair.svg    — Чистий старт проти латання зіпсованого стану
  fig-r15-5-2-persist-through-reset.svg — Що переживає reset: куди класти доказ збою
  fig-r15-6-1-escalation-ladder.svg  — Драбина ескалації за лічильником збоїв
  fig-r15-6-2-counter-lifecycle.svg  — Життя лічильника: коли ++ і коли обнулити
  fig-r15-7-1-brownout-gray-zone.svg — Сіра зона brown-out: гірше за чисте вимкнення
  fig-r15-7-2-power-or-bug.svg       — Як відрізнити збій живлення від бага прошивки
  fig-r15-8-1-degradation-strategies.svg — Сходи деградації: слабшати, а не вмирати
  fig-r15-8-2-fallback-chain.svg     — Ланцюг fallback із чесним прапорцем деградації
  fig-r15-0-1-fault-tolerance-map.svg — Карта розділу (для вступу)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.0.1 — Карта розділу: сходи реакції на біду (оглядова, для вступу)
# ══════════════════════════════════════════════════════════════════════════════
def fig_fault_tolerance_map():
    W, H = 900, 300
    frags = []

    frags.append(text(W / 2, 28, "Сходи реакції на біду — Розділ 4.15",
                      size=15, bold=True, color=INK))

    steps = [
        ("4.15.1", "ПОМІТИТИ"),
        ("4.15.2", "ОБРАТИ\nРІВЕНЬ"),
        ("4.15.3", "НЕ ПУСТИТИ\nперевіркою"),
        ("4.15.4", "БЕЗПЕЧНИЙ\nСТАН"),
        ("4.15.5", "ЧИСТИЙ\nRESET"),
        ("4.15.6", "НЕ\nЗАЦИКЛИТИСЬ"),
        ("4.15.7", "ВІДРІЗНИТИ\nЖИВЛЕННЯ"),
        ("4.15.8", "ДЕГРАДУВАТИ\nЗ ГІДНІСТЮ"),
    ]

    n = len(steps)
    margin_x = 36
    step_w = (W - 2 * margin_x) / n
    box_w = step_w - 8
    box_h = 80
    base_y = H - 70
    step_rise = 14

    colors = [
        ("#eaf0fd", NEG),   # 1
        ("#eaf0fd", NEG),   # 2
        ("#eaf0fd", NEG),   # 3
        ("#fff3cd", "#c07000"),  # 4
        ("#fff3cd", "#c07000"),  # 5
        ("#fff3cd", "#c07000"),  # 6
        ("#fdecea", POS),   # 7
        ("#e8f5e9", FIELD), # 8
    ]

    for i, (num, label) in enumerate(steps):
        cx = margin_x + step_w * i + step_w / 2
        cy = base_y - i * step_rise
        fill, stroke = colors[i]

        box_str, bw, bh = textbox(cx, cy, label, size=11, pad=8,
                                   fill=fill, stroke=stroke, sw=2,
                                   bold=True, min_w=box_w)
        frags.append(box_str)

        # номер теми під рамкою
        frags.append(text(cx, cy + bh / 2 + 15, num, size=10, color=MUTED))

        # стрілка до наступної
        if i < n - 1:
            cx_next = margin_x + step_w * (i + 1) + step_w / 2
            cy_next = base_y - (i + 1) * step_rise
            frags.append(arrow(cx + bw / 2, cy, cx_next - box_w / 2, cy_next,
                               color=MUTED, sw=1.5))

    # підпис внизу
    frags.append(text(W / 2, H - 18,
                      "Лейтмотив: відмовостійкість — не героїзм, а дисципліна дрібних правильних рішень",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-r15-0-1-fault-tolerance-map.svg"), W, H, *frags)
    print("  fig-r15-0-1-fault-tolerance-map.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.1.1 — Проковтнута помилка: причина і симптом рознесені
# ══════════════════════════════════════════════════════════════════════════════
def fig_swallowed_error():
    W, H = 820, 360
    frags = []

    frags.append(text(W / 2, 28, "Проковтнута помилка: симптом виринає далеко від причини",
                      size=14, bold=True, color=INK))

    # ── Верхня смуга: «Проковтнуто» ──────────────────────────────────────
    lane_y1 = 100
    frags.append(text(30, lane_y1 - 28, "ПРОКОВТНУТО", size=11, bold=True, color=POS, anchor="start"))

    nodes_bad = [
        ("i2c_read()\nпровалився", "#fdecea", POS),
        ("err == ESP_FAIL\n(ігнорується)", "#fdecea", POS),
        ("buf — сміття\n0xFF 0xFF …", "#fdecea", POS),
        ("use(buf)\nобчислює", FILL, MUTED),
        ("−1000°C ?!\n«звідки?»", "#fdecea", POS),
    ]

    step = 150
    start_x = 60
    for i, (label, fill, stroke) in enumerate(nodes_bad):
        cx = start_x + i * step
        tb, bw, bh = textbox(cx, lane_y1, label, size=11, pad=8,
                              fill=fill, stroke=stroke, sw=2)
        frags.append(tb)
        if i < len(nodes_bad) - 1:
            frags.append(arrow(cx + bw / 2, lane_y1,
                               cx + step - bw / 2 + 8, lane_y1, color=MUTED, sw=1.5))

    # Стрілка «за кілометр»
    frags.append(text(start_x + 4 * step, lane_y1 + 52,
                      "↑ симптом тут", size=10, color=POS, bold=True))
    frags.append(text(start_x, lane_y1 + 52,
                      "↑ причина тут", size=10, color=POS))

    # Двостороння пунктирна дуга «за кілометр»
    frags.append(line(start_x, lane_y1 + 35, start_x + 4 * step, lane_y1 + 35,
                      color=POS, sw=1.2, dash="6 4"))
    frags.append(text((start_x + start_x + 4 * step) / 2, lane_y1 + 30,
                      "рознесено в часі/просторі", size=10, color=POS, italic=True))

    # ── Нижня смуга: «Перевірено» ─────────────────────────────────────────
    lane_y2 = 250
    frags.append(text(30, lane_y2 - 28, "ПЕРЕВІРЕНО", size=11, bold=True, color=FIELD, anchor="start"))

    nodes_good = [
        ("i2c_read()\nпровалився", "#fdecea", POS),
        ("if (err != OK)\nспіймав!", "#e8f5e9", FIELD),
        ("log + safe\nТУТ ЖЕ", "#e8f5e9", FIELD),
    ]

    for i, (label, fill, stroke) in enumerate(nodes_good):
        cx = start_x + i * step
        tb, bw, bh = textbox(cx, lane_y2, label, size=11, pad=8,
                              fill=fill, stroke=stroke, sw=2)
        frags.append(tb)
        if i < len(nodes_good) - 1:
            frags.append(arrow(cx + bw / 2, lane_y2,
                               cx + step - bw / 2 + 8, lane_y2, color=MUTED, sw=1.5))

    frags.append(text(start_x + 2 * step, lane_y2 + 52,
                      "↑ причина й реакція — поряд", size=10, color=FIELD, bold=True))

    # Висновок
    tb_out, _, _ = textbox(W / 2, H - 28,
                           "Перевірка прив'язує симптом до причини. Тиша — рознімає їх.",
                           size=12, fill="#e8f5e9", stroke=FIELD, sw=2, pad=8, bold=True)
    frags.append(tb_out)

    render(os.path.join(OUT, "fig-r15-1-1-swallowed-error.svg"), W, H, *frags)
    print("  fig-r15-1-1-swallowed-error.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.1.2 — Щаблі гучності помилки
# ══════════════════════════════════════════════════════════════════════════════
def fig_error_ladder():
    W, H = 560, 420
    frags = []

    frags.append(text(W / 2, 28, "Як помилка може заявити про себе: щаблі гучності",
                      size=14, bold=True, color=INK))

    rungs = [
        ("код повернення / статус", FILL, INK),
        ("виняткове значення (errno-стиль)", FILL, INK),
        ("запис у лог", "#eaf0fd", NEG),
        ("assert  (впасти в debug)", "#fff3cd", "#c07000"),
        ("паніка / reset", "#fdecea", POS),
    ]

    rung_h = 56
    rung_w = 340
    cx = W / 2 - 30
    y0 = 80
    indent = 30  # зсув для ефекту «сходів»

    for i, (label, fill, stroke) in enumerate(rungs):
        y = y0 + i * rung_h
        x_left = cx - rung_w / 2 + i * (indent / len(rungs))
        tb = fitbox(x_left, y, rung_w - i * (indent / len(rungs)) * 1.5,
                    rung_h - 6, label, size=13, fill=fill,
                    stroke=stroke, sw=2, bold=(i >= 3))
        frags.append(tb)

        if i < len(rungs) - 1:
            frags.append(arrow(cx, y + rung_h - 6, cx, y + rung_h + 1,
                               color=MUTED, sw=1.5))

    # Стрілка «гучніше»
    arr_x = cx + rung_w / 2 + 24
    arr_y_top = y0 + 20
    arr_y_bot = y0 + len(rungs) * rung_h - 20
    frags.append(arrow(arr_x, arr_y_bot, arr_x, arr_y_top, color=POS, sw=2))
    frags.append(text(arr_x + 16, (arr_y_top + arr_y_bot) / 2, "гучніше\nглобальніше",
                      size=11, color=POS, anchor="start"))

    # Стрілка «тихіше»
    arr2_x = cx - rung_w / 2 - 20
    frags.append(arrow(arr2_x, arr_y_top, arr2_x, arr_y_bot, color=NEG, sw=2))
    frags.append(text(arr2_x - 18, (arr_y_top + arr_y_bot) / 2, "тихіше\nлокальніше",
                      size=11, color=NEG, anchor="end"))

    frags.append(text(W / 2, H - 20, "Готує §4.15.2: вибір рівня залежить від природи збою",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-r15-1-2-error-ladder.svg"), W, H, *frags)
    print("  fig-r15-1-2-error-ladder.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.2.1 — Три рівні реакції і коли який
# ══════════════════════════════════════════════════════════════════════════════
def fig_three_levels():
    W, H = 820, 380
    frags = []

    frags.append(text(W / 2, 28, "Три рівні реакції: коли який обрати",
                      size=14, bold=True, color=INK))

    # Початкове питання
    q_cx, q_cy = W / 2, 75
    tb_q, qw, qh = textbox(q_cx, q_cy, "Звідки збій?", size=14, pad=14,
                            fill="#f4f6f8", stroke=INK, sw=2.5, bold=True)
    frags.append(tb_q)

    # Три гілки
    branches = [
        ("ЗОВНІШНІЙ СВІТ\n(очікувано)\nдавач мовчить,\nфайл відсутній,\nмережа впала",
         "КОД ПОВЕРНЕННЯ\nhай вирішує\nвикликач",
         NEG, "#eaf0fd", 160, 210),
        ("ВНУТРІШНЯ ЛОГІКА\n(порушено припущення)\nNULL-вказівник,\nіндекс за межами",
         "ASSERT\n→ впасти в debug\nдруку файл/рядок",
         "#c07000", "#fff3cd", W / 2, 210),
        ("СТАН НЕВІДНОВНИЙ\nкритичну структуру\nпошкоджено",
         "ПАНІКА / RESET\nдалі небезпечно",
         POS, "#fdecea", 660, 210),
    ]

    for bx, by, stroke, fill, cx, cy in [(b[5], b[5], b[2], b[3], b[4], b[5]) for b in branches]:
        pass  # dummy

    for i, (cond_label, react_label, stroke, fill, cx, cy) in enumerate(branches):
        # Умова
        tb_c, cw, ch = textbox(cx, cy, cond_label, size=11, pad=9,
                                fill="#f4f6f8", stroke=MUTED, sw=1.5)
        frags.append(tb_c)

        # Реакція
        react_y = cy + ch / 2 + 50
        tb_r, rw, rh = textbox(cx, react_y, react_label, size=12, pad=10,
                                fill=fill, stroke=stroke, sw=2.5, bold=True)
        frags.append(tb_r)

        # Стрілка умова → реакція
        frags.append(arrow(cx, cy + ch / 2, cx, react_y - rh / 2, color=stroke, sw=1.8))

        # Стрілка від питання до умови
        frags.append(arrow(q_cx, q_cy + qh / 2, cx, cy - ch / 2, color=MUTED, sw=1.5))

    # Мітки гілок
    frags.append(text(160, 148, "очікувано", size=10, color=NEG, italic=True))
    frags.append(text(W / 2, 148, "баг", size=10, color="#c07000", italic=True))
    frags.append(text(660, 148, "невідновно", size=10, color=POS, italic=True))

    render(os.path.join(OUT, "fig-r15-2-1-three-levels.svg"), W, H, *frags)
    print("  fig-r15-2-1-three-levels.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.2.2 — Пастка assert: побічний ефект зникає в релізі
# ══════════════════════════════════════════════════════════════════════════════
def fig_assert_pitfall():
    W, H = 680, 360
    frags = []

    frags.append(text(W / 2, 28, "Пастка assert: побічний ефект зникає у релізі (NDEBUG)",
                      size=14, bold=True, color=INK))

    col_w = 270
    gap = 60
    col_left = 110
    col_right = col_left + col_w + gap

    # ── Заголовки стовпців ────────────────────────────────────────────────
    frags.append(text(col_left + col_w / 2, 65, "DEBUG", size=14, bold=True, color=FIELD))
    frags.append(text(col_right + col_w / 2, 65, "RELEASE (NDEBUG)", size=14, bold=True, color=POS))

    # Вертикальний роздільник
    frags.append(line(W / 2, 55, W / 2, H - 50, color=MUTED, sw=1.2, dash="5 4"))

    row_y = [110, 175, 240, 305]
    labels_left = [
        ("assert( init() == OK )", FILL, INK),
        ("init() ВИКЛИКАНО ✓", "#e8f5e9", FIELD),
        ("перевірка є ✓", "#e8f5e9", FIELD),
    ]
    labels_right = [
        ("рядок ВИРІЗАНО\nпрепроцесором ✗", "#fdecea", POS),
        ("init() НЕ ВИКЛИКАНО ✗", "#fdecea", POS),
        ("система стартує\nнеініціалізованою ✗", "#fdecea", POS),
    ]

    for i, ((ll, lf, ls), (rl, rf, rs)) in enumerate(zip(labels_left, labels_right)):
        y = row_y[i]
        frags.append(fitbox(col_left, y - 24, col_w, 44, ll, size=12,
                            fill=lf, stroke=ls, sw=1.8))
        frags.append(fitbox(col_right, y - 24, col_w, 44, rl, size=12,
                            fill=rf, stroke=rs, sw=1.8))
        if i < len(labels_left) - 1:
            frags.append(arrow(col_left + col_w / 2, y + 20,
                               col_left + col_w / 2, row_y[i + 1] - 24, color=FIELD, sw=1.4))
            frags.append(arrow(col_right + col_w / 2, y + 20,
                               col_right + col_w / 2, row_y[i + 1] - 24, color=POS, sw=1.4))

    # Великий хрест над правою колонкою
    rx = col_right + col_w / 2
    frags.append(line(rx - 22, 80, rx + 22, 120, color=POS, sw=3.5))
    frags.append(line(rx + 22, 80, rx - 22, 120, color=POS, sw=3.5))

    tb_rule, _, _ = textbox(W / 2, H - 26,
                            "Правило: в assert — лише чиста перевірка. Жодної роботи!",
                            size=12, fill="#fdecea", stroke=POS, sw=2, pad=8, bold=True)
    frags.append(tb_rule)

    render(os.path.join(OUT, "fig-r15-2-2-assert-pitfall.svg"), W, H, *frags)
    print("  fig-r15-2-2-assert-pitfall.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.3.1 — Де перевіряти варто, а де — параноя
# ══════════════════════════════════════════════════════════════════════════════
def fig_where_to_check():
    W, H = 700, 440
    frags = []

    frags.append(text(W / 2, 28, "Де перевіряти: периметрова оборона, а не рівномірна параноя",
                      size=14, bold=True, color=INK))

    cx, cy = W / 2, 235

    # ── Концентричні зони ─────────────────────────────────────────────────
    # Зовнішня (зовнішні джерела)
    r_outer = 170
    frags.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" '
                 'fill="#fff8dc" stroke="%s" stroke-width="3" stroke-dasharray="8 4"/>'
                 % (cx, cy, r_outer, r_outer - 10, "#c07000"))

    # Проміжна (межі модулів)
    r_mid = 115
    frags.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" '
                 'fill="#e8f5e9" stroke="%s" stroke-width="2.5"/>'
                 % (cx, cy, r_mid, r_mid - 8, FIELD))

    # Внутрішня (ядро / гарячий цикл)
    r_inner = 60
    frags.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" '
                 'fill="#f4f6f8" stroke="%s" stroke-width="1.5"/>'
                 % (cx, cy, r_inner, r_inner - 5, MUTED))

    # Підписи зон
    frags.append(text(cx, cy, "ядро\nгарячий цикл", size=10, color=MUTED))
    frags.append(text(cx, cy - r_inner - 12, "межі між модулями", size=10, color=FIELD, bold=True))
    frags.append(text(cx, cy - r_outer + 18, "зовнішній світ: UART, мережа, давач, NVS, ввід",
                      size=10, color="#c07000", bold=True))

    # ── Щити на периметрах ───────────────────────────────────────────────
    shield_outer_y = cy - r_outer - 32
    tb_sh1, _, _ = textbox(cx, shield_outer_y,
                           "ПЕРЕВІРЯЙ: діапазон, довжина, CRC, NULL",
                           size=11, fill="#fff3cd", stroke="#c07000", sw=2.5, pad=8, bold=True)
    frags.append(tb_sh1)
    frags.append(arrow(cx, shield_outer_y + 18, cx, cy - r_outer + 4,
                       color="#c07000", sw=1.8))

    shield_mid_x = cx + r_mid + 42
    tb_sh2, sw2, sh2 = textbox(shield_mid_x + 20, cy,
                               "передумови\nпублічного API",
                               size=11, fill="#e8f5e9", stroke=FIELD, sw=2, pad=8)
    frags.append(tb_sh2)
    frags.append(arrow(shield_mid_x + 20 - sw2 / 2, cy, cx + r_mid, cy,
                       color=FIELD, sw=1.5))

    # Позначка «не дублюй» у центрі
    frags.append(text(cx, cy + 16, "не дублюй\nне гальмуй", size=10, color=MUTED, italic=True))

    frags.append(text(W / 2, H - 22,
                      "Перевіряй НЕДОВІРЕНЕ джерело й ДОРОГУ помилку. Не дублюй перевірку вище.",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-r15-3-1-where-to-check.svg"), W, H, *frags)
    print("  fig-r15-3-1-where-to-check.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.3.2 — Розбір кадру: кожна перевірка ловить свою біду
# ══════════════════════════════════════════════════════════════════════════════
def fig_validate_packet():
    W, H = 780, 400
    frags = []

    frags.append(text(W / 2, 28, "Розбір UART-кадру: кожна перевірка ловить свою атаку/збій",
                      size=14, bold=True, color=INK))

    # Кадр
    fields = [
        ("magic\n2B", 60, "#fff3cd", "#c07000"),
        ("len\n1B", 44, "#eaf0fd", NEG),
        ("payload\n…", 110, "#e8f5e9", FIELD),
        ("CRC\n2B", 60, "#fdecea", POS),
    ]

    frame_y = 105
    frame_h = 52
    x = 80
    positions = []
    for label, w, fill, stroke in fields:
        frags.append(fitbox(x, frame_y, w, frame_h, label, size=11,
                            fill=fill, stroke=stroke, sw=2))
        positions.append((x + w / 2, x, w))
        x += w + 2

    # Мітка «кадр»
    frame_right = x
    frags.append(line(80, frame_y + frame_h + 8, frame_right, frame_y + frame_h + 8,
                      color=MUTED, sw=1))
    frags.append(text((80 + frame_right) / 2, frame_y + frame_h + 22,
                      "UART-кадр", size=11, color=MUTED))

    # Перевірки
    checks = [
        # (field_idx, label_check, label_catches, arrow_down, fill, stroke)
        (0, "перевір buf != NULL\n+ перевір magic", "крах вказівника\n(NULL-buf)\nчужий/шумовий кадр",
         "#fff3cd", "#c07000"),
        (1, "перевір len ≤ sizeof(buf)", "читання за межами\nмасиву (overflow)",
         "#eaf0fd", NEG),
        (2, "лише тоді читай\npayload", "— корисне навантаження —",
         "#e8f5e9", FIELD),
        (3, "перевір CRC", "биті дані\n(шум, пошкодження)",
         "#fdecea", POS),
    ]

    for idx, check_lbl, catch_lbl, fill, stroke in checks:
        cx_f = positions[idx][0]
        check_y = frame_y - 72
        tb_ch, cw, ch = textbox(cx_f, check_y, check_lbl, size=10, pad=7,
                                 fill=fill, stroke=stroke, sw=1.8)
        frags.append(tb_ch)
        frags.append(arrow(cx_f, check_y + ch / 2, cx_f, frame_y, color=stroke, sw=1.5))

        catch_y = frame_y + frame_h + 80
        tb_ca, caw, cah = textbox(cx_f, catch_y, catch_lbl, size=10, pad=7,
                                   fill=fill, stroke=stroke, sw=1.8)
        frags.append(tb_ca)
        frags.append(arrow(cx_f, frame_y + frame_h, cx_f, catch_y - cah / 2,
                           color=stroke, sw=1.5))

    # Стрілка «читання за межами» — виходить за рамку буфера
    len_cx = positions[1][0]
    frags.append(arrow(len_cx + 30, frame_y + 26, len_cx + 100, frame_y + 26,
                       color=POS, sw=2.5))
    frags.append(text(len_cx + 110, frame_y + 24, "← НЕБЕЗПЕКА", size=10, color=POS, bold=True,
                      anchor="start"))

    frags.append(text(W / 2, H - 22,
                      "Усі перевірки зелені → лише тоді читаємо payload. Кожна ловить свій клас загрози.",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-r15-3-2-validate-packet.svg"), W, H, *frags)
    print("  fig-r15-3-2-validate-packet.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.4.1 — Безпечний стан актуаторів
# ══════════════════════════════════════════════════════════════════════════════
def fig_safe_state_actuators():
    W, H = 720, 360
    frags = []

    frags.append(text(W / 2, 28, "Безпечний стан: найменш шкідливий вихід кожного актуатора",
                      size=14, bold=True, color=INK))

    rows = [
        ("Мотор (DC/BLDC)", "СТОП  (PWM duty = 0)", "Так (пружна гальм.)", FIELD, "#e8f5e9"),
        ("Нагрівач",         "OFF  (реле розімкнуто)",  "Так",                FIELD, "#e8f5e9"),
        ("Клапан (н/з)",     "ЗАКРИТО",                  "Так",                FIELD, "#e8f5e9"),
        ("Клапан (н/в) ⚠",  "ВІДКРИТО  ← залежить!",   "Так (інша пружина)", "#c07000", "#fff3cd"),
        ("Гальмо (пружинне)","ПРИТИСНУТО",                "Так (de-energize)",  FIELD, "#e8f5e9"),
        ("Підсвітка",        "OFF",                       "Так",                FIELD, "#e8f5e9"),
    ]

    # Заголовки
    col_x = [40, 280, 530]
    col_w = [230, 240, 160]
    hdr_y = 65
    for hdr, cx in zip(["Актуатор", "Безпечний стан", "Знеструм. = безпека?"],
                        [c + cw / 2 for c, cw in zip(col_x, col_w)]):
        frags.append(text(cx, hdr_y, hdr, size=12, bold=True, color=INK))
    frags.append(line(40, hdr_y + 12, W - 40, hdr_y + 12, color=MUTED, sw=1))

    row_h = 40
    for i, (act, safe, fs, fs_color, fs_fill) in enumerate(rows):
        y = hdr_y + 24 + i * row_h
        fill = fs_fill if i % 2 == 0 else BG
        frags.append(rect(40, y, W - 80, row_h - 4, fill=fill, stroke=MUTED, sw=0.8, rx=4))
        frags.append(text(col_x[0] + col_w[0] / 2, y + row_h / 2, act, size=11, color=INK))
        frags.append(text(col_x[1] + col_w[1] / 2, y + row_h / 2, safe, size=11,
                          color=fs_color, bold=(fs_color != FIELD)))
        frags.append(text(col_x[2] + col_w[2] / 2, y + row_h / 2, fs, size=11, color=fs_color))

    tb_note, _, _ = textbox(W / 2, H - 26,
                            "Безпечний стан не універсальний — визначає інженер під конкретну систему.",
                            size=12, fill="#fff3cd", stroke="#c07000", sw=2, pad=8, bold=True)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r15-4-1-safe-state-actuators.svg"), W, H, *frags)
    print("  fig-r15-4-1-safe-state-actuators.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.4.2 — Чому безпечний стан виходу забезпечують апаратно
# ══════════════════════════════════════════════════════════════════════════════
def fig_reset_glitch():
    W, H = 760, 340
    frags = []

    frags.append(text(W / 2, 28, "«Вікно небезпеки» reset: GPIO невизначений до ініціалізації",
                      size=14, bold=True, color=INK))

    # Часова шкала
    ax_y = 160
    ax_x0 = 60
    ax_x1 = W - 60
    phases = [
        (ax_x0, 190, "RESET\n(чіп у reset)", "#fdecea", POS),
        (190, 370, "BOOTLOADER\n(не наш код)", "#fff3cd", "#c07000"),
        (370, ax_x1, "НАШ КОД\n(ініціалізація)", "#e8f5e9", FIELD),
    ]

    for x0, x1, lbl, fill, stroke in phases:
        frags.append(rect(x0, ax_y - 40, x1 - x0, 80, fill=fill, stroke=stroke, sw=2))
        frags.append(text((x0 + x1) / 2, ax_y + 8, lbl, size=11, color=stroke, bold=True))

    # Рівень GPIO без підтяжки (хаотичний — Hi-Z)
    import random
    random.seed(42)
    gpio_y = ax_y - 65
    frags.append(text(ax_x0 - 4, gpio_y, "GPIO\n(Hi-Z)", size=10, color=POS, anchor="end"))
    # Зигзаг у небезпечній зоні
    pts_x = list(range(ax_x0, 370, 15))
    pts_y = [gpio_y + random.randint(-12, 12) for _ in pts_x]
    for i in range(len(pts_x) - 1):
        frags.append(line(pts_x[i], pts_y[i], pts_x[i + 1], pts_y[i + 1],
                          color=POS, sw=1.5, dash="3 2"))

    # Стабільна лінія після ініціалізації
    frags.append(line(370, gpio_y, ax_x1, gpio_y, color=FIELD, sw=2.5))
    frags.append(text(ax_x1 + 4, gpio_y, "OK", size=11, color=FIELD, bold=True, anchor="start"))

    # Апаратна підтяжка — рівна зелена лінія ВПРОДОВЖ УСІХ фаз
    hw_y = ax_y + 55
    frags.append(line(ax_x0, hw_y, ax_x1, hw_y, color=FIELD, sw=3))
    frags.append(text(ax_x0 - 4, hw_y, "Апаратна\nпідтяжка\n→ «OFF»", size=10,
                      color=FIELD, bold=True, anchor="end"))
    frags.append(text(W / 2, hw_y + 18, "завжди безпечно, навіть під час reset",
                      size=10, color=FIELD, italic=True))

    # Виноска «вікно небезпеки»
    frags.append(line(ax_x0, ax_y - 100, 370, ax_y - 100, color=POS, sw=1.5, dash="5 3"))
    frags.append(text((ax_x0 + 370) / 2, ax_y - 112, "«вікно небезпеки» — мотор може смикнути!",
                      size=11, color=POS, bold=True))

    frags.append(text(W / 2, H - 18,
                      "Прошивка під час reset мовчить → безпеку дає залізо (§4.4.4)",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fig-r15-4-2-reset-glitch.svg"), W, H, *frags)
    print("  fig-r15-4-2-reset-glitch.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.5.1 — Чистий старт проти латання зіпсованого стану
# ══════════════════════════════════════════════════════════════════════════════
def fig_reset_vs_repair():
    W, H = 780, 380
    frags = []

    frags.append(text(W / 2, 28, "Відомий чистий старт надійніший за невідоме латання",
                      size=14, bold=True, color=INK))

    mid_y = 190

    # ── Лівий шлях: REPAIR ────────────────────────────────────────────────
    lx = 190

    tb_bad0, bw, bh = textbox(lx, 75, "Зіпсований\nстан", size=12, pad=10,
                               fill="#fdecea", stroke=POS, sw=2, bold=True)
    frags.append(tb_bad0)

    # «Клубок» — імітація хаотичного стану
    import math
    knot_cx, knot_cy = lx, 175
    for angle in range(0, 360, 40):
        r1 = 22 + (angle % 60) // 10 * 4
        r2 = 18 + ((angle + 80) % 60) // 10 * 4
        x1 = knot_cx + r1 * math.cos(math.radians(angle))
        y1 = knot_cy + r1 * math.sin(math.radians(angle))
        x2 = knot_cx + r2 * math.cos(math.radians(angle + 80))
        y2 = knot_cy + r2 * math.sin(math.radians(angle + 80))
        frags.append(line(x1, y1, x2, y2, color=POS, sw=1.5))
    frags.append(text(knot_cx, knot_cy, "?", size=20, color=POS, bold=True))
    frags.append(text(knot_cx, knot_cy + 44, "«латаємо»\nна льоту", size=11, color=POS))

    # Гілки розгалуження в хаос
    for dy in [-55, 0, 55]:
        tx = 310
        ty = 270 + dy
        frags.append(arrow(knot_cx + 28, knot_cy, tx, ty, color=POS, sw=1.5))
        frags.append(fitbox(tx, ty - 20, 100, 40, "нові дивні\nбаги", size=10,
                            fill="#fdecea", stroke=POS, sw=1.5))

    frags.append(arrow(lx, 75 + bh / 2, lx, knot_cy - 28, color=POS, sw=1.5))
    frags.append(text(lx, H - 26, "REPAIR: шлях у хаос", size=12, bold=True, color=POS))

    # ── Правий шлях: RESET ───────────────────────────────────────────────
    rx = 590

    tb_bad1, bw1, bh1 = textbox(rx, 75, "Зіпсований\nстан", size=12, pad=10,
                                  fill="#fdecea", stroke=POS, sw=2, bold=True)
    frags.append(tb_bad1)

    frags.append(arrow(rx, 75 + bh1 / 2, rx, 145, color=FIELD, sw=2))

    tb_reset, rw, rh = textbox(rx, 165, "RESET\nesp_restart()", size=12, pad=10,
                                fill="#e8f5e9", stroke=FIELD, sw=2.5, bold=True)
    frags.append(tb_reset)

    frags.append(arrow(rx, 165 + rh / 2, rx, 235, color=FIELD, sw=2))

    tb_clean, cw, ch = textbox(rx, 255, "ПОВНІСТЮ ВІДОМИЙ\nчистий старт\n(RAM = 0, периферія в reset)", size=11, pad=10,
                                fill="#e8f5e9", stroke=FIELD, sw=2.5)
    frags.append(tb_clean)

    frags.append(arrow(rx, 255 + ch / 2, rx, 320, color=FIELD, sw=2))
    tb_pred, _, _ = textbox(rx, 335, "передбачувана\nробота ✓", size=12, pad=8,
                             fill="#e8f5e9", stroke=FIELD, sw=2)
    frags.append(tb_pred)

    frags.append(text(rx, H - 26, "RESET: відомий і безпечний", size=12, bold=True, color=FIELD))

    # Роздільна лінія
    frags.append(line(W / 2, 55, W / 2, H - 40, color=MUTED, sw=1, dash="6 4"))

    render(os.path.join(OUT, "fig-r15-5-1-reset-vs-repair.svg"), W, H, *frags)
    print("  fig-r15-5-1-reset-vs-repair.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.5.2 — Що переживає reset: куди класти доказ збою
# ══════════════════════════════════════════════════════════════════════════════
def fig_persist_through_reset():
    W, H = 740, 380
    frags = []

    frags.append(text(W / 2, 28, "Що переживає reset: куди зберігати доказ збою",
                      size=14, bold=True, color=INK))

    layers = [
        ("SRAM (робочий стан)",
         "СТЕРТО при reset\nуся RAM = 0", POS, "#fdecea", 80),
        ("RTC-пам'ять (лічильник збоїв,\nпричина, прапорець safe mode)",
         "Переживає reset і deep-sleep\nНЕ переживає повне знеструмлення", "#c07000", "#fff3cd", 148),
        ("NVS у Flash\n(конфіг, порогові значення)",
         "Переживає знеструмлення\nЗношується → писати ощадливо", FIELD, "#e8f5e9", 90),
    ]

    layer_w = 480
    y = 75
    cx_layer = W / 2 - 20

    for (name, desc, stroke, fill, h) in layers:
        frags.append(rect(cx_layer - layer_w / 2, y, layer_w, h,
                          fill=fill, stroke=stroke, sw=2.5, rx=6))
        frags.append(text(cx_layer, y + 22, name, size=12, bold=True, color=stroke))
        frags.append(text(cx_layer, y + 22 + 24, desc, size=11, color=INK))
        y += h + 12

    # Стрілки «що писати куди»
    arrow_x = cx_layer + layer_w / 2 + 20
    y0_rtc = 75 + 80 + 12 + 10
    y0_nvs = 75 + 80 + 12 + 148 + 12 + 10
    frags.append(text(arrow_x + 8, y0_rtc, "лічильник,\nпричина reset,\nboot_fail_cnt",
                      size=10, color="#c07000", anchor="start"))
    frags.append(text(arrow_x + 8, y0_nvs, "конфіг, порогові\nзначення (рідко)",
                      size=10, color=FIELD, anchor="start"))

    # Порядок reset
    ord_x = 75
    ord_y = 310
    steps_reset = ["enter_safe_state()", "log_fault(reason)", "nvs_commit()", "esp_restart()"]
    frags.append(text(ord_x, ord_y - 18, "Правильний порядок перед reset:", size=11, bold=True,
                      color=INK, anchor="start"))
    for i, s in enumerate(steps_reset):
        frags.append(textbox.__doc__ and None or None)  # dummy
        tb, tw, th = textbox(ord_x + i * 145 + 65, ord_y + 16, s, size=10, pad=6,
                              fill=FILL, stroke=INK, sw=1.5)
        frags.append(tb)
        if i < len(steps_reset) - 1:
            frags.append(arrow(ord_x + i * 145 + 65 + tw / 2, ord_y + 16,
                               ord_x + (i + 1) * 145 + 65 - tw / 2 + 5, ord_y + 16,
                               color=MUTED, sw=1.3))

    render(os.path.join(OUT, "fig-r15-5-2-persist-through-reset.svg"), W, H, *frags)
    print("  fig-r15-5-2-persist-through-reset.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.6.1 — Драбина ескалації за лічильником збоїв
# ══════════════════════════════════════════════════════════════════════════════
def fig_escalation_ladder():
    W, H = 760, 440
    frags = []

    frags.append(text(W / 2, 28, "Драбина ескалації: що пробувати далі, коли просте не допомогло",
                      size=14, bold=True, color=INK))

    rungs = [
        ("1–2 збої", "RESTART\n(просто перезавантажся)", FILL, INK),
        ("поріг досягнуто\n(напр. 5/хв)", "SAFE MODE\n(урізана функціональність)", "#fff3cd", "#c07000"),
        ("safe mode не помогло", "ВІДКОТИТИ КОНФІГ\nдо дефолту / попереднього", "#eaf0fd", NEG),
        ("конфіг не допоміг", "ВІДКОТИТИ ПРОШИВКУ\nна попередній OTA-слот", "#fdecea", POS),
        ("крайнє", "ЗАСТРЯГТИ в SAFE MODE\n+ зателефонувати на допомогу\n(індикатор + зв'язок)", "#fdecea", POS),
    ]

    rung_h = 60
    rung_w = 380
    cx = W / 2
    y = 70

    for i, (condition, action, fill, stroke) in enumerate(rungs):
        # Умова ліворуч
        cond_x = cx - rung_w / 2 - 120
        tb_c, cw, ch = textbox(cond_x, y + rung_h / 2, condition, size=10, pad=7,
                                fill=FILL, stroke=MUTED, sw=1.2)
        frags.append(tb_c)
        frags.append(arrow(cond_x + cw / 2, y + rung_h / 2, cx - rung_w / 2, y + rung_h / 2,
                           color=MUTED, sw=1.2))

        # Сходинка (рамка дії)
        frags.append(rect(cx - rung_w / 2, y, rung_w, rung_h - 4,
                          fill=fill, stroke=stroke, sw=2, rx=6))
        frags.append(text(cx, y + rung_h / 2, action, size=12, color=stroke, bold=True))

        # Стрілка між сходинками
        if i < len(rungs) - 1:
            frags.append(arrow(cx, y + rung_h - 4, cx, y + rung_h + 4, color=MUTED, sw=1.5))

        y += rung_h + 10

    # Лічильник збоку
    cnt_x = cx + rung_w / 2 + 30
    frags.append(line(cnt_x, 70, cnt_x, y - 10, color=POS, sw=2.5))
    frags.append(text(cnt_x + 8, (70 + y - 10) / 2, "boot_fail_cnt\nзростає →",
                      size=11, color=POS, anchor="start"))

    render(os.path.join(OUT, "fig-r15-6-1-escalation-ladder.svg"), W, H, *frags)
    print("  fig-r15-6-1-escalation-ladder.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.6.2 — Життя лічильника: коли ++ і коли обнулити
# ══════════════════════════════════════════════════════════════════════════════
def fig_counter_lifecycle():
    W, H = 760, 380
    frags = []

    frags.append(text(W / 2, 28, "Лічильник збоїв: коли +1 і коли обнулити",
                      size=14, bold=True, color=INK))

    # Осі
    ax_x0 = 60
    ax_x1 = W - 60
    ax_y = 220
    cnt_y0 = 80   # y при cnt=0
    cnt_max = 5
    cnt_y_scale = (ax_y - cnt_y0) / cnt_max  # px per count unit

    # Лінія часу
    frags.append(line(ax_x0, ax_y + 20, ax_x1, ax_y + 20, color=MUTED, sw=1))
    frags.append(text(ax_x0 - 4, ax_y + 20, "час →", size=10, color=MUTED, anchor="end"))

    # Вісь лічильника
    frags.append(line(ax_x0, cnt_y0 - 20, ax_x0, ax_y + 10, color=MUTED, sw=1))
    for v in range(cnt_max + 1):
        yv = ax_y - v * cnt_y_scale
        frags.append(line(ax_x0 - 4, yv, ax_x0, yv, color=MUTED, sw=1))
        frags.append(text(ax_x0 - 8, yv + 4, str(v), size=10, color=MUTED, anchor="end"))

    # Поріг
    threshold = 4
    thresh_y = ax_y - threshold * cnt_y_scale
    frags.append(line(ax_x0, thresh_y, ax_x1, thresh_y, color=POS, sw=1.5, dash="6 4"))
    frags.append(text(ax_x1 + 4, thresh_y, "ПОРІГ", size=10, color=POS, bold=True, anchor="start"))

    # Серія швидких рестартів (cnt ++)
    reboot_times = [80, 130, 190, 270]
    cnt_values = [0, 1, 2, 3, 4]
    px = ax_x0

    for i, (t, cnt) in enumerate(zip(reboot_times, cnt_values)):
        nx = ax_x0 + t
        ny = ax_y - cnt * cnt_y_scale
        if i == 0:
            frags.append(line(px, ax_y, nx, ax_y, color=INK, sw=2))
        else:
            prev_cnt = cnt_values[i - 1]
            prev_x = ax_x0 + reboot_times[i - 1]
            prev_y = ax_y - prev_cnt * cnt_y_scale
            # горизонтальна ділянка
            frags.append(line(prev_x, prev_y, nx, prev_y, color=INK, sw=2))
        # стрибок вгору
        ny_next = ax_y - cnt * cnt_y_scale
        ny_prev = ax_y - (cnt_values[i - 1] if i > 0 else 0) * cnt_y_scale
        frags.append(line(nx, ny_prev if i > 0 else ax_y, nx, ny_next, color=INK, sw=2))
        # мітка «reset»
        frags.append(text(nx, ax_y + 36, "reset" if i < 3 else "порогу\nдосягнуто",
                          size=9, color=POS if i == 3 else MUTED))

    # Зона червона (поріг досягнуто)
    thresh_x = ax_x0 + reboot_times[3]
    frags.append(rect(thresh_x, thresh_y - 10, 180, ax_y - thresh_y + 10,
                      fill="#fdecea", stroke=POS, sw=1, rx=3))
    frags.append(text(thresh_x + 90, thresh_y + (ax_y - thresh_y) / 2,
                      "SAFE MODE!", size=11, bold=True, color=POS))

    # Після стабільної роботи (60 с) — скидання до 0
    stable_x = thresh_x + 200
    frags.append(line(thresh_x + 180, thresh_y, stable_x, thresh_y, color=POS, sw=2))
    frags.append(line(stable_x, thresh_y, stable_x, ax_y, color=FIELD, sw=2))
    frags.append(line(stable_x, ax_y, ax_x1, ax_y, color=FIELD, sw=2))
    frags.append(text(stable_x + (ax_x1 - stable_x) / 2, ax_y + 36,
                      "> 60 с стабільно → скинуто в 0", size=10, color=FIELD, bold=True))

    # Power-on позначка (не рахується)
    pon_x = ax_x0 + 360
    frags.append(line(pon_x, ax_y + 6, pon_x, ax_y - 10, color=MUTED, sw=1.5))
    frags.append(text(pon_x, ax_y + 52, "power-on\n(не рахується)", size=9, color=MUTED))

    render(os.path.join(OUT, "fig-r15-6-2-counter-lifecycle.svg"), W, H, *frags)
    print("  fig-r15-6-2-counter-lifecycle.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.7.1 — Сіра зона brown-out
# ══════════════════════════════════════════════════════════════════════════════
def fig_brownout_gray_zone():
    W, H = 780, 400
    frags = []

    frags.append(text(W / 2, 28, "Сіра зона brown-out: «недокормлено» гірше за «вимкнено»",
                      size=14, bold=True, color=INK))

    ax_x0, ax_x1 = 70, W - 50
    ax_y_bot = 280   # 0 В
    ax_y_top = 90    # норма

    h_norm = ax_y_bot - ax_y_top            # повна висота
    h_safe = h_norm * 0.35                  # сіра зона: 0..35%
    h_green = h_norm * 0.65                 # зелена зона

    y_norm = ax_y_top                       # верх нормальної зони
    y_gray_top = ax_y_top + h_green         # верх сірої зони = низ зеленої
    y_black = ax_y_bot

    # ── Смуги ─────────────────────────────────────────────────────────────
    bw = ax_x1 - ax_x0
    frags.append(rect(ax_x0, y_norm, bw, h_green, fill="#e8f5e9", stroke=FIELD, sw=0, rx=0))
    frags.append(rect(ax_x0, y_gray_top, bw, h_safe, fill="#f5f5dc", stroke="#c07000", sw=0, rx=0))
    frags.append(rect(ax_x0, y_black, bw, 30, fill="#d0d0d0", stroke=MUTED, sw=0, rx=0))

    # Мітки смуг
    frags.append(text(ax_x1 + 6, y_norm + h_green / 2, "НОРМА\n(чиста робота)",
                      size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(text(ax_x1 + 6, y_gray_top + h_safe / 2, "СІРА ЗОНА\n(недетермінований\nзбій)",
                      size=11, color="#c07000", bold=True, anchor="start"))
    frags.append(text(ax_x1 + 6, y_black + 16, "≈ 0 В\n(чисто вимкнено)",
                      size=10, color=MUTED, anchor="start"))

    # Поріг BOD пунктиром
    bod_y = y_gray_top
    frags.append(line(ax_x0, bod_y, ax_x1, bod_y, color=POS, sw=2, dash="8 4"))
    frags.append(text(ax_x0 - 6, bod_y, "BOD", size=11, color=POS, bold=True, anchor="end"))

    # Крива напруги: норма → просідання від Wi-Fi TX → підйом
    import math

    def vx(i, n):
        return ax_x0 + bw * i / n

    n = 120
    pts = []
    for i in range(n + 1):
        t = i / n
        # норма, потім просідання в сіру зону, потім відновлення
        if t < 0.3:
            v = 0.85
        elif t < 0.5:
            v = 0.85 - 0.38 * math.sin((t - 0.3) / 0.2 * math.pi)
        else:
            v = 0.85 - 0.03 * math.exp(-(t - 0.5) * 10)
        py = ax_y_top + (1 - v) * h_norm
        pts.append((vx(i, n), py))

    for i in range(len(pts) - 1):
        c = POS if (pts[i][1] > bod_y or pts[i + 1][1] > bod_y) else NEG
        frags.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=c, sw=2.5))

    # Сплеск Wi-Fi TX (струм)
    spike_x_start = vx(36, n)
    spike_x_end = vx(60, n)
    spike_y_top = ax_y_bot + 50
    spike_y_bot = ax_y_bot + 80
    frags.append(rect(spike_x_start, spike_y_top, spike_x_end - spike_x_start, 30,
                      fill="#fdecea", stroke=POS, sw=2, rx=4))
    frags.append(text((spike_x_start + spike_x_end) / 2, spike_y_top + 18,
                      "сплеск Wi-Fi TX (300+ мА)", size=11, color=POS, bold=True))

    # Стрілка сплеск → просідання
    frags.append(arrow((spike_x_start + spike_x_end) / 2, spike_y_top,
                       (spike_x_start + spike_x_end) / 2, pts[48][1] + 4,
                       color=POS, sw=1.5))

    # Піктограми хаосу в сірій зоні
    chaos_labels = ["биті\nчитання", "зриви\nFlash", "стрибки\nPC"]
    for i, lbl in enumerate(chaos_labels):
        cx_ch = ax_x0 + bw * (0.35 + i * 0.1)
        cy_ch = y_gray_top + h_safe / 2
        frags.append(text(cx_ch, cy_ch, lbl, size=10, color="#c07000"))

    render(os.path.join(OUT, "fig-r15-7-1-brownout-gray-zone.svg"), W, H, *frags)
    print("  fig-r15-7-1-brownout-gray-zone.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.7.2 — Як відрізнити збій живлення від бага прошивки
# ══════════════════════════════════════════════════════════════════════════════
def fig_power_or_bug():
    W, H = 740, 380
    frags = []

    frags.append(text(W / 2, 28, "Діагностика: збій живлення чи баг прошивки?",
                      size=14, bold=True, color=INK))

    rows = [
        ("Причина reset = BROWNOUT\n(`esp_reset_reason()`)", "ЖИВЛЕННЯ", FIELD, "#e8f5e9"),
        ("Корелює зі сплеском\nнавантаження (Wi-Fi TX, мотор)", "ЖИВЛЕННЯ", FIELD, "#e8f5e9"),
        ("Зникає від кращого БЖ /\nконденсатора / кабелю", "ЖИВЛЕННЯ", FIELD, "#e8f5e9"),
        ("Відтворюється на стенді\nпри стабільному живленні", "КОД", POS, "#fdecea"),
        ("Завжди в одному місці коду\n(backtrace збігається)", "КОД", POS, "#fdecea"),
    ]

    col_x = [40, 490]
    col_w = [440, 180]
    hdr_y = 65
    frags.append(text(col_x[0] + col_w[0] / 2, hdr_y, "Ознака", size=12, bold=True, color=INK))
    frags.append(text(col_x[1] + col_w[1] / 2, hdr_y, "Вирок", size=12, bold=True, color=INK))
    frags.append(line(40, hdr_y + 14, W - 40, hdr_y + 14, color=MUTED, sw=1))

    row_h = 52
    for i, (sign, verdict, stroke, fill) in enumerate(rows):
        y = hdr_y + 22 + i * row_h
        frags.append(fitbox(col_x[0], y, col_w[0], row_h - 4, sign, size=11,
                            fill=FILL if i % 2 == 0 else BG, stroke=MUTED, sw=0.8))
        frags.append(fitbox(col_x[1], y, col_w[1], row_h - 4, verdict, size=13,
                            fill=fill, stroke=stroke, sw=2, bold=True))

    tb_out, _, _ = textbox(W / 2, H - 28,
                           "Причина reset + кореляція з навантаженням → живлення. Не шукай баг там, де його немає.",
                           size=11, fill="#e8f5e9", stroke=FIELD, sw=2, pad=8, bold=True)
    frags.append(tb_out)

    render(os.path.join(OUT, "fig-r15-7-2-power-or-bug.svg"), W, H, *frags)
    print("  fig-r15-7-2-power-or-bug.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.8.1 — Сходи деградації: слабшати, а не вмирати
# ══════════════════════════════════════════════════════════════════════════════
def fig_degradation_strategies():
    W, H = 820, 400
    frags = []

    frags.append(text(W / 2, 28, "Сходи деградації: слабшати, а не вмирати",
                      size=14, bold=True, color=INK))

    steps = [
        ("Повна\nфункція ✓", "#e8f5e9", FIELD),
        ("Запасне\nджерело\n(2-й давач)", "#e8f5e9", FIELD),
        ("last-known-\ngood\n(NVS)", "#eaf0fd", NEG),
        ("Розумний\nдефолт", "#fff3cd", "#c07000"),
        ("Вимкнути\nлише уражене", "#fff3cd", "#c07000"),
        ("Знизити\nякість/частоту", "#fdecea", POS),
        ("Безпечний\nстан/зупинка", "#fdecea", POS),
    ]

    n = len(steps)
    step_w = (W - 120) / n
    box_w = step_w - 10
    box_h = 80
    base_y = 280
    rise = 20

    for i, (label, fill, stroke) in enumerate(steps):
        cx = 60 + step_w * i + step_w / 2
        cy = base_y - i * rise
        tb, bw, bh = textbox(cx, cy, label, size=11, pad=8,
                              fill=fill, stroke=stroke, sw=2, min_w=box_w)
        frags.append(tb)
        if i < n - 1:
            cx_next = 60 + step_w * (i + 1) + step_w / 2
            cy_next = base_y - (i + 1) * rise
            frags.append(arrow(cx + bw / 2, cy, cx_next - bw / 2, cy_next,
                               color=MUTED, sw=1.4))

    # Межа «деградація / зупинка»
    border_x = 60 + step_w * (n - 1) + step_w / 2 - box_w / 2 - 6
    frags.append(line(border_x, 100, border_x, 320, color=POS, sw=2, dash="6 4"))
    frags.append(text(border_x - 8, 95, "межа\nдеградації", size=10, color=POS, anchor="end"))

    # Крихкий дизайн — одна стрілка зразу в крах
    frags.append(text(W / 2, 345, "vs  КРИХКИЙ ДИЗАЙН: будь-яка відмова →", size=11, color=POS, bold=True))
    frags.append(arrow(W / 2 + 200, 345, W - 80, 345, color=POS, sw=2))
    tb_crash, _, _ = textbox(W - 52, 345, "КРАХ", size=13, fill="#fdecea", stroke=POS, sw=2.5, bold=True)
    frags.append(tb_crash)

    render(os.path.join(OUT, "fig-r15-8-1-degradation-strategies.svg"), W, H, *frags)
    print("  fig-r15-8-1-degradation-strategies.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.15.8.2 — Ланцюг fallback із чесним прапорцем деградації
# ══════════════════════════════════════════════════════════════════════════════
def fig_fallback_chain():
    W, H = 780, 480
    frags = []

    frags.append(text(W / 2, 28, "Ланцюг fallback: де ставиться прапорець деградації",
                      size=14, bold=True, color=INK))

    cx = W / 2
    nodes = [
        # (y, label, fill, stroke)
        (75,  "Спробувати основний давач", "#e8f5e9", FIELD),
        (165, "Основний OK?", FILL, INK),
        (255, "Спробувати запасний давач", "#eaf0fd", NEG),
        (345, "Запасний OK?", FILL, INK),
        (420, "last-known-good\nз NVS  +  degraded = 1\n+ консервативний режим", "#fdecea", POS),
    ]

    # «Так» гілки праворуч
    yes_x = cx + 250
    for (y, label, fill, stroke) in nodes:
        tb, bw, bh = textbox(cx, y, label, size=12, pad=10,
                              fill=fill, stroke=stroke, sw=2)
        frags.append(tb)
        if label.endswith("?"):
            # Так → праворуч
            frags.append(arrow(cx + bw / 2, y, yes_x, y, color=FIELD, sw=1.8))

    # «Так» результати
    yes_labels = [
        (165, "Повернути значення\ndegraded = 0", "#e8f5e9", FIELD),
        (345, "Повернути значення\ndegraded = 1\n+ індикатор+лог", "#eaf0fd", NEG),
    ]
    for (y, lbl, fill, stroke) in yes_labels:
        tb, _, _ = textbox(yes_x + 90, y, lbl, size=11, pad=8, fill=fill, stroke=stroke, sw=2)
        frags.append(tb)
        frags.append(text(yes_x + 14, y - 10, "ТАК", size=10, color=FIELD, bold=True))

    # «Ні» гілки вниз
    no_labels_y = [165, 345]
    no_y_targets = [255, 420]
    for src_y, tgt_y in zip(no_labels_y, no_y_targets):
        frags.append(arrow(cx, src_y + 30, cx, tgt_y - 24, color=POS, sw=1.8))
        frags.append(text(cx + 14, (src_y + tgt_y) / 2, "НІ", size=10, color=POS, bold=True, anchor="start"))

    # Стрілка від основного давача до питання OK
    frags.append(arrow(cx, 75 + 28, cx, 165 - 24, color=FIELD, sw=1.5))

    # Мовчазний дефолт — ЗАБОРОНЕНА гілка (перекреслена)
    silent_x = yes_x + 90
    silent_y = 420
    tb_s, sw_s, sh_s = textbox(silent_x, silent_y, "Повернути дефолт\nМОВЧКИ", size=11, pad=8,
                                fill="#fdecea", stroke=POS, sw=2)
    frags.append(tb_s)
    # Хрест
    x0s = silent_x - sw_s / 2 - 4
    x1s = silent_x + sw_s / 2 + 4
    y0s = silent_y - sh_s / 2 - 4
    y1s = silent_y + sh_s / 2 + 4
    frags.append(line(x0s, y0s, x1s, y1s, color=POS, sw=4))
    frags.append(line(x1s, y0s, x0s, y1s, color=POS, sw=4))
    frags.append(text(silent_x, silent_y + sh_s / 2 + 18,
                      "ЗАБОРОНЕНО: тихий збій (§4.15.1)", size=10, color=POS, bold=True))

    # Прапорець degraded → індикатор
    deg_x = cx - 220
    deg_y = 390
    tb_d, _, _ = textbox(deg_x, deg_y, "degraded = 1\n→ індикатор\n→ лог/телеметрія",
                          size=11, pad=8, fill="#fff3cd", stroke="#c07000", sw=2)
    frags.append(tb_d)

    render(os.path.join(OUT, "fig-r15-8-2-fallback-chain.svg"), W, H, *frags)
    print("  fig-r15-8-2-fallback-chain.svg — OK")


if __name__ == "__main__":
    print("Генерація фігур для Розділу 4.15 — Відмовостійка прошивка …")
    fig_fault_tolerance_map()
    fig_swallowed_error()
    fig_error_ladder()
    fig_three_levels()
    fig_assert_pitfall()
    fig_where_to_check()
    fig_validate_packet()
    fig_safe_state_actuators()
    fig_reset_glitch()
    fig_reset_vs_repair()
    fig_persist_through_reset()
    fig_escalation_ladder()
    fig_counter_lifecycle()
    fig_brownout_gray_zone()
    fig_power_or_bug()
    fig_degradation_strategies()
    fig_fallback_chain()
    print("Готово. Усі фігури у ./img/")
