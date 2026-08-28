loop:
	for(p = &proc[0]; p < &proc[NPROC]; p++)
	if(q->p_ppid == p->p_pid) {
		wakeup(&proc[1]);
		wakeup(p);
		for(p = &proc[0]; p < &proc[NPROC]; p++)
		if(q->p_pid == p->p_ppid) {
			p->p_ppid  = 1;
			if (p->p_stat == SSTOP)
				setrun(p);
		}
		swtch();
		/* no return */
	}
	q->p_ppid = 1;
	goto loop;
