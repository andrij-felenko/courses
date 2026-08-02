# -*- coding: utf-8 -*-
"""Фігури до теми «Пакування бінарного протоколу: вирівнювання й порядок байтів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
BLUE_BG  = "#eaf0fd"
GREEN_BG = "#eaf6ee"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
PAD_BG   = "#e4e7ea"
CELL_BG  = "#f3f5f8"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def span_row(f, x0, y, bw, h, spans, tick_color="#c7ccd1"):
    """Намалювати стрічку байтів як послідовність іменованих ділянок.
    spans: список (кількість_байтів, підпис, колір_рамки, заливка)."""
    x = x0
    off = 0
    for n, label, col, bg in spans:
        w = n * bw
        f.append(rect(x, y, w, h, fill=bg, stroke=col, sw=2, rx=5))
        for k in range(1, n):
            # позначки байтів — короткі, лише при краях, щоб не перетинати напис
            f.append(line(x + k * bw, y + 3, x + k * bw, y + 10, color=tick_color, sw=1))
            f.append(line(x + k * bw, y + h - 10, x + k * bw, y + h - 3, color=tick_color, sw=1))
        f.append(fitbox(x + 3, y + 6, w - 6, h - 12, label, size=13,
                        pad=5, fill="none", stroke="none", sw=0, color=col, bold=True))
        f.append(mono(x + 2, y - 9, str(off), size=11, color=MUTED, anchor="start"))
        x += w
        off += n
    f.append(mono(x + 2, y - 9, str(off), size=11, color=MUTED, anchor="start"))
    return x


# ── 1. Той самий текст структури — дві різні розкладки ────────────────────────
def fig_layout_drift():
    W, H = 1010, 500
    f = []
    x0, bw = 68, 36

    f.append(mono(x0, 62, "struct Sample { uint8_t id; double value; uint16_t flags; };",
                  size=14, color=INK, anchor="start", bold=True))

    # ── 64-бітна збірка ──
    f.append(text(x0, 96, "gcc -m64 · x86-64 SysV · double вирівнюється на 8 → sizeof == 24",
                  size=13, color=NEG, anchor="start", bold=True))
    span_row(f, x0, 126, bw, 48, [
        (1, "id", POS, RED_BG),
        (7, "падінг 7 байтів", MUTED, PAD_BG),
        (8, "value (double)", NEG, BLUE_BG),
        (2, "flags", FIELD, GREEN_BG),
        (6, "хвостовий падінг 6", MUTED, PAD_BG),
    ])
    f.append(text(x0, 200, "зсуви полів:  id = 0 · value = 8 · flags = 16",
                  size=12, color=MUTED, anchor="start"))

    # ── 32-бітна збірка ──
    f.append(text(x0, 254, "gcc -m32 · i386 SysV · double вирівнюється на 4 → sizeof == 16",
                  size=13, color=POS, anchor="start", bold=True))
    span_row(f, x0, 284, bw, 48, [
        (1, "id", POS, RED_BG),
        (3, "падінг 3", MUTED, PAD_BG),
        (8, "value (double)", NEG, BLUE_BG),
        (2, "flags", FIELD, GREEN_BG),
        (2, "падінг 2", MUTED, PAD_BG),
    ])
    f.append(text(x0, 358, "зсуви полів:  id = 0 · value = 4 · flags = 12",
                  size=12, color=MUTED, anchor="start"))

    # підсумок
    f.append(rect(x0 - 8, 386, W - 2 * x0 + 16, 86, fill=AMBER_BG, stroke=AMBER, sw=1.8, rx=12))
    f.append(text(W / 2, 412,
                  "Той самий вихідний текст, той самий процесор — лише інший режим збірки.",
                  size=13, color=INK, bold=True))
    f.append(text(W / 2, 436,
                  "send(fd, &s, sizeof s, 0) відправить 24 байти з одного боку і 16 з іншого,",
                  size=12, color=INK))
    f.append(text(W / 2, 458,
                  "а поле value читатиметься зі зсуву 8 замість 4. Розкладка — не властивість типу, а властивість збірки.",
                  size=12, color=INK))

    out("layout-drift.svg", W, H, *f,
        title="Один опис структури — дві несумісні розкладки")


# ── 2. Кодек зі зсувів не залежить від хоста ─────────────────────────────────
def fig_shift_codec():
    W, H = 1000, 560
    f = []
    bw = 62

    f.append(text(W / 2, 62, "у програмі є ЧИСЛО  v = 0x0A0B0C0D  (одне й те саме на обох машинах)",
                  size=13.5, color=INK, bold=True))

    def strip(x, y, bytes_, col, bg):
        for i, b in enumerate(bytes_):
            f.append(rect(x + i * bw, y, bw, 40, fill=bg, stroke=col, sw=2, rx=5))
            f.append(mono(x + i * bw + bw / 2, y + 27, b, size=14, color=col,
                          anchor="middle", bold=True))

    # ── шлях 1: копіювання пам'яті ──
    f.append(rect(40, 92, 445, 250, fill=RED_BG, stroke=POS, sw=2, rx=12))
    f.append(text(262, 118, "✗ memcpy(buf, &v, 4) — копіюємо ПАМ'ЯТЬ", size=13, color=POS, bold=True))
    f.append(text(262, 142, "у дріт іде те, як число лежить у цій машині", size=11.5, color=MUTED))

    f.append(text(80, 178, "хост little-endian:", size=12, color=INK, anchor="start", bold=True))
    strip(80, 190, ["0D", "0C", "0B", "0A"], POS, BG)

    f.append(text(80, 262, "хост big-endian:", size=12, color=INK, anchor="start", bold=True))
    strip(80, 274, ["0A", "0B", "0C", "0D"], POS, BG)

    f.append(text(262, 330, "два різні дроти — приймач не має шансу", size=12, color=POS, bold=True))

    # ── шлях 2: зсуви ──
    f.append(rect(515, 92, 445, 250, fill=GREEN_BG, stroke=FIELD, sw=2, rx=12))
    f.append(text(737, 118, "✓ b[0]=v>>24 … b[3]=v — беремо ЧИСЛО", size=13, color=FIELD, bold=True))
    f.append(text(737, 142, "зсув визначений над значенням, не над пам'яттю", size=11.5, color=MUTED))

    f.append(text(555, 178, "хост little-endian:", size=12, color=INK, anchor="start", bold=True))
    strip(555, 190, ["0A", "0B", "0C", "0D"], FIELD, BG)

    f.append(text(555, 262, "хост big-endian:", size=12, color=INK, anchor="start", bold=True))
    strip(555, 274, ["0A", "0B", "0C", "0D"], FIELD, BG)

    f.append(text(737, 330, "один і той самий дріт — без жодного #ifdef", size=12, color=FIELD, bold=True))

    # ── пояснення знизу ──
    f.append(rect(40, 366, W - 80, 92, fill=CELL_BG, stroke=INK, sw=1.6, rx=12))
    f.append(text(W / 2, 392, "Чому так: v >> 24 означає «поділи значення на 2²⁴», а не «візьми перший байт із пам'яті».",
                  size=12.5, color=INK, bold=True))
    f.append(text(W / 2, 416, "Обчислення над значенням дає ту саму відповідь на будь-якому процесорі,",
                  size=12, color=INK))
    f.append(text(W / 2, 438, "тому кодек зі зсувів не треба ні перевіряти на порядок байтів, ні перемикати за платформою.",
                  size=12, color=INK))

    f.append(rect(40, 476, W - 80, 60, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=12))
    f.append(text(W / 2, 500, "Дзеркально при читанні:  v = (b[0]<<24) | (b[1]<<16) | (b[2]<<8) | b[3]",
                  size=12.5, color=INK, bold=True))
    f.append(text(W / 2, 522, "— теж арифметика над значеннями, теж однакова всюди.",
                  size=11.5, color=MUTED))

    out("shift-codec.svg", W, H, *f,
        title="Копіювання пам'яті проти кодека зі зсувів")


# ── 3. Спроєктована розкладка пакета ─────────────────────────────────────────
def fig_packet_spec():
    W, H = 1040, 520
    f = []
    x0, bw = 48, 52

    f.append(text(W / 2, 62, "32 байти, кожен байт має ім'я, кожне поле стоїть на кратному своєму розміру зсуві",
                  size=13, color=INK, bold=True))

    # верхня половина: байти 0..15
    f.append(text(x0, 100, "байти 0…15", size=12, color=MUTED, anchor="start", bold=True))
    span_row(f, x0, 118, bw, 50, [
        (2, "magic", POS, RED_BG),
        (1, "ver", POS, RED_BG),
        (1, "flg", POS, RED_BG),
        (2, "len", NEG, BLUE_BG),
        (2, "rsv=0", MUTED, PAD_BG),
        (8, "time_us (uint64)", FIELD, GREEN_BG),
    ])
    f.append(text(x0, 196, "зсув 8 кратний 8 → 64-бітний час лягає рівно навіть при доступі на місці",
                  size=11.5, color=MUTED, anchor="start"))

    # нижня половина: байти 16..31
    f.append(text(x0, 240, "байти 16…31", size=12, color=MUTED, anchor="start", bold=True))
    span_row(f, x0, 258, bw, 50, [
        (4, "lat_e7 (int32)", FIELD, GREEN_BG),
        (4, "lon_e7 (int32)", FIELD, GREEN_BG),
        (4, "alt_mm (int32)", FIELD, GREEN_BG),
        (2, "mV", NEG, BLUE_BG),
        (2, "crc16", POS, RED_BG),
    ])
    f.append(text(x0, 336, "зсуви 16, 20, 24 кратні 4; 28 і 30 кратні 2 — жодного неявного падінгу",
                  size=11.5, color=MUTED, anchor="start"))

    # три висновки
    notes = [
        (FIELD, GREEN_BG, "Поля від більших до менших",
         "спершу 8 байтів, потім 4, потім 2 — природне вирівнювання виходить само"),
        (NEG, BLUE_BG, "Резерв — явне поле, а не дірка",
         "rsv записуємо нулями; майбутнє поле стане на його місце, зсуви не поїдуть"),
        (POS, RED_BG, "Довжина 32 = 8 × 4",
         "розширення дописуємо лише в хвіст — старий приймач читає своє й ігнорує решту"),
    ]
    bx, bw2 = x0, (W - 2 * x0 - 2 * 16) / 3
    for col, bg, head, sub in notes:
        f.append(rect(bx, 366, bw2, 112, fill=bg, stroke=col, sw=1.8, rx=12))
        f.append(fitbox(bx + 10, 380, bw2 - 20, 30, head, size=12.5, pad=4,
                        fill="none", stroke="none", sw=0, color=col, bold=True))
        words = sub.split()
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if len(t) > 34:
                lines.append(cur)
                cur = wd
            else:
                cur = t
        lines.append(cur)
        yy = 428
        for ln in lines:
            f.append(text(bx + bw2 / 2, yy, ln, size=11, color=INK))
            yy += 17
        bx += bw2 + 16

    out("packet-spec.svg", W, H, *f,
        title="Розкладка пакета як специфікація в байтах")


# ── 4. Приймальний бік: чому приведення покажчика падає ──────────────────────
def fig_receive_alignment():
    W, H = 1000, 540
    f = []
    x0, bw = 60, 28

    f.append(text(W / 2, 62, "кадр Ethernet у прийомному буфері: заголовок займає 14 байтів, далі йде заголовок IP",
                  size=13, color=INK, bold=True))

    # стрічка кадру
    span_row(f, x0, 110, bw, 46, [
        (14, "заголовок Ethernet — 14 байтів", MUTED, PAD_BG),
        (12, "заголовок IP: версія, довжина, TTL…", NEG, BLUE_BG),
        (4, "src IP (uint32)", POS, RED_BG),
    ])
    # позначка зсуву 26
    xmark = x0 + 26 * bw
    f.append(line(xmark, 158, xmark, 190, color=POS, sw=2, dash="4 3"))
    f.append(text(xmark + 6, 208, "зсув 26 у буфері", size=12, color=POS, anchor="start", bold=True))
    f.append(text(xmark + 6, 226, "26 = 4·6 + 2 → адреса НЕ кратна 4", size=11.5, color=POS, anchor="start"))

    # два шляхи
    f.append(rect(50, 252, 440, 176, fill=RED_BG, stroke=POS, sw=2, rx=12))
    f.append(text(270, 278, "✗ приведення покажчика", size=13.5, color=POS, bold=True))
    f.append(mono(70, 306, "const struct ip *h =", size=12.5, color=INK, anchor="start"))
    f.append(mono(70, 326, "    (const struct ip *)(buf + 14);", size=12.5, color=INK, anchor="start"))
    f.append(mono(70, 346, "uint32_t s = h->src;", size=12.5, color=INK, anchor="start"))
    f.append(text(70, 376, "• Cortex-M0/M0+, SPARC → HardFault / SIGBUS", size=11.5, color=POS, anchor="start"))
    f.append(text(70, 396, "• x86 і Cortex-M4 змовчать — і баг доживе до продукту", size=11.5, color=POS, anchor="start"))
    f.append(text(70, 416, "• плюс порядок байтів і падінг усе одно не збігаються", size=11.5, color=POS, anchor="start"))

    f.append(rect(510, 252, 440, 176, fill=GREEN_BG, stroke=FIELD, sw=2, rx=12))
    f.append(text(730, 278, "✓ читання байтами", size=13.5, color=FIELD, bold=True))
    f.append(mono(530, 306, "const uint8_t *p = buf + 26;", size=12.5, color=INK, anchor="start"))
    f.append(mono(530, 326, "uint32_t s = ((uint32_t)p[0] << 24) |", size=12.5, color=INK, anchor="start"))
    f.append(mono(530, 346, "   (p[1]<<16) | (p[2]<<8) | p[3];", size=12.5, color=INK, anchor="start"))
    f.append(text(530, 376, "• жодного вирівнювання не потрібно", size=11.5, color=FIELD, anchor="start"))
    f.append(text(530, 396, "• порядок байтів заданий явно, а не успадкований", size=11.5, color=FIELD, anchor="start"))
    f.append(text(530, 416, "• компілятор із -O2 згортає це в одну команду завантаження", size=11.5, color=FIELD, anchor="start"))

    f.append(rect(50, 448, W - 100, 66, fill=AMBER_BG, stroke=AMBER, sw=1.7, rx=12))
    f.append(text(W / 2, 474, "Ядро Linux обходить цю саму пастку зсувом буфера на 2 байти (NET_IP_ALIGN),",
                  size=12, color=INK, bold=True))
    f.append(text(W / 2, 496, "щоб заголовок IP почався з адреси, кратної 4, — латка для драйверів, а не дозвіл кастити в прикладному коді.",
                  size=11.5, color=INK))

    out("receive-alignment.svg", W, H, *f,
        title="Приймальний бік: приведення покажчика на буфер")


# ── 5. Обмежений читач на обрізаному повідомленні (до вставки proj) ──────────
def fig_codec_trace():
    W, H = 1100, 560
    f = []
    x0, cw = 70, 30          # лінійка байтів: 32 клітинки по 30 px
    got = 20                 # скільки байтів насправді прийшло

    f.append(text(W / 2, 50, "Обрізане повідомлення: межа спрацьовує один раз, далі читання просто порожні",
                  size=13.5, color=INK, bold=True))

    # ── лінійка байтів ───────────────────────────────────────────────────────
    f.append(text(x0 + got * cw / 2, 88, "прийшло: байти 0…19", size=12, color=FIELD, bold=True))
    f.append(text(x0 + (got + (32 - got) / 2) * cw, 88, "не дійшли: 20…31", size=12, color=MUTED, bold=True))
    for i in range(32):
        ok = i < got
        f.append(rect(x0 + i * cw, 100, cw, 30,
                      fill=GREEN_BG if ok else "#eceff1",
                      stroke=FIELD if ok else "#b6bcc2", sw=1.4, rx=3))
    for i in range(0, 33, 4):
        f.append(mono(x0 + i * cw, 148, str(i), size=11, color=MUTED, anchor="middle"))

    # ── два рядки читань ─────────────────────────────────────────────────────
    bw, gap, bh = 150, 12, 64

    def row(y, items):
        x = x0
        for call, note, col, bg in items:
            f.append(rect(x, y, bw, bh, fill=bg, stroke=col, sw=1.8, rx=8))
            f.append(mono(x + bw / 2, y + 26, call, size=11.5, color=col,
                          anchor="middle", bold=True))
            f.append(mono(x + bw / 2, y + 48, note, size=11, color=MUTED, anchor="middle"))
            x += bw + gap

    f.append(text(x0, 168, "поки байтів вистачає, читання просуває курсор і зменшує залишок",
                  size=11.5, color=MUTED, anchor="start"))
    row(182, [
        ("rd_u16 magic",   "20 → 18", FIELD, GREEN_BG),
        ("rd_u8  ver",     "18 → 17", FIELD, GREEN_BG),
        ("rd_u8  flags",   "17 → 16", FIELD, GREEN_BG),
        ("rd_u16 len",     "16 → 14", FIELD, GREEN_BG),
        ("rd_u16 rsv",     "14 → 12", FIELD, GREEN_BG),
        ("rd_u64 time_us", "12 → 4",  FIELD, GREEN_BG),
    ])
    row(300, [
        ("rd_i32 lat_e7", "4 → 0",           FIELD, GREEN_BG),
        ("rd_i32 lon_e7", "0 < 4  ✗",        POS,   RED_BG),
        ("rd_i32 alt_mm", "0, курсор стоїть", MUTED, PAD_BG),
        ("rd_u16 mV",     "0, курсор стоїть", MUTED, PAD_BG),
        ("rd_u16 crc16",  "0, курсор стоїть", MUTED, PAD_BG),
    ])

    # ── пояснення під рядком: злам і липкість ────────────────────────────────
    ax = x0 + bw + gap
    f.append(text(ax, 392, "перше читання за межею:", size=11.5, color=POS, anchor="start", bold=True))
    f.append(text(ax, 410, "bad = true, повертає 0, курсор не рухається", size=11.5, color=INK, anchor="start"))

    bx = x0 + 3 * (bw + gap)
    f.append(text(bx, 392, "прапорець липкий:", size=11.5, color=MUTED, anchor="start", bold=True))
    f.append(text(bx, 410, "усі наступні читання теж віддають нулі", size=11.5, color=INK, anchor="start"))

    # ── присуд ───────────────────────────────────────────────────────────────
    f.append(rect(x0, 442, 6 * bw + 5 * gap, 76, fill=RED_BG, stroke=POS, sw=1.8, rx=12))
    f.append(mono(W / 2, 472, "if (r.bad) → відкинути повідомлення", size=13.5,
                  color=POS, anchor="middle", bold=True))
    f.append(text(W / 2, 496, "одна перевірка наприкінці замість одинадцяти по дорозі — і жодна гілка не працює з напівпрочитаними полями",
                  size=11.5, color=INK))

    out("codec-trace.svg", W, H, *f,
        title="Обмежений читач: липкий прапорець помилки")


# ── 6. Граматика назв: htobe32, le64toh, htons ────────────────────────────────
def fig_endian_naming():
    W, H = 1060, 566
    f = []
    bw, gap, bh = 118, 16, 52
    xs = [70 + i * (bw + gap) for i in range(4)]

    def slot_row(ytop, tokens, labels, colors):
        for x, tok, col in zip(xs, tokens, colors):
            bg = {POS: RED_BG, NEG: BLUE_BG, FIELD: GREEN_BG, MUTED: CELL_BG}[col]
            f.append(rect(x, ytop, bw, bh, fill=bg, stroke=col, sw=2, rx=8))
            f.append(mono(x + bw / 2, ytop + 35, tok, size=22, color=col,
                          anchor="middle", bold=True))
        for x, (l1, l2) in zip(xs, labels):
            f.append(text(x + bw / 2, ytop + bh + 22, l1, size=11, color=MUTED))
            f.append(text(x + bw / 2, ytop + bh + 38, l2, size=11, color=MUTED))

    # рядок 1: htobe32
    slot_row(86, ["h", "to", "be", "32"],
             [("host —", "ваша машина"),
              ("напрям", "перетворення"),
              ("big-endian", "старший байт першим"),
              ("розрядність", "у бітах")],
             [NEG, MUTED, POS, FIELD])
    f.append(mono(624, 104, "htobe32(v)", size=15, color=INK, anchor="start", bold=True))
    f.append(text(624, 128, "узяти 32-бітне значення в поданні машини", size=13, anchor="start"))
    f.append(text(624, 150, "й повернути те саме число, укладене як big-endian", size=13, anchor="start"))

    # рядок 2: le64toh
    slot_row(216, ["le", "64", "to", "h"],
             [("little-endian", "молодший байт першим"),
              ("розрядність", "у бітах"),
              ("напрям", "перетворення"),
              ("host —", "ваша машина")],
             [POS, FIELD, MUTED, NEG])
    f.append(mono(624, 234, "le64toh(v)", size=15, color=INK, anchor="start", bold=True))
    f.append(text(624, 258, "узяти 64-бітне значення, прочитане з буфера", size=13, anchor="start"))
    f.append(text(624, 280, "як little-endian, і повернути в поданні машини", size=13, anchor="start"))

    # панель POSIX
    f.append(rect(70, 348, 960, 122, fill=CELL_BG, stroke=MUTED, sw=1.7, rx=12))
    f.append(text(550, 374, "POSIX-четвірка — той самий набір, лише вужчий і гірше названий",
                  size=13, color=INK, bold=True))
    f.append(mono(118, 404, "htons(v)  ≡  htobe16(v)", size=13.5, color=INK, anchor="start"))
    f.append(mono(118, 428, "htonl(v)  ≡  htobe32(v)", size=13.5, color=INK, anchor="start"))
    f.append(mono(578, 404, "ntohs(v)  ≡  be16toh(v)", size=13.5, color=INK, anchor="start"))
    f.append(mono(578, 428, "ntohl(v)  ≡  be32toh(v)", size=13.5, color=INK, anchor="start"))
    f.append(text(550, 456, "n = network = big-endian · s = short = 16 біт · l = long = 32 біти · 64-бітних варіантів у POSIX немає",
                  size=11.5, color=POS))

    # присуд
    f.append(rect(70, 486, 960, 62, fill=AMBER_BG, stroke=AMBER, sw=1.7, rx=12))
    f.append(text(550, 510, "На big-endian машині htobe32 не робить нічого, на little-endian — переставляє байти.",
                  size=12, color=INK, bold=True))
    f.append(text(550, 534, "Тому переносний код пише htobe32, а не власний bswap32 під #ifdef.",
                  size=12, color=INK))

    out("endian-naming.svg", W, H, *f,
        title="Граматика назв: як прочитати htobe32, le64toh і htons")


if __name__ == "__main__":
    fig_layout_drift()
    fig_shift_codec()
    fig_packet_spec()
    fig_receive_alignment()
    fig_codec_trace()
    fig_endian_naming()
    print("OK: 6 фігур у", IMG)
