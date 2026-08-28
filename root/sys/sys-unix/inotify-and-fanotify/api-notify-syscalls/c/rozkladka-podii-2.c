#define _GNU_SOURCE
#include <sys/fanotify.h>
#include <fcntl.h>      /* AT_FDCWD */
#include <unistd.h>
#include <stdio.h>

int main(void) {
    int fd = fanotify_init(FAN_CLASS_NOTIF | FAN_REPORT_DFID_NAME | FAN_CLOEXEC, 0);
    if (fd < 0) { perror("fanotify_init"); return 1; }

    if (fanotify_mark(fd, FAN_MARK_ADD | FAN_MARK_FILESYSTEM,
                      FAN_CREATE | FAN_DELETE | FAN_MOVED_TO | FAN_ONDIR,
                      AT_FDCWD, "/srv") < 0) { perror("fanotify_mark"); close(fd); return 1; }

    char buf[8192];
    for (;;) {
        ssize_t n = read(fd, buf, sizeof buf);
        if (n <= 0) break;
        struct fanotify_event_metadata *m = (struct fanotify_event_metadata *) buf;
        for (; FAN_EVENT_OK(m, n); m = FAN_EVENT_NEXT(m, n)) {
            if (m->vers != FANOTIFY_METADATA_VERSION) { close(fd); return 2; }
            printf("mask=%llx pid=%d\n", (unsigned long long) m->mask, m->pid);
        }
    }
    close(fd);
    return 0;
}
