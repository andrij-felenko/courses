#include "EspCipsendFsm.hpp"

EspCipsendFsm::EspCipsendFsm(SendCallback sendCb, GetMillisCallback millisCb, uint32_t timeoutMs)
    : state_(State::Idle), sendCb_(sendCb), millisCb_(millisCb), timeoutMs_(timeoutMs), stateStartMs_(0) {
    reset();
}

bool EspCipsendFsm::startSend(int linkId, const uint8_t* data, size_t length) {
    if (state_ != State::Idle || !data || length == 0) {
        return false;
    }
    
    pendingData_ = data;
    pendingLength_ = length;
    
    std::string cmd = "AT+CIPSEND=";
    if (linkId >= 0) {
        cmd += std::to_string(linkId) + ",";
    }
    cmd += std::to_string(length) + "\r\n";
    
    sendCb_(reinterpret_cast<const uint8_t*>(cmd.data()), cmd.length());
    changeState(State::WaitingPrompt);
    return true;
}

void EspCipsendFsm::tick() {
    if (state_ == State::Idle) {
        return;
    }
    
    if (millisCb_() - stateStartMs_ >= timeoutMs_) {
        reset();
        if (onError_) {
            onError_(Error::Timeout);
        }
    }
}

void EspCipsendFsm::processRxByte(char c) {
    if (state_ == State::Idle) {
        return;
    }
    
    rxBuffer_ += c;
    
    if (state_ == State::WaitingPrompt) {
        // Очікуємо символ '>' як запрошення для передачі корисного навантаження
        if (rxBuffer_.find(">") != std::string::npos) {
            sendCb_(pendingData_, pendingLength_);
            rxBuffer_.clear();
            changeState(State::WaitingStatus);
        } else if (rxBuffer_.find("ERROR") != std::string::npos) {
            reset();
            if (onError_) {
                onError_(Error::ErrorResponse);
            }
        }
    } else if (state_ == State::WaitingStatus) {
        // Очікуємо підтвердження або помилку відправки
        if (rxBuffer_.find("SEND OK") != std::string::npos) {
            reset();
            if (onSuccess_) {
                onSuccess_();
            }
        } else if (rxBuffer_.find("ERROR") != std::string::npos) {
            reset();
            if (onError_) {
                onError_(Error::ErrorResponse);
            }
        } else if (rxBuffer_.find("link is not valid") != std::string::npos ||
                   rxBuffer_.find("CLOSED") != std::string::npos) {
            reset();
            if (onError_) {
                onError_(Error::LinkClosed);
            }
        }
        
        // Очищення старого буфера для запобігання переповненню та витоку пам'яті
        if (rxBuffer_.length() > 128) {
            rxBuffer_.erase(0, rxBuffer_.length() - 64);
        }
    }
}

void EspCipsendFsm::reset() {
    state_ = State::Idle;
    rxBuffer_.clear();
    pendingData_ = nullptr;
    pendingLength_ = 0;
}

void EspCipsendFsm::changeState(State newState) {
    state_ = newState;
    stateStartMs_ = millisCb_();
}
