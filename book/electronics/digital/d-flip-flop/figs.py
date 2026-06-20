# -*- coding: utf-8 -*-
"""Фігури до теми «D-тригер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальна геометрія логічних вентилів (не текстові рамки) ─────────────────
def wire(x1, y1, x2, y2, color=INK, sw=1.8):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, color, sw))


def node(cx, cy, r=3.0):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s"/>'
            % (cx, cy, r, INK, INK))


def and_gate(x, y, w=34, h=40):
    """Вентиль AND: пласка спинка ліворуч + півколо праворуч. Повертає (svg, out_x, out_y)."""
    r = h / 2.0
    sx = x + w - r
    d = ('<path d="M %.1f,%.1f L %.1f,%.1f A %.1f,%.1f 0 0 1 %.1f,%.1f L %.1f,%.1f Z" '
         'fill="%s" stroke="%s" stroke-width="2"/>'
         % (x, y, sx, y, r, r, sx, y + h, x, y + h, FILL, INK))
    return d, x + w, y + r


def inverter(x, y, size=26):
    """Інвертор: трикутник вершиною праворуч + бульбашка. Повертає (svg, out_x, out_y)."""
    cy = y + size / 2.0
    tri = ('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s" stroke="%s" '
           'stroke-width="2"/>' % (x, y, x, y + size, x + size, cy, FILL, INK))
    bx = x + size + 6
    bub = ('<circle cx="%.1f" cy="%.1f" r="6" fill="#fff" stroke="%s" stroke-width="2"/>'
           % (bx, cy, INK))
    return tri + bub, bx + 6, cy


def clk_triangle(cx, cy):
    """Знак «по фронту»: маленький трикутник «❯» на тактовому вході."""
    return ('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
            'stroke-width="1.8"/>' % (cx - 6, cy - 7, cx + 6, cy, cx - 6, cy + 7, INK))


def caption(W, sub):
    """Підзаголовок-курсив під титулом (titulo дає render())."""
    return text(W / 2, 50, sub, size=12, color=MUTED, italic=True)


# ── Фіг.1: тактований (gated) латч ──────────────────────────────────────────
def fig_gated_latch():
    W, H = 860, 360
    f = [caption(W, "два AND пропускають S і R, лише коли такт=1; такт=0 → на засувку йдуть нулі → вона тримає")]

    # входи S / такт / R
    f.append(text(104, 154, "S", size=13, color=POS, anchor="end", bold=True))
    f.append(wire(110, 150, 180, 150))
    f.append(text(104, 254, "R", size=13, color=NEG, anchor="end", bold=True))
    f.append(wire(110, 250, 180, 250))
    f.append(text(104, 204, "такт", size=12, anchor="end", bold=True))
    f.append(wire(110, 200, 150, 200))
    f.append(node(150, 200))
    f.append(wire(150, 200, 150, 158)); f.append(wire(150, 158, 180, 158))
    f.append(wire(150, 200, 150, 242)); f.append(wire(150, 242, 180, 242))

    # два AND
    g1, ox1, oy1 = and_gate(180, 134); f.append(g1)
    f.append(text(199, 128, "S·такт", size=9.5, color=MUTED))
    g2, ox2, oy2 = and_gate(180, 230); f.append(g2)
    f.append(text(199, 286, "R·такт", size=9.5, color=MUTED))
    f.append(wire(ox1, oy1, 300, 162)); f.append(wire(ox2, oy2, 300, 238))

    # засувка
    f.append(rect(300, 160, 120, 80, fill="#eef7ee", stroke=INK, sw=2, rx=8))
    f.append(text(360, 204, "SR-засувка", size=13, bold=True))
    f.append(wire(420, 200, 480, 200))
    f.append(text(486, 204, "Q", size=14, color=FIELD, anchor="start", bold=True))

    # пояснювальна рамка
    box = fitbox(560, 118, 270, 168,
                 "такт=1: «відкрито» — Q стежить за S/R\n"
                 "такт=0: «зачинено» — Q тримає\n"
                 "запис тепер за тактом,\n"
                 "та все ще цілий час, поки такт=1",
                 size=12, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10)
    f.append(box)
    render(os.path.join(IMG, "gated-latch.svg"), W, H, *f,
           title="Тактований латч: дозволити запис лише за сигналом такту")


# ── Фіг.2: D-латч ────────────────────────────────────────────────────────────
def fig_d_latch():
    W, H = 860, 360
    f = [caption(W, "беремо S=D, R=D̄ (через інвертор): S і R завжди протилежні, тож S=R=1 неможливе")]

    f.append(text(104, 164, "D", size=13, anchor="end", bold=True))
    f.append(node(140, 160))
    f.append(wire(116, 160, 230, 160))
    f.append(text(180, 152, "S = D", size=10, color=MUTED))
    # гілка на інвертор → R
    f.append(wire(140, 160, 140, 230))
    inv, iox, ioy = inverter(140, 217, size=26); f.append(inv)
    f.append(wire(iox, ioy, 230, ioy))
    f.append(text(205, 222, "R = D̄", size=10, color=MUTED))

    f.append(text(104, 284, "такт", size=12, anchor="end", bold=True))
    f.append(wire(116, 280, 230, 280))

    f.append(rect(230, 150, 130, 150, fill="#eef7ee", stroke=INK, sw=2, rx=8))
    f.append(text(295, 224, "тактований", size=13, bold=True))
    f.append(text(295, 244, "латч", size=10, color=MUTED))
    f.append(wire(360, 200, 430, 200))
    f.append(text(436, 204, "Q", size=14, color=FIELD, anchor="start", bold=True))

    box = fitbox(540, 120, 290, 168,
                 "такт=1 → Q стежить за D (Q=D)\n"
                 "такт=0 → Q тримає (пам'ять)\n"
                 "заборонений стан неможливий\n"
                 "та поки такт=1 латч прозорий:\n"
                 "зміна D одразу йде на Q",
                 size=11.5, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10)
    f.append(box)
    render(os.path.join(IMG, "d-latch.svg"), W, H, *f,
           title="D-латч: один вхід даних D — і заборонений стан зникає")


# ── Фіг.3: майстер-слейв ─────────────────────────────────────────────────────
def fig_master_slave():
    W, H = 880, 380
    f = [caption(W, "латчі тактовані протилежно, тож прозорі по черзі — і пара пропускає D лише на мить переходу")]

    f.append(text(92, 179, "D", size=13, anchor="end", bold=True))
    f.append(wire(100, 175, 170, 175))
    f.append(rect(170, 140, 130, 80, fill="#eef4ff", stroke=INK, sw=2, rx=8))
    f.append(text(235, 184, "майстер", size=13, bold=True))
    f.append(text(235, 200, "латч", size=10, color=MUTED))
    f.append(wire(300, 175, 370, 175))
    f.append(text(335, 167, "внутр.", size=9.5, color=MUTED))
    f.append(rect(370, 140, 130, 80, fill="#eef7ee", stroke=INK, sw=2, rx=8))
    f.append(text(435, 184, "слейв", size=13, bold=True))
    f.append(text(435, 200, "латч", size=10, color=MUTED))
    f.append(wire(500, 175, 580, 175))
    f.append(text(586, 179, "Q", size=14, color=FIELD, anchor="start", bold=True))

    # такт: до майстра прямо (з трикутником), до слейва через інвертор
    f.append(text(92, 304, "такт", size=12, anchor="end", bold=True))
    f.append(wire(100, 300, 235, 300))
    f.append(node(235, 300))
    f.append(wire(235, 300, 235, 220)); f.append(clk_triangle(235, 213))
    f.append(wire(235, 300, 320, 300))
    inv, iox, ioy = inverter(320, 287, size=26); f.append(inv)
    f.append(wire(iox, ioy, 435, ioy)); f.append(wire(435, ioy, 435, 220))
    f.append(clk_triangle(435, 213))
    f.append(text(300, 320, "майстер — по такту", size=10, color=MUTED))
    f.append(text(470, 320, "слейв — по інверсії такту", size=10, color=MUTED))

    box = fitbox(620, 110, 230, 200,
                 "як виходить «фронт»:\n"
                 "такт=0: майстер дивиться\n"
                 "на D, слейв тримає вихід\n"
                 "фронт 0→1: майстер замикає\n"
                 "значення D, слейв веде його\n"
                 "на Q\n"
                 "між фронтами Q мовчить",
                 size=10.8, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10)
    f.append(box)
    render(os.path.join(IMG, "master-slave.svg"), W, H, *f,
           title="D-тригер: два латчі ловлять D рівно по фронту")


# ── Фіг.4: часова діаграма ───────────────────────────────────────────────────
def fig_waveform():
    W, H = 880, 400
    f = [caption(W, "між фронтами D смикається як завгодно — Q байдуже; він оновлюється тільки на наростанні такту")]

    x0, x1 = 130, 830
    edges = [220, 400, 580, 760]

    # такт
    f.append(text(95, 114, "такт", size=13, anchor="end", bold=True))
    f.append(line(x0, 126, x1, 126, color="#e4e4e4", sw=1))
    clk = "130,126 180,126 220,126 220,94 280,94 280,126 360,126 400,126 400,94 460,94 460,126 540,126 580,126 580,94 640,94 640,126 720,126 760,126 760,94 820,94 820,126 830,126"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (clk, INK))
    for ex in edges:
        f.append(line(ex, 90, ex, 330, color=MUTED, sw=1, dash="3 3"))
        f.append(text(ex, 86, "▲", size=10, color=POS, bold=True))

    # D
    f.append(text(95, 204, "D", size=13, color=NEG, anchor="end", bold=True))
    f.append(line(x0, 216, x1, 216, color="#e4e4e4", sw=1))
    dwave = "130,216 150,216 150,184 270,184 270,216 340,216 340,184 370,184 370,216 520,216 520,184 640,184 640,216 700,216 700,184 830,184"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (dwave, NEG))
    f.append(text(330, 178, "D смикнувся між фронтами — Q це проігнорує", size=10.5, color=MUTED, italic=True))

    # Q
    f.append(text(95, 294, "Q", size=13, color=FIELD, anchor="end", bold=True))
    f.append(line(x0, 306, x1, 306, color="#e4e4e4", sw=1))
    qwave = "130,306 220,306 220,274 400,274 400,306 580,306 580,274 760,274 830,274"
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (qwave, FIELD))

    f.append(text(W / 2, 372,
                  "на кожному ▲ (наростання такту) Q ← значення D у цю мить; далі тримає до наступного ▲",
                  size=12, bold=True))
    render(os.path.join(IMG, "waveform.svg"), W, H, *f,
           title="Поведінка D-тригера: Q бере D лише в мить фронту такту")


# ── Фіг.5: умовний символ ────────────────────────────────────────────────────
def fig_symbol():
    W, H = 820, 350
    f = [caption(W, "трикутник на тактовому вході = «спрацьовує по фронту»; один вхід D, виходи Q і Q̄")]

    # прямокутник символу
    f.append(rect(180, 110, 110, 130, fill=FILL, stroke=INK, sw=2, rx=6))
    f.append(text(196, 142, "D", size=14, anchor="start", bold=True))
    f.append(text(274, 142, "Q", size=14, color=FIELD, anchor="end", bold=True))
    f.append(text(274, 218, "Q̄", size=13, color=FIELD, anchor="end", bold=True))
    f.append(clk_triangle(186, 210))
    f.append(text(200, 214, "clk", size=11, anchor="start"))
    f.append(text(235, 100, "D-тригер", size=13, bold=True))
    f.append(text(235, 262, "Q ← D по фронту clk", size=11.5, color=MUTED, italic=True))

    # виводи
    f.append(wire(120, 142, 180, 142)); f.append(text(114, 146, "D", size=14, anchor="end", bold=True))
    f.append(wire(120, 210, 180, 210)); f.append(text(114, 214, "clk", size=13, anchor="end", bold=True))
    f.append(wire(290, 142, 350, 142)); f.append(text(356, 146, "Q", size=14, color=FIELD, anchor="start", bold=True))
    f.append(wire(290, 200, 350, 200)); f.append(text(356, 204, "Q̄", size=13, color=FIELD, anchor="start", bold=True))

    box = fitbox(470, 110, 320, 150,
                 "чому він усюди:\n"
                 "один вхід, без заборонених станів\n"
                 "запис лише в чітку мить (фронт) →\n"
                 "уся машина крокує синхронно\n"
                 "8 поряд = регістр; ланцюжок = лічильник",
                 size=11.5, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10)
    f.append(box)
    f.append(text(W / 2, 312,
                  "D-тригер — основний елемент пам'яті всієї синхронної цифрової техніки",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "symbol.svg"), W, H, *f,
           title="Умовний символ D-тригера")


if __name__ == "__main__":
    fig_gated_latch()
    fig_d_latch()
    fig_master_slave()
    fig_waveform()
    fig_symbol()
    print("OK: 5 figures ->", IMG)
