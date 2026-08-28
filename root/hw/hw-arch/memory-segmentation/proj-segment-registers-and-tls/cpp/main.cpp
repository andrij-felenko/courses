#include <iostream>
#include <iomanip>
#include <thread>
#include <array>
#include <cstdint>
#include <string_view>
#include <unistd.h>
#include <sys/syscall.h>
#include <asm/prctl.h>

extern "C" int arch_prctl(int code, unsigned long addr);

namespace x86_inspection {

/* Локальні змінні потоку стандарту C++11/C++20 */
thread_local uint64_t g_thread_sequence{0xABCDEF0123456789ULL};
thread_local std::array<char, 32> g_thread_name{"Робочий потік C++"};

/* Безпечна обгортка для отримання бази FS */
[[nodiscard]] inline uint64_t read_fs_base() noexcept {
    unsigned long base{0};
    if (syscall(SYS_arch_prctl, ARCH_GET_FS, &base) == 0) {
        return static_cast<uint64_t>(base);
    }
    return 0;
}

/* Зчитування внутрішнього покажчика на TCB через префікс сегмента fs: */
[[nodiscard]] inline uint64_t read_fs_self() noexcept {
    uint64_t self_val{0};
    asm volatile("movq %%fs:0x0, %0" : "=r"(self_val));
    return self_val;
}

/* Зчитування еталону канарки захисту стека */
[[nodiscard]] inline uint64_t read_stack_guard() noexcept {
    uint64_t canary_val{0};
    asm volatile("movq %%fs:0x28, %0" : "=r"(canary_val));
    return canary_val;
}

void print_thread_diagnostics(std::string_view label) {
    const uint64_t fs_base = read_fs_base();
    const uint64_t fs_self = read_fs_self();
    const uint64_t canary  = read_stack_guard();
    
    const auto seq_addr = reinterpret_cast<uintptr_t>(&g_thread_sequence);
    const auto name_addr = reinterpret_cast<uintptr_t>(g_thread_name.data());
    
    std::cout << "\n[" << label << " | Thread ID: " << std::this_thread::get_id() << "]\n"
              << std::hex << std::setfill('0')
              << "  FS_BASE (через ядро)       : 0x" << std::setw(16) << fs_base << "\n"
              << "  Самопокажчик (fs:0x0)      : 0x" << std::setw(16) << fs_self << "\n"
              << "  Stack Canary (fs:0x28)     : 0x" << std::setw(16) << canary << "\n"
              << std::dec
              << "  Адреса g_thread_sequence   : 0x" << std::hex << seq_addr
              << " (зсув від FS: " << std::dec << static_cast<int64_t>(seq_addr - fs_base) << " байтів)\n"
              << "  Адреса g_thread_name       : 0x" << std::hex << name_addr
              << " (зсув від FS: " << std::dec << static_cast<int64_t>(name_addr - fs_base) << " байтів)\n";
}

} // namespace x86_inspection

int main() {
    std::cout << "=== Дослідження сегментації x86-64 та регістра FS (C++20) ===\n";
    
    x86_inspection::print_thread_diagnostics("Головний потік");
    
    std::jthread worker1([] {
        x86_inspection::print_thread_diagnostics("Потік A");
    });
    
    std::jthread worker2([] {
        x86_inspection::print_thread_diagnostics("Потік B");
    });
    
    return 0;
}
