# -*- coding: utf-8 -*-
# Фігури теми «Кодування інструкцій». svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

OP_F, OP = "#fdf4f4", POS          # поле опкоду (що робити) — червоне
RD_F, RD = "#eef2fd", NEG          # регістр-приймач / регістри — синє
IMM_F, IMM = "#f4f7f4", FIELD      # безпосереднє значення / поле — зелене
GLD_F, GLD = "#fbf3df", "#a9842f"  # акцент, примітка


# ── figure 1: fixed vs variable length ───────────────────────────────────────
# Ідея: у сталій довжині кожна команда однакова (4 байти) — наступна завжди на
# +4, вирівняно, декодувати можна всі паралельно. У змінній команди різні (1..N
# байтів) — де починається наступна, знаєш ЛИШЕ розібравши поточну (ланцюг).
def fig_fixed_vs_variable():
    W, H = 800, 430
    p = []

    # ── верх: СТАЛА ДОВЖИНА ──
    p.append(text(W / 2, 54, "СТАЛА ДОВЖИНА (RISC-V): кожна команда — рівно 4 байти",
                  size=13, color=IMM, bold=True))
    x0, y = 70, 74
    cw = 150
    addrs = ["0x00", "0x04", "0x08", "0x0C"]
    names = ["add", "lw", "addi", "bne"]
    for i in range(4):
        x = x0 + i * (cw + 8)
        p.append(rect(x, y, cw, 46, fill=IMM_F, stroke=IMM, sw=1.8, rx=7))
        p.append(text(x + cw / 2, y + 21, names[i], size=12, color=INK, bold=True))
        p.append(text(x + cw / 2, y + 38, "4 байти", size=9.5, color=MUTED))
        p.append(text(x + cw / 2, y - 6, addrs[i], size=9.5, color=MUTED))
    p.append(text(W / 2, y + 74,
                  "наступна команда завжди на +4 — межі відомі НАПЕРЕД, усі можна "
                  "декодувати водночас",
                  size=10, color=MUTED, italic=True))

    # роздільник
    p.append(line(50, 190, W - 50, 190, color=MUTED, sw=1, dash="5,4"))

    # ── низ: ЗМІННА ДОВЖИНА ──
    p.append(text(W / 2, 224, "ЗМІННА ДОВЖИНА (x86): команда — від 1 до 15 байтів",
                  size=13, color=OP, bold=True))
    x = 70
    y2 = 244
    # (мнемоніка, ширина-байтів, піксель-ширина)
    ins = [("push", 1, 64), ("mov r,imm32", 5, 200), ("inc", 1, 64),
           ("add [mem],r", 3, 128), ("ret", 1, 64)]
    addr = 0
    for name, nb, pw in ins:
        p.append(rect(x, y2, pw, 46, fill=OP_F, stroke=OP, sw=1.8, rx=7))
        fs = 11 if pw >= 100 else 9
        p.append(text(x + pw / 2, y2 + 20, name, size=fs, color=INK, bold=True))
        p.append(text(x + pw / 2, y2 + 37, "%d Б" % nb, size=9, color=MUTED))
        p.append(text(x + pw / 2, y2 - 6, "0x%02X" % addr, size=8.5, color=MUTED))
        x += pw + 6
        addr += nb
    p.append(text(W / 2, y2 + 76,
                  "щоб знати, де ПОЧИНАЄТЬСЯ наступна, треба спершу розібрати поточну "
                  "й дізнатися її довжину — суто послідовно",
                  size=10, color=MUTED, italic=True))
    p.append(text(W / 2, H - 16,
                  "той самий розмін усюди: сталість — простий швидкий декодер; "
                  "змінність — щільніший код ціною складнішого розбору",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "fixed-vs-variable.svg"), W, H, *p,
           title="Дві філософії кодування: стала довжина проти змінної")


# ── figure 2: fields of a real 32-bit RISC-V instruction (R vs I) ────────────
# Ідея: те саме 32-бітне число ділиться на поля по-різному залежно від формату,
# АЛЕ опкод завжди в тих самих молодших 7 бітах, а номери регістрів — на тих
# самих місцях. Де в R-типі був другий регістр, в I-типі — безпосереднє число.
def fig_encoding_fields():
    W, H = 820, 400
    p = []
    left = 40
    total_w = W - 2 * left

    def draw_row(y, label, fields):
        # fields: список (ширина-біт, підпис, колір-заливки, колір-рамки)
        p.append(text(left, y - 8, label, size=11.5, color=INK, bold=True, anchor="start"))
        totbits = sum(f[0] for f in fields)
        x = left
        for nb, lab, fc, sc in fields:
            w = total_w * nb / totbits
            p.append(rect(x, y, w, 50, fill=fc, stroke=sc, sw=1.7, rx=5))
            p.append(text(x + w / 2, y + 22, lab, size=10.5, color=INK, bold=True))
            p.append(text(x + w / 2, y + 39, "%d біт" % nb, size=9, color=MUTED))
            x += w

    # R-тип: додати два регістри
    draw_row(70, "R-тип  ·  add x3, x1, x2  (додати регістр до регістра)",
             [(7, "funct7", GLD_F, GLD), (5, "rs2", RD_F, RD),
              (5, "rs1", RD_F, RD), (3, "funct3", OP_F, OP),
              (5, "rd", RD_F, RD), (7, "opcode", OP_F, OP)])

    # I-тип: додати число до регістра
    draw_row(180, "I-тип  ·  addi x3, x1, 100  (додати число до регістра)",
             [(12, "imm[11:0]  (число)", IMM_F, IMM),
              (5, "rs1", RD_F, RD), (3, "funct3", OP_F, OP),
              (5, "rd", RD_F, RD), (7, "opcode", OP_F, OP)])

    # напрямні лінії: спільні поля стоять на тих самих місцях (справа)
    p.append(line(left + total_w * (1 - 7 / 32), 120, left + total_w * (1 - 7 / 32), 180,
                  color=OP, sw=1.3, dash="4,3"))
    p.append(line(left + total_w * (1 - 15 / 32), 120, left + total_w * (1 - 15 / 32), 180,
                  color=RD, sw=1.3, dash="4,3"))
    p.append(text(W / 2, 250,
                  "опкод — завжди молодші 7 біт; rd і rs1 — на тих самих місцях в обох "
                  "форматах (пунктир)", size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 272,
                  "де в R-типі стояв другий регістр (rs2 + funct7), в I-типі лежить "
                  "12-бітне число", size=10.5, color=MUTED, italic=True))

    # приклад-число
    p.append(rect(left, 300, total_w, 62, fill=BG, stroke=INK, sw=1.4, rx=8))
    p.append(text(W / 2, 322, "addi x3, x1, 100   →   0x06408193", size=13, color=INK, bold=True))
    p.append(text(W / 2, 344,
                  "те саме 32-бітне число: молодші 7 біт 0010011 = «add-immediate», "
                  "старші 12 = 100",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "encoding-fields.svg"), W, H, *p,
           title="Одне 32-бітне число, різні формати: спільні поля тримають місце")


# ── figure 3: why a fixed immediate is limited, and the lui+addi trick ───────
# Ідея: у сталій 32-бітній команді на число лишається мало біт (12 → діапазон
# −2048..2047). Більше в ОДНУ команду не влазить фізично. Тому велике число
# складають ДВІ команди: lui кладе старші 20 біт, addi додає молодші 12.
def fig_immediate_limit():
    W, H = 800, 430
    p = []

    # ліворуч: одна команда — тісне поле
    p.append(text(200, 56, "12 біт на число в одній команді", size=12, color=IMM, bold=True))
    p.append(rect(40, 70, 320, 44, fill=BG, stroke=INK, sw=1.5, rx=6))
    # мінінабір полів
    segs = [("opcode+rd+rs1+funct3", 20, OP_F, OP), ("imm 12б", 12, IMM_F, IMM)]
    x = 40
    for lab, nb, fc, sc in segs:
        w = 320 * nb / 32
        p.append(rect(x, 70, w, 44, fill=fc, stroke=sc, sw=1.6, rx=5))
        fs = 9 if w > 90 else 8
        p.append(text(x + w / 2, 96, lab, size=fs, color=INK, bold=(nb == 12)))
        x += w
    p.append(text(200, 138, "12 біт зі знаком →", size=10.5, color=MUTED, italic=True))
    p.append(rect(70, 150, 260, 34, fill=IMM_F, stroke=IMM, sw=1.6, rx=6))
    p.append(text(200, 172, "−2048 … +2047", size=13, color=INK, bold=True))
    p.append(text(200, 204, "більше в ОДНУ команду не влазить —", size=10, color=OP, italic=True))
    p.append(text(200, 219, "місця в 32 бітах просто немає", size=10, color=OP, italic=True))

    # роздільник
    p.append(line(410, 60, 410, 240, color=MUTED, sw=1, dash="5,4"))

    # праворуч: велика константа = дві команди
    p.append(text(610, 56, "велике число 0x12345678?", size=12, color=GLD, bold=True))
    p.append(text(610, 76, "складаємо ДВОМА командами:", size=10, color=MUTED, italic=True))

    p.append(rect(460, 92, 300, 44, fill=RD_F, stroke=RD, sw=1.7, rx=7))
    p.append(text(610, 112, "lui  x5, 0x12345", size=12, color=INK, bold=True))
    p.append(text(610, 128, "кладе старші 20 біт у x5", size=9, color=MUTED))

    p.append(arrow(610, 138, 610, 156, color=INK, sw=1.7))

    p.append(rect(460, 158, 300, 44, fill=IMM_F, stroke=IMM, sw=1.7, rx=7))
    p.append(text(610, 178, "addi x5, x5, 0x678", size=12, color=INK, bold=True))
    p.append(text(610, 194, "додає молодші 12 біт", size=9, color=MUTED))

    p.append(text(610, 226, "два кроки замість одного — плата", size=10, color=MUTED, italic=True))
    p.append(text(610, 241, "за сталу довжину команди", size=10, color=MUTED, italic=True))

    # низ: мораль
    p.append(line(50, 270, W - 50, 270, color=MUTED, sw=1, dash="5,4"))
    p.append(text(W / 2, 300,
                  "Кодування не лише описує команду — воно ОБМЕЖУЄ, що команда взагалі "
                  "може виразити.",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 328,
                  "Скільки біт віддали під число — стільки й діапазон; скільки під поле "
                  "регістра — стільки регістрів адресуєш.",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, 352,
                  "5 біт на регістр → рівно 2⁵ = 32 регістри. Ані на один більше — "
                  "поле не розтягнути.",
                  size=10.5, color=MUTED, italic=True))
    p.append(text(W / 2, H - 20,
                  "формат — це і бюджет: кожне поле вкрадене в інших, тому в ISA завжди "
                  "чимось жертвують",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "immediate-limit.svg"), W, H, *p,
           title="Кодування як бюджет бітів: чим платиш за сталу довжину")


# ── figure 4: why addi's sign extension poisons the naive split ──────────────
# Ідея (вставка math-immediate-split): наївне розбиття hi=val>>12, lo=val&0xFFF
# ламається, коли bit 11 молодшої частини = 1. addi трактує 12 біт ЗІ ЗНАКОМ,
# тож із bit11=1 воно від'ємне: замість +lo додається lo−4096. Різниця рівно
# 4096 = 1<<12 з'їдає одну одиницю зі старшої частини. Компенсація: +1 у hi.
def fig_sign_poison():
    W, H = 820, 400
    p = []

    # ── зверху: одні й ті самі 12 біт, два прочитання ──
    p.append(text(W / 2, 54, "ті самі 12 біт 0xFFF — два прочитання",
                  size=13, color=INK, bold=True))

    # беззнакове прочитання
    p.append(rect(60, 74, 300, 60, fill=IMM_F, stroke=IMM, sw=1.7, rx=8))
    p.append(text(210, 96, "як БЕЗЗНАКОВЕ", size=10.5, color=MUTED))
    p.append(text(210, 118, "0xFFF = +4095", size=15, color=FIELD, bold=True))

    # знакове прочитання (те, що робить addi)
    p.append(rect(460, 74, 300, 60, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    p.append(text(610, 96, "як addi (ЗІ ЗНАКОМ)", size=10.5, color=MUTED))
    p.append(text(610, 118, "0xFFF = −1", size=15, color=POS, bold=True))

    p.append(text(W / 2, 156,
                  "bit 11 = 1 → addi бачить від'ємне: різниця рівно 4096 = 1<<12",
                  size=11, color=INK, italic=True))

    # роздільник
    p.append(line(50, 178, W - 50, 178, color=MUTED, sw=1, dash="5,4"))

    # ── знизу: наївна сума проти виправленої ──
    p.append(text(W / 2, 206, "хочемо: hi·4096 + 4095   але addi дає: hi·4096 + (−1)",
                  size=12, color=INK, bold=True))

    # наївно
    p.append(rect(60, 226, 300, 74, fill=BG, stroke=POS, sw=1.7, rx=8))
    p.append(text(210, 248, "НАЇВНО  hi = val>>12", size=11, color=POS, bold=True))
    p.append(text(210, 270, "hi·4096 + (−1)", size=13, color=INK))
    p.append(text(210, 290, "недобір на 4096 — сума менша", size=9.5, color=MUTED, italic=True))

    p.append(arrow(370, 263, 448, 263, color=INK, sw=2))
    p.append(text(409, 254, "+1", size=12, color=FIELD, bold=True))

    # виправлено
    p.append(rect(460, 226, 300, 74, fill=BG, stroke=FIELD, sw=1.7, rx=8))
    p.append(text(610, 248, "hi = (val+0x800)>>12", size=11, color=FIELD, bold=True))
    p.append(text(610, 270, "(hi+1)·4096 + (−1) = ✓", size=13, color=INK))
    p.append(text(610, 290, "+4096 гасить −1 від знака", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 22,
                  "+0x800 — це +2048: він переносить одиницю в bit 12 РІВНО тоді, коли "
                  "bit 11 молодших = 1",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "sign-poison.svg"), W, H, *p,
           title="Чому наївне розбиття ламається: addi читає число зі знаком")


# ── figure 5: worked split of 0x12345FFF into lui+addi ───────────────────────
# Ідея: конкретне число, де компенсація потрібна. 0x12345FFF: молодші 12 біт
# 0xFFF (bit11=1). Наївний hi=0x12345 дав би недобір; правильний hi=0x12346,
# lo=−1. Перевірка: 0x12346·4096 + (−1) = 0x12346000 − 1 = 0x12345FFF. ✓
def fig_worked_split():
    W, H = 820, 430
    p = []

    p.append(text(W / 2, 54, "val = 0x12345FFF   (молодші 12 біт = 0xFFF, bit 11 = 1)",
                  size=13, color=INK, bold=True))

    # рядок бітів: 20 старших | 12 молодших
    bx, by, bw = 60, 78, W - 120
    hi_w = bw * 20 / 32
    lo_w = bw * 12 / 32
    p.append(rect(bx, by, hi_w, 48, fill=RD_F, stroke=RD, sw=1.7, rx=6))
    p.append(text(bx + hi_w / 2, by + 22, "старші 20 біт = 0x12345", size=11, color=INK, bold=True))
    p.append(text(bx + hi_w / 2, by + 39, "→ lui", size=9.5, color=MUTED))
    p.append(rect(bx + hi_w, by, lo_w, 48, fill="#fdecea", stroke=POS, sw=1.7, rx=6))
    p.append(text(bx + hi_w + lo_w / 2, by + 22, "0xFFF", size=11, color=INK, bold=True))
    p.append(text(bx + hi_w + lo_w / 2, by + 39, "bit 11 = 1", size=9.5, color=POS))

    # роздільник
    p.append(line(50, 150, W - 50, 150, color=MUTED, sw=1, dash="5,4"))

    # два стовпці: наївно (ламається) vs правильно
    # наївно
    p.append(rect(50, 168, 340, 118, fill=BG, stroke=POS, sw=1.6, rx=8))
    p.append(text(220, 190, "НАЇВНО (ламається)", size=11.5, color=POS, bold=True))
    p.append(text(220, 214, "hi = 0x12345,  lo = 0xFFF як −1", size=10.5, color=INK))
    p.append(text(220, 236, "0x12345·4096 + (−1)", size=11, color=INK))
    p.append(text(220, 256, "= 0x12345000 − 1", size=11, color=INK))
    p.append(text(220, 276, "= 0x12344FFF  ✗  (на 4096 менше)", size=11, color=POS, bold=True))

    # правильно
    p.append(rect(430, 168, 340, 118, fill=BG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(600, 190, "З КОМПЕНСАЦІЄЮ ✓", size=11.5, color=FIELD, bold=True))
    p.append(text(600, 214, "hi = (val+0x800)>>12 = 0x12346", size=10.5, color=INK))
    p.append(text(600, 236, "lo = val − (hi<<12) = −1", size=10.5, color=INK))
    p.append(text(600, 256, "0x12346·4096 + (−1)", size=11, color=INK))
    p.append(text(600, 276, "= 0x12346000 − 1 = 0x12345FFF ✓", size=10.5, color=FIELD, bold=True))

    # підсумкові команди
    p.append(rect(bx, 306, bw, 46, fill=GLD_F, stroke=GLD, sw=1.6, rx=8))
    p.append(text(W / 2, 328, "lui  x5, 0x12346      addi x5, x5, -1",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 346, "старша частина на +1 більша; молодша від'ємна — і разом рівно ціль",
                  size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 20,
                  "перенесення +0x800 підняло 0x12345 → 0x12346; знакове −1 з'їдає рівно "
                  "той зайвий 4096",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "worked-split.svg"), W, H, *p,
           title="Розбиття 0x12345FFF: коли старшу частину доводиться збільшити")


# ── figure 6 (вставка hist-thumb): як декодер Thumb-2 розрізняє 16/32-біт ─────
# Ідея: у змішаному потоці декодер дивиться лише на старші 5 біт кожного 16-бітного
# слова. Три зарезервовані шаблони (11101/11110/11111) = «перша половина 32-бітної
# команди, дочитай друге слово»; будь-що інше = ціла 16-бітна команда. Одне 5-бітне
# порівняння задає довжину — потік ніколи не збивається.
def fig_thumb2_decode():
    W, H = 720, 440
    p = []

    p.append(text(W / 2, 34, "Потік Thumb-2: підряд 16-бітні слова (halfwords)",
                  size=14, bold=True))

    # стрічка halfword-ів
    hw_y, hw_w, hw_h, gap = 66, 118, 44, 10
    xs = 60
    labels = [("0100 0…", "16"), ("1111 0…", "hw1"), ("…  …", "hw2"), ("0010 1…", "16")]
    cxs = []
    for i, (lab, kind) in enumerate(labels):
        x = xs + i * (hw_w + gap)
        cxs.append(x + hw_w / 2)
        if kind == "hw1":
            fc, sc = "#eef2fd", NEG
        elif kind == "hw2":
            fc, sc = "#eef1f4", MUTED
        else:
            fc, sc = "#f4f7f4", FIELD
        p.append(rect(x, hw_y, hw_w, hw_h, fill=fc, stroke=sc, sw=1.9, rx=6))
        p.append(text(x + hw_w / 2, hw_y + 21, lab, size=12, color=INK, bold=True))
        p.append(text(x + hw_w / 2, hw_y + 37, kind if kind != "16" else "16-біт", size=9, color=MUTED))

    # брекет: hw1+hw2 = одна 32-бітна команда
    x1 = xs + 1 * (hw_w + gap)
    x2 = xs + 2 * (hw_w + gap) + hw_w
    p.append(line(x1, hw_y - 10, x2, hw_y - 10, color=NEG, sw=2))
    p.append(line(x1, hw_y - 10, x1, hw_y - 3, color=NEG, sw=2))
    p.append(line(x2, hw_y - 10, x2, hw_y - 3, color=NEG, sw=2))
    p.append(text((x1 + x2) / 2, hw_y - 16, "одна 32-бітна команда", size=10, color=NEG))

    # питання декодера
    q_y = 176
    qb, qw, qh = textbox(W / 2, q_y, "Дивись лише на старші 5 біт (bits[15:11])",
                         size=14, bold=True, fill=GLD_F, stroke=GLD)
    p.append(qb)
    p.append(arrow(cxs[0], hw_y + hw_h, cxs[0], q_y - qh / 2, color=MUTED))
    p.append(arrow(cxs[1], hw_y + hw_h, W / 2 - qw / 2 + 20, q_y - qh / 2, color=MUTED))

    # дві гілки
    by = 300
    lb, lw, lh = textbox(200, by,
                         ["НЕ 11101/11110/11111", "→ ціла 16-бітна команда", "наступна одразу за нею  (+2)"],
                         size=12, fill="#f4f7f4", stroke=FIELD, sw=2)
    p.append(lb)
    p.append(arrow(W / 2 - 60, q_y + qh / 2, 200, by - lh / 2, color=FIELD, sw=2))

    rb, rw, rh = textbox(520, by,
                         ["11101 / 11110 / 11111", "→ перша половина 32-бітної", "дочитай hw2 з +2, склей  (+4)"],
                         size=12, fill="#eef2fd", stroke=NEG, sw=2)
    p.append(rb)
    p.append(arrow(W / 2 + 60, q_y + qh / 2, 520, by - rh / 2, color=NEG, sw=2))

    p.append(text(W / 2, H - 22,
                  "одне 5-бітне порівняння задає довжину — потік ніколи не збивається",
                  size=12.5, color=INK, bold=True))

    render(os.path.join(OUT, "thumb2-decode.svg"), W, H, *p)


if __name__ == "__main__":
    fig_fixed_vs_variable()
    fig_encoding_fields()
    fig_immediate_limit()
    fig_sign_poison()
    fig_worked_split()
    fig_thumb2_decode()
    print("OK: figures written to", OUT)
