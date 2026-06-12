# -*- coding: utf-8 -*-
"""
Фігури до 🔌-вставки §3.9.7c — «Де ECC у вашому залізі: серверні DIMM, NAND, Flash-кеш МК».
Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; червоний — акцент / «спіймано» / контрольні біти;
синій — нейтральні дані / корисні біти; зелене — результат / «виправлено» / висновок;
бурштин — те, на що дивимось. Шрифт sans-serif. Нумерація підписів — «Рис. 3.9.7c.k».
Імена SVG містять суфікс s7c, щоб не змішуватися з рисунками тем розділу.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (єдина з figs.py розділу) ───────────────────────────────────────
RED   = "#c0271e"   # акцент / «спіймано» / контрольні (ECC) біти
BLUE  = "#1f47b5"   # нейтральні дані / корисні біти
GREEN = "#1f8a3b"   # результат / висновок / «виправлено»
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"   # на що дивимось
PALE_R = "#fbeceb"
PALE_B = "#eef2fb"
PALE_G = "#eef7f0"
PALE_A = "#faf3e0"
MONO  = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="cInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="cRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="cGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="cBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = {GREEN: "cGreen", RED: "cRed", BLUE: "cBlue"}.get(color, "cInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def cell(x, y, w, h, s, fill="none", stroke=FAINT, sw=1.4, rx=4,
         tcol=INK, size=14, weight="bold", mono=True):
    out = rect(x, y, w, h, fill, stroke, sw, rx)
    out += text(x + w / 2, y + h * 0.64, s, size, tcol, "middle", weight, mono=mono)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.7c.1 — Чому ECC-планка ширша рівно на 8 біт: 64 біти даних + 8 біт
# контролю = 72-бітне слово (SECDED). Показуємо 9 чіпів ×8, де 9-й — контрольний,
# і що дають ці 8 біт: виправити 1, помітити 2.
# ════════════════════════════════════════════════════════════════════════════
def fig_72bit_word():
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 32, "Чому ECC-планка ширша рівно на 8 біт: 64 + 8 = 72",
              20, INK, "middle", "bold")
    s += text(W / 2, 53,
              "восьмеро чіпів несуть дані, дев'ятий — контрольні біти; разом контролер читає 72-бітне слово",
              12.5, GREY, "middle", style="italic")

    # ── верх: ряд із дев'яти чіпів ×8 ───────────────────────────────────────
    x0, ytop = 60, 86
    cw, ch, gap = 88, 58, 8
    s += text(x0, ytop - 10, "Модуль зблизька — дев'ять однакових чіпів DRAM по 8 ліній даних кожен:",
              13, INK, "start", "bold")
    for i in range(9):
        cx = x0 + i * (cw + gap)
        data_chip = (i < 8)
        fill = PALE_B if data_chip else PALE_R
        stc = BLUE if data_chip else RED
        s += rect(cx, ytop, cw, ch, fill, stc, 1.8, 7)
        s += text(cx + cw / 2, ytop + 22, "DRAM", 12, INK, "middle", "bold", mono=False)
        s += text(cx + cw / 2, ytop + 40, "×8", 14, stc, "middle", "bold", mono=True)
        label = f"D{i}" if data_chip else "ECC"
        s += text(cx + cw / 2, ytop + ch + 16, label, 12,
                  BLUE if data_chip else RED, "middle", "bold", mono=True)
    # фігурні дужки під групами
    by = ytop + ch + 26
    x_data_l = x0
    x_data_r = x0 + 8 * (cw + gap) - gap
    s += line(x_data_l, by, x_data_r, by, BLUE, 2)
    s += line(x_data_l, by, x_data_l, by - 6, BLUE, 2)
    s += line(x_data_r, by, x_data_r, by - 6, BLUE, 2)
    s += text((x_data_l + x_data_r) / 2, by + 18, "8 чіпів × 8 = 64 біти ДАНИХ",
              12.5, BLUE, "middle", "bold", mono=False)
    x_ecc_l = x0 + 8 * (cw + gap)
    x_ecc_r = x_ecc_l + cw
    s += line(x_ecc_l, by, x_ecc_r, by, RED, 2)
    s += line(x_ecc_l, by, x_ecc_l, by - 6, RED, 2)
    s += line(x_ecc_r, by, x_ecc_r, by - 6, RED, 2)
    s += text((x_ecc_l + x_ecc_r) / 2, by + 18, "+8 КОНТРОЛЮ",
              12, RED, "middle", "bold", mono=False)

    # ── середина: рівняння ширини ───────────────────────────────────────────
    ey = by + 50
    s += rect(60, ey, W - 120, 52, "#ffffff", INK, 1.6, 12)
    s += text(W / 2, ey + 33,
              "64 біти даних  +  8 біт контролю  =  72-бітне слово, яке контролер читає й перевіряє за один такт",
              15, INK, "middle", "bold", mono=False)

    # ── низ: що саме дають ці 8 біт (SECDED) ────────────────────────────────
    ly = ey + 78
    s += text(60, ly - 8, "Що дають ці 8 додаткових біт — код SECDED:", 14, INK, "start", "bold")
    boxes = [
        (BLUE, PALE_B, "Один біт зіпсувався",
         ["синдром указує НА ЯКИЙ —", "контролер мовчки виправляє,", "процесор бачить чисті дані"]),
        (AMBER, PALE_A, "Два біти зіпсувалися",
         ["синдром каже «помилка є,", "одну не виправити» — це", "видима подія, не тиха втрата"]),
        (GREEN, PALE_G, "SECDED розшифровується як",
         ["Single Error Correct,", "Double Error Detect:", "1 — лагодимо, 2 — помічаємо"]),
    ]
    bw = (W - 120 - 2 * 20) / 3
    for j, (col, fill, title, lines) in enumerate(boxes):
        bx = 60 + j * (bw + 20)
        s += rect(bx, ly, bw, 118, fill, col, 1.8, 10)
        s += text(bx + bw / 2, ly + 26, title, 13.5, col, "middle", "bold", mono=False)
        s += line(bx + 14, ly + 36, bx + bw - 14, ly + 36, col, 1.2)
        for k, t in enumerate(lines):
            s += text(bx + 14, ly + 58 + k * 19, t, 12, INK, "start", mono=False)
    save("fig-r09-s7c-1-72bit-word.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.7c.2 — Де живе ECC: три класи заліза поряд. Серверний DIMM (SECDED
# у контролері пам'яті CPU), контролер NAND (BCH/LDPC на льоту), Flash-кеш МК
# (ECC у самому контролері флешу). Спільна ідея: дані + контрольні біти, рахунок
# «на льоту» у залозі, не в коді.
# ════════════════════════════════════════════════════════════════════════════
def fig_three_homes():
    W, H = 980, 600
    s = header(W, H)
    s += text(W / 2, 30, "Три домівки ECC у вашому залізі — і хто рахує контрольні біти",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 51,
              "усюди той самий рецепт: до даних кладуть контрольні біти, а перевіряє їх спеціальний блок «на льоту», не процесор",
              11.5, GREY, "middle", style="italic")

    col_w = (W - 60 - 2 * 24) / 3
    cy = 78
    cards = [
        ("Серверна RAM", BLUE, PALE_B,
         "ECC-DIMM (72 біти)",
         [("Хто рахує:", "контролер пам'яті в CPU"),
          ("Код:", "SECDED (Геммінг + парність)"),
          ("Зерно:", "64 біти даних"),
          ("Контроль:", "+8 біт (9-й чіп)"),
          ("Уміє:", "1 виправити, 2 помітити")],
         "Тиха помилка в комірці DRAM не дійде до програми — її ловить залізо."),
        ("Накопичувач NAND", RED, PALE_R,
         "Контролер SSD / eMMC",
         [("Хто рахує:", "контролер NAND-флешу"),
          ("Код:", "BCH або LDPC"),
          ("Зерно:", "сектор 512 Б … 4 КБ"),
          ("Контроль:", "десятки–сотні біт/сектор"),
          ("Уміє:", "виправити багато біт")],
         "NAND зношується й сипле помилками — без сильного ECC сектор не прочитати."),
        ("Flash у МК", GREEN, PALE_G,
         "Кеш-контролер флешу",
         [("Хто рахує:", "блок ECC контролера флешу"),
          ("Код:", "SEC-DED на слово флешу"),
          ("Зерно:", "слово 64–128 біт"),
          ("Контроль:", "+6…8 біт на слово"),
          ("Уміє:", "1 виправити, 2 помітити")],
         "Той код, що ви писали у флеш МК, читається назад уже перевіреним."),
    ]
    for j, (name, col, fill, sub, rows, foot) in enumerate(cards):
        cx = 30 + j * (col_w + 24)
        ch = 470
        s += rect(cx, cy, col_w, ch, "#ffffff", col, 2, 12)
        s += rect(cx, cy, col_w, 44, fill, col, 2, 12)
        s += text(cx + col_w / 2, cy + 28, name, 15.5, col, "middle", "bold", mono=False)
        s += text(cx + col_w / 2, cy + 66, sub, 12.5, INK, "middle", "bold", mono=True)
        # маленька блок-схема: [ДАНІ | ECC] → [перевірка] → чисто/прапор
        dy = cy + 84
        bx = cx + 18
        bw = col_w - 36
        s += rect(bx, dy, bw * 0.62, 24, PALE_B, BLUE, 1.4, 4)
        s += text(bx + bw * 0.31, dy + 16, "ДАНІ", 11, BLUE, "middle", "bold", mono=False)
        s += rect(bx + bw * 0.62, dy, bw * 0.38, 24, PALE_R, RED, 1.4, 4)
        s += text(bx + bw * 0.81, dy + 16, "ECC", 11, RED, "middle", "bold", mono=False)
        s += arrow(cx + col_w / 2, dy + 26, cx + col_w / 2, dy + 44, col, 2)
        s += rect(bx, dy + 46, bw, 22, fill, col, 1.4, 4)
        s += text(cx + col_w / 2, dy + 61, "перевірка в залозі", 11, INK, "middle", "bold", mono=False)
        # таблиця властивостей
        ty = dy + 84
        for k, (kk, vv) in enumerate(rows):
            yy = ty + k * 34
            s += text(bx, yy, kk, 11.5, GREY, "start", "bold", mono=False)
            s += text(bx, yy + 16, vv, 12, INK, "start", "bold", mono=False)
        # підвал-користь
        fy = cy + ch - 56
        s += line(cx + 14, fy, cx + col_w - 14, fy, FAINT, 1.2)
        words = foot.split(" ")
        # простий перенос рядка на ~28 символів
        ln, lines = "", []
        for w in words:
            if len(ln) + len(w) + 1 > 30:
                lines.append(ln); ln = w
            else:
                ln = (ln + " " + w).strip()
        if ln:
            lines.append(ln)
        for k, t in enumerate(lines[:3]):
            s += text(cx + 14, fy + 18 + k * 16, t, 10.8, col, "start", "bold", mono=False)

    # нижня спільна стрічка
    s += rect(30, 560, W - 60, 28, PALE_A, AMBER, 1.4, 8)
    s += text(W / 2, 579,
              "Спільне в усіх трьох: контрольні біти рахує спеціалізований блок, а не ваш код — ECC тут «безкоштовний» для програми.",
              11.8, INK, "middle", "bold", mono=False)
    save("fig-r09-s7c-2-three-homes.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.7c.3 — «Перший байт» ECC: де його видно інженеру. Лічильники
# correctable/uncorrectable, прапор ECCD у status-регістрі МК, біт у SMART.
# Показуємо ескалацію: тихе виправлення → лічильник росте → uncorrectable = подія.
# ════════════════════════════════════════════════════════════════════════════
def fig_first_byte():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 30, "«Перший байт» ECC: де інженер реально його бачить",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 51,
              "ECC працює мовчки — поки росте лічильник виправлень; коли помилку вже не виправити, з'являється видима подія",
              11.5, GREY, "middle", style="italic")

    # три рівні ескалації — горизонтальна стрічка
    lanes = [
        (GREEN, PALE_G, "1 біт → тихо виправлено",
         "Дані для програми чисті.",
         "Слід лишається тільки", "у лічильнику CE."),
        (AMBER, PALE_A, "Лічильник CE росте",
         "Багато виправлень з однієї",
         "адреси — комірка/чіп слабне.", "Час замислитись, ще не біда."),
        (RED, PALE_R, "Uncorrectable (UE)",
         "Двох+ біт не виправити.",
         "Прапор у статусі, запис у лог,", "machine-check / помилка читання."),
    ]
    x0, y0 = 40, 86
    lw = (W - 80 - 2 * 18) / 3
    lh = 150
    for j, (col, fill, title, l1, l2, l3) in enumerate(lanes):
        cx = x0 + j * (lw + 18)
        s += rect(cx, y0, lw, lh, fill, col, 1.8, 10)
        s += text(cx + lw / 2, y0 + 28, title, 14, col, "middle", "bold", mono=False)
        s += line(cx + 14, y0 + 38, cx + lw - 14, y0 + 38, col, 1.2)
        for k, t in enumerate([l1, l2, l3]):
            s += text(cx + 14, y0 + 62 + k * 22, t, 11.8, INK, "start", mono=False)
        if j < 2:
            ax = cx + lw + 2
            s += arrow(ax, y0 + lh / 2, ax + 14, y0 + lh / 2, INK, 2.4)

    # де саме читати ці лічильники — три прикладні «реєстри»
    ry = y0 + lh + 40
    s += text(40, ry - 8, "Де подивитися на практиці:", 13.5, INK, "start", "bold")
    regs = [
        ("Сервер (RAM)", "EDAC / mcelog у Linux:",
         "ce_count, ue_count на канал — скільки виправлено й скільки фатальних."),
        ("SSD / eMMC", "SMART-атрибути накопичувача:",
         "лічильники ECC-виправлень і нескоригованих секторів через S.M.A.R.T."),
        ("МК (вбудований Flash)", "status-регістр контролера флешу:",
         "біти на кшталт ECC-correctable та ECC-error (двобітна) + адреса збою."),
    ]
    rw = (W - 80 - 2 * 18) / 3
    for j, (name, where, what) in enumerate(regs):
        cx = 40 + j * (rw + 18)
        s += rect(cx, ry, rw, 120, "#ffffff", INK, 1.5, 10)
        s += text(cx + 12, ry + 24, name, 13, INK, "start", "bold", mono=False)
        s += line(cx + 12, ry + 32, cx + rw - 12, ry + 32, FAINT, 1.2)
        s += text(cx + 12, ry + 54, where, 11.8, BLUE, "start", "bold", mono=False)
        # перенос what на ~34 символи
        words = what.split(" ")
        ln, lines = "", []
        for w in words:
            if len(ln) + len(w) + 1 > 36:
                lines.append(ln); ln = w
            else:
                ln = (ln + " " + w).strip()
        if ln:
            lines.append(ln)
        for k, t in enumerate(lines[:4]):
            s += text(cx + 12, ry + 76 + k * 16, t, 11, INK, "start", mono=False)
    save("fig-r09-s7c-3-first-byte.svg", s)


if __name__ == "__main__":
    fig_72bit_word()
    fig_three_homes()
    fig_first_byte()
    print("r09-s7c (ecc-hardware) figures done.")
