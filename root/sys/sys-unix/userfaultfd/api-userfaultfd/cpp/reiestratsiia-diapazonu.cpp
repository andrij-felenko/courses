struct uffdio_range {
    __u64 start;      // кратна розміру сторінки
    __u64 len;        // кратна розміру сторінки, не нуль
};

struct uffdio_register {
    struct uffdio_range range;
    __u64 mode;       // вхід:  MISSING | WP | MINOR
    __u64 ioctls;     // вихід: які операції дозволено саме цьому діапазону
};

#define UFFDIO_REGISTER_MODE_MISSING  (1<<0)
#define UFFDIO_REGISTER_MODE_WP       (1<<1)
#define UFFDIO_REGISTER_MODE_MINOR    (1<<2)
