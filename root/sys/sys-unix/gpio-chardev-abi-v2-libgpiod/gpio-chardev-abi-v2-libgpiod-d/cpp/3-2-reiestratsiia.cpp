#include <cstdint>

// Концептуальна C++ абстракція для драйверів контролерів у змішаних середовищах
class GpioControllerBase {
public:
    virtual ~GpioControllerBase() = default;

    virtual int direction_input(unsigned int offset) = 0;
    virtual int direction_output(unsigned int offset, int value) = 0;
    virtual int get_value(unsigned int offset) const = 0;
    virtual void set_value(unsigned int offset, int value) = 0;
    virtual void set_multiple(unsigned long mask, unsigned long bits) = 0;

    [[nodiscard]] virtual bool can_sleep() const noexcept { return false; }
    [[nodiscard]] virtual std::uint16_t num_lines() const noexcept = 0;
};
