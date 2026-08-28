/* kernel_wait4() — маска для wait, waitpid, wait3, wait4 */
if (options & ~(WNOHANG|WUNTRACED|WCONTINUED|__WNOTHREAD|__WCLONE|__WALL))
        return -EINVAL;

/* kernel_waitid() — маска для waitid, плюс вимога вибрати подію */
if (options & ~(WNOHANG|WNOWAIT|WEXITED|WSTOPPED|WCONTINUED|
                __WNOTHREAD|__WCLONE|__WALL))
        return -EINVAL;
if (!(options & (WEXITED|WSTOPPED|WCONTINUED)))
        return -EINVAL;
