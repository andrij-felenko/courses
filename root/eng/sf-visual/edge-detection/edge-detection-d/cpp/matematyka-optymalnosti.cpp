#include <cmath>
#include <cstdio>
#include <numeric>
#include <vector>

// SNR ≈ A·|сума додатних ваг| / (n0·√(сума квадратів ваг))
static double snr(const std::vector<int> &k, double A, double n0) {
    double sig = 0, energy = 0;
    for (int w : k) {
        if (w > 0) sig += w;              // внесок у відгук на сходинку
        energy += static_cast<double>(w) * w;  // пропускання шуму
    }
    return A * sig / (n0 * std::sqrt(energy));
}

int main() {
    std::vector<int> sobel = {-1, 0, 1};
    std::vector<int> wide  = {-1, -2, 0, 2, 1};
    std::printf("вузьке  [-1 0 1]:      SNR = %.2f\n", snr(sobel, 100, 10));
    std::printf("ширше   [-1 -2 0 2 1]: SNR = %.2f\n", snr(wide,  100, 10));
    return 0;
}
