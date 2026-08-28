#include <linux/blkzoned.h>
#include <sys/ioctl.h>
#include <cstdint>

// Основні управляючі командні коди ioctl підсистеми ZBD (C++ UAPI):
// BLKREPORTZONES — заповнення масиву описувачів зон для вказаного діапазону LBA
// BLKRESETZONE   — апаратне скидання вказівника запису (Write Pointer) у 0
// BLKOPENZONE    — явний перехід зони в стан Explicitly Opened
// BLKCLOSEZONE   — явний перехід зони в стан Closed (звільнення ресурсів кешу)
// BLKFINISHZONE  — дострокове переведення частково записаної зони у стан Full
// BLKGETZONESZ   — швидке отримання розміру зони в 512-байтових секторах
// BLKGETNRZONES  — швидке отримання загальної кількості зон пристрою
