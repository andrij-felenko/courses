# -*- coding: utf-8 -*-
"""Фігури до вставки «Робочий типостан-автомат». Вивід — ./img/*.svg.
Окремий скрипт, щоб не чіпати figs.py/figs_d.py власника теми."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_affine_move():
    """Афінні типи (Rust) проти простого перетипування (TypeScript).
    У Rust перехід СПОЖИВАЄ старий хендл — стале вжити не можна.
    У TS обʼєкт лишається живим — стале компілюється й падає в рантаймі."""
    W, H = 920, 350
    f = []
    f.append(text(W / 2, 34, "Афінні типи проти простого перетипування", size=17, bold=True))
    f.append(line(30, 192, 890, 192, color=MUTED, sw=1, dash="4 4"))

    # ── Rust ──
    f.append(text(40, 92, "Rust — перехід споживає self:", size=13, bold=True, anchor="start"))
    f.append(fitbox(40, 108, 150, 52, "open\nConn<Open>", size=13,
                    fill="#eeeeee", stroke=MUTED, sw=1.5, color=MUTED, bold=True))
    f.append(arrow(196, 134, 300, 134, color=INK, sw=1.8))
    f.append(text(248, 122, "authenticate(self)", size=11, color=INK))
    f.append(fitbox(306, 108, 160, 52, "authed\nConn<Authed>", size=13,
                    fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))
    f.append(fitbox(496, 106, 394, 56,
                    "open ПЕРЕМІЩЕНО: будь-який пізніший\nopen.* — помилка збірки E0382",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, color=INK))

    # ── TypeScript ──
    f.append(text(40, 214, "TypeScript — обʼєкт лише перетиповано:", size=13, bold=True, anchor="start"))
    f.append(fitbox(40, 230, 150, 52, "open\nConn<'open'>", size=13,
                    fill=FILL, stroke=NEG, sw=1.5, color=INK, bold=True))
    f.append(arrow(196, 256, 300, 256, color=INK, sw=1.8))
    f.append(text(248, 244, "authenticate()", size=11, color=INK))
    f.append(fitbox(306, 230, 160, 52, "authed\nConn<'authed'>", size=13,
                    fill=FILL, stroke=NEG, sw=1.5, color=INK, bold=True))
    f.append(fitbox(496, 228, 394, 56,
                    "old open ДОСІ ЖИВИЙ: після close()\nold.request() компілюється — баг рантайму",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5, color=INK))

    render(os.path.join(IMG, "affine-move.svg"), W, H, *f)


def fig_builder_lattice():
    """Ґратка станів будівника RequestBuilder<U, M>. url() рухає по осі U,
    method() — по осі M; send() існує лише у вершині <Set, Set>."""
    W, H = 740, 470
    f = []
    f.append(text(W / 2, 34, "Будівник: send() лише коли обидва обовʼязкові задані",
                  size=16, bold=True))

    nw, nh = 200, 60
    MM = (80, 320)    # Missing, Missing
    SM = (440, 320)   # Set, Missing  (після url)
    MS = (80, 150)    # Missing, Set  (після method)
    SS = (440, 150)   # Set, Set      (після обох) -> send

    # переходи (під вузлами)
    f.append(arrow(MM[0] + nw, MM[1] + nh / 2, SM[0], SM[1] + nh / 2, color=INK, sw=1.8))
    f.append(arrow(MS[0] + nw, MS[1] + nh / 2, SS[0], SS[1] + nh / 2, color=INK, sw=1.8))
    f.append(arrow(MM[0] + nw / 2, MM[1], MS[0] + nw / 2, MS[1] + nh, color=INK, sw=1.8))
    f.append(arrow(SM[0] + nw / 2, SM[1], SS[0] + nw / 2, SS[1] + nh, color=INK, sw=1.8))

    # підписи переходів (поза лініями)
    f.append(text(360, 340, "url()", size=12, color=INK))
    f.append(text(360, 170, "url()", size=12, color=INK))
    f.append(text(215, 268, "method()", size=12, color=INK, anchor="start"))
    f.append(text(505, 268, "method()", size=12, color=INK, anchor="end"))

    # вузли (над лініями)
    f.append(fitbox(MM[0], MM[1], nw, nh, "<Missing, Missing>\nsend() нема", size=13,
                    fill=FILL, stroke=NEG, sw=1.6, color=INK))
    f.append(fitbox(SM[0], SM[1], nw, nh, "<Set, Missing>\nsend() нема", size=13,
                    fill=FILL, stroke=NEG, sw=1.6, color=INK))
    f.append(fitbox(MS[0], MS[1], nw, nh, "<Missing, Set>\nsend() нема", size=13,
                    fill=FILL, stroke=NEG, sw=1.6, color=INK))
    f.append(fitbox(SS[0], SS[1], nw, nh, "<Set, Set>\nsend() ✓", size=13,
                    fill="#eafaf1", stroke=FIELD, sw=2.0, color=INK, bold=True))

    # старт
    f.append(arrow(MM[0] + nw / 2, 430, MM[0] + nw / 2, MM[1] + nh, color=MUTED, sw=1.6))
    f.append(text(MM[0] + nw / 2, 452, "new()", size=12, color=MUTED))

    render(os.path.join(IMG, "builder-lattice.svg"), W, H, *f)


if __name__ == "__main__":
    fig_affine_move()
    fig_builder_lattice()
    print("ok")
