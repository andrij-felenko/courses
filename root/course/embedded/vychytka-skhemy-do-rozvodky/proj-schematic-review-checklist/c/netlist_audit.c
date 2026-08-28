/* netlist_audit.c - перевірка парності інтерфейсних сигналів у нетлісті */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NETS 512
#define NAME_LEN 64

typedef struct {
    char name[NAME_LEN];
    bool verified;
} NetEntry;

static NetEntry g_nets[MAX_NETS];
static size_t g_net_count = 0;

void add_net(const char *name) {
    if (g_net_count >= MAX_NETS) return;
    strncpy(g_nets[g_net_count].name, name, NAME_LEN - 1);
    g_nets[g_net_count].name[NAME_LEN - 1] = '\0';
    g_nets[g_net_count].verified = false;
    g_net_count++;
}

bool find_net(const char *name) {
    for (size_t i = 0; i < g_net_count; ++i) {
        if (strcmp(g_nets[i].name, name) == 0) return true;
    }
    return false;
}

void verify_uart_and_diff_pairs(void) {
    printf("=== АУДИТ ПАРНОСТІ СИГНАЛІВ СХЕМИ ===\n");
    int issues = 0;

    for (size_t i = 0; i < g_net_count; ++i) {
        char *p = strstr(g_nets[i].name, "_TX");
        if (p && strlen(p) == 3) {
            char expected_rx[NAME_LEN];
            size_t prefix_len = (size_t)(p - g_nets[i].name);
            strncpy(expected_rx, g_nets[i].name, prefix_len);
            expected_rx[prefix_len] = '\0';
            strcat(expected_rx, "_RX");

            if (!find_net(expected_rx)) {
                printf("[ПОМИЛКА] Знайдено сигнал '%s', але відсутній парний '%s'\n",
                       g_nets[i].name, expected_rx);
                issues++;
            }
        }

        /* Перевірка диференційних пар _P та _N */
        char *dp = strstr(g_nets[i].name, "_P");
        if (dp && strlen(dp) == 2) {
            char expected_n[NAME_LEN];
            size_t prefix_len = (size_t)(dp - g_nets[i].name);
            strncpy(expected_n, g_nets[i].name, prefix_len);
            expected_n[prefix_len] = '\0';
            strcat(expected_n, "_N");

            if (!find_net(expected_n)) {
                printf("[ПОМИЛКА] Диференційна лінія '%s' не має пари '%s'\n",
                       g_nets[i].name, expected_n);
                issues++;
            }
        }
    }

    if (issues == 0) {
        printf("[OK] Усі перевірені інтерфейсні пари збігаються.\n");
    } else {
        printf("[УВАГА] Виявлено дефектів: %d. Перевірте опечатки в Net Labels!\n", issues);
    }
}

int main(void) {
    /* Симуляція завантаження міток із САПР */
    add_net("MCU_UART1_TX");
    add_net("MCU_UART1_RX");
    add_net("DEBUG_UART_TX"); /* Без пари - викличе попередження */
    add_net("USB_DP_P");
    add_net("USB_DP_N");
    add_net("CAN_P");          /* Без CAN_N - помилка */

    verify_uart_and_diff_pairs();
    return 0;
}
