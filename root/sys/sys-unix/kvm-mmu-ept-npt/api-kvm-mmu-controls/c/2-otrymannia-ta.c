struct kvm_dirty_log {
    __u32 slot;            /* Номер слота пам'яті */
    __u32 padding1;
    union {
        void *dirty_bitmap; /* Вказівник на виділений буфер бітової карти */
        __u64 padding2;
    };
};

struct kvm_clear_dirty_log {
    __u32 slot;            /* Номер слота пам'яті */
    __u32 num_pages;       /* Кількість сторінок для скидання */
    __u64 first_page;      /* Індекс першої сторінки діапазону */
    union {
        void *dirty_bitmap; /* Вказівник на бітову маску очищених сторінок */
        __u64 padding2;
    };
};
