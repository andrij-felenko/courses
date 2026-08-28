/* peerauth.c — сервер, що з'ясовує, хто на іншому кінці сокета.
 * cc -O2 -Wall -o peerauth peerauth.c */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/pidfd.h>      /* struct pidfd_info, PIDFD_GET_INFO — ядро 6.13+ */
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#ifndef SO_PEERPIDFD
#define SO_PEERPIDFD 77
#endif

struct verdict {
    uid_t uid;              /* хто просить */
    char  unit[128];        /* у якій одиниці systemd він живе */
};

static int probe_naive(int conn, struct verdict *v)
{
    struct ucred uc;
    socklen_t len = sizeof uc;
    if (getsockopt(conn, SOL_SOCKET, SO_PEERCRED, &uc, &len) < 0)
        return -1;
    v->uid = uc.uid;

    /* ↓↓↓ від цього рядка ціль названо ЧИСЛОМ і нічим більше ↓↓↓ */

    char path[64], line[512];
    v->unit[0] = '\0';

    snprintf(path, sizeof path, "/proc/%d/cgroup", uc.pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "0::", 3)) {          /* cgroup v2 — рівно один рядок */
            line[strcspn(line, "\n")] = '\0';
            snprintf(v->unit, sizeof v->unit, "%s", line + 3);
        }
    fclose(f);

    snprintf(path, sizeof path, "/proc/%d/status", uc.pid);
    f = fopen(path, "r");
    if (!f) return -1;
    while (fgets(line, sizeof line, f)) {
        unsigned ruid, euid;
        if (sscanf(line, "Uid: %u %u", &ruid, &euid) == 2) {
            v->uid = euid;                       /* чинний uid — уже не з сокета */
            break;
        }
    }
    fclose(f);
    return 0;
}
