# -*- coding: utf-8 -*-
"""Фігури до теми «BGP: протокол зв'язку між автономними системами».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Ієрархія Автономних Систем, транзит та піринг ─────────────────────────
def fig_as_hierarchy():
    W, H = 780, 420
    f = [text(W / 2, 30, "Структура інтернету: Автономні Системи (AS), транзит і піринг", size=16, bold=True)]

    # Tier 1 Backbone ASes (Top)
    f.append(rect(150, 60, 220, 80, fill="#eef3ff", stroke=NEG, sw=2, rx=10))
    f.append(text(260, 95, "AS 100 (Tier-1 ISP)", size=14, bold=True, color=NEG))
    f.append(text(260, 118, "Глобальний транзит", size=11, color=MUTED))

    f.append(rect(410, 60, 220, 80, fill="#eef3ff", stroke=NEG, sw=2, rx=10))
    f.append(text(520, 95, "AS 200 (Tier-1 ISP)", size=14, bold=True, color=NEG))
    f.append(text(520, 118, "Глобальний транзит", size=11, color=MUTED))

    # Settlement-free Peering between Tier-1
    f.append(line(370, 100, 410, 100, color=NEG, sw=2, dash="4,4"))
    f.append(text(390, 48, "Безкоштовний піринг", size=9, color=NEG, italic=True))

    # Regional / Tier 2 ASes (Middle)
    f.append(rect(80, 200, 200, 75, fill="#fff7e6", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(180, 230, "AS 300 (Регіональний ISP)", size=12, bold=True))
    f.append(text(180, 252, "Клієнт AS 100", size=10, color=MUTED))

    f.append(rect(500, 200, 200, 75, fill="#fff7e6", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(600, 230, "AS 400 (Регіональний ISP)", size=12, bold=True))
    f.append(text(600, 252, "Клієнт AS 200", size=10, color=MUTED))

    # Transit links (Tier 1 -> Tier 2)
    f.append(arrow(220, 200, 240, 140, color=INK, sw=1.6))
    f.append(text(210, 170, "Транзит ($)", size=10, color=INK, bold=True))

    f.append(arrow(580, 200, 540, 140, color=INK, sw=1.6))
    f.append(text(580, 170, "Транзит ($)", size=10, color=INK, bold=True))

    # IXP / Peering between Tier 2
    f.append(rect(280, 290, 220, 50, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(390, 312, "IXP (Точка обміну трафіком)", size=12, bold=True, color=FIELD))
    f.append(text(390, 328, "Прямий піринг без платні", size=10, color=MUTED))

    f.append(line(180, 275, 280, 305, color=FIELD, sw=1.6))
    f.append(line(600, 275, 500, 305, color=FIELD, sw=1.6))

    # Bottom summary box
    f.append(fitbox(90, 355, 600, 48,
                    "Транзит ($): провайдер вищого рівня роздає всі маршрути інтернету за гроші.\n"
                    "Піринг (IXP): сусіди обмінюються лише власними трафіком безкоштовно через BGP.",
                    size=11, fill=BG, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "as-hierarchy.svg"), W, H, *f)


# ── 2. Механізм Path Vector та виявлення петель ──────────────────────────────
def fig_path_vector_loop():
    W, H = 780, 380
    f = [text(W / 2, 30, "Вектор шляху (Path Vector) та виявлення петель в AS-PATH", size=16, bold=True)]

    # AS 65001 (Origin)
    f.append(rect(50, 90, 150, 70, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    f.append(text(125, 118, "AS 65001", size=14, bold=True, color=FIELD))
    f.append(text(125, 140, "Префікс: 1.1.1.0/24", size=10, color=MUTED))

    # AS 65002
    f.append(rect(310, 90, 160, 70, fill="#fff7e6", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(390, 118, "AS 65002", size=14, bold=True))
    f.append(text(390, 140, "Додає себе в AS-PATH", size=10, color=MUTED))

    # AS 65003
    f.append(rect(570, 90, 160, 70, fill="#fff7e6", stroke=MUTED, sw=1.6, rx=8))
    f.append(text(650, 118, "AS 65003", size=14, bold=True))
    f.append(text(650, 140, "Додає себе в AS-PATH", size=10, color=MUTED))

    # Forward propagation arrows with AS-PATH content
    f.append(arrow(200, 125, 310, 125, color=INK, sw=1.8))
    f.append(text(255, 112, "AS-PATH: [65001]", size=9, color=INK, bold=True))

    f.append(arrow(470, 125, 570, 125, color=INK, sw=1.8))
    f.append(text(520, 112, "AS-PATH: [65002, 65001]", size=9, color=INK, bold=True))

    # Loop back path to AS 65001
    f.append(line(650, 160, 650, 240, color=POS, sw=1.8, dash="5,5"))
    f.append(line(650, 240, 125, 240, color=POS, sw=1.8, dash="5,5"))
    f.append(arrow(125, 240, 125, 160, color=POS, sw=1.8))

    f.append(fitbox(200, 205, 380, 32,
                    "Спроба повернути оголошення джерелу:\nAS-PATH: [65003, 65002, 65001]",
                    size=10, fill="#fdf2f2", stroke=POS, sw=1.2, color=POS))

    # Rejection logic at AS 65001
    f.append(fitbox(60, 275, 660, 75,
                    "Перевірка в AS 65001: свій номер (65001) МІСТИТЬСЯ в отриманому AS-PATH!\n"
                    "→ Маршрут ВІДКИДАЄТЬСЯ (Loop Prevention). Без повної карти інтернету петля убита миттєво.",
                    size=12, fill="#fdf2f2", stroke=POS, sw=1.6, bold=True))

    render(os.path.join(IMG, "path-vector-loop.svg"), W, H, *f)


# ── 3. Конвеєр вибору найкращого маршруту (BGP Decision Process) ────────────
def fig_bgp_attributes_decision():
    W, H = 780, 440
    f = [text(W / 2, 28, "Конвеєр вибору найкращого маршруту BGP (Decision Process)", size=16, bold=True)]

    steps = [
        ("1. Weight", "Локальне Cisco-значення на роутері", "Найвище"),
        ("2. Local Preference", "Пріоритет виходу з AS (LocalPref)", "Найвище (за замовч. 100)"),
        ("3. Local Origin", "Локально згенерований маршрут", "Власний > отриманий"),
        ("4. AS-PATH length", "Кількість автономних систем у шляху", "Найкоротший список"),
        ("5. Origin Type", "Походження маршруту", "IGP < EGP < Incomplete"),
        ("6. MED", "Multi-Exit Discriminator для сусіда", "Найнижче значення"),
        ("7. Peer Type", "Тип BGP-сесії", "eBGP > iBGP"),
        ("8. IGP Metric", "Метрика внутрішньої маршрутизації до Next-Hop", "Найнижча метрика")
    ]

    y_start = 60
    box_h = 36
    for i, (title, desc, rule) in enumerate(steps):
        y = y_start + i * 42
        # Number box
        f.append(rect(60, y, 170, box_h, fill="#eef3ff", stroke=NEG, sw=1.4, rx=4))
        f.append(text(145, y + 22, title, size=11, bold=True, color=NEG))

        # Description box
        f.append(rect(240, y, 300, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=4))
        f.append(text(390, y + 22, desc, size=11, color=INK))

        # Rule box
        f.append(rect(550, y, 170, box_h, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=4))
        f.append(text(635, y + 22, rule, size=11, bold=True, color=FIELD))

        if i < len(steps) - 1:
            f.append(arrow(145, y + box_h, 145, y + 42, color=MUTED, sw=1.2))

    f.append(text(W / 2, 418, "Маршрутизатор порівнює атрибути покроково зверху вниз, доки не знайде єдиного переможця.",
                  size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "bgp-attributes-decision.svg"), W, H, *f)


# ── 4. eBGP проти iBGP ───────────────────────────────────────────────────────
def fig_ibgp_vs_ebgp():
    W, H = 780, 400
    f = [text(W / 2, 28, "Зв'язок eBGP між AS та iBGP всередині автономної системи", size=16, bold=True)]

    # AS 64500 Container
    f.append(rect(40, 60, 320, 260, fill="#fafafa", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(200, 85, "AS 64500 (Власна мережа)", size=13, bold=True, color=INK))

    # Routers inside AS 64500
    f.append(circle(100, 160, 28, fill="#fff7e6", stroke=MUTED, sw=1.6))
    f.append(text(100, 165, "R1 (eBGP)", size=10, bold=True))

    f.append(circle(300, 160, 28, fill="#fff7e6", stroke=MUTED, sw=1.6))
    f.append(text(300, 165, "R2 (eBGP)", size=10, bold=True))

    f.append(circle(200, 260, 28, fill="#eef3ff", stroke=NEG, sw=1.6))
    f.append(text(200, 265, "R3 (iBGP)", size=10, bold=True))

    # iBGP Mesh inside AS 64500
    f.append(line(128, 160, 272, 160, color=NEG, sw=1.6, dash="3,3"))
    f.append(line(120, 180, 180, 240, color=NEG, sw=1.6, dash="3,3"))
    f.append(line(280, 180, 220, 240, color=NEG, sw=1.6, dash="3,3"))
    f.append(text(200, 150, "iBGP full-mesh", size=9, color=NEG, italic=True))

    # AS 64501 (External Peer 1)
    f.append(rect(440, 70, 140, 100, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(510, 110, "AS 64501", size=13, bold=True, color=FIELD))
    f.append(text(510, 132, "Провайдер A", size=10, color=MUTED))

    # AS 64502 (External Peer 2)
    f.append(rect(600, 200, 140, 100, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(670, 240, "AS 64502", size=13, bold=True, color=FIELD))
    f.append(text(670, 262, "Провайдер B", size=10, color=MUTED))

    # eBGP sessions (Solid lines across borders)
    f.append(arrow(440, 120, 128, 150, color=FIELD, sw=2))
    f.append(text(300, 112, "eBGP сесія", size=10, color=FIELD, bold=True))

    f.append(arrow(600, 230, 328, 175, color=FIELD, sw=2))
    f.append(text(460, 215, "eBGP сесія", size=10, color=FIELD, bold=True))

    # Bottom summary box
    f.append(fitbox(50, 335, 680, 50,
                    "eBGP: між різними AS (міняє AS-PATH, перевіряє петлі, TTL=1 за замовчуванням).\n"
                    "iBGP: всередині однієї AS (НЕ міняє AS-PATH, не розповсюджує маршрути від одного iBGP іншому).",
                    size=11, fill=BG, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, "ibgp-vs-ebgp.svg"), W, H, *f)


if __name__ == "__main__":
    fig_as_hierarchy()
    fig_path_vector_loop()
    fig_bgp_attributes_decision()
    fig_ibgp_vs_ebgp()
    print("Всі 4 фігури успішно згенеровано у ./img/")
