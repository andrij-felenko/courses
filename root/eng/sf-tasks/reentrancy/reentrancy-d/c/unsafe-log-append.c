#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>

// Глобальний статичний буфер — прихований змінюваний стан
static char g_log_buffer[256];
static size_t g_write_pos = 0;

// Нереентерабельна функція додавання тексту до логу
void unsafe_log_append(const char *text) {
    // Скидання позиції перед записом робить функцію нестійкою до переривань
    g_write_pos = 0;
    
    for (size_t i = 0; text[i] != '\0'; i++) {
        if (g_write_pos < sizeof(g_log_buffer) - 1) {
            g_log_buffer[g_write_pos] = text[i];
            g_write_pos++;
            
            // Затримка імітує проміжок часу між інструкціями процесора
            usleep(1);
        }
    }
    g_log_buffer[g_write_pos] = '\0';
}

// Обробник сигналу, що повторно викликає небезпечну функцію
void signal_handler(int sig) {
    (void)sig;
    // Повторний вхід у функцію під час незавершеного основного виклику
    unsafe_log_append("[SIGNAL] Interrupted!");
}
