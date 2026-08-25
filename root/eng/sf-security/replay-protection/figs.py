# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. threat-model: Модель загрози повтору ──────────────────────────────────
# Ідея: Перехоплення легітимного зашифрованого або підписаного пакету.
# Шифр захищає конфіденційність, підпис — цілісність, але без свіжості
# сервер виконує команду вдруге, бо криптографія математично коректна.

def fig_threat_model():
    W, H = 760, 280
    p = []
    # Клієнт
    p.append(rect(30, 40, 180, 90, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
    p.append(text(120, 68, "Легітимний клієнт", size=12, color=INK, bold=True))
    p.append(text(120, 92, "POST /pay 1000 грн", size=10, color=MUTED))
    p.append(text(120, 112, "Підпис: HMAC-SHA256", size=10, color=FIELD, bold=True))

    # Стрілка клієнт -> сервер (прямий зв'язок)
    p.append(arrow(215, 85, 535, 85, color=FIELD, sw=2.2))
    p.append(text(375, 75, "1. Оригінальний запит (підпис валідний)", size=10, color=FIELD, bold=True))

    # Зловмисник посередині (Sniffer)
    p.append(rect(240, 160, 270, 95, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(375, 185, "Пасивний спостерігач (Sniffer)", size=12, color=POS, bold=True))
    p.append(text(375, 208, "Зберігає байти (ключ не потрібен)", size=10, color=INK))
    p.append(text(375, 232, "2. Повторне надсилання через 1 год", size=10, color=POS, bold=True))

    # Пунктирна лінія від перехоплення до шпигуна
    p.append(line(375, 90, 375, 155, color=POS, sw=1.8, dash="4,3"))
    # Стрілка від шпигуна до сервера
    p.append(arrow(515, 205, 555, 135, color=POS, sw=2.2))

    # Сервер
    p.append(rect(540, 40, 190, 90, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
    p.append(text(635, 68, "Сервер обробки", size=12, color=INK, bold=True))
    p.append(text(635, 92, "Перевірка підпису: OK", size=10, color=FIELD))
    p.append(text(635, 112, "Списання: 1000 + 1000 грн!", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "threat-model.svg"), W, H, *p,
           title="Модель загрози повторного відтворення")


# ── 2. timestamp-nonce-window: Часове вікно та одноразові числа ──────────────
# Ідея: Перевірка свіжості за часовою міткою обмежує термін життя пакету (Δt),
# а кеш Nonce у межах цього вікна виявляє дублікати без безмежного зростання пам'яті.

def fig_timestamp_nonce_window():
    W, H = 760, 290
    p = []

    # Часова шкала
    p.append(arrow(50, 100, 715, 100, color=LINE, sw=2))
    p.append(text(710, 125, "Час (t)", size=11, color=MUTED, anchor="end"))

    # Межі вікна валідності
    p.append(rect(230, 45, 300, 90, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(380, 65, "Допустиме вікно свіжості (±Δt = 300 с)", size=12, color=FIELD, bold=True))

    # Поточний час сервера - дві лінії без перетину напису
    p.append(line(380, 35, 380, 50, color=POS, sw=2, dash="3,2"))
    p.append(line(380, 75, 380, 145, color=POS, sw=2, dash="3,2"))
    p.append(text(380, 28, "T_сервера (зараз)", size=11, color=POS, bold=True))

    # Зони відхилення
    p.append(text(130, 75, "Застарілий (t < T - Δt)", size=11, color=POS, bold=True))
    p.append(text(130, 95, "Відхилити: прострочено", size=10, color=MUTED))

    p.append(text(620, 75, "З майбутнього (t > T + Δt)", size=11, color=POS, bold=True))
    p.append(text(620, 95, "Відхилити: розсинхрон", size=10, color=MUTED))

    # Панель перевірки Nonce
    p.append(rect(60, 165, 640, 105, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    p.append(text(380, 190, "Алгоритм верифікації усередині вікна:", size=12, color=INK, bold=True))
    p.append(text(380, 215, "1. Чи |T_пакета - T_сервера| ≤ 300 с?  →  НІ: відхилити (без звернення до кешу)", size=10, color=INK))
    p.append(text(380, 235, "2. Чи Nonce вже є в оперативному кеші?  →  ТАК: відхилити (Replay Attack!)", size=10, color=POS, bold=True))
    p.append(text(380, 255, "3. Інакше: зберегти Nonce у кеш з TTL = 600 с та виконати запит", size=10, color=FIELD))

    render(os.path.join(OUT, "timestamp-nonce-window.svg"), W, H, *p,
           title="Часове вікно допуску та кешування Nonce")


# ── 3. sliding-window-bitmask: Ковзне вікно бітової маски (RFC 6479) ────────
# Ідея: У мережах без встановлення сесійного часу (IPsec, DTLS, WireGuard)
# порядкові номери пакетів відстежуються ковзною бітовою маскою (64/128 біт).

def fig_sliding_window_bitmask():
    W, H = 760, 300
    p = []

    # Вісь порядкових номерів
    p.append(arrow(40, 80, 725, 80, color=LINE, sw=2))
    p.append(text(710, 105, "Seq №", size=11, color=MUTED, anchor="end"))

    # Зона застарілих пакетів (ліворуч від вікна)
    p.append(rect(40, 45, 170, 70, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(125, 70, "Позаду вікна (Seq < M - W)", size=10, color=POS, bold=True))
    p.append(text(125, 95, "Відхилити без перевірки", size=9, color=MUTED))

    # Ковзне вікно шириною W бітів
    p.append(rect(230, 35, 300, 90, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(380, 58, "Ковзне вікно шириною W = 64 біти", size=12, color=NEG, bold=True))

    # Біти всередині вікна (демонстрація маски)
    for i in range(8):
        bx = 250 + i * 32
        val = "1" if i in [0, 2, 3, 5, 7] else "0"
        c_fill = "#dbeafe" if val == "1" else "#ffffff"
        c_text = NEG if val == "1" else MUTED
        p.append(rect(bx, 75, 26, 26, fill=c_fill, stroke=NEG, sw=1.2, rx=3))
        p.append(text(bx + 13, 93, val, size=11, color=c_text, bold=True))

    p.append(text(380, 116, "Бітова маска: 1 = отримано, 0 = очікується", size=9, color=MUTED))

    # Найбільший отриманий номер (M) - без перетину
    p.append(line(530, 25, 530, 135, color=FIELD, sw=2.2, dash="4,3"))
    p.append(text(530, 20, "M (Seq_max)", size=11, color=FIELD, bold=True))

    # Зона майбутніх номерів (праворуч від M)
    p.append(rect(550, 45, 160, 70, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(630, 70, "Попереду вікна (Seq > M)", size=10, color=FIELD, bold=True))
    p.append(text(630, 95, "Зсунути вікно, M := Seq", size=9, color=MUTED))

    # Пояснювальний блок рішень
    p.append(rect(40, 150, 680, 125, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    p.append(text(380, 175, "Правила обробки вхідного пакету з номером S:", size=12, color=INK, bold=True))
    p.append(text(380, 198, "• S > M:  Пакет новий. Зсунути маску вліво на (S - M) біт, встановити біт 0, оновити M = S.", size=10, color=INK))
    p.append(text(380, 218, "• M - W < S ≤ M:  Пакет у вікні. Якщо біт (M - S) == 1 → ВІДХИЛИТИ (Replay); якщо 0 → ПРИЙНЯТИ і біт := 1.", size=10, color=INK))
    p.append(text(380, 238, "• S ≤ M - W:  Пакет занадто старий. Негайно ВІДХИЛИТИ (захист від переповнення лічильника).", size=10, color=POS, bold=True))
    p.append(text(380, 258, "Часова складність: O(1) за бітовими операціями, фіксована пам'ять: 8-16 байт.", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "sliding-window-bitmask.svg"), W, H, *p,
           title="Ковзне бітове вікно захисту від повторів")


# ── 4. rolling-code-hopping: Динамічний плаваючий код (KeeLoq) ───────────────
# Ідея: Передавач і приймач тримають синхронний лічильник натискань,
# зашифрований спільним майстер-ключем. Прийом уперед у межах вікна відкриває замок.

def fig_rolling_code_hopping():
    W, H = 760, 280
    p = []

    # Брелок (Клієнт)
    p.append(rect(40, 50, 200, 110, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
    p.append(text(140, 75, "Брелок (Transmitter)", size=12, color=INK, bold=True))
    p.append(text(140, 98, "Лічильник: C = 1042", size=10, color=FIELD, bold=True))
    p.append(text(140, 120, "Шифрування: E_K(C, UID)", size=10, color=MUTED))
    p.append(text(140, 142, "C := C + 1 після кліку", size=10, color=INK))

    # Канал радіопередачі
    p.append(arrow(245, 105, 510, 105, color=NEG, sw=2.2))
    p.append(text(380, 92, "Радіоканал (433.92 МГц)", size=10, color=NEG, bold=True))
    p.append(text(380, 122, "Зашифрований блок: 32 біти коду", size=9, color=MUTED))

    # Приймач авто (Receiver)
    p.append(rect(515, 50, 210, 110, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
    p.append(text(620, 75, "Блок авто (Receiver)", size=12, color=INK, bold=True))
    p.append(text(620, 98, "Останній валідний: C_rx = 1041", size=10, color=FIELD, bold=True))
    p.append(text(620, 120, "Розшифрування: D_K(пакет)", size=10, color=MUTED))
    p.append(text(620, 142, "Вікно допуску: [C_rx+1 .. C_rx+256]", size=9, color=INK))

    # Вразливість RollJam
    p.append(rect(40, 180, 680, 80, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(380, 205, "Вектор атаки перехоплення RollJam (глушіння + запис):", size=12, color=POS, bold=True))
    p.append(text(380, 228, "Зловмисник глушить приймач авто й записує код C_1042. Водій тисне вдруге: шпигун записує C_1043,", size=10, color=INK))
    p.append(text(380, 248, "але транслює в авто C_1042. Авто відмикається, а код C_1043 лишається свіжим і дійсним у руках шпигуна!", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "rolling-code-hopping.svg"), W, H, *p,
           title="Плаваючий код (Rolling Code) та вектор RollJam")


# ── 5. defense-taxonomy-matrix: Матриця вибору архітектурного захисту ─────────
# Ідея: Порівняння тактик за критеріями стану, затримки (RTT), пам'яті та сфери застосування.

def fig_defense_taxonomy_matrix():
    W, H = 760, 310
    p = []

    # Заголовок таблиці
    headers = [("Механізм захисту", 130), ("Викликів (RTT)", 95), ("Витрати пам'яті", 115), ("Чутливість до черги", 130), ("Основна сфера", 150)]
    cur_x = 70
    for title, w in headers:
        p.append(rect(cur_x, 30, w, 35, fill="#1e293b", stroke="#0f172a", sw=1))
        p.append(text(cur_x + w/2, 52, title, size=10, color="#ffffff", bold=True))
        cur_x += w

    rows = [
        ("Челендж-відповідь", "2 (Подвійна затримка)", "O(1) на час запиту", "Стійкий (унікальний)", "Автентифікація, TLS"),
        ("Часова мітка + Nonce", "1 (Однобічний виклик)", "O(R · Δt) у кеші/Bloom", "Стійкий у межах ±Δt", "REST API, AWS SigV4"),
        ("Ковзне бітове вікно", "1 (Однобічний виклик)", "O(W) бітів (фіксовано)", "Дозволяє реордеринг ≤ W", "IPsec, DTLS, WireGuard"),
        ("Плаваючий лічильник", "1 (Асинхронний ефір)", "O(1) один лічильник", "Лише монотонне зростання", "Брелоки, CAN Bus SecOC"),
        ("Double Ratchet (DH)", "1 (Сесійний потік)", "O(S) сесійні ключі", "Повне оновлення ентропії", "Signal, E2EE месенджери")
    ]

    cur_y = 65
    for i, row in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        cur_x = 70
        for val, (_, w) in zip(row, headers):
            p.append(rect(cur_x, cur_y, w, 42, fill=bg, stroke="#cbd5e1", sw=1))
            c_text = POS if "Подвійна" in val or "O(R" in val else (FIELD if "O(1)" in val or "O(W)" in val or "REST" in val or "IPsec" in val else INK)
            bld = True if c_text in (POS, FIELD) or cur_x == 70 else False
            p.append(text(cur_x + w/2, cur_y + 25, val, size=9, color=c_text, bold=bld))
            cur_x += w
        cur_y += 42

    p.append(fitbox(50, 278, 660, 24,
                    "Вибір захисту диктується протоколом: надійні канали вимагають монотонності, асинхронні — вікон.",
                    size=10, color=MUTED, fill="#ffffff", stroke="#ffffff", sw=0))

    render(os.path.join(OUT, "defense-taxonomy-matrix.svg"), W, H, *p,
           title="Порівняльна таксономія методів захисту від повторів")


if __name__ == "__main__":
    fig_threat_model()
    fig_timestamp_nonce_window()
    fig_sliding_window_bitmask()
    fig_rolling_code_hopping()
    fig_defense_taxonomy_matrix()
    print("Всі фігури згенеровано успішно.")
