#include <iostream>
#include <thread>
#include <vector>
#include <string_view>
#include <format>
#include <cstdint>
#include <asm/prctl.h>
#include <sys/prctl.h>

extern "C" int arch_prctl(int code, unsigned long *addr);

// Оголошення потоко-локальних змінних у C++11 із вибором моделей доступу
thread_local int global_tls_var = 100;
[[gnu::tls_model("local-exec")]] thread_local int le_tls_var = 200;
[[gnu::tls_model("initial-exec")]] thread_local int ie_tls_var = 300;

class TLSInspector {
public:
    static std::uintptr_t get_fs_base() noexcept {
        std::uintptr_t fs_base = 0;
#if defined(__x86_64__)
        __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif
        return fs_base;
    }

    static std::uintptr_t get_fs_via_syscall() noexcept {
        unsigned long fs_syscall = 0;
        ::arch_prctl(ARCH_GET_FS, &fs_syscall);
        return fs_syscall;
    }

    static void print_info(std::string_view thread_name) {
        const auto fs_base = get_fs_base();
        const auto fs_syscall = get_fs_via_syscall();
        const auto* fs_ptr = reinterpret_cast<const char*>(fs_base);

        std::cout << std::format("=== [{}] (ID: {}) ===\n", thread_name, std::this_thread::get_id());
        std::cout << std::format("  Базова адреса FS (з FS:0): 0x{:x}\n", fs_base);
        std::cout << std::format("  Базова адреса FS (з syscall): 0x{:x}\n", fs_syscall);

        const auto off_global = reinterpret_cast<const char*>(&global_tls_var) - fs_ptr;
        const auto off_le     = reinterpret_cast<const char*>(&le_tls_var) - fs_ptr;
        const auto off_ie     = reinterpret_cast<const char*>(&ie_tls_var) - fs_ptr;

        std::cout << std::format("  &global_tls_var: 0x{:p} | зміщення від FS: {} байтів\n",
                                 static_cast<const void*>(&global_tls_var), off_global);
        std::cout << std::format("  &le_tls_var:     0x{:p} | зміщення від FS: {} байтів\n",
                                 static_cast<const void*>(&le_tls_var), off_le);
        std::cout << std::format("  &ie_tls_var:     0x{:p} | зміщення від FS: {} байтів\n\n",
                                 static_cast<const void*>(&ie_tls_var), off_ie);
    }
};

int main() {
    TLSInspector::print_info("Головний потік (Main)");

    std::vector<std::jthread> threads;
    threads.emplace_back([] { TLSInspector::print_info("Робочий потік 1"); });
    threads.emplace_back([] { TLSInspector::print_info("Робочий потік 2"); });

    return 0;
}
