#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <assert.h>

#include "damper_actuator_port.h"
#include "can_damper_adapter.h"
#include "can_frame_packer.h"

/**
 * @brief Максимальна місткість буфера захоплених кадрів у програмному емуляторі.
 */
#define MOCK_BUS_MAX_FRAMES 32

/**
 * @brief Програмний емулятор шини CAN для тестування в ізоляції від реального заліза.
 */
typedef struct {
    can_bus_driver_t base_driver;
    can_raw_frame_t  captured_frames[MOCK_BUS_MAX_FRAMES];
    size_t           captured_count;
    can_bus_status_t simulated_status;
} mock_can_bus_t;

/**
 * @brief Функція передачі емулятора шини CAN: захоплює кадр або повертає симульовану помилку.
 */
static can_bus_status_t mock_can_transmit(can_bus_driver_t *self, const can_raw_frame_t *frame) {
    if (self == NULL || frame == NULL) {
        return CAN_BUS_STATUS_HARDWARE_ERROR;
    }

    mock_can_bus_t *mock = (mock_can_bus_t *)self->driver_context;
    if (mock == NULL) {
        return CAN_BUS_STATUS_HARDWARE_ERROR;
    }

    if (mock->simulated_status != CAN_BUS_STATUS_OK) {
        return mock->simulated_status;
    }

    if (mock->captured_count >= MOCK_BUS_MAX_FRAMES) {
        return CAN_BUS_STATUS_TX_BUFFER_FULL;
    }

    mock->captured_frames[mock->captured_count++] = *frame;
    return CAN_BUS_STATUS_OK;
}

/**
 * @brief Ініціалізація програмного емулятора шини CAN.
 */
static void mock_can_init(mock_can_bus_t *mock) {
    memset(mock, 0, sizeof(*mock));
    mock->base_driver.transmit = mock_can_transmit;
    mock->base_driver.driver_context = mock;
    mock->simulated_status = CAN_BUS_STATUS_OK;
    mock->captured_count = 0;
}

/**
 * @brief Допоміжний вивід 8-байтного кадру CAN у шістнадцятковому форматі.
 */
static void print_can_frame(const char *label, const can_raw_frame_t *frame) {
    printf("%s ID=0x%03X DLC=%u [", label, frame->can_id, frame->dlc);
    for (uint8_t i = 0; i < frame->dlc; ++i) {
        printf(" %02X", frame->data[i]);
    }
    printf(" ]\n");
}

/**
 * @brief Тест 1: Перевірка трансляції доменної команди та точного побітового розміщення сигналів.
 */
static void test_normal_command_and_dbc_bit_layout(void) {
    printf("\n=== ТЕСТ 1: Трансляція доменної команди у кадр CAN та верифікація бітового розміщення ===\n");

    mock_can_bus_t mock_bus;
    mock_can_init(&mock_bus);

    can_damper_adapter_t adapter;
    damper_actuator_port_t *port = can_damper_adapter_init(&adapter, &mock_bus.base_driver, CAN_ID_DAMPER_CMD);
    assert(port != NULL);

    /*
     * Формуємо доменну команду:
     * - Цільовий кут: 45.0 градусів
     *   За DBC: Offset = -10.0, Scale = 0.05
     *   Raw = (45.0 - (-10.0)) / 0.05 = 55.0 / 0.05 = 1100 = 0x044C (12 бітів)
     *   Little-Endian: Байт 0 = 0x4C; Байт 1 (молодший нібл) = 0x04
     * - Режим команди: DAMPER_MODE_POSITION (0) -> Байт 1 (старший нібл) = 0x00
     *   Разом Байт 1 = 0x04
     * - Максимальна швидкість: 30.0 град/с
     *   За DBC: Offset = 0.0, Scale = 0.1
     *   Raw = 30.0 / 0.1 = 300 = 0x012C (16 бітів)
     *   Big-Endian (Motorola): Байт 2 (MSB) = 0x01; Байт 3 (LSB) = 0x2C
     * - Прапорці: TorqueEnable = true (біт 0 = 1), EmergencyStop = false -> Байт 4 = 0x01
     * - Момент утримання: 80% -> Байт 5 = 80 = 0x50
     * - Rolling counter: 0, Heartbeat: 0x50 -> Байт 6 = 0x50
     */
    damper_position_cmd_t cmd = {
        .target_angle_deg = 45.0f,
        .max_speed_deg_per_sec = 30.0f,
        .hold_torque_pct = 80U,
        .hold_torque = true
    };

    damper_status_t status = damper_port_set_position(port, &cmd);
    assert(status == DAMPER_STATUS_OK);
    assert(mock_bus.captured_count == 1);

    const can_raw_frame_t *frame = &mock_bus.captured_frames[0];
    print_can_frame("  Сформований кадр CAN:", frame);

    /* Верифікація CAN ID та DLC */
    assert(frame->can_id == CAN_ID_DAMPER_CMD);
    assert(frame->dlc == 8);

    /* Верифікація Little-Endian кодування кута (0x044C) */
    assert(frame->data[0] == 0x4CU);
    assert((frame->data[1] & 0x0FU) == 0x04U);
    assert(((frame->data[1] >> 4U) & 0x0FU) == 0x00U); /* Режим POSITION */

    /* Верифікація Big-Endian (Motorola) кодування швидкості (0x012C) */
    assert(frame->data[2] == 0x01U); /* MSB за меншою адресою */
    assert(frame->data[3] == 0x2CU); /* LSB за більшою адресою */

    /* Верифікація прапорців та моменту */
    assert(frame->data[4] == 0x01U); /* TorqueEnable = 1 */
    assert(frame->data[5] == 80U);    /* 80% моменту */

    /* Верифікація rolling counter та маркера */
    assert((frame->data[6] & DAMPER_COUNTER_MASK) == 0U);
    assert((frame->data[6] & 0xF0U) == 0x50U);

    /* Верифікація CRC-8 над байтами 0..6 */
    uint8_t expected_crc = can_calculate_crc8(frame->data, 7U);
    assert(frame->data[7] == expected_crc);

    /* Перевірка симетричної розпаковки для контролю зворотного перетворення */
    can_damper_signals_t unpacked;
    can_unpack_damper_frame(frame, &unpacked);
    assert(fabsf(unpacked.target_angle_deg - 45.0f) < 0.025f);
    assert(fabsf(unpacked.max_speed_deg_per_sec - 30.0f) < 0.05f);
    assert(unpacked.torque_enable == true);
    assert(unpacked.emergency_stop == false);
    assert(unpacked.hold_torque_pct == 80U);
    assert(unpacked.rolling_counter == 0U);

    printf("  [OK] Little-Endian та Big-Endian розміщення перевірено успішно.\n");
    printf("  [OK] CRC-8 (0x%02X) та розпаковка сигналів повністю валідні.\n", frame->data[7]);
}

/**
 * @brief Тест 2: Безпечне квантування та обмеження діапазону (Clamping).
 */
static void test_quantization_clamping(void) {
    printf("\n=== ТЕСТ 2: Безпечне квантування та обмеження діапазону (Clamping) ===\n");

    mock_can_bus_t mock_bus;
    mock_can_init(&mock_bus);

    can_damper_adapter_t adapter;
    damper_actuator_port_t *port = can_damper_adapter_init(&adapter, &mock_bus.base_driver, CAN_ID_DAMPER_CMD);

    /* Випадок А: Кут нижче фізичного мінімуму (-25.0 при мінімумі -10.0) */
    damper_position_cmd_t cmd_underflow = {
        .target_angle_deg = -25.0f,
        .max_speed_deg_per_sec = 50.0f,
        .hold_torque_pct = 50U,
        .hold_torque = true
    };
    damper_status_t status = damper_port_set_position(port, &cmd_underflow);
    assert(status == DAMPER_STATUS_OK);

    const can_raw_frame_t *frame_min = &mock_bus.captured_frames[0];
    print_can_frame("  Кадр з кутом < min (-25.0 град):", frame_min);
    /* Кут насичено до -10.0: Raw = (-10.0 - (-10.0)) / 0.05 = 0 */
    assert(frame_min->data[0] == 0x00U);
    assert((frame_min->data[1] & 0x0FU) == 0x00U);

    /* Випадок Б: Кут вище фізичного максимуму (+150.0 при максимумі +110.0) */
    damper_position_cmd_t cmd_overflow = {
        .target_angle_deg = 150.0f,
        .max_speed_deg_per_sec = 250.0f, /* Перевищує максимум 180.0 град/с */
        .hold_torque_pct = 120U,         /* Перевищує 100% */
        .hold_torque = true
    };
    status = damper_port_set_position(port, &cmd_overflow);
    assert(status == DAMPER_STATUS_OK);

    const can_raw_frame_t *frame_max = &mock_bus.captured_frames[1];
    print_can_frame("  Кадр з кутом > max (+150.0 град):", frame_max);

    /* Кут насичено до 110.0: Raw = (110.0 - (-10.0)) / 0.05 = 2400 = 0x0960 */
    assert(frame_max->data[0] == 0x60U);
    assert((frame_max->data[1] & 0x0FU) == 0x09U);

    /* Швидкість насичено до 180.0: Raw = 180.0 / 0.1 = 1800 = 0x0708 (Big-Endian) */
    assert(frame_max->data[2] == 0x07U);
    assert(frame_max->data[3] == 0x08U);

    /* Відсоток утримання насичено до 100% */
    assert(frame_max->data[5] == 100U);

    printf("  [OK] Clamping гарантує відсутність переповнення бітових полів.\n");
}

/**
 * @brief Тест 3: Послідовність 4-бітного Rolling Counter та розрахунок CRC-8.
 */
static void test_rolling_counter_and_crc_sequence(void) {
    printf("\n=== ТЕСТ 3: Послідовність 4-бітного Rolling Counter та розрахунок CRC-8 ===\n");

    mock_can_bus_t mock_bus;
    mock_can_init(&mock_bus);

    can_damper_adapter_t adapter;
    damper_actuator_port_t *port = can_damper_adapter_init(&adapter, &mock_bus.base_driver, CAN_ID_DAMPER_CMD);

    damper_position_cmd_t cmd = {
        .target_angle_deg = 20.0f,
        .max_speed_deg_per_sec = 40.0f,
        .hold_torque_pct = 60U,
        .hold_torque = true
    };

    /* Відправляємо серію з 5 команд і перевіряємо суворий монотонний інкремент */
    for (uint8_t i = 0; i < 5; ++i) {
        damper_status_t status = damper_port_set_position(port, &cmd);
        assert(status == DAMPER_STATUS_OK);

        const can_raw_frame_t *f = &mock_bus.captured_frames[i];
        uint8_t counter = f->data[6] & DAMPER_COUNTER_MASK;
        assert(counter == i);

        /* Контрольна сума щоразу валідна */
        uint8_t crc = can_calculate_crc8(f->data, 7U);
        assert(f->data[7] == crc);

        printf("  Команда #%u: RollingCounter = %u, CRC-8 = 0x%02X\n", i, counter, crc);
    }

    /* Перевірка циклічного переповнення за модулем 16 (15 -> 0) */
    adapter.rolling_counter = 15U;
    damper_port_set_position(port, &cmd);
    const can_raw_frame_t *f_15 = &mock_bus.captured_frames[5];
    assert((f_15->data[6] & DAMPER_COUNTER_MASK) == 15U);

    damper_port_set_position(port, &cmd);
    const can_raw_frame_t *f_wrap = &mock_bus.captured_frames[6];
    assert((f_wrap->data[6] & DAMPER_COUNTER_MASK) == 0U);

    printf("  [OK] Циклічний лічильник коректно скидається після 15 до 0.\n");
}

/**
 * @brief Тест 4: Емуляція апаратних збоїв шини CAN та перевірка ізоляції домену.
 */
static void test_bus_fault_tolerance_and_domain_isolation(void) {
    printf("\n=== ТЕСТ 4: Емуляція збоїв шини CAN та мапування у доменні статуси ===\n");

    mock_can_bus_t mock_bus;
    mock_can_init(&mock_bus);

    can_damper_adapter_t adapter;
    damper_actuator_port_t *port = can_damper_adapter_init(&adapter, &mock_bus.base_driver, CAN_ID_DAMPER_CMD);

    damper_position_cmd_t cmd = {
        .target_angle_deg = 30.0f,
        .max_speed_deg_per_sec = 20.0f,
        .hold_torque_pct = 70U,
        .hold_torque = true
    };

    /* 1. Симуляція помилки Bus-Off (апаратне відключення шини CAN) */
    mock_bus.simulated_status = CAN_BUS_STATUS_BUS_OFF;
    damper_status_t status = damper_port_set_position(port, &cmd);
    assert(status == DAMPER_STATUS_BUS_ERROR);
    printf("  CAN_BUS_STATUS_BUS_OFF -> %s [OK]\n", damper_status_to_string(status));

    /* 2. Симуляція таймауту відправки кадру */
    mock_bus.simulated_status = CAN_BUS_STATUS_TIMEOUT;
    status = damper_port_set_position(port, &cmd);
    assert(status == DAMPER_STATUS_TIMEOUT);
    printf("  CAN_BUS_STATUS_TIMEOUT -> %s [OK]\n", damper_status_to_string(status));

    /* 3. Валідація некоректних вхідних даних (NaN) у доменному шарі */
    mock_bus.simulated_status = CAN_BUS_STATUS_OK;
    size_t count_before = mock_bus.captured_count;

    damper_position_cmd_t invalid_cmd = {
        .target_angle_deg = NAN,
        .max_speed_deg_per_sec = 20.0f,
        .hold_torque_pct = 70U,
        .hold_torque = true
    };
    status = damper_port_set_position(port, &invalid_cmd);
    assert(status == DAMPER_STATUS_INVALID_ARG);
    /* Жоден некоректний кадр не потрапив у шину */
    assert(mock_bus.captured_count == count_before);
    printf("  NaN target_angle -> %s (кадр не відправлено) [OK]\n", damper_status_to_string(status));
}

/**
 * @brief Тест 5: Аварійна зупинка та перехід у режим калібрування.
 */
static void test_emergency_stop_and_calibration(void) {
    printf("\n=== ТЕСТ 5: Аварійна зупинка та режим калібрування заслінки ===\n");

    mock_can_bus_t mock_bus;
    mock_can_init(&mock_bus);

    can_damper_adapter_t adapter;
    damper_actuator_port_t *port = can_damper_adapter_init(&adapter, &mock_bus.base_driver, CAN_ID_DAMPER_CMD);

    /* Виклик аварійної зупинки */
    damper_status_t status = damper_port_emergency_stop(port);
    assert(status == DAMPER_STATUS_OK);
    assert(mock_bus.captured_count == 1);

    const can_raw_frame_t *f_emg = &mock_bus.captured_frames[0];
    print_can_frame("  Кадр аварійної зупинки:", f_emg);

    /* Режим EMERGENCY_SHUTDOWN (2) у старшому ніблі байта 1 */
    assert(((f_emg->data[1] >> 4U) & 0x0FU) == (uint8_t)DAMPER_MODE_EMERGENCY_SHUTDOWN);
    /* EmergencyStop біт 1 у байті 4 встановлено, TorqueEnable біт 0 знято */
    assert((f_emg->data[4] & (1U << 1)) != 0U);
    assert((f_emg->data[4] & (1U << 0)) == 0U);

    /* Виклик калібрування */
    status = damper_port_calibrate(port);
    assert(status == DAMPER_STATUS_OK);
    assert(mock_bus.captured_count == 2);

    const can_raw_frame_t *f_cal = &mock_bus.captured_frames[1];
    print_can_frame("  Кадр калібрування:", f_cal);

    /* Режим CALIBRATE (1) у старшому ніблі байта 1 */
    assert(((f_cal->data[1] >> 4U) & 0x0FU) == (uint8_t)DAMPER_MODE_CALIBRATE);
    /* Безпечна швидкість калібрування: 10.0 град/с -> Raw = 100 = 0x0064 */
    assert(f_cal->data[2] == 0x00U);
    assert(f_cal->data[3] == 0x64U);

    printf("  [OK] Аварійне переривання та калібрування транслюються детерміновано.\n");
}

int main(void) {
    printf("====================================================================\n");
    printf("  Тестування вихідного порту та адаптера трансляції протоколу CAN   \n");
    printf("====================================================================\n");

    test_normal_command_and_dbc_bit_layout();
    test_quantization_clamping();
    test_rolling_counter_and_crc_sequence();
    test_bus_fault_tolerance_and_domain_isolation();
    test_emergency_stop_and_calibration();

    printf("\n====================================================================\n");
    printf("  УСІ ТЕСТИ ПРОЙДЕНО УСПІШНО! Архітектурна ізоляція повністю доведена.\n");
    printf("====================================================================\n");

    return 0;
}
