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
GREY_FILL = "#f0f1f3"
WARM = "#b8860b"


# ── 1. Розвилка: куди лягає нова версія блока ────────────────────────────────
def fig_write_fork():
    W, H = 1240, 790
    p = []

    def box(cx, cy, s, **kw):
        b, w, h = textbox(cx, cy, s, **kw)
        p.append(b)
        return cx, cy, w, h

    q = box(620, 48, "Куди лягає нова версія блока?", size=17, bold=True,
            fill=WARM_FILL, stroke=WARM, min_w=440, pad=14)

    L = box(280, 175, "на те саме місце", size=15, bold=True,
            fill=BLUE_FILL, stroke=NEG, min_w=300)
    R = box(940, 175, "поруч, на вільне місце", size=15, bold=True,
            fill=GREEN_FILL, stroke=FIELD, min_w=300)
    p.append(arrow(620, q[1] + q[3] / 2, 300, L[1] - L[3] / 2 - 6, color=NEG))
    p.append(arrow(620, q[1] + q[3] / 2, 920, R[1] - R[3] / 2 - 6, color=FIELD))

    # ліва гілка
    L1 = box(280, 300, "на носії є мить, коли\nчастина змін уже лягла,\nа частина ще ні",
             size=14, fill=FILL)
    p.append(arrow(280, L[1] + L[3] / 2, 280, L1[1] - L1[3] / 2))
    L2 = box(280, 430, "спершу записати намір\nв окрему ділянку —\nжурнал", size=14,
             fill=BLUE_FILL, stroke=NEG)
    p.append(arrow(280, L1[1] + L1[3] / 2, 280, L2[1] - L2[3] / 2))
    L3 = box(280, 550, "ext4 · XFS", size=18, bold=True, fill=BLUE_FILL,
             stroke=NEG, min_w=260, pad=12)
    p.append(arrow(280, L2[1] + L2[3] / 2, 280, L3[1] - L3[3] / 2))
    p.append(mtext(280, 625, ["ціна — метадані потрапляють", "на носій двічі"],
                   size=13, color=MUTED))

    # права гілка
    R1 = box(940, 300, "покажчик у батьківському вузлі\nзастарів — а його теж\nне можна правити на місці",
             size=14, fill=FILL)
    p.append(arrow(940, R[1] + R[3] / 2, 940, R1[1] - R1[3] / 2))
    R2 = box(940, 430, "хвиля оновлень піднімається\nдо самого кореня\n(мандрівне дерево)",
             size=14, fill=RED_FILL, stroke=POS)
    p.append(arrow(940, R1[1] + R1[3] / 2, 940, R2[1] - R2[3] / 2))

    O1 = box(730, 560, "копіювати весь шлях\nі перемкнути корінь\nодним записом", size=13,
             fill=GREEN_FILL, stroke=FIELD)
    O2 = box(1090, 560, "вузли посилаються\nномерами, не адресами —\nхвиля обривається", size=13,
             fill=GREEN_FILL, stroke=FIELD)
    p.append(arrow(880, R2[1] + R2[3] / 2, 760, O1[1] - O1[3] / 2 - 4, color=FIELD))
    p.append(arrow(1000, R2[1] + R2[3] / 2, 1070, O2[1] - O2[3] / 2 - 4, color=FIELD))

    B1 = box(730, 675, "Btrfs", size=18, bold=True, fill=GREEN_FILL, stroke=FIELD,
             min_w=200, pad=11)
    B2 = box(1090, 675, "F2FS", size=18, bold=True, fill=GREEN_FILL, stroke=FIELD,
             min_w=200, pad=11)
    p.append(arrow(730, O1[1] + O1[3] / 2, 730, B1[1] - B1[3] / 2, color=FIELD))
    p.append(arrow(1090, O2[1] + O2[3] / 2, 1090, B2[1] - B2[3] / 2, color=FIELD))
    p.append(mtext(730, 740, ["ціна — посилений запис,", "зиск — дешевий знімок"],
                   size=13, color=MUTED))
    p.append(mtext(1090, 740, ["ціна — окрема таблиця,", "зиск — хвиля не йде вгору"],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'write-fork.svg'), W, H, *p)


# ── 2. Три способи описати карту файлу ───────────────────────────────────────
def fig_extent_map():
    W, H = 1180, 720
    p = []

    def head(y, s):
        p.append(text(50, y, s, size=16, bold=True, anchor="start", color=INK))

    def note(y, s):
        p.append(text(50, y, s, size=13, anchor="start", color=MUTED))

    # ── список номерів
    head(40, "Список номерів блоків (ext2, ext3)")
    p.append(fitbox(50, 60, 190, 96, "inode\n12 прямих номерів\n+ 3 непрямі", size=14,
                    fill=BLUE_FILL, stroke=NEG))
    xs = [300, 500, 700]
    labels = ["непрямий блок\n1024 номери",
              "подвійно непрямий\n1024 блоки по 1024",
              "тричі непрямий\nще на рівень глибше"]
    for x, s in zip(xs, labels):
        p.append(fitbox(x, 68, 180, 80, s, size=13, fill=FILL))
    p.append(arrow(240, 108, 300, 108))
    p.append(arrow(480, 108, 500, 108))
    p.append(arrow(680, 108, 700, 108))
    p.append(fitbox(910, 60, 220, 96,
                    "файл на 1 ГіБ:\n262144 покажчики\n≈ 1 МіБ самої карти", size=13,
                    fill=RED_FILL, stroke=POS))
    note(178, "щоб дістатися далекого блока, треба спершу прочитати покажчики — зайві звертання до носія")

    # ── екстенти
    head(250, "Екстенти (ext4, XFS)")
    cells = [("зсув у файлі: 0\nблок: 802816\nдовжина: 32768", GREEN_FILL),
             ("зсув у файлі: 32768\nблок: 835584\nдовжина: 32768", GREEN_FILL),
             ("зсув у файлі: 65536\nблок: 868352\nдовжина: 32768", GREEN_FILL)]
    for i, (s, f) in enumerate(cells):
        p.append(fitbox(50 + i * 240, 270, 220, 90, s, size=13, fill=f, stroke=FIELD))
    p.append(fitbox(790, 270, 340, 90,
                    "12 байтів на запис · до 128 МіБ на запис\nчотири записи вміщаються просто в inode\nтой самий файл — 96 байтів карти",
                    size=13, fill=WARM_FILL, stroke=WARM))
    note(382, "суцільна ділянка описується трьома числами замість переліку кожного блока")

    # ── дерево екстентів
    head(454, "Дерево екстентів (коли записів забагато)")
    p.append(fitbox(430, 474, 320, 66, "корінь у inode: 60 байтів\nзаголовок + до 4 записів",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    leaves = ["листок\nекстенти 0…340", "листок\nекстенти 341…680", "листок\nекстенти 681…1020"]
    for i, s in enumerate(leaves):
        x = 130 + i * 320
        p.append(fitbox(x, 600, 260, 66, s, size=13, fill=FILL))
        p.append(arrow(590 - (1 - i) * 30, 540, x + 130, 594))
    note(690, "глибина росте як логарифм від кількості записів; роздроблений файл — це багато записів, і карта знову дорожчає")

    render(os.path.join(IMG, 'extent-map.svg'), W, H, *p)


# ── 3. Оновлення дерева при копіюванні при записі ────────────────────────────
def fig_cow_tree():
    W, H = 1100, 640
    p = []

    def nodebox(cx, cy, s, fill, stroke, size=13):
        b, w, h = textbox(cx, cy, s, size=size, fill=fill, stroke=stroke, pad=10, min_w=120)
        p.append(b)
        return cx, cy, w, h

    # старе дерево
    leaves = [(130, "листок A"), (290, "листок B"), (450, "листок C"), (610, "листок D")]
    LY = 400
    old_leaf = {}
    for x, nm in leaves:
        old_leaf[nm] = nodebox(x, LY, nm, GREY_FILL, MUTED)
    n1 = nodebox(210, 285, "вузол 1", GREY_FILL, MUTED)
    n2 = nodebox(530, 285, "вузол 2", GREY_FILL, MUTED)
    root = nodebox(370, 170, "старий корінь", GREY_FILL, MUTED)
    for parent, kids in ((n1, ["листок A", "листок B"]), (n2, ["листок C", "листок D"])):
        for k in kids:
            c = old_leaf[k]
            p.append(line(parent[0], parent[1] + parent[3] / 2, c[0], c[1] - c[3] / 2,
                          color=MUTED, sw=1.4))
    for c in (n1, n2):
        p.append(line(root[0], root[1] + root[3] / 2, c[0], c[1] - c[3] / 2, color=MUTED, sw=1.4))

    # нові копії
    nl = nodebox(910, LY, "листок D′", RED_FILL, POS)
    nn = nodebox(910, 285, "вузол 2′", RED_FILL, POS)
    nr = nodebox(910, 170, "новий корінь", RED_FILL, POS)
    p.append(line(nr[0], nr[1] + nr[3] / 2, nn[0], nn[1] - nn[3] / 2, color=POS, sw=2))
    p.append(line(nn[0], nn[1] + nn[3] / 2, nl[0], nl[1] - nl[3] / 2, color=POS, sw=2))
    # спільні гілки
    p.append(line(nr[0] - nr[2] / 2, nr[1] + 6, n1[0] + n1[2] / 2 + 4, n1[1] - 4,
                  color=FIELD, sw=1.8, dash="7,5"))
    p.append(line(nn[0] - nn[2] / 2, nn[1] + 6, old_leaf["листок C"][0] + 50,
                  old_leaf["листок C"][1] - old_leaf["листок C"][3] / 2 - 2,
                  color=FIELD, sw=1.8, dash="7,5"))

    # суперблок
    sb = nodebox(650, 62, "суперблок", WARM_FILL, WARM, size=15)
    p.append(line(sb[0] - sb[2] / 2, sb[1] + 10, root[0] + 40, root[1] - root[3] / 2,
                  color=MUTED, sw=1.6, dash="6,5"))
    p.append(arrow(sb[0] + sb[2] / 2, sb[1] + 10, nr[0] - 40, nr[1] - nr[3] / 2, color=POS))

    # легенда
    lg = ["сіре — старе дерево: воно цілісне до останньої миті",
          "червоне — нові копії: змінений листок і весь шлях над ним",
          "штрих зелений — незмінені гілки нове дерево ділить зі старим",
          "перемикання суперблока — один запис сектора; стану посередині не існує",
          "якщо старий корінь зберегти, він і є знімок"]
    for i, s in enumerate(lg):
        p.append(text(60, 500 + i * 26, s, size=13, anchor="start", color=INK))

    render(os.path.join(IMG, 'cow-tree.svg'), W, H, *p)


# ── 4. Розкладка на носії у чотирьох родин ───────────────────────────────────
def fig_layouts():
    W, H = 1260, 820
    p = []
    X0, BW = 60, 1140

    def strip(top, title, cells, note, accent):
        p.append(text(X0, top + 20, title, size=17, bold=True, anchor="start", color=accent))
        x = X0
        for frac, s, fill in cells:
            w = BW * frac
            p.append(fitbox(x, top + 38, w - 6, 82, s, size=13, fill=fill, stroke=accent))
            x += w
        p.append(text(X0, top + 146, note, size=13, anchor="start", color=MUTED))

    strip(20, "ext4", [
        (0.07, "супер-\nблок", WARM_FILL),
        (0.26, "група блоків\nдескриптор · бітові карти\nтаблиця inode · дані", BLUE_FILL),
        (0.26, "група блоків\nдескриптор · бітові карти\nтаблиця inode · дані", BLUE_FILL),
        (0.26, "група блоків\nдескриптор · бітові карти\nтаблиця inode · дані", BLUE_FILL),
        (0.15, "журнал", RED_FILL),
    ], "запис на місці · таблицю inode-ів відводять під час створення, і вона більше не росте", NEG)

    strip(210, "XFS", [
        (0.28, "група розподілу\nдерева вільного: за адресою\nі за розміром", GREEN_FILL),
        (0.28, "група розподілу\nдерево inode-ів\nдані", GREEN_FILL),
        (0.28, "група розподілу\nусе своє, нічого спільного\nз сусідами", GREEN_FILL),
        (0.16, "журнал\n(відкладений)", RED_FILL),
    ], "групи незалежні — потоки не б'ються за спільні структури · inode-и виділяються на вимогу", FIELD)

    strip(400, "Btrfs", [
        (0.18, "суперблок\n→ корінь", WARM_FILL),
        (0.16, "дерево\nкоренів", GREEN_FILL),
        (0.16, "дерево\nкусків", GREEN_FILL),
        (0.17, "дерево\nекстентів", GREEN_FILL),
        (0.17, "дерево\nконтрольних сум", GREEN_FILL),
        (0.16, "дерево\nпідтому", GREEN_FILL),
    ], "жоден блок не переписується на місці · куски відображають логічний простір на кілька пристроїв", POS)

    strip(590, "F2FS", [
        (0.10, "супер-\nблок ×2", WARM_FILL),
        (0.14, "контрольна\nточка ×2", WARM_FILL),
        (0.08, "SIT", BLUE_FILL),
        (0.08, "NAT", BLUE_FILL),
        (0.08, "SSA", BLUE_FILL),
        (0.52, "основна область: сегменти по 2 МіБ\n6 відкритих логів — гарячі, теплі, холодні\nокремо для вузлів і для даних", GREEN_FILL),
    ], "в основну область пишуть лише послідовно · місце звільняє прибиральник", WARM)

    render(os.path.join(IMG, 'layouts.svg'), W, H, *p)


# ── 5. Три часи ухвалення рішення ────────────────────────────────────────────
def fig_decision_times():
    W, H = 1400, 720
    p = []

    def box(cx, cy, s, **kw):
        b, w, h = textbox(cx, cy, s, **kw)
        p.append(b)
        return w, h

    box(700, 44, "Коли ухвалюють рішення про файлову систему", size=17, bold=True,
        fill=WARM_FILL, stroke=WARM, min_w=560, pad=13)

    COLS = [
        (245, "mkfs — назавжди", RED_FILL, POS, 232, 128, [
            "ext4\nрозмір блока -b · розмір inode -I\nкількість inode-ів -N / -i · bigalloc -C",
            "XFS\nрозмір блока -b · розмір inode -i size=\nкількість і розмір груп -d agcount= / agsize=",
            "Btrfs\nnodesize -n · sectorsize -s\nтип контрольної суми --csum",
            "F2FS\nсегментів у секції -s · секцій у зоні -z\nчастка надлишку -o",
        ]),
        (700, "інструмент — окремою дією", BLUE_FILL, NEG, 232, 128, [
            "ext4\ntune2fs -O ± можливості, -m резерв\nresize2fs: більшати наживо, меншати — ні",
            "XFS\nxfs_growfs -d — лише більшати\nзменшення практично немає",
            "Btrfs\nbalance -dconvert= · device add / remove\nfilesystem resize у два боки",
            "F2FS\nresize.f2fs — збільшити\nfsck.f2fs — лише на відмонтованій",
        ]),
        (1155, "mount — щоразу заново", GREEN_FILL, FIELD, 205, 102, [
            "спільні для всіх\nnoatime · relatime · lazytime\nsync · dirsync · ro",
            "ext4\ndata=ordered | journal | writeback\ncommit= · discard · journal_checksum",
            "XFS\nlogbsize= · allocsize=\ndiscard · inode32 / inode64",
            "Btrfs\ncompress=zstd:N · nodatacow\nautodefrag · ssd · commit=",
            "F2FS\ncompress_algorithm= · fsync_mode=\nbackground_gc= · discard",
        ]),
    ]

    for cx, head, fill, accent, y0, step, rows in COLS:
        box(cx, 118, head, size=15, bold=True, fill=fill, stroke=accent,
            min_w=400, pad=11)
        y = y0
        for s in rows:
            box(cx, y, s, size=13, fill=fill, stroke=accent, min_w=400, pad=10)
            y += step

    p.append(mtext(700, 682,
                   ["у /proc/mounts видно лише праву колонку — те, що чинне зараз;",
                    "ліві дві читають окремими інструментами: dumpe2fs -h · xfs_info · btrfs filesystem show · dump.f2fs"],
                   size=13, color=MUTED))

    render(os.path.join(IMG, 'decision-times.svg'), W, H, *p)


# ── FIEMAP: контракт виклику і рух по файлу (вставка proj-fiemap-layout) ─────
def fig_fiemap_loop():
    W, H = 1280, 730
    p = []

    def box(cx, cy, s, **kw):
        b, w, h = textbox(cx, cy, s, **kw)
        p.append(b)
        return cx, cy, w, h

    # верхня панель: що лежить у пам'яті й хто що заповнює
    p.append(text(130, 78, "Що лежить у пам'яті програми", size=15, bold=True, anchor="start"))

    box(320, 178, "struct fiemap — заголовок\nfm_start · fm_length · fm_flags\nfm_extent_count = 512   (вхід)\nfm_mapped_extents       (вихід)",
        size=13, fill=BLUE_FILL, stroke=NEG)
    box(320, 332, "fm_extents[512]\nмасив одразу за заголовком\n56 байтів на запис", size=13, fill=GREY_FILL)
    p.append(mtext(320, 400, ["один malloc:",
                              "sizeof(struct fiemap) + 512 · sizeof(struct fiemap_extent)"],
                   size=12, color=MUTED))

    box(1000, 172, "ядро", size=17, bold=True, fill=WARM_FILL, stroke=WARM, min_w=220, pad=12)
    p.append(mtext(1000, 248, ["іде деревом екстентів файлу від fm_start",
                               "і кладе записи у вільні слоти;",
                               "останньому в файлі ставить LAST"], size=13))

    p.append(arrow(470, 150, 875, 158))
    p.append(text(672, 126, "ioctl(fd, FS_IOC_FIEMAP, fm)", size=13))
    p.append(arrow(875, 332, 440, 332, color=FIELD))
    p.append(text(660, 362, "fm_mapped_extents — скільки слотів заповнено", size=13, color=MUTED))

    # нижня панель: вікна запитів по логічній осі файлу
    p.append(text(130, 468, "Як рухатися по файлу", size=15, bold=True, anchor="start"))

    X0, X1, YS, HS = 150, 1140, 592, 46
    span = X1 - X0
    p.append(rect(X0, YS, span, HS, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))

    for a, b in [(0.26, 0.30), (0.53, 0.58)]:
        p.append(rect(X0 + span * a, YS + 4, span * (b - a), HS - 8,
                      fill=GREY_FILL, stroke=MUTED, sw=1.0, rx=2))

    parts = [(0.00, 0.09), (0.09, 0.17), (0.17, 0.26),
             (0.30, 0.38), (0.38, 0.47), (0.47, 0.53),
             (0.58, 0.66), (0.66, 0.74), (0.74, 0.83), (0.83, 1.00)]
    for i, (a, b) in enumerate(parts):
        tail = (i == len(parts) - 1)
        p.append(rect(X0 + span * a + 1, YS + 4, span * (b - a) - 2, HS - 8,
                      fill=RED_FILL if tail else BLUE_FILL,
                      stroke=POS if tail else NEG, sw=1.2, rx=2))

    def bracket(fa, fb, lines, color=INK):
        xa, xb, y = X0 + span * fa, X0 + span * fb, YS - 34
        p.append(line(xa, y, xb, y, color=color, sw=1.6))
        p.append(line(xa, y, xa, y + 14, color=color, sw=1.6))
        p.append(line(xb, y, xb, y + 14, color=color, sw=1.6))
        p.append(mtext((xa + xb) / 2, y - 50, lines, size=12, color=color))

    bracket(0.00, 0.38, ["виклик 1", "fm_start = 0"])
    bracket(0.38, 0.74, ["виклик 2", "fm_start = кінець", "останнього поверненого"])
    bracket(0.74, 1.00, ["виклик 3", "в останньому екстенті", "прапорець LAST → стоп"], color=POS)

    p.append(text(X0, YS + HS + 36, "сіре — діра: карта її не описує", size=12,
                  anchor="start", color=MUTED))
    p.append(text(X1, YS + HS + 36, "у переліку просто розрив між зсувами", size=12,
                  anchor="end", color=MUTED))

    render(os.path.join(IMG, 'fiemap-loop.svg'), W, H, *p,
           title="FIEMAP: один виклик — пачка екстентів")


# ── Роздроблення того самого файлу (вставка proj-fiemap-layout) ──────────────
def fig_fragmentation_bands():
    import random
    W, H = 1260, 470
    p = []
    X0, X1 = 330, 1200
    span = X1 - X0

    def strip(y, label, segs, fill, stroke, note):
        frag, _, _ = textbox(168, y + 27, label, size=14, fill=FILL)
        p.append(frag)
        p.append(rect(X0, y, span, 54, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
        for a, b in segs:
            p.append(rect(X0 + span * a, y + 5, max(1.2, span * (b - a)), 44,
                          fill=fill, stroke=stroke, sw=0.8, rx=2))
        p.append(text((X0 + X1) / 2, y + 86, note, size=13, color=MUTED))

    rng = random.Random(11)

    xfs, pos = [], 0.008
    while pos < 0.95:
        ln = rng.uniform(0.06, 0.13)
        xfs.append((pos, min(0.995, pos + ln)))
        pos += ln + rng.uniform(0.005, 0.02)

    btr = []
    for _ in range(170):
        a = rng.uniform(0.004, 0.985)
        btr.append((a, a + rng.uniform(0.0012, 0.004)))

    strip(110, "XFS\nсвіжа копія", xfs, GREEN_FILL, FIELD,
          "47 екстентів · середня довжина ≈ 871 МіБ · частка суцільності ≈ 0.24")
    strip(300, "Btrfs\nтиждень роботи ВМ", btr, RED_FILL, POS,
          "486 300 екстентів · середня довжина ≈ 86 КіБ · частка суцільності ≈ 0.02")

    render(os.path.join(IMG, 'fragmentation-bands.svg'), W, H, *p,
           title="Той самий образ на 40 ГіБ — і два різні підсумки")


if __name__ == '__main__':
    fig_write_fork()
    fig_extent_map()
    fig_cow_tree()
    fig_layouts()
    fig_decision_times()
    fig_fiemap_loop()
    fig_fragmentation_bands()
    print("ok")
