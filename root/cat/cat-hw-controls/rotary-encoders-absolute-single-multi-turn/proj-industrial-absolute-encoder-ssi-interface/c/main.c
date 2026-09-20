#include <stdio.h>
#include "ssi_encoder.h"

int main(void) {
    printf("=== Драйвер декодування кадру SSI абсолютного енкодера ===\n");

    ssi_config_t config = {
        .singleturn_bits = 13,
        .multiturn_bits = 12,
        .use_gray_code = true
    };

    uint8_t test_frame[4] = { 0x4D, 0xA2, 0x14, 0x00 };
    test_frame[3] = calculate_crc8(test_frame, 3);

    ssi_decoded_data_t data;
    bool success = ssi_decode_frame(test_frame, sizeof(test_frame), &config, &data);

    printf("Результат декодування кадру:\n");
    printf("- Валідність кадру: %s\n", success ? "УСПІХ (CRC OK)" : "ПОМИЛКА");
    printf("- Код статусу: 0x%02X\n", data.status_flags);
    printf("- Сирий кут (двійковий): %u / %u\n", data.singleturn_raw, 1U << config.singleturn_bits);
    printf("- Обчислений кут ротора: %.2f град.\n", data.angle_degrees);
    printf("- Кількість повних обертів: %d\n", data.turns_count);

    return 0;
}
