# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. puncturing-concept.svg: Загальний принцип виколювання ──────────────────
def fig_concept():
    W, H = 820, 360
    p = [
        text(W / 2, 28, "Принцип виколювання (puncturing) у системі зв'язку", size=17, bold=True),
        text(W / 2, 50, "Один материнський декодер обслуговує різні швидкості кодування за допомогою вставляння стирань", size=12.5, color=MUTED, italic=True)
    ]

    # Схема блоків
    # 1. Вхідні дані u
    p.append(text(50, 140, "Дані u", size=13, bold=True, color=INK, anchor="start"))
    p.append(arrow(100, 140, 140, 140, sw=2, color=LINE))

    # 2. Материнський кодер R0 = 1/2
    b1 = fitbox(140, 105, 140, 70, ["Материнський", "кодер R₀ = 1/2"], fill="#e8eefc", stroke=FIELD, sw=2, size=12.5)
    p.append(b1)
    p.append(text(295, 125, "Повний потік [v₁, v₂]", size=11, color=MUTED))
    p.append(arrow(280, 140, 320, 140, sw=2, color=LINE))

    # 3. Блок виколювання (матриця P)
    b2 = fitbox(320, 105, 140, 70, ["Блок виколювання", "(матриця P)"], fill="#fdecea", stroke=POS, sw=2, size=12.5)
    p.append(b2)
    p.append(text(390, 195, "Вилучення бітів 0", size=11, color=POS, bold=True))
    p.append(text(480, 125, "Виколотий потік (R = 2/3)", size=11, color=MUTED))
    p.append(arrow(460, 140, 500, 140, sw=2, color=LINE))

    # 4. Канал зв'язку
    p.append(rect(500, 115, 70, 50, fill="#fff5e6", stroke="#e08a1e", sw=1.5, rx=5))
    p.append(text(535, 145, "Канал", size=12.5, bold=True, color="#a8620a"))
    p.append(arrow(570, 140, 610, 140, sw=2, color=LINE))

    # 5. Приймач: вставляння стирань (LLR = 0)
    p.append(text(620, 90, "Приймач", size=14, bold=True, color=INK, anchor="start"))
    b3 = fitbox(610, 105, 140, 70, ["Вставляння стирань", "LLR = 0 на місця '0'"], fill="#eafaf0", stroke=FIELD, sw=2, size=12.5)
    p.append(b3)

    # Текст збоку від стрічки, щоб стрічка його не перетинала!
    p.append(text(760, 210, "Відновлений потік", size=11, color=FIELD, bold=True, anchor="start"))

    # Стрілка від стирань до материнського декодера
    p.append(arrow(680, 175, 680, 245, sw=2, color=LINE))

    # 6. Материнський декодер R0 = 1/2
    b4 = fitbox(610, 245, 140, 70, ["Материнський", "декодер R₀ = 1/2"], fill="#e8eefc", stroke=FIELD, sw=2, size=12.5)
    p.append(b4)

    # Вихід
    p.append(arrow(610, 280, 540, 280, sw=2, color=LINE))
    p.append(text(530, 285, "Оцінка даних û", size=13, bold=True, color=INK, anchor="end"))

    # Пояснювальна примітка внизу
    p.append(text(W / 2, 340, "Завдяки вставлянню LLR = 0 структура ґратки декодера залишається незмінною", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "puncturing-concept.svg"), W, H, *p)


# ── 2. rate-ladder.svg: Візерунки виколювання та швидкості ────────────────────
def fig_rate_ladder():
    W, H = 840, 420
    p = [
        text(W / 2, 28, "Драбина швидкостей виколювання для материнського коду R₀ = 1/2", size=17, bold=True),
        text(W / 2, 50, "Період виколювання p = 3: з 6 вихідних бітів кодера передається 6, 4 або 3 біти", size=12.5, color=MUTED, italic=True)
    ]

    Y0 = 90

    # Заголовки тактів
    p.append(text(140, Y0 + 20, "Вхідні біти u", size=13, bold=True, color=INK, anchor="end"))
    for i in range(3):
        x = 160 + i * 220
        p.append(rect(x, Y0, 200, 32, fill="#f2f3f5", stroke="#cccccc", rx=4))
        p.append(text(x + 100, Y0 + 21, f"Такт {i+1}: u{i+1}", size=13, bold=True, color=INK))

    # Рядок 1: Материнський код R = 1/2 (Всі біти 1 1 1 1 1 1)
    y1 = Y0 + 55
    p.append(text(140, y1 + 20, "R = 1/2 (Материнський)", size=12, bold=True, color=FIELD, anchor="end"))
    p.append(text(140, y1 + 36, "Передається 6/6 бітів", size=10.5, color=MUTED, anchor="end"))
    for i in range(3):
        x = 160 + i * 220
        p.append(rect(x, y1, 95, 40, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
        p.append(text(x + 47, y1 + 25, f"v1,{i+1} (1)", size=12, bold=True, color=FIELD))
        p.append(rect(x + 105, y1, 95, 40, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
        p.append(text(x + 152, y1 + 25, f"v2,{i+1} (1)", size=12, bold=True, color=FIELD))

    # Рядок 2: Виколотий код R = 2/3 (Період p=2, матриця [1 1; 1 0], виколото кожен 4-й)
    y2 = y1 + 90
    p.append(text(140, y2 + 20, "R = 2/3 (Період p=2)", size=12, bold=True, color=INK, anchor="end"))
    p.append(text(140, y2 + 36, "Матриця P = [1 1; 1 0]", size=10.5, color=MUTED, anchor="end"))
    pattern_23 = [
        (True, "v1,1"), (True, "v2,1"),
        (True, "v1,2"), (False, "v2,2 ✂"),
        (True, "v1,3"), (True, "v2,3")
    ]
    idx = 0
    for i in range(3):
        x = 160 + i * 220
        for b in range(2):
            keep, label = pattern_23[idx]
            bx = x + b * 105
            fill = "#eafaf0" if keep else "#fdecea"
            stroke = FIELD if keep else POS
            txt_col = FIELD if keep else POS
            p.append(rect(bx, y2, 95, 40, fill=fill, stroke=stroke, sw=1.5, rx=4))
            p.append(text(bx + 47, y2 + 25, label, size=12, bold=True, color=txt_col))
            idx += 1

    # Рядок 3: Виколотий код R = 3/4 (Період p=3, матриця P = [1 1 0; 1 0 1])
    y3 = y2 + 90
    p.append(text(140, y3 + 20, "R = 3/4 (Період p=3)", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(140, y3 + 36, "Матриця P = [1 1 0; 1 0 1]", size=10.5, color=MUTED, anchor="end"))
    pattern_34 = [
        (True, "v1,1"), (True, "v2,1"),
        (True, "v1,2"), (False, "v2,2 ✂"),
        (False, "v1,3 ✂"), (True, "v2,3")
    ]
    idx = 0
    for i in range(3):
        x = 160 + i * 220
        for b in range(2):
            keep, label = pattern_34[idx]
            bx = x + b * 105
            fill = "#eafaf0" if keep else "#fdecea"
            stroke = FIELD if keep else POS
            txt_col = FIELD if keep else POS
            p.append(rect(bx, y3, 95, 40, fill=fill, stroke=stroke, sw=1.5, rx=4))
            p.append(text(bx + 47, y3 + 25, label, size=12, bold=True, color=txt_col))
            idx += 1

    # Легенда
    p.append(text(W / 2, H - 25, "Зелений: збережений і переданий біт (1 у матриці P)   ·   Червоний: виколотий біт (0 у матриці P, вставляється LLR=0)", size=11.5, color=MUTED))

    render(os.path.join(OUT, "rate-ladder.svg"), W, H, *p)


# ── 3. harq-ir.svg: IR-HARQ та покрокова передача надлишковості ───────────────
def fig_harq_ir():
    W, H = 820, 440
    p = [
        text(W / 2, 28, "Протокол IR-HARQ (Incremental Redundancy HARQ)", size=17, bold=True),
        text(W / 2, 50, "Адаптивне досилання виколотих бітів парності при помилках приймача", size=12.5, color=MUTED, italic=True)
    ]

    # Передавач (Tx) зліва, Приймач (Rx) праворуч
    X_TX = 180
    X_RX = 640

    p.append(text(X_TX, 90, "Передавач (Tx)", size=14, bold=True, color=INK))
    p.append(text(X_RX, 90, "Приймач (Rx)", size=14, bold=True, color=INK))
    p.append(line(X_TX, 105, X_TX, 370, color="#cccccc", sw=1.5, dash="4 4"))
    p.append(line(X_RX, 105, X_RX, 370, color="#cccccc", sw=1.5, dash="4 4"))

    # Етап 1: Перша спроба (R = 3/4)
    y1 = 130
    p.append(text(X_TX - 10, y1 + 15, "1. Спроба (R = 3/4)", size=12, bold=True, color=INK, anchor="end"))
    p.append(arrow(X_TX, y1 + 15, X_RX - 10, y1 + 15, sw=2, color=FIELD))
    p.append(text((X_TX + X_RX) / 2, y1 - 5, "Блок з виколюванням P₁ (4 біти з 6)", size=11.5, color=FIELD, bold=True))

    p.append(text(X_RX + 15, y1 + 15, "Декодування R=3/4", size=12, color=INK, anchor="start"))
    p.append(text(X_RX + 15, y1 + 32, "CRC: Помилка ✗", size=12, bold=True, color=POS, anchor="start"))

    # Відповідь NACK
    y2 = y1 + 55
    p.append(arrow(X_RX - 10, y2 + 15, X_TX + 10, y2 + 15, sw=2, color=POS))
    p.append(text((X_TX + X_RX) / 2, y2 - 5, "Сигнал NACK (потрібна надлишковість)", size=11.5, color=POS, bold=True))

    # Етап 2: Досилання виколотих бітів (Incremental Redundancy)
    y3 = y2 + 65
    p.append(text(X_TX - 10, y3 + 15, "2. Досилання ΔP", size=12, bold=True, color=INK, anchor="end"))
    p.append(arrow(X_TX, y3 + 15, X_RX - 10, y3 + 15, sw=2, color="#e08a1e"))
    p.append(text((X_TX + X_RX) / 2, y3 - 5, "Досилання раніше виколотих бітів ΔP (2 біти)", size=11.5, color="#a8620a", bold=True))

    p.append(text(X_RX + 15, y3 + 10, "Об'єднання вибірок", size=11.5, color=INK, anchor="start"))
    p.append(text(X_RX + 15, y3 + 28, "Декодування R=1/2", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(X_RX + 15, y3 + 46, "CRC: Успіх ✓", size=12, bold=True, color=FIELD, anchor="start"))

    # Відповідь ACK
    y4 = y3 + 65
    p.append(arrow(X_RX - 10, y4 + 15, X_TX + 10, y4 + 15, sw=2, color=FIELD))
    p.append(text((X_TX + X_RX) / 2, y4 - 5, "Сигнал ACK (підтвердження)", size=11.5, color=FIELD, bold=True))

    # Підсумок внизу
    p.append(text(W / 2, H - 25, "Приймач зберігає м'які вибірки LLR від 1-ї спроби та об'єднує їх з досланими бітами", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "harq-ir.svg"), W, H, *p)


# ── 4. ber-tradeoff.svg: Криві BER та компроміс потужності ────────────────────
def fig_ber_tradeoff():
    W, H = 760, 480
    p = [
        text(W / 2, 28, "Криві BER для виколотих кодів (компроміс швидкість / SNR)", size=17, bold=True),
        text(W / 2, 50, "Підвищення швидкості R зменшує d_free і вимагає більшого E_b/N_0 для тієї ж надійності", size=12.5, color=MUTED, italic=True)
    ]

    # Графік: Вісь X (Eb/N0, dB), Вісь Y (log10 BER)
    X0 = 120
    Y0 = 380
    GX_W = 560
    GY_H = 280

    # Осі
    p.append(arrow(X0, Y0, X0 + GX_W + 30, Y0, sw=2, color=LINE))
    p.append(arrow(X0, Y0, X0, Y0 - GY_H - 20, sw=2, color=LINE))

    p.append(text(X0 + GX_W / 2, Y0 + 45, "Відношення сигнал/шум E_b/N_0 (дБ)", size=13, bold=True, color=INK))
    p.append(mtext(45, Y0 - GY_H / 2, ["Ймовірність", "помилки BER"], size=13, bold=True, color=INK))

    # Засічки на осі Y (10^-1 ... 10^-6)
    ber_labels = ["10⁻¹", "10⁻²", "10⁻³", "10⁻⁴", "10⁻⁵", "10⁻⁶"]
    for i, lbl in enumerate(ber_labels):
        y = Y0 - (i + 1) * (GY_H / 6)
        p.append(line(X0 - 5, y, X0, y, color=LINE, sw=1.5))
        p.append(line(X0, y, X0 + GX_W, y, color="#e5e5e5", sw=1, dash="2 4"))
        p.append(text(X0 - 15, y + 4, lbl, size=11, color=MUTED, anchor="end"))

    # Засічки на осі X (1 дБ ... 7 дБ)
    for db in range(1, 8):
        x = X0 + db * (GX_W / 7)
        p.append(line(x, Y0, x, Y0 + 5, color=LINE, sw=1.5))
        p.append(text(x, Y0 + 22, f"{db} дБ", size=11, color=MUTED))

    # Крива R = 1/2 (Материнський code): водоспад біля 2.5 дБ
    pts_r12 = [(1, 1), (1.8, 2), (2.4, 3), (2.9, 4), (3.3, 5), (3.7, 6)]
    path_r12 = []
    for db, b_idx in pts_r12:
        px = X0 + db * (GX_W / 7)
        py = Y0 - b_idx * (GY_H / 6)
        path_r12.append(f"{px:.1f},{py:.1f}")
    p.append(f'<path d="M ' + ' L '.join(path_r12) + f'" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    # Крива R = 2/3: зсунута праворуч на ~1.2 дБ
    pts_r23 = [(1.5, 1), (2.6, 2), (3.4, 3), (4.1, 4), (4.7, 5), (5.2, 6)]
    path_r23 = []
    for db, b_idx in pts_r23:
        px = X0 + db * (GX_W / 7)
        py = Y0 - b_idx * (GY_H / 6)
        path_r23.append(f"{px:.1f},{py:.1f}")
    p.append(f'<path d="M ' + ' L '.join(path_r23) + f'" fill="none" stroke="#e08a1e" stroke-width="3"/>')

    # Крива R = 3/4: зсунута праворуч на ~2.2 дБ
    pts_r34 = [(2.2, 1), (3.4, 2), (4.4, 3), (5.2, 4), (5.9, 5), (6.5, 6)]
    path_r34 = []
    for db, b_idx in pts_r34:
        px = X0 + db * (GX_W / 7)
        py = Y0 - b_idx * (GY_H / 6)
        path_r34.append(f"{px:.1f},{py:.1f}")
    p.append(f'<path d="M ' + ' L '.join(path_r34) + f'" fill="none" stroke="{POS}" stroke-width="3"/>')

    # Написи до кривих у чистому місці угорі
    p.append(text(X0 + 10, Y0 - GY_H + 20, "R = 1/2 (d_free = 5)", size=11.5, bold=True, color=FIELD, anchor="start"))
    p.append(text(X0 + 160, Y0 - GY_H + 20, "R = 2/3 (d_free = 3)", size=11.5, bold=True, color="#a8620a", anchor="start"))
    p.append(text(X0 + 310, Y0 - GY_H + 20, "R = 3/4 (d_free = 3)", size=11.5, bold=True, color=POS, anchor="start"))

    # Енергетичний штраф (ΔSNR при BER = 10^-5)
    y_target = Y0 - 5 * (GY_H / 6)
    x_r12 = X0 + 3.3 * (GX_W / 7)
    x_r34 = X0 + 5.9 * (GX_W / 7)
    p.append(line(x_r12, y_target, x_r34, y_target, color=INK, sw=1.5, dash="3 3"))
    p.append(text((x_r12 + x_r34) / 2, y_target - 12, "Втрата ~2.6 дБ ради вищої швидкості", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "ber-tradeoff.svg"), W, H, *p)


if __name__ == "__main__":
    fig_concept()
    fig_rate_ladder()
    fig_harq_ir()
    fig_ber_tradeoff()
    print("OK: generated 4 figures in img/")
