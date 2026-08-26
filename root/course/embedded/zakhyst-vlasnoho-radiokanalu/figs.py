# -*- coding: utf-8 -*-
"""Фігури до теми «Захист власного радіоканалу: ключ, лічильник, тег».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"   # попередження, увага, теги


# ── 1. Модель загроз у відкритому радіоефірі ──────────────────────────────────
def fig_threat_model_radio():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Модель загроз відкритого радіоефіру: три вектори атаки", size=18, bold=True),
        text(W / 2, 50, "радіохвилі доступні кожному в зоні досяжності; дріт не захищає, контрольна сума (CRC) не рятує",
             size=11.5, color=MUTED, italic=True)
    ]

    # Легітимний відправник (Node A)
    f.append(rect(40, 90, 190, 130, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    f.append(text(135, 118, "Вузол A (Передавач)", size=13, color=FIELD, bold=True))
    f.append(text(135, 140, "Пульт / Сенсор", size=10.5, color=MUTED))
    f.append(line(70, 160, 200, 160, color=MUTED, sw=1))
    f.append(text(135, 180, "tx_cmd = MOTOR_ON", size=10, color=INK, bold=True))
    f.append(text(135, 200, "антена випромінює в ефір", size=9.5, color=MUTED))

    # Легітимний отримувач (Node B)
    f.append(rect(710, 90, 190, 130, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    f.append(text(805, 118, "Вузол B (Приймач)", size=13, color=FIELD, bold=True))
    f.append(text(805, 140, "Дрон / Контролер", size=10.5, color=MUTED))
    f.append(line(740, 160, 870, 160, color=MUTED, sw=1))
    f.append(text(805, 180, "rx_exec(cmd)", size=10, color=INK, bold=True))
    f.append(text(805, 200, "виконує прийняту дію", size=9.5, color=MUTED))

    # Прямий зв'язок (радіохвилі)
    f.append(line(230, 155, 710, 155, color=FIELD, sw=2, dash="6,4"))
    f.append(text(470, 142, "відкритий радіоканал (2.4 ГГц / 868 МГц)", size=11, color=FIELD, bold=True))

    # Зловмисник посередині (Attacker)
    f.append(rect(340, 205, 260, 80, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    f.append(text(470, 228, "Зловмисник (SDR / трансивер)", size=12.5, color=POS, bold=True))
    f.append(text(470, 248, "пасивний слухач або активний інжектор", size=9.5, color=MUTED))
    f.append(text(470, 268, "перехоплює 100% пакетів", size=9.5, color=POS))

    # Три вектори атак (картки знизу)
    card_w = 266
    cards = [
        ("1. Прослуховування (Eavesdropping)",
         ["Пасивне перехоплення відкритих даних", "Витік координат, телеметрії, ключів", "Ліки: автентифіковане шифрування"],
         POS),
        ("2. Підміна та інжекція (Tampering)",
         ["Модифікація бітів у польоті (bit-flipping)", "Фальшиві команди (CRC перераховується!)", "Ліки: автентифікаційний тег (MAC)"],
         POS),
        ("3. Повтор (Replay Attack)",
         ["Запис валідного зашифрованого кадру", "Повторна відправка через N хвилин", "Ліки: монотонний Nonce + Anti-Replay"],
         POS)
    ]

    for i, (title, bullets, accent) in enumerate(cards):
        cx = 40 + i * (card_w + 31)
        f.append(rect(cx, 310, card_w, 130, fill="#ffffff", stroke=accent, sw=1.6, rx=6))
        f.append(text(cx + card_w / 2, 332, title, size=11, color=accent, bold=True))
        by = 358
        for b in bullets:
            f.append(text(cx + 12, by, "•", size=11, color=accent, anchor="start", bold=True))
            f.append(text(cx + 24, by, b, size=9.6, color=INK, anchor="start"))
            by += 24

    return render(os.path.join(IMG, 'threat-model-radio.svg'), W, H, *f)


# ── 2. Анатомія захищеного AEAD-кадру ──────────────────────────────────────────
def fig_aead_frame_layout():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Структура захищеного радіокадру: AAD, шифротекст і тег", size=18, bold=True),
        text(W / 2, 50, "заголовок передається відкритим для маршрутизації, але криптографічно захищений тегом разом із тілом",
             size=11.5, color=MUTED, italic=True)
    ]

    # Повна смуга кадру
    y0 = 90
    h_bar = 65

    # Фізичний рівень (преамбула + sync)
    f.append(rect(40, y0, 110, h_bar, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=4))
    f.append(text(95, y0 + 26, "Preamble + Sync", size=10.5, color=MUTED, bold=True))
    f.append(text(95, y0 + 46, "Фізичний рівень", size=9, color=MUTED))

    # AAD: Заголовок кадру
    f.append(rect(155, y0, 315, h_bar, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
    f.append(text(312, y0 + 24, "Відкритий заголовок (AAD — Associated Data)", size=11.5, color=NEG, bold=True))
    f.append(text(312, y0 + 46, "Proto (1B) | Flags (1B) | Src (2B) | Dst (2B) | Seq/Counter (4B)", size=9.5, color=INK))

    # Шифротекст корисного навантаження (Ciphertext)
    f.append(rect(475, y0, 260, h_bar, fill="#eef6ef", stroke=FIELD, sw=2, rx=4))
    f.append(text(605, y0 + 24, "Зашифровані дані (Ciphertext)", size=11.5, color=FIELD, bold=True))
    f.append(text(605, y0 + 46, "Payload = Plaintext ⊕ Keystream (N байтів)", size=9.5, color=INK))

    # Автентифікаційний тег (Auth Tag / MAC)
    f.append(rect(740, y0, 160, h_bar, fill="#fdf6e7", stroke=GOLD, sw=2, rx=4))
    f.append(text(820, y0 + 24, "Тег автентичності", size=11.5, color=GOLD, bold=True))
    f.append(text(820, y0 + 46, "Tag (16B Poly1305 / CCM)", size=9.5, color=INK))

    # Фігурні дужки / зони захисту
    # Зона відкритості
    f.append(line(155, y0 + h_bar + 15, 470, y0 + h_bar + 15, color=NEG, sw=1.8))
    f.append(text(312, y0 + h_bar + 32, "Відкритий текст (видно в ефірі для швидкої фільтрації)", size=10, color=NEG))

    # Зона шифрування
    f.append(line(475, y0 + h_bar + 15, 735, y0 + h_bar + 15, color=FIELD, sw=1.8))
    f.append(text(605, y0 + h_bar + 32, "Зашифровано (конфіденційність)", size=10, color=FIELD))

    # Зона захисту автентичністю (охоплює AAD + Ciphertext)
    f.append(line(155, y0 + h_bar + 55, 735, y0 + h_bar + 55, color=GOLD, sw=2.2))
    f.append(line(155, y0 + h_bar + 50, 155, y0 + h_bar + 60, color=GOLD, sw=2.2))
    f.append(line(735, y0 + h_bar + 50, 735, y0 + h_bar + 60, color=GOLD, sw=2.2))
    f.append(arrow(445, y0 + h_bar + 55, 740, y0 + h_bar + 10, color=GOLD, sw=2))
    f.append(text(445, y0 + h_bar + 75, "Вхід AEAD-автентифікації: MAC обчислюється над (AAD + Ciphertext)", size=11, color=GOLD, bold=True))

    # Нижня частина: формування Nonce та криптографічне ядро
    box_y = 260
    f.append(rect(40, box_y, 410, 195, fill="#fafbfc", stroke=NEG, sw=1.5, rx=8))
    f.append(text(245, box_y + 24, "Конструкція 12-байтного Nonce (Одноразового числа)", size=11.5, color=NEG, bold=True))
    f.append(text(60, box_y + 54, "• Src ID (2B):", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(160, box_y + 54, "унікальний ідентифікатор передавача", size=10, color=MUTED, anchor="start"))
    f.append(text(60, box_y + 80, "• Dst ID (2B):", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(160, box_y + 80, "ідентифікатор цільового вузла", size=10, color=MUTED, anchor="start"))
    f.append(text(60, box_y + 106, "• Epoch (4B):", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(160, box_y + 106, "номер сесії після перезавантаження МК", size=10, color=MUTED, anchor="start"))
    f.append(text(60, box_y + 132, "• Counter (4B):", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(160, box_y + 132, "монотонний лічильник пакета в сесії", size=10, color=MUTED, anchor="start"))
    f.append(text(245, box_y + 172, "Ключове правило: пара (Ключ, Nonce) НІКОЛИ не повторюється!", size=9.8, color=POS, bold=True))

    # Права картка: чому AAD відкритий
    f.append(rect(480, box_y, 420, 195, fill="#fafbfc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(690, box_y + 24, "Чому AAD передається відкритим, а не шифрується", size=11.5, color=FIELD, bold=True))
    f.append(text(500, box_y + 56, "1. Апаратна / швидка фільтрація:", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(516, box_y + 78, "Приймач відкидає чужі Dst ID до важкого AEAD.", size=9.8, color=MUTED, anchor="start"))
    f.append(text(500, box_y + 106, "2. Захист від відмови в обслуговуванні (DoS):", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(516, box_y + 128, "Старий Sequence Counter відсікається без криптографії.", size=9.8, color=MUTED, anchor="start"))
    f.append(text(500, box_y + 156, "3. Неможливість підміни:", size=10.5, color=INK, anchor="start", bold=True))
    f.append(text(516, box_y + 178, "Зміна хоч одного біта AAD ламає тег → пакет дропається.", size=9.8, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'aead-frame-layout.svg'), W, H, *f)


# ── 3. Вікно захисту від Replay (Anti-Replay Sliding Window) ───────────────────
def fig_anti_replay_window():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Ковзне вікно Anti-Replay: обробка затримок і блокування повторів", size=18, bold=True),
        text(W / 2, 50, "ефір переставляє пакети місцями; вікно з бітовою маскою розрізняє запізнілі пакети та атаки повтору",
             size=11.5, color=MUTED, italic=True)
    ]

    # Вісь номерів послідовності (Sequence Numbers)
    ax_y = 150
    f.append(line(60, ax_y, 880, ax_y, color=INK, sw=2.5))
    f.append(arrow(870, ax_y, 890, ax_y, color=INK, sw=2.5))
    f.append(text(880, ax_y - 14, "Seq Counter", size=10.5, color=INK, bold=True))

    # Зона 1: Застарілі пакети (Ліворуч)
    f.append(rect(70, 80, 230, 140, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    f.append(text(185, 104, "Зона 1: Застарілі (Seq ≤ last - W)", size=11, color=POS, bold=True))
    f.append(text(185, 126, "seq < 937", size=11, color=INK, bold=True))
    f.append(text(185, 172, "АВТОМАТИЧНИЙ DROP", size=10, color=POS, bold=True))
    f.append(text(185, 192, "без виклику криптографії", size=9.5, color=MUTED))

    # Зона 2: Вікно ковзання (Посередині)
    f.append(rect(320, 70, 310, 160, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    f.append(text(475, 96, "Зона 2: Вікно ковзання (W = 64)", size=12, color=NEG, bold=True))
    f.append(text(475, 118, "937 ≤ seq ≤ 1000", size=11, color=INK, bold=True))

    # Бітова маска всередині зони 2
    bits_y = ax_y
    f.append(text(340, bits_y - 8, "[937]", size=9, color=MUTED))
    f.append(text(600, bits_y - 8, "[1000]", size=9, color=MUTED))

    # Малювання бітових клітинок
    for bi in range(12):
        bx = 360 + bi * 19
        is_set = (bi in [0, 1, 3, 4, 6, 7, 10, 11])
        fill_col = "#27ae60" if is_set else "#ffffff"
        txt_col = "#ffffff" if is_set else "#6b7280"
        val = "1" if is_set else "0"
        f.append(rect(bx, bits_y - 12, 17, 24, fill=fill_col, stroke=NEG, sw=1, rx=2))
        f.append(text(bx + 8.5, bits_y + 5, val, size=10, color=txt_col, bold=True))

    f.append(text(475, 190, "Біт 1: прийнято раніше → REPLAY DROP", size=9.5, color=POS, bold=True))
    f.append(text(475, 208, "Біт 0: новий у вікні → OK, ставимо біт 1", size=9.5, color=FIELD, bold=True))

    # Зона 3: Нові пакети попереду (Праворуч)
    f.append(rect(650, 80, 230, 140, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(765, 104, "Зона 3: Попереду (Seq > last)", size=11, color=FIELD, bold=True))
    f.append(text(765, 126, "seq > 1000", size=11, color=INK, bold=True))
    f.append(text(765, 172, "Зсув маски на (seq - last)", size=10, color=FIELD, bold=True))
    f.append(text(765, 192, "last_seq = seq, біт 0 = 1", size=9.5, color=MUTED))

    # Позначка last_seq
    f.append(circle(615, ax_y, 6, fill=POS, stroke=POS, sw=0))
    f.append(line(615, ax_y - 30, 615, ax_y, color=POS, sw=2))
    f.append(text(615, ax_y - 36, "last_seq = 1000", size=10.5, color=POS, bold=True))

    # Нижня частина: Алгоритм і критичний інваріант
    box_y = 255
    f.append(rect(40, box_y, 860, 185, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(W / 2, box_y + 24, "Порядок обробки кадру на приймачі та критичний інваріант", size=12.5, color=INK, bold=True))

    steps = [
        ("Крок 1. Перевірка Seq", "Якщо seq ≤ last_seq - 64 → скидання без криптографії.\nЯкщо у вікні й біт = 1 → скидання дубліката.", NEG),
        ("Крок 2. Перевірка Тегу", "AEAD перевіряє Auth Tag над (AAD + Ciphertext).\nУсі розрахунки в constant-time!", GOLD),
        ("Крок 3. Фіксація стану", "ЛИШЕ після валідного тегу: оновлюємо bitmap\nта last_seq. Невалідному кадру стан не міняти!", FIELD),
        ("Крок 4. Розшифрування", "Корисне навантаження передається обробнику\nкоманд застосунку. Пристрій у безпеці.", FIELD)
    ]

    for i, (title, desc, col) in enumerate(steps):
        sx = 55 + i * 210
        f.append(rect(sx, box_y + 44, 200, 120, fill="#fafbfc", stroke=col, sw=1.4, rx=4))
        f.append(text(sx + 100, box_y + 66, title, size=10.5, color=col, bold=True))
        lines = desc.split("\n")
        f.append(text(sx + 100, box_y + 94, lines[0], size=9, color=INK))
        f.append(text(sx + 100, box_y + 112, lines[1], size=9, color=MUTED))

    return render(os.path.join(IMG, 'anti-replay-window.svg'), W, H, *f)


# ── 4. Правило Verify-then-Decrypt проти небезпечного розшифрування ────────────
def fig_verify_then_decrypt():
    W, H = 940, 440
    f = [
        text(W / 2, 28, "Золоте правило: Verify-then-Decrypt (Перевір перед розшифруванням)", size=18, bold=True),
        text(W / 2, 50, "розбір неавтентифікованих даних веде до витоків пам'яті, збоїв парсера та атак за часом",
             size=11.5, color=MUTED, italic=True)
    ]

    # Ліва колонка: Фатальна помилка (Decrypt & Parse First)
    f.append(rect(40, 75, 415, 340, fill="#fffafa", stroke=POS, sw=2, rx=8))
    f.append(text(247, 102, "НЕБЕЗПЕЧНО: Розшифрування до тегу", size=13, color=POS, bold=True))

    steps_bad = [
        ("1. Прийом пакета з ефіру", "Буфер із даними від ворога"),
        ("2. Розшифрування в буфер", "Шифротекст перетворюється на Plaintext"),
        ("3. Парсер читає структури", "Читання len, cmd_id, вказівників..."),
        ("4. Виконання або паніка", "Вразливість до buffer overflow / crash!"),
        ("5. Перевірка MAC (запізно!)", "Зловмисник уже експлуатував парсер")
    ]
    by = 135
    for title, sub in steps_bad:
        f.append(rect(65, by, 365, 38, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
        f.append(text(247, by + 16, title, size=10.5, color=POS, bold=True))
        f.append(text(247, by + 30, sub, size=9.5, color=MUTED))
        by += 46

    # Права колонка: Правильний конвеєр (Verify First)
    f.append(rect(485, 75, 415, 340, fill="#fbfdfb", stroke=FIELD, sw=2, rx=8))
    f.append(text(692, 102, "БЕЗПЕЧНО: Verify-then-Decrypt", size=13, color=FIELD, bold=True))

    steps_good = [
        ("1. Перевірка Sequence / Window", "Миттєве відсікання старих пакетів"),
        ("2. Обчислення Auth Tag (AEAD)", "Poly1305 / AES-CCM над AAD + Ciphertext"),
        ("3. Constant-Time порівняння", "crypto_verify_16() без timing-витоків"),
        ("4. Невалідно? МИТТЄВИЙ DROP", "Пам'ять чиста, парсер навіть не викликався"),
        ("5. Валідно? Розшифрування", "Гарантовано цілісні дані без підробок")
    ]
    by = 135
    for title, sub in steps_good:
        f.append(rect(510, by, 365, 38, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
        f.append(text(692, by + 16, title, size=10.5, color=FIELD, bold=True))
        f.append(text(692, by + 30, sub, size=9.5, color=MUTED))
        by += 46

    return render(os.path.join(IMG, 'verify-then-decrypt.svg'), W, H, *f)


if __name__ == '__main__':
    fig_threat_model_radio()
    fig_aead_frame_layout()
    fig_anti_replay_window()
    fig_verify_then_decrypt()
    print("OK: threat-model-radio, aead-frame-layout, anti-replay-window, verify-then-decrypt")
