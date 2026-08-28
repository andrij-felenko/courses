#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/ptp_clock.h>

int read_precise_cross_timestamp(const char *ptp_device) {
    int fd = open(ptp_device, O_RDONLY);
    if (fd < 0) {
        perror("open(ptp_device)");
        return -1;
    }

    struct ptp_sys_offset_precise offset;
    memset(&offset, 0, sizeof(offset));

    if (ioctl(fd, PTP_SYS_OFFSET_PRECISE, &offset) == 0) {
        printf("Апаратний Cross-Timestamping (PTP_SYS_OFFSET_PRECISE):\n");
        printf("  Апаратний годинник PHC:  %lld.%09u с\n",
               (long long)offset.device.sec, offset.device.nsec);
        printf("  Системний час (Realtime): %lld.%09u с\n",
               (long long)offset.sys_realtime.sec, offset.sys_realtime.nsec);
        printf("  Монотонний сирий (MonoRaw): %lld.%09u с\n",
               (long long)offset.sys_monoraw.sec, offset.sys_monoraw.nsec);

        long long diff_ns = ((long long)offset.sys_realtime.sec - offset.device.sec) * 1000000000LL +
                            ((long long)offset.sys_realtime.nsec - offset.device.nsec);
        printf("  Миттєвий розсинхрон (Offset): %lld нс\n", diff_ns);
    } else {
        printf("PTP_SYS_OFFSET_PRECISE не підтримується обладнанням. Використання PTP_SYS_OFFSET...\n");
        
        struct ptp_sys_offset sysoff;
        memset(&sysoff, 0, sizeof(sysoff));
        sysoff.n_samples = 5;

        if (ioctl(fd, PTP_SYS_OFFSET, &sysoff) < 0) {
            perror("ioctl(PTP_SYS_OFFSET)");
            close(fd);
            return -1;
        }

        printf("Результати програмного сендвіча PTP_SYS_OFFSET (%u вибірок):\n", sysoff.n_samples);
        for (unsigned int i = 0; i < sysoff.n_samples; i++) {
            long long t_cpu1 = (long long)sysoff.ts[2 * i].sec * 1000000000LL + sysoff.ts[2 * i].nsec;
            long long t_phc  = (long long)sysoff.ts[2 * i + 1].sec * 1000000000LL + sysoff.ts[2 * i + 1].nsec;
            long long t_cpu2 = (long long)sysoff.ts[2 * i + 2].sec * 1000000000LL + sysoff.ts[2 * i + 2].nsec;

            long long cpu_mid = (t_cpu1 + t_cpu2) / 2;
            long long delay = t_cpu2 - t_cpu1;
            long long offset_ns = cpu_mid - t_phc;

            printf("  Зріз %u: PHC=%lld нс, CPU_mid=%lld нс, Затримка PCIe=%lld нс, Зсув=%lld нс\n",
                   i, t_phc, cpu_mid, delay, offset_ns);
        }
    }

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *dev = (argc > 1) ? argv[1] : "/dev/ptp0";
    return read_precise_cross_timestamp(dev);
}
