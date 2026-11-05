#ifndef COMPENSATION_TABLE_HPP
#define COMPENSATION_TABLE_HPP

#include "abbe_compensator.hpp"

#include <cstddef>
#include <iosfwd>
#include <string>
#include <string_view>
#include <vector>

/**
 * @brief Промислові формати експорту калібрувальної таблиці.
 */
enum class CncFormat {
    Csv,     // Табличний текстовий формат для аналітики та метрологічних звітів
    Fanuc,   // Формат параметрів компенсації кроку систем ЧПУ Fanuc (Pitch Error Compensation)
    Siemens  // Формат таблиць компенсації провисання та кроку SINUMERIK ($AN_CEC)
};

/**
 * @brief Клас для інкапсуляції сформованої калібрувальної сітки поправок похибки Аббе.
 *
 * Забезпечує перевірку цілісності сітки (монотонність координат, стабільність кроку),
 * швидку лінійну інтерполяцію коригувального зміщення в реальному часі для систем приводу,
 * розрахунок метрологічної статистики та форматований експорт у промислові стандарти.
 */
class CompensationTable {
public:
    /**
     * @brief Результат перевірки метрологічної сітки позиціонування.
     */
    struct ValidationResult {
        bool isValid{false};        // Сітка придатна для інтерполяції (монотонна, >=2 вузлів)
        bool isMonotonic{false};    // Координати строго монотонно зростають
        bool isUniformStep{false};  // Крок між вузлами є сталим у межах заданого допуску
        double nominalStepMm{0.0};  // Номінальний крок переміщення, мм
        std::string message;        // Інформаційне повідомлення або опис виявленої проблеми
    };

    /**
     * @brief Зведені метрологічні статистичні показники похибок уздовж осі.
     */
    struct Statistics {
        std::size_t pointCount{0};   // Кількість опорних вузлів
        double startPosMm{0.0};      // Початкова координата осі, мм
        double endPosMm{0.0};        // Кінцева координата осі, мм
        double minErrorMm{0.0};      // Мінімальна (найбільш від'ємна) похибка, мм
        double maxErrorMm{0.0};      // Максимальна похибка, мм
        double peakToPeakMm{0.0};    // Розмах похибки (Peak-to-Peak), мм
        double maxCorrectionMm{0.0}; // Максимальна за модулем поправка, мм
    };

    // Конструктори
    CompensationTable() = default;
    CompensationTable(std::vector<CompensationEntry> entries, const AbbeArm& arm);

    // Доступ до даних
    [[nodiscard]] const std::vector<CompensationEntry>& entries() const noexcept;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] const AbbeArm& arm() const noexcept;

    // Валідація калібрувальної сітки
    [[nodiscard]] ValidationResult validate(double stepTolerance = 1e-4) const;
    [[nodiscard]] bool isMonotonic() const noexcept;
    [[nodiscard]] bool isUniformStep(double stepTolerance = 1e-4, double* stepOut = nullptr) const noexcept;

    // Швидка інтерполяція в реальному часі
    [[nodiscard]] double interpolateCorrection(double position_x) const;
    [[nodiscard]] double interpolateError(double position_x) const;

    // Метрологічна статистика
    [[nodiscard]] Statistics statistics() const noexcept;

    // Потоковий експорт у промислових форматах
    void exportCsv(std::ostream& os) const;
    void exportFanuc(std::ostream& os, int startParam = 1000, std::string_view axisName = "X") const;
    void exportSiemens(std::ostream& os, int tableIndex = 1, std::string_view axisName = "X") const;
    void exportFormat(std::ostream& os, CncFormat format) const;

    // Збереження таблиці безпосередньо у файл
    bool saveToFile(std::string_view filePath, CncFormat format) const;

    // Форматоване виведення для консолі / журналювання
    friend std::ostream& operator<<(std::ostream& os, const CompensationTable& table);

private:
    std::vector<CompensationEntry> entries_;
    AbbeArm arm_{0.0, 0.0};
};

#endif // COMPENSATION_TABLE_HPP
