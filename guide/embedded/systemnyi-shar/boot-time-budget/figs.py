# -*- coding: utf-8 -*-
"""Фігури до теми «Бюджет часу завантаження».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Часова смуга завантаження: чотири ланки, ширина = частка часу ─────────────
def fig_boot_timeline():
    W, H = 780, 360
    f = [text(W / 2, 30,
              "Часова смуга завантаження: від живлення до вашого коду",
              size=15, bold=True)]

    ox, oy = 40, 150          # ліво-верх смуги
    span = 700                # повна ширина смуги
    bh = 70                   # висота блоків

    # (підпис, частка_ширини, колір_рамки, заливка, дрібний підпис)
    stages = [
        ("ПЗП", 0.10, MUTED, "#eef1f4", "стрепи · тягне щабель 2"),
        ("Завантажувач 2", 0.46, POS, "#fdecea", "копіює сегменти · SHA-256"),
        ("Старт ESP-IDF", 0.30, NEG, "#eaf0fd", "частота · служби · FreeRTOS"),
        ("app_main", 0.14, FIELD, "#eafaf1", "ваш код"),
    ]

    x = ox
    for name, frac, col, fill, sub in stages:
        w = span * frac
        f.append(rect(x, oy, w, bh, fill=fill, stroke=col, sw=2))
        fs = fit_font(name, w - 10, 13, bold=True)
        f.append(text(x + w / 2, oy + 27, name, size=fs, bold=True, color=INK))
        sfs = fit_font(sub, w - 8, 10)
        f.append(text(x + w / 2, oy + 48, sub, size=sfs, color=MUTED))
        x += w

    # позначка найдовшої ланки (завантажувач 2)
    bx = ox + span * 0.10
    bw = span * 0.46
    f.append(line(bx, oy - 10, bx + bw, oy - 10, color=POS, sw=1.6))
    f.append(text(bx + bw / 2, oy - 16, "найдовша ланка", size=11,
                  bold=True, color=POS))

    # вісь часу під смугою
    f.append(line(ox, oy + bh + 16, ox + span, oy + bh + 16, color=MUTED, sw=1.3))
    f.append(text(ox, oy + bh + 34, "живлення / скидання", size=10.5,
                  color=MUTED, anchor="start"))
    f.append(text(ox + span, oy + bh + 34, "час →", size=10.5,
                  color=MUTED, anchor="end"))

    b, _, _ = textbox(W / 2, 322,
                      "t_завант = t_ПЗП + t_образ + t_перевірка + t_старт_IDF.  "
                      "Розкладене на доданки — можна тиснути; монолітне — ні",
                      size=11.5, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "boot-timeline.svg"), W, H, *f)


# ── Два шляхи пробудження: повний boot проти стабу в RTC-памʼяті ──────────────
def fig_wake_stub_path():
    W, H = 780, 430
    f = [text(W / 2, 30,
              "Два шляхи пробудження зі сну: повне завантаження проти стабу",
              size=15, bold=True)]

    def node(cx, cy, label, col, fill, w=128, h=46):
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=col, sw=1.8))
        fs = fit_font(label.split("\n")[0], w - 10, 12, bold=True)
        f.append(mtext(cx, cy - (len(label.split("\n")) - 1) * fs * 0.55 + fs * 0.35,
                       label, size=fs, bold=True, color=INK))

    # старт зліва — «прокидання зі сну»
    sx, sy = 110, 215
    f.append(circle(sx, sy, 40, fill="#fff7e6", stroke="#b8860b", sw=2))
    f.append(mtext(sx, sy - 4, "прокидання\nзі сну", size=11.5, bold=True, color=INK))

    # ── Верхній шлях: повний boot ───────────────────────────────────────────
    topy = 110
    f.append(text(W / 2 + 40, topy - 42, "Звичайний шлях — увесь ланцюг щоразу",
                  size=12.5, bold=True, color=POS))
    chain = [
        (250, "ПЗП", MUTED, "#eef1f4"),
        (400, "Завантажувач\n+ SHA-256", POS, "#fdecea"),
        (560, "Старт\nESP-IDF", NEG, "#eaf0fd"),
        (705, "app_main", FIELD, "#eafaf1"),
    ]
    # стрілки: від кола до першого вузла, далі ланцюжком між вузлами
    f.append(arrow(sx + 36, sy - 16, chain[0][0] - 58, topy + 6, color=LINE))
    for (cx0, _, _, _), (cx1, _, _, _) in zip(chain, chain[1:]):
        f.append(arrow(cx0 + 60, topy, cx1 - 60, topy, color=LINE))
    # самі вузли (поверх стрілок)
    for cx, label, col, fill in chain:
        node(cx, topy, label, col, fill, w=120 if "\n" in label else 110)

    # ── Нижній шлях: стаб ────────────────────────────────────────────────────
    boty = 320
    f.append(text(W / 2 + 40, boty + 52, "Шлях зі стабом — крихітна функція до завантажувача",
                  size=12.5, bold=True, color=FIELD))
    node(290, boty, "Стаб у\nRTC-памʼяті", FIELD, "#eafaf1", w=140)
    f.append(arrow(sx + 40, sy + 18, 290 - 70, boty, color=LINE))

    # розгалуження від стабу: назад у сон (часто) / повний boot (зрідка)
    node(540, boty - 34, "назад у сон", NEG, "#eaf0fd", w=140, h=42)
    node(540, boty + 40, "повний boot", POS, "#fdecea", w=140, h=42)
    f.append(arrow(360, boty - 6, 470, boty - 34, color=NEG))
    f.append(arrow(360, boty + 6, 470, boty + 40, color=POS))
    f.append(text(452, boty - 40, "нічого робити (часто)", size=10,
                  color=NEG, anchor="middle"))
    f.append(text(452, boty + 62, "є робота (зрідка)", size=10,
                  color=POS, anchor="middle"))

    b, _, _ = textbox(W / 2, 408,
                      "Стаб дістає керування ще до завантажувача — і в більшості пробуджень "
                      "вертає чіп у сон, оминувши весь дорогий старт",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wake-stub-path.svg"), W, H, *f)


# ── Ланцюг самопідняття: від першого незмінного шматка до повного коду ────────
def fig_bootstrap_chain():
    W, H = 860, 430
    f = [text(W / 2, 30,
              "Ланцюг самопідняття: кожна ланка тягне більшу за себе",
              size=15, bold=True)]

    # дві колонки: рання машина (ліворуч) ↔ ESP32 (праворуч) — той самий принцип
    colL = 245
    colR = 615
    f.append(text(colL, 60, "Рання машина (1950-ті)", size=12.5, bold=True, color=MUTED))
    f.append(text(colR, 60, "ESP32, сьогодні", size=12.5, bold=True, color=FIELD))

    # вертикальна пунктирна межа між колонками
    f.append(line(W / 2, 78, W / 2, 360, color=LINE, sw=1, dash="4 5"))

    bw, bh = 250, 52
    ys = [100, 178, 256]   # три рівні: foothold → проміжний → повний код

    # (підпис_лівий, підпис_правий, колір, заливка)
    rungs = [
        ("Тумблери / ПЗП\nкрихітний завантажувач", "ПЗП-завантажувач\n(масковий, незмінний)",
         POS, "#fdecea"),
        ("тягне більший\nзавантажувач", "завантажувач 2 у Flash\n(копіює, звіряє образ)",
         "#b8860b", "#fff7e6"),
        ("той — повний\nробочий код", "ваш застосунок\n(app_main)",
         FIELD, "#eafaf1"),
    ]

    def rung(cx, y, label, col, fill):
        f.append(rect(cx - bw / 2, y, bw, bh, fill=fill, stroke=col, sw=1.9))
        f.append(mtext(cx, y + bh / 2 - 6, label, size=11.5, bold=True, color=INK))

    for (lL, lR, col, fill), y in zip(rungs, ys):
        rung(colL, y, lL, col, fill)
        rung(colR, y, lR, col, fill)

    # стрілки «тягне вгору наступну ланку» (знизу вгору в межах колонки)
    for cx in (colL, colR):
        for yb, yt in zip(ys[1:], ys):
            f.append(arrow(cx, yb, cx, yt + bh, color=LINE))
    # підпис механізму збоку (праворуч від лівої колонки, у проміжку до межі)
    lx = colL + bw / 2 + 10
    f.append(text(lx, (ys[0] + ys[1]) / 2 + bh / 2 + 4,
                  "тягне", size=10.5, color=MUTED, anchor="start"))
    f.append(text(lx, (ys[1] + ys[2]) / 2 + bh / 2 + 4,
                  "тягне", size=10.5, color=MUTED, anchor="start"))

    # нижня рамка-висновок: спільна суть (двома рядками — щоб не вилазила)
    b, _, _ = textbox(W / 2, 392,
                      "Перша ланка — незнищенна й крихітна; вона не «піднімає сама себе» (це неможливо),\n"
                      "а спирається на зовнішню опору й тягне наступну, більшу за себе",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bootstrap-chain.svg"), W, H, *f)


# ── (proj) Три точки зору приладу на той самий шлях RESET→app_main ────────────
def fig_profiler_vantage():
    W, H = 1019, 470
    f = [text(W / 2, 28, "Три точки зору на той самий шлях завантаження",
              size=15, bold=True)]
    x0, x1 = 70, 810
    axy = 150
    segs = [("ПЗП", "#eef1f4", 0.10),
            ("завантажувач 2-го щабля\n(копіює образ · SHA-256)", "#fdf6e3", 0.46),
            ("старт ESP-IDF", "#eaf0fd", 0.30),
            ("app_main", "#eafaf1", 0.14)]
    total = sum(s[2] for s in segs)

    # вісь t=0 — фронт RESET
    f.append(line(x0, axy - 36, x0, axy + 150, color=POS, sw=2))
    f.append(text(x0, axy - 44, "фронт RESET / EN", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(x0, axy - 28, "t = 0", size=11, color=POS, anchor="start"))

    cx = x0
    bx = []
    for name, fill, frac in segs:
        w = (x1 - x0) * frac / total
        f.append(rect(cx, axy, w, 46, fill=fill, stroke=MUTED, sw=1.5))
        f.append(fitbox(cx + 3, axy + 5, w - 6, 36, name, size=11.5, fill="none", stroke="none"))
        bx.append((cx, cx + w))
        cx += w
    am = bx[3][0]
    f.append(line(am, axy - 20, am, axy + 150, color=FIELD, sw=2, dash="5 4"))
    f.append(text(am + 5, axy - 24, "старт app_main", size=12, bold=True, color=FIELD, anchor="start"))

    def span(y, xa, xb, label, color, note):
        f.append(line(xa, y, xb, y, color=color, sw=3))
        f.append(line(xa, y - 6, xa, y + 6, color=color, sw=2))
        f.append(line(xb, y - 6, xb, y + 6, color=color, sw=2))
        f.append(text(xa, y - 9, label, size=12, bold=True, color=color, anchor="start"))
        f.append(text(xa, y + 18, note, size=11, color=MUTED, anchor="start"))

    span(axy + 80, x0, am, "щуп аналізатора (GPIO-маркер)", POS,
         "бачить УВЕСЬ шлях: фронт RESET → перший такт коду")
    span(axy + 134, bx[1][0], bx[1][1], "мітки завантажувача (лог)", "#7b3fa0",
         "час лише в межах 2-го щабля, і лише якщо лог увімкнено")
    span(axy + 210, am, x1, "esp_timer_get_time()", NEG,
         "лічить від старту ESP-IDF — усе лівіше для нього сліпе")

    f.append(rect(x0, axy + 176, am - x0, 22, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(fitbox(x0 + 2, axy + 177, am - x0 - 4, 20,
                    "сліпа зона esp_timer — час сюди зсередини прошивки не видно",
                    size=11, fill="none", stroke="none", color=POS))
    render(os.path.join(IMG, "profiler-vantage.svg"), W, H, *f)


# ── (proj) Той самий профіль у двох режимах: холодний boot ↔ стаб ─────────────
def fig_profiler_coldwake():
    W, H = 880, 420
    f = [text(W / 2, 28, "Той самий профіль у двох режимах: що міряє інструмент",
              size=15, bold=True)]
    colx = 60
    rowh = 34
    f.append(fitbox(colx, 54, 300, 30, "ланка завантаження", size=13, fill="#eceff3", bold=True))
    f.append(fitbox(colx + 308, 54, 250, 30, "холодний boot (POWERON)", size=12.5, fill="#fdecea", bold=True))
    f.append(fitbox(colx + 562, 54, 258, 30, "пробудження зі стабом (DEEPSLEEP)", size=11.5, fill="#eafaf1", bold=True))
    rows = [
        ("ПЗП", "вимір зі щупа", "вимір зі щупа", "#eef1f4", False),
        ("завантажувач: копіювання образу", "найбільший доданок", "пропущено", "#fdf6e3", True),
        ("завантажувач: SHA-256", "велике", "пропущено", "#fdf6e3", True),
        ("старт ESP-IDF (esp_timer)", "середнє", "пропущено", "#eaf0fd", True),
        ("стаб у RTC-памʼяті", "—", "крихти", "#eafaf1", False),
    ]
    y = 94
    for name, cold, wake, fill, cut in rows:
        f.append(fitbox(colx, y, 300, rowh - 4, name, size=11.5, fill=fill))
        f.append(fitbox(colx + 308, y, 250, rowh - 4, cold, size=11.5, fill="#ffffff"))
        f.append(fitbox(colx + 562, y, 258, rowh - 4, wake, size=11.5, fill="#ffffff",
                        color=(MUTED if cut else INK)))
        y += rowh
    f.append(fitbox(colx, y + 8, 300, rowh, "Σ  t_завант", size=13, fill="#eceff3", bold=True))
    f.append(fitbox(colx + 308, y + 8, 250, rowh, "повний шлях", size=13, fill="#fdecea", bold=True, color=POS))
    f.append(fitbox(colx + 562, y + 8, 258, rowh, "майже нуль", size=13, fill="#eafaf1", bold=True, color=FIELD))
    b, _, _ = textbox(W / 2, y + 78,
                      "Той самий інструмент друкує дві колонки — і одразу видно, "
                      "що стаб зрізає весь ланцюг, лишаючи холодний boot рідкісним",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "profiler-coldwake.svg"), W, H, *f)


if __name__ == "__main__":
    fig_boot_timeline()
    fig_wake_stub_path()
    fig_bootstrap_chain()
    fig_profiler_vantage()
    fig_profiler_coldwake()
    print("OK: 5 figures ->", IMG)
