#include <stdio.h>
#include <string.h>
#include <errno.h>

/* Друк структурованих повідомлень у stdout з префіксами для journald */
void log_service_events(const char *db_name, int port) {
    fprintf(stdout, "<6>Ініціалізація мережевого сервера на порту %d успішна\n", port);
    fprintf(stderr, "<3>Помилка відкриття файлу бази даних '%s': %s\n", 
            db_name, strerror(ENOENT));
    fflush(stdout);
    fflush(stderr);
}
