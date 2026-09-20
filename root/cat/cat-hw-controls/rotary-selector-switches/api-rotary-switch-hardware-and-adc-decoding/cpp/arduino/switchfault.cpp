#include <Arduino.h>

enum class SwitchFault { None, ShortToGND, ShortToVCC, OpenCircuit };

struct SwitchState {
    uint8_t position;
    SwitchFault fault;
};

class DiagnosticRotaryDecoder {
private:
    const uint16_t adcMinLimit = 20;
    const uint16_t adcMaxLimit = 1000;
    uint8_t lastValidPos = 0;

public:
    SwitchState process(uint16_t adcRaw) {
        SwitchState state;
        state.position = lastValidPos;

        if (adcRaw < adcMinLimit) {
            state.fault = SwitchFault::ShortToGND;
        } else if (adcRaw > adcMaxLimit) {
            state.fault = SwitchFault::ShortToVCC;
        } else {
            state.fault = SwitchFault::None;
        }

        return state;
    }
};
