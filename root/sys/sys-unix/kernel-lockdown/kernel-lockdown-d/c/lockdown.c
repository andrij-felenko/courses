/* security/lockdown/lockdown.c */
static int lockdown_is_locked_down(enum lockdown_reason what)
{
	if (kernel_locked_down >= what) {
		if (lockdown_reasons[what])
			pr_notice_ratelimited("Lockdown: %s: %s is restricted; see man kernel_lockdown.7\n",
				  current->comm, lockdown_reasons[what]);
		return -EPERM;
	}
	return 0;
}
