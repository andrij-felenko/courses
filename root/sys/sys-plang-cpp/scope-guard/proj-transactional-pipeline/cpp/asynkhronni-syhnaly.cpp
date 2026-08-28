#include <signal.h>

void safe_signal_transaction() {
    sigset_t block_mask, old_mask;
    sigemptyset(&block_mask);
    sigaddset(&block_mask, SIGINT);
    sigaddset(&block_mask, SIGTERM);

    // Блокуємо сигнали на час критичної секції
    pthread_sigmask(SIG_BLOCK, &block_mask, &old_mask);
    auto sig_guard = make_scope_guard([&old_mask] noexcept {
        // Гарантоване відновлення маски сигналів на виході
        pthread_sigmask(SIG_SETMASK, &old_mask, nullptr);
    });

    // Виконання атомарного збереження конфігурації...
}
