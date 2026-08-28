/* C: Традиційне використання sprintf та snprintf */
#include <stdio.h>

void log_connection(const char* host, int port) {
    char buffer[128];

    /* Потенційне переповнення буфера у sprintf при занадто довгому host */
    sprintf(buffer, "Connecting to %s:%d", host, port);

    /* Безпечніша альтернатива C99 snprintf з явним обмеженням розміру */
    snprintf(buffer, sizeof(buffer), "Connecting to %s:%d", host, port);
}
