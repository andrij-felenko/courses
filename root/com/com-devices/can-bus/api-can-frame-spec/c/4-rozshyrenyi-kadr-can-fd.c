/* C: структура кадру CAN FD у <linux/can.h> */
#include <linux/can.h>

struct canfd_frame {
    can_id_t can_id;  /* 32-бітний ID та прапорці (EFF, RTR, ERR) */
    __u8     len;     /* Фактична довжина навантаження (від 0 до 64) */
    __u8     flags;   /* Прапорці CAN FD (CANFD_BRS, CANFD_ESI) */
    __u8     __res0;  /* Зарезервовано */
    __u8     __res1;  /* Зарезервовано */
    __u8     data[64] __attribute__((aligned(8))); /* Буфер 64 байти */
};

#define CANFD_BRS 0x01 /* Bit Rate Switch: перемикання на високу швидкість */
#define CANFD_ESI 0x02 /* Error State Indicator: 0 = Active, 1 = Passive */
