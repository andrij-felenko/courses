# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── bypass: DMA пише в пам'ять повз MMU процесора; IOMMU затуляє сліпу зону ──
# Ідея: кожен доступ ЯДРА йде крізь MMU (переклад+захист), а пристрій із DMA
# б'є прямо у фізичну пам'ять, MMU його не бачить → будь-яка адреса без перевірки.
# Додаємо IOMMU на шлях пристрою — і він теж під наглядом.
def fig_bypass():
    W, H = 770, 470
    p = []

    def panel(y0, title, guarded):
        out = []
        out.append(text(34, y0 - 10, title, size=13, color=INK, bold=True, anchor="start"))
        # процесор
        cx, cy = 50, y0 + 16
        out.append(rect(cx, cy, 104, 52, fill="#eafaf0", stroke=INK, sw=1.6))
        out.append(text(cx + 52, cy + 24, "процесор", size=11.5, color=INK, bold=True))
        out.append(text(cx + 52, cy + 40, "(ядро)", size=9, color=MUTED))
        # MMU на шляху ядра
        mx = cx + 176
        out.append(rect(mx, cy, 108, 52, fill="#eef4ff", stroke=NEG, sw=1.7, rx=6))
        out.append(text(mx + 54, cy + 23, "MMU", size=12.5, color=NEG, bold=True))
        out.append(text(mx + 54, cy + 40, "переклад + захист", size=9, color=MUTED))
        # фізична пам'ять (висока, спільна на обидва рядки)
        rx = 630
        out.append(rect(rx, y0 + 4, 108, 118, fill="#fdf4f4", stroke=INK, sw=1.6, rx=6))
        out.append(text(rx + 54, y0 + 28, "фізична", size=11, color=INK, bold=True))
        out.append(text(rx + 54, y0 + 44, "пам'ять", size=11, color=INK, bold=True))
        # ядро → MMU → пам'ять (перевірено)
        out.append(arrow(cx + 104, cy + 26, mx - 5, cy + 26, color=FIELD, sw=2.0))
        out.append(arrow(mx + 108, cy + 26, rx - 5, y0 + 40, color=FIELD, sw=2.0))
        # пристрій із DMA
        dx, dy = cx, y0 + 92
        out.append(rect(dx, dy, 104, 48, fill="#f6f6f9", stroke=INK, sw=1.6))
        out.append(text(dx + 52, dy + 22, "пристрій", size=11.5, color=INK, bold=True))
        out.append(text(dx + 52, dy + 38, "(DMA)", size=9, color=MUTED))
        if guarded:
            ix = mx
            out.append(rect(ix, dy, 108, 48, fill="#eafaf0", stroke=FIELD, sw=1.9, rx=6))
            out.append(text(ix + 54, dy + 21, "IOMMU", size=12.5, color=FIELD, bold=True))
            out.append(text(ix + 54, dy + 38, "переклад + захист", size=9, color=MUTED))
            out.append(arrow(dx + 104, dy + 24, ix - 5, dy + 24, color=FIELD, sw=2.0))
            out.append(arrow(ix + 108, dy + 24, rx - 5, y0 + 86, color=FIELD, sw=2.0))
            out.append(text(ix + 54, dy + 74, "лише дозволена пам'ять", size=9.5, color=FIELD, bold=True))
        else:
            # пристрій → пам'ять навпростець, повз MMU (небезпека)
            out.append(arrow(dx + 104, dy + 24, rx - 5, y0 + 96, color=POS, sw=2.3))
            out.append(text(dx + 150, dy + 74, "будь-яка адреса — без перевірки", size=10, color=POS, bold=True, anchor="start"))
        return out

    p += panel(66, "Без IOMMU: DMA пише в пам'ять повз MMU", guarded=False)
    p += panel(296, "З IOMMU: пристрій теж під наглядом", guarded=True)

    render(os.path.join(OUT, "bypass.svg"), W, H, *p,
           title="MMU стереже доступ ядра — але DMA його обходить, доки немає IOMMU")


# ── translate: IOMMU перекладає «хто питає + що перекласти» ──────────────────
# Ідея: пристрій шле пару (RequesterID, IOVA). IOMMU спершу за RequesterID
# добирає ТАБЛИЦЮ саме цього пристрою (домен), тоді проходить IO-таблицею й
# дає фізичну адресу — або ПОМИЛКУ, якщо ця IOVA не замаплена цьому пристрою.
def fig_translate():
    W, H = 780, 400
    p = []

    # запит пристрою
    p.append(rect(40, 150, 150, 76, fill="#f6f6f9", stroke=INK, sw=1.6, rx=6))
    p.append(text(115, 172, "пристрій шле:", size=10.5, color=INK, bold=True))
    p.append(text(115, 194, "RequesterID = 03:00.0", size=9.5, color=NEG, bold=True))
    p.append(text(115, 212, "IOVA = 0x8000", size=9.5, color=FIELD, bold=True))

    # IOMMU — велика коробка з двома кроками
    ix, iy = 250, 88
    p.append(rect(ix, iy, 250, 210, fill="#eafaf0", stroke=FIELD, sw=1.9, rx=10))
    p.append(text(ix + 125, iy + 24, "IOMMU", size=14, color=FIELD, bold=True))
    # крок 1: за RequesterID → таблиця пристрою
    p.append(rect(ix + 20, iy + 40, 210, 66, fill=BG, stroke=NEG, sw=1.4, rx=6))
    p.append(text(ix + 125, iy + 60, "1. за RequesterID —", size=10, color=NEG, bold=True))
    p.append(text(ix + 125, iy + 78, "добрати таблицю", size=10, color=NEG, bold=True))
    p.append(text(ix + 125, iy + 96, "саме цього пристрою", size=9, color=MUTED))
    # крок 2: прохід IO-таблицею IOVA→PA
    p.append(rect(ix + 20, iy + 118, 210, 66, fill=BG, stroke=POS, sw=1.4, rx=6))
    p.append(text(ix + 125, iy + 138, "2. прохід IO-таблицею:", size=10, color=POS, bold=True))
    p.append(text(ix + 125, iy + 156, "IOVA → фізична адреса", size=10, color=POS, bold=True))
    p.append(text(ix + 125, iy + 174, "(або ПОМИЛКА)", size=9, color=MUTED))

    # запит → IOMMU
    p.append(arrow(190, 188, ix - 5, iy + 73, color=INK, sw=1.9))

    # два виходи
    ox = ix + 250
    # успіх: фізична адреса
    p.append(rect(ox + 30, iy + 44, 200, 58, fill="#fdf4f4", stroke=POS, sw=1.7, rx=6))
    p.append(text(ox + 130, iy + 66, "замаплено ✓", size=11, color=POS, bold=True))
    p.append(text(ox + 130, iy + 86, "фізична адреса 0x4A000", size=9.5, color=INK))
    p.append(arrow(ix + 230, iy + 73, ox + 28, iy + 73, color=POS, sw=2.0))
    # помилка
    p.append(rect(ox + 30, iy + 128, 200, 58, fill="#eef4ff", stroke=NEG, sw=1.7, rx=6))
    p.append(text(ox + 130, iy + 150, "не замаплено ✕", size=11, color=NEG, bold=True))
    p.append(text(ox + 130, iy + 170, "переривання-помилка", size=9.5, color=INK))
    p.append(arrow(ix + 230, iy + 151, ox + 28, iy + 151, color=NEG, sw=2.0))

    p.append(text(W / 2, H - 18, "Ключова відмінність від MMU ядра: спершу «хто питає?» (RequesterID), і лише тоді «що перекласти?»",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "translate.svg"), W, H, *p,
           title="IOMMU: за RequesterID — таблиця пристрою, тоді переклад IOVA у фізичну адресу")


# ── confine: замкнення пристрою + суцільний вигляд розкиданої пам'яті ────────
# Ідея: у кожного пристрою — власна суцільна IOVA, яку IOMMU розкладає на
# РОЗКИДАНІ фізичні кадри у ВІДВЕДЕНІЙ пристрою ділянці. Спроба сягнути поза неї
# (чужу пам'ять) → помилка. Так одразу і захист, і зникнення scatter-gather.
def fig_confine():
    W, H = 780, 430
    p = []

    # два пристрої з власною суцільною IOVA
    def iova_strip(x, y, col, name, blocks):
        out = []
        out.append(text(x + 60, y - 10, name, size=11, color=col, bold=True))
        out.append(text(x + 60, y + 78, "суцільна IOVA", size=9, color=MUTED))
        for k in range(4):
            yy = y + k * 17
            out.append(rect(x, yy, 120, 15, fill="#f6f6f9", stroke=col, sw=1.2, rx=2))
            out.append(text(x + 60, yy + 12, "IOVA-блок %d" % k, size=9, color=INK))
        return out

    p += iova_strip(40, 70, NEG, "пристрій A", 4)
    p += iova_strip(40, 250, FIELD, "пристрій B", 4)

    # IOMMU з двома таблицями
    ix = 260
    p.append(rect(ix, 90, 130, 250, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(ix + 65, 116, "IOMMU", size=13, color=FIELD, bold=True))
    p.append(rect(ix + 18, 132, 94, 76, fill=BG, stroke=NEG, sw=1.3, rx=5))
    p.append(text(ix + 65, 158, "таблиця A", size=9.5, color=NEG, bold=True))
    p.append(text(ix + 65, 176, "→ ділянка A", size=9, color=MUTED))
    p.append(rect(ix + 18, 224, 94, 76, fill=BG, stroke=FIELD, sw=1.3, rx=5))
    p.append(text(ix + 65, 250, "таблиця B", size=9.5, color=FIELD, bold=True))
    p.append(text(ix + 65, 268, "→ ділянка B", size=9, color=MUTED))

    # фізична пам'ять — стовпчик кадрів, ділянки A і B рознесені
    px = 560
    p.append(text(px + 70, 58, "фізична пам'ять", size=11, color=INK, bold=True))
    frames = [
        ("A", NEG), ("—", None), ("A", NEG), ("B", FIELD),
        ("—", None), ("A", NEG), ("ядро", None), ("B", FIELD),
        ("A", NEG), ("B", FIELD),
    ]
    fy = 72
    for k, (lab, col) in enumerate(frames):
        yy = fy + k * 30
        fill = "#f0f1f3"
        stroke = LINE
        if col is NEG:
            fill, stroke = "#eef4ff", NEG
        elif col is FIELD:
            fill, stroke = "#eafaf0", FIELD
        elif lab == "ядро":
            fill, stroke = "#fdf4f4", POS
        p.append(rect(px, yy, 140, 26, fill=fill, stroke=stroke, sw=1.3, rx=3))
        p.append(text(px + 70, yy + 18, ("кадр %d  ·  %s" % (k, "вільно" if lab == "—" else lab)),
                      size=9, color=INK))

    # A's blocks → scattered A-frames (green mapping)
    a_frames = [0, 2, 5, 8]
    for k, fr in enumerate(a_frames):
        y_iova = 70 + k * 17 + 7
        y_frame = fy + fr * 30 + 13
        p.append(arrow(160, y_iova, ix - 4, 132 + 38, color=NEG, sw=1.0))
    # єдина показова стрілка домену A → кадри (щоб не захаращувати — одна товста)
    p.append(arrow(ix + 112, 170, px - 4, fy + 0 * 30 + 13, color=NEG, sw=1.4))
    p.append(arrow(ix + 112, 178, px - 4, fy + 5 * 30 + 13, color=NEG, sw=1.1))
    p.append(arrow(ix + 112, 262, px - 4, fy + 3 * 30 + 13, color=FIELD, sw=1.4))
    p.append(arrow(ix + 112, 270, px - 4, fy + 7 * 30 + 13, color=FIELD, sw=1.1))

    # заборонений доступ: A тягнеться до ядра/чужого → блок
    p.append(line(px - 40, fy + 6 * 30 + 13, px - 4, fy + 6 * 30 + 13, color=POS, sw=2.0, dash="5,4"))
    p.append(text(px - 46, fy + 6 * 30 + 2, "A → чужа пам'ять:", size=9, color=POS, bold=True, anchor="end"))
    p.append(text(px - 46, fy + 6 * 30 + 16, "ПОМИЛКА ✕", size=9.5, color=POS, bold=True, anchor="end"))

    p.append(text(W / 2, H - 16, "Суцільні IOVA-блоки лягають на РОЗКИДАНІ фізичні кадри у своїй ділянці; вихід за неї — помилка",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "confine.svg"), W, H, *p,
           title="Кожен пристрій замкнено у своїй ділянці; розкидані кадри він бачить суцільними")


# ── timeline: IOMMU визрівав десятиліттями й багатьма руками ─────────────────
# Ідея: той самий блок — переклад між шиною вводу-виводу й пам'яттю — щоразу
# з'являвся наново (мейнфрейм, міні, робоча станція, графіка, x86, ARM), і
# щоразу з іншої НЕГАЙНОЇ причини (ширина адреси, зручність, захист, віртуалізація).
# Головне, що видно: концепція набагато старша за x86-IOMMU середини 2000-х.
def fig_timeline():
    W = 880
    rows = [
        # (рік, назва, суть-внесок, колір-ера)
        ("≈1975", "DEC PDP-11/70 — Unibus Map",
         "переклад на мосту вводу-виводу: 18-бітна шина сягає 22-бітної пам'яті", NEG),
        ("1979", "IBM 43xx — режим ECPS:VSE",
         "канал мейнфрейма адресує пам'ять віртуально, а не фізично", NEG),
        ("1989", "Sun SBus — DVMA",
         "окремий IOMMU-блок на шині робочої станції перекладає адреси пристроїв", FIELD),
        ("1997", "AGP GART (Intel)",
         "таблиця-переклад для однієї відеокарти — вузький, «графічний» IOMMU", FIELD),
        ("2003", "AMD Athlon 64 — GART у контролері пам'яті",
         "той самий GART у процесорі: 32-бітний пристрій дістає пам'ять над 4 ГБ", FIELD),
        ("2005", "AMD DEV (Pacifica)",
         "посторінкова заборона DMA — захист, іще без перекладу адрес", POS),
        ("2006–09", "Intel VT-d · AMD-Vi",
         "повний IOMMU для всіх пристроїв — масово на x86 заради віртуалізації", POS),
        ("поч. 2010-х", "ARM SMMU",
         "той самий задум у світі ARM; StreamID замість RequesterID", INK),
    ]
    top = 74
    dy = 76
    H = top + (len(rows) - 1) * dy + 62
    axis_x = 210
    card_x = axis_x + 44
    card_w = W - card_x - 30
    ch = 52
    p = []
    # вертикальна вісь часу
    p.append(line(axis_x, top - 10, axis_x, top + (len(rows) - 1) * dy + 10, color=LINE, sw=2.2))
    for i, (year, title, detail, col) in enumerate(rows):
        y = top + i * dy
        # рік — ліворуч від осі
        p.append(text(axis_x - 28, y + 4, year, size=12.5, color=col, bold=True, anchor="end"))
        # сполучна лінія осі → картка
        p.append(line(axis_x + 7, y, card_x - 5, y, color=col, sw=1.5))
        # вузол на осі (білий обідок над лінією)
        p.append(circle(axis_x, y, 7, fill=col, stroke=BG, sw=2.2))
        # картка події
        p.append(rect(card_x, y - ch / 2, card_w, ch, fill=BG, stroke=col, sw=1.6, rx=8))
        p.append(text(card_x + 16, y - 6, title, size=12.5, color=INK, bold=True, anchor="start"))
        p.append(text(card_x + 16, y + 15, detail, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Ідея старша за x86: IOMMU визрівав десятиліттями й багатьма руками")


# ── ownership: естафета володіння (потоковий) vs спільне (когерентний) ───────
# Ідея: потоковий мапінг передає буфер, як естафету — поки ним володіє пристрій
# (між map і unmap), CPU чіпати не можна. Когерентний — спільне володіння без
# передач: обидва бачать той самий стан будь-коли, ціною некешованого доступу.
def fig_ownership():
    W, H = 790, 430
    p = []

    # ── Панель 1: потоковий — естафета ──
    y0 = 74
    p.append(text(40, y0, "Потоковий мапінг — естафета володіння", size=13, color=INK, bold=True, anchor="start"))
    bx, bw = 70, 650
    by, bh = y0 + 46, 46
    zA = 180                 # ширина зони «CPU до»
    zB = 300                 # ширина зони «пристрій»
    x1 = bx + zA             # межа map
    x2 = x1 + zB             # межа unmap
    # зона A: CPU готує
    p.append(rect(bx, by, zA, bh, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(bx + zA / 2, by + 20, "CPU володіє", size=11, color=FIELD, bold=True))
    p.append(text(bx + zA / 2, by + 37, "готує буфер", size=9, color=MUTED))
    # зона B: пристрій (DMA в польоті)
    p.append(rect(x1, by, zB, bh, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(x1 + zB / 2, by + 20, "ПРИСТРІЙ володіє", size=11, color=NEG, bold=True))
    p.append(text(x1 + zB / 2, by + 37, "DMA в польоті — CPU не чіпає", size=9, color=MUTED))
    # зона C: CPU читає
    xc = bx + bw
    p.append(rect(x2, by, xc - x2, bh, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text((x2 + xc) / 2, by + 20, "CPU володіє", size=11, color=FIELD, bold=True))
    p.append(text((x2 + xc) / 2, by + 37, "читає дані", size=9, color=MUTED))
    # маркери подій над баром
    p.append(line(x1, by - 18, x1, by, color=INK, sw=1.4))
    p.append(text(x1, by - 24, "dma_map_single", size=9.5, color=INK, bold=True))
    p.append(line(x2, by - 18, x2, by, color=INK, sw=1.4))
    p.append(text(x2, by - 24, "dma_unmap_single", size=9.5, color=INK, bold=True))
    # вісь часу
    p.append(arrow(bx, by + bh + 24, xc, by + bh + 24, color=MUTED, sw=1.4))
    p.append(text(xc, by + bh + 40, "час", size=9.5, color=MUTED, anchor="end"))

    # ── Панель 2: когерентний — спільне володіння ──
    y2 = 262
    p.append(text(40, y2, "Когерентний мапінг — спільне володіння (замаплено раз)",
                  size=13, color=INK, bold=True, anchor="start"))
    cy = y2 + 74
    # процесор
    p.append(rect(95, cy - 26, 132, 52, fill="#eafaf0", stroke=FIELD, sw=1.7, rx=6))
    p.append(text(161, cy + 5, "процесор", size=11.5, color=INK, bold=True))
    # спільний буфер
    p.append(rect(330, cy - 34, 150, 68, fill="#fff9e6", stroke=INK, sw=1.7, rx=6))
    p.append(text(405, cy - 6, "спільний буфер", size=11, color=INK, bold=True))
    p.append(text(405, cy + 15, "(некешовано)", size=9, color=MUTED))
    # пристрій
    p.append(rect(583, cy - 26, 132, 52, fill="#eef4ff", stroke=NEG, sw=1.7, rx=6))
    p.append(text(649, cy + 5, "пристрій", size=11.5, color=INK, bold=True))
    # двобічні стрілки — завжди, без передач
    p.append(arrow(229, cy - 9, 328, cy - 9, color=FIELD, sw=1.9))
    p.append(arrow(328, cy + 11, 229, cy + 11, color=FIELD, sw=1.9))
    p.append(arrow(482, cy - 9, 581, cy - 9, color=NEG, sw=1.9))
    p.append(arrow(581, cy + 11, 482, cy + 11, color=NEG, sw=1.9))
    p.append(text(405, cy + 56, "обидва читають-пишуть будь-коли, без передач", size=9.5, color=MUTED))

    render(os.path.join(OUT, "ownership.svg"), W, H, *p,
           title="Потоковий мапінг передає буфер естафетою; когерентний — тримають обидва разом")


# ── mapcost: покрокова ціна пари map/unmap + економія мапінгу наперед ────────
# Ідея: пара «замапити/зняти» — це виділення IOVA, запис у таблицю й, найдорожче,
# СИНХРОННЕ знеправлення IOTLB. Тому буфери кільця мапують РАЗ наперед, а на пакет
# платять лише дешевим dma_sync — без IOVA, без таблиці, без IOTLB.
def fig_mapcost():
    import math
    W, H = 810, 470
    p = []

    # ── Ліва колонка: пара map/unmap покроково ──
    p.append(text(40, 66, "Пара «замапити / зняти» — покроково", size=13, color=INK, bold=True, anchor="start"))
    steps = [
        ("dma_map_single", None, "hdr"),
        ("1 · знайти фізичні сторінки буфера", MUTED, "n"),
        ("2 · виділити IOVA (per-CPU кеш → дерево)", NEG, "n"),
        ("3 · вписати IOVA→phys у таблицю домену", NEG, "n"),
        ("4 · повернути dma_addr_t = IOVA", FIELD, "ret"),
        ("dma_unmap_single", None, "hdr"),
        ("5 · викреслити запис із таблиці", MUTED, "n"),
        ("6 · знеправити IOTLB — синхронно!", POS, "hot"),
        ("7 · повернути IOVA розподільнику", MUTED, "n"),
    ]
    x, y, w = 40, 90, 330
    for label, col, kind in steps:
        if kind == "hdr":
            p.append(text(x, y + 13, label, size=11, color=INK, bold=True, anchor="start"))
            y += 26
            continue
        fill, stroke, sw = "#f6f6f9", LINE, 1.2
        if kind == "hot":
            fill, stroke, sw = "#fdecea", POS, 1.9
        elif kind == "ret":
            fill, stroke = "#eafaf0", FIELD
        p.append(rect(x, y, w, 26, fill=fill, stroke=stroke, sw=sw, rx=4))
        p.append(text(x + 10, y + 17, label, size=9.5, color=(col or INK), anchor="start"))
        y += 32
    p.append(text(40, y + 10, "крок 6 коштує як сотні записів у пам'ять",
                  size=9.5, color=POS, bold=True, anchor="start"))

    # ── Права колонка: мапінг наперед (кільце буферів) ──
    rx0 = 440
    p.append(text(rx0, 66, "Мапінг наперед — кільце буферів", size=13, color=INK, bold=True, anchor="start"))
    cx, cy = rx0 + 165, 250
    # старт: мапінг раз
    p.append(rect(rx0, 88, 330, 34, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(cx, 109, "старт: dma_map_single × RING_N  (раз)", size=9.5, color=FIELD, bold=True))
    # кільце буферів
    R = 74
    p.append(circle(cx, cy, R, fill=BG, stroke=LINE, sw=1.3))
    for k in range(8):
        a = -math.pi / 2 + k * 2 * math.pi / 8
        bxk = cx + R * math.cos(a) - 16
        byk = cy + R * math.sin(a) - 10
        p.append(rect(bxk, byk, 34, 21, fill="#eef4ff", stroke=NEG, sw=1.2, rx=3))
        p.append(text(bxk + 17, byk + 14, "b%d" % k, size=9.5, color=NEG))
    p.append(text(cx, cy - 3, "замаплені", size=10, color=INK, bold=True))
    p.append(text(cx, cy + 13, "буфери", size=10, color=INK, bold=True))
    # на пакет: лише sync
    p.append(rect(rx0, 350, 330, 34, fill="#fff9e6", stroke=INK, sw=1.5, rx=5))
    p.append(text(cx, 371, "на пакет: лише dma_sync  (без IOTLB)", size=9.5, color=INK, bold=True))
    # зупинка: зняти раз
    p.append(rect(rx0, 398, 330, 34, fill="#eef4ff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(cx, 419, "зупинка: dma_unmap_single × RING_N  (раз)", size=9.5, color=NEG, bold=True))

    render(os.path.join(OUT, "mapcost.svg"), W, H, *p,
           title="Дорога пара map/unmap: платить IOTLB; мапінг наперед амортизує її на тисячі пакетів")


if __name__ == "__main__":
    fig_bypass()
    fig_translate()
    fig_confine()
    fig_timeline()
    fig_ownership()
    fig_mapcost()
    print("figs: готово")
