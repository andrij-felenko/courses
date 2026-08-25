# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_ports():
    """Регістровий файл як чорна скринька 2R1W: адреси -> дані."""
    W, H = 720, 420
    frags = []
    # центральний блок
    bx, by, bw, bh = 250, 90, 220, 250
    frags.append(rect(bx, by, bw, bh, fill="#eef3fb", stroke=INK, sw=2))
    frags.append(text(bx + bw / 2, by + 34, "Регістровий файл", size=16, bold=True))
    frags.append(text(bx + bw / 2, by + 60, "32 × 32 біти", size=13, color=MUTED))
    # маленька матриця «регістрів» усередині
    for i in range(5):
        yy = by + 84 + i * 26
        frags.append(rect(bx + 30, yy, bw - 60, 18, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
        lbl = "R%d" % i if i < 4 else "…"
        frags.append(text(bx + 46, yy + 13, lbl, size=11, color=MUTED, anchor="start"))
    frags.append(text(bx + bw / 2, by + bh - 12, "R31", size=11, color=MUTED))

    # ── ліворуч: два порти читання (адреса in, дані out) ──
    def read_port(cy, name):
        out = []
        # адреса читання (вхід зверху зліва)
        out.append(arrow(70, cy - 22, bx, cy - 22, color=NEG))
        out.append(text(74, cy - 30, "адреса " + name, size=12, color=NEG, anchor="start", bold=True))
        # дані читання (вихід — стрілка НАЗОВНІ вліво)
        out.append(arrow(bx, cy + 14, 70, cy + 14, color=INK))
        out.append(text(74, cy + 8, "дані " + name + " (32)", size=12, anchor="start"))
        return out

    frags += read_port(150, "A")
    frags += read_port(250, "B")

    # ── праворуч: порт запису ──
    frags.append(arrow(bx + bw + 150, 150, bx + bw, 150, color=POS))
    frags.append(text(bx + bw + 60, 142, "адреса W", size=12, color=POS, anchor="start", bold=True))
    frags.append(arrow(bx + bw + 150, 190, bx + bw, 190, color=POS))
    frags.append(text(bx + bw + 60, 182, "дані W (32)", size=12, color=POS, anchor="start"))
    frags.append(arrow(bx + bw + 150, 230, bx + bw, 230, color=POS))
    frags.append(text(bx + bw + 60, 222, "дозвіл W", size=12, color=POS, anchor="start"))
    # такт знизу
    frags.append(arrow(bx + bw / 2, H - 20, bx + bw / 2, by + bh, color=MUTED))
    frags.append(text(bx + bw / 2, H - 26, "такт", size=12, color=MUTED))

    frags.append(text(W / 2, H - 4, "два порти читання (сині) читають одночасно; один порт запису (червоний) пише по фронту такту",
                      size=11, color=MUTED))
    render(os.path.join(IMG, 'ports.svg'), W, H, *frags)


def fig_readport():
    """Як працює один порт читання: адреса -> дешифратор -> словниковий рядок -> бітова лінія."""
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 26, "Один порт читання: адреса вмикає рядок, комірки виставляють біти", size=15, bold=True))

    # дешифратор адреси
    dx, dy, dw, dh = 110, 90, 90, 250
    frags.append(rect(dx, dy, dw, dh, fill="#eef3fb", stroke=INK, sw=1.5))
    frags.append(mtext(dx + dw / 2, dy + dh / 2 - 20, ["Дешифра-", "тор", "адреси"], size=12, bold=True))
    frags.append(arrow(dx - 60, dy + dh / 2, dx, dy + dh / 2, color=NEG))
    frags.append(text(dx - 62, dy + dh / 2 - 8, "адреса", size=11, color=NEG, anchor="end"))
    frags.append(text(dx - 62, dy + dh / 2 + 12, "(5 біт)", size=10, color=MUTED, anchor="end"))

    # сітка комірок: 4 рядки (регістри) × 3 стовпці (біти)
    rows = 4
    cols = 3
    cw, ch = 74, 46
    gx = dx + dw + 40
    gy = dy
    wl_rows = []
    for r in range(rows):
        ry = gy + r * (ch + 12)
        wl_rows.append(ry + ch / 2)
        active = (r == 1)
        # словникова лінія від дешифратора
        wcol = FIELD if active else MUTED
        frags.append(line(dx + dw, ry + ch / 2, gx, ry + ch / 2, color=wcol, sw=2.2 if active else 1.2))
        rlab = "R%d" % r
        frags.append(text(gx - 8, ry + ch / 2 - 12, rlab, size=10, color=wcol, anchor="end"))
        if active:
            frags.append(text((dx + dw + gx) / 2, ry + ch / 2 - 8, "= 1", size=11, color=FIELD, bold=True))
        for c in range(cols):
            cx = gx + c * (cw + 10)
            cell_fill = "#eafaf0" if active else "#ffffff"
            frags.append(rect(cx, ry, cw, ch, fill=cell_fill, stroke=MUTED if not active else FIELD, sw=1.2))
            frags.append(text(cx + cw / 2, ry + ch / 2 + 4, "комірка", size=10, color=MUTED if not active else INK))

    # бітові лінії (стовпці) вниз до буферів читання
    for c in range(cols):
        cx = gx + c * (cw + 10) + cw / 2
        top = gy
        bot = gy + rows * (ch + 12) + 6
        frags.append(line(cx, top, cx, bot, color=MUTED, sw=1.2, dash="4 3"))
        frags.append(arrow(cx, bot, cx, bot + 24, color=INK))
        frags.append(text(cx, bot + 40, "біт %d" % c, size=10))
    frags.append(text(gx + cols * (cw + 10) + 40, gy + rows * (ch + 12) / 2, "…", size=16, color=MUTED, anchor="start"))

    frags.append(text(W / 2, H - 10,
                      "активний рядок (зелений) — це обраний регістр; лише його комірки керують бітовими лініями порту",
                      size=11, color=MUTED))
    render(os.path.join(IMG, 'read-port.svg'), W, H, *frags)


def fig_datapath():
    """Такт тракту даних: читаємо 2 операнди -> АЛП -> запис назад; проблема читання-під-час-запису."""
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 26, "Один такт: два операнди з файлу -> АЛП -> результат назад", size=15, bold=True))

    # регістровий файл ліворуч
    rfx, rfy, rfw, rfh = 50, 70, 170, 170
    frags.append(rect(rfx, rfy, rfw, rfh, fill="#eef3fb", stroke=INK, sw=1.8))
    frags.append(text(rfx + rfw / 2, rfy + 28, "Регістровий", size=13, bold=True))
    frags.append(text(rfx + rfw / 2, rfy + 46, "файл", size=13, bold=True))

    # два операнди -> АЛП
    ax, ay, aw, ah = 340, 80, 150, 140
    # трапеція АЛП
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" fill="#eef3fb" stroke="%s" stroke-width="1.8"/>' % (
        ax, ay, ax + aw, ay, ax + aw - 30, ay + ah / 2 - 10, ax + aw, ay + ah, ax, ay + ah, ax + 30, ay + ah / 2 - 10, INK))
    frags.append(text(ax + aw / 2, ay + ah / 2 + 4, "АЛП", size=16, bold=True))

    frags.append(arrow(rfx + rfw, rfy + 55, ax, ay + 26, color=NEG))
    frags.append(text((rfx + rfw + ax) / 2, rfy + 44, "операнд A", size=11, color=NEG))
    frags.append(arrow(rfx + rfw, rfy + 110, ax, ay + ah - 26, color=NEG))
    frags.append(text((rfx + rfw + ax) / 2, rfy + 128, "операнд B", size=11, color=NEG))

    # результат -> назад у файл (петля запису, проходить НАД пасткою)
    loopy = 268
    frags.append(arrow(ax + aw, ay + ah / 2, ax + aw + 40, ay + ah / 2, color=POS))
    frags.append(line(ax + aw + 40, ay + ah / 2, ax + aw + 40, loopy, color=POS, sw=1.8))
    frags.append(line(ax + aw + 40, loopy, rfx + rfw / 2, loopy, color=POS, sw=1.8))
    frags.append(arrow(rfx + rfw / 2, loopy, rfx + rfw / 2, rfy + rfh, color=POS))
    frags.append(text(ax + aw + 90, ay + ah / 2 - 8, "результат", size=11, color=POS, anchor="start"))
    frags.append(text((rfx + rfw / 2 + ax) / 2, loopy - 8, "запис по фронту такту", size=11, color=POS))

    # пастка: читання під час запису (2 рядки, широка рамка знизу)
    bx, by, bw, bh = 60, 298, 600, 60
    frags.append(fitbox(bx, by, bw, bh,
                        ["Пастка: читаємо той самий регістр, у який цей же такт пишемо —",
                         "порт читання ще віддає СТАРЕ значення, а не щойно записане"],
                        size=12, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, 'datapath.svg'), W, H, *frags)


def fig_cellgrow():
    """Чому площа ~ квадрат портів: комірка + горизонтальні (словникові) і вертикальні (бітові) канали дротів."""
    W, H = 720, 470
    frags = []
    frags.append(text(W / 2, 26, "Комірка тоне у власних дротах: обидва канали ростуть з числом портів", size=15, bold=True))

    # ── зображуємо ОДНУ комірку у двох варіантах: мало портів і багато ──
    def cell_block(ox, oy, nwl, nbl, side, caption):
        out = []
        core = 40  # сама комірка (транзистори) — стала
        gap = 7    # крок між дротами
        chan_w = nbl * gap + 10   # ширина вертикального каналу (бітові лінії)
        chan_h = nwl * gap + 10   # висота горизонтального каналу (словникові рядки)
        cw = core + chan_w
        ch = core + chan_h
        # рамка «крок комірки» — увесь зайнятий квадрат
        out.append(rect(ox, oy, cw, ch, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=4))
        # ядро-комірка (сталі транзистори) у кутку
        out.append(rect(ox + 6, oy + 6, core, core, fill="#eef3fb", stroke=INK, sw=1.6, rx=3))
        out.append(mtext(ox + 6 + core / 2, oy + 6 + core / 2 - 6, ["2 інв.", "комірка"], size=10, bold=True))
        # словникові рядки — горизонтальні, знизу
        for i in range(nwl):
            yy = oy + 6 + core + 6 + i * gap
            out.append(line(ox + 4, yy, ox + cw - 4, yy, color=FIELD, sw=1.6))
        out.append(text(ox + cw - 6, oy + 6 + core + chan_h - 2, "%d словн." % nwl,
                        size=10, color=FIELD, anchor="end"))
        # бітові лінії — вертикальні, праворуч
        for j in range(nbl):
            xx = ox + 6 + core + 6 + j * gap
            out.append(line(xx, oy + 4, xx, oy + ch - 4, color=NEG, sw=1.6))
        out.append(text(ox + 6 + core + chan_w - 4, oy + 12, "%d біт." % nbl,
                        size=10, color=NEG, anchor="end"))
        # підпис зі стороною
        out.append(text(ox + cw / 2, oy + ch + 20, caption, size=12, bold=True))
        out.append(text(ox + cw / 2, oy + ch + 38, "сторона ≈ %d" % side, size=11, color=MUTED))
        return out, cw, ch

    # 2R1W: словникових 3, бітових 4
    b1, w1, h1 = cell_block(70, 70, 3, 4, 1, "2R1W")
    frags += b1
    # 8R4W: словникових 12, бітових 16 — помітно ширше в ОБИДВА боки
    b2, w2, h2 = cell_block(360, 70, 12, 16, 2, "8R4W")
    frags += b2

    # стрілка «×2 порти → ×4 площа»
    frags.append(arrow(70 + w1 + 20, 70 + h1 / 2, 350, 70 + h2 / 2, color=POS))
    frags.append(mtext((70 + w1 + 350) / 2 + 10, 70 + h1 / 2 - 30,
                       ["портів ×2", "→ сторона ×2", "→ площа ×4"], size=11, color=POS, bold=True))

    frags.append(fitbox(60, H - 70, 600, 44,
                        ["Транзистори комірки не змінились — але дроти обабіч розсунули її вчетверо.",
                         "Ростуть ОБИДВА канали (словникові + бітові) → сторона лінійна за портами → площа квадратична."],
                        size=12, fill="#fdf6ec", stroke=MUTED))
    render(os.path.join(IMG, 'cell-grow.svg'), W, H, *frags)


def fig_mitigations():
    """Три пом'якшення порт-тиску: банки, копії для читання, double-pumping."""
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 26, "Як збити порт-тиск, не будуючи монстра на 8 портів", size=15, bold=True))

    colw = 210
    x0 = 30
    gap = 20
    top = 60
    boxh = 300

    def panel(ox, title, sub, body_lines, verdict):
        out = []
        out.append(rect(ox, top, colw, boxh, fill="#f7f9fc", stroke=INK, sw=1.4, rx=8))
        out.append(text(ox + colw / 2, top + 24, title, size=14, bold=True))
        out.append(text(ox + colw / 2, top + 44, sub, size=11, color=MUTED))
        yy = top + 74
        for ln in body_lines:
            out.append(text(ox + colw / 2, yy, ln, size=11))
            yy += 20
        out.append(fitbox(ox + 12, top + boxh - 58, colw - 24, 44, verdict,
                          size=11, fill="#eafaf0", stroke=FIELD))
        return out

    frags += panel(x0, "Банки", "розбити масив",
                   ["ділимо регістри", "на 2 половини;", "кожен банк —", "1R + 1W",
                    "конфлікт, якщо", "обидва в одному"],
                   ["8 портів → 2×(1R1W)", "поки доступи в різні банки"])
    frags += panel(x0 + colw + gap, "Копії читання", "реплікувати",
                   ["тримаємо 2 копії", "з однаковим вмістом;", "пишемо в обидві,",
                    "читаємо з кожної", "своєю адресою", "(+копія = +1 R)"],
                   ["Alpha 21264: 2 копії", "integer-файла в реальному кремнії"])
    frags += panel(x0 + 2 * (colw + gap), "Double-pump", "подвоїти такт",
                   ["масив працює", "на 2× частоті;", "два доступи", "за один такт ядра",
                    "1 фізичний порт", "= 2 логічні"],
                   ["2× швидкість замість", "2× дротів — ціна: тактова стеля"])

    render(os.path.join(IMG, 'mitigations.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
#  Фігури для історичного нарису hist-registers-to-register-file.md
# ─────────────────────────────────────────────────────────────────────────────

def fig_accumulator_vs_regs():
    """Дві машини поруч: акумуляторна (одне робоче слово, туди-сюди в пам'ять)
    проти багаторегістрової (числа лишаються під рукою)."""
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 26, "Одне робоче слово проти багатьох регістрів", size=15, bold=True))

    # ── ЛІВОРУЧ: акумуляторна машина ──
    lx = 60
    frags.append(text(lx + 110, 60, "Акумуляторна машина", size=13, bold=True))
    # пам'ять
    memx, memy, memw, memh = lx, 80, 90, 250
    frags.append(rect(memx, memy, memw, memh, fill="#f4f6f8", stroke=INK, sw=1.5))
    frags.append(text(memx + memw / 2, memy + 20, "пам'ять", size=12, bold=True))
    for i in range(6):
        yy = memy + 40 + i * 32
        frags.append(rect(memx + 12, yy, memw - 24, 22, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    # акумулятор
    accx, accy, accw, acch = lx + 150, 175, 74, 44
    frags.append(rect(accx, accy, accw, acch, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(accx + accw / 2, accy + 20, "акум.", size=12, bold=True, color=FIELD))
    frags.append(text(accx + accw / 2, accy + 37, "1 слово", size=9, color=MUTED))
    # стрілки туди-сюди
    frags.append(arrow(memx + memw, accy + 6, accx, accy + 6, color=NEG))
    frags.append(arrow(accx, accy + acch - 6, memx + memw, accy + acch - 6, color=POS))
    frags.append(text((memx + memw + accx) / 2, accy - 8, "load", size=10, color=NEG))
    frags.append(text((memx + memw + accx) / 2, accy + acch + 16, "store", size=10, color=POS))
    frags.append(text(lx + 130, memy + memh + 24, "кожне друге число —", size=10, color=MUTED))
    frags.append(text(lx + 130, memy + memh + 38, "поїздка в повільну пам'ять", size=10, color=MUTED))

    # ── ПРАВОРУЧ: багаторегістрова ──
    rx0 = 420
    frags.append(text(rx0 + 100, 60, "Багато регістрів", size=13, bold=True))
    # ряд регістрів
    rfx, rfy, rfw, rfh = rx0, 100, 190, 200
    frags.append(rect(rfx, rfy, rfw, rfh, fill="#eef3fb", stroke=INK, sw=1.8))
    frags.append(text(rfx + rfw / 2, rfy + 22, "регістровий файл", size=12, bold=True))
    for i in range(5):
        yy = rfy + 40 + i * 30
        lbl = ["r0", "r1", "r2", "r3", "…"][i]
        frags.append(rect(rfx + 20, yy, rfw - 40, 22, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
        frags.append(text(rfx + 34, yy + 16, lbl, size=11, color=INK, anchor="start"))
    # АЛП крутить операнди між регістрами (петля збоку)
    frags.append(arrow(rfx + rfw + 24, rfy + 70, rfx + rfw, rfy + 70, color=NEG))
    frags.append(line(rfx + rfw + 24, rfy + 70, rfx + rfw + 24, rfy + 130, color=INK, sw=1.5))
    frags.append(arrow(rfx + rfw + 24, rfy + 130, rfx + rfw, rfy + 130, color=POS))
    frags.append(text(rfx + rfw + 34, rfy + 104, "АЛП", size=12, bold=True, anchor="start"))
    frags.append(text(rfx + 95, rfy + rfh + 24, "проміжні суми лишаються", size=10, color=MUTED))
    frags.append(text(rfx + 95, rfy + rfh + 38, "у регістрах — без поїздок", size=10, color=MUTED))

    render(os.path.join(IMG, 'accumulator-vs-regs.svg'), W, H, *frags)


def fig_file_meaning():
    """Старе значення слова 'file': упорядкований ряд однакових комірок —
    картки на дроті (filum) / шеренга (rank & file) -> регістровий файл."""
    W, H = 720, 340
    frags = []
    frags.append(text(W / 2, 26, "Чому «файл»: упорядкований ряд однакових комірок", size=15, bold=True))

    # ── ЛІВОРУЧ: картки, нанизані на дріт (filum) ──
    frags.append(text(160, 62, "Картки на дроті (лат. filum)", size=12, bold=True))
    wire_y = 92
    frags.append(line(40, wire_y, 300, wire_y, color=MUTED, sw=2))
    frags.append(circle(40, wire_y, 4, fill=MUTED, stroke=MUTED))
    for i in range(5):
        cx = 72 + i * 48
        frags.append(rect(cx - 18, wire_y + 6, 36, 46, fill="#ffffff", stroke=INK, sw=1.2, rx=2))
        frags.append(line(cx, wire_y, cx, wire_y + 6, color=MUTED, sw=1))
    frags.append(text(160, wire_y + 82, "документи, нанизані по черзі —", size=10, color=MUTED))
    frags.append(text(160, wire_y + 96, "звідси «файл» як ряд за порядком", size=10, color=MUTED))

    # ── ПРАВОРУЧ: шеренга (rank & file) -> регістри ──
    frags.append(text(535, 62, "Шеренга однакових комірок", size=12, bold=True))
    gx0 = 445
    gy0 = 84
    for i in range(6):
        yy = gy0 + i * 32
        active = (i == 2)
        fill = "#eafaf0" if active else "#ffffff"
        st = FIELD if active else MUTED
        frags.append(rect(gx0, yy, 180, 24, fill=fill, stroke=st, sw=1.6 if active else 1.1, rx=3))
        lbl = "r%d" % i if i < 5 else "r31"
        frags.append(text(gx0 + 16, yy + 17, lbl, size=11, color=INK if active else MUTED, anchor="start"))
        num = i if i < 5 else 31
        frags.append(text(gx0 - 12, yy + 17, "%d" % num, size=10, color=MUTED, anchor="end"))
    frags.append(arrow(gx0 - 42, gy0 + 2 * 32 + 12, gx0 - 4, gy0 + 2 * 32 + 12, color=NEG))
    frags.append(text(gx0 - 46, gy0 + 2 * 32 + 7, "за номером", size=10, color=NEG, anchor="end"))
    frags.append(text(535, gy0 + 6 * 32 + 20, "до кожної — за її номером у ряду", size=10, color=MUTED))

    render(os.path.join(IMG, 'file-meaning.svg'), W, H, *frags)


def fig_risc_timeline():
    """Шлях до багатьох регістрів: акумулятор -> перші кілька регістрів
    (CDC 6600, S/360) -> RISC ставить великий файл у центр тракту."""
    W, H = 720, 300
    frags = []
    frags.append(text(W / 2, 26, "Шлях обчислень до великого регістрового файла", size=15, bold=True))

    axis_y = 150
    frags.append(line(50, axis_y, 670, axis_y, color=MUTED, sw=1.5))

    stops = [
        (110, "1940-і", ["акумулятор:", "одне-два слова", "(ENIAC, IAS)"], NEG),
        (285, "1964", ["перші кілька:", "8 у CDC 6600,", "16 у IBM S/360"], INK),
        (460, "1975–80", ["RISC: IBM 801,", "Berkeley, MIPS —", "16–32 регістри"], POS),
        (625, "нині", ["файл — центр", "тракту даних", "(2R1W і ширше)"], FIELD),
    ]
    for x, yr, lines, col in stops:
        frags.append(circle(x, axis_y, 7, fill="#ffffff", stroke=col, sw=2.5))
        frags.append(text(x, axis_y - 16, yr, size=12, bold=True, color=col))
        frags.append(mtext(x, axis_y + 28, lines, size=10, color=MUTED))

    render(os.path.join(IMG, 'risc-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_ports()
    fig_readport()
    fig_datapath()
    fig_cellgrow()
    fig_mitigations()
    fig_accumulator_vs_regs()
    fig_file_meaning()
    fig_risc_timeline()
    print("figs done")
