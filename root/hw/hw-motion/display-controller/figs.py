# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер дисплея».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
PANEL = "#2457d6"   # панель / «на склі»
HOST  = "#c0392b"   # мікроконтролер / хост
CHIP  = "#8a5fb0"   # окремий чип-контролер
GLASS = "#eaf3ff"   # заливка скла


# ── 1. Дві роботи дисплея: зберігати кадр і засвічувати ним скло ──────────────
def fig_two_jobs():
    W, H = 700, 300
    f = [text(W / 2, 26, "Дві роботи будь-якого дисплея", size=16, bold=True)]

    # робота 1 — пам'ять кадру
    f.append(rect(70, 80, 230, 150, fill="#eef4ff", stroke=PANEL, sw=2))
    f.append(text(185, 106, "1. ПАМ'ЯТЬ КАДРУ", size=13, bold=True, color=PANEL))
    f.append(text(185, 128, "що має бути на екрані", size=11, color=MUTED))
    # сітка пікселів
    gx, gy, c = 120, 150, 18
    for r in range(3):
        for q in range(8):
            on = (r + q) % 3 == 0
            f.append(rect(gx + q * c, gy + r * c, c - 2, c - 2,
                          fill=(INK if on else "#ffffff"), stroke="#c9d6f0", sw=1, rx=2))

    # робота 2 — двигун освіження
    f.append(rect(400, 80, 230, 150, fill="#f6f4ec", stroke=INK, sw=2))
    f.append(text(515, 106, "2. ДВИГУН ОСВІЖЕННЯ", size=13, bold=True))
    f.append(text(515, 128, "~60 раз/с засвічує скло", size=11, color=MUTED))
    # скло, що «забуває»
    f.append(rect(440, 148, 150, 56, fill=GLASS, stroke=PANEL, sw=1.5))
    f.append(text(515, 172, "скло", size=11, color=PANEL))
    f.append(text(515, 190, "(само все забуває)", size=10, color=MUTED, italic=True))

    # стрілка читання пам'яті → скло
    f.append(arrow(300, 200, 398, 176, color=INK, sw=2))
    f.append(text(350, 232, "перечитати й перемалювати", size=10, color=MUTED, italic=True))

    f.append(text(W / 2, 272, "Питання архітектури: хто володіє цими роботами — панель чи мікроконтролер",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "two-jobs.svg"), W, H, *f)


# ── 2. Розумна панель: контролер і пам'ять кадру — всередині модуля ───────────
def fig_smart_panel():
    W, H = 700, 280
    f = [text(W / 2, 26, "Кадр «на склі»: розумна панель", size=16, bold=True)]

    # МК
    f.append(rect(50, 110, 130, 80, fill="#fdecea", stroke=HOST, sw=2))
    f.append(text(115, 145, "МК", size=14, bold=True, color=HOST))
    f.append(text(115, 167, "майже без RAM", size=10, color=MUTED))

    # модуль панелі — велика рамка, всередині контролер+GRAM+скло
    f.append(rect(280, 70, 370, 170, fill="#f7fbff", stroke=PANEL, sw=2.2))
    f.append(text(465, 92, "МОДУЛЬ ПАНЕЛІ", size=12, bold=True, color=PANEL))

    f.append(rect(300, 110, 150, 60, fill="#eef4ff", stroke=PANEL, sw=1.6))
    f.append(text(375, 134, "контролер", size=12, bold=True))
    f.append(text(375, 154, "+ GRAM (кадр)", size=11, color=MUTED))

    f.append(rect(480, 110, 150, 110, fill=GLASS, stroke=PANEL, sw=1.6))
    f.append(text(555, 150, "скло", size=12, color=PANEL))

    # контролер сам освіжає скло (циклічна стрілка)
    f.append(arrow(450, 140, 478, 140, color=PANEL, sw=2))
    f.append(text(555, 175, "освіжає сам,", size=10, color=PANEL))
    f.append(text(555, 192, "без участі МК", size=10, color=PANEL))

    # МК шле лише команди й зміни
    f.append(arrow(180, 150, 298, 140, color=INK, sw=2))
    f.append(text(238, 124, "команди", size=10, color=INK))
    f.append(text(238, 200, "+ зміни пікселів", size=10, color=INK))

    f.append(text(W / 2, 268, "Так влаштовані типові SPI- та 8080-дисплеї (контролери класу ST7789/ILI9341)",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "smart-panel.svg"), W, H, *f)


# ── 3. Вікно адрес у GRAM: оновлюємо лише потрібний прямокутник ───────────────
def fig_gram_window():
    W, H = 700, 300
    f = [text(W / 2, 26, "Вікно адрес: оновлюємо лише прямокутник", size=16, bold=True)]

    # сітка GRAM
    ox, oy, c, cols, rows = 70, 70, 22, 14, 9
    for r in range(rows):
        for q in range(cols):
            f.append(rect(ox + q * c, oy + r * c, c - 1, c - 1,
                          fill="#f4f6f8", stroke="#dde3ea", sw=0.8, rx=0))
    # виділене вікно (x0..x1, y0..y1)
    wx0, wy0, ww, wh = 4, 2, 6, 4
    for r in range(wy0, wy0 + wh):
        for q in range(wx0, wx0 + ww):
            f.append(rect(ox + q * c, oy + r * c, c - 1, c - 1,
                          fill="#eafaf0", stroke=FIELD, sw=1.2, rx=0))
    f.append(rect(ox + wx0 * c, oy + wy0 * c, ww * c, wh * c,
                  fill="none", stroke=FIELD, sw=2.4))
    f.append(text(ox + (wx0 + ww / 2) * c, oy + wy0 * c - 6, "(x0,y0)…(x1,y1)",
                  size=11, color=FIELD, bold=True))

    # потік даних у вікно
    f.append(arrow(ox - 30, oy + (wy0 + wh / 2) * c, ox + wx0 * c - 2,
                   oy + (wy0 + wh / 2) * c, color=FIELD, sw=2))
    f.append(text(ox - 36, oy + (wy0 + wh / 2) * c - 10, "пікселі", size=10, color=FIELD, anchor="end"))

    f.append(text(W / 2, oy + rows * c + 28,
                  "По вузькій шині йде тільки те, що справді змінилося — звідси й уся швидкодія",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "gram-window.svg"), W, H, *f)


# ── 4. Хост-буфер: кадр у RAM МК, периферія сама його гонить ──────────────────
def fig_host_fb():
    W, H = 700, 280
    f = [text(W / 2, 26, "Кадр «у МК»: хост-буфер + дурна панель", size=16, bold=True)]

    # МК — велика рамка з RAM (кадр) і периферією LTDC
    f.append(rect(40, 70, 360, 170, fill="#fff3f1", stroke=HOST, sw=2.2))
    f.append(text(220, 92, "МІКРОКОНТРОЛЕР", size=12, bold=True, color=HOST))

    f.append(rect(60, 110, 150, 100, fill="#fdecea", stroke=HOST, sw=1.6))
    f.append(text(135, 138, "RAM", size=12, bold=True))
    f.append(text(135, 158, "кадровий буфер", size=10, color=MUTED))
    f.append(text(135, 176, "(великий шмат)", size=10, color=MUTED, italic=True))

    f.append(rect(240, 110, 140, 60, fill="#f6f4ec", stroke=INK, sw=1.6))
    f.append(text(310, 134, "LTDC", size=12, bold=True))
    f.append(text(310, 154, "(двигун)", size=10, color=MUTED))
    f.append(arrow(210, 145, 238, 140, color=INK, sw=1.8))
    f.append(text(225, 200, "через DMA", size=10, color=MUTED, italic=True))

    # дурна панель — лише скло
    f.append(rect(470, 90, 180, 130, fill=GLASS, stroke=MUTED, sw=1.8))
    f.append(text(560, 120, "ДУРНА ПАНЕЛЬ", size=12, bold=True, color=MUTED))
    f.append(text(560, 142, "лише скло,", size=11, color=MUTED))
    f.append(text(560, 160, "без пам'яті", size=11, color=MUTED))

    # безперервний потік кадрів
    f.append(arrow(400, 140, 468, 150, color=HOST, sw=2.2))
    f.append(text(434, 124, "безперервний", size=10, color=HOST))
    f.append(text(434, 200, "потік кадрів", size=10, color=HOST))

    f.append(text(W / 2, 268, "Повний контроль над кожним пікселем — ціною швидкої RAM і безупинної шини",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "host-fb.svg"), W, H, *f)


# ── 5. Три розміщення контролера: у панелі, у МК або окремим чипом ────────────
def fig_placement():
    W, H = 720, 300
    f = [text(W / 2, 26, "Той самий контролер — три місця", size=16, bold=True)]

    cols = [
        (130, "У ПАНЕЛІ", PANEL, "#eef4ff",
         ["розумний модуль", "SPI / 8080", "МК майже", "не напружується"]),
        (360, "У МК", HOST, "#fdecea",
         ["периферія LTDC", "повний контроль", "та потрібен", "потужний хост"]),
        (590, "ОКРЕМИМ ЧИПОМ", CHIP, "#f2ecf8",
         ["чип на вашій платі", "тримає GRAM", "велика панель", "на слабкому МК"]),
    ]
    for cx, title, col, fill, lines in cols:
        f.append(rect(cx - 100, 70, 200, 180, fill=fill, stroke=col, sw=2))
        f.append(text(cx, 96, title, size=13, bold=True, color=col))
        y = 130
        for ln in lines:
            f.append(text(cx, y, ln, size=11, color=INK))
            y += 24
        # маленький значок контролера в кожному варіанті
        f.append(rect(cx - 26, 210, 52, 26, fill="#ffffff", stroke=col, sw=1.4))
        f.append(text(cx, 227, "ctrl", size=10, color=col, bold=True))

    f.append(text(W / 2, 282, "Окремий чип — золота середина: зручність «кадр не моя турбота» на більший екран",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "placement.svg"), W, H, *f)


# ── 6. Дві архітектури поруч: чим обертається вибір місця кадру ───────────────
def fig_arch_compare():
    W, H = 720, 320
    f = [text(W / 2, 26, "Кадр «на склі» проти кадру «в МК»", size=16, bold=True)]

    # ліва колонка — розумна панель
    f.append(rect(40, 60, 310, 230, fill="#f7fbff", stroke=PANEL, sw=2))
    f.append(text(195, 86, "Розумна панель (кадр на склі)", size=12, bold=True, color=PANEL))
    plus_rows = ["+ майже не їсть RAM хоста",
                 "+ дешевий МК, проста шина",
                 "+ шле лише ЗМІНИ",
                 "− обмежена гнучкість і розмір"]
    y = 116
    for r in plus_rows:
        col = FIELD if r[0] == "+" else POS
        f.append(text(60, y, r, size=12, color=col, anchor="start"))
        y += 34

    # права колонка — хост-буфер
    f.append(rect(370, 60, 310, 230, fill="#fff3f1", stroke=HOST, sw=2))
    f.append(text(525, 86, "Хост-буфер (кадр у МК)", size=12, bold=True, color=HOST))
    rows2 = ["+ повний контроль пікселів",
             "+ великі екрани, плавна анімація",
             "− багато швидкої RAM (× 2 кадри)",
             "− безперервний потік, потужний МК"]
    y = 116
    for r in rows2:
        col = FIELD if r[0] == "+" else POS
        f.append(text(390, y, r, size=12, color=col, anchor="start"))
        y += 34

    f.append(text(W / 2, 308, "Безкоштовного варіанта немає — є відповідний задачі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "arch-compare.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_jobs()
    fig_smart_panel()
    fig_gram_window()
    fig_host_fb()
    fig_placement()
    fig_arch_compare()
    print("OK: figures written to", IMG)
