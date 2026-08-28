# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. pipeline-stages: 6 етапів наскрізного випуску з бар'єрами ─────────────
def fig_pipeline_stages():
    W, H = 960, 480
    p = []

    stages = [
        ("1. Тригер і версія", "git tag -s v2.4.0\nперевірка підпису тегу\nсемантичний парсинг", "#eef4fb", NEG),
        ("2. Герметична збірка", "SOURCE_DATE_EPOCH\nкрос-матриця плати\nворота Flash / RAM", "#fdf6ed", "#b86200"),
        ("3. Піраміда тестів", "Unit (хост, симуляція)\nЕмуляція чипа (QEMU)\nДим на залізі (HIL)", "#eef7ee", FIELD),
        ("4. Ізольований підпис", "Геш SHA-256 -> HSM\nECDSA / Ed25519\nВшивання заголовка", "#fdf0ed", POS),
        ("5. Генерація SBOM", "CycloneDX / SPDX\nОблік бібліотек і HAL\nАтестація SLSA", "#f6eefb", "#7b2cbf"),
        ("6. Атомний реліз", "Маніфест + метадані\nПакет оновлення\nПублікація в сховище", "#eef9f9", "#007788"),
    ]

    # Розташуємо у два ряди по 3 блоки
    bw, bh = 260, 140
    xs = [50, 350, 650]
    y_row1 = 90
    y_row2 = 280

    for i, (title, details, fill_c, stroke_c) in enumerate(stages):
        if i < 3:
            x = xs[i]
            y = y_row1
        else:
            x = xs[5 - i]
            y = y_row2

        p.append(rect(x, y, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=8))
        p.append(text(x + bw / 2, y + 26, title, size=13, color=stroke_c, bold=True))
        p.append(line(x + 12, y + 36, x + bw - 12, y + 36, color=stroke_c, sw=1))
        p.append(mtext(x + bw / 2, y + 58, details, size=11, color=INK, lh=1.3))

    # Стрілки між етапами верхнього ряду
    p.append(arrow(xs[0] + bw + 4, y_row1 + bh / 2, xs[1] - 6, y_row1 + bh / 2, color=LINE, sw=2))
    p.append(arrow(xs[1] + bw + 4, y_row1 + bh / 2, xs[2] - 6, y_row1 + bh / 2, color=LINE, sw=2))

    # Перехід з верхнього ряду в нижній (з 3-го етапу в 4-й)
    p.append(arrow(xs[2] + bw / 2, y_row1 + bh + 4, xs[2] + bw / 2, y_row2 - 6, color=LINE, sw=2))

    # Стрілки між етапами нижнього ряду (справа наліво: 4 -> 5 -> 6)
    p.append(arrow(xs[2] - 4, y_row2 + bh / 2, xs[1] + bw + 6, y_row2 + bh / 2, color=LINE, sw=2))
    p.append(arrow(xs[1] - 4, y_row2 + bh / 2, xs[0] + bw + 6, y_row2 + bh / 2, color=LINE, sw=2))

    # Підписи воріт (gates)
    p.append(text(xs[0] + bw + 20, y_row1 + bh / 2 - 12, "G1", size=10, color=MUTED, bold=True))
    p.append(text(xs[1] + bw + 20, y_row1 + bh / 2 - 12, "G2", size=10, color=MUTED, bold=True))
    p.append(text(xs[2] + bw / 2 + 16, y_row1 + bh + 25, "G3", size=10, color=MUTED, bold=True))
    p.append(text(xs[2] - 20, y_row2 + bh / 2 - 12, "G4", size=10, color=MUTED, bold=True))
    p.append(text(xs[1] - 20, y_row2 + bh / 2 - 12, "G5", size=10, color=MUTED, bold=True))

    p.append(text(W / 2, H - 20, "Провал будь-яких воріт (G1–G5) негайно блокує конвеєр і скасовує публікацію",
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "pipeline-stages.svg"), W, H, *p,
           title="Шість фаз наскрізного конвеєра: від тегу до сховища релізів")


# ── 2. release-bundle: Анатомія криптографічного пакета випуску ───────────────
def fig_release_bundle():
    W, H = 940, 500
    p = []

    # Контейнер усього бандла
    bx, by, bw, bh = 40, 60, 860, 410
    p.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=LINE, sw=2, rx=10))
    p.append(text(bx + 20, by + 26, "Пакет релізу: release-v2.4.0-bundle.tar.gz (або підписаний OTA-контейнер)",
                  size=13, color=INK, bold=True, anchor="start"))

    # Лівий блок: Двійковий образ із заголовком Secure Boot
    ix, iy, iw, ih = 70, 105, 340, 345
    p.append(rect(ix, iy, iw, ih, fill="#ffffff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(ix + iw / 2, iy + 24, "Двійковий образ (firmware.bin)", size=12, color=NEG, bold=True))

    # Секції всередині бінарника
    sections = [
        ("Заголовок Secure Boot (128 B)", "Magic 0x53424F54, версія v2.4.0,\nanti-rollback counter, прапорці", "#eaf0fd", 62),
        ("Таблиця векторів переривань (1 KB)", "Початковий SP, Reset_Handler, ISR", "#f4f6f8", 48),
        ("Тіло прошивки (.text, .rodata, .data)", "Машинний код застосунку Cortex-M,\nконстанти, ініціалізовані змінні", "#f9fbfd", 80),
        ("Криптографічний підпис (64 B)", "ECDSA (secp256r1) / Ed25519\nпідпис гешу образу завантажувачем", "#fdecea", 54),
    ]

    cur_y = iy + 36
    for stitle, sdesc, sfill, sh in sections:
        p.append(rect(ix + 10, cur_y, iw - 20, sh, fill=sfill, stroke=MUTED, sw=1, rx=4))
        p.append(text(ix + 18, cur_y + 16, stitle, size=10, color=INK, bold=True, anchor="start"))
        p.append(mtext(ix + 18, cur_y + 30, sdesc, size=9, color=MUTED, anchor="start", lh=1.2))
        cur_y += sh + 8

    # Правий верхній блок: Криптографічний маніфест
    mx, my, mw, mh = 450, 105, 420, 160
    p.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(mx + mw / 2, my + 22, "Криптографічний маніфест (manifest.json)", size=12, color=FIELD, bold=True))
    manifest_info = (
        "• product_id, target_hw: [\"rev_B\", \"rev_C\"]\n"
        "• version: 2.4.0, min_secure_version: 3 (anti-rollback)\n"
        "• sha256_digest: a7f8c9... (хеш двійкового образу)\n"
        "• signature: base64 (підпис маніфесту ключем релізу)"
    )
    p.append(mtext(mx + 18, my + 48, manifest_info, size=10, color=INK, anchor="start", lh=1.35))

    # Правий нижній блок: SBOM та SLSA атестація
    sx, sy, sw, sh = 450, 285, 420, 165
    p.append(rect(sx, sy, sw, sh, fill="#ffffff", stroke="#7b2cbf", sw=1.8, rx=6))
    p.append(text(sx + sw / 2, sy + 22, "SBOM (CycloneDX) та SLSA атестація", size=12, color="#7b2cbf", bold=True))
    sbom_info = (
        "• Перелік компонентів (FreeRTOS v10.5.1, mbedTLS v3.4.0)\n"
        "• Хеш закріпленого тулчейну (arm-none-eabi-gcc 13.2.rel1)\n"
        "• SLSA Provenance: посилання на коміт, конвеєр і раннер"
    )
    p.append(mtext(sx + 18, sy + 48, sbom_info, size=10, color=INK, anchor="start", lh=1.35))

    render(os.path.join(OUT, "release-bundle.svg"), W, H, *p,
           title="Анатомія пакета випуску: образ, криптографічний маніфест і SBOM")


# ── 3. signing-isolation: Межа довіри та ізоляція ключа підпису ──────────────
def fig_signing_isolation():
    W, H = 940, 440
    p = []

    # Ліва зона: Недовірене середовище раннера CI
    lx, ly, lw, lh = 50, 70, 360, 330
    p.append(rect(lx, ly, lw, lh, fill="#fdfbf7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(lx + lw / 2, ly + 26, "Недовірена зона: CI Runner", size=13, color="#d97706", bold=True))
    p.append(mtext(lx + lw / 2, ly + 52,
                   "• Збирає артефакти з git-коду\n"
                   "• Має доступ до публічних ключів\n"
                   "• НЕ МІСТИТЬ приватного ключа\n"
                   "• Рахує лише SHA-256 хеш образу",
                   size=11, color=INK, lh=1.4))

    p.append(rect(lx + 30, ly + 150, lw - 60, 60, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(lx + lw / 2, ly + 172, "Зібраний binary.bin", size=11, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 192, "SHA-256: d41d8cd98f00b204...", size=9.5, color=MUTED))

    p.append(rect(lx + 30, ly + 230, lw - 60, 50, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(lx + lw / 2, ly + 252, "Запит на підпис (OIDC токен)", size=10.5, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 268, "Payload: { digest, tag, commit }", size=9.5, color=MUTED))

    # Права зона: Довірений модуль безпеки (HSM / KMS)
    rx, ry, rw, rh = 530, 70, 360, 330
    p.append(rect(rx, ry, rw, rh, fill="#eef7ee", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(rx + rw / 2, ry + 26, "Довірена зона: HSM / KMS / Cosign", size=13, color=FIELD, bold=True))
    p.append(mtext(rx + rw / 2, ry + 52,
                   "• Приватний ключ у крипточипі\n"
                   "• Ключ ніколи не експортується\n"
                   "• Перевірка прав (OIDC/RBAC)\n"
                   "• Підпис накладається на хеш",
                   size=11, color=INK, lh=1.4))

    p.append(rect(rx + 30, ry + 150, rw - 60, 60, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(rx + rw / 2, ry + 172, "Приватний ключ (Ed25519 / RSA)", size=11, color=POS, bold=True))
    p.append(text(rx + rw / 2, ry + 192, "Захищений апаратний анклав", size=9.5, color=MUTED))

    p.append(rect(rx + 30, ry + 230, rw - 60, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(rx + rw / 2, ry + 252, "Цифровий підпис (Signature)", size=10.5, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 268, "Повертається 64-байтний підпис", size=9.5, color=MUTED))

    # Межа довіри посередині
    mid_x = (lx + lw + rx) / 2
    p.append(line(mid_x, ly + 10, mid_x, ly + lh - 10, color=POS, sw=1.5, dash="5,4"))
    p.append(text(mid_x, ly + 20, "МЕЖА ДОВІРИ", size=9, color=POS, bold=True))

    # Стрілки обміну
    p.append(arrow(lx + lw - 10, ly + 255, rx + 10, ly + 255, color=LINE, sw=1.8))
    p.append(text(mid_x, ly + 245, "1. Лише хеш + OIDC →", size=9.5, color=MUTED))

    p.append(arrow(rx + 10, ly + 295, lx + lw - 10, ly + 295, color=FIELD, sw=1.8))
    p.append(text(mid_x, ly + 310, "← 2. Підпис (без ключа)", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "signing-isolation.svg"), W, H, *p,
           title="Ізоляція ключів підпису: раннер передає хеш, HSM повертає підпис")


if __name__ == "__main__":
    fig_pipeline_stages()
    fig_release_bundle()
    fig_signing_isolation()
    print("OK: figures generated ->", OUT)
