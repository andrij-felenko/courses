# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── host-device-roles: асиметрія USB — хост ініціює, пристрій лише відповідає ──
# Ідея: одне рішення «рівних немає» пояснює всю шину. Хост шле запит (суцільна),
# пристрій озивається тільки у відповідь (пунктир) — звідси немає колізій і
# прошивка-device виходить реактивною. Контраст із рівноправними I²C/SPI.
def fig_host_device_roles():
    W, H = 760, 380
    p = []
    hb, hbw, hbh = textbox(150, 150, ["ХОСТ", "(ПК, смартфон)"], size=15, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=2.2, min_w=200)
    p.append(hb)
    p.append(mtext(150, 200, ["Ініціює ВСЕ:", "запити · темп · адреси"],
                   size=11, color=MUTED, lh=1.3))
    db, dbw, dbh = textbox(610, 150, ["ПРИСТРІЙ", "(ESP32, флешка)"], size=15, bold=True,
                           fill="#f4f6f8", stroke=LINE, sw=2.2, min_w=200)
    p.append(db)
    p.append(mtext(610, 200, ["Лише ВІДПОВІДАЄ:", "ніколи не першим"],
                   size=11, color=MUTED, lh=1.3))
    # запит: хост → пристрій (суцільна)
    p.append(arrow(255, 120, 505, 120, color=NEG, sw=2.0))
    p.append(text(380, 110, "запит (хост → пристрій)", size=11, color=NEG, bold=True))
    # відповідь: тільки у відповідь (пунктир)
    p.append(line(505, 180, 258, 180, color=MUTED, sw=1.8, dash="8,4"))
    p.append(text(503, 180, "◄", size=12, color=MUTED))
    p.append(text(380, 198, "відповідь (тільки у відповідь)", size=11, color=MUTED, bold=True))
    p.append(fitbox(150, 300, 460, 48,
                    "Ніхто не говорить без дозволу → колізій немає, пристрій реактивний",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.6, bold=True))
    return render(os.path.join(OUT, "host-device-roles.svg"), W, H, *p,
                  title="Асиметрія USB: хост ініціює, пристрій відповідає")


# ── usb-tree: ярусно-зіркова топологія — корінь-хост, гілки через хаби ─────────
# Ідея: один фізичний порт ПК = ціле дерево. Корінь — хост; хаби розгалужують
# одне з'єднання у кілька портів; листя — кінцеві пристрої. До 127 адрес, до 7
# ярусів. Листя не «бачать» одне одного — весь трафік через хост.
def fig_usb_tree():
    W, H = 760, 420
    p = []
    def node(cx, cy, label, sub, col, fill, w=150):
        b, bw, bh = textbox(cx, cy, label, size=13, bold=True, color=col,
                            fill=fill, stroke=col, sw=2.0, min_w=w)
        out = [b]
        if sub:
            out.append(text(cx, cy + bh / 2 + 14, sub, size=10, color=MUTED, italic=True))
        return out, bh
    # ярус 0: хост (корінь)
    host, hh = node(380, 70, "ХОСТ (корінь)", "кореневий хаб у ПК", NEG, "#eaf0fd", 200)
    p += host
    # ярус 1: два хаби
    hubs = [(200, 200, "Хаб"), (560, 200, "Хаб")]
    for hx, hy, lab in hubs:
        hb, _ = node(hx, hy, lab, "сам — USB-пристрій", FIELD, "#eafaf1", 130)
        p += hb
        p.append(line(380, 70 + 22, hx, hy - 22, color=LINE, sw=1.4))
    # ярус 2: листя
    leaves = [(110, 330, "миша"), (250, 330, "флешка"),
              (470, 330, "вебкамера"), (620, 330, "клавіатура")]
    parents = [200, 200, 560, 560]
    for (lx, ly, lab), px in zip(leaves, parents):
        lb, _ = node(lx, ly, lab, None, INK, "#f4f6f8", 110)
        p += lb
        p.append(line(px, 200 + 22, lx, ly - 18, color=LINE, sw=1.2))
    p.append(fitbox(180, 372, 400, 38,
                    "До 127 адрес · до 7 ярусів · листя не бачать одне одного",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    return render(os.path.join(OUT, "usb-tree.svg"), W, H, *p,
                  title="Топологія USB: ярусно-зіркове дерево з хабами")


# ── address-count: один порт ноутбука — скільки адрес зайнято на дереві ────────
# Ідея: ліміт 127 — про адреси на дереві, не про фізичні гнізда. Один порт несе
# хаб монітора з трьома пристроями (композит = 1 адреса на дві функції) і
# зовнішній хаб ще з двома — разом дев'ять адрес, ліміт ще далеко.
def fig_address_count():
    W = 720
    rows = [
        ("1", "кореневий хаб #1", FIELD),
        ("2", "хаб монітора", FIELD),
        ("3", "клавіатура+тачпад (композит: 2 функції, 1 адреса)", NEG),
        ("4", "флешка", INK),
        ("5", "вебкамера", INK),
        ("6", "кореневий хаб #2", FIELD),
        ("7", "зовнішній хаб", FIELD),
        ("8", "аудіоінтерфейс", INK),
        ("9", "другий монітор", INK),
    ]
    top, rh = 56, 32
    H = top + len(rows) * rh + 58
    p = []
    for i, (addr, lab, col) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            p.append(rect(24, y, W - 48, rh - 4, fill="#f4f6f8", stroke="none", sw=0, rx=4))
        p.append(circle(52, y + (rh - 4) / 2, 13, fill="#eaf0fd", stroke=NEG, sw=1.6))
        p.append(text(52, y + (rh - 4) / 2 + 5, addr, size=13, color=NEG, bold=True))
        p.append(text(80, y + (rh - 4) / 2 + 5, lab, size=13, color=col, anchor="start"))
    by = top + len(rows) * rh + 8
    p.append(fitbox(40, by, W - 80, 40,
                    "Разом 9 адрес, яруси 1–3 — ліміт 127 ще далеко (він про адреси, не про гнізда)",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    return render(os.path.join(OUT, "address-count.svg"), W, H, *p,
                  title="Один порт ноутбука — скільки адрес зайнято")


# ── connector-zoo: до USB — сім несумісних інтерфейсів проти одного роз'єму ────
# Ідея (вставка hist): головна обіцянка USB — не швидкість, а ОДИН роз'єм
# замість зоопарку. Зліва — сім інтерфейсів, кожен зі своїм кабелем і драйвером;
# праворуч — один USB на всіх.
def fig_connector_zoo():
    W, H = 780, 410
    p = []
    zoo = [
        ("PS/2 (миша)", "круглий, 6 pin"),
        ("PS/2 (клавіатура)", "круглий, 6 pin"),
        ("DB-9 RS-232", "серійний порт"),
        ("DB-25 LPT", "паралельний, принтер"),
        ("SCSI", "жорсткий диск, сканер"),
        ("Ігровий / MIDI", "джойстик, синтезатор"),
        ("ADB", "тільки на Mac"),
    ]
    bw, bh, gap = 180, 42, 8
    col_x = [24, 218]
    for i, (name, sub) in enumerate(zoo):
        cx = col_x[i % 2]
        cy = 56 + (i // 2) * (bh + gap)
        p.append(rect(cx, cy, bw, bh, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=6))
        p.append(text(cx + bw / 2, cy + 18, name, size=12, color=INK, bold=True))
        p.append(text(cx + bw / 2, cy + 34, sub, size=10, color=MUTED))
    # стрілка «USB замінив усі сім»
    p.append(arrow(420, 200, 480, 200, color=POS, sw=4.0))
    p.append(text(450, 186, "USB", size=12, color=POS, bold=True))
    p.append(text(450, 226, "замінив усі", size=11, color=POS, bold=True))
    # праворуч: один роз'єм
    ub, ubw, ubh = textbox(620, 200, ["USB Type-A", "один роз'єм на всіх"], size=15, bold=True,
                           color=NEG, fill="#eaf0fd", stroke=NEG, sw=2.8, min_w=230)
    p.append(ub)
    p.append(text(620, 200 + ubh / 2 + 18, "USB 1.0 — січень 1996", size=11, color=MUTED, italic=True))
    p.append(fitbox(40, 360, 700, 38,
                    "Головна обіцянка — один роз'єм замість семи, а не лише вища швидкість",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, bold=True))
    return render(os.path.join(OUT, "connector-zoo.svg"), W, H, *p,
                  title="До USB: сім несумісних інтерфейсів — і один роз'єм")


# ── speed-timeline: як USB набирав швидкість, 1.0 → 1.1 → 2.0 ──────────────────
# Ідея (вставка hist): технічна якість першого релізу не дала перемоги одразу —
# її здобули екосистема (Apple, Windows 98) і стрибок швидкості. Шкала по log:
# від 12 Мбіт/с (1996) до 480 Мбіт/с (2000) — у 40 разів.
def fig_speed_timeline():
    W, H = 760, 360
    p = []
    axis_y = 250
    x0, x1 = 70, 700
    p.append(line(x0, axis_y, x1, axis_y, color=LINE, sw=2.0))
    marks = [
        (1996, "USB 1.0", "LS 1.5 · FS 12 Мбіт/с", NEG, 150),
        (1998, "USB 1.1", "ті самі швидкості,\nале стабільна спец", FIELD, 110),
        (2000, "USB 2.0", "HS 480 Мбіт/с\n(× 40 до FS)", POS, 60),
    ]
    def yx(year):
        return x0 + (x1 - x0) * (year - 1995) / (2001 - 1995)
    for year, ver, note, col, bar in marks:
        x = yx(year)
        p.append(line(x, axis_y, x, axis_y + 8, color=LINE, sw=1.5))
        p.append(text(x, axis_y + 26, str(year), size=12, color=INK, bold=True))
        # стовпчик швидкості
        p.append(rect(x - 26, axis_y - bar, 52, bar, fill="#eaf0fd" if col == NEG else
                      ("#eafaf1" if col == FIELD else "#fdecea"), stroke=col, sw=2.0, rx=4))
        p.append(text(x, axis_y - bar - 10, ver, size=13, color=col, bold=True))
        p.append(mtext(x, axis_y - bar + 22, note.split("\n"), size=10, color=INK, lh=1.2))
    p.append(fitbox(40, 300, 680, 40,
                    "Перемогу дали екосистема (iMac G3, Windows 98) і стрибок швидкості — не лише перший реліз",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    return render(os.path.join(OUT, "speed-timeline.svg"), W, H, *p,
                  title="Як USB набирав швидкість: 1.0 → 1.1 → 2.0")


if __name__ == "__main__":
    fig_host_device_roles()
    fig_usb_tree()
    fig_address_count()
    fig_connector_zoo()
    fig_speed_timeline()
    print("ok: host-device-roles, usb-tree, address-count, connector-zoo, speed-timeline")
