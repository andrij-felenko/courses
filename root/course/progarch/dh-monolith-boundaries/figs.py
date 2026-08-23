# -*- coding: utf-8 -*-
"""Фігури до кроку «Межі всередині моноліта DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CORE = "#eafaf0"    # ядро
BELT = "#eef2fb"    # пояс служб
GEN = "#fdf3e3"     # загальне
KERN = "#fff8e1"    # спільне ядро / шина / контракт
FAC = "#27ae60"     # смуга-фасад


def _box(cx, cy, label, fill=FILL, stroke=LINE, sw=1.6, min_w=120, size=14,
         bold=False, dash=None, min_h=0):
    """Рамка з текстом; повертає (frag, left, right, top, bottom)."""
    lines = label.split("\n")
    tw = max(text_width(ln, size, bold) for ln in lines)
    w = max(min_w, tw + 22)
    h = max(min_h, len(lines) * size * 1.3 + 22 - size * 0.3)
    x, y = cx - w / 2, cy - h / 2
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    body = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
            'fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (x, y, w, h, fill, stroke, sw, d))
    ty = cy - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
    body += mtext(cx, ty, lines, size=size, color=INK, bold=bold)
    return body, x, x + w, y, y + h


def _module(cx, cy, label, fill, min_w=250, min_h=78):
    """Модуль: рамка + зелена смуга-фасад уздовж верхнього краю."""
    b, l, r, t, bt = _box(cx, cy, label, fill=fill, stroke=INK, sw=1.8,
                          min_w=min_w, size=14, bold=True, min_h=min_h)
    strip = ('<rect x="%.1f" y="%.1f" width="%.1f" height="7" rx="3.5" '
             'fill="%s"/>' % (l + 6, t + 3, (r - l) - 12, FAC))
    return b + strip, l, r, t, bt


def fig_rooms():
    """Одна коробка розгортання, вісім модулів + спільне ядро всередині."""
    W, H = 1200, 760
    f = []
    # зовнішня коробка застосунку
    f.append(rect(60, 84, 1080, 620, fill="#fcfdff", stroke=FIELD, sw=2.6))
    f.append(text(600, 116, "Digital Homes — один застосунок · один процес · один деплой",
                  size=15, bold=True, color=FIELD))

    cols = [300, 600, 900]
    rows = [230, 400, 570]
    mods = [
        ("Керування\n(control)", CORE), ("Твін\n(twin)", CORE), ("Автоматизації\n(automations)", CORE),
        ("Телеметрія\n(telemetry)", BELT), ("Відео\n(video)", BELT), ("Сповіщення\n(notifications)", BELT),
        ("Ідентичність\n(identity)", GEN), ("Білінг\n(billing)", GEN), None,
    ]
    i = 0
    for ry in rows:
        for cx in cols:
            m = mods[i]; i += 1
            if m is None:
                # спільне ядро — окремий крихітний чип
                b, l, r, t, bt = _box(cx, ry, "спільне ядро\nids: DeviceId · HomeId",
                                      fill=KERN, stroke=FIELD, sw=1.8, min_w=250, size=12,
                                      min_h=78)
                f.append(b)
                continue
            mb, l, r, t, bt = _module(cx, ry, m[0], m[1])
            f.append(mb)

    # мітки сортів (ліворуч від рядків)
    f.append(text(96, rows[0] - 2, "ЯДРО", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(96, rows[1] - 2, "СЛУЖБИ", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(96, rows[2] - 2, "ЗАГАЛЬНЕ", size=12, bold=True, color=MUTED, anchor="start"))

    f.append(text(600, 686,
                  "зелена смуга = фасад (єдині двері) · тіло модуля = приватні класи й таблиці, чужим невидимі",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "monolith-rooms.svg"), W, H, *f,
           title="Одна коробка розгортання, дев'ять стін усередині")


def fig_import_rules():
    """Стрілки мапи стали правилами імпорту: прямий виклик vs підписка на шину."""
    W, H = 1280, 730
    f = []

    # шина подій — горизонтальний хребет угорі
    bx0, bx1, by = 480, 1190, 140
    f.append(rect(bx0, by - 22, bx1 - bx0, 44, fill=KERN, stroke=NEG, sw=2.2))
    f.append(text((bx0 + bx1) / 2, by + 5,
                  "внутрішньопроцесна шина подій · DeviceEvent (опублікована мова)",
                  size=13, bold=True, color=NEG))

    # ── лівий стовпчик: керування → твін → автоматизації ──
    ctl, cl, cr, ct, cb = _box(250, 140, "Керування\n(control)",
                               fill=CORE, stroke=INK, sw=2.0, min_w=200, size=14, bold=True)
    twn, tl, tr, tt, tb = _box(250, 330, "Твін\n(twin)",
                               fill=CORE, stroke=INK, sw=2.0, min_w=200, size=14, bold=True)
    aut, al, ar, at, ab = _box(250, 520, "Автоматизації\n(automations)",
                               fill=CORE, stroke=INK, sw=2.0, min_w=210, size=14, bold=True)

    # керування публікує у шину
    f.append(arrow(cr + 6, 140, bx0 - 8, 140, color=NEG, sw=2.0))
    f.append(text((cr + bx0) / 2, 122, "публікує факт", size=12, color=NEG))
    # автоматизації → твін: прямий виклик фасаду (вертикаль у стовпчику)
    f.append(arrow(250, at - 6, 250, tb + 6, color=FIELD, sw=2.2))
    f.append(text(236, 420, "twin.currentState()", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(236, 437, "прямий виклик фасаду", size=11, color=FIELD, anchor="end"))
    f.extend([ctl, twn, aut])

    # ── підписники праворуч під шиною (пунктир зі шини + вістря) ──
    subs = [("Телеметрія", 660), ("Сповіщення", 900), ("Білінг", 1140)]
    for lbl, sx in subs:
        b, l, r, t, bt = _box(sx, 330, lbl, fill=BELT, stroke=NEG, sw=1.6, min_w=190, size=13)
        f.append(line(sx, by + 22, sx, t - 18, color=NEG, sw=1.6, dash="5,4"))
        f.append(arrow(sx, t - 18, sx, t - 5, color=NEG, sw=1.6))
        f.append(b)
    f.append(text(900, 372, "підписані — не імпортують control", size=12, color=NEG))

    # автоматизації теж підписані: пунктир зі шини до її правого верху
    f.append(line(bx0 + 24, by + 22, ar + 4, at - 14, color=NEG, sw=1.5, dash="5,4"))
    f.append(arrow(ar + 4, at - 14, ar - 4, at - 5, color=NEG, sw=1.5))

    # ── ідентичність: фундамент, усі кличуть синхронно вниз ──
    f.append(rect(560, 612, 660, 58, fill=GEN, stroke=INK, sw=2.2))
    f.append(text(890, 636, "Ідентичність (identity) — фасад authorize(token)", size=14, bold=True))
    f.append(text(890, 656, "усі кличуть синхронно; напрямок лише вниз — граф ациклічний",
                  size=12, color=MUTED))
    f.append(arrow(900, 348, 900, 610, color=FIELD, sw=1.5))    # сповіщення → identity
    f.append(arrow(1140, 348, 1140, 610, color=FIELD, sw=1.5))  # білінг → identity

    # ── легенда ──
    f.append(line(80, 694, 122, 694, color=FIELD, sw=2.4))
    f.append(text(130, 698, "суцільна — прямий виклик фасаду (синхронно)",
                  size=12, color=INK, anchor="start"))
    f.append(line(560, 694, 602, 694, color=NEG, sw=1.8, dash="5,4"))
    f.append(text(610, 698, "пунктир — підписка на подію через шину",
                  size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "import-rules.svg"), W, H, *f,
           title="Стрілки мапи стали правилами імпорту")


def fig_one_db():
    """Одна база, схема на модуль: JOIN через стіну заборонено, зшивання — на боці читача."""
    W, H = 1140, 640
    f = []

    # читач-дашборд угорі
    rd, rl, rr, rt, rb = _box(570, 105, "дашборд «пристрій + останній вимір»\n(читання-композиція)",
                              fill=KERN, stroke=INK, sw=2.2, min_w=380, size=13, bold=True)
    f.append(rd)

    # одна база
    f.append(rect(90, 250, 960, 320, fill="#fbfdff", stroke=NEG, sw=2.6))
    f.append(text(570, 282, "Одна база даних (Postgres) — але не спільна купа таблиць", size=14, bold=True, color=NEG))

    # три схеми-комори
    sc, scl, scr, sct, scb = _box(260, 430, "схема control\n· device\n· room",
                                  fill=CORE, stroke=FIELD, sw=2.0, min_w=210, size=13)
    st, stl, str_, stt, stb = _box(570, 430, "схема telemetry\n· reading",
                                   fill=BELT, stroke=NEG, sw=2.0, min_w=210, size=13)
    sb, sbl, sbr, sbt, sbb = _box(880, 430, "схема billing\n· plan",
                                  fill=GEN, stroke=MUTED, sw=2.0, min_w=210, size=13)
    f.extend([sc, st, sb])

    # заборонений JOIN між control.device і telemetry.reading
    jx = (scr + stl) / 2
    f.append(line(scr + 4, 470, stl - 4, 470, color=POS, sw=2.2, dash="7,5"))
    f.append(line(jx - 14, 456, jx + 14, 484, color=POS, sw=4))
    f.append(line(jx - 14, 484, jx + 14, 456, color=POS, sw=4))
    f.append(text(jx, 512, "JOIN / FK через стіну", size=12, color=POS, bold=True))
    f.append(text(jx, 528, "заборонено", size=12, color=POS, bold=True))

    # зшивання на боці читача: два виклики фасадів
    f.append(arrow(rl + 40, rb + 4, 260, sct - 6, color=FIELD, sw=1.9))
    f.append(arrow(rr - 40, rb + 4, 570, stt - 6, color=FIELD, sw=1.9))
    f.append(text(330, 210, "control.getDevice()", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(600, 210, "telemetry.lastReading()", size=12, color=FIELD, bold=True, anchor="start"))

    f.append(text(570, 604,
                  "кожен модуль володіє своєю схемою; читач не зшиває JOIN-ом, а кличе два фасади й склеює сам",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "one-db-cellars.svg"), W, H, *f,
           title="Одна база, дев'ять комор — межа й на рівні даних")


def fig_bus_tx():
    """Синхронна диспетчеризація в одній транзакції; праворуч — відкат за винятком підписника."""
    W, H = 1300, 700
    f = []

    def panel(cx0, cx1, ok):
        col = FIELD if ok else POS
        bx0, bx1, bt0, bt1 = cx0 + 24, cx1 - 24, 174, 560
        cx = (cx0 + cx1) / 2
        # рамка транзакції
        f.append(rect(bx0, bt0, bx1 - bx0, bt1 - bt0,
                      fill=("#f4fbf6" if ok else "#fdf3f2"), stroke=col, sw=2.8))
        f.append(text(cx, bt0 - 16, "Щасливий шлях" if ok else "Підписник кинув виняток",
                      size=15, bold=True, color=INK))
        f.append(text(bx0 + 10, bt0 + 20, "BEGIN tx", size=12, bold=True, color=col, anchor="start"))
        # три вертикальні вузли операції
        a, _, _, _, ab = _box(cx, 222, "control.apply(cmd)", fill=CORE, stroke=INK,
                              sw=1.9, min_w=240, size=13, bold=True)
        b, _, _, btb, bb = _box(cx, 292, "repo.apply → запис у device", fill=FILL,
                                stroke=INK, sw=1.6, min_w=290, size=12)
        c, cpl, cpr, ctc, cb = _box(cx, 362, "bus.publish(DeviceEvent)", fill=KERN,
                                    stroke=NEG, sw=2.0, min_w=260, size=13, bold=True)
        f.extend([a, b, c])
        f.append(arrow(cx, ab + 2, cx, btb - 2, color=INK, sw=1.5))
        f.append(arrow(cx, bb + 2, cx, ctc - 2, color=INK, sw=1.5))
        # чотири підписники в ряд, віялом зі шини
        subs = ["telemetry\n.record", "automations\n.on_event",
                "notifications\n.on_event", "billing\n.on_event"]
        n = len(subs)
        left, right = bx0 + 24, bx1 - 24
        centers = [left + (right - left) * (i + 0.5) / n for i in range(n)]
        for i, (lbl, scx) in enumerate(zip(subs, centers)):
            bad = (not ok) and i == 2
            sb, sl, sr, stt, sbb = _box(scx, 470, lbl,
                                        fill=("#fdecea" if bad else BELT),
                                        stroke=(POS if bad else NEG),
                                        sw=(2.4 if bad else 1.5),
                                        min_w=120, size=11, min_h=56)
            f.append(line(cx, cb + 2, scx, stt - 2, color=(POS if bad else NEG),
                          sw=(1.8 if bad else 1.3), dash="4,3"))
            f.append(arrow(scx, stt - 9, scx, stt - 2, color=(POS if bad else NEG), sw=1.4))
            f.append(sb)
            if bad:
                f.append(line(sr - 17, stt - 11, sr - 4, stt + 2, color=POS, sw=3))
                f.append(line(sr - 4, stt - 11, sr - 17, stt + 2, color=POS, sw=3))
                f.append(text(scx, sbb + 17, "кидає виняток", size=11, bold=True, color=POS))
                # виняток розкручується назад через publish → відкат усієї tx
                f.append(arrow(scx - 4, stt - 2, cpr - 6, 372, color=POS, sw=2.4))
        # підсумок
        if ok:
            f.append(text(cx, bt1 - 16, "COMMIT — уся операція атомарна",
                          size=13, bold=True, color=FIELD))
        else:
            f.append(text(cx, bt1 - 26, "ROLLBACK", size=16, bold=True, color=POS))
            f.append(text(cx, bt1 - 8, "запис device відкочено через збій СПОВІЩЕННЯ",
                          size=12, color=POS))

    panel(40, 650, True)
    panel(660, 1270, False)
    render(os.path.join(IMG, "bus-tx-dispatch.svg"), W, H, *f,
           title="Синхронна диспетчеризація в одній транзакції — і відкат за збоєм підписника")


def fig_arch_gate():
    """Фітнес-функція як гейт збірки: три червоні умови валять build."""
    W, H = 1240, 560
    f = []
    # джерело → граф
    s, _, sr, _, _ = _box(160, 150, "джерело\ndh/** (9 модулів)\n+ SQL, schema.sql",
                          fill=FILL, stroke=INK, sw=1.8, min_w=210, size=12, bold=True, min_h=96)
    g, gl, gr, _, gb = _box(160, 340, "побудувати граф\nімпортів (AST)\n+ прочитати\nіменування схем",
                            fill=KERN, stroke=NEG, sw=1.9, min_w=210, size=12, min_h=112)
    f.extend([s, g])
    f.append(arrow(160, 200, 160, 282, color=INK, sw=1.6))
    # три гейти-перевірки
    gates = [
        ("1 · заборонене ребро", "billing → control", 135),
        ("2 · цикл у графі", "automations ⇄ twin", 285),
        ("3 · чужа схема", "telemetry → control.device", 435),
    ]
    xg = 640
    fail_pts = []
    for title_, sub, gy in gates:
        b, bl, br, bt_, bb_ = _box(xg, gy, title_ + "\n" + sub, fill="#fdecea",
                                   stroke=POS, sw=2.0, min_w=310, size=12, bold=True, min_h=74)
        f.append(b)
        f.append(arrow(gr + 6, 340, bl - 6, gy, color=NEG, sw=1.5))
        cxx = br + 30
        f.append(line(cxx - 12, gy - 12, cxx + 12, gy + 12, color=POS, sw=4.2))
        f.append(line(cxx + 12, gy - 12, cxx - 12, gy + 12, color=POS, sw=4.2))
        fail_pts.append((cxx + 16, gy))
    # вузол «червона збірка» (світлий текст на червоному)
    rcx, rcy, rw, rh = 1090, 285, 220, 108
    rl, rt = rcx - rw / 2, rcy - rh / 2
    f.append(rect(rl, rt, rw, rh, fill=POS, stroke="#7a1f16", sw=2.6, rx=9))
    ty = rcy - 2 * 13 * 1.3 / 2 + 13 * 0.35
    f.append(mtext(rcx, ty, ["ЗБІРКА ЧЕРВОНА", "exit 1 —", "merge заблоковано"],
                   size=13, color="#ffffff", bold=True))
    for px, py in fail_pts:
        f.append(arrow(px, py, rl - 6, rcy, color=POS, sw=1.6))
    # зелений шлях
    f.append(line(rcx - 155, 452, rcx + 155, 452, color=FIELD, sw=1.5))
    f.append(text(rcx, 474, "жодного ✗ → ЗБІРКА ЗЕЛЕНА", size=13, bold=True, color=FIELD))
    render(os.path.join(IMG, "arch-gate.svg"), W, H, *f,
           title="Фітнес-функція як гейт збірки: три червоні умови")


def fig_nplus1_batch():
    """Читання-композиція на списку: наївний N+1 проти батч-виклику."""
    W, H = 1220, 660
    f = []
    RED_BG = "#fdecea"
    GRN_BG = "#eafaf0"

    # роздільник між панелями
    f.append(line(610, 120, 610, 600, color=MUTED, sw=1.2, dash="5,5"))

    # ── ЛІВА ПАНЕЛЬ: НАЇВНО (N+1) ──
    f.append(text(325, 96, "НАЇВНО — по виклику на кожен пристрій",
                  size=15, bold=True, color=POS))
    rd, rl, rr, rt, rb = _box(325, 172, "дашборд\ndeviceCards(homeId)",
                              fill=KERN, stroke=INK, sw=2.0, min_w=250, size=13, bold=True)
    cb, cl, cr, ct, cbt = _box(195, 335, "control\nlistDevices()",
                               fill=CORE, stroke=FIELD, sw=1.8, min_w=180, size=13)
    # телеметрія — стос коробок (натяк на повтор N разів)
    tb, tl, tr, tt, tbt = _box(455, 335, "telemetry\nlastReading(id)",
                               fill=BELT, stroke=NEG, sw=1.8, min_w=200, size=13)
    gw, gh = tr - tl, tbt - tt
    f.append(rect(tl + 20, tt + 20, gw, gh, fill=BELT, stroke=NEG, sw=1.1))
    f.append(rect(tl + 10, tt + 10, gw, gh, fill=BELT, stroke=NEG, sw=1.1))
    f.append(tb)
    # стрілки
    f.append(arrow(rl + 36, rb + 4, cl + 70, ct - 6, color=FIELD, sw=1.9))
    f.append(text(150, 258, "1 запит", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(arrow(rr - 36, rb + 4, 455, tt - 6, color=POS, sw=2.2))
    f.append(text(508, 250, "× N", size=15, color=POS, bold=True, anchor="start"))
    f.append(text(508, 268, "по виміру на кожен", size=11, color=POS, anchor="start"))
    # ліві коробки (поверх стосу — дашборд і control малюємо останніми)
    f.append(rd)
    f.append(cb)
    # підсумок
    sb, *_ = _box(325, 495, "1 + N = 1001 запит\n(N = 1000 пристроїв)",
                  fill=RED_BG, stroke=POS, sw=2.0, min_w=300, size=13, bold=True)
    f.append(sb)

    # ── ПРАВА ПАНЕЛЬ: БАТЧ (2) ──
    f.append(text(895, 96, "БАТЧ — усі одним запитом",
                  size=15, bold=True, color=FIELD))
    rd2, rl2, rr2, rt2, rb2 = _box(895, 172, "дашборд\ndeviceCards(homeId)",
                                   fill=KERN, stroke=INK, sw=2.0, min_w=250, size=13, bold=True)
    cb2, cl2, cr2, ct2, cbt2 = _box(765, 335, "control\nlistDevices()",
                                    fill=CORE, stroke=FIELD, sw=1.8, min_w=180, size=13)
    tb2, tl2, tr2, tt2, tbt2 = _box(1040, 335, "telemetry\nlastReadings(ids)",
                                    fill=BELT, stroke=NEG, sw=1.8, min_w=225, size=13)
    f.extend([rd2, cb2, tb2])
    f.append(arrow(rl2 + 36, rb2 + 4, cl2 + 70, ct2 - 6, color=FIELD, sw=1.9))
    f.append(text(720, 258, "1 запит", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(arrow(rr2 - 36, rb2 + 4, 1040, tt2 - 6, color=FIELD, sw=2.2))
    f.append(text(1082, 250, "1 запит", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(1082, 268, "на всіх", size=11, color=FIELD, anchor="start"))
    sb2, *_ = _box(895, 495, "1 + 1 = 2 запити\n(будь-яке N)",
                   fill=GRN_BG, stroke=FIELD, sw=2.0, min_w=300, size=13, bold=True)
    f.append(sb2)

    f.append(text(610, 628,
                  "стіни це не торкається — тисячу запитів породив цикл, а не кордон",
                  size=13, color=MUTED))
    render(os.path.join(IMG, "nplus1-vs-batch.svg"), W, H, *f,
           title="N+1 проти батч-виклику на межі control↔telemetry")


def fig_read_projection():
    """Читання, підняте до проєкції: та сама шина живить денормалізований зріз."""
    W, H = 1240, 760
    f = []
    CARD = "#eef6ff"

    # ── бік запису (джерело правди) ──
    f.append(rect(250, 96, 740, 100, fill="#fcfdff", stroke=FIELD, sw=2.2))
    f.append(text(620, 122, "БІК ЗАПИСУ (джерело правди) — кожен свою нормалізовану схему",
                  size=13, bold=True, color=FIELD))
    ctl, *_ = _box(410, 164, "control\ndevice · room",
                   fill=CORE, stroke=INK, sw=1.8, min_w=210, size=13, bold=True)
    tel, *_ = _box(830, 164, "telemetry\nreading",
                   fill=BELT, stroke=INK, sw=1.8, min_w=210, size=13, bold=True)
    f.extend([ctl, tel])

    # потік фактів у шину
    f.append(arrow(620, 200, 620, 251, color=FIELD, sw=2.0))
    f.append(text(636, 228, "потік фактів DeviceEvent", size=12, color=FIELD, anchor="start"))

    # шина
    f.append(rect(230, 254, 780, 44, fill=KERN, stroke=NEG, sw=2.2))
    f.append(text(620, 281, "внутрішньопроцесна шина подій · DeviceEvent",
                  size=13, bold=True, color=NEG))

    # шина → проєктор (пунктир)
    f.append(line(430, 298, 430, 374, color=NEG, sw=1.7, dash="5,4"))
    f.append(arrow(430, 374, 430, 390, color=NEG, sw=1.7))
    f.append(text(256, 332, "on DeviceEvent", size=12, color=NEG, anchor="start"))
    # лаг
    f.append(text(704, 324, "лаг = кінцева узгодженість", size=12, color=POS, anchor="start"))
    f.append(text(704, 342, "у пам'яті ≈ 0 · у брокері — мс…с", size=11, color=POS, anchor="start"))

    # проєктор
    pj, pl, pr, pt, pbt = _box(430, 428, "проєктор device_card\n(підписник · єдиний писар)",
                               fill=KERN, stroke=INK, sw=2.0, min_w=320, size=13, bold=True)
    f.append(pj)
    f.append(text(704, 418, "вимір (value, at) — прямо з події", size=11, color=MUTED, anchor="start"))
    f.append(text(704, 436, "ім'я, кімната — control.getDevice() раз на пристрій",
                  size=11, color=MUTED, anchor="start"))

    # проєктор → read-модель
    f.append(arrow(430, pbt + 4, 430, 524, color=FIELD, sw=2.0))
    f.append(text(446, 500, "upsert — єдиний писар", size=12, color=FIELD, anchor="start"))

    # read-модель
    rm, rml, rmr, rmt, rmb = _box(410, 582,
                                  "read-модель · device_card\nденормалізований зріз\n1 рядок на пристрій · усе склеєно",
                                  fill=CARD, stroke=NEG, sw=2.0, min_w=360, size=12, bold=True)
    f.append(rm)

    # дашборд + тривіальний SELECT
    dsb, dl, dr, dt, dbt = _box(980, 582, "дашборд\n(один екран)",
                                fill=KERN, stroke=INK, sw=2.0, min_w=170, size=13, bold=True)
    f.append(dsb)
    f.append(arrow(rmr + 6, 582, dl - 6, 582, color=FIELD, sw=2.1))
    f.append(text((rmr + dl) / 2, 564, "1 тривіальний SELECT", size=12, color=FIELD, bold=True))

    f.append(text(620, 710,
                  "склеювання переїхало з ЧАСУ ЧИТАННЯ (кожен показ) на ЧАС ПОДІЇ (раз на зміну)",
                  size=13, bold=True, color=MUTED))
    render(os.path.join(IMG, "read-projection.svg"), W, H, *f,
           title="Читання, підняте до проєкції — CQRS у малому")


if __name__ == "__main__":
    fig_rooms()
    fig_import_rules()
    fig_one_db()
    fig_bus_tx()
    fig_arch_gate()
    fig_nplus1_batch()
    fig_read_projection()
    print("OK: monolith-rooms, import-rules, one-db-cellars, bus-tx-dispatch, arch-gate, "
          "nplus1-vs-batch, read-projection")
