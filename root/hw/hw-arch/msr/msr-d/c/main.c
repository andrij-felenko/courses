#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#define IA32_EFER_MSR 0xC0000080

int main(void) {
    int fd = open("/dev/cpu/0/msr", O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття /dev/cpu/0/msr: %s\n", strerror(errno));
        return 1;
    }

    uint64_t efer_val = 0;
    if (pread(fd, &efer_val, sizeof(efer_val), (off_t)IA32_EFER_MSR) != sizeof(efer_val)) {
        fprintf(stderr, "Помилка читання IA32_EFER: %s\n", strerror(errno));
        close(fd);
        return 1;
    }

    printf("IA32_EFER = 0x%016llX\n", (unsigned long long)efer_val);
    printf("  Long Mode Active (LMA): %s\n", (efer_val & (1 << 10)) ? "Так" : "Ні");
    printf("  No-Execute Enable (NXE): %s\n", (efer_val & (1 << 11)) ? "Так" : "Ні");
    printf("  Syscall Extensions (SCE): %s\n", (efer_val & (1 << 0)) ? "Так" : "Ні");

    close(fd);
    return 0;
}
