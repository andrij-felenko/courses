# -*- coding: utf-8 -*-
"""Фігури до детальної статті «BJT проти MOSFET».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

BJTC = POS      # біполярний — теплим (червоним)
FETC = NEG      # польовий — холодним (синім)


def axes(f, ox, oy, w, h, xlabel, ylabel):
    """Осі з підписами: початок (ox,oy) — лівий-нижній кут, ростуть праворуч і вгору."""
    f.append(line(ox, oy, ox + w, oy, color=INK, sw=1.8))            # X
    f.append(line(ox, oy, ox, oy - h, color=INK, sw=1.8))            # Y
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        ox + w, oy, ox + w - 8, oy - 4, ox + w - 8, oy + 4, INK))    # вістря X
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        ox, oy - h, ox - 4, oy - h + 8, ox + 4, oy - h + 8, INK))    # вістря Y
    f.append(text(ox + w, oy + 20, xlabel, size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 6, oy - h - 6, ylabel, size=12, color=MUTED, anchor="middle"))


# ── 1. Два закони струму: експонента BJT і квадрат MOSFET (із підпороговим коліном) ──
def fig_iv_laws():
    W, H = 780, 430
    f = [text(W / 2, 26, "Два закони керування: чим тече вихідний струм",
              size=16, bold=True)]

    # ліва панель — BJT: Ic ~ exp(Vbe/VT)
    ox, oy, w, h = 70, 340, 260, 250
    axes(f, ox, oy, w, h, "Vbe", "Ic")
    pts = []
    for i in range(0, 101):
        vx = i / 100.0                      # 0..1 → Vbe від 0 до ~0.75 В
        # експонента, обрізана під верх панелі
        y = math.exp((vx - 0.62) / 0.055)
        y = min(y, 1.0)
        pts.append((ox + vx * w, oy - y * (h - 20)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), BJTC))
    f.append(text(ox + w * 0.30, oy - h + 34, "Ic = Is·(e^(Vbe/VT) − 1)",
                  size=13, color=BJTC, anchor="middle", bold=True))
    f.append(text(ox + w * 0.30, oy - h + 54, "різко вгору коло 0.6–0.7 В",
                  size=10, color=MUTED, anchor="middle"))
    f.append(text(ox + w / 2, oy + 42, "БІПОЛЯРНИЙ: чиста експонента",
                  size=12, color=BJTC, anchor="middle", bold=True))

    # права панель — MOSFET: Id ~ (Vgs-Vth)^2 зі споду підпороговою експонентою
    ox2 = 450
    axes(f, ox2, oy, w, h, "Vgs", "Id")
    vth = 0.42                              # частка ширини, де «поріг»
    pts = []
    for i in range(0, 101):
        vx = i / 100.0
        if vx < vth:
            y = 0.06 * math.exp((vx - vth) / 0.06)   # підпорогова експонента (мала)
        else:
            y = ((vx - vth) / (1 - vth)) ** 2         # квадрат над порогом
        y = min(y, 1.0)
        pts.append((ox2 + vx * w, oy - y * (h - 20)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), FETC))
    # позначка порога
    f.append(line(ox2 + vth * w, oy, ox2 + vth * w, oy - h + 14, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox2 + vth * w, oy + 16, "Vth", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox2 + w * 0.72, oy - h + 34, "Id = ½·k·(Vgs − Vth)²",
                  size=13, color=FETC, anchor="middle", bold=True))
    f.append(text(ox2 + w * 0.30, oy - 40, "підпорогова", size=9, color=MUTED, anchor="middle"))
    f.append(text(ox2 + w * 0.30, oy - 28, "експонента", size=9, color=MUTED, anchor="middle"))
    f.append(text(ox2 + w / 2, oy + 42, "ПОЛЬОВИЙ: квадрат (а внизу — теж експонента)",
                  size=11, color=FETC, anchor="middle", bold=True))

    render(os.path.join(IMG, "iv-laws.svg"), W, H, *f)


# ── 2. Крутість gm проти струму: BJT завжди вище ──
def fig_gm():
    W, H = 720, 430
    f = [text(W / 2, 26, "Крутість gm на той самий струм: біполярний виграє",
              size=16, bold=True)]
    ox, oy, w, h = 90, 330, 560, 250
    axes(f, ox, oy, w, h, "струм спокою I (лог)", "gm (лог)")

    # BJT: gm = I/VT  → на лог-лог пряма з нахилом 1, високо
    pts = [(ox + t * w, oy - (0.30 + 0.62 * t) * h) for t in (0.0, 1.0)]
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6"/>' %
             (pts[0][0], pts[0][1], pts[1][0], pts[1][1], BJTC))
    f.append(text(ox + w * 0.72, oy - 0.30 * h - 0.62 * h * 0.72 - 12,
                  "BJT:  gm = Ic / VT", size=13, color=BJTC, bold=True, anchor="middle"))

    # MOSFET: gm = sqrt(2·k·I) → нахил 1/2, нижче
    pts = [(ox + t * w, oy - (0.10 + 0.40 * t) * h) for t in (0.0, 1.0)]
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6"/>' %
             (pts[0][0], pts[0][1], pts[1][0], pts[1][1], FETC))
    f.append(text(ox + w * 0.70, oy - 0.10 * h - 0.40 * h * 0.70 + 22,
                  "MOSFET:  gm = √(2·k·Id)", size=13, color=FETC, bold=True, anchor="middle"))

    # вертикальний «розрив» на фіксованому струмі
    tx = ox + w * 0.55
    yb = oy - (0.30 + 0.62 * 0.55) * h
    yf = oy - (0.10 + 0.40 * 0.55) * h
    f.append(line(tx, yb, tx, yf, color=FIELD, sw=2.0, dash="5 4"))
    f.append(text(tx + 8, (yb + yf) / 2, "на тому самому\nструмі BJT дає\nбільше підсилення",
                  size=10, color=INK, anchor="start").replace("\n", " "))
    f.append(mtext(tx + 10, (yb + yf) / 2 - 6,
                   ["на тому самому струмі", "BJT дає більший gm"], size=10, color=INK, anchor="start"))

    note = ("BJT: нахил 1 — gm росте прямо з I, і множник 1/VT ≈ 40 В⁻¹ великий.\n"
            "MOSFET (над порогом): нахил ½ — gm росте лише як √I, тож завжди нижчий.")
    f.append(fitbox(90, 356, 560, 46, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "gm-comparison.svg"), W, H, *f)


# ── 3. Втрати провідності проти струму: сталий спад vs квадратична парабола ──
def fig_conduction():
    W, H = 740, 440
    f = [text(W / 2, 26, "Втрати у відкритому стані: де сталий спад програє резистору",
              size=16, bold=True)]
    ox, oy, w, h = 80, 340, 580, 250
    axes(f, ox, oy, w, h, "струм навантаження I", "втрати P = спад·I")

    Vsat = 0.30       # В — сталий спад BJT
    Rds = 0.02        # Ом — 20 мОм
    Imax = 8.0        # А по осі
    # BJT: P = Vsat·I → пряма
    def bx(I): return ox + (I / Imax) * w
    def by(P, Pmax): return oy - (P / Pmax) * (h - 20)
    Pmax = max(Vsat * Imax, Rds * Imax * Imax)
    f.append(line(bx(0), by(0, Pmax), bx(Imax), by(Vsat * Imax, Pmax), color=BJTC, sw=2.6))
    f.append(text(bx(Imax) - 6, by(Vsat * Imax, Pmax) - 10,
                  "BJT: P = Vce(sat)·I  (пряма)", size=12, color=BJTC, bold=True, anchor="end"))

    # MOSFET: P = I²·Rds → парабола
    pts = []
    for i in range(0, 101):
        I = Imax * i / 100.0
        pts.append((bx(I), by(Rds * I * I, Pmax)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), FETC))
    f.append(text(bx(Imax) - 6, by(Rds * Imax * Imax, Pmax) - 8,
                  "MOSFET: P = I²·Rds(on)  (парабола)", size=12, color=FETC, bold=True, anchor="end"))

    # точка перетину: Vsat·I = I²·Rds → I = Vsat/Rds
    Icx = Vsat / Rds        # 15 А — за межею осі, тож покажемо стрілкою «десь тут»
    if Icx <= Imax:
        f.append(line(bx(Icx), oy, bx(Icx), by(Vsat * Icx, Pmax), color=FIELD, sw=1.6, dash="4 4"))
        f.append(text(bx(Icx), oy + 16, "перетин", size=10, color=FIELD, anchor="middle"))
    else:
        f.append(text(bx(Imax) - 10, oy - 30,
                      "перетин при I = Vce(sat)/Rds(on) = %.0f А →" % Icx,
                      size=11, color=FIELD, anchor="end"))

    note = ("Ліворуч від перетину (звичайні струми) MOSFET холодніший — його резистивний спад малий.\n"
            "Праворуч I²·Rds(on) переростає сталі 0.3 В, і біполярний вихід (чи IGBT) знову виграє.")
    f.append(fitbox(80, 366, 580, 46, note, size=11, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "conduction-crossover.svg"), W, H, *f)


# ── 4. Теплова стійкість при паралелі: BJT хапає струм, MOSFET сам ділить ──
def fig_thermal():
    W, H = 780, 400
    f = [text(W / 2, 26, "Дві комірки поряд: чому BJT «хапає» струм, а MOSFET ділить порівну",
              size=15, bold=True)]

    def cell(cx, cy, hot, kind, color):
        s = []
        fill = "#fdecea" if hot else "#eef1f5"
        s.append(rect(cx - 42, cy - 30, 84, 60, fill=fill, stroke=color, sw=2, rx=8))
        s.append(text(cx, cy - 6, kind, size=13, color=color, bold=True))
        s.append(text(cx, cy + 14, "тепліша" if hot else "холодна", size=10, color=MUTED))
        return "".join(s)

    # ── BJT (ліворуч): додатний зворотний зв'язок ──
    bx0 = 200
    f.append(text(bx0, 66, "БІПОЛЯРНИЙ — розбіжність", size=13, color=BJTC, bold=True))
    f.append(cell(bx0 - 70, 150, True, "гарячіша", BJTC))
    f.append(cell(bx0 + 70, 150, False, "холодна", BJTC))
    # петля: тепліша → Vbe падає → бере ще більше струму → ще гарячіша
    loop = ("тепліша  →  Vbe падає (−2 мВ/°C)  →  бере БІЛЬШЕ струму  →  ще гарячіша  →  ↺\n"
            "струм «стікається» в одну комірку — теплова втеча, вторинний пробій")
    f.append(fitbox(bx0 - 150, 210, 300, 60, loop, size=10, fill="#fdecea", stroke=BJTC, color=INK))
    f.append(text(bx0, 296, "лік: емітерні баластні резистори", size=10, color=MUTED))

    # ── MOSFET (праворуч): від'ємний зворотний зв'язок ──
    fx0 = 580
    f.append(text(fx0, 66, "ПОЛЬОВИЙ — самобаланс", size=13, color=FETC, bold=True))
    f.append(cell(fx0 - 70, 150, True, "тепліша", FETC))
    f.append(cell(fx0 + 70, 150, False, "холодна", FETC))
    loop2 = ("тепліша  →  Rds(on) РОСТЕ (+тк)  →  бере МЕНШЕ струму  →  холоне  →  рівновага\n"
             "струм сам перетікає в холоднішу — можна паралелити без баласту")
    f.append(fitbox(fx0 - 150, 210, 300, 60, loop2, size=10, fill="#eaf3ec", stroke=FETC, color=INK))
    f.append(text(fx0, 296, "лік не потрібен (у ключовому режимі)", size=10, color=MUTED))

    # застереження внизу
    warn = ("Обережно: у ЛІНІЙНОМУ режимі (мала Vgs, велика Vds) MOSFET має інший, від'ємний "
            "тк порога — і теж може «хапати» струм. Самобаланс — саме про КЛЮЧОВИЙ режим.")
    f.append(fitbox(70, 330, 640, 44, warn, size=10, fill="#fff7e6", stroke="#b8860b", color=INK))
    render(os.path.join(IMG, "thermal-stability.svg"), W, H, *f)


# ── 5. Межа за напругою: питомий Rds росте як BV^2.5 → де царює IGBT ──
def fig_voltage_limit():
    W, H = 740, 430
    f = [text(W / 2, 26, "Межа кремнію: питомий Rds(on) росте круто з напругою",
              size=16, bold=True)]
    ox, oy, w, h = 90, 330, 560, 250
    axes(f, ox, oy, w, h, "напруга пробою BV (лог)", "питомий Rds·площа (лог)")

    # крива BV^2.5 на лог-лог — пряма з нахилом 2.5
    pts = [(ox + t * w, oy - (0.06 + 0.80 * t) * h) for t in (0.0, 1.0)]
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.8"/>' %
             (pts[0][0], pts[0][1], pts[1][0], pts[1][1], FETC))
    f.append(text(ox + w * 0.34, oy - (0.06 + 0.80 * 0.34) * h - 14,
                  "Ron·A ∝ BV^2.5  (ідеальна межа кремнію)", size=12, color=FETC, bold=True, anchor="start"))

    # мітки напруг на осі X
    for t, lbl in ((0.12, "30 В"), (0.40, "100 В"), (0.68, "600 В"), (0.95, "1200 В")):
        f.append(line(ox + t * w, oy, ox + t * w, oy + 5, color=INK, sw=1.4))
        f.append(text(ox + t * w, oy + 18, lbl, size=10, color=MUTED))

    # зони панування
    split = 0.66
    f.append(rect(ox, oy - h, split * w, h, fill="#eaf0fd", stroke="none", sw=0))
    f.append(rect(ox + split * w, oy - h, (1 - split) * w, h, fill="#fdecea", stroke="none", sw=0))
    # перемалювати осі/криву поверх заливок
    f.append(line(ox, oy, ox + w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - h, color=INK, sw=1.8))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.8"/>' %
             (pts[0][0], pts[0][1], pts[1][0], pts[1][1], FETC))
    f.append(text(ox + split * w * 0.5, oy - h + 22, "царює MOSFET",
                  size=13, color=FETC, bold=True))
    f.append(text(ox + split * w + (1 - split) * w * 0.5, oy - h + 22, "царює IGBT",
                  size=13, color=BJTC, bold=True))
    f.append(line(ox + split * w, oy, ox + split * w, oy - h, color=INK, sw=1.4, dash="5 4"))
    f.append(text(ox + split * w, oy - h - 4, "~кількасот В", size=10, color=MUTED, anchor="middle"))

    note = ("Що вища напруга, то товщий і менш легований дрейфовий шар — а його опір злітає як BV^2.5.\n"
            "Тому на сотнях–тисячах вольтів звичайний MOSFET «згорає» в опорі; там сталий спад IGBT дешевший.\n"
            "SiC/GaN і суперперехід зсувають межу праворуч — але сам закон лишається.")
    f.append(fitbox(90, 348, 560, 58, note, size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "voltage-limit.svg"), W, H, *f)


# ── 6. Канал MOSFET у розрізі: чому інтеграл заряду дає квадрат і перекриття ──
def fig_channel():
    W, H = 780, 470
    f = [text(W / 2, 26, "Канал MOSFET у розрізі: звідки береться квадрат (Vgs − Vth)²",
              size=15, bold=True)]

    # ── верхня панель: триодний режим (канал наскрізний, клин) ──
    ox, oy = 80, 70            # лівий-верхній кут «кремнію»
    Lw, Hh = 360, 90          # довжина каналу по X, товща по Y
    f.append(text(ox + Lw / 2, oy - 8, "триод (лінійний): Vds мале — канал наскрізний",
                  size=12, color=FETC, bold=True))
    # тіло напівпровідника
    f.append(rect(ox, oy, Lw, Hh, fill="#eef1f5", stroke=MUTED, sw=1.4, rx=0))
    # затвор-пластина + оксид зверху
    f.append(rect(ox, oy - 30, Lw, 10, fill="#d9d2c5", stroke=MUTED, sw=1.2, rx=0))   # затвор
    f.append(line(ox, oy - 20, ox + Lw, oy - 20, color="#b8b0a0", sw=3))              # оксид
    f.append(text(ox - 6, oy - 24, "затвор", size=10, color=MUTED, anchor="end"))
    # витік і стік (n+)
    f.append(rect(ox - 34, oy, 34, Hh, fill="#cdd8ea", stroke=NEG, sw=1.4, rx=0))
    f.append(rect(ox + Lw, oy, 34, Hh, fill="#cdd8ea", stroke=NEG, sw=1.4, rx=0))
    f.append(text(ox - 17, oy + Hh + 14, "витік", size=10, color=NEG))
    f.append(text(ox + Lw + 17, oy + Hh + 14, "стік", size=10, color=NEG))
    # шар інверсії — клин: товстий біля витоку, тонший біля стоку
    top = oy + 14
    pts = [(ox, top), (ox + Lw, top + 22), (ox + Lw, oy + Hh - 6), (ox, oy + Hh - 6)]
    f.append('<polygon points="%s" fill="#cfefe0" stroke="%s" stroke-width="1.4"/>' %
             (" ".join("%.0f,%.0f" % p for p in pts), FIELD))
    f.append(text(ox + Lw * 0.30, oy + Hh - 16, "шар носіїв (канал)", size=10, color=FIELD))
    # координата y уздовж каналу
    f.append(arrow(ox + 6, oy + Hh + 30, ox + Lw - 6, oy + Hh + 30, color=INK, sw=1.4))
    f.append(text(ox + Lw - 6, oy + Hh + 44, "y: 0 → L", size=10, color=INK, anchor="end"))
    # локальний заряд ∝ (Vgs − Vth − V(y))
    f.append(mtext(ox + Lw + 78, oy + 8,
                   ["місцевий заряд каналу", "Qn(y) = Cox·(Vgs − Vth − V(y))",
                    "тонший там, де V(y) вище", "→ інтеграл по y дає (Vgs−Vth)²"],
                   size=10, color=INK, anchor="start"))

    # ── нижня панель: насичення (канал відсічений біля стоку) ──
    oy2 = oy + Hh + 120
    f.append(text(ox + Lw / 2, oy2 - 8, "насичення: Vds велике — канал «відсічено» біля стоку (pinch-off)",
                  size=12, color=BJTC, bold=True))
    f.append(rect(ox, oy2, Lw, Hh, fill="#eef1f5", stroke=MUTED, sw=1.4, rx=0))
    f.append(rect(ox, oy2 - 30, Lw, 10, fill="#d9d2c5", stroke=MUTED, sw=1.2, rx=0))
    f.append(line(ox, oy2 - 20, ox + Lw, oy2 - 20, color="#b8b0a0", sw=3))
    f.append(rect(ox - 34, oy2, 34, Hh, fill="#cdd8ea", stroke=NEG, sw=1.4, rx=0))
    f.append(rect(ox + Lw, oy2, 34, Hh, fill="#cdd8ea", stroke=NEG, sw=1.4, rx=0))
    # клин, що сходить у нуль ще до стоку (точка відсічки)
    pinch = ox + Lw * 0.82
    pts2 = [(ox, oy2 + 14), (pinch, oy2 + Hh - 6), (ox, oy2 + Hh - 6)]
    f.append('<polygon points="%s" fill="#fbe3dd" stroke="%s" stroke-width="1.4"/>' %
             (" ".join("%.0f,%.0f" % p for p in pts2), BJTC))
    f.append(line(pinch, oy2, pinch, oy2 + Hh, color=BJTC, sw=1.4, dash="4 3"))
    f.append(text(pinch + 3, oy2 + 16, "відсічка", size=10, color=BJTC, anchor="start"))
    f.append(mtext(ox + Lw + 78, oy2 + 8,
                   ["за відсічкою заряд = 0", "далі струм уже не росте", "Id = ½·k·(Vgs − Vth)²",
                    "струм «насичується»"], size=10, color=INK, anchor="start"))

    note = ("Заряд каналу в точці y: Qn(y) = Cox·(Vgs − Vth − V(y)) — де потенціал каналу вищий, там носіїв менше.\n"
            "Сталість струму вздовж каналу зшиває Qn·швидкість; інтеграл по всій довжині L дає рівно ½·k·(Vgs−Vth)².")
    f.append(fitbox(80, oy2 + Hh + 30, 620, 44, note, size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "channel-derivation.svg"), W, H, *f)


# ── 7. Побудова бандгап-опори: PTAT + CTAT = пласка сума ──
def fig_bandgap():
    W, H = 740, 430
    f = [text(W / 2, 26, "Бандгап-опора: як VT·ln(N) вирівнює дрейф Vbe з температурою",
              size=15, bold=True)]
    ox, oy, w, h = 90, 320, 520, 240
    axes(f, ox, oy, w, h, "температура T →", "напруга")

    # CTAT: Vbe падає з T (нахил ≈ −2 мВ/°C) — від високо ліворуч до низько праворуч
    y0c, y1c = oy - 0.82 * h, oy - 0.34 * h
    f.append(line(ox, y0c, ox + w, y1c, color=BJTC, sw=2.6))
    f.append(text(ox + w * 0.16, y0c - 8, "Vbe (CTAT): падає ≈ −2 мВ/°C",
                  size=12, color=BJTC, bold=True, anchor="start"))

    # PTAT: M·VT·ln(N) росте з T — від низько ліворуч до високо праворуч
    y0p, y1p = oy - 0.10 * h, oy - 0.58 * h
    f.append(line(ox, y0p, ox + w, y1p, color=FETC, sw=2.6))
    f.append(text(ox + w * 0.42, y1p + 16, "M·VT·ln(N) (PTAT): росте ≈ +2 мВ/°C",
                  size=12, color=FETC, bold=True, anchor="start"))

    # сума — майже горизонтальна лінія коло ~1.2 В
    ys = oy - 0.92 * h
    f.append(line(ox, ys, ox + w, ys, color=FIELD, sw=3.0))
    f.append(text(ox + w * 0.5, ys - 10, "сума ≈ Eg/q ≈ 1.2 В  (пласка!)",
                  size=13, color=FIELD, bold=True, anchor="middle"))

    # вертикальні пунктири, що показують складання в одній точці T
    tx = ox + w * 0.62
    f.append(line(tx, oy, tx, ys, color=MUTED, sw=1.0, dash="3 3"))
    yc = y0c + (y1c - y0c) * 0.62
    yp = y0p + (y1p - y0p) * 0.62
    f.append(circle(tx, yc, 3.5, fill=BJTC, stroke=BJTC, sw=1))
    f.append(circle(tx, yp, 3.5, fill=FETC, stroke=FETC, sw=1))
    f.append(circle(tx, ys, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(tx + 6, (yc + yp) / 2, "+", size=16, color=INK, anchor="start", bold=True))

    note = ("Vbe одного переходу спадає з T (доповнює абсолютну — CTAT). Різниця двох Vbe за струмів у N разів дає\n"
            "ΔVbe = VT·ln(N), що РОСТЕ з T (пропорційна абсолютній — PTAT). Підбираєш множник M так, щоб нахили\n"
            "погасилися: Vbe + M·VT·ln(N) ≈ Eg/q ≈ 1.2 В — стала, майже незалежна від температури.")
    f.append(fitbox(90, 344, 560, 60, note, size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "bandgap-construction.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════
#  Фігури до вставки proj-gate-driver.md (драйвер затвора силового MOSFET)
# ══════════════════════════════════════════════════════════════════════════

# ── D1. Форма затвора при вмиканні: сходинка → плато Міллера → добір ──
def fig_gate_waveform():
    W, H = 780, 430
    f = [text(W / 2, 26, "Що бачить затвор під час вмикання: три ділянки Qg",
              size=16, bold=True)]
    ox, oy, w, h = 80, 330, 620, 250
    axes(f, ox, oy, w, h, "заряд, накачаний у затвор (час)", "Vgs")

    a = 0.22        # кінець першого нахилу (дійшли до рівня плато)
    b = 0.58        # кінець плато Міллера
    vth = 0.30      # рівень Vth (частка висоти)
    vpl = 0.52      # рівень плато Міллера
    vfin = 0.86     # кінцевий Vgs (= Vdrv)

    pts = [(ox, oy),
           (ox + a * w, oy - vpl * h),              # піднялись крізь Vth до плато
           (ox + b * w, oy - vpl * h),              # плато Міллера (горизонт)
           (ox + (b + 0.20) * w, oy - vfin * h),    # добираємо до Vdrv
           (ox + w, oy - vfin * h)]                 # насичення
    # зона плато Міллера підсвічена (перед кривою, щоб крива була зверху)
    f.append(rect(ox + a * w, oy - vfin * h - 6, (b - a) * w, vfin * h + 6,
                  fill="#fdecea", stroke="none", sw=0))
    for lvl, lbl, col in ((vth, "Vth (тут відкривається канал)", MUTED),
                          (vpl, "плато Міллера", BJTC),
                          (vfin, "Vdrv (повністю відкритий)", FIELD)):
        f.append(line(ox, oy - lvl * h, ox + w, oy - lvl * h, color=col, sw=1.1, dash="5 4"))
        f.append(text(ox + w - 4, oy - lvl * h - 5, lbl, size=10, color=col, anchor="end"))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), FETC))
    f.append(text(ox + (a + b) / 2 * w, oy - vfin * h - 12,
                  "тут Vds валиться — уся втрата тут", size=10, color=BJTC, bold=True, anchor="middle"))
    for xc, lbl in (((0 + a) / 2, "1) заряд Ciss"),
                    ((a + b) / 2, "2) плато (Qgd)"),
                    ((b + 1) / 2, "3) добір")):
        f.append(text(ox + xc * w, oy + 34, lbl, size=11, color=INK, anchor="middle"))

    note = ("Драйвер жене в затвор струм — Vgs росте. На плато Міллера ВЕСЬ струм іде на перезаряд Cgd,\n"
            "поки стік валить напругу; Vgs завмирає. Що довше тут стоїмо — то більша втрата. Швидкість\n"
            "проходу плато = Idrv / Cgd, тому головне число драйвера — пік СТРУМУ, а не напруга.")
    f.append(fitbox(80, 352, 620, 56, note, size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "gate-waveform.svg"), W, H, *f)


# ── D2. Вибір частоти: провідність рівна, комутація росте → сумарна яма ──
def fig_loss_vs_freq():
    W, H = 740, 430
    f = [text(W / 2, 26, "Вибір частоти: де сумарні втрати найменші",
              size=16, bold=True)]
    ox, oy, w, h = 90, 330, 560, 250
    axes(f, ox, oy, w, h, "частота перемикання f_sw (лог)", "втрати, Вт")

    Pcond = 0.30
    def Psw(t):  return 0.03 + 0.90 * t
    def Ptot(t): return Pcond + Psw(t)

    # провідність — горизонталь
    yc = oy - Pcond / 1.25 * h
    f.append(line(ox, yc, ox + w, yc, color=FETC, sw=2.2, dash="6 4"))
    f.append(text(ox + 8, yc - 8, "провідність  I²·Rds(on)  — від частоти НЕ залежить",
                  size=10, color=FETC, anchor="start"))
    # комутація (пунктир)
    pts = [(ox + t / 120.0 * w, oy - min(Psw(t / 120.0), 1.15) / 1.25 * h) for t in range(0, 121)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="2 4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), BJTC))
    f.append(text(ox + w - 4, oy - Psw(1.0) / 1.25 * h - 10,
                  "комутація  ∝ f_sw", size=11, color=BJTC, anchor="end", bold=True))
    # сумарна (суцільна)
    pts = [(ox + t / 120.0 * w, oy - min(Ptot(t / 120.0), 1.15) / 1.25 * h) for t in range(0, 121)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), INK))
    f.append(text(ox + w * 0.5, oy - Ptot(0.5) / 1.25 * h - 12,
                  "СУМА", size=12, color=INK, anchor="middle", bold=True))
    # робоча точка нижче перетину (запас)
    tw_ = 0.30
    f.append(line(ox + tw_ * w, oy, ox + tw_ * w, oy - Ptot(tw_) / 1.25 * h, color=FIELD, sw=1.6, dash="4 4"))
    f.append(circle(ox + tw_ * w, oy - Ptot(tw_) / 1.25 * h, 5, fill=FIELD, stroke=BG, sw=2))
    f.append(text(ox + tw_ * w, oy + 18, "робоча f_sw", size=10, color=FIELD, anchor="middle", bold=True))

    note = ("Провідність не залежить від частоти — це поличка. Комутація росте прямо з f_sw. Сума має пологе\n"
            "дно; практично беруть частоту трохи НИЖЧЕ перетину (де комутація ще менша за провідність) —\n"
            "лишаючи запас на нагрів і розкид. Вища f_sw дає менші котушки/конденсатори, але гарячіший ключ.")
    f.append(fitbox(90, 350, 560, 56, note, size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "loss-vs-freq.svg"), W, H, *f)


# ── D3. Паразитне вмикання: dV/dt через Cgd піднімає Vgs; кламп гасить ──
def fig_miller_turnon():
    W, H = 780, 430
    f = [text(W / 2, 26, "Паразитне вмикання: сусід смикнув стік — dV/dt лізе в затвор",
              size=15, bold=True)]

    # ── ліва панель: шлях струму через Cgd ──
    lx = 60
    dx, dy = lx + 150, 70
    gx, gy = lx + 40,  200
    sx, sy = lx + 150, 330
    f.append(rect(dx - 18, dy + 20, 36, 260, fill="#f4f6f8", stroke=INK, sw=1.6, rx=6))
    f.append(text(dx, dy + 8, "стік (D)", size=11, color=INK, anchor="middle"))
    f.append(text(sx, sy + 22, "витік (S)", size=11, color=INK, anchor="middle"))
    f.append(text(gx - 6, gy - 16, "затвор (G)", size=11, color=INK, anchor="end"))
    # Cgd між стоком і затвором
    f.append(line(dx, dy + 60, gx + 40, gy - 10, color=BJTC, sw=2.2))
    f.append(text((dx + gx) / 2 + 22, (dy + gy) / 2, "Cgd", size=12, color=BJTC, bold=True, anchor="middle"))
    f.append(arrow(dx - 58, dy + 12, dx - 58, dy + 72, color=BJTC, sw=2.4))
    f.append(text(dx - 64, dy + 6, "dV/dt ↑", size=11, color=BJTC, anchor="end", bold=True))
    # Rg від затвора до драйвера
    f.append(rect(gx - 84, gy - 12, 56, 24, fill=FILL, stroke=INK, sw=1.4, rx=4))
    f.append(text(gx - 56, gy + 5, "Rg", size=12, color=INK, anchor="middle", bold=True))
    f.append(line(gx - 28, gy, gx, gy, color=INK, sw=1.6))
    f.append(text(gx - 84, gy + 30, "до драйвера", size=9, color=MUTED, anchor="middle"))
    f.append(text(dx, dy + 300, "i = Cgd · dV/dt", size=11, color=BJTC, anchor="middle", bold=True))

    # ── права панель: сплеск Vgs і поріг ──
    ox, oy, w, h = 420, 320, 300, 230
    axes(f, ox, oy, w, h, "час", "Vgs (вимкнений ключ)")
    vth = 0.62
    f.append(line(ox, oy - vth * h, ox + w, oy - vth * h, color=POS, sw=1.4, dash="5 4"))
    f.append(text(ox + w - 4, oy - vth * h - 6, "Vth", size=11, color=POS, anchor="end", bold=True))
    # без клампа — горб перевалює Vth
    pts = [(ox + i / 120.0 * w, oy - min(0.90 * math.exp(-((i / 120.0 - 0.32) ** 2) / 0.010), 1.05) * h)
           for i in range(0, 121)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts), BJTC))
    f.append(text(ox + w * 0.30, oy - 0.985 * h, "без клампа: горб > Vth →",
                  size=9.5, color=BJTC, anchor="middle", bold=True))
    f.append(text(ox + w * 0.30, oy - 0.985 * h + 12, "ключ на мить проводить",
                  size=9.5, color=BJTC, anchor="middle"))
    # з клампом — горб придушено
    pts2 = [(ox + i / 120.0 * w, oy - min(0.34 * math.exp(-((i / 120.0 - 0.32) ** 2) / 0.010), 1.05) * h)
            for i in range(0, 121)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts2), FIELD))
    f.append(text(ox + w * 0.72, oy - 0.44 * h, "з клампом / малим Rg:",
                  size=9.5, color=FIELD, anchor="middle", bold=True))
    f.append(text(ox + w * 0.72, oy - 0.44 * h + 12, "горб нижче Vth",
                  size=9.5, color=FIELD, anchor="middle"))

    note = ("Межа безпеки: (dV/dt)max ≈ Vth / (Cgd · Rg). Малий Rg на вимикання й активний Міллер-кламп\n"
            "тримають затвор притиснутим до витоку, тож наведений горб не дотягує до Vth — ключ не «стрілить».")
    f.append(fitbox(60, 356, 660, 46, note, size=10, fill="#fff7e6", stroke="#b8860b", color=INK))
    render(os.path.join(IMG, "miller-turnon.svg"), W, H, *f)


if __name__ == "__main__":
    fig_iv_laws()
    fig_gm()
    fig_conduction()
    fig_thermal()
    fig_voltage_limit()
    fig_channel()
    fig_bandgap()
    fig_gate_waveform()
    fig_loss_vs_freq()
    fig_miller_turnon()
    print("OK: iv-laws, gm-comparison, conduction-crossover, thermal-stability, "
          "voltage-limit, channel-derivation, bandgap-construction, "
          "gate-waveform, loss-vs-freq, miller-turnon")
