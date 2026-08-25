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


# ── 1. Де живуть розширені права: сховище «ім'я → значення» при inode ────────
def fig_xattr_store():
    W, H = 1250, 700
    p = []

    p.append(fitbox(50, 45, 1150, 62,
                    "Inode має сталий розмір — тому все, що змінної довжини, "
                    "винесено в окреме сховище пар «ім'я → значення»",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    p.append(fitbox(50, 135, 270, 380,
                    "inode\n\n"
                    "тип об'єкта\n"
                    "дванадцять бітів режиму\n"
                    "uid власника\n"
                    "gid групи\n"
                    "розмір\n"
                    "часові позначки\n"
                    "лічильник посилань\n"
                    "де лежать блоки\n\n"
                    "сталий розмір:\n"
                    "нового поля не додати",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(335, 320, 400, 320, color=MUTED))

    COLS = [(415, 300), (715, 275), (990, 210)]
    p.append(fitbox(415, 135, 785, 52,
                    "розширені атрибути: рядкове ім'я → байти значення, довжина довільна",
                    size=14, fill=WARM_FILL, stroke=WARM, bold=True))

    rows = [
        ("system.posix_acl_access", "список записів ACL цього об'єкта",
         "лише ядро,\nчерез setfacl", GREEN_FILL, FIELD),
        ("system.posix_acl_default", "шаблон прав для майбутніх нащадків",
         "лише ядро,\nчерез setfacl", GREEN_FILL, FIELD),
        ("security.capability", "можливості виконуваного файлу",
         "CAP_SETFCAP", RED_FILL, POS),
        ("security.selinux", "мітка політики обов'язкового контролю",
         "рішення модуля\nбезпеки", RED_FILL, POS),
        ("trusted.mydata", "службові дані поза очима користувача",
         "CAP_SYS_ADMIN", FILL, LINE),
        ("user.mime_type", "будь-що від прикладної програми",
         "звичайне право w\nна сам файл", BLUE_FILL, NEG),
    ]

    y = 200
    RH = 56
    for name, meaning, who, fill, stroke in rows:
        p.append(fitbox(COLS[0][0], y, COLS[0][1], RH, name,
                        size=13, fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(COLS[1][0], y, COLS[1][1], RH, meaning,
                        size=12, fill=BG, stroke=MUTED))
        p.append(fitbox(COLS[2][0], y, COLS[2][1], RH, who,
                        size=12, fill=BG, stroke=MUTED))
        y += RH + 6

    p.append(fitbox(50, 578, 1150, 78,
                    "де ці байти лежать насправді — справа файлової системи: ext4 кладе дрібні "
                    "в запас усередині inode,\nбільші — в один окремий блок, а зовсім великі "
                    "(понад 2048 байтів) — у прихований inode-носій; XFS і Btrfs меж майже не мають",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'xattr-store.svg'), W, H, *p, title="Сховище розширених атрибутів при inode")


# ── 2. Драбина перевірки з ACL: де вмикається маска ──────────────────────────
def fig_acl_ladder():
    W, H = 1200, 900
    p = []

    p.append(fitbox(60, 45, 1080, 62,
                    "Процес просить дію: у нього fsuid, fsgid і повний список додаткових груп. "
                    "Питання йдуть згори вниз",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    QX, QW = 60, 520
    RX, RW = 650, 490
    rows = [
        ("fsuid збігається\nз власником файлу?",
         "запис user:: вирішує остаточно\nмаска НЕ діє", GREEN_FILL, FIELD),
        ("fsuid збігається\nз іменованим записом\nuser:ім'я: ?",
         "цей запис ∩ маска\nвирішує остаточно", WARM_FILL, WARM),
        ("хоч одна група процесу\nзбігається з group::\nчи з group:ім'я: ?",
         "перебираємо ВСІ такі записи:\nдосить, щоб хоч один ∩ маска\nмістив усе потрібне", WARM_FILL, WARM),
        ("не збіглося нічого",
         "запис other:: вирішує\nмаска НЕ діє", BLUE_FILL, NEG),
    ]

    y = 155
    RH, GAP = 96, 34
    centers = []
    for q, r, fill, stroke in rows:
        p.append(fitbox(QX, y, QW, RH, q, size=14, fill=BG, stroke=LINE))
        p.append(arrow(QX + QW + 14, y + RH / 2, RX - 14, y + RH / 2, color=stroke))
        p.append(fitbox(RX, y, RW, RH, r, size=13, fill=fill, stroke=stroke, bold=True))
        centers.append(y + RH)
        y += RH + GAP

    for cy in centers[:-1]:
        p.append(arrow(QX + QW / 2, cy + 6, QX + QW / 2, cy + GAP - 8, color=MUTED))

    p.append(fitbox(60, 675, 1080, 82,
                    "Клас обирається ОДИН раз. Якщо клас групи збігся, але прав не дав, "
                    "до запису other:: черга не переходить —\nце EACCES. Маска стосується лише "
                    "середнього класу: іменованих записів і group::",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(fitbox(60, 780, 1080, 68,
                    "останній щабель той самий, що й без ACL: CAP_DAC_OVERRIDE або "
                    "CAP_DAC_READ_SEARCH обходять усе рішення",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'acl-ladder.svg'), W, H, *p, title="Порядок перевірки за списком контролю доступу")


# ── 3. Успадкування: default ACL каталогу ───────────────────────────────────
def fig_default_acl():
    W, H = 1180, 700
    p = []

    p.append(fitbox(50, 40, 1080, 52,
                    "Каталог може нести ДВА списки: один вирішує доступ до нього самого, "
                    "другий — шаблон для нащадків",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    p.append(fitbox(360, 120, 460, 170,
                    "каталог project/\n\n"
                    "system.posix_acl_access — хто ходить сюди\n"
                    "system.posix_acl_default — що дістанеться\nтому, що тут створять",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    p.append(arrow(520, 300, 330, 395, color=FIELD))
    p.append(arrow(670, 300, 855, 395, color=NEG))

    p.append(text(190, 355, "створюють каталог", size=13, color=FIELD, bold=True))
    p.append(text(1010, 355, "створюють звичайний файл", size=13, color=NEG, bold=True))

    p.append(fitbox(50, 405, 460, 180,
                    "новий підкаталог\n\n"
                    "копію шаблону кладуть ДВІЧІ:\n"
                    "і як власний access ACL,\n"
                    "і як власний default ACL —\n"
                    "тож правило йде вглиб деревом",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(670, 405, 460, 180,
                    "новий файл\n\n"
                    "копію шаблону кладуть ОДИН раз,\n"
                    "як власний access ACL;\n"
                    "другого списку у файлу немає,\n"
                    "бо всередині файлу нічого не створять",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(50, 615, 1080, 62,
                    "поки шаблон є, umask мовчить: межу ставить аргумент mode виклику open чи mkdir, "
                    "перетнутий із класами успадкованого списку",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'default-acl.svg'), W, H, *p, title="Успадкування прав через default ACL")


# ── 4. Байти самого атрибута: заголовок і записи по вісім ────────────────────
def fig_acl_blob_bytes():
    W, H = 1240, 690
    p = []

    p.append(fitbox(50, 38, 1140, 54,
                    "Значення атрибута system.posix_acl_access цілком: "
                    "чотири байти заголовка і далі записи рівно по вісім байтів",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    CX, CW, CSTEP = 60, 44, 50          # клітинка байта
    DX, DW = 490, 330                    # стовпчик «що це значить»
    RX, RW = 850, 340                    # стовпчик «рядок у виводі»

    def cells(y, vals, fills):
        for i, (v, f) in enumerate(zip(vals, fills)):
            p.append(fitbox(CX + i * CSTEP, y, CW, 46, v, size=13,
                            fill=f[0], stroke=f[1], bold=True))

    # заголовок
    HY = 110
    cells(HY, ["02", "00", "00", "00"], [(WARM_FILL, WARM)] * 4)
    p.append(fitbox(DX, HY, DW, 46, "u32 версія = 0x0002",
                    size=13, fill=BG, stroke=MUTED))
    p.append(fitbox(RX, HY, RW, 46, "інше число — EOPNOTSUPP",
                    size=13, fill=BG, stroke=MUTED))

    # підписи полів запису
    LY = 178
    p.append(fitbox(CX, LY, 94, 34, "тег u16", size=12, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(CX + 2 * CSTEP, LY, 94, 34, "права u16", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(CX + 4 * CSTEP, LY, 194, 34, "ідентифікатор u32", size=12, fill=FILL, stroke=LINE))

    FIELDS = [(BLUE_FILL, NEG), (BLUE_FILL, NEG),
              (GREEN_FILL, FIELD), (GREEN_FILL, FIELD),
              (FILL, LINE), (FILL, LINE), (FILL, LINE), (FILL, LINE)]

    rows = [
        (["01", "00", "06", "00", "ff", "ff", "ff", "ff"],
         "тег 1 — власник файлу\nправа 6 = rw-, ідентифікатор не вжито",
         "user::rw-", BG, MUTED),
        (["02", "00", "06", "00", "e9", "03", "00", "00"],
         "тег 2 — іменований користувач\nправа 6 = rw-, uid 1001",
         "user:hanna:rw-   #effective:r--", WARM_FILL, WARM),
        (["04", "00", "04", "00", "ff", "ff", "ff", "ff"],
         "тег 4 — група файлу\nправа 4 = r--",
         "group::r--", BG, MUTED),
        (["10", "00", "04", "00", "ff", "ff", "ff", "ff"],
         "тег 16 — маска\nправа 4 = r--, стеля класу групи",
         "mask::r--", GREEN_FILL, FIELD),
        (["20", "00", "00", "00", "ff", "ff", "ff", "ff"],
         "тег 32 — решта\nправа 0 = ---",
         "other::---", BG, MUTED),
    ]

    y = 232
    RH, GAP = 58, 8
    for vals, meaning, out, fill, stroke in rows:
        cells(y, vals, FIELDS)
        p.append(fitbox(DX, y, DW, RH, meaning, size=12, fill=BG, stroke=MUTED))
        p.append(fitbox(RX, y, RW, RH, out, size=13, fill=fill, stroke=stroke, bold=True))
        y += RH + GAP

    p.append(fitbox(50, 566, 1140, 88,
                    "Разом 4 + 5 × 8 = 44 байти. Числа на носії — завжди little-endian, "
                    "хоч би яка була машина.\nІмені «hanna» в цих байтах немає — є число 1001: "
                    "перейменування користувача списку не зачепить,\nа переїзд файлу туди, "
                    "де 1001 — інша людина, змінить геть усе",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'acl-blob-bytes.svg'), W, H, *p,
           title="Двійковий вигляд списку доступу в розширеному атрибуті")


fig_xattr_store()
fig_acl_ladder()
fig_default_acl()
fig_acl_blob_bytes()
print("ok")
