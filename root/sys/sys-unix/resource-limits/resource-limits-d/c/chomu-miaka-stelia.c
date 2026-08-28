#include <sys/resource.h>

/* Забрати весь виданий нам запас дескрипторів. */
static void take_all_nofile(void)
{
    struct rlimit rl;

    if (getrlimit(RLIMIT_NOFILE, &rl) != 0)
        return;
    if (rl.rlim_cur >= rl.rlim_max)
        return;

    rl.rlim_cur = rl.rlim_max;          /* у межах жорсткого — без CAP_SYS_RESOURCE */
    setrlimit(RLIMIT_NOFILE, &rl);
}
