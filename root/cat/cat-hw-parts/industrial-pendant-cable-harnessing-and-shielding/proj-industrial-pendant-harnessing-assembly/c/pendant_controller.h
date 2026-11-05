/**
 * @file pendant_controller.h
 * @brief Оголошення структур стану кнопок, конфігурації антибрязкання та прототипів функцій.
 */

#ifndef PENDANT_CONTROLLER_H
#define PENDANT_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

/** Максимальна кількість дискретних входів кнопок пульта */
#define PENDANT_BUTTON_COUNT 6

/** Преамбула фрейму RS-485 */
#define PENDANT_FRAME_PREAMBLE 0xAA55

/**
 * @brief Перелік кнопок підвісного пульта
 */
typedef enum {
    BTN_UP = 0,
    BTN_DOWN,
    BTN_LEFT,
    BTN_RIGHT,
    BTN_START,
    BTN_STOP
} PendantButtonId;

/**
 * @brief Структура стану окремої кнопки з урахуванням антибрязкання
 */
typedef struct {
    bool raw_state;       /**< Поточний сирий стан пін-входу */
    bool debounced_state; /**< Стабільний стан після фільтрації */
    uint8_t counter;      /**< Лічильник інтегруючого фільтра */
} ButtonChannel;

/**
 * @brief Структура стану лінії аварійної зупинки (Emergency Stop - NC)
 */
typedef struct {
    bool is_closed;       /**< true, якщо ланцюг замкнено (все гаразд); false, якщо обрив або натиснуто */
    uint32_t fault_count; /**< Лічильник аварійних спрацьовувань */
} EmergencyStopState;

/**
 * @brief Загальний стан пульта керування
 */
typedef struct {
    ButtonChannel buttons[PENDANT_BUTTON_COUNT];
    EmergencyStopState e_stop;
    uint16_t packet_counter;
} PendantController;

/**
 * @brief Структура телеметричного фрейму для передачі через RS-485
 */
#pragma pack(push, 1)
typedef struct {
    uint16_t preamble;     /**< Преамбула для синхронізації (0xAA55) */
    uint16_t packet_id;    /**< Лічильник пакетів */
    uint8_t button_mask;   /**< Бітова маска стабільних станів кнопок */
    uint8_t e_stop_status; /**< Статус аварійної лінії (0 - аварія/обрив, 1 - норма) */
    uint16_t crc16;        /**< Контрольна сума CRC-16 (Modbus / CCITT) */
} PendantTelemetryFrame;
#pragma pack(pop)

/**
 * @brief Ініціалізація структури контролера пульта
 * @param ctrl Вказівник на структуру пульта
 */
void pendant_init(PendantController *ctrl);

/**
 * @brief Опитування входів із програмним антибрязканням та перевіркою E-Stop
 * @param ctrl Вказівник на структуру пульта
 * @param raw_inputs Сирова маска з дискретних входів (біти 0-5)
 * @param e_stop_pin_level Рівень на сигнальному піні E-Stop (true - високий/замкнено, false - низький/обрив)
 */
void pendant_poll_inputs(PendantController *ctrl, uint8_t raw_inputs, bool e_stop_pin_level);

/**
 * @brief Обчислення контрольної суми CRC-16 (Modbus поліном 0xA001)
 * @param data Вказівник на буфер даних
 * @param length Довжина буфера у байтах
 * @return Обчислена контрольна сума
 */
uint16_t pendant_calculate_crc16(const uint8_t *data, size_t length);

/**
 * @brief Пакування стану пульта у телеметричний фрейм для RS-485
 * @param ctrl Вказівник на структуру пульта
 * @param frame Вказівник на вихідний фрейм
 */
void pendant_build_frame(PendantController *ctrl, PendantTelemetryFrame *frame);

#endif /* PENDANT_CONTROLLER_H */
