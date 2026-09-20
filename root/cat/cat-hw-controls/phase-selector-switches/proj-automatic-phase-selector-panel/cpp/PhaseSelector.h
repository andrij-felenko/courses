#pragma once

#include <Arduino.h>

// Ідентифікатори фаз мережі
enum class PhaseId : uint8_t {
    NONE = 0,
    L1   = 1,
    L2   = 2,
    L3   = 3
};

// Стан машини керування перемикачем
enum class ControllerState : uint8_t {
    ALL_OFF,       // Усі реле вимкнені (аварія мережі)
    DEAD_TIME,     // Захисна часова пауза між вимкненням і увімкненням реле
    ACTIVE,        // Подача живлення від вибраної фази
    RETURN_DELAY   // Затримка повернення на пріоритетну фазу L1
};

// Конфігураційні параметри контролера перемикача фаз
struct PhaseConfig {
    // Аналогові входи вимірювання напруги фаз (0..1023)
    uint8_t pinVoltL1;
    uint8_t pinVoltL2;
    uint8_t pinVoltL3;

    // Цифрові виходи керування силовими реле/контакторами
    uint8_t pinRelayL1;
    uint8_t pinRelayL2;
    uint8_t pinRelayL3;

    // Коефіцієнт масштабування АЦП у Вольти RMS (наприклад, 0.4884 для 500В шкали)
    float voltageScaleFactor;

    // Порогові значення напруги (Вольти)
    float uMin;        // Мінімально припустима напруга (наприклад, 180.0 В)
    float uMax;        // Максимально припустима напруга (наприклад, 250.0 В)
    float uHysteresis; // Гістерезис повернення у норму (наприклад, 5.0 В)

    // Часові інтервали (мілісекунди)
    uint32_t deadTimeMs;    // Пауза гасіння дуги при зміні фази (наприклад, 500 мс)
    uint32_t returnDelayMs; // Затримка відновлення пріоритетної фази L1 (наприклад, 5000 мс)
};

class PhaseSelector {
public:
    explicit PhaseSelector(const PhaseConfig& config);
    ~PhaseSelector();

    // Ініціалізація GPIO-пінів
    void begin();

    // Неблокувальне оновлення стану (виклики у циклі loop)
    void update();

    // Поточна активна фаза, від якої живиться навантаження
    PhaseId getActivePhase() const;

    // Отримання виміряного значення напруги конкретної фази (В)
    float getVoltage(PhaseId phase) const;

    // Перевірка придатності фази для живлення
    bool isPhaseValid(PhaseId phase) const;

    // Поточний стан машини керування
    ControllerState getState() const;

private:
    void measureVoltages();
    PhaseId selectBestAvailablePhase() const;
    void setRelaysHardware(PhaseId activePhase);

    PhaseConfig m_config;
    
    float m_voltages[4]{0.0f, 0.0f, 0.0f, 0.0f};
    bool  m_phaseOk[4]{false, false, false, false};

    PhaseId m_activePhase{PhaseId::NONE};
    PhaseId m_targetPhase{PhaseId::NONE};
    ControllerState m_state{ControllerState::ALL_OFF};

    uint32_t m_stateTimer{0};
    uint32_t m_returnTimer{0};
};
