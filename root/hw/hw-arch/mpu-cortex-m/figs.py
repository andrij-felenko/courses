# -*- coding: utf-8 -*-
"""Фігури до теми «Блок захисту пам'яті (MPU) в Cortex-M».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

PURPLE = "#6a3fb5"   # MPU / вартовий
AMBER  = "#b9770e"   # атрибути / права


# ── 1. MPU як вартовий на шляху кожного звернення до пам'яті ──────────────────
def fig_gate():
    W, H = 820, 350
    f = [text(W / 2, 26, "MPU стоїть на шляху кожного звернення ядра до пам'яті", size=14, bold=True)]

    # Ядро зліва
    cx, cy, cw, ch = 40, 130, 140, 90
    f.append(rect(cx, cy, cw, ch, fill="#eef2fb", stroke=NEG, sw=2.2, rx=8))
    f.append(text(cx + cw / 2, cy + 34, "ядро", size=13, color=NEG, bold=True))
    f.append(text(cx + cw / 2, cy + 56, "Cortex-M", size=11, color=NEG))
    f.append(text(cx + cw / 2, cy + 76, "хоче адресу X", size=10, color=MUTED))

    # MPU-вартовий у центрі
    mx, my, mw, mh = 300, 108, 170, 134
    f.append(rect(mx, my, mw, mh, fill="#f1ecfa", stroke=PURPLE, sw=2.6, rx=10))
    f.append(text(mx + mw / 2, my + 28, "MPU", size=15, color=PURPLE, bold=True))
    f.append(text(mx + mw / 2, my + 50, "адреса X у якійсь", size=9.5, color=PURPLE))
    f.append(text(mx + mw / 2, my + 65, "дозволеній області?", size=9.5, color=PURPLE))
    f.append(text(mx + mw / 2, my + 88, "чи це право", size=9.5, color=PURPLE))
    f.append(text(mx + mw / 2, my + 103, "для цього режиму?", size=9.5, color=PURPLE))
    f.append(arrow(cx + cw, cy + 45, mx, my + 67, color=NEG, sw=2.2))

    # Дозвіл → шина пам'яті (вгору-праворуч)
    f.append(arrow(mx + mw, my + 34, 640, 120, color=FIELD, sw=2.4))
    f.append(text(560, 108, "дозволено:", size=10, color=FIELD, bold=True))
    f.append(rect(640, 100, 150, 44, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(715, 120, "звернення йде", size=10, color=FIELD, bold=True))
    f.append(text(715, 136, "на шину пам'яті", size=10, color=FIELD))

    # Заборона → MemManage fault (вниз-праворуч)
    f.append(arrow(mx + mw, my + mh - 30, 640, 250, color=POS, sw=2.4))
    f.append(text(560, 236, "порушення:", size=10, color=POS, bold=True))
    f.append(rect(640, 228, 150, 60, fill="#fdeef0", stroke=POS, sw=2, rx=6))
    f.append(text(715, 248, "звернення блок-", size=10, color=POS, bold=True))
    f.append(text(715, 263, "ується, ядро йде", size=10, color=POS))
    f.append(text(715, 278, "в MemManage fault", size=10, color=POS, bold=True))

    f.append(text(W / 2, 332,
                  "Перевірка апаратна й миттєва: MPU не гальмує дозволені звернення, а заборонене зупиняє ще до того, як воно торкнеться пам'яті.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "gate.svg"), W, H, *f)


# ── 2. Область = база + розмір + права + атрибути (дескриптор) ────────────────
def fig_region():
    W, H = 820, 380
    f = [text(W / 2, 26, "Одна область MPU: звідки, доки, і що з нею можна", size=14, bold=True)]

    # Карта пам'яті (вертикальна смуга) зліва
    mx, my, mw, mh = 70, 70, 150, 270
    f.append(rect(mx, my, mw, mh, fill="#f7f8fb", stroke=MUTED, sw=1.6, rx=6))
    f.append(text(mx + mw / 2, my - 10, "карта пам'яті", size=10.5, color=MUTED, bold=True))
    # Область усередині карти
    ry, rh = my + 90, 90
    f.append(rect(mx, ry, mw, rh, fill="#f1ecfa", stroke=PURPLE, sw=2.4))
    f.append(text(mx + mw / 2, ry + 48, "ОБЛАСТЬ", size=12, color=PURPLE, bold=True))
    # мітки база / кінець
    f.append(line(mx - 12, ry, mx, ry, color=PURPLE, sw=1.6))
    f.append(text(mx - 16, ry + 4, "0x2000_0000", size=9.5, color=PURPLE, anchor="end", bold=True))
    f.append(text(mx - 16, ry - 8, "база", size=9, color=MUTED, anchor="end"))
    f.append(line(mx - 12, ry + rh, mx, ry + rh, color=PURPLE, sw=1.6))
    f.append(text(mx - 16, ry + rh + 4, "+ розмір (2ⁿ)", size=9.5, color=PURPLE, anchor="end"))

    # Дескриптор (регістри) праворуч
    dx, dy = 340, 74
    rows = [
        ("база", "де починається (кратна розміру)", NEG),
        ("розмір", "2ⁿ байтів: 32 Б … 4 ГБ", NEG),
        ("права (AP)", "чит/зап окремо привіл. й непривіл.", AMBER),
        ("XN", "чи можна звідси ВИКОНУВАТИ код", AMBER),
        ("атрибути", "кешованість, тип пам'яті", MUTED),
    ]
    rh2 = 50
    f.append(text(dx + 210, dy - 12, "що зберігає одна область", size=11, color=PURPLE, bold=True))
    for i, (k, v, col) in enumerate(rows):
        yy = dy + i * rh2
        f.append(rect(dx, yy, 130, rh2 - 8, fill="#f1ecfa", stroke=col, sw=1.8, rx=5))
        f.append(text(dx + 65, yy + (rh2 - 8) / 2 + 4, k, size=11, color=col, bold=True))
        f.append(rect(dx + 138, yy, 300, rh2 - 8, fill=BG, stroke=MUTED, sw=1.1, rx=5))
        f.append(text(dx + 148, yy + (rh2 - 8) / 2 + 4, v, size=10, color=INK, anchor="start"))

    f.append(text(W / 2, 366,
                  "Область — це не самі байти, а короткий опис: де вона, яка завбільшки і за якими правилами до неї звертатися.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "region.svg"), W, H, *f)


# ── 3. Пріоритет за номером: старша область перекриває молодшу ────────────────
def fig_priority():
    W, H = 780, 340
    f = [text(W / 2, 26, "Області перекриваються — виграє та, що зі старшим номером", size=14, bold=True)]

    base_x, base_y, base_w = 120, 90, 460

    # Область 0 — велика, вся RAM, чит+зап
    f.append(rect(base_x, base_y, base_w, 70, fill="#eef2fb", stroke=NEG, sw=2, rx=6))
    f.append(text(base_x + 12, base_y + 26, "Область 0", size=11.5, color=NEG, bold=True, anchor="start"))
    f.append(text(base_x + 12, base_y + 48, "уся RAM — читати й писати", size=10.5, color=NEG, anchor="start"))

    # Область 3 — маленька, всередині, тільки читати (перекриває)
    ox, oy, ow = base_x + 250, base_y + 20, 200
    f.append(rect(ox, oy, ow, 90, fill="#fdeef0", stroke=POS, sw=2.4, rx=6))
    f.append(text(ox + ow / 2, oy + 30, "Область 3", size=11.5, color=POS, bold=True))
    f.append(text(ox + ow / 2, oy + 52, "лише читати", size=10.5, color=POS, bold=True))
    f.append(text(ox + ow / 2, oy + 72, "(старший номер!)", size=9.5, color=POS))

    # Дужка «тут діє область 3»
    f.append(line(ox, base_y + 130, ox + ow, base_y + 130, color=POS, sw=1.6, dash="4,3"))
    f.append(text(ox + ow / 2, base_y + 150, "тут запис заборонено", size=10, color=POS, bold=True))

    # Дужки «тут діє область 0»
    f.append(line(base_x, base_y + 130, ox, base_y + 130, color=NEG, sw=1.6, dash="4,3"))
    f.append(text((base_x + ox) / 2, base_y + 150, "тут запис дозволено", size=10, color=NEG))

    # Правило
    box, bw, bh = textbox(W / 2, 250, "Правило перекриття\nдіють атрибути області з НАЙБІЛЬШИМ номером",
                          size=11, pad=12, fill="#f1ecfa", stroke=PURPLE, sw=2, color=PURPLE, bold=True)
    f.append(box)

    f.append(text(W / 2, 322,
                  "Так широку область роблять «дефолтом», а точковими старшими областями вирізають у ній винятки — наприклад, роблять шматок RAM тільки для читання.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "priority.svg"), W, H, *f)


# ── 4. Порушення доступу → MemManage fault, слід у MMFAR/MMFSR ────────────────
def fig_fault():
    W, H = 800, 330
    f = [text(W / 2, 26, "Заборонений доступ ловиться апаратно й лишає слід", size=14, bold=True)]

    # Код-порушник
    f.append(rect(40, 90, 200, 66, fill="#fdeef0", stroke=POS, sw=2, rx=6))
    f.append(text(140, 116, "*p = 42;", size=13, color=POS, bold=True))
    f.append(text(140, 138, "p у забороненій області", size=9.5, color=POS))

    # MPU ловить
    f.append(arrow(240, 123, 320, 123, color=POS, sw=2.2))
    mx, my, mw, mh = 320, 92, 140, 62
    f.append(rect(mx, my, mw, mh, fill="#f1ecfa", stroke=PURPLE, sw=2.4, rx=8))
    f.append(text(mx + mw / 2, my + 26, "MPU", size=13, color=PURPLE, bold=True))
    f.append(text(mx + mw / 2, my + 46, "порушення!", size=10, color=PURPLE, bold=True))

    # Стрибок у обробник
    f.append(arrow(mx + mw, my + 30, 560, my + 30, color=POS, sw=2.2))
    f.append(rect(560, 88, 200, 70, fill="#eef2fb", stroke=NEG, sw=2, rx=6))
    f.append(text(660, 112, "MemManage_Handler", size=10.5, color=NEG, bold=True))
    f.append(text(660, 134, "ядро стрибає сюди", size=9.5, color=NEG))
    f.append(text(660, 150, "замість зіпсувати пам'ять", size=9, color=MUTED))

    # Слід: два регістри
    f.append(text(W / 2, 200, "у обробнику вже готові докази:", size=11, color=INK, bold=True))
    f.append(rect(150, 216, 220, 56, fill=BG, stroke=AMBER, sw=1.8, rx=6))
    f.append(text(260, 240, "MMFAR", size=11.5, color=AMBER, bold=True))
    f.append(text(260, 260, "адреса, куди ліз код", size=9.5, color=INK))
    f.append(rect(430, 216, 220, 56, fill=BG, stroke=AMBER, sw=1.8, rx=6))
    f.append(text(540, 240, "MMFSR", size=11.5, color=AMBER, bold=True))
    f.append(text(540, 260, "що саме порушено (чит/зап/вик.)", size=9, color=INK))

    f.append(text(W / 2, 312,
                  "Замість тихо затерти чужі дані, помилковий доступ стає гучним винятком із точною адресою — баг ловиться в місці, де стався.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "fault.svg"), W, H, *f)


# ── 5. Планувальник переставляє області MPU на кожному перемиканні контексту ──
def fig_ctxswitch():
    W, H = 860, 380
    f = [text(W / 2, 26, "На кожному перемиканні контексту планувальник переставляє «задачні» області MPU",
              size=13.5, bold=True)]

    # Спільні (ядрові) області — сталі, зліва
    kx, ky, kw = 40, 70, 250
    f.append(text(kx + kw / 2, ky - 12, "сталі області ядра (не міняються)", size=10.5, color=PURPLE, bold=True))
    krows = [("0  flash — код+конст.", "усім читати/викон.", NEG),
             ("1  ядрові дані/heap", "лише привіл.", NEG),
             ("2  периферія", "лише привіл.", AMBER)]
    for i, (k, v, col) in enumerate(krows):
        yy = ky + i * 46
        f.append(rect(kx, yy, kw, 38, fill="#eef2fb", stroke=col, sw=1.8, rx=5))
        f.append(text(kx + 10, yy + 16, k, size=10, color=col, bold=True, anchor="start"))
        f.append(text(kx + 10, yy + 31, v, size=9, color=MUTED, anchor="start"))

    # Задача A (посередині) vs Задача B (праворуч) — області, що переставляються
    def task_col(x, name, addrs, col):
        f.append(text(x + 125, 62, name, size=11.5, color=col, bold=True))
        rows = [("5  стек задачі", addrs[0], col),
                ("6  дані задачі", addrs[1], col),
                ("7  спільна шина", "SPI давача", MUTED)]
        for i, (k, v, c) in enumerate(rows):
            yy = 74 + i * 46
            f.append(rect(x, yy, 250, 38, fill="#fdeef0" if col == POS else "#eef6ef",
                          stroke=c, sw=2.0, rx=5))
            f.append(text(x + 10, yy + 16, k, size=10, color=c, bold=True, anchor="start"))
            f.append(text(x + 10, yy + 31, v, size=9, color=MUTED, anchor="start"))

    # показуємо ДВІ можливі «правіші» половини таблиці як стан ДО і ПІСЛЯ світчу
    task_col(330, "поки біжить задача A", ("0x2000_1000", "0x2000_1800"), FIELD)
    f.append(text(600, 250, "перемикання", size=11, color=PURPLE, bold=True))
    f.append(arrow(455, 250, 585, 250, color=PURPLE, sw=2.6))
    f.append(text(600, 268, "контексту", size=11, color=PURPLE, bold=True))
    f.append(text(600, 288, "(PendSV)", size=9.5, color=MUTED))
    task_col(605, "тепер біжить задача B", ("0x2000_3000", "0x2000_3800"), POS)

    f.append(text(W / 2, 366,
                  "Області 0–2 (ядро) стоять завжди; області 5–7 планувальник переписує під стек і дані тієї задачі, яку зараз пускає — і пускає її непривілейованою.",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "ctxswitch.svg"), W, H, *f)


# ── 6. «Канарка» між стеками: переповнення впирається в заборонену область ─────
def fig_canary():
    W, H = 760, 400
    f = [text(W / 2, 26, "Заборонена «канарка» між стеками ловить переповнення на першому ж байті",
              size=13, bold=True)]

    # вертикальна карта RAM: стек A росте вниз, канарка, стек B
    cx, cw = 200, 220
    top = 56
    # Стек A
    f.append(rect(cx, top, cw, 90, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(cx + cw / 2, top + 30, "стек задачі A", size=11.5, color=FIELD, bold=True))
    f.append(text(cx + cw / 2, top + 50, "чит/зап (обл. 5)", size=9.5, color=MUTED))
    f.append(text(cx + cw / 2, top + 70, "росте вниз ↓", size=9.5, color=FIELD))
    # Канарка
    ky2 = top + 90
    f.append(rect(cx, ky2, cw, 46, fill="#fdeef0", stroke=POS, sw=2.6, rx=6))
    f.append(text(cx + cw / 2, ky2 + 20, "КАНАРКА — заборонено все", size=10.5, color=POS, bold=True))
    f.append(text(cx + cw / 2, ky2 + 37, "(старша область, AP = нема доступу)", size=9, color=POS))
    # Стек B
    by = ky2 + 46
    f.append(rect(cx, by, cw, 90, fill="#eef2fb", stroke=NEG, sw=2, rx=6))
    f.append(text(cx + cw / 2, by + 34, "стек задачі B", size=11.5, color=NEG, bold=True))
    f.append(text(cx + cw / 2, by + 54, "чит/зап (обл. 5 після світчу)", size=9, color=MUTED))

    # стрілка переповнення A → канарка
    ax = cx - 26
    f.append(arrow(ax, top + 20, ax, ky2 + 8, color=POS, sw=2.4))
    f.append(text(ax - 6, (top + ky2) / 2, "переповнення A", size=9.5, color=POS,
                  anchor="end", bold=True))

    # праворуч: що станеться
    rx = cx + cw + 40
    box, bw, bh = textbox(rx + 120, 150,
                          "перший байт за межу стека\n= доступ у канарку\n→ MemManage fault\nодразу, не через сусіда",
                          size=10.5, pad=12, fill="#f1ecfa", stroke=PURPLE, sw=2,
                          color=PURPLE, bold=True)
    f.append(box)

    f.append(text(W / 2, 320,
                  "Без канарки стек A, переповнюючись, тихо заповз би у стек B і повалив систему пізніше й деінде.",
                  size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 340,
                  "Канарку роблять старшою забороненою областю, тож вона перекриває «чит/зап» широкої RAM — і перший же зайвий байт ловиться.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "canary.svg"), W, H, *f)


# ── 7. Родовід: дві гілки від мейнфреймів — переклад адрес vs. лише перевірка ─
def fig_lineage():
    W, H = 860, 430
    f = [text(W / 2, 26, "Дві гілки «заліза на шляху звернень»: MMU перекладає, MPU лише перевіряє",
              size=13.5, bold=True)]

    # вісь часу
    ax0, ax1, ay = 60, W - 30, 400
    f.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.5))
    for yr, lx in [("1962", 150), ("1964", 300), ("1965", 430), ("1973", 560), ("1999", 690), ("Cortex-M", 800)]:
        f.append(line(lx, ay - 4, lx, ay + 4, color=MUTED, sw=1.3))
        f.append(text(lx, ay + 18, yr, size=10, color=MUTED))

    # спільний корінь
    root, rw, rh = textbox(150, 210, "спільна ідея:\nзалізо звіряє\nкожне звернення\nз описом ділянки",
                           size=10, pad=10, fill=FILL, stroke=INK, sw=1.8, bold=True)
    f.append(root)

    # ── верхня гілка: переклад адрес → MMU ──
    uy = 95
    f.append(text(120, uy - 22, "гілка «ПЕРЕКЛАД адрес»", size=11, color=NEG, bold=True, anchor="start"))
    up = [(300, "B5000\nдескриптори,\nсегменти"),
          (450, "Multics\nсегменти,\nвіртуальна пам'ять"),
          (640, "MMU\nтаблиці сторінок,\nкеш перекладів")]
    prev = (150 + 40, 190)
    for lx, label in up:
        box, bw, bh = textbox(lx, uy, label, size=9.5, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG)
        f.append(box)
        f.append(arrow(prev[0], prev[1], lx - bw / 2 - 2, uy + 6, color=NEG, sw=1.8))
        prev = (lx + bw / 2, uy)
    f.append(mtext(770, uy, ["→ великі", "процесори"], size=9.5, color=NEG, bold=True))

    # ── нижня гілка: лише перевірка права → MPU ──
    ly = 320
    f.append(text(120, ly + 34, "гілка «лише ПЕРЕВІРКА права»", size=11, color=PURPLE, bold=True, anchor="start"))
    lo = [(300, "база-межа\n(CTSS,\nIBM 7090)"),
          (450, "ключі блоків\n(System/360)"),
          (640, "ARM MPU\n8 областей,\nбез перекладу")]
    prev = (150 + 40, 230)
    for lx, label in lo:
        box, bw, bh = textbox(lx, ly, label, size=9.5, pad=8, fill="#f1ecfa", stroke=PURPLE, sw=1.8, color=PURPLE)
        f.append(box)
        f.append(arrow(prev[0], prev[1], lx - bw / 2 - 2, ly - 6, color=PURPLE, sw=1.8))
        prev = (lx + bw / 2, ly)
    # фінал: Cortex-M MPU
    fin, fw, fh = textbox(800, ly, "Cortex-M\nMPU", size=10, pad=9, fill="#f1ecfa", stroke=PURPLE, sw=2.4, color=PURPLE, bold=True)
    f.append(fin)
    f.append(arrow(690 + 52, ly, 800 - fw / 2 - 2, ly, color=PURPLE, sw=2))

    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gate()
    fig_region()
    fig_priority()
    fig_fault()
    fig_ctxswitch()
    fig_canary()
    fig_lineage()
    print("OK: 7 figures ->", IMG)
