# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Кістяк ADR: сили → рішення → наслідки ───────────────────────────────────
# Форма змушує рухатися в одному напрямку. Контекст (сили) веде до рішення,
# рішення — до наслідків (і плюси, і мінуси). Угорі — заголовок і статус.
def fig_anatomy():
    W, H = 760, 470
    p = []
    p.append(text(W / 2, 28, "Кістяк ADR: сили ведуть до рішення, рішення — до наслідків", size=14, bold=True))

    cx = W / 2
    bw = 460                       # ширина блоків контексту/рішення/наслідків

    # ── Заголовок + Статус (вузька смуга вгорі) ──
    hy = 52
    p.append(rect(cx - bw / 2, hy, bw * 0.62, 34, fill="#f4f6f8", stroke=INK, sw=1.5))
    p.append(text(cx - bw / 2 + 14, hy + 15, "Заголовок", size=10.5, bold=True, anchor="start"))
    p.append(text(cx - bw / 2 + 14, hy + 29, "«0007. Гроші — в копійках, int64»", size=9.5, color=MUTED, anchor="start"))
    p.append(rect(cx - bw / 2 + bw * 0.66, hy, bw * 0.34, 34, fill="#eef6ff", stroke=NEG, sw=1.5))
    p.append(text(cx - bw / 2 + bw * 0.66 + bw * 0.17, hy + 15, "Статус", size=10.5, bold=True, color=NEG))
    p.append(text(cx - bw / 2 + bw * 0.66 + bw * 0.17, hy + 29, "ухвалено", size=9.5, color=MUTED))

    # ── КОНТЕКСТ (сили) ──
    ky = 112
    kh = 96
    p.append(rect(cx - bw / 2, ky, bw, kh, fill="#e7f7ee", stroke=FIELD, sw=1.8))
    p.append(text(cx - bw / 2 + 14, ky + 20, "КОНТЕКСТ — сили в грі (ще без рішення)", size=11.5, bold=True, color=FIELD, anchor="start"))
    forces = [
        "вимога: фінансовий звіт не має губити копійку",
        "факт: double дає похибку округлення на дробах",
        "обмеження: суми до мільярдів — int64 вміщує з запасом",
    ]
    for i, f in enumerate(forces):
        fy = ky + 42 + i * 17
        p.append(circle(cx - bw / 2 + 24, fy - 4, 3, fill=FIELD, stroke=FIELD, sw=1))
        p.append(text(cx - bw / 2 + 36, fy, f, size=10, color=INK, anchor="start"))

    # стрілка вниз: сили → рішення
    ay1 = ky + kh
    p.append(arrow(cx, ay1, cx, ay1 + 24, color=INK, sw=2))
    p.append(text(cx + 12, ay1 + 16, "випливає", size=9, color=MUTED, italic=True, anchor="start"))

    # ── РІШЕННЯ ──
    ry = ay1 + 28
    rh = 50
    p.append(rect(cx - bw / 2, ry, bw, rh, fill="#f4f6f8", stroke=INK, sw=2))
    p.append(text(cx - bw / 2 + 14, ry + 20, "РІШЕННЯ — активним голосом", size=11.5, bold=True, anchor="start"))
    p.append(text(cx - bw / 2 + 14, ry + 38, "«Ми зберігаємо гроші як int64 у копійках.»", size=10.5, color=INK, anchor="start"))

    # стрілка вниз: рішення → наслідки
    ay2 = ry + rh
    p.append(arrow(cx, ay2, cx, ay2 + 24, color=INK, sw=2))
    p.append(text(cx + 12, ay2 + 16, "породжує", size=9, color=MUTED, italic=True, anchor="start"))

    # ── НАСЛІДКИ (і плюси, і мінуси) ──
    ny = ay2 + 28
    nh = 74
    p.append(rect(cx - bw / 2, ny, bw, nh, fill="#fdf2f0", stroke=POS, sw=1.8))
    p.append(text(cx - bw / 2 + 14, ny + 19, "НАСЛІДКИ — і виграш, і ціна", size=11.5, bold=True, color=POS, anchor="start"))
    # плюс
    p.append(plus(cx - bw / 2 + 24, ny + 40, r=7))
    p.append(text(cx - bw / 2 + 40, ny + 44, "арифметика точна, копійка не тікає", size=10, color=INK, anchor="start"))
    # мінус
    p.append(minus(cx - bw / 2 + 24, ny + 60, r=7))
    p.append(text(cx - bw / 2 + 40, ny + 64, "код багатослівніший, потрібне ділення на 100 для показу", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *p)


# ── 2. Журнал росте шарами; застаріле не стирають, лише тьмянить статус ─────────
# ADR-журнал — як геологічні шари: нове лягає поверх старого, старе тьмяніє під
# новим статусом, але лишається читабельним. Стрілка «замінює» зшиває шари.
def fig_layers():
    W, H = 760, 400
    p = []
    p.append(text(W / 2, 28, "Журнал росте шарами: застаріле не стирають, лише тьмянить статус", size=14, bold=True))

    # вісь часу вниз (ліворуч)
    axx = 78
    y0, y1 = 70, 340
    p.append(line(axx, y0, axx, y1, color=INK, sw=2))
    p.append(arrow(axx, y1 - 2, axx, y1 + 12, color=INK, sw=2))
    p.append(text(axx - 10, (y0 + y1) / 2, "час", size=10, color=MUTED, anchor="middle"))

    bx = 150                        # ліва межа карток ADR
    bw = 520

    # (y, номер, назва, статус, колір-рамки, приглушено?)
    cards = [
        (92, "ADR-0003", "Обрали PostgreSQL", "ЗАМІНЕНО ADR-0012", MUTED, True),
        (200, "ADR-0012", "Перейшли на іншу базу", "УХВАЛЕНО", FIELD, False),
    ]
    y_repl_from = None
    y_repl_to = None
    for y, num, title_, status, col, faded in cards:
        fill = "#f0f1f2" if faded else "#e7f7ee"
        stroke = MUTED if faded else FIELD
        p.append(rect(bx, y, bw, 78, fill=fill, stroke=stroke, sw=1.8))
        # номер на осі
        p.append(circle(axx, y + 39, 6, fill=stroke, stroke=stroke, sw=2))
        p.append(line(axx + 6, y + 39, bx, y + 39, color=stroke, sw=1.3, dash="3,3"))
        tcol = MUTED if faded else INK
        p.append(text(bx + 16, y + 24, num, size=12, bold=True, color=stroke, anchor="start"))
        p.append(text(bx + 16, y + 46, title_, size=12.5, bold=True, color=tcol, anchor="start"))
        # плашка статусу праворуч усередині картки
        sw_box = 210
        scol = MUTED if faded else FIELD
        p.append(rect(bx + bw - sw_box - 12, y + 46, sw_box, 22,
                      fill=("#f4f6f8" if faded else "#eef6ff"), stroke=scol, sw=1.3))
        p.append(text(bx + bw - sw_box / 2 - 12, y + 61, status, size=10, bold=True, color=scol))
        if faded:
            p.append(text(bx + 16, y + 66, "лишається читабельним — причину не стерто", size=9.5, color=MUTED, italic=True, anchor="start"))
            y_repl_from = y + 39
        else:
            y_repl_to = y + 39

    # стрілка «замінює»: від нового шару назад до старого (праворуч від карток)
    if y_repl_from is not None and y_repl_to is not None:
        rx = bx + bw + 18
        p.append(line(bx + bw, y_repl_to, rx, y_repl_to, color=NEG, sw=1.6))
        p.append(line(rx, y_repl_to, rx, y_repl_from, color=NEG, sw=1.6))
        p.append(arrow(rx, y_repl_from, bx + bw, y_repl_from, color=NEG, sw=1.6))
        p.append(text(rx + 8, (y_repl_from + y_repl_to) / 2, "замінює", size=10, bold=True, color=NEG, anchor="start"))

    p.append(text(W / 2, H - 18,
                  "«Чому свого часу вирішили так» ніколи не застаріває — тому старий шар не видаляють",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "layers.svg"), W, H, *p)


# ── 3. adr new -s: одна команда править ДВА файли одразу ────────────────────────
# Ключова робота, яку adr-tools знімає з рук: створити новий запис і водночас
# перешити статуси. Ліворуч — стан ДО; праворуч — стан ПІСЛЯ команди `adr new -s 7`.
def fig_supersede():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 26, "adr new -s 7 «…»: одна команда править обидва файли", size=14, bold=True))

    # підпис команди по центру-згори
    p.append(rect(W / 2 - 250, 44, 500, 30, fill="#f4f6f8", stroke=INK, sw=1.5))
    p.append(text(W / 2, 64, "$ adr new -s 7 «Гроші — Decimal замість int64»", size=12, bold=True))

    colw = 300
    fileh = 130
    lx = 40                       # ліва колонка (старий ADR-0007)
    rx = W - 40 - colw            # права колонка (новий ADR-0011)

    # ── старий ADR-0007: статус змінюється ──
    oy = 100
    # ДО
    p.append(text(lx + colw / 2, oy - 6, "ADR-0007 — ДО команди", size=11, bold=True, color=MUTED))
    p.append(rect(lx, oy, colw, fileh, fill="#f0f1f2", stroke=MUTED, sw=1.6))
    p.append(text(lx + 14, oy + 22, "# 7. Гроші — int64 у копійках", size=10.5, bold=True, color=INK, anchor="start"))
    p.append(text(lx + 14, oy + 44, "## Status", size=10, bold=True, color=INK, anchor="start"))
    p.append(rect(lx + 14, oy + 52, 130, 20, fill="#eef6ff", stroke=NEG, sw=1.3))
    p.append(text(lx + 14 + 65, oy + 66, "Accepted", size=10, bold=True, color=NEG))
    p.append(text(lx + 14, oy + 96, "## Context …", size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx + 14, oy + 112, "## Decision …", size=9.5, color=MUTED, anchor="start"))

    # ПІСЛЯ (старий файл — новий статус)
    ay = oy + fileh + 46
    p.append(text(lx + colw / 2, ay - 6, "ADR-0007 — ПІСЛЯ (той самий файл)", size=11, bold=True, color=POS))
    p.append(rect(lx, ay, colw, fileh, fill="#fdf2f0", stroke=POS, sw=1.8))
    p.append(text(lx + 14, ay + 22, "# 7. Гроші — int64 у копійках", size=10.5, bold=True, color=INK, anchor="start"))
    p.append(text(lx + 14, ay + 44, "## Status", size=10, bold=True, color=INK, anchor="start"))
    p.append(rect(lx + 14, ay + 52, 250, 20, fill="#fdecea", stroke=POS, sw=1.4))
    p.append(text(lx + 14 + 125, ay + 66, "Superseded by [11. Гроші — Decimal]", size=9, bold=True, color=POS))
    p.append(text(lx + 14, ay + 96, "## Context …  (незмінний)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx + 14, ay + 112, "## Decision … (незмінне)", size=9.5, color=MUTED, anchor="start"))

    # ── новий ADR-0011: створюється з зустрічним лінком ──
    ny = oy + fileh / 2 + 46
    p.append(text(rx + colw / 2, ny - 22, "ADR-0011 — НОВИЙ файл", size=11, bold=True, color=FIELD))
    p.append(rect(rx, ny, colw, fileh + 18, fill="#e7f7ee", stroke=FIELD, sw=1.8))
    p.append(text(rx + 14, ny + 22, "# 11. Гроші — Decimal замість int64", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(rx + 14, ny + 44, "Date: 2026-07-06", size=9.5, color=MUTED, anchor="start"))
    p.append(text(rx + 14, ny + 66, "## Status", size=10, bold=True, color=INK, anchor="start"))
    p.append(rect(rx + 14, ny + 74, 250, 20, fill="#e7f7ee", stroke=FIELD, sw=1.4))
    p.append(text(rx + 14 + 125, ny + 88, "Accepted · Supersedes [7. Гроші — int64]", size=9, bold=True, color=FIELD))
    p.append(text(rx + 14, ny + 118, "## Context …  (пишеш сам)", size=9.5, color=MUTED, anchor="start"))
    p.append(text(rx + 14, ny + 136, "## Decision … (пишеш сам)", size=9.5, color=MUTED, anchor="start"))

    # двобічна стрілка «зшито автоматично» між правками статусів.
    # Обидва стуби виходять із ПРАВОГО краю статус-плашок у гутер (нічого не перетинають),
    # спину ведемо посередині гутера, підпис — у вільному просвіті над спиною.
    mxl = lx + 14 + 250            # правий край статус-плашки старого файлу (ПІСЛЯ)
    mxr = rx                       # лівий край нового файлу
    my_from = ay + 62              # рівень статус-рядка старого (ПІСЛЯ)
    my_to = ny + 84                # рівень статус-рядка нового
    midx = (mxl + mxr) / 2 + 10
    p.append(arrow(midx, my_from, mxl, my_from, color=INK, sw=1.4))   # ← у старий файл
    p.append(line(midx, my_from, midx, my_to, color=INK, sw=1.4, dash="4,3"))
    p.append(arrow(midx, my_to, mxr, my_to, color=INK, sw=1.4))       # → у новий файл
    p.append(text(midx, min(my_from, my_to) - 12, "зшито авто", size=9.5, bold=True, color=INK))

    render(os.path.join(OUT, "supersede.svg"), W, H, *p)


# ── 4. ADR і код їдуть в ОДНОМУ пул-реквесті ────────────────────────────────────
# Сенс тримати ADR у репозиторії: рішення проходить те саме рев'ю, що й код,
# що його втілює. Рецензент бачить причину поруч зі зміною — в одному дифі.
def fig_pr():
    W, H = 760, 300
    p = []
    p.append(text(W / 2, 26, "Один пул-реквест: рішення і код проходять одні очі", size=14, bold=True))

    prx, pry, prw, prh = 60, 56, W - 120, 150
    p.append(rect(prx, pry, prw, prh, fill="#f7f9fb", stroke=INK, sw=1.8))
    p.append(text(prx + 18, pry + 26, "Pull request #482  —  «Гроші: перехід на Decimal»", size=12, bold=True, color=INK, anchor="start"))

    # два «файли» у дифі
    fy = pry + 44
    fw = (prw - 54) / 2
    # ADR-файл
    p.append(rect(prx + 18, fy, fw, 88, fill="#e7f7ee", stroke=FIELD, sw=1.6))
    p.append(text(prx + 18 + 12, fy + 20, "+ doc/adr/0011-…decimal.md", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(prx + 18 + 12, fy + 40, "чому міняємо, які сили,", size=9.5, color=INK, anchor="start"))
    p.append(text(prx + 18 + 12, fy + 55, "що віддаємо натомість", size=9.5, color=INK, anchor="start"))
    p.append(text(prx + 18 + 12, fy + 76, "→ ПРИЧИНА рішення", size=9.5, bold=True, color=FIELD, anchor="start"))
    # код-файл
    cxx = prx + 18 + fw + 18
    p.append(rect(cxx, fy, fw, 88, fill="#eef6ff", stroke=NEG, sw=1.6))
    p.append(text(cxx + 12, fy + 20, "~ src/money.hpp", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(cxx + 12, fy + 40, "struct Money { Decimal v; };", size=9, color=INK, anchor="start"))
    p.append(text(cxx + 12, fy + 55, "// заміна int64 → Decimal", size=9, color=INK, anchor="start"))
    p.append(text(cxx + 12, fy + 76, "→ ВТІЛЕННЯ рішення", size=9.5, bold=True, color=NEG, anchor="start"))

    # знизу — висновок
    p.append(text(W / 2, H - 34, "Рецензент читає причину й зміну разом; історію «хто/коли/чому» дає сам git",
                  size=10.5, color=INK, italic=True))
    p.append(text(W / 2, H - 16, "— безкоштовно, без окремої вікі", size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "pr-review.svg"), W, H, *p)


# ── 5. Родовід форми ADR: від Александера до нащадків ───────────────────────────
# Одна ідея («сили в конфлікті + одна відповідь») перекочувала з рук у руки;
# кожен додав відсутню деталь. Вертикальна вісь часу; вузли-віхи хребта;
# від Найгарда (2011) розходяться три гілки-нащадки внизу.
def fig_lineage():
    W, H = 860, 660
    p = []
    p.append(text(W / 2, 30, "Родовід форми ADR: одна ідея, передана з рук у руки", size=15, bold=True))

    # вісь часу вниз (ліворуч)
    axx = 96
    y0, y1 = 66, 452
    p.append(line(axx, y0, axx, y1, color=INK, sw=2))
    p.append(arrow(axx, y1 - 2, axx, y1 + 14, color=INK, sw=2))
    p.append(text(axx, y1 + 30, "час", size=10, color=MUTED))

    # головна лінія предків: (y, рік, заголовок, підпис, колір)
    spine = [
        (96,  "1977", "Крістофер Александер — «A Pattern Language»", "рамка: сили в конфлікті + один лад-відповідь", FIELD),
        (200, "1994", "Банда чотирьох — «Design Patterns»", "рамку перекладено в код (типові патерни)", NEG),
        (306, "2011", "Майкл Найгард — «Documenting Architecture Decisions»", "приземлено на КОНКРЕТНЕ рішення + статус + файл у репо", INK),
    ]
    bx = 156            # ліва межа карток предків
    bw = 500
    ny_bottom = None    # низ картки Найгарда (від неї — гілки)
    for y, yr, title_, sub, col in spine:
        p.append(rect(bx, y, bw, 68, fill="#f4f6f8", stroke=col, sw=1.9))
        p.append(circle(axx, y + 34, 7, fill=col, stroke=col, sw=2))
        p.append(line(axx + 7, y + 34, bx, y + 34, color=col, sw=1.3, dash="3,3"))
        p.append(text(axx - 14, y + 22, yr, size=12, bold=True, color=col, anchor="end"))
        p.append(text(bx + 16, y + 27, title_, size=11.5, bold=True, color=INK, anchor="start"))
        p.append(text(bx + 16, y + 50, sub, size=10, color=MUTED, anchor="start"))
        if yr == "2011":
            ny_bottom = y + 68

    # стрілки спадкоємності вздовж хребта (у зазорах між картками)
    for (ya, *_1), (yb, *_2) in zip(spine, spine[1:]):
        p.append(arrow(axx + 44, ya + 68, axx + 44, yb, color=MUTED, sw=1.6))

    # ── три гілки-нащадки від Найгарда (2011) ──
    fy = 540
    fh = 96
    # (назва, автор/рік, три рядки-суть, колір)
    kids = [
        ("adr-tools", "Нат Прайс", ["менше тертя:", "нумерація, дати,", "«замінює» — авто"], NEG),
        ("Y-statements", "Олаф Ціммерман · 2012", ["дисципліна:", "рішення в одне", "стисле речення"], FIELD),
        ("MADR", "Копп · Армбрустер · Ціммерман", ["шаблон + Markdown", "+ машиночитність", "(2018)"], POS),
    ]
    fw = 244
    gap = (W - 2 * 40 - 3 * fw) / 2
    xs = [40 + i * (fw + gap) for i in range(3)]

    # вузол розгалуження під карткою Найгарда
    jx = axx + 44
    jy = ny_bottom + 26
    p.append(line(jx, ny_bottom, jx, jy, color=MUTED, sw=1.6))
    p.append(text(bx + 4, jy - 6, "з допису Найгарда розходяться гілки-нащадки:", size=10, color=MUTED, italic=True, anchor="start"))

    for (name, who, note, col), x in zip(kids, xs):
        cxb = x + fw / 2
        p.append(line(jx, jy, cxb, jy, color=col, sw=1.5))
        p.append(arrow(cxb, jy, cxb, fy, color=col, sw=1.5))
        p.append(rect(x, fy, fw, fh, fill="#ffffff", stroke=col, sw=1.9))
        p.append(text(cxb, fy + 24, name, size=13, bold=True, color=col))
        p.append(text(cxb, fy + 42, who, size=9.5, color=MUTED))
        for i, ln in enumerate(note):
            p.append(text(cxb, fy + 60 + i * 12, ln, size=9.5, color=INK))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p)


if __name__ == "__main__":
    fig_anatomy()
    fig_layers()
    fig_supersede()
    fig_pr()
    fig_lineage()
    print("figs done")
