#include "liquid_level_controller.hpp"
#include <algorithm>
#include <stdexcept>

LiquidLevelController::LiquidLevelController(const ControllerConfig& config,
                                               DigitalWriteFn dwFunc,
                                               AnalogReadFn arFunc,
                                               DelayUsFn delayUsFunc)
    : config_(config),
      filter_(config.filterWindowSize),
      digitalWrite_(dwFunc),
      analogRead_(arFunc),
      delayUs_(delayUsFunc),
      lastFilteredLevel_(0.0f),
      relayActive_(false),
      initialized_(false) {
    if (config_.thresholds.lowThreshold >= config_.thresholds.highThreshold) {
        throw std::invalid_argument("Нижній поріг має бути суворо меншим за верхній поріг!");
    }
}

void LiquidLevelController::begin() {
    // Встановлюємо початковий безпечний стан пінів збудження (OFF — зняття напруги)
    digitalWrite_(config_.pinExcitationA, false);
    digitalWrite_(config_.pinExcitationB, false);

    // Ініціалізуємо реле у вимкненому стані
    relayActive_ = false;
    setRelayOutput(false);

    filter_.reset();
    initialized_ = true;
}

float LiquidLevelController::readRawSensorExcited() {
    // -------------------------------------------------------------------------
    // ПРИНЦИП ЗАХИСТУ ВІД ЕЛЕКТРОЛІЗУ:
    // Постійний струм (DC), що протікає через занурені металеві електроди у воді,
    // викликає швидкий електроліз, окиснення контакту та руйнування давача.
    // Для запобігання цього напруга подається короткочасним прямокутним імпульсом
    // лише на момент зчитування, після чого полярність інвертується для розрядки
    // паразитної ємності рідини, а електроди знеструмлюються.
    // -------------------------------------------------------------------------

    // Фаза 1: Пряма полярність збудження (A = HIGH, B = LOW)
    digitalWrite_(config_.pinExcitationA, true);
    digitalWrite_(config_.pinExcitationB, false);

    // Коротка затримка для стабілізації фронту напруги та струму в рідкому середовищі
    delayUs_(config_.pulseDelayUs);

    // Зчитування аналогового значення при прямій полярності
    uint16_t rawForward = analogRead_(config_.pinAnalogRead);

    // Фаза 2: Інверсна полярність для нейтралізації гальванічного заряду (A = LOW, B = HIGH)
    digitalWrite_(config_.pinExcitationA, false);
    digitalWrite_(config_.pinExcitationB, true);
    delayUs_(config_.pulseDelayUs);

    // Зчитування аналогового значення при зворотній полярності
    uint16_t rawReverse = analogRead_(config_.pinAnalogRead);

    // Фаза 3: Повне знеструмлення електродів (A = LOW, B = LOW)
    digitalWrite_(config_.pinExcitationA, false);
    digitalWrite_(config_.pinExcitationB, false);

    // Обчислення усередненого значення виміряного прямокутного імпульсу
    float averageRaw = static_cast<float>(rawForward + rawReverse) / 2.0f;

    // Масштабування сирого 10-бітного ADC (0..1023) у відсотки (0..100%)
    float percentage = (averageRaw / 1023.0f) * 100.0f;
    return std::clamp(percentage, 0.0f, 100.0f);
}

void LiquidLevelController::updateRelayState(float currentLevel) {
    // -------------------------------------------------------------------------
    // ЛОГІКА ПОРОГОВОГО РЕГУЛЮВАННЯ З ГІСТЕРЕЗИСOM:
    // Гістерезис запобігає «деренчанню» (короткочасному повторюваному перемиканню)
    // силового реле та насоса при дрібних коливаннях поверхні рідини навколо порогу.
    // -------------------------------------------------------------------------

    if (config_.mode == ControlMode::Fill) {
        // Режим наповнення (Fill):
        // Якщо рівень впав нижче Low Threshold -> ВМИКАЄМО насос підкачування.
        // Якщо рівень піднявся вище High Threshold -> ВИМИКАЄМО насос.
        // У проміжку між Low та High стан реле НЕ ЗМІНЮЄТЬСЯ (зона гістерезису).
        if (currentLevel <= config_.thresholds.lowThreshold) {
            relayActive_ = true;
        } else if (currentLevel >= config_.thresholds.highThreshold) {
            relayActive_ = false;
        }
    } else if (config_.mode == ControlMode::Drain) {
        // Режим осушення (Drain):
        // Якщо рівень піднявся вище High Threshold -> ВМИКАЄМО дренажний насос.
        // Якщо рівень впав нижче Low Threshold -> ВИМИКАЄМО дренажний насос.
        // У проміжку стан реле залишається попереднім.
        if (currentLevel >= config_.thresholds.highThreshold) {
            relayActive_ = true;
        } else if (currentLevel <= config_.thresholds.lowThreshold) {
            relayActive_ = false;
        }
    }

    setRelayOutput(relayActive_);
}

void LiquidLevelController::setRelayOutput(bool active) {
    // Урахування активного рівня реле (Active Low чи Active High)
    bool pinLogicState = config_.activeLowRelay ? !active : active;
    digitalWrite_(config_.pinRelay, pinLogicState);
}

float LiquidLevelController::update() {
    if (!initialized_) {
        begin();
    }

    // 1. Отримання сирого вимірювання з генерацією прямокутного імпульсу
    filter_.addSample(readRawSensorExcited());
    lastFilteredLevel_ = filter_.getAverage();

    // 2. Оновлення стану виконаного реле за алгоритмом гістерезису
    updateRelayState(lastFilteredLevel_);

    return lastFilteredLevel_;
}

float LiquidLevelController::getFilteredLevel() const {
    return lastFilteredLevel_;
}

bool LiquidLevelController::isRelayActive() const {
    return relayActive_;
}

const ControllerConfig& LiquidLevelController::getConfig() const {
    return config_;
}

void LiquidLevelController::setThresholds(float low, float high) {
    if (low >= high) {
        throw std::invalid_argument("Нижній поріг має бути суворо меншим за верхній поріг!");
    }
    config_.thresholds.lowThreshold = low;
    config_.thresholds.highThreshold = high;
}

void LiquidLevelController::setControlMode(ControlMode mode) {
    config_.mode = mode;
}
