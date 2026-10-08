#include <cstdint>

namespace atmospheric {

struct MagnusParams {
    float a; // Основний масштабний коефіцієнт [hPa]
    float b; // Безрозмірний температурний коефіцієнт
    float c; // Температурний зсув знаменника [°C]
};

// Константні конфігурації для фазових станів води та льоду
constexpr MagnusParams PARAMS_WATER{6.112f, 17.62f, 243.12f};
constexpr MagnusParams PARAMS_ICE{6.112f, 22.46f, 272.62f};
constexpr MagnusParams PARAMS_HIGH_TEMP{6.112f, 18.729f, 257.87f};

} // namespace atmospheric
