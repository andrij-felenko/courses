/* inspect_mq.c — Зчитування конфігурації blk-mq з sysfs на C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

void print_sysfs_attr(const char *dev, const char *attr) {
    char path[256];
    snprintf(path, sizeof(path), "/sys/block/%s/mq/%s", dev, attr);
    
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        snprintf(path, sizeof(path), "/sys/block/%s/queue/%s", dev, attr);
        fd = open(path, O_RDONLY);
    }
    
    if (fd >= 0) {
        char buf[128];
        ssize_t n = read(fd, buf, sizeof(buf) - 1);
        if (n > 0) {
            buf[n] = '\0';
            /* Видалення символу нового рядка */
            char *newline = strchr(buf, '\n');
            if (newline) *newline = '\0';
            printf("  %-20s: %s\n", attr, buf);
        }
        close(fd);
    } else {
        printf("  %-20s: [недоступно]\n", attr);
    }
}

int main(int argc, char *argv[]) {
    const char *dev_name = (argc > 1) ? argv[1] : "nvme0n1";
    printf("Інспектування blk-mq для пристрою /dev/%s:\n", dev_name);
    
    print_sysfs_attr(dev_name, "nr_hw_queues");
    print_sysfs_attr(dev_name, "scheduler");
    print_sysfs_attr(dev_name, "nr_requests");
    print_sysfs_attr(dev_name, "io_poll");
    
    return 0;
}
