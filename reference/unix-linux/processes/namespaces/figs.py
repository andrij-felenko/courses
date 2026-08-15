# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT = "#fbfcff"


# ── 1. Ім'я → об'єкт: та сама таблиця, але примірників кілька ─────────────────
def fig_name_to_object():
    W, H = 1020, 600
    p = []

    def half(x0, head, accent, fill, rows, note):
        out = [fitbox(x0, 56, 440, 34, head, size=13, fill=fill,
                      stroke=accent, sw=1.8, color=accent, bold=True)]
        out.append(fitbox(x0 + 110, 108, 220, 44, "задача", size=13,
                          fill=SOFT, stroke=accent, sw=1.6, color=INK, bold=True))
        out.append(arrow(x0 + 220, 154, x0 + 220, 176, color=accent, sw=1.6))
        out.append(fitbox(x0 + 110, 178, 220, 40, "nsproxy", size=12,
                          fill="#ffffff", stroke=accent, sw=1.4, color=MUTED))
        out.append(arrow(x0 + 220, 220, x0 + 220, 242, color=accent, sw=1.6))

        y = 244
        out.append(fitbox(x0, y, 440, 32, "таблиця імен цього простору", size=12,
                          fill=fill, stroke=accent, sw=1.4, color=accent, bold=True))
        y += 36
        for r in rows:
            out.append(fitbox(x0 + 14, y, 412, 40, r, size=12,
                              fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
            y += 46
        out.append(fitbox(x0, y + 6, 440, 46, note, size=11,
                          fill=SOFT, stroke=MUTED, sw=1.2, color=MUTED))
        return "".join(out)

    p.append(half(40, "Процес поза контейнером", NEG, "#eaf0fd",
                  ["4711  →  задача веб-сервера",
                   "/var/lib/db  →  цей набір даних",
                   "eth0  →  цей мережевий пристрій"],
                  "має ім'я для кожного з трьох об'єктів\nі може назвати будь-який із них"))

    p.append(half(540, "Процес у власних просторах", FIELD, "#eafaf0",
                  ["1  →  задача веб-сервера",
                   "(немає імені)",
                   "(немає імені)"],
                  "два об'єкти для нього не заборонені —\nвони просто безіменні: kill дасть ESRCH"))

    p.append(line(510, 56, 510, 500, color="#d7dbe0", sw=1.4, dash="6 6"))

    p.append(fitbox(40, 512, 940, 56,
                    "об'єкти ядра ті самі й лежать в одній пам'яті — задача, дерево монтувань, мережевий пристрій",
                    size=12, fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, H - 14,
                  "змінюється не доступ до об'єктів, а таблиця, через яку до них дістаються",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "name-to-object.svg"), W, H, *p,
           title="Простір імен — це примірник відображення «ім'я → об'єкт»")


# ── 2. Один процес — кілька номерів у вкладених просторах ────────────────────
def fig_pid_translation():
    W, H = 1000, 480
    p = []

    cols = [
        (310, "початковий простір\n(уся система)", NEG, "#eaf0fd"),
        (530, "простір контейнера\n(нащадок)", PURPLE, "#f5f0fb"),
        (750, "вкладений простір\n(нащадок контейнера)", FIELD, "#eafaf0"),
    ]

    p.append(fitbox(40, 64, 250, 54, "та сама задача в ядрі", size=12,
                    fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))
    for x, head, accent, fill in cols:
        p.append(fitbox(x, 64, 210, 54, head, size=11, fill=fill,
                        stroke=accent, sw=1.6, color=accent, bold=True))

    rows = [
        ("менеджер контейнерів", ["4711", "немає імені", "немає імені"]),
        ("головний процес контейнера", ["4712", "1", "немає імені"]),
        ("процес у вкладеному просторі", ["4713", "37", "1"]),
    ]

    y = 134
    for label, nums in rows:
        p.append(fitbox(40, y, 250, 64, label, size=12, fill=SOFT,
                        stroke=MUTED, sw=1.4, color=INK))
        for (x, _h, accent, fill), n in zip(cols, nums):
            known = n != "немає імені"
            p.append(fitbox(x, y, 210, 64, n, size=15 if known else 11,
                            fill=fill if known else "#f4f6f8",
                            stroke=accent if known else MUTED,
                            sw=1.6 if known else 1.1,
                            color=accent if known else MUTED,
                            bold=known))
        y += 72

    p.append(fitbox(40, y + 8, 920, 56,
                    "видимість несиметрична: предок має ім'я для кожного нащадка, нащадок про предка не знає нічого",
                    size=12, fill="#ffffff", stroke=INK, sw=1.6, color=INK))

    p.append(text(W / 2, H - 14,
                  "getpid() повертає число, перекладене в простір того, хто питає; глибина вкладеності — до 32 рівнів",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pid-translation.svg"), W, H, *p,
           title="Номер процесу залежить від того, хто дивиться")


# ── 3. Відображення ідентифікаторів у просторі користувачів ──────────────────
def fig_uid_map():
    W, H = 1000, 490
    p = []

    LX, RX, CW = 80, 600, 320

    p.append(fitbox(LX, 62, CW, 40, "усередині простору", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(fitbox(RX, 62, CW, 40, "у просторі-предку", size=13,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))

    pairs = [
        ("0\nroot цього простору", "100000\nзвичайне число без прав"),
        ("1000\nзвичайний користувач", "101000\nтеж без жодних прав"),
        ("65535\nверхнє число діапазону", "165535\nверхнє число діапазону"),
    ]

    y = 124
    for left, right in pairs:
        p.append(fitbox(LX, y, CW, 66, left, size=12, fill=SOFT,
                        stroke=FIELD, sw=1.5, color=INK))
        p.append(fitbox(RX, y, CW, 66, right, size=12, fill=SOFT,
                        stroke=NEG, sw=1.5, color=INK))
        p.append(arrow(LX + CW + 16, y + 33, RX - 16, y + 33, color=MUTED, sw=1.6))
        y += 78

    p.append(fitbox(LX, y + 10, CW + 200 + CW, 54,
                    "/proc/<pid>/uid_map:      0   100000   65536",
                    size=14, fill="#ffffff", stroke=INK, sw=1.6, color=INK, bold=True))

    p.append(text(W / 2, H - 40,
                  "три числа рядка: початок усередині · початок у предка · довжина діапазону",
                  size=12, color=INK))
    p.append(text(W / 2, H - 14,
                  "усі повноваження всередині діють лише щодо об'єктів цього простору; назовні ядро переводить число назад",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "uid-map.svg"), W, H, *p,
           title="Root усередині простору — звичайний користувач зовні")


# ── 4. Що утримує простір живим ──────────────────────────────────────────────
def fig_ns_lifetime():
    W, H = 1010, 540
    p = []

    p.append(fitbox(40, 150, 300, 200,
                    "простір імен\n\nструктура ядра\nз лічильником посилань",
                    size=14, fill="#eafaf0", stroke=FIELD, sw=2.2, color=INK, bold=True))

    holders = [
        "задачі, що зараз у ньому перебувають",
        "відкритий дескриптор на /proc/<pid>/ns/<тип>",
        "прив'язне монтування цього файлу — так робить ip netns",
        "вкладений простір: для номерів і для користувачів",
        "простір користувачів, що володіє цим простором",
    ]

    RAIL = 392
    BX, BW, BH, GAP = 452, 518, 56, 10
    y0 = 64
    centers = []
    for i, h in enumerate(holders):
        y = y0 + i * (BH + GAP)
        cy = y + BH / 2
        centers.append(cy)
        p.append(fitbox(BX, y, BW, BH, h, size=12, fill=SOFT,
                        stroke=NEG, sw=1.5, color=INK))
        p.append(line(BX - 14, cy, RAIL, cy, color=NEG, sw=1.5))

    p.append(line(RAIL, centers[0], RAIL, centers[-1], color=NEG, sw=2))
    p.append(arrow(RAIL, 250, 352, 250, color=NEG, sw=2))

    p.append(fitbox(40, 406, 930, 60,
                    "поки живе хоч одне посилання — простір цілий; коли впало останнє — ядро його прибирає",
                    size=13, fill="#ffffff", stroke=INK, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, H - 40,
                  "простір без жодного процесу — нормальний робочий стан, а не витік",
                  size=12, color=INK))
    p.append(text(W / 2, H - 14,
                  "порівняти два простори можна лише за номером вузла в readlink /proc/<pid>/ns/<тип>",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "ns-lifetime.svg"), W, H, *p,
           title="Що утримує простір імен живим")


# ── 5. Хронологія: типи входили поодинці, кожен під власним тиском ───────────
def fig_ns_timeline():
    rows = [
        ("2.4.19\nсерпень 2002", "монтування", NEG,
         "Alexander Viro — перенесення ідеї Plan 9; прапорець назвали просто CLONE_NEWNS"),
        ("2.6.19\nлистопад 2006", "UTS · IPC", NEG,
         "Serge Hallyn, Cédric Le Goater (IBM) · Kirill Korotaev, Pavel Emelyanov (OpenVZ)"),
        ("2.6.24\nсічень 2008", "номери процесів", PURPLE,
         "перший тип, де ім'я перекладається; звідси вся семантика процесу номер 1"),
        ("2.6.29\nберезень 2009", "мережа (завершено)", PURPLE,
         "Eric Biederman, Daniel Lezcano, Pavel Emelyanov — переробка всього стека, шість випусків"),
        ("3.0\nлипень 2011", "setns() і /proc/<pid>/ns", FIELD,
         "простір дістав ручку: у нього стало можливо ввійти, а не лише народитися в ньому"),
        ("3.8\nлютий 2013", "користувачі", PURPLE,
         "Eric Biederman; шість років від порожньої заготовки — типи kuid_t/kgid_t по всьому дереву"),
        ("4.6\nтравень 2016", "cgroup", FIELD,
         "Aditya Kali (Google) — щоб контейнер не бачив, у якій точці ієрархії він насправді сидить"),
        ("5.6\nберезень 2020", "час", FIELD,
         "Andrei Vagin, Dmitry Safonov — не заради ізоляції, а заради перенесення живих процесів"),
    ]

    W = 1060
    RH, GAP = 62, 10
    top = 74
    H = top + len(rows) * (RH + GAP) + 96
    p = []

    p.append(fitbox(40, 24, 200, 38, "версія ядра", size=12, fill="#eceff2",
                    stroke=INK, sw=1.4, color=INK, bold=True))
    p.append(fitbox(256, 24, 230, 38, "що ввійшло", size=12, fill="#eceff2",
                    stroke=INK, sw=1.4, color=INK, bold=True))
    p.append(fitbox(502, 24, 518, 38, "хто і під яким тиском", size=12,
                    fill="#eceff2", stroke=INK, sw=1.4, color=INK, bold=True))

    y = top
    for ver, what, accent, who in rows:
        p.append(fitbox(40, y, 200, RH, ver, size=12, fill=SOFT,
                        stroke=MUTED, sw=1.3, color=INK, bold=True))
        p.append(fitbox(256, y, 230, RH, what, size=13, fill="#ffffff",
                        stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(502, y, 518, RH, who, size=11, fill="#ffffff",
                        stroke=MUTED, sw=1.2, color=INK))
        y += RH + GAP

    p.append(fitbox(40, y + 8, 980, 46,
                    "об'єкта «контейнер» у ядрі так і не з'явилося — кожен розріз мусив бути корисним сам по собі",
                    size=13, fill="#ffffff", stroke=INK, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, H - 14,
                  "вісімнадцять років між першим і останнім типом; спільного плану не було в жодну мить",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "ns-timeline.svg"), W, H, *p,
           title="Простори імен входили в ядро поодинці, з 2002 по 2020 рік")


# ── 6. Хто опиняється в новому просторі: три виклики ─────────────────────────
def fig_who_enters():
    W = 1060
    RH, GAP = 96, 12
    top = 116
    p = []

    cols = [(40, 200, "виклик"),
            (256, 250, "що робить"),
            (522, 250, "шість звичайних типів"),
            (788, 232, "номери процесів і час")]

    for x, w, head in cols:
        p.append(fitbox(x, 40, w, 56, head, size=12, fill="#eceff2",
                        stroke=INK, sw=1.4, color=INK, bold=True))

    rows = [
        ("clone3()\nclone()", NEG, "створює новий простір",
         "дитина народжується вже в ньому;\nтой, хто кликав, лишається де був",
         "так само — дитина в новому,\nбатько в старому"),
        ("unshare()", PURPLE, "створює новий простір",
         "викликач переходить у новий\nтієї ж миті",
         "викликач лишається в старому;\nу новий потраплять лише\nйого майбутні діти"),
        ("setns()", FIELD, "приєднує до наявного\nза дескриптором",
         "викликач входить сам",
         "викликач лишається в старому;\nувійдуть лише\nйого майбутні діти"),
    ]

    y = top
    for call, accent, what, common, special in rows:
        p.append(fitbox(cols[0][0], y, cols[0][1], RH, call, size=13,
                        fill="#ffffff", stroke=accent, sw=1.9, color=accent, bold=True))
        p.append(fitbox(cols[1][0], y, cols[1][1], RH, what, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(cols[2][0], y, cols[2][1], RH, common, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(cols[3][0], y, cols[3][1], RH, special, size=11,
                        fill="#f5f0fb", stroke=PURPLE, sw=1.4, color=INK))
        y += RH + GAP

    p.append(fitbox(40, y + 10, 980, 62,
                    "членство в просторі номерів і в просторі часу фіксується в мить створення задачі —\n"
                    "тому для себе його не змінює жоден із трьох викликів",
                    size=13, fill="#ffffff", stroke=INK, sw=1.8, color=INK, bold=True))

    H = y + 10 + 62 + 40
    p.append(text(W / 2, H - 14,
                  "решта шести типів такого обмеження не має: там перехід відбувається одразу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "who-enters.svg"), W, H, *p,
           title="Хто саме опиняється в новому просторі імен")


# ── 7. Дві ручки на простір номерів після unshare ────────────────────────────
def fig_pid_for_children():
    W, H = 1010, 430
    p = []

    p.append(fitbox(40, 140, 240, 116,
                    "процес,\nщо зробив\nunshare(CLONE_NEWPID)",
                    size=13, fill=SOFT, stroke=INK, sw=1.8, color=INK, bold=True))

    rows = [
        (78, "/proc/self/ns/pid\npid:[4026531836]", NEG,
         "старий простір номерів —\nмій, і змінити його вже не можна"),
        (234, "/proc/self/ns/pid_for_children\npid:[4026532567]", FIELD,
         "новий простір номерів —\nу ньому народяться діти"),
    ]

    for y, handle, accent, target in rows:
        cy = y + 58
        p.append(arrow(288, cy, 336, cy, color=accent, sw=1.8))
        p.append(fitbox(342, y, 320, 116, handle, size=12,
                        fill="#ffffff", stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(arrow(670, cy, 714, cy, color=accent, sw=1.8))
        p.append(fitbox(720, y, 250, 116, target, size=11,
                        fill=SOFT, stroke=accent, sw=1.4, color=INK))

    p.append(text(W / 2, H - 40,
                  "два різні номери вузла в одного процесу — це нормальний стан, а не збій",
                  size=12, color=INK))
    p.append(text(W / 2, H - 14,
                  "так само влаштована пара time / time_for_children у просторі часу",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pid-for-children.svg"), W, H, *p,
           title="Після unshare у процесу дві ручки на простір номерів")


# ── 6. Порядок кроків збірки контейнера вручну (вставка proj) ────────────────
def fig_container_order():
    W = 1080
    LX, RX, CW = 40, 580, 460
    RH, GAP = 60, 10
    top = 112
    rows = [
        ("L", "clone(дитина, стек, прапорці | SIGCHLD)\nдитина народжується вже у власних просторах"),
        ("R", "read(канал) — чекає\nдо мапи вона «nobody» 65534, зміна ідентифікаторів не працює"),
        ("L", "у setgroups пишемо deny\nінакше ядро не прийме мапу груп"),
        ("L", "uid_map ← «0 1000 1» · gid_map ← «0 1000 1»\nодин рядок — усе, що дозволено без прав"),
        ("S", "батько пише в канал один байт — дитина прокидається вже з мапою"),
        ("R", "sethostname(\"box\")\nвласний рядок у просторі UTS"),
        ("R", "mount(NULL, \"/\", MS_REC | MS_PRIVATE)\nвідв'язати свіжу копію дерева від поширення"),
        ("R", "mount(rootfs, rootfs, MS_BIND | MS_REC)\npivot_root вимагає, щоб новий корінь був точкою монтування"),
        ("R", "mount(\"proc\", \"proc\", \"proc\")\nсвіжий примірник procfs — під новий простір номерів"),
        ("R", "pivot_root(\".\", \".\") · umount2(\".\", MNT_DETACH)\nстарий корінь знято зі стосу — назад дороги немає"),
        ("R", "execve(\"/bin/sh\")\nдитина стає програмою контейнера й лишається PID 1"),
        ("L", "waitpid(pid) → код виходу\nсмерть PID 1 забирає весь простір номерів"),
    ]
    H = top + len(rows) * (RH + GAP) + 66
    p = []

    p.append(fitbox(LX, 56, CW, 42, "батько — звичайний користувач, uid 1000", size=13,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(RX, 56, CW, 42, "дитина — root у власних просторах", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    y = top
    for lane, txt in rows:
        if lane == "L":
            p.append(fitbox(LX, y, CW, RH, txt, size=12, fill=SOFT, stroke=NEG, sw=1.4, color=INK))
        elif lane == "R":
            p.append(fitbox(RX, y, CW, RH, txt, size=12, fill=SOFT, stroke=FIELD, sw=1.4, color=INK))
        else:
            p.append(fitbox(LX, y, RX + CW - LX, RH, txt, size=13, fill="#fdecea",
                            stroke=POS, sw=1.7, color=POS, bold=True))
        y += RH + GAP

    p.append(text(W / 2, H - 20,
                  "переставити рядки не можна: мапа — до першої дії від імені root, приватність — до всіх монтувань, "
                  "прив'язка — до pivot_root",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "container-order.svg"), W, H, *p,
           title="Дванадцять кроків: кожен можливий лише після попереднього")


# ── 7. Чому pivot_root(\".\", \".\") працює ──────────────────────────────────
def fig_pivot_root_stack():
    W, H = 1060, 470
    p = []

    def panel(x, head, accent, fill, boxes, note):
        out = [fitbox(x, 56, 300, 44, head, size=12, fill=fill,
                      stroke=accent, sw=1.8, color=accent, bold=True)]
        y = 118
        for label, bfill, bstroke, bcolor, dash_hint in boxes:
            out.append(fitbox(x, y, 300, 66, label, size=11, fill=bfill,
                              stroke=bstroke, sw=1.5 if not dash_hint else 1.2, color=bcolor))
            y += 76
        out.append(fitbox(x, 326, 300, 84, note, size=11, fill="#ffffff",
                          stroke=MUTED, sw=1.2, color=INK))
        return "".join(out)

    p.append(panel(40, "1 · перед викликом", NEG, "#eaf0fd",
                   [("корінь процесу — дерево хоста", "#ffffff", NEG, INK, False),
                    ("rootfs, прив'язаний сам на себе:\nтепер це точка монтування", SOFT, NEG, INK, False)],
                   "cwd переведено в rootfs;\nхост-корінь досяжний звичайним шляхом"))

    p.append(panel(380, "2 · pivot_root(\".\", \".\")", PURPLE, "#f5f0fb",
                   [("старий корінь — покладений зверху\nв ту саму точку", "#f5f0fb", PURPLE, INK, False),
                    ("rootfs — тепер це «/»", SOFT, PURPLE, INK, False)],
                   "корінь і cwd показують на новий корінь,\nстарий лежить стосом поверх нього"))

    p.append(panel(720, "3 · umount2(\".\", MNT_DETACH)", FIELD, "#eafaf0",
                   [("старий корінь від'єднано —\nіменувати його вже нічим", "#f4f6f8", MUTED, MUTED, True),
                    ("rootfs — єдиний корінь", "#eafaf0", FIELD, INK, False)],
                   "«.» розкривається з нового кореня\nвгору по стосу — знімається саме старий"))

    p.append(text(W / 2, H - 40,
                  "put_old збігається з new_root — тому окремий каталог під старий корінь усередині образу не потрібен",
                  size=12, color=INK))
    p.append(text(W / 2, H - 14,
                  "chroot так не вміє: він міняє точку відліку шляху, а не дерево, і старий корінь лишається на місці",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pivot-root-stack.svg"), W, H, *p,
           title="Підміна кореня без тимчасового каталогу")


if __name__ == "__main__":
    fig_container_order()
    fig_pivot_root_stack()
    fig_ns_timeline()
    fig_name_to_object()
    fig_pid_translation()
    fig_uid_map()
    fig_ns_lifetime()
    fig_who_enters()
    fig_pid_for_children()
    print("OK: figures written to", OUT)
