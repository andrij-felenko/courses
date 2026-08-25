# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GAS = "#e67e22"   # газ / здуття


# ── Фігура 1: два боки роздуття — оборотне «дихання» vs незворотний газ ──────
def fig_two_channels():
    W, H = 720, 360
    els = []
    els.append(text(W/2, 28, "Два боки роздуття пакета", size=17, bold=True))

    # ліва панель — оборотне дихання
    els.append(fitbox(30, 55, 315, 40, "ОБОРОТНЕ: дихання електродів",
                      size=14, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    # плаский vs набряклий (заряд)
    els.append(rect(70, 130, 90, 120, fill="#f4f6f8", stroke=LINE, sw=1.5))
    els.append(text(115, 265, "розряджений", size=12, color=MUTED))
    els.append(rect(215, 118, 90, 144, fill="#eaf0fd", stroke=NEG, sw=2))
    els.append(text(260, 277, "заряджений", size=12, color=NEG))
    els.append(arrow(168, 190, 207, 190, color=NEG))
    els.append(text(188, 178, "+10%", size=13, color=NEG, bold=True))
    els.append(text(188, 305, "графіт вбирає Li → товщає;", size=12, color=INK))
    els.append(text(188, 323, "розряд повертає назад", size=12, color=INK))

    # права панель — незворотний газ
    els.append(fitbox(375, 55, 315, 40, "НЕЗВОРОТНЕ: газ у пакеті",
                      size=14, bold=True, fill="#fdf0e6", stroke=GAS, color=GAS))
    els.append(rect(430, 130, 90, 120, fill="#f4f6f8", stroke=LINE, sw=1.5))
    els.append(text(475, 265, "свіжий пакет", size=12, color=MUTED))
    # набряклий газом — з бульбашками
    els.append(rect(575, 112, 96, 150, fill="#fdf0e6", stroke=GAS, sw=2, rx=14))
    for (bx, by, br) in [(600, 150, 7), (640, 175, 6), (615, 205, 8), (648, 225, 5), (590, 230, 6)]:
        els.append(circle(bx, by, br, fill="#ffffff", stroke=GAS, sw=1.5))
    els.append(text(623, 277, "здутий газом", size=12, color=GAS))
    els.append(arrow(526, 190, 567, 190, color=GAS))
    els.append(text(628, 305, "хімія виділяє газ;", size=12, color=INK))
    els.append(text(628, 323, "назад НЕ вертається", size=12, color=INK, bold=True))

    els.append(line(360, 110, 360, 335, color=MUTED, sw=1, dash="4 4"))
    render(os.path.join(OUT, "two-channels.svg"), W, H, *els)


# ── Фігура 2: карта реакцій газовиділення ───────────────────────────────────
def fig_gas_map():
    W, H = 760, 470
    els = []
    els.append(text(W/2, 28, "Звідки береться газ: чотири джерела", size=17, bold=True))

    # центр — пакет
    cx, cy = W/2, 250
    els.append(circle(cx, cy, 52, fill="#fdf0e6", stroke=GAS, sw=2.5))
    els.append(mtext(cx, cy - 4, ["газ", "у пакеті"], size=14, bold=True, color=GAS))

    def src(bx, by, title, lines, col):
        out = fitbox(bx, by, 250, 30, title, size=13, bold=True,
                     fill="#ffffff", stroke=col, color=col)
        out += mtext(bx + 125, by + 52, lines, size=12, color=INK, lh=1.25)
        return out

    # верх-ліво: формування SEI
    els.append(src(45, 60,  "1. Формування SEI (перший заряд)",
                   ["EC відновлюється на аноді →", "C₂H₄ (етилен) + Li₂CO₃.",
                    "Одноразовий сплеск на заводі."], NEG))
    # верх-право: гідроліз солі
    els.append(src(465, 60, "2. Гідроліз солі LiPF₆",
                   ["слід води: PF₅ + H₂O →", "POF₃ + 2 HF; кислота гризе",
                    "плівку → знову газ."], POS))
    # низ-ліво: окиснення на катоді
    els.append(src(45, 330, "3. Окиснення на катоді",
                   ["надто висока напруга →", "розчинник згоряє на катоді",
                    "→ CO₂ + CO."], POS))
    # низ-право: осадження літію
    els.append(src(465, 330, "4. Осадження літію / мідь",
                   ["перезаряд/холод → Li-метал;",
                    "глибокий розряд → мідь тане.",
                    "І те, й те тягне газ."], "#8e44ad"))

    # стрілки до центру
    els.append(arrow(230, 130, cx - 40, cy - 30, color=NEG))
    els.append(arrow(530, 130, cx + 40, cy - 30, color=POS))
    els.append(arrow(230, 372, cx - 40, cy + 30, color=POS))
    els.append(arrow(530, 372, cx + 40, cy + 30, color="#8e44ad"))

    els.append(text(W/2, 452, "1 — на заводі, разово; 2–4 — за зловживання, накопичується",
                    size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "gas-map.svg"), W, H, *els)


# ── Фігура 3: чому LiPo здувається видимо — м'який пакет як підсилювач ───────
def fig_pouch_amplifier():
    W, H = 720, 330
    els = []
    els.append(text(W/2, 28, "Однаковий газ, різна доля: банка vs пакет", size=17, bold=True))

    # циліндр у банці
    els.append(text(180, 62, "жорстка банка (18650)", size=13, bold=True, color=NEG))
    els.append(rect(120, 85, 120, 150, fill="#eaf0fd", stroke=NEG, sw=2.5, rx=10))
    for (bx, by) in [(155, 120), (205, 140), (175, 180), (215, 200)]:
        els.append(circle(bx, by, 6, fill="#ffffff", stroke=GAS, sw=1.5))
    els.append(mtext(180, 258, ["газ → тиск усередині;", "форма та сама, аж до клапана"],
                     size=12, color=INK, lh=1.3))

    # пакет LiPo
    els.append(text(540, 62, "м'який пакет (LiPo)", size=13, bold=True, color=GAS))
    # роздута «подушка»
    els.append('<path d="M 470 210 Q 470 110 540 110 Q 610 110 610 210 '
               'Q 610 250 540 250 Q 470 250 470 210 Z" '
               'fill="#fdf0e6" stroke="%s" stroke-width="2.5"/>' % GAS)
    for (bx, by) in [(515, 150), (565, 165), (540, 195), (585, 200), (505, 195)]:
        els.append(circle(bx, by, 6, fill="#ffffff", stroke=GAS, sw=1.5))
    els.append(mtext(540, 275, ["той самий газ роздуває", "тонку оболонку — видно оком"],
                     size=12, color=INK, lh=1.3))

    els.append(line(360, 75, 360, 300, color=MUTED, sw=1, dash="4 4"))
    render(os.path.join(OUT, "pouch-amplifier.svg"), W, H, *els)


if __name__ == "__main__":
    fig_two_channels()
    fig_gas_map()
    fig_pouch_amplifier()
    print("figures written to", OUT)
