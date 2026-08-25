# -*- coding: utf-8 -*-
"""Фігури теми «Кворуми та безлідерна реплікація». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Кольори для діаграм
GREEN_F = "#e8f8f0"
GREEN_B = "#27ae60"
BLUE_F  = "#eaf2fd"
BLUE_B  = "#2457d6"
AMBER_F = "#fef9e7"
AMBER_B = "#d35400"
RED_F   = "#fdecea"
RED_B   = "#c0392b"
GRAY_F  = "#f4f6f8"
GRAY_B  = "#6b7280"


# ── 1. quorum-overlap: перетин кворуму запису та читання ─────────────────────
def fig_quorum_overlap():
    W, H = 960, 360
    f = []

    # Заголовок / пояснення зон
    f.append(text(W / 2, 40, "Гарантований перетин множин: R + W > N (N = 5, W = 3, R = 3)", size=16, bold=True))

    # П'ять вузлів у ряд
    nodes = [
        ("Вузол 1", "v2 (новий)", BLUE_F, BLUE_B),
        ("Вузол 2", "v2 (новий)", BLUE_F, BLUE_B),
        ("Вузол 3", "v2 (новий)", GREEN_F, GREEN_B),  # Перетин!
        ("Вузол 4", "v1 (старий)", AMBER_F, AMBER_B),
        ("Вузол 5", "v1 (старий)", AMBER_F, AMBER_B),
    ]

    nw, nh = 140, 90
    y_node = 140
    xs = [60 + i * 175 for i in range(5)]

    for i, (name, val, fill, stroke) in enumerate(nodes):
        cx = xs[i] + nw / 2
        cy = y_node + nh / 2
        f.append(rect(xs[i], y_node, nw, nh, fill=fill, stroke=stroke, sw=2, rx=8))
        f.append(text(cx, y_node + 32, name, size=15, bold=True, color=INK))
        f.append(text(cx, y_node + 65, val, size=13, bold=True, color=stroke))

    # Дужка / рамка кворуму запису W=3 (Вузли 1, 2, 3)
    w_x, w_y, w_w, w_h = xs[0] - 10, y_node - 45, 175 * 2 + nw + 20, 28
    f.append(rect(w_x, w_y, w_w, w_h, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=6))
    f.append(text(w_x + w_w / 2, w_y + 19, "Кворум запису W = 3 (вузли 1, 2, 3 отримали v2)", size=13, bold=True, color=BLUE_B))

    # Дужка / рамка кворуму читання R=3 (Вузли 3, 4, 5)
    r_x, r_y, r_w, r_h = xs[2] - 10, y_node + nh + 18, 175 * 2 + nw + 20, 28
    f.append(rect(r_x, r_y, r_w, r_h, fill=AMBER_F, stroke=AMBER_B, sw=1.5, rx=6))
    f.append(text(r_x + r_w / 2, r_y + 19, "Кворум читання R = 3 (вузли 3, 4, 5 опитано)", size=13, bold=True, color=AMBER_B))

    # Підсвічування вузла перетину (Вузол 3)
    f.append(rect(xs[2] - 4, y_node - 4, nw + 8, nh + 8, fill="none", stroke=GREEN_B, sw=3, rx=10))
    f.append(text(xs[2] + nw / 2, y_node + nh + 75, "Вузол 3 належить обом кворумам (|W ∩ R| ≥ 1)", size=14, bold=True, color=GREEN_B))
    f.append(text(xs[2] + nw / 2, y_node + nh + 95, "Читач бачить версії {v2, v1, v1} і обирає найсвіжішу v2", size=13, color=MUTED))

    render(out("quorum-overlap.svg"), W, H, *f,
           title="Перетин кворумів запису та читання за формулою R + W > N")


# ── 2. leaderless-flow: координація запису та читання з Read-Repair ─────────
def fig_leaderless_flow():
    W, H = 980, 420
    f = []

    f.append(text(W / 2, 35, "Безлідерна реплікація: запис (W = 2) та читання з Read-Repair (R = 2) при N = 3", size=16, bold=True))

    # Ліва колонка: Запис W = 2
    f.append(rect(40, 65, 430, 330, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(255, 95, "Операція запису (W = 2)", size=15, bold=True, color=BLUE_B))

    # Учасники запису
    f.append(rect(60, 120, 90, 40, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=5))
    f.append(text(105, 145, "Клієнт", size=13, bold=True))

    f.append(rect(180, 120, 100, 40, fill=AMBER_F, stroke=AMBER_B, sw=1.5, rx=5))
    f.append(text(230, 145, "Координатор", size=13, bold=True))

    f.append(rect(310, 115, 140, 25, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(380, 132, "Репліка A (v2 OK)", size=11, bold=True))

    f.append(rect(310, 150, 140, 25, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(380, 167, "Репліка B (v2 OK)", size=11, bold=True))

    f.append(rect(310, 185, 140, 25, fill=RED_F, stroke=RED_B, sw=1, rx=4))
    f.append(text(380, 202, "Репліка C (повільна/збій)", size=11, bold=True))

    # Стрілки запису
    f.append(arrow(150, 140, 180, 140, color=BLUE_B))
    f.append(arrow(280, 130, 310, 127, color=GREEN_B))
    f.append(arrow(280, 140, 310, 162, color=GREEN_B))
    f.append(arrow(280, 150, 310, 197, color=RED_B))

    f.append(text(255, 250, "1. Координатор надсилає v2 усім 3 реплікам", size=12, anchor="middle"))
    f.append(text(255, 275, "2. Отримує 2 успішні відповіді (W = 2)", size=12, anchor="middle"))
    f.append(text(255, 300, "3. Відповідає клієнту «Успіх»", size=12, bold=True, color=GREEN_B, anchor="middle"))
    f.append(text(255, 330, "Репліка C відстає, маючи старий стан v1", size=12, color=MUTED, italic=True, anchor="middle"))
    f.append(text(255, 360, "Запис завершено успішно без очікування репліки C", size=12, color=INK, anchor="middle"))

    # Права колонка: Читання R = 2 + Read Repair
    f.append(rect(510, 65, 430, 330, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(725, 95, "Читання та Read-Repair (R = 2)", size=15, bold=True, color=GREEN_B))

    # Учасники читання
    f.append(rect(530, 120, 90, 40, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=5))
    f.append(text(575, 145, "Клієнт", size=13, bold=True))

    f.append(rect(650, 120, 100, 40, fill=AMBER_F, stroke=AMBER_B, sw=1.5, rx=5))
    f.append(text(700, 145, "Координатор", size=13, bold=True))

    f.append(rect(780, 115, 140, 25, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(850, 132, "Репліка B (віддає v2)", size=11, bold=True))

    f.append(rect(780, 150, 140, 25, fill=AMBER_F, stroke=AMBER_B, sw=1, rx=4))
    f.append(text(850, 167, "Репліка C (віддає v1)", size=11, bold=True))

    # Стрілки читання
    f.append(arrow(620, 140, 650, 140, color=BLUE_B))
    f.append(arrow(650, 130, 780, 127, color=GREEN_B))
    f.append(arrow(650, 145, 780, 162, color=AMBER_B))

    f.append(text(725, 230, "1. Координатор опитує репліки B і C (R = 2)", size=12, anchor="middle"))
    f.append(text(725, 255, "2. B повертає v2, C повертає застарілу v1", size=12, anchor="middle"))
    f.append(text(725, 280, "3. Клієнту повертається v2 (max версія)", size=12, bold=True, color=BLUE_B, anchor="middle"))

    # Read repair стрілка
    f.append(rect(540, 310, 370, 65, fill=GREEN_F, stroke=GREEN_B, sw=1.5, rx=6))
    f.append(text(725, 333, "4. Асинхронний Read-Repair:", size=12, bold=True, color=GREEN_B, anchor="middle"))
    f.append(text(725, 355, "Координатор надсилає v2 на відсталу репліку C", size=12, color=INK, anchor="middle"))

    render(out("leaderless-flow.svg"), W, H, *f,
           title="Потоки повідомлень запису та читання з відновленням під час читання")


# ── 3. sloppy-hinted-handoff: нестрогий кворум і передача натяків ────────────
def fig_sloppy_hinted_handoff():
    W, H = 960, 380
    f = []

    f.append(text(W / 2, 35, "Нестрогий кворум (Sloppy Quorum) та передача натяків (Hinted Handoff)", size=16, bold=True))

    # Ліва частина: Фаза аварії
    f.append(rect(40, 65, 420, 290, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(250, 95, "Фаза 1: Домашній вузол C недоступний", size=14, bold=True, color=RED_B))

    f.append(rect(60, 130, 110, 45, fill=GREEN_F, stroke=GREEN_B, sw=1.5, rx=6))
    f.append(text(115, 157, "Вузол A (v2)", size=12, bold=True))

    f.append(rect(60, 190, 110, 45, fill=GREEN_F, stroke=GREEN_B, sw=1.5, rx=6))
    f.append(text(115, 217, "Вузол B (v2)", size=12, bold=True))

    f.append(rect(60, 250, 110, 45, fill=RED_F, stroke=RED_B, sw=1.5, rx=6))
    f.append(text(115, 270, "Вузол C (Дім)", size=12, bold=True, color=RED_B))
    f.append(text(115, 288, "ВІДМОВА", size=11, bold=True, color=RED_B))

    # Тимчасовий вузол D
    f.append(rect(240, 250, 200, 50, fill=AMBER_F, stroke=AMBER_B, sw=2, rx=6))
    f.append(text(340, 270, "Вузол D (Сусід / Handoff)", size=12, bold=True, color=AMBER_B))
    f.append(text(340, 288, "Зберігає v2 з натяком «для C»", size=11, color=INK))

    f.append(arrow(170, 272, 240, 272, color=AMBER_B))
    f.append(text(250, 335, "Запис прийнято: W=3 зібрано з {A, B, D}", size=12, bold=True, color=AMBER_B))

    # Права частина: Фаза повернення (Handoff)
    f.append(rect(500, 65, 420, 290, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(710, 95, "Фаза 2: Вузол C ожив, передача натяку", size=14, bold=True, color=GREEN_B))

    f.append(rect(520, 130, 180, 50, fill=AMBER_F, stroke=AMBER_B, sw=1.5, rx=6))
    f.append(text(610, 150, "Вузол D (тримав натяк)", size=12, bold=True))
    f.append(text(610, 170, "Знаходить v2 з міткою C", size=11, color=MUTED))

    f.append(rect(730, 130, 170, 50, fill=GREEN_F, stroke=GREEN_B, sw=2, rx=6))
    f.append(text(815, 150, "Вузол C (Ожив)", size=12, bold=True, color=GREEN_B))
    f.append(text(815, 170, "Приймає v2 у рідне місце", size=11, color=GREEN_B))

    f.append(arrow(700, 155, 730, 155, color=GREEN_B))
    f.append(text(715, 143, "Передача", size=11, bold=True, color=GREEN_B))

    f.append(rect(520, 210, 380, 75, fill=BLUE_F, stroke=BLUE_B, sw=1.2, rx=6))
    f.append(text(710, 235, "Після успішної передачі:", size=12, bold=True, color=BLUE_B))
    f.append(text(710, 255, "1. Вузол C повністю наздогнав актуальний стан", size=12))
    f.append(text(710, 275, "2. Вузол D видаляє локальну копію-натяк", size=12))

    f.append(text(710, 335, "Відновлено строгий кворум домашніх реплік {A, B, C}", size=12, bold=True, color=GREEN_B))

    render(out("sloppy-hinted-handoff.svg"), W, H, *f,
           title="Нестрогий кворум зберігає доступність запису, а передача натяків відновлює дім")


# ── 4. merkle-tree-sync: синхронізація через дерева Меркла ──────────────────
def fig_merkle_tree_sync():
    W, H = 960, 390
    f = []

    f.append(text(W / 2, 35, "Анти-ентропія: порівняння діапазонів ключів через дерева Меркла", size=16, bold=True))

    # Дерево Репліки 1 (ліворуч)
    f.append(rect(40, 60, 420, 270, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(250, 85, "Репліка 1 (повний актуальний стан)", size=13, bold=True, color=BLUE_B))

    # Корінь
    f.append(rect(190, 105, 120, 32, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=5))
    f.append(text(250, 126, "Root: #e8a1", size=12, bold=True))

    # Рівень 1
    f.append(rect(90, 160, 120, 32, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=5))
    f.append(text(150, 181, "Hash(k1,k2): #4b2c", size=11, bold=True))

    f.append(rect(290, 160, 120, 32, fill=BLUE_F, stroke=BLUE_B, sw=1.5, rx=5))
    f.append(text(350, 181, "Hash(k3,k4): #9d0f", size=11, bold=True))

    f.append(line(230, 137, 160, 160, color=BLUE_B))
    f.append(line(270, 137, 340, 160, color=BLUE_B))

    # Листя (ключі)
    f.append(rect(50, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(95, 239, "k1: v2 (#a1)", size=10, bold=True))

    f.append(rect(150, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(195, 239, "k2: v1 (#c4)", size=10, bold=True))

    f.append(rect(250, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(295, 239, "k3: v3 (#8e)", size=10, bold=True))

    f.append(rect(350, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(395, 239, "k4: v2 (#1f)", size=10, bold=True))

    f.append(line(130, 192, 95, 220, color=MUTED))
    f.append(line(170, 192, 195, 220, color=MUTED))
    f.append(line(330, 192, 295, 220, color=MUTED))
    f.append(line(370, 192, 395, 220, color=MUTED))

    # Дерево Репліки 2 (праворуч, відстає на k2)
    f.append(rect(500, 60, 420, 270, fill=GRAY_F, stroke=GRAY_B, sw=1.2, rx=8))
    f.append(text(710, 85, "Репліка 2 (відстає у ключі k2)", size=13, bold=True, color=RED_B))

    # Корінь (розбіжність)
    f.append(rect(650, 105, 120, 32, fill=RED_F, stroke=RED_B, sw=1.5, rx=5))
    f.append(text(710, 126, "Root: #f17b ≠", size=12, bold=True, color=RED_B))

    # Рівень 1 (лівий не зійшовся, правий зійшовся)
    f.append(rect(550, 160, 120, 32, fill=RED_F, stroke=RED_B, sw=1.5, rx=5))
    f.append(text(610, 181, "Hash(k1,k2): #2a88 ≠", size=11, bold=True, color=RED_B))

    f.append(rect(750, 160, 120, 32, fill=GREEN_F, stroke=GREEN_B, sw=1.5, rx=5))
    f.append(text(810, 181, "Hash(k3,k4): #9d0f =", size=11, bold=True, color=GREEN_B))

    f.append(line(690, 137, 620, 160, color=RED_B))
    f.append(line(730, 137, 800, 160, color=GREEN_B))

    # Листя (ключі)
    f.append(rect(510, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(555, 239, "k1: v2 (#a1)", size=10, bold=True))

    f.append(rect(610, 220, 90, 30, fill=RED_F, stroke=RED_B, sw=1.5, rx=4))
    f.append(text(655, 239, "k2: v0 (#00)", size=10, bold=True, color=RED_B))

    f.append(rect(710, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(755, 239, "k3: v3 (#8e)", size=10, bold=True))

    f.append(rect(810, 220, 90, 30, fill=GREEN_F, stroke=GREEN_B, sw=1, rx=4))
    f.append(text(855, 239, "k4: v2 (#1f)", size=10, bold=True))

    f.append(line(590, 192, 555, 220, color=MUTED))
    f.append(line(630, 192, 655, 220, color=RED_B))
    f.append(line(790, 192, 755, 220, color=MUTED))
    f.append(line(830, 192, 855, 220, color=MUTED))

    # Пояснення знизу
    f.append(rect(40, 345, 880, 35, fill=AMBER_F, stroke=AMBER_B, sw=1.2, rx=6))
    f.append(text(480, 367, "Порівняння коренів (#e8a1 ≠ #f17b) → спуск ліворуч → знайдено розбіжність лише у k2 без передачі всієї бази", size=12, bold=True, color=AMBER_B))

    render(out("merkle-tree-sync.svg"), W, H, *f,
           title="Дерева Меркла дозволяють локалізувати різницю між репліками за логарифмічний час")


if __name__ == "__main__":
    fig_quorum_overlap()
    fig_leaderless_flow()
    fig_sloppy_hinted_handoff()
    fig_merkle_tree_sync()
    print("OK: generated 4 figures")
