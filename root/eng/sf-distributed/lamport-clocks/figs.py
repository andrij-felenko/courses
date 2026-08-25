# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Дрейф фізичних годинників і стрибок часу NTP ─────────────────────
def fig_drift_and_ntp():
    W, H = 960, 480
    p = []

    # Заголовок / підзаголовок панелей
    p.append(fitbox(20, 16, 440, 44, "Дрейф кварцових генераторів", size=14, fill="#fbfdff", stroke="#dfe4ea", bold=True))
    p.append(fitbox(500, 16, 440, 44, "Корекція NTP: плавне підтягування vs стрибок", size=14, fill="#fbfdff", stroke="#dfe4ea", bold=True))

    # Ліва панель: Дрейф двох вузлів
    p.append(rect(20, 70, 440, 390, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Осі часу
    p.append(text(40, 100, "Ідеальний час T (еталон):", size=12, color=MUTED, anchor="start", bold=True))
    p.append(line(40, 120, 430, 120, color=LINE, sw=1.8))
    for i, t in enumerate(["0 с", "+100 с", "+200 с", "+300 с"]):
        x = 60 + i * 110
        p.append(line(x, 115, x, 125, color=LINE, sw=1.5))
        p.append(text(x, 140, t, size=11, color=MUTED))

    # Сервер 1 (+30 ppm, поспішає)
    p.append(text(40, 180, "Сервер A (частота +30 ppm — поспішає):", size=12, color=POS, anchor="start", bold=True))
    p.append(line(40, 200, 430, 200, color=POS, sw=1.8))
    for i, t in enumerate(["0.00 с", "+100.003 с", "+200.006 с", "+300.009 с"]):
        x = 60 + i * 110
        p.append(line(x, 195, x, 205, color=POS, sw=1.5))
        p.append(text(x, 220, t, size=10.5, color=POS))

    # Сервер 2 (-40 ppm, відстає)
    p.append(text(40, 260, "Сервер B (частота −40 ppm — відстає):", size=12, color=NEG, anchor="start", bold=True))
    p.append(line(40, 280, 430, 280, color=NEG, sw=1.8))
    for i, t in enumerate(["0.00 с", "+99.996 с", "+199.992 с", "+299.988 с"]):
        x = 60 + i * 110
        p.append(line(x, 275, x, 285, color=NEG, sw=1.5))
        p.append(text(x, 300, t, size=10.5, color=NEG))

    # Пояснення розходження (skew)
    p.append(fitbox(40, 330, 400, 110,
                    "Розходження (skew) через 300 с = 21 мс\n"
                    "За добу накопичується понад 6 секунд розриву.\n"
                    "Настінний годинник фізично не здатен гарантувати\n"
                    "однаковий час на різних материнських платах.",
                    size=12, fill="#fef9f8", stroke=POS, color=INK))

    # Права панель: NTP корекція (Slew vs Step)
    p.append(rect(500, 70, 440, 390, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Варіант 1: Плавний дрейф (Slew)
    p.append(text(520, 100, "1. Плавне зведення (Slewing / adjtime):", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(line(520, 140, 910, 140, color=MUTED, sw=1.2, dash="4,4"))
    # Лінія часу плавно прискорюється
    p.append(line(520, 150, 700, 145, color=FIELD, sw=2))
    p.append(line(700, 145, 910, 140, color=FIELD, sw=2))
    p.append(text(710, 125, "годинник плавно сповільнюється/прискорюється (монотонно)", size=11, color=FIELD))

    # Варіант 2: Стрибок (Step)
    p.append(text(520, 185, "2. Стрибок (Clock Step / settimeofday):", size=12.5, color=POS, anchor="start", bold=True))
    p.append(line(520, 240, 680, 210, color=POS, sw=2))
    # Стрибок вниз (назад у часі)
    p.append(arrow(680, 210, 680, 255, color=POS, sw=2.2))
    p.append(line(680, 255, 910, 225, color=POS, sw=2))
    
    b1, _, _ = textbox(770, 205, "Стрибок назад на −50 мс!", size=11.5, pad=6, fill="#fdecea", stroke=POS, color=POS, bold=True)
    p.append(b1)

    # Катастрофічний наслідок стрибка назад
    p.append(fitbox(520, 280, 400, 160,
                    "Катастрофа стрибка назад (t_новше < t_давніше):\n"
                    "• Порушення монотонності часу (t2 < t1)\n"
                    "• Відповідь у логах з'являється РАНІШЕ за запит\n"
                    "• Таймаути зависають або спрацьовують миттєво\n"
                    "• База даних з Last-Write-Wins стирає свіжі транзакції\n"
                    "  старішим фізичним штампом часу.",
                    size=12, fill="#fdf2ee", stroke=POS, color=INK))

    render(os.path.join(OUT, "clock-drift-and-ntp.svg"), W, H, *p,
           title="Чому фізичний годинник бреше: дрейф генераторів та аномалії NTP")


# ── Фігура 2: Просторово-часова діаграма і відношення «сталося раніше» ──────────
def fig_happened_before():
    W, H = 960, 460
    p = []

    # Заголовок
    p.append(text(480, 36, "Просторово-часова діаграма причинності (Happened-Before Relation)", size=16, bold=True))

    # Три процеси (горизонтальні лінії часу зліва направо)
    pnames = ["Вузол P1", "Вузол P2", "Вузол P3"]
    py_coords = [110, 230, 350]

    for name, y in zip(pnames, py_coords):
        p.append(text(30, y + 5, name, size=13, color=INK, anchor="start", bold=True))
        p.append(arrow(110, y, 920, y, color=LINE, sw=1.8))
        p.append(text(925, y + 5, "час", size=11, color=MUTED, anchor="start"))

    events = [
        # (x, y, label, name, fill)
        (180, 110, "e11", "a", "#eef2f7"),
        (320, 110, "e12", "b (send m1)", "#fdecea"),
        (760, 110, "e13", "x (локальна)", "#eef7f0"),

        (220, 230, "e21", "c", "#eef2f7"),
        (450, 230, "e22", "d (recv m1)", "#fdecea"),
        (580, 230, "e23", "e (send m2)", "#fdf2ee"),
        (820, 230, "e24", "f", "#eef2f7"),

        (260, 350, "e31", "y (локальна)", "#eef7f0"),
        (720, 350, "e32", "g (recv m2)", "#fdf2ee"),
        (860, 350, "e33", "h", "#eef2f7"),
    ]

    # Стрілки повідомлень (причинні переходи через мережу)
    p.append(arrow(320, 110, 450, 230, color=POS, sw=2.2))
    p.append(text(395, 160, "повідомлення m1", size=11.5, color=POS, bold=True, italic=True))

    p.append(arrow(580, 230, 720, 350, color=NEG, sw=2.2))
    p.append(text(660, 280, "повідомлення m2", size=11.5, color=NEG, bold=True, italic=True))

    # Малювання вузлів подій
    for ex, ey, elbl, edesc, efill in events:
        p.append(circle(ex, ey, 14, fill=efill, stroke=LINE, sw=1.8))
        p.append(text(ex, ey + 4, elbl, size=11, bold=True))
        p.append(text(ex, ey - 20, edesc, size=10, color=MUTED))

    # Причинний ланцюжок
    p.append(fitbox(40, 400, 440, 46,
                    "Причинний ланцюг: e11 → e12 → e22 → e23 → e32 → e33\n"
                    "(транзитивність: дія на P1 причинно вплинула на стан P3)",
                    size=11.5, fill="#f4f8f4", stroke=FIELD, color=INK, bold=True))

    # Паралельні події
    p.append(fitbox(500, 400, 440, 46,
                    "Паралельні події (concurrent): e13 || e31\n"
                    "Немає шляху повідомлень: жодна не передує іншій!",
                    size=11.5, fill="#fef9f8", stroke=POS, color=INK, bold=True))

    render(os.path.join(OUT, "happened-before-spacetime.svg"), W, H, *p,
           title="Відношення «сталося раніше» (Happened-Before) та паралельність")


# ── Фігура 3: Еволюція лічильників годинника Лампорта ──────────────────────────
def fig_lamport_evolution():
    W, H = 960, 480
    p = []

    pnames = ["Вузол A", "Вузол B", "Вузол C"]
    py_coords = [110, 230, 350]

    for name, y in zip(pnames, py_coords):
        p.append(text(30, y + 5, name, size=13, color=INK, anchor="start", bold=True))
        p.append(arrow(110, y, 920, y, color=LINE, sw=1.8))

    # Стрілка m1: A(340, 110) -> B(460, 230)
    p.append(arrow(340, 110, 460, 230, color=POS, sw=2.2))
    b_m1, _, _ = textbox(410, 155, "m1 (ts=2)", size=11, pad=5, fill="#ffffff", stroke=POS, color=POS, bold=True)
    p.append(b_m1)

    # Стрілка m2: B(600, 230) -> C(740, 350)
    p.append(arrow(600, 230, 740, 350, color=NEG, sw=2.2))
    b_m2, _, _ = textbox(680, 275, "m2 (ts=4)", size=11, pad=5, fill="#ffffff", stroke=NEG, color=NEG, bold=True)
    p.append(b_m2)

    cevents = [
        # (x, y, L_val, label, note)
        (180, 110, 1, "eA1", "L=1"),
        (340, 110, 2, "eA2", "L=2 (send)"),
        (780, 110, 3, "eA3", "L=3"),

        (240, 230, 1, "eB1", "L=1"),
        (460, 230, 3, "eB2", "L=max(1,2)+1=3"),
        (600, 230, 4, "eB3", "L=4 (send)"),

        (200, 350, 1, "eC1", "L=1"),
        (300, 350, 2, "eC2", "L=2"),
        (740, 350, 5, "eC3", "L=max(2,4)+1=5"),
        (860, 350, 6, "eC4", "L=6"),
    ]

    for cx, cy, cval, clbl, cnote in cevents:
        is_recv = "max" in cnote
        fill = "#eef7f0" if is_recv else "#fbfdff"
        stroke = FIELD if is_recv else LINE
        sw = 2.2 if is_recv else 1.5

        p.append(circle(cx, cy, 16, fill=fill, stroke=stroke, sw=sw))
        p.append(text(cx, cy + 5, str(cval), size=13, bold=True, color=FIELD if is_recv else INK))
        p.append(text(cx, cy - 24, clbl, size=10.5, color=MUTED, bold=True))
        p.append(text(cx, cy + 30, cnote, size=10, color=FIELD if is_recv else MUTED))

    # Висновок про властивості годинника
    p.append(fitbox(30, 410, 440, 56,
                    "Правило оновлення: L := max(L_local, L_msg) + 1\n"
                    "Гарантія годинника: якщо a → b, то завжди L(a) < L(b).",
                    size=12, fill="#f4f8f4", stroke=FIELD, color=INK, bold=True))

    p.append(fitbox(490, 410, 440, 56,
                    "Пастка однобічності: L(eA3)=3 < L(eB3)=4, але eA3 || eB3!\n"
                    "З меншого L НЕ випливає причинний зв'язок (потрібні вектори).",
                    size=12, fill="#fdf2ee", stroke=POS, color=POS, bold=True))

    render(os.path.join(OUT, "lamport-clock-evolution.svg"), W, H, *p,
           title="Робота логічного годинника Лампорта: оновлення лічильників при обміні")


# ── Фігура 4: Побудова тотального порядку через кортеж (L, PID) ────────────────
def fig_total_order():
    W, H = 960, 450
    p = []

    # Ліва частина: Частковий порядок (DAG причинності з паралельними гілками)
    p.append(fitbox(20, 16, 440, 40, "Частковий порядок причинності (Poset DAG)", size=13.5, fill="#fbfdff", stroke="#dfe4ea", bold=True))
    p.append(rect(20, 66, 440, 360, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    dag_nodes = [
        (100, 140, "a: (1, Node A)", "#eef2f7"),
        (360, 140, "b: (1, Node B)", "#eef2f7"),
        (100, 260, "c: (2, Node A)", "#eef7f0"),
        (360, 260, "d: (2, Node B)", "#eef7f0"),
        (230, 360, "e: (3, Node B)", "#fdecea"),
    ]

    p.append(arrow(100, 165, 100, 235, color=LINE, sw=1.8))
    p.append(arrow(360, 165, 360, 235, color=LINE, sw=1.8))
    p.append(arrow(120, 280, 210, 340, color=LINE, sw=1.8))
    p.append(arrow(340, 280, 250, 340, color=LINE, sw=1.8))

    p.append(line(160, 140, 300, 140, color=POS, sw=1.5, dash="4,4"))
    p.append(text(230, 130, "a || b (непорівнянні)", size=11, color=POS))

    for nx, ny, nlbl, nfill in dag_nodes:
        b, _, _ = textbox(nx, ny, nlbl, size=11.5, pad=6, fill=nfill, stroke=LINE)
        p.append(b)

    # Права частина: Тотальний лінійний порядок (Total Order)
    p.append(fitbox(500, 16, 440, 40, "Тотальний порядок через розв'язання нічиїх (L, PID)", size=13.5, fill="#fbfdff", stroke="#dfe4ea", bold=True))
    p.append(rect(500, 66, 440, 360, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    p.append(text(520, 95, "Правило порівняння: (L_1, PID_1) < (L_2, PID_2)", size=12, color=MUTED, anchor="start", bold=True))

    ordered_steps = [
        ("1. Подія a", "(L=1, PID=A)", "найменший L, PID A < B", "#eef2f7"),
        ("2. Подія b", "(L=1, PID=B)", "той самий L=1, але PID B > A", "#eef2f7"),
        ("3. Подія c", "(L=2, PID=A)", "більший L=2, PID A < B", "#eef7f0"),
        ("4. Подія d", "(L=2, PID=B)", "той самий L=2, PID B > A", "#eef7f0"),
        ("5. Подія e", "(L=3, PID=B)", "найбільший L=3", "#fdecea"),
    ]

    for i, (title, tuple_lbl, reason, cfill) in enumerate(ordered_steps):
        sy = 130 + i * 55
        p.append(fitbox(520, sy, 400, 44,
                        "%s  →  %s  [%s]" % (title, tuple_lbl, reason),
                        size=11.5, fill=cfill, stroke=LINE, color=INK))
        if i < 4:
            p.append(arrow(720, sy + 44, 720, sy + 54, color=FIELD, sw=2))

    render(os.path.join(OUT, "total-order-tiebreak.svg"), W, H, *p,
           title="Перетворення часткового порядку на тотальний через кортежі (L, PID)")


if __name__ == "__main__":
    fig_drift_and_ntp()
    fig_happened_before()
    fig_lamport_evolution()
    fig_total_order()
    print("Всі 4 фігури успішно згенеровано.")
