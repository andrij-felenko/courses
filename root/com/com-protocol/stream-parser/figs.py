# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── blocking: блокуючий проти неблокуючого прийому ────────────────────────────
# Ідея: угорі цикл очікування забирає весь процесор, решта задач стоїть;
# унизу — один крок на наявний байт і миттєве повернення керування.

def fig_blocking():
    W, H = 720, 320
    p = []
    lane_x, lane_w = 60, 600

    # ── блокуючий (угорі) ──
    yb = 78
    p.append(text(lane_x, yb - 26, "Блокуючий: while(!available());", size=13,
                  color=POS, anchor="start", bold=True))
    p.append(rect(lane_x, yb, lane_w * 0.72, 40, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(lane_x + lane_w * 0.36, yb + 24,
                  "цикл очікування байта — процесор зайнятий ТІЛЬКИ цим", size=11, color=POS))
    # затиснуті задачі праворуч
    bx = lane_x + lane_w * 0.72 + 12
    for lab in ("ПІД", "дисплей"):
        b = fitbox(bx, yb, 80, 40, lab + "\n(стоїть)", size=10, fill="#f0f0f0",
                   stroke=MUTED, sw=1.3, color=MUTED)
        p.append(b)
        bx += 92
    p.append(text(lane_x, yb + 70, "поки байт не прийде — усі інші задачі заморожені",
                  size=10, color=MUTED, anchor="start", italic=True))

    # ── неблокуючий (унизу) ──
    yn = 210
    p.append(text(lane_x, yn - 26, "Неблокуючий: if(available()) feed(read());",
                  size=13, color=FIELD, anchor="start", bold=True))
    segs = [("feed\nбайта", FIELD, "#eafaf0"), ("ПІД", INK, BG),
            ("дисплей", INK, BG), ("телеметрія", INK, BG)]
    sx = lane_x
    sw = (lane_w) / len(segs) - 10
    centers = []
    for i, (lab, col, fill) in enumerate(segs):
        p.append(fitbox(sx, yn, sw, 40, lab, size=10, fill=fill, stroke=col, sw=1.5, color=col))
        centers.append(sx + sw)
        if i > 0:
            p.append(arrow(centers[i - 1] - sw - 10 + sw + 1, yn + 20, sx - 1, yn + 20,
                           color=INK, sw=1.4))
        sx += sw + 10
    p.append(text(lane_x, yn + 70,
                  "обробляє той байт, що вже є, і одразу віддає керування циклу",
                  size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "blocking.svg"), W, H, *p,
           title="Стояти й чекати проти кроку на наявний байт")


# ── fsm: скінченний автомат прийму пакета (4 стани) ───────────────────────────
# Ідея: чотири стани, кожен байт просуває на один крок; з GET_CRC завжди назад
# у WAIT_SYNC, пунктир — захисний скид при завеликій довжині.

def fig_fsm():
    W, H = 760, 360
    p = []

    states = {
        "WAIT_SYNC": (140, 150, NEG,   "#eaf0fd", "чекаємо SYNC"),
        "GET_LEN":   (380, 150, "#b08900", "#fbf3df", "беремо довжину"),
        "GET_DATA":  (620, 150, INK,   "#eef4ff", "збираємо len байтів"),
        "GET_CRC":   (620, 300, FIELD, "#eafaf0", "звіряємо CRC"),
    }
    box = {}
    for name, (cx, cy, col, fill, sub) in states.items():
        b, w, h = textbox(cx, cy, name, size=13, bold=True, color=col,
                          fill=fill, stroke=col, sw=2, min_w=150, pad=12)
        p.append(b)
        p.append(text(cx, cy + h / 2 + 14, sub, size=10, color=MUTED))
        box[name] = (cx, cy, w, h)

    def edge(a, b, label, color=INK, lift=0):
        ax, ay, aw, ah = box[a]; bx, by, bw, bh = box[b]
        x1 = ax + aw / 2; x2 = bx - bw / 2
        p.append(arrow(x1, ay, x2, by, color=color, sw=1.9))
        p.append(text((x1 + x2) / 2, min(ay, by) - 8 - lift, label, size=11, color=color, bold=True))

    edge("WAIT_SYNC", "GET_LEN", "b == SYNC", NEG)
    edge("GET_LEN", "GET_DATA", "len = b", "#b08900")

    # GET_DATA -> GET_DATA (петля, idx<len)
    cx, cy, w, h = box["GET_DATA"]
    p.append('<path d="M %.0f,%.0f C %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" '
             'stroke="%s" stroke-width="1.9" marker-end="url(#arrow)"/>'
             % (cx + 18, cy - h / 2, cx + 18, cy - h / 2 - 42,
                cx + w / 2 + 16, cy - h / 2 - 42, cx + w / 2 + 2, cy - 6, INK))
    p.append(text(cx + w / 2 + 8, cy - h / 2 - 50, "buf[idx++]=b; idx<len",
                  size=10, color=INK, bold=True))

    # GET_DATA -> GET_CRC (вниз)
    p.append(arrow(cx, cy + h / 2, cx, box["GET_CRC"][1] - box["GET_CRC"][3] / 2, color=INK, sw=1.9))
    p.append(text(cx + 60, (cy + box["GET_CRC"][1]) / 2, "idx == len", size=11, color=INK, bold=True))

    # GET_CRC -> WAIT_SYNC (велика дуга назад)
    gx, gy, gw, gh = box["GET_CRC"]; wx, wy, ww, wh = box["WAIT_SYNC"]
    p.append('<path d="M %.0f,%.0f C %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" '
             'stroke="%s" stroke-width="1.9" marker-end="url(#arrow)"/>'
             % (gx - gw / 2, gy, 300, gy + 40, 110, gy + 10, wx, wy + wh / 2, FIELD))
    p.append(text(360, gy + 48, "звірити CRC; як зійшовся — видати пакет; у будь-якому разі назад",
                  size=10.5, color=FIELD, bold=True))

    # GET_LEN -> WAIT_SYNC (пунктир, захисний скид)
    lx, ly, lw, lh = box["GET_LEN"]
    p.append('<path d="M %.0f,%.0f C %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="none" '
             'stroke="%s" stroke-width="1.7" stroke-dasharray="5 3" marker-end="url(#arrow)"/>'
             % (lx, ly + lh / 2, lx - 40, ly + 90, wx + 60, ly + 90, wx, wy + wh / 2, POS))
    p.append(text(260, ly + 104, "len > MAX → скидання", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "fsm.svg"), W, H, *p,
           title="Скінченний автомат прийому: кожен байт — один крок")


# ── state: стан, що живе між викликами feed() ─────────────────────────────────
# Ідея: жменька змінних переживає виклики; саме вона дає змогу «пам'ятати»
# половину зібраного пакета, нічого не блокуючи.

def fig_state():
    W, H = 720, 300
    p = []
    cx = W / 2

    # три послідовні виклики feed() як вертикальні мітки часу
    calls_y = 96
    xs = [150, 360, 570]
    p.append(line(90, calls_y, 630, calls_y, color=MUTED, sw=1.4))
    for i, x in enumerate(xs):
        p.append(circle(x, calls_y, 6, fill=BG, stroke=INK, sw=1.6))
        p.append(text(x, calls_y - 14, "feed(b%d)" % (i + 1), size=11, color=INK, bold=True))
        if i < len(xs) - 1:
            p.append(text((x + xs[i + 1]) / 2, calls_y - 12, "…інші задачі…",
                          size=9, color=MUTED, italic=True))

    # коробка збереженого стану під лінією
    bx, by, bw, bh = 150, 150, 420, 96
    p.append(rect(bx, by, bw, bh, fill="#f6f4ec", stroke=INK, sw=2))
    p.append(text(bx + bw / 2, by + 22, "стан, що переживає виклики", size=12, color=INK, bold=True))
    vars_ = [("st", "поточний\nстан"), ("len", "очікувана\nдовжина"),
             ("idx", "скільки\nзібрано"), ("buf[]", "накопичувач"), ("crc", "на льоту")]
    vw = bw / len(vars_)
    for i, (v, sub) in enumerate(vars_):
        vx = bx + i * vw + vw / 2
        p.append(text(vx, by + 50, v, size=12, color=NEG, bold=True))
        p.append(mtext(vx, by + 67, sub, size=9, color=MUTED, lh=1.15))

    # стрілки від кожного виклику до коробки стану
    for x in xs:
        p.append(line(x, calls_y + 6, x if bx <= x <= bx + bw else cx, by - 2,
                      color=MUTED, sw=1.2, dash="4 3"))

    p.append(text(cx, H - 18,
                  "виклик лише оновлює ці змінні й виходить — наступний байт продовжить з того ж місця",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "state.svg"), W, H, *p,
           title="Пам'ять автомата — жменька змінних між викликами")


# ── trace: трасування пакета AA 03 41 42 43 <CRC> байт за байтом ──────────────
# Ідея: шість прийнятих байтів — шість переходів; таблиця байт / стан до / дія /
# стан після.

def fig_trace():
    W, H = 760, 360
    p = []
    cols = [("байт", 70), ("стан до", 180), ("дія", 350), ("стан після", 590)]
    x0, tw = 50, 660
    hy = 70
    p.append(rect(x0, hy, tw, 30, fill="#f0f0f0", stroke=MUTED, sw=1.3, rx=4))
    for lab, cx in cols:
        p.append(text(cx, hy + 20, lab, size=11.5, color=INK, anchor="start", bold=True))

    rows = [
        ("0xAA", NEG,        "WAIT_SYNC", "SYNC знайдено",       "GET_LEN",   NEG),
        ("0x03", "#b08900",  "GET_LEN",   "len=3, idx=0",        "GET_DATA",  "#b08900"),
        ("0x41", INK,        "GET_DATA",  "buf[0], idx=1",       "GET_DATA",  INK),
        ("0x42", INK,        "GET_DATA",  "buf[1], idx=2",       "GET_DATA",  INK),
        ("0x43", INK,        "GET_DATA",  "buf[2], idx=3 = len", "GET_CRC",   INK),
        ("CRC",  FIELD,      "GET_CRC",   "звірка → видати",     "WAIT_SYNC", FIELD),
    ]
    ry = hy + 30
    rh = 34
    for byte, bc, before, act, after, ac in rows:
        p.append(rect(x0, ry, tw, rh, fill=BG, stroke="#cfcfcf", sw=1, rx=0))
        p.append(text(cols[0][1], ry + 22, byte, size=12, color=bc, anchor="start", bold=True))
        p.append(text(cols[1][1], ry + 22, before, size=11, color=INK, anchor="start"))
        p.append(text(cols[2][1], ry + 22, act, size=11, color=INK, anchor="start"))
        p.append(text(cols[3][1], ry + 22, after, size=11, color=ac, anchor="start", bold=True))
        ry += rh

    p.append(rect(x0, ry + 8, tw, 38, fill="#eafaf0", stroke=FIELD, sw=1.3))
    p.append(text(W / 2, ry + 32,
                  "Шість байтів — шість викликів feed(); між ними МК вільний робити будь-що інше.",
                  size=11.5, color=INK, bold=True))

    render(os.path.join(OUT, "trace.svg"), W, H, *p,
           title="Трасування пакета AA 03 41 42 43 <CRC>")


# ── inc-crc: інкрементний CRC — рахуємо на льоту ──────────────────────────────
# Ідея: CRC ініціалізують на довжині й оновлюють кожним байтом даних; коли
# приходить контрольний байт, відповідь уже готова — лишається порівняти.

def fig_inc_crc():
    W, H = 740, 250
    p = []
    y = 120
    step = 150
    x = 60
    nodes = [
        ("LEN", "#b08900", "#fbf3df", "crc = init(len)"),
        ("D0", INK, "#eef4ff", "crc = upd(crc, b)"),
        ("D1", INK, "#eef4ff", "crc = upd(crc, b)"),
        ("D2", INK, "#eef4ff", "crc = upd(crc, b)"),
        ("CRC", FIELD, "#eafaf0", "b == crc ?"),
    ]
    centers = []
    for i, (lab, col, fill, sub) in enumerate(nodes):
        b, w, h = textbox(x, y, lab, size=13, bold=True, color=col, fill=fill,
                          stroke=col, sw=1.8, min_w=70)
        p.append(b)
        p.append(text(x, y + h / 2 + 16, sub, size=9.5, color=MUTED))
        centers.append((x, w))
        if i > 0:
            px, pw = centers[i - 1]
            p.append(arrow(px + pw / 2, y, x - w / 2, y, color=INK, sw=1.7))
        x += step

    p.append(text(W / 2, y - 60, "контрольна сума росте разом з прийомом",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 22,
                  "коли приходить контрольний байт — відповідь уже готова, лишається порівняти",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "inc-crc.svg"), W, H, *p,
           title="Інкрементний CRC: підрахунок іде паралельно з прийомом")


# ── robust: три запобіжники надійного автомата ────────────────────────────────
# Ідея: хай що піде не так, автомат завжди має дорогу назад у WAIT_SYNC;
# три латки — межа довжини, таймаут, ресинхрон за CRC.

def fig_robust():
    W, H = 720, 320
    p = []
    # центр — WAIT_SYNC як «безпечна гавань»
    cx, cy = W / 2, H / 2
    core, cw, ch = textbox(cx, cy, "WAIT_SYNC", size=14, bold=True, color=NEG,
                           fill="#eaf0fd", stroke=NEG, sw=2.2, min_w=170, pad=14)
    p.append(core)
    p.append(text(cx, cy + ch / 2 + 16, "безпечна гавань: завжди є дорога сюди", size=10, color=MUTED))

    guards = [
        (150, 86, "Межа довжини", "len > буфер → скид\n(інакше переповнення)", POS, "#fdecea"),
        (W - 150, 86, "Таймаут", "застрягли надовго → скид\n(загублений байт)", "#b08900", "#fbf3df"),
        (cx, H - 70, "Ресинхрон за CRC", "побитий пакет → відкинути,\nчекати наступний SYNC", FIELD, "#eafaf0"),
    ]
    for gx, gy, title_, body, col, fill in guards:
        b, bw, bh = textbox(gx, gy, title_, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.8, min_w=160)
        p.append(b)
        p.append(mtext(gx, gy + bh / 2 + 16, body, size=9.5, color=MUTED))
        # стрілка до центру
        diry = 1 if gy < cy else -1
        p.append(arrow(gx, gy + diry * bh / 2 + (8 if diry > 0 else -8),
                       cx + (gx - cx) * 0.18, cy - diry * ch / 2, color=col, sw=1.6))

    render(os.path.join(OUT, "robust.svg"), W, H, *p,
           title="Три запобіжники: хай що піде не так — дорога назаду WAIT_SYNC")


# ── integration: автомат у головному циклі ────────────────────────────────────
# Ідея: feed() — лише одна з кооперативних задач у loop(); буфер UART тримає
# байти між обертами, тож жоден не губиться.

def fig_integration():
    W, H = 720, 320
    p = []
    cx, cy = W / 2, 168
    r = 110

    p.append(text(cx, 40, "loop(): кожна задача робить трохи й віддає керування",
                  size=12.5, color=INK, bold=True))

    # коло задач
    tasks = [
        ("UART → feed()", FIELD, "#eafaf0"),
        ("крок ПІД", INK, BG),
        ("дисплей", INK, BG),
        ("телеметрія", INK, BG),
    ]
    import math
    centers = []
    for i, (lab, col, fill) in enumerate(tasks):
        a = -math.pi / 2 + i * 2 * math.pi / len(tasks)
        tx, ty = cx + r * math.cos(a), cy + r * math.sin(a) * 0.78
        b, w, h = textbox(tx, ty, lab, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.6, min_w=120)
        p.append(b)
        centers.append((tx, ty))
    # стрілки по колу
    for i in range(len(centers)):
        x1, y1 = centers[i]
        x2, y2 = centers[(i + 1) % len(centers)]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        p.append(arrow(x1 + (x2 - x1) * 0.28, y1 + (y2 - y1) * 0.28,
                       x1 + (x2 - x1) * 0.72, y1 + (y2 - y1) * 0.72, color=MUTED, sw=1.5))

    # буфер UART збоку
    bx = 40
    p.append(rect(bx, cy - 24, 96, 48, fill="#fdf6e3", stroke="#b08900", sw=1.6))
    p.append(mtext(bx + 48, cy - 4, "буфер UART\nтримає байти", size=9.5, color="#8a6d00"))
    fx, fy = centers[0]
    p.append(arrow(bx + 96, cy, fx - 60, fy, color="#b08900", sw=1.5))

    p.append(text(cx, H - 18,
                  "буфер тримає байти між обертами циклу — жоден не губиться, навіть якщо feed() не миттєвий",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "integration.svg"), W, H, *p,
           title="feed() — одна з кооперативних задач головного циклу")


if __name__ == "__main__":
    fig_blocking()
    fig_fsm()
    fig_state()
    fig_trace()
    fig_inc_crc()
    fig_robust()
    fig_integration()
    print("OK: figures written to", OUT)
