# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Розгалуження історії: що міняється, а що ні ──────────────────────────
def fig_history_fork():
    W, H = 1360, 940
    p = []

    trunk_y = 300
    p.append(text(150, 120, "ОДНА ІСТОРІЯ", size=15, bold=True))
    p.append(line(80, trunk_y, 560, trunk_y, color=LINE, sw=2.4))
    p.append(circle(560, trunk_y, 8, fill=POS, stroke=POS, sw=1))

    frag, w0, h0 = textbox(300, 175, ["стан машини: ключ генератора,",
                                      "лічильники, відкриті з'єднання"],
                           size=12.5, pad=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)
    p.append(line(300, 175 + h0 / 2 + 8, 300, trunk_y - 12, color=MUTED, sw=1.1, dash="5 4"))

    frag, wsn, hsn = textbox(560, 430, ["ЗНІМОК",
                                        "увесь стан збережено у файл"],
                             size=13, pad=13, fill=RED_FILL, stroke=POS, sw=1.5)
    p.append(frag)
    p.append(line(560, trunk_y + 12, 560, 430 - hsn / 2 - 8, color=POS, sw=1.4, dash="5 4"))

    # дві гілки
    up_y, dn_y = 150, 560
    p.append(line(560, trunk_y, 700, up_y, color=LINE, sw=2.4))
    p.append(arrow(700, up_y, 1130, up_y, sw=2.4))
    p.append(line(560, trunk_y, 700, dn_y, color=LINE, sw=2.4))
    p.append(arrow(700, dn_y, 1130, dn_y, sw=2.4))

    frag, wa, ha = textbox(940, up_y - 82, ["копія A: та сама гама,",
                                            "ті самі одноразові числа"],
                           size=12.5, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.3)
    p.append(frag)
    frag, wb, hb = textbox(940, dn_y + 82, ["копія B: та сама гама,",
                                            "ті самі одноразові числа"],
                           size=12.5, pad=13, fill=WARM_FILL, stroke=LINE, sw=1.3)
    p.append(frag)

    # ідентифікатори
    p.append(text(310, trunk_y - 42, "ID = G₁", size=15, bold=True, color=NEG))
    p.append(text(940, up_y - 22, "ID = G₂", size=15, bold=True, color=NEG))
    p.append(text(940, dn_y - 22, "ID = G₃", size=15, bold=True, color=NEG))

    frag, _, _ = textbox(680, 790, ["Гість не бачить розгалуження: обидві копії пам'ятають лише стовбур.",
                                    "Єдине, що їх розрізняє, — 128-бітне число, яке вписав гіпервізор."],
                         size=13, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(frag)

    frag, _, _ = textbox(680, 900, ["Пауза, перезавантаження гостя й жива міграція розгалуження не роблять — там ID лишається G₁."],
                         size=12.5, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'history-fork.svg'), W, H, *p,
           title="Знімок роздвоює історію машини, і обидві гілки цього не помічають")


# ── 2. Де лежать шістнадцять байтів і як про них дізнаються ─────────────────
def fig_where_it_lives():
    W, H = 1420, 860
    p = []
    lx, rx = 330, 1080

    p.append(text(lx, 70, "ГІПЕРВІЗОР", size=15, bold=True))
    p.append(text(rx, 70, "ГОСТЬОВЕ ЯДРО", size=15, bold=True))
    p.append(line(700, 95, 700, 700, color=MUTED, sw=1.4, dash="7 6"))

    frag, w1, h1 = textbox(lx, 170, ["опис пристрою в таблицях ACPI:",
                                     "_CID = «VM_Gen_Counter»,",
                                     "метод ADDR → фізична адреса"],
                           size=13, pad=14, fill=WARM_FILL, stroke=LINE, sw=1.5)
    p.append(frag)

    frag, w2, h2 = textbox(lx, 380, ["сторінка гостьової фізичної пам'яті,",
                                     "вилучена з карти доступного ОЗП:",
                                     "16 байтів, вирівняні на 8"],
                           size=13, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6)
    p.append(frag)

    frag, w3, h3 = textbox(lx, 600, ["під час клонування або відкоту",
                                     "гіпервізор вписує сюди нове число",
                                     "і б'є Notify(0x80)"],
                           size=13, pad=14, fill=RED_FILL, stroke=POS, sw=1.5)
    p.append(frag)
    p.append(line(lx, 380 + h2 / 2 + 10, lx, 600 - h3 / 2 - 10, color=MUTED, sw=1.2, dash="5 4"))

    frag, w4, h4 = textbox(rx, 170, ["драйвер vmgenid бере адресу",
                                     "з ADDR і робить memremap"],
                           size=13, pad=14, fill=BLUE_FILL, stroke=LINE, sw=1.5)
    p.append(frag)
    p.append(arrow(lx + w1 / 2 + 16, 170, rx - w4 / 2 - 16, 170))

    frag, w5, h5 = textbox(rx, 380, ["next_id — покажчик у ту сторінку",
                                     "this_id — власна копія 16 байтів"],
                           size=13, pad=14, fill=BLUE_FILL, stroke=LINE, sw=1.5)
    p.append(frag)
    p.append(arrow(lx + w2 / 2 + 16, 380, rx - w5 / 2 - 16, 380))

    frag, w6, h6 = textbox(rx, 600, ["обробник звіряє this_id з next_id",
                                     "і, якщо різні, б'є тривогу"],
                           size=13, pad=14, fill=BLUE_FILL, stroke=LINE, sw=1.5)
    p.append(frag)
    p.append(arrow(lx + w3 / 2 + 16, 600, rx - w6 / 2 - 16, 600))

    frag, _, _ = textbox(700, 760, ["Пам'ять дає звірку будь-якої миті, сповіщення — поштовх;",
                                    "без ACPI ту саму пару дає вузол дерева пристроїв «microsoft,vmgenid» з reg і перериванням."],
                         size=12.5, pad=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'where-it-lives.svg'), W, H, *p,
           title="Ідентифікатор покоління — це не пристрій, а шістнадцять байтів у пам'яті")


# ── 3. Що відбувається після тривоги ────────────────────────────────────────
def fig_after_alarm():
    W, H = 1420, 900
    p = []
    cx = 470

    frag, w1, h1 = textbox(cx, 110, ["vmgenid_notify(): this_id ≠ next_id"],
                           size=13.5, pad=15, fill=RED_FILL, stroke=POS, sw=1.7)
    p.append(frag)

    frag, w2, h2 = textbox(cx, 250, ["add_vmfork_randomness(нове число, 16)"],
                           size=13.5, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.6)
    p.append(frag)
    p.append(arrow(cx, 110 + h1 / 2 + 12, cx, 250 - h2 / 2 - 12))

    rows = [
        (450, ["add_device_randomness():",
               "число вмішано в накопичувач,",
               "але зараховано нуль бітів"],
         ["воно унікальне, та не таємне:", "з боку господаря його видно через QMP"]),
        (640, ["crng_reseed():",
               "ключ генератора перезаряджено,",
               "номер покоління підріс"],
         ["на цей номер дивиться getrandom()", "у vDSO перед кожною видачею"]),
        (820, ["vmfork_chain:",
               "сповіщено підписників усередині ядра"],
         ["WireGuard стирає сеанси, щоб не", "повторити одноразове число"]),
    ]

    # вертикальна шина від add_vmfork_randomness до трьох наслідків
    bus_x = 130
    p.append(line(cx, 250 + h2 / 2 + 12, cx, 350, color=LINE, sw=1.8))
    p.append(line(bus_x, 350, cx, 350, color=LINE, sw=1.8))
    p.append(line(bus_x, 350, bus_x, rows[-1][0], color=LINE, sw=1.8))

    for y, lines, note in rows:
        frag, w, h = textbox(cx, y, lines, size=13, pad=14,
                             fill=GREEN_FILL, stroke=FIELD, sw=1.5)
        p.append(frag)
        p.append(arrow(bus_x, y, cx - w / 2 - 14, y))
        frag2, nw, _ = textbox(1150, y, note, size=12.5, pad=12,
                               fill=GREY_FILL, stroke=MUTED, sw=1.2)
        p.append(frag2)
        p.append(line(cx + w / 2 + 14, y, 1150 - nw / 2 - 14, y, color=MUTED, sw=1.1, dash="5 4"))

    render(os.path.join(IMG, 'after-alarm.svg'), W, H, *p,
           title="Тривога перетворюється на три різні дії всередині ядра")


# ── 4. Розкладка блоба fw_cfg у QEMU (для довідки-контракту) ────────────────
def fig_page_layout():
    W, H = 1400, 660
    p = []

    p.append(text(700, 118, "Блоб fw_cfg «etc/vmgenid_guid» — рівно одна сторінка, 4096 байтів",
                  size=15, bold=True))
    p.append(text(700, 152, "ширина сегментів не пропорційна їхньому розмірові",
                 size=12, color=MUTED, italic=True))

    bar_y, bar_h = 230, 112
    p.append(fitbox(90, bar_y, 340, bar_h,
                    ["36 байтів заглушки", "проти пошуку", "SDT-заголовка в OVMF"],
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.3))
    p.append(fitbox(430, bar_y, 170, bar_h,
                    ["4 байти", "доповнення", "до вирівнювання на 8"],
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.3))
    p.append(fitbox(600, bar_y, 300, bar_h,
                    ["GUID", "16 байтів", "те, що читає гість"],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2))
    p.append(fitbox(900, bar_y, 410, bar_h,
                    ["решта сторінки", "до 4096 байтів"],
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.3))

    off_y = bar_y + bar_h + 34
    for x, s in ((90, "0"), (430, "36"), (600, "40"), (900, "56"), (1310, "4096")):
        p.append(text(x, off_y, s, size=13, color=MUTED, bold=True))
    p.append(text(700, off_y + 32, "зсув від початку блоба, у байтах", size=12, color=MUTED))

    p.append(line(750, bar_y + bar_h, 750, 452, color=MUTED, sw=1.3, dash="5 4"))
    frag, _, _ = textbox(750, 492,
                         ["ADDR() → Package(2) { VGIA + 0x28 , 0 }",
                          "молодші 32 біти адреси GUID, потім старші"],
                         size=13.5, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.6)
    p.append(frag)

    frag, _, _ = textbox(700, 605,
                         ["VGIA — іменована комірка в SSDT: адресу блоба туди вписує прошивка,",
                          "а QEMU дізнається її назад із записуваного блоба «etc/vmgenid_addr»."],
                         size=12.5, pad=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'page-layout.svg'), W, H, *p,
           title="Шістнадцять байтів GUID лежать із зсувом 40 у сторінці fw_cfg")


if __name__ == '__main__':
    fig_history_fork()
    fig_where_it_lives()
    fig_after_alarm()
    fig_page_layout()
    print("ok")
