#include <linux/types.h>
#include <linux/filter.h>

/* Структура інструкції віртуальної машини BPF (8 байтів) */
struct sock_filter {
    __u16 code; /* Код операції (Opcode), клас та режим адресації */
    __u8  jt;   /* Зміщення переходу при істинній умові (Jump True) */
    __u8  jf;   /* Зміщення переходу при хибній умові (Jump False) */
    __u32 k;    /* Універсальний аргумент: константа, зміщення або довжина */
};

/* Контейнер програми BPF для системного виклику setsockopt */
struct sock_fprog {
    unsigned short      len;    /* Кількість інструкцій у масиві */
    struct sock_filter *filter; /* Покажчик на масив інструкцій */
};
