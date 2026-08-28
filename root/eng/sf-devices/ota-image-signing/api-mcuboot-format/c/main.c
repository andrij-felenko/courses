struct image_version {
    uint8_t  iv_major;        /* Старший номер версії */
    uint8_t  iv_minor;        /* Молодший номер версії */
    uint16_t iv_revision;     /* Номер ревізії */
    uint32_t iv_build_num;    /* Номер збірки */
};

struct image_header {
    uint32_t ih_magic;             /* Магічне число образу (0x96f3b83d) */
    uint32_t ih_load_addr;         /* Адреса завантаження в RAM (0 для XIP) */
    uint16_t ih_hdr_size;          /* Фізичний розмір заголовка та вирівнювання коду */
    uint16_t ih_protect_tlv_size;  /* Сумарний розмір захищеної зони TLV */
    uint32_t ih_img_size;          /* Розмір виконуваного двійкового коду програми */
    uint32_t ih_flags;             /* Бітова маска властивостей та режимів образу */
    struct image_version ih_ver;   /* 8-байтна семантична версія прошивки */
    uint32_t _pad1;                /* Резервне поле для вирівнювання 32 байтів */
};
