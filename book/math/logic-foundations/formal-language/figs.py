# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Формальна мова».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # діагональ, «свої» операції, акцент
BLUE  = "#2457d6"   # структура, службові написи
GREEN = "#27ae60"   # належить мові / підсумок
ACC   = "#eafaf0"   # заливка «належить»
COLD  = "#eef2fb"   # заливка нейтральної картки
PAPER = "#fbfcfe"   # заливка панелі


def defs_arrows(*colors):
    out = ["<defs>"]
    for c in colors:
        mid = "ar_%s" % c.lstrip("#")
        out.append('<marker id="%s" viewBox="0 0 10 10" refX="8.4" refY="5" '
                   'markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">'
                   '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % (mid, c))
    out.append("</defs>")
    return "".join(out)


def arrow_c(x1, y1, x2, y2, color, sw=2.0):
    mid = "ar_%s" % color.lstrip("#")
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def cell(x, y, w, h, s, fill="#ffffff", stroke="#c9ced6", sw=1.2, size=13,
         color=INK, bold=False, rx=4):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx)
    out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


# ── Фігура 1: від алфавіту до мови ───────────────────────────────────────────
# Чотири кроки означення в одній картинці. Головне — останній: мова НЕ мусить
# мати закономірності, вона просто ВИБРАНА підмножина. Наскрізний приклад:
# Σ = {a, b}, L = «слів, де стільки ж a, скільки b» (розсипана по всіх довжинах).
def fig_alphabet_to_language():
    W, H = 1000, 630
    P = [defs_arrows(INK, GREEN, BLUE)]
    P.append(text(W / 2, 32, "Від алфавіту до мови: чотири кроки", size=17, bold=True))
    P.append(text(W / 2, 56, "кожен крок додає рівно одне поняття — і жодного натяку на зміст",
                  size=12, color=MUTED))

    # ── три картки-кроки ─────────────────────────────────────────────────────
    P.append(rect(30, 76, 280, 112, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
    P.append(text(170, 100, "1 · АЛФАВІТ  Σ", size=12.5, color=BLUE, bold=True))
    P.append(rect(88, 112, 164, 38, fill=COLD, stroke=BLUE, sw=1.4, rx=6))
    P.append(text(170, 138, "Σ = { a, b }", size=17, bold=True))
    P.append(text(170, 172, "скінченний набір значків", size=11, color=MUTED))

    P.append(rect(336, 76, 330, 112, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
    P.append(text(501, 100, "2 · СЛОВО", size=12.5, color=BLUE, bold=True))
    for i, ch in enumerate("abba"):
        P.append(cell(431 + i * 36, 112, 32, 34, ch, fill=COLD, stroke=BLUE,
                      sw=1.4, size=15, bold=True))
    P.append(text(501, 172, "скінченний ланцюжок символів:  |abba| = 4", size=11, color=MUTED))

    P.append(rect(692, 76, 278, 112, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
    P.append(text(831, 100, "3 · Σ*  —  УСІ слова", size=12.5, color=BLUE, bold=True))
    P.append(text(831, 132, "нескінченно багато,", size=12.5, color=INK))
    P.append(text(831, 152, "зате їх можна перелічити", size=12.5, color=INK))
    P.append(text(831, 174, "коротші раніше, рівні — за абеткою", size=10.5, color=MUTED))

    # ── головна панель: Σ* по довжинах, мова — зелена підмножина ─────────────
    P.append(rect(30, 204, 940, 324, fill=PAPER, stroke=GREEN, sw=2, rx=12))
    P.append(text(500, 230, "4 · МОВА  L ⊆ Σ*  —  просто ВИБРАНА підмножина", size=14,
                  color=GREEN, bold=True))
    P.append(text(500, 252, "L = «слова, у яких стільки ж a, скільки b».   Зелене — належить L, біле — ні.",
                  size=11.5, color=INK))

    x0, cw, gap, ch = 210, 58, 8, 40
    rows = [[""], ["a", "b"], ["aa", "ab", "ba", "bb"],
            ["aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb"]]
    counts = ["1 слово", "2 слова", "4 слова", "8 слів"]
    for i, (words, cnt) in enumerate(zip(rows, counts)):
        y = 268 + i * 54
        P.append(text(194, y + ch / 2 + 4, "|w| = %d  ·  %s" % (i, cnt), size=11,
                      color=MUTED, anchor="end"))
        for j, w in enumerate(words):
            inside = w.count("a") == w.count("b")
            P.append(cell(x0 + j * (cw + gap), y, cw, ch, w if w else "ε",
                          fill=ACC if inside else "#ffffff",
                          stroke=GREEN if inside else "#c9ced6",
                          sw=2.0 if inside else 1.2,
                          size=14, bold=inside, color=INK))
    P.append(text(210, 500, "…  далі 16 слів довжини 4 (шість із них у L), 32 слова довжини 5 — і так без кінця",
                  size=11.5, color=MUTED, anchor="start"))

    P.append(fitbox(752, 268, 208, 202,
                    "ЖОДНОЇ ЗАКОНОМІРНОСТІ\nозначення не вимагає.\n\n"
                    "Мовою є БУДЬ-ЯКА\nпідмножина Σ* — хоч\nзадана правилом, хоч\nвибрана навмання.\n\n"
                    "Правило — рідкісна\nрозкіш, а не частина\nозначення.",
                    size=11.5, fill="#ffffff", stroke=BLUE, color=INK))

    P.append(fitbox(30, 542, 940, 66,
                    "Ні алфавіт, ні слово, ні Σ*, ні L не знають, що таке «зміст». Мова — це відповідь\n"
                    "на єдине питання «чи це слово в ній?», і ні на яке більше. Уся сила — саме в цій бідності.",
                    size=13, fill=ACC, stroke=GREEN, color=INK, bold=True))
    render("img/alphabet-to-language.svg", W, H, *P)


# ── Фігура 2: мов більше, ніж описів ─────────────────────────────────────────
# Мова = нескінченний рядок ✓/✗ по одному на кожне слово Σ*. Хоч який список
# мов складіть — діагональ, перевернута по всій довжині, дає мову поза списком.
# Звідси головне: описів зліченно, мов — ні.
def fig_diagonal():
    W, H = 1040, 620
    P = [defs_arrows(INK, RED, GREEN)]
    P.append(text(W / 2, 32, "Мов більше, ніж будь-який список може вмістити", size=17, bold=True))
    P.append(text(W / 2, 56, "рядок — одна мова; стовпчик — одне слово Σ* у шортлекс-порядку; клітинка — «чи належить»",
                  size=12, color=MUTED))
    P.append(text(W / 2, 78, "припустімо, що список L₁, L₂, L₃, … охопив УСІ мови над Σ = {a, b}",
                  size=12.5, color=INK, bold=True))

    words = ["ε", "a", "b", "aa", "ab", "ba", "bb"]
    M = [
        [1, 0, 1, 1, 0, 0, 1],
        [0, 1, 1, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0, 1, 1],
        [1, 1, 0, 0, 1, 0, 0],
    ]
    D = [1 - M[i][i] for i in range(7)]          # перевернута діагональ

    lx, lw = 40, 76
    x0, cw, HD, CH = 116, 74, 34, 34
    y0 = 104
    HEAD = "#e9edf3"
    YES, NO = "✓", "✗"

    # шапка
    P.append(cell(lx, y0, lw, HD, "слово →", fill=HEAD, stroke="#c9ced6",
                  size=10.5, color=MUTED, rx=0))
    for j, w in enumerate(words):
        P.append(cell(x0 + j * cw, y0, cw, HD, w, fill=HEAD, stroke="#c9ced6",
                      size=13, bold=True, rx=0))
    P.append(cell(x0 + 7 * cw, y0, 60, HD, "…", fill=HEAD, stroke="#c9ced6",
                  size=13, color=MUTED, rx=0))

    # тіло
    for i in range(7):
        y = y0 + HD + i * CH
        P.append(cell(lx, y, lw, HD, "L%s" % "₁₂₃₄₅₆₇"[i], fill="#f7f8fa",
                      stroke="#c9ced6", size=13, bold=True, rx=0))
        for j in range(7):
            diag = (i == j)
            v = M[i][j]
            P.append(cell(x0 + j * cw, y, cw, CH, YES if v else NO,
                          fill="#fdecea" if diag else "#ffffff",
                          stroke=RED if diag else "#c9ced6",
                          sw=2.2 if diag else 1.0,
                          size=15, bold=True,
                          color=RED if diag else (GREEN if v else "#b6bcc6"), rx=0))
        P.append(cell(x0 + 7 * cw, y, 60, CH, "…", fill="#ffffff", stroke="#c9ced6",
                      size=13, color=MUTED, rx=0))
    ytab = y0 + HD + 7 * CH
    P.append(text(lx + lw / 2, ytab + 22, "⋮", size=15, color=MUTED))
    P.append(text(x0 + 3.5 * cw, ytab + 24, "список нібито триває й охоплює всі мови",
                  size=11.5, color=MUTED))

    # рядок D
    yD = ytab + 46
    P.append(line(lx, yD - 12, x0 + 7 * cw + 60, yD - 12, color=MUTED, sw=1.2, dash="5 4"))
    P.append(cell(lx, yD, lw, 38, "D", fill="#eafaf0", stroke=GREEN, sw=2.2,
                  size=15, bold=True, color=GREEN, rx=0))
    for j in range(7):
        P.append(cell(x0 + j * cw, yD, cw, 38, YES if D[j] else NO,
                      fill=ACC, stroke=GREEN, sw=2.0, size=15, bold=True,
                      color=GREEN if D[j] else "#8aa79a", rx=0))
    P.append(cell(x0 + 7 * cw, yD, 60, 38, "…", fill=ACC, stroke=GREEN, sw=2.0,
                  size=13, color=MUTED, rx=0))
    P.append(text(x0 + 3.5 * cw, yD + 60, "D[wₙ]  =  НЕ ( Lₙ[wₙ] )   —   перевертаємо кожну червону клітинку",
                  size=12.5, color=INK, bold=True))

    # права панель-пояснення
    P.append(rect(720, y0, 288, 268, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
    P.append(text(864, y0 + 26, "ЩО ТУТ ВІДБУВАЄТЬСЯ", size=12, color=BLUE, bold=True))
    P.append(mtext(864, y0 + 56, [
        "Мова — це нескінченний",
        "рядок ✓/✗: по одній",
        "відповіді на КОЖНЕ слово.",
        "",
        "Червона діагональ бере",
        "у мові Lₙ відповідь саме",
        "на n-те слово wₙ.",
        "",
        "D перевертає їх усі, тож",
        "D незгодна з L₁ на w₁,",
        "з L₂ на w₂, з кожною Lₙ",
        "на своєму wₙ.",
    ], size=11.5, color=INK, lh=1.42))

    P.append(fitbox(40, 508, 968, 92,
                    "Отже D — мова, якої в списку немає. Але список ми оголосили повним: суперечність. Мов НЕ зліченно.\n"
                    "А кожен скінченний опис — програма, граматика, регулярний вираз, стаття людською говіркою — сам є словом\n"
                    "над якимось скінченним алфавітом. Тож описів рівно стільки, скільки слів у Σ*, тобто ЗЛІЧЕННО багато.\n"
                    "Висновок неминучий: майже жодна мова не має скінченного опису — описів просто не вистачає на всіх.",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK))
    render("img/diagonal.svg", W, H, *P)


# ── Фігура 3: операції над мовами ────────────────────────────────────────────
# Дві операції дісталися задарма від множин, дві працюють лише тому, що
# елементи — СЛОВА. Наскрізні A = {a, ab}, B = {b, ba}: усе рахується в голові.
def fig_operations():
    W, H = 1000, 580
    P = [defs_arrows(INK, GREEN, RED, BLUE)]
    P.append(text(W / 2, 32, "Операції над мовами: дві зі спадку множин, дві — свої", size=17, bold=True))
    P.append(text(W / 2, 56, "наскрізний приклад над Σ = {a, b}", size=12, color=MUTED))

    P.append(rect(250, 76, 220, 56, fill=COLD, stroke=BLUE, sw=1.8, rx=8))
    P.append(text(360, 110, "A = { a, ab }", size=16, bold=True))
    P.append(rect(530, 76, 220, 56, fill=COLD, stroke=BLUE, sw=1.8, rx=8))
    P.append(text(640, 110, "B = { b, ba }", size=16, bold=True))

    pw, gap, py, ph = 223, 16, 168, 268
    xs = [30 + k * (pw + gap) for k in range(4)]
    heads = [("A ∪ B", "зі спадку множин", BLUE),
             ("A ∩ B", "зі спадку множин", BLUE),
             ("A · B", "СКЛЕЙКА — своя", RED),
             ("A*", "ЗІРКА КЛІНІ — своя", RED)]
    for x, (nm, sub, col) in zip(xs, heads):
        P.append(rect(x, py, pw, ph, fill=PAPER, stroke=col, sw=1.8, rx=10))
        P.append(text(x + pw / 2, py + 32, nm, size=19, color=INK, bold=True))
        P.append(text(x + pw / 2, py + 54, sub, size=11, color=col, bold=True))

    # 1 · об'єднання
    P.append(rect(xs[0] + 16, py + 76, pw - 32, 44, fill=ACC, stroke=GREEN, sw=1.6, rx=6))
    P.append(text(xs[0] + pw / 2, py + 104, "{ a, ab, b, ba }", size=14, bold=True))
    P.append(mtext(xs[0] + pw / 2, py + 150, [
        "Слово в результаті,", "якщо воно є бодай", "в одній із двох мов.",
        "", "Просто зсипали разом —", "нічого нового."], size=11.5, color=INK, lh=1.5))

    # 2 · переріз
    P.append(rect(xs[1] + 16, py + 76, pw - 32, 44, fill="#f0f1f3", stroke=MUTED, sw=1.6, rx=6))
    P.append(text(xs[1] + pw / 2, py + 104, "∅", size=19, bold=True, color=MUTED))
    P.append(mtext(xs[1] + pw / 2, py + 150, [
        "Спільних слів немає.", "", "∅ — теж повноцінна",
        "мова: підмножина, у якій", "нема жодного слова.", "",
        "Не плутати з { ε }."], size=11.5, color=INK, lh=1.5))

    # 3 · склейка — сітка пар
    gx, gcw, gch = xs[2] + 18, 62, 30
    grid = [["·", "b", "ba"], ["a", "ab", "aba"], ["ab", "abb", "abba"]]
    for r, row in enumerate(grid):
        for c, s in enumerate(row):
            head = (r == 0 or c == 0)
            P.append(cell(gx + c * gcw, py + 78 + r * gch, gcw, gch, s,
                          fill="#e9edf3" if head else ACC,
                          stroke="#c9ced6" if head else GREEN,
                          sw=1.0 if head else 1.6,
                          size=12.5, bold=True,
                          color=BLUE if head else INK, rx=0))
    P.append(mtext(xs[2] + pw / 2, py + 190, [
        "A · B = { u·v : u ∈ A, v ∈ B }",
        "", "кожне слово з A, і за ним", "кожне слово з B —",
        "усі чотири пари склеєні."], size=11.5, color=INK, lh=1.5))

    # 4 · зірка
    P.append(mtext(xs[3] + pw / 2, py + 92, [
        "A⁰ = { ε }",
        "A¹ = { a, ab }",
        "A² = { aa, aab, aba, abab }",
        "A³ = … (8 слів)",
    ], size=12, color=INK, lh=1.55, bold=True))
    P.append(rect(xs[3] + 16, py + 168, pw - 32, 34, fill=ACC, stroke=GREEN, sw=1.6, rx=6))
    P.append(text(xs[3] + pw / 2, py + 190, "A* = A⁰ ∪ A¹ ∪ A² ∪ …", size=12.5, bold=True))
    P.append(mtext(xs[3] + pw / 2, py + 224, [
        "Будь-скільки склейок поспіль,", "включно з НУЛЕМ —",
        "саме нуль і дає ε."], size=11.5, color=INK, lh=1.5))

    P.append(fitbox(30, 458, 940, 96,
                    "∪, ∩ і доповнення дісталися задарма: мова — звичайна множина. А склейка й зірка працюють ЛИШЕ тому,\n"
                    "що елементи мови — СЛОВА, які можна дописувати одне до одного; для довільних множин вони позбавлені змісту.\n"
                    "Звідси й позначення Σ*: погляньте на алфавіт як на мову з однолітерних слів — тоді його зірка Кліні\n"
                    "і є множина всіх скінченних слів над Σ. Збігу немає: це буквально та сама операція.",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK))
    render("img/operations.svg", W, H, *P)


# ── Фігура 4 (вставка hist): лінія спадку Туе → Бекус ────────────────────────
# Одна дія — заміна підрядка — крізь три доби. Сині картки — задум (Туе),
# червоні — формалізація (Пост, Марков, Хомський), зелені — застосування
# (Бекус, Кнут). Проміжок 1914→1936 підписано окремим поворотним маркером:
# питання Туе неможливо було поставити, доки не означили «алгоритм».
def fig_lineage_timeline():
    W, H = 1220, 560
    P = [defs_arrows(INK, BLUE, RED, GREEN, MUTED)]
    P.append(text(W / 2, 34, "Один рядок крізь століття: від задачі Туе до нотації Бекуса",
                  size=17, bold=True))
    P.append(text(W / 2, 57, "та сама дія — замінити підрядок іншим — щораз береться до нової роботи",
                  size=12, color=MUTED))

    # легенда трьох діб
    leg = [("задум", BLUE), ("формалізація", RED), ("застосування", GREEN)]
    lx = 360
    for name, col in leg:
        P.append(rect(lx, 74, 16, 16, fill=col, stroke=col, sw=1, rx=3))
        P.append(text(lx + 24, 87, name, size=12, color=INK, anchor="start"))
        lx += 34 + text_width(name, 12) + 40

    AX = 300  # вісь
    P.append(line(48, AX, W - 40, AX, color="#c9ced6", sw=2.5))

    # особові картки: (x, above?, year, name, ident, what, band)
    cards = [
        (120, True,  "1914", "Аксель Туе", "норвежець",
         "ставить задачу про слово", BLUE),
        (470, False, "1943", "Еміль Пост", "амер. (нар. у Польщі)",
         "рядки + правила = ціла машина", RED),
        (640, True,  "1947", "Пост · Марков-мол.", "незалежно",
         "задача Туе нерозв'язна", RED),
        (810, False, "1956–59", "Ноам Хомський", "США",
         "та сама дія → ієрархія класів", RED),
        (980, True,  "1959", "Джон Бекус", "IBM, США",
         "продукції описують ALGOL (BNF)", GREEN),
        (1130, False, "1964", "Дональд Кнут", "США",
         "«Backus–Naur Form»", GREEN),
    ]
    CW, CH = 182, 108
    for x, above, year, name, ident, what, col in cards:
        top = AX - 52 - CH if above else AX + 52
        # з'єднувач до осі + вузол
        yc = top + CH if above else top
        P.append(line(x, yc, x, AX, color=col, sw=1.6))
        P.append(circle(x, AX, 5.5, fill=col, stroke="#ffffff", sw=1.6))
        # картка
        P.append(rect(x - CW / 2, top, CW, CH, fill=PAPER, stroke=col, sw=1.8, rx=10))
        P.append(text(x, top + 26, year, size=15, color=col, bold=True))
        P.append(text(x, top + 47, name, size=12.5, color=INK, bold=True))
        P.append(text(x, top + 64, ident, size=9.5, color=MUTED))
        P.append(fitbox(x - CW / 2 + 8, top + 72, CW - 16, CH - 80, what,
                        size=10.5, pad=4, fill="#ffffff", stroke="#e2e6ec",
                        color=INK, rx=6))

    # поворотний маркер 1936 між Туе і Постом
    px = 300
    P.append(line(px, AX - 46, px, AX + 46, color=MUTED, sw=1.6, dash="5 4"))
    P.append(circle(px, AX, 4.5, fill=MUTED, stroke="#ffffff", sw=1.4))
    P.append(fitbox(px - 92, AX - 118, 184, 66,
                    "1936 · Тюрінг · Черч\nаж тепер означено,\nщо таке «алгоритм»",
                    size=10.5, pad=6, fill=COLD, stroke=MUTED, color=INK, rx=8))
    P.append(line(px, AX - 52, px, AX - 46, color=MUTED, sw=1.6, dash="5 4"))

    P.append(fitbox(48, 494, W - 88, 48,
                    "Питання 1914 року — «чи є загальний спосіб звести один рядок до іншого» — стало можливо "
                    "спростувати аж тоді, коли зʼявилося поняття механічної процедури. Туе випередив власний "
                    "інструмент на 22 роки.",
                    size=12, fill=ACC, stroke=GREEN, color=INK))
    render("img/lineage-timeline.svg", W, H, *P)


# ── Фігура 5 (вставка hist): та сама дія в чотирьох убраннях ──────────────────
# Переписування рядка, продукція, правило граматики й правило BNF — одна дія:
# ліворуч взірець, праворуч заміна. Праворуч — вивід aabb, який показує, навіщо
# драбина класів (скінченному автомату лічити дужки не під силу).
def fig_same_operation():
    W, H = 1060, 520
    P = [defs_arrows(INK, BLUE, RED, GREEN)]
    P.append(text(W / 2, 34, "Та сама дія в чотирьох убраннях", size=17, bold=True))
    P.append(text(W / 2, 57, "ліворуч — взірець, праворуч — на що його замінити; більше нічого",
                  size=12, color=MUTED))

    rows = [
        ("Туе", "1914", "… a b …   →   … b a …", "переписати підрядок у рядку", BLUE),
        ("Пост", "1943", "g $   →   $ h", "продукція — породжує рядок", RED),
        ("Хомський", "1956", "S   →   a S b", "правило граматики", RED),
        ("Бекус", "1959", "⟨вираз⟩ ::= ⟨вираз⟩ + ⟨доданок⟩", "правило BNF", GREEN),
    ]
    LX, LW = 40, 560
    RH, y0, gap = 84, 88, 16
    for i, (who, yr, rule, gloss, col) in enumerate(rows):
        y = y0 + i * (RH + gap)
        P.append(rect(LX, y, LW, RH, fill=PAPER, stroke=col, sw=1.8, rx=10))
        # тег «хто · рік»
        P.append(rect(LX + 14, y + 16, 120, RH - 32, fill=COLD, stroke=col, sw=1.4, rx=7))
        P.append(text(LX + 74, y + RH / 2 - 4, who, size=13, color=INK, bold=True))
        P.append(text(LX + 74, y + RH / 2 + 16, yr, size=11, color=col, bold=True))
        # правило (шрифт підганяється, щоб не вилізло)
        cx = LX + 155 + (LW - 170) / 2
        fs = fit_font(rule, LW - 185, 17, bold=True)
        P.append(text(cx, y + RH / 2 - 2, rule, size=fs, color=INK, bold=True))
        P.append(text(cx, y + RH / 2 + 22, gloss, size=10.5, color=MUTED))

    # права панель: вивід aabb
    RX, RW = 636, 384
    P.append(rect(RX, y0, RW, 4 * (RH + gap) - gap, fill=PAPER, stroke=BLUE, sw=1.8, rx=12))
    P.append(text(RX + RW / 2, y0 + 30, "Одна дія в дії", size=14, color=BLUE, bold=True))
    P.append(rect(RX + 24, y0 + 46, RW - 48, 40, fill=COLD, stroke="#c9ced6", sw=1.2, rx=6))
    P.append(mtext(RX + RW / 2, y0 + 64, ["граматика:   S → a S b     S → ε"],
                   size=12.5, color=INK, bold=True, lh=1.3))
    P.append(mtext(RX + RW / 2, y0 + 116, [
        "S",
        "⇒  a S b",
        "⇒  a a S b b",
        "⇒  a a b b",
    ], size=15, color=INK, bold=True, lh=1.5))
    P.append(fitbox(RX + 24, y0 + 210, RW - 48, 88,
                    "Виросло aabb — стільки ж a, скільки b, у такому\n"
                    "порядку. Саме такі мови й вимагають драбини\n"
                    "класів: скінченному автомату вони не під силу,\n"
                    "бо лічити відкриті дужки він не вміє.",
                    size=10, pad=8, fill=ACC, stroke=GREEN, color=INK, rx=8))

    P.append(fitbox(40, 482, W - 80, 34,
                    "Задача про слово, система-продукція, правило граматики й правило BNF — це те саме "
                    "переписування в різних убраннях. Хто відкривав опис синтаксису мови програмування — "
                    "читав правнука задачі Туе.",
                    size=12, fill=ACC, stroke=GREEN, color=INK))
    render("img/same-operation.svg", W, H, *P)


# ═══ Фігури до вставки «Незліченно мов, зліченно описів» ═════════════════════

# ── Зоопарк зліченних множин: countable = listable ───────────────────────────
# Чотири різні на вигляд нескінченні множини, кожна нанизана на нитку 1,2,3,…,
# усі розміру ℵ₀. Готує ґрунт до стрибка на 2^ℵ₀.
def fig_countability_zoo():
    W, H = 1060, 440
    P = [defs_arrows(INK, BLUE, GREEN)]
    P.append(text(W / 2, 32, "Перелічити нескінченне: різні множини — та сама нитка", size=17, bold=True))
    P.append(text(W / 2, 56, "нанизати всі елементи на один список 1, 2, 3, … так, щоб жоден не загубився",
                  size=12, color=MUTED))

    cards = [
        ("ℕ  — натуральні",  ["0", "1", "2", "3", "4", "5"],           "по порядку"),
        ("ℤ  — цілі",        ["0", "+1", "−1", "+2", "−2", "+3"],       "туди-сюди від нуля"),
        ("ℚ⁺ — раціональні", ["1/1", "2/1", "1/2", "3/1", "1/3", "4/1"], "змійкою по дробах"),
        ("Σ* — усі слова",   ["ε", "a", "b", "aa", "ab", "ba"],         "коротші раніше (шортлекс)"),
    ]
    cwc, gap = 238, 16
    for k, (name, elems, rule) in enumerate(cards):
        x = 30 + k * (cwc + gap)
        P.append(rect(x, 90, cwc, 210, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
        P.append(text(x + cwc / 2, 118, name, size=13, color=BLUE, bold=True))
        P.append(text(x + cwc / 2, 140, "порядок переліку →", size=10, color=MUTED))
        n = len(elems); cw = 33; g = 2; tot = n * cw + (n - 1) * g; ex0 = x + (cwc - tot) / 2
        for i, e in enumerate(elems):
            cx = ex0 + i * (cw + g)
            P.append(text(cx + cw / 2, 158, str(i + 1), size=9, color=MUTED))
            P.append(cell(cx, 164, cw, 32, e, fill=COLD, stroke="#c9ced6", size=12.5, bold=True))
        P.append(text(x + cwc / 2, 224, rule, size=10.5, color=MUTED))
        P.append(rect(x + cwc / 2 - 44, 240, 88, 30, fill=ACC, stroke=GREEN, sw=1.8, rx=8))
        P.append(text(x + cwc / 2, 260, "розмір ℵ₀", size=12.5, color=INK, bold=True))

    P.append(fitbox(30, 316, 1000, 96,
                    "У кожної множини — своя нитка, що не губить жодного елемента, тож усі вони одного розміру: ℵ₀ —\n"
                    "потужність будь-якої множини, яку можна вишикувати в список. Здається, що більшого й не буває.\n"
                    "Наступний крок — булеан 𝒫(Σ*), множина всіх мов, — показує, що буває: 2^ℵ₀ строго більше за ℵ₀.",
                    size=12.5, fill=COLD, stroke=BLUE, color=INK))
    render("img/countability-zoo.svg", W, H, *P)


# ── Діагональ з'їдає будь-який список ─────────────────────────────────────────
# Ліворуч — сам аргумент (D перевертає діагональ, різниться з Lₙ на wₙ).
# Праворуч — «залатали D» → нова діагональ дає новий втікач D′.
def fig_diagonal_escape():
    W, H = 820, 520
    P = [defs_arrows(INK, RED, GREEN, BLUE)]
    P.append(text(W / 2, 32, "Діагональ з'їдає будь-який список мов", size=17, bold=True))
    P.append(text(W / 2, 56, "клітинка — «чи належить слово wⱼ мові Lᵢ»; діагональ перевертаємо в мову D",
                  size=12, color=MUTED))

    words = ["ε", "a", "b", "aa", "ab"]
    YES, NO = "✓", "✗"
    lw, cw, HD, CH = 50, 44, 30, 30

    def draw_table(ox, rows, rowlabels, title, sub, dlabel, dcolor):
        cxm = ox + (lw + 5 * cw) / 2
        P.append(text(cxm, 92, title, size=13, color=BLUE, bold=True))
        P.append(text(cxm, 110, sub, size=10.5, color=MUTED))
        y0 = 122
        P.append(cell(ox, y0, lw, HD, "", fill="#e9edf3", stroke="#c9ced6", rx=0))
        for j, w in enumerate(words):
            P.append(cell(ox + lw + j * cw, y0, cw, HD, w, fill="#e9edf3", stroke="#c9ced6",
                          size=13, bold=True, rx=0))
        for i, row in enumerate(rows):
            y = y0 + HD + i * CH
            P.append(cell(ox, y, lw, HD, rowlabels[i], fill="#f7f8fa", stroke="#c9ced6",
                          size=12.5, bold=True,
                          color=GREEN if rowlabels[i].startswith("D") else INK, rx=0))
            for j, v in enumerate(row):
                diag = (i == j)
                P.append(cell(ox + lw + j * cw, y, cw, CH, YES if v else NO,
                              fill="#fdecea" if diag else "#ffffff",
                              stroke=RED if diag else "#c9ced6", sw=2.2 if diag else 1.0,
                              size=14, bold=True,
                              color=RED if diag else (GREEN if v else "#b6bcc6"), rx=0))
        D = [1 - rows[i][i] for i in range(5)]
        yD = y0 + HD + 5 * CH + 14
        P.append(line(ox, yD - 7, ox + lw + 5 * cw, yD - 7, color=MUTED, sw=1.1, dash="5 4"))
        P.append(cell(ox, yD, lw, 34, dlabel, fill="#eafaf0", stroke=dcolor, sw=2.2,
                      size=14, bold=True, color=dcolor, rx=0))
        for j, v in enumerate(D):
            P.append(cell(ox + lw + j * cw, yD, cw, 34, YES if v else NO, fill=ACC, stroke=dcolor,
                          sw=2.0, size=14, bold=True, color=dcolor if v else "#8aa79a", rx=0))
        return yD, cxm

    M = [[1, 0, 1, 1, 0], [0, 1, 1, 0, 1], [1, 1, 0, 0, 0], [0, 1, 0, 1, 1], [1, 0, 0, 0, 1]]
    yD1, cx1 = draw_table(40, M, ["L₁", "L₂", "L₃", "L₄", "L₅"],
                          "будь-який список", "припустімо, тут УСІ мови", "D", GREEN)
    P.append(text(cx1, yD1 + 58, "D різниться з кожним Lₙ саме на wₙ", size=11.5, color=INK, bold=True))

    P.append(arrow_c(320, 240, 462, 240, BLUE, sw=2.4))
    P.append(text(391, 226, "+ D", size=13, color=BLUE, bold=True))

    Dr = [1 - M[i][i] for i in range(5)]
    N = [Dr, M[0], M[1], M[2], M[3]]
    yD2, cx2 = draw_table(510, N, ["D", "L₁", "L₂", "L₃", "L₄"],
                          "залатали — додали D", "новий список: D, L₁, L₂, …", "D′", RED)
    P.append(text(cx2, yD2 + 58, "нова діагональ → новий втікач D′", size=11.5, color=INK, bold=True))

    P.append(fitbox(40, 404, 740, 96,
                    "Хоч який список подати — перевернута діагональ дає мову поза ним. Залатали одним D —\n"
                    "нова діагональ народжує новий D′. Наздогнати неможливо: поза будь-яким зліченним списком\n"
                    "лишається 2^ℵ₀ мов. Доведення не питає, ЯК вибрані Lₙ, — це про потужність, не про обчислення.",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK))
    render("img/diagonal-escape.svg", W, H, *P)


# ── Два підрахунки: ℵ₀ описів проти 2^ℵ₀ мов ─────────────────────────────────
def fig_two_counts():
    W, H = 1060, 500
    P = [defs_arrows(INK, GREEN, BLUE, RED)]
    P.append(text(W / 2, 32, "Описів зліченно, мов незліченно: майже кожна мова без імені", size=17, bold=True))
    P.append(text(W / 2, 56, "кожен опис — слово над скінченним алфавітом; мов — стільки, скільки підмножин Σ*",
                  size=12, color=MUTED))

    lx, lw2, ly, lh = 30, 296, 84, 300
    P.append(rect(lx, ly, lw2, lh, fill=PAPER, stroke=BLUE, sw=1.8, rx=10))
    P.append(text(lx + lw2 / 2, ly + 26, "СКІНЧЕННІ ОПИСИ", size=12.5, color=BLUE, bold=True))
    items = [
        ("1", "програма",  "int f(){…}"),
        ("2", "граматика", "S → a S b | ε"),
        ("3", "регекс",    "a* b*"),
        ("4", "речення",   "«парної довжини»"),
        ("5", "формула",   "{ aⁿbⁿ : n ≥ 0 }"),
    ]
    for i, (num, kind, code) in enumerate(items):
        y = ly + 52 + i * 40
        P.append(circle(lx + 30, y + 14, 12, fill=COLD, stroke=BLUE, sw=1.5))
        P.append(text(lx + 30, y + 18, num, size=12, color=BLUE, bold=True))
        P.append(text(lx + 52, y + 11, kind, size=11, color=MUTED, anchor="start"))
        P.append(text(lx + 52, y + 27, code, size=12.5, color=INK, anchor="start", bold=True))
    P.append(text(lx + lw2 / 2, ly + lh - 16, "…  усе це — слова: зліченно = ℵ₀", size=11.5, color=INK, bold=True))

    cxc, cyc = 470, 220
    for i in range(5):
        P.append(arrow_c(lx + lw2 + 4, ly + 66 + i * 40, cxc - 46, cyc, GREEN, sw=1.5))
    P.append(circle(cxc, cyc, 40, fill=ACC, stroke=GREEN, sw=2))
    for dx, dy in [(-14, -10), (10, -14), (16, 8), (-8, 14), (0, 0), (-20, 4), (20, -2)]:
        P.append(circle(cxc + dx, cyc + dy, 4.5, fill=GREEN, stroke=GREEN, sw=1))
    P.append(text(cxc, cyc + 62, "мови, що мають", size=11, color=INK))
    P.append(text(cxc, cyc + 78, "імʼя  (ℵ₀)", size=11, color=INK, bold=True))

    fx, fy, fw, fh = 560, 84, 470, 300
    P.append(rect(fx, fy, fw, fh, fill="#fbfbfc", stroke=RED, sw=2, rx=12))
    P.append(text(fx + fw / 2, fy + 26, "УСІ МОВИ  =  𝒫(Σ*)  =  2^ℵ₀", size=14, color=RED, bold=True))
    for r in range(8):
        for c in range(16):
            px = fx + 30 + c * 26 + (13 if r % 2 else 0)
            py = fy + 58 + r * 26
            if px < fx + fw - 16 and py < fy + fh - 40:
                P.append(circle(px, py, 2.6, fill="#c9ced6", stroke="#c9ced6", sw=0.6))
    P.append(circle(fx + 74, fy + fh - 74, 9, fill=GREEN, stroke=GREEN, sw=1))
    P.append(text(fx + 74, fy + fh - 50, "названі: цятка", size=10, color=INK, bold=True))
    P.append(text(fx + fw - 150, fy + fh - 30, "решта — без імені,", size=11, color=MUTED, anchor="start"))
    P.append(text(fx + fw - 150, fy + fh - 15, "нерозпізнавана", size=11, color=MUTED, anchor="start"))

    P.append(fitbox(30, 400, 1000, 82,
                    "Багато описів припадає на ту саму мову, тож названих мов щонайбільше стільки ж, скільки описів: ℵ₀.\n"
                    "А всіх мов 2^ℵ₀. Різниця 2^ℵ₀ − ℵ₀ = 2^ℵ₀: безіменних не просто більшість — це майже всі мови,\n"
                    "і жодну з них не можна пред'явити нарізно — бо вказати на неї означало б її описати.",
                    size=12.5, fill=COLD, stroke=BLUE, color=INK))
    render("img/two-counts.svg", W, H, *P)


# ═══ Фігури до вставки «Мова, яку можна виконати» (proj-language-algebra) ═════

# ── Дві ручки на одній мові: предикат проти генератора ───────────────────────
# Одна мова L = a*, два подання. Предикат бере ОДНЕ слово й дає повну відповідь
# (і «так», і «ні») — розв'язувач. Генератор видає ВСІ слова по черзі, але
# прямого «ні» не каже — лише перелічує. Уся різниця в складності — звідси.
def fig_two_representations():
    W, H = 1000, 432
    P = [defs_arrows(INK, GREEN, RED, BLUE)]
    P.append(text(W / 2, 32, "Дві ручки на одній мові", size=17, bold=True))
    P.append(text(W / 2, 56, "L = a* = { ε, a, aa, aaa, … } — одна мова, два способи її тримати",
                  size=12, color=MUTED))

    # ── ліва картка: предикат ────────────────────────────────────────────────
    P.append(rect(40, 82, 430, 256, fill=PAPER, stroke=BLUE, sw=1.8, rx=12))
    P.append(text(255, 108, "ПРЕДИКАТ", size=14, color=BLUE, bold=True))
    P.append(text(255, 128, "питаємо про ОДНЕ слово", size=11.5, color=MUTED))
    P.append(rect(70, 144, 370, 40, fill=COLD, stroke=BLUE, sw=1.4, rx=8))
    P.append(text(255, 169, "w  →  ( w ∈ L ? )  →  ✓ або ✗", size=14, bold=True))
    P.append(text(96, 216, "«aa»", size=13, bold=True, anchor="start"))
    P.append(arrow_c(152, 212, 198, 212, GREEN))
    P.append(text(212, 216, "✓  належить", size=13, color=GREEN, bold=True, anchor="start"))
    P.append(text(96, 242, "«ab»", size=13, bold=True, anchor="start"))
    P.append(arrow_c(152, 238, 198, 238, RED))
    P.append(text(212, 242, "✗  не належить", size=13, color=RED, bold=True, anchor="start"))
    P.append(fitbox(70, 264, 370, 60,
                    "Відповідає І «так», І «ні».\nЯкщо завжди спиняється — це РОЗВ'ЯЗУВАЧ.",
                    size=12, fill=ACC, stroke=GREEN, color=INK, bold=True))

    # ── права картка: генератор ──────────────────────────────────────────────
    P.append(rect(530, 82, 430, 256, fill=PAPER, stroke=GREEN, sw=1.8, rx=12))
    P.append(text(745, 108, "ГЕНЕРАТОР", size=14, color=GREEN, bold=True))
    P.append(text(745, 128, "просимо НАСТУПНЕ слово", size=11.5, color=MUTED))
    conv = ["ε", "a", "aa", "aaa", "aaaa"]
    cx0, ccw, cgap = 548, 66, 6
    for i, s in enumerate(conv):
        P.append(cell(cx0 + i * (ccw + cgap), 150, ccw, 34, s, fill=COLD,
                      stroke=GREEN, sw=1.4, size=13, bold=True))
    P.append(text(cx0 + 5 * (ccw + cgap) + 8, 172, "…", size=15, color=MUTED, anchor="start"))
    P.append(arrow_c(548, 202, 918, 202, GREEN, sw=2.0))
    P.append(text(745, 224, "по одному, у шортлекс-порядку — далі без кінця", size=11.5, color=INK))
    P.append(fitbox(560, 244, 372, 80,
                    "Видає всі слова по черзі.\nПрямого «ні» про конкретне слово не каже —\nлише «ось наступне».",
                    size=12, fill=ACC, stroke=GREEN, color=INK, bold=True))

    P.append(fitbox(40, 356, 920, 60,
                    "Предикат обводить множину контуром; генератор виписує її вміст по одному. Та сама мова L —\n"
                    "а питання, на які кожна ручка відповідає ЛЕГКО, різні: одна вирішує належність, друга лише перелічує.",
                    size=12.5, fill=COLD, stroke=BLUE, color=INK))
    render("img/two-representations.svg", W, H, *P)


# ── Чому належність легша за перелік: стоп-правило ───────────────────────────
# Шортлекс дає стоп-правило (перейшли до довших слів → «ні»), тож належність
# РОЗВ'ЯЗНА. Довільний порядок стоп-правила не має → лише НАПІВрозв'язна;
# а для деяких мов упорядкувати за довжиною не можна навіть у принципі.
def fig_membership_vs_listing():
    W, H = 1040, 548
    P = [defs_arrows(INK, GREEN, RED, BLUE)]
    P.append(text(W / 2, 32, "Чому належність легша за перелік", size=17, bold=True))
    P.append(text(W / 2, 56, "шукаємо, чи належить мові слово  w = ba  (довжина 2)",
                  size=12, color=MUTED))

    cw, ch, cy = 44, 34, 114

    # ── верхня стрічка: шортлекс ─────────────────────────────────────────────
    P.append(text(60, 92, "ШОРТЛЕКС  —  довжина не спадає", size=13, color=BLUE,
                  bold=True, anchor="start"))
    P.append(text(82, 106, "0", size=10, color=MUTED))
    P.append(cell(60, cy, cw, ch, "ε", fill=COLD, stroke="#c9ced6", size=13, bold=True))
    P.append(text(170, 106, "1", size=10, color=MUTED))
    P.append(cell(124, cy, cw, ch, "a", fill=COLD, stroke="#c9ced6", size=13, bold=True))
    P.append(cell(172, cy, cw, ch, "b", fill=COLD, stroke="#c9ced6", size=13, bold=True))
    P.append(text(342, 106, "2", size=10, color=MUTED))
    for i, s in enumerate(["aa", "ab", "ba", "bb"]):
        found = (s == "ba")
        P.append(cell(248 + i * (cw + 4), cy, cw, ch, s,
                      fill=ACC if found else COLD,
                      stroke=GREEN if found else "#c9ced6",
                      sw=2.4 if found else 1.2, size=13, bold=True,
                      color=GREEN if found else INK))
    P.append(text(344 + cw / 2, cy + ch + 20, "✓ трапилось", size=11, color=GREEN, bold=True))
    xstop = 248 + 4 * (cw + 4) + 8
    P.append(line(xstop, cy - 8, xstop, cy + ch + 8, color=RED, sw=2.4, dash="6 4"))
    P.append(text(xstop + 66, 106, "3", size=10, color=MUTED))
    for i, s in enumerate(["aaa", "aab", "aba"]):
        P.append(cell(xstop + 18 + i * (cw + 4), cy, cw, ch, s, fill="#f4f5f7",
                      stroke="#dde1e7", size=11.5, color="#aab0ba", bold=True))
    P.append(text(xstop + 18 + 3 * (cw + 4) + 4, cy + ch / 2 + 4, "…", size=14,
                  color=MUTED, anchor="start"))
    P.append(fitbox(xstop + 214, cy - 6, 296, 52,
                    "перейшли до слів довжини 3 →\nякщо w не трапилось раніше,\nвпевнено кажемо «ні»",
                    size=10.5, fill="#fdecea", stroke=RED, color=INK))
    P.append(fitbox(704, cy + ch + 12, 296, 30, "належність РОЗВ'ЯЗНА",
                    size=12.5, fill=ACC, stroke=GREEN, color=INK, bold=True))

    # ── нижня стрічка: довільний порядок ─────────────────────────────────────
    cy2 = 252
    P.append(text(60, cy2 - 22, "ДОВІЛЬНИЙ ПОРЯДОК  —  мова просто перелічна", size=13,
                  color=RED, bold=True, anchor="start"))
    jum = ["aab", "bbbb", "a", "abab", "b", "aa", "baa"]
    jw = 54
    for i, s in enumerate(jum):
        P.append(cell(60 + i * (jw + 4), cy2, jw, ch, s, fill=COLD, stroke="#c9ced6",
                      size=12.5, bold=True))
    xq = 60 + len(jum) * (jw + 4)
    P.append(text(xq + 6, cy2 + ch / 2 + 4, "…", size=15, color=MUTED, anchor="start"))
    P.append(cell(xq + 34, cy2, jw + 8, ch, "ba ?", fill="#fdecea", stroke=RED, sw=1.6,
                  size=12.5, bold=True, color=RED, rx=6))
    P.append(text(xq + 34 + (jw + 8) / 2, cy2 + ch + 20, "десь попереду — але де?",
                  size=10.5, color=RED, anchor="middle"))
    P.append(fitbox(704, cy2 + ch + 8, 296, 34,
                    "належність лише НАПІВрозв'язна", size=12.5, fill="#fdecea",
                    stroke=RED, color=INK, bold=True))

    # ── підсумкова панель: критерій Поста + зупинка ──────────────────────────
    P.append(fitbox(40, 372, 960, 148,
                    "Стоп-правило вгорі працює ЛИШЕ завдяки порядку за довжиною. Унизу слово w може випірнути\n"
                    "будь-де попереду, тож поки не випірнуло — «ні» сказати не можна, і чекати можна вічно.\n"
                    "\n"
                    "Розв'язно ⟺ перелічити можна І саму мову, І її доповнення (критерій Поста, 1944). Але є мови —\n"
                    "як-от мова програм, що спиняються, — де доповнення не перелічити навіть у принципі: систематично\n"
                    "виписати всі програми, що НЕ спиняються, неможливо. Стоп-правила там немає — і взятися йому нізвідки.",
                    size=12.5, fill=COLD, stroke=BLUE, color=INK))
    render("img/membership-vs-listing.svg", W, H, *P)


if __name__ == "__main__":
    fig_alphabet_to_language()
    fig_diagonal()
    fig_operations()
    fig_lineage_timeline()
    fig_same_operation()
    fig_countability_zoo()
    fig_diagonal_escape()
    fig_two_counts()
    fig_two_representations()
    fig_membership_vs_listing()
    print("OK: alphabet-to-language.svg, diagonal.svg, operations.svg, "
          "lineage-timeline.svg, same-operation.svg, "
          "countability-zoo.svg, diagonal-escape.svg, two-counts.svg, "
          "two-representations.svg, membership-vs-listing.svg")
