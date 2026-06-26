# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Бюджет пам'яті мікроконтролера».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

FLASHBG = "#eef2f7"   # холодна заливка під Flash
RAMBG   = "#fdf6e3"   # тепла заливка під RAM
CODEBG  = "#e8eef9"   # .text
RODBG   = "#e9f7ef"   # .rodata
DATABG  = "#fdecea"   # .data (живе у двох — гаряче)
BSSBG   = "#f3e8fb"   # .bss
HEAPBG  = "#e9f7ef"   # купа
STACKBG = "#eaf0fd"   # стек
GREY    = "#6b7280"
PURPLE  = "#7b3fa0"


# ── 1. Дві пам'яті, два питання ──────────────────────────────────────────────
# Ідея: Flash і RAM — окремі стовпи. У Flash лежить усе незмінне (код, сталі,
# початкові значення); у RAM — усе, що живе під час роботи. Підпис під кожним:
# Flash рахують РАЗ (при лінкуванні), RAM — і при лінкуванні, і ПІД ЧАС роботи.
def fig_two_memories():
    W, H = 900, 470
    P = [text(W / 2, 30, "Дві пам'яті — два різні питання бюджету", size=17, bold=True),
         text(W / 2, 50, "Flash тримає незмінне, RAM — усе, що живе під час роботи",
              size=11, color=MUTED, italic=True)]

    colw = 300
    top = 90
    bot = 380
    # ── Flash ──
    fx = 110
    P.append(rect(fx, top, colw, bot - top, fill=FLASHBG, stroke=LINE, sw=2, rx=10))
    P.append(text(fx + colw / 2, top - 12, "FLASH — нелетка, велика, повільніша",
                  size=13, bold=True))
    seg = (bot - top) / 3.0
    P.append(fitbox(fx + 14, top + 14, colw - 28, seg - 20,
                    ".text\nкод програми", fill=CODEBG, bold=True, size=13))
    P.append(fitbox(fx + 14, top + seg + 8, colw - 28, seg - 16,
                    ".rodata\nсталі, рядки, таблиці", fill=RODBG, bold=True, size=13))
    P.append(fitbox(fx + 14, top + 2 * seg + 2, colw - 28, seg - 14,
                    ".data (копія)\nпочаткові значення змінних", fill=DATABG, bold=True, size=12))

    # ── RAM ──
    rx = 490
    P.append(rect(rx, top, colw, bot - top, fill=RAMBG, stroke=LINE, sw=2, rx=10))
    P.append(text(rx + colw / 2, top - 12, "RAM (SRAM) — летка, мала, швидка",
                  size=13, bold=True))
    # знизу вгору: .data, .bss, купа↑ ... вільне ... стек↓
    P.append(fitbox(rx + 14, bot - 56, colw - 28, 44,
                    ".data + .bss — статичні змінні", fill=DATABG, bold=True, size=12))
    P.append(text(rx + colw / 2, bot - 78, "↑ купа росте вгору", size=12, color=FIELD, bold=True))
    P.append(text(rx + colw / 2, top + 70, "↓ стек росте вниз", size=12, color=NEG, bold=True))
    P.append(fitbox(rx + 14, top + 12, colw - 28, 30,
                    "стек (на старті — згори)", fill=STACKBG, bold=True, size=12))
    P.append(text(rx + colw / 2, (top + bot) / 2 + 4, "вільне місце", size=12, color=GREY, italic=True))

    # ── копіювання .data Flash→RAM на старті ──
    P.append(arrow(fx + colw, top + 2 * seg + seg / 2, rx, bot - 34, color=POS, sw=2))
    P.append(text((fx + colw + rx) / 2, top + 2 * seg + 6,
                  "старт: копія Flash→RAM", size=11, color=POS, bold=True))

    # ── два питання внизу ──
    P.append(fitbox(fx, bot + 22, colw, 56,
                    "Бюджет Flash = .text + .rodata + .data\nрахують РАЗ — при лінкуванні",
                    fill="#ffffff", stroke=LINE, size=12, bold=True))
    P.append(fitbox(rx, bot + 22, colw, 56,
                    "Бюджет RAM = .data + .bss + купа + стек\nі при лінкуванні, і ПІД ЧАС роботи",
                    fill="#ffffff", stroke=POS, size=12, bold=True))
    return render("img/two-memories.svg", W, H, *P)


# ── 2. Чотири секції → де кожна осідає ───────────────────────────────────────
# Ідея: чотири різновиди даних із коду, від кожного стрілка(и) у Flash і/або RAM.
# .data — єдина з ДВОМА стрілками (коштує в обох). .bss — лише RAM (у Flash нуль).
def fig_sections():
    W, H = 920, 430
    P = [text(W / 2, 30, "Звідки беруться байти: чотири секції коду", size=17, bold=True),
         text(W / 2, 50, ".data платить двічі; .bss у Flash не коштує нічого",
              size=11, color=MUTED, italic=True)]

    # ліворуч — чотири різновиди оголошень
    lx = 60
    bw = 250
    ys = [90, 168, 246, 324]
    rows = [
        ("int табл[256] = {…};  // код", ".text — інструкції", CODEBG),
        ('const char msg[] = "OK";', ".rodata — лише читання", RODBG),
        ("int лічильник = 42;", ".data — є початкове значення", DATABG),
        ("uint8_t буфер[1024];", ".bss — без значення (нуль)", BSSBG),
    ]
    for (code, name, col), y in zip(rows, ys):
        P.append(fitbox(lx, y, bw, 58, name, fill=col, bold=True, size=12))

    # праворуч — дві пам'яті
    flx, frx = 560, 740
    fw = 150
    ftop, fbot = 80, 360
    P.append(rect(flx, ftop, fw, fbot - ftop, fill=FLASHBG, stroke=LINE, sw=2, rx=10))
    P.append(text(flx + fw / 2, ftop - 10, "FLASH", size=14, bold=True))
    P.append(rect(frx, ftop, fw, fbot - ftop, fill=RAMBG, stroke=LINE, sw=2, rx=10))
    P.append(text(frx + fw / 2, ftop - 10, "RAM", size=14, bold=True))

    fc = flx + fw / 2
    rc = frx + fw / 2
    # .text → Flash
    P.append(arrow(lx + bw, ys[0] + 29, flx, 120, color=LINE, sw=1.8))
    # .rodata → Flash
    P.append(arrow(lx + bw, ys[1] + 29, flx, 170, color=LINE, sw=1.8))
    # .data → Flash (початкове значення) І → RAM (робоча копія)
    P.append(arrow(lx + bw, ys[2] + 29, flx, 240, color=POS, sw=2.2))
    P.append(arrow(lx + bw, ys[2] + 29, frx, 230, color=POS, sw=2.2))
    # .bss → лише RAM
    P.append(arrow(lx + bw, ys[3] + 29, frx, 310, color=PURPLE, sw=2.2))

    P.append(text(fc, 120, ".text", size=11, bold=True))
    P.append(text(fc, 172, ".rodata", size=11, bold=True))
    P.append(text(fc, 246, ".data", size=11, color=POS, bold=True))
    P.append(text(rc, 232, ".data", size=11, color=POS, bold=True))
    P.append(text(rc, 312, ".bss", size=11, color=PURPLE, bold=True))
    P.append(text(rc, 332, "(нулі)", size=10, color=PURPLE))

    P.append(fitbox(450, 372, W - 480, 44,
                    ".data — у Flash лежить початкове значення, у RAM його копія: коштує в ОБОХ.   "
                    ".bss у Flash = 0 байтів (зберігати нулі нема сенсу), на старті його просто чистять у RAM.",
                    fill="#ffffff", stroke=POS, size=11))
    return render("img/sections.svg", W, H, *P)


# ── 3. RAM під час роботи: затиск ────────────────────────────────────────────
# Ідея: вертикальний стовп RAM. Знизу — нерухомий поверх (.data+.bss). Над ним
# купа росте ВГОРУ; згори стек росте ВНИЗ; між ними тане вільне місце. Зустріч
# = крах. Показуємо два моменти: спокій і затиск.
def fig_squeeze():
    W, H = 860, 470
    P = [text(W / 2, 30, "RAM під час роботи: стек і купа йдуть назустріч", size=17, bold=True),
         text(W / 2, 50, "статичний поверх нерухомий; зіткнення стека з купою = крах",
              size=11, color=MUTED, italic=True)]

    top, bot = 90, 410
    colw = 260
    base_h = 70   # .data + .bss

    def column(x, heap_h, stack_h, label, danger=False):
        out = [rect(x, top, colw, bot - top, fill="#ffffff", stroke=LINE, sw=2, rx=8)]
        # верх = висока адреса
        out.append(text(x + colw / 2, top - 10, label, size=12, bold=True))
        out.append(text(x - 6, top + 12, "висока", size=9, color=GREY, anchor="end"))
        out.append(text(x - 6, bot - 4, "низька", size=9, color=GREY, anchor="end"))
        # статичний поверх знизу
        out.append(rect(x + 6, bot - base_h, colw - 12, base_h - 4, fill=DATABG, stroke=LINE, sw=1.2))
        out.append(text(x + colw / 2, bot - base_h / 2 - 2, ".data + .bss", size=11, bold=True))
        out.append(text(x + colw / 2, bot - base_h / 2 + 12, "(нерухомий)", size=9, color=GREY))
        # купа над поверхом, росте вгору
        hy = bot - base_h - heap_h
        out.append(rect(x + 6, hy, colw - 12, heap_h, fill=HEAPBG, stroke=FIELD, sw=1.4))
        out.append(text(x + colw / 2, hy + heap_h / 2 + 4, "купа ↑", size=11, color=FIELD, bold=True))
        # стек згори, росте вниз
        out.append(rect(x + 6, top + 6, colw - 12, stack_h, fill=STACKBG, stroke=NEG, sw=1.4))
        out.append(text(x + colw / 2, top + 6 + stack_h / 2 + 4, "стек ↓", size=11, color=NEG, bold=True))
        # проміжок
        gap_top = top + 6 + stack_h
        gap_bot = hy
        if danger:
            mid = (gap_top + gap_bot) / 2
            out.append(line(x + 6, mid, x + colw - 6, mid, color=POS, sw=2.4, dash="6 4"))
            out.append(text(x + colw / 2, mid - 8, "зіткнення!", size=12, color=POS, bold=True))
        else:
            out.append(text(x + colw / 2, (gap_top + gap_bot) / 2 + 4, "вільне", size=11, color=GREY, italic=True))
        return out

    P += column(70, 60, 55, "спокій: запас є")
    P += column(530, 110, 110, "затиск: запасу нема", danger=True)

    P.append(fitbox(70, bot + 20, W - 140, 46,
                    "Вільне місце посередині — це і є справжній запас RAM.\n"
                    "Глибша рекурсія чи більший буфер роздувають стек і купу, доки вони стуляться — і дані одне одного затруть.",
                    fill="#ffffff", stroke=POS, size=11))
    return render("img/squeeze.svg", W, H, *P)


# ── 4. Бюджет на серветці ────────────────────────────────────────────────────
# Ідея: для RAM — стовп використаного (по поверхах) проти стелі чипа; зверху
# смуга «запас». Праворуч — той самий чип без запасу: стовп пробиває стелю.
def fig_napkin():
    W, H = 860, 460
    P = [text(W / 2, 30, "Бюджет на серветці: складаємо поверхи, лишаємо запас", size=17, bold=True),
         text(W / 2, 50, "сума статики, купи й стека проти стелі RAM — із запасом ~20–30%",
              size=11, color=MUTED, italic=True)]

    base_y = 400
    top_y = 90
    full = base_y - top_y      # вся висота = 100% RAM чипа
    colw = 150

    def budget(x, parts, ceiling_frac, label, ok):
        """parts: список (назва, частка_від_повної_висоти, колір)."""
        out = [text(x + colw / 2, base_y + 22, label, size=12, bold=True)]
        # стеля чипа
        cy = base_y - full * ceiling_frac
        out.append(line(x - 20, cy, x + colw + 20, cy, color=POS, sw=2.2, dash="7 4"))
        out.append(text(x + colw + 24, cy + 4, "стеля RAM", size=10, color=POS, anchor="start", bold=True))
        # поверхи знизу вгору
        y = base_y
        for name, frac, col in parts:
            h = full * frac
            out.append(rect(x, y - h, colw, h, fill=col, stroke=LINE, sw=1.3))
            if h > 22:
                out.append(text(x + colw / 2, y - h / 2 + 4, name, size=11, bold=True))
            y -= h
        used_top = y
        # запас або пробій
        if ok:
            out.append(rect(x, cy, colw, used_top - cy, fill="#ffffff", stroke=FIELD, sw=1.6, rx=4))
            out.append(text(x + colw / 2, (cy + used_top) / 2 + 4, "запас", size=11, color=FIELD, bold=True))
            out.append(text(x + colw / 2, top_y - 14, "вміщається ✓", size=12, color=FIELD, bold=True))
        else:
            out.append(text(x + colw / 2, used_top - 8, "пробій ✗", size=12, color=POS, bold=True))
        return out

    left = [(".data+.bss", 0.30, DATABG), ("купа", 0.22, HEAPBG), ("стек", 0.20, STACKBG)]
    P += budget(150, left, 0.92, "вміщається із запасом", ok=True)

    right = [(".data+.bss", 0.42, DATABG), ("купа", 0.34, HEAPBG), ("стек", 0.30, STACKBG)]
    P += budget(560, right, 0.92, "не вміщається", ok=False)

    return render("img/napkin.svg", W, H, *P)


# ── 5. Ручний water-mark: заповнити 0xA5 → попрацювати → просканувати ─────────
# Ідея: три знімки тієї самої стекової ділянки. (1) перед стартом уся залита
# 0xA5. (2) під час роботи стек витоптав верх — там справжні дані, унизу 0xA5
# цілий. (3) скан знизу шукає перший НЕ-0xA5 байт — це й є найглибша межа.
def fig_watermark():
    W, H = 900, 470
    P = [text(W / 2, 30, "Ручний water-mark: фарбуємо 0xA5, працюємо, скануємо", size=17, bold=True),
         text(W / 2, 50, "межа недоторканого 0xA5 = найглибша точка, якої стек сягав",
              size=11, color=MUTED, italic=True)]

    top, bot = 90, 410
    colw = 200
    xs = [70, 350, 630]
    titles = ["1. перед стартом", "2. попрацювало", "3. скан знизу"]
    # частка зверху, яку витоптав стек (справжні дані); решта знизу — цілий 0xA5
    used = [0.0, 0.55, 0.55]
    PAT = "#fdf6e3"   # незаймана 0xA5-ділянка (тепла)
    USED = "#e8eef9"  # витоптано (справжні дані)

    for x, title, u in zip(xs, titles, used):
        P.append(text(x + colw / 2, top - 12, title, size=12, bold=True))
        P.append(rect(x, top, colw, bot - top, fill="#ffffff", stroke=LINE, sw=2, rx=8))
        P.append(text(x - 6, top + 12, "вершина", size=9, color=GREY, anchor="end"))
        P.append(text(x - 6, bot - 4, "дно", size=9, color=GREY, anchor="end"))
        split = top + (bot - top) * u
        if u > 0:
            P.append(rect(x + 5, top + 5, colw - 10, split - top - 5, fill=USED, stroke=NEG, sw=1.2))
            P.append(text(x + colw / 2, (top + split) / 2 + 4, "справжні дані", size=11, color=NEG, bold=True))
            P.append(text(x + colw / 2, (top + split) / 2 + 20, "(стек витоптав)", size=9, color=GREY))
        # незаймана 0xA5
        P.append(rect(x + 5, split, colw - 10, bot - split - 5, fill=PAT, stroke=FIELD, sw=1.2))
        P.append(text(x + colw / 2, (split + bot) / 2, "0xA5 0xA5 0xA5", size=11, color=FIELD, bold=True))
        P.append(text(x + colw / 2, (split + bot) / 2 + 16, "цілий візерунок", size=9, color=GREY))

    # на третьому стовпі — стрілка скану знизу вгору й позначка межі
    x = xs[2]
    split = top + (bot - top) * used[2]
    P.append(arrow(x + colw + 18, bot - 6, x + colw + 18, split, color=POS, sw=2.2))
    P.append(text(x + colw + 24, (split + bot) / 2, "скан ↑", size=10, color=POS, anchor="start", bold=True))
    P.append(line(x - 4, split, x + colw + 4, split, color=POS, sw=2.4, dash="6 4"))
    P.append(text(x + colw / 2, split - 8, "найглибша межа", size=11, color=POS, bold=True))

    P.append(fitbox(70, bot + 22, W - 140, 44,
                    "Перший НЕ-0xA5 байт від дна — це межа: усе нижче стек ніколи не чіпав.\n"
                    "Відстань від дна до межі = непочатий запас; решта до вершини — пік ужитого стека.",
                    fill="#ffffff", stroke=POS, size=11))
    return render("img/watermark.svg", W, H, *P)


# ── 6. Запас понад виміряне: пік + переривання + майбутня правка ──────────────
# Ідея: горизонтальний «термометр» однієї стекової ділянки. Зліва направо росте
# глибина. Позначки: виміряний пік (звичайний прогін) → переривання додає згори
# → завтрашня глибша гілка → і лише тоді стеля. Запас = відстань до стелі.
def fig_headroom():
    W, H = 900, 360
    P = [text(W / 2, 30, "Запас закладай ПОНАД виміряне", size=17, bold=True),
         text(W / 2, 50, "вимір — лише те, що відпрацювало; реальний пік завжди глибший",
              size=11, color=MUTED, italic=True)]

    x0, x1 = 70, 830
    y = 150
    bar_h = 64
    full = x1 - x0
    P.append(text(x0, y - 16, "дно стека", size=10, color=GREY, anchor="start"))
    P.append(text(x1, y - 16, "стеля (кінець ділянки)", size=10, color=POS, anchor="end", bold=True))

    # сегменти глибини (частки повної ширини)
    segs = [
        ("виміряний пік", 0.46, "#e8eef9", NEG),
        ("+ переривання", 0.16, "#fff4e0", "#b8860b"),
        ("+ глибша гілка завтра", 0.16, "#fdecea", POS),
    ]
    x = x0
    for name, frac, col, edge in segs:
        w = full * frac
        P.append(rect(x, y, w, bar_h, fill=col, stroke=edge, sw=1.6))
        P.append(fitbox(x, y + bar_h + 6, w, 34, name, fill="#ffffff", stroke=edge, size=10, bold=True))
        x += w
    used_end = x
    # запас
    P.append(rect(used_end, y, x1 - used_end, bar_h, fill="#ffffff", stroke=FIELD, sw=1.8, rx=4))
    P.append(text((used_end + x1) / 2, y + bar_h / 2 + 4, "ЗАПАС", size=12, color=FIELD, bold=True))
    P.append(text((used_end + x1) / 2, y + bar_h + 18, "(подушка)", size=10, color=FIELD))
    # стеля
    P.append(line(x1, y - 6, x1, y + bar_h + 6, color=POS, sw=2.6))

    P.append(fitbox(70, 270, W - 140, 56,
                    "Вимір water-mark показує лише ті гілки, що встигли відпрацювати під час прогону.\n"
                    "Переривання приходить поверх стека задачі, що саме виконувалась; завтрашня правка додасть рівень викликів.\n"
                    "Тому до виміряного піка додають подушку — тримати зайнятим ≲70–80% ділянки.",
                    fill="#ffffff", stroke=POS, size=11))
    return render("img/headroom.svg", W, H, *P)


# ════════ вставка hist-bss-name ════════════════════════════════════════════════

# ── h1. IBM 704: машина й числа її епохи ──────────────────────────────────────
# Ідея: машина-кімната проти сьогоднішнього буфера. Три коштовні факти про 704
# (лампи, 36-біт слово, лише 4096 слів = ~18 КБ) — і шпилька: один буфер у .bss
# сьогодні більший за всю пам'ять цього велетня.
def fig_ibm704():
    W, H = 880, 420
    P = [text(W / 2, 30, "IBM 704 (1954): світ, де народилося слово «bss»", size=17, bold=True),
         text(W / 2, 50, "кожне з 4096 слів пам'яті — на вагу золота, тож пам'ять рахували поштучно",
              size=11, color=MUTED, italic=True)]

    # ліворуч — «машина-кімната» з трьома фактами
    mx, mtop = 60, 90
    mw, mh = 360, 250
    P.append(rect(mx, mtop, mw, mh, fill=FLASHBG, stroke=LINE, sw=2, rx=12))
    P.append(text(mx + mw / 2, mtop - 10, "Вершина обчислень середини 1950-х", size=12, bold=True))
    facts = [
        ("рахує на ЕЛЕКТРОННИХ ЛАМПАХ", "транзистор у комп'ютерах щойно зароджувався"),
        ("слово завдовжки 36 бітів", "пам'ять мірялася словами, не байтами"),
        ("уся пам'ять — лише 4096 слів", "≈ 18 КБ на феритових осердях"),
    ]
    fy = mtop + 18
    for head, sub in facts:
        P.append(fitbox(mx + 16, fy, mw - 32, 62, head + "\n" + sub,
                        fill="#ffffff", stroke=LINE, size=12, bold=True))
        fy += 74

    # праворуч — сьогоднішній буфер для контрасту
    bx, btop = 500, 130
    bw, bh = 320, 170
    P.append(rect(bx, btop, bw, bh, fill=BSSBG, stroke=PURPLE, sw=2, rx=12))
    P.append(text(bx + bw / 2, btop - 10, "Сьогодні: один буфер у .bss", size=12, color=PURPLE, bold=True))
    P.append(fitbox(bx + 16, btop + 16, bw - 32, 64,
                    "uint8_t буфер[1024];\nви кладете його, не думаючи",
                    fill="#ffffff", stroke=PURPLE, size=13, bold=True))
    P.append(fitbox(bx + 16, btop + 92, bw - 32, 62,
                    "1024 байти НЕ вмістилися б\nу пам'ять 704 й наполовину",
                    fill="#fdecea", stroke=POS, size=12, bold=True))

    # стрілка-порівняння
    P.append(arrow(mx + mw, mtop + mh - 40, bx, btop + bh - 40, color=POS, sw=2))
    P.append(text((mx + mw + bx) / 2, mtop + mh - 16, "та сама потреба — ощаджувати пам'ять",
                  size=11, color=POS, bold=True))
    return render("img/ibm704.svg", W, H, *P)


# ── h2. Родовід слова: BSS → FAP/MAP → .bss ──────────────────────────────────
# Ідея: горизонтальний ланцюг ланок, кожна підписана «що» і «чому перейшло».
# Наскрізна теза внизу: переходило на сумісності й звичці, бо РІЧ не зникала.
def fig_lineage():
    W, H = 940, 360
    P = [text(W / 2, 30, "Родовід трьох літер: від IBM 704 до вашого ARM", size=17, bold=True),
         text(W / 2, 50, "слово переходило з покоління в покоління на самій сумісності — бо потреба не зникала",
              size=11, color=MUTED, italic=True)]

    y = 150
    bw, bh = 200, 96
    gap = 30
    xs = [40, 40 + bw + gap, 40 + 2 * (bw + gap), 40 + 3 * (bw + gap)]
    stages = [
        ("UA-SAP", "псевдооперація BSS\nIBM 704 · сер. 1950-х\nНатт, Реймшоу та ін.", FLASHBG, LINE),
        ("FAP / MAP", "асемблери IBM\nдля 709 та 7090/7094\nназву взяли як є", "#eef2f7", LINE),
        ("Unix / C", "секція .bss\nнеініціалізовані\nстатичні дані", "#e9f7ef", FIELD),
        ("GCC сьогодні", "стовпчик bss\nу звіті size\nна ARM-МК", BSSBG, PURPLE),
    ]
    for (head, body, fill, edge), x in zip(stages, xs):
        P.append(rect(x, y, bw, bh, fill=fill, stroke=edge, sw=2, rx=10))
        P.append(text(x + bw / 2, y + 22, head, size=13, color=edge if edge != LINE else INK, bold=True))
        P.append(mtext(x + bw / 2, y + 42, body, size=10.5, color=INK))

    for i in range(len(xs) - 1):
        P.append(arrow(xs[i] + bw, y + bh / 2, xs[i + 1], y + bh / 2, color=POS, sw=2.4))

    P.append(fitbox(40, y + bh + 36, W - 80, 44,
                    "На кожному стрибку інженери НЕ вигадували нову назву — успадковували готову, бо вже мали під неї код і звичку.\n"
                    "А називана річ — «зарезервувати пам'ять без початкових значень» — є в КОЖНІЙ машині, від лампового велетня до МК.",
                    fill="#ffffff", stroke=POS, size=11))
    return render("img/lineage.svg", W, H, *P)


# ── h3. Що робила псевдооперація BSS: резервує, але не заповнює ───────────────
# Ідея: ліворуч BSS — відкладає блок ПОРОЖНІХ комірок під символ. Праворуч
# псевдооперація даних — і резервує, І заповнює числами. Та сама межа = .bss/.data.
def fig_bss_op():
    W, H = 900, 420
    P = [text(W / 2, 30, "Що робила BSS: «Block Started by Symbol»", size=17, bold=True),
         text(W / 2, 50, "відкладала блок під символ — але НЕ клала в нього жодних значень",
              size=11, color=MUTED, italic=True)]

    cell = 38
    n = 5
    grid_w = n * cell

    def cells(x, y, filled, col_edge, values=None):
        out = []
        for i in range(n):
            cx = x + i * cell
            out.append(rect(cx, y, cell, cell, fill=("#ffffff" if not filled else "#fff4e0"),
                            stroke=col_edge, sw=1.4, rx=3))
            if filled and values:
                out.append(text(cx + cell / 2, y + cell / 2 + 5, values[i], size=12, bold=True))
        return out

    # ── ліворуч: BSS — порожній блок ──
    lx, ly = 80, 130
    P.append(text(lx + grid_w / 2, ly - 16, "BSS ім'я, 5", size=13, color=PURPLE, bold=True))
    P += cells(lx, ly, filled=False, col_edge=PURPLE)
    P.append(text(lx + grid_w / 2, ly + cell + 28, "відклала 5 слів під «ім'я»", size=11, bold=True))
    P.append(text(lx + grid_w / 2, ly + cell + 46, "комірки ПОРОЖНІ — нічого не записано", size=10, color=GREY))
    P.append(fitbox(lx - 4, ly + cell + 64, grid_w + 8, 56,
                    "сьогодні це → .bss\nмісце є, даних нема\n(у Flash коштує 0)",
                    fill=BSSBG, stroke=PURPLE, size=11, bold=True))

    # ── праворуч: псевдооперація даних — блок із числами ──
    rx2, ry = 520, 130
    P.append(text(rx2 + grid_w / 2, ry - 16, "DEC 7,3,0,9,1", size=13, color=POS, bold=True))
    P += cells(rx2, ry, filled=True, col_edge=POS, values=["7", "3", "0", "9", "1"])
    P.append(text(rx2 + grid_w / 2, ry + cell + 28, "відклала 5 слів І заповнила їх", size=11, bold=True))
    P.append(text(rx2 + grid_w / 2, ry + cell + 46, "значення зберігаються в програмі", size=10, color=GREY))
    P.append(fitbox(rx2 - 4, ry + cell + 64, grid_w + 8, 56,
                    "сьогодні це → .data\nі місце, і початкові дані\n(значення лежать у Flash)",
                    fill=DATABG, stroke=POS, size=11, bold=True))

    P.append(fitbox(80, 350, W - 160, 44,
                    "Symbol = ім'я-мітка ділянки · Block = суцільний блок слів.   "
                    "Уся різниця між BSS і командою даних — чи кладемо в блок значення; це й є сьогоднішня межа між .bss і .data.",
                    fill="#ffffff", stroke=LINE, size=11))
    return render("img/bss-op.svg", W, H, *P)


if __name__ == "__main__":
    paths = [fig_two_memories(), fig_sections(), fig_squeeze(), fig_napkin(),
             fig_watermark(), fig_headroom(),
             fig_ibm704(), fig_lineage(), fig_bss_op()]
    for p in paths:
        print("wrote", p)
