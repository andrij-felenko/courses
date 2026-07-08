# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Соленоїд JF-0530B (12 В, push-pull)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Будова: котушка + осердя-плунжер + пружина; два стани (рядками) ───────────
def fig_anatomy():
    W, H = 900, 560
    f = [text(W / 2, 30, "Соленоїд усередині: котушка втягує сталеве осердя, пружина повертає його назад",
              size=15, bold=True)]

    # два стани один під одним: кожен на всю ширину, підписи розведено
    def frame(row_y, title, energized, col):
        f.append(text(W / 2, row_y - 26, title, size=12.5, bold=True, color=col, anchor="middle"))

        # котушка — намотка в лівій частині
        cx, cy, cw, ch = 150, row_y, 190, 84
        f.append(rect(cx, cy, cw, ch, fill="#fdf0ec", stroke=POS, sw=1.8, rx=6))
        for k in range(8):
            xx = cx + 14 + k * 22
            f.append(line(xx, cy + 8, xx, cy + ch - 8, color=POS, sw=1.4))
        f.append(text(cx + cw / 2, cy - 10, "котушка ≈40 Ом", size=10, bold=True, color=POS, anchor="middle"))

        # осердя-штифт: стрижень крізь котушку, торець праворуч
        core_y = cy + ch / 2
        core_len = 300
        if energized:
            core_x0 = cx - 24         # втягнуто глибоко
        else:
            core_x0 = cx + 44         # виштовхнуто назовні
        f.append(rect(core_x0, core_y - 11, core_len, 22, fill="#dfe4ea", stroke=INK, sw=1.8, rx=4))
        # підпис осердя — праворуч від котушки й вище стрижня, де немає ні витків, ні пружини
        f.append(text(cx + cw + 44, core_y - 22, "осердя (штифт)", size=10, color=INK, anchor="middle"))

        tip = core_x0 + core_len

        # нерухома опора праворуч (фіксована, спільна для обох рядків)
        opora = 800
        f.append(line(opora, cy - 6, opora, cy + ch + 6, color=INK, sw=3))
        # пружина від торця штифта до опори (зиґзаґ)
        n = 6
        span = opora - tip
        pts = []
        for k in range(n + 1):
            xx = tip + span * k / n
            yy = core_y + (0 if (k == 0 or k == n) else (11 if k % 2 else -11))
            pts.append((xx, yy))
        for k in range(n):
            f.append(line(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], color=FIELD, sw=2))
        f.append(text((tip + opora) / 2, core_y - 22, "пружина", size=10, bold=True, color=FIELD, anchor="middle"))

        # стрілка руху осердя — під стрижнем, окремим рівнем (щоб не різати написів)
        arr_y = cy + ch + 30
        if energized:
            f.append(arrow(core_x0 + 120, arr_y, core_x0 + 40, arr_y, color=col, sw=2.4))
            f.append(text(core_x0 + 190, arr_y + 4, "осердя втягується всередину", size=10, bold=True, color=col, anchor="start"))
        else:
            f.append(arrow(core_x0 + 40, arr_y, core_x0 + 120, arr_y, color=col, sw=2.4))
            f.append(text(core_x0 + 190, arr_y + 4, "пружина виштовхує штифт назовні", size=10, bold=True, color=col, anchor="start"))

    frame(150, "Струму НЕМА — пружина тримає штифт виштовхнутим", False, FIELD)
    frame(340, "Котушка ПІД СТРУМОМ — осердя втягнуто", True, POS)

    b, _, _ = textbox(W / 2, 500,
                      "Струм у котушці робить її магнітом, і той ВТЯГУЄ сталеве осердя всередину; знімеш струм — пружина сама виштовхує штифт назад.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Драйв: low-side N-MOSFET + гасильний діод на шині 12 В ────────────────────
def fig_drive_mosfet():
    W, H = 900, 560
    f = [text(W / 2, 30, "Правильний драйв: нижній ключ на N-MOSFET, а через котушку — гасильний діод",
              size=14.5, bold=True)]

    # шина +12В зверху
    railY = 92
    f.append(line(140, railY, W - 120, railY, color=POS, sw=3))
    f.append(plus(140, railY, 9))
    f.append(text(W - 120, railY - 12, "+12 В (шина живлення, buck-boost DPS)",
                  size=11, bold=True, color=POS, anchor="end"))

    # котушка соленоїда (символ індуктивності — дужки) між шиною і стоком
    coilX = 430
    coilTop = railY
    coilBot = 250
    f.append(line(coilX, railY, coilX, coilTop + 14, color=INK, sw=2))
    for k in range(4):
        yy = coilTop + 20 + k * 26
        f.append('<path d="M%.0f %.0f q 16 13 0 26" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (coilX, yy, INK))
    f.append(line(coilX, coilTop + 20 + 4 * 26, coilX, coilBot, color=INK, sw=2))
    f.append(text(coilX - 20, (coilTop + coilBot) / 2 + 6, "котушка", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(coilX - 20, (coilTop + coilBot) / 2 + 22, "соленоїда", size=11, bold=True, color=INK, anchor="end"))

    # гасильний діод паралельно котушці (катод до +12В, анод до стоку)
    dX = coilX + 150
    f.append(line(dX, railY, dX, coilBot, color=NEG, sw=2))          # права вітка діода
    f.append(line(coilX, railY, dX, railY, color=NEG, sw=2))          # верх до шини
    f.append(line(coilX, coilBot, dX, coilBot, color=NEG, sw=2))      # низ до стоку
    # трикутник діода (вершиною ВГОРУ = струм від стоку до +12В при кидку)
    dy0 = (railY + coilBot) / 2
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (dX - 12, dy0 + 12, dX + 12, dy0 + 12, dX, dy0 - 12, NEG))
    f.append(line(dX - 14, dy0 - 12, dX + 14, dy0 - 12, color=NEG, sw=2.4))  # смужка катода
    f.append(text(dX + 22, dy0 - 4, "гасильний", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(dX + 22, dy0 + 12, "(flyback) діод", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(dX + 22, dy0 + 30, "напр. 1N4007", size=9.5, color=MUTED, anchor="start"))

    # MOSFET нижнім ключем: стік згори (до котушки), витік — на землю, затвор — з МК
    mX = coilX
    drain_y = coilBot
    gate_y = 330
    src_y = 420
    # вертикаль каналу
    f.append(line(mX, drain_y, mX, src_y, color=INK, sw=3))
    f.append(text(mX + 18, drain_y + 16, "стік (D)", size=10, color=MUTED, anchor="start"))
    f.append(text(mX + 18, src_y - 6, "витік (S)", size=10, color=MUTED, anchor="start"))
    # затвор
    f.append(line(mX - 60, gate_y, mX - 8, gate_y, color=NEG, sw=2))
    f.append(line(mX - 8, gate_y - 22, mX - 8, gate_y + 22, color=INK, sw=3))
    f.append(text(mX - 66, gate_y + 4, "затвор (G)", size=10, bold=True, color=NEG, anchor="end"))
    f.append(text(mX + 60, (drain_y + src_y) / 2, "логік-левел", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(text(mX + 60, (drain_y + src_y) / 2 + 16, "N-MOSFET", size=10, bold=True, color=FIELD, anchor="start"))

    # МК ліворуч → затвор через резистор
    f.append(rect(120, gate_y - 40, 150, 80, fill="#eef2f8", stroke=NEG, sw=2, rx=10))
    f.append(text(195, gate_y - 6, "мікроконтролер", size=10.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(195, gate_y + 14, "вивід GPIO", size=10, color=INK, anchor="middle"))
    # резистор у затвор (прямокутник) + підтяжка вниз
    rgx = 300
    f.append(line(270, gate_y, rgx, gate_y, color=INK, sw=2))
    f.append(rect(rgx, gate_y - 9, 40, 18, fill=BG, stroke=INK, sw=1.5, rx=3))
    f.append(text(rgx + 20, gate_y - 16, "220 Ω", size=9, color=MUTED, anchor="middle"))
    f.append(line(rgx + 40, gate_y, mX - 60, gate_y, color=INK, sw=2))
    # підтяжка затвора до землі (щоб не плавав)
    f.append(text(rgx + 20, gate_y + 30, "+ 100 кΩ на землю", size=9, color=MUTED, anchor="middle"))

    # земля-шина знизу
    gndY = 470
    f.append(line(140, gndY, W - 120, gndY, color=INK, sw=2.6))
    f.append(minus(140, gndY, 9))
    f.append(line(mX, src_y, mX, gndY, color=INK, sw=2))
    f.append(line(195, gate_y + 40, 195, gndY, color=INK, sw=1.6))  # земля МК
    f.append(text(W / 2, gndY + 18, "СПІЛЬНА земля: мінус 12 В і земля мікроконтролера — одна точка",
                  size=10.5, bold=True, color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, 524,
                      "GPIO у «1» відкриває MOSFET, той з'єднує низ котушки із землею — струм тече, осердя втягується.\nУ «0» діод замикає кидок котушки на шину, гасячи стрибок напруги.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "drive-mosfet.svg"), W, H, *f)


# ── 3. Той самий драйвер, що й у степера: вільний канал ULN2003 ──────────────────
def fig_uln_channel():
    W, H = 900, 470
    f = [text(W / 2, 30, "Дешева заміна: вільний канал ULN2003 — той самий чіп, що крутить 28BYJ-48",
              size=14.5, bold=True)]

    # шина +12В
    railY = 92
    f.append(line(150, railY, W - 130, railY, color=POS, sw=3))
    f.append(plus(150, railY, 9))
    f.append(text(W - 130, railY - 12, "+12 В (шина соленоїдів)", size=11, bold=True, color=POS, anchor="end"))

    # блок ULN2003
    ux, uy, uw, uh = 380, 150, 220, 200
    f.append(rect(ux, uy, uw, uh, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(ux + uw / 2, uy + 24, "ULN2003", size=13, bold=True, color=FIELD, anchor="middle"))
    f.append(text(ux + uw / 2, uy + 42, "масив Дарлінгтона, 7 каналів", size=9.5, color=MUTED, anchor="middle"))

    # вивід COM угорі → на +12В
    comx = ux + uw / 2
    f.append(line(comx, uy, comx, railY, color=NEG, sw=2.2))
    f.append(text(comx + 8, (uy + railY) / 2, "COM → +12 В", size=10, bold=True, color=NEG, anchor="start"))
    f.append(text(comx - 8, uy - 8, "(вбудовані гасильні діоди)", size=9, color=MUTED, anchor="end"))

    # вхід INx зліва (з МК), вихід OUTx справа (на котушку)
    iny = uy + 120
    f.append(text(ux + 30, iny, "INx", size=11, bold=True, color=INK, anchor="middle"))
    f.append(text(ux + uw - 34, iny, "OUTx", size=11, bold=True, color=INK, anchor="middle"))

    # МК ліворуч
    f.append(rect(120, iny - 34, 150, 68, fill="#eef2f8", stroke=NEG, sw=2, rx=10))
    f.append(text(195, iny - 6, "мікроконтролер", size=10.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(195, iny + 14, "GPIO → INx", size=10, color=INK, anchor="middle"))
    f.append(arrow(270, iny, ux + 6, iny, color=NEG, sw=1.8))

    # котушка праворуч: від +12В до OUTx
    coilX = ux + uw + 120
    f.append(line(coilX, railY, coilX, iny - 60, color=INK, sw=2))
    for k in range(4):
        yy = iny - 56 + k * 22
        f.append('<path d="M%.0f %.0f q 14 11 0 22" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (coilX, yy, INK))
    f.append(line(coilX, iny - 56 + 4 * 22, coilX, iny, color=INK, sw=2))
    f.append(line(ux + uw, iny, coilX, iny, color=INK, sw=2))
    f.append(text(coilX + 16, (railY + iny) / 2, "котушка", size=10.5, bold=True, color=INK, anchor="start"))
    f.append(text(coilX + 16, (railY + iny) / 2 + 16, "соленоїда", size=10.5, bold=True, color=INK, anchor="start"))
    f.append(text(coilX + 16, (railY + iny) / 2 + 32, "0.3 А @ 12 В", size=9.5, color=MUTED, anchor="start"))

    # земля
    gndY = 388
    f.append(line(150, gndY, W - 130, gndY, color=INK, sw=2.6))
    f.append(minus(150, gndY, 9))
    f.append(line(ux + uw / 2, uy + uh, ux + uw / 2, gndY, color=INK, sw=2))  # GND мікросхеми
    f.append(text(ux + uw / 2 + 12, uy + uh + 16, "GND чіпа", size=9.5, color=MUTED, anchor="start"))
    f.append(line(195, iny + 34, 195, gndY, color=INK, sw=1.6))

    b, _, _ = textbox(W / 2, 436,
                      "0.3 А влазить у 500-мА канал із запасом, а вбудований діод на COM уже гасить кидок — окремий MOSFET і зовнішній діод не потрібні.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "uln-channel.svg"), W, H, *f)


# ── 4. Бюджет живлення: два соленоїди на 12 В, окремо від логіки ────────────────
def fig_power_budget():
    W, H = 900, 500
    f = [text(W / 2, 30, "Живлення: 12 В на соленоїди — окрема шина, не з виводу мікроконтролера",
              size=14.5, bold=True)]

    # джерело: buck-boost DPS
    sx, sy, sw_, sh = 50, 150, 180, 128
    f.append(rect(sx, sy, sw_, sh, fill="#fdecea", stroke=POS, sw=2, rx=12))
    f.append(text(sx + sw_ / 2, sy + 30, "buck-boost DPS", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(sx + sw_ / 2, sy + 54, "виставлено 12 В", size=10.5, bold=True, color=INK, anchor="middle"))
    f.append(text(sx + sw_ / 2, sy + 78, "тримає ≥ 1 А", size=10, color=MUTED, anchor="middle"))
    f.append(text(sx + sw_ / 2, sy + 102, "(від акумулятора)", size=9.5, color=MUTED, anchor="middle"))

    railY = sy + 24
    gndY = 420
    f.append(line(sx + sw_, railY, W - 70, railY, color=POS, sw=3))
    f.append(plus(sx + sw_, railY, 8))
    f.append(text(W - 70, railY - 12, "+12 В", size=11, bold=True, color=POS, anchor="end"))

    # два стовпці навантаження: котушка(індуктор збоку від дроту) → ключ → земля
    def load(colX, label):
        wireX = colX                       # вертикальний дріт від шини до землі
        # котушка — три дуги ЗБОКУ від дроту (символ індуктивності), підпис ще лівіше
        ind_top = railY + 16
        for k in range(3):
            yy = ind_top + k * 20
            f.append('<path d="M%.0f %.0f q 13 10 0 20" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (wireX, yy, INK))
        f.append(line(wireX, railY, wireX, ind_top, color=INK, sw=2))
        ind_bot = ind_top + 3 * 20
        f.append(text(wireX - 16, (ind_top + ind_bot) / 2, label, size=10.5, bold=True, color=INK, anchor="end"))
        f.append(text(wireX - 16, (ind_top + ind_bot) / 2 + 16, "0.3 А", size=9.5, color=MUTED, anchor="end"))
        # ключ-блок
        dw, dh = 120, 52
        dx, dy = wireX - dw / 2, ind_bot + 20
        f.append(line(wireX, ind_bot, wireX, dy, color=INK, sw=2))
        f.append(rect(dx, dy, dw, dh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
        f.append(text(wireX, dy + 21, "ключ + діод", size=10.5, bold=True, color=FIELD, anchor="middle"))
        f.append(text(wireX, dy + 39, "(MOSFET/ULN)", size=9, color=MUTED, anchor="middle"))
        f.append(line(wireX, dy + dh, wireX, gndY, color=INK, sw=2))

    load(500, "соленоїд 1")
    load(710, "соленоїд 2")

    # МК окремо (лівий-нижній кут), живиться від 3.3/5 В — ТІЛЬКИ сигнали
    mcx, mcy, mcw, mch = 250, 320, 170, 60
    f.append(rect(mcx, mcy, mcw, mch, fill="#eef2f8", stroke=NEG, sw=1.8, rx=10))
    f.append(text(mcx + mcw / 2, mcy + 24, "мікроконтролер", size=10.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(mcx + mcw / 2, mcy + 44, "3.3 В / 5 В, окремо", size=9.5, color=MUTED, anchor="middle"))
    # тонкі сигнальні стрілки до ключів
    f.append(arrow(mcx + mcw, mcy + 20, 500 - 60, 380, color=NEG, sw=1.4))
    f.append(arrow(mcx + mcw, mcy + 40, 710 - 60, 380, color=NEG, sw=1.4))
    f.append(text(mcx + mcw / 2, mcy - 10, "лише сигнали до ключів", size=9.5, color=MUTED, anchor="middle"))

    # земля-шина
    f.append(line(sx + sw_, gndY, W - 70, gndY, color=INK, sw=2.6))
    f.append(minus(sx + sw_, gndY, 8))
    f.append(line(sx + sw_ / 2, sy + sh, sx + sw_ / 2, gndY, color=INK, sw=2))  # мінус DPS → земля
    f.append(line(mcx + mcw / 2, mcy + mch, mcx + mcw / 2, gndY, color=INK, sw=1.6))  # земля МК
    f.append(text(W / 2, gndY + 20, "СПІЛЬНА земля всіх: DPS, ключі, мікроконтролер",
                  size=10.5, bold=True, color=POS, anchor="middle"))

    # позначка сумарного струму (правий-верхній, над шиною)
    b0, _, _ = textbox(720, 96, "два одночасні спрацювання:\n0.3 + 0.3 ≈ 0.6 А піку",
                       size=10, fill="#fdf3e6", stroke=POS, color=INK, bold=True)
    f.append(b0)

    b, _, _ = textbox(W / 2, 470,
                      "Індуктивне навантаження живе на своїй 12-вольтовій шині; мікроконтролер лише керує ключами. Землю всіх вузлів зводять у спільну точку.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "power-budget.svg"), W, H, *f)


# ── 5. Історична смуга: від іскри на контакті до гасильного діода ────────────
#     (для вставки hist-freewheeling-diode.md)
def fig_hist_timeline():
    W, H = 1000, 660
    f = [text(W / 2, 34, "Від іскри на контакті до діода поперек котушки: як дозріла схема",
              size=15.5, bold=True)]

    # вертикальна вісь ліворуч; праворуч — картки-події з ЗАПАСОМ по висоті
    axis_x = 150
    top, bot = 78, H - 46
    f.append(line(axis_x, top, axis_x, bot, color=MUTED, sw=3))

    # рядки: (рік, заголовок, текст-картка, колір)
    rows = [
        ("1832",
         "Джозеф Генрі бачить іскру",
         "Розриваєш коло з котушкою — на контакті скаче іскра. Генрі пояснює її самоіндукцією: явище вже є, ліку ще нема.",
         NEG),
        ("1834",
         "Фарадей: «додатковий струм»",
         "Майкл Фарадей друкує про «extra current at break» — той самий кидок при розмиканні. Проблему названо й описано.",
         NEG),
        ("~1900–1920",
         "Іскру душать конденсатором",
         "У реле й дзвінках поперек КОНТАКТУ ставлять конденсатор чи RC-ланку. Придатного діода поперек котушки ще нема.",
         MUTED),
        ("1920 · 1933",
         "З'являються тверді випрямлячі",
         "Мідно-закисний (1920) і селеновий (1933) дають перший придатний вентиль — тепер є ЩО поставити поперек обмотки.",
         FIELD),
        ("~1930 → 1950",
         "Слово flyback з ЕПТ",
         "Схеми зворотного ходу променя (flyback) в осцилографах і ТБ; звідти «flyback» перейде на кидок індуктивності.",
         POS),
        ("кінець 1950-х →",
         "Кремнієвий діод — і звичка",
         "Дешевий кремнієвий діод робить діод поперек котушки рефлексом схемотехніка. Ніхто не патентує — це загальна практика.",
         INK),
    ]

    n = len(rows)
    span = bot - top
    row_h = span / n
    card_x = axis_x + 70
    card_w = W - card_x - 40

    for i, (yr, head, body_txt, col) in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        # вузол на осі
        f.append(circle(axis_x, cy, 7, fill=BG, stroke=col, sw=3))
        # рік — ЛІВОРУЧ від осі, окремою колонкою (широкою, щоб не налазив на вісь)
        f.append(text(axis_x - 18, cy + 4, yr, size=11.5, bold=True, color=col, anchor="end"))
        # картка події — праворуч; висота з запасом, текст через fitbox (не вилазить)
        ch = row_h - 22
        top_y = cy - ch / 2
        # короткий поводок від осі до картки
        f.append(line(axis_x + 7, cy, card_x, cy, color=col, sw=1.6))
        f.append(rect(card_x, top_y, card_w, ch, fill="#fafbfc", stroke=col, sw=1.6, rx=8))
        f.append(text(card_x + 14, top_y + 20, head, size=11.5, bold=True, color=col, anchor="start"))
        # тіло — у нижній частині картки, з переносом; fitbox центрує в заданому боксі
        body_h = ch - 30
        f.append(fitbox(card_x + 8, top_y + 26, card_w - 16, body_h, body_txt,
                        size=10.5, pad=6, fill="none", stroke="none", color=INK))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── 6. Один сигнал — два ключі: MOSFET і канал ULN2003 (для proj-drive-solenoid) ─
#     Наголос: код той самий, різниця лише в монтажі й гасінні кидка.
def fig_two_paths_code():
    W, H = 960, 560
    f = [text(W / 2, 30, "Один сигнал SOL_PIN — два ключі: код драйва однаковий, різниться лише монтаж",
              size=14.5, bold=True)]

    # МК угорі-центр, з нього одна ніжка SOL_PIN, що роздвоюється
    mcx, mcy, mcw, mch = W / 2 - 95, 62, 190, 58
    f.append(rect(mcx, mcy, mcw, mch, fill="#eef2f8", stroke=NEG, sw=2, rx=10))
    f.append(text(W / 2, mcy + 24, "мікроконтролер", size=11.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(W / 2, mcy + 43, "digitalWrite / analogWrite(SOL_PIN)", size=9.5, color=INK, anchor="middle"))

    # точка розгалуження під МК
    forkY = mcy + mch + 26
    f.append(line(W / 2, mcy + mch, W / 2, forkY, color=INK, sw=2.2))
    f.append(circle(W / 2, forkY, 4, fill=INK, stroke=INK, sw=1))
    # підпис SOL_PIN — ЗБОКУ від вертикального дроту (не на ньому), щоб лінія не різала напис
    f.append(text(W / 2 + 12, forkY - 6, "SOL_PIN", size=10.5, bold=True, color=INK, anchor="start"))

    leftX, rightX = 250, 710
    f.append(line(W / 2, forkY, leftX, forkY, color=INK, sw=2))       # горизонталь ліворуч
    f.append(line(W / 2, forkY, rightX, forkY, color=INK, sw=2))      # горизонталь праворуч
    f.append(line(leftX, forkY, leftX, forkY + 24, color=INK, sw=2))
    f.append(line(rightX, forkY, rightX, forkY + 24, color=INK, sw=2))

    railY = forkY + 40      # локальна «+12 В» риска над котушками
    gndY = 452

    # ── спільний малювальник однієї гілки (котушка → ключ-бокс → земля) ─────────
    def branch(cx, gate_in_y, key_lines, key_col, coil_label):
        # +12 В шматок над котушкою
        f.append(line(cx - 60, railY, cx + 60, railY, color=POS, sw=2.6))
        f.append(plus(cx - 60, railY, 7))
        f.append(text(cx + 60, railY - 10, "+12 В", size=9.5, bold=True, color=POS, anchor="end"))
        # котушка (символ індуктивності) від +12В до верху ключа
        coil_top = railY + 12
        for k in range(4):
            yy = coil_top + k * 18
            f.append('<path d="M%.0f %.0f q 12 9 0 18" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (cx, yy, INK))
        coil_bot = coil_top + 4 * 18
        f.append(line(cx, railY, cx, coil_top, color=INK, sw=2))
        f.append(text(cx + 16, (coil_top + coil_bot) / 2, coil_label, size=10, bold=True, color=INK, anchor="start"))
        f.append(text(cx + 16, (coil_top + coil_bot) / 2 + 15, "0.3 А", size=9, color=MUTED, anchor="start"))
        # ключ-бокс
        kw, kh = 150, 66
        kx, ky = cx - kw / 2, coil_bot + 18
        f.append(line(cx, coil_bot, cx, ky, color=INK, sw=2))
        f.append(rect(kx, ky, kw, kh, fill="#f7f9f7", stroke=key_col, sw=2, rx=8))
        for j, ln in enumerate(key_lines):
            f.append(text(cx, ky + 20 + j * 16, ln, size=10 if j == 0 else 9,
                          bold=(j == 0), color=key_col if j == 0 else MUTED, anchor="middle"))
        # вхід керування збоку ключа (від горизонталі SOL_PIN)
        f.append(line(cx, gate_in_y, kx, ky + kh / 2, color=key_col, sw=1.8))
        # до землі
        f.append(line(cx, ky + kh, cx, gndY, color=INK, sw=2))
        return ky + kh / 2

    branch(leftX, forkY + 24,
           ["low-side MOSFET", "затвор ← SOL_PIN", "потрібен зовн. діод"],
           FIELD, "котушка")
    branch(rightX, forkY + 24,
           ["канал ULN2003", "IN ← SOL_PIN", "діод вбудований"],
           NEG, "котушка")

    # спільна земля
    f.append(line(180, gndY, W - 120, gndY, color=INK, sw=2.6))
    f.append(minus(180, gndY, 8))
    f.append(text(W / 2, gndY + 18, "обидва — НИЖНІ ключі: HIGH → низ котушки притягнуто до спільної землі",
                  size=10.5, bold=True, color=POS, anchor="middle"))

    # застереження-рамки під кожною гілкою (де замикається кидок)
    b1, _, _ = textbox(leftX, 512,
                       "гасильний ДІОД\nпаралельно котушці — ОБОВ'ЯЗКОВО",
                       size=10, fill="#fdf3e6", stroke=POS, color=INK, bold=True)
    f.append(b1)
    b2, _, _ = textbox(rightX, 512,
                       "COM → +12 В\nі вбудований діод усе гасить",
                       size=10, fill="#eaf2ea", stroke=FIELD, color=INK, bold=True)
    f.append(b2)

    render(os.path.join(IMG, "two-paths-code.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_drive_mosfet()
    fig_uln_channel()
    fig_power_budget()
    fig_hist_timeline()
    fig_two_paths_code()
    print("OK: 6 figures ->", IMG)
