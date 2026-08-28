struct fuse_init_in {
    uint32_t major;        /* Мажорна версія FUSE протоколу (7) */
    uint32_t minor;        /* Мінорна версія FUSE протоколу (наприклад, 38) */
    uint32_t max_readahead;/* Максимальний розмір попереднього читання в байтах */
    uint32_t flags;        /* Бітова маска прапорців capabilities гостя */
    uint32_t flags2;       /* Розширені прапорці capabilities */
    uint32_t unused[11];
};

struct fuse_init_out {
    uint32_t major;
    uint32_t minor;
    uint32_t max_readahead;
    uint32_t flags;
    uint16_t max_background;
    uint16_t congestion_threshold;
    uint32_t max_write;    /* Максимальний розмір блоку запису */
    uint32_t time_gran;    /* Точність позначок часу (в наносекундах) */
    uint16_t max_pages;    /* Максимальна кількість сторінок у виклику */
    uint16_t map_alignment;/* Вирівнювання для DAX мапінгів (log2 від розміру сторінки) */
    uint32_t flags2;       /* Розширені прапорці capabilities */
    uint32_t unused[7];    /* Зарезервовано; частину вже зайняли новіші версії протоколу */
};
