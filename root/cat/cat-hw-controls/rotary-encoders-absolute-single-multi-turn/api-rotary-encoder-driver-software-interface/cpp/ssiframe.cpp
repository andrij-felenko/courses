#include <cstdint>
#include <cstdbool>

// Клас кадру SSI для C++ систем керування
struct SsiFrame {
    uint32_t raw_gray_code{0};  // 25-бітове значення у коді Ґрея
    uint16_t turn_count{0};      // Декодована кількість обертів
    uint16_t position_single{0}; // Декодована однооборотна позиція
    bool     is_valid{false};    // Прапорець готовості та цілісності
};

// Клас кадру BiSS-C з вбудованим контролем цілісності
struct BisscFrame {
    uint32_t position_raw{0};    // 32-бітове двійкове значення позиції
    bool     error_flag{true};   // Апаратна помилка E (active low)
    bool     warning_flag{true}; // Апаратне попередження W (active low)
    uint8_t  crc_received{0};    // Прийнята 6-бітова контрольна сума
    bool     crc_valid{false};   // Результат перевірки полінома
};
