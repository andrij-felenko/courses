/* Приклад функції відправки даних у сокет через AT+CIPSEND на C */
#include <stdio.h>
#include <string.h>

bool esp01_send_socket_data(int socket_id, const char *data, size_t len) {
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%d,%zu\r\n", socket_id, len);
    
    /* Надсилання AT-команди на модуль */
    printf("%s", cmd);
    
    /* Очікування символу запрошення '>' від модуля */
    /* Після отримання '>' передається безпосередньо корисний буфер */
    printf("%.*s", (int)len, data);
    return true;
}
