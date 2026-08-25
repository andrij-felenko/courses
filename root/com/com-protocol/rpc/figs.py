# -*- coding: utf-8 -*-
"""Фігури до теми «RPC, серіалізація та протокольні буфери (gRPC / Cap'n Proto)».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_BG   = "#eaf0fd"
GREEN_BG  = "#eaf6ee"
RED_BG    = "#fdecea"
AMBER_BG  = "#fdf6e3"
AMBER     = "#b8860b"
PAD_BG    = "#e4e7ea"
MONO      = "Consolas, 'DejaVu Sans Mono', monospace"


def mono_text(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── 1. Анатомія та життєвий цикл RPC-виклику ──────────────────────────────────
def fig_rpc_flow():
    W, H = 1020, 540
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 28, "Анатомія віддаленого виклику процедури (RPC flow)", size=16, bold=True))

    # Контейнери: Клієнтський вузол та Серверний вузол
    f.append(rect(25, 55, 455, 460, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(252, 80, "Клієнтський вузол (Client)", size=14, color=NEG, bold=True))

    f.append(rect(540, 55, 455, 460, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(767, 80, "Серверний вузол (Server)", size=14, color=POS, bold=True))

    # Мережевий простір посередині
    f.append(rect(488, 55, 44, 460, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(510, 285, "Мережа (TCP / HTTP2)", size=11, color=MUTED, bold=True, anchor="middle", italic=True))

    # ── Клієнт: Застосунок вгорі ──
    f.append(fitbox(45, 100, 415, 52, "1. Логіка застосунку (User Code)\nres = client.GetUser(id=42)",
                    size=13, fill=BLUE_BG, stroke=NEG, sw=1.5, color=INK, bold=True))

    # Клієнт: Ліва колонка (Запит униз)
    f.append(fitbox(45, 185, 195, 80, "2. Клієнтський стаб\n(Client Stub)\nМаршалінг у байти,\nпризначення Call-ID",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    f.append(fitbox(45, 305, 195, 80, "3. Клієнтський\nтранспорт\nКадрування повідомлення,\nвідправка в сокет",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    # Клієнт: Права колонка (Відповідь угору)
    f.append(fitbox(265, 305, 195, 80, "8. Отримання кадру\nЧитання із сокета,\nзіставлення Call-ID",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    f.append(fitbox(265, 185, 195, 80, "9. Демаршалінг\n(Unmarshal Reply)\nРозбір результату,\nповернення в код",
                    size=11, fill=GREEN_BG, stroke=FIELD, sw=1.5, color=INK, bold=True))

    # Стрілки на клієнті
    f.append(arrow(142, 153, 142, 183, color=NEG, sw=1.8))
    f.append(arrow(142, 267, 142, 303, color=NEG, sw=1.8))

    f.append(arrow(362, 303, 362, 267, color=FIELD, sw=1.8))
    f.append(arrow(362, 183, 362, 153, color=FIELD, sw=1.8))

    # ── Сервер: Обробник угорі ──
    f.append(fitbox(560, 100, 415, 52, "6. Серверна функція (Handler)\nОбробка запиту, виконання бізнес-логіки",
                    size=13, fill=RED_BG, stroke=POS, sw=1.5, color=INK, bold=True))

    # Сервер: Ліва колонка (Запит угору)
    f.append(fitbox(560, 305, 195, 80, "4. Серверний\nтранспорт\nПрийом кадру з мережі,\nперевірка дедлайну",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    f.append(fitbox(560, 185, 195, 80, "5. Серверний\nскелетон (Skeleton)\nДемаршалінг аргументів,\nвиклик обробника",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    # Сервер: Права колонка (Відповідь униз)
    f.append(fitbox(780, 185, 195, 80, "7. Маршалінг відповіді\nСеріалізація результату\nта статусу помилки",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    f.append(fitbox(780, 305, 195, 80, "7b. Серверний\nтранспорт\nКадрування відповіді,\nвідправка в мережу",
                    size=11, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK))

    # Стрілки на сервері
    f.append(arrow(657, 303, 657, 267, color=POS, sw=1.8))
    f.append(arrow(657, 183, 657, 153, color=POS, sw=1.8))

    f.append(arrow(877, 153, 877, 183, color=FIELD, sw=1.8))
    f.append(arrow(877, 267, 877, 303, color=FIELD, sw=1.8))

    # ── Мережеві стрілки ──
    # Запит: з клієнтського транспорту в серверний транспорт
    f.append(arrow(241, 345, 558, 345, color=NEG, sw=2.0))
    f.append(text(400, 400, "1..3 Клієнт формує запит", size=11, color=NEG, anchor="middle"))

    # Відповідь: з серверного транспорту в клієнтський транспорт
    f.append(arrow(778, 440, 462, 440, color=FIELD, sw=2.0))
    f.append(line(877, 387, 877, 440, color=FIELD, sw=1.8))
    f.append(line(462, 440, 362, 440, color=FIELD, sw=1.8))
    f.append(arrow(362, 440, 362, 387, color=FIELD, sw=1.8))
    f.append(text(620, 460, "7..9 Сервер повертає результат", size=11, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, "rpc-flow.svg"), W, H, *f)


# ── 2. Двійковий формат Protocol Buffers: Varint, ZigZag та TLV ──────────────
def fig_protobuf_varint_tlv():
    W, H = 1000, 530
    f = []

    f.append(text(W / 2, 28, "Двійкове пакування Protocol Buffers: TLV, Varint та ZigZag", size=16, bold=True))

    # Секція 1: Структура ключа поля (Tag / Key)
    f.append(rect(40, 52, 920, 125, fill="#ffffff", stroke="#94a3b8", sw=1.3, rx=8))
    f.append(text(55, 75, "1. Ключ поля (Tag = field_number << 3 | wire_type):", size=13, color=INK, bold=True, anchor="start"))

    f.append(fitbox(60, 92, 540, 40, "Номер поля (field_number: 1..536870911)  [біти 7..3]", size=12, fill=BLUE_BG, stroke=NEG, sw=1.2, color=NEG, bold=True))
    f.append(fitbox(605, 92, 335, 40, "Тип дроту (wire_type: 0..5) [біти 2..0]", size=12, fill=GREEN_BG, stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    f.append(text(60, 155, "wire_type: 0 = Varint (int32/bool), 1 = 64-bit (fixed64/double), 2 = Length-delimited (string/bytes/message), 5 = 32-bit (fixed32/float)", size=11, color=MUTED, anchor="start"))

    # Секція 2: Base-128 Varint кодування числа 300
    f.append(rect(40, 190, 920, 165, fill="#ffffff", stroke="#94a3b8", sw=1.3, rx=8))
    f.append(text(55, 212, "2. Base-128 Varint: кодування числа 300 (0x012C = 00000001 00101100_2):", size=13, color=INK, bold=True, anchor="start"))

    # Крок розбиття на 7-бітні групи
    f.append(mono_text(60, 240, "Крок 1: розбиваємо на 7-бітні шматки:  [0000010] [0101100]  (значення 2 та 44)", size=12, color=INK))
    f.append(mono_text(60, 265, "Крок 2: міняємо порядок (little-endian): молодші 7 біт ідуть першими -> 0101100, потім 0000010", size=12, color=INK))
    f.append(mono_text(60, 290, "Крок 3: додаємо MSB (1 = продовження є, 0 = останній байт):", size=12, color=INK))

    # Байтові блоки
    f.append(rect(60, 302, 180, 42, fill=AMBER_BG, stroke=AMBER, sw=1.5, rx=5))
    f.append(mono_text(70, 327, "1 0101100 (0xAC)", size=13, color=INK, bold=True))

    f.append(rect(255, 302, 180, 42, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=5))
    f.append(mono_text(265, 327, "0 0000010 (0x02)", size=13, color=INK, bold=True))

    f.append(text(460, 327, "-> Замість 4 байтів uint32 число 300 займає 2 байти: 0xAC 0x02", size=12, color=FIELD, bold=True, anchor="start"))

    # Секція 3: ZigZag кодування для знакових чисел
    f.append(rect(40, 368, 920, 142, fill="#ffffff", stroke="#94a3b8", sw=1.3, rx=8))
    f.append(text(55, 390, "3. ZigZag кодування для sint32/sint64: (n << 1) ^ (n >> 31)", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(60, 412, "Звичайний int32(-1) у Varint займає 10 байтів через знакове розширення до 64 біт. ZigZag відображає знакові числа у беззнакові:", size=11, color=MUTED, anchor="start"))

    # Табличка ZigZag
    f.append(fitbox(60, 425, 170, 70, "Вхідне n = 0\nZigZag = 0\nVarint: 1 байт (0x00)", size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1, color=INK))
    f.append(fitbox(245, 425, 170, 70, "Вхідне n = -1\nZigZag = 1\nVarint: 1 байт (0x01)", size=11, fill=GREEN_BG, stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    f.append(fitbox(430, 425, 170, 70, "Вхідне n = 1\nZigZag = 2\nVarint: 1 байт (0x02)", size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1, color=INK))
    f.append(fitbox(615, 425, 170, 70, "Вхідне n = -2\nZigZag = 3\nVarint: 1 байт (0x03)", size=11, fill=GREEN_BG, stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    f.append(fitbox(800, 425, 150, 70, "Вхідне n = 2147483647\nZigZag = 4294967294\nVarint: 5 байтів", size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1, color=INK))

    render(os.path.join(IMG, "protobuf-varint-tlv.svg"), W, H, *f)


# ── 3. Порівняння: Десеріалізація Protobuf vs Zero-Copy Cap'n Proto ───────────
def fig_protobuf_vs_capnproto():
    W, H = 1000, 520
    f = []

    f.append(text(W / 2, 28, "Порівняння обробки: класичний парсинг (Protobuf) проти Zero-Copy (Cap'n Proto)", size=16, bold=True))

    # Ліва колонка: Protobuf (Традиційний парсинг)
    f.append(rect(40, 55, 435, 440, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(257, 85, "Protocol Buffers (Традиційний парсинг)", size=14, color=POS, bold=True))

    f.append(fitbox(60, 110, 395, 55, "Мережевий буфер (Wire Bytes)\nПотік стиснених тегів TLV і Varint", size=12, fill=PAD_BG, stroke="#94a3b8", sw=1.2, color=INK))

    f.append(arrow(257, 168, 257, 208, color=POS, sw=1.8))

    f.append(fitbox(60, 212, 395, 80, "Динамічне виділення пам'яті (Heap Allocations)\nmalloc() під кожне вкладене повідомлення,\nкопіювання байтів рядків у std::string/масиви", size=12, fill=RED_BG, stroke=POS, sw=1.3, color=POS, bold=True))

    f.append(arrow(257, 295, 257, 330, color=POS, sw=1.8))

    f.append(fitbox(60, 334, 395, 75, "Дерево C++ / Go об'єктів у купі\nЗвернення до полів через покажчики,\nкеш-промахи (Cache Misses) під час обходу", size=12, fill="#f8fafc", stroke="#94a3b8", sw=1.2, color=INK))

    f.append(fitbox(60, 425, 395, 55, "Ціна: витрати CPU на розкодування Varint,\nфрагментація купи та затримка виділення", size=11, fill=RED_BG, stroke=POS, sw=1.2, color=POS))

    # Права колонка: Cap'n Proto / FlatBuffers (Zero-Copy)
    f.append(rect(525, 55, 435, 440, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(742, 85, "Cap'n Proto / FlatBuffers (Zero-Copy)", size=14, color=FIELD, bold=True))

    f.append(fitbox(545, 110, 395, 55, "Мережевий буфер (Wire Bytes)\nДані вкладені з вирівнюванням слів (64-bit words),\nпокажчики кодують відносні зміщення", size=12, fill=PAD_BG, stroke="#94a3b8", sw=1.2, color=INK))

    # Розриваємо стрілку навколо тексту без перетину
    f.append(line(742, 168, 742, 186, color=FIELD, sw=2.0))
    f.append(text(742, 202, "Нуль тактів декодування (0 CPU cycles)", size=12, color=FIELD, bold=True))
    f.append(arrow(742, 216, 742, 238, color=FIELD, sw=2.0))

    f.append(fitbox(545, 242, 395, 70, "Безпосереднє читання з буфера (In-place Access)\nПряма арифметика покажчиків: base_ptr + offset\nЖодного виділення пам'яті в купі (0 mallocs)", size=12, fill=GREEN_BG, stroke=FIELD, sw=1.5, color=FIELD, bold=True))

    f.append(arrow(742, 314, 742, 350, color=FIELD, sw=1.8))

    f.append(fitbox(545, 354, 395, 60, "O(1) прямий доступ до будь-якого поля\nІдеальна локальність процесорного кешу L1/L2,\nчитання лише тих полів, які дійсно потрібні", size=12, fill="#f8fafc", stroke=FIELD, sw=1.2, color=INK))

    f.append(fitbox(545, 425, 395, 55, "Компроміс: трохи більший розмір у дроті\nчерез вирівнювання (без стиснення Varint)", size=11, fill=AMBER_BG, stroke=AMBER, sw=1.2, color=INK))

    render(os.path.join(IMG, "protobuf-vs-capnproto.svg"), W, H, *f)


def main():
    fig_rpc_flow()
    fig_protobuf_varint_tlv()
    fig_protobuf_vs_capnproto()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
