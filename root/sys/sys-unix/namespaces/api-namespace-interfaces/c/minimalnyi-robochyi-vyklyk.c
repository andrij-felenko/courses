#define _GNU_SOURCE
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/wait.h>
#include <unistd.h>

static void put(const char *path, const char *s) {
    int fd = open(path, O_WRONLY);
    if (fd < 0 || write(fd, s, strlen(s)) < 0) { perror(path); exit(1); }
    close(fd);
}

int main(void) {
    char buf[64];
    uid_t uid = getuid();
    gid_t gid = getgid();

    /* 1. Три простори одним викликом. CAP_SYS_ADMIN не потрібен:
          простір користувачів створюється першим і дає права на решту. */
    if (unshare(CLONE_NEWUSER | CLONE_NEWPID | CLONE_NEWNS) < 0) {
        perror("unshare"); return 1;
    }

    /* 2. Мапа: нуль усередині — це наш звичайний ідентифікатор зовні.
          setgroups мусить бути заборонено ДО запису gid_map. */
    put("/proc/self/setgroups", "deny");
    snprintf(buf, sizeof buf, "0 %u 1\n", uid);  put("/proc/self/uid_map", buf);
    snprintf(buf, sizeof buf, "0 %u 1\n", gid);  put("/proc/self/gid_map", buf);

    /* 3. Свіжа копія дерева монтувань усе ще ділиться подіями з системою —
          відв'язуємо, інакше наш /proc вилізе назовні. */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0) {
        perror("make-rprivate"); return 1;
    }

    /* 4. Ми самі лишилися в старому просторі номерів; новий дістане дитина,
          і саме вона буде там процесом номер 1. */
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }

    if (child == 0) {
        if (mount("proc", "/proc", "proc", 0, NULL) < 0) {
            perror("mount /proc"); _exit(1);
        }
        execlp("ps", "ps", "-ef", (char *)NULL);
        _exit(127);
    }

    waitpid(child, NULL, 0);
    return 0;
}
