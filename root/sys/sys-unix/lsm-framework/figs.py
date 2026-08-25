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
GREY_FILL = "#eeeeee"


# ── 1. Що відбувається всередині одного виклику гачка ───────────────────────
def fig_hook_call():
    W, H = 1360, 940
    p = []

    p.append(fitbox(70, 60, 520, 66, "код ядра: do_dentry_open()",
                    size=16, bold=True, fill=FILL, stroke=LINE))
    p.append(arrow(330, 126, 330, 176))

    p.append(fitbox(70, 176, 520, 90,
                    "класична перевірка прав\n"
                    "дев'ять бітів, ACL, можливості",
                    size=15, fill=FILL, stroke=LINE))

    # бічна гілка відмови
    p.append(arrow(590, 221, 780, 221, color=POS, sw=2))
    p.append(fitbox(790, 176, 520, 90,
                    "сказала «ні» → повернення з EACCES\n"
                    "гачок нижче не викликають узагалі",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(arrow(330, 266, 330, 316))
    p.append(fitbox(70, 316, 520, 66, "security_file_open(file)",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(330, 382, 330, 436))
    p.append(text(600, 412, "усередині — розгорнутий ланцюг гнізд", size=14, color=MUTED))

    # ланцюг гнізд
    slots = [
        ("гніздо 0", "capability", "0", GREEN_FILL, FIELD, "далі"),
        ("гніздо 1", "landlock",   "0", GREEN_FILL, FIELD, "далі"),
        ("гніздо 2", "apparmor",   "-EACCES", RED_FILL, POS, "стоп"),
        ("гніздо 3", "bpf",        "не питали", GREY_FILL, MUTED, ""),
    ]
    y = 436
    for i, (nm, mod, ret, fill, stroke, tail) in enumerate(slots):
        p.append(fitbox(70, y, 190, 74, nm, size=14, fill=BG, stroke=MUTED))
        p.append(fitbox(268, y, 250, 74, mod, size=16, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(526, y, 230, 74, "повернув " + ret, size=14, fill=fill, stroke=stroke))
        if tail:
            p.append(fitbox(764, y, 150, 74, tail, size=14, bold=True,
                            fill=BG, stroke=stroke, color=stroke))
        if i < len(slots) - 1:
            p.append(arrow(165, y + 74, 165, y + 100, color=MUTED))
        y += 100

    p.append(fitbox(950, 436, 360, 174,
                    "порожнє гніздо — це\n"
                    "не перевірка вказівника,\n"
                    "а вимкнений static_branch:\n"
                    "у машинному коді на місці\n"
                    "виклику стоїть перехід,\n"
                    "який ніколи не спрацьовує",
                    size=13, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(950, 636, 360, 200,
                    "типове значення гачка\n"
                    "file_open — нуль.\n"
                    "перша відповідь, що НЕ\n"
                    "дорівнює типовій, обриває\n"
                    "ланцюг і стає відповіддю\n"
                    "всього гачка",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(330, 836, 330, 864, color=POS, sw=2))
    p.append(fitbox(70, 864, 844, 66,
                    "security_file_open повертає -EACCES; гнізда після другого не опитано ніколи",
                    size=15, bold=True, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'hook-call.svg'), W, H, *p,
           title="Виклик гачка: ланцюг гнізд, який обривається на першій відмові")


# ── 2. Пам'ять модуля на чужому об'єкті ────────────────────────────────────
def fig_object_blob():
    W, H = 1340, 830
    p = []

    p.append(text(340, 62, "що кожен модуль просить на старті", size=16, bold=True))

    asks = [
        ("selinux",  "lbs_inode = 16", "мітка контексту", BLUE_FILL, NEG),
        ("landlock", "lbs_inode = 8",  "посилання на правило", GREEN_FILL, FIELD),
        ("apparmor", "lbs_inode = 0",  "судить за шляхом, на inode не пише", WARM_FILL, WARM),
    ]
    y = 92
    for nm, need, why, fill, stroke in asks:
        p.append(fitbox(70, y, 200, 86, nm, size=16, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(278, y, 190, 86, need, size=14, fill=BG, stroke=MUTED))
        p.append(fitbox(476, y, 320, 86, why, size=13, fill=BG, stroke=MUTED))
        y += 100

    p.append(arrow(430, 396, 430, 452, sw=2))
    p.append(text(700, 430, "каркас додає докупи й роздає зсуви", size=14, color=MUTED))

    p.append(fitbox(70, 452, 726, 74,
                    "blob_sizes.lbs_inode = sizeof(rcu_head) + 16 + 8 = 40 байтів",
                    size=16, bold=True, fill=FILL, stroke=LINE))

    # об'єкт і його блоб
    p.append(fitbox(70, 578, 300, 100, "struct inode\ni_security", size=16, bold=True,
                    fill=BG, stroke=LINE))
    p.append(arrow(370, 628, 452, 628, sw=2))

    p.append(text(880, 566, "одне виділення на весь об'єкт", size=15, bold=True))
    seg = [("службовий\nrcu_head", GREY_FILL, MUTED, 190),
           ("selinux\nзсув 16", BLUE_FILL, NEG, 220),
           ("landlock\nзсув 32", GREEN_FILL, FIELD, 230)]
    x = 452
    for txt, fill, stroke, w in seg:
        p.append(fitbox(x, 588, w, 90, txt, size=14, bold=True, fill=fill, stroke=stroke))
        x += w + 6

    p.append(fitbox(452, 700, 646, 96,
                    "кожен модуль читає свої байти за власним зсувом,\n"
                    "порахованим один раз на завантаженні системи;\n"
                    "сусіда він не бачить і не заважає йому",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(880, 92, 420, 190,
                    "як було до цього\n\n"
                    "поле i_security виділяв і володів ним\n"
                    "сам модуль. другому модулеві\n"
                    "покласти туди своє було нікуди —\n"
                    "звідси й правило «один модуль\n"
                    "на всю машину»",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(880, 302, 420, 170,
                    "полів таких кільканадцять:\n"
                    "cred, file, inode, sock, task,\n"
                    "superblock, key, msg_msg,\n"
                    "perf_event, tun_dev, bdev —\n"
                    "по одному на рід об'єкта,\n"
                    "яким цікавляться модулі",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'object-blob.svg'), W, H, *p,
           title="Байти модуля на об'єкті ядра: як каркас ділить одне поле між усіма")


# ── 3. Хто увімкнеться на завантаженні й у якому порядку ───────────────────
def fig_boot_order():
    W, H = 1380, 860
    p = []

    p.append(text(300, 60, "1. записи, зібрані з образу ядра", size=16, bold=True))
    p.append(fitbox(70, 84, 460, 176,
                    "секція .lsm_info.init\n"
                    "кожен DEFINE_LSM(...) поклав сюди\n"
                    "свій запис на етапі збірки:\n"
                    "ім'я, функція init, потрібні байти,\n"
                    "місце в черзі, прапорці",
                    size=14, fill=FILL, stroke=LINE))

    p.append(arrow(300, 260, 300, 314, sw=2))

    p.append(text(300, 300, "2. порядок задає текстовий рядок", size=16, bold=True, color=MUTED))
    p.append(fitbox(70, 314, 460, 130,
                    "CONFIG_LSM з образу, а якщо в командному\n"
                    "рядку є lsm= — то він, і CONFIG_LSM\n"
                    "не діє взагалі",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(70, 466, 460, 90,
                    "lsm=landlock,yama,integrity,apparmor,selinux,bpf",
                    size=13, bold=True, fill=BG, stroke=NEG))

    p.append(arrow(300, 556, 300, 610, sw=2))
    p.append(fitbox(70, 610, 460, 160,
                    "два місця в черзі не обговорюються:\n\n"
                    "capability — завжди перший\n"
                    "integrity — завжди останній",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    # права колонка: черга і відсів
    p.append(text(950, 60, "3. що з цього справді увімкнеться", size=16, bold=True))
    rows = [
        ("capability", "перший за приписом", GREEN_FILL, FIELD),
        ("landlock",   "увімкнено", GREEN_FILL, FIELD),
        ("yama",       "увімкнено", GREEN_FILL, FIELD),
        ("apparmor",   "перший виключний → взято", GREEN_FILL, FIELD),
        ("selinux",    "виключний уже є → вимкнено", RED_FILL, POS),
        ("bpf",        "увімкнено", GREEN_FILL, FIELD),
        ("integrity",  "останній за приписом", GREEN_FILL, FIELD),
    ]
    y = 84
    for nm, note, fill, stroke in rows:
        p.append(fitbox(700, y, 230, 66, nm, size=15, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(938, y, 370, 66, note, size=13, fill=BG, stroke=stroke))
        y += 78

    p.append(fitbox(700, 640, 608, 96,
                    "виключними оголошені selinux, apparmor і smack:\n"
                    "усі троє претендують на ті самі поверхні назовні —\n"
                    "/proc/self/attr, атрибути security.*, поля аудиту",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(700, 756, 608, 84,
                    "підсумок видно живим:\n"
                    "cat /sys/kernel/security/lsm",
                    size=14, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'boot-order.svg'), W, H, *p,
           title="Від записів у образі до живого списку модулів")


# ── 4. Де сидить BPF-програма відносно ланцюга гнізд ────────────────────────
def fig_bpf_stub():
    W, H = 1280, 880
    p = []

    p.append(fitbox(60, 40, 560, 60, "security_socket_create(family, type, …)",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(340, 100, 340, 138))

    p.append(fitbox(60, 138, 170, 74, "capability\n0 → далі",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(230, 175, 258, 175))
    p.append(fitbox(258, 138, 170, 74, "apparmor\n0 → далі",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(428, 175, 456, 175))
    p.append(fitbox(456, 138, 180, 74, "гніздо bpf",
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(700, 130, 520, 90,
                    "у ланцюзі стоїть не програма, а модуль bpf —\n"
                    "завжди, на всіх 268 гачках",
                    size=13, fill=FILL, stroke=LINE))

    p.append(arrow(546, 212, 546, 258))
    p.append(fitbox(300, 258, 480, 92,
                    "bpf_lsm_socket_create(…)\n{ return 0; }",
                    size=16, bold=True, fill=FILL, stroke=LINE))
    p.append(fitbox(820, 250, 400, 108,
                    "таку заглушку ядро генерує\nна кожен гачок: noinline,\n"
                    "повертає типове значення",
                    size=13, fill=FILL, stroke=LINE))

    p.append(arrow(430, 350, 300, 404))
    p.append(arrow(650, 350, 800, 404))

    p.append(fitbox(60, 404, 440, 116,
                    "нічого не причеплено\n"
                    "статичний ключ вимкнено: заглушка\nкоштує стільки ж, скільки «return 0»",
                    size=14, fill=GREY_FILL, stroke=MUTED))

    p.append(fitbox(640, 404, 580, 116,
                    "програму причеплено\n"
                    "точку входу заглушки залатано трампліном —\n"
                    "тим самим, що обслуговує fentry/fexit",
                    size=14, fill=WARM_FILL, stroke=WARM))

    p.append(arrow(930, 520, 930, 570))
    p.append(fitbox(640, 570, 580, 110,
                    "SEC(\"lsm/socket_create\")\n"
                    "cgroup у мапі, family ≠ AF_UNIX\n→ return -EPERM",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(930, 680, 930, 726))
    p.append(fitbox(640, 726, 580, 96,
                    "−EPERM стає значенням заглушки,\n"
                    "тобто відповіддю гнізда bpf і всього ланцюга",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(fitbox(60, 690, 440, 132,
                    "у програмі, що просила сокет:\n"
                    "socket(AF_INET, SOCK_STREAM, 0) = −1,\n"
                    "errno = EPERM.\n"
                    "AF_UNIX і файли — без змін",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'bpf-stub.svg'), W, H, *p,
           title="Програма замінює тіло заглушки, а не гніздо в ланцюзі")


fig_hook_call()
fig_object_blob()
fig_boot_order()
fig_bpf_stub()
print("ok")
