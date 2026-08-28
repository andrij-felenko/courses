#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define AT_BUF_SIZE        256
#define UART_TIMEOUT_MS    5000

typedef enum {
    MODEM_OK = 0,
    MODEM_ERROR_TIMEOUT,
    MODEM_ERROR_RESPONSE,
    MODEM_ERROR_REGISTRATION
} modem_status_t;

/* Структура конфігурації таймерів PSM */
typedef struct {
    uint32_t periodic_tau_sec;  /* Бажаний інтервал Periodic TAU в секундах */
    uint32_t active_time_sec;   /* Бажаний інтервал Active Time в секундах */
} psm_config_t;

/* Функції низькорівневого вводу-виводу UART (платформозалежні заглушки) */
extern void platform_uart_send(const char *data, size_t len);
extern size_t platform_uart_receive_line(char *buf, size_t max_len, uint32_t timeout_ms);
extern void platform_delay_ms(uint32_t ms);
extern void platform_gpio_set_dtr(bool high);

/* Кодування інтервалу в 8-бітний рядок GPRS Timer 3 (T3412-ext) за 3GPP TS 24.008 */
static bool encode_t3412(uint32_t seconds, char *out_str) {
    uint8_t unit_bits = 0;
    uint32_t value = 0;

    if (seconds <= 62) {
        unit_bits = 0b011; /* Крок 2 с */
        value = seconds / 2;
    } else if (seconds <= 31 * 60) {
        unit_bits = 0b101; /* Крок 1 хв */
        value = seconds / 60;
    } else if (seconds <= 31 * 600) {
        unit_bits = 0b000; /* Крок 10 хв */
        value = seconds / 600;
    } else if (seconds <= 31 * 3600) {
        unit_bits = 0b001; /* Крок 1 год */
        value = seconds / 3600;
    } else if (seconds <= 31 * 36000) {
        unit_bits = 0b010; /* Крок 10 год */
        value = seconds / 36000;
    } else if (seconds <= 31 * 320 * 3600) {
        unit_bits = 0b110; /* Крок 320 год */
        value = seconds / (320 * 3600);
    } else {
        return false; /* Перевищення ліміту 413 днів */
    }

    if (value > 31) value = 31;
    if (value == 0) value = 1;

    /* Формування 8-бітного рядка "b8b7b6b5b4b3b2b1" */
    for (int i = 2; i >= 0; i--) {
        *out_str++ = ((unit_bits >> i) & 1) ? '1' : '0';
    }
    for (int i = 4; i >= 0; i--) {
        *out_str++ = ((value >> i) & 1) ? '1' : '0';
    }
    *out_str = '\0';
    return true;
}

/* Кодування інтервалу в 8-бітний рядок GPRS Timer 2 (T3324) за 3GPP TS 24.008 */
static bool encode_t3324(uint32_t seconds, char *out_str) {
    uint8_t unit_bits = 0;
    uint32_t value = 0;

    if (seconds == 0) {
        strcpy(out_str, "11100000"); /* Деактивовано: миттєвий перехід у PSM */
        return true;
    } else if (seconds <= 62) {
        unit_bits = 0b000; /* Крок 2 с */
        value = seconds / 2;
    } else if (seconds <= 31 * 60) {
        unit_bits = 0b001; /* Крок 1 хв */
        value = seconds / 60;
    } else if (seconds <= 31 * 360) {
        unit_bits = 0b010; /* Крок 6 хв (декада) */
        value = seconds / 360;
    } else {
        return false; /* Перевищення максимального значення 186 хв */
    }

    if (value > 31) value = 31;
    if (value == 0) value = 1;

    for (int i = 2; i >= 0; i--) {
        *out_str++ = ((unit_bits >> i) & 1) ? '1' : '0';
    }
    for (int i = 4; i >= 0; i--) {
        *out_str++ = ((value >> i) & 1) ? '1' : '0';
    }
    *out_str = '\0';
    return true;
}

/* Надсилання AT-команди та очікування відповіді "OK" */
modem_status_t modem_send_cmd_expect_ok(const char *cmd, uint32_t timeout_ms) {
    char rx_buf[AT_BUF_SIZE];
    platform_uart_send(cmd, strlen(cmd));
    platform_uart_send("\r\n", 2);

    uint32_t elapsed = 0;
    while (elapsed < timeout_ms) {
        size_t len = platform_uart_receive_line(rx_buf, sizeof(rx_buf) - 1, 500);
        if (len > 0) {
            rx_buf[len] = '\0';
            if (strstr(rx_buf, "OK") != NULL) {
                return MODEM_OK;
            }
            if (strstr(rx_buf, "ERROR") != NULL || strstr(rx_buf, "+CME ERROR") != NULL) {
                return MODEM_ERROR_RESPONSE;
            }
        }
        elapsed += 500;
    }
    return MODEM_ERROR_TIMEOUT;
}

/* Конфігурація режимів енергозбереження PSM та eDRX */
modem_status_t modem_configure_power_saving(const psm_config_t *cfg) {
    char t3412_str[9];
    char t3324_str[9];
    char at_cmd[128];

    if (!encode_t3412(cfg->periodic_tau_sec, t3412_str) ||
        !encode_t3324(cfg->active_time_sec, t3324_str)) {
        return MODEM_ERROR_RESPONSE;
    }

    /* Налаштування PSM: AT+CPSMS=1,,,"<T3412>","<T3324>" */
    snprintf(at_cmd, sizeof(at_cmd), "AT+CPSMS=1,,,\"%s\",\"%s\"", t3412_str, t3324_str);
    modem_status_t status = modem_send_cmd_expect_ok(at_cmd, UART_TIMEOUT_MS);
    if (status != MODEM_OK) return status;

    /* Налаштування eDRX: AT+CEDRXS=1,5,"0010" (AcT=5 NB-IoT, цикл 40.96 с) */
    status = modem_send_cmd_expect_ok("AT+CEDRXS=1,5,\"0010\"", UART_TIMEOUT_MS);
    return status;
}

/* Перевірка реєстрації в мережі оператора */
modem_status_t modem_wait_network_registration(uint32_t timeout_sec) {
    char rx_buf[AT_BUF_SIZE];
    uint32_t elapsed = 0;

    while (elapsed < timeout_sec) {
        platform_uart_send("AT+CEREG?\r\n", 12);
        size_t len = platform_uart_receive_line(rx_buf, sizeof(rx_buf) - 1, 1000);
        if (len > 0) {
            rx_buf[len] = '\0';
            /* Статуси 1 (Home) та 5 (Roaming) свідчать про успішну реєстрацію */
            if (strstr(rx_buf, "+CEREG: 4,1") != NULL || strstr(rx_buf, "+CEREG: 4,5") != NULL ||
                strstr(rx_buf, "+CEREG: 1") != NULL || strstr(rx_buf, "+CEREG: 5") != NULL) {
                return MODEM_OK;
            }
        }
        platform_delay_ms(1000);
        elapsed += 1;
    }
    return MODEM_ERROR_REGISTRATION;
}

/* Відправка UDP дейтаграми з телеметрією */
modem_status_t modem_send_udp_telemetry(const char *server_ip, uint16_t port,
                                        const uint8_t *payload, size_t payload_len) {
    char cmd[128];
    /* Відкриття UDP сокета: AT+QIOPEN=1,0,"UDP","<IP>",<PORT>,0,0 */
    snprintf(cmd, sizeof(cmd), "AT+QIOPEN=1,0,\"UDP\",\"%s\",%u,0,0", server_ip, port);
    if (modem_send_cmd_expect_ok(cmd, UART_TIMEOUT_MS) != MODEM_OK) {
        return MODEM_ERROR_RESPONSE;
    }

    /* Підготовка до передачі даних фіксованої довжини */
    snprintf(cmd, sizeof(cmd), "AT+QISEND=0,%zu", payload_len);
    platform_uart_send(cmd, strlen(cmd));
    platform_uart_send("\r\n", 2);
    platform_delay_ms(100);

    /* Надсилання сирого бінарного корисного навантаження */
    platform_uart_send((const char *)payload, payload_len);
    platform_delay_ms(200);

    /* Закриття сокета після підтвердження відправки */
    modem_send_cmd_expect_ok("AT+QICLOSE=0", UART_TIMEOUT_MS);
    return MODEM_OK;
}

/* Повний робочий цикл вимірювання та сну */
void telemetry_node_run_cycle(void) {
    /* 1. Апаратне пробудження модема через лінію DTR */
    platform_gpio_set_dtr(false);
    platform_delay_ms(50);

    /* 2. Ініціалізація модема */
    modem_send_cmd_expect_ok("AT", UART_TIMEOUT_MS);
    modem_send_cmd_expect_ok("AT+CEREG=4", UART_TIMEOUT_MS);

    /* 3. Встановлення конфігурації сну: TAU = 24 год, Active Time = 10 с */
    psm_config_t psm = { .periodic_tau_sec = 86400, .active_time_sec = 10 };
    modem_configure_power_saving(&psm);

    /* 4. Очікування мережі та відправка пакету */
    if (modem_wait_network_registration(60) == MODEM_OK) {
        uint8_t telemetry_data[8] = { 0xAA, 0x01, 0x18, 0x2A, 0x0C, 0x55, 0x00, 0xFF };
        modem_send_udp_telemetry("198.51.100.42", 5683, telemetry_data, sizeof(telemetry_data));
    }

    /* 5. Дозвіл модему перейти в режим сну: піднімаємо DTR у високий стан */
    platform_gpio_set_dtr(true);
}
