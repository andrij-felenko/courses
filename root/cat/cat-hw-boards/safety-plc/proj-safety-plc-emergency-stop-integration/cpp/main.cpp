#include <iostream>
#include <iomanip>
#include "SafetyTypes.hpp"
#include "EdmMonitor.hpp"
#include "EStopBlock.hpp"

// Допоміжна функція виводу стану циклу контролера безпеки
void print_cycle_status(uint32_t cycle_num,
                        uint32_t time_ms,
                        const safety::EStopBlock& estop,
                        bool ch1,
                        bool ch2,
                        bool edm_nc,
                        bool reset) {
    std::cout << std::setw(6) << cycle_num << " | "
              << std::setw(6) << time_ms << " мс | "
              << (ch1 ? " 1 " : " 0 ") << " | "
              << (ch2 ? " 1 " : " 0 ") << " | "
              << (edm_nc ? " 1 " : " 0 ") << " | "
              << (reset ? " 1 " : " 0 ") << " | "
              << (estop.is_output_active() ? "  УВІМК (1) " : "  ВИМК  (0) ") << " | "
              << safety::to_string(estop.get_state()) << "\n";
}

int main() {
    std::cout << "========================================================================\n";
    std::cout << "   СИСТЕМА БЕЗПЕКИ SAFETY PLC: МОНІТОРИНГ E-STOP ТА EDM (ISO 13849-1)   \n";
    std::cout << "========================================================================\n\n";

    // Налаштування параметрів блоку безпеки
    safety::EStopConfig config;
    config.discrepancy_time_ms = 100; // Допустимий розкид затримки каналів = 100 мс
    config.require_manual_reset = true; // Вимога підтвердженого скидання
    config.edm_config.feedback_timeout_ms = 250; // Таймаут реле = 250 мс

    safety::EStopBlock estop(config);

    uint32_t cycle_counter = 0;
    uint32_t simulated_time_ms = 0;
    const uint32_t cycle_step_ms = 10; // Крок циклу PLC = 10 мс

    std::cout << "Цикл   | Час     | К1  | К2  | EDM | RST | Вихід безпеки | Стан автомата\n";
    std::cout << "-------+---------+-----+-----+-----+-----+---------------+-----------------------------------------\n";

    // Фізичні входи за замовчуванням: E-Stop не натиснуто (К1=1, К2=1), реле вимкнені (EDM NC=1)
    bool input_ch1 = true;
    bool input_ch2 = true;
    bool input_edm_nc = true;
    bool input_reset = false;

    // 1. Початковий стан — очікування скидання після подачі живлення
    for (int i = 0; i < 3; ++i) {
        cycle_counter++;
        simulated_time_ms += cycle_step_ms;
        estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
        print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);
    }

    // 2. Натискання кнопки Reset для активації безпечних виходів
    std::cout << "\n---> Натискання кнопки Reset (фронт 0 -> 1)\n";
    input_reset = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    // Звільнення кнопки Reset, реле замикаються (EDM NC стає 0, бо силовий вихід увімкнено)
    input_reset = false;
    input_edm_nc = false; // Силове реле спрацювало, його NC контакт розімкнувся
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    std::cout << "\n---> Нормальна робота об'єкта (Виходи увімкнені)\n";
    for (int i = 0; i < 2; ++i) {
        cycle_counter++;
        simulated_time_ms += cycle_step_ms;
        estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
        print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);
    }

    // 3. Аварійна зупинка E-Stop (одночасне розмикання двох каналів)
    std::cout << "\n---> Натискання кнопки E-Stop (К1=0, К2=0)\n";
    input_ch1 = false;
    input_ch2 = false;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    // Силові реле вимикаються -> EDM NC відновлюється в 1
    input_edm_nc = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    // 4. Відновлення грибка E-Stop та ручне скидання
    std::cout << "\n---> Повернення грибка E-Stop у вихідний стан (К1=1, К2=1)\n";
    input_ch1 = true;
    input_ch2 = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    std::cout << "---> Скидання аварії кнопкою Reset\n";
    input_reset = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    input_reset = false;
    input_edm_nc = false; // Реле увімкнулось
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    // 5. Симуляція помилки розбіжності каналів (Discrepancy Fault)
    std::cout << "\n---> Симуляція апаратного розриву Каналу 1 (К1=0, К2=1)\n";
    input_ch1 = false;
    input_ch2 = true;

    // Імітуємо перебіг часу, що перевищує discrepancy_time_ms (100 мс)
    for (int i = 0; i < 12; ++i) {
        cycle_counter++;
        simulated_time_ms += cycle_step_ms;
        estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
        if (i == 0 || i == 10 || estop.get_state() == safety::SafetyState::DiscrepancyFault) {
            print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);
            if (estop.get_state() == safety::SafetyState::DiscrepancyFault) break;
        }
    }

    // Реле знеструмлені через помилку
    input_edm_nc = true;

    std::cout << "---> Спроба скидання Reset при несправному Каналi 1 (К1=0) -> має бути відхилено\n";
    input_reset = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    std::cout << "---> Відновлення Каналу 1 (К1=1) та успішне скидання аварії\n";
    input_ch1 = true;
    input_reset = false;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);

    input_reset = true; // Фронт Reset
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    input_reset = false;
    input_edm_nc = false; // Реле увімкнено
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);

    // 6. Симуляція приварювання контактів силового реле (EDM Fault)
    std::cout << "\n---> Симуляція приварювання контактів реле (при E-Stop EDM NC залишається 0)\n";
    input_ch1 = false;
    input_ch2 = false;
    // УВАГА: Силовий вихід вимкнено, але через приварювання NC контакт НЕ замкнувся (input_edm_nc = false)

    for (int i = 0; i < 27; ++i) {
        cycle_counter++;
        simulated_time_ms += cycle_step_ms;
        estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
        if (i == 0 || estop.get_state() == safety::SafetyState::EdmFault) {
            print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);
            if (estop.get_state() == safety::SafetyState::EdmFault) {
                std::cout << "     Виявлено помилку EDM: " << safety::to_string(estop.get_edm_monitor().get_fault()) << "\n";
                break;
            }
        }
    }

    std::cout << "\n---> Заміна привареного реле (EDM NC відновлено в 1) та відновлення E-Stop (К1=1, К2=1)\n";
    input_edm_nc = true;
    input_ch1 = true;
    input_ch2 = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);

    std::cout << "---> Скидання помилки EDM натисканням кнопки Reset\n";
    input_reset = true;
    cycle_counter++;
    simulated_time_ms += cycle_step_ms;
    estop.update(input_ch1, input_ch2, input_edm_nc, input_reset, cycle_step_ms);
    print_cycle_status(cycle_counter, simulated_time_ms, estop, input_ch1, input_ch2, input_edm_nc, input_reset);

    std::cout << "\n========================================================================\n";
    std::cout << "                    ДЕМОНСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО                      \n";
    std::cout << "========================================================================\n";

    return 0;
}
