#include <Arduino.h>

class WaterFlowSensor {
public:
    enum ErrorCode {
        OK = 0,
        ERR_INVALID_ARG = -1,
        ERR_NOT_INITIALIZED = -2
    };

    WaterFlowSensor(uint8_t pin, float k_factor, uint32_t sample_period_ms = 1000)
        : _pin(pin), _k_factor(k_factor), _sample_period_ms(sample_period_ms),
          _pulse_count_isr(0), _current_flow_lmin(0.0f), _total_volume_liters(0.0),
          _last_calc_time(0), _is_initialized(false) {}

    ErrorCode begin() {
        if (_k_factor <= 0.0f || _sample_period_ms == 0) {
            return ERR_INVALID_ARG;
        }
        pinMode(_pin, INPUT_PULLUP);
        _instance = this;
        attachInterrupt(digitalPinToInterrupt(_pin), WaterFlowSensor::isr_router, RISING);
        _last_calc_time = millis();
        _is_initialized = true;
        return OK;
    }

    void update() {
        if (!_is_initialized) return;
        uint32_t now = millis();
        uint32_t dt_ms = now - _last_calc_time;
        if (dt_ms >= _sample_period_ms) {
            noInterrupts();
            uint32_t pulses = _pulse_count_isr;
            _pulse_count_isr = 0;
            interrupts();

            float dt_sec = (float)dt_ms / 1000.0f;
            float freq_hz = (float)pulses / dt_sec;
            _current_flow_lmin = freq_hz / _k_factor;
            _total_volume_liters += _current_flow_lmin * (dt_sec / 60.0f);
            _last_calc_time = now;
        }
    }

    float getFlowRateLmin() const { return _current_flow_lmin; }
    double getTotalVolumeLiters() const { return _total_volume_liters; }

private:
    static void IRAM_ATTR isr_router() {
        if (_instance) {
            _instance->_pulse_count_isr++;
        }
    }

    static WaterFlowSensor* _instance;
    uint8_t _pin;
    float _k_factor;
    uint32_t _sample_period_ms;
    volatile uint32_t _pulse_count_isr;
    float _current_flow_lmin;
    double _total_volume_liters;
    uint32_t _last_calc_time;
    bool _is_initialized;
};

WaterFlowSensor* WaterFlowSensor::_instance = nullptr;
