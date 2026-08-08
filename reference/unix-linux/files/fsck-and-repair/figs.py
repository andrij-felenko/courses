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
GRAY_FILL = "#eef1f4"
WARM = "#b8860b"


# ── 1. Надлишковість метаданих: суперечність видно, правда — ні ──────────────
def fig_redundancy():
    W, H = 1180, 780
    p = []

    # твердження
    p.append(fitbox(340, 58, 500, 62,
                    "блок 118340 належить inode 2359297",
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=2))
    p.append(text(590, 152, "це саме твердження записане в чотирьох різних місцях носія",
                  size=14, color=MUTED))

    cells = [
        (50, "карта блоків\ninode 2359297", "первинне", FIELD, GREEN_FILL, False),
        (330, "бітова карта\nвільних блоків", "похідне", NEG, BLUE_FILL, False),
        (610, "поле i_blocks\nу тому ж inode", "похідне", POS, RED_FILL, True),
        (890, "лічильник вільних\nблоків групи", "похідне", NEG, BLUE_FILL, False),
    ]
    for x0, label, tag, color, fill, bad in cells:
        p.append(arrow(590, 178, x0 + 120, 226, color=MUTED, sw=1.4))
        p.append(fitbox(x0, 230, 240, 82, label, size=14, fill=fill,
                        stroke=color, sw=2 if bad else 1.6))
        b, _, _ = textbox(x0 + 120, 350, tag, size=13, bold=True,
                          fill=BG, stroke=color, color=color, sw=1.6, rx=14)
        p.append(b)

    # розбіжність
    p.append(rect(50, 390, 1080, 128, fill=BG, stroke=POS, sw=1.8, rx=10))
    p.append(text(90, 424, "що показала перевірка", size=14, bold=True,
                  color=POS, anchor="start"))
    p.append(fitbox(90, 440, 460, 58,
                    "перерахунок із карти блоків:  8 блоків",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(fitbox(630, 440, 460, 58,
                    "записане в полі i_blocks:  24 блоки",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.6))

    # два наслідки
    p.append(fitbox(50, 580, 520, 132,
                    "коли одна із записок ПОХІДНА —\n"
                    "її не обирають, а будують заново\n"
                    "з первинних і кладуть поверх",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(610, 580, 520, 132,
                    "коли обидві ПЕРВИННІ —\n"
                    "доказів немає в жодної, і ремонт\n"
                    "обирає менш руйнівний варіант",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.8))

    return render(os.path.join(IMG, 'redundancy.svg'), W, H, *p,
                  title="Одне твердження, чотири записи: розбіжність видно, правда — не завжди")


# ── 2. П'ять проходів e2fsck: залежність за даними ──────────────────────────
def fig_passes():
    W, H = 1220, 940
    p = []

    rows = [
        ("Прохід 1 — inode, блоки, розміри",
         "читає всі inode поспіль; для кожного зайнятого обходить\nкарту блоків і ловить неможливі значення",
         "дає: власні бітові карти\nзайнятих блоків та inode"),
        ("Прохід 2 — структура каталогів",
         "перевіряє записи каталогів; номер має вести на inode,\nпозначений зайнятим у карті з проходу 1",
         "дає: скільки разів кожен\nномер згадано в каталогах"),
        ("Прохід 3 — зв'язність каталогів",
         "від кожного каталогу йде вгору за записом «..»;\nгілка, що не дістає кореня, чіпляється до lost+found",
         "дає: перелік каталогів,\nдосяжних від кореня"),
        ("Прохід 4 — лічильники імен",
         "звіряє пораховане на проході 2 з полем st_nlink;\ninode без жодного імені йде до lost+found",
         "дає: виправлені лічильники\nімен у самих inode"),
        ("Прохід 5 — зведені відомості",
         "карти з проходу 1 лягають поверх дискових, лічильники\nвільного місця перераховуються, том стає чистим",
         "дає: узгоджений том,\nякий можна монтувати"),
    ]

    y = 80
    for i, (head, body, gives) in enumerate(rows):
        p.append(rect(50, y, 660, 128, fill=BG, stroke=INK, sw=1.8, rx=10))
        p.append(fitbox(50, y, 660, 40, head, size=15, bold=True,
                        fill=GRAY_FILL, stroke=INK, sw=1.8, rx=10))
        p.append(fitbox(70, y + 52, 620, 62, body, size=13,
                        fill=BG, stroke=MUTED, sw=1.2))
        p.append(arrow(715, y + 64, 765, y + 64, color=MUTED, sw=1.5))
        p.append(fitbox(770, y + 28, 400, 72, gives, size=13,
                        fill=BLUE_FILL, stroke=NEG, sw=1.6))
        if i < len(rows) - 1:
            p.append(arrow(380, y + 128, 380, y + 160, color=INK))
        y += 160

    p.append(text(610, 908,
                  "кожен прохід ставить питання, відповідь на яке лежить у таблиці попереднього",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'passes.svg'), W, H, *p,
                  title="Проходи e2fsck: порядок диктує залежність за даними")


# ── 3. Шлях від увімкнення до перевірки ─────────────────────────────────────
def fig_boot_path():
    W, H = 1400, 780
    p = []

    p.append(fitbox(500, 62, 400, 62,
                    "рядок у fstab: номер проходу ≠ 0",
                    size=15, bold=True, fill=GRAY_FILL, stroke=INK, sw=1.8))
    p.append(arrow(700, 124, 700, 156, color=INK))
    p.append(fitbox(440, 160, 520, 76,
                    "читаємо суперблок: чи розмонтовано чисто,\nчи не стоїть позначка помилки",
                    size=14, fill=WARM_FILL, stroke=WARM, sw=1.8))

    branches = [
        (40, "чисто розмонтовано", GREEN_FILL, FIELD,
         "повної перевірки не буде\nвзагалі — просто монтуємо"),
        (500, "стоїть позначка помилки\nабо задано fsck.mode=force", WARM_FILL, WARM,
         "повна перевірка тому\nв режимі preen"),
        (960, "брудно, але журнал цілий", BLUE_FILL, NEG,
         "ядро докочує журнал\nпід час монтування — секунди"),
    ]
    for x0, head, fill, color, body in branches:
        p.append(arrow(700, 240, x0 + 200, 296, color=color, sw=1.6))
        p.append(rect(x0, 300, 400, 136, fill=BG, stroke=color, sw=1.8, rx=10))
        p.append(fitbox(x0, 300, 400, 52, head, size=14, bold=True,
                        fill=fill, stroke=color, sw=1.8, color=color, rx=10))
        p.append(fitbox(x0 + 20, 364, 360, 58, body, size=13,
                        fill=BG, stroke=MUTED, sw=1.2))

    # наслідки повної перевірки
    p.append(arrow(700, 440, 480, 552, color=WARM, sw=1.6))
    p.append(arrow(700, 440, 940, 552, color=WARM, sw=1.6))
    p.append(fitbox(260, 556, 440, 124,
                    "усе виправилося однозначно\nкод завершення 0 або 1\nтом монтується далі",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(fitbox(720, 556, 440, 124,
                    "потрібне рішення людини\nдо коду домішано четвірку\nаварійна оболонка, «Fix<y>?»",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.8))

    p.append(text(700, 730,
                  "повна перевірка — виняток, який вмикає сама файлова система або адміністратор",
                  size=14, color=MUTED))

    return render(os.path.join(IMG, 'boot-path.svg'), W, H, *p,
                  title="Від завантаження до «Fix<y>?»: хто й чому запускає перевірку")


# ── 4. Код завершення як набір незалежних бітів ──────────────────────────────
def fig_exit_bits():
    W, H = 1300, 620
    p = []

    p.append(text(650, 44, "перевірка повертає одне число — і це сума незалежних ознак",
                  size=15, color=MUTED))
    p.append(fitbox(400, 68, 500, 56, "e2fsck -p /dev/sdb1 ; echo $?   →   5",
                    size=17, bold=True, fill=WARM_FILL, stroke=WARM, sw=2))

    weights = [("128", False), ("64", False), ("32", False), ("16", False),
               ("8", False), ("4", True), ("2", False), ("1", True)]
    cw, gap = 112, 8
    total = len(weights) * cw + (len(weights) - 1) * gap
    x0 = (W - total) / 2
    for i, (w_lbl, on) in enumerate(weights):
        x = x0 + i * (cw + gap)
        p.append(fitbox(x, 172, cw, 66, w_lbl, size=20, bold=True,
                        fill=RED_FILL if on else GRAY_FILL,
                        stroke=POS if on else MUTED, sw=2 if on else 1.4,
                        color=POS if on else MUTED))
        p.append(text(x + cw / 2, 262, "1" if on else "0", size=16,
                      color=POS if on else MUTED, bold=on))

    x_bit4 = x0 + 5 * (cw + gap) + cw / 2
    x_bit1 = x0 + 7 * (cw + gap) + cw / 2

    p.append(fitbox(60, 306, 470, 108,
                    "нулі старших розрядів кажуть не менше:\nперевірка справді відбулася,\nїї не скасовували, програма не збоїла",
                    size=14, fill=GRAY_FILL, stroke=MUTED, sw=1.4))

    p.append(arrow(x_bit4, 278, 720, 302, color=POS, sw=1.6))
    p.append(arrow(x_bit1, 278, 1090, 302, color=POS, sw=1.6))
    p.append(fitbox(570, 306, 300, 108,
                    "4 — лишилися\nневиправлені суперечності",
                    size=14, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(fitbox(940, 306, 300, 108,
                    "1 — частину помилок\nвиправлено на місці",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(text(650, 478,
                  "5 не є окремим кодом: воно означає «щось виправлено» І «щось лишилося»",
                  size=15, bold=True))
    p.append(text(650, 516,
                  "тому код розбирають побітно, а не звіряють на рівність числу",
                  size=14, color=MUTED))
    p.append(fitbox(300, 546, 700, 46,
                    "systemd: біт 2 → перезавантаження кореня · біт 4 → аварійна оболонка",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.6))

    return render(os.path.join(IMG, 'exit-bits.svg'), W, H, *p,
                  title="Код завершення e2fsck як сума незалежних ознак")


# ── 5. Аудит st_nlink: рахуємо записи каталогів, а не файли ─────────────────
def fig_counting():
    W, H = 1300, 770
    p = []

    p.append(text(275, 58, "що читаємо: записи каталогів", size=15, bold=True))
    p.append(text(1045, 58, "з чим звіряємо: поле в inode", size=15, bold=True))

    # праворуч — inode, до яких ведуть згадки
    targets = [
        (92, "поза обходом: батьківський каталог\n"
             "ми його не читали — судити нема про що", GRAY_FILL, MUTED),
        (214, "inode 100 · каталог audit\nполічили 3   ·   st_nlink 3", GREEN_FILL, FIELD),
        (336, "inode 101 · каталог docs\nполічили 2   ·   st_nlink 2", GREEN_FILL, FIELD),
        (458, "inode 102 · файл під двома іменами\nполічили 2   ·   st_nlink 2", BLUE_FILL, NEG),
        (580, "inode 103 · файл data.bin\nполічили 1   ·   st_nlink 1", BLUE_FILL, NEG),
    ]
    for y, label, fill, stroke in targets:
        p.append(fitbox(840, y, 410, 88, label, size=14, fill=fill, stroke=stroke, sw=1.8))

    # ліворуч — усі записи каталогів піддерева, по одному в рядок
    rows = [
        ("…/audit  — запис у батьківському каталозі", 1, GRAY_FILL, MUTED),
        ("audit/.", 1, WARM_FILL, WARM),
        ("audit/..", 0, WARM_FILL, WARM),
        ("audit/docs", 2, BLUE_FILL, NEG),
        ("audit/copy.txt", 3, BLUE_FILL, NEG),
        ("audit/data.bin", 4, BLUE_FILL, NEG),
        ("audit/docs/.", 2, WARM_FILL, WARM),
        ("audit/docs/..", 1, WARM_FILL, WARM),
        ("audit/docs/note.txt", 3, BLUE_FILL, NEG),
    ]
    for i, (label, to, fill, stroke) in enumerate(rows):
        y = 92 + i * 60
        p.append(fitbox(55, y, 440, 44, label, size=14, fill=fill, stroke=stroke, sw=1.6))
        p.append(arrow(503, y + 22, 832, targets[to][0] + 44, color=stroke, sw=1.4))

    p.append(mtext(650, 700,
                   ["у файла стільки згадок, скільки імен;",
                    "у каталогу до них додаються власна «.» і по «..» від кожного підкаталогу"],
                   size=14, color=MUTED))

    return render(os.path.join(IMG, 'counting.svg'), W, H, *p,
                  title="Записи каталогів як одиниця підрахунку, а не файли")


# ── 6. Три межі, за якими обхід за іменами не має права судити ──────────────
def fig_limits():
    W, H = 1300, 690
    p = []

    p.append(text(650, 34, "три випадки, у яких обхід за іменами не має права судити",
                  size=15, bold=True))

    cols = [
        (45, WARM_FILL, WARM,
         "жорстке посилання\nза межами піддерева",
         "inode 102 має два імені:\naudit/docs/note.txt\nі /backup/note.txt",
         "у піддереві audit\nтрапилося одне ім'я",
         "полічили 1, у полі 2.\nПоле праве — неповний обхід.\n"
         "Аудит піддерева доводить\n«щонайменше», а не «рівно»"),
        (480, BLUE_FILL, NEG,
         "межа монтування",
         "у блоці каталогу — номер\nнакритої теки, а stat дає\nкорінь змонтованої системи",
         "d_ino і st_ino на одну назву\nне збігаються → далі не йдемо",
         "два томи — дві нумерації.\nЗшити їх нічим, тож такий\nзапис випадає зі звіту"),
        (915, RED_FILL, POS,
         "inode, на який\nне вказує ніхто",
         "inode 217: st_nlink 1,\nдані цілі, але жоден запис\nкаталогу його не називає",
         "нічого: ми ходимо іменами,\nа імені немає",
         "саме це четвертий прохід\nчіпляє до lost+found —\n"
         "і саме цього наш аудит\nне знайде ніколи"),
    ]
    for x, fill, stroke, title_s, on_disk, seen, verdict in cols:
        cx = x + 170
        p.append(fitbox(x, 62, 340, 58, title_s, size=15, bold=True,
                        fill=fill, stroke=stroke, sw=2, color=stroke))
        p.append(arrow(cx, 126, cx, 152, color=stroke, sw=1.6))
        p.append(fitbox(x, 156, 340, 120, on_disk, size=14,
                        fill=BG, stroke=MUTED, sw=1.6))
        p.append(arrow(cx, 280, cx, 306, color=stroke, sw=1.6))
        p.append(fitbox(x, 310, 340, 110, seen, size=14,
                        fill=GRAY_FILL, stroke=MUTED, sw=1.6))
        p.append(arrow(cx, 424, cx, 450, color=stroke, sw=1.6))
        p.append(fitbox(x, 454, 340, 150, verdict, size=14,
                        fill=fill, stroke=stroke, sw=1.8))

    p.append(mtext(650, 640,
                   ["дві перші межі програма розпізнає й мовчить;",
                    "третя — сліпа пляма, яка не подає жодного знаку"],
                   size=14, color=MUTED))

    return render(os.path.join(IMG, 'limits.svg'), W, H, *p,
                  title="Межі аудиту st_nlink обходом піддерева")


if __name__ == '__main__':
    print(fig_redundancy())
    print(fig_passes())
    print(fig_boot_path())
    print(fig_exit_bits())
    print(fig_counting())
    print(fig_limits())
