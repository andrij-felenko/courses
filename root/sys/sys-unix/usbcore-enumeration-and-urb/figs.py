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

def fig_usb_core_architecture():
    W, H = 1000, 680
    p = []

    # Title / Header
    f_hdr, _, _ = textbox(W / 2, 40, ["Трирівнева архітектура підсистеми USB у ядрі Linux"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Layer 1: Userspace
    f_usr, _, _ = textbox(W / 2, 110, ["Простір користувача (Userspace)", "Прикладні програми (lsusb, Wireshark, libusb) • sysfs (/sys/bus/usb/) • devtmpfs (/dev/bus/usb/)"], size=13, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_usr)

    # Layer 2: USB Device Drivers
    f_drv1, _, _ = textbox(250, 220, ["Класові драйвери пристроїв", "usb-storage, uvcvideo, usbhid, cdc-acm"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_drv1)

    f_drv2, _, _ = textbox(750, 220, ["Драйвери простору користувача", "usbfs ioctl / libusb claiming"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_drv2)

    # Layer 3: USB Core Subsystem
    f_core, _, _ = textbox(W / 2, 360, [
        "Ядро підсистеми USB (USB Core / usbcore)",
        "• Менеджер нумерації (Enumeration, hub_event)  • Маршрутизатор запитів URB",
        "• Управління живленням (Runtime PM & Autosuspend) • Розбір та валідація дескрипторів",
        "• Модель шини 'usb' та прив'язка struct usb_driver до struct usb_interface"
    ], size=13, bold=True, fill=WARM, stroke=LINE)
    p.append(f_core)

    # Layer 4: Host Controller Drivers
    f_hcd, _, _ = textbox(W / 2, 500, ["Драйвери хост-контролерів (HCD)", "xhci-hcd (USB 3.x/4) • ehci-hcd (USB 2.0) • ohci-hcd / uhci-hcd (USB 1.1)"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_hcd)

    # Layer 5: Hardware
    f_hw, _, _ = textbox(W / 2, 610, ["Апаратне забезпечення (Hardware)", "PCIe / SoC USB Host Controller (xHCI) ↔ Root Hub ↔ Фізичні пристрої USB"], size=13, fill=RED, stroke=LINE)
    p.append(f_hw)

    # Arrows
    p.append(arrow(W / 2 - 100, 140, 250, 195))
    p.append(arrow(W / 2 + 100, 140, 750, 195))
    p.append(arrow(250, 245, 380, 310))
    p.append(arrow(750, 245, 620, 310))
    p.append(arrow(W / 2, 410, W / 2, 475))
    p.append(arrow(W / 2, 525, W / 2, 585))

    out_path = os.path.join(IMG, 'usb-core-architecture.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_urb_lifecycle():
    W, H = 1080, 620
    p = []

    f_hdr, _, _ = textbox(W / 2, 35, ["Життєвий цикл та стан об'єкта USB Request Block (URB)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Step 1: Alloc & Init
    f_st1, _, _ = textbox(170, 130, ["1. Виділення та ініціалізація", "usb_alloc_urb()", "usb_fill_bulk_urb() / control / int", "Налаштування буфера та complete callback"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_st1)

    # Step 2: Submit
    f_st2, _, _ = textbox(540, 130, ["2. Відправка в ядро", "usb_submit_urb()", "Перевірка параметрів та прапорців", "Передача до HCD (urb->status = -EINPROGRESS)"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_st2)

    # Step 3: HCD Schedule & DMA
    f_st3, _, _ = textbox(910, 130, ["3. Планування в HCD", "Формування кільця TRB (xHCI)", "DMA-передача даних по шині", "Фізичний обмін пакетами"], size=12, fill=PURPLE, stroke=LINE)
    p.append(f_st3)

    # Step 4: IRQ & Complete
    f_st4, _, _ = textbox(910, 360, ["4. Переривання та Callback", "Апаратне IRQ від контролера", "Виклик urb->complete(urb)", "Контекст softirq / tasklet"], size=12, fill=WARM, stroke=LINE)
    p.append(f_st4)

    # Step 5: Decision (Free or Resubmit)
    f_st5, _, _ = textbox(540, 360, ["5. Завершення або повторна відправка", "Перевірка status (0 = ОК, -ENOENT)", "Повторна відправка usb_submit_urb()", "або виклик usb_free_urb()"], size=12, fill=RED, stroke=LINE)
    p.append(f_st5)

    # Arrows
    p.append(arrow(320, 130, 390, 130))
    p.append(arrow(690, 130, 765, 130))
    p.append(arrow(910, 200, 910, 290))
    p.append(arrow(765, 360, 690, 360))
    p.append(arrow(540, 290, 540, 200)) # Resubmit loop arrow

    # Annotations (placed nicely away from arrows)
    p.append(text(620, 245, "Цикл повторної відправки (Resubmit)", size=11, color=MUTED, bold=True))

    out_path = os.path.join(IMG, 'urb-lifecycle.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_usb_enumeration_pipeline():
    W, H = 1050, 680
    p = []

    f_hdr, _, _ = textbox(W / 2, 35, ["Конвеєр нумерації пристрою USB (Enumeration Pipeline)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Step 1
    f_s1, _, _ = textbox(170, 120, ["1. Виявлення підключення", "Переривання змінення стану порту", "Сигнал на D+/D- ↔ Hub Event", "Запуск hub_event() у робочій черзі"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_s1)

    # Step 2
    f_s2, _, _ = textbox(525, 120, ["2. Портовий скид (Port Reset)", "Скидання лінії в стан SE0 (10 мс)", "Встановлення швидкості (LS/FS/HS/SS)", "Призначення адреси 0 за замовчуванням"], size=12, fill=GREEN, stroke=LINE)
    p.append(f_s2)

    # Step 3
    f_s3, _, _ = textbox(880, 120, ["3. Читання перших 8 байтів", "GET_DESCRIPTOR (Device)", "Визначення розміру bMaxPacketSize0", "Повторне скидання порту для стабілізації"], size=12, fill=WARM, stroke=LINE)
    p.append(f_s3)

    # Step 4
    f_s4, _, _ = textbox(880, 340, ["4. Призначення адреси шини", "SET_ADDRESS (Адреса N: 1..127)", "Пристрій переходить у стан Addressed", "Всі наступні URB адресовані N"], size=12, fill=PURPLE, stroke=LINE)
    p.append(f_s4)

    # Step 5
    f_s5, _, _ = textbox(525, 340, ["5. Повне зчитування дескрипторів", "Зчитування Device Descriptor (18B)", "Зчитування Config/Interface/Endpoint", "Створення системних структур у ядрі"], size=12, fill=BLUE, stroke=LINE)
    p.append(f_s5)

    # Step 6
    f_s6, _, _ = textbox(170, 340, ["6. Пошук драйвера & Probe", "Матчинг id_table з Vendor/Product ID", "Створення нод у sysfs (/sys/bus/usb/)", "Виклик driver->probe(interface)"], size=12, fill=RED, stroke=LINE)
    p.append(f_s6)

    # Connecting arrows
    p.append(arrow(320, 120, 370, 120))
    p.append(arrow(680, 120, 730, 120))
    p.append(arrow(880, 190, 880, 270))
    p.append(arrow(730, 340, 680, 340))
    p.append(arrow(370, 340, 320, 340))

    out_path = os.path.join(IMG, 'usb-enumeration-pipeline.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    fig_usb_core_architecture()
    fig_urb_lifecycle()
    fig_usb_enumeration_pipeline()
