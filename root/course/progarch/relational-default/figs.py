# -*- coding: utf-8 -*-
"""Фігури до кроку «„Нудне“ реляційне за замовчуванням»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

JOBS = ["облік і звʼязки", "телеметрія", "сесії", "черга задач", "пошук і документи"]


def fig_one_vs_many():
    """Ті самі пʼять робіт: ліворуч на одному Postgres, праворуч на пʼяти сховищах.
    Контраст — не в можливостях, а в кількості систем, які треба тримати добре."""
    W, H = 1180, 600
    frags = []

    frags.append(line(590, 48, 590, 560, color=MUTED, sw=1, dash="4,6"))
    frags.append(text(300, 66, "Один нудний рушій", size=16, bold=True))
    frags.append(text(880, 66, "Пʼять збуджених рушіїв", size=16, bold=True))

    ys = [130, 200, 270, 340, 410]

    # ── ліва панель: пілюлі-роботи сходяться в один Postgres ──
    for job, y in zip(JOBS, ys):
        b, _, _ = textbox(160, y, job, size=12, fill="#eef2fb", min_w=170)
        frags.append(b)
    # центральний Postgres
    frags.append(rect(380, 165, 150, 210, fill="#eafaf0", stroke=FIELD, sw=2.2))
    frags.append(text(455, 262, "PostgreSQL", size=16, bold=True, color=FIELD))
    frags.append(text(455, 286, "один рушій", size=12, color=MUTED))
    for y in ys:
        frags.append(arrow(247, y, 378, 270, color=FIELD, sw=1.7))
    b, _, _ = textbox(300, 490, "один бекап · одна модель відмови · одне чергування",
                      size=12.5, fill="#eafaf0", stroke=FIELD, min_w=500)
    frags.append(b)

    # ── права панель: кожна робота — власне сховище ──
    stores = ["Postgres", "InfluxDB", "Redis", "RabbitMQ", "Elasticsearch"]
    for job, store, y in zip(JOBS, stores, ys):
        b, _, _ = textbox(700, y, job, size=12, fill="#eef2fb", min_w=170)
        frags.append(b)
        b, _, _ = textbox(1010, y, store, size=12, fill="#fdecea", stroke=POS, min_w=150)
        frags.append(b)
        frags.append(arrow(787, y, 933, y, color=POS, sw=1.7))
    b, _, _ = textbox(880, 490, "пʼять бекапів · пʼять моделей відмови · пʼять чергувань",
                      size=12.5, fill="#fdecea", stroke=POS, min_w=520)
    frags.append(b)

    render(os.path.join(IMG, "one-vs-many.svg"), W, H, *frags,
           title="Один рушій на пʼять робіт проти пʼяти рушіїв")


def fig_data_gravity():
    """Вісь зворотності: код за швом — легко назад; вибір сховища — коло незворотного
    кінця, і що більше даних натекло, то далі туди сповзає (стос росте)."""
    W, H = 1120, 470
    frags = []

    x0, x1 = 110, 985
    axis_y = 300
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.8))
    frags.append(mtext(x0 + 6, axis_y + 30, ["зворотне", "двобічні двері"],
                       size=12, color=MUTED, anchor="start"))
    frags.append(mtext(x1 - 6, axis_y + 30, ["незворотне", "однобічні двері"],
                       size=12, color=MUTED, anchor="end"))
    frags.append(text((x0 + x1) / 2, axis_y + 52, "росте ціна відкату  →",
                      size=12, color=MUTED))

    # маркери-пілюлі над віссю з тиком до осі
    def marker(x, label, cy=180, hi=False):
        out = []
        fill = "#fdecea" if hi else FILL
        stroke = POS if hi else LINE
        b, _, h = textbox(x, cy, label, size=12.5, fill=fill, stroke=stroke,
                          bold=hi, min_w=0)
        out.append(b)
        out.append(line(x, cy + h / 2, x, axis_y - 2, color=MUTED, sw=1.2, dash="3,4"))
        return out

    frags += marker(250, "структура коду за швом")
    frags += marker(455, "формат конфіга")
    frags += marker(640, "ORM за репозиторієм")

    # ── вибір сховища: пілюля вище, під нею стос даних, що росте ──
    sx = 862
    b, _, _ = textbox(sx, 132, "ВИБІР СХОВИЩА", size=13, fill="#fdecea",
                      stroke=POS, bold=True, min_w=176)
    frags.append(b)
    stack_y = 176
    for i, w in enumerate((70, 100, 130, 160)):
        yy = stack_y + i * 22
        frags.append(rect(sx - w / 2, yy, w, 16, fill="#f6dcd7", stroke=POS, sw=1.2, rx=3))
    frags.append(line(sx, stack_y + 4 * 22, sx, axis_y - 2, color=POS, sw=1.4))
    frags.append(text(sx, 174, "тяжіння даних росте", size=11, color=MUTED))

    frags.append(mtext((x0 + x1) / 2, 405,
                       ["коло правого кінця: мільйони рядків · живий трафік · споживачі нижче за течією"],
                       size=12.5, color=MUTED))

    render(os.path.join(IMG, "data-gravity.svg"), W, H, *frags,
           title="Дані мають тяжіння: сховище сповзає до незворотного кінця")


def fig_default_gate():
    """Ворота дефолту: одне питання — чи є ВИМІРЯНИЙ сценарій проти Postgres.
    Ні → нудне + записана розтяжка. Так → спеціалізоване, але зміряй драйвер спершу."""
    W, H = 1060, 560
    frags = []

    b, _, _ = textbox(530, 82, "Треба зберігати дані застосунку", size=13,
                      fill=FILL, min_w=340)
    frags.append(b)
    frags.append(arrow(530, 102, 530, 180, color=LINE, sw=1.8))

    # ворота-питання
    b, _, gh = textbox(530, 208, "Чи є ВИМІРЯНИЙ сценарій, що ламає Postgres?\n"
                       "(драйвер + число-межа)", size=13, fill="#eef2fb",
                       stroke=NEG, bold=False, min_w=460)
    frags.append(b)

    # ліва гілка «ні»
    frags.append(arrow(430, 236, 300, 329, color=FIELD, sw=1.8))
    frags.append(text(338, 266, "ні", size=13, color=FIELD, bold=True))
    b, _, _ = textbox(280, 348, "PostgreSQL за замовчуванням", size=13,
                      fill="#eafaf0", stroke=FIELD, bold=True, min_w=280)
    frags.append(b)
    frags.append(arrow(280, 372, 280, 443, color=FIELD, sw=1.7))
    b, _, _ = textbox(280, 470, "запиши сигнальну розтяжку:\n"
                      "число під моніторингом (фітнес-функція)", size=12,
                      fill="#f7f9fc", stroke=MUTED, min_w=340)
    frags.append(b)

    # права гілка «так»
    frags.append(arrow(630, 236, 762, 329, color=POS, sw=1.8))
    frags.append(text(724, 268, "так", size=13, color=POS, bold=True))
    b, _, _ = textbox(790, 348, "спеціалізоване сховище", size=13,
                      fill="#fdecea", stroke=POS, bold=True, min_w=260)
    frags.append(b)
    frags.append(mtext(790, 402, ["назви драйвер і виміряй його ж",
                                  "на Postgres спершу"], size=12, color=MUTED))

    render(os.path.join(IMG, "default-gate.svg"), W, H, *frags,
           title="Ворота дефолту: нудне, поки виміряний сценарій не скаже інакше")


def fig_boring_pendulum():
    """Маятник галузевої моди на сховища: зерна масштабу (Bigtable/Dynamo) → пік
    «web scale» → сатира → «жетони новизни» Маккінлі → «просто візьми Postgres» →
    Postgres №1. Гаряча заливка під кривою = «температура» моди на спеціалізоване."""
    W, H = 1320, 560
    frags = []
    x0, x1 = 110, 1210
    axis_y = 346

    # ── крива «температури моди» (вище = гарячіше) ──
    pts = [(150, 306), (300, 236), (360, 198), (475, 124), (565, 110),
           (665, 152), (830, 214), (990, 272), (1120, 308)]
    poly = " ".join("%d,%d" % p for p in pts) + " %d,%d %d,%d" % (
        pts[-1][0], axis_y, pts[0][0], axis_y)
    frags.append('<polygon points="%s" fill="#fdecea" stroke="none"/>' % poly)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join("%d,%d" % p for p in pts), POS))

    # підписи піку й повернення
    frags.append(mtext(565, 74, ["пік «web scale»",
                                 "під кожну форму даних — свій модний двигун"],
                       size=12.5, color=POS, bold=True))
    frags.append(mtext(1035, 246, ["маятник назад:", "нудне за замовчуванням"],
                       size=12.5, color=FIELD, bold=True))

    # ── вісь ──
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=1.8))

    # ── події: тік на осі + пілюля нижче з веденою лінією ──
    def event(cx, lines, low=False):
        out = [circle(cx, axis_y, 5, fill=POS, stroke=POS, sw=1)]
        cy = 480 if low else 406
        b, w, h = textbox(cx, cy, "\n".join(lines), size=11.5, fill="#f7f9fc",
                          stroke=LINE, min_w=156)
        out.append(line(cx, axis_y + 5, cx, cy - h / 2, color=MUTED, sw=1.1, dash="3,4"))
        out.append(b)
        return out

    frags += event(150, ["2006–07", "статті Bigtable · Dynamo", "(зерна масштабу)"])
    frags += event(300, ["2009", "зустріч «NoSQL» · MongoDB"], low=True)
    frags += event(360, ["2010", "сатира «web scale»"])
    frags += event(665, ["2015", "«Choose Boring Technology»", "жетони новизни"])
    frags += event(1120, ["2022–23", "«Just Use Postgres»", "Postgres — №1 у SO"])

    render(os.path.join(IMG, "boring-pendulum.svg"), W, H, *frags,
           title="Маятник моди: від «web scale» назад до нудного")


# ── Фігури до вставки proj-postgres-many-hats ───────────────────────────────

def fig_many_hats_schema():
    """Одна база — пʼять капелюхів: таблиця «таблиця/колонка · капелюх · механізм»
    у межах однієї коробки PostgreSQL. Виграш — одна межа відмови, не пʼять."""
    W, H = 1260, 600
    frags = []

    # межа однієї бази
    frags.append(rect(50, 60, 1160, 470, fill="#f2fbf6", stroke=FIELD, sw=2.4, rx=14))
    frags.append(text(80, 98, "PostgreSQL — один рушій", size=15, bold=True,
                      color=FIELD, anchor="start"))

    # заголовки колонок
    cx1, cx2, cx3 = 290, 640, 970
    frags.append(text(cx1, 140, "таблиця / колонка", size=13, bold=True, color=MUTED))
    frags.append(text(cx2, 140, "капелюх", size=13, bold=True, color=MUTED))
    frags.append(text(cx3, 140, "механізм", size=13, bold=True, color=MUTED))

    rows = [
        ("homes ← devices", "реляційне ядро", "FOREIGN KEY (home_id)"),
        ("devices.config",  "документ",       "GIN (config) · @>"),
        ("events.tsv",      "пошук",          "to_tsquery · GIN"),
        ("commands",        "черга",          "FOR UPDATE SKIP LOCKED"),
        ("telemetry",       "часоряд",        "(device_id, ts) · партиції"),
    ]
    ys = [195, 258, 321, 384, 447]
    for (t, hat, mech), y in zip(rows, ys):
        b, _, _ = textbox(cx1, y, t, size=12.5, fill="#eef2fb", min_w=230)
        frags.append(b)
        b, _, _ = textbox(cx2, y, hat, size=12.5, fill="#eafaf0", stroke=FIELD, min_w=200)
        frags.append(b)
        b, _, _ = textbox(cx3, y, mech, size=12.5, fill=FILL, min_w=330)
        frags.append(b)

    b, _, _ = textbox(630, 505, "одна база · один бекап · одне чергування",
                      size=13, fill="#eafaf0", stroke=FIELD, bold=True, min_w=520)
    frags.append(b)

    render(os.path.join(IMG, "many-hats-schema.svg"), W, H, *frags,
           title="Один PostgreSQL у пʼятьох капелюхах")


def fig_skip_locked_workers():
    """FOR UPDATE SKIP LOCKED: кожен воркер бере СВІЙ рядок, зайняте пропускає —
    три воркери, три різні задачі, нуль блокувань."""
    W, H = 1200, 560
    frags = []

    # таблиця commands праворуч
    frags.append(text(860, 70, "таблиця commands", size=14, bold=True))
    jobs = [
        ("#1   🔒 взято A", True),
        ("#2   🔒 взято B", True),
        ("#3   🔒 взято C", True),
        ("#4   готово",     False),
        ("#5   готово",     False),
        ("#6   готово",     False),
    ]
    ys = [115, 178, 241, 304, 367, 430]
    for (label, taken), y in zip(jobs, ys):
        fill = "#eafaf0" if taken else FILL
        stroke = FIELD if taken else LINE
        b, _, _ = textbox(860, y, label, size=12.5, fill=fill, stroke=stroke, min_w=250)
        frags.append(b)

    # воркери ліворуч, вирівняні до своїх рядків
    for name, y in (("воркер A", 115), ("воркер B", 178), ("воркер C", 241)):
        b, _, _ = textbox(150, y, name, size=12.5, fill="#eef2fb", min_w=150)
        frags.append(b)
        frags.append(arrow(228, y, 731, y, color=FIELD, sw=2))

    # пояснення пропуску
    frags.append(text(480, 205, "#1 зайнято → пропускаю, беру #2",
                      size=11.5, color=POS))

    b, _, _ = textbox(600, 495, "три воркери · три різні задачі · нуль блокувань",
                      size=13, fill="#eafaf0", stroke=FIELD, bold=True, min_w=520)
    frags.append(b)

    render(os.path.join(IMG, "skip-locked-workers.svg"), W, H, *frags,
           title="SKIP LOCKED: черга воркерів без блокувань")


def fig_where_postgres_ends():
    """Чесна межа: для кожного капелюха — де Postgres достатній (зелене) і за яким
    профілем виграє спеціаліст (червоне). Поріг — виміряне число."""
    W, H = 1300, 610
    frags = []

    cx1, cx2, cx3 = 150, 570, 1060
    frags.append(text(cx1, 92, "капелюх", size=13, bold=True, color=MUTED))
    frags.append(text(cx2, 92, "поки достатньо Postgres", size=13, bold=True, color=FIELD))
    frags.append(text(cx3, 92, "далі — спеціаліст", size=13, bold=True, color=POS))

    rows = [
        ("часоряд",     "десятки тис. вставок/с · гарячі в памʼяті",
         "TimescaleDB · колонкове\n(10⁵/с, TB, аналітика)"),
        ("черга",       "тисячі задач/с · короткі транзакції",
         "Kafka · RabbitMQ\n(backlog, порядок, фан-аут)"),
        ("пошук",       "базова релевантність, помірний корпус",
         "Elasticsearch\n(BM25, помилки, фасети)"),
        ("документ",    "гнучкі, помірні документи",
         "документна БД\n(величезні, шардинг)"),
        ("кеш / сесії", "епізодичний доступ",
         "Redis\n(суб-мс, ефемерне)"),
    ]
    ys = [165, 250, 335, 420, 505]
    for (hat, ok, spec), y in zip(rows, ys):
        b, _, _ = textbox(cx1, y, hat, size=12.5, fill="#eef2fb", min_w=180)
        frags.append(b)
        b, _, _ = textbox(cx2, y, ok, size=12, fill="#eafaf0", stroke=FIELD, min_w=540)
        frags.append(b)
        frags.append(arrow(846, y, 884, y, color=POS, sw=1.8))
        b, _, _ = textbox(cx3, y, spec, size=12, fill="#fdecea", stroke=POS, min_w=340)
        frags.append(b)

    b, _, _ = textbox(650, 570,
                      "спершу — розширення того самого Postgres:  "
                      "Citus · TimescaleDB · pgvector · pg_partman",
                      size=12.5, fill=FILL, stroke=FIELD, min_w=820)
    frags.append(b)

    render(os.path.join(IMG, "where-postgres-ends.svg"), W, H, *frags,
           title="Чесна межа: де Postgres перестає бути достатнім")


if __name__ == "__main__":
    fig_one_vs_many()
    fig_data_gravity()
    fig_default_gate()
    fig_boring_pendulum()
    fig_many_hats_schema()
    fig_skip_locked_workers()
    fig_where_postgres_ends()
    print("OK: one-vs-many.svg, data-gravity.svg, default-gate.svg, boring-pendulum.svg, "
          "many-hats-schema.svg, skip-locked-workers.svg, where-postgres-ends.svg")
