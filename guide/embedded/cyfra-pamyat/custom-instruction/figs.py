# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SW   = "#2457d6"   # суто софт (послідовно)
CI   = "#1f8a3b"   # кастомна інструкція (золота середина)
HW   = "#c0392b"   # окремий апаратний прискорювач


# ── spectrum: три точки на осі «софт - кастомна інструкція - окреме залізо» ────
# Ідея: кастомна інструкція — золота середина між «усе кодом» і «окремий блок
# на шині». Показуємо, що вона дає, і чим платить кожна крайність.

def fig_spectrum():
    W = 780
    cw, ch = 232, 196
    gap = 24
    x0 = (W - 3 * cw - 2 * gap) / 2
    top = 78
    p = [text(W/2, 32, "Три способи зробити операцію швидше", size=17, bold=True),
         text(W/2, 52, "кастомна інструкція — золота середина між «усе кодом» і «окремий блок на шині»",
              size=11.5, color=MUTED, italic=True)]

    cards = [
        (SW, "Суто програмно",
         ["операція = багато",
          "тактів ядра поспіль",
          "",
          "+ нуль заліза, гнучко",
          "− повільно на гарячій",
          "  внутрішній петлі"]),
        (CI, "Кастомна інструкція",
         ["своя логіка ВСЕРЕДИНІ",
          "конвеєра ядра",
          "",
          "+ 1-2 такти, як рідна",
          "+ без шини й DMA",
          "− треба міняти ядро"]),
        (HW, "Окремий прискорювач",
         ["блок на шині поряд",
          "з ядром, свій інтерфейс",
          "",
          "+ величезний потік",
          "− такти на шину туди-сюди",
          "− складна синхронізація"]),
    ]
    for i, (col, title, lines) in enumerate(cards):
        x = x0 + i * (cw + gap)
        fill = {SW: "#f3f5fd", CI: "#eef7ee", HW: "#fdecea"}[col]
        p.append(rect(x, top, cw, ch, fill=fill, stroke=col, sw=2))
        p.append(rect(x, top, cw, 30, fill=col, sw=0, rx=6))
        p.append(text(x + cw/2, top + 20, title, size=12.5, color="#ffffff", bold=True))
        ty = top + 52
        for ln in lines:
            isplus = ln.strip().startswith("+")
            ismin  = ln.strip().startswith("−") or ln.startswith("  ")
            c = CI if isplus else (POS if ismin else INK)
            b = isplus or (ln.strip().startswith("−"))
            p.append(text(x + 14, ty, ln, size=10.5, color=c, anchor="start", bold=b))
            ty += 19

    # вісь під картками: послідовно -> у конвеєрі -> на шині
    ay = top + ch + 30
    p.append(line(x0, ay, x0 + 3*cw + 2*gap, ay, color=MUTED, sw=1.4))
    p.append(text(x0 + cw/2, ay + 18, "найдешевше залізо", size=10, color=MUTED, italic=True))
    p.append(text(x0 + cw + gap + cw/2, ay + 18, "найщільніше з ядром", size=10, color=CI, italic=True, bold=True))
    p.append(text(x0 + 2*(cw+gap) + cw/2, ay + 18, "найбільший потік", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "spectrum.svg"), W, ay + 40, *p)


# ── datapath: як кастомна інструкція влазить у тракт ядра ──────────────────────
# Ідея (центральна): декодер ловить зарезервований опкод, бере до 2 регістрів-
# джерел, проганяє крізь ВЛАСНУ логіку поряд з ALU, кладе результат у регістр.
# Все за один прохід конвеєра — як рідна інструкція.

def fig_datapath():
    W, H = 780, 430
    p = [text(W/2, 30, "Куди вмикається кастомна інструкція", size=17, bold=True),
         text(W/2, 50, "декодер ловить свій опкод; логіка читає регістри, рахує, пише результат — за один прохід",
              size=11, color=MUTED, italic=True)]

    # регістровий файл
    rfx, rfy, rfw, rfh = 40, 150, 150, 130
    p.append(rect(rfx, rfy, rfw, rfh, fill="#eef0f4", stroke=INK, sw=1.8))
    p.append(text(rfx + rfw/2, rfy + 22, "Регістровий", size=12, bold=True))
    p.append(text(rfx + rfw/2, rfy + 38, "файл", size=12, bold=True))
    p.append(text(rfx + rfw/2, rfy + 64, "rs1, rs2 -> ...", size=10.5, color=MUTED))
    p.append(text(rfx + rfw/2, rfy + 84, "... -> rd", size=10.5, color=MUTED))

    # декодер зверху
    dcx, dcy, dcw, dch = 270, 76, 240, 42
    p.append(rect(dcx, dcy, dcw, dch, fill="#fff8e6", stroke="#b8860b", sw=1.8))
    p.append(text(dcx + dcw/2, dcy + 18, "Декодер інструкції", size=11.5, bold=True))
    p.append(text(dcx + dcw/2, dcy + 34, "побачив зарезервований опкод", size=10, color="#8a6d00", italic=True))

    # ALU
    alx, aly, alw, alh = 300, 168, 180, 64
    p.append(rect(alx, aly, alw, alh, fill="#f3f5fd", stroke=SW, sw=1.8))
    p.append(text(alx + alw/2, aly + 26, "Штатний ALU", size=12, color=SW, bold=True))
    p.append(text(alx + alw/2, aly + 44, "+  −  &  |  <<", size=10.5, color=MUTED))

    # кастомний блок
    cbx, cby, cbw, cbh = 300, 252, 180, 70
    p.append(rect(cbx, cby, cbw, cbh, fill="#eef7ee", stroke=CI, sw=2.2))
    p.append(text(cbx + cbw/2, cby + 24, "ВАША логіка", size=12.5, color=CI, bold=True))
    p.append(text(cbx + cbw/2, cby + 42, "комбінаційна або", size=10, color=INK))
    p.append(text(cbx + cbw/2, cby + 56, "на кілька тактів", size=10, color=INK))

    # мультиплексор вибору результату
    mxx, mxy, mxw, mxh = 540, 196, 70, 96
    p.append(rect(mxx, mxy, mxw, mxh, fill="#eef0f4", stroke=INK, sw=1.7, rx=4))
    p.append(text(mxx + mxw/2, mxy + 44, "mux", size=12, bold=True))
    p.append(text(mxx + mxw/2, mxy + 62, "вибір", size=9.5, color=MUTED))

    # назад у регістр
    rbx, rby, rbw, rbh = 660, 198, 96, 92
    p.append(rect(rbx, rby, rbw, rbh, fill="#eef0f4", stroke=INK, sw=1.8))
    p.append(text(rbx + rbw/2, rby + 40, "запис", size=11.5, bold=True))
    p.append(text(rbx + rbw/2, rby + 58, "у rd", size=11, color=MUTED))

    # стрілки: регістри -> ALU і -> кастом
    p.append(arrow(rfx + rfw, rfy + 40, alx, aly + 24, color=INK, sw=1.7))
    p.append(arrow(rfx + rfw, rfy + 90, cbx, cby + 30, color=CI, sw=2))
    p.append(text(rfx + rfw + 26, rfy + 24, "rs1, rs2", size=10, color=INK, anchor="start", bold=True))

    # декодер вмикає кастомний блок (вертикальна стрілка вниз)
    p.append(line(dcx + dcw/2, dcy + dch, dcx + dcw/2, cby - 6, color="#b8860b", sw=1.5, dash="5 3"))
    p.append(arrow(dcx + dcw/2, cby - 18, cbx + cbw/2, cby - 6, color="#b8860b", sw=1.5))
    p.append(text(dcx + dcw/2 + 8, aly - 4, "вмикає саме ваш блок", size=9.5, color="#8a6d00", anchor="start", italic=True))

    # ALU і кастом -> mux
    p.append(arrow(alx + alw, aly + 32, mxx, mxy + 28, color=SW, sw=1.6))
    p.append(arrow(cbx + cbw, cby + 35, mxx, mxy + 70, color=CI, sw=2))
    # mux -> запис
    p.append(arrow(mxx + mxw, mxy + 48, rbx, rby + 46, color=INK, sw=1.7))
    # запис -> назад у регістровий файл (петля знизу)
    p.append(line(rbx + rbw/2, rby + rbh, rbx + rbw/2, 360, color=INK, sw=1.5))
    p.append(line(rbx + rbw/2, 360, rfx + rfw/2, 360, color=INK, sw=1.5))
    p.append(arrow(rfx + rfw/2, 360, rfx + rfw/2, rfy + rfh, color=INK, sw=1.5))
    p.append(text((rfx + rbx)/2, 354, "результат повертається у регістр — як після звичайної інструкції",
                  size=9.5, color=MUTED, italic=True))

    box = fitbox(40, 376, W-80, 44,
                 "Ключове: ваш блок сидить ПОРЯД з ALU всередині того самого ядра й користується тими "
                 "самими регістрами. Ні шини, ні DMA — лише ще один шлях обчислення.",
                 size=11, pad=10, fill="#f4f7f4", stroke=CI, sw=1.7, bold=True)
    p.append(box)
    render(os.path.join(OUT, "datapath.svg"), W, 430, *p)


# ── cycles: та сама дрібна операція — цикл проти однієї інструкції ─────────────
# Ідея: конкретні числа. Підрахунок одиничних бітів 32-розрядного слова: софтова
# петля — десятки тактів; одна кастомна інструкція popcount — один такт.

def fig_cycles():
    W, H = 780, 330
    bx, bw = 250, 460
    p = [text(W/2, 30, "Підрахунок одиничних бітів 32-розрядного слова", size=17, bold=True),
         text(W/2, 50, "порядок тактів на одну операцію — менше краще", size=11.5, color=MUTED, italic=True)]

    bars = [
        ("Софтова петля по бітах", SW, 1.00, "≈ 32 ітерації × кілька тактів → десятки тактів"),
        ("Софт, трюк-таблиця",     SW, 0.34, "кілька звернень до RAM + зсуви → одиниці-десятки"),
        ("Кастомна popcount",      CI, 0.05, "1 такт: усе порахувала схема в тракті ядра"),
    ]
    y = 92
    for label, col, frac, note in bars:
        fill = "#eef7ee" if col == CI else "#f3f5fd"
        p.append(text(bx - 14, y + 24, label, size=11.5, color=col, anchor="end", bold=True))
        p.append(rect(bx, y, max(bw*frac, 10), 38, fill=fill, stroke=col, sw=1.9))
        p.append(text(bx + max(bw*frac, 10) + 12, y + 24, note, size=10, anchor="start"))
        y += 70

    p.append(line(bx, y + 2, bx + bw, y + 2, color=MUTED, sw=1.3, dash="4 3"))
    p.append(arrow(bx, y + 2, bx + bw, y + 2, color=MUTED, sw=1.3))
    p.append(text(bx, y + 20, "-> більше тактів", size=10, color=MUTED, anchor="start", italic=True))

    box = fitbox(40, y + 36, W-80, 44,
                 "Виграш у рази дає не «швидший код», а перенос самої петлі в залізо: те, що ядро "
                 "робило бітами поспіль, схема рахує за один прохід.",
                 size=11, pad=10, fill="#f4f7f4", stroke=CI, sw=1.7, bold=True)
    p.append(box)
    render(os.path.join(OUT, "cycles.svg"), W, y + 96, *p)


# ── encoding: R-формат кастомної команди; одне кодування по обидва боки стіни ──
# Ідея (для вставки proj): опкод custom-0 задає БЛОК, funct3+funct7 — конкретну
# команду; ці самі біти мусять збігтися в HDL-декодері й в асемблері, інакше
# «компілюється, але дає сміття». Червона нитка внизу — головна пастка.

def fig_encoding():
    W = 820
    p = [text(W/2, 30, "Кодування кастомної popcount у R-форматі RISC-V", size=17, bold=True),
         text(W/2, 50, "опкод custom-0 задає блок; funct3+funct7 — конкретну команду в блоці",
              size=11.5, color=MUTED, italic=True)]

    # поля R-формату пропорційно до бітів (32 біти на bw px)
    bx, bw = 40, W - 80
    fy, fh = 74, 56
    fields = [  # (назва, біти, значення, колір-акцент)
        ("funct7", 7, "0000000", CI),
        ("rs2",    5, "(не треба)", MUTED),
        ("rs1",    5, "x = вхід", INK),
        ("funct3", 3, "000", CI),
        ("rd",     5, "результат", INK),
        ("opcode", 7, "0001011", POS),
    ]
    x = bx
    for name, bits, val, col in fields:
        w = bw * bits / 32.0
        fill = "#eef7ee" if col == CI else ("#fdecea" if col == POS else "#eef0f4")
        p.append(rect(x, fy, w, fh, fill=fill, stroke=col, sw=2 if col in (CI, POS) else 1.5))
        p.append(text(x + w/2, fy + 19, name, size=11.5, bold=True, color=col))
        p.append(text(x + w/2, fy + 35, "%d біт" % bits, size=9.5, color=MUTED))
        vs = fit_font(val, w - 6, 10)
        p.append(text(x + w/2, fy + 50, val, size=vs, color=col if col != MUTED else MUTED))
        x += w
    # шкала бітів під полями
    p.append(text(bx, fy + fh + 14, "31", size=9, color=MUTED, anchor="start"))
    p.append(text(bx + bw, fy + fh + 14, "0", size=9, color=MUTED, anchor="end"))

    # повний 32-бітний код
    cy = fy + fh + 40
    p.append(text(W/2, cy, "32 біти разом = 0x0005050B  (popcount a0, a0)",
                  size=13, bold=True, color=INK))

    # дві стіни + червона нитка «мусить збігтися»
    ty = cy + 30
    half = (bw - 30) / 2
    hh = 58
    p.append(rect(bx, ty, half, hh, fill="#f3f5fd", stroke=SW, sw=1.8))
    p.append(text(bx + half/2, ty + 22, "Залізо (HDL-декодер)", size=12, bold=True, color=SW))
    p.append(text(bx + half/2, ty + 42, "insn[6:0]==0x0B, funct3==0, funct7==0", size=9.5, color=INK))
    p.append(rect(bx + half + 30, ty, half, hh, fill="#fff8e6", stroke="#b8860b", sw=1.8))
    p.append(text(bx + half + 30 + half/2, ty + 22, "Асемблер (.insn)", size=12, bold=True, color="#8a6d00"))
    p.append(text(bx + half + 30 + half/2, ty + 42, ".insn r 0x0B, 0, 0, ...", size=9.5, color=INK))
    # червона двостороння стрілка-нитка між стінами
    midy = ty + hh/2
    p.append(line(bx + half, midy, bx + half + 30, midy, color=POS, sw=2.4))
    p.append(arrow(bx + half + 30, midy, bx + half + 6, midy, color=POS, sw=2.4))
    p.append(arrow(bx + half, midy, bx + half + 24, midy, color=POS, sw=2.4))

    box = fitbox(bx, ty + hh + 14, bw, 40,
                 "Головна пастка: одне кодування (opcode/funct3/funct7) мусить збігтися "
                 "байт-у-байт по обидва боки. Розійшлося на біт — «компілюється, але дає сміття».",
                 size=11, pad=10, fill="#fdecea", stroke=POS, sw=1.8, bold=True)
    p.append(box)
    render(os.path.join(OUT, "encoding.svg"), W, ty + hh + 14 + 40 + 16, *p)


# ── pcpi-flow: рукостискання PCPI крок за кроком (для вставки proj) ────────────
# Ідея: ядро не впізнало опкод -> пропонує назовні -> наш блок звіряє funct,
# рахує, піднімає ready того ж такту; таймаут 16 тактів -> виняток; багатотактна
# тримає wait, щоб таймаут не спрацював зарано.

def fig_pcpi_flow():
    W = 820
    p = [text(W/2, 30, "Виконання кастомної команди через PCPI (PicoRV32)", size=17, bold=True),
         text(W/2, 50, "ядро пропонує невпізнану команду назовні; наш блок відповідає за такт",
              size=11.5, color=MUTED, italic=True)]

    sx, sw_, sh = 60, W - 120, 44
    gap = 20
    steps = [
        (INK, "1. Декодер ядра не впізнав опкод",
               "не кидає виняток одразу — пропонує команду назовні"),
        (SW,  "2. Ядро: pcpi_valid=1, виставляє insn / rs1 / rs2",
               "повний код команди й уже прочитані операнди — на шину PCPI"),
        (CI,  "3. Наш блок звіряє opcode+funct3+funct7",
               "збіг -> це наша команда; комбінаційно рахує popcount(rs1)"),
        (CI,  "4. Блок: pcpi_rd=результат, pcpi_wr=1, pcpi_ready=1",
               "однотактна -> готово ВЖЕ цього такту, pcpi_wait лишається 0"),
        (INK, "5. Ядро забрало rd і пішло далі — як після рідної команди",
               "результат у регістрі; конвеєр не помітив різниці"),
    ]
    y = 74
    for col, title, note in steps:
        fill = "#eef7ee" if col == CI else ("#f3f5fd" if col == SW else "#eef0f4")
        p.append(rect(sx, y, sw_, sh, fill=fill, stroke=col, sw=2 if col == CI else 1.6))
        p.append(text(sx + 14, y + 19, title, size=11.5, bold=True, color=col, anchor="start"))
        p.append(text(sx + 14, y + 36, note, size=10, color=MUTED, anchor="start"))
        y += sh + gap
    # стрілки вниз між кроками
    ay = 74 + sh
    for _ in range(len(steps) - 1):
        p.append(arrow(sx + sw_/2, ay, sx + sw_/2, ay + gap, color=MUTED, sw=1.5))
        ay += sh + gap

    # рамка-таймаут (червона гілка) під кроками
    ty2 = y + 4
    bh = 60
    box = fitbox(sx, ty2, sw_, bh,
                 ["Таймаут: якщо за 16 тактів ЖОДЕН блок не підняв pcpi_ready —",
                  "команда вважається незаконною й летить виняток.",
                  "Багатотактний блок тримає pcpi_wait, щоб таймаут не спрацював завчасно."],
                 size=11, pad=10, fill="#fdecea", stroke=POS, sw=1.7, bold=True)
    p.append(box)
    render(os.path.join(OUT, "pcpi-flow.svg"), W, ty2 + bh + 16, *p)


if __name__ == "__main__":
    fig_spectrum()
    fig_datapath()
    fig_cycles()
    fig_encoding()
    fig_pcpi_flow()
    print("figs done")
