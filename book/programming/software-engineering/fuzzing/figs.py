# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#caa24a"   # бурштин — мутація / увага
WARNBG = "#fff6e0"
COV = "#1f8a8a"    # бірюза — покриття


# ── feedback-loop: цикл coverage-guided фаззингу ──────────────────────────────
# Ідея: фаззер не кидає випадкові байти наосліп — він замикає петлю. Мутує вхід,
# запускає під інструментуванням, дивиться на покриття. Новий код → вхід цінний,
# лишаємо в корпусі й мутуємо далі; аварія → відклали в скарбничку. Саме зворотний
# зв'язок за покриттям відрізняє розумний фаззер від «мавпи з клавіатурою».

def fig_feedback_loop():
    W, H = 820, 432
    p = []
    cx, cy = W / 2, 188
    r = 132

    nodes = [
        ("корпус",        "набір цікавих\nвходів", cx - r, cy - 92, COV, "#e6f4f4"),
        ("мутація",       "перевернути біт,\nвставити, зрізати", cx + r, cy - 92, WARN, WARNBG),
        ("запуск під\nінструментуванням", "виконати функцію,\nзібрати покриття", cx + r, cy + 92, NEG, "#e9eefb"),
        ("вердикт",       "новий код? аварія?", cx - r, cy + 92, FIELD, "#eef6ef"),
    ]
    bw, bh = 188, 78
    centers = []
    for name, note, nx, ny, col, fill in nodes:
        p.append(rect(nx - bw / 2, ny - bh / 2, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(mtext(nx, ny - 6, name, size=11.5, color=col, bold=True, lh=1.15))
        p.append(mtext(nx, ny + 22, note, size=9, color=INK, lh=1.2))
        centers.append((nx, ny))

    # стрілки по колу: корпус → мутація → запуск → вердикт → корпус
    p.append(arrow(centers[0][0] + bw / 2, centers[0][1], centers[1][0] - bw / 2, centers[1][1], color=INK, sw=2))
    p.append(arrow(centers[1][0], centers[1][1] + bh / 2, centers[2][0], centers[2][1] - bh / 2, color=INK, sw=2))
    p.append(arrow(centers[2][0] - bw / 2, centers[2][1], centers[3][0] + bw / 2, centers[3][1], color=INK, sw=2))
    p.append(arrow(centers[3][0], centers[3][1] - bh / 2, centers[0][0], centers[0][1] + bh / 2, color=INK, sw=2))

    # підписи на дугах
    p.append(text(cx, cy - 92 - bh / 2 - 8, "узяти вхід і змінити", size=9.5, color=MUTED))
    p.append(text(cx + r + 4, cy, "прогнати", size=9.5, color=MUTED, anchor="start"))
    p.append(text(cx, cy + 92 + bh / 2 + 16, "новий код покрито?", size=9.5, color=MUTED))
    p.append(mtext(cx - r - 4, cy - 4, "так →\nдодати в корпус", size=9.5, color=FIELD, anchor="end", lh=1.2))

    # відгалуження «аварія» в скарбничку
    p.append(arrow(centers[3][0], centers[3][1] + bh / 2, centers[3][0], centers[3][1] + bh / 2 + 36, color=POS, sw=2))
    crash, ccw, cch = textbox(centers[3][0], centers[3][1] + bh / 2 + 56, "аварія → відкласти креш",
                              size=10, bold=True, color=POS, fill="#fbecec", stroke=POS, sw=1.8)
    p.append(crash)

    p.append(text(cx, H - 16, "зворотний зв'язок за покриттям веде мутації до нового коду — не навмання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "feedback-loop.svg"), W, H, *p,
           title="Цикл coverage-guided фаззингу")


# ── harness: що таке fuzz-ціль (LLVMFuzzerTestOneInput) ───────────────────────
# Ідея: фаззер дає сирий буфер (data,size); ціль перетворює його у вхід функції,
# яку перевіряємо, і повертає 0. Аварію ловить НЕ ціль, а санітайзер під сподом.
# Це місток між «потоком випадкових байтів» і «конкретною функцією парсера».

def fig_harness():
    W, H = 820, 340
    p = []

    # ліворуч — фаззер
    fz, fw, fh = textbox(110, 150, "ФАЗЕР\n(libFuzzer)\nдає (data, size)",
                         size=11, bold=True, color=COV, fill="#e6f4f4", stroke=COV, sw=2, min_w=170)
    p.append(fz)

    # центр — fuzz-ціль
    hx, hy, hw, hh = 300, 80, 240, 168
    p.append(rect(hx, hy, hw, hh, fill="#1e1e2e", stroke="#333344", sw=1.5, rx=10))
    p.append(text(hx + hw / 2, hy + 24, "fuzz-ціль", size=12, color="#cdd6f4", bold=True))
    p.append(mtext(hx + 16, hy + 52,
                   "int LLVMFuzzer-\n  TestOneInput(\n  data, size) {\n  parse(data, size);\n  return 0;\n}",
                   size=10, color="#7fb8a0", anchor="start", lh=1.32))

    # праворуч — функція під тестом
    tg, tw, th = textbox(710, 124, "ФУНКЦІЯ\nпід тестом\n(parser/decoder)",
                         size=11, bold=True, color=NEG, fill="#e9eefb", stroke=NEG, sw=2, min_w=160)
    p.append(tg)

    p.append(arrow(196, 150, hx - 4, 150, color=INK, sw=2))
    p.append(arrow(hx + hw + 4, 124, 632, 124, color=INK, sw=2))
    p.append(text((hx + hw + 632) / 2, 112, "виклик", size=9.5, color=MUTED))

    # санітайзер під сподом — оракул аварії
    sx = hx + hw / 2
    p.append(arrow(sx, hy + hh + 4, sx, hy + hh + 40, color=POS, sw=2))
    san, sw_, sh = textbox(sx, hy + hh + 60, "санітайзер (ASan/UBSan) — оракул: будь-яке UB → аварія",
                           size=10, bold=True, color=POS, fill="#fbecec", stroke=POS, sw=1.8)
    p.append(san)

    p.append(text(W / 2, H - 12, "ціль — місток від потоку байтів до конкретної функції; аварію бачить санітайзер",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "harness.svg"), W, H, *p,
           title="Fuzz-ціль: місток між фаззером і функцією")


# ── what-to-fuzz: добрі й погані кандидати ────────────────────────────────────
# Ідея: фаззинг сяє там, де є недовірений вхід → детермінована функція без стану й
# побічних ефектів (парсер, декодер). Кепсько лягає на код зі станом, мережею,
# залізом, де результат залежить не лише від входу.

def fig_what_to_fuzz():
    W, H = 840, 360
    p = []
    colw = 380
    lx, rx = 30, W - 30 - colw
    top, ch = 78, 222

    # ліва — добре фаззити
    p.append(rect(lx, top, colw, ch, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    p.append(text(lx + colw / 2, top + 28, "добре фаззити", size=14, color=FIELD, bold=True))
    p.append(text(lx + colw / 2, top + 49, "вхід → результат, без стану збоку", size=10, color=INK))
    p.append(line(lx + 20, top + 60, lx + colw - 20, top + 60, color=FIELD, sw=1, dash="4 3"))
    good = ["парсер протоколу чи кадру",
            "декодер формату (JPEG, JSON, шрифт)",
            "розбір недовіреного вводу ззовні",
            "чиста функція: той самий вхід → той самий вихід",
            "робота з буфером і межами"]
    for i, t in enumerate(good):
        p.append(text(lx + 22, top + 84 + i * 26, "+  " + t, size=10.5, color=FIELD, anchor="start"))

    # права — кепсько фаззити
    p.append(rect(rx, top, colw, ch, fill="#fbecec", stroke=POS, sw=2, rx=12))
    p.append(text(rx + colw / 2, top + 28, "кепсько фаззити", size=14, color=POS, bold=True))
    p.append(text(rx + colw / 2, top + 49, "результат залежить не лише від входу", size=10, color=INK))
    p.append(line(rx + 20, top + 60, rx + colw - 20, top + 60, color=POS, sw=1, dash="4 3"))
    bad = ["код з прихованим станом між викликами",
           "звернення до мережі чи диска",
           "залежність від реального заліза / годинника",
           "недетермінована логіка (потоки, гонки)",
           "повільні операції — крадуть швидкість"]
    for i, t in enumerate(bad):
        p.append(text(rx + 22, top + 84 + i * 26, "−  " + t, size=10.5, color=POS, anchor="start"))

    p.append(text(W / 2, H - 14, "ідеальна ціль — детермінована функція над недовіреним входом",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "what-to-fuzz.svg"), W, H, *p,
           title="Що добре і що кепсько фаззити")


# ── ladder: де фаззинг серед сіток якості ─────────────────────────────────────
# Ідея: фаззинг не заміняє інші перевірки, а додає унікальне — САМ ШУКАЄ вхід, що
# ламає. Тести перевіряють входи, які придумав ти; фаззер вигадує входи, яких ти
# не уявив. Тому він стоїть поряд із тестами й санітайзерами, не замість них.

def fig_ladder():
    W, H = 820, 360
    p = []
    bx, bw = 150, 540
    rows = [
        ("ворнінги · статичний аналіз", "ловлять підозрілі КОНСТРУКЦІЇ без запуску", FIELD, "#eef6ef"),
        ("хост-тести", "перевіряють входи, які придумав ТИ", "#1f8a8a", "#e6f4f4"),
        ("фаззинг + санітайзери", "САМ шукає входи, яких ти не уявив", POS, "#fbecec"),
    ]
    top, rh, gap = 78, 70, 20
    for i, (name, note, col, fill) in enumerate(rows):
        y = top + i * (rh + gap)
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=2.2, rx=10))
        p.append(text(bx + bw / 2, y + 30, name, size=13.5, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 51, note, size=10, color=INK))

    # підпис унизу
    p.append(text(W / 2, H - 30,
                  "тест відповідає на «чи правильно для входу X»; фаззер питає «а який X усе зламає»",
                  size=11, color=INK))
    p.append(text(W / 2, H - 12,
                  "фаззинг доповнює тести й санітайзери, а не заміняє їх",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "ladder.svg"), W, H, *p,
           title="Місце фаззингу серед сіток якості")


# ════════════════════════════════════════════════════════════════════════════
# Фігури детальної версії (fuzzing-d.md)
# ════════════════════════════════════════════════════════════════════════════


# ── coverage-grow: як росте покриття від цінних входів ────────────────────────
# Ідея: інструментування ставить «лічильник» на кожну гілку. Вхід, що засвітив
# нову гілку, додають у корпус — і мутації від нього сягають ще глибше. Так фаззер
# повзе вглиб дерева гілок крок за кроком, а не штурмує його випадково.

def fig_coverage_grow():
    W, H = 800, 380
    p = []
    # дерево гілок: корінь і три рівні
    levels = [
        [(W / 2, 80)],
        [(W / 2 - 180, 170), (W / 2 + 180, 170)],
        [(W / 2 - 260, 268), (W / 2 - 100, 268), (W / 2 + 100, 268), (W / 2 + 260, 268)],
    ]
    # які вузли «покрито» (засвічено зворотним зв'язком) — росте зліва направо
    reached = {(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)}
    r = 20
    # ребра
    p.append(line(levels[0][0][0], levels[0][0][1] + r, levels[1][0][0], levels[1][0][1] - r, color=MUTED, sw=1.5))
    p.append(line(levels[0][0][0], levels[0][0][1] + r, levels[1][1][0], levels[1][1][1] - r, color=MUTED, sw=1.5))
    for j in range(2):
        for k in range(2):
            child = levels[2][j * 2 + k]
            p.append(line(levels[1][j][0], levels[1][j][1] + r, child[0], child[1] - r, color=MUTED, sw=1.5))
    # вузли
    for li, lvl in enumerate(levels):
        for ni, (nx, ny) in enumerate(lvl):
            on = (li, ni) in reached
            col = COV if on else MUTED
            fill = "#e6f4f4" if on else "#f1f1f1"
            p.append(circle(nx, ny, r, fill=fill, stroke=col, sw=2.2 if on else 1.5))
            p.append(text(nx, ny + 5, "✓" if on else "?", size=15, color=col, bold=True))

    # легенда
    p.append(circle(110, 330, 11, fill="#e6f4f4", stroke=COV, sw=2))
    p.append(text(128, 335, "гілку покрито — вхід додано в корпус", size=10.5, color=INK, anchor="start"))
    p.append(circle(110, 356, 11, fill="#f1f1f1", stroke=MUTED, sw=1.5))
    p.append(text(128, 361, "гілка ще не досягнута — ціль для дальших мутацій", size=10.5, color=MUTED, anchor="start"))

    p.append(text(W / 2, 312, "кожен вхід, що засвітив нову гілку, стає трампліном глибше",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "coverage-grow.svg"), W, H, *p,
           title="Покриття росте вглиб дерева гілок")


# ── mutation-vs-generation: дві школи добування входів ────────────────────────
# Ідея: мутаційний фаззер бере готові приклади й псує їх — нічого не знає про
# формат, але стартує миттєво. Генераційний будує вхід за описом граматики —
# глибоко проходить валідатори, але описувати формат треба руками.

def fig_mutation_vs_generation():
    W, H = 840, 340
    p = []
    colw = 380
    lx, rx = 30, W - 30 - colw
    top, ch = 76, 206

    p.append(rect(lx, top, colw, ch, fill=WARNBG, stroke=WARN, sw=2, rx=12))
    p.append(text(lx + colw / 2, top + 28, "мутаційний", size=14, color="#8a6d1a", bold=True))
    p.append(text(lx + colw / 2, top + 49, "псує готові приклади з корпусу", size=10, color=INK))
    p.append(line(lx + 20, top + 60, lx + colw - 20, top + 60, color=WARN, sw=1, dash="4 3"))
    ml = ["+  стартує миттєво — формат не описуєш",
          "+  знаходить багато за малих зусиль",
          "−  глибокі валідатори часто не пройде",
          "−  не вигадає геть нову структуру"]
    for i, t in enumerate(ml):
        col = POS if t.startswith("−") else FIELD
        p.append(text(lx + 22, top + 86 + i * 28, t, size=10.5, color=col, anchor="start"))

    p.append(rect(rx, top, colw, ch, fill="#e9eefb", stroke=NEG, sw=2, rx=12))
    p.append(text(rx + colw / 2, top + 28, "генераційний", size=14, color=NEG, bold=True))
    p.append(text(rx + colw / 2, top + 49, "будує вхід за описом формату", size=10, color=INK))
    p.append(line(rx + 20, top + 60, rx + colw - 20, top + 60, color=NEG, sw=1, dash="4 3"))
    gl = ["+  глибоко проходить валідатори",
          "+  досягає коду за перевірками формату",
          "−  опис граматики треба писати руками",
          "−  дорожчий старт, вужчий під один формат"]
    for i, t in enumerate(gl):
        col = POS if t.startswith("−") else FIELD
        p.append(text(rx + 22, top + 86 + i * 28, t, size=10.5, color=col, anchor="start"))

    p.append(text(W / 2, H - 14, "структуро-свідомий фаззинг поєднує обидва: мутує, та лишається в межах граматики",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "mutation-vs-generation.svg"), W, H, *p,
           title="Мутаційний проти генераційного фаззингу")


# ── triage: шлях від сирого крешу до полагодженого бага ───────────────────────
# Ідея: знайдений креш — це ще не звіт. Його треба відтворити, мінімізувати вхід
# до найкоротшого, дедуплікувати за місцем аварії й аж тоді чинити. Без тріажу
# тисяча крешів від одного бага тоне сама в собі.

def fig_triage():
    W, H = 860, 250
    p = []
    steps = [
        ("креш-вхід", "фаззер відклав\nбайти, що впали", POS, "#fbecec"),
        ("відтворити", "запустити ще раз —\nпадає стабільно?", WARN, WARNBG),
        ("мінімізувати", "зрізати зайве до\nнайкоротшого входу", COV, "#e6f4f4"),
        ("дедуплікувати", "згрупувати за\nмісцем аварії", NEG, "#e9eefb"),
        ("полагодити", "виправити причину,\nдодати в корпус", FIELD, "#eef6ef"),
    ]
    n = len(steps)
    margin, gap = 24, 16
    bw = (W - 2 * margin - (n - 1) * gap) / n
    by, bh = 80, 104
    cxs = []
    for i, (name, note, col, fill) in enumerate(steps):
        x = margin + i * (bw + gap)
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, by + 28, name, size=12, color=col, bold=True))
        p.append(mtext(x + bw / 2, by + 50, note, size=9, color=INK, lh=1.25))
        cxs.append((x, x + bw))
    for i in range(n - 1):
        p.append(arrow(cxs[i][1] + 2, by + bh / 2, cxs[i + 1][0] - 2, by + bh / 2, color=INK, sw=1.8))

    p.append(text(W / 2, H - 16, "сирий креш ще не звіт: відтвори, зріж до мінімуму, згрупуй — і лише тоді лагодь",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "triage.svg"), W, H, *p,
           title="Тріаж крешу: від сирих байтів до причини")


if __name__ == "__main__":
    fig_feedback_loop()
    fig_harness()
    fig_what_to_fuzz()
    fig_ladder()
    fig_coverage_grow()
    fig_mutation_vs_generation()
    fig_triage()
    print("OK: figures written to", OUT)
