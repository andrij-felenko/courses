# -*- coding: utf-8 -*-
"""Фігури до теми «Що ганяє ціну плати: шари, розмір, отвори, клас, покриття, строк»
(root/hw/hw-pcb/shcho-haniaie-tsinu-platy).

Дві фігури:
  cost-drivers-breakdown.svg — структура виробничих витрат для різних технологічних класів плат
  panel-utilization.svg      — ефективність використання площі виробничої панелі (86% проти 52%)

Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os

# scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. cost-drivers-breakdown.svg
# ════════════════════════════════════════════════════════════════════════════
def fig_cost_drivers_breakdown():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 28, "Структура виробничої собівартості за класами складності плат", size=15, bold=True))

    # 4 стовпчики порівняння технологічних класів
    classes = [
        {
            "name": "2L Проста",
            "spec": "2 шари · HASL · 6/6 mil",
            "mult": "1.0× (база)",
            "bars": [
                ("FR-4 текстоліт", 38, "#3498db"),
                ("Мех. свердління", 18, "#9b59b6"),
                ("Травлення міді", 16, "#e67e22"),
                ("HASL покриття", 12, "#2ecc71"),
                ("Тест і AOI", 16, "#e74c3c"),
            ]
        },
        {
            "name": "4L Стандарт",
            "spec": "4 шари · ENIG · 5/5 mil",
            "mult": "2.2× бази",
            "bars": [
                ("Текстоліт + препрег", 30, "#3498db"),
                ("1 цикл пресування", 22, "#f39c12"),
                ("Внутр. AOI + травлення", 20, "#e67e22"),
                ("ENIG золото", 15, "#27ae60"),
                ("Тест і контроль", 13, "#e74c3c"),
            ]
        },
        {
            "name": "6L Силова",
            "spec": "6 шарів · 2 oz · ENIG",
            "mult": "4.2× бази",
            "bars": [
                ("Товста мідь 70 мкм", 36, "#2980b9"),
                ("Пресування + смола", 24, "#f39c12"),
                ("Тривале травлення", 18, "#d35400"),
                ("ENIG золото", 12, "#27ae60"),
                ("Тест підвищ. струмом", 10, "#c0392b"),
            ]
        },
        {
            "name": "8L HDI / VIPPO",
            "spec": "8L · Мікроотвори · VIPPO",
            "mult": "9.6× бази",
            "bars": [
                ("Тонкі High-Tg ядра", 20, "#1f618d"),
                ("2 цикли пресування", 25, "#d68910"),
                ("Лазерні отвори + VIPPO", 28, "#8e44ad"),
                ("ENIG + хім. мідь", 14, "#229954"),
                ("LDI + AOI (3/3 mil)", 13, "#a93226"),
            ]
        },
    ]

    col_w = 160
    col_gap = 25
    left_margin = 35
    top_y = 65

    # Легенда
    leg_items = [
        ("Матеріали", "#3498db"),
        ("Пресування", "#f39c12"),
        ("Свердління/VIPPO", "#8e44ad"),
        ("Травлення", "#e67e22"),
        ("Фініш/Золото", "#27ae60"),
        ("Контроль/LDI", "#e74c3c"),
    ]
    leg_x = 75
    for lbl, col in leg_items:
        f.append(rect(leg_x, 388, 14, 14, fill=col, stroke=col, rx=2))
        f.append(text(leg_x + 20, 400, lbl, size=11, color=INK, anchor="start"))
        leg_x += 115

    for i, c in enumerate(classes):
        cx = left_margin + i * (col_w + col_gap)

        # Картка заголовка
        f.append(rect(cx, top_y, col_w, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
        f.append(text(cx + col_w / 2, top_y + 20, c["name"], size=13, bold=True, color=INK))
        f.append(text(cx + col_w / 2, top_y + 38, c["spec"], size=10, color=MUTED))
        f.append(text(cx + col_w / 2, top_y + 55, c["mult"], size=11, bold=True, color=POS))

        # Стовпчик часток
        bar_y = top_y + 75
        bar_h_total = 210
        cur_y = bar_y

        for bname, pct, col in c["bars"]:
            h = (pct / 100.0) * bar_h_total
            f.append(rect(cx + 10, cur_y, col_w - 20, h, fill=col, stroke="#ffffff", sw=1, rx=3))
            if h >= 22:
                f.append(text(cx + col_w / 2, cur_y + h / 2 + 4, "%d%%" % pct, size=11, bold=True, color="#ffffff"))
            cur_y += h

        f.append(rect(cx + 10, bar_y, col_w - 20, bar_h_total, fill="none", stroke="#94a3b8", sw=1.2, rx=4))

    f.append(text(W / 2, 370, "Кожен новий цикл пресування, тип отвору (VIPPO) та перехід на тонкий клас 3/3 mil стрибкоподібно підіймають вартість", size=11, color=MUTED))

    render(os.path.join(IMG, "cost-drivers-breakdown.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. panel-utilization.svg
# ════════════════════════════════════════════════════════════════════════════
def fig_panel_utilization():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 26, "Ефективність розкрою стандартної виробничої панелі 18\"×24\" (457×610 мм)", size=15, bold=True))

    panels = [
        {
            "title": "Оптимальний розкрій: 50×70 мм",
            "subtitle": "Корисне використання: 86.4%",
            "status_col": "#27ae60",
            "x0": 40,
            "pw": 320,
            "ph": 260,
            "cols": 5,
            "rows": 3,
            "bw": 52,
            "bh": 68,
            "margin_x": 18,
            "margin_y": 14,
            "gap": 5,
            "count_text": "15 плат на заготовці (відхід 13.6%)",
            "cost_note": "Мінімальна собівартість одиниці",
        },
        {
            "title": "Невдалий розкрій: 110×140 мм",
            "subtitle": "Корисне використання: 52.8%",
            "status_col": "#c0392b",
            "x0": 420,
            "pw": 320,
            "ph": 260,
            "cols": 2,
            "rows": 1,
            "bw": 120,
            "bh": 180,
            "margin_x": 28,
            "margin_y": 36,
            "gap": 12,
            "count_text": "2 плати на заготовці (відхід 47.2%)",
            "cost_note": "Майже половина площі йде у сміття",
        }
    ]

    top_y = 52

    for p in panels:
        px = p["x0"]
        pw = p["pw"]
        ph = p["ph"]

        # Заголовок блоку
        f.append(text(px + pw / 2, top_y + 16, p["title"], size=13, bold=True, color=INK))
        f.append(text(px + pw / 2, top_y + 34, p["subtitle"], size=12, bold=True, color=p["status_col"]))

        # Тіло панелі (сірий фон - відходи текстоліту)
        panel_y = top_y + 45
        f.append(rect(px, panel_y, pw, ph, fill="#fee2e2" if p["cols"] == 2 else "#dcfce7", stroke="#94a3b8", sw=2, rx=6))

        # Технологічні поля (tooling strip)
        tool_w = 12
        f.append(rect(px + tool_w, panel_y + tool_w, pw - 2 * tool_w, ph - 2 * tool_w, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))

        # Технологічні отвори на полях
        holes = [
            (px + 6, panel_y + 6),
            (px + pw - 6, panel_y + 6),
            (px + 6, panel_y + ph - 6),
            (px + pw - 6, panel_y + ph - 6),
        ]
        for hx, hy in holes:
            f.append(circle(hx, hy, 3.5, fill="#ffffff", stroke="#64748b", sw=1))

        # Оптичні репери (fiducials)
        fids = [
            (px + 6, panel_y + ph / 2),
            (px + pw - 6, panel_y + ph / 2),
        ]
        for fx, fy in fids:
            f.append(circle(fx, fy, 2.5, fill="#64748b", stroke="#334155", sw=0.8))

        # Сітка плат
        start_x = px + p["margin_x"]
        start_y = panel_y + p["margin_y"]

        for r in range(p["rows"]):
            for c in range(p["cols"]):
                bx = start_x + c * (p["bw"] + p["gap"])
                by = start_y + r * (p["bh"] + p["gap"])
                f.append(rect(bx, by, p["bw"], p["bh"], fill="#2563eb", stroke="#1d4ed8", sw=1.5, rx=3))
                # Текст на платі
                if p["cols"] == 5:
                    f.append(text(bx + p["bw"] / 2, by + p["bh"] / 2 + 3, "PCB", size=9, color="#ffffff", bold=True))
                else:
                    f.append(text(bx + p["bw"] / 2, by + p["bh"] / 2 - 8, "Плата 110×140", size=12, color="#ffffff", bold=True))
                    f.append(text(bx + p["bw"] / 2, by + p["bh"] / 2 + 10, "PCB", size=10, color="#bfdbfe"))

        # Підсумок під панеллю
        info_y = panel_y + ph + 22
        f.append(text(px + pw / 2, info_y, p["count_text"], size=12, bold=True, color=INK))
        f.append(text(px + pw / 2, info_y + 18, p["cost_note"], size=11, color=MUTED))

    # Загальний висновок унизу
    f.append(text(W / 2, 412, "Замовник платить за повну площу виробничої заготовки: чим вища утилізація площі, тим дешевша окрема плата", size=11, color=MUTED))

    render(os.path.join(IMG, "panel-utilization.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cost_drivers_breakdown()
    fig_panel_utilization()
    print("OK: 2 фігури згенеровано у", IMG)
