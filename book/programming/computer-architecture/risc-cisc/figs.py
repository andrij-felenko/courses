# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні відтінки під єдиний вигляд розділу «Архітектура».
BLUE   = "#1f47b5"   # CISC-бік
GREEN  = "#1f8a3b"   # RISC-бік
F_BLUE = "#f3f5fd"
F_GRN  = "#eef7ee"
F_GREY = "#f4f5f7"


# ── question: дві відповіді на одне питання ───────────────────────────────────
# Ідея: одне питання вгорі, від нього дві стрілки до двох протилежних світоглядів.
# Читач має одразу побачити, що це не дрібниця, а РОЗВИЛКА.

def fig_question():
    W, H = 720, 340
    p = []
    qb, qw, qh = textbox(W / 2, 58, "Скільки команд має знати процесор?",
                         size=15, bold=True, fill=F_GREY, stroke=INK, sw=2, pad=14)
    p.append(qb)

    lx, rx, ty = 210, 510, 150
    p.append(arrow(W / 2 - 30, 58 + qh / 2, lx, ty - 56, color=GREEN, sw=2))
    p.append(arrow(W / 2 + 30, 58 + qh / 2, rx, ty - 56, color=BLUE, sw=2))

    risc = "RISC\nмало, усі прості\nоднакова довжина\n~1 такт кожна"
    cisc = "CISC\nбагато, є складні\nрізна довжина\nрізна тривалість"
    rb, rw, rh = textbox(lx, ty + 8, risc, size=12, bold=True, color=GREEN, fill=F_GRN, stroke=GREEN, sw=2, pad=12)
    cb, cw, ch = textbox(rx, ty + 8, cisc, size=12, bold=True, color=BLUE, fill=F_BLUE, stroke=BLUE, sw=2, pad=12)
    p.append(rb); p.append(cb)

    p.append(text(lx, ty + 8 + rh / 2 + 26, "ARM · RISC-V · AVR · Xtensa (ESP32)", size=11, color=GREEN))
    p.append(text(rx, ty + 8 + ch / 2 + 26, "x86 — процесори ПК", size=11, color=BLUE))
    p.append(text(W / 2, H - 18, "Дві протилежні відповіді на одне й те саме питання.",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "question.svg"), W, H, *p,
           title="Розвилка філософії: мало простих чи багато складних?")


# ── same-task: одна задача двома способами ────────────────────────────────────
# Ідея (worked-приклад у картинці): та сама робота — CISC однією командою,
# RISC трьома. Поруч видно load/store: пам'ять чіпають лише LD/ST.

def fig_same_task():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 54, "Задача: m = m + R1  (число m лежить у пам'яті)",
                  size=13, bold=True))

    # ── ліва колонка: CISC ──
    lx, lw = 60, 300
    p.append(rect(lx, 80, lw, 220, fill=F_BLUE, stroke=BLUE, sw=2, rx=10))
    p.append(text(lx + lw / 2, 106, "CISC — одна команда", size=12.5, bold=True, color=BLUE))
    p.append(rect(lx + 24, 124, lw - 48, 40, fill=BG, stroke=BLUE, sw=1.6, rx=6))
    p.append(text(lx + lw / 2, 149, "ADD [m], R1", size=14, bold=True))
    p.append(text(lx + lw / 2, 188, "ця одна команда сама:", size=10.5, color=MUTED, italic=True))
    for i, t in enumerate(("1. читає m з пам'яті", "2. додає R1", "3. пише суму назад у m")):
        p.append(text(lx + 40, 210 + i * 22, t, size=11, anchor="start"))
    p.append(text(lx + lw / 2, 288, "коротко в коді · важко й довго виконати",
                  size=10.5, color=BLUE, bold=True))

    # ── права колонка: RISC ──
    rx, rw = 400, 300
    p.append(rect(rx, 80, rw, 220, fill=F_GRN, stroke=GREEN, sw=2, rx=10))
    p.append(text(rx + rw / 2, 106, "RISC — три прості команди", size=12.5, bold=True, color=GREEN))
    rows = [("LD  R2, [m]", "; завантажити m у регістр"),
            ("ADD R2, R1", "; додати в регістрах"),
            ("ST  [m], R2", "; зберегти назад")]
    for i, (op, cm) in enumerate(rows):
        ry = 124 + i * 40
        p.append(rect(rx + 20, ry, rw - 40, 32, fill=BG, stroke=GREEN, sw=1.5, rx=6))
        p.append(text(rx + 34, ry + 21, op, size=11.5, bold=True, anchor="start"))
        p.append(text(rx + 150, ry + 21, cm, size=10, color=MUTED, anchor="start"))
    p.append(text(rx + rw / 2, 288, "кожна проста · ~1 такт · легко в конвеєр",
                  size=10.5, color=GREEN, bold=True))

    # ── спільний висновок: load/store ──
    p.append(text(W / 2, 332,
                  "У RISC пам'ять чіпають ЛИШЕ LD і ST; обчислення — між регістрами (load/store).",
                  size=11.5, bold=True))
    p.append(text(W / 2, 358,
                  "Та сама робота: CISC економить рядки коду, RISC — складність заліза.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "same-task.svg"), W, H, *p)


# ── tradeoff: ваги двох сторін ────────────────────────────────────────────────
# Ідея: дві колонки «за/проти», щоб читач побачив, що це не «краще-гірше», а обмін.

def fig_tradeoff():
    W, H = 740, 340
    p = []
    p.append(text(W / 2, 50, "Кожна сторона за щось платить", size=14, bold=True))

    def column(cx, title, color, fill, plus, minus):
        out = [rect(cx - 150, 76, 300, 210, fill=fill, stroke=color, sw=2, rx=10),
               text(cx, 102, title, size=12.5, bold=True, color=color)]
        out.append(text(cx - 128, 130, "виграш", size=10.5, color=GREEN, anchor="start", bold=True))
        for i, t in enumerate(plus):
            out.append(text(cx - 128, 150 + i * 20, "+ " + t, size=10.5, anchor="start"))
        base = 150 + len(plus) * 20 + 14
        out.append(text(cx - 128, base, "ціна", size=10.5, color=POS, anchor="start", bold=True))
        for i, t in enumerate(minus):
            out.append(text(cx - 128, base + 20 + i * 20, "− " + t, size=10.5, anchor="start"))
        return out

    p += column(205, "CISC", BLUE, F_BLUE,
                ["компактний код", "менше команд на дію"],
                ["різна довжина команд", "складне декодування", "важкий конвеєр", "ненажерливе залізо"])
    p += column(535, "RISC", GREEN, F_GRN,
                ["просте декодування", "гладкий конвеєр", "просте й економне залізо"],
                ["довший код", "більше команд на дію"])

    p.append(text(W / 2, 312,
                  "CISC родом з епохи, коли пам'ять була дорога, а код часто писали вручну.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p)


# ── revolution: чому викинули складні команди ─────────────────────────────────
# Ідея: гістограма частоти команд — кілька простих величезні, складні крихітні;
# і висновок-стрілка «оптимізуй типовий випадок».

def fig_revolution():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 46, "Спостереження, що схилило терези", size=14, bold=True))

    ox, oy = 90, 250
    aw, ah = 420, 180
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 18, oy - ah, "як\nчасто", size=10, color=INK, anchor="end"))

    bars = [("прості", 0.95, GREEN), ("прості", 0.82, GREEN), ("прості", 0.7, GREEN),
            ("прості", 0.5, GREEN), ("складні", 0.12, BLUE), ("складні", 0.06, BLUE)]
    bw = aw / (len(bars) + 1.2)
    for i, (lab, frac, col) in enumerate(bars):
        bx = ox + 12 + i * bw
        bh = ah * frac
        fill = F_GRN if col == GREEN else F_BLUE
        p.append(rect(bx, oy - bh, bw * 0.74, bh, fill=fill, stroke=col, sw=1.5, rx=4))
    p.append(text(ox + 12 + 1.5 * bw, oy + 18, "кілька простих — майже весь код", size=10, color=GREEN))
    p.append(text(ox + 12 + 4.9 * bw, oy + 18, "складні — рідкісні", size=10, color=BLUE))

    concl, ww, wh = textbox(ox + aw + 100, oy - ah / 2 - 4,
                            "Викинь рідкісні\nскладні команди.\nЛиши мало простих —\nі зроби їх\nблискавичними.",
                            size=11.5, bold=True, color=INK, fill=F_GREY, stroke=INK, sw=1.8, pad=12)
    p.append(concl)
    p.append(text(ox + aw + 100, oy - ah / 2 + wh / 2 + 22,
                  "«оптимізуй типовий випадок»", size=11, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "Складне хай складає компілятор — а залізо хай летить.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "revolution.svg"), W, H, *p)


# ── convergence: CISC зовні, RISC усередині ───────────────────────────────────
# Ідея: конвеєр x86 — складна команда входить, декодер ріже її на µops,
# далі тече RISC-подібне ядро. Видима ISA лишається CISC заради сумісності.

def fig_convergence():
    W, H = 780, 300
    p = []
    p.append(text(W / 2, 48, "Сучасний x86: складна мова зовні, прості кроки всередині",
                  size=13.5, bold=True))

    y = 150
    # вхід — складна команда
    b1 = fitbox(40, y - 34, 150, 68, "складна\nx86-команда\n(видима ISA)",
                size=11, fill=F_BLUE, stroke=BLUE, sw=2, bold=True, color=BLUE)
    p.append(b1)
    p.append(arrow(192, y, 236, y, color=INK, sw=1.8))

    # декодер
    b2 = fitbox(238, y - 34, 150, 68, "декодер\nрозкладає", size=11.5, fill=F_GREY, stroke=INK, sw=2, bold=True)
    p.append(b2)
    p.append(arrow(390, y, 434, y, color=INK, sw=1.8))

    # три µops
    for i in range(3):
        my = y - 40 + i * 40
        p.append(rect(436, my - 14, 150, 28, fill=F_GRN, stroke=GREEN, sw=1.5, rx=6))
        p.append(text(511, my + 5, "µop %d" % (i + 1), size=11, bold=True, color=GREEN))
    p.append(arrow(588, y, 632, y, color=INK, sw=1.8))

    # RISC-ядро
    b3 = fitbox(634, y - 34, 110, 68, "RISC-подібне\nядро\n(конвеєр)",
                size=11, fill=F_GRN, stroke=GREEN, sw=2, bold=True, color=GREEN)
    p.append(b3)

    p.append(text(511, y + 70, "µops — прості RISC-подібні мікрооперації", size=10.5, color=GREEN))
    p.append(text(W / 2, H - 36,
                  "Видима ISA лишається CISC заради СУМІСНОСТІ зі старим софтом;",
                  size=11.5, bold=True))
    p.append(text(W / 2, H - 16,
                  "реалізація під нею — RISC-стилю. Перемогла сама ідея простих швидких кроків.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "convergence.svg"), W, H, *p)


# ── where: хто де панує і чому ────────────────────────────────────────────────
# Ідея: дві колонки доменів; підкреслено РІЗНІ причини переваги —
# RISC через енергію, CISC через спадщину софту.

def fig_where():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 48, "Хто де панує — і чому саме", size=14, bold=True))

    # RISC-колонка
    lx, lw = 50, 320
    p.append(rect(lx, 76, lw, 200, fill=F_GRN, stroke=GREEN, sw=2, rx=10))
    p.append(text(lx + lw / 2, 102, "RISC — де вирішує енергія", size=12.5, bold=True, color=GREEN))
    risc = ["телефони й планшети (ARM)", "мікроконтролери (AVR, Cortex-M)",
            "ESP32 (Xtensa; нові — RISC-V)", "дедалі більше серверів"]
    for i, t in enumerate(risc):
        p.append(text(lx + 26, 132 + i * 24, "• " + t, size=11, anchor="start"))
    p.append(text(lx + lw / 2, 250, "просте залізо → менше кремнію → довша батарея",
                  size=10, color=GREEN, bold=True))

    # CISC-колонка
    rx, rw = 390, 320
    p.append(rect(rx, 76, rw, 200, fill=F_BLUE, stroke=BLUE, sw=2, rx=10))
    p.append(text(rx + rw / 2, 102, "CISC — де вирішує спадщина", size=12.5, bold=True, color=BLUE))
    cisc = ["настільні ПК", "ноутбуки", "багато серверів"]
    for i, t in enumerate(cisc):
        p.append(text(rx + 26, 132 + i * 24, "• " + t, size=11, anchor="start"))
    p.append(text(rx + rw / 2, 234, "тримається на СУМІСНОСТІ —", size=10.5, color=BLUE, bold=True))
    p.append(text(rx + rw / 2, 250, "десятиліттях готового софту", size=10.5, color=BLUE, bold=True))

    p.append(text(W / 2, 304, "Сила x86 — не в архітектурі, а в екосистемі.", size=12, bold=True))
    p.append(text(W / 2, 326, "Та й цю межу розмиває перехід ноутбуків і серверів на ARM.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "where.svg"), W, H, *p)


if __name__ == "__main__":
    fig_question()
    fig_same_task()
    fig_tradeoff()
    fig_revolution()
    fig_convergence()
    fig_where()
    print("OK: figures written to", OUT)
