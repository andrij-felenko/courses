#define _GNU_SOURCE
#include <unistd.h>
#include <linux/close_range.h>
#include <sys/syscall.h>

/* Очищення всіх зайвих дескрипторів перед викликом execve */
int sanitize_fds_before_exec(void) {
    /* Закриваємо все, крім stdin (0), stdout (1) та stderr (2) */
    return syscall(SYS_close_range, 3, ~0U, 0);
}

/* Встановлення прапорця CLOEXEC на всі успадковані дескриптори */
int mark_all_fds_cloexec(void) {
    return syscall(SYS_close_range, 3, ~0U, CLOSE_RANGE_CLOEXEC);
}
