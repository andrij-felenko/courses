# -*- coding: utf-8 -*-
"""
Фігури для ⚙️ вставки ch25-s7-a-ws2812-timing.md (тема §4.7.7).
Два SVG:
  img/fig-25-7a-1-bit-timing.svg   — точний таймінг бітів WS2812B
  img/fig-25-7a-2-encode-byte.svg  — кодування байта в RMT-символи

Стиль: примітиви з figs.py розділу (без svgkit), щоб не змішувати API.
Нові функції: fig77a_bit_timing(), fig77a_encode_byte()
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Локальна палітра (узгоджена з figs.py розділу) ────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"

# ── Локальні примітиви (стиль figs.py) ────────────────────────────────────────
def _esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _hdr(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )

def _ftr():
    return "</svg>\n"

def _line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')

def _arrow(x1, y1, x2, y2, color=INK, w=2):
    m = {"aInk":INK,"aRed":RED,"aGreen":GREEN,"aBlue":BLUE,"aGrey":GREY}
    mid = {v:k for k,v in m.items()}.get(color,"aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{mid})"/>\n')

def _text(x, y, s, size=13, color=INK, anchor="start", weight="normal", style_="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style_}">{_esc(s)}</text>\n')

def _rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=4):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')

def _poly(points, color=INK, w=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polyline points="{pts}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')

def _save(name, body):
    body += _ftr()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.7a.1 — Точний таймінг біта WS2812B
# ══════════════════════════════════════════════════════════════════════════════
def fig77a_bit_timing():
    W, H = 960, 430
    s = _hdr(W, H)

    # Заголовок
    s += _text(W/2, 30, "Таймінг бітів WS2812B: «0» і «1» — лише тривалість HIGH у вікні ~1.25 мкс",
               16, INK, "middle", "bold")
    s += _text(W/2, 50, "вийшов за допуск ±150 нс — піксель прочитає не той біт; скидання ≥50 мкс «защіпає» кадр",
               10.5, GREY, "middle", style_="italic")

    # --- Загальна шкала осі часу ---
    # Розмістимо два біта і reset праворуч
    OX, OY = 70, 160    # початок осі
    HI = 100            # рівень HIGH (y-координата)
    LO = 160            # рівень LOW (y-координата)

    # Масштаб: 1 мкс = 130px
    SCALE = 130.0

    T0H = 0.4   # мкс
    T0L = 0.85
    T1H = 0.8
    T1L = 0.45
    T   = 1.25  # мкс/біт

    TOL = 0.15  # допуск ±150 нс

    # --- Біт «0» ---
    BIT0_X = OX
    bw0 = T * SCALE  # ширина вікна біта 0

    # хвиля биту «0»
    p0 = [
        (BIT0_X,            LO),
        (BIT0_X,            HI),
        (BIT0_X + T0H*SCALE, HI),
        (BIT0_X + T0H*SCALE, LO),
        (BIT0_X + bw0,      LO),
    ]
    s += _poly(p0, BLUE, 3)

    # підписи T0H / T0L
    x_t0h_mid = BIT0_X + T0H*SCALE/2
    x_t0l_mid = BIT0_X + T0H*SCALE + T0L*SCALE/2
    s += _text(x_t0h_mid, HI - 12, "T0H = 0.4 мкс", 9.5, BLUE, "middle", "bold")
    s += _text(x_t0l_mid, LO + 16, "T0L = 0.85 мкс", 9.5, BLUE, "middle")

    # підпис «0»
    s += _text(BIT0_X + bw0/2, HI - 28, "«0»", 14, BLUE, "middle", "bold")

    # допускові вікна (зелені прямокутники навколо фронтів T0H)
    tol_w = TOL * SCALE
    tol_h = LO - HI + 10
    s += _rect(BIT0_X + T0H*SCALE - tol_w, HI - 5, tol_w*2, tol_h, LGRN, GREEN, 1.5, 3)
    s += _text(BIT0_X + T0H*SCALE, HI - 5, "±150 нс", 8.5, GREEN, "middle")

    # пунктирна межа вікна
    bit0_end = BIT0_X + bw0
    s += _line(bit0_end, HI - 20, bit0_end, LO + 25, FAINT, 1.2, "4,3")

    # --- Відступ між бітами ---
    GAP = 18
    BIT1_X = BIT0_X + bw0 + GAP

    # --- Біт «1» ---
    bw1 = T * SCALE
    p1 = [
        (BIT1_X,             LO),
        (BIT1_X,             HI),
        (BIT1_X + T1H*SCALE, HI),
        (BIT1_X + T1H*SCALE, LO),
        (BIT1_X + bw1,       LO),
    ]
    s += _poly(p1, RED, 3)

    x_t1h_mid = BIT1_X + T1H*SCALE/2
    x_t1l_mid = BIT1_X + T1H*SCALE + T1L*SCALE/2
    s += _text(x_t1h_mid, HI - 12, "T1H = 0.8 мкс", 9.5, RED, "middle", "bold")
    s += _text(x_t1l_mid, LO + 16, "T1L = 0.45 мкс", 9.5, RED, "middle")
    s += _text(BIT1_X + bw1/2, HI - 28, "«1»", 14, RED, "middle", "bold")

    # допускове вікно T1H
    s += _rect(BIT1_X + T1H*SCALE - tol_w, HI - 5, tol_w*2, tol_h, LGRN, GREEN, 1.5, 3)
    s += _text(BIT1_X + T1H*SCALE, HI - 5, "±150 нс", 8.5, GREEN, "middle")

    bit1_end = BIT1_X + bw1

    # --- Reset/latch ---
    RST_GAP = 18
    RST_X = bit1_end + RST_GAP
    RST_W = 200  # px — символічна, означає «≥50 мкс»
    p_rst = [
        (RST_X,           LO),
        (RST_X + RST_W,   LO),
    ]
    s += _poly(p_rst, GREY, 3)
    s += _rect(RST_X, HI, RST_W, LO - HI, FAINT, GREY, 1.2, 0)
    s += _text(RST_X + RST_W/2, (HI + LO)/2 + 5, "reset/latch", 10.5, GREY, "middle", "bold")
    s += _text(RST_X + RST_W/2, (HI + LO)/2 + 20, "≥ 50 мкс LOW", 9.5, GREY, "middle")

    # Загальне вікно біта (пунктир над «0» і над «1»)
    for bx in (BIT0_X, BIT1_X):
        s += _line(bx, HI - 42, bx + T*SCALE, HI - 42, GOLD, 1.4, "5,3")
    s += _text(BIT0_X + T*SCALE/2, HI - 52, "T ≈ 1.25 мкс (вікно біта)", 9.5, "#8a6a14", "middle", "bold")
    s += _text(BIT1_X + T*SCALE/2, HI - 52, "T ≈ 1.25 мкс (вікно біта)", 9.5, "#8a6a14", "middle", "bold")

    # Вісь даних
    s += _text(OX - 8, (HI+LO)/2 + 4, "DATA", 10, INK, "end", "bold")
    s += _line(OX - 4, HI, OX - 4, LO, INK, 1.4)

    # --- Підсумок внизу ---
    s += _rect(80, 300, W - 160, 60, LAMB, GOLD, 1.4, 8)
    s += _text(W/2, 322, "Інформація — у ТРИВАЛОСТІ HIGH, не в рівні сигналу. «0»: короткий HIGH (0.4 мкс);",
               10.5, INK, "middle", "bold")
    s += _text(W/2, 342, "«1»: широкий HIGH (0.8 мкс). Вийшов за допуск ±150 нс — піксель прочитає хибний біт, колір «попливе».",
               10, INK, "middle")

    # --- Легенда кольорів ---
    s += _rect(80, 374, 380, 42, LBLUE, BLUE, 1.3, 6)
    s += _text(270, 400, "Синій: біт «0» (вузький HIGH)", 10, BLUE, "middle")
    s += _rect(480, 374, 380, 42, LRED, RED, 1.3, 6)
    s += _text(670, 400, "Червоний: біт «1» (широкий HIGH)", 10, RED, "middle")

    _save("fig-25-7a-1-bit-timing.svg", s)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.7a.2 — Кодування байта в RMT-символи
# ══════════════════════════════════════════════════════════════════════════════
def fig77a_encode_byte():
    W, H = 960, 440
    s = _hdr(W, H)

    s += _text(W/2, 30, "Один байт каналу → 8 RMT-символів: кожен біт = пара (HIGH, LOW)",
               16, INK, "middle", "bold")
    s += _text(W/2, 50, "функція encodeByte(); старший біт першим (MSB-first); tick = 0.1 мкс → duration у тіках",
               10.5, GREY, "middle", style_="italic")

    # --- Приклад байта G = 0b10110010 ---
    BYTE_VAL = 0b10110010
    BITS = [(BYTE_VAL >> (7 - i)) & 1 for i in range(8)]  # MSB-first

    # --- Ліва частина: клітинки байта ---
    CELL_W = 52
    CELL_H = 42
    BY = 100   # top-y байта
    BX = 50    # left-x

    s += _text(BX + 8*CELL_W/2, BY - 14, "G = 0b10110010  (MSB зліва)", 11, INK, "middle", "bold")

    for i, b in enumerate(BITS):
        cx = BX + i * CELL_W
        fill = LRED if b else LBLUE
        stroke = RED if b else BLUE
        s += _rect(cx, BY, CELL_W, CELL_H, fill, stroke, 2, 4)
        s += _text(cx + CELL_W/2, BY + CELL_H/2 + 6, str(b), 18, RED if b else BLUE, "middle", "bold")

    # підписи позицій
    s += _text(BX + CELL_W*0.5, BY + CELL_H + 16, "b7", 9, GREY, "middle")
    s += _text(BX + CELL_W*7.5, BY + CELL_H + 16, "b0", 9, GREY, "middle")

    # --- Стрілка з підписом encodeByte() ---
    ARR_X1 = BX + 8*CELL_W + 14
    ARR_X2 = ARR_X1 + 60
    ARR_Y  = BY + CELL_H/2
    s += _arrow(ARR_X1, ARR_Y, ARR_X2, ARR_Y, INK, 2.4)
    s += _text((ARR_X1+ARR_X2)/2, ARR_Y - 10, "encodeByte()", 9.5, INK, "middle", "bold")

    # --- Права частина: 8 RMT-символів ---
    SYM_X = ARR_X2 + 14
    SYM_Y  = BY - 10
    SYM_W  = 72   # ширина одного символу (px)
    SYM_H  = 62   # висота блоку символу
    HI_H   = 20   # висота HIGH-частини
    LO_H   = SYM_H - HI_H - 14  # висота LOW-частини
    TICK_H = 8     # висота «тіка»

    for i, b in enumerate(BITS):
        sx = SYM_X + i * SYM_W

        # фон символу
        fill = LRED if b else LBLUE
        stroke = RED if b else BLUE
        s += _rect(sx, SYM_Y, SYM_W - 4, SYM_H, fill, stroke, 1.5, 4)

        # HIGH блок
        hi_w_frac = 8/12 if b else 4/12   # 1: 8 tick HIGH з 12; 0: 4 tick HIGH
        hi_w = (SYM_W - 14) * (8/12 if b else 4/12) * 12/8
        lo_w = (SYM_W - 14) - hi_w

        y_top = SYM_Y + 6
        bar_h = 22
        # HIGH bar
        s += _rect(sx + 5, y_top, (SYM_W - 14) * (hi_w_frac), bar_h, RED if b else BLUE,
                   RED if b else BLUE, 0, 2)
        # LOW bar
        lo_x = sx + 5 + (SYM_W - 14) * hi_w_frac
        lo_w_px = (SYM_W - 14) * (1 - hi_w_frac)
        s += _rect(lo_x, y_top, lo_w_px, bar_h, FAINT, GREY, 0, 2)

        # підпис тіків
        if b:
            tick_txt = "8t+4t"
        else:
            tick_txt = "4t+8t"
        s += _text(sx + (SYM_W-4)/2, y_top + bar_h + 14, tick_txt, 8.5,
                   RED if b else BLUE, "middle", "bold")

    # легенда тіків
    s += _text(SYM_X + 8*SYM_W/2, SYM_Y + SYM_H + 22,
               "tick = 0.1 мкс;  «1»: 8+4 тіки = 0.8+0.4 мкс;  «0»: 4+8 тіки = 0.4+0.8 мкс",
               9.5, INK, "middle")

    # --- Блок знизу: місток до кадру ---
    FRAME_Y = 250
    s += _rect(50, FRAME_Y, W - 100, 56, LGRN, GREEN, 1.5, 8)
    s += _text(W/2, FRAME_Y + 18, "Кадр: encodeByte(G) → encodeByte(R) → encodeByte(B)  ×  N пікселів  → rmtWrite()",
               11, GREEN, "middle", "bold")
    s += _text(W/2, FRAME_Y + 38, "Порядок GRB (не RGB!) і MSB-first — дві типові пастки. CPU складає масив → RMT жене наносекунди.",
               10, INK, "middle")

    # --- Таблиця-пояснення структури rmt_data_t ---
    TBL_Y = 326
    s += _rect(50, TBL_Y, W - 100, 86, "#f8f8ff", INK, 1.3, 8)
    s += _text(W/2, TBL_Y + 18, "Поля rmt_data_t для одного біта:", 11, INK, "middle", "bold")
    cols = [
        ("level0 = 1", "HIGH для duration0"),
        ("duration0", "кількість тіків HIGH"),
        ("level1 = 0", "LOW для duration1"),
        ("duration1", "кількість тіків LOW"),
    ]
    for ci, (field, desc) in enumerate(cols):
        cx = 90 + ci * 215
        s += _rect(cx, TBL_Y + 30, 200, 48, FAINT, GREY, 1.2, 4)
        s += _text(cx + 100, TBL_Y + 46, field, 10.5, BLUE, "middle", "bold")
        s += _text(cx + 100, TBL_Y + 68, desc, 9, INK, "middle")

    # --- Підсумок ---
    s += _rect(50, 424, W - 100, 0, FAINT, FAINT, 0)  # placeholder

    _save("fig-25-7a-2-encode-byte.svg", s)


if __name__ == "__main__":
    fig77a_bit_timing()
    fig77a_encode_byte()
    print("OK — figures for §4.7.7a (WS2812 timing) generated in", OUT)
