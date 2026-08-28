#define _GNU_SOURCE
#include <sys/fanotify.h>
#include <fcntl.h>      // AT_FDCWD
#include <unistd.h>
#include <iostream>
#include <vector>
#include <cstddef>

int main() {
    int fd = fanotify_init(FAN_CLASS_NOTIF | FAN_REPORT_DFID_NAME | FAN_CLOEXEC, 0);
    if (fd < 0) { std::perror("fanotify_init"); return 1; }

    if (fanotify_mark(fd, FAN_MARK_ADD | FAN_MARK_FILESYSTEM,
                      FAN_CREATE | FAN_DELETE | FAN_MOVED_TO | FAN_ONDIR,
                      AT_FDCWD, "/srv") < 0) { std::perror("fanotify_mark"); close(fd); return 1; }

    alignas(struct fanotify_event_metadata) char buf[8192];
    for (;;) {
        ssize_t n = read(fd, buf, sizeof(buf));
        if (n <= 0) break;
        auto *m = reinterpret_cast<struct fanotify_event_metadata *>(buf);
        for (; FAN_EVENT_OK(m, n); m = FAN_EVENT_NEXT(m, n)) {
            if (m->vers != FANOTIFY_METADATA_VERSION) { close(fd); return 2; }
            std::cout << "mask=" << std::hex << m->mask << std::dec
                      << " pid=" << m->pid << "\n";
        }
    }
    close(fd);
    return 0;
}
