#include <iostream>
#include <span>
#include <cstdint>
#include <unistd.h>
#include <sys/mman.h>

// Оголошення зовнішніх символів компонувальника GCC/Clang
extern "C" {
    extern char __start_my_init[];
    extern char __stop_my_init[];
}

// Використання стандартних атрибутів C++20 з розширеннями GNU
#define MY_INIT [[gnu::section("my_init"), gnu::aligned(4096)]]

MY_INIT const char init_payload[] = "C++ Init Payload Structure Configuration";

MY_INIT void execute_cpp_init() {
    std::cout << "[INIT C++] Виконання ранньої ініціалізації: " << init_payload << std::endl;
}

// RAII-обгортка для автоматичного контролю життєвого циклу секції ініціалізації
class InitSectionPurger {
public:
    InitSectionPurger(void* start, void* end) noexcept
        : start_(reinterpret_cast<uintptr_t>(start)),
          end_(reinterpret_cast<uintptr_t>(end)) {}

    ~InitSectionPurger() {
        const size_t page_size = static_cast<size_t>(sysconf(_SC_PAGESIZE));
        const uintptr_t page_start = start_ & ~(page_size - 1);
        const uintptr_t page_end = (end_ + page_size - 1) & ~(page_size - 1);
        const size_t len = page_end - page_start;

        if (len > 0 && munmap(reinterpret_cast<void*>(page_start), len) == 0) {
            std::cout << "[RAII Purger] Секція init-пам'яті (" << len 
                      << " байтів) успішно деалокована." << std::endl;
        }
    }

    // Заборона копіювання для збереження семантики унікального володіння
    InitSectionPurger(const InitSectionPurger&) = delete;
    InitSectionPurger& operator=(const InitSectionPurger&) = delete;

private:
    uintptr_t start_;
    uintptr_t end_;
};

int main() {
    {
        // Контекст ініціалізації: RAII-об'єкт автоматично демонтує пам'ять при виході
        InitSectionPurger purger(__start_my_init, __stop_my_init);
        execute_cpp_init();
    }

    std::cout << "[MAIN] Програма працює у штатному режимі користувацького простору." << std::endl;
    return 0;
}
