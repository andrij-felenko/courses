#include <Arduino.h>

struct HBridgeGates {
    bool q1_pChannel;
    bool q2_nChannel;
    bool q3_pChannel;
    bool q4_nChannel;
};

class HBridgeController {
public:
    static HBridgeGates computeGates(ServoDirection dir) {
        HBridgeGates gates = {false, false, false, false};

        switch (dir) {
            case ServoDirection::Clockwise:
                gates.q1_pChannel = true;
                gates.q4_nChannel = true;
                break;
            case ServoDirection::CounterClockwise:
                gates.q3_pChannel = true;
                gates.q2_nChannel = true;
                break;
            case ServoDirection::Stop:
            default:
                // Усі ключі закриті
                break;
        }
        return gates;
    }
};
