# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Акценти поверх палітри svgkit
RADIO = "#b9560f"; RADBG = "#fff1e6"; RADST = "#d2772a"   # радіо — тепле
MEDIA = "#6d28a8"; MEDBG = "#f5edfb"; MEDST = "#9b5fc7"   # медіа/графіка — фіолетове
CACHE = "#8a6a14"; CACBG = "#fff6e0"; CACST = "#caa24a"


def antenna(p, x, y_top, label="радіо"):
    p.append(line(x, y_top, x, y_top - 34, color=RADIO, sw=2.2))
    p.append(circle(x, y_top - 34, 2.6, fill=RADIO, stroke=RADIO, sw=0))
    p.append('<path d="M %.0f,%.0f A 9,9 0 0 1 %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (x + 5, y_top - 32, x + 5, y_top - 16, RADST))
    p.append('<path d="M %.0f,%.0f A 16,16 0 0 1 %.0f,%.0f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (x + 5, y_top - 40, x + 5, y_top - 8, RADST))


def no_radio(p, cx, cy):
    """Перекреслене коло — «радіо немає»."""
    r = 16
    p.append(circle(cx, cy, r, fill="#f3f3f3", stroke=POS, sw=2.4))
    p.append(line(cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7, color=POS, sw=2.4))


# ── p4-vs-s3: різне призначення ───────────────────────────────────────────────
def fig_p4_vs_s3():
    W, H = 880, 430
    p = []
    # S3
    p.append(rect(50, 80, 360, 300, fill="#fbfcff", stroke=INK, sw=2, rx=12))
    p.append(text(230, 104, "ESP32-S3 — універсал «AIoT»", size=13, color=INK, bold=True))
    p.append(rect(70, 124, 200, 70, fill=RADBG, stroke=RADST, sw=1.8, rx=8))
    p.append(text(170, 150, "Радіо на чипі", size=12, color=RADIO, bold=True))
    p.append(text(170, 170, "Wi-Fi 4 + BLE", size=10.5, color=INK))
    antenna(p, 360, 124)
    p.append(fitbox(70, 214, 200, 56, "2× Xtensa\nпомірні обчислення", size=11, fill="#fbecec", stroke=POS, sw=1.6, bold=True, color=POS))
    p.append(fitbox(70, 290, 320, 70, "~520 КБ RAM · дисплей по SPI\nдобрий для під'єднаних дрібниць",
                    size=11, fill=BG, stroke=INK, sw=1.5, bold=True))

    # P4
    p.append(rect(470, 80, 360, 300, fill="#fbfcff", stroke=INK, sw=2.4, rx=12))
    p.append(text(650, 104, "ESP32-P4 — обчислення й медіа", size=13, color=INK, bold=True))
    no_radio(p, 500, 158)
    p.append(text(640, 150, "Радіо немає", size=12, color=POS, bold=True))
    p.append(text(640, 170, "(доточують збоку)", size=10, color=MUTED))
    p.append(fitbox(490, 200, 320, 50, "2× RISC-V до 400 МГц + ШІ-вектор",
                    size=11.5, fill="#fbecec", stroke=POS, sw=1.6, bold=True, color=POS))
    p.append(fitbox(490, 258, 156, 50, "до 32 МБ\nPSRAM", size=11, fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(fitbox(654, 258, 156, 50, "камера · дисплей\nвідео H.264", size=11, fill=MEDBG, stroke=MEDST, sw=1.6, bold=True, color=MEDIA))
    p.append(fitbox(490, 316, 320, 46, "High-Speed USB · 55 GPIO · апаратна графіка",
                    size=10.5, fill=BG, stroke=INK, sw=1.5, bold=True))

    p.append(arrow(412, 230, 468, 230, color=INK, sw=2.4))
    p.append(text(440, 220, "інший", size=9.5, color=MUTED))
    p.append(text(440, 250, "вибір", size=9.5, color=MUTED))
    p.append(text(W / 2, 412, "не «потужніший S3», а чіп під іншу роботу: радіо виміняне на обчислення й ввід-вивід",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "p4-vs-s3.svg"), W, H, *p,
           title="ESP32-P4 проти ESP32-S3: різне призначення в межах родини")


# ── cores: три ядра ───────────────────────────────────────────────────────────
def fig_cores():
    W, H = 780, 300
    p = []
    busy = 212
    p.append(fitbox(70, 90, 210, 84, "Ядро 0 (HP)\nRISC-V · до 400 МГц\nFPU + ШІ-вектор",
                    size=11.5, fill="#fbecec", stroke=POS, sw=2, bold=True, color=POS))
    p.append(fitbox(300, 90, 210, 84, "Ядро 1 (HP)\nRISC-V · до 400 МГц\nFPU + ШІ-вектор",
                    size=11.5, fill="#fbecec", stroke=POS, sw=2, bold=True, color=POS))
    p.append(text(175, 188, "важка логіка, інтерфейс, зображення", size=9.5, color=MUTED))
    p.append(fitbox(560, 100, 160, 66, "LP-ядро\nдо 40 МГц\nжевріє у сні", size=11, fill=BG, stroke=INK, sw=1.8, bold=True))

    p.append(line(120, busy, 640, busy, color=FIELD, sw=5))
    p.append(text(640, busy - 9, "спільні пам'ять і периферія", size=10, color=FIELD, anchor="end", bold=True))
    p.append(line(175, 174, 175, busy, color=FIELD, sw=2))
    p.append(line(405, 174, 405, busy, color=FIELD, sw=2))
    p.append(line(640, 166, 640, busy, color=INK, sw=1.6, dash="4 3"))
    p.append(arrow(560, 133, 510, 133, color=POS, sw=1.8))
    p.append(text(535, 122, "будить за потреби", size=9, color=POS, anchor="middle"))

    p.append(text(W / 2, 264, "знайома двоступенева ощадність родини — тільки «велика» половина набагато потужніша",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "cores.svg"), W, H, *p,
           title="Три ядра P4: дві HP-машини RISC-V і ощадне LP-ядро")


# ── mipi: рідні шини камери й дисплея ─────────────────────────────────────────
def fig_mipi():
    W, H = 860, 320
    p = []
    # чіп
    p.append(rect(320, 90, 220, 150, fill="#fbfcff", stroke=INK, sw=2.4, rx=12))
    p.append(text(430, 116, "ESP32-P4", size=14, color=INK, bold=True))
    p.append(fitbox(338, 132, 184, 40, "MIPI-DSI (вихід)", size=11, fill=MEDBG, stroke=MEDST, sw=1.6, bold=True, color=MEDIA))
    p.append(fitbox(338, 182, 184, 46, "MIPI-CSI + ISP\n(вхід)", size=11, fill=MEDBG, stroke=MEDST, sw=1.6, bold=True, color=MEDIA))

    # дисплей праворуч
    p.append(rect(640, 100, 180, 86, fill="#eef3fb", stroke=NEG, sw=2, rx=10))
    p.append(text(730, 130, "Дисплей", size=13, color=NEG, bold=True))
    p.append(text(730, 152, "до 1080p", size=11, color=INK))
    p.append(text(730, 170, "як у смартфоні", size=9.5, color=MUTED))
    p.append(arrow(540, 152, 638, 143, color=MEDIA, sw=2.4))

    # камера ліворуч
    p.append(rect(40, 150, 180, 90, fill="#eef6ef", stroke=FIELD, sw=2, rx=10))
    p.append(text(130, 178, "Камера", size=13, color=FIELD, bold=True))
    p.append(text(130, 200, "сирий потік", size=10.5, color=INK))
    p.append(text(130, 220, "→ ISP робить кадр", size=9.5, color=MUTED))
    p.append(arrow(220, 200, 318, 203, color=MEDIA, sw=2.4))

    p.append(text(W / 2, 300, "екран і камеру під'єднано їхніми рідними швидкими шинами, а не пристосованим SPI",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "mipi.svg"), W, H, *p,
           title="MIPI-DSI до дисплея, MIPI-CSI з ISP від камери")


# ── companion: радіо-компаньйон через ESP-Hosted ──────────────────────────────
def fig_companion():
    W, H = 820, 330
    p = []
    # P4 (господар)
    p.append(rect(60, 110, 300, 140, fill="#fbfcff", stroke=INK, sw=2.4, rx=12))
    p.append(text(210, 138, "ESP32-P4 (господар)", size=13, color=INK, bold=True))
    p.append(text(210, 162, "обчислення · екран · камера", size=10.5, color=INK))
    no_radio(p, 90, 220)
    p.append(text(210, 224, "радіо немає", size=11, color=POS, bold=True))

    # C6 (підлеглий)
    p.append(rect(540, 110, 220, 140, fill="#fff1e6", stroke=RADST, sw=2.2, rx=12))
    p.append(text(650, 138, "ESP32-C6", size=13, color=RADIO, bold=True))
    p.append(text(650, 158, "(підлеглий, радіо)", size=10, color=MUTED))
    p.append(text(650, 182, "Wi-Fi 6 + BLE", size=11.5, color=INK, bold=True))
    antenna(p, 745, 110)

    # шина між ними
    p.append(arrow(360, 175, 538, 175, color=INK, sw=2.4))
    p.append(arrow(538, 200, 360, 200, color=INK, sw=2.4))
    p.append(text(449, 165, "ESP-Hosted", size=11, color=NEG, bold=True))
    p.append(text(449, 222, "SDIO / SPI / UART", size=9.5, color=MUTED))

    p.append(text(W / 2, 304, "зв'язок доточують рівно тоді, коли потрібен, — і не їсть кристал, коли ні",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "companion.svg"), W, H, *p,
           title="P4 рахує й малює, ESP32-C6 поруч дає Wi-Fi/BLE через ESP-Hosted")


# ── when-which: тригери вибору ────────────────────────────────────────────────
def fig_when_which():
    W, H = 880, 360
    p = []
    # ліворуч — P4
    p.append(rect(50, 80, 380, 250, fill=MEDBG, stroke=MEDST, sw=2, rx=12))
    p.append(text(240, 106, "Тягне до P4", size=14, color=MEDIA, bold=True))
    left = ["великий жвавий екран (HMI)", "камера й запис відео",
            "важкі локальні обчислення (ШІ)", "швидкий ввід-вивід (HS-USB)"]
    for i, ln in enumerate(left):
        p.append(text(72, 140 + i * 34, "• " + ln, size=12, color=INK, anchor="start"))

    # праворуч — звичайний ESP32
    p.append(rect(450, 80, 380, 250, fill=RADBG, stroke=RADST, sw=2, rx=12))
    p.append(text(640, 106, "Тягне до звичайного ESP32", size=14, color=RADIO, bold=True))
    right = ["суть задачі — зв'язок (Wi-Fi/BLE)", "проста дешева масова річ",
             "потрібен один чіп без компаньйона", "екрана й камери нема"]
    for i, ln in enumerate(right):
        p.append(text(472, 140 + i * 34, "• " + ln, size=12, color=INK, anchor="start"))

    p.append(text(W / 2, 348, "часто задача чітко світиться однією з колонок: «про екран і камеру» чи «про вихід у мережу»",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "when-which.svg"), W, H, *p,
           title="Коли P4, а коли звичайний ESP32: тригери вибору")


if __name__ == "__main__":
    fig_p4_vs_s3(); fig_cores(); fig_mipi(); fig_companion(); fig_when_which()
    print("OK: figures written to", OUT)
