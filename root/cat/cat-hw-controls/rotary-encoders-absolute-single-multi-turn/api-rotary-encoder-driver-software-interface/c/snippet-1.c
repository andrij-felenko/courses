#include <stdint.h>
#include <stdbool.h>

// Структура сирого кадру SSI (12 біт обертів + 13 біт позиції)
typedef struct {
    uint32_t raw_gray_code;  // 25-бітове сире значення у коді Ґрея
    uint16_t turn_count;      // Декодована кількість обертів
    uint16_t position_single; // Декодована однооборотна позиція
    bool     is_valid;        // Стан валідності за тривалістю паузи
} ssi_frame_t;

// Структура кадру BiSS-C із бітами діагностики та CRC
typedef struct {
    uint32_t position_raw;    // 32-бітове двійкове значення позиції
    bool     error_flag;      // Прапорець апаратної помилки E (0 - помилка)
    bool     warning_flag;    // Прапорець попередження W (0 - деградація)
    uint8_t  crc_received;    // Отримана 6-бітова контрольна сума
    bool     crc_valid;       // Прапорець успішної перевірки CRC
} bissc_frame_t;
