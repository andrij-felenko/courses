#pragma once

#include "spi_interface.hpp"
#include <cstdint>
#include <optional>

namespace resolver {

/**
 * @brief Режими роботи AD2S1210, що задаються комбінацією ліній A0 та A1.
 */
enum class Mode : std::uint8_t {
    Position      = 0b00, ///< Зчитання кутового положення (A1=0, A0=0)
    Velocity      = 0b01, ///< Зчитання кутової швидкості (A1=0, A0=1)
    Reserved      = 0b10, ///< Зарезервований режим (A1=1, A0=0)
    Configuration = 0b11  ///< Конфігураційний режим читання/запису регістрів (A1=1, A0=1)
};

/**
 * @brief Роздільна здатність перетворювача «резольвер-цифра» AD2S1210.
 */
enum class Resolution : std::uint8_t {
    Res10Bit = 10,
    Res12Bit = 12,
    Res14Bit = 14,
    Res16Bit = 16
};

/**
 * @brief Структура для збереження та дешифрування станів регістра помилок Fault Register.
 */
struct FaultStatus {
    bool configuration_parity_error{false}; ///< D7: Помилка парності конфігурації
    bool phase_error{false};                ///< D6: Помилка фази збудження/сигналу
    bool velocity_overflow{false};         ///< D5: Переповнення кутової швидкості
    bool loss_of_tracking{false};          ///< D4: Втрата стеження (LOT - Loss of Tracking)
    bool degradation_of_signal{false};     ///< D3: Деградація сигналу (DOS)
    bool loss_of_signal{false};            ///< D2: Втрата сигналу (LOS)
    bool parity_error{false};              ///< D1: Помилка парності шини даних
    bool reference_loss{false};            ///< D0: Втрата опорного сигналу

    std::uint8_t raw_value{0};             ///< Сире значення регістра помилок

    /// Перевірка наявності будь-якої критичної помилки
    [[nodiscard]] bool has_fault() const noexcept {
        return loss_of_signal || degradation_of_signal || loss_of_tracking ||
               velocity_overflow || phase_error || parity_error || configuration_parity_error;
    }
};

/**
 * @brief Комплексний результат зчитування з резольвера у фізичних та сирих одиницях.
 */
struct ResolverData {
    double position_degrees{0.0};      ///< Кут повороту у градусах [0..360)
    double position_radians{0.0};      ///< Кут повороту у радіанах [0..2π)
    double velocity_rad_per_sec{0.0};  ///< Кутова швидкість у рад/с
    double velocity_rpm{0.0};          ///< Кутова швидкість в обертах за хвилину (RPM)
    std::uint16_t raw_position{0};     ///< Сирий 16-бітний код кута з AD2S1210
    std::int16_t raw_velocity{0};      ///< Сирий 16-бітний код швидкості (знаковий)
    bool is_valid{false};              ///< Ознака коректності даних
    FaultStatus fault{};               ///< Стан діагностичних прапорців
};

/**
 * @brief Структура конфігураційних параметрів драйвера AD2S1210.
 */
struct Config {
    Resolution resolution{Resolution::Res16Bit};
    std::uint32_t clk_in_hz{8192000};          ///< Частота системного тактування CLKIN (за замовчуванням 8.192 МГц)
    std::uint32_t excitation_freq_hz{10000};  ///< Частота збудження резольвера (10 кГц)
    std::uint8_t los_threshold{0x20};          ///< Поріг втрати сигналу (LOS Threshold Register 0x84)
    std::uint8_t dos_overrange_threshold{0x7F};///< Поріг переповнення DOS (Register 0x85)
    std::uint8_t dos_mismatch_threshold{0x28}; ///< Поріг неузгодженості DOS (Register 0x86)
    std::uint8_t lot_high_threshold{0x0A};     ///< Верхній поріг втрати стеження LOT (Register 0x87)
    std::uint8_t lot_low_threshold{0x05};      ///< Нижній поріг втрати стеження LOT (Register 0x88)
    bool hysteresis_enable{true};              ///< Включення гістерезису для усунення тремтіння
    bool phase_lock_enable{true};              ///< Включення фазового автопідстроювання
};

/**
 * @brief Основний C++ клас-драйвер для перетворювача «резольвер-цифра» AD2S1210.
 */
class Ad2s1210Driver {
public:
    /**
     * @brief Конструктор драйвера.
     * @param spi Посилання на апаратний SPI-драйвер.
     * @param gpio Посилання на апаратний GPIO-драйвер.
     */
    Ad2s1210Driver(ISpiDriver& spi, ISpiGpio& gpio);

    /**
     * @brief Ініціалізація мікросхеми та застосування конфігурації.
     * @param config Структура налаштувань.
     * @return true у разі успішної конфігурації та відсутності апаратних помилок.
     */
    bool init(const Config& config);

    /**
     * @brief Апаратне скидання мікросхеми імпульсом на лінії RESET.
     */
    void reset_hardware();

    /**
     * @brief Перемикання режиму роботи через маніпуляцію лініями A0 та A1.
     * @param mode Бажаний режим (Position, Velocity, Configuration).
     */
    void set_mode(Mode mode);

    /**
     * @brief Отримати поточний встановлений режим.
     */
    [[nodiscard]] Mode get_current_mode() const noexcept { return current_mode_; }

    /**
     * @brief Запис значення у внутрішній регістр AD2S1210 (потрібен режим Configuration).
     * @param reg_addr Адреса регістра.
     * @param data Байт даних.
     * @return true у разі успішного запису.
     */
    bool write_register(std::uint8_t reg_addr, std::uint8_t data);

    /**
     * @brief Зчитування значення з внутрішнього регістра AD2S1210.
     * @param reg_addr Адреса регістра.
     * @return Прочитаний байт або std::nullopt у разі збою SPI.
     */
    std::optional<std::uint8_t> read_register(std::uint8_t reg_addr);

    /**
     * @brief Налаштування роздільної здатності у Control Register.
     */
    bool set_resolution(Resolution res);

    /**
     * @brief Налаштування частоти генератора збудження (EXC Frequency Register 0x89).
     */
    bool set_excitation_frequency(std::uint32_t freq_hz, std::uint32_t clk_hz);

    /**
     * @brief Стробування імпульсом SAMPLE для фіксації поточних відліків кута та швидкості.
     */
    void sample_strobe();

    /**
     * @brief Зчитування сирого 16-бітного коду кутового положення в режимі Position.
     */
    std::optional<std::uint16_t> read_raw_position();

    /**
     * @brief Зчитування сирого 16-бітного знакового коду кутової швидкості в режимі Velocity.
     */
    std::optional<std::int16_t> read_raw_velocity();

    /**
     * @brief Комплексне зчитування кута, швидкості та діагностичного статусу.
     * @return Структура ResolverData з обчисленими фізичними величинами.
     */
    std::optional<ResolverData> read_resolver_data();

    /**
     * @brief Зчитування та дешифрування регістра помилок Fault Register (0xFF).
     */
    FaultStatus read_fault_register();

    // Математичні функції перетворення сирих кодувань у фізичні одиниці

    /**
     * @brief Перетворення сирого відліку кута в градуси [0..360).
     */
    static double raw_to_degrees(std::uint16_t raw_pos, Resolution res) noexcept;

    /**
     * @brief Перетворення сирого відліку кута в радіани [0..2π).
     */
    static double raw_to_radians(std::uint16_t raw_pos, Resolution res) noexcept;

    /**
     * @brief Перетворення сирого відліку швидкості в оберти за хвилину (RPM).
     */
    static double raw_to_rpm(std::int16_t raw_vel, Resolution res, std::uint32_t clk_hz) noexcept;

    /**
     * @brief Перетворення сирого відліку швидкості в радіани за секунду (rad/s).
     */
    static double raw_to_rad_per_sec(std::int16_t raw_vel, Resolution res, std::uint32_t clk_hz) noexcept;

private:
    ISpiDriver& spi_;
    ISpiGpio& gpio_;
    Config config_{};
    Mode current_mode_{Mode::Position};

    /// Отримання максимальної швидкості в об/хв для заданої роздільної здатності та тактової частоти
    static double get_max_rpm_for_resolution(Resolution res, std::uint32_t clk_hz) noexcept;

    /// Розрахунок значення регістра частоти збудження (0x89)
    static std::uint8_t calculate_excitation_val(std::uint32_t freq_hz, std::uint32_t clk_hz) noexcept;
};

} // namespace resolver
