# -*- coding: utf-8 -*-
"""Фігури до статті «Двопортова пам'ять». Виконати: python figs.py
Вивід — ./img/*.svg. Залежність — svgkit зі scripts/ (не переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: архітектура — два порти, спільне ядро комірок ──────────────────
def arch():
    W, H = 720, 380
    p = []
    # спільне ядро памʼяті
    core_x, core_y, core_w, core_h = W/2 - 90, 120, 180, 150
    p.append(rect(core_x, core_y, core_w, core_h, fill="#eef3ff", stroke=LINE, sw=2))
    p.append(text(W/2, core_y - 10, "Спільне ядро комірок", size=14, bold=True))
    # сітка комірок усередині
    for r in range(4):
        for c in range(4):
            cx = core_x + 22 + c * 34
            cy = core_y + 24 + r * 34
            p.append(rect(cx, cy, 26, 26, fill=BG, stroke=MUTED, sw=1, rx=3))
    p.append(text(W/2, core_y + core_h + 22, "одна комірка — один тригер на два порти",
                  size=11, color=MUTED))

    # порт A (ліворуч)
    ax = 70
    p.append(fitbox(ax, 150, 150, 90, "Порт A\n(адреса · дані · запис)",
                    size=13, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(text(ax + 75, 128, "Пристрій ліворуч", size=12, color=INK))
    p.append(arrow(ax + 150, 195, core_x, 195, color=FIELD, sw=2.2))

    # порт B (праворуч)
    bx = W - 70 - 150
    p.append(fitbox(bx, 150, 150, 90, "Порт B\n(адреса · дані · запис)",
                    size=13, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(text(bx + 75, 128, "Пристрій праворуч", size=12, color=INK))
    p.append(arrow(bx, 195, core_x + core_w, 195, color=POS, sw=2.2))

    p.append(text(W/2, 330,
                  "Кожен порт — власна шина адреси й даних; обидва бачать ті самі комірки.",
                  size=12, color=INK))
    render(os.path.join(IMG, "arch.svg"), W, H, *p, title="Двопортова памʼять: два незалежні вікна в один масив")


# ── Фігура 2: зона зіткнення й рішення арбітра (BUSY) ────────────────────────
def collision():
    W, H = 720, 400
    p = []
    # дві адресні лінії, що збігаються
    p.append(text(120, 70, "Порт A ← адреса 0x100", size=13, bold=True, color=FIELD, anchor="start"))
    p.append(text(120, 96, "Порт B ← адреса 0x100", size=13, bold=True, color=POS, anchor="start"))
    p.append(text(120, 122, "…збіг у ту саму мить", size=12, color=MUTED, anchor="start"))

    # ромб-рішення
    dcx, dcy = W/2, 200
    dw, dh = 210, 96
    diamond = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
               'fill="#fff7e6" stroke="%s" stroke-width="2"/>' %
               (dcx, dcy - dh/2, dcx + dw/2, dcy, dcx, dcy + dh/2, dcx - dw/2, dcy, LINE))
    p.append(diamond)
    p.append(mtext(dcx, dcy - 6, ["Арбітр: чия адреса", "стала першою?"], size=13, bold=True))

    p.append(arrow(300, 100, dcx - 60, dcy - 20, color=LINE, sw=1.8))

    # переможець
    p.append(fitbox(80, 300, 250, 70,
                    "Переможець: BUSY = 1\nдоступ дозволено, чекати не треба",
                    size=12, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(dcx - 40, dcy + 40, 200, 300, color=FIELD, sw=2))

    # той, хто програв
    p.append(fitbox(W - 80 - 250, 300, 250, 70,
                    "Той, хто спізнився: BUSY = 0\nчекай, поки перший завершить",
                    size=12, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(dcx + 40, dcy + 40, W - 200, 300, color=POS, sw=2))

    render(os.path.join(IMG, "collision.svg"), W, H, *p,
           title="Одна адреса — два порти: арбітр вирішує за різницею часу")


# ── Фігура 3: семафор — «запиши 0, прочитай назад» ──────────────────────────
def semaphore():
    W, H = 720, 430
    p = []
    lat_x, lat_y, lat_w, lat_h = W/2 - 60, 175, 120, 70
    p.append(rect(lat_x, lat_y, lat_w, lat_h, fill="#eef3ff", stroke=LINE, sw=2))
    p.append(text(W/2, lat_y - 10, "Один латч-семафор", size=13, bold=True))
    p.append(text(W/2, lat_y + lat_h/2 + 6, "перемагає той,", size=12, color=MUTED))
    p.append(text(W/2, lat_y + lat_h/2 + 22, "хто зайшов першим", size=12, color=MUTED))

    # A пише 0
    p.append(fitbox(50, 90, 230, 60, "A: пише 0 у семафор",
                    size=13, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(165, 150, lat_x + 20, lat_y, color=FIELD, sw=2))
    # B пише 0 майже одночасно
    p.append(fitbox(W - 50 - 230, 90, 230, 60, "B: пише 0 у той самий семафор",
                    size=12, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(W - 165, 150, lat_x + lat_w - 20, lat_y, color=POS, sw=2))

    # A читає назад 0 — володіє
    p.append(fitbox(50, 320, 230, 80,
                    "A читає назад: 0\n→ ресурс мій",
                    size=12, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(lat_x + 20, lat_y + lat_h, 165, 320, color=FIELD, sw=2))
    # B читає назад 1 — програв
    p.append(fitbox(W - 50 - 230, 320, 230, 80,
                    "B читає назад: 1\n→ зайнято, чекай",
                    size=12, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(lat_x + lat_w - 20, lat_y + lat_h, W - 165, 320, color=POS, sw=2))

    render(os.path.join(IMG, "semaphore.svg"), W, H, *p,
           title="Семафор: запиши 0 і прочитай назад")


# ── Фігура (proj): захоплення замка — переможець володіє, спізнілий іде робити інше ──
def lock_flow():
    W, H = 760, 470
    p = []
    # один семафорний латч по центру зверху
    lat_x, lat_y, lat_w, lat_h = W/2 - 70, 96, 140, 66
    p.append(rect(lat_x, lat_y, lat_w, lat_h, fill="#fff7e6", stroke=LINE, sw=2))
    p.append(text(W/2, lat_y - 12, "Один латч-семафор", size=13, bold=True))
    p.append(mtext(W/2, lat_y + lat_h/2 - 2, ["залізо пропускає", "лише одного"],
                   size=11, color=MUTED))

    # обидва ядра пишуть 0 у той самий латч
    p.append(fitbox(40, 40, 220, 44, "Ядро A: пише 0", size=13,
                    fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(150, 84, lat_x + 24, lat_y, color=FIELD, sw=2))
    p.append(fitbox(W - 40 - 220, 40, 220, 44, "Ядро B: пише 0 (майже водночас)",
                    size=11, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(W - 150, 84, lat_x + lat_w - 24, lat_y, color=POS, sw=2))

    # переможець ліворуч: читає назад 0 → володіє блоком
    p.append(fitbox(40, 210, 250, 66,
                    "A читає назад: 0\n→ замок мій, блок мій",
                    size=12, fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(lat_x + 24, lat_y + lat_h, 165, 210, color=FIELD, sw=2))
    p.append(fitbox(40, 320, 250, 60,
                    "Працює зі скринькою\nпід захистом", size=12,
                    fill=BG, stroke=FIELD, sw=1.5))
    p.append(arrow(165, 276, 165, 320, color=FIELD, sw=2))
    p.append(fitbox(40, 410, 250, 40, "Віддає замок: пише 1", size=12,
                    fill=BG, stroke=FIELD, sw=1.5))
    p.append(arrow(165, 380, 165, 410, color=FIELD, sw=2))

    # спізнілий праворуч: читає назад 1 → НЕ чекає, іде робити інше
    p.append(fitbox(W - 40 - 250, 210, 250, 66,
                    "B читає назад: 1\n→ замок у сусіда",
                    size=12, fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(lat_x + lat_w - 24, lat_y + lat_h, W - 165, 210, color=POS, sw=2))
    p.append(fitbox(W - 40 - 250, 320, 250, 60,
                    "НЕ чекає — іде робити\nсвоє (крутить радіо)", size=12,
                    fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(W - 165, 276, W - 165, 320, color=POS, sw=2))
    p.append(fitbox(W - 40 - 250, 410, 250, 40, "Спробує знову за мить", size=12,
                    fill=BG, stroke=POS, sw=1.5))
    p.append(arrow(W - 165, 380, W - 165, 410, color=POS, sw=2))

    render(os.path.join(IMG, "lock-flow.svg"), W, H, *p,
           title="Замок «запиши 0, прочитай назад»: спізнілий не чекає, а йде робити інше")


# ── Фігура (proj): розклад скриньки в DPRAM + окремий простір семафорів ──────
def mailbox_layout():
    W, H = 760, 470
    p = []

    # ── ліворуч: карта однієї скриньки (кільце) ──
    col_x, col_w = 70, 250
    p.append(text(col_x + col_w/2, 66, "Скринька A→B у DPRAM", size=14, bold=True))
    fields = [
        ("head  (пише продюсер)", "#eaf7ee", FIELD),
        ("tail  (пише споживач)", "#fdeef0", POS),
        ("_pad  (вирівнювання)",  "#f0f0f0", MUTED),
        ("slot[0]", "#eef3ff", MUTED),
        ("slot[1]", "#eef3ff", MUTED),
        ("…       slot[15]", "#eef3ff", MUTED),
    ]
    fy, fh, gap = 88, 44, 6
    for i, (name, fill, col) in enumerate(fields):
        y = fy + i * (fh + gap)
        p.append(rect(col_x, y, col_w, fh, fill=fill, stroke=col, sw=1.8))
        p.append(text(col_x + 12, y + fh/2 + 4, name, size=12, color=INK, anchor="start"))
    # зростання адреси вниз
    p.append(text(col_x - 18, fy + 6, "0x000", size=10, color=MUTED, anchor="end"))
    last_y = fy + (len(fields) - 1) * (fh + gap)
    p.append(text(col_x - 18, last_y + fh, "адреса ↓", size=10, color=MUTED, anchor="end"))
    p.append(text(col_x + col_w/2, last_y + fh + 26,
                  "друга скринька B→A — такий самий блок нижче", size=10.5, color=MUTED))

    # ── праворуч: окремий простір семафорних латчів ──
    sem_x, sem_w = W - 70 - 250, 250
    p.append(text(sem_x + sem_w/2, 66, "Семафори — ОКРЕМИЙ простір", size=14, bold=True))
    p.append(text(sem_x + sem_w/2, 84, "(інше залізо, не масив даних)", size=11, color=MUTED))
    scols = 4
    scw = sem_w / scols
    sch = 40
    for i in range(8):
        r, c = i // scols, i % scols
        x = sem_x + c * scw
        y = 100 + r * (sch + 10)
        hot = i in (0, 1)
        p.append(rect(x, y, scw - 8, sch,
                      fill="#fff7e6" if hot else BG,
                      stroke=POS if hot else MUTED, sw=2 if hot else 1.3, rx=4))
        p.append(text(x + (scw - 8)/2, y + sch/2 + 4, "S%d" % i, size=12,
                      bold=hot, color=INK))
    p.append(text(sem_x + sem_w/2, 230,
                  "S0 стереже A→B,  S1 — B→A", size=11.5, bold=True, color=POS))
    p.append(text(sem_x + sem_w/2, 250, "решта латчів — вільні", size=10.5, color=MUTED))

    # ── низ: спільна для обох порталів думка про базу/зміщення ──
    note_y = 300
    p.append(fitbox(sem_x, note_y, sem_w, 130,
                    "Обидва ядра накладають ТУ САМУ\n"
                    "struct на DPRAM.\n\n"
                    "Базова адреса в кожного СВОЯ,\n"
                    "а зміщення полів — однакові\n"
                    "до байта.",
                    size=12, fill="#eef3ff", stroke=LINE, sw=1.5))

    render(os.path.join(IMG, "mailbox-layout.svg"), W, H, *p,
           title="Розклад скриньки в спільній памʼяті: кільце + окремі семафори")


# ── Фігура (hist): конфлікт на однопортовій памʼяті → розвʼязок VRAM ─────────
def hist_contention():
    W, H = 720, 470
    p = []
    # Ліворуч: однопортова памʼять — двоє тягнуться до одних воріт
    p.append(text(180, 60, "Однопортова DRAM", size=15, bold=True))
    mem_x, mem_y, mem_w, mem_h = 120, 150, 120, 110
    p.append(rect(mem_x, mem_y, mem_w, mem_h, fill="#eef3ff", stroke=LINE, sw=2))
    p.append(mtext(mem_x + mem_w/2, mem_y + mem_h/2 - 6, ["кадр", "у памʼяті"],
                   size=12, color=MUTED))
    p.append(fitbox(40, 300, 130, 56, "Процесор\nхоче писати", size=12,
                    fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(fitbox(190, 300, 130, 56, "Відеовихід\nчитає кадр", size=12,
                    fill="#fdeef0", stroke=POS, sw=2, bold=True))
    # обидва в одні ворота — стрілки збігаються у той самий бік памʼяті
    p.append(arrow(105, 300, mem_x + 20, mem_y + mem_h, color=FIELD, sw=2))
    p.append(arrow(255, 300, mem_x + mem_w - 20, mem_y + mem_h, color=POS, sw=2))
    p.append(text(180, 400, "одні ворота на двох →", size=12, color=INK))
    p.append(text(180, 418, "черга, затинання", size=12, bold=True, color=POS))

    # роздільник
    p.append(line(370, 90, 370, 430, color=MUTED, sw=1, dash="4,4"))

    # Праворуч: VRAM — довільний порт + послідовний порт зі зсувним регістром
    p.append(text(545, 60, "VRAM: два різні порти", size=15, bold=True))
    ar_x, ar_y, ar_w, ar_h = 480, 150, 130, 90
    p.append(rect(ar_x, ar_y, ar_w, ar_h, fill="#eef3ff", stroke=LINE, sw=2))
    p.append(mtext(ar_x + ar_w/2, ar_y + ar_h/2 - 4, ["масив", "DRAM"], size=12, color=MUTED))
    # зсувний регістр знизу масиву
    sr_y = ar_y + ar_h + 16
    cells = 8
    cw = ar_w / cells
    for i in range(cells):
        p.append(rect(ar_x + i*cw, sr_y, cw - 2, 24, fill=BG, stroke=MUTED, sw=1, rx=2))
    p.append(text(ar_x + ar_w/2, sr_y + 52, "зсувний регістр (цілий рядок)", size=11, color=MUTED))
    # довільний порт зверху (процесор)
    p.append(fitbox(440, 300, 120, 56, "Процесор →\nдовільний порт", size=11,
                    fill="#eaf7ee", stroke=FIELD, sw=2, bold=True))
    p.append(arrow(500, 300, ar_x + 20, ar_y + ar_h, color=FIELD, sw=2))
    # послідовний порт (SCLK) праворуч від регістра
    p.append(fitbox(605, 300, 90, 56, "Відео →\nSCLK", size=11,
                    fill="#fdeef0", stroke=POS, sw=2, bold=True))
    p.append(arrow(ar_x + ar_w, sr_y + 12, 605, sr_y + 12, color=POS, sw=2))
    p.append(text(560, 400, "різні ворота →", size=12, color=INK))
    p.append(text(560, 418, "нікому не заважають", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, "hist-contention.svg"), W, H, *p,
           title="Що винайшли 1980-го: розвести процесор і кадр по різних портах")


# ── Фігура (hist): часова смуга — ідея → патент → чип → продукт ──────────────
def hist_timeline():
    W, H = 820, 340
    p = []
    ax0, ax1, ay = 90, W - 90, 150
    p.append(line(ax0, ay, ax1, ay, color=LINE, sw=2))
    # позначки років
    years = [
        (1973, "Xerox Alto:\nмікрокод краде\nтакти процесора", POS, -1),
        (1980, "IBM Research:\nідея асиметрії\nDill·Ling·Matick", FIELD, 1),
        (1984, "TI TMS4161:\nперший чип VRAM\n(Guttag + MOS)", NEG, -1),
        (1985, "патент\nUS 4 541 075\n(подано 1982)", MUTED, 1),
        (1986, "IBM RT PC:\nперший продукт\nна VRAM", FIELD, -1),
        (1987, "IBM 8514/A:\nмасова графіка", INK, 1),
    ]
    span = years[-1][0] - years[0][0]
    for yr, label, col, side in years:
        x = ax0 + (ax1 - ax0) * (yr - years[0][0]) / span
        p.append(circle(x, ay, 6, fill=col, stroke=col, sw=1))
        p.append(text(x, ay + (24 if side < 0 else -12) + (0 if side < 0 else 0),
                      str(yr), size=13, bold=True, color=col))
        by = ay - 92 if side > 0 else ay + 40
        p.append(fitbox(x - 68, by, 136, 62, label, size=10.5,
                        fill=BG, stroke=col, sw=1.5, color=INK))
        # тонка ніжка від точки до рамки
        p.append(line(x, ay, x, by + (62 if side > 0 else 0), color=col, sw=1, dash="3,3"))
    p.append(text(W/2, H - 16,
                  "Винахід колективний: ідея й патент — IBM; практичний чип — Texas Instruments.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *p,
           title="Відеопамʼять: ідея → патент → перший чип → перший продукт")


# ── Фігура (comp): симетрична розпіновка двох портів ─────────────────────────
def comp_pinout():
    W, H = 760, 430
    p = []

    # корпус мікросхеми — центральний прямокутник
    chip_x, chip_y, chip_w, chip_h = W / 2 - 130, 80, 260, 300
    p.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#f4f6f8", stroke=LINE, sw=2))
    p.append(text(W / 2, chip_y - 12, "Двопортова SRAM (корпус)", size=14, bold=True))

    # масив комірок усередині
    arr_x, arr_y, arr_w, arr_h = W / 2 - 55, 150, 110, 96
    p.append(rect(arr_x, arr_y, arr_w, arr_h, fill="#eef3ff", stroke=MUTED, sw=1.5))
    p.append(mtext(W / 2, arr_y + 42, ["Масив", "комірок"], size=12, bold=True, color=INK))

    # блок логіки арбітражу й переривань — знизу по центру
    p.append(fitbox(W / 2 - 90, 290, 180, 56,
                    "Логіка арбітражу\nй переривань (BUSY · INT)",
                    size=11, fill="#fff7e6", stroke=LINE, sw=1.5, bold=True))

    y0, dy = 118, 36
    left_pins = ["A0…A9", "I/O0…7", "CE", "OE", "R/W", "BUSY", "INT"]

    # ── лівий порт: виводи ліворуч ──
    lx = chip_x
    p.append(text(lx - 90, y0 - 24, "Лівий порт (L)", size=13, bold=True, color=FIELD))
    for i, name in enumerate(left_pins):
        yy = y0 + i * dy
        p.append(line(lx - 62, yy, lx, yy, color=FIELD, sw=2))
        p.append(text(lx - 66, yy + 4, name, size=12, color=INK, anchor="end"))

    # ── правий порт: виводи праворуч (дзеркально) ──
    rx = chip_x + chip_w
    p.append(text(rx + 90, y0 - 24, "Правий порт (R)", size=13, bold=True, color=POS))
    for i, name in enumerate(left_pins):
        yy = y0 + i * dy
        p.append(line(rx, yy, rx + 62, yy, color=POS, sw=2))
        p.append(text(rx + 66, yy + 4, name, size=12, color=INK, anchor="start"))

    # живлення знизу
    p.append(text(W / 2, H - 16,
                  "Живлення (VCC) і земля (GND) — спільні для обох портів",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "comp-pinout.svg"), W, H, *p,
           title="Симетрична розпіновка: два однакові порти в один масив")


if __name__ == "__main__":
    arch()
    collision()
    semaphore()
    lock_flow()
    mailbox_layout()
    hist_contention()
    hist_timeline()
    comp_pinout()
    print("OK: arch.svg, collision.svg, semaphore.svg, lock-flow.svg, mailbox-layout.svg, "
          "hist-contention.svg, hist-timeline.svg, comp-pinout.svg")
