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
WARM = "#b8860b"


# ── 1. Арифметика створення: запит програми мінус маска процесу ──────────────
def fig_mask_subtraction():
    W, H = 1240, 800
    p = []

    LX, LW = 50, 250
    CX, CW, GAP, GGAP = 330, 54, 10, 30
    GW = 3 * CW + 2 * GAP          # 182
    OX, OW = 1000, 190             # колонка вісімкового запису

    def gx(i):
        return CX + i * (GW + GGAP)

    p.append(fitbox(LX, 44, 1140, 60,
                    "режим нового об'єкта = режим, який попросила програма   &   ~маска процесу",
                    size=17, bold=True, fill=FILL, stroke=LINE))

    for i, head in enumerate(("власник", "група", "решта")):
        p.append(text(gx(i) + GW / 2, 138, head, size=14, bold=True))
    p.append(text(OX + OW / 2, 138, "вісімкою", size=14, bold=True, color=MUTED))

    rows = [
        ("чого просить програма\nopen(..., O_CREAT, 0666)",
         ["r", "w", "-", "r", "w", "-", "r", "w", "-"],
         "0666", GREEN_FILL, FIELD),
        ("що маска велить зняти\numask 0022",
         ["·", "·", "·", "·", "w", "·", "·", "w", "·"],
         "0022", RED_FILL, POS),
        ("що лишилося в новому файлі",
         ["r", "w", "-", "r", "-", "-", "r", "-", "-"],
         "0644", BLUE_FILL, NEG),
    ]

    y = 158
    for label, cells, octal, fill, stroke in rows:
        p.append(fitbox(LX, y, LW, 66, label, size=13, fill=BG, stroke=MUTED))
        for i in range(3):
            for j in range(3):
                ch = cells[i * 3 + j]
                p.append(fitbox(gx(i) + j * (CW + GAP), y, CW, 66, ch,
                                size=22, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(OX, y, OW, 66, octal, size=20, bold=True,
                        fill=BG, stroke=stroke))
        y += 92

    p.append(fitbox(LX, 448, 1140, 66,
                    "біта x у запиті не було — і маска його не поверне:\n"
                    "навіть із umask 000 такий open дасть 0666, а не 0777",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(LX, 556, 1140, 54,
                    "той самий рахунок для інших об'єктів, різниця лише в тому, що просить програма",
                    size=14, bold=True, fill=FILL, stroke=LINE))

    cases = [
        ("mkdir(..., 0777)", "0777 & ~0022", "0755  drwxr-xr-x", GREEN_FILL, FIELD),
        ("open(..., 0600)\nключ, генератор наполягає", "0600 & ~0022", "0600  -rw-------", BLUE_FILL, NEG),
        ("open(..., 0666)\nта сама програма, umask 0077", "0666 & ~0077", "0600  -rw-------", WARM_FILL, WARM),
    ]
    CCW = (1140 - 2 * 30) // 3
    for i, (what, calc, res, fill, stroke) in enumerate(cases):
        x = LX + i * (CCW + 30)
        p.append(fitbox(x, 632, CCW, 62, what, size=13, fill=fill, stroke=stroke))
        p.append(fitbox(x, 706, CCW, 40, calc, size=14, fill=BG, stroke=MUTED))
        p.append(fitbox(x, 758, CCW, 40, res, size=14, bold=True, fill=BG, stroke=stroke))

    render(os.path.join(IMG, 'mask-subtraction.svg'), W, H, *p,
           title="Права нового об'єкта: запит програми за вирахуванням маски процесу")


# ── 2. Звідки маска приходить у процес і як спускається деревом ──────────────
def fig_mask_inheritance():
    W, H = 1280, 860
    p = []

    p.append(fitbox(50, 44, 1180, 72,
                    "маска — властивість ПРОЦЕСУ: не файлу, не каталогу й не облікового запису\n"
                    "копіюється дитині при fork і переживає exec — тому веде себе як частина оточення",
                    size=15, bold=True, fill=FILL, stroke=LINE))

    LX, LW = 50, 540
    RX, RW = 690, 540

    left = [
        ("PID 1 — systemd", "власна маска 0022", GREEN_FILL, FIELD, 66),
        ("юніт служби", "UMask=0027 у [Service] —\nстає маскою цього процесу", BLUE_FILL, NEG, 82),
        ("процес служби", "маска 0027 → журнали виходять 0640", BLUE_FILL, NEG, 66),
        ("усе, що служба запускає", "та сама 0027, поки хтось не викличе umask()", FILL, LINE, 66),
    ]

    right = [
        ("вхід у систему", "консоль, ssh, графічний сеанс", GREEN_FILL, FIELD, 66),
        ("стек PAM", "pam_umask бере UMASK\nз /etc/login.defs", WARM_FILL, WARM, 82),
        ("оболонка", "profile і rc можуть перевизначити:\numask 002", WARM_FILL, WARM, 82),
        ("усе, що ви запускаєте з неї", "успадкована 002 → файли 0664", FILL, LINE, 66),
    ]

    def chain(x, w, items, y0):
        y = y0
        for i, (head, note, fill, stroke, h) in enumerate(items):
            p.append(fitbox(x, y, 230, h, head, size=15, bold=True, fill=fill, stroke=stroke))
            p.append(fitbox(x + 254, y, w - 254, h, note, size=13, fill=BG, stroke=MUTED))
            if i < len(items) - 1:
                p.append(arrow(x + 115, y + h + 4, x + 115, y + h + 40))
            y += h + 44
        return y

    p.append(fitbox(LX, 148, LW, 50, "гілка служб", size=15, bold=True,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(RX, 148, RW, 50, "гілка людини за клавіатурою", size=15, bold=True,
                    fill=GREEN_FILL, stroke=FIELD))

    ye = chain(LX, LW, left, 222)
    chain(RX, RW, right, 222)

    p.append(fitbox(50, 700, 1180, 72,
                    "у ядрі маска зберігається біля робочого каталогу й кореня процесу —\n"
                    "серед того, що процес несе з собою, а не серед того, що лежить на диску",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(50, 788, 1180, 62,
                    "правка profile чи login.defs не діє на вже запущені процеси: демон, народжений при завантаженні,\n"
                    "довіку тримає маску того моменту — звідси різні права у файлів вашої оболонки й тієї самої задачі з cron",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'mask-inheritance.svg'), W, H, *p,
           title="Звідки маска приходить у процес і як спускається деревом")


# ── 3. Де маска діє, а де її навіть не питають ──────────────────────────────
def fig_mask_scope():
    W, H = 1280, 820
    p = []

    LX, LW = 50, 570
    RX, RW = 660, 570

    p.append(fitbox(LX, 44, LW, 66,
                    "проходить крізь маску\nу виклику є аргумент режиму, і об'єкт народжується зараз",
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(RX, 44, RW, 66,
                    "маски не бачить\nабо режим ставлять окремою дією, або його диктує щось інше",
                    size=14, bold=True, fill=RED_FILL, stroke=POS))

    left = [
        "open, openat, creat з O_CREAT — новий файл",
        "O_TMPFILE — безіменний файл на справжній ФС",
        "mkdir, mkdirat — каталог",
        "mknod, mkfifo — файл пристрою, іменований канал",
        "bind — вузол сокета домену Unix у файловій системі",
        "mq_open, sem_open, shm_open — об'єкти POSIX IPC",
    ]
    right = [
        "chmod, fchmod — режим наявного об'єкта, маска тут ні до чого",
        "open без O_CREAT (і з O_CREAT на наявний файл) —\nаргумент режиму просто не використовують",
        "cp -p, tar -p, install -m, mkdir -m —\nстворюють, а потім ставлять режим точно",
        "каталог із типовим ACL — маску цілком ігнорують,\nправа беруть із успадкованого ACL",
        "FAT, NTFS, exFAT — режим дає монтування\n(umask=, fmask=, dmask=), і це інший механізм",
    ]

    y = 138
    for s in left:
        p.append(fitbox(LX, y, LW, 62, s, size=13, fill=BG, stroke=FIELD))
        y += 74

    y = 138
    for s in right:
        p.append(fitbox(RX, y, RW, 84, s, size=13, fill=BG, stroke=POS))
        y += 96

    p.append(fitbox(LX, 640, 1180, 66,
                    "у справу йдуть лише молодші дев'ять бітів: ядро бере mask & 0777",
                    size=15, bold=True, fill=FILL, stroke=LINE))
    p.append(fitbox(LX, 724, 1180, 82,
                    "тому спеціальних бітів маска не чіпає взагалі: setgid, успадкований новим підкаталогом\n"
                    "від батьківського каталогу, лишається на місці, хай яка маска стоїть у процесі",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'mask-scope.svg'), W, H, *p,
           title="Де маска діє, а де її навіть не питають")


# ── 4. Вікно, у якому маска процесу дорівнює нулю (вставка proj-exact-mode) ──
def fig_race_window():
    W, H = 1240, 660
    p = []

    LX, LW = 50, 240
    T0, T1 = 352, 944          # межі вікна між umask(0) і umask(old)

    p.append(fitbox(60, 40, 1120, 56,
                    "umask(0) … umask(old) — це не «прочитати маску», а вимкнути її для ВСЬОГО процесу",
                    size=17, bold=True, fill=FILL, stroke=LINE))

    p.append(line(T0, 126, T0, 452, color=POS, sw=2, dash="7,5"))
    p.append(line(T1, 126, T1, 452, color=POS, sw=2, dash="7,5"))
    p.append(fitbox(T0 + 10, 132, T1 - T0 - 20, 46,
                    "вікно, у якому маска процесу = 0000",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(LX, 208, LW, 70, "Потік A\nгенерує ключ",
                    size=14, bold=True, fill=BG, stroke=MUTED))
    p.append(fitbox(T0 + 18, 208, 190, 70, "old = umask(0)",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(600, 208, 300, 70, "open(\"key.pem\",\nO_CREAT, 0600)",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(T1 + 18, 208, 190, 70, "umask(old)",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(LX, 320, LW, 82, "Потік B\nскидає кеш на диск",
                    size=14, bold=True, fill=BG, stroke=MUTED))
    p.append(fitbox(T0 + 18, 320, 360, 82,
                    "open(\"cache.db\",\nO_CREAT|O_TRUNC, 0666)",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(T0 + 390, 361, T1 + 10, 361, color=POS))
    p.append(fitbox(T1 + 18, 320, 250, 82, "вийшло 0666\nзамість 0644",
                    size=15, bold=True, fill=RED_FILL, stroke=POS))

    p.append(fitbox(60, 478, 1120, 62,
                    "маска — поле процесу, а не потоку: pthread_create клонує задачу з CLONE_FS,\n"
                    "тож структура з коренем, робочим каталогом і маскою в потоків спільна",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(60, 560, 1120, 62,
                    "потік B не зробив нічого дивного і не має способу дізнатися,\n"
                    "що саме зараз його файл вийде відкритим на запис усьому світу",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'race-window.svg'), W, H, *p,
           title="Вікно нульової маски між двома викликами umask")


# ── 5. Ім'я проти дескриптора (вставка proj-exact-mode) ──────────────────────
def fig_name_vs_fd():
    W, H = 1240, 700
    p = []
    LX, LW = 60, 530
    RX, RW = 650, 530

    p.append(fitbox(60, 40, 1120, 54,
                    "точний режим ставлять уже після створення — питання лише, до ЧОГО його прикладають",
                    size=17, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(LX, 116, LW, 60, "chmod(\"vault/key.pem\", 0600)\nза ІМЕНЕМ",
                    size=15, bold=True, fill=RED_FILL, stroke=POS))
    p.append(fitbox(RX, 116, RW, 60, "fchmod(fd, 0600)\nза ДЕСКРИПТОРОМ",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))

    left = [
        "ядро розбирає шлях НАНОВО, у мить виклику",
        "а «vault/key.pem» — уже інший об'єкт:\nміж двома викликами ім'я підмінили посиланням",
        "0600 лягло на чужий inode —\nі ми щойно роздали чужому файлові свої права",
    ]
    right = [
        "розбору шляху немає зовсім",
        "дескриптор тримає сам об'єкт —\nтой inode, який створив саме наш open",
        "0600 лягло рівно туди, куди й мало",
    ]

    y = 210
    for i in range(3):
        h = 84
        p.append(fitbox(LX, y, LW, h, left[i], size=14, fill=BG, stroke=POS))
        p.append(fitbox(RX, y, RW, h, right[i], size=14, fill=BG, stroke=FIELD))
        if i < 2:
            p.append(arrow(LX + LW / 2, y + h + 6, LX + LW / 2, y + h + 34, color=POS))
            p.append(arrow(RX + RW / 2, y + h + 6, RX + RW / 2, y + h + 34, color=FIELD))
        y += 124

    p.append(fitbox(60, 596, 1120, 76,
                    "O_EXCL — друга половина тієї самої гарантії: він каже, що об'єкт створили саме ми,\n"
                    "а не відкрили чужий, який хтось підклав під це ім'я за мить до нас",
                    size=15, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'name-vs-fd.svg'), W, H, *p,
           title="Ім'я проти дескриптора при постановці режиму")


fig_mask_subtraction()
fig_mask_inheritance()
fig_mask_scope()
fig_race_window()
fig_name_vs_fd()
print("ok")
