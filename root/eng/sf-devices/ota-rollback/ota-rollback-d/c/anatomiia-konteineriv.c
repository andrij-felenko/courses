struct image_header {
    uint32_t ih_magic;             /* Магічне число MCUboot (0x96f3b83d) */
    uint32_t ih_load_addr;         /* Базова адреса завантаження (якщо XIP, то 0) */
    uint16_t ih_hdr_size;          /* Розмір заголовка (типово 0x20 = 32 байти) */
    uint16_t ih_protect_tlv_size;  /* Розмір області захищених дескрипторів TLV */
    uint32_t ih_img_size;          /* Точний розмір тіла прошивки без заголовка та TLV */
    uint32_t ih_flags;             /* Бітові прапорці (зашифрований образ, RAM load) */
    struct {
        uint8_t  iv_major;
        uint8_t  iv_minor;
        uint16_t iv_revision;
        uint32_t iv_build_num;
    } ih_ver;                      /* Семантична версія образу (SemVer) */
    uint32_t _pad1;
};
