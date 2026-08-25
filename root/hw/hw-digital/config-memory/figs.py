# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_cell_vs_data():
    """Комірка конфігурації vs комірка даних: перша НЕ адресується під час роботи —
    її вихід постійно тримає перемикач/біт LUT."""
    W, H = 740, 400
    frags = []
    frags.append(text(W / 2, 26, "Комірка даних читається адресою; комірка конфігурації просто ТРИМАЄ вихід",
                      size=16, bold=True))

    # ЛІВОРУЧ: звичайна комірка даних у пам'яті
    lx = 40
    frags.append(fitbox(lx, 58, 300, 26, "Комірка даних (звичайна RAM)", size=13, bold=True,
                        fill="#eef2ff", stroke=NEG))
    frags.append(rect(lx + 90, 104, 120, 60, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(lx + 150, 130, "1 біт", size=13, bold=True))
    frags.append(text(lx + 150, 150, "даних", size=11, color=MUTED))
    # адреса заходить, дані виходять
    frags.append(arrow(lx + 20, 134, lx + 88, 134, color=INK, sw=2))
    frags.append(text(lx + 8, 122, "адреса", size=11, color=INK, anchor="start"))
    frags.append(text(lx + 8, 150, "обирає її", size=10, color=MUTED, anchor="start"))
    frags.append(arrow(lx + 212, 134, lx + 280, 134, color=INK, sw=2))
    frags.append(text(lx + 250, 122, "дані", size=11, color=INK))
    frags.append(fitbox(lx + 20, 200, 280, 70,
                        "Її раз-по-раз ЧИТАЮТЬ і ПЕРЕПИСУЮТЬ:\n"
                        "адреса вибирає одну з мільйонів,\n"
                        "вміст живе своїм життям під час роботи.",
                        size=11, fill=FILL, stroke=LINE))

    # ПРАВОРУЧ: комірка конфігурації
    rx = 400
    frags.append(fitbox(rx, 58, 300, 26, "Комірка конфігурації (тканина FPGA)", size=13, bold=True,
                        fill="#e9f7ef", stroke=FIELD))
    frags.append(rect(rx + 20, 104, 110, 60, fill="#dff3e6", stroke=FIELD, sw=2))
    frags.append(text(rx + 75, 128, "засув", size=13, bold=True))
    frags.append(text(rx + 75, 148, "тримає 1 біт", size=10, color=MUTED))
    # вихід іде НАПРЯМУ в перемикач / біт LUT — без адреси
    frags.append(arrow(rx + 132, 134, rx + 200, 134, color=FIELD, sw=2.4))
    frags.append(rect(rx + 202, 108, 96, 52, fill="#ffffff", stroke=INK, sw=1.5))
    frags.append(text(rx + 250, 130, "перемикач", size=11))
    frags.append(text(rx + 250, 148, "/ біт LUT", size=11, color=MUTED))
    frags.append(fitbox(rx + 20, 200, 280, 70,
                        "Її НЕ адресують під час роботи:\n"
                        "залили раз при старті — і вихід\n"
                        "СТАЛО тримає дріт чи біт таблиці.",
                        size=11, fill=FILL, stroke=LINE))

    frags.append(fitbox(120, 300, 500, 66,
                        "Та сама SRAM-схема — різна роль. Комірка даних — це «зошит», куди пишуть і звідки читають.\n"
                        "Комірка конфігурації — це «перемикач, застиглий у положенні»: вона й Є частиною схеми,\n"
                        "її вихід нікуди не читають шиною — він мовчки задає, як з'єднані дроти.",
                        size=12, fill="#fff8e1", stroke=POS))
    render(os.path.join(IMG, 'cell-vs-data.svg'), W, H, *frags)


def fig_cell_tech():
    """Три технології комірки конфігурації на рівні того, ЩО тримає біт:
    SRAM-засув (6T, летка), флеш-плавучий-затвор (1-2T, нелетка), антизапобіжник (зв'язка, OTP)."""
    W, H = 760, 430
    frags = []
    frags.append(text(W / 2, 26, "Чим фізично тримається один біт конфігурації — три технології",
                      size=16, bold=True))

    cols = [
        (26, "#e9f7ef", FIELD, "SRAM-засув",
         "5–6 транзисторів",
         ["Два інвертори, замкнені",
          "в кільце, тримають біт",
          "«самі себе» — доки є струм.",
          "",
          "ЛЕТКА: вимкнув живлення —",
          "біт зник, треба заливати",
          "наново при кожному старті.",
          "",
          "Перезаписів — безліч,",
          "чутлива до радіації."]),
        (270, "#eef2ff", NEG, "Плавучий затвор (флеш)",
         "1–2 транзистори",
         ["Заряд замкнено в ізольо-",
          "ваному затворі — він і задає",
          "стан транзистора.",
          "",
          "НЕЛЕТКА: заряд лишається",
          "без живлення; чип живий",
          "одразу при ввімкненні.",
          "",
          "Перезаписів — тисячі;",
          "доза радіації зсуває поріг."]),
        (514, "#fdecea", POS, "Антизапобіжник",
         "фізична зв'язка",
         ["У потрібних місцях імпульсом",
          "НАЗАВЖДИ пропалено провідну",
          "зв'язку там, де її не було.",
          "",
          "НЕЛЕТКА й незмінна: схема",
          "не «залита», а вплавлена.",
          "",
          "Переписати НЕ можна (OTP);",
          "майже незнищенна радіацією."]),
    ]
    for x, fill, stroke, title, sub, lines in cols:
        frags.append(fitbox(x, 56, 220, 30, title, size=13, bold=True, fill=fill, stroke=stroke))
        frags.append(text(x + 110, 104, sub, size=12, bold=True, color=stroke))
        y = 128
        for ln in lines:
            if ln:
                frags.append(text(x + 8, y, ln, size=10.5, color=INK, anchor="start"))
            y += 19

    frags.append(fitbox(70, 356, 620, 56,
                        "Одна роль — тримати біт схеми — три способи. SRAM панує (гнучка, дешева в перешиванні),\n"
                        "але летка. Флеш і антизапобіжник нелеткі: живі при старті — коштом місткості (флеш)\n"
                        "чи одноразовості (антизапобіжник). Вибір диктують гнучкість, старт і стійкість до радіації.",
                        size=12, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'cell-tech.svg'), W, H, *frags)


def fig_seu_scrub():
    """Частка перекидає біт комірки конфігурації → тканина тихо мис-з'єднується →
    скрабінг (зчитав-порівняв-переписав) відновлює."""
    W, H = 740, 360
    frags = []
    frags.append(text(W / 2, 26, "Перекинутий біт конфігурації тихо ламає схему — скрабінг його ловить",
                      size=16, bold=True))

    # 1: нормальна тканина
    x1 = 40
    frags.append(fitbox(x1, 56, 190, 24, "1 · схема правильна", size=12, bold=True,
                        fill="#e9f7ef", stroke=FIELD))
    for r in range(3):
        for c in range(3):
            frags.append(rect(x1 + 20 + c * 42, 96 + r * 42, 32, 32,
                              fill="#dff3e6", stroke=FIELD, sw=1.2))
            frags.append(text(x1 + 36 + c * 42, 117 + r * 42,
                              ("1" if (r + c) % 2 else "0"), size=11, color=FIELD))

    # частка
    frags.append(text(x1 + 250, 150, "☄", size=26, color=POS))
    frags.append(arrow(x1 + 262, 162, x1 + 300, 190, color=POS, sw=2.4))
    frags.append(text(x1 + 250, 128, "частка", size=11, color=POS))

    # 2: один біт перекинуто
    x2 = 300
    frags.append(fitbox(x2, 56, 190, 24, "2 · один біт перекинуто", size=12, bold=True,
                        fill="#fdecea", stroke=POS))
    for r in range(3):
        for c in range(3):
            bad = (r == 1 and c == 1)
            frags.append(rect(x2 + 20 + c * 42, 96 + r * 42, 32, 32,
                              fill=("#f9c9c2" if bad else "#dff3e6"),
                              stroke=(POS if bad else FIELD), sw=(2.2 if bad else 1.2)))
            val = "X" if bad else ("1" if (r + c) % 2 else "0")
            frags.append(text(x2 + 36 + c * 42, 117 + r * 42, val, size=11, bold=bad,
                              color=(POS if bad else FIELD)))
    frags.append(text(x2 + 96, 232, "дріт з'єднано не туди —", size=10.5, color=POS))
    frags.append(text(x2 + 96, 248, "схема тихо рахує хибно", size=10.5, color=MUTED))

    # 3: скрабінг відновив
    x3 = 560
    frags.append(fitbox(x3, 56, 150, 24, "3 · скрабінг виправив", size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))
    for r in range(3):
        for c in range(3):
            frags.append(rect(x3 + 10 + c * 42, 96 + r * 42, 32, 32,
                              fill="#dff3e6", stroke=FIELD, sw=1.2))
            frags.append(text(x3 + 26 + c * 42, 117 + r * 42,
                              ("1" if (r + c) % 2 else "0"), size=11, color=FIELD))
    frags.append(arrow(x2 + 200, 150, x3 + 4, 150, color=NEG, sw=2))
    frags.append(text((x2 + 200 + x3) / 2, 138, "зчитав →", size=10, color=NEG))
    frags.append(text((x2 + 200 + x3) / 2, 168, "переписав", size=10, color=NEG))

    frags.append(fitbox(90, 288, 560, 56,
                        "Комірка конфігурації — це визначення самої схеми, тож перекинутий біт не псує дані,\n"
                        "а ПЕРЕПАЮЄ тканину: дріт іде не туди, LUT рахує інше. Скрабінг фоново зчитує\n"
                        "конфігурацію, звіряє з еталоном і мовчки переписує — доки помилка не накопичилась.",
                        size=12, fill="#fff8e1", stroke=POS))
    render(os.path.join(IMG, 'seu-scrub.svg'), W, H, *frags)


# ── Фігури до вставки «⚙️ Скрабер конфігураційної пам'яті» ────────────────────

def fig_scrub_loop():
    """Кільце скрабера: кадр за кадром читаємо назад, звіряємо, за потреби переписуємо."""
    W, H = 760, 480
    p = [text(W / 2, 28, "Скраб кадрами: прочитати назад → звірити → переписати лише хибний",
              size=16, bold=True)]

    # чотири вузли по вертикалі в центрі; бічні стрілки-повернення обабіч
    cx = W / 2
    bw = 340                       # ширина вузла
    xL = cx - bw / 2               # лівий край вузлів = 210
    xR = cx + bw / 2               # правий край вузлів = 550

    # 1) взяти наступний кадр
    n1 = rect(xL, 60, bw, 52, fill="#eef2ff", stroke=NEG, sw=2)
    n1 += mtext(cx, 80, ["взяти наступний кадр конфігурації  f", "(рухаємось адресами кадрів)"],
                size=12.5, color=INK)
    p.append(n1)
    # 2) readback
    n2 = rect(xL, 150, bw, 60, fill=FILL, stroke=INK, sw=2)
    n2 += mtext(cx, 170, ["READBACK кадру f: прочитати назад біти", "+ синдром ECC / внесок у CRC"],
                size=12, color=INK)
    p.append(n2)
    # 3) рішення
    n3 = rect(xL, 248, bw, 60, fill="#fff8e1", stroke=POS, sw=2)
    n3 += mtext(cx, 268, ["синдром = 0 ?", "(кадр збігається з еталоном)"],
                size=12.5, color=INK, bold=True)
    p.append(n3)
    # 4) writeback
    n4 = rect(xL, 346, bw, 62, fill="#fdecea", stroke=POS, sw=2)
    n4 += mtext(cx, 367, ["WRITEBACK: переписати ЛИШЕ кадр f", "виправленими бітами"],
                size=12, color=POS)
    p.append(n4)

    # прямі стрілки вниз по центру
    p.append(arrow(cx, 112, cx, 150, color=INK, sw=1.9))                       # 1→2
    p.append(arrow(cx, 210, cx, 248, color=INK, sw=1.9))                       # 2→3
    # 3 → «ні» → writeback
    p.append(arrow(cx, 308, cx, 346, color=POS, sw=1.9))
    p.append(text(cx + 8, 330, "ні → біт побито", size=12, color=POS, bold=True, anchor="start"))

    # 3 → «так» → праворуч і вгору назад до 1 (кадр цілий, нічого не пишемо)
    rxr = xR + 90                  # = 640
    p.append(line(xR, 278, rxr, 278, color=FIELD, sw=1.9))
    p.append(line(rxr, 278, rxr, 86, color=FIELD, sw=1.9))
    p.append(arrow(rxr, 86, xR, 86, color=FIELD, sw=1.9))
    p.append(text(xR + 6, 268, "так → кадр цілий", size=12, color="#1e7a45", bold=True, anchor="start"))

    # writeback → ліворуч і вгору назад до 1
    lxl = xL - 90                  # = 120
    p.append(line(xL, 377, lxl, 377, color=POS, sw=1.9))
    p.append(line(lxl, 377, lxl, 86, color=POS, sw=1.9))
    p.append(arrow(lxl, 86, xL, 86, color=POS, sw=1.9))
    p.append(text(lxl - 6, 235, "повернути", size=11, color=POS, anchor="end"))
    p.append(text(lxl - 6, 251, "кадр на місце", size=11, color=POS, anchor="end"))

    p.append(fitbox(cx - 250, 430, 500, 30,
                    "прогнав усі кадри — і знову з першого: сторож ніколи не спить",
                    size=11.5, fill="#ffffff", stroke=MUTED, color=MUTED))
    render(os.path.join(IMG, "scrub-loop.svg"), W, H, *p)


def fig_blind_vs_rb():
    """Сліпий скраб проти readback-скрабу: що робить кожен і чим платить."""
    W, H = 760, 430
    p = [text(W / 2, 28, "Дві стратегії скрабу: сліпо переписати все — чи звірити й виправити",
              size=16, bold=True)]

    lx, lw = 40, 330
    p.append(rect(lx, 56, lw, 350, fill="#fdf3f0", stroke=POS, sw=2))
    p.append(text(lx + lw / 2, 82, "СЛІПИЙ СКРАБ (blind)", size=14, bold=True, color=POS))
    p.append(fitbox(lx + 18, 96, lw - 36, 42,
                    ["періодично перезаписати ВЕСЬ кадр",
                     "(чи весь чип) з еталона — не читаючи"],
                    size=11.5, fill="#ffffff", stroke=POS))
    p.append(text(lx + 18, 172, "+  простий: лише пише, звіряння нема",
                  size=12, color="#1e7a45", anchor="start"))
    p.append(text(lx + 18, 195, "+  MBU не страшний: пише все підряд",
                  size=12, color="#1e7a45", anchor="start"))
    p.append(text(lx + 18, 226, "−  пише й по цілому — марна робота",
                  size=12, color=POS, anchor="start"))
    p.append(text(lx + 18, 249, "−  у живий кадр → ризик контенції",
                  size=12, color=POS, anchor="start"))
    p.append(text(lx + 18, 272, "−  не знає, що і коли збоїло",
                  size=12, color=POS, anchor="start"))
    p.append(fitbox(lx + 18, 322, lw - 36, 68,
                    ["де: логіку можна на мить спинити,",
                     "потрібна гранична простота"],
                    size=11.5, fill="#fdecea", stroke=POS, color=POS))

    rx = 390
    p.append(rect(rx, 56, lw, 350, fill="#e9f7ef", stroke=FIELD, sw=2))
    p.append(text(rx + lw / 2, 82, "READBACK-СКРАБ", size=14, bold=True, color="#1e7a45"))
    p.append(fitbox(rx + 18, 96, lw - 36, 42,
                    ["прочитати кадр назад, звірити (ECC/CRC),",
                     "виправити лише хибне — у ціле не пише"],
                    size=11.5, fill="#ffffff", stroke=FIELD))
    p.append(text(rx + 18, 172, "+  цілого не чіпає → без контенції",
                  size=12, color="#1e7a45", anchor="start"))
    p.append(text(rx + 18, 195, "+  дає звіт: де й коли був збій",
                  size=12, color="#1e7a45", anchor="start"))
    p.append(text(rx + 18, 226, "−  складніший: звіряти й рахувати ECC",
                  size=12, color=POS, anchor="start"))
    p.append(text(rx + 18, 249, "−  ECC кадру ловить 1–2 біти; більше —",
                  size=12, color=POS, anchor="start"))
    p.append(text(rx + 34, 269, "перекладає на CRC + перезаливку", size=12, color=POS, anchor="start"))
    p.append(fitbox(rx + 18, 322, lw - 36, 68,
                    ["де: логіку спиняти не можна,",
                     "потрібен облік збоїв (космос)"],
                    size=11.5, fill="#e9f7ef", stroke=FIELD, color="#1e7a45"))
    render(os.path.join(IMG, "blind-vs-rb.svg"), W, H, *p)


def fig_window():
    """Вісь часу: вікно вразливості між проходами; повільний скраб пускає MBU."""
    W, H = 760, 400
    p = [text(W / 2, 28, "Вікно вразливості: чим рідший прохід, тим більше встигає накопичитися",
              size=15.5, bold=True)]
    ox, ax = 80, 690

    # ── ЧАСТИЙ скраб ──
    y1 = 120
    p.append(line(ox, y1, ax, y1, color=INK, sw=2))
    p.append(text(ox, y1 - 28, "ЧАСТИЙ скраб", size=12.5, bold=True, color="#1e7a45", anchor="start"))
    passes = [ox + (ax - ox) * k / 8 for k in range(9)]
    for xx in passes:
        p.append(line(xx, y1 - 10, xx, y1 + 10, color=FIELD, sw=2))
    p.append(text(passes[0] + 4, y1 + 26, "↑ проходи скрабера (часто)", size=11,
                  color="#1e7a45", anchor="start"))
    ux = ox + (ax - ox) * 3.4 / 8
    p.append(circle(ux, y1, 6, fill="#fdecea", stroke=POS, sw=2.2))
    p.append(text(ux, y1 - 20, "upset", size=11, color=POS))
    nx = passes[4]
    p.append(arrow(ux + 6, y1 - 4, nx - 4, y1 - 4, color=FIELD, sw=1.6))

    # ── РІДКИЙ скраб ──
    y2 = 240
    p.append(line(ox, y2, ax, y2, color=INK, sw=2))
    p.append(text(ox, y2 - 28, "РІДКИЙ скраб", size=12.5, bold=True, color=POS, anchor="start"))
    for k in range(3):
        xx = ox + (ax - ox) * k / 2
        p.append(line(xx, y2 - 10, xx, y2 + 10, color=FIELD, sw=2))
    p.append(text(ox + (ax - ox) * 0.02, y2 + 26, "↑ проходи скрабера (рідко)", size=11,
                  color="#1e7a45", anchor="start"))
    u1 = ox + (ax - ox) * 0.60
    u2 = ox + (ax - ox) * 0.78
    p.append(circle(u1, y2, 6, fill="#fdecea", stroke=POS, sw=2.2))
    p.append(circle(u2, y2, 6, fill="#fdecea", stroke=POS, sw=2.2))
    p.append(text(u1 - 6, y2 - 20, "upset 1", size=11, color=POS, anchor="end"))
    p.append(text(u2 + 6, y2 - 20, "upset 2 (той самий кадр)", size=11, color=POS, anchor="start"))
    b0 = ox + (ax - ox) * 0.5
    b1 = ax
    p.append(line(b0, y2 + 44, b1, y2 + 44, color=POS, sw=1.6, dash="5,4"))
    p.append(line(b0, y2 + 38, b0, y2 + 50, color=POS, sw=1.6))
    p.append(line(b1, y2 + 38, b1, y2 + 50, color=POS, sw=1.6))
    p.append(text((b0 + b1) / 2, y2 + 62, "вікно вразливості", size=11.5, color=POS, bold=True))

    p.append(fitbox(ox, 320, ax - ox, 56,
                    "два біти в одному кадрі за один прохід — це вже MBU: ECC кадру (1–2 біти)\n"
                    "може не витягти. Правило: скрабуй ≈ на порядок частіше за темп збоїв.",
                    size=11.5, fill="#fff8e1", stroke="#b8860b", color=INK))
    render(os.path.join(IMG, "window.svg"), W, H, *p)


if __name__ == '__main__':
    fig_cell_vs_data()
    fig_cell_tech()
    fig_seu_scrub()
    fig_scrub_loop()
    fig_blind_vs_rb()
    fig_window()
    print("figs written to", IMG)
