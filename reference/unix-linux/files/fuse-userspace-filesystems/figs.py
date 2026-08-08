# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

USER_FILL = "#eaf0fd"   # простір користувача
KERN_FILL = "#fff6e5"   # ядро
DATA_FILL = "#eaf6ef"
WARN_FILL = "#fdecea"
WARM = "#b8860b"


# ── 1. Шлях одного read() через FUSE ────────────────────────────────────────
def fig_read_roundtrip():
    W, H = 1210, 760
    p = []

    colw = 270
    ax, bx, cx = 30, 470, 910          # ліві краї колонок
    acx, bcx, ccx = ax + colw / 2, bx + colw / 2, cx + colw / 2
    top, bot = 95, 610

    # тло колонок
    p.append(rect(ax, top, colw, bot - top, fill=USER_FILL, stroke=NEG, sw=1.6, rx=10))
    p.append(rect(bx, top, colw, bot - top, fill=KERN_FILL, stroke=WARM, sw=1.6, rx=10))
    p.append(rect(cx, top, colw, bot - top, fill=USER_FILL, stroke=NEG, sw=1.6, rx=10))

    # заголовки
    for c, t, s in ((acx, "Програма", "простір користувача"),
                    (bcx, "Ядро", "VFS і модуль fuse"),
                    (ccx, "Демон файлової системи", "теж простір користувача")):
        p.append(text(c, 52, t, size=17, bold=True))
        p.append(text(c, 76, s, size=12, color=MUTED))

    def box(cx_, y, s, fill=BG):
        return fitbox(cx_ - 118, y - 34, 236, 68, s, size=13, fill=fill, stroke=INK, sw=1.4)

    def gap_label(gx, y, s):
        return mtext(gx, y, s, size=12, color=MUTED)

    # крок 1
    p.append(box(acx, 150, "read(fd, buf, 4096)\nна файлі з /mnt/build"))
    p.append(gap_label(385, 130, "системний виклик"))
    p.append(arrow(ax + colw + 10, 150, bx - 10, 150, color=INK))
    p.append(box(bcx, 150, "VFS бачить: цей inode\nналежить fuse"))

    # крок 2
    p.append(box(bcx, 285, "модуль fuse складає запит\nі приспиняє програму"))
    p.append(gap_label(825, 258, ["повідомлення FUSE_READ:", "nodeid, зміщення, розмір"]))
    p.append(arrow(bx + colw + 10, 285, cx - 10, 285, color=POS))
    p.append(box(ccx, 285, "read(/dev/fuse)\nповертає цей запит", fill=DATA_FILL))

    # крок 3 — усередині колонки демона
    p.append(arrow(ccx, 322, ccx, 358, color=INK))
    p.append(box(ccx, 400, "демон дістає байти\nзвідки завгодно: мережа,\nархів, шифросховище", fill=DATA_FILL))

    # крок 4
    p.append(arrow(cx - 10, 500, bx + colw + 10, 500, color=POS))
    p.append(gap_label(825, 470, ["write(/dev/fuse):", "відповідь із байтами"]))
    p.append(box(bcx, 500, "модуль fuse копіює байти\nі будить програму"))

    # крок 5
    p.append(arrow(bx - 10, 570, ax + colw + 10, 570, color=INK))
    p.append(gap_label(385, 543, "повернення з виклику"))
    p.append(box(acx, 570, "n == 4096, байти в buf"))

    # підпис-висновок
    p.append(fitbox(30, 650, W - 60, 74,
                    "Червоні стрілки — перетини межі ядра. Їх два на кожен запит, і кожен коштує "
                    "перемикання контексту та копіювання даних.\n"
                    "Для файлової системи всередині ядра таких перетинів немає жодного.",
                    size=14, fill=WARN_FILL, stroke=POS, sw=1.6))

    render(os.path.join(IMG, 'read-roundtrip.svg'), W, H, *p)


# ── 2. Монтування без прав root ─────────────────────────────────────────────
def fig_mount_handshake():
    W, H = 1250, 720
    p = []

    lanes = [(40, 340, "Демон", "звичайний користувач", USER_FILL, NEG),
             (455, 340, "fusermount3", "setuid root", WARN_FILL, POS),
             (870, 340, "Ядро", "підсистема монтувань", KERN_FILL, WARM)]
    top, bot = 95, 600
    for x, w, t, s, fill, stroke in lanes:
        p.append(rect(x, top, w, bot - top, fill=fill, stroke=stroke, sw=1.6, rx=10))
        p.append(text(x + w / 2, 52, t, size=17, bold=True))
        p.append(text(x + w / 2, 76, s, size=12, color=MUTED))

    l1, l2, l3 = 40 + 170, 455 + 170, 870 + 170   # центри доріжок

    def step(cx_, y, s, h=78):
        return fitbox(cx_ - 155, y - h / 2, 310, h, s, size=13, fill=BG, stroke=INK, sw=1.4)

    p.append(step(l1, 150, "1. open(\"/dev/fuse\") —\nдескриптор N, поки нікуди не веде"))
    p.append(arrow(l1 + 158, 172, l2 - 158, 228, color=INK))
    p.append(step(l2, 250, "2. демон запускає помічника\nі дає йому сокет для відповіді"))
    p.append(arrow(l2 + 158, 272, l3 - 158, 348, color=INK))
    p.append(step(l3, 370,
                  "3. mount(\"fuse\", точка, \"fd=N,\nrootmode=…,user_id=…,group_id=…\")\n"
                  "плюс примусові nosuid і nodev", h=94))
    p.append(arrow(l3 - 158, 400, l2 + 158, 462, color=INK))
    p.append(step(l2, 480, "4. дескриптор повертається демонові\nчерез сокет; привілеї скинуто"))
    p.append(arrow(l2 - 158, 502, l1 + 158, 542, color=INK))
    p.append(step(l1, 550, "5. цикл на дескрипторі N:\nзапит → відповідь → запит"))

    p.append(fitbox(40, 636, W - 80, 66,
                    "Монтування прив'язане саме до дескриптора N. Закрився дескриптор — з'єднання обірване, "
                    "і кожен виклик у цій точці відповідає ENOTCONN.",
                    size=14, fill=DATA_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'mount-handshake.svg'), W, H, *p)


# ── 3. Три шляхи даних ──────────────────────────────────────────────────────
def fig_data_paths():
    W, H = 1210, 700
    p = []

    cols = [
        (40, "Файлова система в ядрі", "ext4, XFS",
         ["read() у програмі", "VFS", "ext4 усередині ядра", "кеш сторінок", "носій"],
         "перетинів межі: 0\nкопіювань даних: 1", DATA_FILL, FIELD),
        (455, "FUSE, звичайний режим", "sshfs, gocryptfs",
         ["read() у програмі", "VFS", "модуль fuse", "демон у просторі\nкористувача", "мережа, архів,\nсховище — що завгодно"],
         "перетинів межі: 2 на запит\nкопіювань даних: 2", WARN_FILL, POS),
        (870, "FUSE з passthrough", "ядро 6.9 і новіші",
         ["read() у програмі", "VFS", "модуль fuse", "файл-підкладка,\nзареєстрований раз", "носій"],
         "перетинів межі на дані: 0\nдемон бачить лише open()", USER_FILL, NEG),
    ]
    colw = 300

    for x, title, sub, steps, foot, fill, stroke in cols:
        p.append(text(x + colw / 2, 46, title, size=16, bold=True))
        p.append(text(x + colw / 2, 70, sub, size=12, color=MUTED))
        y = 100
        for i, s in enumerate(steps):
            p.append(fitbox(x, y, colw, 62, s, size=13, fill=fill, stroke=stroke, sw=1.5))
            if i < len(steps) - 1:
                p.append(arrow(x + colw / 2, y + 62, x + colw / 2, y + 90, color=INK))
            y += 92
        p.append(fitbox(x, 560, colw, 80, foot, size=13, bold=True, fill=BG, stroke=stroke, sw=1.8))

    render(os.path.join(IMG, 'data-paths.svg'), W, H, *p)


# ── 4. Черги одного з'єднання (вставка api-fuse-protocol) ───────────────────
def fig_fuse_queues():
    W, H = 1240, 770
    p = []

    SPLIT = 845
    p.append(text(420, 44, "Ядро", size=17, bold=True))
    p.append(text(420, 68, "модуль fuse: черги одного з'єднання", size=12, color=MUTED))
    p.append(text(1050, 44, "Демон", size=17, bold=True))
    p.append(text(1050, 68, "простір користувача", size=12, color=MUTED))
    p.append(line(SPLIT, 88, SPLIT, 700, color=MUTED, sw=1.4, dash="7 7"))

    # джерело запиту
    p.append(fitbox(40, 100, 760, 54,
                    "ядро складає запит: opcode · nodeid · unique (парний номер)",
                    size=14, fill=KERN_FILL, stroke=WARM, sw=1.6))
    p.append(arrow(420, 154, 420, 186, color=INK))

    lanes = [
        (190, "1 · interrupts — FUSE_INTERRUPT; забирається поперед усього іншого", WARN_FILL, POS),
        (262, "2 · forget — FUSE_FORGET і FUSE_BATCH_FORGET; відповіді не буде", FILL, MUTED),
        (334, "3 · pending — звичайні запити в порядку надходження", USER_FILL, NEG),
        (406, "4 · bg_queue — фонові (readahead, writeback): у роботі не більше max_background", DATA_FILL, FIELD),
    ]
    for y, s, fill, stroke in lanes:
        p.append(fitbox(40, y, 760, 58, s, size=13, fill=fill, stroke=stroke, sw=1.6))

    # збірник праворуч від стосу
    p.append(line(812, 219, 812, 435, color=INK, sw=1.6))
    for y, _s, _f, _st in lanes:
        p.append(line(800, y + 29, 812, y + 29, color=INK, sw=1.4))
    p.append(arrow(812, 327, 898, 327, color=INK))

    # бік демона
    p.append(fitbox(900, 292, 300, 72, "read(/dev/fuse)\nвіддає один запит цілком",
                    size=13, fill=USER_FILL, stroke=NEG, sw=1.6))
    p.append(arrow(1050, 364, 1050, 398, color=INK))
    p.append(fitbox(900, 400, 300, 84, "демон рахує відповідь\nі кладе в неї той самий unique",
                    size=13, fill=USER_FILL, stroke=NEG, sw=1.6))
    p.append(arrow(1050, 484, 1050, 518, color=INK))
    p.append(fitbox(900, 520, 300, 72, "write(/dev/fuse)\nодна відповідь = один write",
                    size=13, fill=USER_FILL, stroke=NEG, sw=1.6))

    # processing і повернення
    p.append(fitbox(40, 500, 760, 76,
                    "processing — хеш-таблиця за unique:\nзапити, вже видані демонові й ще без відповіді",
                    size=13, fill=DATA_FILL, stroke=NEG, sw=1.6))
    p.append(arrow(898, 556, 806, 556, color=POS))
    p.append(arrow(420, 576, 420, 614, color=INK))
    p.append(fitbox(40, 616, 760, 60,
                    "ядро знаходить запит за unique, копіює тіло в буфер програми й будить її",
                    size=13, fill=KERN_FILL, stroke=WARM, sw=1.6))

    p.append(text(620, 726,
                  "Запити з черг interrupts і forget у processing не потрапляють — відповіді на них не буде.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'fuse-queues.svg'), W, H, *p)


# ── 5. Домовленість FUSE_INIT (вставка api-fuse-protocol) ───────────────────
def fig_init_negotiation():
    W, H = 1240, 700
    p = []

    cols = [
        (30, 340, "Ядро → демон", "FUSE_INIT — завжди перше повідомлення", KERN_FILL, WARM, [
            "major = 7",
            "minor = найвища,\nяку знає це ядро",
            "max_readahead\nз налаштувань пристрою",
            "flags і flags2 —\nусе, що ядро вміє",
        ]),
        (440, 340, "Демон → ядро", "fuse_init_out", USER_FILL, NEG, [
            "major мусить бути\nрівно 7",
            "minor — свій",
            "flags і flags2 — лише те,\nщо демон справді вміє",
            "max_write, max_readahead",
            "max_background,\ncongestion_threshold",
            "time_gran, max_pages",
        ]),
        (850, 360, "Що діє на з'єднанні", "після перевірок у ядрі", DATA_FILL, FIELD, [
            "прапорці = перетин\nдвох наборів",
            "max_write ≥ 4096",
            "max_pages ≤ 256 → 1 МіБ",
            "time_gran у межах 1…10⁹ нс",
            "max_background без прав\nадміністратора обмежено\nпараметром модуля",
        ]),
    ]

    for x, w, head, sub, fill, stroke, items in cols:
        p.append(text(x + w / 2, 46, head, size=16, bold=True))
        p.append(text(x + w / 2, 70, sub, size=12, color=MUTED))
        y = 104
        for s in items:
            h = 62 if "\n" not in s else (72 if s.count("\n") == 1 else 86)
            p.append(fitbox(x, y, w, h, s, size=13, fill=fill, stroke=stroke, sw=1.6))
            y += h + 12

    p.append(arrow(378, 300, 434, 300, color=INK))
    p.append(arrow(788, 300, 844, 300, color=INK))

    p.append(fitbox(30, 588, 1180, 62,
                    "major у відповіді не 7 → з'єднання не піднялося: кожен запит у цій точці монтування дає ECONNREFUSED",
                    size=14, bold=True, fill=WARN_FILL, stroke=POS, sw=1.8))

    render(os.path.join(IMG, 'init-negotiation.svg'), W, H, *p)


# ── 6. Три питання ядра — одна ваша функція ─────────────────────────────────
def fig_getattr_funnel():
    W, H = 1190, 620
    p = []

    p.append(text(W / 2, 40, "Що надсилає ядро — і що з цього кличе ваш код",
                  size=17, bold=True))

    asks = [
        (100, "FUSE_LOOKUP (1)\nу каталозі nodeid=2\nзнайди ім'я «7»"),
        (205, "FUSE_GETATTR (3)\nатрибути об'єкта,\nномер якого вже відомий"),
        (310, "FUSE_READDIRPLUS (44)\nусі імена каталогу\nразом з атрибутами"),
    ]
    for y, s in asks:
        p.append(fitbox(40, y, 320, 84, s, size=13,
                        fill=KERN_FILL, stroke=WARM, sw=1.6))
        p.append(arrow(368, y + 42, 452, 258, color=INK))

    p.append(fitbox(460, 196, 260, 124,
                    "високорівневий шар\nlibfuse\n\nтримає власне дерево імен\nі перекладає nodeid у шлях",
                    size=13, fill=DATA_FILL, stroke=FIELD, sw=1.6))
    p.append(arrow(728, 258, 806, 258, color=INK))
    p.append(fitbox(812, 206, 338, 104,
                    "одна ваша функція\ngen_getattr(path, st, fi)\n\nзаповнює st_mode, st_nlink, st_size",
                    size=13, fill=USER_FILL, stroke=NEG, sw=1.6))

    p.append(text(W / 2, 400, "«ls -l» у каталозі з 12 файлів", size=15, bold=True))
    p.append(fitbox(40, 420, 530, 160,
                    "звичайний READDIR\n\n"
                    "повідомлень через межу: 16\n"
                    "LOOKUP каталогу · OPENDIR · READDIR ·\n"
                    "12 × LOOKUP · RELEASEDIR\n\n"
                    "викликів вашого getattr: 25",
                    size=13, fill=WARN_FILL, stroke=POS, sw=1.8))
    p.append(fitbox(620, 420, 530, 160,
                    "READDIRPLUS\n\n"
                    "повідомлень через межу: 4\n"
                    "LOOKUP каталогу · OPENDIR ·\n"
                    "READDIRPLUS · RELEASEDIR\n\n"
                    "викликів вашого getattr: 13",
                    size=13, fill=DATA_FILL, stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'getattr-funnel.svg'), W, H, *p)


fig_read_roundtrip()
fig_mount_handshake()
fig_data_paths()
fig_fuse_queues()
fig_init_negotiation()
fig_getattr_funnel()
print("ok")
