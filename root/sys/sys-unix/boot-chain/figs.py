# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Сходи ланок: хто виконує, звідки код, як знаходить наступного ────────
def fig_chain_ladder():
    W, H = 1360, 760
    p = []

    c1x, c1w = 50, 300
    c2x, c2w = 372, 372
    c3x, c3w = 766, 544

    p.append(text(c1x + c1w / 2, 74, "ланка", size=15, bold=True))
    p.append(text(c2x + c2w / 2, 74, "де живе її код", size=15, bold=True))
    p.append(text(c3x + c3w / 2, 74, "як вона знаходить наступну", size=15, bold=True))

    rows = [
        ("Прошивка",
         "постійна пам'ять на платі;\nадресу першої команди задає схема",
         "читає файл із розділу ESP\n(у старій схемі — перший сектор диска)",
         BLUE_FILL),
        ("Завантажувач",
         "файл на ESP\nабо блоки, дописані біля початку диска",
         "читає з файлової системи ядро, initramfs\nі складає рядок параметрів",
         BLUE_FILL),
        ("Стиснене ядро",
         "образ, покладений у пам'ять\nпопередньою ланкою",
         "розпаковує саме себе на місці\nй передає керування всередину",
         WARM_FILL),
        ("Ядро",
         "розпакований код у пам'яті;\nносії ще не змонтовані",
         "піднімає підсистеми й розпаковує\ncpio-архів у rootfs — файлову систему в пам'яті",
         WARM_FILL),
        ("/init з initramfs",
         "rootfs: кілька мегабайтів\nу оперативній пам'яті",
         "знаходить і монтує справжній корінь,\nпереставляє корінь і викликає exec",
         WARM_FILL),
        ("init, він же PID 1",
         "справжній корінь на носії;\nпроцес живе до вимкнення",
         "наступної ланки немає — від цієї миті\nвін не шукає, а тримає служби",
         GREEN_FILL),
    ]

    y = 96
    rh, gap = 94, 14
    for name, where, howto, fill in rows:
        p.append(fitbox(c1x, y, c1w, rh, name, size=16, bold=True, fill=fill))
        p.append(fitbox(c2x, y, c2w, rh, where, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(c3x, y, c3w, rh, howto, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        y += rh + gap

    render(os.path.join(IMG, 'chain-ladder.svg'), W, H, *p)


# ── 2. switch_root: той самий процес, інший корінь ──────────────────────────
def fig_switch_root():
    W, H = 1320, 600
    p = []

    lx, rx, pw, py, ph = 30, 790, 500, 70, 470
    p.append(rect(lx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(rx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(text(lx + pw / 2, 104, "до переходу", size=16, bold=True))
    p.append(text(rx + pw / 2, 104, "після переходу", size=16, bold=True))

    # ліва панель
    p.append(fitbox(lx + 30, 132, 440, 70,
                    "PID 1 — /init з initramfs",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(lx + 30, 232, 440, 74,
                    "корінь: rootfs у пам'яті\n(розпакований cpio-архів)",
                    size=13, fill=WARM_FILL))
    p.append(fitbox(lx + 30, 330, 440, 74,
                    "/sysroot: справжня файлова система,\nщойно змонтована з носія",
                    size=13, fill=GREY_FILL))
    p.append(text(lx + pw / 2, 452, "пам'ять під rootfs зайнята", size=13, color=MUTED))
    p.append(text(lx + pw / 2, 478, "процеси відлічують шляхи від rootfs", size=13, color=MUTED))

    # права панель
    p.append(fitbox(rx + 30, 132, 440, 70,
                    "PID 1 — /usr/lib/systemd/systemd",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(rx + 30, 232, 440, 74,
                    "корінь: справжня файлова система\nз носія",
                    size=13, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(rx + 30, 330, 440, 74,
                    "rootfs: відчеплений,\nпам'ять повернуто системі",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(text(rx + pw / 2, 452, "номер процесу той самий: 1", size=13, color=MUTED))
    p.append(text(rx + pw / 2, 478, "код у ньому — уже інший", size=13, color=MUTED))

    # середина
    mid = (lx + pw + rx) / 2
    p.append(text(mid, 196, "переносимо /dev, /proc, /sys", size=13))
    p.append(text(mid, 226, "переставляємо корінь", size=13))
    p.append(text(mid, 256, "exec поверх себе", size=13))
    p.append(arrow(lx + pw + 20, 310, rx - 20, 310))
    p.append(text(mid, 348, "нового процесу", size=13, color=MUTED))
    p.append(text(mid, 374, "не з'являється", size=13, color=MUTED))

    render(os.path.join(IMG, 'switch-root.svg'), W, H, *p)


# ── 3. Довіра йде тими самими ребрами ──────────────────────────────────────
def fig_trust_chain():
    W, H = 1340, 560
    p = []

    y = 176
    nodes = [
        (140, "вшитий ключ\nу постійній пам'яті", GREEN_FILL, FIELD),
        (420, "прошивка", BLUE_FILL, NEG),
        (700, "завантажувач", BLUE_FILL, NEG),
        (960, "ядро", BLUE_FILL, NEG),
        (1210, "initramfs\nі рядок параметрів", RED_FILL, POS),
    ]
    edges = []
    for cx, label, fill, stroke in nodes:
        fr, x0, x1, y0, y1 = tb(cx, y, label.split("\n"), size=14,
                                fill=fill, stroke=stroke, min_w=190)
        p.append(fr)
        edges.append((x0, x1))

    for i in range(3):
        p.append(arrow(edges[i][1] + 10, y, edges[i + 1][0] - 10, y))
        p.append(text((edges[i][1] + edges[i + 1][0]) / 2, y - 26,
                      "перевіряє підпис", size=12, color=MUTED))
    p.append(arrow(edges[3][1] + 10, y, edges[4][0] - 10, y, color=POS))
    p.append(text((edges[3][1] + edges[4][0]) / 2, y - 26,
                  "підпису немає", size=12, color=POS))

    p.append(text(140, 268, "корінь довіри: змінити не можна", size=12, color=MUTED))
    p.append(text(1210, 268, "зібрані вже на цій машині", size=12, color=MUTED))

    # нижній ряд: єдиний образ
    p.append(fitbox(700, 380, 620, 96,
                    "єдиний образ: ядро, рядок параметрів і initramfs\nскладені в один файл — і підписані разом",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(660, y + 44, 700, 372))
    p.append(text(370, 420, "дірку закривають так:", size=13, color=MUTED))

    render(os.path.join(IMG, 'trust-chain.svg'), W, H, *p)


# ── 4. Довжина ланцюга за добами ───────────────────────────────────────────
def fig_chain_eras():
    W, H = 1500, 700
    p = []

    c1x, c1w = 40, 268
    c2x, c2w = 332, 700
    c3x, c3w = 1056, 404

    p.append(text(c1x + c1w / 2, 72, "доба", size=15, bold=True))
    p.append(text(c2x + c2w / 2, 72, "ланки між живленням і ядром", size=15, bold=True))
    p.append(text(c3x + c3w / 2, 72, "чим це вимушене", size=15, bold=True))

    rows = [
        ("BIOS і LILO\n1990-ті",
         "перший сектор, 446 байтів коду  →  решта коду,\nзнайдена за жорстким списком номерів блоків  →  ядро",
         "прошивка знає лише «сектор нуль»\nі нічого не знає про файли",
         RED_FILL),
        ("BIOS і GRUB Legacy\nвід 1999",
         "перший сектор  →  проміжна частина в щілині\nперед першим розділом  →  основна частина файлом  →  ядро",
         "проміжна частина приносить із собою\nдрайвер файлової системи",
         WARM_FILL),
        ("UEFI і GRUB 2\nвід середини 2000-х",
         "прошивка читає файл із розділу ESP  →  завантажувач  →  ядро",
         "прошивка сама розуміє FAT,\nа список завантажень лежить у її пам'яті",
         BLUE_FILL),
        ("UEFI і EFI-заглушка\nвід ядра 3.3, 2012",
         "прошивка  →  ядро",
         "ядро прикидається програмою у форматі\nпрошивки й запускає себе саме",
         GREEN_FILL),
        ("UEFI і єдиний образ\n(UKI)",
         "прошивка  →  один файл: ядро, рядок параметрів, initramfs",
         "підписати треба все, а не лише ядро,\nтож усе складають в один підписаний файл",
         GREEN_FILL),
    ]

    y = 96
    rh, gap = 98, 16
    for era, chain, why, fill in rows:
        p.append(fitbox(c1x, y, c1w, rh, era, size=14, bold=True, fill=fill))
        p.append(fitbox(c2x, y, c2w, rh, chain, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(c3x, y, c3w, rh, why, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        y += rh + gap

    render(os.path.join(IMG, 'chain-eras.svg'), W, H, *p)


# ── 5. Розкладка файлу initramfs: дві cpio-частини в одному файлі ──────────
def fig_initramfs_layout():
    W, H = 1240, 480
    p = []

    x0, xm, x1 = 60, 452, 1180
    ytop, bh = 168, 104

    p.append(text((x0 + x1) / 2, 62, "один файл /boot/initrd.img-…", size=17, bold=True))

    p.append(fitbox(x0, ytop, xm - x0, bh,
                    "рання частина\ncpio БЕЗ стиснення\nkernel/x86/microcode/…",
                    size=14, fill=WARM_FILL))
    p.append(fitbox(xm, ytop, x1 - xm, bh,
                    "основна частина\ncpio, стиснений (gzip / zstd / lz4)\n"
                    "/init · /etc/initrd-release · модулі · сценарії пошуку кореня",
                    size=14, fill=BLUE_FILL))

    # маркер зсуву 0 і чому там падає zcat
    p.append(line(x0, ytop - 46, x0, ytop - 6, color=POS, sw=2))
    p.append(text(x0 + 6, ytop - 54, "зсув 0 — сюди дивиться zcat", size=13,
                  color=POS, anchor="start"))

    # підписи знизу: що з чим робить кожен інструмент
    p.append(text((x0 + xm) / 2, ytop + bh + 42, "unmkinitramfs → early/", size=13, color=MUTED))
    p.append(text((xm + x1) / 2, ytop + bh + 42, "unmkinitramfs → main/", size=13, color=MUTED))

    frag, _, _, _, _ = tb((x0 + x1) / 2, ytop + bh + 116,
                          "Мікрокод потрібен ядру раніше за будь-який розпаковувач,\n"
                          "тож ця частина лежить відкритим текстом — і файл починається не з підпису gzip.\n"
                          "На машині без мікрокоду ранньої частини немає зовсім, і той самий zcat спрацьовує.",
                          size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'initramfs-layout.svg'), W, H, *p)


# ── 6. blame проти критичного шляху ────────────────────────────────────────
def fig_blame_vs_chain():
    W, H = 1280, 560
    p = []

    nx, nw = 40, 396          # колонка назв
    bx, bw = 452, 128         # колонка місця в blame
    tx, tw = 608, 620         # смуга часу
    T = 11.0                  # секунд на всю смугу
    sx = tw / T

    p.append(text(nx + nw / 2, 62, "юніт", size=15, bold=True))
    p.append(text(bx + bw / 2, 62, "місце в blame", size=15, bold=True))
    p.append(text(tx + tw / 2, 62, "коли він насправді працював", size=15, bold=True))

    rows = [
        ("snapd.seeded.service", "№ 1", 0.903, 8.402, RED_FILL, POS),
        ("systemd-journal-flush.service", "№ 4", 1.104, 0.744, GREY_FILL, MUTED),
        ("systemd-udev-settle.service", "№ 3", 1.421, 2.301, GREEN_FILL, FIELD),
        ("NetworkManager.service", "№ 5", 3.722, 0.381, GREEN_FILL, FIELD),
        ("NetworkManager-wait-online.service", "№ 2", 4.103, 6.114, GREEN_FILL, FIELD),
    ]

    y, rh, gap = 96, 52, 22
    for name, rank, at, dur, fill, edge in rows:
        p.append(fitbox(nx, y, nw, rh, name, size=13, fill=fill, stroke=edge, sw=1.4))
        p.append(fitbox(bx, y, bw, rh, rank, size=14, bold=True, fill="#ffffff",
                        stroke=MUTED, sw=1.2))
        p.append(rect(tx + at * sx, y + 8, dur * sx, rh - 16, fill=fill, stroke=edge, sw=1.4, rx=4))
        p.append(text(tx + at * sx + dur * sx + 10,
                      y + rh / 2 + 5,
                      "@%.3f  +%.3f" % (at, dur), size=12, color=MUTED, anchor="start"))
        y += rh + gap

    axis_y = y + 14
    p.append(line(tx, axis_y, tx + tw, axis_y, color=MUTED, sw=1.4))
    for s in range(0, 12, 2):
        p.append(line(tx + s * sx, axis_y, tx + s * sx, axis_y + 7, color=MUTED, sw=1.2))
        p.append(text(tx + s * sx, axis_y + 25, "%d с" % s, size=12, color=MUTED))

    # межа: коли досягнуто цілі
    gx = tx + 10.217 * sx
    p.append(line(gx, 88, gx, axis_y, color=FIELD, sw=2, dash="6 5"))
    p.append(text(gx, 80, "graphical.target @10.218", size=13, color=FIELD, bold=True))

    frag, _, _, _, _ = tb(W / 2, axis_y + 80,
                          "Зелені три склеюються встик: 1.421+2.301 = 3.722, 3.722+0.381 = 4.103, "
                          "4.103+6.114 = 10.217 — це і є шлях.\n"
                          "Червоний найдовший, але закінчився за секунду до цілі: прибрати його — "
                          "і завантаження триватиме рівно стільки ж.",
                          size=13, fill="#ffffff", stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'blame-vs-chain.svg'), W, H, *p)


fig_chain_ladder()
fig_switch_root()
fig_trust_chain()
fig_chain_eras()
fig_initramfs_layout()
fig_blame_vs_chain()
print("ok")
