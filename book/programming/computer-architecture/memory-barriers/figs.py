# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── reorder: чому запис і наступне читання можуть «помінятися» ────────────────
# Ідея: програма пише в керівний регістр, тоді читає стан. У пам'яті-моделі це
# порядок-підказка, а не наказ. Апаратура (буфер запису, конвеєр) має право
# випустити читання РАНІШЕ, ніж запис дійшов до пристрою — і код бачить старе.
def fig_reorder():
    W, H = 760, 360
    p = []

    def col(x, title, a1, a2, tint):
        out = []
        cw = 250
        out.append(rect(x, 70, cw, 250, fill="#fbfcfd", stroke="#c7ccd2", sw=1.4))
        out.append(text(x + cw / 2, 92, title, size=13, color=INK, bold=True))
        # інструкція 1
        out.append(rect(x + 22, 116, cw - 44, 54, fill=tint[0], stroke=tint[2], sw=1.6, rx=5))
        for i, ln in enumerate(a1):
            out.append(text(x + cw / 2, 137 + i * 16, ln, size=11,
                            color=INK, bold=(i == 0)))
        # інструкція 2
        out.append(rect(x + 22, 196, cw - 44, 54, fill=tint[1], stroke=tint[3], sw=1.6, rx=5))
        for i, ln in enumerate(a2):
            out.append(text(x + cw / 2, 217 + i * 16, ln, size=11,
                            color=INK, bold=(i == 0)))
        return out, x + cw / 2, cw

    left, lx, cw = col(40, "як написано в коді",
                       ["STR  R1, [CTRL]", "увімкнути пристрій"],
                       ["LDR  R2, [STATUS]", "прочитати стан"],
                       ("#eef4ff", "#eafaf0", NEG, FIELD))
    p += left
    # стрілка «згори вниз — порядок програми»
    p.append(arrow(lx, 172, lx, 194, color=NEG, sw=1.8))

    right, rx, _ = col(470, "що дозволила апаратура",
                       ["LDR  R2, [STATUS]", "читання випустили ПЕРШИМ"],
                       ["STR  R1, [CTRL]", "запис ще в буфері…"],
                       ("#fbeeee", "#fbeeee", POS, POS))
    p += right
    p.append(arrow(rx, 172, rx, 194, color=POS, sw=1.8))

    # велика стрілка «дозволено переставити» між колонками
    p.append(arrow(40 + cw + 8, 195, 470 - 8, 195, color=MUTED, sw=2.2))
    p.append(text((40 + cw + 470) / 2, 183, "модель пам'яті", size=10, color=MUTED, bold=True))
    p.append(text((40 + cw + 470) / 2, 213, "дозволяє переставити", size=10, color=MUTED))

    p.append(text(W / 2, 345,
                  "R2 дістав СТАРИЙ стан — пристрій ще не ввімкнувся: порядок у коді був підказкою, не наказом",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "reorder.svg"), W, H, *p,
           title="Порядок у коді — не порядок у залізі")


# ── three: три бар'єри як три різні гарантії ─────────────────────────────────
# Ідея: DMB упорядковує лише пам'ять між собою; DSB чекає, поки пам'ять реально
# завершиться, і аж тоді пускає будь-які команди; ISB викидає конвеєр і
# перечитує команди наново. Три різні «стіни» різної сили.
def fig_three():
    W, H = 760, 430
    p = []

    rows = [
        (90, "DMB", NEG, "#eef4ff",
         "упорядкувати пам'ять",
         "усі доступи до пам'яті ДО бар'єра стають видимі перед доступами ПІСЛЯ.",
         "Не-пам'ятні команди можуть бігти вперед. Нічого не «чекає»."),
        (210, "DSB", FIELD, "#eafaf0",
         "дочекатися пам'яті",
         "як DMB, але ЖОДНА наступна команда не почнеться, доки всі доступи ДО бар'єра",
         "реально не завершаться (запис дійшов до пристрою, кеш/TLB прибрані)."),
        (330, "ISB", POS, "#fbeeee",
         "перечитати команди",
         "викинути вже вибрані команди з конвеєра й вибрати наступні НАНОВО —",
         "щоб зміна керівних регістрів (CONTROL, VTOR, CPACR) справді подіяла."),
    ]
    for y, name, c, tint, cap, l1, l2 in rows:
        p.append(rect(40, y, 150, 92, fill=tint, stroke=c, sw=2.0, rx=6))
        p.append(text(115, y + 40, name, size=22, color=INK, bold=True))
        p.append(text(115, y + 66, cap, size=10.5, color=c, bold=True))
        p.append(rect(210, y, 510, 92, fill="#fbfcfd", stroke="#c7ccd2", sw=1.3, rx=6))
        p.append(text(465, y + 40, l1, size=11.5, color=INK, anchor="middle"))
        p.append(text(465, y + 62, l2, size=11.5, color=INK, anchor="middle"))

    # шкала сили збоку
    p.append(text(W / 2, 418,
                  "сила зростає: DMB тільки впорядковує → DSB ще й чекає завершення → ISB ще й скидає конвеєр",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "three-barriers.svg"), W, H, *p,
           title="Три бар'єри — три різні гарантії")


# ── nvic: чому потрібні DSB+ISB після вимкнення переривання ───────────────────
# Ідея: запис у NVIC, що вимикає переривання, «в дорозі». Без бар'єра наступні
# команди (аж до дозволу переривань) біжать, і переривання ще встигає влетіти.
# DSB дочекався, поки вимкнення дійшло; ISB пересвідчився, що далі йде вже
# новий стан.
def fig_nvic():
    W, H = 760, 360
    p = []

    lane = 300
    y0 = 120
    # доріжка часу
    p.append(line(40, y0, 720, y0, color="#c7ccd2", sw=1.4))
    p.append(arrow(700, y0, 720, y0, color="#c7ccd2", sw=1.4))
    p.append(text(730, y0 + 4, "час", size=10, color=MUTED, anchor="start"))

    def evt(x, y, s, c, tint, w=150, dash=None):
        out = []
        out.append(rect(x, y, w, 40, fill=tint, stroke=c, sw=1.7, rx=5, ))
        out.append(text(x + w / 2, y + 24, s, size=11, color=INK, bold=True))
        out.append(line(x + w / 2, y + 40, x + w / 2, y0, color=c, sw=1.3, dash="3 3"))
        return out

    # БЕЗ бар'єра (вгорі)
    p.append(text(40, 60, "БЕЗ бар'єра", size=12, color=POS, bold=True, anchor="start"))
    p += evt(40, 70, "STR → вимкнути", NEG, "#eef4ff", w=150)
    p += evt(250, 70, "наступні команди", MUTED, "#f4f6f8", w=150)
    # переривання влітає, бо запис ще в дорозі
    p.append(rect(430, 70, 150, 40, fill="#fbeeee", stroke=POS, sw=1.8, rx=5))
    p.append(text(505, 94, "⚡ ISR усе одно влетів", size=10.5, color=POS, bold=True))
    p.append(line(505, 110, 505, y0, color=POS, sw=1.3, dash="3 3"))
    p.append(text(505, y0 + 20, "запис ще «в дорозі»", size=9.5, color=POS))

    # З бар'єром (внизу)
    yb = 210
    p.append(text(40, yb - 6, "З DSB+ISB", size=12, color=FIELD, bold=True, anchor="start"))
    p += evt(40, yb, "STR → вимкнути", NEG, "#eef4ff", w=140)
    p.append(rect(200, yb, 120, 40, fill="#eafaf0", stroke=FIELD, sw=1.9, rx=5))
    p.append(text(260, yb + 18, "DSB", size=12, color=INK, bold=True))
    p.append(text(260, yb + 33, "дочекався", size=9, color=FIELD))
    p.append(rect(340, yb, 110, 40, fill="#fbeeee", stroke=POS, sw=1.9, rx=5))
    p.append(text(395, yb + 18, "ISB", size=12, color=INK, bold=True))
    p.append(text(395, yb + 33, "перечитав", size=9, color=POS))
    p += evt(470, yb, "наступні команди", MUTED, "#f4f6f8", w=150)
    p.append(text(545, yb + 58, "переривання вже справді вимкнене", size=9.5, color=FIELD))

    render(os.path.join(OUT, "nvic-barrier.svg"), W, H, *p,
           title="Навіщо DSB+ISB після вимкнення переривання")


# ── smc: самозмінний код провалюється у дві незалежні щілини ─────────────────
# Ідея: три доріжки. Без бар'єрів — байти ще в буфері, конвеєр тримає старе:
# виконується старе/сміття. Є DSB, нема ISB — дані в RAM, але конвеєр старий:
# усе одно старе. DSB, потім ISB — дані осіли, конвеєр перечитано: нове тіло.
def fig_smc():
    W, H = 812, 430
    p = []

    label_x = 168
    bx = 240          # ліва межа блоків-подій
    bw = 116          # ширина блоку
    gap = 10

    def blk(x, y, s, sub, c, tint, w=bw):
        out = [rect(x, y, w, 46, fill=tint, stroke=c, sw=1.7, rx=5)]
        out.append(text(x + w / 2, y + 21, s, size=11, color=INK, bold=True))
        out.append(text(x + w / 2, y + 37, sub, size=8.5, color=c))
        return out

    def verdict(x, y, s, c):
        return list(blk(x, y, s.split("|")[0], s.split("|")[1], c,
                        "#fbeeee" if c == POS else "#eafaf0", w=150))

    rows = [
        (60, "без бар'єрів", POS,
         [("memcpy", "пише нове", NEG, "#eef4ff"),
          ("буфер запису", "байти ще тут", MUTED, "#f4f6f8"),
          ("конвеєр", "старі команди", MUTED, "#f4f6f8")],
         "стрибок → СТАРЕ|тіло або сміття"),
        (185, "DSB, немає ISB", POS,
         [("memcpy", "пише нове", NEG, "#eef4ff"),
          ("DSB", "дані в RAM", FIELD, "#eafaf0"),
          ("конвеєр", "досі старий", POS, "#fbeeee")],
         "стрибок → все|одно СТАРЕ"),
        (310, "DSB, потім ISB", FIELD,
         [("memcpy", "пише нове", NEG, "#eef4ff"),
          ("DSB", "дані в RAM", FIELD, "#eafaf0"),
          ("ISB", "перечитав", FIELD, "#eafaf0")],
         "стрибок → НОВЕ|тіло"),
    ]
    for y, cap, cc, cells, verd in rows:
        p.append(text(label_x, y + 26, cap, size=11.5, color=cc, bold=True, anchor="end"))
        x = bx
        for i, (s, sub, c, tint) in enumerate(cells):
            p += blk(x, y, s, sub, c, tint)
            if i < len(cells) - 1:
                p.append(arrow(x + bw, y + 23, x + bw + gap, y + 23, color=MUTED, sw=1.6))
            x += bw + gap
        p += verdict(x + 6, y, verd, POS if "НОВЕ" not in verd else FIELD)

    # правий підпис-поділ праці
    p.append(text(W / 2, 405,
                  "DSB лагодить ДАНІ (байти осідають у RAM) · ISB лагодить КОНВЕЄР (старі вибрані команди — геть)",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "smc-pipeline.svg"), W, H, *p,
           title="Самозмінний код: дві щілини, два бар'єри")


fig_reorder()
fig_three()
fig_nvic()
fig_smc()
print("ok")
