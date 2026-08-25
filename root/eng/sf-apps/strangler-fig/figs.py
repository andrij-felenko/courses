# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_fig_over_host():
    """Ботанічна паралель: фікус проростає згори, обвиває стовбур, заступає крону.
    Три фази — той самий силует стовбура, дедалі більше зайнятий фікусом."""
    W, H = 1040, 430
    frags = []
    frags.append(text(W / 2, 30,
                      "Як фікус-душитель заступає дерево — три фази, той самий стовбур",
                      size=16, bold=True))

    phases = [
        (185, "Фаза 1", "насінина проросла\nу розвилці згори",
         0.12, "фікус — лише пагін нагорі;\nдерево ще годує все"),
        (520, "Фаза 2", "корені сповзли\nпо стовбуру донизу",
         0.5, "половину крони тримає фікус,\nполовину — ще дерево"),
        (855, "Фаза 3", "фікус дійшов ґрунту,\nобхопив стовбур",
         0.92, "дерево зсередини зникло;\nкрону тримає сам фікус"),
    ]
    base_y = 350          # рівень ґрунту
    top_y = 130           # верх крони
    trunk_h = base_y - top_y
    for cx, tag, cap, frac, note in phases:
        # ґрунт
        frags.append(line(cx - 130, base_y, cx + 130, base_y, color="#8a6d3b", sw=3))
        # стовбур-господар (сірий)
        frags.append(rect(cx - 16, top_y, 32, trunk_h, fill="#efe7db", stroke="#a1887f", sw=1.5, rx=4))
        # крона-господар (світле кільце позаду)
        frags.append(circle(cx, top_y, 46, fill="#eef6ee", stroke="#bcd6bc", sw=1.5))
        # фікус: зелена «мантія» на стовбурі знизу вгору за frac
        fh = trunk_h * frac
        frags.append(rect(cx - 24, base_y - fh, 48, fh, fill="#d7efd7", stroke=FIELD, sw=2, rx=6))
        # зелена частка крони пропорційно
        if frac >= 0.9:
            frags.append(circle(cx, top_y, 46, fill="#d7efd7", stroke=FIELD, sw=2))
        elif frac >= 0.4:
            # півкрони зелена
            frags.append('<path d="M %.0f %.0f A 46 46 0 0 1 %.0f %.0f Z" fill="#d7efd7" stroke="%s" stroke-width="2"/>'
                         % (cx, top_y - 46, cx, top_y + 46, FIELD))
        # підписи
        frags.append(text(cx, 68, tag, size=13, bold=True, color=FIELD))
        frags.append(mtext(cx, 90, cap, size=10.5, color=INK))
        frags.append(mtext(cx, base_y + 26, note, size=10.5, color=MUTED))

    frags.append(text(W / 2, 415,
                      "нове росте на старому й довкола нього; господар слабне поступово, а не гине від сокири в один день",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "fig-over-host.svg"), W, H, *frags)


def fig_interceptor():
    """Перехоплювач на вході: той самий запит, але маршрут за можливістю йде в нове.
    Показано три можливості — одна вже переїхала, одна в переїзді, одна ще стара."""
    W, H = 1080, 470
    frags = []
    frags.append(text(W / 2, 30,
                      "Перехоплювач на вході: клієнт стукає в одні двері, маршрут веде куди готово",
                      size=16, bold=True))

    # клієнт зліва
    cl, cw, _ = textbox(105, 235, "клієнти\n(той самий\nдомен-URL)", size=12, min_w=120,
                        fill="#eaf0fd", stroke=NEG)
    frags.append(cl)

    # перехоплювач — вузька висока рамка
    ix = 300
    frags.append(rect(ix - 55, 110, 110, 250, fill="#fff7e6", stroke="#d68910", sw=2, rx=10))
    frags.append(mtext(ix, 140, "Перехоп-\nлювач", size=12, bold=True, color="#b9770e"))
    frags.append(mtext(ix, 250, "дивиться\nна запит,\nобирає\nмаршрут", size=10.5, color=MUTED))
    frags.append(arrow(105 + cw / 2, 235, ix - 55, 235, color=NEG, sw=2))

    # три можливості: рядки
    rows = [
        (150, "«показати рахунок»", FIELD, "d7efd7", "переїхало", "нове", True),
        (235, "«оформити замовлення»", "#d68910", "fff2d6", "у переїзді", "нове+звірка зі старим", None),
        (320, "«річний звіт»", MUTED, "efe7db", "ще старе", "спадщина", False),
    ]
    newx, oldx = 720, 720
    # блоки нове / старе праворуч
    frags.append(rect(newx - 90, 118, 260, 96, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    frags.append(text(newx + 40, 140, "НОВА система", size=12, bold=True, color=FIELD))
    frags.append(rect(oldx - 90, 300, 260, 96, fill="#f4ece0", stroke="#a1887f", sw=2, rx=10))
    frags.append(text(oldx + 40, 322, "СТАРА система (спадщина)", size=12, bold=True, color="#8a6d3b"))

    lblx = ix + 165        # центр мітки можливості — з відступом, щоб стрілка йшла зліва направо
    for y, label, col, fill, tag, dest, to_new in rows:
        b, bw, _ = textbox(lblx, y, label, size=10.5, min_w=180, fill="#" + fill, stroke=col)
        frags.append(b)
        frags.append(arrow(ix + 55, y, lblx - bw / 2, y, color=col, sw=1.6))
        frags.append(text(lblx, y + 24, tag, size=9.5, color=col, italic=True, bold=True))
        # куди веде
        if to_new is True:
            frags.append(arrow(lblx + bw / 2, y, newx - 90, 175, color=FIELD, sw=1.8))
        elif to_new is False:
            frags.append(arrow(lblx + bw / 2, y, oldx - 90, 355, color="#a1887f", sw=1.8))
        else:
            # у переїзді — веде в НОВЕ, пунктиром звірка зі старим
            frags.append(arrow(lblx + bw / 2, y, newx - 90, 200, color="#d68910", sw=1.8))
            frags.append(line(lblx + bw / 2, y + 10, oldx - 90, 330, color="#a1887f", sw=1.2, dash="3 4"))

    frags.append(text(W / 2, 440,
                      "двері для клієнта одні й ті самі; за дверима перехоплювач тихо пересуває можливість зі старого в нове, по одній",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "interceptor.svg"), W, H, *frags)


def fig_risk_curves():
    """Дві криві ризику в часі: великий вибух (стрибок наприкінці) vs фікус (рівний струмочок)."""
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 30,
                      "Куди йде ризик у часі: один страшний стрибок проти рівного струмочка",
                      size=16, bold=True))

    ox, oy = 110, 380      # початок осей
    ax_w, ax_h = 720, 300
    # осі
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(arrow(ox + ax_w, oy, ox + ax_w + 20, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    frags.append(arrow(ox, oy - ax_h, ox, oy - ax_h - 20, color=LINE, sw=2))
    frags.append(text(ox + ax_w / 2, oy + 34, "час →", size=12, color=MUTED, italic=True))
    frags.append(mtext(ox - 58, oy - ax_h / 2, "ризик,\nщо все\nзламається", size=11, color=MUTED))

    # ── велика-вибух: майже 0, тоді різкий пік у день Х ──
    import math
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        # плаский низ, потім експ-пік біля 0.85
        if t < 0.8:
            v = 0.06 + 0.04 * t
        else:
            v = 0.09 + 0.9 * math.exp(-((t - 0.9) ** 2) / 0.0016)
        v = min(v, 1.0)
        x = ox + t * ax_w
        y = oy - v * ax_h
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), POS))
    frags.append(text(ox + 0.9 * ax_w, oy - 0.98 * ax_h - 6, "великий вибух", size=12, bold=True, color=POS))
    frags.append(mtext(ox + 0.62 * ax_w, oy - 0.5 * ax_h,
                       "місяці тиші —\nувесь ризик зібрано\nв один день перемикання", size=10.5, color=POS, bold=True))

    # ── фікус: невисокий рівний струмочок ──
    pts2 = []
    for i in range(0, 101):
        t = i / 100.0
        v = 0.16 + 0.05 * math.sin(t * 12) * (1 - t)   # дрібні брижі, згасають
        x = ox + t * ax_w
        y = oy - v * ax_h
        pts2.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts2), FIELD))
    frags.append(text(ox + 0.2 * ax_w, oy - 0.30 * ax_h, "фікус (по кроку)", size=12, bold=True, color=FIELD))
    frags.append(mtext(ox + 0.30 * ax_w, oy - 0.10 * ax_h,
                       "малий ризик на кожен крок —\nзламалось, відкотив один крок", size=10.5, color=FIELD, bold=True))

    frags.append(text(W / 2, 448,
                      "великий вибух відкладає весь ризик на день Х; фікус розмінює його на дрібні кроки, кожен із яких можна відкотити",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "risk-curves.svg"), W, H, *frags)


def fig_naming_arc():
    """Хроніка назви: спостереження фікуса (2001) → перший запис 'Strangler
    Application' (29.06.2004) → тихе перейменування на 'Strangler Fig Application'.
    Три віхи на одній лінії часу, третя показує, як 'Fig' повертає метафору."""
    W, H = 1000, 360
    frags = []
    frags.append(text(W / 2, 30,
                      "Як народжувалася й мінялася назва — три віхи на лінії часу",
                      size=16, bold=True))

    ax_y = 150
    x0, x1 = 90, 910
    frags.append(line(x0, ax_y, x1, ax_y, color=LINE, sw=2))
    frags.append(arrow(x1, ax_y, x1 + 20, ax_y, color=LINE, sw=2))

    marks = [
        (180, "2001", "Квінсленд, Австралія",
         "Фаулер бачить\nфікуси-душителі\nв дощовому лісі", NEG, "eaf0fd", "up"),
        (490, "29.06.2004", "запис у bliki",
         "«Strangler\nApplication» —\nзастосунок-душитель", INK, "f4f6f8", "down"),
        (800, "згодом", "тихе перейменування",
         "«Strangler Fig\nApplication» —\n«Fig» вертає фікус", FIELD, "d7efd7", "up"),
    ]
    for x, yr, sub, note, col, fill, side in marks:
        frags.append(circle(x, ax_y, 8, fill=col, stroke=col, sw=2))
        # рік — завжди над віссю, близько до крапки
        frags.append(text(x, ax_y - 16, yr, size=14, bold=True, color=col))
        frags.append(text(x, ax_y + 26, sub, size=10.5, color=MUTED, italic=True))
        # виносний блок-нотатка: угору або вниз, щоб не налазив на сусідів
        if side == "up":
            b, bw, bh = textbox(x, ax_y - 78, note, size=10.5, min_w=170,
                                fill="#" + fill, stroke=col)
            frags.append(b)
            frags.append(line(x, ax_y - 26, x, ax_y - 78 + bh / 2, color=col, sw=1.2, dash="3 3"))
        else:
            b, bw, bh = textbox(x, ax_y + 82, note, size=10.5, min_w=170,
                                fill="#" + fill, stroke=col)
            frags.append(b)
            frags.append(line(x, ax_y + 40, x, ax_y + 82 - bh / 2, color=col, sw=1.2, dash="3 3"))

    frags.append(text(W / 2, 340,
                      "спершу — просто «душитель»; згодом «Fig» повертає в назву дерево, а з ним і сенс метафори",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "naming-arc.svg"), W, H, *frags)


def fig_migration_ladder():
    """Драбина переїзду можливості: п'ять щаблів зі зростанням довіри
    (усе старе → тінь → canary 1% → 25% → усі), і окрема стрілка відкату
    з будь-якого щабля назад на перевірене старе. Трійка target/percent/shadow
    підписана під кожним щаблем."""
    W, H = 1120, 470
    frags = []
    frags.append(text(W / 2, 30,
                      "Переїзд можливості — драбина щаблів, не стрибок; будь-який щабель оборотний",
                      size=16, bold=True))

    # п'ять щаблів: (підпис, target, percent, shadow, зростання рівня)
    steps = [
        ("усе старе",   "legacy",  "0",   "off"),
        ("тінь увімк.", "legacy",  "0",   "on"),
        ("canary 1%",   "service", "1",   "on"),
        ("canary 25%",  "service", "25",  "on"),
        ("усі на новому", "service", "100", "off"),
    ]
    n = len(steps)
    left, right = 90, W - 60
    span = (right - left) / n
    bw = span - 34            # ширша клітина з запасом, щоб підписи не тислися
    base = 380                # низ найнижчого щабля
    rise = 46                 # на скільки кожен щабель вищий
    box_h = 74
    tops = []
    for i, (cap, tgt, pct, sh) in enumerate(steps):
        cx = left + span * i + span / 2
        top = base - i * rise - box_h
        tops.append((cx, top))
        col = FIELD if tgt == "service" else "#8a6d3b"
        fill = "#eafaf1" if tgt == "service" else "#f4ece0"
        frags.append(rect(cx - bw / 2, top, bw, box_h, fill=fill, stroke=col, sw=2, rx=8))
        frags.append(text(cx, top + 22, cap, size=12, bold=True, color=col))
        frags.append(mtext(cx, top + 40,
                           "target=%s\npercent=%s  shadow=%s" % (tgt, pct, sh),
                           size=9.5, color=INK, lh=1.25))
        # тонка сходинка-підмостка під клітиною
        frags.append(line(cx - bw / 2, top + box_h, cx + bw / 2, top + box_h, color=col, sw=1))
        # стрілка підйому на наступний щабель
        if i > 0:
            px, ptop = tops[i - 1]
            frags.append(arrow(px + bw / 2, ptop + box_h - 6,
                               cx - bw / 2, top + box_h - 6, color=MUTED, sw=1.6))

    frags.append(text(W / 2, base + 6,
                      "між щаблями — погляд на метрику розбіжності; угору лише коли тінь чиста",
                      size=11.5, color=MUTED, italic=True))

    # окрема червона дуга відкату: з верхнього щабля назад на найнижчий
    tcx, ttop = tops[-1]
    fcx, ftop = tops[0]
    arc_y = base + 46
    frags.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" '
                 'fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (tcx, ttop + box_h + 4, tcx, arc_y + 30,
                    fcx, arc_y + 30, fcx, ftop + box_h + 4, POS))
    frags.append(text(W / 2, arc_y + 26, "ВІДКАТ одним рядком конфігу — з будь-якого щабля на старе",
                      size=12, bold=True, color=POS))

    render(os.path.join(IMG, "migration-ladder.svg"), W, H, *frags)


def fig_dual_write_outbox():
    """Правильний запис проти наївного подвійного. Дві фази-панелі:
    зверху істина в старій базі (PUT + outbox в одній транзакції, ретранслятор
    наздоганяє нову), знизу істина в новій (PUT у нову, зворотний струмок у стару
    на випадок відкату). Збоку — червона нота про наївний подвійний запис."""
    W, H = 1140, 560
    frags = []
    frags.append(text(W / 2, 30,
                      "Запис несиметричний: одна база — власник, друга наздоганяє журналом (outbox)",
                      size=16, bold=True))

    def db_box(cx, cy, title, col, fill):
        b, bw, bh = textbox(cx, cy, title, size=12, min_w=180, bold=True,
                            fill=fill, stroke=col, color=col)
        return b, bw, bh

    # ── Фаза 1 (зверху): істина в СТАРІЙ ──
    y1 = 120
    frags.append(text(160, y1 - 42, "Фаза: істина в старій базі", size=13, bold=True, color="#8a6d3b"))
    put1, pw, _ = textbox(150, y1, "PUT профілю", size=11, min_w=130, fill="#eaf0fd", stroke=NEG)
    frags.append(put1)
    # стара база + outbox як одна транзакція (спільна пунктирна рамка)
    old_cx = 470
    frags.append('<rect x="%.0f" y="%.0f" width="300" height="120" rx="12" '
                 'fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 5"/>'
                 % (old_cx - 150, y1 - 60, "#8a6d3b"))
    frags.append(text(old_cx, y1 - 44, "одна транзакція однієї бази", size=10,
                      color="#8a6d3b", italic=True))
    ob1, obw, _ = db_box(old_cx - 74, y1 + 4, "стара\nusers", "#8a6d3b", "#f4ece0")
    frags.append(ob1)
    obx1, obxw, _ = db_box(old_cx + 84, y1 + 4, "outbox\n(слід зміни)", "#b9770e", "#fff2d6")
    frags.append(obx1)
    frags.append(arrow(150 + pw / 2, y1, old_cx - 150, y1, color=NEG, sw=1.8))
    # ретранслятор → нова база
    new_cx = 980
    nb1, nbw, _ = db_box(new_cx, y1 + 4, "нова\nprofiles", FIELD, "#eafaf1")
    frags.append(nb1)
    frags.append(arrow(old_cx + 84 + obxw / 2, y1 + 4, new_cx - nbw / 2, y1 + 4,
                       color=FIELD, sw=1.8))
    frags.append(mtext((old_cx + 84 + new_cx) / 2, y1 - 20,
                       "ретранслятор:\nназдоганяє, ідемпотентно", size=10, color=FIELD, bold=True))

    # роздільник фаз
    frags.append(line(80, 300, W - 80, 300, color=LINE, sw=1, dash="2 5"))

    # ── Фаза 2 (знизу): істина в НОВІЙ ──
    y2 = 400
    frags.append(text(160, y2 - 42, "Фаза: істина в новій базі", size=13, bold=True, color=FIELD))
    put2, pw2, _ = textbox(150, y2, "PUT профілю", size=11, min_w=130, fill="#eaf0fd", stroke=NEG)
    frags.append(put2)
    nb2, nbw2, _ = db_box(new_cx, y2, "нова\nprofiles", FIELD, "#eafaf1")
    frags.append(nb2)
    frags.append(arrow(150 + pw2 / 2, y2, new_cx - nbw2 / 2, y2, color=NEG, sw=1.8))
    # зворотний струмок у стару
    ob2, obw2, _ = db_box(old_cx, y2, "стара\nusers", "#8a6d3b", "#f4ece0")
    frags.append(ob2)
    frags.append(arrow(new_cx - nbw2 / 2, y2 + 18, old_cx + obw2 / 2, y2 + 18,
                       color="#8a6d3b", sw=1.6))
    frags.append(mtext((old_cx + new_cx) / 2, y2 + 46,
                       "зворотний струмок:\nстара свіжа на випадок відкату",
                       size=10, color="#8a6d3b", bold=True))

    # ── червона нота: наївний подвійний запис ──
    note, ntw, _ = textbox(W / 2, 528,
                           "наївний подвійний запис — обробник пише синхронно В ОБИДВІ бази — копії розходяться",
                           size=11, min_w=0, fill="#fdecea", stroke=POS, color=POS, bold=True)
    frags.append(note)

    render(os.path.join(IMG, "dual-write-outbox.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_fig_over_host()
    fig_interceptor()
    fig_risk_curves()
    fig_naming_arc()
    fig_migration_ladder()
    fig_dual_write_outbox()
    print("ok")
