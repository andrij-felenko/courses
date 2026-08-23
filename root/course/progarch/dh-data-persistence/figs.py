# -*- coding: utf-8 -*-
"""Фігури до кроку «Дані переживають процес»
(root/course/progarch/dh-data-persistence)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")

GREEN_F = "#eafaf1"
AMBER_F = "#fdf3e7"; AMBER_S = "#e08a3c"
RED_F = "#fdecea"


def box_c(cx, cy, w, h, s, **kw):
    return fitbox(cx - w / 2.0, cy - h / 2.0, w, h, s, **kw)


def lifetime_gap():
    """Головна теза: процес живе короткими запусками з розривами на рестартах,
    а дані мусять текти безперервно попід усіма розривами."""
    W, H = 880, 380
    frags = []
    # лейбли доріжок ліворуч
    frags.append(text(78, 126, "процес", size=13, color=MUTED, anchor="end"))
    frags.append(text(78, 281, "дані", size=13, color=MUTED, anchor="end"))
    # доріжка процесу — три окремі запуски з розривами
    frags.append(box_c(195, 120, 170, 52, "запуск 1", size=14))
    frags.append(box_c(455, 120, 170, 52, "запуск 2", size=14))
    frags.append(box_c(715, 120, 170, 52, "запуск 3", size=14))
    # причини рестартів над розривами
    frags.append(text(325, 76, "деплой", size=13, color=POS))
    frags.append(text(585, 76, "збій живлення / краш", size=13, color=POS))
    # пунктирні червоні лінії розривів — від процесу до межі даних
    frags.append(line(325, 150, 325, 248, color=POS, sw=1.6, dash="6 4"))
    frags.append(line(585, 150, 585, 248, color=POS, sw=1.6, dash="6 4"))
    # доріжка даних — одна безперервна зелена смуга попід розривами
    frags.append(box_c(465, 275, 720, 52,
                       "факти дому: пристрої · власник · поріг · лічильник безпеки",
                       size=14, fill=GREEN_F, stroke=FIELD, bold=True))
    frags.append(text(465, 334, "дані живуть безперервно, попри рестарти процесу",
                      size=13, color=MUTED))
    render(os.path.join(IMG, "lifetime-gap.svg"), W, H, *frags)


def durability_gap():
    """«Записав» ≠ «збережено»: між застосунком і тривким диском лежить
    летючий кеш ОС, і саме там краш зжирає нібито записане."""
    W, H = 860, 300
    frags = []
    # ланцюжок запису зліва направо
    frags.append(box_c(130, 150, 150, 66, "застосунок\nsave()", size=14))
    frags.append(arrow(207, 150, 333, 150))
    frags.append(box_c(420, 150, 176, 66, "кеш ОС\n(RAM — летюча)", size=13,
                       fill=AMBER_F, stroke=AMBER_S))
    frags.append(arrow(510, 150, 650, 150))
    frags.append(text(580, 138, "fsync", size=12, color=INK))
    frags.append(box_c(742, 150, 162, 66, "диск / флеш\n(тривка)", size=13,
                       fill=GREEN_F, stroke=FIELD, bold=True))
    # вікно втрати над кешем
    frags.append(text(420, 62, "краш зараз — «записане» зникає", size=13, color=POS))
    frags.append(arrow(420, 74, 420, 114, color=POS))
    # зворотне підтвердження знизу — тривкість істинна лише звідси
    frags.append(arrow(742, 205, 210, 205, color=FIELD))
    frags.append(text(470, 232, "«записано» стає правдою лише після підтвердження з диска",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "durability-gap.svg"), W, H, *frags)


def earns_durable():
    """Тривке сховище — рішення, не дефолт: лише джерела правди, що мусять
    пережити рестарт, дістають місце на диску; похідне й «світове» — перечитуємо."""
    W, H = 880, 400
    frags = []
    # ворота-питання
    frags.append(box_c(440, 56, 400, 58, "мусить пережити рестарт як джерело правди?",
                       size=14, bold=True))
    # дві гілки
    frags.append(text(268, 118, "так", size=14, color=FIELD, bold=True))
    frags.append(text(612, 118, "ні", size=14, color=AMBER_S, bold=True))
    frags.append(arrow(360, 88, 250, 150, color=FIELD))
    frags.append(arrow(520, 88, 630, 150, color=AMBER_S))
    # ліва доріжка — тривке
    frags.append(box_c(225, 172, 320, 42, "→ тривке сховище", size=15,
                       fill=GREEN_F, stroke=FIELD, bold=True))
    for y, lab in [(228, "пристрої й кімнати"), (274, "власник і члени родини"),
                   (320, "поріг опалення"), (366, "лічильник «гріємо N хв»")]:
        frags.append(box_c(225, y, 300, 38, lab, size=13, fill=GREEN_F, stroke=FIELD))
    # права доріжка — перечитати
    frags.append(box_c(650, 172, 340, 42, "→ перечитати зі світу, не зберігати",
                       size=14, fill=AMBER_F, stroke=AMBER_S, bold=True))
    for y, lab in [(228, "поточна температура — з давача"),
                   (274, "«обігрівач увімкнено» — з реле")]:
        frags.append(box_c(650, y, 330, 38, lab, size=13, fill=AMBER_F, stroke=AMBER_S))
    frags.append(text(650, 336, "світ сам тримає цю правду —", size=12, color=MUTED))
    frags.append(text(650, 356, "її не треба дублювати на диск", size=12, color=MUTED))
    render(os.path.join(IMG, "earns-durable.svg"), W, H, *frags)


def atomic_write():
    """Наївний open('w') рве файл на краху (вікно нуля байтів), а атомарний rename
    цей третій стан прибирає конструктивно: у будь-яку мить path = старий XOR новий."""
    W, H = 940, 430
    f = []
    f.append(text(W / 2, 34, "Один запис реєстру на диск — дві стратегії", size=17, bold=True))

    # ── Рядок 1: наївно open('w') ──
    f.append(mtext(90, 110, ["наївно", "open('w')"], size=13, color=MUTED, bold=True))
    f.append(box_c(225, 122, 120, 52, "старий\nфайл ✓", size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(arrow(290, 122, 388, 122))
    f.append(mtext(339, 92, ["open('w')", "→ 0 байтів"], size=11, color=POS))
    f.append(box_c(480, 122, 172, 52, "порожній /\nрваний файл", size=13, fill=RED_F, stroke=POS, bold=True))
    f.append(arrow(570, 122, 668, 122))
    f.append(mtext(619, 96, ["write +", "fsync"], size=11, color=MUTED))
    f.append(box_c(762, 122, 120, 52, "новий\nфайл ✓", size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(text(480, 180, "краш у цьому вікні → ні старого, ні нового: ВТРАЧЕНО ВСЕ", size=13, color=POS, bold=True))

    # роздільник між стратегіями
    f.append(line(50, 216, 890, 216, color=MUTED, sw=1.2, dash="6 5"))

    # ── Рядок 2: атомарно tmp + rename ──
    f.append(mtext(90, 296, ["атомарно", "tmp+rename"], size=13, color=MUTED, bold=True))
    f.append(box_c(220, 308, 150, 52, "старий файл ✓\nнедоторканий", size=12, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(arrow(297, 308, 440, 308))
    f.append(mtext(368, 278, ["пишемо tmp,", "fsync(tmp)"], size=11, color=AMBER_S))
    f.append(box_c(528, 308, 132, 52, "rename\n⚡ атомарно", size=13, fill=FILL, stroke=INK, bold=True))
    f.append(arrow(594, 308, 692, 308))
    f.append(box_c(778, 308, 150, 52, "новий файл ✓", size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(text(W / 2, 374, "у будь-яку мить path = старий АБО новий — третього стану нема", size=13, color=FIELD, bold=True))
    render(os.path.join(IMG, "atomic-write.svg"), W, H, *f)


def two_writers():
    """Двоє писарів у той самий файл читають ту саму базу й пишуть по черзі —
    останній rename затирає попередній (lost update). Ліки — серіалізувати запис."""
    W, H = 900, 450
    f = []
    f.append(text(W / 2, 34, "Гонка двох писарів у той самий файл (lost update)", size=17, bold=True))
    # вісь часу
    f.append(text(66, 76, "час", size=12, color=MUTED))
    f.append(arrow(66, 88, 66, 378, color=MUTED, sw=1.6))
    # заголовки колонок
    f.append(text(258, 80, "автономний цикл", size=14, color=NEG, bold=True))
    f.append(text(654, 80, "CLI (людина)", size=14, color=NEG, bold=True))
    # кроки — зигзаг униз у часі
    f.append(box_c(258, 124, 252, 46, "1. читає файл → {замок}", size=13, fill=FILL, stroke=LINE))
    f.append(box_c(654, 182, 252, 46, "2. читає файл → {замок}", size=13, fill=FILL, stroke=LINE))
    f.append(box_c(258, 250, 276, 46, "3. rename → {замок, темп.=21}", size=12, fill=GREEN_F, stroke=FIELD, bold=True))
    f.append(box_c(654, 308, 276, 46, "4. rename → {замок, лампа}", size=12, fill=GREEN_F, stroke=FIELD, bold=True))
    # червона стрілка-затирання від кроку 3 до кроку 4
    f.append(line(396, 258, 524, 308, color=POS, sw=1.8, dash="6 4"))
    f.append(text(468, 276, "затирає", size=12, color=POS, bold=True))
    # підсумок
    f.append(text(W / 2, 402, "крок 4 перезаписав крок 3: {замок, лампа} — оновлення темп.=21 ЗНИКЛО",
                  size=13, color=POS, bold=True))
    f.append(text(W / 2, 428, "ліки: серіалізувати запис (замок · один писар · черга). SQLite тримає цю чергу сам.",
                  size=12, color=FIELD, bold=True))
    render(os.path.join(IMG, "two-writers.svg"), W, H, *f)


def op_timeline():
    """Вставка hist: вісь часу ідеї ортогональної тривкості —
    1978 (назвали розрив) → 1979 (S-algol) → 1980–83 (PS-algol) → 1995 (три принципи)."""
    W, H = 1000, 300
    frags = []
    xs = [170, 380, 590, 800]
    years = ["1978", "1979", "1980–83", "1995"]
    labels = [
        "VLDB: Аткінсон\nназиває розрив\n«дані vs програма»",
        "S-algol: Моррісон,\nСент-Ендрюс —\nортогональні типи",
        "PS-algol —\nперша реалізована\nтривка мова",
        "три принципи\nортогональної\nтривкості (VLDB J.)",
    ]
    frags.append(line(70, 140, 890, 140, color=MUTED, sw=2))          # спина часу
    frags.append(text(70, 128, "◄ ідея визріває", size=11, color=MUTED, anchor="start"))
    for x, yr, lab in zip(xs, years, labels):
        frags.append(line(x, 112, x, 133, color=MUTED, sw=1.2))       # рік → спина
        frags.append(circle(x, 140, 6, fill=FIELD, stroke=FIELD))     # вузол
        frags.append(line(x, 147, x, 168, color=MUTED, sw=1.2))       # спина → рамка
        frags.append(text(x, 108, yr, size=16, color=INK, bold=True))
        frags.append(box_c(x, 208, 186, 78, lab, size=12, fill=GREEN_F, stroke=FIELD))
    render(os.path.join(IMG, "op-timeline.svg"), W, H, *frags)


def two_answers():
    """Вставка hist: один розрив (неузгодженість імпедансів) — дві відповіді.
    Ліворуч ортогональна тривкість (прибрати межу), праворуч мейнстрім (мости)."""
    W, H = 1000, 440
    frags = []
    LX, RX = 262, 738
    frags.append(box_c(500, 58, 470, 64,
                       "Неузгодженість імпедансів:\nобʼєкти в памʼяті — не рядки в базі",
                       size=14, bold=True))
    frags.append(arrow(430, 92, LX + 40, 133, color=FIELD))
    frags.append(arrow(570, 92, RX - 40, 133, color=AMBER_S))
    # ліва гілка — ортогональна тривкість
    frags.append(box_c(LX, 165, 372, 58, "Ортогональна тривкість:\nприбрати межу — мова сама тривка",
                       size=13, fill=GREEN_F, stroke=FIELD, bold=True))
    frags.append(arrow(LX, 195, LX, 223, color=FIELD))
    frags.append(box_c(LX, 251, 352, 50, "жодного перекладу:\nобʼєкт просто лишається",
                       size=12, fill=GREEN_F, stroke=FIELD))
    frags.append(arrow(LX, 277, LX, 313, color=FIELD))
    frags.append(box_c(LX, 348, 372, 66,
                       "лишилось як ІДЕАЛ:\n«прозора тривкість» у JPA/Hibernate —\nтой самий принцип, здобутий мостом",
                       size=11, fill=GREEN_F, stroke=FIELD))
    # права гілка — мейнстрім
    frags.append(box_c(RX, 165, 372, 58, "Мейнстрім:\nлишити межу, збудувати мости",
                       size=13, fill=AMBER_F, stroke=AMBER_S, bold=True))
    frags.append(arrow(RX, 195, RX, 223, color=AMBER_S))
    frags.append(box_c(RX, 251, 372, 50, "СКБД + серіалізація + ORM\n(переклад обʼєкт ↔ рядок)",
                       size=12, fill=AMBER_F, stroke=AMBER_S))
    frags.append(arrow(RX, 277, RX, 313, color=AMBER_S))
    frags.append(box_c(RX, 348, 372, 66,
                       "ПЕРЕМОГЛО: сховище спільне,\nмовно-нейтральне, з запитами\nй транзакціями для всіх",
                       size=11, fill=AMBER_F, stroke=AMBER_S))
    render(os.path.join(IMG, "two-answers.svg"), W, H, *frags)


if __name__ == "__main__":
    lifetime_gap()
    durability_gap()
    earns_durable()
    atomic_write()
    two_writers()
    op_timeline()
    two_answers()
    print("ok")
