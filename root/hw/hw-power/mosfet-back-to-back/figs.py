# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def nmos(cx, cy, s_at="bottom", label="Q", flip_diode=False):
    """Малий значок N-MOSFET: три виводи (D зверху, S знизу, G зліва) + body-діод.
    Повертає (svg, ports) де ports = {'d':(x,y),'s':(x,y),'g':(x,y)}.
    s_at лишено для сумісності; орієнтація фіксована (D угорі, S унизу)."""
    body_x = cx
    d = (body_x, cy - 34)          # стік угорі
    s = (body_x, cy + 34)          # витік унизу
    g = (body_x - 40, cy)          # затвор зліва
    out = []
    # канал (вертикальна риска) і затворна пластина
    out.append(line(body_x + 6, cy - 26, body_x + 6, cy + 26, color=INK, sw=2.4))
    out.append(line(body_x - 14, cy, body_x - 2, cy, color=INK, sw=2))     # затвор до пластини
    out.append(line(body_x - 2, cy - 16, body_x - 2, cy + 16, color=INK, sw=2))  # пластина затвора
    # виводи D і S до каналу
    out.append(line(body_x + 6, cy - 26, d[0], d[1], color=INK, sw=2))
    out.append(line(body_x + 6, cy + 26, s[0], s[1], color=INK, sw=2))
    out.append(line(body_x + 6, cy, body_x + 6 + 0, cy, color=INK, sw=2))
    # затвор до точки g
    out.append(line(g[0], g[1], body_x - 14, cy, color=INK, sw=2))
    # body-діод збоку (трикутник + риска). N-MOS: анод=витік(низ), катод=стік(верх)
    dx = body_x + 26
    if not flip_diode:
        # струм пускає S(низ) -> D(верх): анод унизу
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="none" stroke="%s" stroke-width="2"/>'
                   % (dx - 7, cy + 8, dx + 7, cy + 8, dx, cy - 6, INK))
        out.append(line(dx - 8, cy - 6, dx + 8, cy - 6, color=INK, sw=2.4))  # катод (верх)
    else:
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="none" stroke="%s" stroke-width="2"/>'
                   % (dx - 7, cy - 8, dx + 7, cy - 8, dx, cy + 6, INK))
        out.append(line(dx - 8, cy + 6, dx + 8, cy + 6, color=INK, sw=2.4))
    out.append(line(dx, cy - 34, dx, cy + 34, color=MUTED, sw=1))            # шина діода
    out.append(line(body_x + 6, cy - 26, dx, cy - 26, color=MUTED, sw=1))
    out.append(line(body_x + 6, cy + 26, dx, cy + 26, color=MUTED, sw=1))
    out.append(text(g[0] - 6, cy - 8, "G", size=12, color=MUTED, anchor="end"))
    out.append(text(d[0] + 14, d[1] + 4, "D", size=12, color=MUTED, anchor="start"))
    out.append(text(s[0] + 14, s[1] + 4, "S", size=12, color=MUTED, anchor="start"))
    out.append(text(body_x - 4, cy + 60, label, size=15, color=INK, bold=True))
    return "".join(out), {"d": d, "s": s, "g": g}


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 1 — один ключ тече назад крізь діод; пара спина-до-спини замикає обидва боки
# ─────────────────────────────────────────────────────────────────────────────
def fig_problem():
    W, H = 760, 420
    parts = []
    parts.append(text(W / 2, 26, "Один ключ — вентиль лише в один бік; пара — в обидва", size=17, bold=True))

    # --- ліва панель: один MOSFET ---
    lx = 190
    parts.append(fitbox(40, 50, 300, 30, "ОДИН MOSFET: канал закрито, а діод тече",
                        size=13, bold=True, fill="#fdecea", stroke=POS))
    q1, p1 = nmos(lx, 200, label="Q")
    parts.append(q1)
    # вивід D до «навантаження» (право), S до «джерела» (ліво) — умовно горизонтально через виводи
    parts.append(line(p1["s"][0], p1["s"][1], p1["s"][0], 320, color=INK, sw=2))
    parts.append(line(p1["d"][0], p1["d"][1], p1["d"][0], 110, color=INK, sw=2))
    parts.append(text(lx, 105, "вихід (навантаження)", size=12, color=MUTED))
    parts.append(text(lx, 338, "вхід (джерело)", size=12, color=MUTED))
    # зворотний струм крізь діод
    parts.append('<path d="M %d 150 L %d 250" stroke="%s" stroke-width="3" fill="none" marker-end="url(#arrow)"/>'
                 % (lx + 70, lx + 70, POS))
    parts.append(text(lx + 100, 205, "струм", size=12, color=POS, bold=True))
    parts.append(text(lx + 100, 222, "назад", size=12, color=POS, bold=True))
    parts.append(fitbox(50, 358, 300, 46,
                        "Вихід піднявся вище входу → body-діод відкрився.\n«Вимкнено», а струм усе одно тече.",
                        size=11, fill="#fdecea", stroke=POS))

    # --- права панель: два спина-до-спини ---
    parts.append(line(W / 2 + 5, 45, W / 2 + 5, H - 10, color=MUTED, sw=1, dash="4 4"))
    rx1, rx2 = 500, 620
    parts.append(fitbox(420, 50, 300, 30, "ДВА спина-до-спини: назустріч — глухо",
                        size=13, bold=True, fill="#eafaf1", stroke=FIELD))
    a1, pa = nmos(rx1, 200, label="Q1")
    a2, pb = nmos(rx2, 200, label="Q2")
    parts.append(a1)
    parts.append(a2)
    # спільний вузол унизу (common-source): S1—S2 (обидва аноди діодів тут)
    parts.append(line(pa["s"][0], pa["s"][1], pa["s"][0], 300, color=INK, sw=2))
    parts.append(line(pb["s"][0], pb["s"][1], pb["s"][0], 300, color=INK, sw=2))
    parts.append(line(pa["s"][0], 300, pb["s"][0], 300, color=INK, sw=2))
    parts.append(circle((pa["s"][0] + pb["s"][0]) / 2, 300, 3, fill=INK, stroke=INK))
    parts.append(text((rx1 + rx2) / 2, 318, "спільний витік", size=11, color=MUTED))
    # виводи назовні: D1 ← вхід, D2 → вихід
    parts.append(line(pa["d"][0], pa["d"][1], pa["d"][0], 110, color=INK, sw=2))
    parts.append(line(pb["d"][0], pb["d"][1], pb["d"][0], 110, color=INK, sw=2))
    parts.append(text(rx1, 105, "бік A", size=12, color=MUTED))
    parts.append(text(rx2, 105, "бік B", size=12, color=MUTED))
    parts.append(fitbox(410, 358, 320, 46,
                        "Аноди обох діодів у спільному вузлі, катоди — назовні.\nЗворотний струм у будь-який бік упреться в закритий діод.",
                        size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "one-vs-pair.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 2 — спільний витік vs спільний стік: де стоїть спільний вузол і що з драйвером
# ─────────────────────────────────────────────────────────────────────────────
def fig_topologies():
    W, H = 760, 440
    parts = []
    parts.append(text(W / 2, 26, "Дві збірки: спільний витік і спільний стік", size=17, bold=True))

    # ── ліворуч: COMMON-SOURCE ──
    lx1, lx2 = 150, 270
    parts.append(fitbox(40, 48, 300, 28, "СПІЛЬНИЙ ВИТІК (common-source)",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    a1, pa = nmos(lx1, 190, label="Q1")
    a2, pb = nmos(lx2, 190, label="Q2")
    parts.append(a1)
    parts.append(a2)
    # спільний витік знизу
    parts.append(line(pa["s"][0], pa["s"][1], pa["s"][0], 290, color=INK, sw=2))
    parts.append(line(pb["s"][0], pb["s"][1], pb["s"][0], 290, color=INK, sw=2))
    parts.append(line(pa["s"][0], 290, pb["s"][0], 290, color=INK, sw=2))
    node = ((pa["s"][0] + pb["s"][0]) / 2, 290)
    parts.append(circle(node[0], node[1], 3.5, fill=NEG, stroke=NEG))
    # затвори зведені разом і на драйвер від спільного вузла
    parts.append(line(pa["g"][0], pa["g"][1], 70, pa["g"][1], color=INK, sw=2))
    parts.append(line(pb["g"][0], pb["g"][1], pb["g"][0], 130, color=INK, sw=2))
    parts.append(line(70, pa["g"][1], 70, 130, color=INK, sw=2))
    parts.append(line(70, 130, pb["g"][0], 130, color=INK, sw=2))
    parts.append(line(70, pa["g"][1], 70, 350, color=INK, sw=2))          # до драйвера
    parts.append(line(node[0], node[1], node[0], 350, color=NEG, sw=2))   # опорна лінія драйвера
    parts.append(line(70, 350, node[0], 350, color=INK, sw=2))
    parts.append(fitbox(95, 336, 90, 28, "1 драйвер", size=11, bold=True, fill="#eaf0fd", stroke=NEG))
    parts.append(text(node[0], 308, "спільний VS = опора драйвера", size=10.5, color=NEG))
    parts.append(fitbox(45, 375, 290, 44,
                        "Обидва затвори й спільний витік — один вузол відліку. Одного драйвера досить.",
                        size=11, fill="#eaf0fd", stroke=NEG))

    # ── роздільник ──
    parts.append(line(W / 2, 44, W / 2, H - 8, color=MUTED, sw=1, dash="4 4"))

    # ── праворуч: COMMON-DRAIN ──
    rx1, rx2 = 500, 620
    parts.append(fitbox(420, 48, 300, 28, "СПІЛЬНИЙ СТІК (common-drain)",
                        size=13, bold=True, fill="#eafaf1", stroke=FIELD))
    # тут малюємо дзеркально: витоки НАЗОВНІ (до клем), стоки — досередини
    # використаємо той самий значок, але вивід D всередину, S назовні
    b1, qb = nmos(rx1, 190, label="Q1")
    b2, qc = nmos(rx2, 190, label="Q2")
    parts.append(b1)
    parts.append(b2)
    # спільний стік ЗВЕРХУ (D1—D2)
    parts.append(line(qb["d"][0], qb["d"][1], qb["d"][0], 120, color=INK, sw=2))
    parts.append(line(qc["d"][0], qc["d"][1], qc["d"][0], 120, color=INK, sw=2))
    parts.append(line(qb["d"][0], 120, qc["d"][0], 120, color=INK, sw=2))
    parts.append(circle((qb["d"][0] + qc["d"][0]) / 2, 120, 3.5, fill=FIELD, stroke=FIELD))
    parts.append(text((rx1 + rx2) / 2, 112, "спільний стік", size=11, color=FIELD))
    # витоки назовні до клем
    parts.append(line(qb["s"][0], qb["s"][1], qb["s"][0], 300, color=INK, sw=2))
    parts.append(line(qc["s"][0], qc["s"][1], qc["s"][0], 300, color=INK, sw=2))
    parts.append(text(rx1, 318, "клема A", size=11, color=MUTED))
    parts.append(text(rx2, 318, "клема B", size=11, color=MUTED))
    # два різні опорні потенціали
    parts.append(text((rx1 + rx2) / 2, 348, "два витоки = дві опори", size=11, color=FIELD, bold=True))
    parts.append(fitbox(425, 375, 290, 44,
                        "Витоки «плавають» по-різному. Затвори треба піднімати над обома — драйвер складніший.",
                        size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, "common-source-drain.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 3 — чотири стани пари: провід уперед/назад (обидва канали) і блок у двох напрямках
# ─────────────────────────────────────────────────────────────────────────────
def fig_states():
    W, H = 720, 300
    parts = []
    parts.append(text(W / 2, 26, "Що робить пара в чотирьох ситуаціях", size=17, bold=True))

    rows = [
        ("Увімкнено, струм уперед", "обидва канали відкриті — падіння на 2·Rds(on), діоди ні до чого", FIELD, "#eafaf1"),
        ("Увімкнено, струм назад", "обидва канали відкриті — струм так само йде каналами, теж 2·Rds(on)", FIELD, "#eafaf1"),
        ("Вимкнено, тиснемо з боку A", "діод Q1 хоче пустити, але канал і діод Q2 стоять поперек — глухо", POS, "#fdecea"),
        ("Вимкнено, тиснемо з боку B", "тепер поперек стоїть Q1 — знову глухо; блокує в обидва боки", POS, "#fdecea"),
    ]
    y = 58
    for title, sub, col, fill in rows:
        parts.append(rect(40, y, 640, 50, fill=fill, stroke=col, sw=1.5, rx=8))
        parts.append(text(60, y + 22, title, size=13, color=INK, bold=True, anchor="start"))
        parts.append(text(60, y + 40, sub, size=11.5, color=MUTED, anchor="start"))
        y += 58

    render(os.path.join(IMG, "four-states.svg"), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 4 (для вставки hist) — «вартовий» комірки: чип-монітор + пара спина-до-
# спини (спільний витік) на одному дроті; два роздільні затвори «заряд»/«розряд»
# ─────────────────────────────────────────────────────────────────────────────
def fig_guardian():
    W, H = 760, 430
    parts = []
    parts.append(text(W / 2, 26, "Вартовий однієї комірки: монітор + пара на одному дроті", size=16.5, bold=True))

    # --- комірка (ліворуч) ---
    cell_x = 70
    parts.append(rect(cell_x - 26, 150, 52, 130, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    parts.append(text(cell_x, 200, "Li", size=20, color=NEG, bold=True))
    parts.append(text(cell_x, 224, "3.6 В", size=12, color=MUTED))
    parts.append(plus(cell_x, 138))
    parts.append(minus(cell_x, 292))
    # «+» комірки йде вгору до клеми PACK+
    parts.append(line(cell_x, 128, cell_x, 96, color=INK, sw=2))
    parts.append(line(cell_x, 96, 690, 96, color=INK, sw=2))
    parts.append(text(700, 100, "P+", size=13, color=INK, bold=True, anchor="start"))
    # «−» комірки йде вниз, крізь пару, до клеми PACK−
    parts.append(line(cell_x, 302, cell_x, 360, color=INK, sw=2))
    parts.append(line(cell_x, 360, 300, 360, color=INK, sw=2))

    # --- пара спина-до-спини у мінусовій лінії (спільний витік) ---
    rx1, rx2 = 380, 500
    a1, pa = nmos(rx1, 330, label="")
    a2, pb = nmos(rx2, 330, label="")
    parts.append(a1)
    parts.append(a2)
    # мінус-лінія входить у D1 (низ ← клема) — тут D унизу за значком, тож підводимо до s? Значок: D угорі, S унизу.
    # Робимо лінію: від комірки(−) до S1(низ Q1) НЕ можна (S — спільний). Тому:
    #   клема-бік і комірка-бік = СТОКИ (назовні), спільний вузол = ВИТОКИ (всередині).
    # Ліва клема-лінія (від комірки−) заходить у D1 (верх Q1) через провід збоку.
    parts.append(line(300, 360, 300, pa["d"][1] - 6, color=INK, sw=2))
    parts.append(line(300, pa["d"][1] - 6, pa["d"][0], pa["d"][1] - 6, color=INK, sw=2))
    parts.append(line(pa["d"][0], pa["d"][1] - 6, pa["d"][0], pa["d"][1], color=INK, sw=2))
    # спільний витік S1—S2 (аноди body-діодів тут)
    parts.append(line(pa["s"][0], pa["s"][1], pa["s"][0], 392, color=INK, sw=2))
    parts.append(line(pb["s"][0], pb["s"][1], pb["s"][0], 392, color=INK, sw=2))
    parts.append(line(pa["s"][0], 392, pb["s"][0], 392, color=INK, sw=2))
    parts.append(circle((pa["s"][0] + pb["s"][0]) / 2, 392, 3.5, fill=INK, stroke=INK))
    parts.append(text((rx1 + rx2) / 2, 410, "спільний витік", size=10.5, color=MUTED))
    # D2 → назовні до клеми PACK−
    parts.append(line(pb["d"][0], pb["d"][1] - 6, pb["d"][0], pb["d"][1], color=INK, sw=2))
    parts.append(line(pb["d"][0], pb["d"][1] - 6, 620, pb["d"][1] - 6, color=INK, sw=2))
    parts.append(line(620, pb["d"][1] - 6, 620, 360, color=INK, sw=2))
    parts.append(line(620, 360, 690, 360, color=INK, sw=2))
    parts.append(text(700, 364, "P−", size=13, color=INK, bold=True, anchor="start"))
    # підписи ролей
    parts.append(text(rx1, 284, "«заряд»", size=11.5, color=FIELD, bold=True))
    parts.append(text(rx2, 284, "«розряд»", size=11.5, color=POS, bold=True))

    # --- чип-монітор (вгорі праворуч) ---
    parts.append(rect(360, 118, 200, 84, fill="#fbfbe8", stroke=INK, sw=1.8, rx=8))
    parts.append(text(460, 144, "монітор комірки", size=13, color=INK, bold=True))
    parts.append(text(460, 165, "стежить за U та I,", size=11, color=MUTED))
    parts.append(text(460, 183, "рубає заряд і розряд", size=11, color=MUTED))
    # виводи чипа до затворів (OC → «заряд», OD → «розряд»)
    parts.append(line(400, 208, 400, 250, color=FIELD, sw=2))
    parts.append(line(400, 250, pa["g"][0] - 8, 250, color=FIELD, sw=2))
    parts.append(line(pa["g"][0] - 8, 250, pa["g"][0] - 8, pa["g"][1], color=FIELD, sw=2))
    parts.append(line(pa["g"][0] - 8, pa["g"][1], pa["g"][0], pa["g"][1], color=FIELD, sw=2))
    parts.append(text(388, 240, "OC", size=10, color=FIELD, bold=True, anchor="end"))
    parts.append(line(520, 208, 520, 244, color=POS, sw=2))
    parts.append(line(520, 244, pb["g"][0] - 8, 244, color=POS, sw=2))
    parts.append(line(pb["g"][0] - 8, 244, pb["g"][0] - 8, pb["g"][1], color=POS, sw=2))
    parts.append(line(pb["g"][0] - 8, pb["g"][1], pb["g"][0], pb["g"][1], color=POS, sw=2))
    parts.append(text(532, 240, "OD", size=10, color=POS, bold=True, anchor="start"))
    # опора монітора — від «−» комірки (VSS) до спільної лінії
    parts.append(line(360, 190, 300, 190, color=MUTED, sw=1.2, dash="3 3"))
    parts.append(line(300, 190, 300, 360, color=MUTED, sw=1.2, dash="3 3"))
    parts.append(text(300, 178, "VDD/VSS з комірки", size=9.5, color=MUTED))

    parts.append(fitbox(40, 300, 210, 46,
                        "Одна комірка —\nодин вартовий:\nчип + пара FET",
                        size=12, fill="#f4f4f4", stroke=MUTED))

    render(os.path.join(IMG, "cell-guardian.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_problem()
    fig_topologies()
    fig_states()
    fig_guardian()
    print("ok: one-vs-pair.svg, common-source-drain.svg, four-states.svg, cell-guardian.svg")
