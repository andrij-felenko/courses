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


# ── 1. Одне обчислення — дві споживачки ─────────────────────────────────────
def fig_two_consumers():
    W, H = 1340, 940
    p = []

    p.append(fitbox(430, 60, 480, 66,
                    "файл іде в діло: запуск, відображення коду, читання",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(670, 126, 670, 172))

    p.append(fitbox(430, 172, 480, 62,
                    "ядро рахує хеш вмісту",
                    size=16, bold=True, fill=FILL, stroke=LINE, sw=2))

    # розгалуження
    p.append(line(670, 234, 670, 268, color=LINE, sw=1.8))
    p.append(line(300, 268, 1040, 268, color=LINE, sw=1.8))
    p.append(arrow(300, 268, 300, 316))
    p.append(arrow(1040, 268, 1040, 316))

    p.append(text(166, 300, "запам'ятати", size=15, bold=True, color=NEG))
    p.append(text(1174, 300, "порівняти", size=15, bold=True, color=POS))

    # ліва гілка: вимірювання
    p.append(rect(60, 316, 480, 500, fill=BLUE_FILL, stroke=NEG, sw=2))
    p.append(text(300, 350, "вимірювання", size=17, bold=True, color=NEG))

    p.append(fitbox(92, 372, 416, 86,
                    "рядок дописано у список:\n"
                    "хеш запису, хеш файлу, підказка з іменем",
                    size=13, fill=BG, stroke=NEG))
    p.append(arrow(300, 458, 300, 496))

    p.append(fitbox(92, 496, 416, 86,
                    "тим самим записом розширено\n"
                    "регістр PCR у чипі TPM",
                    size=13, fill=BG, stroke=NEG))
    p.append(arrow(300, 582, 300, 620))

    p.append(fitbox(92, 620, 416, 100,
                    "назовні йдуть дві речі:\n"
                    "список як текст\n"
                    "і підписаний чипом знімок регістра",
                    size=13, fill=BG, stroke=NEG))
    p.append(arrow(300, 720, 300, 758))

    p.append(fitbox(92, 758, 416, 40,
                    "вирок виносить ЧУЖА сторона",
                    size=14, bold=True, fill=BLUE_FILL, stroke=NEG))

    # права гілка: оцінка
    p.append(rect(800, 316, 480, 500, fill=RED_FILL, stroke=POS, sw=2))
    p.append(text(1040, 350, "оцінка", size=17, bold=True, color=POS))

    p.append(fitbox(832, 372, 416, 86,
                    "еталон беруть із розширеного атрибута\n"
                    "security.ima цього ж inode",
                    size=13, fill=BG, stroke=POS))
    p.append(arrow(1040, 458, 1040, 496))

    p.append(fitbox(832, 496, 416, 86,
                    "усередині або хеш,\n"
                    "або підпис під ключем із кільця .ima",
                    size=13, fill=BG, stroke=POS))
    p.append(arrow(1040, 582, 1040, 620))

    p.append(fitbox(832, 620, 416, 100,
                    "збіглося — відкриття триває;\n"
                    "ні — виклик повертає EACCES,\n"
                    "як звичайна відмова за правами",
                    size=13, fill=BG, stroke=POS))
    p.append(arrow(1040, 720, 1040, 758))

    p.append(fitbox(832, 758, 416, 40,
                    "вирок виносить САМА машина",
                    size=14, bold=True, fill=RED_FILL, stroke=POS))

    p.append(fitbox(60, 852, 1220, 56,
                    "обчислення спільне; розходяться потреби — «дізнатися, що тут було» проти «не пустити чуже»",
                    size=14, fill=WARM_FILL, stroke=WARM))

    return render(os.path.join(IMG, 'two-consumers.svg'), W, H, *p)


# ── 2. Ланцюг розширень PCR ─────────────────────────────────────────────────
def fig_pcr_chain():
    W, H = 1360, 800
    p = []

    p.append(text(680, 40, "регістр рухається лише вперед: PCR ← H(PCR ‖ запис)",
                  size=17, bold=True))

    xs = [90, 405, 720, 1035]
    labels = [
        "PCR = 000…0\nпорожній старт",
        "PCR = H(000…0 ‖ A)\nпісля запису A",
        "PCR = H(попереднє ‖ B)\nпісля запису B",
        "PCR = H(попереднє ‖ C)\nпісля запису C",
    ]
    for i, (x, lab) in enumerate(zip(xs, labels)):
        p.append(fitbox(x, 110, 250, 96, lab, size=13,
                        fill=BLUE_FILL if i else FILL, stroke=NEG if i else LINE))
        if i:
            p.append(arrow(xs[i - 1] + 250, 158, x, 158))

    recs = ["запис A\n/init", "запис B\n/usr/bin/bash", "запис C\n/usr/lib/libc.so"]
    for i, r in enumerate(recs):
        x = xs[i + 1]
        p.append(fitbox(x, 262, 250, 78, r, size=13, fill=GREEN_FILL, stroke=FIELD))
        p.append(arrow(x + 125, 262, x + 125, 212))

    p.append(line(60, 386, 1300, 386, color=MUTED, dash="7,6"))

    # спроба підробки
    p.append(text(680, 430, "спроба прибрати запис B зі списку", size=16, bold=True, color=POS))

    p.append(fitbox(90, 470, 560, 130,
                    "у текстовому списку рядок B стерто:\n"
                    "залишилися лише A і C,\n"
                    "перерахунок дає H(H(000…0 ‖ A) ‖ C)",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(730, 470, 560, 130,
                    "у чипі лежить H(H(H(000…0 ‖ A) ‖ B) ‖ C)\n"
                    "і присвоїти йому інше значення нічим:\n"
                    "операції «відняти запис» не існує",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(370, 600, 500, 646))
    p.append(arrow(1010, 600, 880, 646))

    p.append(fitbox(430, 646, 520, 62,
                    "два числа не збігаються — підробку видно",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(90, 730, 1200, 46,
                    "щоб підсумок збігся, довелося б підібрати прообраз хеша — саме цього криптографічна функція й не дозволяє",
                    size=13, fill=FILL, stroke=LINE))

    return render(os.path.join(IMG, 'pcr-chain.svg'), W, H, *p)


# ── 3. Драбина довіри ───────────────────────────────────────────────────────
def fig_trust_ladder():
    W, H = 1300, 830
    p = []

    p.append(text(650, 40, "кожен щабель тримається на нижчому", size=17, bold=True))

    steps = [
        ("дані файлу", "самі байти, які стануть кодом", GREEN_FILL, FIELD),
        ("security.ima", "хеш або підпис цих байтів", BLUE_FILL, NEG),
        ("security.evm", "HMAC над метаданими inode разом з атрибутами security.*", BLUE_FILL, NEG),
        ("ключ HMAC у ядрі", "довірений ключ, який розпечатує TPM; на диску його немає", WARM_FILL, WARM),
        ("непошкоджене ядро", "саме воно і рахує, і вирішує", WARM_FILL, WARM),
        ("secure boot", "прошивка перевірила підпис кожної ланки завантаження", RED_FILL, POS),
    ]

    y = 96
    for i, (name, note, fill, stroke) in enumerate(steps):
        p.append(fitbox(120, y, 330, 76, name, size=16, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(500, y, 680, 76, note, size=13, fill=BG, stroke=stroke))
        if i:
            p.append(arrow(285, y, 285, y - 42))
        y += 118

    p.append(text(285, 806, "опора", size=13, color=MUTED))
    p.append(text(840, 806, "що саме дає цей щабель", size=13, color=MUTED))

    return render(os.path.join(IMG, 'trust-ladder.svg'), W, H, *p)


# ── 4. Хроніка: від статті 2004-го до вироку в 3.7 ──────────────────────────
def fig_ima_timeline():
    W, H = 1400, 900
    p = []

    rows = [
        ("2004", "стаття USENIX Security: ланцюг вимірювань\nвід BIOS аж у прикладний рівень", GREEN_FILL, FIELD),
        ("травень 2005", "перші латки в списку розсилки ядра — окремим модулем LSM;\nспільнота відмовляє", RED_FILL, "#c0392b"),
        ("червень 2009 · 2.6.30", "вимірювання входить у дерево:\nзібрати хеш, покласти в журнал, розширити PCR", BLUE_FILL, NEG),
        ("січень 2012 · 3.2", "EVM: HMAC над метаданими inode,\nключ бере з кільця ключів ядра", BLUE_FILL, NEG),
        ("березень 2012 · 3.3", "у EVM з'являється підпис —\nеталон переживає перенос на іншу машину", BLUE_FILL, NEG),
        ("грудень 2012 · 3.7", "IMA-appraisal: ядро саме порівнює з еталоном\nі відмовляє у відкритті", WARM_FILL, WARM),
    ]

    y = 70
    for i, (when, what, fill, stroke) in enumerate(rows):
        p.append(fitbox(90, y, 380, 92, when, size=17, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(520, y, 800, 92, what, size=14, fill=BG, stroke=stroke))
        if i:
            p.append(arrow(280, y - 46, 280, y - 4))
        y += 138

    return render(os.path.join(IMG, 'ima-timeline.svg'), W, H, *p)


# ── 5. Розкладка байтів у security.ima і security.evm ──────────────────────
def fig_xattr_layout():
    W, H = 1340, 700
    p = []

    p.append(text(670, 40, "перший байт називає, що лежить далі", size=17, bold=True))

    X0 = 320

    def strip(y, cells):
        x = X0
        for w, label, fill, stroke in cells:
            p.append(fitbox(x, y, w, 74, label, size=13, fill=fill, stroke=stroke))
            x += w

    p.append(text(180, 96, "security.ima", size=16, bold=True, color=NEG))

    p.append(fitbox(40, 118, 260, 74, "тип 0x04\nеталон — хеш", size=13,
                    fill=BLUE_FILL, stroke=NEG))
    strip(118, [(96, "0x04", BLUE_FILL, NEG),
                (128, "алгоритм\n1 байт", FILL, LINE),
                (776, "дайджест вмісту\n32 байти для sha256", BG, LINE)])

    p.append(fitbox(40, 216, 260, 74, "тип 0x03\nеталон — підпис", size=13,
                    fill=BLUE_FILL, stroke=NEG))
    strip(216, [(96, "0x03", BLUE_FILL, NEG),
                (110, "версія\n2", FILL, LINE),
                (128, "алгоритм\n1 байт", FILL, LINE),
                (176, "keyid\n4 байти", FILL, LINE),
                (176, "розмір підпису\n2 байти", FILL, LINE),
                (314, "сам підпис", BG, LINE)])

    p.append(line(40, 330, 1300, 330, color=MUTED, dash="7,6"))

    p.append(text(180, 380, "security.evm", size=16, bold=True, color=WARM))

    p.append(fitbox(40, 402, 260, 74, "тип 0x02\nHMAC на цій машині", size=13,
                    fill=WARM_FILL, stroke=WARM))
    strip(402, [(96, "0x02", WARM_FILL, WARM),
                (904, "HMAC-SHA1 над метаданими inode, 20 байтів", BG, LINE)])

    p.append(fitbox(40, 500, 260, 74, "тип 0x05\nпереносний підпис", size=13,
                    fill=WARM_FILL, stroke=WARM))
    strip(500, [(96, "0x05", WARM_FILL, WARM),
                (110, "версія\n2", FILL, LINE),
                (128, "алгоритм\n1 байт", FILL, LINE),
                (176, "keyid\n4 байти", FILL, LINE),
                (176, "розмір підпису\n2 байти", FILL, LINE),
                (314, "сам підпис", BG, LINE)])

    p.append(fitbox(40, 610, 1260, 60,
                    "форма підпису однакова в обох атрибутах; різне те, над чим його рахують — "
                    "над даними файлу чи над метаданими inode",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    return render(os.path.join(IMG, 'xattr-layout.svg'), W, H, *p)


# ── 6. Розкладка двійкового запису журналу ──────────────────────────────────
def fig_record_layout():
    W, H = 1360, 830
    p = []

    p.append(text(680, 44, "один запис двійкового журналу: що з чого рахують",
                  size=17, bold=True))

    cells = [
        (60, 130, "PCR\n4 байти", FILL, LINE),
        (190, 340, "хеш запису\n20 байтів (SHA-1) або 32 (SHA-256)", BLUE_FILL, NEG),
        (530, 170, "довжина\nімені", FILL, LINE),
        (700, 200, "ім'я шаблону\nima-ng", FILL, LINE),
        (900, 170, "довжина\nданих", FILL, LINE),
        (1070, 230, "дані шаблону", GREEN_FILL, FIELD),
    ]
    for x, w, label, fill, stroke in cells:
        p.append(fitbox(x, 120, w, 90, label, size=13, fill=fill, stroke=stroke))

    # розкриття поля даних
    p.append(line(1070, 210, 120, 330, color=MUTED, dash="6,5"))
    p.append(line(1300, 210, 1300, 330, color=MUTED, dash="6,5"))
    p.append(text(900, 292, "усередині — пари «довжина + поле»", size=13, color=MUTED))

    inner = [
        (120, 150, "4 байти\n40"),
        (270, 430, "«sha256:» з нуль-байтом\n+ 32 байти хеша вмісту"),
        (700, 150, "4 байти\n14"),
        (850, 450, "/usr/bin/bash\nз нуль-байтом у кінці"),
    ]
    for x, w, label in inner:
        p.append(fitbox(x, 330, w, 86, label, size=13, fill=BG, stroke=FIELD))

    p.append(fitbox(60, 450, 1240, 90,
                    "перевірка 1 — запис сам із собою:\n"
                    "хеш над оцими байтами мусить дорівнювати полю «хеш запису»",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(680, 540, 680, 580))

    p.append(fitbox(60, 580, 1240, 90,
                    "перевірка 2 — ланцюг:\n"
                    "PCR ← H(PCR ‖ хеш запису), запис за записом, від нулів",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(680, 670, 680, 710))

    p.append(fitbox(60, 710, 1240, 80,
                    "без першої перевірки збіг ланцюга доводить лише порядок хешів,\n"
                    "а не те, які саме файли за ними стоять",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    return render(os.path.join(IMG, 'record-layout.svg'), W, H, *p)


# ── 7. Що видно з одного знімка регістра ────────────────────────────────────
def fig_replay_verdict():
    W, H = 1400, 840
    p = []

    p.append(text(700, 40, "один знімок регістра з чипа — і що з нього видно",
                  size=17, bold=True))

    p.append(fitbox(350, 76, 700, 70,
                    "перерахунок дає значення регістра після КОЖНОГО запису",
                    size=14, fill=FILL, stroke=LINE))
    p.append(arrow(700, 146, 700, 190))

    p.append(fitbox(350, 190, 700, 70,
                    "чи є знімок із чипа серед цих значень?",
                    size=15, bold=True, fill=WARM_FILL, stroke=WARM))

    p.append(line(700, 260, 700, 300, color=LINE, sw=1.8))
    p.append(line(230, 300, 1170, 300, color=LINE, sw=1.8))
    for cx in (230, 700, 1170):
        p.append(arrow(cx, 300, cx, 344))

    cols = [
        (40, "збіг на останньому", GREEN_FILL, FIELD,
         "усю історію підтверджено чипом:\nсписок справжній до останнього рядка"),
        (510, "збіг раніше", BLUE_FILL, NEG,
         "після знімка дописалися нові рядки;\nдовіряти можна лише частині до місця збігу"),
        (980, "збігу немає", RED_FILL, POS,
         "журнал і чип розійшлися;\nдалі питання одне — де саме"),
    ]
    for x, head, fill, stroke, body in cols:
        p.append(fitbox(x, 344, 380, 60, head, size=15, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(x, 414, 380, 100, body, size=13, fill=BG, stroke=stroke))

    p.append(arrow(1170, 514, 1170, 560))
    p.append(fitbox(980, 560, 380, 110,
                    "якийсь запис не сходиться\nсам із собою —\nось точний рядок",
                    size=13, fill=RED_FILL, stroke=POS))
    p.append(arrow(1170, 670, 1170, 712))
    p.append(fitbox(980, 712, 380, 110,
                    "усі записи цілі — рядок вилучено\nчи переставлено; одного знімка мало,\n"
                    "потрібна попередня контрольна точка",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(40, 610, 850, 110,
                    "збіг не означає «система в порядку»:\n"
                    "він доводить лише, що список справжній.\n"
                    "Чи дозволені в ньому файли — окреме питання до переліку еталонів",
                    size=13, fill=WARM_FILL, stroke=WARM))

    return render(os.path.join(IMG, 'replay-verdict.svg'), W, H, *p)


if __name__ == '__main__':
    fig_two_consumers()
    fig_pcr_chain()
    fig_trust_ladder()
    fig_ima_timeline()
    fig_xattr_layout()
    fig_record_layout()
    fig_replay_verdict()
    print("ok")
