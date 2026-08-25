# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

RED = "#c0392b"


def laser_diode(cx, cy, r=17):
    """Символ лазерного діода: діод у колі + дві стрілочки випромінювання назовні."""
    s = circle(cx, cy, r, fill="#fff", stroke=INK, sw=1.6)
    # трикутник діода вістрям униз (анод зверху -> катод знизу)
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" sw="1"/>'
           % (cx - 8, cy - 6, cx + 8, cy - 6, cx, cy + 6, INK, INK))
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
           % (cx - 8, cy - 6, cx + 8, cy - 6, cx, cy + 6, INK))
    bar = line(cx - 8, cy + 6, cx + 8, cy + 6, color=INK, sw=2)
    # дві стрілки випромінювання вправо-вгору
    e1 = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
          % (cx + r - 3, cy - 3, cx + r + 12, cy - 13, RED))
    e2 = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
          % (cx + r + 1, cy + 1, cx + r + 16, cy - 8, RED))
    return s + tri + bar + e1 + e2


# ── Фігура 1: внутрішня схема KY-008 (два варіанти плати) ────────────────────
def fig_schematic():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 30, "Всередині KY-008: лазерний діод + гасильний резистор і три піни", size=16, bold=True))

    # ── лівий варіант: середній = живлення (+), S керує ──
    lx = 40
    frags.append(text(lx + 175, 62, "Варіант А (частіший): середній пін — живлення +", size=13, bold=True))
    frags.append(rect(lx, 76, 350, 250, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    # три піни зліва, з добрим інтервалом
    pins = [("S", 130, RED), ("+", 200, INK), ("−", 270, NEG)]
    for name, py, col in pins:
        frags.append(circle(lx + 24, py, 9, fill="#fff", stroke=col, sw=2))
        frags.append(text(lx + 24, py + 5, name, size=13, bold=True, color=col))
    # + пін -> резистор -> анод діода (верхня гілка)
    frags.append(line(lx + 33, 200, lx + 120, 200))
    frags.append(line(lx + 120, 200, lx + 120, 150))
    frags.append(rect(lx + 100, 128, 40, 22, fill="#fff", stroke=INK, sw=1.4, rx=3))
    frags.append(text(lx + 120, 143, "R", size=12, bold=True))
    frags.append(line(lx + 120, 128, lx + 120, 122))
    # діод трохи правіше й вище
    frags.append(laser_diode(lx + 175, 122))
    frags.append(line(lx + 120, 105, lx + 175, 105))
    frags.append(line(lx + 120, 122, lx + 120, 105))
    frags.append(line(lx + 175, 105, lx + 175, 106))  # анод (короткий стик у діод)
    # катод діода -> вниз -> до піна S (S притягує до 0 → струм тече)
    frags.append(line(lx + 175, 139, lx + 175, 200))
    frags.append(line(lx + 33, 130, lx + 90, 130))
    frags.append(line(lx + 90, 130, lx + 90, 230))
    frags.append(line(lx + 90, 230, lx + 175, 230))
    frags.append(line(lx + 175, 230, lx + 175, 200))
    frags.append(text(lx + 195, 205, "S тягне 0 → світить", size=10, color=MUTED, anchor="start"))
    # земля − пін
    frags.append(line(lx + 33, 270, lx + 300, 270))
    frags.append(text(lx + 305, 274, "GND", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 175, 306,
                      "+ → 5 В,  − → GND,  S ← вивід МК", size=12, color=INK))

    # ── правий варіант: середній NC, діод живиться від S ──
    rx = 440
    frags.append(text(rx + 150, 62, "Варіант Б: середній не з'єднаний (NC)", size=13, bold=True))
    frags.append(rect(rx, 76, 300, 250, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    pins2 = [("S", 130, RED), ("NC", 200, MUTED), ("−", 270, NEG)]
    for name, py, col in pins2:
        frags.append(circle(rx + 24, py, 9, fill="#fff", stroke=col, sw=2))
        frags.append(text(rx + 24, py + 5, name, size=11, bold=True, color=col))
    # S -> резистор -> анод діода -> катод -> земля
    frags.append(line(rx + 33, 130, rx + 100, 130))
    frags.append(rect(rx + 100, 119, 40, 22, fill="#fff", stroke=INK, sw=1.4, rx=3))
    frags.append(text(rx + 120, 134, "R", size=12, bold=True))
    frags.append(line(rx + 140, 130, rx + 168, 130))
    frags.append(laser_diode(rx + 188, 130))
    frags.append(line(rx + 188, 113, rx + 188, 130))  # анод
    frags.append(line(rx + 188, 147, rx + 188, 270))  # катод -> земля
    frags.append(line(rx + 33, 270, rx + 188, 270))
    frags.append(text(rx + 150, 306,
                      "струм діода тече з піна S, не з живлення", size=12, color=INK))

    render(os.path.join(OUT, "schematic.svg"), W, H, *frags)


# ── Фігура 2: розводка пін-у-пін до мікроконтролера ──────────────────────────
def fig_wiring():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 30, "Підключення KY-008 до плати (універсальне: живи середній пін)", size=16, bold=True))

    # модуль зліва
    frags.append(rect(60, 90, 150, 180, fill="#eef2ff", stroke=NEG, sw=1.6))
    frags.append(text(135, 116, "KY-008", size=14, bold=True))
    frags.append(laser_diode(135, 160, r=14))
    mpins = [("S", 210, RED), ("+", 235, INK), ("−", 260, NEG)]
    for name, py, col in mpins:
        frags.append(circle(200, py, 8, fill="#fff", stroke=col, sw=2))
        frags.append(text(178, py + 5, name, size=12, bold=True, color=col, anchor="middle"))

    # плата справа
    frags.append(rect(510, 90, 150, 200, fill="#f4f6f8", stroke=INK, sw=1.6))
    frags.append(text(585, 116, "Плата (МК)", size=13, bold=True))
    bpins = [("D-пін", 210, RED), ("5V", 235, INK), ("GND", 260, NEG)]
    for name, py, col in bpins:
        frags.append(circle(510, py, 8, fill="#fff", stroke=col, sw=2))
        frags.append(text(560, py + 5, name, size=12, bold=True, color=col, anchor="middle"))

    # дроти
    frags.append(line(208, 210, 502, 210, color=RED, sw=2.2))
    frags.append(line(208, 235, 502, 235, color=INK, sw=2.2))
    frags.append(line(208, 260, 502, 260, color=NEG, sw=2.2))
    frags.append(text(355, 202, "цифровий вивід → S", size=11, color=RED))
    frags.append(text(355, 227, "5 В → +", size=11, color=INK))
    frags.append(text(355, 252, "GND → −", size=11, color=NEG))

    frags.append(text(W / 2, 320,
                      "digitalWrite(pin, HIGH) → промінь; LOW → темно. Резистор уже на платі.",
                      size=12, color=MUTED))
    render(os.path.join(OUT, "wiring.svg"), W, H, *frags)


# ── Фігура 3: чому резистор обов'язковий — крута крива діода ─────────────────
def fig_curve():
    W, H = 640, 400
    frags = []
    frags.append(text(W / 2, 30, "Чому лазерний діод не можна вмикати «прямо в напругу»", size=15, bold=True))

    # осі
    ox, oy = 110, 330
    frags.append(line(ox, oy, ox, 70, color=INK, sw=1.6))     # вісь струму
    frags.append(line(ox, oy, 560, oy, color=INK, sw=1.6))    # вісь напруги
    frags.append(text(ox - 60, 200, "струм", size=12, color=INK, anchor="middle"))
    frags.append(text(ox - 60, 216, "крізь", size=12, color=INK, anchor="middle"))
    frags.append(text(ox - 60, 232, "діод", size=12, color=INK, anchor="middle"))
    frags.append(text(340, oy + 34, "напруга на діоді", size=12, color=INK))

    # поріг ~2 В (позначка на осі)
    thx = 300
    frags.append(line(thx, oy, thx, oy + 6, color=INK))
    frags.append(text(thx, oy + 22, "≈2 В (поріг)", size=11, color=MUTED))

    # крива: майже нуль до порогу, тоді майже вертикаль
    path = ('<path d="M%d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" '
            'fill="none" stroke="%s" stroke-width="2.6"/>'
            % (ox, oy - 2,
               ox + 120, oy - 4, thx - 30, oy - 6, thx, oy - 14,
               thx + 24, oy - 90, thx + 40, 120, thx + 52, 90,
               RED))
    frags.append(path)

    # безпечна точка на кривій + пунктир
    frags.append(circle(thx + 40, 120, 5, fill=RED, stroke=RED))
    frags.append(line(ox, 120, thx + 40, 120, color=MUTED, sw=1, dash="4 4"))
    frags.append(text(ox - 6, 116, "робочий", size=10, color=MUTED, anchor="end"))
    frags.append(text(ox - 6, 130, "струм", size=10, color=MUTED, anchor="end"))

    # стрілка «крихітний приріст напруги → лавина струму»
    frags.append(text(thx + 150, 150, "крихітний +ΔU", size=11, color=INK, anchor="start"))
    frags.append(text(thx + 150, 166, "→ струм злітає", size=11, color=INK, anchor="start"))
    frags.append(text(thx + 150, 182, "до руйнівного", size=11, color=RED, anchor="start"))

    # висновок рамкою
    box, w, h = textbox(W / 2, 372,
                        "Резистор задає струм у робочій точці — без нього діод спалює сам себе",
                        size=12, pad=8)
    frags.append(box)
    render(os.path.join(OUT, "curve.svg"), W, H, *frags)


# ── Фігура 4: лазерний бар'єр — випромінювач, промінь, приймач, перетин ───────
def fig_barrier():
    W, H = 780, 420
    frags = []
    frags.append(text(W / 2, 30, "Лазерний бар'єр: KY-008 світить на фоторезистор, код ловить перетин", size=15, bold=True))

    beam_y = 200

    # ── випромінювач KY-008 (ліворуч) ──
    frags.append(rect(40, 140, 130, 120, fill="#eef2ff", stroke=NEG, sw=1.6))
    frags.append(text(105, 166, "KY-008", size=13, bold=True))
    frags.append(text(105, 184, "лазер", size=11, color=MUTED))
    frags.append(laser_diode(105, beam_y, r=13))

    # ── приймач KY-018 (праворуч) ──
    frags.append(rect(610, 140, 130, 120, fill="#eefbf1", stroke=FIELD, sw=1.6))
    frags.append(text(675, 166, "KY-018", size=13, bold=True))
    frags.append(text(675, 184, "фоторезистор", size=10, color=MUTED))
    frags.append(circle(675, beam_y, 14, fill="#fff", stroke=FIELD, sw=2))

    # ── промінь між ними (підпис ВИЩЕ, з великим відступом від лінії) ──
    frags.append(text(390, 118, "промінь 650 нм", size=11, color=RED))
    frags.append(line(150, beam_y, 608, beam_y, color=RED, sw=3))

    # ── предмет, що перетинає промінь (пунктирна рамка, посередині) ──
    ox = 385
    frags.append(rect(ox - 20, 152, 40, 96, fill="#ffffff", stroke=INK, sw=1.6, rx=4))
    # штрихування предмета — короткі риски В МЕЖАХ рамки, не торкаються написів
    for dx in (-12, -4, 4, 12):
        frags.append(line(ox + dx, 158, ox + dx, 242, color=MUTED, sw=1, dash="3 3"))
    frags.append(text(ox, 284, "предмет перетинає", size=11, color=INK))

    # ── що бачить АЦП: два стани, окремим рядком нижче, поза лініями ──
    frags.append(text(W / 2, 320, "цілий → АЦП дає високе число        перекрито → різкий провал",
                      size=12, color=INK))

    # висновок рамкою
    box, w, h = textbox(W / 2, 384,
                        "Лазер — лише джерело; «перетин» бачить код за провалом освітленості давача",
                        size=12, pad=8)
    frags.append(box)
    render(os.path.join(OUT, "barrier.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_schematic()
    fig_wiring()
    fig_curve()
    fig_barrier()
    print("ok: schematic.svg, wiring.svg, curve.svg, barrier.svg")
