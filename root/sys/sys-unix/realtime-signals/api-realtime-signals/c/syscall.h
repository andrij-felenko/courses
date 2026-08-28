#include <sys/syscall.h>
#include <unistd.h>

/* обгорток у glibc немає — лише через syscall(2) */
long syscall(SYS_rt_sigqueueinfo,   pid_t tgid,            int sig, siginfo_t *info);
long syscall(SYS_rt_tgsigqueueinfo, pid_t tgid, pid_t tid, int sig, siginfo_t *info);

/* під sigwaitinfo() і sigtimedwait(): timeout == NULL означає «без межі» */
long syscall(SYS_rt_sigtimedwait, const sigset_t *set, siginfo_t *info,
             const struct timespec *timeout, size_t sigsetsize);
