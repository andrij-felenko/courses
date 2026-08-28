#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <algorithm>
#include <optional>
#include <string_view>

enum class BoardRev : uint8_t {
    Unknown = 0x00,
    RevA    = 0x01,
    RevB    = 0x02,
    RevC    = 0x03
};

enum class PinTristate : uint8_t {
    PullDown = 0,
    PullUp   = 1,
    Floating = 2
};

struct AdcRevWindow {
    uint16_t raw_min;
    uint16_t raw_max;
    BoardRev revision;
};

/* Чистий інтерфейс давача */
class IImuDriver {
public:
    virtual ~IImuDriver() = default;
    virtual bool init() = 0;
    virtual bool read_accel(float& x, float& y, float& z) = 0;
    virtual bool read_gyro(float& x, float& y, float& z) = 0;
    virtual void sleep() = 0;
};

struct BoardDescriptor {
    BoardRev         revision;
    std::string_view board_name;
    uint8_t          spi_bus_index;
    uint16_t         cs_pin_mask;
    float            accel_gain_correction;
    IImuDriver*      imu_driver;
};

/* Апаратні абстракції */
extern "C" {
    uint16_t hal_adc_read_raw(uint8_t channel);
    void     hal_gpio_set_mode_input(uint8_t pin);
    void     hal_gpio_set_pullup(uint8_t pin);
    void     hal_gpio_set_pulldown(uint8_t pin);
    void     hal_gpio_set_floating(uint8_t pin);
    bool     hal_gpio_read(uint8_t pin);
    void     hal_delay_us(uint32_t us);
}

class BoardIdDetector {
public:
    static constexpr std::array<AdcRevWindow, 3> kAdcWindows{{
        { 0,    500,  BoardRev::RevA },
        { 800,  1400, BoardRev::RevB },
        { 1700, 2300, BoardRev::RevC },
    }};

    static BoardRev read_from_adc(uint8_t adc_channel) {
        std::array<uint16_t, 16> samples{};
        for (auto& s : samples) {
            s = hal_adc_read_raw(adc_channel);
            hal_delay_us(50);
        }

        std::sort(samples.begin(), samples.end());
        const uint16_t median = samples[samples.size() / 2];

        for (const auto& w : kAdcWindows) {
            if (median >= w.raw_min && median <= w.raw_max) {
                return w.revision;
            }
        }
        return BoardRev::Unknown;
    }

    static PinTristate detect_tristate(uint8_t pin) {
        hal_gpio_set_mode_input(pin);

        hal_gpio_set_pullup(pin);
        hal_delay_us(100);
        const bool with_up = hal_gpio_read(pin);

        hal_gpio_set_pulldown(pin);
        hal_delay_us(100);
        const bool with_down = hal_gpio_read(pin);

        hal_gpio_set_floating(pin);

        if (with_up && !with_down) {
            return PinTristate::Floating;
        } else if (with_up && with_down) {
            return PinTristate::PullUp;
        } else {
            return PinTristate::PullDown;
        }
    }
};

/* Конкретні класи драйверів */
class Bmi270Driver final : public IImuDriver {
public:
    bool init() override { return true; }
    bool read_accel(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 1.0f;
        return true;
    }
    bool read_gyro(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 0.0f;
        return true;
    }
    void sleep() override {}
};

class Lsm6dsoDriver final : public IImuDriver {
public:
    bool init() override { return true; }
    bool read_accel(float& x, float& y, float& z) override {
        x = 0.01f; y = -0.02f; z = 0.99f;
        return true;
    }
    bool read_gyro(float& x, float& y, float& z) override {
        x = 0.0f; y = 0.0f; z = 0.0f;
        return true;
    }
    void sleep() override {}
};

class BspManager {
private:
    static inline Bmi270Driver  s_bmi270{};
    static inline Lsm6dsoDriver s_lsm6dso{};

    static constexpr size_t kMaxBoards = 2;
    static inline const std::array<BoardDescriptor, kMaxBoards> s_descriptors{{
        {
            BoardRev::RevA,
            "SensorNode-v1.2-RevA",
            1,
            (1u << 4),
            1.002f,
            &s_bmi270
        },
        {
            BoardRev::RevB,
            "SensorNode-v2.0-RevB",
            2,
            (1u << 12),
            0.995f,
            &s_lsm6dso
        }
    }};

public:
    static std::optional<BoardDescriptor> get_descriptor(BoardRev rev) {
        for (const auto& desc : s_descriptors) {
            if (desc.revision == rev) {
                return desc;
            }
        }
        return std::nullopt;
    }
};
