# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. stop-and-wait: часова діаграма Stop-and-Wait ARQ ────────────────────────
def fig_stop_and_wait():
    W, H = 820, 480
    p = []

    # Заголовок та напрямок часу
    p.append(text(140, 30, "Передавач (TX)", size=13, color=INK, bold=True))
    p.append(text(680, 30, "Приймач (RX)", size=13, color=INK, bold=True))

    # Вертикальні часові осі
    p.append(line(140, 45, 140, 435, color=LINE, sw=1.8))
    p.append(line(680, 45, 680, 435, color=LINE, sw=1.8))
    p.append(arrow(140, 430, 140, 450, color=LINE, sw=1.8))
    p.append(arrow(680, 430, 680, 450, color=LINE, sw=1.8))
    p.append(text(140, 468, "час t", size=11, color=MUTED, italic=True))
    p.append(text(680, 468, "час t", size=11, color=MUTED, italic=True))

    # ── Етап 1: Успішна передача Кадру 0 ──
    # Передача кадру 0 (T_frame)
    p.append(rect(125, 55, 30, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(140, 80, "Кадр 0", size=10, color=NEG, bold=True))
    p.append(line(115, 55, 115, 95, color=MUTED, sw=1.2))
    p.append(text(105, 78, "T_frame", size=9.5, color=MUTED, anchor="end"))

    # Поширення в каналі
    p.append(arrow(155, 55, 665, 115, color=NEG, sw=1.6))
    p.append(arrow(155, 95, 665, 155, color=NEG, sw=1.6))
    p.append(text(410, 80, "Кадр 0 (дані)", size=11, color=NEG, bold=True))

    # Приймач отримує та обробляє Кадр 0
    p.append(rect(665, 115, 30, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(680, 140, "Кадр 0", size=10, color=NEG, bold=True))

    # Приймач надсилає ACK 0
    p.append(arrow(665, 160, 155, 200, color=FIELD, sw=1.6))
    p.append(text(410, 172, "ACK 0 (підтверджено)", size=11, color=FIELD, bold=True))

    # Вимірювання T_prop та RTT
    p.append(line(490, 55, 490, 115, color=MUTED, sw=1, dash="3 3"))
    p.append(text(500, 90, "T_prop", size=9.5, color=MUTED, anchor="start"))

    # Зона простою передавача
    p.append(rect(145, 95, 12, 105, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=2))
    p.append(text(165, 150, "Простій TX (очікування ACK)", size=10, color="#856404", anchor="start", italic=True))

    # ── Етап 2: Втрата Кадру 1 та таймаут ──
    # Передача кадру 1
    p.append(rect(125, 210, 30, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(140, 235, "Кадр 1", size=10, color=POS, bold=True))

    # Політ кадру та втрата на півдорозі
    p.append(line(155, 210, 390, 250, color=POS, sw=1.6))
    p.append(line(155, 250, 390, 290, color=POS, sw=1.6))
    p.append(circle(390, 270, 14, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(390, 275, "✗", size=16, color=POS, bold=True))
    p.append(text(435, 274, "Кадр 1 втрачено в шумі", size=10.5, color=POS, bold=True, anchor="start"))

    # Таймер повтору RTO на передавачі
    p.append(line(115, 210, 115, 340, color=POS, sw=1.4, dash="4 3"))
    p.append(text(105, 275, "Таймаут (RTO)", size=9.5, color=POS, anchor="end", bold=True))

    # Повторна передача Кадру 1 після таймауту
    p.append(rect(125, 340, 30, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(140, 365, "Кадр 1", size=10, color=NEG, bold=True))
    p.append(text(80, 365, "Повтор", size=10, color=POS, bold=True))

    p.append(arrow(155, 340, 665, 400, color=NEG, sw=1.6))
    p.append(arrow(155, 380, 665, 440, color=NEG, sw=1.6))
    p.append(text(410, 385, "Кадр 1 (повторна передача)", size=11, color=NEG, bold=True))

    render(os.path.join(OUT, "stop-and-wait.svg"), W, H, *p,
           title="Часова діаграма Stop-and-Wait ARQ: успіх, втрата та таймаут")


# ── 2. sliding-window-concept: буфери ковзного вікна ────────────────────────────
def fig_sliding_window_concept():
    W, H = 820, 370
    p = []

    # ── Вікно передавача (Sender Window) ──
    p.append(text(40, 35, "Буфер передавача (Sender Window W = 4 кадри):", size=13, color=INK, bold=True, anchor="start"))

    cw, ch = 54, 46
    x0, y_s = 60, 60
    cells_s = [
        ("0", "#e2e8f0", MUTED, "Підтверджено"),
        ("1", "#e2e8f0", MUTED, "Підтверджено"),
        ("2", "#fdecea", POS, "У польоті"),
        ("3", "#fdecea", POS, "У польоті"),
        ("4", "#eef6ef", FIELD, "Готовий"),
        ("5", "#eef6ef", FIELD, "Готовий"),
        ("6", "#f4f6f8", MUTED, "Заблоковано"),
        ("7", "#f4f6f8", MUTED, "Заблоковано"),
        ("8", "#f4f6f8", MUTED, "Заблоковано"),
        ("9", "#f4f6f8", MUTED, "Заблоковано"),
        ("10", "#f4f6f8", MUTED, "Заблоковано"),
        ("11", "#f4f6f8", MUTED, "Заблоковано"),
    ]

    for i, (lab, fill, col, _) in enumerate(cells_s):
        x = x0 + i * cw
        p.append(rect(x, y_s, cw, ch, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(text(x + cw/2, y_s + ch/2 + 5, "#" + lab, size=11.5, color=col, bold=True))

    # Рамка ковзного вікна (від 2 до 5)
    win_x = x0 + 2 * cw
    win_w = 4 * cw
    p.append(rect(win_x - 3, y_s - 4, win_w + 6, ch + 8, fill="none", stroke="#2457d6", sw=2.2, rx=6))
    p.append(text(win_x + win_w/2, y_s - 14, "Ковзне вікно передавання W = 4", size=11, color=NEG, bold=True))

    # Покажчики
    p.append(arrow(win_x + cw/2, y_s + ch + 28, win_x + cw/2, y_s + ch + 4, color=POS, sw=1.6))
    p.append(text(win_x + cw/2, y_s + ch + 40, "Send Base (#2)", size=10.5, color=POS, bold=True))

    p.append(arrow(win_x + 2*cw + cw/2, y_s + ch + 28, win_x + 2*cw + cw/2, y_s + ch + 4, color=FIELD, sw=1.6))
    p.append(text(win_x + 2*cw + cw/2, y_s + ch + 40, "Next Seq Num (#4)", size=10.5, color=FIELD, bold=True))

    # ── Вікно приймача (Receiver Window) ──
    y_r = 230
    p.append(text(40, y_r - 25, "Буфер приймача (Selective Repeat, W_R = 4):", size=13, color=INK, bold=True, anchor="start"))

    cells_r = [
        ("0", "#e2e8f0", MUTED),
        ("1", "#e2e8f0", MUTED),
        ("2", "#fdecea", POS),     # Очікується (пропуск)
        ("3", "#eef6ef", FIELD),   # Прийнято out-of-order
        ("4", "#eaf0fd", NEG),     # Дозволено вікном
        ("5", "#eaf0fd", NEG),     # Дозволено вікном
        ("6", "#f4f6f8", MUTED),
        ("7", "#f4f6f8", MUTED),
        ("8", "#f4f6f8", MUTED),
        ("9", "#f4f6f8", MUTED),
        ("10", "#f4f6f8", MUTED),
        ("11", "#f4f6f8", MUTED),
    ]

    for i, (lab, fill, col) in enumerate(cells_r):
        x = x0 + i * cw
        p.append(rect(x, y_r, cw, ch, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(text(x + cw/2, y_r + ch/2 + 5, "#" + lab, size=11.5, color=col, bold=True))

    # Рамка вікна приймача
    p.append(rect(win_x - 3, y_r - 4, win_w + 6, ch + 8, fill="none", stroke="#2457d6", sw=2.2, rx=6))
    p.append(text(win_x + win_w/2, y_r - 12, "Вікно приймання W_R = 4", size=11, color=NEG, bold=True))

    # Покажчик очікуваного кадру
    p.append(arrow(win_x + cw/2, y_r + ch + 26, win_x + cw/2, y_r + ch + 4, color=POS, sw=1.6))
    p.append(text(win_x + cw/2, y_r + ch + 38, "Rcv Base (#2, чекаємо)", size=10.5, color=POS, bold=True))

    p.append(text(win_x + cw + cw/2, y_r + ch + 38, "#3 у буфері", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "sliding-window-concept.svg"), W, H, *p,
           title="Концепція ковзного вікна у передавача та приймача")


# ── 3. go-back-n-loss: масовий повтор при втраті кадру в Go-Back-N ──────────────
def fig_go_back_n_loss():
    W, H = 820, 520
    p = []

    p.append(text(140, 25, "Передавач TX (W = 4)", size=13, color=INK, bold=True))
    p.append(text(680, 25, "Приймач RX (W_R = 1)", size=13, color=INK, bold=True))

    p.append(line(140, 40, 140, 480, color=LINE, sw=1.8))
    p.append(line(680, 40, 680, 480, color=LINE, sw=1.8))
    p.append(arrow(140, 475, 140, 495, color=LINE, sw=1.8))
    p.append(arrow(680, 475, 680, 495, color=LINE, sw=1.8))

    # Пачка з 4 кадрів (0, 1, 2, 3)
    p.append(arrow(140, 50, 680, 95, color=NEG, sw=1.5))
    p.append(text(280, 62, "Кадр 0", size=10.5, color=NEG, bold=True))

    p.append(arrow(140, 75, 680, 120, color=NEG, sw=1.5))
    p.append(text(280, 87, "Кадр 1", size=10.5, color=NEG, bold=True))

    # Кадр 2 губиться
    p.append(line(140, 100, 410, 125, color=POS, sw=1.5))
    p.append(circle(410, 125, 11, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(410, 129, "✗", size=13, color=POS, bold=True))
    p.append(text(430, 128, "Кадр 2 втрачено", size=10, color=POS, bold=True, anchor="start"))

    p.append(arrow(140, 125, 680, 170, color=NEG, sw=1.5))
    p.append(text(280, 137, "Кадр 3", size=10.5, color=NEG, bold=True))

    # Відповіді приймача
    p.append(arrow(680, 95, 140, 140, color=FIELD, sw=1.5))
    p.append(text(540, 112, "ACK 0", size=10.5, color=FIELD, bold=True))

    p.append(arrow(680, 120, 140, 165, color=FIELD, sw=1.5))
    p.append(text(540, 137, "ACK 1", size=10.5, color=FIELD, bold=True))

    # Приймач отримує Кадр 3 поза чергою (чекає 2) -> ВІДКИДАЄ
    p.append(rect(665, 170, 30, 24, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
    p.append(text(710, 185, "Відкинуто! (чекає 2)", size=10, color=POS, bold=True, anchor="start"))

    p.append(arrow(680, 195, 140, 240, color="#d97706", sw=1.5))
    p.append(text(540, 212, "Дублікат ACK 1", size=10.5, color="#d97706", bold=True))

    # Таймаут Кадру 2 на передавачі
    p.append(line(115, 100, 115, 270, color=POS, sw=1.4, dash="3 3"))
    p.append(text(105, 190, "RTO Кадру 2", size=10, color=POS, anchor="end", bold=True))

    # Передавач повертається назад на N (Go-Back-N) і шле ВСЮ пачку 2, 3, 4, 5
    p.append(rect(60, 275, 160, 26, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(140, 292, "Go Back N: повтор 2, 3...", size=10.5, color=POS, bold=True))

    p.append(arrow(140, 310, 680, 355, color=POS, sw=1.6))
    p.append(text(280, 322, "Кадр 2 (повтор)", size=10.5, color=POS, bold=True))

    p.append(arrow(140, 335, 680, 380, color=POS, sw=1.6))
    p.append(text(280, 347, "Кадр 3 (повтор)", size=10.5, color=POS, bold=True))

    p.append(arrow(140, 360, 680, 405, color=NEG, sw=1.5))
    p.append(text(280, 372, "Кадр 4 (новий)", size=10.5, color=NEG, bold=True))

    p.append(arrow(140, 385, 680, 430, color=NEG, sw=1.5))
    p.append(text(280, 397, "Кадр 5 (новий)", size=10.5, color=NEG, bold=True))

    # Успішні ACK після повтору
    p.append(arrow(680, 355, 140, 400, color=FIELD, sw=1.5))
    p.append(text(540, 372, "ACK 2", size=10.5, color=FIELD, bold=True))

    p.append(arrow(680, 380, 140, 425, color=FIELD, sw=1.5))
    p.append(text(540, 397, "ACK 3", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "go-back-n-loss.svg"), W, H, *p,
           title="Go-Back-N ARQ: відкидання позачергових кадрів та повтор усього вікна")


# ── 4. selective-repeat-loss: точковий повтор у Selective Repeat ────────────────
def fig_selective_repeat_loss():
    W, H = 820, 520
    p = []

    p.append(text(140, 25, "Передавач TX (W_S = 4)", size=13, color=INK, bold=True))
    p.append(text(680, 25, "Приймач RX (W_R = 4)", size=13, color=INK, bold=True))

    p.append(line(140, 40, 140, 480, color=LINE, sw=1.8))
    p.append(line(680, 40, 680, 480, color=LINE, sw=1.8))
    p.append(arrow(140, 475, 140, 495, color=LINE, sw=1.8))
    p.append(arrow(680, 475, 680, 495, color=LINE, sw=1.8))

    # Пачка з 4 кадрів (0, 1, 2, 3)
    p.append(arrow(140, 50, 680, 95, color=NEG, sw=1.5))
    p.append(text(280, 62, "Кадр 0", size=10.5, color=NEG, bold=True))

    p.append(arrow(140, 75, 680, 120, color=NEG, sw=1.5))
    p.append(text(280, 87, "Кадр 1", size=10.5, color=NEG, bold=True))

    # Кадр 2 втрачено
    p.append(line(140, 100, 410, 125, color=POS, sw=1.5))
    p.append(circle(410, 125, 11, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(410, 129, "✗", size=13, color=POS, bold=True))
    p.append(text(430, 128, "Кадр 2 втрачено", size=10, color=POS, bold=True, anchor="start"))

    p.append(arrow(140, 125, 680, 170, color=NEG, sw=1.5))
    p.append(text(280, 137, "Кадр 3", size=10.5, color=NEG, bold=True))

    # Відповіді
    p.append(arrow(680, 95, 140, 140, color=FIELD, sw=1.5))
    p.append(text(540, 112, "ACK 0", size=10.5, color=FIELD, bold=True))

    p.append(arrow(680, 120, 140, 165, color=FIELD, sw=1.5))
    p.append(text(540, 137, "ACK 1", size=10.5, color=FIELD, bold=True))

    # Приймач отримує Кадр 3: БУФЕРИЗУЄ й шле ACK 3!
    p.append(rect(665, 170, 30, 24, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=3))
    p.append(text(710, 185, "Кадр 3 збережено в буфер!", size=10, color=FIELD, bold=True, anchor="start"))

    p.append(arrow(680, 195, 140, 240, color=FIELD, sw=1.5))
    p.append(text(540, 212, "ACK 3 (вибіркове)", size=10.5, color=FIELD, bold=True))

    # Таймаут лише для Кадру 2
    p.append(line(115, 100, 115, 270, color=POS, sw=1.4, dash="3 3"))
    p.append(text(105, 190, "RTO Кадру 2", size=10, color=POS, anchor="end", bold=True))

    # Передавач шле ЛИШЕ Кадр 2 (не чіпає 3, бо ACK3 вже прийшов!)
    p.append(rect(60, 275, 160, 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(140, 292, "Повтор ЛИШЕ Кадру 2", size=10.5, color=NEG, bold=True))

    p.append(arrow(140, 310, 680, 355, color=POS, sw=1.6))
    p.append(text(280, 322, "Кадр 2 (повторна передача)", size=10.5, color=POS, bold=True))

    # Приймач отримує Кадр 2, склеює з буферизованим 3 і віддає застосунку 2 і 3!
    p.append(rect(665, 355, 30, 24, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=3))
    p.append(text(710, 370, "Отримано 2 → віддано #2 і #3!", size=10, color=FIELD, bold=True, anchor="start"))

    p.append(arrow(680, 380, 140, 425, color=FIELD, sw=1.5))
    p.append(text(540, 397, "ACK 2 (вікно зсунуто)", size=10.5, color=FIELD, bold=True))

    # Передавач продовжує нові кадри
    p.append(arrow(140, 430, 680, 475, color=NEG, sw=1.5))
    p.append(text(280, 442, "Кадр 4 (новий)", size=10.5, color=NEG, bold=True))

    render(os.path.join(OUT, "selective-repeat-loss.svg"), W, H, *p,
           title="Selective Repeat ARQ: буферизація та точковий повтор втраченого кадру")


# ── 5. sequence-ambiguity: неоднозначність номерів при W > 2^(k-1) ──────────────
def fig_sequence_ambiguity():
    W, H = 840, 460
    p = []

    p.append(text(420, 25, "Чому розмір вікна має бути W <= 2^(k-1): приклад помилки при k = 2 (номери 0..3) та W = 3",
                  size=12, color=POS, bold=True))

    p.append(text(150, 60, "Передавач (W = 3)", size=12.5, color=INK, bold=True))
    p.append(text(690, 60, "Приймач (W_R = 3)", size=12.5, color=INK, bold=True))

    p.append(line(150, 75, 150, 415, color=LINE, sw=1.8))
    p.append(line(690, 75, 690, 415, color=LINE, sw=1.8))
    p.append(arrow(150, 410, 150, 430, color=LINE, sw=1.8))
    p.append(arrow(690, 410, 690, 430, color=LINE, sw=1.8))

    # Передавач шле 0, 1, 2
    p.append(arrow(150, 85, 690, 125, color=NEG, sw=1.5))
    p.append(text(300, 97, "Кадр 0 (епоха 1)", size=10.5, color=NEG, bold=True))

    p.append(arrow(150, 110, 690, 150, color=NEG, sw=1.5))
    p.append(text(300, 122, "Кадр 1 (епоха 1)", size=10.5, color=NEG, bold=True))

    p.append(arrow(150, 135, 690, 175, color=NEG, sw=1.5))
    p.append(text(300, 147, "Кадр 2 (епоха 1)", size=10.5, color=NEG, bold=True))

    # Приймач отримує 0, 1, 2 і ЗСУВАЄ вікно на [3, 0, 1]!
    p.append(rect(670, 185, 140, 36, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(740, 200, "Вікно зсунуто!", size=10, color=FIELD, bold=True))
    p.append(text(740, 214, "Нове вікно: [3, 0, 1]", size=10, color=FIELD, bold=True))

    # Усі ACK губляться в каналі!
    p.append(line(690, 140, 430, 160, color=POS, sw=1.5))
    p.append(text(415, 160, "✗ ACK 0 втрачено", size=10, color=POS, bold=True, anchor="end"))

    p.append(line(690, 165, 430, 185, color=POS, sw=1.5))
    p.append(text(415, 185, "✗ ACK 1 втрачено", size=10, color=POS, bold=True, anchor="end"))

    p.append(line(690, 190, 430, 210, color=POS, sw=1.5))
    p.append(text(415, 210, "✗ ACK 2 втрачено", size=10, color=POS, bold=True, anchor="end"))

    # Таймаут на передавачі для Кадру 0
    p.append(line(125, 85, 125, 260, color=POS, sw=1.4, dash="3 3"))
    p.append(text(115, 175, "RTO Кадру 0", size=10, color=POS, anchor="end", bold=True))

    # Передавач повторює СТАРИЙ Кадр 0
    p.append(arrow(150, 270, 690, 320, color=POS, sw=1.8))
    p.append(text(330, 285, "Повтор СТАРОГО Кадру 0 (епоха 1)", size=11, color=POS, bold=True))

    # КАТАСТРОФА: Приймач думає, що це НОВИЙ Кадр 0 з епохи 2!
    p.append(rect(650, 325, 180, 52, fill="#fdecea", stroke=POS, sw=1.8, rx=5))
    p.append(text(740, 345, "ФАТАЛЬНА ПОМИЛКА!", size=11, color=POS, bold=True))
    p.append(text(740, 362, "Приймач сприймає #0 як", size=10, color=POS))
    p.append(text(740, 374, "НОВИЙ кадр епохи 2!", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "sequence-ambiguity.svg"), W, H, *p,
           title="Неоднозначність номерів послідовності при перевищенні розміру вікна")


# ── 6. harq-combining: Chase Combining проти Incremental Redundancy ─────────────
def fig_harq_combining():
    W, H = 840, 430
    p = []

    # ── Ліва колонка: Chase Combining ──
    p.append(text(210, 30, "Chase Combining (CC, HARQ Type I)", size=13, color=NEG, bold=True))
    p.append(rect(20, 50, 380, 360, fill="#f8fafc", stroke=MUTED, sw=1.4, rx=6))

    # Спроба 1
    p.append(rect(40, 70, 160, 36, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(120, 93, "Спроба 1: Біти [S + P]", size=11, color=NEG, bold=True))
    p.append(text(210, 88, "→ Шумовий канал →", size=10, color=MUTED, anchor="start"))
    p.append(rect(320, 70, 60, 36, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(350, 93, "CRC ✗", size=11, color=POS, bold=True))

    p.append(arrow(350, 110, 350, 145, color=MUTED, sw=1.4))
    p.append(rect(270, 150, 120, 32, fill="#e2e8f0", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(330, 171, "Збережено LLR₁", size=10.5, color=INK, bold=True))

    # Спроба 2 (той самий пакет)
    p.append(rect(40, 210, 160, 36, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(120, 233, "Спроба 2: Ті самі [S + P]", size=10.5, color=NEG, bold=True))
    p.append(text(210, 228, "→ Шумовий канал →", size=10, color=MUTED, anchor="start"))
    p.append(rect(320, 210, 60, 36, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(350, 233, "LLR₂", size=11, color=NEG, bold=True))

    # Soft Combining
    p.append(arrow(330, 185, 330, 270, color=FIELD, sw=1.6))
    p.append(arrow(350, 250, 350, 270, color=FIELD, sw=1.6))
    p.append(rect(180, 275, 200, 40, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(280, 294, "Soft Combining (додавання LLR):", size=10, color=FIELD, bold=True))
    p.append(text(280, 308, "LLR_total = LLR₁ + LLR₂ (SNR ↑)", size=10.5, color=FIELD, bold=True))

    p.append(arrow(280, 320, 280, 345, color=FIELD, sw=1.6))
    p.append(rect(240, 350, 80, 36, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(280, 373, "CRC ✓", size=12, color=FIELD, bold=True))

    # ── Права колонка: Incremental Redundancy ──
    p.append(text(630, 30, "Incremental Redundancy (IR, HARQ Type II)", size=13, color=FIELD, bold=True))
    p.append(rect(440, 50, 380, 360, fill="#f8fafc", stroke=MUTED, sw=1.4, rx=6))

    # Спроба 1 (RV0)
    p.append(rect(460, 70, 160, 36, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(540, 93, "Спроба 1 (RV0): Інфо S + P₁", size=10.5, color=NEG, bold=True))
    p.append(text(630, 88, "→ R = 3/4 →", size=10, color=MUTED, anchor="start"))
    p.append(rect(740, 70, 60, 36, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(770, 93, "CRC ✗", size=11, color=POS, bold=True))

    p.append(arrow(770, 110, 770, 145, color=MUTED, sw=1.4))
    p.append(rect(690, 150, 120, 32, fill="#e2e8f0", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(750, 171, "Буфер: кодові біти RV0", size=10, color=INK, bold=True))

    # Спроба 2 (RV2 - нові біти надлишковості)
    p.append(rect(460, 210, 160, 36, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(540, 233, "Спроба 2 (RV2): Додаткові P₂", size=10.5, color=FIELD, bold=True))
    p.append(text(630, 228, "→ Нові біти →", size=10, color=MUTED, anchor="start"))
    p.append(rect(740, 210, 60, 36, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(770, 233, "RV2", size=11, color=FIELD, bold=True))

    # Зниження швидкості коду
    p.append(arrow(750, 185, 750, 270, color=FIELD, sw=1.6))
    p.append(arrow(770, 250, 770, 270, color=FIELD, sw=1.6))
    p.append(rect(590, 275, 215, 40, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(697, 294, "Об'єднання RV0 + RV2 у декодері:", size=10, color=FIELD, bold=True))
    p.append(text(697, 308, "Ефективна швидкість R: 3/4 → 1/2", size=10.5, color=FIELD, bold=True))

    p.append(arrow(697, 320, 697, 345, color=FIELD, sw=1.6))
    p.append(rect(657, 350, 80, 36, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(697, 373, "CRC ✓", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "harq-combining.svg"), W, H, *p,
           title="Механізми гібридного ARQ (HARQ): Chase Combining та Incremental Redundancy")


if __name__ == "__main__":
    fig_stop_and_wait()
    fig_sliding_window_concept()
    fig_go_back_n_loss()
    fig_selective_repeat_loss()
    fig_sequence_ambiguity()
    fig_harq_combining()
    print("All figures generated successfully.")
