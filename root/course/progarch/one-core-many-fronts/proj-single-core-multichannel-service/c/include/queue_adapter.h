#ifndef QUEUE_ADAPTER_H
#define QUEUE_ADAPTER_H

#include "inbound_port.h"
#include <stdint.h>
#include <stdbool.h>

/**
 * @file queue_adapter.h
 * @brief Драйвуючий асинхронний адаптер черги повідомлень (Queue Driving Adapter).
 *
 * Оголошує структуру конверта повідомлення (Message Envelope), протокольні директиви
 * життєвого циклу повідомлення (ACK, NACK, DLQ) та інтерфейс обробника черги через poll().
 */

#ifdef __cplusplus
extern "C" {
#endif

#define QUEUE_MSG_ID_LEN         36
#define QUEUE_CORRELATION_ID_LEN 36

/**
 * @brief Протокольні директиви квитування повідомлень черги.
 */
typedef enum {
    QUEUE_ACTION_ACK = 0,     /**< Успішна обробка: повідомлення підтверджено та вилучається з черги */
    QUEUE_ACTION_NACK = 1,    /**< Тимчасовий збій системи: повернення в чергу на повторну спробу (Retry) */
    QUEUE_ACTION_DLQ = 2,     /**< Фатальна бізнес-помилка або отруйне повідомлення: ізоляція у Dead Letter Queue */
    QUEUE_ACTION_TIMEOUT = 3, /**< Вичерпано таймаут очікування надходження повідомлення */
    QUEUE_ACTION_ERROR = 4    /**< Системна помилка читання дескриптора каналу */
} queue_action_t;

/**
 * @brief Отримання рядкового найменування директиви квитування.
 */
const char *queue_action_to_string(queue_action_t action);

/**
 * @brief Конверт повідомлення черги (Queue Message Envelope).
 *
 * Містить метадані трасування, кількість спроб доставки та корисне навантаження.
 */
typedef struct {
    char message_id[QUEUE_MSG_ID_LEN];             /**< Унікальний ID повідомлення (UUID) */
    char correlation_id[QUEUE_CORRELATION_ID_LEN]; /**< Ідентифікатор наскрізного ланцюжка запитів */
    uint32_t delivery_attempt;                     /**< Номер поточної спроби доставки брокером */
    uint64_t timestamp_ms;                         /**< Часова мітка публікації */
    char auth_token[CLIMATE_AUTH_TOKEN_LEN];       /**< Токен автентифікації відправника */
    char room_id[CLIMATE_ROOM_ID_LEN];             /**< Ідентифікатор кімнати */
    double target_temp_c;                          /**< Цільова температура */
} queue_message_envelope_t;

/**
 * @brief Опитує дескриптор черги через poll() та обробляє отримане повідомлення.
 *
 * Транслює конверт у climate_cmd_t, викликає вхідний порт та мапить статус ядра:
 *  - CORE_STATUS_OK -> ACK
 *  - CORE_STATUS_INTERNAL_ERROR -> NACK
 *  - CORE_STATUS_INVALID_ARG / CORE_STATUS_UNAUTHORIZED / CORE_STATUS_OUT_OF_RANGE -> DLQ
 *
 * @param port Покажчик на контракт вхідного порту.
 * @param queue_fd Файловий дескриптор черги (сокет або пайп).
 * @param timeout_ms Таймаут очікування виклику poll() у мілісекундах.
 * @return queue_action_t Протокольне рішення квитування.
 */
queue_action_t queue_adapter_poll_fd(inbound_port_t *port, int queue_fd, int timeout_ms);

#ifdef __cplusplus
}
#endif

#endif /* QUEUE_ADAPTER_H */
