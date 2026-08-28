#include <type_traits>
#include <cstdint>

enum class EngineState : uint8_t {
    kStopped = 0,
    kStarting = 1,
    kRunning = 2,
    kFault = 255
};

// Конвертація з цілого числа (наприклад, з двійкового протоколу):
uint8_t raw_byte = 2;
auto state = static_cast<EngineState>(raw_byte);

// Зворотна конвертація у базовий цілочисельний тип:
auto raw_val = static_cast<std::underlying_type_t<EngineState>>(state);
