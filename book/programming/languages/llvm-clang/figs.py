# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
IR_BG   = "#151d2b"
IR_FG   = "#bcd0ff"
ASM_FG  = "#7fe0a0"


def codebox(x, y, w, h, s, fg=CODE_FG, bg=CODE_BG, size=12):
    """Темна рамка з моноширинним рядком, вирівняним ліворуч."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=8)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="start" font-weight="700">%s</text>'
            % (x + 14, y + h / 2 + size * 0.35, size, fg, esc(s)))
    return out


# ── explosion: M×N без IR  vs  M+N з IR ────────────────────────────────────────
# Ідея: ліворуч кожна мова тягне свій провід до кожного ядра (плутанина M×N);
# праворуч усі сходяться в IR, від IR — по одному проводу до ядра (M+N).

def fig_explosion():
    W, H = 820, 380
    p = []
    langs = ["C", "Rust", "Swift"]
    chips = ["ARM", "RISC-V", "x86"]

    # ── ліва панель: кожна мова → кожне ядро (M×N) ──
    p.append(text(200, 60, "без спільного IR", size=13, color=POS, bold=True))
    lx_l, cx_l = 70, 330
    ly = [110, 170, 230]
    cy = [110, 170, 230]
    lboxes, cboxes = [], []
    for i, l in enumerate(langs):
        b, w, h = textbox(lx_l, ly[i], l, size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.6, min_w=64)
        p.append(b); lboxes.append((lx_l + w / 2, ly[i]))
    for j, c in enumerate(chips):
        b, w, h = textbox(cx_l, cy[j], c, size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6, min_w=76)
        cboxes.append((cx_l - w / 2, cy[j], b))
    # проводи M×N (малюємо ПІД коробками ядер)
    for (lx, lyy) in lboxes:
        for (cxx, cyy, _b) in cboxes:
            p.append(line(lx + 34, lyy, cxx - 4, cyy, color="#c0392b", sw=1.2))
    for (_c1, _c2, b) in cboxes:
        p.append(b)
    p.append(text(200, 300, "3 × 3 = 9 окремих перекладачів", size=11, color=POS, bold=True))
    p.append(text(200, 320, "нова мова АБО нове ядро → ще ціла пачка", size=10, color=MUTED, italic=True))

    # ── розділювач ──
    p.append(line(W / 2, 80, W / 2, 300, color=MUTED, sw=1.2, dash="4 4"))

    # ── права панель: усе сходиться в IR (M+N) ──
    ox = 440
    p.append(text(ox + 180, 60, "зі спільним IR", size=13, color=FIELD, bold=True))
    lx_r, ir_x, cx_r = ox + 20, ox + 190, ox + 340
    lyr = [110, 170, 230]
    cyr = [110, 170, 230]
    lr, cr = [], []
    for i, l in enumerate(langs):
        b, w, h = textbox(lx_r, lyr[i], l, size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.6, min_w=64)
        p.append(b); lr.append((lx_r + w / 2, lyr[i]))
    # центральний вузол IR
    irb, iw, ih = textbox(ir_x, 170, "IR\n+ оптимізатор", size=11, bold=True,
                          fill="#fff7e6", stroke="#b8860b", sw=2.2, min_w=110, color="#b8860b")
    for (lx, lyy) in lr:
        p.append(line(lx + 34, lyy, ir_x - iw / 2, 170, color=FIELD, sw=1.6))
    p.append(irb)
    for j, c in enumerate(chips):
        b, w, h = textbox(cx_r, cyr[j], c, size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.6, min_w=76)
        p.append(line(ir_x + iw / 2, 170, cx_r - w / 2, cyr[j], color=NEG, sw=1.6))
        p.append(b)
    p.append(text(ox + 180, 300, "3 + 3 = 6 частин навколо однієї серцевини", size=11, color=FIELD, bold=True))
    p.append(text(ox + 180, 320, "нова мова = 1 перед; нове ядро = 1 зад", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "explosion.svg"), W, H, *p,
           title="Навіщо спільний IR: M×N перекладачів проти M+N частин")


# ── library: LLVM як бібліотека — перед (Clang та інші) · опт · зад ────────────
# Ідея: серцевина LLVM (опт над IR + кодогени під ядра) — переносний СКЛАДНИК;
# зверху різні передні частини лишають той самий IR, знизу — той самий асемблер.

def fig_library():
    W, H = 800, 420
    p = []
    # верх: передні частини (кожна дає IR)
    fronts = [("Clang\nC / C++ / Obj-C", FIELD, "#eef6ef"),
              ("Swift", NEG, "#eef4ff"),
              ("Rust", "#b8860b", "#fff7e6"),
              ("Julia, …", MUTED, "#f3f4f6")]
    fx = [110, 300, 470, 640]
    for (lab, col, fill), x in zip(fronts, fx):
        b, w, h = textbox(x, 80, lab, size=10.5, bold=True, fill=fill, stroke=col, sw=1.8, min_w=120, color=col)
        p.append(b)
        p.append(arrow(x, 80 + h / 2, x, 150, color=col, sw=1.8))
        p.append(text(x + 40, 128, "IR", size=10, color=col, anchor="start", bold=True))
    # серцевина: рамка LLVM
    p.append(rect(60, 158, 680, 150, fill="#fbfffb", stroke=FIELD, sw=2, rx=14))
    p.append(text(W / 2, 180, "LLVM — переносна серцевина (та сама для всіх мов)", size=12, color=FIELD, bold=True))
    # усередині серцевини: IR → оптимізатор (opt) → кодогени
    p.append(codebox(90, 205, 150, 40, "IR (SSA)", size=12, bg=IR_BG, fg=IR_FG))
    p.append(arrow(244, 225, 292, 225, color=INK, sw=2))
    b, w, h = textbox(370, 225, "оптимізатор\n(проходи над IR)", size=10.5, bold=True,
                      fill="#fff7e6", stroke="#b8860b", sw=1.8, min_w=170, color="#b8860b")
    p.append(b)
    p.append(arrow(370 + w / 2, 225, 520, 225, color=INK, sw=2))
    b2, w2, h2 = textbox(620, 225, "кодогени\nпід ядра", size=10.5, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, min_w=150, color=NEG)
    p.append(b2)
    # низ: ядра
    chips = [("ARM", NEG), ("RISC-V", NEG), ("Xtensa", NEG), ("x86", NEG)]
    cxs = [150, 320, 490, 650]
    for (lab, col), x in zip(chips, cxs):
        p.append(arrow(620, 225 + h2 / 2, x, 350, color=NEG, sw=1.6))
        b, w, h = textbox(x, 372, lab, size=10.5, bold=True, fill=BG, stroke=INK, sw=1.4, min_w=96)
        p.append(b)
    p.append(text(W / 2, H - 12, "передню частину пишуть раз на мову, задню — раз на ядро; оптимізатор — спільний",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "library.svg"), W, H, *p,
           title="LLVM як бібліотека: багато передів → одна серцевина → багато ядер")


# ── ir-shape: одна C-функція → її LLVM IR (SSA, типовані регістри) ─────────────
# Ідея: показати, що IR — це проста, одноманітна «псевдо-асемблерна» мова, де
# кожне ім'я присвоюють РІВНО раз (SSA), з явними типами (i32).

def fig_ir_shape():
    W, H = 800, 340
    p = []
    # ліворуч: C
    p.append(text(200, 62, "як ви написали (C)", size=12, color=FIELD, bold=True))
    csrc = [
        "int add_scaled(int a, int b) {",
        "    int t = a * 4;",
        "    return t + b;",
        "}",
    ]
    y = 84
    for ln in csrc:
        p.append(codebox(50, y, 320, 34, ln, size=11.5))
        y += 40
    # стрілка
    p.append(arrow(380, 170, 430, 170, color=INK, sw=2.4))
    p.append(text(405, 156, "clang", size=9, color=MUTED, bold=True))
    p.append(text(405, 194, "-emit-llvm", size=8.5, color=MUTED))
    # праворуч: IR
    p.append(text(610, 62, "проміжне подання LLVM (IR)", size=12, color="#b8860b", bold=True))
    ir = [
        "define i32 @add_scaled(i32 %a, i32 %b) {",
        "  %t   = mul i32 %a, 4",
        "  %sum = add i32 %t, %b",
        "  ret i32 %sum",
        "}",
    ]
    y = 84
    for ln in ir:
        p.append(codebox(440, y, 330, 34, ln, size=11, bg=IR_BG, fg=IR_FG))
        y += 40
    p.append(text(W / 2, H - 26, "кожен %-регістр присвоєно РІВНО раз (SSA); тип явний (i32); ще не прив'язано до ядра",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "ir-shape.svg"), W, H, *p,
           title="IR зблизька: та сама функція мовою LLVM")


# ── three-forms: одне IR — три обличчя (пам'ять · .bc біткод · .ll текст) ──────
# Ідея: IR існує в трьох рівноцінних формах; між ними переходять без втрат.

def fig_three_forms():
    W, H = 760, 300
    p = []
    cx = W / 2
    # центр — «те саме IR»
    cb, cw, ch = textbox(cx, 150, "одне й те саме IR", size=13, bold=True,
                         fill="#fff7e6", stroke="#b8860b", sw=2.2, min_w=200, color="#b8860b")
    forms = [
        (150, 90, "у пам'яті\nкомпілятора", "структури C++", NEG, "#eef4ff"),
        (150, 210, "біткод .bc", "стисло, для машини", FIELD, "#eef6ef"),
        (610, 150, "текст .ll", "читомо людині", POS, "#fdecea"),
    ]
    for x, y, lab, sub, col, fill in forms:
        b, w, h = textbox(x, y, lab, size=11, bold=True, fill=fill, stroke=col, sw=1.8, min_w=150, color=col)
        p.append(b)
        p.append(text(x, y + h / 2 + 16, sub, size=9.5, color=MUTED, italic=True))
        # двобічна стрілка до центру
        p.append(line(x, y, cx, 150, color=col, sw=1.6, dash="5 3"))
    p.append(cb)
    p.append(text(cx, H - 22, "між формами переходять без втрат: те саме подання, різна упаковка",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "three-forms.svg"), W, H, *p,
           title="Три обличчя IR: пам'ять · біткод · текст")


# ── jvm-vs-llvm: розвилка задуму — JVM (JIT на льоту) vs LLVM (AOT наскрізно) ──
# Ідея: ліворуч модель Java — байткод крутить ВМ, JIT квапливо латає гарячі місця;
# праворуч задум LLVM — те саме нейтральне подання, але завчасна оптимізація всієї програми.

def fig_jvm_vs_llvm():
    W, H = 820, 380
    p = []
    # ── розділювач ──
    p.append(line(W / 2, 70, W / 2, 320, color=MUTED, sw=1.2, dash="4 4"))

    # ── ліва панель: JVM ──
    p.append(text(205, 56, "модель Java (JVM)", size=13, color=NEG, bold=True))
    b, w, h = textbox(205, 108, "переносний\nбайткод", size=11, bold=True,
                      fill="#eef4ff", stroke=NEG, sw=1.8, min_w=150, color=NEG)
    p.append(b)
    p.append(arrow(205, 108 + h / 2, 205, 176, color=NEG, sw=1.8))
    b2, w2, h2 = textbox(205, 200, "віртуальна машина\n+ JIT на льоту", size=11, bold=True,
                         fill="#fff7e6", stroke="#b8860b", sw=1.8, min_w=190, color="#b8860b")
    p.append(b2)
    p.append(text(205, 262, "оптимізує ШМАТКАМИ під час виконання", size=10, color=POS, bold=True))
    p.append(text(205, 284, "часу обмаль — глибоко копати ніколи", size=9.5, color=MUTED, italic=True))

    # ── права панель: задум LLVM ──
    ox = 410
    p.append(text(ox + 205, 56, "задум LLVM", size=13, color=FIELD, bold=True))
    b, w, h = textbox(ox + 205, 108, "нейтральне\nподання (IR)", size=11, bold=True,
                      fill="#eef6ef", stroke=FIELD, sw=1.8, min_w=150, color=FIELD)
    p.append(b)
    p.append(arrow(ox + 205, 108 + h / 2, ox + 205, 176, color=FIELD, sw=1.8))
    b2, w2, h2 = textbox(ox + 205, 200, "завчасна (AOT)\nоптимізація", size=11, bold=True,
                         fill="#fff7e6", stroke="#b8860b", sw=1.8, min_w=190, color="#b8860b")
    p.append(b2)
    p.append(text(ox + 205, 262, "бачить УСЮ програму разом", size=10, color=FIELD, bold=True))
    p.append(text(ox + 205, 284, "часу скільки треба — оптимізує наскрізно", size=9.5, color=MUTED, italic=True))

    p.append(text(W / 2, H - 18, "«та сама ідея, але нижче рівнем і заздалегідь» — звідси назва Low Level Virtual Machine",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(OUT, "jvm-vs-llvm.svg"), W, H, *p,
           title="Розвилка задуму: JVM на льоту проти LLVM наскрізно")


# ── why-clang: три сили, що штовхали Apple до власного переднього кінця ─────────
# Ідея: ліцензія (GPL vs дозвільна) · Objective-C (периферія в GCC) · IDE (замкнений vs бібліотека).

def fig_why_clang():
    W, H = 800, 360
    p = []
    p.append(text(W / 2, 46, "чому Apple не влаштовував GCC — три причини разом", size=12.5, color=INK, bold=True))
    cards = [
        (150, "ЛІЦЕНЗІЯ", "GPL зобовʼязує\nвідкривати зміни;\nдозвільна LLVM — ні", POS, "#fdecea"),
        (400, "МОВА", "Objective-C —\nголовна для Apple,\nу GCC на других ролях", NEG, "#eef4ff"),
        (650, "ІНСТРУМЕНТИ", "GCC замкнений;\nдля IDE треба\nперед-бібліотека", FIELD, "#eef6ef"),
    ]
    for cx, head, body, col, fill in cards:
        p.append(rect(cx - 110, 80, 220, 180, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(cx, 112, head, size=12.5, color=col, bold=True))
        p.append(line(cx - 80, 126, cx + 80, 126, color=col, sw=1.2))
        p.append(mtext(cx, 158, body.split("\n"), size=11, color=INK))
    # стрілки в спільний висновок
    for cx in (150, 400, 650):
        p.append(arrow(cx, 260, W / 2, 300, color=MUTED, sw=1.4))
    b, w, h = textbox(W / 2, 322, "→ збудувати ВЛАСНИЙ перед поверх LLVM = Clang", size=11.5, bold=True,
                      fill="#fff7e6", stroke="#b8860b", sw=2, min_w=440, color="#b8860b")
    p.append(b)
    render(os.path.join(OUT, "why-clang.svg"), W, H, *p,
           title="Три причини, чому Apple створила Clang замість GCC")


if __name__ == "__main__":
    fig_explosion()
    fig_library()
    fig_ir_shape()
    fig_three_forms()
    fig_jvm_vs_llvm()
    fig_why_clang()
    print("OK: figures written to", OUT)
