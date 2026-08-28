#include <stdint.h>
#include <stdbool.h>

/* Тип покажчика на низькорівневу фізичну операцію шини */
typedef driver_status_t (*bus_transfer_fn_t)(void *context);

/* Уніфікований стійкий виконавець транзакцій */
driver_status_t resilient_transaction_execute(
    circuit_breaker_t *cb,
    retry_policy_t    *retry_policy,
    bus_transfer_fn_t  transfer_fn,
    void              *context
) {
    /* 1. Фаза перевірки здоров'я: Fast-Fail якщо чип в ізоляції */
    if (!cb_allow_transaction(cb)) {
        return DRIVER_ERR_BUS_TIMEOUT; /* Пристрій офлайн */
    }

    driver_status_t status = DRIVER_OK;
    uint8_t attempt = 0;

    while (attempt < retry_policy->max_attempts) {
        attempt++;

        /* 2. Фізичне виконання транзакції з апаратним таймаутом всередині */
        status = transfer_fn(context);

        /* 3. Успіх: фіксація здоров'я та негайне повернення */
        if (status == DRIVER_OK) {
            cb_report_success(cb);
            return DRIVER_OK;
        }

        /* 4. Аналіз та класифікація збою */
        error_action_t action = classify_driver_error(status);

        if (action == ACTION_CIRCUIT_BREAKER_HIT) {
            /* Фатальна помилка: негайний розрив без ретраїв */
            cb_report_failure(cb);
            return status;
        }

        if (action == ACTION_BUS_RECOVER) {
            /* Залипання шини: апаратне відновлення 9 імпульсами */
            i2c_hardware_bus_recover();
        }

        /* 5. Обчислення експоненційного відкату з джитером */
        if (attempt < retry_policy->max_attempts) {
            uint32_t delay_us = retry_calculate_delay_us(retry_policy, attempt);
            platform_delay_us(delay_us);
        }
    }

    /* Якщо всі спроби вичерпано — інформуємо Circuit Breaker про відмову */
    cb_report_failure(cb);
    return status;
}
