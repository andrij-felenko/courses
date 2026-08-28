#include <cstdint>
#include <cstddef>
#include <array>
#include <string_view>
#include <optional>

enum class BoardHwRev : uint8_t {
    Unknown = 0,
    Rev1    = 1,
    Rev2    = 2
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

/* Чистий інтерфейс датчика інерції */
class IImuSensor {
public:
    virtual ~IImuSensor() = default;
    virtual bool init() = 0;
    virtual bool get_accel(Vector3f& acc) = 0;
    virtual bool get_gyro(Vector3f& gyr) = 0;
};

/* Дескриптор плати */
struct BoardBspConfig {
    BoardHwRev       revision;
    std::string_view name;
    uint8_t          spi_channel;
    uint16_t         cs_gpio_pin;
    IImuSensor      *imu_driver;
};

/* Реалізації драйверів під конкретні мікросхеми */
class Bmi270Driver final : public IImuSensor {
public:
    bool init() override { return true; }
    bool get_accel(Vector3f& acc) override {
        acc = {0.0f, 0.0f, 1.0f};
        return true;
    }
    bool get_gyro(Vector3f& gyr) override {
        gyr = {0.0f, 0.0f, 0.0f};
        return true;
    }
};

class Lsm6dsoDriver final : public IImuSensor {
public:
    bool init() override { return true; }
    bool get_accel(Vector3f& acc) override {
        acc = {0.01f, -0.02f, 0.99f};
        return true;
    }
    bool get_gyro(Vector3f& gyr) override {
        gyr = {0.0f, 0.0f, 0.0f};
        return true;
    }
};

class BspManager {
private:
    static inline Bmi270Driver  s_bmi270{};
    static inline Lsm6dsoDriver s_lsm6dso{};

    static constexpr size_t kMaxBoards = 2;
    static inline const std::array<BoardBspConfig, 2> s_boards{{
        { BoardHwRev::Rev1, "Device-Rev1.0", 1, 4,  &s_bmi270 },
        { BoardHwRev::Rev2, "Device-Rev2.0", 2, 12, &s_lsm6dso }
    }};

    static inline const BoardBspConfig* s_active_config{nullptr};

public:
    static bool init(BoardHwRev rev) {
        for (const auto& board : s_boards) {
            if (board.revision == rev) {
                s_active_config = &board;
                return s_active_config->imu_driver->init();
            }
        }
        return false;
    }

    static std::optional<Vector3f> read_acceleration() {
        if (!s_active_config || !s_active_config->imu_driver) {
            return std::nullopt;
        }
        Vector3f acc;
        if (s_active_config->imu_driver->get_accel(acc)) {
            return acc;
        }
        return std::nullopt;
    }
};
