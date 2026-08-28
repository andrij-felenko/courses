/* handle_signal() — обробник таки запускається */
switch (syscall_get_error(current, regs)) {
case -ERESTART_RESTARTBLOCK:
case -ERESTARTNOHAND:
    regs->ax = -EINTR;
    break;
case -ERESTARTSYS:
    if (!(ksig->ka.sa.sa_flags & SA_RESTART)) {
        regs->ax = -EINTR;
        break;
    }
    fallthrough;
case -ERESTARTNOINTR:
    regs->ax = regs->orig_ax;   /* номер виклику назад у rax */
    regs->ip -= 2;              /* лічильник на довжину `syscall` назад */
    break;
}

/* arch_do_signal_or_restart() — обробника немає */
switch (syscall_get_error(current, regs)) {
case -ERESTARTNOHAND:
case -ERESTARTSYS:
case -ERESTARTNOINTR:
    regs->ax = regs->orig_ax;
    regs->ip -= 2;
    break;
case -ERESTART_RESTARTBLOCK:
    regs->ax = get_nr_restart_syscall(regs);   /* підміна номера */
    regs->ip -= 2;
    break;
}
