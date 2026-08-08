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
GREY_FILL = "#f1f3f5"
WARM = "#b8860b"


# ── 1. Чотири об'єкти шару VFS ──────────────────────────────────────────────
def fig_four_objects():
    W, H = 1200, 800
    p = []

    BX, BW, BH = 60, 450, 120
    AX, AW = 580, 560
    rows = [
        (70, "struct super_block — примірник ФС",
         ["розмір блока, ознака «лише читання»,", "межа розміру файлу, носій"],
         "таблиця s_op", WARM_FILL, WARM,
         ["який примірник якої файлової системи", "живе: від монтування до відмонтування"]),
        (240, "struct inode — сам файл",
         ["тип, права, власник, розмір, часи,", "лічильник імен"],
         "таблиці i_op (об'єкт) та i_fop (заготовка)", GREEN_FILL, FIELD,
         ["який саме файл, байдуже під яким іменем", "живе: доки файл комусь потрібен"]),
        (410, "struct dentry — ім'я в кеші",
         ["каталог + ім'я → inode;", "без inode означає «імені немає»"],
         "таблиця d_op (майже завжди порожня)", BLUE_FILL, NEG,
         ["яке ім'я — і щоб це було швидко", "живе: доки корисно пам'ятати"]),
        (580, "struct file — опис відкритого файлу",
         ["позиція, прапорці, режим доступу,", "пара «монтування + dentry»"],
         "таблиця f_op (копія i_fop)", RED_FILL, POS,
         ["яке саме відкриття цього файлу", "живе: від open до останнього close"]),
    ]

    for y, title, body, tab, fill, stroke, ann in rows:
        p.append(rect(BX, y, BW, BH, fill=fill, stroke=stroke, sw=2, rx=9))
        p.append(text(BX + BW / 2, y + 26, title, size=15, bold=True, color=stroke))
        p.append(line(BX, y + 38, BX + BW, y + 38, color=stroke, sw=1.2))
        p.append(text(BX + 18, y + 62, body[0], size=13, anchor="start"))
        p.append(text(BX + 18, y + 84, body[1], size=13, anchor="start"))
        p.append(text(BX + 18, y + 108, tab, size=13, anchor="start", bold=True, color=stroke))
        p.append(fitbox(AX, y + 20, AW, 80,
                        ["питання: " + ann[0], ann[1]],
                        size=14, fill=GREY_FILL, stroke=MUTED, sw=1.4, color=INK))

    # стрілки знизу вгору між об'єктами
    for lower, upper, lbl in ((240, 70, "лежить у примірнику"),
                              (410, 240, "вказує на inode"),
                              (580, 410, "тримає пару з dentry")):
        cx = BX + 130
        p.append(arrow(cx, lower - 6, cx, upper + BH + 6, color=INK, sw=1.8))
        p.append(text(cx + 16, lower - 24, lbl, size=13, anchor="start", color=MUTED))

    p.append(fitbox(BX, 725, 1080, 56,
                    ["самі структури тримає VFS — вміст таблиць операцій заповнює файлова система"],
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, color=INK))

    render(os.path.join(IMG, 'four-objects.svg'), W, H, *p)


# ── 2. Прохід шляху й перехід межі монтування ───────────────────────────────
def fig_path_walk():
    W, H = 1240, 760
    p = []

    C1X, C1W = 60, 230
    C2X, C2W = 320, 580
    C3X, C3W = 930, 230

    p.append(text(C1X + C1W / 2, 62, "складова шляху", size=15, bold=True, color=MUTED))
    p.append(text(C2X + C2W / 2, 62, "що зробив спільний шар", size=15, bold=True, color=MUTED))
    p.append(text(C3X + C3W / 2, 62, "чинна файлова система", size=15, bold=True, color=MUTED))

    RH = 52

    def row(y, comp, what, fs, fill, stroke):
        p.append(fitbox(C1X, y, C1W, RH, [comp], size=15, bold=True,
                        fill=fill, stroke=stroke, sw=1.8, color=INK))
        p.append(fitbox(C2X, y, C2W, RH, [what], size=14,
                        fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
        p.append(fitbox(C3X, y, C3W, RH, [fs], size=15, bold=True,
                        fill=fill, stroke=stroke, sw=1.8, color=stroke))

    row(90, "/", "влучання в кеш записів каталогу", "ext4", BLUE_FILL, NEG)
    row(154, "boot", "влучання в кеш записів каталогу", "ext4", BLUE_FILL, NEG)
    row(218, "efi", "промах → i_op->lookup ext4 читає свій каталог", "ext4", BLUE_FILL, NEG)

    p.append(fitbox(60, 288, 1100, 62,
                    ["dentry «efi» позначено точкою монтування:",
                     "пара «монтування + dentry» замінюється на корінь vfat"],
                    size=15, bold=True, fill=RED_FILL, stroke=POS, sw=2.2, color=POS))

    row(370, "EFI", "промах → i_op->lookup vfat перебирає 32-байтові записи", "vfat", WARM_FILL, WARM)
    row(434, "BOOT", "промах → i_op->lookup vfat", "vfat", WARM_FILL, WARM)
    row(498, "BOOTX64.EFI", "промах → i_op->lookup vfat", "vfat", WARM_FILL, WARM)

    # завершення відкриття
    steps = ["перевірка прав\nна відкриття", "виділення\nstruct file",
             "f_op ← i_fop,\nвиклик f_op->open", "номер дескриптора\nв таблицю процесу"]
    sx, sw2, gap = 60, 245, 40
    for i, s in enumerate(steps):
        x = sx + i * (sw2 + gap)
        p.append(fitbox(x, 600, sw2, 70, s.split("\n"), size=14,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK))
        if i:
            p.append(arrow(x - gap + 4, 635, x - 6, 635, color=FIELD, sw=1.8))

    p.append(text(620, 700, "далі кожен read() іде коротко: номер → struct file → f_op->read_iter",
                  size=15, bold=True, color=MUTED))

    render(os.path.join(IMG, 'path-walk.svg'), W, H, *p)


# ── 3. Поділ праці ──────────────────────────────────────────────────────────
def fig_division():
    W, H = 1180, 720
    p = []

    LX, LW = 70, 470
    RX, RW = 620, 470

    p.append(text(LX + LW / 2, 62, "спільний шар (VFS)", size=17, bold=True, color=NEG))
    p.append(text(RX + RW / 2, 62, "файлова система", size=17, bold=True, color=WARM))

    left = ["таблиця дескрипторів процесу",
            "розбір шляху й перевірка прав",
            "кеш записів каталогу (dentry)",
            "кеш сторінок і зворотний запис",
            "mmap, splice, випереджувальне читання",
            "дерево монтувань",
            "блокування простору імен"]
    right = ["розкладка на носії",
             "формат каталогу й пошук імені",
             "розподіл вільних блоків",
             "журнал і відновлення після збою",
             "сторінка файлу → блок на носії",
             "власні розширені атрибути"]

    IH, IG, Y0 = 54, 14, 90
    for i, s in enumerate(left):
        p.append(fitbox(LX, Y0 + i * (IH + IG), LW, IH, [s], size=15,
                        fill=BLUE_FILL, stroke=NEG, sw=1.6, color=INK))
    for i, s in enumerate(right):
        p.append(fitbox(RX, Y0 + i * (IH + IG), RW, IH, [s], size=15,
                        fill=WARM_FILL, stroke=WARM, sw=1.6, color=INK))

    p.append(line(580, 86, 580, 552, color=POS, sw=3, dash="9,6"))
    p.append(text(580, 582, "різ проходить просто над inode", size=15, bold=True, color=POS))

    p.append(fitbox(70, 616, 1020, 66,
                    ["generic-реалізації й кеш сторінок належать спільному шарові:",
                     "файлова система їх не пише, а лише під'єднує своїми вказівниками"],
                    size=15, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK))

    render(os.path.join(IMG, 'division-of-labour.svg'), W, H, *p)


fig_four_objects()
fig_path_walk()
fig_division()
print("ok")


# ── 4. Хронологія народження спільного шару (вставка hist) ──────────────────
def fig_vnode_timeline():
    W, H = 1400, 810
    p = []

    p.append(text(700, 46, "Позначка «переказ» — факт із переказів і спогадів, а не з публікації",
                  size=16, color=MUTED, italic=True))

    rows = [
        ("берез. 1984",
         ["Sun береться за NFS: мережева файлова система мусить стояти в дереві",
          "поруч із дисковою й бути невідрізненною від неї · переказ"], BLUE_FILL, NEG),
        ("черв. 1984",
         ["перше ядро SunOS із новими об'єктами: inode розділено на незалежний",
          "від формату vnode і приватну частину файлової системи · переказ"], BLUE_FILL, NEG),
        ("лют. 1985",
         ["Research Unix, 8-ма редакція: file system switch і мережеві імена",
          "вигляду /n/<машина>/<шлях> · дата без первинного джерела"], WARM_FILL, WARM),
        ("1985",
         ["П. Вайнберґер, «The UNIX eighth edition network file system»,",
          "ACM Conference on Computer Science, с. 299–301"], WARM_FILL, WARM),
        ("черв. 1986",
         ["С. Клейман, «Vnodes: An Architecture for Multiple File System Types",
          "in Sun UNIX», USENIX Summer, с. 238–247"], BLUE_FILL, NEG),
        ("1987",
         ["System V Release 3: власний file system switch від AT&T"], WARM_FILL, WARM),
        ("18 жовт. 1988",
         ["оголошено System V Release 4, спільну роботу AT&T і Sun:",
          "інтерфейс VFS від Sun заступає file system switch"], GREEN_FILL, FIELD),
        ("весна 1992",
         ["Linux 0.96: власний шар VFS — спершу Кріс Провенцано,",
          "далі переписав Торвальдс"], RED_FILL, POS),
        ("квіт. 1992",
         ["ext Ремі Кара — перша файлова система Linux, написана",
          "через новий інтерфейс; випущено в складі 0.96c"], RED_FILL, POS),
        ("гілка 2.1",
         ["dentry й кеш записів каталогу стають окремим об'єктом —",
          "такого в задумі 1986 року не було · переказ"], RED_FILL, POS),
    ]

    Y0, STEP, BH = 100, 68, 58
    BX, BW = 300, 1040
    AXIS = 282

    p.append(line(AXIS, Y0 - 6, AXIS, Y0 + (len(rows) - 1) * STEP + BH + 6,
                  color=MUTED, sw=2.5))

    for i, (year, lines, fill, stroke) in enumerate(rows):
        top = Y0 + i * STEP
        p.append(text(262, top + 36, year, size=17, bold=True, color=INK, anchor="end"))
        p.append(circle(AXIS, top + BH / 2, 7, fill=stroke, stroke=stroke, sw=2))
        p.append(fitbox(BX, top, BW, BH, lines, size=16,
                        fill=fill, stroke=stroke, sw=1.6, color=INK))

    render(os.path.join(IMG, 'vnode-timeline.svg'), W, H, *p)


fig_vnode_timeline()


# ── 5. Команда → спільний шар → функція модуля (вставка proj) ───────────────
def fig_tinyfs_flow():
    W, H = 1460, 800
    p = []

    C1X, C1W = 50, 300
    C2X, C2W = 380, 590
    C3X, C3W = 1000, 410

    p.append(text(C1X + C1W / 2, 52, "команда в оболонці", size=16, bold=True, color=MUTED))
    p.append(text(C2X + C2W / 2, 52, "що робить спільний шар", size=16, bold=True, color=MUTED))
    p.append(text(C3X + C3W / 2, 52, "що з цього дістається модулю", size=16, bold=True, color=MUTED))

    rows = [
        ("insmod tinyfs.ko",
         ["ядро виконує module_init"],
         ["register_filesystem(&tiny_fs_type):", "тип з'являється в /proc/filesystems"],
         GREY_FILL, MUTED),
        ("mount -t tinyfs none /mnt/tiny",
         ["створює fs_context, кличе get_tree,", "бере анонімний номер пристрою"],
         ["tiny_init_fs_context → tiny_get_tree", "→ tiny_fill_super → d_make_root"],
         GREEN_FILL, FIELD),
        ("ls /mnt/tiny",
         ["open(O_DIRECTORY), далі getdents64", "потрапляє в iterate_dir()"],
         ["f_op->iterate_shared = tiny_iterate"],
         BLUE_FILL, NEG),
        ("cat /mnt/tiny/status",
         ["розбір шляху: промах у кеші імен", "на складовій «status»"],
         ["i_op->lookup = tiny_lookup"],
         WARM_FILL, WARM),
        ("↳ той самий cat, далі",
         ["відкриття, читання, закриття"],
         ["f_op->open, ->read, ->release =", "tiny_open, tiny_read, tiny_release"],
         WARM_FILL, WARM),
        ("umount /mnt/tiny",
         ["кличе kill_sb і скидає всі inode"],
         ["kill_anon_super — готова функція ядра,", "модуль не пише її сам"],
         RED_FILL, POS),
        ("rmmod tinyfs",
         ["ядро виконує module_exit"],
         ["unregister_filesystem(&tiny_fs_type)"],
         GREY_FILL, MUTED),
    ]

    Y0, RH, GAP = 82, 78, 14
    for i, (cmd, vfs, mod, fill, stroke) in enumerate(rows):
        y = Y0 + i * (RH + GAP)
        p.append(fitbox(C1X, y, C1W, RH, [cmd], size=15, bold=True,
                        fill=fill, stroke=stroke, sw=1.8, color=INK))
        p.append(fitbox(C2X, y, C2W, RH, vfs, size=15,
                        fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
        p.append(fitbox(C3X, y, C3W, RH, mod, size=15,
                        fill=fill, stroke=stroke, sw=1.8, color=INK))
        p.append(arrow(C1X + C1W + 6, y + RH / 2, C2X - 8, y + RH / 2, color=MUTED, sw=1.6))
        p.append(arrow(C2X + C2W + 6, y + RH / 2, C3X - 8, y + RH / 2, color=MUTED, sw=1.6))

    p.append(fitbox(50, 726, 1360, 58,
                    ["жодну з цих функцій ядро не кличе за іменем:",
                     "воно бачить тільки вказівники, покладені модулем у таблиці операцій"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, color=INK))

    render(os.path.join(IMG, 'tinyfs-flow.svg'), W, H, *p)


# ── 6. Що лежить у пам'яті під час читання (вставка proj) ───────────────────
def fig_tinyfs_objects():
    W, H = 1400, 820
    p = []

    p.append(fitbox(60, 60, 380, 110,
                    ["модуль tinyfs.ko",
                     "struct file_system_type tiny_fs_type",
                     "плюс чотири сталі таблиці операцій"],
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, color=INK))
    p.append(arrow(250, 176, 250, 218, color=WARM, sw=2))
    p.append(text(268, 204, "register_filesystem()", size=14, anchor="start", color=WARM))

    p.append(fitbox(60, 224, 700, 96,
                    ["struct super_block  —  виділив і тримає спільний шар",
                     "s_magic 0x54494E59 · s_op → tiny_super_ops · s_maxbytes · власний номер пристрою"],
                    size=15, fill=GREY_FILL, stroke=MUTED, sw=1.8, color=INK))
    p.append(arrow(200, 326, 200, 368, color=MUTED, sw=2))
    p.append(text(218, 354, "s_root", size=14, anchor="start", color=MUTED))

    p.append(fitbox(60, 374, 300, 96,
                    ["struct dentry", "ім'я «/» цього примірника"],
                    size=15, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK))
    p.append(arrow(368, 422, 428, 422, color=NEG, sw=2))
    p.append(fitbox(436, 374, 520, 96,
                    ["struct inode  —  S_IFDIR | 0555, i_ino 1",
                     "i_op → tiny_dir_inode_ops (lookup)",
                     "i_fop → tiny_dir_ops (iterate_shared)"],
                    size=15, fill=BLUE_FILL, stroke=NEG, sw=1.8, color=INK))

    p.append(arrow(200, 476, 200, 528, color=NEG, sw=2))
    p.append(text(218, 512, "d_parent", size=14, anchor="start", color=MUTED))

    p.append(fitbox(60, 534, 300, 96,
                    ["struct dentry", "ім'я «status» у кеші імен"],
                    size=15, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK))
    p.append(arrow(368, 582, 428, 582, color=FIELD, sw=2))
    p.append(fitbox(436, 534, 520, 96,
                    ["struct inode  —  S_IFREG | 0444, i_ino 2",
                     "i_op порожній",
                     "i_fop → tiny_file_ops (open, read, release)"],
                    size=15, fill=GREEN_FILL, stroke=FIELD, sw=1.8, color=INK))

    p.append(arrow(696, 636, 696, 682, color=FIELD, sw=2))
    p.append(text(714, 668, "i_fop копіюється у f_op", size=14, anchor="start", color=MUTED))
    p.append(fitbox(436, 688, 520, 96,
                    ["struct file  —  f_pos, прапорці, f_op = копія i_fop",
                     "private_data вказує на текст, знятий під час open"],
                    size=15, fill=RED_FILL, stroke=POS, sw=1.8, color=INK))
    p.append(arrow(964, 736, 1024, 736, color=POS, sw=2))
    p.append(fitbox(1032, 688, 310, 96,
                    ["буфер kmalloc, 256 Б",
                     "єдина пам'ять, яку модуль", "виділив сам"],
                    size=15, bold=True, fill=RED_FILL, stroke=POS, sw=2, color=INK))

    p.append(fitbox(1000, 224, 342, 400,
                    ["Кольорові рамки — об'єкти, форму",
                     "яких задає спільний шар: модуль",
                     "лише заповнює в них вказівники.",
                     "",
                     "Модуль володіє рівно двома",
                     "речами: своєю структурою типу",
                     "файлової системи й цим буфером",
                     "на 256 байтів."],
                    size=15, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))

    render(os.path.join(IMG, 'tinyfs-objects.svg'), W, H, *p)


fig_tinyfs_flow()
fig_tinyfs_objects()


# ── Чотири значення порожнього вказівника (вставка api) ─────────────────────
def fig_null_pointer_kinds():
    W, H = 1420, 700
    p = []

    LX, LW = 50, 250
    MX, MW = 330, 610
    RX, RW = 970, 400

    p.append(text(LX + LW / 2, 52, "вид порожнього поля", size=16, bold=True, color=MUTED))
    p.append(text(MX + MW / 2, 52, "що робить спільний шар", size=16, bold=True, color=MUTED))
    p.append(text(RX + RW / 2, 52, "приклади полів", size=16, bold=True, color=MUTED))

    rows = [
        ("підстановка",
         ["бере власну типову реалізацію —",
          "ззовні різниці не видно"],
         ["i_op->getattr → generic_fillattr",
          "i_op->permission → generic_permission",
          "f_op->fadvise → generic_fadvise"],
         GREEN_FILL, FIELD),
        ("тиша",
         ["дію просто не виконує;",
          "програма помилки не бачить"],
         ["s_op->write_inode — нікуди не пише",
          "s_op->put_super — нічого не прибирає",
          "a_ops->writepages — не пише ніхто"],
         BLUE_FILL, NEG),
        ("відмова кодом",
         ["виклик доходить до програми",
          "як конкретний номер помилки"],
         ["i_op->link → EPERM",
          "f_op->fsync → EINVAL",
          "s_op->statfs → ENOSYS"],
         RED_FILL, POS),
        ("обов'язкове поле",
         ["перевірки немає — ядро йде",
          "за вказівником; порожньо = хиба"],
         ["i_op->lookup у каталозі",
          "a_ops->dirty_folio у власній таблиці",
          "fs_type->kill_sb та init_fs_context"],
         WARM_FILL, WARM),
    ]

    Y0, STEP, BH = 84, 148, 128
    for i, (kind, mid, right, fill, stroke) in enumerate(rows):
        y = Y0 + i * STEP
        p.append(fitbox(LX, y, LW, BH, [kind], size=18, bold=True,
                        fill=fill, stroke=stroke, sw=2.2, color=stroke))
        p.append(fitbox(MX, y, MW, BH, mid, size=16,
                        fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))
        p.append(fitbox(RX, y, RW, BH, right, size=14,
                        fill=GREY_FILL, stroke=stroke, sw=1.6, color=INK))

    render(os.path.join(IMG, 'null-pointer-kinds.svg'), W, H, *p)


fig_null_pointer_kinds()
