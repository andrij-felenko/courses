# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── back-power-path: GPIO живить мертвий давач крізь захисний діод ──────────────
# Ідея (серце аудиту): чип спить, але один пін лишився HIGH і дивиться у вимкнений
# давач. Струм тече з піна крізь внутрішній ESD-діод давача в його мертву шину VDD
# і далі в землю. Це невидимий витік: на схемі давач «вимкнено», а він живиться
# через сигнальну ніжку. Показуємо саме цей паразитний шлях стрілками.

def fig_back_power():
    W, H = 720, 380
    p = []

    # ── чип (живий, спить) ліворуч ──
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 120, 180, 150
    p.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "Мікроконтролер", size=13, bold=True, color=FIELD))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "глибокий сон", size=11, color=MUTED, italic=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 96, "GPIO лишився", size=11, color=POS))
    b, _, _ = textbox(mcu_x + mcu_w / 2, mcu_y + 122, "HIGH = 3.3 В", size=12, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.6, pad=7)
    p.append(b)

    # вихідний пін чипа
    pin_y = mcu_y + 122
    p.append(circle(mcu_x + mcu_w, pin_y, 5, fill=POS, stroke=POS, sw=1))

    # ── давач (мертвий: живлення знято) праворуч ──
    s_x, s_y, s_w, s_h = 470, 120, 190, 180
    p.append(rect(s_x, s_y, s_w, s_h, fill="#f3f4f6", stroke=MUTED, sw=2, rx=8))
    p.append(text(s_x + s_w / 2, s_y + 24, "Давач", size=13, bold=True, color=MUTED))
    p.append(text(s_x + s_w / 2, s_y + 42, "живлення ЗНЯТО", size=11, color=MUTED, italic=True))

    # внутрішня шина VDD давача (мертва) + ESD-діод від піна до VDD
    vdd_y = s_y + 70
    p.append(line(s_x + 20, vdd_y, s_x + s_w - 20, vdd_y, color=MUTED, sw=2))
    p.append(text(s_x + s_w / 2, vdd_y - 8, "VDD давача (0 В, мертва)", size=10, color=MUTED))

    # вхідний пін давача
    spin_x = s_x
    p.append(circle(spin_x, pin_y, 5, fill=POS, stroke=POS, sw=1))
    # ESD-діод: трикутник від піна вгору до VDD (провідний у цьому напрямку)
    dx = spin_x + 34
    p.append(line(spin_x, pin_y, dx, pin_y, color=POS, sw=2.2))
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
             % (dx, pin_y - 11, dx, pin_y + 11, dx + 20, pin_y, POS))
    p.append(line(dx + 20, pin_y - 11, dx + 20, pin_y + 11, color=POS, sw=2.2))   # катод
    p.append(line(dx + 20, pin_y, dx + 20, vdd_y, color=POS, sw=2.2))
    p.append(line(dx + 20, vdd_y, dx + 20, vdd_y, color=POS, sw=2.2))
    p.append(text(dx + 8, pin_y + 30, "ESD-діод", size=10, color=POS, italic=True))

    # шлях у землю давача
    gnd_y = s_y + s_h - 24
    p.append(line(dx + 20, vdd_y, s_x + s_w - 30, vdd_y, color=POS, sw=2.2))
    p.append(line(s_x + s_w - 30, vdd_y, s_x + s_w - 30, gnd_y, color=POS, sw=2.2))
    # символ землі
    gx = s_x + s_w - 30
    for i, ww in enumerate((18, 12, 6)):
        p.append(line(gx - ww / 2, gnd_y + i * 5, gx + ww / 2, gnd_y + i * 5, color=MUTED, sw=2))
    p.append(text(gx, gnd_y + 30, "GND", size=10, color=MUTED))

    # ── паразитний струм: товста червона стрілка від піна чипа до піна давача ──
    p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="3.2" '
             'marker-end="url(#arrow)"/>' % (mcu_x + mcu_w + 4, pin_y, spin_x - 6, pin_y, POS))
    b, _, _ = textbox((mcu_x + mcu_w + spin_x) / 2, pin_y - 34, "паразитний струм\nкрізь сигнальну ніжку",
                      size=11, bold=True, color=POS, fill="#fff5f5", stroke=POS, sw=1.5, pad=8)
    p.append(b)

    p.append(text(W / 2, H - 16,
                  "вимкнений давач живиться через ніжку даних — на схемі його «нема», а він пʼє струм",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "back-power-path.svg"), W, H, *p,
           title="Зворотне живлення: HIGH-пін у мертвий давач")


# ── bisection: аудит діленням навпіл по дереву живлення ────────────────────────
# Ідея: витік невидимий, вузлів багато — не вгадуй, а діли. Лічильник у корені
# показує сумарний струм; піднімаєш (відрізаєш) гілку — дивишся, на скільки впав
# струм. Велике падіння = винний у цій гілці. Так половиниш плату до винуватця.

def fig_bisection():
    W, H = 720, 420
    p = []

    # вузол-вимірювач у корені дерева
    mx, my = 360, 70
    b, _, _ = textbox(mx, my, "лічильник у розриві\nживлення: 480 мкА", size=12, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.8, pad=10)
    p.append(b)

    # шина живлення
    rail_y = my + 50
    p.append(line(140, rail_y, 580, rail_y, color=INK, sw=2.4))
    p.append(line(mx, my + 18, mx, rail_y, color=INK, sw=2))

    # чотири гілки: чип, давач (винний), радіо, дисплей
    branches = [
        (200, "Чип\n(сон)", "12 мкА", FIELD, "#eafaf1", False),
        (340, "Давач-\nгілка", "440 мкА", POS, "#fdecea", True),   # винна
        (450, "Радіо\n(off)", "6 мкА", MUTED, "#f3f4f6", False),
        (550, "Дисплей\n(off)", "22 мкА", MUTED, "#f3f4f6", False),
    ]
    for bx, lab, cur, col, fill, guilty in branches:
        p.append(line(bx, rail_y, bx, rail_y + 40, color=INK, sw=2))
        # на винній гілці — ножиці/розрив
        if guilty:
            p.append(line(bx - 9, rail_y + 18, bx + 9, rail_y + 26, color=POS, sw=2.2))
            p.append(line(bx - 9, rail_y + 26, bx + 9, rail_y + 18, color=POS, sw=2.2))
            p.append(text(bx + 30, rail_y + 24, "відрізали тут", size=10, color=POS, italic=True))
        bb, _, _ = textbox(bx, rail_y + 66, lab, size=11, bold=True,
                           color=col, fill=fill, stroke=col, sw=1.6, pad=8)
        p.append(bb)
        p.append(text(bx, rail_y + 104, cur, size=11, bold=True, color=col))

    # результат: після відрізання струм упав до 40 мкА
    res_y = rail_y + 150
    b, _, _ = textbox(mx, res_y, "відрізали давач-гілку → лічильник упав 480 → 40 мкА",
                      size=12, bold=True, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10)
    p.append(b)
    p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % (mx, rail_y + 116, mx, res_y - 22, FIELD))

    p.append(text(W / 2, res_y + 50,
                  "велике падіння струму вказує гілку-винуватця — далі ділиш уже її",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "bisection.svg"), W, H, *p,
           title="Аудит діленням навпіл по дереву живлення")


# ── audit-loop: процедура аудиту як замкнений цикл ─────────────────────────────
# Ідея: аудит — не разовий погляд, а цикл. Ціль → виміряй → над бюджетом? →
# поділи й знайди шлях → виправ → переміряй. Виходиш із циклу, коли чип став
# найбільшим споживачем (далі економити нема на чому).

def fig_audit_loop():
    W, H = 720, 430
    p = []
    cx, cy = 360, 215
    boxes = [
        (360, 70,  "1. Ціль\nбюджет спокою", FIELD, "#eafaf1"),
        (590, 160, "2. Виміряй\nреальний струм", NEG, "#eaf0fd"),
        (590, 290, "3. Над бюджетом?\nподіли навпіл", POS, "#fdecea"),
        (360, 370, "4. Знайди шлях\nвитоку", POS, "#fdecea"),
        (130, 290, "5. Виправ\n(HW/FW)", NEG, "#eaf0fd"),
        (130, 160, "6. Переміряй", FIELD, "#eafaf1"),
    ]
    pts = []
    for bx, by, lab, col, fill in boxes:
        b, w, h = textbox(bx, by, lab, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.8, pad=10)
        p.append(b)
        pts.append((bx, by, w, h))

    # стрілки по колу 1→2→3→4→5→6→(2)
    def edge(a, b):
        x1, y1, w1, h1 = pts[a]
        x2, y2, w2, h2 = pts[b]
        import math
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * (w1 / 2 + 6), y1 + uy * (h1 / 2 + 6)
        ex, ey = x2 - ux * (w2 / 2 + 10), y2 - uy * (h2 / 2 + 10)
        return ('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.0" '
                'marker-end="url(#arrow)"/>' % (sx, sy, ex, ey, MUTED))
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]:
        p.append(edge(a, b))
    # цикл назад: 6 → 3 (переміряв — знов перевір бюджет) пунктиром усередину
    x6, y6, w6, h6 = pts[5]
    x3, y3, w3, h3 = pts[2]
    p.append('<path d="M%.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (x6 + w6 / 2 - 4, y6 + 10, cx + 30, cy, x3 - w3 / 2 + 4, y3 - 8, MUTED))

    # центр: умова виходу
    b, _, _ = textbox(cx, cy, "вихід:\nчип — найбільший\nспоживач", size=11, bold=True,
                      color=FIELD, fill="#f0fff4", stroke=FIELD, sw=1.6, pad=9)
    p.append(b)

    render(os.path.join(OUT, "audit-loop.svg"), W, H, *p,
           title="Аудит струму спокою як замкнений цикл")


# ── firmware-pipeline: прошивкова частина аудиту як конвеєр ────────────────────
# Ідея: шлях у сон — це послідовність, що повторює фізику. Профіль зводить усі
# ніжки в безпечний рівень → вузли гасяться в порядку «сигнали → VDD» → заморозка
# тримає рівні на deep-sleep → ізоляція прибирає струм RTC-ніжок → сон. Збоку —
# два інструменти контролю: self-test (ділення навпіл) і baseline (проти регресій).

def fig_firmware_pipeline():
    W, H = 760, 430
    p = []

    # ── головний конвеєр: чотири стадії → сон ──
    stages = [
        (130, "1. Профіль ніжок\nусі → LOW / Hi-Z", FIELD, "#eafaf1"),
        (300, "2. Порядок гасіння\nсигнали → VDD", NEG, "#eaf0fd"),
        (470, "3. Заморозка\nhold + deep-sleep", POS, "#fdecea"),
        (630, "4. Ізоляція\nRTC-ніжок", POS, "#fdecea"),
    ]
    row_y = 110
    pts = []
    for sx, lab, col, fill in stages:
        b, w, h = textbox(sx, row_y, lab, size=11, bold=True, color=col,
                          fill=fill, stroke=col, sw=1.8, pad=9)
        p.append(b)
        pts.append((sx, w, h))

    # стрілки порядку між стадіями
    for i in range(len(pts) - 1):
        x1, w1, _ = pts[i]
        x2, w2, _ = pts[i + 1]
        p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
                 'stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (x1 + w1 / 2 + 4, row_y, x2 - w2 / 2 - 8, row_y, INK))

    # підпис над стрілками: фізика порядку
    p.append(text(W / 2, row_y - 52,
                  "обов'язковий шлях у сон — порядок повторює фізику засинання",
                  size=11, color=MUTED, italic=True))

    # фінал конвеєра: deep-sleep
    last_x, last_w, _ = pts[-1]
    sleep_y = row_y + 80
    b, _, _ = textbox(last_x, sleep_y, "esp_deep_sleep_start()", size=11, bold=True,
                      color=INK, fill="#f0f2f5", stroke=INK, sw=1.8, pad=9)
    p.append(b)
    p.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (last_x, row_y + 22, last_x, sleep_y - 20, INK))

    # ── два інструменти контролю збоку (окрема смуга) ──
    ctrl_y = 300
    p.append(line(70, ctrl_y - 36, W - 70, ctrl_y - 36, color=MUTED, sw=1, dash="4 4"))
    p.append(text(W / 2, ctrl_y - 18, "інструменти контролю (режим обслуговування)",
                  size=11, color=MUTED, italic=True))

    b, w1, _ = textbox(235, ctrl_y + 24, "self-test:\nділення навпіл по гілках",
                       size=11, bold=True, color=FIELD, fill="#eafaf1",
                       stroke=FIELD, sw=1.8, pad=10)
    p.append(b)
    p.append(text(235, ctrl_y + 70, "гасить гілки по черзі → внесок кожної",
                  size=10, color=MUTED, italic=True))

    b, w2, _ = textbox(525, ctrl_y + 24, "baseline:\nзахист від регресій",
                       size=11, bold=True, color=NEG, fill="#eaf0fd",
                       stroke=NEG, sw=1.8, pad=10)
    p.append(b)
    p.append(text(525, ctrl_y + 70, "звіряє кожну збірку з записаним числом",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "firmware-pipeline.svg"), W, H, *p,
           title="Прошивкова частина аудиту струму спокою")


if __name__ == "__main__":
    fig_back_power()
    fig_bisection()
    fig_audit_loop()
    fig_firmware_pipeline()
    print("OK: figures written to", OUT)
