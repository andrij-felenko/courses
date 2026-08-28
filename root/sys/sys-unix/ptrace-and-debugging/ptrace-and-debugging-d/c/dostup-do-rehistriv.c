struct user_regs_struct regs;
ptrace(PTRACE_GETREGS, pid, NULL, &regs);

/* На архітектурі x86_64:
 * regs.rip      — Instruction Pointer (адреса наступної інструкції)
 * regs.rsp      — Stack Pointer (вказівник на верхівку стека)
 * regs.orig_rax — Номер системного виклику (копія, збережена ядром)
 * regs.rax      — Код повернення виклику (на вході — заглушка -ENOSYS)
 * regs.rdi, regs.rsi, regs.rdx — Перші аргументи системного виклику
 */
