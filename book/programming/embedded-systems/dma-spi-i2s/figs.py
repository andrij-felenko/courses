# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── block-to-bus: великий буфер у RAM виливається у шину словом за словом ──────
# Ідея: ядро дає DMA один наказ (джерело, призначення, довжина), далі шина сама
# смикає запит на кожне готове слово, DMA шле слово — ядро вільне весь час.

def fig_block_to_bus():
    W, H = 720, 320
    p = []

    # буфер у RAM — стовпчик клітинок-слів
    rx, ry, rw = 70, 70, 120
    cell, n = 26, 7
    p.append(text(rx + rw / 2, ry - 14, "буфер кадру в RAM", size=12, color=INK, bold=True))
    for i in range(n):
        fill = "#eef4ff" if i else "#dbe6fb"
        p.append(rect(rx, ry + i * cell, rw, cell, fill=fill, stroke="#c9d6f0", sw=1.0, rx=0))
    p.append(text(rx + rw / 2, ry + n * cell + 16, "150 КБ слів", size=10, color=MUTED))

    # DMA посередині
    dma, dw, dh = textbox(360, 150, "DMA\nджерело → призначення\nдовжина, старт",
                          size=11, bold=True, fill="#f2ecf8", stroke="#8a5fb0", sw=1.8, pad=12)
    p.append(dma)

    # шина праворуч (FIFO периферії)
    bx, by, bw, bh = 560, 110, 110, 80
    p.append(fitbox(bx, by, bw, bh, "FIFO шини\n(SPI / I2S)", size=11, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(bx + bw / 2, by + bh + 26, "одне слово\nза такт", size=10, color=MUTED))

    # потік RAM → DMA → шина
    p.append(arrow(rx + rw + 6, 150, 360 - dw / 2 - 6, 150, color=INK, sw=2.0))
    p.append(arrow(360 + dw / 2 + 6, 150, bx - 6, 150, color=INK, sw=2.0))

    # зворотний пунктир «запит на наступне слово»
    p.append(line(bx, by + bh - 8, 360 + dw / 2, dh + 70, color=FIELD, sw=1.6, dash="5 4"))
    p.append(text((bx + 360) / 2, dh + 78, "запит на наступне слово", size=10, color=FIELD))

    # ядро збоку — вільне
    p.append(fitbox(290, 256, 140, 40, "ядро вільне", size=12, bold=True,
                    fill=FILL, stroke=INK, sw=1.5, color=FIELD))

    render(os.path.join(OUT, "block-to-bus.svg"), W, H, *p,
           title="Один наказ — і DMA виливає весь блок у шину словом за словом")


# ── frame-jitter: без DMA кадр ривками; з DMA рівний потік ─────────────────────
# Ідея: дві часові доріжки. Без DMA ядро суцільно зайняте заливкою, кадр
# виходить нерівно; з DMA шина зайнята, ядро паралельно рахує наступний кадр.

def fig_frame_jitter():
    W, H = 720, 320
    p = []
    tx0, tx1 = 90, 660

    def track(y, label, segs):
        out = [text(tx0 - 8, y - 22, label, size=11, color=INK, anchor="start", bold=True)]
        out.append(line(tx0, y, tx1, y, color=INK, sw=1.4))
        x = tx0
        span = tx1 - tx0
        for frac, fill, lab in segs:
            w = span * frac
            out.append(rect(x, y - 16, w, 32, fill=fill, stroke=INK, sw=1.0, rx=0))
            if w > 40 and lab:
                out.append(text(x + w / 2, y + 5, lab, size=10, color=INK))
            x += w
        return out

    # без DMA: заливка ядром, ривок, заливка — нема часу на обчислення
    p += track(70, "Без DMA: ядро прикуте до шини",
               [(0.42, "#f3dede", "ядро жене байти"),
                (0.06, "#ffffff", ""),
                (0.42, "#f3dede", "ядро жене байти"),
                (0.10, "#ffffff", "")])
    p.append(text(tx0 + (tx1 - tx0) * 0.5, 108, "кадр виходить ривками — на логіку часу немає",
                  size=10, color=POS, italic=True))

    # з DMA: дві доріжки — шина зайнята, ядро паралельно рахує
    p += track(190, "З DMA — шина зайнята весь час",
               [(0.46, "#eafaf0", "DMA жене кадр A"),
                (0.46, "#eafaf0", "DMA жене кадр B"),
                (0.08, "#eafaf0", "")])
    p += track(250, "          ядро паралельно",
               [(0.46, "#eef4ff", "рахує кадр B"),
                (0.46, "#eef4ff", "рахує кадр C"),
                (0.08, "#eef4ff", "")])
    p.append(text(tx0 + (tx1 - tx0) * 0.5, 290, "рівний потік — картинка плавна, ядро встигає й логіку",
                  size=10, color=FIELD, italic=True))

    render(os.path.join(OUT, "frame-jitter.svg"), W, H, *p,
           title="Той самий такт і ті самі 150 КБ — але без DMA кадр смикається")


# ── audio-duplex: симетричний безперервний потік звуку через DMA ───────────────
# Ідея: на відміну від дисплея, звук тече в обидва боки без пауз. Мікрофон сам
# наповнює одну половину кільця, ядро обробляє іншу; так само на вихід.

def fig_audio_duplex():
    W, H = 720, 340
    p = []
    cy = 90

    # верхній рядок: мікрофон → шина → DMA → RAM
    chain_in = [("мікрофон", "#eafaf0"), ("шина I2S", FILL), ("DMA", "#f2ecf8"), ("кільце в RAM", "#eef4ff")]
    x, bw, bh, step = 60, 120, 46, 160
    cin = []
    for i, (lab, fill) in enumerate(chain_in):
        p.append(fitbox(x, cy - bh / 2, bw, bh, lab, size=11, bold=True, fill=fill, stroke=INK, sw=1.5))
        cin.append((x, x + bw))
        if i:
            p.append(arrow(cin[i - 1][1] + 2, cy, x - 2, cy, color=INK, sw=1.8))
        x += step
    p.append(text(W / 2, cy - bh / 2 - 14, "вхід: семпли течуть БЕЗ пауз — пропустив вікно — «клац»",
                  size=10, color=MUTED, italic=True))

    # кільце буферів посередині — дві половини
    ky = 200
    kx, kw, khalf = 250, 220, 110
    p.append(rect(kx, ky, khalf, 56, fill="#dff0df", stroke=FIELD, sw=1.6, rx=0))
    p.append(rect(kx + khalf, ky, khalf, 56, fill="#f3dede", stroke=POS, sw=1.6, rx=0))
    p.append(text(kx + khalf / 2, ky + 32, "DMA пише", size=10, color=FIELD, bold=True))
    p.append(text(kx + khalf + khalf / 2, ky + 32, "ядро читає", size=10, color=POS, bold=True))
    p.append(text(kx + kw / 2, ky - 12, "кільцевий (подвійний) буфер", size=11, color=INK, bold=True))
    p.append(text(kx + kw / 2, ky + 78, "половини міняються місцями кожен блок", size=10, color=MUTED))

    # нижній рядок: RAM → DMA → шина → підсилювач
    cy2 = 300
    chain_out = [("кільце в RAM", "#eef4ff"), ("DMA", "#f2ecf8"), ("шина I2S", FILL), ("підсилювач", "#eafaf0")]
    x = 60
    cout = []
    for i, (lab, fill) in enumerate(chain_out):
        p.append(fitbox(x, cy2 - bh / 2, bw, bh, lab, size=11, bold=True, fill=fill, stroke=INK, sw=1.5))
        cout.append((x, x + bw))
        if i:
            p.append(arrow(cout[i - 1][1] + 2, cy2, x - 2, cy2, color=INK, sw=1.8))
        x += step
    p.append(text(W / 2, cy2 + bh / 2 + 16, "вихід: ядро готує семпли наперед, DMA рівно віддає їх у підсилювач",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "audio-duplex.svg"), W, H, *p,
           title="Звук — симетричний безперервний потік: DMA з кільцем тримає обидва напрями")


# ── comp-spi-display: вартість одного кадру і де застрягає ядро ────────────────
def fig_frame_cost():
    W, H = 720, 250
    p = []
    tx0, tx1 = 90, 660
    span = tx1 - tx0

    # верхня доріжка — SPI-шина зайнята весь кадр
    y1 = 90
    p.append(text(tx0 - 8, y1 - 24, "SPI-шина", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(tx0, y1 - 16, span, 32, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=0))
    p.append(text(tx0 + span / 2, y1 + 5, "150 КБ пікселів ≈ 30.7 мс", size=11, color=INK))

    # нижня доріжка — ядро без DMA: суцільна заливка + порожнє «нема часу рахувати»
    y2 = 165
    p.append(text(tx0 - 8, y2 - 24, "ядро без DMA", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(tx0, y2 - 16, span, 32, fill="#f3dede", stroke=POS, sw=1.4, rx=0))
    p.append(text(tx0 + span / 2, y2 + 5, "байт → регістр SPI → чекати  (на наступний кадр часу 0)",
                  size=10, color=INK))

    p.append(text(W / 2, 222, "вузьке місце — не панель і не шина, а прикуте ядро",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "frame-cost.svg"), W, H, *p,
           title="Скільки коштує кадр і де застрягає ядро")


# ── comp-spi-display: без DMA проти з DMA + два буфери ─────────────────────────
def fig_dma_vs_nodma():
    W, H = 720, 340
    p = []
    tx0, tx1 = 100, 660
    span = tx1 - tx0

    def track(y, label, color, fill, segs):
        out = [text(tx0 - 12, y + 4, label, size=10, color=INK, anchor="end", bold=True)]
        out.append(line(tx0, y, tx1, y, color=INK, sw=1.2))
        x = tx0
        for frac, lab in segs:
            w = span * frac
            out.append(rect(x, y - 14, w, 28, fill=fill, stroke=color, sw=1.2, rx=0))
            if w > 50 and lab:
                out.append(text(x + w / 2, y + 4, lab, size=9, color=INK))
            x += w
        return out

    # без DMA
    p.append(text(tx0, 56, "Без DMA", size=12, color=POS, anchor="start", bold=True))
    p += track(86, "CPU", POS, "#f3dede", [(0.92, "байт → SPI DR (суцільно)"), (0.08, "")])
    p += track(122, "шина", INK, "#eafaf0", [(0.92, "пікселі"), (0.08, "")])
    p.append(text(tx0 + span / 2, 150, "наступний кадр спізнюється", size=9, color=POS, italic=True))

    # з DMA + 2 буфери
    p.append(text(tx0, 206, "DMA + два буфери", size=12, color=FIELD, anchor="start", bold=True))
    p += track(236, "шина", FIELD, "#eafaf0", [(0.46, "DMA жене буфер A"), (0.46, "DMA жене буфер B"), (0.08, "")])
    p += track(272, "CPU", NEG, "#eef4ff", [(0.46, "малює буфер B"), (0.46, "малює буфер C"), (0.08, "")])
    # лінія обміну A↔B
    swx = tx0 + span * 0.46
    p.append(line(swx, 222, swx, 286, color=INK, sw=1.4, dash="4 3"))
    p.append(text(swx, 306, "обмін A↔B", size=9, color=MUTED))

    render(os.path.join(OUT, "dma-vs-nodma.svg"), W, H, *p,
           title="Хто кого годує: ядро проти DMA")


# ── comp-i2s-mic: блок-схема корпусу INMP441-класу ────────────────────────────
def fig_mic_block():
    W, H = 720, 250
    p = []
    cy = 120
    # корпус-рамка
    p.append(rect(60, 60, 470, 130, fill="#fbfbfd", stroke=MUTED, sw=1.4, rx=10))
    p.append(text(295, 80, "корпус 3×4 мм", size=10, color=MUTED))

    chain = [("капсула", "#eafaf0"), ("сигма-дельта\nАЦП", "#eef4ff"), ("I2S-\nпередавач", "#f2ecf8")]
    x, bw, bh, step = 90, 110, 56, 145
    c = []
    for i, (lab, fill) in enumerate(chain):
        p.append(fitbox(x, cy - bh / 2, bw, bh, lab, size=11, bold=True, fill=fill, stroke=INK, sw=1.5))
        c.append((x, x + bw))
        if i:
            p.append(arrow(c[i - 1][1] + 2, cy, x - 2, cy, color=INK, sw=1.8))
        x += step

    # назовні — три лінії I2S
    p.append(arrow(530, cy, 600, cy, color=INK, sw=2.0))
    p.append(fitbox(600, cy - 34, 100, 68, "три лінії I2S\n+ живлення", size=10, bold=True,
                    fill=FILL, stroke=INK, sw=1.5))
    p.append(text(W / 2, 225, "назовні — готові 24-бітні відліки, а не аналогова напруга",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "mic-block.svg"), W, H, *p,
           title="Усередині цифрового мікрофона INMP441-класу")


# ── comp-i2s-mic: часова діаграма SCK / WS / SD ───────────────────────────────
def fig_i2s_timing():
    W, H = 720, 300
    p = []
    x0, x1 = 110, 660
    span = x1 - x0
    hi, lo = 18, 18         # амплітуда

    def label(y, s, color):
        return text(x0 - 12, y + 4, s, size=11, color=color, anchor="end", bold=True)

    # SCK — рівний меандр (метроном)
    ys = 70
    p.append(label(ys, "SCK", INK))
    bits = 16
    bw = span / bits
    pts = []
    for i in range(bits + 1):
        x = x0 + i * bw
        up = (i % 2 == 0)
        pts.append("%.1f,%.1f" % (x, ys - (hi if up else -lo) / 1 * 0 - (hi if up else -lo)))
    # будуємо як прямокутний меандр
    seg = [f"{x0:.1f},{ys + lo:.1f}"]
    for i in range(bits):
        x = x0 + i * bw
        seg.append("%.1f,%.1f" % (x, ys - hi))
        seg.append("%.1f,%.1f" % (x + bw / 2, ys - hi))
        seg.append("%.1f,%.1f" % (x + bw / 2, ys + lo))
        seg.append("%.1f,%.1f" % (x + bw, ys + lo))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(seg), INK))

    # WS — перемикається раз на слово (тут на півекрана)
    yw = 150
    p.append(label(yw, "WS", NEG))
    mid = x0 + span / 2
    wsseg = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        x0, yw + lo, mid, yw + lo, mid, yw - hi, x1, yw - hi, x1, yw - hi)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (wsseg, NEG))
    p.append(text(x0 + span * 0.25, yw + 32, "лівий канал", size=9, color=NEG))
    p.append(text(x0 + span * 0.75, yw + 32, "правий канал", size=9, color=NEG))

    # SD — біти MSB-first (схематично кілька рівнів)
    yd = 230
    p.append(label(yd, "SD", FIELD))
    pattern = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0]
    sdseg = []
    prev = None
    for i, b in enumerate(pattern):
        x = x0 + i * bw
        lvl = yd - hi if b else yd + lo
        if prev is not None and prev != lvl:
            sdseg.append("%.1f,%.1f" % (x, prev))
        sdseg.append("%.1f,%.1f" % (x, lvl))
        sdseg.append("%.1f,%.1f" % (x + bw, lvl))
        prev = lvl
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(sdseg), FIELD))
    p.append(text(x0 + bw * 0.5, yd - 26, "MSB", size=9, color=FIELD))

    render(os.path.join(OUT, "i2s-timing.svg"), W, H, *p,
           title="Як читається I2S: SCK тактує, WS вибирає канал, SD несе біти")


# ── hist-soundblaster: шина ISA та канали DMA ─────────────────────────────────
def fig_isa_bus():
    W, H = 720, 300
    p = []
    # шина-смуга
    bx, by, bw, bh = 80, 130, 560, 40
    p.append(rect(bx, by, bw, bh, fill="#eef0f4", stroke=INK, sw=1.6, rx=4))
    p.append(text(bx + bw / 2, by + bh / 2 + 4, "шина ISA: адреси · дані · IRQ · DMA-канали", size=11, color=INK, bold=True))

    # пристрої зверху, що чіпляються до шини
    devs = [("DRAM refresh", "канал 0", MUTED, "#efefef"),
            ("Sound Blaster", "канал 1", FIELD, "#eafaf0"),
            ("дисковод", "канал 2", MUTED, "#efefef"),
            ("HDD", "канал 3", MUTED, "#efefef")]
    n = len(devs)
    for i, (name, ch, col, fill) in enumerate(devs):
        cx = bx + bw * (i + 0.5) / n
        b, w, h = textbox(cx, 70, name + "\n" + ch, size=10, bold=True, color=col, fill=fill, stroke=col, sw=1.6)
        p.append(line(cx, 70 + h / 2, cx, by, color=col, sw=1.6))
        p.append(b)

    p.append(text(W / 2, 240, "пристрої ділять IRQ та DMA-канали; Sound Blaster узяв вільний канал 1",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "isa-bus.svg"), W, H, *p,
           title="Шина ISA і канал DMA 1 Sound Blaster'а")


# ── hist-soundblaster: CPU-loop проти DMA ─────────────────────────────────────
def fig_dma_flow():
    W, H = 720, 280
    p = []
    # ліворуч — без DMA: CPU у циклі ~8%
    p.append(fitbox(70, 70, 240, 130,
                    "Без DMA (Covox-стиль):\nCPU у циклі\nбайт → порт → чекати\n~8% часу зайнято",
                    size=11, fill="#f3dede", stroke=POS, sw=1.6, color=INK))
    # праворуч — з DMA: тільки ISR на кінці буфера
    p.append(fitbox(410, 70, 240, 130,
                    "З DMA (Sound Blaster):\nконтролер краде 1 цикл\nна байт; CPU вільний,\nISR лише на кінці буфера",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK))
    p.append(arrow(310 + 8, 135, 410 - 8, 135, color=INK, sw=2.0))
    p.append(text(W / 2, 235, "затрати CPU падають із ~8% до часток відсотка",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dma-flow.svg"), W, H, *p,
           title="Що робить процесор під час звуку: цикл проти DMA")


# ── hist-soundblaster: еволюція Sound Blaster ─────────────────────────────────
def fig_timeline():
    W, H = 720, 250
    p = []
    x0, x1, y = 80, 660, 130
    p.append(line(x0, y, x1, y, color=INK, sw=2.0))
    p.append(arrow(x1 - 2, y, x1 + 6, y, color=INK, sw=2.0))
    items = [("1988", "Game Blaster"), ("1989", "SB 1.0"), ("1991", "SB Pro"),
             ("1992", "SB 16"), ("1994", "AWE32")]
    n = len(items)
    for i, (yr, name) in enumerate(items):
        x = x0 + (x1 - x0 - 30) * i / (n - 1)
        p.append(circle(x, y, 5, fill=FIELD, stroke=INK, sw=1.5))
        p.append(text(x, y - 16, yr, size=11, color=INK, bold=True))
        p.append(text(x, y + 26, name, size=10, color=MUTED))
    p.append(text(W / 2, 200, "канал DMA 1 та IRQ 5 лишались незмінними в усіх поколіннях",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Еволюція Sound Blaster: 1988–1994")


if __name__ == "__main__":
    # стаття
    fig_block_to_bus()
    fig_frame_jitter()
    fig_audio_duplex()
    # вставка comp-spi-display
    fig_frame_cost()
    fig_dma_vs_nodma()
    # вставка comp-i2s-mic
    fig_mic_block()
    fig_i2s_timing()
    # вставка hist-soundblaster
    fig_isa_bus()
    fig_dma_flow()
    fig_timeline()
    print("OK: figures written to", OUT)
