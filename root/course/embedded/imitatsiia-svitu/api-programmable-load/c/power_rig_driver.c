/* power_rig_driver.c - Драйвер керування живленням та навантаженням на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int socket_fd;
    char ip_address[32];
    double max_voltage_limit;
    double max_current_limit;
    bool is_output_enabled;
} power_supply_t;

typedef struct {
    int socket_fd;
    char ip_address[32];
    bool is_input_enabled;
} electronic_load_t;

/* Допоміжна функція надсилання SCPI команди */
static bool scpi_send(int sock_fd, const char *cmd) {
    /* У реальному стенді: return send(sock_fd, cmd, strlen(cmd), 0) > 0; */
    printf("[SCPI OUT] %s", cmd);
    return true;
}

/* Ініціалізація симулятора батареї */
bool power_supply_init(power_supply_t *ps, const char *ip, double ovp, double ocp) {
    if (!ps || !ip) return false;
    strncpy(ps->ip_address, ip, sizeof(ps->ip_address) - 1);
    ps->max_voltage_limit = ovp;
    ps->max_current_limit = ocp;
    ps->is_output_enabled = false;

    char cmd[64];
    /* Вимкнення виходу перед конфігурацією для безпеки */
    scpi_send(ps->socket_fd, ":OUTP:STAT OFF\n");

    /* Встановлення апаратних порогів захисту */
    snprintf(cmd, sizeof(cmd), ":PROT:VOLT %.2f\n", ovp);
    scpi_send(ps->socket_fd, cmd);
    snprintf(cmd, sizeof(cmd), ":PROT:CURR %.2f\n", ocp);
    scpi_send(ps->socket_fd, cmd);

    return true;
}

/* Налаштування параметрів батареї: ЕРС та внутрішнього опору R_int */
bool power_supply_set_battery_profile(power_supply_t *ps, double vocv, double r_int) {
    if (!ps || vocv > ps->max_voltage_limit) return false;

    char cmd[64];
    snprintf(cmd, sizeof(cmd), ":SOUR:VOLT %.3f\n", vocv);
    scpi_send(ps->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":SOUR:RES %.4f\n", r_int);
    scpi_send(ps->socket_fd, cmd);

    return true;
}

/* Запуск імпульсного навантаження для тестування просідання напруги */
bool electronic_load_trigger_pulse(electronic_load_t *load, double base_a, double peak_a, double pulse_sec) {
    if (!load) return false;

    char cmd[64];
    scpi_send(load->socket_fd, ":MODE CC\n");
    
    snprintf(cmd, sizeof(cmd), ":TRAN:MODE PULSE\n");
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:ALEV %.2f\n", base_a);
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:BLEV %.2f\n", peak_a);
    scpi_send(load->socket_fd, cmd);

    snprintf(cmd, sizeof(cmd), ":TRAN:BWID %.4f\n", pulse_sec);
    scpi_send(load->socket_fd, cmd);

    scpi_send(load->socket_fd, ":INP:STAT ON\n");
    return true;
}
