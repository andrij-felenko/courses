#include "abbe_compensator.hpp"
#include "compensation_table.hpp"

#include <iomanip>
#include <iostream>
#include <vector>

int main() {
    std::cout << "======================================================================\n";
    std::cout << "  ЦИФРОВА КОМПЕНСАЦІЯ ПОХИБКИ АББЕ В ПРЕЦИЗІЙНИХ СИСТЕМАХ ПОЗИЦІОНУВАННЯ\n";
    std::cout << "======================================================================\n\n";

    // 1. Конфігурація кінематичної моделі верстата / КВМ
    // Поздовжня вісь переміщення: X
    // Геометричні зсуви робочої точки (кінця фрези / щупа) відносно оптичної вимірювальної шкали:
    // dy = 120.0 мм (бічний зсув уздовж осі Y)
    // dz = 250.0 мм (висота над напрямними вздовж осі Z)
    const AbbeArm machineArm{120.0, 250.0};
    AbbeCompensator compensator(machineArm, AngleUnit::Arcseconds);

    std::cout << "Параметри просторового плеча Аббе:\n";
    std::cout << "  - Горизонтальне плече (dy): " << machineArm.dy << " мм\n";
    std::cout << "  - Вертикальне плече (dz):   " << machineArm.dz << " мм\n";
    std::cout << "  - Одиниця замірів кутів:    " 
              << AbbeCompensator::angleUnitToString(compensator.angleUnit()) << " (кутові секунди)\n\n";

    // 2. Серія кутових вимірів лазерного інтерферометра або автоколіматора вздовж ходу 500 мм
    // Тангаж (pitch, поворот навколо Y) та рискання (yaw, поворот навколо Z)
    const std::vector<InterferometerSample> laserMeasurements = {
        {  0.0,  0.00,  0.00},
        { 50.0, +1.80, -0.90},
        {100.0, +3.50, -1.60},
        {150.0, +5.00, -2.20},
        {200.0, +5.80, -2.00},
        {250.0, +5.40, -0.80},
        {300.0, +4.10, +1.10},
        {350.0, +2.20, +2.50},
        {400.0, -0.40, +3.30},
        {450.0, -2.60, +3.70},
        {500.0, -4.50, +3.40}
    };

    compensator.addSamples(laserMeasurements);
    std::cout << "Завантажено " << compensator.sampleCount() << " метрологічних точок інтерферометра.\n\n";

    // 3. Формування таблиці цифрової компенсації
    CompensationTable compTable = compensator.generateTable();

    // 4. Перевірка цілісності калібрувальної сітки
    const auto validation = compTable.validate();
    std::cout << "Статус валідації калібрувальної сітки:\n";
    std::cout << "  - Придатна для ЧПУ: " << (validation.isValid ? "ТАК" : "НІ") << "\n";
    std::cout << "  - Строго монотонна: " << (validation.isMonotonic ? "ТАК" : "НІ") << "\n";
    std::cout << "  - Рівномірний крок: " << (validation.isUniformStep ? "ТАК" : "НІ") << "\n";
    std::cout << "  - Номінальний крок: " << validation.nominalStepMm << " мм\n";
    std::cout << "  - Повідомлення:     " << validation.message << "\n\n";

    // 5. Розрахунок метрологічних статистичних показників
    const auto stats = compTable.statistics();
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Метрологічна статистика похибок на довжині ходу "
              << stats.startPosMm << " .. " << stats.endPosMm << " мм:\n";
    std::cout << "  - Найбільша додатна похибка:     " << (stats.maxErrorMm * 1000.0) << " мкм\n";
    std::cout << "  - Найбільша від'ємна похибка:    " << (stats.minErrorMm * 1000.0) << " мкм\n";
    std::cout << "  - Розмах похибки (Peak-to-Peak): " << (stats.peakToPeakMm * 1000.0) << " мкм\n";
    std::cout << "  - Максимальна корекція осі:      " << (stats.maxCorrectionMm * 1000.0) << " мкм\n\n";

    // 6. Виведення таблиці калібрування в консоль
    std::cout << compTable << "\n";

    // 7. Тестування швидкої лінійної інтерполяції поправки в реальному часі для ЧПУ приводу
    std::cout << "Тестування інтерполятора поправок для довільних поточних координат:\n";
    const std::vector<double> testPositions = {
        -15.0,  // До початку діапазону (clamping)
         25.0,  // Між 0.0 та 50.0 мм
        175.5,  // Між 150.0 та 200.0 мм
        320.0,  // Між 300.0 та 350.0 мм
        485.0,  // Між 450.0 та 500.0 мм
        540.0   // За межами робочого ходу (clamping)
    };

    std::cout << "----------------------------------------------------------------------\n";
    std::cout << "   Позиція X [мм]   |   Інтерпольована похибка [мкм]   |  Поправка [мкм] \n";
    std::cout << "----------------------------------------------------------------------\n";
    for (double posX : testPositions) {
        const double errUm  = compTable.interpolateError(posX) * 1000.0;
        const double corrUm = compTable.interpolateCorrection(posX) * 1000.0;
        std::cout << "     " << std::setw(10) << std::setprecision(2) << posX << "     | "
                  << "            " << std::setw(10) << std::setprecision(3) << errUm << "          | "
                  << "  " << std::setw(10) << std::setprecision(3) << corrUm << "\n";
    }
    std::cout << "----------------------------------------------------------------------\n\n";

    // 8. Експорт у промислові формати (CSV, Fanuc Pitch Comp, Siemens SINUMERIK)
    const std::string csvPath = "abbe_compensation.csv";
    const std::string fanucPath = "fanuc_pitch_comp.nc";
    const std::string siemensPath = "siemens_cec_table.ini";

    if (compTable.saveToFile(csvPath, CncFormat::Csv)) {
        std::cout << "[УСПІХ] Збережено метрологічний звіт: " << csvPath << "\n";
    }
    if (compTable.saveToFile(fanucPath, CncFormat::Fanuc)) {
        std::cout << "[УСПІХ] Згенеровано таблицю компенсації Fanuc: " << fanucPath << "\n";
    }
    if (compTable.saveToFile(siemensPath, CncFormat::Siemens)) {
        std::cout << "[УСПІХ] Згенеровано профіль компенсації Siemens 840D: " << siemensPath << "\n";
    }

    std::cout << "\nДемонстрацію цифрової компенсації похибки Аббе успішно завершено.\n";
    return 0;
}
