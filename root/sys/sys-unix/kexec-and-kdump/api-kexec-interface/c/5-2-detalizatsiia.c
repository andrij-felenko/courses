struct elf_prstatus {
    struct elf_siginfo pr_info;    // Інформація про сигнал аварії
    short pr_cursig;               // Поточний сигнал
    unsigned long pr_sigpend;      // Зависші сигнали
    unsigned long pr_sighold;      // Заблоковані сигнали
    pid_t pr_pid;                  // PID процесу, що виконувався на цьому CPU
    pid_t pr_ppid;                 // PPID батьківського процесу
    pid_t pr_pgrp;                 // Група процесів
    pid_t pr_sid;                  // Сесія
    struct user_regs_struct pr_reg;// Збережені апаратні регістри CPU (RAX, RBX, RIP, RSP, RFLAGS)
};
