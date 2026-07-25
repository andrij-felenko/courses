# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Семантичні кольори символів (єдині на всі фігури теми)
DATA_F, DATA_S = "#eaf0ff", NEG          # дані — холодні
PAR_F,  PAR_S  = "#eef7ef", FIELD        # контроль — зелені
BAD_F,  BAD_S  = "#fdeceb", POS          # биті — гарячі


# ── symbols: пакет б'є багато сусідніх БІТІВ, але лише кілька СИМВОЛІВ ──────────
# Ідея: одиниця обліку RS — символ (байт), а не біт. Суцільний пакет накриває
# смугу бітів, та лягає лише в кілька сусідніх символів — їх RS і вертає.

def fig_symbols():
    W, H = 760, 300
    x0, y0 = 40, 92
    sw, sh, gap = 52, 44, 6
    ndata, npar = 9, 3
    bad = {4, 5}
    p = []

    def cell(i, label, f, s, color):
        x = x0 + i * (sw + gap)
        out = rect(x, y0, sw, sh, fill=f, stroke=s, sw=2.0 if color is POS else 1.4, rx=5)
        out += text(x + sw / 2, y0 + sh / 2 + 5, label, size=13, color=color, bold=True)
        return out

    for i in range(ndata):
        f, s, c = (BAD_F, BAD_S, POS) if i in bad else (DATA_F, DATA_S, NEG)
        p.append(cell(i, "S%d" % i, f, s, c))
    for j in range(npar):
        p.append(cell(ndata + j, "p", PAR_F, PAR_S, FIELD))

    p.append(text(x0, y0 - 14, "дані: символи S0…S8", size=12, color=NEG, anchor="start", bold=True))
    px0 = x0 + ndata * (sw + gap)
    p.append(text(px0, y0 - 14, "контроль", size=12, color=FIELD, anchor="start", bold=True))

    bx0 = x0 + min(bad) * (sw + gap) - 4
    bx1 = x0 + max(bad) * (sw + gap) + sw + 4
    p.append(rect(bx0, y0 - 6, bx1 - bx0, sh + 12, fill="none", stroke=POS, sw=2.2, rx=6))
    p.append(text((bx0 + bx1) / 2, y0 + sh + 28, "пакет: подряпина / завмирання", size=12, color=POS, bold=True))

    by = y0 + sh + 66
    p.append(text(x0, by - 10, "ті самі 16 бітів поспіль — багато бітів, мало символів:", size=12, color=INK, anchor="start"))
    bw = 11
    for k in range(48):
        bx = x0 + k * (bw + 2)
        in_burst = 32 <= k < 48
        f = POS if in_burst else MUTED
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="14" rx="1" fill="%s"/>' % (bx, by, bw, f))
    p.append(text(x0 + 40 * (bw + 2), by + 34,
                  "16 бітів поспіль → лише 2 биті символи (S4, S5)", size=12, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT, "symbols.svg"), W, H, *p)


# ── link-budget: три факти далекого зв'язку → потрібна пряма корекція ──────────
def fig_link_budget():
    W, H = 760, 340
    p = []
    # Земля ↔ апарат, сигнал слабне (затухання дуги)
    ey, ax, axx = 110, 80, 690
    p.append(circle(ax, ey, 22, fill=DATA_F, stroke=NEG, sw=2.2))
    p.append(text(ax, ey + 4, "Земля", size=11, color=NEG, bold=True))
    p.append(rect(axx - 14, ey - 10, 28, 20, fill=FILL, stroke=INK, sw=2, rx=3))
    p.append(line(axx, ey - 10, axx, ey - 30, color=INK, sw=2))
    p.append('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (axx - 20, ey - 30, axx, ey - 50, axx + 20, ey - 30, INK))
    p.append(text(axx, ey + 28, "апарат", size=11, color=INK, bold=True))
    # хвилі, що слабнуть
    for i in range(7):
        cx = ax + 70 + i * 80
        op = 1.0 - i * 0.13
        p.append('<path d="M%d,%d A 40 40 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="2.2" opacity="%.2f"/>'
                 % (cx, ey - 38, cx, ey + 38, NEG, op))
    p.append(text((ax + axx) / 2, ey - 56, "мільярди кілометрів — сигнал слабне", size=11, color=MUTED, italic=True))

    # три факти-картки
    cards = [
        ("Сигнал — слабший за подих", POS,
         "Передавач — як лампочка (близько 20 Вт).\nЗа мільярди км до антени долітають крихти\nенергії — на самій межі шуму."),
        ("Перепитати — не варіант", "#caa24a",
         "Радіохвиля йде в один бік годинами.\nЗапит «повтори» вертався б добу й довше —\nдіалог із підтвердженням тут марний."),
        ("Тож лагодимо на місці", FIELD,
         "Раз перепитати не можна — приймач мусить\nвиправити з того, що прийшло. Для цього\nв потік наперед домішують надлишок."),
    ]
    cw, ch, cy, gx = 232, 130, 180, 20
    for i, (title, col, body) in enumerate(cards):
        cx = 30 + i * (cw + gx)
        p.append(rect(cx, cy, cw, ch, fill=BG, stroke=col, sw=2.2, rx=10))
        p.append(rect(cx, cy, cw, 7, fill=col, stroke=col, sw=0, rx=0))
        p.append(text(cx + cw / 2, cy + 30, title, size=13, color=col, bold=True))
        p.append(mtext(cx + cw / 2, cy + 54, body, size=10.5, color=INK))

    render(os.path.join(OUT, "link-budget.svg"), W, H, *p)


# ── concatenation: каскад — зовнішній RS + внутрішній згортковий ───────────────
def fig_concatenation():
    W, H = 860, 360
    p = []

    def stage(x, y, w, label, col, sub):
        out = rect(x, y, w, 48, fill=BG if col is INK else (col + "14"), stroke=col, sw=2.2, rx=8)
        out += text(x + w / 2, y + 20, label, size=12, color=col, bold=True)
        out += text(x + w / 2, y + 38, sub, size=10, color=MUTED)
        return out

    # борт: дані → RS (зовн.) → згортковий (внутр.) → канал
    y1 = 78
    xs = 30
    p.append(text(xs, y1 - 12, "на борту — два шари захисту:", size=12, color=INK, anchor="start", bold=True))
    p.append(stage(xs, y1, 120, "дані", INK, "знімки, виміри"))
    p.append(arrow(xs + 122, y1 + 24, xs + 150, y1 + 24, color=INK))
    p.append(stage(xs + 152, y1, 200, "зовнішній: Рід–Соломон", POS, "RS(255,223), символи"))
    p.append(arrow(xs + 354, y1 + 24, xs + 382, y1 + 24, color=INK))
    p.append(stage(xs + 384, y1, 190, "внутрішній: згортковий", NEG, "поверх RS"))
    p.append(arrow(xs + 576, y1 + 24, xs + 604, y1 + 24, color=INK))
    p.append(stage(xs + 606, y1, 150, "канал →", "#caa24a", "шум + сплески"))

    # канал: смуга символів з рідким шумом і сплеском
    cy = 180
    p.append(text(xs, cy - 10, "у каналі: поодинокі похибки + зрідка цілий сплеск", size=11, color="#caa24a", anchor="start", bold=True))
    bw = 13
    burst = set(range(38, 46))
    spo = {7, 22, 31}
    for k in range(54):
        bx = xs + k * (bw + 2)
        f = POS if (k in burst or k in spo) else FIELD
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="2" fill="%s"/>' % (bx, cy, bw, f))
    p.append(text(xs + 42 * (bw + 2), cy - 10, "← сплеск", size=10.5, color=POS, anchor="middle", bold=True))

    # земля: декодери у зворотному порядку
    y2 = 248
    p.append(text(xs, y2 - 12, "на Землі — знімаємо шари у зворотному порядку:", size=12, color=INK, anchor="start", bold=True))
    p.append(stage(xs, y2, 200, "декодер Вітербі", NEG, "гасить рідкий шум"))
    p.append(arrow(xs + 202, y2 + 24, xs + 230, y2 + 24, color=INK))
    p.append(stage(xs + 232, y2, 220, "декодер Рід–Соломона", POS, "замітає сплески символів"))
    p.append(arrow(xs + 454, y2 + 24, xs + 482, y2 + 24, color=FIELD))
    p.append(stage(xs + 484, y2, 180, "чисті дані", FIELD, "знімок без діри"))

    # підказка про серії Вітербі
    p.append(text(W / 2, y2 + 86, "Вітербі, спіткнувшись, лишає по собі сплеск — саме його й замітає Рід–Соломон.",
                  size=11, color=INK))

    render(os.path.join(OUT, "concatenation.svg"), W, H, *p)


# ── burst: той самий сплеск очима бітового й символьного коду ──────────────────
def fig_burst():
    W, H = 820, 400
    p = []
    bw = 13
    burst = set(range(10, 22))      # сплеск завдовжки 12 «елементів»

    # верх: бітовий код
    yb = 70
    p.append(text(30, yb - 14, "код, що рахує БІТАМИ (як Геммінг (7,4)): межа — 1 биток на блок",
                  size=12, color=NEG, anchor="start", bold=True))
    nb = 50
    for k in range(nb):
        bx = 40 + k * (bw + 2)
        f = POS if k in burst else DATA_F
        s = BAD_S if k in burst else DATA_S
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="26" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>'
                 % (bx, yb, bw, f, s))
    p.append(line(40 + min(burst) * (bw + 2), yb - 8, 40 + (max(burst) + 1) * (bw + 2) - 2, yb - 8, color=POS, sw=2))
    p.append(text(40 + 16 * (bw + 2), yb - 14 + 0, "сплеск", size=10.5, color=POS, anchor="middle", bold=True))
    p.append(rect(560, yb + 44, 230, 36, fill=BAD_F, stroke=BAD_S, sw=2.2, rx=8))
    p.append(text(675, yb + 67, "блок втрачено — діра в даних", size=11.5, color=POS, bold=True))
    p.append(text(40, yb + 60, "стелю пробито багаторазово — код безпорадний.", size=11, color=INK, anchor="start"))

    # низ: символьний код
    ys = 230
    p.append(text(30, ys - 14, "Рід–Соломон рахує СИМВОЛАМИ (байтами): той самий сплеск — лише кілька символів",
                  size=12, color=POS, anchor="start", bold=True))
    nsym, symw, symgap = 8, 80, 8
    bad_sym = {2, 3}
    for i in range(nsym):
        x = 40 + i * (symw + symgap)
        f, s, c = (BAD_F, BAD_S, POS) if i in bad_sym else (PAR_F, PAR_S, FIELD)
        p.append(rect(x, ys, symw, 38, fill=f, stroke=s, sw=2.0, rx=4))
        p.append(text(x + symw / 2, ys + 23, "символ %d" % i, size=10.5, color=c, bold=True))
    p.append(rect(560, ys + 64, 230, 36, fill="#eafaee", stroke=FIELD, sw=2.4, rx=8))
    p.append(text(675, ys + 87, "символи відновлено — дані цілі", size=11.5, color=FIELD, bold=True))
    p.append(text(40, ys + 82, "сплеск ліг у кілька сусідніх символів; RS вертає до межі (RS(255,223) — 16 символів).",
                  size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "burst.svg"), W, H, *p)


# ── credit: чотири ланки — код, декодер, каскад, політ ─────────────────────────
def fig_credit():
    W, H = 860, 320
    p = []
    cols = [POS, NEG, "#caa24a", FIELD]
    items = [
        ("Рід і Соломон, 1960", "Lincoln Lab, MIT",
         "дали сам КОД:\nлічити символами,\nа не бітами"),
        ("Берлекамп, Мессі\nта інші, ~1969", "+ Пітерсон",
         "швидкий ДЕКОДЕР —\nбез нього код\nзанадто важкий"),
        ("Форні: теорія\nкаскадів", "concatenated code",
         "як скласти два\nкоди шарами —\nоснова схеми"),
        ("JPL і NASA", "інженери",
         "звели все в\nреальний радіо-\nзв'язок — і він\nпрацює досі"),
    ]
    cw, ch, gx, y = 192, 200, 24, 80
    for i, (title, who, body) in enumerate(items):
        x = 24 + i * (cw + gx)
        p.append(rect(x, y, cw, ch, fill=BG, stroke=cols[i], sw=2.4, rx=10))
        p.append(rect(x, y, cw, 8, fill=cols[i], stroke=cols[i], sw=0))
        p.append(mtext(x + cw / 2, y + 36, title, size=12.5, color=INK, bold=True))
        p.append(text(x + cw / 2, y + 78, who, size=10, color=MUTED, italic=True))
        p.append(mtext(x + cw / 2, y + 104, body, size=10.5, color=cols[i]))
        if i < 3:
            ax = x + cw + 2
            p.append(arrow(ax, y + ch / 2, ax + 20, y + ch / 2, color=INK))

    p.append(text(W / 2, 50, "Жодного одинокого генія — чотири незамінні ланки", size=13, color=INK, bold=True))
    render(os.path.join(OUT, "credit.svg"), W, H, *p)


# ── poly-oversample: дані = крива, кодове слово = її відліки в n точках ─────────
# Ідея detailed-версії: k символів даних задають криву степеня k−1; кодове слово —
# її значення в n точках. Будь-яких k досить, зайві n−k — надлишок; відлік поза
# кривою — помилка, яку видно, бо низька крива лишається єдиною під більшістю точок.

def fig_poly_oversample():
    W, H = 780, 380
    p = []
    x0, xw = 90, 82                       # px(i) = x0 + i*xw, i = 0..7
    baseY = 300

    def px(i):
        return x0 + i * xw

    def val(t):
        return 40 + 9.0 * (t - 3.5) ** 2

    def py(t):
        return baseY - val(t)

    # осі — єдині <line>-елементи; текст тримаємо осторонь них
    p.append(line(70, 70, 70, baseY, color=MUTED, sw=1.6))
    p.append(line(70, baseY, 730, baseY, color=MUTED, sw=1.6))
    p.append(text(78, 90, "значення символу", size=12, color=MUTED, anchor="start"))
    p.append(text(726, baseY + 22, "точки передавання →", size=12, color=MUTED, anchor="end"))

    # крива степеня k−1 (парабола) — <path>, тож перевірку перетину не зачіпає
    pts = []
    t = 0.0
    while t <= 7.0001:
        pts.append((px(t), py(t)))
        t += 0.1
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % q for q in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))

    data_i = {0, 1, 2}
    err_i = 5
    for i in range(8):
        cx = px(i)
        if i == err_i:
            ty = py(i)                                  # справжнє місце — на кривій
            p.append(circle(cx, ty, 6, fill=BG, stroke=MUTED, sw=1.6))
            ey = ty - 64                                # збитий відлік — над кривою
            p.append(line(cx, ty - 6, cx, ey + 7, color=POS, sw=1.5, dash="4 3"))
            p.append(circle(cx, ey, 7, fill=BAD_F, stroke=BAD_S, sw=2.4))
        elif i in data_i:
            p.append(circle(cx, py(i), 7, fill=DATA_F, stroke=DATA_S, sw=2.2))
        else:
            p.append(circle(cx, py(i), 7, fill=PAR_F, stroke=PAR_S, sw=2.2))

    p.append(text(px(3.5), py(3.5) + 30, "крива степеня k−1", size=12, color=INK, bold=True))
    p.append(text(px(err_i) + 14, py(err_i) - 60, "помилка", size=12, color=POS, anchor="start", bold=True))

    # легенда — три позначки, добре рознесені
    ly = 96

    def leg(x, f, s, label, col):
        out = circle(x, ly, 7, fill=f, stroke=s, sw=2.2)
        out += text(x + 14, ly + 4, label, size=12, color=col, anchor="start")
        return out

    p.append(leg(300, DATA_F, DATA_S, "дані (будь-які k)", NEG))
    p.append(leg(470, PAR_F, PAR_S, "надлишок (n−k)", FIELD))
    p.append(leg(628, BAD_F, BAD_S, "збитий", POS))

    render(os.path.join(OUT, "poly-oversample.svg"), W, H, *p)


# ── decode-pipeline: чотири кроки декодера RS ──────────────────────────────────
def fig_decode_pipeline():
    W, H = 1000, 300
    y = 120
    p = []

    def stage(x, w, title, col, sub):
        fillc = BG if col is INK else (col + "14")
        out = rect(x, y, w, 56, fill=fillc, stroke=col, sw=2.2, rx=8)
        out += text(x + w / 2, y + 23, title, size=12, color=col, bold=True)
        out += text(x + w / 2, y + 42, sub, size=10, color=MUTED)
        return out

    stages = [
        ("прийняте r(x)", INK, "c(x) + помилка", 118),
        ("синдроми r(αʲ)", NEG, "лише помилка", 140),
        ("Берлекамп–Мессі", POS, "локатор Λ(x)", 165),
        ("пошук Чієна", "#caa24a", "позиції", 120),
        ("формула Форні", FIELD, "величини", 130),
        ("виправлене c(x)", INK, "помилку знято", 130),
    ]
    x = 22
    for idx, (ttl, col, sub, w) in enumerate(stages):
        p.append(stage(x, w, ttl, col, sub))
        x += w
        if idx < len(stages) - 1:
            p.append(arrow(x + 3, y + 28, x + 25, y + 28, color=INK))
            x += 28

    p.append(text(W / 2, 70, "синдроми залежать лише від помилки, а не від даних — на цьому стоїть увесь декодер",
                  size=12, color=INK))
    p.append(text(W / 2, 232, "чотири кроки — і символьні помилки зняті до межі коду t = (n−k)/2",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, "decode-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_symbols()
    fig_link_budget()
    fig_concatenation()
    fig_burst()
    fig_credit()
    fig_poly_oversample()
    fig_decode_pipeline()
    print("ok: symbols, link-budget, concatenation, burst, credit, poly-oversample, decode-pipeline")
