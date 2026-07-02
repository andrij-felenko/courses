# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ORANGE = "#d98a00"


# ── module-chain: ланцюг живлення одного модуля ────────────────────────────────
# Ідея: живлення модуля — це не «напруга», а ланцюг від джерела (діапазон!) через
# захист і регулятор до розв'язки на самих виводах. Межа відповідальності —
# роз'єм модуля: усе праворуч тримаєш ти.
def fig_module_chain():
    W, H = 780, 320
    p = []
    y = 120
    h = 66

    # джерело — діапазон, не число
    p.append(fitbox(20, y, 130, h, "Джерело\n3.0–4.2 В\n(плаває!)",
                    size=12, fill="#eef2ff", stroke=NEG, color=NEG, bold=True))
    p.append(arrow(150, y + h / 2, 178, y + h / 2, color=INK, sw=2.0))

    # захист на вводі
    p.append(fitbox(178, y, 128, h, "Захист вводу\nполярність,\nкидок, струм",
                    size=11, fill="#fff5e6", stroke=ORANGE, color=INK, bold=True))
    p.append(arrow(306, y + h / 2, 334, y + h / 2, color=INK, sw=2.0))

    # регулятор
    p.append(fitbox(334, y, 128, h, "Регулятор\nLDO чи\nімпульсний",
                    size=12, fill="#f4fbf6", stroke=FIELD, color=FIELD, bold=True))
    p.append(arrow(462, y + h / 2, 490, y + h / 2, color=INK, sw=2.0))

    # розв'язка на виводах
    p.append(fitbox(490, y, 120, h, "Розв'язка\nбіля виводів",
                    size=12, fill="#f6f6f6", stroke=INK, color=INK, bold=True))
    p.append(arrow(610, y + h / 2, 638, y + h / 2, color=INK, sw=2.0))

    # модуль-споживач
    p.append(fitbox(638, y, 122, h, "Модуль\n3.3 В,\nсмикає струм",
                    size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # підпис під ланцюгом — суть моделі
    p.append(line(20, 208, 610, 208, color=MUTED, sw=1.2, dash="5,4"))
    p.append(text(315, 228, "твій «блок живлення» для одного модуля", size=12, color=INK, italic=True))

    return render(os.path.join(OUT, "module-chain.svg"), W, H, *p)


# ── ldo-vs-switcher: центральний вибір регулятора ──────────────────────────────
# Ідея: LDO пропускає весь струм і зайву напругу палить теплом (тихо, але гаряче
# при великому падінні); імпульсний «переливає» струм, тож бере з входу менше —
# ефективно, але шумно. Показуємо контраст на однаковому виході.
def fig_ldo_vs_switcher():
    W, H = 760, 400
    p = []

    # спільна умова згори
    p.append(text(W / 2, 30, "Вхід 5 В → вихід 3.3 В, навантаження 0.5 А", size=13, bold=True))

    # ── ЛІВОРУЧ: LDO ──
    p.append(rect(30, 55, 340, 315, fill="#f4fbf6", stroke=FIELD, sw=1.6))
    p.append(text(200, 82, "LDO (лінійний)", size=14, color=FIELD, bold=True))
    p.append(fitbox(70, 110, 260, 40, "струм входу = струм виходу = 0.5 А",
                    size=11, fill=BG, stroke=INK, color=INK))
    p.append(fitbox(70, 165, 260, 56,
                    "зайва напруга (5 − 3.3) = 1.7 В\nпадає на регуляторі як ТЕПЛО\n0.5 А × 1.7 В = 0.85 Вт грійки",
                    size=11, fill="#fff5e6", stroke=ORANGE, color=INK, bold=True))
    p.append(fitbox(70, 235, 260, 40, "ККД ≈ 3.3 / 5 ≈ 66 %",
                    size=12, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(fitbox(70, 290, 260, 56,
                    "+ тихо, дешево, чистий вихід\n− гаряче при великому падінні",
                    size=11, fill=BG, stroke=FIELD, color=INK))

    # ── ПРАВОРУЧ: імпульсний ──
    p.append(rect(390, 55, 340, 315, fill="#eef2ff", stroke=NEG, sw=1.6))
    p.append(text(560, 82, "Імпульсний (buck)", size=14, color=NEG, bold=True))
    p.append(fitbox(430, 110, 260, 40, "переливає струм: вихід > вхід",
                    size=11, fill=BG, stroke=INK, color=INK))
    p.append(fitbox(430, 165, 260, 56,
                    "потужність зберігається:\nIвх ≈ 3.3·0.5 / (5·0.9) ≈ 0.37 А\nвтрати лише ~0.18 Вт",
                    size=11, fill="#f4fbf6", stroke=FIELD, color=INK, bold=True))
    p.append(fitbox(430, 235, 260, 40, "ККД ≈ 90 % і вище",
                    size=12, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(fitbox(430, 290, 260, 56,
                    "+ мало тепла навіть при великому падінні\n− шум-пульсація, дорожче, котушка",
                    size=11, fill=BG, stroke=NEG, color=INK))

    return render(os.path.join(OUT, "ldo-vs-switcher.svg"), W, H, *p)


# ── decoupling: один далекий конденсатор мало ─────────────────────────────────
# Ідея: між регулятором і виводами модуля — опір і індуктивність доріжки. Коли
# модуль різко смикає струм, далекий конденсатор не встигає (дріт «гальмує»);
# маленька кераміка просто біля виводів віддає заряд миттєво.
def fig_decoupling():
    W, H = 760, 340
    p = []

    # регулятор ліворуч
    p.append(fitbox(30, 130, 120, 66, "Регулятор\n3.3 В",
                    size=12, fill="#f4fbf6", stroke=FIELD, color=FIELD, bold=True))

    # довга доріжка з індуктивністю/опором
    p.append(line(150, 163, 560, 163, color=INK, sw=2.4))
    p.append(text(355, 150, "доріжка: опір + індуктивність (гальмує струм)", size=10, color=MUTED))

    # об'ємний конденсатор біля регулятора
    p.append(line(200, 163, 200, 230, color=INK, sw=1.8))
    p.append(fitbox(150, 232, 100, 40, "об'ємний\n(далеко)", size=10, fill=BG, stroke=INK, color=INK))

    # локальна кераміка біля виводів
    p.append(line(520, 163, 520, 230, color=POS, sw=2.0))
    p.append(fitbox(468, 232, 108, 40, "кераміка\nбіля виводів", size=10, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # модуль праворуч
    p.append(fitbox(560, 130, 120, 66, "Модуль\n(різко смикає)",
                    size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))
    p.append(arrow(560, 196, 560, 210, color=POS, sw=2.4))
    p.append(text(620, 214, "піковий струм", size=10, color=POS, anchor="start"))

    # пояснення знизу
    box = fitbox(150, 285, 460, 42,
                 "Далекий конденсатор віддає ПОВІЛЬНИЙ струм; швидкий пік бере локальна кераміка просто біля виводів.",
                 size=11, fill="#f6f6f6", stroke=INK, color=INK)
    p.append(box)

    return render(os.path.join(OUT, "decoupling.svg"), W, H, *p)


# ── monitor-fsm: скінченний автомат сторожа живлення ───────────────────────────
# Ідея: два пороги (нижній V_SAG, вищий V_OK) розводять стани, щоб не торохтіти на
# межі. OK → важкі дії дозволені; SAG → заборонені; RECOVER → напруга піднялася,
# але чекаємо стабільно, перш ніж повертатись. Один поріг дав би дребезг.
def fig_monitor_fsm():
    W, H = 780, 360
    p = []

    # три стани в ряд
    yc = 150
    r = 52
    x_ok, x_sag, x_rec = 150, 630, 390

    # OK (зелений) — усе дозволено
    p.append(circle(x_ok, yc, r, fill="#eaf7ef", stroke=FIELD, sw=2.4))
    p.append(text(x_ok, yc - 6, "OK", size=16, color=FIELD, bold=True))
    p.append(text(x_ok, yc + 14, "все дозволено", size=9, color=INK))

    # SAG (червоний) — важкі дії заборонені
    p.append(circle(x_sag, yc, r, fill="#fdecea", stroke=POS, sw=2.4))
    p.append(text(x_sag, yc - 6, "SAG", size=16, color=POS, bold=True))
    p.append(text(x_sag, yc + 14, "радіо стоп", size=9, color=INK))

    # RECOVER (синій) — піднялися, але чекаємо
    p.append(circle(x_rec, yc, r, fill="#eaf0fd", stroke=NEG, sw=2.4))
    p.append(text(x_rec, yc - 6, "RECOVER", size=13, color=NEG, bold=True))
    p.append(text(x_rec, yc + 14, "тримай стабільно", size=9, color=INK))

    # OK → SAG (просіла нижче V_SAG) — верхня дуга праворуч
    p.append(arrow(x_ok + r, yc - 30, x_sag - r, yc - 30, color=POS, sw=2.0))
    p.append(text((x_ok + x_sag) / 2, yc - 42, "Vdd < V_SAG  (провал)", size=11, color=POS, bold=True))

    # SAG → RECOVER (піднялася вище V_OK)
    p.append(arrow(x_sag - r, yc + 24, x_rec + r, yc + 24, color=NEG, sw=2.0))
    p.append(text((x_sag + x_rec) / 2, yc + 42, "Vdd > V_OK", size=11, color=NEG, bold=True))

    # RECOVER → OK (протрималася t_hold)
    p.append(arrow(x_rec - r, yc + 24, x_ok + r, yc + 24, color=FIELD, sw=2.0))
    p.append(text((x_rec + x_ok) / 2, yc + 42, "стабільно t_hold", size=11, color=FIELD, bold=True))

    # RECOVER → SAG (знову провалилася, поки чекали) — коротка петля згори
    p.append(arrow(x_rec + 30, yc - r, x_sag - 30, yc - r + 6, color=POS, sw=1.6))
    p.append(text((x_rec + x_sag) / 2 + 6, yc - r - 6, "знов < V_SAG", size=9, color=POS))

    # підпис: чому два пороги
    p.append(fitbox(120, 272, 540, 54,
                    "Два різні пороги: V_SAG нижчий, V_OK вищий. Зазор між ними — гістерезис.\n"
                    "На самій межі стан не «торохтить» туди-сюди від кожного мілівольта шуму.",
                    size=11, fill="#f6f6f6", stroke=INK, color=INK))

    return render(os.path.join(OUT, "monitor-fsm.svg"), W, H, *p)


# ── power-up-order: поетапне ввімкнення вузлів через load switch ────────────────
# Ідея: вузли вмикають по черзі (спершу ядро/чутливе, тоді ненажерливе радіо),
# перевіряючи, що рейка втрималась після кожного кроку. Якщо просіла — скидання
# всієї послідовності, а не вперте ввімкнення наступного в просілу шину.
def fig_power_up_order():
    W, H = 780, 340
    p = []

    p.append(text(W / 2, 30, "Поетапне ввімкнення: кожен крок — тільки якщо рейка втрималась", size=12, bold=True))

    # чотири кроки конвеєром
    steps = [
        ("1. Регулятор\nрейка 3.3 В", "#f4fbf6", FIELD, FIELD),
        ("2. Ядро МК\n+ давач", "#eaf0fd", NEG, NEG),
        ("3. Пауза:\nрейка тримається?", "#fff5e6", ORANGE, INK),
        ("4. Радіо\n(ненажерливе)", "#fdecea", POS, POS),
    ]
    x = 24
    y = 90
    w = 168
    h = 74
    gap = 20
    cx_last = 0
    for i, (label, fill, stroke, color) in enumerate(steps):
        p.append(fitbox(x, y, w, h, label, size=11, fill=fill, stroke=stroke, color=color, bold=True))
        cx_last = x + w
        if i < len(steps) - 1:
            p.append(arrow(x + w, y + h / 2, x + w + gap, y + h / 2, color=INK, sw=2.0))
        x += w + gap

    # гілка «просіла» від кроку-паузи вниз — скидання
    x_pause = 24 + 2 * (w + gap)
    p.append(arrow(x_pause + w / 2, y + h, x_pause + w / 2, y + h + 40, color=POS, sw=2.0))
    p.append(fitbox(x_pause - 30, y + h + 42, w + 60, 44,
                    "просіла → СКИНУТИ все: вимкнути вузли, зачекати, пробувати спершу",
                    size=10, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # стрілка «повернення» від скидання назад до кроку 1
    p.append(line(x_pause - 30, y + h + 64, 108, y + h + 64, color=POS, sw=1.6, dash="5,4"))
    p.append(line(108, y + h + 64, 108, y + h, color=POS, sw=1.6, dash="5,4"))
    p.append(arrow(108, y + h, 108, y + h - 2, color=POS, sw=1.6))

    return render(os.path.join(OUT, "power-up-order.svg"), W, H, *p)


if __name__ == "__main__":
    fig_module_chain()
    fig_ldo_vs_switcher()
    fig_decoupling()
    fig_monitor_fsm()
    fig_power_up_order()
    print("OK figs:", sorted(os.listdir(OUT)))
