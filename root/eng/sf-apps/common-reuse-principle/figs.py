# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Податок за зайве: зміна в C б'є по споживачеві класу A ──────────────────
def fig_release_tax():
    W, H = 1020, 560
    frags = []
    frags.append(text(W / 2, 36, "Податок за зайве в компоненті", size=17, bold=True))

    # Пакет-контейнер із трьома класами
    cx0, cy0, cw, ch = 560, 96, 320, 300
    frags.append(rect(cx0, cy0, cw, ch, fill="#fbfcfd", stroke=LINE, sw=1.8))
    frags.append(text(cx0 + cw / 2, cy0 + 30, "пакет toolkit  ·  одна версія 2.4.0",
                      size=12.5, bold=True, color=MUTED))
    ax, aw, ah = cx0 + 46, 228, 54
    frags.append(fitbox(ax, cy0 + 52, aw, ah, "клас A   (strings)", size=13, bold=True,
                        fill="#f2faf5", stroke=FIELD, sw=2.2))
    frags.append(fitbox(ax, cy0 + 120, aw, ah, "клас B   (http)", size=13, bold=True,
                        fill=FILL, stroke=MUTED, sw=1.6, color=MUTED))
    frags.append(fitbox(ax, cy0 + 188, aw, ah, "клас C   (crypto)", size=13, bold=True,
                        fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(plus(cx0 + cw - 26, cy0 + 188 + ah / 2, r=13))
    frags.append(text(cx0 + cw - 26, cy0 + 188 + ah + 20, "зміна тут", size=11.5,
                      color=POS, bold=True))

    # Споживач зліва
    frags.append(fitbox(70, 200, 200, 88, "Споживач\nвикликає лише\nклас A", size=13,
                        bold=True, fill="#eaf0fd", stroke=NEG, sw=2.0))

    # залежить від УСЬОГО пакета
    frags.append(arrow(272, 244, cx0 - 4, 244, color=INK, sw=2.0))
    frags.append(text((272 + cx0) / 2, 230, "залежить від УСЬОГО пакета",
                      size=12.5, bold=True))

    # новий випуск (внизу під пакетом)
    frags.append(fitbox(cx0 + 30, cy0 + ch + 18, 260, 46,
                        "новий випуск: 2.4.0 → 2.4.1", size=12.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(arrow(cx0 + 120, cy0 + ch + 16, cx0 + 130, cy0 + ch - 4,
                       color=POS, sw=2.0))

    # наслідок для споживача (червоний зворотний шлях)
    frags.append(fitbox(60, 320, 220, 96,
                        "мусить переоновитись,\nперетестуватись,\nперерозгорнутись",
                        size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=2.0))
    frags.append(arrow(cx0 + 28, cy0 + ch + 40, 284, 368, color=POS, sw=2.2))

    frags.append(fitbox(70, H - 54, W - 140, 36,
                        "Зміна в C, до якого споживач ніколи не торкається, все одно "
                        "штовхає його на повне коло переоновлення — бо версія в пакета одна на всіх.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'release-tax.svg'), W, H, *frags)


# ── 2. Поділ за реальним ужитком: до / після ─────────────────────────────────
def fig_split_by_reuse():
    W, H = 1100, 560
    frags = []
    frags.append(text(300, 40, "Було: одне звалище — усі зчеплені", size=15,
                      bold=True, color=POS))
    frags.append(text(812, 40, "Стало: поділ за ужитком", size=15, bold=True, color=FIELD))
    frags.append(line(W / 2, 62, W / 2, H - 66, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: фатальний пакет, два споживачі, обидва зчеплені ──
    fat_x, fat_y, fat_w, fat_h = 200, 210, 250, 150
    frags.append(rect(fat_x, fat_y, fat_w, fat_h, fill="#fbfcfd", stroke=POS, sw=2.0))
    frags.append(text(fat_x + fat_w / 2, fat_y + 26, "пакет toolkit", size=12.5,
                      bold=True, color=POS))
    for k, lab in enumerate(("strings", "http", "crypto")):
        red = lab == "crypto"
        frags.append(fitbox(fat_x + 30, fat_y + 42 + k * 34, fat_w - 60, 28, lab,
                            size=12, bold=True,
                            fill="#fdecea" if red else FILL,
                            stroke=POS if red else MUTED, sw=1.8 if red else 1.4,
                            color=INK if red else MUTED))
    frags.append(plus(fat_x + fat_w - 20, fat_y + 42 + 2 * 34 + 14, r=11))

    frags.append(fitbox(60, 110, 150, 58, "App-A\nхоче strings", size=12.5, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(fitbox(60, 402, 150, 58, "App-B\nхоче crypto", size=12.5, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(arrow(212, 148, fat_x + 40, fat_y - 4, color=INK, sw=1.8))
    frags.append(arrow(212, 422, fat_x + 40, fat_y + fat_h + 4, color=INK, sw=1.8))
    frags.append(fitbox(70, 300, 260, 44,
                        "зміна в crypto → перезбирається\nй App-A, що crypto не вживає",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.6))

    # ── ПРАВА: три окремі компоненти, чисті 1:1 залежності ──
    rx = 720
    comps = [("strings", 96, FIELD), ("http", 236, MUTED), ("crypto", 376, FIELD)]
    for lab, cy, col in comps:
        frags.append(fitbox(rx, cy, 150, 60, lab, size=13, bold=True,
                            fill="#f2faf5" if col is FIELD else FILL, stroke=col,
                            sw=2.0 if col is FIELD else 1.5,
                            color=INK if col is FIELD else MUTED))
    frags.append(plus(rx + 150 - 16, 376 + 30, r=11))
    frags.append(fitbox(940, 96, 150, 60, "App-A", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(fitbox(940, 376, 150, 60, "App-B", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(arrow(rx + 150 + 4, 126, 936, 126, color=FIELD, sw=2.0))
    frags.append(arrow(rx + 150 + 4, 406, 936, 406, color=FIELD, sw=2.0))
    frags.append(text(rx + 75, 452, "http нікому тут не потрібен — не тягнуть",
                      size=11, color=MUTED))
    frags.append(fitbox(rx - 30, 300, 260, 44,
                        "зміна в crypto нікого\nстороннього не торкається",
                        size=11.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    frags.append(fitbox(70, H - 52, W - 140, 36,
                        "CRP: разом тримай лише те, що справді вживають разом; решту "
                        "винось — тоді чужий випуск не тягне на перезбирання того, кому він ні до чого.",
                        size=12.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'split-by-reuse.svg'), W, H, *frags)


# ── 3. Той самий принцип на двох масштабах: ISP та CRP ────────────────────────
def fig_isp_fractal():
    W, H = 1040, 620
    frags = []
    frags.append(text(W / 2, 36, "Один принцип — два масштаби", size=17, bold=True))
    frags.append(line(W / 2, 60, W / 2, H - 130, color="#d0d5db", sw=1.2, dash="5,5"))

    def panel(gx, head, unit_lab, thing_lab, slots, client_lab, tail):
        out = [text(gx + 210, 82, head, size=15, bold=True, color=NEG)]
        # «товста» річ зі списком клітин
        bx, by, bw = gx + 130, 108, 240
        bh = 40 + len(slots) * 34
        out.append(rect(bx, by, bw, bh, fill="#fbfcfd", stroke=LINE, sw=1.8))
        out.append(text(bx + bw / 2, by + 24, thing_lab, size=12.5, bold=True, color=MUTED))
        for k, (name, used) in enumerate(slots):
            out.append(fitbox(bx + 24, by + 34 + k * 34, bw - 48, 28, name, size=11.5,
                              bold=True,
                              fill="#f2faf5" if used else FILL,
                              stroke=FIELD if used else MUTED,
                              sw=2.0 if used else 1.3,
                              color=INK if used else MUTED))
        # клієнт унизу
        cy = by + bh + 60
        out.append(fitbox(gx + 130, cy, 240, 52, client_lab, size=12.5, bold=True,
                          fill="#eaf0fd", stroke=NEG, sw=1.8))
        out.append(arrow(gx + 250, cy - 2, gx + 250, by + bh + 4, color=INK, sw=1.8))
        out.append(text(gx + 250, cy + 78, unit_lab, size=12, color=MUTED, italic=True))
        out.append(fitbox(gx + 60, cy + 96, 380, 40, tail, size=12, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.6))
        return out

    frags += panel(0, "ISP — масштаб КЛАСУ", "одиниця: метод у класі",
                   "інтерфейс Repo",
                   [("save()", True), ("findById()", True), ("bulkImport()", False),
                    ("reindex()", False), ("vacuum()", False)],
                   "клієнт кличе 2 методи з 5",
                   "залежить і від 3 методів,\nяких ніколи не кличе")
    frags += panel(520, "CRP — масштаб КОМПОНЕНТА", "одиниця: клас у компоненті",
                   "компонент toolkit",
                   [("strings", True), ("dates", True), ("http", False),
                    ("crypto", False), ("images", False)],
                   "споживач вживає 2 класи з 5",
                   "залежить і від 3 класів,\nяких ніколи не вживає")

    frags.append(fitbox(90, H - 70, W - 180, 48,
                        "Той самий хід на обох масштабах: не залеж від зайвого — "
                        "ріж «товсте» за реальним ужитком (метод у класі ⟶ клас у компоненті).",
                        size=13, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, 'isp-fractal.svg'), W, H, *frags)


# ── 4. Транзитивне дерево споживача: до / після поділу (для proj-вставки) ──────
def fig_deptree_split():
    W, H = 1080, 560
    frags = []
    frags.append(text(W / 2, 34, "Транзитивне дерево споживача: до і після поділу",
                      size=17, bold=True))
    frags.append(text(275, 72, "До поділу", size=15, bold=True, color=POS))
    frags.append(text(812, 72, "Після поділу", size=15, bold=True, color=FIELD))
    frags.append(line(W / 2, 88, W / 2, H - 74, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: app → toolkit → {undici, node-forge} ──
    frags.append(fitbox(200, 108, 150, 46, "app", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(fitbox(190, 216, 170, 46, "toolkit@2.4.0", size=13, bold=True,
                        fill=FILL, stroke=LINE, sw=1.7))
    frags.append(fitbox(96, 336, 150, 44, "undici", size=12.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.7))
    frags.append(fitbox(300, 336, 160, 44, "node-forge", size=12.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.7))
    frags.append(arrow(275, 156, 275, 214, color=INK, sw=1.8))
    frags.append(arrow(252, 264, 172, 334, color=INK, sw=1.6))
    frags.append(arrow(298, 264, 380, 334, color=INK, sw=1.6))
    frags.append(fitbox(66, 410, 408, 44,
                        "увесь підтин у node_modules —\nхоч жоден рядок для padLeft його не кличе",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.5))

    # ── ПРАВА: app → @toolkit/strings; примарні листки ──
    frags.append(fitbox(740, 108, 150, 46, "app", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(fitbox(716, 216, 198, 46, "@toolkit/strings", size=12.5, bold=True,
                        fill="#f2faf5", stroke=FIELD, sw=2.0))
    frags.append(text(815, 292, "0 залежностей", size=11.5, color=FIELD, bold=True))
    frags.append(arrow(815, 156, 815, 214, color=FIELD, sw=1.9))
    frags.append(text(812, 320, "більше не в дереві:", size=11, color=POS))
    for gx, gw, lab in ((700, 150, "undici"), (884, 158, "node-forge")):
        frags.append(rect(gx, 336, gw, 44, fill="#f7f8fa", stroke="#c7ccd3",
                          sw=1.2, rx=6))
        frags.append(text(gx + gw / 2, 363, lab, size=12, color="#aab0b8"))
    frags.append(fitbox(690, 410, 388, 44,
                        "важкі листки зникли з дерева —\nразом зі своєю вагою й поверхнею для атак",
                        size=11.5, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.5))

    frags.append(fitbox(70, H - 54, W - 140, 36,
                        "Пакет — одиниця встановлення: залежиш від toolkit → несеш увесь "
                        "його підтин. Поділ лишає в дереві рівно те, що вживаєш.",
                        size=12, bold=True, fill="#f2faf5", stroke=FIELD, sw=1.5))
    render(os.path.join(IMG, 'deptree-split.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_release_tax()
    fig_split_by_reuse()
    fig_isp_fractal()
    fig_deptree_split()
    print("ok: release-tax, split-by-reuse, isp-fractal, deptree-split")
