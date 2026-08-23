# -*- coding: utf-8 -*-
"""Фігури для кроку «DH на папері» (root/course/progarch, views-and-communication).
Три в'ю на одну систему Digital Homes: ідея множинних в'ю, контейнерна в'ю,
в'ю розгортання. Запуск: python figs.py  → пише у ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)

ACCENT = "#2457d6"   # холодний акцент для рамок-в'ю
WARM   = "#c0392b"


# ── 1. Одна система — чотири в'ю (кожна відповідає на СВОЄ питання) ───────────
def fig_lenses():
    W, H = 980, 430
    pill, pw, ph = textbox(490, 92, "Одна система: Digital Homes",
                           size=16, bold=True, fill="#eef2ff", stroke=ACCENT, sw=2, pad=14)
    frags = [pill]
    cards = [
        (130, ["C4 · рівень 1", "Хто користується", "і що поруч зовні?"], "Контекст"),
        (375, ["C4 · рівень 2", "З яких запускних", "частин і якими", "протоколами?"], "Контейнери"),
        (620, ["", "Де фізично працює", "і що ламає мережа?"], "Розгортання"),
        (865, ["сценарій", "У якому ПОРЯДКУ", "крок за кроком?"], "Динаміка"),
    ]
    cy_top = 200
    for cx, lines, title in cards:
        # промінь від спільної системи до рамки в'ю
        frags.append(line(490, 92 + ph / 2, cx, cy_top, color=MUTED, sw=1.3))
    for cx, lines, title in cards:
        frags.append(rect(cx - 105, cy_top, 210, 190, fill=FILL, stroke=ACCENT, sw=1.6))
        frags.append(text(cx, cy_top + 32, title, size=16, bold=True, color=ACCENT))
        frags.append(mtext(cx, cy_top + 62, [l for l in lines], size=12, color=INK, lh=1.35))
    render(os.path.join(OUT, "views-lenses.svg"), W, H, *frags,
           title="Одна система — чотири в'ю, чотири питання")


# ── 2. Контейнерна в'ю DH (C4·2): які частини і чим говорять ──────────────────
def fig_container():
    W, H = 1150, 420
    yb = 190
    bw, bh = 150, 70
    centers = {
        "user": 105, "app": 340, "cloud": 575, "hub": 810, "dev": 1045,
    }
    frags = []
    # вузли
    frags.append(fitbox(centers["user"] - bw / 2, yb - bh / 2, bw, bh, "Мешканець",
                        size=15, fill="#eef2ff", stroke=ACCENT, sw=1.6))
    frags.append(circle(centers["user"], yb - bh / 2 - 2, 12, fill="#eef2ff", stroke=ACCENT, sw=1.6))
    frags.append(fitbox(centers["app"] - bw / 2, yb - bh / 2, bw, bh, "Мобільна апка", size=14))
    frags.append(fitbox(centers["cloud"] - bw / 2, yb - bh / 2, bw, bh, "Хмара DH\nстан дому + API", size=14))
    frags.append(fitbox(centers["hub"] - bw / 2, yb - bh / 2, bw, bh, "Хаб\n(у домі)", size=14))
    frags.append(fitbox(centers["dev"] - bw / 2, yb - bh / 2, bw, bh, "Пристрої\nлампа · замок · камера", size=13))
    # стрілки-ланцюг
    def edge(a, b):
        frags.append(arrow(centers[a] + bw / 2, yb, centers[b] - bw / 2, yb, sw=1.8))
    edge("user", "app"); edge("app", "cloud"); edge("cloud", "hub"); edge("hub", "dev")
    # підписи над стрілками (у порожній смузі)
    frags.append(text(222, 128, "користується", size=12, color=MUTED))
    frags.append(mtext(457, 118, ["HTTPS / REST", "керує, бачить стан"], size=12, color=INK))
    frags.append(mtext(692, 118, ["MQTT / TLS", "команди, телеметрія"], size=12, color=INK))
    frags.append(mtext(927, 118, ["Zigbee / BLE", "локально, мс"], size=12, color=INK))
    # локальний шлях: апка напряму до хаба (пунктир, нижче)
    frags.append('<path d="M340,225 Q575,360 810,225" fill="none" stroke="%s" '
                 'stroke-width="1.7" stroke-dasharray="6 5" marker-end="url(#arrow)"/>' % MUTED)
    frags.append(mtext(575, 360, ["у домашній Wi-Fi:", "апка напряму до хаба"], size=12, color=MUTED))
    render(os.path.join(OUT, "dh-container-view.svg"), W, H, *frags,
           title="Контейнерна в'ю Digital Homes")


# ── 3. В'ю розгортання: ті самі частини, але ДЕ вони фізично живуть ───────────
def fig_deployment():
    W, H = 1040, 540
    frags = []
    # регіон «дім»
    frags.append('<rect x="40" y="80" width="560" height="420" rx="14" fill="#f2fbf5" '
                 'stroke="%s" stroke-width="1.8" stroke-dasharray="8 6"/>' % FIELD)
    frags.append(text(320, 108, "Дім — локальна Wi-Fi", size=15, bold=True, color=FIELD))
    frags.append(fitbox(75, 150, 150, 60, "Телефон\n(апка)", size=13))
    frags.append(fitbox(270, 265, 220, 74, "Хаб (edge-бокс)\nрушій · буфер · лок. API", size=13))
    frags.append(fitbox(80, 372, 190, 60, "Пристрої\nлампа · замок · камера", size=12))
    # локальні лінії
    frags.append(line(225, 190, 270, 285, color=LINE, sw=1.6))
    frags.append(text(200, 244, "LAN", size=11, color=MUTED))
    frags.append(line(270, 320, 240, 372, color=LINE, sw=1.6))
    frags.append(text(150, 352, "Zigbee / BLE", size=11, color=MUTED))
    # регіон «хмара»
    frags.append('<rect x="700" y="200" width="310" height="160" rx="14" fill="#eef2ff" '
                 'stroke="%s" stroke-width="1.8"/>' % ACCENT)
    frags.append(text(855, 228, "Хмарний регіон", size=15, bold=True, color=ACCENT))
    frags.append(fitbox(755, 252, 200, 74, "Хмара DH\nстан дому + API", size=14))
    # міжрегіональний зв'язок через інтернет (може впасти)
    frags.append(line(490, 300, 755, 289, color=LINE, sw=1.8))
    frags.append(text(628, 262, "інтернет", size=12, color=INK))
    # маркер розриву на лінії
    frags.append(line(640, 286, 656, 302, color=WARM, sw=2.4))
    frags.append(line(656, 286, 640, 302, color=WARM, sw=2.4))
    frags.append(text(648, 326, "падає?", size=12, color=WARM, bold=True))
    render(os.path.join(OUT, "dh-deployment-view.svg"), W, H, *frags,
           title="В'ю розгортання Digital Homes")


if __name__ == "__main__":
    fig_lenses()
    fig_container()
    fig_deployment()
    print("OK: 3 фігури у", OUT)
