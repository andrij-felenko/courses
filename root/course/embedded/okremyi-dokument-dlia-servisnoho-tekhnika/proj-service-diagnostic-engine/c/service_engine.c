/* service_engine.c — Сервісний діагностичний модуль на чистому C */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define CLI_BUFFER_SIZE     128
#define SESSION_TIMEOUT_MS  (900 * 1000)
#define MAX_ACT_TIMEOUT_MS  (15 * 1000)

typedef enum {
    SRV_STATE_LOCKED = 0,
    SRV_STATE_CHALLENGE_ISSUED,
    SRV_STATE_UNLOCKED,
    SRV_STATE_EMERGENCY
} srv_state_t;

typedef struct {
    srv_state_t state;
    uint32_t    session_timer_ms;
    uint32_t    act_timer_ms;
    uint8_t     active_channel;
    uint32_t    current_nonce;
    char        rx_buf[CLI_BUFFER_SIZE];
    uint16_t    rx_idx;
} srv_context_t;

static srv_context_t g_srv;

/* Прототипи апаратних функцій платформи */
extern uint32_t hw_get_tick_ms(void);
extern uint32_t hw_trng_get_random(void);
extern void hw_uart_puts(const char *str);
extern void hw_gpio_set_relay(uint8_t channel, bool state);
extern bool hw_i2c_probe_device(uint8_t addr_7bit);
extern uint16_t hw_adc_read_raw(uint8_t channel);

/* Ініціалізація сервісного контексту */
void srv_init(void) {
    memset(&g_srv, 0, sizeof(g_srv));
    g_srv.state = SRV_STATE_LOCKED;
}

/* Примусове аварійне знеструмлення всіх силових виходів */
void srv_emergency_all_off(void) {
    hw_gpio_set_relay(1, false);
    hw_gpio_set_relay(2, false);
    g_srv.active_channel = 0;
    g_srv.act_timer_ms = 0;
}

/* Обробник команди апаратного самотестування */
static void cmd_handle_selftest(void) {
    bool i2c_rtc = hw_i2c_probe_device(0x68);
    bool i2c_eeprom = hw_i2c_probe_device(0x50);
    uint16_t v_core_adc = hw_adc_read_raw(0);

    char resp[96];
    snprintf(resp, sizeof(resp), "+OK: BIST (RTC:%s, EEPROM:%s, ADC0_RAW:0x%04X)\r\n",
             i2c_rtc ? "OK" : "FAULT",
             i2c_eeprom ? "OK" : "FAULT",
             v_core_adc);
    hw_uart_puts(resp);
}

/* Обробник безпечного ввімкнення реле на фіксований час */
static void cmd_handle_actuate(uint8_t channel, uint16_t timeout_sec) {
    if (g_srv.state != SRV_STATE_UNLOCKED) {
        hw_uart_puts("-ERR: 0x4001 ACCESS_DENIED_LOCKED\r\n");
        return;
    }
    if (channel < 1 || channel > 2) {
        hw_uart_puts("-ERR: 0x4002 INVALID_CHANNEL\r\n");
        return;
    }
    if (timeout_sec == 0 || timeout_sec > 15) {
        hw_uart_puts("-ERR: 0x4003 TIMEOUT_OUT_OF_RANGE (1..15s)\r\n");
        return;
    }

    /* Увімкнення каналу та запуск таймера знеструмлення */
    srv_emergency_all_off();
    g_srv.active_channel = channel;
    g_srv.act_timer_ms = hw_get_tick_ms() + (timeout_sec * 1000);
    hw_gpio_set_relay(channel, true);

    char resp[64];
    snprintf(resp, sizeof(resp), "+OK: RELAY_%u ACTIVE FOR %u SEC\r\n", channel, timeout_sec);
    hw_uart_puts(resp);
}

/* Диспетчер вхідного рядка команд */
static void srv_dispatch_line(const char *cmd) {
    if (strncmp(cmd, "auth challenge", 14) == 0) {
        g_srv.current_nonce = hw_trng_get_random();
        g_srv.state = SRV_STATE_CHALLENGE_ISSUED;
        char resp[64];
        snprintf(resp, sizeof(resp), "+OK: CHALLENGE 0x%08X\r\n", (unsigned int)g_srv.current_nonce);
        hw_uart_puts(resp);
        return;
    }

    if (strncmp(cmd, "auth key ", 9) == 0) {
        if (strcmp(cmd + 9, "SRV_PASS_2026") == 0) {
            g_srv.state = SRV_STATE_UNLOCKED;
            g_srv.session_timer_ms = hw_get_tick_ms() + SESSION_TIMEOUT_MS;
            hw_uart_puts("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
        } else {
            g_srv.state = SRV_STATE_LOCKED;
            hw_uart_puts("-ERR: 0x4004 AUTH_FAILED\r\n");
        }
        return;
    }

    if (g_srv.state != SRV_STATE_UNLOCKED) {
        hw_uart_puts("-ERR: 0x4000 LOCKED_ENTER_AUTH_FIRST\r\n");
        return;
    }

    /* Поновлюємо таймер активності сесії */
    g_srv.session_timer_ms = hw_get_tick_ms() + SESSION_TIMEOUT_MS;

    if (strcmp(cmd, "diag selftest") == 0) {
        cmd_handle_selftest();
    } else if (strncmp(cmd, "diag act relay ", 15) == 0) {
        unsigned int ch = 0, sec = 0;
        if (sscanf(cmd + 15, "%u %u", &ch, &sec) == 2) {
            cmd_handle_actuate((uint8_t)ch, (uint16_t)sec);
        } else {
            hw_uart_puts("-ERR: 0x4005 BAD_ARGUMENTS\r\n");
        }
    } else if (strcmp(cmd, "sys lock") == 0) {
        srv_emergency_all_off();
        g_srv.state = SRV_STATE_LOCKED;
        hw_uart_puts("+OK: SERVICE_LOCKED\r\n");
    } else {
        hw_uart_puts("-ERR: 0x4006 UNKNOWN_COMMAND\r\n");
    }
}

/* Періодичний крок оновлення сервісного рушія (викликається у суперциклі) */
void srv_poll_step(void) {
    uint32_t now = hw_get_tick_ms();

    /* Перевірка тайм-ауту увімкнення навантаження */
    if (g_srv.active_channel != 0 && now >= g_srv.act_timer_ms) {
        srv_emergency_all_off();
        hw_uart_puts("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\nSRV> ");
    }

    /* Перевірка тайм-ауту неактивності сесії */
    if (g_srv.state == SRV_STATE_UNLOCKED && now >= g_srv.session_timer_ms) {
        srv_emergency_all_off();
        g_srv.state = SRV_STATE_LOCKED;
        hw_uart_puts("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
    }
}

/* Прийом чергового байта від UART переривання */
void srv_feed_byte(char c) {
    if (c == '\r' || c == '\n') {
        if (g_srv.rx_idx > 0) {
            g_srv.rx_buf[g_srv.rx_idx] = '\0';
            srv_dispatch_line(g_srv.rx_buf);
            g_srv.rx_idx = 0;
            if (g_srv.state == SRV_STATE_UNLOCKED) {
                hw_uart_puts("SRV> ");
            }
        }
    } else if (g_srv.rx_idx < (CLI_BUFFER_SIZE - 1)) {
        if (c >= 0x20 && c <= 0x7E) { /* Тільки друковані ASCII */
            g_srv.rx_buf[g_srv.rx_idx++] = c;
        }
    }
}
