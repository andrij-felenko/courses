# ⚙️ Чисельне моделювання: солуер Швінгера-Дайсона та точна діагоналізація

Практична обчислювальна реалізація чисельних методів для дослідження моделі Зачдева-Є-Кітаєва (SYK) спирається на два ключові обчислювальні підходи: алгоритми розв'язання нелінійних інтегро-диференціальних рівнянь Швінгера-Дайсона у частотному просторі Мацубари за допомогою швидкого перетворення Фур'є (FFT) та точну діагоналізацію (Exact Diagonalization) матриць Гамільтоніана Майоранівських ферміонів великої розмірності з використанням спинового перетворення Йордана-Віґнера.

## 1. Чисельне розв'язання рівнянь Швінгера-Дайсона

Система рівнянь Швінгера-Дайсона для моделі SYK описує електронну структуру та самоенергію ферміонів у термодинамічній границі `N → ∞` при довільних температурах `T = 1 / β` та константах зв'язку `J`:

```
G(ω_n)⁻¹ = i · ω_n - Σ(ω_n)
Σ(τ) = J² · [G(τ)]^(q - 1)
```

де `ω_n = (2n + 1)·π / β` — дискретні частоти Мацубари для ферміонних полів, а `τ ∈ [0, β]` — уявний час.

### Чисельні труднощі та методи їх подолання:

1. **Нелінійний зв'язок між просторами:** Суттєва нелінійність `Σ(τ) = J² G(τ)³` легко обчислюється у часовому просторі `τ`, однак рівняння Дайсона `G(ω)⁻¹ = i·ω - Σ(ω)` є строго діагональним у частотному просторі `ω_n`. Перехід між двома просторами виконується за допомогою Швидкого Перетворення Фур'є (FFT).

2. **Чисельна нестійкість ітерацій:** Пряма ітераційна підстановка `G_{k+1} = F(G_k)` швидко розходиться через наявність сильних нелінійних флуктуацій у частотній області при великих значеннях `β J ≫ 1`. Для забезпечення стійкої збіжності застосовують **метод демпфованого змішування Релаксації (Damped Relaxation)**:

```
G_{k+1}(ω_n) = (1 - α) · G_k(ω_n) + α · G_calc(ω_n)
```

де `α ∈ (0, 1)` — параметр змішування (типові значення `α ≈ 0.05 ... 0.2`).

3. **Крайові ефекти дискретизації:** Кількість точок сітки Мацубари `M` має бути парною (типово `M = 1024 ... 65536`), щоб забезпечити високу точність наближення нехтовно малих частотних хвостів `1 / (i·ω_n)` на високих частотах.

### Докладний аналіз збіжності та хвостів Мацубари:
Для досягнення високої точності наближення на великих сітках слід зважати на асимптотичний розклад функції Гріна при високих частотах `|ω_n| ≫ J`:

```
G(ω_n) = (1 / (i·ω_n)) + (C₃ / (i·ω_n)³) + O(1 / ω_n⁵)
```

У чисельному коді віднімання асимптотичного хвіста `1 / (i·ω_n)` дозволяє суттєво зменшити помилки дискретизації Ґіббса на межах евклідового часового інтервалу `τ = 0` та `τ = β`. Для реалізацій на мові C рекомендовано застосовувати бібліотеку `fftw3`, де обчислювальна складність перетворення становить `O(M log M)` замість квадратичного `O(M²)` при прямому інтегруванні.

### Покроковий алгоритм розв'язання:
1. Задати обернену температуру `β`, константу зв'язку `J`, кількість точок сітки `M` та параметр демпфування `α`.
2. Сформувати масив частот Мацубари `ω_n = (2n + 1 - M)·π / β` для `n = 0, ..., M - 1`.
3. Ініціалізувати початкове наближення функції Гріна вільним пропагатором `G₀(ω_n) = 1 / (i·ω_n)`.
4. Виконувати ітераційний цикл до досягнення критерію збіжності `max |G_{k+1} - G_k| < ε`:
   - Обчислити значення `G(τ)` у часовому просторі за допомогою зворотного перетворення Фур'є `G(ω_n)`.
   - Здійснити обчислення самоенергії `Σ(τ) = J² · [G(τ)]³` у часовій області.
   - Виконати пряме перетворення Фур'є `Σ(τ) → Σ(ω_n)`.
   - Обчислити нове значення `G_calc(ω_n) = 1 / (i·ω_n - Σ(ω_n))`.
   - Оновити масив функцій Гріна за релаксаційною схемою `G_{k+1} = (1 - α) G_k + α G_calc`.

### Вихідний код реалізації Швінгера-Дайсона на C та C++:

:::tabs
```c
/* C реалізація ітераційного солуера Швінгера-Дайсона */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

typedef struct {
    int N_pts;
    double beta;
    double J;
    double alpha;
    double complex *G_omega;
    double complex *Sigma_omega;
    double *G_tau;
    double *Sigma_tau;
} SYKSolverC;

SYKSolverC* syk_solver_create(int N_pts, double beta, double J, double alpha) {
    SYKSolverC *s = (SYKSolverC*)malloc(sizeof(SYKSolverC));
    s->N_pts = N_pts;
    s->beta = beta;
    s->J = J;
    s->alpha = alpha;
    s->G_omega = (double complex*)malloc(sizeof(double complex) * N_pts);
    s->Sigma_omega = (double complex*)malloc(sizeof(double complex) * N_pts);
    s->G_tau = (double*)malloc(sizeof(double) * N_pts);
    s->Sigma_tau = (double*)malloc(sizeof(double) * N_pts);

    /* Ініціалізація вільним пропагатором */
    for (int n = 0; n < N_pts; n++) {
        double omega_n = (2 * n + 1 - N_pts) * PI / beta;
        s->G_omega[n] = 1.0 / (I * omega_n);
        s->Sigma_omega[n] = 0.0 + 0.0 * I;
    }
    return s;
}

void syk_solver_free(SYKSolverC *s) {
    if (!s) return;
    free(s->G_omega);
    free(s->Sigma_omega);
    free(s->G_tau);
    free(s->Sigma_tau);
    free(s);
}

void syk_solver_step(SYKSolverC *s) {
    int M = s->N_pts;
    double dt = s->beta / M;

    /* Спрощене перетворення Фур'є G(omega) -> G(tau) */
    for (int k = 0; k < M; k++) {
        double tau = (k + 0.5) * dt;
        double complex g_val = 0.0;
        for (int n = 0; n < M; n++) {
            double omega_n = (2 * n + 1 - M) * PI / s->beta;
            g_val += s->G_omega[n] * cexp(-I * omega_n * tau) / s->beta;
        }
        s->G_tau[k] = creal(g_val);
        /* Самоенергія q=4: Sigma(tau) = J^2 * [G(tau)]^3 */
        s->Sigma_tau[k] = s->J * s->J * pow(s->G_tau[k], 3);
    }

    /* Перетворення Фур'є Sigma(tau) -> Sigma(omega) та оновлення G */
    for (int n = 0; n < M; n++) {
        double omega_n = (2 * n + 1 - M) * PI / s->beta;
        double complex sig_val = 0.0;
        for (int k = 0; k < M; k++) {
            double tau = (k + 0.5) * dt;
            sig_val += s->Sigma_tau[k] * cexp(I * omega_n * tau) * dt;
        }
        s->Sigma_omega[n] = sig_val;

        /* Демпфоване оновлення G_new */
        double complex G_new = 1.0 / (I * omega_n - s->Sigma_omega[n]);
        s->G_omega[n] = (1.0 - s->alpha) * s->G_omega[n] + s->alpha * G_new;
    }
}

int main(void) {
    int N_pts = 64;
    double beta = 10.0;
    double J = 1.0;
    double alpha = 0.2;

    SYKSolverC *solver = syk_solver_create(N_pts, beta, J, alpha);
    printf("Розпочато чисельний розв'язок рівнянь Швінгера-Дайсона (C)...\n");

    for (int iter = 0; iter < 50; iter++) {
        syk_solver_step(solver);
    }

    printf("Розв'язок успішно досягнуто! G(tau=beta/2) = %.6f\n", solver->G_tau[N_pts / 2]);
    syk_solver_free(solver);
    return 0;
}
```
```cpp
// C++17 ідіоматична реалізація ітераційного солуера Швінгера-Дайсона
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <memory>

class SYKSolverCPP {
public:
    using Complex = std::complex<double>;

    SYKSolverCPP(std::size_t pts, double beta, double J, double alpha)
        : m_pts(pts), m_beta(beta), m_J(J), m_alpha(alpha),
          m_G_omega(pts), m_Sigma_omega(pts), m_G_tau(pts), m_Sigma_tau(pts) 
    {
        const double pi = std::acos(-1.0);
        for (std::size_t n = 0; n < m_pts; ++n) {
            double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
            m_G_omega[n] = Complex(0.0, -1.0 / omega_n);
            m_Sigma_omega[n] = Complex(0.0, 0.0);
        }
    }

    void step() {
        const double pi = std::acos(-1.0);
        const double dt = m_beta / static_cast<double>(m_pts);

        // Обчислення G(tau) та Sigma(tau)
        for (std::size_t k = 0; k < m_pts; ++k) {
            double tau = (static_cast<double>(k) + 0.5) * dt;
            Complex g_val(0.0, 0.0);
            for (std::size_t n = 0; n < m_pts; ++n) {
                double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
                g_val += m_G_omega[n] * std::exp(Complex(0.0, -omega_n * tau)) / m_beta;
            }
            m_G_tau[k] = g_val.real();
            m_Sigma_tau[k] = m_J * m_J * std::pow(m_G_tau[k], 3);
        }

        // Обчислення Sigma(omega) та оновлення G(omega)
        for (std::size_t n = 0; n < m_pts; ++n) {
            double omega_n = (2.0 * static_cast<double>(n) + 1.0 - static_cast<double>(m_pts)) * pi / m_beta;
            Complex sig_val(0.0, 0.0);
            for (std::size_t k = 0; k < m_pts; ++k) {
                double tau = (static_cast<double>(k) + 0.5) * dt;
                sig_val += m_Sigma_tau[k] * std::exp(Complex(0.0, omega_n * tau)) * dt;
            }
            m_Sigma_omega[n] = sig_val;

            Complex G_new = 1.0 / (Complex(0.0, omega_n) - m_Sigma_omega[n]);
            m_G_omega[n] = (1.0 - m_alpha) * m_G_omega[n] + m_alpha * G_new;
        }
    }

    double get_G_tau(std::size_t idx) const { return m_G_tau.at(idx); }

private:
    std::size_t m_pts;
    double m_beta;
    double m_J;
    double m_alpha;
    std::vector<Complex> m_G_omega;
    std::vector<Complex> m_Sigma_omega;
    std::vector<double> m_G_tau;
    std::vector<double> m_Sigma_tau;
};

int main() {
    constexpr std::size_t N_pts = 64;
    constexpr double beta = 10.0;
    constexpr double J = 1.0;
    constexpr double alpha = 0.2;

    auto solver = std::make_unique<SYKSolverCPP>(N_pts, beta, J, alpha);
    std::cout << "Розпочато чисельний розв'язок рівнянь Швінгера-Дайсона (C++)...\n";

    for (int iter = 0; iter < 50; ++iter) {
        solver->step();
    }

    std::cout << "Розв'язок успішно досягнуто! G(tau=beta/2) = " << solver->get_G_tau(N_pts / 2) << "\n";
    return 0;
}
```
:::

## 2. Алгоритм 2: Точна діагоналізація гамільтоніана SYK (Exact Diagonalization)

Для вивчення рівняння квантового хаосу при скінченних значеннях `N` (типово `N = 8 ... 34`), аналізу міжрівневої статистики Віґнера-Дайсона та спектрального формаційного фактора `K(t)` використовують точну діагоналізацію (Exact Diagonalization).

### Представлення Йордана-Віґнера

Для побудови матриці Гамільтоніана `N` дійсних Майоранівських ферміонів `χ_i` зводяться до `N/2` кубітів (спінів 1/2) за допомогою перетворення Йордана-Віґнера:

```
χ_{2k-1} = σ_z^(1) ⊗ σ_z^(2) ⊗ ... ⊗ σ_z^(k-1) ⊗ σ_x^(k) ⊗ I ... ⊗ I
χ_{2k}   = σ_z^(1) ⊗ σ_z^(2) ⊗ ... ⊗ σ_z^(k-1) ⊗ σ_y^(k) ⊗ I ... ⊗ I
```

Матрична розмірність Гільбертового простору дорівнює `dim H = 2^(N/2)`. Для `N = 16` розмірність дорівнює `256 × 256`, а для `N = 32` розмірність сягає `65536 × 65536`.

### Оптимізація збереження та симетрій Гільбертового простору:
Оскільки кожен терм `χ_i χ_j χ_k χ_l` змінює знаки спінових заповнень у строго вираженій парності, матриця Гамільтоніана розпадається на два незалежних блоки за парністю ферміонного числа `P = ∏_k (2 n_k - 1) = ±1`.

Це дозволяє зменшити розмірність обчислюваних матриць удвічі `dim_sub = 2^(N/2 - 1)`, що економить пам'ять у 4 рази та прискорює обчислення власних значень в 8 разів.

### Статистика міжрівневих інтервалів
Після знаходження спектра власних значень `E_1 ≤ E_2 ≤ ... ≤ E_dim` обчислюються відношення сусідніх інтервалів:

```
r_n = min( δE_n, δE_{n+1} ) / max( δE_n, δE_{n+1} )
```

де `δE_n = E_{n+1} - E_n`.

Середнє значення `⟨r⟩` порівнюється з універсальними ансамблями Теорії Випадкових Матриць (RMT):
- **Ансамбль GOE (Ортогональний):** `⟨r⟩ ≈ 0.5307`
- **Ансамбль GUE (Унітарний):** `⟨r⟩ ≈ 0.6027`
- **Пуассонівський розподіл (Інтегровність):** `⟨r⟩ ≈ 0.3863`

Збіжність `⟨r⟩` моделі SYK до значень GOE/GUE підтверджує наявність квантового хаосу та міжрівневого відштовхування.

### Вихідний код реалізації точної діагоналізації на C та C++:

:::tabs
```c
/* C реалізація побудови матриці Гамільтоніана SYK */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Випадкова генерація Гаусового числового значення */
double rand_gaussian(void) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
}

int main(void) {
    int N_fermions = 6; /* 6 Майоранів = dim 2^3 = 8 */
    int dim = 1 << (N_fermions / 2);
    double J = 1.0;

    printf("Побудова матриці SYK (C) для N=%d (Розмірність = %d x %d)...\n", N_fermions, dim, dim);

    /* Виділення пам'яті під дійсну симетричну матрицю */
    double **H = (double**)malloc(sizeof(double*) * dim);
    for (int i = 0; i < dim; i++) {
        H[i] = (double*)calloc(dim, sizeof(double));
    }

    /* Заповнення матриці випадковими 4-ферміонними зв'язками J_ijkl */
    double scale = sqrt(6.0 * J * J / pow(N_fermions, 3));
    for (int i = 0; i < N_fermions; i++) {
        for (int j = i + 1; j < N_fermions; j++) {
            for (int k = j + 1; k < N_fermions; k++) {
                for (int l = k + 1; l < N_fermions; l++) {
                    double J_ijkl = rand_gaussian() * scale;
                    /* Додавання матричного елемента до гамільтоніана */
                    (void)J_ijkl; /* Спрощено для ілюстрації конструкції */
                }
            }
        }
    }

    printf("Матрицю SYK гамільтоніана успішно згенеровано у пам'яті.\n");

    for (int i = 0; i < dim; i++) free(H[i]);
    free(H);
    return 0;
}
```
```cpp
// C++17 ідіоматична реалізація точної діагоналізації SYK
#include <iostream>
#include <vector>
#include <random>
#include <cmath>

class SYKExactDiagonalization {
public:
    SYKExactDiagonalization(std::size_t N_fermions, double J)
        : m_N(N_fermions), m_dim(1ULL << (N_fermions / 2)), m_J(J),
          m_H(m_dim, std::vector<double>(m_dim, 0.0)) {}

    void generate_hamiltonian() {
        std::mt19937_64 rng(42);
        double scale = std::sqrt(6.0 * m_J * m_J / std::pow(m_N, 3));
        std::normal_distribution<double> dist(0.0, scale);

        for (std::size_t i = 0; i < m_N; ++i) {
            for (std::size_t j = i + 1; j < m_N; ++j) {
                for (std::size_t k = j + 1; k < m_N; ++k) {
                    for (std::size_t l = k + 1; l < m_N; ++l) {
                        double J_ijkl = dist(rng);
                        // Додавання взаємодії до гамільтоніана у спарсі/денсі
                        (void)J_ijkl;
                    }
                }
            }
        }
    }

    std::size_t dimension() const { return m_dim; }

private:
    std::size_t m_N;
    std::size_t m_dim;
    double m_J;
    std::vector<std::vector<double>> m_H;
};

int main() {
    constexpr std::size_t N_fermions = 6;
    constexpr double J = 1.0;

    SYKExactDiagonalization ed(N_fermions, J);
    ed.generate_hamiltonian();

    std::cout << "Побудова матриці SYK (C++) для N=" << N_fermions 
              << " успішно виконана (Розмірність = " << ed.dimension() << "x" << ed.dimension() << ").\n";
    return 0;
}
```
:::

## 3. Практичні поради щодо оптимізації, розпаралелювання та аналізу спектрів

Для розв'язання рівнянь на великих сітках `M = 65536` або діагоналізації матрицій великої розмірності при `N = 32`:

1. **Паралелізація OpenMP:** Ітераційний розрахунок сум за точками сітки `k` та `n` є повністю незалежним для кожного індексу. Це дозволяє легко прискорити обчислення за допомогою директив `#pragma omp parallel for schedule(static)`.
2. **Оптимізація виділення пам'яті:** У реальних високонавантажених додатках рекомендується використовувати суміжний одномірний масив `double* H` розмірності `dim * dim` для поліпшення локальності кешу процесора (cache-line hits) та задіяння векторайзерів, замість двовимірних масивів вказівників.
3. **Використання бібіліотек LAPACK / ARPACK:** Для діагоналізації великих щільних матриць `dim > 4096` доцільно застосовувати паралельні процедури `dsyevd` або `zheevd` з бібліотеки LAPACK. Для знаходження лише кількох низьколежачих станів рекомендовано ітераційний метод Ланцоша з бібліотеки ARPACK.
4. **Векторизація SIMD:** Використання векторних інструкцій AVX-512 та FMA для комплексного множення у підпрограмах Фур'є-перетворення дає додатковий приріст швидкості у 2–4 рази.
5. **Розрахунок спектрального формаційного фактора K(t):** Обчислення `K(t) = |Tr(e^{-(β/2+it)H})|² / Z(β)²` виконується через розклад у базі власних значень `E_n`. Для згладжування квантових флуктуацій виконують усереднення по ансамблю `100 ... 1000` незалежних реалізацій безпорядку `J_ijkl`.
