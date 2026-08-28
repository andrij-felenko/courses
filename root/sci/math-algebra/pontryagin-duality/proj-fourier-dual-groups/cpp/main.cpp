#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <span>
#include <iomanip>

namespace math::fourier {

using Complex = std::complex<double>;
constexpr double PI = 3.14159265358979323846;

/* Представлення скінченної абелевої групи як прямого добутку циклічних компонент */
class FiniteAbelianGroup {
public:
    explicit FiniteAbelianGroup(std::vector<int> orders)
        : orders_(std::move(orders)) {
        strides_.resize(orders_.size());
        total_order_ = 1;
        for (int ord : orders_) {
            total_order_ *= ord;
        }
        if (!orders_.empty()) {
            strides_.back() = 1;
            for (int i = static_cast<int>(orders_.size()) - 2; i >= 0; --i) {
                strides_[i] = strides_[i + 1] * orders_[i + 1];
            }
        }
    }

    [[nodiscard]] int total_order() const noexcept {
        return total_order_;
    }

    [[nodiscard]] std::span<const int> orders() const noexcept {
        return orders_;
    }

    /* Декодування лінійного індексу у вектор координат */
    [[nodiscard]] std::vector<int> decode(int idx) const {
        std::vector<int> coords(orders_.size());
        int rem = idx;
        for (size_t i = 0; i < orders_.size(); ++i) {
            coords[i] = rem / strides_[i];
            rem %= strides_[i];
        }
        return coords;
    }

    /* Кодування вектора координат у лінійний індекс */
    [[nodiscard]] int encode(std::span<const int> coords) const {
        int idx = 0;
        for (size_t i = 0; i < orders_.size(); ++i) {
            idx += coords[i] * strides_[i];
        }
        return idx;
    }

    /* Обчислення значення характеру chi_y(x) */
    [[nodiscard]] Complex eval_character(int x_idx, int y_idx) const {
        const auto x = decode(x_idx);
        const auto y = decode(y_idx);

        double total_phase = 0.0;
        for (size_t i = 0; i < orders_.size(); ++i) {
            total_phase += 2.0 * PI * (static_cast<double>(x[i] * y[i])) / static_cast<double>(orders_[i]);
        }
        return std::polar(1.0, total_phase);
    }

    /* Пряме перетворення Фур'є (GDFT) */
    [[nodiscard]] std::vector<Complex> transform(std::span<const Complex> input) const {
        const int N = total_order_;
        const double scale = 1.0 / std::sqrt(static_cast<double>(N));
        std::vector<Complex> output(N);

        for (int y = 0; y < N; ++y) {
            Complex sum = 0.0;
            for (int x = 0; x < N; ++x) {
                sum += input[x] * std::conj(eval_character(x, y));
            }
            output[y] = sum * scale;
        }
        return output;
    }

    /* Обернене перетворення Фур'є (IGDFT) */
    [[nodiscard]] std::vector<Complex> inverse_transform(std::span<const Complex> input) const {
        const int N = total_order_;
        const double scale = 1.0 / std::sqrt(static_cast<double>(N));
        std::vector<Complex> output(N);

        for (int x = 0; x < N; ++x) {
            Complex sum = 0.0;
            for (int y = 0; y < N; ++y) {
                sum += input[y] * eval_character(x, y);
            }
            output[x] = sum * scale;
        }
        return output;
    }

    /* Групова згортка f * h */
    [[nodiscard]] std::vector<Complex> convolve(std::span<const Complex> f, std::span<const Complex> h) const {
        const int N = total_order_;
        std::vector<Complex> out(N, 0.0);
        std::vector<int> diff_coords(orders_.size());

        for (int x = 0; x < N; ++x) {
            const auto x_coords = decode(x);
            Complex sum = 0.0;
            for (int z = 0; z < N; ++z) {
                const auto z_coords = decode(z);
                for (size_t i = 0; i < orders_.size(); ++i) {
                    diff_coords[i] = (x_coords[i] - z_coords[i] + orders_[i]) % orders_[i];
                }
                const int diff_idx = encode(diff_coords);
                sum += f[z] * h[diff_idx];
            }
            out[x] = sum;
        }
        return out;
    }

    /* Знаходження анулятора підгрупи */
    [[nodiscard]] std::vector<int> find_annihilator(std::span<const int> generator_indices) const {
        const int N = total_order_;
        constexpr double EPS = 1e-7;
        std::vector<int> annihilator;

        for (int y = 0; y < N; ++y) {
            bool is_ann = true;
            for (int gen : generator_indices) {
                const Complex val = eval_character(gen, y);
                if (std::abs(val - 1.0) > EPS) {
                    is_ann = false;
                    break;
                }
            }
            if (is_ann) {
                annihilator.push_back(y);
            }
        }
        return annihilator;
    }

private:
    std::vector<int> orders_;
    std::vector<int> strides_;
    int total_order_{1};
};

} // namespace math::fourier

int main() {
    using namespace math::fourier;

    // Створюємо групу G = Z_2 x Z_4
    FiniteAbelianGroup G({2, 4});

    std::cout << "Група G = Z_2 x Z_4, загальний порядок |G| = " << G.total_order() << "\n\n";

    // Створюємо тестовий сигнал
    std::vector<Complex> signal(G.total_order());
    for (size_t i = 0; i < signal.size(); ++i) {
        signal[i] = Complex(static_cast<double>(i + 1), 0.0);
    }

    // Обчислюємо пряме та обернене перетворення
    const auto spectrum = G.transform(signal);
    const auto reconstructed = G.inverse_transform(spectrum);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Відновлення сигналу через унітарний GDFT:\n";
    double total_err = 0.0;
    for (int i = 0; i < G.total_order(); ++i) {
        const double err = std::abs(signal[i] - reconstructed[i]);
        total_err += err;
        std::cout << "  x=" << i << ": початковий=" << signal[i].real()
                  << " -> відновлений=" << reconstructed[i].real() << "\n";
    }
    std::cout << "Похибка відновлення: " << total_err << "\n\n";

    // Перевірка теореми Планшереля
    double energy_time = 0.0;
    for (const auto& val : signal) {
        energy_time += std::norm(val);
    }
    double energy_freq = 0.0;
    for (const auto& val : spectrum) {
        energy_freq += std::norm(val);
    }
    std::cout << "Енергія в часовому домені:   " << energy_time << "\n";
    std::cout << "Енергія в частотному домені: " << energy_freq << "\n";
    std::cout << "Різниця енергій (теорема Планшереля): " << std::abs(energy_time - energy_freq) << "\n\n";

    // Знаходження анулятора підгрупи H = <(0, 2)>
    const int gen_idx = G.encode(std::array<int, 2>{0, 2});
    const auto ann = G.find_annihilator(std::array<int, 1>{gen_idx});

    std::cout << "Підгрупа H породжена елементом (0, 2) [індекс " << gen_idx << "]\n";
    std::cout << "Розмір анулятора H^perp = " << ann.size() << " (очікувано 4):\n";
    for (int freq_idx : ann) {
        const auto coords = G.decode(freq_idx);
        std::cout << "  Частота " << freq_idx << ": (" << coords[0] << ", " << coords[1] << ")\n";
    }

    return 0;
}
