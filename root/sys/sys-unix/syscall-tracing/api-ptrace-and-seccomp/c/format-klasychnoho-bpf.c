struct sock_filter {
    __u16 code; /* Код операції (BPF_LD, BPF_JMP, BPF_RET тощо) */
    __u8  jt;   /* Зміщення переходу, якщо умова ІСТИННА (jump true) */
    __u8  jf;   /* Зміщення переходу, якщо умова ХИБНА (jump false) */
    __u32 k;    /* Константа або зміщення у структурі seccomp_data */
};

struct sock_fprog {
    unsigned short len;       /* Кількість інструкцій у масиві */
    struct sock_filter *filter; /* Масив інструкцій */
};
