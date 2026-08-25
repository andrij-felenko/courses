# -*- coding: utf-8 -*-
"""Фігури до теми «VLAN та транкінг».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Логічна ізоляція пристроїв у VLAN на одному комутаторі ───────────────
def fig_vlan_isolation():
    """Показує фізичний комутатор, розділений на два логічні VLAN (VLAN 10 та VLAN 20).
    Рамки групують вузли кожного VLAN. Стрілки показують дозволений обмін усередині
    VLAN та заблоковану L2-взаємодію між VLAN без маршрутизатора."""
    W, H = 820, 440
    f = [text(W / 2, 28, "Розділення фізичного комутатора на логічні VLAN", size=16, bold=True)]

    # Фізичний комутатор в центрі
    sw, sw_w, sw_h = textbox(W / 2, 210, "Фізичний L2-комутатор\n(Таблиця MAC розбита за VLAN ID)",
                             size=13, bold=True, fill="#f4f6f8", stroke=INK, min_w=220)
    f.append(sw)

    # Ліва зона: VLAN 10 (Sales)
    v10_box = rect(25, 60, 315, 310, fill="#fdecea", stroke=POS, sw=1.6, rx=8)
    f.append(v10_box)
    f.append(text(182, 85, "VLAN 10: Бухгалтерія (Sales)", size=13, bold=True, color=POS))
    f.append(text(182, 103, "Підмережа 192.168.10.0/24", size=11, color=MUTED))

    h1, h1_w, h1_h = textbox(100, 150, "Вузол A\n192.168.10.2", size=11, fill=BG, stroke=POS)
    h2, h2_w, h2_h = textbox(260, 150, "Вузол B\n192.168.10.3", size=11, fill=BG, stroke=POS)
    f.append(h1)
    f.append(h2)

    # Стрілка внутрішнього обміну VLAN 10
    f.append(line(150, 150, 210, 150, color=POS, sw=1.8, dash="4,4"))
    f.append(text(182, 138, "L2-трафік", size=10, color=POS, bold=True))

    # З'єднання з комутатором
    f.append(arrow(100, 185, 295, 200, color=POS, sw=1.5))
    f.append(arrow(260, 185, 295, 220, color=POS, sw=1.5))
    f.append(text(182, 275, "Порти 1-2: Access VLAN 10", size=11, color=POS, bold=True))

    # Права зона: VLAN 20 (Engineering)
    v20_box = rect(480, 60, 315, 310, fill="#eef3ff", stroke=NEG, sw=1.6, rx=8)
    f.append(v20_box)
    f.append(text(637, 85, "VLAN 20: Розробка (Dev)", size=13, bold=True, color=NEG))
    f.append(text(637, 103, "Підмережа 192.168.20.0/24", size=11, color=MUTED))

    h3, h3_w, h3_h = textbox(555, 150, "Вузол C\n192.168.20.2", size=11, fill=BG, stroke=NEG)
    h4, h4_w, h4_h = textbox(715, 150, "Вузол D\n192.168.20.3", size=11, fill=BG, stroke=NEG)
    f.append(h3)
    f.append(h4)

    # Стрілка внутрішнього обміну VLAN 20
    f.append(line(605, 150, 665, 150, color=NEG, sw=1.8, dash="4,4"))
    f.append(text(637, 138, "L2-трафік", size=10, color=NEG, bold=True))

    # З'єднання з комутатором
    f.append(arrow(555, 185, 525, 200, color=NEG, sw=1.5))
    f.append(arrow(715, 185, 525, 220, color=NEG, sw=1.5))
    f.append(text(637, 275, "Порти 3-4: Access VLAN 20", size=11, color=NEG, bold=True))

    # Бар'єр ізоляції між VLAN під комутатором (лінія розбита, щоб не перетинати плашку)
    f.append(line(W / 2, 260, W / 2, 305, color=POS, sw=2, dash="3,3"))
    f.append(rect(W / 2 - 90, 310, 180, 26, fill="#fff0f0", stroke=POS, sw=1.2))
    f.append(text(W / 2, 327, "Прямий L2-доступ заблоковано", size=10, bold=True, color=POS))
    f.append(line(W / 2, 340, W / 2, 375, color=POS, sw=2, dash="3,3"))

    f.append(text(W / 2, 415, "Кадри VLAN 10 не потрапляють у VLAN 20 на канальному рівні без маршрутизатора.",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "vlan-isolation.svg"), W, H, *f)


# ── 2. Передача кадрів через транковий канал ────────────────────────────────
def fig_trunk_8021q():
    """Схема проходження кадру через транковий порт IEEE 802.1Q між двома комутаторами:
    вхід немаркованого кадру на Access-порт -> додавання тегу 802.1Q (VID=10) ->
    передача через Trunk -> зняття тегу на виході з Access-порту другого комутатора."""
    W, H = 800, 420
    f = [text(W / 2, 28, "Передача кадрів через транковий канал IEEE 802.1Q", size=16, bold=True)]

    # Комутатор 1
    sw1, _, _ = textbox(170, 160, "Комутатор А\n(Switch 1)", size=13, bold=True, fill="#f4f6f8", stroke=INK, min_w=150)
    f.append(sw1)

    # Комутатор 2
    sw2, _, _ = textbox(630, 160, "Комутатор Б\n(Switch 2)", size=13, bold=True, fill="#f4f6f8", stroke=INK, min_w=150)
    f.append(sw2)

    # Транкова лінія між ними
    f.append(line(245, 160, 555, 160, color=FIELD, sw=3.5))
    f.append(rect(340, 142, 120, 36, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(400, 158, "Trunk Link", size=12, bold=True, color=FIELD))
    f.append(text(400, 172, "IEEE 802.1Q (VLAN 10, 20)", size=9, color=MUTED))

    # Крок 1: Вхід у Switch 1
    f.append(arrow(40, 160, 95, 160, color=POS, sw=1.8))
    f.append(fitbox(20, 200, 150, 45, "Крок 1: Кадр без тегу\n(Вузол A, VLAN 10)", size=10, fill="#fdecea", stroke=POS))

    # Крок 2: Додавання тегу 802.1Q
    f.append(fitbox(265, 80, 150, 48, "Крок 2: Тегування\nTPID=0x8100, VID=10\n[Tag + Header]", size=10, fill="#fff9e6", stroke="#d97706"))
    f.append(arrow(170, 120, 300, 105, color="#d97706", sw=1.5))

    # Крок 3: Передача через Trunk
    f.append(arrow(340, 160, 460, 160, color=FIELD, sw=2))

    # Крок 4: Зняття тегу на Switch 2
    f.append(fitbox(505, 80, 150, 48, "Крок 3: Зняття тегу\nОчищення 802.1Q\nперед видачею", size=10, fill="#fff9e6", stroke="#d97706"))
    f.append(arrow(630, 120, 560, 105, color="#d97706", sw=1.5))

    # Вихід до Вузла B
    f.append(arrow(705, 160, 760, 160, color=POS, sw=1.8))
    f.append(fitbox(640, 200, 150, 45, "Крок 4: Кадр без тегу\n(Вузол B, VLAN 10)", size=10, fill="#fdecea", stroke=POS))

    # Нижня схема порталів
    f.append(text(170, 270, "Порт 1: Access (VLAN 10)\nПорт 24: Trunk (802.1Q)", size=11, color=INK, bold=True))
    f.append(text(630, 270, "Порт 24: Trunk (802.1Q)\nПорт 1: Access (VLAN 10)", size=11, color=INK, bold=True))

    f.append(text(W / 2, 395, "Транк передає марковані кадри. Кінцеві пристрої отримують звичайні зняті кадри.",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "trunk-8021q.svg"), W, H, *f)


# ── 3. Структура заголовка IEEE 802.1Q ──────────────────────────────────────
def fig_frame_structure_8021q():
    """Порівняння звичайного Ethernet II кадру та кадру з 4-байтовим тегом IEEE 802.1Q.
    Деталізація полів 802.1Q Tag: TPID (16 біт), PCP (3 біти), DEI (1 біт), VID (12 біт)."""
    W, H = 820, 450
    f = [text(W / 2, 28, "Структура заголовка IEEE 802.1Q у кадрі Ethernet II", size=16, bold=True)]

    # 1. Звичайний Ethernet II кадр (1518 байт max)
    f.append(text(45, 65, "Звичайний кадр Ethernet II:", size=12, bold=True, anchor="start", color=INK))
    f.append(rect(45, 75, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(85, 97, "Dst MAC\n(6B)", size=10))

    f.append(rect(125, 75, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(165, 97, "Src MAC\n(6B)", size=10))

    f.append(rect(205, 75, 100, 36, fill="#eafaf0", stroke=FIELD))
    f.append(text(255, 97, "EtherType\n(2B)", size=10, bold=True, color=FIELD))

    f.append(rect(305, 75, 340, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(475, 97, "Payload (Корисні дані: 46 - 1500 байт)", size=11))

    f.append(rect(645, 75, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(685, 97, "FCS / CRC\n(4B)", size=10))
    f.append(text(765, 97, "1518 B max", size=10, color=MUTED, bold=True))

    # 2. Маркований кадр 802.1Q (1522 байт max)
    f.append(text(45, 150, "Маркований кадр 802.1Q (IEEE 802.3ac):", size=12, bold=True, anchor="start", color=POS))
    f.append(rect(45, 160, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(85, 182, "Dst MAC\n(6B)", size=10))

    f.append(rect(125, 160, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(165, 182, "Src MAC\n(6B)", size=10))

    # 802.1Q Tag (вставка 4 байти)
    f.append(rect(205, 160, 140, 36, fill="#fff9e6", stroke="#d97706", sw=2))
    f.append(text(275, 182, "802.1Q Tag (4 Bytes)", size=11, bold=True, color="#d97706"))

    f.append(rect(345, 160, 90, 36, fill="#eafaf0", stroke=FIELD))
    f.append(text(390, 182, "EtherType\n(2B)", size=10, bold=True, color=FIELD))

    f.append(rect(435, 160, 210, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(540, 182, "Payload (46 - 1500 B)", size=11))

    f.append(rect(645, 160, 80, 36, fill="#f4f6f8", stroke=LINE))
    f.append(text(685, 182, "FCS / CRC\n(4B)", size=10))
    f.append(text(765, 182, "1522 B max", size=10, color=POS, bold=True))

    # Стрілки розгортки тегу
    f.append(line(205, 196, 120, 250, color="#d97706", sw=1.5, dash="3,3"))
    f.append(line(345, 196, 700, 250, color="#d97706", sw=1.5, dash="3,3"))

    # 3. Деталізація полів 802.1Q Tag
    f.append(rect(120, 250, 580, 130, fill="#fffdfa", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(410, 270, "Детальна структура 4-байтового тегу 802.1Q:", size=12, bold=True, color="#d97706"))

    # TPID (16 біт)
    f.append(rect(140, 290, 170, 50, fill="#fdecea", stroke=POS))
    f.append(text(225, 312, "TPID (16 біт)", size=11, bold=True, color=POS))
    f.append(text(225, 330, "0x8100 (ідентифікатор тегу)", size=9, color=MUTED))

    # PCP (3 біти)
    f.append(rect(320, 290, 90, 50, fill="#eef3ff", stroke=NEG))
    f.append(text(365, 312, "PCP (3b)", size=11, bold=True, color=NEG))
    f.append(text(365, 330, "Пріоритет (0-7)", size=9, color=MUTED))

    # DEI (1 біт)
    f.append(rect(420, 290, 70, 50, fill="#eafaf0", stroke=FIELD))
    f.append(text(455, 312, "DEI (1b)", size=11, bold=True, color=FIELD))
    f.append(text(455, 330, "Drop Elig.", size=9, color=MUTED))

    # VID (12 біт)
    f.append(rect(500, 290, 180, 50, fill="#fef3c7", stroke="#d97706", sw=1.8))
    f.append(text(590, 312, "VID (12 біт)", size=12, bold=True, color="#b45309"))
    f.append(text(590, 330, "VLAN ID (0 - 4095)", size=10, bold=True, color="#b45309"))

    f.append(text(W / 2, 425, "Вставка 802.1Q розширює максимальний розмір кадру Ethernet з 1518 до 1522 байтів.",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, "frame-structure-8021q.svg"), W, H, *f)


if __name__ == "__main__":
    fig_vlan_isolation()
    fig_trunk_8021q()
    fig_frame_structure_8021q()
    print("Згенеровано 3 фігури у ./img/")
