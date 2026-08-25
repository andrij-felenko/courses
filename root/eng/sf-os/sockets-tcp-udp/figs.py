# -*- coding: utf-8 -*-
"""Фігури до теми «Сокети TCP/UDP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"   # тепле виділення (порт / лінія)


# ── 1. Що таке сокет: адреса + порт = кінцівка з'єднання ───────────────────────
# Ідея: IP знаходить машину, порт — програму на ній; разом це один кінець розмови.
def fig_socket():
    W, H = 760, 300
    f = [text(W / 2, 26, "Сокет — один кінець розмови: адреса + порт", size=15, bold=True)]

    # дві машини
    by, bh = 70, 150
    ax, aw = 48, 250
    bx, bw = 462, 250
    f.append(rect(ax, by, aw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(ax + aw / 2, by + 24, "машина A", size=12, color=NEG, bold=True))
    f.append(text(ax + aw / 2, by + 44, "192.168.1.10", size=11, color=INK, bold=True))
    f.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(bx + bw / 2, by + 24, "машина B", size=12, color=FIELD, bold=True))
    f.append(text(bx + bw / 2, by + 44, "192.168.1.20", size=11, color=INK, bold=True))

    # порти-«двері» на кожній машині
    for x, w, col in ((ax, aw, NEG), (bx, bw, FIELD)):
        f.append(rect(x + w / 2 - 42, by + 64, 84, 40, fill="#fff7e6", stroke=AMBER, sw=1.6, rx=7))
        f.append(text(x + w / 2, by + 80, "порт", size=9.5, color=AMBER))
        f.append(text(x + w / 2, by + 96, "8080" if col is NEG else "53", size=12, color=AMBER, bold=True))

    # лінія між сокетами
    midy = by + 84
    f.append(arrow(ax + aw + 4, midy, bx - 4, midy, color=INK, sw=2.0))
    f.append(arrow(bx - 4, midy + 18, ax + aw + 4, midy + 18, color=INK, sw=2.0))
    f.append(text((ax + aw + bx) / 2, midy - 8, "з'єднання", size=10, color=MUTED, italic=True))

    f.append(text(W / 2, by + bh + 26,
                  "адреса (IP) знаходить машину · порт знаходить програму на ній",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, by + bh + 44,
                  "пара {адреса : порт} і є сокет — кінцівка, до якої під'єднуються",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "socket.svg"), W, H, *f)


# ── 2. TCP проти UDP: дві вдачі однієї мережі ─────────────────────────────────
# Ідея: TCP — з'єднання, надійний упорядкований потік; UDP — датаграми «вистрелив
# і забув», без гарантій, зате легко й швидко.
def fig_tcp_udp():
    W, H = 760, 330
    f = [text(W / 2, 26, "TCP проти UDP: надійний потік чи легкі датаграми", size=15, bold=True)]

    lx, lw = 36, 340
    rx, rw = 384, 340
    by, bh = 54, 250
    f.append(rect(lx, by, lw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, by + 26, "TCP — потік із гарантіями", size=12.5, color=NEG, bold=True))
    for i, s in enumerate(["• спершу з'єднання (рукостискання)",
                           "• надійно: втрачене — повторюється",
                           "• порядок збережено: байти підряд",
                           "• потік без меж — не «листи», а ріка",
                           "• дорожче: стани, підтвердження, буфери"]):
        f.append(text(lx + 16, by + 58 + i * 32, s, size=10.2, color=INK, anchor="start"))

    f.append(rect(rx, by, rw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + rw / 2, by + 26, "UDP — датаграми без зобов'язань", size=12.5, color=FIELD, bold=True))
    for i, s in enumerate(["• без з'єднання: одразу шлеш",
                           "• без гарантій: може зникнути",
                           "• без порядку: міг прийти не той черзі",
                           "• межі є: одне sendto = одна датаграма",
                           "• дешево й швидко: майже сам IP"]):
        f.append(text(rx + 16, by + 58 + i * 32, s, size=10.2, color=INK, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "TCP бере на себе надійність; UDP лишає її тобі — натомість дає швидкість",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tcp-udp.svg"), W, H, *f)


# ── 3. Виклики сокетного API: дві колонки кроків (TCP-клієнт, UDP) ─────────────
# Ідея: показати порядок викликів BSD-сокетів окремо для TCP і для UDP — звідки
# видно, що в TCP є фаза з'єднання, а в UDP її немає.
def fig_api():
    W, H = 760, 340
    f = [text(W / 2, 26, "Послідовність викликів: TCP-клієнт і UDP-вузол", size=15, bold=True)]

    def column(x0, w, title, col, steps):
        f.append(text(x0 + w / 2, 56, title, size=12.5, color=col, bold=True))
        y, sh, gap = 70, 34, 12
        prev = None
        for s in steps:
            f.append(rect(x0, y, w, sh, fill="#fbfbfb", stroke=col, sw=1.5, rx=8))
            f.append(text(x0 + w / 2, y + 22, s, size=11, color=INK, bold=True))
            if prev is not None:
                f.append(arrow(x0 + w / 2, prev, x0 + w / 2, y - 3, color=MUTED, sw=1.5))
            prev = y + sh
            y += sh + gap

    column(70, 250, "TCP-клієнт", NEG,
           ["socket()", "connect()", "send()  /  recv()", "close()"])
    column(440, 250, "UDP-вузол", FIELD,
           ["socket()", "bind()", "sendto()  /  recvfrom()", "close()"])

    f.append(text(W / 2, H - 30,
                  "у TCP є окремий крок connect() — встановити з'єднання наперед;",
                  size=10.3, color=MUTED, italic=True))
    f.append(text(W / 2, H - 14,
                  "у UDP його немає: адресу кладуть у кожен sendto(), читають у recvfrom()",
                  size=10.3, color=MUTED, italic=True))
    render(os.path.join(IMG, "api.svg"), W, H, *f)


# ── 4. Сокети на мікроконтролері: той самий API над стеком lwIP ────────────────
# Ідея: знайомі BSD-виклики лежать НАД крихітним стеком lwIP, що крутиться в МК;
# програмі це виглядає як «звичайні» сокети.
def fig_lwip():
    W, H = 760, 300
    f = [text(W / 2, 26, "Сокети на МК: знайомий API над стеком lwIP", size=15, bold=True)]

    cx, cw = 200, 360
    layers = [
        ("твій код: socket / bind / connect / sendto / recv", FIELD, "#eafaf0"),
        ("BSD-сокети ESP-IDF (інтерфейс)", NEG, "#eef3ff"),
        ("lwIP: TCP, UDP, IP — крихітний стек у RAM МК", AMBER, "#fff7e6"),
        ("драйвер Wi-Fi / Ethernet → ефір чи дріт", MUTED, "#f4f6f8"),
    ]
    y, h, gap = 56, 46, 10
    for label, col, bg in layers:
        f.append(fitbox(cx, y, cw, h, label, size=11, color=INK, fill=bg, stroke=col, sw=1.6, rx=9))
        y += h + gap

    # бічна підпис-дужка: «однаковий API»
    bx = cx + cw + 20
    f.append(line(bx, 56, bx, 56 + h, color=NEG, sw=2))
    f.append(line(bx, 56 + 2 * (h + gap), bx, 56 + 2 * (h + gap) + h, color=AMBER, sw=2))
    f.append(text(bx + 8, 56 + h / 2 + 4, "той самий код,", size=10, color=NEG, anchor="start"))
    f.append(text(bx + 8, 56 + h / 2 + 18, "що й на ПК", size=10, color=NEG, anchor="start"))
    f.append(text(bx + 8, 56 + 2 * (h + gap) + h / 2 + 4, "увесь стек —", size=10, color=AMBER, anchor="start"))
    f.append(text(bx + 8, 56 + 2 * (h + gap) + h / 2 + 18, "кілька КБ RAM", size=10, color=AMBER, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "пишеш звичні сокети — а під ними працює стек, що влазить у пам'ять мікроконтролера",
                  size=10.3, color=MUTED, italic=True))
    render(os.path.join(IMG, "lwip.svg"), W, H, *f)


# ── 5. Коли TCP, а коли UDP ────────────────────────────────────────────────────
# Ідея: дві колонки тригерів вибору — за тим, що дорожче коштує: втрата чи затримка.
def fig_when():
    W, H = 760, 320
    f = [text(W / 2, 26, "Коли TCP, а коли UDP", size=15, bold=True)]

    lx, lw = 36, 340
    rx, rw = 384, 340
    by, bh = 54, 220
    f.append(rect(lx, by, lw, bh, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(lx + lw / 2, by + 26, "Бери TCP, коли втрата неприпустима", size=11.5, color=NEG, bold=True))
    for i, s in enumerate(["• конфігурація, команди, прошивка",
                           "• передача файлу — кожен байт важить",
                           "• HTTP / вебсервер, REST",
                           "• треба порядок і повнота даних"]):
        f.append(text(lx + 16, by + 58 + i * 34, s, size=10.2, color=INK, anchor="start"))

    f.append(rect(rx, by, rw, bh, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + rw / 2, by + 26, "Бери UDP, коли важить свіжість", size=11.5, color=FIELD, bold=True))
    for i, s in enumerate(["• телеметрія: новіший відлік цінніший",
                           "• відео й звук наживо — стара кадр зайвий",
                           "• синхронізація часу (NTP)",
                           "• розсилка багатьом одразу (multicast)"]):
        f.append(text(rx + 16, by + 58 + i * 34, s, size=10.2, color=INK, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "питання просте: що дорожче — втратити шматок чи дочекатися його повтору?",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "when.svg"), W, H, *f)


if __name__ == "__main__":
    fig_socket()
    fig_tcp_udp()
    fig_api()
    fig_lwip()
    fig_when()
    print("OK: 5 figures ->", IMG)
