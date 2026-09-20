#ifndef CLIMATE_CORE_H
#define CLIMATE_CORE_H

#include "inbound_port.h"

/**
 * @file climate_core.h
 * @brief Прикладне ядро системи керування мікрокліматом.
 *
 * Зберігає внутрішній стан (таблицю кімнат та їхніх температур), бізнес-правила
 * допустимого температурного діапазону та валідацію доступу. Експортує
 * нейтральний вхідний порт для підключення адаптерів.
 */

#ifdef __cplusplus
extern "C" {
#endif

#define CLIMATE_CORE_MAX_ROOMS 16
#define CLIMATE_TEMP_MIN_C     15.0
#define CLIMATE_TEMP_MAX_C     30.0
#define CLIMATE_DEFAULT_TEMP_C 20.0

/**
 * @brief Внутрішній запис кімнати в стані ядра.
 */
typedef struct {
    char room_id[CLIMATE_ROOM_ID_LEN]; /**< Унікальний ідентифікатор кімнати */
    double current_temp_c;             /**< Поточна задана температура */
    bool is_occupied;                  /**< Ознака зайнятості слота */
} climate_room_entry_t;

/**
 * @brief Структура внутрішнього стану прикладного ядра.
 */
typedef struct climate_core {
    inbound_port_t port;                               /**< Експортований вхідний порт для адаптерів */
    char expected_auth_token[CLIMATE_AUTH_TOKEN_LEN];  /**< Очікуваний токен для авторизації команд */
    climate_room_entry_t rooms[CLIMATE_CORE_MAX_ROOMS];/**< Таблиця стану мікроклімату приміщень */
    size_t room_count;                                 /**< Кількість активних кімнат */
} climate_core_t;

/**
 * @brief Ініціалізує прикладне ядро та налаштовує контракт вхідного порту.
 *
 * @param core Покажчик на виділену пам'ять ядра.
 * @param valid_auth_token Секретний токен, необхідний для виконання команд.
 */
void climate_core_init(climate_core_t *core, const char *valid_auth_token);

/**
 * @brief Отримує інтерфейс вхідного порту для інжекції в драйвуючі адаптери.
 *
 * @param core Покажчик на екземпляр ядра.
 * @return inbound_port_t* Покажчик на вхідний порт.
 */
inbound_port_t *climate_core_get_port(climate_core_t *core);

/**
 * @brief Реалізація бізнес-логіки виконання команди для вхідного порту.
 *
 * @param self Покажчик на інтерфейс вхідного порту.
 * @param cmd Вхідна команда.
 * @param out_result Структура для запису результату.
 * @return core_status_t Статус виконання операції.
 */
core_status_t climate_core_execute(inbound_port_t *self, const climate_cmd_t *cmd, climate_result_t *out_result);

/**
 * @brief Допоміжна функція інспекції поточної температури в кімнаті (для тестування та моніторингу).
 *
 * @param core Покажчик на ядро.
 * @param room_id Ідентифікатор кімнати.
 * @param out_temp Покажчик для запису поточної температури.
 * @return true Якщо кімнату знайдено.
 * @return false Якщо кімната відсутня у реєстрі ядра.
 */
bool climate_core_get_room_temp(const climate_core_t *core, const char *room_id, double *out_temp);

#ifdef __cplusplus
}
#endif

#endif /* CLIMATE_CORE_H */
