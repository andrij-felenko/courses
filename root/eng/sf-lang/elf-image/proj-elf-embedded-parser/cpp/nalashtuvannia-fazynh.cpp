#include <cstdint>
#include <cstddef>
#include <span>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;
    
    // Створення безпечного представлення для мутованого двійкового потоку
    std::span<const uint8_t> fuzz_buffer(data, size);
    elf::ElfParser parser(fuzz_buffer);
    
    // Запуск парсингу - парсер НЕ ПОВИНЕН падати або викликати витоки пам'яті!
    auto summary = parser.parse();
    (void)summary;
    
    return 0;
}
