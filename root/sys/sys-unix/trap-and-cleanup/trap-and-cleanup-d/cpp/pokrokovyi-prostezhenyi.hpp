#include <csignal>
#include <unistd.h>
#include <cstdlib>

namespace {
    extern "C" void reraise_dispatcher(int sig) noexcept {
        // 1. Звільнення ресурсів
        
        // 2. Скидання диспозиції на стан за замовчуванням
        struct sigaction sa{};
        sa.sa_handler = SIG_DFL;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;
        sigaction(sig, &sa, nullptr);

        // 3. Повторна генерація сигналу для встановлення WIFSIGNALED
        std::raise(sig);
    }
}
