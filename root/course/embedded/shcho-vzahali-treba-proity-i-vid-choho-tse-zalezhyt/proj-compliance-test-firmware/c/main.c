#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

typedef enum {
    RF_MODE_IDLE = 0,
    RF_MODE_TX_CW,        /* Немодульована синусоїда (Continuous Wave) */
    RF_MODE_TX_MODULATED, /* Псевдовипадковий модульований потік PRBS9 */
    RF_MODE_RX_STANDBY    /* Безперервний прийом */
} rf_test_mode_t;

typedef struct {
    rf_test_mode_t mode;
    uint8_t channel;      /* Номер каналу: 0..39 для BLE (2402..2480 МГц) */
    int8_t power_dbm;     /* Потужність: -20..+8 дБм */
    uint32_t payload_cnt; /* Лічильник відправлених пакетів */
} rf_test_state_t;

static rf_test_state_t g_rf_state = {
    .mode = RF_MODE_IDLE,
    .channel = 0,
    .power_dbm = 0,
    .payload_cnt = 0
};

/* Апаратно-залежні заглушки для взаємодії з регістрами трансивера */
static void hw_radio_stop(void) {
    /* Скидання автоматів станів радіомодуля та вимкнення синтезатора PLL */
}

static void hw_radio_start_cw(uint8_t channel, int8_t power_dbm) {
    /* Налаштування частоти: F_rf = 2402 + channel * 2 МГц */
    /* Встановлення потужності передавача та запуск генерації тону */
}

static void hw_radio_start_modulated(uint8_t channel, int8_t power_dbm) {
    /* Запуск апаратного генератора PRBS9 з безперервною GFSK модуляцією */
}

static void hw_radio_start_rx(uint8_t channel) {
    /* Увімкнення підсилювача LNA та демодулятора в режимі прослуховування */
}

void rf_test_init(void) {
    g_rf_state.mode = RF_MODE_IDLE;
    hw_radio_stop();
}

bool rf_test_execute_command(const char *cmd_line, char *resp_buf, size_t resp_max) {
    char cmd[16] = {0};
    int chan = 0;
    int power = 0;

    if (sscanf(cmd_line, "%15s %d %d", cmd, &chan, &power) < 1) {
        snprintf(resp_buf, resp_max, "ERR: EMPTY_CMD\r\n");
        return false;
    }

    if (strcmp(cmd, "STOP") == 0) {
        hw_radio_stop();
        g_rf_state.mode = RF_MODE_IDLE;
        snprintf(resp_buf, resp_max, "OK: RADIO_STOPPED\r\n");
        return true;
    }

    if (chan < 0 || chan > 39) {
        snprintf(resp_buf, resp_max, "ERR: INVALID_CHANNEL (0..39)\r\n");
        return false;
    }

    if (power < -20 || power > 8) {
        snprintf(resp_buf, resp_max, "ERR: INVALID_POWER (-20..+8 dBm)\r\n");
        return false;
    }

    if (strcmp(cmd, "TX_CW") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.power_dbm = (int8_t)power;
        g_rf_state.mode = RF_MODE_TX_CW;
        hw_radio_start_cw(g_rf_state.channel, g_rf_state.power_dbm);
        snprintf(resp_buf, resp_max, "OK: TX_CW CH=%d PWR=%d dBm\r\n", chan, power);
        return true;
    }

    if (strcmp(cmd, "TX_MOD") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.power_dbm = (int8_t)power;
        g_rf_state.mode = RF_MODE_TX_MODULATED;
        hw_radio_start_modulated(g_rf_state.channel, g_rf_state.power_dbm);
        snprintf(resp_buf, resp_max, "OK: TX_MOD PRBS9 CH=%d PWR=%d dBm\r\n", chan, power);
        return true;
    }

    if (strcmp(cmd, "RX") == 0) {
        hw_radio_stop();
        g_rf_state.channel = (uint8_t)chan;
        g_rf_state.mode = RF_MODE_RX_STANDBY;
        hw_radio_start_rx(g_rf_state.channel);
        snprintf(resp_buf, resp_max, "OK: RX_STANDBY CH=%d\r\n", chan);
        return true;
    }

    snprintf(resp_buf, resp_max, "ERR: UNKNOWN_CMD: %s\r\n", cmd);
    return false;
}
