#ifndef RELAY_CONTROLLER_H
#define RELAY_CONTROLLER_H

#include <Arduino.h>
#include <EEPROM.h>

/**
 * @brief Клас для керування силовим реле модуля ESP-01S та збереження його стану в EEPROM.
 * 
 * Особливості ESP-01S Relay Module:
 *  - Управління реле здійснюється через вивід GPIO0.
 *  - Більшість плат ESP-01S Relay v1.0/v4.0 мають активний низький рівень (Active LOW):
 *      - LOW (0)  -> реле увімкнено (ON)
 *      - HIGH (1) -> реле вимкнено (OFF)
 *  - Під час завантаження ESP8266 вивід GPIO0 мусить мати високий рівень (HIGH/pull-up), 
 *    інакше контролер перейде у режим прошивки (UART Download Mode).
 */
class RelayController {
public:
    // Структура конфігурації для збереження у EEPROM
    struct EEPROMData {
        uint8_t magic; // Магічний байт для перевірки ініціалізації (0xA5)
        uint8_t state; // Збережений стан: 1 — увімкнено, 0 — вимкнено
    };

    static constexpr uint8_t DEFAULT_RELAY_PIN = 0; // GPIO0 за замовчуванням для ESP-01S
    static constexpr uint8_t EEPROM_MAGIC = 0xA5;   // Маркер ініціалізованої пам'яті
    static constexpr size_t EEPROM_SIZE = 16;        // Виділений розмір EEPROM

    /**
     * @brief Конструктор контролера реле.
     * @param pin Номер GPIO виводу.
     * @param active_low Логіка керування (true — активний LOW, false — активний HIGH).
     */
    explicit RelayController(uint8_t pin = DEFAULT_RELAY_PIN, bool active_low = true)
        : pin_(pin), active_low_(active_low), state_(false), eeprom_address_(0) {}

    /**
     * @brief Ініціалізація GPIO та відновлення стану з EEPROM.
     * @param eeprom_addr Базова адреса в EEPROM.
     */
    void begin(int eeprom_addr = 0) {
        eeprom_address_ = eeprom_addr;

        // Ініціалізація EEPROM для ESP8266
        EEPROM.begin(EEPROM_SIZE);

        // Спочатку відновлюємо збережений стан із пам'яті
        state_ = loadStateFromEEPROM();

        // Спочатку виставляємо потрібний рівень на виводі, а потім переводимо в режим OUTPUT,
        // щоб запобігти короткочасному імпульсу або клацанню реле при старті
        applyPinState();
        pinMode(pin_, OUTPUT);
    }

    /**
     * @brief Зміна стану реле.
     * @param enable true — увімкнути реле, false — вимкнути.
     * @param save_to_eeprom Зберегти стан у EEPROM після зміни.
     */
    void setState(bool enable, bool save_to_eeprom = true) {
        if (state_ == enable) {
            return;
        }

        state_ = enable;
        applyPinState();

        if (save_to_eeprom) {
            saveStateToEEPROM(state_);
        }
    }

    /**
     * @brief Переключення стану реле.
     * @return Новий стан реле.
     */
    bool toggle() {
        setState(!state_, true);
        return state_;
    }

    /**
     * @brief Отримати поточний стан реле.
     * @return true, якщо реле увімкнене.
     */
    bool getState() const {
        return state_;
    }

private:
    uint8_t pin_;
    bool active_low_;
    bool state_;
    int eeprom_address_;

    /**
     * @brief Застосування логічного рівня на GPIO0 залежно від active_low_.
     */
    void applyPinState() {
        uint8_t level = active_low_ ? (state_ ? LOW : HIGH) : (state_ ? HIGH : LOW);
        digitalWrite(pin_, level);
    }

    /**
     * @brief Збереження стану в EEPROM та викликом commit().
     */
    void saveStateToEEPROM(bool state) {
        EEPROMData data;
        data.magic = EEPROM_MAGIC;
        data.state = state ? 1 : 0;

        EEPROM.put(eeprom_address_, data);
        EEPROM.commit();
    }

    /**
     * @brief Зчитування збереженого стану з EEPROM.
     */
    bool loadStateFromEEPROM() {
        EEPROMData data;
        EEPROM.get(eeprom_address_, data);

        if (data.magic == EEPROM_MAGIC) {
            return (data.state == 1);
        }

        // Якщо EEPROM чистий або містить невалідні дані — записуємо вимкнений стан
        saveStateToEEPROM(false);
        return false;
    }
};

#endif // RELAY_CONTROLLER_H
