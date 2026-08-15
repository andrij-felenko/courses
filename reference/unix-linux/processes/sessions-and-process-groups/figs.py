# -*- coding: utf-8 -*-
"""Фігури до теми «Сеанси, групи процесів і керівний термінал»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

HOT = "#fdecea"     # заливка під червоне
COOL = "#eef3fb"    # заливка під синє
GOOD = "#eaf7ef"    # заливка під зелене


def fig_session_map():
    """Сеанс, його групи й покажчик переднього плану."""
    W, H = 1280, 620
    f = []

    # ── сеанс ───────────────────────────────────────────────────────────────
    sx, sy, sw_, sh = 400, 70, 840, 490
    f.append(rect(sx, sy, sw_, sh, fill="#fbfcfe", stroke=NEG, sw=2, rx=14))
    f.append(text(sx + sw_ / 2, sy + 34, "сеанс SID = 901", size=16, bold=True, color=NEG))

    # ── група оболонки ──────────────────────────────────────────────────────
    gx, gw = sx + 40, 360
    f.append(rect(gx, 130, gw, 116, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    f.append(text(gx + gw / 2, 158, "група PGID = 901", size=14, bold=True, color=MUTED))
    f.append(fitbox(gx + 24, 176, gw - 48, 52,
                    "bash · PID 901\nлідер сеансу й лідер групи",
                    size=13, fill=FILL, stroke=LINE))

    # ── група переднього плану ──────────────────────────────────────────────
    fx, fw = sx + 40, 760
    f.append(rect(fx, 286, fw, 128, fill=GOOD, stroke=FIELD, sw=2, rx=10))
    f.append(text(fx + fw / 2, 314, "група PGID = 940 — передній план",
                  size=14, bold=True, color=FIELD))
    for i, s in enumerate(["find · 940\nлідер групи", "grep · 941", "less · 942"]):
        f.append(fitbox(fx + 30 + i * 240, 332, 200, 62, s, size=13,
                        fill=BG, stroke=FIELD))

    # ── фонова група ────────────────────────────────────────────────────────
    bx, bw = sx + 40, 360
    f.append(rect(bx, 452, bw, 90, fill=BG, stroke=MUTED, sw=1.5, rx=10))
    f.append(text(bx + bw / 2, 480, "група PGID = 950 — фон", size=14, bold=True, color=MUTED))
    f.append(fitbox(bx + 24, 492, bw - 48, 36, "make · 950", size=13,
                    fill=FILL, stroke=LINE))

    # ── термінал ────────────────────────────────────────────────────────────
    f.append(rect(60, 236, 250, 150, fill=COOL, stroke=NEG, sw=2, rx=12))
    f.append(mtext(185, 282, ["керівний термінал", "/dev/pts/3"],
                   size=14, bold=True, color=NEG))
    f.append(text(185, 340, "TPGID = 940", size=14, color=NEG))

    # звʼязок «термінал ↔ сеанс»
    f.append(line(310, 268, 356, 268, color=NEG, sw=2))
    f.append(line(356, 268, 356, 110, color=NEG, sw=2))
    f.append(arrow(356, 110, sx - 2, 110, color=NEG))
    f.append(text(316, 96, "приписаний до сеансу цілком",
                  size=13, color=NEG, anchor="start"))

    # покажчик переднього плану
    f.append(arrow(310, 352, fx - 4, 352, color=FIELD))
    f.append(text(322, 336, "покажчик переднього плану",
                  size=13, color=FIELD, anchor="start"))

    f.append(text(W / 2, H - 24,
                  "сигнали від клавіатури йдуть за покажчиком — тобто рівно одній групі, а не всьому сеансові",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'session-map.svg'), W, H, *f,
           title="Сеанс, групи процесів і покажчик переднього плану")


def _reach_panel(f, x0, title, tcol, rows, note, ncol, nfill):
    """Одна панель фігури про адресатів: три рядки сеансу й позначка отримувача."""
    PW = 400
    f.append(rect(x0, 66, PW, 372, fill=BG, stroke=MUTED, sw=1.5, rx=12))
    f.append(fitbox(x0 + 20, 88, PW - 40, 52, title, size=14, bold=True,
                    fill=nfill, stroke=tcol, color=tcol))
    for i, (label, hit) in enumerate(rows):
        y = 164 + i * 76
        f.append(fitbox(x0 + 20, y, PW - 40, 58, label, size=13,
                        fill=nfill if hit else FILL,
                        stroke=ncol if hit else MUTED,
                        sw=2 if hit else 1.2,
                        color=ncol if hit else INK))
    f.append(fitbox(x0 + 20, 396, PW - 40, 30, note, size=12,
                    fill=BG, stroke=BG, color=MUTED))


def fig_signal_reach():
    """Три події — три різні адресати."""
    W, H = 1320, 500
    f = []
    rows_a = [("лідер сеансу (оболонка)", False),
              ("група переднього плану", True),
              ("фонові групи", False)]
    rows_b = [("лідер сеансу (оболонка)", True),
              ("група переднього плану", False),
              ("фонові групи", False)]
    rows_c = [("лідер сеансу — уже мертвий", False),
              ("група переднього плану", True),
              ("фонові групи", False)]

    _reach_panel(f, 30, "Ctrl+C з клавіатури\n→ SIGINT", FIELD, rows_a,
                 "адреса — покажчик переднього плану", FIELD, GOOD)
    _reach_panel(f, 460, "термінал зник (обрив звʼязку)\n→ SIGHUP + SIGCONT", NEG, rows_b,
                 "керівний термінал прибрано всім у сеансі", NEG, COOL)
    _reach_panel(f, 890, "керівний процес завершився\n→ SIGHUP", POS, rows_c,
                 "термінал відʼєднано від сеансу", POS, HOT)

    f.append(text(W / 2, H - 26,
                  "виділено тих, кому ядро надсилає сигнал; решту сповіщає вже оболонка — і лише за домовленістю",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'signal-reach.svg'), W, H, *f,
           title="Кому саме адресована кожна з трьох подій")


def _timeline(y, label, marks, x0=250, x1=1230):
    """Часова доріжка: пунктир малюється відрізками МІЖ рамками."""
    out = [text(40, y + 5, label, size=13, color=MUTED, anchor="start", bold=True)]
    spans = []
    for cx, s, kw in marks:
        b, w, _ = textbox(cx, y, s, size=12, **kw)
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


def fig_setpgid_race():
    """Чому setpgid викликають з обох боків."""
    W, H = 1300, 560
    f = []

    f.append(text(40, 48, "якщо групу переставляє ТІЛЬКИ батько",
                  size=15, bold=True, color=POS, anchor="start"))
    f.extend(_timeline(112, "оболонка", [
        (330, "fork()", {}),
        (940, "setpgid(pid, pid)\nзапізно", dict(stroke=POS, color=POS, fill=HOT)),
    ]))
    f.extend(_timeline(206, "дитина", [
        (470, "execvp()", {}),
        (740, "читає термінал,\nще в групі оболонки", dict(stroke=POS, color=POS, fill=HOT)),
    ]))
    f.append(text(40, 268, "наслідок: термінальні сигнали дістаються дитині разом з оболонкою",
                  size=13, color=POS, anchor="start"))

    f.append(text(40, 344, "якщо групу переставляє ТІЛЬКИ дитина",
                  size=15, bold=True, color=POS, anchor="start"))
    f.extend(_timeline(408, "оболонка", [
        (330, "fork()", {}),
        (560, "tcsetpgrp(fd, pid)\nEPERM", dict(stroke=POS, color=POS, fill=HOT)),
    ]))
    f.extend(_timeline(502, "дитина", [
        (900, "setpgid(0, 0)\nгрупа зʼявилася аж тепер", dict(stroke=POS, color=POS, fill=HOT)),
    ]))
    f.append(text(40, 546, "наслідок: передати термінал нема кому — групи з таким номером ще не існує",
                  size=13, color=POS, anchor="start"))

    render(os.path.join(OUT, 'setpgid-race.svg'), W, H, *f,
           title="Щілина між fork і exec: чому setpgid роблять двічі")


def fig_flat_vs_session():
    """Чому самих груп було мало: плоский простір номерів проти сеансу-огорожі."""
    W, H = 1320, 580
    f = []

    # ── ЛІВА панель: 4.1BSD ────────────────────────────────────────────────
    f.append(text(340, 74, "4.1BSD, 1981: сама лише група", size=16, bold=True, color=POS))

    f.append(fitbox(80, 106, 230, 56, "вхід 1\nтермінал tty00", size=13,
                    fill=COOL, stroke=NEG))
    f.append(fitbox(370, 106, 230, 56, "вхід 2\nтермінал tty01", size=13,
                    fill=COOL, stroke=NEG))

    f.append(rect(80, 214, 520, 168, fill="#fbfcfe", stroke=MUTED, sw=2, rx=12))
    f.append(text(340, 242, "один плоский простір номерів груп", size=13, color=MUTED))

    for i, s in enumerate(["група 214", "група 377", "група 402"]):
        f.append(fitbox(100 + i * 168, 274, 148, 54, s, size=13, fill=BG, stroke=LINE))

    f.append(arrow(195, 162, 174, 274, color=NEG))
    f.append(arrow(485, 162, 510, 274, color=NEG))

    f.append(arrow(174, 356, 500, 356, color=POS, sw=2.2))
    f.append(text(80, 424, "setpgrp(0, 402) з процесу першого входу", size=13,
                  color=POS, anchor="start"))
    f.append(text(80, 448, "вписує його в чужу групу — і спрацьовує", size=13,
                  color=POS, anchor="start"))

    # ── роздільник ──────────────────────────────────────────────────────────
    f.append(line(640, 96, 640, 470, color=MUTED, sw=1.2, dash="6,6"))

    # ── ПРАВА панель: POSIX.1-1988 ─────────────────────────────────────────
    f.append(text(980, 74, "POSIX.1-1988: сеанс як огорожа", size=16, bold=True, color=FIELD))

    f.append(fitbox(690, 106, 250, 56, "вхід 1\nтермінал tty00", size=13,
                    fill=COOL, stroke=NEG))
    f.append(fitbox(1010, 106, 250, 56, "вхід 2\nтермінал tty01", size=13,
                    fill=COOL, stroke=NEG))

    f.append(rect(690, 214, 250, 168, fill=GOOD, stroke=FIELD, sw=2, rx=12))
    f.append(text(815, 242, "сеанс 214", size=13, bold=True, color=FIELD))
    f.append(fitbox(712, 262, 206, 48, "група 214", size=13, fill=BG, stroke=LINE))
    f.append(fitbox(712, 320, 206, 48, "група 377", size=13, fill=BG, stroke=LINE))

    f.append(rect(1010, 214, 250, 168, fill=GOOD, stroke=FIELD, sw=2, rx=12))
    f.append(text(1135, 242, "сеанс 402", size=13, bold=True, color=FIELD))
    f.append(fitbox(1032, 262, 206, 48, "група 402", size=13, fill=BG, stroke=LINE))

    f.append(arrow(815, 162, 815, 214, color=NEG))
    f.append(arrow(1135, 162, 1135, 214, color=NEG))

    f.append(line(944, 298, 1006, 298, color=POS, sw=2.2))
    f.append(text(975, 274, "✕", size=20, bold=True, color=POS))
    f.append(text(690, 424, "той самий виклик упирається в межу сеансу:", size=13,
                  color=FIELD, anchor="start"))
    f.append(text(690, 448, "setpgid дозволений лише всередині свого сеансу", size=13,
                  color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'flat-vs-session.svg'), W, H, *f,
           title="Що додав сеанс до моделі, зібраної на самих групах")


def fig_terminal_handover():
    """Хто тримає термінал упродовж життя одного завдання."""
    W, H = 1360, 520
    f = []

    f.append(text(40, 62, "покажчик переднього плану термінала",
                  size=13, bold=True, color=MUTED, anchor="start"))

    BY, BH = 92, 48
    segs = [
        (260, 470, "оболонка · 901", COOL, NEG),
        (470, 720, "завдання · 940", GOOD, FIELD),
        (720, 950, "оболонка · 901", COOL, NEG),
        (950, 1180, "завдання · 940", GOOD, FIELD),
        (1180, 1320, "оболонка", COOL, NEG),
    ]
    for a, b, s, fl, col in segs:
        f.append(fitbox(a + 3, BY, b - a - 6, BH, s, size=13,
                        fill=fl, stroke=col, color=col, bold=True))

    notes = [
        (470, "tcsetpgrp(940)"),
        (720, "tcsetpgrp(901)\ntcsetattr(режим оболонки)"),
        (950, "fg: tcsetattr(режим завдання)\ntcsetpgrp(940) · kill(-940, SIGCONT)"),
        (1180, "tcsetpgrp(901)"),
    ]
    for cx, s in notes:
        f.append(line(cx, BY + BH, cx, 176, color=MUTED, sw=1.2, dash="4 4"))
        b, _w, _h = textbox(cx, 208, s, size=11, fill=BG, stroke=MUTED, color=INK)
        f.append(b)

    f.append(text(40, 305, "оболонка", size=13, bold=True, color=MUTED, anchor="start"))
    for cx, s in [(365, "промпт"),
                  (595, "waitpid(-940, WUNTRACED)\nспить"),
                  (835, "промпт · «[1]+ Зупинено»"),
                  (1065, "waitpid — спить"),
                  (1250, "промпт")]:
        b, _w, _h = textbox(cx, 300, s, size=11, fill=FILL, stroke=MUTED, color=INK)
        f.append(b)

    f.append(text(40, 397, "завдання", size=13, bold=True, color=MUTED, anchor="start"))
    for cx, s, fl, col in [(595, "виконується", GOOD, FIELD),
                           (835, "зупинене · стан T", HOT, POS),
                           (1065, "виконується", GOOD, FIELD),
                           (1250, "вийшло", BG, MUTED)]:
        b, _w, _h = textbox(cx, 392, s, size=11, fill=fl, stroke=col, color=col)
        f.append(b)

    f.append(line(720, 410, 720, 438, color=POS, sw=1.2, dash="4 4"))
    b, _w, _h = textbox(720, 458, "Ctrl+Z → SIGTSTP групі 940",
                        size=11, fill=HOT, stroke=POS, color=POS)
    f.append(b)

    f.append(text(40, 502,
                  "оболонка тримає термінал лише поки друкує промпт — тож забирає його щоразу З ФОНУ",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'terminal-handover.svg'), W, H, *f,
           title="Термінал переходить із рук у руки чотири рази за життя одного завдання")


if __name__ == '__main__':
    fig_session_map()
    fig_signal_reach()
    fig_setpgid_race()
    fig_flat_vs_session()
    fig_terminal_handover()
    print("готово:", OUT)
