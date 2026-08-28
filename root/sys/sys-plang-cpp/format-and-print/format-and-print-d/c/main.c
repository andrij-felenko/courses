/* Традиційний підхід мовою C: snprintf із фіксованим буфером */
#include <stdio.h>
#include <stddef.h>

void format_address_c(char* buf, size_t buf_size, const char* host, int port) {
    /* Потенційна небезпека: якщо host буде некоректним вказівником або специфікатор %s 
       отримає int, компілятор C не виявить помилку на етапі збірки.
       При перевищенні buf_size рядок буде обрізано без попередження. */
    snprintf(buf, buf_size, "Server %s listening on port %d", host, port);
}
