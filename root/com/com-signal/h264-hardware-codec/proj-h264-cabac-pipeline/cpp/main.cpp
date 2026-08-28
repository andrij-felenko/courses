#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <span>

class CabacEncoder {
public:
    struct Context {
        std::uint8_t pStateIdx{0}; // Стан ймовірності (0..63)
        std::uint8_t valMPS{0};    // Найімовірніший символ
    };

    explicit CabacEncoder(std::vector<std::uint8_t>& outputBuffer)
        : m_buffer(outputBuffer) {}

    void encodeBin(Context& ctx, bool binVal) {
        // 1. Пошук розщеплення діапазону за таблицею LPS
        std::uint32_t rLPS = s_rangeTabLPS[ctx.pStateIdx][(m_range >> 6) & 3];
        m_range -= rLPS;

        if (binVal == static_cast<bool>(ctx.valMPS)) {
            ctx.pStateIdx = s_transIdxMPS[ctx.pStateIdx];
        } else {
            m_low += m_range;
            m_range = rLPS;
            if (ctx.pStateIdx == 0) {
                ctx.valMPS = 1 - ctx.valMPS;
            }
            ctx.pStateIdx = s_transIdxLPS[ctx.pStateIdx];
        }

        // 2. Ренормалізація та вибірка старших бітів
        while (m_range < 256) {
            if (m_low < 256) {
                putBitWithOutstanding(0);
            } else if (m_low >= 512) {
                putBitWithOutstanding(1);
                m_low -= 512;
            } else {
                ++m_bitsOutstanding;
                m_low -= 256;
            }
            m_range <<= 1;
            m_low <<= 1;
        }
    }

    void flush() {
        // Завершення кодування та очищення залишків бітів
        putBitWithOutstanding((m_low >> 9) & 1);
        m_low <<= 1;
        putBitWithOutstanding((m_low >> 9) & 1);
        if (m_bitLeft < 8) {
            m_buffer.push_back(m_bitBuf << m_bitLeft);
        }
    }

private:
    void putBit(int bit) {
        m_bitBuf = static_cast<std::uint8_t>((m_bitBuf << 1) | (bit & 1));
        --m_bitLeft;
        if (m_bitLeft == 0) {
            m_buffer.push_back(m_bitBuf);
            m_bitBuf = 0;
            m_bitLeft = 8;
        }
    }

    void putBitWithOutstanding(int bit) {
        putBit(bit);
        while (m_bitsOutstanding > 0) {
            putBit(!bit);
            --m_bitsOutstanding;
        }
    }

    std::uint32_t m_low{0};
    std::uint32_t m_range{510};
    std::uint32_t m_bitsOutstanding{0};
    std::vector<std::uint8_t>& m_buffer;
    std::uint8_t m_bitBuf{0};
    int m_bitLeft{8};

    static constexpr std::array<std::array<std::uint8_t, 4>, 12> s_rangeTabLPS = {{
        { 128, 176, 208, 240 }, { 128, 167, 197, 227 }, { 128, 158, 187, 216 }, { 123, 150, 178, 205 },
        { 116, 142, 169, 195 }, { 111, 135, 160, 185 }, { 105, 128, 152, 175 }, { 100, 122, 144, 166 },
        {  95, 116, 137, 158 }, {  90, 110, 130, 150 }, {  85, 104, 123, 142 }, {  81,  99, 117, 135 }
    }};

    static constexpr std::array<std::uint8_t, 64> s_transIdxMPS = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
        33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
        49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 62, 63
    };

    static constexpr std::array<std::uint8_t, 64> s_transIdxLPS = {
        0, 0, 1, 2, 2, 4, 4, 5, 6, 7, 8, 9, 9, 11, 11, 12,
        13, 13, 15, 15, 16, 16, 18, 18, 19, 19, 21, 21, 22, 22, 24, 24,
        25, 25, 27, 27, 28, 28, 30, 30, 31, 31, 33, 33, 34, 34, 36, 36,
        37, 37, 39, 39, 40, 40, 42, 42, 43, 43, 45, 45, 46, 46, 48, 48
    };
};

int main() {
    std::vector<std::uint8_t> outputStream;
    CabacEncoder encoder(outputStream);

    CabacEncoder::Context syntaxContext{.pStateIdx = 10, .valMPS = 0};

    // Вхідна послідовність бінів
    const std::array<bool, 5> testSequence = {false, false, true, false, true};
    for (bool bin : testSequence) {
        encoder.encodeBin(syntaxContext, bin);
    }
    encoder.flush();

    std::cout << "Сформовано байтів CABAC (C++): " << outputStream.size() << '\n';
    return 0;
}
