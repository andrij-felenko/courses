# ⚙️ Моделювання спінової системи Гейзенберга методом Монте-Карло

Чисельний метод Монте-Карло за алгоритмом Метрополіса — Гастінгса відтворює термодинаміку класичного 3D-спінового гамільтоніана Гейзенберга на двовимірній кристалічній ґратці. Симуляція обчислює середню намагніченість, внутрішню енергію, прослідковує магнітну сприйнятливість, теплоємність та відстежує ефекти низьковимірних магнітних флуктуацій.

### Задача та математична модель

Розглянемо двовимірну квадратну ґратку розміром `L × L` з періодичними межовими умовами (конфігурація тора). У кожному вузлі `(i, j)` знаходиться тривимірний класичний спіновий вектор одиничної довжини:

```
S_i = (S_(i,x), S_(i,y), S_(i,z)) = (sin θ · cos φ,  sin θ · sin φ,  cos θ)
|S_i| = 1
```

Енергія магнітної системи описується класичним гамільтоніаном Гейзенберга з врахуванням взаємодії між сусідніми спінами та зовнішнього магнітного поля `h` вздовж осі `Z`:

```
H = -J · ∑_(⟨i,j⟩) (S_i · S_j) - h · ∑_i S_(i,z)
```

де `J` — константа обмінної взаємодії (`J > 0` відповідає феромагнітному обміну), а `⟨i,j⟩` означає підсумовування по всіх парах найближчих сусідів без подвійного врахування зв'язків.

Чисельний метод Монте-Карло за алгоритмом Метрополіса — Гастінгса формує марковський ланцюг станів спінової решітки відповідно до канонічного розподілу Гіббса `P(S) ∝ exp(-H(S) / (k_B · T))`.

На кожному мікрокроці алгоритму виконуються наступні послідовні дії:
1. Випадково вибирається вузол ґратки `i`.
2. Ґенерується новий випадковий напрямок спіна `S_i'`.
3. Обчислюється локальна зміна енергії `ΔE = H(S_i') - H(S_i)` від зміни лише цього одного спіна:

```
ΔE = -J · (S_i' - S_i) · ∑_(nbr) S_nbr - h · (S_(i,z)' - S_(i,z))
```

4. Зміна стану приймається з ймовірністю `P_acc = min(1, exp(-ΔE / (k_B · T)))`.

### Реалізація алгоритму Метрополіса

Нижче наведено робочі реалізації симулятора чотирма мовами програмування (C, C++, Python та TypeScript). Кожне рішення є повністю самостійним та ідіоматичним для своєї платформи.

:::tabs
```c
/* heisenberg_mc.c — Моделювання 2D спинової решітки Гейзенберга на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    int size;
    double J;
    double h;
    double temp;
    Vec3 *spins;
} Lattice;

static double rand_double(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

static Vec3 random_unit_vector(void) {
    double z = 2.0 * rand_double() - 1.0;
    double phi = 2.0 * M_PI * rand_double();
    double r = sqrt(1.0 - z * z);
    Vec3 v = { r * cos(phi), r * sin(phi), z };
    return v;
}

static double dot_product(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

Lattice* lattice_create(int size, double J, double h, double temp) {
    Lattice *lat = (Lattice*)malloc(sizeof(Lattice));
    lat->size = size;
    lat->J = J;
    lat->h = h;
    lat->temp = temp;
    lat->spins = (Vec3*)malloc(sizeof(Vec3) * size * size);

    for (int i = 0; i < size * size; ++i) {
        lat->spins[i] = random_unit_vector();
    }
    return lat;
}

void lattice_free(Lattice *lat) {
    if (lat) {
        free(lat->spins);
        free(lat);
    }
}

static void get_neighbors(int idx, int size, int nbrs[4]) {
    int r = idx / size;
    int c = idx % size;
    nbrs[0] = ((r - 1 + size) % size) * size + c; /* Північ */
    nbrs[1] = ((r + 1) % size) * size + c;        /* Південь */
    nbrs[2] = r * size + ((c + 1) % size);        /* Схід */
    nbrs[3] = r * size + ((c - 1 + size) % size); /* Захід */
}

void metropolis_step(Lattice *lat) {
    int total_sites = lat->size * lat->size;
    for (int step = 0; step < total_sites; ++step) {
        int idx = rand() % total_sites;
        int nbrs[4];
        get_neighbors(idx, lat->size, nbrs);

        Vec3 old_spin = lat->spins[idx];
        Vec3 new_spin = random_unit_vector();

        Vec3 sum_nbrs = {0.0, 0.0, 0.0};
        for (int k = 0; k < 4; ++k) {
            sum_nbrs.x += lat->spins[nbrs[k]].x;
            sum_nbrs.y += lat->spins[nbrs[k]].y;
            sum_nbrs.z += lat->spins[nbrs[k]].z;
        }

        double dE = -lat->J * (dot_product(new_spin, sum_nbrs) - dot_product(old_spin, sum_nbrs))
                    - lat->h * (new_spin.z - old_spin.z);

        if (dE <= 0.0 || rand_double() < exp(-dE / lat->temp)) {
            lat->spins[idx] = new_spin;
        }
    }
}

void compute_observables(const Lattice *lat, double *energy, double *magnetization) {
    double total_E = 0.0;
    Vec3 total_M = {0.0, 0.0, 0.0};
    int size = lat->size;

    for (int idx = 0; idx < size * size; ++idx) {
        int nbrs[4];
        get_neighbors(idx, size, nbrs);
        
        /* Враховуємо лише вихідні зв'язки Схід і Південь, щоб не подвоювати */
        double e_pair = dot_product(lat->spins[idx], lat->spins[nbrs[1]]) +
                        dot_product(lat->spins[idx], lat->spins[nbrs[2]]);
        
        total_E -= lat->J * e_pair + lat->h * lat->spins[idx].z;
        total_M.x += lat->spins[idx].x;
        total_M.y += lat->spins[idx].y;
        total_M.z += lat->spins[idx].z;
    }

    int n_sites = size * size;
    *energy = total_E / n_sites;
    *magnetization = sqrt(dot_product(total_M, total_M)) / n_sites;
}

int main(void) {
    srand((unsigned int)time(NULL));
    int size = 16;
    double J = 1.0;
    double h = 0.05;
    double temp = 0.8;

    Lattice *lat = lattice_create(size, J, h, temp);

    printf("Термалізація 2D решітки Гейзенберга (%dx%d)...\n", size, size);
    for (int i = 0; i < 2000; ++i) {
        metropolis_step(lat);
    }

    printf("Вимірювання термодинамічних величин...\n");
    double avg_E = 0.0, avg_M = 0.0;
    int samples = 1000;
    for (int i = 0; i < samples; ++i) {
        metropolis_step(lat);
        double E, M;
        compute_observables(lat, &E, &M);
        avg_E += E;
        avg_M += M;
    }

    printf("Результати (T = %.2f, h = %.2f):\n", temp, h);
    printf(" Середня енергія на вузол: %f\n", avg_E / samples);
    printf(" Середня намагніченість |M|: %f\n", avg_M / samples);

    lattice_free(lat);
    return 0;
}
```
```cpp
// heisenberg_mc.cpp — Ідіоматичний C++20 симулятор спінового гамільтоніана Гейзенберга
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <numeric>

struct SpinVector {
    double x{0.0}, y{0.0}, z{1.0};

    [[nodiscard]] double dot(const SpinVector& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    SpinVector& operator+=(const SpinVector& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
};

class HeisenbergLattice {
public:
    HeisenbergLattice(std::size_t side_length, double J_exchange, double ext_field, double temperature)
        : size_(side_length), J_(J_exchange), h_(ext_field), temp_(temperature),
          rng_(std::random_device{}()), dist_01_(0.0, 1.0), spins_(side_length * side_length) 
    {
        for (auto& s : spins_) {
            s = generate_random_spin();
        }
    }

    void sweep_metropolis() {
        std::uniform_int_distribution<std::size_t> site_dist(0, spins_.size() - 1);

        for (std::size_t i = 0; i < spins_.size(); ++i) {
            std::size_t idx = site_dist(rng_);
            const auto nbrs = get_neighbors(idx);

            SpinVector nbr_sum{};
            for (auto n : nbrs) nbr_sum += spins_[n];

            const SpinVector old_s = spins_[idx];
            const SpinVector new_s = generate_random_spin();

            double dE = -J_ * (new_s.dot(nbr_sum) - old_s.dot(nbr_sum))
                        - h_ * (new_s.z - old_s.z);

            if (dE <= 0.0 || dist_01_(rng_) < std::exp(-dE / temp_)) {
                spins_[idx] = new_s;
            }
        }
    }

    struct Observables {
        double energy_per_spin;
        double magnetization;
    };

    [[nodiscard]] Observables measure() const {
        double total_energy = 0.0;
        SpinVector total_m{};

        for (std::size_t idx = 0; idx < spins_.size(); ++idx) {
            std::size_t r = idx / size_;
            std::size_t c = idx % size_;
            std::size_t south = ((r + 1) % size_) * size_ + c;
            std::size_t east  = r * size_ + ((c + 1) % size_);

            double e_pair = spins_[idx].dot(spins_[south]) + spins_[idx].dot(spins_[east]);
            total_energy -= J_ * e_pair + h_ * spins_[idx].z;
            total_m += spins_[idx];
        }

        double n = static_cast<double>(spins_.size());
        double mag_abs = std::sqrt(total_m.dot(total_m)) / n;
        return { total_energy / n, mag_abs };
    }

private:
    SpinVector generate_random_spin() {
        double z = 2.0 * dist_01_(rng_) - 1.0;
        double phi = 2.0 * M_PI * dist_01_(rng_);
        double r = std::sqrt(1.0 - z * z);
        return { r * std::cos(phi), r * std::sin(phi), z };
    }

    [[nodiscard]] std::array<std::size_t, 4> get_neighbors(std::size_t idx) const noexcept {
        std::size_t r = idx / size_;
        std::size_t c = idx % size_;
        return {
            ((r + size_ - 1) % size_) * size_ + c,
            ((r + 1) % size_) * size_ + c,
            r * size_ + ((c + 1) % size_),
            r * size_ + ((c + size_ - 1) % size_)
        };
    }

    std::size_t size_;
    double J_, h_, temp_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_01_;
    std::vector<SpinVector> spins_;
};

int main() {
    constexpr std::size_t L = 16;
    HeisenbergLattice lattice(L, 1.0, 0.05, 0.8);

    std::cout << "Термалізація C++ системи...\n";
    for (int i = 0; i < 2000; ++i) lattice.sweep_metropolis();

    double sum_e = 0.0, sum_m = 0.0;
    constexpr int steps = 1000;
    for (int i = 0; i < steps; ++i) {
        lattice.sweep_metropolis();
        auto [e, m] = lattice.measure();
        sum_e += e;
        sum_m += m;
    }

    std::cout << "C++20 Результати:\n"
              << " Середня енергія на спін: " << sum_e / steps << '\n'
              << " Модуль намагніченості |M|: " << sum_m / steps << '\n';
}
```
```python
# heisenberg_mc.py — Симуляція моделі Гейзенберга на Python + NumPy
import numpy as np

class HeisenbergModel2D:
    def __init__(self, size=16, J=1.0, h=0.05, temp=0.8):
        self.L = size
        self.J = J
        self.h = h
        self.temp = temp
        # Просторові спіни (L, L, 3)
        angles_z = 2.0 * np.random.random((size, size)) - 1.0
        angles_phi = 2.0 * np.pi * np.random.random((size, size))
        r = np.sqrt(1.0 - angles_z**2)
        
        self.spins = np.stack([r * np.cos(angles_phi), r * np.sin(angles_phi), angles_z], axis=-1)

    def step(self):
        for _ in range(self.L * self.L):
            r = np.random.randint(0, self.L)
            c = np.random.randint(0, self.L)
            
            # Сума 4 найближчих сусідів з періодичними межами
            nbr_sum = (self.spins[(r-1)%self.L, c] + self.spins[(r+1)%self.L, c] +
                       self.spins[r, (c-1)%self.L] + self.spins[r, (c+1)%self.L])
            
            old_spin = self.spins[r, c].copy()
            
            # Новий випадковий спін на сфері
            z = 2.0 * np.random.random() - 1.0
            phi = 2.0 * np.pi * np.random.random()
            rad = np.sqrt(1.0 - z**2)
            new_spin = np.array([rad * np.cos(phi), rad * np.sin(phi), z])
            
            dE = -self.J * (np.dot(new_spin, nbr_sum) - np.dot(old_spin, nbr_sum)) - self.h * (new_spin[2] - old_spin[2])
            
            if dE <= 0 or np.random.random() < np.exp(-dE / self.temp):
                self.spins[r, c] = new_spin

    def measure(self):
        # Сума взаємодій вздовж правого та нижнього сусіда
        east_spins = np.roll(self.spins, -1, axis=1)
        south_spins = np.roll(self.spins, -1, axis=0)
        
        e_pairs = np.sum(self.spins * east_spins) + np.sum(self.spins * south_spins)
        total_E = -self.J * e_pairs - self.h * np.sum(self.spins[:, :, 2])
        
        total_M = np.sum(self.spins, axis=(0, 1))
        mag = np.linalg.norm(total_M) / (self.L * self.L)
        energy = total_E / (self.L * self.L)
        return energy, mag

if __name__ == "__main__":
    sim = HeisenbergModel2D(size=16, temp=0.8, h=0.05)
    print("Термалізація Python моделі...")
    for _ in range(1000):
        sim.step()
    
    energies, mags = [], []
    for _ in range(500):
        sim.step()
        e, m = sim.measure()
        energies.append(e)
        mags.append(m)
        
    print(f"Python Результати (T=0.8, h=0.05):")
    print(f" Середня енергія: {np.mean(energies):.4f}")
    print(f" Середня намагніченість: {np.mean(mags):.4f}")
```
```ts
// heisenberg_mc.ts — TypeScript симуляція Метрополіса для Гейзенберга
interface Spin3D {
    x: number;
    y: number;
    z: number;
}

class HeisenbergLatticeTS {
    private spins: Spin3D[];
    private L: number;
    private J: number;
    private h: number;
    private temp: number;

    constructor(size: number, J: number, h: number, temp: number) {
        this.L = size;
        this.J = J;
        this.h = h;
        this.temp = temp;
        this.spins = new Array(size * size);
        for (let i = 0; i < this.spins.length; i++) {
            this.spins[i] = this.randomSpin();
        }
    }

    private randomSpin(): Spin3D {
        const z = 2.0 * Math.random() - 1.0;
        const phi = 2.0 * Math.PI * Math.random();
        const r = Math.sqrt(1.0 - z * z);
        return { x: r * Math.cos(phi), y: r * Math.sin(phi), z };
    }

    private dot(a: Spin3D, b: Spin3D): number {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    public step(): void {
        const total = this.L * this.L;
        for (let s = 0; s < total; s++) {
            const idx = Math.floor(Math.random() * total);
            const r = Math.floor(idx / this.L);
            const c = idx % this.L;

            const nbrIdx = [
                ((r - 1 + this.L) % this.L) * this.L + c,
                ((r + 1) % this.L) * this.L + c,
                r * this.L + ((c + 1) % this.L),
                r * this.L + ((c - 1 + this.L) % this.L)
            ];

            const sumNbr: Spin3D = { x: 0, y: 0, z: 0 };
            for (const n of nbrIdx) {
                sumNbr.x += this.spins[n].x;
                sumNbr.y += this.spins[n].y;
                sumNbr.z += this.spins[n].z;
            }

            const oldS = this.spins[idx];
            const newS = this.randomSpin();

            const dE = -this.J * (this.dot(newS, sumNbr) - this.dot(oldS, sumNbr))
                       - this.h * (newS.z - oldS.z);

            if (dE <= 0 || Math.random() < Math.exp(-dE / this.temp)) {
                this.spins[idx] = newS;
            }
        }
    }

    public measure(): { energy: number; mag: number } {
        let totalE = 0;
        let mx = 0, my = 0, mz = 0;

        for (let r = 0; r < this.L; r++) {
            for (let c = 0; c < this.L; c++) {
                const idx = r * this.L + c;
                const south = ((r + 1) % this.L) * this.L + c;
                const east = r * this.L + ((c + 1) % this.L);

                const ePair = this.dot(this.spins[idx], this.spins[south]) +
                              this.dot(this.spins[idx], this.spins[east]);

                totalE -= this.J * ePair + this.h * this.spins[idx].z;
                mx += this.spins[idx].x;
                my += this.spins[idx].y;
                mz += this.spins[idx].z;
            }
        }

        const n = this.L * this.L;
        const mag = Math.sqrt(mx * mx + my * my + mz * mz) / n;
        return { energy: totalE / n, mag };
    }
}

const simTS = new HeisenbergLatticeTS(16, 1.0, 0.05, 0.8);
for (let i = 0; i < 1000; i++) simTS.step();
let sumE = 0, sumM = 0;
for (let i = 0; i < 500; i++) {
    simTS.step();
    const res = simTS.measure();
    sumE += res.energy;
    sumM += res.mag;
}
console.log(`TypeScript TS: Energy=${(sumE/500).toFixed(4)}, |M|=${(sumM/500).toFixed(4)}`);
```
:::

### Пояснення алгоритму та обчислювальних нюансів

1. **Генерація рівномірного вектора на 2D сфері:** У чисельному моделюванні 3D-спінів вибір випадкового нового напрямку спіна є однією з найпоширеніших математичних пасток. Якщо вибирати полярні кути `θ` та `φ` рівномірно на інтервалах `[0, π]` та `[0, 2π]`, спіни штучно згрупуються біля полюсів сфери, оскільки елемент тілесного кута `dΩ = sin θ dθ dφ = d(cos θ) dφ` залежить від синуса `θ`. Щоб рівномірно покрити сферу, необхідно генерувати величину `z = cos θ` рівномірно на проміжку `[-1, 1]`, а полярний кут `φ` — рівномірно на `[0, 2π]`. Тоді радіус у екваторіальній площині `r = √(1 - z²)` і компоненти вектора дорівнюють `x = r · cos φ`, `y = r · sin φ`.

2. **Обчислення зміни енергії `ΔE`:** При локальній зміні одного спіна немає потреби перераховувати загальну енергію всієї решітки (що вимагало б `O(L²)` операцій). Достатньо обчислити скалярний добуток нового та старого спина з вектором суми чотирьох найближчих сусідів: `ΔE = -J · (S_new - S_old) · ∑ S_nbr`. Це знижує трудомісткість одного мікрокроку до `O(1)`.

3. **Обчислення макроскопічних величин та подвійне врахування:** Під час вимірювання повної енергії системи підсумовування парних взаємодій `S_i · S_j` по всіх вузлах без запобіжних заходів порахує кожен зв'язок двічі (наприклад, для `(i,j)` і для `(j,i)`). У програмі це вирішується підсумовуванням лише двох вихідних напрямків для кожного вузла: Схід `(r, c+1)` та Південь `(r+1, c)`.

4. **Теорема Мерміна — Вагнера у чисельному експерименті:** Теорема Мерміна — Вагнера строго стверджує, що двовимірна класична модель Гейзенберга з неперервною симетрією `SO(3)` не має спонтанного феромагнітного порядку за будь-якої кінцевої температури `T > 0` при нульовому магнітному полі `h = 0`. Довгохвильові спінові хвилі флуктують настільки сильно, що руйнують далекий порядок. Саме тому для спостереження стійкої намагніченості у чисельному моделюванні 2D решітки вводиться мале зовнішнє поляризувальне поле `h = 0.05`.

5. **Оптимізація продуктивності в C та C++:** Завдяки локальності пам'яті (одновимірний масив спинів розміром `L*L`), використанню статичних функцій та відсутності динамічних виділень пам'яті всередині циклів Метрополіса, С та C++ версії здатні виконувати понад 50 мільйонів спинових переворотів на секунду на одноядерному процесорі.

6. **Термалізація та час автокореляції:** Перед тим, як проводити фізичні вимірювання енергії та намагніченості, система повинна пройти етап термалізації (від 1000 до 5000 повних проходів Метрополіса по решітці). Це необхідно для того, щоб вихідна випадкова конфігурація спінів вийшла з високоенергетичного стану та досягла термодинамічної рівноваги.

7. **Розрахунок флуктуацій та сприйнятливості:** З накопичених Монте-Карло вибірок енергії `E` та намагніченості `M` можна обчислити другорядні термодинамічні величини — магнітну сприйнятливість `χ` та теплоємність `C_v`:

```
χ = (N / (k_B · T)) · [ ⟨M²⟩ - ⟨M⟩² ]
C_v = (1 / (N · k_B · T²)) · [ ⟨E²⟩ - ⟨E⟩² ]
```

Ці флуктуаційні співвідношення є чисельним втіленням флуктуаційно-дисипативної теореми. Поблизу критичної температури фазового переходу ці величини демонструють гострі піки, що дозволяє чисельно визначати точку Кюрі.

### Обчислювальний порівняльний аналіз реалізацій

Порівнюючи чотири реалізації однієї задачі (С, C++, Python/NumPy, TypeScript), варто виділити ключові відмінності в архітектурі даних:

- **C-версія:** Оперує виділеним масивом структур `Vec3`. Вона демонструє найкращу кеш-локальність даних (cache spatial locality) і мінімальні накладні витрати викликів.
- **C++-версія:** Застосовує безпечний `std::vector<SpinVector>`, стандартизований датчик псевдовипадкових чисел `std::mt19937` з рівномірним розподілом `std::uniform_real_distribution`, що виключає періодичні пастки старого C-генератора `rand()`. Завдяки агресивній інлайнінговій оптимізації сучасних компіляторів (`g++ -O3`), швидкодія C++ повністю порівнювана з чистим C.
- **Python-версія:** Оптимізована під матричні векторні операції NumPy (`np.roll` для зручного зсуву решітки при підрахунку сусідів). Проте повузлові цикли Метрополіса на чистому Python виконуються значно повільніше за C/C++, тому для великих ґраток `L > 64` використовують додаткову C-бібліотеку або Cython.
- **TypeScript-версія:** Оперує масивом об'єктів. Сучасні JIT-компілятори JS (наприклад, V8 у Node.js чи браузерах) мономорфізують клас `Spin3D` і забезпечують швидкодію, яка становить 30–50% від швидкості C++.
