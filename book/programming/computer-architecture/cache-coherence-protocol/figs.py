# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── machine: протокол як скінченний автомат (вхід/пам'ять/вихід) ────────────────
# Ідея: показати, ЩО таке протокол як механізм. Це автомат на кожну лінію:
# ВХІД — дія свого ядра (PrRd/PrWr) або підслуханий чужий запит із шини;
# ПАМ'ЯТЬ — стан лінії (біти в тегу); ВИХІД — що кинути в шину (BusRd/BusRdX/…)
# і новий стан. Однакові вхідні дії в різних станах дають різні виходи — у цьому
# вся суть автомата.

def fig_machine():
    W, H = 760, 360
    p = []

    # центральна коробка — автомат
    mx, my, mw, mh = 300, 120, 160, 130
    p.append(rect(mx, my, mw, mh, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(mx + mw / 2, my + 34, "автомат", size=14, color=INK, bold=True))
    p.append(text(mx + mw / 2, my + 52, "лінії", size=14, color=INK, bold=True))
    # пам'ять-стан усередині
    p.append(rect(mx + 22, my + 66, mw - 44, 44, fill="#ffffff", stroke=MUTED, sw=1.4, rx=4))
    p.append(text(mx + mw / 2, my + 84, "стан лінії", size=9.5, color=MUTED))
    p.append(text(mx + mw / 2, my + 100, "M · E · S · I", size=11, color=INK, bold=True))

    # ── вхід зліва: дві причини переходу ──
    p.append(text(150, 78, "ВХІД — що трапилось", size=11, color=INK, anchor="middle", bold=True))
    p.append(fitbox(40, 96, 220, 40, "своє ядро: PrRd (читаю) /\nPrWr (пишу)",
                    size=10, fill="#eafaf0", stroke=FIELD, color=INK))
    p.append(fitbox(40, 148, 220, 44, "чужий запит із шини:\nBusRd / BusRdX (підслухано)",
                    size=10, fill="#fdf1ec", stroke=POS, color=INK))
    p.append(arrow(262, 118, mx, my + 46, color=FIELD, sw=1.8))
    p.append(arrow(262, 170, mx, my + 96, color=POS, sw=1.8))

    # ── вихід справа: дві дії ──
    p.append(text(610, 78, "ВИХІД — що зробити", size=11, color=INK, anchor="middle", bold=True))
    p.append(fitbox(500, 96, 220, 40, "кинути в шину:\nBusRd / BusRdX / BusUpgr",
                    size=10, fill="#eef4ff", stroke=NEG, color=INK))
    p.append(fitbox(500, 148, 220, 44, "перейти в новий стан\n(і, може, віддати дані)",
                    size=10, fill="#f4f6f8", stroke=MUTED, color=INK))
    p.append(arrow(mx + mw, my + 46, 500, 118, color=NEG, sw=1.8))
    p.append(arrow(mx + mw, my + 96, 500, 170, color=MUTED, sw=1.8))

    # висновок унизу
    p.append(fitbox(150, 288, 460, 46,
                    "Та сама дія в РІЗНИХ станах дає різний вихід: запис у стані Exclusive — тихий,\nа той самий запис у Shared мусить кинути invalidate у шину. У цьому вся суть.",
                    size=10, fill="#ffffff", stroke=INK, color=INK, bold=True))

    render(os.path.join(OUT, "machine.svg"), W, H, *p,
           title="Протокол — це скінченний автомат на кожну кеш-лінію")


# ── msi: повний автомат трьох станів із шинними переходами ─────────────────────
# Ідея: найпростіший робочий протокол — три стани M·S·I. Показуємо ОБИДВА види
# переходів: суцільні — від дій СВОГО ядра (PrRd/PrWr), пунктирні — від
# ПІДСЛУХАНИХ чужих запитів. Видно ключову асиметрію: у стані M підслуханий чужий
# BusRd змушує віддати свіжі дані й упасти в S; чужий BusRdX — узагалі в I.

def fig_msi():
    W, H = 820, 470
    p = []

    # Три стани трикутником, широко рознесені: M ліворуч, S праворуч, I внизу.
    st = {
        "M": (180, 140, "M — Modified", "єдина змінена копія;\nпам'ять застаріла", "#fdecea", POS),
        "S": (640, 140, "S — Shared", "чиста копія; може бути\nв інших ядрах", "#eef4ff", NEG),
        "I": (410, 380, "I — Invalid", "копії немає", "#f0f1f3", MUTED),
    }
    bw, bh = 190, 82
    def edge(k, side):
        cx, cy = st[k][0], st[k][1]
        return {"L": (cx - bw / 2, cy), "R": (cx + bw / 2, cy),
                "T": (cx, cy - bh / 2), "B": (cx, cy + bh / 2),
                "BL": (cx - bw / 3, cy + bh / 2), "BR": (cx + bw / 3, cy + bh / 2),
                "TL": (cx - bw / 3, cy - bh / 2), "TR": (cx + bw / 3, cy - bh / 2)}[side]
    for k, (cx, cy, name, sub, fill, col) in st.items():
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.9))
        p.append(text(cx, cy - 15, name, size=13, color=INK, bold=True))
        for i, ln in enumerate(sub.split("\n")):
            p.append(text(cx, cy + 6 + i * 15, ln, size=9.5, color=INK))

    def solid(ax, ay, bx, by, color):
        p.append(arrow(ax, ay, bx, by, color=color, sw=1.9))

    def dashed(ax, ay, bx, by, color):
        p.append(line(ax, ay, bx, by, color=color, sw=1.7, dash="6 4"))
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.7" marker-end="url(#arrow)"/>'
                 % ((ax + (bx - ax) * 0.85), (ay + (by - ay) * 0.85), bx, by, color))

    def lab(lx, ly, label, color, italic=False):
        for i, ln in enumerate(label.split("\n")):
            p.append(text(lx, ly + i * 13, ln, size=9.5, color=color, bold=not italic, italic=italic))

    # ── дії свого ядра (суцільні), ліва половина ──
    # I → M : запис у порожню (BusRdX). Ліва гілка трикутника.
    (ax, ay), (bx, by) = edge("I", "TL"), edge("M", "B")
    solid(ax, ay, bx, by, POS);  lab(210, 300, "PrWr\n→ BusRdX", POS)
    # I → S : читання порожньої (BusRd). Права гілка трикутника.
    (ax, ay), (bx, by) = edge("I", "TR"), edge("S", "B")
    solid(ax, ay, bx, by, NEG);  lab(590, 300, "PrRd\n→ BusRd", NEG)
    # S → M : апгрейд (BusUpgr). Верхня горизонталь, трохи вище центрів.
    solid(st["S"][0] - bw / 2, 122, st["M"][0] + bw / 2, 122, POS)
    lab(410, 110, "PrWr → BusUpgr (апгрейд S → M)", POS)

    # «влучив» — петлі-підписи над боксами
    p.append(text(180, 140 - bh / 2 - 10, "PrRd/PrWr: влучив (лишається)", size=8.5, color=POS, italic=True))
    p.append(text(640, 140 - bh / 2 - 10, "PrRd: влучив (лишається)", size=8.5, color=NEG, italic=True))

    # ── підслухані з шини (пунктир), нижче горизонталі S→M ──
    # M → S : чужий BusRd — віддай дані, стань спільним. Горизонталь по центрах.
    dashed(st["M"][0] + bw / 2, 158, st["S"][0] - bw / 2, 158, POS)
    lab(410, 176, "чужий BusRd: віддай свіжі дані, стань S", POS, italic=True)
    # M → I : чужий BusRdX. Ліва внутрішня діагональ.
    (ax, ay), (bx, by) = edge("M", "BR"), edge("I", "TL")
    dashed(ax, ay, bx, by, POS);  lab(250, 250, "чужий BusRdX:\nвіддай, стань I", POS, italic=True)
    # S → I : чужий BusRdX. Права внутрішня діагональ.
    (ax, ay), (bx, by) = edge("S", "BL"), edge("I", "TR")
    dashed(ax, ay, bx, by, NEG);  lab(560, 250, "чужий BusRdX:\nвикинь копію", NEG, italic=True)

    # легенда
    p.append(line(70, 42, 100, 42, color=INK, sw=2))
    p.append(text(106, 46, "дія СВОГО ядра (PrRd/PrWr)", size=9.5, color=INK, anchor="start"))
    p.append(line(430, 42, 460, 42, color=MUTED, sw=1.7, dash="6 4"))
    p.append(text(466, 46, "ПІДСЛУХАНО чуже з шини", size=9.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "msi.svg"), W, H, *p,
           title="MSI: найпростіший робочий автомат — три стани")


# ── owned: чого коштує ділити брудну лінію в MESI й що дає стан Owned ───────────
# Ідея: у MESI лінію в стані Modified не можна лишити брудною, коли її просить
# інший, — доводиться СПЕРШУ записати в пам'ять (write-back), і лише тоді обидва
# в Shared. Це зайвий похід у RAM. MOESI додає Owned: власник віддає дані прямо
# сусіду з кеша, лишається Owned (брудний, але спільний), пам'ять НЕ чіпаємо.

def fig_owned():
    W, H = 760, 420
    p = []

    midx = W / 2
    p.append(line(midx, 54, midx, H - 24, color="#d8dde3", sw=1.4, dash="5 4"))

    def core(x, y, name, val, state, col, fill):
        p.append(rect(x, y, 128, 58, fill=fill, stroke=col, sw=1.7))
        p.append(text(x + 64, y + 22, name, size=11.5, color=INK, bold=True))
        p.append(text(x + 64, y + 40, "%s · %s" % (val, state), size=10, color=INK, bold=True))

    def ram(x, y, val, col):
        p.append(rect(x, y, 128, 46, fill="#fdf4f4", stroke=col, sw=1.5))
        p.append(text(x + 64, y + 19, "RAM", size=10, color=INK, bold=True))
        p.append(text(x + 64, y + 36, val, size=10, color=INK, bold=True))

    # ── ліворуч: MESI ──
    p.append(text(midx / 2, 46, "MESI: брудну лінію треба спершу записати", size=11.5, color=POS, anchor="middle", bold=True))
    core(30, 78, "ядро A", "X=8", "Modified", POS, "#fdecea")
    p.append(text(168, 118, "B просить", size=9, color=MUTED, anchor="start"))
    p.append(text(168, 131, "брудну X", size=9, color=MUTED, anchor="start"))
    # крок write-back у RAM
    p.append(arrow(94, 136, 94, 176, color=POS, sw=1.8))
    ram(30, 178, "X: 5 → 8", POS)
    p.append(text(94, 240, "1) write-back у RAM (зайвий похід)", size=9, color=POS, anchor="middle", bold=True))
    core(30, 258, "ядро A", "X=8", "Shared", NEG, "#eef4ff")
    core(210, 258, "ядро B", "X=8", "Shared", NEG, "#eef4ff")
    p.append(arrow(160, 200, 250, 256, color=NEG, sw=1.6))
    p.append(text(midx / 2, 340, "2) обидва Shared, але пам'ять уже чіпали", size=9.5, color=INK, anchor="middle"))
    p.append(fitbox(30, 354, 308, 40, "Ціна: кожне «брудна → спільна»\n= зайвий запис у повільну RAM",
                    size=10, fill="#fdecea", stroke=POS, color=INK, bold=True))

    # ── праворуч: MOESI ──
    rx0 = midx + 30
    p.append(text(midx + midx / 2, 46, "MOESI: власник Owned віддає дані прямо", size=11.5, color=FIELD, anchor="middle", bold=True))
    core(rx0, 78, "ядро A", "X=8", "Modified", POS, "#fdecea")
    p.append(text(rx0 + 64 + 90, 152, "B просить X", size=9.5, color=MUTED, anchor="middle"))
    # дані прямо в кеш B, RAM не чіпаємо
    core(rx0, 178, "ядро A", "X=8", "Owned", FIELD, "#eafaf0")
    core(rx0 + 180, 178, "ядро B", "X=8", "Shared", NEG, "#eef4ff")
    p.append(arrow(rx0 + 128, 200, rx0 + 178, 200, color=FIELD, sw=2))
    p.append(text(midx + midx / 2, 234, "дані кеш→кеш, RAM НЕ чіпали", size=9.5, color=FIELD, anchor="middle", bold=True))
    ram(rx0 + 90, 258, "X: 5 (застаріле — і хай)", MUTED)
    p.append(text(midx + midx / 2, 322, "A лишається Owned: брудний, але спільний;", size=9, color=INK, anchor="middle"))
    p.append(text(midx + midx / 2, 336, "він відповідальний записати X колись пізніше", size=9, color=INK, anchor="middle"))
    p.append(fitbox(rx0, 354, 308, 40, "Виграш: жодного write-back,\nщоб поділитися брудною лінією",
                    size=10, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    render(os.path.join(OUT, "owned.svg"), W, H, *p,
           title="Заради чого стан Owned: не писати в RAM щоб поділитися брудним")


# ── family: родовід протоколів — кожен стан гасить свій різновид зайвих дій ─────
# Ідея: MSI → MESI → MOESI, і окрема гілка MESIF. Показати НЕ просто ланцюг, а
# ЩО САМЕ кожен доданий стан прибирає: E — зайвий invalidate на «читаю сам, тоді
# пишу»; O — зайвий write-back на «ділюся брудним»; F — зайву відповідь, коли
# копію мають кілька (один призначений відповідач).

def fig_family():
    W, H = 760, 430
    p = []

    bw, bh = 150, 66
    row_y = 130
    def node(cx, letters, sub, col, fill):
        p.append(rect(cx - bw / 2, row_y - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.9))
        p.append(text(cx, row_y - 12, letters, size=15, color=INK, bold=True))
        p.append(text(cx, row_y + 10, sub, size=9, color=MUTED))

    xs = [130, 340, 560]
    node(xs[0], "M S I", "3 стани — база", MUTED, "#f0f1f3")
    node(xs[1], "M E S I", "+ Exclusive", FIELD, "#eafaf0")
    node(xs[2], "M O E S I", "+ Owned", POS, "#fdecea")
    p.append(arrow(xs[0] + bw / 2, row_y, xs[1] - bw / 2, row_y, color=INK, sw=1.9))
    p.append(arrow(xs[1] + bw / 2, row_y, xs[2] - bw / 2, row_y, color=INK, sw=1.9))

    # що прибирає кожен доданий стан — картки під стрілками
    def gain(cx, title, body, col):
        y = row_y + bh / 2 + 26
        p.append(fitbox(cx - 118, y, 236, 58, body, size=9, fill="#ffffff", stroke=col, color=INK))
        p.append(text(cx, y - 6, title, size=9.5, color=col, anchor="middle", bold=True))

    gain((xs[0] + xs[1]) / 2, "E прибирає:",
         "зайвий invalidate, коли ядро\nсамо читало лінію, тоді пише —\nперший запис стає тихим", FIELD)
    gain((xs[1] + xs[2]) / 2, "O прибирає:",
         "зайвий write-back у RAM,\nщоб поділитися брудною лінією —\nвласник віддає її прямо з кеша", POS)

    # окрема гілка MESIF від MESI
    fx, fy = 340, 340
    p.append(rect(fx - bw / 2, fy - bh / 2, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.9))
    p.append(text(fx, fy - 12, "M E S I F", size=15, color=INK, bold=True))
    p.append(text(fx, fy + 10, "+ Forward", size=9, color=MUTED))
    p.append(arrow(xs[1], row_y + bh / 2, fx, fy - bh / 2, color=NEG, sw=1.8))
    p.append(fitbox(fx + bw / 2 + 20, fy - 34, 250, 68,
                    "F прибирає зайву відповідь: коли\nкопію мають кілька ядер, лишень\nОДИН (у стані Forward) віддає її\nтому, хто просить — не всі разом",
                    size=9, fill="#ffffff", stroke=NEG, color=INK))

    p.append(text(W / 2, H - 18, "спільна логіка одна — кожен зайвий стан лише гасить свій різновид непотрібної роботи на шині",
                  size=9.5, color=MUTED, anchor="middle", italic=True))

    render(os.path.join(OUT, "family.svg"), W, H, *p,
           title="Родовід: MSI → MESI → MOESI, і гілка MESIF")


if __name__ == "__main__":
    fig_machine()
    fig_msi()
    fig_owned()
    fig_family()
    print("figs: готово")
