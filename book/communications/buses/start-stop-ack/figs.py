# -*- coding: utf-8 -*-
"""Фігури до теми «Старт, стоп, ACK/NACK» (I2C).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# локальні відтінки заливок (узгоджені з палітрою svgkit)
F_BLUE  = "#e9eefb"   # під NEG (SCL/адреса/читання)
F_RED   = "#fbecec"   # під POS (СТОП/NACK)
F_GREEN = "#eef6ef"   # під FIELD (СТАРТ/ACK)
F_INK   = "#eef4ff"   # нейтральний (байт даних)
AMBER   = "#b08900"   # повторний старт / проміжний стан
F_AMBER = "#fbf3df"


def clk(f, x0, y_hi, y_lo, n, cyc, color=NEG, sw=2.4, start_low=True):
    """Малює n тактів прямокутного клока від x0. Повертає кінцеву x."""
    x = x0
    lvl = y_lo if start_low else y_hi
    # стартовий рівень
    if start_low:
        f.append(line(x, y_lo, x + cyc * 0.5, y_lo, color=color, sw=sw))
        x += cyc * 0.5
    for i in range(n):
        # підйом
        f.append(line(x, y_lo, x, y_hi, color=color, sw=sw))
        f.append(line(x, y_hi, x + cyc * 0.5, y_hi, color=color, sw=sw))
        x += cyc * 0.5
        # спад
        f.append(line(x, y_hi, x, y_lo, color=color, sw=sw))
        f.append(line(x, y_lo, x + cyc * 0.5, y_lo, color=color, sw=sw))
        x += cyc * 0.5
    return x


# ── 1. Умови СТАРТ і СТОП ────────────────────────────────────────────────────
def fig_startstop():
    W, H = 900, 360
    f = [text(W / 2, 30, "СТАРТ і СТОП: SDA міняється саме тоді, коли SCL високий",
              size=17, bold=True)]
    f.append(text(W / 2, 52, "у спокої обидві лінії високі; СТАРТ — SDA падає при SCL=1; СТОП — SDA піднімається при SCL=1",
                  size=11.5, color=MUTED, italic=True))

    y_hi, y_lo = 110, 150
    sx, ex = 150, 760
    # SCL: спокій-високий, далі кілька тактів, потім знову високий
    f.append(text(sx - 16, (y_hi + y_lo) / 2 + 4, "SCL", size=12.5, color=NEG, bold=True, anchor="end"))
    # ділянка спокою (високо) до старту
    f.append(line(sx, y_hi, 210, y_hi, color=NEG, sw=2.6))
    xend = clk(f, 210, y_hi, y_lo, 4, 80, color=NEG, sw=2.6, start_low=True)
    f.append(line(xend, y_hi, ex, y_hi, color=NEG, sw=2.6))

    # SDA
    y2_hi, y2_lo = 200, 240
    f.append(text(sx - 16, (y2_hi + y2_lo) / 2 + 4, "SDA", size=12.5, color=POS, bold=True, anchor="end"))
    sda = [
        (sx, y2_hi), (210, y2_hi), (210, y2_lo),          # СТАРТ: падіння при високому SCL
        (450, y2_lo), (450, y2_hi), (490, y2_hi),         # дані (умовно)
        (490, y2_lo), (610, y2_lo), (610, y2_hi),
        (xend, y2_hi), (xend, y2_lo), (700, y2_lo),       # тримаємо низько перед стопом
        (700, y2_hi), (ex, y2_hi),                        # СТОП: підйом при високому SCL
    ]
    for i in range(len(sda) - 1):
        f.append(line(sda[i][0], sda[i][1], sda[i + 1][0], sda[i + 1][1], color=POS, sw=2.6))

    # маркери СТАРТ/СТОП
    f.append(line(210, y_hi - 8, 210, y2_lo + 8, color=FIELD, sw=1.4, dash="4,3"))
    f.append(text(210, y_hi - 14, "СТАРТ (S)", size=12, color=FIELD, bold=True))
    f.append(line(700, y_hi - 8, 700, y2_lo + 8, color=POS, sw=1.4, dash="4,3"))
    f.append(text(700, y_hi - 14, "СТОП (P)", size=12, color=POS, bold=True))
    f.append(text(335, y2_lo + 26, "дані: SDA міняється лише при SCL=0", size=10.5, color=MUTED))

    b = fitbox(60, H - 56, W - 120, 40,
               ["СТАРТ «захоплює» шину й починає обмін; СТОП завершує його й відпускає лінію.",
                "Між ними дані змінюються тільки поки SCL низький."],
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "start-stop.svg"), W, H, *f)


# ── 2. Чому СТАРТ/СТОП не сплутати з даними ───────────────────────────────────
def fig_unmistakable():
    W, H = 900, 380
    f = [text(W / 2, 30, "Чому СТАРТ і СТОП неможливо сплутати з даними", size=17, bold=True)]
    f.append(text(W / 2, 52, "звичайний біт міняє SDA при НИЗЬКОМУ такті; СТАРТ/СТОП — навмисно при ВИСОКОМУ",
                  size=11.5, color=MUTED, italic=True))

    # ліва панель — дозволено
    f.append(rect(60, 80, 380, 235, fill=BG, stroke="#e0e0e0", sw=2, rx=12))
    f.append(text(250, 106, "звичайний біт даних", size=13, bold=True))
    yh, yl = 150, 184
    f.append(text(96, 169, "SCL", size=11, color=NEG, bold=True, anchor="end"))
    f.append(line(110, yl, 175, yl, color=NEG, sw=2.4))
    f.append(line(175, yl, 175, yh, color=NEG, sw=2.4))
    f.append(line(175, yh, 240, yh, color=NEG, sw=2.4))
    f.append(line(240, yh, 240, yl, color=NEG, sw=2.4))
    f.append(line(240, yl, 305, yl, color=NEG, sw=2.4))
    f.append(line(305, yl, 305, yh, color=NEG, sw=2.4))
    f.append(line(305, yh, 370, yh, color=NEG, sw=2.4))
    f.append(text(96, 225, "SDA", size=11, color=POS, bold=True, anchor="end"))
    f.append(line(110, 210, 240, 210, color=POS, sw=2.4))
    f.append(line(240, 210, 240, 244, color=POS, sw=2.4))
    f.append(line(240, 244, 370, 244, color=POS, sw=2.4))
    f.append(line(240, 140, 240, 250, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(250, 282, "SDA міняється, поки SCL низький → дозволено",
                  size=10.5, color=MUTED, bold=True))

    # права панель — спецсигнал
    f.append(rect(460, 80, 380, 235, fill=BG, stroke="#e0e0e0", sw=2, rx=12))
    f.append(text(650, 106, "СТАРТ / СТОП", size=13, bold=True, color=FIELD))
    f.append(text(492, 169, "SCL", size=11, color=NEG, bold=True, anchor="end"))
    f.append(line(510, 150, 770, 150, color=NEG, sw=2.4))
    f.append(text(492, 225, "SDA", size=11, color=POS, bold=True, anchor="end"))
    f.append(line(510, 210, 640, 210, color=POS, sw=2.4))
    f.append(line(640, 210, 640, 244, color=POS, sw=2.4))
    f.append(line(640, 244, 770, 244, color=POS, sw=2.4))
    f.append(line(640, 140, 640, 250, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text(650, 282, "SDA міняється, поки SCL ВИСОКИЙ → спецсигнал",
                  size=10.5, color=FIELD, bold=True))

    b = fitbox(60, H - 50, W - 120, 36,
               "Заборонений для даних стан зробили сигналом: жоден легальний біт так не поводиться — тож знаки унікальні.",
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "unmistakable.svg"), W, H, *f)


# ── 3. Дев'ятий такт: ACK / NACK ─────────────────────────────────────────────
def fig_ack():
    W, H = 920, 380
    f = [text(W / 2, 30, "Дев'ятий такт: підтвердження ACK / NACK", size=17, bold=True)]
    f.append(text(W / 2, 52, "після 8 біт даних — ще один такт; приймач тягне SDA вниз = ACK, лишає високим = NACK",
                  size=11.5, color=MUTED, italic=True))

    sx = 130
    cyc = 74
    yh, yl = 116, 152
    f.append(text(sx - 16, (yh + yl) / 2 + 4, "SCL", size=12, color=NEG, bold=True, anchor="end"))
    x = sx
    for i in range(9):
        f.append(line(x, yl, x, yh, color=NEG, sw=2.2))
        f.append(line(x, yh, x + cyc * 0.5, yh, color=NEG, sw=2.2))
        f.append(line(x + cyc * 0.5, yh, x + cyc * 0.5, yl, color=NEG, sw=2.2))
        f.append(line(x + cyc * 0.5, yl, x + cyc, yl, color=NEG, sw=2.2))
        lab = "ACK" if i == 8 else str(8 - i)
        col = FIELD if i == 8 else MUTED
        f.append(text(x + cyc * 0.25, yh - 8, lab, size=9.5, color=col, bold=True))
        x += cyc

    # SDA: 8 біт від передавача (умовний візерунок), тоді ACK = 0
    y2h, y2l = 196, 232
    f.append(text(sx - 16, (y2h + y2l) / 2 + 4, "SDA", size=12, color=POS, bold=True, anchor="end"))
    bits = [1, 0, 1, 0, 0, 1, 0, 1]   # умовні дані
    x = sx
    prev = None
    pts = []
    for i, bv in enumerate(bits):
        yv = y2h if bv else y2l
        if prev is not None and prev != yv:
            pts.append((x, prev)); pts.append((x, yv))
        pts.append((x, yv)); pts.append((x + cyc, yv))
        prev = yv
        x += cyc
    # ACK-такт: лінію тягнуть у 0
    if prev != y2l:
        pts.append((x, prev)); pts.append((x, y2l))
    pts.append((x, y2l)); pts.append((x + cyc, y2l))
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=POS, sw=2.2))

    # підсвітити 9-й такт
    f.append(rect(x, 190, cyc, 48, fill=F_GREEN, stroke=FIELD, sw=1.4, rx=0))
    f.append(text(x + cyc / 2, y2l + 22, "приймач тягне 0 = ACK", size=10.5, color=FIELD, bold=True))
    f.append(text(sx + 4 * cyc, y2l + 22, "8 біт від передавача", size=10.5, color=MUTED))

    b = fitbox(60, H - 56, W - 120, 40,
               ["Кожен байт на I2C — це 9 тактів: 8 даних плюс 1 підтвердження.",
                "ACK (0) — «прийняв, давай далі»; NACK (1, лінію ніхто не тягне) — «ні / досить»."],
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "ack.svg"), W, H, *f)


# ── 4. Хто підтверджує: запис проти читання ──────────────────────────────────
def fig_whoack():
    W, H = 900, 400
    f = [text(W / 2, 30, "Хто підтверджує: при записі — ведений, при читанні — ведучий",
              size=16.5, bold=True)]
    f.append(text(W / 2, 52, "ACK завжди дає ПРИЙМАЧ байта; при читанні ведучий NACK-ом каже «це останній»",
                  size=11.5, color=MUTED, italic=True))

    def cell(x, y, w, label, fill, stroke, col):
        f.append(rect(x, y, w, 44, fill=fill, stroke=stroke, sw=1.8, rx=5))
        f.append(text(x + w / 2, y + 28, label, size=11.5, color=col, bold=True))

    # запис
    f.append(rect(60, 84, 380, 250, fill=BG, stroke="#e0e0e0", sw=2, rx=12))
    f.append(text(250, 110, "ЗАПИС (ведучий пише)", size=12.5, color=FIELD, bold=True))
    cell(90, 150, 90, "дані", F_INK, INK, INK)
    cell(184, 150, 44, "A", F_GREEN, FIELD, FIELD)
    cell(232, 150, 90, "дані", F_INK, INK, INK)
    cell(326, 150, 44, "A", F_GREEN, FIELD, FIELD)
    f.append(text(250, 226, "ведений ACK-ає кожен прийнятий байт", size=11, bold=True))
    f.append(text(250, 248, "(приймач = ведений)", size=10.5, color=MUTED))

    # читання
    f.append(rect(460, 84, 380, 250, fill=BG, stroke="#e0e0e0", sw=2, rx=12))
    f.append(text(650, 110, "ЧИТАННЯ (ведучий читає)", size=12.5, color=NEG, bold=True))
    cell(490, 150, 90, "дані", F_INK, INK, INK)
    cell(584, 150, 44, "A", F_GREEN, FIELD, FIELD)
    cell(632, 150, 90, "дані", F_INK, INK, INK)
    cell(726, 150, 44, "N", F_RED, POS, POS)
    f.append(text(650, 226, "ведучий ACK-ає, щоб просити ще,", size=11, bold=True))
    f.append(text(650, 248, "а NACK-ом каже «досить» перед СТОП", size=11, color=POS, bold=True))
    f.append(text(650, 270, "(приймач = ведучий)", size=10.5, color=MUTED))

    b = fitbox(60, H - 50, W - 120, 36,
               "Правило просте: підтверджує той, хто щойно ПРИЙНЯВ байт; напрямок задає біт R/W.",
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "whoack.svg"), W, H, *f)


# ── 5. Повна проста транзакція запису ────────────────────────────────────────
def fig_transaction():
    W, H = 900, 340
    f = [text(W / 2, 30, "Повна проста транзакція запису: усі «розділові знаки»", size=17, bold=True)]
    f.append(text(W / 2, 52, "СТАРТ · адреса+W · ACK · байт даних · ACK · СТОП", size=11.5, color=MUTED, italic=True))

    y = 130
    blocks = [
        (110, 50, "S", F_GREEN, FIELD, FIELD, "старт"),
        (164, 150, "адреса + W", F_BLUE, NEG, NEG, "кого + напрям"),
        (318, 44, "A", F_GREEN, FIELD, FIELD, "ведений: «ок»"),
        (366, 150, "байт даних", F_INK, INK, INK, "що пишемо"),
        (520, 44, "A", F_GREEN, FIELD, FIELD, "ведений: «ок»"),
        (568, 50, "P", F_RED, POS, POS, "стоп"),
    ]
    for x, w, lab, fill, stroke, col, sub in blocks:
        f.append(rect(x, y, w, 56, fill=fill, stroke=stroke, sw=1.8, rx=5))
        f.append(text(x + w / 2, y + 34, lab, size=11.5, color=col, bold=True))
        f.append(text(x + w / 2, y + 80, sub, size=10, color=col, bold=True))

    f.append(line(110, 108, 700, 108, color=MUTED, sw=1.5))
    f.append(text(700, 100, "час →", size=11, color=MUTED, anchor="start"))

    b = fitbox(60, H - 56, W - 120, 40,
               ["Кожен обмін загорнутий між СТАРТ і СТОП, а кожен байт ведений квитує знаком A.",
                "Читання має ту саму форму — лише з R замість W і даними у зворотний бік."],
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "transaction.svg"), W, H, *f)


# ── 6. Повторний СТАРТ ───────────────────────────────────────────────────────
def fig_repeated_start():
    W, H = 940, 340
    f = [text(W / 2, 30, "Повторний СТАРТ (Sr): змінити напрям, не відпускаючи шину",
              size=16.5, bold=True)]
    f.append(text(W / 2, 52, "написати номер регістра, тоді Sr і читати — без СТОПу між фазами, щоб ніхто не вклинився",
                  size=11.5, color=MUTED, italic=True))

    y = 140
    blocks = [
        (80, 44, "S", F_GREEN, FIELD, FIELD),
        (128, 80, "адр+W", F_BLUE, NEG, NEG),
        (212, 32, "A", F_GREEN, FIELD, FIELD),
        (248, 80, "№ рег.", F_INK, INK, INK),
        (332, 32, "A", F_GREEN, FIELD, FIELD),
        (368, 50, "Sr", F_AMBER, AMBER, AMBER),
        (422, 80, "адр+R", F_BLUE, NEG, NEG),
        (506, 32, "A", F_GREEN, FIELD, FIELD),
        (542, 80, "дані", F_INK, INK, INK),
        (626, 32, "N", F_RED, POS, POS),
        (662, 44, "P", F_RED, POS, POS),
    ]
    for x, w, lab, fill, stroke, col in blocks:
        f.append(rect(x, y, w, 56, fill=fill, stroke=stroke, sw=1.8, rx=5))
        f.append(text(x + w / 2, y + 34, lab, size=11.5, color=col, bold=True))

    f.append(text(393, y - 14, "Sr замість P+S", size=11, color=AMBER, bold=True))
    f.append(line(80, y + 86, 710, y + 86, color=MUTED, sw=1.4))
    f.append(text(310, y + 104, "фаза запису (який регістр)", size=10.5, color=MUTED))
    f.append(text(640, y + 104, "фаза читання (дані звідти)", size=10.5, color=MUTED))

    b = fitbox(60, H - 56, W - 120, 40,
               ["Повторний старт тримає шину «своєю» весь час — «запис-потім-читання» лишається неподільним.",
                "Стояв би тут звичайний СТОП — шина б на мить звільнилася, і хтось міг би вклинитися."],
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "repeated-start.svg"), W, H, *f)


# ── 7. Про що говорить NACK ──────────────────────────────────────────────────
def fig_nack_diag():
    W, H = 900, 360
    f = [text(W / 2, 30, "NACK — корисний сигнал: про що він каже", size=17, bold=True)]
    f.append(text(W / 2, 52, "відсутність ACK означає різне залежно від того, ДЕ вона сталася",
                  size=11.5, color=MUTED, italic=True))

    panels = [
        (60, POS, F_RED, "після АДРЕСИ",
         ["на шині нема пристрою", "з такою адресою"], "→ перевір адресу й дроти"),
        (350, AMBER, F_AMBER, "після байта (запис)",
         ["ведений не може прийняти", "(зайнятий або помилка)"], "→ сповільни чи перевір стан"),
        (640, FIELD, F_GREEN, "від ведучого (читання)",
         ["«це був останній байт,", "далі не треба»"], "→ нормальне завершення"),
    ]
    for x, col, fill, title, lines, foot in panels:
        f.append(rect(x, 90, 200, 180, fill=fill, stroke=col, sw=2, rx=12))
        f.append(text(x + 100, 120, title, size=12, color=col, bold=True))
        for i, ln in enumerate(lines):
            f.append(text(x + 100, 154 + i * 20, ln, size=10.5, color=INK))
        f.append(text(x + 100, 240, foot, size=10, color=MUTED, italic=True))

    b = fitbox(60, H - 56, W - 120, 40,
               ["Реакція на ACK/NACK — основа надійного драйвера: за ними видно і відсутність чіпа, і його стан.",
                "Бібліотеки повертають цей результат (наприклад, код повернення Wire.endTransmission())."],
               size=11.5, fill=F_GREEN, stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "nack-diag.svg"), W, H, *f)


if __name__ == "__main__":
    fig_startstop()
    fig_unmistakable()
    fig_ack()
    fig_whoack()
    fig_transaction()
    fig_repeated_start()
    fig_nack_diag()
    print("OK: 7 figures ->", IMG)
