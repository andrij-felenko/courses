#define NETLBL_CATMAP_MAPTYPE      unsigned long
#define NETLBL_CATMAP_MAPBITS      (sizeof(NETLBL_CATMAP_MAPTYPE) * 8)
#define NETLBL_CATMAP_MAPCNT       4
#define NETLBL_CATMAP_SIZE         (NETLBL_CATMAP_MAPBITS * NETLBL_CATMAP_MAPCNT)

struct netlbl_lsm_catmap {
    u32 startbit;                  /* початковий бітовий індекс вузла (кратний 256) */
    NETLBL_CATMAP_MAPTYPE bitmap[NETLBL_CATMAP_MAPCNT]; /* бітова маска 256 бітів */
    struct netlbl_lsm_catmap *next;/* вказівник на наступний вузол категорій */
};
