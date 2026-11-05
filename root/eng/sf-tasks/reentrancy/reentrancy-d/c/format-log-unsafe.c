#include <stdio.h>
#include <time.h>

// НЕРЕЕНТЕРАБЕЛЬНИЙ ВАРІАНТ: використовує статичний буфер у сегменті даних.
// Якщо обробник сигналів перерве виконання цієї функції і викличе її знову,
// вміст буфера буде зіпсовано.
const char* format_log_unsafe(const char* level, const char* message) {
    static char buffer[256]; // Статичний буфер — джерело проблеми!
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);

    snprintf(buffer, sizeof(buffer), "[%02d:%02d:%02d] [%s] %s",
             tm_info->tm_hour, tm_info->tm_min, tm_info->tm_sec,
             level, message);

    return buffer; // Повернення вказівника на спільний статичний масив
}

// РЕЕНТЕРАБЕЛЬНИЙ ВАРІАНТ: буфер та його розмір передаються викликачем.
// Функція працює виключно з автоматичною пам'яттю на стекі викликача.
int format_log_reentrant(char* out_buf, size_t out_size, const char* level, const char* message) {
    if (!out_buf || out_size == 0) {
        return -1;
    }

    time_t now = time(NULL);
    struct tm tm_info;
    
    // Використовуємо gmtime_r замість нереентерабельного gmtime/localtime
    if (gmtime_r(&now, &tm_info) == NULL) {
        return -1;
    }

    int written = snprintf(out_buf, out_size, "[%02d:%02d:%02d] [%s] %s",
                           tm_info->tm_hour, tm_info->tm_min, tm_info->tm_sec,
                           level, message);

    return (written >= 0 && (size_t)written < out_size) ? 0 : -1;
}
