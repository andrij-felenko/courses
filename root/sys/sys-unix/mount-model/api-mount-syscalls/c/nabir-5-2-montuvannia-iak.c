#define _GNU_SOURCE
#include <linux/mount.h>      /* FSOPEN_*, FSCONFIG_*, MOVE_MOUNT_*, MOUNT_ATTR_* */
#include <sys/syscall.h>
#include <unistd.h>

static int sys_fsopen(const char *fs, unsigned f)
{ return syscall(SYS_fsopen, fs, f); }

static int sys_fsconfig(int fd, unsigned cmd, const char *k, const void *v, int aux)
{ return syscall(SYS_fsconfig, fd, cmd, k, v, aux); }

static int sys_fsmount(int fd, unsigned f, unsigned attr)
{ return syscall(SYS_fsmount, fd, f, attr); }

static int sys_move_mount(int ffd, const char *fp, int tfd, const char *tp, unsigned f)
{ return syscall(SYS_move_mount, ffd, fp, tfd, tp, f); }
