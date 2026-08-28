typedef struct {
    uint32_t magic;               /* Магічний маркер валідності (0x544F4F42) */
    uint32_t sequence;            /* Монотонний лічильник транзакцій */
    uint8_t  active_slot;         /* Ідентифікатор активного слота (0 = A, 1 = B) */
    uint8_t  slot_state;          /* Стан слота (PENDING_VERIFY, VALID, MARKED_BAD) */
    uint8_t  boot_attempts_left;  /* Залишок спроб старту (початково 3) */
    uint8_t  max_boot_attempts;   /* Максимальний ліміт спроб */
    uint32_t image_version;       /* Семантична версія прошивки */
    uint32_t image_crc;           /* Хеш-сума бінарного коду */
    uint32_t header_crc;          /* Контрольна сума CRC32 структури метаданих */
} __attribute__((packed)) boot_metadata_t;
