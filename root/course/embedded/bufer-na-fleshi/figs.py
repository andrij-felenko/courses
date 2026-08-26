# -*- coding: utf-8 -*-
"""Фігури для статті bufer-na-fleshi («Буфер на флеші: накопичити й віддати потім»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. flash-asymmetry: Асиметрія читання, запису та стирання в SPI NOR Flash ─
def fig_flash_asymmetry():
    W, H = 760, 340
    p = []

    # Тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Стовпець 1: Читання
    cx1 = 145
    p.append(rect(35, 35, 215, 270, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(cx1, 65, "Зчитування (Read)", size=14, bold=True, color="#0f172a"))
    p.append(line(50, 78, 235, 78, color="#cbd5e1", sw=1.2))
    p.append(mtext(cx1, 105, [
        "Гранулярність: 1 байт",
        "Затримка: мікросекунди",
        "Струм: ~5–10 мА"
    ], size=11.5, color=INK, lh=1.4))
    p.append(mtext(cx1, 175, [
        "Довільний доступ по SPI",
        "Читання не зношує",
        "структуру затвора"
    ], size=11, color=MUTED, lh=1.35))
    b1, _, _ = textbox(cx1, 265, "Знос: 0 (необмежено)", size=11, bold=True, color=FIELD, fill="#ecfdf5", stroke=FIELD, pad=6)
    p.append(b1)

    # Стовпець 2: Запис
    cx2 = 380
    p.append(rect(272, 35, 215, 270, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    p.append(text(cx2, 65, "Запис (Page Program)", size=14, bold=True, color="#92400e"))
    p.append(line(287, 78, 472, 78, color="#fde68a", sw=1.2))
    p.append(mtext(cx2, 105, [
        "Гранулярність: 1–256 Б",
        "Час запису: ~0.7–3.0 мс",
        "Тільки біти 1 -> 0"
    ], size=11.5, color=INK, lh=1.4))
    p.append(mtext(cx2, 175, [
        "Інжекція електронів",
        "у плаваючий затвор.",
        "0 -> 1 без стирання — ні!"
    ], size=11, color=MUTED, lh=1.35))
    b2, _, _ = textbox(cx2, 265, "Атомарний зсув 1 -> 0", size=11, bold=True, color="#b45309", fill="#fef3c7", stroke="#d97706", pad=6)
    p.append(b2)

    # Стовпець 3: Стирання
    cx3 = 615
    p.append(rect(510, 35, 215, 270, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(cx3, 65, "Стирання (Sector Erase)", size=14, bold=True, color=POS))
    p.append(line(525, 78, 710, 78, color="#fca5a5", sw=1.2))
    p.append(mtext(cx3, 105, [
        "Гранулярність: 4096 Б",
        "Час стирання: 40–200 мс",
        "Всі біти стають 1 (0xFF)"
    ], size=11.5, color=INK, lh=1.4))
    p.append(mtext(cx3, 175, [
        "Висока напруга (12–20 В)",
        "Тунелювання електронів",
        "Деградація оксидного шару"
    ], size=11, color=MUTED, lh=1.35))
    b3, _, _ = textbox(cx3, 265, "Ресурс: ~100 000 циклів", size=11, bold=True, color=POS, fill="#fee2e2", stroke=POS, pad=6)
    p.append(b3)

    render(os.path.join(OUT, "flash-asymmetry.svg"), W, H, *p)


# ── 2. sector-ring-fifo: Архітектура кільця секторів (Head/Tail/Queued/Free) ──
def fig_sector_ring_fifo():
    W, H = 760, 370
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    sectors = [
        {"id": 0, "state": "COMMITTED", "fill": "#eff6ff", "stroke": "#3b82f6", "color": "#1e40af", "desc": "Вичитано частково"},
        {"id": 1, "state": "TAIL SECTOR", "fill": "#dbeafe", "stroke": "#1d4ed8", "color": "#1e3a8a", "desc": "Активне читання"},
        {"id": 2, "state": "COMMITTED", "fill": "#eff6ff", "stroke": "#3b82f6", "color": "#1e40af", "desc": "Очікує відправки"},
        {"id": 3, "state": "COMMITTED", "fill": "#eff6ff", "stroke": "#3b82f6", "color": "#1e40af", "desc": "Очікує відправки"},
        {"id": 4, "state": "HEAD SECTOR", "fill": "#dcfce7", "stroke": FIELD, "color": "#14532d", "desc": "Активний запис"},
        {"id": 5, "state": "FREE (0xFF)", "fill": "#f8fafc", "stroke": "#cbd5e1", "color": MUTED, "desc": "Стерто, готовий"},
        {"id": 6, "state": "FREE (0xFF)", "fill": "#f8fafc", "stroke": "#cbd5e1", "color": MUTED, "desc": "Стерто, готовий"},
        {"id": 7, "state": "FREE (0xFF)", "fill": "#f8fafc", "stroke": "#cbd5e1", "color": MUTED, "desc": "Резервний сектор"}
    ]

    sx, sy = 35, 40
    w_sec, h_sec = 160, 105
    dx, dy = 175, 140

    coords = [
        (sx + 0*dx, sy + 0*dy),
        (sx + 1*dx, sy + 0*dy),
        (sx + 2*dx, sy + 0*dy),
        (sx + 3*dx, sy + 0*dy),
        (sx + 3*dx, sy + 1*dy),
        (sx + 2*dx, sy + 1*dy),
        (sx + 1*dx, sy + 1*dy),
        (sx + 0*dx, sy + 1*dy),
    ]

    # Стрілки
    p.append(arrow(sx + w_sec + 2, sy + h_sec/2, sx + dx - 4, sy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + dx + w_sec + 2, sy + h_sec/2, sx + 2*dx - 4, sy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + 2*dx + w_sec + 2, sy + h_sec/2, sx + 3*dx - 4, sy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + 3*dx + w_sec/2, sy + h_sec + 2, sx + 3*dx + w_sec/2, sy + dy - 4, color="#64748b", sw=1.8))
    p.append(arrow(sx + 3*dx - 4, sy + dy + h_sec/2, sx + 2*dx + w_sec + 2, sy + dy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + 2*dx - 4, sy + dy + h_sec/2, sx + 1*dx + w_sec + 2, sy + dy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + 1*dx - 4, sy + dy + h_sec/2, sx + 0*dx + w_sec + 2, sy + dy + h_sec/2, color="#64748b", sw=1.8))
    p.append(arrow(sx + w_sec/2, sy + dy - 4, sx + w_sec/2, sy + h_sec + 2, color="#64748b", sw=1.8))

    for i, sc in enumerate(sectors):
        cx, cy = coords[i]
        p.append(rect(cx, cy, w_sec, h_sec, fill=sc["fill"], stroke=sc["stroke"], sw=1.5, rx=6))
        p.append(text(cx + w_sec/2, cy + 22, f"Сектор #{sc['id']} (4 КБ)", size=12.5, bold=True, color=sc["color"]))
        p.append(text(cx + w_sec/2, cy + 50, sc["state"], size=10.5, bold=True, color=sc["color"]))
        p.append(text(cx + w_sec/2, cy + 78, sc["desc"], size=10, color=MUTED))

    # Виноски
    b_tail, _, _ = textbox(210, 325, "Хвіст (Tail Pointer): сектор #1, вичитування в мережу", size=11, bold=True, color="#1e3a8a", fill="#dbeafe", stroke="#1d4ed8", pad=6)
    p.append(b_tail)
    b_head, _, _ = textbox(575, 325, "Голова (Head Pointer): сектор #4, запис нових подій", size=11, bold=True, color="#14532d", fill="#dcfce7", stroke=FIELD, pad=6)
    p.append(b_head)

    render(os.path.join(OUT, "sector-ring-fifo.svg"), W, H, *p)


# ── 3. record-state-machine: Атомарний життєвий цикл байта прапорців ──────────
def fig_record_state_machine():
    W, H = 760, 340
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    states = [
        {"x": 35, "y": 45, "hex": "0xFF (1111 1111b)", "title": "1. Стерто / Вільно", "lines": ["Свіжий сектор", "після Erase.", "Пам'ять готова", "до запису."], "color": "#475569", "fill": "#f8fafc", "stroke": "#94a3b8"},
        {"x": 215, "y": 45, "hex": "0xFE (1111 1110b)", "title": "2. Запис даних", "lines": ["Записано Header", "та Payload.", "При знеструмленні:", "CRC не зійдеться."], "color": "#b45309", "fill": "#fef3c7", "stroke": "#f59e0b"},
        {"x": 395, "y": 45, "hex": "0xFC (1111 1100b)", "title": "3. Зафіксовано", "lines": ["Атомарний запис 1 Б.", "Скинуто біт 1 -> 0.", "Запис готовий", "до відправлення."], "color": "#15803d", "fill": "#dcfce7", "stroke": FIELD},
        {"x": 575, "y": 45, "hex": "0x00 (0000 0000b)", "title": "4. Вичитано (ACK)", "lines": ["Мережа надіслала ACK.", "Скинуто всі біти.", "Запис позначено", "як спожитий."], "color": "#1e40af", "fill": "#dbeafe", "stroke": "#3b82f6"}
    ]

    w_box = 150
    h_box = 200

    for i, st in enumerate(states):
        p.append(rect(st["x"], st["y"], w_box, h_box, fill=st["fill"], stroke=st["stroke"], sw=1.5, rx=6))
        p.append(text(st["x"] + w_box/2, st["y"] + 25, st["title"], size=12, bold=True, color=st["color"]))
        p.append(text(st["x"] + w_box/2, st["y"] + 55, st["hex"], size=10.5, bold=True, color=st["color"]))
        p.append(line(st["x"] + 15, st["y"] + 68, st["x"] + w_box - 15, st["y"] + 68, color=st["stroke"], sw=1.0))
        p.append(mtext(st["x"] + w_box/2, st["y"] + 95, st["lines"], size=11, color=MUTED, lh=1.35))

        if i < 3:
            next_x = states[i+1]["x"]
            mid_y = st["y"] + 55
            p.append(arrow(st["x"] + w_box + 2, mid_y, next_x - 4, mid_y, color="#64748b", sw=1.8))

    b_note, _, _ = textbox(380, 290, "Головний принцип Flash State Machine: перехід між станами здійснюється скиданням бітів 1 -> 0\nбез попереднього стирання сектора. Жодне знеструмлення не пошкоджує готові дані.", size=11, bold=True, color="#0f172a", fill="#f1f5f9", stroke="#cbd5e1", pad=8)
    p.append(b_note)

    render(os.path.join(OUT, "record-state-machine.svg"), W, H, *p)


# ── 4. overflow-policies: Політики переповнення та мульти-кільце тривог ──────
def fig_overflow_policies():
    W, H = 760, 340
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Секція 1: FIFO Drop
    cx1 = 145
    p.append(rect(35, 35, 215, 270, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(cx1, 62, "1. FIFO Drop", size=13.5, bold=True, color="#1e40af"))
    p.append(line(50, 75, 235, 75, color="#bfdbfe", sw=1.2))
    p.append(mtext(cx1, 100, [
        "Стратегія: викидати найстаріше",
        "Коли Head наздогнав Tail:",
        "Tail просувається на +1 сектор,",
        "а старий сектор стирається."
    ], size=10.5, color=INK, lh=1.35))
    p.append(mtext(cx1, 180, [
        "Застосування: телеметрія",
        "свіжого стану (тиск, рівень),",
        "де нові дані цінніші",
        "за пропущені старі."
    ], size=10.5, color=MUTED, lh=1.35))
    b1, _, _ = textbox(cx1, 265, "Пріоритет: свіжість", size=11, bold=True, color="#1e40af", fill="#dbeafe", stroke="#3b82f6", pad=6)
    p.append(b1)

    # Секція 2: LIFO Drop
    cx2 = 380
    p.append(rect(272, 35, 215, 270, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    p.append(text(cx2, 62, "2. LIFO / Tail Drop", size=13.5, bold=True, color="#92400e"))
    p.append(line(287, 75, 472, 75, color="#fde68a", sw=1.2))
    p.append(mtext(cx2, 100, [
        "Стратегія: ігнорувати нове",
        "Коли буфер переповнено:",
        "нові події відкидаються,",
        "поки мережа не вичитає хвіст."
    ], size=10.5, color=INK, lh=1.35))
    p.append(mtext(cx2, 180, [
        "Застосування: діагностика",
        "першопричин аварій (RCA),",
        "де перші 1000 записів",
        "після збою є критичними."
    ], size=10.5, color=MUTED, lh=1.35))
    b2, _, _ = textbox(cx2, 265, "Пріоритет: початок збою", size=11, bold=True, color="#92400e", fill="#fef3c7", stroke="#f59e0b", pad=6)
    p.append(b2)

    # Секція 3: Priority Multi-Ring
    cx3 = 615
    p.append(rect(510, 35, 215, 270, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(cx3, 62, "3. Multi-Ring (Пріоритет)", size=13.5, bold=True, color=POS))
    p.append(line(525, 75, 710, 75, color="#fca5a5", sw=1.2))
    p.append(mtext(cx3, 100, [
        "Стратегія: 2 кільця",
        "Кільце A (90%): телеметрія",
        "працює в режимі FIFO Drop.",
        "Кільце B (10%): аварії/тривоги",
        "ніколи не стираються!"
    ], size=10.5, color=INK, lh=1.35))
    p.append(mtext(cx3, 185, [
        "Застосування: промавтоматика.",
        "Потік телеметрії деградує,",
        "але жоден сигнал аварії",
        "не втрачається."
    ], size=10.5, color=MUTED, lh=1.35))
    b3, _, _ = textbox(cx3, 265, "Пріоритет: гарантія тривог", size=11, bold=True, color=POS, fill="#fee2e2", stroke=POS, pad=6)
    p.append(b3)

    render(os.path.join(OUT, "overflow-policies.svg"), W, H, *p)


if __name__ == "__main__":
    fig_flash_asymmetry()
    fig_sector_ring_fifo()
    fig_record_state_machine()
    fig_overflow_policies()
    print("Всі 4 фігури успішно згенеровано у img/")
