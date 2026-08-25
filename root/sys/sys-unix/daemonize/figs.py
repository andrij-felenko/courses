# -*- coding: utf-8 -*-
"""Фігури до теми «Демонізація: відхід у фон»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_ties_and_tools():
    """Які нитки ріже кожен прийом."""
    W, H = 1320, 540
    f = []

    lab_x, lab_w = 30, 440
    col_w = 168
    cols = ["&", "nohup … &", "disown", "setsid … &", "повний обряд"]
    head_y, head_h = 56, 46
    row_y, row_h = 102, 64

    rows = [
        ("оболонка не чекає\nна завершення",            [1, 1, 1, 1, 1]),
        ("немає керуючого\nтермінала",                  [0, 0, 0, 1, 1]),
        ("SIGHUP при обриві\nсеансу не вбиває",         [0, 1, 1, 1, 1]),
        ("процес поза деревом\nоболонки",               [0, 0, 0, 1, 1]),
        ("термінал не здобути\nвипадково згодом",       [0, 0, 0, 0, 1]),
        ("успадкований стан очищено\n(fd, cwd, umask, сигнали)", [0, 0, 0, 0, 1]),
    ]

    # шапка
    f.append(rect(lab_x, head_y, lab_w, head_h, fill=BG, stroke=MUTED, sw=1))
    f.append(text(lab_x + lab_w / 2, head_y + head_h / 2 + 5,
                  "що саме має бути знято", size=14, bold=True, color=MUTED))
    for i, c in enumerate(cols):
        x = lab_x + lab_w + i * col_w
        last = (i == len(cols) - 1)
        f.append(rect(x, head_y, col_w, head_h,
                      fill="#eef3fb" if last else BG, stroke=MUTED, sw=1))
        f.append(text(x + col_w / 2, head_y + head_h / 2 + 5, c,
                      size=14, bold=True, color=NEG if last else INK))

    # рядки
    for r, (label, marks) in enumerate(rows):
        y = row_y + r * row_h
        f.append(fitbox(lab_x, y, lab_w, row_h, label,
                        size=13, fill=BG, stroke=MUTED, sw=1, rx=0))
        for i, m in enumerate(marks):
            x = lab_x + lab_w + i * col_w
            last = (i == len(cols) - 1)
            f.append(rect(x, y, col_w, row_h,
                          fill="#f7faff" if last else BG, stroke=MUTED, sw=1, rx=0))
            f.append(text(x + col_w / 2, y + row_h / 2 + 8,
                          "✓" if m else "✕", size=22, bold=True,
                          color=FIELD if m else POS))

    f.append(text(W / 2, H - 22,
                  "✓ — нитку перерізано, ✕ — лишилася; кожен короткий прийом розв'язує рівно одну задачу",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'ties-and-tools.svg'), W, H, *f,
           title="Що тримає програму за термінал і хто що відпускає")


def _fd_rows(f, x0, title, pairs, note, note_color, note_fill):
    """Одна панель фігури про дескриптори."""
    f.append(rect(x0, 56, 560, 350, fill=BG, stroke=MUTED, sw=1, rx=10))
    f.append(text(x0 + 280, 90, title, size=14, bold=True))
    ys = [150, 215, 280]
    for (left, right), y in zip(pairs, ys):
        b, wl, _ = textbox(x0 + 110, y, left, size=13, min_w=110)
        f.append(b)
        b, wr, _ = textbox(x0 + 390, y, right, size=13, fill=BG)
        f.append(b)
        f.append(arrow(x0 + 110 + wl / 2 + 8, y, x0 + 390 - wr / 2 - 8, y))
    b, _, _ = textbox(x0 + 280, 350, note, size=13,
                      fill=note_fill, stroke=note_color, color=note_color)
    f.append(b)


def fig_fd_hole():
    """Дірка на місці стандартних потоків."""
    W, H = 1200, 470
    f = []
    _fd_rows(f, 30, "0, 1, 2 закрито й лишено вільними",
             [("fd 0", "data.db"),
              ("fd 1", "сокет клієнта"),
              ("fd 2", "config.yaml")],
             "perror() пише у fd 2 — тобто у config.yaml",
             POS, "#fdecea")
    _fd_rows(f, 610, "0, 1, 2 зайнято /dev/null",
             [("fd 0, 1, 2", "/dev/null"),
              ("fd 3", "data.db"),
              ("fd 4", "сокет клієнта")],
             "perror() пише у fd 2 — тобто в нікуди",
             FIELD, "#eaf7ef")
    f.append(text(W / 2, H - 22,
                  "open() завжди повертає найменший вільний номер — саме тому дірку треба заткнути",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'fd-hole.svg'), W, H, *f,
           title="Чому стандартні потоки не можна просто закрити")


def _lane(y, label, marks, x0=170, x1=1180, size=13):
    """Часова доріжка: пунктир малюється відрізками МІЖ рамками."""
    out = [text(40, y + 5, label, size=13, color=MUTED, anchor="start", bold=True)]
    spans = []
    for cx, s, kw in marks:
        b, w, _ = textbox(cx, y, s, size=size, **kw)
        out.append(b)
        spans.append((cx - w / 2 - 6, cx + w / 2 + 6))
    spans.sort()
    cur = x0
    for a, b_ in spans:
        if a > cur:
            out.append(line(cur, y, a, y, color=MUTED, sw=1.2, dash="4 4"))
        cur = max(cur, b_)
    if cur < x1:
        out.append(line(cur, y, x1, y, color=MUTED, sw=1.2, dash="4 4"))
    return out


def fig_readiness_pipe():
    """Труба готовності між пускачем і демоном."""
    W, H = 1260, 430
    f = []
    f.extend(_lane(130, "пускач", [
        (250, "pipe()", {}),
        (410, "fork()", {}),
        (660, "read(труба)\nблокує", {}),
        (1090, "_exit(0 або 1)", dict(stroke=NEG, color=NEG)),
    ]))
    f.extend(_lane(320, "демон", [
        (410, "setsid()\nдруге fork()", {}),
        (700, "відкрив порт,\nпрочитав конфіг", {}),
        (960, "write(труба, «R»)", dict(stroke=FIELD, color=FIELD)),
    ]))

    # сповіщення про готовність: знизу вгору, повз усі написи
    f.append(line(960, 288, 960, 225, color=FIELD, sw=1.6))
    f.append(line(960, 225, 660, 225, color=FIELD, sw=1.6))
    f.append(arrow(660, 225, 660, 168, color=FIELD))
    f.append(text(975, 212, "готовність", size=12, color=FIELD, anchor="start"))

    f.append(text(W / 2, H - 22,
                  "демон помер до готовності → кінець запису зник → read() повертає 0 байтів, а не чекає вічно",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'readiness-pipe.svg'), W, H, *f,
           title="Труба готовності: єдиний зв'язок, що переживає обидва розділення")


def fig_who_prepares():
    """Хто готує контекст служби."""
    W, H = 1240, 620
    f = []
    panels = [
        (30, "Демон готує контекст сам", FILL, LINE,
         ["fork() — вийти з дерева оболонки",
          "setsid() — позбутися термінала",
          "fork() — не здобути його знову",
          "chdir(\"/\") і явна umask()",
          "закрити fd, зайняти 0–2 через /dev/null",
          "скинути диспозиції й маску сигналів"],
         "код виходу втрачено — готовність доводиться\nпередавати саморобною трубою, номер — файлом",
         POS, "#fdecea"),
        (630, "Менеджер служб дає контекст", "#eef3fb", NEG,
         ["без термінала, власний сеанс",
          "визначені cwd, umask, ліміти, права",
          "stdout і stderr — одразу в журнал",
          "власна cgroup, з якої не вийти",
          "сокети можуть бути відкриті наперед",
          "готовність — sd_notify(READY=1)"],
         "програма лишається на передньому плані:\nменеджер бачить її код виходу й керує нею",
         FIELD, "#eaf7ef"),
    ]
    for x0, title, fill, stroke, items, note, ncol, nfill in panels:
        f.append(rect(x0, 56, 580, 452, fill=BG, stroke=MUTED, sw=1, rx=10))
        f.append(text(x0 + 290, 92, title, size=15, bold=True, color=stroke))
        for i, s in enumerate(items):
            f.append(fitbox(x0 + 30, 116 + i * 62, 520, 48, s,
                            size=13, fill=fill, stroke=stroke, sw=1.4))
        b, _, _ = textbox(x0 + 290, 552, note, size=13,
                          fill=nfill, stroke=ncol, color=ncol)
        f.append(b)
    f.append(text(W / 2, H - 16,
                  "властивості ті самі — різниця в тому, хто їх забезпечує і чи лишається зворотний зв'язок",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'who-prepares.svg'), W, H, *f,
           title="Два способи дістати чистий контекст")


if __name__ == '__main__':
    fig_ties_and_tools()
    fig_fd_hole()
    fig_readiness_pipe()
    fig_who_prepares()
    print("готово:", OUT)
