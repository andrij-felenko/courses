struct user_regs_struct {
    unsigned long r15;
    unsigned long r14;
    unsigned long r13;
    unsigned long r12;
    unsigned long rbp;
    unsigned long rbx;
    unsigned long r11;
    unsigned long r10;
    unsigned long r8;
    unsigned long r9;
    unsigned long rax;
    unsigned long rcx;
    unsigned long rdx;
    unsigned long rsi;
    unsigned long rdi;
    unsigned long orig_rax; /* Початковий номер системного виклику */
    unsigned long rip;      /* Вказівник на поточну інструкцію (IP) */
    unsigned long cs;
    unsigned long eflags;   /* Прапорці процесора (rflags) */
    unsigned long rsp;      /* Вказівник на вершину стека (SP) */
    unsigned long ss;
    unsigned long fs_base;
    unsigned long gs_base;
    unsigned long ds;
    unsigned long es;
    unsigned long fs;
    unsigned long gs;
};
