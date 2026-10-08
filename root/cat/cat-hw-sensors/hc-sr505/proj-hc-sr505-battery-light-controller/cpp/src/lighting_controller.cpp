#include "lighting_controller.hpp"
#include "power_management.hpp"
#include <iostream>

LightingController::LightingController(PirSensor& sensor, PowerManager& power_mgr, uint8_t relay_pin, uint32_t hold_duration_ms)
    : sensor_(sensor),
      power_mgr_(power_mgr),
      relay_pin_(relay_pin),
      hold_duration_ms_(hold_duration_ms) {}

void LightingController::init() {
    setRelayState(false);
    current_state_ = ControllerState::Idle;
    std::cout << "[LightingController] Контролер освітлення ініціалізовано на pin "
              << static_cast<int>(relay_pin_) << ", затримка утримання: " << hold_duration_ms_ << " мс\n";
}

void LightingController::setRelayState(bool turn_on) {
    light_active_ = turn_on;
    std::cout << "[LightingController] Силовий ключ (Pin " << static_cast<int>(relay_pin_)
              << ") -> " << (turn_on ? "УВІМКНЕНО [СВІТЛО]" : "ВИМКНЕНО [ТЕМРЯВА]") << "\n";
}

void LightingController::update(uint32_t current_time_ms) {
    bool motion_active = sensor_.isMotionDetected();
    bool new_motion_event = sensor_.consumeMotionEvent();

    switch (current_state_) {
    case ControllerState::Idle:
        // Перехід у стан активного освітлення при фіксації руху
        if (new_motion_event || motion_active) {
            std::cout << "[LightingController] Подія: Виявлено рух! Перехід у стан LightOn.\n";
            setRelayState(true);
            last_motion_timestamp_ = current_time_ms;
            current_state_ = ControllerState::LightOn;
        }
        break;

    case ControllerState::LightOn:
        // Перезапуск таймера утримання, якщо рух продовжується
        if (new_motion_event || motion_active) {
            last_motion_timestamp_ = current_time_ms;
        }

        // Коли давач перестає фіксувати рух, переходимо до режиму відліку таймауту
        if (!motion_active) {
            current_state_ = ControllerState::Timeout;
        }
        break;

    case ControllerState::Timeout:
        // Якщо рух відновився до вичерпання таймауту — продовжуємо освітлення
        if (new_motion_event || motion_active) {
            std::cout << "[LightingController] Подія: Рух відновився під час таймауту. Перезапуск таймера.\n";
            last_motion_timestamp_ = current_time_ms;
            current_state_ = ControllerState::LightOn;
            break;
        }

        // Перевірка завершення неблокуючого софтверного таймера затримки
        if ((current_time_ms - last_motion_timestamp_) >= hold_duration_ms_) {
            std::cout << "[LightingController] Затримку " << hold_duration_ms_
                      << " мс вичерпано. Вимикаємо світло та готуємось до сну.\n";
            setRelayState(false);
            current_state_ = ControllerState::Sleep;
        }
        break;

    case ControllerState::Sleep:
        std::cout << "[LightingController] Ініціалізація переходу мікроконтролера в режим сну...\n";
        // Запит до модуля живлення для переведення МК в сон (Deep Sleep)
        power_mgr_.enterSleep();
        
        // Після відновлення роботи (пробудження від EXTI) повертаємося в стан Idle
        std::cout << "[LightingController] Систему пробуджено! Відновлення роботи контролера.\n";
        current_state_ = ControllerState::Idle;
        break;
    }
}
