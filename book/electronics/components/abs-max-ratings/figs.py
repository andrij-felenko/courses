# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e0a32e"   # «прірва» — жовте попередження
AMBERBG = "#fff3e0"
REDBG   = "#fbecec"
GRNBG   = "#eef6ef"
BLUEBG  = "#e9eefb"


# ── two-tables: дві таблиці меж — знищення проти роботи ───────────────────────
# Ідея: Absolute Maximum і Recommended Operating стоять поруч у даташиті, схожі
# на вигляд, але кажуть протилежне. Ліва (червона) — межі виживання; права
# (зелена) — де гарантовано працює. Це дві РІЗНІ таблиці з різним сенсом.

def fig_two_tables():
    W, H = 720, 360
    p = []
    # ліва таблиця — Absolute Maximum (червона рамка)
    p.append(rect(40, 56, 320, 250, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(200, 82, "ABSOLUTE MAXIMUM", size=12, color=POS, bold=True))
    p.append(text(200, 100, "межа знищення — не переходь", size=9, color=INK))
    rows_l = [("Живлення", "6 В"), ("Напруга входу", "−0.3…Vcc+0.3"),
              ("Струм ніжки", "±40 мА"), ("Темп. кристала", "150 °C")]
    y = 130
    for name, val in rows_l:
        p.append(text(56, y, name, size=10, color=INK, anchor="start"))
        p.append(text(344, y, val, size=10, color=POS, anchor="end", bold=True))
        p.append(line(56, y + 12, 344, y + 12, color="#e0bcbc", sw=1))
        y += 38
    p.append(text(200, 296, "перейшов — прилад мертвий або скалічений",
                  size=9, color=POS, bold=True))
    # права таблиця — Recommended Operating (зелена рамка)
    p.append(rect(380, 56, 300, 250, fill=GRNBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(530, 82, "RECOMMENDED OPERATING", size=10, color=FIELD, bold=True))
    p.append(text(530, 100, "де працювати насправді", size=9, color=INK))
    rows_r = [("Живлення", "1.8…5.5 В"), ("Темп. роботи", "−40…85 °C")]
    y = 138
    for name, val in rows_r:
        p.append(text(396, y, name, size=10, color=INK, anchor="start"))
        p.append(text(664, y, val, size=10, color=FIELD, anchor="end", bold=True))
        p.append(line(396, y + 12, 664, y + 12, color="#bcd8c4", sw=1))
        y += 38
    p.append(text(530, 244, "тут гарантовані всі параметри", size=9, color=FIELD, bold=True))
    p.append(text(530, 264, "з таблиці Electrical Characteristics", size=9, color=INK))
    p.append(text(360, 344,
                  "Absolute Maximum — «не зруйнуй». Recommended — «працюй тут». Це різні таблиці.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "two-tables.svg"), W, H, *p,
           title="Дві таблиці меж: знищення проти роботи")


# ── cliff: шкала живлення — зелена зона, жовта прірва, червона риса ───────────
# Ідея: на одній осі напруги видно, що рекомендований діапазон (зелене)
# закінчується раніше за абсолютний максимум (червона риса), а між ними —
# вузька «прірва» (жовте), де ще живе, але нічого не гарантовано.

def fig_cliff():
    W, H = 700, 330
    ax0, ax1, ay = 80, 654, 230
    p = []
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    p.append(arrow(ax1 - 1, ay, ax1, ay, color=INK, sw=2))
    p.append(text(ax1 + 4, ay + 4, "Vcc (В)", size=10, color=INK, anchor="start", bold=True))
    # позначки 0..7 (80 px на вольт)
    for v in range(8):
        x = ax0 + v * 80
        p.append(line(x, ay, x, ay + 5, color=INK, sw=1.2))
        p.append(text(x, ay + 18, str(v), size=9, color=INK))
    # зони
    p.append(rect(ax0 + 1.8 * 80, 140, (5.5 - 1.8) * 80, 90, fill=GRNBG, stroke=FIELD, sw=1.4, rx=0))
    p.append(text(ax0 + 3.65 * 80, 178, "Recommended", size=10, color=FIELD, bold=True))
    p.append(text(ax0 + 3.65 * 80, 196, "усе гарантовано", size=9, color=INK))
    p.append(rect(ax0 + 5.5 * 80, 140, 0.5 * 80, 90, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=0))
    p.append(text(ax0 + 5.75 * 80, 130, "прірва", size=9, color=AMBER, bold=True))
    p.append(line(ax0 + 6 * 80, 118, ax0 + 6 * 80, ay, color=POS, sw=2.4, dash="5 4"))
    p.append(text(ax0 + 6 * 80 + 4, 112, "Abs Max 6 В", size=9, color=POS, anchor="start", bold=True))
    p.append(rect(ax0 + 6 * 80, 140, 80, 90, fill=REDBG, stroke=POS, sw=1.4, rx=0))
    p.append(text(ax0 + 6.5 * 80, 190, "руйнування", size=9, color=POS, bold=True))
    p.append(text(350, 298,
                  "У зеленому — усе як обіцяно. У жовтій прірві — може й працює, та нічого не гарантовано.",
                  size=9, color=INK))
    p.append(text(350, 316,
                  "За червоною межею прилад псується — часто незворотно, навіть від короткого дотику.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "cliff.svg"), W, H, *p,
           title="Прірва між «працює» і «гине»: напруга живлення")


# ── why-gap: чотири причини закладати зазор ──────────────────────────────────
# Ідея: рекомендований діапазон = абсолютний максимум мінус запас на чотири
# реальні речі (розкид партії, температура, старіння, надійність).

def fig_why_gap():
    W, H = 700, 296
    p = []
    rows = [("Розкид партії", "екземпляри різні; край гарантують із запасом"),
            ("Температура", "у спеку межі стискаються — потрібен буфер"),
            ("Старіння", "прилад слабшає з роками"),
            ("Надійність", "робота біля межі вкорочує життя, хай і «працює»")]
    y = 66
    for name, desc in rows:
        p.append(rect(56, y, 196, 38, fill=BLUEBG, stroke="#9bb0c2", sw=1.4, rx=6))
        p.append(text(154, y + 24, name, size=11, color=INK, bold=True))
        p.append(arrow(254, y + 19, 286, y + 19, color=MUTED, sw=2))
        p.append(text(298, y + 24, desc, size=10, color=INK, anchor="start"))
        y += 50
    p.append(text(350, 284,
                  "Recommended — це Abs Max мінус запас на все це. Жити треба в зеленому, не «майже на межі».",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "why-gap.svg"), W, H, *p,
           title="Навіщо прірва: запас на реальність")


# ── transient: коротка піка вище межі, хоч середнє низьке ─────────────────────
# Ідея: абсолютний максимум — про МИТТЄВЕ значення. Сигнал майже весь час
# низький, та один короткий сплеск переростає межу — і цього досить.

def fig_transient():
    W, H = 700, 300
    ox, oy = 80, 222
    base = oy - 48          # рівень «низького» сигналу
    maxline = 99            # червона риса Abs Max
    peak = 87               # вершина піки (вище за червону)
    p = []
    p.append(arrow(ox, oy, ox, 58, color=INK, sw=2))
    p.append(arrow(ox, oy, 654, oy, color=INK, sw=2))
    p.append(text(658, oy + 4, "час", size=13, color=INK, anchor="start", bold=True))
    p.append(text(ox - 4, 50, "напруга", size=13, color=INK, bold=True))
    p.append(line(ox, maxline, 640, maxline, color=POS, sw=1.6, dash="5 4"))
    p.append(text(636, maxline - 8, "Abs Max", size=9.5, color=POS, anchor="end", bold=True))
    # сигнал: пласка лінія з гострим сплеском у центрі
    pts = []
    for xi in range(0, 281):
        x = ox + xi * 2
        t = xi
        # гаусів сплеск навколо t=126
        bump = math.exp(-((t - 126) ** 2) / (2 * 9.0 ** 2))
        yv = base - (base - peak) * bump
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), NEG))
    p.append(circle(ox + 126 * 2, peak + 6, 5, fill=POS, stroke=BG, sw=2))
    p.append(text(ox + 126 * 2, peak - 6, "піка > межі!", size=9, color=POS, bold=True))
    p.append(text(ox + 146, base + 14, "середнє — низьке й безпечне…", size=9, color=INK, anchor="start"))
    p.append(text(350, 288,
                  "Сплеск (вмикання, ESD, гаряче підключення) на мить переростає Abs Max — і прилад мертвий.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "transient.svg"), W, H, *p,
           title="Коротка піка вбиває, хоч середнє в нормі")


# ── params: типові рядки таблиці Absolute Maximum ────────────────────────────
# Ідея: набір меж стандартний, варто знати його в обличчя; найпідступніша —
# напруга входу проти рейок живлення.

def fig_params():
    W, H = 700, 322
    p = []
    rows = [("Напруга живлення", "найбільше Vcc"),
            ("Напруга на входах", "часто −0.3…Vcc+0.3 В (інакше — латч-ап)"),
            ("Струм через ніжку", "скільки витримає вивід"),
            ("Потужність / темп. кристала Tj", "межа нагріву"),
            ("Температура зберігання", "ширша за робочу"),
            ("ESD", "стійкість до статичного розряду")]
    y = 64
    for name, desc in rows:
        p.append(rect(50, y, 260, 30, fill="#fdeeee", stroke="#d8a0a0", sw=1.3, rx=5))
        p.append(text(64, y + 20, name, size=10, color=INK, anchor="start", bold=True))
        p.append(text(326, y + 20, desc, size=9.5, color=INK, anchor="start"))
        y += 40
    p.append(text(350, 310,
                  "Жодну межу не можна переходити навіть на мить. Найпідступніша — напруга входу проти рейок.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "params.svg"), W, H, *p,
           title="Що зазвичай стоїть у Absolute Maximum")


# ── rule: три вкладені зони — цілься в серцевину ──────────────────────────────
# Ідея: проєктувати треба в зеленій серцевині (Recommended із запасом), жовту
# прірву лишати на аварії, червоного не торкатися ніколи.

def fig_rule():
    W, H = 680, 280
    p = []
    p.append(rect(60, 70, 560, 152, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(340, 92, "Absolute Maximum — ніколи не торкайся", size=11, color=POS, bold=True))
    p.append(rect(112, 108, 456, 98, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=8))
    p.append(text(340, 130, "прірва — «може й живе», не гарантовано", size=10, color="#b07d1e", bold=True))
    p.append(rect(172, 146, 336, 52, fill=GRNBG, stroke=FIELD, sw=1.6, rx=8))
    p.append(text(340, 176, "Recommended + запас — тут проєктуй", size=11, color=FIELD, bold=True))
    p.append(text(340, 266,
                  "Цілься в зелену серцевину із запасом; жовте лиши на аварії; червоного не торкайся ніколи.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "rule.svg"), W, H, *p,
           title="Правило проєктування: цілься в серцевину")


# ════════════════ фігури вставки comp-abs-max-failures ════════════════════════

# ── clamp-diodes: два захисні діоди на вході і коли вони відмикаються ─────────
# Ідея: на кожній ніжці — діод до Vcc і діод до GND; у межах рейок мовчать,
# за рейками відмикаються й пропускають струм, що його й обмежує рядок входу.

def fig_clamp_diodes():
    W, H = 700, 300
    cx = 300
    vcc_y, gnd_y, pin_y = 80, 240, 160
    p = []
    # рейки
    p.append(line(120, vcc_y, 480, vcc_y, color=POS, sw=2.4))
    p.append(text(110, vcc_y + 4, "Vcc", size=12, color=POS, anchor="end", bold=True))
    p.append(line(120, gnd_y, 480, gnd_y, color=NEG, sw=2.4))
    p.append(text(110, gnd_y + 4, "GND", size=12, color=NEG, anchor="end", bold=True))
    # вхідна ніжка
    p.append(line(120, pin_y, cx, pin_y, color=INK, sw=2))
    p.append(circle(120, pin_y, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(118, pin_y - 8, "вхід", size=11, color=INK, anchor="end", bold=True))
    p.append(line(cx, pin_y, 470, pin_y, color=INK, sw=2))
    p.append(rect(470, pin_y - 22, 92, 44, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(516, pin_y + 4, "логіка", size=11, color=INK, bold=True))
    # верхній діод (ніжка → Vcc), трикутник вістрям угору = провідність до Vcc
    p.append(line(cx, pin_y, cx, vcc_y + 6, color=INK, sw=1.6))
    p.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" fill="#fdecea" stroke="%s" stroke-width="1.5"/>'
             % (cx - 8, pin_y - 28, cx + 8, pin_y - 28, cx, pin_y - 44, POS))
    p.append(line(cx - 9, vcc_y + 6, cx + 9, vcc_y + 6, color=POS, sw=2))
    p.append(text(cx + 16, pin_y - 34, "вгору > Vcc+0.6 В", size=9, color=POS, anchor="start"))
    # нижній діод (GND → ніжка), вістрям угору
    p.append(line(cx, pin_y, cx, gnd_y - 6, color=INK, sw=1.6))
    p.append('<path d="M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f Z" fill="#eaf0fd" stroke="%s" stroke-width="1.5"/>'
             % (cx - 8, pin_y + 44, cx + 8, pin_y + 44, cx, pin_y + 28, NEG))
    p.append(line(cx - 9, pin_y + 44, cx + 9, pin_y + 44, color=NEG, sw=2))
    p.append(text(cx + 16, pin_y + 40, "вниз < −0.6 В", size=9, color=NEG, anchor="start"))
    p.append(text(350, 282,
                  "У межах 0…Vcc діоди мовчать. За рейками — відмикаються; струм крізь них і обмежує рядок входу.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "clamp-diodes.svg"), W, H, *p,
           title="Захисні діоди на вході — і коли вони відмикаються")


# ── latchup: паразитний тиристор замикає Vcc на GND ──────────────────────────
# Ідея: два паразитні біполярні транзистори в підкладці творять тиристорну
# петлю; інжектований струм її «вмикає» — і Vcc коротне на GND крізь кристал.

def fig_latchup():
    W, H = 700, 320
    p = []
    p.append(line(120, 70, 580, 70, color=POS, sw=2.4))
    p.append(text(110, 74, "Vcc", size=12, color=POS, anchor="end", bold=True))
    p.append(line(120, 260, 580, 260, color=NEG, sw=2.4))
    p.append(text(110, 264, "GND", size=12, color=NEG, anchor="end", bold=True))
    # два паразитні транзистори як рамки в петлі
    p.append(rect(250, 100, 90, 50, fill=REDBG, stroke=POS, sw=1.6, rx=6))
    p.append(text(295, 122, "PNP", size=11, color=POS, bold=True))
    p.append(text(295, 138, "паразит", size=9, color=INK))
    p.append(rect(360, 180, 90, 50, fill=BLUEBG, stroke=NEG, sw=1.6, rx=6))
    p.append(text(405, 202, "NPN", size=11, color=NEG, bold=True))
    p.append(text(405, 218, "паразит", size=9, color=INK))
    # петля зворотного зв'язку між ними
    p.append(arrow(340, 125, 360, 190, color=INK, sw=1.8))
    p.append(arrow(360, 205, 340, 145, color=INK, sw=1.8))
    p.append(text(355, 168, "петля", size=9, color=INK, anchor="start"))
    # з'єднання до рейок
    p.append(line(295, 100, 295, 70, color=POS, sw=2))
    p.append(line(405, 230, 405, 260, color=NEG, sw=2))
    # інжекція струму збоку
    p.append(arrow(180, 125, 248, 125, color=AMBER, sw=2.4))
    p.append(text(175, 121, "інжекція струму", size=9, color="#b07d1e", anchor="end", bold=True))
    p.append(text(175, 135, "(вхід / hot-plug)", size=9, color=MUTED, anchor="end"))
    # коротке замикання крізь кристал
    p.append(line(490, 70, 490, 260, color=POS, sw=2.6, dash="6 4"))
    p.append(text(498, 165, "коротке Vcc→GND", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(498, 180, "крізь кристал", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(350, 300,
                  "Струм «вмикає» петлю; коротке тримається саме, доки не зняти живлення. Не обмежиш — кристал вигоряє.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "latchup.svg"), W, H, *p,
           title="Латч-ап: паразитний тиристор замикає Vcc на GND")


# ── overvoltage: чотири шляхи вигнати вхід за рейки ──────────────────────────
# Ідея: різні рівні логіки, сигнал раніше за живлення, індуктивний викид,
# ємнісне перекидання при гарячому підключенні — усе відмикає захисний діод.

def fig_overvoltage():
    W, H = 700, 300
    p = []
    items = ["5 В на 3.3-вольтовий вхід",
             "сигнал раніше за живлення (рейка ще 0)",
             "індуктивний викид котушки / довгого дроту",
             "ємнісне перекидання при гарячому підключенні"]
    y = 66
    for i, s in enumerate(items, 1):
        p.append(rect(50, y, 470, 36, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=6))
        p.append(circle(72, y + 18, 12, fill=BG, stroke=AMBER, sw=1.6))
        p.append(text(72, y + 22, str(i), size=12, color="#b07d1e", bold=True))
        p.append(text(96, y + 22, s, size=10.5, color=INK, anchor="start"))
        p.append(arrow(524, y + 18, 556, y + 18, color=POS, sw=2))
        y += 50
    p.append(rect(556, 66, 110, 186, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(611, 150, "діод", size=11, color=POS, bold=True))
    p.append(text(611, 168, "відкрито", size=11, color=POS, bold=True))
    p.append(text(350, 282,
                  "Будь-який шлях відмикає захисний діод — і впорскує струм, що здатен запустити латч-ап.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "overvoltage.svg"), W, H, *p,
           title="Звідки береться перенапруга на вході")


# ── hotplug: що коїться в мить дотику роз'єму під напругою ────────────────────
# Ідея: сигнал може торкнутися раніше за землю, розряджені ємності тягнуть
# кидок струму, індуктивність кабелю дає викид — усі троє штовхають вхід за рейки.

def fig_hotplug():
    W, H = 700, 300
    p = []
    troubles = [("Порядок дотику", "сигнал торкнувся\nраніше за землю —\nчип ще «плаває»"),
                ("Кидок струму", "розряджені вхідні\nємності — мов\nкоротке замикання"),
                ("Викид напруги", "індуктивність\nкабелю дає сплеск\nпри кидку струму")]
    x = 40
    for name, desc in troubles:
        bx, bw = x, 200
        p.append(rect(bx, 60, bw, 40, fill=AMBERBG, stroke=AMBER, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, 85, name, size=11, color="#b07d1e", bold=True))
        p.append(fitbox(bx, 110, bw, 66, desc, size=10, fill=FILL, stroke="#cfd6dd"))
        p.append(arrow(bx + bw / 2, 180, bx + bw / 2, 206, color=POS, sw=2))
        x += bw + 20
    p.append(rect(40, 206, 620, 40, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(350, 231, "усі три штовхають вхід за рейки — знову за абсолютний максимум, з ризиком латч-апу",
                  size=10.5, color=POS, bold=True))
    p.append(text(350, 282,
                  "Тому на роз'ємах землю й живлення роблять довшими, а на лініях ставлять резистори й TVS.",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(OUT, "hotplug.svg"), W, H, *p,
           title="Гаряче підключення: що коїться в мить дотику")


if __name__ == "__main__":
    fig_two_tables(); fig_cliff(); fig_why_gap(); fig_transient(); fig_params(); fig_rule()
    fig_clamp_diodes(); fig_latchup(); fig_overvoltage(); fig_hotplug()
    print("figs.py: 10 SVG згенеровано в", OUT)
