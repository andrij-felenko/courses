### Читання даних через hidraw (Код на C)

Якщо у вас є пристрій, що надсилає специфічні звіти, ви можете прочитати їх безпосередньо через `/dev/hidraw`.
Приклад простої програми мовою C, що читає Raw-звіти:

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    int fd;
    int res;
    unsigned char buf[8];

    // Відкриваємо перший доступний hidraw пристрій
    // У реальному житті потрібно перевіряти, який саме пристрій ми відкрили
    fd = open("/dev/hidraw0", O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття /dev/hidraw0");
        return 1;
    }

    printf("Пристрій відкрито. Чекаємо на дані...\n");

    while (1) {
        // Читаємо сирий звіт (довжина залежить від дескриптора пристрою)
        res = read(fd, buf, sizeof(buf));
        if (res < 0) {
            perror("Помилка читання");
            break;
        }

        // Виводимо прочитані байти
        printf("Прочитано %d байт: ", res);
        for (int i = 0; i < res; i++) {
            printf("%02hhx ", buf[i]);
        }
        printf("\n");
    }

    close(fd);
    return 0;
}
```
