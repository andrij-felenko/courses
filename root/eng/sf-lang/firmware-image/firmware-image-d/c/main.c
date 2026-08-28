// як ці поля лежать у файлі образу (спрощено, ESP32):
struct esp_image_header {
    uint8_t  magic;        // 0xE9 — підпис «це образ»
    uint8_t  segment_count;// 1   — далі один сегмент
    uint8_t  spi_mode;     // режим Flash
    uint8_t  spi_size_freq;// розмір + частота Flash
    uint32_t entry_addr;   // 0x40080000 — звідки виконувати
};
struct esp_segment_header {
    uint32_t load_addr;    // 0x40080000 — куди класти байти
    uint32_t data_len;     // 2 — стільки байтів даних далі
};
