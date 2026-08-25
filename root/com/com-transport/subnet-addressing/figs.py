# -*- coding: utf-8 -*-
"""Фігури до теми «Адресація підмереж: маски, поділ і розрахунок».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import os
import sys

# Додаємо шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle,
    textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig1_subnet_mask_bitwise_and():
    """Фігура 1: Порозрядна операція І (AND) та поділ IPv4-адреси на префікс і хост."""
    w, h = 860, 400
    f = []

    # Заголовок фігури
    f.append(text(w / 2, 28, "Порозрядна операція І (AND) та поділ IPv4-адреси на префікс і хост",
                  size=16, bold=True, color=INK))

    # Контейнер для двійкового розрахунку
    f.append(rect(25, 50, 810, 195, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    # Підзаголовок прикладу
    f.append(text(45, 75, "Приклад: адреса 192.168.10.138 з маскою 255.255.255.192 (/26)",
                  size=13, bold=True, color=INK, anchor="start"))

    # Пояснення зон: 24 біти мережі, 2 біти підмережі, 6 бітів хоста
    # Октет 1..3: x=225..590 (24 біти)
    f.append(rect(225, 90, 365, 145, fill="#eff6ff", stroke=NEG, sw=1.0, rx=4))
    f.append(text(407, 105, "Базова мережа: 24 біти (192.168.10)", size=11, color=NEG, bold=True))

    # 2 біти підмережі: x=595..670
    f.append(rect(595, 90, 75, 145, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=4))
    f.append(text(632, 105, "Підмережа: 2 біти", size=10, color=FIELD, bold=True))

    # 6 бітів хоста: x=675..825
    f.append(rect(675, 90, 150, 145, fill="#fef2f2", stroke=POS, sw=1.0, rx=4))
    f.append(text(750, 105, "Хост: 6 бітів", size=11, color=POS, bold=True))

    # Рядок 1: IP-адреса
    f.append(text(45, 130, "IP-адреса (вузол):", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(205, 130, "192.168.10.138", size=12, color=MUTED, anchor="end"))
    f.append(text(407, 130, "11000000 . 10101000 . 00001010", size=13, color=INK))
    f.append(text(632, 130, "10", size=13, color=FIELD, bold=True))
    f.append(text(750, 130, "001010", size=13, color=POS, bold=True))

    # Оператор AND
    f.append(text(45, 155, "Побітова операція І:", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(205, 155, "AND (&)", size=12, color=MUTED, anchor="end"))

    # Рядок 2: Маска підмережі
    f.append(text(45, 180, "Маска підмережі:", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(205, 180, "255.255.255.192", size=12, color=MUTED, anchor="end"))
    f.append(text(407, 180, "11111111 . 11111111 . 11111111", size=13, color=INK))
    f.append(text(632, 180, "11", size=13, color=FIELD, bold=True))
    f.append(text(750, 180, "000000", size=13, color=MUTED, bold=True))

    # Розділова лінія розрахунку
    f.append(line(45, 195, 820, 195, color=LINE, sw=1.5))

    # Рядок 3: Мережева адреса
    f.append(text(45, 220, "Мережева адреса:", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(205, 220, "192.168.10.128", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(407, 220, "11000000 . 10101000 . 00001010", size=13, color=NEG, bold=True))
    f.append(text(632, 220, "10", size=13, color=NEG, bold=True))
    f.append(text(750, 220, "000000", size=13, color=MUTED, bold=True))

    # Нижні інформаційні картки (4 блоки)
    box1, _, _ = textbox(130, 310, "Мережева адреса\n192.168.10.128\nХостові біти: всі 0\nІдентифікатор у таблицях",
                         size=12, pad=8, fill="#eff6ff", stroke=NEG)
    f.append(box1)

    box2, _, _ = textbox(375, 310, "Діапазон хостів (вузлів)\n192.168.10.129 – .190\nХостові біти: 000001 – 111110\nПризначаються пристроям",
                         size=12, pad=8, fill="#f0fdf4", stroke=FIELD)
    f.append(box2)

    box3, _, _ = textbox(605, 310, "Широкомовна адреса\n192.168.10.191\nХостові біти: всі 1\nПакет для всіх вузлів",
                         size=12, pad=8, fill="#fef2f2", stroke=POS)
    f.append(box3)

    box4, _, _ = textbox(770, 310, "Ємність блоку\nВсього: 2⁶ = 64\nКорисних: 64−2 = 62\nКрок блоку: 64",
                         size=12, pad=8, fill=FILL, stroke=LINE)
    f.append(box4)

    render(os.path.join(IMG, "subnet-mask-bitwise-and.svg"), w, h, *f)


def fig2_vlsm_address_tree():
    """Фігура 2: Двійкове дерево простору адрес (VLSM) для блоку 10.0.0.0/24."""
    w, h = 880, 440
    f = []

    f.append(text(w / 2, 25, "Ієрархічне двійкове розбиття адресного простору (VLSM) для блоку 10.0.0.0/24",
                  size=16, bold=True, color=INK))

    # Корінь: 10.0.0.0/24
    box_root, _, _ = textbox(440, 65, "Базовий пул: 10.0.0.0/24 (256 адрес)",
                             size=13, pad=8, fill="#f8fafc", stroke=LINE, bold=True)
    f.append(box_root)

    # Стрілки від кореня до рівня 1
    f.append(arrow(340, 85, 230, 125, color=LINE))
    f.append(arrow(540, 85, 650, 125, color=LINE))

    # Рівень 1 (/25 - 128 адрес)
    box_l1_left, _, _ = textbox(230, 145, "Підблок: 10.0.0.0/25\n128 адрес (поділ далі)",
                                size=12, pad=6, fill="#eff6ff", stroke=NEG)
    f.append(box_l1_left)

    box_l1_right, _, _ = textbox(650, 145, "Відділ продажу: 10.0.0.128/25\n128 адрес (потреба: 100 хостів)\nДіапазон: .129 – .254 (62 вільно)",
                                 size=12, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    f.append(box_l1_right)

    # Стрілки від 10.0.0.0/25 до рівня 2
    f.append(arrow(170, 175, 120, 215, color=LINE))
    f.append(arrow(290, 175, 340, 215, color=LINE))

    # Рівень 2 (/26 - 64 адреси)
    box_l2_left, _, _ = textbox(120, 235, "Інженерія: 10.0.0.0/26\n64 адреси (потреба: 50 хостів)\nДіапазон: .1 – .62 (62 хости)",
                                size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    f.append(box_l2_left)

    box_l2_right, _, _ = textbox(340, 235, "Підблок: 10.0.0.64/26\n64 адреси (поділ далі)",
                                 size=11, pad=6, fill="#eff6ff", stroke=NEG)
    f.append(box_l2_right)

    # Стрілки від 10.0.0.64/26 до рівня 3
    f.append(arrow(290, 265, 235, 305, color=LINE))
    f.append(arrow(390, 265, 445, 305, color=LINE))

    # Рівень 3 (/27 - 32 адреси)
    box_l3_left, _, _ = textbox(235, 325, "Бухгалтерія: 10.0.0.64/27\n32 адреси (потреба: 20 хостів)\nДіапазон: .65 – .94 (30 хостів)",
                                size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True)
    f.append(box_l3_left)

    box_l3_right, _, _ = textbox(445, 325, "Підблок: 10.0.0.96/27\n32 адреси (поділ далі)",
                                 size=11, pad=6, fill="#eff6ff", stroke=NEG)
    f.append(box_l3_right)

    # Стрілки від 10.0.0.96/27 до рівня 4
    f.append(arrow(400, 355, 355, 390, color=LINE))
    f.append(arrow(490, 355, 545, 390, color=LINE))

    # Рівень 4 (/28 - 16 адрес)
    box_l4_left, _, _ = textbox(355, 405, "Сервери: 10.0.0.96/28 (16 IP)\nДіапазон: .97 – .110 (14 хостів)",
                                size=10, pad=5, fill="#f0fdf4", stroke=FIELD, bold=True)
    f.append(box_l4_left)

    box_l4_right, _, _ = textbox(545, 405, "Резерв / P2P: 10.0.0.112/28 (16 IP)\nМоже ділитися на /30 або /31 лінки",
                                 size=10, pad=5, fill="#fef2f2", stroke=POS)
    f.append(box_l4_right)

    # Підсумковий текстовий блок справа внизу
    f.append(rect(660, 275, 205, 140, fill="#fdf8e2", stroke="#d97706", sw=1.0, rx=6))
    f.append(text(762, 295, "Золоте правило VLSM", size=12, color="#b45309", bold=True))
    summary_lines = [
        "1. Сортувати потреби за",
        "   спаданням розміру.",
        "2. Виділяти блок 2ⁿ точно",
        "   під розмір із запасом.",
        "3. Вирівнювати початок за",
        "   кратною межею степеня 2.",
        "4. Жодного перекриття адрес."
    ]
    f.append(mtext(670, 315, summary_lines, size=10, color=INK, anchor="start", lh=1.25))

    render(os.path.join(IMG, "vlsm-address-tree.svg"), w, h, *f)


def fig3_point_to_point_30_vs_31():
    """Фігура 3: Канали точка-точка: маска /30 проти стандарту RFC 3021 /31."""
    w, h = 860, 360
    f = []

    f.append(text(w / 2, 28, "Канали «точка-точка»: класична маска /30 проти стандарту RFC 3021 (/31)",
                  size=16, bold=True, color=INK))

    # Ліва колонка: Традиційна маска /30
    f.append(rect(30, 55, 385, 285, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    f.append(text(222, 80, "Традиційна маска /30 (4 адреси на лінк)", size=14, bold=True, color=POS))

    # Вміст /30
    lines_30 = [
        "Блок: 198.51.100.0/30 (маска 255.255.255.252)",
        "-----------------------------------------------",
        "198.51.100.0  ->  Мережева адреса (НЕ використовується)",
        "198.51.100.1  ->  Інтерфейс Router A",
        "198.51.100.2  ->  Інтерфейс Router B",
        "198.51.100.3  ->  Широкомовна адреса (НЕ використовується)"
    ]
    f.append(mtext(45, 110, lines_30, size=11, color=INK, anchor="start", lh=1.35))

    # Марнування
    box_w30, _, _ = textbox(222, 260, "Ефективність: 50%\nВтрачається 2 із 4 адрес на кожному лінку!\nНа 1 000 P2P-з'єднань марнується 2 000 IP-адрес.",
                            size=11, pad=8, fill="#fee2e2", stroke=POS, color=POS, bold=True)
    f.append(box_w30)

    # Права колонка: RFC 3021 /31
    f.append(rect(445, 55, 385, 285, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(637, 80, "Сучасний стандарт RFC 3021 (/31)", size=14, bold=True, color=FIELD))

    # Вміст /31
    lines_31 = [
        "Блок: 198.51.100.0/31 (маска 255.255.255.254)",
        "-----------------------------------------------",
        "198.51.100.0  ->  Інтерфейс Router A (вузол 0)",
        "198.51.100.1  ->  Інтерфейс Router B (вузол 1)",
        "",
        "Широкомовлення та номер мережі відсутні:",
        "на каналі точка-точка є лише два учасники."
    ]
    f.append(mtext(460, 110, lines_31, size=11, color=INK, anchor="start", lh=1.35))

    # Ефективність
    box_w31, _, _ = textbox(637, 260, "Ефективність: 100%\nУсі 2 адреси використовуються інтерфейсами!\nЕкономія 50% адресного простору магістралей.",
                            size=11, pad=8, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True)
    f.append(box_w31)

    render(os.path.join(IMG, "point-to-point-30-vs-31.svg"), w, h, *f)


def fig4_enterprise_subnet_hierarchy():
    """Фігура 4: Ієрархічна адресація підприємства та агрегація на межах блоків."""
    w, h = 880, 420
    f = []

    f.append(text(w / 2, 25, "Ієрархічне планування адресного простору та агрегація маршрутів",
                  size=16, bold=True, color=INK))

    # Ліва частина: Ядро мережі та сумарний анонс
    box_core, _, _ = textbox(130, 110, "Ядро корпоративної\nмережі (Core Router)\nАнонс: 10.20.0.0/16",
                             size=12, pad=10, fill="#eff6ff", stroke=NEG, bold=True)
    f.append(box_core)

    # Стрілки від ядра до маршрутизаторів розподілу
    f.append(arrow(215, 95, 305, 95, color=LINE))
    f.append(arrow(215, 125, 305, 230, color=LINE))
    f.append(arrow(215, 145, 305, 335, color=LINE))

    # Рівень розподілу (Distribution Routers)
    box_dist1, _, _ = textbox(400, 95, "Будівля А (Офіс)\nПул: 10.20.0.0/20 (4096 IP)",
                              size=12, pad=8, fill="#f8fafc", stroke=LINE, bold=True)
    f.append(box_dist1)

    box_dist2, _, _ = textbox(400, 230, "Будівля Б (Виробництво)\nПул: 10.20.16.0/20 (4096 IP)",
                              size=12, pad=8, fill="#f8fafc", stroke=LINE, bold=True)
    f.append(box_dist2)

    box_dist3, _, _ = textbox(400, 335, "Дата-центр / Сервери\nПул: 10.20.32.0/20 (4096 IP)",
                              size=12, pad=8, fill="#f8fafc", stroke=LINE, bold=True)
    f.append(box_dist3)

    # Стрілки від Будівлі А до підмереж доступу (VLAN)
    f.append(arrow(495, 75, 565, 55, color=LINE))
    f.append(arrow(495, 90, 565, 95, color=LINE))
    f.append(arrow(495, 105, 565, 135, color=LINE))
    f.append(arrow(495, 120, 565, 175, color=LINE))

    # Підмережі доступу Будівлі А
    box_vlan10, _, _ = textbox(700, 55, "VLAN 10: Співробітники  -> 10.20.0.0/22 (1022 хости)",
                               size=11, pad=5, fill="#f0fdf4", stroke=FIELD)
    f.append(box_vlan10)

    box_vlan20, _, _ = textbox(700, 95, "VLAN 20: Корпоративний Wi-Fi -> 10.20.4.0/24 (254 хости)",
                               size=11, pad=5, fill="#f0fdf4", stroke=FIELD)
    f.append(box_vlan20)

    box_vlan30, _, _ = textbox(700, 135, "VLAN 30: Відеоспостереження  -> 10.20.5.0/25 (126 хостів)",
                               size=11, pad=5, fill="#f0fdf4", stroke=FIELD)
    f.append(box_vlan30)

    box_vlan99, _, _ = textbox(700, 175, "VLAN 99: Керування (OOBM)     -> 10.20.5.128/26 (62 хости)",
                               size=11, pad=5, fill="#fef2f2", stroke=POS)
    f.append(box_vlan99)

    # Стрілки від Будівлі Б
    f.append(arrow(495, 230, 565, 230, color=LINE))
    box_b_sub, _, _ = textbox(700, 230, "VLANs 110-140: Цехи та IoT -> 10.20.16.0/21 (2046 хостів)",
                              size=11, pad=5, fill="#f8fafc", stroke=LINE)
    f.append(box_b_sub)

    # Стрілки від ДЦ
    f.append(arrow(495, 335, 565, 335, color=LINE))
    box_dc_sub, _, _ = textbox(700, 335, "VLANs 200-250: Кластери та SAN -> 10.20.32.0/21 (2046 хостів)",
                               size=11, pad=5, fill="#f8fafc", stroke=LINE)
    f.append(box_dc_sub)

    # Нижня плашка про агрегацію
    f.append(rect(30, 375, 820, 30, fill="#fdf8e2", stroke="#d97706", sw=1.0, rx=4))
    f.append(text(440, 395, "Агрегація: кожна будівля згортає десятки VLAN в один маршрут /20, а ядро — в один анонс /16",
                  size=11, color="#b45309", bold=True))

    render(os.path.join(IMG, "enterprise-subnet-hierarchy.svg"), w, h, *f)


if __name__ == "__main__":
    fig1_subnet_mask_bitwise_and()
    fig2_vlsm_address_tree()
    fig3_point_to_point_30_vs_31()
    fig4_enterprise_subnet_hierarchy()
    print("Всі 4 фігури успішно згенеровано у", IMG)
