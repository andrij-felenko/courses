#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <linux/input.h>
#include <linux/uinput.h>

static int g_src_fd = -1;
static int g_uinput_fd = -1;

static void cleanup_and_exit(int sig) {
    (void)sig;
    if (g_src_fd >= 0) {
        // Звільняємо монопольне захоплення перед виходом
        ioctl(g_src_fd, EVIOCGRAB, 0);
        close(g_src_fd);
    }
    if (g_uinput_fd >= 0) {
        ioctl(g_uinput_fd, UI_DEV_DESTROY);
        close(g_uinput_fd);
    }
    printf("\n[KeyMapper] Пристрій звільнено. Завершення роботи.\n");
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/input/eventX\n", argv[0]);
        return 1;
    }

    const char *src_device = argv[1];
    g_src_fd = open(src_device, O_RDONLY);
    if (g_src_fd < 0) {
        perror("Не вдалося відкрити джерельний пристрій evdev");
        return 1;
    }

    g_uinput_fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (g_uinput_fd < 0) {
        perror("Не вдалося відкрити /dev/uinput");
        close(g_src_fd);
        return 1;
    }

    // Декларація типів подій та клавіш для віртуального пристрою
    ioctl(g_uinput_fd, UI_SET_EVBIT, EV_KEY);
    ioctl(g_uinput_fd, UI_SET_EVBIT, EV_SYN);
    for (int i = 0; i < KEY_MAX; ++i) {
        ioctl(g_uinput_fd, UI_SET_KEYBIT, i);
    }

    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234;
    usetup.id.product = 0x5678;
    strcpy(usetup.name, "Virtual Remapped Keyboard");

    if (ioctl(g_uinput_fd, UI_DEV_SETUP, &usetup) < 0 ||
        ioctl(g_uinput_fd, UI_DEV_CREATE) < 0) {
        perror("Помилка створення пристрою uinput");
        close(g_src_fd);
        close(g_uinput_fd);
        return 1;
    }

    // Реєстрація системних сигналів для безпечного виходу
    signal(SIGINT, cleanup_and_exit);
    signal(SIGTERM, cleanup_and_exit);

    // Монопольне захоплення джерельного пристрою
    if (ioctl(g_src_fd, EVIOCGRAB, 1) < 0) {
        perror("Не вдалося виконати EVIOCGRAB на клавіатурі");
        cleanup_and_exit(1);
    }

    printf("[KeyMapper] Успішно захоплено %s. Натисніть Ctrl+C для виходу.\n", src_device);
    printf("[KeyMapper] Перетворюємо Caps Lock (код %d) -> Escape (код %d)\n", KEY_CAPSLOCK, KEY_ESC);

    struct input_event ev;
    while (read(g_src_fd, &ev, sizeof(ev)) > 0) {
        if (ev.type == EV_KEY) {
            if (ev.code == KEY_CAPSLOCK) {
                ev.code = KEY_ESC; // Заміна CapsLock на Escape
            }
        }
        if (write(g_uinput_fd, &ev, sizeof(ev)) < 0) {
            perror("Помилка запису події в uinput");
            break;
        }
    }

    cleanup_and_exit(0);
    return 0;
}
