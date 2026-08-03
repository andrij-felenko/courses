# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT = "#fbfcff"


# ── 1. Кілька жеребів визначають усю карту ──────────────────────────────────
def fig_draws():
    W, H = 1140, 620
    p = []

    # заголовки колонок
    p.append(fitbox(40, 56, 300, 44, "жереб ядра в execve", size=13,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(430, 56, 670, 44, "що цей один жереб пересуває", size=13,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    rows = [
        ("база відображень\nmmap_base", NEG,
         "libc.so.6 · ld-linux.so · усі інші бібліотеки ·\n"
         "великі шматки купи, узяті окремим mmap"),
        ("вершина стека", PURPLE,
         "стек головного потоку разом з усіма\nкадрами, аргументами й оточенням"),
        ("база виконуваного\nфайлу (лише ET_DYN)", FIELD,
         "код і дані самої програми —\nтільки якщо її зібрано з -pie"),
        ("початок купи\nbrk", "#b8860b",
         "класична купа, що росте зсувом межі;\nрухається лише за randomize_va_space=2"),
        ("місце vDSO", MUTED,
         "сторінка коду від ядра; адресу процес\nдістає з допоміжного вектора"),
    ]

    y = 122
    RH = 74
    for name, accent, what in rows:
        p.append(fitbox(40, y, 300, RH, name, size=12, fill=SOFT,
                        stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(arrow(350, y + RH / 2, 418, y + RH / 2, color=accent, sw=1.7))
        p.append(fitbox(430, y, 670, RH, what, size=12, fill="#ffffff",
                        stroke=MUTED, sw=1.3, color=INK))
        y += RH + 12

    p.append(fitbox(40, y + 10, 1060, 56,
                    "усередині кожної ділянки відстані зафіксовані при лінкуванні — "
                    "рухається тільки база, вміст їде за нею цілим блоком",
                    size=13, fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, H - 16,
                  "п'ять випадкових чисел визначають адресу кожного байта в процесі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "draws.svg"), W, H, *p,
           title="Ядро тягне жереб не на об'єкт, а на базу відображення")


# ── 2. Біти ентропії по ділянках ────────────────────────────────────────────
def fig_entropy_bits():
    W = 1160
    RH, GAP = 62, 10
    top = 132
    p = []

    cols = [(40, 300, "що рухається"),
            (356, 250, "x86-64\n(64-бітна задача)"),
            (622, 240, "32-бітна задача\n(compat)"),
            (878, 242, "чим регулюється")]
    for x, w, head in cols:
        p.append(fitbox(x, 52, w, 62, head, size=12, fill="#eceff2",
                        stroke=INK, sw=1.5, color=INK, bold=True))

    rows = [
        ("база відображень", "28 бітів\n2.7 · 10⁸ місць", "8 бітів\n256 місць",
         "vm.mmap_rnd_bits\nvm.mmap_rnd_compat_bits"),
        ("вершина стека", "22 біти", "11 бітів", "зашито в архітектурі"),
        ("початок купи (brk)", "18 бітів\n(до 2024 — 13)", "13 бітів",
         "kernel.randomize_va_space = 2"),
        ("образ ядра (KASLR)", "9 бітів\n512 місць", "—",
         "CONFIG_RANDOMIZE_BASE\nпараметр nokaslr"),
    ]

    y = top
    for what, wide, narrow, knob in rows:
        p.append(fitbox(cols[0][0], y, cols[0][1], RH, what, size=13, fill=SOFT,
                        stroke=INK, sw=1.5, color=INK, bold=True))
        p.append(fitbox(cols[1][0], y, cols[1][1], RH, wide, size=12,
                        fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))
        p.append(fitbox(cols[2][0], y, cols[2][1], RH, narrow, size=12,
                        fill="#fdecea", stroke=POS, sw=1.6, color=INK))
        p.append(fitbox(cols[3][0], y, cols[3][1], RH, knob, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))
        y += RH + GAP

    y += 14
    p.append(fitbox(40, y, 540, 92,
                    "перебір 8 бітів проти сервера,\n"
                    "що піднімає робітника після падіння:\n"
                    "128 спроб · 0.5 с ≈ хвилина",
                    size=13, fill="#fdecea", stroke=POS, sw=2.0, color=INK, bold=True))
    p.append(fitbox(620, y, 500, 92,
                    "перебір 28 бітів у тих самих умовах:\n"
                    "1.34 · 10⁸ спроб · 0.5 с ≈ 2 роки",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=2.0, color=INK, bold=True))

    H = y + 92 + 46
    p.append(text(W / 2, H - 16,
                  "нижні 12 бітів адреси завжди нулі: база кратна сторінці, тому випадковим може бути лише те, що вище",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "entropy-bits.svg"), W, H, *p,
           title="Скільки бітів випадковості дістає кожна база")


# ── 3. Витік однієї адреси розкриває цілу ділянку ───────────────────────────
def fig_leak_collapse():
    W, H = 1180, 560
    p = []

    # ── ліва панель: арифметика витоку
    p.append(fitbox(40, 56, 520, 44, "один покажчик назовні — і бази більше немає",
                    size=13, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True))

    steps = [
        ("витекла адреса printf у процесі", "0x7f3c2a1b4e40", POS),
        ("зсув printf у файлі libc.so.6\n(читається з дистрибутива)", "0x00061e40", MUTED),
        ("база libc = різниця", "0x7f3c2a153000", FIELD),
    ]
    y = 120
    for label, value, accent in steps:
        p.append(fitbox(40, y, 300, 70, label, size=11, fill=SOFT,
                        stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(356, y, 204, 70, value, size=13, fill="#ffffff",
                        stroke=accent, sw=1.7, color=accent, bold=True))
        y += 82

    p.append(fitbox(40, y + 6, 520, 64,
                    "далі відома кожна адреса в цій бібліотеці —\n"
                    "стан «нападник знає половину» не існує",
                    size=12, fill="#eceff2", stroke=INK, sw=1.7, color=INK, bold=True))

    # роздільник
    p.append(line(600, 56, 600, 500, color="#d7dbe0", sw=1.4, dash="6 6"))

    # ── права панель: залежні й незалежні бази
    p.append(fitbox(640, 56, 500, 44, "чи розкриває витік ще й сусіда",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))

    p.append(fitbox(640, 120, 500, 156,
                    "до ядра 4.1: один жереб на дві бази\n\n"
                    "виконуваний файл лежав упритул до області\n"
                    "відображень, відстань між ними стала —\n"
                    "витік адреси програми давав базу libc",
                    size=12, fill="#fdecea", stroke=POS, sw=1.9, color=INK))

    p.append(fitbox(640, 296, 500, 156,
                    "з ядра 4.1: два незалежні жереби\n\n"
                    "переміщуваний виконуваний файл дістав\n"
                    "власне випадкове місце — витік із нього\n"
                    "нічого не каже про бібліотеки",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.9, color=INK))

    p.append(text(W / 2, H - 16,
                  "бібліотеки між собою досі один блок: завантажувач кладе їх поспіль, тому їхні взаємні відстані сталі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "leak-collapse.svg"), W, H, *p,
           title="Витік адреси коштує рівно стільки, скільки коштувала вся ентропія")


# ── 4. П'ять поверхів вимикачів ─────────────────────────────────────────────
def fig_switch_levels():
    W = 1180
    RH, GAP = 82, 12
    top = 128
    p = []

    cols = [(40, 250, "поверх"),
            (306, 330, "вимикач"),
            (652, 488, "що саме він вирішує")]
    for x, w, head in cols:
        p.append(fitbox(x, 54, w, 52, head, size=13, fill="#eceff2",
                        stroke=INK, sw=1.5, color=INK, bold=True))

    rows = [
        ("збірка програми", POS, "-pie  /  -no-pie",
         "чи має виконуваний файл право їздити взагалі;\nсисктлом це вже не виправити"),
        ("збірка ядра", PURPLE, "CONFIG_RANDOMIZE_BASE\nCONFIG_COMPAT_BRK",
         "чи є в ядрі код рандомізації образу\nй чи допускається давня розкладка купи"),
        ("завантаження", NEG, "nokaslr  у рядку ядра",
         "рандомізація образу ядра на цей запуск —\nвимикають заради налагодження ядра"),
        ("уся система", FIELD, "kernel.randomize_va_space\nvm.mmap_rnd_bits",
         "0 — нічого · 1 — відображення, стек, vDSO ·\n2 — плюс купа; і скільки бітів давати"),
        ("окремий процес", "#b8860b", "personality(ADDR_NO_RANDOMIZE)\nsetarch --addr-no-randomize",
         "вимкнення для цього процесу й усіх нащадків;\nсаме це робить gdb перед запуском"),
    ]

    y = top
    for level, accent, knob, what in rows:
        p.append(fitbox(cols[0][0], y, cols[0][1], RH, level, size=13, fill=SOFT,
                        stroke=accent, sw=1.9, color=accent, bold=True))
        p.append(fitbox(cols[1][0], y, cols[1][1], RH, knob, size=12,
                        fill="#ffffff", stroke=accent, sw=1.5, color=INK, bold=True))
        p.append(fitbox(cols[2][0], y, cols[2][1], RH, what, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
        y += RH + GAP

    p.append(fitbox(40, y + 12, 1100, 58,
                    "поверхи не рівноправні: нижній не відновлює того, що вимкнув верхній — "
                    "не-PIE бінарник лишиться на місці за будь-якого сисктла",
                    size=13, fill="#eceff2", stroke=INK, sw=1.9, color=INK, bold=True))

    H = y + 12 + 58 + 44
    p.append(text(W / 2, H - 16,
                  "розкладку обирають в execve — тому робітник, піднятий самим fork, успадковує чужий жереб замість власного",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "switch-levels.svg"), W, H, *p,
           title="П'ять поверхів, на яких рандомізацію вмикають і вимикають")


# ── 5. Хроніка: цифра йшла слідом за атакою ─────────────────────────────────
def fig_lineage():
    W = 1220
    RH, GAP = 66, 9
    top = 128
    p = []

    cols = [(40, 132, "рік"),
            (188, 470, "що сталося"),
            (674, 546, "що стало з бітами")]
    for x, w, head in cols:
        p.append(fitbox(x, 54, w, 52, head, size=13, fill="#eceff2",
                        stroke=INK, sw=1.5, color=INK, bold=True))

    rows = [
        ("1997", MUTED, "Форрест, Сомаяджі й Еклі показують,\nщо випадковий відступ ламає переповнення",
         "бітів ще ніхто не рахує — є сама ідея"),
        ("2001", NEG, "PaX публікує проєкт і латку;\nтермін ASLR з'являється тут",
         "на i386: 24 біти стек, 16 mmap, 16 образ"),
        ("2003", FIELD, "OpenBSD 3.4 · Exec Shield Інґо Молнара\nв Red Hat",
         "19 бітів стеку (крок 16 Б), 8 бітів бази mmap"),
        ("2004", POS, "Шахам зі співавторами перебирає\nApache за 216 секунд",
         "16 бітів на 32-бітній системі визнано\nнедостатніми — і це не полагодили, а переросли"),
        ("2007", "#b8860b", "Їржі Косіна рандомізує brk на i386 і x86_64",
         "32 МіБ = 13 бітів — цифра простоїть 17 років"),
        ("2014", POS, "Марко-Ґісберт і Ріполь описують offset2lib;\nу головну гілку входить KASLR",
         "витік із програми = база libc; образ ядра — 9 бітів"),
        ("2015", FIELD, "латка Кіса Кука розділяє жереби (4.1);\nCVE-2015-1593 виправлено в 3.19-rc3",
         "два незалежні жереби; стекові повернуто\nдва старші розряди"),
        ("2016", NEG, "Деніел Кешмен додає сисктли (4.5)",
         "vm.mmap_rnd_bits — типово 28 і 8"),
        ("2022→2024", POS, "вирівнювання на 2 МіБ (5.18) мовчки з'їдає біти;\nДженніфер Міллер описує ASLRn't",
         "база бібліотек: 28 → 19 бітів,\nі це не атака, а оптимізація"),
        ("2024", FIELD, "Кіс Кук піднімає рандомізацію brk на x86_64",
         "13 → 18 бітів, як уже було на arm64"),
    ]

    y = top
    for year, accent, what, bits in rows:
        p.append(fitbox(cols[0][0], y, cols[0][1], RH, year, size=14, fill=SOFT,
                        stroke=accent, sw=1.9, color=accent, bold=True))
        p.append(fitbox(cols[1][0], y, cols[1][1], RH, what, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(cols[2][0], y, cols[2][1], RH, bits, size=11,
                        fill="#ffffff", stroke=accent, sw=1.4, color=INK))
        y += RH + GAP

    p.append(fitbox(40, y + 14, 1140, 58,
                    "жодну з цих цифр не вивели з теорії — кожну поставили після того, "
                    "як хтось показав робочу атаку або втрату",
                    size=13, fill="#eceff2", stroke=INK, sw=1.9, color=INK, bold=True))

    H = y + 14 + 58 + 44
    p.append(text(W / 2, H - 16,
                  "рух не однобічний: біти додає безпека, а забирає швидкодія",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Хроніка ентропії: кожна цифра має дату й привід")


# ── 6. Мапа розрядів: що саме друкує вимірювач ──────────────────────────────
def fig_bitmap():
    NB = 48
    CW = 20                      # ширина клітинки одного розряду
    LX, LW = 36, 286             # колонка підписів
    GX = LX + LW + 24            # початок сітки розрядів
    W = GX + NB * CW + 34
    RH, GAP = 54, 9
    top = 132

    C_ZERO = "#dfe3e7"
    C_FIX = "#ffffff"
    C_MOVE = "#bfe9cd"
    C_SPILL = "#f6c8c1"

    p = []
    p.append(fitbox(LX, 42, LW, 54, "орієнтир і його жереб", size=12,
                    fill="#eceff2", stroke=INK, sw=1.5, color=INK, bold=True))
    p.append(fitbox(GX, 42, NB * CW, 54,
                    "номер двійкового розряду адреси", size=12,
                    fill="#eceff2", stroke=INK, sw=1.5, color=INK, bold=True))

    # підписи розрядів під шапкою
    for b in range(0, NB, 4):
        cx = GX + (NB - 1 - b) * CW + CW / 2
        p.append(text(cx, 118, str(b), size=11, color=MUTED))

    rows = [
        ("база libc.so.6", "жереб бази відображень:\n28 бітів",
         {"zero": (0, 11), "move": (12, 39), "spill": (40, 40)}),
        ("база програми, зібраної з -pie", "власний жереб від 4.1:\nтеж 28 бітів",
         {"zero": (0, 11), "move": (12, 39), "spill": (40, 41)}),
        ("покажчик на локальну змінну", "22 біти сторінками\nплюс 9 підсторінкових",
         {"zero": (0, 3), "move": (4, 33)}),
        ("межа brk у PIE-програмі", "свої 18 бітів тонуть\nу 28 бітах бази програми",
         {"zero": (0, 11), "move": (12, 39), "spill": (40, 41)}),
        ("база vDSO", "їде за стеком, а власного\nзсуву в ній лише ~9 бітів",
         {"zero": (0, 11), "move": (12, 33)}),
    ]

    y = top
    for label, note, zones in rows:
        p.append(fitbox(LX, y, LW, RH, label + "\n" + note, size=11, fill=SOFT,
                        stroke=MUTED, sw=1.3, color=INK))
        for b in range(NB):
            fill = C_FIX
            for kind, (lo, hi) in zones.items():
                if lo <= b <= hi:
                    fill = {"zero": C_ZERO, "move": C_MOVE, "spill": C_SPILL}[kind]
            x = GX + (NB - 1 - b) * CW
            p.append(rect(x, y + 8, CW - 2, RH - 16, fill=fill,
                          stroke="#b9c0c7", sw=0.8, rx=1))
        y += RH + GAP

    y += 12
    legend = [
        (C_ZERO, "завжди нуль — вирівнювання"),
        (C_FIX, "стале — цю частину адреси жереб не чіпає"),
        (C_MOVE, "рухоме — сюди й лягла випадковість"),
        (C_SPILL, "рухоме через перенесення — розряд ворушиться, а бітів не додає"),
    ]
    lx = LX
    for fill, cap in legend:
        wdt = 34 + text_width(cap, 11) + 18
        p.append(rect(lx, y, 24, 24, fill=fill, stroke="#b9c0c7", sw=1.0, rx=2))
        p.append(text(lx + 34, y + 16, cap, size=11, color=INK, anchor="start"))
        lx += wdt

    H = y + 24 + 44
    p.append(text(W / 2, H - 16,
                  "кількість рухомих розрядів — це стеля ентропії, а не сама ентропія: "
                  "перенесення від віднімання ворушить розряди понад полем жереба",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "bitmap.svg"), W, H, *p,
           title="Мапа розрядів: де в адресі сидить випадковість")


if __name__ == "__main__":
    fig_draws()
    fig_entropy_bits()
    fig_leak_collapse()
    fig_switch_levels()
    fig_lineage()
    fig_bitmap()
    print("OK: figures written to", OUT)
