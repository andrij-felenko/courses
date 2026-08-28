// Запис байта у стимул-порт ITM з очікуванням місця (основа CMSIS ITM_SendChar)
static inline void itm_send8(uint32_t port, uint8_t value) {
    if (!(ITM->TCR & ITM_TCR_ITMENA_Msk)) return;   // блок ITM вимкнено
    if (!(ITM->TER & (1u << port)))        return;   // цей порт не ввімкнено
    while (ITM->PORT[port].u32 == 0u) { }            // 0 = буфера нема, чекаємо
    ITM->PORT[port].u8 = value;                      // запис байта = відправлення
}

// Те саме одним 32-бітним словом — один пакет на 4 байти даних
static inline void itm_send32(uint32_t port, uint32_t value) {
    if (!(ITM->TCR & ITM_TCR_ITMENA_Msk)) return;
    if (!(ITM->TER & (1u << port)))        return;
    while (ITM->PORT[port].u32 == 0u) { }
    ITM->PORT[port].u32 = value;
}
