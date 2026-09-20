enum class FsmState {
    Released,
    Enabled,
    Panic,
    Fault
};

class EnablingFSM {
public:
    FsmState currentState = FsmState::Released;
    unsigned long syncStartTime = 0;
    bool syncPending = false;
    unsigned long discrepancyTimeout = 200; // мс

    FsmState process(bool chA, bool chB) {
        unsigned long now = millis();
        bool mismatch = (chA != chB);

        if (mismatch) {
            if (!syncPending) {
                syncPending = true;
                syncStartTime = now;
            } else if ((now - syncStartTime) >= discrepancyTimeout) {
                currentState = FsmState::Fault;
                return currentState;
            }
        } else {
            syncPending = false;
        }

        if (currentState == FsmState::Fault) {
            if (!chA && !chB) currentState = FsmState::Released;
            return currentState;
        }

        if (!chA && !chB) {
            currentState = FsmState::Released;
        } else if (chA && chB) {
            if (currentState != FsmState::Panic) {
                currentState = FsmState::Enabled;
            }
        }
        return currentState;
    }
};
