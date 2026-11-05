#ifndef FASTENER_CALCULATOR_HPP
#define FASTENER_CALCULATOR_HPP

#include <string>
#include <string_view>
#include <stdexcept>
#include <cmath>

/**
 * @file FastenerCalculator.hpp
 * @brief Оголошення класу FastenerCalculator, перерахувань матеріалів MaterialGrade та режимів тертя LubricationCondition.
 */

/**
 * @brief Класи матеріалів та міцності кріпильних елементів.
 */
enum class MaterialGrade {
    Steel_8_8,         // Високоміцна конструкційна сталь (клас 8.8)
    Steel_10_9,        // Високоміцна легована сталь (клас 10.9)
    Steel_12_9,        // Високоміцна легована сталь (клас 12.9)
    Stainless_A2_70,   // Корозійностійка аустенітна сталь (A2-70)
    Stainless_A4_70,   // Кислотостійка аустенітна сталь (A4-70)
    Titanium_Grade5    // Титановий сплав (Ti-6Al-4V, Grade 5)
};

/**
 * @brief Умови змащення та трибологічні режими на різьбі й під головкою.
 */
enum class LubricationCondition {
    Dry,            // Сухе різьблення (високий ризик задирання, особливо для титану та нержавійки)
    LightlyOiled,   // Стандартне машинне мастило
    AntiSeize       // Протизадирне пастоподібне мастило (містить мідь, графіт або дисульфід молібдену)
};

/**
 * @brief Калькулятор параметрів нарізного з'єднання.
 * 
 * Здійснює розрахунок номінальної площі поперечного перерізу різьби (As), 
 * рекомендованого зусилля затягування (Fp), моменту затягування (T), 
 * пружних деформацій та аналізує ризик задирання різьби (galling).
 */
class FastenerCalculator {
private:
    double nominalDiameter_;             // Номінальний діаметр різьби d (мм)
    double pitch_;                       // Крок різьби P (мм)
    MaterialGrade grade_;                // Матеріал та клас міцності
    LubricationCondition lubrication_;   // Умови змащення

    // Допоміжні методи для отримання механічних властивостей матеріалу
    double getYieldStrength() const;     // Межа плинності Rp0.2 або Re (МПа)
    double getTensileStrength() const;   // Межа міцності Rm (МПа)
    double getYoungModulus() const;      // Модуль пружності E (ГПа)
    double getFrictionCoefficient() const; // Коефіцієнт тертя в різьбі та під головкою

public:
    /**
     * @brief Конструктор калькулятора кріплення.
     * @param nominalDiameter Номінальний діаметр d в міліметрах (наприклад, 10.0 для M10).
     * @param pitch Крок різьби P в міліметрах (наприклад, 1.5 для основного кроку M10).
     * @param grade Клас міцності або марка матеріалу.
     * @param lubrication Умови змащення та наявність захисних паст.
     */
    FastenerCalculator(double nominalDiameter, double pitch, MaterialGrade grade, LubricationCondition lubrication);

    // Сетери та гетери
    void setNominalDiameter(double d);
    double getNominalDiameter() const;

    void setPitch(double p);
    double getPitch() const;

    void setMaterialGrade(MaterialGrade grade);
    MaterialGrade getMaterialGrade() const;

    void setLubrication(LubricationCondition lubrication);
    LubricationCondition getLubrication() const;

    /**
     * @brief Розрахунок розрахункової (напруженої) площі поперечного перерізу різьби As (мм²).
     * За стандартом ISO 898-1 / DIN 13.
     */
    double calculateStressArea() const;

    /**
     * @brief Розрахунок рекомендованого зусилля затягування Fp (Н).
     * Зазвичай приймається на рівні 75-90% від межі плинності для відповідного класу міцності.
     * @param utilizationFactor Коефіцієнт використання межі плинності (за замовчуванням 0.75).
     */
    double calculatePreload(double utilizationFactor = 0.75) const;

    /**
     * @brief Розрахунок необхідного моменту затягування T (Н·м).
     * Враховує геометрію різьби, зусилля затягування та коефіцієнт тертя у різьбі й під головкою гвинта.
     */
    double calculateTighteningTorque() const;

    /**
     * @brief Розрахунок пружного подовження болта ΔL (мм) на заданій довжині стику Lk (мм).
     * @param clampedLength Робоча довжина стержня болта (мм).
     */
    double calculateElongation(double clampedLength) const;

    /**
     * @brief Перевірка ризику задирання (galling) різьби.
     * Особливо критично для титану Grade 5 та нержавіючої сталі A2/A4 за умови сухого тертя.
     * @return Текстовий опис стану та рекомендації українською мовою.
     */
    std::string assessGallingRisk() const;

    /**
     * @brief Повертає текстову назву матеріалу українською мовою.
     */
    std::string_view getMaterialName() const;

    /**
     * @brief Повертає текстову назву умов змащення українською мовою.
     */
    std::string_view getLubricationName() const;
};

#endif // FASTENER_CALCULATOR_HPP
