# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"
GREY_FILL = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Той самий текст шляху, два різні початки розбору ─────────────────────
def fig_two_roots():
    W, H = 1120, 700
    p = []

    def tree(px, title, start_node, target_node, verdict):
        """Панель із однаковим деревом; різняться маркер старту й ціль."""
        out = []
        pw = 500
        out.append(rect(px, 40, pw, 620, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
        out.append(text(px + pw / 2, 78, title, size=15, bold=True))

        col_l = px + 150
        col_r = px + 350
        root_x = px + 250

        nodes = {
            "/":            (root_x, 150, "/"),
            "etc":          (col_l, 250, "etc"),
            "passwd_a":     (col_l, 350, "passwd"),
            "srv":          (col_r, 250, "srv"),
            "ftp":          (col_r, 350, "ftp"),
            "etc2":         (col_r, 450, "etc"),
            "passwd_b":     (col_r, 550, "passwd"),
        }
        edges = [("/", "etc"), ("etc", "passwd_a"), ("/", "srv"),
                 ("srv", "ftp"), ("ftp", "etc2"), ("etc2", "passwd_b")]

        box_h = 34
        for a, b in edges:
            xa, ya, _ = nodes[a]
            xb, yb, _ = nodes[b]
            out.append(line(xa, ya + box_h / 2, xb, yb - box_h / 2,
                            color=MUTED, sw=1.2))

        for key, (x, y, label) in nodes.items():
            if key == target_node:
                fill, stroke = RED_FILL, POS
            elif key == start_node:
                fill, stroke = GREEN_FILL, FIELD
            else:
                fill, stroke = FILL, LINE
            frag, _w, _h = textbox(x, y, label, size=13, pad=9, min_w=90,
                                   fill=fill, stroke=stroke)
            out.append(frag)

        sx, sy, _ = nodes[start_node]
        out.append(text(sx - 62, sy + 5, "старт", size=12, color=FIELD,
                        anchor="end", bold=True))
        tx, ty, _ = nodes[target_node]
        out.append(text(tx + 62, ty + 5, "знайдено", size=12, color=POS,
                        anchor="start", bold=True))

        out.append(fitbox(px + 30, 600, pw - 60, 44, verdict, size=13,
                          fill=WARM_FILL, stroke=WARM))
        return "".join(out)

    p.append(tree(30, "процес A: корінь — справжній корінь",
                  "/", "passwd_a", "«/etc/passwd» → файл системи"))
    p.append(tree(590, "процес B: після chroot(\"/srv/ftp\")",
                  "ftp", "passwd_b", "«/etc/passwd» → файл усередині дерева"))

    render(os.path.join(IMG, 'two-roots.svg'), W, H, *p,
           title="Один і той самий текст шляху веде в різні файли")


# ── 2. Класична втеча подвійним chroot ──────────────────────────────────────
def fig_escape():
    W, H = 1080, 760
    p = []

    steps = [
        (40, 40, "1. процес уже в дереві",
         "/jail", "/jail",
         "корінь і поточний каталог збіглися:\n«..» у корені веде сам у себе"),
        (560, 40, "2. mkdir foo; chroot(\"foo\")",
         "/jail/foo", "/jail",
         "корінь опустився нижче,\nа поточний каталог лишили на місці"),
        (40, 400, "3. chdir(\"..\") — і ще раз",
         "/jail/foo", "/",
         "поточний каталог не в новому корені,\nтож перевірка не спрацьовує жодного разу"),
        (560, 400, "4. chroot(\".\")",
         "/", "/",
         "коренем стає справжній корінь:\nдерево відкрито повністю"),
    ]

    nodes = ["/", "/jail", "/jail/foo"]

    for px, py, title, root_at, cwd_at, note in steps:
        pw, ph = 480, 330
        p.append(rect(px, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
        p.append(text(px + pw / 2, py + 34, title, size=14, bold=True))

        col_x = px + 130
        ys = [py + 80, py + 138, py + 196]
        for i, name in enumerate(nodes):
            if i:
                p.append(line(col_x, ys[i - 1] + 17, col_x, ys[i] - 17,
                              color=MUTED, sw=1.2))
            frag, _w, _h = textbox(col_x, ys[i], name, size=13, pad=9, min_w=150)
            p.append(frag)

        ri = nodes.index(root_at)
        ci = nodes.index(cwd_at)
        frag, _w, _h = textbox(px + 290, ys[ri], "корінь", size=12, pad=8,
                               min_w=88, fill=GREEN_FILL, stroke=FIELD, bold=True)
        p.append(frag)
        frag, _w, _h = textbox(px + 400, ys[ci], "тут я", size=12, pad=8,
                               min_w=88, fill=BLUE_FILL, stroke=NEG, bold=True)
        p.append(frag)

        p.append(fitbox(px + 30, py + 236, pw - 60, 66, note, size=12,
                        fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'escape-double-chroot.svg'), W, H, *p,
           title="Чотири кроки класичної втечі з chroot")


# ── 3. Що виклик міняє і що лишає незмінним ─────────────────────────────────
def fig_scope():
    W, H = 1060, 560
    p = []

    left = [
        "ЩО МІНЯЄТЬСЯ",
        "",
        "одне поле в описі процесу:",
        "звідки починати розбір шляху,",
        "що написаний із «/»",
        "",
        "успадковується через fork,",
        "переживає execve",
    ]
    right = [
        "ЩО ЛИШАЄТЬСЯ ТИМ САМИМ",
        "",
        "поточний каталог процесу",
        "уже відкриті дескриптори",
        "таблиця монтувань",
        "uid, gid і можливості",
        "PID-и, сигнали, ptrace",
        "мережа й відкриті сокети",
        "спільна пам'ять і черги",
        "параметри ядра, модулі",
    ]

    frag, _w, _h = textbox(280, 290, left, size=14, pad=26,
                           fill=GREEN_FILL, stroke=FIELD, min_w=420)
    p.append(frag)
    frag, _w, _h = textbox(780, 290, right, size=14, pad=26,
                           fill=RED_FILL, stroke=POS, min_w=420)
    p.append(frag)

    p.append(text(W / 2, 60, "chroot: одна зміна — і все решта поза нею",
                  size=16, bold=True))

    render(os.path.join(IMG, 'scope-of-chroot.svg'), W, H, *p,
           title="Обсяг дії chroot")


# ── 4. chroot проти pivot_root ──────────────────────────────────────────────
def fig_pivot():
    W, H = 1080, 620
    p = []

    # ліва панель — chroot
    p.append(rect(40, 40, 480, 540, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(280, 78, "chroot", size=16, bold=True))

    frag, _w, _h = textbox(280, 150, ["монтування «/»", "(усе дерево системи)"],
                           size=13, pad=12, min_w=340)
    p.append(frag)
    p.append(line(280, 186, 280, 224, color=MUTED, sw=1.2))
    frag, _w, _h = textbox(280, 260, ["каталог /new", "— новий корінь процесу"],
                           size=13, pad=12, min_w=340,
                           fill=GREEN_FILL, stroke=FIELD)
    p.append(frag)

    p.append(fitbox(70, 340, 420, 96,
                    "старе дерево нікуди не поділося:\n"
                    "воно змонтоване й досяжне —\n"
                    "потрібен лише спосіб на нього послатися",
                    size=12, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(70, 460, 420, 76,
                    "оборона тримається на тому,\n"
                    "що процес утратив права",
                    size=12, fill=FILL, stroke=LINE))

    # права панель — pivot_root
    p.append(rect(560, 40, 480, 540, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(800, 78, "pivot_root у власному просторі монтувань",
                  size=15, bold=True))

    frag, _w, _h = textbox(800, 150, ["монтування «/»", "— тепер це дерево контейнера"],
                           size=13, pad=12, min_w=340,
                           fill=GREEN_FILL, stroke=FIELD)
    p.append(frag)
    frag, _w, _h = textbox(800, 260, ["старе дерево:", "відмонтовано"],
                           size=13, pad=12, min_w=340,
                           fill=GREY_FILL, stroke=MUTED, color=MUTED)
    p.append(frag)

    p.append(fitbox(590, 340, 420, 96,
                    "у цьому просторі монтувань\n"
                    "старого кореня немає в таблиці —\n"
                    "послатися на нього нема чим",
                    size=12, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(590, 460, 420, 76,
                    "оборона тримається на тому,\n"
                    "що дороги не існує",
                    size=12, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'chroot-vs-pivot-root.svg'), W, H, *p,
           title="chroot лишає старе дерево змонтованим, pivot_root — ні")


if __name__ == '__main__':
    fig_two_roots()
    fig_escape()
    fig_scope()
    fig_pivot()
    print("ok")
