#pragma once

#include <cstdint>
#include <cstddef>
#include <functional>
#include <string>

class EspCipsendFsm {
public:
    enum class State {
        Idle,
        WaitingPrompt,
        WaitingStatus
    };

    enum class Error {
        Timeout,
        ErrorResponse,
        LinkClosed
    };

    using SendCallback = std::function<void(const uint8_t* data, size_t len)>;
    using GetMillisCallback = std::function<uint32_t()>;
    using SuccessCallback = std::function<void()>;
    using ErrorCallback = std::function<void(Error err)>;

    EspCipsendFsm(SendCallback sendCb, GetMillisCallback millisCb, uint32_t timeoutMs = 5000);

    // Ініціює процес відправки даних (з вказуванням з'єднання, -1 для режиму single connection).
    bool startSend(int linkId, const uint8_t* data, size_t length);

    // Метод, який має викликатись регулярно для обробки тайм-аутів.
    void tick();

    // Передача отриманих з UART байтів у кінцевий автомат.
    void processRxByte(char c);

    // Реєстрація функцій зворотного виклику
    void setOnSuccess(SuccessCallback cb) { onSuccess_ = cb; }
    void setOnError(ErrorCallback cb) { onError_ = cb; }

    State getState() const { return state_; }

private:
    State state_;
    SendCallback sendCb_;
    GetMillisCallback millisCb_;
    SuccessCallback onSuccess_;
    ErrorCallback onError_;
    
    std::string rxBuffer_;
    const uint8_t* pendingData_;
    size_t pendingLength_;
    
    uint32_t timeoutMs_;
    uint32_t stateStartMs_;
    
    void reset();
    void changeState(State newState);
};
