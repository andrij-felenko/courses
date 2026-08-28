#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <string.h>

static volatile sig_atomic_t g_signal_count = 0;

static void user_signal_handler(int signo) {
    (void)signo;
    g_signal_count++;
}

static void* signal_emitter_thread(void *arg) {
    pthread_t target = *(pthread_t*)arg;
    for (int i = 0; i < 6; ++i) {
        struct timespec ts = { .tv_sec = 0, .tv_nsec = 25000000 }; // 25 мс
        nanosleep(&ts, NULL);
        pthread_kill(target, SIGUSR1);
    }
    return NULL;
}

int main(void) {
    // 1. Реєструємо обробник сигналу БЕЗ SA_RESTART для демонстрації переривань
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = user_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0; // Навмисно вимикаємо авто-перезапуск
    if (sigaction(SIGUSR1, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    int pipefds[2];
    if (pipe(pipefds) == -1) {
        perror("pipe");
        return 1;
    }

    pthread_t main_thread = pthread_self();
    pthread_t emitter;
    if (pthread_create(&emitter, NULL, signal_emitter_thread, &main_thread) != 0) {
        perror("pthread_create");
        return 1;
    }

    printf("[Головний потік] Очікування даних із каналу під час надходження сигналів...\n");

    // Запишемо тестове повідомлення в канал
    const char message[] = "System Programming in Unix\n";
    write(pipefds[1], message, sizeof(message));

    char buffer[128];
    size_t count = sizeof(message);
    size_t total_read = 0;
    int eintr_retries = 0;

    // Цикл стійкого читання з підрахунком подоланих EINTR
    while (total_read < count) {
        ssize_t res = read(pipefds[0], buffer + total_read, count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                eintr_retries++;
                printf("  -> [Перехоплено EINTR #%d] Системний виклик перервано, перезапуск...\n", eintr_retries);
                continue;
            }
            perror("read error");
            break;
        }
        if (res == 0) {
            printf("[Головний потік] Досягнуто кінця каналу (EOF)\n");
            break;
        }
        total_read += (size_t)res;
    }

    printf("[Головний потік] Успішно прочитано %zu байтів: %s", total_read, buffer);
    printf("[Підсумок] Отримано сигналів процесом: %d, виконано перезапусків виклику: %d\n", 
           (int)g_signal_count, eintr_retries);

    pthread_join(emitter, NULL);
    close(pipefds[0]);
    close(pipefds[1]);
    return 0;
}
