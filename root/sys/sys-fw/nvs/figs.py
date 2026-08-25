# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── keyvalue: NVS як словник «ключ → значення» на Flash ───────────────────────
# Ідея: звертаєшся до даних на ІМ'Я (ключ), а не за адресою; значення бувають
# трьох родів — ціле, рядок, blob. Усе живе в розділі nvs у Flash.

def fig_keyvalue():
    W, H = 720, 330
    p = []
    # рамка розділу
    bx, by, bw, bh = 120, 70, 480, 232
    p.append(rect(bx, by, bw, bh, fill="#fbfbff", stroke=INK, sw=1.8, rx=12))
    p.append(text(bx + bw / 2, by + 24, "розділ  nvs  (у Flash)", size=11, color=MUTED, bold=True))

    rows = [
        ("wifi_ssid", '"Home_5G"', "рядок", "#eafaf0", FIELD),
        ("boot_count", "42", "ціле", "#eaf0fd", NEG),
        ("volume", "7", "ціле", "#eaf0fd", NEG),
        ("calib", "⟨13 байтів⟩", "blob", "#fdf6e3", "#b8860b"),
    ]
    y = by + 64
    for key, val, kind, fill, col in rows:
        p.append(text(bx + 36, y + 5, key, size=13, color=INK, anchor="start", bold=True))
        p.append(arrow(bx + 196, y, bx + 256, y, color=MUTED, sw=1.7))
        vb, vw, vh = textbox(bx + 256 + 95, y, val, size=13, bold=True,
                             color=col, fill=fill, stroke=col, sw=1.6, min_w=190, pad=8)
        p.append(vb)
        p.append(text(bx + 256 + 200, y + 4, kind, size=10, color=MUTED, anchor="start"))
        y += 50

    p.append(text(W / 2, H - 16,
                  "звертаєшся на ім'я (ключ), а не за адресою; значення — число, рядок або «сирі» байти",
                  size=11, color=INK))
    render(os.path.join(OUT, "keyvalue.svg"), W, H, *p,
           title="NVS — словник «ключ → значення» на Flash")


# ── namespace: простори імен розводять однойменні ключі ───────────────────────
# Ідея: ключ retries у просторі wifi і retries у просторі app — різні дані,
# бо повне ім'я це простір + ключ.

def fig_namespace():
    W, H = 720, 300
    p = []
    boxes = [
        (60, "wifi", FIELD, "#eafaf0", [("retries", "3"), ("ssid", '"Home"')]),
        (390, "app", NEG, "#eaf0fd", [("retries", "5"), ("volume", "7")]),
    ]
    bw, bh = 270, 170
    by = 80
    for bx, ns, col, fill, items in boxes:
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(bx + bw / 2, by + 26, 'простір "%s"' % ns, size=13, color=col, bold=True))
        yy = by + 64
        for k, v in items:
            p.append(text(bx + 30, yy, k, size=13, color=INK, anchor="start", bold=True))
            p.append(text(bx + 150, yy, "→", size=13, color=MUTED, anchor="middle"))
            p.append(text(bx + 180, yy, v, size=13, color=INK, anchor="start"))
            yy += 40

    # підкреслити однойменний ключ
    p.append(text(W / 2, 268, 'wifi/retries ≠ app/retries — повне ім\'я це простір + ключ',
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "namespace.svg"), W, H, *p,
           title="Простори імен розводять однойменні ключі")


# ── value-types: три роди значень ────────────────────────────────────────────
# Ідея: ціле, рядок, blob — трьох досить майже на будь-яку настройку.

def fig_value_types():
    W, H = 720, 250
    p = []
    cards = [
        ("ціле", "uint8…int64", "лічильники,\nгучність, режим", NEG, "#eaf0fd"),
        ("рядок", "текст", "імена мереж,\nпаролі, адреси", FIELD, "#eafaf0"),
        ("blob", "«сирі» байти", "структура,\nкалібрування, ключ", "#b8860b", "#fdf6e3"),
    ]
    cw, ch = 200, 130
    gap = (W - 3 * cw) / 4
    y = 80
    for i, (name, sub, body, col, fill) in enumerate(cards):
        x = gap + i * (cw + gap)
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x + cw / 2, y + 32, name, size=16, color=col, bold=True))
        p.append(text(x + cw / 2, y + 54, sub, size=11, color=MUTED, italic=True))
        p.append(mtext(x + cw / 2, y + 84, body, size=12, color=INK))
    p.append(text(W / 2, H - 18, "трьох цих родів досить майже на будь-яку настройку пристрою",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "value-types.svg"), W, H, *p,
           title="Три роди значень у NVS")


# ── cycle: обряд роботи open → get/set → commit → close ───────────────────────
# Ідея: до commit зміни живуть лише в RAM; commit торкається Flash.

def fig_cycle():
    W, H = 760, 250
    p = []
    y = 120
    bw, bh = 120, 56
    steps = [
        ("open\nпростір", FILL, INK),
        ("get / set\nключі", "#eaf0fd", INK),
        ("commit\n→ Flash", "#eafaf0", FIELD),
        ("close", FILL, INK),
    ]
    gap = (W - 4 * bw) / 5
    centers = []
    for i, (lab, fill, col) in enumerate(steps):
        x = gap + i * (bw + gap)
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=12, fill=fill, stroke=col, sw=1.7, bold=True, color=col))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 4, y, x - 4, y, color=INK, sw=1.8))

    # дужка «до commit — лише RAM»
    p.append(text(centers[1][0], y + 64, "до commit зміни лише в RAM — забув його, після перезавантаження побачиш старе",
                  size=11, color=POS, anchor="start", italic=True))
    render(os.path.join(OUT, "cycle.svg"), W, H, *p,
           title="Обряд роботи з NVS")


# ── append: оновлення дописуванням, а не переписуванням ───────────────────────
# Ідея: новий запис лягає в кінець, старий лише позначається застарілим (✗);
# збій під час запису не псує попереднього значення.

def fig_append():
    W, H = 720, 300
    p = []
    # сторінка-смуга з комірок
    sx, sy, cw, ch = 70, 120, 96, 60
    cells = [
        ("volume=5", "00", True),    # застаріле
        ("ssid=Home", "10", False),  # чинне
        ("volume=7", "10", False),   # чинне (нове)
        ("", "11", None),            # порожнє
        ("", "11", None),
    ]
    for i, (lab, st, stale) in enumerate(cells):
        x = sx + i * cw
        if stale is None:
            fill, stroke = "#f7f7f7", "#cccccc"
        elif stale:
            fill, stroke = "#fdecea", POS
        else:
            fill, stroke = "#eafaf0", FIELD
        p.append(rect(x, sy, cw - 8, ch, fill=fill, stroke=stroke, sw=1.7, rx=6))
        if lab:
            p.append(text(x + (cw - 8) / 2, sy + 28, lab, size=11, color=INK, bold=True))
            mark = "✗ застаріле" if stale else "✓ чинне"
            mc = POS if stale else FIELD
            p.append(text(x + (cw - 8) / 2, sy + 46, mark, size=9, color=mc))
        else:
            p.append(text(x + (cw - 8) / 2, sy + 34, "порожньо", size=9, color=MUTED))

    p.append(text(sx, sy - 16, "сторінка nvs →", size=11, color=MUTED, anchor="start", bold=True))

    # стрілка: старий volume → новий volume (дописано далі)
    ax1 = sx + 0 * cw + (cw - 8) / 2
    ax2 = sx + 2 * cw + (cw - 8) / 2
    p.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="5 4" marker-end="url(#arrow)"/>'
             % (ax1, sy - 4, (ax1 + ax2) / 2, sy - 48, ax2, sy - 4, INK))
    p.append(text((ax1 + ax2) / 2, sy - 52, "оновлення volume — новий запис, старий лише гасне",
                  size=11, color=INK))

    p.append(text(W / 2, H - 18,
                  "нове пишемо поряд, старе не чіпаємо — збій посеред запису не псує попереднього значення",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "append.svg"), W, H, *p,
           title="Оновлення — дописуванням, а не переписуванням")


# ── nvs-vs-fs: NVS проти файлової системи ─────────────────────────────────────
# Ідея: маленьке й «налаштування» → NVS; велике й «файл» → файлова система.

def fig_nvs_vs_fs():
    W, H = 720, 270
    p = []
    cards = [
        (60, "NVS", FIELD, "#eafaf0",
         ["дрібні іменовані", "налаштування", "", "байти — сотні байтів", "десятки ключів"],
         "ssid, пароль, гучність,\nлічильники, калібрування"),
        (390, "файлова система", NEG, "#eaf0fd",
         ["великі дані,", "схожі на файли", "", "кілобайти — мегабайти", "багато даних"],
         "журнали, картинки,\nзвук, веб-сторінки"),
    ]
    bw, bh = 270, 150
    by = 70
    for bx, name, col, fill, lines, examples in cards:
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=2, rx=12))
        p.append(text(bx + bw / 2, by + 28, name, size=15, color=col, bold=True))
        p.append(mtext(bx + bw / 2, by + 56, "\n".join(lines), size=11, color=INK, lh=1.25))
        p.append(mtext(bx + bw / 2, by + bh + 24, examples, size=11, color=MUTED))
    p.append(text(W / 2, H - 16, "маленьке й «налаштування» → NVS;  велике й «файл» → файлова система",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "nvs-vs-fs.svg"), W, H, *p,
           title="NVS проти файлової системи")


# ── pages: розділ → сторінки (по сектору) → записи (вставка) ───────────────────
# Ідея: стан запису — 2 біти 11→10→00; кожен перехід лише ГАСИТЬ біт.

def fig_pages():
    W, H = 720, 320
    p = []
    # розділ із трьох сторінок
    px, py, pw, ph = 60, 70, 600, 96
    p.append(text(px, py - 14, "розділ nvs (≥ 3 сторінки = 3 сектори по 4 КБ)", size=11, color=MUTED, anchor="start", bold=True))
    pages = ["сторінка\n(сектор)", "сторінка\n(сектор)", "сторінка\n(сектор)"]
    gap = 16
    each = (pw - 2 * gap) / 3
    for i, lab in enumerate(pages):
        x = px + i * (each + gap)
        p.append(fitbox(x, py, each, ph, lab, size=12, fill="#fbfbff", stroke=INK, sw=1.7, bold=True))

    # збільшена одна сторінка → записи
    p.append(line(px + each / 2, py + ph, 130, 210, color=MUTED, sw=1.2, dash="4 4"))
    p.append(line(px + each / 2 + each + gap, py + ph, 600, 210, color=MUTED, sw=1.2, dash="4 4"))

    ex, ey, ecw, ech = 110, 210, 100, 50
    recs = [("запис", "10"), ("запис", "10"), ("запис", "00"), ("запис", "11"), ("запис", "11")]
    for i, (lab, st) in enumerate(recs):
        x = ex + i * (ecw + 6)
        col = {"11": MUTED, "10": FIELD, "00": POS}[st]
        fill = {"11": "#f7f7f7", "10": "#eafaf0", "00": "#fdecea"}[st]
        p.append(rect(x, ey, ecw, ech, fill=fill, stroke=col, sw=1.6, rx=6))
        p.append(text(x + ecw / 2, ey + 24, lab, size=11, color=INK, bold=True))
        p.append(text(x + ecw / 2, ey + 40, st, size=11, color=col, bold=True))

    p.append(text(W / 2, H - 26, "стан запису — 2 біти:  11 порожньо  →  10 записано  →  00 застаріло",
                  size=12, color=INK, bold=True))
    p.append(text(W / 2, H - 8, "кожен перехід лише ГАСИТЬ біт (1→0) — а це Flash уміє без стирання",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pages.svg"), W, H, *p,
           title="Розділ → сторінки → записи")


# ── gc: збирання сміття переносить чинні записи, стару сторінку стирає ─────────
# Ідея: повна сторінка з багатьма «застарілими» → живі переїжджають на чисту,
# стару стирають цілком; знос розмазується.

def fig_gc():
    W, H = 720, 290
    p = []
    bw, bh = 200, 150
    yb = 80
    # ліва: повна сторінка
    lx = 70
    p.append(rect(lx, yb, bw, bh, fill="#fff8f6", stroke=POS, sw=1.8, rx=10))
    p.append(text(lx + bw / 2, yb + 24, "повна сторінка", size=12, color=POS, bold=True))
    states = ["00", "10", "00", "00", "10", "00"]
    for i, st in enumerate(states):
        cx = lx + 40 + (i % 3) * 62
        cy = yb + 58 + (i // 3) * 44
        col = FIELD if st == "10" else POS
        fill = "#eafaf0" if st == "10" else "#fdecea"
        p.append(rect(cx - 26, cy - 16, 52, 32, fill=fill, stroke=col, sw=1.4, rx=4))
        p.append(text(cx, cy + 5, st, size=11, color=col, bold=True))
    p.append(text(lx + bw / 2, yb + bh + 20, "багато «застарілих» (00)", size=10, color=MUTED, italic=True))

    # стрілка
    mx = lx + bw + 50
    p.append(arrow(lx + bw + 8, yb + bh / 2, mx + 38, yb + bh / 2, color=INK, sw=2))
    p.append(text(mx + 23, yb + bh / 2 - 12, "перенести\nчинні", size=10, color=INK))

    # права: чиста сторінка з лише чинними
    rx = mx + 50
    p.append(rect(rx, yb, bw, bh, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(rx + bw / 2, yb + 24, "чиста сторінка", size=12, color=FIELD, bold=True))
    for i in range(2):
        cx = rx + 70 + i * 62
        cy = yb + 70
        p.append(rect(cx - 26, cy - 16, 52, 32, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=4))
        p.append(text(cx, cy + 5, "10", size=11, color=FIELD, bold=True))
    p.append(text(rx + bw / 2, yb + bh + 20, "лише чинні (10)", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 14, "стару сторінку стирають цілком — місце повертається, а знос розмазується",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "gc.svg"), W, H, *p,
           title="Збирання сміття: переїзд чинних, стирання старої")


if __name__ == "__main__":
    fig_keyvalue()
    fig_namespace()
    fig_value_types()
    fig_cycle()
    fig_append()
    fig_nvs_vs_fs()
    fig_pages()
    fig_gc()
    print("OK: figures written to", OUT)
