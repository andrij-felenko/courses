#include <linux/filter.h>

struct sock_filter {
    __u16 code;  /* Код інструкції (наприклад, BPF_LD | BPF_W | BPF_ABS) */
    __u8  jt;    /* Зміщення переходу при істинності умови (Jump True) */
    __u8  jf;    /* Зміщення переходу при хибності умови (Jump False) */
    __u32 k;     /* Багатофункціональне поле операнда / зміщення / константи */
};

struct sock_fprog {
    unsigned short len;         /* Кількість інструкцій BPF у масиві */
    struct sock_filter *filter; /* Вказівник на масив інструкцій */
};
