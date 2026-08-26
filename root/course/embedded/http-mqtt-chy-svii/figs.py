# -*- coding: utf-8 -*-
"""Фігури до теми «HTTP, MQTT чи свій: вибір протоколу до сервера».
Запуск:  python figs.py   → генерує SVG у ./img/
Стиль і примітиви — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Накладні витрати на передачу 8 байтів корисних даних ───────────────────
def fig_overhead_layers():
    W, H = 840, 480
    f = [text(W / 2, 28,
              "Накладний тягар трьох протоколів для відправки 8 байтів телеметрії",
              size=15, bold=True)]

    ox = 160
    max_w = 620
    bar_h = 52

    # HTTP/REST (JSON + TLS): ~720 байтів сумарно
    # MQTT QoS 1 (TLS): ~140 байтів
    # Custom UDP Binary + AEAD: ~44 байти
    protocols = [
        ("HTTP/REST (TLS + JSON)\n~720 байтів", [
            ("IP + TCP (40)", 40, "#95a5a6"),
            ("TLS запис (29)", 29, "#7f8c8d"),
            ("HTTP-заголовки (580 B)", 580, NEG),
            ("JSON (63 B)", 63, "#e67e22"),
            ("Дані 8 B", 8, FIELD),
        ], 720),
        ("MQTT QoS 1 (TLS)\n~140 байтів", [
            ("IP + TCP (40)", 40, "#95a5a6"),
            ("TLS (29)", 29, "#7f8c8d"),
            ("MQTT + Topic (48 B)", 48, POS),
            ("Payload (15 B)", 15, "#e67e22"),
            ("Дані 8 B", 8, FIELD),
        ], 140),
        ("Власний UDP бінарний\n~44 байти", [
            ("IP + UDP (28)", 28, "#95a5a6"),
            ("Header+Tag (8 B)", 8, POS),
            ("Дані 8 B", 8, FIELD),
        ], 44),
    ]

    y = 75
    scale = max_w / 720.0

    for title, segments, total_bytes in protocols:
        lines = title.split("\n")
        f.append(text(ox - 14, y + 20, lines[0], size=12, bold=True, anchor="end"))
        f.append(text(ox - 14, y + 36, lines[1], size=11, color=MUTED, anchor="end"))

        cur_x = ox
        for seg_name, b_val, col in segments:
            seg_w = max(b_val * scale, 6.0)
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                     'fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.5"/>'
                     % (cur_x, y, seg_w, bar_h, col, col))
            if seg_w > 42:
                f.append(text(cur_x + seg_w / 2, y + bar_h / 2 + 4, seg_name,
                              size=10.5, bold=True, color=INK))
            elif seg_w > 18:
                f.append(text(cur_x + seg_w / 2, y + bar_h / 2 + 4, str(b_val),
                              size=9.5, bold=True, color=INK))
            cur_x += seg_w

        y += 105

    b, _, _ = textbox(W / 2, 420,
                      "Зелений сектор (8 байтів) — це корисні дані датчика (температура + вологість + заряд).\n"
                      "Усе інше — протокольний баласт. У HTTP 98.8% трафіку складають заголовки та конверти,\n"
                      "тоді як власний бінарний кадр віддає корисним даним майже 20% пакета навіть з урахуванням IP/UDP.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "transport-overhead-layers.svg"), W, H, *f)


# ── 2. Енергетичний профіль та час активності радіотракту ─────────────────────
def fig_lifecycle_energy():
    W, H = 840, 490
    f = [text(W / 2, 28,
              "Час активності передавача (TX/RX) під час відправки одного відліку",
              size=15, bold=True)]

    # Шкала трьох сценаріїв на часовій осі
    ox = 180
    span = 580
    row_h = 56

    # 1. HTTP/TLS холодний старт (DNS + TCP SYN/ACK + TLS Handshake + HTTP Req/Resp + FIN): ~1400 мс
    # 2. MQTT/TLS постійне з'єднання (Publish + PubAck): ~120 мс
    # 3. Custom UDP постріл (Single Datagram send): ~15 мс
    scenarios = [
        ("HTTP/TLS (холодний)\nDNS + TLS + Запит\n≈ 1400 мс", [
            ("DNS", 0.15, "#95a5a6"),
            ("TCP SYN", 0.12, "#7f8c8d"),
            ("TLS 1.3 Handshake (крипто + сертифікат)", 0.42, POS),
            ("HTTP POST", 0.18, NEG),
            ("200 OK + FIN", 0.13, "#27ae60"),
        ]),
        ("MQTT/TLS (теплий сокет)\nPublish QoS 1\n≈ 120 мс", [
            ("Прокидання стека", 0.08, "#95a5a6"),
            ("MQTT PUBLISH", 0.45, POS),
            ("PUBACK", 0.47, FIELD),
        ]),
        ("UDP Binary (постріл)\nFire & Sleep\n≈ 15 мс", [
            ("RF активність + 1 пакет UDP", 1.0, FIELD),
        ]),
    ]

    y = 80
    for title, segs in scenarios:
        lines = title.split("\n")
        f.append(text(ox - 14, y + 16, lines[0], size=11.5, bold=True, anchor="end"))
        f.append(text(ox - 14, y + 32, lines[1], size=10, color=MUTED, anchor="end"))
        f.append(text(ox - 14, y + 46, lines[2], size=10.5, bold=True, color=POS, anchor="end"))

        cx = ox
        for sname, frac, col in segs:
            sw = span * frac
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" '
                     'fill="%s" fill-opacity="0.30" stroke="%s" stroke-width="1.5"/>'
                     % (cx, y, sw, row_h, col, col))
            if sw > 50:
                f.append(text(cx + sw / 2, y + row_h / 2 + 4, sname,
                              size=10, bold=True, color=INK))
            cx += sw

        y += 105

    b, _, _ = textbox(W / 2, 420,
                      "Радіомодем у режимі передачі споживає 80–250 мА. Кожна секунда неспання коштує тисяч міліампер-секунд.\n"
                      "Холодний сеанс HTTP/TLS утримує чип увімкненим у 100 разів довше, ніж швидкий постріл датаграмою UDP.\n"
                      "Для батарейного пристрою протокольний вибір — це вибір між місяцями та роками автономної роботи.",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "lifecycle-energy-radio.svg"), W, H, *f)


# ── 3. Потік повідомлень MQTT: рівні QoS 0, 1, 2 та механізм LWT ─────────────
def fig_mqtt_qos():
    W, H = 840, 520
    f = [text(W / 2, 28,
              "Рівні гарантії доставки MQTT (QoS 0, 1, 2) та заповіт LWT",
              size=15, bold=True)]

    cols = [
        ("QoS 0 (At most once)", 60, 230, [
            ("PUBLISH", True, "без підтвердження (Fire & Forget)"),
        ], "Втрата можлива, дублікатів 0,\n1 пакет у мережі"),
        ("QoS 1 (At least once)", 260, 430, [
            ("PUBLISH (id=42)", True, "зберегти в черзі до ACK"),
            ("PUBACK (id=42)", False, "видалити з буфера"),
        ], "Гарантована доставка,\nризик дубліката при таймауті"),
        ("QoS 2 (Exactly once)", 460, 630, [
            ("PUBLISH (id=7)", True, "стан: очікує REC"),
            ("PUBREC", False, "стан: отримано"),
            ("PUBREL", True, "стан: звільнити ID"),
            ("PUBCOMP", False, "транзакція закрита"),
        ], "Рівно один раз, 4 пакети,\nвимагає RAM-стан транзакції"),
    ]

    for title, x1, x2, msgs, note in cols:
        mid = (x1 + x2) / 2
        f.append(text(mid, 68, title, size=12, bold=True, color=INK))
        f.append(line(x1 + 10, 85, x1 + 10, 310, color=MUTED, sw=1.2))
        f.append(line(x2 - 10, 85, x2 - 10, 310, color=MUTED, sw=1.2))
        f.append(text(x1 + 10, 80, "Клієнт", size=10, bold=True, color=MUTED))
        f.append(text(x2 - 10, 80, "Брокер", size=10, bold=True, color=MUTED))

        my = 110
        for mtext_str, to_broker, desc in msgs:
            if to_broker:
                f.append(arrow(x1 + 12, my, x2 - 12, my, color=NEG, sw=1.6))
                f.append(text(mid, my - 6, mtext_str, size=9.5, bold=True, color=NEG))
            else:
                f.append(arrow(x2 - 12, my, x1 + 12, my, color=FIELD, sw=1.6))
                f.append(text(mid, my - 6, mtext_str, size=9.5, bold=True, color=FIELD))
            my += 44

        b_note, _, _ = textbox(mid, 340, note, size=10, fill=FILL, stroke=LINE)
        f.append(b_note)

    # LWT блок праворуч / внизу
    lwt_x = 650
    f.append(text(lwt_x + 85, 68, "Заповіт (LWT)", size=12, bold=True, color=POS))
    b_lwt, _, _ = textbox(lwt_x + 85, 170,
                          "1. Під час CONNECT клієнт реєструє\n"
                          "   топік і payload заповіту:\n"
                          "   \"device/status\": \"OFFLINE\".\n\n"
                          "2. Якщо клієнт гине раптово\n"
                          "   (обрив TCP, втрата живлення),\n"
                          "   брокер сам публікує заповіт\n"
                          "   всім підписникам.",
                          size=10, fill="#fdecea", stroke=POS, color=INK)
    f.append(b_lwt)

    b, _, _ = textbox(W / 2, 450,
                      "QoS 0 підходить для частих метрик, де втрата одного відліку не критична. QoS 1 — робоча конячка IoT;\n"
                      "дублікати фільтруються ідемпотентністю на сервері. QoS 2 занадто важкий для батарейних вузлів.\n"
                      "LWT вирішує проблему «мовчазної смерті» вузла без необхідності опитувати його статуси через HTTP.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "mqtt-qos-flow.svg"), W, H, *f)


# ── 4. Матриця інженерного вибору протоколу ──────────────────────────────────
def fig_decision_matrix():
    W, H = 840, 500
    f = [text(W / 2, 28,
              "Інженерна матриця вибору протоколу до сервера",
              size=15, bold=True)]

    # Дерево критеріїв
    # Рівень 1: Живлення
    # Рівень 2: Потреба у зворотному керуванні (Push від сервера)
    # Рівень 3: Обмеження трафіку та інфраструктури

    boxes = [
        (130, 80, 210, 48, "Батарейне живлення\n(глибокий сон 95%+)", "#fdecea", POS),
        (580, 80, 210, 48, "Постійне живлення\n(мережа / бортова мережа)", "#eaf0fd", NEG),

        # Гілка батареї
        (130, 180, 210, 48, "Трафік критичний?\n(NB-IoT / LoRa / супутник)", "#fff8e1", INK),
        (30, 280, 180, 52, "Так: ліміт байтів\n→ Власний бінарний UDP\nабо CoAP", "#eafaf1", FIELD),
        (230, 280, 180, 52, "Ні: Wi-Fi / LTE-M\n→ HTTP REST (JSON/CBOR)\nкороткі пачки", "#f4f6f8", LINE),

        # Гілка постійного живлення
        (580, 180, 210, 48, "Потрібен миттєвий зворотний\nконтроль (Push від сервера)?", "#fff8e1", INK),
        (480, 280, 180, 52, "Так: двосторонній канал\n→ MQTT (TLS, Keep-Alive)\nабо WebSockets", "#eafaf1", FIELD),
        (680, 280, 180, 52, "Ні: тільки вивантаження\nлогів / OTA / телеметрія\n→ HTTP/HTTPS REST", "#f4f6f8", LINE),
    ]

    for cx, cy, w, h, stext, fill, stroke in boxes:
        f.append(fitbox(cx - w / 2, cy - h / 2, w, h, stext, size=11,
                        fill=fill, stroke=stroke, bold=True))

    # Стрілки
    # Головні розгалуження
    f.append(arrow(130, 104, 130, 156, color=POS, sw=1.6))
    f.append(arrow(580, 104, 580, 156, color=NEG, sw=1.6))

    # Батарейні стрілки
    f.append(arrow(130 - 30, 204, 30 + 30, 254, color=INK, sw=1.4))
    f.append(text(60, 222, "Так", size=10, bold=True, color=FIELD))
    f.append(arrow(130 + 30, 204, 230 - 30, 254, color=INK, sw=1.4))
    f.append(text(195, 222, "Ні", size=10, bold=True, color=MUTED))

    # Мережеві стрілки
    f.append(arrow(580 - 30, 204, 480 + 30, 254, color=INK, sw=1.4))
    f.append(text(510, 222, "Так", size=10, bold=True, color=FIELD))
    f.append(arrow(580 + 30, 204, 680 - 30, 254, color=INK, sw=1.4))
    f.append(text(645, 222, "Ні", size=10, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 420,
                      "Критерій вибору зводиться до двох запитань: (1) чи дозволяє бюджет енергії тримати TCP-з'єднання відкритим?\n"
                      "(2) чи повинна хмара миттєво віддавати команди на пристрій без запиту з його боку?\n"
                      "Відповідь «Ні + Ні» веде до бінарного UDP; «Ні + Так» — до MQTT; «Так + Ні» — до стандартного HTTP/REST.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "decision-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_overhead_layers()
    fig_lifecycle_energy()
    fig_mqtt_qos()
    fig_decision_matrix()
    print("OK: 4 figures generated in", IMG)
