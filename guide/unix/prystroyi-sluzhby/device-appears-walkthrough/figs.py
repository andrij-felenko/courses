# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми device-appears-walkthrough."""

import os
import sys

# Шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_device_plug_full_pipeline():
    """Повний наскрізний ланцюг від фізичного під'єднання до ноди у /dev."""
    w, h = 920, 840
    frags = []

    # Рівні системи (кольорові підкладки)
    frags.append(rect(20, 20, 880, 100, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(40, 42, "1. АПАРАТНИЙ РІВЕНЬ (Hardware / USB PHY / Контролер шини)", size=12, color=POS, anchor="start", bold=True))

    frags.append(rect(20, 130, 880, 360, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(40, 152, "2. ПРОСТІР ЯДРА (Kernel Space / Драйвери / sysfs / Netlink)", size=12, color=FIELD, anchor="start", bold=True))

    frags.append(rect(20, 500, 880, 210, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(40, 522, "3. ПРОСТІР КОРИСТУВАЧА (User Space / systemd-udevd / Правила)", size=12, color=NEG, anchor="start", bold=True))

    frags.append(rect(20, 720, 880, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 742, "4. ДОСТУП ЗАСТОСУНКУ (Application / devtmpfs / /dev Nodes)", size=12, color=MUTED, anchor="start", bold=True))

    # Ліва частина: Апаратний рівень і вхід у ядро
    frags.append(fitbox(40, 55, 400, 55, "Замикання контактів: VBUS/GND та D+/D-\nПідтяжка pull-up 1.5 кОм змінює диференційну напругу", size=11, fill="#ffffff", stroke="#fca5a5", bold=True))
    frags.append(arrow(450, 82, 490, 82, color=POS, sw=2))

    frags.append(fitbox(490, 55, 390, 55, "Хост-контролер xHCI генерує переривання IRQ\nCPU перемикається на обробник ISR ядра", size=11, fill="#ffffff", stroke="#fca5a5", bold=True))
    frags.append(arrow(685, 110, 685, 165, color=POS, sw=2))

    # Рівень ядра: Нумерація, kobject, uevent
    frags.append(fitbox(490, 165, 390, 60, "Робоча черга ядра: hub_event()\nСкидання лінії (Reset) -> Читання дескрипторів EP0\nОтримання VID/PID та конфігурацій інтерфейсів", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(490, 195, 430, 195, color=LINE, sw=2))

    frags.append(fitbox(40, 165, 390, 60, "Створення struct device та kobject\nРеєстрація у дереві /sys/devices/pci.../usb...\nСтворення атрибутів kernfs (idVendor, idProduct)", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(235, 225, 235, 260, color=LINE, sw=2))

    frags.append(fitbox(40, 260, 390, 65, "Виклик kobject_uevent(&dev->kobj, KOBJ_ADD)\nФормування рядків: ACTION=add, DEVPATH=...,\nSUBSYSTEM=usb, MODALIAS=usb:v...p...", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(430, 292, 490, 292, color=FIELD, sw=2.5))

    frags.append(fitbox(490, 260, 390, 65, "Широкомовна розсилка через Netlink\nСокет NETLINK_KOBJECT_UEVENT (multicast group 1)\nПакет потрапляє в чергу сокета простору користувача", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(685, 325, 685, 375, color=NEG, sw=2.5))

    # Паралельні ядерні структури та зв'язування драйвера
    frags.append(fitbox(490, 375, 390, 75, "Автозавантаження модуля & probe():\nЯдро або udevd завантажує .ko (наприклад cdc_acm / ftdi_sio)\nДрайвер зв'язується з пристроєм: usb_register_driver()\nВикликається driver->probe(), ініціалізація буферів", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(490, 412, 430, 412, color=LINE, sw=2))

    frags.append(fitbox(40, 375, 390, 75, "devtmpfs: реєстрація ноди пристрою\nДрайвер викликає device_create() з major:minor\ndevtmpfs_create_node() створює сирий файл у /dev", size=11, fill="#ffffff", stroke="#86efac", bold=True))
    frags.append(arrow(235, 450, 235, 535, color=NEG, sw=2))

    # Рівень простору користувача: systemd-udevd
    frags.append(fitbox(40, 535, 400, 65, "systemd-udevd отримує Netlink-повідомлення\nПарсить змінні оточення (ACTION, DEVPATH, SUBSYSTEM)\nВиділяє робочий потік udev worker для обробки події", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))
    frags.append(arrow(440, 567, 490, 567, color=LINE, sw=2))

    frags.append(fitbox(490, 535, 390, 65, "Оцінка правил: /usr/lib/udev/rules.d/\nЗіставлення ATTR, запуск IMPORT{builtin} = 'usb_id'\nФормування властивостей ID_VENDOR_ID, ID_MODEL_ID", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))
    frags.append(arrow(685, 600, 685, 630, color=LINE, sw=2))

    frags.append(fitbox(490, 630, 390, 65, "Призначення прав та стабільних симлінків\nВстановлення GROUP=\"dialout\", MODE=\"0660\"\nСтворення /dev/serial/by-id/usb-FTDI... -> /dev/ttyUSB0", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))
    frags.append(arrow(490, 662, 440, 662, color=LINE, sw=2))

    frags.append(fitbox(40, 630, 400, 65, "Оновлення бази udev (/run/udev/data/+subsystem:dev)\nСповіщення systemd через sd_notify / D-Bus (TAG+=\"systemd\")\nПристрій переходить у стан готового до роботи", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))
    frags.append(arrow(235, 695, 235, 750, color=MUTED, sw=2))

    # Рівень застосунку
    frags.append(fitbox(40, 750, 400, 55, "Застосунок відкриває стабільний симлінк\nopen(\"/dev/serial/by-id/usb-FTDI...\", O_RDWR)\nVFS перенаправляє запит на cdev_open() драйвера", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))
    frags.append(arrow(440, 777, 490, 777, color=FIELD, sw=2))

    frags.append(fitbox(490, 750, 390, 55, "Прямий ввід-вивід із залізом встановлено\nПотік read()/write() передає пакети через USB URB", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    render(os.path.join(OUT_DIR, "device-plug-full-pipeline.svg"), w, h, *frags)


def fig_modalias_to_driver_matching():
    """Схема формування рядка MODALIAS та зіставлення з модулями ядра."""
    w, h = 880, 540
    frags = []

    # Верхній блок: Апаратні дескриптори заліза
    frags.append(rect(20, 20, 840, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(40, 42, "1. АПАРАТНІ ІДЕНТИФІКАТОРИ З ДЕСКРИПТОРІВ USB (Дескриптор пристрою та інтерфейсу)", size=12, color=MUTED, anchor="start", bold=True))

    frags.append(fitbox(40, 55, 255, 60, "Дескриптор пристрою:\nidVendor = 0x0403 (FTDI)\nidProduct = 0x6001 (FT232R)\nbcdDevice = 0x0600", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(310, 55, 265, 60, "Класи пристрою:\nbDeviceClass = 0x00\nbDeviceSubClass = 0x00\nbDeviceProtocol = 0x00", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    frags.append(fitbox(590, 55, 255, 60, "Дескриптор інтерфейсу:\nbInterfaceClass = 0xFF (Vendor)\nbInterfaceSubClass = 0xFF\nbInterfaceProtocol = 0xFF", size=11, fill="#ffffff", stroke="#cbd5e1", bold=True))

    # Стрілка вниз до формування MODALIAS
    frags.append(arrow(440, 130, 440, 170, color=LINE, sw=2))

    # Центральний блок: Рядок MODALIAS
    frags.append(rect(20, 170, 840, 105, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(40, 192, "2. СИНТЕЗ РЯДКА MODALIAS У ЯДРІ (Макрос usb_make_modalias)", size=12, color=FIELD, anchor="start", bold=True))

    frags.append(fitbox(40, 205, 800, 55, "MODALIAS = \"usb:v0403p6001d0600dc00dsc00dp00icFFiscFFipFFin00\"\nСинтаксис: v[VID] p[PID] d[REV] dc[Клас] dsc[Підклас] dp[Протокол] ic[КласIF] isc[ПідкласIF] ip[ПротоколIF] in[НомерIF]", size=11, fill="#ffffff", stroke="#86efac", bold=True))

    # Стрілка вниз до зіставлення
    frags.append(arrow(440, 275, 440, 315, color=LINE, sw=2))

    # Блок зіставлення з модулями
    frags.append(rect(20, 315, 840, 205, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(40, 337, "3. ЗІСТАВЛЕННЯ ТА ЗАВАНТАЖЕННЯ ДРАЙВЕРА (libkmod / modules.alias)", size=12, color=NEG, anchor="start", bold=True))

    frags.append(fitbox(40, 350, 380, 75, "Таблиця ідентифікаторів у C-коді драйвера:\nstatic const struct usb_device_id id_table[] = {\n    { USB_DEVICE(0x0403, 0x6001) }, ...\n};\nMODULE_DEVICE_TABLE(usb, id_table);", size=10, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(arrow(420, 387, 470, 387, color=LINE, sw=2))

    frags.append(fitbox(470, 350, 370, 75, "Генерація depmod при складанні ядра:\n/lib/modules/$(uname -r)/modules.alias:\nalias usb:v0403p6001d*dc*dsc*dp*ic*isc*ip*in* ftdi_sio", size=10, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(arrow(655, 425, 655, 445, color=NEG, sw=2))
    frags.append(arrow(230, 425, 230, 445, color=NEG, sw=2))

    frags.append(fitbox(40, 445, 380, 60, "systemd-udevd викликає libkmod:\nЗнаходить модуль ftdi_sio за шаблоном alias\nЗавантажує модуль у ядро (finit_module)", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(fitbox(470, 445, 370, 60, "Ядерна шина usb_bus_type:\nВикликає match() -> знаходить збіг -> probe()\nДрайвер бере контроль над кінцевими точками", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))

    render(os.path.join(OUT_DIR, "modalias-to-driver-matching.svg"), w, h, *frags)


def fig_netlink_uevent_packet_flow():
    """Схема розсилки пакетів Netlink uevent від ядра до простору користувача."""
    w, h = 880, 520
    frags = []

    # Ядро: генератор події
    frags.append(rect(20, 20, 840, 160, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(40, 42, "ПРОСТІР ЯДРА: ПІДСИСТЕМА KOBJECT ТА СОКЕТ NETLINK", size=12, color=FIELD, anchor="start", bold=True))

    frags.append(fitbox(40, 55, 370, 95, "kobject_uevent_env(kobj, KOBJ_ADD, env)\nЗбирає буфер змінних kobj_uevent_env:\n  ACTION=add\n  DEVPATH=/devices/pci0000:00/.../usb1/1-1\n  SUBSYSTEM=usb\n  MODALIAS=usb:v0403p6001...", size=10, fill="#ffffff", stroke="#86efac", bold=True))

    frags.append(arrow(410, 102, 470, 102, color=FIELD, sw=2))

    frags.append(fitbox(470, 55, 370, 95, "Ядерний сокет Netlink:\nnetlink_broadcast(uevent_sock, skb, 0, 1, GFP_KERNEL)\nПередає сформований sk_buff у черги сокетів\nусіх процесів, підписаних на групу 1", size=10, fill="#ffffff", stroke="#86efac", bold=True))

    # Стрілка вниз крізь межу ядра
    frags.append(arrow(655, 180, 655, 230, color=LINE, sw=2.5))
    frags.append(arrow(225, 180, 225, 230, color=LINE, sw=2.5))
    frags.append(text(440, 208, "Межа ядра / Системний виклик recvmsg(fd, &msg, 0)", size=11, color=MUTED, bold=True))

    # Простір користувача: підписники
    frags.append(rect(20, 230, 840, 270, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(40, 252, "ПРОСТІР КОРИСТУВАЧА: ПІДПИСНИКИ НА NETLINK_KOBJECT_UEVENT (Група 1)", size=12, color=NEG, anchor="start", bold=True))

    frags.append(fitbox(40, 270, 370, 110, "Головний демон: systemd-udevd\nsocket(AF_NETLINK, SOCK_RAW, 15)\nbind(fd, {nl_family=AF_NETLINK, nl_groups=1})\nЧитає пакунок, парсить рядки 'KEY=VALUE\\0'\nСтворює подію udev_event і передає worker'у", size=10, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(fitbox(470, 270, 370, 110, "Утиліти моніторингу (udevadm / власні програми)\nudevadm monitor --environment\nОтримує точну копію сирого пакета з ядра\nВиводить у термінал весь набір змінних оточення", size=10, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(arrow(225, 380, 225, 410, color=NEG, sw=2))
    frags.append(arrow(655, 380, 655, 410, color=NEG, sw=2))

    frags.append(fitbox(40, 410, 370, 75, "Конвеєр обробки systemd-udevd:\nВиконання правил -> Завантаження модулів ->\nНалаштування /dev -> Симлінки -> udev db", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))

    frags.append(fitbox(470, 410, 370, 75, "Відображення події в реальному часі:\nДіагностика під'єднання пристроїв,\nавтоматизація скриптів налагодження", size=11, fill="#ffffff", stroke="#93c5fd", bold=True))

    render(os.path.join(OUT_DIR, "netlink-uevent-packet-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_device_plug_full_pipeline()
    fig_modalias_to_driver_matching()
    fig_netlink_uevent_packet_flow()
    print("All figures generated successfully.")
