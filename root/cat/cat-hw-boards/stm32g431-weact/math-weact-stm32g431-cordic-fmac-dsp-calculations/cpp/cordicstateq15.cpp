// C++ реалізація ітераційного кроку CORDIC у форматі з фіксованою комою Q1.15
#include <cstdint>
#include <array>

struct CordicStateQ15 {
    int16_t x;
    int16_t y;
    int16_t z;
};

class CordicAcceleratorQ15 {
private:
    static constexpr std::array<int16_t, 15> lut_q15 = {
        8192, 4836, 2555, 1297, 651, 326, 163, 81, 41, 20, 10, 5, 3, 1, 1
    };

public:
    static void step(CordicStateQ15& state, uint8_t i) {
        const int16_t d = (state.z >= 0) ? 1 : -1;
        const int16_t x_shift = static_cast<int16_t>(state.x >> i);
        const int16_t y_shift = static_cast<int16_t>(state.y >> i);

        if (d > 0) {
            state.x = static_cast<int16_t>(state.x - y_shift);
            state.y = static_cast<int16_t>(state.y + x_shift);
            state.z = static_cast<int16_t>(state.z - lut_q15[i]);
        } else {
            state.x = static_cast<int16_t>(state.x + y_shift);
            state.y = static_cast<int16_t>(state.y - x_shift);
            state.z = static_cast<int16_t>(state.z + lut_q15[i]);
        }
    }
};
