# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ENC  = "#c0392b"      # зашифроване — гаряче
ENCF = "#fdecea"
CLR  = "#6b7280"      # чисте — сіре
CLRF = "#eef1f4"
OK   = "#27ae60"
OKF  = "#eafaf0"
BLU  = "#2457d6"
BLUF = "#eaf0fd"


# ── where-the-line-runs: що стандартизовано, а що лишилось власним ───────────
# Ідея: один комплект байтів угорі, три власні шляхи до ключа внизу,
# і горизонтальна межа між ними — це і є вся конструкція CENC.

def fig_line():
    W, H = 1060, 470
    p = []

    # верх: єдиний комплект сегментів
    p.append(fitbox(300, 34, 720, 72,
                    "Один комплект сегментів fMP4 — ті самі байти для всіх пристроїв\n"
                    "медіа зашифроване AES-128 під ключем K, у файлі лежить лише його номер KID",
                    size=15, fill=OKF, stroke=OK, sw=2))

    # межа
    LY = 168
    p.append(line(300, LY, 1020, LY, color=INK, sw=2, dash="8 6"))
    b, _, _ = textbox(150, LY, "МЕЖА CENC\nвище — байти\nоднакові для всіх\nнижче — у кожної\nсистеми своє",
                      size=13, fill="#ffffff", stroke=INK, sw=1.6, color=INK)
    p.append(b)

    cols = [
        (430, "Widevine", "Android, Chrome,\nсмарт-ТВ"),
        (660, "PlayReady", "Windows, Xbox,\nчастина смарт-ТВ"),
        (890, "FairPlay",  "iPhone, iPad,\nApple TV, Safari"),
    ]
    for cx, drm, dev in cols:
        b, w1, h1 = textbox(cx, 250, drm + "\nвласний сервер ліцензій\nі власний доказ довіри",
                            size=13, fill=BLUF, stroke=BLU, sw=1.6, min_w=200)
        p.append(b)
        b, w2, h2 = textbox(cx, 388, dev, size=13, fill=FILL, stroke=LINE, min_w=200)
        p.append(b)
        # пристрій → своя система ліцензій
        p.append(arrow(cx, 388 - h2 / 2 - 4, cx, 250 + h1 / 2 + 6, color=BLU, sw=1.8))
        # система ліцензій → той самий ключ до тих самих байтів
        p.append(arrow(cx, 250 - h1 / 2 - 4, cx, 112, color=ENC, sw=2))
        p.append(text(cx + 26, 150, "K", size=15, color=ENC, bold=True))

    render(os.path.join(OUT, "where-the-line-runs.svg"), W, H, *p)


# ── subsample: чому шифрують не весь семпл ───────────────────────────────────
# Ідея: чисті байти на початку — це те, без чого файл перестає бути файлом.

def fig_subsample():
    W, H = 1060, 430
    p = []

    BY, BH = 96, 66
    X0, XM, X1 = 60, 236, 1000

    p.append(fitbox(X0, BY, XM - X0, BH, "чисті\n32 Б", size=14, fill=CLRF, stroke=CLR, sw=1.8))
    p.append(fitbox(XM, BY, X1 - XM, BH, "зашифровано — тіло зрізу, 48 088 Б",
                    size=16, fill=ENCF, stroke=ENC, sw=2))

    p.append(text((X0 + X1) / 2, BY - 22, "один семпл (закодований кадр) = 48 120 Б",
                  size=14, color=MUTED))

    # що саме лишили чистим
    b, w1, h1 = textbox(190, 268, "4 Б — довжина NAL-одиниці\n1 Б — заголовок NAL\n27 Б — заголовок зрізу",
                        size=13, fill=CLRF, stroke=CLR, sw=1.4)
    p.append(b)
    p.append(arrow(190, 268 - h1 / 2 - 6, 148, BY + BH + 8, color=CLR, sw=1.6))

    b, w2, h2 = textbox(700, 268, "коефіцієнти перетворення й вектори руху —\n"
                                  "єдине, що без ключа не має жодного сенсу",
                        size=13, fill=ENCF, stroke=ENC, sw=1.4)
    p.append(b)
    p.append(arrow(700, 268 - h2 / 2 - 6, 700, BY + BH + 8, color=ENC, sw=1.6))

    p.append(fitbox(60, 348, 940, 56,
                    "Демультиплексор без ключа: знаходить межі одиниць, читає їхні типи,\n"
                    "будує покажчик і перемикає бітрейт — і не бачить ані пікселя",
                    size=14, fill=OKF, stroke=OK, sw=1.8))

    render(os.path.join(OUT, "subsample-layout.svg"), W, H, *p)


# ── pattern: cenc проти cbcs на тому самому діапазоні ────────────────────────
# Ідея: та сама захищена ділянка, удесятеро менше роботи.

def fig_pattern():
    W, H = 1020, 360
    p = []

    N, BW, GAP, X0 = 20, 34, 4, 210

    def row(y, filled):
        out = []
        for i in range(N):
            x = X0 + i * (BW + GAP)
            if filled(i):
                out.append(rect(x, y, BW, 44, fill=ENCF, stroke=ENC, sw=1.8, rx=3))
            else:
                out.append(rect(x, y, BW, 44, fill=CLRF, stroke=CLR, sw=1.2, rx=3))
        return "".join(out)

    p.append(text(X0 + BW / 2, 58, "16 Б", size=11, color=MUTED))

    p.append(row(78, lambda i: True))
    b, _, _ = textbox(110, 100, "cenc\nусі блоки", size=13, fill=FILL, stroke=LINE)
    p.append(b)

    p.append(row(178, lambda i: i % 10 == 0))
    b, _, _ = textbox(110, 200, "cbcs\n1 із 10", size=13, fill=FILL, stroke=LINE)
    p.append(b)

    p.append(text(W / 2, 268, "візерунок: один зашифрований блок по 16 Б, далі дев'ять чистих — і знову",
                  size=14, color=INK))
    p.append(text(W / 2, 302, "робота дешифратора падає приблизно вдесятеро; захищена ділянка та сама",
                  size=14, color=MUTED))

    render(os.path.join(OUT, "pattern-encryption.svg"), W, H, *p)


# ── boxtree: де живе кожен бокс CENC ─────────────────────────────────────────
# Ідея: ліворуч — те, що оголошують раз на доріжку; праворуч — те, що
# повторюється в кожному фрагменті. Стрілка між ними — «типове → уточнення».

def fig_boxtree():
    W, H = 1140, 580
    p = []

    p.append(text(300, 40, "сегмент ініціалізації", size=15, color=MUTED, bold=True))
    p.append(text(850, 40, "медіасегмент", size=15, color=MUTED, bold=True))

    L = [
        (70,  62,  470, 34, "moov", BLUF, BLU),
        (104, 108, 436, 40, "pssh × N — по боксу на кожну систему захисту", FILL, LINE),
        (104, 160, 436, 34, "trak → mdia → minf → stbl → stsd", FILL, LINE),
        (140, 206, 400, 34, "encv — цей код стоїть замість avc1", ENCF, ENC),
        (176, 252, 364, 30, "sinf", ENCF, ENC),
        (212, 294, 328, 32, "frma — справжній код: avc1", FILL, LINE),
        (212, 338, 328, 32, "schm — схема: cbcs, версія 0x00010000", FILL, LINE),
        (212, 382, 328, 30, "schi", FILL, LINE),
        (248, 424, 292, 44, "tenc — типові значення\nна всю доріжку", OKF, OK),
    ]
    for x, y, w, h, s, f, st in L:
        p.append(fitbox(x, y, w, h, s, size=13, fill=f, stroke=st, sw=1.6))

    R = [
        (620, 62,  470, 34, "moof", BLUF, BLU),
        (654, 108, 436, 30, "traf", FILL, LINE),
        (688, 150, 402, 34, "saiz — розмір запису на кожен семпл", FILL, LINE),
        (688, 196, 402, 34, "saio — зсув, за яким ці записи лежать", FILL, LINE),
        (688, 242, 402, 46, "senc — початкове значення\nі пари «чисто / захищено» на семпл", OKF, OK),
        (688, 300, 402, 34, "pssh — лише коли ключ міняють у польоті", FILL, LINE),
        (620, 356, 470, 40, "mdat — самі семпли, зашифровані частково", ENCF, ENC),
    ]
    for x, y, w, h, s, f, st in R:
        p.append(fitbox(x, y, w, h, s, size=13, fill=f, stroke=st, sw=1.6))

    p.append(arrow(544, 446, 684, 272, color=OK, sw=2))

    p.append(fitbox(70, 490, 1020, 60,
                    "tenc каже те, що справджується майже завжди; senc уточнює те, що на кожному семплі своє.\n"
                    "saiz і saio — загальний механізм файлу: вони лише кажуть, де й якого розміру ці записи.",
                    size=13, fill=FILL, stroke=LINE, sw=1.6))

    render(os.path.join(OUT, "cenc-box-tree.svg"), W, H, *p)


# ── keystream-state: що переживає стрибок через чисті байти ─────────────────
# Ідея: в cenc потік гами один на весь семпл і проходить крізь чисті ділянки,
# у cbcs кожна захищена ділянка починає власний ланцюг від того самого IV.

def fig_state():
    W, H = 1060, 450
    p = []

    SY, SH = 76, 46
    strip = [(60, 110, False, "чисто"), (170, 250, True, "захищено"),
             (420, 80, False, "чисто"), (500, 250, True, "захищено"),
             (750, 70, False, "чисто"), (820, 180, True, "захищено")]

    p.append(text(530, 54, "один семпл: пари «чисто / захищено», прочитані з senc",
                  size=14, color=MUTED))
    for x, w, enc, lab in strip:
        if enc:
            p.append(fitbox(x, SY, w, SH, lab, size=14, fill=ENCF, stroke=ENC, sw=1.8))
        else:
            p.append(fitbox(x, SY, w, SH, lab, size=13, fill=CLRF, stroke=CLR, sw=1.4))

    p.append(text(60, 158, "cenc — один потік гами на весь семпл",
                  size=14, color=ENC, anchor="start", bold=True))
    for x, w, lab in ((170, 250, "блоки гами 0 … 6"),
                      (500, 250, "далі 6 … 13"),
                      (820, 180, "далі 13 … 17")):
        p.append(fitbox(x, 176, w, 44, lab, size=13, fill=ENCF, stroke=ENC, sw=1.6))
    p.append(line(420, 198, 500, 198, color=ENC, sw=1.6, dash="5 4"))
    p.append(line(750, 198, 820, 198, color=ENC, sw=1.6, dash="5 4"))
    p.append(text(60, 254, "потік не переривається: чисті байти його не рухають,",
                  size=13, color=MUTED, anchor="start"))
    p.append(text(60, 276, "а недобрана решта блока гами дістається наступній ділянці",
                  size=13, color=MUTED, anchor="start"))

    p.append(text(60, 330, "cbcs — свій ланцюг на кожній захищеній ділянці",
                  size=14, color=BLU, anchor="start", bold=True))
    for x, w in ((170, 250), (500, 250), (820, 180)):
        p.append(fitbox(x, 348, w, 44, "IV → ланцюг з нуля", size=13,
                        fill=BLUF, stroke=BLU, sw=1.6))
    p.append(text(60, 426, "IV той самий для всіх ділянок — сталий, узятий із tenc",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "keystream-state.svg"), W, H, *p)


fig_line()
fig_subsample()
fig_pattern()
fig_boxtree()
fig_state()
print("ok")
