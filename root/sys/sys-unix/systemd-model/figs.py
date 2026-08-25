# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
RED = "#fdecea"
WARM = "#fff6e5"
GREY = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Дві незалежні осі: потреба й черга ───────────────────────────────────
def fig_two_axes():
    W, H = 1300, 700
    p = []

    lab_x, lab_w = 40, 268
    c1x, c1w = 330, 452
    c2x, c2w = 806, 452

    r1y, r1h = 210, 218
    r2y, r2h = 452, 218

    p.append(text(W / 2, 62, "Юніт А і юніт Б: чотири можливі пари ребер між ними",
                  size=17, bold=True))

    p.append(fitbox(c1x, 108, c1w, 76,
                    "потреба задана\nА: Requires=Б", size=15, bold=True, fill=BLUE))
    p.append(fitbox(c2x, 108, c2w, 76,
                    "потреби немає\n(Б у транзакцію не тягнеться)", size=15, bold=True, fill=GREY))

    p.append(fitbox(lab_x, r1y, lab_w, 76,
                    "черга задана\nА: After=Б", size=15, bold=True, fill=BLUE))
    p.append(fitbox(lab_x, r2y, lab_w, 76,
                    "черги немає", size=15, bold=True, fill=GREY))

    p.append(fitbox(c1x, r1y, c1w, r1h,
                    "Б підіймають першим, і лише\n"
                    "коли він піднявся — беруться за А.\n"
                    "Б не піднявся — А навіть\n"
                    "не пробує стартувати.\n"
                    "Це те, що зазвичай мають на увазі,\n"
                    "пишучи «залежність»",
                    size=15, fill=GREEN))

    p.append(fitbox(c2x, r1y, c2w, r1h,
                    "«Якщо Б узагалі стартує сьогодні —\n"
                    "то я після нього».\n"
                    "Б через це не запускають:\n"
                    "нема кому — ребро мовчить.\n"
                    "Так пишуть After=network.target\n"
                    "без жодного Wants=",
                    size=15, fill=WARM))

    p.append(fitbox(c1x, r2y, c1w, r2h,
                    "А і Б рушають одночасно.\n"
                    "Б упав через півсекунди —\n"
                    "А вже працює й ніколи\n"
                    "про це не дізнається.\n"
                    "Найчастіша помилка\n"
                    "в написаних руками юнітах",
                    size=15, fill=RED))

    p.append(fitbox(c2x, r2y, c2w, r2h,
                    "Два незалежні юніти.\n"
                    "Менеджер вільний пустити їх\n"
                    "в одній хвилі — і саме\n"
                    "з таких пар береться\n"
                    "весь виграш у часі старту",
                    size=15, fill=GREY))

    render(os.path.join(IMG, 'two-axes.svg'), W, H, *p)


# ── 2. Транзакція: замикання за потребою й хвилі за чергою ──────────────────
def fig_transaction():
    W, H = 1340, 900
    p = []

    # -- панель А ------------------------------------------------------------
    p.append(text(W / 2, 54, "Крок перший: хто взагалі потрапляє в транзакцію",
                  size=17, bold=True))

    goal, gx0, gx1, gy0, gy1 = tb(230, 220, "multi-user.target", size=15,
                                  bold=True, fill=GREEN)
    p.append(goal)

    members = [
        ("local-fs.target", 100),
        ("systemd-journald.service", 160),
        ("sshd.service", 220),
        ("postgresql.service", 280),
        ("nginx.service", 340),
    ]
    mem_bounds = {}
    for name, y in members:
        frag, x0, x1, y0, y1 = tb(940, y, name, size=14, fill=BLUE)
        p.append(frag)
        mem_bounds[name] = (x0, x1, y0, y1)
        p.append(line(gx1 + 10, 220, x0 - 10, y, color=MUTED, sw=1.4, dash="5,5"))

    p.append(text(230, 300, "мета, яку попросили", size=13, color=MUTED))
    p.append(text(230, 322, "підняти", size=13, color=MUTED))
    p.append(text(940, 392, "ребра потреби (Wants=/Requires=) тягнуть за собою", size=13, color=MUTED))
    p.append(text(940, 414, "все, без чого мета не має сенсу — і так далі вглиб", size=13, color=MUTED))

    p.append(line(60, 452, W - 60, 452, color=MUTED, sw=1.2, dash="8,6"))

    # -- панель Б ------------------------------------------------------------
    p.append(text(W / 2, 500, "Крок другий: ребра черги розкладають той самий набір на хвилі",
                  size=17, bold=True))

    cols = [200, 530, 860, 1170]
    for i, cx in enumerate(cols):
        p.append(text(cx, 556, "хвиля %d" % (i + 1), size=14, bold=True, color=MUTED))

    b = {}
    frag, *bnd = tb(cols[0], 700, "local-fs.target", size=14, fill=BLUE)
    p.append(frag); b["local-fs"] = bnd

    frag, *bnd = tb(cols[1], 620, "systemd-journald.service", size=14, fill=BLUE)
    p.append(frag); b["journald"] = bnd
    frag, *bnd = tb(cols[1], 700, "sshd.service", size=14, fill=BLUE)
    p.append(frag); b["sshd"] = bnd
    frag, *bnd = tb(cols[1], 780, "postgresql.service", size=14, fill=BLUE)
    p.append(frag); b["pg"] = bnd

    frag, *bnd = tb(cols[2], 780, "nginx.service", size=14, fill=BLUE)
    p.append(frag); b["nginx"] = bnd

    frag, *bnd = tb(cols[3], 700, "multi-user.target", size=14, bold=True, fill=GREEN)
    p.append(frag); b["goal"] = bnd

    def link(a, c):
        ax1, ay = b[a][1], (b[a][2] + b[a][3]) / 2
        cx0, cy = b[c][0], (b[c][2] + b[c][3]) / 2
        p.append(arrow(ax1 + 8, ay, cx0 - 8, cy))

    for dst in ("journald", "sshd", "pg"):
        link("local-fs", dst)
    link("pg", "nginx")
    for src in ("journald", "sshd", "nginx"):
        link(src, "goal")

    p.append(text(W / 2, 862,
                  "Три юніти другої хвилі нічим не впорядковані між собою — тому їх пускають разом",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'transaction.svg'), W, H, *p)


# ── 3. Дерево контрольних груп: чим саме тримають службу ────────────────────
def fig_cgroup_tree():
    W, H = 1260, 760
    p = []

    p.append(text(W / 2, 54, "Межа служби — не номер процесу, а контрольна група",
                  size=17, bold=True))

    y1, y2, y3, y4, y5 = 120, 250, 390, 530, 660

    root, rx0, rx1, ry0, ry1 = tb(620, y1, "-.slice", size=15, bold=True, fill=GREY)
    p.append(root)

    nodes = {}

    def put(key, cx, cy, txt, **kw):
        frag, x0, x1, y0, y1_ = tb(cx, cy, txt, **kw)
        p.append(frag)
        nodes[key] = (cx, x0, x1, y0, y1_)

    put("init", 200, y2, "init.scope", size=14, fill=WARM)
    put("sys", 620, y2, "system.slice", size=14, bold=True, fill=GREY)
    put("usr", 1040, y2, "user.slice", size=14, bold=True, fill=GREY)

    put("pid1", 200, y3, "systemd (PID 1)", size=13, fill=GREEN)
    put("nginx", 440, y3, "nginx.service", size=14, fill=BLUE)
    put("pg", 760, y3, "postgresql.service", size=14, fill=BLUE)
    put("u1000", 1060, y3, "user-1000.slice", size=14, fill=GREY)

    put("nginxp", 440, y4, "nginx: master\nnginx: worker\nnginx: worker", size=13, fill=GREEN)
    put("pgp", 770, y4, "postgres\npostgres: checkpointer\npostgres: walwriter", size=13, fill=GREEN)
    put("sess", 1060, y4, "session-3.scope", size=14, fill=WARM)

    put("sessp", 1060, y5, "bash\nvim\nfirefox", size=13, fill=GREEN)

    def elbow(pkey, ckey, prx0=None, pry1=None):
        if pkey == "root":
            px, py = 620, ry1
        else:
            px, py = nodes[pkey][0], nodes[pkey][4]
        cx, cy = nodes[ckey][0], nodes[ckey][3]
        mid = (py + cy) / 2
        p.append(line(px, py, px, mid, color=MUTED, sw=1.4))
        p.append(line(px, mid, cx, mid, color=MUTED, sw=1.4))
        p.append(line(cx, mid, cx, cy, color=MUTED, sw=1.4))

    for k in ("init", "sys", "usr"):
        elbow("root", k)
    elbow("init", "pid1")
    elbow("sys", "nginx")
    elbow("sys", "pg")
    elbow("usr", "u1000")
    elbow("nginx", "nginxp")
    elbow("pg", "pgp")
    elbow("u1000", "sess")
    elbow("sess", "sessp")

    legend = [
        "*.slice — вузол дерева, на якому вішають обмеження на все піддерево",
        "*.service — група навколо процесів, які запустив сам менеджер",
        "*.scope — група навколо процесів, яких менеджер не запускав, а лише огорнув",
    ]
    p.append(mtext(40, 706, legend, size=13, color=MUTED, anchor="start", lh=1.5))

    render(os.path.join(IMG, 'cgroup-tree.svg'), W, H, *p)


# ── 4. Як з багатьох файлів на диску виходить один юніт ─────────────────────
def fig_unit_resolution():
    W, H = 1420, 790
    p = []

    p.append(text(W / 2, 44, "Що менеджер справді читає, коли ви кажете «nginx.service»",
                  size=17, bold=True))

    ax, aw = 50, 620          # ліва панель
    bx, bw = 750, 620         # права панель
    pw, vw, gap = 430, 172, 18

    p.append(fitbox(ax, 82, aw, 56,
                    "Крок 1 — ФРАГМЕНТ\nперший знайдений файл виграє, далі не шукають",
                    size=15, bold=True, fill=GREEN))
    p.append(fitbox(bx, 82, bw, 56,
                    "Крок 2 — ДОВАЖКИ\nчитають УСІ знайдені, у порядку імен файлів",
                    size=15, bold=True, fill=BLUE))

    rows_a = [
        ("/etc/systemd/system/nginx.service", "беруть ЦЕЙ", GREEN, GREEN),
        ("/run/systemd/system/nginx.service", "уже не дивляться", GREY, GREY),
        ("/usr/local/lib/systemd/system/nginx.service", "уже не дивляться", GREY, GREY),
        ("/usr/lib/systemd/system/nginx.service", "файл пакунка лежить без дії", GREY, GREY),
    ]
    rows_b = [
        ("/usr/lib/systemd/system/service.d/10-all.conf", "читають 1-м", BLUE, WARM),
        ("/usr/lib/systemd/system/nginx.service.d/20-pkg.conf", "читають 2-м", BLUE, WARM),
        ("/run/systemd/system/nginx.service.d/50-run.conf", "читають 3-м", BLUE, WARM),
        ("/etc/systemd/system/nginx.service.d/90-local.conf", "читають 4-м", BLUE, WARM),
    ]

    ys = [168, 228, 288, 348]
    for (px, group) in ((ax, rows_a), (bx, rows_b)):
        for y, (path_s, verdict, fill_p, fill_v) in zip(ys, group):
            p.append(fitbox(px, y, pw, 46, path_s, size=13, fill=fill_p))
            p.append(fitbox(px + pw + gap, y, vw, 46, verdict, size=12, fill=fill_v))

    note_a = [
        "Порядок згори вниз — це і є пріоритет.",
        "Посилання на /dev/null у /etc — юніт замаскований:",
        "для менеджера його просто немає.",
    ]
    note_b = [
        "Сортує ІМ'Я файлу, а не каталог.",
        "Однакове ім'я в різних каталогах — виграє той,",
        "що вище в переліку кроку 1.",
    ]
    p.append(mtext(ax, 428, note_a, size=13, color=MUTED, anchor="start", lh=1.5))
    p.append(mtext(bx, 428, note_b, size=13, color=MUTED, anchor="start", lh=1.5))

    p.append(line(50, 512, W - 50, 512, color=MUTED, sw=1.2, dash="8,6"))

    p.append(text(W / 2, 552, "Ефективний юніт = фрагмент + усі доважки, злиті в цьому порядку",
                  size=16, bold=True))

    bottom = [
        ("Скалярна директива (Type=, Restart=, User=) — діє ОСТАННЄ присвоєння в порядку читання", GREEN),
        ("Директива-список (ExecStart=, Wants=, Environment=) — присвоєння НАКОПИЧУЮТЬСЯ; порожнє значення обнуляє список", WARM),
        ("Побачити результат: systemctl cat nginx.service — покаже фрагмент і всі доважки тим самим порядком", BLUE),
    ]
    for i, (s, fill) in enumerate(bottom):
        p.append(fitbox(50, 588 + i * 62, W - 100, 50, s, size=14, fill=fill))

    render(os.path.join(IMG, 'unit-resolution.svg'), W, H, *p)


# ── 4. Requires= без After= і з After=: два прогони на осі часу ─────
def fig_ordering_race():
    W, H = 1240, 670
    p = []
    XL, XR = 320, 1010

    def X(t):
        return XL + t * (XR - XL) / 11.0

    p.append(text(W / 2, 46,
                  "Той самий Requires=, два прогони: коли менеджер дізнається про збій",
                  size=18, bold=True))

    def panel(top, caption, waiting):
        p.append(text(44, top, caption, size=16, bold=True, anchor="start"))
        r1 = top + 54
        r2 = top + 112
        ax = top + 158

        p.append(text(44, r1 + 5, "late-dep.service", size=14, anchor="start"))
        p.append(rect(X(0), r1 - 18, X(10) - X(0), 36, fill=WARM))
        p.append(text((X(0) + X(10)) / 2, r1 + 5, "працює 10 секунд", size=14))
        p.append(text(X(10) + 16, r1 + 5, "✗ падає", size=14, bold=True,
                      color="#c0392b", anchor="start"))

        p.append(text(44, r2 + 5, "app.service", size=14, anchor="start"))
        if waiting:
            p.append(rect(X(0), r2 - 18, X(10) - X(0), 36, fill=GREY))
            p.append(text((X(0) + X(10)) / 2, r2 + 5,
                          "робота стоїть у стані waiting", size=14))
            p.append(text(X(10) + 16, r2 + 5, "✗ dependency", size=14, bold=True,
                          color="#c0392b", anchor="start"))
        else:
            p.append(rect(X(0), r2 - 18, 26, 36, fill=GREEN))
            p.append(text(X(0) + 44, r2 + 5,
                          "✓ відпрацював і завершився — про збій не дізнається ніколи",
                          size=14, anchor="start"))

        p.append(line(X(0), ax, X(11), ax, color=MUTED))
        for t in (0, 2, 4, 6, 8, 10):
            p.append(line(X(t), ax - 5, X(t), ax + 5, color=MUTED))
            p.append(text(X(t), ax + 24, "%d с" % t, size=12, color=MUTED))

    panel(112, "Прогін 1: Requires= є, After= немає", False)
    panel(438, "Прогін 2: додано After=late-dep.service", True)

    render(os.path.join(IMG, 'ordering-race.svg'), W, H, *p)


fig_two_axes()

fig_transaction()
fig_cgroup_tree()
fig_ordering_race()
fig_unit_resolution()
print("ok")
