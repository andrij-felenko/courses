# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-stages: LZ77 готує потік, Гаффман його записує ────────────────────────
# Ідея: показати конвеєр DEFLATE як два цехи. Перший (LZ77) перетворює сирі
# байти на потік «літера або (довжина, відступ)»; другий (Гаффман) кодує цей
# потік короткими бітами. Стрілка веде зліва направо.

def fig_two_stages():
    W, H = 700, 320
    p = []
    # сирий вхід
    raw, rw, rh = textbox(110, 90, "сирі байти\n…рядок рядок…", size=13, bold=True,
                          fill="#eaf2fb", stroke=INK, sw=1.8, min_w=150)
    p.append(raw)
    # цех 1: LZ77
    s1, w1, h1 = textbox(350, 90, "LZ77\nсловник повторів", size=13, bold=True,
                         fill="#d7f0de", stroke=FIELD, sw=1.9, min_w=190)
    p.append(s1)
    # цех 2: Гаффман
    s2, w2, h2 = textbox(590, 90, "Гаффман\nентропійне кодування", size=13, bold=True,
                         fill="#f3c6bf", stroke=POS, sw=1.9, min_w=190)
    p.append(s2)

    p.append(arrow(190, 90, 252, 90, color=MUTED, sw=2.0))
    p.append(arrow(448, 90, 492, 90, color=MUTED, sw=2.0))

    # що тече між цехами
    p.append(text(221, 74, "байти", size=10, color=MUTED))
    p.append(text(470, 74, "символи", size=10, color=MUTED))

    # проміжний потік символів під цехом 1
    mid, mw, mh = textbox(350, 185, "потік символів:\nлітера · (довжина, відступ) · літера", size=12,
                          fill=FILL, stroke=MUTED, sw=1.4, color=INK, min_w=320)
    p.append(mid)
    p.append(line(350, 116, 350, 162, color=MUTED, sw=1.2, dash="3,3"))

    # вихід: щільні біти
    out, ow, oh = textbox(590, 185, "щільні біти\n0110…", size=12,
                          fill=FILL, stroke=POS, sw=1.4, color=INK, min_w=150)
    p.append(out)
    p.append(line(590, 116, 590, 162, color=MUTED, sw=1.2, dash="3,3"))

    p.append(text(W / 2, H - 24,
                  "LZ77 викидає повтори; Гаффман дешево записує те, що лишилось",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "two-stages.svg"), W, H, *p,
           title="DEFLATE = LZ77, тоді Гаффман")


# ── worked: ABABABAB → LZ77-токени → коди ─────────────────────────────────────
# Ідея: на крихітному рядку показати обидва кроки руками. Перший рядок — байти,
# другий — токени LZ77 (літери + один зворотний збіг), третій — що кодує Гаффман.

def fig_worked():
    W, H = 700, 330
    p = []
    x0 = 70

    # рядок 1: вхідні байти
    p.append(text(x0, 70, "вхід:", size=12, color=INK, bold=True, anchor="start"))
    chars = list("ABABABAB")
    cw = 40
    for i, ch in enumerate(chars):
        bx = x0 + 70 + i * cw
        col = "#eaf2fb"
        p.append(rect(bx, 54, cw - 6, 30, fill=col, stroke=INK, sw=1.4, rx=4))
        p.append(text(bx + (cw - 6) / 2, 74, ch, size=14, color=INK, bold=True))
        p.append(text(bx + (cw - 6) / 2, 100, str(i), size=9, color=MUTED))

    # дужка: перші AB — буквально, решта — збіг назад
    p.append(text(x0, 150, "LZ77:", size=12, color=INK, bold=True, anchor="start"))
    t1, tw1, th1 = textbox(x0 + 130, 150, "A", size=13, bold=True, fill="#d7f0de", stroke=FIELD, sw=1.6, min_w=44)
    p.append(t1)
    t2, tw2, th2 = textbox(x0 + 185, 150, "B", size=13, bold=True, fill="#d7f0de", stroke=FIELD, sw=1.6, min_w=44)
    p.append(t2)
    t3, tw3, th3 = textbox(x0 + 330, 150, "(довжина 6, відступ 2)", size=12, bold=True,
                           fill="#f3c6bf", stroke=POS, sw=1.7, min_w=210)
    p.append(t3)

    p.append(text(x0 + 130, 188, "буквально", size=10, color=FIELD))
    p.append(text(x0 + 330, 188, "«скопіюй 6 байтів за 2 кроки тому»", size=10, color=POS))

    # рядок 3: що бачить Гаффман
    p.append(text(x0, 250, "Гаффман\nкодує:", size=11, color=INK, bold=True, anchor="start"))
    items = ["літера A", "літера B", "довжина 6", "відступ 2"]
    bx = x0 + 120
    for it in items:
        b, bw, bh = textbox(bx + 55, 252, it, size=11, fill=FILL, stroke=MUTED, sw=1.3, color=INK, min_w=100)
        p.append(b)
        bx += 118

    p.append(text(W / 2, H - 18,
                  "три появи довжин/відступів — рідкісні символи; A, B — часті → короткі коди",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "worked.svg"), W, H, *p,
           title="Два кроки руками: ABABABAB")


# ── block-types: три типи блоку DEFLATE ───────────────────────────────────────
# Ідея: три картки поруч — без стиску / фіксований Гаффман / динамічний Гаффман,
# під кожною — коли вигідний. Заголовок 3 біти (BFINAL+BTYPE) спільний.

def fig_block_types():
    W, H = 700, 330
    p = []
    cards = [
        ("00 — без стиску", "сирі байти 1:1\n(+ довжина)", "вже стиснене\nабо випадкове", "#cfe0f5", NEG),
        ("01 — фіксований\nГаффман", "готова таблиця\nкодів у RFC", "короткі дані:\nтаблиця задарма", "#d7f0de", FIELD),
        ("10 — динамічний\nГаффман", "своя таблиця\nна цей блок", "довгі дані:\nточно під них", "#f3c6bf", POS),
    ]
    cw = 200
    gap = 18
    x = 50
    for (title, body, when, fill, stroke) in cards:
        # шапка
        hb, hw, hh = textbox(x + cw / 2, 92, title, size=13, bold=True, fill=fill, stroke=stroke, sw=1.9, min_w=cw)
        p.append(hb)
        # тіло
        bb = fitbox(x, 130, cw, 64, body, size=12, fill=FILL, stroke=stroke, sw=1.4, color=INK)
        p.append(bb)
        # коли вигідний
        p.append(text(x + cw / 2, 222, "коли:", size=10, color=MUTED, bold=True))
        wb = fitbox(x, 232, cw, 56, when, size=11, fill="#fbfcfd", stroke=MUTED, sw=1.2, color=INK)
        p.append(wb)
        x += cw + gap

    p.append(text(W / 2, H - 14,
                  "кодер обирає тип на кожен блок окремо — що дешевше, те й бере",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "block-types.svg"), W, H, *p,
           title="Три типи блоку DEFLATE")


# ── window: ковзне вікно 32 КБ ────────────────────────────────────────────────
# Ідея: смуга даних; ліворуч — уже оброблене вікно 32 КБ (словник), праворуч —
# те, що ще попереду; збіг шукається лише в межах вікна назад.

def fig_window():
    W, H = 700, 300
    p = []
    bx, by, bh = 60, 110, 60
    # уся стрічка
    p.append(rect(bx, by, 580, bh, fill="#f4f6f8", stroke=MUTED, sw=1.3, rx=4))
    # вікно 32 КБ (минуле)
    ww = 300
    p.append(rect(bx, by, ww, bh, fill="#d7f0de", stroke=FIELD, sw=1.9, rx=4))
    p.append(text(bx + ww / 2, by + 36, "вікно 32 КБ (словник минулого)", size=12, color=INK, bold=True))
    # поточна позиція
    cx = bx + ww
    p.append(line(cx, by - 16, cx, by + bh + 16, color=POS, sw=2.2))
    p.append(text(cx, by - 22, "тут читаємо", size=11, color=POS, bold=True))
    # майбутнє
    p.append(text(cx + 130, by + 36, "ще попереду", size=12, color=MUTED))

    # збіг: стрілка від поточного назад у вікно
    p.append(arrow(cx - 4, by + bh + 30, bx + 90, by + bh + 30, color=NEG, sw=1.9))
    p.append(text((cx + bx + 90) / 2, by + bh + 48, "збіг шукаємо лише назад, у межах вікна",
                  size=11, color=NEG))

    p.append(text(W / 2, H - 14,
                  "відступ кодується max 32768; що далі назад — то довший код відступу",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "window.svg"), W, H, *p,
           title="Ковзне вікно 32 КБ")


# ── two-alphabets: дві абетки Гаффмана ────────────────────────────────────────
# Ідея: показати, що в DEFLATE два дерева: одне для (літера+довжина), друге для
# відступів; символ 256 — кінець блоку.

def fig_two_alphabets():
    W, H = 700, 340
    p = []
    # абетка 1: літери+довжини
    a1, w1, h1 = textbox(200, 95, "абетка 1: літери + довжини", size=13, bold=True,
                         fill="#f3c6bf", stroke=POS, sw=1.9, min_w=300)
    p.append(a1)
    rows1 = ["0…255 — літери (байти)", "256 — кінець блоку", "257…285 — довжини збігу 3…258"]
    for i, r in enumerate(rows1):
        p.append(text(60, 140 + i * 26, r, size=12, color=INK, anchor="start"))

    # абетка 2: відступи
    a2, w2, h2 = textbox(530, 95, "абетка 2: відступи", size=13, bold=True,
                         fill="#cfe0f5", stroke=NEG, sw=1.9, min_w=240)
    p.append(a2)
    rows2 = ["0…29 — код відступу", "відступ 1…32768", "(+ додаткові біти)"]
    for i, r in enumerate(rows2):
        p.append(text(425, 140 + i * 26, r, size=12, color=INK, anchor="start"))

    # роздільна лінія
    p.append(line(350, 70, 350, 230, color=MUTED, sw=1.2, dash="4,4"))

    p.append(text(W / 2, H - 70,
                  "довжина і відступ ідуть парою: довжина — з абетки 1, відступ — з абетки 2",
                  size=12, color=INK))
    p.append(text(W / 2, H - 44,
                  "кожна абетка — своє дерево Гаффмана; декодер знає, котре зараз читати",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "two-alphabets.svg"), W, H, *p,
           title="DEFLATE: дві абетки, два дерева")


# ── wrappers: zip / gzip / zlib / png навколо того самого DEFLATE ──────────────
# Ідея: ядро DEFLATE однакове; різні формати лише по-різному його загортають
# (заголовок + контрольна сума). Концентричні рамки / вкладені прямокутники.

def fig_wrappers():
    W, H = 700, 320
    p = []
    # ядро
    core, cw, ch = textbox(350, 165, "DEFLATE\n(RFC 1951)", size=14, bold=True,
                           fill="#f3c6bf", stroke=POS, sw=2.0, min_w=180)
    p.append(core)

    # чотири обгортки навколо
    wraps = [
        (350, 70, "gzip: заголовок + CRC-32 + розмір", FIELD),
        (350, 262, "zlib: 2 байти + Adler-32", NEG),
        (150, 165, "zip\n(архів)", MUTED),
        (560, 165, "PNG\n(зображення)", MUTED),
    ]
    for (x, y, lab, col) in wraps:
        b, bw, bh = textbox(x, y, lab, size=12, bold=True, fill="#fbfcfd", stroke=col, sw=1.6, min_w=150)
        p.append(b)
        # лінія до ядра
        p.append(line(x, y + (18 if y < 165 else -18) if x == 350 else y,
                      350, 165, color="#dde3ea", sw=1.0))

    p.append(text(W / 2, H - 14,
                  "ядро те саме; формати різняться лише заголовком і контрольною сумою",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "wrappers.svg"), W, H, *p,
           title="Один DEFLATE, різні обгортки")


# ════════════════════════ ДЕТАЛЬНА ВЕРСІЯ ════════════════════════

# ── block-layout: розкладка динамічного блоку по бітах ────────────────────────
# Ідея: горизонтальна стрічка полів блоку — від BFINAL/BTYPE через HLIT/HDIST/
# HCLEN, далі довжини code-length-кодів, спаковані довжини двох абеток, і дані.

def fig_block_layout():
    W, H = 720, 320
    p = []
    fields = [
        ("BFINAL\n1 біт", "#eaf2fb", INK, 70),
        ("BTYPE\n2 біти", "#eaf2fb", INK, 70),
        ("HLIT\n5", "#d7f0de", FIELD, 60),
        ("HDIST\n5", "#d7f0de", FIELD, 60),
        ("HCLEN\n4", "#d7f0de", FIELD, 60),
        ("довжини CL-\nкодів", "#cfe0f5", NEG, 95),
        ("спаковані дов-\nжини абеток", "#f3c6bf", POS, 120),
        ("стиснені\nдані", "#fbe3a0", "#b8860b", 90),
    ]
    x = 30
    y = 120
    h = 64
    for (lab, fill, stroke, w) in fields:
        p.append(fitbox(x, y, w, h, lab, size=11, fill=fill, stroke=stroke, sw=1.6, bold=True, color=INK))
        x += w + 6

    p.append(text(120, y - 16, "заголовок", size=11, color=MUTED, bold=True))
    p.append(text(470, y - 16, "опис двох дерев", size=11, color=POS, bold=True))

    p.append(text(W / 2, y + h + 40,
                  "HLIT/HDIST/HCLEN — лічильники; далі дерева описані самі собою, тоді дані",
                  size=12, color=INK))
    p.append(text(W / 2, y + h + 64,
                  "усе — щільний бітовий потік, без вирівнювання на байти",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "block-layout.svg"), W, H, *p,
           title="Розкладка динамічного блоку")


# ── code-length-codes: як пакують самі довжини (мета-Гаффман) ──────────────────
# Ідея: довжини кодів двох абеток — це теж послідовність чисел 0..15; її стискає
# ТРЕТІЙ Гаффман над алфавітом 0..18, де 16/17/18 — повтори. Показати ланцюг.

def fig_code_length_codes():
    W, H = 720, 340
    p = []
    # рівень 1: довжини двох абеток
    l1, w1, h1 = textbox(360, 80, "довжини кодів обох абеток:  3 3 3 0 0 0 0 0 5 5 …", size=12, bold=True,
                         fill="#f3c6bf", stroke=POS, sw=1.7, min_w=470)
    p.append(l1)
    p.append(text(360, 116, "багато повторів і нулів", size=10, color=MUTED))

    p.append(arrow(360, 130, 360, 168, color=MUTED, sw=2.0))

    # рівень 2: алфавіт довжин кодів 0..18
    l2, w2, h2 = textbox(360, 195, "алфавіт 0…18:  0…15 = довжина · 16 = повтор · 17,18 = серія нулів", size=12, bold=True,
                         fill="#cfe0f5", stroke=NEG, sw=1.7, min_w=560)
    p.append(l2)

    p.append(arrow(360, 213, 360, 251, color=MUTED, sw=2.0))

    # рівень 3: ще один Гаффман
    l3, w3, h3 = textbox(360, 278, "третій Гаффман кодує цей алфавіт → лічильник HCLEN", size=12, bold=True,
                         fill="#d7f0de", stroke=FIELD, sw=1.7, min_w=470)
    p.append(l3)

    p.append(text(W / 2, H - 14,
                  "дерево описує себе: довжини дерев стискає ще одне маленьке дерево",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "code-length-codes.svg"), W, H, *p,
           title="Як пакують самі таблиці")


# ── length-extra: код + додаткові біти кодують діапазон ───────────────────────
# Ідея: один код довжини покриває не одне число, а діапазон; точне значення в
# діапазоні добирають кілька «сирих» додаткових бітів. Економія алфавіту.

def fig_length_extra():
    W, H = 700, 300
    p = []
    rows = [
        ("265", "1 дод. біт", "11…12"),
        ("266", "1 дод. біт", "13…14"),
        ("269", "2 дод. біти", "19…22"),
        ("285", "0 дод. бітів", "258 (макс)"),
    ]
    x0, y0 = 120, 95
    colw = [110, 160, 200]
    heads = ["код", "додаткові біти", "довжина"]
    for j, hd in enumerate(heads):
        p.append(text(x0 + sum(colw[:j]) + colw[j] / 2, y0, hd, size=12, color=INK, bold=True))
    for i, (code, extra, val) in enumerate(rows):
        ry = y0 + 30 + i * 38
        p.append(line(x0, ry - 14, x0 + sum(colw), ry - 14, color="#dde3ea", sw=1.0))
        p.append(text(x0 + colw[0] / 2, ry + 6, code, size=13, color=POS, bold=True))
        p.append(text(x0 + colw[0] + colw[1] / 2, ry + 6, extra, size=12, color=NEG))
        p.append(text(x0 + colw[0] + colw[1] + colw[2] / 2, ry + 6, val, size=13, color=INK, bold=True))

    p.append(text(W / 2, H - 30,
                  "один код = діапазон; точне число добирають сирі додаткові біти — алфавіт лишається малим",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "length-extra.svg"), W, H, *p,
           title="Код довжини + додаткові біти")


if __name__ == "__main__":
    fig_two_stages()
    fig_worked()
    fig_block_types()
    fig_window()
    fig_two_alphabets()
    fig_wrappers()
    fig_block_layout()
    fig_code_length_codes()
    fig_length_extra()
    print("OK: figures written to", OUT)
