# -*- coding: utf-8 -*-
"""
Генератор SVG для 📜-вставки до §3.6.7 — «Хробак Морріса (1988):
переповнення буфера, що зупинило інтернет».
Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; «безпечно» зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 3.6.7i.k.
Допоміжні функції скопійовані з figs.py розділу (щоб скрипти не ділили файлів).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'Courier New', monospace"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def _mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.6.7i.1 — анатомія переповнення в fingerd ────────────────────────
# 512-байтовий буфер на стеку, gets() пише 536 байтів, затирає адресу повернення,
# яку наведено назад у буфер, де лежить «маленька програма» хробака.
def fig_fingerd():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 32, "Як хробак пробивав fingerd: класичне «smashing the stack»", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "буфер на 512 байтів читали через gets() — а gets() не знає меж і пише стільки, скільки прийшло",
              12, GREY, "middle", style="italic")

    # ── ліворуч: «як має бути» ──
    lx = 60
    top = 92
    cw = 250
    s += text(lx + cw / 2, top - 8, "Звичайний запит (вкладається)", 13.5, GREEN, "middle", "bold")
    # стек: низькі адреси вгорі; буфер, далі збережені регістри, далі адреса повернення
    s += rect(lx, top, cw, 150, "#f1f7f2", GREEN, 1.6, 6)
    s += rect(lx + 16, top + 16, cw - 32, 70, "#e7f2ea", GREEN, 1.4, 4)
    s += text(lx + cw / 2, top + 44, "буфер[512]", 13, INK, "middle", "bold")
    s += _mono(lx + cw / 2, top + 64, "\"andrij\\0\" …", 11.5, GREEN, "middle")
    s += rect(lx + 16, top + 92, cw - 32, 22, "#eef3fb", BLUE, 1.2, 3)
    s += _mono(lx + cw / 2, top + 107, "збережені регістри", 11, BLUE, "middle")
    s += rect(lx + 16, top + 116, cw - 32, 22, "#fff8e6", AMBER, 1.4, 3)
    s += _mono(lx + cw / 2, top + 131, "адреса повернення →", 11, INK, "middle")
    s += text(lx + cw / 2, top + 168, "функція чесно повертається назад", 11, GREEN, "middle", style="italic")

    # ── праворуч: «атака» ──
    rx0 = W - 60 - cw
    s += text(rx0 + cw / 2, top - 8, "Запит хробака: 536 байтів у 512", 13.5, RED, "middle", "bold")
    s += rect(rx0, top, cw, 150, "#fdf4f4", RED, 1.6, 6)
    # буфер, заповнений кодом хробака
    s += rect(rx0 + 16, top + 16, cw - 32, 70, "#f7e2e2", RED, 1.4, 4)
    s += text(rx0 + cw / 2, top + 40, "буфер[512]", 13, INK, "middle", "bold")
    s += _mono(rx0 + cw / 2, top + 60, "код хробака (shell)", 11, RED, "middle")
    s += _mono(rx0 + cw / 2, top + 77, "0x90 0x90 … exec()", 10.5, RED, "middle")
    # затерті регістри
    s += rect(rx0 + 16, top + 92, cw - 32, 22, "#f7e2e2", RED, 1.2, 3)
    s += _mono(rx0 + cw / 2, top + 107, "затерто «зайвими» 24 Б", 10.5, RED, "middle")
    # підмінена адреса повернення
    s += rect(rx0 + 16, top + 116, cw - 32, 22, "#ffd9d9", RED, 1.8, 3)
    s += _mono(rx0 + cw / 2, top + 131, "адреса повернення = &буфер", 10.3, RED, "middle", "bold")
    # стрілка «повернення в буфер»
    s += arrow(rx0 + cw - 6, top + 127, rx0 + cw + 26, top + 127, RED, 2)
    s += arrow(rx0 + cw + 20, top + 127, rx0 + cw + 20, top + 50, RED, 2)
    s += arrow(rx0 + cw + 20, top + 50, rx0 + cw - 6, top + 50, RED, 2)
    s += text(rx0 + cw / 2, top + 168, "«повертається» у власний код хробака", 11, RED, "middle", "bold", style="italic")

    # ── посередині-внизу: стрічка байтів і де 512 → 536 ──
    by = 312
    s += text(W / 2, by - 12, "Чому 536 у 512: «зайві» 24 байти перелазять за буфер і лягають точно на адресу повернення",
              12.5, INK, "middle", "bold")
    bx = 150
    bw = 620
    s += rect(bx, by, 512 / 536 * bw, 30, "#e7f2ea", GREEN, 1.4)
    s += rect(bx + 512 / 536 * bw, by, 24 / 536 * bw, 30, "#ffd9d9", RED, 1.6)
    s += text(bx + 512 / 536 * bw / 2, by + 20, "512 байтів буфера", 12, INK, "middle", "bold")
    s += text(bx + 512 / 536 * bw + 24 / 536 * bw / 2, by + 49, "+24", 11, RED, "middle", "bold")
    s += line(bx, by + 36, bx, by + 44, GREY, 1)
    s += line(bx + bw, by + 36, bx + bw, by + 44, GREY, 1)
    s += _mono(bx, by + 58, "0", 10.5, GREY, "start")
    s += _mono(bx + bw, by + 58, "536", 10.5, RED, "end")

    # ── підсумок ──
    s += rect(60, by + 96, W - 120, 88, "#fafafa", INK, 1.4, 9)
    s += text(W / 2, by + 120, "Корінь — рівно той, що в §3.6.7: запис за межі масиву + відсутність перевірки довжини.",
              13, INK, "middle", "bold")
    s += text(W / 2, by + 144, "gets() приймає лише адресу буфера, але не його розмір — і фізично не може спинитись на 512-му байті.",
              11.5, INK, "middle")
    s += text(W / 2, by + 165, "Саме тому gets() згодом викинули зі стандарту C, а перевірка меж стала залізним правилом.",
              11.5, GREEN, "middle", "bold")
    save("fig-19-7i-1-fingerd-overflow.svg", s)


# ── Рис. 3.6.7i.2 — хробак ішов не одним лазом, а трьома ────────────────────
def fig_vectors():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Хробак не мав «одного трюка»: він пробував три двері одночасно", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "тому атрибуція «це баг gets()» — неповна; переповнення було лише одним із трьох незалежних шляхів",
              12, GREY, "middle", style="italic")

    cards = [
        ("1. fingerd — переповнення буфера",
         RED, "#fdf4f4",
         ["сервіс finger показував, хто залогінений;",
          "у ньому 512-байтовий буфер читали через",
          "gets() без меж. Хробак слав 536 байтів —",
          "і перехоплював керування (Рис. 3.6.7i.1).",
          "",
          "Це — герой нашої теми §3.6.7."]),
        ("2. sendmail — режим DEBUG",
         AMBER, "#fffaf0",
         ["поштовий сервер sendmail часто лишали",
          "з увімкненим debug-режимом, що дозволяв",
          "слати команди прямо в систему.",
          "Не переповнення — а відчинені «службові",
          "двері», які забули замкнути в продакшені.",
          ""]),
        ("3. rsh / rexec — слабкі паролі",
         BLUE, "#eef3fb",
         ["довірчі зв'язки між машинами (rsh) +",
          "перебір паролів за словником на ~900 слів",
          "і за іменами користувачів.",
          "Жодної «діри» в коді — лише людська звичка",
          "ставити слабкі паролі й довіряти сусідам.",
          ""]),
    ]
    cw = 280
    gap = 10
    x0 = (W - (cw * 3 + gap * 2)) / 2
    top = 86
    ch = 250
    for i, (title, col, fill, lines) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, top, cw, ch, fill, col, 1.8, 10)
        s += rect(x, top, cw, 38, col, col, 0, 10)
        s += text(x + cw / 2, top + 25, title, 13.5, "#ffffff", "middle", "bold")
        yy = top + 64
        for ln in lines:
            s += text(x + 16, yy, ln, 11.7, INK, "start")
            yy += 19

    # нижня смуга: спільний механізм самопоширення
    by = top + ch + 24
    s += rect(x0, by, cw * 3 + gap * 2, 64, "#f1f7f2", GREEN, 1.7, 9)
    s += text(W / 2, by + 25, "Пробивши будь-які з трьох дверей, хробак копіював себе на нову машину — і повторював усе звідти.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, by + 47, "Самопоширення без участі людини — ось чому це «хробак» (worm), а не «вірус», що чекає запуску.",
              11.5, GREEN, "middle", style="italic")
    save("fig-19-7i-2-vectors.svg", s)


# ── Рис. 3.6.7i.3 — чесний масштаб і чому це сповільнення, а не «вимкнення» ─
def fig_scale():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 32, "Чесний масштаб: «зупинив інтернет» — гіпербола", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "інтернету в сьогоднішньому розумінні ще не було; йшлося про ~60 тисяч хостів дослідницької мережі",
              12, GREY, "middle", style="italic")

    # ── ліворуч: пропорція 6000 / 60000 ──
    lx = 70
    top = 96
    s += text(lx, top, "Скільки заразилось (оцінка за ~добу):", 13.5, INK, "start", "bold")
    grid_x = lx
    grid_y = top + 18
    cols = 20
    cell = 17
    total = 100  # 100 клітинок = 60 000 хостів, кожна = 600
    infected = 10  # ~10%
    for k in range(total):
        r = k // cols
        c = k % cols
        x = grid_x + c * cell
        y = grid_y + r * cell
        fill = "#f3c0bb" if k < infected else "#eef1f4"
        stroke = RED if k < infected else FAINT
        s += rect(x, y, cell - 3, cell - 3, fill, stroke, 1.1, 2)
    s += text(grid_x, grid_y + (total // cols) * cell + 20, "кожна клітинка ≈ 600 хостів · червоні ≈ ~6 000 із ~60 000",
              11, GREY, "start", style="italic")
    s += rect(grid_x, grid_y + (total // cols) * cell + 32, 360, 56, "#fff8e6", AMBER, 1.5, 8)
    s += text(grid_x + 12, grid_y + (total // cols) * cell + 52, "Навіть «10%» — це здогад, а не вимір:", 11.5, INK, "start", "bold")
    s += text(grid_x + 12, grid_y + (total // cols) * cell + 70, "хтось припустив ~60 тис. хостів і ~10% уражених. (перевірити)",
              11, INK, "start")

    # ── праворуч: чому «впало», хоч код не псував даних ──
    rx0 = 500
    s += text(rx0, top, "Чому машини «лягали», хоч хробак", 13.5, INK, "start", "bold")
    s += text(rx0, top + 18, "нічого не стирав і не псував:", 13.5, INK, "start", "bold")
    s += rect(rx0, top + 30, 350, 150, "#fdf4f4", RED, 1.6, 9)
    s += text(rx0 + 16, top + 56, "Помилка в самому хроб'якові:", 12.5, RED, "start", "bold")
    s += text(rx0 + 16, top + 78, "перш ніж заразити машину, він питав —", 11.7, INK, "start")
    s += text(rx0 + 16, top + 97, "«я тут уже є?». Але щоб його не обманули", 11.7, INK, "start")
    s += text(rx0 + 16, top + 116, "фальшивим «так», він однаково ставив", 11.7, INK, "start")
    s += text(rx0 + 16, top + 135, "ще одну копію 1 раз із 7.", 11.7, INK, "start")
    s += text(rx0 + 16, top + 160, "Копії множились на одній машині лавиною.", 11.7, RED, "start", "bold")

    s += rect(rx0, top + 192, 350, 96, "#f1f7f2", GREEN, 1.6, 9)
    s += text(rx0 + 16, top + 216, "Наслідок — не «знищення», а вичерпання:", 12, GREEN, "start", "bold")
    s += text(rx0 + 16, top + 237, "процесор і пам'ять з'їдали десятки копій,", 11.5, INK, "start")
    s += text(rx0 + 16, top + 256, "машина переставала відповідати (DoS).", 11.5, INK, "start")
    s += text(rx0 + 16, top + 276, "Дані цілі — але працювати неможливо.", 11.5, INK, "start", "bold")

    # ── низ: одне речення-висновок ──
    s += rect(60, 452, W - 120, 36, "#fafafa", INK, 1.4, 8)
    s += text(W / 2, 475, "Точніше: хробак не «вимкнув» мережу, а перевантажив тисячі машин до повного гальмування за лічені години.",
              12.5, INK, "middle", "bold")
    save("fig-19-7i-3-scale.svg", s)


# ── Рис. 3.6.7i.4 — що по собі лишив: від патчів до першого вироку й CERT ──
def fig_aftermath():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Спадок: один баг переповнення змінив культуру безпеки", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "2 листопада 1988 — і далі ланцюг наслідків, що дожив до вашого коду на МК",
              12, GREY, "middle", style="italic")

    steps = [
        ("2 лист. 1988", BLUE,
         ["хробака запущено", "(з мережі MIT,", "щоб сховати слід", "Корнелла)"]),
        ("За добу", RED,
         ["~6 000 із ~60 000", "хостів загальмовано;", "адмінів підняли", "по тривозі"]),
        ("Дні по тому", AMBER,
         ["команди в Берклі та", "MIT розібрали код,", "випустили латки,", "відрізали діри"]),
        ("1990–91", INK,
         ["Р. Т. Морріс —", "перший засуджений", "за CFAA (1986):", "умовно + штраф"]),
        ("Наслідок", GREEN,
         ["засновано CERT/CC", "у Carnegie Mellon —", "координація реакції", "на інциденти"]),
    ]
    n = len(steps)
    cw = 158
    gap = 14
    x0 = (W - (cw * n + gap * (n - 1))) / 2
    top = 96
    ch = 168
    for i, (when, col, lines) in enumerate(steps):
        x = x0 + i * (cw + gap)
        s += rect(x, top, cw, ch, "#fafafa", col, 1.8, 10)
        s += rect(x, top, cw, 32, col, col, 0, 10)
        s += text(x + cw / 2, top + 21, when, 13, "#ffffff", "middle", "bold")
        yy = top + 58
        for ln in lines:
            s += text(x + 12, yy, ln, 11.3, INK, "start")
            yy += 20
        if i < n - 1:
            ax = x + cw + 2
            s += arrow(ax, top + ch / 2, ax + gap - 4, top + ch / 2, col, 2.2)

    # ── нижня мораль ──
    by = top + ch + 22
    s += rect(x0, by, cw * n + gap * (n - 1), 70, "#f1f7f2", GREEN, 1.7, 9)
    s += text(W / 2, by + 26, "Урок для §3.6.7: переповнення буфера — не музейний експонат, а діра, що відчиняє машину чужому коду.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, by + 49, "Перевірка меж і відмова від «функцій без розміру» (як gets()) — пряма спадщина цієї ночі 1988-го.",
              11.5, GREEN, "middle", style="italic")
    save("fig-19-7i-4-aftermath.svg", s)


if __name__ == "__main__":
    fig_fingerd()
    fig_vectors()
    fig_scale()
    fig_aftermath()
    print("done.")
