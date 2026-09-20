#include "can_damper_adapter.h"
#include <math.h>
#include <string.h>

/**
 * @brief Мапування апаратних кодів збоїв CAN-шини у доменні результати.
 *
 * Забезпечує антикорупційний шар (ACL): специфіка шини не просочується в домен.
 */
static damper_status_t map_bus_status_to_domain(can_bus_status_t bus_status) {
    switch (bus_status) {
        case CAN_BUS_STATUS_OK:
            return DAMPER_STATUS_OK;
        case CAN_BUS_STATUS_TIMEOUT:
            return DAMPER_STATUS_TIMEOUT;
        case CAN_BUS_STATUS_TX_BUFFER_FULL:
        case CAN_BUS_STATUS_BUS_OFF:
        case CAN_BUS_STATUS_HARDWARE_ERROR:
        default:
            return DAMPER_STATUS_BUS_ERROR;
    }
}

/**
 * @brief Реалізація методу set_position таблиці vtable вихідного порту.
 */
static damper_status_t can_damper_set_position(
    damper_actuator_port_t *self, const damper_position_cmd_t *cmd)
{
    if (self == NULL || cmd == NULL) {
        return DAMPER_STATUS_INVALID_ARG;
    }

    can_damper_adapter_t *adapter = (can_damper_adapter_t *)self;
    if (!adapter->is_initialized || adapter->bus_driver == NULL || adapter->bus_driver->transmit == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }

    /* Доменна валідація числових параметрів */
    if (isnan(cmd->target_angle_deg) || isinf(cmd->target_angle_deg) ||
        isnan(cmd->max_speed_deg_per_sec) || isinf(cmd->max_speed_deg_per_sec) ||
        cmd->max_speed_deg_per_sec < 0.0f) {
        return DAMPER_STATUS_INVALID_ARG;
    }

    /* Формування непакованої структури сигналів */
    can_damper_signals_t signals = {
        .target_angle_deg = cmd->target_angle_deg,
        .max_speed_deg_per_sec = cmd->max_speed_deg_per_sec,
        .command_mode = (uint8_t)DAMPER_MODE_POSITION,
        .torque_enable = cmd->hold_torque,
        .emergency_stop = false,
        .hold_torque_pct = cmd->hold_torque_pct,
        .rolling_counter = adapter->rolling_counter
    };

    /* Пакування кадру CAN за специфікацією DBC */
    can_raw_frame_t frame;
    can_pack_damper_frame(&signals, &frame);
    frame.can_id = adapter->can_id;

    /* Циклічний інкремент 4-бітного лічильника для наступної команди */
    adapter->rolling_counter = can_increment_counter(adapter->rolling_counter);

    /* Передача кадру через абстрактний драйвер та мапування статусу */
    can_bus_status_t bus_res = adapter->bus_driver->transmit(adapter->bus_driver, &frame);
    return map_bus_status_to_domain(bus_res);
}

/**
 * @brief Реалізація аварійної зупинки актуатора.
 */
static damper_status_t can_damper_emergency_stop(damper_actuator_port_t *self) {
    if (self == NULL) {
        return DAMPER_STATUS_INVALID_ARG;
    }

    can_damper_adapter_t *adapter = (can_damper_adapter_t *)self;
    if (!adapter->is_initialized || adapter->bus_driver == NULL || adapter->bus_driver->transmit == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }

    can_damper_signals_t signals = {
        .target_angle_deg = 0.0f,
        .max_speed_deg_per_sec = 0.0f,
        .command_mode = (uint8_t)DAMPER_MODE_EMERGENCY_SHUTDOWN,
        .torque_enable = false,
        .emergency_stop = true,
        .hold_torque_pct = 0U,
        .rolling_counter = adapter->rolling_counter
    };

    can_raw_frame_t frame;
    can_pack_damper_frame(&signals, &frame);
    frame.can_id = adapter->can_id;

    adapter->rolling_counter = can_increment_counter(adapter->rolling_counter);

    can_bus_status_t bus_res = adapter->bus_driver->transmit(adapter->bus_driver, &frame);
    return map_bus_status_to_domain(bus_res);
}

/**
 * @brief Реалізація команди калібрування нульової точки сервоприводу.
 */
static damper_status_t can_damper_calibrate(damper_actuator_port_t *self) {
    if (self == NULL) {
        return DAMPER_STATUS_INVALID_ARG;
    }

    can_damper_adapter_t *adapter = (can_damper_adapter_t *)self;
    if (!adapter->is_initialized || adapter->bus_driver == NULL || adapter->bus_driver->transmit == NULL) {
        return DAMPER_STATUS_NOT_INITIALIZED;
    }

    can_damper_signals_t signals = {
        .target_angle_deg = 0.0f,
        .max_speed_deg_per_sec = 10.0f, /* Безпечна низька швидкість пошуку упорів */
        .command_mode = (uint8_t)DAMPER_MODE_CALIBRATE,
        .torque_enable = true,
        .emergency_stop = false,
        .hold_torque_pct = 50U,
        .rolling_counter = adapter->rolling_counter
    };

    can_raw_frame_t frame;
    can_pack_damper_frame(&signals, &frame);
    frame.can_id = adapter->can_id;

    adapter->rolling_counter = can_increment_counter(adapter->rolling_counter);

    can_bus_status_t bus_res = adapter->bus_driver->transmit(adapter->bus_driver, &frame);
    return map_bus_status_to_domain(bus_res);
}

/**
 * @brief Таблиця операцій вихідного адаптера CAN.
 */
static const damper_actuator_ops_t CAN_DAMPER_OPS = {
    .set_position = can_damper_set_position,
    .emergency_stop = can_damper_emergency_stop,
    .calibrate = can_damper_calibrate
};

/**
 * @brief Фабрична ініціалізація вихідного адаптера.
 */
damper_actuator_port_t *can_damper_adapter_init(
    can_damper_adapter_t *adapter,
    can_bus_driver_t     *bus_driver,
    uint32_t              can_id
) {
    if (adapter == NULL || bus_driver == NULL) {
        return NULL;
    }

    adapter->base_port.ops = &CAN_DAMPER_OPS;
    adapter->bus_driver = bus_driver;
    adapter->can_id = can_id;
    adapter->rolling_counter = 0U;
    adapter->is_initialized = true;

    return &adapter->base_port;
}
