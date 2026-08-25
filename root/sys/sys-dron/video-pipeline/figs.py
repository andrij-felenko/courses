# -*- coding: utf-8 -*-
"""Фігури до теми «Відеотракт станції на GStreamer»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def pipeline():
    W, H = 1400, 660
    f = []

    # ── джерело: панель зі стосом елементів ───────────────────────────────
    f.append(rect(40, 190, 250, 310, fill="#ffffff", stroke=MUTED, sw=1.5))
    f.append(text(165, 216, "Джерело — за схемою адреси", size=13, color=MUTED))

    src = [
        "udpsrc / rtspsrc",
        "rtpjitterbuffer",
        "rtph264depay",
        "h264parse",
    ]
    ys = [234, 298, 362, 426]
    for s, y in zip(src, ys):
        f.append(fitbox(60, y, 210, 44, s, size=14))
    for y in ys[:-1]:
        f.append(arrow(165, y + 44, 165, y + 62))

    # ── трійник ───────────────────────────────────────────────────────────
    f.append(arrow(292, 345, 336, 345))
    f.append(fitbox(340, 295, 100, 100, "tee\nтрійник", size=14, bold=True))

    # ── гілка показу ──────────────────────────────────────────────────────
    up_y, up_h = 150, 70
    f.append(arrow(444, 320, 500, up_y + up_h / 2))
    up = [
        (500, 180, "queue\nпротікальна, 2 буфери"),
        (720, 160, "valve\nклапан показу"),
        (930, 190, "decodebin3\nвибір за рангом"),
        (1160, 180, "стік\nописувач кадру"),
    ]
    for x, w, s in up:
        f.append(fitbox(x, up_y, w, up_h, s, size=13))
    for i in range(len(up) - 1):
        x0 = up[i][0] + up[i][1]
        f.append(arrow(x0, up_y + up_h / 2, up[i + 1][0] - 4, up_y + up_h / 2))
    f.append(arrow(1340, up_y + up_h / 2, 1360, up_y + up_h / 2))
    f.append(text(1370, up_y + up_h / 2 - 22, "екран", size=13, color=FIELD, bold=True, anchor="end"))

    # ── гілка запису ──────────────────────────────────────────────────────
    dn_y, dn_h = 480, 70
    f.append(arrow(444, 372, 500, dn_y + dn_h / 2))
    dn = [
        (500, 180, "queue\nбез утрат"),
        (720, 160, "valve\nклапан запису"),
        (930, 230, "splitmuxsink\nпакувальник + файл"),
    ]
    for x, w, s in dn:
        f.append(fitbox(x, dn_y, w, dn_h, s, size=13))
    for i in range(len(dn) - 1):
        x0 = dn[i][0] + dn[i][1]
        f.append(arrow(x0, dn_y + dn_h / 2, dn[i + 1][0] - 4, dn_y + dn_h / 2))
    f.append(arrow(1160, dn_y + dn_h / 2, 1200, dn_y + dn_h / 2))
    f.append(text(1210, dn_y + dn_h / 2 + 5, "MP4 / MOV / MKV", size=13,
                  color=NEG, bold=True, anchor="start"))

    # ── підпис унизу ──────────────────────────────────────────────────────
    f.append(text(40, 620,
                  "Розгалуження стоїть ДО декодера: у файл лягає той самий бітовий потік, що прилетів по радіо.",
                  size=14, color=INK, anchor="start"))
    f.append(text(40, 644,
                  "Клапани вмикають показ і запис, не чіпаючи джерела: з'єднання не рветься, ключового кадру чекати не треба.",
                  size=14, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'pipeline.svg'), W, H, *f,
           title="Відеотракт станції: від пакета до екрана і до файлу")


def latency():
    W, H = 1160, 470
    f = []
    x0, scale, bh = 330, 8.0, 34

    rows = [
        ("кодування на борту", 50, MUTED, "борт"),
        ("політ радіоканалом", 20, MUTED, "канал"),
        ("буфер вирівнювання", 80, FIELD, "станція"),
        ("декодування", 33, FIELD, "станція"),
        ("показ кадру", 17, FIELD, "станція"),
    ]
    y = 96
    for name, ms, col, who in rows:
        f.append(text(310, y + bh * 0.72, name, size=14, anchor="end"))
        f.append(rect(x0, y, ms * scale, bh, fill=col, stroke=col, sw=1.0, rx=3))
        f.append(text(x0 + ms * scale + 12, y + bh * 0.72, "%d мс" % ms,
                      size=14, anchor="start", bold=True))
        f.append(text(x0 + ms * scale + 90, y + bh * 0.72, who, size=13,
                      color=MUTED, anchor="start"))
        y += 62

    f.append(line(x0, 84, x0, y - 22, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(40, y + 24,
                  "Разом «від скла до скла» ≈ 200 мс для 1080p30.",
                  size=14, anchor="start", bold=True))
    f.append(text(40, y + 52,
                  "Зелені три доданки — 130 мс — єдине, на що впливає наземна станція.",
                  size=14, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'latency.svg'), W, H, *f,
           title="Бюджет затримки відео: хто скільки додає")


def watchdog():
    W, H = 1400, 520
    f = []

    chain = [
        (60, 250, "джерело\nudpsrc / rtspsrc"),
        (390, 260, "трійник\nзонд A: останній пакет"),
        (730, 180, "декодер"),
        (970, 270, "стік\nзонд B: останній кадр"),
    ]
    cy, ch = 66, 64
    for x, w, s in chain:
        f.append(fitbox(x, cy, w, ch, s, size=13))
    for i in range(len(chain) - 1):
        x0 = chain[i][0] + chain[i][1]
        f.append(arrow(x0, cy + ch / 2, chain[i + 1][0] - 4, cy + ch / 2))
    f.append(arrow(1240, cy + ch / 2, 1275, cy + ch / 2))
    f.append(text(1360, cy + ch / 2 + 5, "екран", size=13, color=FIELD,
                  bold=True, anchor="end"))

    panels = [
        (40, FIELD, "A свіжий, B свіжий",
         ["Норма.", "Кадри доходять до екрана,", "перезапуск не потрібен."]),
        (490, POS, "A свіжий, B старіший за 2×T",
         ["Потік іде, та не декодується:", "не той кодек, немає ключового",
          "кадру, збій декодера."]),
        (940, POS, "A старіший за T",
         ["Джерело зникло: радіоканал,", "живлення камери,",
          "маршрут у мережі."]),
    ]
    for x, col, cond, lines in panels:
        f.append(rect(x, 220, 420, 200, fill="#ffffff", stroke=col, sw=2))
        f.append(fitbox(x + 20, 240, 380, 52, cond, size=14, bold=True))
        f.append(mtext(x + 210, 328, lines, size=13, color=INK, lh=1.35))

    f.append(text(40, 470,
                  "T — час очікування джерела (типово 8 с). Після кожної невдалої спроби пауза подвоюється: 1, 2, 4 … 30 с.",
                  size=14, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'watchdog.svg'), W, H, *f,
           title="Дві точки спостереження розрізняють три стани тракту")


def threads():
    W, H = 1420, 770
    f = []

    lanes = [
        (40, 380, "1 · Нитка виклику — головна"),
        (520, 360, "2 · Нитка робітника приймача"),
        (1000, 380, "3 · Нитки потоку GStreamer"),
    ]
    for x, w, head in lanes:
        f.append(fitbox(x, 40, w, 52, head, size=15, bold=True))
        f.append(rect(x, 110, w, 420, fill="#ffffff", stroke=MUTED, sw=1.5))

    # ── нитка 1 ───────────────────────────────────────────────────────────
    f.append(fitbox(65, 140, 330, 64,
                    "VideoManager, QML, код станції:\n"
                    "start · stop · startDecoding · startRecording", size=13))
    f.append(fitbox(65, 250, 330, 100,
                    "QTimer сторожа, такт 1000 мс:\n"
                    "читає мітки часу зондів\n"
                    "і лічильники якости", size=13))
    f.append(fitbox(65, 400, 330, 100,
                    "обробники сигналів:\n"
                    "onStartComplete · timeout ·\n"
                    "streamingChanged · recordingChanged", size=13))

    # ── нитка 2 ───────────────────────────────────────────────────────────
    f.append(fitbox(545, 140, 310, 64, "черга задач під м'ютексом", size=13))
    f.append(fitbox(545, 250, 310, 100,
                    "єдина нитка, що будує,\n"
                    "розбирає й перемикає конвеєр:\n"
                    "елементи, пади, клапани", size=13))
    f.append(fitbox(545, 400, 310, 100,
                    "перезапуск тракту\n"
                    "з наростальною паузою", size=13))

    # ── нитка 3 ───────────────────────────────────────────────────────────
    f.append(fitbox(1025, 140, 330, 64,
                    "зонди на трійнику й на стоці:\n"
                    "мітки часу останніх буферів", size=13))
    f.append(fitbox(1025, 250, 330, 100,
                    "sync-message шини:\n"
                    "ERROR · EOS · QOS ·\n"
                    "ELEMENT · LATENCY", size=13))
    f.append(fitbox(1025, 400, 330, 100,
                    "лічильники якости,\nатомарні", size=13))

    # ── переходи між нитками ──────────────────────────────────────────────
    f.append(arrow(425, 200, 515, 200))
    f.append(text(470, 186, "dispatch", size=12, color=MUTED))

    f.append(arrow(995, 450, 885, 450))
    f.append(text(940, 436, "dispatch", size=12, color=MUTED))

    # ── смуга сигналів ────────────────────────────────────────────────────
    f.append(arrow(700, 535, 700, 594))
    f.append(arrow(1190, 535, 1190, 594))
    f.append(rect(40, 598, 1340, 92, fill="#ffffff", stroke=FIELD, sw=2))
    f.append(mtext(760, 632,
                   ["Сигнали приймача летять із ниток 2 і 3 у нитку одержувача чергою подій:",
                    "обробник виконується там, де живе одержувач, і завжди пізніше за виклик."],
                   size=14, color=INK, lh=1.4))
    f.append(arrow(210, 594, 210, 535))

    f.append(text(40, 726,
                  "Правило одне: усе, що чіпає конвеєр, виконує нитка 2 — байдуже, звідки покликали.",
                  size=14, color=INK, anchor="start", bold=True))
    f.append(text(40, 754,
                  "Виклик із чужої нитки не помилка: він стає задачею в черзі й відповідає сигналом.",
                  size=14, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'threads.svg'), W, H, *f,
           title="Три нитки приймача відео й що між ними ходить")


pipeline()
latency()
watchdog()
threads()


def sink_eras():
    """Вставка hist-video-sink: чотири покоління стоку до сцени."""
    W, H = 1420, 800
    f = []

    X0, XW = 320, 1070          # смуга ланцюга
    ROW_H = 190
    tops = [60, 250, 440, 630]

    eras = [
        ("До 2020\nsrc/VideoStreaming",
         [(240, "qtvideosink\nкопія QtGStreamer"),
          (250, "власні painters\nvideonode, шейдери"),
          (220, "VideoItem\nQQuickItem")],
         POS, "апстрим QtGStreamer завмер — близько сорока файлів чужого GL-коду лишилися на утриманні QGC"),

        ("лютий 2020\nPR #8266",
         [(230, "glupload"),
          (270, "qmlglsink\nз gst-plugins-good"),
          (250, "GstGLVideoItem\nу QML")],
         POS, "qmlglsink вимагає контексту OpenGL, а Qt 6 малює через RHI: Metal, Vulkan, D3D11"),

        ("квіт.–трав. 2026\n#14228, потім усі платформи",
         [(230, "videoconvert\n→ BGRA"),
          (170, "appsink"),
          (250, "GstAppSinkAdapter"),
          (240, "QVideoSink\nVideoOutput")],
         POS, "два повних копіювання кадру центральним процесором — близько 0.5 ГБ/с на порожньому місці"),

        ("липень 2026\nвласний плагін gstqgc",
         [(250, "qgcvideosinkbin"),
          (270, "qgcqvideosink\nвласний елемент"),
          (240, "QVideoSink\nVideoOutput")],
         FIELD, "через межу йде описувач кадру: dmabuf, GL, Vulkan, D3D, CUDA, IOSurface, AHardwareBuffer"),
    ]

    for i, (label, chain, note_color, note) in enumerate(eras):
        top = tops[i]

        # ліва колонка — доба
        f.append(fitbox(40, top + 8, 250, 76, label, size=14, bold=True, fill="#ffffff"))

        # ланцюг
        gap = 34
        total = sum(w for w, _ in chain) + gap * (len(chain) - 1)
        x = X0 + (XW - total) / 2
        for j, (w, s) in enumerate(chain):
            f.append(fitbox(x, top + 8, w, 76, s, size=14))
            if j < len(chain) - 1:
                f.append(arrow(x + w, top + 46, x + w + gap, top + 46))
            x += w + gap

        # рядок «що зрушило далі»
        mark = "⤷ " if note_color == POS else "✓ "
        f.append(text(340, top + 120, mark + note, size=13, color=note_color, anchor="start"))

        # стрілка часу вниз
        if i < len(eras) - 1:
            f.append(arrow(165, top + 92, 165, top + ROW_H + 4, color=MUTED, sw=1.6))

    render(os.path.join(IMG, 'sink-eras.svg'), W, H, *f,
           title="Чотири покоління стоку: чим станція віддавала кадр в інтерфейс")


sink_eras()


# ── Зупинка запису: п'ять кроків (до вставки proj-min-video-pipeline) ────────
def stop_rec():
    W, H = 1280, 570
    f = []

    # ── верхня смуга: ланцюг гілки запису ─────────────────────────────────
    TOP, BH = 78, 86

    def box(x, w, s, **kw):
        return fitbox(x, TOP, w, BH, s, size=14, **kw)

    f.append(box(48, 110, "tee", bold=True))
    f.append(arrow(158, TOP + BH / 2, 194, TOP + BH / 2))

    f.append(box(196, 210, "queue\nне протікає"))
    f.append(arrow(406, TOP + BH / 2, 442, TOP + BH / 2))

    f.append(box(444, 210, "valve\ndrop = TRUE",
                 fill="#fdecea", stroke=POS, color=POS))

    # різ між клапаном і пакувальником
    f.append(line(700, 56, 700, TOP + BH + 16, color=POS, sw=2, dash="7 6"))
    f.append(text(700, 50, "розлінковано", size=13, color=POS, bold=True))

    f.append(box(746, 230, "splitmuxsink", bold=True))
    f.append(arrow(976, TOP + BH / 2, 1012, TOP + BH / 2))
    f.append(box(1014, 218, "flight-00000.mp4"))

    # гілка показу — окремо, щоб було видно, що її не чіпають
    f.append(arrow(103, TOP + BH + 2, 103, TOP + BH + 44, color=MUTED, sw=1.6))
    f.append(fitbox(30, TOP + BH + 46, 190, 54, "гілка показу\nпрацює далі",
                    size=13, fill="#ffffff", stroke=MUTED, color=MUTED))

    # подія кінця потоку — знизу прямо в пакувальник
    f.append(arrow(861, TOP + BH + 84, 861, TOP + BH + 6, color=POS, sw=2))
    f.append(text(861, TOP + BH + 108,
                  "подія кінця потоку — прямо в пад пакувальника, повз клапан",
                  size=13, color=POS))

    # ── нижня смуга: п'ять кроків ─────────────────────────────────────────
    SY, SH, SW, GAP = 330, 112, 222, 30
    x0 = (W - (5 * SW + 4 * GAP)) / 2
    steps = [
        "1 · клапан\ndrop = TRUE\nкадри не заходять",
        "2 · різ\ngst_pad_unlink\nпакувальник окремо",
        "3 · кінець потоку\ngst_pad_send_event\nу пад пакувальника",
        "4 · підтвердження\nsplitmuxsink-\nfragment-closed",
        "5 · прибирання\nset_state(NULL)\ngst_bin_remove",
    ]
    for i, s in enumerate(steps):
        x = x0 + i * (SW + GAP)
        f.append(fitbox(x, SY, SW, SH, s, size=13))
        if i < len(steps) - 1:
            f.append(arrow(x + SW, SY + SH / 2, x + SW + GAP - 4, SY + SH / 2))

    f.append(text(W / 2, SY + SH + 40,
                  "стеля очікування — 3 с: зависла файлова система не має права "
                  "підвісити застосунок", size=14, color=POS))

    render(os.path.join(IMG, 'stop-rec.svg'), W, H, *f,
           title="Зупинка запису: п'ять кроків, після яких файл відкривається")


stop_rec()
print("ok")
