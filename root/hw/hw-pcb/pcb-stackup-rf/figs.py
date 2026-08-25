# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"   # мідь: доріжки, майданчики, стінки отвору
COPDK  = "#8a561f"   # темніший обрис міді
CORE   = "#d8c98a"   # склоепоксидне осердя (FR-4), скол у розрізі

SIG    = "#c0392b"   # доріжка/провідник сигналу (гарячий)
WAVE   = "#2457d6"   # хвиля напруги
GND    = "#444a52"   # опорна земля


# ── rlgc-ladder: доріжка = ланцюжок LC-ланок (звідки √(L/C)) ─────────────────
# Ідея: доріжка не «дріт», а лінія передачі. Розрізаємо її на короткі
# шматочки; кожен має послідовну індуктивність ΔL і шунтову ємність ΔC на
# землю. Нескінченний ланцюжок таких ланок і дає хвильовий опір √(L'/C').
def fig_rlgc_ladder():
    W, H = 780, 340
    p = []
    p.append(text(W/2, 30, "Доріжка як ланцюжок LC-ланок: звідки береться Z₀", size=15, bold=True))

    # верх: фізична доріжка над суцільною землею, поділена на шматочки Δx
    tx0, tx1 = 70, 710
    ty = 78
    gy = 116
    p.append(rect(tx0, ty - 5, tx1 - tx0, 10, fill=SIG, stroke="#8a2b1f", sw=1.2, rx=3))   # доріжка
    p.append(rect(tx0, gy, tx1 - tx0, 10, fill=GND, stroke="#2c3138", sw=1.2, rx=2))       # земля
    p.append(text((tx0+tx1)/2, ty - 12, "доріжка (сигнал)", size=10.5, color=SIG, bold=True))
    p.append(text((tx0+tx1)/2, gy + 24, "суцільна земля під нею (зворотний шлях струму)", size=10.5, color=GND))
    # поділ на шматочки Δx
    for i in range(1, 6):
        xx = tx0 + i * (tx1 - tx0) / 6
        p.append(line(xx, ty - 5, xx, ty + 5, color="#ffffff", sw=1.2))
    # дужка Δx над одним шматочком
    xa = tx0 + 2*(tx1-tx0)/6
    xb = tx0 + 3*(tx1-tx0)/6
    p.append(line(xa, 52, xb, 52, color=MUTED, sw=1.0))
    p.append(line(xa, 52, xa, 60, color=MUTED, sw=1.0))
    p.append(line(xb, 52, xb, 60, color=MUTED, sw=1.0))
    p.append(text((xa+xb)/2, 48, "Δx", size=11, color=MUTED, italic=True))

    # низ: еквівалентна LC-драбина
    ey = 210          # верхня рейка (сигнал)
    eg = 288          # нижня рейка (земля)
    ex0, ex1 = 70, 710
    p.append(text((ex0+ex1)/2, 168, "кожен шматочок Δx → послідовна ΔL і шунтова ΔC", size=12, bold=True, color=INK))
    p.append(line(ex0, eg, ex1, eg, color=GND, sw=2.4))           # рейка землі
    # чотири LC-ланки: котушка на верхній рейці, конденсатор униз на землю
    nseg = 4
    seg = (ex1 - ex0 - 40) / nseg
    x = ex0 + 20
    def coil(x1, x2, y):
        # проста «котушка»: кілька дужок
        n = 4; step = (x2 - x1) / n; f = []
        for k in range(n):
            cx = x1 + step*(k+0.5)
            f.append('<path d="M %.1f %.1f q %.1f -14 %.1f 0" fill="none" stroke="%s" stroke-width="2"/>'
                     % (x1+step*k, y, step/2, step, WAVE))
        return "".join(f)
    def cap(cx, y1, y2):
        # конденсатор: дві пластини між рейками
        my = (y1+y2)/2
        return (line(cx, y1, cx, my-5, color=INK, sw=1.6) +
                line(cx-11, my-5, cx+11, my-5, color=INK, sw=2.2) +
                line(cx-11, my+2, cx+11, my+2, color=INK, sw=2.2) +
                line(cx, my+2, cx, y2, color=INK, sw=1.6))
    prevx = ex0
    for s in range(nseg):
        x1 = ex0 + 20 + s*seg
        x2 = x1 + seg*0.55
        node = x1 + seg*0.72
        p.append(coil(x1, x2, ey))
        p.append(line(x2, ey, x1+seg, ey, color=INK, sw=1.6))    # рейка далі
        if s == 0:
            p.append(line(ex0, ey, x1, ey, color=INK, sw=1.6))
        p.append(cap(node, ey, eg))
        p.append(circle(node, ey, 2.4, fill=INK, stroke=INK, sw=1))
        if s == 1:
            b,_,_ = textbox((x1+x2)/2, ey - 26, "ΔL", size=11, color=WAVE, fill="#eaf0fd", stroke=WAVE, sw=1.1, pad=4)
            p.append(b)
            b,_,_ = textbox(node + 46, (ey+eg)/2, "ΔC", size=11, color=INK, fill="#ffffff", stroke=INK, sw=1.1, pad=4)
            p.append(b)
    # вхід зліва: сюди «дивиться» хвиля і бачить Z₀
    p.append(arrow(ex0 - 2, ey, ex0 + 16, ey, color=SIG, sw=2.0))
    b,_,_ = textbox(ex0 + 4, ey - 30, "хвиля бачить\nтут Z₀ = √(L′/C′)", size=10.5, color=SIG,
                    fill="#fdecea", stroke=SIG, sw=1.1, pad=5)
    p.append(b)
    p.append(text((ex0+ex1)/2, H - 12,
                  "L′, C′ — на одиницю довжини; ланок нескінченно багато, ланка нескінченно мала",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "rlgc-ladder.svg"), W, H, *p)


# ── microstrip-xsec: розріз мікросмужки — поле в FR-4 і в повітрі ────────────
# Ідея: робоча геометрія Z₀. Смужка шириною W на висоті h над суцільною землею;
# силові лінії йдуть і крізь FR-4, і крізь повітря — тому «ефективна» εr десь
# посередині. Це пояснює, ЧОМУ у формулу входить εeff, а не голе εr.
def fig_microstrip_xsec():
    W, H = 820, 370
    p = []
    p.append(text(W/2, 30, "Мікросмужка в розрізі: поле ділиться між FR-4 і повітрям", size=15, bold=True))

    # малюнок тримаємо ЛІВОРУЧ (до x≈540), висновок — окремим стовпчиком праворуч,
    # щоб рамки й лінії не наповзали одна на одну
    cx = 300
    core_x0, core_w = 120, 380
    core_y, core_h = 168, 108
    p.append(rect(core_x0, core_y, core_w, core_h, fill=CORE, stroke="#b8a55f", sw=1.5, rx=3))
    for i in range(1, 5):
        yy = core_y + i*core_h/5
        p.append(line(core_x0+8, yy, core_x0+core_w-8, yy, color="#c7b673", sw=0.8, dash="5 6"))
    # земля — суцільна мідь під осердям
    gy = core_y + core_h
    p.append(rect(core_x0, gy, core_w, 12, fill=COPPER, stroke=COPDK, sw=1.2, rx=1))
    # смужка-провідник зверху осердя
    strip_w = 80
    strip_y = core_y - 12
    p.append(rect(cx - strip_w/2, strip_y, strip_w, 12, fill=SIG, stroke="#8a2b1f", sw=1.3, rx=2))
    # зонні підписи — з КРАЮ, не на полі
    p.append(text(core_x0 + 60, core_y - 30, "повітря (εr ≈ 1)", size=10.5, color=MUTED))
    # підпис FR-4 — праворуч від пучка поля, у чистій частині осердя
    p.append(text(core_x0 + core_w - 66, core_y + core_h/2 + 4, "FR-4 (εr ≈ 4.3)", size=11.5, color="#8a7a2f", bold=True))

    # силові лінії поля: центральні — прямо вниз крізь FR-4; крайові дуги — крізь повітря
    for dx in (-24, -10, 10, 24):
        p.append(line(cx+dx, strip_y+12, cx+dx*0.5, gy, color=WAVE, sw=1.3))
    for sgn in (-1, 1):
        x0 = cx + sgn*strip_w/2
        p.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="4 4"/>'
                 % (x0, strip_y+6, x0+sgn*58, strip_y-4, x0+sgn*76, gy-28, x0+sgn*48, gy, WAVE))
    # підпис «поле» — ліворуч від пучка ліній, у порожнечі (без виноски-різака)
    p.append(text(core_x0 + 40, strip_y + 52, "поле", size=10.5, color=WAVE, bold=True, anchor="middle"))

    # розмір W (над смужкою)
    p.append(line(cx - strip_w/2, strip_y - 14, cx + strip_w/2, strip_y - 14, color=INK, sw=1.2))
    p.append(text(cx, strip_y - 18, "W", size=12, color=INK, bold=True))
    # розмір h (ліворуч від осердя)
    hx = core_x0 - 22
    p.append(line(hx, strip_y+6, hx, gy, color=INK, sw=1.2))
    p.append(line(hx-4, strip_y+6, hx+4, strip_y+6, color=INK, sw=1.2))
    p.append(line(hx-4, gy, hx+4, gy, color=INK, sw=1.2))
    p.append(text(hx - 12, (strip_y+gy)/2 + 4, "h", size=12, color=INK, bold=True, anchor="middle"))
    # підпис землі
    p.append(text(cx, gy + 30, "суцільна земля", size=11, color=COPDK, bold=True))

    # роздільник і висновок ПРАВОРУЧ, в чистому полі
    p.append(line(560, 60, 560, H - 26, color="#d0d4d8", sw=1.2, dash="6 5"))
    b, bw, bh = textbox(688, 150,
                        "частина поля — у FR-4,\nчастина — у повітрі →\nεeff десь ПОСЕРЕДИНІ:\n1 < εeff < εr",
                        size=10.5, color=INK, fill="#f4f6f8", stroke=MUTED, sw=1.2, pad=8)
    p.append(b)
    b2, _, _ = textbox(688, 250,
                       "ширше W →\nбільша ємність →\nменший Z₀",
                       size=10.5, color=SIG, fill="#fdecea", stroke=SIG, sw=1.2, pad=8)
    p.append(b2)

    render(os.path.join(OUT, "microstrip-xsec.svg"), W, H, *p)


# ── reflection-boundary: відбиття від неузгодженого кінця (Γ) ────────────────
# Ідея: падаюча хвиля на стику Z₀|Z_L ділиться на пройдену й відбиту; частка
# відбитого — Γ = (Z_L−Z₀)/(Z_L+Z₀). Три канонічні випадки: відкрито (+1),
# узгоджено (0), коротко (−1). Це фізика, з якої росте «навіщо 50 Ω і термінація».
def fig_reflection_boundary():
    W, H = 780, 380
    p = []
    p.append(text(W/2, 30, "Відбиття від кінця: скільки хвилі вертає, вирішує Γ", size=15, bold=True))

    # горизонтальна лінія передачі з Z₀, стик праворуч
    lx0, lx1 = 70, 470
    ly = 120
    p.append(line(lx0, ly, lx1, ly, color=INK, sw=2.6))
    p.append(text((lx0+lx1)/2, ly - 40, "лінія  Z₀ = 50 Ω", size=12, color=INK, bold=True))
    # падаюча хвиля →
    p.append(arrow(lx0+30, ly - 16, lx0+150, ly - 16, color=SIG, sw=2.2))
    p.append(text(lx0+90, ly - 22, "падаюча", size=10.5, color=SIG, bold=True))
    # відбита хвиля ←
    p.append(arrow(lx1-30, ly + 20, lx1-150, ly + 20, color=WAVE, sw=2.2))
    p.append(text(lx1-92, ly + 34, "відбита = Γ·падаюча", size=10.5, color=WAVE, bold=True))
    # стик і навантаження Z_L
    p.append(line(lx1, ly - 34, lx1, ly + 34, color=MUTED, sw=1.4, dash="5 4"))
    p.append(rect(lx1, ly - 22, 46, 44, fill="#f4f6f8", stroke=INK, sw=1.4, rx=4))
    p.append(text(lx1+23, ly + 5, "Z_L", size=12, color=INK, bold=True))
    # формула Γ під стиком
    b,_,_ = textbox((lx0+lx1)/2, ly + 74, "Γ = (Z_L − Z₀) / (Z_L + Z₀)", size=13, color=INK,
                    fill="#ffffff", stroke=INK, sw=1.3, pad=7)
    p.append(b)

    # три випадки праворуч — стовпчик карток
    rx = 560
    cases = [
        ("Z_L → ∞  (відкрито)",  "Γ = +1",  "уся хвиля назад,\nтой самий знак", POS, "#fdecea"),
        ("Z_L = Z₀  (узгоджено)", "Γ = 0",   "нічого не вертає —\nвся енергія пройшла", FIELD, "#eafaf0"),
        ("Z_L = 0  (коротко)",   "Γ = −1",  "уся хвиля назад,\nоберт. знак", NEG, "#eaf0fd"),
    ]
    cy = 92
    for title_, gam, note, col, bg in cases:
        p.append(text(rx, cy, title_, size=11, color=INK, bold=True, anchor="start"))
        b,_,_ = textbox(rx + 150, cy + 22, gam, size=13, color=col, fill=bg, stroke=col, sw=1.3, pad=6)
        p.append(b)
        p.append(mtext(rx, cy + 40, note, size=10, color=MUTED, anchor="start"))
        cy += 92

    p.append(text(W/2, H - 12,
                  "Γ = 0 (узгоджено) — жодного відлуння; будь-яке неузгодження вертає частину назад",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "reflection-boundary.svg"), W, H, *p)


if __name__ == "__main__":
    fig_rlgc_ladder()
    fig_microstrip_xsec()
    fig_reflection_boundary()
    print("figs done:", os.listdir(OUT))
