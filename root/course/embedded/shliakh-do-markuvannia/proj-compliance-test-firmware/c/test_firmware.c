/* test_firmware.c — Диспетчер сертифікаційних режимів для вбудованої системи */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    TEST_MODE_IDLE = 0,
    TEST_MODE_CW_TX,
    TEST_MODE_MODULATED_TX,
    TEST_MODE_RX,
    TEST_MODE_DIGITAL_STRESS
} test_mode_t;

typedef struct {
    test_mode_t mode;
    uint8_t channel;      /* Номер каналу (наприклад, 0..39 для BLE) */
    int8_t power_dbm;     /* Цільова потужність у дБм */
    bool is_active;
} rf_test_state_t;

static rf_test_state_t g_state = {TEST_MODE_IDLE, 0, 0, false};

/* Апаратні абстракції керування трансивером */
extern void radio_set_channel(uint8_t ch);
extern void radio_set_power(int8_t dbm);
extern void radio_start_cw(void);
extern void radio_start_modulated_stream(void);
extern void radio_start_rx(void);
extern void radio_stop(void);
extern void digital_peripherals_stress_start(void);
extern void digital_peripherals_stress_stop(void);
extern void uart_send_string(const char *msg);

void test_firmware_stop_all(void) {
    radio_stop();
    digital_peripherals_stress_stop();
    g_state.is_active = false;
    g_state.mode = TEST_MODE_IDLE;
    uart_send_string("STATUS: IDLE\r\n");
}

void test_firmware_process_command(const char *cmd) {
    if (strncmp(cmd, "STOP", 4) == 0) {
        test_firmware_stop_all();
    } else if (strncmp(cmd, "TX_CW", 5) == 0) {
        /* Формат команди: TX_CW <ch> <pwr_dbm> */
        test_firmware_stop_all();
        g_state.channel = 19; /* За замовчуванням середній канал */
        g_state.power_dbm = 4;
        radio_set_channel(g_state.channel);
        radio_set_power(g_state.power_dbm);
        radio_start_cw();
        g_state.mode = TEST_MODE_CW_TX;
        g_state.is_active = true;
        uart_send_string("STATUS: CW_TX_RUNNING\r\n");
    } else if (strncmp(cmd, "TX_MOD", 6) == 0) {
        test_firmware_stop_all();
        g_state.channel = 19;
        g_state.power_dbm = 4;
        radio_set_channel(g_state.channel);
        radio_set_power(g_state.power_dbm);
        radio_start_modulated_stream();
        g_state.mode = TEST_MODE_MODULATED_TX;
        g_state.is_active = true;
        uart_send_string("STATUS: MODULATED_TX_RUNNING\r\n");
    } else if (strncmp(cmd, "RX_CONT", 7) == 0) {
        test_firmware_stop_all();
        g_state.channel = 19;
        radio_set_channel(g_state.channel);
        radio_start_rx();
        g_state.mode = TEST_MODE_RX;
        g_state.is_active = true;
        uart_send_string("STATUS: RX_RUNNING\r\n");
    } else if (strncmp(cmd, "STRESS", 6) == 0) {
        test_firmware_stop_all();
        digital_peripherals_stress_start();
        g_state.mode = TEST_MODE_DIGITAL_STRESS;
        g_state.is_active = true;
        uart_send_string("STATUS: STRESS_RUNNING\r\n");
    } else {
        uart_send_string("ERROR: UNKNOWN_CMD\r\n");
    }
}
