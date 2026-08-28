struct tpacket_bd_ts {
    unsigned int ts_sec;  /* Секунди Epoch */
    unsigned int ts_usec; /* Мікросекунди */
};

struct tpacket_hdr_v1 {
    uint32_t block_status;              /* Прапорець володіння та стану блоку */
    uint32_t num_pkts;                  /* Кількість пакетів, упакованих у цей блок */
    uint32_t offset_to_first_pkt;       /* Зсув у байтах від початку блоку до першого пакета */
    uint32_t blk_len;                   /* Загальний розмір записаних даних у блоці у байтах */
    uint64_t seq_num;                   /* Порядковий номер блоку (монотонний лічильник ядра) */
    struct tpacket_bd_ts ts_first_pkt;  /* Часова мітка першого пакета у блоці */
    struct tpacket_bd_ts ts_last_pkt;   /* Часова мітка останнього пакета у блоці */
};

struct tpacket_block_desc {
    uint32_t version;                   /* Версія заголовка блоку (TPACKET_V3) */
    uint32_t offset_to_priv;            /* Зсув до приватної області користувача */
    struct tpacket_hdr_v1 h1;           /* Внутрішній заголовок інформації про блок */
};
