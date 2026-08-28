struct pi_desc {
    __u32 pir[8];        /* PIR[255:0]: 256-бітний бітмап очікуваних переривань */
    union {
        struct {
            __u32 on : 1;      /* Bit 256: Outstanding Notification (є нові IRQ) */
            __u32 sn : 1;      /* Bit 257: Suppress Notification (придушити IPI) */
            __u32 rsvd_1 : 14;
            __u32 nv : 8;      /* Bits 271:264: Notification Vector (наприклад 0xF2) */
            __u32 rsvd_2 : 8;
            __u32 ndst;        /* Bits 319:288: Notification Destination (Physical APIC ID) */
        };
        __u64 control;
    };
    __u32 rsvd[6];
} __aligned(64);
