#include <complex>
#include <vector>

constexpr double PI = 3.14159265358979323846;

// Групова затримка з виміряного відгуку.
// f — частоти в Гц (зростаючі, крок довільний), H — комплексний відгук.
// tau[k] — затримка в секундах, віднесена до середини пари (f[k], f[k+1]).
std::vector<double> group_delay(const std::vector<double>& f,
                               const std::vector<std::complex<double>>& H)
{
    std::vector<double> tau(f.size() - 1);
    for (std::size_t k = 0; k + 1 < f.size(); ++k) {
        // std::arg добутку зі спряженим = приріст фази, уже згорнутий у (−π, π]
        const double dphi = std::arg(H[k + 1] * std::conj(H[k]));
        const double dw = 2.0 * PI * (f[k + 1] - f[k]);
        tau[k] = -dphi / dw;
    }
    return tau;
}
