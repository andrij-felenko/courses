# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"
PURPLE  = "#7a5ea8"
PURPBG  = "#f1ecf8"


def commit(cx, cy, r=9, fill=BG, stroke=INK, sw=2):
    return circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)


# ── branch-as-label: гілка — це рухомий ярлик, не копія ───────────────────────
# Ідея: коміти лежать ланцюжком (кожен знає батька). Гілка — лише рухомий
# покажчик на один коміт; зробив коміт «на гілці» — покажчик переповз на новий.
# Тому гілка майже безкоштовна: це не копія файлів, а 40 байтів імені з адресою.

def fig_branch_as_label():
    W, H = 820, 320
    p = []
    p.append(text(W / 2, 40, "гілка — це рухомий ярлик на один коміт, а не копія коду", size=14, color=INK, bold=True))

    y = 150
    xs = [120, 230, 340, 450, 560]
    # ланцюжок комітів зі стрілками «дитина → батько»
    for i in range(len(xs) - 1):
        p.append(arrow(xs[i + 1] - 9, y, xs[i] + 9, y, color=MUTED, sw=1.8))
    for i, x in enumerate(xs):
        p.append(commit(x, y))
    p.append(text(xs[0], y + 28, "перший", size=9, color=MUTED))
    p.append(text(xs[-1], y + 28, "останній", size=9, color=MUTED))
    p.append(text(W / 2, y + 58, "кожен коміт памʼятає свого батька → виходить ланцюжок історії",
                  size=10, color=MUTED, italic=True))

    # ярлик main, що вказує на останній коміт
    lx = xs[-1]
    p.append(rect(lx - 34, y - 70, 68, 26, fill=GREENBG, stroke=FIELD, sw=1.8, rx=6))
    p.append(text(lx, y - 52, "main", size=12, color=FIELD, bold=True))
    p.append(arrow(lx, y - 44, lx, y - 13, color=FIELD, sw=2))

    # новий коміт + переповзання ярлика
    nx = 670
    p.append(arrow(nx - 9, y, lx + 9, y, color=MUTED, sw=1.8))
    p.append(commit(nx, y, fill=GREENBG, stroke=FIELD))
    p.append("<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.6\" stroke-dasharray=\"4 4\" marker-end=\"url(#arrow)\"/>" % (lx, y - 31, nx, y - 13, FIELD))
    p.append(text((lx + nx) / 2 + 6, y - 40, "коміт →", size=9, color=FIELD, italic=True))
    p.append(text(nx + 4, y - 52, "ярлик повзе сюди", size=9.5, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 14, "новий коміт «на гілці» = ярлик перестрибнув на нього; самі файли нікуди не копіюються",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "branch-as-label.svg"), W, H, *p, title="")


# ── three-strategies: три стратегії на одній осі ─────────────────────────────
# Ідея: стратегії — це точки на шкалі «скільки довгоживучих гілок / який ритм
# випуску». Trunk-based: одна гілка, релізи постійні. GitHub Flow: main +
# короткі гілки, деплой щодня. git-flow: багато довгих гілок, нечасті версійні
# релізи. Більше гілок = більше порядку для версій, але й більше тертя.

def fig_three_strategies():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 38, "три стратегії — точки на одній шкалі", size=15, color=INK, bold=True))

    cards = [
        (40, "Trunk-based", "одна спільна гілка",
         ["усі ллють у trunk щодня",
          "гілки живуть години",
          "релізи — постійно"],
         "← найпростіше, найшвидше", FIELD, GREENBG),
        (300, "GitHub Flow", "main + короткі гілки",
         ["гілка на задачу, з PR",
          "злив → одразу деплой",
          "веб і сервіси"],
         "проста середина", NEG, BLUEBG),
        (560, "git-flow", "багато довгих гілок",
         ["develop, release, hotfix",
          "версійні релізи (v1.4.2)",
          "кілька версій у полі"],
         "найбільше порядку →", PURPLE, PURPBG),
    ]
    cw = 220
    for x, name, sub, body, foot, col, fill in cards:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, 70, cw, 210, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(x + cw / 2, 98, name, size=14, color=tagcol, bold=True))
        p.append(text(x + cw / 2, 118, sub, size=10, color=MUTED))
        p.append(line(x + 24, 130, x + cw - 24, 130, color=col, sw=1))
        for j, ln in enumerate(body):
            p.append(text(x + 22, 156 + j * 24, "• " + ln, size=10.5, color=INK, anchor="start"))
        p.append(text(x + cw / 2, 262, foot, size=10, color=tagcol, bold=True))

    # вісь під картками
    ay = 308
    p.append("<line x1=\"40\" y1=\"%d\" x2=\"780\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.6\" marker-end=\"url(#arrow)\"/>" % (ay, ay, MUTED))
    p.append(text(60, ay + 22, "менше гілок · швидший ритм · більше дисципліни тестів", size=9.5, color=MUTED, anchor="start"))
    p.append(text(780, ay + 22, "більше гілок · версії · більше тертя", size=9.5, color=MUTED, anchor="end"))
    render(os.path.join(OUT, "three-strategies.svg"), W, H, *p, title="")


# ── gitflow-map: карта гілок git-flow ────────────────────────────────────────
# Ідея: канонічна мапа git-flow у двох постійних доріжках (main — лише релізи;
# develop — щоденна інтеграція) і трьох тимчасових (feature від develop; release
# відгалужується перед випуском; hotfix — від main, коли горить у полі). Кожна
# тимчасова гілка вливається назад у свої постійні.

def fig_gitflow_map():
    W, H = 840, 380
    p = []
    p.append(text(W / 2, 34, "карта git-flow: дві постійні доріжки + три тимчасові", size=14.5, color=INK, bold=True))

    # доріжки (горизонтальні рівні)
    lanes = [
        ("main", 80, POS, "лише релізи й теги"),
        ("hotfix", 130, AMBER, ""),
        ("release", 185, NEG, ""),
        ("develop", 250, FIELD, "щоденна інтеграція"),
        ("feature", 320, PURPLE, ""),
    ]
    x0, x1 = 150, 800
    for name, y, col, note in lanes:
        tagcol = AMBERTX if col == AMBER else col
        p.append(line(x0, y, x1, y, color="#dddddd", sw=1.2, dash="3 4"))
        p.append(rect(40, y - 14, 96, 28, fill=BG, stroke=col, sw=1.8, rx=6))
        p.append(text(88, y + 5, name, size=11, color=tagcol, bold=True))
        if note:
            p.append(text(x1 + 4, y + 4, note, size=9, color=MUTED, anchor="end"))

    ymain, yhot, yrel, ydev, yfeat = 80, 130, 185, 250, 320

    def c(x, y, col):
        return commit(x, y, r=7, fill=BG, stroke=col, sw=1.8)

    def branchline(x1_, y1_, x2_, y2_, col):
        return "<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.8\" marker-end=\"url(#arrow)\"/>" % (x1_, y1_, x2_, y2_, col)

    # develop тягнеться весь час
    for x in (190, 360, 520, 660, 760):
        p.append(c(x, ydev, FIELD))
    # feature: від develop і назад
    p.append(branchline(220, ydev, 290, yfeat, PURPLE))
    p.append(c(330, yfeat, PURPLE)); p.append(c(290, yfeat, PURPLE))
    p.append(line(290, yfeat, 360, yfeat, color=PURPLE, sw=1.8))
    p.append(branchline(370, yfeat, 430, ydev, PURPLE))
    # release: від develop, стабілізація, у main (+теги) і назад у develop
    p.append(branchline(540, ydev, 590, yrel, NEG))
    p.append(c(590, yrel, NEG)); p.append(c(630, yrel, NEG))
    p.append(line(590, yrel, 630, yrel, color=NEG, sw=1.8))
    p.append(branchline(640, yrel, 690, ymain, NEG))     # у main
    p.append(branchline(640, yrel, 700, ydev, NEG))      # назад у develop
    p.append(c(700, ymain, POS))
    p.append(text(700, ymain - 16, "v1.4", size=9, color=POS, bold=True))
    # перший реліз на старті
    p.append(c(150, ymain, POS)); p.append(text(150, ymain - 16, "v1.3", size=9, color=POS, bold=True))
    p.append(branchline(150, ymain, 188, ydev, FIELD))
    # hotfix: від main (релізу), фікс, назад у main і develop
    p.append(branchline(700, ymain, 740, yhot, AMBER))
    p.append(c(740, yhot, AMBER))
    p.append(branchline(750, yhot, 790, ymain, AMBER))
    p.append(branchline(750, yhot, 770, ydev, AMBER))
    p.append(c(790, ymain, POS)); p.append(text(790, ymain - 16, "v1.4.1", size=9, color=POS, bold=True))

    p.append(text(W / 2, H - 12, "час тече зліва направо; тимчасова гілка завжди вливається назад у свої постійні доріжки",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "gitflow-map.svg"), W, H, *p, title="")


# ── hotfix-flow: терміновий фікс у полі для версійної прошивки ─────────────────
# Ідея: прошивка v1.4.0 уже в тисячах пристроїв; знайшли критичний баг. Не можна
# тягнути в реліз усе недороблене з develop. Тому гілку hotfix роблять ВІД ТЕГА
# релізу, кладуть один точковий фікс, випускають v1.4.1 — і вливають той самий
# фікс назад у develop, щоб він не зник у наступній версії.

def fig_hotfix_flow():
    W, H = 820, 360
    p = []
    p.append(text(W / 2, 36, "терміновий фікс у полі: гілка від тега релізу", size=15, color=INK, bold=True))

    ytag = 110
    # тег релізу
    p.append(rect(60, ytag - 22, 150, 44, fill=POS and REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(135, ytag - 4, "v1.4.0 у полі", size=11.5, color=POS, bold=True))
    p.append(text(135, ytag + 14, "тисячі пристроїв", size=9, color=MUTED))

    # стрілка вниз: гілка hotfix
    p.append(arrow(135, ytag + 24, 135, 188, color=AMBER, sw=2.2))
    p.append(text(150, 165, "гілка hotfix від цього тега", size=9.5, color=AMBERTX, anchor="start"))

    yhot = 210
    p.append(rect(60, yhot - 22, 200, 56, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(160, yhot - 2, "hotfix: один точковий фікс", size=10.8, color=AMBERTX, bold=True))
    p.append(text(160, yhot + 16, "нічого зайвого з develop", size=9.2, color=MUTED))
    p.append(text(160, yhot + 30, "→ випуск v1.4.1", size=9.6, color=AMBERTX, bold=True))

    # дві стрілки злиття назад
    p.append(arrow(260, yhot - 6, 470, ytag, color=AMBER, sw=2))
    p.append(text(365, ytag - 28, "у main (стає v1.4.1)", size=9, color=AMBERTX))

    yrel = 286
    p.append(rect(470, yrel - 22, 250, 56, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(595, yrel - 2, "develop (наступна версія)", size=10.6, color=FIELD, bold=True))
    p.append(text(595, yrel + 16, "сюди ТЕЖ вливають той самий фікс,", size=9, color=INK))
    p.append(text(595, yrel + 30, "щоб у v1.5 баг не воскрес", size=9, color=INK))
    p.append(arrow(260, yhot + 12, 468, yrel - 8, color=AMBER, sw=2))

    # реліз-вузол v1.4.1 праворуч від тега
    p.append(rect(470, ytag - 22, 130, 44, fill=REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(535, ytag + 4, "v1.4.1 у поле", size=11, color=POS, bold=True))

    p.append(text(W / 2, H - 12, "фікс іде в обидві лінії: у випущену версію — щоб полагодити, і в develop — щоб не загубити",
                  size=10.3, color=MUTED, italic=True))
    render(os.path.join(OUT, "hotfix-flow.svg"), W, H, *p, title="")


# ── hist-timeline: хроніка гілкування в git ──────────────────────────────────
# Ідея (для вставки hist): чотири віхи на одній осі часу. 2005 — git народився
# з кризи BitKeeper (Торвальдс, дешеві гілки). 2010 — git-flow (Дрізсен).
# 2011 — GitHub Flow (Чейкон). 2020 — сам Дрізсен застерігає проти git-flow для
# безперервного викочування. Стрілка часу несе всю розповідь одним поглядом.

def fig_hist_timeline():
    W, H = 840, 410
    p = []
    p.append(text(W / 2, 32, "хроніка: від народження git до перегляду git-flow", size=15, color=INK, bold=True))

    ax_y = 205
    x0, x1 = 70, 770
    p.append("<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke=\"%s\" stroke-width=\"2\" marker-end=\"url(#arrow)\"/>" % (x0, ax_y, x1, ax_y, MUTED))
    p.append(text(x1, ax_y - 12, "час", size=10, color=MUTED, anchor="end", italic=True))

    bw, bh = 152, 82
    # роки-позначки на осі (рівномірні підписи, не масштаб)
    events = [
        (120, "квіт. 2005", "git народжується", "криза BitKeeper;\nТорвальдс пише за дні;\nдешеві гілки", FIELD, GREENBG, "up"),
        (340, "січ. 2010", "git-flow", "Вінсент Дрізсен:\n«A successful Git\nbranching model»", PURPLE, PURPBG, "down"),
        (520, "серп. 2011", "GitHub Flow", "Скотт Чейкон:\nменше гілок,\nдеплой щодня", NEG, BLUEBG, "up"),
        (730, "бер. 2020", "перегляд", "сам Дрізсен:\nдля CD git-flow —\nрадше тягар", POS, REDBG, "down"),
    ]
    for x, yr, name, body, col, fill, side in events:
        tagcol = AMBERTX if col == AMBER else col
        # вузол на осі
        p.append(circle(x, ax_y, 7, fill=fill, stroke=col, sw=2.2))
        p.append(text(x, ax_y + 22 if side == "down" else ax_y - 16, yr, size=9.5, color=MUTED, bold=True))
        # картка з боку осі
        bx = x - bw / 2
        by = (ax_y + 34) if side == "down" else (ax_y - 34 - bh)
        # лінія-привʼязка
        ly1 = (ax_y + 7) if side == "down" else (ax_y - 7)
        ly2 = by if side == "down" else (by + bh)
        p.append(line(x, ly1, x, ly2, color=col, sw=1.4, dash="3 3"))
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x, by + 19, name, size=12, color=tagcol, bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x, by + 37 + j * 13, ln, size=9, color=INK))

    p.append(text(W / 2, H - 14, "одна дуга поглядів: спершу «усе передбачити гілками» → потім «менше гілок, більше автотестів»",
                  size=10.2, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p, title="")


# ── hist-pendulum: маятник поглядів на гілки ──────────────────────────────────
# Ідея: за п'ятнадцять років думка індустрії хитнулася. Лівий полюс — «гілки
# передбачають усе» (git-flow, багато довгих гілок, ручна дисципліна). Правий —
# «менше гілок, більше автотестів» (trunk-based / GitHub Flow). Стрілка-дуга
# показує сам рух, а не статичні крапки: куди й чому хитнувся маятник.

def fig_hist_pendulum():
    W, H = 820, 330
    p = []
    p.append(text(W / 2, 34, "маятник поглядів: чим тримати порядок — гілками чи тестами", size=14.5, color=INK, bold=True))

    cx, cy = W / 2, 96
    # дуга маятника (півколо)
    p.append("<path d=\"M %d %d A 300 300 0 0 1 %d %d\" fill=\"none\" stroke=\"%s\" stroke-width=\"1.6\" stroke-dasharray=\"5 5\"/>" % (cx - 300, cy + 60, cx + 300, cy + 60, MUTED))
    # вісь підвісу
    p.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    # стрілка руху вздовж дуги (зліва направо = з часом)
    p.append("<path d=\"M %d %d A 250 250 0 0 1 %d %d\" fill=\"none\" stroke=\"%s\" stroke-width=\"2.4\" marker-end=\"url(#arrow)\"/>" % (cx - 180, cy + 175, cx + 180, cy + 175, FIELD))
    p.append(text(cx, cy + 150, "напрям зсуву з 2010-х →", size=10, color=FIELD, bold=True))

    # лівий полюс
    lx, ly = 150, 215
    p.append(rect(lx - 120, ly - 26, 240, 96, fill=PURPBG, stroke=PURPLE, sw=2, rx=12))
    p.append(text(lx, ly - 6, "«гілки передбачають усе»", size=11.5, color=PURPLE, bold=True))
    p.append(text(lx, ly + 12, "git-flow: багато довгих гілок", size=9.5, color=INK))
    p.append(text(lx, ly + 27, "порядок — ручна дисципліна", size=9.5, color=INK))
    p.append(text(lx, ly + 50, "версійний реліз, латки в полі", size=9, color=MUTED, italic=True))

    # правий полюс
    rx_, ry = 670, 215
    p.append(rect(rx_ - 120, ry - 26, 240, 96, fill=GREENBG, stroke=FIELD, sw=2, rx=12))
    p.append(text(rx_, ry - 6, "«менше гілок, більше тестів»", size=11.2, color=FIELD, bold=True))
    p.append(text(rx_, ry + 12, "trunk-based / GitHub Flow", size=9.5, color=INK))
    p.append(text(rx_, ry + 27, "порядок — автотести на коміт", size=9.5, color=INK))
    p.append(text(rx_, ry + 50, "безперервне викочування", size=9, color=MUTED, italic=True))

    p.append(text(W / 2, H - 12, "обидва полюси живі: вибір диктує не мода, а природа того, що випускаєш",
                  size=10.2, color=MUTED, italic=True))
    render(os.path.join(OUT, "hist-pendulum.svg"), W, H, *p, title="")


if __name__ == "__main__":
    fig_branch_as_label()
    fig_three_strategies()
    fig_gitflow_map()
    fig_hotfix_flow()
    fig_hist_timeline()
    fig_hist_pendulum()
    print("OK: figures written to", OUT)
