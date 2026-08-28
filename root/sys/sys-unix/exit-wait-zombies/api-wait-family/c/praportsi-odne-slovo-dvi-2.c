static int eligible_child(struct wait_opts *wo, bool ptrace, struct task_struct *p)
{
        if (!eligible_pid(wo, p))
                return 0;
        if (ptrace || (wo->wo_flags & __WALL))
                return 1;
        if ((p->exit_signal != SIGCHLD) ^ !!(wo->wo_flags & __WCLONE))
                return 0;
        return 1;
}
