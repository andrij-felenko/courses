namespace embedded::nfc {

template <typename I2cDriver>
class NtagI2cWriter {
public:
    explicit NtagI2cWriter(I2cDriver& i2c, uint8_t i2cAddress = 0x55) noexcept
        : i2c_(i2c), address_(i2cAddress) {}

    Status writeNdef(std::span<const uint8_t> ndefData) noexcept {
        if (ndefData.empty() || ndefData.size() > 240) {
            return Status::InvalidParam;
        }

        std::array<uint8_t, 256> memoryImage{};
        size_t offset = 0;

        // 1. TLV Marker
        memoryImage[offset++] = 0x03;
        if (ndefData.size() < 255) {
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size());
        } else {
            memoryImage[offset++] = 0xFF;
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size() >> 8);
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size() & 0xFF);
        }

        // 2. NDEF Data
        std::copy(ndefData.begin(), ndefData.end(), memoryImage.begin() + offset);
        offset += ndefData.size();

        // 3. Terminator TLV
        memoryImage[offset++] = 0xFE;

        // 4. Посторінковий запис по 16 байтів
        uint8_t startBlock = 0x04;
        size_t bytesWritten = 0;

        while (bytesWritten < offset) {
            const size_t chunk = std::min<size_t>(16, offset - bytesWritten);
            std::array<uint8_t, 16> pageBuf{};
            std::copy_n(memoryImage.begin() + bytesWritten, chunk, pageBuf.begin());

            if (!i2c_.writeMemoryBlock(address_, startBlock, pageBuf)) {
                return Status::InvalidParam;
            }

            startBlock++;
            bytesWritten += chunk;
        }

        return Status::Ok;
    }

private:
    I2cDriver& i2c_;
    uint8_t address_;
};

} // namespace embedded::nfc
