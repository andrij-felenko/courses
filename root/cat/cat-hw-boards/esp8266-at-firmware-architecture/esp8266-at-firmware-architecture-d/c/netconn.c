#include "lwip/netconn.h"
#include "lwip/ip_addr.h"
#include "esp_log.h"
#include <string.h>
#include <stdlib.h>

// Структура обробника AT-команди AT+CIPSTART
typedef struct {
    int link_id;
    char type[4];
    char addr[64];
    uint16_t port;
} at_cipstart_param_t;

// Фрагмент FSM-парсер та трансляція в netconn API
int at_setup_cipstart_handler(const char *cmd_args) {
    at_cipstart_param_t param;
    memset(&param, 0, sizeof(param));

    // Синтаксичний розбір аргументів: id,"type","addr",port
    if (sscanf(cmd_args, "%d,\"%3[^\"]\",\"%63[^\"]\",%hu", 
               &param.link_id, param.type, param.addr, &param.port) < 4) {
        return -1; // Помилка синтаксису
    }

    ip_addr_t remote_ip;
    if (!ipaddr_aton(param.addr, &remote_ip)) {
        return -2; // Некоректна IP-адреса
    }

    // Створення сокета через netconn API
    struct netconn *conn = netconn_new(NETCONN_TCP);
    if (conn == NULL) {
        return -3; // Вичерпано DRAM кучу під TCP PCB
    }

    // Блокуючий виклик підключення (виконується через tcpip_thread)
    err_t err = netconn_connect(conn, &remote_ip, param.port);
    if (err != ERR_OK) {
        netconn_delete(conn);
        return -4; // Відмова у з'єднанні
    }

    return 0; // OK
}
