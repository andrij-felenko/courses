#include <cmath>
#include <span>

// Діюче (RMS) значення блоку відліків струму. Блок не порожній.
float rms_of_block(std::span<const float> i)
{
    float sum_sq = 0.0f;
    for (float s : i)
        sum_sq += s * s;                        // крок 1: квадрат, одразу в суму
    return std::sqrt(sum_sq / i.size());        // крок 2 і 3: середнє, тоді корінь
}
