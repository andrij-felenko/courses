#include <sys/inotify.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <cstddef>

int main() {
    int ifd = inotify_init1(IN_CLOEXEC);
    if (ifd == -1) return 1;

    inotify_add_watch(ifd, "/srv/app/src",
                      IN_CREATE | IN_CLOSE_WRITE | IN_MOVED_TO | IN_DELETE);

    alignas(struct inotify_event) char buf[4096];
    for (;;) {
        ssize_t n = read(ifd, buf, sizeof(buf));
        if (n <= 0) break;
        for (char *q = buf; q < buf + n; ) {
            auto *e = reinterpret_cast<const struct inotify_event *>(q);
            std::cout << "wd=" << e->wd
                      << " mask=" << std::hex << e->mask << std::dec
                      << " cookie=" << e->cookie
                      << " name=" << (e->len ? e->name : "(сам об'єкт стеження)") << "\n";
            q += sizeof(struct inotify_event) + e->len;
        }
    }
    close(ifd);
    return 0;
}
