#ifndef ENCLOSURE_JOINT_CALCULATOR_HPP
#define ENCLOSURE_JOINT_CALCULATOR_HPP

#include <string>

/**
 * @brief Типізований перелік матеріалів конструкції кришки/корпусу.
 */
enum class MaterialType {
    Aluminum6061,
    Steel,
    Thermoplastic,
    Fr4
};

/**
 * @brief Типізований перелік класів міцності гвинтів з потайною головкою.
 */
enum class FastenerGrade {
    A2_70,
    Grade10_9,
    Grade12_9
};

/**
 * @brief Структура для збереження результатів розрахунку та звіту верифікації.
 */
struct VerificationReport {
    double plate_thickness;       // Загальна товщина пластини (мм)
    double h_k;                   // Глибина конуса зенкування (мм)
    double t_cyl;                 // Залишкова товщина стінки / пояска (мм)
    double contact_area;          // Площа контакту конічної головки (мм²)
    double T_tight;               // Допустимий момент затягування (Н·м)
    double contact_pressure;      // Контактний тиск у з'єднанні (МПа)
    bool knife_edge_warning;      // Прапорець ризику дефекту "knife-edge"
    std::string hex_strip_warning;// Попередження щодо шестигранника 2.0 мм
    bool is_passed;               // Загальний статус проходження верифікації
    MaterialType mat_type;
    FastenerGrade grade;
};

/**
 * @brief Клас для розрахунку геометрії зенкування 90°, верифікації товщини стінки
 *        на дефект knife-edge та аналізу міцності з'єднання М3 DIN 7991.
 */
class EnclosureJointCalculator {
public:
    EnclosureJointCalculator() = default;
    ~EnclosureJointCalculator() = default;

    /**
     * @brief Проводить розрахунок та генерує звіт верифікації з'єднання.
     * @param plate_thickness Товщина стінки/кришки (мм)
     * @param mat Матеріал корпусу
     * @param grade Клас міцності гвинта М3 DIN 7991
     * @return VerificationReport Звіт із результатами розрахунків
     */
    VerificationReport calculate(double plate_thickness, MaterialType mat, FastenerGrade grade) const;

    /**
     * @brief Виводить детальний звіт у стандартний потік виведення українською мовою.
     * @param report Структура звіту верифікації
     */
    void printReport(const VerificationReport& report) const;
};

#endif // ENCLOSURE_JOINT_CALCULATOR_HPP
