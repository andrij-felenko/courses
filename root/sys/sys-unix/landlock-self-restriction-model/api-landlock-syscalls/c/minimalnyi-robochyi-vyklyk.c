#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/landlock.h>
#include <stdio.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* права, яких давніші ядра не знають, за версією ABI */
static const struct { int abi; __u64 bits; } fs_since[] = {
    { 2, LANDLOCK_ACCESS_FS_REFER },
    { 3, LANDLOCK_ACCESS_FS_TRUNCATE },
    { 5, LANDLOCK_ACCESS_FS_IOCTL_DEV },
};

int main(void)
{
    struct landlock_ruleset_attr rs = {
        .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE |
                             LANDLOCK_ACCESS_FS_WRITE_FILE |
                             LANDLOCK_ACCESS_FS_TRUNCATE |
                             LANDLOCK_ACCESS_FS_REFER,
    };
    struct landlock_path_beneath_attr rule = {
        .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE,
    };
    int abi, fd;

    abi = syscall(SYS_landlock_create_ruleset, NULL, 0,
                  LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1)
        return perror("landlock"), 1;              /* ENOSYS або EOPNOTSUPP */
    for (unsigned i = 0; i < sizeof fs_since / sizeof *fs_since; i++)
        if (abi < fs_since[i].abi)
            rs.handled_access_fs &= ~fs_since[i].bits;

    fd = syscall(SYS_landlock_create_ruleset, &rs, sizeof rs, 0);
    if (fd < 0)
        return perror("create_ruleset"), 1;

    rule.parent_fd = open("/usr/share", O_PATH | O_CLOEXEC);
    if (rule.parent_fd < 0)
        return perror("/usr/share"), 1;
    if (syscall(SYS_landlock_add_rule, fd, LANDLOCK_RULE_PATH_BENEATH, &rule, 0))
        return perror("add_rule"), 1;
    close(rule.parent_fd);

    prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);        /* обов'язково ДО restrict_self */
    if (syscall(SYS_landlock_restrict_self, fd, 0))
        return perror("restrict_self"), 1;
    close(fd);

    if (open("/etc/passwd", O_RDONLY) < 0)
        perror("/etc/passwd");                     /* → Permission denied */
    return 0;
}
