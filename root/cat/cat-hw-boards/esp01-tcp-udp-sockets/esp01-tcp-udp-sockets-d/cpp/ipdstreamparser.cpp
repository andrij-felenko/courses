// Приклад FSM-парсера заголовка +IPD на мові C++
#include <iostream>
#include <cstdint>

class IpdStreamParser {
public:
    enum class State {
        Idle,
        PrefixPlus,
        PrefixI,
        PrefixP,
        PrefixD,
        ReadSocketId,
        ReadPayloadLen,
        ReadPayloadData
    };

    IpdStreamParser() : currentState_(State::Idle), socketId_(0), payloadLen_(0), bytesRead_(0) {}

    void parseChar(char ch) {
        switch (currentState_) {
            case State::Idle:
                if (ch == '+') currentState_ = State::PrefixPlus;
                break;
            case State::PrefixPlus:
                currentState_ = (ch == 'I') ? State::PrefixI : State::Idle;
                break;
            case State::PrefixI:
                currentState_ = (ch == 'P') ? State::PrefixP : State::Idle;
                break;
            case State::PrefixP:
                currentState_ = (ch == 'D') ? State::PrefixD : State::Idle;
                break;
            case State::PrefixD:
                if (ch == ',') {
                    socketId_ = 0;
                    currentState_ = State::ReadSocketId;
                } else {
                    currentState_ = State::Idle;
                }
                break;
            case State::ReadSocketId:
                if (ch >= '0' && ch <= '9') {
                    socketId_ = ch - '0';
                } else if (ch == ',') {
                    payloadLen_ = 0;
                    currentState_ = State::ReadPayloadLen;
                } else {
                    currentState_ = State::Idle;
                }
                break;
            case State::ReadPayloadLen:
                if (ch >= '0' && ch <= '9') {
                    payloadLen_ = payloadLen_ * 10 + (ch - '0');
                } else if (ch == ':') {
                    bytesRead_ = 0;
                    currentState_ = State::ReadPayloadData;
                } else {
                    currentState_ = State::Idle;
                }
                break;
            case State::ReadPayloadData:
                bytesRead_++;
                if (bytesRead_ >= payloadLen_) {
                    currentState_ = State::Idle;
                }
                break;
        }
    }

    State getState() const { return currentState_; }
    int getSocketId() const { return socketId_; }
    int getPayloadLen() const { return payloadLen_; }

private:
    State currentState_;
    int socketId_;
    int payloadLen_;
    int bytesRead_;
};
