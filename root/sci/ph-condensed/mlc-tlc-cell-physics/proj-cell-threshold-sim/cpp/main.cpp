#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <string>

// Типи комірок NAND
enum class CellType { SLC = 1, MLC = 2, TLC = 3, QLC = 4 };

// Параметри фізичного стану комірки
struct Cell {
    double vth;            // Порогова напруга V_th у вольтах
    int target_state;      // Цільовий логічний стан (0 .. 2^N - 1)
};

// Клас симулятора фізики комірок NAND
class FlashArraySimulator {
private:
    size_t cell_count;
    CellType type;
    int states_count;
    std::vector<Cell> cells;
    
    std::mt19937 rng;
    
public:
    FlashArraySimulator(size_t count, CellType cell_type) 
        : cell_count(count), type(cell_type), rng(42) 
    {
        states_count = 1 << static_cast<int>(type);
        cells.resize(cell_count);
    }

    // Етап 1: Стирання комірок (формування від'ємного піку Erased)
    void erase_array() {
        std::normal_distribution<double> erased_dist(-2.5, 0.30);
        for (auto& cell : cells) {
            cell.vth = erased_dist(rng);
            cell.target_state = 0; // Стираний стан 'E'
        }
    }

    // Етап 2: Інкрементальне програмування ISPP
    void program_array(double delta_vpgm) {
        std::uniform_int_distribution<int> state_dist(0, states_count - 1);
        std::normal_distribution<double> inject_noise(0.0, 0.05);

        // Цільові напруги верифікації V_verify для кожної з точок
        std::vector<double> v_verify(states_count);
        double window_step = 6.0 / states_count; // Робоче вікно 6.0 Вольт
        for (int i = 0; i < states_count; ++i) {
            v_verify[i] = -1.5 + i * window_step;
        }

        for (auto& cell : cells) {
            cell.target_state = state_dist(rng);
            if (cell.target_state == 0) continue; // Erased стан не програмується

            double target_v = v_verify[cell.target_state];
            // Цикл імпульсів ISPP
            while (cell.vth < target_v) {
                cell.vth += delta_vpgm + inject_noise(rng);
            }
        }
    }

    // Етап 3: Додавання фізичних шумів (Disturb, RTN, Retention)
    void apply_degradation(double pe_cycles, double retention_hours) {
        // Коефіцієнт деградації оксиду зростає від P/E циклів
        double oxide_damage = std::sqrt(pe_cycles / 1000.0);
        
        std::normal_distribution<double> rtn_dist(0.0, 0.03 * (1.0 + oxide_damage));
        std::normal_distribution<double> disturb_dist(0.04 * oxide_damage, 0.02);

        // Логарифмічний витік заряду у часі
        double retention_loss = 0.05 * oxide_damage * std::log(1.0 + retention_hours);

        for (auto& cell : cells) {
            double rtn = rtn_dist(rng);
            double disturb = (cell.target_state > 0) ? disturb_dist(rng) : 0.01;
            
            cell.vth += rtn + disturb - retention_loss;
        }
    }

    // Етап 4: Декодування станів та розрахунок RBER
    double calculate_rber() {
        std::vector<double> v_ref(states_count - 1);
        double window_step = 6.0 / states_count;
        for (int i = 0; i < states_count - 1; ++i) {
            v_ref[i] = -1.5 + (i + 0.5) * window_step;
        }

        size_t bit_errors = 0;
        size_t total_bits = cell_count * static_cast<int>(type);

        for (const auto& cell : cells) {
            int detected_state = 0;
            for (int i = 0; i < states_count - 1; ++i) {
                if (cell.vth > v_ref[i]) {
                    detected_state = i + 1;
                }
            }

            // Кодування Грея: обчислення різниці бітів
            int diff = cell.target_state ^ detected_state;
            while (diff > 0) {
                if (diff & 1) bit_errors++;
                diff >>= 1;
            }
        }

        return static_cast<double>(bit_errors) / total_bits;
    }
};

int main() {
    const size_t NUM_CELLS = 100000;
    std::cout << "=== Симуляція фізики порогових напруг NAND (100,000 комірок) ===" << std::endl;

    std::vector<CellType> types = { CellType::SLC, CellType::MLC, CellType::TLC, CellType::QLC };
    std::vector<std::string> names = { "SLC (1 біт)", "MLC (2 біти)", "TLC (3 біти)", "QLC (4 біти)" };

    std::cout << std::left << std::setw(15) << "Тип комірки"
              << std::setw(15) << "P/E Цикли"
              << std::setw(18) << "Час Retention"
              << std::setw(15) << "RBER (Помилки)" << std::endl;
    std::cout << std::string(63, '-') << std::endl;

    for (size_t i = 0; i < types.size(); ++i) {
        FlashArraySimulator sim(NUM_CELLS, types[i]);
        sim.erase_array();
        sim.program_array(0.20); // ΔV_pgm = 0.20В
        
        // Симуляція підвищеного навантаження (3000 P/E, 1000 годин при 55°C)
        double pe = (types[i] == CellType::SLC) ? 10000.0 : (types[i] == CellType::MLC) ? 3000.0 : 1000.0;
        sim.apply_degradation(pe, 1000.0);
        
        double rber = sim.calculate_rber();

        std::cout << std::left << std::setw(15) << names[i]
                  << std::setw(15) << static_cast<int>(pe)
                  << std::setw(18) << "1000 год"
                  << std::scientific << std::setprecision(3) << rber << std::endl;
    }

    return 0;
}
