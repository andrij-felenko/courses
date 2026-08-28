# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. anatomy-of-conflict: Конкуренція двох правил за один актуатор ─────────
def fig_anatomy_of_conflict():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Анатомія конфлікту правил: конкуренція за спільний актуатор (Actuator Contention)", size=14, color=INK, bold=True))

    # Лівий блок: Джерело 1 (Контур якості повітря)
    b1_x, b1_y, b1_w, b1_h = 30, 65, 230, 140
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill=BLUEBG, stroke=NEG, sw=1.6, rx=8))
    p.append(text(b1_x + b1_w / 2, b1_y + 24, "Правило 1: Якість повітря", size=11, color=NEG, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 46, "Давач: CO2 = 1450 ppm (> 1000)", size=10, color=INK))
    p.append(rect(b1_x + 15, b1_y + 60, b1_w - 30, 65, fill=BG, stroke=NEG, sw=1, rx=5))
    p.append(text(b1_x + b1_w / 2, b1_y + 80, "ЦІЛЬОВА КОМАНДА:", size=10, color=NEG, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 98, "Відкрити заслінку на 100%", size=10, color=FIELD, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 114, "(Пріоритет: Комфорт / Автоматика)", size=9, color=MUTED))

    # Лівий блок: Джерело 2 (Контур захисту від замерзання)
    b2_x, b2_y, b2_w, b2_h = 30, 235, 230, 140
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(b2_x + b2_w / 2, b2_y + 24, "Правило 2: Захист калорифера", size=11, color=POS, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 46, "Давач: T_води = +3 °C (< +5 °C)", size=10, color=INK))
    p.append(rect(b2_x + 15, b2_y + 60, b2_w - 30, 65, fill=BG, stroke=POS, sw=1, rx=5))
    p.append(text(b2_x + b2_w / 2, b2_y + 80, "ЦІЛЬОВА КОМАНДА:", size=10, color=POS, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 98, "Закрити заслінку на 0%", size=10, color=POS, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 114, "(Пріоритет: Захист обладнання)", size=9, color=MUTED))

    # Центральний блок: Пріоритетний арбітр
    ca_x, ca_y, ca_w, ca_h = 310, 110, 240, 210
    p.append(rect(ca_x, ca_y, ca_w, ca_h, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(ca_x + ca_w / 2, ca_y + 26, "ПРІОРИТЕТНИЙ АРБІТР", size=13, color=AMBERTX, bold=True))
    p.append(text(ca_x + ca_w / 2, ca_y + 46, "Actuator Arbiter / Resolver", size=10, color=MUTED, italic=True))

    p.append(rect(ca_x + 15, ca_y + 60, ca_w - 30, 75, fill=BG, stroke=AMBER, sw=1, rx=6))
    p.append(text(ca_x + ca_w / 2, ca_y + 78, "Оцінка правил та обмежень:", size=10, color=INK, bold=True))
    p.append(text(ca_x + ca_w / 2, ca_y + 96, "Protection (L1) > Comfort (L3)", size=10, color=POS, bold=True))
    p.append(text(ca_x + ca_w / 2, ca_y + 114, "Селектор найгіршого випадку: Min()", size=9, color=MUTED))

    p.append(rect(ca_x + 15, ca_y + 145, ca_w - 30, 50, fill=GREENBG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(ca_x + ca_w / 2, ca_y + 164, "Результуюча уставка:", size=10, color=FIELD, bold=True))
    p.append(text(ca_x + ca_w / 2, ca_y + 182, "ПОЗИЦІЯ ЗАСЛІНКИ = 0% (Закрито)", size=10, color=INK, bold=True))

    # Стрілки від джерел до арбітра
    p.append(arrow(b1_x + b1_w + 4, b1_y + 70, ca_x - 4, ca_y + 70, color=NEG, sw=2))
    p.append(text((b1_x + b1_w + ca_x) / 2, ca_y + 60, "Req: 100%", size=9, color=NEG, bold=True))

    p.append(arrow(b2_x + b2_w + 4, b2_y + 70, ca_x - 4, ca_y + 150, color=POS, sw=2))
    p.append(text((b2_x + b2_w + ca_x) / 2, ca_y + 160, "Req: 0%", size=9, color=POS, bold=True))

    # Правий блок: Фізичний актуатор
    act_x, act_y, act_w, act_h = 600, 110, 230, 210
    p.append(rect(act_x, act_y, act_w, act_h, fill=BG, stroke=LINE, sw=1.8, rx=8))
    p.append(text(act_x + act_w / 2, act_y + 26, "ФІЗИЧНИЙ АКТУАТОР", size=12, color=INK, bold=True))
    p.append(text(act_x + act_w / 2, act_y + 46, "Сервопривід заслінки (0…10 В)", size=10, color=MUTED))

    p.append(rect(act_x + 15, act_y + 62, act_w - 30, 60, fill=REDBG, stroke=POS, sw=1, rx=5))
    p.append(text(act_x + act_w / 2, act_y + 80, "БЕЗ АРБІТРАЖУ:", size=10, color=POS, bold=True))
    p.append(text(act_x + act_w / 2, act_y + 98, "Брязкіт реле / розрив калорифера", size=9, color=INK))
    p.append(text(act_x + act_w / 2, act_y + 112, "Хаотичне смикання приводу", size=9, color=MUTED))

    p.append(rect(act_x + 15, act_y + 132, act_w - 30, 65, fill=GREENBG, stroke=FIELD, sw=1, rx=5))
    p.append(text(act_x + act_w / 2, act_y + 150, "З ПРІОРИТЕТНИМ АРБІТРОМ:", size=10, color=FIELD, bold=True))
    p.append(text(act_x + act_w / 2, act_y + 168, "Захист перемагає комфорт", size=10, color=FIELD, bold=True))
    p.append(text(act_x + act_w / 2, act_y + 184, "Труби цілі, подано аварійне сповіщення", size=9, color=INK))

    p.append(arrow(ca_x + ca_w + 4, ca_y + 105, act_x - 4, act_y + 105, color=FIELD, sw=2.5))
    p.append(text((ca_x + ca_w + act_x) / 2, ca_y + 95, "Out: 0 V", size=10, color=FIELD, bold=True))

    # Нижній висновок
    p.append(rect(30, 395, 800, 30, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 414, "Актуатор не може одночасно виконувати дві протилежні команди. Арбітраж гарантує єдиний детермінований вихід.", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "anatomy-of-conflict.svg"), W, H, *p,
           title="Анатомія конфлікту правил та арбітраж")


# ── 2. hardware-software-interlock: Взаємне блокування H-моста та реверсу ────
def fig_interlocks():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Взаємні блокування (Mutual Exclusion Interlocks): апаратний та програмний захист", size=14, color=INK, bold=True))

    # Лівий блок: Апаратне блокування (Cross-Interlock реле / драйвер)
    bx1, by1, bw1, bh1 = 30, 55, 385, 330
    p.append(rect(bx1, by1, bw1, bh1, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(bx1 + bw1 / 2, by1 + 24, "Апаратне блокування (Hardware Interlock)", size=12, color=NEG, bold=True))
    p.append(text(bx1 + bw1 / 2, by1 + 44, "Фізична неможливість наскрізного замикання (Shoot-Through)", size=10, color=MUTED, italic=True))

    p.append(rect(bx1 + 15, by1 + 58, bw1 - 30, 80, fill=BG, stroke=NEG, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 76, "Електричне перехресне блокування контактів:", size=10, color=NEG, bold=True))
    p.append(text(bx1 + 25, by1 + 96, "• Котушка KM1 (Вперед) живиться через NC контакт KM2", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 25, by1 + 114, "• Котушка KM2 (Назад) живиться через NC контакт KM1", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 25, by1 + 130, "• При спрацьовуванні KM1 ланцюг KM2 фізично розірвано", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(rect(bx1 + 15, by1 + 148, bw1 - 30, 80, fill=BG, stroke=NEG, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 166, "Апаратний Dead-Time у драйверах MOSFET/IGBT:", size=10, color=NEG, bold=True))
    p.append(text(bx1 + 25, by1 + 186, "• Драйвер (IR2104 / UCC27211) має вхід Interlock Logic", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 25, by1 + 204, "• Апаратна затримка t_dead (100…500 нс) між плечима", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 25, by1 + 220, "• Блокує наскрізний струм при розрядці затворів", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(rect(bx1 + 15, by1 + 238, bw1 - 30, 75, fill=GREENBG, stroke=FIELD, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 256, "Головна властивість апаратного захисту:", size=10, color=FIELD, bold=True))
    p.append(text(bx1 + bw1 / 2, by1 + 276, "Працює навіть при повному зависанні процесора,", size=10, color=INK))
    p.append(text(bx1 + bw1 / 2, by1 + 294, "пробитті прошивки чи помилках конфігурації GPIO.", size=10, color=INK, bold=True))

    # Правий блок: Програмне блокування (FSM з Dead-Time)
    bx2, by2, bw2, bh2 = 445, 55, 385, 330
    p.append(rect(bx2, by2, bw2, bh2, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(bx2 + bw2 / 2, by2 + 24, "Програмне блокування (Software Interlock FSM)", size=12, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 44, "Контроль послідовності та часових пауз у мікроконтролері", size=10, color=MUTED, italic=True))

    p.append(rect(bx2 + 15, by2 + 58, bw2 - 30, 80, fill=BG, stroke=AMBER, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 76, "Скінченний автомат реверсу з паузою (Dead-Time):", size=10, color=AMBERTX, bold=True))
    p.append(text(bx2 + 25, by2 + 96, "FORWARD → STOP_WAIT (150 мс) → REVERSE", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(bx2 + 25, by2 + 114, "• Заборона прямого переходу FORWARD ↔ REVERSE", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(bx2 + 25, by2 + 130, "• Гасіння ЕРС самоіндукції та повної зупинки вала", size=9, color=INK, anchor="start"))

    p.append(rect(bx2 + 15, by2 + 148, bw2 - 30, 80, fill=BG, stroke=AMBER, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 166, "Програмні захисні перевірки (Sanity Guards):", size=10, color=AMBERTX, bold=True))
    p.append(text(bx2 + 25, by2 + 186, "• if (cmd_fwd && cmd_rev) { force_safe_stop(); }", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(bx2 + 25, by2 + 204, "• Контроль таймауту оренди (Lease TTL Timeout)", size=9, color=INK, anchor="start"))
    p.append(text(bx2 + 25, by2 + 220, "• Валідація стану давачів кінцевих положень", size=9, color=INK, anchor="start"))

    p.append(rect(bx2 + 15, by2 + 238, bw2 - 30, 75, fill=REDBG, stroke=POS, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 256, "Уразливість суто програмного захисту:", size=10, color=POS, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 276, "Збій вказівника пам'яті, зависання в перериванні або", size=10, color=INK))
    p.append(text(bx2 + bw2 / 2, by2 + 294, "дефект драйвера GPIO вимикає програмні перевірки!", size=10, color=POS, bold=True))

    # Нижній висновок
    p.append(rect(30, 395, 800, 30, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 414, "Правило надійності: програмне блокування організує плавні процеси, апаратне — рятує залізо від фізичного вибуху.", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "hardware-software-interlock.svg"), W, H, *p,
           title="Взаємні блокування: апаратні та програмні")


# ── 3. priority-matrix-hierarchy: Ієрархія авторитетів та селекція станів ────
def fig_priority_hierarchy():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Ієрархічна матриця авторитетів (Priority Layers) та маскування правил", size=14, color=INK, bold=True))

    # Піраміда / Шари пріоритетів
    layers = [
        ("РІВЕНЬ 0: SAFETY / EMERGENCY", "E-Stop, Пожежний шлейф, Струмове відсікання, SIL-контур", "Безумовне скидання в аварійний безпечний стан (Fail-Safe)", REDBG, POS, 50, 65, 460, 62),
        ("РІВЕНЬ 1: EQUIPMENT PROTECTION", "Термозахист двигуна, Давач сухого ходу помпи, Граничний тиск", "Захист заліза від руйнування: блокування небезпечних дій", AMBERBG, AMBER, 50, 137, 460, 62),
        ("РІВЕНЬ 2: OPERATOR MANUAL OVERRIDE", "Фізичні кнопки пульта, Локальний щит, Сервісний режим наладки", "Пряме втручання людини з пріоритетом над автоматикою", BLUEBG, NEG, 50, 209, 460, 62),
        ("РІВЕНЬ 3: AUTOMATION & OPTIMIZATION", "PID-контури клімату, Сценарії за розкладом, Енергозбереження", "Штатні алгоритми; поступаються всім вищим рівням", GREENBG, FIELD, 50, 281, 460, 62),
    ]

    for title_l, sub_l, desc_l, bg_l, stroke_l, lx, ly, lw, lh in layers:
        tag_c = AMBERTX if stroke_l == AMBER else stroke_l
        p.append(rect(lx, ly, lw, lh, fill=bg_l, stroke=stroke_l, sw=1.6, rx=6))
        p.append(text(lx + 15, ly + 20, title_l, size=11, color=tag_c, bold=True, anchor="start"))
        p.append(text(lx + 15, ly + 38, sub_l, size=10, color=INK, anchor="start"))
        p.append(text(lx + 15, ly + 52, desc_l, size=9, color=MUTED, anchor="start"))

    # Стрілка спадання пріоритету
    p.append(arrow(30, 70, 30, 335, color=POS, sw=3))
    p.append(text(25, 205, "ПРІОРИТЕТ", size=9, color=POS, bold=True, anchor="middle"))

    # Права панель: Маскування правил залежно від глобального стану (State Gating)
    mx, my, mw, mh = 530, 65, 300, 278
    p.append(rect(mx, my, mw, mh, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    p.append(text(mx + mw / 2, my + 24, "Матриця маскування правил", size=12, color=INK, bold=True))
    p.append(text(mx + mw / 2, my + 42, "Динамічний дозвіл за станом системи", size=10, color=MUTED, italic=True))

    rows_matrix = [
        ("EMERGENCY", "L0 дозволено", "L1..L3 ЗАМАСКОВАНО", REDBG, POS),
        ("FAULT_TRIP", "L0, L1 дозволено", "L2..L3 ЗАМАСКОВАНО", AMBERBG, AMBER),
        ("MANUAL_SERVICE", "L0..L2 дозволено", "L3 (Авто) ЗАМАСКОВАНО", BLUEBG, NEG),
        ("AUTO_NORMAL", "L0..L3 дозволено", "Всі правила активні", GREENBG, FIELD),
    ]

    for i, (st_name, st_ok, st_mask, bg_m, str_m) in enumerate(rows_matrix):
        ry = my + 55 + i * 52
        tag_m = AMBERTX if str_m == AMBER else str_m
        p.append(rect(mx + 10, ry, mw - 20, 46, fill=bg_m, stroke=str_m, sw=1, rx=5))
        p.append(text(mx + 20, ry + 18, st_name, size=10, color=tag_m, bold=True, anchor="start"))
        p.append(text(mx + 20, ry + 34, f"{st_ok} | {st_mask}", size=9, color=INK, anchor="start"))

    # Нижня панель
    p.append(rect(30, 360, 800, 65, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(W / 2, 380, "Механізм State Gating: коли система переходить у стан аварії або сервісу,", size=10, color=INK, bold=True))
    p.append(text(W / 2, 398, "правила автоматизації блокуються до виконання, а не просто 'програють' на виході арбітра.", size=10, color=MUTED))
    p.append(text(W / 2, 414, "Це усуває накопичення похибок інтеграторів (Anti-Windup) та черги застарілих команд.", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "priority-matrix-hierarchy.svg"), W, H, *p,
           title="Ієрархія пріоритетів та станова селекція")


# ── 4. limiter-vs-blending: Стратегії селекції: Limiter проти Blending ───────
def fig_limiter_vs_blending():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Стратегії злиття для неперервних сигналів: Worst-Case Limiter проти Blending", size=14, color=INK, bold=True))

    # Ліва половина: Worst-Case Limiter (Селектор найжорсткішого обмеження)
    bx1, by1, bw1, bh1 = 30, 55, 385, 330
    p.append(rect(bx1, by1, bw1, bh1, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx1 + bw1 / 2, by1 + 24, "Worst-Case Limiter (High/Low Selector)", size=12, color=FIELD, bold=True))
    p.append(text(bx1 + bw1 / 2, by1 + 44, "Принцип пріоритетного відсікання безпечних меж", size=10, color=MUTED, italic=True))

    p.append(rect(bx1 + 15, by1 + 58, bw1 - 30, 85, fill=BG, stroke=FIELD, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 76, "Auctioneering Control (Вибір максимуму/мінімуму):", size=10, color=FIELD, bold=True))
    p.append(text(bx1 + 20, by1 + 96, "• Охолодження: u_out = max(u_temp, u_humidity, u_co2)", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 20, by1 + 114, "• Нагрів: u_out = min(u_pid_comfort, u_thermal_limit)", size=9, color=INK, anchor="start"))
    p.append(text(bx1 + 20, by1 + 130, "• Жодне оптимізаційне правило не перевищить ліміт безпеки", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(rect(bx1 + 15, by1 + 153, bw1 - 30, 80, fill=BG, stroke=FIELD, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 172, "Діапазонний обмежувач (Safe Clamping):", size=10, color=FIELD, bold=True))
    p.append(text(bx1 + 20, by1 + 192, "u_final = clamp(u_requested, u_safe_min, u_safe_max)", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(bx1 + 20, by1 + 210, "• Гарантує фізично безпечний робочий діапазон", size=9, color=MUTED, anchor="start"))
    p.append(text(bx1 + 20, by1 + 224, "• Не порушує стійкість системи керування", size=9, color=MUTED, anchor="start"))

    p.append(rect(bx1 + 15, by1 + 243, bw1 - 30, 70, fill=FILL, stroke=LINE, sw=1, rx=5))
    p.append(text(bx1 + bw1 / 2, by1 + 262, "ПЕРЕВАГА ДЛЯ БЕЗПЕКИ:", size=10, color=FIELD, bold=True))
    p.append(text(bx1 + bw1 / 2, by1 + 280, "Абсолютна детермінованість і захист обладнання.", size=9, color=INK))
    p.append(text(bx1 + bw1 / 2, by1 + 296, "Критичне правило отримує 100% авторитету.", size=9, color=INK, bold=True))

    # Права половина: Weighted Blending (Зважене усереднення)
    bx2, by2, bw2, bh2 = 445, 55, 385, 330
    p.append(rect(bx2, by2, bw2, bh2, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(bx2 + bw2 / 2, by2 + 24, "Weighted Blending (Зважене усереднення)", size=12, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 44, "Компроміс між некритичними цілями оптимізації", size=10, color=MUTED, italic=True))

    p.append(rect(bx2 + 15, by2 + 58, bw2 - 30, 85, fill=BG, stroke=AMBER, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 76, "Математична модель змішування:", size=10, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 96, "u_out = w1 · u_comfort + w2 · u_energy + w3 · u_noise", size=10, color=INK, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 114, "де w1 + w2 + w3 = 1.0 (динамічні вагові коефіцієнти)", size=9, color=MUTED))
    p.append(text(bx2 + bw2 / 2, by2 + 130, "Працює ТІЛЬКИ в межах безпечної зони!", size=9, color=POS, bold=True))

    p.append(rect(bx2 + 15, by2 + 153, bw2 - 30, 80, fill=REDBG, stroke=POS, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 172, "СМЕРТЕЛЬНА ПОМИЛКА: Усереднення з аварією", size=10, color=POS, bold=True))
    p.append(text(bx2 + 20, by2 + 192, "• Правило 1 (Авто): 100% потужності котла", size=9, color=INK, anchor="start"))
    p.append(text(bx2 + 20, by2 + 208, "• Правило 2 (Аварія): 0% (Перегрів води 105 °C)", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(bx2 + 20, by2 + 224, "• Середнє (0 + 100)/2 = 50% → ВИБУХ КОТЛА!", size=9, color=POS, bold=True, anchor="start"))

    p.append(rect(bx2 + 15, by2 + 243, bw2 - 30, 70, fill=BG, stroke=AMBER, sw=1, rx=5))
    p.append(text(bx2 + bw2 / 2, by2 + 262, "ПРАВИЛО ЗАСТОСУВАННЯ:", size=10, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by2 + 280, "Усереднення дозволене лише між комфортними цілями.", size=9, color=INK))
    p.append(text(bx2 + bw2 / 2, by2 + 296, "Безпека ніколи не бере участі в усередненні!", size=9, color=POS, bold=True))

    # Нижній висновок
    p.append(rect(30, 395, 800, 30, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 414, "Золоте правило арбітражу: Жорсткий вибір для безпеки й захисту, лінійне злиття — лише для комфорту.", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "limiter-vs-blending.svg"), W, H, *p,
           title="Стратегії вибору найжорсткішого обмеження та злиття")


def main():
    fig_anatomy_of_conflict()
    fig_interlocks()
    fig_priority_hierarchy()
    fig_limiter_vs_blending()
    print("Усі 4 фігури для blokuvannia-i-priorytet успішно згенеровано.")

if __name__ == "__main__":
    main()
