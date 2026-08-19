# -*- coding: utf-8 -*-
"""Фігури для теми «Планарний граф та теорема Куратовського» (book/algorithms/complexity-computability/planar-graph)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
COLOR_BG_BOX = "#f8fafc"
COLOR_GRID_BORDER = "#cbd5e1"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_BG = "#dbeafe"
COLOR_SUCCESS = "#059669"
COLOR_SUCCESS_BG = "#d1fae5"
COLOR_WARNING = "#d97706"
COLOR_WARNING_BG = "#fef3c7"
COLOR_DANGER = "#dc2626"
COLOR_DANGER_BG = "#fee2e2"
COLOR_MUTED = "#64748b"


def fig_kuratowski_subgraphs():
    """Фігура 1: Канонічні непланарні підграфи Куратовського K5 та K3,3 та їхні підрозбиття."""
    W, H = 1000, 480
    frags = []

    # Заголовок
    tb, _, _ = textbox(500, 32, "Заборонені підграфи Куратовського: повний K5 та двочастковий K3,3",
                       size=16, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb)

    # Ліва панель: K5
    frags.append(rect(30, 65, 450, 395, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(255, 95, "Повний граф K5 (5 вершин, 10 ребер)", size=15, color=COLOR_ACCENT, bold=True))
    frags.append(text(255, 120, "Неможливо вкласти у площину без самоперетинів: E = 10 > 3V − 6 = 9", size=12, color=COLOR_MUTED))

    # Вершини K5 по колу
    k5_cx, k5_cy, k5_r = 255, 230, 85
    k5_pts = []
    for i in range(5):
        angle = -math.pi / 2 + i * 2 * math.pi / 5
        x = k5_cx + k5_r * math.cos(angle)
        y = k5_cy + k5_r * math.sin(angle)
        k5_pts.append((x, y))

    # Ребра K5
    for i in range(5):
        for j in range(i + 1, 5):
            x1, y1 = k5_pts[i]
            x2, y2 = k5_pts[j]
            # Якщо ребро внутрішнє перетинне — виділяємо кольором
            is_crossing = (abs(i - j) not in (1, 4))
            c = COLOR_DANGER if is_crossing else COLOR_ACCENT
            sw = 2.0 if is_crossing else 1.5
            frags.append(line(x1, y1, x2, y2, color=c, sw=sw))

    # Вершини K5
    v_labels = ["v1", "v2", "v3", "v4", "v5"]
    for i, (x, y) in enumerate(k5_pts):
        frags.append(circle(x, y, 14, fill="#ffffff", stroke=COLOR_ACCENT, sw=2.0))
        frags.append(text(x, y + 4, v_labels[i], size=11, color=INK, bold=True))

    frags.append(text(255, 345, "Внутрішні ребра обов'язково перетинаються", size=12, color=COLOR_DANGER, bold=True))
    frags.append(text(255, 370, "Число перетинів cr(K5) = 1", size=12, color=COLOR_MUTED))
    frags.append(text(255, 435, "Мінімальний повний непланарний граф", size=12, color=INK, italic=True))

    # Права панель: K3,3
    frags.append(rect(520, 65, 450, 395, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(745, 95, "Повний двочастковий граф K3,3 (6 вершин, 9 ребер)", size=15, color=COLOR_ACCENT, bold=True))
    frags.append(text(745, 120, "Задача про 3 будинки та 3 комунікації: E = 9 > 2V − 4 = 8", size=12, color=COLOR_MUTED))

    # Вершини K3,3: 3 зверху (будинки), 3 знизу (ресурси)
    top_pts = [(620, 185), (745, 185), (870, 185)]
    bot_pts = [(620, 295), (745, 295), (870, 295)]

    # Ребра K3,3
    for i, (x1, y1) in enumerate(top_pts):
        for j, (x2, y2) in enumerate(bot_pts):
            is_diag = (i != j)
            c = COLOR_WARNING if is_diag else COLOR_SUCCESS
            sw = 1.8 if is_diag else 1.5
            frags.append(line(x1, y1, x2, y2, color=c, sw=sw))

    # Вершини верхні
    top_labels = ["A", "B", "C"]
    for i, (x, y) in enumerate(top_pts):
        frags.append(circle(x, y, 14, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2.0))
        frags.append(text(x, y + 4, top_labels[i], size=11, color=COLOR_ACCENT, bold=True))
        frags.append(text(x, y - 20, "Дім %d" % (i + 1), size=11, color=COLOR_MUTED))

    # Вершини нижні
    bot_labels = ["X", "Y", "Z"]
    res_names = ["Газ", "Світло", "Вода"]
    for j, (x, y) in enumerate(bot_pts):
        frags.append(circle(x, y, 14, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2.0))
        frags.append(text(x, y + 4, bot_labels[j], size=11, color=COLOR_SUCCESS, bold=True))
        frags.append(text(x, y + 26, res_names[j], size=11, color=COLOR_MUTED))

    frags.append(text(745, 360, "Неможливо з'єднати кожен дім з усіма ресурсами без перетинів", size=12, color=COLOR_DANGER, bold=True))
    frags.append(text(745, 385, "Число перетинів cr(K3,3) = 1", size=12, color=COLOR_MUTED))
    frags.append(text(745, 435, "Мінімальний двочастковий непланарний граф", size=12, color=INK, italic=True))

    return render(os.path.join(IMG, "fig1-kuratowski-subgraphs.svg"), W, H, *frags)


def fig_euler_faces_duality():
    """Фігура 2: Планарне вкладення, грані, формула Ейлера та циклічна система ротацій."""
    W, H = 1000, 460
    frags = []

    # Заголовок
    tb, _, _ = textbox(500, 32, "Формула Ейлера для планарного графа: V − E + F = 2 та комбінаторні грані",
                       size=16, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb)

    # Ліва панель: Граф із виділеними гранями
    frags.append(rect(30, 65, 480, 375, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(270, 95, "Топологічне розбиття площини на грані (Faces)", size=15, color=COLOR_ACCENT, bold=True))

    v_coords = {
        'v1': (120, 150),
        'v2': (420, 150),
        'v3': (270, 360),
        'v4': (270, 240),
        'v5': (270, 150)
    }

    g_edges = [
        ('v1', 'v5'), ('v5', 'v2'), ('v2', 'v3'), ('v3', 'v1'),
        ('v1', 'v4'), ('v5', 'v4'), ('v2', 'v4'), ('v3', 'v4')
    ]

    # Грані: заливки підграней
    frags.append('<polygon points="120,150 270,150 270,240" fill="#dbeafe" opacity="0.6"/>')
    frags.append('<polygon points="270,150 420,150 270,240" fill="#fef3c7" opacity="0.6"/>')
    frags.append('<polygon points="120,150 270,240 270,360" fill="#d1fae5" opacity="0.6"/>')
    frags.append('<polygon points="420,150 270,360 270,240" fill="#fce7f3" opacity="0.6"/>')

    # Малюємо ребра
    for u, v in g_edges:
        x1, y1 = v_coords[u]
        x2, y2 = v_coords[v]
        frags.append(line(x1, y1, x2, y2, color=INK, sw=2.0))

    # Підписи граней
    frags.append(text(220, 185, "f1", size=13, color=COLOR_ACCENT, bold=True))
    frags.append(text(320, 185, "f2", size=13, color=COLOR_WARNING, bold=True))
    frags.append(text(210, 275, "f3", size=13, color=COLOR_SUCCESS, bold=True))
    frags.append(text(330, 275, "f4", size=13, color="#db2777", bold=True))
    frags.append(text(80, 260, "f_ext (зовнішня)", size=12, color=COLOR_MUTED, bold=True))

    # Малюємо вершини
    for name, (x, y) in v_coords.items():
        frags.append(circle(x, y, 12, fill="#ffffff", stroke=COLOR_ACCENT, sw=2.0))
        frags.append(text(x, y + 4, name, size=10, color=INK, bold=True))

    frags.append(text(270, 400, "V = 5 вершин,  E = 8 ребер,  F = 5 граней (4 внутр. + 1 зовн.)", size=12, color=INK, bold=True))
    frags.append(text(270, 422, "Баланс Ейлера: 5 − 8 + 5 = 2", size=13, color=COLOR_SUCCESS, bold=True))

    # Права панель: Комбінаторна ротаційна система
    frags.append(rect(530, 65, 440, 375, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(750, 95, "Система ротацій (Rotation System)", size=15, color=COLOR_ACCENT, bold=True))
    frags.append(text(750, 120, "Циклічний порядок інцидентних ребер проти годинникової стрілки", size=12, color=COLOR_MUTED))

    # Вузол v4 з розбіжними ребрами
    rcx, rcy = 750, 230
    frags.append(circle(rcx, rcy, 22, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2.2))
    frags.append(text(rcx, rcy + 5, "v4", size=14, color=COLOR_ACCENT, bold=True))

    # Промені до сусідів: v5(зверху), v1(зліва зверху), v3(знизу), v2(справа зверху)
    nbrs = [
        ("v5 (вгору)", rcx, rcy - 75, 0, -1),
        ("v1 (ліво)", rcx - 90, rcy - 40, -0.9, -0.4),
        ("v3 (вниз)", rcx, rcy + 75, 0, 1),
        ("v2 (право)", rcx + 90, rcy - 40, 0.9, -0.4),
    ]

    for lbl, nx, ny, dx, dy in nbrs:
        frags.append(line(rcx + dx * 22, rcy + dy * 22, nx, ny, color=COLOR_MUTED, sw=1.8))
        frags.append(circle(nx, ny, 8, fill="#ffffff", stroke=COLOR_MUTED, sw=1.5))
        frags.append(text(nx, ny - 12 if dy < 0 else ny + 20, lbl, size=11, color=INK, bold=True))

    # Дугова стрілка обходу (ротація)
    frags.append(text(750, 345, "Ротація навколо v4:  (v5 → v1 → v3 → v2)", size=13, color=COLOR_ACCENT, bold=True))
    frags.append(text(750, 375, "Планарне вкладення повністю визначається", size=12, color=INK))
    frags.append(text(750, 395, "циклічними перестановками ребер для всіх вершин", size=12, color=COLOR_MUTED))
    frags.append(text(750, 422, "Алгоритмічна основа DCEL та комбінаторних карт", size=11, color=COLOR_MUTED, italic=True))

    return render(os.path.join(IMG, "fig2-euler-faces-duality.svg"), W, H, *frags)


def fig_left_right_dfs():
    """Фігура 3: Дерево DFS, зворотні ребра та Left-Right критерій планарності."""
    W, H = 1000, 460
    frags = []

    # Заголовок
    tb, _, _ = textbox(500, 32, "Алгоритм лінійного тесту планарності: дерево DFS та розміщення ребер Left/Right",
                       size=16, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb)

    # Ліва частина: DFS-дерево з прямими та зворотними ребрами
    frags.append(rect(30, 65, 460, 375, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(260, 95, "Остовне DFS-дерево та зворотні ребра", size=15, color=COLOR_ACCENT, bold=True))

    # Вершини вздовж стовбура DFS
    dfs_nodes = [
        ("r (корінь)", 260, 135),
        ("u", 260, 205),
        ("v", 260, 275),
        ("w", 260, 345)
    ]

    # Прямі деревні ребра
    for i in range(len(dfs_nodes) - 1):
        x1, y1 = dfs_nodes[i][1], dfs_nodes[i][2]
        x2, y2 = dfs_nodes[i+1][1], dfs_nodes[i+1][2]
        frags.append(line(x1, y1 + 14, x2, y2 - 14, color=COLOR_ACCENT, sw=2.5))

    # Зворотне ребро e1: від w до r (зліва)
    frags.append('<path d="M 246 345 C 130 345 130 135 246 135" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % COLOR_SUCCESS)
    frags.append(text(125, 240, "e1: Left", size=12, color=COLOR_SUCCESS, bold=True))

    # Зворотне ребро e2: від v до r (зправа)
    frags.append('<path d="M 274 275 C 370 275 370 135 274 135" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % COLOR_DANGER)
    frags.append(text(395, 205, "e2: Right", size=12, color=COLOR_DANGER, bold=True))

    # Зворотне ребро e3: від w до u (зправа)
    frags.append('<path d="M 274 345 C 340 345 340 205 274 205" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % COLOR_WARNING)
    frags.append(text(355, 290, "e3: Right", size=12, color=COLOR_WARNING, bold=True))

    # Вузли
    for name, x, y in dfs_nodes:
        frags.append(circle(x, y, 14, fill="#ffffff", stroke=COLOR_ACCENT, sw=2.0))
        frags.append(text(x, y + 4, name.split()[0], size=11, color=INK, bold=True))

    frags.append(text(260, 400, "Деревні ребра задають базисний остов (T)", size=12, color=INK, bold=True))
    frags.append(text(260, 422, "Зворотні ребра (back-edges) повертаються до предків", size=11, color=COLOR_MUTED))

    # Права частина: Конфлікт ребер та розв'язання через 2-SAT
    frags.append(rect(510, 65, 460, 375, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, sw=1.2))
    frags.append(text(740, 95, "Граф конфліктів та вибір орієнтацій", size=15, color=COLOR_ACCENT, bold=True))

    tb_rule, _, _ = textbox(740, 140, "Правило вкладення:\nЯкщо два зворотні ребра перехрещуються вздовж стовбура,\nвони мусять належати протилежним сторонам (L ≠ R)",
                            size=12, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=1.2, pad=8)
    frags.append(tb_rule)

    # Візуалізація графу конфліктів
    frags.append(text(740, 215, "Граф несумісності ребер:", size=13, color=INK, bold=True))

    # Вузли e1, e2, e3
    frags.append(circle(640, 280, 20, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2.0))
    frags.append(text(640, 285, "e1 (L)", size=12, color=COLOR_SUCCESS, bold=True))

    frags.append(circle(840, 280, 20, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=2.0))
    frags.append(text(840, 285, "e2 (R)", size=12, color=COLOR_DANGER, bold=True))

    frags.append(circle(740, 340, 20, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=2.0))
    frags.append(text(740, 345, "e3 (R)", size=12, color=COLOR_WARNING, bold=True))

    # Ребра конфлікту: e1 конфліктує з e2
    frags.append(line(660, 280, 820, 280, color=COLOR_DANGER, sw=2.0))
    frags.append(text(740, 270, "Конфлікт (L ≠ R)", size=11, color=COLOR_DANGER, bold=True))

    frags.append(line(655, 295, 725, 330, color=COLOR_MUTED, sw=1.5, dash="3,3"))

    frags.append(text(740, 400, "Граф конфліктів 2-розфарбовуваний ⇔ Початковий граф планарний", size=12, color=COLOR_SUCCESS, bold=True))
    frags.append(text(740, 422, "Алгоритм працює за час O(V + E) = O(V)", size=12, color=COLOR_ACCENT, bold=True))

    return render(os.path.join(IMG, "fig3-left-right-dfs.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_kuratowski_subgraphs()
    fig_euler_faces_duality()
    fig_left_right_dfs()
    print("Всі 3 фігури успішно згенеровано у %s" % IMG)
