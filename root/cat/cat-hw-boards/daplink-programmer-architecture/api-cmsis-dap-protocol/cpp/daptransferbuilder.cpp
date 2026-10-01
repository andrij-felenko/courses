#include <cstdint>
#include <vector>

// Формування бінарного кадру запису в регістри CoreSight
class DapTransferBuilder {
public:
    static std::vector<uint8_t> buildDpWrite(uint8_t regAddr, uint32_t data) {
        std::vector<uint8_t> packet;
        packet.reserve(8);
        
        packet.push_back(0x05); // DAP_Transfer
        packet.push_back(0x00); // DAP Index
        packet.push_back(0x01); // Transfer Count = 1
        
        // Бітова маска: Direction=0 (Write), Port=0 (DP), Address A[2:3]
        const uint8_t requestByte = regAddr & 0x0C;
        packet.push_back(requestByte);
        
        // Додавання 32-бітного слова у форматі Little-Endian
        for (int i = 0; i < 4; ++i) {
            packet.push_back(static_cast<uint8_t>((data >> (i * 8)) & 0xFF));
        }
        
        return packet;
    }
};
