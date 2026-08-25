# ⚙️ Алгоритм та симуляція однофотонних імпульсів ФЕУ

Цей проект присвячено чисельному моделюванню стохастичних процесів формування та цифрової обробки сигналів фотоелектронного помножувача (ФЕУ). Симуляція охоплює повний фізичний траєкторійний цикл: від квантового вильоту первинного фотоелектрона за законом Пуассона до каскадного помноження на системі дінодів, згортки з аналоговою імпульсною характеристикою анодного кола та часової дискримінації за методом постійної частки (CFD).

### Фізичні основи алгоритму симуляції

1. **Моделювання фотоелектричного випромінювання (Первинний шар):**
   При падінні на фотокатод слабкого світлового спалаху середня кількість фотоелектронів визначається добутком кількості фотонів на квантову ефективність `μ = η · N_photon`. Оскільки випромінювання фотонів є квантово-статистичним процесом, точна кількість випромінених електронів у кожному окремому вимірювальному події описується генератором випадкових чисел з розподілом Пуассона з параметром `μ`.

2. **Стохастичний каскад дінодного підсилення (Помножувач):**
   Кожен вибитий первинний фотоелектрон прискорюється в міжелектродному просторі й бомбардує перший дінод. Кількість вибитих вторинних електронів є випадковою величиною. У традиційній моделі емісія на кожному діноді підпорядковується розподілу Пуассона з середнім значенням `λ = δ`. Проте при високих енергіях первинних електронів флуктуації структури емітера краще описувати розподілом Пойя (негативним біноміальним). У даній симуляції проводиться поетапний розрахунок для `N` послідовних каскадів: кількість електронів на кроці `k` визначає параметр Пуассона для кроку `k+1`.

3. **Аналогова згортка та часовий профіль анодного струму:**
   Електронна хмарина, що прибуває на анод, має сумарний заряд `Q = M · e`, де `M` — підсумкова кількість електронів після `N` дінодів. Струмовий сплеск не є миттєвим delta-імпульсом через розкид часу прольоту (TTS) окремих електронів у лавині. Його форма на навантаженні 50 Ом моделюється аналітичною імпульсною функцією Gamma-профілю:

```
V(t) = V_peak · (t / t_rise) · exp(1 - t / t_rise)   [при t > 0]
```

де `t_rise` — час зростання фронту імпульсу (1–2 нс). На аналоговий сигнал накладається гаусів термодинамічний шум підсилювача з середньоквадратичним відхиленням `σ_noise`.

4. **Дискримінація за постійною часткою (CFD) для усунення часового зсуву (Walk Error):**
   Звичайна порогова дискримінація за амплітудою створює похибку прив'язки часу (амплітудний зсув, *walk error*): імпульси більшої амплітуди перетинають фіксований поріг раніше за імпульси меншої амплітуди, навіть якщо вони виникли в один момент часу.
   Алгоритм CFD усуває цю похибку за допомогою трьох послідовних операцій:
   - Вхідний сигнал `V(t)` розділяється на два канали.
   - У першому каналі сигнал інвертується й ослаблюється у `f` разів (де `f = 0.2` — постійна частка, 20% від піку).
   - У другому каналі сигнал затримується на час `t_delay = t_rise · (1 - f)`.
   - Два сигнали підсумовуються: `V_cfd(t) = V_delayed(t) - f · V_orig(t)`.
   - Точка перетину нуля (`V_cfd(t) = 0`) визначає точний час прильоту фотона, який абсолютно не залежить від амплітуди імпульсу.

### Крайові випадки та геометрична інтерполяція

Під час чисельного аналізу анодних імпульсів виникають три важливі крайові ситуації:
- **Нульовий вихід електронів:** Якщо первинний фотон не вибив жодного фотоелектрона чи емісія на першому діноді випадково дорівнювала нулю, алгоритм повертає чистий шум з нульовою сигнальною складовою.
- **Дробовий крок дискретизації:** Точка перетину нуля дискримінатора CFD зазвичай потрапляє між двома сусідніми цифровими відліками `t[i-1]` та `t[i]`. Для збереження sub-nanosecond точності алгоритм здійснює сублінійну інтерполяцію нахилу нульового переходу.
- **Шумові хибні спрацьовування:** У відсутності корисного імпульсу високовольтний фліккер-шум може створити хибний нульовий перетин. Щоб запобігти цьому, в реальних CFD застосовують додатковий амплітудний компаратор зброювання (armations comparator), який дозволяє пошук нуля лише після перевищення сигналом мінімального порогу `V_arm > 3 · σ_noise`.

### Аналіз часового джитеру та оптимізація параметрів

Параметри симуляції безпосередньо відображають фізичні властивості детектора та оцифровщика:
- **Частка CFD (`f = 0.2`):** Значення 20% від амплітуди піку обрано тому, що на цій висоті фронт імпульсу є найкрутішим і найменше піддається впливу шумів підсилювача.
- **Крок дискретизації (`dt_ns = 0.1 нс`):** Відповідає частоті оцифрування аналогово-цифрового перетворювача 10 Gsps. При повільнішому АЦП (наприклад, 1 Gsps, `dt = 1 нс`) інтерполяція нульового перетину стає менш точною через нелінійність фронту.
- **Розподіл амплітуд:** Шляхом багаторазового прогону методу Монте-Карло для тисяч світлових спалахів алгоритм дозволяє будувати амплітудний спектр однофотонних імпульсів (PHS), обчислювати коефіцієнт підсилення та аналізувати часовий джитер (TTS).

### Моделювання накладання імпульсів (Pulse Pile-Up) та мертвого часу

При великій інтенсивності світлового потоку (понад `10⁶` фотонів за секунду) часовий інтервал між сусідніми каскадними імпульсами стає порівнянним із тривалістю спаду імпульсу `t_fall`. У цьому випадку виникає ефект **накладання імпульсів** (*pulse pile-up*): другий імпульс нашаровується на спадний хвіст першого.
В реальних цифрових оцифровщиках це викликає два негативні наслідки:
- **Паразитна зміна порогу:** Амплітуда другого імпульсу відраховується не від нуля, а від залишкового потенціалу попереднього хвоста, що викривляє спектр амплітуд (PHS).
- **Мертвий час (Dead Time):** Якщо новий фотон прибуває раніше, ніж дискримінатор повернеться в стан зброювання, друга подія губиться. Симуляція дозволяє кількісно обчислити паралітичний та непаралітичний мертвий час системи зчитування.

### Розбір реалізації мовами C та C++

Наведені нижче приклади демонструють ідіоматичні реалізації симулятора:

- **C++ реалізація:** Використовує сучасний стандарт C++17, об'єктно-орієнтовану структуру `PMTSimulator`, генератор псевдовипадкових чисел `std::mt19937` із мережі Мерсенна та стандартний математичний розподіл `std::poisson_distribution`. Контейнер `std::vector<double>` керує пам'яттю за принципом RAII, запобігаючи витокам пам'яті.
- **C реалізація:** Написана в чистому стандарті C99 з використанням функцій `rand()`, моделюванням пуассонівського процесу за алгоритмом Кнута та прямими масивами статичного розміру для ефективного випилювання в мікроконтролерних системах зчитування.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <algorithm>

struct PMTConfig {
    double quantum_efficiency = 0.25; // 25% квантова ефективність
    double dynode_gain = 4.0;         // Середнє підсилення одного дінода (δ)
    std::size_t num_dynodes = 10;     // Кількість дінодів N
    double t_rise_ns = 1.2;           // Час фронту імпульсу (нс)
    double t_fall_ns = 3.5;           // Час спаду імпульсу (нс)
    double dt_ns = 0.1;               // Крок дискретизації часу (нс)
    double noise_sigma_mV = 0.5;      // Шуми електронного підсилювача (мВ)
    double cfd_fraction = 0.2;        // Частка CFD (20%)
};

class PMTSimulator {
public:
    explicit PMTSimulator(const PMTConfig& config) 
        : cfg_(config), rng_(std::random_device{}()) {}

    // Стохастична симуляція каскаду дінодів
    std::uint64_t simulate_cascade(std::size_t num_photoelectrons) {
        std::uint64_t current_electrons = num_photoelectrons;
        for (std::size_t d = 0; d < cfg_.num_dynodes; ++d) {
            if (current_electrons == 0) break;
            std::poisson_distribution<std::uint64_t> dist(current_electrons * cfg_.dynode_gain);
            current_electrons = dist(rng_);
        }
        return current_electrons;
    }

    // Генерація оцифрованого аналогового сигналу анода
    std::vector<double> generate_pulse(std::uint64_t total_anode_electrons, double total_time_ns) {
        std::size_t num_samples = static_cast<std::size_t>(total_time_ns / cfg_.dt_ns);
        std::vector<double> voltage(num_samples, 0.0);

        if (total_anode_electrons == 0) return voltage;

        constexpr double e_charge = 1.602e-19;
        double Q_coulomb = static_cast<double>(total_anode_electrons) * e_charge;
        double R_load = 50.0;
        std::normal_distribution<double> noise_dist(0.0, cfg_.noise_sigma_mV);

        for (std::size_t i = 0; i < num_samples; ++i) {
            double t = static_cast<double>(i) * cfg_.dt_ns;
            if (t > 0.0) {
                double shape = (t / cfg_.t_rise_ns) * std::exp(1.0 - t / cfg_.t_rise_ns);
                double current_A = (Q_coulomb / (cfg_.t_fall_ns * 1e-9)) * shape;
                voltage[i] = (current_A * R_load * 1e3) + noise_dist(rng_);
            } else {
                voltage[i] = noise_dist(rng_);
            }
        }
        return voltage;
    }

    // Алгоритм CFD-дискримінації для знаходження точки перетину нуля
    double find_cfd_zero_crossing(const std::vector<double>& waveform) {
        std::size_t delay_samples = static_cast<std::size_t>((cfg_.t_rise_ns * (1.0 - cfg_.cfd_fraction)) / cfg_.dt_ns);
        std::vector<double> cfd_signal(waveform.size(), 0.0);

        for (std::size_t i = 0; i < waveform.size(); ++i) {
            double delayed = (i >= delay_samples) ? waveform[i - delay_samples] : 0.0;
            double attenuated = cfg_.cfd_fraction * waveform[i];
            cfd_signal[i] = delayed - attenuated;
        }

        // Пошук нульового перетину
        for (std::size_t i = 1; i < cfd_signal.size(); ++i) {
            if (cfd_signal[i - 1] < 0.0 && cfd_signal[i] >= 0.0) {
                // Лінійна інтерполяція часу перетину
                double t1 = static_cast<double>(i - 1) * cfg_.dt_ns;
                double t2 = static_cast<double>(i) * cfg_.dt_ns;
                double y1 = cfd_signal[i - 1];
                double y2 = cfd_signal[i];
                return t1 + (0.0 - y1) * (t2 - t1) / (y2 - y1);
            }
        }
        return -1.0; // Нуль не знайдено
    }

private:
    PMTConfig cfg_;
    std::mt19937 rng_;
};

int main() {
    PMTConfig config;
    PMTSimulator sim(config);

    std::size_t primary_photons = 5;
    std::uint64_t anode_electrons = sim.simulate_cascade(primary_photons);

    std::cout << "=== Симуляція анодного імпульсу ФЕУ та CFD-таймінгу ===\n";
    std::cout << "Кількість первинних фотоелектронів: " << primary_photons << "\n";
    std::cout << "Загальний заряд на аноді (електронів): " << anode_electrons << "\n";
    std::cout << "Коефіцієнт підсилення каскаду M: " << std::scientific << static_cast<double>(anode_electrons) / primary_photons << "\n";

    auto waveform = sim.generate_pulse(anode_electrons, 25.0);
    double cfd_time = sim.find_cfd_zero_crossing(waveform);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "\nРезультат CFD дискримінації:\n";
    std::cout << "Точний час прильоту фотона (Zero-Crossing): " << cfd_time << " нс\n";

    std::cout << "\nФорма оцифрованої напруги анода (перші 10 відліків):\n";
    for (std::size_t i = 0; i < 10 && i < waveform.size(); ++i) {
        std::cout << "t = " << i * config.dt_ns << " нс: " << waveform[i] << " мВ\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

typedef struct {
    double quantum_efficiency;
    double dynode_gain;
    int num_dynodes;
    double t_rise_ns;
    double t_fall_ns;
    double dt_ns;
    double noise_sigma_mV;
    double cfd_fraction;
} PMTConfigC;

// Генерація випадкового значення Пуассона
long simulate_poisson_c(double lambda) {
    double L = exp(-lambda);
    double k = 0;
    double p = 1.0;
    do {
        k += 1.0;
        p *= ((double)rand() / RAND_MAX);
    } while (p > L);
    return (long)(k - 1);
}

long simulate_cascade_c(const PMTConfigC* cfg, long num_photoelectrons) {
    long current_electrons = num_photoelectrons;
    for (int d = 0; d < cfg->num_dynodes; ++d) {
        if (current_electrons <= 0) break;
        double mean = (double)current_electrons * cfg->dynode_gain;
        current_electrons = simulate_poisson_c(mean);
    }
    return current_electrons;
}

void generate_pulse_c(const PMTConfigC* cfg, long total_electrons, double total_time_ns, double* voltage, int num_samples) {
    double e_charge = 1.602e-19;
    double Q_coulomb = (double)total_electrons * e_charge;
    double R_load = 50.0;

    for (int i = 0; i < num_samples; ++i) {
        double t = (double)i * cfg->dt_ns;
        double noise = ((double)rand() / RAND_MAX - 0.5) * 2.0 * cfg->noise_sigma_mV;
        if (t > 0.0) {
            double shape = (t / cfg->t_rise_ns) * exp(1.0 - t / cfg->t_rise_ns);
            double current_A = (Q_coulomb / (cfg->t_fall_ns * 1e-9)) * shape;
            voltage[i] = (current_A * R_load * 1000.0) + noise;
        } else {
            voltage[i] = noise;
        }
    }
}

double find_cfd_zero_crossing_c(const PMTConfigC* cfg, const double* waveform, int num_samples) {
    int delay_samples = (int)((cfg->t_rise_ns * (1.0 - cfg->cfd_fraction)) / cfg->dt_ns);
    
    for (int i = 1; i < num_samples; ++i) {
        double delayed1 = ((i - 1) >= delay_samples) ? waveform[(i - 1) - delay_samples] : 0.0;
        double cfd1 = delayed1 - (cfg->cfd_fraction * waveform[i - 1]);

        double delayed2 = (i >= delay_samples) ? waveform[i - delay_samples] : 0.0;
        double cfd2 = delayed2 - (cfg->cfd_fraction * waveform[i]);

        if (cfd1 < 0.0 && cfd2 >= 0.0) {
            double t1 = (double)(i - 1) * cfg->dt_ns;
            double t2 = (double)i * cfg->dt_ns;
            return t1 + (0.0 - cfd1) * (t2 - t1) / (cfd2 - cfd1);
        }
    }
    return -1.0;
}

int main(void) {
    srand((unsigned int)time(NULL));

    PMTConfigC cfg = {0.25, 4.0, 10, 1.2, 3.5, 0.1, 0.5, 0.2};
    long primary_pe = 5;
    long anode_e = simulate_cascade_c(&cfg, primary_pe);

    printf("=== [C] Симуляція імпульсу ФЕУ та CFD ===\n");
    printf("Первинні фотоелектрони: %ld\n", primary_pe);
    printf("Анодний заряд: %ld электронів\n", anode_e);

    int num_samples = 250;
    double voltage[250];
    generate_pulse_c(&cfg, anode_e, 25.0, voltage, num_samples);

    double cfd_time = find_cfd_zero_crossing_c(&cfg, voltage, num_samples);
    printf("CFD час прильоту: %.3f нс\n", cfd_time);

    printf("\nПерші 5 відліків напруги (мВ):\n");
    for (int i = 0; i < 5; ++i) {
        printf("t = %.1f нс: %.2f мВ\n", (double)i * cfg.dt_ns, voltage[i]);
    }

    return 0;
}
```
:::
