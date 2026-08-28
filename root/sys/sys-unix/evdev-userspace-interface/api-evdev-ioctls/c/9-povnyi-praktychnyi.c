#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <errno.h>

static int check_bit(const unsigned char *mask, int bit) {
    return (mask[bit / 8] & (1 << (bit % 8))) != 0;
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";

    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття пристрою evdev");
        return EXIT_FAILURE;
    }

    // 1. Запит версії драйвера evdev
    int version = 0;
    if (ioctl(fd, EVIOCGVERSION(&version)) < 0) {
        perror("Помилка EVIOCGVERSION");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("Версія evdev API: %d.%d.%d\n",
           version >> 16, (version >> 8) & 0xff, version & 0xff);

    // 2. Зчитування ідентифікаторів пристрою (bustype, vendor, product, version)
    struct input_id id;
    if (ioctl(fd, EVIOCGID(&id)) == 0) {
        printf("ID: Bus=0x%04x Vendor=0x%04x Product=0x%04x Version=0x%04x\n",
               id.bustype, id.vendor, id.product, id.version);
    }

    // 3. Зчитування назви пристрою
    char name[256] = "Невідомий пристрій";
    if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0) {
        printf("Назва: %s\n", name);
    }

    // 4. Зчитування фізичного шляху
    char phys[256] = "N/A";
    if (ioctl(fd, EVIOCGPHYS(sizeof(phys)), phys) >= 0) {
        printf("Фізичний шлях: %s\n", phys);
    }

    // 5. Перевірка підтримуваних типів подій (evbit)
    unsigned char evbit[(EV_MAX / 8) + 1];
    memset(evbit, 0, sizeof(evbit));
    if (ioctl(fd, EVIOCGBIT(0, sizeof(evbit)), evbit) < 0) {
        perror("Помилка зчитання EVIOCGBIT(0)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Підтримувані типи подій:\n");
    if (check_bit(evbit, EV_KEY)) printf("  - EV_KEY (Клавіші/Кнопки)\n");
    if (check_bit(evbit, EV_REL)) printf("  - EV_REL (Відносні осі)\n");
    if (check_bit(evbit, EV_ABS)) printf("  - EV_ABS (Абсолютні осі)\n");
    if (check_bit(evbit, EV_MSC)) printf("  - EV_MSC (Службові події)\n");
    if (check_bit(evbit, EV_SW))  printf("  - EV_SW  (Перемикачі)\n");
    if (check_bit(evbit, EV_LED)) printf("  - EV_LED (Світлодіоди)\n");
    if (check_bit(evbit, EV_FF))  printf("  - EV_FF  (Force Feedback)\n");

    // 6. Якщо підтримуються абсолютні осі, запитуємо деталі ABS_X
    if (check_bit(evbit, EV_ABS)) {
        unsigned char absbit[(ABS_MAX / 8) + 1];
        memset(absbit, 0, sizeof(absbit));
        if (ioctl(fd, EVIOCGBIT(EV_ABS, sizeof(absbit)), absbit) >= 0) {
            if (check_bit(absbit, ABS_X)) {
                struct input_absinfo abs;
                if (ioctl(fd, EVIOCGABS(ABS_X), &abs) == 0) {
                    printf("Вісь ABS_X: min=%d, max=%d, fuzz=%d, flat=%d, res=%d\n",
                           abs.minimum, abs.maximum, abs.fuzz, abs.flat, abs.resolution);
                }
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
