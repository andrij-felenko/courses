#include <iostream>
#include <cstdint>
#include <cstring>
#include <array>
#include <span>
#include <csignal>
#include <system_error>
#include <unistd.h>

namespace security_demo {

/**
 * @brief Клас керування встановленням та відновленням сигнального обробника (RAII).
 */
class ScopedSignalHandler {
public:
    ScopedSignalHandler(int signum, void (*handler)(int, siginfo_t *, void *))
        : signum_(signum) {
        struct sigaction sa{};
        sa.sa_sigaction = handler;
        sa.sa_flags = SA_SIGINFO;
        ::sigemptyset(&sa.sa_mask);

        if (::sigaction(signum_, &sa, &old_act_) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction registration failed");
        }
    }

    ~ScopedSignalHandler() noexcept {
        ::sigaction(signum_, &old_act_, nullptr);
    }

    ScopedSignalHandler(const ScopedSignalHandler &) = delete;
    ScopedSignalHandler &operator=(const ScopedSignalHandler &) = delete;

private:
    int signum_;
    struct sigaction old_act_{};
};

/* Обробник сигналу порушення захисту пам'яті */
void on_segfault(int sig, siginfo_t *info, void *) {
    std::cout << "\n[!] Апаратне перехоплення MMU: Сигнал SIGSEGV (" << sig << ")\n"
              << "    Адреса аварії: " << info->si_addr << "\n";

    if (info->si_code == SEGV_ACCERR) {
        std::cout << "    Код причини: SEGV_ACCERR (Спроба вибірки інструкції зі сторінки NX=1)\n"
                  << "    Результат: Апаратний захист W^X успішно запобіг виконанню стека.\n";
    }

    ::_exit(EXIT_SUCCESS);
}

} // namespace security_demo

int main() {
    try {
        /* Реєстрація RAII-обробника SIGSEGV */
        security_demo::ScopedSignalHandler guard(SIGSEGV, security_demo::on_segfault);

        /* Розміщення байтів машинного коду на стеку (NOP, NOP, RET) */
        alignas(16) std::array<uint8_t, 3> stack_code = { 0x90, 0x90, 0xC3 };

        std::cout << "[+] Стек-буфер розташовано за адресою: "
                  << static_cast<void *>(stack_code.data()) << "\n"
                  << "[+] Виклик функції за адресою стека...\n";

        using ShellcodeFunc = void (*)();
        auto execute_from_stack = reinterpret_cast<ShellcodeFunc>(stack_code.data());

        /* Передача керування: викличе апаратне переривання #PF на сторінці з бітом NX */
        execute_from_stack();

        std::cerr << "[-] КРИТИЧНО: Стек виконуваний! Захист NX відсутній.\n";
        return EXIT_FAILURE;
    } catch (const std::exception &ex) {
        std::cerr << "[-] Помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
}
