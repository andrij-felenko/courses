/* pulsegen.h — цей файл читають обидві сторони */
#ifndef _UAPI_PULSEGEN_H
#define _UAPI_PULSEGEN_H

#include <linux/types.h>
#include <linux/ioctl.h>

struct pulse_cfg {
        __u32 period_us;      /* період імпульсу, мкс: 10 … 1000000 */
        __u32 duty_permille;  /* заповнення, ‰: 1 … 999          */
};

struct pulse_burst {
        __u32 want;           /* → скільки імпульсів замовляємо        */
        __u32 __pad;          /*   мусить бути 0                       */
        __u64 issued;         /* ← усього видано від завантаження      */
};

#define PULSE_IOC_TYPE 'B'

#define PULSE_SET_CFG  _IOW(PULSE_IOC_TYPE, 0x01, struct pulse_cfg)
#define PULSE_GET_CFG  _IOR(PULSE_IOC_TYPE, 0x02, struct pulse_cfg)
#define PULSE_BURST   _IOWR(PULSE_IOC_TYPE, 0x03, struct pulse_burst)

#endif
