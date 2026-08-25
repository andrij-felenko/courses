# ⚙️ Чисельне моделювання електричного зсуву та полів на межі діелектриків

Ця практична вставка містить концепцію, математичний алгоритм та повноцінну реалізацію двовимірного чисельного солвера для розрахунку розподілу полів електричного зсуву `D`, напруженості електричного поля `E` та поляризації `P` у складних неоднорідних діелектричних структурах методом скінченних різниць (FDM) та методом послідовної верхньої релаксації (SOR).

---

### 1. Постановка завдання та математична модель

У багатьох інженерних пристроях (наприклад, у друкованих платах із високочастотними провідниками, мікросмужкових фільтрах, планарних конденсаторах та п'єзодатчиках) електричне поле проходить крізь межі кількох матеріалів із різними діелектричними проникностями `ε_r(x,y)`.

Загальне рівняння для електростатичного потенціалу `φ(x,y)` (де `E = - ∇φ`, а `D = ε₀ · ε_r · E`) випливає з теореми Гаусса `∇ · D = ρ_free`:

```
∇ · (ε₀ · ε_r(x,y) · ∇φ(x,y)) = - ρ_free(x,y)   [неоднорідне рівняння Пуассона]
```

Розкриваючи похідні в 2D декартових координатах:

```
∂/∂x [ ε_r(x,y) · ∂φ/∂x ] + ∂/∂y [ ε_r(x,y) · ∂φ/∂y ] = - ρ_free(x,y) / ε₀
```

#### Математична дискретизація на сітці:
Розб'ємо область розрахунку на прямокутну сітку `NX × NY` із однаковим кроком `h = Δx = Δy`. Для кожного внутрішнього вузла сітки `(i, j)` нам потрібно розкласти оператор дивергенції у скінченні різниці. 

Оскільки діелектрична проникність `ε_r(x,y)` змінюється від вузла до вузла і може зазнавати стрибків на межі матеріалів, пряме використання центральних різниць для другого похідного виявилося б нестійким. Замість цього використовують концепцію ефективних діелектричних проникностей на півкроках сітки — між центральним вузлом `(i, j)` та його чотирма сусідами (схід `E`, захід `W`, північ `N`, південь `S`).

Ефективна проникність між вузлами обчислюється як середнє арифметичне або середнє гармонійне:

```
ε_east  = 0.5 * (ε_r[i][j] + ε_r[i+1][j])      [ефективна проникність на східній грані]
ε_west  = 0.5 * (ε_r[i][j] + ε_r[i-1][j])      [ефективна проникність на західній грані]
ε_north = 0.5 * (ε_r[i][j] + ε_r[i][j+1])      [ефективна проникність на північній грані]
ε_south = 0.5 * (ε_r[i][j] + ε_r[i][j-1])      [ефективна проникність на південній грані]
```

Потік вектора електричного зсуву `D` крізь чотири грані контрольного об'єму навколо вузла `(i, j)` записується як:

```
[ ε_east · (φ[i+1][j] - φ[i][j]) - ε_west · (φ[i][j] - φ[i-1][j]) ] / h²
+ [ ε_north · (φ[i][j+1] - φ[i][j]) - ε_south · (φ[i][j] - φ[i][j-1]) ] / h² = - ρ_free[i][j] / ε₀
```

Виражаючи значення потенціалу `φ[i][j]` через значення у сусідніх вузлах:

```
φ[i][j] = [ ε_east · φ[i+1][j] + ε_west · φ[i-1][j] + ε_north · φ[i][j+1] + ε_south · φ[i][j-1] + (h² · ρ_free[i][j] / ε₀) ] / DenOM
```

де `DenOM = ε_east + ε_west + ε_north + ε_south`.

Ця формула автоматично задовольняє граничну умову неперервності нормальної компоненти вектора електричного зсуву `D_1n = D_2n` на довільних межах між діелектриками без додаткового виділення поверхонь!

---

### 2. Алгоритм послідовної верхньої релаксації (SOR) та спектральний радіус

Якщо розв'язувати отриману систему з `N²` рівнянь простим методом ітерацій Якобі або Гаусса — Зейделя, кількість ітерацій для досягнення точності `10⁻⁶` на сітці 100×100 перевищить 40 000 кроків.

Для прискорення використовують метод послідовної верхньої релаксації (SOR, *Successive Over-Relaxation*). Суть метода полягає у проведенні екстраполяції між старим значенням потенціалу та новим цільовим значенням Гаусса — Зейделя `φ_GS`:

```
φ^(k+1)[i][j] = φ^(k)[i][j] + ω · ( φ_GS[i][j] - φ^(k)[i][j] )
```

Коефіцієнт релаксації `ω` вибирається у діапазоні `1.0 < ω < 2.0`. 

Теорія чисельних методів (теорема Янга — Франкеля) стверджує, що для прямокутної сітки `NX × NY` спектральний радіус матриці ітерацій Якобі дорівнює:

```
ρ(B_J) = 0.5 * [ cos(π / NX) + cos(π / NY) ]
```

Тоді оптимальне значення коефіцієнта релаксації `ω_opt` обчислюється за строгою аналітичною формулою:

```
ω_opt = 2 / [ 1 + √(1 - ρ(B_J)²) ]
```

Для сітки розміром 100×100 значення `ρ(B_J) ≈ cos(π / 100) ≈ 0.99951`, звідки `ω_opt ≈ 1.905`. Застосування `ω_opt` зменшує кількість необхідних ітерацій з 40 000 до менш ніж 400 кроків, тобто прискорює розрахунок у 100 разів!

---

### 3. Фізичний розрахунок мікросмужкової лінії (Microstrip Line)

Розглянемо практичну інженерну задачу розрахунку мікросмужкової лінії, яка є основним елементом надвисокочастотних (НВЧ) мікросхем та печатних плат.

Мікросмужкова лінія складається з заземленого металевого екрана ухилу `y = 0`, діелектричної підкладки товщиною `h_sub` із проникністю `ε_r` (наприклад, склотекстоліт FR-4 з `ε_r = 4.4`), та тонкого сигнального провідника шириною `w` на поверхні підкладки, на який подано напругу `V₀ = 100 В`.

```
                    Повітря (ε_r = 1.0)
       ┌───────────────────────────────────────────┐
       │   Сигнальна смужка (+100 В)               │
       │   ───────────────[██████]───────────────   │ (y = h_sub)
       │   Підкладка FR-4 (ε_r = 4.4)               │
       └───────────────────────────────────────────┘
       ============================================= (Заземлення y = 0)
```

Силові лінії електричного поля `E` виходять із сигнальної смужки. Частина ліній іде вниз крізь діелектричну підкладку прямо до заземленої площини. Проте частина силових ліній виходить у верхній напівпростір повітря — це так звані **крайові поля** (*fringe fields*).

Завдяки вектору електричного зсуву `D` ми можемо знайти повний вільний заряд на одиницю довжини смужки `Q_free` проінтегрувавши вектор `D` по замкненому прямокутному контуру, що охоплює смужку:

```
Q_free = ∮_S D · dA                    [повільний заряд на одиницю довжини, Кл/м]
```

Знаючи заряд `Q_free` та напругу `V₀`, обчислюємо погонну ємність лінії `C = Q_free / V₀`, ефективну діелектричну проникність `ε_eff = C / C_vacuum`, та хвильовий опір лінії `Z₀ = 1 / (c · √(C · C_vacuum))`.

---

### 4. Реалізація солвера мовами C та C++

Нижче наведено повноцінні вихідні коди 2D-солвера на C та C++20, які розраховують потенціал `φ`, напруженість `E`, вектор зсуву `D` та поляризацію `P` для мікросмужкової лінії.

:::tabs
```c
/* dielectric_solver.c — Чисельний 2D розв'язувач полів D, E, P методом FDM/SOR на C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define NX 100
#define NY 100
#define EPS0 8.854187817e-12

typedef struct {
    int nx;
    int ny;
    double h;
    double *phi;
    double *eps_r;
    double *rho_free;
    bool *is_boundary;
    double *Ex;
    double *Ey;
    double *Dx;
    double *Dy;
    double *Px;
    double *Py;
} Solver2D;

Solver2D* solver_create(int nx, int ny, double domain_size) {
    Solver2D *s = (Solver2D*)calloc(1, sizeof(Solver2D));
    if (!s) return NULL;

    s->nx = nx;
    s->ny = ny;
    s->h = domain_size / (nx - 1);
    size_t sz = (size_t)nx * ny;

    s->phi = (double*)calloc(sz, sizeof(double));
    s->eps_r = (double*)calloc(sz, sizeof(double));
    s->rho_free = (double*)calloc(sz, sizeof(double));
    s->is_boundary = (bool*)calloc(sz, sizeof(bool));
    s->Ex = (double*)calloc(sz, sizeof(double));
    s->Ey = (double*)calloc(sz, sizeof(double));
    s->Dx = (double*)calloc(sz, sizeof(double));
    s->Dy = (double*)calloc(sz, sizeof(double));
    s->Px = (double*)calloc(sz, sizeof(double));
    s->Py = (double*)calloc(sz, sizeof(double));

    /* Ініціалізація за замовчуванням: вакуум (eps_r = 1.0) */
    for (size_t i = 0; i < sz; i++) {
        s->eps_r[i] = 1.0;
    }
    return s;
}

void solver_destroy(Solver2D *s) {
    if (!s) return;
    free(s->phi);
    free(s->eps_r);
    free(s->rho_free);
    free(s->is_boundary);
    free(s->Ex);
    free(s->Ey);
    free(s->Dx);
    free(s->Dy);
    free(s->Px);
    free(s->Py);
    free(s);
}

static inline int idx(Solver2D *s, int i, int j) {
    return i * s->ny + j;
}

void solver_setup_microstrip(Solver2D *s, double eps_substrate) {
    int nx = s->nx;
    int ny = s->ny;

    /* Нижня половина (j < ny/2): підкладка з проникністю eps_substrate */
    for (int i = 0; i < nx; i++) {
        for (int j = 0; j < ny / 2; j++) {
            s->eps_r[idx(s, i, j)] = eps_substrate;
        }
    }

    /* Заземлена нижня границя (y = 0) */
    for (int i = 0; i < nx; i++) {
        int id = idx(s, i, 0);
        s->phi[id] = 0.0;
        s->is_boundary[id] = true;
    }

    /* Верхня границя (y = NY-1): 0 В */
    for (int i = 0; i < nx; i++) {
        int id = idx(s, i, ny - 1);
        s->phi[id] = 0.0;
        s->is_boundary[id] = true;
    }

    /* Сигнальна смужка на межі діелектриків (j = ny/2, від i = nx/4 до 3*nx/4): +100 В */
    int j_strip = ny / 2;
    for (int i = nx / 4; i <= 3 * nx / 4; i++) {
        int id = idx(s, i, j_strip);
        s->phi[id] = 100.0;
        s->is_boundary[id] = true;
    }
}

double solver_step_sor(Solver2D *s, double omega) {
    double max_diff = 0.0;
    int nx = s->nx;
    int ny = s->ny;
    double h2 = s->h * s->h;

    for (int i = 1; i < nx - 1; i++) {
        for (int j = 1; j < ny - 1; j++) {
            int id = idx(s, i, j);
            if (s->is_boundary[id]) continue;

            double eps_e = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i + 1, j)]);
            double eps_w = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i - 1, j)]);
            double eps_n = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i, j + 1)]);
            double eps_s = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i, j - 1)]);

            double num = eps_e * s->phi[idx(s, i + 1, j)] +
                         eps_w * s->phi[idx(s, i - 1, j)] +
                         eps_n * s->phi[idx(s, i, j + 1)] +
                         eps_s * s->phi[idx(s, i, j - 1)] +
                         (h2 * s->rho_free[id] / EPS0);
            double den = eps_e + eps_w + eps_n + eps_s;
            double phi_target = num / den;

            double diff = fabs(phi_target - s->phi[id]);
            if (diff > max_diff) max_diff = diff;

            s->phi[id] += omega * (phi_target - s->phi[id]);
        }
    }
    return max_diff;
}

void solver_compute_vector_fields(Solver2D *s) {
    int nx = s->nx;
    int ny = s->ny;
    double h2 = 2.0 * s->h;

    for (int i = 1; i < nx - 1; i++) {
        for (int j = 1; j < ny - 1; j++) {
            int id = idx(s, i, j);
            double ex = -(s->phi[idx(s, i + 1, j)] - s->phi[idx(s, i - 1, j)]) / h2;
            double ey = -(s->phi[idx(s, i, j + 1)] - s->phi[idx(s, i, j - 1)]) / h2;

            s->Ex[id] = ex;
            s->Ey[id] = ey;

            double eps = s->eps_r[id];
            s->Dx[id] = EPS0 * eps * ex;
            s->Dy[id] = EPS0 * eps * ey;

            s->Px[id] = s->Dx[id] - EPS0 * ex;
            s->Py[id] = s->Dy[id] - EPS0 * ey;
        }
    }
}

int main(void) {
    Solver2D *s = solver_create(NX, NY, 0.1);
    if (!s) return 1;

    solver_setup_microstrip(s, 4.4); /* FR-4 склотекстоліт eps_r = 4.4 */

    double omega = 1.90;
    int iter;
    for (iter = 0; iter < 5000; iter++) {
        double diff = solver_step_sor(s, omega);
        if (diff < 1e-6) break;
    }

    solver_compute_vector_fields(s);

    int test_i = NX / 2;
    int test_j_sub = NY / 4;     /* Точка в підкладці */
    int test_j_air = 3 * NY / 4; /* Точка в повітрі */

    int id_sub = idx(s, test_i, test_j_sub);
    int id_air = idx(s, test_i, test_j_air);

    printf("Розв'язок збігся за %d ітерацій.\n", iter);
    printf("Точка підкладки FR-4 (eps=4.4): Ey = %.2f В/м, Dy = %.3e Кл/м²\n",
           s->Ey[id_sub], s->Dy[id_sub]);
    printf("Точка повітря (eps=1.0):        Ey = %.2f В/м, Dy = %.3e Кл/м²\n",
           s->Ey[id_air], s->Dy[id_air]);

    solver_destroy(s);
    return 0;
}
```
```cpp
// dielectric_solver.cpp — Об'єктно-орієнтований C++20 розв'язувач полів D, E, P
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <iomanip>
#include <span>
#include <stdexcept>

class DielectricPoissonSolver2D {
public:
    static constexpr double EPS0 = 8.854187817e-12;

    struct FieldPoint {
        double phi;
        double Ex, Ey;
        double Dx, Dy;
        double Px, Py;
    };

    DielectricPoissonSolver2D(size_t nx, size_t ny, double domain_size)
        : nx_(nx), ny_(ny), h_(domain_size / static_cast<double>(nx - 1)),
          phi_(nx * ny, 0.0), eps_r_(nx * ny, 1.0),
          rho_free_(nx * ny, 0.0), is_boundary_(nx * ny, false),
          Ex_(nx * ny, 0.0), Ey_(nx * ny, 0.0),
          Dx_(nx * ny, 0.0), Dy_(nx * ny, 0.0),
          Px_(nx * ny, 0.0), Py_(nx * ny, 0.0) {}

    void setup_microstrip_geometry(double substrate_eps_r, double strip_voltage) {
        for (size_t i = 0; i < nx_; ++i) {
            for (size_t j = 0; j < ny_ / 2; ++j) {
                eps_r_[index(i, j)] = substrate_eps_r;
            }
        }

        // Заземлені грані
        for (size_t i = 0; i < nx_; ++i) {
            set_boundary(i, 0, 0.0);
            set_boundary(i, ny_ - 1, 0.0);
        }

        // Смужковий провідник на межі розділу
        size_t j_strip = ny_ / 2;
        for (size_t i = nx_ / 4; i <= 3 * nx_ / 4; ++i) {
            set_boundary(i, j_strip, strip_voltage);
        }
    }

    double iterate_sor(double omega) {
        double max_diff = 0.0;
        double h2 = h_ * h_;

        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                size_t id = index(i, j);
                if (is_boundary_[id]) continue;

                double eps_e = 0.5 * (eps_r_[id] + eps_r_[index(i + 1, j)]);
                double eps_w = 0.5 * (eps_r_[id] + eps_r_[index(i - 1, j)]);
                double eps_n = 0.5 * (eps_r_[id] + eps_r_[index(i, j + 1)]);
                double eps_s = 0.5 * (eps_r_[id] + eps_r_[index(i, j - 1)]);

                double num = eps_e * phi_[index(i + 1, j)] +
                             eps_w * phi_[index(i - 1, j)] +
                             eps_n * phi_[index(i, j + 1)] +
                             eps_s * phi_[index(i, j - 1)] +
                             (h2 * rho_free_[id] / EPS0);
                double den = eps_e + eps_w + eps_n + eps_s;
                double phi_target = num / den;

                double diff = std::abs(phi_target - phi_[id]);
                if (diff > max_diff) max_diff = diff;

                phi_[id] += omega * (phi_target - phi_[id]);
            }
        }
        return max_diff;
    }

    void compute_fields() {
        double h2 = 2.0 * h_;
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                size_t id = index(i, j);
                double ex = -(phi_[index(i + 1, j)] - phi_[index(i - 1, j)]) / h2;
                double ey = -(phi_[index(i, j + 1)] - phi_[index(i, j - 1)]) / h2;

                Ex_[id] = ex;
                Ey_[id] = ey;

                double eps = eps_r_[id];
                Dx_[id] = EPS0 * eps * ex;
                Dy_[id] = EPS0 * eps * ey;

                Px_[id] = Dx_[id] - EPS0 * ex;
                Py_[id] = Dy_[id] - EPS0 * ey;
            }
        }
    }

    [[nodiscard]] FieldPoint get_point(size_t i, size_t j) const {
        size_t id = index(i, j);
        return FieldPoint{
            .phi = phi_[id],
            .Ex = Ex_[id], .Ey = Ey_[id],
            .Dx = Dx_[id], .Dy = Dy_[id],
            .Px = Px_[id], .Py = Py_[id]
        };
    }

private:
    void set_boundary(size_t i, size_t j, double val) {
        size_t id = index(i, j);
        phi_[id] = val;
        is_boundary_[id] = true;
    }

    [[nodiscard]] size_t index(size_t i, size_t j) const noexcept {
        return i * ny_ + j;
    }

    size_t nx_, ny_;
    double h_;
    std::vector<double> phi_, eps_r_, rho_free_;
    std::vector<bool> is_boundary_;
    std::vector<double> Ex_, Ey_, Dx_, Dy_, Px_, Py_;
};

int main() {
    constexpr size_t N = 100;
    auto solver = std::make_unique<DielectricPoissonSolver2D>(N, N, 0.1);

    solver->setup_microstrip_geometry(4.4, 100.0);

    constexpr double omega = 1.90;
    size_t iter = 0;
    for (; iter < 5000; ++iter) {
        if (solver->iterate_sor(omega) < 1e-6) break;
    }

    solver->compute_fields();

    auto pt_sub = solver->get_point(N / 2, N / 4);
    auto pt_air = solver->get_point(N / 2, 3 * N / 4);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "[C++20 Solver] Збіжність за " << iter << " ітерацій.\n";
    std::cout << "Підкладка (eps=4.4): Ey = " << pt_sub.Ey << " В/м, Dy = " << pt_sub.Dy << " Кл/м²\n";
    std::cout << "Повітря    (eps=1.0): Ey = " << pt_air.Ey << " В/м, Dy = " << pt_air.Dy << " Кл/м²\n";

    return 0;
}
```
:::

---

### 5. Пастки чисельного моделювання полів D та E

#### 1. Неправильна усередненість проникності на межі:
Просте використання значення `ε_r` лівого чи правого вузла замість середнього арифметичного `0.5*(ε1+ε2)` або гармонійного `2*ε1*ε2/(ε1+ε2)` призводить до порушення граничної умови `D_1n = D_2n` та неконтрольованих похибок понад 25% на межі розділу матеріалів.

#### 2. Сингулярності на гострих кутах провідників:
На гострих краях прямокутної сигнальної смужки напруженість поля `E` фізично прагне до безкінечності за законом `E ∝ r^(-1/3)`. Для точного обчислення вектора `D` біля країв необхідна локальна сіткова адаптація (Mesh Refinement) або застосування скінченно-елементних квадратур.

#### 3. Вибір коефіцієнта релаксації ω:
При `ω >= 2.0` метод SOR стає чисельно нестійким і моментально розходиться. Для сітки 100×100 оптимальне `ω` становить `1.90–1.92`. Якщо `ω` вибрати надто малим (`ω = 1.0`), програма працюватиме у 50 разів повільніше.

#### 4. Кеш-ефективність та розміщення даних у пам'яті:
При двовимірному обході масивів `phi[i][j]` індексація `i * ny + j` гарантує послідовний доступ до сусідніх комірок пам'яті в закладеному внутрішньому циклі по `j`. Перестановка циклів місцями призведе до постійних промахів L1/L2-кешу процесора (Cache Misses) і сповільнить виконання розрахунку в 3–5 разів.
