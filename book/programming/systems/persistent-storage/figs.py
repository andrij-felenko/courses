# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUEF  = "#f3f5fd"   # летке / холодне
GREENF = "#eef7ee"   # нелетке / збережене
WARN   = "#9a7322"
WARNF  = "#fff8e8"
WARNS  = "#caa24a"


# ── volatile-vs-nv: як тримається біт у леткій і нелеткій комірці ─────────────
# Ідея: летка тримає біт КРУГООБІГОМ струму (петля), нелетка — ЗАСТРЯГЛИМ
# зарядом; те саме питання «а без струму?» дає протилежну відповідь.
def fig_volatile_vs_nv():
    W, H = 760, 384
    p = [text(W/2, 30, "Два способи тримати біт: струмом чи фізично", size=17, bold=True),
         text(W/2, 50, "летка комірка пам'ятає, лише поки тече струм; нелетка — завдяки застряглому фізичному стану",
              size=11, color=MUTED, italic=True)]

    # ── ліва панель: летка (SRAM-петля) ──
    p.append(rect(40, 78, 330, 250, fill=BLUEF, stroke=NEG, sw=2, rx=12))
    p.append(text(205, 102, "Летка (volatile) — біт тримає струм", size=12, color=NEG, bold=True))

    # петля з двох інверторів
    p.append(fitbox(84, 126, 100, 40, "інвертор", size=10.5, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(fitbox(226, 126, 100, 40, "інвертор", size=10.5, fill=BG, stroke=INK, color=INK, bold=True))
    p.append(arrow(186, 138, 224, 138, color=FIELD, sw=2))          # верхня стрілка →
    p.append(arrow(224, 154, 186, 154, color=FIELD, sw=2))          # нижня стрілка ←
    p.append(text(205, 186, "вихід → вхід, по колу: сам себе тримає", size=9.5, color=MUTED, italic=True))

    p.append(line(64, 202, 346, 202, color=NEG, sw=1, dash="3 3"))
    p.append(text(205, 222, "прибрали струм", size=11, color=POS, bold=True))
    p.append(fitbox(74, 234, 262, 44, "петля рветься → біт зникає за мілісекунди",
                    size=10.5, fill="#fdecea", stroke=POS, color=POS, bold=True))
    p.append(text(205, 300, "як напис крейдою під дощем:", size=9.5, color=MUTED, italic=True))
    p.append(text(205, 316, "не поновлюєш — змиває", size=9.5, color=MUTED, italic=True))

    # ── права панель: нелетка (плавучий затвор) ──
    p.append(rect(390, 78, 330, 250, fill=GREENF, stroke=FIELD, sw=2, rx=12))
    p.append(text(555, 102, "Нелетка (non-volatile) — біт застряг", size=12, color=FIELD, bold=True))

    # плавучий затвор: острівець у ізоляторі з електронами
    p.append(rect(470, 124, 170, 46, fill=BG, stroke=WARNS, sw=1.6, rx=6))
    p.append(text(555, 118, "плавучий затвор (в ізоляторі)", size=9, color=MUTED, anchor="middle"))
    for i in range(5):
        p.append(minus(494 + i*28, 147, r=7))
    p.append(text(555, 190, "електрони замкнені оксидом — нема куди стекти", size=9.5, color=MUTED, italic=True))

    p.append(line(414, 202, 696, 202, color=FIELD, sw=1, dash="3 3"))
    p.append(text(555, 222, "прибрали струм", size=11, color=FIELD, bold=True))
    p.append(fitbox(424, 234, 262, 44, "заряд лишається → біт цілий ~10 років",
                    size=10.5, fill=GREENF, stroke=FIELD, color=FIELD, bold=True))
    p.append(text(555, 300, "як чорнило на папері:", size=9.5, color=MUTED, italic=True))
    p.append(text(555, 316, "лежить саме, без живлення", size=9.5, color=MUTED, italic=True))

    p.append(text(W/2, 356, "Те саме питання — «а без струму?» — розводить два світи пам'яті: робочий (летка) і той, що переживає вимкнення (нелетка).",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "volatile-vs-nv.svg"), W, H, *p)


# ── flash-write-cycle: читати легко, а писати — стерти блок, тоді нулі ────────
# Ідея: асиметрія Flash — читання побайтне й швидке; запис лише в один бік
# (гасити 1→0), а щоб повернути 1, треба стерти ЦІЛИЙ блок, і це зношує.
def fig_flash_write_cycle():
    W, H = 760, 396
    p = [text(W/2, 30, "Flash: читати просто, а писати — обхідним шляхом", size=17, bold=True),
         text(W/2, 50, "запис лише гасить одиниці в нулі; щоб знову підняти одиниці — стерти цілий блок, і кожне стирання зношує",
              size=10.5, color=MUTED, italic=True)]

    # читання — легко (ліва вузька колонка)
    p.append(rect(40, 78, 200, 120, fill=BLUEF, stroke=NEG, sw=1.8, rx=12))
    p.append(text(140, 102, "Читання", size=13, color=NEG, bold=True))
    for i, s in enumerate(["будь-який байт", "одразу, швидко", "скільки завгодно"]):
        p.append(text(58, 128 + i*22, "• " + s, size=10.5, color=INK, anchor="start"))

    # запис — три кроки (широка права область)
    p.append(text(490, 96, "Запис — три кроки", size=13, color=WARN, bold=True))

    # крок 1: стерти блок → усе 1
    p.append(text(360, 128, "1. стерти цілий блок", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(fitbox(360, 138, 150, 30, "1 1 1 1 1 1 1 1", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True, rx=4))
    p.append(arrow(516, 153, 556, 153, color=INK, sw=2))
    # крок 2: записати потрібні нулі
    p.append(text(560, 128, "2. записати нулі", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(fitbox(560, 138, 150, 30, "1 0 1 1 0 0 1 0", size=11, fill=GREENF, stroke=FIELD, color=INK, bold=True, rx=4))

    # крок 3: наочно про напрям і блок
    p.append(text(280, 208, "напрям запису — лише в один бік:", size=10.5, color=INK, bold=True, anchor="start"))
    p.append(fitbox(280, 220, 90, 30, "1 → 0", size=12, fill=GREENF, stroke=FIELD, color=FIELD, bold=True, rx=4))
    p.append(text(378, 240, "просто (запис)", size=9.5, color=FIELD, anchor="start"))
    p.append(fitbox(280, 258, 90, 30, "0 → 1", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True, rx=4))
    p.append(text(378, 278, "лише через стирання ВСЬОГО блоку", size=9.5, color=POS, anchor="start"))

    # знос
    p.append(rect(40, 220, 210, 100, fill=WARNF, stroke=WARNS, sw=1.6, rx=10))
    p.append(text(145, 244, "Знос", size=12, color=WARN, bold=True))
    p.append(text(58, 268, "стирання псує оксид;", size=10, color=INK, anchor="start"))
    p.append(text(58, 288, "блок витримує лише", size=10, color=INK, anchor="start"))
    p.append(text(58, 308, "~10⁴–10⁵ стирань", size=10.5, color=WARN, bold=True, anchor="start"))

    p.append(rect(40, 336, 680, 52, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    p.append(text(W/2, 358, "Тому код читають мільйони разів, а пишуть рідко. Хто пише у Flash щосекунди — зносить блок за дні;",
                  size=10.5, color=INK, bold=True))
    p.append(text(W/2, 378, "часте й мінливе тримають у RAM, а знос неминучих записів розмазують по всьому чипу.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "flash-write-cycle.svg"), W, H, *p)


# ── memory-lineage: сходинки свободи — кожен крок додав гнучкості, за ціну ────
# Ідея: родовід нелеткої пам'яті — це драбина, де кожен щабель віддає трохи
# жорсткості й здобуває трохи свободи, платячи за неї своєю ціною.
def fig_memory_lineage():
    W, H = 980, 470
    p = [text(W/2, 30, "Родовід нелеткої пам'яті: щабель за щаблем — більше свободи, за свою ціну", size=16, bold=True),
         text(W/2, 50, "від «вплавлено на заводі, не змінити» до «дешево й масово, але блоками»",
              size=11, color=MUTED, italic=True)]

    # шість щаблів: (підпис-носій, рік/автор, здобута свобода, ціна, колір-акцент, заливка)
    rows = [
        ("масочний ROM", "1960-ті",            "дані вплавлено маскою — вихідна точка", "не змінити взагалі ніколи",          MUTED,  FILL),
        ("PROM",         "Чжоу, 1956",         "програмуй сам, на столі",               "рівно один раз — назад ніяк",        NEG,    BLUEF),
        ("плавучий затвор","Кан і Ші, 1967",   "принцип: заряд можна і зняти",          "лише доведений принцип, ще не виріб", FIELD,  GREENF),
        ("EPROM 1702",   "Фроман, 1971",       "стирай і переписуй багато разів",       "вийми чип, світи УФ, оптом",         WARN,   WARNF),
        ("EEPROM",       "Гарарі 1976; Intel ~1980","стирай струмом, не виймаючи, побайтно","знос оксиду; дорого — лише малі обсяги", NEG, BLUEF),
        ("Flash",        "Масуока 1980 · NAND 1987","дешево, щільно, масово (терабайти)","стирання лише цілим блоком; знос блоку", FIELD, GREENF),
    ]

    # геометрія драбини: кожен щабель нижче й правіше, стрілка вгору-праворуч між ними
    x0, y0 = 30, 96          # лівий верх найнижчого щабля рахуємо від верхнього
    rh, gap = 54, 8          # висота смуги щабля і відступ
    step_dx = 18             # зсув управо на кожен щабель (відчуття підйому)
    band_w = 250             # ширина кольорової картки носія
    n = len(rows)

    for i, (name, who, freedom, price, acc, fillc) in enumerate(rows):
        y = y0 + i * (rh + gap)
        x = x0 + i * step_dx
        # картка носія (ліворуч)
        p.append(rect(x, y, band_w, rh, fill=fillc, stroke=acc, sw=1.8, rx=9))
        p.append(text(x + 14, y + 22, name, size=12.5, color=acc, bold=True, anchor="start"))
        p.append(text(x + 14, y + 40, who, size=9.5, color=MUTED, anchor="start"))
        # здобута свобода (+, зелена зона праворуч від картки)
        fx = x + band_w + 16
        p.append(text(fx, y + 15, "+ свобода", size=9, color=FIELD, bold=True, anchor="start"))
        p.append(fitbox(fx, y + 20, 300, 30, freedom, size=10, fill=GREENF, stroke=FIELD, color=INK, rx=6))
        # ціна (−, права колонка)
        cx = fx + 316
        p.append(text(cx, y + 15, "− ціна", size=9, color=POS, bold=True, anchor="start"))
        p.append(fitbox(cx, y + 20, 224, 30, price, size=9.5, fill="#fdecea", stroke=POS, color=INK, rx=6))
        # стрілка підйому між щаблями
        if i < n - 1:
            ay = y + rh
            p.append(arrow(x + 26, ay + 2, x + step_dx + 26, ay + gap - 1, color=INK, sw=1.8))

    p.append(text(W/2, H - 14, "Кожен щабель віддає трохи жорсткості й здобуває трохи свободи — але жоден крок не безкоштовний.",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "memory-lineage.svg"), W, H, *p)


# ── ab-slot-swap: пиши поруч, перемикайся однією перевірюваною дією ───────────
# Ідея: чинний слот НЕ чіпаємо; новий запис із більшим seq лягає в запасний;
# зміна поколінь = мить, коли новий слот уперше сходиться за CRC.
def fig_ab_slot_swap():
    W, H = 780, 392
    p = [text(W/2, 30, "Атомарне оновлення: пиши поруч, перемикайся однією дією", size=17, bold=True),
         text(W/2, 50, "чинний слот недоторканий, поки в запасному не з'явиться повний запис із більшим seq і зійденою сумою",
              size=10, color=MUTED, italic=True)]

    yb = 92                    # верх смуги слотів (крок «було»)
    slot_w, slot_h = 150, 70
    ax = 120                   # слот A
    bx = 510                   # слот B
    midx = (ax + slot_w + bx) / 2

    # ── крок «було»: A чинний (seq 7), B — старий запасний (seq 6) ──
    p.append(text(ax + slot_w/2, 82, "було", size=11, color=MUTED, bold=True))
    p.append(rect(ax, yb, slot_w, slot_h, fill=GREENF, stroke=FIELD, sw=2.2, rx=10))
    p.append(text(ax + slot_w/2, yb + 22, "слот A", size=12, color=FIELD, bold=True))
    p.append(text(ax + slot_w/2, yb + 43, "seq = 7", size=12, color=INK, bold=True))
    p.append(fitbox(ax + 16, yb + 50, slot_w - 32, 16, "ЧИННИЙ · CRC ✓", size=8.5, fill=GREENF, stroke=FIELD, color=FIELD, bold=True, rx=4))
    p.append(rect(bx, yb, slot_w, slot_h, fill=BG, stroke=MUTED, sw=2, rx=10))
    p.append(text(bx + slot_w/2, yb + 22, "слот B", size=12, color=MUTED, bold=True))
    p.append(text(bx + slot_w/2, yb + 43, "seq = 6", size=12, color=INK, bold=True))
    p.append(fitbox(bx + 16, yb + 50, slot_w - 32, 16, "старий, запасний", size=8.5, fill=FILL, stroke=MUTED, color=MUTED, bold=True, rx=4))
    p.append(arrow(ax + slot_w + 14, yb + slot_h/2, bx - 14, yb + slot_h/2, color=NEG, sw=2.4))
    p.append(text(midx, yb + slot_h/2 - 12, "пишемо в запасний", size=10, color=NEG, bold=True))
    p.append(text(midx, yb + slot_h/2 + 22, "слот A цілий — старі дані живі", size=9, color=MUTED, italic=True))

    # ── крок «стало»: B записався (seq 8, CRC ✓) → чинний; A тепер старий ──
    yb2 = 216
    p.append(text(ax + slot_w/2, yb2 - 10, "стало", size=11, color=MUTED, bold=True))
    p.append(rect(ax, yb2, slot_w, slot_h, fill=BG, stroke=MUTED, sw=2, rx=10))
    p.append(text(ax + slot_w/2, yb2 + 22, "слот A", size=12, color=MUTED, bold=True))
    p.append(text(ax + slot_w/2, yb2 + 43, "seq = 7", size=12, color=INK, bold=True))
    p.append(fitbox(ax + 16, yb2 + 50, slot_w - 32, 16, "тепер старий", size=8.5, fill=FILL, stroke=MUTED, color=MUTED, bold=True, rx=4))
    p.append(rect(bx, yb2, slot_w, slot_h, fill=GREENF, stroke=FIELD, sw=2.4, rx=10))
    p.append(text(bx + slot_w/2, yb2 + 22, "слот B", size=12, color=FIELD, bold=True))
    p.append(text(bx + slot_w/2, yb2 + 43, "seq = 8", size=12, color=INK, bold=True))
    p.append(fitbox(bx + 16, yb2 + 50, slot_w - 32, 16, "ЧИННИЙ · CRC ✓", size=8.5, fill=GREENF, stroke=FIELD, color=FIELD, bold=True, rx=4))
    p.append(arrow(ax + slot_w + 14, yb2 + slot_h/2, bx - 14, yb2 + slot_h/2, color=FIELD, sw=2.4))
    p.append(text(midx, yb2 + slot_h/2 - 12, "зійшовся за CRC", size=10, color=FIELD, bold=True))
    p.append(text(midx, yb2 + slot_h/2 + 22, "і seq більший → чинний", size=9, color=MUTED, italic=True))

    # нижній висновок
    p.append(rect(50, 316, 680, 60, fill=WARNF, stroke=WARNS, sw=1.6, rx=10))
    p.append(text(W/2, 338, "Зміна поколінь — не мить запису байтів, а мить, коли новий слот УПЕРШЕ сходиться за CRC й переважає за seq.",
                  size=10, color=INK, bold=True))
    p.append(text(W/2, 360, "Обрив живлення раніше — читач бачить старий цілий слот; пізніше — новий цілий; напівстану нема ніде.",
                  size=10, color=INK, bold=True))
    render(os.path.join(OUT, "ab-slot-swap.svg"), W, H, *p)


# ── seal-crc-hmac-sign: печатка запису — окрема вісь від логіки слотів ────────
# Ідея: та сама рамка «печатка над seq+data», три рівні захисту — від
# випадковості (CRC) до зловмисника без ключа (HMAC) й без приватного (підпис).
def fig_seal_crc_hmac_sign():
    W, H = 800, 384
    p = [text(W/2, 30, "Печатка запису: від захисту від випадковості до захисту від підробки", size=15.5, bold=True),
         text(W/2, 50, "логіка A/B-слотів і seq не змінюється — інша лише природа печатки над (seq + data)",
              size=10, color=MUTED, italic=True)]

    col_w = 236
    xs = [24, 282, 540]
    top = 78
    box_h = 258

    cols = [
        ("CRC-32", NEG, BLUEF, "лінійна контрольна сума",
         [("ловить", "випадкове псування", "недопис, збій біта, шум"),
          ("НЕ ловить", "зловмисну підробку", "хто керує даними — підбере CRC"),
          ("ключ", "не потрібен", "дешево, швидко")],
         "проти випадковості"),
        ("HMAC-SHA-256", WARN, WARNF, "хеш на СПІЛЬНОМУ ключі",
         [("ловить", "і випадкове, і підробку", "без ключа печатку не підробити"),
          ("ключ", "один спільний секрет", "у писача і в читача"),
          ("межа", "хто витягне ключ із чипа", "той зможе підробляти")],
         "довірений пристрій"),
        ("Підпис (пара ключів)", FIELD, GREENF, "приватний підписав, відкритий звірив",
         [("ловить", "і випадкове, і підробку", "приватний ключ лишає виробник"),
          ("ключ", "у пристрої лише ВІДКРИТИЙ", "ним не підробиш, лише звіриш"),
          ("це і є", "основа безпечного OTA", "образ приймаємо лише з підписом")],
         "виробник ↔ пристрій"),
    ]

    for x, (title, col, fill, sub, rows, foot) in zip(xs, cols):
        p.append(rect(x, top, col_w, box_h, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(x + col_w/2, top + 24, title, size=12, color=col, bold=True))
        p.append(text(x + col_w/2, top + 43, sub, size=8.5, color=MUTED, italic=True))
        yy = top + 62
        for tag, l1, l2 in rows:
            p.append(fitbox(x + 12, yy, 68, 36, tag, size=8.5, fill=BG, stroke=col, color=col, bold=True, rx=5))
            p.append(text(x + 88, yy + 14, l1, size=9, color=INK, anchor="start", bold=True))
            p.append(text(x + 88, yy + 29, l2, size=8, color=MUTED, anchor="start"))
            yy += 46
        p.append(fitbox(x + 22, top + box_h - 30, col_w - 44, 20, foot, size=9.5,
                        fill=BG, stroke=col, color=col, bold=True, rx=5))

    p.append(text(W/2, 366, "Атомарність від зникнення живлення й захист від підробки — незалежні осі: слоти й seq тримають першу, печатка — другу.",
                  size=10, color=INK, bold=True))
    render(os.path.join(OUT, "seal-crc-hmac-sign.svg"), W, H, *p)


if __name__ == "__main__":
    fig_volatile_vs_nv()
    fig_flash_write_cycle()
    fig_memory_lineage()
    fig_ab_slot_swap()
    fig_seal_crc_hmac_sign()
    print("figs.py: 5 SVG записано в", OUT)
