#pragma once
#include <cstdint>

class SpiHal {
public:
    virtual ~SpiHal() = default;
    
    virtual void init() = 0;
    virtual uint8_t transfer(uint8_t data) = 0;
    virtual void cs_low() = 0;
    virtual void cs_high() = 0;
    virtual bool is_miso_low() = 0;
    virtual bool get_gdo0() = 0; // Для перевірки статусу прийому/передачі
};
