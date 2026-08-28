#include <linux/filter.h>
#include <linux/seccomp.h>

struct sock_filter {
    __u16 code;   /* Код операції BPF (інструкція завантаження, переходу або повернення) */
    __u8  jt;     /* Зсув переходу при True (кількість інструкцій для пропуску) */
    __u8  jf;     /* Зсув переходу при False */
    __u32 k;      /* Багатоцільове поле (константа, номер виклику, зміщення в пам'яті) */
};

struct sock_fprog {
    unsigned short      len;     /* Кількість інструкцій у масиві filter */
    struct sock_filter *filter;  /* Вказівник на масив інструкцій */
};

struct seccomp_data {
    int   nr;                    /* Номер системного виклику (__NR_*) */
    __u32 arch;                  /* Ідентифікатор архітектури (AUDIT_ARCH_X86_64 тощо) */
    __u64 instruction_pointer;   /* Адреса інструкції CPU, що ініціювала виклик */
    __u64 args[6];               /* 6 аргументів системного виклику */
};
