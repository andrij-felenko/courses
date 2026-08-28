#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <cstdint>
#include <span>
#include <algorithm>

class SDRQuadratureMixer {
public:
    static constexpr size_t NcoTableSize = 1024;

    SDRQuadratureMixer(double sampleRate, double targetFreq)
        : phaseAccumulator_{0} {
        sinTable_.resize(NcoTableSize);
        cosTable_.resize(NcoTableSize);

        for (size_t i = 0; i < NcoTableSize; ++i) {
            double angle = (2.0 * std::numbers::pi * i) / NcoTableSize;
            sinTable_[i] = static_cast<float>(std::sin(angle));
            cosTable_[i] = static_cast<float>(std::cos(angle));
        }

        double normFreq = targetFreq / sampleRate;
        phaseIncrement_ = static_cast<uint32_t>(normFreq * 4294967296.0);
    }

    // Обробка масиву відліків із поверненням комплексного вектора I/Q
    void process(std::span<const float> inRf, 
                 std::span<std::complex<float>> outIq) {
        const size_t count = std::min(inRf.size(), outIq.size());
        
        for (size_t n = 0; n < count; ++n) {
            uint32_t index = phaseAccumulator_ >> (32 - 10);
            
            float cosVal = cosTable_[index];
            float sinVal = sinTable_[index];
            
            float sample = inRf[n];
            // I = sample * cos, Q = -sample * sin
            outIq[n] = std::complex<float>(sample * cosVal, -sample * sinVal);
            
            phaseAccumulator_ += phaseIncrement_;
        }
    }

private:
    std::vector<float> sinTable_;
    std::vector<float> cosTable_;
    uint32_t phaseAccumulator_{0};
    uint32_t phaseIncrement_{0};
};
