# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
AMBER = "#b7791f"


# ── 1. Шлях байта від буфера програми до носія ─────────────────────────────────
def fig_write_path():
    W, H = 1180, 720
    p = []

    BX, BW, BH = 60, 430, 74
    ys = [70, 210, 350, 490, 620]

    stages = [
        ("буфер програми",
         "власна пам'ять процесу", MUTED, SOFT),
        ("сторінка кешу сторінок, позначена «брудна»",
         "оперативна пам'ять, якою розпоряджається ядро", POS, WARM),
        ("черга запитів блокового пристрою",
         "оперативна пам'ять, якою розпоряджається ядро", POS, WARM),
        ("кеш накопичувача",
         "енергозалежна пам'ять на платі пристрою", POS, WARM),
        ("носій: пластина або NAND",
         "переживає зникнення живлення", FIELD, GREEN),
    ]

    for i, (head, sub, accent, tint) in enumerate(stages):
        y = ys[i]
        p.append(rect(BX, y, BW, BH, fill=tint, stroke=accent, sw=1.8, rx=8))
        p.append(text(BX + BW / 2, y + 30, head, size=13, bold=True, color=INK))
        p.append(text(BX + BW / 2, y + 52, sub, size=10.5, color=MUTED))

    moves = [
        ("копіювання в межах пам'яті:\nжодної команди пристроєві не йде",
         "`write` повертає успіх одразу після цього кроку"),
        ("зворотний запис — за одним із трьох приводів:\nвік (типово 30 с) · обсяг (10 % і 20 % пам'яті) · прохання `fsync`",
         "до цього моменту зникнення живлення стирає зміни без сліду"),
        ("контролер підтверджує запис,\nщойно дані лягли в його власний буфер",
         "ядро вважає запит виконаним, хоча носій ще порожній"),
        ("лише за окремою командою скидання кешу\n(SYNCHRONIZE CACHE / FLUSH CACHE) або з ознакою FUA",
         "рівно тут закінчується довговічність — і рівно це вимикають «для швидкості»"),
    ]

    LX, LW = 545, 590
    for i, (what, note) in enumerate(moves):
        y0 = ys[i] + BH
        y1 = ys[i + 1]
        mid = (y0 + y1) / 2
        col = POS if i == 3 else NEG
        p.append(arrow(BX + BW / 2, y0 + 4, BX + BW / 2, y1 - 6, color=col, sw=2))
        p.append(mtext(LX, mid - 12, what, size=11, color=INK, anchor="start", lh=1.35))
        p.append(mtext(LX, mid + 26, note, size=10.5, color=col, anchor="start", lh=1.3))

    p.append(text(W / 2, H - 18,
                  "кожна стрілка має власний момент «прийнято»; успіх виклику каже лише про ту стрілку, яку він проходить",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "write-path.svg"), W, H, *p,
           title="Чотири передачі даних між буфером програми і носієм")


# ── 2. Що саме гарантує кожен виклик ───────────────────────────────────────────
def fig_levels():
    W, H = 1180, 520
    p = []

    LX, LW = 40, 330
    CX, CW = 380, 190
    HY, HH = 62, 66
    RY, RH = 136, 62
    GAP = 6

    cols = ["write()", "fdatasync(fd)", "fsync(fd)", "fsync(fd)\n+ fsync(каталогу)"]
    rows = [
        ("байти перейшли з програми до ядра",        ["так", "так", "так", "так"]),
        ("дані файлу пішли з пам'яті в пристрій",     ["ні", "так", "так", "так"]),
        ("розмір і список блоків (inode) на носії",   ["ні", "лише потрібне\nдля читання", "так", "так"]),
        ("нове ім'я в каталозі на носії",             ["ні", "ні", "ні", "так"]),
        ("пристрій скинув власний кеш на носій",      ["ні", "так *", "так *", "так *"]),
    ]

    p.append(fitbox(LX, HY, LW, HH, "що вважається зробленим", size=12,
                    fill="#eceff2", stroke=MUTED, sw=1.4, color=INK, bold=True))
    for j, c in enumerate(cols):
        x = CX + j * (CW + GAP)
        p.append(fitbox(x, HY, CW, HH, c, size=12,
                        fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))

    for i, (label, vals) in enumerate(rows):
        y = RY + i * (RH + GAP)
        p.append(fitbox(LX, y, LW, RH, label, size=11.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        for j, v in enumerate(vals):
            x = CX + j * (CW + GAP)
            yes = v.startswith("так")
            part = v.startswith("лише")
            tint = GREEN if yes else (WARM if part else "#f7f7f8")
            stro = FIELD if yes else (AMBER if part else MUTED)
            colr = FIELD if yes else (AMBER if part else MUTED)
            p.append(fitbox(x, y, CW, RH, v, size=11.5,
                            fill=tint, stroke=stro, sw=1.3, color=colr, bold=yes))

    p.append(text(W / 2, H - 26,
                  "* якщо скидання кешу пристрою не вимкнене налаштуванням черги, варіантом монтування або самим пристроєм",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "durability-levels.svg"), W, H, *p,
           title="Межа, до якої дотягується кожен виклик")


# ── 3. Надійна заміна файлу: стан диска після збою на кожному кроці ────────────
def fig_replace():
    W, H = 1240, 560
    p = []

    XS = [40, 345, 650, 955]
    CW = 245
    SY, SH = 66, 92
    NY, NH = 250, 150

    steps = [
        ("1. записати вміст\nу тимчасовий файл", "write(tmp)", POS, WARM,
         "старий файл цілий і робочий;\nтимчасовий на диску порожній —\nблоки для нього ще не виділено"),
        ("2. проштовхнути його\nна носій", "fsync(tmp)", AMBER, WARM,
         "старий файл цілий і робочий;\nпоруч лежить готовий тимчасовий,\nякий після збою просто зайвий"),
        ("3. підмінити ім'я", "rename(tmp, файл)", AMBER, WARM,
         "ім'я вже вказує на новий вміст,\nале сам запис каталогу може\nще лишатися тільки в пам'яті"),
        ("4. проштовхнути\nзапис каталогу", "fsync(каталог)", FIELD, GREEN,
         "нове ім'я і новий вміст на носії;\nз цієї миті заміна пережила б\nбудь-яке зникнення живлення"),
    ]

    for i, (head, call, accent, tint, state) in enumerate(steps):
        x = XS[i]
        p.append(fitbox(x, SY, CW, SH, head, size=12.5,
                        fill=tint, stroke=accent, sw=1.8, color=INK, bold=True))
        p.append(fitbox(x + 18, SY + SH + 14, CW - 36, 34, call, size=12,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=NEG))
        p.append(arrow(x + CW / 2, SY + SH + 54, x + CW / 2, NY - 8, color=accent, sw=1.7))
        p.append(fitbox(x, NY, CW, NH, state, size=11,
                        fill=SOFT, stroke=accent, sw=1.4, color=INK))
        if i < 3:
            p.append(arrow(x + CW + 12, SY + SH / 2, XS[i + 1] - 12, SY + SH / 2,
                           color=MUTED, sw=1.6))

    p.append(text(W / 2, NY - 26, "стан диска, якщо живлення зникло саме на цьому кроці",
                  size=12, color=MUTED, bold=True))

    p.append(fitbox(40, NY + NH + 40, W - 80, 62,
                    "у жодному з чотирьох станів читач не бачить половини файлу: до третього кроку працює старий вміст, "
                    "після нього — новий; проміжного вмісту не існує, бо підміна імені неподільна",
                    size=11.5, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "durable-replace.svg"), W, H, *p,
           title="Заміна файлу, що переживає збій на будь-якому кроці")


# ── 4. Пороги брудної пам'яті: три зони й важіль кожної межі ───────────────────
def fig_dirty_thresholds():
    W, H = 1180, 500
    p = []
    HOT = "#fdecea"

    X0, X1 = 100, 1080
    b1 = X0 + (X1 - X0) * 10.0 / 30.0
    b2 = X0 + (X1 - X0) * 20.0 / 30.0

    p.append(text(W / 2, 40, "Три зони поведінки зворотного запису і важіль, що рухає кожну межу",
                  size=13.5, bold=True, color=INK))

    knobs = [
        (b1, "dirty_background_ratio = 10 %\nабо dirty_background_bytes", AMBER, WARM),
        (b2, "dirty_ratio = 20 %\nабо dirty_bytes", POS, HOT),
    ]
    KY, KH, KW = 92, 62, 290
    for cx, label, accent, tint in knobs:
        p.append(fitbox(cx - KW / 2, KY, KW, KH, label, size=11.5,
                        fill=tint, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(line(cx, KY + KH + 4, cx, 190, color=accent, sw=1.4, dash="4,4"))

    BY, BH = 190, 64
    zones = [
        (X0, b1, "тільки за віком", GREEN, FIELD),
        (b1, b2, "фонове винесення", WARM, AMBER),
        (b2, X1, "дроселювання запису", HOT, POS),
    ]
    for xa, xb, label, tint, accent in zones:
        p.append(fitbox(xa, BY, xb - xa, BH, label, size=13,
                        fill=tint, stroke=accent, sw=1.8, color=accent, bold=True))

    p.append(arrow(X0, 278, X1, 278, color=MUTED, sw=1.6))
    p.append(text(W / 2, 300,
                  "частка брудних сторінок від доступної пам'яті (вільна + та, що вивільняється) — зростає праворуч",
                  size=11, color=MUTED, italic=True))

    DY, DH = 318, 96
    details = [
        (X0, b1, "потоки зворотного запису прокидаються\nза розкладом і виносять тільки те,\nщо брудне довше за поріг віку", FIELD),
        (b1, b2, "потоки зворотного запису працюють\nбезперервно; програма, що пише,\nу жорсткий поріг ще не впирається", AMBER),
        (b2, X1, "write() у самій програмі затримується,\nдоки зворотний запис не опустить\nчастку назад під поріг", POS),
    ]
    for xa, xb, txt, accent in details:
        p.append(fitbox(xa + 8, DY, xb - xa - 16, DH, txt, size=11,
                        fill=SOFT, stroke=accent, sw=1.4, color=INK))

    p.append(fitbox(40, 434, W - 80, 48,
                    "Вік діє в усіх трьох зонах незалежно від обсягу: dirty_writeback_centisecs = 500 — як часто прокидатися, "
                    "dirty_expire_centisecs = 3000 — з якого віку виносити.",
                    size=11.5, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "dirty-thresholds.svg"), W, H, *p,
           title="Пороги брудної пам'яті й важелі, що ними керують")


# ── 4. Прапорець проти лічильника: хто побачить помилку зворотного запису ──────
def fig_errseq():
    W, H = 1240, 640
    p = []

    AX, BX = 40, 660
    PW = 560
    LW, RW, GAP2 = 300, 230, 20
    HY, HH = 46, 46
    MY, MH = 116, 52
    RY, RH, RG = 214, 78, 22

    def panel(x0, head, head_col, head_tint, mid, rows):
        p.append(fitbox(x0, HY, PW, HH, head, size=13,
                        fill=head_tint, stroke=head_col, sw=1.8, color=INK, bold=True))
        p.append(fitbox(x0 + 70, MY, PW - 140, MH, mid, size=12,
                        fill="#ffffff", stroke=MUTED, sw=1.3, color=NEG))
        for i, (who, res, ok) in enumerate(rows):
            y = RY + i * (RH + RG)
            p.append(fitbox(x0, y, LW, RH, who, size=11.5,
                            fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
            col = FIELD if ok == "y" else (AMBER if ok == "w" else NEG)
            tint = GREEN if ok == "y" else (WARM if ok == "w" else "#fdeceb")
            p.append(arrow(x0 + LW + 6, y + RH / 2, x0 + LW + GAP2 - 4, y + RH / 2,
                           color=MUTED, sw=1.5))
            p.append(fitbox(x0 + LW + GAP2, y, RW, RH, res, size=11.5,
                            fill=tint, stroke=col, sw=1.4, color=col, bold=True))

    panel(AX,
          "до ядра 4.13: один прапорець на весь inode",
          NEG, WARM,
          "address_space: AS_EIO",
          [("сторонній `sync`, що трапився\nпершим після невдалого\nзворотного запису",
            "забирає прапорець\nсобі — і нікому\nпро це не каже", "n"),
           ("`fsync` бази даних,\nчиї сторінки саме й загинули",
            "0 — успіх", "n"),
           ("повторний `fsync`\nтієї самої бази",
            "0 — успіх, брудних\nсторінок уже немає", "n")])

    panel(BX,
          "з ядра 4.13: лічильник помилок errseq_t",
          FIELD, GREEN,
          "address_space: {EIO, №7}   ·   опис файлу: f_wb_err",
          [("дескриптор, відкритий\nдо помилки (f_wb_err = №6)",
            "EIO — рівно\nодин раз", "y"),
           ("інший дескриптор того самого\nфайлу, теж відкритий раніше",
            "теж EIO —\nсвій, окремий", "y"),
           ("дескриптор, відкритий\nвже ПІСЛЯ помилки (№7)",
            "0 — помилка\nдля нього в минулому", "w")])

    p.append(fitbox(40, H - 116, W - 80, 74,
                    "лічильник замінює «хто перший прочитав, той і забрав» на «кожен відкритий до помилки побачить її один раз»; "
                    "але дескриптор, відкритий уже після невдалого запису, не бачить нічого — саме в цю щілину й потрапляв "
                    "процес, який відкриває файли лише в момент контрольної точки",
                    size=11.5, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "errseq.svg"), W, H, *p,
           title="Хто побачить помилку зворотного запису: прапорець проти лічильника")


# ── Від шляху до лічильника скидань кеша пристрою ─────────────────────────────
def fig_device_chain():
    W, H = 1180, 650
    p = []

    BX, BW = 55, 470
    AX = 570

    def step(y, h, body, note, tint, accent, size=12):
        p.append(fitbox(BX, y, BW, h, body, size=size,
                        fill=tint, stroke=accent, sw=1.7, color=INK))
        if note:
            p.append(mtext(AX, y + h / 2 - 8, note, size=11, color=MUTED,
                           anchor="start", lh=1.35))

    step(70, 58, "шлях, довговічність якого перевіряємо\n/srv/data", "", SOFT, NEG)
    p.append(arrow(BX + BW / 2, 130, BX + BW / 2, 156, color=MUTED, sw=1.6))

    step(158, 62, "stat(шлях).st_dev  →  major : minor\nнаприклад  259 : 2",
         "st_dev називає не файлову систему, а блоковий пристрій;\n"
         "розкладають його макросами major() і minor()\nіз <sys/sysmacros.h>",
         COOL, NEG)
    p.append(arrow(BX + BW / 2, 222, BX + BW / 2, 248, color=MUTED, sw=1.6))

    step(250, 62, "/sys/dev/block/259:2\nсимвольне посилання в дерево пристроїв",
         "ціль — щось на кшталт\n/sys/devices/…/nvme0n1/nvme0n1p2", COOL, NEG)
    p.append(arrow(BX + BW / 2, 314, BX + BW / 2, 342, color=MUTED, sw=1.6))

    p.append(text(BX + BW / 2, 362, "чи лежить поруч файл «partition»?",
                  size=12.5, bold=True, color=AMBER))

    HW = (BW - 22) / 2
    p.append(fitbox(BX, 380, HW, 84,
                    "так — це РОЗДІЛ\nберемо на рівень вище\n…/259:2/../stat",
                    size=11.5, fill=WARM, stroke=AMBER, sw=1.7, color=INK))
    p.append(fitbox(BX + HW + 22, 380, HW, 84,
                    "ні — це вже ЦІЛИЙ ДИСК\nберемо як є\n…/259:2/stat",
                    size=11.5, fill=GREEN, stroke=FIELD, sw=1.7, color=INK))
    p.append(mtext(AX, 396,
                   "лічильники скидань для розділів НЕ ведуться —\n"
                   "рахує їх лише цілий диск, тож із розділу треба\n"
                   "піднятися на крок угору; «..» після символьного\n"
                   "посилання йде вгору від його цілі",
                   size=11, color=POS, anchor="start", lh=1.35))

    p.append(arrow(BX + HW / 2, 468, BX + BW / 2 - 34, 502, color=MUTED, sw=1.6))
    p.append(arrow(BX + HW + 22 + HW / 2, 468, BX + BW / 2 + 34, 502, color=MUTED, sw=1.6))

    p.append(fitbox(BX, 506, BW, 108,
                    "17 чисел одним рядком\n"
                    "поле 5 — записів завершено\n"
                    "поле 16 — скидань кеша завершено\n"
                    "поле 17 — мілісекунд на скидання",
                    size=12, fill=SOFT, stroke=FIELD, sw=1.8, color=INK))
    p.append(mtext(AX, 522,
                   "поля 16 і 17 з'явилися в ядрі 5.5;\n"
                   "на старішому ядрі рядок коротший,\n"
                   "і перевірити скидання цим способом не вийде.\n"
                   "Блоковий шар зливає одночасні скидання в одне,\n"
                   "тож приріст поля 16 буває МЕНШИЙ за кількість fsync",
                   size=11, color=MUTED, anchor="start", lh=1.35))

    render(os.path.join(OUT, "device-chain.svg"), W, H, *p,
           title="Як від імені файлу дійти до лічильника скидань кеша")


# ── Що мусить дійти до носія при кожному з двох викликів ──────────────────────
def fig_sync_matrix():
    W, H = 1140, 510
    p = []

    LX, LW = 35, 300
    CX, CW, GAP = 345, 375, 10
    HY, HH = 66, 52
    RY, RH = 132, 142

    p.append(fitbox(LX, HY, LW, HH, "що саме змінює програма", size=12,
                    fill="#eceff2", stroke=MUTED, sw=1.4, color=INK, bold=True))
    for j, c in enumerate(["fdatasync(fd)", "fsync(fd)"]):
        p.append(fitbox(CX + j * (CW + GAP), HY, CW, HH, c, size=13,
                        fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))

    rows = [
        ("перезапис уже виділених блоків\nрозмір файлу не змінюється",
         ("дані блоків\nі скидання кеша пристрою\n\ninode не оновлюють: час зміни\nдля читання не потрібен", GREEN, FIELD),
         ("дані блоків\nі час зміни в inode\n→ окремий коміт журналу\nі скидання кеша пристрою", WARM, AMBER)),
        ("дописування в кінець\nфайл росте",
         ("дані блоків\nновий розмір і карта блоків\n→ коміт журналу\nі скидання кеша пристрою", WARM, AMBER),
         ("те саме, що ліворуч:\nметадані все одно потрібні,\nтож економити нема на чому", WARM, AMBER)),
    ]

    for i, (label, a, b) in enumerate(rows):
        y = RY + i * (RH + GAP)
        p.append(fitbox(LX, y, LW, RH, label, size=11.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        for j, (txt, tint, accent) in enumerate((a, b)):
            p.append(fitbox(CX + j * (CW + GAP), y, CW, RH, txt, size=11.5,
                            fill=tint, stroke=accent, sw=1.5, color=INK))

    p.append(fitbox(LX, RY + 2 * (RH + GAP) + 18, W - 2 * LX, 50,
                    "Різниця між двома викликами вимірюється тільки в лівому верхньому куті; "
                    "на дописуванні вони роблять однакову роботу.",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "sync-matrix.svg"), W, H, *p,
           title="Скільки роботи мусить зробити пристрій на один виклик")


fig_write_path()
fig_levels()
fig_replace()
fig_errseq()
fig_dirty_thresholds()
fig_device_chain()
fig_sync_matrix()
print("ok")
