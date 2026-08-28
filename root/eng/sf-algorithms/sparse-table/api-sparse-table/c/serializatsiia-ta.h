/* Заголовок та функції серіалізації мовою C */
#pragma pack(push, 1)
typedef struct {
    char magic[4];        /* 'S', 'P', 'T', 'B' */
    uint32_t version;     /* Версія формату: 1 */
    uint32_t element_size;/* Розмір типу T у байтах */
    uint64_t n;           /* Кількість елементів */
    uint32_t levels;      /* Кількість рівнів */
    uint32_t flags;       /* Бітові прапорці */
    uint64_t checksum;    /* CRC64 / xxHash64 */
} st_file_header_t;
#pragma pack(pop)

bool st_save_to_file(const sparse_table_t *st, const char *filepath);
sparse_table_t *st_load_from_mmap(const char *filepath);
