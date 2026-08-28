#include <vector>

std::vector<std::complex<float>> buf(1024);
for (size_t i = 0; i < 1024; ++i) {
    buf[i] = {samples[i] * hann[i], 0.0f};
}

fft_radix2(buf);

// пошук найсильнішої лінії серед бінів 1 … n/2−1
size_t kmax = 1;
float max_pwr = std::norm(buf[1]);
for (size_t k = 2; k < 512; ++k) {
    if (float pwr = std::norm(buf[k]); pwr > max_pwr) {
        max_pwr = pwr;
        kmax = k;
    }
}

float amp = 2.0f * std::abs(buf[kmax]) / w_sum;
float hz  = static_cast<float>(kmax) * (fs / 1024.0f);
