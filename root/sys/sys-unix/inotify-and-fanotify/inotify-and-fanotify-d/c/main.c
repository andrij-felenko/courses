#include <sys/inotify.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    int ifd = inotify_init1(IN_CLOEXEC);
    if (ifd == -1) return 1;

    inotify_add_watch(ifd, "/srv/app/src",
                      IN_CREATE | IN_CLOSE_WRITE | IN_MOVED_TO | IN_DELETE);

    char buf[4096] __attribute__((aligned(__alignof__(struct inotify_event))));
    for (;;) {
        ssize_t n = read(ifd, buf, sizeof buf);
        if (n <= 0) break;
        for (char *q = buf; q < buf + n; ) {
            struct inotify_event *e = (struct inotify_event *) q;
            printf("wd=%d mask=%08x cookie=%u name=%s\n",
                   e->wd, e->mask, e->cookie,
                   e->len ? e->name : "(сам об'єкт стеження)");
            q += sizeof(struct inotify_event) + e->len;
        }
    }
    close(ifd);
    return 0;
}
