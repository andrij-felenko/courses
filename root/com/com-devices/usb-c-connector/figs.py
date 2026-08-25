# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── pinout: усі 24 контакти у двох симетричних рядах ──────────────────────────
# Ідея: показати фізичну розкладку A1..A12 / B1..B12 так, щоб одразу читалося
# дзеркало — B-ряд є A-ряд, повернутий на 180°. Колір кодує функцію.

A = ["GND","TX1+","TX1−","VBUS","CC1","D+","D−","SBU1","VBUS","RX2−","RX2+","GND"]
B = ["GND","RX1+","RX1−","VBUS","SBU2","D−","D+","CC2","VBUS","TX2−","TX2+","GND"]

def _pincolor(name):
    if name.startswith("VBUS"): return "#fdecea", POS      # живлення — гаряче
    if name.startswith("GND"):  return "#eef1f4", MUTED     # земля — сіре
    if name.startswith("CC"):   return "#e7f7ee", FIELD     # конфігурація — зелене
    if name.startswith("D"):    return "#eaf0fd", NEG       # USB 2.0 дані — синє
    if name.startswith(("TX","RX")): return "#f3ecfb", "#7c3aed"   # швидкі пари
    if name.startswith("SBU"):  return "#fff7e6", "#b7791f"        # боковина
    return FILL, INK

def _pinrow(y, names, prefix):
    cw, gap, x0 = 50, 4, 70
    out = []
    for i, nm in enumerate(names):
        x = x0 + i * (cw + gap)
        fill, edge = _pincolor(nm)
        out.append(rect(x, y, cw, 30, fill=fill, stroke=edge, sw=1.4, rx=4))
        out.append(text(x + cw / 2, y + 20, nm, size=12, color=edge, bold=True))
        out.append(text(x + cw / 2, y - 6 if prefix == "A" else y + 44,
                        "%s%d" % (prefix, i + 1), size=10, color=MUTED))
    return "".join(out), x0, cw, gap

def fig_pinout():
    W, H = 760, 300
    rowA, x0, cw, gap = _pinrow(70, A, "A")
    rowB, _, _, _ = _pinrow(150, B, "B")
    p = [rowA, rowB]
    # підписи рядів
    p.append(text(36, 90, "A", size=15, color=INK, bold=True))
    p.append(text(36, 170, "B", size=15, color=INK, bold=True))
    # дужка симетрії: A1 ↔ B12, A12 ↔ B1
    xL = x0 + cw / 2
    xR = x0 + 11 * (cw + gap) + cw / 2
    p.append(line(xL, 250, xR, 250, color=FIELD, sw=1.4, dash="5 4"))
    p.append(arrow(xL, 248, xL, 184, color=FIELD, sw=1.6))
    p.append(arrow(xR, 248, xR, 184, color=FIELD, sw=1.6))
    p.append(text(W / 2, 244, "поворот на 180° міняє ряди місцями: A1↔B12, A12↔B1",
                  size=12, color=FIELD, italic=True))
    # легенда
    leg = [("VBUS / GND — живлення", POS), ("CC — конфігурація", FIELD),
           ("D+/D− — USB 2.0", NEG), ("TX/RX — швидкі пари", "#7c3aed"),
           ("SBU — боковина", "#b7791f")]
    lx = 70
    for lbl, col in leg:
        p.append(circle(lx, 280, 5, fill=col, stroke=col, sw=1))
        p.append(text(lx + 10, 284, lbl, size=11, color=INK, anchor="start"))
        lx += text_width(lbl, 11) + 40
    render(os.path.join(OUT, "pinout.svg"), W, H, *p,
           title="24 контакти Type-C: два дзеркальні ряди")


# ── reversibility: чому штекер не має «верху» ────────────────────────────────
# Ідея: те саме гніздо, дві орієнтації штекера; функції збігаються, бо ряди
# дублюють одне одного. Активний CC різний — звідси й береться орієнтація.

def fig_reversibility():
    W, H = 720, 300
    p = []
    def jack(cx, cy, flipped):
        w, h = 230, 70
        x, y = cx - w / 2, cy - h / 2
        out = rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.6, rx=18)
        # язичок усередині
        out += rect(x + 20, cy - 9, w - 40, 18, fill="#eef1f4", stroke=MUTED, sw=1.1, rx=4)
        # активний CC — кружок з того боку, що мейтиться
        ccx = x + 40 if not flipped else x + w - 40
        out += circle(ccx, cy, 8, fill="#e7f7ee", stroke=FIELD, sw=2)
        out += text(ccx, cy + 4, "CC", size=9, color=FIELD, bold=True)
        return out
    p.append(jack(195, 110, False))
    p.append(text(195, 60, "штекер «лицем угору»", size=13, color=INK, bold=True))
    p.append(text(195, 165, "мейтиться CC1", size=12, color=FIELD))
    p.append(jack(525, 110, True))
    p.append(text(525, 60, "штекер перевернуто", size=13, color=INK, bold=True))
    p.append(text(525, 165, "мейтиться CC2", size=12, color=FIELD))
    # підсумок унизу
    box = fitbox(80, 210, 560, 64,
                 "VBUS, GND і D+/D− продубльовані на обидва ряди — тож працюють однаково "
                 "в будь-якій орієнтації.\nЄдине, що змінюється, — який саме CC проводить; "
                 "по ньому порт і впізнає поворот.",
                 size=13, fill="#f7faf8", stroke=FIELD)
    p.append(box)
    render(os.path.join(OUT, "reversibility.svg"), W, H, *p,
           title="Реверсивність: однаково обома боками")


# ── cc-roles: дільник Rp–Rd визначає роль, орієнтацію і струм ─────────────────
# Ідея: джерело тримає Rp (підтяжка до 5В), приймач — Rd до землі; разом це
# дільник. Активний CC просідає до напруги дільника → джерело впізнає приймача
# й читає, який струм воно саме оголосило (за номіналом Rp).

def fig_cc_roles():
    W, H = 720, 360
    p = []
    # джерело (DFP) ліворуч
    p.append(rect(40, 60, 150, 220, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(115, 84, "Джерело (DFP)", size=13, color=POS, bold=True))
    p.append(text(115, 104, "виставляє Rp", size=11, color=INK))
    p.append(line(115, 120, 115, 150, color=POS, sw=1.6))
    p.append(text(150, 138, "5 В", size=11, color=POS, anchor="start"))
    p.append(rect(95, 150, 40, 26, fill=BG, stroke=POS, sw=1.4, rx=3))
    p.append(text(115, 168, "Rp", size=12, color=POS, bold=True))
    # приймач (UFP) праворуч
    p.append(rect(530, 60, 150, 220, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    p.append(text(605, 84, "Приймач (UFP)", size=13, color=NEG, bold=True))
    p.append(text(605, 104, "виставляє Rd", size=11, color=INK))
    p.append(rect(585, 150, 40, 26, fill=BG, stroke=NEG, sw=1.4, rx=3))
    p.append(text(605, 168, "Rd", size=12, color=NEG, bold=True))
    p.append(text(640, 200, "5.1 кОм", size=11, color=NEG, anchor="start"))
    p.append(line(605, 176, 605, 210, color=NEG, sw=1.6))
    # земля приймача
    p.append(line(595, 210, 615, 210, color=INK, sw=2))
    p.append(line(599, 214, 611, 214, color=INK, sw=2))
    p.append(line(603, 218, 607, 218, color=INK, sw=2))
    # лінія CC між ними (дільник)
    p.append(line(135, 163, 585, 163, color=FIELD, sw=2.2))
    p.append(circle(360, 163, 6, fill="#e7f7ee", stroke=FIELD, sw=2))
    p.append(text(360, 146, "активний CC", size=12, color=FIELD, bold=True))
    p.append(text(360, 192, "напруга дільника Rp–Rd", size=12, color=FIELD, italic=True))
    # таблиця: Rp → струм
    p.append(text(360, 244, "Номінал Rp оголошує доступний струм:", size=12, color=INK, bold=True))
    rows = [("56 кОм", "USB за замовчуванням (0.5 / 0.9 А)"),
            ("22 кОм", "1.5 А"), ("10 кОм", "3.0 А")]
    ry = 262
    for rp, cur in rows:
        p.append(text(150, ry + 12, rp, size=12, color=POS, anchor="start", bold=True))
        p.append(text(260, ry + 12, "→  " + cur, size=12, color=INK, anchor="start"))
        ry += 26
    render(os.path.join(OUT, "cc-roles.svg"), W, H, *p,
           title="Дільник Rp–Rd: роль, орієнтація, струм")


# ── functions: чотири функціональні групи контактів ──────────────────────────
# Ідея: згорнути 24 піни в чотири ролі — щоб видно було, що для USB 2.0 досить
# малого підмножини, а решта вмикається під швидкість/відео/живлення кабелю.

def fig_functions():
    W, H = 720, 300
    p = []
    groups = [
        ("VBUS · GND", "живлення і земля", "×4 кожен, дубльовані", POS, "#fdecea"),
        ("CC1 · CC2", "конфігурація", "виявлення, орієнтація,\nроль, струм; один → VCONN", FIELD, "#e7f7ee"),
        ("D+ · D−", "USB 2.0", "дані й прошивка;\nдубльовані на обидва ряди", NEG, "#eaf0fd"),
        ("TX/RX ×2", "швидкі пари + SBU", "USB 3.x і alt-mode\n(DisplayPort тощо)", "#7c3aed", "#f3ecfb"),
    ]
    bw, gap, x0, y = 158, 16, 40, 70
    for i, (head, role, note, edge, fill) in enumerate(groups):
        x = x0 + i * (bw + gap)
        p.append(rect(x, y, bw, 150, fill=fill, stroke=edge, sw=1.6, rx=8))
        p.append(text(x + bw / 2, y + 28, head, size=14, color=edge, bold=True))
        p.append(line(x + 16, y + 40, x + bw - 16, y + 40, color=edge, sw=1))
        p.append(text(x + bw / 2, y + 62, role, size=12, color=INK, bold=True))
        p.append(mtext(x + bw / 2, y + 86, note, size=11, color=MUTED))
    p.append(text(W / 2, 252, "Для прошивки ESP32 по USB 2.0 досить VBUS, GND, D+/D− і Rd на CC.",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 274, "Швидкі пари, SBU і VCONN лишаються незадіяними.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "functions.svg"), W, H, *p,
           title="Чотири функціональні групи контактів")


# ── vconn: як джерело розрізняє Rd, Ra і порожнечу ───────────────────────────
# Ідея: після того, як на активному CC знайдено повноцінний Rd, джерело
# дивиться на ДРУГИЙ CC. Менший резистор Ra ≈ 1 кОм там — ознака кабелю з
# маркером; на цей контакт подається VCONN, що оживляє мікросхему e-marker.

def fig_vconn():
    W, H = 720, 330
    p = []
    # активний CC: Rd знайдено
    p.append(rect(40, 60, 300, 110, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    p.append(text(190, 84, "Активний CC", size=13, color=NEG, bold=True))
    p.append(text(190, 106, "Rd ≈ 5.1 кОм → є приймач", size=12, color=INK))
    p.append(text(190, 128, "по цій лінії піде узгодження", size=11, color=MUTED))
    p.append(text(190, 150, "і, далі, дані-конфігурація", size=11, color=MUTED))
    # другий CC: три варіанти
    p.append(text(530, 52, "Другий CC — що там?", size=13, color=INK, bold=True))
    opts = [
        ("Ra ≈ 0.8–1.2 кОм", "кабель з маркером → подати VCONN", FIELD, "#e7f7ee"),
        ("нічого (висить)", "пасивний кабель → VCONN не треба", MUTED, "#eef1f4"),
        ("ще один Rd", "приймач у безпровідній орієнтації", NEG, "#eaf0fd"),
    ]
    oy = 64
    for head, note, edge, fill in opts:
        p.append(rect(380, oy, 300, 56, fill=fill, stroke=edge, sw=1.4, rx=6))
        p.append(text(390, oy + 22, head, size=12, color=edge, anchor="start", bold=True))
        p.append(text(390, oy + 42, note, size=11, color=INK, anchor="start"))
        oy += 66
    # стрілка від активного до рішення
    p.append(arrow(340, 115, 378, 92, color=LINE, sw=1.6))
    # підсумок
    p.append(fitbox(40, 270, 640, 44,
                    "Той самий контакт буває лінією конфігурації або живленням кабелю VCONN — "
                    "вирішує, який резистор на ньому знайдено.",
                    size=13, fill="#f7faf8", stroke=FIELD))
    render(os.path.join(OUT, "vconn.svg"), W, H, *p,
           title="Незадіяний CC: Rd, Ra чи VCONN")


# ── altmode: ті самі швидкі пари ведуть або USB 3.x, або DisplayPort ──────────
# Ідея: фізичні контакти TX/RX і SBU не закріплені за одним протоколом; після
# домовленості по CC внутрішній мультиплексор перемикає їх на USB 3.x або на
# смуги DisplayPort (а SBU стає допоміжним каналом AUX).

def fig_altmode():
    W, H = 700, 320
    p = []
    # центральний мультиплексор
    p.append(rect(290, 130, 120, 90, fill="#f3ecfb", stroke="#7c3aed", sw=1.8, rx=8))
    p.append(mtext(350, 170, "MUX\nу пристрої", size=13, color="#7c3aed", bold=True))
    # вхід: фізичні контакти
    p.append(rect(40, 120, 180, 110, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(130, 142, "Фізичні контакти", size=12, color=INK, bold=True))
    p.append(text(130, 164, "TX1/RX1, TX2/RX2", size=11, color=MUTED))
    p.append(text(130, 184, "SBU1, SBU2", size=11, color=MUTED))
    p.append(text(130, 210, "(не закріплені за", size=10, color=MUTED))
    p.append(text(130, 224, "одним протоколом)", size=10, color=MUTED))
    p.append(arrow(220, 175, 288, 175, color=LINE, sw=1.8))
    # виходи: два режими
    p.append(rect(470, 70, 200, 70, fill="#e7f7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(570, 96, "USB 3.x", size=13, color=FIELD, bold=True))
    p.append(text(570, 118, "усі пари — дані SuperSpeed", size=11, color=INK))
    p.append(rect(470, 200, 200, 80, fill="#fff7e6", stroke="#b7791f", sw=1.5, rx=8))
    p.append(text(570, 226, "DisplayPort alt-mode", size=13, color="#b7791f", bold=True))
    p.append(text(570, 248, "пари → смуги відео,", size=11, color=INK))
    p.append(text(570, 266, "SBU → допоміжний AUX", size=11, color=INK))
    p.append(arrow(410, 160, 468, 110, color=LINE, sw=1.8))
    p.append(arrow(410, 190, 468, 235, color=LINE, sw=1.8))
    # хто командує
    p.append(text(350, 250, "режим обирає домовленість по CC", size=12, color=INK, bold=True))
    p.append(text(350, 270, "(USB-device чи DisplayPort)", size=11, color=MUTED))
    render(os.path.join(OUT, "altmode.svg"), W, H, *p,
           title="Alt-mode: ті самі піни, різні протоколи")


if __name__ == "__main__":
    fig_pinout()
    fig_reversibility()
    fig_cc_roles()
    fig_functions()
    fig_vconn()
    fig_altmode()
    print("done")
