/* repl_async.c — Неблокуючий цикл подій із Readline та poll() на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <poll.h>
#include <time.h>
#include <readline/readline.h>
#include <readline/history.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_resized = 0;

static void handle_signal(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        g_running = 0;
    } else if (sig == SIGWINCH) {
        g_resized = 1;
    }
}

/* Колбек, який викликає Readline при натисканні Enter */
static void line_handler(char *line) {
    if (line == NULL) {
        /* EOF (Ctrl+D) */
        g_running = 0;
        return;
    }

    if (*line != '\0') {
        add_history(line);
        if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
            g_running = 0;
        } else {
            printf("[Оброблено команду]: %s\n", line);
        }
    }

    free(line);
}

int main(void) {
    struct sigaction sa;
    struct pollfd pfd;
    time_t last_tick = time(NULL);

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGWINCH, &sa, NULL);

    /* Реєструємо колбек-обробник і встановлюємо сирий режим термінала */
    rl_callback_handler_install("async-shell> ", line_handler);

    pfd.fd = STDIN_FILENO;
    pfd.events = POLLIN;

    while (g_running) {
        /* Обробка асинхронної зміни геометрії вікна термінала */
        if (g_resized) {
            g_resized = 0;
            rl_resize_terminal();
        }

        /* Очікуємо введення від користувача з таймаутом 500 мс */
        int ret = poll(&pfd, 1, 500);

        if (ret > 0 && (pfd.revents & POLLIN)) {
            /* Передаємо доступні байти Readline для обробки клавіш */
            rl_callback_read_char();
        }

        /* Фонова періодична робота: кожні 5 секунд показуємо повідомлення */
        time_t now = time(NULL);
        if (now - last_tick >= 5) {
            last_tick = now;

            /* Зберігаємо поточний стан вводу, друкуємо повідомлення й відновлюємо промпт */
            rl_save_prompt();
            write(1, "\n[Фонова подія]: сервер активний\n", 34);
            rl_restore_prompt();
            rl_forced_update_display();
        }
    }

    /* Обов'язкове відновлення початкового стану термінала перед виходом */
    rl_callback_handler_remove();
    printf("\nАсинхронний цикл завершено.\n");
    return 0;
}
