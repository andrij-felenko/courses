#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <sys/prctl.h>

void enable_debugging_access(void) {
    // Дозволяємо будь-якому процесу з тим самим UID підключатися через ptrace
    if (prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0) == -1) {
        perror("Помилка налаштування PR_SET_PTRACER");
    } else {
        printf("Процес (PID: %d) відкритий для підключення GDB\n", getpid());
    }
}
