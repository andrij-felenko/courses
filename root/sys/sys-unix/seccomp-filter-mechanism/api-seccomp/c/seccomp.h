#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>

/* давніші двері: без прапорців і без значення, що повертається */
int prctl(PR_SET_SECCOMP /* 22 */, unsigned long mode, struct sock_fprog *prog);
int prctl(PR_GET_SECCOMP /* 21 */);

/* сучасні двері; обгортки в glibc немає — лише через syscall(2) */
int syscall(SYS_seccomp, unsigned int operation, unsigned int flags, void *args);
