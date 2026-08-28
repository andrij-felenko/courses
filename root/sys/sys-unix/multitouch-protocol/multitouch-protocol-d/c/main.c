#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <libevdev/libevdev.h>

int main() {
    struct libevdev *dev = NULL;
    int fd = open("/dev/input/event0", O_RDONLY|O_NONBLOCK);
    int rc = libevdev_new_from_fd(fd, &dev);
    
    if (rc < 0) {
        printf("Помилка ініціалізації: %s\n", strerror(-rc));
        return 1;
    }
    
    if (libevdev_has_event_code(dev, EV_ABS, ABS_MT_SLOT)) {
        printf("Пристрій підтримує Протокол B (Slots)\n");
        int num_slots = libevdev_get_num_slots(dev);
        printf("Максимальна кількість одночасних дотиків: %d\n", num_slots);
    } else if (libevdev_has_event_code(dev, EV_ABS, ABS_MT_POSITION_X)) {
        printf("Пристрій підтримує Протокол A (Stateless)\n");
    } else {
        printf("Пристрій не підтримує мультидотик\n");
    }
    
    // Читання подій. Дескриптор відкрито з O_NONBLOCK, тож щойно черга
    // порожня, libevdev_next_event поверне -EAGAIN і цикл завершиться;
    // у справжній програмі на дескрипторі чекають через poll() чи epoll.
    struct input_event ev;
    while (libevdev_next_event(dev, LIBEVDEV_READ_FLAG_NORMAL, &ev) == LIBEVDEV_READ_STATUS_SUCCESS) {
        if (ev.type == EV_ABS && ev.code == ABS_MT_SLOT) {
            printf("Перемикання на слот %d\n", ev.value);
        } else if (ev.type == EV_ABS && ev.code == ABS_MT_TRACKING_ID) {
            if (ev.value == -1)
                printf("Дотик завершено\n");
            else
                printf("Новий дотик, ID = %d\n", ev.value);
        } else if (ev.type == EV_ABS && ev.code == ABS_MT_POSITION_X) {
            // Отримати поточний активний слот можна через libevdev
            int slot = libevdev_get_current_slot(dev);
            printf("Слот %d: X = %d\n", slot, ev.value);
        }
    }
    
    libevdev_free(dev);
    close(fd);
    return 0;
}
