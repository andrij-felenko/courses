#include <iostream>
#include <iomanip>
#include "teach_pendant_controller.hpp"

// Допоміжна функція виводу текстового опису стану дозволу
const char* enabling_state_to_string(EnablingState state) {
    switch (state) {
        case EnablingState::Released: return "Вільний (Off)";
        case EnablingState::Enabled:  return "Дозволено (Enable)";
        case EnablingState::Panic:    return "Паніка (Panic Stop)";
    }
    return "Невідомо";
}

int main() {
    std::cout << "=== Система керування пультом налагодження Teach Pendant ===" << std::endl;

    TeachPendantController controller;

    // Реєстрація обробника подій зміни стану телеметрії
    controller.set_state_callback([](const PendantState& state) {
        std::cout << "[ТЕЛЕМЕТРІЯ] Час: " << state.timestamp_ms << " мс"
                  << " | Кнопка дозволу: " << enabling_state_to_string(state.enabling_switch)
                  << " | E-Stop: " << (state.estop_button == EmergencyState::Triggered ? "АКТИВОВАНО!" : "Норма")
                  << " | Джойстик X: " << state.joystick_axes[0]
                  << ", Y: " << state.joystick_axes[1] << std::endl;
    });

    // Реєстрація обробника подій тригеру аварійної зупинки
    controller.set_emergency_callback([](EmergencyState estop) {
        if (estop == EmergencyState::Triggered) {
            std::cout << "⚠️ [УВАГА] Натиснуто кнопковий аварійний стоп E-STOP! Силові приводи знеструмлено." << std::endl;
        } else {
            std::cout << "ℹ️ [ІНФО] Аварійну кнопку E-STOP деактивовано." << std::endl;
        }
    });

    // Симуляція покрокового розкладу роботи пульта налагодження
    std::array<int16_t, 6> axes_zero{0, 0, 0, 0, 0, 0};
    std::array<int16_t, 6> axes_moving{350, -120, 50, 0, 0, 0};

    std::cout << "\n--- Крок 1: Початковий стан (Пульт вільний) ---" << std::endl;
    controller.update(100, 0, 0, 1, axes_zero, 0x0000);

    std::cout << "\n--- Крок 2: Оператор натиснув кнопку дозволу до середини (Робочий режим) ---" << std::endl;
    controller.update(120, 1, 1, 1, axes_moving, 0x0001);

    std::cout << "\n--- Крок 3: Оператор в паніці стиснув кнопку дозволу до упору ---" << std::endl;
    controller.update(140, 1, 0, 1, axes_moving, 0x0001);

    std::cout << "\n--- Крок 4: Натискання грибка аварійної зупинки E-Stop ---" << std::endl;
    controller.update(160, 0, 0, 0, axes_zero, 0x0000);

    // Перевірка формування мережевого кадру та обчислення CRC16
    PendantPacket packet = controller.build_packet();
    std::cout << "\n--- Перевірка згенерованого кадру пакета ---" << std::endl;
    std::cout << "Заголовок кадру: 0x" << std::hex << static_cast<int>(packet.header) << std::dec << std::endl;
    std::cout << "Статус дозволу: " << static_cast<int>(packet.enabling_status) << std::endl;
    std::cout << "Розмір кадру: " << sizeof(PendantPacket) << " байт" << std::endl;
    std::cout << "Контрольна сума CRC16: 0x" << std::hex << std::setw(4) << std::setfill('0') 
              << packet.crc16 << std::dec << std::endl;

    // Валідація контрольної суми
    constexpr size_t data_len = sizeof(PendantPacket) - sizeof(uint16_t);
    uint16_t computed_crc = TeachPendantController::calculate_crc16(reinterpret_cast<const uint8_t*>(&packet), data_len);

    if (computed_crc == packet.crc16) {
        std::cout << "✅ Перевірка CRC16 пройшла успішно!" << std::endl;
    } else {
        std::cout << "❌ Помилка CRC16!" << std::endl;
    }

    return 0;
}
