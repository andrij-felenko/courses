#include <cstdint>
#include <array>

// Оголошення структури кадру HIL_SENSOR у стилі сучасного C++
struct alignas(8) HilSensorMessage {
    uint64_t time_usec{0};           // Монотонний час симуляції у мікросекундах
    float xacc{0.0f};                // Акселерометр X (м/с²) у Body Frame
    float yacc{0.0f};                // Акселерометр Y (м/с²) у Body Frame
    float zacc{0.0f};                // Акселерометр Z (м/с²) у Body Frame
    float xgyro{0.0f};               // Гіроскоп X (рад/с) навколо осі Roll
    float ygyro{0.0f};               // Гіроскоп Y (рад/с) навколо осі Pitch
    float zgyro{0.0f};               // Гіроскоп Z (рад/с) навколо осі Yaw
    float xmag{0.0f};                // Магнітометр X (Гаус)
    float ymag{0.0f};                // Магнітометр Y (Гаус)
    float zmag{0.0f};                // Магнітометр Z (Гаус)
    float abs_pressure{0.0f};        // Абсолютний тиск (гПа / мілібари)
    float diff_pressure{0.0f};       // Диференційний тиск трубки Піто (гПа)
    float pressure_alt{0.0f};        // Розрахована барометрична висота (метри)
    float temperature{0.0f};         // Температура сенсорного модуля (°C)
    uint32_t fields_updated{0};      // Бітова маска оновлених сенсорів
    uint8_t id{0};                   // Ідентифікатор комплексу сенсорів
};
