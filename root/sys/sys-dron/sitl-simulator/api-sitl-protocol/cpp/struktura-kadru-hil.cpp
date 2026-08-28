#include <cstdint>
#include <array>

// Оголошення структури актуаторів у стилі сучасного C++
struct alignas(8) HilActuatorControlsMessage {
    uint64_t time_usec{0};           // Часова мітка автопілота (мкс)
    uint64_t flags{0};               // Прапорці конфігурації режиму
    std::array<float, 16> controls{};// Нормалізовані керуючі сигнали
    uint8_t mode{0};                 // Стан озброєння системи (MAV_MODE_FLAG)
};
