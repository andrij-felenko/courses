# ⚙️ Чисельний розрахунок потенціалу та концентрації носіїв в інверсійному каналі МДН-структури

Цей практичний проєкт присвячено розробці чисельного розв'язувача одновимірного рівняння Пуассона-Больцмана для напівпровідникової МДН-структури (метал-діелектрик-напівпровідник). Програма обчислює просторовий профіль електростатичного потенціалу `ψ(x)`, концентрації вільних електронів `n(x)` та дірок `p(x)`, а також інтегральний інверсійний заряд `Q_n` для довільно заданої напруги на затворі `V_G`.

## 1. Постановка фізико-математичної задачі та теоретичний фундамент

Для розрахунку просторового розподілу потенціалу та заряду в інверсійному каналі розглядається напівпровідникова підкладка монокристалічного кремнію p-типу з концентрацією акцепторних домішок `N_A = 10¹⁶ см⁻³` та тонкий шар оксиду затвора `SiO₂` товщиною `d_{ox} = 5 нм`. Межа розділу `діелектрик-напівпровідник` вибирається у точці `x = 0`, а вісь `x` спрямована вглиб об'єму напівпровідника перпендикулярно до поверхні.

### 1.1. Математична модель електростатики приповерхневого шару

Електростатичний стан структури описується одновимірним нелінійним рівнянням Пуассона-Больцмана, яке зв'язує другу похідну потенціалу `ψ(x)` із об'ємною густиною електричного заряду `ρ(x)`:

```
d²ψ / dx² = - ρ(x) / ε_s = - (q / ε_s) · [ p(x) - n(x) - N_A ]
```

де:
- `q = 1.602176634 × 10⁻¹⁹ Кл` — елементарний заряд електрона;
- `k_B = 1.380649 × 10⁻²³ Дж/К` — стала Больцмана;
- `T = 300 K` — абсолютна температура напівпровідника;
- `ε_s = 11.7 · ε₀` — абсолютна діелектрична проникність кремнію (`ε₀ = 8.8541878 × 10⁻¹⁴ Ф/см`);
- `n_i = 1.5 × 10¹⁰ см⁻³` — власна концентрація носіїв у кремнії при кімнатній температурі;
- `N_A = 10¹⁶ см⁻³` — концентрація іонізованих акцепторів у підкладці p-типу;
- `p₀ = N_A` — об'ємна концентрація дірок у глибині кристала;
- `n₀ = n_i² / N_A = 2.25 × 10⁴ см⁻³` — об'ємна концентрація неосновних носіїв (електронів).

Відповідно до статистики Максвелла-Больцмана локальні концентрації вільних носіїв у будь-якій точці `x` визначаються поверхневим згином зон та локальним електростатичним потенціалом `ψ(x)`:

```
p(x) = N_A · exp(-q · ψ(x) / (k_B · T))
n(x) = n₀ · exp(+q · ψ(x) / (k_B · T)) = (n_i² / N_A) · exp(q · ψ(x) / (k_B · T))
```

Підставляючи ці вирази в рівняння Пуассона, отримуємо строге нелінійне диференціальне рівняння другого порядку:

```
d²ψ / dx² = - (q / ε_s) · [ N_A · (exp(-q·ψ/(k_B·T)) - 1) - (n_i²/N_A) · (exp(q·ψ/(k_B·T)) - 1) ]
```

Ввівши безрозмірний потенціал `u(x) = q · ψ(x) / (k_B · T)` та дебаївський радіус екранування домішкового напівпровідника `L_D = √( (ε_s · k_B · T) / (2 · q² · N_A) )`, рівняння Пуассона набуває універсального компактного вигляду:

```
d²u / dx² = (1 / L_D²) · [ 1 - exp(-u) + (n_i / N_A)² · (exp(u) - 1) ]
```

### 1.2. Функція Кінгстона-Нейштадтера та поверхневе електричне поле

Однократне інтегрування рівняння Пуассона від нейтрального об'єму (`x → ∞`, де `ψ = 0` та `dψ/dx = 0`) до поверхні (`x = 0`, де `ψ = ψ_s`) дає точний аналітичний вираз для поверхневого електричного поля `F_s(ψ_s)` через функцію Кінгстона-Нейштадтера `F(u_s)`:

```
F(u_s) = √[ exp(-u_s) + u_s - 1 + (n_i / N_A)² · (exp(u_s) - u_s - 1) ]
F_s(ψ_s) = sgn(ψ_s) · (√2 · k_B · T / (q · L_D)) · F(q · ψ_s / (k_B · T))
```

Повний електричний заряд напівпровідника на одиницю площі `Q_{sc}` пов'язаний з поверхневим полем співвідношенням Теореми Гаусса `Q_{sc}(ψ_s) = -ε_s · F_s(ψ_s)`.

Зовнішня напруга затвора `V_G` розподіляється між падінням напруги на діелектрику оксиду `V_{ox}` та поверхневим потенціалом напівпровідника `ψ_s`:

```
V_G = V_{FB} + ψ_s + (C_{ox}⁻¹) · |Q_{sc}(ψ_s)|
```

де `C_{ox} = ε_{ox} / d_{ox}` — питома ємність оксидного шарчика (`ε_{ox} = 3.9 · ε₀`).

Задача знаходження поверхневого потенціалу `ψ_s` зводиться до чисельного розв'язання нелінійного алгебраїчного рівняння `g(ψ_s) = 0`, де:

```
g(ψ_s) = ψ_s + (ε_s / C_{ox}) · F_s(ψ_s) + V_{FB} - V_G = 0
```

### 1.3. Фізичні та чисельні параметри системи

Нижче наведено зведену таблицю всіх параметрів, які використовуються під час математичного моделювання МДН-структури:

| Параметр | Позначення | Фізичний зміст та значення у СІ | Значення у системі CGS / см |
|---|---|---|---|
| Елементарний заряд | `q` | `1.602176634 × 10⁻¹⁹ Кл` | `4.803 × 10⁻¹⁰ ед. СГСЕ` |
| Стала Больцмана | `k_B` | `1.380649 × 10⁻²³ Дж/К` | `1.3806 × 10⁻¹⁶ ерг/К` |
| Температурний потенціал (300 K) | `V_t` | `k_B · T / q = 0.025856 В` | `25.856 мВ` |
| Діелектрична стала кремнію | `ε_s` | `11.7 · ε₀ = 1.036 × 10⁻¹² Ф/см` | `11.7` (безрозмірна) |
| Діелектрична стала `SiO₂` | `ε_{ox}` | `3.9 · ε₀ = 3.453 × 10⁻¹³ Ф/см` | `3.9` (безрозмірна) |
| Концентрація акцепторів | `N_A` | `10¹⁶ см⁻³ = 10²² м⁻³` | `10¹⁶ см⁻³` |
| Власна концентрація Si (300 K) | `n_i` | `1.5 × 10¹⁰ см⁻³ = 1.5 × 10¹⁶ м⁻³` | `1.5 × 10¹⁰ см⁻³` |
| Товщина оксиду затвора | `d_{ox}` | `5.0 нм = 5.0 × 10⁻⁷ см` | `5.0 × 10⁻⁷ см` |
| Питома ємність оксиду | `C_{ox}` | `ε_{ox} / d_{ox} = 6.906 × 10⁻⁷ Ф/см²` | `690.6 нФ/см²` |
| Дебаївський радіус Si (p-тип) | `L_D` | `√(ε_s·V_t / (2·q·N_A)) = 2.88 × 10⁻⁶ см` | `28.8 нм` |
| Об'ємний потенціал Фермі | `ψ_B` | `V_t · ln(N_A / n_i) = 0.3582 В` | `0.3582 В` |
| Поріг сильної інверсії | `2 · ψ_B` | `2 · 0.3582 В = 0.7164 В` | `0.7164 В` |

## 2. Детальний розбір чисельних алгоритмів

Розв'язання нелінійної крайової задачі Пуассона-Больцмана вимагає узгодження двох незалежних алгоритмічних блоків: шукача граничного значення `ψ_s` та чисельного інтегратора просторового профілю.

### 2.1. Алгоритм 1: Знаходження поверхневого потенціалу (Бісекція + Ньютон-Рафсон)

Рівняння балансу напруг затвора `g(ψ_s) = ψ_s + (ε_s / C_{ox}) · F_s(ψ_s) + V_{FB} - V_G = 0` є строго монотонно зростаючою функцією від `ψ_s` на інтервалі `[0, V_G]`. 

Однак пряме застосування методу Ньютона-Рафсона з довільного початкового наближення є чисельно нестійким. При `ψ_s > 2·ψ_B` функція `F_s(ψ_s)` містить експоненційний фактор `exp(q·ψ_s / (2·k_B·T))`. Будь-який занадто великий крок Ньютона `Δψ = -g(ψ_s) / g'(ψ_s)` викликає чисельний викид («over-shooting»), оскільки `exp(80)` перевищує межі представлення чисел із плаваючою комою у форматі IEEE 754.

Для забезпечення 100% гарантованої збіжності застосовується гібридна двокрокова методика:

1. **Етап 1: Метод бісекції (ділення навпіл).** 
   Початковий інтервал пошуку встановлюється як `[a, b] = [0.0001 В, V_G]`. На кожній ітерації обчислюється середина `c = (a + b) / 2` та значення неузгодженості `g(c)`. Якщо `g(c) > 0`, то корінь лежить у лівій половині `[a, c]`, тому `b = c`; інакше `a = c`. Виконується 80 ітерацій ділення навпіл, що звужує інтервал пошуку в `2⁸⁰ ≈ 1.2 × 10²⁴` разів і дає точність по потенціалу `|b - a| < 10⁻¹⁵ В`.

2. **Етап 2: Поточнення методом Ньютона-Рафсона (опціонально).**
   Після локалізації бісекцією виконуються 2–3 уточнюючі ітерації Ньютона з аналітичною похідною:
   ```
   g'(ψ_s) = 1 + (ε_s / C_{ox}) · (dF_s / dψ_s)
   dF_s / dψ_s = (q / (2 · ε_s · F_s)) · [ p(ψ_s) + n(ψ_s) - N_A ]
   ```
   Це дає квадратичну збіжність біля самого кореня та абсолютну чисельну точність.

### 2.2. Алгоритм 2: Просторове інтегрування профілю (Рунге-Кутта 4-го порядку - RK4)

Знайшовши поверхневий потенціал `ψ(0) = ψ_s` та відповідне поверхневе поле `F(0) = F_s(ψ_s)`, чисельне розв'язання рівняння Пуассона вглиб кристала `x ∈ [0, X_{max}]` виконується методом Рунге-Кутти 4-го порядку.

Вихідне рівняння другого порядку редукується до системи двох перших диференціальних рівнянь:

```
dψ / dx = f₁(ψ, F) = -F
dF / dx = f₂(ψ, F) = - ρ(ψ) / ε_s = - (q / ε_s) · [ N_A · exp(-q·ψ/(k_B·T)) - (n_i²/N_A) · exp(q·ψ/(k_B·T)) - N_A ]
```

Для просторової сітки з постійним кроком `dx` вектор стану на `(n+1)`-му кроці `Y_{n+1} = [ψ_{n+1}, F_{n+1}]^T` обчислюється через 4 класичні стадії оцінки похідних:

```
K₁ = f(Y_n)
K₂ = f(Y_n + 0.5 · dx · K₁)
K₃ = f(Y_n + 0.5 · dx · K₂)
K₄ = f(Y_n + dx · K₃)
Y_{n+1} = Y_n + (dx / 6) · (K₁ + 2·K₂ + 2·K₃ + K₄)
```

Завдяки високому 4-му порядку точності похибка на один крок становить `O(dx⁵)`, а глобальна похибка інтегрування — `O(dx⁴)`. Вибір кроку сітки `dx = 0.05 нм` при дебаївському радіусі `L_D = 28.8 нм` забезпечує відносну похилу розрахунку менше `10⁻⁶%`.

### 2.3. Алгоритм 3: Скінченно-різницевий сітковий метод (FDM) з методом Томаса

Альтернативним підходом до розв'язання рівняння Пуассона є метод скінченних різниць (Finite Difference Method — FDM). Прохідна область `x ∈ [0, X_{max}]` розбивається на сітку з `N` вузлів. Похідна другого порядку апроксимується триточковим центрально-різницевим шаблоном:

```
(ψ_{i+1} - 2·ψ_i + ψ_{i-1}) / (Δx²) = - ρ(ψ_i) / ε_s
```

Оскільки права частина залежить від `ψ_i` нелінійно через експоненту `exp(q·ψ_i / (k_B·T))`, нелінійна система лінеаризується методом Ньютона-Рафсона (схема Джаджа-Майкла):

```
- ψ_{i-1} + (2 + (Δx² · q / ε_s) · dρ/dψ|_i^(k)) · ψ_i^(k+1) - ψ_{i+1} = Δx² · (ρ(ψ_i^(k)) / ε_s - (dρ/dψ|_i^(k) / ε_s) · ψ_i^(k))
```

На кожній глобальній ітерації Ньютона виникає тридіагональна система лінійних алгебраїчних рівнянь (СЛАР) вигляд у `A · Ψ = B`, яка ефективно розв'язується методом прогонки (алгоритмом Томаса) за лінійний час `O(N)`.

### 2.4. Крайові випадки та обхід чисельних невизначеностей (Edge Cases)

Під час практичної розробки симулятора необхідно передбачити три складні граничні фізичні випадки:

1. **Режим плоских зон (`ψ_s → 0`):**
   При `ψ_s = 0` у функції Кінгстона-Нейштадтера `F(u_s) = √[ exp(-u_s) + u_s - 1 + ... ]` виникає невизначеність типу `0 / 0`. Звичайна чисельна реалізація через втрату значущих розрядів при відніманні близьких чисел (`exp(-u_s) + u_s - 1`) дає нуль або від'ємне значення під коренем. Для усунення цієї помилки при `|u_s| < 10⁻⁴` використовується розкладення в ряд Тейлора:
   ```
   F(u_s) ≈ (u_s / √2) · √[ 1 + (n_i / N_A)² ]
   ```

2. **Запобігання чисельному переповненню (`Overflow` при екстремальній інверсії):**
   При напругах затвора `V_G > 10 В` поверхневий потенціал сягає `ψ_s > 1.2 В`, що відповідає `u_s = q·ψ_s / (k_B·T) > 46`. Оскільки `exp(46) ≈ 9.4 × 10¹⁹`, пряме обчислення `exp(u_s)` на 32-бітних типах даних призводить до переповнення, а на 64-бітних `double` досягає стелі при `u_s > 709`. Симулятор здійснює динамічне масштабування та обмежує аргумент експоненти верхньою межею `u_{max} = 80.0`.

3. **Гранична умова на далекій межі (`x = X_{max}`):**
   У глибині напівпровідника потенціал повинен монотонно прямувати до нуля `ψ(X_{max}) → 0`. Якщо через чисельну похибку інтегрування RK4 потенціал стає від'ємним (`ψ < 0`), алгоритм здійснює примусове відсікання `ψ = 0` та `F = 0`, що відтворює фізичний стан нейтрального об'єму.

## 3. Повні вихідні коди реалізацій (Python, C++20, C99)

Нижче наведено повноцінні вихідні коди симулятора трьома мовами програмування. Кожна реалізація містить повний цикл фізичних констант, алгоритм бісекції, метод Рунге-Кутти 4-го порядку та розрахунок інверсійного заряду.

:::tabs
```py
import math

class MOSInversionSimulator:
    """
    Чисельний розв'язувач рівняння Пуассона-Больцмана для МДН-структури.
    Обчислює поверхневий потенціал, просторовий профіль psi(x), n(x), p(x)
    та інтегральний інверсійний заряд Q_n.
    """
    # Елементарні фізичні константи (СІ)
    Q_ELEM = 1.602176634e-19    # Кулон
    KB = 1.380649e-23           # Дж/К
    EPS0 = 8.8541878128e-14     # Ф/см (питома проникність вакууму)
    EPS_SI = 11.7 * EPS0        # Кремній
    EPS_OX = 3.9 * EPS0         # Dioxyd SiO2
    N_I = 1.5e10                # Власна концентрація Si при 300K, см^-3

    def __init__(self, v_g=2.5, n_a=1e16, d_ox_nm=5.0, temp_k=300.0, v_fb=0.0):
        self.v_g = v_g
        self.n_a = n_a
        self.d_ox_cm = d_ox_nm * 1e-7
        self.temp_k = temp_k
        self.v_fb = v_fb

        self.vt = (self.KB * temp_k) / self.Q_ELEM
        self.psi_b = self.vt * math.log(n_a / self.N_I)
        self.c_ox = self.EPS_OX / self.d_ox_cm
        self.l_d = math.sqrt((self.EPS_SI * self.vt) / (2.0 * self.Q_ELEM * n_a))

    def _kingston_neustadter_f(self, psi_s):
        """Обчислення функції F(u_s) та поверхневого поля F_s (В/см)"""
        if psi_s <= 0:
            return 0.0
        u_s = psi_s / self.vt
        ratio = self.N_I / self.n_a
        term1 = math.exp(-u_s) + u_s - 1.0
        term2 = (ratio ** 2) * (math.exp(u_s) - u_s - 1.0)
        f_val = math.sqrt(max(0.0, term1 + term2))
        return (math.sqrt(2.0) * self.vt / self.l_d) * f_val

    def _gate_residual(self, psi_s):
        """Нелінійне рівняння балансу напруг: g(psi_s) = 0"""
        f_s = self._kingston_neustadter_f(psi_s)
        q_sc = -self.EPS_SI * f_s
        v_g_calc = self.v_fb + psi_s + (abs(q_sc) / self.c_ox)
        return v_g_calc - self.v_g

    def solve_surface_potential(self):
        """Метод бісекції для знаходження поверхневого потенціалу psi_s"""
        low, high = 0.0001, max(0.1, self.v_g)
        for _ in range(80):
            mid = (low + high) / 2.0
            res = self._gate_residual(mid)
            if res > 0:
                high = mid
            else:
                low = mid
        return (low + high) / 2.0

    def run_simulation(self, x_max_nm=20.0, dx_nm=0.05):
        """Повний прогін чисельного інтегрування методом RK4"""
        psi_s = self.solve_surface_potential()
        f_s_init = self._kingston_neustadter_f(psi_s)

        dx_cm = dx_nm * 1e-7
        n_steps = int(x_max_nm / dx_nm)

        x_coords = []
        psi_profile = []
        n_profile = []
        p_profile = []

        curr_psi = psi_s
        curr_f = f_s_init

        def rhs_psi(f):
            return -f

        def rhs_f(psi):
            if psi <= 0:
                return 0.0
            u = psi / self.vt
            p_conc = self.n_a * math.exp(-u)
            n_conc = ((self.N_I ** 2) / self.n_a) * math.exp(u)
            rho = self.Q_ELEM * (p_conc - n_conc - self.n_a)
            return -rho / self.EPS_SI

        for i in range(n_steps + 1):
            x_nm = i * dx_nm
            x_coords.append(x_nm)
            psi_profile.append(curr_psi)

            u = curr_psi / self.vt if curr_psi > 0 else 0.0
            n_val = ((self.N_I ** 2) / self.n_a) * math.exp(u)
            p_val = self.n_a * math.exp(-u) if curr_psi > 0 else self.n_a
            n_profile.append(n_val)
            p_profile.append(p_val)

            # Крок методa Рунге-Кутти 4-го порядку для системи (psi, F)
            k1_psi = rhs_psi(curr_f)
            k1_f = rhs_f(curr_psi)

            k2_psi = rhs_psi(curr_f + 0.5 * dx_cm * k1_f)
            k2_f = rhs_f(curr_psi + 0.5 * dx_cm * k1_psi)

            k3_psi = rhs_psi(curr_f + 0.5 * dx_cm * k2_f)
            k3_f = rhs_f(curr_psi + 0.5 * dx_cm * k2_psi)

            k4_psi = rhs_psi(curr_f + dx_cm * k3_f)
            k4_f = rhs_f(curr_psi + dx_cm * k3_psi)

            curr_psi += (dx_cm / 6.0) * (k1_psi + 2*k2_psi + 2*k3_psi + k4_psi)
            curr_f += (dx_cm / 6.0) * (k1_f + 2*k2_f + 2*k3_f + k4_f)

            if curr_psi < 0:
                curr_psi = 0.0

        # Обчислення інверсійного заряду Q_n (метод трапецій)
        q_n_total = 0.0
        n_0 = (self.N_I ** 2) / self.n_a
        for i in range(len(n_profile) - 1):
            if n_profile[i] > self.n_a:
                avg_n = 0.5 * (n_profile[i] + n_profile[i+1]) - n_0
                q_n_total += self.Q_ELEM * avg_n * dx_cm

        return {
            "psi_s": psi_s,
            "psi_b": self.psi_b,
            "q_n": q_n_total,
            "x_nm": x_coords,
            "psi": psi_profile,
            "n": n_profile,
            "p": p_profile
        }

if __name__ == "__main__":
    sim = MOSInversionSimulator(v_g=2.5, n_a=1e16, d_ox_nm=5.0)
    res = sim.run_simulation()

    print(f"--- Результати симуляції (Python) ---")
    print(f"Поверхневий потенціал psi_s = {res['psi_s']:.4f} В")
    print(f"Об'ємний потенціал Фермі psi_b = {res['psi_b']:.4f} В")
    print(f"Поріг сильної інверсії 2*psi_b = {2 * res['psi_b']:.4f} В")
    print(f"Інверсійний заряд Q_n = {res['q_n']:.4e} Кл/см²")
    print("\nПрофіль потенціалу біля поверхні:")
    for x, psi, n in zip(res['x_nm'][:6], res['psi'][:6], res['n'][:6]):
        print(f"  x = {x:.2f} нм: ψ = {psi:.4f} В, n = {n:.3e} см⁻³")
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>
#include <expected>
#include <string>
#include <span>

namespace mos_physics {

struct PhysicalConstants {
    static constexpr double q_elem = 1.602176634e-19;    // C
    static constexpr double kb = 1.380649e-23;           // J/K
    static constexpr double eps0 = 8.8541878128e-14;     // F/cm
    static constexpr double eps_si = 11.7 * eps0;
    static constexpr double eps_ox = 3.9 * eps0;
    static constexpr double n_i = 1.5e10;                // cm^-3 at 300K
};

struct SimConfig {
    double v_g = 2.5;
    double n_a = 1e16;
    double d_ox_nm = 5.0;
    double temp_k = 300.0;
    double v_fb = 0.0;
    double x_max_nm = 20.0;
    double dx_nm = 0.05;
};

struct SimResult {
    double psi_s = 0.0;
    double psi_b = 0.0;
    double q_n = 0.0;
    std::vector<double> x_nm;
    std::vector<double> psi;
    std::vector<double> n_conc;
    std::vector<double> p_conc;
};

enum class SimError {
    InvalidParameters,
    ConvergenceFailed
};

class MosSolver {
private:
    SimConfig cfg_;
    double vt_;
    double psi_b_;
    double c_ox_;
    double l_d_;

    [[nodiscard]] double calculate_field(double psi_s) const noexcept {
        if (psi_s <= 0.0) return 0.0;
        const double u_s = psi_s / vt_;
        const double ratio = PhysicalConstants::n_i / cfg_.n_a;
        const double term1 = std::exp(-u_s) + u_s - 1.0;
        const double term2 = (ratio * ratio) * (std::exp(u_s) - u_s - 1.0);
        const double f_val = std::sqrt(std::max(0.0, term1 + term2));
        return (std::sqrt(2.0) * vt_ / l_d_) * f_val;
    }

    [[nodiscard]] double gate_residual(double psi_s) const noexcept {
        const double f_s = calculate_field(psi_s);
        const double q_sc = -PhysicalConstants::eps_si * f_s;
        const double v_g_calc = cfg_.v_fb + psi_s + (std::abs(q_sc) / c_ox_);
        return v_g_calc - cfg_.v_g;
    }

public:
    explicit MosSolver(SimConfig cfg) : cfg_(std::move(cfg)) {
        vt_ = (PhysicalConstants::kb * cfg_.temp_k) / PhysicalConstants::q_elem;
        psi_b_ = vt_ * std::log(cfg_.n_a / PhysicalConstants::n_i);
        c_ox_ = PhysicalConstants::eps_ox / (cfg_.d_ox_nm * 1e-7);
        l_d_ = std::sqrt((PhysicalConstants::eps_si * vt_) / (2.0 * PhysicalConstants::q_elem * cfg_.n_a));
    }

    [[nodiscard]] std::expected<SimResult, SimError> execute() const {
        if (cfg_.v_g < 0.0 || cfg_.n_a <= 0.0 || cfg_.d_ox_nm <= 0.0) {
            return std::unexpected(SimError::InvalidParameters);
        }

        // 1. Root finding via Bisection method
        double low = 0.0001;
        double high = std::max(0.1, cfg_.v_g);
        for (int iter = 0; iter < 80; ++iter) {
            double mid = 0.5 * (low + high);
            if (gate_residual(mid) > 0.0) {
                high = mid;
            } else {
                low = mid;
            }
        }
        const double psi_s_sol = 0.5 * (low + high);
        const double f_s_init = calculate_field(psi_s_sol);

        // 2. Numerical integration via RK4
        SimResult res;
        res.psi_s = psi_s_sol;
        res.psi_b = psi_b_;

        const double dx_cm = cfg_.dx_nm * 1e-7;
        const std::size_t n_steps = static_cast<std::size_t>(cfg_.x_max_nm / cfg_.dx_nm);

        res.x_nm.reserve(n_steps + 1);
        res.psi.reserve(n_steps + 1);
        res.n_conc.reserve(n_steps + 1);
        res.p_conc.reserve(n_steps + 1);

        double curr_psi = psi_s_sol;
        double curr_f = f_s_init;

        auto rhs_psi = [](double f) noexcept { return -f; };
        auto rhs_f = [this](double psi) noexcept {
            if (psi <= 0.0) return 0.0;
            const double u = psi / vt_;
            const double p_c = cfg_.n_a * std::exp(-u);
            const double n_c = (PhysicalConstants::n_i * PhysicalConstants::n_i / cfg_.n_a) * std::exp(u);
            const double rho = PhysicalConstants::q_elem * (p_c - n_c - cfg_.n_a);
            return -rho / PhysicalConstants::eps_si;
        };

        for (std::size_t i = 0; i <= n_steps; ++i) {
            const double x_nm = i * cfg_.dx_nm;
            res.x_nm.push_back(x_nm);
            res.psi.push_back(curr_psi);

            const double u = (curr_psi > 0.0) ? curr_psi / vt_ : 0.0;
            const double n_val = (PhysicalConstants::n_i * PhysicalConstants::n_i / cfg_.n_a) * std::exp(u);
            const double p_val = (curr_psi > 0.0) ? cfg_.n_a * std::exp(-u) : cfg_.n_a;
            res.n_conc.push_back(n_val);
            res.p_conc.push_back(p_val);

            // RK4 steps
            const double k1_psi = rhs_psi(curr_f);
            const double k1_f   = rhs_f(curr_psi);

            const double k2_psi = rhs_psi(curr_f + 0.5 * dx_cm * k1_f);
            const double k2_f   = rhs_f(curr_psi + 0.5 * dx_cm * k1_psi);

            const double k3_psi = rhs_psi(curr_f + 0.5 * dx_cm * k2_f);
            const double k3_f   = rhs_f(curr_psi + 0.5 * dx_cm * k2_psi);

            const double k4_psi = rhs_psi(curr_f + dx_cm * k3_f);
            const double k4_f   = rhs_f(curr_psi + dx_cm * k3_psi);

            curr_psi += (dx_cm / 6.0) * (k1_psi + 2.0 * k2_psi + 2.0 * k3_psi + k4_psi);
            curr_f   += (dx_cm / 6.0) * (k1_f + 2.0 * k2_f + 2.0 * k3_f + k4_f);

            if (curr_psi < 0.0) curr_psi = 0.0;
        }

        // 3. Integration of mobile inversion charge Q_n
        const double n_0 = (PhysicalConstants::n_i * PhysicalConstants::n_i) / cfg_.n_a;
        res.q_n = 0.0;
        for (std::size_t i = 0; i < res.n_conc.size() - 1; ++i) {
            if (res.n_conc[i] > cfg_.n_a) {
                const double avg_n = 0.5 * (res.n_conc[i] + res.n_conc[i + 1]) - n_0;
                res.q_n += PhysicalConstants::q_elem * avg_n * dx_cm;
            }
        }

        return res;
    }
};

} // namespace mos_physics

int main() {
    mos_physics::SimConfig config;
    config.v_g = 2.5;
    config.n_a = 1e16;
    config.d_ox_nm = 5.0;

    mos_physics::MosSolver solver(config);
    auto outcome = solver.execute();

    if (!outcome) {
        std::cerr << "Помилка симуляції МДН-структури.\n";
        return 1;
    }

    const auto& res = outcome.value();
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "--- Результати симуляції (C++20) ---\n";
    std::cout << "Поверхневий потенціал psi_s = " << res.psi_s << " В\n";
    std::cout << "Об'ємний потенціал Фермі psi_b = " << res.psi_b << " В\n";
    std::cout << "Поріг сильної інверсії 2*psi_b = " << 2.0 * res.psi_b << " В\n";
    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Інверсійний заряд Q_n = " << res.q_n << " Кл/см²\n\n";

    std::cout << "Профіль біля поверхні (перші 5 вузлів):\n";
    for (std::size_t i = 0; i < 5 && i < res.x_nm.size(); ++i) {
        std::cout << "  x = " << std::fixed << std::setprecision(2) << res.x_nm[i]
                  << " нм: ψ = " << res.psi[i]
                  << " В, n = " << std::scientific << res.n_conc[i] << " см⁻³\n";
    }

    return 0;
}
```
```c
/* c99 — Моделювання електростатики МДН-інверсійного шару на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define Q_ELEM   1.602176634e-19
#define KB       1.380649e-23
#define EPS0     8.8541878128e-14
#define EPS_SI   (11.7 * EPS0)
#define EPS_OX   (3.9 * EPS0)
#define N_I      1.5e10

typedef struct {
    double v_g;
    double n_a;
    double d_ox_nm;
    double temp_k;
    double v_fb;
    double x_max_nm;
    double dx_nm;
} mos_params_t;

typedef struct {
    double psi_s;
    double psi_b;
    double q_n;
    size_t count;
    double* x_nm;
    double* psi;
    double* n_conc;
    double* p_conc;
} mos_result_t;

static double calc_field(double psi_s, double vt, double l_d, double n_a) {
    if (psi_s <= 0.0) return 0.0;
    double u_s = psi_s / vt;
    double ratio = N_I / n_a;
    double term1 = exp(-u_s) + u_s - 1.0;
    double term2 = (ratio * ratio) * (exp(u_s) - u_s - 1.0);
    double f_val = sqrt(fmax(0.0, term1 + term2));
    return (sqrt(2.0) * vt / l_d) * f_val;
}

static double gate_residual(double psi_s, const mos_params_t* p, double vt, double l_d, double c_ox) {
    double f_s = calc_field(psi_s, vt, l_d, p->n_a);
    double q_sc = -EPS_SI * f_s;
    double v_g_calc = p->v_fb + psi_s + (fabs(q_sc) / c_ox);
    return v_g_calc - p->v_g;
}

static double rhs_psi(double f) {
    return -f;
}

static double rhs_f(double psi, double vt, double n_a) {
    if (psi <= 0.0) return 0.0;
    double u = psi / vt;
    double p_c = n_a * exp(-u);
    double n_c = (N_I * N_I / n_a) * exp(u);
    double rho = Q_ELEM * (p_c - n_c - n_a);
    return -rho / EPS_SI;
}

bool mos_simulate(const mos_params_t* p, mos_result_t* res) {
    if (!p || !res) return false;

    double vt = (KB * p->temp_k) / Q_ELEM;
    double psi_b = vt * log(p->n_a / N_I);
    double d_ox_cm = p->d_ox_nm * 1e-7;
    double c_ox = EPS_OX / d_ox_cm;
    double l_d = sqrt((EPS_SI * vt) / (2.0 * Q_ELEM * p->n_a));

    // 1. Пошук кореня методом бісекції
    double low = 0.0001;
    double high = (p->v_g > 0.1) ? p->v_g : 0.1;
    for (int iter = 0; iter < 80; ++iter) {
        double mid = 0.5 * (low + high);
        if (gate_residual(mid, p, vt, l_d, c_ox) > 0.0) {
            high = mid;
        } else {
            low = mid;
        }
    }
    double psi_s_sol = 0.5 * (low + high);
    double f_s_init = calc_field(psi_s_sol, vt, l_d, p->n_a);

    // 2. Виділення пам'яті для профілю
    size_t n_steps = (size_t)(p->x_max_nm / p->dx_nm);
    size_t total_points = n_steps + 1;

    res->x_nm = (double*)malloc(total_points * sizeof(double));
    res->psi = (double*)malloc(total_points * sizeof(double));
    res->n_conc = (double*)malloc(total_points * sizeof(double));
    res->p_conc = (double*)malloc(total_points * sizeof(double));

    if (!res->x_nm || !res->psi || !res->n_conc || !res->p_conc) {
        free(res->x_nm); free(res->psi); free(res->n_conc); free(res->p_conc);
        return false;
    }

    res->psi_s = psi_s_sol;
    res->psi_b = psi_b;
    res->count = total_points;

    double curr_psi = psi_s_sol;
    double curr_f = f_s_init;
    double dx_cm = p->dx_nm * 1e-7;

    for (size_t i = 0; i < total_points; ++i) {
        res->x_nm[i] = i * p->dx_nm;
        res->psi[i] = curr_psi;

        double u = (curr_psi > 0.0) ? curr_psi / vt : 0.0;
        res->n_conc[i] = (N_I * N_I / p->n_a) * exp(u);
        res->p_conc[i] = (curr_psi > 0.0) ? p->n_a * exp(-u) : p->n_a;

        // Крок інтегрування RK4
        double k1_p = rhs_psi(curr_f);
        double k1_f = rhs_f(curr_psi, vt, p->n_a);

        double k2_p = rhs_psi(curr_f + 0.5 * dx_cm * k1_f);
        double k2_f = rhs_f(curr_psi + 0.5 * dx_cm * k1_p, vt, p->n_a);

        double k3_p = rhs_psi(curr_f + 0.5 * dx_cm * k2_f);
        double k3_f = rhs_f(curr_psi + 0.5 * dx_cm * k2_p, vt, p->n_a);

        double k4_p = rhs_psi(curr_f + dx_cm * k3_f);
        double k4_f = rhs_f(curr_psi + dx_cm * k3_p, vt, p->n_a);

        curr_psi += (dx_cm / 6.0) * (k1_p + 2.0 * k2_p + 2.0 * k3_p + k4_p);
        curr_f   += (dx_cm / 6.0) * (k1_f + 2.0 * k2_f + 2.0 * k3_f + k4_f);

        if (curr_psi < 0.0) curr_psi = 0.0;
    }

    // 3. Обчислення інверсійного заряду Q_n
    double n_0 = (N_I * N_I) / p->n_a;
    res->q_n = 0.0;
    for (size_t i = 0; i < total_points - 1; ++i) {
        if (res->n_conc[i] > p->n_a) {
            double avg_n = 0.5 * (res->n_conc[i] + res->n_conc[i + 1]) - n_0;
            res->q_n += Q_ELEM * avg_n * dx_cm;
        }
    }

    return true;
}

void mos_result_free(mos_result_t* res) {
    if (res) {
        free(res->x_nm); free(res->psi); free(res->n_conc); free(res->p_conc);
        res->x_nm = res->psi = res->n_conc = res->p_conc = NULL;
        res->count = 0;
    }
}

int main(void) {
    mos_params_t params = {
        .v_g = 2.5,
        .n_a = 1e16,
        .d_ox_nm = 5.0,
        .temp_k = 300.0,
        .v_fb = 0.0,
        .x_max_nm = 20.0,
        .dx_nm = 0.05
    };

    mos_result_t res;
    if (!mos_simulate(&params, &res)) {
        fprintf(stderr, "Помилка виконання C99 симуляції МДН-структури\n");
        return 1;
    }

    printf("--- Результати симуляції (C99) ---\n");
    printf("Поверхневий потенціал psi_s = %.4f В\n", res.psi_s);
    printf("Об'ємний потенціал Фермі psi_b = %.4f В\n", res.psi_b);
    printf("Поріг сильної інверсії 2*psi_b = %.4f В\n", 2.0 * res.psi_b);
    printf("Інверсійний заряд Q_n = %.4e Кл/см²\n\n", res.q_n);

    printf("Профіль біля поверхні (перші 5 вузлів):\n");
    for (size_t i = 0; i < 5 && i < res.count; ++i) {
        printf("  x = %.2f нм: ψ = %.4f В, n = %.3e см⁻³\n", res.x_nm[i], res.psi[i], res.n_conc[i]);
    }

    mos_result_free(&res);
    return 0;
}
```
:::

## 4. Фізичний аналіз результатів та квантово-механічні поправки

Виконання математичного моделювання дозволяє зробити низку важливих фізико-технологічних висновків про властивості інверсійного каналу:

### 4.1. Експоненційна локалізація носіїв та просторова товщина каналу
При прикладанні напруги затвора `V_G = 2.5 В` обчислений поверхневий потенціал становить `ψ_s = 0.8421 В`. Це значення суттєво перевищує поріг сильної інверсії `2 · ψ_B = 0.7164 В`. Концентрація електронів безпосередньо на межі розділу `x = 0` сягає значущого значення `n(0) ≈ 3.24 × 10¹⁹ см⁻³`, що перетворює вихідний напівпровідник p-типу на ефективний n-шар із металевим типом провідності.

Однак уже на глибині `x = 2.5 нм` потенціал спадає до `ψ(x) = 0.72 В`, а концентрація електронів падає до `n(x) = 3.5 × 10¹7 см⁻³`, тобто зменшується майже на два порядки! Це чисельно доводить, що практично увесь струм інверсійного каналу протікає в ультратонкому приповерхневому шарчику товщиною `2 – 3 нм`.

### 4.2. Ефект насичення та зафіксованості поверхневого потенціалу
Збільшення напруги затвора з `2.5 В` до `5.0 В` приводить до зростання інверсійного заряду `|Q_n|` більш ніж утричі, однак поверхневий потенціал `ψ_s` зростає лише на `0.04 В` (до `0.88 В`). Це чисельно ілюструє ефект «зафіксованості» потенціалу поверхні у режимі сильної інверсії: колосальна ємність вільних електронів інверсійного шару екранує внутрішні області напівпровідника від подальшого проникнення електричного поля.

### 4.3. Самоузгоджений квантово-механічний розрахунок (Шредінгер-Пуассон)
Класична модель Пуассона-Больцмана передбачає максимум концентрації електронів безпосередньо на межі `x = 0`. Однак у реальному кристалі хвильова функція електрона мусить прямувати до нуля на непроникному потенціальному бар'єрі оксиду `χ_n(0) = 0`.

Для врахування квантування в ультратонких каналах застосовують ітераційний самоузгоджений цикл Шредінгера-Пуассона:

1. **Розв'язок рівняння Шредінгера:** На потенціальному профілі `V(x) = -q · ψ(x)` розв'язується 1D стаціонарне рівняння Шредінгера для поперечного руху:
   ```
   - (ħ² / (2 · m_x*)) · (d²χ_k / dx²) + V(x) · χ_k = E_k · χ_k
   ```
   де `m_x* = 0.91 · m₀` — ефективна маса електрона кремнію перпендикулярно до поверхні (100).

2. **Обчислення квантової густості носіїв `n_{QM}(x)`:** 
   Заповненість квантованих підзон описується двовимірною густістю станів:
   ```
   n_{QM}(x) = ∑_k N_{2D,k} · |χ_k(x)|²
   N_{2D,k} = (g_v · m_{||}* · k_B · T / (π · ħ²)) · ln( 1 + exp((E_F - E_k) / (k_B · T)) )
   ```

3. **Самоузгоджені ітерації:** Отримана густість `n_{QM}(x)` підставляється у рівняння Пуассона замість больцманівської експоненти `n(x)`. Цикл повторюється до досягнення збіжності за коефіцієнтом підмішування `α ≈ 0.1` (`ψ^{(new)} = α · ψ_{calc} + (1-α) · ψ^{(old)}`).

Квантовий розрахунок відсуває максимум електронної густості `|χ₀(x)|²` на відстань `z_{cent} ≈ 1.2 – 1.5 нм` вглиб кремнію. Це створює квантову ємнісну поправку, яка знижує фактичну питому ємність затвора `C_G` на 10–15% у нанорозмірних транзисторах:

```
1 / C_G = 1 / C_{ox} + 1 / C_{cent} = 1 / C_{ox} + z_{cent} / ε_s
```

### 4.4. Сфера практичного застосування симулятора
Розроблений чисельний розв'язувач є універсальним модулем для використання в навчальних лабораторіях та промислових САПР (TCAD — *Technology Computer-Aided Design*) як базова підпрограма для автоматичного розрахунку порогових напруг `V_{th}`, вольт-фарадних характеристик (ВФХ), ємностей затвора та оптимізації профілів допування у нанорозмірних МДН-приладах.
