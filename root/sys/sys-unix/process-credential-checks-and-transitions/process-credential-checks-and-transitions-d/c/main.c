#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>

int main(void) {
    uid_t ruid, euid, suid;

    // Отримання всіх трьох UID
    if (getresuid(&ruid, &euid, &suid) != 0) {
        perror("Помилка getresuid");
        return EXIT_FAILURE;
    }
    printf("Початковий стан: RUID=%d, EUID=%d, SUID=%d\n", ruid, euid, suid);

    // Тимчасове скидання привілеїв (якщо euid == 0)
    if (euid == 0) {
        if (seteuid(ruid) != 0) {
            perror("Помилка тимчасового скидання seteuid");
            return EXIT_FAILURE;
        }
        getresuid(&ruid, &euid, &suid);
        printf("Після тимчасового скидання: RUID=%d, EUID=%d, SUID=%d\n", ruid, euid, suid);

        // Відновлення привілеїв зі збереженого SUID
        if (seteuid(suid) != 0) {
            perror("Помилка відновлення привілеїв");
            return EXIT_FAILURE;
        }
        printf("Привілеї успішно відновлено.\n");
    }

    return EXIT_SUCCESS;
}
