/* capsesc.c — Caps Lock працює як Escape для всієї системи.
 * збірка: cc -O2 -Wall -o capsesc capsesc.c
 * запуск: sudo ./capsesc /dev/input/by-id/…-event-kbd
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <fcntl.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define LBITS         (8 * sizeof(unsigned long))
#define NLONGS(n)     (((n) + LBITS - 1) / LBITS)
#define TESTBIT(a, n) (((a)[(n) / LBITS] >> ((n) % LBITS)) & 1UL)
#define SETBIT(a, n)  ((a)[(n) / LBITS] |= 1UL << ((n) % LBITS))
#define CLRBIT(a, n)  ((a)[(n) / LBITS] &= ~(1UL << ((n) % LBITS)))
#define KEYWORDS      NLONGS(KEY_MAX + 1)

static __u16 remap(__u16 code)
{
        return code == KEY_CAPSLOCK ? KEY_ESC : code;
}

/* Час лишаємо нулями: нуль ядро дійсною позначкою не вважає й ставить свою.
   Чужу воно бере лише в новіших ядрах — і лише не з майбутнього й не старшу за 10 с. */
static int emit(int ui, __u16 type, __u16 code, __s32 value)
{
        struct input_event ev = { .type = type, .code = code, .value = value };
        return write(ui, &ev, sizeof ev) == (ssize_t)sizeof ev ? 0 : -1;
}

static int build_device(int ui, int src)
{
        unsigned long keys[KEYWORDS] = { 0 };
        struct uinput_setup us = {
                .id = { .bustype = BUS_VIRTUAL, .vendor = 0x1d6b,
                        .product = 0x0001,       .version = 1 },
        };

        /* 1. Типи подій. EV_REP тут навмисно немає — див. нижче про автоповтор. */
        if (ioctl(ui, UI_SET_EVBIT, EV_KEY) < 0) return -1;
        if (ioctl(ui, UI_SET_EVBIT, EV_SYN) < 0) return -1;

        /* 2. Клавіші. Беремо маску джерела — але оголошуємо ПІДМІНЕНІ коди:
              з нашого пристрою вилітає KEY_ESC, а KEY_CAPSLOCK — ніколи. */
        if (ioctl(src, EVIOCGBIT(EV_KEY, sizeof keys), keys) < 0) return -1;
        for (unsigned c = 0; c <= KEY_MAX; c++)
                if (TESTBIT(keys, c) && ioctl(ui, UI_SET_KEYBIT, remap(c)) < 0)
                        return -1;

        /* 3. Паспорт: шина, виробник, модель, назва.
              -EINVAL тут означає ядро, старше за 4.5, — там лише старий шлях. */
        snprintf(us.name, sizeof us.name, "capsesc virtual keyboard");
        if (ioctl(ui, UI_DEV_SETUP, &us) < 0) return -1;

        /* 4. Аж тепер пристрій народжується. */
        return ioctl(ui, UI_DEV_CREATE);
}
