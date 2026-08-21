# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"
PURPLE = "#f3e5f5"


# ── 1. Архітектура M2M-пристрою: дві черги на одному дескрипторі ───────────
def fig_m2m_architecture():
    W, H = 1100, 720
    p = []

    # Верх: Простір користувача
    f_user, w_u, h_u = textbox(550, 70, [
        "Простір користувача (Userspace)",
        "Один відкритий дескриптор: fd = open(\"/dev/video0\", O_RDWR)",
        "poll(POLLIN | POLLOUT) / epoll"
    ], size=14, pad=14, fill=BLUE, stroke=LINE, bold=True)
    p.append(f_user)

    # Межа просторів (пунктир)
    p.append(line(50, 145, 1050, 145, color=MUTED, sw=1.5, dash="6,6"))
    p.append(text(150, 138, "Ядро Linux (Kernel Space) — struct v4l2_m2m_ctx", size=12, color=MUTED, italic=True))

    # Ліва колонка в ядрі: Черга OUTPUT
    f_out, w_out, h_out = textbox(300, 240, [
        "Черга OUTPUT (vb2_queue)",
        "V4L2_BUF_TYPE_VIDEO_OUTPUT",
        "Вхідні кадри / стиснений потік від програми",
        "Операції: VIDIOC_QBUF / VIDIOC_DQBUF",
        "Стан буферів: QUEUED → ACTIVE → DONE"
    ], size=13, pad=14, fill=WARM, stroke=LINE)
    p.append(f_out)

    # Права колонка в ядрі: Черга CAPTURE
    f_cap, w_cap, h_cap = textbox(800, 240, [
        "Черга CAPTURE (vb2_queue)",
        "V4L2_BUF_TYPE_VIDEO_CAPTURE",
        "Порожні буфери під готовий результат",
        "Операції: VIDIOC_QBUF / VIDIOC_DQBUF",
        "Стан буферів: QUEUED → ACTIVE → DONE"
    ], size=13, pad=14, fill=GREEN, stroke=LINE)
    p.append(f_cap)

    # Стрілки між Userspace та чергами
    p.append(arrow(430, 105, 300, 165))
    p.append(arrow(800, 165, 670, 105))

    # Планувальник завдань M2M
    f_sched, w_s, h_s = textbox(550, 390, [
        "Каркас v4l2-mem2mem (Планувальник завдань)",
        "struct v4l2_m2m_dev & черга робіт job_queue",
        "Перевірка: є буфер в OUTPUT І є буфер в CAPTURE?",
        "Виклик драйвера: ops->device_run(ctx)"
    ], size=13, pad=15, fill=PURPLE, stroke=LINE, bold=True)
    p.append(f_sched)

    p.append(arrow(300, 315, 450, 345))
    p.append(arrow(800, 315, 650, 345))

    # Нижній шар: Апаратний блок
    f_hw, w_hw, h_hw = textbox(550, 560, [
        "Апаратний блок прискорювача (VPU / Кодек / Масштабувач / CSC)",
        "1. DMA Read: зчитує вхідний кадр з пам'яті (OUTPUT buf)",
        "2. Апаратне обчислення / декодування / масштабування матрицею",
        "3. DMA Write: записує результат у пам'ять (CAPTURE buf)"
    ], size=13, pad=16, fill=GREY, stroke=LINE)
    p.append(f_hw)

    p.append(arrow(550, 445, 550, 495))

    # Зворотний зв'язок: Переривання
    f_irq, w_irq, h_irq = textbox(550, 670, [
        "Апаратне переривання (IRQ) → Обробник драйвера: v4l2_m2m_buf_done() + v4l2_m2m_job_finish()",
        "Пробудження epoll/poll (POLLIN на CAPTURE, POLLOUT на OUTPUT)"
    ], size=12, pad=10, fill=RED, stroke=POS, sw=1.3)
    p.append(f_irq)

    p.append(arrow(550, 625, 550, 645))

    render(os.path.join(IMG, 'm2m-architecture.svg'), W, H, *p,
           title="Архітектура V4L2 M2M: дві черги на єдиному дескрипторі файлу")


# ── 2. Життєвий цикл завдання M2M (Job Lifecycle) ──────────────────────────
def fig_m2m_job_lifecycle():
    W, H = 1100, 640
    p = []

    steps = [
        ("1. Подання буферів (Userspace)",
         "Програма викликає VIDIOC_QBUF для OUTPUT (вхідні дані)\nта VIDIOC_QBUF для CAPTURE (пам'ять під вихід).",
         BLUE),
        ("2. Реєстрація в контексті (Kernel M2M)",
         "vb2_qbuf() ставить буфери в черги ctx->q_data[SRC/DST].\nv4l2_m2m_buf_queue() додає контекст у чергу готових робіт.",
         WARM),
        ("3. Запуск обробки: ops->device_run()",
         "Коли апаратура вільна, планувальник вибирає контекст і викликає\ndevice_run(). Драйвер програмує DMA-регістри і запускає чип.",
         PURPLE),
        ("4. Асинхронне виконання в кремнії",
         "Прискорювач виконує DMA зчитування/запис автономно.\nЯдро не блокується, процес може виконувати іншу роботу.",
         GREY),
        ("5. Переривання та завершення (IRQ Bottom-Half)",
         "Апаратура генерує IRQ. Драйвер викликає v4l2_m2m_buf_done()\nта v4l2_m2m_job_finish(), плануючи наступне завдання.",
         RED),
        ("6. Отримання результату (Userspace)",
         "Дескриптор сигналізує POLLIN. Програма викликає VIDIOC_DQBUF\nі забирає оброблений кадр або стиснений пакет.",
         GREEN),
    ]

    y_start = 75
    y_step = 92
    for i, (title, desc, color) in enumerate(steps):
        cy = y_start + i * y_step
        f, w, h = textbox(550, cy, [title, desc], size=12, pad=10, fill=color, stroke=LINE, min_w=850)
        p.append(f)
        if i < len(steps) - 1:
            p.append(arrow(550, cy + h / 2 + 1, 550, cy + y_step - h / 2 - 1))

    render(os.path.join(IMG, 'm2m-job-lifecycle.svg'), W, H, *p,
           title="Послідовність виконання апаратного завдання v4l2-mem2mem")


# ── 3. Stateful vs Stateless відеодекодери ──────────────────────────────────
def fig_stateful_vs_stateless():
    W, H = 1100, 640
    p = []

    # Лівий блок: Stateful
    f_st_title, _, _ = textbox(280, 80, [
        "Stateful декодер (зі збереженням стану)",
        "Samsung MFC, Hantro G1, Coda, Venus"
    ], size=13, pad=12, fill=BLUE, stroke=LINE, bold=True, min_w=480)
    p.append(f_st_title)

    f_st_usr, _, _ = textbox(280, 185, [
        "Userspace (FFmpeg / GStreamer)",
        "Передає сирий потік бітів (Annex B / NAL)",
        "Не розбирає SPS/PPS/заголовки слайсів"
    ], size=12, pad=12, fill=FILL, stroke=LINE, min_w=480)
    p.append(f_st_usr)

    f_st_drv, _, _ = textbox(280, 310, [
        "Драйвер та V4L2 M2M черги",
        "OUTPUT: пакети бітстріму",
        "CAPTURE: готові неспрощені YUV кадри",
        "DRC події: V4L2_EVENT_SOURCE_CHANGE"
    ], size=12, pad=12, fill=WARM, stroke=LINE, min_w=480)
    p.append(f_st_drv)

    f_st_hw, _, _ = textbox(280, 470, [
        "Апаратура з мікроконтролером / прошивкою",
        "• Вбудований парсер бітстріму",
        "• Внутрішній менеджер буферів посилань (DPB)",
        "• Автоматичне виділення та трекінг кадрів"
    ], size=12, pad=14, fill=GREEN, stroke=LINE, min_w=480)
    p.append(f_st_hw)

    p.append(arrow(280, 120, 280, 145))
    p.append(arrow(280, 225, 280, 260))
    p.append(arrow(280, 360, 280, 410))

    # Правий блок: Stateless
    f_sl_title, _, _ = textbox(820, 80, [
        "Stateless декодер (без стану в ядрі)",
        "Rockchip RKVDEC, Allwinner Cedrus, RPi HEVC"
    ], size=13, pad=12, fill=BLUE, stroke=LINE, bold=True, min_w=480)
    p.append(f_sl_title)

    f_sl_usr, _, _ = textbox(820, 185, [
        "Userspace (Парсер кодека)",
        "Парсить SPS, PPS, матриці квантування,",
        "параметри слайсів і таблиці посилань DPB"
    ], size=12, pad=12, fill=FILL, stroke=LINE, min_w=480)
    p.append(f_sl_usr)

    f_sl_req, _, _ = textbox(820, 310, [
        "V4L2 Request API (/dev/mediaX)",
        "Атомарний запит зв'язує разом:",
        "1. V4L2 контроли (SPS/PPS/Slice metadata)",
        "2. OUTPUT буфер (payload слайса) + CAPTURE буфер"
    ], size=12, pad=12, fill=PURPLE, stroke=LINE, min_w=480)
    p.append(f_sl_req)

    f_sl_hw, _, _ = textbox(820, 470, [
        "Чистий обчислювальний прискорювач",
        "• Не має прошивки та парсера",
        "• Декодує рівно один слайс за параметрами ядра",
        "• Тотальний контроль та детермінізм"
    ], size=12, pad=14, fill=WARM, stroke=LINE, min_w=480)
    p.append(f_sl_hw)

    p.append(arrow(820, 120, 820, 145))
    p.append(arrow(820, 225, 820, 260))
    p.append(arrow(820, 360, 820, 410))

    # Порівняльний підсумок знизу
    f_sum, _, _ = textbox(550, 585, [
        "Stateful: простіший Userspace, складніша закрита прошивка чипа.",
        "Stateless: відкритий стек, нуль бінарних блобів, керування кожним кадром через Request API."
    ], size=12, pad=11, fill=GREY, stroke=MUTED, min_w=1020)
    p.append(f_sum)

    render(os.path.join(IMG, 'stateful-vs-stateless.svg'), W, H, *p,
           title="Архітектурне порівняння: Stateful та Stateless відеодекодери")


# ── 4. Динамічна зміна роздільності (DRC Flow) ─────────────────────────────
def fig_m2m_drc_sequence():
    W, H = 1100, 620
    p = []

    f1, _, _ = textbox(550, 70, [
        "1. Декодування потоку: OUTPUT черга приймає NAL-пакети, CAPTURE віддає YUV 1080p"
    ], size=13, pad=11, fill=BLUE, stroke=LINE, min_w=900)
    p.append(f1)

    f2, _, _ = textbox(550, 155, [
        "2. Новий SPS у бітстрімі: зміна роздільності на 4K (3840×2160) або оновлення буферів DPB"
    ], size=13, pad=11, fill=WARM, stroke=LINE, min_w=900)
    p.append(f2)
    p.append(arrow(550, 93, 550, 132))

    f3, _, _ = textbox(550, 240, [
        "3. Драйвер зупиняє CAPTURE чергу та надсилає V4L2_EVENT_SOURCE_CHANGE (POLLPRI)"
    ], size=13, pad=11, fill=RED, stroke=POS, min_w=900)
    p.append(f3)
    p.append(arrow(550, 178, 550, 217))

    f4, _, _ = textbox(550, 325, [
        "4. Userspace спустошує старі кадри (VIDIOC_DQBUF) і викликає VIDIOC_STREAMOFF(CAPTURE)"
    ], size=13, pad=11, fill=GREY, stroke=LINE, min_w=900)
    p.append(f4)
    p.append(arrow(550, 263, 550, 302))

    f5, _, _ = textbox(550, 410, [
        "5. Зчитування нових параметрів: VIDIOC_G_FMT(CAPTURE) повертає новий розмір та вирівнювання"
    ], size=13, pad=11, fill=PURPLE, stroke=LINE, min_w=900)
    p.append(f5)
    p.append(arrow(550, 348, 550, 387))

    f6, _, _ = textbox(550, 495, [
        "6. Перевиділення пулу: VIDIOC_REQBUFS(count=0) звільняє 1080p, REQBUFS(N) виділяє 4K буфери"
    ], size=13, pad=11, fill=WARM, stroke=LINE, min_w=900)
    p.append(f6)
    p.append(arrow(550, 433, 550, 472))

    f7, _, _ = textbox(550, 575, [
        "7. Перезапуск CAPTURE: VIDIOC_QBUF + VIDIOC_STREAMON(CAPTURE). Потік OUTPUT не переривався!"
    ], size=13, pad=11, fill=GREEN, stroke=LINE, bold=True, min_w=900)
    p.append(f7)
    p.append(arrow(550, 518, 550, 552))

    render(os.path.join(IMG, 'm2m-drc-sequence.svg'), W, H, *p,
           title="Послідовність динамічної зміни формату (DRC) у Stateful декодері")


if __name__ == "__main__":
    fig_m2m_architecture()
    fig_m2m_job_lifecycle()
    fig_stateful_vs_stateless()
    fig_m2m_drc_sequence()
    print("All figures generated successfully.")
