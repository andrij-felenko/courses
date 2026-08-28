void proc_task_name(struct seq_file *m, struct task_struct *p, bool escape)
{
	char tcomm[64];

	if (p->flags & PF_WQ_WORKER)
		wq_worker_comm(tcomm, sizeof(tcomm), p);
	else if (p->flags & PF_KTHREAD)
		get_kthread_comm(tcomm, sizeof(tcomm), p);
	else
		__get_task_comm(tcomm, sizeof(tcomm), p);
	…
}
