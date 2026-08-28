void daemonize(const char *name, ...)
{
	/* ... */
	vsnprintf(current->comm, sizeof(current->comm), name, args);
	exit_mm(current);
	set_special_pids(1, 1);
	current->signal->tty = NULL;

	/* Block and flush all signals */
	sigfillset(&blocked);
	sigprocmask(SIG_BLOCK, &blocked, NULL);
	flush_signals(current);

	/* Become as one with the init task */
	exit_fs(current);
	current->fs = init_task.fs;
	exit_files(current);
	current->files = init_task.files;

	reparent_to_init();
}
