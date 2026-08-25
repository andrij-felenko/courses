# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── idea: словник будується з потоку, у файл ідуть лише номери ─────────────────
# Ідея: показати головну дивовижу LZW — словник НЕ передається. Кодувальник
# нарощує таблицю з тих самих байтів, що вже пройшли; у файл летять лише короткі
# номери. Декодер відбудує ту саму таблицю з тих самих байтів.

def fig_idea():
    W, H = 720, 300
    p = []

    # вхідний потік
    p.append(text(40, 60, "вхідний потік байтів", size=12, color=MUTED, anchor="start"))
    seq = "ABABABA"
    cell = 30
    x0 = 40
    for i, ch in enumerate(seq):
        p.append(rect(x0 + i * cell, 72, cell, cell, fill="#eef4ff", stroke=INK, sw=1))
        p.append(text(x0 + i * cell + cell / 2, 72 + cell / 2 + 5, ch, size=13, color=INK, bold=True))

    # словник росте збоку — кадри
    bx, by = 360, 56
    b, bw, bh = textbox(bx + 120, by + 60, "словник, що РОСТЕ\nз уже прочитаного:\n2→AB  3→BA  4→ABA",
                        size=11.5, bold=False, fill="#f6f4ec", stroke=FIELD, sw=1.6, color=INK)
    p.append(b)
    p.append(text(bx + 120, by + 60 - bh / 2 - 8, "будується на льоту, у файл НЕ йде", size=10, color=FIELD, bold=True))

    # стрілка вниз — у файл лише номери
    p.append(arrow(W / 2, 130, W / 2, 168, color=INK, sw=1.8))

    # вихід — самі номери
    yo = 200
    p.append(text(40, yo - 12, "у файл — лише номери (словник не передається):", size=12, color=NEG, anchor="start", bold=True))
    codes = ["0", "1", "2", "4"]
    xp = 40
    for c in codes:
        cb, cbw, cbh = textbox(xp + 24, yo + 24, c, size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG, min_w=46)
        p.append(cb)
        xp += cbw + 16
    p.append(text(xp + 6, yo + 28, "→ декодер відтворить той самий словник сам", size=10.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "idea.svg"), W, H, *p,
           title="Душа LZW: словник росте з даних, а не передається")


# ── encode: покрокова трасу кодування ABABABA ─────────────────────────────────
# Ідея: показати правило «нарощуй W, поки W+c у словнику; не влізло — видай код W
# і додай W+c». Видно, як рядки в словнику довшають, а кодів меншає, ніж байтів.

def fig_encode():
    W, H = 720, 410
    p = []
    rows = [
        # (W перед, c, дія, що видали, що додали)
        ("—", "A", "A є → тримаємо", "",        ""),
        ("A", "B", "AB нема → видай 0, додай AB", "0 (A)", "2 = AB"),
        ("B", "A", "BA нема → видай 1, додай BA", "1 (B)", "3 = BA"),
        ("A", "B", "AB є → тримаємо AB",        "",        ""),
        ("AB", "A", "ABA нема → видай 2, додай ABA", "2 (AB)", "4 = ABA"),
        ("A", "—", "кінець → видай 4",        "4 (ABA)", ""),
    ]
    # заголовки колонок
    cols = [("W", 70), ("вхід c", 150), ("дія", 240), ("видано", 470), ("додано в словник", 600)]
    yh = 58
    for name, x in cols:
        p.append(text(x, yh, name, size=11, color=MUTED, bold=True))
    p.append(line(40, yh + 8, W - 30, yh + 8, color=MUTED, sw=1))

    y = yh + 34
    dy = 48
    for (w, c, act, emit, add) in rows:
        p.append(text(70, y, w, size=12.5, color=INK, bold=True))
        p.append(text(150, y, c, size=12.5, color=INK, bold=True))
        p.append(text(240, y, act, size=11, color=INK, anchor="start"))
        if emit:
            eb, ebw, ebh = textbox(470 + 14, y - 4, emit, size=11, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.3, color=NEG)
            p.append(eb)
        if add:
            ab, abw, abh = textbox(600 + 24, y - 4, add, size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.3, color=FIELD)
            p.append(ab)
        y += dy

    p.append(line(40, y - 16, W - 30, y - 16, color=MUTED, sw=1, dash="3 3"))
    p.append(text(W / 2, y + 6, "7 байтів входу → 4 коди виходу; словник AB, BA, ABA з'явився сам",
                  size=11.5, color=POS, italic=True, bold=True))

    render(os.path.join(OUT, "encode.svg"), W, H, *p,
           title="Кодування ABABABA: нарощуй збіг, видай код, додай продовження")


# ── mirror: декодер відбудовує ТОЙ САМИЙ словник без передачі ──────────────────
# Ідея: дві колонки поруч — кодувальник і декодер. Однакові рядки словника
# з'являються по обидва боки в тому самому порядку, хоча між ними йдуть лише
# номери. Це доказ, що передавати словник не треба.

def fig_mirror():
    W, H = 740, 330
    p = []
    # дві панелі
    p.append(rect(40, 56, 300, 240, fill="#f6f8fa", stroke=NEG, sw=1.6))
    p.append(rect(400, 56, 300, 240, fill="#f6f8fa", stroke=FIELD, sw=1.6))
    p.append(text(190, 78, "КОДУВАЛЬНИК", size=12, color=NEG, bold=True))
    p.append(text(550, 78, "ДЕКОДЕР", size=12, color=FIELD, bold=True))

    enc = ["бачить A·B → додає  2 = AB",
           "бачить B·A → додає  3 = BA",
           "бачить AB·A → додає 4 = ABA"]
    dec = ["прийняв 1 → додає  2 = AB",
           "прийняв 2 → додає  3 = BA",
           "прийняв 4 → додає  4 = ABA"]
    y = 108
    for e, d in zip(enc, dec):
        p.append(text(58, y, e, size=10.5, color=INK, anchor="start"))
        p.append(text(418, y, d, size=10.5, color=INK, anchor="start"))
        y += 30

    # потік номерів посередині
    p.append(text(W / 2, 210, "0  1  2  4", size=15, color=INK, bold=True))
    p.append(text(W / 2, 230, "лише номери в каналі", size=10, color=MUTED, italic=True))
    p.append(arrow(345, 200, 398, 200, color=MUTED, sw=1.4))

    p.append(text(W / 2, 282,
                  "однаковий словник по обидва боки — а в каналі жодного рядка таблиці",
                  size=11, color=POS, italic=True, bold=True))
    render(os.path.join(OUT, "mirror.svg"), W, H, *p,
           title="Декодер відтворює той самий словник синхронно")


# ── kwkwk: пастка «декодер на крок позаду» ────────────────────────────────────
# Ідея: показати єдиний особливий випадок. На кроці, де кодувальник видає код 4,
# декодер цей код 4 саме ЗАРАЗ створює — у його таблиці його ще нема. Виверт:
# відома послідовність = попередній рядок + його ж перший символ.

def fig_kwkwk():
    W, H = 740, 320
    p = []
    # ліворуч — момент кодувальника
    bl, bwl, bhl = textbox(195, 110, "кодувальник видає код 4\nі В ТУ Ж МИТЬ додає\n4 = ABA",
                           size=11.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.7, color=NEG)
    p.append(bl)
    # праворуч — біда декодера
    br, bwr, bhr = textbox(545, 110, "декодер читає код 4,\nа в його таблиці\nкоду 4 ЩЕ НЕМА",
                           size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.7, color=POS)
    p.append(br)
    p.append(arrow(305, 110, 425, 110, color=MUTED, sw=1.6))
    p.append(text(W / 2, 92, "крок позаду", size=10, color=MUTED, italic=True))

    # розв'язок
    sol, sw_, sh_ = textbox(W / 2, 210,
                            "виверт: невідомий рядок = попередній (AB) + його ж перший символ (A) = ABA",
                            size=11.5, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(sol)
    p.append(text(W / 2, 268,
                  "трапляється рівно тоді, коли рядок iде підряд сам за собою (взірець cScSc)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "kwkwk.svg"), W, H, *p,
           title="Пастка KwKwK: декодер на крок позаду — і як її обійти")


# ── patent: патент Unisys гальмує GIF → народжується PNG ───────────────────────
# Ідея: одна часова смуга. Алгоритм вільно розходиться (GIF, compress), аж тут
# власник згадує про патент — і спільнота тікає в PNG. Патент спливає, але запізно.

def fig_patent():
    W, H = 760, 250
    p = []
    y = 130
    p.append(line(60, y, W - 50, y, color=INK, sw=2))
    marks = [
        (60,  "1983", "патент\nподано"),
        (215, "1985", "патент\nвидано"),
        (340, "1987", "LZW у GIF —\nрозходиться"),
        (500, "1994", "Unisys: «GIF\nліцензуйте!»"),
        (640, "1996", "у відповідь —\nPNG (вільний)"),
        (W - 70, "2003", "патент\nспливає"),
    ]
    for x, yr, lab in marks:
        col = POS if "ліцензуйте" in lab or "видано" in lab else (FIELD if "PNG" in lab else INK)
        p.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        p.append(text(x, y - 16, yr, size=12, color=col, bold=True))
        # підпис то вгорі, то внизу не плутаємо — усі вниз
        p.append(mtext(x, y + 28, lab, size=9.5, color=INK))
    p.append(text(W / 2, H - 14,
                  "сім років мовчанки, тоді раптова вимога ліцензій — і втеча у вільний формат",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "patent.svg"), W, H, *p,
           title="Патент Unisys на LZW: чому GIF поступився PNG")


# ══ ФІГУРИ ДЕТАЛЬНОЇ ВЕРСІЇ (lzw-d.md) ════════════════════════════════════════

# ── d_trace: повна траса WED WE WEE WEB WET зі словником, що росте ─────────────
# Ідея: показати на реальнішому рядку, як записи довшають і ПОВТОРНО вживаються
# (код 261 = " WE" спрацьовує двічі). Видно стиск 18 символів → 12 кодів.

def fig_d_trace():
    W, H = 760, 520
    p = []
    rows = [
        ("W",   "E", "87 (W)",  "256 = WE"),
        ("E",   "D", "69 (E)",  "257 = ED"),
        ("D",   "␣", "68 (D)",  "258 = D␣"),
        ("␣",   "W", "32 (␣)",  "259 = ␣W"),
        ("WE",  "␣", "256 (WE)", "260 = WE␣"),
        ("␣W",  "E", "259 (␣W)", "261 = ␣WE"),
        ("E",   "E", "69 (E)",  "262 = EE"),
        ("E",   "␣", "69 (E)",  "263 = E␣"),
        ("␣WE", "B", "261 (␣WE)", "264 = ␣WEB"),
        ("B",   "␣", "66 (B)",  "265 = B␣"),
        ("␣WE", "T", "261 (␣WE)", "266 = ␣WET"),
        ("T",   "—", "84 (T)",  "—"),
    ]
    cols = [("W", 70), ("c", 175), ("видано код", 250), ("додано в словник", 470)]
    yh = 60
    for name, x in cols:
        p.append(text(x, yh, name, size=11, color=MUTED, bold=True))
    p.append(line(40, yh + 8, W - 30, yh + 8, color=MUTED, sw=1))
    y = yh + 32
    dy = 35
    for (w, c, emit, add) in rows:
        reused = emit.startswith("261") and add == "—"
        p.append(text(70, y, w, size=11.5, color=INK, bold=True))
        p.append(text(175, y, c, size=11.5, color=INK, bold=True))
        ecol = FIELD if emit.startswith("256") or emit.startswith("259") or emit.startswith("261") else NEG
        eb, ebw, ebh = textbox(250 + 52, y - 4, emit, size=10.5, bold=True,
                               fill=("#eafaf0" if ecol == FIELD else "#eaf0fd"),
                               stroke=ecol, sw=1.2, color=ecol)
        p.append(eb)
        if add != "—":
            ab, abw, abh = textbox(470 + 44, y - 4, add, size=10.5, bold=True,
                                   fill="#f6f4ec", stroke=INK, sw=1.1, color=INK)
            p.append(ab)
        y += dy
    p.append(line(40, y - 14, W - 30, y - 14, color=MUTED, sw=1, dash="3 3"))
    p.append(text(W / 2, y + 6,
                  "18 символів → 12 кодів; зелені — багатосимвольні записи (261=«␣WE» спрацював двічі)",
                  size=11, color=POS, italic=True, bold=True))
    render(os.path.join(OUT, "d-trace.svg"), W, H, *p,
           title="Повна траса: WED WE WEE WEB WET (␣ = пробіл)")


# ── d_width: розрядність коду росте; службові коди clear/end ───────────────────
# Ідея: показати, як ширина коду в бітах піднімається сходинками 9→10→11→12 у міру
# того, як номери ростуть, і де сидять службові коди скидання (256) та кінця (257).

def fig_d_width():
    W, H = 740, 330
    p = []
    # сходинки ширини
    base_y = 250
    steps = [(9, "0…511", "#eef4ff"), (10, "512…1023", "#e6eefc"),
             (11, "1024…2047", "#dde7fb"), (12, "2048…4095", "#d3e0fa")]
    x = 70
    bw = 150
    for i, (bits, rng, col) in enumerate(steps):
        h = 30 + i * 28
        p.append(rect(x, base_y - h, bw, h, fill=col, stroke=NEG, sw=1.4))
        p.append(text(x + bw / 2, base_y - h - 8, "%d біт" % bits, size=12, color=NEG, bold=True))
        p.append(text(x + bw / 2, base_y - h / 2 + 4, "коди " + rng, size=9.5, color=INK))
        x += bw + 6
    p.append(line(60, base_y, W - 40, base_y, color=INK, sw=1.5))
    p.append(text(W / 2, base_y + 24,
                  "ширина росте на біт, коли черговий номер уже не влазить — обидва боки одночасно",
                  size=10.5, color=MUTED, italic=True))

    # службові коди
    sb, sbw, sbh = textbox(W / 2, 72, "службові коди (поряд із 256 символами): 256 = скидання · 257 = кінець",
                           size=11, bold=True, fill="#fdf6e3", stroke="#d98a00", sw=1.5, color="#a8690a")
    p.append(sb)
    render(os.path.join(OUT, "d-width.svg"), W, H, *p,
           title="Розрядність коду росте сходинками; службові коди clear/end")


# ── d_proof: чому cScSc — ЄДИНИЙ випадок відсутнього коду ──────────────────────
# Ідея: логічний ланцюжок. Декодер відстає рівно на один запис; тож єдиний код,
# якого може бракувати, — це наступний-вільний; а він виникає лише коли збіг
# наздоганяє власний хвіст. Звідси й формула prev + перший символ prev.

def fig_d_proof():
    W, H = 720, 440
    p = []
    chain = [
        ("декодер завжди має\nусі коди, КРІМ\nнаступного-вільного", NEG, "#eaf0fd"),
        ("отже єдиний бракливий\nкод = той, що його\nкодувальник щойно завів", INK, "#f6f4ec"),
        ("а так буває лише коли\nрядок iде підряд сам за\nсобою (взірець cScSc)", POS, "#fdecea"),
        ("тоді бракливий рядок =\nprev + перший символ prev\n— завжди, без винятків", FIELD, "#eafaf0"),
    ]
    y = 78
    for i, (txt, col, fill) in enumerate(chain):
        b, bw, bh = textbox(W / 2, y, txt, size=11.5, bold=True, fill=fill, stroke=col, sw=1.7, color=col)
        p.append(b)
        if i < len(chain) - 1:
            p.append(arrow(W / 2, y + bh / 2 + 2, W / 2, y + bh / 2 + 26, color=INK, sw=1.8))
        y += bh + 36
    render(os.path.join(OUT, "d-proof.svg"), W, H, *p,
           title="Чому cScSc — єдиний випадок, коли коду ще немає")


if __name__ == "__main__":
    fig_idea()
    fig_encode()
    fig_mirror()
    fig_kwkwk()
    fig_patent()
    fig_d_trace()
    fig_d_width()
    fig_d_proof()
    print("OK: figures written to", OUT)
