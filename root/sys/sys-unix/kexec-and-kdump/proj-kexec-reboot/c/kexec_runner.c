/* kexec_runner.c — Реалізація мовою C з обробкою помилок goto cleanup */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/syscall.h>
#include <sys/reboot.h>
#include <linux/kexec.h>

#ifndef SYS_kexec_file_load
#if defined(__x86_64__)
#define SYS_kexec_file_load 320
#elif defined(__aarch64__)
#define SYS_kexec_file_load 294
#endif
#endif

int is_kexec_already_loaded(void) {
    int fd = open("/sys/kernel/kexec_loaded", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 0;
    
    char buf[4] = {0};
    ssize_t ret = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    return (ret > 0 && buf[0] == '1');
}

int load_new_kernel(const char *kernel_path, const char *initrd_path, const char *cmdline, unsigned long flags) {
    int kernel_fd = -1;
    int initrd_fd = -1;
    int result = -1;

    kernel_fd = open(kernel_path, O_RDONLY | O_CLOEXEC);
    if (kernel_fd < 0) {
        fprintf(stderr, "Помилка відкриття ядра '%s': %s\n", kernel_path, strerror(errno));
        goto cleanup;
    }

    if (initrd_path != NULL && strlen(initrd_path) > 0) {
        initrd_fd = open(initrd_path, O_RDONLY | O_CLOEXEC);
        if (initrd_fd < 0) {
            fprintf(stderr, "Помилка відкриття initramfs '%s': %s\n", initrd_path, strerror(errno));
            goto cleanup;
        }
    }

    size_t cmdline_len = cmdline ? strlen(cmdline) + 1 : 0;

    long ret = syscall(SYS_kexec_file_load, kernel_fd, initrd_fd, cmdline_len, cmdline, flags);
    if (ret != 0) {
        fprintf(stderr, "Системний виклик kexec_file_load завершився з помилкою %ld: %s\n", ret, strerror(errno));
        goto cleanup;
    }

    printf("Ядро успішно підготовлено до запуску через kexec!\n");
    result = 0;

cleanup:
    if (initrd_fd >= 0) close(initrd_fd);
    if (kernel_fd >= 0) close(kernel_fd);
    return result;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Використання: %s <path_to_vmlinuz> [path_to_initrd] [cmdline]\n", argv[0]);
        return 1;
    }

    if (is_kexec_already_loaded()) {
        printf("Увага: У пам'яті вже підготовлено ядро для kexec.\n");
    }

    const char *kernel_path = argv[1];
    const char *initrd_path = (argc > 2 && strlen(argv[2]) > 0) ? argv[2] : NULL;
    const char *cmdline = (argc > 3) ? argv[3] : "console=tty0 quiet";

    if (load_new_kernel(kernel_path, initrd_path, cmdline, 0) == 0) {
        printf("Для виклику гарячого перезавантаження виконайте: reboot -f\n");
    }

    return 0;
}
