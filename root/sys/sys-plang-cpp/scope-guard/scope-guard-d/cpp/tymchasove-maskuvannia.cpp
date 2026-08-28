#include <csignal>
#include <scope>

void execute_critical_section() {
    sigset_t new_mask, old_mask;
    sigfillset(&new_mask);
    // Блокуємо всі сигнали для поточного потоку
    pthread_sigmask(SIG_SETMASK, &new_mask, &old_mask);

    // Охоронець гарантовано відновить початкову маску при будь-якому виході
    std::scope_exit signal_restorer = [&old_mask] noexcept {
        pthread_sigmask(SIG_SETMASK, &old_mask, nullptr);
    };

    // Виконання чутливої операції...
}
