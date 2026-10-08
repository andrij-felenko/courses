#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Типи станів полюсів давача SS41F
typedef enum {
    SS41F_POLE_UNKNOWN = 0,
    SS41F_POLE_SOUTH   = 1, // Низький логічний рівень на виході (South Pole)
    SS41F_POLE_NORTH   = 2  // Високий логічний рівень на виході (North Pole)
} ss41f_pole_t;

// Коди відповідей API драйвера
typedef enum {
    SS41F_OK = 0,
    SS41F_ERR_INVALID_ARG,
    SS41F_ERR_GPIO_INIT,
    SS41F_ERR_ALREADY_INIT
} ss41f_status_t;

// Вказівник на callback-функцію сповіщення про зміну полюса
typedef void (*ss41f_callback_t)(ss41f_pole_t pole, uint32_t timestamp_us, void *user_data);

// Структура конфігурації драйвера SS41F
typedef struct {
    uint16_t gpio_pin;           // Номер піна GPIO
    void    *gpio_port;          // Вказівник на порт GPIO (наприклад, GPIOA)
    uint32_t debounce_window_us; // Вікно фільтрації брязкоту у мікросекундах
    ss41f_callback_t callback;   // Користувацький callback
    void    *user_data;          // Користувацький контекст для callback
} ss41f_config_t;

// Структура контексту (стану) драйвера SS41F
typedef struct {
    ss41f_config_t config;
    volatile ss41f_pole_t current_pole;
    volatile uint32_t last_change_us;
    volatile uint32_t event_count;
    bool is_initialized;
} ss41f_driver_t;

// Прототип функції ініціалізації
ss41f_status_t ss41f_init(ss41f_driver_t *driver, const ss41f_config_t *config) {
    if (driver == NULL || config == NULL) {
        return SS41F_ERR_INVALID_ARG;
    }
    if (driver->is_initialized) {
        return SS41F_ERR_ALREADY_INIT;
    }

    driver->config = *config;
    driver->last_change_us = 0;
    driver->event_count = 0;

    // Зчитування початкового стану піна GPIO (припускаємо підтяжку до VCC)
    bool initial_pin_low = true; // Припускаємо низький рівень (Південний полюс)
    driver->current_pole = initial_pin_low ? SS41F_POLE_SOUTH : SS41F_POLE_NORTH;

    driver->is_initialized = true;
    return SS41F_OK;
}
