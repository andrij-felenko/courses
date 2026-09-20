#ifndef RVDT_DECODER_HPP
#define RVDT_DECODER_HPP

#include <cstdint>
#include <cmath>
#include <optional>
#include <array>

namespace hw_controls {

/**
 * @brief Налаштування динамічної розрядності RDC-перетворювача
 */
enum class Resolution : uint8_t {
    Bits10 = 0, ///< 10 біт (максимальна кутова швидкість)
    Bits12 = 1, ///< 12 біт
    Bits14 = 2, ///< 14 біт
    Bits16 = 3  ///< 16 біт (максимальна точність вимірювання)
};

/**
 * @brief Опорна частота генератора збудження первинної обмотки RVDT
 */
enum class ExcitationFreq : uint8_t {
    Freq2kHz  = 0,
    Freq5kHz  = 1,
    Freq10kHz = 2,
    Freq20kHz = 3
};

/**
 * @brief Абстрактний інтерфейс низькорівневого шинного адаптера SPI та ліній GPIO
 */
class IRVdtSpiBus {
public:
    virtual ~IRVdtSpiBus() = default;

    /** @brief Керування лінією вибору пристрою CS (Active Low) */
    virtual void set_cs(bool active) = 0;

    /** @brief Керування лінією стробування вибірки SAMPLE (Active Low) */
    virtual void set_sample(bool active) = 0;

    /** @brief Керування лініями адресації режимів A0 та A1 RDC-конвертера */
    virtual void set_mode_lines(bool a0, bool a1) = 0;

    /** @brief Прийом/передача одного байта по шині SPI */
    virtual uint8_t transfer_byte(uint8_t tx_byte) = 0;

    /** @brief Мікросекундна затримка для витримання часових інтервалів стробування */
    virtual void delay_us(uint32_t microseconds) = 0;
};

/**
 * @brief Прапорці апаратних помилок RDC-конвертера та тракту RVDT
 */
struct FaultFlags {
    bool loss_of_signal{false};       ///< LOS: Розрив ліній або відсутність сигналу збудження
    bool loss_of_tracking{false};     ///< LOT: Втрата відстеження кутового положення сервосистемою
    bool degradation_of_signal{false};///< DOS: Амплітудне спотворення або деградація сигналу RVDT
    bool parity_error{false};         ///< Помилка паритету при прийомі SPI кадру
    bool any_fault{false};            ///< Зведений прапорець наявності хоча б однієї відмови
};

/**
 * @brief Конфігурація драйвера та параметрів RVDT-датчика
 */
struct RVDTConfig {
    Resolution resolution{Resolution::Bits16};
    ExcitationFreq excitation_freq{ExcitationFreq::Freq10kHz};
    float full_scale_angle_deg{60.0f}; ///< Повний діапазон вимірювання кута (наприклад ±60.0°)
    float ratiometric_gain{1.0f};      ///< Коефіцієнт ратіометричної масштабної корекції
};

/**
 * @brief Результат вимірювання кутової позиції та швидкості
 */
struct RVDTMeasurement {
    float angle_deg{0.0f};        ///< Кут повороту вала у градусах
    float angle_rad{0.0f};        ///< Кут повороту вала у радіанах
    int16_t velocity_raw{0};      ///< Сирий код кутової швидкості
    uint16_t raw_code{0};         ///< Сирий цифровий код позиції RDC
    FaultFlags faults{};          ///< Статус апаратних прапорців
    bool valid{false};            ///< Ознака валідності отриманих даних
};

/**
 * @brief Клас драйвера RDC-конвертера для зчитування та діагностики датчиків RVDT
 */
class RVDTDecoder {
public:
    explicit RVDTDecoder(IRVdtSpiBus& bus, const RVDTConfig& config = {})
        : bus_(bus), config_(config) {}

    /**
     * @brief Ініціалізація RDC-конвертера, налаштування регістрів та перевірка зв'язку
     * @return true у разі успішної конфігурації
     */
    bool init();

    /**
     * @brief Зчитування поточної кутової позиції з ратіометричним перерахунком
     * @return Обчислене вимірювання або std::nullopt при помилці SPI
     */
    std::optional<RVDTMeasurement> read_position();

    /**
     * @brief Зчитування регістра статусів апаратних помилок RDC (Address 0xFF / FAULT)
     * @return Структура з розпарсеними прапорцями помилок
     */
    FaultFlags read_faults();

    /**
     * @brief Очищення зафіксованих прапорців помилок (Fault Reset Cycle)
     * @return true після успішного скидання засувок помилок
     */
    bool reset_fault_latch();

    /**
     * @brief Оновлення конфігураційних параметрів
     */
    void set_config(const RVDTConfig& config) { config_ = config; }
    [[nodiscard]] const RVDTConfig& get_config() const { return config_; }

private:
    uint16_t get_max_code_for_resolution() const;
    bool check_parity(uint16_t raw_word) const;

    IRVdtSpiBus& bus_;
    RVDTConfig config_;
    bool initialized_{false};
};

} // namespace hw_controls

#endif // RVDT_DECODER_HPP
