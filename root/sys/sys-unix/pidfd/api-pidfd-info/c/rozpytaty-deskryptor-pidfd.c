#include <linux/pidfd.h>
#include <sys/ioctl.h>

struct pidfd_info {
    __u64 mask;      /* на вході — що просимо; на виході — що справді заповнено */
    __u64 cgroupid;
    __u32 pid, tgid, ppid;
    __u32 ruid, rgid, euid, egid, suid, sgid, fsuid, fsgid;
    __s32 exit_code;
    /* далі — поля, додані пізнішими ядрами */
};

int ioctl(int pidfd, PIDFD_GET_INFO, struct pidfd_info *info);
