# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── scan-chain: реєстри чипа нанизані на одну нитку TDI→TDO ────────────────────
# Ідея: усі службові реєстри з'єднані послідовно в один довгий зсувний регістр;
# дані протягуються крізь усе ядро за такти TCK — доступ ціною серіалізації.

def fig_scan_chain():
    W, H = 720, 250
    p = []
    y = 120
    bw, bh = 96, 56
    gap = 34
    n = 4
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    labels = ["реєстр\nкерування", "стан\nядра", "тестові\nклітинки", "межовий\nскан"]
    cx = []
    for i in range(n):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, y - bh / 2, bw, bh, labels[i], size=11, bold=True,
                        fill="#eef4ff", stroke=INK, sw=1.5))
        cx.append((x, x + bw))
    # нитка крізь усі реєстри
    for i in range(n - 1):
        p.append(arrow(cx[i][1], y, cx[i + 1][0] - 2, y, color=INK, sw=2.0))
    # вхід TDI зліва, вихід TDO справа
    p.append(arrow(x0 - 56, y, x0 - 2, y, color=NEG, sw=2.2))
    p.append(text(x0 - 56, y - 12, "TDI", size=12, color=NEG, anchor="start", bold=True))
    p.append(arrow(cx[-1][1], y, cx[-1][1] + 54, y, color=POS, sw=2.2))
    p.append(text(cx[-1][1] + 54, y - 12, "TDO", size=12, color=POS, anchor="end", bold=True))
    # такт TCK збоку
    p.append(text(W / 2, y + bh / 2 + 30, "кожен імпульс TCK зсуває весь ланцюг на один біт",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "scan-chain.svg"), W, H, *p,
           title="Усі реєстри чипа — одна нитка від TDI до TDO")


# ── jtag-vs-swd: ті самі можливості, різна кількість ліній ─────────────────────
# Ідея: чотири лінії JTAG проти двох ліній SWD ведуть до ОДНОГО блока в чипі;
# SWD об'єднує дані й керування в одну двоспрямовану лінію.

def fig_jtag_vs_swd():
    W, H = 720, 300
    p = []
    # спільна ціль праворуч
    tx, ty, tw, th = W - 180, 100, 150, 100
    p.append(rect(tx, ty, tw, th, fill="#f6f4ec", stroke=INK, sw=2))
    p.append(mtext(tx + tw / 2, ty + th / 2 - 6, ["відлагоджу-", "вальний блок", "у ядрі"],
                   size=12, bold=True))

    # JTAG зверху-зліва: 4 лінії
    jx = 60
    jlabels = ["TCK такт", "TMS режим", "TDI вхід", "TDO вихід"]
    jy0 = 56
    for i, lab in enumerate(jlabels):
        yy = jy0 + i * 26
        p.append(text(jx, yy, lab, size=11, color=NEG, anchor="start", bold=(i == 0)))
    p.append(text(jx, jy0 - 22, "JTAG — 4 лінії", size=13, color=NEG, anchor="start", bold=True))
    p.append(arrow(jx + 150, jy0 + 30, tx - 4, ty + 24, color=NEG, sw=1.8))

    # SWD знизу-зліва: 2 лінії
    sy0 = 196
    slabels = ["SWCLK такт", "SWDIO дані ⇄ керування"]
    for i, lab in enumerate(slabels):
        yy = sy0 + i * 26
        p.append(text(jx, yy, lab, size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(jx, sy0 - 22, "SWD — 2 лінії", size=13, color=FIELD, anchor="start", bold=True))
    p.append(arrow(jx + 220, sy0 + 14, tx - 4, ty + th - 24, color=FIELD, sw=1.8))

    p.append(text(W / 2, H - 16, "та сама сила — SWDIO суміщає TDI, TDO і TMS, перемикаючи напрям",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "jtag-vs-swd.svg"), W, H, *p,
           title="JTAG і SWD ведуть до одного блока, різним числом ліній")


# ── debug-port-into-core: дріт ззовні → порт → запис у реальний регістр ────────
# Ідея: halt не магія — це запис 1 у конкретний біт апаратного регістра DAP
# через відлагоджувальний порт; ланцюг доступу йде до пам'яті через AP.

def fig_debug_port():
    W, H = 720, 300
    p = []
    # зонд зліва
    p.append(fitbox(40, 120, 110, 60, "зонд\n(host)", size=12, bold=True,
                    fill=FILL, stroke=INK, sw=1.6))
    # порт у чипі
    p.append(fitbox(210, 120, 120, 60, "порт\nSWD / JTAG", size=12, bold=True,
                    fill="#eef4ff", stroke=INK, sw=1.6))
    p.append(arrow(150, 150, 208, 150, color=INK, sw=2.0))
    p.append(text(179, 138, "2–4 дроти", size=10, color=MUTED))
    # DAP
    p.append(fitbox(390, 120, 110, 60, "DAP\n(DP + AP)", size=12, bold=True,
                    fill="#eafaf0", stroke=INK, sw=1.6))
    p.append(arrow(330, 150, 388, 150, color=INK, sw=2.0))
    # цільовий регістр / шина
    p.append(fitbox(560, 60, 130, 56, "регістр HALT\nядра", size=11, bold=True,
                    fill="#fdecea", stroke=POS, sw=1.8, color=POS))
    p.append(fitbox(560, 184, 130, 56, "пам'ять / шина\nчерез AP", size=11, bold=True,
                    fill="#f2ecf8", stroke="#8a5fb0", sw=1.8, color="#8a5fb0"))
    p.append(arrow(500, 140, 558, 96, color=POS, sw=1.8))
    p.append(arrow(500, 162, 558, 206, color="#8a5fb0", sw=1.8))

    p.append(text(W / 2, H - 16, "halt = запис 1 у біт реального регістра; читання пам'яті — через AP",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "debug-port-into-core.svg"), W, H, *p,
           title="Як дріт ззовні дотягується до нутрощів ядра")


# ── esp32-jtag-pins: піни JTAG на ESP32 і конфлікт зі strapping ────────────────
# Ідея: класичний ESP32 віддає 4 GPIO під JTAG, причому два з них — strapping;
# нові чипи дають USB-JTAG прямо по USB, без зовнішнього зонда й без конфлікту.

def fig_esp32_pins():
    W, H = 720, 320
    p = []
    # лівий блок: класичний ESP32
    lx = 40
    p.append(text(lx, 56, "Класичний ESP32 / S2 — 4 GPIO", size=13, color=INK, anchor="start", bold=True))
    pins = [
        ("MTCK", "GPIO13", FILL, INK),
        ("MTDI", "GPIO12", "#fdf6e3", POS),
        ("MTMS", "GPIO14", FILL, INK),
        ("MTDO", "GPIO15", "#fdf6e3", POS),
    ]
    y = 78
    for sig, gpio, fill, col in pins:
        p.append(rect(lx, y, 150, 36, fill=fill, stroke=col, sw=1.5))
        p.append(text(lx + 10, y + 23, sig, size=12, color=col, anchor="start", bold=True))
        p.append(text(lx + 142, y + 23, gpio, size=11, color=MUTED, anchor="end"))
        y += 44
    p.append(text(lx, y + 14, "GPIO12/15 — strapping:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(lx, y + 32, "хибний рівень при reset зриває", size=10, color=POS, anchor="start"))
    p.append(text(lx, y + 48, "завантаження", size=10, color=POS, anchor="start"))

    # роздільник
    p.append(line(W / 2 + 10, 50, W / 2 + 10, H - 30, color="#dddddd", sw=1.2, dash="4 4"))

    # правий блок: нові чипи — USB-JTAG
    rx = W / 2 + 50
    p.append(text(rx, 56, "ESP32-S3 / C3 / C6 — USB-JTAG", size=13, color=FIELD, anchor="start", bold=True))
    p.append(fitbox(rx, 88, 150, 50, "один\nUSB-кабель", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD))
    p.append(arrow(rx + 150, 113, rx + 200, 113, color=FIELD, sw=2.0))
    p.append(fitbox(rx + 200, 88, 60, 50, "чип", size=12, bold=True,
                    fill=FILL, stroke=INK, sw=1.5))
    benefits = ["прошивка", "відлагодження", "консоль", "— без зонда, без конфлікту GPIO"]
    yy = 168
    for b in benefits:
        p.append(text(rx, yy, "• " + b if not b.startswith("—") else b,
                      size=11, color=(MUTED if b.startswith("—") else INK), anchor="start"))
        yy += 22

    render(os.path.join(OUT, "esp32-jtag-pins.svg"), W, H, *p,
           title="JTAG коштує ніжок; на нових ESP32 він іде прямо по USB")


# ── swd-frame: кадр транзакції SWD біт-за-бітом (read) ─────────────────────────
# Ідея: показати три фази однієї read-транзакції — запит (8 біт), ACK (3 біти),
# дані (32 біти + парність) — і де між ними вставлено такт зміни напряму Trn.

def fig_swd_frame():
    W, H = 720, 250
    p = []
    y = 110
    bh = 46

    def seg(x, w, lab, sub, fill, col):
        p.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.6))
        p.append(text(x + w / 2, y + 20, lab, size=11, color=col, bold=True))
        if sub:
            p.append(text(x + w / 2, y + 37, sub, size=9, color=MUTED))
        return x + w

    x = 40
    x = seg(x, 150, "Запит (host→)", "8 біт", "#eef4ff", NEG)
    x = seg(x, 34, "Trn", "↻", "#efefef", MUTED)
    x = seg(x, 90, "ACK (→host)", "3 біти", "#eafaf0", FIELD)
    x = seg(x, 230, "Дані (→host)", "32 біти + парність", "#fdf6e3", "#9a7d1a")
    x = seg(x, 34, "Trn", "↻", "#efefef", MUTED)

    # розпис полів запиту під смугою
    p.append(text(40, y + bh + 30, "Запит: Start·APnDP·RnW·A[2]·A[3]·Parity·Stop·Park  (LSB-перший)",
                  size=11, color=INK, anchor="start"))
    p.append(text(40, y + bh + 50, "ACK: OK=001 · WAIT=010 · FAULT=100  (LSB-перший)",
                  size=11, color=INK, anchor="start"))
    p.append(text(40, y - 16, "Кадр читання DP/AP-регістра по одній лінії SWDIO",
                  size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "swd-frame.svg"), W, H, *p,
           title="Один кадр SWD: запит → ACK → дані, з тактами зміни напряму")


# ════════════════ Фігури ДЕТАЛЬНОЇ версії (swd-jtag-internals-d.md) ════════════
# Імена з префіксом «d-», щоб не плутати з фігурами базової статті у тій самій ./img/.


# ── d-tap-fsm: автомат TAP на 16 станів, дві гілки IR/DR ───────────────────────
# Ідея: показати, що TMS веде автомат двома симетричними гілками (DR і IR);
# на кожному ребрі підписано значення TMS; 5×1 завжди приводить у TLR.

def fig_tap_fsm():
    W, H = 760, 560
    p = []

    def node(cx, cy, label, fill="#eef4ff", col=INK, w=118, h=38):
        p.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=1.6, rx=8))
        fs = fit_font(label, w - 12, 11, False)
        p.append(text(cx, cy + 4, label, size=fs, color=col, bold=True))
        return (cx, cy, w, h)

    def edge(a, b, tms, side="mid", color=INK):
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        p.append(arrow(ax, ay + (a[3] / 2 if by > ay else -a[3] / 2),
                       bx, by - (b[3] / 2 if by > ay else -b[3] / 2), color=color, sw=1.5))
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx = -16 if side == "left" else (16 if side == "right" else 0)
        p.append(text(mx + dx, my, str(tms), size=10, color=POS if tms == 1 else NEG, bold=True))

    tlr = node(W / 2, 50, "Test-Logic-Reset", fill="#fdecea", col=POS, w=150)
    rti = node(W / 2, 130, "Run-Test/Idle", fill="#eafaf0", col=FIELD, w=140)

    dx = 200
    sds = node(dx, 210, "Select-DR-Scan")
    cap_dr = node(dx, 280, "Capture-DR")
    sh_dr = node(dx, 350, "Shift-DR", fill="#dcecff", col=NEG)
    e1_dr = node(dx, 420, "Exit1-DR")
    upd_dr = node(dx, 490, "Update-DR")

    ix = W - 200
    sis = node(ix, 210, "Select-IR-Scan")
    cap_ir = node(ix, 280, "Capture-IR")
    sh_ir = node(ix, 350, "Shift-IR", fill="#dcecff", col=NEG)
    e1_ir = node(ix, 420, "Exit1-IR")
    upd_ir = node(ix, 490, "Update-IR")

    edge(rti, tlr, 1)
    edge(rti, sds, 1, "left")
    edge(sds, sis, 1, "mid")
    edge(sds, cap_dr, 0, "left")
    edge(cap_dr, sh_dr, 0, "left")
    edge(sh_dr, e1_dr, 1, "left")
    edge(e1_dr, upd_dr, 1, "left")
    edge(sis, cap_ir, 0, "right")
    edge(cap_ir, sh_ir, 0, "right")
    edge(sh_ir, e1_ir, 1, "right")
    edge(e1_ir, upd_ir, 1, "right")

    for nd in (sh_dr, sh_ir):
        lx = nd[0] - nd[2] / 2 - 18
        p.append('<path d="M%.1f %.1f q -26 0 -26 -18 q 0 -18 26 -18" fill="none" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
                 % (lx, nd[1] + 8, NEG))
        p.append(text(lx - 30, nd[1] - 6, "0", size=10, color=NEG, bold=True))

    p.append(text(W / 2, H - 14, "TMS читається на фронті TCK; «1» п'ять разів поспіль → Test-Logic-Reset з будь-якого стану",
                  size=11, color=MUTED, italic=True))
    p.append(text(dx, 178, "гілка даних (DR)", size=11, color=NEG, bold=True))
    p.append(text(ix, 178, "гілка інструкцій (IR)", size=11, color=NEG, bold=True))

    render(os.path.join(OUT, "d-tap-fsm.svg"), W, H, *p,
           title="Автомат TAP: дві симетричні гілки, керовані TMS")


# ── d-swd-bits: кадр read і кадр write біт-за-бітом, з напрямом SWDIO ──────────
# Ідея: дві смуги однакового масштабу; видно, де лінію жене host, де чип,
# і де такти зміни напряму; на read turnaround між ACK і даними НЕ потрібен,
# на write — потрібен.

def fig_swd_bits():
    W, H = 760, 420
    p = []
    unit = 7.0
    x0 = 70

    HOST = "#eef4ff"; HCOL = NEG
    CHIP = "#eafaf0"; CCOL = FIELD
    TRN = "#efefef"; TCOL = MUTED

    def band(y, title, segs):
        p.append(text(x0, y - 12, title, size=12, color=INK, anchor="start", bold=True))
        x = x0
        for lab, n, fill, col in segs:
            w = n * unit
            p.append(rect(x, y, w, 40, fill=fill, stroke=col, sw=1.4, rx=3))
            if w > 26:
                fs = fit_font(lab, w - 4, 10, False, min_size=9)
                p.append(text(x + w / 2, y + 16, lab, size=fs, color=col))
                p.append(text(x + w / 2, y + 31, str(n) + " б", size=9, color=MUTED))
            x += w
        return x

    band(70, "Читання (RnW=1): turnaround між запитом і ACK, дані йдуть одразу за ACK",
         [("запит host", 8, HOST, HCOL), ("Trn", 1, TRN, TCOL),
          ("ACK чип", 3, CHIP, CCOL), ("дані чип", 32, CHIP, CCOL),
          ("par", 1, CHIP, CCOL), ("Trn", 1, TRN, TCOL)])

    band(180, "Запис (RnW=0): після ACK ще один turnaround, бо дані знову жене host",
         [("запит host", 8, HOST, HCOL), ("Trn", 1, TRN, TCOL),
          ("ACK чип", 3, CHIP, CCOL), ("Trn", 1, TRN, TCOL),
          ("дані host", 32, HOST, HCOL), ("par", 1, HOST, HCOL)])

    yq = 280
    p.append(text(x0, yq - 6, "8-бітний запит, молодший біт першим:", size=12, color=INK, anchor="start", bold=True))
    fields = [("Start\n=1", "#f6f4ec"), ("APnDP", HOST), ("RnW", HOST),
              ("A[2]", HOST), ("A[3]", HOST), ("Par", "#fdf6e3"),
              ("Stop\n=0", "#f6f4ec"), ("Park\n=1", "#f6f4ec")]
    fw = 78
    x = x0
    for lab, fill in fields:
        p.append(rect(x, yq + 6, fw, 44, fill=fill, stroke=INK, sw=1.3, rx=4))
        p.append(mtext(x + fw / 2, yq + 24, lab, size=10, color=INK))
        x += fw + 4
    p.append(text(x0, yq + 72, "Par — біт непарності над APnDP·RnW·A[2]·A[3]; стартовий і park завжди 1, стоп завжди 0",
                  size=10, color=MUTED, anchor="start", italic=True))

    ly = 386
    p.append(rect(x0, ly, 16, 12, fill=HOST, stroke=HCOL, sw=1.3))
    p.append(text(x0 + 22, ly + 11, "жене host", size=10, color=HCOL, anchor="start"))
    p.append(rect(x0 + 130, ly, 16, 12, fill=CHIP, stroke=CCOL, sw=1.3))
    p.append(text(x0 + 152, ly + 11, "жене чип", size=10, color=CCOL, anchor="start"))
    p.append(rect(x0 + 260, ly, 16, 12, fill=TRN, stroke=TCOL, sw=1.3))
    p.append(text(x0 + 282, ly + 11, "Trn — нічий такт зміни напряму", size=10, color=TCOL, anchor="start"))

    render(os.path.join(OUT, "d-swd-bits.svg"), W, H, *p,
           title="Кадр SWD біт-за-бітом: читання і запис")


# ── d-dp-ap-map: мапа регістрів DP та AP, маршрут через SELECT ─────────────────
# Ідея: дві таблиці (DP і MEM-AP) з адресами A[3:2]; стрілка SELECT показує,
# що DP-регістр SELECT задає, ЯКИЙ AP і банк адресують наступні AP-доступи.

def fig_dp_ap_map():
    W, H = 760, 420
    p = []

    def table(x, y, title, rows, col):
        rw, rh = 300, 34
        p.append(text(x, y - 10, title, size=13, color=col, anchor="start", bold=True))
        p.append(rect(x, y, rw, rh, fill=col, stroke=col, sw=1.4, rx=6))
        p.append(text(x + 14, y + 22, "адреса A[3:2]", size=11, color=BG, anchor="start", bold=True))
        p.append(text(x + 150, y + 22, "регістр (R / W)", size=11, color=BG, anchor="start", bold=True))
        yy = y + rh
        for addr, name in rows:
            p.append(rect(x, yy, rw, rh, fill=FILL, stroke="#d7dde6", sw=1.0, rx=0))
            p.append(text(x + 14, yy + 22, addr, size=11, color=INK, anchor="start"))
            p.append(text(x + 150, yy + 22, name, size=11, color=INK, anchor="start"))
            yy += rh
        return (x, y, rw, yy)

    dp = table(40, 70, "DP — Debug Port (говорить дріт)", [
        ("0b00", "IDCODE (R) / ABORT (W)"),
        ("0b01", "CTRL/STAT (R/W)*"),
        ("0b10", "SELECT (W) / RESEND (R)"),
        ("0b11", "RDBUFF (R)"),
    ], NEG)

    ap = table(420, 70, "MEM-AP — міст до шини", [
        ("0x00", "CSW (R/W) — режим доступу"),
        ("0x04", "TAR (R/W) — адреса в пам'яті"),
        ("0x0C", "DRW (R/W) — дані"),
        ("0xF8", "BASE / IDR — опис AP"),
    ], "#8a5fb0")

    p.append(arrow(dp[0] + dp[2], 70 + 34 * 3 - 17, ap[0] - 4, 70 + 16,
                   color=POS, sw=1.9))
    p.append(text((dp[0] + dp[2] + ap[0]) / 2, 70 + 34 * 2 + 4,
                  "SELECT задає,", size=10, color=POS, bold=True))
    p.append(text((dp[0] + dp[2] + ap[0]) / 2, 70 + 34 * 2 + 18,
                  "ЯКИЙ AP і банк", size=10, color=POS, bold=True))

    p.append(text(40, dp[3] + 26, "* який саме регістр на 0b01 і 0b10 — залежить від поля DPBANKSEL у SELECT",
                  size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(40, dp[3] + 46, "Читання AP запізнюється на крок: значення приходить у наступному читанні або з RDBUFF",
                  size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "d-dp-ap-map.svg"), W, H, *p,
           title="Мапа регістрів: DP веде дріт, AP веде до пам'яті")


# ── d-jtag-to-swd: послідовність перемикання каналу ───────────────────────────
# Ідея: лінійка кроків; ключове — магічне 16-бітне слово між двома line-reset,
# і що все завершується читанням IDCODE як перевіркою.

def fig_jtag_to_swd():
    W, H = 760, 250
    p = []
    y = 110
    bh = 64
    steps = [
        ("≥50 тактів\nSWDIO=1", "line reset", "#eef4ff", NEG),
        ("0111100111100111", "0x79E7 (MSB)\n= 0xE79E (LSB)", "#fdf6e3", "#9a7d1a"),
        ("≥50 тактів\nSWDIO=1", "line reset", "#eef4ff", NEG),
        ("≥2 такти\nSWDIO=0", "idle", "#eafaf0", FIELD),
        ("читати\nIDCODE", "перевірка", "#fdecea", POS),
    ]
    n = len(steps)
    gap = 26
    bw = (W - 80 - (n - 1) * gap) / n
    x = 40
    centers = []
    for lab, sub, fill, col in steps:
        p.append(rect(x, y - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        fs = fit_font(max(lab.split("\n"), key=len), bw - 10, 11, True)
        p.append(mtext(x + bw / 2, y - 4, lab, size=fs, color=col, bold=True))
        p.append(text(x + bw / 2, y + bh / 2 + 16, sub.replace("\n", " "), size=9, color=MUTED))
        centers.append((x, x + bw))
        x += bw + gap
    for i in range(n - 1):
        p.append(arrow(centers[i][1], y, centers[i + 1][0] - 2, y, color=INK, sw=1.8))

    p.append(text(W / 2, H - 16, "магічне слово між двома line-reset перемикає SWJ-DP із JTAG у SWD; IDCODE підтверджує успіх",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "d-jtag-to-swd.svg"), W, H, *p,
           title="Перемикання JTAG → SWD: послідовність на одній лінії")


# ── d-daisy-chain: ланцюг JTAG із кількох чипів проти одиночної цілі SWD ───────
# Ідея: у JTAG TDI→TDO проходить крізь УСІ чипи послідовно (IR-и складаються,
# зайві в BYPASS = 1 біт); SWD адресує один чип, ланцюга нема.

def fig_daisy_chain():
    W, H = 760, 330
    p = []
    p.append(text(40, 50, "JTAG: TDI → TDO крізь усі чипи; зайві ставимо в BYPASS (1 біт)",
                  size=12, color=NEG, anchor="start", bold=True))
    y = 96
    bw, bh = 130, 56
    gap = 44
    chips = [("чип A\nBYPASS", FILL, INK), ("чип B\n(ціль, IR)", "#dcecff", NEG), ("чип C\nBYPASS", FILL, INK)]
    x = 90
    cxs = []
    for lab, fill, col in chips:
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(mtext(x + bw / 2, y + bh / 2 - 4, lab.split("\n"), size=11, color=col, bold=True))
        cxs.append((x, x + bw))
        x += bw + gap
    p.append(arrow(34, y + bh / 2, cxs[0][0] - 2, y + bh / 2, color=NEG, sw=2.0))
    p.append(text(34, y + bh / 2 - 10, "TDI", size=11, color=NEG, anchor="start", bold=True))
    for i in range(len(chips) - 1):
        p.append(arrow(cxs[i][1], y + bh / 2, cxs[i + 1][0] - 2, y + bh / 2, color=NEG, sw=2.0))
    p.append(arrow(cxs[-1][1], y + bh / 2, cxs[-1][1] + 40, y + bh / 2, color=POS, sw=2.0))
    p.append(text(cxs[-1][1] + 40, y + bh / 2 - 10, "TDO", size=11, color=POS, anchor="end", bold=True))
    p.append(text(W / 2, y + bh + 22, "TCK і TMS — паралельно всім; довжина зсуву = сума IR усіх чипів",
                  size=10, color=MUTED, italic=True))

    p.append(line(60, 210, W - 60, 210, color="#dddddd", sw=1.2, dash="5 5"))

    p.append(text(40, 244, "SWD: один чип на лінії; ланцюга немає (кілька — лише через multidrop за адресою)",
                  size=12, color=FIELD, anchor="start", bold=True))
    yy = 268
    p.append(fitbox(90, yy, 120, 50, "зонд", size=12, bold=True, fill=FILL, stroke=INK, sw=1.5))
    p.append(arrow(210, yy + 25, 268, yy + 25, color=FIELD, sw=2.2))
    p.append(text(239, yy + 16, "2 лінії", size=10, color=MUTED))
    p.append(fitbox(268, yy, 140, 50, "один чип\n(SW-DP)", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD))

    render(os.path.join(OUT, "d-daisy-chain.svg"), W, H, *p,
           title="Кілька пристроїв: ланцюг JTAG проти одиночної цілі SWD")


if __name__ == "__main__":
    # базова стаття
    fig_scan_chain()
    fig_jtag_vs_swd()
    fig_debug_port()
    fig_esp32_pins()
    fig_swd_frame()
    # детальна версія
    fig_tap_fsm()
    fig_swd_bits()
    fig_dp_ap_map()
    fig_jtag_to_swd()
    fig_daisy_chain()
    print("OK: figures written to", OUT)
