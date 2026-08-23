# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорові наконечники (svgkit дає лише нейтральний #arrow)
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)


def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))


def block(x, y, w, h, lines, fill, stroke, color=INK, size=12.5, bold=True):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.7, rx=10)
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out


# ── decision: сервер віддає РІШЕННЯ, не файл ───────────────────────────────────
def fig_decision():
    W, H = 720, 380
    f = [COL_MARKERS]
    # сервер у центрі ліворуч
    f.append(block(40, 150, 150, 90, ["СЕРВЕР OTA", "ухвалює", "рішення"],
                   "#eef4ff", NEG, size=14))
    f.append(text(115, 270, "дивиться: залізо,", size=11, color=MUTED))
    f.append(text(115, 286, "версія, група", size=11, color=MUTED))

    # три пристрої праворуч, різні
    dev = [
        (470, 60, ["ESP32", "v1.8"], "→ дай v2.4.1", FIELD, "G"),
        (470, 170, ["C3", "v2.4.1"], "→ лишайся як є", MUTED, "B"),
        (470, 280, ["ESP32", "v2.0"], "→ дай ІНШИЙ образ", FIELD, "G"),
    ]
    for (dx, dy, dl, ans, col, mid) in dev:
        f.append(block(dx, dy - 28, 110, 56, dl, FILL, LINE, size=12))
        # запит угору, відповідь униз — стрілка від сервера до пристрою
        f.append(carrow(195, 195, dx - 6, dy, NEG, "B", sw=1.8))
        f.append(text(dx + 120, dy - 4, "?", size=15, color=MUTED, anchor="start", bold=True))
        f.append(text(dx + 8, dy + 46, ans, size=11.5, color=col, anchor="start", bold=True))

    f.append(text(330, 30, "однакове питання «що мені залити?» — РІЗНІ відповіді",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(OUT, "decision.svg"), W, H, *f)


# ── channels: nightly → beta → stable ────────────────────────────────────────
def fig_channels():
    W, H = 720, 360
    f = [COL_MARKERS]
    f.append(text(W / 2, 30, "Одна збірка дозріває по каналах", size=15, bold=True))

    # три горизонтальні русла
    rows = [
        (80, "nightly", "розробники · одиниці", POS, "v2.5.0-nightly"),
        (170, "beta", "добровольці · малий %", "#d68910", "v2.5.0-beta"),
        (260, "stable", "основна маса · увесь парк", FIELD, "v2.4.1"),
    ]
    for (ry, name, who, col, ver) in rows:
        f.append(rect(60, ry, 600, 64, fill="#fbfcfd", stroke=col, sw=1.8, rx=10))
        f.append(text(90, ry + 28, name, size=15, color=col, anchor="start", bold=True))
        f.append(text(90, ry + 48, who, size=11, color=MUTED, anchor="start"))
        f.append(text(640, ry + 38, ver, size=12.5, color=INK, anchor="end", bold=True))

    # стрілки дозрівання згори вниз (вузька група → ширша)
    f.append(carrow(360, 144, 360, 168, NEG, "B"))
    f.append(carrow(360, 234, 360, 258, NEG, "B"))
    f.append(text(380, 160, "визріло", size=10.5, color=MUTED, anchor="start"))
    f.append(text(380, 250, "перевірено", size=10.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, 348, "чим стабільніший канал — тим повільніша й безпечніша течія",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "channels.svg"), W, H, *f)


# ── rollout: щаблі 5 → 20 → 50 → 100 % ───────────────────────────────────────
def fig_rollout():
    W, H = 720, 360
    f = [COL_MARKERS]
    f.append(text(W / 2, 30, "Поетапне розгортання обмежує радіус ураження", size=14.5, bold=True))

    base = 300          # вісь
    steps = [("canary", 5, FIELD), ("20%", 20, FIELD), ("50%", 50, "#d68910"), ("100%", 100, NEG)]
    x = 90
    bw = 110
    gap = 40
    maxh = 200
    for i, (lab, pct, col) in enumerate(steps):
        h = maxh * pct / 100.0
        bx = x + i * (bw + gap)
        f.append(rect(bx, base - h, bw, h, fill="#eef4ff" if col == NEG else "#eafaf1",
                      stroke=col, sw=1.8, rx=8))
        f.append(text(bx + bw / 2, base - h - 10, "%d%%" % pct, size=14, color=col, bold=True))
        f.append(text(bx + bw / 2, base + 22, lab, size=12, color=INK, bold=True))
        if i < len(steps) - 1:
            ax = bx + bw + 6
            f.append(carrow(ax, base - 30, ax + gap - 12, base - 30, NEG, "B", sw=1.8))
    # рубильник напоготові
    f.append(text(W / 2, base + 56, "на КОЖНОМУ щаблі — рубильник: біда → стоп, решта на старій версії",
                  size=11.5, color=POS, bold=True))
    f.append(text(W / 2, 70, "сервер дивиться на здоров'я й піднімає частку лише, якщо група жива",
                  size=11.5, color=MUTED))
    render(os.path.join(OUT, "rollout.svg"), W, H, *f)


# ── fleet: двобічна вулиця рішення↓ звіт↑ → карта парку ──────────────────────
def fig_fleet():
    W, H = 720, 380
    f = [COL_MARKERS]
    f.append(text(W / 2, 28, "OTA — двобічна вулиця", size=15, bold=True))

    f.append(block(60, 150, 150, 90, ["СЕРВЕР"], "#eef4ff", NEG, size=15))
    f.append(block(510, 150, 150, 90, ["ПАРК", "пристроїв"], FILL, LINE, size=13))

    # униз: рішення
    f.append(carrow(215, 175, 505, 175, FIELD, "G", sw=2.2))
    f.append(text(360, 165, "рішення ↓  маніфест · образ", size=12, color=FIELD, bold=True))
    # вгору: звіт
    f.append(carrow(505, 215, 215, 215, NEG, "B", sw=2.2))
    f.append(text(360, 235, "звіт ↑  версія · вдалося? · живий?", size=12, color=NEG, bold=True))

    # карта парку
    f.append(rect(180, 290, 360, 70, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=10))
    f.append(text(360, 312, "карта парку зі звітів:", size=12, color=INK, bold=True))
    f.append(text(360, 332, "розподіл версій · частка успіху свіжого оновлення", size=11.5, color=MUTED))
    f.append(text(360, 350, "саме частка успіху вирішує: піднімати щабель чи смикати рубильник", size=10.5, color=POS))
    render(os.path.join(OUT, "fleet.svg"), W, H, *f)


# ── pipeline: розробник підписує → сервер роздає → пристрій судить ───────────
def fig_pipeline():
    W, H = 720, 320
    f = [COL_MARKERS]
    f.append(text(W / 2, 30, "Де в конвеєрі живе підпис", size=15, bold=True))

    y = 110
    h = 84
    # розробник / складання
    f.append(block(40, y, 180, h, ["РОЗРОБНИК", "(складання)", "ПІДПИСУЄ образ"], "#fdecea", POS, size=12.5))
    f.append(text(130, y + h + 22, "🔑 таємний ключ", size=12, color=POS, bold=True))
    f.append(text(130, y + h + 40, "нікуди звідси не виходить", size=10.5, color=MUTED))
    # сервер
    f.append(block(270, y, 180, h, ["СЕРВЕР OTA", "тільки РОЗДАЄ", "ключа НЕ має"], "#eef4ff", NEG, size=12.5))
    # пристрій
    f.append(block(500, y, 180, h, ["ПРИСТРІЙ", "СУДИТЬ образ", "перед запуском"], "#eafaf1", FIELD, size=12.5))
    f.append(text(590, y + h + 22, "🔓 відкритий ключ", size=12, color=FIELD, bold=True))

    f.append(carrow(222, y + h / 2, 268, y + h / 2, NEG, "B"))
    f.append(carrow(452, y + h / 2, 498, y + h / 2, NEG, "B"))
    f.append(text(245, y + h / 2 - 10, "підписане", size=10, color=MUTED))
    f.append(text(475, y + h / 2 - 10, "підписане", size=10, color=MUTED))

    f.append(text(W / 2, 285, "зламали сервер → нападник РОЗДАЄ образи, та ПІДПИСАТИ свій не зможе",
                  size=12, color=POS, bold=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *f)


# ── mirai-cascade: камери на дефолтних паролях → Mirai → Dyn → впали сайти ────
def fig_mirai_cascade():
    W, H = 760, 360
    f = [COL_MARKERS]
    f.append(text(W / 2, 28, "Каскад 2016-го: дешева камера поклала пів-інтернету", size=14.5, bold=True))

    # 1. армія камер на стандартних паролях
    f.append(block(30, 110, 150, 96, ["~150 тис. камер", "і DVR", "пароль admin"],
                   "#fdecea", POS, size=12))
    f.append(text(105, 226, "стандартні", size=10.5, color=MUTED))
    f.append(text(105, 242, "заводські паролі", size=10.5, color=MUTED))

    # 2. Mirai збирає в ботнет
    f.append(block(230, 110, 140, 96, ["MIRAI", "перебір 62 пар", "логін/пароль"],
                   "#fdecea", POS, size=12))
    f.append(text(300, 226, "росте сама,", size=10.5, color=MUTED))
    f.append(text(300, 242, "як епідемія", size=10.5, color=MUTED))

    # 3. удар по DNS Dyn
    f.append(block(420, 110, 140, 96, ["удар по Dyn", "(DNS-служба)", "~1.2 Тбіт/с"],
                   "#eef4ff", NEG, size=12))
    f.append(text(490, 226, "21.10.2016", size=10.5, color=MUTED))
    f.append(text(490, 242, "телефонна книга", size=10.5, color=MUTED))

    # 4. впали сайти
    f.append(block(605, 110, 130, 96, ["недосяжні:", "Twitter, GitHub", "Netflix, Reddit"],
                   FILL, LINE, size=11.5))
    f.append(text(670, 226, "самі живі —", size=10.5, color=MUTED))
    f.append(text(670, 242, "адреси не знайти", size=10.5, color=MUTED))

    # стрілки каскаду
    f.append(carrow(182, 158, 228, 158, POS, "R", sw=2.0))
    f.append(carrow(372, 158, 418, 158, POS, "R", sw=2.0))
    f.append(carrow(562, 158, 603, 158, NEG, "B", sw=2.0))

    f.append(text(W / 2, 300, "вразливість — не код сайтів, а заводський пароль у двадцятидоларовій камері",
                  size=12, color=POS, bold=True))
    f.append(text(W / 2, 322, "зброєю стали РЕЧІ звичайних людей, оновлювані абияк або ніяк",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "mirai-cascade.svg"), W, H, *f)


# ── channel-vs-cargo: захист труби проти захисту вантажу ──────────────────────
def fig_channel_vs_cargo():
    W, H = 760, 380
    f = [COL_MARKERS]
    f.append(text(W / 2, 28, "Дві моделі захисту — і чому перша провалюється", size=14.5, bold=True))

    # ── верх: захист каналу (провал) ──
    yA = 70
    f.append(text(40, yA, "Захист КАНАЛУ (HTTPS): береже лише трубу", size=12.5,
                  color=POS, anchor="start", bold=True))
    f.append(block(60, yA + 18, 150, 64, ["СЕРВЕР", "зламаний"], "#fdecea", POS, size=12))
    f.append(block(560, yA + 18, 150, 64, ["ПРИСТРІЙ", "вірить трубі"], FILL, LINE, size=12))
    # труба (порожня всередині, щоб під нею пройшла стрілка «отрути»)
    f.append(rect(215, yA + 22, 340, 56, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=14))
    f.append(text(385, yA + 40, "шифрована труба ✓ ціла", size=11.5, color=FIELD, bold=True))
    f.append(carrow(232, yA + 62, 538, yA + 62, POS, "R", sw=2.2))
    f.append(text(385, yA + 102, "труба чесно везе ОТРУТУ — зламаний сервер пройшов як свій",
                  size=11.5, color=POS, anchor="middle", bold=True))

    # роздільник
    f.append(line(40, 222, W - 40, 222, MUTED, 1.0, dash="4 4"))

    # ── низ: захист вантажу (рятує) ──
    yB = 250
    f.append(text(40, yB, "Захист ВАНТАЖУ (TUF / Uptane / підпис): перевірка на місці", size=12.5,
                  color=FIELD, anchor="start", bold=True))
    f.append(block(60, yB + 18, 150, 64, ["СЕРВЕР", "роздає"], "#eef4ff", NEG, size=12))
    f.append(block(560, yB + 18, 150, 64, ["ПРИСТРІЙ", "СУДИТЬ образ"], "#eafaf1", FIELD, size=12))
    f.append(carrow(215, yB + 50, 555, yB + 50, NEG, "B", sw=2.0))
    f.append(text(385, yB + 40, "образ із підписом", size=11, color=MUTED))
    # замок перевірки на пристрої
    f.append(text(635, yB + 100, "🔓 перевірка перед запуском", size=11, color=FIELD, anchor="middle", bold=True))
    f.append(text(300, yB + 100, "не довіряє ні трубі, ні серверу", size=11, color=FIELD, anchor="middle", bold=True))
    render(os.path.join(OUT, "channel-vs-cargo.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision()
    fig_channels()
    fig_rollout()
    fig_fleet()
    fig_pipeline()
    fig_mirai_cascade()
    fig_channel_vs_cargo()
    print("ok: 7 figures ->", OUT)
