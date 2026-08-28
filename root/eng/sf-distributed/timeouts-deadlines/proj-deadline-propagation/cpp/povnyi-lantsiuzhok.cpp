/* Імітація обробки конвеєра в C++ */
bool execute_subcall(std::string_view name,
                     const DeadlineContext& parent,
                     std::chrono::milliseconds configured_limit) {
    auto sub_ctx = derive_subcall_context(parent, configured_limit);
    if (!sub_ctx) {
        std::cout << "[-] " << name << ": ВІДХИЛЕНО НА СТАРТІ (залишок "
                  << parent.remaining().count() << " мс замалий)\n";
        return false;
    }

    std::cout << "[+] " << name << ": запуск із таймаутом "
              << sub_ctx->remaining().count() << " мс (батьківський залишок: "
              << parent.remaining().count() << " мс)\n";

    /* Імітація роботи сервісу 40 мс */
    ::usleep(40 * 1000);

    std::cout << "[+] " << name << ": завершено. Новий залишок: "
              << parent.remaining().count() << " мс\n";
    return true;
}

int main() {
    std::cout << "=== ДЕМОНСТРАЦІЯ НАСКРІЗНОГО БЮДЖЕТУ ЧАСУ (C++) ===\n\n";

    /* 1. Отримання вхідного запиту з бюджетом 150 мс */
    auto root_ctx = parse_deadline("150", std::chrono::milliseconds(10),
                                   std::chrono::milliseconds(500));
    if (!root_ctx || root_ctx->is_expired()) {
        std::cerr << "[!] Некоректний або прострочений запит на вході\n";
        return 1;
    }

    std::cout << "[Вхід] Запит отримано. Бюджет: "
              << root_ctx->remaining().count() << " мс\n";

    /* 2. Перебування в черзі воркерів 50 мс */
    ::usleep(50 * 1000);
    std::cout << "[Черга] Потік звільнився. Залишок: "
              << root_ctx->remaining().count() << " мс\n";

    /* 3. Крок 1: AuthService */
    if (!execute_subcall("AuthService", *root_ctx, std::chrono::milliseconds(100))) {
        std::cerr << "[!] Auth провалено\n";
        return 1;
    }

    /* 4. Крок 2: PaymentService */
    if (!execute_subcall("PaymentService", *root_ctx, std::chrono::milliseconds(100))) {
        std::cerr << "[!] Payment провалено\n";
        return 1;
    }

    /* 5. Крок 3: NotificationService */
    if (!execute_subcall("NotificationService", *root_ctx, std::chrono::milliseconds(80))) {
        std::cout << "[!] Notification відхилено за браком часу, переводимо в async fallback\n";
    }

    std::cout << "\n[Результат] Операція завершена успішно.\n";
    return 0;
}
