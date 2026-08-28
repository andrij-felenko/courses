struct uffdio_copy {
    __u64 dst;        // адреса в зареєстрованому діапазоні, кратна сторінці
    __u64 src;        // буфер наглядача — обов'язково ПОЗА діапазоном
    __u64 len;
    __u64 mode;       // UFFDIO_COPY_MODE_DONTWAKE (1<<0) | _MODE_WP (1<<1)
    __s64 copy;       // вихід: скільки байтів лягло, або −errno
};

struct uffdio_zeropage {
    struct uffdio_range range;
    __u64 mode;       // UFFDIO_ZEROPAGE_MODE_DONTWAKE (1<<0)
    __s64 zeropage;   // вихід: скільки байтів, або −errno
};

struct uffdio_continue {
    struct uffdio_range range;
    __u64 mode;       // _MODE_DONTWAKE (1<<0) | _MODE_WP (1<<1)
    __s64 mapped;     // вихід: скільки байтів відображено, або −errno
};

struct uffdio_writeprotect {
    struct uffdio_range range;
    __u64 mode;       // _MODE_WP (1<<0) — поставити; без нього — зняти
                      // _MODE_DONTWAKE (1<<1)
};

struct uffdio_poison {
    struct uffdio_range range;
    __u64 mode;       // _MODE_DONTWAKE (1<<0)
    __s64 updated;    // вихід: скільки байтів отруєно, або −errno
};

struct uffdio_move {
    __u64 dst, src, len;
    __u64 mode;       // _MODE_DONTWAKE (1<<0) | _MODE_ALLOW_SRC_HOLES (1<<1)
    __s64 move;       // вихід: скільки байтів перенесено, або −errno
};
