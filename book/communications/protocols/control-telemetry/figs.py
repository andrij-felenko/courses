# -*- coding: utf-8 -*-
# Фігури теми «Керування й телеметрія» + історичної вставки про MAVLink.
# svgkit імпортуємо, не переписуємо (§5). Вивід — у ./img/, імена slug-only.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── локальні кольори ролей (узгоджені між фігурами) ──────────────────────────
CTRL = POS        # керування — гаряче/критичне (червоне)
TELE = "#b08900"  # телеметрія — бурштинове
VIDEO = NEG       # відео — холодне (синє)


def carrow(x1, y1, x2, y2, color=INK, sw=2.2, dash=None):
    """Кольорова стрілка: лінія + трикутний наконечник (render() дає лише один
    одноколірний marker, тож наконечник малюємо самі)."""
    import math
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    body = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"%s/>' % (x1, y1, x2, y2, color, sw, d))
    ang = math.atan2(y2 - y1, x2 - x1)
    s = 9.0
    ax, ay = x2, y2
    bx = ax - s * math.cos(ang - 0.42); by = ay - s * math.sin(ang - 0.42)
    cx = ax - s * math.cos(ang + 0.42); cy = ay - s * math.sin(ang + 0.42)
    head = ('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
            % (ax, ay, bx, by, cx, cy, color))
    return body + head


def drone(cx, cy, color=INK, label=None):
    """Схематичний квадрокоптер: тіло + 4 промені з кружками-моторами."""
    r = 16
    p = [line(cx - r, cy - r, cx + r, cy + r, color=color, sw=2.4),
         line(cx - r, cy + r, cx + r, cy - r, color=color, sw=2.4)]
    for dx, dy in ((-r, -r), (r, -r), (-r, r), (r, r)):
        p.append(circle(cx + dx, cy + dy, 6.5, fill="none", stroke=color, sw=2))
    p.append(rect(cx - 9, cy - 7, 18, 14, fill="#eef2fb", stroke=color, sw=1.6, rx=2))
    if label:
        p.append(text(cx, cy + r + 22, label, size=11, color=color, bold=True))
    return "".join(p)


def antenna(cx, cy, color=INK, label=None):
    """Наземна станція: щогла з «хвилями»."""
    p = [line(cx, cy, cx, cy - 34, color="#8a8a8a", sw=3),
         line(cx - 8, cy - 38, cx + 8, cy - 38, color="#8a8a8a", sw=3)]
    for rr in (10, 18, 26):
        p.append('<path d="M %.1f,%.1f A %d %d 0 0 1 %.1f,%.1f" fill="none" '
                 'stroke="%s" stroke-width="1.4"/>' % (cx - rr, cy - 38, rr, rr, cx + rr, cy - 38, FIELD))
    if label:
        p.append(text(cx, cy + 18, label, size=11, color=color, bold=True))
    return "".join(p)


# ════════════════════════════════════════════════════════════════════════════
# ТЕМА: керування й телеметрія
# ════════════════════════════════════════════════════════════════════════════

def fig_two_links():
    W, H = 940, 360
    p = [text(W/2, 30, "Зв'язок апарата — не одна лінія, а кілька ролей", size=18, bold=True),
         text(W/2, 50, "керування «віжки» вгору, телеметрія «панель приладів» в обидва боки, інколи ще й відео",
              size=11.5, color=MUTED, italic=True)]
    p.append(drone(200, 175, color=NEG, label="борт (апарат)"))
    p.append(antenna(770, 205, color=FIELD, label="пульт / станція"))
    # керування вгору
    p.append(carrow(700, 120, 250, 120, color=CTRL, sw=2.6))
    p.append(text(470, 108, "КЕРУВАННЯ: команди вгору (низька затримка)", size=11.5, color=CTRL, bold=True))
    # телеметрія в два боки
    p.append(carrow(250, 168, 700, 168, color=TELE, sw=2.6))
    p.append(text(470, 190, "ТЕЛЕМЕТРІЯ: стан вниз, налаштування вгору", size=11.5, color=TELE, bold=True))
    # відео вниз
    p.append(carrow(250, 214, 700, 214, color=VIDEO, sw=2.2, dash="5 3"))
    p.append(text(470, 236, "ВІДЕО (FPV): картинка вниз, широка смуга", size=11, color=VIDEO, bold=True))
    box, _, _ = textbox(W/2, 300, "Кожна лінія має свої вимоги — тому їх часто розділяють\n(різні смуги, різні модулі).",
                        size=12, fill="#eef6ef", stroke=FIELD, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "two-links.svg"), W, H, *p)


def fig_control_link():
    W, H = 900, 330
    p = [text(W/2, 30, "Лінія керування: «віжки» апарата", size=18, bold=True),
         text(W/2, 50, "мало даних, але миттєво й безвідмовно", size=11.5, color=MUTED, italic=True)]
    chans = ["газ", "крен", "тангаж", "нишпорення", "режим"]
    x0 = 70
    for i, c in enumerate(chans):
        p.append(fitbox(x0 + i*112, 80, 100, 34, c, size=11.5, fill="#fdecea", stroke=CTRL, bold=True))
    p.append(carrow(W/2, 122, W/2, 158, color=CTRL, sw=2.6))
    p.append(text(W/2, 150, "канали → радіо", size=10.5, color=MUTED, anchor="start"))
    reqs = [("низька затримка", "запізнена команда = аварія"),
            ("висока надійність", "втрата → безпечний режим"),
            ("мало даних", "лише стіки й перемикачі")]
    for i, (h, sub) in enumerate(reqs):
        x = 70 + i*280
        p.append(fitbox(x, 168, 260, 56, h + "\n" + sub, size=12, fill=FILL, stroke=CTRL))
    box, _, _ = textbox(W/2, 268, "Зникла лінія керування → спрацьовує failsafe:\nповернення додому (RTL) або посадка.",
                        size=12, fill="#fdecea", stroke=CTRL, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "control-link.svg"), W, H, *p)


def fig_telemetry_link():
    W, H = 900, 320
    p = [text(W/2, 30, "Лінія телеметрії: «панель приладів» і розмова", size=18, bold=True),
         text(W/2, 50, "багато даних, двосторонньо, терпить затримку", size=11.5, color=MUTED, italic=True)]
    p.append(drone(160, 175, color=NEG, label="борт"))
    p.append(antenna(770, 200, color=FIELD, label="станція (QGroundControl)"))
    p.append(carrow(230, 150, 700, 150, color=TELE, sw=2.6))
    p.append(text(465, 138, "ВНИЗ: висота, кути, GPS, заряд, режим, попередження", size=11, color=TELE, bold=True))
    p.append(carrow(700, 196, 230, 196, color=TELE, sw=2.6, dash="5 3"))
    p.append(text(465, 216, "ВГОРУ: маршрут-місія, параметри, окремі команди", size=11, color=TELE, bold=True))
    box, _, _ = textbox(W/2, 272, "Тут «розмовляє» MAVLink. Загубився пакет — нічого:\nприйде наступний (затримка в сотні мс прийнятна).",
                        size=12, fill="#fff7e0", stroke=TELE, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "telemetry-link.svg"), W, H, *p)


def fig_video_link():
    W, H = 900, 300
    p = [text(W/2, 30, "Третя лінія: відео (FPV)", size=18, bold=True),
         text(W/2, 50, "одна річ — картинка вниз, але найширша смуга", size=11.5, color=MUTED, italic=True)]
    p.append(drone(160, 160, color=NEG, label="камера на борту"))
    p.append(antenna(770, 185, color=FIELD, label="екран / окуляри"))
    # широка стрілка вниз — кілька паралельних ліній, щоб показати «товщину» потоку
    for off in (-5, 0, 5):
        p.append(carrow(230, 150+off, 700, 150+off, color=VIDEO, sw=2.0))
    p.append(text(465, 132, "ВІДЕО ВНИЗ: суцільний потік кадрів (багато даних/с)", size=11, color=VIDEO, bold=True))
    box, _, _ = textbox(W/2, 240, "Широку смугу виносять в окремий діапазон (часто 5.8 ГГц),\nщоб відео не «забивало» вузькі критичні лінії.",
                        size=12, fill="#eaf0fd", stroke=VIDEO, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "video-link.svg"), W, H, *p)


def fig_why_separate():
    W, H = 940, 320
    p = [text(W/2, 30, "Навіщо розділяти лінії (і часто — діапазони)", size=18, bold=True),
         text(W/2, 50, "вимоги ролей майже протилежні", size=11.5, color=MUTED, italic=True)]
    cards = [("Різні вимоги",
              "керуванню — затримка,\nтелеметрії — обсяг даних,\nвідео — смуга; один канал\nусе не потягне оптимально"),
             ("Різні діапазони",
              "керування 2.4/868/433 МГц,\nтелеметрія 433/915 МГц,\nвідео 5.8 ГГц —\nне глушать одне одного"),
             ("Безпека",
              "критичну лінію керування\nізолюють, щоб збій відео\nчи телеметрії її\nне зачепив")]
    cols = [CTRL, TELE, FIELD]
    for i, (h, body) in enumerate(cards):
        x = 60 + i*295
        p.append(rect(x, 76, 270, 200, fill="#fafafa", stroke=cols[i], sw=1.6, rx=8))
        p.append(text(x+135, 104, h, size=13.5, color=cols[i], bold=True))
        p.append(line(x+20, 116, x+250, 116, color="#e2e2e2", sw=1))
        p.append(mtext(x+135, 142, body, size=11.5, color=INK))
    render(os.path.join(OUT, "why-separate.svg"), W, H, *p)


def fig_requirements():
    W, H = 940, 312
    p = [text(W/2, 30, "Три ролі — три набори вимог", size=18, bold=True),
         text(W/2, 50, "контраст показує, чому їх не зливають в одне", size=11.5, color=MUTED, italic=True)]
    cols = [("", INK, 150), ("Керування", CTRL, 220), ("Телеметрія", TELE, 230), ("Відео", VIDEO, 180)]
    rows = [("затримка", ["критична (мс)", "терпить (×100 мс)", "помірна"]),
            ("надійність", ["найвища", "висока", "середня"]),
            ("обсяг даних", ["крихти", "середній", "великий потік"]),
            ("оновлення", ["сотні Гц", "одиниці Гц", "десятки кадрів/с"]),
            ("напрям", ["вгору", "у два боки", "вниз"])]
    xs = [70, 220, 440, 670]
    ws = [150, 220, 230, 180]
    y = 78; rh = 36
    # заголовок
    for j, (lbl, col, _) in enumerate(cols):
        p.append(rect(xs[j], y, ws[j], rh, fill="#f0f0f0", stroke="#8a8a8a", sw=1.2, rx=0))
        if lbl:
            p.append(text(xs[j]+ws[j]/2, y+rh/2+4, lbl, size=12, color=col, bold=True))
    # рядки
    for i, (name, vals) in enumerate(rows):
        ry = y + rh + i*rh
        p.append(rect(xs[0], ry, ws[0], rh, fill="#fafafa", stroke="#e2e2e2", sw=1, rx=0))
        p.append(text(xs[0]+12, ry+rh/2+4, name, size=11, color=INK, anchor="start", bold=True))
        for j, v in enumerate(vals):
            col = [CTRL, TELE, VIDEO][j]
            p.append(rect(xs[j+1], ry, ws[j+1], rh, fill="#fff", stroke="#e2e2e2", sw=1, rx=0))
            p.append(text(xs[j+1]+ws[j+1]/2, ry+rh/2+4, v, size=10.5, color=col))
    render(os.path.join(OUT, "requirements.svg"), W, H, *p)


def fig_convergence():
    W, H = 900, 300
    p = [text(W/2, 30, "Сучасний поворот: керування й телеметрія в одній лінії", size=17, bold=True),
         text(W/2, 50, "технології зливаються, ролі — ні", size=11.5, color=MUTED, italic=True)]
    # ліворуч — класика (два радіо), праворуч — сучасне (одне радіо)
    p.append(rect(60, 76, 360, 180, fill="#fafafa", stroke="#8a8a8a", sw=1.4, rx=8))
    p.append(text(240, 100, "Класично: двоє радіо", size=13, color=INK, bold=True))
    p.append(fitbox(90, 118, 130, 44, "радіо\nкерування", size=11, fill="#fdecea", stroke=CTRL, bold=True))
    p.append(fitbox(260, 118, 130, 44, "радіо\nтелеметрії", size=11, fill="#fff7e0", stroke=TELE, bold=True))
    p.append(carrow(155, 172, 155, 210, color=CTRL, sw=2))
    p.append(carrow(325, 210, 325, 172, color=TELE, sw=2))
    p.append(text(240, 236, "окремі антени, більша вага", size=10.5, color=MUTED, italic=True))

    p.append(rect(480, 76, 360, 180, fill="#fafafa", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(660, 100, "Сучасно: одне радіо", size=13, color=INK, bold=True))
    p.append(fitbox(560, 124, 200, 44, "ExpressLRS / Crossfire", size=11.5, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(carrow(660, 176, 660, 206, color=CTRL, sw=2))
    p.append(carrow(700, 206, 700, 176, color=TELE, sw=2, dash="4 3"))
    p.append(text(660, 230, "керування вгору + телеметрія вниз", size=10.5, color=MUTED, italic=True))
    p.append(text(660, 246, "тим самим лінком", size=10.5, color=MUTED, italic=True))
    p.append(text(W/2, 288, "Дві РОЛІ — «віжки» й «панель приладів» — лишаються різними, хоч би скільки радіо було.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "convergence.svg"), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
# ВСТАВКА: історія MAVLink
# ════════════════════════════════════════════════════════════════════════════

def fig_timeline():
    W, H = 940, 300
    p = [text(W/2, 30, "Дві гілки, одна мова: як народилися відкриті дрони", size=18, bold=True),
         text(W/2, 50, "не один геній, а спільнота й два паралельні автопілоти", size=11.5, color=MUTED, italic=True)]
    axis_y = 150
    p.append(line(70, axis_y, 870, axis_y, color="#8a8a8a", sw=2))
    events = [("2007", "DIY Drones;\nArduPilot на Arduino", -1),
              ("2008", "Маєр у ETH:\nдрон із зором", 1),
              ("2009", "MAVLink;\nArduPilot 1.0", -1),
              ("2011", "PX4 і\nвідкритий Pixhawk", 1),
              ("2012", "pymavlink,\nMAVProxy", -1),
              ("2014", "Dronecode\nFoundation", 1)]
    n = len(events)
    for i, (yr, lbl, side) in enumerate(events):
        x = 110 + i * (760/(n-1))
        p.append(circle(x, axis_y, 6, fill=POS, stroke=POS, sw=1))
        p.append(text(x, axis_y + (-16 if side < 0 else 22), yr, size=12, color=INK, bold=True))
        ly = axis_y + (-72 if side < 0 else 60)
        p.append(line(x, axis_y, x, ly + (28 if side < 0 else -8), color="#cfcfcf", sw=1))
        p.append(mtext(x, ly, lbl, size=10.5, color=MUTED))
    render(os.path.join(OUT, "timeline.svg"), W, H, *p)


def fig_problem():
    W, H = 900, 300
    p = [text(W/2, 30, "Проблема: борту й землі треба багато про що домовлятися", size=17, bold=True),
         text(W/2, 50, "десятки різних повідомлень крізь вузький шумний канал", size=11.5, color=MUTED, italic=True)]
    p.append(drone(150, 170, color=NEG, label="борт"))
    p.append(antenna(770, 195, color=FIELD, label="земля"))
    msgs = ["висота", "GPS", "батарея", "режим", "команди"]
    for i, m in enumerate(msgs):
        p.append(fitbox(330 + (i%3)*90, 110 + (i//3)*40, 82, 32, m, size=10.5, fill=FILL, stroke="#8a8a8a"))
    p.append(carrow(230, 230, 700, 230, color="#8a8a8a", sw=2.0, dash="6 4"))
    p.append(text(465, 222, "вузький, шумний радіоканал", size=11, color=MUTED, bold=True))
    box, _, _ = textbox(W/2, 276, "Потрібна спільна МОВА: компактна (мало байтів),\nнадійна (з перевіркою) і стандартна (зрозуміла будь-кому).",
                        size=12, fill=FILL, stroke=INK, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "problem.svg"), W, H, *p)


def fig_mavlink_idea():
    W, H = 940, 250
    p = [text(W/2, 30, "Ідея MAVLink: крихітні пакети з контролем", size=18, bold=True),
         text(W/2, 50, "знайомий кадр: маркер, довжина, ID типу, дані, CRC", size=11.5, color=MUTED, italic=True)]
    fields = [("STX", "#eef2fb"), ("LEN", "#eef2fb"), ("SEQ", "#eef2fb"),
              ("SYS", "#eef2fb"), ("COMP", "#eef2fb"), ("MSG ID", "#fff7e0"),
              ("PAYLOAD", "#eef6ef"), ("CRC", "#fdecea")]
    widths = [70, 70, 70, 70, 80, 100, 220, 90]
    x = 60; y = 100; h = 56
    for (lbl, col), w in zip(fields, widths):
        p.append(rect(x, y, w, h, fill=col, stroke="#8a8a8a", sw=1.4, rx=4))
        p.append(text(x + w/2, y + h/2 + 4, lbl, size=11.5, color=INK, bold=True))
        x += w
    p.append(text(60 + sum(widths[:5]) + widths[5]/2, y + h + 22, "↑ за ID знаємо, як читати дані", size=10.5, color=TELE, bold=True))
    p.append(text(60 + sum(widths[:7]) + widths[7]/2, y - 10, "↓ CRC: чи не зіпсувалося", size=10.5, color=POS, bold=True, anchor="end"))
    render(os.path.join(OUT, "mavlink-idea.svg"), W, H, *p)


def fig_by_accident():
    W, H = 900, 280
    p = [text(W/2, 30, "Несподіванка: світовий стандарт виник «між іншим»", size=17, bold=True),
         text(W/2, 50, "головною метою був дрон із зором, а не протокол", size=11.5, color=MUTED, italic=True)]
    p.append(rect(60, 80, 360, 150, fill="#fafafa", stroke="#8a8a8a", sw=1.4, rx=8))
    p.append(text(240, 106, "ГОЛОВНА мета", size=13, color=INK, bold=True))
    p.append(mtext(240, 138, "дрон із комп'ютерним зором,\nщо сам літає в приміщенні\n(змагання мікроапаратів)", size=11.5, color=MUTED))
    p.append(text(240, 214, "→ лишилася науковою роботою", size=10.5, color=MUTED, italic=True))
    p.append(rect(480, 80, 360, 150, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(660, 106, "ПОБІЧНІ інструменти", size=13, color=FIELD, bold=True))
    p.append(mtext(660, 138, "MAVLink (протокол)\n+ QGroundControl (станція)\nзроблені «by accident»", size=11.5, color=INK))
    p.append(text(660, 214, "→ стали світовим стандартом", size=10.5, color=FIELD, bold=True))
    render(os.path.join(OUT, "by-accident.svg"), W, H, *p)


def fig_collective():
    W, H = 940, 320
    p = [text(W/2, 30, "Відкриті дрони — праця спільноти, а не одного героя", size=17, bold=True),
         text(W/2, 50, "дві гілки автопілотів, що прийняли спільну мову", size=11.5, color=MUTED, italic=True)]
    # дві гілки
    p.append(rect(60, 78, 380, 150, fill="#eef2fb", stroke=NEG, sw=1.6, rx=8))
    p.append(text(250, 102, "Гілка PX4 (ETH Zürich)", size=13, color=NEG, bold=True))
    p.append(mtext(250, 134, "Лоренц Маєр →\nMAVLink · PX4 · Pixhawk · QGroundControl", size=11, color=INK))
    p.append(rect(500, 78, 380, 150, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(690, 102, "Гілка ArduPilot (DIY Drones)", size=13, color=FIELD, bold=True))
    p.append(mtext(690, 134, "Кріс Андерсон (спільнота),\nЖорді Муньйос (код),\nЕндрю Тридджелл (pymavlink, MAVProxy)", size=11, color=INK))
    # спільна мова знизу
    p.append(carrow(250, 228, 430, 268, color="#8a8a8a", sw=2))
    p.append(carrow(690, 228, 510, 268, color="#8a8a8a", sw=2))
    box, _, _ = textbox(W/2, 286, "Обидві гілки прийняли MAVLink — тому він і став універсальним.",
                        size=12.5, fill="#fff7e0", stroke=TELE, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "collective.svg"), W, H, *p)


def fig_open():
    W, H = 920, 300
    p = [text(W/2, 30, "Чому «відкрите» змінило все", size=18, bold=True),
         text(W/2, 50, "відкритий протокол + відкрите залізо/код = екосистема", size=11.5, color=MUTED, italic=True)]
    p.append(rect(60, 80, 380, 90, fill="#eef2fb", stroke=NEG, sw=1.5, rx=8))
    p.append(text(250, 108, "Відкритий ПРОТОКОЛ (MAVLink)", size=12.5, color=NEG, bold=True))
    p.append(mtext(250, 134, "будь-який пристрій говорить\nз будь-яким", size=11, color=INK))
    p.append(rect(480, 80, 380, 90, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(670, 108, "Відкриті ЗАЛІЗО й КОД", size=12.5, color=FIELD, bold=True))
    p.append(mtext(670, 134, "Pixhawk, PX4, ArduPilot —\nвивчати, повторювати, удосконалювати", size=11, color=INK))
    box, _, _ = textbox(W/2, 220, "Разом → екосистема: хобі, наука, поля й ліси,\nкартографія, рятувальні роботи — доступ для всіх, а не лише корпорацій.",
                        size=12, fill=FILL, stroke=INK, bold=True, pad=12)
    p.append(box)
    render(os.path.join(OUT, "open.svg"), W, H, *p)


def fig_legacy():
    W, H = 900, 250
    p = [text(W/2, 30, "Що лишилось: три рівні роботи з MAVLink", size=18, bold=True),
         text(W/2, 50, "від структури пакета до власного коду", size=11.5, color=MUTED, italic=True)]
    levels = [("Пакет", "heartbeat,\nID типу, CRC"),
              ("Потік і команди", "читати телеметрію,\nслати команди автопілоту"),
              ("pymavlink", "місток від станції\nдо власного коду")]
    for i, (h, body) in enumerate(levels):
        x = 60 + i*290
        p.append(rect(x, 84, 260, 110, fill="#fafafa", stroke=FIELD, sw=1.6, rx=8))
        p.append(text(x+130, 112, h, size=13, color=FIELD, bold=True))
        p.append(line(x+20, 124, x+240, 124, color="#e2e2e2", sw=1))
        p.append(mtext(x+130, 150, body, size=11.5, color=INK))
        if i < 2:
            p.append(carrow(x+260, 139, x+290, 139, color="#8a8a8a", sw=2))
    render(os.path.join(OUT, "legacy.svg"), W, H, *p)


if __name__ == "__main__":
    fig_two_links(); fig_control_link(); fig_telemetry_link(); fig_video_link()
    fig_why_separate(); fig_requirements(); fig_convergence()
    fig_timeline(); fig_problem(); fig_mavlink_idea(); fig_by_accident()
    fig_collective(); fig_open(); fig_legacy()
    print("OK: figs.py — 14 фігур у", OUT)
