#pragma once

#include <cstdint>

// Інтерфейс для апаратно-залежних викликів
class IUart {
public:
    virtual ~IUart() = default;
    virtual void write(const uint8_t* data, uint16_t len) = 0;
    virtual bool readChar(uint8_t& c) = 0;
    virtual uint32_t getTickMs() const = 0;
};
