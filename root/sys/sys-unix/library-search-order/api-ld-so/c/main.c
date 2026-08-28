typedef struct {
    size_t dls_size;           /* Загальний розмір буфера в байтах */
    unsigned int dls_cnt;      /* Кількість елементів у масиві dls_serpath */
    Dl_serpath dls_serpath[1]; /* Масив змінної довжини із записами шляхів */
} Dl_serinfo;

typedef struct {
    char *dls_name;            /* Абсолютний шлях до каталогу пошуку */
    unsigned int dls_flags;    /* Джерело походження шляху */
} Dl_serpath;
