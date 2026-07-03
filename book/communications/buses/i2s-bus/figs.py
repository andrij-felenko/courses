# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Помічник: цифровий сигнал (0/1) із заданих сегментів ──────────────────────
# segs — список (тривалість, рівень 0|1). Малює прямокутну хвилю на осі y_hi/y_lo.
def wave(x0, y_hi, y_lo, unit, segs, color=INK, sw=2.2):
    out, x, prev = [], x0, None
    for dur, lvl in segs:
        y = y_hi if lvl else y_lo
        if prev is not None and prev != lvl:               # вертикальний фронт
            out.append(line(x, y_hi, x, y_lo, color=color, sw=sw))
        out.append(line(x, y, x + dur * unit, y, color=color, sw=sw))
        x += dur * unit
        prev = lvl
    return "".join(out), x


# ── lines: три лінії I2S і хто ними керує ─────────────────────────────────────
# Ідея: передавач і приймач; ведучий (будь-хто з них) жене SCK і WS, дані SD
# течуть від передавача до приймача. Показуємо, що такт і кадр — від ведучого.
def fig_lines():
    W, H = 700, 330
    p = []
    tx, ty, bw, bh = 66, 100, 156, 150
    rx = W - 66 - bw
    p.append(rect(tx, ty, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(tx + bw / 2, ty + 26, "ПЕРЕДАВАЧ", size=14, color=FIELD, bold=True))
    p.append(text(tx + bw / 2, ty + 44, "(джерело звуку)", size=10, color=MUTED, italic=True))
    p.append(rect(rx, ty, bw, bh, fill=FILL, stroke=INK, sw=2))
    p.append(text(rx + bw / 2, ty + 26, "ПРИЙМАЧ", size=14, color=INK, bold=True))
    p.append(text(rx + bw / 2, ty + 44, "(ЦАП, кодек)", size=10, color=MUTED, italic=True))

    rows = [
        ("SCK", "такт біта (bit clock)", ty + 80, NEG, 1),
        ("WS",  "вибір слова: 0 = лівий, 1 = правий", ty + 108, POS, 1),
        ("SD",  "самі відліки звуку", ty + 136, FIELD, 1),
    ]
    for name, role, ly, col, direction in rows:
        p.append(arrow(tx + bw, ly, rx, ly, color=col, sw=2))
        p.append(text(W / 2, ly - 6, name, size=12, color=col, bold=True))
        p.append(text(W / 2, ly + 14, role, size=9, color=MUTED, italic=True))

    p.append(text(W / 2, H - 42, "SCK і WS дає ВЕДУЧИЙ (тут — передавач); SD несе дані до приймача",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, H - 22, "ведучим може бути й приймач — тоді такт і кадр жене він, а SD усе одно від джерела",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "lines.svg"), W, H, *p,
           title="Три лінії I2S: такт, вибір слова, дані")


# ── frame: один кадр — ліве слово, тоді праве ─────────────────────────────────
# Ідея: WS — меандр із частотою відліків; поки WS=0 йде лівий канал, WS=1 — правий.
# SD несе слова старшим бітом уперед. Ключове: MSB стартує на ОДИН такт ПІСЛЯ фронту WS.
def fig_frame():
    W, H = 700, 300
    p = []
    x0, u = 80, 30
    y_scl_hi, y_scl_lo = 70, 92
    y_ws_hi, y_ws_lo = 128, 158
    y_sd_hi, y_sd_lo = 196, 226

    p.append(text(56, 82, "SCK", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(56, 146, "WS", size=12, color=POS, anchor="end", bold=True))
    p.append(text(56, 214, "SD", size=12, color=FIELD, anchor="end", bold=True))

    # SCK: 16 напівперіодів = 8 тактів у видимій частині
    scl_segs = []
    for i in range(16):
        scl_segs.append((0.5, 1 if i % 2 == 0 else 0))
    f, xend = wave(x0, y_scl_hi, y_scl_lo, u, scl_segs, color=NEG, sw=1.8)
    p.append(f)

    # WS: перші 4 такти низько (лівий), далі 4 такти високо (правий)
    ws_segs = [(4, 0), (4, 1)]
    f, _ = wave(x0, y_ws_hi, y_ws_lo, u, ws_segs, color=POS, sw=2.2)
    p.append(f)
    p.append(text(x0 + 2 * u, y_ws_lo + 18, "ЛІВИЙ канал", size=10, color=POS, bold=True))
    p.append(text(x0 + 6 * u, y_ws_hi - 8, "ПРАВИЙ канал", size=10, color=POS, bold=True))

    # SD: слово = MSB … LSB, але зсунуте на 1 такт праворуч від фронту WS.
    # лівий MSB стартує через 1 такт після падіння WS (тут WS падає на x0).
    def word(xstart, labels, col):
        out = []
        for i, lab in enumerate(labels):
            bx = xstart + i * u
            out.append(rect(bx, y_sd_hi, u, y_sd_lo - y_sd_hi, fill="#eef6ef", stroke=col, sw=1.3, rx=0))
            out.append(text(bx + u / 2, (y_sd_hi + y_sd_lo) / 2 + 4, lab, size=9, color=col, bold=(lab in ("MSB", "LSB"))))
        return out
    p += word(x0 + 1 * u, ["MSB", "·", "·", "LSB"], POS)     # лівий: зсув на 1 такт
    p += word(x0 + 5 * u, ["MSB", "·", "·", "LSB"], INK)      # правий: так само зсунуто
    # порожній перший такт (дані ще від попереднього слова) — позначка
    p.append(text(x0 + 0.5 * u, (y_sd_hi + y_sd_lo) / 2 + 4, "×", size=11, color=MUTED, bold=True))

    # стрілка «1 такт затримки» від фронту WS до MSB
    p.append(line(x0, y_ws_lo, x0, y_sd_lo + 22, color=MUTED, sw=1, dash="3 3"))
    p.append(line(x0 + u, y_sd_hi, x0 + u, y_sd_lo + 22, color=MUTED, sw=1, dash="3 3"))
    p.append(arrow(x0, y_sd_lo + 16, x0 + u, y_sd_lo + 16, color=NEG, sw=1.6))
    p.append(text(x0 + u / 2, y_sd_lo + 34, "1 такт", size=9, color=NEG, bold=True))

    p.append(text(W / 2, H - 12, "WS = частота відліків; слово йде старшим бітом уперед, MSB — через ОДИН такт після фронту WS",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "frame.svg"), W, H, *p,
           title="Кадр I2S: ліве слово, тоді праве")


# ── ws-timing: чому MSB зсунуто на один такт ──────────────────────────────────
# Ідея: WS міняється на ОДИН такт РАНІШЕ від першого біта нового слова. Цей проміжок —
# сигнал приймачу «попереднє слово закінчилось»: він засуває його й готує вхід. Тому
# ні передавачу, ні приймачу не треба знати довжину слова наперед.
def fig_ws_timing():
    W, H = 700, 300
    p = []
    x0, u = 90, 46
    y_ws_hi, y_ws_lo = 80, 116
    y_sd_hi, y_sd_lo = 176, 214

    p.append(text(66, 102, "WS", size=12, color=POS, anchor="end", bold=True))
    p.append(text(66, 200, "SD", size=12, color=FIELD, anchor="end", bold=True))

    # WS падає в точці fall (кінець правого слова → початок лівого)
    fall = x0 + 1 * u
    f, _ = wave(x0, y_ws_hi, y_ws_lo, u, [(1, 1), (5, 0)], color=POS, sw=2.4)
    p.append(f)
    p.append(text(x0 + 0.5 * u, y_ws_hi - 10, "правий", size=9, color=POS))
    p.append(text(x0 + 3.5 * u, y_ws_lo + 18, "лівий (новий)", size=9, color=POS, bold=True))

    # SD: останній біт (LSB) старого слова, тоді ПРОМІЖОК, тоді MSB нового
    p.append(rect(x0, y_sd_hi, u, y_sd_lo - y_sd_hi, fill=BG, stroke=MUTED, sw=1.3, rx=0))
    p.append(text(x0 + u / 2, (y_sd_hi + y_sd_lo) / 2 + 4, "LSB старого", size=8.5, color=MUTED))
    # проміжок між fall(WS) і початком MSB — один такт
    p.append(rect(fall, y_sd_hi, u, y_sd_lo - y_sd_hi, fill="#fdf2f2", stroke=POS, sw=1.2, rx=0, ))
    p.append(text(fall + u / 2, (y_sd_hi + y_sd_lo) / 2 + 4, "проміжок", size=8.5, color=POS, bold=True))
    for i, lab in enumerate(["MSB", "·", "·"]):
        bx = fall + (i + 1) * u
        p.append(rect(bx, y_sd_hi, u, y_sd_lo - y_sd_hi, fill="#eef6ef", stroke=FIELD, sw=1.3, rx=0))
        p.append(text(bx + u / 2, (y_sd_hi + y_sd_lo) / 2 + 4, lab, size=9, color=FIELD, bold=(lab == "MSB")))

    # вертикалі, що зв'язують фронт WS і початок MSB
    p.append(line(fall, y_ws_lo, fall, y_sd_lo + 20, color=NEG, sw=1, dash="3 3"))
    p.append(line(fall + u, y_sd_hi, fall + u, y_sd_lo + 20, color=NEG, sw=1, dash="3 3"))
    p.append(arrow(fall, y_sd_lo + 14, fall + u, y_sd_lo + 14, color=NEG, sw=1.6))
    p.append(text(fall + u / 2, y_sd_lo + 34, "рівно 1 такт", size=9, color=NEG, bold=True))

    b, bw2, bh2 = textbox(W / 2, H - 40, "фронт WS на такт раніше за MSB → приймач засуває старе слово\nй готує вхід; довжину слова знати наперед НЕ треба",
                          size=10, fill="#eef6ef", stroke=FIELD, sw=1.4, color=INK)
    p.append(b)
    render(os.path.join(OUT, "ws-timing.svg"), W, H, *p,
           title="Один такт затримки: сигнал «слово закінчилось»")


# ── clocks: ієрархія тактів MCLK → SCK → WS ───────────────────────────────────
# Ідея: три вкладені частоти. WS = fs (частота відліків). SCK = fs × біт × канали.
# MCLK (256·fs) — не частина стандарту, потрібен ЦАП/АЦП для внутрішньої роботи.
def fig_clocks():
    W, H = 700, 330
    p = []
    x0, u = 90, 4.6
    y0 = 80
    # WS: 1 період на всю ширину = 1 відлік (стерео-пара)
    yb = y0
    f, _ = wave(x0, yb, yb + 26, u * 32, [(0.5, 0), (0.5, 1)], color=POS, sw=2.2)
    p.append(f)
    p.append(text(66, yb + 20, "WS", size=12, color=POS, anchor="end", bold=True))
    p.append(text(x0 + 32 * u + 14, yb + 18, "= fs (частота відліків)", size=10, color=POS, anchor="start", bold=True))

    # SCK: 32 такти на кадр (16 біт × 2 канали)
    yb = y0 + 66
    segs = [(0.5, 1 if i % 2 == 0 else 0) for i in range(64)]
    f, _ = wave(x0, yb, yb + 26, u, segs, color=NEG, sw=1.3)
    p.append(f)
    p.append(text(66, yb + 20, "SCK", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(x0 + 64 * 0.5 * u + 14, yb + 18, "= fs × 16 біт × 2 канали", size=10, color=NEG, anchor="start", bold=True))

    # MCLK: густа гребінка (символічно 256·fs) — просто дуже часта хвиля
    yb = y0 + 132
    p.append(rect(x0, yb, 64 * 0.5 * u, 26, fill="#f0f0f0", stroke=MUTED, sw=1.2, rx=0))
    for i in range(0, int(64 * 0.5 * u), 4):
        p.append(line(x0 + i, yb, x0 + i, yb + 26, color=MUTED, sw=0.6))
    p.append(text(66, yb + 20, "MCLK", size=12, color=MUTED, anchor="end", bold=True))
    p.append(text(x0 + 64 * 0.5 * u + 14, yb + 18, "≈ 256 × fs (поза стандартом)", size=10, color=MUTED, anchor="start", bold=True))

    # числовий приклад
    b, _, _ = textbox(W / 2, y0 + 210,
                      "приклад: fs = 48 кГц, 16 біт, стерео\nWS = 48 кГц · SCK = 48000·16·2 = 1.536 МГц · MCLK = 256·48000 = 12.288 МГц",
                      size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.4, color=INK)
    p.append(b)
    render(os.path.join(OUT, "clocks.svg"), W, H, *p,
           title="Три частоти I2S: WS, SCK, MCLK")


# ── variants: I2S проти ліво- і правовирівняного ──────────────────────────────
# Ідея: та сама WS, але момент MSB різний. I2S — MSB через 1 такт після фронту.
# Left-justified — MSB одразу з фронтом. Right-justified — LSB притиснутий до кінця слова.
def fig_variants():
    W, H = 700, 320
    p = []
    x0, u = 92, 30
    slot = 8  # тактів на канал у видимій частині
    y_ws_hi, y_ws_lo = 66, 92

    p.append(text(70, 84, "WS", size=11, color=POS, anchor="end", bold=True))
    f, _ = wave(x0, y_ws_hi, y_ws_lo, u, [(slot, 0), (slot, 1)], color=POS, sw=2)
    p.append(f)

    def dataline(y, label, start_off, nbits, col, tail=False):
        out = [text(70, y + 20, label, size=10, color=col, anchor="end", bold=True)]
        # порожні такти-заповнювачі до слова
        for i in range(start_off):
            bx = x0 + i * u
            out.append(rect(bx, y, u, 26, fill=BG, stroke="#dddddd", sw=1, rx=0))
        for i in range(nbits):
            bx = x0 + (start_off + i) * u
            lab = "MSB" if i == 0 else ("LSB" if i == nbits - 1 else "·")
            out.append(rect(bx, y, u, 26, fill="#eef6ef", stroke=col, sw=1.2, rx=0))
            out.append(text(bx + u / 2, y + 17, lab, size=8.5, color=col, bold=(i == 0 or i == nbits - 1)))
        return out

    nb = 6
    p += dataline(120, "I2S", 1, nb, FIELD)                 # MSB через 1 такт
    p.append(text(x0 + slot * u + 8, 120 + 17, "MSB на такт ПІЗНІШЕ фронту", size=9, color=FIELD, anchor="start"))
    p += dataline(170, "ліво-\nвирівняний", 0, nb, NEG)     # MSB одразу
    p.append(text(x0 + slot * u + 8, 170 + 17, "MSB ОДРАЗУ з фронтом", size=9, color=NEG, anchor="start"))
    p += dataline(220, "право-\nвирівняний", slot - nb, nb, POS)  # LSB у кінець слота
    p.append(text(x0 + slot * u + 8, 220 + 17, "LSB притиснутий до КІНЦЯ слова", size=9, color=POS, anchor="start"))

    # мітка фронту WS
    p.append(line(x0, y_ws_lo, x0, 246, color=MUTED, sw=1, dash="3 3"))
    p.append(line(x0 + slot * u, y_ws_hi, x0 + slot * u, 246, color=MUTED, sw=1, dash="3 3"))

    p.append(text(W / 2, H - 30, "усі троє мають однакову WS — різниться лише де в слоті лежить слово",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, H - 12, "переплутати формат = зсув на біт → шум замість музики; тому вирівнювання узгоджують у налаштуванні",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "variants.svg"), W, H, *p,
           title="I2S проти ліво- й правовирівняного формату")


# ── history: чому знадобилась звукова шина — ланцюг чіпів у CD-програвачі ──────
# Ідея: у CD-програвачі початку 1980-х цифровий звук іде крізь низку окремих
# мікросхем. Кожен стик між ними — місце, де треба ганяти рівний потік
# стереовідліків. Саме ця «фабрика» на платі й породила потребу в спільній
# звуковій лінії — щоб стики були однакові в чіпів різних виробників.
def fig_history_chain():
    W, H = 720, 340
    p = []

    p.append(text(W / 2, 52, "Цифровий звук на платі CD-програвача (початок 1980-х):",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 72, "потік стереовідліків проходить крізь ланцюг окремих чіпів",
                  size=11, color=MUTED, italic=True))

    boxes = [
        ("лазер +\nсерво", "сирі біти\nз диска", MUTED, "#f4f6f8"),
        ("декодер\nEFM · CIRC", "виправлення\nпомилок", NEG, "#eaf0fd"),
        ("цифровий\nфільтр", "4× пере-\nдискретизація", FIELD, "#eef6ef"),
        ("ЦАП\n(на канал)", "число →\nнапруга", POS, "#fdecea"),
    ]
    bw, bh, gap = 130, 84, 28
    total = len(boxes) * bw + (len(boxes) - 1) * gap
    x = (W - total) / 2
    y = 108
    centers = []
    for i, (title, sub, col, fill) in enumerate(boxes):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(mtext(x + bw / 2, y + 26, title, size=12, color=col, bold=True, lh=1.15))
        p.append(mtext(x + bw / 2, y + 58, sub, size=9.5, color=MUTED, lh=1.1))
        centers.append(x + bw / 2)
        if i < len(boxes) - 1:
            p.append(arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, color=INK, sw=2))
        x += bw + gap

    # підкреслити стики — саме тут потрібна спільна звукова лінія
    yb = y + bh + 30
    for i in range(len(boxes) - 1):
        sx = (centers[i] + centers[i + 1]) / 2
        p.append(line(sx, y + bh + 4, sx, yb, color=FIELD, sw=1.4, dash="3 3"))
        p.append(circle(sx, yb, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(W / 2, yb + 24,
                  "кожен стик — рівний потік стереовідліків між двома чіпами",
                  size=11, color=FIELD, bold=True))
    p.append(text(W / 2, yb + 44,
                  "три лінії SCK · WS · SD зробили ці стики однаковими для чіпів різних виробників",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "history-chain.svg"), W, H, *p,
           title="Навіщо окрема звукова шина")


# ── tx-formats: три формати слова у слоті (для proj-вставки) ──────────────────
# Ідея: та сама WS, різне місце слова. Philips — MSB через 1 такт; left-justified —
# MSB одразу; right-justified — LSB у кінці слота. Один такт зсуву = шум.
def fig_tx_formats():
    W, H = 700, 300
    p = []
    x0, u = 96, 30
    slot = 8
    y_ws_hi, y_ws_lo = 62, 88

    p.append(text(74, 80, "WS", size=11, color=POS, anchor="end", bold=True))
    f, _ = wave(x0, y_ws_hi, y_ws_lo, u, [(slot, 0), (slot, 1)], color=POS, sw=2)
    p.append(f)
    p.append(text(x0 + 2 * u, y_ws_lo + 16, "лівий канал", size=9, color=POS))

    def dataline(y, label, start_off, nbits, col, note):
        out = [mtext(76, y + 8, label, size=9.5, color=col, anchor="end", bold=True)]
        for i in range(start_off):
            bx = x0 + i * u
            out.append(rect(bx, y, u, 26, fill=BG, stroke="#dddddd", sw=1, rx=0))
        for i in range(nbits):
            bx = x0 + (start_off + i) * u
            lab = "MSB" if i == 0 else ("LSB" if i == nbits - 1 else "·")
            out.append(rect(bx, y, u, 26, fill="#eef6ef", stroke=col, sw=1.2, rx=0))
            out.append(text(bx + u / 2, y + 17, lab, size=8.5, color=col,
                            bold=(i == 0 or i == nbits - 1)))
        out.append(text(x0 + slot * u + 10, y + 17, note, size=9, color=col, anchor="start"))
        return out

    nb = 6
    p += dataline(116, "Philips\nI2S", 1, nb, FIELD, "MSB через 1 такт після WS")
    p += dataline(166, "left-\njustified", 0, nb, NEG, "MSB одразу з фронтом")
    p += dataline(216, "right-\njustified", slot - nb, nb, POS, "LSB у кінці слота")

    p.append(line(x0, y_ws_lo, x0, 244, color=MUTED, sw=1, dash="3 3"))
    p.append(line(x0 + slot * u, y_ws_hi, x0 + slot * u, 244, color=MUTED, sw=1, dash="3 3"))
    p.append(text(W / 2, H - 12,
                  "переплутати формат = зсув на один такт → приймач бере біти не так → шум",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "tx-formats.svg"), W, H, *p,
           title="Три формати слова: Philips / left / right")


# ── tx-pingpong: подвійна буферизація TX через DMA ────────────────────────────
# Ідея: DMA ллє один буфер у периферію, CPU наповнює другий; на межі ролі
# міняються без паузи. Поки CPU устигає — у звуці немає діри.
def fig_tx_pingpong():
    W, H = 700, 340
    p = []
    cx, cy, cw, ch = 40, 120, 120, 96
    p.append(rect(cx, cy, cw, ch, fill=FILL, stroke=INK, sw=2))
    p.append(text(cx + cw / 2, cy + 34, "ПРОЦЕСОР", size=13, color=INK, bold=True))
    p.append(text(cx + cw / 2, cy + 54, "наповнює", size=10, color=MUTED, italic=True))
    p.append(text(cx + cw / 2, cy + 70, "ривками", size=10, color=MUTED, italic=True))

    px, py, pw, ph = W - 40 - 130, 120, 130, 96
    p.append(rect(px, py, pw, ph, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(px + pw / 2, py + 30, "I2S + DMA", size=13, color=FIELD, bold=True))
    p.append(text(px + pw / 2, py + 50, "→ ЦАП", size=12, color=FIELD, bold=True))
    p.append(text(px + pw / 2, py + 70, "ллє рівномірно", size=10, color=MUTED, italic=True))

    bx, bw, bh = 250, 200, 44
    ya, yb = 96, 176
    p.append(rect(bx, ya, bw, bh, fill="#fdf2f2", stroke=POS, sw=2))
    p.append(text(bx + bw / 2, ya + 20, "БУФЕР A", size=12, color=POS, bold=True))
    p.append(text(bx + bw / 2, ya + 37, "DMA ллє його → ЦАП", size=9.5, color=POS))
    p.append(rect(bx, yb, bw, bh, fill="#eef2fd", stroke=NEG, sw=2))
    p.append(text(bx + bw / 2, yb + 20, "БУФЕР B", size=12, color=NEG, bold=True))
    p.append(text(bx + bw / 2, yb + 37, "CPU наповнює наперед", size=9.5, color=NEG))

    p.append(arrow(cx + cw, cy + 20, bx, yb + bh / 2, color=NEG, sw=2))
    p.append(arrow(bx + bw, ya + bh / 2, px, py + 30, color=POS, sw=2))

    p.append(arrow(bx + bw / 2 - 30, ya + bh, bx + bw / 2 - 30, yb, color=MUTED, sw=1.6))
    p.append(arrow(bx + bw / 2 + 30, yb, bx + bw / 2 + 30, ya + bh, color=MUTED, sw=1.6))
    p.append(text(bx + bw / 2, (ya + bh + yb) / 2 + 4, "на межі — обмін ролями",
                  size=9, color=MUTED, italic=True))

    b, _, _ = textbox(W / 2, H - 34,
                      "поки DMA спорожнює один буфер, CPU наповнює інший;\n"
                      "устигає наповнити швидше, ніж DMA спорожнює → у звуці НЕМАЄ діри",
                      size=10.5, fill=FILL, stroke=INK, sw=1.4, color=INK)
    p.append(b)
    render(os.path.join(OUT, "tx-pingpong.svg"), W, H, *p,
           title="Подвійна буферизація: DMA ллє, CPU наповнює")


if __name__ == "__main__":
    fig_lines()
    fig_frame()
    fig_ws_timing()
    fig_clocks()
    fig_variants()
    fig_history_chain()
    fig_tx_formats()
    fig_tx_pingpong()
    print("OK: figures written to", OUT)
