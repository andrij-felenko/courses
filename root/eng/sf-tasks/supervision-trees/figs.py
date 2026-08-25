# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. tree-structure.svg: Ієрархія дерева нагляду ─────────────────────────
def fig_tree_structure():
    W, H = 760, 380
    p = []
    
    # Заголовок / фон
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    # Корінь (Root Supervisor)
    root_x, root_y = 380, 50
    root_box, rw, rh = textbox(root_x, root_y, "Кореневий наглядач (Root Supervisor)\nСтратегія: one_for_all", size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=2.0)
    p.append(root_box)
    
    # Середній рівень: Підсистема мережі та Підсистема сховища
    net_x, net_y = 200, 160
    db_x, db_y = 560, 160
    
    net_box, nw, nh = textbox(net_x, net_y, "Наглядач мережі (Net Supervisor)\nСтратегія: one_for_one", size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    db_box, dw, dh = textbox(db_x, db_y, "Наглядач даних (DB Supervisor)\nСтратегія: rest_for_one", size=11, bold=True, fill="#fdf6e3", stroke="#b58900", sw=1.8)
    p.append(net_box)
    p.append(db_box)
    
    # Зв'язки корінь -> підсистеми
    p.append(arrow(root_x - 70, root_y + rh/2, net_x, net_y - nh/2 - 2, color=NEG, sw=1.6))
    p.append(arrow(root_x + 70, root_y + rh/2, db_x, db_y - dh/2 - 2, color=NEG, sw=1.6))
    
    # Робочі процеси під мережею
    w1_x, w1_y = 110, 270
    w2_x, w2_y = 290, 270
    
    w1_box, _, _ = textbox(w1_x, w1_y, "TCP Приймач\n(Worker)", size=10, fill=FILL, stroke=LINE, sw=1.4)
    w2_box, _, _ = textbox(w2_x, w2_y, "Пул з'єднань\n(Worker)", size=10, fill=FILL, stroke=LINE, sw=1.4)
    p.append(w1_box)
    p.append(w2_box)
    
    p.append(arrow(net_x - 40, net_y + nh/2, w1_x, w1_y - 20, color=FIELD, sw=1.4))
    p.append(arrow(net_x + 40, net_y + nh/2, w2_x, w2_y - 20, color=FIELD, sw=1.4))
    
    # Робочі процеси під сховищем
    w3_x, w3_y = 470, 270
    w4_x, w4_y = 650, 270
    
    w3_box, _, _ = textbox(w3_x, w3_y, "Драйвер диска\n(Worker)", size=10, fill=FILL, stroke=LINE, sw=1.4)
    w4_box, _, _ = textbox(w4_x, w4_y, "Кеш запитів\n(Worker)", size=10, fill=FILL, stroke=LINE, sw=1.4)
    p.append(w3_box)
    p.append(w4_box)
    
    p.append(arrow(db_x - 40, db_y + dh/2, w3_x, w3_y - 20, color="#b58900", sw=1.4))
    p.append(arrow(db_x + 40, db_y + dh/2, w4_x, w4_y - 20, color="#b58900", sw=1.4))
    
    # Стрілки напрямків (легенда)
    p.append(arrow(40, 100, 40, 200, color=NEG, sw=2.0))
    p.append(text(48, 150, "Нагляд і команди перезапуску (згори вниз)", size=10, color=NEG, anchor="start", bold=True))
    
    p.append(arrow(720, 200, 720, 100, color=POS, sw=2.0))
    p.append(text(712, 150, "Сигнали смерті та ескалація (знизу вгору)", size=10, color=POS, anchor="end", bold=True))
    
    # Нижня плашка
    p.append(fitbox(W/2 - 250, 335, 500, 28, "Ізоляція відмов: падіння TCP-приймача не впливає на підсистему даних", size=11, fill="#f4f6f8", stroke=MUTED, sw=1.2, italic=True))
    
    render(os.path.join(OUT, "tree-structure.svg"), W, H, *p, title="Ієрархічна структура дерева нагляду")


# ── 2. restart-strategies.svg: Порівняння стратегій ────────────────────────
def fig_restart_strategies():
    W, H = 760, 390
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    # Три колонки для трьох стратегій
    cols = [
        (130, "one_for_one", "Один за одного", "Падає лише B →\nперезапускається тільки B"),
        (380, "one_for_all", "Один за всіх", "Падає B → зупиняються\nі перезапускаються A, B, C"),
        (630, "rest_for_one", "Решта за одним", "Падає B → перезапускаються\nлише B і наступний C; A цілий")
    ]
    
    for cx, strat, label_ukr, desc in cols:
        # Заголовок колонки
        p.append(fitbox(cx - 105, 25, 210, 52, f"{strat}\n({label_ukr})", size=11, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5))
        
        # Наглядач
        sup_box, _, _ = textbox(cx, 110, "Наглядач", size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.5)
        p.append(sup_box)
        
        # Працівники A, B, C
        y_a, y_b, y_c = 180, 240, 300
        
        if strat == "one_for_one":
            a_box, _, _ = textbox(cx - 70, y_a, "A (цілий)", size=10, fill="#eafaf0", stroke=FIELD, sw=1.4)
            b_box, _, _ = textbox(cx, y_b, "B (ЗБІЙ → РЕСТАРТ)", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
            c_box, _, _ = textbox(cx + 70, y_c, "C (цілий)", size=10, fill="#eafaf0", stroke=FIELD, sw=1.4)
        elif strat == "one_for_all":
            a_box, _, _ = textbox(cx - 70, y_a, "A (РЕСТАРТ)", size=10, fill="#fff3cd", stroke="#e67e22", sw=1.4)
            b_box, _, _ = textbox(cx, y_b, "B (ЗБІЙ → РЕСТАРТ)", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
            c_box, _, _ = textbox(cx + 70, y_c, "C (РЕСТАРТ)", size=10, fill="#fff3cd", stroke="#e67e22", sw=1.4)
        else: # rest_for_one
            a_box, _, _ = textbox(cx - 70, y_a, "A (недоторканий)", size=10, fill="#eafaf0", stroke=FIELD, sw=1.4)
            b_box, _, _ = textbox(cx, y_b, "B (ЗБІЙ → РЕСТАРТ)", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
            c_box, _, _ = textbox(cx + 70, y_c, "C (РЕСТАРТ)", size=10, fill="#fff3cd", stroke="#e67e22", sw=1.4)
            
        p.append(a_box)
        p.append(b_box)
        p.append(c_box)
        
        # Стрілки від наглядача
        p.append(line(cx, 125, cx - 70, y_a - 15, color=MUTED, sw=1.2))
        p.append(line(cx, 125, cx, y_b - 15, color=POS, sw=1.6))
        p.append(line(cx, 125, cx + 70, y_c - 15, color=MUTED, sw=1.2))
        
        # Опис внизу
        p.append(textbox(cx, 355, desc, size=9.5, fill="none", stroke="none", color=INK)[0])
    
    # Вертикальні розділювачі
    p.append(line(255, 20, 255, 375, color="#e0e0e0", sw=1.0, dash="4,4"))
    p.append(line(505, 20, 505, 375, color="#e0e0e0", sw=1.0, dash="4,4"))
    
    render(os.path.join(OUT, "restart-strategies.svg"), W, H, *p, title="Стратегії перезапуску дочірніх процесів")


# ── 3. escalation-budget.svg: Бюджет перезапусків та ескалація ─────────────
def fig_escalation_budget():
    W, H = 740, 310
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    # Шкала часу
    t_start, t_end = 40, 700
    t_y = 120
    p.append(arrow(t_start, t_y, t_end, t_y, color=INK, sw=2.0))
    p.append(text(t_end + 10, t_y + 4, "Час (t)", size=11, bold=True, color=INK, anchor="start"))
    
    # Вікно MaxT (повністю охоплює всі внутрішні елементи)
    w_left, w_right = 150, 650
    p.append(rect(w_left, 45, w_right - w_left, 175, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text((w_left + w_right)/2, 68, "Ковзне часове вікно: MaxT = 10 секунд", size=11, bold=True, color=POS))

    # Збої (хрестики / спалахи)
    crashes = [
        (205, "Збій 1 (t=2с)\nПерезапуск", FIELD),
        (315, "Збій 2 (t=5с)\nПерезапуск", FIELD),
        (425, "Збій 3 (t=7с)\nПерезапуск", "#b58900"),
        (555, "Збій 4 (t=9с)\nПоза MaxR=3!", POS)
    ]

    for cx, label, col in crashes:
        p.append(circle(cx, t_y, 7, fill=col, stroke=INK, sw=1.5))
        p.append(line(cx, t_y - 20, cx, t_y + 20, color=col, sw=2.0))
        tbox, _, _ = textbox(cx, t_y + 45, label, size=9.5, bold=(col == POS), fill="#ffffff", stroke=col, sw=1.2)
        p.append(tbox)
    
    # Ескалація вгору
    p.append(arrow(555, 90, 555, 25, color=POS, sw=2.4))
    p.append(fitbox(425, 10, 260, 24, "ЕСКАЛАЦІЯ: Наглядач завершується аварійно", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.5, color=POS))
    
    # Пояснення внизу
    p.append(fitbox(W/2 - 270, 255, 540, 42, "Правило інтенсивності: якщо процес зазнає понад MaxR аварій за вікно MaxT,\nзбій вважається системним. Наглядач убиває всіх нащадків і передає аварію вище.", size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    
    render(os.path.join(OUT, "escalation-budget.svg"), W, H, *p, title="Інтенсивність збоїв і лавинна ескалація")


# ── 4. lifecycle-states.svg: Життєвий цикл дочірнього процесу ──────────────
def fig_lifecycle_states():
    W, H = 740, 320
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    
    # Стани
    s_init, _, _ = textbox(110, 80, "Початок\n(Init / Start)", size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6)
    s_run, _, _ = textbox(300, 80, "Робота\n(Running)", size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    s_norm, _, _ = textbox(520, 80, "Нормальний вихід\n(:normal / exit 0)", size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.4)
    
    s_crash, _, _ = textbox(300, 200, "Аварія / Збій\n(Crash / Panic)", size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    s_check, _, _ = textbox(520, 200, "Перевірка restart_type\n(permanent / transient)", size=10, bold=True, fill="#fdf6e3", stroke="#b58900", sw=1.5)
    s_stop, _, _ = textbox(660, 140, "Зупинка\n(Terminated)", size=10.5, fill="#eaeaea", stroke="#777777", sw=1.4)
    
    p += [s_init, s_run, s_norm, s_crash, s_check, s_stop]
    
    # Стрілки переходів
    p.append(arrow(155, 80, 255, 80, color=FIELD, sw=1.6)) # init -> run
    p.append(arrow(345, 80, 445, 80, color=MUTED, sw=1.4)) # run -> normal exit
    p.append(arrow(595, 80, 640, 120, color=MUTED, sw=1.4)) # normal -> stop (якщо transient/temporary)
    
    p.append(arrow(300, 105, 300, 175, color=POS, sw=1.8)) # run -> crash
    p.append(text(310, 140, "необроблений виняток", size=9, color=POS, anchor="start"))
    
    p.append(arrow(355, 200, 445, 200, color=POS, sw=1.6)) # crash -> check
    
    # Перевірка -> Рестарт (петля назад до Init)
    p.append(line(520, 225, 520, 270, color=FIELD, sw=1.6))
    p.append(line(520, 270, 110, 270, color=FIELD, sw=1.6))
    p.append(arrow(110, 270, 110, 105, color=FIELD, sw=1.6))
    p.append(text(315, 285, "Бюджет не вичерпано → Перезапуск у чистому стані", size=10, color=FIELD, bold=True))
    
    # Перевірка -> Зупинка / Ескалація (якщо temporary або бюджет вичерпано)
    p.append(arrow(585, 190, 640, 155, color=POS, sw=1.4))
    p.append(text(625, 220, "Бюджет вичерпано\n→ Ескалація", size=9, color=POS))
    
    render(os.path.join(OUT, "lifecycle-states.svg"), W, H, *p, title="Життєвий цикл та логіка відновлення дочірнього процесу")


if __name__ == "__main__":
    fig_tree_structure()
    fig_restart_strategies()
    fig_escalation_budget()
    fig_lifecycle_states()
    print("All figures generated successfully.")
