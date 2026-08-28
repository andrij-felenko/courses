static struct security_hook_list yama_hooks[] __ro_after_init = {
	LSM_HOOK_INIT(ptrace_access_check, yama_ptrace_access_check),
	LSM_HOOK_INIT(ptrace_traceme,      yama_ptrace_traceme),
	LSM_HOOK_INIT(task_prctl,          yama_task_prctl),
	LSM_HOOK_INIT(task_free,           yama_task_free),
};

static int __init yama_init(void)
{
	security_add_hooks(yama_hooks, ARRAY_SIZE(yama_hooks), &yama_lsmid);
	yama_init_sysctl();
	return 0;
}

DEFINE_LSM(yama) = {
	.name = "yama",
	.init = yama_init,
};
