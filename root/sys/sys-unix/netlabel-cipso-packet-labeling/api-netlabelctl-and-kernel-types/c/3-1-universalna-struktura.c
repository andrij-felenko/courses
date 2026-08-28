struct netlbl_lsm_secattr_mls {
    u32 lvl;                       /* числовий рівень чутливості (sensitivity) */
    struct netlbl_lsm_catmap *cat; /* динамічний бітмап категорій (categories) */
};

struct netlbl_lsm_secattr {
    u32 flags;                     /* бітова маска валідності полів */
    u32 type;                      /* джерело мітки: CIPSO, CALIPSO, UNLBL */
    char *domain;                  /* назва LSM-домену (якщо задана) */
    u32 secid;                     /* числовий Security ID ядра */
    struct netlbl_lsm_secattr_mls mls; /* параметри MLS */
    struct netlbl_lsm_cache *cache;    /* вказівник на кеш швидкого шляху */
};
