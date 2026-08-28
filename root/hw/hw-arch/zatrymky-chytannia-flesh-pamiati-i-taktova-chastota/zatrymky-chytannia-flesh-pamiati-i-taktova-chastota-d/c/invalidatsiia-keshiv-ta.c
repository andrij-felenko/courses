/* Безпечна інвалідація кешу інструкцій та даних у C */
void flash_cache_flush(void) {
    /* 1. Тимчасово вимикаємо кеші (біти ICEN та DCEN скидаються в 0) */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);

    /* 2. Подаємо команду скидання тегів (запис 1 у біти ICRST та DCRST) */
    FLASH_ACR_REG |= (FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);

    /* 3. Очищаємо біти скидання */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);

    /* 4. Вмикаємо кеші назад для нових звертань */
    FLASH_ACR_REG |= (FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);
}
