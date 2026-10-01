#include <stdint.h>

// Структура основного заголовка бінарного образу ESP8266
typedef struct {
    uint8_t magic;           // Магічний байт (завжди 0xE9)
    uint8_t segment_count;   // Кількість сегментів у бінарному файлі
    uint8_t spi_mode;        // Режим роботи SPI (0: QIO, 1: QOUT, 2: DIO, 3: DOUT)
    uint8_t spi_speed_size;  // Старші 4 біти: частота SPI, молодші 4 біти: розмір флеш
    uint32_t entry_addr;     // Адреса точки входу для передачі управління
} __attribute__((packed)) esp_image_header_t;

// Структура заголовка окремого сегмента
typedef struct {
    uint32_t target_addr;    // Адреса призначення в RAM (IRAM: 0x40100000, DRAM: 0x3FFE8000)
    uint32_t segment_len;    // Довжина секції в байтах
} __attribute__((packed)) esp_segment_header_t;
