# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff3"
WARM = "#b8860b"


# ── 1. Два різні числа про один файл ────────────────────────────────────────
def fig_size_vs_blocks():
    W, H = 1080, 560
    p = []
    p.append(text(W / 2, 40, "один файл — два незалежні числа", size=16, bold=True, color=INK))

    sx, sw_, sy, sh = 60, 960, 90, 74
    p.append(rect(sx, sy, sw_, sh, fill=GREY_FILL, stroke=MUTED, sw=1.6, rx=6))

    # два острови даних
    islands = [(sx + 20, 60), (sx + 700, 90)]
    for ix, iw in islands:
        p.append(rect(ix, sy + 2, iw, sh - 4, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))

    p.append(text(sx + 50, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 745, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 400, sy + sh / 2 + 5, "діра: блоків немає взагалі",
                  size=14, color=MUTED, bold=True))

    p.append(text(sx, sy + sh + 26, "зсув 0", size=12, color=MUTED, anchor="start"))
    p.append(text(sx + sw_, sy + sh + 26, "зсув 1 ТіБ", size=12, color=MUTED, anchor="end"))

    # два вимірювачі
    p.append(fitbox(60, 230, 460, 116,
                    ["st_size = 1 099 511 627 776 байтів",
                      "«докуди тягнеться простір зсувів»",
                      "це показує ls -l"],
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(fitbox(620, 230, 400, 116,
                    ["st_blocks = 296 одиниць по 512 Б",
                      "«скільки місця справді віддано»",
                      "це показує du"],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2))

    p.append(arrow(290, 226, 290, sy + sh + 44, color=NEG, sw=1.8))
    p.append(arrow(820, 226, 820, sy + sh + 44, color=WARM, sw=1.8))

    p.append(fitbox(60, 396, 960, 116,
                    ["read за будь-яким зсувом усередині діри повертає нулі —",
                      "і жоден із цих нулів ніде не записаний",
                      "стерти діру не можна: там нема чого стирати"],
                    size=15, fill=RED_FILL, stroke=POS, sw=2, bold=True))

    render(os.path.join(IMG, 'size-vs-blocks.svg'), W, H, *p)


# ── 2. Звідки береться діра: часткове відображення ──────────────────────────
def fig_hole_in_map():
    W, H = 1080, 620
    p = []
    p.append(text(W / 2, 38, "карта блоків описує не всі зсуви файлу", size=16, bold=True, color=INK))

    # ліворуч: карта блоків
    mx, my, mw = 70, 90, 420
    rows = [("блок файлу 0", "1204", True),
            ("блок файлу 1", "1205", True),
            ("блок файлу 2", "—", False),
            ("блок файлу 3", "—", False),
            ("блок файлу 4", "—", False),
            ("блок файлу 5", "7731", True)]
    rh = 46
    p.append(text(mx + mw / 2, my - 12, "карта блоків в inode", size=14, bold=True, color=WARM))
    for i, (nm, num, present) in enumerate(rows):
        y = my + i * rh
        fill = GREEN_FILL if present else GREY_FILL
        stroke = FIELD if present else MUTED
        p.append(rect(mx, y, mw, rh - 6, fill=fill, stroke=stroke, sw=1.6, rx=5))
        p.append(text(mx + 18, y + 26, nm, size=13, anchor="start"))
        p.append(text(mx + mw - 18, y + 26, num, size=13.5, anchor="end", bold=True,
                      color=FIELD if present else POS))

    p.append(text(mx + mw / 2, my + 6 * rh + 24,
                  "прочерк — запис із нулем: носій такого номера не має",
                  size=12.5, color=MUTED))

    # праворуч: що бачить read
    rx0, rw0 = 610, 400
    p.append(text(rx0 + rw0 / 2, my - 12, "що отримує read", size=14, bold=True, color=NEG))
    for i, (nm, num, present) in enumerate(rows):
        y = my + i * rh
        if present:
            p.append(fitbox(rx0, y, rw0, rh - 6, ["4096 байтів, прочитаних із носія"],
                            size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))
        else:
            p.append(fitbox(rx0, y, rw0, rh - 6, ["4096 нулів, породжених ядром"],
                            size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))
        p.append(arrow(mx + mw + 14, y + (rh - 6) / 2, rx0 - 14, y + (rh - 6) / 2,
                       color=FIELD if present else NEG, sw=1.5))

    p.append(fitbox(70, 468, 940, 130,
                    ["чому саме нулі, а не помилка й не сміття з носія:",
                      "помилка зламала б рівність «файл — це масив байтів», у якому читається кожен зсув;",
                      "невичищений блок віддав би чужі дані. Нуль — єдина відповідь, що не робить ні того, ні того"],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2))

    render(os.path.join(IMG, 'hole-in-map.svg'), W, H, *p)


# ── 3. Три стани діапазону, які читаються однаково ──────────────────────────
def fig_three_states():
    W, H = 1160, 620
    p = []
    p.append(text(W / 2, 38, "три різні стани діапазону, і read у всіх трьох дає нулі",
                  size=16, bold=True, color=INK))

    cols = [(50, "діра", POS, RED_FILL,
             ["fallocate --punch-hole",
              "запис за кінець файлу"]),
            (410, "невиписаний екстент", WARM, WARM_FILL,
             ["fallocate (без прапорців)",
              "fallocate --zero-range"]),
            (770, "справжні записані нулі", FIELD, GREEN_FILL,
             ["write буфера з нулів",
              "dd if=/dev/zero"])]
    cw = 340

    for x, ttl, stroke, fill, how in cols:
        p.append(fitbox(x, 70, cw, 46, [ttl], size=15, bold=True,
                        fill=fill, stroke=stroke, sw=2))
        p.append(fitbox(x, 126, cw, 66, how, size=12.5, fill=FILL, stroke=stroke, sw=1.3))

    rows = [("блоки на носії", ["не виділені", "виділені", "виділені"]),
            ("байти на носії", ["їх немає", "не записані", "записані нулями"]),
            ("du покаже", ["нічого", "повний обсяг", "повний обсяг"]),
            ("SEEK_HOLE вважає", ["діра", "дані", "дані"]),
            ("запис сюди може дати ENOSPC", ["так", "ні", "ні"])]

    ry, rrh = 210, 62
    for j, (label, vals) in enumerate(rows):
        y = ry + j * rrh
        p.append(text(40, y + 36, label, size=13, anchor="end", color=MUTED))
        for (x, ttl, stroke, fill, how), v in zip(cols, vals):
            p.append(fitbox(x, y, cw, rrh - 10, [v], size=13.5, fill=FILL, stroke=stroke, sw=1.2))

    p.append(fitbox(50, ry + len(rows) * rrh + 14, 1060, 66,
                    ["різниця не в тому, що прочитається, а в тому, чи місце вже ваше"],
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'three-states.svg'), W, H, *p)


# ── 4. Обхід файлу через SEEK_DATA / SEEK_HOLE ──────────────────────────────
def fig_seek_walk():
    W, H = 1120, 560
    p = []
    p.append(text(W / 2, 38, "обхід карти файлу двома питаннями", size=16, bold=True, color=INK))

    sx, sw_, sy, sh = 90, 940, 80, 66
    p.append(rect(sx, sy, sw_, sh, fill=GREY_FILL, stroke=MUTED, sw=1.6, rx=6))
    # дані: 0..120 і 480..660
    for a, b in ((0, 130), (470, 660)):
        p.append(rect(sx + a, sy + 2, b - a, sh - 4, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(sx + 65, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 565, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 300, sy + sh / 2 + 5, "діра", size=12.5, color=MUTED, bold=True))
    p.append(text(sx + 800, sy + sh / 2 + 5, "діра до кінця файлу", size=12.5, color=MUTED, bold=True))

    # позначки зсувів
    marks = [(0, "0"), (130, "a"), (470, "b"), (660, "c"), (940, "кінець")]
    for off, lb in marks:
        p.append(line(sx + off, sy, sx + off, sy + sh + 16, color=INK, sw=1.1, dash="4,3"))
        p.append(text(sx + off, sy + sh + 34, lb, size=12.5, color=INK, bold=True))

    steps = [("lseek(fd, 0, SEEK_DATA)", "→ 0", "запит уже стоїть на даних"),
             ("lseek(fd, 0, SEEK_HOLE)", "→ a", "де кінчається перший острів"),
             ("lseek(fd, a, SEEK_DATA)", "→ b", "де починається наступний"),
             ("lseek(fd, b, SEEK_HOLE)", "→ c", "де кінчається другий острів"),
             ("lseek(fd, c, SEEK_DATA)", "→ ENXIO", "далі даних немає — обхід завершено")]

    tx, tw0, ty0, th0 = 90, 940, 200, 58
    for i, (call, res, why) in enumerate(steps):
        y = ty0 + i * (th0 + 10)
        last = (i == len(steps) - 1)
        p.append(rect(tx, y, tw0, th0, fill=RED_FILL if last else FILL,
                      stroke=POS if last else LINE, sw=1.8 if last else 1.3, rx=6))
        p.append(text(tx + 22, y + 36, call, size=14, anchor="start", bold=True,
                      color=POS if last else NEG))
        p.append(text(tx + 430, y + 36, res, size=14, anchor="start", bold=True,
                      color=POS if last else FIELD))
        p.append(text(tx + tw0 - 22, y + 36, why, size=12.5, anchor="end", color=MUTED))

    render(os.path.join(IMG, 'seek-walk.svg'), W, H, *p)


# ── 5. Дві дороги SEEK_HOLE у Linux (для історичної вставки) ────────────────
def fig_seek_hole_timeline():
    rows = [
        ("середина 2000-х", ["Solaris 10: lseek дістає SEEK_HOLE і SEEK_DATA",
                             "два питання про найближчу межу замість карти файлу"], FIELD, GREEN_FILL),
        ("жовтень 2007", ["Andreas Dilger пропонує ioctl FIEMAP — повну карту екстентів",
                          "не «де найближча межа», а вся розкладка файлу на носії"], WARM, WARM_FILL),
        ("листопад – грудень 2007", ["Josef Bacik надсилає в LKML перший патч, реалізація через bmap",
                                     "LWN, 3 грудня: «SEEK_HOLE or FIEMAP?» — вирок на користь карти"], NEG, BLUE_FILL),
        ("грудень 2008", ["ядро 2.6.28: FIEMAP прийнято в Linux",
                          "SEEK_HOLE лишається поза ядром — його «зробить бібліотека C»"], WARM, WARM_FILL),
        ("квітень 2011", ["Bacik надсилає патч удруге",
                          "«fiemap у таких речах, як cp, створює більше проблем, ніж розв'язує»"], NEG, BLUE_FILL),
        ("жовтень 2011", ["ядро 3.1: SEEK_HOLE і SEEK_DATA в Linux",
                          "разом із загальною відповіддю «весь файл — дані, діра в кінці»"], FIELD, GREEN_FILL),
        ("2011 – 2018", ["розповзання по файлових системах: Btrfs 3.1, OCFS2 3.2, XFS 3.5,",
                         "ext4 і tmpfs 3.8, NFS 3.18, FUSE 4.5, GFS2 4.15"], FIELD, GREEN_FILL),
        ("2024", ["POSIX.1-2024: обидва значення нарешті в стандарті",
                  "поза Linux — Solaris 10, FreeBSD 7.0, DragonFly BSD 2.3.1"], FIELD, GREEN_FILL),
    ]

    bx, bw, bh, gap = 250, 830, 58, 16
    top = 78
    W = bx + bw + 40
    H = top + len(rows) * (bh + gap) + 30

    p = [text(W / 2, 40, "SEEK_HOLE приходив у Linux двічі", size=17, bold=True, color=INK)]

    spine = 210
    p.append(line(spine, top + bh / 2, spine, top + (len(rows) - 1) * (bh + gap) + bh / 2,
                  color=MUTED, sw=2, dash="4,5"))

    for i, (year, lines, col, fill) in enumerate(rows):
        y = top + i * (bh + gap)
        cy = y + bh / 2
        p.append(text(spine - 34, cy + 5, year, size=13.5, anchor="end", color=INK, bold=True))
        p.append(circle(spine, cy, 7, fill=fill, stroke=col, sw=2.2))
        p.append(fitbox(bx, y, bw, bh, lines, size=13.5, pad=14,
                        fill=fill, stroke=col, sw=1.6, color=INK))

    render(os.path.join(IMG, 'seek-hole-timeline.svg'), W, H, *p)


# ── 6. Питання проти карти: два контракти ───────────────────────────────────
def fig_question_vs_map():
    W, H = 1100, 470
    p = [text(W / 2, 40, "два способи спитати файлову систему про порожнечу",
              size=17, bold=True, color=INK)]

    colw, colx = 500, (40, 560)
    heads = ["ioctl FIEMAP: «віддай карту»", "lseek SEEK_HOLE: «де найближча межа»"]
    fills = (WARM_FILL, GREEN_FILL)
    cols = (WARM, FIELD)

    bodies = [
        ["відповідь — масив екстентів зі зсувами,\nдовжинами й набором прапорців",
         "два виклики: спершу спитати кількість,\nпотім віддати буфер потрібного розміру",
         "прапорці UNWRITTEN, DELALLOC, ENCODED,\nDATA_INLINE — а рядка «діра» в карті немає",
         "ФС без підтримки відповідає EOPNOTSUPP:\nу викликача мусить бути запасна гілка"],
        ["відповідь — одне число: зсув межі",
         "один виклик, той самий lseek,\nбез структур і без буферів",
         "кінець файлу завжди вважається дірою,\nтож відповідь є завжди",
         "ФС без підтримки каже «все — дані»:\nвідповідь незручна, але правдива"],
    ]

    for c in range(2):
        x = colx[c]
        p.append(fitbox(x, 70, colw, 46, heads[c], size=15, pad=12,
                        fill=fills[c], stroke=cols[c], sw=2, bold=True, color=INK))
        for i, b in enumerate(bodies[c]):
            p.append(fitbox(x, 132 + i * 74, colw, 62, b, size=13, pad=12,
                            fill=FILL, stroke=cols[c], sw=1.4, color=INK))

    p.append(fitbox(40, 420, W - 80, 40,
                    "слабший контракт переміг сильніший: на просте питання завжди є проста відповідь",
                    size=14, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.5, color=INK, bold=True))

    render(os.path.join(IMG, 'question-vs-map.svg'), W, H, *p)


# ── 7. Чотири режими fallocate над діапазоном (для довідкової вставки) ──────
def fig_range_ops():
    W, H = 1200, 790
    p = []
    p.append(text(W / 2, 38, "що кожен режим fallocate робить із діапазоном",
                  size=16, bold=True, color=INK))

    LX, LW = 40, 230          # колонка назви режиму
    BX, BW = 300, 380         # смуга «було»
    AX = 740                  # смуга «стало»
    BH = 48

    p.append(text(LX + LW / 2, 78, "режим", size=13.5, bold=True, color=MUTED))
    p.append(text(BX + BW / 2, 78, "було", size=13.5, bold=True, color=MUTED))
    p.append(text(AX + BW / 2, 78, "стало", size=13.5, bold=True, color=MUTED))

    def bar(x, y, parts):
        out, cur = "", x
        for w, lines, fill, stroke in parts:
            out += fitbox(cur, y, w, BH, lines, size=12, pad=6,
                          fill=fill, stroke=stroke, sw=1.5, rx=4)
            cur += w
        return out

    DATA = (GREEN_FILL, FIELD)
    HOLE = (GREY_FILL, MUTED)
    ZERO = (WARM_FILL, WARM)
    PICK = (RED_FILL, POS)

    rows = [
        (["FALLOC_FL_PUNCH_HOLE", "з 2.6.38"],
         [(110, ["дані A"], *DATA), (140, ["дані B"], *DATA), (130, ["дані C"], *DATA)],
         [(110, ["дані A"], *DATA), (140, ["діра"], *HOLE), (130, ["дані C"], *DATA)],
         "range",
         ["st_size без змін · st_blocks ↓", "діапазон читається як нулі"]),
        (["FALLOC_FL_ZERO_RANGE", "з 3.15"],
         [(110, ["дані A"], *DATA), (140, ["дані B"], *DATA), (130, ["дані C"], *DATA)],
         [(110, ["дані A"], *DATA), (140, ["нулі,", "блоки лишились"], *ZERO),
          (130, ["дані C"], *DATA)],
         "range",
         ["st_size без змін · st_blocks без змін", "запис сюди вже не дасть ENOSPC"]),
        (["FALLOC_FL_COLLAPSE_RANGE", "з 3.15"],
         [(110, ["дані A"], *DATA), (140, ["діапазон", "зникає"], *PICK),
          (130, ["дані C"], *DATA)],
         [(110, ["дані A"], *DATA), (130, ["дані C"], *DATA)],
         "range",
         ["st_size ↓ на len · діри не лишається", "хвіст поїхав ЛІВОРУЧ на len"]),
        (["FALLOC_FL_INSERT_RANGE", "з 4.1"],
         [(110, ["дані A"], *DATA), (130, ["дані C"], *DATA)],
         [(110, ["дані A"], *DATA), (140, ["вставлена", "діра"], *HOLE),
          (130, ["дані C"], *DATA)],
         "point",
         ["st_size ↑ на len · дані не переписані", "хвіст поїхав ПРАВОРУЧ на len"]),
    ]

    y0, pitch = 100, 150
    for i, (name, before, after, mark, cap) in enumerate(rows):
        y = y0 + i * pitch
        p.append(fitbox(LX, y + 6, LW, BH + 8, name, size=12.5, pad=8,
                        bold=True, fill=FILL, stroke=NEG, sw=1.6))

        p.append(bar(BX, y + 6, before))
        p.append(bar(AX, y + 6, after))

        bw_before = sum(s[0] for s in before)
        bw_after = sum(s[0] for s in after)
        if bw_after < BW:
            p.append(rect(AX + bw_after, y + 6, BW - bw_after, BH, fill=BG,
                          stroke=MUTED, sw=1.2, rx=4))
            p.append(text(AX + bw_after + (BW - bw_after) / 2, y + 6 + BH / 2 + 4,
                          "коротший", size=11, color=MUTED))
        if bw_before < BW:
            p.append(rect(BX + bw_before, y + 6, BW - bw_before, BH, fill=BG,
                          stroke=MUTED, sw=1.2, rx=4))
            p.append(text(BX + bw_before + (BW - bw_before) / 2, y + 6 + BH / 2 + 4,
                          "кінець файлу", size=11, color=MUTED))

        p.append(arrow(694, y + 6 + BH / 2, 732, y + 6 + BH / 2, color=INK, sw=1.8))

        by = y + 6 + BH + 16
        if mark == "range":
            p.append(line(BX + 110, by, BX + 250, by, color=POS, sw=1.6))
            p.append(line(BX + 110, by - 5, BX + 110, by + 5, color=POS, sw=1.6))
            p.append(line(BX + 250, by - 5, BX + 250, by + 5, color=POS, sw=1.6))
            p.append(text(BX + 180, by + 24, "[offset, offset+len)", size=11, color=POS))
        else:
            p.append(line(BX + 110, by - 6, BX + 110, by + 5, color=POS, sw=1.6))
            p.append(text(BX + 110, by + 24, "offset", size=11, color=POS))

        p.append(fitbox(AX, y + 6 + BH + 10, BW, 44, cap, size=12, pad=8,
                        fill=FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(40, y0 + 4 * pitch + 2, 1120, 76,
                    ["зелене — блоки з даними · сіре — діра, блоків немає · тепле — блоки є, вміст нульовий",
                      "PUNCH_HOLE і ZERO_RANGE зсувів не чіпають; COLLAPSE_RANGE та INSERT_RANGE пересувають увесь хвіст файлу,",
                      "тому зсуви, які програма запам'ятала до виклику, після нього вже нічого не означають"],
                    size=13, pad=14, fill=BLUE_FILL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'range-ops.svg'), W, H, *p)


# ── Розріджене копіювання: діру не пишуть, її лишають ───────────
def fig_sparse_copy():
    W, H = 1160, 600
    p = []
    p.append(text(W / 2, 38, "копія зберігає діру тим, що в неї нічого не пише",
                  size=16, bold=True, color=INK))

    sx, sw_ = 110, 900
    sy, sh = 100, 64
    dy = 250
    isl = [(0, 150), (420, 600)]

    p.append(text(sx, sy - 14, "джерело: 1 ТіБ, два острови даних",
                  size=13, color=MUTED, anchor="start"))
    p.append(rect(sx, sy, sw_, sh, fill=GREY_FILL, stroke=MUTED, sw=1.6, rx=6))
    for a, b in isl:
        p.append(rect(sx + a, sy + 2, b - a, sh - 4, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(sx + 75, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 510, sy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))

    p.append(text(sx, dy - 14, "копія: ті самі острови, між ними — діра",
                  size=13, color=MUTED, anchor="start"))
    p.append(rect(sx, dy, sw_, sh, fill=GREY_FILL, stroke=MUTED, sw=1.6, rx=6))
    for a, b in isl:
        p.append(rect(sx + a, dy + 2, b - a, sh - 4, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(sx + 75, dy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))
    p.append(text(sx + 510, dy + sh / 2 + 5, "дані", size=12.5, color=FIELD, bold=True))

    for off, lb in ((0, "0"), (150, "a"), (420, "b"), (600, "c"), (900, "кінець")):
        p.append(line(sx + off, sy - 4, sx + off, dy + sh + 14, color=INK, sw=1.0, dash="4,4"))
        p.append(text(sx + off, dy + sh + 34, lb, size=12.5, color=INK, bold=True))

    for a, b in isl:
        cx = sx + (a + b) / 2.0
        p.append(arrow(cx, sy + sh + 6, cx, dy - 6, color=FIELD, sw=2))

    p.append(text(sx + 285, sy + sh + 46, "сюди не пишемо", size=13, color=POS, bold=True))
    p.append(text(sx + 750, sy + sh + 46, "і сюди теж не пишемо", size=13, color=POS, bold=True))

    p.append(fitbox(110, 380, 540, 72,
                    ["прочитано лише острови — 148 КіБ",
                     "решти трильйона байтів програма не торкалася"],
                    size=13.5, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(690, 380, 320, 72,
                    ["ftruncate(dfd, розмір джерела)",
                     "інакше копія кінчалася б на c"],
                    size=13.5, fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(arrow(850, 376, 960, 322, color=WARM, sw=1.8))

    p.append(fitbox(110, 480, 900, 96,
                    ["діру не «створюють» — її лишають: блок з'являється рівно там, куди щось написали",
                     "тому вся хитрість не в копіюванні даних, а в тому, щоб знати, де їх немає"],
                    size=14.5, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'sparse-copy.svg'), W, H, *p)


# ── Драбина запасних шляхів копіювання ────────────────────
def fig_copy_fallback():
    W, H = 1160, 560
    p = []
    p.append(text(W / 2, 38, "три шляхи копіювання і що обирає між ними",
                  size=16, bold=True, color=INK))

    p.append(fitbox(80, 90, 520, 80, ["lseek(fd, 0, SEEK_HOLE) відповідає?"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=1.6))
    p.append(fitbox(660, 90, 420, 80,
                    ["ТАК — йти по карті:", "читати лише острови даних"],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(arrow(604, 130, 654, 130, color=FIELD, sw=1.8))

    p.append(fitbox(80, 220, 520, 80, ["st_blocks · 512 менше за st_size?"],
                    size=15, bold=True, fill=FILL, stroke=LINE, sw=1.6))
    p.append(fitbox(660, 220, 420, 80,
                    ["НІ — файл щільний:", "копіювати підряд, нулів не шукати"],
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(arrow(604, 260, 654, 260, color=NEG, sw=1.8))

    p.append(fitbox(80, 350, 1000, 80,
                    ["ТАК — читати вікнами, кратними st_blksize приймача,",
                     "і не писати ті вікна, що складаються з самих нулів"],
                    size=14, fill=WARM_FILL, stroke=WARM, sw=2))

    p.append(arrow(340, 176, 340, 214, color=MUTED, sw=1.8))
    p.append(text(358, 200, "ні", size=13, color=MUTED, anchor="start", bold=True))
    p.append(arrow(340, 306, 340, 344, color=MUTED, sw=1.8))
    p.append(text(358, 330, "так", size=13, color=MUTED, anchor="start", bold=True))

    p.append(fitbox(80, 460, 1000, 76,
                    ["жоден із трьох шляхів не губить байтів: помилитися вони можуть",
                     "лише в бік «копія зайняла більше місця, ніж могла б»"],
                    size=14.5, bold=True, fill=RED_FILL, stroke=POS, sw=2))

    render(os.path.join(IMG, 'copy-fallback.svg'), W, H, *p)


if __name__ == '__main__':
    fig_size_vs_blocks()
    fig_hole_in_map()
    fig_three_states()
    fig_seek_walk()
    fig_seek_hole_timeline()
    fig_question_vs_map()
    fig_range_ops()
    fig_sparse_copy()
    fig_copy_fallback()
    print("ok")
