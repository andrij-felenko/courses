# -*- coding: utf-8 -*-
"""Фігури до теми «Антиаліасинговий фільтр» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  folding-time.svg   — швидку синусоїду рідко відлічили: відліки малюють зовсім іншу, повільну
  spectrum-fold.svg  — частоти вище fN «загортаються» назад у смугу й накладаються на сигнал
  transition-band.svg— що має зробити фільтр: пропустити смугу, прибити вище fN; вузький перехід — конфлікт
  oversample.svg     — вища частота відліків розсуває fN: між сигналом і fN з'являється місце для пологого фільтра
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def folding_time():
    """Швидка синусоїда, відліки рідкі: точки лягають так, що читаються як повільна хвиля-двійник."""
    W, H = 720, 340
    p = []
    x0, x1 = 70, 650
    midy = 165
    amp = 78
    # справжня швидка синусоїда (багато періодів)
    fast = []
    N = 400
    cycles_fast = 9.0
    for k in range(N + 1):
        xx = x0 + (x1 - x0) * k / N
        ph = 2 * math.pi * cycles_fast * k / N
        fast.append((xx, midy - math.sin(ph) * amp))
    d = "M" + " L".join("%.1f %.1f" % q for q in fast)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, NEG))

    # моменти відліку — рідкі (трохи більше за один на період → з'являється повільний двійник)
    nsamp = 10
    samp_pts = []
    for k in range(nsamp + 1):
        frac = k / nsamp
        xx = x0 + (x1 - x0) * frac
        ph = 2 * math.pi * cycles_fast * frac
        yy = midy - math.sin(ph) * amp
        samp_pts.append((xx, yy))
        p.append(line(xx, midy + amp + 14, xx, yy, color=MUTED, sw=1, dash="2 3"))
        p.append(circle(xx, yy, 4.5, fill=POS, stroke=POS, sw=1))

    # повільна хвиля-двійник крізь самі відліки (аліас)
    d2 = "M" + " L".join("%.1f %.1f" % q for q in samp_pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7 4"/>' % (d2, POS))

    p.append(text(x0 + 130, midy - amp - 18, "справжній сигнал (швидкий)", size=12, color=NEG, anchor="start"))
    p.append(text(x0 + 250, midy + amp + 40, "моменти відліку", size=11, color=MUTED, anchor="start"))
    p.append(text(x1 - 200, midy + amp - 4, "хвиля-привид (повільна)", size=12, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 312,
                      "Відлічили рідше, ніж двічі за період, — і ті самі точки чесно лягають\n"
                      "на зовсім іншу, повільну хвилю. Це і є аліас: підробка, нечутна від правди.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'folding-time.svg'), W, H, *p,
           title="Звідки береться привид: рідкі відліки малюють чужу повільну хвилю")


def spectrum_fold():
    """Спектр: усе вище fN дзеркалиться навколо fN і падає назад у смугу, накладаючись на сигнал."""
    W, H = 720, 360
    p = []
    ox, oy = 70, 250
    axw = 580
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))            # вісь частоти
    p.append(arrow(ox, oy, ox, oy - 180, color=INK, sw=2))           # вісь рівня
    p.append(text(ox + axw - 6, oy + 22, "частота", size=12, color=INK, anchor="end"))

    # позначки fmax, fN, fs
    fmax_x = ox + 150
    fN_x = ox + 270
    fs_x = ox + 510
    for xx, lbl, col in [(fmax_x, "fmax", FIELD), (fN_x, "fN = fs/2", POS), (fs_x, "fs", MUTED)]:
        p.append(line(xx, oy, xx, oy + 7, color=col, sw=2))
        p.append(text(xx, oy + 24, lbl, size=12, bold=True, color=col))
    # вертикаль-дзеркало на fN
    p.append(line(fN_x, oy, fN_x, oy - 170, color=POS, sw=1.4, dash="4 4"))

    # корисний сигнал: трикутник у смузі 0..fmax
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eafaf0" stroke="%s" stroke-width="2"/>'
             % (ox + 4, oy, fmax_x, oy - 120, fmax_x, oy, FIELD))
    p.append(text(ox + 60, oy - 70, "корисний", size=12, bold=True, color=FIELD))
    p.append(text(ox + 60, oy - 54, "сигнал", size=12, bold=True, color=FIELD))

    # завада вище fN: горбик праворуч від fN
    hf_c = fN_x + 95
    p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (hf_c - 45, oy, hf_c, oy - 95, hf_c + 45, oy, POS))
    p.append(text(hf_c, oy - 108, "завада вище fN", size=12, bold=True, color=POS))

    # її дзеркальне відображення — назад у смугу (аліас)
    al_c = fN_x - 95
    p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>'
             % (al_c - 45, oy, al_c, oy - 95, al_c + 45, oy, POS))
    p.append(text(al_c, oy - 108, "її аліас", size=12, bold=True, color=POS))
    # дуга «загортання» навколо fN
    p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (hf_c, oy - 95, fN_x, oy - 150, al_c, oy - 95, MUTED))
    p.append(text(fN_x, oy - 156, "загортається навколо fN", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 332,
                      "Усе, що сидить вище fN, після відліків відбивається навколо fN і падає назад у смугу.\n"
                      "Там воно лягає поверх корисного сигналу — і вже не відокремиться нічим.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'spectrum-fold.svg'), W, H, *p,
           title="Загортання спектра: частоти вище fN падають назад на сигнал")


def transition_band():
    """Маска фільтра: пропустити до fmax, прибити від fN; вузький перехід fmax→fN — у цьому весь конфлікт."""
    W, H = 720, 390
    p = []
    ox, oy = 70, 280
    axw = 580
    axh = 220
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox + axw - 6, oy + 22, "частота", size=12, color=INK, anchor="end"))
    p.append(text(ox - 46, oy - axh + 16, "підси-", size=11, color=MUTED, anchor="start"))
    p.append(text(ox - 46, oy - axh + 30, "лення", size=11, color=MUTED, anchor="start"))

    fmax_x = ox + 180
    fN_x = ox + 300
    top_y = oy - 170      # рівень пропускання
    bot_y = oy - 24       # рівень придушення (підлога)

    # смуга пропускання
    p.append(rect(ox + 2, top_y, fmax_x - ox - 2, oy - top_y, fill="#eafaf0", stroke="none", sw=0))
    p.append(line(ox + 2, top_y, fmax_x, top_y, color=FIELD, sw=2.4))
    p.append(text((ox + fmax_x) / 2, top_y - 10, "пропустити", size=12, bold=True, color=FIELD))
    p.append(text((ox + fmax_x) / 2, oy - 8, "смуга сигналу", size=11, color=MUTED))

    # смуга затримання (стоп)
    p.append(rect(fN_x, bot_y, ox + axw - 40 - fN_x, oy - bot_y, fill="#fdecea", stroke="none", sw=0))
    p.append(line(fN_x, bot_y, ox + axw - 40, bot_y, color=POS, sw=2.4))
    p.append(text((fN_x + ox + axw - 40) / 2, bot_y - 10, "прибити (стоп)", size=12, bold=True, color=POS))

    # ідеальний (цеглина) і реальний (похилий) спади
    p.append(line(fmax_x, top_y, fmax_x, bot_y, color=MUTED, sw=1.6, dash="4 4"))   # ідеал: вертикаль
    p.append(text(fmax_x - 4, top_y - 26, "ідеал:", size=11, color=MUTED, anchor="end"))
    p.append(text(fmax_x - 4, top_y - 12, "стінка", size=11, color=MUTED, anchor="end"))
    # реальний пологий спад фільтра
    p.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (fmax_x, top_y, fmax_x + 70, top_y + 30, ox + axw - 60, bot_y + 6, NEG))
    p.append(text(fN_x + 70, top_y + 40, "реальний фільтр:", size=12, bold=True, color=NEG, anchor="start"))
    p.append(text(fN_x + 70, top_y + 56, "пологий спад", size=12, bold=True, color=NEG, anchor="start"))

    # позначки осі + перехідна смуга
    for xx, lbl, col in [(fmax_x, "fmax", FIELD), (fN_x, "fN", POS)]:
        p.append(line(xx, oy, xx, oy + 7, color=col, sw=2))
        p.append(text(xx, oy + 24, lbl, size=12, bold=True, color=col))
    # двостороння стрілка перехідної смуги
    ty = oy + 44
    p.append(line(fmax_x, ty, fN_x, ty, color=INK, sw=1.6))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fmax_x + 7, ty - 4, fmax_x + 7, ty + 4, fmax_x, ty, INK))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fN_x - 7, ty - 4, fN_x - 7, ty + 4, fN_x, ty, INK))
    p.append(text((fmax_x + fN_x) / 2, ty + 17, "перехідна смуга — увесь конфлікт", size=12, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 362,
                      "Фільтр мусить устигнути впасти від «пропустити» до «прибити» на проміжку fmax → fN.\n"
                      "Вузький проміжок = крутий спад = фільтр високого порядку. Розсунути їх — головна хитрість.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'transition-band.svg'), W, H, *p,
           title="Що має зробити фільтр: пропустити смугу, прибити вище fN")


def oversample():
    """Дві однакові смуги сигналу, дві частоти відліку: вища fs відсуває fN далеко — перехід широкий."""
    W, H = 720, 380
    p = []

    def panel(x0, fs_x_rel, title, gentle):
        out = []
        oy = 250
        axw = 300
        out.append(arrow(x0, oy, x0 + axw, oy, color=INK, sw=2))
        out.append(arrow(x0, oy, x0, oy - 150, color=INK, sw=2))
        top_y = oy - 120
        fmax_x = x0 + 70           # та сама смуга сигналу в обох панелях
        fN_x = x0 + fs_x_rel
        # смуга сигналу (однакова)
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eafaf0" stroke="%s" stroke-width="1.8"/>'
                   % (x0 + 2, oy, fmax_x, top_y, fmax_x, oy, FIELD))
        out.append(text((x0 + fmax_x) / 2, top_y - 8, "сигнал", size=11, bold=True, color=FIELD))
        # позначки fmax, fN
        out.append(line(fmax_x, oy, fmax_x, oy + 7, color=FIELD, sw=2))
        out.append(text(fmax_x, oy + 22, "fmax", size=11, bold=True, color=FIELD))
        out.append(line(fN_x, oy, fN_x, oy + 7, color=POS, sw=2))
        out.append(text(fN_x, oy + 22, "fN", size=11, bold=True, color=POS))
        out.append(line(fN_x, oy, fN_x, oy - 135, color=POS, sw=1.2, dash="4 4"))
        # спад фільтра: крутий чи пологий
        if gentle:
            out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                       % (fmax_x, top_y, (fmax_x + fN_x) / 2 + 20, oy - 50, fN_x, oy - 6, NEG))
        else:
            out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                       % (fmax_x, top_y, fmax_x + 12, oy - 30, fN_x, oy - 6, NEG))
        # перехідна смуга
        ty = oy + 40
        out.append(line(fmax_x, ty, fN_x, ty, color=INK, sw=1.4))
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fmax_x + 6, ty - 4, fmax_x + 6, ty + 4, fmax_x, ty, INK))
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>' % (fN_x - 6, ty - 4, fN_x - 6, ty + 4, fN_x, ty, INK))
        out.append(text(x0 + axw / 2 - 20, oy - 138, title, size=13, bold=True))
        return out

    p += panel(60, 60, "звичайна fs: тісно", False)
    p.append(text(190, 318, "вузький перехід → крутий фільтр", size=11, color=POS))
    p += panel(400, 230, "вища fs: просторо", True)
    p.append(text(560, 318, "широкий перехід → пологий фільтр", size=11, color=FIELD))

    b, _, _ = textbox(W / 2, 348,
                      "Підняти частоту відліків — і fN їде далеко вправо від сигналу. Між ними з'являється\n"
                      "широка перехідна смуга, тож аналоговий фільтр може бути простим і пологим.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'oversample.svg'), W, H, *p,
           title="Надлишкові відліки розсувають fN — і фільтр можна взяти простіший")


def sampling_timeline():
    """Чотири незалежні внески 1915–1949 на осі часу, усі сходяться до однієї межі fs > 2B."""
    W, H = 760, 470
    p = []
    ox, oy = 60, 116          # вісь часу (вгорі)
    axw = 640
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(text(ox + axw - 4, oy - 12, "час", size=12, color=INK, anchor="end"))

    def xof(year):
        return ox + 20 + (year - 1912) * (axw - 60) / (1953 - 1912)

    for yr in (1915, 1928, 1933, 1949):
        xx = xof(yr)
        p.append(line(xx, oy - 6, xx, oy + 6, color=MUTED, sw=1.4))
        p.append(text(xx, oy - 14, str(yr), size=11, color=MUTED))

    cw, ch = 168, 64
    row_hi = oy + 24          # верхній ряд карток (під віссю)
    row_lo = oy + 116         # нижній ряд карток
    # картки внесків — почергово в два ряди, щоб не злипались
    nodes = [
        (1915, FIELD, "Е. Т. Уїттекер", "Единбург", "формула sin(x)/x", "математичний апарат", row_hi),
        (1928, NEG,   "Г. Найквіст",    "Bell Labs", "межа 2B імпульсів", "число, передавання", row_lo),
        (1933, POS,   "В. Котельников", "Москва",    "ПЕРШЕ строге", "формулювання теореми", row_hi),
        (1949, INK,   "К. Шеннон",      "Bell Labs", "повне доведення", "+ теорія інформації", row_lo),
    ]
    cards = []
    for yr, col, name, place, l1, l2, cy in nodes:
        xx = xof(yr)
        cx = max(ox + cw / 2 + 2, min(xx, ox + axw - cw / 2 - 2))
        cards.append((cx, cy, col))
        # лінія від осі до верхнього краю картки
        p.append(line(xx, oy + 6, cx, cy, color=col, sw=1.6, dash="3 3"))
        p.append(circle(xx, oy, 4, fill=col, stroke=col))
        p.append(rect(cx - cw / 2, cy, cw, ch, fill="#ffffff", stroke=col, sw=2, rx=8))
        p.append(text(cx, cy + 17, name, size=13, bold=True, color=col))
        p.append(text(cx, cy + 32, place, size=10, color=MUTED))
        p.append(text(cx, cy + 47, l1, size=11, color=INK))
        p.append(text(cx, cy + 60, l2, size=11, color=INK))

    # підсумкова межа — усі стрілки сходяться сюди
    by = row_lo + ch + 56     # центр підсумкового блоку
    bw, bh = 150, 50
    p.append(rect(W / 2 - bw / 2, by - bh / 2, bw, bh, fill="#fff8e1", stroke=INK, sw=2.4, rx=10))
    p.append(text(W / 2, by - 3, "fs > 2B", size=18, bold=True, color=INK))
    p.append(text(W / 2, by + 16, "одна межа на всіх", size=11, color=MUTED))
    # стрілки від нижнього краю кожної картки до верху підсумкового блоку
    for cx, cy, col in cards:
        sx, sy = cx, cy + ch
        tx = W / 2 + (cx - W / 2) * 0.16
        p.append(arrow(sx, sy, tx, by - bh / 2 - 4, color=MUTED, sw=1.3))

    bb, _, _ = textbox(W / 2, H - 26,
                       "Чотири людини, три країни, різні коридори — формула, число, перше формулювання, доведення.\n"
                       "Ніхто ні в кого не вкрав: більшість працювала, не знаючи про решту. Звідси й назва WKS.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(bb)
    render(os.path.join(OUT, 'sampling-timeline.svg'), W, H, *p,
           title="Теорема відліків: чотири незалежні внески сходяться до однієї межі")


if __name__ == '__main__':
    folding_time()
    spectrum_fold()
    transition_band()
    oversample()
    sampling_timeline()
    print("OK: 5 figures ->", OUT)
