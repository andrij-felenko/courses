// startup.cpp — Ідіоматична стартова ініціалізація мовою C++20
#include <cstdint>
#include <span>
#include <algorithm>

// Імпорт символів зі скрипта компонування
extern "C" {
    extern std::uint32_t _sidata[];
    extern std::uint32_t _sdata[];
    extern std::uint32_t _edata[];
    extern std::uint32_t _sbss[];
    extern std::uint32_t _ebss[];

    void __libc_init_array() noexcept;
    int main();
    void Reset_Handler() noexcept;
}

void Reset_Handler() noexcept {
    // 1. Безпечне перенесення .data через std::span та std::copy
    const auto data_words = static_cast<std::size_t>(_edata - _sdata);
    const std::span<const std::uint32_t> flash_data{_sidata, data_words};
    const std::span<std::uint32_t> ram_data{_sdata, data_words};
    std::copy(flash_data.begin(), flash_data.end(), ram_data.begin());

    // 2. Обнулення .bss через std::fill
    const auto bss_words = static_cast<std::size_t>(_ebss - _sbss);
    const std::span<std::uint32_t> ram_bss{_sbss, bss_words};
    std::fill(ram_bss.begin(), ram_bss.end(), 0U);

    // 3. Ініціалізація глобальних об'єктів C++ (конструктори .init_array)
    __libc_init_array();

    // 4. Передача керування в main()
    main();

    while (true) {
        asm volatile("wfi");
    }
}
