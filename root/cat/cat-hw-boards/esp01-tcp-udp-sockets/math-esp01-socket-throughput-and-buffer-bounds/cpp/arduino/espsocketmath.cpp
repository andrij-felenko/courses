#include <Arduino.h>

class EspSocketMath {
public:
    // Обчислення обсягу буфера хоста для захисту від переповнення
    static constexpr size_t computeHostBuffer(uint32_t baudRate, uint32_t latencyMs) {
        size_t bytesPerMs = baudRate / 10000;
        size_t latencyBytes = bytesPerMs * latencyMs;
        constexpr size_t espFifoHeadroom = 128;
        return latencyBytes + espFifoHeadroom + 64; // З резервом watermark
    }

    // Обчислення таймауту FSM-автомата для відправки сокета
    static uint32_t computeSendTimeoutMs(uint32_t baudRate, size_t payloadSize, uint32_t networkRttMs) {
        uint32_t uartTxTimeMs = static_cast<uint32_t>((payloadSize + 50) * 10000UL / baudRate);
        constexpr uint32_t espProcessingMs = 100;
        constexpr uint32_t marginMs = 500;
        return uartTxTimeMs + networkRttMs + espProcessingMs + marginMs;
    }
};
