#include "blheli_esc.hpp"
#include <algorithm>
#include <iostream>

BLHeliESC::BLHeliESC(uint8_t pwm_pin, uint8_t adc_pin, float voltage_divider_ratio)
    : pwm_pin_(pwm_pin),
      adc_pin_(adc_pin),
      current_pulse_us_(MIN_PULSE_US),
      divider_ratio_(voltage_divider_ratio),
      is_calibrated_(false) {}

bool BLHeliESC::init() {
    // Налаштування апаратної периферії: ШІМ пін у режим виходу, АЦП у режим аналогового входу
    std::cout << "[ESC HW] Ініціалізація ШІМ на піні " << static_cast<int>(pwm_pin_) 
              << " та АЦП на піні " << static_cast<int>(adc_pin_) << std::endl;
    
    // Встановлюємо початковий безпечний сигнал (1000 мкс)
    hw_set_pwm_us(SAFE_PULSE_US);
    return true;
}

void BLHeliESC::calibrate() {
    std::cout << "\n=== СТАРТ АВТОКАЛІБРУВАННЯ BLHELI ESC ===" << std::endl;
    std::cout << "[ESC CALIB] Крок 1: Подача максимального газу (2000 мкс)..." << std::endl;
    std::cout << "[ESC CALIB] Подайте живлення на силову губу ESC протягом 2 секунд!" << std::endl;
    
    // 1. Подаємо максимальний імпульс газу для входу в режим калібрування ESC
    hw_set_pwm_us(MAX_PULSE_US);
    hw_delay_ms(2000); // Очікування звукового сигналу ESC (beep-beep) підтвердження макс. газу

    std::cout << "[ESC CALIB] Крок 2: Подача мінімального газу (1000 мкс)..." << std::endl;
    // 2. Опускаємо газ до мінімуму для збереження нижньої межі
    hw_set_pwm_us(MIN_PULSE_US);
    hw_delay_ms(2000); // Очікування фінального звукового сигналу армінгу ESC

    is_calibrated_ = true;
    current_pulse_us_ = MIN_PULSE_US;
    std::cout << "[ESC CALIB] Автокалібрування завершено успішно. ESC готовий до роботи!\n" << std::endl;
}

void BLHeliESC::setThrottlePercent(float percent) {
    // Обмеження вхідного значення у діапазоні 0.0% .. 100.0%
    float clamped_percent = std::clamp(percent, 0.0f, 100.0f);
    
    // Лінійна інтерполяція відсотка в тривалість імпульсу мікросекунд
    uint16_t pulse = static_cast<uint16_t>(MIN_PULSE_US + (clamped_percent / 100.0f) * (MAX_PULSE_US - MIN_PULSE_US));
    setPulseWidthUs(pulse);
}

void BLHeliESC::setPulseWidthUs(uint16_t pulse_us) {
    // Жорстке обмеження тривалості імпульсу в безпечних межах 1000..2000 мкс
    current_pulse_us_ = std::clamp(pulse_us, MIN_PULSE_US, MAX_PULSE_US);
    hw_set_pwm_us(current_pulse_us_);
}

uint16_t BLHeliESC::getPulseWidthUs() const {
    return current_pulse_us_;
}

float BLHeliESC::readBECVoltage() {
    uint16_t raw_adc = hw_read_adc_raw();
    
    // Перетворення цифрового значення АЦП у напругу на піні МК
    float pin_voltage = (static_cast<float>(raw_adc) / ADC_MAX_RAW) * ADC_REF_VOLTAGE;
    
    // Обчислення реальної напруги лінії BEC з урахуванням дільника
    float bec_voltage = pin_voltage * divider_ratio_;
    return bec_voltage;
}

bool BLHeliESC::isBECVoltageSafe() {
    float v_bec = readBECVoltage();
    return (v_bec >= BEC_SAFE_VOLTAGE_MIN);
}

void BLHeliESC::emergencyStop() {
    std::cout << "[ESC ALARM] АВАРІЙНА ЗУПИНКА! Скидання імпульсу на 1000 мкс!" << std::endl;
    current_pulse_us_ = SAFE_PULSE_US;
    hw_set_pwm_us(SAFE_PULSE_US);
}

bool BLHeliESC::isCalibrated() const {
    return is_calibrated_;
}

// Реалізація низькорівневих апаратних залучень
void BLHeliESC::hw_set_pwm_us(uint16_t us) {
    current_pulse_us_ = us;
    // У реальному embedded-коді тут проводиться запис у регістр порівняння таймера (TIMx->CCRx)
    // або виклику функції типу analogWriteMicroseconds()
}

uint16_t BLHeliESC::hw_read_adc_raw() {
    // Симуляція зчитування АЦП. Повертає значення близько 5.0В BEC через дільник 2.0 (тобто ~2.5В на піні)
    // 2.5В / 3.3В * 4095 = ~3102 RAW
    static uint16_t simulated_raw = 3102; 
    return simulated_raw;
}

void BLHeliESC::hw_delay_ms(uint32_t ms) {
    // В системі реального часу виконується delay(ms) або очікування системного таймера
    (void)ms;
}
