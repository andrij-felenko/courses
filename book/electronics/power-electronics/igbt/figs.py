# -*- coding: utf-8 -*-
"""Фігури до теми «IGBT» та її історичної вставки «Баліга, RCA проти GE…».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def tri(x1, y1, x2, y2, color, sw=2.2):
    """Стрілка кольоровою лінією з трикутним наконечником на кінці (x2,y2).
    svgkit має лише один marker; тут наконечник домальовуємо вручну, щоб тримати колір."""
    import math
    out = [line(x1, y1, x2, y2, color=color, sw=sw)]
    ang = math.atan2(y2 - y1, x2 - x1)
    s = 7.0
    bx, by = x2 - s * math.cos(ang), y2 - s * math.sin(ang)
    px, py = -math.sin(ang) * s * 0.6, math.cos(ang) * s * 0.6
    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        x2, y2, bx + px, by + py, bx - px, by - py, color))
    return "".join(out)


# ═════════════════════ ФІГУРИ СТАТТІ «IGBT» ═════════════════════════════════

# ── 1. Гібрид: польовий вхід (MOSFET) + біполярний вихід (BJT) ────────────────
def fig_hybrid():
    W, H = 860, 320
    f = [text(W / 2, 26, "IGBT: польовий затвор спереду, біполярна провідність ззаду",
              size=15, bold=True)]

    # ЛІВА панель — вхід як у MOSFET
    f.append(rect(40, 56, 360, 226, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(220, 80, "вхід — як у MOSFET", size=12.5, bold=True, color=INK))
    # затвор / оксид / канал
    f.append(rect(150, 116, 140, 24, fill="#cfd6dd", stroke=INK, sw=1.6, rx=0))
    f.append(text(220, 132, "затвор (G)", size=11, bold=True, color=FIELD))
    f.append(rect(150, 140, 140, 14, fill="#fff3b0", stroke="#e0a32e", sw=1.4, rx=0))
    f.append(text(220, 151, "оксид (ізолятор)", size=9, color=INK))
    f.append(rect(150, 154, 140, 30, fill="#e3edfb", stroke=INK, sw=1.6, rx=0))
    f.append(text(220, 173, "канал", size=10.5, color=INK))
    f.append(text(220, 212, "керує НАПРУГА", size=11.5, bold=True, color=FIELD))
    f.append(text(220, 230, "струм затвора ≈ 0", size=10, color=INK))
    f.append(text(220, 256, "(легко гнати навіть від драйвера логіки)", size=9.5, color=MUTED, italic=True))

    # стрілка-«плюс» між панелями
    f.append(tri(404, 168, 452, 168, MUTED, sw=2.6))
    f.append(text(428, 158, "+", size=18, color=MUTED, bold=True))

    # ПРАВА панель — вихід як у BJT
    f.append(rect(460, 56, 360, 226, fill=BG, stroke="#c9d3dc", sw=1.6, rx=10))
    f.append(text(640, 80, "вихід — як у BJT", size=12.5, bold=True, color=INK))
    f.append(text(640, 100, "колектор (C)", size=10, bold=True, color=INK))
    # шар p / n із впорснутими дірками
    f.append('<path d="M 600,118 L 680,118 L 680,198 L 600,198 Z" fill="#f6dede" stroke="%s" stroke-width="1.5"/>' % INK)
    f.append(text(640, 134, "p", size=12, bold=True, color=POS))
    f.append(text(640, 190, "n", size=12, bold=True, color=NEG))
    f.append(line(640, 108, 640, 118, color=INK, sw=2))
    f.append(line(640, 198, 640, 208, color=INK, sw=2))
    for (cx, cy) in [(620, 150), (655, 158), (638, 170), (665, 146), (615, 178)]:
        f.append(circle(cx, cy, 4, fill="#f3c6c6", stroke=POS, sw=1.2))
    f.append(text(640, 230, "провідність БІПОЛЯРНА", size=11, bold=True, color=POS))
    f.append(text(640, 248, "впорскування дірок → малий спад на сотнях В", size=9, color=INK))
    f.append(text(640, 270, "емітер (E)", size=10, bold=True, color=INK))
    return render(os.path.join(IMG, "hybrid.svg"), W, H, *f)


# ── 2. Спад напруги від струму: MOSFET (пряма) проти IGBT (поріг + полого) ────
def fig_mosfet_vs_igbt():
    W, H = 760, 360
    f = [text(W / 2, 26, "Спад напруги від струму: MOSFET проти IGBT", size=15, bold=True)]
    # осі
    ox, oy = 90, 290
    f.append(line(ox, oy, ox, 46, color=INK, sw=1.8))
    f.append(line(ox, oy, 664, oy, color=INK, sw=1.8))
    f.append(text(672, 294, "струм I", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(84, 40, "спад напруги U(on)", size=12, bold=True, color=INK))
    # MOSFET — пряма з нуля, круто вгору
    f.append('<path d="M %.0f,%.0f L 650,70" fill="none" stroke="%s" stroke-width="2.8"/>' % (ox, oy, NEG))
    f.append(text(644, 84, "MOSFET: U = I·Rds(on)", size=10.5, bold=True, color=NEG, anchor="end"))
    f.append(text(486, 120, "круто росте з I", size=9, color=NEG))
    # IGBT — від порогу ~0.8 В, далі полого
    f.append('<path d="M %.0f,250 L 650,158" fill="none" stroke="%s" stroke-width="2.8"/>' % (ox, POS))
    f.append(text(644, 150, "IGBT: поріг + I·r", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(text(84, 254, "≈0.8 В", size=9, bold=True, color=POS, anchor="end"))
    f.append(text(430, 210, "полого: спад майже сталий", size=9, color=POS))
    # точка перетину = межа
    f.append(circle(264, 222, 6, fill="#fff3b0", stroke="#e0a32e", sw=2))
    f.append(line(264, 222, 264, oy, color=MUTED, sw=1.3, dash="3,3"))
    f.append(text(264, 308, "межа", size=10, bold=True, color="#e0a32e"))
    f.append(text(178, 328, "← тут вигідніший MOSFET", size=9.5, bold=True, color=NEG))
    f.append(text(458, 328, "тут вигідніший IGBT →", size=9.5, bold=True, color=POS))
    return render(os.path.join(IMG, "mosfet-vs-igbt.svg"), W, H, *f)


# ══════════ ФІГУРИ ВСТАВКИ «Баліга, RCA проти GE…» ══════════════════════════

# ── 3. Стрічка часу: чотири незалежні внески за п'ятнадцять років ─────────────
def fig_igbt_timeline():
    W, H = 900, 540
    f = [text(W / 2, 28, "Спірне батьківство IGBT: чотири незалежні внески за п'ятнадцять років",
              size=16, bold=True)]
    # вісь часу
    ax0, ax1, ay = 70, 830, 250
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=3))
    f.append(tri(ax1, ay, ax1 + 18, ay, INK, sw=3))

    def year_x(y):  # 1968 → ax0 ; 1986 → 792
        return ax0 + 38 + (y - 1968) * 38.0

    for yr in range(1968, 1987, 2):
        x = year_x(yr)
        f.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.5))
        f.append(text(x, ay + 22, str(yr), size=12, color=MUTED))

    # смуга «десять років нікому не потрібно»
    gx0, gx1 = year_x(1968), year_x(1978)
    f.append(rect(gx0, ay - 36, gx1 - gx0, 18, fill="#e4e4e4", stroke="none", sw=0, rx=0))
    f.append(text((gx0 + gx1) / 2, ay - 23, "десять років ідея нікому не потрібна",
                  size=11, color=MUTED, italic=True))

    def event(yr, up, color, fill, title, who, what):
        x = year_x(yr)
        f.append(circle(x, ay, 5, fill=color, stroke=color, sw=2))
        bw, bh = 172, 66
        if up:
            f.append(line(x, ay - 6, x, ay - 86, color=color, sw=2, dash="3,3"))
            by = ay - 86 - bh
        else:
            f.append(line(x, ay + 6, x, ay + 70, color=color, sw=2, dash="3,3"))
            by = ay + 70
        bx = x - bw / 2
        f.append(rect(bx, by, bw, bh, fill=fill, stroke=color, sw=2, rx=7))
        f.append(text(x, by + 20, title, size=12, bold=True, color=color))
        f.append(text(x, by + 38, who, size=11, color=INK))
        f.append(text(x, by + 54, what, size=10, color=INK))

    event(1968, True, NEG, "#e9eefb", "1968 · ідея на папері", "Ямаґамі, Акаґірі", "Mitsubishi · яп. заявка")
    event(1978, False, FIELD, "#eef6ef", "1978 · перші прилади", "Пламмер, Шарф", "Stanford · патент + ISSCC")
    event(1979, True, POS, "#fbecec", "1979 · виготовив і виміряв", "Баліга (GE)", "стаття, Electronics Letters")
    # RCA 1980 — нижче, окремо від Стенфорда, щоб не злипалось
    x80 = year_x(1980)
    f.append(circle(x80, ay, 5, fill=INK, stroke=INK, sw=2))
    f.append(line(x80, ay + 6, x80, ay + 150, color=INK, sw=2, dash="3,3"))
    f.append(rect(x80 - 86, ay + 150, 172, 66, fill="#e4e4e4", stroke=INK, sw=2, rx=7))
    f.append(text(x80, ay + 170, "1980 · конкурентний патент", size=12, bold=True, color=INK))
    f.append(text(x80, ay + 188, "Бекке, Вітлі (RCA)", size=11, color=INK))
    f.append(text(x80, ay + 204, "видано 1982, US 4,364,073", size=10, color=INK))
    event(1985, True, "#caa24a", "#fbf3df", "1984–85 · без защіпки", "Накаґава (Toshiba)", "«справжнє народження»")

    # дужка «чотири команди — за ~2 роки» (1978…1980)
    bx0, bx1, byb = year_x(1978), year_x(1980), ay + 232
    f.append(line(bx0, byb, bx1, byb, color=MUTED, sw=1.5))
    f.append(line(bx0, byb - 6, bx0, byb, color=MUTED, sw=1.5))
    f.append(line(bx1, byb - 6, bx1, byb, color=MUTED, sw=1.5))
    f.append(text((bx0 + bx1) / 2, byb + 16, "тісне скупчення команд", size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "igbt-timeline.svg"), W, H, *f)


# ── 4. Паразитний тиристор усередині IGBT і механізм защіпки ──────────────────
def fig_latchup():
    W, H = 900, 360
    f = [text(W / 2, 26, "Схований PNPN усередині IGBT: корисний PNP і паразитний NPN",
              size=16, bold=True)]

    # ЛІВО — переріз чотирьох шарів
    f.append(text(220, 56, "Переріз: ті самі чотири шари", size=12.5, bold=True, color=INK))
    lx, lw = 70, 300
    layers = [
        ("затвор (MOS) — керує каналом", "#dfe6ef", INK, 22),
        ("p (тіло)", "#fbecec", POS, 38),
        ("n− (дрейф, тримає напругу)", "#e9eefb", NEG, 48),
        ("p+ (анод) — нове проти MOSFET", "#fbecec", POS, 28),
        ("колектор", "#dfe6ef", INK, 22),
    ]
    y = 70
    # два n+ острівці у шарі затвора
    f.append(rect(lx, y, lw, 22, fill="#dfe6ef", stroke=INK, sw=1.4))
    f.append(text(lx + lw / 2, y + 15, "затвор (MOS) — керує каналом", size=10.5, color=INK))
    f.append(rect(lx, y, 60, 22, fill="#e9eefb", stroke=INK, sw=1.4))
    f.append(text(lx + 30, y + 15, "n+", size=11, bold=True, color=NEG))
    f.append(rect(lx + lw - 60, y, 60, 22, fill="#e9eefb", stroke=INK, sw=1.4))
    f.append(text(lx + lw - 30, y + 15, "n+", size=11, bold=True, color=NEG))
    y += 22
    for label, fill, col, h in layers[1:]:
        f.append(rect(lx, y, lw, h, fill=fill, stroke=INK, sw=1.4))
        f.append(text(lx + lw / 2, y + h / 2 + 4, label, size=10.5, bold=(col != INK), color=col))
        y += h
    f.append(text(220, y + 26, "Чотири шари n+/p/n−/p+ — це схований PNPN-тиристор",
                  size=10.5, color=MUTED, italic=True))

    # ПРАВО — що це насправді: PNP + паразитний NPN
    f.append(text(660, 56, "Що це насправді:", size=13.5, bold=True, color=INK))
    f.append(rect(490, 84, 120, 50, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(550, 106, "MOSFET", size=12.5, bold=True, color=FIELD))
    f.append(text(550, 124, "(керує затвор)", size=10, color=FIELD))
    f.append(rect(700, 84, 120, 50, fill="#fbecec", stroke=POS, sw=2, rx=6))
    f.append(text(760, 106, "PNP", size=12.5, bold=True, color=POS))
    f.append(text(760, 124, "(корисний)", size=10, color=POS))
    f.append(rect(700, 170, 120, 50, fill="#e9eefb", stroke=NEG, sw=2, rx=6))
    f.append(text(760, 192, "NPN", size=12.5, bold=True, color=NEG))
    f.append(text(760, 210, "паразит!", size=10, bold=True, color=NEG))
    f.append(tri(610, 109, 700, 109, FIELD, sw=2))
    f.append(text(655, 101, "вмикає", size=10, color=FIELD))
    # взаємний підкач між PNP і NPN
    f.append(tri(752, 134, 752, 170, POS, sw=2.4))
    f.append(tri(768, 170, 768, 136, NEG, sw=2.4))
    f.append(text(828, 150, "взаємний", size=10, color=INK, anchor="start"))
    f.append(text(828, 165, "підкач —", size=10, color=INK, anchor="start"))
    f.append(text(828, 182, "защіпка", size=11, bold=True, color=INK, anchor="start"))
    # пояснювальна рамка
    f.append(rect(490, 240, 360, 96, fill="#fbf3df", stroke="#caa24a", sw=2, rx=8))
    f.append(text(670, 263, "За великого струму NPN «прокидається»:", size=11.5, bold=True, color=INK))
    f.append(text(670, 283, "PNP і NPN живлять один одного, защіпка", size=11, color=INK))
    f.append(text(670, 301, "замикається — затвор уже нічим не керує.", size=11, color=INK))
    f.append(text(670, 319, "Рецепт (Накаґава, 1984): не дати NPN увімкнутись.", size=11, color=INK))
    return render(os.path.join(IMG, "latchup.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hybrid()
    fig_mosfet_vs_igbt()
    fig_igbt_timeline()
    fig_latchup()
    print("OK: hybrid, mosfet-vs-igbt, igbt-timeline, latchup")
