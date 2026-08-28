// Структура ядра Linux drivers/spi/ (C)
struct spi_transfer {
    const void *tx_buf;     // Буфер передачі
    void       *rx_buf;     // Буфер прийому
    unsigned    len;        // Довжина в байтах
    uint32_t    speed_hz;   // Динамічна швидкість для цього сегмента
    uint16_t    delay_usecs;// Пауза після сегмента (t_lag)
    uint8_t     bits_per_word; // Розрядність слів (8, 16, 32)
    uint8_t     cs_change;  // Деактивувати CS між сегментами
};
