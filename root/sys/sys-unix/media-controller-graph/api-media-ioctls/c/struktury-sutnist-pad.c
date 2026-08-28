struct media_device_info {
        char  driver[16];        /* ім'я драйвера, ASCII з нулем */
        char  model[32];         /* модель, UTF-8 */
        char  serial[40];        /* серійний номер або порожньо */
        char  bus_info[32];      /* розташування: "platform:…", "usb-…" */
        __u32 media_version;     /* версія API, KERNEL_VERSION(a,b,c) */
        __u32 hw_revision;       /* ревізія заліза, формат довільний */
        __u32 driver_version;    /* версія драйвера, KERNEL_VERSION(a,b,c) */
        __u32 reserved[31];
};

struct media_entity_desc {
        __u32 id;                /* задає програма; | MEDIA_ENT_ID_FLAG_NEXT */
        char  name[32];
        __u32 type;              /* насправді функція, MEDIA_ENT_F_* */
        __u32 revision;          /* завжди 0, поле застаріле */
        __u32 flags;             /* MEDIA_ENT_FL_* */
        __u32 group_id;          /* завжди 0, поле застаріле */
        __u16 pads;              /* скільки падів */
        __u16 links;             /* скільки вихідних зв'язків */
        __u32 reserved[4];
        union {
                struct { __u32 major, minor; } dev;   /* номери вузла в /dev */
                __u8 raw[184];
        };
};

struct media_pad_desc {
        __u32 entity;            /* чий це пад */
        __u16 index;             /* номер пада всередині сутности, з 0 */
        __u32 flags;             /* MEDIA_PAD_FL_* */
        __u32 reserved[2];
};

struct media_link_desc {
        struct media_pad_desc source;
        struct media_pad_desc sink;
        __u32 flags;             /* MEDIA_LNK_FL_* */
        __u32 reserved[2];
};

struct media_links_enum {
        __u32 entity;
        struct media_pad_desc  __user *pads;    /* NULL — не заповнювати */
        struct media_link_desc __user *links;
        __u32 reserved[4];
};

#define MEDIA_ENT_ID_FLAG_NEXT   (1U << 31)
