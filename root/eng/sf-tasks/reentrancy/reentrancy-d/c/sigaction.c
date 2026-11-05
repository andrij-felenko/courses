#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

// НЕБЕЗПЕЧНИЙ ВАРІАНТ: використання неатомарних змінних та нереентерабельних функцій
int g_unsafe_counter = 0; // Звичайна змінна в сегменті даних — загроза torn write!

void unsafe_signal_handler(int sig) {
    // КРИТИЧНА ПОМИЛКА 1: printf() не є асинхронно-сигнально безпечною функцією!
    // КРИТИЧНА ПОМИЛКА 2: ++g_unsafe_counter не є атомарною операцією!
    printf("Отримано сигнал %d, лічильник: %d\n", sig, ++g_unsafe_counter);
}

// БЕЗПЕЧНИЙ ВАРІАНТ: використання volatile sig_atomic_t та системного виклику write()
static volatile sig_atomic_t g_signal_flag = 0;

void safe_signal_handler(int sig) {
    (void)sig;
    // Атомарний запис прапорця за один шинний такт без побічних ефектів
    g_signal_flag = 1;
}

int main(void) {
    struct sigaction sa;
    sa.sa_handler = safe_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    if (sigaction(SIGINT, &sa, NULL) < 0) {
        return 1;
    }

    const char start_msg[] = "Програма запущена. Натисніть Ctrl+C для відправки SIGINT...\n";
    // Системний виклик write() є асинхронно-сигнально безпечним
    write(STDOUT_FILENO, start_msg, sizeof(start_msg) - 1);

    while (!g_signal_flag) {
        // Основний цикл перевіряє прапорець без блокування ресурсів
        usleep(100000);
    }

    const char exit_msg[] = "Сигнал успішно зафіксовано. Безпечний вихід з програми.\n";
    write(STDOUT_FILENO, exit_msg, sizeof(exit_msg) - 1);

    return 0;
}
