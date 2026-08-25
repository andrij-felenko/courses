# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

LIGHT = ["#fdecea", "#eef4ff", "#eafaf0", "#f3eafa", "#fff9db"]


def fig_concept():
    W, H = 840, 430
    p = []

    p.append(line(420, 48, 420, 320, color="#d8dde3", sw=1.3, dash="5 4"))

    # ── ліворуч: логічна ілюзія ──
    p.append(text(210, 68, "Логічна картина (погляд програми)", size=13, color=NEG, bold=True))

    p.append(text(120, 102, "Вузол 0 (Потік 0)", size=11, color=INK, bold=True))
    p.append(text(300, 102, "Вузол 1 (Потік 1)", size=11, color=INK, bold=True))
    p.append(arrow(120, 110, 160, 142, color=MUTED, sw=1.5))
    p.append(arrow(300, 110, 260, 142, color=MUTED, sw=1.5))

    p.append(rect(60, 145, 300, 64, fill=LIGHT[1], stroke=NEG, sw=1.6, rx=4))
    p.append(text(210, 172, "Єдиний плаский адресний простір", size=12, color=INK, bold=True))
    p.append(text(210, 194, "0x0000_0000 ... 0xFFFF_FFFF", size=11, color=MUTED))

    p.append(text(210, 240, "Звичайні вказівники (*ptr) і структури:", size=11.5, color=INK))
    p.append(text(210, 262, "потік на вузлі 1 читає пам'ять вузла 0 напряму", size=11.5, color=INK))
    p.append(text(210, 292, "одиниця адресації = БАЙТ / ВКАЗІВНИК", size=11, color=NEG, bold=True))

    # ── праворуч: фізична реальність ──
    p.append(text(630, 68, "Фізична реальність (вузли кластера)", size=13, color=POS, bold=True))

    # Вузол 0
    p.append(rect(450, 102, 160, 86, fill=LIGHT[0], stroke=POS, sw=1.3, rx=4))
    p.append(text(530, 124, "Вузол 0", size=11.5, color=POS, bold=True))
    p.append(text(530, 144, "ЦП 0 + Локальна RAM 0", size=10.5, color=INK))
    p.append(text(530, 166, "Своя фізична шина", size=10, color=MUTED))

    # Вузол 1
    p.append(rect(650, 102, 160, 86, fill=LIGHT[0], stroke=POS, sw=1.3, rx=4))
    p.append(text(730, 124, "Вузол 1", size=11.5, color=POS, bold=True))
    p.append(text(730, 144, "ЦП 1 + Локальна RAM 1", size=10.5, color=INK))
    p.append(text(730, 166, "Своя фізична шина", size=10, color=MUTED))

    # Мережа
    p.append(rect(480, 222, 300, 44, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    p.append(text(630, 248, "Мережне з'єднання (Ethernet / InfiniBand)", size=11, color=INK, bold=True))

    p.append(arrow(530, 188, 530, 222, color=LINE, sw=1.4))
    p.append(arrow(730, 188, 730, 222, color=LINE, sw=1.4))

    p.append(text(630, 292, "фізично роздільна пам'ять без спільної шини", size=11, color=POS, bold=True))

    # ── висновок ──
    p.append(fitbox(50, 338, 740, 72,
                    "Розподілена спільна пам'ять (DSM) створює програмну або апаратну ілюзію\n"
                    "єдиного адресного простору над фізично незалежними серверами,\n"
                    "транслюючи звернення до пам'яті в мережні повідомлення.",
                    size=12, fill="#ffffff", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "concept.svg"), W, H, *p,
           title="Концепція DSM: логічна ілюзія проти фізичної реальності")


def fig_page_fault_flow():
    W, H = 860, 490
    p = []

    p.append(text(430, 34, "Життєвий цикл перехоплення сторінкової помилки у Software DSM", size=13, color=INK, bold=True))

    # 8 кроків послідовності
    steps = [
        ("1. Доступ", "ЦП виконує *ptr = 42\nна захищеній сторінці", LIGHT[1], NEG),
        ("2. MMU", "Апаратний збій\nPage Fault (права)", LIGHT[0], POS),
        ("3. Ядро ОС", "Формування сигналу\nSIGSEGV (si_addr)", LIGHT[4], LINE),
        ("4. Обробник", "sigaction перехоплює\nадресу віддаленої сторінки", LIGHT[3], "#8e44ad"),
        ("5. Мережа", "Запит сторінки 4KB\nу віддаленого власника", LIGHT[1], NEG),
        ("6. Відповідь", "Отримання даних\nчерез TCP/IP або RDMA", LIGHT[2], FIELD),
        ("7. mprotect", "Зняття захисту\nPROT_READ | PROT_WRITE", LIGHT[2], FIELD),
        ("8. Повтор", "ЦП прозоро повторює\nкоманду без помилки", LIGHT[2], POS)
    ]

    bx, by = 45, 76
    bw, bh = 175, 78
    dx, dy = 195, 106

    coords = [
        (bx, by),
        (bx + dx, by),
        (bx + 2 * dx, by),
        (bx + 3 * dx, by),
        (bx + 3 * dx, by + dy),
        (bx + 2 * dx, by + dy),
        (bx + dx, by + dy),
        (bx, by + dy)
    ]

    for i, (title_s, desc_s, bg_c, strk_c) in enumerate(steps):
        cx, cy = coords[i]
        p.append(rect(cx, cy, bw, bh, fill=bg_c, stroke=strk_c, sw=1.5, rx=4))
        p.append(text(cx + bw / 2, cy + 22, title_s, size=11, color=strk_c, bold=True))
        p.append(mtext(cx + bw / 2, cy + 44, desc_s, size=10, color=INK, lh=1.25))

    # Стрілки між кроками
    # 0 -> 1 -> 2 -> 3
    p.append(arrow(coords[0][0] + bw, coords[0][1] + bh / 2, coords[1][0], coords[1][1] + bh / 2, color=LINE, sw=1.6))
    p.append(arrow(coords[1][0] + bw, coords[1][1] + bh / 2, coords[2][0], coords[2][1] + bh / 2, color=LINE, sw=1.6))
    p.append(arrow(coords[2][0] + bw, coords[2][1] + bh / 2, coords[3][0], coords[3][1] + bh / 2, color=LINE, sw=1.6))
    # 3 -> 4 (вниз)
    p.append(arrow(coords[3][0] + bw / 2, coords[3][1] + bh, coords[4][0] + bw / 2, coords[4][1], color=LINE, sw=1.6))
    # 4 -> 5 -> 6 -> 7 (вліво)
    p.append(arrow(coords[4][0], coords[4][1] + bh / 2, coords[5][0] + bw, coords[5][1] + bh / 2, color=LINE, sw=1.6))
    p.append(arrow(coords[5][0], coords[5][1] + bh / 2, coords[6][0] + bw, coords[6][1] + bh / 2, color=LINE, sw=1.6))
    p.append(arrow(coords[6][0], coords[6][1] + bh / 2, coords[7][0] + bw, coords[7][1] + bh / 2, color=LINE, sw=1.6))

    # Підсумок унизу
    p.append(fitbox(45, 306, 765, 70,
                    "Для прикладної програми весь ланцюжок від MMU до отримання мережного пакета\n"
                    "виглядає як звичайна затримка читання або запису в пам'ять.\n"
                    "Програма не містить жодного рядка з кодом сокетів чи серіалізації.",
                    size=12, fill="#ffffff", stroke=POS, color=INK))

    render(os.path.join(OUT, "page-fault-flow.svg"), W, H, *p,
           title="Послідовність обробки сторінкової помилки в DSM")


def fig_consistency_models():
    W, H = 860, 440
    p = []

    p.append(line(430, 48, 430, 330, color="#d8dde3", sw=1.3, dash="5 4"))

    # ── ліворуч: послідовна узгодженість ──
    p.append(text(215, 68, "Послідовна узгодженість (SC)", size=13, color=POS, bold=True))
    p.append(text(215, 90, "Кожен запис синхронізується негайно", size=11, color=MUTED))

    # Стрічка вузла 0
    p.append(text(75, 130, "Вузол 0", size=11, color=INK, bold=True))
    p.append(line(125, 126, 385, 126, color="#c7ccd2", sw=1.2))

    # Стрічка вузла 1
    p.append(text(75, 220, "Вузол 1", size=11, color=INK, bold=True))
    p.append(line(125, 216, 385, 216, color="#c7ccd2", sw=1.2))

    # Запис 1
    p.append(rect(145, 116, 55, 20, fill=LIGHT[0], stroke=POS, sw=1.2, rx=2))
    p.append(text(172, 130, "W(x)=1", size=10, color=POS, bold=True))
    p.append(arrow(172, 136, 215, 216, color=POS, sw=1.3))
    p.append(text(220, 175, "Інвалідація", size=9.5, color=POS))

    # Запис 2
    p.append(rect(275, 116, 55, 20, fill=LIGHT[0], stroke=POS, sw=1.2, rx=2))
    p.append(text(302, 130, "W(x)=2", size=10, color=POS, bold=True))
    p.append(arrow(302, 136, 345, 216, color=POS, sw=1.3))
    p.append(text(350, 175, "Інвалідація", size=9.5, color=POS))

    p.append(text(215, 275, "Мережний трафік на КОЖНУ інструкцію запису:", size=11, color=INK))
    p.append(text(215, 296, "висока латентність мережі блокує ЦП", size=11, color=POS, bold=True))

    # ── праворуч: узгодженість за звільненням ──
    p.append(text(645, 68, "Узгодженість за звільненням (RC)", size=13, color=FIELD, bold=True))
    p.append(text(645, 90, "Синхронізація лише на бар'єрах", size=11, color=MUTED))

    # Стрічка вузла 0
    p.append(text(485, 130, "Вузол 0", size=11, color=INK, bold=True))
    p.append(line(535, 126, 795, 126, color="#c7ccd2", sw=1.2))

    # Стрічка вузла 1
    p.append(text(485, 220, "Вузол 1", size=11, color=INK, bold=True))
    p.append(line(535, 216, 795, 216, color="#c7ccd2", sw=1.2))

    # Локальні записи
    p.append(rect(545, 116, 45, 20, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=2))
    p.append(text(567, 130, "Acquire", size=9.5, color=FIELD, bold=True))

    p.append(rect(600, 116, 42, 20, fill=LIGHT[1], stroke=NEG, sw=1.1, rx=2))
    p.append(text(621, 130, "W(x)=1", size=9.5, color=INK))

    p.append(rect(648, 116, 42, 20, fill=LIGHT[1], stroke=NEG, sw=1.1, rx=2))
    p.append(text(669, 130, "W(x)=2", size=9.5, color=INK))

    p.append(rect(700, 116, 45, 20, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=2))
    p.append(text(722, 130, "Release", size=9.5, color=FIELD, bold=True))

    p.append(arrow(722, 136, 755, 216, color=FIELD, sw=1.4))
    p.append(text(768, 175, "Diff / Пакет", size=9.5, color=FIELD, bold=True))

    p.append(rect(740, 216, 45, 20, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=2))
    p.append(text(762, 230, "Acquire", size=9.5, color=FIELD, bold=True))

    p.append(text(645, 275, "Локальні записи виконуються зі швидкістю RAM;", size=11, color=INK))
    p.append(text(645, 296, "мережні повідомлення об'єднуються у пачку", size=11, color=FIELD, bold=True))

    # ── висновок ──
    p.append(fitbox(50, 350, 760, 68,
                    "Послідовна узгодженість робить мережу частиною кожного запису.\n"
                    "Узгодженість за звільненням (RC) відкладає обмін до межі критичної секції,\n"
                    "зменшуючи кількість мережних транзакцій на кілька порядків.",
                    size=12, fill="#ffffff", stroke=LINE, color=INK))

    render(os.path.join(OUT, "consistency-models.svg"), W, H, *p,
           title="Порівняння послідовної узгодженості та узгодженості за звільненням")


def fig_twin_diff():
    W, H = 860, 480
    p = []

    p.append(text(430, 32, "Механізм Twin-and-Diff для розв'язання False Sharing на сторінках 4KB", size=13, color=INK, bold=True))

    # Сторінка 4KB
    p.append(rect(80, 64, 700, 52, fill=LIGHT[1], stroke=NEG, sw=1.4, rx=4))
    p.append(text(430, 84, "Спільна віртуальна сторінка (4096 байтів)", size=11.5, color=NEG, bold=True))

    # Змінна A та Змінна B
    p.append(rect(95, 92, 180, 20, fill=LIGHT[0], stroke=POS, sw=1.2, rx=2))
    p.append(text(185, 106, "Змінна A (зміщує Вузол 1)", size=10, color=POS, bold=True))

    p.append(rect(585, 92, 180, 20, fill=LIGHT[2], stroke=FIELD, sw=1.2, rx=2))
    p.append(text(675, 106, "Змінна B (зміщує Вузол 2)", size=10, color=FIELD, bold=True))

    # Вузол 1 ліворуч
    p.append(rect(60, 142, 340, 160, fill="#ffffff", stroke=POS, sw=1.4, rx=4))
    p.append(text(230, 164, "Вузол 1: створення Twin і запис у змінну A", size=11, color=POS, bold=True))

    p.append(rect(80, 180, 140, 38, fill=LIGHT[4], stroke=LINE, sw=1.1, rx=3))
    p.append(text(150, 198, "Twin 1 (копія 4KB)", size=10.5, color=INK))
    p.append(text(150, 212, "стан до запису", size=9.5, color=MUTED))

    p.append(rect(240, 180, 140, 38, fill=LIGHT[0], stroke=POS, sw=1.1, rx=3))
    p.append(text(310, 198, "Брудна сторінка", size=10.5, color=POS, bold=True))
    p.append(text(310, 212, "змінено байти 0..7", size=9.5, color=POS))

    p.append(rect(80, 238, 300, 48, fill=LIGHT[0], stroke=POS, sw=1.2, rx=3))
    p.append(text(230, 258, "Обчислення різниці (Diff 1):", size=10.5, color=POS, bold=True))
    p.append(text(230, 276, "[зсув 0, довжина 8, нові байти A]", size=10, color=INK))

    # Вузол 2 праворуч
    p.append(rect(460, 142, 340, 160, fill="#ffffff", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(630, 164, "Вузол 2: створення Twin і запис у змінну B", size=11, color=FIELD, bold=True))

    p.append(rect(480, 180, 140, 38, fill=LIGHT[4], stroke=LINE, sw=1.1, rx=3))
    p.append(text(550, 198, "Twin 2 (копія 4KB)", size=10.5, color=INK))
    p.append(text(550, 212, "стан до запису", size=9.5, color=MUTED))

    p.append(rect(640, 180, 140, 38, fill=LIGHT[2], stroke=FIELD, sw=1.1, rx=3))
    p.append(text(710, 198, "Брудна сторінка", size=10.5, color=FIELD, bold=True))
    p.append(text(710, 212, "змінено байти 2048..2055", size=9.5, color=FIELD))

    p.append(rect(480, 238, 300, 48, fill=LIGHT[2], stroke=FIELD, sw=1.2, rx=3))
    p.append(text(630, 258, "Обчислення різниці (Diff 2):", size=10.5, color=FIELD, bold=True))
    p.append(text(630, 276, "[зсув 2048, довжина 8, нові байти B]", size=10, color=INK))

    # Злиття в центрі
    p.append(arrow(230, 302, 360, 332, color=POS, sw=1.5))
    p.append(arrow(630, 302, 500, 332, color=FIELD, sw=1.5))

    p.append(rect(200, 334, 460, 52, fill=LIGHT[3], stroke="#8e44ad", sw=1.4, rx=4))
    p.append(text(430, 354, "Злиття змін (Diff Merge)", size=11.5, color="#8e44ad", bold=True))
    p.append(text(430, 374, "Накладання неперетинних зсувів: відсутність конфліктів", size=10.5, color=INK))

    # Підсумок
    p.append(fitbox(50, 404, 760, 58,
                    "Twin-and-Diff дозволяє кільком вузлам одночасно писати в одну сторінку 4KB,\n"
                    "передаючи лише малі пачки змінених байтів замість перекидання всієї сторінки.",
                    size=11.5, fill="#ffffff", stroke=LINE, color=INK))

    render(os.path.join(OUT, "twin-diff.svg"), W, H, *p,
           title="Принцип роботи протоколу Twin-and-Diff")


def fig_memory_tiers():
    W, H = 840, 380
    p = []

    p.append(text(420, 32, "Спектр затримок доступу до пам'яті: від кешу ЦП до мережного DSM", size=13, color=INK, bold=True))

    tiers = [
        ("L1 / L2 Кеш", "1 – 4 нс", "Кремній ядра", LIGHT[2], FIELD),
        ("L3 Кеш (LLC)", "10 – 15 нс", "Спільний на кристалі", LIGHT[2], FIELD),
        ("Локальна RAM", "60 – 80 нс", "Контролер пам'яті DDR5", LIGHT[1], NEG),
        ("CXL.mem Пул", "200 – 250 нс", "PCIe 5.0/6.0 комутатор", LIGHT[4], "#d35400"),
        ("RDMA мережа", "1 – 2 мкс", "InfiniBand / RoCE NIC", LIGHT[3], "#8e44ad"),
        ("Software DSM", "50 – 100 мкс", "TCP/IP стек + Page Fault", LIGHT[0], POS)
    ]

    bx, by = 60, 68
    bw, bh = 110, 200
    gap = 12

    for i, (name_s, lat_s, tech_s, bg_c, strk_c) in enumerate(tiers):
        x = bx + i * (bw + gap)
        # Висота графічного стовпчика для візуалізації логарифмічного масштабу
        bar_h = 30 + i * 28
        bar_y = by + (bh - bar_h)

        p.append(rect(x, by, bw, bh, fill="#fafbfc", stroke="#e1e4e8", sw=1.1, rx=4))
        p.append(rect(x + 10, bar_y, bw - 20, bar_h, fill=bg_c, stroke=strk_c, sw=1.3, rx=3))

        p.append(text(x + bw / 2, by + 24, name_s, size=11, color=INK, bold=True))
        p.append(text(x + bw / 2, bar_y - 10, lat_s, size=12, color=strk_c, bold=True))
        p.append(mtext(x + bw / 2, by + bh - 24, tech_s, size=9.5, color=MUTED, lh=1.2))

    # Стрілка знизу
    p.append(arrow(70, 290, 770, 290, color=POS, sw=1.8))
    p.append(text(420, 310, "Зростання латентності у 100 000 разів (5 порядків величини)", size=11, color=POS, bold=True))

    p.append(fitbox(50, 332, 740, 36,
                    "CXL та RDMA скорочують прірву між локальною RAM та віддаленими пулами пам'яті.",
                    size=11.5, fill="#ffffff", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "memory-tiers.svg"), W, H, *p,
           title="Ієрархія затримок доступу до пам'яті")


if __name__ == "__main__":
    fig_concept()
    fig_page_fault_flow()
    fig_consistency_models()
    fig_twin_diff()
    fig_memory_tiers()
    print("All figures generated successfully.")
