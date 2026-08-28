/* C Implementation: Direct /proc/stat CPU Utilization Calculator */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

typedef struct {
    unsigned long long user;
    unsigned long long nice;
    unsigned long long system;
    unsigned long long idle;
    unsigned long long iowait;
    unsigned long long irq;
    unsigned long long softirq;
    unsigned long long steal;
} CpuSnap;

int read_cpu_snapshot(CpuSnap *snap) {
    FILE *f = fopen("/proc/stat", "r");
    if (!f) return -1;

    char buffer[1024];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    int items = sscanf(buffer, "cpu %llu %llu %llu %llu %llu %llu %llu %llu",
                       &snap->user, &snap->nice, &snap->system, &snap->idle,
                       &snap->iowait, &snap->irq, &snap->softirq, &snap->steal);

    return (items >= 8) ? 0 : -1;
}

int main(void) {
    CpuSnap s1, s2;
    if (read_cpu_snapshot(&s1) != 0) {
        perror("Failed to read initial /proc/stat");
        return 1;
    }

    /* Інтервал заміру 1 секунда */
    sleep(1);

    if (read_cpu_snapshot(&s2) != 0) {
        perror("Failed to read second /proc/stat");
        return 1;
    }

    unsigned long long delta_user = (s2.user + s2.nice) - (s1.user + s1.nice);
    unsigned long long delta_system = s2.system - s1.system;
    unsigned long long delta_idle = s2.idle - s1.idle;
    unsigned long long delta_iowait = s2.iowait - s1.iowait;
    unsigned long long delta_irq = (s2.irq + s2.softirq) - (s1.irq + s1.softirq);
    unsigned long long delta_steal = s2.steal - s1.steal;

    unsigned long long delta_total = delta_user + delta_system + delta_idle +
                                    delta_iowait + delta_irq + delta_steal;

    if (delta_total == 0) delta_total = 1;

    double pct_user = (double)delta_user * 100.0 / delta_total;
    double pct_system = (double)delta_system * 100.0 / delta_total;
    double pct_idle = (double)delta_idle * 100.0 / delta_total;
    double pct_iowait = (double)delta_iowait * 100.0 / delta_total;

    printf("=== CPU UTILIZATION REPORT ===\n");
    printf("User Space:   %6.2f%%\n", pct_user);
    printf("Kernel Space: %6.2f%%\n", pct_system);
    printf("IO Wait:      %6.2f%%\n", pct_iowait);
    printf("Idle:         %6.2f%%\n", pct_idle);

    return 0;
}
