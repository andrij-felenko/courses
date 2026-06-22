# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HUMAN = "#7a4ea8"   # фіолетовий — людський шар
HUMANBG = "#f3edfb"
WARN = "#caa24a"
WARNBG = "#fff6e0"


# ── what-review-catches: де людина бачить те, чого не бачить інструмент ────────
# Ідея: інструменти (компілятор, статичний аналіз, тести, фаззинг) ловлять
# механічні й структурні вади — кожен свій клас. Рецензент стоїть окремим шаром
# і ловить те, що автоматика не формалізує: намір, архітектуру, читабельність,
# крайову логіку. Дві колонки: ліворуч — що ловлять інструменти; праворуч —
# що ловить лише жива людина. Між ними — те саме розриття «форма проти суті».

def fig_what_review_catches():
    W, H = 860, 430
    p = []

    # ліва колонка — інструменти
    lx, lw = 30, 380
    top, ch = 70, 320
    p.append(rect(lx, top, lw, ch, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(lx + lw / 2, top + 28, "Інструменти ловлять", size=14, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, top + 48, "механічне й структурне — автоматично", size=10, color=MUTED, italic=True))
    p.append(line(lx + 18, top + 60, lx + lw - 18, top + 60, color=FIELD, sw=1, dash="4 3"))
    tools = [
        ("компілятор + ворнінги", "тип, синтаксис, звуження"),
        ("статичний аналіз", "use-after-free, NULL, межі"),
        ("хост-тести", "поведінка на відомих входах"),
        ("фаззинг", "крах на хаотичному вході"),
    ]
    for i, (name, what) in enumerate(tools):
        y = top + 84 + i * 56
        p.append(rect(lx + 18, y, lw - 36, 46, fill=BG, stroke=FIELD, sw=1.3, rx=8))
        p.append(text(lx + 30, y + 19, name, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 30, y + 36, what, size=9.5, color=MUTED, anchor="start"))

    # права колонка — людина
    rx, rw = W - 30 - 380, 380
    p.append(rect(rx, top, rw, ch, fill=HUMANBG, stroke=HUMAN, sw=2, rx=12))
    p.append(text(rx + rw / 2, top + 28, "Рецензент ловить", size=14, color=HUMAN, bold=True))
    p.append(text(rx + rw / 2, top + 48, "те, що автоматика не формалізує", size=10, color=MUTED, italic=True))
    p.append(line(rx + 18, top + 60, rx + rw - 18, top + 60, color=HUMAN, sw=1, dash="4 3"))
    human = [
        ("намір", "код робить НЕ те, що мав робити"),
        ("архітектура", "рішення тісно в'яже модулі"),
        ("читабельність", "за пів року ніхто не зрозуміє"),
        ("крайова логіка", "забутий випадок, не баг форми"),
    ]
    for i, (name, what) in enumerate(human):
        y = top + 84 + i * 56
        p.append(rect(rx + 18, y, rw - 36, 46, fill=BG, stroke=HUMAN, sw=1.3, rx=8))
        p.append(text(rx + 30, y + 19, name, size=11.5, color=INK, bold=True, anchor="start"))
        p.append(text(rx + 30, y + 36, what, size=9.5, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "інструмент перевіряє, чи код правильний за формою; людина — чи він правильний за задумом",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "what-review-catches.svg"), W, H, *p,
           title="Рев'ю — людський шар поверх автоматичних сіток")


# ── diff-size-fatigue: розмір diff і втома рецензента ──────────────────────────
# Ідея: здатність ловити дефекти різко спадає з розміром diff і з часом за одним
# присідом. Крива «частка знайдених дефектів» від розміру: плато до ~400 рядків,
# потім обвал. Окремо — позначка «після ~60 хв увага вигоряє».

def fig_diff_size_fatigue():
    W, H = 820, 420
    p = []

    # осі
    ox, oy = 90, 330           # початок координат
    aw, ah = 640, 250          # довжина осей
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))           # X
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))           # Y
    p.append(text(ox + aw / 2, oy + 52, "розмір diff — рядків коду в одному рев'ю", size=11, color=INK))
    p.append(mtext(28, oy - ah / 2, "частка\nзнайдених\nдефектів", size=10, color=INK, lh=1.25))

    # поділки X
    xs = [(0, "0"), (200, "200"), (400, "400"), (800, "800"), (1600, "1600")]
    def px(v): return ox + (v / 1600.0) * aw
    for v, lab in xs:
        x = px(v)
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        p.append(text(x, oy + 20, lab, size=9.5, color=MUTED))
    # поділки Y
    for frac, lab in [(0.0, "0%"), (0.5, "50%"), (0.9, "90%")]:
        y = oy - frac * ah
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.2))
        p.append(text(ox - 12, y + 4, lab, size=9.5, color=MUTED, anchor="end"))
        p.append(line(ox, y, ox + aw, y, color="#e3e3e3", sw=1, dash="3 4"))

    # «солодка зона» 200–400
    p.append(rect(px(200), oy - ah, px(400) - px(200), ah, fill="#eef6ef", stroke="none", sw=0))
    p.append(text((px(200) + px(400)) / 2, oy - ah + 14, "солодка зона", size=10, color=FIELD, bold=True))
    p.append(text((px(200) + px(400)) / 2, oy - ah + 30, "200–400 рядків", size=9, color=FIELD))

    # крива виходу: плато ~0.9 до 400, далі обвал
    pts = [(0, 0.90), (100, 0.90), (200, 0.88), (400, 0.80),
           (700, 0.55), (1000, 0.35), (1300, 0.28), (1600, 0.25)]
    poly = " ".join("%.1f,%.1f" % (px(v), oy - f * ah) for v, f in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, POS))
    # позначка обвалу
    p.append(text(px(1000), oy - 0.35 * ah - 16, "обвал: великий diff гортають по діагоналі",
                  size=9.5, color=POS, italic=True))

    # ── вкладка втоми (окрема міні-шкала справа вгорі) ──
    bx, by, bw2, bh2 = px(820), oy - ah + 6, px(1600) - px(820) - 6, 96
    p.append(rect(bx, by, bw2, bh2, fill=WARNBG, stroke=WARN, sw=1.6, rx=8))
    p.append(text(bx + bw2 / 2, by + 20, "Втома рецензента", size=11, color="#8a6d1a", bold=True))
    p.append(mtext(bx + bw2 / 2, by + 40,
                   "після ~60 хв за одним\nприсідом увага вигоряє —\nнові дефекти перестають\nзнаходитися",
                   size=9, color=INK, lh=1.3))

    p.append(text(W / 2, H - 14,
                  "малий diff читають уважно й до кінця; великий стомлює — і він проходить майже без догляду",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "diff-size-fatigue.svg"), W, H, *p,
           title="Розмір diff і втома: чому короткий PR ловить більше")


# ── pr-flow: pull request як асинхронний цикл ─────────────────────────────────
# Ідея: рев'ю — це не одна дія, а цикл: автор подає зміну, рецензент читає й
# лишає зауваження, автор виправляє, коло повторюється, аж поки апрув → злиття.
# Асинхронність: автор і рецензент не сидять разом, обмін триває в часі.

def fig_pr_flow():
    W, H = 840, 410
    p = []

    # дві доріжки: автор (зліва) і рецензент (справа)
    ax = 150          # центр колонки автора
    rxc = W - 150     # центр колонки рецензента
    p.append(text(ax, 64, "Автор", size=13, color=NEG, bold=True))
    p.append(text(rxc, 64, "Рецензент", size=13, color=HUMAN, bold=True))
    p.append(line(ax, 78, ax, 318, color=NEG, sw=1.2, dash="4 5"))
    p.append(line(rxc, 78, rxc, 318, color=HUMAN, sw=1.2, dash="4 5"))

    bw3, bh3 = 188, 46
    def box(cx, cy, s, col, fill):
        return (rect(cx - bw3 / 2, cy - bh3 / 2, bw3, bh3, fill=fill, stroke=col, sw=1.8, rx=9)
                + mtext(cx, cy - (s.count("\n")) * 6 + 4, s, size=10.5, color=INK, lh=1.25, bold=False))

    # кроки по черзі, зверху вниз
    y1 = 110
    p.append(box(ax, y1, "відкрив pull request\n(diff: що змінив)", NEG, "#e9eefb"))
    p.append(box(rxc, y1 + 56, "читає diff, звіряє\nз наміром і контекстом", HUMAN, HUMANBG))
    p.append(box(rxc, y1 + 124, "лишає зауваження\n(питання, поради)", HUMAN, HUMANBG))
    p.append(box(ax, y1 + 180, "виправляє, відповідає,\nоновлює diff", NEG, "#e9eefb"))

    # стрілки переходів (асинхронні, навскіс між доріжками)
    p.append(arrow(ax + bw3 / 2, y1, rxc - bw3 / 2, y1 + 56, color=MUTED, sw=1.8))
    p.append(arrow(rxc, y1 + 56 + bh3 / 2, rxc, y1 + 124 - bh3 / 2, color=HUMAN, sw=1.8))
    p.append(arrow(rxc - bw3 / 2, y1 + 124, ax + bw3 / 2, y1 + 180, color=MUTED, sw=1.8))

    # петля «коло повторюється»
    p.append(arrow(ax, y1 + 180 - bh3 / 2, ax, y1 + bh3 / 2 + 2, color=NEG, sw=1.6))
    p.append(text(ax - bw3 / 2 - 8, y1 + 90, "коло", size=9.5, color=NEG, anchor="end", italic=True))
    p.append(text(ax - bw3 / 2 - 8, y1 + 104, "повторюється", size=9.5, color=NEG, anchor="end", italic=True))

    # фінал: апрув → злиття (під обома доріжками, по центру)
    fy = y1 + 240
    fbody, fw, fh = textbox(W / 2, fy, "апрув → злиття в основну гілку", size=12,
                            bold=True, fill="#eef6ef", stroke=FIELD, sw=2, pad=14, color=FIELD)
    # стрілка від останнього кроку рецензента вниз-до центру
    p.append(arrow(rxc, y1 + 124 + bh3 / 2, W / 2 + fw / 2 - 12, fy - fh / 2, color=FIELD, sw=1.8))
    p.append(fbody)

    p.append(text(W / 2, H - 16,
                  "обмін асинхронний: автор і рецензент не сидять разом — коментарі живуть у часі, доки код не дозрів",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "pr-flow.svg"), W, H, *p,
           title="Pull request: рев'ю як цикл, а не одна дія")


if __name__ == "__main__":
    fig_what_review_catches()
    fig_diff_size_fatigue()
    fig_pr_flow()
    print("OK: figures written to", OUT)
