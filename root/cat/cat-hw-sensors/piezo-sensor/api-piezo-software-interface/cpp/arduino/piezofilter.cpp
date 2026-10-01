class PiezoFilter {
private:
    uint16_t _threshold_delta;
    uint32_t _blanking_ms;
    uint32_t _last_trigger_time;

public:
    PiezoFilter() : _threshold_delta(200), _blanking_ms(40), _last_trigger_time(0) {}

    void setThresholdDelta(uint16_t delta) {
        _threshold_delta = delta;
    }

    void setBlankingTime(uint32_t ms) {
        _blanking_ms = ms;
    }

    bool checkTrigger(uint16_t raw_val, uint16_t baseline, uint32_t current_ms) {
        if ((current_ms - _last_trigger_time) < _blanking_ms) {
            return false;
        }
        if (raw_val > (baseline + _threshold_delta)) {
            _last_trigger_time = current_ms;
            return true;
        }
        return false;
    }
};
