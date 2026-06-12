# -*- coding: utf-8 -*-
"""
Фігури для ⚙️-вставки ch27-s6-a-queue-pattern.md
  Рис. 4.10.6a.1 — контраст двох топологій (спільні змінні vs. усе через черги)
  Рис. 4.10.6a.2 — передавання володіння великим буфером через вказівник

Чистий Python; вивід → ./img/
"""
import os
import sys

# Спільний kit — textbox/fitbox/render і т.д.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *  # noqa: F401, F403

# ─── локальна палітра (сумісна з figs.py цього розділу) ─────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
PURP  = "#7a4fb0"
LPURP = "#efe9f7"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

FONT = "Segoe UI, Arial, Helvetica, sans-serif"


# ─── примітиви (аналог figs.py, щоб не дублювати svgkit прямо) ──────────────

def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hdr(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGold" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GOLD}"/></marker>\n'
        f'</defs>\n'
    )


def _ftr():
    return "</svg>\n"


_MARKERS = {INK: "aInk", RED: "aRed", BLUE: "aBlue",
            GREEN: "aGreen", GREY: "aGrey", GOLD: "aGold"}


def _line(x1, y1, x2, y2, color=INK, w=1.8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def _arrow(x1, y1, x2, y2, color=INK, w=2.0):
    m = _MARKERS.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _darrow(x1, y1, x2, y2, color=INK, w=1.6):
    """Двонапрямлена стрілка (для гонок — підкреслити спільний доступ)."""
    m = _MARKERS.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" '
            f'marker-start="url(#{m})" marker-end="url(#{m})"/>\n')


def _rect(x, y, w, h, fill="#f4f6f8", stroke=INK, sw=1.6, rx=8):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def _text(x, y, s, size=14, color=INK, anchor="middle", bold=False, italic=False):
    w = ' font-weight="700"' if bold else ''
    it = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}"{w}{it}>{_esc(s)}</text>\n')


def _mtext(x, y, lines, size=14, color=INK, anchor="middle", bold=False):
    if isinstance(lines, str):
        lines = [l for l in lines.split("\n") if l or True]
    lh = size * 1.35
    w = ' font-weight="700"' if bold else ''
    out = (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
           f'fill="{color}" text-anchor="{anchor}"{w}>')
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out += f'<tspan x="{x:.1f}" dy="{dy:.1f}">{_esc(ln)}</tspan>'
    out += '</text>\n'
    return out


def _textw(s, size=14, bold=False):
    k = 0.62 if bold else 0.57
    return len(str(s)) * size * k


def _tbox(cx, cy, s, size=13, pad=9, fill="#f4f6f8", stroke=INK, sw=1.6,
          color=INK, bold=False, min_w=0, rx=8):
    """Рамка, що гарантовано вміщає напис (як textbox із svgkit)."""
    lines = s.split("\n") if isinstance(s, str) else list(s)
    tw = max(_textw(ln, size, bold) for ln in lines)
    w = max(min_w, tw + 2 * pad)
    h = len(lines) * size * 1.35 + 2 * pad
    x, y = cx - w / 2, cy - h / 2
    out = _rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx)
    ty = cy - (len(lines) - 1) * size * 1.35 / 2 + size * 0.38
    out += _mtext(cx, ty, lines, size=size, color=color, bold=bold)
    return out, w, h


def _queue_box(cx, cy, label, n_slots=3, col=BLUE):
    """Намалювати чергу як ряд клітинок з підписом."""
    sw, sh = 28, 24
    total_w = n_slots * sw + 2
    out = ""
    x0 = cx - total_w / 2
    out += _rect(x0 - 4, cy - sh / 2 - 4, total_w + 8, sh + 8,
                 fill=LBLUE if col == BLUE else LGRN, stroke=col, sw=1.8, rx=5)
    for i in range(n_slots):
        out += _rect(x0 + i * sw + 1, cy - sh / 2, sw - 2, sh,
                     fill="#ffffff", stroke=col, sw=1.0, rx=3)
    out += _text(cx, cy - sh / 2 - 12, label, size=11, color=col, bold=True)
    return out


def _save(name, body):
    body += _ftr()
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.6a.1 — «Наївна архітектура» зліва vs. «Усе через чергу» справа
# ═══════════════════════════════════════════════════════════════════════════════

def fig_everything_through_queue():
    W, H = 1000, 500
    s = _hdr(W, H)

    # ── заголовок ──────────────────────────────────────────────────────────────
    s += _text(W / 2, 32, "Дві топології: спільні змінні vs. «усе через чергу»",
               17, INK, "middle", bold=True)
    s += _text(W / 2, 54,
               "зліва — кожна стрілка доступу потенційна гонка; справа — задачі зв'язані лише чергами",
               10, GREY, "middle")

    # ── роздільник ────────────────────────────────────────────────────────────
    s += _line(W / 2, 68, W / 2, H - 20, FAINT, 1.6)
    s += _text(W / 4, 76, "Наївна архітектура", 13, RED, "middle", bold=True)
    s += _text(3 * W / 4, 76, "«Усе через чергу»", 13, GREEN, "middle", bold=True)

    # ══════════════════════════════
    #  ЛІВОРУЧ — наївна архітектура
    # ══════════════════════════════
    # Задачі
    left_tasks = [
        (90, 160, "taskSensor", BLUE),
        (90, 270, "taskButton", PURP),
        (90, 380, "taskControl", GOLD),
    ]
    # Спільні змінні (центр лівої половини)
    shared_cx = 250
    shared = [
        (shared_cx, 160, "volatile bool\nhasData", RED),
        (shared_cx, 270, "struct Cmd\ncommand", RED),
        (shared_cx, 380, "int mode", RED),
    ]

    for tx, ty, lab, col in left_tasks:
        tb, tw, th = _tbox(tx, ty, lab, size=11, fill=LBLUE if col == BLUE else
                           (LPURP if col == PURP else LAMB),
                           stroke=col, color=col, bold=True, min_w=100)
        s += tb

    for sx, sy, lab, col in shared:
        tb, tw, th = _tbox(sx, sy, lab, size=10, fill=LRED, stroke=RED,
                           color=RED, min_w=100)
        s += tb

    # Двонапрямлені стрілки-гонки між задачами та спільними змінними
    for (tx, ty, _, _), (sx, sy, _, _) in zip(left_tasks, shared):
        s += _darrow(tx + 55, ty, sx - 55, sy, RED, 1.6)

    # Хрестики-мітки + пояснення «гонка!»
    s += _rect(190, 420, 130, 40, LRED, RED, 1.4, 6)
    s += _text(255, 435, "потрібен м'ютекс", 9.5, RED, "middle", bold=True)
    s += _text(255, 451, "на кожну змінну!", 9.5, RED, "middle")

    # Мітка «гонка» у центрі лівої половини
    s += _text(shared_cx, 110, "← гонки →", 10.5, RED, "middle", bold=True)

    # ═════════════════════════════
    #  ПРАВОРУЧ — усе через черги
    # ═════════════════════════════
    ox = 530  # зміщення правої колонки

    # Задачі-вузли
    right_tasks = [
        (ox + 30,  160, "taskSensor",  BLUE),
        (ox + 30,  290, "taskButton",  PURP),
        (ox + 260, 220, "taskControl", GOLD),
        (ox + 430, 220, "taskActuator", GREEN),
    ]
    for tx, ty, lab, col in right_tasks:
        tb, tw, th = _tbox(tx, ty, lab, size=11,
                           fill=LBLUE if col == BLUE else
                           (LPURP if col == PURP else
                            (LAMB if col == GOLD else LGRN)),
                           stroke=col, color=col, bold=True, min_w=100)
        s += tb

    # Черга qEvents (fan-in від Sensor та Button у Control)
    qex, qey = ox + 155, 225
    s += _queue_box(qex, qey, "qEvents", n_slots=4, col=BLUE)

    # Черга qActuator (від Control до Actuator)
    qax, qay = ox + 345, 220
    s += _queue_box(qax, qay, "qActuator", n_slots=3, col=GREEN)

    # Стрілки producer→queue
    s += _arrow(ox + 30 + 55, 160, qex - 30, qey - 8, BLUE, 2.0)
    s += _arrow(ox + 30 + 55, 290, qex - 30, qey + 8, PURP, 2.0)

    # Стрілка queue→control
    s += _arrow(qex + 30, qey, ox + 260 - 55, 220, BLUE, 2.0)

    # Стрілка control→qActuator
    s += _arrow(ox + 260 + 55, 220, qax - 28, qay, GOLD, 2.0)

    # Стрілка qActuator→Actuator
    s += _arrow(qax + 28, qay, ox + 430 - 55, 220, GREEN, 2.0)

    # Підпис: жодної спільної змінної
    s += _rect(ox + 20, 360, 420, 38, LGRN, GREEN, 1.5, 8)
    s += _text(ox + 230, 374, "Жодної спільної змінної між задачами —", 10, GREEN, "middle", bold=True)
    s += _text(ox + 230, 390, "лише черги як єдині зв'язки.", 10, INK, "middle")

    # fan-in підпис
    s += _text(qex, qey + 40, "fan-in", 9, GREY, "middle")

    # ── нижня рамка-висновок ──────────────────────────────────────────────────
    s += _rect(30, H - 68, W - 60, 50, LAMB, GOLD, 1.5, 10)
    s += _text(W / 2, H - 50, "Share-nothing: замість спільного стану — передавання повідомлень.", 10.5, INK, "middle", bold=True)
    s += _text(W / 2, H - 32, "Немає спільного → немає гонки → не треба м'ютекса на дані; він лишається лише для нероздільного заліза.", 9.5, GREY, "middle")

    _save("fig-27-6a-1-everything-through-queue.svg", s)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.10.6a.2 — Передавання володіння великим буфером через вказівник
# ═══════════════════════════════════════════════════════════════════════════════

def fig_ownership_transfer():
    W, H = 960, 380
    s = _hdr(W, H)

    s += _text(W / 2, 32, "Передавання володіння буфером через чергу вказівником",
               17, INK, "middle", bold=True)
    s += _text(W / 2, 54,
               "виробник наповнив → send(ptr) → більше НЕ торкається; споживач вжив → повернув у пул",
               10, GREY, "middle")

    # ── вісь часу ─────────────────────────────────────────────────────────────
    ax_y = 120
    ox, ex = 60, 900
    s += _arrow(ox, ax_y, ex, ax_y, INK, 1.8)
    s += _text(ex + 6, ax_y + 4, "час →", 9.5, INK, "start")

    # ── Фаза 1: виробник «володіє» буфером ───────────────────────────────────
    p1x, p1y = ox + 40, ax_y - 70
    buf1x, buf1y = ox + 40, ax_y - 40
    # лінія виробника
    s += _rect(buf1x, buf1y, 160, 30, LGRN, GREEN, 2.0, 6)
    s += _text(buf1x + 80, buf1y + 19, "буфер (виробник)", 10, GREEN, "middle", bold=True)
    s += _text(buf1x + 80, ax_y - 82, "ВИРОБНИК", 10, GREEN, "middle", bold=True)
    s += _text(buf1x + 80, ax_y - 67, "заповнює", 8.5, GREY, "middle")
    # фігурна скоба «Виробник»
    s += _line(buf1x, ax_y + 8, buf1x, ax_y + 20, GREEN, 1.4)
    s += _line(buf1x + 160, ax_y + 8, buf1x + 160, ax_y + 20, GREEN, 1.4)
    s += _line(buf1x, ax_y + 20, buf1x + 160, ax_y + 20, GREEN, 1.4)
    s += _text(buf1x + 80, ax_y + 34, "володіє", 9, GREEN, "middle")

    # ── Подія: send(ptr) ─────────────────────────────────────────────────────
    send_x = buf1x + 180
    s += _line(send_x, ax_y - 80, send_x, ax_y + 6, GOLD, 2.2)
    s += _text(send_x + 4, ax_y - 84, "send(ptr)", 10.5, GOLD, "start", bold=True)
    # Чергова «коробка»
    q_box_x, q_box_y = send_x + 8, ax_y - 52
    tb, tw, th = _tbox(q_box_x + 50, q_box_y, "qActuator\n[ptr]", size=9,
                       fill=LAMB, stroke=GOLD, color=GOLD, min_w=80)
    s += tb
    s += _arrow(send_x, ax_y - 45, q_box_x, q_box_y, GOLD, 1.8)
    s += _arrow(q_box_x + tw, q_box_y, send_x + 200, ax_y - 20, GOLD, 1.8)

    # ── Червона зона-заборона «виробник не торкається» ───────────────────────
    forb_x = send_x + 14
    forb_w = 240
    s += _rect(forb_x, buf1y, forb_w, 30, "#fff0f0", RED, 1.6, 4)
    s += _text(forb_x + forb_w / 2, buf1y + 10, "✗ виробник", 9.5, RED, "middle", bold=True)
    s += _text(forb_x + forb_w / 2, buf1y + 24, "більше НЕ чіпає", 9, RED, "middle")

    # ── Фаза 3: споживач «володіє» ─────────────────────────────────────────
    con_x = send_x + 260
    s += _rect(con_x, buf1y, 200, 30, LBLUE, BLUE, 2.0, 6)
    s += _text(con_x + 100, buf1y + 19, "буфер (споживач)", 10, BLUE, "middle", bold=True)
    s += _text(con_x + 100, ax_y - 82, "СПОЖИВАЧ", 10, BLUE, "middle", bold=True)
    s += _text(con_x + 100, ax_y - 67, "вживає → повертає", 8.5, GREY, "middle")
    s += _line(con_x, ax_y + 8, con_x, ax_y + 20, BLUE, 1.4)
    s += _line(con_x + 200, ax_y + 8, con_x + 200, ax_y + 20, BLUE, 1.4)
    s += _line(con_x, ax_y + 20, con_x + 200, ax_y + 20, BLUE, 1.4)
    s += _text(con_x + 100, ax_y + 34, "володіє", 9, BLUE, "middle")

    # ── Пул ──────────────────────────────────────────────────────────────────
    pool_x = con_x + 220
    tb, tw, th = _tbox(pool_x + 60, ax_y - 50, "пул\nбуферів", size=10,
                       fill=LGRN, stroke=GREEN, color=GREEN, min_w=80)
    s += tb
    s += _arrow(con_x + 200, buf1y + 15, pool_x + 60, ax_y - 50 + th / 2, GREEN, 1.8)

    # ── Правило ──────────────────────────────────────────────────────────────
    s += _rect(60, H - 80, W - 120, 56, LGRN, GREEN, 1.5, 10)
    s += _text(W / 2, H - 62, "Правило «передав — забув»: після xQueueSend виробник більше не читає й не пише цей буфер.", 10, INK, "middle", bold=True)
    s += _text(W / 2, H - 44, "Подвійний доступ або подвійний free — крах. Дисципліна одна: send = назавжди віддав.", 9.5, GREY, "middle")
    s += _text(W / 2, H - 26, "Якщо потрібна відповідь — окрема черга або task notification, не зворотний send (§4.10.6).", 9, GREY, "middle")

    _save("fig-27-6a-2-ownership-transfer.svg", s)


if __name__ == "__main__":
    fig_everything_through_queue()
    fig_ownership_transfer()
    print("OK — figs for ch27-s6-a-queue-pattern written to", OUT)
