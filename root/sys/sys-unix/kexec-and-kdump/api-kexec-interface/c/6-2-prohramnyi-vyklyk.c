#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <errno.h>

#ifndef SYS_kexec_file_load
#define SYS_kexec_file_load 320
#endif

int load_kernel_image(const char *kernel_path, const char *initrd_path, const char *cmdline) {
    int kfd = open(kernel_path, O_RDONLY);
    if (kfd < 0) {
        perror("Помилка відкриття файлу ядра");
        return -1;
    }

    int ifd = -1;
    if (initrd_path != NULL) {
        ifd = open(initrd_path, O_RDONLY);
        if (ifd < 0) {
            perror("Помилка відкриття файлу initrd");
            close(kfd);
            return -1;
        }
    }

    unsigned long cmdline_len = cmdline ? strlen(cmdline) + 1 : 0;
    long res = syscall(SYS_kexec_file_load, kfd, ifd, cmdline_len, cmdline, 0);

    if (ifd >= 0) close(ifd);
    close(kfd);

    if (res < 0) {
        perror("Помилка виконання kexec_file_load");
        return -1;
    }

    printf("Ядро успішно завантажено в пам'ять через kexec_file_load\n");
    return 0;
}
