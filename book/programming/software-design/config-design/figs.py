# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: один артефакт — багато середовищ ──────────────────────────────
# Той самий незмінний бінарник ліворуч; праворуч три середовища, у кожне він
# заходить з іншим конфігом. Показує суть: код один, форма — ззовні.
def fig_one_artifact():
    W, H = 720, 380
    frags = []

    # Артефакт (незмінний) ліворуч
    ax, ay, aw, ah = 40, 150, 150, 90
    frags.append(rect(ax, ay, aw, ah, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(ax + aw / 2, ay + 34, "той самий", size=14, color=INK))
    frags.append(text(ax + aw / 2, ay + 56, "бінарник", size=15, color=INK, bold=True))
    frags.append(text(ax + aw / 2, ay - 14, "build раз", size=13, color=MUTED))

    # Три середовища праворуч
    envs = [
        ("dev", "БД: localhost\nлог: debug\nключ: тестовий", "#eafaf1", FIELD),
        ("staging", "БД: stage-db\nлог: info\nключ: staging", "#fff7e6", "#b8860b"),
        ("prod", "БД: prod-db\nлог: warn\nключ: бойовий", "#fdecea", POS),
    ]
    ex = 430
    ew, eh = 250, 96
    ey0 = 40
    gap = 16
    for i, (name, cfg, fill, col) in enumerate(envs):
        ey = ey0 + i * (eh + gap)
        frags.append(rect(ex, ey, ew, eh, fill=fill, stroke=col, sw=2))
        frags.append(text(ex + 60, ey + 24, name, size=15, color=col, bold=True))
        # конфіг рядками
        for j, ln in enumerate(cfg.split("\n")):
            frags.append(text(ex + 130, ey + 22 + j * 22, ln, size=13,
                              color=INK, anchor="start"))
        # стрілка від артефакту до середовища
        frags.append(arrow(ax + aw + 6, ay + ah / 2, ex - 8, ey + eh / 2, color=col))
        # мітка «+ конфіг» на стрілці (виносимо вбік, щоб не накладалось)
        mx = (ax + aw + ex) / 2
        my = (ay + ah / 2 + ey + eh / 2) / 2
        frags.append(text(mx, my - 6, "+ конфіг", size=12, color=col, bold=True))

    render(os.path.join(IMG, "one-artifact-many-envs.svg"), W, H, *frags)


# ── Фігура 2: шари конфігу перекривають один одного ─────────────────────────
# Пласти від найслабшого (типові значення в коді) до найсильнішого (аргумент
# командного рядка). Що вище — то більша вага; верхній перебиває нижні.
def fig_layers():
    W, H = 680, 430
    frags = []

    layers = [
        ("аргумент командного рядка", "--port=9090", "#fdecea", POS, "найсильніший"),
        ("змінні середовища", "PORT=8080", "#fff3e0", "#c66900", ""),
        ("файл середовища", "config.prod.yaml", "#fff7e6", "#b8860b", ""),
        ("спільний файл", "config.yaml", "#eafaf1", FIELD, ""),
        ("типові значення в коді", "port = 3000", "#eef2ff", NEG, "найслабший"),
    ]
    # малюємо знизу вгору: останній у списку — найнижчий пласт
    bx = 150
    bw = 300
    bh = 56
    gap = 10
    n = len(layers)
    y0 = 60
    for idx, (name, val, fill, col, tag) in enumerate(layers):
        # idx 0 (найсильніший) має бути ЗВЕРХУ
        y = y0 + idx * (bh + gap)
        frags.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=2))
        frags.append(text(bx + bw / 2, y + 22, name, size=14, color=INK, bold=True))
        frags.append(text(bx + bw / 2, y + 42, val, size=13, color=MUTED))
        if tag:
            frags.append(text(bx + bw + 20, y + bh / 2 + 5, tag, size=13,
                              color=col, anchor="start", bold=True))

    # вертикальна стрілка ваги збоку зліва
    axx = 100
    frags.append(arrow(axx, y0 + (n - 1) * (bh + gap) + bh, axx, y0, color=INK, sw=2))
    frags.append(text(axx - 12, y0 + (n * (bh + gap)) / 2, "вага росте", size=13,
                     color=INK, anchor="middle"))
    # повертаємо підпис вертикально
    # (простіше: ставимо його вертикальним через transform)
    frags[-1] = ('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>'
                 % (axx - 14, y0 + (n * (bh + gap)) / 2, FONT, INK,
                    axx - 14, y0 + (n * (bh + gap)) / 2, "вага росте вгору"))

    render(os.path.join(IMG, "config-layers.svg"), W, H, *frags)


# ── Фігура 3 (для hist-вставки): чому конфіг переселився в середовище ────────
# Ліворуч старий світ — database.yml із секретом усередині артефакту, збірку
# не перенести, секрет тече в git. Праворуч світ Heroku — один образ, ефемерні
# дино, конфіг приходить ззовні через DATABASE_URL при запуску.
def fig_config_in_env_birth():
    W, H = 900, 440
    frags = []

    # вертикальний розділювач двох світів
    midx = W / 2
    frags.append(line(midx, 40, midx, H - 30, color=MUTED, sw=1.5, dash="6 6"))
    frags.append(text(W * 0.25, 34, "старий світ: конфіг у коді",
                      size=15, color=INK, bold=True))
    frags.append(text(W * 0.75, 34, "світ PaaS: конфіг у середовищі",
                      size=15, color=INK, bold=True))

    # ── ЛІВОРУЧ: артефакт із зашитим файлом ───────────────────────────────
    ax, ay, aw, ah = 60, 90, 300, 150
    frags.append(rect(ax, ay, aw, ah, fill="#eef2ff", stroke=NEG, sw=2))
    frags.append(text(ax + aw / 2, ay + 26, "один артефакт (збірка)",
                      size=14, color=INK, bold=True))
    # вкладений файл-конфіг із секретом
    fx, fy, fw, fh = ax + 24, ay + 44, aw - 48, 84
    frags.append(rect(fx, fy, fw, fh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(fx + fw / 2, fy + 22, "database.yml",
                      size=13, color=INK, bold=True))
    frags.append(text(fx + fw / 2, fy + 44, "host: prod-db",
                      size=12, color=MUTED))
    frags.append(text(fx + fw / 2, fy + 64, "password: s3cr3t",
                      size=12, color=POS, bold=True))
    # два наслідки під артефактом
    frags.append(text(ax + aw / 2, ay + ah + 32,
                      "секрет тече в git · збірку не перенести",
                      size=13, color=POS))
    frags.append(text(ax + aw / 2, ay + ah + 58,
                      "між середовищами",
                      size=13, color=POS))

    # ── ПРАВОРУЧ: один образ → ефемерні дино, конфіг ззовні ────────────────
    ix, iy, iw, ih = midx + 40, 90, 150, 66
    frags.append(rect(ix, iy, iw, ih, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(ix + iw / 2, iy + 30, "один образ",
                      size=14, color=INK, bold=True))
    frags.append(text(ix + iw / 2, iy + 50, "(slug)",
                      size=12, color=MUTED))

    # три ефемерні дино праворуч від образу
    dyx = ix + iw + 70
    dyw, dyh = 118, 40
    dyys = [96, 150, 204]
    for k, dyy in enumerate(dyys):
        frags.append(rect(dyx, dyy, dyw, dyh, fill=FILL, stroke=MUTED, sw=1.5,
                          rx=6))
        frags.append(text(dyx + dyw / 2, dyy + 25, "дино (тимчасове)",
                          size=11, color=MUTED))
        frags.append(arrow(ix + iw + 6, iy + ih / 2, dyx - 6, dyy + dyh / 2,
                          color=FIELD))

    # змінна середовища заходить у дино ззовні при запуску
    envy = 300
    ew2, eh2 = 208, 46
    ex2 = dyx + dyw / 2 - ew2 / 2   # відцентрувати під колонкою дино
    frags.append(rect(ex2, envy, ew2, eh2, fill="#fff3e0", stroke="#c66900",
                     sw=2))
    frags.append(text(ex2 + ew2 / 2, envy + 20, "змінна середовища при запуску",
                      size=12, color=INK, bold=True))
    frags.append(text(ex2 + ew2 / 2, envy + 38, "DATABASE_URL=…",
                      size=12, color="#c66900", bold=True))
    # стрілка від env угору до нижнього дино
    frags.append(arrow(ex2 + ew2 / 2, envy - 4,
                      dyx + dyw / 2, dyys[-1] + dyh + 4, color="#c66900"))

    render(os.path.join(IMG, "config-in-env-birth.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_one_artifact()
    fig_layers()
    fig_config_in_env_birth()
    print("figs done")
