struct verity_sb {              /* 512 байтів, packed, little-endian */
        uint8_t  signature[8];      /*   0   "verity\0\0" */
        uint32_t version;           /*   8   формат суперблока — завжди 1 */
        uint32_t hash_type;         /*  12   0 — Chromium OS, 1 — типовий */
        uint8_t  uuid[16];          /*  16   UUID пристрою гешів */
        uint8_t  algorithm[32];     /*  32   "sha256" і нулі */
        uint32_t data_block_size;   /*  64   байти */
        uint32_t hash_block_size;   /*  68   байти */
        uint64_t data_blocks;       /*  72 */
        uint16_t salt_size;         /*  80   байтів солі, до 256 */
        uint8_t  _pad1[6];          /*  82 */
        uint8_t  salt[256];         /*  88 */
        uint8_t  _pad2[168];        /* 344 … 512 */
};
