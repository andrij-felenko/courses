// C++ Idiomatic Implementation: Paul Kellet's Pink Noise Filter Class
#include <array>

namespace noise {

class PinkNoiseFilter {
public:
    double process(double white_sample) noexcept {
        b_[0] = 0.99886 * b_[0] + white_sample * 0.0555179;
        b_[1] = 0.99332 * b_[1] + white_sample * 0.0750759;
        b_[2] = 0.96900 * b_[2] + white_sample * 0.1538520;
        b_[3] = 0.86650 * b_[3] + white_sample * 0.3104856;
        b_[4] = 0.55000 * b_[4] + white_sample * 0.5329522;
        b_[5] = -0.7616 * b_[5] - white_sample * 0.0168980;
        double pink = b_[0] + b_[1] + b_[2] + b_[3] + b_[4] + b_[5] + b_[6] + white_sample * 0.5362;
        b_[6] = white_sample * 0.115926;
        return pink * 0.11;
    }

private:
    std::array<double, 7> b_{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
};

} // namespace noise
