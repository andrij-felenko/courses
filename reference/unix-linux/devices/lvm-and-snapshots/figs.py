# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GRAY_FILL = "#eef1f4"
WARM = "#b8860b"


# ── 1. Логічний том — не шматок диска, а список екстентів ───────────────────
def fig_extent_mapping():
    W, H = 1240, 760
    p = []

    p.append(text(60, 60, "Фізичні томи: кожен диск порізано на екстенти однакового розміру (типово 4 МіБ)",
                  size=15, anchor="start", bold=True))

    pvs = [(60, "/dev/sda2", BLUE_FILL, NEG),
           (460, "/dev/sdb1", GREEN_FILL, FIELD),
           (860, "/dev/sdc1", WARM_FILL, WARM)]
    for x0, name, fill, stroke in pvs:
        p.append(text(x0, 96, name, size=13, anchor="start", bold=True, color=stroke))
        for k in range(8):
            p.append(rect(x0 + k * 38, 110, 34, 36, fill=fill, stroke=stroke, sw=1.3, rx=4))

    p.append(fitbox(60, 190, 1104, 52,
                    "Група томів vg0 — спільний запас усіх екстентів; окремих дисків тут уже не видно",
                    size=15, bold=True, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    p.append(text(60, 300, "Логічний том home — упорядкований список екстентів; кольором позначено, з якого диска взято кожен",
                  size=15, anchor="start", bold=True))

    lv = [("логічний 0", "sda2 · 3", BLUE_FILL, NEG),
          ("логічний 1", "sda2 · 4", BLUE_FILL, NEG),
          ("логічний 2", "sdb1 · 0", GREEN_FILL, FIELD),
          ("логічний 3", "sdb1 · 1", GREEN_FILL, FIELD),
          ("логічний 4", "sdc1 · 5", WARM_FILL, WARM),
          ("логічний 5", "sdc1 · 6", WARM_FILL, WARM)]
    for i, (top, src, fill, stroke) in enumerate(lv):
        x0 = 60 + i * 186
        p.append(fitbox(x0, 325, 170, 66, top + "\n" + src, size=13,
                        fill=fill, stroke=stroke, sw=1.6))

    p.append(text(60, 448, "Файлова система бачить суцільну стрічку 0…5 і не знає, що екстенти лежать на трьох різних дисках",
                  size=13, anchor="start", color=MUTED))

    p.append(rect(60, 490, 1104, 210, fill=BG, stroke=INK, sw=1.6, rx=10))
    p.append(text(84, 524, "Те саме, як його бачить ядро — таблиця device mapper:",
                  size=14, anchor="start", bold=True))
    rows = [
        "0        16384   linear   /dev/sda2   24576",
        "16384    16384   linear   /dev/sdb1    2048",
        "32768    16384   linear   /dev/sdc1   42048",
    ]
    for j, r in enumerate(rows):
        p.append(text(84, 566 + j * 34, r, size=14, anchor="start", color=NEG))
    p.append(text(84, 676,
                  "початок  довжина  ціль     пристрій    зсув        (усе — у секторах по 512 байтів)",
                  size=13, anchor="start", color=MUTED))

    render(os.path.join(IMG, "extent-mapping.svg"), W, H, *p)


# ── 2. Старий знімок: копіювання при записі через сховище винятків ──────────
def fig_cow_snapshot():
    W, H = 1220, 800
    p = []

    p.append(text(60, 58, "Програма пише в чанк, який ще жодного разу не змінювали від створення знімка",
                  size=15, anchor="start", bold=True))

    # origin
    p.append(text(80, 108, "origin — робочий том", size=14, anchor="start", bold=True))
    for i in range(5):
        hot = (i == 2)
        p.append(fitbox(80, 126 + i * 62, 250, 52,
                        ("чанк 2 — сюди пишуть" if hot else "чанк %d" % i),
                        size=13, fill=RED_FILL if hot else GRAY_FILL,
                        stroke=POS if hot else MUTED, sw=1.8 if hot else 1.3))

    # exception table
    p.append(text(460, 108, "таблиця винятків", size=14, anchor="start", bold=True))
    p.append(rect(460, 126, 300, 176, fill=BG, stroke=INK, sw=1.6, rx=8))
    p.append(fitbox(480, 150, 260, 40, "чанк 0  →  COW 0", size=13,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.3))
    p.append(fitbox(480, 200, 260, 40, "чанк 2  →  COW 1", size=13,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))
    p.append(text(480, 274, "новий рядок з'явився щойно", size=12, anchor="start", color=WARM))

    # cow store
    p.append(text(880, 108, "COW-том — сховище винятків", size=14, anchor="start", bold=True))
    cow = ["COW 0 — старий чанк 0", "COW 1 — старий чанк 2", "вільне", "вільне"]
    for i, s in enumerate(cow):
        used = i < 2
        p.append(fitbox(880, 126 + i * 62, 260, 52, s, size=13,
                        fill=WARM_FILL if used else BG,
                        stroke=WARM if used else MUTED, sw=1.6 if used else 1.2))

    p.append(arrow(340, 322, 468, 322, color=WARM, sw=2))
    p.append(arrow(770, 322, 872, 322, color=WARM, sw=2))

    # steps
    p.append(text(60, 430, "У що перетворюється один-єдиний запис програми:", size=15,
                  anchor="start", bold=True))
    steps = [
        "① прочитати з origin\nстарий вміст чанка 2",
        "② записати цей вміст\nу вільне місце COW-тому",
        "③ додати рядок\nу таблицю винятків",
        "④ і аж тепер покласти\nнові дані в origin",
    ]
    for i, s in enumerate(steps):
        p.append(fitbox(60 + i * 285, 460, 260, 86, s, size=13,
                        fill=BLUE_FILL, stroke=NEG, sw=1.5))

    p.append(fitbox(60, 590, 1100, 60,
                    "Поки чанк не скопійовано, кожен запис у нього коштує носієві вчетверо дорожче; наступні записи в той самий чанк — уже звичайні",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.8))

    p.append(fitbox(60, 676, 1100, 76,
                    "Читання знімка: якщо чанк є в таблиці винятків — беремо з COW-тому, інакше — прямо з origin\n"
                    "Скільки місця треба COW-тому — залежить не від розміру тому, а від того, скільки різних чанків змінять",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, "cow-snapshot.svg"), W, H, *p)


# ── 3. Тонкий пул: два рівноправні дерева над спільними блоками ─────────────
def fig_thin_trees():
    W, H = 1260, 720
    p = []

    p.append(text(60, 56, "Після знімка немає «оригіналу» й «знімка» — є два дерева відображень над одним запасом блоків",
                  size=15, anchor="start", bold=True))

    p.append(fitbox(200, 90, 240, 54, "дерево thin LV", size=14, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(820, 90, 240, 54, "дерево знімка", size=14, bold=True,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    leaves = [(100, "логічний 0", BLUE_FILL, NEG), (340, "логічний 1", BLUE_FILL, NEG),
              (720, "логічний 0", GREEN_FILL, FIELD), (960, "логічний 1", GREEN_FILL, FIELD)]
    for x0, s, fill, stroke in leaves:
        p.append(fitbox(x0, 210, 200, 50, s, size=13, fill=fill, stroke=stroke, sw=1.5))

    p.append(line(320, 144, 200, 208, color=NEG, sw=1.6))
    p.append(line(320, 144, 440, 208, color=NEG, sw=1.6))
    p.append(line(940, 144, 820, 208, color=FIELD, sw=1.6))
    p.append(line(940, 144, 1060, 208, color=FIELD, sw=1.6))

    # pool
    p.append(rect(60, 470, 1140, 150, fill=GRAY_FILL, stroke=MUTED, sw=1.6, rx=10))
    p.append(text(80, 500, "спільний запас блоків пулу", size=14, anchor="start", bold=True, color=MUTED))
    blocks = [(100, "новий блок\nпосилань: 1", WARM_FILL, WARM),
              (400, "старий вміст 0\nпосилань: 1", GREEN_FILL, FIELD),
              (700, "вміст 1\nпосилань: 2", BLUE_FILL, NEG),
              (1000, "вільний", BG, MUTED)]
    for x0, s, fill, stroke in blocks:
        p.append(fitbox(x0, 516, 180, 76, s, size=13, fill=fill, stroke=stroke, sw=1.6))

    p.append(arrow(200, 262, 190, 512, color=WARM, sw=2))
    p.append(arrow(440, 262, 790, 512, color=NEG, sw=2))
    p.append(arrow(820, 262, 490, 512, color=FIELD, sw=2))
    p.append(arrow(1060, 262, 790, 512, color=FIELD, sw=2))

    p.append(fitbox(60, 646, 1140, 58,
                    "У thin LV щойно переписали логічний блок 0: пул видав новий блок і дерево вказало на нього; дерево знімка далі показує старий вміст",
                    size=14, fill=BG, stroke=INK, sw=1.6))

    render(os.path.join(IMG, "thin-trees.svg"), W, H, *p)


# ── 4. Що змінилося між LVM1 і LVM2 (вставка hist-) ────────────────────────
def fig_lvm1_vs_lvm2():
    W, H = 1360, 700
    p = []

    LX, RX, PW = 50, 710, 600

    # ── ліва панель: LVM1 ───────────────────────────────────────────────
    p.append(text(LX + PW / 2, 44, "LVM1 — латка до ядра 2.2, у дереві з 2.4",
                  size=16, bold=True, color=NEG))

    p.append(rect(LX, 70, PW, 62, fill=GRAY_FILL, stroke=MUTED))
    p.append(mtext(LX + PW / 2, 94, ["простір користувача: команди LVM",
                                     "лише передають накази модулю"], size=14))

    p.append(arrow(LX + PW / 2, 132, LX + PW / 2, 168, color=INK))

    p.append(rect(LX, 168, PW, 232, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(text(LX + PW / 2, 196, "один модуль ядра: lvm.o", size=15, bold=True, color=NEG))
    inner = ["розбір двійкових метаданих з диска",
             "відображення екстентів на носії",
             "знімки — лише для читання"]
    for j, s in enumerate(inner):
        p.append(fitbox(LX + 30, 214 + j * 58, PW - 60, 44, s, size=14,
                        fill=BG, stroke=NEG, sw=1.2))

    p.append(text(LX + PW / 2, 442, "хто теж хоче підмінювати блоки — будує свій стек:",
                  size=14, color=MUTED))
    p.append(fitbox(LX, 462, PW / 2 - 15, 62, "md — дзеркала й RAID",
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.5))
    p.append(fitbox(LX + PW / 2 + 15, 462, PW / 2 - 15, 62, "cryptoloop — шифрування",
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.5))
    p.append(fitbox(LX, 556, PW, 62,
                    "три незалежні механізми роблять те саме й не складаються один з одним",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.5))

    # ── роздільник ──────────────────────────────────────────────────────
    p.append(line(680, 60, 680, 630, color=MUTED, sw=1, dash="6,6"))

    # ── права панель: LVM2 ──────────────────────────────────────────────
    p.append(text(RX + PW / 2, 44, "LVM2 — ядро 2.6, від 17 грудня 2003",
                  size=16, bold=True, color=FIELD))

    p.append(rect(RX, 70, PW, 62, fill=GRAY_FILL, stroke=MUTED))
    p.append(mtext(RX + PW / 2, 94, ["простір користувача: lvm2 + libdevmapper",
                                     "читають текстові метадані, складають таблицю"], size=14))

    p.append(arrow(RX + PW / 2, 132, RX + PW / 2, 168, color=INK))

    p.append(rect(RX, 168, PW, 96, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(text(RX + PW / 2, 198, "device mapper у ядрі", size=15, bold=True, color=FIELD))
    p.append(text(RX + PW / 2, 228, "виконує таблицю «діапазон адрес → ціль»", size=14))
    p.append(text(RX + PW / 2, 250, "про групи томів не знає нічого", size=13, color=MUTED))

    tg = ["linear", "snapshot", "crypt", "mirror"]
    tw = (PW - 3 * 14) / 4
    for j, s in enumerate(tg):
        x = RX + j * (tw + 14)
        p.append(arrow(x + tw / 2, 264, x + tw / 2, 306, color=FIELD, sw=1.4))
        p.append(fitbox(x, 306, tw, 48, s, size=14, fill=BG, stroke=FIELD, sw=1.4))

    p.append(text(RX + PW / 2, 388, "цілі — змінний список, ядро добудовують без LVM:",
                  size=14, color=MUTED))
    p.append(fitbox(RX, 408, PW, 56,
                    "згодом сюди ж стали multipath, thin, dm-verity, dm-cache",
                    size=14, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(RX, 490, PW, 128,
                    "механіка спільна: знімки, шифрування й дзеркала стали цілями "
                    "ОДНОГО шару, а політику «з яких екстентів скласти том» винесено "
                    "нагору, у програму",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, "lvm1-vs-lvm2.svg"), W, H, *p)


# ── 5. Стек dm-пристроїв, які насправді створює одна команда LVM ───────────
def fig_dm_stack():
    W, H = 1360, 840
    p = []

    p.append(text(60, 54, "Одна команда LVM створює не один пристрій, а стек: "
                          "видиме ім'я вгорі, шари й приховані томи під ним",
                  size=16, anchor="start", bold=True))

    LX, RX, BW = 60, 720, 580          # ліва й права колонки

    # ── ліва колонка: класичний знімок ───────────────────────────────────
    p.append(fitbox(LX, 92, BW, 46,
                    "lvcreate -s -n snap -L 5G vg0/base",
                    size=15, bold=True, fill=GRAY_FILL, stroke=INK, sw=1.6))

    p.append(text(LX, 168, "видимі імена в /dev/mapper", size=13,
                  anchor="start", color=MUTED))
    p.append(fitbox(LX, 184, 274, 84,
                    "vg0-base\nsnapshot-origin", size=14,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(LX + 306, 184, 274, 84,
                    "vg0-snap\nsnapshot", size=14,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))

    p.append(text(LX, 314, "шари — власних імен LV не мають", size=13,
                  anchor="start", color=MUTED))
    p.append(fitbox(LX, 330, 274, 84,
                    "vg0-base-real\nlinear", size=14,
                    fill=BG, stroke=MUTED, sw=1.4))
    p.append(fitbox(LX + 306, 330, 274, 84,
                    "vg0-snap-cow\nlinear", size=14,
                    fill=BG, stroke=MUTED, sw=1.4))

    p.append(arrow(LX + 137, 268, LX + 137, 328, color=NEG, sw=1.8))
    p.append(arrow(LX + 443, 268, LX + 443, 328, color=WARM, sw=1.8))
    p.append(arrow(LX + 400, 268, LX + 180, 328, color=WARM, sw=1.6))

    p.append(fitbox(LX, 470, BW, 56, "/dev/sdb1  —  екстенти групи vg0",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(arrow(LX + 137, 414, LX + 137, 468, color=MUTED, sw=1.6))
    p.append(arrow(LX + 443, 414, LX + 443, 468, color=MUTED, sw=1.6))

    p.append(fitbox(LX, 566, BW, 118,
                    "знімок читає з обох: чанк є в таблиці винятків — бере\n"
                    "з -cow, немає — прямо з -real; тому знищення знімка\n"
                    "прибирає два верхні пристрої, а -real стає зайвим",
                    size=13, fill=GRAY_FILL, stroke=MUTED, sw=1.3))

    # ── права колонка: тонкий пул ────────────────────────────────────────
    p.append(fitbox(RX, 92, BW, 46,
                    "lvcreate -T vg0/pool -V 2T -n app",
                    size=15, bold=True, fill=GRAY_FILL, stroke=INK, sw=1.6))

    p.append(text(RX, 168, "видимі імена в /dev/mapper", size=13,
                  anchor="start", color=MUTED))
    p.append(fitbox(RX, 184, 274, 84,
                    "vg0-pool\nlinear", size=14,
                    fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(RX + 306, 184, 274, 84,
                    "vg0-app\nthin", size=14,
                    fill=WARM_FILL, stroke=WARM, sw=1.8))

    p.append(text(RX, 314, "шар пулу — сюди дивляться обидва", size=13,
                  anchor="start", color=MUTED))
    p.append(fitbox(RX + 150, 330, 280, 84,
                    "vg0-pool-tpool\nthin-pool", size=14,
                    fill=BG, stroke=INK, sw=1.8))

    p.append(arrow(RX + 137, 268, RX + 250, 328, color=NEG, sw=1.8))
    p.append(arrow(RX + 443, 268, RX + 330, 328, color=WARM, sw=1.8))

    p.append(text(RX, 452, "приховані томи — lvs показує їх у дужках і лише з -a",
                  size=13, anchor="start", color=MUTED))
    p.append(fitbox(RX, 470, 274, 84,
                    "vg0-pool_tmeta\nlinear", size=14,
                    fill=RED_FILL, stroke=POS, sw=1.4))
    p.append(fitbox(RX + 306, 470, 274, 84,
                    "vg0-pool_tdata\nlinear", size=14,
                    fill=BG, stroke=MUTED, sw=1.4))

    p.append(arrow(RX + 250, 414, RX + 150, 468, color=MUTED, sw=1.6))
    p.append(arrow(RX + 330, 414, RX + 440, 468, color=MUTED, sw=1.6))

    p.append(fitbox(RX, 604, BW, 56, "/dev/sdb1  —  екстенти групи vg0",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(arrow(RX + 137, 554, RX + 137, 602, color=MUTED, sw=1.6))
    p.append(arrow(RX + 443, 554, RX + 443, 602, color=MUTED, sw=1.6))

    p.append(fitbox(RX, 700, BW, 62,
                    "_tmeta червоний навмисно: він менший за всіх\n"
                    "і кінчається першим, а це вбиває цілий пул",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.6))

    render(os.path.join(IMG, "dm-stack.svg"), W, H, *p)


# ── 6. Крива заповнення: E/M = 1 − e^(−ρ) ───────────────────────────────────
def fig_fill_curve():
    W, H = 1180, 730
    X0, X1, Y0, Y1 = 150.0, 1080.0, 560.0, 140.0     # рамка поля
    SX = (X1 - X0) / 5.0                              # 1 одиниця ρ
    SY = Y0 - Y1                                      # 100 %

    def px(r):
        return X0 + r * SX

    def py(f):
        return Y0 - f * SY

    p = []
    p.append(text(60, 48, "Скільки різних чанків тому торкнуться за час життя знімка",
                  size=15, anchor="start", bold=True))
    p.append(text(150, 100, "частка тому, яку займе сховище винятків",
                  size=13, anchor="start", color=MUTED))

    # осі
    p.append(line(X0, Y0, X1, Y0, color=INK, sw=1.8))
    p.append(line(X0, Y0, X0, Y1, color=INK, sw=1.8))
    for k in range(1, 6):
        p.append(text(px(k), 585, str(k), size=13, color=MUTED))
    p.append(text(X1, 615, "ρ = N / M  —  торкань на один чанк тому",
                  size=13, anchor="end", color=MUTED))

    # рівні насичення
    for f, lab in ((0.63, "63 %"), (0.95, "95 %")):
        p.append(line(X0, py(f), X1, py(f), color=MUTED, sw=1.1, dash="5 6"))
        p.append(text(140, py(f) + 5, lab, size=13, anchor="end", color=MUTED))
    p.append(text(140, 566, "0", size=13, anchor="end", color=MUTED))

    # наївна пряма E = N
    p.append(line(px(0), py(0), px(1), py(1), color=MUTED, sw=1.6, dash="7 7"))
    p.append(text(344, 136, "наївна оцінка N·c", size=14, anchor="start", color=MUTED))

    # сама крива
    prev = None
    for i in range(0, 251):
        r = i * 0.02
        cur = (px(r), py(1.0 - math.exp(-r)))
        if prev:
            p.append(line(prev[0], prev[1], cur[0], cur[1], color=NEG, sw=2.6))
        prev = cur

    # три робочі точки
    pts = [(0.1448, 0.1348, NEG, BLUE_FILL),
           (1.1587, 0.6861, WARM, WARM_FILL),
           (4.6349, 0.9903, POS, RED_FILL)]
    for r, f, col, fil in pts:
        p.append(circle(px(r), py(f), 7, fill=fil, stroke=col, sw=2.4))

    p.append(text(200, 518, "чанк 4 КіБ:   ρ = 0.14  →  13 % тому",
                  size=14, anchor="start", color=NEG, bold=True))
    p.append(text(392, 330, "чанк 64 КіБ:   ρ = 1.16  →  69 % тому",
                  size=14, anchor="start", color=WARM, bold=True))
    p.append(text(1120, 112, "чанк 256 КіБ:   ρ = 4.63  →  99 % тому",
                  size=14, anchor="end", color=POS, bold=True))

    p.append(fitbox(60, 640, 1060, 66,
                    "Поки торкань менше, ніж чанків, витрата йде майже врівень із записаним; далі повтори\n"
                    "починають траплятися все частіше, і крива лягає в стелю — увесь том, і ані байта більше",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, "fill-curve.svg"), W, H, *p)


# ── 7. Той самий запис, три розміри чанка ───────────────────────────────────
def fig_chunk_cost():
    W, H = 1100, 620
    BX = 260.0                       # ліва межа стовпчиків
    S = 680.0 / 560.0                # px на ГіБ (шкала 0…560 ГіБ)

    p = []
    p.append(text(60, 48, "74 ГіБ розкиданого запису по 8 КіБ за три години на томі 512 ГіБ",
                  size=15, anchor="start", bold=True))

    rows = [(150, "чанк 4 КіБ", "класичний знімок", 69.0, "69 ГіБ  ·  ×0.93 від записаного",
             BLUE_FILL, NEG),
            (250, "чанк 64 КіБ", "тонкий пул, чанк задано вручну", 351.3, "351 ГіБ  ·  ×4.7",
             WARM_FILL, WARM),
            (350, "чанк 256 КіБ", "тонкий пул за умовчанням", 507.0, "507 ГіБ  ·  ×6.8",
             RED_FILL, POS)]
    for y, name, sub, gib, val, fil, col in rows:
        p.append(text(248, y + 26, name, size=14, anchor="end", bold=True, color=col))
        p.append(text(248, y + 48, sub, size=12, anchor="end", color=MUTED))
        p.append(rect(BX, y, gib * S, 62, fill=fil, stroke=col, sw=1.8, rx=5))
        p.append(text(BX + gib * S + 16, y + 38, val, size=14, anchor="start", bold=True, color=col))

    # шкала
    p.append(line(BX, 430, BX + 640, 430, color=MUTED, sw=1.4))
    for g in (0, 128, 256, 384, 512):
        x = BX + g * S
        p.append(line(x, 424, x, 430, color=MUTED, sw=1.4))
        p.append(text(x, 450, ("%d ГіБ" % g) if g == 512 else str(g), size=12, color=MUTED))
    p.append(line(BX + 512 * S, 120, BX + 512 * S, 424, color=POS, sw=1.5, dash="6 7"))
    p.append(text(BX + 512 * S, 108, "512 ГіБ — увесь том", size=13, anchor="end", color=POS))

    p.append(fitbox(60, 480, 980, 96,
                    "Записано те саме; різниця — лише в зернистості обліку. Множник c/w бере повний чанк\n"
                    "за кожен торкнутий, а знижка за повтори (1 − e^(−ρ))/ρ його трохи гасить — але не рятує:\n"
                    "при чанку 256 КіБ знімок за три години коштує майже другий такий самий том",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.6))

    render(os.path.join(IMG, "chunk-cost.svg"), W, H, *p)


fig_extent_mapping()
fig_cow_snapshot()
fig_thin_trees()
fig_lvm1_vs_lvm2()
fig_dm_stack()
fig_fill_curve()
fig_chunk_cost()
print("ok")
