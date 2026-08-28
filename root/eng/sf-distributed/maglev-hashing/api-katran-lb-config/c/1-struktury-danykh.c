#include <linux/types.h>

/* Ідентифікатор віртуального сервісу (VIP Key) */
struct vip_definition {
    __u32 vip;          /* IPv4-адреса або префікс IPv6 у мережевому порядку байтів */
    __u16 port;         /* Порт сервісу (наприклад, 80, 443) */
    __u8  proto;        /* Протокол транспортного рівня (IPPROTO_TCP або IPPROTO_UDP) */
    __u8  flags;        /* Прапорці поведінки (VIP_FLAG_QUIC, VIP_FLAG_DSR) */
};

/* Метадані віртуального сервісу (VIP Value) */
struct vip_meta {
    __u32 flags;        /* Режими маршрутизації: DSR, GUE, IPIP */
    __u32 table_size;   /* Розмір активної таблиці Maglev (зазвичай 65537) */
    __u32 vip_num;      /* Внутрішній числовий ідентифікатор VIP */
};

/* Дескриптор цільового сервера (Real Backend Definition) */
struct real_definition {
    __u32 address;      /* IPv4/IPv6-адреса реального сервера */
    __u32 flags;        /* Прапорці доступності та типу тунелювання */
    __u16 port;         /* Цільовий порт на бекенді */
    __u8  weight;       /* Відносна вага сервера в таблиці Maglev */
    __u8  pad;
};

/* Ключ потоку для таблиці сесій (Flow Key) */
struct flow_key {
    __u32 src;          /* IP-адреса клієнта */
    __u32 dst;          /* VIP-адреса балансувальника */
    __u16 src_port;     /* Порт клієнта */
    __u16 dst_port;     /* Порт сервісу */
    __u8  proto;        /* TCP / UDP */
    __u8  pad[3];
};

/* Запис у таблиці активних сесій (Flow Value) */
struct flow_value {
    __u32 backend_idx;  /* Індекс сервера в масиві реальних серверів */
    __u64 last_seen;    /* Часова мітка останнього пакета в наносекундах */
};
