#ifndef CONTACTOR_TIMER_HPP
#define CONTACTOR_TIMER_HPP

#include <cstdint>

struct ContactorPinConfig {
    uint8_t coil_pin;
    uint8_t nc_feedback_pin;
};

class ContactorTimer {
public:
    ContactorTimer(ContactorPinConfig phase_a, ContactorPinConfig phase_b, uint32_t dead_time_ms);
    void begin();
    bool selectPhase(uint8_t target_phase);
    void update();
    uint8_t getActivePhase() const;

private:
    ContactorPinConfig phase_a_;
    ContactorPinConfig phase_b_;
    uint32_t dead_time_ms_;
    uint8_t active_phase_;
    uint8_t pending_phase_;
    uint32_t switch_timestamp_ms_;
    enum class State { IDLE, WAITING_RELEASE, DEAD_TIME, ENABLING };
    State state_;

    bool readNcState(uint8_t pin) const;
    void setCoilState(uint8_t pin, bool enabled);
    uint32_t getSystemMillis() const;
};

#endif // CONTACTOR_TIMER_HPP
