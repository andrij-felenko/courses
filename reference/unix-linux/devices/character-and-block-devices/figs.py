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

def fig_cdev_vs_bdev_architecture():
    W, H = 1200, 780
    p = []

    # Title / Header
    f_hdr, _, _ = textbox(W / 2, 40, ["Порівняння шляхів передачі даних: Символьний (cdev) vs Блочний (bdev) пристрій"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Column 1: Userspace
    cx_user = 200
    f_usr, _, _ = textbox(cx_user, 110, ["Простір користувача", "системні виклики read() / write()"], size=14, bold=True, fill=BLUE, stroke=LINE)
    p.append(f_usr)

    # Column 2: cdev path (Left side)
    cx_cdev = 400
    y_cdev_hdr = 200
    f_cdev_title, _, _ = textbox(cx_cdev, y_cdev_hdr, ["Символьний пристрій (cdev)", "Послідовний потік байтів"], size=14, bold=True, fill=GREEN, stroke=LINE)
    p.append(f_cdev_title)

    y_cdev_vfs = 320
    f_cdev_vfs, _, _ = textbox(cx_cdev, y_cdev_vfs, ["VFS Layer", "chrdev_open() -> f_op", "таблиця file_operations"], size=13, fill=FILL, stroke=LINE)
    p.append(f_cdev_vfs)

    y_cdev_drv = 460
    f_cdev_drv, _, _ = textbox(cx_cdev, y_cdev_drv, ["Драйвер cdev", "my_cdev_read() / write()", "copy_to_user() / copy_from_user()"], size=13, fill=FILL, stroke=LINE)
    p.append(f_cdev_drv)

    y_cdev_hw = 620
    f_cdev_hw, _, _ = textbox(cx_cdev, y_cdev_hw, ["Апаратура (UART / TTY / RNG)", "Прямий побайтовий обмін", "без сторінкового кешу"], size=13, fill=RED, stroke=LINE)
    p.append(f_cdev_hw)

    # Column 3: bdev path (Right side)
    cx_bdev = 850
    y_bdev_hdr = 200
    f_bdev_title, _, _ = textbox(cx_bdev, y_bdev_hdr, ["Блочний пристрій (bdev)", "Адресовані блоки (512B / 4KB)"], size=14, bold=True, fill=PURPLE, stroke=LINE)
    p.append(f_bdev_title)

    y_bdev_vfs = 310
    f_bdev_vfs, _, _ = textbox(cx_bdev + 50, y_bdev_vfs, ["VFS & Page Cache", "Сторінковий кеш (address_space)", "Буферизація та читання з випередженням"], size=13, fill=FILL, stroke=LINE)
    p.append(f_bdev_vfs)

    y_bdev_bio = 430
    f_bdev_bio, _, _ = textbox(cx_bdev + 50, y_bdev_bio, ["Block I/O Layer (struct bio)", "Формування векторів I/O", "blk-mq (мультичерги запитів)"], size=13, fill=FILL, stroke=LINE)
    p.append(f_bdev_bio)

    y_bdev_sched = 540
    f_bdev_sched, _, _ = textbox(cx_bdev + 50, y_bdev_sched, ["Планувальник I/O", "Злиття (Merging) та сортування", "BFQ / Kyber / mq-deadline"], size=13, fill=FILL, stroke=LINE)
    p.append(f_bdev_sched)

    y_bdev_hw = 660
    f_bdev_hw, _, _ = textbox(cx_bdev + 50, y_bdev_hw, ["Контролер носія (NVMe / SATA / MMC)", "Пакетна передача блоків (DMA)", "Висока пропускна здатність"], size=13, fill=RED, stroke=LINE)
    p.append(f_bdev_hw)

    # Arrows
    p.append(arrow(cx_user, 145, cx_cdev, y_cdev_hdr - 25))
    p.append(arrow(cx_user, 145, cx_bdev + 50, y_bdev_hdr - 25))

    p.append(arrow(cx_cdev, y_cdev_hdr + 25, cx_cdev, y_cdev_vfs - 25))
    p.append(arrow(cx_cdev, y_cdev_vfs + 25, cx_cdev, y_cdev_drv - 25))
    p.append(arrow(cx_cdev, y_cdev_drv + 25, cx_cdev, y_cdev_hw - 25))

    p.append(arrow(cx_bdev + 50, y_bdev_hdr + 25, cx_bdev + 50, y_bdev_vfs - 25))
    p.append(arrow(cx_bdev + 50, y_bdev_vfs + 25, cx_bdev + 50, y_bdev_bio - 25))
    p.append(arrow(cx_bdev + 50, y_bdev_bio + 25, cx_bdev + 50, y_bdev_sched - 25))
    p.append(arrow(cx_bdev + 50, y_bdev_sched + 25, cx_bdev + 50, y_bdev_hw - 25))

    out_path = os.path.join(IMG, 'cdev-vs-bdev-architecture.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

def fig_dev_t_split_and_vfs_lookup():
    W, H = 1100, 680
    p = []

    # Title
    f_hdr, _, _ = textbox(W / 2, 35, ["Маршрутизація VFS за типом пристрою та dev_t"], size=16, bold=True, fill=WARM, stroke=LINE)
    p.append(f_hdr)

    # Inode Box
    f_inode, _, _ = textbox(250, 110, ["Вузол файлу пристрою (struct inode)", "i_mode: S_IFCHR / S_IFBLK", "i_rdev: dev_t (Major = 12 bit, Minor = 20 bit)"], size=13, fill=BLUE, stroke=LINE)
    p.append(f_inode)

    # Split decision box
    f_dec, _, _ = textbox(250, 240, ["Перевірка типу пристрою в VFS", "init_special_inode() задає i_fop"], size=13, bold=True, fill=WARM, stroke=LINE)
    p.append(f_dec)

    # Branch Left: S_ISCHR
    f_chr_branch, _, _ = textbox(180, 360, ["Символьний пристрій (S_ISCHR)", "def_chr_fops -> chrdev_open()", "kobj_lookup() у cdev_map"], size=13, fill=GREEN, stroke=LINE)
    p.append(f_chr_branch)

    f_chr_op, _, _ = textbox(180, 500, ["struct cdev", "file->f_op = cdev->ops", "Прямий системний виклик read/write"], size=13, fill=FILL, stroke=LINE)
    p.append(f_chr_op)

    # Branch Right: S_ISBLK
    f_blk_branch, _, _ = textbox(720, 360, ["Блочний пристрій (S_ISBLK)", "def_blk_fops -> blkdev_open()", "пошук block_device за dev_t"], size=13, fill=PURPLE, stroke=LINE)
    p.append(f_blk_branch)

    f_blk_op, _, _ = textbox(720, 500, ["struct block_device & gendisk", "file->f_op = def_blk_fops", "Перенаправлення до Page Cache & blk-mq"], size=13, fill=FILL, stroke=LINE)
    p.append(f_blk_op)

    # Arrows
    p.append(arrow(250, 155, 250, 215))
    p.append(arrow(250, 265, 180, 335))
    p.append(arrow(250, 265, 720, 335))

    p.append(arrow(180, 395, 180, 475))
    p.append(arrow(720, 395, 720, 475))

    out_path = os.path.join(IMG, 'dev-t-split-and-vfs-lookup.svg')
    render(out_path, W, H, *p)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    fig_cdev_vs_bdev_architecture()
    fig_dev_t_split_and_vfs_lookup()
