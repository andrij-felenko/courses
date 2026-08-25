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

def fig_kobject_embedding_container_of():
    W, H = 1000, 560
    p = []

    # Title
    t_hdr, _, _ = textbox(W / 2, 35, ["Вбудовування struct kobject у структуру драйвера та перехід через container_of()"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(t_hdr)

    # Outer container: struct my_device (Heap allocated)
    p.append(rect(60, 90, 440, 430, fill="none", stroke=LINE, sw=2, rx=8))
    p.append(text(280, 115, "struct my_device (виділено динамічно в купі)", size=14, bold=True, color=INK))

    # Base address indicator
    p.append(arrow(30, 140, 58, 140, color=FIELD, sw=2))
    p.append(text(25, 130, "dev (базова адреса)", size=11, bold=True, color=FIELD, anchor="end"))

    # Fields inside struct my_device
    f1, _, _ = textbox(280, 155, ["int dev_id", "ідентифікатор екземпляра [offset 0]"], size=12, fill=FILL, stroke=LINE, min_w=400)
    p.append(f1)

    f2, _, _ = textbox(280, 215, ["void __iomem *mmio_base", "відображені регістри пристрою [offset 8]"], size=12, fill=FILL, stroke=LINE, min_w=400)
    p.append(f2)

    # Embedded kobject (highlighted)
    p.append(rect(80, 260, 400, 170, fill=BLUE, stroke=NEG, sw=2, rx=6))
    p.append(text(280, 280, "struct kobject kobj [offset 24]", size=13, bold=True, color=NEG))
    
    kobj_fields = [
        "const char *name  ──► \"my_dev0\"",
        "struct kref kref  ──► refcount = 1",
        "struct kobject *parent, *kset",
        "const struct kobj_type *ktype ──► my_ktype",
        "struct kernfs_node *sd ──► /sys/devices/.../my_dev0"
    ]
    p.append(mtext(100, 305, kobj_fields, size=11, color=INK, anchor="start", lh=1.35))

    # kobj pointer indicator
    p.append(arrow(30, 280, 78, 280, color=NEG, sw=2))
    p.append(text(25, 270, "kobj_ptr (&dev->kobj)", size=11, bold=True, color=NEG, anchor="end"))

    f3, _, _ = textbox(280, 470, ["struct cdev cdev", "інтерфейс символьного пристрою [offset 104]"], size=12, fill=FILL, stroke=LINE, min_w=400)
    p.append(f3)

    # Right side: container_of computation explanation
    p.append(rect(540, 90, 420, 430, fill="none", stroke=LINE, sw=1.8, rx=8))
    p.append(text(750, 120, "Арифметика container_of(ptr, type, member)", size=14, bold=True, color=INK))

    math_block = [
        "1. Макрос отримує вказівник на kobject:",
        "   struct kobject *kobj_ptr = ...;",
        "",
        "2. Обчислюється байтовий зсув поля:",
        "   size_t offset = offsetof(struct my_device, kobj);",
        "   // offset = 24 байти",
        "",
        "3. Від адреси kobj віднімається зсув:",
        "   char *raw = (char *)kobj_ptr - offset;",
        "",
        "4. Приведення до цільового типу структури:",
        "   struct my_device *dev = (struct my_device *)raw;"
    ]
    p.append(mtext(560, 155, math_block, size=11.5, color=INK, anchor="start", lh=1.35))

    # Bottom formula box
    f_res, _, _ = textbox(750, 455, [
        "dev = container_of(kobj_ptr, struct my_device, kobj);",
        "Єдиний безпечний спосіб дістатися драйвера з release() чи show()"
    ], size=11.5, bold=True, fill=GREEN, stroke=FIELD, min_w=380)
    p.append(f_res)

    # Connecting arrow between kobj_ptr and container_of arithmetic
    p.append(arrow(480, 280, 538, 280, color=NEG, sw=2))

    render(os.path.join(IMG, "kobject-embedding-container-of.svg"), W, H, *p)

def fig_kref_lifecycle_transitions():
    W, H = 1000, 560
    p = []

    t_hdr, _, _ = textbox(W / 2, 35, ["Граф переходів станів лічильника kref / refcount_t"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(t_hdr)

    # Node 1: kref_init
    n1, _, _ = textbox(150, 160, ["kref_init(&kref)", "refcount = 1", "Об'єкт створено в kzalloc()"], size=12.5, bold=True, fill=GREEN, stroke=FIELD, min_w=200)
    p.append(n1)

    # Node 2: Active References (kref >= 1)
    n2, _, _ = textbox(500, 160, ["Активний стан (Живий об'єкт)", "refcount = N  (N ≥ 1)", "Доступ відкритий: sysfs, VFS, драйвер"], size=12.5, bold=True, fill=BLUE, stroke=NEG, min_w=260)
    p.append(n2)

    # Node 3: kref_put decrementing (N > 1 -> N-1)
    n3, _, _ = textbox(850, 160, ["kref_put()", "refcount = N - 1", "Звільнення одного посилання"], size=12, fill=FILL, stroke=LINE, min_w=180)
    p.append(n3)

    # Node 4: Zero crossing (N reaches 0)
    n4, _, _ = textbox(500, 360, ["Перехід через нуль (0)", "refcount_dec_and_test() == true", "Всі посилання скинуто"], size=12.5, bold=True, fill=PURPLE, stroke=LINE, min_w=260)
    p.append(n4)

    # Node 5: Release Callback & kfree
    n5, _, _ = textbox(150, 360, ["release callback", "ktype->release(kobj)", "kfree(container_of(kobj))"], size=12.5, bold=True, fill=RED, stroke=POS, min_w=200)
    p.append(n5)

    # Node 6: Protection against increment from 0
    n6, _, _ = textbox(850, 360, ["refcount_inc_not_zero()", "Спроба kref_get() коли ref=0", "ПОМИЛКА: об'єкт мертвий"], size=12, bold=True, fill=GREY, stroke=POS, min_w=190)
    p.append(n6)

    # Arrows between nodes
    p.append(arrow(255, 160, 365, 160, color=LINE, sw=2))
    p.append(text(310, 145, "Реєстрація", size=11, color=MUTED))

    # Loop for kref_get
    p.append(arrow(635, 140, 755, 140, color=LINE, sw=2))
    p.append(text(695, 128, "kref_get() [+1]", size=11, color=NEG, bold=True))

    p.append(arrow(755, 180, 635, 180, color=LINE, sw=2))
    p.append(text(695, 198, "kref_put() [−1]", size=11, color=MUTED))

    # Arrow from Active to Zero crossing
    p.append(arrow(500, 215, 500, 310, color=POS, sw=2.2))
    p.append(text(510, 265, "kref_put(): refcount падає з 1 до 0", size=11.5, bold=True, color=POS, anchor="start"))

    # Arrow from Zero crossing to Release callback
    p.append(arrow(365, 360, 255, 360, color=POS, sw=2.2))
    p.append(text(310, 345, "Виклик деструктора", size=11, bold=True, color=POS))

    # Arrow from Zero crossing to Protection node
    p.append(arrow(635, 360, 750, 360, color=LINE, sw=1.8))
    p.append(text(695, 345, "Паралельний запит", size=11, color=MUTED))

    # Bottom summary box
    p.append(rect(100, 450, 800, 80, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(500, 475, "Правило ядра: пам'ять структури звільняється ТІЛЬКИ в release() callback", size=13, bold=True, color=INK))
    p.append(text(500, 505, "Прямий kfree() поза release() або розміщення kobject у статичній пам'яті гарантує Kernel Panic!", size=12, bold=True, color=POS))

    render(os.path.join(IMG, "kref-lifecycle-transitions.svg"), W, H, *p)

def fig_device_unplug_vs_release_timeline():
    W, H = 1050, 580
    p = []

    t_hdr, _, _ = textbox(W / 2, 35, ["Розділення фізичного від'єднання (Unplug) та звільнення пам'яті (Release)"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(t_hdr)

    # Time arrow at the top
    p.append(arrow(100, 80, 950, 80, color=LINE, sw=2))
    p.append(text(960, 85, "Час (t)", size=12, bold=True, color=INK, anchor="start"))

    # Track 1: Hardware State
    p.append(text(90, 130, "Апаратний стан:", size=12, bold=True, color=INK, anchor="end"))
    b_hw1, _, _ = textbox(250, 130, ["Пристрій підключено", "Нормальна робота (USB/PCI)"], size=11, fill=GREEN, stroke=FIELD, min_w=220)
    p.append(b_hw1)

    p.append(arrow(365, 130, 445, 130, color=POS, sw=2))
    p.append(text(405, 115, "Hot-Unplug!", size=11, bold=True, color=POS))

    b_hw2, _, _ = textbox(600, 130, ["Апаратура фізично відсутня", "Лінії шини відключено"], size=11, fill=RED, stroke=POS, min_w=220)
    p.append(b_hw2)

    # Track 2: sysfs / kernfs state
    p.append(text(90, 220, "Ядро та sysfs:", size=12, bold=True, color=INK, anchor="end"))
    b_sys1, _, _ = textbox(250, 220, ["/sys/devices/.../dev0 існує", "Каталог і файли доступні"], size=11, fill=BLUE, stroke=NEG, min_w=220)
    p.append(b_sys1)

    b_sys2, _, _ = textbox(600, 220, ["kobject_del() / kernfs_drain", "Каталог миттєво видалено з /sys", "Нові open/read дають -ENODEV"], size=11, fill=WARM, stroke=LINE, min_w=240)
    p.append(b_sys2)

    # Track 3: Userspace & In-flight I/O
    p.append(text(90, 320, "Процеси користувача:", size=12, bold=True, color=INK, anchor="end"))
    b_usr1, _, _ = textbox(250, 320, ["Процес А: відкрив /sys/.../stat", "Процес Б: виконує ioctl()"], size=11, fill=FILL, stroke=LINE, min_w=220)
    p.append(b_usr1)

    b_usr2, _, _ = textbox(600, 320, ["Процес А читає буфер kernfs", "Процес Б завершує системний виклик", "Поточні виклики добігають кінця"], size=11, fill=FILL, stroke=LINE, min_w=240)
    p.append(b_usr2)

    b_usr3, _, _ = textbox(870, 320, ["close(fd)", "Всі дескриптори закрито"], size=11, fill=GREY, stroke=LINE, min_w=180)
    p.append(b_usr3)

    # Track 4: kref count & Memory
    p.append(text(90, 440, "refcount & Пам'ять:", size=12, bold=True, color=INK, anchor="end"))
    b_mem1, _, _ = textbox(250, 440, ["kref refcount = 3", "(драйвер + процес А + процес Б)", "Пам'ять валідна"], size=11, fill=BLUE, stroke=NEG, min_w=220)
    p.append(b_mem1)

    b_mem2, _, _ = textbox(600, 440, ["Драйвер скинув своє посилання", "kref refcount = 2 ──► 1", "Пам'ять все ще утримується!"], size=11, fill=PURPLE, stroke=LINE, min_w=240)
    p.append(b_mem2)

    b_mem3, _, _ = textbox(870, 440, ["kref refcount = 0", "ktype->release(kobj)", "kfree(my_dev) ──► Пам'ять звільнено"], size=11, bold=True, fill=GREEN, stroke=FIELD, min_w=220)
    p.append(b_mem3)

    # Vertical dotted timeline synchronization lines
    p.append(line(450, 95, 450, 480, color=POS, sw=1.5, dash="4,4"))
    p.append(text(450, 500, "t1: Від'єднання пристрою", size=10.5, color=POS, bold=True))

    p.append(line(735, 95, 735, 480, color=MUTED, sw=1.5, dash="4,4"))
    p.append(text(735, 500, "t2: Завершення I/O", size=10.5, color=MUTED, bold=True))

    p.append(line(960, 95, 960, 480, color=FIELD, sw=1.5, dash="4,4"))
    p.append(text(960, 500, "t3: Фінальний release()", size=10.5, color=FIELD, bold=True))

    # Bottom conclusion text
    p.append(text(500, 545, "Завдяки kref аварія use-after-free неможлива: пам'ять живе довше за апаратуру рівно на стільки, скільки триває I/O", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "device-unplug-vs-release-timeline.svg"), W, H, *p)

if __name__ == "__main__":
    fig_kobject_embedding_container_of()
    fig_kref_lifecycle_transitions()
    fig_device_unplug_vs_release_timeline()
    print("Figures generated successfully!")
