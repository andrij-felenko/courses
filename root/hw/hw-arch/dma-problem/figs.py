# -*- coding: utf-8 -*-
"""Фігури до теми «Проблема потоку даних» (DMA) та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Імена файлів — slug-only, без номерів. Заголовки фігур — без «Рис.» і номерів
(підпис дає сам Markdown). Стаття: isr-overhead, cpu-ceiling.
Вставка 🧮: throughput-ceiling, transfer-cost.
Вставка 📜: channel-timeline, channel-vs-dma.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WARM = "#c0a020"   # жовтий акцент для «синхронізатора»


# ── Стаття, фіг.1: вартість одного байта за перериванням ────────────────────
def fig_isr_overhead():
    W, H = 760, 360
    f = [text(W / 2, 30, "Вартість обслуговування одного байта за перериванням",
              size=16, bold=True)]

    # Низька частота: один блок — сервіс ≫ корисна робота
    y = 78
    f.append(text(60, y - 12, "Рідка подія: службові такти величезні поруч із копією одного байта",
                  size=12, color=MUTED, anchor="start"))
    f.append(rect(60, y, 210, 56, fill="#fdecea", stroke=POS))
    f.append(fitbox(60, y, 210, 56, "вхід ISR:\nзбереження контексту", size=12,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(rect(270, y, 56, 56, fill="#eef6ef", stroke=FIELD))
    f.append(fitbox(270, y, 56, 56, "копія\n1 байта", size=11,
                    fill="#eef6ef", stroke=FIELD, color=FIELD))
    f.append(rect(326, y, 200, 56, fill="#fdecea", stroke=POS))
    f.append(fitbox(326, y, 200, 56, "вихід ISR:\nвідновлення контексту", size=12,
                    fill="#fdecea", stroke=POS, color=POS))

    # Висока частота: блоки зливаються в стіну
    y2 = 196
    f.append(text(60, y2 - 12, "Щільний потік: службові блоки зливаються в суцільну стіну",
                  size=12, color=MUTED, anchor="start"))
    x = 60
    unit = 0
    while x < 700:
        f.append(rect(x, y2, 40, 56, fill="#fdecea", stroke=POS, sw=0.8))
        f.append(rect(x + 40, y2, 6, 56, fill="#eef6ef", stroke=FIELD, sw=0.8))
        f.append(rect(x + 46, y2, 8, 56, fill="#fdecea", stroke=POS, sw=0.8))
        x += 54
        unit += 1
    f.append(text(60, y2 + 86, "Корисна копія (зелене) тоне у службових тактах (червоне).",
                  size=12, color=INK, anchor="start"))

    # Легенда
    ly = 330
    f.append(rect(60, ly - 11, 16, 13, fill="#fdecea", stroke=POS, sw=1))
    f.append(text(82, ly, "службові такти (вхід/вихід ISR)", size=11, anchor="start"))
    f.append(rect(330, ly - 11, 16, 13, fill="#eef6ef", stroke=FIELD, sw=1))
    f.append(text(352, ly, "корисна робота (копія байта)", size=11, anchor="start"))

    render(os.path.join(IMG, "fig-isr-overhead.svg"), W, H, *f)


# ── Стаття, фіг.2: частка CPU vs частота подій ──────────────────────────────
def fig_cpu_ceiling():
    W, H = 720, 400
    ox, oy = 90, 330          # початок осей
    aw, ah = 540, 270         # довжина осей
    f = [text(W / 2, 28, "Частка ядра на обслуговування проти частоти подій",
              size=16, bold=True)]

    # осі
    f.append(arrow(ox, oy, ox, oy - ah, sw=1.8))
    f.append(arrow(ox, oy, ox + aw, oy, sw=1.8))
    f.append(text(ox - 70, oy - ah / 2, "Частка\nядра", size=12))
    f.append(text(ox + aw / 2, oy + 56, "Частота подій (байти/с, лог-шкала)", size=12))

    # шкала Y 0..100%
    for frac in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        yy = oy - frac * ah
        f.append(line(ox - 5, yy, ox, yy, sw=1.2))
        f.append(text(ox - 12, yy + 4, "%d%%" % int(frac * 100), size=10,
                      color=MUTED, anchor="end"))
    # лінія 100% — обрив
    y100 = oy - ah
    f.append(line(ox, y100, ox + aw, y100, color=POS, sw=1.6, dash="6,4"))
    f.append(text(ox + aw + 4, y100 + 4, "100%", size=10, color=POS, anchor="start"))

    # шкала X (декади)
    labels = ["10 к", "100 к", "1 М", "10 М", "100 М"]
    n = len(labels)
    for i, lab in enumerate(labels):
        xx = ox + aw * (i + 0.5) / n
        f.append(line(xx, oy, xx, oy + 5, sw=1.0))
        f.append(text(xx, oy + 20, lab, size=10, color=MUTED))

    # крива «переривання-на-байт»: U = R*c/f, c=60 тактів, f=240МГц → 100% при 4МБ/с
    def x_of(R):  # R у байтах/с → x (лог від 10к)
        return ox + aw * (math.log10(R) - 4) / n
    def y_of(U):
        return oy - min(U, 1.0) * ah
    pts = []
    R = 1e4
    while R <= 1e8:
        U = R * 60 / (240e6 / 4)        # c=60 тактів/4 байти
        pts.append((x_of(R), y_of(U)))
        R *= 1.15
    d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, POS))

    # лінія DMA — поблизу нуля
    f.append(line(ox, oy - 3, ox + aw, oy - 6, color=FIELD, sw=2.5))

    # підписи кривих
    b, _, _ = textbox(ox + aw - 150, y100 + 40, "переривання-на-байт:\nповзе до 100%",
                      size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(b)
    b, _, _ = textbox(ox + 150, oy - 40, "DMA: ядро поза гарячим шляхом",
                      size=11, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b)

    render(os.path.join(IMG, "fig-cpu-ceiling.svg"), W, H, *f)


# ── Вставка 🧮, фіг.1: стеля R(макс) у двох режимах ─────────────────────────
def fig_throughput_ceiling():
    W, H = 740, 430
    ox, oy = 95, 360
    aw, ah = 540, 300
    f = [text(W / 2, 26, "Стеля без DMA: R(макс) = f(такт) / c", size=16, bold=True)]

    f.append(arrow(ox, oy, ox, oy - ah, sw=2))
    f.append(arrow(ox, oy, ox + aw, oy, sw=2))
    f.append(text(ox + aw / 2, oy + 56, "Потік R (байти/с, лог-шкала)", size=12))
    f.append(text(ox - 60, oy - ah / 2, "Частка ядра\nU = R / R(макс)", size=12))

    for frac in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        yy = oy - frac * ah
        f.append(line(ox - 5, yy, ox, yy, sw=1.2))
        f.append(text(ox - 12, yy + 4, "%d%%" % int(frac * 100), size=10,
                      color=MUTED, anchor="end"))
    y100 = oy - ah
    f.append(line(ox, y100, ox + aw, y100, color=POS, sw=1.6, dash="6,4"))
    f.append(text(ox + aw + 4, y100 + 4, "обрив", size=10, color=POS, anchor="start"))

    labels = ["10 к", "100 к", "1 М", "10 М", "100 М"]
    n = len(labels)
    for i, lab in enumerate(labels):
        xx = ox + aw * (i + 0.5) / n
        f.append(line(xx, oy, xx, oy + 5, sw=1.0))
        f.append(text(xx, oy + 20, lab, size=10, color=MUTED))

    def x_of(R):
        return ox + aw * (math.log10(R) - 4) / n

    # Режим А: R(макс)=240 МБ/с;  Режим Б: 16 МБ/с
    def curve(Rmax, color):
        pts = []
        R = 1e4
        while R <= 1e8:
            U = min(R / Rmax, 1.0)
            pts.append((x_of(R), oy - U * ah))
            R *= 1.15
        d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, color)
    f.append(curve(240e6, NEG))
    f.append(curve(16e6, POS))

    # маркери типових потоків (стеля режиму Б)
    def marker(R, label, color):
        x = x_of(R)
        U = min(R / 16e6, 1.0)
        y = oy - U * ah
        return (circle(x, y, 4.5, fill=color, stroke=color) +
                text(x, y - 10, label, size=10, color=color))
    f.append(marker(384e3, "аудіо", FIELD))
    f.append(marker(2e6, "АЦП", MUTED))
    f.append(marker(4.6e6, "дисплей", INK))

    # підписи режимів
    b, _, _ = textbox(ox + 200, oy - 0.78 * ah, "Режим А (щільний цикл)\nR(макс) ≈ 240 МБ/с",
                      size=10, fill="#eaf0fd", stroke=NEG, color=INK)
    f.append(b)
    b, _, _ = textbox(ox + aw - 150, oy - 0.62 * ah, "Режим Б (ISR на елемент)\nR(макс) ≈ 16 МБ/с",
                      size=10, fill="#fdecea", stroke=POS, color=INK)
    f.append(b)

    render(os.path.join(IMG, "fig-throughput-ceiling.svg"), W, H, *f)


# ── Вставка 🧮, фіг.2: ціна одного перенесення у двох режимах ───────────────
def fig_transfer_cost():
    W, H = 720, 320
    f = [text(W / 2, 28, "Ціна одного перенесення: щільний цикл проти переривання",
              size=16, bold=True)]

    base_x = 90
    scale = 8.5   # px за такт

    # Режим А: ~4 такти
    yA = 90
    f.append(text(base_x, yA - 12, "Режим А — щільний цикл: ≈ 4 такти/слово",
                  size=12, anchor="start", color=NEG))
    f.append(rect(base_x, yA, 4 * scale, 46, fill="#eef6ef", stroke=FIELD))
    f.append(text(base_x + 4 * scale + 8, yA + 28, "load + store + dec + branch",
                  size=11, anchor="start", color=INK))

    # Режим Б: 4 такти копії + 56 ISR
    yB = 190
    f.append(text(base_x, yB - 12, "Режим Б — переривання на елемент: ≈ 60 тактів",
                  size=12, anchor="start", color=POS))
    f.append(rect(base_x, yB, 4 * scale, 46, fill="#eef6ef", stroke=FIELD))
    f.append(rect(base_x + 4 * scale, yB, 56 * scale, 46, fill="#fdecea", stroke=POS))
    f.append(fitbox(base_x + 4 * scale, yB, 56 * scale, 46,
                    "вхід + вихід ISR: збереження/відновлення контексту (≈ 56 тактів)",
                    size=11, fill="#fdecea", stroke=POS, color=INK))

    f.append(text(W / 2, 290,
                  "Доданок ISR сплачується при кожному елементі — звідси стеля ~15× нижча.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "fig-transfer-cost.svg"), W, H, *f)


# ── Вставка 📜, фіг.1: еволюція канального I/O ──────────────────────────────
def fig_channel_timeline():
    W, H = 880, 320
    f = [text(W / 2, 26, "Еволюція канального I/O: від IBM 704 до DMA мікроконтролера",
              size=16, bold=True)]
    f.append(arrow(50, 150, 830, 150, sw=2.5))

    nodes = [
        (100, "1953", "IBM 704", "Programmed I/O", "ядро саме\nгнало кожен байт", POS, "#fdecea", True),
        (235, "1957", "IBM 709", "Data Synchronizer", "перший канал:\nпаралельний I/O", WARM, "#fff6e0", False),
        (378, "1959", "IBM 7090", "Канали 7607/7606", "до 8 каналів;\nядро лише ініціює", FIELD, "#eef6ef", True),
        (521, "1964", "System/360", "CCW-програма", "канал виконує\nзбережену програму", NEG, "#eaf0fd", False),
        (664, "1981", "System/370-XA", "Процесор каналів", "RISC-двигун\nдля I/O", "#8e44ad", "#f4eaf8", True),
        (790, "сьогодні", "DMA у МК", "(ESP32 та ін.)", "спрощений нащадок:\nфіксований переказ", LINE, "#f4f6f8", False),
    ]
    for cx, year, t1, t2, note, col, fill, above in nodes:
        f.append(circle(cx, 150, 8, fill=fill, stroke=col, sw=2.2))
        if above:
            f.append(text(cx, 178, year, size=11, color=MUTED))
            f.append(line(cx, 123, cx, 141, color=col, sw=1.4, dash="5,3"))
            f.append(rect(cx - 66, 70, 132, 50, fill=fill, stroke=col, sw=1.8))
            f.append(fitbox(cx - 66, 70, 132, 50, t1 + "\n" + t2, size=11,
                            fill=fill, stroke=col, color=INK, bold=True))
            f.append(mtext(cx, 198, note, size=10, color=MUTED))
        else:
            f.append(text(cx, 130, year, size=11, color=MUTED))
            f.append(line(cx, 159, cx, 181, color=col, sw=1.4, dash="5,3"))
            f.append(rect(cx - 66, 181, 132, 50, fill=fill, stroke=col, sw=1.8))
            f.append(fitbox(cx - 66, 181, 132, 50, t1 + "\n" + t2, size=11,
                            fill=fill, stroke=col, color=INK, bold=True))

    f.append(text(W / 2, 300,
                  "Одна ідея «звільнити ядро від I/O» пройшла від кімнатної шафи до кутка кремнію за 70 років.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "fig-channel-timeline.svg"), W, H, *f)


# ── Вставка 📜, фіг.2: канал IBM проти DMA МК ──────────────────────────────
def fig_channel_vs_dma():
    W, H = 820, 420
    f = [text(W / 2, 26, "Канал IBM проти DMA мікроконтролера", size=16, bold=True)]

    f.append(rect(70, 40, 330, 38, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(fitbox(70, 40, 330, 38, "Канал IBM (System/360)", size=14,
                    fill="#eaf0fd", stroke=NEG, color=INK, bold=True))
    f.append(rect(420, 40, 330, 38, fill="#f4f6f8", stroke=LINE, sw=2))
    f.append(fitbox(420, 40, 330, 38, "DMA мікроконтролера (ESP32)", size=14,
                    fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    # спільний верхній блок
    f.append(rect(40, 92, 710, 44, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(fitbox(40, 92, 710, 44,
                    "СПІЛЬНЕ: окремий апаратний агент на шині — ядро вільне рахувати",
                    size=12, fill="#eef6ef", stroke=FIELD, color=INK, bold=True))

    left = [
        "Ядро лишає в пам'яті\nканальну програму (CCW)",
        "Канал сам виконує CCW:\nчитай / перемотай / читай",
        "Умовні переходи й\nперевірка статусу в програмі",
        "Повноцінна збережена\nпрограма з гілками",
    ]
    right = [
        "Ядро задає один дескриптор:\nадреса → адреса, N байтів",
        "DMA виконує фіксований\nпереказ (або список блоків)",
        "Гілок немає:\nлише scatter-gather",
        "Спрощений нащадок:\nлише «скопіюй цей блок»",
    ]
    y = 150
    for i, (l, r) in enumerate(zip(left, right)):
        fillL = "#d6e8fd" if i == 3 else "#eaf0fd"
        f.append(rect(70, y, 330, 46, fill=fillL, stroke=NEG, sw=1.5))
        f.append(fitbox(70, y, 330, 46, l, size=11, fill=fillL, stroke=NEG, color=INK))
        if i == 2:
            fillR, strokeR = "#f0f0f0", MUTED
        elif i == 3:
            fillR, strokeR = "#eef6ef", FIELD
        else:
            fillR, strokeR = "#f4f6f8", LINE
        f.append(rect(420, y, 330, 46, fill=fillR, stroke=strokeR, sw=1.5))
        f.append(fitbox(420, y, 330, 46, r, size=11, fill=fillR, stroke=strokeR, color=INK))
        if i < 3:
            f.append(line(235, y + 46, 235, y + 56, color=NEG, sw=1.5))
            f.append(line(585, y + 46, 585, y + 56, color=LINE, sw=1.5))
        y += 56

    f.append(rect(40, y + 2, 710, 36, fill="#fff6e0", stroke=WARM, sw=2))
    f.append(fitbox(40, y + 2, 710, 36,
                    "DMA — це канал, з якого зняли процесор: той самий агент на шині, але виконує лише фіксований переказ.",
                    size=12, fill="#fff6e0", stroke=WARM, color=INK))
    render(os.path.join(IMG, "fig-channel-vs-dma.svg"), W, H, *f)


if __name__ == "__main__":
    fig_isr_overhead()
    fig_cpu_ceiling()
    fig_throughput_ceiling()
    fig_transfer_cost()
    fig_channel_timeline()
    fig_channel_vs_dma()
    print("OK: 6 фігур у", IMG)
