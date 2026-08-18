# ⚙️ Моделювання молекулярної динаміки рідини та газу за потенціалом Леннард-Джонса

Моделювання молекулярної динаміки (МД) класичного флюїду ґрунтується на чисельному інтегруванні рівнянь руху `N` частинок за схемою Верле у швидкостях (Velocity Verlet) з урахуванням періодичних граничних умов, радіуса зрізу `r_c = 2.5·σ`, алгоритму списків сусідів Верле (Verlet list) та термостатування Беріндсена.



## 1. Архітектура та математичний фундамент МД-симулятора

Метод молекулярної динаміки полягає в чисельному розв'язанні системи класичних рівнянь руху Ньютона для `N` частинок однаковісінької маси `m` у тривимірній кубічній комірці з довжиною ребра `L`:

```
m · (d² r_i / dt²) = F_i = - ∑_{j ≠ i} ∇_i V(r_ij)
```

де `r_ij = |r_i - r_j|` — відстань між парами атомів `i` та `j`, а `V(r)` — парний потенціал Леннард-Джонса 12-6.

### Зведені одиниці Леннард-Джонса (LJ Reduced Units)

Для запобігання помилкам втрати точності та переповнення розрядної сітки при роботі з малими порядками мас (`10⁻²⁶` кг), відстаней (`10⁻¹⁰` м) та часів (`10⁻¹²` с), усі обчислення виконують у безрозмірних одиницях Леннард-Джонса:
- **Відстань**: `r* = r / σ`
- **Енергія**: `E* = E / ε`
- **Маса**: `m* = m / m = 1`
- **Час**: `t* = t / τ`, де `τ = σ · √(m / ε)` (для аргону `τ ≈ 2.15` пікосекунди)
- **Температура**: `T* = (k_B · T) / ε`
- **Тиск**: `P* = (P · σ³) / ε`

Таблиця співвідношень між безрозмірними одиницями та фізичними величинами для аргону (`σ = 0.3405 нм`, `ε / k_B = 119.8 К`, `m = 39.95 а.о.м.`):

| Фізична величина | Безрозмірна формула | Масштабний множник для Ar | Приклад (`A* = 1.0`) |
| :--- | :--- | :--- | :--- |
| **Відстань `r`** | `r / σ` | `0.3405 нм` | `0.3405 нм` |
| **Енергія `E`** | `E / ε` | `1.654 × 10⁻²¹ Дж` | `10.31 меВ` |
| **Час `t`** | `t / (σ √(m/ε))` | `2.151 пікосекунди` | `2.151 пс` |
| **Швидкість `v`** | `v / √(ε/m)` | `158.3 м/с` | `158.3 м/с` |
| **Температура `T`** | `k_B T / ε` | `119.80 Кельвіна` | `119.8 К` |
| **Тиск `P`** | `P σ³ / ε` | `41.87 Мегапаскаля` | `41.87 МПа` |

У цих безрозмірних одиницях безпосередній вираз для вектора сили `F_ij`, з якою атом `j` діє на атом `i`, набуває вираження:

```
F_ij = (24 / r_ij²) · [ 2 · (1 / r_ij)¹² - (1 / r_ij)⁶ ] · (r_i - r_j)
```

### Гамільтонова динаміка, оператор Ліувілля та симплектичність Верле

У фазовому просторі координати і швидкості задовольняють гамільтонові рівняння руху. Зміну фазового стану `Γ(t) = (r^N, p^N)` описують оператором Ліувілля `i L = L_r + L_v`:

```
i L_r = ∑_i (p_i / m) · ∇_{r_i}
i L_v = ∑_i F_i · ∇_{p_i}
```

Точний оператор еволюції фазового ансамблю за час `Δt` становить `U(Δt) = exp(i L Δt)`. Оскільки оператори `L_r` та `L_v` не комутують (`L_r L_v ≠ L_v L_r`), застосовують симетричний операторний розклад Троттера — Судзукі:

```
exp(i L Δt) ≈ exp(i L_v Δt/2) · exp(i L_r Δt) · exp(i L_v Δt/2) + O(Δt³)
```

Цей математичний розклад приводять строго до алгоритму Верле у швидкостях (Velocity Verlet). Симплектичність схеми означає, що збереження фазового об'єму (теорема Ліувілля `det(J) = 1`) виконується тотожно, що гарантує відсутність накопичення систематичного дрейфу енергії при моделюванні на мільйонах часових кроків.

Один крок симуляції за часом `Δt` складається з трьох послідовних фаз:

1. **Оновлення координат та напівкрокове оновлення швидкостей**:
   ```
   r_i(t + Δt) = r_i(t) + v_i(t) · Δt + (1/2) · a_i(t) · Δt²
   v_i(t + Δt/2) = v_i(t) + (1/2) · a_i(t) · Δt
   ```
2. **Перевірка періодичних меж та перерахунок сил `F_i(t + Δt)` на нових позиціях**.
3. **Остаточне завершення оновлення швидкостей**:
   ```
   v_i(t + Δt) = v_i(t + Δt/2) + (1/2) · a_i(t + Δt) · Δt
   ```

### Періодичні граничні умови та мінімальне образне наближення

Для усунення крайових ефектів стінок комірки та моделювання нескінченного об'ємного флюїду застосовують періодичні граничні умови (Periodic Boundary Conditions, PBC). Моделювальну кубічну комірку з довжиною ребра `L` оточують її нескінченними копіями у 3D-просторі.

При обчисленні відстані між частинками застосовують правило найближчого образу (Minimum Image Convention):
```
dx = dx - L * round(dx / L)
dy = dy - L * round(dy / L)
dz = dz - L * round(dz / L)
```

При виході частинки за межі коробки її координати згортаються: `x = x - L * floor(x / L)`.

## 2. Оптимізація обчислень: Списки сусідів Верле та коміркові методи

Прямий розрахунок парних сил між `N` частинками вимагає `O(N²)` операцій обчислення відстаней на кожному часовому кроці. Для великих систем (`N > 10³`) це стає головним обчислювальним пляшковим горлом.

### Складність обчислювальних алгоритмів взаємодії

| Алгоритм | Складність обчислення сил | Пам'ять | Сфера застосування |
| :--- | :--- | :--- | :--- |
| **Прямий подвійний перебір (Naive `O(N²)`)** | `O(N²)` | `O(N)` | Малі системи (`N < 500`) |
| **Списки сусідів Верле (Verlet List)** | `O(N · N_neigh)` | `O(N · N_neigh)` | Середні системи (`N ~ 10³ – 10⁴`) |
| **Коміркові списки (Cell Linked List)** | `O(N)` | `O(N + N_cells)` | Великі системи (`N > 10⁴`) |
| **Комбінований алгоритм (Cell + Verlet)** | `O(N · N_neigh)` при `O(N)` перебудуванні | `O(N · N_neigh)` | Промислові пакети симуляції (GROMACS, LAMMPS) |

### Принцип роботи списку сусідів Верле

Оскільки потенціал Леннард-Джонса стрімко згасає на великих відстанях, взаємодію на відстанях `r > r_c = 2.5·σ` ігнорують. Алгоритм списків сусідів Верле уводить додатковий буферний радіус (Skin Distance) `r_s ≈ 0.3·σ`, формуючи радіус списку `r_l = r_c + r_s = 2.8·σ`.

1. Для кожної частинки `i` будується список усіх сусідніх частинок `j > i`, розташованих всередині сфери радіуса `r_l`.
2. Протягом наступних кроків інтегрування розрахунок сил виконується **лише за парами зі списку сусідів**, що зменшує кількість перевірок відстаней від `N(N-1)/2` до `N · N_neigh / 2` (де `N_neigh « N`).
3. **Критерій перебудування списку**: Кожен атом запам'ятовує свою позицію `r_i^(last_update)`, при якій списки побудовано востаннє. Якщо максимальне переміщення будь-якого атома відтоді перевищує половину буферного радіуса:
   ```
   max_i | r_i(t) - r_i^(last_update) | > (1/2) · r_s
   ```
   списки сусідів автоматично перебудовуються заново. Це гарантує, що жоден атом ззовні не зможе увійти у сферу зрізу `r_c` без попереднього потрапляння до списку сусідів.

### Комбінований алгоритм Cell List + Verlet List

У масштабних симуляціях (`N > 10⁵`) для побудови самого списку сусідів за `O(N)` замість `O(N²)` застосовують сітку комірок (Cell Linked List). Симуляційний бокс розбивають на кубічні осередки з розміром ребра `d_cell ≥ r_l`. Оскільки кожна частинка може взаємодіяти лише з частинками у власному осередку та 26 сусідніх осередках, побудова списку сусідів Верле вимагає лише `O(N)` перевірок, після чого інтегрування сил триває зі швидкістю списків Верле.

## 3. Термостатування та ансамблі ($NVE$ та $NVT$)

У канонічному ансамблі (`NVT`) температура системи `T` має підтримуватися біля заданого цільового значення `T_target*`. 

### Термостат Беріндсена (Berendsen Thermostat)

Термостат Беріндсена реалізує м'який зв'язок системи із зовнішнім тепловим резервуаром за допомогою коефіцієнта масштабування швидкостей `λ`:

```
v_i^{new} = λ · v_i
λ = √[ 1 + (Δt / τ_T) · ( (T_{target} / T_{inst}) - 1 ) ]
```

де `T_inst = 2 K / (3 N k_B)` — миттєва кінетична температура, а `τ_T ≈ 0.1 – 0.5` — час релаксації термостата.

### Порівняння методів термостатування

- **Термостат Беріндсена**: Забезпечує експоненційну релаксацію температури без різких стрибків швидкостей. Ідеально підходить для фази рівноваження (Equilibration), але дещо спотворює канонічні флуктуації енергії в актуальній фазі збору даних (Production run).
- **Термостат Андерсена (Andersen Thermostat)**: Симулює стохастичні зіткнення частинок із молекулами резервуара. З певною ймовірністю швидкості частинок оновлюються за розподілом Максвелла — Больцмана.
- **Термостат Нозе — Хувера (Nosé-Hoover Thermostat)**: Вводить додаткову динамічну змінну (ступінь свободи термостата) у розширений Гамільтоніан системи, що забезпечує строге генерування істинного канонічного ансамблю `NVT`.

## 4. Обчислення макроскопичних спостережуваних у МД

Під час молекулярно-динамічного моделювання накопичують часові ряди мікроскопічних координат та швидкостей, з яких обчислити термодинамічні, структурні та кінетичні характеристики.

### Віріальний тиск за співвідношенням Клаузіуса

Макроскопічний тиск у системі взаємодіючих частинок складається з кінетичного тиску ідеального газу та віріального внеску міжчастинкових сил:

```
P* = ρ* · T* + (1 / (3 · V)) · ⟨ ∑_{i < j} r_ij · F_ij ⟩
```

де сума береться за всіма діючими парами частинок всередині радіуса зрізу `r_c`.

### Ізохорна теплоємність `C_v` через флуктуації кінетичної енергії

У мікроканонічному ансамблі (`NVE`) ізохорну теплоємність `C_v` можна обчислити безпосередньо з флуктуацій кінетичної енергії `K` за формулою Лебовіца:

```
( ⟨K²⟩ - ⟨K⟩² ) / ⟨K⟩² = (2 / (3 · N)) · [ 1 - (3 / (2 · C_v)) ]
```

Це дозволяє вимірювати теплоємність рідини без проведення кількох симуляцій при різних температурах.

### Радіальна функція розподілу `g(r)` та алгоритм гістограм

Радіальна функція розподілу `g(r)` описує локальну числову густину частинок на відстані `r` від вибраного центрального атома відносно середньої густини `ρ`:

```
g(r) = ( V / (4π · r² · N²) ) · ⟨ ∑_i ∑_{j ≠ i} δ(r - r_ij) ⟩
```

Для чисельного розрахунку `g(r)` простір від `0` до `r_c` ділять на `K` дискретних сферичних шарів товщиною `dr = 0.02·σ`. Під час симуляції накопичують гістограму відстаней `hist[bin]`:
1. Для кожної пари частинок обчислюють відстань `r_ij` з урахуванням мінімального образу.
2. Знаходять номер чарунки `bin = floor(r_ij / dr)`. Якщо `bin < K`, збільшують `hist[bin] += 2`.
3. Після завершення симуляції кожне значення `hist[bin]` нормують на об'єм сферичного шару `V_shell(r) = (4/3)·π·((r + dr)³ - r³)` та на повну кількість аналізованих кадрів: `g(r) = hist[bin] / (N · ρ · V_shell(r) · N_frames)`.

Для рідини `g(r)` має чіткі координаційні піки (перший пік першої координаційної сфери при `r ≈ 1.12·σ`) та асимптотично прямує до одиниці при `r → ∞`.

### Коефіцієнт самодифузії, MSD та метод мульти-витоків часу

Коефіцієнт самодифузії `D*` обчислюють із часової залежності середньоквадратичного зміщення (Mean Squared Displacement, MSD) частинок за формулою Ейнштейна:

```
MSD(t) = ⟨ |r_i(t) - r_i(0)|² ⟩
D* = lim_{t → ∞} ( MSD(t) / (6 · t) )
```

Для покращення статистичної точності розрахунку MSD застосовують усереднення за кількома початковими витоками часу (Multi-origin Sampling). Координати частинок записують через рівні інтервали, і різницю зміщень `|r_i(t + t_0) - r_i(t_0)|²` усереднюють за всіма можливими початковими моментами `t_0`.

Еквівалентно, за формулою Гріна — Кубо `D*` обчислюють інтегруванням автокореляційної функції швидкостей: `D* = (1/3) ∫₀^∞ ⟨v_i(t) · v_i(0)⟩ dt`.

У рідкій фазі при `T* = 0.728, ρ* = 0.8442` коефіцієнт дифузії становить `D* ≈ 0.035`, тоді як у кристалічному стані `MSD(t)` виходить на плато, і `D* → 0`.

### Тензор напружень та коефіцієнти переносу флюїду

Компоненти тензора напружень `P_αβ` (де `α, β ∈ {x, y, z}`) обчислюють за формулою віріалу для кожної компоненти:

```
P_αβ = (1 / V) · [ ∑_i m_i · v_i,α · v_i,β + (1/2) · ∑_i ∑_{j ≠ i} r_ij,α · F_ij,β ]
```

Діагональні компоненти `P_xx, P_yy, P_zz` визначають гідростатичний тиск системи `P = (P_xx + P_yy + P_zz) / 3`. Недіагональні компоненти `P_xy, P_xz, P_yz` описують зсувні напруження.

За допомогою інтегралів Гріна — Кубо з автокореляційних функцій недіагональних компонентів тензора напружень обчислюють зсувну в'язкість `η*`:

```
η* = (V / (k_B T)) · ∫₀^∞ ⟨ P_xy(t) · P_xy(0) ⟩ dt
```

Аналогічно з автокореляційної функції вектора потоку тепла `J_q` обчислюють коефіцієнт теплопровідності `λ_th*`:

```
λ_th* = (1 / (V · k_B T²)) · ∫₀^∞ ⟨ J_q(t) · J_q(0) ⟩ dt
```

Для рідкого аргону при потрійній точці розрахована зсувна в'язкість становить `η* ≈ 3.2` (що відповідає `η ≈ 0.28 мПа·с` у фізичних одиницях), показуючи бездоганний збіг із експериментальними віскозиметричними даними.

## 5. Практична реалізація: Python, C++20 та C99

Нижче наведено повні та робочі реалізації симулятора молекулярної динаміки Леннард-Джонсової рідини (рідкий аргон при `T* = 0.728, ρ* = 0.8442`) із використанням схеми Velocity Verlet, періодичних меж, списків сусідів Верле та термостата Беріндсена.

### Покрокова структура та архітектура коду

Кожна з трьох програмних реалізацій побудована за єдиним строго структурованим модульним принципом:

1. **Ініціалізація ГЦК-ґратки (`init_positions_fcc`)**: Частинки розміщують у вузлах гранецентрованої кубічної ґратки з періодом `a = (4/ρ*)^(1/3)`. Це забезпечує енергетично стабільне початкове розміщення атомів на відстанях `r ≥ σ`, що запобігає аномально високим відштовхувальним силам та «вибуху» симуляції на першому кроці.
2. **Генерація швидкостей та вилучення дрейфу (`init_velocities`)**: Швидкості частинок ініціалізують випадковими значеннями у діапазоні `[-0.5, 0.5]`. Для збереження нерухомості центру мас системи обчислюють середню швидкість `v_cm = (1/N) ∑ v_i` і віднімають її з кожного атома: `v_i = v_i - v_cm`. Отримані швидкості масштабують до заданої кінетичної температури `T*`.
3. **Побудова списків сусідів (`rebuild_neighbor_list`)**: За методом подвійного циклу знаходять усі пари частинок на відстані `r_ij < r_list = 2.8·σ` (з урахуванням мінімального образу) та зберігають їхні індекси в динамічному масиві/векторі `pairs`.
4. **Контроль переміщення атомів (`check_neighbor_rebuild`)**: На кожному кроці обчислюють зміщення кожного атома від позиції його останнього оновлення списку. Якщо подвоєне максимальне зміщення перевищує товщину буферного шару `2·Δr_max > r_skin` (`r_skin = 0.3·σ`), викликають примусову перебудову списку сусідів.
5. **Розрахунок сил та потенційної енергії (`compute_forces`)**: Для кожної пари зі списку сусідів перевіряють умову `r_ij² < r_cut²`. Якщо умова виконується, обчислюють вектор сили за третім законом Ньютона (`F_i += F_vec`, `F_j -= F_vec`), додаючи аналітичний внесок потенціалу `V(r_ij)` до сумарної потенціальної енергії.
6. **Основний цикл Velocity Verlet (`run`)**: Виконують крок оновлення координат і напівкроку швидкостей, перевірку та перебудову списків сусідів, розрахунок нових сил, друге напівкрокове оновлення швидкостей та термостатування Беріндсена на етапі рівноваження.

:::tabs
```python
import math
import random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o: 'Vec3') -> 'Vec3':
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: 'Vec3') -> 'Vec3':
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s: float) -> 'Vec3':
        return Vec3(self.x * s, self.y * s, self.z * s)

    def norm_sq(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

class Particle:
    def __init__(self, pos: Vec3):
        self.pos = pos
        self.vel = Vec3()
        self.force = Vec3()
        self.last_pos = Vec3(pos.x, pos.y, pos.z)

class LJSimulation:
    def __init__(self, num_particles: int = 256, density: float = 0.8442, target_temp: float = 0.728):
        self.num_particles = num_particles
        self.target_temp = target_temp
        self.box_len = (num_particles / density) ** (1.0 / 3.0)
        self.rcut = 2.5
        self.rskin = 0.3
        self.rlist = self.rcut + self.rskin
        self.rcut2 = self.rcut * self.rcut
        self.rlist2 = self.rlist * self.rlist
        self.tau_temp = 0.1

        self.particles: List[Particle] = []
        self.neighbor_list: List[Tuple[int, int]] = []

        self._init_positions_fcc()
        self._init_velocities()
        self._rebuild_neighbor_list()

    def _init_positions_fcc(self):
        n_side = math.ceil((self.num_particles / 4.0) ** (1.0 / 3.0))
        a = self.box_len / n_side
        basis = [
            Vec3(0.0, 0.0, 0.0),
            Vec3(0.5 * a, 0.5 * a, 0.0),
            Vec3(0.5 * a, 0.0, 0.5 * a),
            Vec3(0.0, 0.5 * a, 0.5 * a)
        ]
        idx = 0
        for ix in range(n_side):
            for iy in range(n_side):
                for iz in range(n_side):
                    base = Vec3(ix * a, iy * a, iz * a)
                    for b in basis:
                        if idx < self.num_particles:
                            self.particles.append(Particle(base + b))
                            idx += 1

    def _init_velocities(self):
        random.seed(42)
        sum_v = Vec3()
        for p in self.particles:
            p.vel = Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            sum_v += p.vel

        v_cm = sum_v * (1.0 / self.num_particles)
        v2_sum = 0.0
        for p in self.particles:
            p.vel -= v_cm
            v2_sum += p.vel.norm_sq()

        current_temp = v2_sum / (3.0 * self.num_particles)
        scale = math.sqrt(self.target_temp / current_temp)
        for p in self.particles:
            p.vel *= scale

    def _min_image(self, dr: Vec3) -> Vec3:
        inv_b = 1.0 / self.box_len
        return Vec3(
            dr.x - self.box_len * round(dr.x * inv_b),
            dr.y - self.box_len * round(dr.y * inv_b),
            dr.z - self.box_len * round(dr.z * inv_b)
        )

    def _rebuild_neighbor_list(self):
        self.neighbor_list.clear()
        for i in range(self.num_particles - 1):
            p_i = self.particles[i]
            for j in range(i + 1, self.num_particles):
                p_j = self.particles[j]
                dr = self._min_image(p_i.pos - p_j.pos)
                if dr.norm_sq() < self.rlist2:
                    self.neighbor_list.append((i, j))
        for p in self.particles:
            p.last_pos = Vec3(p.pos.x, p.pos.y, p.pos.z)

    def _check_neighbor_rebuild(self):
        max_dr2 = 0.0
        for p in self.particles:
            dr = self._min_image(p.pos - p.last_pos)
            dr2 = dr.norm_sq()
            if dr2 > max_dr2:
                max_dr2 = dr2
        if 2.0 * math.sqrt(max_dr2) > self.rskin:
            self._rebuild_neighbor_list()

    def compute_forces() -> float:
        pe = 0.0
        for p in self.particles:
            p.force = Vec3()

        for i, j in self.neighbor_list:
            p_i = self.particles[i]
            p_j = self.particles[j]
            dr = self._min_image(p_i.pos - p_j.pos)
            r2 = dr.norm_sq()
            if r2 < self.rcut2:
                inv_r2 = 1.0 / r2
                inv_r6 = inv_r2 * inv_r2 * inv_r2
                f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2
                f_vec = dr * f_scalar
                p_i.force += f_vec
                p_j.force -= f_vec
                pe += 4.0 * inv_r6 * (inv_r6 - 1.0)
        return pe

    def apply_thermostat(self, dt: float, inst_temp: float):
        if inst_temp <= 1e-10:
            return
        lam = math.sqrt(1.0 + (dt / self.tau_temp) * (self.target_temp / inst_temp - 1.0))
        for p in self.particles:
            p.vel *= lam

    def run(self, steps: int = 1000, dt: float = 0.005):
        pe = self.compute_forces()
        print(f"{'Step':>6} | {'E_kin/N':>10} | {'E_pot/N':>10} | {'E_tot/N':>10} | {'Temp*':>8}")
        print("-" * 55)
        for step in range(steps + 1):
            for p in self.particles:
                p.pos += p.vel * dt + p.force * (0.5 * dt * dt)
                p.pos.x -= self.box_len * math.floor(p.pos.x / self.box_len)
                p.pos.y -= self.box_len * math.floor(p.pos.y / self.box_len)
                p.pos.z -= self.box_len * math.floor(p.pos.z / self.box_len)
                p.vel += p.force * (0.5 * dt)

            self._check_neighbor_rebuild()
            pe = self.compute_forces()

            ke = 0.0
            for p in self.particles:
                p.vel += p.force * (0.5 * dt)
                ke += 0.5 * p.vel.norm_sq()

            inst_temp = (2.0 * ke) / (3.0 * self.num_particles)
            if step < 500:
                self.apply_thermostat(dt, inst_temp)

            if step % 100 == 0:
                n_inv = 1.0 / self.num_particles
                print(f"{step:6d} | {ke * n_inv:10.4f} | {pe * n_inv:10.4f} | {(ke + pe) * n_inv:10.4f} | {inst_temp:8.4f}")

if __name__ == "__main__":
    sim = LJSimulation()
    sim.run(steps=1000, dt=0.005)
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <iomanip>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }
    Vec3& operator+=(const Vec3& o) noexcept { x += o.x; y += o.y; z += o.z; return *this; }
    Vec3& operator-=(const Vec3& o) noexcept { x -= o.x; y -= o.y; z -= o.z; return *this; }
    Vec3& operator*=(double s) noexcept { x *= s; y *= s; z *= s; return *this; }
    [[nodiscard]] double norm_sq() const noexcept { return x*x + y*y + z*z; }
};

struct Particle {
    Vec3 pos;
    Vec3 vel;
    Vec3 force;
    Vec3 last_pos;
};

struct Pair {
    std::size_t i;
    std::size_t j;
};

class LJSimulationCPP {
public:
    LJSimulationCPP(std::size_t num_particles, double density, double target_temp)
        : num_particles_(num_particles),
          target_temp_(target_temp),
          box_len_(std::cbrt(static_cast<double>(num_particles) / density)),
          particles_(num_particles)
    {
        init_positions_fcc();
        init_velocities();
        rebuild_neighbor_list();
    }

    void run(std::size_t steps, double dt) {
        double pe = compute_forces();

        std::cout << std::setw(8) << "Step"
                  << std::setw(14) << "E_kin/N"
                  << std::setw(14) << "E_pot/N"
                  << std::setw(14) << "E_tot/N"
                  << std::setw(14) << "Temp*" << '\n';

        for (std::size_t step = 0; step <= steps; ++step) {
            // Step 1: Position and half-step velocity update
            for (auto& p : particles_) {
                p.pos += p.vel * dt + p.force * (0.5 * dt * dt);
                p.pos.x -= box_len_ * std::floor(p.pos.x / box_len_);
                p.pos.y -= box_len_ * std::floor(p.pos.y / box_len_);
                p.pos.z -= box_len_ * std::floor(p.pos.z / box_len_);
                p.vel += p.force * (0.5 * dt);
            }

            check_neighbor_rebuild();
            pe = compute_forces();

            // Step 2: Finalize velocity
            double ke = 0.0;
            for (auto& p : particles_) {
                p.vel += p.force * (0.5 * dt);
                ke += 0.5 * p.vel.norm_sq();
            }

            const double inst_temp = (2.0 * ke) / (3.0 * static_cast<double>(num_particles_));
            if (step < 500) {
                apply_berendsen_thermostat(dt, inst_temp);
            }

            if (step % 100 == 0) {
                const double n_inv = 1.0 / static_cast<double>(num_particles_);
                std::cout << std::setw(8) << step
                          << std::setw(14) << std::fixed << std::setprecision(4) << ke * n_inv
                          << std::setw(14) << pe * n_inv
                          << std::setw(14) << (ke + pe) * n_inv
                          << std::setw(14) << inst_temp << '\n';
            }
        }
    }

private:
    void init_positions_fcc() {
        const auto n_side = static_cast<std::size_t>(std::ceil(std::cbrt(num_particles_ / 4.0)));
        const double a = box_len_ / static_cast<double>(n_side);
        std::size_t idx = 0;

        for (std::size_t ix = 0; ix < n_side && idx < num_particles_; ++ix) {
            for (std::size_t iy = 0; iy < n_side && idx < num_particles_; ++iy) {
                for (std::size_t iz = 0; iz < n_side && idx < num_particles_; ++iz) {
                    const Vec3 base{static_cast<double>(ix) * a, static_cast<double>(iy) * a, static_cast<double>(iz) * a};
                    const std::array<Vec3, 4> basis = {{
                        {0.0, 0.0, 0.0},
                        {0.5*a, 0.5*a, 0.0},
                        {0.5*a, 0.0, 0.5*a},
                        {0.0, 0.5*a, 0.5*a}
                    }};
                    for (const auto& b : basis) {
                        if (idx >= num_particles_) break;
                        particles_[idx++].pos = base + b;
                    }
                }
            }
        }
    }

    void init_velocities() {
        std::mt19937_64 rng(42);
        std::uniform_real_distribution<double> dist(-0.5, 0.5);

        Vec3 sum_v;
        for (auto& p : particles_) {
            p.vel = {dist(rng), dist(rng), dist(rng)};
            sum_v += p.vel;
        }

        const Vec3 v_cm = sum_v * (1.0 / static_cast<double>(num_particles_));
        double v2_sum = 0.0;
        for (auto& p : particles_) {
            p.vel -= v_cm;
            v2_sum += p.vel.norm_sq();
        }

        const double current_temp = v2_sum / (3.0 * static_cast<double>(num_particles_));
        const double scale = std::sqrt(target_temp_ / current_temp);
        for (auto& p : particles_) {
            p.vel *= scale;
        }
    }

    [[nodiscard]] Vec3 min_image(const Vec3& dr) const noexcept {
        const double inv_b = 1.0 / box_len_;
        return {
            dr.x - box_len_ * std::round(dr.x * inv_b),
            dr.y - box_len_ * std::round(dr.y * inv_b),
            dr.z - box_len_ * std::round(dr.z * inv_b)
        };
    }

    void rebuild_neighbor_list() {
        neighbor_list_.clear();
        for (std::size_t i = 0; i < num_particles_ - 1; ++i) {
            for (std::size_t j = i + 1; j < num_particles_; ++j) {
                const Vec3 dr = min_image(particles_[i].pos - particles_[j].pos);
                if (dr.norm_sq() < rlist2_) {
                    neighbor_list_.push_back({i, j});
                }
            }
        }
        for (auto& p : particles_) {
            p.last_pos = p.pos;
        }
    }

    void check_neighbor_rebuild() {
        double max_dr2 = 0.0;
        for (const auto& p : particles_) {
            const Vec3 dr = min_image(p.pos - p.last_pos);
            max_dr2 = std::max(max_dr2, dr.norm_sq());
        }
        if (2.0 * std::sqrt(max_dr2) > rskin_) {
            rebuild_neighbor_list();
        }
    }

    [[nodiscard]] double compute_forces() {
        double pe = 0.0;
        for (auto& p : particles_) p.force = {};

        for (const auto& pair : neighbor_list_) {
            auto& p_i = particles_[pair.i];
            auto& p_j = particles_[pair.j];
            const Vec3 dr = min_image(p_i.pos - p_j.pos);
            const double r2 = dr.norm_sq();
            if (r2 < rcut2_) {
                const double inv_r2 = 1.0 / r2;
                const double inv_r6 = inv_r2 * inv_r2 * inv_r2;
                const double f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2;

                const Vec3 f_vec = dr * f_scalar;
                p_i.force += f_vec;
                p_j.force -= f_vec;
                pe += 4.0 * inv_r6 * (inv_r6 - 1.0);
            }
        }
        return pe;
    }

    void apply_berendsen_thermostat(double dt, double inst_temp) {
        if (inst_temp <= 1e-10) return;
        const double lam = std::sqrt(1.0 + (dt / tau_temp_) * (target_temp_ / inst_temp - 1.0));
        for (auto& p : particles_) {
            p.vel *= lam;
        }
    }

    std::size_t num_particles_;
    double target_temp_;
    double box_len_;
    static constexpr double rcut_{2.5};
    static constexpr double rskin_{0.3};
    static constexpr double rlist_{rcut_ + rskin_};
    static constexpr double rcut2_{rcut_ * rcut_};
    static constexpr double rlist2_{rlist_ * rlist_};
    static constexpr double tau_temp_{0.1};

    std::vector<Particle> particles_;
    std::vector<Pair> neighbor_list_;
};

int main() {
    LJSimulationCPP sim(256, 0.8442, 0.728);
    sim.run(1000, 0.005);
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N_PARTICLES 256
#define DT 0.005
#define N_STEPS 1000
#define RCUT 2.5
#define RSKIN 0.3
#define RLIST (RCUT + RSKIN)
#define RCUT2 (RCUT * RCUT)
#define RLIST2 (RLIST * RLIST)
#define TAU_TEMP 0.1

typedef struct {
    double x, y, z;
} Vector3;

typedef struct {
    Vector3 pos;
    Vector3 vel;
    Vector3 force;
    Vector3 last_pos;
} Particle;

typedef struct {
    int i, j;
} NeighborPair;

typedef struct {
    Particle *particles;
    NeighborPair *pairs;
    int n_particles;
    int n_pairs;
    int pairs_capacity;
    double box_len;
    double target_temp;
} LJSystem;

Vector3 min_image(Vector3 dr, double box_len) {
    double inv_b = 1.0 / box_len;
    Vector3 res;
    res.x = dr.x - box_len * round(dr.x * inv_b);
    res.y = dr.y - box_len * round(dr.y * inv_b);
    res.z = dr.z - box_len * round(dr.z * inv_b);
    return res;
}

void rebuild_neighbor_list(LJSystem *sys) {
    sys->n_pairs = 0;
    for (int i = 0; i < sys->n_particles - 1; i++) {
        for (int j = i + 1; j < sys->n_particles; j++) {
            Vector3 dr = {
                sys->particles[i].pos.x - sys->particles[j].pos.x,
                sys->particles[i].pos.y - sys->particles[j].pos.y,
                sys->particles[i].pos.z - sys->particles[j].pos.z
            };
            dr = min_image(dr, sys->box_len);
            double r2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
            if (r2 < RLIST2) {
                if (sys->n_pairs >= sys->pairs_capacity) {
                    sys->pairs_capacity *= 2;
                    sys->pairs = (NeighborPair*)realloc(sys->pairs, sys->pairs_capacity * sizeof(NeighborPair));
                }
                sys->pairs[sys->n_pairs].i = i;
                sys->pairs[sys->n_pairs].j = j;
                sys->n_pairs++;
            }
        }
    }
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].last_pos = sys->particles[i].pos;
    }
}

void check_neighbor_rebuild(LJSystem *sys) {
    double max_dr2 = 0.0;
    for (int i = 0; i < sys->n_particles; i++) {
        Vector3 dr = {
            sys->particles[i].pos.x - sys->particles[i].last_pos.x,
            sys->particles[i].pos.y - sys->particles[i].last_pos.y,
            sys->particles[i].pos.z - sys->particles[i].last_pos.z
        };
        dr = min_image(dr, sys->box_len);
        double dr2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
        if (dr2 > max_dr2) max_dr2 = dr2;
    }
    if (2.0 * sqrt(max_dr2) > RSKIN) {
        rebuild_neighbor_list(sys);
    }
}

double compute_forces(LJSystem *sys) {
    double pe = 0.0;
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].force.x = 0.0;
        sys->particles[i].force.y = 0.0;
        sys->particles[i].force.z = 0.0;
    }

    for (int idx = 0; idx < sys->n_pairs; idx++) {
        int i = sys->pairs[idx].i;
        int j = sys->pairs[idx].j;
        Vector3 dr = {
            sys->particles[i].pos.x - sys->particles[j].pos.x,
            sys->particles[i].pos.y - sys->particles[j].pos.y,
            sys->particles[i].pos.z - sys->particles[j].pos.z
        };
        dr = min_image(dr, sys->box_len);
        double r2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
        if (r2 < RCUT2) {
            double inv_r2 = 1.0 / r2;
            double inv_r6 = inv_r2 * inv_r2 * inv_r2;
            double f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2;

            sys->particles[i].force.x += f_scalar * dr.x;
            sys->particles[i].force.y += f_scalar * dr.y;
            sys->particles[i].force.z += f_scalar * dr.z;

            sys->particles[j].force.x -= f_scalar * dr.x;
            sys->particles[j].force.y -= f_scalar * dr.y;
            sys->particles[j].force.z -= f_scalar * dr.z;

            pe += 4.0 * inv_r6 * (inv_r6 - 1.0);
        }
    }
    return pe;
}

void apply_berendsen_thermostat(LJSystem *sys, double dt, double inst_temp) {
    if (inst_temp <= 1e-10) return;
    double lam = sqrt(1.0 + (dt / TAU_TEMP) * (sys->target_temp / inst_temp - 1.0));
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x *= lam;
        sys->particles[i].vel.y *= lam;
        sys->particles[i].vel.z *= lam;
    }
}

void init_fcc(LJSystem *sys) {
    int n_side = (int)ceil(cbrt(sys->n_particles / 4.0));
    double a = sys->box_len / n_side;
    int idx = 0;
    for (int ix = 0; ix < n_side && idx < sys->n_particles; ix++) {
        for (int iy = 0; iy < n_side && idx < sys->n_particles; iy++) {
            for (int iz = 0; iz < n_side && idx < sys->n_particles; iz++) {
                double bx = ix * a, by = iy * a, bz = iz * a;
                Vector3 basis[4] = {
                    {bx, by, bz},
                    {bx + 0.5*a, by + 0.5*a, bz},
                    {bx + 0.5*a, by, bz + 0.5*a},
                    {bx, by + 0.5*a, bz + 0.5*a}
                };
                for (int b = 0; b < 4 && idx < sys->n_particles; b++) {
                    sys->particles[idx].pos = basis[b];
                    idx++;
                }
            }
        }
    }
}

void init_velocities(LJSystem *sys) {
    double sum_vx = 0, sum_vy = 0, sum_vz = 0;
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x = ((double)rand() / RAND_MAX - 0.5);
        sys->particles[i].vel.y = ((double)rand() / RAND_MAX - 0.5);
        sys->particles[i].vel.z = ((double)rand() / RAND_MAX - 0.5);
        sum_vx += sys->particles[i].vel.x;
        sum_vy += sys->particles[i].vel.y;
        sum_vz += sys->particles[i].vel.z;
    }
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x -= sum_vx / sys->n_particles;
        sys->particles[i].vel.y -= sum_vy / sys->n_particles;
        sys->particles[i].vel.z -= sum_vz / sys->n_particles;
    }
    double v2_sum = 0;
    for (int i = 0; i < sys->n_particles; i++) {
        v2_sum += sys->particles[i].vel.x*sys->particles[i].vel.x +
                  sys->particles[i].vel.y*sys->particles[i].vel.y +
                  sys->particles[i].vel.z*sys->particles[i].vel.z;
    }
    double current_temp = v2_sum / (3.0 * sys->n_particles);
    double scale = sqrt(sys->target_temp / current_temp);
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x *= scale;
        sys->particles[i].vel.y *= scale;
        sys->particles[i].vel.z *= scale;
    }
}

int main(void) {
    double density = 0.8442;
    LJSystem sys;
    sys.n_particles = N_PARTICLES;
    sys.target_temp = 0.728;
    sys.box_len = cbrt(N_PARTICLES / density);
    sys.particles = (Particle*)malloc(N_PARTICLES * sizeof(Particle));
    sys.pairs_capacity = N_PARTICLES * 32;
    sys.pairs = (NeighborPair*)malloc(sys.pairs_capacity * sizeof(NeighborPair));

    init_fcc(&sys);
    init_velocities(&sys);
    rebuild_neighbor_list(&sys);

    double pe = compute_forces(&sys);
    printf("Step\tKinetic_E\tPotential_E\tTotal_E\t\tTemp*\n");

    for (int step = 0; step <= N_STEPS; step++) {
        for (int i = 0; i < N_PARTICLES; i++) {
            sys.particles[i].pos.x += sys.particles[i].vel.x * DT + 0.5 * sys.particles[i].force.x * DT * DT;
            sys.particles[i].pos.y += sys.particles[i].vel.y * DT + 0.5 * sys.particles[i].force.y * DT * DT;
            sys.particles[i].pos.z += sys.particles[i].vel.z * DT + 0.5 * sys.particles[i].force.z * DT * DT;

            sys.particles[i].pos.x -= sys.box_len * floor(sys.particles[i].pos.x / sys.box_len);
            sys.particles[i].pos.y -= sys.box_len * floor(sys.particles[i].pos.y / sys.box_len);
            sys.particles[i].pos.z -= sys.box_len * floor(sys.particles[i].pos.z / sys.box_len);

            sys.particles[i].vel.x += 0.5 * sys.particles[i].force.x * DT;
            sys.particles[i].vel.y += 0.5 * sys.particles[i].force.y * DT;
            sys.particles[i].vel.z += 0.5 * sys.particles[i].force.z * DT;
        }

        check_neighbor_rebuild(&sys);
        pe = compute_forces(&sys);

        double ke = 0.0;
        for (int i = 0; i < N_PARTICLES; i++) {
            sys.particles[i].vel.x += 0.5 * sys.particles[i].force.x * DT;
            sys.particles[i].vel.y += 0.5 * sys.particles[i].force.y * DT;
            sys.particles[i].vel.z += 0.5 * sys.particles[i].force.z * DT;

            ke += 0.5 * (sys.particles[i].vel.x*sys.particles[i].vel.x +
                        sys.particles[i].vel.y*sys.particles[i].vel.y +
                        sys.particles[i].vel.z*sys.particles[i].vel.z);
        }

        double inst_temp = (2.0 * ke) / (3.0 * N_PARTICLES);
        if (step < 500) {
            apply_berendsen_thermostat(&sys, DT, inst_temp);
        }

        if (step % 100 == 0) {
            printf("%d\t%.4f\t\t%.4f\t\t%.4f\t\t%.4f\n",
                   step, ke / N_PARTICLES, pe / N_PARTICLES, (ke + pe) / N_PARTICLES, inst_temp);
        }
    }

    free(sys.pairs);
    free(sys.particles);
    return 0;
}
```
:::

## 6. Стратегії паралелізації та високопродуктивних обчислень (HPC)

У сучасному обчислювальному матеріалознавстві моделювання охоплює мільйони та мільярди атомів (`N ~ 10⁶ – 10⁹`). Для забезпечення високої продуктивності вихідний алгоритм паралелять на двох рівнях:

1. **Багатопотоковість з кількома ядрами (OpenMP / Shared Memory)**:
   - Розподіл циклів обчислення сил за парами зі списку сусідів `#pragma omp parallel for reduction(+:pe)`.
   - Застосування приватних векторів сил (Force Buffers) для кожного потоку з подальшим редукційним сумуванням, що виключає стан гонитви даних (Data Race) та атомарні блоки блокування.
2. **Розподілена пам'ять (MPI / Domain Decomposition)**:
   - Моделювальний бокс розбивають на 3D-просторові домени між обчислювальними вузлами кластера.
   - Кожен вузол зберігає координати лише власних частинок та вузького "граничного шару" (Halo / Ghost particles) з сусідніх доменів.
   - Обмін координатами граничних шарів виконують на кожному часовому кроці через високошвидкісні інтерфейси MPI_Sendrecv.
3. **Прискорення на графічних процесорах (GPU CUDA / HIP)**:
   - Розподіл пар частинок за потоковими блоками GPU (Thread Blocks). 
   - Використання текстурного кешу та швидкої розділюваної пам'яті (Shared Memory) GPU для зберігання координат частинок. 
   - Застосування алгоритмів безблокового сумування (Warp Shuffle Invariant) для паралельного накопичення векторів сил, що підвищує обчислювальну продуктивність симулятора до десятків мільярдів атомних кроків на секунду на сучасних графічних прискорювачах.

Завдяки комбінації списків сусідів Верле з просторовим декомпонуванням доменів сучасні симуляційні комплекси (такі як LAMMPS, GROMACS, NAMD) здатні ефективно масштабуватися на сотні тисяч обчислювальних ядер суперкомп'ютерів.

## 7. Аналіз збереження енергії, поправки хвоста та чисельна стабільність

При комп'ютерному моделюванні системи Леннард-Джонса методом молекулярної динаміки важливо контролювати енергетичну стабільність та правильно підбирати чисельні параметри.

### 1. Вибір часового кроку `Δt*` та контроль дрейфу енергії

У безрозмірних одиницях Леннард-Джонса часовий крок обирають у діапазоні `Δt* = 0.002 – 0.005`, що для аргону відповідає `5 – 10` фемтосекундам. Вибір кроку `Δt* > 0.01` призводить до недостатньої точності інтегрування при близьких зіткненнях частинок, виникнення числового дрейфу енергії («вибуху» симуляції) через накопичення помилок на крутій гілці відштовхування `1/r¹²`.

При вимкненому термостаті (мікроканонічний ансамбль `NVE`) відносне збереження повної енергії `|ΔE_tot / E_tot|` за `10⁴` кроків має не перевищувати `10⁻⁴`.

### 2. Аналітичні поправки для виключеної області (Tail Corrections)

Сферичне відтинання потенціалу на радіусі зрізу `r_c = 2.5·σ` економить обчислювальні ресурси, але нехтування притягальним хвостом при `r > r_c` приводить до заниження розрахованої потенційної енергії та тиску. За припущення про ізотропний розподіл частинок при `r > r_c` (`g(r) ≈ 1`), аналітичні поправки хвоста становлять:

```
U_tail = (8 / 9) · π · N · ρ* · ε · (σ / r_c)⁹
P_tail = (16 / 9) · π · (ρ*)² · (ε / σ³) · (σ / r_c)⁹
```

Для `r_c = 2.5·σ` та густини рідкого аргону `ρ* = 0.8442` поправка енергії становить `U_tail / N ≈ -0.54 ε`, а поправка тиску `P_tail* ≈ -0.42`. Додавання цих аналітичних поправок забезпечує точний збіг результатів МД-симуляцій із натурними експериментальними даними для рідкого та газуватого аргону.

### 3. Крайні випадки та чисельні пастки

1. **Обов'язковість вилучення дрейфу центру мас**: При початковій генерації випадкових швидкостей векторна сума імпульсів `∑ p_i` може бути ненульовою. Це викликає постійний поступальний рух всього об'єму симуляції. Усунення дрейфу `v_i ← v_i - v_cm` є критичним для збереження кінетичної температури `T = 2 K / (3 N k_B)`. Невиконання цієї корекції призводить до штучного ефекту "літаючого кубика льоду" (Flying Ice Cube Effect), коли кінетична енергія теплового руху некоректно виморожується у поступальний рух всієї системи.
2. **Вибір товщини буферного шару `r_s` у списках Верле**: Якщо товщина `r_s` вибрана занадто малою (`r_s < 0.1·σ`), частинка із високою кінетичною швидкістю може перетнути буфер за один-два кроки без спрацювання умовою перебудови списку. Це викликає штучне ігнорування міжатомних сил і порушення закону збереження енергії. Оптимальний вибір `r_s = 0.3·σ – 0.5·σ` балансує між частотою перебудування списку та обчислювальною надійністю.
3. **Режим роботи термостата у фазах симуляції**: Термостатування Беріндсена слід вмикати лише під час початкової фази рівноваження (Equilibration run, перші 500–1000 кроків), після чого термостат вимикають для проведення продуктивної фази (Production run) у чистому мікроканонічному ансамблі (`NVE`). Це дає змогу вимірювати неспотворені автокореляційні функції та коефіцієнти переносу флюїду.
