# -*- coding: utf-8 -*-
"""Фігури до теми «libcamera: користувацький стек камери над V4L2 та Media Controller»."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_uvc_vs_embedded():
    """Порівняння архітектури UVC-камери та вбудованої CSI-2 камери з ISP."""
    W, H = 880, 360
    f = []

    # Верхній блок: UVC камера
    f.append(rect(15, 15, 850, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(440, 35, "Класична UVC USB-камера (всередині корпусу апаратний ASIC)", size=13, bold=True, color="#1e293b"))

    f.append(rect(30, 50, 160, 85, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=6))
    f.append(mtext(110, 78, "Оптичний сенсор\n+ Вбудований ISP\n(3A в залізі)", size=11, bold=True, color="#334155"))

    f.append(rect(220, 50, 140, 85, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=6))
    f.append(mtext(290, 83, "USB Device\nController", size=11, bold=True, color="#334155"))

    f.append(rect(430, 50, 190, 85, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(525, 78, "Ядро Linux: uvcvideo\n/dev/video0\n(V4L2 Capture Node)", size=11, bold=True, color="#1e40af"))

    f.append(rect(690, 50, 155, 85, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(mtext(767, 83, "Застосунок\n(OpenCV / браузер)", size=11, bold=True, color="#14532d"))

    f.append(arrow(190, 92, 220, 92, color="#475569", sw=1.8))
    f.append(arrow(360, 92, 430, 92, color="#475569", sw=1.8))
    f.append(text(395, 82, "USB", size=10, bold=True, color="#475569"))
    f.append(arrow(620, 92, 690, 92, color="#475569", sw=1.8))
    f.append(text(655, 82, "YUYV", size=10, bold=True, color="#2563eb"))

    # Нижній блок: Вбудована CSI-2 камера з відкритим ISP
    f.append(rect(15, 175, 850, 170, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    f.append(text(440, 195, "Вбудована MIPI CSI-2 камера (розподілений конвеєр SoC ISP та програмні 3A)", size=13, bold=True, color="#1e293b"))

    f.append(rect(30, 210, 150, 115, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=6))
    f.append(mtext(105, 238, "Сирий сенсор\n(RAW Bayer 10/12b)\n+ I2C / VCM Мотор\n(Sony IMX477 тощо)", size=10, bold=True, color="#991b1b"))

    f.append(rect(210, 210, 190, 115, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    f.append(mtext(305, 235, "SoC Апаратний ISP\n• CSI-2 Receiver\n• Demosaic / LSC / 3DNR\n• 3A Statistics Engine\n• Scaler / DMA Write", size=10, bold=True, color="#92400e"))

    f.append(rect(430, 210, 190, 115, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(525, 238, "Ядро Linux\n• /dev/media0 (MC)\n• /dev/v4l-subdevX\n• Media Request API\n• dma-buf пам'ять", size=10, bold=True, color="#1e40af"))

    f.append(rect(650, 210, 200, 115, fill="#fae8ff", stroke="#a855f7", sw=1.2, rx=6))
    f.append(mtext(750, 238, "libcamera (User Space)\n• Pipeline Handler\n• IPA Sandbox (3A AE/AWB)\n• Request-based API\n• Zero-Copy dma-buf", size=10, bold=True, color="#6b21a8"))

    f.append(arrow(180, 267, 210, 267, color="#dc2626", sw=1.8))
    f.append(text(195, 257, "CSI-2", size=9, bold=True, color="#dc2626"))

    f.append(arrow(400, 267, 430, 267, color="#d97706", sw=1.8))
    f.append(text(415, 257, "DMA", size=9, bold=True, color="#d97706"))

    f.append(arrow(620, 267, 650, 267, color="#2563eb", sw=1.8))
    f.append(text(635, 257, "ioctl", size=9, bold=True, color="#2563eb"))

    render(os.path.join(IMG, 'uvc-vs-embedded-pipeline.svg'), W, H, *f)


def fig_libcamera_architecture():
    """Архітектурні шари libcamera: застосунки, ядро libcamera, Pipeline Handlers, IPA та ядро Linux."""
    W, H = 880, 400
    f = []

    # Шар 1: Застосунки та інтеграційні мости
    f.append(rect(20, 15, 840, 65, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(75, 42, "Application Layer:", size=11, bold=True, color="#166534"))
    f.append(rect(140, 25, 150, 45, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(mtext(215, 45, "Власні C++ Програми\n(libcamera API)", size=10, bold=True, color="#14532d"))
    f.append(rect(310, 25, 160, 45, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(mtext(390, 45, "GStreamer Елемент\n(libcamerasrc)", size=10, bold=True, color="#14532d"))
    f.append(rect(490, 25, 170, 45, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(mtext(575, 45, "PipeWire Мультимедіа\n(SPA Camera Plugin)", size=10, bold=True, color="#14532d"))
    f.append(rect(680, 25, 165, 45, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(mtext(762, 45, "v4l2-compat Wrapper\n(LD_PRELOAD /dev/video)", size=10, bold=True, color="#14532d"))

    # Стрілка вниз від App до Core
    f.append(arrow(440, 80, 440, 105, color="#16a34a", sw=2))

    # Шар 2: libcamera Core API
    f.append(rect(20, 105, 840, 75, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=8))
    f.append(text(120, 130, "libcamera Core C++ API", size=12, bold=True, color="#1e40af"))
    f.append(rect(190, 115, 140, 55, fill="#ffffff", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(260, 138, "CameraManager\n& Camera Object", size=10, bold=True, color="#1e3a8a"))
    f.append(rect(350, 115, 150, 55, fill="#ffffff", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(425, 138, "CameraConfiguration\n& StreamConfig", size=10, bold=True, color="#1e3a8a"))
    f.append(rect(520, 115, 150, 55, fill="#ffffff", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(595, 138, "Request & FrameBuffer\n(dma-buf wrapper)", size=10, bold=True, color="#1e3a8a"))
    f.append(rect(690, 115, 155, 55, fill="#ffffff", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(767, 138, "ControlList & Properties\n(Exposure, Gain, AF)", size=10, bold=True, color="#1e3a8a"))

    # Стрілка вниз до Pipeline Handler
    f.append(arrow(340, 180, 340, 205, color="#2563eb", sw=2))

    # Шар 3: Pipeline Handlers та IPA Sandbox
    f.append(rect(20, 205, 540, 95, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=8))
    f.append(text(140, 227, "Pipeline Handlers (Драйвери SoC)", size=11, bold=True, color="#6b21a8"))
    f.append(rect(35, 237, 115, 50, fill="#ffffff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(mtext(92, 258, "RPi Handler\n(Broadcom / Pi 5)", size=9, bold=True, color="#581c87"))
    f.append(rect(160, 237, 115, 50, fill="#ffffff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(mtext(217, 258, "IPU3 Handler\n(Intel Surface)", size=9, bold=True, color="#581c87"))
    f.append(rect(285, 237, 125, 50, fill="#ffffff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(mtext(347, 258, "RkISP1 / i.MX8\n(Rockchip / NXP)", size=9, bold=True, color="#581c87"))
    f.append(rect(420, 237, 125, 50, fill="#ffffff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(mtext(482, 258, "Simple & UVC\n(Generic Video)", size=9, bold=True, color="#581c87"))

    # Блок IPA Sandbox поруч
    f.append(rect(580, 205, 280, 95, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=8))
    f.append(text(720, 227, "IPA Sandbox (Ізольований процес 3A)", size=11, bold=True, color="#9a3412"))
    f.append(rect(595, 237, 250, 50, fill="#ffffff", stroke="#ea580c", sw=1.2, rx=6))
    f.append(mtext(720, 258, "3A Алгоритми: AE / AWB / AF / LSC\n(IPC через Unix Socket + memfd + seccomp)", size=9, bold=True, color="#7c2d12"))

    # IPC стрілка двостороння між Pipeline Handler та IPA
    f.append(arrow(560, 252, 580, 252, color="#ea580c", sw=1.8))
    f.append(arrow(580, 267, 560, 267, color="#ea580c", sw=1.8))

    # Стрілка вниз до ядра
    f.append(arrow(340, 300, 340, 325, color="#9333ea", sw=2))

    # Шар 4: Linux Kernel
    f.append(rect(20, 325, 840, 60, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=8))
    f.append(text(100, 357, "Linux Kernel Subsystems:", size=11, bold=True, color="#334155"))
    f.append(rect(190, 335, 150, 42, fill="#ffffff", stroke="#475569", sw=1.2, rx=6))
    f.append(mtext(265, 355, "Media Controller\n(/dev/mediaX)", size=10, bold=True, color="#1e293b"))
    f.append(rect(360, 335, 150, 42, fill="#ffffff", stroke="#475569", sw=1.2, rx=6))
    f.append(mtext(435, 355, "V4L2 Subdevices\n(/dev/v4l-subdevX)", size=10, bold=True, color="#1e293b"))
    f.append(rect(530, 335, 150, 42, fill="#ffffff", stroke="#475569", sw=1.2, rx=6))
    f.append(mtext(605, 355, "V4L2 Video Nodes\n(/dev/videoX vb2)", size=10, bold=True, color="#1e293b"))
    f.append(rect(700, 335, 145, 42, fill="#ffffff", stroke="#475569", sw=1.2, rx=6))
    f.append(mtext(772, 355, "Media Request API\n& dma-buf Framework", size=10, bold=True, color="#1e293b"))

    render(os.path.join(IMG, 'libcamera-architecture-layers.svg'), W, H, *f)


def fig_request_lifecycle():
    """Життєвий цикл об'єкта Request та синхронізація кадрів у libcamera."""
    W, H = 880, 270
    f = []

    # Стан 1: Створення та наповнення
    f.append(rect(20, 60, 180, 110, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(110, 85, "1. Request Created", size=12, bold=True, color="#0f172a"))
    f.append(mtext(110, 115, "• Camera::createRequest()\n• Прив'язка FrameBuffer\n• Заповнення ControlList\n(Exposure, Gain, Focus)", size=10, color="#334155"))

    # Стан 2: Постановка в чергу
    f.append(rect(240, 60, 180, 110, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    f.append(text(330, 85, "2. Queued in Camera", size=12, bold=True, color="#1e40af"))
    f.append(mtext(330, 115, "• Camera::queueRequest()\n• Pipeline Handler обробка\n• Виділення request_fd\n(MEDIA_IOC_REQUEST_ALLOC)", size=10, color="#1e3a8a"))

    # Стан 3: Обробка ядром та IPA
    f.append(rect(460, 60, 180, 110, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    f.append(text(550, 85, "3. Processing & 3A", size=12, bold=True, color="#92400e"))
    f.append(mtext(550, 115, "• DMA запис сенсора/ISP\n• Статистика до IPA 3A\n• Розрахунок наступного кадру\n• V4L2 DQBUF переривання", size=10, color="#78350f"))

    # Стан 4: Завершення запиту
    f.append(rect(680, 60, 180, 110, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=8))
    f.append(text(770, 85, "4. Request Completed", size=12, bold=True, color="#14532d"))
    f.append(mtext(770, 115, "• Сигнал requestCompleted\n• Зчитування FrameMetadata\n• Передача dma-buf до GPU\n• Request::reuse()", size=10, color="#166534"))

    # Стрілки прямого переходу
    f.append(arrow(200, 115, 240, 115, color="#3b82f6", sw=2))
    f.append(arrow(420, 115, 460, 115, color="#d97706", sw=2))
    f.append(arrow(640, 115, 680, 115, color="#16a34a", sw=2))

    # Зворотна петля перевикористання Request
    f.append(line(770, 170, 770, 220, color="#64748b", sw=1.8, dash="4,4"))
    f.append(line(770, 220, 110, 220, color="#64748b", sw=1.8, dash="4,4"))
    f.append(arrow(110, 220, 110, 170, color="#64748b", sw=1.8))
    f.append(text(440, 240, "Цикл перевикористання буферів та запитів без повторного виділення пам'яті (Request::reuse)", size=11, bold=True, color="#475569"))

    render(os.path.join(IMG, 'request-buffer-lifecycle.svg'), W, H, *f)


def fig_compatibility_pipewire():
    """Стек сумісності libcamera: GStreamer, v4l2-compat та мультиплексування PipeWire."""
    W, H = 880, 300
    f = []

    # Верхній рівень: Різні типи клієнтів
    f.append(rect(20, 20, 240, 70, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=6))
    f.append(mtext(140, 48, "Застарілі V4L2 програми\n(Firefox, Chromium, Zoom, Skype)", size=10, bold=True, color="#1e293b"))

    f.append(rect(300, 20, 260, 70, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=6))
    f.append(mtext(430, 48, "Мультимедійні пайплайни\n(GStreamer, OpenCV, ffmpeg)", size=10, bold=True, color="#1e293b"))

    f.append(rect(600, 20, 260, 70, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=6))
    f.append(mtext(730, 48, "Пісочниці Wayland / Flatpak\n(XDG Desktop Portal Camera)", size=10, bold=True, color="#1e293b"))

    # Середній рівень: Мости сумісності
    f.append(rect(20, 120, 240, 55, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=6))
    f.append(mtext(140, 145, "v4l2-compat.so\n(LD_PRELOAD ioctl перехоплення)", size=10, bold=True, color="#991b1b"))

    f.append(rect(300, 120, 260, 55, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    f.append(mtext(430, 145, "libcamerasrc Плагін\n(GStreamer Source Element)", size=10, bold=True, color="#92400e"))

    f.append(rect(600, 120, 260, 55, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=6))
    f.append(mtext(730, 145, "PipeWire Мультиплексор\n(SPA libcamera source plugin)", size=10, bold=True, color="#1e40af"))

    # Стрілки від верху до середини
    f.append(arrow(140, 90, 140, 120, color="#dc2626", sw=1.8))
    f.append(arrow(430, 90, 430, 120, color="#d97706", sw=1.8))
    f.append(arrow(730, 90, 730, 120, color="#2563eb", sw=1.8))

    # Нижній рівень: Єдиний libcamera Core
    f.append(rect(20, 210, 840, 75, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=8))
    f.append(text(440, 235, "libcamera Core Subsystem (Єдина точка контролю апаратури)", size=12, bold=True, color="#581c87"))
    f.append(mtext(440, 260, "CameraManager ─── Pipeline Handlers ─── Media Controller & V4L2 Subdevs ─── Hardware CSI-2 & ISP", size=10, bold=True, color="#6b21a8"))

    # Стрілки від мостів до libcamera Core
    f.append(arrow(140, 175, 200, 210, color="#9333ea", sw=1.8))
    f.append(arrow(430, 175, 430, 210, color="#9333ea", sw=1.8))
    f.append(arrow(730, 175, 670, 210, color="#9333ea", sw=1.8))

    render(os.path.join(IMG, 'compatibility-and-pipewire-stack.svg'), W, H, *f)


def main():
    fig_uvc_vs_embedded()
    fig_libcamera_architecture()
    fig_request_lifecycle()
    fig_compatibility_pipewire()


if __name__ == '__main__':
    main()
