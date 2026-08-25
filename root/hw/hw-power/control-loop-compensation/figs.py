# -*- coding: utf-8 -*-
"""Фігури до статті «Компенсатор і стійкість зворотного зв'язку DC-DC».
Чистий Python, без залежностей; svgkit зі scripts/ імпортуємо, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: компенсатор докидає фазу саме там, де підсилення =0 дБ ──────────
def fig_phase_boost():
    W, H = 760, 430
    f = [render_head(W, H)]
    # дві панелі Боде: величина (верх) і фаза (низ)
    L, R = 70, 690
    # верхня панель — величина
    yT0, yT1 = 60, 175          # рамка величини
    y0dB = 128                  # рівень 0 дБ
    f.append(text(300, 30, "Той самий контур: без і з компенсатором", size=16, bold=True, anchor="middle"))
    # осі величини
    f.append(line(L, yT1, R, yT1, color=MUTED, sw=1.2))          # низ
    f.append(line(L, yT0, L, yT1, color=MUTED, sw=1.2))          # ліва
    f.append(line(L, y0dB, R, y0dB, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(L-6, y0dB+4, "0 дБ", size=11, color=MUTED, anchor="end"))
    f.append(text(L-6, yT0+10, "|T|", size=12, color=INK, anchor="end"))
    # крива величини «без компенсатора» — рано перетинає 0 дБ (fc низька, крутий спад)
    raw_mag = [(L, 80), (L+130, 92), (L+230, 118), (L+300, y0dB), (L+430, 168), (R, 172)]
    f.append(polyline(raw_mag, color=MUTED, sw=2.4))
    # крива «з компенсатором» — вища на низах, чистий перетин пізніше
    cmp_mag = [(L, 66), (L+150, 82), (L+320, 108), (L+470, y0dB), (L+560, 150), (R, 165)]
    f.append(polyline(cmp_mag, color=NEG, sw=2.6))
    fc_raw = L+300
    fc_cmp = L+470
    f.append(line(fc_raw, y0dB, fc_raw, yT1+118, color=MUTED, sw=1.0, dash="3 4"))
    f.append(line(fc_cmp, y0dB, fc_cmp, yT1+118, color=NEG, sw=1.0, dash="3 4"))

    # нижня панель — фаза
    yB0, yB1 = 245, 380
    ym180 = 355                 # рівень −180°
    f.append(line(L, yB1, R, yB1, color=MUTED, sw=1.2))
    f.append(line(L, yB0, L, yB1, color=MUTED, sw=1.2))
    f.append(line(L, ym180, R, ym180, color=POS, sw=1.2, dash="4 4"))
    f.append(text(L-6, ym180+4, "−180°", size=11, color=POS, anchor="end"))
    f.append(text(L-6, yB0+10, "фаза", size=12, color=INK, anchor="end"))
    # фаза «без компенсатора» — валиться до −180 (подвійний полюс LC)
    raw_ph = [(L, 258), (L+150, 268), (L+250, 300), (L+320, 340), (L+430, 352), (R, 356)]
    f.append(polyline(raw_ph, color=MUTED, sw=2.4))
    # фаза «з компенсатором» — горб догори саме коло fc (докинута фаза)
    cmp_ph = [(L, 258), (L+180, 292), (L+330, 320), (fc_cmp, 300), (L+560, 330), (R, 352)]
    f.append(polyline(cmp_ph, color=NEG, sw=2.6))

    # позначки запасу фази на fc кожної кривої
    f.append(line(fc_raw, 328, fc_raw, ym180, color=MUTED, sw=3.0))
    f.append(line(fc_cmp, 300, fc_cmp, ym180, color=NEG, sw=3.0))
    b, bw, bh = textbox(fc_raw, 405, "малий запас фази", size=11, color=MUTED, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    f.append(line(fc_raw, 389, fc_raw, 358, color=MUTED, sw=1.0, dash="2 3"))
    b, bw, bh = textbox(fc_cmp+68, 268, "докинута фаза\n→ здоровий запас", size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    # легенда
    f.append(line(R-165, 52, R-140, 52, color=MUTED, sw=2.6)); f.append(text(R-135, 56, "сам перетворювач", size=11, color=MUTED, anchor="start"))
    f.append(line(R-165, 70, R-140, 70, color=NEG, sw=2.8));  f.append(text(R-135, 74, "+ компенсатор", size=11, color=NEG, anchor="start"))
    f.append("</svg>")
    write(os.path.join(IMG, "phase-boost.svg"), f)


# ── Фігура 2: сходинка типів I / II / III — скільки фази докидає кожен ────────
def fig_types_ladder():
    W, H = 760, 360
    f = [render_head(W, H)]
    f.append(text(W/2, 30, "Три типи компенсатора: скільки фази здатен докинути кожен", size=16, bold=True))
    cols = [
        ("Тип I", "інтегратор", "0° boost",
         "лише полюс на нулі.\nТягне вихід точно до цілі,\nале фази НЕ додає —\nтільки для дуже повільних\n(коеф. потужності, LED).", FIELD, "#eafaf0"),
        ("Тип II", "полюс-нуль", "до ~90° boost",
         "нуль піднімає фазу,\nполюс потім прибирає шум.\nРобоча конячка струмового\nрежиму й виходів із ESR\n(електроліт, тантал).", NEG, "#eaf0fd"),
        ("Тип III", "два нулі", "до ~180° boost",
         "два нулі й два полюси.\nДокидає фазу навіть проти\nкрутого −180° подвійного\nполюса LC. Треба для\nкерамічних виходів.", POS, "#fdecea"),
    ]
    bw = 220
    gap = 20
    x0 = (W - (bw*3 + gap*2)) / 2
    top = 60
    for i, (name, sub, boost, body, col, fill) in enumerate(cols):
        x = x0 + i*(bw+gap)
        f.append(rect(x, top, bw, 250, fill=fill, stroke=col, sw=2.0, rx=10))
        f.append(text(x+bw/2, top+30, name, size=18, color=col, bold=True))
        f.append(text(x+bw/2, top+50, sub, size=12, color=MUTED))
        # смужка «boost»
        f.append(rect(x+20, top+64, bw-40, 26, fill=BG, stroke=col, sw=1.5, rx=6))
        f.append(text(x+bw/2, top+82, boost, size=13, color=col, bold=True))
        f.append(mtext(x+bw/2, top+118, body, size=11.5, color=INK, lh=1.28))
    # стрілка «дедалі більше фази»
    ax0, ax1, ay = x0+30, x0+bw*3+gap*2-30, top+270
    f.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2.0))
    f.append(text((ax0+ax1)/2, ay-8, "дедалі більший запас фази ⇒ дедалі крутіший (низькоомний) вихід можна приборкати", size=11.5, color=MUTED))
    f.append("</svg>")
    write(os.path.join(IMG, "types-ladder.svg"), f)


# ── Фігура 3: два види підсилювача похибки → різна схема компенсації ──────────
def fig_two_amps():
    W, H = 760, 360
    f = [render_head(W, H)]
    f.append(text(W/2, 28, "Один компенсатор — дві різні схеми, бо різний підсилювач похибки", size=16, bold=True))

    # ── ліворуч: операційний (напруго-вихідний): мережа ОБГОРТАЄ підсилювач ──
    cxL = 200
    f.append(text(cxL, 60, "Операційний (напруга на виході)", size=13, color=NEG, bold=True))
    # трикутник ОП
    tx, ty = 150, 150
    f.append(triangle(tx, ty, 70, 46, NEG))
    f.append(minus(tx-8, ty-14, 7))
    f.append(plus(tx-8, ty+14, 7))
    # FB-вузол зліва, вхід
    f.append(line(60, ty-14, tx-8, ty-14, color=LINE, sw=1.5))
    f.append(text(52, ty-11, "FB", size=11, color=INK, anchor="end"))
    f.append(line(60, ty+14, tx-8, ty+14, color=LINE, sw=1.5))
    f.append(text(52, ty+18, "Vоп", size=11, color=MUTED, anchor="end"))
    # вихід COMP
    f.append(line(tx+42, ty, 320, ty, color=LINE, sw=1.5))
    f.append(text(324, ty+4, "COMP", size=11, color=INK, anchor="start"))
    # мережа R/C з виходу НАЗАД на FB (обгортає)
    f.append(line(tx+42, ty, tx+42, ty-70, color=LINE, sw=1.4))
    f.append(line(tx+42, ty-70, 60, ty-70, color=LINE, sw=1.4))
    f.append(line(60, ty-70, 60, ty-14, color=LINE, sw=1.4))
    b, bwv, bhv = textbox((tx+42+60)/2, ty-70, "R, C навколо", size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, bwv, bhv = textbox(cxL, 300, "Мережа замикається з виходу\nНАЗАД на вхід FB — «обгортає»\nпідсилювач. Нулі/полюси задає\nвідношення опорів.", size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(b)

    # ── праворуч: крутонапутній OTA (струм на виході): мережа НА ЗЕМЛЮ ──
    cxR = 560
    f.append(text(cxR, 60, "Крутісний OTA (струм на виході)", size=13, color=POS, bold=True))
    tx2, ty2 = 520, 150
    f.append(triangle(tx2, ty2, 70, 46, POS))
    f.append(minus(tx2-8, ty2-14, 7))
    f.append(plus(tx2-8, ty2+14, 7))
    f.append(text(tx2+18, ty2-3, "gm", size=12, color=POS, bold=True))
    f.append(line(430, ty2-14, tx2-8, ty2-14, color=LINE, sw=1.5))
    f.append(text(422, ty2-11, "FB", size=11, color=INK, anchor="end"))
    f.append(line(430, ty2+14, tx2-8, ty2+14, color=LINE, sw=1.5))
    f.append(text(422, ty2+18, "Vоп", size=11, color=MUTED, anchor="end"))
    # вихід COMP → мережа на землю
    f.append(line(tx2+42, ty2, 640, ty2, color=LINE, sw=1.5))
    f.append(text(600, ty2-8, "COMP", size=11, color=INK, anchor="start"))
    f.append(line(640, ty2, 640, ty2+50, color=LINE, sw=1.4))
    b, bwv, bhv = textbox(640, ty2+62, "R, C\nна землю", size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(b)
    # земля
    gy = ty2+92
    f.append(line(640, gy, 640, gy+6, color=LINE, sw=1.4))
    f.append(line(628, gy+6, 652, gy+6, color=LINE, sw=1.8))
    f.append(line(632, gy+10, 648, gy+10, color=LINE, sw=1.4))
    f.append(line(636, gy+14, 644, gy+14, color=LINE, sw=1.2))
    b, bwv, bhv = textbox(cxR, 300, "Вихід — це струм у вузол COMP.\nМережа стоїть від COMP НА ЗЕМЛЮ.\nНулі/полюси задає gm·R і сам C —\nабсолютні номінали, не відношення.", size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(b)

    # розділювач
    f.append(line(370, 70, 370, 270, color=MUTED, sw=1.0, dash="4 5"))
    f.append("</svg>")
    write(os.path.join(IMG, "two-amps.svg"), f)


# ══ Фігури до вставки math-k-factor ══════════════════════════════════════════

# ── Фігура K1: геометрія K-factor — нуль і полюс симетрично навколо fc ────────
def fig_kfactor_geometry():
    import math
    W, H = 760, 400
    f = [render_head(W, H)]
    f.append(text(W/2, 30, "Чому fc — геометричний центр: нуль і полюс симетрично навколо нього", size=15, bold=True))
    # фазова панель: горб фази з максимумом на fc (лог-вісь по x)
    L, R = 80, 690
    yTop, yBot = 70, 300
    yBase = 285          # рівень 0° додатку фази
    # осі
    f.append(line(L, yBot, R, yBot, color=MUTED, sw=1.2))
    f.append(line(L, yTop, L, yBot, color=MUTED, sw=1.2))
    f.append(text(L-8, yTop+8, "додаток\nфази".split("\n")[0], size=11, color=INK, anchor="end"))
    f.append(text(R, yBot+18, "log f", size=11, color=MUTED, anchor="end"))
    f.append(line(L, yBase, R, yBase, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(L-8, yBase+4, "0°", size=11, color=MUTED, anchor="end"))
    # позиції нуля (fc/K), fc, полюса (fc*K) — симетрично в лог-масштабі
    xz = 230     # нуль
    xc = (L+R)/2 # fc — рівно посередині між нулем і полюсом (геом. центр)
    xp = 540     # полюс = дзеркало нуля відносно fc
    # горб фази: дзвоноподібна крива, максимум на xc
    pts = []
    for i in range(0, 101):
        x = L + (R-L)*i/100.0
        # відстань від центру в «декадах» экрана
        t = (x - xc) / ((xp - xz)/2.0)      # 0 у центрі, ±1 на нулі/полюсі
        amp = 1.0/(1.0 + t*t*1.7)            # горб, симетричний
        y = yBase - amp*(yBase - yTop - 20)
        pts.append((x, y))
    f.append(polyline(pts, color=NEG, sw=2.6))
    # вертикалі нуля, fc, полюса
    for x, lab, col, sub in [(xz, "нуль", FIELD, "fc/K"), (xc, "fc", POS, "зріз"), (xp, "полюс", FIELD, "fc·K")]:
        f.append(line(x, yBase, x, yTop+18, color=col, sw=1.4, dash="3 3"))
        f.append(circle(x, yBase, 3.5, fill=col, stroke=col))
        f.append(text(x, yBot+18, lab, size=12, color=col, bold=True))
        f.append(text(x, yBot+34, sub, size=11, color=MUTED))
    # позначка максимуму на fc
    f.append(circle(xc, yTop+20, 4, fill=POS, stroke=POS))
    b, bw, bh = textbox(xc, yTop-2, "тут горб найвищий → boost", size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(b)
    # дуги «однакова відстань у лог-масштабі»
    f.append(line(xz, yBase+46, xc, yBase+46, color=INK, sw=1.2))
    f.append(line(xc, yBase+46, xp, yBase+46, color=INK, sw=1.2))
    f.append(text((xz+xc)/2, yBase+42, "×K", size=11, color=INK, anchor="middle"))
    f.append(text((xc+xp)/2, yBase+42, "×K", size=11, color=INK, anchor="middle"))
    b, bw, bh = textbox(W/2, 375, "рівні кроки в лог-масштабі: fc = √(f_нуль · f_полюс) — геометричне середнє", size=12, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    f.append("</svg>")
    write(os.path.join(IMG, "kfactor-geometry.svg"), f)


# ── Фігура K2: K росте з boost — розсув нуля-полюса й ціна на низах ───────────
def fig_k_vs_boost():
    import math
    W, H = 760, 360
    f = [render_head(W, H)]
    f.append(text(W/2, 30, "K як важіль: більший підйом фази ⇒ ширше розсув ⇒ нижчий виграш на низах", size=15, bold=True))
    L, R = 80, 470
    yTop, yBot = 60, 300
    # крива K = tan(45 + boost/2) для Типу II, boost 0..170
    f.append(line(L, yBot, R, yBot, color=MUTED, sw=1.2))
    f.append(line(L, yTop, L, yBot, color=MUTED, sw=1.2))
    f.append(text((L+R)/2, yBot+34, "потрібний підйом фази boost, °", size=11, color=MUTED))
    f.append(text(L-10, yTop-2, "K", size=12, color=INK, anchor="end", bold=True))
    bmax = 170.0
    Kmax = 12.0
    def X(b): return L + (R-L)*b/bmax
    def Y(k): return yBot - (yBot-yTop)*min(k, Kmax)/Kmax
    # сітка
    for kv in [2, 4, 6, 8, 10]:
        f.append(line(L, Y(kv), R, Y(kv), color="#e5e7eb", sw=1.0))
        f.append(text(L-6, Y(kv)+4, str(kv), size=10, color=MUTED, anchor="end"))
    # крива Тип II
    pts2 = []
    for i in range(0, 176):
        b = i
        if b >= 178: break
        k = math.tan(math.radians(45 + b/2.0))
        if k > Kmax*1.4: break
        pts2.append((X(b), Y(k)))
    f.append(polyline(pts2, color=NEG, sw=2.6))
    f.append(text(X(150), Y(math.tan(math.radians(45+150/2.0)))-10, "Тип II  K=tan(45+b/2)", size=11, color=NEG, anchor="end"))
    # крива Тип III: K=[tan(45+b/4)]^2 — те саме K дає ВДВІЧІ більший boost
    pts3 = []
    for i in range(0, 176):
        b = i
        k = math.tan(math.radians(45 + b/4.0))**2
        if k > Kmax*1.4: break
        pts3.append((X(b), Y(k)))
    f.append(polyline(pts3, color=POS, sw=2.6))
    f.append(text(X(150), Y(math.tan(math.radians(45+150/4.0))**2)+18, "Тип III  K=[tan(45+b/4)]²", size=11, color=POS, anchor="end"))
    # права колонка — пояснення
    b, bw, bh = textbox(620, 130, "Тип II: один нуль,\nодин полюс.\nboost < 90°\n(K → ∞ на 90°).", size=11.5, color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, bw, bh = textbox(620, 240, "Тип III: подвійні\nнуль і полюс.\nboost < 180°\nза те саме K.", size=11.5, color=POS, fill="#fdecea", stroke=POS)
    f.append(b)
    f.append("</svg>")
    write(os.path.join(IMG, "k-vs-boost.svg"), f)


# ── Фігура K3: карта нулів-полюсів трьох типів на осі частоти ─────────────────
def fig_polezero_map():
    W, H = 760, 340
    f = [render_head(W, H)]
    f.append(text(W/2, 30, "Карта нулів (○) і полюсів (✕) трьох типів на осі частоти", size=15, bold=True))
    L, R = 110, 690
    fc = (L+R)/2
    rows = [
        ("Тип I", 90, [("p", L+20, "полюс\nна 0")], []),
        ("Тип II", 170, [("p", L+20, "0"), ("z", fc-120, "fc/K"), ("p", fc+120, "fc·K")], []),
        ("Тип III", 250, [("p", L+20, "0"), ("z", fc-140, "fc/√K"), ("z", fc-100, ""),
                          ("p", fc+100, ""), ("p", fc+140, "fc·√K")], []),
    ]
    # спільна вісь fc
    f.append(line(fc, 55, fc, 300, color=POS, sw=1.2, dash="4 4"))
    f.append(text(fc, 50, "fc (зріз)", size=12, color=POS, bold=True))
    for name, y, marks, _ in rows:
        f.append(line(L, y, R, y, color=MUTED, sw=1.4))
        f.append(text(L-10, y+4, name, size=13, color=INK, anchor="end", bold=True))
        for kind, x, lab in marks:
            if kind == "z":
                f.append(circle(x, y, 6, fill=BG, stroke=FIELD, sw=2.2))
            else:
                # ✕ полюс
                f.append(line(x-5, y-5, x+5, y+5, color=POS, sw=2.2))
                f.append(line(x-5, y+5, x+5, y-5, color=POS, sw=2.2))
            if lab:
                f.append(text(x, y+22 if kind=="z" else y-14, lab.replace("\n"," "), size=10.5, color=MUTED))
    # легенда
    f.append(circle(150, 320, 6, fill=BG, stroke=FIELD, sw=2.2)); f.append(text(165, 324, "нуль (піднімає фазу)", size=11, color=INK, anchor="start"))
    f.append(line(360, 315, 370, 325, color=POS, sw=2.2)); f.append(line(360, 325, 370, 315, color=POS, sw=2.2))
    f.append(text(378, 324, "полюс (опускає фазу / прибирає шум)", size=11, color=INK, anchor="start"))
    f.append("</svg>")
    write(os.path.join(IMG, "polezero-map.svg"), f)


# ── Фігура 7 (історична): що вже було й що докинув Венейбл ────────────────────
def fig_lineage():
    W, H = 760, 320
    f = [render_head(W, H)]
    f.append(text(W/2, 30, "Родовід рецепта: три готові цеглини й замок над ними",
                  size=16, bold=True, anchor="middle"))

    # три «цеглини аналізу», що були ДО 1983 — рядок знизу
    yb = 210
    boxes = [
        ("Боде, 1940-і", ["запас фази", "й підсилення —", "МІРА стійкості"]),
        ("Мідлбрук і Чук, 1970-і", ["усереднена модель:", "Боде силової частини", "з номіналів"]),
        ("Тип I / II / III", ["стандартні форми", "нуль–полюс навколо", "підсилювача похибки"]),
    ]
    cxs = [150, 380, 610]
    bw, bh = 200, 96
    for (title, lines), cx in zip(boxes, cxs):
        f.append(rect(cx-bw/2, yb, bw, bh, fill=FILL, stroke=MUTED, sw=1.6))
        f.append(text(cx, yb+22, title, size=13, bold=True, color=INK, anchor="middle"))
        for i, ln in enumerate(lines):
            f.append(text(cx, yb+44+i*16, ln, size=11.5, color=MUTED, anchor="middle"))

    # «замок» Венейбла зверху — K-фактор, що робить із аналізу СИНТЕЗ
    yk = 78
    kbx, kby, kbw, kbh = 205, yk, 350, 66
    f.append(rect(kbx, kby, kbw, kbh, fill="#eaf0fd", stroke=NEG, sw=2.2))
    f.append(text(kbx+kbw/2, kby+24, "Венейбл, POWERCON 10, 1983 — K-фактор",
                  size=13.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(kbx+kbw/2, kby+45, "від «зріз + запас фази» → просто до номіналів (з першого разу)",
                  size=11.5, color=INK, anchor="middle"))

    # три стрілки знизу вгору — цеглини живлять замок
    for cx in cxs:
        f.append(arrow(cx, yb-4, min(max(cx, kbx+40), kbx+kbw-40), kby+kbh+6,
                       color=MUTED, sw=1.6))

    # підпис ліворуч: до Венейбла це був АНАЛІЗ (перевірити готове), він дав СИНТЕЗ
    f.append(text(W/2, 300, "Було: порахувати стійкість готової схеми (аналіз).  "
                  "Стало: піти від бажаного назад до деталей (синтез).",
                  size=11.5, color=INK, anchor="middle", italic=True))
    write(os.path.join(IMG, "lineage.svg"), f)


# ── дрібні помічники поверх svgkit ───────────────────────────────────────────
def render_head(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>'
            % (w, h, FONT, w, h, BG, LINE))

def polyline(pts, color=INK, sw=2.0):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw)

def triangle(cx, cy, w, h, color):
    # трикутник підсилювача, вершина праворуч
    x0 = cx - w/2
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6" opacity="0.12"/>'
            '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="1.8"/>'
            % (x0, cy-h/2, x0, cy+h/2, x0+w, cy, color, color,
               x0, cy-h/2, x0, cy+h/2, x0+w, cy, color))

def write(path, frags):
    import io
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(frags))
    print("wrote", os.path.basename(path))


if __name__ == "__main__":
    fig_phase_boost()
    fig_types_ladder()
    fig_two_amps()
    fig_kfactor_geometry()
    fig_k_vs_boost()
    fig_polezero_map()
    fig_lineage()
    print("done")
