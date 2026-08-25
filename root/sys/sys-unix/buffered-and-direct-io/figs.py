# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f1f2f4"


# ── 1. Два шляхи одного читання ────────────────────────────────────────────────
def fig_two_paths():
    W, H = 1240, 700
    p = []

    p.append(text(310, 44, "буферизоване читання", size=16, bold=True, color=NEG))
    p.append(text(930, 44, "пряме читання (O_DIRECT)", size=16, bold=True, color=POS))
    p.append(line(620, 70, 620, H - 130, color="#c8ccd2", sw=1.2, dash="6 6"))

    BW, BH = 380, 66

    def column(cx, stages, accent):
        out = []
        for (y, label, sub, tint) in stages:
            out.append(rect(cx - BW / 2, y, BW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
            out.append(text(cx, y + 28, label, size=13, bold=True, color=INK))
            out.append(text(cx, y + 49, sub, size=10.5, color=MUTED))
        return out

    left_stages = [
        (90,  "носій: сектори по 4096 байтів", "накопичувач", GREEN),
        (250, "сторінка кеша сторінок", "пам'ять ядра, лишається після виклику", WARM),
        (410, "буфер програми", "власна пам'ять процесу", SOFT),
    ]
    right_stages = [
        (90,  "носій: сектори по 4096 байтів", "накопичувач", GREEN),
        (410, "буфер програми, сторінки закріплені", "власна пам'ять процесу", SOFT),
    ]
    p += column(310, left_stages, NEG)
    p += column(930, right_stages, POS)

    # ліві переходи
    p.append(arrow(310, 90 + BH + 4, 310, 250 - 6, color=NEG, sw=2))
    p.append(mtext(330, 180, "DMA пристрою\nв пам'ять ядра", size=11, color=INK, anchor="start", lh=1.3))
    p.append(arrow(310, 250 + BH + 4, 310, 410 - 6, color=NEG, sw=2))
    p.append(mtext(330, 340, "копіювання процесором\n(≈0.7 ядра на 7 ГБ/с)", size=11, color=POS, anchor="start", lh=1.3))

    # правий перехід
    p.append(arrow(930, 90 + BH + 4, 930, 410 - 6, color=POS, sw=2.4))
    p.append(mtext(950, 250, "DMA пристрою просто\nв буфер програми", size=11, color=INK, anchor="start", lh=1.3))

    # підсумкові панелі
    LY = 520
    left_note = ("сторінка лишилася в пам'яті:\n"
                 "• обслужить наступного читача\n"
                 "• дозволяє читання наперед\n"
                 "• збирає дрібні записи в один\n"
                 "• колись витіснить чиюсь чужу")
    right_note = ("у пам'яті не лишилося нічого:\n"
                  "• кеш свій або ніякий\n"
                  "• читання наперед своє\n"
                  "• кожен запис — окрема операція\n"
                  "• вимоги до вирівнювання")
    p.append(fitbox(310 - 250, LY, 500, 132, left_note, size=12, fill=COOL, stroke=NEG))
    p.append(fitbox(930 - 250, LY, 500, 132, right_note, size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Буферизоване й пряме читання: що лишається в пам'яті після виклику")


# ── 2. Чому потрібне вирівнювання ──────────────────────────────────────────────
def fig_alignment():
    W, H = 1200, 660
    p = []

    SX, SW_, SH = 90, 200, 58
    ys = 120
    marks = [98304, 102400, 106496]

    p.append(text(W / 2, 46, "запит: 5000 байтів із зміщення 100 000, логічний блок 4096",
                  size=15, bold=True, color=INK))

    # смуга секторів
    for i in range(5):
        x = SX + i * SW_
        p.append(rect(x, ys, SW_, SH, fill=GREY, stroke=LINE, sw=1.4, rx=0))
        p.append(text(x + SW_ / 2, ys + 35, "сектор %d" % (23 + i), size=12, color=MUTED))
    for i, m in enumerate(marks):
        x = SX + (i + 1) * SW_
        p.append(text(x, ys - 14, str(m), size=11, color=MUTED))

    # бажана ділянка — смугою ПІД сектором, а не поверх нього: накладання поверх читалося б
    # як окремий блок і його справедливо ловить svgcheck (§5).
    x0 = SX + SW_ + (100000 - 98304) / 4096.0 * SW_
    x1 = SX + SW_ + (105000 - 98304) / 4096.0 * SW_
    yb = ys + SH + 10
    p.append(rect(x0, yb, x1 - x0, 20, fill="#fdecea", stroke=POS, sw=2, rx=3))
    p.append(line(x0, ys + SH, x0, yb, color=POS, sw=1.2, dash="3,3"))
    p.append(line(x1, ys + SH, x1, yb, color=POS, sw=1.2, dash="3,3"))
    p.append(text((x0 + x1) / 2, yb + 44, "потрібні байти", size=12, color=POS, bold=True))

    # що довелось би зробити
    p.append(mtext(SX, 300,
                   "Перший і останній сектори потрібні не цілком. Щоб записати таку ділянку,",
                   size=13, color=INK, anchor="start"))
    p.append(mtext(SX, 326,
                   "хтось мусить прочитати сектор, підмінити в ньому частину й записати назад.",
                   size=13, color=INK, anchor="start"))

    CY = 420
    p.append(fitbox(SX, CY, 470, 150,
                    "буферизований шлях\n\nсторінка кеша і є тим місцем,\nде відбувається підміна —\nпрограма про це не знає",
                    size=12.5, fill=COOL, stroke=NEG))
    p.append(fitbox(SX + 540, CY, 470, 150,
                    "прямий шлях\n\nтакого місця немає зовсім,\nтому запит мусить прийти\nвирівняним уже готовим",
                    size=12.5, fill="#fdecea", stroke=POS))

    p.append(text(W / 2, H - 40,
                  "вирівняний запит: зміщення 98 304, довжина 8192, адреса буфера кратна 4096",
                  size=12.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "alignment.svg"), W, H, *p,
           title="Невирівняний запит потребує читання-підміни-запису, а прямому шляху нема де це зробити")


# ── 3. Глибина черги ───────────────────────────────────────────────────────────
def fig_queue_depth():
    W, H = 1200, 620
    p = []

    T0, TW = 300, 760          # початок і ширина осі часу
    UNIT = TW / 8.0            # 80 мкс на поділку

    p.append(text(W / 2, 44, "затримка одного читання 4 КіБ — 80 мкс", size=15, bold=True, color=INK))

    # вісь
    def axis(y):
        out = [line(T0, y, T0 + TW, y, color="#c8ccd2", sw=1.2)]
        for k in range(9):
            x = T0 + k * UNIT
            out.append(line(x, y - 6, x, y + 6, color="#c8ccd2", sw=1.2))
        return out

    # ── глибина 1
    Y1 = 150
    p.append(mtext(80, Y1 - 6, "глибина 1", size=14, bold=True, color=NEG, anchor="start"))
    p.append(mtext(80, Y1 + 18, "12 500 запитів/с\n≈ 51 МБ/с", size=11.5, color=MUTED, anchor="start", lh=1.3))
    p += axis(Y1 + 70)
    for k in range(8):
        x = T0 + k * UNIT
        p.append(rect(x + 3, Y1 + 44, UNIT - 6, 52, fill=COOL, stroke=NEG, sw=1.6, rx=4))
    p.append(text(T0 + TW / 2, Y1 + 128, "вісім запитів поспіль — вісім затримок підряд", size=11.5, color=MUTED))

    # ── глибина 8
    Y2 = 380
    p.append(mtext(80, Y2 - 6, "глибина 8", size=14, bold=True, color=POS, anchor="start"))
    p.append(mtext(80, Y2 + 18, "100 000 запитів/с\n≈ 410 МБ/с", size=11.5, color=MUTED, anchor="start", lh=1.3))
    p += axis(Y2 + 118)
    for k in range(8):
        y = Y2 + 34 + k * 10
        p.append(rect(T0 + 3, y, UNIT - 6, 8, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
    p.append(text(T0 + TW / 2, Y2 + 176,
                  "ті самі вісім запитів у польоті одночасно — одна затримка на всіх", size=11.5, color=MUTED))

    p.append(text(W / 2, H - 30,
                  "пропускна здатність = глибина черги ÷ затримка",
                  size=14, bold=True, color=FIELD))

    render(os.path.join(OUT, "queue-depth.svg"), W, H, *p,
           title="Глибина черги визначає, скільки вдається взяти з носія за ту саму затримку")


# ── 4. Хвіст файлу на прямому шляху ────────────────────────────────────────────
def fig_tail():
    W, H = 1180, 570
    p = []

    p.append(text(W / 2, 44, "хвіст файлу: розмір 5 000 000 байтів, блок 4096",
                  size=15, bold=True, color=INK))
    p.append(text(W / 2, 70, "1220 цілих блоків = 4 997 120 байтів; на хвіст лишається 2880",
                  size=12, color=MUTED))

    BX, BWD, BH = 470, 600, 54
    W1 = BWD * 2880 / 4096.0

    rows = [
        (120, "джерело", "read на 4096 байтів\nзі зміщення 4 997 120",
         "2880 байтів даних", GREEN, "за кінцем файлу", GREY,
         "ядро віддало 2880 — це не помилка, а кінець файлу"),
        (260, "буфер", "хвіст буфера\nзанулюємо самі",
         "2880 байтів даних", GREEN, "1216 нулів", WARM,
         "інакше на носій поїхало б чуже сміття з купи"),
        (400, "ціль", "write на 4096 байтів\nз того самого зміщення",
         "2880 потрібних", GREEN, "1216 зайвих", WARM,
         "файл вийшов на 5 001 216 → ftruncate до 5 000 000"),
    ]

    for (y, name, what, l1, c1, l2, c2, note) in rows:
        p.append(mtext(80, y + 20, name, size=14, bold=True, color=INK, anchor="start"))
        p.append(mtext(80, y + 46, what, size=11, color=MUTED, anchor="start", lh=1.35))
        p.append(rect(BX, y, W1, BH, fill=c1, stroke=POS, sw=1.6, rx=4))
        p.append(text(BX + W1 / 2, y + 32, l1, size=12, color=INK))
        p.append(rect(BX + W1, y, BWD - W1, BH, fill=c2, stroke=LINE, sw=1.4, rx=4))
        p.append(text(BX + W1 + (BWD - W1) / 2, y + 32, l2, size=11.5, color=MUTED))
        p.append(text(BX + BWD / 2, y + BH + 22, note, size=11, color=MUTED))

    p.append(text(W / 2, H - 40,
                  "прямому шляху нема де підмішати хвіст до наявного сектора — тому пишемо цілий блок і вкорочуємо файл",
                  size=12.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "tail.svg"), W, H, *p,
           title="Хвіст файлу: читання коротшає на кінці, запис округлюється вгору, довжину повертає ftruncate")


fig_two_paths()
fig_alignment()
fig_queue_depth()
fig_tail()
print("готово")
