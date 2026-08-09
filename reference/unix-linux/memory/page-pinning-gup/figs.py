# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Чотири способи, якими кадр тікає з-під пристрою ───────────────────────
def fig_frame_escapes():
    W, H = 1360, 600
    p = []

    cols = [
        (195, "Витіснення", NEG, COOL,
         "рідко вживану сторінку\nядро пише у своп\nі забирає кадр",
         "наступне звертання\nповерне вміст —\nможливо, в інший кадр",
         "старий номер кадру,\nа під ним уже\nчужі дані"),
        (480, "Ущільнення", FIELD, GREENF,
         "вміст переносять\nв інший кадр, щоб\nзібрати суцільний блок",
         "запис таблиці правлять\nтієї ж миті: адреса\nлишається чинною",
         "старий номер кадру,\nа даних там\nбільше немає"),
        (765, "Копіювання при записі", POS, WARM,
         "після fork перший же\nзапис розщеплює\nсторінку на дві",
         "хто пише, той дістає\nсвіжий кадр і жодної\nрізниці не бачить",
         "старий кадр, який\nдістався другому\nпроцесові"),
        (1050, "Звільнення", MUTED, PALE,
         "munmap, вихід процесу,\nповернення пам'яті\nалокатором",
         "програма й не збиралася\nбільше туди\nдивитися",
         "кадр із вільного пулу,\nвже виданий\nкомусь іншому"),
    ]

    for x, name, accent, fillc, kernel, prog, dev in cols:
        p.append(fitbox(x, 58, 260, 46, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 122, 260, 92, kernel, size=12,
                        fill=SOFT, stroke=accent, sw=1.4, color=INK))
        p.append(fitbox(x, 232, 260, 92, prog, size=12,
                        fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(x, 342, 260, 92, dev, size=12,
                        fill="#fff", stroke=accent, sw=1.4, color=INK))

    p.append(text(175, 174, "що робить ядро", size=12.5, color=MUTED, anchor="end"))
    p.append(text(175, 284, "що бачить програма", size=12.5, color=MUTED, anchor="end"))
    p.append(text(175, 394, "що бачить пристрій", size=12.5, color=MUTED, anchor="end"))

    p.append(fitbox(30, 462, 1280, 96,
                    "спільне в усіх чотирьох: ядро тримає чинною ВІРТУАЛЬНУ адресу, а не фізичний кадр,\n"
                    "і робить це мовчки — у пристрою ж є лише номер кадру, який ніхто не оновлює",
                    size=13.5, fill=WARM, stroke=POS, sw=1.6, color=INK))

    return render(os.path.join(OUT, "frame-escapes.svg"), W, H, *p,
                  title="Куди дівається кадр, номер якого вже віддали пристроєві")


# ── 2. Намір, закодований у лічильнику посилань ──────────────────────────────
def fig_refcount_bias():
    W, H = 1240, 620
    p = []

    p.append(fitbox(120, 58, 1000, 52,
                    "page->_refcount — одне поле на всі види володіння кадром",
                    size=15, fill=PALE, stroke=MUTED, sw=1.5, color=INK, bold=True))

    p.append(fitbox(120, 146, 470, 68,
                    "звичайне посилання: get_page, get_user_pages\n«мені потрібен цей об'єкт сторінки»",
                    size=13, fill=COOL, stroke=NEG, sw=1.6, color=INK))
    p.append(fitbox(650, 146, 470, 68,
                    "закріплення: pin_user_pages\n«у вміст цього кадру писатиме залізо»",
                    size=13, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(arrow(355, 214, 355, 250, NEG))
    p.append(arrow(885, 214, 885, 250, POS))
    p.append(fitbox(255, 250, 200, 54, "+ 1", size=17,
                    fill="#fff", stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(785, 250, 200, 54, "+ 1024", size=17,
                    fill="#fff", stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(text(885, 328, "GUP_PIN_COUNTING_BIAS", size=12, color=MUTED))

    p.append(fitbox(120, 350, 1000, 56,
                    "запит зворотного запису: лічильник ≥ 1024 → «можливо, під DMA»",
                    size=14.5, fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(fitbox(120, 428, 470, 96,
                    "хибне «так» можливе: 1024 звичайних\nпосилань виглядають як одне закріплення.\n"
                    "Ціна — обережніший шлях, не помилка",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(650, 428, 470, 96,
                    "хибне «ні» неможливе: доки закріплення\nживе, ці 1024 у лічильнику стоять.\n"
                    "Саме ця несиметричність робить трюк чинним",
                    size=12.5, fill=GREENF, stroke=FIELD, sw=1.5, color=INK))

    p.append(fitbox(120, 542, 1000, 56,
                    "у великої сторінки в дескрипторі є вільне місце — там лічильник закріплень тримають точно, без зсуву",
                    size=12.5, fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    return render(os.path.join(OUT, "refcount-bias.svg"), W, H, *p,
                  title="Як намір «сюди писатиме залізо» вміщується в наявний лічильник")


# ── 3. Закріплена сторінка й розгалуження процесу ────────────────────────────
def fig_pin_vs_fork():
    W, H = 1320, 620
    p = []

    panels = [
        (40, "Буфер закріплено", FIELD, GREENF),
        (480, "Процес розгалузився", MUTED, PALE),
        (920, "Батько записав байт", POS, WARM),
    ]
    for x, name, accent, fillc in panels:
        p.append(fitbox(x, 58, 360, 44, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))

    # панель 1
    p.append(fitbox(50, 120, 150, 44, "батько", size=13, fill=SOFT, stroke=MUTED, sw=1.3))
    p.append(fitbox(240, 120, 150, 44, "пристрій", size=13, fill=SOFT, stroke=POS, sw=1.5))
    p.append(fitbox(135, 216, 170, 48, "кадр K", size=14, fill="#fff", stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(125, 166, 180, 214, MUTED))
    p.append(arrow(315, 166, 260, 214, POS))
    p.append(fitbox(50, 292, 340, 58,
                    "один через таблицю сторінок,\nдругий за голим номером кадру",
                    size=12, fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    # панель 2
    p.append(fitbox(490, 120, 150, 44, "батько", size=13, fill=SOFT, stroke=MUTED, sw=1.3))
    p.append(fitbox(680, 120, 150, 44, "пристрій", size=13, fill=SOFT, stroke=POS, sw=1.5))
    p.append(fitbox(575, 216, 170, 48, "кадр K", size=14, fill="#fff", stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(565, 166, 620, 214, MUTED))
    p.append(arrow(755, 166, 700, 214, POS))
    p.append(fitbox(490, 292, 150, 44, "дитина", size=13, fill=SOFT, stroke=MUTED, sw=1.3))
    p.append(arrow(620, 266, 565, 290, MUTED))
    p.append(fitbox(660, 292, 170, 58,
                    "обидва записи\nзахищено від запису",
                    size=12, fill="#fff", stroke=MUTED, sw=1.2, color=MUTED))

    # панель 3
    p.append(fitbox(930, 120, 150, 44, "батько", size=13, fill=SOFT, stroke=MUTED, sw=1.3))
    p.append(fitbox(1120, 120, 150, 44, "пристрій", size=13, fill=SOFT, stroke=POS, sw=1.5))
    p.append(fitbox(930, 216, 160, 48, "кадр K′", size=14, fill="#fff", stroke=NEG, sw=1.8, bold=True))
    p.append(fitbox(1110, 216, 160, 48, "кадр K", size=14, fill=WARM, stroke=POS, sw=1.8, bold=True))
    p.append(arrow(1005, 166, 1010, 214, NEG))
    p.append(arrow(1195, 166, 1190, 214, POS))
    p.append(fitbox(1110, 292, 160, 44, "дитина", size=13, fill=SOFT, stroke=MUTED, sw=1.3))
    p.append(arrow(1190, 266, 1190, 290, MUTED))
    p.append(fitbox(930, 292, 160, 58, "копія, свіжий\nкадр", size=12,
                    fill="#fff", stroke=NEG, sw=1.2, color=NEG))

    p.append(fitbox(40, 382, 1240, 76,
                    "пакети з мережі лягають у пам'ять ДИТИНИ, а батько читає свій буфер і бачить старе;\n"
                    "у зворотний бік це витік — дитина читає те, що приходить батькові",
                    size=13.5, fill=WARM, stroke=POS, sw=1.7, color=INK))
    p.append(fitbox(40, 478, 1240, 92,
                    "лікування: fork не захищає закріплені анонімні сторінки від запису, а копіює їх одразу,\n"
                    "тож закріплений кадр гарантовано лишається в того, хто його закріпив",
                    size=13.5, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))

    return render(os.path.join(OUT, "pin-vs-fork.svg"), W, H, *p,
                  title="Чому закріплення й розгалуження процесу сваряться за кадр")


# ── 4. Діапазон байтів → цілі сторінки ──────────────────────────────────────
def fig_pin_range():
    W, H = 1280, 570
    p = []
    PX, PW, PY, PH = 100, 265, 240, 82

    p.append(fitbox(60, 36, 1160, 46,
                    "діапазон, який назвала програма, і сторінки, які через це доведеться закріпити (не в масштабі)",
                    size=13.5, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    bx0, bx1 = PX + 46, PX + 2 * PW + 120
    p.append(rect(bx0, 150, bx1 - bx0, 44, fill=WARM, stroke=POS, sw=1.8, rx=4))
    p.append(text((bx0 + bx1) / 2, 178, "буфер програми: len байтів",
                  size=13, color=INK, bold=True))

    p.append(arrow(bx0, 126, bx0, 146, POS))
    p.append(text(bx0, 114, "addr", size=13, color=POS, bold=True))
    p.append(arrow(bx1, 126, bx1, 146, POS))
    p.append(text(bx1, 114, "addr + len", size=13, color=POS, bold=True))

    p.append(line(bx0, 194, bx0, PY, MUTED, sw=1.1, dash="4,4"))
    p.append(line(bx1, 194, bx1, PY, MUTED, sw=1.1, dash="4,4"))

    cells = [("сторінка N\nзакріплено", True), ("сторінка N+1\nзакріплено", True),
             ("сторінка N+2\nзакріплено", True), ("сторінка N+3\nне чіпаємо", False)]
    for i, (label, taken) in enumerate(cells):
        p.append(fitbox(PX + i * PW, PY, PW - 12, PH, label, size=12.5,
                        fill=GREENF if taken else "#fff",
                        stroke=FIELD if taken else MUTED, sw=1.6,
                        color=INK if taken else MUTED))

    p.append(line(PX, PY + PH, PX, 368, MUTED, sw=1.1, dash="4,4"))
    p.append(line(bx0, PY + PH, bx0, 368, MUTED, sw=1.1, dash="4,4"))
    p.append(arrow(PX, 368, bx0, 368, NEG))
    p.append(text(PX + 90, 372, "зміщення в першій сторінці",
                  size=12.5, color=NEG, anchor="start"))

    p.append(fitbox(60, 400, 1160, 68,
                    "закріплюють ЦІЛІ сторінки: краї діапазону їдуть разом із чужими байтами-сусідами,\n"
                    "а два байти, що припали на межу, коштують двох закріплень",
                    size=13.5, fill=WARM, stroke=POS, sw=1.6, color=INK))
    p.append(fitbox(60, 486, 1160, 56,
                    "nr_pages = ⌈((addr & 4095) + len) / 4096⌉ — рахувати від початку сторінки, а не від addr",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.2, color=MUTED))

    return render(os.path.join(OUT, "pin-range-pages.svg"), W, H, *p,
                  title="Чому діапазон у байтах перетворюється на більше сторінок, ніж здається")


# ── 5. Три відповіді закріплення ────────────────────────────────────────────
def fig_pin_partial():
    W, H = 1300, 550
    p = []

    p.append(fitbox(70, 42, 1160, 48,
                    "pinned = pin_user_pages_fast(start, nr_pages, FOLL_WRITE, pages)",
                    size=14.5, fill=PALE, stroke=MUTED, sw=1.5, color=INK, bold=True))

    cols = [
        (70, "pinned < 0", NEG, COOL,
         "жодної сторінки\nне закріплено",
         "повернути помилку;\nвідпускати нічого"),
        (490, "0 < pinned < nr_pages", POS, WARM,
         "закріплено рівно pinned\nсторінок — вони вже наші",
         "ВІДПУСТИТИ ці pinned,\nа тоді вже повертати\nпомилку"),
        (910, "pinned = nr_pages", FIELD, GREENF,
         "закріплено весь\nдіапазон",
         "працювати, потім\nвідпустити всі"),
    ]
    for x, head, accent, fillc, what, todo in cols:
        p.append(arrow(x + 160, 96, x + 160, 134, accent))
        p.append(fitbox(x, 134, 320, 50, head, size=13.5,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x, 202, 320, 84, what, size=12.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(x, 302, 320, 92, todo, size=12.5,
                        fill="#fff", stroke=accent, sw=1.5, color=INK))

    p.append(fitbox(70, 424, 1160, 96,
                    "середня гілка — єдина, яку легко проґавити, і це витік, якого не побачить ніхто:\n"
                    "закріплення переживає вихід процесу, тож кадри не повернуться в пул до перезавантаження",
                    size=13.5, fill=WARM, stroke=POS, sw=1.7, color=INK))

    return render(os.path.join(OUT, "pin-partial.svg"), W, H, *p,
                  title="Три відповіді pin_user_pages_fast і що робити з кожною")


if __name__ == "__main__":
    print(fig_frame_escapes())
    print(fig_refcount_bias())
    print(fig_pin_vs_fork())
    print(fig_pin_range())
    print(fig_pin_partial())
