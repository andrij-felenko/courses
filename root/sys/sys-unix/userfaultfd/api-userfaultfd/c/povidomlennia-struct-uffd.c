struct uffd_msg {
    __u8  event;
    __u8  reserved1;
    __u16 reserved2;
    __u32 reserved3;
    union {
        struct { __u64 flags; __u64 address;
                 union { __u32 ptid; } feat; } pagefault;
        struct { __u32 ufd; }                  fork;
        struct { __u64 from, to, len; }        remap;
        struct { __u64 start, end; }           remove;
        struct { __u64 reserved1, reserved2, reserved3; } reserved;
    } arg;                 /* саме reserved тримає об'єднання на 24 байтах */
} __packed;
