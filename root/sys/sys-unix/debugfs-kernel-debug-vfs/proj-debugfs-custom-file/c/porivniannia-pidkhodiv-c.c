/* Userspace Client in C (POSIX File I/O) */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

#define PATH_EVENT_COUNT "/sys/kernel/debug/inspector_demo/event_count"
#define PATH_CONTROL     "/sys/kernel/debug/inspector_demo/control"
#define PATH_EVENTS_LOG  "/sys/kernel/debug/inspector_demo/events_log"

static void read_and_print_file(const char *path, const char *title) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Error opening %s: %s\n", path, strerror(errno));
        return;
    }

    printf("=== %s ===\n", title);
    char buffer[512];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';
        fputs(buffer, stdout);
    }
    close(fd);
    printf("\n");
}

static void write_control(const char *val) {
    int fd = open(PATH_CONTROL, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Error opening control file: %s\n", strerror(errno));
        return;
    }
    ssize_t written = write(fd, val, strlen(val));
    if (written < 0) {
        fprintf(stderr, "Failed write to control: %s\n", strerror(errno));
    } else {
        printf("Written '%s' to control file.\n", val);
    }
    close(fd);
}

int main(void) {
    if (access("/sys/kernel/debug/inspector_demo", F_OK) != 0) {
        fprintf(stderr, "Error: debugfs node not found. Are you root?\n");
        return EXIT_FAILURE;
    }

    read_and_print_file(PATH_EVENT_COUNT, "Current Event Count");
    write_control("1");
    read_and_print_file(PATH_EVENTS_LOG, "Kernel Event Log");

    return EXIT_SUCCESS;
}
