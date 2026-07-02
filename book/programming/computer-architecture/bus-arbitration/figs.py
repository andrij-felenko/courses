# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── contention: два майстри просять шину, арбітр пропускає одного ──────────────
# Ідея: ядро й DMA — обидва майстри — піднімають REQ одночасно. Одна шина фізично
# не веде дві транзакції. Арбітр обирає одного (GRANT), другий стоїть до звільнення.

def fig_contention():
    W, H = 720, 380
    p = []

    # шина внизу — спільний фізичний ресурс
    bus_y, bus_x, bus_w = 300, 70, 580
    p.append(rect(bus_x, bus_y, bus_w, 34, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=4))
    p.append(text(W / 2, bus_y + 22, "Системна шина — одна, веде одну транзакцію за раз", size=12, color=NEG, bold=True))

    # арбітр посередині
    arb, aw, ah = textbox(W / 2, 208, "арбітр", size=13, bold=True,
                          fill="#fff9e6", stroke="#e0a800", sw=2.0, pad=12)
    p.append(arb)
    p.append(line(W / 2, 208 + ah / 2, W / 2, bus_y, color="#e0a800", sw=1.8))

    # два майстри вгорі
    core, cw, ch = textbox(180, 92, "ядро\n(майстер)", size=12, bold=True, pad=11)
    p.append(core)
    dma, dw, dh = textbox(540, 92, "DMA\n(майстер)", size=12, bold=True,
                          fill="#d4edda", stroke=FIELD, sw=2.0, pad=11)
    p.append(dma)

    # REQ обох піднято до арбітра
    p.append(arrow(180, 92 + ch / 2, W / 2 - aw / 2 - 4, 208 - ah / 3, color=INK, sw=1.7))
    p.append(text(300, 150, "REQ", size=11, color=INK, bold=True))
    p.append(arrow(540, 92 + dh / 2, W / 2 + aw / 2 + 4, 208 - ah / 3, color=FIELD, sw=1.7))
    p.append(text(430, 150, "REQ", size=11, color=FIELD, bold=True))

    # GRANT — лише одному (ядру): суцільна зелена; іншому — відмова (пунктир, чекає)
    p.append(arrow(W / 2 - aw / 2 - 4, 208 + ah / 3, 180, 92 + ch / 2 + 2, color=POS, sw=2.2))
    p.append(text(210, 178, "GRANT", size=11, color=POS, bold=True, anchor="start"))
    p.append(line(W / 2 + aw / 2 + 4, 208 + ah / 3, 540, 92 + dh / 2 + 2, color=MUTED, sw=1.5, dash="5 4"))
    p.append(text(560, 178, "чекає", size=11, color=MUTED, anchor="start", italic=True))

    # легенда
    ly = 356
    p.append(line(80, ly, 112, ly, color=POS, sw=3))
    p.append(text(120, ly + 4, "надано (GRANT) — майстер шле транзакцію", size=11, color=INK, anchor="start"))
    p.append(line(440, ly, 472, ly, color=MUTED, sw=2.5, dash="5 4"))
    p.append(text(480, ly + 4, "відкладено — стоїть у черзі", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "contention.svg"), W, H, *p,
           title="Двоє просять — одна шина: арбітр пропускає одного, другий чекає")


# ── priority-vs-rr: фіксований пріоритет (голодування) проти каруселі ──────────
# Ідея: обидва майстри просять кожного такту. За фіксованого пріоритету
# високий бере шину завжди — низький голодує. Карусель чергує власника по колу.

def fig_priority_vs_rr():
    W, H = 720, 340
    p = []
    x0, x1 = 130, 660
    n = 12
    cell = (x1 - x0) / n

    def owner_lane(y, owners, m0_label, m1_label):
        # два ряди: хто отримав шину цього такту (M0 угорі, M1 унизу)
        for i, who in enumerate(owners):
            cx = x0 + i * cell
            top = (who == 0)
            # M0
            fill0 = "#fdecea" if top else "#f4f6f8"
            p.append(rect(cx, y - 26, cell - 3, 22, fill=fill0,
                          stroke=POS if top else "#c8ccd0", sw=1.3 if top else 1.0, rx=0))
            if top:
                p.append(text(cx + (cell - 3) / 2, y - 10, "▶", size=10, color=POS, bold=True))
            # M1
            fill1 = "#d4edda" if not top else "#f4f6f8"
            p.append(rect(cx, y - 2, cell - 3, 22, fill=fill1,
                          stroke=FIELD if not top else "#c8ccd0", sw=1.3 if not top else 1.0, rx=0))
            if not top:
                p.append(text(cx + (cell - 3) / 2, y + 13, "▶", size=10, color=FIELD, bold=True))
        p.append(text(x0 - 10, y - 11, m0_label, size=11, color=POS, bold=True, anchor="end"))
        p.append(text(x0 - 10, y + 13, m1_label, size=11, color=FIELD, bold=True, anchor="end"))

    # фіксований пріоритет: M0 завжди, M1 ніколи
    y1 = 96
    p.append(text(x0, y1 - 44, "Фіксований пріоритет — обидва просять кожен такт", size=12, color=INK, bold=True, anchor="start"))
    owner_lane(y1, [0] * n, "M0 ↑", "M1 ↓")
    p.append(text(x1 + 6, y1 + 13, "голодує", size=11, color=POS, anchor="start", bold=True))

    # карусель: власник іде по колу
    y2 = 236
    p.append(text(x0, y2 - 44, "Карусель (round-robin) — черга йде по колу", size=12, color=INK, bold=True, anchor="start"))
    owner_lane(y2, [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], "M0", "M1")
    p.append(text(x1 + 6, y2 + 1, "обидва рухаються", size=11, color=INK, anchor="start"))

    # вісь часу
    p.append(text(x0, 316, "такти шини →", size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "priority-vs-rr.svg"), W, H, *p,
           title="Фіксований пріоритет голодує слабшого; карусель дає всім хід")


# ── handshake: REQ/GRANT/шина за тактами — латентність арбітражу ───────────────
# Ідея: майстер піднімає REQ; арбітр вирішує й піднімає GRANT (не миттєво —
# зазвичай наступного такту); лише тоді майстер веде транзакцію на шині.

def fig_handshake():
    W, H = 720, 320
    p = []
    x0, x1 = 150, 670
    T = 8
    dt = (x1 - x0) / T
    hi, lo = 18, 22   # висота «високого» рівня вгору від базової лінії

    # такти-сітка
    for i in range(T + 1):
        gx = x0 + i * dt
        p.append(line(gx, 70, gx, 250, color="#e5e8eb", sw=1.0))
    p.append(text(x0, 268, "такти шини →", size=10, color=MUTED, anchor="start", italic=True))
    for i in range(T):
        p.append(text(x0 + i * dt + dt / 2, 266, str(i), size=9, color=MUTED))

    def wave(y, name, hi_from, hi_to, col):
        # цифровий сигнал: 0 до hi_from, 1 у [hi_from,hi_to), 0 далі
        base = y
        top = y - lo
        p.append(text(x0 - 12, y - 6, name, size=11, color=col, bold=True, anchor="end"))
        pts = []
        pts.append((x0, base))
        xa = x0 + hi_from * dt
        xb = x0 + hi_to * dt
        pts.append((xa, base)); pts.append((xa, top))
        pts.append((xb, top)); pts.append((xb, base))
        pts.append((x1, base))
        d = "M %.1f %.1f " % pts[0]
        for (px, py) in pts[1:]:
            d += "L %.1f %.1f " % (px, py)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, col))

    wave(112, "REQ", 1, 6, INK)          # майстер просить з такту 1
    wave(168, "GRANT", 2, 6, POS)        # арбітр надає з такту 2 (на такт пізніше)
    # шина: транзакція йде, поки є GRANT (такти 2..5)
    y3 = 224
    p.append(text(x0 - 12, y3 - 6, "шина", size=11, color=NEG, bold=True, anchor="end"))
    bx = x0 + 2 * dt
    bw = 4 * dt
    p.append(rect(bx, y3 - lo, bw, lo, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    p.append(text(bx + bw / 2, y3 - 6, "транзакція майстра", size=10, color=NEG, bold=True))

    # позначка латентності між REQ↑ і GRANT↑
    la = x0 + 1 * dt
    lb = x0 + 2 * dt
    p.append(line(la, 84, la, 60, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(lb, 140, lb, 60, color=MUTED, sw=1.0, dash="3 3"))
    p.append(arrow(la, 66, lb, 66, color="#a07800", sw=1.5))
    p.append(text((la + lb) / 2, 56, "затримка арбітражу", size=10, color="#a07800"))

    render(os.path.join(OUT, "handshake.svg"), W, H, *p,
           title="Рукостискання REQ → GRANT → транзакція коштує тактів шини")


# ── daisy-grant: лінія надання йде крізь пристрої послідовно ───────────────────
# Ідея (hist): одна лінія grant проходить від арбітра крізь пристрої по черзі.
# Ближній, якщо просить, «з'їдає» надання й бере шину; дальні мовчать. Твердий
# пріоритет за місцем: хто ближче до арбітра — той завжди перший, дальній голодує.

def fig_daisy_grant():
    W, H = 760, 300
    p = []

    ay = 150
    # арбітр зліва
    arb, aw, ah = textbox(78, ay, "арбітр\n(ЦП)", size=12, bold=True,
                          fill="#fff9e6", stroke="#e0a800", sw=2.0, pad=11)
    p.append(arb)

    # три пристрої в ряд; grant тече крізь них зліва направо
    xs = [250, 430, 610]
    bw2, bh2 = 120, 66
    labels = ["пристрій A\n(ближній)", "пристрій B", "пристрій C\n(дальній)"]
    reqs = [False, True, True]   # B і C просять; A — ні

    boxes = []
    for x, lab, req in zip(xs, labels, reqs):
        fill = "#d4edda" if req else "#f4f6f8"
        strk = FIELD if req else "#c8ccd0"
        p.append(rect(x - bw2 / 2, ay - bh2 / 2, bw2, bh2, fill=fill, stroke=strk, sw=1.8, rx=6))
        p.append(mtext(x, ay - 5, lab.split("\n"), size=11, color=INK, bold=True))
        boxes.append(x)

    # grant-лінія: арбітр → A → (пропущено) → B (з'їдає)
    gy = ay
    # арбітр → A
    p.append(arrow(78 + aw / 2, gy, xs[0] - bw2 / 2, gy, color=POS, sw=2.4))
    p.append(text((78 + aw / 2 + xs[0] - bw2 / 2) / 2, gy - 8, "GRANT", size=10, color=POS, bold=True))
    # A → B (A не просив → пропускає далі)
    p.append(arrow(xs[0] + bw2 / 2, gy, xs[1] - bw2 / 2, gy, color=POS, sw=2.4))
    p.append(text((xs[0] + bw2 / 2 + xs[1] - bw2 / 2) / 2, gy - 8, "пропуск", size=10, color=POS, italic=True))
    # B «з'їдає» — далі надання НЕ йде (сірий обрубок-пунктир)
    p.append(line(xs[1] + bw2 / 2, gy, xs[2] - bw2 / 2, gy, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text((xs[1] + bw2 / 2 + xs[2] - bw2 / 2) / 2, gy - 8, "далі не доходить", size=10, color=MUTED, italic=True))

    # позначки: B бере шину; C голодує
    p.append(text(xs[1], ay + bh2 / 2 + 20, "▲ бере шину", size=11, color=FIELD, bold=True))
    p.append(text(xs[2], ay + bh2 / 2 + 20, "голодує, поки просить B", size=10.5, color=POS, bold=True))
    p.append(text(xs[0], ay + bh2 / 2 + 20, "не просить", size=10.5, color=MUTED, italic=True))

    # напрям пріоритету
    p.append(text(W / 2, H - 18, "пріоритет спадає зліва направо — за фізичним місцем у ланцюжку",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "daisy-grant.svg"), W, H, *p,
           title="Ланцюжкове надання: ближній «з'їдає» grant, дальній голодує")


# ── daisy-delay: затримка проходження grant крізь ланцюжок ─────────────────────
# Ідея (hist): у daisy chain надання мусить пробігти крізь усіх послідовно —
# затримки складаються (n·t). Паралельний арбітр веде окрему лінію до кожного —
# рішення приходить усім за один крок, незалежно від довжини.

def fig_daisy_delay():
    W, H = 760, 360
    p = []

    # ── верх: daisy — затримки складаються ──
    ty = 96
    p.append(text(30, ty - 46, "Ланцюжок: grant біжить крізь усіх — затримки складаються",
                  size=12, color=INK, bold=True, anchor="start"))
    ax = 70
    arb1, aw1, ah1 = textbox(ax, ty, "арбітр", size=11, bold=True,
                             fill="#fff9e6", stroke="#e0a800", sw=1.8, pad=9)
    p.append(arb1)
    xs = [210, 350, 490, 630]
    prev = ax + aw1 / 2
    for i, x in enumerate(xs):
        p.append(rect(x - 42, ty - 22, 84, 44, fill="#f4f6f8", stroke="#c8ccd0", sw=1.6, rx=6))
        p.append(text(x, ty + 4, "П%d" % (i + 1), size=12, color=INK, bold=True))
        p.append(arrow(prev, ty, x - 42, ty, color=NEG, sw=1.9))
        p.append(text((prev + x - 42) / 2, ty - 7, "t", size=10, color=NEG, italic=True))
        prev = x + 42
    p.append(text(W - 30, ty + 40, "до П4 — затримка 4·t", size=11, color=POS, bold=True, anchor="end"))

    # ── низ: паралельний арбітр — окрема лінія до кожного ──
    by = 268
    p.append(text(30, by - 60, "Паралельний арбітр: окрема лінія до кожного — рішення всім за один крок",
                  size=12, color=INK, bold=True, anchor="start"))
    arb2, aw2, ah2 = textbox(70, by, "арбітр", size=11, bold=True,
                             fill="#fff9e6", stroke="#e0a800", sw=1.8, pad=9)
    p.append(arb2)
    for i, x in enumerate(xs):
        p.append(rect(x - 42, by - 22, 84, 44, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
        p.append(text(x, by + 4, "П%d" % (i + 1), size=12, color=INK, bold=True))
        p.append(arrow(70 + aw2 / 2, by - 16 + i * 0, x - 42, by, color=FIELD, sw=1.7))
    p.append(text(W - 30, by + 40, "усім — затримка 1·t", size=11, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(OUT, "daisy-delay.svg"), W, H, *p,
           title="Чому ланцюжок повільніший: затримки складаються vs паралельні лінії")


if __name__ == "__main__":
    fig_contention()
    fig_priority_vs_rr()
    fig_handshake()
    fig_daisy_grant()
    fig_daisy_delay()
    print("OK: figures written to", OUT)
