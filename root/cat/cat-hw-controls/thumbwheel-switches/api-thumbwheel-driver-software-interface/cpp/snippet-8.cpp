ThumbwheelStatus ThumbwheelDriver::decodeValue(uint16_t& outValue) {
    uint16_t result = 0;
    uint16_t multiplier = 1;
    
    for (uint8_t i = 0; i < config_.decadesCount; ++i) {
        uint8_t bcd = nibbles_[i];
        
        if (bcd > 9) {
            return ThumbwheelStatus::InvalidBcd;
        }
        
        result += bcd * multiplier;
        multiplier *= 10;
    }
    
    validatedValue_ = result;
    outValue = result;
    return ThumbwheelStatus::Ok;
}
