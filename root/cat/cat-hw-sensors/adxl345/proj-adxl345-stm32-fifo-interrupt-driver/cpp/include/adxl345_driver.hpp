#ifndef ADXL345_DRIVER_HPP
#define ADXL345_DRIVER_HPP

#include <cstdint>
#include <cstddef>
#include <functional>

namespace adxl345 {

// Регістри акселерометра ADXL345
namespace Register {
    constexpr uint8_t DEVID          = 0x00; // Ідентифікатор пристрою (очікується 0xE5)
    constexpr uint8_t THRESH_TAP     = 0x1D; // Поріг подвійного/одиночного торкання
    constexpr uint8_t OFSX           = 0x1E; // Зміщення осі X
    constexpr uint8_t OFSY           = 0x1F; // Зміщення осі Y
    constexpr uint8_t OFSZ           = 0x20; // Зміщення осі Z
    constexpr uint8_t BW_RATE        = 0x2C; // Частота вибірок і режим вимірювання
    constexpr uint8_t POWER_CTL      = 0x2D; // Керування живленням
    constexpr uint8_t INT_ENABLE     = 0x2E; // Увімкнення джерел переривань
    constexpr uint8_t INT_MAP        = 0x2F; // Прив'язка переривань до виводів INT1/INT2
    constexpr uint8_t INT_SOURCE     = 0x30; // Статус джерел переривань (Read-only)
    constexpr uint8_t DATA_FORMAT    = 0x31; // Формат даних та діапазон вимірювань
    constexpr uint8_t DATAX0         = 0x32; // Молодший байт осі X
    constexpr uint8_t DATAX1         = 0x33; // Старший байт осі X
    constexpr uint8_t DATAY0         = 0x34; // Молодший байт осі Y
    constexpr uint8_t DATAY1         = 0x35; // Старший байт осі Y
    constexpr uint8_t DATAZ0         = 0x36; // Молодший байт осі Z
    constexpr uint8_t DATAZ1         = 0x37; // Старший байт осі Z
    constexpr uint8_t FIFO_CTL       = 0x38; // Керування режимом FIFO
    constexpr uint8_t FIFO_STATUS    = 0x39; // Статус буфера FIFO
}

// Маски бітів регістрів ADXL345
namespace Mask {
    // POWER_CTL
    constexpr uint8_t POWER_CTL_MEASURE = (1 << 3);
    constexpr uint8_t POWER_CTL_SLEEP   = (1 << 2);

    // INT_ENABLE / INT_MAP / INT_SOURCE
    constexpr uint8_t INT_DATA_READY    = (1 << 7);
    constexpr uint8_t INT_SINGLE_TAP    = (1 << 6);
    constexpr uint8_t INT_DOUBLE_TAP    = (1 << 5);
    constexpr uint8_t INT_ACTIVITY      = (1 << 4);
    constexpr uint8_t INT_INACTIVITY    = (1 << 3);
    constexpr uint8_t INT_FREE_FALL     = (1 << 2);
    constexpr uint8_t INT_WATERMARK     = (1 << 1);
    constexpr uint8_t INT_OVERRUN       = (1 << 0);

    // DATA_FORMAT
    constexpr uint8_t DATA_FORMAT_SELF_TEST = (1 << 7);
    constexpr uint8_t DATA_FORMAT_SPI       = (1 << 6);
    constexpr uint8_t DATA_FORMAT_INT_INVERT = (1 << 5);
    constexpr uint8_t DATA_FORMAT_FULL_RES   = (1 << 3);
    constexpr uint8_t DATA_FORMAT_JUSTIFY    = (1 << 2);

    // FIFO_CTL режими
    constexpr uint8_t FIFO_MODE_BYPASS  = (0x00 << 6);
    constexpr uint8_t FIFO_MODE_FIFO    = (0x01 << 6);
    constexpr uint8_t FIFO_MODE_STREAM  = (0x02 << 6);
    constexpr uint8_t FIFO_MODE_TRIGGER = (0x03 << 6);
}

// Константа Device ID ADXL345
constexpr uint8_t ADXL345_EXPECTED_DEVID = 0xE5;

// Фізичні діапазони вимірювання
enum class Range : uint8_t {
    G2  = 0x00, // ±2g (10-бітний або full-res)
    G4  = 0x01, // ±4g
    G8  = 0x02, // ±8g
    G16 = 0x03  // ±16g
};

// Одиниці вимірювання для конвертера
enum class Unit {
    G,             // Прискорення у g
    MetersPerSecSq // Прискорення у м/с²
};

// Структура 3-осьового сирого вектора (LSB)
struct RawVector3 {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

// Структура 3-осьового вектора прискорення (фізичні величини)
struct AccelerationVector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

// Шаблонізований типобезпечний конвертер одиниць вимірювання
template <Unit TargetUnit>
class UnitConverter {
public:
    static constexpr float STANDARD_GRAVITY = 9.80665f; // Прискорення вільного падіння м/с²

    // Конвертація одиничного сирого значення LSB
    static constexpr float convert_value(int16_t raw_lsb, Range range, bool full_res = true) {
        float lsb_per_g = 256.0f; // В режимі FULL_RES чутливість стала: 3.9 mg/LSB (256 LSB/g)
        if (!full_res) {
            switch (range) {
                case Range::G2:  lsb_per_g = 256.0f; break; // 10 біт: ±2g  => 256 LSB/g
                case Range::G4:  lsb_per_g = 128.0f; break; // 10 біт: ±4g  => 128 LSB/g
                case Range::G8:  lsb_per_g = 64.0f;  break; // 10 біт: ±8g  => 64 LSB/g
                case Range::G16: lsb_per_g = 32.0f;  break; // 10 біт: ±16g => 32 LSB/g
            }
        }
        float g_val = static_cast<float>(raw_lsb) / lsb_per_g;

        if constexpr (TargetUnit == Unit::G) {
            return g_val;
        } else if constexpr (TargetUnit == Unit::MetersPerSecSq) {
            return g_val * STANDARD_GRAVITY;
        }
    }

    // Конвертація 3-осьового вектора
    static constexpr AccelerationVector3 convert_vector(const RawVector3& raw, Range range, bool full_res = true) {
        return AccelerationVector3{
            convert_value(raw.x, range, full_res),
            convert_value(raw.y, range, full_res),
            convert_value(raw.z, range, full_res)
        };
    }
};

// Абстрактний інтерфейс апаратної шини SPI/I2C
class IBus {
public:
    virtual ~IBus() = default;
    virtual void acquire() = 0;
    virtual void release() = 0;
    virtual bool read_registers(uint8_t reg, uint8_t* buffer, size_t len) = 0;
    virtual bool write_register(uint8_t reg, uint8_t value) = 0;
};

// RAII-обгортка для автоматичного захоплення та звільнення апаратної шини
class BusGuard {
public:
    explicit BusGuard(IBus& bus) : bus_(bus), acquired_(true) {
        bus_.acquire();
    }

    ~BusGuard() {
        if (acquired_) {
            bus_.release();
        }
    }

    BusGuard(const BusGuard&) = delete;
    BusGuard& operator=(const BusGuard&) = delete;

    BusGuard(BusGuard&& other) noexcept : bus_(other.bus_), acquired_(other.acquired_) {
        other.acquired_ = false;
    }

    BusGuard& operator=(BusGuard&& other) = delete;

private:
    IBus& bus_;
    bool acquired_;
};

// Головний клас C++ драйвера ADXL345
class Adxl345Driver {
public:
    using WatermarkCallback = std::function<void()>;

    explicit Adxl345Driver(IBus& bus);
    ~Adxl345Driver() = default;

    // Первинна ініціалізація та перевірка DEVID
    bool init(Range range = Range::G2, bool full_res = true);

    // Налаштування режиму FIFO Stream та порогу Watermark
    bool configure_fifo_watermark(uint8_t watermark_samples, uint8_t int_pin = 1);

    // Зчитати один сирий 3-осьовий вектор
    bool read_raw_accel(RawVector3& raw);

    // Пакетне burst-зчитування накопичених вибірок із FIFO-буфера
    size_t read_fifo_burst(RawVector3* out_buffer, size_t max_samples);

    // Реєстрація C++ callback-обробника події Watermark
    void set_watermark_callback(WatermarkCallback cb);

    // Виклик обробника події заповнення FIFO (викликається із подійної системи)
    void handle_watermark_event();

    Range get_current_range() const { return current_range_; }
    bool is_full_resolution() const { return full_resolution_; }

private:
    IBus& bus_;
    Range current_range_{Range::G2};
    bool full_resolution_{true};
    WatermarkCallback watermark_cb_{nullptr};

    bool write_register(uint8_t reg, uint8_t val);
    bool read_registers(uint8_t reg, uint8_t* buffer, size_t len);
};

} // namespace adxl345

#endif // ADXL345_DRIVER_HPP
