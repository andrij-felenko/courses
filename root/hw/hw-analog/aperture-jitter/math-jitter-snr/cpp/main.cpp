#include <cmath>
#include <numbers>

// Максимально допустимий RMS-джиттер такту (с),
// щоб на частоті f_hz отримати задану кількість ефективних розрядів.
float max_jitter_for_bits(float f_hz, float bits)
{
    float snr_db = 6.02f * bits + 1.76f;                    // цільовий SNR
    float ratio  = std::pow(10.0f, snr_db / 20.0f);        // SNR у разах (амплітудно)
    return 1.0f / (2.0f * std::numbers::pi_v<float> * f_hz * ratio);
}

// приклад: max_jitter_for_bits(10e6f, 14.0f) ≈ 0.79e-12 с (з урахуванням 1.76 дБ)
