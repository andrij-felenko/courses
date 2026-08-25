# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_buffering_vs_streaming():
    """Повне буферизування проти потокового передавання: використання RAM."""
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 28, "Порівняння підходів: повне буферизування в RAM проти потокового конвеєра",
                      size=16, bold=True))

    # Ліва колонка: Повне буферизування (In-Memory Buffering)
    frags.append(rect(30, 60, 425, 340, fill=BG, stroke=POS, sw=1.5, rx=8))
    frags.append(text(242, 88, "Повне буферизування (In-Memory Buffering)", size=14, bold=True, color=POS))
    frags.append(text(242, 108, "Споживання пам'яті пропорційне розміру тіла: O(N)", size=11, color=MUTED))

    # Візуалізація пам'яті ліворуч: великий блок RAM
    frags.append(rect(50, 130, 385, 120, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    frags.append(text(242, 155, "Пул оперативної пам'яті процесу (RAM)", size=12, bold=True, color=POS))

    b1, _, _ = textbox(135, 205, "Запит 1: 500 МБ\n(буфер у RAM)", size=11, min_w=150, fill="#f9d5d5", stroke=POS, bold=True)
    b2, _, _ = textbox(315, 205, "Запит 2: 500 МБ\n(буфер у RAM)", size=11, min_w=150, fill="#f9d5d5", stroke=POS, bold=True)
    frags += [b1, b2]

    # Наслідки ліворуч
    note_l, _, _ = textbox(242, 320, "• 100 одночасних з'єднань = 50 ГБ RAM → ризик OOM-killer\n• Висока затримка TTFB: клієнт чекає повного викачування\n• Навантаження на збирач сміття (GC) та фрагментація пам'яті",
                           size=11, min_w=390, fill="#fff5f5", stroke=POS, pad=10)
    frags.append(note_l)

    # Права колонка: Потокове передавання (Streaming Pipeline)
    frags.append(rect(485, 60, 425, 340, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(697, 88, "Потокове передавання (Streaming Pipeline)", size=14, bold=True, color=FIELD))
    frags.append(text(697, 108, "Споживання пам'яті фіксоване й обмежене: O(1)", size=11, color=MUTED))

    # Візуалізація пам'яті праворуч: конвеєр із фіксованим буфером
    frags.append(rect(505, 130, 385, 120, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(697, 155, "Пул оперативної пам'яті процесу (RAM)", size=12, bold=True, color=FIELD))

    c1, _, _ = textbox(585, 205, "Чанк 1: 64 КБ\n(обробка/запис)", size=11, min_w=140, fill="#d4efdf", stroke=FIELD, bold=True)
    c2, _, _ = textbox(770, 205, "Чанк 2: 64 КБ\n(обробка/запис)", size=11, min_w=140, fill="#d4efdf", stroke=FIELD, bold=True)
    frags += [c1, c2]

    # Наслідки праворуч
    note_r, _, _ = textbox(697, 320, "• 100 одночасних з'єднань = лише 6.4 МБ RAM у піку\n• Мінімальна затримка TTFB: дані віддаються відразу\n• Стабільне навантаження незалежно від розміру файлу (10 ГБ+)",
                           size=11, min_w=390, fill="#f0fff4", stroke=FIELD, pad=10)
    frags.append(note_r)

    render(os.path.join(IMG, "buffering-vs-streaming.svg"), W, H, *frags)


def fig_chunked_transfer_framing():
    """Анатомія блокового кодування Chunked Transfer Encoding."""
    W, H = 940, 460
    frags = []
    frags.append(text(W / 2, 28, "Анатомія блокового кодування Transfer-Encoding: chunked",
                      size=16, bold=True))

    # Заголовок протоколу
    frags.append(rect(40, 60, 860, 55, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(470, 82, "HTTP/1.1 200 OK \\r\\n Transfer-Encoding: chunked \\r\\n Trailer: Content-MD5, X-Checksum \\r\\n\\r\\n",
                      size=12, bold=True, color=INK))
    frags.append(text(470, 102, "Заголовки відповіді: розмір тіла заздалегідь невідомий, анонсовано підсумкові трейлери",
                      size=10, color=MUTED))

    # Чанк 1
    frags.append(rect(40, 130, 860, 70, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    frags.append(rect(50, 140, 140, 50, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(120, 160, "1a \\r\\n", size=12, bold=True, color=NEG))
    frags.append(text(120, 178, "Розмір (26 байтів, hex)", size=9, color=MUTED))

    frags.append(rect(200, 140, 540, 50, fill=BG, stroke=NEG, sw=1.0, rx=4))
    frags.append(text(470, 160, "abcdefghijklmnopqrstuvwxyz (26 байтів корисного навантаження)", size=11, bold=True, color=INK))
    frags.append(text(470, 178, "Тіло фрагмента даних", size=9, color=MUTED))

    frags.append(rect(750, 140, 140, 50, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(820, 160, "\\r\\n", size=12, bold=True, color=NEG))
    frags.append(text(820, 178, "Розділювач CRLF", size=9, color=MUTED))

    # Чанк 2
    frags.append(rect(40, 215, 860, 70, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    frags.append(rect(50, 225, 140, 50, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(120, 245, "10 \\r\\n", size=12, bold=True, color=NEG))
    frags.append(text(120, 263, "Розмір (16 байтів, hex)", size=9, color=MUTED))

    frags.append(rect(200, 225, 540, 50, fill=BG, stroke=NEG, sw=1.0, rx=4))
    frags.append(text(470, 245, "1234567890abcdef (16 байтів корисного навантаження)", size=11, bold=True, color=INK))
    frags.append(text(470, 263, "Тіло фрагмента даних", size=9, color=MUTED))

    frags.append(rect(750, 225, 140, 50, fill="#d0e1fd", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(820, 245, "\\r\\n", size=12, bold=True, color=NEG))
    frags.append(text(820, 263, "Розділювач CRLF", size=9, color=MUTED))

    # Фінальний чанк і Трейлери
    frags.append(rect(40, 300, 860, 95, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=6))
    frags.append(rect(50, 310, 140, 75, fill="#fdebd0", stroke="#f39c12", sw=1.0, rx=4))
    frags.append(text(120, 338, "0 \\r\\n", size=12, bold=True, color="#d35400"))
    frags.append(text(120, 360, "Фінальний нуль-чанк", size=9, color=MUTED))

    frags.append(rect(200, 310, 540, 75, fill=BG, stroke="#f39c12", sw=1.0, rx=4))
    frags.append(text(470, 335, "Content-MD5: Q2hlY2tzdW1WYWx1ZQ== \\r\\n", size=11, bold=True, color=INK))
    frags.append(text(470, 355, "X-Checksum-SHA256: e3b0c44298fc1c149afbf4c8... \\r\\n", size=11, bold=True, color=INK))
    frags.append(text(470, 373, "Трейлери (метадані, розраховані на льоту під час стримінгу)", size=9, color=MUTED))

    frags.append(rect(750, 310, 140, 75, fill="#fdebd0", stroke="#f39c12", sw=1.0, rx=4))
    frags.append(text(820, 338, "\\r\\n", size=12, bold=True, color="#d35400"))
    frags.append(text(820, 360, "Кінцевий порожній CRLF", size=9, color=MUTED))

    frags.append(text(W / 2, 425, "З'єднання лишається відкритим для наступного HTTP-запиту без розриву TCP-сесії",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "chunked-transfer-framing.svg"), W, H, *frags)


def fig_backpressure_flow():
    """Ланцюг зворотного тиску (Backpressure) крізь сокети й буфери."""
    W, H = 940, 400
    frags = []
    frags.append(text(W / 2, 28, "Ланцюг поширення зворотного тиску (Backpressure) від споживача до джерела",
                      size=16, bold=True))

    # Блок 1: Повільний споживач
    frags.append(rect(30, 60, 200, 280, fill=BG, stroke=POS, sw=1.5, rx=8))
    frags.append(text(130, 85, "1. Споживач (Sink)", size=13, bold=True, color=POS))
    frags.append(text(130, 105, "Повільна обробка / I/O", size=10, color=MUTED))
    b_sink, _, _ = textbox(130, 180, "Додаток не встигає\nчитати з сокета\nчерез повільний диск\nабо довгий парсинг",
                           size=11, min_w=175, fill="#fdecea", stroke=POS)
    frags.append(b_sink)
    frags.append(text(130, 275, "Буфер SO_RCVBUF", size=11, bold=True, color=POS))
    frags.append(text(130, 295, "переповнюється (100%)", size=10, color=POS))

    # Стрілка тиску 1 -> 2
    frags.append(arrow(240, 200, 310, 200, color=POS, sw=2.0))
    frags.append(text(275, 185, "Зворотний", size=10, bold=True, color=POS))
    frags.append(text(275, 220, "тиск", size=10, bold=True, color=POS))

    # Блок 2: Стек TCP та вікно
    frags.append(rect(320, 60, 280, 280, fill=BG, stroke="#e67e22", sw=1.5, rx=8))
    frags.append(text(460, 85, "2. Стек TCP та Мережа", size=13, bold=True, color="#e67e22"))
    frags.append(text(460, 105, "Керування потоком TCP Flow Control", size=10, color=MUTED))
    b_tcp, _, _ = textbox(460, 180, "TCP Receiver Window\nзвужується до 0:\nZero-Window Update\nвідправляється серверу",
                          size=11, min_w=250, fill="#fef5e7", stroke="#e67e22")
    frags.append(b_tcp)
    frags.append(text(460, 275, "Мережевий потік зупинено:", size=11, bold=True, color="#e67e22"))
    frags.append(text(460, 295, "TCP ACK RWIN = 0", size=10, color="#e67e22"))

    # Стрілка тиску 2 -> 3
    frags.append(arrow(610, 200, 680, 200, color=POS, sw=2.0))
    frags.append(text(645, 185, "Зворотний", size=10, bold=True, color=POS))
    frags.append(text(645, 220, "тиск", size=10, bold=True, color=POS))

    # Блок 3: Відправник / Джерело
    frags.append(rect(690, 60, 220, 280, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(800, 85, "3. Джерело (Source)", size=13, bold=True, color=FIELD))
    frags.append(text(800, 105, "Відправник даних", size=10, color=MUTED))
    b_src, _, _ = textbox(800, 180, "Буфер SO_SNDBUF\nзаповнюється;\nwrite() блокується або\nвертає EAGAIN",
                          size=11, min_w=195, fill="#eafaf1", stroke=FIELD)
    frags.append(b_src)
    frags.append(text(800, 275, "Генерація призупинена:", size=11, bold=True, color=FIELD))
    frags.append(text(800, 295, "читання з диска на паузі", size=10, color=FIELD))

    frags.append(text(W / 2, 375, "Саморегуляція: швидкість відправника автоматично підлаштовується під пропускну здатність споживача",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "backpressure-flow.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_buffering_vs_streaming()
    fig_chunked_transfer_framing()
    fig_backpressure_flow()
    print("Всі фігури згенеровано успішно.")
