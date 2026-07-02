# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── module-anatomy: що ховається під металевим екраном ────────────────────────
# Ідея: голий чіп не працює сам; модуль додає кварц, Flash, RF-узгодження й
# розв'язку, накриває все екраном, а антену виносить у вільну від міді зону.

def fig_module_anatomy():
    W, H = 920, 470
    p = []

    # зовнішня плата модуля
    p.append(rect(70, 90, 780, 300, fill="#f6f4ee", stroke=INK, sw=2.2, rx=10))
    p.append(text(80, 80, "модуль (WROOM / WROVER-клас)", size=11, color=MUTED,
                  anchor="start", bold=True))

    # зона антени (без міді) праворуч
    p.append(rect(690, 90, 160, 300, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=0))
    p.append(text(770, 116, "зона антени", size=11, color=FIELD, bold=True))
    p.append(text(770, 134, "(без міді під нею)", size=10, color=FIELD))
    p.append('<path d="M 708,206 v -38 h 18 v 38 h 18 v -38 h 18 v 38 h 18 v -38 '
             'h 18 v 38 h 18 v -38 h 18" fill="none" stroke="%s" stroke-width="2.4"/>' % FIELD)
    p.append(text(770, 360, "PCB-антена", size=10, color=FIELD))

    # металевий екран над начинкою
    p.append(rect(70, 90, 620, 300, fill="#e9ebf0", stroke=MUTED, sw=1.6, rx=10))
    p.append(text(90, 116, "металевий екран (shield can)", size=11, color=INK,
                  anchor="start", bold=True))
    p.append(text(90, 134, "тримає випромінювання всередині", size=10, color=MUTED,
                  anchor="start"))

    # начинка під екраном
    p.append(rect(150, 210, 120, 120, fill="#2b2b2b", stroke="#000000", sw=1.2, rx=6))
    p.append(text(210, 272, "ESP32", size=12, color="#ffffff", bold=True))
    p.append(text(210, 290, "кристал у QFN", size=10, color="#cfd6e6"))

    p.append(fitbox(310, 210, 130, 52, "Flash (SPI)\nкод", size=11, bold=True,
                    fill="#fdf0e6", stroke="#c07a2e", color="#9a5a1e"))
    p.append(fitbox(310, 278, 130, 52, "кварц 40 МГц", size=11, bold=True,
                    fill="#e9eefb", stroke=NEG, color=NEG))
    p.append(fitbox(470, 210, 150, 52, "RF-узгодження\nдо антени", size=11, bold=True,
                    fill="#eef6ef", stroke=FIELD, color=FIELD))
    p.append(fitbox(470, 278, 150, 52, "розв'язка\nживлення", size=11, bold=True,
                    fill="#e4e4e4", stroke=MUTED, color=INK))

    # крайові напівотвори знизу
    for i in range(11):
        bx = 150 + i * 46
        p.append(rect(bx, 384, 16, 12, fill="#9a9aa0", stroke="#666666", sw=0.8, rx=2))
    p.append(text(W / 2, 430, "напівотвори по краю (castellated) — ними модуль паяють на твою плату",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "module-anatomy.svg"), W, H, *p,
           title="Що ховається під металевим екраном модуля")


# ── certification: готовий модуль успадковує дозвіл, голий чіп — повна процедура ─
# Ідея: будь-який передавач треба сертифікувати; модуль уже має FCC/CE/IC, тож
# виріб успадковує дозвіл, а голий чіп веде на повну процедуру власним коштом.

def fig_certification():
    W, H = 900, 430
    p = []

    # ліва колонка — готовий модуль
    p.append(rect(60, 80, 360, 300, fill="#fbfdfb", stroke=FIELD, sw=2, rx=12))
    p.append(text(240, 110, "Береш готовий модуль", size=14, color=FIELD, bold=True))
    rows_ok = ["модуль уже має FCC / CE / IC",
               "виробник пройшов випроби радіо",
               "твій виріб успадковує дозвіл",
               "на ринок — швидко й дешево"]
    for i, r in enumerate(rows_ok):
        cy = 150 + i * 42
        p.append(plus(86, cy, r=8))
        p.append(text(108, cy + 4, r, size=11, color=INK, anchor="start"))
    p.append(fitbox(86, 332, 308, 32, "FCC ID на корпусі = квиток на ринок",
                    size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD))

    # права колонка — голий чіп
    p.append(rect(480, 80, 360, 300, fill="#fffafa", stroke=POS, sw=2, rx=12))
    p.append(text(660, 110, "Береш голий чіп + свою антену", size=13, color=POS, bold=True))
    rows_bad = ["сам проєктуєш ВЧ-тракт і антену",
                "сам ідеш на повну сертифікацію",
                "лабораторія, місяці, чималі гроші",
                "ризик не пройти з першого разу"]
    for i, r in enumerate(rows_bad):
        cy = 150 + i * 42
        p.append(minus(508, cy, r=8))
        p.append(text(528, cy + 4, r, size=11, color=INK, anchor="start"))
    p.append(fitbox(506, 332, 308, 32, "виправдано лише на великому масштабі",
                    size=11, bold=True, fill="#fbecec", stroke=POS, color=POS))

    render(os.path.join(OUT, "certification.svg"), W, H, *p,
           title="Головна причина модуля: готова сертифікація радіо")


# ── impedance-rotation: як лінія й L-ланка «крутять» імпеданс до 50 Ω ──────────
# Ідея (для детальної): відбиття Γ живе в одиничному колі; узгодження — це шлях
# від точки чіпа (30+j10) до центру (50 Ω, Γ=0). Реактивність рухає точку по
# колах, послідовна/паралельна — у різні боки. Показуємо два кроки L-ланки.

def fig_impedance_rotation():
    W, H = 720, 560
    p = []
    cx, cy, R = 360, 275, 210

    # одиничне коло Γ (усе, що всередині, — фізично можливе навантаження)
    p.append(circle(cx, cy, R, fill="#fbfaf6", stroke=INK, sw=2))
    # осі
    p.append(line(cx - R, cy, cx + R, cy, color=MUTED, sw=1, dash="4 4"))
    p.append(line(cx, cy - R, cx, cy + R, color=MUTED, sw=1, dash="4 4"))
    # центр = ідеальне узгодження
    p.append(circle(cx, cy, 5, fill=FIELD, stroke="none"))
    p.append(text(cx + 8, cy - 10, "центр: Γ = 0", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx + 8, cy + 6, "50 Ω, усе в ефір", size=10, color=FIELD, anchor="start"))

    # межа кола = |Γ|=1 (повне відбиття)
    p.append(text(cx, cy - R - 12, "|Γ| = 1 — уся енергія відбита назад", size=11,
                  color=POS, bold=True))

    # точка чіпа (30 + j10): праворуч-вгору від центру, помірний |Γ|
    px, py = cx + 84, cy - 46
    p.append(circle(px, py, 6, fill=POS, stroke="none"))
    p.append(text(px + 12, py - 6, "чіп: 30 + j10 Ω", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(px + 12, py + 10, "|Γ| ≈ 0.28", size=10, color=POS, anchor="start"))

    # проміжна точка після послідовної реактивності
    mx, my = cx + 96, cy + 30

    # шлях узгодження: чіп -> проміжна (по дузі) -> центр (по дузі)
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" '
             'stroke-width="2.6"/>' % (px, py, cx + 150, cy - 6, mx, my, NEG))
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" '
             'stroke-width="2.6"/>' % (mx, my, cx + 40, cy + 70, cx, cy, NEG))
    p.append(circle(mx, my, 5, fill=NEG, stroke="none"))

    # підписи кроків
    p.append(text(cx + 156, cy + 12, "крок 1: реактивність", size=10, color=NEG, anchor="start"))
    p.append(text(cx + 156, cy + 28, "(котушка) — по колу", size=10, color=NEG, anchor="start"))
    p.append(text(cx - 40, cy + 96, "крок 2: реактивність (ємність) — у центр", size=10,
                  color=NEG, anchor="middle"))

    # легенда внизу
    p.append(fitbox(90, 500, 540, 44,
                    "L-ланка (котушка + конденсатор) додає рівно стільки реактивності, "
                    "щоб перевести точку чіпа в центр. π-схема — це дві такі ланки, ширша смуга.",
                    size=11, fill="#eef1fb", stroke=NEG, color=INK))

    render(os.path.join(OUT, "impedance-rotation.svg"), W, H, *p,
           title="Узгодження як шлях у центр кола відбиття")


# ── decoupling-impedance: чому три ємності, і де ховається brownout ────────────
# Ідея: розв'язка — це низький імпеданс живлення в широкій смузі. Bulk тримає
# низ, 100 нФ — середину, паразити псують верх. Пік струму радіо на просадці.

def fig_decoupling_impedance():
    W, H = 820, 500
    p = []
    ox, oy = 110, 380          # початок осей
    ax, ay = 660, 60           # довжина осей

    # осі
    p.append(line(ox, oy, ox + ax, oy, color=INK, sw=2))          # частота →
    p.append(line(ox, oy, ox, oy - ay - 260, color=INK, sw=2))    # імпеданс ↑
    p.append(text(ox + ax, oy + 24, "частота →", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ay - 250, "|Z| живлення", size=11, color=INK, anchor="start"))

    # мітки частот
    for i, lab in enumerate(["10 кГц", "1 МГц", "100 МГц", "2.4 ГГц"]):
        fx = ox + 60 + i * 150
        p.append(line(fx, oy, fx, oy + 5, color=INK, sw=1))
        p.append(text(fx, oy + 20, lab, size=9, color=MUTED))

    # ціль-імпеданс (target impedance): горизонтальна межа
    ty = oy - 120
    p.append(line(ox, ty, ox + ax, ty, color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(ox + ax, ty - 8, "ціль: тримати нижче цієї лінії", size=10,
                  color=FIELD, anchor="end"))

    # криві-«ванни» окремих ємностей (кожна: спад -> мінімум ESR -> зростання)
    def valley(x0, xm, x1, ymin, col, dash=None):
        d = ' stroke-dasharray="4 4"' if dash else ''
        return ('<path d="M %d,%d Q %d,%d %d,%d Q %d,%d %d,%d" fill="none" '
                'stroke="%s" stroke-width="2"%s/>' %
                (x0, oy - 300, (x0 + xm) // 2, ymin - 10, xm, ymin,
                 (xm + x1) // 2, ymin - 6, x1, oy - 300, col, d))

    # bulk 10 мкФ — низ смуги
    p.append(valley(ox + 20, ox + 130, ox + 300, oy - 200, MUTED, dash=True))
    p.append(text(ox + 70, oy - 205, "10 мкФ", size=9, color=MUTED))
    # 100 нФ — середина
    p.append(valley(ox + 140, ox + 320, ox + 520, oy - 235, NEG, dash=True))
    p.append(text(ox + 300, oy - 240, "100 нФ", size=9, color=NEG))
    # ємність кристала/корпусу — верх
    p.append(valley(ox + 330, ox + 500, ox + 640, oy - 250, "#8a6bbf", dash=True))
    p.append(text(ox + 500, oy - 255, "внутрішня C", size=9, color="#8a6bbf"))

    # результуюча (огинальна) — суцільна, лишається під ціллю до ~сотень МГц
    p.append('<path d="M %d,%d C %d,%d %d,%d %d,%d C %d,%d %d,%d %d,%d" fill="none" '
             'stroke="%s" stroke-width="3"/>' %
             (ox + 20, oy - 300, ox + 120, ty + 6, ox + 330, ty + 4, ox + 470, ty + 8,
              ox + 560, ty + 2, ox + 610, oy - 250, ox + 660, oy - 210, INK))
    p.append(text(ox + 150, ty + 26, "сумарний імпеданс (що бачить чіп)", size=10,
                  color=INK, anchor="start", bold=True))

    # зона brownout: сплеск струму радіо піднімає просадку
    p.append(text(ox + 40, oy - 300 - 14, "паразитна L виводів псує верх смуги", size=9,
                  color=POS, anchor="start"))
    p.append(fitbox(ox + 20, oy + 40, ax - 20, 44,
                    "Пік струму передавача (до ~500 мА) на цьому імпедансі створює просадку "
                    "напруги; якщо вона нижча за ~2.44 В — спрацьовує brownout і чіп ресетиться.",
                    size=10, fill="#fbecec", stroke=POS, color=INK))

    render(os.path.join(OUT, "decoupling-impedance.svg"), W, H, *p,
           title="Розв'язка як низький імпеданс живлення в широкій смузі")


# ── strapping-map: піни вибору завантаження та пастка напруги Flash ───────────
# Ідея: кілька GPIO при скиданні вирішують режим старту й напругу Flash;
# MTDI (IO12) — пастка: висока при старті = 1.8 В Flash = псує модуль на 3.3 В.

def fig_strapping_map():
    W, H = 860, 470
    p = []

    p.append(text(W / 2, 40, "Піни-strapping: що вони вирішують у мить скидання",
                  size=14, color=INK, bold=True))

    rows = [
        ("IO0", "внутр. підтяжка ↑", "низько → режим прошивки; високо → запуск з Flash", FIELD),
        ("IO2", "внутр. підтяжка ↓", "має бути вільним/низько для входу в прошивку", MUTED),
        ("IO15 (MTDO)", "внутр. підтяжка ↑", "низько → глушить лог завантажувача на UART", MUTED),
        ("IO12 (MTDI)", "внутр. підтяжка ↓", "ВИСОКО при старті → 1.8 В Flash → псує модуль 3.3 В", POS),
    ]
    y0 = 80
    for i, (pin, pull, meaning, col) in enumerate(rows):
        y = y0 + i * 82
        p.append(rect(60, y, 160, 64, fill="#eef1fb", stroke=col, sw=1.8, rx=8))
        p.append(text(140, y + 28, pin, size=13, color=col, bold=True))
        p.append(text(140, y + 48, pull, size=9, color=MUTED))
        p.append('<path d="M 224,%d h 26" fill="none" stroke="%s" stroke-width="2"/>' % (y + 32, MUTED))
        p.append(arrow(250, y + 32, 264, y + 32, color=MUTED, sw=2))
        p.append(fitbox(270, y + 8, 520, 48, meaning, size=11, bold=(col == POS),
                        fill=("#fbecec" if col == POS else "#f6f4ee"),
                        stroke=col, color=INK))

    p.append(text(W / 2, y0 + 4 * 82 + 6,
                  "Незадіяний пін бере рівень від внутрішньої підтяжки — тож зовнішня логіка на цих ніжках небезпечна.",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "strapping-map.svg"), W, H, *p,
           title="Піни вибору завантаження й пастка напруги Flash")


# ── lmatch-topology: L-ланка як дві реактивності (для math-вставки) ────────────
# Ідея: L-ланка перетворює низький опір у високий двома елементами. Послідовна
# реактивність — біля НИЖЧОГО опору, паралельна — біля ВИЩОГО. Один Q на всю
# ланку, і він жорстко заданий відношенням опорів: Q = √(R_вис/R_низ − 1).

def fig_lmatch_topology():
    W, H = 860, 430
    p = []

    # дві сторони: ліворуч чіп (низький R), праворуч антена 50 Ω (вищий R)
    p.append(fitbox(60, 150, 150, 110, "чіп\n30 + j10 Ω\n(нижчий опір)",
                    size=12, bold=True, fill="#fbecec", stroke=POS, color=INK))
    p.append(fitbox(650, 150, 150, 110, "антена\n50 Ω\n(вищий опір)",
                    size=12, bold=True, fill="#eef6ef", stroke=FIELD, color=INK))

    # горішня сигнальна лінія
    p.append(line(210, 175, 650, 175, color=INK, sw=2))
    # нижня земляна лінія
    p.append(line(210, 350, 800, 350, color=INK, sw=2))
    p.append(text(430, 372, "земля", size=10, color=MUTED))

    # послідовна котушка (X_series) біля НИЖЧОГО опору — у розрив горішньої лінії
    p.append(rect(300, 158, 90, 34, fill="#e9eefb", stroke=NEG, sw=2, rx=6))
    p.append(text(345, 180, "L (послід.)", size=11, color=NEG, bold=True))
    p.append(text(345, 138, "+jX_s", size=11, color=NEG, bold=True))

    # паралельний конденсатор (X_shunt) біля ВИЩОГО опору — з лінії на землю
    p.append(line(560, 175, 560, 260, color=INK, sw=2))
    # символ конденсатора
    p.append(line(538, 260, 582, 260, color=INK, sw=2.4))
    p.append(line(538, 274, 582, 274, color=INK, sw=2.4))
    p.append(line(560, 274, 560, 350, color=INK, sw=2))
    p.append(text(600, 272, "C (парал.)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(600, 290, "−jX_p", size=11, color=NEG, anchor="start"))

    # ключова формула Q
    p.append(fitbox(230, 60, 400, 40,
                    "один Q на всю ланку:  Q = √(R_вис / R_низ − 1)",
                    size=13, bold=True, fill="#fbfaf6", stroke=INK, color=INK))

    # підказка про напрямок
    p.append(text(345, 405, "послідовна — біля нижчого опору", size=10, color=MUTED))
    p.append(text(600, 405, "паралельна — біля вищого", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "lmatch-topology.svg"), W, H, *p,
           title="L-ланка: послідовна плюс паралельна реактивність")


# ── q-bandwidth: чому нижча Q дає ширшу смугу ─────────────────────────────────
# Ідея: узгоджувач — резонансна система. Висока Q = гострий пік = вузька смуга;
# низька Q = пологий пік = широка. Смуга Wi-Fi/BLE (2.400–2.4835 ГГц) мусить
# уміститися під «добрим» рівнем — тому цілять НИЗЬКУ Q.

def fig_q_bandwidth():
    W, H = 860, 480
    p = []
    ox, oy = 110, 400        # початок осей
    axw, axh = 660, 320      # ширина/висота поля

    # осі
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw, oy + 24, "частота →", size=11, color=INK, anchor="end"))
    p.append(text(ox - 12, oy - axh + 4, "узгодженість", size=11, color=INK, anchor="start"))
    p.append(text(ox - 12, oy - axh + 20, "(вище — краще)", size=9, color=MUTED, anchor="start"))

    # центральна частота 2.4415 ГГц — центр піків
    fc = ox + axw / 2
    p.append(line(fc, oy, fc, oy - axh, color=MUTED, sw=1, dash="4 4"))
    p.append(text(fc, oy + 20, "2.44 ГГц", size=9, color=MUTED))

    # смуга Wi-Fi/BLE навколо центру (2.400–2.4835 ГГц) — зелена зона
    bw = 150
    p.append(rect(fc - bw, oy - axh, 2 * bw, axh, fill="#eef6ef", stroke="none"))
    p.append(text(fc, oy - axh - 8, "смуга Wi-Fi / BLE (2.400–2.4835 ГГц)", size=10,
                  color=FIELD, bold=True))

    # рівень «доброго узгодження»
    ty = oy - axh * 0.62
    p.append(line(ox, ty, ox + axw, ty, color=INK, sw=1.2, dash="6 4"))
    p.append(text(ox + 6, ty - 6, "поріг «добре» (низьке відбиття)", size=9,
                  color=INK, anchor="start"))

    # крива високої Q — гострий вузький пік (виходить із зеленої зони по краях)
    def peak(halfw, col, sw, dash=None):
        # дзвоноподібний пік із вершиною на fc, спад тим різкіший, чим менший halfw
        pts = []
        n = 60
        for i in range(n + 1):
            x = ox + axw * i / n
            # лоренціан-подібний
            val = 1.0 / (1.0 + ((x - fc) / halfw) ** 2)
            y = oy - 20 - (axh - 40) * val
            pts.append("%.1f,%.1f" % (x, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), col, sw, d))

    p.append(peak(70, POS, 2.6))       # висока Q — вузький
    p.append(peak(190, FIELD, 3))      # низька Q — широкий

    p.append(text(fc + 82, oy - axh + 70, "висока Q:", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(fc + 82, oy - axh + 86, "гострий пік, вузька смуга —", size=10, color=POS, anchor="start"))
    p.append(text(fc + 82, oy - axh + 100, "краї Wi-Fi випадають", size=10, color=POS, anchor="start"))

    p.append(text(ox + 20, oy - 70, "низька Q: пологий пік,", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(ox + 20, oy - 54, "уся смуга під порогом", size=10, color=FIELD, anchor="start"))

    p.append(fitbox(ox, oy + 34, axw, 30,
                    "смуга ≈ f₀ / Q — тому ширшу смугу дає НИЖЧА Q, і саме її цілять для всього Wi-Fi/BLE",
                    size=11, bold=True, fill="#fbfaf6", stroke=INK, color=INK))

    render(os.path.join(OUT, "q-bandwidth.svg"), W, H, *p,
           title="Нижча Q — ширша смуга: чому це вирішує для Wi-Fi/BLE")


# ── pi-two-l: π-схема як дві L-ланки через віртуальний опір ────────────────────
# Ідея: π = дві L-ланки спина до спини через ПРОМІЖНИЙ віртуальний опір R_v,
# НИЖЧИЙ за обидва кінці. Кожна ланка тепер трансформує менший перепад, але
# додається вільний параметр R_v — ним ЗАДАЮТЬ Q (а отже смугу) незалежно.

def fig_pi_two_l():
    W, H = 900, 470
    p = []

    # три вузли: чіп (30+j10) — віртуальний R_v — антена 50
    p.append(fitbox(50, 150, 130, 96, "чіп\n30 + j10 Ω",
                    size=12, bold=True, fill="#fbecec", stroke=POS, color=INK))
    p.append(fitbox(720, 150, 130, 96, "антена\n50 Ω",
                    size=12, bold=True, fill="#eef6ef", stroke=FIELD, color=INK))
    p.append(fitbox(390, 150, 120, 96, "R_v\n(віртуальний,\nнижчий за обидва)",
                    size=11, bold=True, fill="#fff6e6", stroke="#c07a2e", color="#9a5a1e"))

    # сигнальна й земляна лінії
    p.append(line(180, 175, 390, 175, color=INK, sw=2))
    p.append(line(510, 175, 720, 175, color=INK, sw=2))
    p.append(line(180, 360, 850, 360, color=INK, sw=2))
    p.append(text(500, 382, "земля", size=10, color=MUTED))

    # ланка 1 (чіп ↔ R_v): послідовна L у лінію + паралельна C1 на землю (біля чіпа)
    p.append(rect(250, 158, 70, 34, fill="#e9eefb", stroke=NEG, sw=2, rx=6))
    p.append(text(285, 180, "L", size=12, color=NEG, bold=True))
    # C1 біля чіпа (перший конденсатор π)
    p.append(line(210, 175, 210, 250, color=INK, sw=2))
    p.append(line(192, 250, 228, 250, color=INK, sw=2.2))
    p.append(line(192, 262, 228, 262, color=INK, sw=2.2))
    p.append(line(210, 262, 210, 360, color=INK, sw=2))
    p.append(text(205, 290, "C1", size=11, color=NEG, bold=True, anchor="end"))

    # ланка 2 (R_v ↔ антена): C2 біля антени (другий конденсатор π)
    p.append(line(690, 175, 690, 250, color=INK, sw=2))
    p.append(line(672, 250, 708, 250, color=INK, sw=2.2))
    p.append(line(672, 262, 708, 262, color=INK, sw=2.2))
    p.append(line(690, 262, 690, 360, color=INK, sw=2))
    p.append(text(695, 290, "C2", size=11, color=NEG, bold=True, anchor="start"))

    # дужки, що показують дві L-ланки
    p.append('<path d="M 185,120 H 445" fill="none" stroke="%s" stroke-width="1.6"/>' % MUTED)
    p.append(text(315, 112, "L-ланка 1", size=10, color=MUTED))
    p.append('<path d="M 455,120 H 715" fill="none" stroke="%s" stroke-width="1.6"/>' % MUTED)
    p.append(text(585, 112, "L-ланка 2", size=10, color=MUTED))

    p.append(fitbox(120, 405, 660, 44,
                    "π = C1 · L · C2 — дві L-ланки спина до спини через віртуальний R_v. "
                    "R_v — вільний параметр: ним задають Q (а отже смугу) незалежно від відношення 30↔50.",
                    size=11, fill="#fff6e6", stroke="#c07a2e", color=INK))

    render(os.path.join(OUT, "pi-two-l.svg"), W, H, *p,
           title="π-схема (CLC) як дві L-ланки через віртуальний опір")


# ── shield-history-timeline: як народилася модульна сертифікація ──────────────
# Ідея (для вставки hist-shield-can): вісь часу від «кожен виріб сертифікуй
# наново» через сплеск Wi-Fi/Bluetooth до правил FCC — DA 00-1407 (вісім умов,
# екран №1), кодифікації 2007 (split/limited) і живого гіда KDB 996369.

def fig_shield_history_timeline():
    W, H = 940, 430
    p = []

    # горизонтальна вісь часу
    axis_y = 150
    p.append(line(70, axis_y, 870, axis_y, color=INK, sw=2.4))
    p.append(arrow(860, axis_y, 895, axis_y, color=INK, sw=2.4))
    p.append(text(892, axis_y - 12, "час", size=11, color=MUTED, anchor="end"))

    # віхи: (x, рік, підпис угорі/внизу, колір позначки)
    marks = [
        (150, "≈1999–2001", "сплеск Wi-Fi і\nBluetooth: OEM-\nрадіо у кожен\nноутбук", "up", FIELD),
        (360, "26.06.2000", "FCC, DA 00-1407:\nвісім умов модуля\n(екран — умова №1)", "down", POS),
        (600, "23.04.2007", "FCC 07-56 (ET 03-201):\nкодифікація у §15.212\n+ split + limited", "up", NEG),
        (820, "донині", "KDB 996369:\nживий гід,\nодне vs limited", "down", MUTED),
    ]
    for x, yr, cap, side, col in marks:
        p.append(circle(x, axis_y, 8, fill=col, stroke=INK, sw=1.6))
        p.append(text(x, axis_y + (26 if side == "down" else -16),
                      yr, size=12, color=INK, bold=True))
        if side == "up":
            p.append(line(x, axis_y - 30, x, axis_y - 46, color=MUTED, sw=1.2))
            p.append(fitbox(x - 95, axis_y - 128, 190, 74, cap, size=10,
                            fill="#f6f4ee", stroke=col, color=INK))
        else:
            p.append(line(x, axis_y + 34, x, axis_y + 50, color=MUTED, sw=1.2))
            p.append(fitbox(x - 95, axis_y + 52, 190, 72, cap, size=10,
                            fill="#f6f4ee", stroke=col, color=INK))

    # нижня рамка з суттю: чому екран
    p.append(fitbox(70, 352, 800, 60,
                    "Наскрізна нитка — металевий екран («radio-in-a-can»): він робить модуль самодостатнім,\n"
                    "тож радіо міряють раз, а виріб успадковує дозвіл. Без екрана — лише limited під конкретний корпус.",
                    size=12, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(OUT, "shield-history-timeline.svg"), W, H, *p,
           title="Як народилася модульна сертифікація радіо")


# ── tx-current-profile: профіль струму в часі й де ховається brownout ─────────
# Ідея (proj-brownout): спокій — тонка лінія; момент увімкнення радіо й перший
# сплеск PA — вузький високий пік (до ~500 мА); на слабкому живленні цей пік
# просаджує напругу нижче порога BOD, і чіп ресетиться саме в цю мить.

def fig_tx_current_profile():
    W, H = 860, 470
    p = []
    ox, oy = 90, 250            # нуль струму (осі)
    axr = 770                   # правий край осі часу
    top = 70                    # верх графіка струму

    p.append(text(W / 2, 34, "Профіль струму: спокій, старт радіо, піки передачі",
                  size=15, color=INK, bold=True))

    p.append(line(ox, top, ox, oy, color=INK, sw=2))
    p.append(line(ox, oy, axr, oy, color=INK, sw=2))
    p.append(text(ox - 10, top - 6, "струм", size=10, color=INK, anchor="start"))
    p.append(text(axr, oy + 22, "час →", size=11, color=INK, anchor="end"))

    def yI(ma):                 # 0..600 мА → пікселі
        return oy - (ma / 600.0) * (oy - top)
    for ma in (100, 300, 500):
        yy = yI(ma)
        p.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1))
        p.append(text(ox - 8, yy + 4, "%d мА" % ma, size=9, color=MUTED, anchor="end"))

    base = yI(20)
    radio_on = yI(120)
    spike1 = yI(500)
    tx = yI(260)
    x1, x2 = ox + 210, ox + 250
    seg = ('<path d="M %d,%d L %d,%d '
           'L %d,%d L %d,%d '
           'L %d,%d L %d,%d L %d,%d '
           % (ox + 10, base, x1, base,
              x1, radio_on, x2, radio_on,
              x2 + 8, spike1, x2 + 22, spike1, x2 + 30, tx))
    xx = x2 + 30
    for _ in range(6):
        seg += 'L %d,%d L %d,%d L %d,%d ' % (xx + 18, tx, xx + 26, yI(430), xx + 40, tx)
        xx += 70
    seg += 'L %d,%d" fill="none" stroke="%s" stroke-width="2.4"/>' % (axr - 6, tx, NEG)
    p.append(seg)

    p.append(text((ox + 10 + x1) / 2, base + 20, "спокій (радіо спить)", size=10, color=MUTED))
    p.append('<path d="M %d,%d v -18" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>'
             % (x1, oy, MUTED))
    p.append(text(x1 + 4, radio_on - 8, "вмикаємо Wi-Fi:", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 4, radio_on + 6, "PHY/PLL старт", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 34, spike1 - 8, "перший сплеск PA", size=10, color=POS, anchor="start", bold=True))
    p.append(text(xx - 130, tx - 12, "піки передачі", size=10, color=NEG, anchor="start"))

    bod = yI(560)
    p.append(line(ox, bod, axr, bod, color=POS, sw=1.4, dash="6 4"))
    p.append(text(axr, bod - 6, "пік, що на слабкому живленні тягне 3V3 нижче порога BOD",
                  size=9, color=POS, anchor="end"))

    p.append(fitbox(ox, oy + 40, axr - ox, 44,
                    "Небезпечний не середній струм, а ВУЗЬКИЙ перший пік: за одиниці "
                    "мілісекунд він розряджає слабку розв'язку, напруга проколює ~2.43 В — "
                    "і BOD ресетить чіп саме в мить виходу в ефір.",
                    size=10, fill="#fbecec", stroke=POS, color=INK))

    render(os.path.join(OUT, "tx-current-profile.svg"), W, H, *p, title=None)


# ── brownout-recovery: рішення після скидання за причиною ──────────────────────
# Ідея (proj-brownout): esp_reset_reason() на старті — розвилка. BROWNOUT веде
# окремою гілкою: не чіпати Wi-Fi одразу, підняти поріг, порізати пік PA,
# лишити слід у RTC-лічильнику, і лише тоді обережно в ефір.

def fig_brownout_recovery():
    W, H = 820, 540
    p = []

    p.append(text(W / 2, 34, "Старт: розвилка за причиною скидання", size=15, color=INK, bold=True))

    p.append(fitbox(300, 60, 220, 40, "esp_reset_reason()", size=12, bold=True,
                    fill="#eef1fb", stroke=NEG, color=NEG))
    p.append(arrow(410, 100, 410, 128, color=INK, sw=2))
    p.append(fitbox(300, 130, 220, 34, "це ESP_RST_BROWNOUT?", size=11, bold=True,
                    fill="#f6f4ee", stroke=INK, color=INK))

    p.append(arrow(300, 147, 152, 147, color=FIELD, sw=2))
    p.append(text(224, 138, "ні", size=10, color=FIELD, bold=True))
    p.append(fitbox(36, 172, 220, 56, "звичайний старт:\nWi-Fi на повну, як завжди",
                    size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD))

    p.append(arrow(520, 147, 664, 147, color=POS, sw=2))
    p.append(text(592, 138, "так", size=10, color=POS, bold=True))
    steps = [
        "полічити brownout у RTC-лічильнику",
        "НЕ вмикати Wi-Fi одразу",
        "підняти поріг BOD (запас)",
        "обмежити стартовий сплеск PA",
        "знизити TX-потужність за потреби",
        "аж тепер — обережно в ефір",
    ]
    sy, prev = 172, None
    for i, s in enumerate(steps):
        hot = i in (2, 3, 4)
        p.append(fitbox(498, sy, 300, 40, s, size=10, bold=hot,
                        fill=("#fbecec" if hot else "#f6f4ee"),
                        stroke=(POS if hot else MUTED), color=INK))
        if prev is not None:
            p.append(arrow(648, prev + 40, 648, sy, color=MUTED, sw=1.6))
        prev = sy
        sy += 56

    p.append(fitbox(36, 300, 220, 150,
                    "RTC-пам'ять переживає скидання (живиться окремо). "
                    "Лічильник brownout у ній = детектор поганого живлення: "
                    "кілька підряд → зменшуй апетит радіо назавжди, не гадай наосліп.",
                    size=10, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(OUT, "brownout-recovery.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_module_anatomy()
    fig_certification()
    fig_impedance_rotation()
    fig_decoupling_impedance()
    fig_strapping_map()
    fig_lmatch_topology()
    fig_q_bandwidth()
    fig_pi_two_l()
    fig_shield_history_timeline()
    fig_tx_current_profile()
    fig_brownout_recovery()
    print("OK: figures written to", OUT)
