# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8860b"
MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def code_line(x, y, s, size=13.5, color="#e8e8e8", anchor="start", bold=True):
    w = ' font-weight="700"' if bold else ''
    a = ' text-anchor="%s"' % anchor
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%.1f" fill="%s"%s%s>%s</text>'
            % (x, y, MONO, size, color, a, w, esc(s)))


# ── three-shades: три різні «не гарантовано» ──────────────────────────────────
# Implementation-defined / unspecified / undefined — від найлагіднішого до згубного.
def fig_three_shades():
    W, H = 780, 340
    p = []
    cards = [
        (30, FIELD, "#f3faf4", "Означено реалізацією",
         ["компілятор ОБЕРЕ",
          "варіант і ЗАДОКУМЕНТУЄ",
          "його",
          "",
          "розмір int; зсув",
          "від'ємного числа"]),
        (280, GOLD, "#fdf6e9", "Неспецифіковано",
         ["один із кількох",
          "варіантів, але",
          "документувати не мусить",
          "",
          "порядок обчислення",
          "аргументів f(a(), b())"]),
        (530, POS, "#fdecea", "Невизначено (UB)",
         ["стандарт НЕ обіцяє",
          "нічого — програма",
          "втрачає будь-який сенс",
          "",
          "переповнення int;",
          "вихід за межі масиву"]),
    ]
    for x, col, fill, head, body in cards:
        p.append(rect(x, 66, 220, 210, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + 110, 92, head, size=12.5, color=col, bold=True))
        p.append(line(x + 20, 104, x + 200, 104, color=col, sw=1.2))
        for i, ln in enumerate(body):
            if ln:
                it = ln.startswith("розмір") or ln.startswith("порядок") or ln.startswith("переповнення")
                p.append(text(x + 110, 130 + i * 22, ln, size=10, color=(MUTED if it else INK),
                              italic=it))
    # шкала небезпеки внизу
    p.append(text(W / 2, 308, "керовано  →  непередбачувано, але локально  →  згубно на всю програму",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "three-shades.svg"), W, H, *p,
           title="Три різні «стандарт не гарантує»: означене, неспецифіковане, невизначене")


# ── null-check-removed: механізм CVE-2009-1897 ────────────────────────────────
# Розіменування ДО перевірки → компілятор виводить «tun ≠ null» → викидає if(!tun).
def fig_null_check():
    W, H = 780, 360
    p = []
    # код зліва
    p.append(rect(30, 66, 360, 240, fill="#0f1115", stroke=NEG, sw=2, rx=10))
    p.append(text(210, 92, "як написано", size=12.5, color="#9ecbff", bold=True))
    src = [
        ("s = tun->sk;", "#ffd479", "1. розіменували tun"),
        ("if (!tun)", "#e8e8e8", "2. аж тепер перевірка"),
        ("    return err;", "#e8e8e8", ""),
        ("use(s);", "#e8e8e8", ""),
    ]
    for i, (ln, col, note) in enumerate(src):
        y = 128 + i * 34
        p.append(code_line(52, y, ln, size=14, color=col))
        if note:
            p.append(text(372, y, note, size=9, color=MUTED, anchor="end", italic=True))
    p.append(text(210, 288, "розіменування було ДО перевірки", size=10, color="#ff8a80", bold=True))

    # висновок компілятора справа
    p.append(rect(430, 66, 320, 240, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(590, 92, "що вивів компілятор", size=12.5, color=POS, bold=True))
    reason = [
        "tun->sk уже спрацював —",
        "отже tun НЕ може бути null",
        "(інакше це UB, а UB",
        "не буває за задумом)",
        "",
        "→ if(!tun) завжди хибне",
        "→ перевірку ВИКИНУТО",
    ]
    for i, ln in enumerate(reason):
        if ln:
            bold = ln.startswith("→")
            p.append(text(590, 126 + i * 22, ln, size=10.5,
                          color=(POS if bold else INK), bold=bold))
    render(os.path.join(OUT, "null-check-removed.svg"), W, H, *p,
           title="Одне UB — і компілятор законно прибирає перевірку на null")


# ── overflow-loop: знакове переповнення «неможливе» → вічний цикл ──────────────
def fig_overflow_loop():
    W, H = 780, 320
    p = []
    p.append(rect(30, 66, 350, 210, fill="#0f1115", stroke=GOLD, sw=2, rx=10))
    p.append(text(205, 92, "код", size=12.5, color="#ffd479", bold=True))
    code = [
        "int i = 0;",
        "while (i + 1 > i)",
        "    i++;",
    ]
    for i, ln in enumerate(code):
        p.append(code_line(52, 128 + i * 30, ln, size=14))
    p.append(text(205, 246, "виглядає: «поки не переповниться»",
                  size=10, color=MUTED, italic=True))

    # ланцюг міркування праворуч
    steps = [
        ("знакове переповнення = UB", INK),
        ("отже його «не буває»", INK),
        ("→ i+1 > i ЗАВЖДИ істина", POS),
        ("→ умова стала true", POS),
        ("→ вічний цикл", POS),
    ]
    p.append(rect(420, 66, 330, 210, fill="#fdecea", stroke=POS, sw=2, rx=10))
    p.append(text(585, 92, "як міркує оптимізатор", size=12.5, color=POS, bold=True))
    for i, (s, col) in enumerate(steps):
        p.append(text(585, 126 + i * 28, s, size=10.5, color=col,
                      bold=s.startswith("→")))
    render(os.path.join(OUT, "overflow-loop.svg"), W, H, *p,
           title="«i+1 > i завжди істина» — бо переповнення оголошено неможливим")


# ── poison: UB отруює всю програму, не лише свій рядок ─────────────────────────
def fig_poison():
    W, H = 780, 300
    p = []
    # звичайний баг — локальний
    p.append(rect(30, 70, 340, 160, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(200, 98, "звичайна помилка", size=12.5, color=FIELD, bold=True))
    p.append(text(200, 128, "наслідок ЛОКАЛЬНИЙ:", size=10.5, color=INK, bold=True))
    p.append(text(200, 150, "неправильне число тут,", size=10, color=INK))
    p.append(text(200, 168, "решта коду ціла;", size=10, color=INK))
    p.append(text(200, 190, "можна відтворити й", size=10, color=INK))
    p.append(text(200, 208, "покроково знайти", size=10, color=INK))

    # UB — глобальне
    p.append(rect(410, 70, 340, 160, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    p.append(text(580, 98, "невизначена поведінка", size=12.5, color=POS, bold=True))
    p.append(text(580, 128, "наслідок ГЛОБАЛЬНИЙ:", size=10.5, color=POS, bold=True))
    p.append(text(580, 150, "код навколо теж «пливе» —", size=10, color=INK))
    p.append(text(580, 168, "перевірки зникають, порядок", size=10, color=INK))
    p.append(text(580, 190, "міняється; під іншим -O та сама", size=10, color=INK))
    p.append(text(580, 208, "програма поводиться інакше", size=10, color=INK))

    p.append(text(W / 2, 264, "UB — не «неправильна відповідь», а вихід програми з-під правил геть",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "poison.svg"), W, H, *p,
           title="Звичайний баг псує один рядок; UB знецінює всю програму")


# ── asm-diff: та сама функція під -O0 і під -O2 ───────────────────────────────
# Ліворуч перевірка на null є (test+je), праворуч оптимізатор її прибрав.
def fig_asm_diff():
    W, H = 820, 380
    p = []
    # -O0: перевірка на місці
    p.append(rect(30, 62, 370, 288, fill="#0f1115", stroke=FIELD, sw=2, rx=10))
    p.append(text(215, 88, "-O0  (перевірка ЖИВА)", size=12.5, color="#7ee2a8", bold=True))
    o0 = [
        ("mov   rax, [rdi]", "#e8e8e8", "rax = tun->sk"),
        ("mov   [sk], rax", "#e8e8e8", "зберегли sk"),
        ("cmp   rdi, 0", "#7ee2a8", "tun == 0 ?"),
        ("jne   .ok", "#7ee2a8", "ні → далі"),
        ("mov   eax, POLLERR", "#e8e8e8", "так → вихід"),
        ("ret", "#e8e8e8", ""),
        (".ok: ...", "#e8e8e8", "робота зі sk"),
    ]
    for i, (ln, col, note) in enumerate(o0):
        y = 120 + i * 31
        p.append(code_line(50, y, ln, size=12.5, color=col))
        if note:
            p.append(text(384, y, note, size=9, color=MUTED, anchor="end", italic=True))

    # -O2: перевірки немає
    p.append(rect(420, 62, 370, 288, fill="#0f1115", stroke=POS, sw=2, rx=10))
    p.append(text(605, 88, "-O2  (перевірку ВИКИНУТО)", size=12.5, color="#ff8a80", bold=True))
    o2 = [
        ("mov   rax, [rdi]", "#e8e8e8", "rax = tun->sk"),
        ("mov   [sk], rax", "#e8e8e8", "зберегли sk"),
        ("", "", ""),
        ("; cmp/jne зникли —", "#ff8a80", "перевірки"),
        (";  tun вважається", "#ff8a80", "«не null»"),
        ("", "", ""),
        ("...", "#e8e8e8", "одразу робота зі sk"),
    ]
    for i, (ln, col, note) in enumerate(o2):
        y = 120 + i * 31
        if ln:
            p.append(code_line(440, y, ln, size=12.5, color=col))
        if note:
            p.append(text(774, y, note, size=9, color=MUTED, anchor="end", italic=True))
    render(os.path.join(OUT, "asm-diff.svg"), W, H, *p,
           title="Той самий tun_chr_poll: під -O0 cmp/jne є, під -O2 їх нема")


# ── exploit-chain: як зникла перевірка стає підвищенням привілеїв ──────────────
def fig_exploit_chain():
    W, H = 820, 300
    p = []
    steps = [
        ("mmap 0", "нападник відображає\nпам'ять за адресою 0\nі кладе туди свій sk", NEG),
        ("poll()", "ядро кличе tun_chr_poll;\ntun == null, але перевірки\nвже нема в бінарнику", GOLD),
        ("tun->sk", "розіменування null\nчитає з адреси 0 —\nз даних нападника", POS),
        ("root", "керування переходить\nна код нападника\nу режимі ядра", POS),
    ]
    n = len(steps)
    bw, gap = 168, 26
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    for i, (head, body, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        p.append(rect(x, 96, bw, 130, fill="#fbfbfc", stroke=col, sw=2, rx=10))
        p.append(text(x + bw / 2, 122, head, size=13, color=col, bold=True))
        p.append(line(x + 18, 134, x + bw - 18, 134, color=col, sw=1.2))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(x + bw / 2, 156 + j * 18, ln, size=9.5, color=INK))
        if i < n - 1:
            ax = x + bw
            p.append(arrow(ax + 3, 161, ax + gap - 3, 161, color=INK, sw=2))
    p.append(text(W / 2, 268,
                  "одне UB прибрало перевірку — і локальний користувач став ядром",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "exploit-chain.svg"), W, H, *p,
           title="Від зниклої перевірки до захоплення ядра")


# ── ub-birth: як народилося поняття — від C89 до «носових демонів» ─────────────
# Вставка hist-nasal-demons: два усталені факти на осі часу + суть повороту.
def fig_ub_birth():
    W, H = 780, 300
    p = []
    axis_y = 150
    p.append(line(70, axis_y, 710, axis_y, color=INK, sw=2))
    for x in (70, 710):
        p.append(line(x, axis_y - 6, x, axis_y + 6, color=INK, sw=2))

    # ── віха 1: C89 (грудень 1989) ──
    x1 = 230
    p.append(rect(x1 - 13, axis_y - 13, 26, 26, fill="#fdf6e9", stroke=GOLD, sw=2, rx=6))
    p.append(text(x1, axis_y + 5, "§", size=15, color=GOLD, bold=True))
    p.append(text(x1, axis_y - 32, "1989", size=13, color=GOLD, bold=True))
    p.append(text(x1, axis_y - 62, "ANSI C (C89)", size=10.5, color=INK, bold=True))
    p.append(text(x1, axis_y - 46, "стандарт ділить «не диктовано»", size=9, color=MUTED))
    for i, ln in enumerate(["impl-defined — обери й задокументуй",
                            "unspecified — обери, та мовчи",
                            "undefined — «жодних вимог»"]):
        p.append(text(x1, axis_y + 36 + i * 18, ln, size=9.5,
                      color=(POS if i == 2 else INK), bold=(i == 2)))

    # ── віха 2: Woods, 25.02.1992 ──
    x2 = 545
    p.append(rect(x2 - 13, axis_y - 13, 26, 26, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(text(x2, axis_y + 5, "@", size=14, color=POS, bold=True))
    p.append(text(x2, axis_y - 32, "25.02.1992", size=13, color=POS, bold=True))
    p.append(text(x2, axis_y - 62, "Джон Ф. Вудс · comp.std.c", size=10.5, color=INK, bold=True))
    p.append(text(x2, axis_y - 46, "тема «Why is this legal?»", size=9, color=MUTED))
    for i, ln in enumerate(["UB може «випустити",
                            "демонів із вашого носа»",
                            "→ гасло «nasal demons»"]):
        p.append(text(x2, axis_y + 36 + i * 18, ln, size=9.5,
                      color=(POS if i == 2 else INK), bold=(i == 2)))

    p.append(text(W / 2, 34, "«не диктовано» стало точним поняттям — а тоді й фольклором",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, 286,
                  "формальне означення (ліворуч) породило метафору, що пояснює його силу (праворуч)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "ub-birth.svg"), W, H, *p,
           title="Народження поняття UB: від рядка стандарту C89 до «носових демонів»")


if __name__ == "__main__":
    fig_three_shades()
    fig_null_check()
    fig_overflow_loop()
    fig_poison()
    fig_asm_diff()
    fig_exploit_chain()
    fig_ub_birth()
    print("OK: figures written to", OUT)
