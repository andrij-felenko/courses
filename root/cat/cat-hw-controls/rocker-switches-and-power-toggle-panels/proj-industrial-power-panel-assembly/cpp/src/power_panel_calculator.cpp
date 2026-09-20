#include "../include/power_panel_calculator.hpp"
#include <iostream>
#include <iomanip>
#include <cmath>

namespace PowerPanel {

PowerPanelCalculator::PowerPanelCalculator(PowerCircuitConfig config)
    : m_config(std::move(config)) {}

void PowerPanelCalculator::setConfig(const PowerCircuitConfig& config) {
    m_config = config;
}

const PowerCircuitConfig& PowerPanelCalculator::getConfig() const {
    return m_config;
}

double PowerPanelCalculator::calculateWireResistance() const {
    if (m_config.wireSectionMm2 <= 0.0 || m_config.wireLengthM < 0.0) {
        return 0.0;
    }
    /* R = rho * L / S */
    return (m_config.wireResistivityOhmMm2M * m_config.wireLengthM) / m_config.wireSectionMm2;
}

double PowerPanelCalculator::calculateVoltageDrop() const {
    double rWire = calculateWireResistance();
    /* U_drop = I * R */
    return m_config.currentA * rWire;
}

double PowerPanelCalculator::calculateContactPowerLoss() const {
    /* P = I^2 * R_contact (переведення мОм в Ом) */
    double rContactOhm = m_config.switchContactResistanceMohm / 1000.0;
    return m_config.currentA * m_config.currentA * rContactOhm;
}

double PowerPanelCalculator::calculateTemperatureRise() const {
    double pLoss = calculateContactPowerLoss();
    /* Delta_T = P_loss * R_th */
    return pLoss * m_config.switchThermalResistanceCw;
}

double PowerPanelCalculator::findRecommendedWireSection(double maxCurrentDensity) const {
    if (m_config.currentA <= 0.0 || maxCurrentDensity <= 0.0) {
        return STANDARD_WIRE_SECTIONS.front();
    }

    /* 1. Обчислення за граничною густиною струму: S_min = I / J_max */
    double minSectionDensity = m_config.currentA / maxCurrentDensity;

    /* 2. Обчислення за допустимим спадом напруги: U_allowed = V * pct / 100, S_min = rho * L * I / U_allowed */
    double maxDropV = m_config.voltageV * (m_config.maxAllowedVoltageDropPercent / 100.0);
    double minSectionDrop = 0.0;
    if (maxDropV > 0.0) {
        minSectionDrop = (m_config.wireResistivityOhmMm2M * m_config.wireLengthM * m_config.currentA) / maxDropV;
    }

    double minRequired = std::max(minSectionDensity, minSectionDrop);

    /* Пошук найменшого перерізу зі стандартного ряду, що є >= minRequired */
    for (double section : STANDARD_WIRE_SECTIONS) {
        if (section >= minRequired) {
            return section;
        }
    }

    return STANDARD_WIRE_SECTIONS.back();
}

CalculationResult PowerPanelCalculator::analyze() const {
    CalculationResult res{};

    res.wireResistanceOhm = calculateWireResistance();
    res.voltageDropV = calculateVoltageDrop();

    if (m_config.voltageV > 0.0) {
        res.voltageDropPercent = (res.voltageDropV / m_config.voltageV) * 100.0;
    }

    res.contactPowerLossW = calculateContactPowerLoss();
    res.wirePowerLossW = m_config.currentA * m_config.currentA * res.wireResistanceOhm;

    res.temperatureRiseC = calculateTemperatureRise();
    res.finalTemperatureC = m_config.ambientTempC + res.temperatureRiseC;

    res.currentDensityAMm2 = (m_config.wireSectionMm2 > 0.0) 
        ? (m_config.currentA / m_config.wireSectionMm2) : 0.0;

    res.recommendedSectionMm2 = findRecommendedWireSection();

    /* Перевірка критеріїв безпеки */
    res.isVoltageDropSafe = (res.voltageDropPercent <= m_config.maxAllowedVoltageDropPercent);
    res.isThermalSafe = (res.finalTemperatureC <= m_config.maxAllowedTempC);
    res.isCurrentDensitySafe = (res.currentDensityAMm2 <= 5.0);

    res.isOverallSafe = res.isVoltageDropSafe && res.isThermalSafe && res.isCurrentDensitySafe;

    return res;
}

void PowerPanelCalculator::printReport(const CalculationResult& res) const {
    std::cout << "=================================================================\n";
    std::cout << "      ОЦІНКА ТЕПЛОВОГО ТА ЕЛЕКТРИЧНОГО РЕЖИМУ СИЛОВОЇ ПАНЕЛІ      \n";
    std::cout << "=================================================================\n";
    std::cout << " Конфігурація кола:\n";
    std::cout << "  - Напруга живлення:                  " << m_config.voltageV << " В\n";
    std::cout << "  - Струм навантаження:                " << m_config.currentA << " А\n";
    std::cout << "  - Довжина кабельної лінії:          " << m_config.wireLengthM << " м\n";
    std::cout << "  - Переріз жила:                     " << m_config.wireSectionMm2 << " мм²\n";
    std::cout << "  - Перехідний опір контактів рокера: " << m_config.switchContactResistanceMohm << " мОм\n";
    std::cout << "  - Температура довкілля:             " << m_config.ambientTempC << " °C\n";
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << " Електричні параметри та втрати:\n";
    std::cout << "  - Опір провідників лінії:            " << std::fixed << std::setprecision(4) 
              << res.wireResistanceOhm << " Ом\n";
    std::cout << "  - Падіння напруги на лінії:          " << std::setprecision(2) 
              << res.voltageDropV << " В (" << res.voltageDropPercent << "%)\n";
    std::cout << "  - Густина струму в жилі:             " << res.currentDensityAMm2 << " А/мм²\n";
    std::cout << "  - Теплові втрати в провіднику:       " << res.wirePowerLossW << " Вт\n";
    std::cout << "  - Теплові втрати на контактах:       " << res.contactPowerLossW << " Вт\n";
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << " Тепловий баланс рокерного перемикача:\n";
    std::cout << "  - Перегрів корпусу (Delta T):        " << res.temperatureRiseC << " °C\n";
    std::cout << "  - Стаціонарна температура корпусу:  " << res.finalTemperatureC << " °C (макс: " 
              << m_config.maxAllowedTempC << " °C)\n";
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << " Рекомендації та статус безпеки:\n";
    std::cout << "  - Мінімальний рекомендований переріз:" << res.recommendedSectionMm2 << " мм²\n";
    std::cout << "  - Статус спаду напруги:              " 
              << (res.isVoltageDropSafe ? "[OK] (у межах норми)" : "[ПОМИЛКА] (ПЕРЕВИЩЕНО МЕЖУ!)") << "\n";
    std::cout << "  - Статус густини струму:             " 
              << (res.isCurrentDensitySafe ? "[OK] (достатній переріз)" : "[ПОМИЛКА] (ПЕРЕГРІВ ЖИЛИ!)") << "\n";
    std::cout << "  - Статус температури рокера:        " 
              << (res.isThermalSafe ? "[OK] (норми дотримано)" : "[ПОМИЛКА] (НЕБЕЗПЕКА ОПЛАВЛЕННЯ!)") << "\n";
    std::cout << "=================================================================\n\n";
}

} // namespace PowerPanel
