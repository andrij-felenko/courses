# -*- coding: utf-8 -*-
"""Фігури до теми «Фільтрація за джерелом: IGMPv3, MLDv2 і SSM».
Запуск: python figs.py → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння архітектур: ASM (з RP) проти SSM (пряме SPT) ──────────────
def fig_ssm_vs_asm_architecture():
    W, H = 840, 440
    frags = [
        text(W / 2, 28, "Порівняння моделей групової розсилки: класичний ASM проти SSM", size=16, bold=True),

        # Left panel: ASM (*, G)
        rect(25, 50, 385, 330, fill="#fdf8f8", stroke=POS, sw=1.5, rx=8),
        text(217, 75, "Any-Source Multicast (ASM, модель (*, G))", size=13, bold=True, color=POS),
        text(217, 94, "Джерело невідоме заздалегідь · Потрібна точка рандеву (RP)", size=10, color=MUTED, italic=True),

        # Source 1 (Legitimate)
        circle(70, 145, 20, fill="#ffffff", stroke=POS, sw=1.5),
        text(70, 150, "S1", size=12, bold=True),
        text(70, 178, "Джерело 1", size=10, color=MUTED),

        # Source 2 (Rogue / Spammer)
        circle(70, 225, 20, fill="#fee2e2", stroke=POS, sw=1.5),
        text(70, 230, "S2", size=12, bold=True, color=POS),
        text(70, 258, "Зловмисник", size=10, color=POS),

        # Rendezvous Point (RP)
        rect(170, 168, 85, 40, fill="#ffffff", stroke=POS, sw=1.8, rx=4),
        text(212, 193, "RP (Точка РВ)", size=11, bold=True),

        # Receivers
        circle(355, 145, 20, fill="#ffffff", stroke=POS, sw=1.5),
        text(355, 150, "R1", size=12, bold=True),
        text(355, 178, "Запит (*, G)", size=10, color=MUTED),

        circle(355, 225, 20, fill="#ffffff", stroke=POS, sw=1.5),
        text(355, 230, "R2", size=12, bold=True),
        text(355, 258, "Запит (*, G)", size=10, color=MUTED),

        # Links in ASM
        arrow(92, 145, 168, 180, color=POS, sw=1.4),
        arrow(92, 225, 168, 195, color=POS, sw=1.4),
        arrow(257, 180, 333, 150, color=POS, sw=1.4),
        arrow(257, 195, 333, 225, color=POS, sw=1.4),

        fitbox(35, 275, 365, 95,
               "• Клієнт підписується на групу (*, G), не знаючи джерела.\n"
               "• Трафік іде через спільне дерево (Shared Tree) і точку RP.\n"
               "• Будь-який вузол може надсилати спам/DoS у спільну групу G.\n"
               "• Складний механізм перемикання SPT Switchover та MSDP.",
               size=10, fill="#ffffff", stroke=LINE, sw=1),

        # Right panel: SSM (S, G)
        rect(430, 50, 385, 330, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8),
        text(622, 75, "Source-Specific Multicast (SSM, модель (S, G))", size=13, bold=True, color=FIELD),
        text(622, 94, "Джерело відоме заздалегідь · Пряме дерево найкоротшого шляху (SPT)", size=10, color=MUTED, italic=True),

        # Source 1 (Legitimate)
        circle(475, 145, 20, fill="#ffffff", stroke=FIELD, sw=1.5),
        text(475, 150, "S1", size=12, bold=True),
        text(475, 178, "Джерело S1", size=10, color=MUTED),

        # Source 2 (Rogue / Blocked)
        circle(475, 225, 20, fill="#fee2e2", stroke=MUTED, sw=1.5),
        text(475, 230, "S2", size=12, bold=True, color=MUTED),
        text(475, 258, "Заблоковано", size=10, color=POS),

        # Direct Router / SPT
        rect(575, 125, 95, 40, fill="#ffffff", stroke=FIELD, sw=1.8, rx=4),
        text(622, 150, "Маршрутизатор", size=10.5, bold=True),

        # Receivers
        circle(765, 145, 20, fill="#ffffff", stroke=FIELD, sw=1.5),
        text(765, 150, "R1", size=12, bold=True),
        text(765, 178, "Запит (S1, G)", size=10, color=FIELD),

        circle(765, 225, 20, fill="#ffffff", stroke=FIELD, sw=1.5),
        text(765, 230, "R2", size=12, bold=True),
        text(765, 258, "Запит (S1, G)", size=10, color=FIELD),

        # Links in SSM
        arrow(497, 145, 573, 145, color=FIELD, sw=1.8),
        line(497, 225, 565, 225, color=POS, sw=1.5, dash="4,4"),
        text(535, 215, "✕ Drop", size=11, color=POS, bold=True),
        arrow(672, 145, 743, 145, color=FIELD, sw=1.6),
        arrow(655, 167, 743, 225, color=FIELD, sw=1.6),

        fitbox(440, 275, 365, 95,
               "• Клієнт явно вказує (S, G): «Хочу потік G лише від джерела S1».\n"
               "• Дерево найкоротшого шляху (SPT) будується безпосередньо до S1.\n"
               "• Немає точки RP, спільного дерева (*, G) та протоколу MSDP.\n"
               "• Повний захист: спам від невідомих джерел відкидається на вході.",
               size=10, fill="#ffffff", stroke=LINE, sw=1),

        # Bottom summary box
        fitbox(25, 390, 790, 40,
               "SSM замінює відкриту багатоточкову модель на безпечну канальну модель: приймач сам обирає джерело,\n"
               "усуваючи потребу в глобальній координації адрес та складних протоколах пошуку джерел.",
               size=10.5, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-ssm-vs-asm-architecture.svg"), W, H, *frags)


# ── 2. Формат пакетів IGMPv3 та Group Record ─────────────────────────────────
def fig_igmpv3_mldv2_packet_structure():
    W, H = 840, 450
    frags = [
        text(W / 2, 26, "Структура повідомлення IGMPv3 Membership Report та Group Record", size=16, bold=True),

        # Top box: Overall IGMPv3 Report Header
        rect(40, 48, 760, 95, fill="#f8fafc", stroke=NEG, sw=1.6, rx=6),
        text(420, 68, "Заголовок повідомлення IGMPv3 Membership Report (Тип 0x22, RFC 3376)", size=12.5, bold=True, color=NEG),

        # Fields of Header
        rect(55, 82, 130, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(120, 102, "Type = 0x22", size=11, bold=True),
        text(120, 118, "(8 біт)", size=10, color=MUTED),

        rect(195, 82, 130, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(260, 102, "Reserved", size=11),
        text(260, 118, "(8 біт: 0x00)", size=10, color=MUTED),

        rect(335, 82, 170, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(420, 102, "Checksum", size=11, bold=True),
        text(420, 118, "(16 біт: контр. сума)", size=10, color=MUTED),

        rect(515, 82, 120, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(575, 102, "Reserved", size=11),
        text(575, 118, "(16 біт: 0x0000)", size=10, color=MUTED),

        rect(645, 82, 140, 48, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4),
        text(715, 102, "Nr of Records (M)", size=11, bold=True, color=FIELD),
        text(715, 118, "(16 біт: к-сть груп)", size=10, color=MUTED),

        # Middle Box: Group Record Format
        rect(40, 155, 760, 195, fill="#fdfbf7", stroke=FIELD, sw=1.6, rx=6),
        text(420, 176, "Формат структури Group Record (Запис про групу)", size=12.5, bold=True, color=FIELD),

        # Group Record Fields
        rect(55, 192, 145, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(127, 212, "Record Type (8 біт)", size=11, bold=True),
        text(127, 227, "Тип фільтрації (1..6)", size=9.5, color=FIELD),

        rect(210, 192, 140, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(280, 212, "Aux Data Len (8 біт)", size=11),
        text(280, 227, "Довжина даних = 0", size=9.5, color=MUTED),

        rect(360, 192, 165, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(442, 212, "Nr of Sources (N)", size=11, bold=True),
        text(442, 227, "16 біт: к-сть адрес S", size=9.5, color=MUTED),

        rect(535, 192, 250, 46, fill="#ffffff", stroke=NEG, sw=1.5, rx=4),
        text(660, 212, "Multicast Address (G)", size=11, bold=True, color=NEG),
        text(660, 227, "32 біти IPv4 (напр. 232.1.1.1)", size=9.5, color=MUTED),

        # Source IP Address Array
        rect(55, 248, 730, 88, fill="#ffffff", stroke=LINE, sw=1.2, rx=4),
        text(420, 268, "Список IP-адрес джерел: Source Address [1 .. N] (по 32 біти / 128 біт у MLDv2)", size=11, bold=True),

        rect(70, 280, 205, 45, fill="#f1f5f9", stroke=LINE, sw=1, rx=3),
        text(172, 298, "Source Address [1] (IP S1)", size=10.5),
        text(172, 314, "наприклад 198.51.100.10", size=9.5, color=MUTED),

        rect(290, 280, 205, 45, fill="#f1f5f9", stroke=LINE, sw=1, rx=3),
        text(392, 298, "Source Address [2] (IP S2)", size=10.5),
        text(392, 314, "наприклад 198.51.100.20", size=9.5, color=MUTED),

        rect(510, 280, 90, 45, fill="#f1f5f9", stroke=LINE, sw=1, rx=3),
        text(555, 307, ". . .", size=15, bold=True),

        rect(615, 280, 155, 45, fill="#f1f5f9", stroke=LINE, sw=1, rx=3),
        text(692, 298, "Source Address [N]", size=10.5),
        text(692, 314, "остання адреса списку", size=9.5, color=MUTED),

        # Bottom Record Types Reference
        fitbox(40, 360, 760, 80,
               "Типи записів (Record Type):\n"
               "• 1 = MODE_IS_INCLUDE (поточний стан INCLUDE)  |  2 = MODE_IS_EXCLUDE (поточний стан EXCLUDE)\n"
               "• 3 = CHANGE_TO_INCLUDE_MODE (зміна на IN)     |  4 = CHANGE_TO_EXCLUDE_MODE (зміна на EX)\n"
               "• 5 = ALLOW_NEW_SOURCES (додати нові джерела)  |  6 = BLOCK_OLD_SOURCES (вилучити джерела)",
               size=10, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-igmpv3-mldv2-packet-structure.svg"), W, H, *frags)


# ── 3. Скінченний автомат фільтрації джерел (INCLUDE vs EXCLUDE) ─────────────
def fig_filter_mode_fsm():
    W, H = 840, 440
    frags = [
        text(W / 2, 26, "Скінченний автомат фільтрації джерел на вузлі та агрегація на інтерфейсі", size=16, bold=True),

        # Left block: Socket States
        rect(30, 50, 235, 330, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8),
        text(147, 74, "Рівень сокетів додатків", size=12.5, bold=True, color=NEG),
        text(147, 92, "Кожен процес обирає свій фільтр", size=10, color=MUTED, italic=True),

        rect(45, 108, 205, 56, fill="#ffffff", stroke=FIELD, sw=1.3, rx=5),
        text(147, 126, "Сокет A (IPTV Плеєр)", size=11, bold=True, color=FIELD),
        text(147, 142, "Фільтр: INCLUDE {S1, S2}", size=10),
        text(147, 156, "Приймати лише S1 та S2", size=9.5, color=MUTED),

        rect(45, 172, 205, 56, fill="#ffffff", stroke=FIELD, sw=1.3, rx=5),
        text(147, 190, "Сокет B (Аналізатор)", size=11, bold=True, color=FIELD),
        text(147, 206, "Фільтр: INCLUDE {S2, S3}", size=10),
        text(147, 220, "Приймати лише S2 та S3", size=9.5, color=MUTED),

        rect(45, 236, 205, 56, fill="#ffffff", stroke=POS, sw=1.3, rx=5),
        text(147, 254, "Сокет C (ASM спадщина)", size=11, bold=True, color=POS),
        text(147, 270, "Фільтр: EXCLUDE {S4}", size=10),
        text(147, 284, "Приймати всіх, крім S4", size=9.5, color=MUTED),

        fitbox(45, 302, 205, 68,
               "Ядро ОС об'єднує сокети:\n"
               "якщо хоча б один сокет EXCLUDE,\n"
               "весь інтерфейс переходить в EX.",
               size=9.5, fill="#ffffff", stroke=LINE, sw=1),

        # Center block: Kernel Aggregation Logic
        rect(290, 50, 260, 330, fill="#fdfbf7", stroke=LINE, sw=1.5, rx=8),
        text(420, 74, "Агрегація в ядрі ОС", size=12.5, bold=True),
        text(420, 92, "Правила об'єднання станів", size=10, color=MUTED, italic=True),

        fitbox(305, 108, 230, 80,
               "1. Лише INCLUDE сокети:\n"
               "Режим інтерфейсу = INCLUDE\n"
               "Список джерел = S_A ∪ S_B\n"
               "{S1, S2} ∪ {S2, S3} = {S1, S2, S3}",
               size=10, fill="#ffffff", stroke=FIELD, sw=1.2),

        fitbox(305, 196, 230, 80,
               "2. Наявний EXCLUDE сокет:\n"
               "Режим інтерфейсу = EXCLUDE\n"
               "Список виключень = S_EX ∖ S_IN\n"
               "Інтерфейс приймає всіх, крім S4",
               size=10, fill="#ffffff", stroke=POS, sw=1.2),

        fitbox(305, 284, 230, 86,
               "Генерація повідомлень IGMPv3:\n"
               "Зміна списку → ALLOW / BLOCK\n"
               "Зміна режиму → TO_IN / TO_EX",
               size=9.5, fill="#ffffff", stroke=LINE, sw=1),

        # Right block: Router Port State
        rect(575, 50, 235, 330, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8),
        text(692, 74, "Стан порту маршрутизатора", size=12.5, bold=True, color=FIELD),
        text(692, 92, "Таймери джерел (Source Timers)", size=10, color=MUTED, italic=True),

        rect(590, 108, 205, 62, fill="#ffffff", stroke=FIELD, sw=1.3, rx=5),
        text(692, 126, "Група G: Режим INCLUDE", size=11, bold=True, color=FIELD),
        text(692, 143, "• Джерело S1: Timer = 260s", size=10),
        text(692, 158, "• Джерело S2: Timer = 260s", size=10),

        rect(590, 178, 205, 62, fill="#ffffff", stroke=POS, sw=1.3, rx=5),
        text(692, 196, "Група G: Режим EXCLUDE", size=11, bold=True, color=POS),
        text(692, 213, "• Group Timer = 260s", size=10),
        text(692, 228, "• Блоковано S4 (Timer = 260s)", size=10),

        fitbox(590, 248, 205, 122,
               "Маршрутизатор скидає таймери:\n"
               "при отриманні чергового звіту\n"
               "Membership Report.\n"
               "Якщо таймер джерела спливає,\n"
               "потік (S, G) обрізається через PIM.",
               size=9.5, fill="#ffffff", stroke=LINE, sw=1),

        # Arrows between blocks
        arrow(267, 136, 288, 136, color=NEG, sw=1.5),
        arrow(267, 236, 288, 236, color=NEG, sw=1.5),
        arrow(552, 136, 573, 136, color=FIELD, sw=1.5),
        arrow(552, 236, 573, 236, color=FIELD, sw=1.5),

        # Bottom summary box
        fitbox(30, 387, 780, 42,
               "Агрегація станів дозволяє ядру ОС і маршрутизатору точно відстежувати потреби багатьох процесів:\n"
               "у мережу передається лише математично необхідний мінімум запитів без надлишкової дуплікації трафіку.",
               size=10.5, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-filter-mode-fsm.svg"), W, H, *frags)


# ── 4. Побудова дерева найкоротшого шляху в PIM-SSM ───────────────────────────
def fig_pim_ssm_spt_build():
    W, H = 840, 430
    frags = [
        text(W / 2, 26, "Побудова дерева найкоротшого шляху (SPT) за протоколом PIM-SSM", size=16, bold=True),

        # Multicast Source
        rect(40, 155, 120, 75, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6),
        text(100, 180, "Джерело S", size=12.5, bold=True, color=FIELD),
        text(100, 198, "198.51.100.1", size=10.5, bold=True),
        text(100, 215, "Відеопотік / Фінанси", size=9.5, color=MUTED),

        # First-Hop Router (FHR)
        circle(240, 192, 26, fill="#ffffff", stroke=LINE, sw=1.8),
        text(240, 196, "FHR", size=12, bold=True),
        text(240, 232, "First-Hop Router", size=9.5, color=MUTED),

        # Core Router (Transit)
        circle(420, 192, 26, fill="#ffffff", stroke=LINE, sw=1.8),
        text(420, 196, "R_Core", size=12, bold=True),
        text(420, 232, "Транзитний роутер", size=9.5, color=MUTED),

        # Last-Hop Router (LHR)
        circle(600, 192, 26, fill="#ffffff", stroke=LINE, sw=1.8),
        text(600, 196, "LHR", size=12, bold=True),
        text(600, 232, "Last-Hop Router", size=9.5, color=MUTED),

        # Receiver Host
        rect(700, 155, 110, 75, fill="#ffffff", stroke=NEG, sw=1.8, rx=6),
        text(755, 180, "Отримувач", size=12.5, bold=True, color=NEG),
        text(755, 198, "192.0.2.50", size=10.5, bold=True),
        text(755, 215, "Клієнтський хост", size=9.5, color=MUTED),

        # Step 1: IGMPv3 Join from Receiver to LHR
        arrow(700, 172, 628, 172, color=NEG, sw=1.8),
        text(664, 162, "1. IGMPv3 INCLUDE (S, G)", size=10, bold=True, color=NEG),

        # Step 2: PIM Join (S, G) hop-by-hop from LHR to Core to FHR
        arrow(574, 178, 448, 178, color=POS, sw=1.8),
        text(511, 168, "2. PIM Join (S, G)", size=10, bold=True, color=POS),

        arrow(394, 178, 268, 178, color=POS, sw=1.8),
        text(331, 168, "3. PIM Join (S, G)", size=10, bold=True, color=POS),

        # Step 3: Direct Multicast Traffic from Source to Receiver down the SPT
        arrow(162, 205, 212, 205, color=FIELD, sw=2.2),
        arrow(268, 205, 392, 205, color=FIELD, sw=2.2),
        arrow(448, 205, 572, 205, color=FIELD, sw=2.2),
        arrow(628, 205, 698, 205, color=FIELD, sw=2.2),
        text(420, 258, "▼ 4. Прямий датаграмний потік (S, G) вниз по дереву SPT ▼", size=11, bold=True, color=FIELD),

        # Comparison / Steps Details Box
        fitbox(40, 275, 760, 98,
               "Алгоритм сигналізації PIM-SSM:\n"
               "1. Отримувач надсилає IGMPv3 Membership Report із записом MODE_IS_INCLUDE (S, G).\n"
               "2. Останній маршрутизатор (LHR) виконує RPF-перевірку до IP-адреси S і надсилає PIM Join (S, G) сусіду.\n"
               "3. Повідомлення Join поширюється вгору до першого маршрутизатора (FHR), формуючи стан (S, G) в таблицях mroute.\n"
               "4. Трафік тече виключно найкоротшим шляхом від S до отримувача без затримок і без участі Rendezvous Point.",
               size=10, fill="#ffffff", stroke=LINE, sw=1.2),

        # Bottom summary box
        fitbox(40, 385, 760, 38,
               "PIM-SSM скорочує затримку встановлення з'єднання до часу одного проходження сигналу (RTT),\n"
               "виключаючи складну фазу реєстрації в RP та усуваючи єдину точку відмови в топології мережі.",
               size=10.5, fill=FILL, stroke=LINE, sw=1.2)
    ]
    render(os.path.join(IMG, "fig-pim-ssm-spt-build.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_ssm_vs_asm_architecture()
    fig_igmpv3_mldv2_packet_structure()
    fig_filter_mode_fsm()
    fig_pim_ssm_spt_build()
    print("Всі фігури згенеровано успішно.")
