#include <cstdint>
#include <cstddef>
#include <span>

extern "C" size_t LLVMFuzzerMutate(uint8_t *data, size_t size, size_t max_size);

extern "C" size_t LLVMFuzzerCustomMutator(uint8_t *data, size_t size, size_t max_size, unsigned int seed) {
    size_t mutated_size = LLVMFuzzerMutate(data, size, max_size);
    if (mutated_size < (protocol_fuzzer::HEADER_SIZE + protocol_fuzzer::CRC_SIZE)) {
        return mutated_size;
    }

    if (data[0] == protocol_fuzzer::FRAME_MAGIC_BYTE) {
        const uint8_t payload_len = data[2];
        if (payload_len <= protocol_fuzzer::MAX_PAYLOAD_SIZE && 
            (protocol_fuzzer::HEADER_SIZE + payload_len + protocol_fuzzer::CRC_SIZE) <= mutated_size) {
            
            const auto span = std::span<const uint8_t>(&data[1], (protocol_fuzzer::HEADER_SIZE - 1) + payload_len);
            const uint16_t crc = protocol_fuzzer::crc16_ccitt(span);
            
            const size_t crc_pos = protocol_fuzzer::HEADER_SIZE + payload_len;
            data[crc_pos] = static_cast<uint8_t>(crc & 0xFF);
            data[crc_pos + 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);
        }
    }

    return mutated_size;
}
