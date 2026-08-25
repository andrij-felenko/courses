# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE   = "#eaf0fd"
GREEN  = "#eaf6ef"
WARM   = "#fff6e5"
RED    = "#fdecea"
GREY   = "#eceff1"
PURPLE = "#f3e8ff"

def fig_iio_architecture():
    W, H = 1000, 680
    p = []

    # Title / Header
    f_hdr, _, _ = textbox(W / 2, 40, ["Архітектура підсистеми Industrial I/O (IIO) у ядрі Linux"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Layer 1: Userspace
    cx_user = W / 2
    f_user_box, _, _ = textbox(cx_user, 120, [
        "Простір користувача (User Space)",
        "libiio / Додатки / Утиліти (iio-sensor-proxy, lsiio)"
    ], size=14, bold=True, fill=BLUE, stroke=LINE, min_w=600)
    p.append(f_user_box)

    # Interfaces between Userspace and Kernel
    # 3 Channels: Sysfs, Char Dev, Event FD
    x_sysfs, y_if = 220, 240
    x_cdev = 500
    x_evt = 780

    f_sysfs, _, _ = textbox(x_sysfs, y_if, [
        "Sysfs Інтерфейс",
        "/sys/bus/iio/devices/iio:deviceX/",
        "Покенальні *_raw, *_scale, *_offset"
    ], size=12, fill=GREEN, stroke=LINE)
    p.append(f_sysfs)

    f_cdev, _, _ = textbox(x_cdev, y_if, [
        "Символьний пристрій",
        "/dev/iio:deviceX",
        "Потік буферизованих даних (kfifo)"
    ], size=12, fill=GREEN, stroke=LINE)
    p.append(f_cdev)

    f_evt, _, _ = textbox(x_evt, y_if, [
        "Event File Descriptor",
        "ioctl(IIO_GET_EVENT_FD_IOCTL)",
        "Асинхронні події (порогові переривання)"
    ], size=12, fill=GREEN, stroke=LINE)
    p.append(f_evt)

    # Arrows Userspace <-> Interfaces
    p.append(arrow(300, 150, x_sysfs, y_if - 30))
    p.append(arrow(cx_user, 150, x_cdev, y_if - 30))
    p.append(arrow(700, 150, x_evt, y_if - 30))

    # Layer 2: IIO Core Kernel Subsystem
    y_core = 390
    f_core_box, _, _ = textbox(cx_user, y_core, [
        "Ядро підсистеми IIO (IIO Core Subsystem)",
        "struct iio_dev  |  struct iio_info  |  struct iio_chan_spec",
        "Менеджер буферів (kfifo/industrialio-buffer)  |  Тригери (IIO Triggers)  |  Подмиєвий каскад"
    ], size=13, bold=True, fill=PURPLE, stroke=LINE, min_w=850)
    p.append(f_core_box)

    # Arrows Interfaces <-> IIO Core
    p.append(arrow(x_sysfs, y_if + 30, x_sysfs, y_core - 40))
    p.append(arrow(x_cdev, y_if + 30, x_cdev, y_core - 40))
    p.append(arrow(x_evt, y_if + 30, x_evt, y_core - 40))

    # Layer 3: Hardware Drivers
    y_drv = 530
    f_drv_box, _, _ = textbox(cx_user, y_drv, [
        "Драйвери пристроїв IIO (IIO Device Drivers)",
        "Драйвери ADC/DAC (ADS1115, AD7991), Акселерометрів (MPU6050, ADXL345), Сенсорів тиску/температури (BMP280)",
        "Обслуговування шин (I2C, SPI, Platform) та переривань (IRQ Bottom-Half)"
    ], size=12, fill=GREY, stroke=LINE, min_w=850)
    p.append(f_drv_box)

    p.append(arrow(cx_user, y_core + 40, cx_user, y_drv - 30))

    # Layer 4: Physical Hardware
    y_hw = 630
    f_hw_box, _, _ = textbox(cx_user, y_hw, [
        "Апаратне забезпечення (Physical Hardware)",
        "Аналогові датчики, АЦП, ЦАП, Інерційні модулі (IMU), Шинні контролери SPI / I2C"
    ], size=12, fill=RED, stroke=LINE, min_w=850)
    p.append(f_hw_box)

    p.append(arrow(cx_user, y_drv + 25, cx_user, y_hw - 20))

    render(os.path.join(IMG, 'iio-arch.svg'), W, H, *p)

def fig_iio_buffer_trigger_flow():
    W, H = 1050, 500
    p = []

    f_hdr, _, _ = textbox(W / 2, 35, ["Конвеєр високошвидкісної буферизації та тригерів IIO"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Step 1: Trigger Event
    x1, y1 = 160, 140
    f1, _, _ = textbox(x1, y1, [
        "1. Джерело тригера",
        "Апаратне переривання (IRQ)",
        "або hrtimer / sysfs trigger"
    ], size=12, fill=RED, stroke=LINE)
    p.append(f1)

    # Step 2: IIO Trigger Handler
    x2, y2 = 450, 140
    f2, _, _ = textbox(x2, y2, [
        "2. iio_trigger_poll()",
        "Викликає iio_pollfunc_store_time()",
        "Фіксація 64-біт таймстампа (ns)"
    ], size=12, fill=PURPLE, stroke=LINE)
    p.append(f2)

    # Step 3: Driver Top/Bottom Half Read
    x3, y3 = 840, 140
    f3, _, _ = textbox(x3, y3, [
        "3. Top/Bottom Half драйвера",
        "Зчитування сирих даних каналів",
        "через SPI/I2C/DMA у буфер"
    ], size=12, fill=GREEN, stroke=LINE)
    p.append(f3)

    p.append(arrow(x1 + 100, y1, x2 - 120, y2))
    p.append(arrow(x2 + 120, y2, x3 - 110, y3))

    # Step 4: Push to kfifo
    x4, y4 = 840, 320
    f4, _, _ = textbox(x4, y4, [
        "4. iio_push_to_buffers_with_timestamp()",
        "Запис упакованої структури даних",
        "у кільцевий буфер kfifo"
    ], size=12, fill=GREEN, stroke=LINE)
    p.append(f4)

    p.append(arrow(x3, y3 + 30, x4, y4 - 30))

    # Step 5: Waitqueue / Poll notification
    x5, y5 = 450, 320
    f5, _, _ = textbox(x5, y5, [
        "5. wake_up_interruptible()",
        "Розбудження процесів,",
        "очікуючих у poll()/select()"
    ], size=12, fill=BLUE, stroke=LINE)
    p.append(f5)

    p.append(arrow(x4 - 140, y4, x5 + 120, y5))

    # Step 6: User space read
    x6, y6 = 160, 320
    f6, _, _ = textbox(x6, y6, [
        "6. Простір користувача",
        "read(/dev/iio:deviceX)",
        "Отримання масиву семплів з таймстампами"
    ], size=12, fill=BLUE, stroke=LINE)
    p.append(f6)

    p.append(arrow(x5 - 120, y5, x6 + 110, y6))

    render(os.path.join(IMG, 'iio-buffer-trigger-flow.svg'), W, H, *p)

if __name__ == "__main__":
    fig_iio_architecture()
    fig_iio_buffer_trigger_flow()
    print("Figures generated successfully.")
