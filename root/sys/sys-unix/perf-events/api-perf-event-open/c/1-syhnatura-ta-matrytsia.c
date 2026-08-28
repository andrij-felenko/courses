#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>

long perf_event_open(struct perf_event_attr *attr,
                     pid_t pid,
                     int cpu,
                     int group_fd,
                     unsigned long flags) {
    return syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}
