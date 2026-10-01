#include <Arduino.h>

enum HostState { STATE_INIT, STATE_CONNECTING, STATE_IDLE, STATE_SENDING, STATE_RECONNECT };

class HostSocketFSM {
private:
    HostState state = STATE_INIT;
    unsigned long stateTimer = 0;
    unsigned long backoffMs = 1000;

public:
    void update(unsigned long nowMs, bool isClosed) {
        if (isClosed && state != STATE_RECONNECT) {
            state = STATE_RECONNECT;
            stateTimer = nowMs;
            return;
        }

        switch (state) {
            case STATE_INIT:
                Serial.print("AT+CIPMUX=1\r\n");
                state = STATE_CONNECTING;
                stateTimer = nowMs;
                break;

            case STATE_CONNECTING:
                if (nowMs - stateTimer > 10000) {
                    state = STATE_RECONNECT;
                    stateTimer = nowMs;
                }
                break;

            case STATE_RECONNECT:
                if (nowMs - stateTimer >= backoffMs) {
                    backoffMs = min(backoffMs * 2, 60000UL);
                    state = STATE_INIT;
                    stateTimer = nowMs;
                }
                break;

            default:
                break;
        }
    }
};
