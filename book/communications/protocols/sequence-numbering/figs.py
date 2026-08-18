# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. sequence-wrap-around: простір номерів за модулем 2^N ────────────────────
def fig_sequence_wrap_around():
    W, H = 840, 520
    p = []

    cx, cy, R = 420, 270, 170

    # Заголовок та підзаголовок
    p.append(text(W / 2, 32, "Кільцевий числовий простір номерів послідовності за модулем 2^N", size=15, color=INK, bold=True))
    p.append(text(W / 2, 54, "Вікно однозначності: майбутні пакети [+1, +2^(N-1)-1] та минулі пакети [-2^(N-1), -1]", size=11.5, color=MUTED))

    # Сектори кільця (колами / секторами)
    # Зовнішнє кільце
    p.append(circle(cx, cy, R, fill="#f8fafc", stroke=LINE, sw=2.0))
    p.append(circle(cx, cy, R - 55, fill=BG, stroke=LINE, sw=1.5))

    # Права половина (Майбутні пакети / випередження) - зеленуватий сектор
    # Візуалізуємо дугами або підписами секторів
    # Верхня точка: seq_max (кут -90 градусів = зверху)
    # Поділимо на сектори:
    # 1. Точка seq_max (зверху)
    p.append(line(cx, cy - R + 55, cx, cy - R, color=POS, sw=3))
    p.append(circle(cx, cy - R, 7, fill=POS, stroke=BG, sw=1.5))
    tb_max, _, _ = textbox(cx, cy - R - 24, "seq_max (поточний максимум)", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    p.append(tb_max)

    # 2. Протилежна точка: горизонт неоднозначності (seq_max + 2^(N-1))
    p.append(line(cx, cy + R - 55, cx, cy + R, color="#d97706", sw=3, dash="4 3"))
    p.append(circle(cx, cy + R, 6, fill="#fef3c7", stroke="#d97706", sw=1.5))
    tb_amb, _, _ = textbox(cx, cy + R + 26, "Горизонт невизначеності: seq_max ± 2^(N-1)\n(дистанція рівно напівпростору)", size=11, pad=6, fill="#fef3c7", stroke="#d97706", bold=True)
    p.append(tb_amb)

    # Права дуга: майбутні пакети (+1 .. +2^(N-1)-1)
    p.append(arrow(cx + 80, cy - 120, cx + 130, cy - 60, color=FIELD, sw=2.2))
    p.append(text(cx + 125, cy - 8, "Майбутні номери (Δ > 0)", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 125, cy + 12, "seq ∈ [seq_max + 1,  seq_max + 2^(N-1) - 1]", size=10.5, color=INK, anchor="start"))
    p.append(text(cx + 125, cy + 30, "• Новий пакет або пропуск (втрата)", size=10, color=MUTED, anchor="start"))
    p.append(text(cx + 125, cy + 46, "• Просування seq_max уперед", size=10, color=MUTED, anchor="start"))

    # Ліва дуга: минулі пакети (-2^(N-1)+1 .. -1)
    p.append(arrow(cx - 130, cy - 60, cx - 80, cy - 120, color=NEG, sw=2.2))
    p.append(text(cx - 125, cy - 8, "Минулі номери (Δ < 0)", size=12.5, color=NEG, bold=True, anchor="end"))
    p.append(text(cx - 125, cy + 12, "seq ∈ [seq_max - 2^(N-1) + 1,  seq_max - 1]", size=10.5, color=INK, anchor="end"))
    p.append(text(cx - 125, cy + 30, "• Перевпорядкований пакет (запізнілий)", size=10, color=MUTED, anchor="end"))
    p.append(text(cx - 125, cy + 46, "• Дублікат або застарілий кадр", size=10, color=MUTED, anchor="end"))

    # Центральна мітка
    p.append(text(cx, cy - 15, "Модуль M = 2^N", size=13, color=INK, bold=True))
    p.append(text(cx, cy + 6, "Напівпростір W = 2^(N-1)", size=11, color=MUTED))
    p.append(text(cx, cy + 24, "Приклад N=8: M=256, W=128", size=10, color=MUTED, italic=True))

    # Стрілка напрямку зростання
    p.append(arrow(cx + 18, cy - 155, cx + 55, cy - 150, color=FIELD, sw=2.0))
    p.append(text(cx + 70, cy - 155, "+1 зростання", size=10, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "sequence-wrap-around.svg"), W, H, *p)


# ── 2. packet-triage-loss-reorder: тріаж пакетів на приймачі ───────────────────
def fig_packet_triage():
    W, H = 840, 470
    p = []

    p.append(text(W / 2, 28, "Алгоритм розпізнавання: черговість, втрати, перевпорядкування та дублікати", size=14.5, color=INK, bold=True))
    p.append(text(W / 2, 48, "Тріаж вхідного пакета через знакову модульну дистанцію d = (intN_t)(seq - seq_expected)", size=11, color=MUTED))

    # Вхідний блок
    tb_in, _, _ = textbox(130, 110, "Вхідний пакет із номером seq\nПоточний очікуваний номер: seq_exp", size=11, pad=8, fill="#f0f4f8", stroke=LINE, bold=True)
    p.append(tb_in)

    # Обчислення дистанції
    p.append(arrow(240, 110, 310, 110, color=LINE, sw=1.8))
    tb_calc, _, _ = textbox(430, 110, "Знакова різниця за модулем 2^N:\nΔ = (intN_t)(seq - seq_exp)", size=11.5, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    p.append(tb_calc)

    # Розгалуження на 3 гілки
    # 1. Δ == 0 (Черговий пакет)
    p.append(arrow(430, 140, 160, 220, color=FIELD, sw=2.0))
    tb_zero, _, _ = textbox(160, 260, "Δ = 0: Очікуваний пакет (In-Order)\n• Віддати застосунку негайно\n• Зсунути seq_exp = seq + 1\n• Перевірити буфер перевпорядкування", size=10.5, pad=8, fill="#eafaf1", stroke=FIELD, bold=True)
    p.append(tb_zero)
    p.append(text(250, 175, "Δ = 0 (черга)", size=10.5, color=FIELD, bold=True))

    # 2. Δ > 0 (Випередження: втрата або пропуск)
    p.append(arrow(430, 140, 430, 220, color=POS, sw=2.0))
    tb_pos, _, _ = textbox(430, 270, "0 < Δ < 2^(N-1): Випередження (Gap)\n• Зафіксувати втрату пакетів: [seq_exp .. seq-1]\n• Збільшити лічильник втрат: loss += Δ\n• Зберегти поточний seq у буфер черги\n• Оновити seq_max = seq", size=10.5, pad=8, fill="#fdecea", stroke=POS, bold=True)
    p.append(tb_pos)
    p.append(text(440, 175, "Δ > 0 (пропуск)", size=10.5, color=POS, bold=True, anchor="start"))

    # 3. Δ < 0 (Минулий пакет: перевпорядкування або дублікат)
    p.append(arrow(430, 140, 700, 220, color=NEG, sw=2.0))
    tb_neg, _, _ = textbox(700, 270, " -2^(N-1) < Δ < 0: Минулий пакет\n• Перевірити вікно прийому (бітову маску)\n• Якщо біт = 1 → ДУБЛІКАТ (відкинути)\n• Якщо біт = 0 → ПЕРЕВПОРЯДКОВАНИЙ\n  (заповнити дірку в буфері, відновити потік)", size=10.5, pad=8, fill="#eaf0fd", stroke=NEG, bold=True)
    p.append(tb_neg)
    p.append(text(610, 175, "Δ < 0 (минуле)", size=10.5, color=NEG, bold=True))

    # Нижня рамка: результат
    p.append(rect(60, 370, 720, 75, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 395, "Підсумок класифікації та реакція приймача", size=12, color=INK, bold=True))
    p.append(text(420, 416, "Помилкова класифікація унеможливлюється, якщо затримка перевпорядкування не перевищує 2^(N-1) пакетів", size=10.5, color=MUTED))
    p.append(text(420, 433, "Коректна обробка вимагає ковзної маски отриманих пакетів або черги відкладеної доставки", size=10.5, color=MUTED))

    render(os.path.join(OUT, "packet-triage-loss-reorder.svg"), W, H, *p)


# ── 3. jitter-calculation: затримка та розрахунок джиттера за RFC 3550 ─────────
def fig_jitter_calculation():
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 28, "Часові мітки та розрахунок інтервального джиттера (RFC 3550)", size=14.5, color=INK, bold=True))
    p.append(text(W / 2, 48, "Оцінка варіації мережевої затримки: D(i, j) = (R_j - S_j) - (R_i - S_i),  J = J + (|D| - J) / 16", size=11, color=MUTED))

    # Вісь передавача TX та приймача RX
    tx_y, rx_y = 110, 330
    p.append(text(60, tx_y, "TX (Відправник)", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(60, rx_y, "RX (Одержувач)", size=12, color=INK, bold=True, anchor="end"))

    p.append(line(80, tx_y, 780, tx_y, color=LINE, sw=1.8))
    p.append(line(80, rx_y, 780, rx_y, color=LINE, sw=1.8))
    p.append(arrow(770, tx_y, 800, tx_y, color=LINE, sw=1.8))
    p.append(arrow(770, rx_y, 800, rx_y, color=LINE, sw=1.8))
    p.append(text(805, tx_y + 4, "t", size=12, color=MUTED, italic=True, anchor="start"))
    p.append(text(805, rx_y + 4, "t", size=12, color=MUTED, italic=True, anchor="start"))

    # Пакети: Пакет 1
    s1_x, r1_x = 160, 310
    p.append(circle(s1_x, tx_y, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(circle(r1_x, rx_y, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(arrow(s1_x, tx_y + 5, r1_x, rx_y - 5, color=FIELD, sw=1.8))
    p.append(text(s1_x, tx_y - 12, "S₁ = 0 мс", size=10.5, color=FIELD, bold=True))
    p.append(text(r1_x, rx_y + 18, "R₁ = 30 мс", size=10.5, color=FIELD, bold=True))
    p.append(text(215, 200, "Пакет 1 (затримка 30 мс)", size=10, color=FIELD, italic=True))

    # Пакет 2 (швидкий, затримка 20 мс)
    s2_x, r2_x = 320, 420
    p.append(circle(s2_x, tx_y, 5, fill=NEG, stroke=LINE, sw=1.5))
    p.append(circle(r2_x, rx_y, 5, fill=NEG, stroke=LINE, sw=1.5))
    p.append(arrow(s2_x, tx_y + 5, r2_x, rx_y - 5, color=NEG, sw=1.8))
    p.append(text(s2_x, tx_y - 12, "S₂ = 20 мс", size=10.5, color=NEG, bold=True))
    p.append(text(r2_x, rx_y + 18, "R₂ = 40 мс", size=10.5, color=NEG, bold=True))
    p.append(text(355, 235, "Пакет 2 (затримка 20 мс)", size=10, color=NEG, italic=True))

    # Пакет 3 (затриманий, затримка 55 мс)
    s3_x, r3_x = 480, 710
    p.append(circle(s3_x, tx_y, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(circle(r3_x, rx_y, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(arrow(s3_x, tx_y + 5, r3_x, rx_y - 5, color=POS, sw=1.8))
    p.append(text(s3_x, tx_y - 12, "S₃ = 40 мс", size=10.5, color=POS, bold=True))
    p.append(text(r3_x, rx_y + 18, "R₃ = 95 мс", size=10.5, color=POS, bold=True))
    p.append(text(575, 200, "Пакет 3 (затримка 55 мс - сплеск)", size=10, color=POS, italic=True))

    # Нижня інформаційна панель із розрахунком
    p.append(rect(80, 380, 680, 80, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 402, "Покроковий розрахунок різниці затримок D та оновлення джиттера J:", size=11.5, color=INK, bold=True))
    p.append(text(420, 422, "1 → 2: D(1, 2) = (40 - 20) - (30 - 0) = 20 - 30 = -10 мс  ⇒  |D| = 10 мс  ⇒  J₁ = 0 + (10 - 0)/16 = 0.625 мс", size=10, color=INK))
    p.append(text(420, 442, "2 → 3: D(2, 3) = (95 - 40) - (40 - 20) = 55 - 20 = +35 мс  ⇒  |D| = 35 мс  ⇒  J₂ = 0.625 + (35 - 0.625)/16 ≈ 2.77 мс", size=10, color=INK))

    render(os.path.join(OUT, "jitter-calculation.svg"), W, H, *p)


# ── 4. anti-replay-bitmask: ковзна бітова маска вікна прийому ─────────────────
def fig_anti_replay_bitmask():
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 28, "Ковзна бітова маска захисту від повторів (Anti-Replay Sliding Window)", size=14.5, color=INK, bold=True))
    p.append(text(W / 2, 48, "Розмір вікна W = 64 біти (RFC 4303 IPsec / DTLS). Захист від Replay-атак без зберігання всієї історії", size=11, color=MUTED))

    # Візуалізація бітової маски як низки комірок
    start_x, cell_w, cell_h = 100, 18, 30
    y_cells = 140

    # Заголовок шкали
    p.append(text(start_x, y_cells - 25, "Ліва межа вікна: top_seq - W + 1", size=10.5, color=MUTED, anchor="start"))
    p.append(text(start_x + 35 * cell_w, y_cells - 25, "Права межа: top_seq (найбільший перевірений номер)", size=10.5, color=POS, bold=True, anchor="end"))

    # Малюємо 35 видимих комірок для ілюстрації
    # Нехай top_seq = 100
    # Деякі біти встановлені (зелені), деякі нулі (сірі дірки)
    bits = [1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
    for i, b in enumerate(bits):
        bx = start_x + i * cell_w
        col = "#eafaf1" if b == 1 else "#f8fafc"
        stk = FIELD if b == 1 else "#cbd5e1"
        p.append(rect(bx, y_cells, cell_w, cell_h, fill=col, stroke=stk, sw=1.2, rx=2))
        p.append(text(bx + cell_w / 2, y_cells + 19, str(b), size=10, color=FIELD if b == 1 else MUTED, bold=(b == 1)))

    # Стрілка на top_seq (крайня права клітинка)
    top_x = start_x + (len(bits) - 1) * cell_w + cell_w / 2
    p.append(arrow(top_x, y_cells - 18, top_x, y_cells - 2, color=POS, sw=2))
    p.append(text(top_x, y_cells + cell_h + 16, "top_seq (100)", size=10, color=POS, bold=True))

    # Стрілка на ліву межу
    left_x = start_x + cell_w / 2
    p.append(arrow(left_x, y_cells - 18, left_x, y_cells - 2, color=MUTED, sw=1.5))
    p.append(text(left_x, y_cells + cell_h + 16, "top_seq - 63 (37)", size=10, color=MUTED))

    # Сценарії вхідних номерів:
    # 1. Новий пакет seq > top_seq (наприклад, seq = 103)
    p.append(rect(60, 220, 220, 130, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    p.append(text(170, 245, "Сценарій 1: seq > top_seq", size=11, color=POS, bold=True))
    p.append(text(170, 268, "Новий пакет (seq = 103)", size=10.5, color=INK))
    p.append(text(170, 288, "• Зсув маски вліво на Δ = 3", size=10, color=MUTED))
    p.append(text(170, 306, "• mask = (mask << 3) | 1", size=10, color=MUTED))
    p.append(text(170, 324, "• top_seq = 103 (ПРИЙНЯТО)", size=10, color=POS, bold=True))

    # 2. Пакет усередині вікна (seq = 94, де біт = 0)
    p.append(rect(310, 220, 220, 130, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(420, 245, "Сценарій 2: усередині вікна", size=11, color=FIELD, bold=True))
    p.append(text(420, 268, "Запізнілий пакет (seq = 94)", size=10.5, color=INK))
    p.append(text(420, 288, "• Перевірка біта: (mask >> 6) & 1", size=10, color=MUTED))
    p.append(text(420, 306, "• Біт = 0 → mask |= (1 << 6)", size=10, color=MUTED))
    p.append(text(420, 324, "• Пакет ПРИЙНЯТО (не дубль)", size=10, color=FIELD, bold=True))

    # 3. Повторний або надто старий пакет (seq = 95 або seq < 37)
    p.append(rect(560, 220, 220, 130, fill="#f8fafc", stroke=LINE, sw=1.4, rx=6))
    p.append(text(670, 245, "Сценарій 3: атака повтору", size=11, color=INK, bold=True))
    p.append(text(670, 268, "Дублікат або старий пакет", size=10.5, color=INK))
    p.append(text(670, 288, "• Якщо біт == 1 → ВЖЕ БУВ", size=10, color=POS, bold=True))
    p.append(text(670, 306, "• Якщо seq < 37 → ЗАСТАРІВ", size=10, color=POS, bold=True))
    p.append(text(670, 324, "• ВІДХИЛИТИ БЕЗ ОБРОБКИ", size=10, color=POS, bold=True))

    # Підсумок
    p.append(rect(60, 380, 720, 70, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 405, "Перевага: O(1) за часом та пам'яттю (рівно один 64-бітний або 128-бітний регістр)", size=11, color=INK, bold=True))
    p.append(text(420, 428, "Гарантує захист від Replay-атак при будь-якій кількості легітимно перевпорядкованих пакетів у межах вікна", size=10.5, color=MUTED))

    render(os.path.join(OUT, "anti-replay-bitmask.svg"), W, H, *p)


# ── 5. reorder-buffer-queue: буфер перевпорядкування та видача застосунку ──────
def fig_reorder_buffer():
    W, H = 840, 460
    p = []

    p.append(text(W / 2, 28, "Архітектура буфера перевпорядкування (Reordering Buffer)", size=14.5, color=INK, bold=True))
    p.append(text(W / 2, 48, "Трансформація невпорядкованого UDP/радіо потоку в строго послідовну чергу доставки", size=11, color=MUTED))

    # Схема потоку:
    # Зліва: Невпорядкований потік пакетів
    tb_raw, _, _ = textbox(130, 150, "Вхідний потік з мережі:\n[#12] [#14] [#11] [#15]\n(перевпорядкування,\nвтрати, затримки)", size=10.5, pad=8, fill="#fdecea", stroke=POS, bold=True)
    p.append(tb_raw)

    p.append(arrow(225, 150, 285, 150, color=LINE, sw=2.0))

    # По центру: Кільцевий буфер / Слот-масив
    p.append(rect(290, 90, 270, 220, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    p.append(text(425, 115, "Слоти буфера очікування", size=12, color=INK, bold=True))

    # Комірки всередині буфера
    slots = [
        ("Слот 11", "Пакет #11 (Готовий)", "#eafaf1", FIELD),
        ("Слот 12", "Пакет #12 (Готовий)", "#eafaf1", FIELD),
        ("Слот 13", "ДІРКА (Очікування #13)", "#fef3c7", "#d97706"),
        ("Слот 14", "Пакет #14 (У буфері)", "#eaf0fd", NEG),
        ("Слот 15", "Пакет #15 (У буфері)", "#eaf0fd", NEG),
    ]
    for i, (sl, st, fl, sk) in enumerate(slots):
        sy = 135 + i * 32
        p.append(rect(305, sy, 240, 26, fill=fl, stroke=sk, sw=1.2, rx=4))
        p.append(text(315, sy + 17, sl, size=10, color=INK, bold=True, anchor="start"))
        p.append(text(535, sy + 17, st, size=10, color=sk, bold=True, anchor="end"))

    # Стрілка на видачу
    p.append(arrow(565, 150, 625, 150, color=FIELD, sw=2.2))

    # Справа: Впорядкована черга застосунку
    tb_app, _, _ = textbox(720, 150, "Видача застосунку:\n[#11] → [#12] → (пауза)\nПотік строго за зростанням\nseq_expected = 13", size=10.5, pad=8, fill="#eafaf1", stroke=FIELD, bold=True)
    p.append(tb_app)

    # Нижній блок логіки таймера
    p.append(rect(100, 340, 640, 90, fill="#fffbeb", stroke="#d97706", sw=1.3, rx=6))
    p.append(text(420, 365, "Логіка розблокування дірки (Таймаут перевпорядкування):", size=11.5, color="#b45309", bold=True))
    p.append(text(420, 388, "• Якщо Пакет #13 надходить до спливання таймауту → видати #13, #14, #15 суцільним ланцюжком.", size=10, color=INK))
    p.append(text(420, 408, "• Якщо таймаут сплив (пакет #13 втрачено безповоротно) → зафіксувати втрату, перескочити на seq_exp = 14 і видати #14, #15.", size=10, color=INK))

    render(os.path.join(OUT, "reorder-buffer-queue.svg"), W, H, *p)


if __name__ == "__main__":
    fig_sequence_wrap_around()
    fig_packet_triage()
    fig_jitter_calculation()
    fig_anti_replay_bitmask()
    fig_reorder_buffer()
    print("Figures generated successfully!")
