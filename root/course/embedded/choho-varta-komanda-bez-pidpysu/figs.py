# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Атака повтору (Replay Attack): чому CRC не рятує ───────────────────────
def fig_replay_attack():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 28, "Атака повтору: перехоплення та відтворення валідного кадру", size=16, bold=True))

    # Ліворуч: Пульт / Сервер
    tx_x, tx_y, tx_w, tx_h = 40, 70, 160, 80
    p.append(fitbox(tx_x, tx_y, tx_w, tx_h, "Легітимний пульт\n(Оператор)\nШле: «Відчинити»",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))

    # Праворуч: Виконавець (Ворота / Сервопривід)
    rx_x, rx_y, rx_w, rx_h = 620, 70, 160, 80
    p.append(fitbox(rx_x, rx_y, rx_w, rx_h, "Контролер воріт\n(Привід / Реле)\nПеревіряє: CRC16",
                    size=12, fill=FILL, stroke=LINE, sw=1.8, bold=True))

    # Початкова передача (Фаза 1)
    p.append(arrow(tx_x + tx_w + 4, tx_y + 40, rx_x - 4, rx_y + 40, color=FIELD, sw=2.0))
    p.append(text((tx_x + tx_w + rx_x) / 2, tx_y + 24, "1) Кадр [0x01, 0x2D, CRC=0xA412] (Легітимно)", size=11, color=FIELD, bold=True))

    # Зловмисник посередині (SDR / Сніфер)
    att_x, att_y, att_w, att_h = 290, 180, 240, 75
    p.append(rect(att_x, att_y, att_w, att_h, fill="#fff7f5", stroke=POS, sw=1.8))
    p.append(text(att_x + att_w / 2, att_y + 22, "Зловмисник (SDR-приймач)", size=12, color=POS, bold=True))
    p.append(text(att_x + att_w / 2, att_y + 42, "Записує сирий радіосигнал у пам'ять", size=10.5, color=INK))
    p.append(text(att_x + att_w / 2, att_y + 60, "(Ключа не знає, кадр не дешифрує)", size=10, color=MUTED))

    # Стрілка запису
    p.append(arrow((tx_x + tx_w + rx_x) / 2, tx_y + 45, att_x + att_w / 2, att_y - 4, color=POS, sw=1.6))
    p.append(text(att_x + att_w / 2 + 80, 160, "2) Запис у файл", size=10, color=POS))

    # Фаза 2: Відтворення (Replay) пізніше
    p.append(arrow(att_x + att_w + 4, att_y + 35, rx_x - 4, rx_y + tx_h + 40, color=POS, sw=2.2))
    p.append(text((att_x + att_w + rx_x) / 2 + 10, att_y + 55, "3) Відтворення вночі", size=11, color=POS, bold=True))
    p.append(text((att_x + att_w + rx_x) / 2 + 10, att_y + 72, "той самий [0x01, 0x2D, CRC=0xA412]", size=10, color=POS))

    # Нижня панель висновку
    p.append(fitbox(40, 275, W - 80, 65,
                    "Результат: контролер перевіряє CRC — байти цілі, помилок зв'язку немає. "
                    "Ворота відчиняються для зловмисника, бо кадр НЕ МАЄ доказу свіжості (лічильника/nonce) "
                    "та криптографічного коду автентичності (MAC/підпису).",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.6))
    return render(os.path.join(OUT, "replay-attack.svg"), W, H, *p)


# ── 2. Ковзне вікно валідності (Sliding Replay Window) ─────────────────────────
def fig_sliding_window():
    W, H = 840, 370
    p = []
    p.append(text(W / 2, 28, "Ковзне вікно захисту від повтору (64-бітна бітова маска)", size=16, bold=True))

    # Стрілка числової осі SeqNum угорі
    axis_y = 48
    p.append(line(40, axis_y, 780, axis_y, color=MUTED, sw=1.5))
    p.append(arrow(770, axis_y, 800, axis_y, color=MUTED, sw=1.5))
    p.append(text(805, axis_y + 4, "SeqNum →", size=10, color=MUTED, anchor="start"))

    # Зона застарілих пакетів (ліворуч від вікна)
    p.append(rect(40, 65, 230, 95, fill="#fdecea", stroke=POS, sw=1.4))
    p.append(text(155, 88, "Застарілі пакети (Seq < Max - 63)", size=11, color=POS, bold=True))
    p.append(text(155, 112, "diff >= 64 → ВІДХИЛ", size=11, color=POS, bold=True))
    p.append(text(155, 138, "Діапазон 0 .. 1036", size=10, color=MUTED))

    # Вікно 64 біти (по центру)
    win_x, win_w = 285, 340
    p.append(rect(win_x, 60, win_w, 105, fill="#eafaf0", stroke=FIELD, sw=2.0))
    p.append(text(win_x + win_w / 2, 80, "Ковзне вікно W = 64 біти [Max - 63 .. Max]", size=12, color=FIELD, bold=True))
    p.append(text(win_x + win_w / 2, 98, "Діапазон 1037 .. 1100 (MaxSeq = 1100)", size=10.5, color=INK))

    # Бітова маска комірок усередині вікна
    cell_y = 115
    cell_w, cell_h = 22, 26
    for i in range(12):
        cx = win_x + 16 + i * (cell_w + 2)
        if i in [0, 1, 3, 4, 6, 7, 10, 11]:
            c_fill, c_txt, c_col = "#c8e6c9", "1", FIELD
        else:
            c_fill, c_txt, c_col = "#ffffff", "0", MUTED
        p.append(rect(cx, cell_y, cell_w, cell_h, fill=c_fill, stroke=LINE, sw=1.0))
        p.append(text(cx + cell_w / 2, cell_y + 17, c_txt, size=11, color=c_col, bold=True))

    p.append(text(win_x + 16 + 12 * 24 + 16, cell_y + 17, "...", size=14, color=MUTED, bold=True))

    # Зона нових пакетів (праворуч)
    p.append(rect(640, 65, 160, 95, fill="#eef2fb", stroke=NEG, sw=1.4))
    p.append(text(720, 88, "Майбутні пакети", size=11, color=NEG, bold=True))
    p.append(text(720, 112, "Seq > MaxSeq", size=11, color=NEG, bold=True))
    p.append(text(720, 138, "Зсув маски: << shift", size=10, color=INK))

    # Три сценарії перевірки (нижні картки)
    card_y, card_h = 185, 155
    cw = 240
    # Картка 1: Повтор
    p.append(fitbox(40, card_y, cw, card_h,
                    "Сценарій 1: Повтор\nКадр Seq = 1098 (біт 2 вже 1)\n\n"
                    "• diff = 1100 - 1098 = 2 < 64\n"
                    "• (mask & (1ULL << 2)) != 0\n"
                    "✗ ВІДХИЛЕНО: дублікат!",
                    size=11, fill="#fff7f5", stroke=POS, sw=1.5))

    # Картка 2: Затримка в дорозі (Out-of-order)
    p.append(fitbox(295, card_y, cw, card_h,
                    "Сценарій 2: Запізнілий кадр\nКадр Seq = 1095 (біт 5 був 0)\n\n"
                    "• diff = 1100 - 1095 = 5 < 64\n"
                    "• (mask & (1ULL << 5)) == 0\n"
                    "✓ ПРИЙНЯТО! mask |= (1ULL << 5)",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.5))

    # Картка 3: Новий лідер
    p.append(fitbox(550, card_y, cw, card_h,
                    "Сценарій 3: Новий лідер\nКадр Seq = 1104 (> 1100)\n\n"
                    "• shift = 1104 - 1100 = 4\n"
                    "• mask = (mask << 4) | 1ULL\n"
                    "• MaxSeq = 1104. ✓ ПРИЙНЯТО!",
                    size=11, fill="#eef2fb", stroke=NEG, sw=1.5))

    return render(os.path.join(OUT, "sliding-window.svg"), W, H, *p)


# ── 3. Симетрична автентифікація vs Асиметричний підпис ────────────────────────
def fig_auth_comparison():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 28, "Порівняння: Симетричний MAC vs Асиметричний цифровий підпис", size=16, bold=True))

    # Ліва колонка: Симетричний MAC
    lx, ly, lw, lh = 40, 65, 360, 300
    p.append(rect(lx, ly, lw, lh, fill="#fcfcfd", stroke=LINE, sw=1.5))
    p.append(text(lx + lw / 2, ly + 24, "Симетричний MAC (HMAC / AES-GMAC / Poly1305)", size=12.5, color=FIELD, bold=True))

    mac_items = [
        ("Секрет", "Спільний ключ K у пульта і в мікроконтролера"),
        ("Швидкість", "10 – 80 мкс на Cortex-M4 (дуже швидко)"),
        ("Розмір тегу", "8 – 16 байтів (HMAC) або 16 байтів (GMAC/Poly)"),
        ("Вразливість", "Злам одного чипа розкриває ключ для всіх!"),
        ("Призначення", "Високочастотне керування (мотори, телеметрія)"),
    ]
    for i, (k, v) in enumerate(mac_items):
        yy = ly + 55 + i * 46
        p.append(text(lx + 16, yy, k + ":", size=11, color=FIELD, bold=True, anchor="start"))
        p.append(fitbox(lx + 16, yy + 4, lw - 32, 24, v, size=10, fill="#f4f6f8", stroke=LINE, sw=0.8, anchor="start"))

    # Права колонка: Асиметричний підпис
    rx, ry, rw, rh = 440, 65, 360, 300
    p.append(rect(rx, ry, rw, rh, fill="#fcfcfd", stroke=LINE, sw=1.5))
    p.append(text(rx + rw / 2, ry + 24, "Асиметричний підпис (Ed25519 / ECDSA)", size=12.5, color=NEG, bold=True))

    sig_items = [
        ("Секрет", "Приватний SK — на сервері, відкритий PK — у чипі"),
        ("Швидкість", "3 – 40 мс на Cortex-M4 (у 500–1000 разів довше)"),
        ("Розмір підпису", "64 байти (Ed25519) або 64 байти (ECDSA P-256)"),
        ("Безпека", "Вичитка Flash дає лише PK — підробити команду годі!"),
        ("Призначення", "Оновлення прошивки (OTA), конфігурація, зміна сесії"),
    ]
    for i, (k, v) in enumerate(sig_items):
        yy = ry + 55 + i * 46
        p.append(text(rx + 16, yy, k + ":", size=11, color=NEG, bold=True, anchor="start"))
        p.append(fitbox(rx + 16, yy + 4, rw - 32, 24, v, size=10, fill="#f4f6f8", stroke=LINE, sw=0.8, anchor="start"))

    return render(os.path.join(OUT, "auth-comparison.svg"), W, H, *p)


# ── 4. Структура захищеного бінарного кадру ────────────────────────────────────
def fig_secure_frame_structure():
    W, H = 840, 340
    p = []
    p.append(text(W / 2, 28, "Формат захищеного бінарного кадру керування", size=16, bold=True))

    fx, fy = 40, 75
    fields = [
        ("Magic", "2 Б", "0xA55A", "#eef2fb", NEG, 70),
        ("Ver / ID", "2 Б", "Type/Cmd", "#eef2fb", NEG, 80),
        ("SeqNum", "8 Б", "Лічильник", "#eafaf0", FIELD, 120),
        ("Timestamp", "4 Б", "UTC час", "#eafaf0", FIELD, 100),
        ("Len", "2 Б", "Довжина N", "#f4f6f8", LINE, 80),
        ("Payload", "N Б", "Дані команди (кут, швидкість, реле)", "#f4f6f8", LINE, 200),
        ("Auth Tag", "16 / 64 Б", "HMAC / Ed25519", "#fff7f5", POS, 110),
    ]

    cur_x = fx
    for name, sz, desc, fill_c, strk_c, f_w in fields:
        p.append(rect(cur_x, fy, f_w, 65, fill=fill_c, stroke=strk_c, sw=1.6))
        p.append(text(cur_x + f_w / 2, fy + 22, name, size=11.5, color=strk_c, bold=True))
        p.append(text(cur_x + f_w / 2, fy + 40, sz, size=10, color=MUTED))
        p.append(text(cur_x + f_w / 2, fy + 56, desc, size=9.5, color=INK))
        cur_x += f_w

    # Фігурна дужка автентифікації: від Magic до кінця Payload
    auth_w = (cur_x - 110) - fx
    p.append(line(fx, fy + 80, fx + auth_w, fy + 80, color=POS, sw=2.0))
    p.append(line(fx, fy + 75, fx, fy + 85, color=POS, sw=2.0))
    p.append(line(fx + auth_w, fy + 75, fx + auth_w, fy + 85, color=POS, sw=2.0))
    p.append(arrow(fx + auth_w / 2, fy + 80, fx + auth_w / 2, fy + 105, color=POS, sw=1.8))
    p.append(text(fx + auth_w / 2, fy + 120, "Дані, що покриваються криптографічним кодом (AAD / Signed Message)", size=11, color=POS, bold=True))

    # Стрілка тегу
    p.append(arrow(fx + auth_w + 55, fy + 105, fx + auth_w + 55, fy + 70, color=POS, sw=1.8))
    p.append(text(fx + auth_w + 55, fy + 120, "Тег обчислюється над цим діапазоном", size=10, color=POS))

    # Пояснення захисту полів
    p.append(fitbox(40, 220, W - 80, 95,
                    "Ключові властивості полів:\n"
                    "• SeqNum (64 біти) унеможливлює атаку повтору (переповниться лише через 584 роки при 1 млрд пакетів/с).\n"
                    "• Timestamp (32 біти) обмежує часове вікно валідності кадру при відомому часі RTC/GNSS.\n"
                    "• Auth Tag захищає весь заголовок і корисне навантаження: зміна бодай одного біта робить тег невалідним.",
                    size=11, fill="#fcfcfd", stroke=LINE, sw=1.2))

    return render(os.path.join(OUT, "secure-frame-structure.svg"), W, H, *p)


# ── 5. Конвеєр верифікації та захист від атак за часом (Constant-Time) ─────────
def fig_verification_pipeline():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 28, "Конвеєр безпечної обробки вхідного кадру керування", size=16, bold=True))

    steps = [
        ("1. Парсинг заголовка", "Magic, довжина\nперевірка меж буфера", "#f4f6f8", LINE),
        ("2. Звірка тегу (MAC)", "crypto_verify()\nКонстантний час!", "#fff7f5", POS),
        ("3. Часове вікно", "|T_cmd - T_loc| <= Δt\nПеревірка за RTC", "#eef2fb", NEG),
        ("4. Захист від повтору", "Ковзне вікно 64 біти\nПеревірка й зсув", "#eafaf0", FIELD),
        ("5. Виконання", "Диспетчеризація\nрух, реле, привід", "#eafaf0", FIELD),
    ]

    bx, by, bw, bh, gap = 40, 75, 136, 85, 20
    for i, (title_s, desc_s, fill_c, strk_c) in enumerate(steps):
        x = bx + i * (bw + gap)
        p.append(fitbox(x, by, bw, bh, title_s + "\n" + desc_s, size=11, fill=fill_c, stroke=strk_c, sw=1.8, bold=True))
        if i < len(steps) - 1:
            ax1, ax2 = x + bw, x + bw + gap
            p.append(arrow(ax1 + 2, by + bh / 2, ax2 - 2, by + bh / 2, color=LINE, sw=1.8))

    # Стрілки скидання при помилці
    for i in range(4):
        x = bx + i * (bw + gap) + bw / 2
        p.append(arrow(x, by + bh + 4, x, by + bh + 45, color=POS, sw=1.5))
        p.append(text(x, by + bh + 58, "✗ Відхил", size=9.5, color=POS, bold=True))

    p.append(line(bx + bw / 2, by + bh + 45, bx + 3 * (bw + gap) + bw / 2, by + bh + 45, color=POS, sw=1.4, dash="3 3"))

    # Пояснювальний блок
    p.append(fitbox(40, 240, W - 80, 95,
                    "Залізне правило безпеки: НІКОЛИ не виконувати бізнес-логіку до кроку 4!\n"
                    "• Крок 2 виконується виключно в константному часі (constant_time_memcmp), щоб унеможливити side-channel атаки за часом виконання.\n"
                    "• Оновлення стану лічильника (Крок 4) відбувається ЛИШЕ після успішної автентифікації, щоб зловмисник не міг зіпсувати стан вікна сміттєвими пакетами.",
                    size=11, fill="#fcfcfd", stroke=LINE, sw=1.2))

    return render(os.path.join(OUT, "verification-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_replay_attack()
    fig_sliding_window()
    fig_auth_comparison()
    fig_secure_frame_structure()
    fig_verification_pipeline()
    print("Figures generated successfully in", OUT)
