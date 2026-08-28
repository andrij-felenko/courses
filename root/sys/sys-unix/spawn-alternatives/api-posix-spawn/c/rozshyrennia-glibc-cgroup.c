#define _GNU_SOURCE
#include <fcntl.h>
#include <spawn.h>
#include <sys/wait.h>

/* Народити дитину одразу в потрібній контрольній групі. */
int cg = open("/sys/fs/cgroup/build.slice/job.scope", O_DIRECTORY | O_RDONLY);
posix_spawnattr_setcgroup_np(&at, cg);
posix_spawnattr_setflags(&at, POSIX_SPAWN_SETCGROUP);

/* Дістати не номер, а дескриптор процесу. */
int pidfd;
char *argv[] = { "sleep", "10", NULL };
int rc = pidfd_spawnp(&pidfd, "sleep", NULL, NULL, argv, environ);
if (rc == 0) {
    siginfo_t info;
    waitid(P_PIDFD, pidfd, &info, WEXITED);
    close(pidfd);
}
