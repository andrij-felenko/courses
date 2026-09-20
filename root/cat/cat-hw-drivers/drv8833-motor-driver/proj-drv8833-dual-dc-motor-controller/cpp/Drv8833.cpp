#include "Drv8833.hpp"

#if defined(ARDUINO)
    #include <Arduino.h>
#else
    #include <iostream>
    #include <algorithm>

    #ifndef OUTPUT
        #define OUTPUT 1
    #endif
    #ifndef INPUT_PULLUP
        #define INPUT_PULLUP 2
    #endif
    #ifndef HIGH
        #define HIGH 1
    #endif
    #ifndef LOW
        #define LOW 0
    #endif

    static inline void pinMode(uint8_t pin, uint8_t mode) {
        (void)pin; (void)mode;
    }
    static inline void digitalWrite(uint8_t pin, uint8_t val) {
        (void)pin; (void)val;
    }
    static inline void analogWrite(uint8_t pin, int val) {
        (void)pin; (void)val;
    }
    static inline int digitalRead(uint8_t pin) {
        (void)pin;
        return HIGH;
    }
#endif

Drv8833::Drv8833(const Drv8833Config& config)
    : m_config(config) {
}

Drv8833::~Drv8833() {
    stopAll(false);
    disable();
}

void Drv8833::begin() {
    pinMode(m_config.ain1_pin, OUTPUT);
    pinMode(m_config.ain2_pin, OUTPUT);
    pinMode(m_config.bin1_pin, OUTPUT);
    pinMode(m_config.bin2_pin, OUTPUT);

    digitalWrite(m_config.ain1_pin, LOW);
    digitalWrite(m_config.ain2_pin, LOW);
    digitalWrite(m_config.bin1_pin, LOW);
    digitalWrite(m_config.bin2_pin, LOW);

    if (m_config.nsleep_pin >= 0) {
        pinMode(static_cast<uint8_t>(m_config.nsleep_pin), OUTPUT);
        enable();
    } else {
        m_enabled = true;
    }

    if (m_config.nfault_pin >= 0) {
        pinMode(static_cast<uint8_t>(m_config.nfault_pin), INPUT_PULLUP);
    }

    m_faultState = false;
    m_lastCommandTimeMs = 0;
}

void Drv8833::enable() {
    if (m_config.nsleep_pin >= 0) {
        digitalWrite(static_cast<uint8_t>(m_config.nsleep_pin), HIGH);
    }
    m_enabled = true;
}

void Drv8833::disable() {
    if (m_config.nsleep_pin >= 0) {
        digitalWrite(static_cast<uint8_t>(m_config.nsleep_pin), LOW);
    }
    m_enabled = false;
}

void Drv8833::setMotor(MotorChannel channel, MotorMode mode, uint8_t speed) {
    if (m_faultState || !m_enabled) {
        if (mode != MotorMode::Coast && mode != MotorMode::Brake) {
            return;
        }
    }

    if (channel == MotorChannel::ChannelA) {
        applyHBridge(m_config.ain1_pin, m_config.ain2_pin, mode, speed);
        m_modeA = mode;
        m_speedA = speed;
    } else {
        applyHBridge(m_config.bin1_pin, m_config.bin2_pin, mode, speed);
        m_modeB = mode;
        m_speedB = speed;
    }
}

void Drv8833::setSpeed(MotorChannel channel, int16_t speed) {
    if (speed > 0) {
        uint8_t pwmVal = static_cast<uint8_t>(speed > 255 ? 255 : speed);
        setMotor(channel, MotorMode::Forward, pwmVal);
    } else if (speed < 0) {
        int16_t absSpeed = -speed;
        uint8_t pwmVal = static_cast<uint8_t>(absSpeed > 255 ? 255 : absSpeed);
        setMotor(channel, MotorMode::Reverse, pwmVal);
    } else {
        stopMotor(channel, true);
    }
}

void Drv8833::stopMotor(MotorChannel channel, bool hardBrake) {
    MotorMode mode = hardBrake ? MotorMode::Brake : MotorMode::Coast;
    setMotor(channel, mode, 0);
}

void Drv8833::stopAll(bool hardBrake) {
    stopMotor(MotorChannel::ChannelA, hardBrake);
    stopMotor(MotorChannel::ChannelB, hardBrake);
}

bool Drv8833::hasFault() const {
    if (m_config.nfault_pin >= 0) {
        return (digitalRead(static_cast<uint8_t>(m_config.nfault_pin)) == LOW);
    }
    return false;
}

void Drv8833::resetFault() {
    m_faultState = false;
}

void Drv8833::update(uint32_t currentTimeMs) {
    if (hasFault()) {
        if (!m_faultState) {
            m_faultState = true;
            stopAll(false);
        }
        return;
    }

    bool isMovingA = (m_modeA == MotorMode::Forward || m_modeA == MotorMode::Reverse) && (m_speedA > 0);
    bool isMovingB = (m_modeB == MotorMode::Forward || m_modeB == MotorMode::Reverse) && (m_speedB > 0);

    if (isMovingA || isMovingB) {
        if (m_lastCommandTimeMs == 0) {
            m_lastCommandTimeMs = currentTimeMs;
        }

        if (m_config.timeout_ms > 0) {
            if ((currentTimeMs - m_lastCommandTimeMs) >= m_config.timeout_ms) {
                stopAll(true);
            }
        }
    } else {
        m_lastCommandTimeMs = currentTimeMs;
    }
}

void Drv8833::applyHBridge(uint8_t pin1, uint8_t pin2, MotorMode mode, uint8_t speed) {
    switch (mode) {
    case MotorMode::Forward:
        analogWrite(pin1, speed);
        digitalWrite(pin2, LOW);
        break;

    case MotorMode::Reverse:
        digitalWrite(pin1, LOW);
        analogWrite(pin2, speed);
        break;

    case MotorMode::Brake:
        digitalWrite(pin1, HIGH);
        digitalWrite(pin2, HIGH);
        break;

    case MotorMode::Coast:
    default:
        digitalWrite(pin1, LOW);
        digitalWrite(pin2, LOW);
        break;
    }
}
