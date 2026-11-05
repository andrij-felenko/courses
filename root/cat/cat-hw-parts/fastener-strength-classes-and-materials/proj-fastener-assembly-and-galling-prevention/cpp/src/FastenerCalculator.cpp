#include "FastenerCalculator.hpp"
#include <cmath>
#include <stdexcept>

/**
 * @file FastenerCalculator.cpp
 * @brief Реалізація методів класу FastenerCalculator: розрахунок площі As, зусилля затягування Fp, моменту T, деформацій та аналіз ризику задирання.
 */

FastenerCalculator::FastenerCalculator(double nominalDiameter, double pitch, MaterialGrade grade, LubricationCondition lubrication)
    : nominalDiameter_(nominalDiameter), pitch_(pitch), grade_(grade), lubrication_(lubrication) {
    if (nominalDiameter <= 0.0) {
        throw std::invalid_argument("Номінальний діаметр має бути додатним числом.");
    }
    if (pitch <= 0.0) {
        throw std::invalid_argument("Крок різьби має бути додатним числом.");
    }
}

void FastenerCalculator::setNominalDiameter(double d) {
    if (d <= 0.0) {
        throw std::invalid_argument("Номінальний діаметр має бути додатним числом.");
    }
    nominalDiameter_ = d;
}

double FastenerCalculator::getNominalDiameter() const {
    return nominalDiameter_;
}

void FastenerCalculator::setPitch(double p) {
    if (p <= 0.0) {
        throw std::invalid_argument("Крок різьби має бути додатним числом.");
    }
    pitch_ = p;
}

double FastenerCalculator::getPitch() const {
    return pitch_;
}

void FastenerCalculator::setMaterialGrade(MaterialGrade grade) {
    grade_ = grade;
}

MaterialGrade FastenerCalculator::getMaterialGrade() const {
    return grade_;
}

void FastenerCalculator::setLubrication(LubricationCondition lubrication) {
    lubrication_ = lubrication;
}

LubricationCondition FastenerCalculator::getLubrication() const {
    return lubrication_;
}

double FastenerCalculator::getYieldStrength() const {
    switch (grade_) {
        case MaterialGrade::Steel_8_8:
            return 640.0;  // МПа (0.8 * 800)
        case MaterialGrade::Steel_10_9:
            return 900.0;  // МПа (0.9 * 1000)
        case MaterialGrade::Steel_12_9:
            return 1080.0; // МПа (0.9 * 1200)
        case MaterialGrade::Stainless_A2_70:
        case MaterialGrade::Stainless_A4_70:
            return 450.0;  // МПа (умовна межа плинності для класу 70)
        case MaterialGrade::Titanium_Grade5:
            return 880.0;  // МПа (Ti-6Al-4V)
    }
    return 640.0;
}

double FastenerCalculator::getTensileStrength() const {
    switch (grade_) {
        case MaterialGrade::Steel_8_8:
            return 800.0;  // МПа
        case MaterialGrade::Steel_10_9:
            return 1000.0; // МПа
        case MaterialGrade::Steel_12_9:
            return 1200.0; // МПа
        case MaterialGrade::Stainless_A2_70:
        case MaterialGrade::Stainless_A4_70:
            return 700.0;  // МПа
        case MaterialGrade::Titanium_Grade5:
            return 950.0;  // МПа
    }
    return 800.0;
}

double FastenerCalculator::getYoungModulus() const {
    switch (grade_) {
        case MaterialGrade::Steel_8_8:
        case MaterialGrade::Steel_10_9:
        case MaterialGrade::Steel_12_9:
        case MaterialGrade::Stainless_A2_70:
        case MaterialGrade::Stainless_A4_70:
            return 210.0; // ГПа для сталей та нержавійки
        case MaterialGrade::Titanium_Grade5:
            return 113.5; // ГПа для титанового сплаву Grade 5
    }
    return 210.0;
}

double FastenerCalculator::getFrictionCoefficient() const {
    switch (lubrication_) {
        case LubricationCondition::Dry:
            if (grade_ == MaterialGrade::Titanium_Grade5) {
                return 0.55; // Титан має схильність до сильного сухого тертя та задирання
            }
            if (grade_ == MaterialGrade::Stainless_A2_70 || grade_ == MaterialGrade::Stainless_A4_70) {
                return 0.50; // Нержавіюча сталь схильна до холодне зварювання / задирання на сухому терті
            }
            return 0.40; // Суха сталь
        case LubricationCondition::LightlyOiled:
            return 0.14; // Стандартне машинне мастило
        case LubricationCondition::AntiSeize:
            return 0.09; // Протизадирне пастоподібне мастило (Anti-Seize)
    }
    return 0.14;
}

double FastenerCalculator::calculateStressArea() const {
    // Розрахунок площі напруженого перерізу As за емпіричною формулою ISO/DIN:
    // As = 0.7854 * (d - 0.9382 * P)^2
    double effectiveDiameter = nominalDiameter_ - 0.9382 * pitch_;
    return 0.7854 * effectiveDiameter * effectiveDiameter;
}

double FastenerCalculator::calculatePreload(double utilizationFactor) const {
    double As = calculateStressArea();
    double Rp02 = getYieldStrength();
    // Fp = As * Rp0.2 * v (де v — коефіцієнт використання плинності, зазвичай 0.75)
    return As * Rp02 * utilizationFactor;
}

double FastenerCalculator::calculateTighteningTorque() const {
    double Fp = calculatePreload(0.75);
    double mu = getFrictionCoefficient();
    
    // Середній діаметр різьби d2 = d - 0.6495 * P
    double d2 = nominalDiameter_ - 0.6495 * pitch_;
    // Середній діаметр опорної поверхні головки гвинта dw ≈ 1.5 * d
    double dw = 1.5 * nominalDiameter_;
    
    // Момент на різьбі: Tr = Fp * (p / (pi * d2) + mu / cos(alpha)) * (d2 / 2) -> з кутом профілю 60° (cos(30°) ≈ 0.866)
    double tanPsi = pitch_ / (M_PI * d2);
    double muV = mu / 0.866; // приведення тертя для трикутної різьби
    double Tr = Fp * (tanPsi + muV) * (d2 / 2.0);
    
    // Момент під головкою: Tb = Fp * mu * (dw / 3.0)
    double Tb = Fp * mu * (dw / 3.0);
    
    double T_total = Tr + Tb; // в Н·мм
    return T_total / 1000.0;  // переведення в Н·м
}

double FastenerCalculator::calculateElongation(double clampedLength) const {
    double Fp = calculatePreload(0.75);
    double As = calculateStressArea();
    double E_GPa = getYoungModulus();
    double E_MPa = E_GPa * 1000.0; // переведення ГПа в МПа (Н/мм²)
    
    // Закон Гука: ΔL = (Fp * Lk) / (As * E)
    return (Fp * clampedLength) / (As * E_MPa);
}

std::string FastenerCalculator::assessGallingRisk() const {
    if (lubrication_ == LubricationCondition::AntiSeize) {
        return "Низький ризик задирання. Застосування пасти Anti-Seize ефективно розділяє металеві поверхні та знижує коефіцієнт тертя.";
    }
    if (lubrication_ == LubricationCondition::LightlyOiled) {
        return "Помірний ризик. Мастило забезпечує базовий захист, проте слід контролювати швидкість затягування.";
    }
    
    // Сухе тертя
    if (grade_ == MaterialGrade::Titanium_Grade5) {
        return "КРИТИЧНИЙ РИЗИК ЗАДИРАННЯ! Титан (Grade 5) у сухих умовах має схильність до холодне зварювання та миттєвого задирання різьби. КАТЕГОРИЧНО рекомендується використовувати Anti-Seize мастило.";
    }
    if (grade_ == MaterialGrade::Stainless_A2_70 || grade_ == MaterialGrade::Stainless_A4_70) {
        return "ВИСОКИЙ РИЗИК ЗАДИРАННЯ! Аустенітні нержавіючі сталі (A2/A4) на сухому терті легко задирають різьбу через утворення мікрозварювань при високих питомих тисках. Потрібне мастило або зниження швидкості монтажу.";
    }
    
    return "Помірний ризик для вуглецевої сталі на сухому терті. Рекомендується легке змащування для стабілізації зусилля попереднього натягу.";
}

std::string_view FastenerCalculator::getMaterialName() const {
    switch (grade_) {
        case MaterialGrade::Steel_8_8: return "Сталь 8.8";
        case MaterialGrade::Steel_10_9: return "Сталь 10.9";
        case MaterialGrade::Steel_12_9: return "Сталь 12.9";
        case MaterialGrade::Stainless_A2_70: return "Нержавіюча сталь A2-70";
        case MaterialGrade::Stainless_A4_70: return "Нержавіюча сталь A4-70";
        case MaterialGrade::Titanium_Grade5: return "Титан Grade 5 (Ti-6Al-4V)";
    }
    return "Невідомий матеріал";
}

std::string_view FastenerCalculator::getLubricationName() const {
    switch (lubrication_) {
        case LubricationCondition::Dry: return "Сухе різьблення";
        case LubricationCondition::LightlyOiled: return "Злегка змащене (машинне мастило)";
        case LubricationCondition::AntiSeize: return "Протизадирне мастило (Anti-Seize)";
    }
    return "Невідомі умови змащення";
}
