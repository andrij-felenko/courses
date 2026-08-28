/* pinbuf.h — цей файл читають і модуль, і програма */
#ifndef _UAPI_PINBUF_H
#define _UAPI_PINBUF_H

#include <linux/types.h>
#include <linux/ioctl.h>

struct pinbuf_req {
        __u64 addr;    /* → адреса буфера; вирівнювання не потрібне   */
        __u64 len;     /* → довжина, байтів                           */
        __u64 sum;     /* ← сума всіх байтів, яку побачило ядро       */
        __u32 pages;   /* ← скільки сторінок довелося закріпити       */
        __u32 segs;    /* ← на скільки суцільних сегментів вони лягли */
};

#define PINBUF_IOC_TYPE 'p'
#define PINBUF_XFER _IOWR(PINBUF_IOC_TYPE, 0x01, struct pinbuf_req)

#endif
