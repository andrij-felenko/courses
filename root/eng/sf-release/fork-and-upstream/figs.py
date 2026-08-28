# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Форк і апстрим: як не жити з вічним патчем»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_fork_divergence():
    """Фігура 1: Накопичення дивергенції, зсуву контексту та боргу злиття."""
    w, h = 820, 460
    f = []

    f.append(text(w / 2, 28, "Дивергенція форку та наростання боргу злиття (Merge Debt)", size=16, bold=True))

    # Лінія апстриму (Upstream Mainline)
    f.append(text(120, 75, "Upstream Mainline (RTOS / Linux Kernel)", size=13, bold=True, color=NEG, anchor="start"))
    f.append(line(80, 110, 740, 110, color=NEG, sw=3))

    u_commits = [
        (130, 110, "U1: v2.4"),
        (240, 110, "U2: CVE Fix"),
        (360, 110, "U3: Subsys API v2"),
        (480, 110, "U4: v2.5-rc1"),
        (600, 110, "U5: Driver refactor"),
        (710, 110, "U6: v2.5.0"),
    ]

    for cx, cy, label in u_commits:
        f.append(circle(cx, cy, 14, fill="#eaf0fd", stroke=NEG, sw=2.2))
        tb, _, _ = textbox(cx, cy - 30, label, size=11, pad=5, fill="#f0f4fc", stroke=NEG, bold=True)
        f.append(tb)

    # Точка форку
    f.append(arrow(130, 125, 180, 240, color=POS, sw=2.5))
    tb_fork, _, _ = textbox(135, 185, "Точка створення\nфорку (Fork Point)", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(tb_fork)

    # Лінія довгоживучого форку (Downstream Fork)
    f.append(text(210, 245, "Downstream Fork (Ізольований приватний форк продукту)", size=13, bold=True, color=POS, anchor="start"))
    f.append(line(180, 280, 740, 280, color=POS, sw=3))

    d_commits = [
        (180, 280, "D1: Custom Pinmux"),
        (300, 280, "D2: Vendor HAL Tweak"),
        (420, 280, "D3: In-Tree Eth Patch"),
        (540, 280, "D4: Scheduler Mod"),
        (670, 280, "D5: App Logic in Core"),
    ]

    for cx, cy, label in d_commits:
        f.append(circle(cx, cy, 14, fill="#fdecea", stroke=POS, sw=2.2))
        tb, _, _ = textbox(cx, cy + 32, label, size=11, pad=5, fill="#fff5f5", stroke=POS, bold=True)
        f.append(tb)

    # Зона розриву / зсуву контексту (Divergence Gap)
    f.append(line(360, 125, 420, 265, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(600, 125, 670, 265, color=POS, sw=2, dash="5,5"))
    f.append(arrow(710, 125, 670, 265, color=POS, sw=2.5))

    # Попереджувальний блок про злиття
    warn_text = "Спроба злиття через 18 місяців:\n• 340 конфліктів у 85 файлах ядра\n• Зсув архітектури підсистем (API drift)\n• Неможливість отримати безпекові латки"
    f.append(fitbox(480, 360, 310, 85, warn_text, size=11, pad=8, fill="#fdecea", stroke=POS, bold=False))

    # Висновок зліва
    cost_text = "Борг злиття (Merge Debt) зростає нелінійно:\nкожний локальний in-tree патч збільшує\nвартість супроводу кожної наступної версії."
    f.append(fitbox(50, 360, 390, 85, cost_text, size=11, pad=8, fill="#f4f6f8", stroke=LINE, bold=False))

    render(os.path.join(OUT_DIR, "fork-divergence-and-merge-debt.svg"), w, h, *f)


def fig_upstream_first():
    """Фігура 2: Замкнене коло життєвого циклу Upstream First."""
    w, h = 840, 460
    f = []

    f.append(text(w / 2, 26, "Замкнений контур життєвого циклу Upstream First", size=16, bold=True))

    boxes_data = [
        (160, 95, 230, 75, "1. Виявлення потреби\nВиправлення бага або новий\nдрайвер у внутрішньому проєкті", "#f4f6f8", LINE),
        (580, 95, 230, 75, "2. Ізоляція від специфіки\nВиокремлення узагальненої\nчастини, очищення від комерційної таємниці", "#f4f6f8", LINE),
        (700, 240, 220, 75, "3. Відправка в Upstream\nPull Request / поштовий список\nПідпис DCO (Signed-off-by)", "#eaf0fd", NEG),
        (580, 385, 230, 75, "4. Код-рев'ю та злиття\nПрийняття в upstream/main\nОтримання фіксованого commit hash", "#eaf0fd", NEG),
        (160, 385, 230, 75, "5. Backport у продукт\nCherry-pick у гілку релізу з тегом\nUpstream-commit: <hash>", "#eafaf1", FIELD),
        (40, 240, 220, 75, "6. Автоматичне списання\nПід час планового rebase патч\nвидаляється без конфліктів", "#eafaf1", FIELD),
    ]

    for cx, cy, bw, bh, txt, fill_col, strk_col in boxes_data:
        f.append(fitbox(cx - bw / 2, cy - bh / 2, bw, bh, txt, size=11, pad=6, fill=fill_col, stroke=strk_col, bold=False))

    # Стрілки по колу
    f.append(arrow(275, 95, 465, 95, color=INK, sw=2))
    f.append(arrow(670, 133, 700, 202, color=INK, sw=2))
    f.append(arrow(700, 278, 670, 347, color=NEG, sw=2))
    f.append(arrow(465, 385, 275, 385, color=FIELD, sw=2))
    f.append(arrow(70, 347, 40, 278, color=FIELD, sw=2))
    f.append(arrow(40, 202, 70, 133, color=INK, sw=2))

    # Центр діаграми — економічний сенс
    center_text = "ЕКОНОМІЧНИЙ ПРИНЦИП:\nНайдишевша для підтримки лінія коду —\nце код, прийнятий і тестований апстримом."
    f.append(fitbox(280, 190, 280, 100, center_text, size=11, pad=8, fill="#fff9db", stroke="#f59f00", bold=True))

    render(os.path.join(OUT_DIR, "upstream-first-lifecycle.svg"), w, h, *f)


def fig_isolated_architecture():
    """Фігура 3: Багатошарова архітектура ізоляції без модифікації вихідного коду апстриму."""
    w, h = 820, 480
    f = []

    f.append(text(w / 2, 26, "Анатомія архітектурної ізоляції локальних модифікацій", size=16, bold=True))

    layers = [
        (60, 65, 700, 60, "Рівень застосунку (Application & Business Logic)\nВласні алгоритми, мережеві протоколи, бізнес-правила системи", "#f4f6f8", LINE),
        (60, 140, 700, 65, "Шар адаптації та фасаду (Glue / Shim Abstraction Layer)\nСтабільний API для застосунку; приховує зміни версій ядра/RTOS", "#eaf0fd", NEG),
        (60, 220, 700, 65, "Позадеревні драйвери (Out-of-Tree Drivers & Modules)\nДрайвери датчиків, кастомних шин (Zephyr modules, Linux loadable modules)", "#eafaf1", FIELD),
        (60, 300, 700, 60, "Апаратна конфігурація (Device Tree Overlays & Board Definitions)\n.overlay файли, Kconfig дефконфіги специфічної плати без правок у dts вендора", "#fff9db", "#f59f00"),
        (60, 375, 700, 65, "Чистий апстрим (Clean Upstream RTOS / Linux Baseline)\nНезмінний оригінальний код ядра; 0 змінених рядків у дереві апстриму", "#fdecea", POS),
    ]

    for lx, ly, lw, lh, ltxt, lfill, lstroke in layers:
        f.append(fitbox(lx, ly, lw, lh, ltxt, size=12, pad=6, fill=lfill, stroke=lstroke, bold=False))

    # Стрілки взаємодії між шарами
    f.append(arrow(410, 125, 410, 140, color=LINE, sw=1.8))
    f.append(arrow(410, 205, 410, 220, color=NEG, sw=1.8))
    f.append(arrow(410, 285, 410, 300, color=FIELD, sw=1.8))
    f.append(arrow(410, 360, 410, 375, color=POS, sw=1.8))

    # Червоний бар'єр ізоляції
    f.append(line(45, 367, 775, 367, color=POS, sw=2.5, dash="6,4"))
    tb_barrier, _, _ = textbox(w / 2, 458, "МЕЖА ІЗОЛЯЦІЇ: Жоден комміт продукту не модифікує файли всередині апстриму", size=11, pad=5, fill="#fff5f5", stroke=POS, bold=True)
    f.append(tb_barrier)

    render(os.path.join(OUT_DIR, "isolated-architecture-layers.svg"), w, h, *f)


def fig_rebase_vs_merge():
    """Фігура 4: Порівняння рекурсивних злиттів (Merge Spaghetti) та лінійного ребейзу."""
    w, h = 840, 460
    f = []

    f.append(text(w / 2, 26, "Стратегії супроводу: рекурсивні злиття проти лінійного ребейзу", size=16, bold=True))

    # Ліва колонка: Merge Tangle
    f.append(fitbox(40, 60, 360, 380, "", fill="#fbfbfc", stroke=POS, sw=1.5))
    f.append(text(220, 85, "Рекурсивні злиття (Merge Tangle)", size=13, bold=True, color=POS))

    f.append(text(70, 120, "Upstream", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(130, 115, 370, 115, color=NEG, sw=2))
    f.append(circle(160, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(circle(250, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(circle(340, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))

    f.append(text(70, 200, "Product", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(130, 195, 370, 195, color=POS, sw=2))
    f.append(circle(160, 195, 8, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(circle(210, 195, 8, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(circle(290, 195, 8, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(circle(360, 195, 8, fill="#fdecea", stroke=POS, sw=1.5))

    # Перехресні стрілки злиття
    f.append(arrow(160, 123, 210, 187, color=MUTED, sw=1.5))
    f.append(arrow(250, 123, 290, 187, color=MUTED, sw=1.5))
    f.append(arrow(340, 123, 360, 187, color=MUTED, sw=1.5))

    m_drawbacks = "НАСЛІДКИ MERGE:\n• Зміни апстриму розмиваються у merge-комітах\n• Неможливо провести git bisect\n• Патчі не підлягають ізольованому аудиту"
    f.append(fitbox(60, 260, 320, 110, m_drawbacks, size=11, pad=8, fill="#fff5f5", stroke=POS, bold=False))

    # Права колонка: Linear Rebase
    f.append(fitbox(440, 60, 360, 380, "", fill="#fbfbfc", stroke=FIELD, sw=1.5))
    f.append(text(620, 85, "Лінійний ребейз (Rebase onto Tag)", size=13, bold=True, color=FIELD))

    f.append(text(460, 120, "v2.5.0", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(510, 115, 770, 115, color=NEG, sw=2))
    f.append(circle(530, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(circle(590, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(circle(650, 115, 8, fill="#eaf0fd", stroke=NEG, sw=1.5))

    f.append(text(460, 200, "Patches", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(650, 195, 770, 195, color=FIELD, sw=2))
    f.append(arrow(650, 123, 650, 187, color=FIELD, sw=1.8))
    f.append(circle(680, 195, 8, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(circle(720, 195, 8, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(circle(760, 195, 8, fill="#eafaf1", stroke=FIELD, sw=1.5))

    r_benefits = "ПЕРЕВАГИ REBASE:\n• Чиста лінійна історія поверх релізного тегу\n• Кожен локальний патч залишається автономним\n• Працює автоматизований git bisect"
    f.append(fitbox(460, 260, 320, 110, r_benefits, size=11, pad=8, fill="#f0fff4", stroke=FIELD, bold=False))

    render(os.path.join(OUT_DIR, "rebase-vs-merge-history.svg"), w, h, *f)


if __name__ == "__main__":
    fig_fork_divergence()
    fig_upstream_first()
    fig_isolated_architecture()
    fig_rebase_vs_merge()
    print("All figures successfully generated in", OUT_DIR)
