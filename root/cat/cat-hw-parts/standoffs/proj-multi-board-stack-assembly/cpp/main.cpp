#include "stack_calculator.hpp"
#include <iostream>

int main() {
    std::cout << "Запуск моделювання трирівневого приладового стека радіомодема...\n";

    StackAssemblyCalculator calculator;

    // Рівень 1 (Базова силова плата живлення з DC-DC та дроселями)
    PcbLayer power_board{
        .name = "Плата живлення 24В/5В",
        .pcb_thickness_mm = 1.6,
        .top_components_height_mm = 9.20, // Високі індуктивності та радіатори
        .bottom_components_height_mm = 0.0,
        .bottom_leads_protrusion_mm = 1.4,
        .max_deflection_mm = 0.20
    };
    calculator.setBaseBoard(power_board);

    // Стійки між рівнем 1 та рівнем 2:
    // Потрібна гальванічна розв'язка силового контуру -> Нейлон PA66 M3, висота 12.0 мм
    StandoffTierConfig tier1_config{
        .standoff_height_mm = 12.0,
        .thread = StandoffThread::M3,
        .material = StandoffMaterial::NylonPA66,
        .required_air_gap_mm = 1.0
    };

    // Рівень 2 (Центральний мікроконтролерний модуль MCU)
    PcbLayer mcu_board{
        .name = "Плата процесора MCU",
        .pcb_thickness_mm = 1.6,
        .top_components_height_mm = 4.50, // Штирьові роз'єми та кнопки
        .bottom_components_height_mm = 1.20,// SMD пасивні елементи знизу
        .bottom_leads_protrusion_mm = 0.50,
        .max_deflection_mm = 0.15
    };
    calculator.addStackedBoard(mcu_board, tier1_config);

    // Стійки між рівнем 2 та рівнем 3:
    // Потрібен суцільний замкнутий GND-контур екранування -> Латунь CW614N M3, висота 8.0 мм
    StandoffTierConfig tier2_config{
        .standoff_height_mm = 8.0,
        .thread = StandoffThread::M3,
        .material = StandoffMaterial::BrassCW614N,
        .required_air_gap_mm = 1.0
    };

    // Рівень 3 (Високочастотний трансивер та прецизійні датчики)
    PcbLayer rf_board{
        .name = "Плата RF трансивера",
        .pcb_thickness_mm = 1.6,
        .top_components_height_mm = 3.00,
        .bottom_components_height_mm = 1.00,
        .bottom_leads_protrusion_mm = 0.80,
        .max_deflection_mm = 0.15
    };
    calculator.addStackedBoard(rf_board, tier2_config);

    // Виконання розрахунку
    auto report = calculator.analyzeStack();
    calculator.printReport(report);

    // Перевірка монтажного крутного моменту для латунних та нейлонових стійок
    std::cout << "\nКонтроль монтажного моменту (перевірка збірки):\n";
    double test_m3_brass = 0.60;
    std::cout << " - Момент затягування латуні M3 (0.60 Н*м): " 
              << (StackAssemblyCalculator::isTorqueSafe(StandoffThread::M3, StandoffMaterial::BrassCW614N, test_m3_brass) 
                  ? "НОРМА" : "ПЕРЕВИЩЕННЯ МЕЖІ!") << "\n";

    double test_m3_nylon = 0.30;
    std::cout << " - Момент затягування нейлону M3 (0.30 Н*м): " 
              << (StackAssemblyCalculator::isTorqueSafe(StandoffThread::M3, StandoffMaterial::NylonPA66, test_m3_nylon) 
                  ? "НОРМА" : "КРИТИЧНО! РИЗИК ЗРИВУ РІЗЬБИ PA66") << "\n";

    return 0;
}
