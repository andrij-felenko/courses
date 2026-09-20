class InputStorage {
public:
    static InputError saveProfile(InputProfile &profile, uint32_t nvm_address) {
        size_t payload_len = sizeof(InputProfile) - sizeof(uint16_t);
        profile.crc16 = computeCrc16(reinterpret_cast<const uint8_t*>(&profile), payload_len);
        return InputError::Ok;
    }

    static InputError loadProfile(InputProfile &profile, uint32_t nvm_address) {
        size_t payload_len = sizeof(InputProfile) - sizeof(uint16_t);
        uint16_t expected_crc = computeCrc16(reinterpret_cast<const uint8_t*>(&profile), payload_len);
        if (profile.crc16 != expected_crc) {
            return InputError::CrcMismatch;
        }
        return InputError::Ok;
    }

private:
    static uint16_t computeCrc16(const uint8_t *data, size_t length) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < length; ++i) {
            crc ^= data[i];
            for (uint8_t j = 0; j < 8; ++j) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }
};
