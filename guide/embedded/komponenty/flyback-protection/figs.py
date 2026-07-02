# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Захист flyback»
(guide/embedded/komponenty/flyback-protection, версія -d).

Кут детальної: не «що робить діод», а КІЛЬКІСНО — куди йде енергія поля,
за яким законом згасає струм, чим платимо за м'якість, і як три архітектури
захисту від зворотної полярності виграють одна в одної на своїй ділянці.

Фігури:
  energy-path.svg  — куди дітися енергії поля: петля рециркуляції ↔ «продавлений» сплеск
  decay-curves.svg — i(t) = I0·e^(−t/τ): проста петля повільна, вища напруга затиску — швидше
  clamp-map.svg    — чотири схеми на площині «напруга затиску ↔ час згасання»
  ideal-diode.svg  — «ідеальний діод»: P-канал згори vs N-канал знизу, орієнтація тіла
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), "img")


# ── 1. Куди дітися енергії поля ─────────────────────────────────────────────
def fig_energy_path():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Енергія поля мусить кудись піти", size=17, bold=True))

    # Ліворуч: без шляху — «продавлений» сплеск
    lx = 180
    f.append(text(lx, 60, "Немає шляху", size=14, bold=True, color=POS))
    # котушка як прямокутник-джерело
    f.append(rect(lx-40, 90, 80, 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(lx, 120, "L", size=20, bold=True, color=INK))
    f.append(text(lx, 142, "½·L·I²", size=12, color=MUTED))
    # обрив
    f.append(line(lx, 160, lx, 210, color=INK, sw=2))
    f.append(line(lx-14, 214, lx+14, 226, color=POS, sw=3))
    f.append(line(lx-14, 226, lx+14, 238, color=POS, sw=3))
    f.append(text(lx+52, 226, "обрив", size=12, color=POS))
    # блискавка-сплеск
    f.append(text(lx, 300, "V злітає:", size=13, color=INK))
    f.append(text(lx, 322, "V = L·di/dt", size=13, bold=True, color=POS))
    f.append(text(lx, 348, "сотні вольтів → пробій", size=12, color=POS))

    # Праворуч: петля рециркуляції
    rx = 520
    f.append(text(rx, 60, "Петля рециркуляції", size=14, bold=True, color=FIELD))
    f.append(rect(rx-40, 90, 80, 70, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(rx, 120, "L", size=20, bold=True, color=INK))
    f.append(text(rx, 142, "½·L·I²", size=12, color=MUTED))
    # діод у петлі (справа)
    dx = rx+90
    f.append(line(rx+40, 110, dx, 110, color=INK, sw=2))
    f.append(line(dx, 110, dx, 205, color=INK, sw=2))
    # трикутник діода
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (dx-9, 150, dx+9, 150, dx, 168, FIELD, INK))
    f.append(line(dx-11, 168, dx+11, 168, color=INK, sw=2.5))
    f.append(text(dx+26, 162, "діод", size=12, color=FIELD))
    f.append(line(dx, 205, rx+40, 205, color=INK, sw=2))
    f.append(line(rx-40, 110, rx-70, 110, color=INK, sw=2))
    f.append(line(rx-70, 110, rx-70, 205, color=INK, sw=2))
    f.append(line(rx-70, 205, rx-40, 205, color=INK, sw=2))
    # стрілка струму по колу
    f.append(arrow(rx-70, 175, rx-70, 150, color=FIELD, sw=2.2))
    f.append(text(rx, 300, "струм тече по колу,", size=13, color=INK))
    f.append(text(rx, 322, "V ≈ Vжив + 0.7 В", size=13, bold=True, color=FIELD))
    f.append(text(rx, 348, "енергія → тепло у R", size=12, color=FIELD))

    # роздільник
    f.append(line(350, 55, 350, 355, color=MUTED, sw=1, dash="4,4"))
    render(os.path.join(IMG, "energy-path.svg"), W, H, *f)


# ── 2. Крива згасання i(t) = I0·e^(−t/τ) ────────────────────────────────────
def fig_decay_curves():
    W, H = 720, 400
    ox, oy = 90, 320          # початок осей
    pw, ph = 560, 250         # поле графіка
    f = []
    f.append(text(W/2, 26, "Згасання струму котушки після розмикання", size=17, bold=True))
    # осі
    f.append(line(ox, oy, ox+pw, oy, color=INK, sw=2))           # t
    f.append(line(ox, oy, ox, oy-ph, color=INK, sw=2))           # i
    f.append(text(ox+pw-6, oy+22, "час →", size=13, color=INK, anchor="end"))
    f.append(text(ox-12, oy-ph+4, "i(t)", size=13, color=INK, anchor="end"))
    f.append(text(ox-12, oy-ph+22, "I₀", size=12, color=MUTED, anchor="end"))
    # рівень I0
    f.append(line(ox, oy-ph+14, ox+pw, oy-ph+14, color=MUTED, sw=1, dash="3,4"))

    def curve(tau_px, color, sw=2.4):
        pts = []
        for k in range(0, pw+1, 6):
            i = math.exp(-k / tau_px)
            y = oy - 14 - (ph-28) * i
            pts.append("%.1f,%.1f" % (ox + k, y))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    # проста петля — велика τ (повільно)
    f.append(curve(190, FIELD))
    # затиск Зенером — мала τ (швидко)
    f.append(curve(70, POS))

    # позначки τ (де крива падає до 0.37·I0)
    def tau_mark(tau_px, color, label):
        x = ox + tau_px
        y37 = oy - 14 - (ph-28) * math.exp(-1)
        return (line(x, oy, x, y37, color=color, sw=1, dash="3,3")
                + text(x, oy+18, label, size=12, color=color))
    f.append(tau_mark(190, FIELD, "τ = L/R"))
    f.append(tau_mark(70, POS, "τ' = L/(R+Rz)"))
    # лінія 0.37
    f.append(text(ox-12, oy-14-(ph-28)*math.exp(-1)+4, "0.37·I₀", size=11, color=MUTED, anchor="end"))
    f.append(line(ox, oy-14-(ph-28)*math.exp(-1), ox+200, oy-14-(ph-28)*math.exp(-1),
                  color=MUTED, sw=1, dash="2,4"))

    # підписи кривих
    f.append(text(ox+300, oy-14-(ph-28)*math.exp(-300/190)-10, "проста петля (діод): м'яко, ДОВГО",
                  size=12, color=FIELD, anchor="start"))
    f.append(text(ox+150, oy-14-(ph-28)*math.exp(-150/70)-10, "діод + Зенер: жорсткіше, ШВИДКО",
                  size=12, color=POS, anchor="start"))
    render(os.path.join(IMG, "decay-curves.svg"), W, H, *f)


# ── 3. Площина «напруга затиску ↔ час згасання» ─────────────────────────────
def fig_clamp_map():
    W, H = 720, 420
    ox, oy = 90, 350
    pw, ph = 560, 290
    f = []
    f.append(text(W/2, 26, "Чим гасимо сплеск: затиск проти швидкості", size=17, bold=True))
    f.append(line(ox, oy, ox+pw, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy-ph, color=INK, sw=2))
    f.append(text(ox+pw/2, oy+34, "напруга затиску (навантаження на ключ) →", size=13, color=INK))
    # вертикальний підпис осі Y
    f.append('<text x="%d" y="%d" font-family="%s" font-size="13" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">час згасання →</text>'
             % (28, oy-ph/2, FONT, INK, 28, oy-ph/2))

    # чотири точки: (x=затиск, y=час). Вгорі повільно, праворуч — жорсткіше.
    def dot(cx, cy, label, sub, color):
        s = circle(cx, cy, 9, fill=color, stroke=INK, sw=1.5)
        s += text(cx, cy-18, label, size=13, bold=True, color=INK)
        s += text(cx, cy+26, sub, size=11, color=MUTED)
        return s
    # проста петля: низький затиск (~Vжив+0.7), дуже повільно (високо)
    f.append(dot(ox+70,  oy-250, "простий діод", "V+0.7 · найдовше", FIELD))
    # діод+Зенер: помірний затиск, помірний час
    f.append(dot(ox+250, oy-160, "діод + Зенер", "V+Vz · швидше", "#e67e22"))
    # RC-снабер: гасить дзвін, помірно
    f.append(dot(ox+330, oy-95, "RC-снабер", "гасить дзвін", NEG))
    # TVS: високий затиск, найшвидше
    f.append(dot(ox+470, oy-55, "TVS / супресор", "Vclamp · найшвидше", POS))

    # тренд-стрілка
    f.append(arrow(ox+90, oy-235, ox+455, oy-70, color=MUTED, sw=1.6))
    f.append(text(ox+300, oy-205, "жорсткіший затиск → швидше згасання", size=12,
                  color=MUTED, italic=True))
    render(os.path.join(IMG, "clamp-map.svg"), W, H, *f)


# ── 4. «Ідеальний діод»: P-канал згори vs N-канал знизу ─────────────────────
def fig_ideal_diode():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 26, "«Ідеальний діод»: MOSFET замість падіння 0.7 В", size=17, bold=True))

    # ── Ліворуч: P-канал у плюсовій шині (high-side) ──
    lx = 190
    f.append(text(lx, 58, "P-канал у «+» шині", size=14, bold=True, color=POS))
    f.append(plus(lx-90, 100, r=11))
    f.append(text(lx-90, 128, "від бат.", size=11, color=MUTED))
    # тіло FET
    f.append(rect(lx-30, 90, 60, 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(lx, 118, "PMOS", size=13, bold=True, color=INK))
    # тіло-діод (катод до входу-бат.)
    f.append(text(lx, 138, "тіло: →бат.", size=10, color=MUTED))
    f.append(line(lx-30, 110, lx-70, 110, color=INK, sw=2))
    f.append(line(lx+30, 110, lx+70, 110, color=INK, sw=2))
    f.append(text(lx+96, 114, "до схеми", size=11, color=MUTED))
    # затвор до мінуса
    f.append(line(lx, 160, lx, 195, color=INK, sw=2))
    f.append(minus(lx, 210, r=11))
    f.append(text(lx, 240, "затвор→«−»", size=11, color=NEG))
    f.append(text(lx, 300, "Vgs<0 → відкрито", size=12, color=FIELD))
    f.append(text(lx, 322, "падіння = I·Rds(on)", size=12, bold=True, color=INK))
    f.append(text(lx, 348, "мала ціна, але дорожчий FET", size=11, color=MUTED))

    # роздільник
    f.append(line(360, 50, 360, 365, color=MUTED, sw=1, dash="4,4"))

    # ── Праворуч: N-канал у зворотній шині (low-side) ──
    rx = 540
    f.append(text(rx, 58, "N-канал у «−» шині", size=14, bold=True, color=NEG))
    f.append(text(rx, 300, "Vgs>0 → відкрито", size=12, color=FIELD))
    f.append(text(rx, 322, "менший Rds(on) за ту ж ціну", size=12, bold=True, color=INK))
    f.append(text(rx, 348, "рве «землю» — стережись контурів", size=11, color=MUTED))
    # схема-навантаження зверху
    f.append(rect(rx-30, 80, 60, 46, fill=FILL, stroke=INK, sw=1.5))
    f.append(text(rx, 108, "схема", size=12, color=INK))
    f.append(plus(rx-90, 103, r=11))
    f.append(line(rx-79, 103, rx-30, 103, color=INK, sw=2))
    # FET знизу
    f.append(rect(rx-30, 150, 60, 66, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(rx, 178, "NMOS", size=13, bold=True, color=INK))
    f.append(text(rx, 198, "тіло: →земля", size=10, color=MUTED))
    f.append(line(rx, 126, rx, 150, color=INK, sw=2))
    f.append(line(rx, 216, rx, 240, color=INK, sw=2))
    f.append(minus(rx, 252, r=11))
    f.append(text(rx, 280, "до «−» бат.", size=11, color=MUTED))
    # затвор до плюса
    f.append(line(rx+30, 183, rx+64, 183, color=INK, sw=2))
    f.append(line(rx+64, 183, rx+64, 103, color=POS, sw=1.6, dash="3,3"))
    f.append(text(rx+64, 96, "затвор→«+»", size=10, color=POS, anchor="middle"))
    render(os.path.join(IMG, "ideal-diode.svg"), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
#  Фігури до вставки comp-ideal-diode-controller.md
#  (клас мікросхем-контролерів «ідеального діода»)
# ═══════════════════════════════════════════════════════════════════════════

# ── 5. Блок-схема класу: силовий тракт + нутрощі контролера ──────────────────
def fig_controller_block():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Контролер «ідеального діода»: силовий тракт і нутрощі", size=17, bold=True))

    # силовий тракт угорі: ANODE(VIN) → N-MOSFET → CATHODE(VOUT)
    ty = 78
    f.append(text(70, ty-18, "вхід", size=12, color=MUTED))
    f.append(plus(70, ty, r=11))
    f.append(line(81, ty, 300, ty, color=INK, sw=3))            # товста силова
    # тіло N-MOSFET
    f.append(rect(300, ty-30, 90, 60, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(345, ty-6, "N-MOSFET", size=12, bold=True, color=INK))
    f.append(text(345, ty+14, "падіння = I·Rds", size=10, color=MUTED))
    f.append(line(390, ty, 630, ty, color=INK, sw=3))
    f.append(text(660, ty-18, "вихід", size=12, color=MUTED))
    f.append(plus(660, ty, r=11))
    f.append(text(140, ty-16, "ANODE", size=11, color=INK))
    f.append(text(560, ty-16, "CATHODE", size=11, color=INK))

    # корпус контролера
    bx, by, bw, bh = 250, 150, 300, 210
    f.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke=INK, sw=2))
    f.append(text(bx+bw/2, by-8, "контролер", size=13, bold=True, color=INK))

    # чотири внутрішні блоки
    f.append(fitbox(bx+18, by+18, 122, 46, "підсилювач\nпохибки Vds", size=11, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(bx+160, by+18, 122, 46, "серво затвора\n(тримає ~20 мВ)", size=11, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(bx+18, by+82, 122, 46, "компаратор\nзворотного струму", size=11, fill="#fdecea", stroke=POS))
    f.append(fitbox(bx+160, by+82, 122, 46, "зарядний насос\n(затвор > входу)", size=11, fill="#fff4e5", stroke="#e67e22"))

    # щупи від контролера до тракту: ANODE, CATHODE, GATE
    f.append(line(bx+40, by, 140, ty+11, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(150, 128, "щуп ANODE", size=10, color=FIELD, anchor="start"))
    f.append(line(bx+bw-40, by, 560, ty+11, color=FIELD, sw=1.6, dash="4,3"))
    f.append(text(470, 128, "щуп CATHODE", size=10, color=FIELD, anchor="start"))
    # GATE вниз-вгору до затвора MOSFET
    f.append(line(bx+bw/2, by, bx+bw/2, 118, color="#e67e22", sw=2))
    f.append(line(bx+bw/2, 118, 345, 118, color="#e67e22", sw=2))
    f.append(line(345, 118, 345, ty+30, color="#e67e22", sw=2))
    f.append(text(bx+bw/2+6, 138, "GATE", size=10, color="#e67e22", anchor="start"))

    # сигнальні ніжки знизу
    sy = by+bh
    for i,(lbl,col) in enumerate([("VDD",INK),("EN/UVLO",INK),("GND",INK),("FLT",POS)]):
        x = bx+40 + i*72
        f.append(line(x, sy, x, sy+22, color=INK, sw=1.6))
        f.append(text(x, sy+38, lbl, size=10, color=col))

    f.append(text(W/2, H-8, "Сенсор — саме падіння на MOSFET (ANODE↔CATHODE), а не окремий шунт",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "controller-block.svg"), W, H, *f)


# ── 6. Серво падіння: три режими на осі Vds(струм) ──────────────────────────
def fig_servo_regulation():
    W, H = 760, 420
    ox, oy = 110, 300
    pw, ph = 560, 230
    f = []
    f.append(text(W/2, 26, "Як серво тримає падіння: три режими роботи", size=17, bold=True))
    # осі: X — струм (від'ємний ліворуч = зворотний), Y — падіння Vds
    f.append(line(ox, oy, ox+pw, oy, color=INK, sw=2))
    f.append(line(ox+pw*0.28, oy-ph, ox+pw*0.28, oy+40, color=INK, sw=2))   # вісь Y зсунута (0 струму)
    x0 = ox+pw*0.28
    f.append(text(ox+pw-4, oy+24, "струм у навантаження →", size=12, color=INK, anchor="end"))
    f.append(text(ox+6, oy+24, "← зворотний", size=11, color=POS, anchor="start"))
    f.append(text(x0-8, oy-ph+6, "падіння Vds", size=12, color=INK, anchor="end"))

    # лінія цілі 20 мВ
    ytar = oy - 70
    f.append(line(x0, ytar, ox+pw, ytar, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox+pw-4, ytar-6, "ціль ≈ 20 мВ", size=11, color=MUTED, anchor="end"))

    # режим 1: зворотний струм → канал закрито (ліворуч від 0)
    f.append(rect(ox, oy-ph, x0-ox, ph, fill="#fdecea", stroke="none"))
    f.append(text((ox+x0)/2, oy-ph+20, "зворотний", size=12, bold=True, color=POS))
    f.append(text((ox+x0)/2, oy-ph+38, "струм", size=12, bold=True, color=POS))
    f.append(text((ox+x0)/2, oy-ph+64, "GATE зірвано в 0", size=10, color=POS))
    f.append(text((ox+x0)/2, oy-ph+80, "канал закрито", size=10, color=POS))

    # режим 2: регуляція — падіння тримається на цілі, поки серво має запас
    # (від малого струму до струму зламу i_knee, де gate вже full-on)
    xk = x0 + pw*0.40
    f.append(line(x0, ytar, xk, ytar, color=FIELD, sw=3))
    f.append(text((x0+xk)/2, ytar-14, "серво тримає ~20 мВ", size=11, color=FIELD))
    f.append(text((x0+xk)/2, oy-30, "легке навантаження:", size=10, color=MUTED))
    f.append(text((x0+xk)/2, oy-16, "GATE прикрито", size=10, color=MUTED))
    # точка зламу
    f.append(circle(xk, ytar, 5, fill=FIELD, stroke=INK, sw=1.3))
    f.append(text(xk, ytar+18, "злам", size=10, color=INK))

    # режим 3: важке навантаження — gate full-on, падіння росте як I·Rds
    xe = ox+pw-10
    ye = oy - 175
    f.append(line(xk, ytar, xe, ye, color=NEG, sw=3))
    f.append(text((xk+xe)/2+10, (ytar+ye)/2-10, "важке: GATE навстіж,", size=10, color=NEG, anchor="middle"))
    f.append(text((xk+xe)/2+10, (ytar+ye)/2+6, "падіння = I·Rds(on)", size=10, color=NEG, anchor="middle"))

    render(os.path.join(IMG, "servo-regulation.svg"), W, H, *f)


# ── 7. ORing двох джерел через ідеальні діоди ───────────────────────────────
def fig_oring():
    W, H = 760, 400
    f = []
    f.append(text(W/2, 26, "ORing: два джерела на спільну шину без втрат і без зустрічного струму", size=15, bold=True))

    # два входи ліворуч
    def source(cx, cy, label, volt, hot):
        s = plus(cx, cy, r=12)
        s += text(cx, cy-22, label, size=12, bold=True, color=INK)
        s += text(cx, cy+30, volt, size=11, color=(POS if hot else MUTED))
        return s
    f.append(source(90, 130, "джерело A", "12.0 В (вище)", True))
    f.append(source(90, 280, "джерело B", "11.6 В", False))

    # ідеальні діоди (контролер+MOSFET) як блоки
    def iddiode(x, y, active):
        col = FIELD if active else MUTED
        s = rect(x, y-28, 130, 56, fill=("#eafaf1" if active else "#f0f0f0"), stroke=col, sw=2)
        s += text(x+65, y-6, "ідеальний діод", size=11, bold=True, color=INK)
        s += text(x+65, y+12, ("веде" if active else "відсічено"), size=11, color=col)
        return s
    f.append(line(102, 130, 250, 130, color=INK, sw=3))
    f.append(iddiode(250, 130, True))
    f.append(line(102, 280, 250, 280, color=INK, sw=3))
    f.append(iddiode(250, 280, False))

    # спільна шина
    busx = 520
    f.append(line(380, 130, busx, 130, color=INK, sw=3))
    f.append(line(380, 280, busx, 280, color=INK, sw=3))
    f.append(line(busx, 110, busx, 300, color=INK, sw=3))
    f.append(text(busx, 96, "спільна шина", size=12, bold=True, color=INK))
    # навантаження
    f.append(line(busx, 205, 640, 205, color=INK, sw=3))
    f.append(rect(640, 175, 80, 60, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(680, 210, "плата", size=12, color=INK))
    f.append(text(680, 250, "12.0 В − 20 мВ", size=10, color=FIELD))

    # напрям і блокування
    f.append(arrow(300, 165, 300, 250, color=POS, sw=2))
    f.append(text(320, 210, "зустрічний\nструм?", size=10, color=POS, anchor="start"))
    f.append(text(315, 300, "ні — компаратор тримає B закритим", size=10, color=POS, anchor="start"))
    render(os.path.join(IMG, "oring.svg"), W, H, *f)


if __name__ == "__main__":
    IMG = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.isdir(IMG):
        os.makedirs(IMG)
    fig_energy_path()
    fig_decay_curves()
    fig_clamp_map()
    fig_ideal_diode()
    fig_controller_block()
    fig_servo_regulation()
    fig_oring()
    print("OK: 7 figures written to", IMG)
