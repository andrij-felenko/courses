# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"


def codebox(x, y, w, title, lines, accent=INK, fill="#fbfcff"):
    """Картка з моноширинними рядками: заголовок, роздільник, рядки."""
    h = 40 + len(lines) * 20 + 14
    out = [rect(x, y, w, h, fill=fill, stroke=accent, sw=1.8, rx=10)]
    out.append(text(x + w / 2, y + 22, title, size=12, color=accent, bold=True))
    out.append(line(x + 14, y + 32, x + w - 14, y + 32, color="#e4e4e4", sw=1.2))
    cy = y + 52
    for ln in lines:
        out.append(text(x + 16, cy, ln, size=11, color=INK, anchor="start"))
        cy += 20
    return "".join(out), h


# ── 1. context-is-registers: «контекст» = знімок регістрів процесора ───────────
def fig_context_is_registers():
    W, H = 760, 340
    p = []
    # Процесор: набір регістрів
    px, py, pw, ph = 60, 70, 300, 220
    p.append(rect(px, py, pw, ph, fill="#eef2fd", stroke=NEG, sw=2, rx=12))
    p.append(text(px + pw / 2, py + 24, "Процесорне ядро", size=13, color=NEG, bold=True))
    regs = [
        ("PC", "лічильник команд — де я в коді"),
        ("SP", "вказівник стека — де мій стек"),
        ("R0…R12", "робочі регістри — проміжні дані"),
        ("PSR", "прапорці — результат порівнянь"),
    ]
    ry = py + 46
    for name, desc in regs:
        p.append(rect(px + 16, ry, 90, 30, fill="#fbfcff", stroke=NEG, sw=1.4, rx=5))
        p.append(text(px + 16 + 45, ry + 20, name, size=12, color=NEG, bold=True))
        p.append(text(px + 118, ry + 20, desc, size=10, color=INK, anchor="start"))
        ry += 40
    # стрілка «знімок»
    p.append(arrow(px + pw + 12, py + ph / 2, px + pw + 78, py + ph / 2, color=POS, sw=2.2))
    p.append(text(px + pw + 45, py + ph / 2 - 12, "знімок", size=11, color=POS, bold=True))
    # Знімок = контекст
    cx, cy2, cw, ch = px + pw + 90, py + 34, 260, 152
    p.append(rect(cx, cy2, cw, ch, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    p.append(text(cx + cw / 2, cy2 + 24, "Контекст задачі", size=13, color=FIELD, bold=True))
    p.append(mtext(cx + cw / 2, cy2 + 58,
                   ["усі ці значення разом —", "повний «стан свідомості» задачі", "тієї миті, коли її спинили"],
                   size=11, color=INK, lh=1.35))
    p.append(text(cx + cw / 2, cy2 + ch + 22,
                  "відновиш ці значення — задача побіжить далі, наче не спинялася",
                  size=10, color=MUTED, italic=True))
    p.append(text(W / 2, H - 12,
                  "«контекст» — це не абстракція, а конкретний набір регістрів процесора",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "context-is-registers.svg"), W, H, *p,
           title="Що таке контекст: знімок регістрів")


# ── 2. three-steps: зберегти на свій стек → підмінити SP → відновити з чужого ──
def fig_three_steps():
    W, H = 780, 360
    p = []
    # Два стеки — A (спиняється) і B (пускається)
    def stack(x, name, accent, top_lbl, filled):
        sx, sy, sw2, sh = x, 80, 150, 210
        out = [rect(sx, sy, sw2, sh, fill="#fbfcff", stroke=accent, sw=1.8, rx=8)]
        out.append(text(sx + sw2 / 2, sy - 10, name, size=12, color=accent, bold=True))
        # шари знизу вгору
        base = ["локальні", "виклики"]
        segs = list(base)
        if filled:
            segs = base + ["КАДР", "регістрів"]
        lh = 34
        yy = sy + sh - 14 - lh
        fills = ["#eef2f7", "#eef2f7", "#fdecea", "#fdecea"]
        for i, lab in enumerate(segs):
            col = POS if lab in ("КАДР", "регістрів") else "#cfd6dd"
            out.append(rect(sx + 12, yy, sw2 - 24, lh - 4, fill=fills[i], stroke=col, sw=1.2, rx=4))
            out.append(text(sx + sw2 / 2, yy + 20, lab, size=10,
                            color=(POS if col == POS else INK),
                            bold=(col == POS)))
            yy -= lh
        # SP-стрілка на верхівку заповненого
        top_y = yy + lh
        out.append(text(sx + sw2 + 6, top_y + 14, top_lbl, size=10, color=accent, anchor="start", bold=True))
        return "".join(out)

    p.append(stack(70, "стек задачі A", NEG, "SP тут", True))
    p.append(stack(560, "стек задачі B", FIELD, "SP звідси", True))

    # Середня колонка — три кроки
    mx = 300
    steps = [
        ("1", "зберегти регістри A", "на ЇЇ стек", NEG),
        ("2", "підмінити SP", "A → B", POS),
        ("3", "відновити регістри B", "з ЇЇ стека", FIELD),
    ]
    sy = 96
    for num, t1, t2, col in steps:
        p.append(circle(mx + 90, sy + 18, 16, fill="#fff", stroke=col, sw=2))
        p.append(text(mx + 90, sy + 23, num, size=13, color=col, bold=True))
        p.append(text(mx + 90, sy + 52, t1, size=11, color=col, bold=True))
        p.append(text(mx + 90, sy + 70, t2, size=10, color=MUTED))
        sy += 84
    # напрямок: зі стека A (крок 1) до стека B (крок 3) — короткі стрілки в чистих коридорах
    p.append(arrow(224, 300, 356, 300, color=NEG, sw=1.6))     # A → кроки (нижній коридор, під написами)
    p.append(text(290, 292, "від A", size=10, color=NEG, bold=True))
    p.append(arrow(486, 300, 556, 300, color=FIELD, sw=1.6))   # кроки → B
    p.append(text(521, 292, "до B", size=10, color=FIELD, bold=True))
    p.append(text(W / 2, H - 12,
                  "контекст живе НЕ в планувальнику, а на власному стеку кожної задачі; SP — єдина «ручка» до нього",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-steps.svg"), W, H, *p,
           title="Механізм: зберегти → підмінити SP → відновити")


# ── 3. hw-sw-split: хто зберігає які регістри на Cortex-M (і чому — ABI) ────────
def fig_hw_sw_split():
    W, H = 760, 330
    p = []
    # Ліворуч — залізо (автоматично)
    hx, hy, hw2, hh = 60, 80, 300, 190
    p.append(rect(hx, hy, hw2, hh, fill="#eef2fd", stroke=NEG, sw=2, rx=12))
    p.append(text(hx + hw2 / 2, hy + 24, "Залізо — само, на вході в переривання", size=11, color=NEG, bold=True))
    p.append(text(hx + hw2 / 2, hy + 46, "caller-saved (за ABI — леткі)", size=10, color=MUTED, italic=True))
    hwregs = "R0  R1  R2  R3  R12  LR  PC  PSR"
    p.append(rect(hx + 18, hy + 60, hw2 - 36, 44, fill="#fbfcff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(hx + hw2 / 2, hy + 87, hwregs, size=12, color=NEG, bold=True))
    p.append(mtext(hx + hw2 / 2, hy + 128,
                   ["ці регістри й так «леткі» — код",
                    "уже не чекає їх цілими після виклику,",
                    "тож залізо стекає їх безкоштовно"],
                   size=10, color=INK, lh=1.3))

    # Праворуч — планувальник (вручну)
    sx2, sy2, sw3, sh2 = 400, 80, 300, 190
    p.append(rect(sx2, sy2, sw3, sh2, fill="#eafaf0", stroke=FIELD, sw=2, rx=12))
    p.append(text(sx2 + sw3 / 2, sy2 + 24, "Планувальник — вручну, у PendSV", size=11, color=FIELD, bold=True))
    p.append(text(sx2 + sw3 / 2, sy2 + 46, "callee-saved (за ABI — збережні)", size=10, color=MUTED, italic=True))
    swregs = "R4  R5  R6  R7  R8  R9  R10  R11"
    p.append(rect(sx2 + 18, sy2 + 60, sw3 - 36, 44, fill="#fbfcff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(sx2 + sw3 / 2, sy2 + 87, swregs, size=12, color=FIELD, bold=True))
    p.append(mtext(sx2 + sw3 / 2, sy2 + 128,
                   ["ці регістри код лишав цілими через",
                    "виклики — тож саме їх мусить зберегти",
                    "код перемикання, залізо їх не чіпає"],
                   size=10, color=INK, lh=1.3))

    p.append(text(W / 2, H - 12,
                  "поділ праці збігається з поділом ABI: разом обидві половини й дають повний контекст",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hw-sw-split.svg"), W, H, *p,
           title="Хто що зберігає (на прикладі Cortex-M)")


# ── 4. switch-cost: ціна перемикання — і чому потоки дешевші за процеси ─────────
def fig_switch_cost():
    W, H = 817, 320
    p = []
    ox = 70
    track_w = 620
    # Верхня смуга: часта скибочка — багато накладних
    def timeline(y, label, slice_frac, ov_frac, ncells):
        out = [text(ox - 10, y + 18, label, size=11, color=INK, anchor="end", bold=True)]
        x = ox
        cw = track_w / ncells
        for i in range(ncells):
            ov_w = cw * ov_frac
            work_w = cw - ov_w
            out.append(rect(x, y, ov_w, 34, fill="#fdecea", stroke=POS, sw=1.0, rx=2))
            out.append(rect(x + ov_w, y, work_w, 34, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=2))
            x += cw
        return "".join(out)

    p.append(timeline(80, "часто", 0.4, 0.42, 9))
    p.append(text(ox + track_w + 8, 80 + 18, "багато перемикань →", size=10, color=POS, anchor="start", bold=True))
    p.append(text(ox + track_w + 8, 80 + 32, "багато накладних", size=10, color=POS, anchor="start"))

    p.append(timeline(150, "рідко", 0.85, 0.12, 3))
    p.append(text(ox + track_w + 8, 150 + 18, "мало перемикань →", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + track_w + 8, 150 + 32, "більше корисного", size=10, color=FIELD, anchor="start"))

    # легенда
    p.append(rect(ox, 210, 16, 16, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    p.append(text(ox + 24, 223, "накладні витрати перемикання (зберегти/відновити)", size=10, color=INK, anchor="start"))
    p.append(rect(ox, 236, 16, 16, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(ox + 24, 249, "корисна робота задачі", size=10, color=INK, anchor="start"))

    p.append(fitbox(ox, 272, track_w, 32,
                    "потік ↔ потік: лише регістри — дешево  ·  процес ↔ процес: ще й скидання кешу/TLB — у рази дорожче",
                    size=11, fill="#f4f6f8", stroke=MUTED, sw=1.2, color=INK))
    render(os.path.join(OUT, "switch-cost.svg"), W, H, *p,
           title="Ціна перемикання — і де вона більша")


if __name__ == "__main__":
    fig_context_is_registers()
    fig_three_steps()
    fig_hw_sw_split()
    fig_switch_cost()
    print("OK: figures written to", OUT)
