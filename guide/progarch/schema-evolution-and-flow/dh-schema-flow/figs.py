# -*- coding: utf-8 -*-
"""Фігури до кроку dh-schema-flow (курс progarch, модуль «Еволюція схем, матеріалізація, рух даних»).
Три фігури: (1) життя числа у звіті; (2) джерело правди проти похідного; (3) ідемпотентний перерахунок вікна."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL = "#fdecea"
MUTE_FILL = "#f0f1f3"


def tb(cx, cy, s, **kw):
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag, w, h


# ── Фігура 1: життя числа у звіті ────────────────────────────────────────────
def fig_journey():
    W, H = 1180, 380
    f = []
    cy = 200

    b1, w1, _ = tb(170, cy,
                   "Сирі виміри — незмінні\n"
                   "fw ≤ 2.0:  {schema:1, w:812}\n"
                   "fw ≥ 2.1:  {schema:2, wh:145203}\n"
                   "мільйони рядків · багато прошивок",
                   size=13, stroke=FIELD, fill=GREEN_FILL)
    b2, w2, _ = tb(500, cy,
                   "Зведення до канону\nза схемою КОЖНОГО рядка\n→ канонічний Вт·год",
                   size=13)
    b3, w3, _ = tb(770, cy,
                   "Денний агрегат\nматеріалізований\nкВт·год / дім / день",
                   size=13, stroke=NEG, fill="#eef2fc")
    b4, w4, _ = tb(1020, cy,
                   "Звіт родині\nцього місяця\n318 кВт·год",
                   size=13, stroke=INK, fill=FILL, bold=False)

    # стрілки між стадіями (від краю до краю)
    e1 = 170 + w1 / 2
    s2 = 500 - w2 / 2
    e2 = 500 + w2 / 2
    s3 = 770 - w3 / 2
    e3 = 770 + w3 / 2
    s4 = 1020 - w4 / 2
    f.append(arrow(e1, cy, s2, cy, color=LINE))
    f.append(arrow(e2, cy, s3, cy, color=LINE))
    f.append(arrow(e3, cy, s4, cy, color=LINE))

    # підписи над стрілками
    f.append(text((e1 + s2) / 2, cy - 22, "schema-on-read", size=11, color=MUTED))
    f.append(text((e2 + s3) / 2, cy - 22, "ETL → аналітичне", size=11, color=MUTED))
    f.append(text((e3 + s4) / 2, cy - 22, "показ", size=11, color=MUTED))

    f += [b1, b2, b3, b4]
    f.append(text(W / 2, 350,
                  "багато різнорідних сирих рядків   →   одне число у звіті",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'number-journey.svg'), W, H, *f)


# ── Фігура 2: джерело правди проти похідного (перебудовного) ──────────────────
def fig_source_derived():
    W, H = 1020, 410
    f = []

    raw, wr, hr = tb(205, 185,
                     "Сирі виміри\nджерело правди\nнезмінні · на диску",
                     size=14, stroke=FIELD, fill=GREEN_FILL, pad=14)

    # група «похідне» — рамка-контейнер + два блоки всередині
    gx, gy, gw, gh = 630, 118, 310, 150
    f.append(rect(gx, gy, gw, gh, fill=MUTE_FILL, stroke=MUTED, sw=1.5))
    f.append(text(gx + gw / 2, gy - 10, "похідне · перебудовне", size=12, color=MUTED))
    d1, _, _ = tb(gx + gw / 2, 158, "Денний агрегат\nматеріалізований", size=13, stroke=MUTED)
    d2, _, _ = tb(gx + gw / 2, 222, "Звіт: 318 кВт·год", size=13, stroke=MUTED)

    er = 205 + wr / 2
    # пряма стрілка: сире → похідне (агрегуємо)
    f.append(arrow(er, 165, gx, 165, color=LINE))
    f.append(text((er + gx) / 2, 150, "агрегуємо", size=12, color=INK))
    # зворотна стрілка: перебудувати з сирого (нижче, окремо)
    f.append(arrow(gx, 222, er, 222, color=FIELD, sw=2))
    f.append(text((er + gx) / 2, 240, "перебудувати з сирого будь-коли", size=12, color=FIELD))

    f += [raw, d1, d2]

    note, _, _ = tb(W / 2, 350,
                    "Кеш (модуль 13) вводив ДРУГЕ джерело правди, що тихо дрейфує.\n"
                    "Тут похідне теж може розійтися з сирим — але сире незмінне, тож будь-яку\n"
                    "розбіжність лікуємо, відкинувши й перебудувавши похідне з нуля.",
                    size=12, stroke=MUTED, fill=BG, color=INK)
    f.append(note)
    render(os.path.join(IMG, 'source-vs-derived.svg'), W, H, *f)


# ── Фігура 3: ідемпотентний перерахунок вікна ────────────────────────────────
def fig_reprocess():
    W, H = 1060, 380
    f = []
    f.append(text(W / 2, 50, "Денні рядки місяця (кВт·год / день)", size=14, bold=True))

    x0, cw, gap, ytop, ch = 60, 28, 3, 90, 44
    step = cw + gap
    bad_lo, bad_hi = 9, 22  # індекси зіпсованого вікна (включно)
    for i in range(30):
        x = x0 + i * step
        bad = bad_lo <= i <= bad_hi
        f.append(rect(x, ytop, cw, ch,
                      fill=RED_FILL if bad else GREEN_FILL,
                      stroke=POS if bad else FIELD, sw=1.5, rx=3))

    win_cx = x0 + ((bad_lo + bad_hi + 1) / 2) * step - gap / 2

    # легенда
    ly = 172
    f.append(rect(120, ly - 12, 20, 20, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=3))
    f.append(text(152, ly + 3, "правильні дні", size=12, color=INK, anchor="start"))
    f.append(rect(300, ly - 12, 20, 20, fill=RED_FILL, stroke=POS, sw=1.5, rx=3))
    f.append(text(332, ly + 3, "вікно з багом: схему прочитано хибно", size=12, color=INK, anchor="start"))

    # стрілка від вікна вниз до блоку перерахунку
    f.append(arrow(win_cx, ytop + ch + 4, win_cx, 212, color=POS, sw=2))

    box, wbx, _ = tb(win_cx, 262,
                     "Перерахунок вікна\n"
                     "взяти СИРЕ за ці дні\n"
                     "обчислити наново\n"
                     "ЗАМІНИТИ денні рядки (upsert за дім+день)",
                     size=12, stroke=NEG, fill="#eef2fc")

    idem, _, _ = tb(900, 262,
                    "прогін 1× → 291\n"
                    "прогін 3× → 291\n"
                    "= той самий результат\n(ідемпотентно)",
                    size=12, stroke=FIELD, fill=GREEN_FILL)
    f.append(arrow(win_cx + wbx / 2, 262, 900 - 120, 262, color=LINE))

    f += [box, idem]
    f.append(text(win_cx, 330, "зелені дні не чіпаємо — їх уже пораховано правильно",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'reprocess-window.svg'), W, H, *f)


# ── Фігура 4: конвеєр DH — що якою мовою рахується (до proj-вставки) ───────────
def fig_pipeline_stages():
    W, H = 1220, 380
    f = []
    cy = 150
    x1, x2, x3, x4 = 175, 480, 785, 1075

    b1, w1, _ = tb(x1, cy,
                   "Оперативне сховище\nсирі виміри · незмінні",
                   size=13, stroke=FIELD, fill=GREEN_FILL)
    b2, w2, _ = tb(x2, cy,
                   "Декод рядок-за-рядком\nPython · гілка за schema\n→ канонічний Вт·год",
                   size=13)
    b3, w3, _ = tb(x3, cy,
                   "Згортка множинна\nSQL · GROUP BY дім,день\n→ кВт·год / день",
                   size=13, stroke=NEG, fill="#eef2fc")
    b4, w4, _ = tb(x4, cy,
                   "Аналітичне сховище\ndaily_kwh + родовід",
                   size=13, stroke=MUTED, fill=MUTE_FILL)

    e1, s2 = x1 + w1 / 2, x2 - w2 / 2
    e2, s3 = x2 + w2 / 2, x3 - w3 / 2
    e3, s4 = x3 + w3 / 2, x4 - w4 / 2
    f.append(arrow(e1, cy, s2, cy, color=LINE))
    f.append(arrow(e2, cy, s3, cy, color=LINE))
    f.append(arrow(e3, cy, s4, cy, color=LINE))
    f.append(text((e1 + s2) / 2, cy - 20, "extract: ts-вікно + carry-in", size=11, color=MUTED))
    f.append(text((e2 + s3) / 2, cy - 20, "канон Вт·год", size=11, color=MUTED))
    f.append(text((e3 + s4) / 2, cy - 20, "upsert (дім, день)", size=11, color=MUTED))

    f += [b1, b2, b3, b4]

    # петля перерахунку: з аналітичного назад над сирим
    ly = 250
    f.append(line(x4, cy + 32, x4, ly, color=FIELD, sw=2))
    f.append(line(x1, cy + 32, x1, ly, color=FIELD, sw=2))
    f.append(arrow(x4, ly, x1, ly, color=FIELD, sw=2))
    f.append(text((x1 + x4) / 2, ly - 8,
                  "reprocess = run_etl(вікно) знову  →  upsert ЗАМІНЮЄ рядок (ідемпотентно)",
                  size=12, color=FIELD))

    f.append(text(W / 2, 330,
                  "рядок-за-рядком (Python): гілки, незручні для SQL      ·      "
                  "множинно (SQL): згортка над мільйонами рядків",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'pipeline-stages.svg'), W, H, *f)


# ── Фігура 5: родовід дисципліни (часова смуга; вставка hist-reprocessing-lineage) ──
def fig_lineage():
    W, H = 1220, 470
    f = []
    axis_y = 180
    f.append(line(70, axis_y, W - 70, axis_y, color=INK, sw=2))
    xs = [255, 610, 965]
    data = [
        ("2011", True, FIELD, GREEN_FILL,
         "Нейтан Марз (Nathan Marz)\n«How to beat the CAP theorem»\nQuery = Function(All Data):\nнезмінне сире + перерахунок\n(назву «Lambda» дадуть згодом)"),
        ("2013", False, NEG, "#eef2fc",
         "Джей Крепс (Jay Kreps)\n«The Log»\nдописуваний журнал —\nуніверсальне джерело правди"),
        ("2014", True, NEG, "#eef2fc",
         "Джей Крепс\n«Questioning the Lambda…»\nKappa: перерахунок =\nповторне програвання журналу;\nзасновано Confluent"),
    ]
    for x, (yr, above, st, fl, txt) in zip(xs, data):
        f.append(circle(x, axis_y, 7, fill=BG, stroke=INK, sw=2))
        if above:
            by = 105
            b, w, h = tb(x, by, txt, size=12, stroke=st, fill=fl)
            f.append(line(x, axis_y - 10, x, by + h / 2, color=MUTED, sw=1.2, dash="3,3"))
            # рік — ЗБОКУ від пунктирного зв'язку (не в стовпчику лінії), щоб не перетинала напис
            f.append(text(x + 26, axis_y - 8, yr, size=17, bold=True, anchor="start"))
        else:
            by = 300
            b, w, h = tb(x, by, txt, size=12, stroke=st, fill=fl)
            f.append(line(x, axis_y + 10, x, by - h / 2, color=MUTED, sw=1.2, dash="3,3"))
            f.append(text(x + 26, axis_y + 26, yr, size=17, bold=True, anchor="start"))
        f.append(b)
    band, _, _ = tb(W / 2, 415,
                    "Спільна дисципліна, до якої зійшлися обидві школи:\n"
                    "СИРЕ — незмінне й лише дописується; ПОХІДНЕ — завжди перебудовне з сирого.",
                    size=13, stroke=FIELD, fill=GREEN_FILL)
    f.append(band)
    render(os.path.join(IMG, 'lineage-timeline.svg'), W, H, *f,
           title="Родовід: «сире незмінне, похідне переобчислюй, щоб виправити»")


# ── Фігура 6: Lambda (два шари) проти Kappa (один журнал) ─────────────────────
def fig_lambda_kappa():
    W, H = 1220, 470
    f = []
    f.append(line(W / 2, 60, W / 2, 350, color=MUTED, sw=1, dash="4,4"))
    f.append(text(305, 44, "Lambda — Нейтан Марз, 2011", size=15, bold=True))
    f.append(text(915, 44, "Kappa — Джей Крепс, 2014", size=15, bold=True))

    # ── Lambda (ліворуч): незмінне сире → два шари → serving ──
    raw, wr, _ = tb(150, 175, "Незмінний\nmaster dataset\nсире · лише дописуємо",
                    size=12, stroke=FIELD, fill=GREEN_FILL)
    batch, wb, _ = tb(400, 110, "Пакетний шар\nперерахунок з нуля\nповільно · точно",
                      size=12, stroke=NEG, fill="#eef2fc")
    speed, ws, _ = tb(400, 245, "Швидкісний шар\nпотік · наближено\nшвидко · неточно",
                      size=12, stroke=MUTED, fill=MUTE_FILL)
    serv, wsv, _ = tb(575, 178, "Serving\nзлити\nобидва", size=12)
    f.append(arrow(150 + wr / 2, 165, 400 - wb / 2, 118, color=LINE))
    f.append(arrow(150 + wr / 2, 188, 400 - ws / 2, 238, color=LINE))
    f.append(arrow(400 + wb / 2, 120, 575 - wsv / 2, 168, color=LINE))
    f.append(arrow(400 + ws / 2, 238, 575 - wsv / 2, 190, color=LINE))
    f += [raw, batch, speed, serv]
    f.append(text(305, 328, "дві бази коду — тримати в такт", size=12, color=POS))

    # ── Kappa (праворуч): незмінний журнал → одна обробка → таблиця; перерахунок = переграти ──
    log, wl, hl = tb(770, 175, "Відтворюваний\nжурнал подій\nєдине джерело правди",
                     size=12, stroke=FIELD, fill=GREEN_FILL)
    strm, wst, hst = tb(985, 175, "Потокова\nобробка\n(одна)", size=12, stroke=NEG, fill="#eef2fc")
    tbl, wtb, _ = tb(1140, 175, "Таблиця-\nрезультат", size=12)
    f.append(arrow(770 + wl / 2, 175, 985 - wst / 2, 175, color=LINE))
    f.append(arrow(985 + wst / 2, 175, 1140 - wtb / 2, 175, color=LINE))
    # петля перерахунку: від обробки вниз і назад у журнал
    f.append(line(985, 175 + hst / 2, 985, 300, color=FIELD, sw=1.5, dash="4,3"))
    f.append(line(985, 300, 770, 300, color=FIELD, sw=1.5, dash="4,3"))
    f.append(arrow(770, 300, 770, 175 + hl / 2, color=FIELD, sw=1.5))
    f += [log, strm, tbl]
    f.append(text(915, 328, "перерахунок = перечитати журнал крізь новий код", size=12, color=FIELD))

    # ── спільне ядро ──
    band, _, _ = tb(W / 2, 412,
                    "Спільне ядро обох: СИРЕ (master dataset / журнал) — незмінне й лише дописується;\n"
                    "будь-яку помилку в ПОХІДНОМУ лікують перерахунком з сирого, а не правкою на місці.",
                    size=13, stroke=FIELD, fill=GREEN_FILL)
    f.append(band)
    render(os.path.join(IMG, 'lambda-vs-kappa.svg'), W, H, *f)


if __name__ == '__main__':
    fig_journey()
    fig_source_derived()
    fig_reprocess()
    fig_pipeline_stages()
    fig_lineage()
    fig_lambda_kappa()
    print("OK: 6 SVG -> img/")
