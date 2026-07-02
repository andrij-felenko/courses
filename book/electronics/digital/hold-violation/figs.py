# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольорові маркери (svgkit дає лише чорний #arrow).
MARK = ('<defs>'
        '<marker id="aInk" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '<marker id="aPos" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '<marker id="aFld" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '</defs>') % (INK, POS, FIELD)


def amark(x1, y1, x2, y2, mid="aInk", color=INK, sw=1.8):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def save(path, w, h, *frags):
    defs = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker></defs>' % LINE)
    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>' % (w, h, FONT, w, h, BG))
    parts = [head, defs, MARK]
    parts.extend(f for f in frags if f)
    parts.append("</svg>")
    import io
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return path


# ── Фігура 1: вікно hold і «занадто рання» зміна ────────────────────────────
def fig_window():
    W, H = 760, 430
    els = [text(W/2, 26, "Фронт такту й «заборонене вікно» довкола нього", size=17, bold=True)]

    x_edge = 380          # позиція фронту
    su_w, h_w = 78, 62    # ширина зон setup / hold (умовно)
    # смуга часу
    t0, t1 = 70, 700

    # ── тактовий сигнал угорі ──
    clk_y = 70
    els.append(text(48, clk_y+4, "CLK", size=13, bold=True, anchor="end"))
    # проста меандр-подібна лінія з наростанням у x_edge
    els.append(line(t0, clk_y+18, x_edge-6, clk_y+18, color=INK, sw=2.2))
    els.append(line(x_edge-6, clk_y+18, x_edge+6, clk_y-14, color=INK, sw=2.2))
    els.append(line(x_edge+6, clk_y-14, t1, clk_y-14, color=INK, sw=2.2))
    els.append(text(x_edge, clk_y-24, "↑ фронт", size=12, bold=True, color=INK))

    # ── зони setup та hold ──
    zy, zh = 120, 150
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eaf0fd" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (x_edge-su_w, zy, su_w, zh, NEG))
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % (x_edge, zy, h_w, zh, POS))
    els.append(line(x_edge, zy-6, x_edge, zy+zh+6, color=INK, sw=1.4, dash="3 3"))
    els.append(text(x_edge-su_w/2, zy-8, "setup t_su", size=12, bold=True, color=NEG))
    els.append(text(x_edge+h_w/2, zy-8, "hold t_h", size=12, bold=True, color=POS))
    els.append(text(x_edge-su_w/2, zy+zh/2, "«до»", size=11, color=NEG))
    els.append(text(x_edge+h_w/2, zy+zh/2, "«після»", size=11, color=POS))

    # ── два варіанти входу D ──
    def dwave(y, change_x, label, ok):
        col = FIELD if ok else POS
        seg = []
        seg.append(text(48, y+4, "D", size=13, bold=True, anchor="end"))
        # рівень «старий» до change_x, потім «новий»
        lo, hi = y+14, y-14
        seg.append(line(t0, lo, change_x, lo, color=col, sw=2.4))
        seg.append(line(change_x, lo, change_x, hi, color=col, sw=2.4))
        seg.append(line(change_x, hi, t1, hi, color=col, sw=2.4))
        seg.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (change_x, y, col))
        seg.append(text(change_x, y+34 if ok else y+34, label, size=11.5, bold=True, color=col))
        return "".join(seg)

    # добрий: змінюється ЗАДОВГО до вікна (ліворуч) і стоїть весь час вікна
    els.append(dwave(320, x_edge-su_w-70, "змінився завчасно — стоїть усе вікно", True))
    # поганий: змінюється ВІДРАЗУ ПІСЛЯ фронту, всередині hold
    els.append(dwave(390, x_edge+h_w-24, "змінився надто рано після фронту", False))

    # підпис-присуд
    els.append(fitbox(x_edge+h_w+26, 300, 210, 46, "порушення hold:\nдані «зірвалися» у вікні",
                       size=12, fill="#fdecea", stroke=POS, bold=True, color=POS))
    els.append(fitbox(x_edge-su_w-266, 300, 214, 46, "чисте захоплення:\nдані незмінні у вікні",
                       size=12, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))

    return save(os.path.join(OUT, "hold-window.svg"), W, H, *els)


# ── Фігура 2: перегони по короткому шляху (нова зміна доганяє фронт) ─────────
def fig_race():
    W, H = 760, 470
    els = [text(W/2, 26, "Порушення hold: нова зміна доганяє той самий фронт", size=17, bold=True)]

    # два тригери під спільним тактом, коротка логіка між ними
    fy, fh, fw = 90, 96, 108
    ax, bx = 120, 470
    def ff(x, name):
        s = rect(x, fy, fw, fh, fill=FILL, stroke=INK, sw=1.8)
        s += text(x+fw/2, fy+22, name, size=13, bold=True)
        s += text(x+12, fy+52, "D", size=12, anchor="start")
        s += text(x+fw-12, fy+52, "Q", size=12, anchor="end")
        # трикутник такту
        s += '<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6"/>' % (x+8, fy+fh-8, x+18, fy+fh-16, x+8, fy+fh-24, INK)
        return s
    els.append(ff(ax, "FF1 (джерело)"))
    els.append(ff(bx, "FF2 (приймач)"))

    # коротка комбінаційна логіка (або зовсім дріт)
    els.append(amark(ax+fw, fy+52, bx-6, fy+52, "aPos", POS, 2.2))
    els.append(fitbox((ax+fw+bx)/2-58, fy+18, 116, 30, "коротка логіка\n(мала t_logic)", size=10.5, fill="#fff7f0", stroke=POS, color=POS))

    # спільний такт до обох
    cly = fy+fh+34
    els.append(line(60, cly, 700, cly, color=INK, sw=2))
    els.append(amark(ax+8, cly, ax+8, fy+fh+2, "aInk", INK, 1.6))
    els.append(amark(bx+8, cly, bx+8, fy+fh+2, "aInk", INK, 1.6))
    els.append(text(60, cly+18, "спільний CLK — той самий фронт запускає джерело і перевіряє приймач", size=11.5, color=MUTED, anchor="start"))

    # часова діаграма внизу
    ty = 300
    t0, t1 = 120, 700
    xe = 300   # фронт
    els.append(text(70, ty-18, "у часі:", size=12, bold=True, anchor="start"))
    # фронт CLK
    els.append(line(xe, ty-8, xe, ty+150, color=INK, sw=1.4, dash="3 3"))
    els.append(text(xe, ty-16, "↑ фронт", size=11.5, bold=True))
    # вікно hold
    hw = 70
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="150" fill="#fdecea" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3"/>' % (xe, ty, hw, POS))
    els.append(text(xe+hw/2, ty-2+150+14, "вікно hold FF2", size=11, bold=True, color=POS))

    # Q джерела: старе значення тримається до xe, тоді КОРОТКО — нове (доїжджає в межах hold)
    qy = ty+40
    els.append(text(112, qy+4, "Q(FF1)", size=12, bold=True, anchor="end"))
    els.append(line(t0, qy+12, xe, qy+12, color=INK, sw=2.2))           # старе
    # clock-to-Q(min): маленька затримка після фронту
    xq = xe+26
    els.append(line(xe, qy+12, xq, qy+12, color=INK, sw=2.2))
    els.append(line(xq, qy+12, xq, qy-12, color=NEG, sw=2.4))            # перемикання
    els.append(line(xq, qy-12, t1, qy-12, color=NEG, sw=2.4))           # нове
    els.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (xq, qy, NEG))
    els.append(amark(xe+2, qy+30, xq-2, qy+30, "aInk", INK, 1.4))
    els.append(amark(xq-2, qy+30, xe+2, qy+30, "aInk", INK, 1.4))
    els.append(text((xe+xq)/2, qy+44, "t_cq(min)", size=10.5, color=MUTED))

    # вхід D приймача = Q джерела + коротка логіка → змінюється ще в межах hold-вікна
    dy = ty+108
    xd = xq+18   # + t_logic(min); усе одно всередині вікна hold (xd < xe+hw)
    els.append(text(112, dy+4, "D(FF2)", size=12, bold=True, anchor="end"))
    els.append(line(t0, dy+12, xd, dy+12, color=INK, sw=2.2))
    els.append(line(xd, dy+12, xd, dy-12, color=POS, sw=2.6))
    els.append(line(xd, dy-12, t1, dy-12, color=POS, sw=2.6))
    els.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (xd, dy, POS))
    els.append(text(xd+8, dy-18, "зміна всередині hold ✗", size=11.5, bold=True, color=POS, anchor="start"))

    els.append(fitbox(430, ty+96, 268, 44, "нове значення долетіло надто швидко —\nстерло старе перш ніж FF2 його «дотримав»",
                       size=10.5, fill="#fdecea", stroke=POS, color=POS))
    return save(os.path.join(OUT, "hold-race.svg"), W, H, *els)


# ── Фігура 3: перекіс такту (skew) та лікування затримкою ───────────────────
def fig_fix():
    W, H = 760, 340
    els = [text(W/2, 26, "Ліки: додати затримку в шлях даних, щоб зміна вийшла з вікна", size=16, bold=True)]

    t0, t1 = 90, 700
    xe = 300
    hw = 70

    def frame(yc, title, xd, ok, extra=None):
        s = [text(70, yc-30, title, size=12.5, bold=True, anchor="start")]
        # фронт + вікно hold
        s.append(line(xe, yc-18, xe, yc+40, color=INK, sw=1.3, dash="3 3"))
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="58" fill="#fdecea" stroke="%s" stroke-width="1.0" stroke-dasharray="4 3"/>' % (xe, yc-18, hw, POS))
        # лінія D(FF2)
        col = FIELD if ok else POS
        s.append(line(t0, yc+12, xd, yc+12, color=INK, sw=2.2))
        s.append(line(xd, yc+12, xd, yc-8, color=col, sw=2.4))
        s.append(line(xd, yc-8, t1, yc-8, color=col, sw=2.4))
        s.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (xd, yc+2, col))
        mark = "✗ у вікні" if not ok else "✓ поза вікном"
        s.append(text(xd+8, yc-14, mark, size=11.5, bold=True, color=col, anchor="start"))
        if extra:
            s.append(extra)
        return "".join(s)

    # ДО: зміна всередині вікна hold
    els.append(frame(90, "було: шлях занадто швидкий", xe+22, False))
    els.append(text(70, 66, "D(FF2)", size=11, bold=True, anchor="start", color=MUTED))

    # ПІСЛЯ: додали затримку — зміна виїхала за праву межу вікна
    xd2 = xe+hw+30
    extra = amark(xe+24, 232, xd2-2, 232, "aFld", FIELD, 1.8) + \
            text((xe+24+xd2)/2, 246, "+ додана затримка", size=10.5, color=FIELD)
    els.append(frame(210, "стало: у шлях даних вставили буфер-затримку", xd2, True, extra))
    els.append(text(70, 186, "D(FF2)", size=11, bold=True, anchor="start", color=MUTED))

    # підпис знизу
    els.append(fitbox(470, 258, 236, 54, "Період такту у формулу hold\nне входить — тому сповільнити\nтакт НЕ рятує; лікує лише затримка",
                      size=10.5, fill="#f4f6f8", stroke=INK, color=INK))
    return save(os.path.join(OUT, "hold-fix.svg"), W, H, *els)


# ── Фігура 4 (вставка math): прихід vs потрібний час — slack як зазор ────────
def fig_slack():
    W, H = 760, 340
    els = [text(W/2, 26, "Hold slack — зазор між приходом даних і краєм вікна", size=16, bold=True)]

    # спільна вісь часу; t=0 — той самий фронт (launch = capture)
    t0, t1 = 120, 700
    x0 = 200               # t = 0 (фронт)
    axy = 230
    els.append(line(t0, axy, t1, axy, color=INK, sw=1.8))
    els.append(line(t1, axy-5, t1, axy+5, color=INK, sw=1.4))
    els.append(text(t1, axy+20, "час →", size=11, color=MUTED, anchor="end"))
    els.append(line(x0, axy-150, x0, axy+16, color=INK, sw=1.4, dash="3 3"))
    els.append(text(x0-4, axy+30, "t = 0  (спільний фронт: launch = capture)", size=11, bold=True, anchor="start"))

    # ── required time = t_hold + t_skew (права межа вікна, куди дані приходити НЕ можна) ──
    xreq = x0 + 200
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="110" fill="#fdecea" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3"/>' % (x0, axy-114, xreq-x0, POS))
    els.append(line(xreq, axy-130, xreq, axy+16, color=POS, sw=1.8))
    els.append(amark(x0+2, axy-124, xreq-2, axy-124, "aPos", POS, 1.5))
    els.append(amark(xreq-2, axy-124, x0+2, axy-124, "aPos", POS, 1.5))
    els.append(text((x0+xreq)/2, axy-132, "потрібний час = t_hold + t_skew", size=11, bold=True, color=POS))
    els.append(text(x0+8, axy-92, "зона заборони (сюди приходити не можна)", size=10.5, color=POS, anchor="start"))

    # ── data arrival = t_cq(min) + t_logic(min) (коли нове значення реально приходить) ──
    xarr = xreq + 96       # безпечний випадок: прихід ПРАВІШЕ за межу → slack > 0
    els.append(line(xarr, axy-46, xarr, axy+64, color=FIELD, sw=2.0))
    els.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s"/>' % (xarr, axy, FIELD))
    els.append(text(xarr+6, axy-40, "нове значення прийшло", size=10.5, bold=True, color=FIELD, anchor="start"))
    els.append(amark(x0+2, axy+56, xarr-2, axy+56, "aFld", FIELD, 1.6))
    els.append(amark(xarr-2, axy+56, x0+2, axy+56, "aFld", FIELD, 1.6))
    els.append(text((x0+xarr)/2, axy+72, "прихід даних = t_cq(min) + t_logic(min)", size=11, bold=True, color=FIELD))

    # ── slack = arrival − required (зелений зазор) ──
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="28" fill="#eafaf1" stroke="%s" stroke-width="1.2" rx="4"/>' % (xreq, axy-14, xarr-xreq, FIELD))
    els.append(text((xreq+xarr)/2, axy+4, "slack", size=12, bold=True, color=FIELD))

    # присуд (короткий, щоб шрифт не зменшувався)
    els.append(fitbox(150, 300, 460, 30,
                      "slack > 0 → запас є;   slack < 0 → порушення hold",
                      size=13, fill="#f4f6f8", stroke=INK, color=INK, bold=True))
    return save(os.path.join(OUT, "hold-slack-number-line.svg"), W, H, *els)


# ── Фігура 5 (вставка math): гойдалка setup↔hold по перекосу такту ───────────
def fig_seesaw():
    W, H = 760, 400
    els = [text(W/2, 26, "Один перекіс — дві протилежні межі: вікно безпечного skew", size=15.5, bold=True)]

    # X — перекіс t_skew (capture − launch); Y — запас (slack); нуль-лінія посередині
    ax_l, ax_r = 120, 680
    y0 = 195                          # рівень slack = 0
    y_top, y_bot = 70, 300           # плато для прямих
    els.append(line(ax_l-16, y0, ax_r+10, y0, color=INK, sw=1.6))
    els.append(text(ax_r+10, y0-8, "t_skew →", size=11, color=MUTED, anchor="end"))
    els.append(text(ax_l-18, y0-8, "slack", size=11, color=MUTED, anchor="start"))
    els.append(text(ax_l-18, y0+16, "0", size=10.5, color=MUTED, anchor="start"))

    # Дві прямі як лінійні функції slack(t_skew). Нахил однаковий за модулем,
    # але зерокросинги РІЗНІ (setup ліворуч, hold праворуч) — між ними й лежить вікно.
    #   hold  slack = C₁ − t_skew  (спадна у slack): високо ліворуч, під нуль праворуч
    #   setup slack = C₂ + t_skew  (зростна у slack): під нуль ліворуч, високо праворуч
    m = 0.24                          # px slack на px skew (екранний нахил)
    xs0, xh0 = 335, 560               # задані зерокросинги: setup=0 ліворуч, hold=0 праворуч
    # hold: спадає вниз-екрану вправо (slack зменшується), проходить (xh0, y0)
    yh_l = y0 - (xh0 - ax_l) * m
    yh_r = y0 + (ax_r - xh0) * m
    # setup: піднімається вгору-екрану вправо (slack зростає), проходить (xs0, y0)
    ys_l = y0 + (xs0 - ax_l) * m
    ys_r = y0 - (ax_r - xs0) * m
    els.append(line(ax_l, yh_l, ax_r, yh_r, color=POS, sw=2.4))
    els.append(line(ax_l, ys_l, ax_r, ys_r, color=NEG, sw=2.4))
    els.append(text(ax_l+4, yh_l-8, "hold slack = C₁ − t_skew", size=11, bold=True, color=POS, anchor="start"))
    els.append(text(ax_r-4, ys_r-8, "setup slack = C₂ + t_skew", size=11, bold=True, color=NEG, anchor="end"))
    els.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (xh0, y0, POS))
    els.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (xs0, y0, NEG))
    els.append(line(xh0, y_top, xh0, y_bot, color=POS, sw=1.0, dash="2 3"))
    els.append(line(xs0, y_top, xs0, y_bot, color=NEG, sw=1.0, dash="2 3"))
    els.append(text(xh0+4, y_top+2, "hold=0", size=10, color=POS, anchor="start"))
    els.append(text(xs0-4, y_top+2, "setup=0", size=10, color=NEG, anchor="end"))

    # безпечне вікно між зерокросингами (де обидва slack ≥ 0)
    lo, hi = min(xh0, xs0), max(xh0, xs0)
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf1" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>' % (lo, y_top, hi-lo, y_bot-y_top, FIELD))
    els.append(text((lo+hi)/2, y_bot-10, "обидва запаси ≥ 0", size=11, bold=True, color=FIELD))

    els.append(fitbox(120, 336, 520, 46,
                      "Праворуч по осі — виграєш setup, програєш hold; ліворуч — навпаки.\nБезпечно лише там, де жодна пряма ще не пірнула під нуль.",
                      size=11.5, fill="#f4f6f8", stroke=INK, color=INK))
    return save(os.path.join(OUT, "hold-setup-seesaw.svg"), W, H, *els)


if __name__ == "__main__":
    p1 = fig_window()
    p2 = fig_race()
    p3 = fig_fix()
    p4 = fig_slack()
    p5 = fig_seesaw()
    print("OK:", os.path.basename(p1), os.path.basename(p2), os.path.basename(p3),
          os.path.basename(p4), os.path.basename(p5))
