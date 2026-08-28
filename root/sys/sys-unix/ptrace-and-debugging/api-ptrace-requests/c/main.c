struct user_regs_struct {
    unsigned long long r15;
    unsigned long long r14;
    unsigned long long r13;
    unsigned long long r12;
    unsigned long long rbp;
    unsigned long long rbx;
    unsigned long long r11;
    unsigned long long r10;
    unsigned long long r9;
    unsigned long long r8;
    unsigned long long rax; /* На вході у виклик — заглушка -ENOSYS; на виході — код повернення */
    unsigned long long rcx;
    unsigned long long rdx; /* 3-й аргумент виклику */
    unsigned long long rsi; /* 2-й аргумент виклику */
    unsigned long long rdi; /* 1-й аргумент виклику */
    unsigned long long orig_rax; /* Номер системного виклику (єдине надійне джерело на вході) */
    unsigned long long rip; /* Instruction Pointer (лічильник інструкцій) */
    unsigned long long cs;
    unsigned long long eflags;
    unsigned long long rsp; /* Stack Pointer (вказівник стека) */
    unsigned long long ss;
    unsigned long long fs_base;
    unsigned long long gs_base;
    unsigned long long ds;
    unsigned long long es;
    unsigned long long fs;
    unsigned long long gs;
};
