#define FUSE_SETUPMAPPING    48
#define FUSE_REMOVEMAPPING 49

struct fuse_setupmapping_in {
    uint64_t fh;             /* Хендл відкритого файла, виданий у відповіді на FUSE_OPEN */
    uint64_t foffset;        /* Зсув усередині файла на хості */
    uint64_t len;            /* Довжина ділянки відображення в байтах */
    uint64_t flags;          /* Прапорці доступу (FUSE_SETUPMAPPING_FLAG_READ / WRITE) */
    uint64_t moffset;        /* Зсув усередині Shared Memory Region ВМ */
};

struct fuse_removemapping_in {
    uint32_t count;          /* Кількість елементів для видалення */
    uint32_t pad;
    /* Далі слідує масив struct fuse_removemapping_one[count] */
};

struct fuse_removemapping_one {
    uint64_t moffset;        /* Зсув усередині Shared Memory Region ВМ */
    uint64_t len;            /* Довжина ділянки для звільнення */
};
