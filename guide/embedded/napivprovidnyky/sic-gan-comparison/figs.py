# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def poly(points, fill="none", stroke=INK, sw=2.0):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (pts, fill, stroke, sw))


# ── bandgap: чому ширша заборонена зона = вища робоча напруга й температура ─────
# Ідея: усе тримається на одному числі — ширині забороненої зони. Ширша зона →
# міцніший кристал (важче пробити полем, важче «розхитати» теплом). Звідси і
# критичне поле, і робоча температура. Показуємо три сходинки пліч-о-пліч.

def fig_bandgap():
    W, H = 820, 440
    frags = []

    mats = [
        ("Si",  1.12, "#9aa7b8", 60),
        ("SiC", 3.26, POS,       320),
        ("GaN", 3.40, NEG,       580),
    ]
    base_y, top_y = 370, 100         # рівні валентної зони й стелі діаграми
    span = top_y - base_y            # від'ємний (вгору)
    eg_max = 3.6
    panel_w = 200

    for name, eg, col, x in mats:
        # валентна зона (низ) — суцільна смуга
        frags.append(rect(x, base_y, panel_w, 24, fill="#e9edf2", stroke=MUTED, sw=1.4, rx=3))
        frags.append(text(x + panel_w / 2, base_y + 17, "валентна зона", size=9, color=MUTED))
        # зона провідності (верх) — на висоті, пропорційній Eg
        cb_y = base_y + span * (eg / eg_max)
        frags.append(rect(x, cb_y - 24, panel_w, 24, fill="#dfeae0" if col != "#9aa7b8" else "#eceff3",
                          stroke=col, sw=1.8, rx=3))
        frags.append(text(x + panel_w / 2, cb_y - 7, "зона провідності", size=9, color=col, bold=True))
        # стрілка-проміжок
        midx = x + panel_w / 2
        frags.append(line(midx, base_y, midx, cb_y, color=col, sw=2.4, dash="5,4"))
        frags.append(text(x + panel_w / 2, (base_y + cb_y) / 2 + 4,
                          "%.2f еВ" % eg, size=13, color=col, bold=True))
        # підпис матеріалу
        frags.append(text(x + panel_w / 2, base_y + 52, name, size=18, color=col, bold=True))

    # висновок
    frags.append(text(W / 2, 422,
                      "ширша зона → електрон важче «перекинути» полем чи теплом → вища напруга пробою й вища робоча T",
                      size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "bandgap.svg"), W, H, *frags,
           title="Заборонена зона Si, SiC, GaN: чому широка зона дає міцніший прилад")


# ── thin-drift: чому той самий вольтаж тримає набагато тонший і менш опірний шар ─
# Ідея: блокувальну напругу тримає збіднений дрейфовий шар. Поле в ньому не може
# перевищити критичне. У SiC/GaN критичне поле ~10× вище → шар можна зробити ~10×
# тонший на ту саму напругу. Тонший і дужче легований шар = набагато менший опір.

def fig_thin_drift():
    W, H = 860, 440
    frags = []

    # спільна вісь: напруга однакова (площа трикутника поля = напруга)
    def panel(x, name, col, width_px, ecrit_label, thick_label):
        out = []
        top, bot = 90, 300
        # стовп напівпровідника (дрейфовий шар) — висота фіксована, ширина — товщина
        out.append(rect(x, top, width_px, bot - top, fill="#eef1f6" if col == "#9aa7b8" else "#eaf3ec",
                        stroke=col, sw=2, rx=4))
        out.append(text(x + width_px / 2, top - 10, name, size=15, color=col, bold=True))
        out.append(text(x + width_px / 2, bot + 20, thick_label, size=11, color=col, bold=True))
        # трикутник поля поверх (вершина = критичне поле, біля переходу)
        ex = x + width_px
        out.append(poly([(x, bot), (ex, bot), (ex, top + 30)], fill="none", stroke=POS, sw=2.4))
        out.append(text(ex - 6, top + 44, ecrit_label, size=10, color=POS, anchor="end", bold=True))
        out.append(text(x + 6, bot - 8, "глибина шару", size=8, color=MUTED, anchor="start"))
        return "".join(out)

    frags.append(panel(70,  "Si",  "#9aa7b8", 240, "E_крит ≈ 0.3 МВ/см", "товстий слабколегований шар"))
    frags.append(panel(470, "SiC", POS,        62, "E_крит ≈ 3 МВ/см", "тонкий ~×10 шар"))

    # дужка «та сама блокувальна напруга»
    frags.append(text(W / 2, 350, "площа під полем = блокувальна напруга — однакова в обох",
                      size=11, color=INK, bold=True))
    frags.append(rect(60, 366, 740, 56, fill="#f4f7f4", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(W / 2, 390,
                      "поле в шарі не сміє перейти критичне; у SiC/GaN воно ~×10 вище, тож шар роблять ~×10 тоншим,",
                      size=11, color=INK, bold=True))
    frags.append(text(W / 2, 410,
                      "а легують ~×10 щільніше — а тонкий і дужче легований шар має радикально менший опір.",
                      size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thin-drift.svg"), W, H, *frags,
           title="Чому широкозонний прилад на ту саму напругу тонший і менш опірний")


# ── no-body-diode: ключова практична відмінність GaN — нема паразитного діода ──
# Ідея: у кремнієвому MOSFET вбудований body-діод проводить назад, але «вмикається»
# повільно (зворотне відновлення) — джерело втрат. GaN HEMT діода не має зовсім:
# назад проводить сам канал. Немає заряду відновлення — але вище падіння в реверсі.

def fig_no_body_diode():
    W, H = 860, 400
    frags = []

    # ── ліва панель: Si MOSFET з body-діодом ──
    frags.append(rect(40, 60, 380, 300, fill="#eef1f6", stroke="#7d8aa0", sw=2.2, rx=12))
    frags.append(text(230, 86, "Кремнієвий MOSFET", size=14, color="#5b6880", bold=True))
    # символ транзистора (спрощено)
    frags.append(line(150, 120, 150, 280, color=INK, sw=2.6))            # канал
    frags.append(text(150, 110, "D", size=11, color=INK, bold=True))
    frags.append(text(150, 296, "S", size=11, color=INK, bold=True))
    frags.append(line(110, 200, 150, 200, color=INK, sw=2))               # затвор
    frags.append(text(96, 204, "G", size=11, color=INK, anchor="end", bold=True))
    # body-діод збоку
    frags.append(line(210, 120, 210, 280, color=POS, sw=2))
    frags.append(line(150, 120, 210, 120, color=POS, sw=2))
    frags.append(line(150, 280, 210, 280, color=POS, sw=2))
    frags.append(poly([(200, 192), (220, 192), (210, 208)], fill=POS, stroke=POS, sw=1))
    frags.append(line(200, 208, 220, 208, color=POS, sw=2.2))
    frags.append(text(248, 200, "вбудований", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(248, 216, "body-діод", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(230, 318, "проводить назад, але має", size=10, color=INK))
    frags.append(text(230, 336, "ЗАРЯД ВІДНОВЛЕННЯ → втрати", size=11, color=POS, bold=True))

    # ── права панель: GaN HEMT без діода ──
    frags.append(rect(440, 60, 380, 300, fill="#eaeefc", stroke=NEG, sw=2.2, rx=12))
    frags.append(text(630, 86, "GaN HEMT", size=14, color=NEG, bold=True))
    frags.append(line(560, 120, 560, 280, color=INK, sw=2.6))
    frags.append(text(560, 110, "D", size=11, color=INK, bold=True))
    frags.append(text(560, 296, "S", size=11, color=INK, bold=True))
    frags.append(line(520, 200, 560, 200, color=INK, sw=2))
    frags.append(text(506, 204, "G", size=11, color=INK, anchor="end", bold=True))
    # перекреслене місце діода
    frags.append(circle(640, 200, 26, fill="none", stroke="#c0392b", sw=2.2))
    frags.append(line(622, 182, 658, 218, color="#c0392b", sw=2.2))
    frags.append(text(688, 196, "діода", size=10, color="#c0392b", anchor="start", bold=True))
    frags.append(text(688, 212, "немає", size=10, color="#c0392b", anchor="start", bold=True))
    frags.append(text(630, 318, "назад проводить сам канал:", size=10, color=INK))
    frags.append(text(630, 336, "0 заряду відновлення, але вище падіння", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "no-body-diode.svg"), W, H, *frags,
           title="Si MOSFET має body-діод (повільний у реверсі); GaN HEMT — не має зовсім")


# ── where-each: коротка карта рішення — де кремній, де SiC, де GaN ─────────────
# Ідея: жоден не «найкращий» — кожен виграє у своєму куті простору «напруга ×
# частота». Зводимо в одну картину: вісь напруги (вертикаль) × частоти (горизонт).

def fig_where_each():
    W, H = 820, 470
    frags = []

    # осі
    x0, y0 = 110, 390
    x1, y1 = 760, 70
    frags.append(line(x0, y0, x1, y0, color=INK, sw=2))      # горизонт — частота
    frags.append(line(x0, y0, x0, y1, color=INK, sw=2))      # вертикаль — напруга
    frags.append(text((x0 + x1) / 2, y0 + 34, "частота перемикання →", size=12, color=INK, bold=True))
    frags.append(text(x0 - 70, (y0 + y1) / 2, "напруга →", size=12, color=INK, bold=True))
    frags.append(text(x0 - 70, (y0 + y1) / 2 + 16, "(блокувальна)", size=9, color=MUTED))

    # три зони
    # кремній: низька напруга + низька/середня частота (лівий низ і центр)
    frags.append(rect(x0 + 8, y0 - 130, 300, 122, fill="#eef1f6", stroke="#7d8aa0", sw=2, rx=10))
    frags.append(text(x0 + 158, y0 - 96, "Кремній (Si)", size=14, color="#5b6880", bold=True))
    frags.append(text(x0 + 158, y0 - 74, "до ~600 В, до сотень кГц", size=10, color="#5b6880"))
    frags.append(text(x0 + 158, y0 - 54, "дешево, зріло, скрізь", size=10, color=MUTED, italic=True))

    # GaN: низька-середня напруга + ВИСОКА частота (правий низ/середина)
    frags.append(rect(x0 + 330, y0 - 175, 300, 167, fill="#eaeefc", stroke=NEG, sw=2, rx=10))
    frags.append(text(x0 + 480, y0 - 145, "GaN", size=15, color=NEG, bold=True))
    frags.append(text(x0 + 480, y0 - 123, "до ~650 В, дуже висока частота", size=10, color=NEG, bold=True))
    frags.append(text(x0 + 480, y0 - 103, "малі швидкі перетворювачі,", size=10, color=INK))
    frags.append(text(x0 + 480, y0 - 85, "зарядки, LiDAR, RF", size=10, color=INK))

    # SiC: ВИСОКА напруга + середня-висока частота (верх)
    frags.append(rect(x0 + 8, y1 + 6, 622, 110, fill="#eaf3ec", stroke=POS, sw=2, rx=10))
    frags.append(text(x0 + 319, y1 + 38, "SiC (карбід кремнію)", size=15, color=POS, bold=True))
    frags.append(text(x0 + 319, y1 + 60, "сотні вольт — кіловольти, середня-висока частота, гаряче середовище", size=10, color=POS, bold=True))
    frags.append(text(x0 + 319, y1 + 80, "тяга електромобілів, сонячні інвертори, промислове живлення", size=10, color=INK))

    render(os.path.join(OUT, "where-each.svg"), W, H, *frags,
           title="Карта рішення: кремній унизу, GaN — швидкий, SiC — високовольтний")


# ── hist-timeline: дві окремі історії до силового приладу (для вставки 📜) ──────
# Ідея: SiC і GaN прийшли різними шляхами й у різний час. Дві паралельні
# доріжки на спільній осі років роблять видимим головне — між відкриттям ефекту
# й приладом у продажу лежать десятиліття, і SiC повз ~120 років, а GaN ~16.

def fig_hist_timeline():
    W, H = 880, 470
    frags = []

    # спільна вісь років: 1880 ... 2020 зліва направо
    yr0, yr1 = 1880, 2025
    xL, xR = 70, 820

    def X(year):
        return xL + (xR - xL) * (year - yr0) / (yr1 - yr0)

    # вісь часу посередині
    axis_y = 250
    frags.append(line(xL, axis_y, xR, axis_y, color=MUTED, sw=2))
    for yr in (1880, 1910, 1940, 1970, 2000, 2025):
        frags.append(line(X(yr), axis_y - 5, X(yr), axis_y + 5, color=MUTED, sw=1.5))
        frags.append(text(X(yr), axis_y + 22, str(yr), size=10, color=MUTED))

    # ── SiC — над віссю ──
    frags.append(text(xL - 4, 70, "SiC", size=16, color=POS, anchor="start", bold=True))
    sic = [
        (1891, "Ачесон", "абразив"),
        (1907, "Раунд", "світіння"),
        (1955, "Лелі", "кристал"),
        (1978, "Таїров,", "Цвєтков"),
        (2001, "діод", "Infineon"),
        (2011, "MOSFET", "Cree"),
    ]
    top_y = 96
    for i, (yr, a, b) in enumerate(sic):
        x = X(yr)
        ly = top_y + (i % 2) * 56          # дві висоти, щоб підписи не злипались
        frags.append(line(x, axis_y, x, ly + 34, color=POS, sw=1.3, dash="3,3"))
        frags.append(circle(x, axis_y, 5, fill=POS, stroke=POS, sw=1))
        frags.append(text(x, ly, str(yr), size=11, color=POS, bold=True))
        frags.append(text(x, ly + 15, a, size=9.5, color=INK))
        frags.append(text(x, ly + 28, b, size=9, color=MUTED))

    # ── GaN — під віссю ──
    frags.append(text(xL - 4, axis_y + 70, "GaN", size=16, color=NEG, anchor="start", bold=True))
    gan = [
        (1993, "Хан", "HEMT, 2DEG"),
        (2004, "Eudyna", "RF, відкритий"),
        (2009, "EPC", "силовий, закритий"),
    ]
    base_y = axis_y + 64
    for i, (yr, a, b) in enumerate(gan):
        x = X(yr)
        ly = base_y + (i % 2) * 54
        frags.append(line(x, axis_y, x, ly - 14, color=NEG, sw=1.3, dash="3,3"))
        frags.append(circle(x, axis_y, 5, fill=NEG, stroke=NEG, sw=1))
        frags.append(text(x, ly, str(yr), size=11, color=NEG, bold=True))
        frags.append(text(x, ly + 15, a, size=9.5, color=INK))
        frags.append(text(x, ly + 28, b, size=9, color=MUTED))

    # висновок унизу
    frags.append(text(W / 2, 452,
                      "між відкриттям ефекту й приладом у продажу — десятиліття: SiC повз ~120 років, GaN ~16",
                      size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *frags,
           title="Два шляхи до силового приладу: SiC і GaN на одній лінії часу")


if __name__ == "__main__":
    fig_bandgap()
    fig_thin_drift()
    fig_no_body_diode()
    fig_where_each()
    fig_hist_timeline()
    print("OK: figs written to", OUT)
