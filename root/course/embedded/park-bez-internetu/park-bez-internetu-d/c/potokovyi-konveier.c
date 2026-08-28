/* Звірка апаратного ідентифікатора та захист від відкату в C */
int check_hardware_and_rollback(uint16_t target_id, uint32_t version, 
                                uint16_t device_hw_id, uint32_t current_efuse_ver) {
    if (target_id != device_hw_id) {
        return -1; /* Невідповідність апаратної плати */
    }
    if (version < current_efuse_ver) {
        return -2; /* Спроба відкату на застарілу версію */
    }
    return 0; /* Перевірку пройдено успішно */
}
