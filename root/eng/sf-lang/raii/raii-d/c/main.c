#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;

int write_log_entry_c(const char* message) {
    // Ручне блокування
    if (pthread_mutex_lock(&log_mutex) != 0) {
        return -1;
    }

    // Ручне відкриття файлу
    FILE* file = fopen("app.log", "a");
    if (!file) {
        // Помилка: не забути розблокувати м'ютекс перед виходом!
        pthread_mutex_unlock(&log_mutex);
        return -2;
    }

    // Ручне виділення пам'яті
    size_t len = strlen(message);
    char* buffer = (char*)malloc(len + 1);
    if (!buffer) {
        // Помилка: не забути закрити файл І розблокувати м'ютекс!
        fclose(file);
        pthread_mutex_unlock(&log_mutex);
        return -3;
    }

    memcpy(buffer, message, len);
    buffer[len] = '\0';

    if (len == 0) {
        // Ранній вихід: знову повний ручний ритуал очищення
        free(buffer);
        fclose(file);
        pthread_mutex_unlock(&log_mutex);
        return 0;
    }

    fwrite(buffer, 1, len, file);
    fputc('\n', file);

    // Фінальне ручне звільнення на успішному шляху
    free(buffer);
    fclose(file);
    pthread_mutex_unlock(&log_mutex);
    return 0;
}
