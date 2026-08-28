/* Таблиця операцій апаратного драйвера енергонезалежної пам'яті */
typedef struct {
    /* Читання блоку даних з фізичної адреси */
    audit_status_t (*read)(uint32_t physical_addr, uint8_t *buf, size_t len);
    
    /* Запис сторінки Flash (розмір сторінки зазвичай 256 байтів, вирівняно) */
    audit_status_t (*write_page)(uint32_t physical_addr, const uint8_t *buf, size_t len);
    
    /* Стирання одного сектора Flash (зазвичай 4096 байтів) */
    audit_status_t (*erase_sector)(uint32_t sector_addr);
    
    /* Загальний розмір виділеної області пам'яті під аудит (у байтах) */
    uint32_t total_size_bytes;
    
    /* Розмір одного фізичного сектора (наприклад, 4096) */
    uint32_t sector_size_bytes;
} audit_flash_hal_t;
