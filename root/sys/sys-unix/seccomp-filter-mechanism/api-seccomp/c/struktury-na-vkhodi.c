struct seccomp_data {          /* вхідний буфер програми-фільтра */
    int   nr;                  /* зсув  0 */
    __u32 arch;                /* зсув  4  — константа AUDIT_ARCH_* */
    __u64 instruction_pointer; /* зсув  8 */
    __u64 args[6];             /* зсув 16, далі 24, 32, 40, 48, 56 */
};

struct sock_filter {           /* одна інструкція BPF, рівно 8 байтів */
    __u16 code;                /* що робити */
    __u8  jt, jf;              /* куди стрибати: правда / неправда */
    __u32 k;                   /* стала */
};

struct sock_fprog {
    unsigned short      len;   /* кількість інструкцій, 1…4096 */
    struct sock_filter *filter;
};

#define BPF_STMT(code, k)          { (unsigned short)(code), 0, 0, k }
#define BPF_JUMP(code, k, jt, jf)  { (unsigned short)(code), jt, jf, k }
