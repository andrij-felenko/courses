// g711_codec.cpp - Ідіоматична реалізація G.711 мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cmath>
#include <cstdint>
#include <algorithm>

namespace g711 {

constexpr int16_t MAX_PCM = 32512;
constexpr int16_t BIAS = 33;

constexpr std::array<uint16_t, 8> SEG_END_ALAW = {
    0x1F, 0x3F, 0x7F, 0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF
};

class Codec {
public:
    [[nodiscard]] static constexpr uint8_t encode_alaw(int16_t pcm_val) noexcept {
        int mask = (pcm_val >= 0) ? 0xD5 : 0x55;
        if (pcm_val < 0) {
            pcm_val = -pcm_val - 1;
            if (pcm_val < 0) pcm_val = 32767;
        }

        pcm_val = std::min(pcm_val, MAX_PCM);

        int pcm_shifted = pcm_val >> 3;
        int seg = 0;
        while (seg < 8 && pcm_shifted > SEG_END_ALAW[seg]) {
            ++seg;
        }

        if (seg >= 8) {
            return static_cast<uint8_t>(0x7F ^ mask);
        }

        uint8_t aval = static_cast<uint8_t>(seg << 4);
        if (seg < 2) {
            aval |= (pcm_val >> 1) & 0x0F;
        } else {
            aval |= (pcm_val >> (seg + 2)) & 0x0F;
        }
        return static_cast<uint8_t>(aval ^ mask);
    }

    [[nodiscard]] static constexpr int16_t decode_alaw(uint8_t a_val) noexcept {
        a_val ^= 0xD5;
        int t = (a_val & 0x0F) << 4;
        int seg = (a_val & 0x70) >> 4;

        switch (seg) {
            case 0:  t += 8; break;
            case 1:  t += 0x108; break;
            default: t = (t + 0x108) << (seg - 1); break;
        }
        return (a_val & 0x80) ? static_cast<int16_t>(t) : static_cast<int16_t>(-t);
    }

    static void encode_stream_alaw(std::span<const int16_t> pcm_in, std::span<uint8_t> alaw_out) {
        const size_t count = std::min(pcm_in.size(), alaw_out.size());
        for (size_t i = 0; i < count; ++i) {
            alaw_out[i] = encode_alaw(pcm_in[i]);
        }
    }

    static void decode_stream_alaw(std::span<const uint8_t> alaw_in, std::span<int16_t> pcm_out) {
        const size_t count = std::min(alaw_in.size(), pcm_out.size());
        for (size_t i = 0; i < count; ++i) {
            pcm_out[i] = decode_alaw(alaw_in[i]);
        }
    }
};

} // namespace g711

int main() {
    const std::vector<int16_t> pcm_buffer = { 0, 100, 500, 2000, 10000, -5000, 32000 };
    std::vector<uint8_t> alaw_buffer(pcm_buffer.size());
    std::vector<int16_t> restored_pcm(pcm_buffer.size());

    g711::Codec::encode_stream_alaw(pcm_buffer, alaw_buffer);
    g711::Codec::decode_stream_alaw(alaw_buffer, restored_pcm);

    std::cout << "G.711 C++20 Stream Processing Results:\n";
    for (size_t i = 0; i < pcm_buffer.size(); ++i) {
        std::cout << "PCM In: " << pcm_buffer[i]
                  << " -> A-law: 0x" << std::hex << (int)alaw_buffer[i] << std::dec
                  << " -> PCM Out: " << restored_pcm[i]
                  << " (Diff: " << std::abs(pcm_buffer[i] - restored_pcm[i]) << ")\n";
    }

    return 0;
}
