struct ptrace_syscall_info {
    __u8 op;                    /* Тип події: ENTRY, EXIT або SECCOMP */
    __u32 arch;                 /* Архітектура процесора (AUDIT_ARCH_*) */
    __u64 instruction_pointer;  /* Значення rip / pc */
    __u64 stack_pointer;        /* Значення rsp / sp */
    union {
        struct {
            __u64 nr;           /* Апаратний номер системного виклику */
            __u64 args[6];      /* Масив із 6 чисельних аргументів */
        } entry;
        struct {
            __s64 rval;         /* Повернене значення (код успіху або -errno) */
            __u8 is_error;      /* 1 якщо rval є кодом помилки, 0 якщо успіх */
        } exit;
        struct {
            __u64 nr;           /* Номер системного виклику */
            __u64 args[6];      /* Аргументи виклику */
            __u32 ret_data;     /* 16-бітні дані з BPF розрахунку */
        } seccomp;
    };
};
