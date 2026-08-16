# ⚙️ Чисельне моделювання електростатичних полів методом дзеркальних зображень

Для інженерного розрахунку паразитних ємностей, напруженості електричного поля та сил кулонівського притягання біля провідних поверхонь застосовують чисельне комп'ютерне моделювання. Метод дзеркальних зображень дозволяє обчислити електричний потенціал `V(x, y, z)`, вектор напруженості поля `E⃗(x, y, z)` та густину поверхневого індукованого заряду `σ` для довільної конфігурації точкових зарядів без розв'язання об'ємних сіткових диференціальних рівнянь (як у сіткових методах скінченних елементів FEM або скінченних різниць FDM).

Головна перевага обчислювального алгоритму дзеркальних зображень полягає у його надзвичайній обчислювальній ефективності та швидкодії: замість розв'язування величезних систем лінійних алгебраїчних рівнянь для тисяч або мільйонів вузлів просторової сітки, ми проводимо пряме алгебраїчне підсумовування кулонівських внесків від скінченної кількості реальних та дзеркальних зарядів. Це знижує обчислювальну складність алгоритму від `O(N³)` до `O(N)`, де `N` — кількість зарядів у досліджуваній системі.

При моделюванні високочастотних мікросмужкових ліній передачі на друкованих платах або складних заземлених корпусів приладів розробникам необхідно швидко отримувати векторні карти полів та оцінювати локальну напруженість для запобігання пробою. Чисельний солвер на основі методу дзеркальних зображень будує такі карти за мікросекунди.

Нижче наведено робочі реалізації електростатичного солвера мовами C та C++, які моделюють поле точкових зарядів поблизу трьох класичних провідних геометрій:
1. Нескінченна заземлена провідна площина `z = 0`;
2. Заземлена провідна сфера заданого радіуса `R` з центром у початку координат;
3. Кутовий відбивач зі взаємно перпендикулярними заземленими стінками під кутом `90°`.

### Реалізація чисельного солвера

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <numbers>
#include <iomanip>
#include <stdexcept>

// Фізична стала: 1 / (4 * pi * epsilon_0) [Н·м²/Кл²]
constexpr double K_COULOMB = 8.9875517923e9;

// Структура для 3D-вектора
struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] double length_sq() const noexcept {
        return x * x + y * y + z * z;
    }

    [[nodiscard]] double length() const noexcept {
        return std::sqrt(length_sq());
    }

    Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    Vector3D operator+(const Vector3D& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

// Точковий заряд (реальний або дзеркальний)
struct PointCharge {
    Vector3D pos;
    double charge{0.0};
    bool is_image{false};
};

// Клас розв'язувача електростатичних полів методом дзеркальних зображень
class ElectrostaticImageSolver {
public:
    enum class GeometryType { Plane, Sphere, CornerReflector90 };

    ElectrostaticImageSolver() = default;

    void add_real_charge(const Vector3D& position, double charge) {
        m_real_charges.push_back({position, charge, false});
    }

    void setup_plane_boundary(double plane_z = 0.0) {
        m_geometry = GeometryType::Plane;
        m_plane_z = plane_z;
        rebuild_image_charges();
    }

    void setup_sphere_boundary(const Vector3D& center, double radius) {
        if (radius <= 0.0) {
            throw std::invalid_argument("Радіус сфери має бути додатним");
        }
        m_geometry = GeometryType::Sphere;
        m_sphere_center = center;
        m_sphere_radius = radius;
        rebuild_image_charges();
    }

    void setup_corner_90_boundary() {
        m_geometry = GeometryType::CornerReflector90;
        rebuild_image_charges();
    }

    // Обчислення потенціалу V у довільній точці P
    [[nodiscard]] double evaluate_potential(const Vector3D& p) const noexcept {
        double v_total = 0.0;

        auto add_contribution = [&](const PointCharge& q) {
            Vector3D r_vec = p - q.pos;
            double dist = r_vec.length();
            if (dist > 1e-12) {
                v_total += K_COULOMB * q.charge / dist;
            }
        };

        for (const auto& q : m_real_charges) add_contribution(q);
        for (const auto& q : m_image_charges) add_contribution(q);

        return v_total;
    }

    // Обчислення вектора напруженості E у довільній точці P
    [[nodiscard]] Vector3D evaluate_field(const Vector3D& p) const noexcept {
        Vector3D e_total{0.0, 0.0, 0.0};

        auto add_contribution = [&](const PointCharge& q) {
            Vector3D r_vec = p - q.pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * q.charge / (dist_sq * dist);
                e_total = e_total + r_vec * factor;
            }
        };

        for (const auto& q : m_real_charges) add_contribution(q);
        for (const auto& q : m_image_charges) add_contribution(q);

        return e_total;
    }

    // Обчислення результуючої кулонівської сили, що діє на реальний заряд з індексом idx
    [[nodiscard]] Vector3D calculate_force_on_charge(size_t idx) const {
        if (idx >= m_real_charges.size()) {
            throw std::out_of_range("Некоректний індекс реального заряду");
        }

        const auto& target = m_real_charges[idx];
        Vector3D e_other{0.0, 0.0, 0.0};

        // Внесок інших реальних зарядів
        for (size_t i = 0; i < m_real_charges.size(); ++i) {
            if (i == idx) continue;
            Vector3D r_vec = target.pos - m_real_charges[i].pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * m_real_charges[i].charge / (dist_sq * dist);
                e_other = e_other + r_vec * factor;
            }
        }

        // Внесок усіх дзеркальних зарядів
        for (const auto& img : m_image_charges) {
            Vector3D r_vec = target.pos - img.pos;
            double dist_sq = r_vec.length_sq();
            double dist = std::sqrt(dist_sq);
            if (dist > 1e-12) {
                double factor = K_COULOMB * img.charge / (dist_sq * dist);
                e_other = e_other + r_vec * factor;
            }
        }

        return e_other * target.charge;
    }

    [[nodiscard]] const std::vector<PointCharge>& get_image_charges() const noexcept {
        return m_image_charges;
    }

private:
    void rebuild_image_charges() {
        m_image_charges.clear();

        for (const auto& real_q : m_real_charges) {
            switch (m_geometry) {
            case GeometryType::Plane: {
                // Дзеркальне відбиття відносно z = m_plane_z
                double z_img = 2.0 * m_plane_z - real_q.pos.z;
                m_image_charges.push_back({
                    {real_q.pos.x, real_q.pos.y, z_img},
                    -real_q.charge,
                    true
                });
                break;
            }
            case GeometryType::Sphere: {
                // Сферична інверсія відносно m_sphere_center
                Vector3D rel_pos = real_q.pos - m_sphere_center;
                double d = rel_pos.length();
                if (d <= m_sphere_radius) {
                    throw std::logic_error("Заряд знаходиться всередині сфери!");
                }
                double d_img = (m_sphere_radius * m_sphere_radius) / d;
                Vector3D img_pos = m_sphere_center + rel_pos * (d_img / d);
                double img_charge = -real_q.charge * (m_sphere_radius / d);

                m_image_charges.push_back({img_pos, img_charge, true});
                break;
            }
            case GeometryType::CornerReflector90: {
                // Три дзеркальні зображення для 90-градусного кута
                m_image_charges.push_back({{-real_q.pos.x, real_q.pos.y, real_q.pos.z}, -real_q.charge, true});
                m_image_charges.push_back({{real_q.pos.x, -real_q.pos.y, real_q.pos.z}, -real_q.charge, true});
                m_image_charges.push_back({{-real_q.pos.x, -real_q.pos.y, real_q.pos.z}, real_q.charge, true});
                break;
            }
            }
        }
    }

    GeometryType m_geometry{GeometryType::Plane};
    std::vector<PointCharge> m_real_charges;
    std::vector<PointCharge> m_image_charges;

    double m_plane_z{0.0};
    Vector3D m_sphere_center{0.0, 0.0, 0.0};
    double m_sphere_radius{1.0};
};

int main() {
    std::cout << "=== Моделювання поля методом дзеркальних зображень (C++) ===\n\n";

    ElectrostaticImageSolver solver;
    // Розмістимо заряд +2 мкКл на висоті z = 0.05 м (5 см)
    solver.add_real_charge({0.0, 0.0, 0.05}, 2.0e-6);
    solver.setup_plane_boundary(0.0);

    Vector3D test_point{0.0, 0.0, 0.02}; // Точка 2 см над площиною
    double v_pot = solver.evaluate_potential(test_point);
    Vector3D e_field = solver.evaluate_field(test_point);
    Vector3D force = solver.calculate_force_on_charge(0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Потенціал у точці (0, 0, 0.02 м): " << v_pot / 1000.0 << " кВ\n";
    std::cout << "Напруженість E_z: " << e_field.z / 1000.0 << " кВ/м\n";
    std::cout << "Сила притягання до площини: " << force.z << " Н\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define K_COULOMB 8.9875517923e9

typedef struct {
    double x;
    double y;
    double z;
} es_vec3_t;

typedef struct {
    es_vec3_t pos;
    double charge;
    bool is_image;
} es_point_charge_t;

typedef enum {
    GEOM_PLANE,
    GEOM_SPHERE,
    GEOM_CORNER_90
} es_geometry_type_t;

typedef struct {
    es_geometry_type_t geom_type;
    es_point_charge_t* real_charges;
    size_t real_count;
    es_point_charge_t* image_charges;
    size_t image_count;

    double plane_z;
    es_vec3_t sphere_center;
    double sphere_radius;
} es_solver_t;

static inline double vec3_length_sq(es_vec3_t v) {
    return v.x * v.x + v.y * v.y + v.z * v.z;
}

static inline double vec3_length(es_vec3_t v) {
    return sqrt(vec3_length_sq(v));
}

static inline es_vec3_t vec3_sub(es_vec3_t a, es_vec3_t b) {
    return (es_vec3_t){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline es_vec3_t vec3_scale(es_vec3_t v, double s) {
    return (es_vec3_t){v.x * s, v.y * s, v.z * s};
}

es_solver_t* es_solver_create(void) {
    es_solver_t* s = (es_solver_t*)calloc(1, sizeof(es_solver_t));
    if (!s) return NULL;
    s->geom_type = GEOM_PLANE;
    s->plane_z = 0.0;
    return s;
}

void es_solver_destroy(es_solver_t* s) {
    if (!s) return;
    free(s->real_charges);
    free(s->image_charges);
    free(s);
}

bool es_solver_add_charge(es_solver_t* s, es_vec3_t pos, double q) {
    es_point_charge_t* new_arr = (es_point_charge_t*)realloc(
        s->real_charges, (s->real_count + 1) * sizeof(es_point_charge_t));
    if (!new_arr) return false;

    s->real_charges = new_arr;
    s->real_charges[s->real_count++] = (es_point_charge_t){pos, q, false};
    return true;
}

void es_solver_rebuild_images(es_solver_t* s) {
    free(s->image_charges);
    s->image_charges = NULL;
    s->image_count = 0;

    if (s->geom_type == GEOM_PLANE) {
        s->image_charges = (es_point_charge_t*)malloc(s->real_count * sizeof(es_point_charge_t));
        s->image_count = s->real_count;
        for (size_t i = 0; i < s->real_count; ++i) {
            es_vec3_t pos = s->real_charges[i].pos;
            pos.z = 2.0 * s->plane_z - pos.z;
            s->image_charges[i] = (es_point_charge_t){pos, -s->real_charges[i].charge, true};
        }
    } else if (s->geom_type == GEOM_SPHERE) {
        s->image_charges = (es_point_charge_t*)malloc(s->real_count * sizeof(es_point_charge_t));
        s->image_count = s->real_count;
        for (size_t i = 0; i < s->real_count; ++i) {
            es_vec3_t rel = vec3_sub(s->real_charges[i].pos, s->sphere_center);
            double d = vec3_length(rel);
            double d_img = (s->sphere_radius * s->sphere_radius) / d;
            es_vec3_t img_pos = {
                s->sphere_center.x + rel.x * (d_img / d),
                s->sphere_center.y + rel.y * (d_img / d),
                s->sphere_center.z + rel.z * (d_img / d)
            };
            double img_q = -s->real_charges[i].charge * (s->sphere_radius / d);
            s->image_charges[i] = (es_point_charge_t){img_pos, img_q, true};
        }
    }
}

double es_solver_eval_potential(const es_solver_t* s, es_vec3_t p) {
    double v_total = 0.0;
    for (size_t i = 0; i < s->real_count; ++i) {
        double dist = vec3_length(vec3_sub(p, s->real_charges[i].pos));
        if (dist > 1e-12) v_total += K_COULOMB * s->real_charges[i].charge / dist;
    }
    for (size_t i = 0; i < s->image_count; ++i) {
        double dist = vec3_length(vec3_sub(p, s->image_charges[i].pos));
        if (dist > 1e-12) v_total += K_COULOMB * s->image_charges[i].charge / dist;
    }
    return v_total;
}

int main(void) {
    printf("=== Моделювання поля методом дзеркальних зображень (C) ===\n\n");

    es_solver_t* solver = es_solver_create();
    es_solver_add_charge(solver, (es_vec3_t){0.0, 0.0, 0.05}, 2.0e-6);
    es_solver_rebuild_images(solver);

    es_vec3_t p = {0.0, 0.0, 0.02};
    double v = es_solver_eval_potential(solver, p);

    printf("Потенціал у точці (0, 0, 0.02 м): %.4f кВ\n", v / 1000.0);

    es_solver_destroy(solver);
    return 0;
}
```
:::

---

### Детальний аналіз алгоритму та особливості обчислень

Розглянемо ключові обчислювальні блоки, числові особливості та інженерні нюанси реалізації даного електростатичного розв'язувача.

#### 1. Генерація та перебудова дзеркальних зарядів (`rebuild_image_charges`)
Підсистема підтримки дзеркальних зарядів працює за принципом відкладеного або явного перерахунку при зміні геометрії чи позицій реальних джерел.
* Для **плоської заземленої межі** (`z = z_plane`) дзеркальне відбиття виконується простим дзеркальним зміщенням координати `z_img = 2*z_plane - z_real` та інверсією знаку заряду `q_img = -q_real`.
* Для **сферичної заземленої межі** радіуса `R` напрямок вектору дзеркального заряду збігається з радіус-вектором реального заряду, відносно центра сфери, а його відстань обчислюється як `d' = R² / d`. Величина заряду зменшується пропорційно відношенню радіуса до відстані `q' = -q·(R/d)`.
* Для **кутового відбивача під кутом 90°** створюється три дзеркальних заряди у II, III та IV квадрантах із чергуванням знаків, що компенсують напруженість на обох стінках `x = 0` та `y = 0`.

#### 2. Обчислення кулонівської суперпозиції полів (`evaluate_potential` та `evaluate_field`)
Сумарний потенціал `V` та вектор напруженості `E⃗` у довільній точці простору розраховуються прямою суперпозицією полів усіх зарядів.
Для напруженості електричного поля векторний доданок від кожного заряду має вигляд:

```
E⃗_i = K_COULOMB · q_i · (r⃗ - r⃗_i) / |r⃗ - r⃗_i|³
```

У реалізації C++ для уникнення повторного обчислення квадратного кореня спочатку вираховується квадрат відстані `dist_sq`, після чого формула використовує ділення на `(dist_sq * sqrt(dist_sq))`. Це оптимально використовує обчислювальні інструкції сучасних процесорів (FMA / SSE / AVX).

#### 3. Обчислення сили, що діє на реальний заряд (`calculate_force_on_charge`)
При обчисленні механічної кулонівської сили, що діє на обраний реальний заряд `q_target`, принципово важливо **виключити власний внесок цього заряду** у створюване поле, оскільки заряд не діє сам на себе (`r⃗ - r⃗_target = 0`).
Метод `calculate_force_on_charge` просумовує поля від усіх інших реальних зарядів та від усіх дзеркальних зарядів, після чого множить підсумковий вектор напруженості на величину заряду `q_target`:

```
F⃗_target = q_target · ∑_(i ≠ target) E⃗_real,i + q_target · ∑_(j) E⃗_image,j
```

#### 4. Захист від числових сингулярностей та вибір відсічки
При спробі обчислити поле безпосередньо у точці розташування точкового заряду або прямо на дзеркальній межі відстань `dist` наближається до нуля (`dist -> 0`), що спричиняє ділення на нуль та виникнення числових значень `NaN` або `Infinity`. У програмі реалізовано порогову перевірку `if (dist > 1e-12)`, яка пропускає некоректні сингулярні внески, забезпечуючи числову стійкість алгоритму. Поріг `1e-12` м обрано з міркувань подвійної точності типів `double` (64 біти IEEE 754), де машинний нуль для просторових координат у метрах становить порядок `10⁻¹⁶`.

#### 5. Побудова двовимірних ізопотенціальних карт і трасування силових ліній
Для візуалізації полів у геофізичних та антенних задачах солвер інтегрують із процедурами трасування силових ліній. Починаючи з точки біля позитивного заряду, алгоритм здійснює числове інтегрування методом Ейлера або Рунге — Кутти 4-го порядку для векторного диференціального рівняння силової лінії:

```
dr⃗ / ds = E⃗ / |E⃗|
```

Крок інтегрування `ds` обирається адаптивно: зменшується поблизу точкових джерел та металевої межі для збереження ортогональності ліній по відношенню до еквіпотенціалей провідника. Усі обчислення виконуються в пам'яті O(1) без виділення додаткових сіток.

#### 6. Порівняння реалізацій мовами C++ та C
* **C++ реалізація** використовує стандартні контейнери `std::vector`, строго типізоване перелічування `enum class GeometryType`, методи обробки виняткових ситуацій `std::invalid_argument` та зручне перевантаження математичних операторів додавання й віднімання для структури `Vector3D`.
* **C реалізація** виконана у класичному процедурному стилі ANSI C з ручним управлінням динамічною пам'яттю (`malloc`, `realloc`, `free`), чистими функціями утиліт `vec3_sub`, `vec3_scale` та поінтерною перевіркою виділення ресурсів, що є ідеальним для вбудованих мікроконтролерних систем та вбудованих фізичних солверів.
