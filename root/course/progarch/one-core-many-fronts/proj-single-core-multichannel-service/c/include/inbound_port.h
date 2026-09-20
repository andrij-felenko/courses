#ifndef INBOUND_PORT_H
#define INBOUND_PORT_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

/**
 * @file inbound_port.h
 * @brief Протокольно-нейтральний контракт вхідного порту (Driving/Inbound Port).
 *
 * У гексагональній архітектурі (порти й адаптери) вхідний порт визначає межу
 * прикладного ядра (Use Case Boundary). Він повністю ізольований від транспортних
 * протоколів, форматів серіалізації, мережевих сокетів та специфіки вводу-виводу ОС.
 */

#ifdef __cplusplus
extern "C" {
#endif

#define CLIMATE_ROOM_ID_LEN    32
#define CLIMATE_AUTH_TOKEN_LEN 64
#define CLIMATE_MSG_LEN        128

/**
 * @brief Доменні статуси виконання команд прикладним ядром.
 *
 * Нейтральні статуси ядра, які кожен драйвуючий адаптер транслює
 * у власну протокольну форму (коди завершення CLI, HTTP-статуси, ACK/NACK/DLQ черги).
 */
typedef enum {
    CORE_STATUS_OK = 0,               /**< Команду успішно виконано прикладним ядром */
    CORE_STATUS_INVALID_ARG = 1,      /**< Неприпустимі параметри (порожній ID кімнати тощо) */
    CORE_STATUS_UNAUTHORIZED = 2,     /**< Недійсний або відсутній токен авторизації */
    CORE_STATUS_OUT_OF_RANGE = 3,     /**< Цільова температура виходить за межі безпечного діапазону */
    CORE_STATUS_INTERNAL_ERROR = 4    /**< Внутрішня системна помилка ядра (вичерпано ресурси) */
} core_status_t;

/**
 * @brief Отримання рядкового представлення статусу ядра для діагностики та логування.
 *
 * @param status Доменний статус ядра.
 * @return const char* Статичний текстовий опис статусу.
 */
const char *core_status_to_string(core_status_t status);

/**
 * @brief Нейтральна доменна команда керування мікрокліматом кімнати.
 *
 * Представляє очищені дані, що передаються в ядро з будь-якого зовнішнього джерела:
 * командного рядка, HTTP-запиту чи пакета з черги повідомлень брокера.
 */
typedef struct {
    char room_id[CLIMATE_ROOM_ID_LEN];       /**< Ідентифікатор кімнати (наприклад, "living-room") */
    double target_temp_c;                    /**< Бажана температура у градусах Цельсія */
    char auth_token[CLIMATE_AUTH_TOKEN_LEN]; /**< Секретний токен автентифікації клієнта */
} climate_cmd_t;

/**
 * @brief Доменний результат виконання кліматичної команди.
 *
 * Повертає статус операції, попереднє та нове значення температури кімнати,
 * а також діагностичне пояснення бізнес-рівня.
 */
typedef struct {
    core_status_t status;          /**< Результат обробки ядром */
    double previous_temp_c;        /**< Попередня встановлена температура кімнати */
    double current_temp_c;         /**< Фактично встановлена поточна температура */
    char message[CLIMATE_MSG_LEN]; /**< Зрозуміле текстове пояснення результату */
} climate_result_t;

typedef struct inbound_port inbound_port_t;

/**
 * @brief Абстрактний контракт вхідного порту (Inbound Port Contract).
 *
 * Побудований на базі структури з покажчиком на контекст і покажчиком на функцію.
 * Адаптери взаємодіють виключно з цим інтерфейсом, не знаючи про конкретну реалізацію ядра.
 */
struct inbound_port {
    void *ctx; /**< Непрозорий покажчик на стан прикладного ядра */

    /**
     * @brief Функція виконання команди керування мікрокліматом.
     *
     * @param self Покажчик на контракт вхідного порту.
     * @param cmd Покажчик на вхідну команду.
     * @param out_result Покажчик на структуру для запису доменного результату.
     * @return core_status_t Статус виконання операції.
     */
    core_status_t (*execute)(inbound_port_t *self, const climate_cmd_t *cmd, climate_result_t *out_result);
};

/**
 * @brief Допоміжний виклик виконання команди через вхідний порт із захистом від NULL.
 *
 * @param port Покажчик на вхідний порт.
 * @param cmd Покажчик на вхідну команду.
 * @param out_result Покажчик на структуру результату.
 * @return core_status_t Статус виконання.
 */
static inline core_status_t inbound_port_execute(inbound_port_t *port, const climate_cmd_t *cmd, climate_result_t *out_result) {
    if (!port || !port->execute) {
        if (out_result) {
            out_result->status = CORE_STATUS_INTERNAL_ERROR;
        }
        return CORE_STATUS_INTERNAL_ERROR;
    }
    return port->execute(port, cmd, out_result);
}

#ifdef __cplusplus
}
#endif

#endif /* INBOUND_PORT_H */
