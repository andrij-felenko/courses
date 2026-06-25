# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні відтінки під єдину палітру svgkit
AMBER   = "#caa24a"   # бурштин — симулятор / середній шар
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── loop: цикл «прошивка ↔ симулятор» (основна ідея SITL) ─────────────────────
# Ідея: той самий код автопілота крутиться як звичайний процес на ПК. Замість
# справжніх давачів і моторів його з обох боків обступає симулятор: зліва годує
# підробленими вимірами, справа ловить команди на мотори й рахує нову фізику.
# Між ними замкнене коло; код не бачить, що заліза нема. Збоку — MAVLink назовні.

def fig_loop():
    W, H = 820, 392
    p = []
    # центр — прошивка як процес на ПК
    fw_x, fw_y, fw_w, fw_h = 300, 150, 220, 110
    p.append(rect(fw_x, fw_y, fw_w, fw_h, fill=GREENBG, stroke=FIELD, sw=2.4, rx=12))
    p.append(text(fw_x + fw_w / 2, fw_y + 30, "КОД АВТОПІЛОТА", size=13.5, color=FIELD, bold=True))
    p.append(text(fw_x + fw_w / 2, fw_y + 50, "той самий, що й у плату", size=9.6, color=INK))
    p.append(text(fw_x + fw_w / 2, fw_y + 70, "оцінка стану · керування", size=9.6, color=MUTED))
    p.append(text(fw_x + fw_w / 2, fw_y + 90, "звичайний процес на ПК", size=10, color=FIELD, bold=True))

    # лівий бік — симулятор годує сенсорами
    p.append(rect(40, 120, 200, 80, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(140, 146, "СИМУЛЯТОР", size=12.5, color=AMBERTX, bold=True))
    p.append(text(140, 166, "модель фізики й давачів", size=9.4, color=INK))
    p.append(text(140, 184, "гіроскоп, GPS, баро…", size=9.2, color=MUTED))
    # стрілка сенсори → код
    p.append(arrow(240, 158, fw_x - 2, 178, color=AMBER, sw=2.4))
    p.append(text((240 + fw_x) / 2, 150, "виміри", size=9.6, color=AMBERTX, bold=True))

    # правий бік — команди на мотори назад у симулятор
    p.append(rect(580, 120, 200, 80, fill=AMBERBG, stroke=AMBER, sw=2, rx=10))
    p.append(text(680, 146, "ТА САМА МОДЕЛЬ", size=12.5, color=AMBERTX, bold=True))
    p.append(text(680, 166, "рахує, як апарат полетів", size=9.4, color=INK))
    p.append(text(680, 184, "→ нові виміри", size=9.2, color=MUTED))
    # стрілка код → мотори
    p.append(arrow(fw_x + fw_w + 2, 178, 580, 158, color=NEG, sw=2.4))
    p.append(text((fw_x + fw_w + 580) / 2 + 8, 150, "тяга моторів", size=9.6, color=NEG, bold=True))

    # замкнене коло знизу
    p.append("<path d=\"M 680 200 L 680 300 L 140 300 L 140 200\" fill=\"none\" stroke=\"%s\" stroke-width=\"2\" stroke-dasharray=\"6 5\" marker-end=\"url(#arrow)\"/>" % MUTED)
    p.append(text(410, 294, "замкнене коло: фізика → виміри → рішення → тяга → фізика…", size=10, color=MUTED))

    # MAVLink назовні
    p.append(arrow(fw_x + fw_w / 2, fw_y - 2, fw_x + fw_w / 2, 78, color=INK, sw=2))
    p.append(rect(fw_x + fw_w / 2 - 150, 44, 300, 32, fill=BLUEBG, stroke=NEG, sw=1.6, rx=8))
    p.append(text(fw_x + fw_w / 2, 64, "MAVLink — як зі справжнім дроном (наземна станція, скрипти)", size=9.4, color=NEG))

    p.append(text(W / 2, H - 14, "жодного заліза — а код поводиться так, ніби летить",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "loop.svg"), W, H, *p,
           title="SITL: код автопілота крутиться на ПК, фізику дає симулятор")


# ── sitl-vs-hil: де кінчається код і починається залізо ──────────────────────
# Ідея: SITL і HIL відрізняються однією межею — ЩО справжнє. У SITL справжній лише
# КОД (процес на ПК), решта — модель. У HIL справжні КОД І ПЛАТА (чіп у петлі), а
# світ навколо — модель. Що правіше зсунута межа, то реалістичніше, але дорожче.

def fig_sitl_vs_hil():
    W, H = 820, 360
    p = []
    cw, cx_l, cx_r = 360, 30, 430
    top, ch = 70, 250

    def panel(x, title, tcol, fill, rows, foot, footcol):
        out = [rect(x, top, cw, ch, fill=fill, stroke=tcol, sw=2, rx=12)]
        out.append(text(x + cw / 2, top + 28, title, size=13.5, color=tcol, bold=True))
        for i, (label, kind, kindcol) in enumerate(rows):
            ry = top + 52 + i * 46
            out.append(rect(x + 24, ry, cw - 48, 36, fill=BG, stroke=kindcol, sw=1.6, rx=8))
            out.append(text(x + 40, ry + 23, label, size=10.6, color=INK, anchor="start"))
            out.append(text(x + cw - 40, ry + 23, kind, size=10.2, color=kindcol, anchor="end", bold=True))
        out.append(text(x + cw / 2, top + ch - 14, foot, size=10, color=footcol, bold=True))
        return out

    # SITL
    p += panel(cx_l, "SITL — у петлі лише КОД", FIELD, GREENBG,
               [("код автопілота", "справжній", FIELD),
                ("чіп / плата", "нема", MUTED),
                ("давачі, мотори, фізика", "модель", AMBERTX)],
               "усе в одному процесі на ПК — швидко, безпечно, без заліза", FIELD)
    # HIL
    p += panel(cx_r, "HIL — у петлі КОД І ПЛАТА", NEG, BLUEBG,
               [("код автопілота", "справжній", FIELD),
                ("чіп / плата", "справжня", NEG),
                ("давачі, мотори, фізика", "модель", AMBERTX)],
               "реальний чіп у петлі — реалістичніше, але потрібна плата", NEG)

    p.append(text(W / 2, H - 12, "та сама межа, лише зсунута: SITL перевіряє код, HIL — код разом із залізом",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "sitl-vs-hil.svg"), W, H, *p,
           title="SITL і HIL: різниця в одному — що справжнє, а що модель")


# ── lockstep: крок-у-крок між прошивкою й симулятором ─────────────────────────
# Ідея: годинник веде не стіна, а сам обмін. Симулятор шле виміри з МІТКОЮ ЧАСУ →
# прошивка робить РІВНО один крок керування → шле команди → симулятор рахує
# фізику на dt і шле наступні виміри. Жоден не біжить попереду; час — модельний,
# тож хід можна пришвидшити, сповільнити чи спинити на брейкпоінті.

def fig_lockstep():
    W, H = 820, 392
    p = []
    lx, rx = 150, 670          # дві доріжки-стовпи
    top = 86
    # стовпи-учасники
    p.append(rect(lx - 110, top - 36, 220, 28, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(lx, top - 17, "СИМУЛЯТОР (фізика, час)", size=10.6, color=AMBERTX, bold=True))
    p.append(rect(rx - 110, top - 36, 220, 28, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(rx, top - 17, "ПРОШИВКА (крок керування)", size=10.6, color=FIELD, bold=True))
    p.append(line(lx, top, lx, H - 60, color=AMBER, sw=1.4, dash="3 4"))
    p.append(line(rx, top, rx, H - 60, color=FIELD, sw=1.4, dash="3 4"))

    steps = [
        (top + 26, lx, rx, "виміри + мітка часу t", AMBER, "→"),
        (top + 70, rx, lx, "один крок: оцінка → керування → тяга", FIELD, "←"),
        (top + 114, lx, rx, "крок фізики на dt; час = t + dt", AMBER, "→"),
        (top + 158, rx, lx, "наступний крок керування", FIELD, "←"),
        (top + 202, lx, rx, "виміри на t + dt …", AMBER, "→"),
    ]
    for y, a, b, label, col, d in steps:
        p.append(arrow(a, y, b, y, color=col, sw=2.2))
        midx = (a + b) / 2
        p.append(text(midx, y - 8, label, size=9.8, color=INK))

    p.append(rect(120, H - 52, 580, 30, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(410, H - 32, "ніхто не біжить попереду; час — модельний → хід можна пришвидшити, сповільнити чи спинити",
                  size=9.8, color=MUTED, italic=True))
    render(os.path.join(OUT, "lockstep.svg"), W, H, *p,
           title="Lockstep: крок симулятора — крок прошивки, по черзі")


# ── ci-place: місце SITL у тесті й CI ────────────────────────────────────────
# Ідея: SITL стоїть на новому, системному поверсі над пірамідою тестів прошивки.
# Юніт/моки/HIL перевіряють ШМАТКИ коду; SITL ганяє ВЕСЬ автопілот як цілість —
# зліт, місію, відмову, регресію — у CI на кожен коміт, без жодного дрона.

def fig_ci_place():
    W, H = 820, 400
    p = []
    # ліва колонка — піраміда тестів (стисло), права — системний рівень SITL
    # піраміда
    p.append(text(225, 56, "тести ШМАТКІВ коду", size=12.5, color=INK, bold=True))
    bars = [
        (300, 196, "юніт-тести логіки", FIELD, GREENBG),
        (250, 244, "моки периферії", AMBER, AMBERBG),
        (170, 292, "HIL — чіп у петлі", NEG, BLUEBG),
    ]
    cx = 225
    for w, y, label, col, fill in bars:
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(cx - w / 2, y, w, 40, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(cx, y + 25, label, size=10.8, color=tagcol, bold=True))
    p.append(text(225, 350, "кожен бачить свій шматок", size=9.6, color=MUTED, italic=True))

    # роздільник
    p.append(line(455, 80, 455, 360, color="#cccccc", sw=1.2, dash="4 4"))

    # системний рівень SITL
    p.append(text(635, 56, "SITL — ВЕСЬ автопілот як цілість", size=12.5, color=POS, bold=True))
    p.append(rect(490, 90, 290, 168, fill=REDBG, stroke=POS, sw=2.2, rx=12))
    items = ["зліт і посадка", "ціла місія за планом", "відмова давача / GPS",
             "регресія: та сама місія після правки"]
    for i, it in enumerate(items):
        iy = 122 + i * 34
        p.append(circle(516, iy - 4, 4.5, fill=POS, stroke=POS, sw=1))
        p.append(text(532, iy, it, size=10.6, color=INK, anchor="start"))

    p.append(rect(490, 280, 290, 64, fill=GREENBG, stroke=FIELD, sw=2, rx=10))
    p.append(text(635, 304, "у CI — на кожен коміт, без дрона", size=11, color=FIELD, bold=True))
    p.append(text(635, 326, "зламав політ правкою — знаєш за хвилини", size=9.6, color=INK))

    p.append(text(W / 2, H - 12, "піраміда перевіряє частини; SITL доводить, що вони разом таки літають",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "ci-place.svg"), W, H, *p,
           title="Де SITL у тесті: системний поверх над пірамідою")


# ════════════════════════════════════════════════════════════════════════════
# Фігури детальної версії sitl-simulation-d.md
# ════════════════════════════════════════════════════════════════════════════


# ── hal-swap: підміна на рівні HAL ───────────────────────────────────────────
# Ідея: SITL — це ще одна «плата» в архітектурі автопілота. Над межею HAL — той
# самий незмінний код (оцінка стану, керування, місії). Під межею бойова збірка
# бере драйвери чипа (SPI/I2C/PWM), а збірка SITL — backend, що бере виміри з
# моделі й віддає тягу в модель. Код над межею не знає, який бекенд унизу.

def fig_hal_swap():
    W, H = 820, 392
    p = []
    bx, bw = 70, W - 140
    # верх — незмінний код
    p.append(rect(bx, 64, bw, 96, fill=GREENBG, stroke=FIELD, sw=2.2, rx=12))
    p.append(text(W / 2, 90, "КОД АВТОПІЛОТА — однаковий в обох збірках", size=13, color=FIELD, bold=True))
    p.append(text(W / 2, 114, "оцінка стану (EKF) · керування · режими · місії", size=10.4, color=INK))
    p.append(text(W / 2, 138, "не знає, що під ним — чіп чи модель", size=10.4, color=FIELD, bold=True))

    # межа HAL
    p.append(rect(W / 2 - 220, 178, 440, 36, fill=AMBERBG, stroke=AMBER, sw=1.9, rx=8))
    p.append(text(W / 2, 201, "межа HAL — однаковий інтерфейс «дай вимір / дай тягу»", size=10.4, color=AMBERTX, bold=True))

    # низ — два бекенди
    cw = 350
    p.append(rect(bx, 244, cw, 96, fill=BLUEBG, stroke=NEG, sw=2, rx=12))
    p.append(text(bx + cw / 2, 270, "бойовий бекенд (плата)", size=12, color=NEG, bold=True))
    p.append(text(bx + cw / 2, 292, "драйвери чипа: SPI / I2C / PWM", size=10, color=INK))
    p.append(text(bx + cw / 2, 312, "реальні давачі й мотори", size=10, color=MUTED))

    rx2 = W - bx - cw
    p.append(rect(rx2, 244, cw, 96, fill=AMBERBG, stroke=AMBER, sw=2.4, rx=12))
    p.append(text(rx2 + cw / 2, 270, "бекенд SITL (модель)", size=12, color=AMBERTX, bold=True))
    p.append(text(rx2 + cw / 2, 292, "виміри з моделі фізики", size=10, color=INK))
    p.append(text(rx2 + cw / 2, 312, "тяга → у модель, не в залізо", size=10, color=MUTED))

    p.append(arrow(bx + cw / 2, 244, bx + 120, 214, color=INK, sw=2))
    p.append(arrow(rx2 + cw / 2, 244, rx2 + cw - 120, 214, color=INK, sw=2))
    p.append(text(W / 2, H - 12, "SITL — це просто ще одна «плата»: підмінили найнижчий шар, усе вище лишилось",
                  size=10.6, color=MUTED, italic=True))
    render(os.path.join(OUT, "hal-swap.svg"), W, H, *p,
           title="SITL зсередини: підміна на рівні HAL")


# ── fidelity: вісь точності бекендів фізики ──────────────────────────────────
# Ідея: «симулятор фізики» — не одне. Від легкої вбудованої моделі (швидко, грубо)
# через аеродинамічні рушії (JSBSim) до повного 3D-світу з сенсорами й камерою
# (Gazebo, AirSim) і аж до реального заліза (HIL). Що правіше — реалістичніше й
# важче; вибір бекенда — це вибір, ЩО саме ти хочеш перевірити.

def fig_fidelity():
    W, H = 820, 360
    p = []
    base = 300
    cols = [
        (40, 70, "вбудована модель", "груба фізика,\nмиттєвий старт", FIELD, GREENBG),
        (210, 110, "JSBSim / аеродинаміка", "точна динаміка\nпольоту", AMBER, AMBERBG),
        (400, 150, "Gazebo / AirSim", "3D-світ, зіткнення,\nкамера, лідар", NEG, BLUEBG),
        (590, 190, "реальне залізо (HIL)", "справжній чіп,\nреальний час", POS, REDBG),
    ]
    bw = 165
    for x, hh, name, note, col, fill in cols:
        y = base - hh
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, y, bw, hh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(x + bw / 2, y + 24, name, size=10.8, color=tagcol, bold=True))
        for j, ln in enumerate(note.split("\n")):
            p.append(text(x + bw / 2, y + 46 + j * 14, ln, size=9.2, color=INK))
    # вісь під стовпами
    p.append("<line x1=\"40\" y1=\"%d\" x2=\"790\" y2=\"%d\" stroke=\"%s\" stroke-width=\"1.6\" marker-end=\"url(#arrow)\"/>" % (base + 14, base + 14, MUTED))
    p.append(text(44, base + 32, "швидше / грубіше", size=9.6, color=MUTED, anchor="start"))
    p.append(text(786, base + 32, "реалістичніше / важче →", size=9.6, color=MUTED, anchor="end"))
    p.append(text(W / 2, H - 8, "вибір бекенда = вибір, що перевіряєш: логіку місії, динаміку польоту чи зір",
                  size=10.4, color=MUTED, italic=True))
    render(os.path.join(OUT, "fidelity.svg"), W, H, *p,
           title="Бекенди фізики SITL: від грубої моделі до 3D-світу")


if __name__ == "__main__":
    fig_loop()
    fig_sitl_vs_hil()
    fig_lockstep()
    fig_ci_place()
    fig_hal_swap()
    fig_fidelity()
    print("OK: figures written to", OUT)
