# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Скінченний автомат станів сервера Raft ───────────────────────────
def fig_state_transitions():
    W, H = 1000, 560
    p = []

    # Три основні ролі вузла
    fw, fh = 220.0, 100.0
    
    # Координати центрів вузлів: Follower (ліворуч), Candidate (по центру вгорі), Leader (праворуч)
    fx, fy = 160.0, 410.0
    cx, cy = 500.0, 190.0
    lx, ly = 840.0, 410.0

    # Follower
    p.append(fitbox(fx - fw/2, fy - fh/2, fw, fh, 
                    "ФОЛОВЕР (Follower)\n\nПасивний стан: відповідає на RPC,\nскидає таймаут виборів",
                    size=13, fill="#f4f6f8", stroke=LINE, bold=True))

    # Candidate
    p.append(fitbox(cx - fw/2, cy - fh/2, fw, fh, 
                    "КАНДИДАТ (Candidate)\n\nІнкрементує терм, голосує за себе,\nнадсилає RequestVote усім",
                    size=13, fill="#fef9e7", stroke="#d4ac0d", bold=True))

    # Leader
    p.append(fitbox(lx - fw/2, ly - fh/2, fw, fh, 
                    "ЛІДЕР (Leader)\n\nОбслуговує клієнтів, розсилає\nсерцебиття та реплікує лог",
                    size=13, fill="#eef7f0", stroke=FIELD, bold=True))

    # 1. Follower -> Candidate (таймаут виборів)
    p.append(arrow(fx + 20, fy - fh/2, cx - fw/2 + 20, cy + fh/2, color=POS, sw=2.0))
    p.append(textbox(260, 260, "таймаут виборів сплив,\nпочаток виборів", size=11,
                     fill="#ffffff", stroke=POS, color=POS, bold=True)[0])

    # 2. Candidate -> Leader (отримано голоси більшості)
    p.append(arrow(cx + fw/2 - 20, cy + fh/2, lx - 20, ly - fh/2, color=FIELD, sw=2.0))
    p.append(textbox(740, 260, "зібрано голоси більшості\nкворуму (N/2 + 1)", size=11,
                     fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)[0])

    # 3. Candidate -> Candidate (новий таймаут, розкол голосів)
    p.append(line(cx - 60, cy - fh/2, cx - 60, cy - fh/2 - 30, color=LINE, sw=1.6))
    p.append(line(cx - 60, cy - fh/2 - 30, cx + 60, cy - fh/2 - 30, color=LINE, sw=1.6))
    p.append(arrow(cx + 60, cy - fh/2 - 30, cx + 60, cy - fh/2, color=LINE, sw=1.6))
    p.append(textbox(cx, cy - fh/2 - 50, "таймаут сплив без більшості:\nновий терм, нові вибори", size=10.5,
                     fill="#ffffff", stroke=MUTED, color=INK)[0])

    # 4. Leader -> Follower (виявлено вищий терм)
    p.append(arrow(lx - fw/2, ly + 20, fx + fw/2, fy + 20, color=NEG, sw=2.0))
    p.append(textbox(500, 475, "виявлено повідомлення з вищим термом T > currentTerm\n(або дізнався про нового легітимного лідера)", size=11,
                     fill="#ffffff", stroke=NEG, color=NEG, bold=True)[0])

    # 5. Candidate -> Follower (виявлено нового лідера або вищий терм)
    p.append(arrow(cx - 20, cy + fh/2, fx + 70, fy - fh/2, color=MUTED, sw=1.6))
    p.append(textbox(470, 335, "отримано AppendEntries від нового\nлідера або знайдено вищий терм", size=10.5,
                     fill="#ffffff", stroke=MUTED, color=INK)[0])

    # Початковий запуск (Start -> Follower)
    p.append(arrow(fx - fw/2 - 60, fy, fx - fw/2, fy, color=LINE, sw=2.0))
    p.append(text(fx - fw/2 - 35, fy - 12, "старт вузла", size=11, color=MUTED, bold=True))

    render(os.path.join(OUT, "state-transitions.svg"), W, H, *p,
           title="Скінченний автомат станів сервера Raft")


# ── Фіг. 2: Структура реплікованого логу та коміт-індекс ─────────────────────
def fig_log_structure():
    W, H = 960, 440
    p = []

    # 5 вузлів, 8 записів у лозі
    nodes = [
        ("Вузол 1 (Лідер)", [ (1,"x←3"), (1,"y←1"), (1,"z←0"), (2,"x←4"), (3,"x←5"), (3,"y←9"), (3,"x←7"), (3,"z←2") ]),
        ("Вузол 2 (Фоловер)", [ (1,"x←3"), (1,"y←1"), (1,"z←0"), (2,"x←4"), (3,"x←5"), (3,"y←9"), (3,"x←7"), None ]),
        ("Вузол 3 (Фоловер)", [ (1,"x←3"), (1,"y←1"), (1,"z←0"), (2,"x←4"), (3,"x←5"), None, None, None ]),
        ("Вузол 4 (Фоловер)", [ (1,"x←3"), (1,"y←1"), (1,"z←0"), (2,"x←4"), (2,"x←2"), None, None, None ]),
        ("Вузол 5 (Фоловер)", [ (1,"x←3"), (1,"y←1"), (1,"z←0"), None, None, None, None, None ]),
    ]

    x0 = 220.0
    y0 = 80.0
    cw = 80.0
    ch = 50.0
    row_gap = 62.0

    # Заголовки індексів
    for idx in range(1, 9):
        cx = x0 + (idx - 1) * cw + cw / 2
        p.append(text(cx, y0 - 15, f"Індекс {idx}", size=12, color=MUTED, bold=True))

    for r_idx, (n_name, entries) in enumerate(nodes):
        cy = y0 + r_idx * row_gap
        # Назва вузла
        is_leader = "Лідер" in n_name
        p.append(fitbox(20, cy, 180, ch, n_name, size=12,
                        fill="#eef7f0" if is_leader else "#f4f6f8",
                        stroke=FIELD if is_leader else LINE, bold=True))

        for c_idx, item in enumerate(entries):
            cx = x0 + c_idx * cw
            if item is None:
                p.append(rect(cx, cy, cw, ch, fill="#ffffff", stroke="#e5e7eb", sw=1.0, rx=4))
                continue
            term, cmd = item
            
            # Колір коміту: індекси 1..5 зафіксовані більшістю (на вузлах 1, 2, 3)
            # індекс 6..8 ще не зафіксовані
            is_committed = (c_idx + 1) <= 5 and (r_idx <= 2 or (c_idx + 1 <= 4 and r_idx == 3))
            
            if (c_idx + 1) <= 5:
                box_fill = "#eef7f0" if is_committed else "#fef9e7"
                box_stroke = FIELD if is_committed else "#d4ac0d"
            else:
                box_fill = "#ffffff"
                box_stroke = LINE

            p.append(rect(cx, cy, cw, ch, fill=box_fill, stroke=box_stroke, sw=1.5, rx=4))
            # Терм (вгорі маленьким) та команда (по центру)
            p.append(text(cx + cw/2, cy + 16, f"терм {term}", size=10, color=MUTED))
            p.append(text(cx + cw/2, cy + 36, cmd, size=13, color=INK, bold=True))

    # Лінія коміту (commitIndex = 5)
    commit_x = x0 + 5 * cw
    p.append(line(commit_x, y0 - 30, commit_x, y0 + 5 * row_gap - 10, color=FIELD, sw=2.5, dash="6,4"))
    p.append(textbox(commit_x, y0 + 5 * row_gap + 15, "commitIndex = 5\n(зафіксовано на більшості 3/5 вузлів)",
                     size=11.5, fill="#f4f8f4", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(OUT, "log-structure.svg"), W, H, *p,
           title="Організація реплікованого логу: індекси, терми та лінія фіксації")


# ── Фіг. 3: Аномалія коміту з попереднього терму (Figure 8 Онгаро) ───────────
def fig_term_commitment_anomaly():
    W, H = 960, 480
    p = []

    # Дві паралельні колонки: (A) Небезпечна наївна фіксація старого терму, (B) Правило Raft
    pw = 430.0
    ph = 370.0
    py = 65.0

    # Панель A (Сценарій перезапису запису старого терму)
    ax = 35.0
    p.append(rect(ax, py, pw, ph, fill="#fffaf9", stroke=POS, sw=1.5, rx=10))
    p.append(text(ax + pw/2, py + 26, "Аномалія: наївна фіксація чужого терму", size=14, color=POS, bold=True))
    p.append(fitbox(ax + 20, py + 50, pw - 40, 75,
                    "1. Терм 2: S1 записує (T2) на індекс 2 на сервери S1, S2.\n"
                    "2. S1 падає. S5 стає лідером у термі 3 за голосами S3, S4, S5.\n"
                    "3. S5 пише (T3) в індекс 2 і падає. S1 відновлюється в термі 4.",
                    size=11, fill="#ffffff", stroke="#f5c6cb", color=INK))

    p.append(fitbox(ax + 20, py + 135, pw - 40, 95,
                    "4. S1 реплікує старий запис (T2) на S3 — тепер (T2) на більшості (S1, S2, S3)!\n"
                    "ЯКБИ S1 вважав (T2) коміченим лише за кворумом копій:\n"
                    "S1 падає, S5 прокидається й обирається в термі 5 (голоси S2, S3, S4, S5),\n"
                    "бо його лог (T3 на індексі 2) не старіший за їхні!\n"
                    "S5 перетирає «комічений» запис (T2) своїм (T3) на всіх вузлах!",
                    size=10.5, fill="#fdecea", stroke=POS, color=POS, bold=True))

    p.append(textbox(ax + pw/2, py + 290, "НАСЛІДОК:\nВтрата зафіксованих даних і розходження автоматів",
                     size=11.5, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # Панель B (Залізне правило безпеки Raft)
    bx = 495.0
    p.append(rect(bx, py, pw, ph, fill="#f9fbf9", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(bx + pw/2, py + 26, "Захист Raft: фіксація через ПОТОЧНИЙ терм", size=14, color=FIELD, bold=True))
    
    p.append(fitbox(bx + 20, py + 50, pw - 40, 75,
                    "Правило Raft (§5.4.2):\n"
                    "Лідер НІКОЛИ не фіксує напряму записи попередніх термів,\n"
                    "просто підраховуючи кількість їхніх реплік на фоловерах.",
                    size=11.5, fill="#ffffff", stroke="#c3e6cb", color=INK, bold=True))

    p.append(fitbox(bx + 20, py + 135, pw - 40, 95,
                    "Як досягається безпека:\n"
                    "1. Лідер терму 4 зобов'язаний записати новий запис (T4) у свій терм.\n"
                    "2. Коли запис (T4) успішно репліковано на більшість вузлів,\n"
                    "   усі попередні записи (зокрема T2) фіксуються НЕПРЯМО завдяки\n"
                    "   властивості Log Matching.\n"
                    "3. Тепер S5 не зможе отримати голоси S1, S2, S3 (їхній останній терм 4 > 3).",
                    size=11, fill="#f4f8f4", stroke=FIELD, color=INK))

    p.append(textbox(bx + pw/2, py + 290, "РЕЗУЛЬТАТ:\nІнваріант Leader Completeness збережено на 100%",
                     size=11.5, fill="#eef7f0", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(OUT, "term-commitment-anomaly.svg"), W, H, *p,
           title="Аномалія Онгаро (Рис. 8): чому не можна комітити старі терми за кворумом")


# ── Фіг. 4: Мережевий розкол, робота більшості та зцілення ───────────────────
def fig_network_partition():
    W, H = 960, 460
    p = []

    # Ліва половина: Меншість (2 вузли)
    mx, my, mw, mh = 30.0, 70.0, 420.0, 350.0
    p.append(rect(mx, my, mw, mh, fill="#fffaf9", stroke=POS, sw=1.5, rx=10))
    p.append(text(mx + mw/2, my + 26, "Ізольована меншість (2 вузли з 5)", size=13.5, color=POS, bold=True))
    
    # Вузли меншості
    p.append(fitbox(mx + 30, my + 55, 160, 50, "S1 (Старий Лідер, T1)", size=11, fill="#fdecea", stroke=POS, bold=True))
    p.append(fitbox(mx + 230, my + 55, 160, 50, "S2 (Фоловер, T1)", size=11, fill="#f4f6f8", stroke=LINE))
    
    p.append(fitbox(mx + 20, my + 130, mw - 40, 100,
                    "• Клієнт шле запис W1 на S1.\n"
                    "• S1 додає W1 у свій лог і шле AppendEntries на S2.\n"
                    "• Разом є 2 копії. Але кворум вимагає 3 (5/2 + 1)!\n"
                    "• S1 НЕ МОЖЕ зафіксувати W1 і не відповідає успіхом клієнту.",
                    size=11, fill="#ffffff", stroke="#f5c6cb", color=INK))

    p.append(textbox(mx + mw/2, my + 285, "Стан: записи висять незафіксованими,\nвідсутній прогрес",
                     size=11.5, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # Червона стіна розриву мережі посередині (два сегменти лінії, щоб не перетинати напис)
    sep_x = 480.0
    p.append(line(sep_x, 50, sep_x, 195, color=POS, sw=3.0, dash="8,5"))
    p.append(textbox(sep_x, 245, "МЕРЕЖЕВИЙ\nРОЗКОЛ\n(Partition)", size=11,
                     fill="#ffffff", stroke=POS, color=POS, bold=True)[0])
    p.append(line(sep_x, 295, sep_x, 430, color=POS, sw=3.0, dash="8,5"))

    # Права половина: Більшість (3 вузли)
    rx, ry, rw, rh = 510.0, 70.0, 420.0, 350.0
    p.append(rect(rx, ry, rw, rh, fill="#f9fbf9", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(rx + rw/2, ry + 26, "Активна більшість (3 вузли з 5)", size=13.5, color=FIELD, bold=True))

    # Вузли більшості
    p.append(fitbox(rx + 20, ry + 55, 120, 50, "S3 (Лідер, T2)", size=11, fill="#eef7f0", stroke=FIELD, bold=True))
    p.append(fitbox(rx + 150, ry + 55, 120, 50, "S4 (Фоловер, T2)", size=11, fill="#f4f6f8", stroke=LINE))
    p.append(fitbox(rx + 280, ry + 55, 120, 50, "S5 (Фоловер, T2)", size=11, fill="#f4f6f8", stroke=LINE))

    p.append(fitbox(rx + 20, ry + 130, rw - 40, 100,
                    "• S3 обирається лідером у новому термі 2 (3 голоси).\n"
                    "• Клієнт шле запис W2 на S3.\n"
                    "• S3 реплікує W2 на S4 та S5 (кворум 3/3 зібрано!).\n"
                    "• S3 фіксує W2 (commitIndex зростає) і звітує успіх.",
                    size=11, fill="#ffffff", stroke="#c3e6cb", color=INK))

    p.append(textbox(rx + rw/2, ry + 285, "Зцілення мережі:\nS1 бачить терм 2 → стає фоловером;\nнезафіксований W1 на S1 замінюється на W2",
                     size=11, fill="#eef7f0", stroke=FIELD, color=FIELD, bold=True)[0])

    render(os.path.join(OUT, "network-partition.svg"), W, H, *p,
           title="Поведінка Raft під час розділення мережі та узгодження після зцілення")


if __name__ == "__main__":
    fig_state_transitions()
    fig_log_structure()
    fig_term_commitment_anomaly()
    fig_network_partition()
    print("All figures generated successfully.")
