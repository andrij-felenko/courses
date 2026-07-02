# -*- coding: utf-8 -*-
"""Фігури до детальної теми «Діоди Зенера, Шотткі» (guide/embedded/komponenty).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Ці фігури — для ДЕТАЛЬНОЇ версії (базова має свій набір: zener-iv, regulator тощо).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED, GRN, BLU = POS, FIELD, NEG


def polyline(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, fill, color, sw, d))


def polygon(pts, fill="#eef4ff", stroke="none", sw=1.0, opacity=1.0):
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    op = '' if opacity == 1.0 else ' fill-opacity="%.2f"' % opacity
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, fill, stroke, sw, op))


# ── 1. Реальна зворотна гілка: нахил = rZ, коліно IZK ─────────────────────────
# Ідея базової фігури — «гілка вертикальна». Тут показуємо ПРАВДУ: гілка має
# скінченний нахил rZ = ΔV/ΔI, а біля коліна (IZK) вона різко загинається —
# саме тому Зенер тримають вище коліна. ΔI → маленьке ΔV = rZ·ΔI.
def fig_dynamic_r():
    W, H = 720, 430
    f = [text(W / 2, 28, "Зворотна гілка не вертикальна: нахил — це rZ", size=16, bold=True)]
    # осі: горизонталь — напруга (вниз від нуля = зворотна), вертикаль — струм (вниз = зворотний)
    ox, oy = 470, 90          # початок координат (0,0)
    # вісь напруги вліво (−U), вісь струму вниз (−I)
    f.append(line(ox, oy, 120, oy, color=LINE, sw=1.6))            # вісь −U (вліво)
    f.append(line(ox, oy, ox, 370, color=LINE, sw=1.6))           # вісь −I (вниз)
    f.append(text(150, oy - 10, "−U (зворотна напруга)", size=11, color=MUTED, anchor="start"))
    f.append(text(ox + 8, 360, "−I", size=12, color=MUTED, anchor="start"))
    f.append(text(ox + 6, oy - 8, "0", size=11, color=MUTED, anchor="start"))

    # робоча ділянка: майже стала напруга біля U_Z, з малим нахилом rZ
    uz_x = 230                # x-координата U_Z (зліва)
    knee_y = oy + 40          # коліно (малий струм)
    # гілка від коліна вниз (робоча) з малим нахилом
    top = (uz_x + 26, knee_y)
    bot = (uz_x - 4, 340)
    # заокруглене коліно
    f.append(polyline([(ox - 6, oy + 6), (uz_x + 70, oy + 14),
                       (uz_x + 44, knee_y - 6), top, bot],
                      color=RED, sw=2.6))
    # пунктир: проєкція U_Z
    f.append(line(uz_x + 11, oy, uz_x + 11, 340, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(uz_x + 11, oy - 8, "U_Z", size=12, color=RED, bold=True))

    # позначити коліно й струми
    f.append(circle(uz_x + 44, knee_y - 6, 4, fill=RED, stroke=RED))
    f.append(line(ox, knee_y - 6, uz_x + 44, knee_y - 6, color=MUTED, sw=0.9, dash="3 3"))
    f.append(text(ox + 8, knee_y - 2, "I_ZK (коліно)", size=10.5, color=MUTED, anchor="start"))

    # трикутник нахилу ΔV/ΔI на робочій ділянці
    ay = 250
    by = 320
    ax = uz_x + 13
    bx = uz_x + 1
    f.append(line(ax, ay, ax, by, color=NEG, sw=1.4))            # ΔI
    f.append(line(ax, by, bx, by, color=GRN, sw=1.4))            # ΔV
    f.append(text(ax + 6, (ay + by) / 2, "ΔI", size=11, color=NEG, anchor="start"))
    f.append(text((ax + bx) / 2 - 2, by + 16, "ΔV", size=11, color=GRN, anchor="middle"))

    tb, tw, th = textbox(345, 190, "rZ = ΔV / ΔI\n(динамічний опір)\n— нахил гілки", size=12,
                         fill="#eef7ee", stroke=GRN)
    f.append(tb)
    tb2, _, _ = textbox(345, 300, "нижче I_ZK гілка\nрізко загинається —\nсюди не заходимо", size=11,
                        fill="#fdecea", stroke=RED)
    f.append(tb2)
    return render(os.path.join(IMG, "zener-dynamic-r.svg"), W, H, *f)


# ── 2. Температурний коефіцієнт проти U_Z: дві криві, перетин ~5–6 В ──────────
# Тунельний (Зенер) механізм — від'ємний TK; лавинний — додатний. Вони
# перетинають нуль там, де змішуються. Праворуч — температурно-компенсована
# опора: Зенер (+) послідовно з прямим переходом (−) гасять один одного.
def fig_tempco():
    W, H = 760, 440
    f = [text(W / 2, 28, "Температурний дрейф U_Z і точка «нуля»", size=16, bold=True)]
    # осі
    ox, oy = 90, 250
    x1 = 430
    f.append(line(ox, oy, x1, oy, color=LINE, sw=1.4))          # вісь U_Z
    f.append(line(ox, 70, ox, 400, color=LINE, sw=1.4))         # вісь TK
    f.append(text((ox + x1) / 2, 418, "U_Z, В", size=12, color=MUTED))
    f.append(text(ox - 60, 78, "TK, мВ/°C", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 8, oy + 4, "0", size=11, color=MUTED, anchor="end"))

    # шкала U_Z: 2..12 В по осі
    def ux(u):
        return ox + (u - 2) / (12 - 2) * (x1 - ox)
    for u in (2, 4, 6, 8, 10, 12):
        f.append(line(ux(u), oy - 4, ux(u), oy + 4, color=LINE, sw=1.0))
        f.append(text(ux(u), oy + 18, str(u), size=10, color=MUTED))

    # від'ємний внесок (тунель) — сильний унизу, згасає вгорі напруги
    def tk_zener(u):
        return -3.4 * math.exp(-(u - 2) / 3.2)      # мВ/°C, від'ємний
    # додатний внесок (лавина) — росте з напругою
    def tk_aval(u):
        return 0.42 * (u - 4.2)                       # мВ/°C, додатний

    def ty(tk):
        return oy - tk * 26                           # масштаб TK у пікселі

    pts_z = [(ux(u), ty(tk_zener(u))) for u in [2 + i * 0.2 for i in range(51)]]
    pts_a = [(ux(u), ty(tk_aval(u))) for u in [2 + i * 0.2 for i in range(51)]]
    pts_sum = [(ux(u), ty(tk_zener(u) + tk_aval(u))) for u in [2 + i * 0.2 for i in range(51)]]
    f.append(polyline(pts_z, color=NEG, sw=2.0, dash="6 4"))
    f.append(polyline(pts_a, color=RED, sw=2.0, dash="6 4"))
    f.append(polyline(pts_sum, color=INK, sw=2.8))

    # точка нуля суми (де tk_zener+tk_aval=0)
    u0 = None
    for i in range(500):
        u = 2 + i * 0.02
        if tk_zener(u) + tk_aval(u) >= 0:
            u0 = u
            break
    if u0:
        f.append(circle(ux(u0), ty(0), 5, fill=GRN, stroke=GRN))
        f.append(line(ux(u0), ty(0), ux(u0), oy + 30, color=GRN, sw=1.0, dash="3 3"))
        f.append(text(ux(u0), oy + 44, "≈%.1f В: TK≈0" % u0, size=10.5, color=GRN, bold=True))

    # легенда
    f.append(text(ux(2.4), ty(tk_zener(2.6)) - 8, "тунель (−)", size=10.5, color=NEG, anchor="start"))
    f.append(text(ux(10.2), ty(tk_aval(10.4)) - 6, "лавина (+)", size=10.5, color=RED, anchor="start"))
    f.append(text(ux(8.4), ty(tk_zener(8.4) + tk_aval(8.4)) - 12, "сума", size=11, color=INK, bold=True, anchor="start"))

    # праворуч — компенсована опора
    bx = 560
    tb, tw, th = textbox(bx, 120, "Зенер  ≈5.6 В\n+2 мВ/°C", size=11, fill="#fdecea", stroke=RED, min_w=150)
    f.append(tb)
    tb2, _, _ = textbox(bx, 200, "прямий перехід\n≈0.65 В\n−2 мВ/°C", size=11, fill="#eaf0fd", stroke=NEG, min_w=150)
    f.append(tb2)
    f.append(line(bx, 148, bx, 172, color=LINE, sw=1.6))
    tb3, _, _ = textbox(bx, 300, "разом ≈6.2 В\n≈0.2 мВ/°C\n(еталон опори)", size=11.5,
                        fill="#eef7ee", stroke=GRN, bold=True, min_w=160)
    f.append(tb3)
    f.append(line(bx, 232, bx, 268, color=GRN, sw=1.8))
    return render(os.path.join(IMG, "tempco-crossover.svg"), W, H, *f)


# ── 3. Робоче вікно стабілізатора: між I_ZK і I_Zmax ─────────────────────────
# Резистор задає загальний струм; навантаження забирає частину. Зенер живе між
# двома стінами: знизу I_ZK (мале навантаження випадає з пробою НЕ тут — навпаки,
# велике навантаження з'їдає струм Зенера), зверху I_Zmax (перегрів). Показуємо
# смугу дозволеного I_Z і як її з'їдають два крайні режими.
def fig_window():
    W, H = 740, 430
    f = [text(W / 2, 28, "Вікно стабілізатора: I_Z між коліном і межею потужності", size=15.5, bold=True)]
    # вертикальна шкала струму крізь Зенер
    ax = 150
    top_y, bot_y = 80, 360
    f.append(line(ax, top_y, ax, bot_y, color=LINE, sw=1.6))
    f.append(text(ax - 12, top_y - 8, "I_Z", size=12, color=MUTED, anchor="end"))
    f.append(text(ax - 12, bot_y + 4, "0", size=11, color=MUTED, anchor="end"))

    izk_y = bot_y - 40         # I_ZK (мінімум)
    izmax_y = top_y + 40       # I_Zmax (максимум)
    # заборонені зони
    f.append(rect(ax, bot_y - 40, 470, 40, fill="#fdecea", stroke="none", rx=0))
    f.append(rect(ax, top_y, 470, 40, fill="#fdecea", stroke="none", rx=0))
    # дозволена смуга
    f.append(rect(ax, izmax_y, 470, izk_y - izmax_y, fill="#eef7ee", stroke=GRN, sw=1.2, rx=0))
    f.append(line(ax, izk_y, ax + 470, izk_y, color=RED, sw=1.4, dash="5 4"))
    f.append(line(ax, izmax_y, ax + 470, izmax_y, color=RED, sw=1.4, dash="5 4"))
    f.append(text(ax + 8, izk_y + 24, "I_ZK: нижче — випав з пробою, стабілізації нема", size=10.5, color=RED, anchor="start"))
    f.append(text(ax + 8, izmax_y - 12, "I_Zmax = P_max/U_Z: вище — перегрів", size=10.5, color=RED, anchor="start"))
    f.append(text(ax + 8, (izmax_y + izk_y) / 2 - 8, "дозволений I_Z", size=12.5, color=GRN, bold=True, anchor="start"))
    f.append(text(ax + 8, (izmax_y + izk_y) / 2 + 10, "(робоча смуга)", size=10.5, color=GRN, anchor="start"))

    # два стовпчики: I_R = I_Z + I_load. I_Z (зелене) — знизу від нуля, тож його
    # ВИСОТА читається прямо по осі й має лягти в смугу; I_load (синє) — згори.
    def bar(cx, i_z_h, i_load_h):
        w = 46
        x = cx - w / 2
        base = bot_y
        # частина Зенера (низ, зеленим) — висота = I_Z
        f.append(rect(x, base - i_z_h, w, i_z_h, fill="#dff0e4", stroke=GRN, sw=1.0, rx=3))
        # частина навантаження (згори, синім)
        f.append(rect(x, base - i_z_h - i_load_h, w, i_load_h, fill="#dbe6ff", stroke=NEG, sw=1.0, rx=3))
        return base - i_z_h, base - i_z_h - i_load_h

    # I_R (задає резистор) однаковий у двох режимах; міняється лише розподіл.
    # I_R підібрано так, щоб при малому навантаженні I_Z сягав стелі I_Zmax.
    i_R = (bot_y - izmax_y) + 30       # трохи вище I_Zmax-рівня для навантаження
    # режим 1: мале навантаження → I_Z великий (майже весь I_R)
    zt1, lt1 = bar(360, (bot_y - izmax_y), 30)
    # режим 2: велике навантаження → I_Z малий (ледь над I_ZK)
    zt2, lt2 = bar(560, (bot_y - izk_y) + 6, (bot_y - izmax_y) - ((bot_y - izk_y) + 6) + 30)
    f.append(text(360, bot_y + 18, "мале навантаження", size=10.5, color=INK))
    f.append(text(560, bot_y + 18, "велике навантаження", size=10.5, color=INK))
    # рівень I_R
    f.append(line(337, bot_y - i_R, 583, bot_y - i_R, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(583, bot_y - i_R - 4, "I_R = (U_вх−U_Z)/R_S", size=10, color=MUTED, anchor="start"))
    # підписи часток
    f.append(text(360, (bot_y + zt1) / 2 + 3, "I_Z", size=9.5, color="#1a1a1a"))
    f.append(text(360, (zt1 + lt1) / 2 + 3, "I_L", size=9.5, color="#1a1a1a"))
    f.append(text(560, (bot_y + zt2) / 2 + 3, "I_Z", size=9, color="#1a1a1a"))
    f.append(text(560, (zt2 + lt2) / 2 + 3, "I_L", size=9.5, color="#1a1a1a"))
    return render(os.path.join(IMG, "regulator-window.svg"), W, H, *f)


# ── 4. Бар'єр Шотткі: трикутник компромісу ΦB ↔ V_F ↔ витік ──────────────────
# Зонна діаграма контакту метал–напівпровідник + сам компроміс: низький бар'єр —
# мале падіння, але великий витік (і ризик теплової втечі); високий — навпаки.
def fig_schottky_tradeoff():
    W, H = 760, 430
    f = [text(W / 2, 26, "Бар'єр Шотткі ΦB: одна висота — три наслідки", size=16, bold=True)]

    # ЛІВОРУЧ: зонна діаграма (метал | напівпровідник), термоемісія через бар'єр
    mx = 60
    sx = 190
    ex = 340
    top = 70
    ec = 300          # рівень дна зони провідності далеко в напівпровіднику
    # метал (заштрихований блок)
    f.append(rect(mx, top, sx - mx, 260, fill="#e6e9ee", stroke=LINE, sw=1.2))
    f.append(text((mx + sx) / 2, top + 140, "метал", size=12, color=INK))
    # рівень Фермі металу
    ef = 230
    f.append(line(mx, ef, sx, ef, color=NEG, sw=1.6))
    f.append(text(mx + 4, ef - 6, "E_F", size=10, color=NEG, anchor="start"))
    # бар'єр: дно зони провідності найвище на контакті (пік), спадає до бульку E_C
    barrier_top = top + 40
    f.append(polyline([(sx, barrier_top), (sx + 40, barrier_top + 6),
                       (sx + 90, ec - 6), (ex, ec)], color=RED, sw=2.4))
    # висота бар'єра ΦB — від E_F металу до піку зони, вертикальною мірою
    f.append(line(sx + 6, ef, sx + 6, barrier_top, color=RED, sw=1.0, dash="3 3"))
    f.append(text(sx + 12, (ef + barrier_top) / 2 + 4, "ΦB", size=13, color=RED, bold=True, anchor="start"))
    # E_C і E_V у нейтральному напівпровіднику
    f.append(line(sx + 90, ec, ex, ec, color=INK, sw=1.2))
    f.append(text(ex + 4, ec + 4, "E_C", size=10, color=INK, anchor="start"))
    f.append(line(sx, ec + 46, ex, ec + 46, color=MUTED, sw=1.0))
    f.append(text(ex + 4, ec + 50, "E_V", size=10, color=MUTED, anchor="start"))
    # електрон, що термічно перестрибує бар'єр
    f.append(circle(mx + 18, ef, 4, fill=NEG, stroke=NEG))
    f.append(arrow(mx + 22, ef - 4, sx - 2, barrier_top + 6, color=NEG, sw=1.6))
    f.append(mtext(mx + 6, top + 22, ["термоемісія:", "електрон ПОНАД бар'єр"],
                   size=9.5, color=NEG, anchor="start"))
    f.append(text((sx + ex) / 2 + 20, ec + 82, "напівпровідник (n)", size=11, color=INK))
    f.append(text((mx + ex) / 2, 360, "лише ОСНОВНІ носії → нема Q_rr", size=10.5, color=GRN, bold=True))

    # ПРАВОРУЧ: терези компромісу
    bx = 560
    f.append(text(bx, 70, "низький ΦB", size=12, color=INK, bold=True))
    tb, _, _ = textbox(bx, 120, "+ мале падіння V_F (~0.2 В)\n− великий зворотний витік\n− ризик теплової втечі",
                       size=10.5, fill="#fdecea", stroke=RED, min_w=230)
    f.append(tb)
    f.append(text(bx, 210, "високий ΦB", size=12, color=INK, bold=True))
    tb2, _, _ = textbox(bx, 262, "+ малий витік, вища U_R\n− більше падіння V_F\n(ближче до кремнію)",
                        size=10.5, fill="#eef7ee", stroke=GRN, min_w=230)
    f.append(tb2)
    tb3, _, _ = textbox(bx, 350, "витік росте з T → може\nрозганяти сам себе (теплова втеча)",
                        size=10, fill="#fff6e6", stroke="#b8860b", min_w=250)
    f.append(tb3)
    return render(os.path.join(IMG, "schottky-tradeoff.svg"), W, H, *f)


# ── 5. Больцманів хвіст: звідки exp(−ΦB/kT) ──────────────────────────────────
# Розподіл електронів за енергією ~ exp(−E/kT). Перескочити бар'єр можуть лише
# ті, у кого E > ΦB — заштрихований «хвіст» праворуч. Його частка = exp(−ΦB/kT).
# Дві криві (холодна й гаряча) показують, ЧОМУ хвіст росте з T так круто.
def fig_boltzmann_tail():
    W, H = 760, 420
    f = [text(W / 2, 26, "Струм — це «хвіст» розподілу за бар'єром: exp(−ΦB/kT)", size=15.5, bold=True)]
    ox, oy = 90, 320               # початок осей
    x1 = 560
    f.append(line(ox, oy, x1, oy, color=LINE, sw=1.5))          # вісь енергії
    f.append(line(ox, oy, ox, 70, color=LINE, sw=1.5))          # вісь «скільки електронів»
    f.append(text((ox + x1) / 2, oy + 40, "енергія електрона E  →", size=12, color=MUTED))
    f.append(mtext(ox - 14, 150, ["скільки", "електронів", "має таку E"], size=10.5,
                   color=MUTED, anchor="end"))

    # бар'єр ΦB — вертикаль
    bx = 360
    f.append(line(bx, oy, bx, 80, color=RED, sw=2.0, dash="6 4"))
    f.append(text(bx, 72, "ΦB (висота бар'єра)", size=12, color=RED, bold=True))

    import math as _m
    # два «теплові» масштаби: холодний (вузький, спадає круто) і гарячий (широкий)
    def dist(E, kT, amp):
        return amp * _m.exp(-(E - ox) / kT)      # ~exp(−E/kT), від початку осі

    def curve(kT, amp, color, dash=None):
        pts = [(x, oy - dist(x, kT, amp)) for x in [ox + i * 2 for i in range(int((x1 - ox) / 2))]
               if dist(x, kT, amp) <= (oy - 80)]
        # обрізати верх, щоб не вилазило
        pts = [(x, max(y, 80)) for (x, y) in pts]
        return polyline(pts, color=color, sw=2.4, dash=dash), pts

    cold_kT, hot_kT = 55.0, 95.0
    amp = oy - 90
    cold, cpts = curve(cold_kT, amp, NEG)
    hot, hpts = curve(hot_kT, amp * 0.72, RED, dash="2 3")
    # заливка хвоста (холодного) за бар'єром
    tail = [(x, y) for (x, y) in cpts if x >= bx]
    if tail:
        poly = [(bx, oy)] + tail + [(tail[-1][0], oy)]
        f.append(polygon(poly, fill="#dbe6ff", stroke="none", opacity=0.9))
    # заливка гарячого хвоста (поверх, напівпрозоро) — видно, що більший
    thot = [(x, y) for (x, y) in hpts if x >= bx]
    if thot:
        polyh = [(bx, oy)] + thot + [(thot[-1][0], oy)]
        f.append(polygon(polyh, fill="#fdecea", stroke="none", opacity=0.6))
    f.append(cold)
    f.append(hot)

    # підписи кривих
    f.append(text(ox + 40, oy - dist(ox + 40, cold_kT, amp) - 8, "холодний діод", size=10.5,
                  color=NEG, anchor="start", bold=True))
    f.append(text(ox + 150, oy - dist(ox + 150, hot_kT, amp * 0.72) - 8, "гарячий (T↑)", size=10.5,
                  color=RED, anchor="start", bold=True))
    # стрілка на хвіст
    f.append(arrow(470, 250, 430, oy - 14, color=INK, sw=1.5))
    f.append(mtext(474, 244, ["лише ці перескочать:", "частка = exp(−ΦB/kT)"], size=10.5,
                   color=INK, anchor="start"))

    tb, _, _ = textbox(575, 130,
                       "більша T →\nширший розподіл →\nхвіст за ΦB росте\nЕКСПОНЕНЦІЙНО",
                       size=10.5, fill="#fff6e6", stroke="#b8860b", min_w=160)
    f.append(tb)
    return render(os.path.join(IMG, "boltzmann-tail.svg"), W, H, *f)


# ── 6. Річардсонів графік: ln(I0/T²) проти 1/T — пряма з нахилом −ΦB/k ────────
# Уся температурна залежність згорнута в пряму. Нахил дає висоту бар'єра,
# відрізок — сталу A*. Праворуч показуємо, як крутість цієї прямої = крутість
# росту витоку з температурою.
def fig_richardson_plot():
    W, H = 760, 420
    f = [text(W / 2, 26, "Річардсонів графік: ln(I₀/T²) проти 1/T — пряма", size=16, bold=True)]
    ox, oy = 110, 320
    x1, top = 470, 80
    f.append(line(ox, oy, x1, oy, color=LINE, sw=1.5))          # вісь 1/T
    f.append(line(ox, oy, ox, top, color=LINE, sw=1.5))         # вісь ln(I0/T2)
    f.append(text((ox + x1) / 2, oy + 42, "1000/T  (більше T →  вліво)", size=11.5, color=MUTED))
    f.append(mtext(ox - 16, 170, ["ln(I₀ / T²)"], size=12, color=MUTED, anchor="end"))
    # напрямок «гарячіше»
    f.append(arrow(x1 - 10, oy - 16, ox + 30, oy - 16, color=MUTED, sw=1.2))
    f.append(text(ox + 40, oy - 22, "гарячіше", size=10, color=MUTED, anchor="start"))

    import math as _m
    # пряма: y = ln(A*S) − (PhiB/k)*(1/T). Малюємо у власних одиницях.
    # осьова змінна u = 1000/T; беремо діапазон T=250..450 → u≈4..2.22
    def X(u):   # u = 1000/T
        return ox + (u - 2.2) / (4.2 - 2.2) * (x1 - ox)
    k = 8.617e-5
    # нахил у «пікселях»: візьмемо PhiB=0.5 і намалюємо лінію в умовному масштабі
    def line_y(u, slope_px, y_at_u3):
        return y_at_u3 + slope_px * (u - 3.0)

    # дві прямі: нижчий бар'єр (крутіша й вища) і вищий бар'єр (нижча)
    slope1 = 62      # px на одиницю u — крутий нахил (−ΦB/k), низький ΦB → вищий I0
    slope2 = 82      # крутіший — вищий бар'єр
    yc1, yc2 = 150, 240
    p1 = [(X(u), line_y(u, slope1, yc1)) for u in [2.3 + i * 0.05 for i in range(35)]]
    p2 = [(X(u), line_y(u, slope2, yc2)) for u in [2.3 + i * 0.05 for i in range(35)]]
    f.append(polyline(p2, color=GRN, sw=2.6))
    f.append(polyline(p1, color=RED, sw=2.6))
    f.append(text(X(2.35), line_y(2.35, slope1, yc1) - 8, "низький ΦB", size=10.5, color=RED, anchor="start", bold=True))
    f.append(text(X(2.35), line_y(2.35, slope2, yc2) - 8, "високий ΦB", size=10.5, color=GRN, anchor="start", bold=True))

    # трикутник нахилу на червоній
    ua, ub = 3.2, 3.7
    f.append(line(X(ua), line_y(ua, slope1, yc1), X(ub), line_y(ua, slope1, yc1), color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(X(ub), line_y(ua, slope1, yc1), X(ub), line_y(ub, slope1, yc1), color=NEG, sw=1.4))
    f.append(text((X(ua) + X(ub)) / 2, line_y(ua, slope1, yc1) - 6, "Δ(1/T)", size=9.5, color=MUTED))
    f.append(text(X(ub) + 6, (line_y(ua, slope1, yc1) + line_y(ub, slope1, yc1)) / 2,
                  "нахил = −ΦB/k", size=10.5, color=NEG, anchor="start", bold=True))

    # позначки температур по осі
    for T in (400, 350, 300, 250):
        u = 1000.0 / T
        if 2.2 <= u <= 4.2:
            f.append(line(X(u), oy - 4, X(u), oy + 4, color=LINE, sw=1.0))
            f.append(text(X(u), oy + 18, "%d K" % T, size=9, color=MUTED))

    tb, _, _ = textbox(615, 140, "нахил → висота ΦB\nвідрізок → стала A*·S",
                       size=11, fill="#eef7ee", stroke=GRN, min_w=190)
    f.append(tb)
    tb2, _, _ = textbox(615, 250, "круто вправо-вниз =\nвитік ПАДАЄ на морозі,\nРОСТЕ у спеку",
                        size=10.5, fill="#fff6e6", stroke="#b8860b", min_w=200)
    f.append(tb2)
    return render(os.path.join(IMG, "richardson-plot.svg"), W, H, *f)


# ── 7. Теплова втеча: генерація тепла (експонента) проти відведення (пряма) ───
# P_gen = U_R·I0(T) росте експоненційно; P_відв = (T−T_amb)/R_th — пряма.
# Перетини: нижній — стійкий, дотик — межа. Круте охолодження (менший R_th =
# крутіша пряма) рятує; погане — пряма не наздоганяє експоненту → втеча.
def fig_thermal_runaway():
    W, H = 760, 430
    f = [text(W / 2, 26, "Теплова втеча: генерація (експонента) проти відведення (пряма)", size=15, bold=True)]
    ox, oy = 90, 350
    x1, top = 560, 70
    f.append(line(ox, oy, x1, oy, color=LINE, sw=1.5))          # вісь T
    f.append(line(ox, oy, ox, top, color=LINE, sw=1.5))         # вісь потужності
    f.append(text((ox + x1) / 2, oy + 40, "температура переходу T  →", size=12, color=MUTED))
    f.append(mtext(ox - 14, 150, ["потужність,", "Вт"], size=11, color=MUTED, anchor="end"))

    import math as _m
    Tamb_x = ox + 40            # T_amb на осі
    # генерація: P = c·exp((x−ox)/scale)  (експонента з T)
    scale = 105.0
    c = 3.0
    def Pgen(x):
        return c * _m.exp((x - Tamb_x) / scale)
    gpts = [(x, oy - Pgen(x)) for x in [ox + i * 2 for i in range(int((x1 - ox) / 2))]
            if Pgen(x) <= (oy - top)]
    f.append(polyline(gpts, color=RED, sw=2.8))
    f.append(text(gpts[-1][0] - 4, gpts[-1][1] + 4, "P_gen = U_R·I₀(T)", size=11, color=RED, anchor="end", bold=True))

    # дві прямі відведення з одного T_amb, різний нахил (=1/R_th)
    def removal(x, slope):
        return max(0.0, slope * (x - Tamb_x))
    good_slope = 1.05    # добре охолодження — крута пряма
    bad_slope = 0.42     # погане — полога
    gr = [(x, oy - removal(x, good_slope)) for x in [Tamb_x + i * 2 for i in range(int((x1 - Tamb_x) / 2))]
          if removal(x, good_slope) <= (oy - top)]
    br = [(x, oy - removal(x, bad_slope)) for x in [Tamb_x + i * 2 for i in range(int((x1 - Tamb_x) / 2))]
          if removal(x, bad_slope) <= (oy - top)]
    f.append(polyline(gr, color=NEG, sw=2.4))
    f.append(polyline(br, color="#b8860b", sw=2.4, dash="6 4"))
    f.append(text(gr[-1][0], gr[-1][1] - 6, "добре охолодження", size=10, color=NEG, anchor="end", bold=True))
    f.append(text(br[-1][0] + 4, br[-1][1], "погане (пологе)", size=10, color="#b8860b", anchor="start", bold=True))

    # T_amb мітка
    f.append(line(Tamb_x, oy, Tamb_x, oy + 8, color=LINE, sw=1.2))
    f.append(text(Tamb_x, oy + 22, "T_amb", size=10, color=MUTED))

    # знайти перетин доброї прямої з генерацією (стійка точка) — перша, де removal>=Pgen
    xs = None
    for i in range(int((x1 - Tamb_x))):
        x = Tamb_x + i
        if removal(x, good_slope) >= Pgen(x):
            xs = x
            break
    if xs:
        f.append(circle(xs, oy - Pgen(xs), 5, fill=GRN, stroke=GRN))
        f.append(text(xs, oy - Pgen(xs) - 12, "стійка робоча точка", size=10, color=GRN, bold=True))

    # погана пряма нижче експоненти скрізь → підпис «немає перетину»
    f.append(arrow(430, 150, 500, 110, color="#b8860b", sw=1.5))
    f.append(mtext(300, 140, ["погана пряма НІДЕ не наздожене", "експоненту → T біжить угору → втеча"],
                   size=10.5, color="#b8860b", anchor="start"))

    tb, _, _ = textbox(180, 250,
                       "T↑ → I₀↑ (експон.) →\nP↑ → T↑↑  (петля)",
                       size=11, fill="#fdecea", stroke=RED, bold=True, min_w=220)
    f.append(tb)
    return render(os.path.join(IMG, "thermal-runaway.svg"), W, H, *f)


# ── 8. Важіль бар'єра: ΔΦ_B на 0.1 еВ множить I₀ у ~50 разів (для math-вставки)─
# Серце числового прикладу вставки про термоемісію. exp(−ΦB/kT): при кімнатній T
# kT≈0.02585 еВ, тож зниження ΦB на 0.10 еВ множить I₀ на exp(0.10/0.02585)≈48.
# Показуємо це як важіль: маленький зсув бар'єра ліворуч → величезний стрибок I₀
# праворуч (лог-шкала), а пряме падіння зсувається лише на ~0.10 В.
def fig_barrier_lever():
    import math as _m
    W, H = 760, 430
    f = [text(W / 2, 26, "Важіль бар'єра: −0.1 еВ на ΦB → ×48 до I₀", size=16, bold=True)]
    kT = 0.02585  # еВ при 300 K
    # ── ліворуч: два бар'єри різної висоти (зонна картинка спрощено) ──
    ox, base = 70, 330
    f.append(line(ox, base, ox, 90, color=LINE, sw=1.4))       # вісь енергії
    f.append(text(ox - 8, 96, "E", size=12, color=MUTED, anchor="end"))
    f.append(line(ox, base, 300, base, color=LINE, sw=1.4))    # рівень Фермі металу
    f.append(text(ox + 6, base + 16, "рівень Фермі металу", size=9.5, color=MUTED, anchor="start"))
    # два бар'єри
    phiA, phiB = 0.60, 0.50
    yA = base - phiA * 300        # масштаб: 1 еВ = 300 px
    yB = base - phiB * 300
    xb = 210
    f.append(line(ox, yA, xb, yA, color=RED, sw=2.4, dash="6 4"))
    f.append(line(ox, yB, xb, yB, color=GRN, sw=2.4))
    f.append(text(xb + 6, yA + 4, "ΦB = 0.60 еВ", size=10.5, color=RED, anchor="start", bold=True))
    f.append(text(xb + 6, yB + 4, "ΦB = 0.50 еВ", size=10.5, color=GRN, anchor="start", bold=True))
    # стрілка зсуву бар'єра
    f.append(arrow(ox + 40, yA, ox + 40, yB, color=INK, sw=1.6))
    f.append(text(ox + 46, (yA + yB) / 2 + 4, "−0.10 еВ", size=10, color=INK, anchor="start", bold=True))
    # хвиляста стрілка «перескочити» від Фермі понад бар'єр
    f.append(text(ox + 120, base - 6, "термоемісія понад ΦB", size=9.5, color=MUTED, anchor="start"))

    # ── праворуч: логарифмічна вісь I₀ і два рівні ──
    lx = 470
    top_y, bot_y = 90, 330
    f.append(line(lx, top_y, lx, bot_y, color=LINE, sw=1.5))
    f.append(text(lx, top_y - 10, "I₀  (лог-шкала)", size=12, color=MUTED))
    # три декади для орієнтиру
    for d in range(4):
        y = bot_y - d * (bot_y - top_y) / 3.0
        f.append(line(lx - 5, y, lx + 5, y, color=MUTED, sw=1.0))
        f.append(text(lx - 9, y + 4, "×10%d" % d, size=9, color=MUTED, anchor="end"))
    # рівень для ΦB=0.60 (низький I0) і 0.50 (вищий у 48 разів = +1.68 декади)
    decades = _m.log10(_m.exp(0.10 / kT))   # ≈1.68
    yA2 = bot_y - 0.15 * (bot_y - top_y) / 1.0        # умовний старт (низько)
    # прив'яжемо масштаб: 1 декада = (bot_y-top_y)/3
    dec_px = (bot_y - top_y) / 3.0
    yA2 = bot_y - 0.2 * dec_px
    yB2 = yA2 - decades * dec_px
    f.append(circle(lx, yA2, 6, fill=RED, stroke=RED))
    f.append(circle(lx, yB2, 6, fill=GRN, stroke=GRN))
    f.append(line(lx, yA2, lx + 120, yA2, color=RED, sw=1.0, dash="4 4"))
    f.append(line(lx, yB2, lx + 120, yB2, color=GRN, sw=1.0, dash="4 4"))
    f.append(text(lx + 124, yA2 + 4, "I₀ (ΦB=0.60)", size=10, color=RED, anchor="start"))
    f.append(text(lx + 124, yB2 + 4, "I₀ ×48 (ΦB=0.50)", size=10, color=GRN, anchor="start", bold=True))
    # подвійна стрілка стрибка
    f.append(arrow(lx - 22, yA2, lx - 22, yB2, color=INK, sw=1.8))
    f.append(mtext(lx - 28, (yA2 + yB2) / 2, ["×48", "(≈1.7", "декади)"], size=10, color=INK, anchor="end", bold=True))

    tb, _, _ = textbox(W / 2, 392,
                       "exp(0.10 / 0.02585) ≈ 48   ·   а пряме падіння зсувається лише на ≈ n·0.10 В",
                       size=11, fill="#fff6e6", stroke="#b8860b", bold=True, min_w=300)
    f.append(tb)
    return render(os.path.join(IMG, "barrier-lever.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dynamic_r()
    fig_tempco()
    fig_window()
    fig_schottky_tradeoff()
    fig_boltzmann_tail()
    fig_richardson_plot()
    fig_thermal_runaway()
    fig_barrier_lever()
    print("OK: 8 фігур у", IMG)
