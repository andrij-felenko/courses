#ifndef ABBE_COMPENSATOR_HPP
#define ABBE_COMPENSATOR_HPP

#include <cstddef>
#include <optional>
#include <string_view>
#include <vector>

// Попереднє оголошення класу CompensationTable для уникнення циклічної залежності
class CompensationTable;

/**
 * @brief Одиниці вимірювання кутових величин для даних лазерного інтерферометра чи автоколіматора.
 */
enum class AngleUnit {
    Arcseconds,   // Кутові секунди (arcsec, ")
    Microradians, // Мікрорадіани (µrad, urad)
    Milliradians, // Мілірадіани (mrad)
    Radians       // Радіани (rad)
};

/**
 * @brief Точні коефіцієнти переведення кутових одиниць у радіани.
 * 1 кутова секунда = π / (180 * 3600) рад ≈ 4.84813681109536e-6 рад.
 */
inline constexpr double ARCSEC_TO_RAD = 4.8481368110953599359e-6;
inline constexpr double URAD_TO_RAD   = 1.0e-6;
inline constexpr double MRAD_TO_RAD   = 1.0e-3;

/**
 * @brief Просторове плече Аббе (Abbe offset vector).
 *
 * Визначає просторове зміщення функціональної точки (кінця вимірювального щупа
 * координатно-вимірювальної машини або вершини різального інструмента верстата з ЧПУ)
 * відносно лінії вимірювання лінійного переміщення (оптичної шкали або енкодера).
 */
struct AbbeArm {
    double dy{0.0}; // Зміщення функціональної точки вздовж осі Y (горизонтальне плече), мм
    double dz{0.0}; // Зміщення функціональної точки вздовж осі Z (вертикальне плече), мм
};

/**
 * @brief Дискретний метрологічний замір лазерного інтерферометра в контрольній точці осі.
 */
struct InterferometerSample {
    double position_x{0.0}; // Номінальна координата каретки вздовж осі X, мм
    double pitch{0.0};      // Тангаж (кут повороту навколо осі Y) у робочих кутових одиницях
    double yaw{0.0};        // Рискання (кут повороту навколо осі Z) у робочих кутових одиницях
};

/**
 * @brief Розрахована точка цифрової компенсації похибки Аббе для координати X.
 */
struct CompensationEntry {
    double position_x{0.0};     // Номінальна координата осі X, мм
    double pitch_rad{0.0};      // Тангаж, нормалізований у радіани
    double yaw_rad{0.0};        // Рискання, нормалізоване у радіани
    double error_pitch_mm{0.0}; // Паразитне поздовжнє зміщення від тангажу (dz * pitch_rad), мм
    double error_yaw_mm{0.0};   // Паразитне поздовжнє зміщення від рискання (dy * yaw_rad), мм
    double total_error_mm{0.0}; // Сумарне лінійне зміщення першого порядку (похибка Аббе), мм
    double correction_mm{0.0};  // Компенсуюча поправка протилежного знака (-total_error_mm), мм
};

/**
 * @brief Клас для інкапсуляції параметрів просторового плеча Аббе, накопичення
 * замірів інтерферометра та виконання розрахунку лінійних поправок першого порядку.
 */
class AbbeCompensator {
public:
    // Конструктори
    AbbeCompensator() = default;
    explicit AbbeCompensator(const AbbeArm& arm, AngleUnit unit = AngleUnit::Arcseconds);
    AbbeCompensator(double dy_mm, double dz_mm, AngleUnit unit = AngleUnit::Arcseconds);

    // Геометрична конфігурація просторового плеча
    void setArm(const AbbeArm& arm) noexcept;
    void setArm(double dy_mm, double dz_mm) noexcept;
    [[nodiscard]] const AbbeArm& arm() const noexcept;

    // Керування одиницями вимірювання кутів
    void setAngleUnit(AngleUnit unit) noexcept;
    [[nodiscard]] AngleUnit angleUnit() const noexcept;

    // Додавання та накопичення метрологічних вибірок
    bool addSample(const InterferometerSample& sample);
    bool addSample(double position_x, double pitch, double yaw);
    std::size_t addSamples(const std::vector<InterferometerSample>& samples);
    void clearSamples() noexcept;

    [[nodiscard]] const std::vector<InterferometerSample>& samples() const noexcept;
    [[nodiscard]] std::size_t sampleCount() const noexcept;

    // Статичні математичні методи перетворення кутів
    [[nodiscard]] static double toRadians(double angle, AngleUnit unit) noexcept;
    [[nodiscard]] static std::optional<AngleUnit> parseAngleUnit(std::string_view str) noexcept;
    [[nodiscard]] static std::string_view angleUnitToString(AngleUnit unit) noexcept;

    // Розрахунок похибок і поправок для точки
    [[nodiscard]] CompensationEntry calculatePoint(const InterferometerSample& sample) const noexcept;
    [[nodiscard]] CompensationEntry calculatePoint(double position_x, double pitch, double yaw) const noexcept;

    // Генерація готової таблиці компенсації (потрібно #include "compensation_table.hpp")
    [[nodiscard]] CompensationTable generateTable() const;

private:
    AbbeArm arm_{0.0, 0.0};
    AngleUnit unit_{AngleUnit::Arcseconds};
    std::vector<InterferometerSample> samples_;
};

#endif // ABBE_COMPENSATOR_HPP
