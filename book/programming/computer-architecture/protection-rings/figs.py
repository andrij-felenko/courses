# -*- coding: utf-8 -*-
"""Фігури для теми «Кільця захисту й рівні привілеїв»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def _box(cx, cy, s, **kw):
    """textbox із центром (cx,cy); повертає (frag, (left,right,top,bottom))."""
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag, (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2)


def fig_rings():
    W, H = 900, 660
    cx, cy = 300, 340
    rc, r0, r3 = 72, 152, 232
    F = []
    # смуги (спершу зовнішня, щоб внутрішні перекрили)
    F.append(circle(cx, cy, r3, fill="#eaf0fd", stroke=LINE, sw=1.6))
    F.append(circle(cx, cy, r0, fill="#fff2df", stroke=LINE, sw=1.6))
    F.append(circle(cx, cy, rc, fill="#fdecea", stroke=LINE, sw=1.6))
    # підписи смуг — на вертикальній осі над центром (розведені по y)
    F.append(text(cx, cy - 200, "Застосунки", size=18, bold=True))
    F.append(text(cx, cy - 178, "кільце 3", size=13, color=MUTED))
    F.append(text(cx, cy - 118, "Ядро ОС", size=18, bold=True))
    F.append(text(cx, cy - 96, "кільце 0", size=13, color=MUTED))
    F.append(text(cx, cy - 6, "Гіпервізор, залізо", size=15, bold=True))
    F.append(text(cx, cy + 16, "кільце −1", size=13, color=MUTED))
    # ворота — зелена стрілка по діагоналі в порожній правий-нижній сектор
    th = math.radians(35)
    ct, st = math.cos(th), math.sin(th)
    p_out = (cx + 192 * ct, cy + 192 * st)   # у смузі застосунків
    p_in = (cx + 112 * ct, cy + 112 * st)    # у смузі ядра
    F.append(arrow(p_out[0], p_out[1], p_in[0], p_in[1], color=FIELD, sw=3.2))
    # підпис воріт — назовні по тій самій діагоналі, з пунктирним поводком
    lc = (cx + 322 * ct, cy + 322 * st)
    gate, gw, gh = textbox(lc[0], lc[1], "єдиний законний вхід —\nпастка (system call)",
                           size=14, color=FIELD, stroke=FIELD, fill="#eafaf0")
    F.append(line(p_out[0], p_out[1], lc[0] - gw / 2 + 8, lc[1] - gh / 2 + 6,
                  color=FIELD, sw=1.2, dash="4 3"))
    F.append(gate)
    render(os.path.join(IMG, 'rings.svg'), W, H, *F,
           title="Рівні привілею як вкладені кільця")


def fig_gate():
    W, H = 960, 520
    F = []
    # ── A. Законний запит послуги ──────────────────────────────
    yA = 150
    F.append(text(56, 96, "A. Законний запит послуги", size=14, bold=True, anchor="start"))
    b1, e1 = _box(120, yA, "Застосунок\n(кільце 3)", size=14, bold=True)
    b2, e2 = _box(440, yA, ["CPU: підняти рівень 3→0", "і стрибнути на", "фіксовану адресу ядра"],
                  size=13, fill="#eafaf0", stroke=FIELD)
    b3, e3 = _box(780, yA, ["Ядро ОС (кільце 0):", "обробник виклику"], size=13)
    F += [b1, b2, b3]
    F.append(arrow(e1[1], yA, e2[0], yA, color=FIELD, sw=2.4))
    F.append(text((e1[1] + e2[0]) / 2, yA - 12, "system call", size=12, color=FIELD, bold=True))
    F.append(arrow(e2[1], yA, e3[0], yA, color=FIELD, sw=2.4))
    # повернення — пунктирна дуга під рядком A
    yr = 250
    F.append(line(780, e3[3], 780, yr, color=MUTED, sw=1.4, dash="5 3"))
    F.append(line(120, e1[3], 120, yr, color=MUTED, sw=1.4, dash="5 3"))
    F.append(arrow(780, yr, 120, yr, color=MUTED, sw=1.6))
    F.append(text(450, yr - 9, "повернення, рівень 0→3", size=12, color=MUTED))
    # розділювач
    F.append(line(40, 300, W - 40, 300, color="#d0d0d0", sw=1.2, dash="2 5"))
    # ── B. Спроба зробити напряму ──────────────────────────────
    yB = 388
    F.append(text(56, 340, "B. Спроба зробити напряму", size=14, bold=True, anchor="start"))
    c1, f1 = _box(120, yB, "Застосунок\n(кільце 3)", size=14, bold=True)
    c2, f2 = _box(440, yB, ["CPU: рівень ≠ 0?", "команду відхилено"],
                  size=13, fill="#fdecea", stroke=POS, color=POS, bold=True)
    c3, f3 = _box(780, yB, ["Ядро ОС:", "обробник помилки"], size=13)
    F += [c1, c2, c3]
    F.append(arrow(f1[1], yB, f2[0], yB, color=POS, sw=2.4))
    F.append(text((f1[1] + f2[0]) / 2, yB - 12, "hlt (привілейована)", size=12, color=POS, bold=True))
    F.append(arrow(f2[1], yB, f3[0], yB, color=POS, sw=2.4))
    F.append(text((f2[1] + f3[0]) / 2, yB - 12, "пастка-помилка", size=12, color=POS, bold=True))
    F.append(text(W / 2, 476,
                  "Привілейовану команду так і не виконано — керування перехоплено на перевірці рівня.",
                  size=13))
    render(os.path.join(IMG, 'gate.svg'), W, H, *F,
           title="Дві дороги до привілейованих дій")


def fig_trap_roundtrip():
    """Шлях однієї відмови: hlt → #GP → ядро → обробник → siglongjmp."""
    W, H = 1020, 560
    F = []
    yA, yB = 140, 350

    a1, e1 = _box(170, yA, ["Ваш код, кільце 3:", "hlt"], size=13, bold=True)
    a2, e2 = _box(510, yA, ["Процесор: рівень ≠ 0 —", "команду відхилено, #GP(13)"],
                  size=13, fill="#fdecea", stroke=POS, color=POS)
    a3, e3 = _box(860, yA, ["Апаратна пастка:", "вектор 13 у таблиці"], size=13)
    F += [a1, a2, a3]
    F.append(arrow(e1[1], yA, e2[0], yA, color=POS, sw=2.4))
    F.append(arrow(e2[1], yA, e3[0], yA, color=POS, sw=2.4))

    # вертикальний перехід у кільце 0
    F.append(arrow(860, e3[3], 860, yB - 40, color=POS, sw=2.4))
    F.append(text(845, 250, "рівень 3 → 0", size=12, color=POS, anchor="end"))

    b3, f3 = _box(860, yB, ["Ядро: обробник #GP", "→ SIGSEGV процесові"], size=13)
    b2, f2 = _box(510, yB, ["Ядро кладе кадр сигналу", "на стек користувача", "й вертає в кільце 3"], size=13)
    b1, f1 = _box(170, yB, ["on_trap(): запам'ятати", "сигнал → siglongjmp"], size=13, bold=True)
    F += [b1, b2, b3]
    F.append(arrow(f3[0], yB, f2[1], yB, color=MUTED, sw=2.2))
    F.append(arrow(f2[0], yB, f1[1], yB, color=MUTED, sw=2.2))

    # виноска про RIP — у вільній смузі між рядами
    nb, nbw, nbh = textbox(300, 242, ["RIP лишається НА команді hlt:", "просте return з обробника",
                                      "виконало б її знову — і знову"],
                           size=12, fill="#eafaf0", stroke=FIELD, color=FIELD)
    F.append(line(e2[0] + 14, e2[3], 340, 242 - nbh / 2, color=FIELD, sw=1.2, dash="4 3"))
    F.append(nb)

    F.append(text(W / 2, 502,
                  "Команду так і не виконано, програма живе далі — але дорога туди й назад "
                  "коштує кілька мікросекунд.", size=13))
    render(os.path.join(IMG, 'trap-roundtrip.svg'), W, H, *F,
           title="Шлях однієї відмови: від hlt до вашого обробника")


def fig_three_fates():
    """Одне й те саме #GP ядро може передати, підмінити або проковтнути."""
    W, H = 980, 460
    F = []
    F.append(fitbox(230, 60, 520, 54,
                    ["Процесор: привілейована команда в кільці 3", "→ #GP(13), команду не виконано"],
                    size=14, fill="#fdecea", stroke=POS, color=POS, bold=True))

    cols = [
        (170, "Передати далі",
         ["ядро шле процесові SIGSEGV —", "програма бачить відмову", "hlt · rdmsr · mov %cr0"]),
        (490, "Підмінити результат",
         ["ядро емулює команду й вертає", "правдоподібне число", "smsw · sgdt · sidt під UMIP"]),
        (810, "Проковтнути",
         ["ядро вважає команду за", "порожню, як nop", "cli · sti після iopl(3)"]),
    ]
    for cx, head, body in cols:
        F.append(arrow(490, 118, cx, 186, color=POS, sw=2.0))
        F.append(fitbox(cx - 140, 190, 280, 46, [head], size=15, bold=True,
                        fill="#eaf0fd", stroke=NEG, color=NEG))
        F.append(fitbox(cx - 140, 248, 280, 80, body, size=13))

    F.append(text(W / 2, 388,
                  "Апаратна відмова однакова завжди — різниться тільки те, що з нею робить ядро.",
                  size=13))
    render(os.path.join(IMG, 'three-fates.svg'), W, H, *F,
           title="Одне #GP — три різні долі")


def fig_multics_rings():
    """Мапа восьми апаратних кілець Honeywell 6180 (вставка hist-rings-multics)."""
    W, H = 980, 560
    F = []
    F.append(text(96, 72, "кільце", size=13, color=MUTED))
    F.append(text(180, 72, "хто там жив", size=13, color=MUTED, anchor="start"))
    F.append(text(880, 68, "менше влади", size=13, color=MUTED))
    F.append(arrow(880, 84, 880, 520, color=MUTED, sw=2))

    rows = [
        ("0", "Ядро (hardcore supervisor): уся влада над машиною", "#fdecea", POS),
        ("1", "Менеджери захищених об'єктів: поштові сегменти, TCP/IP", "#fff2df", LINE),
        ("2", "Резерв під спільні служби самої системи", "#fff2df", LINE),
        ("3", "Служби майданчика: пошта, менеджер БД, дошка Forum", "#fff2df", LINE),
        ("4", "Звичайний користувач — сюди потрапляв ваш власний код", "#eaf0fd", NEG),
        ("5", "Обмежені підсистеми, писані самими користувачами", "#f4f6f8", LINE),
        ("6", "Дуже обмежений код: до воріт ядра не дотягнеться", "#f4f6f8", LINE),
        ("7", "Те саме, ще жорсткіше", "#f4f6f8", LINE),
    ]
    y0, step, rh = 92, 58, 42
    for i, (num, desc, fill, stroke) in enumerate(rows):
        y = y0 + i * step
        F.append(fitbox(60, y - rh / 2, 72, rh, num, size=20, bold=True,
                        fill=fill, stroke=stroke, sw=1.8))
        F.append(fitbox(160, y - rh / 2, 640, rh, desc, size=15,
                        fill=fill, stroke=stroke, sw=1.4))
    render(os.path.join(IMG, 'multics-rings.svg'), W, H, *F,
           title="Вісім кілець Multics і їхні мешканці")


def fig_ring_count():
    """Як спадало число рівнів привілею (вставка hist-rings-multics)."""
    W, H = 1000, 430
    F = []
    F.append(arrow(70, 240, 950, 240, color=MUTED, sw=2))
    F.append(text(70, 228, "час", size=12, color=MUTED, anchor="start"))

    stations = [
        (140, "GE-645\n1967", "64", "у програмі", FILL, MUTED),
        (380, "Honeywell 6180\n1973", "8", "у залізі", "#fff2df", LINE),
        (620, "Intel 80286\n1982", "4", "у залізі", "#eaf0fd", NEG),
        (860, "Linux · Windows · macOS\nсьогодні", "2", "в ужитку в ОС", "#eafaf0", FIELD),
    ]
    for x, cap, n, sub, fill, stroke in stations:
        box, bw, bh = textbox(x, 105, cap, size=14, bold=True)
        F.append(line(x, 105 + bh / 2, x, 269, color=MUTED, sw=1.4, dash="4 3"))
        F.append(box)
        F.append(circle(x, 305, 36, fill=fill, stroke=stroke, sw=2.2))
        F.append(text(x, 316, n, size=30, bold=True, color=INK))
        F.append(text(x, 372, sub, size=13, color=MUTED))
    F.append(text(W / 2, 410,
                  "Кожне врізання — плата за біти в дескрипторах і швидкість перевірки.",
                  size=13))
    render(os.path.join(IMG, 'ring-count.svg'), W, H, *F,
           title="Скільки рівнів привілею — від Multics до сьогодні")


if __name__ == '__main__':
    fig_rings()
    fig_gate()
    fig_trap_roundtrip()
    fig_three_fates()
    fig_multics_rings()
    fig_ring_count()
    print("OK:", os.listdir(IMG))
