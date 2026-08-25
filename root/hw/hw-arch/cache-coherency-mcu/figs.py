# -*- coding: utf-8 -*-
"""Фігури до теми «Кеш-коерентність у мікроконтролері».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CACHE = "#6a3fb5"   # кеш
DMA   = "#b9770e"   # інший майстер (DMA)
STALE = "#c0392b"   # застарілі дані
FRESH = "#27ae60"   # свіжі дані


# ── 1. Дві дороги до пам'яті: ядро через кеш, DMA — повз кеш ──────────────────
def fig_two_masters():
    W, H = 780, 360
    f = [text(W / 2, 28, "Два майстри бачать SRAM по-різному", size=15, bold=True)]

    # Ядро
    core = rect(60, 70, 150, 56, fill="#eef2fb", stroke=NEG, sw=2.2, rx=10)
    f.append(core)
    f.append(text(135, 94, "Ядро (CPU)", size=13, color=NEG, bold=True))
    f.append(text(135, 113, "читає й пише", size=10, color=MUTED))

    # Кеш — на дорозі ядра
    f.append(rect(60, 165, 150, 56, fill="#f1ecfa", stroke=CACHE, sw=2.4, rx=10))
    f.append(text(135, 189, "Кеш даних (L1)", size=12, color=CACHE, bold=True))
    f.append(text(135, 208, "копія рядків", size=10, color=CACHE))

    # SRAM
    f.append(rect(300, 235, 190, 66, fill="#eafaf0", stroke=FRESH, sw=2.2, rx=10))
    f.append(text(395, 262, "SRAM (пам'ять)", size=13, color=INK, bold=True))
    f.append(text(395, 283, "справжні байти", size=10, color=MUTED))

    # DMA — окремий майстер
    f.append(rect(580, 70, 150, 56, fill="#fdf3e6", stroke=DMA, sw=2.2, rx=10))
    f.append(text(655, 94, "DMA", size=13, color=DMA, bold=True))
    f.append(text(655, 113, "інший майстер", size=10, color=MUTED))

    # Дорога ядра: CPU -> кеш -> SRAM
    f.append(arrow(135, 126, 135, 165, color=NEG, sw=2))
    f.append(arrow(135, 221, 335, 235, color=CACHE, sw=2))
    f.append(text(215, 240, "лише при промаху / витісненні", size=10, color=CACHE, italic=True, anchor="start"))

    # Дорога DMA: DMA -> SRAM напряму, повз кеш
    f.append(arrow(655, 126, 455, 235, color=DMA, sw=2.2))
    f.append(text(560, 175, "напряму,", size=11, color=DMA, bold=True, anchor="start"))
    f.append(text(560, 191, "повз кеш", size=11, color=DMA, bold=True, anchor="start"))

    # Підпис-висновок
    f.append(text(W / 2, 335, "Ядро говорить з копією в кеші; DMA — зі справжньою пам'яттю. Копія і оригінал розходяться.",
                  size=11, color=INK))
    render(os.path.join(IMG, "two-masters.svg"), W, H, *f)


# ── 2. Два випадки розсинхрону: несвіже читання і загублений запис ────────────
def fig_two_hazards():
    W, H = 820, 430
    f = [text(W / 2, 26, "Дві біди кеша при DMA — і чим лікувати", size=15, bold=True)]

    # ── Верхня панель: DMA пише, ядро читає старе (RX) ──
    y0 = 58
    f.append(rect(30, y0, 760, 158, fill="#fff8f6", stroke=STALE, sw=1.4, rx=10))
    f.append(text(50, y0 + 22, "1) DMA приніс нове в SRAM, а ядро читає старе з кеша", size=12.5, color=STALE, bold=True, anchor="start"))

    # SRAM новий
    f.append(rect(70, y0 + 42, 150, 44, fill="#eafaf0", stroke=FRESH, sw=2))
    f.append(text(145, y0 + 62, "SRAM: НОВЕ", size=11, color=INK, bold=True))
    f.append(text(145, y0 + 79, "DMA щойно записав", size=9.5, color=FRESH))

    # Кеш старий
    f.append(rect(70, y0 + 100, 150, 44, fill="#fdecea", stroke=STALE, sw=2))
    f.append(text(145, y0 + 120, "Кеш: СТАРЕ", size=11, color=STALE, bold=True))
    f.append(text(145, y0 + 137, "лишилася копія", size=9.5, color=STALE))

    # Ядро читає кеш
    f.append(arrow(220, y0 + 122, 330, y0 + 122, color=STALE, sw=2))
    f.append(rect(330, y0 + 100, 130, 44, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(395, y0 + 126, "Ядро читає", size=11, color=NEG, bold=True))
    f.append(text(395, y0 + 122 - 26, "бачить СТАРЕ ✗", size=10.5, color=STALE, bold=True))

    # Ліки
    f.append(rect(510, y0 + 60, 250, 84, fill="#eafaf0", stroke=FRESH, sw=2, rx=8))
    f.append(text(635, y0 + 82, "Ліки: invalidate", size=12, color=FRESH, bold=True))
    f.append(text(635, y0 + 102, "викинути копію з кеша ПІСЛЯ DMA —", size=9.5, color=INK))
    f.append(text(635, y0 + 118, "наступне читання піде в SRAM", size=9.5, color=INK))
    f.append(text(635, y0 + 136, "за свіжим", size=9.5, color=INK))

    # ── Нижня панель: ядро пише в кеш, DMA везе старе (TX) ──
    y1 = 240
    f.append(rect(30, y1, 760, 158, fill="#f7f9ff", stroke=NEG, sw=1.4, rx=10))
    f.append(text(50, y1 + 22, "2) Ядро записало в кеш (write-back), а DMA везе старе з SRAM", size=12.5, color=NEG, bold=True, anchor="start"))

    # Кеш новий (dirty)
    f.append(rect(70, y1 + 42, 150, 44, fill="#eafaf0", stroke=FRESH, sw=2))
    f.append(text(145, y1 + 62, "Кеш: НОВЕ", size=11, color=INK, bold=True))
    f.append(text(145, y1 + 79, "брудний рядок", size=9.5, color=FRESH))

    # SRAM старий
    f.append(rect(70, y1 + 100, 150, 44, fill="#fdecea", stroke=STALE, sw=2))
    f.append(text(145, y1 + 120, "SRAM: СТАРЕ", size=11, color=STALE, bold=True))
    f.append(text(145, y1 + 137, "запис ще не дійшов", size=9.5, color=STALE))

    # DMA читає SRAM
    f.append(arrow(220, y1 + 122, 330, y1 + 122, color=DMA, sw=2))
    f.append(rect(330, y1 + 100, 130, 44, fill="#fdf3e6", stroke=DMA, sw=2))
    f.append(text(395, y1 + 126, "DMA читає", size=11, color=DMA, bold=True))
    f.append(text(395, y1 + 122 - 26, "везе СТАРЕ ✗", size=10.5, color=STALE, bold=True))

    # Ліки
    f.append(rect(510, y1 + 60, 250, 84, fill="#f7f9ff", stroke=NEG, sw=2, rx=8))
    f.append(text(635, y1 + 82, "Ліки: clean", size=12, color=NEG, bold=True))
    f.append(text(635, y1 + 102, "злити брудний рядок у SRAM ПЕРЕД", size=9.5, color=INK))
    f.append(text(635, y1 + 118, "DMA — тоді він забере вже", size=9.5, color=INK))
    f.append(text(635, y1 + 136, "оновлені байти", size=9.5, color=INK))

    render(os.path.join(IMG, "two-hazards.svg"), W, H, *f)


# ── 3. Часова вісь правильного порядку clean/invalidate навколо DMA ───────────
def fig_timeline():
    W, H = 820, 300
    f = [text(W / 2, 26, "Куди ставити clean і invalidate на осі часу", size=15, bold=True)]

    axis_y = 150
    f.append(line(50, axis_y, 770, axis_y, color=INK, sw=2))
    f.append(arrow(760, axis_y, 775, axis_y, color=INK, sw=2))
    f.append(text(770, axis_y + 22, "час", size=11, color=MUTED, anchor="end", italic=True))

    def tick(x, top_lines, bot_lines, color, top_fill):
        f.append(line(x, axis_y - 6, x, axis_y + 6, color=color, sw=2))
        b, w, h = textbox(x, axis_y - 52, top_lines, size=10.5, fill=top_fill, stroke=color, sw=1.8, color=INK, pad=8)
        f.append(b)
        f.append(line(x, axis_y - 52 + h / 2, x, axis_y - 6, color=color, sw=1.4, dash="4,3"))
        if bot_lines:
            f.append(text(x, axis_y + 40, bot_lines, size=10, color=MUTED))

    tick(150, "CPU наповнив\nбуфер (TX)", "дані сидять у кеші", NEG, "#eef2fb")
    tick(330, "clean D-cache\n(by addr)", "кеш → SRAM", FRESH, "#eafaf0")
    tick(500, "старт DMA\n(SRAM ↔ пристрій)", "ядро зайняте іншим", DMA, "#fdf3e6")
    tick(690, "invalidate D-cache\n(перед читанням RX)", "викинути стару копію", STALE, "#fdecea")

    f.append(text(W / 2, 245, "Порядок непорушний: clean ПЕРЕД тим, як DMA читає; invalidate ПІСЛЯ того, як DMA записав.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 268, "Переплутати місцями — знову несвіжі дані або затертий чужий рядок.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── 4. Що додав MESI над MSI: стан Exclusive і зайва транзакція шини ──────────
def fig_msi_vs_mesi():
    W, H = 820, 380
    f = [text(W / 2, 26, "Що додав «іллінойський» MESI над MSI", size=15, bold=True)]

    # ── Ліворуч: MSI. Читання-єдиний-власник дає Shared → запис мусить кричати на шину ──
    xL = 40
    f.append(rect(xL, 52, 360, 300, fill="#fff8f6", stroke=STALE, sw=1.4, rx=12))
    f.append(text(xL + 180, 76, "MSI — три стани", size=13, color=STALE, bold=True))

    f.append(rect(xL + 40, 96, 280, 40, fill="#eef2fb", stroke=NEG, sw=1.8))
    f.append(text(xL + 180, 121, "1) Ядро читає адресу, більше ніхто її не має", size=10.5, color=INK))

    f.append(arrow(xL + 180, 136, xL + 180, 160, color=STALE, sw=2))

    f.append(rect(xL + 40, 162, 280, 40, fill="#fdecea", stroke=STALE, sw=1.8))
    f.append(text(xL + 180, 181, "2) Рядок лягає як Shared", size=10.5, color=STALE, bold=True))
    f.append(text(xL + 180, 197, "MSI не вміє сказати «я тут сам»", size=9.5, color=STALE))

    f.append(arrow(xL + 180, 202, xL + 180, 226, color=STALE, sw=2))

    f.append(rect(xL + 40, 228, 280, 40, fill="#fdecea", stroke=STALE, sw=1.8))
    f.append(text(xL + 180, 247, "3) Ядро хоче записати →", size=10.5, color=INK))
    f.append(text(xL + 180, 263, "мусить кинути invalidate на шину", size=10, color=STALE, bold=True))

    f.append(rect(xL + 40, 288, 280, 46, fill="#fdecea", stroke=STALE, sw=2, rx=8))
    f.append(text(xL + 180, 308, "Зайва транзакція шини —", size=10.5, color=STALE, bold=True))
    f.append(text(xL + 180, 324, "хоч копію ніхто не тримав", size=10, color=STALE))

    # ── Праворуч: MESI. Той самий шлях, але Exclusive → запис мовчки ──
    xR = 420
    f.append(rect(xR, 52, 360, 300, fill="#f3fbf6", stroke=FRESH, sw=1.4, rx=12))
    f.append(text(xR + 180, 76, "MESI — додано Exclusive", size=13, color=FRESH, bold=True))

    f.append(rect(xR + 40, 96, 280, 40, fill="#eef2fb", stroke=NEG, sw=1.8))
    f.append(text(xR + 180, 121, "1) Ядро читає, шина мовчить — ніхто не озвався", size=10, color=INK))

    f.append(arrow(xR + 180, 136, xR + 180, 160, color=FRESH, sw=2))

    f.append(rect(xR + 40, 162, 280, 40, fill="#eafaf0", stroke=FRESH, sw=1.8))
    f.append(text(xR + 180, 181, "2) Рядок лягає як Exclusive", size=10.5, color=INK, bold=True))
    f.append(text(xR + 180, 197, "«чисто й лише в мене»", size=9.5, color=FRESH))

    f.append(arrow(xR + 180, 202, xR + 180, 226, color=FRESH, sw=2))

    f.append(rect(xR + 40, 228, 280, 40, fill="#eafaf0", stroke=FRESH, sw=1.8))
    f.append(text(xR + 180, 247, "3) Ядро записує →", size=10.5, color=INK))
    f.append(text(xR + 180, 263, "тихо переходить у Modified", size=10, color=FRESH, bold=True))

    f.append(rect(xR + 40, 288, 280, 46, fill="#eafaf0", stroke=FRESH, sw=2, rx=8))
    f.append(text(xR + 180, 308, "Жодної транзакції шини —", size=10.5, color=FRESH, bold=True))
    f.append(text(xR + 180, 324, "у типовому «читаю, потім пишу»", size=10, color=INK))

    render(os.path.join(IMG, "msi-vs-mesi.svg"), W, H, *f)


# ── 5. Життєвий цикл RX-буфера: ДВА invalidate, дві різні небезпеки ───────────
def fig_rx_lifecycle():
    W, H = 900, 430
    f = [text(W / 2, 28, "Життєвий цикл RX-буфера: два invalidate, дві різні небезпеки", size=15, bold=True)]

    ax, ay, aw = 70, 150, 760
    f.append(line(ax, ay, ax + aw, ay, color=INK, sw=2))
    f.append(arrow(ax + aw - 12, ay, ax + aw, ay, color=INK, sw=2))
    f.append(text(ax + aw, ay - 12, "час", size=12, color=MUTED, anchor="end", italic=True))

    xs = [ax + 60, ax + 300, ax + 470, ax + 700]
    labels = ["invalidate\n(перед стартом)", "DMA возить\nбайти в SRAM",
              "IRQ «готово»\n+ invalidate", "ядро читає\nбуфер"]
    cols = [STALE, DMA, STALE, NEG]
    for x, lb, c in zip(xs, labels, cols):
        f.append(line(x, ay - 7, x, ay + 7, color=c, sw=2.4))
        b, w, h = textbox(x, ay - 52, lb, size=10.5, pad=8, stroke=c, color=INK,
                          fill="#fdecea" if c == STALE else ("#fdf3e6" if c == DMA else "#eef2fb"))
        f.append(b)
        f.append(line(x, ay - 52 + h / 2, x, ay - 7, color=c, sw=1.3, dash="4,3"))

    # смуга DMA-передавання під віссю
    f.append(rect(xs[1] - 40, ay + 20, xs[2] - xs[1] + 20, 20, fill="#fdf3e6", stroke=DMA, sw=1.3))
    f.append(text((xs[1] + xs[2]) / 2 - 10, ay + 34, "DMA пише напряму в SRAM, повз кеш", size=10, color=DMA))

    b1, w1, h1 = textbox(ax + 195, ay + 135,
                         ["ЧОМУ перед стартом:", "викинути брудні рядки буфера,",
                          "щоб під час приймання вони НЕ", "витіснились і не затерли свіже"],
                         size=11, pad=10, stroke=STALE, fill="#fdecea", color=INK)
    f.append(b1)
    b2, w2, h2 = textbox(ax + 585, ay + 135,
                         ["ЧОМУ після IRQ:", "викинути рядки, що ядро могло",
                          "спекулятивно затягнути в кеш", "під час приймання (там старе)"],
                         size=11, pad=10, stroke=STALE, fill="#fdecea", color=INK)
    f.append(b2)

    f.append(text(W / 2, H - 18,
                  "Той самий invalidate стоїть двічі — але лікує дві РІЗНІ біди: до старту чистить кеш під DMA, після старту забирає свіже.",
                  size=11, color=INK))
    render(os.path.join(IMG, "rx-lifecycle.svg"), W, H, *f)


# ── 6. Півбуферне (half-transfer) приймання: яку половину знедійснювати ────────
def fig_half_transfer():
    W, H = 880, 420
    f = [text(W / 2, 28, "Півбуфер: поки DMA пише верхню половину, ядро жує нижню", size=15, bold=True)]

    bx, by, bw, bh = 120, 90, 640, 66
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=INK, sw=2))
    f.append(line(bx + bw / 2, by, bx + bw / 2, by + bh, color=INK, sw=2))
    f.append(text(bx + bw / 4, by + bh / 2 + 5, "нижня половина", size=12.5, bold=True))
    f.append(text(bx + 3 * bw / 4, by + bh / 2 + 5, "верхня половина", size=12.5, bold=True))
    f.append(text(bx - 10, by + bh / 2 + 5, "0", size=11, color=MUTED, anchor="end"))
    f.append(text(bx + bw + 10, by + bh / 2 + 5, "N", size=11, color=MUTED, anchor="start"))

    # DMA пише верхню
    f.append(arrow(bx + 3 * bw / 4, by - 14, bx + 3 * bw / 4, by, color=DMA, sw=2.2))
    b, w, h = textbox(bx + 3 * bw / 4, by - 42, ["DMA ПИШЕ", "(зараз тут)"], size=11, pad=7,
                      stroke=DMA, color=INK, fill="#fdf3e6")
    f.append(b)

    # ядро читає нижню
    f.append(arrow(bx + bw / 4, by + bh + 14, bx + bw / 4, by + bh, color=NEG, sw=2.2))
    b, w, h = textbox(bx + bw / 4, by + bh + 42, ["ядро ЧИТАЄ", "(invalidate цю)"], size=11, pad=7,
                      stroke=NEG, color=INK, fill="#eef2fb")
    f.append(b)

    b1, w1, h1 = textbox(bx + bw / 4, 300,
                         ["Half-transfer IRQ (HT):", "нижня половина готова →",
                          "invalidate ЛИШЕ нижню,", "потім читай нижню"],
                         size=11, pad=10, stroke=STALE, fill="#fdecea", color=INK)
    f.append(b1)
    b2, w2, h2 = textbox(bx + 3 * bw / 4, 300,
                         ["Transfer-complete IRQ (TC):", "верхня половина готова →",
                          "invalidate ЛИШЕ верхню,", "потім читай верхню"],
                         size=11, pad=10, stroke=STALE, fill="#fdecea", color=INK)
    f.append(b2)

    f.append(text(W / 2, H - 16,
                  "КОЖНА половина — сама вирівняна на 32 й кратна 32, інакше invalidate однієї зачепить рядок сусідньої, яку DMA саме пише.",
                  size=11, color=STALE))
    render(os.path.join(IMG, "half-transfer.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_masters()
    fig_two_hazards()
    fig_timeline()
    fig_msi_vs_mesi()
    fig_rx_lifecycle()
    fig_half_transfer()
    print("OK: figures written to", IMG)
