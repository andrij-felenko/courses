// privtrap.cpp — опитування CPL та ізольоване тестування привілейованих інструкцій
// Linux, x86-64. Збірка: g++ -O2 -std=c++20 -o privtrap privtrap.cpp
#define _GNU_SOURCE
#include <array>
#include <csetjmp>
#include <csignal>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iostream>
#include <string_view>

namespace {

sigjmp_buf g_resume;
volatile sig_atomic_t g_got_signo = 0;
volatile sig_atomic_t g_got_code = 0;
volatile uint64_t g_produced = 0;

void on_trap(int signo, siginfo_t* si, void* /*uctx*/) {
    g_got_signo = signo;
    g_got_code = si->si_code;
    siglongjmp(g_resume, 1);
}

[[nodiscard]] unsigned get_cpl() noexcept {
    uint16_t cs = 0;
    __asm__ volatile ("mov %%cs, %0" : "=r"(cs));
    return static_cast<unsigned>(cs & 3u);
}

struct Probe {
    std::string_view mnem;
    void (*run)();
    std::string_view description;
};

void try_one(const Probe& p) {
    g_got_signo = 0;
    g_produced = 0;
    if (sigsetjmp(g_resume, 1) == 0) {
        p.run();
        std::cout << "  " << p.mnem << " виконано, результат 0x"
                  << std::hex << g_produced << std::dec << " (" << p.description << ")\n";
    } else {
        std::cout << "  " << p.mnem << " пастка: "
                  << strsignal(g_got_signo) << ", si_code=" << g_got_code
                  << " (" << p.description << ")\n";
    }
}

} // namespace

int main() {
    std::cout << "рівень привілею цього процесу: CPL = " << get_cpl() << "\n\n";

    struct sigaction sa{};
    sa.sa_sigaction = on_trap;
    sa.sa_flags = SA_SIGINFO;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, nullptr);
    sigaction(SIGILL, &sa, nullptr);

    constexpr std::array probes = {
        Probe{"nop",   [] { __asm__ volatile ("nop"); }, "звичайна команда — контроль"},
        Probe{"hlt",   [] { __asm__ volatile ("hlt"); }, "зупинка CPU"},
        Probe{"cli",   [] { __asm__ volatile ("cli"); }, "вимикання переривань"},
        Probe{"cr0",   [] {
            uint64_t v = 0;
            __asm__ volatile ("mov %%cr0, %0" : "=r"(v));
            g_produced = v;
        }, "читання CR0"},
        Probe{"rdmsr", [] {
            uint32_t lo = 0, hi = 0;
            __asm__ volatile ("rdmsr" : "=a"(lo), "=d"(hi) : "c"(0xC0000080u));
            g_produced = (static_cast<uint64_t>(hi) << 32) | lo;
        }, "читання EFER MSR"},
        Probe{"smsw",  [] {
            uint16_t w = 0;
            __asm__ volatile ("smsw %0" : "=r"(w));
            g_produced = w;
        }, "читання 16 бітів CR0"},
        Probe{"sldt",  [] {
            uint16_t s = 0;
            __asm__ volatile ("sldt %0" : "=r"(s));
            g_produced = s;
        }, "читання селектора LDT"},
        Probe{"ud2",   [] { __asm__ volatile ("ud2"); }, "невизначена інструкція"}
    };

    for (const auto& probe : probes) {
        try_one(probe);
    }
    return 0;
}
