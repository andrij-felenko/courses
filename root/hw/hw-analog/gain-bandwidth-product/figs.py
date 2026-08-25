# -*- coding: utf-8 -*-
"""Фігури до теми «Добуток підсилення на смугу».
Запуск:  python figs.py   → пише SVG у ./img/
Чотири фігури:
  rolloff.svg  — спадна пряма розімкненого підсилення; полиці замкнення сідають на неї
  area.svg     — прямокутник сталої площі: підсилення × смуга = const
  cascade.svg  — один великий каскад проти двох помірних: ширша смуга
  pole.svg     — звідки спад: внутрішня RC-ланка ріже високі частоти
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # тепла мідь для дротів


# ── 1. Спадна пряма й полиці замкнення на ній ───────────────────────────────
def fig_rolloff():
    W, H = 840, 470
    f = [text(W / 2, 30, "Одна спадна пряма — і всі полиці сідають на неї", size=17, bold=True),
         text(W / 2, 52, "де полиця підсилення впирається в похилу — там кінчається смуга; добуток той самий",
              size=12, color=MUTED, italic=True)]

    # поле графіка (обидві осі логарифмічні: декади підсилення × декади частоти)
    L, R, T, B = 90, 730, 90, 380
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(R, B + 26, "частота (лог)", size=13, bold=True, anchor="end"))
    f.append(text(L + 4, T - 10, "підсилення (лог)", size=13, bold=True, anchor="start"))

    # вертикальні поділки частоти: декади 1..6 (умовно МГц на кінці)
    n_dec_f = 6
    def fx(dec):  # dec у [0..n_dec_f]
        return L + (R - L) * dec / n_dec_f
    flabels = ["", "10", "100", "1к", "10к", "100к", "1М"]
    for d in range(n_dec_f + 1):
        x = fx(d)
        f.append(line(x, T, x, B, color="#eef0f2", sw=1))
        if flabels[d]:
            f.append(text(x, B + 16, flabels[d], size=10, color=MUTED))

    # горизонтальні поділки підсилення: 1, 10, 100, 1000, 10000, 100000
    n_dec_g = 5
    def gy(dec):  # dec у [0..n_dec_g], 0 = підсилення 1 (унизу)
        return B - (B - T) * dec / n_dec_g
    glabels = ["1", "10", "100", "1к", "10к", "100к"]
    for d in range(n_dec_g + 1):
        y = gy(d)
        f.append(line(L, y, R, y, color="#eef0f2", sw=1))
        f.append(text(L - 8, y + 4, glabels[d], size=10, color=MUTED, anchor="end"))

    # ПОХИЛА: розімкнене підсилення. На лог-лог −20 дБ/дек = пряма
    # від (підсилення 100к на низькій частоті) до (підсилення 1 на f_t = 1 МГц).
    # У наших координатах: декада підсилення на декаду частоти → нахил 1.
    # точка зламу розімкненого: підсилення 100к тримається до ~10 Гц (dec_f=1), далі котиться.
    x_open_break = fx(1.0)
    # пряма йде так, що падає рівно на 1 декаду підсилення за 1 декаду частоти
    # від (fx(1), gy(5)) до (fx(6), gy(0))
    f.append(line(L, gy(5), x_open_break, gy(5), color=INK, sw=2.6))
    f.append(line(x_open_break, gy(5), fx(6), gy(0), color=INK, sw=2.6))
    f.append(text(fx(2.0) + 6, gy(4.2) - 6, "розімкнене A", size=12.5, bold=True,
                  color=INK, anchor="start"))
    f.append(text(fx(5.0), gy(0.0) + 0, "", size=10))
    # точка f_t (підсилення = 1)
    f.append(circle(fx(6), gy(0), 5, fill=POS, stroke=POS))
    f.append(text(fx(6) - 4, gy(0) - 12, "f_t (A=1)", size=11.5, color=POS, bold=True, anchor="end"))

    # ТРИ полиці замкнення на різному підсиленні: 1000, 100, 10
    shelves = [(3, NEG, "×1000"), (2, FIELD, "×100"), (1, POS, "×10")]
    for dec_g, col, lab in shelves:
        y = gy(dec_g)
        # полиця тримається до перетину з похилою: на похилій підсилення dec_g
        # відповідає частоті, де decf = dec_g + (поч.зламу). Похила: g_dec = 5 - (decf-1)
        # => decf = 6 - dec_g
        decf_corner = 6 - dec_g
        xc = fx(decf_corner)
        f.append(line(L, y, xc, y, color=col, sw=2.2, dash="6 4"))
        # після кутка полиця падає вздовж похилої (пунктир легший)
        f.append(circle(xc, y, 4.5, fill=BG, stroke=col, sw=2.2))
        f.append(text(L + 8, y - 7, lab, size=11, color=col, bold=True, anchor="start"))
        # підпис смуги під кутком
        f.append(text(xc, y + 16, "смуга", size=10, color=col, anchor="middle"))

    # висновок-рамка (рядки розбито вручну, щоб шрифт лишався читабельним)
    f.append(fitbox(L + 6, 396, R - L - 12, 60,
                    ["Полиця × її смуга = та сама відстань до f_t.",
                     "×10 дає смугу вдесятеро ширшу за ×100 — добуток «підсилення × смуга» не міняється."],
                    size=12.5, fill="#eaf6ee", stroke=FIELD, sw=1.6, bold=True))
    render(os.path.join(IMG, "rolloff.svg"), W, H, *f)


# ── 2. Прямокутник сталої площі ─────────────────────────────────────────────
def fig_area():
    W, H = 760, 430
    f = [text(W / 2, 30, "Площа прямокутника стала: тягнеш ширину — падає висота", size=17, bold=True),
         text(W / 2, 52, "висота = підсилення, ширина = смуга; їхній добуток (площа) заданий приладом",
              size=12, color=MUTED, italic=True)]

    # осі
    Ox, Oy = 110, 360            # початок координат
    AX = 660                     # права межа осі частоти
    AY = 90                      # верхня межа осі підсилення
    f.append(line(Ox, Oy, Ox, AY, color=INK, sw=2))
    f.append(line(Ox, Oy, AX, Oy, color=INK, sw=2))
    f.append(text(AX, Oy + 26, "смуга →", size=13, bold=True, anchor="end"))
    f.append(text(Ox + 4, AY - 10, "підсилення →", size=13, bold=True, anchor="start"))

    # стала площа: g * b = K. Беремо K і малюємо два прямокутники.
    # координатний масштаб: 1 одиниця підсилення = sg px, 1 одиниця смуги = sb px
    sg = (Oy - AY) / 11.0
    sb = (AX - Ox) / 11.0
    K = 20.0

    def rect_for(gain):
        b = K / gain
        w = b * sb
        h = gain * sg
        x = Ox
        y = Oy - h
        return x, y, w, h, b

    # прямокутник А: високе підсилення, вузька смуга
    gA = 10.0
    xA, yA, wA, hA, bA = rect_for(gA)
    f.append(rect(xA, yA, wA, hA, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=2))
    f.append(text(xA + wA / 2, yA - 8, "вузька смуга", size=11, color=NEG, bold=True))
    f.append(text(xA - 8, yA + hA / 2, "велике", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(xA - 8, yA + hA / 2 + 14, "підс.", size=11, color=NEG, bold=True, anchor="end"))

    # прямокутник Б: помірне підсилення, ширша смуга
    gB = 4.0
    xB, yB, wB, hB, bB = rect_for(gB)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="7 4"/>'
             % (xB, yB, wB, hB, POS))
    f.append(text(xB + wB - 4, yB - 8, "ширша смуга", size=11, color=POS, bold=True, anchor="end"))
    f.append(text(xB + wB + 8, yB + hB / 2, "менше", size=11, color=POS, bold=True, anchor="start"))
    f.append(text(xB + wB + 8, yB + hB / 2 + 14, "підс.", size=11, color=POS, bold=True, anchor="start"))

    # підпис рівної площі по центру меншого прямокутника
    f.append(text(Ox + 64, Oy - 36, "площа", size=12, color=INK, bold=True, anchor="middle"))
    f.append(text(Ox + 64, Oy - 20, "однакова", size=12, color=INK, bold=True, anchor="middle"))

    # формула-рамка
    box, bw, bh = textbox(W / 2, 404, "підсилення × смуга = GBW = const",
                          size=14, bold=True, fill="#eaf6ee", stroke=FIELD, sw=1.6)
    f.append(box)
    render(os.path.join(IMG, "area.svg"), W, H, *f)


# ── 3. Один великий каскад проти двох помірних ──────────────────────────────
def fig_cascade():
    W, H = 840, 420
    f = [text(W / 2, 30, "Те саме сумарне підсилення — а смуга ширша двома каскадами", size=17, bold=True),
         text(W / 2, 52, "×900 одним махом дає вузьку смугу; два по ×30 (теж ×900) тримають ширшу",
              size=12, color=MUTED, italic=True)]

    # верхній ряд: один каскад ×900
    y1 = 130
    f.append(text(70, y1 - 44, "Один каскад", size=13, bold=True, anchor="start"))
    f.append(line(70, y1, 150, y1, color=WIRE, sw=2.4))
    box1 = fitbox(150, y1 - 30, 150, 60, "×900", size=20, fill="#eaf0fd", stroke=NEG, sw=2.2, bold=True)
    f.append(box1)
    f.append(line(300, y1, 380, y1, color=WIRE, sw=2.4))
    # смуга під ним
    f.append(text(385, y1, "смуга = GBW/900", size=12.5, color=NEG, bold=True, anchor="start"))
    f.append(text(385, y1 + 18, "= 1.1 кГц (вузька)", size=11.5, color=MUTED, anchor="start"))

    # нижній ряд: два каскади по ×30
    y2 = 280
    f.append(text(70, y2 - 44, "Два каскади", size=13, bold=True, anchor="start"))
    f.append(line(70, y2, 130, y2, color=WIRE, sw=2.4))
    f.append(fitbox(130, y2 - 30, 110, 60, "×30", size=18, fill="#eaf6ee", stroke=FIELD, sw=2.2, bold=True))
    f.append(line(240, y2, 300, y2, color=WIRE, sw=2.4))
    f.append(fitbox(300, y2 - 30, 110, 60, "×30", size=18, fill="#eaf6ee", stroke=FIELD, sw=2.2, bold=True))
    f.append(line(410, y2, 470, y2, color=WIRE, sw=2.4))
    f.append(text(478, y2 - 4, "кожен: смуга = GBW/30", size=12.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(478, y2 + 14, "= 33 кГц на каскад", size=11.5, color=MUTED, anchor="start"))
    f.append(text(478, y2 + 32, "разом ≈ 21 кГц (ширша!)", size=11.5, color=POS, bold=True, anchor="start"))

    # роздільна лінія
    f.append(line(60, 205, W - 60, 205, color="#e0e0e0", sw=1))

    # підсумок (GBW=1 МГц)
    f.append(fitbox(60, 348, W - 120, 54,
                    ["GBW = 1 МГц у обох. Те саме сумарне ×900 — але розкладене по двох каскадах",
                     "віддає у ~19 разів ширшу смугу. Велике підсилення вигідно ділити."],
                    size=12.5, fill=FILL, stroke=LINE, sw=1.4, bold=True))
    render(os.path.join(IMG, "cascade.svg"), W, H, *f)


# ── 4. Звідки спад: внутрішня RC-ланка ───────────────────────────────────────
def fig_pole():
    W, H = 820, 410
    f = [text(W / 2, 30, "Звідки сам спад: одна повільна RC-ланка всередині", size=17, bold=True),
         text(W / 2, 52, "корекційна ємність навмисне робить одну ланку «вузьким місцем» — спад рівний −20 дБ/дек",
              size=12, color=MUTED, italic=True)]

    # ліворуч: схемка R-C (дільник), пояснення
    cx = 70
    midy = 200
    f.append(text(cx + 110, 92, "усередині підсилювача", size=12.5, bold=True, anchor="middle"))
    # вхід
    f.append(line(cx, midy, cx + 60, midy, color=WIRE, sw=2.4))
    f.append(text(cx, midy - 12, "сигнал", size=11, color=MUTED, anchor="start"))
    # резистор (велика вихідна провідність ланки) — прямокутник
    f.append(rect(cx + 60, midy - 12, 70, 24, fill=FILL, stroke=INK, sw=1.8, rx=3))
    f.append(text(cx + 95, midy + 5, "R", size=13, bold=True))
    # вузол
    node_x = cx + 130
    f.append(line(node_x, midy, node_x + 70, midy, color=WIRE, sw=2.4))
    f.append(circle(node_x, midy, 4, fill=INK, stroke=INK))
    # конденсатор на землю
    capx = node_x
    f.append(line(capx, midy, capx, midy + 34, color=WIRE, sw=2.4))
    f.append(line(capx - 16, midy + 34, capx + 16, midy + 34, color=INK, sw=2.6))
    f.append(line(capx - 16, midy + 44, capx + 16, midy + 44, color=INK, sw=2.6))
    f.append(text(capx + 22, midy + 42, "C (корекція)", size=11, bold=True, anchor="start"))
    # земля
    gy0 = midy + 60
    f.append(line(capx, midy + 44, capx, gy0, color=INK, sw=1.6))
    f.append(line(capx - 12, gy0, capx + 12, gy0, color=INK, sw=2))
    f.append(line(capx - 7, gy0 + 5, capx + 7, gy0 + 5, color=INK, sw=1.6))
    f.append(line(capx - 3, gy0 + 10, capx + 3, gy0 + 10, color=INK, sw=1.6))
    # вихід ланки
    f.append(text(node_x + 74, midy - 12, "далі", size=11, color=MUTED, anchor="start"))

    # пояснювальна рамка під схемою (рядки розбито вручну)
    f.append(fitbox(cx, 298, 320, 72,
                    ["Низькі частоти C не пропускає —",
                     "підсилення повне. Високі — C коротить",
                     "вузол на землю, сигнал слабшає:",
                     "−20 дБ за декаду."],
                    size=11.5, fill=FILL, stroke=LINE, sw=1.4))

    # праворуч: маленький лог-лог графік спаду від f_p
    GL, GR, GT, GB = 460, 760, 100, 300
    f.append(line(GL, GT, GL, GB, color=INK, sw=1.8))
    f.append(line(GL, GB, GR, GB, color=INK, sw=1.8))
    f.append(text(GR, GB + 22, "f (лог)", size=12, bold=True, anchor="end"))
    f.append(text(GL + 2, GT - 8, "A (лог)", size=12, bold=True, anchor="start"))
    # полиця до f_p, далі похила
    xp = GL + (GR - GL) * 0.32
    f.append(line(GL, GT + 24, xp, GT + 24, color=INK, sw=2.6))
    f.append(line(xp, GT + 24, GR - 16, GB - 14, color=INK, sw=2.6))
    f.append(circle(xp, GT + 24, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(xp + 6, GT + 18, "f_p", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(xp + 70, GT + 70, "−20 дБ/дек", size=11.5, bold=True, anchor="start"))
    f.append(text((GL + GR) / 2, GB + 44, "одна ланка → один злам → рівний нахил",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "pole.svg"), W, H, *f)


if __name__ == "__main__":
    fig_rolloff()
    fig_area()
    fig_cascade()
    fig_pole()
    print("OK: 4 SVG -> img/")
