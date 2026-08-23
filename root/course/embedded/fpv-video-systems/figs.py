# -*- coding: utf-8 -*-
"""Фігури до теми «FPV-відеосистеми: аналог проти DJI O3/HDZero/Walksnail».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
ANALOG = "#2457d6"   # аналог / однобічне — холодне
DIGI   = "#c0392b"   # цифра / двобічне — гаряче
GOOD   = "#27ae60"


# ── 1. Конвеєр FPV: аналог проти цифри ──────────────────────────────────────
def fig_pipeline():
    W, H = 760, 380
    parts = []

    def chain(y, label, color, stages):
        out = [text(20, y - 36, label, size=15, color=color, anchor="start", bold=True)]
        n = len(stages)
        gap = 14
        x0 = 130
        bw = (W - x0 - 30 - gap * (n - 1)) / n
        cx_prev = None
        for i, (name, ms) in enumerate(stages):
            x = x0 + i * (bw + gap)
            fill = "#fdecea" if (color == DIGI and name in ("кодер", "декодер")) else FILL
            stroke = color if (color == DIGI and name in ("кодер", "декодер")) else LINE
            out.append(fitbox(x, y - 20, bw, 40, name, size=12, fill=fill, stroke=stroke))
            out.append(text(x + bw / 2, y + 36, ms, size=11, color=MUTED))
            if cx_prev is not None:
                out.append(arrow(cx_prev, y, x - 2, y, color=color, sw=1.6))
            cx_prev = x + bw + 2
        return "".join(out)

    parts.append(text(W / 2, 26, "Шлях кадру: скло → скло", size=17, bold=True))

    parts.append(chain(120, "Аналог", ANALOG, [
        ("сенсор", "~15 мс"), ("модуляція", "~1 мс"),
        ("радіо", "~1 мс"), ("екран", "~3 мс"),
    ]))
    parts.append(text(W - 30, 120, "≈ 20 мс", size=14, color=ANALOG, anchor="end", bold=True))

    parts.append(chain(265, "Цифра", DIGI, [
        ("сенсор", "~7 мс"), ("кодер", "~12 мс"),
        ("радіо", "~4 мс"), ("декодер", "~6 мс"), ("екран", "~8 мс"),
    ]))
    parts.append(text(W - 30, 265, "≈ 37 мс", size=14, color=DIGI, anchor="end", bold=True))

    body, w, h = textbox(W / 2, 345, "Цифра вклинює стиснення/розпакування — звідси зайвий час",
                         size=12, color=INK, fill="#fff8e1", stroke="#e0a800")
    parts.append(body)

    render(os.path.join(IMG, 'pipeline.svg'), W, H, *parts)


# ── 2. Дві філософії вмирання ───────────────────────────────────────────────
def fig_two_philosophies():
    W, H = 760, 400
    parts = [text(W / 2, 26, "Що робити з утраченим пакетом", size=17, bold=True)]

    # Ліва колонка — однобічна
    lx = 190
    parts.append(text(lx, 64, "Однобічна (one-way)", size=15, color=ANALOG, anchor="middle", bold=True))
    parts.append(text(lx, 84, "аналог · HDZero", size=12, color=MUTED))
    parts.append(fitbox(lx - 120, 100, 240, 38, "Передавач шле потік уперед", size=12,
                        fill="#eaf0fd", stroke=ANALOG))
    parts.append(arrow(lx, 142, lx, 172, color=ANALOG))
    parts.append(fitbox(lx - 120, 174, 240, 38, "Пакет загубився — не перепитуємо",
                        size=12, fill=FILL))
    parts.append(arrow(lx, 216, lx, 246, color=ANALOG))
    parts.append(fitbox(lx - 120, 248, 240, 56, "«Іскри»/шум на кадрі\nзатримка СТАЛА, кадр не замерзає",
                        size=12, fill="#eaf0fd", stroke=ANALOG))
    body, w, h = textbox(lx, 340, "Живуча картинка ціною чистоти", size=12,
                         color=ANALOG, fill="#eaf0fd", stroke=ANALOG, bold=True)
    parts.append(body)

    # Розділювач
    parts.append(line(W / 2, 50, W / 2, 360, color=MUTED, sw=1, dash="4 4"))

    # Права колонка — двобічна
    rx = 570
    parts.append(text(rx, 64, "Двобічна (two-way)", size=15, color=DIGI, anchor="middle", bold=True))
    parts.append(text(rx, 84, "DJI · Walksnail", size=12, color=MUTED))
    parts.append(fitbox(rx - 120, 100, 240, 38, "Приймач має зворотний канал", size=12,
                        fill="#fdecea", stroke=DIGI))
    parts.append(arrow(rx, 142, rx, 172, color=DIGI))
    parts.append(fitbox(rx - 120, 174, 240, 38, "Просить переслати втрачене (ARQ)",
                        size=12, fill=FILL))
    parts.append(arrow(rx, 216, rx, 246, color=DIGI))
    parts.append(fitbox(rx - 120, 248, 240, 56, "Чистий кадр\nале +затримка або ЗАМЕРЗАННЯ",
                        size=12, fill="#fdecea", stroke=DIGI))
    body, w, h = textbox(rx, 340, "Чиста картинка ціною ризику", size=12,
                         color=DIGI, fill="#fdecea", stroke=DIGI, bold=True)
    parts.append(body)

    render(os.path.join(IMG, 'two-philosophies.svg'), W, H, *parts)


# ── 3. Чотири системи поруч ─────────────────────────────────────────────────
def fig_four_systems():
    W, H = 780, 360
    parts = [text(W / 2, 26, "Чотири школи FPV", size=17, bold=True)]

    rows = ["Затримка", "Картинка", "На межі", "Відкритість"]
    cols = [
        ("Аналог",  ANALOG, ["~12-40 мс", "низька (ТБ)", "«сніг»", "повна"]),
        ("HDZero",  ANALOG, ["~14 мс*", "720p/540p", "«іскри»", "відкрита"]),
        ("DJI O3/O4", DIGI, ["~20-40 мс", "1080p, 4K-зап.", "замерзання", "закрита"]),
        ("Walksnail", DIGI, ["~22-35 мс", "1080p/120", "замерзання", "закрита"]),
    ]

    x0, y0 = 150, 70
    cw, rh = 150, 50
    # заголовки рядків
    for r, name in enumerate(rows):
        parts.append(text(x0 - 12, y0 + rh * (r + 1) + rh / 2 + 4, name,
                          size=12, color=INK, anchor="end", bold=True))
    # колонки
    for c, (name, color, vals) in enumerate(cols):
        cx = x0 + c * cw
        parts.append(fitbox(cx + 4, y0, cw - 8, rh - 8, name, size=13,
                            fill="#fdecea" if color == DIGI else "#eaf0fd",
                            stroke=color, bold=True))
        for r, v in enumerate(vals):
            y = y0 + rh * (r + 1)
            parts.append(fitbox(cx + 4, y + 4, cw - 8, rh - 8, v, size=11, fill=FILL))

    body, w, h = textbox(W / 2, 340,
                         "*гоночний режим ~20 мс · гонка → ліва пара · зйомка/фрістайл → права",
                         size=11, color=INK, fill="#fff8e1", stroke="#e0a800")
    parts.append(body)

    render(os.path.join(IMG, 'four-systems.svg'), W, H, *parts)


# ── 4. Анатомія бюджету затримки ────────────────────────────────────────────
def fig_budget_anatomy():
    W, H = 760, 430
    parts = [text(W / 2, 26, "Три виміри одного бюджету затримки", size=17, bold=True)]

    # Спільна шкала мс: 0..40 мс ліворуч (детально), потім розрив до 200 (реакція)
    x0 = 175           # початок смуг
    xend = W - 30
    detail_ms = 40.0   # ліва, детальна зона
    xbreak = 560       # де закінчується детальна зона
    pxd = (xbreak - x0) / detail_ms   # px на мс у детальній зоні

    def xd(ms):        # позиція в детальній зоні
        return x0 + ms * pxd

    # ── Ряд 1: кадровий дедлайн ──
    y1 = 90
    parts.append(text(x0 - 12, y1 + 5, "Кадровий дедлайн", size=12, color=INK,
                      anchor="end", bold=True))
    # сегменти обробки (сенсор/кодер/декодер/екран) — стек до 14 мс
    segs = [("сенсор", 3, ANALOG), ("кодер", 4, DIGI), ("декодер", 4, "#8e44ad"),
            ("екран", 3, GOOD)]
    cx = x0
    for name, ms, col in segs:
        w = ms * pxd
        parts.append(rect(cx, y1 - 14, w, 28, fill="#ffffff", stroke=col, sw=1.6))
        if w > 26:
            parts.append(text(cx + w / 2, y1 + 4, name, size=9, color=col))
        cx += w
    load_x = cx
    # лінія періоду кадру (10 мс при 100 к/с)
    px = xd(10)
    parts.append(line(px, y1 - 26, px, y1 + 22, color="#e0a800", sw=2, dash="4 3"))
    parts.append(text(px, y1 - 31, "період кадру 10 мс (100 к/с)", size=10,
                      color="#b8860b"))
    parts.append(text(load_x + 6, y1 + 4, "обробка 14 мс", size=10, color=MUTED,
                      anchor="start"))

    # ── Ряд 2: скло-скло (обробка + радіо, діапазон) ──
    y2 = 175
    parts.append(text(x0 - 12, y2 + 5, "Скло-скло", size=12, color=INK,
                      anchor="end", bold=True))
    # обчислювальна частина (та сама 14 мс)
    parts.append(rect(x0, y2 - 14, 14 * pxd, 28, fill="#eef1f5", stroke=LINE, sw=1.4))
    parts.append(text(x0 + 7 * pxd, y2 + 4, "обробка", size=9, color=MUTED))
    # радіо як діапазон 6..18 поверх (Walksnail-стиль)
    rmin, rmax = 6, 18
    rx1 = x0 + 14 * pxd
    parts.append(rect(rx1, y2 - 14, rmin * pxd, 28, fill="#fdecea", stroke=DIGI, sw=1.4))
    parts.append(rect(rx1 + rmin * pxd, y2 - 14, (rmax - rmin) * pxd, 28,
                      fill="#fbe0dc", stroke=DIGI, sw=1.0))
    parts.append(text(rx1 + (rmax / 2) * pxd, y2 + 4, "радіо: min … max", size=9,
                      color=DIGI))
    # підписи меж
    parts.append(text(x0 + 22 * pxd, y2 - 22, "22 мс (поле)", size=9, color=ANALOG))
    parts.append(text(x0 + 35 * pxd, y2 - 22, "35 мс (бетон)", size=9, color=DIGI))
    parts.append(line(x0 + 35 * pxd, y2 - 16, x0 + 35 * pxd, y2 + 18,
                      color=DIGI, sw=1, dash="2 2"))

    # ── Ряд 3: бюджет реакції пілота (стиснена шкала) ──
    y3 = 270
    parts.append(text(x0 - 12, y3 + 5, "Бюджет реакції", size=12, color=INK,
                      anchor="end", bold=True))
    # вся смуга = 200 мс
    full_w = xend - x0
    parts.append(rect(x0, y3 - 14, full_w, 28, fill="#eafaf1", stroke=GOOD, sw=1.4))
    parts.append(text(xend - 6, y3 + 4, "≈200 мс реакції людини", size=10,
                      color="#1e8449", anchor="end"))
    # з'їдена частина (35 мс) пропорційно до 200
    eaten = full_w * (35.0 / 200.0)
    parts.append(rect(x0, y3 - 14, eaten, 28, fill="#fdecea", stroke=DIGI, sw=1.4))
    parts.append(text(x0 + eaten / 2, y3 + 4, "−35", size=10, color=DIGI, bold=True))
    parts.append(text(x0 + eaten + (full_w - eaten) / 2, y3 - 22,
                      "лишилось 165 мс — фора на дію", size=10, color="#1e8449"))

    # Підсумкова рамка
    body, w, h = textbox(W / 2, 360,
                         "Обробка мусить влізти в період кадру · радіо — зсув поверх ·\n"
                         "скло-скло з'їдає бюджет реакції; рахуй за гіршим (max)",
                         size=11, color=INK, fill="#fff8e1", stroke="#e0a800")
    parts.append(body)

    render(os.path.join(IMG, 'budget-anatomy.svg'), W, H, *parts)


# ── 5. Сходи частот: відео тікає від керування на 5.8 ГГц ───────────────────
def fig_freq_ladder():
    W, H = 760, 430
    parts = [text(W / 2, 26, "Чому відео втекло на 5.8 ГГц", size=17, bold=True)]

    # Вертикальна вісь спектра: знизу низькі частоти, угорі високі
    ax_x = 150
    y_bot, y_top = 370, 70
    parts.append(arrow(ax_x, y_bot, ax_x, y_top - 6, color=MUTED, sw=1.6))
    parts.append(text(ax_x, y_top - 16, "частота ↑", size=11, color=MUTED))

    # Рівні-щаблі: (мітка, y, призначення, колір, нота)
    bands = [
        ("ТБ-канали · 430 МГц", 350, "відео", DIGI, "труться з керуванням"),
        ("900 МГц", 300, "відео", DIGI, "далеко, добре пробиває"),
        ("1.2 / 1.3 ГГц", 250, "відео", DIGI, "2-га гармоніка → 2.4 ГГц!"),
        ("2.4 ГГц", 170, "керування", ANALOG, "сюди переїхали команди"),
        ("5.8 ГГц", 100, "відео", GOOD, "втеча: широка смуга, мала антена"),
    ]
    for label, y, role, color, note in bands:
        fill = "#fdecea" if color == DIGI else ("#eaf0fd" if color == ANALOG else "#e9f7ef")
        parts.append(line(ax_x - 6, y, ax_x + 6, y, color=MUTED, sw=1.4))
        parts.append(fitbox(ax_x + 20, y - 17, 150, 34, label, size=12,
                            fill=fill, stroke=color, bold=True))
        parts.append(text(ax_x + 182, y - 2, role, size=11, color=color, anchor="start", bold=True))
        parts.append(text(ax_x + 182, y + 13, note, size=10, color=MUTED, anchor="start"))

    # Стрілка-втеча від 1.2 ГГц угору до 5.8 ГГц
    parts.append(arrow(ax_x - 22, 250, ax_x - 22, 104, color=GOOD, sw=2.2))
    parts.append(text(ax_x - 30, 180, "втеча", size=11, color=GOOD, anchor="end", bold=True))

    body, w, h = textbox(W / 2, 405,
                         "Рознеси відео й керування якнайдалі по спектру — щоб не глушили одне одного",
                         size=12, color=INK, fill="#fff8e1", stroke="#e0a800")
    parts.append(body)

    render(os.path.join(IMG, 'freq-ladder.svg'), W, H, *parts)


# ── 6. Стрічка часу FPV: від CCD-камери до трьох цифрових шкіл ───────────────
def fig_fpv_timeline():
    W, H = 900, 360
    parts = [text(W / 2, 26, "Сорок років FPV", size=17, bold=True)]

    x0, x1 = 95, W - 95
    axis_y = 250
    parts.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))

    # (рік, підпис, угору?, колір)  колір: ANALOG = однобічна гілка, DIGI = двобічна
    ev = [
        (1989, "Беррі:\nProject Cyclops", True,  ANALOG),
        (2006, "Денис VRFlyer:\nвідео палить спільноту", False, ANALOG),
        (2011, "5.8 ГГц —\nаналог-стандарт", True,  ANALOG),
        (2015, "SmartAudio /\nTramp", False, ANALOG),
        (2019, "DJI ламає стіну\n720p · ~28 мс", True,  DIGI),
        (2021, "Shark Byte →\nHDZero (open)", False, ANALOG),
        (2022, "Walksnail\nAvatar", True,  DIGI),
    ]
    ymin, ymax = 1989, 2022
    def xof(yr):
        return x0 + (x1 - x0) * (yr - ymin) / (ymax - ymin)

    for yr, label, up, color in ev:
        x = xof(yr)
        fill = "#fdecea" if color == DIGI else "#eaf0fd"
        parts.append(circle(x, axis_y, 6, fill=color, stroke=color, sw=1))
        if up:
            parts.append(line(x, axis_y - 6, x, axis_y - 40, color=MUTED, sw=1.2))
            parts.append(text(x, axis_y - 50, str(yr), size=12, color=color, bold=True))
            parts.append(fitbox(x - 78, axis_y - 96, 156, 40, label, size=11,
                                fill=fill, stroke=color))
        else:
            parts.append(line(x, axis_y + 6, x, axis_y + 40, color=MUTED, sw=1.2))
            parts.append(text(x, axis_y + 34, str(yr), size=12, color=color, bold=True))
            parts.append(fitbox(x - 78, axis_y + 44, 156, 40, label, size=11,
                                fill=fill, stroke=color))

    # Легенда
    parts.append(circle(x0 + 6, 326, 6, fill=ANALOG, stroke=ANALOG, sw=1))
    parts.append(text(x0 + 18, 330, "однобічна гілка (аналог, HDZero)",
                      size=11, color=MUTED, anchor="start"))
    parts.append(circle(x0 + 320, 326, 6, fill=DIGI, stroke=DIGI, sw=1))
    parts.append(text(x0 + 332, 330, "двобічна (DJI, Walksnail)",
                      size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'fpv-timeline.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_pipeline()
    fig_two_philosophies()
    fig_four_systems()
    fig_budget_anatomy()
    fig_freq_ladder()
    fig_fpv_timeline()
    print("OK: 6 фігур у", IMG)
