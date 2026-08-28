/* Компактний індексний вузол EROFS (32 байти) */
struct erofs_inode_compact {
    uint16_t i_format;       /* Біти 0..0: 0=compact, 1=extended; Біти 1..3: layout */
    uint16_t i_xattr_icount; /* Кількість інлайн-атрибутів xattr */
    uint16_t i_mode;         /* Прапорці доступу та тип файла (POSIX mode_t) */
    uint16_t i_nlink;        /* Лічильник жорстких посилань */
    uint32_t i_size;         /* Розмір файла в байтах (до 4 ГБ) */
    uint32_t i_reserved;     /* Зарезервовано для вирівнювання */
    union {
        uint32_t raw_blkaddr;/* Фізична адреса першого блоку даних */
        uint32_t rdev;       /* Номер пристрою для mknod (major/minor) */
    } i_u;
    uint32_t i_ino;          /* Унікальний номер індексного вузла */
    uint16_t i_uid;          /* UID власника */
    uint16_t i_gid;          /* GID власника */
    uint32_t i_reserved2;    /* Зарезервовано; окремої чексуми вузол не має */
};

/* Розширений індексний вузол EROFS (64 байти) */
struct erofs_inode_extended {
    uint16_t i_format;       /* Біти 0..0: 1=extended; Біти 1..3: layout */
    uint16_t i_xattr_icount; /* Кількість інлайн-атрибутів xattr */
    uint16_t i_mode;         /* Прапорці доступу та тип файла */
    uint16_t i_reserved1;    /* Зарезервовано */
    uint64_t i_size;         /* Повний 64-бітний розмір файла в байтах */
    union {
        uint32_t raw_blkaddr;/* Фізична адреса першого блоку даних */
        uint32_t rdev;       /* Номер пристрою для special node */
    } i_u;
    uint32_t i_ino;          /* Унікальний номер індексного вузла */
    uint32_t i_uid;          /* Повний 32-бітний UID власника */
    uint32_t i_gid;          /* Повний 32-бітний GID власника */
    uint64_t i_mtime;        /* Час модифікації у секундах (POSIX Epoch) */
    uint32_t i_mtime_nsec;   /* Наносекунди часу модифікації */
    uint32_t i_nlink;        /* 32-бітний лічильник жорстких посилань */
    uint8_t  i_reserved2[16];/* Зарезервоване поле вирівнювання */
};
