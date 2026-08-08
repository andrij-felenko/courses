# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"


# ── 1. Сигнальний кадр на стеку користувача ─────────────────────────────────
def fig_stack_frame():
    W, H = 1180, 780
    p = []

    SX, SW = 60.0, 470.0          # колонка стека

    p.append(text(SX, 40, "стек користувача (росте вниз)", size=14, color=MUTED,
                  anchor="start", bold=True))

    # верхня частина: старі кадри
    p.append(rect(SX, 62, SW, 76, fill=FILL, stroke=MUTED, sw=1.5, rx=6))
    p.append(mtext(SX + SW / 2, 92, ["кадри функцій, які працювали",
                                     "в мить приходу сигналу"], size=13, color=MUTED))

    # позначка старої вершини
    p.append(line(SX - 26, 146, SX + SW + 26, 146, color=INK, sw=2, dash="7 5"))
    p.append(text(SX + SW + 34, 151, "покажчик стека до сигналу", size=12,
                  color=INK, anchor="start"))

    # червона зона
    p.append(rect(SX, 156, SW, 60, fill=WARM, stroke=POS, sw=2, rx=6))
    p.append(mtext(SX + SW / 2, 180, ["ЧЕРВОНА ЗОНА — 128 байтів",
                                      "ядро їх не чіпає: вони можуть бути зайняті"],
                   size=13, color=POS))

    # сам кадр
    p.append(rect(SX - 12, 232, SW + 24, 372, fill="#ffffff", stroke=NEG, sw=2.4, rx=10))
    p.append(text(SX + SW / 2, 258, "СИГНАЛЬНИЙ КАДР", size=15, color=NEG, bold=True))

    parts = [
        (274, 52, "адреса повернення → батут", COLD,
         "сюди подивиться інструкція\nповернення обробника"),
        (336, 128, "ucontext_t", GREENFILL,
         "uc_mcontext: усі регістри, покажчики\nінструкції та стека, прапорці\n"
         "uc_sigmask: маска, яку відновити\nuc_stack: запасний стек, що діяв"),
        (474, 52, "siginfo_t", SOFT,
         "номер, код причини, відправник,\nадреса збою  (при SA_SIGINFO)"),
        (536, 56, "розширений стан процесора", FILL,
         "регістри співпроцесора й векторні;\nрозмір залежить від розширень"),
    ]
    for y, h, head, fill, sub in parts:
        p.append(rect(SX + 4, y, SW - 8, h, fill=fill, stroke=MUTED, sw=1.4, rx=6))
        p.append(text(SX + 22, y + 20, head, size=13, color=INK, anchor="start", bold=True))
        p.append(mtext(SX + 22, y + 38, sub.split("\n"), size=11.5, color=MUTED,
                       anchor="start", lh=1.25))

    # нова вершина
    p.append(line(SX - 26, 612, SX + SW + 26, 612, color=NEG, sw=2.4))
    p.append(mtext(SX + SW + 34, 611, ["покажчик стека", "на вході в обробник"], size=12,
                   color=NEG, anchor="start", lh=1.25))

    p.append(rect(SX, 626, SW, 62, fill=FILL, stroke=MUTED, sw=1.4, rx=6, ))
    p.append(mtext(SX + SW / 2, 650, ["сюди ляжуть власні кадри обробника",
                                      "й кадри вкладених сигналів"], size=13, color=MUTED))
    p.append(arrow(SX + SW / 2, 700, SX + SW / 2, 740, color=MUTED, sw=1.6))
    p.append(text(SX + SW / 2, 762, "нижчі адреси", size=12, color=MUTED))

    # ── праворуч: що ядро кладе в регістри ──
    RX, RW = 700.0, 440.0
    p.append(rect(RX, 232, RW, 300, fill=SOFT, stroke=FIELD, sw=2, rx=10))
    p.append(text(RX + RW / 2, 260, "регістри перед стрибком в обробник",
                  size=14, color=FIELD, bold=True))

    regs = [
        ("1-й аргумент", "номер сигналу"),
        ("2-й аргумент", "адреса siginfo_t у кадрі"),
        ("3-й аргумент", "адреса ucontext_t у кадрі"),
        ("покажчик стека", "початок кадру, вирівняний за ABI"),
        ("покажчик інструкції", "адреса обробника"),
    ]
    for i, (a, b) in enumerate(regs):
        y = 284 + i * 46
        p.append(rect(RX + 18, y, 168, 34, fill=COLD, stroke=NEG, sw=1.3, rx=5))
        p.append(text(RX + 102, y + 22, a, size=12, color=INK))
        p.append(text(RX + 200, y + 22, b, size=12, color=MUTED, anchor="start"))

    p.append(fitbox(RX, 556, RW, 108,
                    "З погляду процесора нічого незвичайного:\n"
                    "виконується звичайна функція, у якої є\n"
                    "аргументи, свій стек і адреса повернення.\n"
                    "Виклику в програмі при цьому не було.",
                    size=13, fill=WARM, stroke=POS, sw=1.8, color=INK))

    render(os.path.join(OUT, "stack-frame.svg"), W, H, *p,
           title="Що ядро записує на стек користувача перед запуском обробника")


# ── 2. Повний оберт: від перерваної інструкції й назад до неї ───────────────
def fig_round_trip():
    W, H = 1240, 640
    p = []

    UY, KY = 150.0, 430.0          # смуги режимів
    p.append(rect(30, 92, 1180, 130, fill=SOFT, stroke=MUTED, sw=1.3, rx=8))
    p.append(text(46, 114, "режим користувача", size=13, color=MUTED, anchor="start", bold=True))
    p.append(rect(30, 372, 1180, 130, fill=FILL, stroke=MUTED, sw=1.3, rx=8))
    p.append(text(46, 394, "режим ядра", size=13, color=MUTED, anchor="start", bold=True))

    def ubox(x, w, s, accent, fill):
        p.append(fitbox(x, UY - 4, w, 74, s, size=12.5, fill=fill, stroke=accent,
                        sw=1.8, color=INK))

    def kbox(x, w, s, accent, fill):
        p.append(fitbox(x, KY - 4, w, 74, s, size=12.5, fill=fill, stroke=accent,
                        sw=1.8, color=INK))

    ubox(46, 190, "перервана інструкція\nпрограми", MUTED, SOFT)
    kbox(276, 214, "ядро на межі повернення\nбачить сигнал і будує\nкадр на стеку", NEG, COLD)
    ubox(516, 200, "обробник виконується\nяк звичайна функція", FIELD, GREENFILL)
    ubox(740, 190, "інструкція повернення\n→ батут:\nmov $15,%rax; syscall", POS, WARM)
    kbox(956, 224, "rt_sigreturn:\nчитає кадр, ставить маску,\nвідновлює всі регістри", NEG, COLD)

    # стрілки вниз/угору між смугами
    p.append(arrow(236, UY + 74, 300, KY - 6, color=MUTED, sw=1.8))
    p.append(arrow(430, KY - 6, 560, UY + 74, color=NEG, sw=1.8))
    p.append(arrow(716, UY + 34, 736, UY + 34, color=FIELD, sw=1.8))
    p.append(arrow(930, UY + 74, 990, KY - 6, color=POS, sw=1.8))

    # повернення на початок
    p.append(line(1068, KY + 74, 1068, 560, color=NEG, sw=2))
    p.append(line(1068, 560, 141, 560, color=NEG, sw=2))
    p.append(arrow(141, 560, 141, UY + 76, color=NEG, sw=2))
    p.append(text(604, 584, "керування повертається на ту саму інструкцію, "
                            "усі регістри й прапорці — як були", size=13, color=NEG, bold=True))

    p.append(text(620, 56, "Межу режимів перетинають чотири рази: два спуски в ядро "
                           "й два підйоми назад", size=14, color=INK, bold=True))

    render(os.path.join(OUT, "round-trip.svg"), W, H, *p,
           title="Оберт сигналу: підроблений виклик і розбирання кадру")


# ── 3. Куди лягає кадр: звичайний стек, переповнений, запасна площадка ──────
def fig_altstack():
    W, H = 1220, 620
    p = []

    cases = [
        (40, POS if False else FIELD, GREENFILL, "Звичайний випадок",
         ["місця під вершиною вдосталь", "кадр лягає на той самий стек",
          "обробник запускається"], True),
        (450, POS, WARM, "Переповнений стек",
         ["стек з'їдено рекурсією", "кадр записати нікуди",
          "ядро вбиває процес"], False),
        (860, NEG, COLD, "Запасна площадка",
         ["sigaltstack + SA_ONSTACK", "кадр лягає на окрему ділянку",
          "обробник запускається"], True),
    ]

    CW = 330.0
    for x, accent, fill, head, notes, ok in cases:
        p.append(rect(x, 46, CW, 500, fill="#ffffff", stroke=accent, sw=2.2, rx=10))
        p.append(text(x + CW / 2, 76, head, size=15, color=accent, bold=True))

    # ── випадок 1 ──
    x = 40
    p.append(rect(x + 40, 100, 250, 120, fill=FILL, stroke=MUTED, sw=1.4, rx=6))
    p.append(text(x + 165, 164, "вільне місце", size=13, color=MUTED))
    p.append(rect(x + 40, 224, 250, 74, fill=GREENFILL, stroke=FIELD, sw=2, rx=6))
    p.append(text(x + 165, 266, "сигнальний кадр", size=13, color=FIELD, bold=True))
    p.append(rect(x + 40, 302, 250, 88, fill=SOFT, stroke=MUTED, sw=1.4, rx=6))
    p.append(text(x + 165, 352, "кадри програми", size=13, color=MUTED))
    p.append(mtext(x + 24, 424, ["• місця під вершиною вдосталь",
                                 "• кадр лягає на той самий стек",
                                 "• обробник спокійно запускається"],
                   size=12.5, color=INK, anchor="start"))

    # ── випадок 2 ──
    x = 450
    p.append(rect(x + 40, 100, 250, 46, fill=WARM, stroke=POS, sw=2, rx=6, ))
    p.append(text(x + 165, 128, "сторожова сторінка", size=12.5, color=POS, bold=True))
    p.append(rect(x + 40, 150, 250, 240, fill=SOFT, stroke=MUTED, sw=1.4, rx=6))
    p.append(mtext(x + 165, 254, ["стек з'їдено рекурсією", "вільного місця немає"],
                   size=13, color=MUTED))
    p.append(mtext(x + 24, 424, ["• збій стався саме через брак місця",
                                 "• кадр записати нікуди",
                                 "• обробник не запуститься взагалі",
                                 "• процес убито, у журналі ядра —",
                                 "   слід про поганий кадр"],
                   size=12.5, color=INK, anchor="start"))

    # ── випадок 3 ──
    x = 860
    p.append(rect(x + 24, 100, 130, 290, fill=SOFT, stroke=MUTED, sw=1.4, rx=6))
    p.append(mtext(x + 89, 236, ["основний", "стек:", "місця нема"], size=12, color=MUTED))
    p.append(rect(x + 176, 100, 130, 106, fill=FILL, stroke=MUTED, sw=1.4, rx=6))
    p.append(text(x + 241, 156, "запас", size=12.5, color=MUTED))
    p.append(rect(x + 176, 210, 130, 90, fill=COLD, stroke=NEG, sw=2, rx=6))
    p.append(mtext(x + 241, 248, ["сигнальний", "кадр"], size=12.5, color=NEG, bold=True))
    p.append(text(x + 241, 330, "площадка", size=12.5, color=NEG))
    p.append(mtext(x + 24, 424, ["• площадка заведена наперед",
                                 "• кадр лягає осторонь від стека",
                                 "• переповнення стека нарешті",
                                 "   можна спіймати обробником"],
                   size=12.5, color=INK, anchor="start"))

    p.append(fitbox(40, 556, 1150, 44,
                    "Обробник виконується лише там, де ядру вдалося записати кадр — "
                    "інакше сигнал перетворюється на смерть процесу",
                    size=13.5, fill=FILL, stroke=INK, sw=1.8, color=INK))

    render(os.path.join(OUT, "altstack.svg"), W, H, *p,
           title="Три випадки: куди ядро кладе сигнальний кадр")


# ── 4. aarch64: ланцюг записів у sigcontext.__reserved ─────────────────────
def fig_aarch64_chain():
    W, H = 1230, 800
    p = []

    SX, BW = 250.0, 500.0

    # фіксована частина sigcontext
    p.append(rect(SX - 16, 54, BW + 32, 60, fill=COLD, stroke=NEG, sw=1.8, rx=8))
    p.append(text(SX + BW / 2, 78, "фіксована частина sigcontext", size=13.5,
                  color=NEG, bold=True))
    p.append(text(SX + BW / 2, 98, "fault_address · regs[0..30] · sp · pc · pstate",
                  size=12, color=MUTED))

    p.append(text(SX - 16, 140, "__reserved[4096] — ланцюг записів змінної довжини",
                  size=13.5, color=INK, anchor="start", bold=True))

    # зовнішня рамка ланцюга
    p.append(rect(SX - 16, 152, BW + 32, 572, fill=SOFT, stroke=MUTED, sw=1.6, rx=10))

    recs = [
        (170, "fpsimd_context", "magic 0x46508001", "size 528",
         "fpsr, fpcr, 32 векторні регістри по 128 бітів", GREENFILL, FIELD),
        (290, "esr_context", "magic 0x45535201", "size 16",
         "ESR_EL1 — чому саме стався збій (лише для збоїв)", WARM, POS),
        (410, "sve_context", "magic 0x53564501", "size залежить від vl",
         "довжина вектора vl задає, скільки байтів далі", FILL, MUTED),
        (530, "extra_context", "magic 0x45585401", "size 32",
         "решта не вмістилась: datap веде на продовження", COLD, NEG),
    ]
    for y, name, magic, size, sub, fill, stroke in recs:
        p.append(rect(SX, y, BW, 76, fill=fill, stroke=stroke, sw=1.6, rx=6))
        p.append(text(SX + 18, y + 24, name, size=13.5, color=INK,
                      anchor="start", bold=True))
        p.append(text(SX + BW - 18, y + 24, magic, size=11.5, color=MUTED,
                      anchor="end"))
        p.append(text(SX + 18, y + 46, sub, size=11.5, color=MUTED, anchor="start"))
        p.append(text(SX + 18, y + 66, size, size=11.5, color=stroke, anchor="start"))

    # термінатор
    p.append(rect(SX, 650, BW, 54, fill="#ffffff", stroke=INK, sw=2.2, rx=6))
    p.append(text(SX + 18, 673, "термінатор", size=13.5, color=INK,
                  anchor="start", bold=True))
    p.append(text(SX + 18, 693, "magic = 0  ·  size = 0  —  кінець ланцюга",
                  size=11.5, color=INK, anchor="start"))

    # стрибки «+ size»
    for gy in (254, 374, 494, 614):
        p.append(arrow(SX - 46, gy, SX - 46, gy + 30, color=INK, sw=1.8))
        p.append(text(SX - 78, gy + 20, "+ size", size=12, color=INK, anchor="end"))

    p.append(arrow(SX + BW / 2, 116, SX + BW / 2, 150, color=NEG, sw=1.8))

    # ── праворуч: правило обходу ──
    RX, RW = 810.0, 380.0
    p.append(fitbox(RX, 170, RW, 180,
                    "ЯК ЧИТАТИ\n\n"
                    "1. стати на початок __reserved\n"
                    "2. прочитати magic поточного запису\n"
                    "3. не той, що шукаєте — додати size\n"
                    "    до адреси й повторити\n"
                    "4. magic == 0 — записів більше немає",
                    size=13, fill=SOFT, stroke=FIELD, sw=2, color=INK))

    p.append(fitbox(RX, 380, RW, 150,
                    "Порядку записів не гарантовано.\n"
                    "Шукати треба за magic, а не за зсувом:\n"
                    "набір записів залежить від того,\n"
                    "які розширення має процесор\n"
                    "і що саме сталося з програмою.",
                    size=13, fill=FILL, stroke=MUTED, sw=1.6, color=INK))

    p.append(fitbox(RX, 560, RW, 164,
                    "extra_context — запобіжник:\n"
                    "коли записи не влазять у 4096 байтів,\n"
                    "ядро кладе його передостаннім,\n"
                    "а поле datap показує на продовження\n"
                    "ланцюга, виділене нижче на стеку.",
                    size=13, fill=COLD, stroke=NEG, sw=1.8, color=INK))

    render(os.path.join(OUT, "aarch64-chain.svg"), W, H, *p,
           title="aarch64: записи змінної довжини всередині sigcontext")


# ── 5. Що насправді означає збережений покажчик інструкції ──────────────────
def fig_saved_rip():
    W, H = 1180, 630
    p = []

    def strip(y_head, head, items, mark_i, mark_lines, mark_color, note_fill,
              note_stroke, note):
        p.append(text(70, y_head, head, size=15, color=INK, anchor="start", bold=True))
        # порахувати позицію позначеної рамки
        x, boxes = 70.0, []
        for w, _h, _s, _f, _st in items:
            boxes.append((x, w))
            x += w + 18
        bx, bw = boxes[mark_i]
        cx = bx + bw / 2
        p.append(mtext(cx, y_head + 32, mark_lines, size=12.5, color=mark_color,
                       lh=1.35, bold=True))
        y_box = y_head + 90
        p.append(arrow(cx, y_box - 26, cx, y_box - 4, color=mark_color, sw=2.4))
        for (bx2, bw2), (w, htxt, sub, fill, st) in zip(boxes, items):
            p.append(rect(bx2, y_box, w, 60, fill=fill, stroke=st, sw=1.9, rx=6))
            p.append(text(bx2 + w / 2, y_box + 25, htxt, size=13.5, color=INK, bold=True))
            p.append(text(bx2 + w / 2, y_box + 45, sub, size=11.5, color=MUTED))
        p.append(fitbox(70, y_box + 78, 1040, 96, note, size=13,
                        fill=note_fill, stroke=note_stroke, sw=1.8, color=INK))

    strip(66, "А. Збій від самої інструкції",
          [(280, "…попередні інструкції…", "уже виконані", FILL, MUTED),
           (330, "movq (%rdi), %rax", "ось вона впала", WARM, POS),
           (300, "movl $1, %eax", "ще не виконана", FILL, MUTED)],
          1, ["збережений RIP", "показує САМЕ на аварійну інструкцію"], POS,
          WARM, POS,
          "Повернення без правки → процесор виконає ТУ САМУ інструкцію → той самий збій → той самий сигнал.\n"
          "Якщо обробник не усунув причину й не переставив RIP, це нескінченний цикл.")

    strip(370, "Б. Сигнал застав перерваний системний виклик",
          [(280, "movl $0, %eax", "номер виклику read", FILL, MUTED),
           (250, "syscall", "два байти", COLD, NEG),
           (380, "cmpq $-1, %rax", "сюди виклик повернувся б", FILL, MUTED)],
          1, ["збережений RIP — ВІДКОЧЕНИЙ на два байти назад,",
              "а в RAX лежить номер виклику, не результат"], NEG,
          COLD, NEG,
          "Ядро вже приготувало повтор виклику — ДО того, як побудувало кадр. Переставите RIP — повтору не буде;\n"
          "перепишете RAX — виклик піде з чужим номером. Правити контекст безпечно лише для сигналів,\n"
          "породжених самою інструкцією: SIGSEGV, SIGBUS, SIGILL, SIGFPE.")

    render(os.path.join(OUT, "saved-rip.svg"), W, H, *p,
           title="Збережений RIP означає різне залежно від того, звідки прийшов сигнал")


fig_stack_frame()
fig_round_trip()
fig_altstack()
fig_aarch64_chain()
fig_saved_rip()
print("ok")
