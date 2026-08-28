/* Імітація виклику мікросервісу з контролем бюджету */
int call_downstream_service(const char *name, int sock_fd, const deadline_context_t *parent_ctx,
                            int64_t configured_timeout_ms) {
    deadline_context_t sub_ctx;
    if (!create_subcall_context(parent_ctx, configured_timeout_ms, 15, &sub_ctx)) {
        printf("[-] %s: ВІДХИЛЕНО НА СТАРТІ (залишок %lld мс замалий для виклику)\n",
               name, (long long)context_remaining_ms(parent_ctx));
        return -1;
    }

    printf("[+] %s: запуск із таймаутом %lld мс (залишок батька %lld мс)\n",
           name, (long long)context_remaining_ms(&sub_ctx),
           (long long)context_remaining_ms(parent_ctx));

    /* Імітуємо відправку заголовка дедлайну та очікування відповіді */
    char hdr[64];
    serialize_deadline_header(&sub_ctx, hdr, sizeof(hdr));

    /* Імітуємо читання відповіді */
    uint8_t resp_buf[16];
    if (sock_fd >= 0) {
        if (read_exact_with_deadline(sock_fd, resp_buf, sizeof(resp_buf), &sub_ctx) != 0) {
            printf("[-] %s: ТАЙМАУТ / ПОМИЛКА під час очікування відповіді\n", name);
            return -1;
        }
    } else {
        /* Імітація локальної роботи (наприклад, 40 мс) */
        usleep(40 * 1000);
    }

    printf("[+] %s: успішно завершено, новий залишок %lld мс\n",
           name, (long long)context_remaining_ms(parent_ctx));
    return 0;
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ НАСКРІЗНОГО БЮДЖЕТУ ЧАСУ (C) ===\n\n");

    /* 1. Клієнтський запит із бюджетом 150 мс */
    const char *incoming_header = "150";
    deadline_context_t root_ctx;
    parse_deadline_header(incoming_header, 10, 500, &root_ctx);

    printf("[Вхід] Запит отримано. Дедлайн через %lld мс\n",
           (long long)context_remaining_ms(&root_ctx));

    /* 2. Імітуємо затримку в черзі пулу потоків (Admission Delay) */
    usleep(50 * 1000); /* 50 мс у черзі */
    printf("[Черга] Потік узяв запит у роботу. Залишок: %lld мс\n",
           (long long)context_remaining_ms(&root_ctx));

    /* 3. Крок 1: Аутентифікація (налаштований ліміт 100 мс) */
    if (call_downstream_service("AuthService", -1, &root_ctx, 100) != 0) {
        printf("[!] Запит провалено на етапі Auth\n");
        return 1;
    }

    /* 4. Крок 2: Платіж (налаштований ліміт 100 мс) */
    if (call_downstream_service("PaymentService", -1, &root_ctx, 100) != 0) {
        printf("[!] Запит провалено на етапі Payment\n");
        return 1;
    }

    /* 5. Крок 3: Сповіщення (налаштований ліміт 80 мс) */
    if (call_downstream_service("NotificationService", -1, &root_ctx, 80) != 0) {
        printf("[!] Notification відхилено за браком часу, переводимо в async fallback\n");
    }

    printf("\n[Результат] Операція завершена в межах дедлайну.\n");
    return 0;
}
