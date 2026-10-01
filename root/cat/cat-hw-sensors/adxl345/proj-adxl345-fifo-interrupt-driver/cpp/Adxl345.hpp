#ifndef ADXL345_HPP
#define ADXL345_HPP

#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>
#include <unordered_map>
#include <array>

namespace adxl345 {

// Карта регістрів акселерометра ADXL345
namespace Register {
    constexpr uint8_t DEVID          = 0x00; // Ідентифікатор пристрою (0xE5)
    constexpr uint8_t THRESH_TAP     = 0x1D; // Поріг для одиночного/подвійного дотику
    constexpr uint8_t OFSX           = 0x1E; // Зсув осі X
    constexpr uint8_t OFSY           = 0x1F; // Зсув осі Y
    constexpr uint8_t OFSZ           = 0x20; // Зсув осі Z
    constexpr uint8_t BW_RATE        = 0x2C; // Вибір частоти оновлення даних та енергоспоживання
    constexpr uint8_t POWER_CTL      = 0x2D; // Керування режимами живлення
    constexpr uint8_t INT_ENABLE     = 0x2E; // Увімкнення переривань
    constexpr uint8_t INT_MAP        = 0x2F; // Прив'язка переривань до виводів INT1/INT2
    constexpr uint8_t INT_SOURCE     = 0x30; // Джерело виникнення переривання (прапорці)
    constexpr uint8_t DATA_FORMAT    = 0x31; // Формат даних та вибір діапазону
    constexpr uint8_t DATAX0         = 0x32; // Молодший байт осі X
    constexpr uint8_t DATAX1         = 0x33; // Старший байт осі X
    constexpr uint8_t DATAY0         = 0x34; // Молодший байт осі Y
    constexpr uint8_t DATAY1         = 0x35; // Старший байт осі Y
    constexpr uint8_t DATAZ0         = 0x36; // Молодший байт осі Z
    constexpr uint8_t DATAZ1         = 0x37; // Старший байт осі Z
    constexpr uint8_t FIFO_CTL       = 0x38; // Керування режимами FIFO-буфера
    constexpr uint8_t FIFO_STATUS    = 0x39; // Статус FIFO-буфера та кількість елементів
} // namespace Register

// Біти регістра POWER_CTL
namespace PowerCtlBit {
    constexpr uint8_t MEASURE    = (1 << 3); // 1 = вимірювання, 0 = Standby
    constexpr uint8_t SLEEP      = (1 << 2); // Режим сну
    constexpr uint8_t AUTO_SLEEP = (1 << 4); // Автоматичний перехід у сон
} // namespace PowerCtlBit

// Біти регістра DATA_FORMAT
namespace DataFormatBit {
    constexpr uint8_t SELF_TEST  = (1 << 7); // Режим самотестування
    constexpr uint8_t SPI        = (1 << 6); // Режим 3-провідного SPI
    constexpr uint8_t INT_INVERT = (1 << 5); // Інверсія полярності переривань
    constexpr uint8_t FULL_RES   = (1 << 3); // Режим повної роздільної здатності (3.9 mg/LSB)
    constexpr uint8_t JUSTIFY    = (1 << 2); // Вирівнювання (0 = праворуч, 1 = ліворуч)
} // namespace DataFormatBit

// Прапорці переривань регістра INT_ENABLE / INT_SOURCE
namespace IntBit {
    constexpr uint8_t DATA_READY = (1 << 7); // Готовність даних
    constexpr uint8_t SINGLE_TAP = (1 << 6); // Поодинокий дотик
    constexpr uint8_t DOUBLE_TAP = (1 << 5); // Подвійний дотик
    constexpr uint8_t ACTIVITY   = (1 << 4); // Активність (рух)
    constexpr uint8_t INACTIVITY = (1 << 3); // Спокій
    constexpr uint8_t FREE_FALL  = (1 << 2); // Вільне падіння
    constexpr uint8_t WATERMARK  = (1 << 1); // Досягнення порогу заповнення FIFO
    constexpr uint8_t OVERRUN    = (1 << 0); // Переповнення FIFO
} // namespace IntBit

// Очікуваний ID пристрою ADXL345
constexpr uint8_t ADXL345_EXPECTED_DEVID = 0xE5;

// Діапазон вимірювання прискорення
enum class Range : uint8_t {
    Range_2G  = 0x00, // +/- 2g
    Range_4G  = 0x01, // +/- 4g
    Range_8G  = 0x02, // +/- 8g
    Range_16G = 0x03  // +/- 16g
};

// Режими роботи апаратного FIFO-буфера
enum class FifoMode : uint8_t {
    Bypass  = 0x00, // Буфер вимкнено (пряме зчитування)
    Fifo    = 0x01, // Зупинка накопичення при заповненні (32 кадри)
    Stream  = 0x02, // Потоковий буфер (нові дані витісняють найстаріші)
    Trigger = 0x03  // Накопичення до настання події тригера
};

// Типи подій для зворотних викликів (callbacks)
enum class Event : uint8_t {
    Watermark, // Досягнуто рівень Watermark у FIFO
    Overrun,   // Переповнення буфера FIFO
    DataReady  // Новий кадр ready у режимі Bypass
};

// Структура кадру прискорення у фізичних одиницях (g)
struct AccelData {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

// Абстрактний інтерфейс апаратного шинного транспорту (I2C або SPI)
class IBus {
public:
    virtual ~IBus() = default;

    // Запис одного байта в заданий регістр
    virtual bool writeRegister(uint8_t reg, uint8_t value) = 0;

    // Читання одного байта з регістра
    virtual bool readRegister(uint8_t reg, uint8_t& value) = 0;

    // Пакетне неблокуюче зчитування послідовності байтів (burst read)
    virtual bool readBurst(uint8_t startReg, std::span<uint8_t> buffer) = 0;
};

// Драйвер 3-осьового акселерометра ADXL345
class ADXL345 {
public:
    using EventCallback = std::function<void(Event event, std::span<const AccelData> samples)>;

    explicit ADXL345(IBus& bus);
    ~ADXL345() = default;

    // Заборона копіювання об'єкта драйвера
    ADXL345(const ADXL345&) = delete;
    ADXL345& operator=(const ADXL345&) = delete;

    // Семантика переміщення
    ADXL345(ADXL345&&) noexcept = default;
    ADXL345& operator=(ADXL345&&) noexcept = default;

    // Ініціалізація датчика: перевірка DEVID, налаштування розмаху та повної роздільної здатності
    bool init(Range range = Range::Range_2G, bool fullResolution = true);

    // Конфігурація апаратного FIFO-буфера та рівня Watermark (1..31 кадрів)
    bool configureFifo(FifoMode mode, uint8_t watermarkLevel);

    // Керування режимом вимірювання (Standby / Measurement mode)
    bool setMeasurementMode(bool enable);

    // Реєстрація функцій зворотного виклику для подій переривань
    void registerCallback(Event event, EventCallback callback);

    // Перевірка джерел переривань і виклик відповідних callbacks (викликається у суперциклі)
    bool processInterrupts();

    // Неблокуюче пакетне вивантаження накопичених кадрів із FIFO (burst read)
    bool readFifoBurst(std::span<AccelData> outputBuffer, size_t& readCount);

    // Зчитування поодинокого кадру прискорення
    bool readSingleSample(AccelData& sample);

    // Запит кількості доступних кадрів у FIFO-буфері
    bool getFifoEntryCount(uint8_t& count);

private:
    IBus& bus_;
    Range range_{Range::Range_2G};
    bool fullRes_{true};
    float scaleFactor_{0.00390625f}; // Множник перерахунку в g (3.9 mg/LSB)

    std::unordered_map<Event, EventCallback> callbacks_;
    std::array<AccelData, 32> internalBuffer_{};

    void updateScaleFactor();
    AccelData convertRawToG(int16_t rawX, int16_t rawY, int16_t rawZ) const;
};

} // namespace adxl345

#endif // ADXL345_HPP
