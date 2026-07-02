# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-tiers: дві шини й міст між ними ────────────────────────────────────────
# Ідея: швидкі майстри (ядро, пам'ять, DMA) на AHB; повільна периферія
# (UART, GPIO, таймер) на APB; між ними — міст, що є рабом на AHB і майстром на APB.

def fig_two_tiers():
    W, H = 760, 400
    p = []

    # ── верхня шина: AHB (швидка) ──
    ahb_y, ahb_x, ahb_w = 120, 60, 640
    p.append(rect(ahb_x, ahb_y, ahb_w, 30, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=4))
    p.append(text(ahb_x + ahb_w / 2, ahb_y + 20, "AHB — швидка шина (повна тактова частота, пакети, конвеєр)",
                  size=12, color=NEG, bold=True))

    # швидкі майстри/раби на AHB
    top_boxes = [(150, "ядро"), (330, "SRAM"), (500, "DMA")]
    for x, lab in top_boxes:
        b, bw, bh = textbox(x, 58, lab, size=12, bold=True, pad=11)
        p.append(b)
        p.append(line(x, 58 + bh / 2, x, ahb_y, color=NEG, sw=1.6))

    # ── міст ──
    br_cx = 620
    bridge, brw, brh = textbox(br_cx, 205, "міст\nAHB↔APB", size=12, bold=True,
                               fill="#fff9e6", stroke="#e0a800", sw=2.2, pad=12)
    p.append(bridge)
    p.append(line(br_cx, ahb_y + 30, br_cx, 205 - brh / 2, color="#e0a800", sw=2.0))
    p.append(text(br_cx + 60, ahb_y + 52, "раб на AHB", size=10, color=MUTED, anchor="start", italic=True))

    # ── нижня шина: APB (повільна) ──
    apb_y, apb_x, apb_w = 290, 60, 640
    p.append(rect(apb_x, apb_y, apb_w, 30, fill="#f4f6f8", stroke=INK, sw=1.8, rx=4))
    p.append(text(apb_x + apb_w / 2, apb_y + 20, "APB — повільна шина (проста, дешева, одне звертання за раз)",
                  size=12, color=INK, bold=True))
    p.append(line(br_cx, 205 + brh / 2, br_cx, apb_y, color="#e0a800", sw=2.0))
    p.append(text(br_cx + 60, apb_y - 8, "майстер на APB", size=10, color=MUTED, anchor="start", italic=True))

    # повільна периферія на APB
    bot_boxes = [(150, "UART"), (300, "GPIO"), (450, "таймер")]
    for x, lab in bot_boxes:
        b, bw, bh = textbox(x, 360, lab, size=12, bold=True,
                            fill="#d4edda", stroke=FIELD, sw=1.8, pad=11)
        p.append(b)
        p.append(line(x, apb_y + 30, x, 360 - bh / 2, color=FIELD, sw=1.6))

    render(os.path.join(OUT, "two-tiers.svg"), W, H, *p,
           title="Дві шини, один міст: швидке — на AHB, повільне — на APB")


# ── apb-fsm: автомат APB IDLE → SETUP → ACCESS ────────────────────────────────
# Ідея: кожне звертання по APB — рівно два такти. Перший (SETUP) виставляє адресу
# й PSEL; другий (ACCESS) піднімає PENABLE, і раб віддає дані по PREADY. Повільний
# раб тримає PREADY=0 і подовжує ACCESS зайвими тактами очікування.

def fig_apb_fsm():
    W, H = 720, 340
    p = []

    cy = 150
    # три стани в ряд
    idle, iw, ih = textbox(120, cy, "IDLE\n(спокій)", size=12, bold=True, pad=13)
    p.append(idle)
    setup, sw_, sh = textbox(360, cy, "SETUP\nтакт 1", size=12, bold=True,
                             fill="#eaf0fd", stroke=NEG, sw=2.0, pad=13)
    p.append(setup)
    acc, awd, ah = textbox(600, cy, "ACCESS\nтакт 2", size=12, bold=True,
                           fill="#d4edda", stroke=FIELD, sw=2.0, pad=13)
    p.append(acc)

    # переходи
    p.append(arrow(120 + iw / 2, cy, 360 - sw_ / 2, cy, color=INK, sw=1.8))
    p.append(text((120 + iw / 2 + 360 - sw_ / 2) / 2, cy - 12, "є звертання", size=10.5, color=INK))
    p.append(arrow(360 + sw_ / 2, cy, 600 - awd / 2, cy, color=INK, sw=1.8))
    p.append(text((360 + sw_ / 2 + 600 - awd / 2) / 2, cy - 12, "завжди", size=10.5, color=INK))

    # ACCESS → IDLE (готово) — дуга вниз
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (600, cy + ah / 2, 360, cy + 120, 120, cy + ih / 2, INK))
    p.append(text(360, cy + 118, "PREADY=1 → готово", size=10.5, color=FIELD, bold=True))

    # ACCESS сам на себе (очікування) — петля вгорі
    lx = 600
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (lx - 18, cy - ah / 2, lx, cy - 70, lx + 18, cy - ah / 2, POS))
    p.append(text(lx, cy - 74, "PREADY=0", size=10.5, color=POS, bold=True))
    p.append(text(lx, cy - 60, "такт очікування", size=9.5, color=POS))

    # підписи сигналів під станами
    p.append(text(360, cy + ih / 2 + 22, "PSEL=1, адреса виставлена, PENABLE=0", size=10, color=NEG))
    p.append(text(600, cy + ah / 2 + 22, "PENABLE=1, раб віддає дані", size=10, color=FIELD))

    render(os.path.join(OUT, "apb-fsm.svg"), W, H, *p,
           title="Кожне звертання по APB — два такти: SETUP, потім ACCESS")


# ── clock-domains: AHB на повній частоті, APB за дільником ─────────────────────
# Ідея: міст стоїть на межі двох тактових доменів. AHB цокає на повній HCLK;
# APB — за дільником, повільніше. Міст переносить звертання через межу, узгоджуючи
# темпи. Тому периферія на APB не тягне вниз частоту ядра й пам'яті на AHB.

def fig_clock_domains():
    W, H = 740, 320
    p = []

    # ── ліва зона: домен AHB ──
    p.append(rect(40, 70, 300, 200, fill="#f7f9ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(190, 96, "Домен AHB — HCLK повністю", size=12, color=NEG, bold=True))
    # швидкий такт: багато імпульсів
    _clock_wave(p, 70, 140, 250, n=8, col=NEG)
    p.append(text(190, 172, "напр. 180 МГц", size=11, color=NEG))
    core, cw, ch = textbox(190, 220, "ядро · SRAM · DMA", size=11, bold=True, pad=10)
    p.append(core)

    # ── права зона: домен APB ──
    p.append(rect(400, 70, 300, 200, fill="#f5faf6", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(550, 96, "Домен APB — HCLK ÷ дільник", size=12, color=FIELD, bold=True))
    # повільний такт: удвічі менше імпульсів
    _clock_wave(p, 430, 140, 610, n=4, col=FIELD)
    p.append(text(550, 172, "напр. 45 МГц", size=11, color=FIELD))
    per, pw, ph = textbox(550, 220, "UART · GPIO · таймер", size=11, bold=True,
                          fill="#d4edda", stroke=FIELD, sw=1.8, pad=10)
    p.append(per)

    # ── міст на межі ──
    p.append(line(370, 70, 370, 270, color="#e0a800", sw=2.4, dash="6 4"))
    br, brw, brh = textbox(370, 300, "міст переносить звертання через межу доменів",
                           size=11, bold=True, fill="#fff9e6", stroke="#e0a800", sw=1.8, pad=8)
    p.append(br)

    render(os.path.join(OUT, "clock-domains.svg"), W, H, *p,
           title="Міст стоїть на межі: швидкий такт AHB, повільніший APB")


# ── amba-timeline: три віхи AMBA й незмінна APB червоною ниткою ─────────────────
# Ідея: 1996 (ASB+APB) → 1999 (додано AHB, один фронт такту) → 2003 (AXI). Крізь
# усі роки тягнеться проста APB — вона переживає всі перевороти системної шини.

def fig_amba_timeline():
    W, H = 760, 360
    p = []

    # горизонтальна вісь часу
    axis_y = 300
    p.append(line(60, axis_y, 700, axis_y, color=INK, sw=2.0))
    p.append(arrow(680, axis_y, 705, axis_y, color=INK, sw=2.0))
    p.append(text(700, axis_y + 22, "час", size=11, color=MUTED, anchor="end", italic=True))

    # три віхи: (x, рік, підпис-версія, що з'явилося)
    milestones = [
        (170, "1996", "AMBA 1", "ASB + APB", NEG),
        (400, "1999", "AMBA 2", "+ AHB\n(один фронт такту)", FIELD),
        (630, "2003", "AMBA 3", "+ AXI, ATB", POS),
    ]
    for x, year, ver, what, col in milestones:
        p.append(circle(x, axis_y, 7, fill=col, stroke=col, sw=2))
        p.append(text(x, axis_y + 22, year, size=13, color=col, bold=True))
        b, bw, bh = textbox(x, 110, ver + "\n" + what, size=11, bold=True,
                            fill="#f7f9ff", stroke=col, sw=1.8, pad=10)
        p.append(b)
        p.append(line(x, 110 + bh / 2, x, axis_y - 7, color=col, sw=1.5, dash="4 3"))

    # червона нитка APB: тягнеться крізь усі роки, незмінна
    thread_y = 250
    p.append(line(120, thread_y, 690, thread_y, color=POS, sw=2.6))
    p.append(text(400, thread_y - 10, "APB — незмінна проста периферійна шина крізь усі покоління",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "amba-timeline.svg"), W, H, *p,
           title="Три віхи AMBA: швидка дорога росте, проста APB лишається")


def _clock_wave(p, x0, y, x1, n, col):
    """Малий прямокутний такт: n повних імпульсів між x0 і x1."""
    step = (x1 - x0) / (2 * n)
    hi, lo = y - 16, y
    pts = [(x0, lo)]
    x = x0
    for i in range(n):
        pts.append((x, hi)); x += step
        pts.append((x, hi)); pts.append((x, lo)); x += step
        pts.append((x, lo))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pt for pt in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (d, col))


if __name__ == "__main__":
    fig_two_tiers()
    fig_apb_fsm()
    fig_clock_domains()
    fig_amba_timeline()
    print("OK: figures written to", OUT)
