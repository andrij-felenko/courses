# -*- coding: utf-8 -*-
"""Фігури до теми «Монолітне ядро з модулями: вибір Linux»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

ZONE_U = "#eef4fb"   # простір користувача
ZONE_K = "#fdf1ea"   # ядро


def box(cx, cy, s, size=12, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── 1. Де проходить межа привілею ───────────────────────────────────────────
def fig_boundary():
    W, H = 1020, 470
    f = []

    # заголовки панелей
    f.append(text(262, 58, "Монолітне ядро", size=15, bold=True))
    f.append(text(757, 58, "Мікроядро", size=15, bold=True))

    # ── ліва панель ──
    f.append(rect(40, 72, 445, 92, fill=ZONE_U, stroke=MUTED, sw=1.2))
    f.append(text(52, 94, "простір користувача", size=11, color=MUTED, anchor="start"))
    for cx, name in ((114, "bash"), (262, "nginx"), (411, "gcc")):
        f.append(box(cx, 132, name, size=12, min_w=92))
    f.append(line(40, 174, 485, 174, color=POS, sw=3))

    f.append(rect(40, 184, 445, 216, fill=ZONE_K, stroke=MUTED, sw=1.2))
    f.append(text(52, 206, "ядро — один адресний простір", size=11, color=MUTED, anchor="start"))
    grid = [(114, 255, "планувальник"), (262, 255, "керування\nпам'яттю"), (411, 255, "VFS\nі ext4"),
            (114, 335, "драйвер\nдиска"), (262, 335, "мережевий\nстек"), (411, 335, "драйвер\nWi-Fi")]
    for cx, cy, s in grid:
        f.append(box(cx, cy, s, size=12, min_w=118))
    f.append(text(262, 428, "виклик між ними — звичайний виклик функції", size=12, color=MUTED, italic=True))

    # ── права панель ──
    f.append(rect(535, 72, 445, 214, fill=ZONE_U, stroke=MUTED, sw=1.2))
    f.append(text(547, 94, "простір користувача", size=11, color=MUTED, anchor="start"))
    f.append(box(757, 126, "застосунки", size=12, min_w=150))
    for cx, cy, s in ((646, 186, "сервер ФС"), (869, 186, "драйвер диска"),
                      (646, 240, "мережевий сервер"), (869, 240, "драйвер Wi-Fi")):
        f.append(box(cx, cy, s, size=12, min_w=150))
    f.append(text(757, 276, "кожен — окремий адресний простір", size=11, color=MUTED, italic=True))
    f.append(line(535, 296, 980, 296, color=POS, sw=3))

    f.append(rect(535, 306, 445, 94, fill=ZONE_K, stroke=MUTED, sw=1.2))
    f.append(text(547, 328, "мікроядро", size=11, color=MUTED, anchor="start"))
    f.append(box(757, 364, "адресні простори · потоки · повідомлення", size=12))
    f.append(text(757, 428, "виклик між ними — повідомлення крізь ядро", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "boundary.svg"), W, H, *f,
           title="Одна й та сама система, дві різні межі привілею")


# ── 2. Скільки разів один read() перетинає межу ─────────────────────────────
def fig_crossings():
    W, H = 1080, 580
    f = []

    # ліва панель — моноліт
    f.append(text(275, 58, "Монолітне ядро", size=15, bold=True))
    f.append(box(150, 90, "застосунок", size=12, min_w=140, fill=ZONE_U))
    f.append(box(400, 90, "ядро", size=12, min_w=140, fill=ZONE_K))

    f.append(text(275, 132, "1.  read()", size=12))
    f.append(arrow(160, 148, 390, 148))
    f.append(box(400, 212, "VFS → ext4\n→ драйвер диска", size=12, min_w=180, fill=ZONE_K))
    f.append(text(275, 288, "2.  дані назад", size=12))
    f.append(arrow(390, 304, 160, 304))
    f.append(mtext(275, 360, ["між підсистемами ядра", "межу не перетинають жодного разу"],
                   size=12, color=MUTED))

    b, _, _ = textbox(275, 448, "переходів межі: 2", size=16, bold=True, min_w=260, fill="#eaf7ee", stroke=FIELD, sw=2)
    f.append(b)
    f.append(text(275, 520, "решта — прямі виклики функцій", size=12, color=MUTED, italic=True))

    # права панель — мікроядро
    f.append(text(800, 58, "Мікроядро", size=15, bold=True))
    f.append(box(630, 90, "застосунок", size=12, min_w=130, fill=ZONE_U))
    f.append(box(800, 90, "мікроядро", size=12, min_w=130, fill=ZONE_K))
    f.append(box(975, 90, "сервери", size=12, min_w=130, fill=ZONE_U))

    steps = [(630, 800, "1.  read()"),
             (800, 975, "2.  до сервера ФС"),
             (975, 800, "3.  запит блоку"),
             (800, 975, "4.  до драйвера диска"),
             (975, 800, "5.  блок прочитано"),
             (800, 975, "6.  назад у сервер ФС"),
             (975, 800, "7.  готові дані"),
             (800, 630, "8.  дані застосункові")]
    y = 148
    for x1, x2, lab in steps:
        mid = (x1 + x2) / 2.0
        f.append(text(mid, y - 10, lab, size=11))
        dx = 10 if x2 > x1 else -10
        f.append(arrow(x1 + dx, y, x2 - dx, y))
        y += 40

    b, _, _ = textbox(800, 500, "переходів межі: 8", size=16, bold=True, min_w=260, fill="#fdecea", stroke=POS, sw=2)
    f.append(b)
    f.append(text(800, 546, "кожен — перемикання контексту й перевірка прав", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "crossings.svg"), W, H, *f,
           title="Один read() з диска: скільки разів дані перетинають межу привілею")


# ── 3. Що робить завантаження модуля ────────────────────────────────────────
def fig_module_load():
    W, H = 1010, 430
    f = []

    f.append(box(130, 150, "файл .ko\n(ELF-об'єктник)", size=13, min_w=150))
    f.append(box(130, 262, "• код і дані\n• нерозв'язані символи\n• vermagic\n• цифровий підпис",
                 size=11, fill=BG))

    f.append(arrow(206, 150, 274, 150))

    f.append(box(360, 150, "ядро: finit_module", size=13, min_w=170))
    f.append(box(360, 268, "• звірити vermagic\n• перевірити підпис\n• розв'язати символи\n"
                           "• релокувати\n• розмістити в пам'яті ядра", size=11, fill=BG))

    f.append(arrow(452, 150, 592, 150))

    f.append(rect(600, 88, 380, 276, fill=ZONE_K, stroke=MUTED, sw=1.2))
    f.append(text(614, 112, "адресний простір ядра", size=11, color=MUTED, anchor="start"))
    f.append(text(790, 162, "прямі виклики", size=11, color=MUTED))
    f.append(box(688, 190, "ядро", size=13, min_w=90))
    f.append(box(892, 190, "модуль", size=13, min_w=90))
    f.append(arrow(736, 190, 844, 190))
    f.append(mtext(790, 250, ["ті самі привілеї", "та сама пам'ять", "та сама паніка"],
                   size=12, color=INK))
    f.append(text(790, 330, "ізоляції між ними немає", size=13, color=POS, bold=True))

    render(os.path.join(OUT, "module-load.svg"), W, H, *f,
           title="Завантаження модуля — це лінкування, а не ізоляція")


# ── 4. Наслідки одного рішення ──────────────────────────────────────────────
def fig_consequences():
    W, H = 1240, 510
    f = []

    f.append(box(620, 80, "модуль лінкується в ТОЙ САМИЙ адресний простір ядра",
                 size=14, bold=True, fill="#fdecea", stroke=POS, sw=2))

    cols = [
        (170, "немає стабільного\nвнутрішнього ABI",
         ["vermagic: чуже ядро —\nвідмова завантажити",
          "DKMS: перезбирати\nпісля кожного оновлення",
          "надійний шлях —\nвлити драйвер у дерево"]),
        (470, "модуль — похідний\nтвір коду ядра",
         ["MODULE_LICENSE\nі позначка taint «P»",
          "EXPORT_SYMBOL_GPL\nзакритий для закритих",
          "звіт про ваду з tainted-\nядром здебільшого відкидають"]),
        (770, "завантажити модуль =\nвиконати будь-що в ядрі",
         ["CAP_SYS_MODULE —\nце вже повна влада",
          "цифровий підпис модулів\n(CONFIG_MODULE_SIG)",
          "lockdown, коли ввімкнено\nSecure Boot"]),
        (1070, "помилка модуля =\nпаніка всієї системи",
         ["FUSE, vfio, libusb: драйвер\nу просторі користувача",
          "eBPF: верифікатор\nзамість апаратної межі",
          "livepatch: латати ядро\nбез перезавантаження"]),
    ]

    for cx, head, leaves in cols:
        f.append(arrow(620, 102, cx, 158))
        f.append(fitbox(cx - 140, 160, 280, 60, head, size=13, bold=True, fill="#fff6e5", stroke="#c98a00", sw=1.6))
        y = 264
        f.append(arrow(cx, 222, cx, y - 3))
        for lf in leaves:
            f.append(fitbox(cx - 140, y, 280, 56, lf, size=12))
            if y < 400:
                f.append(arrow(cx, y + 56, cx, y + 68))
            y += 70

    render(os.path.join(OUT, "consequences.svg"), W, H, *f,
           title="Що випливає з одного рішення про адресний простір")


# ── 5. Закиди 1992 року й те, як розсудив час (до вставки hist-) ────────────
def fig_verdicts():
    W, H = 1180, 636
    f = []

    f.append(text(310, 70, "Закид, сказаний у січні 1992-го", size=14, bold=True))
    f.append(text(900, 70, "Як розсудив час", size=14, bold=True))

    rows = [
        ("Таненбаум: монолітне ядро 1991 року —\nце крок назад у 1970-ті",
         "Linux лишився монолітним, але навчився\nвантажити модулі: драйвер відокремили,\nне ізолюючи його адресним простором"),
        ("Таненбаум: прив'язка до 80x86 — система\nзастаріє разом із самою архітектурою",
         "Березень 1995, версія 1.2: Alpha, MIPS, SPARC.\nЗакид був слушний — тому його й усунули,\nрозділивши код на спільний і машинний"),
        ("Таненбаум: серед проєктувальників ОС\nмікроядра вже перемогли",
         "Перемогли в нішах: QNX, L4 у радіомодемах,\nseL4 з доведеною коректністю,\nMINIX 3 всередині чипсетів Intel"),
        ("Торвальдс: у MINIX кульгає багатозадачність,\nа Linux уже є — і безкоштовно",
         "Вирішила не будова, а умови поширення:\nMINIX став вільним аж 2000 року,\nколи це вже нічого не міняло"),
    ]

    y = 88
    for left, right in rows:
        f.append(fitbox(40, y, 540, 118, left, size=13, fill="#fdf1ea", stroke=MUTED, sw=1.4))
        f.append(arrow(596, y + 59, 654, y + 59))
        f.append(fitbox(670, y, 470, 118, right, size=13, fill="#eef4fb", stroke=MUTED, sw=1.4))
        y += 134

    render(os.path.join(OUT, "verdicts.svg"), W, H, *f,
           title="Чотири твердження суперечки 1992 року й те, чим вони обернулися")


# ── 6. Шлях модуля і де спрацьовує кожна пастка (вставка proj) ──────────────
def fig_module_path():
    W, H = 1240, 710
    f = []

    f.append(text(165, 78, "крок", size=13, bold=True, color=MUTED))
    f.append(text(525, 78, "що з'являється", size=13, bold=True, color=MUTED))
    f.append(text(980, 78, "що може відмовити", size=13, bold=True, color=MUTED))

    rows = [
        ("hello.c",
         "module_init / module_exit\nMODULE_LICENSE, module_param\npr_info у кільцевий буфер ядра",
         "немає MODULE_LICENSE →\nmodpost зупиняє збирання"),
        ("make (kbuild + modpost)",
         "hello.ko: ELF з нерозв'язаними\nсимволами плюс рядок vermagic;\nModule.symvers з експортами",
         "GPL-only символ у закритому\nмодулі → помилка modpost"),
        ("insmod hello.ko",
         "ядро звіряє vermagic, розв'язує\nсимволи, кладе код у свою пам'ять,\nкличе init-функцію",
         "інше ядро → ENOEXEC,\n«Invalid module format»"),
        ("модуль живий",
         "/proc/modules, /sys/module/hello/,\nrefcnt, holders, parameters, taint",
         "несумісна ліцензія → taint «P»;\nзібраний поза деревом → «O»"),
        ("rmmod hello",
         "ядро кличе exit-функцію\nй звільняє пам'ять модуля",
         "refcnt > 0 → EWOULDBLOCK,\n«Module hello is in use»"),
    ]

    y = 96
    for step, gives, fails in rows:
        f.append(fitbox(40, y, 250, 96, step, size=13, bold=True, fill="#eef4fb", stroke=MUTED, sw=1.4))
        f.append(fitbox(310, y, 430, 96, gives, size=12, fill=FILL, stroke=MUTED, sw=1.4))
        f.append(fitbox(760, y, 440, 96, fails, size=12, fill="#fdecea", stroke=POS, sw=1.4))
        if y < 570:
            f.append(arrow(165, y + 98, 165, y + 118))
        y += 120

    render(os.path.join(OUT, "proj-module-path.svg"), W, H, *f,
           title="Шлях модуля: що додає кожен крок і чим кожен крок відмовляє")


# ── 7. Експорт символу, тримачі й лічильник посилань (вставка proj) ─────────
def fig_module_refcount():
    W, H = 1180, 540
    f = []

    f.append(text(40, 76, "збирання", size=12, color=MUTED, anchor="start"))
    f.append(box(200, 120, "make: hello.ko", size=13))
    f.append(box(590, 120, "Module.symvers\nhello_ping: CRC, ім'я, модуль", size=12))
    f.append(box(960, 120, "make: hello_user.ko\nKBUILD_EXTRA_SYMBOLS", size=12))
    f.append(arrow(268, 120, 488, 120))
    f.append(arrow(692, 120, 876, 120))

    f.append(rect(40, 195, 1100, 200, fill=ZONE_K, stroke=MUTED, sw=1.2))
    f.append(text(56, 218, "адресний простір ядра — жодної межі всередині", size=11,
                 color=MUTED, anchor="start"))
    f.append(box(300, 290, "hello.ko\nEXPORT_SYMBOL(hello_ping)", size=12))
    f.append(box(880, 290, "hello_user.ko\nкличе hello_ping()", size=12))
    f.append(text(600, 268, "прямий виклик функції, без жодної перевірки", size=11, color=MUTED))
    f.append(arrow(796, 290, 402, 290))
    f.append(text(600, 314, "ядро записує посилання: hello.refcnt = 1", size=11, color=POS))
    f.append(text(590, 350, "/sys/module/hello/refcnt → 1", size=12))
    f.append(text(590, 374, "/sys/module/hello/holders/ → hello_user", size=12))

    f.append(box(330, 460, "rmmod hello →\nERROR: Module hello is in use by: hello_user",
                 size=12, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(box(850, 460, "спершу rmmod hello_user, потім rmmod hello\n→ знімаються обидва",
                 size=12, fill="#eaf7ee", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "proj-module-refcount.svg"), W, H, *f,
           title="Один експортований символ — і другий модуль тримає перший")


fig_boundary()
fig_crossings()
fig_module_load()
fig_consequences()
fig_verdicts()
fig_module_path()
fig_module_refcount()
print("ok")
