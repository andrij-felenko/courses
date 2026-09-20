#include "can_bus.hpp"
#include "can_damper_actuator_adapter.hpp"
#include "damper_domain.hpp"
#include "mock_can_bus_driver.hpp"

#include <cassert>
#include <iomanip>
#include <iostream>
#include <string_view>

// ============================================================================
// ДОПОМІЖНІ ФУНКЦІЇ ВІДОБРАЖЕННЯ ТА ВЕРИФІКАЦІЇ
// ============================================================================

/// @brief Форматований вивід шістнадцяткового дампу (hex-dump) кадру CAN.
void print_can_frame(const CanFrame& frame, std::string_view description) {
    std::cout << "\n[CAN FRAME] " << description << "\n";
    std::cout << "  Ідентифікатор (CAN ID): 0x" << std::hex << std::uppercase << frame.id
              << std::dec << " | Довжина (DLC): " << static_cast<int>(frame.dlc) << " байтів\n";
    std::cout << "  Корисне навантаження:   [ ";
    for (uint8_t byte : frame.data) {
        std::cout << std::hex << std::uppercase << std::setw(2) << std::setfill('0')
                  << static_cast<int>(byte) << " ";
    }
    std::cout << std::dec << "]\n";

    // Побайтова розшифровка сигналів згідно зі специфікацією DBC
    const uint8_t mode = frame.data[0] & 0x0F;
    const uint16_t angle_raw = static_cast<uint16_t>(frame.data[1]) |
                               (static_cast<uint16_t>(frame.data[2]) << 8);
    const double angle_deg = static_cast<double>(angle_raw) * can_dbc::kAngleScale;

    const uint16_t speed_raw = (static_cast<uint16_t>(frame.data[3]) << 8) |
                               static_cast<uint16_t>(frame.data[4]);
    const double speed_val = static_cast<double>(speed_raw) * can_dbc::kSpeedScale;

    const uint8_t counter = frame.data[6] & 0x0F;
    const uint8_t crc = frame.data[7];

    std::cout << "  Розшифровка полів DBC:\n";
    std::cout << "    - Byte 0:    Mode = 0x0" << static_cast<int>(mode) << "\n";
    std::cout << "    - Bytes 1-2: Target Angle (Little-Endian) = " << angle_deg
              << "° (raw: 0x" << std::hex << angle_raw << std::dec << " = " << angle_raw << ")\n";
    std::cout << "    - Bytes 3-4: Speed (Big-Endian)          = " << speed_val
              << " °/с (raw: 0x" << std::hex << speed_raw << std::dec << " = " << speed_raw << ")\n";
    std::cout << "    - Byte 6:    Rolling Counter             = " << static_cast<int>(counter) << "\n";
    std::cout << "    - Byte 7:    CRC-8 (SAE J1850)           = 0x" << std::hex << std::uppercase
              << std::setw(2) << std::setfill('0') << static_cast<int>(crc) << std::dec << "\n";
}

// ============================================================================
// ГОЛОВНИЙ ТЕСТОВИЙ СТЕНД ПРОГРАМИ
// ============================================================================

int main() {
    std::cout << "====================================================================\n";
    std::cout << " ДЕМОНСТРАЦІЯ ВИХІДНОГО АДАПТЕРА ДЛЯ АКТУАТОРА ЗАСЛІНКИ (CAN DBC)\n";
    std::cout << " Шаблон «Порти й адаптери»: чистий домен та низькорівневий протокол\n";
    std::cout << "====================================================================\n";

    // 1. Конфігурація: створення класу-шпигуна та зв'язування з адаптером
    MockCanBusDriver mock_bus_driver;
    CanDamperActuatorAdapter actuator_adapter(mock_bus_driver);

    // Доменне ядро спілкується з актуатором виключно через абстрактний вихідний порт!
    IDamperActuatorPort& actuator_port = actuator_adapter;

    // ------------------------------------------------------------------------
    // СЦЕНАРІЙ 1: Відправка штатної команди (кут 45.0°, Little-Endian vs Big-Endian)
    // ------------------------------------------------------------------------
    std::cout << "\n>>> СЦЕНАРІЙ 1: Штатна команда позиціонування (45.0°, швидкість 20.0°/с)\n";
    {
        const SetDamperCommand command{
            .target_angle = DamperAngle(45.0),
            .mode = DamperMode::normal(),
            .target_speed_deg_per_sec = 20.0
        };

        const auto result = actuator_port.send_command(command);
        assert(result.has_value() && "Команда повинна виконатися успішно!");
        assert(mock_bus_driver.frame_count() == 1 && "Має бути надіслано рівно 1 кадр");

        const CanFrame frame = mock_bus_driver.last_frame().value();
        print_can_frame(frame, "Команда позиціонування на кут 45.0°");

        // Верифікація правильного розміщення байтів за DBC
        assert(frame.id == 0x120 && "Ідентифікатор CAN має бути 0x120");
        assert(frame.data[0] == 0x01 && "Режим Normal кодується як 0x01");

        // 45.0° / 0.1 = 450 (0x01C2). Little-Endian: data[1] = 0xC2, data[2] = 0x01
        assert(frame.data[1] == 0xC2 && "Молодший байт кута (LSB)");
        assert(frame.data[2] == 0x01 && "Старший байт кута (MSB)");

        // 20.0 / 0.1 = 200 (0x00C8). Big-Endian: data[3] = 0x00, data[4] = 0xC8
        assert(frame.data[3] == 0x00 && "Старший байт швидкості (MSB)");
        assert(frame.data[4] == 0xC8 && "Молодший байт швидкості (LSB)");

        // Rolling counter для першого кадру дорівнює 0
        assert(frame.data[6] == 0x00 && "Rolling counter першого кадру має бути 0");

        // Верифікація розрахунку контрольної суми CRC-8
        std::span<const uint8_t, 7> data_slice(frame.data.data(), 7);
        const uint8_t expected_crc = Crc8Calculator::calculate(data_slice);
        assert(frame.data[7] == expected_crc && "Контрольна сума CRC-8 розрахована некоректно");

        std::cout << "  [✓] Успішно підтверджено: правильність Little-Endian, Big-Endian та CRC-8!\n";
    }

    // ------------------------------------------------------------------------
    // СЦЕНАРІЙ 2: Монотонний інкремент Rolling Counter (0 -> 1 -> 2)
    // ------------------------------------------------------------------------
    std::cout << "\n>>> СЦЕНАРІЙ 2: Перевірка послідовності 4-бітного лічильника rolling counter\n";
    {
        // Друга команда: кут 60.0°
        const SetDamperCommand cmd2{
            .target_angle = DamperAngle(60.0),
            .mode = DamperMode::normal(),
            .target_speed_deg_per_sec = 25.0
        };
        const auto res2 = actuator_port.send_command(cmd2);
        assert(res2.has_value());
        const CanFrame frame2 = mock_bus_driver.last_frame().value();
        print_can_frame(frame2, "Друга команда: кут 60.0° (counter = 1)");
        assert(frame2.data[6] == 0x01 && "Rolling counter має зрости до 1");

        // Третя команда: кут 75.0°
        const SetDamperCommand cmd3{
            .target_angle = DamperAngle(75.0),
            .mode = DamperMode::normal(),
            .target_speed_deg_per_sec = 10.0
        };
        const auto res3 = actuator_port.send_command(cmd3);
        assert(res3.has_value());
        const CanFrame frame3 = mock_bus_driver.last_frame().value();
        print_can_frame(frame3, "Третя команда: кут 75.0° (counter = 2)");
        assert(frame3.data[6] == 0x02 && "Rolling counter має зрости до 2");

        std::cout << "  [✓] Успішно підтверджено: монотонний інкремент лічильника послідовності!\n";
    }

    // ------------------------------------------------------------------------
    // СЦЕНАРІЙ 3: Граничні значення та безпека типів (Value Objects)
    // ------------------------------------------------------------------------
    std::cout << "\n>>> СЦЕНАРІЙ 3: Граничні значення, режим калібрування та захист від переповнення\n";
    {
        // Крайня точка: 0.0° (повне перекриття заслінки) у режимі калібрування
        const SetDamperCommand cal_cmd{
            .target_angle = DamperAngle(0.0),
            .mode = DamperMode::calibration(),
            .target_speed_deg_per_sec = 5.0
        };
        const auto res_cal = actuator_port.send_command(cal_cmd);
        assert(res_cal.has_value());
        const CanFrame frame_cal = mock_bus_driver.last_frame().value();
        print_can_frame(frame_cal, "Режим калібрування: кут 0.0°");
        assert(frame_cal.data[0] == 0x02 && "Режим Calibration кодується як 0x02");
        assert(frame_cal.data[1] == 0x00 && frame_cal.data[2] == 0x00 && "Raw-код кута 0.0° дорівнює 0");

        // Перевірка інваріанта Value Object: захист від від'ємного кута (-15.0°)
        const auto invalid_angle = DamperAngle::create(-15.0);
        assert(!invalid_angle.has_value() && "DamperAngle не повинен дозволяти від'ємні значення");
        std::cout << "  [✓] Value Object захистив від некоректного кута: "
                  << to_string(invalid_angle.error()) << "\n";

        // Безпечний конструктор насичує кути поза діапазоном [0°, 90°]
        const DamperAngle clamped_angle(120.0);
        assert(clamped_angle.degrees() == 90.0 && "Кут > 90° повинен насичуватися до 90.0° (clamping)");
        std::cout << "  [✓] Clamping arithmetic запобігла wrap-around переповненню: 120.0° -> "
                  << clamped_angle.degrees() << "°\n";
    }

    // ------------------------------------------------------------------------
    // СЦЕНАРІЙ 4: Емуляція апаратних відмов шини (Fault Injection)
    // ------------------------------------------------------------------------
    std::cout << "\n>>> СЦЕНАРІЙ 4: Симуляція апаратних збоїв шини CAN та трансляція помилок\n";
    {
        // 4.1. Емуляція переповнення буфера передачі контролера
        mock_bus_driver.simulate_failure(true, CanBusError::TxQueueFull);
        const SetDamperCommand fail_cmd{
            .target_angle = DamperAngle(30.0),
            .mode = DamperMode::normal()
        };

        const auto fail_result = actuator_port.send_command(fail_cmd);
        assert(!fail_result.has_value() && "Виклик порту повинен повернути помилку");
        assert(fail_result.error() == ActuatorError::DeviceOffline &&
               "Помилка TxQueueFull має мапитися у доменний DeviceOffline");
        std::cout << "  [✓] Апаратна відмова TxQueueFull успішно трансльована в: "
                  << to_string(fail_result.error()) << "\n";

        // 4.2. Емуляція аварійного відключення контролера шини (Bus-Off)
        mock_bus_driver.simulate_failure(true, CanBusError::BusOff);
        const auto bus_off_result = actuator_port.send_command(fail_cmd);
        assert(!bus_off_result.has_value());
        assert(bus_off_result.error() == ActuatorError::BusFailure &&
               "Помилка BusOff має мапитися у доменний BusFailure");
        std::cout << "  [✓] Апаратна відмова BusOff успішно трансльована в: "
                  << to_string(bus_off_result.error()) << "\n";

        // 4.3. Відновлення працездатності шини
        mock_bus_driver.simulate_failure(false);
        const auto recovered_result = actuator_port.send_command(fail_cmd);
        assert(recovered_result.has_value() && "Після відновлення шини команди повинні успішно проходити");
        std::cout << "  [✓] Після відновлення зв'язку актуатор повернувся до штатної роботи!\n";
    }

    std::cout << "\n====================================================================\n";
    std::cout << " ВСІ ТЕСТОВІ СЦЕНАРІЇ ТА АРХІТЕКТУРНІ ПЕРЕВІРКИ ПРОЙДЕНО УСПІШНО!   \n";
    std::cout << " Межа між чистим доменом та двійковим протоколом CAN збережена строго.\n";
    std::cout << "====================================================================\n";

    return 0;
}
