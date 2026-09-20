#ifndef ENCODER_SSI_H
#define ENCODER_SSI_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура розпарсеного кадру абсолютного енкодера
 */
typedef struct {
    uint32_t single_turn_pos;   /**< Однооборотна кутова позиція (відліки) */
    uint32_t multi_turn_count;  /**< Лічильник повних обертів */
    bool error_flag;            /**< Прапорець наявності апаратної помилки енкодера (true - помилка) */
    bool warning_flag;          /**< Прапорець попередження (true - попередження) */
    uint8_t crc;                /**< Зчитане значення CRC (для BiSS-C) */
    bool crc_valid;             /**< Результат перевірки цілісності кадру CRC */
    uint64_t raw_frame;         /**< Сирий 64-бітне значення кадру даних */
} encoder_frame_t;

/**
 * @brief Конфігурація протоколу та разрядності енкодера
 */
typedef struct {
    uint8_t single_turn_bits;   /**< Кількість бітів однооборотної роздільності (ST, наприклад 18) */
    uint8_t multi_turn_bits;    /**< Кількість бітів багатооборотного лічильника (MT, наприклад 12) */
    bool is_gray_code;          /**< Прапорець кодування: true - код Ґрея, false - двійковий */
    bool has_biss_crc;          /**< Прапорець наявності 6-бітної CRC BiSS-C у кадрі */
    bool active_low_status;     /**< true якщо nERROR/nWARN мають інверсну логіку (0 = помилка) */
} encoder_config_t;

/**
 * @brief Ініціалізація конфігураційної структури енкодера
 * @param config Вказівник на конфігурацію
 * @param st_bits Розрядність однооборотної позиції (біт)
 * @param mt_bits Розрядність багатооборотного лічильника (біт)
 * @param is_gray true якщо використовується код Ґрея
 * @param has_crc true якщо кадр містить BiSS-C CRC-6
 */
void encoder_ssi_init_config(encoder_config_t *config,
                             uint8_t st_bits,
                             uint8_t mt_bits,
                             bool is_gray,
                             bool has_crc);

/**
 * @brief Розбір сирого кадру даних, отриманого через SPI/SSI/BiSS-C
 * @param config Вказівник на конфігурацію енкодера
 * @param raw_frame 64-бітне значення вибірки з шини SPI
 * @param out_frame Вихідна структура розпарсених даних
 * @return true якщо кадр розпарсений та пройшов перевірку CRC, false якщо виявлено помилку
 */
bool encoder_ssi_parse_frame(const encoder_config_t *config,
                             uint64_t raw_frame,
                             encoder_frame_t *out_frame);

/**
 * @brief Перетворення однооборотної позиції у фізичний кут у градусах
 * @param config Конфігурація енкодера
 * @param frame Розпарсений кадр енкодера
 * @return Кут у градусах [0.0, 360.0)
 */
double encoder_frame_to_angle_degrees(const encoder_config_t *config,
                                      const encoder_frame_t *frame);

#ifdef __cplusplus
}
#endif

#endif /* ENCODER_SSI_H */
