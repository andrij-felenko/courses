# ⚙️ Алгоритми перевірки та генерації трикутних чисел

У цій вставці наведено практичні програмні реалізації фундаментальних алгоритмів, пов'язаних із трикутними числами. Ми розберемо точну перевірку чисел на трикутність без використання обчислень із плаваючою крапкою, ефективне генератування квадратних трикутних чисел за допомогою діофантових рекурентних співвідношень Пелля, застосування трикутної індексації для пакування симетричних матриць у лінійну пам'ять із розв'язанням оберненої задачі відновлення двовимірних координат, трикутне зондування у структурах даних хеш-таблиць, унікальну індексацію ребер повних графів для оптимізації алгоритмів на графах, тривимірне пакування тетраедричних тензорів, векторну SIMD-оптимізацію, порівняння кеш-локальності, замір часових затримок, концептуальні обмеження типів у C++20 та бітові трюки, а також детальний аналіз кеш-оптимізації, паралельного сумування та методологію тестування. Усі приклади реалізовано мовами C та C++ з дотриманням ідіоматичних стандартів кожної мови.

## Алгоритм перевірки чисел на трикутність (`is_triangular`)

Часто у комбінаторних та теоретико-числових обчисленнях виникає потреба з'ясувати, чи є задане 64-бітове ціле число `M` трикутним числом, і якщо так, то знайти його порядковий індекс `n`.

### Теоретичне підґрунтя та пастки точкової арифметики

З алгебраїчної тотожності відомо, що число `M` є трикутним числом тоді й лише тоді, коли діофантове рівняння `n(n + 1) / 2 = M` має розв'язок у натуральних числах `n`. Звівши рівняння до квадратного вигляду `n² + n - 2M = 0`, обчислимо дискримінант:

```
D = 1² - 4 · 1 · (-2M) = 8M + 1
```

Дискримінант `D = 8M + 1` має бути точним квадратом цілого непарного числа `s = 2n + 1`. Якщо `8M + 1 = s²`, шуканий індекс обчислюється за формулою `n = (s - 1) / 2`.

Застосування стандартних функцій із плаваючою крапкою, таких як `sqrt()` із бібліотеки `<math.h>` чи `std::sqrt`, наївним чином для 64-бітових цілих чисел `uint64_t` є **неприпустимою системною помилкою**. Тип `double` стандарту IEEE 754 має лише 53 біти мантиси, тому при значеннях `M > 2⁵³` (приблизно `9 · 10¹⁵`) обчислення `sqrt(8M + 1)` втрачає молодші біти точності й повертає округлені значення. Це призводить до хибнопозитивних або хибнонегативних результатів перевірки, де звичайні числа визнаються трикутними або навпаки.

Крім того, вираз `8M + 1` при великих значеннях `M` може призвести до арифметичного переповнення 64-бітного беззнакового цілого типу `uint64_t`. Максимальне значення `UINT64_MAX` дорівнює `2⁶⁴ - 1 ≈ 1.84 · 10¹⁹`. Отже, перед обчисленням виразу `8M + 1` необхідно виконувати сувору перевірку межі `M ≤ (UINT64_MAX - 1) / 8 ≈ 2.30 · 10¹⁸`. Для чисел, що перевищують цю межу, перевірка має виконуватися через розширений 128-бітний тип `__int128_t` у компіляторах GCC та Clang, або через довгу арифметику.

### Швидка попередня фільтрація за модулем 9

Перш ніж виконувати ресурсомістке обчислення точного цілочисельного квадратного кореня `isqrt()`, доцільно застосувати надшвидкий попередній фільтр. У математичному аналізі доведено, що цифровий корінь будь-якого трикутного числа (остача від ділення на 9) може набувати лише значень `1, 3, 6` або `9` (що відповідає `0 mod 9`).

Якщо остача `M mod 9` належить множині `{2, 4, 5, 7, 8}`, число `M` гарантовано **не є** трикутним, і алгоритм може миттєво повернути `false` без обчислення квадратного кореня. Оскільки операція взяття остачі `M % 9` виконується за один процесний такт, це дає змогу відсіяти 55% нетрикутних кандидаток за мінімальний час, не витрачаючи ресурси процесора на обчислення коренів.

### Точний цілочисельний квадратний корінь (Метод Ньютона)

Для точного обчислення кореня `s = ⌊√(8M + 1)⌋` без втрати точності використаємо метод Ньютона (целочисельний алгоритм вавилонян). Для заданого числа `S` послідовність наближень задається формулою:

```
x_{k+1} = ⌊ (x_k + ⌊S / x_k⌋) / 2 ⌋
```

Цей алгоритм володіє квадратичною швидкістю збіжності: кількість точних двійкових розрядів подвоюється на кожній ітерації, тому для 64-бітного числа перевірка завершується менш ніж за 6–8 кроків.

### Детальний розбір реалізації перевірки

Розглянемо архітектуру реалізації мовою C++. Метод `get_triangular_index` оголошено як `constexpr` та `noexcept`. Оголошення `constexpr` гарантує, що при передачі константних значень під час компіляції (наприклад, `TriangularChecker::is_triangular(15)`) увесь розрахунок виконується безпосередньо компілятором, а у підсумковий бінарний код потрапляє готовий результат `true`. Оголошення `noexcept` дає змогу компілятору генерувати оптимізований виклик без побудови таблиць обробки винятків (stack unwinding frame).

Використання контейнера `std::optional<std::uint64_t>` у C++ є ідіоматичним способом вираження семантики «значення може бути відсутнім». Це позбавляє розробника від використання вказівників вигляду `uint64_t *out_n` з мови C та небезпеки передачі нульового вказівника `NULL`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення точного цілочисельного квадратного кореня за методом Ньютона */
static uint64_t integer_sqrt(uint64_t n) {
    if (n == 0) return 0;
    
    uint64_t x = n;
    uint64_t y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
    }
    return x;
}

/* Перевірка, чи є число M трикутним */
bool is_triangular(uint64_t m, uint64_t *out_n) {
    if (m == 0) {
        if (out_n) *out_n = 0;
        return true;
    }
    
    /* Фільтрація переповнення 64-бітного цілого (8M + 1 <= UINT64_MAX) */
    if (m > (UINT64_MAX - 1) / 8) {
        return false;
    }
    
    /* Швидкий фільтр за цифровим коренем (модуль 9) */
    uint64_t rem9 = m % 9;
    if (rem9 == 2 || rem9 == 4 || rem9 == 5 || rem9 == 7 || rem9 == 8) {
        return false;
    }
    
    uint64_t disc = 8 * m + 1;
    uint64_t s = integer_sqrt(disc);
    
    /* Перевіряємо, чи є дискримінант точним квадратом */
    if (s * s != disc) {
        return false;
    }
    
    /* Дискримінант 8M + 1 для ненульового M завжди непарний */
    if ((s & 1) == 0) {
        return false;
    }
    
    if (out_n) {
        *out_n = (s - 1) / 2;
    }
    return true;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <optional>
#include <limits>

namespace math {

class TriangularChecker {
public:
    // Обчислення цілочисельного квадратного кореня
    static constexpr std::uint64_t integer_sqrt(std::uint64_t n) noexcept {
        if (n == 0) return 0;
        std::uint64_t x = n;
        std::uint64_t y = (x + 1) / 2;
        while (y < x) {
            x = y;
            y = (x + n / x) / 2;
        }
        return x;
    }

    // Перевірка на трикутність з поверненням індексу через std::optional
    static constexpr std::optional<std::uint64_t> get_triangular_index(std::uint64_t m) noexcept {
        if (m == 0) return 0;

        if (m > (std::numeric_limits<std::uint64_t>::max() - 1) / 8) {
            return std::nullopt;
        }

        // Швидкий фільтр за модулем 9
        const std::uint64_t rem9 = m % 9;
        if (rem9 == 2 || rem9 == 4 || rem9 == 5 || rem9 == 7 || rem9 == 8) {
            return std::nullopt;
        }

        const std::uint64_t disc = 8 * m + 1;
        const std::uint64_t s = integer_sqrt(disc);

        if (s * s != disc || (s & 1) == 0) {
            return std::nullopt;
        }

        return (s - 1) / 2;
    }

    static constexpr bool is_triangular(std::uint64_t m) noexcept {
        return get_triangular_index(m).has_value();
    }
};

} // namespace math
```
:::

## Генерація квадратних трикутних чисел за Пеллем

Розглянемо виражений у математичній вставці діофантовий алгоритм генерації чисел, які одночасно є трикутними та квадратними.

### Алгоритмічна рекурентність

Генерація спирається на пару взаємопов'язаних рекурентних формул для індексу трикутного числа `n` та кореня квадрата `k`:

```
n[m+1] = 3 n[m] + 4 k[m] + 1
k[m+1] = 2 n[m] + 3 k[m] + 1
```

з початковим станом `n₁ = 1`, `k₁ = 1` та `N₁ = 1`.

Ці формули дають змогу генерувати нові квадратні трикутні числа за час `O(1)` на кожен елемент, використовуючи виключно цілочисельне додавання та множення без транскурсивного пошуку.

### Аналіз цілочисельного переповнення

Оскільки квадратні трикутні числа зростають експоненційно (кожен наступний елемент є приблизно у 34 рази більшим за попередній), тип `uint64_t` дозволяє обчислити лише перші 6 нетривіальних квадратних трикутних чисел перед настанням арифметичного переповнення. Шостим квадратним трикутним числом є `N₆ = 4804915598241 = 2192012² = T₁₃₈6005`. Шостий елемент є останнім, який повністю вміщується у межі 64-бітного беззнакового цілого типу.

Для виявлення переповнення перед виконанням обчислень наступного кроку у коді реалізовано попереднє перевірочне співвідношення: `if (n > (UINT64_MAX - 4 * k - 1) / 3)`. Це запобігає некерованому циклічному згортанню цілих чисел (integer wrap-around) у C та undefined behavior у розрахунках.

### Програмна реалізація генератора

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint64_t index_n;
    uint64_t root_k;
    uint64_t value_n;
} SquareTriangularNumber;

/* Генерація перших count квадратних трикутних чисел */
size_t generate_square_triangular(SquareTriangularNumber *out_arr, size_t max_count) {
    if (max_count == 0 || out_arr == NULL) return 0;

    uint64_t n = 1;
    uint64_t k = 1;
    size_t generated = 0;

    while (generated < max_count) {
        out_arr[generated].index_n = n;
        out_arr[generated].root_k = k;
        out_arr[generated].value_n = k * k;
        generated++;

        /* Перевірка на можливе 64-бітне переповнення перед наступним кроком */
        if (n > (UINT64_MAX - 4 * k - 1) / 3) {
            break;
        }

        uint64_t next_n = 3 * n + 4 * k + 1;
        uint64_t next_k = 2 * n + 3 * k + 1;

        n = next_n;
        k = next_k;
    }

    return generated;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>

namespace math {

struct SquareTriangular {
    std::uint64_t index_n;
    std::uint64_t root_k;
    std::uint64_t value;
};

class SquareTriangularGenerator {
public:
    static std::vector<SquareTriangular> generate(std::size_t count) {
        std::vector<SquareTriangular> result;
        result.reserve(count);

        std::uint64_t n = 1;
        std::uint64_t k = 1;

        while (result.size() < count) {
            result.push_back({n, k, k * k});

            // Перевірка на переповнення
            if (n > (std::numeric_limits<std::uint64_t>::max() - 4 * k - 1) / 3) {
                break;
            }

            const std::uint64_t next_n = 3 * n + 4 * k + 1;
            const std::uint64_t next_k = 2 * n + 3 * k + 1;

            n = next_n;
            k = next_k;
        }

        return result;
    }
};

} // namespace math
```
:::

## Упаковка нижньотрикутних та симетричних матриць

У високопродуктивних обчисленнях, лінійній алгебрі та комп'ютерній графіці трикутні числа застосовуються для компактного зберігання нижнотрикутних або симетричних матриць розміру `N × N` у суцільному одновимірному масиві без витрат пам'яті на зберігання нульових або дубльованих елементів.

### Пряма індексація: від двовимірного `(i, j)` до 1D `flat_index`

Для нижньотрикутної матриці (де `0 ≤ j ≤ i < N`) кількість елементів у перших `i` рядках (від рядка 0 до `i-1`) дорівнює точно `i`-му трикутному числу:

```
T[i] = i(i + 1) / 2
```

Тоді плоский 1D-індекс елемента `(i, j)` у суцільному масиві обчислюється за формулою:

```
flat_index(i, j) = T[i] + j = i(i + 1) / 2 + j
```

Загальний необхідний обсяг пам'яті для зберігання матриці `N × N` становить `T[N] = N(N + 1) / 2` елементів замість `N²`, що дає економію майже 50% обсягу ОЗП. Оскільки елементи одного рядка лежать у пам'яті підряд, ця схема зберігання гарантує чудову локальність даних для клейових процесних кешів (L1/L2 data cache) при послідовному обході рядків.

При традиційному зберіганні повної матриці `N × N` елементи верхнього трикутника не використовуються, але все одно завантажуються у лінійки кешу процесора (cache lines по 64 байти). Схема пакування через трикутні числа гарантує, що кожна завантажена кеш-лінія містить виключно корисні дані, збільшуючи пропускну здатність шини пам'яті на 40–50% при матричному множенні та розв'язанні систем лінійних рівнянь методом Гаусса або Холецького.

```
Структура компактного зберігання матриці 4×4 (T₄ = 10 елементів):
 Рядок 0:  (0,0)               -> flat_index = 0 + 0 = 0
 Рядок 1:  (1,0), (1,1)        -> flat_index = 1 + 0 = 1, 1 + 1 = 2
 Рядок 2:  (2,0), (2,1), (2,2) -> flat_index = 3 + 0 = 3, 3 + 1 = 4, 3 + 2 = 5
 Рядок 3:  (3,0)... (3,3)      -> flat_index = 6 + 0 = 6 ... 6 + 3 = 9
```

### Обернена індексація: від 1D `flat_index` до двовимірного `(i, j)`

Зворотно, за заданим плоским індексом `K` у масиві (де `0 ≤ K < T[N]`), потрібно відновити індекс рядка `i` та індекс стовпчика `j`.

Оскільки `K = i(i + 1)/2 + j`, де `0 ≤ j ≤ i`, маємо подвійну нерівність `i(i + 1)/2 ≤ K < (i + 1)(i + 2)/2`. Розв'язуючи відповідне квадратне рівняння відносно `i`, отримуємо індекс рядка `i`:

```
i = ⌊ (√(8K + 1) - 1) / 2 ⌋
```

Після цього індекс стовпчика `j` знаходиться простим відніманням:

```
j = K - i(i + 1) / 2
```

### Детальний розбір C++ класу `TriangularMatrix`

У наведеній нижче реалізації мовою C++ використовується шаблонний клас `TriangularMatrix<T>`. Для доступу до елементів перевантажено оператор `operator()(i, j)`, що відповідає стандартній математичній нотації виклику матриць. При спробі звернення до верхньотрикутних елементів (`j > i`) або при виході за межі виміру генерується стандартний виняток `std::out_of_range`.

Обернений мапінг реалізовано у вигляді статичної функції `inverse_map`, яка повертає пару індексів `std::pair<std::size_t, std::size_t>`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t dim;
    double *data;
} TriangularMatrix;

/* Ініціалізація нижньотрикутної матриці */
bool tri_matrix_init(TriangularMatrix *mat, size_t dim) {
    mat->dim = dim;
    size_t total_elements = dim * (dim + 1) / 2;
    mat->data = (double *)calloc(total_elements, sizeof(double));
    return mat->data != NULL;
}

/* Звільнення пам'яті */
void tri_matrix_free(TriangularMatrix *mat) {
    if (mat->data) {
        free(mat->data);
        mat->data = NULL;
    }
    mat->dim = 0;
}

/* Пряме отримання елемента (i, j) */
double tri_matrix_get(const TriangularMatrix *mat, size_t i, size_t j) {
    if (j > i || i >= mat->dim) return 0.0;
    size_t flat_idx = i * (i + 1) / 2 + j;
    return mat->data[flat_idx];
}

/* Запис елемента (i, j) */
bool tri_matrix_set(TriangularMatrix *mat, size_t i, size_t j, double val) {
    if (j > i || i >= mat->dim) return false;
    size_t flat_idx = i * (i + 1) / 2 + j;
    mat->data[flat_idx] = val;
    return true;
}

/* Обернена функція: відновлення (i, j) за flat_idx */
void tri_matrix_map_inverse(size_t flat_idx, size_t *out_i, size_t *out_j) {
    uint64_t disc = 8 * (uint64_t)flat_idx + 1;
    uint64_t s = 0;
    while ((s + 1) * (s + 1) <= disc) {
        s++;
    }
    size_t i = (size_t)(s - 1) / 2;
    size_t j = flat_idx - i * (i + 1) / 2;
    
    if (out_i) *out_i = i;
    if (out_j) *out_j = j;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <utility>

namespace math {

template <typename T>
class TriangularMatrix {
private:
    std::size_t dim_;
    std::vector<T> data_;

public:
    explicit TriangularMatrix(std::size_t dim)
        : dim_(dim), data_(dim * (dim + 1) / 2, T{}) {}

    std::size_t dimension() const noexcept { return dim_; }
    std::size_t capacity() const noexcept { return data_.size(); }

    // Пряма індексація
    T& operator()(std::size_t i, std::size_t j) {
        if (j > i || i >= dim_) {
            throw std::out_of_range("Індекси виходять за межі нижньотрикутної матриці");
        }
        const std::size_t flat_idx = i * (i + 1) / 2 + j;
        return data_[flat_idx];
    }

    const T& operator()(std::size_t i, std::size_t j) const {
        if (j > i || i >= dim_) {
            throw std::out_of_range("Індекси виходять за межі нижньотрикутної матриці");
        }
        const std::size_t flat_idx = i * (i + 1) / 2 + j;
        return data_[flat_idx];
    }

    // Обернена індексація (відновлення координат)
    static std::pair<std::size_t, std::size_t> inverse_map(std::size_t flat_index) noexcept {
        const std::uint64_t disc = 8 * static_cast<std::uint64_t>(flat_index) + 1;
        
        std::uint64_t s = flat_index;
        std::uint64_t y = (s + 1) / 2;
        while (y < s) {
            s = y;
            y = (s + disc / s) / 2;
        }

        const std::size_t i = static_cast<std::size_t>((s - 1) / 2);
        const std::size_t j = flat_index - i * (i + 1) / 2;
        return {i, j};
    }
};

} // namespace math
```
:::

## Порівняльний аналіз продуктивності та кеш-локальності

Проведемо аналіз ефективності трикутної упаковки порівняно зі стандартним зберіванням у 2D масивах.

При класичному розставленні двохмірної матриці `A[N][N]` обхід за стовпчиками призводить до постійних промахів кешу (cache misses), бо крок між сусідніми елементами одного стовпчика дорівнює `N · sizeof(double)` байтів. При `N = 4096` крок становить 32 КБ, що негативно впливає на роботу L1 Data Cache.

Упаковка нижнього трикутника за формулою `flat_index(i, j) = i(i + 1)/2 + j` гарантує, що для кожного рядка `i` всі його елементи `j = 0...i` розміщені в пам'яті суцільним неперервним блоком. Завдяки цьому апаратний предвибірок процесних кешів (hardware cache prefetcher) завчасно завантажує наступні рядки у L1/L2 кеш, що зменшує затримку доступу до пам'яті від ~200 тактів RAM до 3–4 тактів L1 кешу.

## Трикутне зондування в хеш-таблицях (`Triangular Probing`)

Ще одним практичним алгоритмічним застосуванням трикутних чисел є **трикутне зондування** (англ. *triangular probing*) у відкритих адресованих хеш-таблицях.

### Механізм розв'язання колізій

У хеш-таблицях з відкритою адресацією при виникненні колізії (коли два ключі дають однаковий початковий хеш `h(k)`) необхідно шукати наступні вільні слоти в таблиці. При лінійному зондуванні (`h(k) + i`) виникає проблема первинної кластеризації: зайняті комірки збираються у довгі неперервні блоки, що уповільнює пошук до `O(N)`. При квадратичному зондуванні використовується послідовність `h(k) + c₁ i + c₂ i²`.

Трикутне зондування використовує додавання трикутних чисел на крок `i`:

```
hash_slot(k, i) = ( h(k) + T[i] ) mod M = ( h(k) + i(i + 1)/2 ) mod M
```

Послідовність зсувів становить: `+0, +1, +3, +6, +10, +15, +21...`

Цей спосіб зондування володіє унікальною арифметичною властивістю: якщо розмір хеш-таблиці `M` обрано як **степінь двійки** (`M = 2ᵖ`), то трикутне зондування гарантує обхід **усіх без винятку `M` комірок** таблиці до появи повторів. Це пояснюється тим, що різниця між послідовними трикутними числами `T[i] - T[j]` покриває повну систему остач за модулем степеня двійки.

Порівняно з квадратичним зондуванням, трикутне зондування вимагає менше арифметичних операцій на кожен крок (додавання поточного `i` замість множення `i²`), що робить його вкрай швидким у критичних до обчислень вузлах мережевих маршрутизаторів та ігрових рушіїв.

### Програмна реалізація трикутного зондування

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define TABLE_SIZE_POWER_OF_TWO 16 // 2^4 = 16 слотів

typedef struct {
    uint64_t key;
    uint32_t value;
    bool occupied;
} HashEntry;

typedef struct {
    HashEntry entries[TABLE_SIZE_POWER_OF_TWO];
} TriangularHashTable;

static inline uint32_t hash_function(uint64_t key) {
    /* Проста хеш-функція Мура для 64-бітних цілих */
    key = (key ^ (key >> 30)) * 0xbf58476d1ce4e5b9ULL;
    key = (key ^ (key >> 27)) * 0x94d049bb133111ebULL;
    key = key ^ (key >> 31);
    return (uint32_t)key;
}

bool hash_table_insert(TriangularHashTable *table, uint64_t key, uint32_t val) {
    uint32_t h = hash_function(key);
    
    for (uint32_t step = 0; step < TABLE_SIZE_POWER_OF_TWO; step++) {
        /* Обчислимо step-не трикутне число T[step] */
        uint32_t tri_offset = step * (step + 1) / 2;
        uint32_t slot = (h + tri_offset) & (TABLE_SIZE_POWER_OF_TWO - 1);
        
        if (!table->entries[slot].occupied || table->entries[slot].key == key) {
            table->entries[slot].key = key;
            table->entries[slot].value = val;
            table->entries[slot].occupied = true;
            return true;
        }
    }
    
    return false; // Таблиця повністю заповнена
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <cstddef>

namespace math {

template <std::size_t PowerOfTwoExponent = 4>
class TriangularProbingHashTable {
public:
    static constexpr std::size_t Size = std::size_t{1} << PowerOfTwoExponent;

    struct Entry {
        std::uint64_t key;
        std::uint32_t value;
        bool occupied{false};
    };

private:
    std::vector<Entry> table_{Size};

    static constexpr std::uint32_t hash_func(std::uint64_t key) noexcept {
        key = (key ^ (key >> 30)) * 0xbf58476d1ce4e5b9ULL;
        key = (key ^ (key >> 27)) * 0x94d049bb133111ebULL;
        return static_cast<std::uint32_t>(key ^ (key >> 31));
    }

public:
    bool insert(std::uint64_t key, std::uint32_t value) {
        const std::uint32_t base_hash = hash_func(key);

        for (std::size_t step = 0; step < Size; ++step) {
            const std::size_t tri_offset = step * (step + 1) / 2;
            const std::size_t slot = (base_hash + tri_offset) & (Size - 1);

            if (!table_[slot].occupied || table_[slot].key == key) {
                table_[slot] = {key, value, true};
                return true;
            }
        }
        return false;
    }

    std::optional<std::uint32_t> find(std::uint64_t key) const {
        const std::uint32_t base_hash = hash_func(key);

        for (std::size_t step = 0; step < Size; ++step) {
            const std::size_t tri_offset = step * (step + 1) / 2;
            const std::size_t slot = (base_hash + tri_offset) & (Size - 1);

            if (!table_[slot].occupied) {
                return std::nullopt;
            }
            if (table_[slot].key == key) {
                return table_[slot].value;
            }
        }
        return std::nullopt;
    }
};

} // namespace math
```
:::

## Індексація ребер у повних графах (`Complete Graph Edge Indexing`)

У теорії графів та алгоритмах мережевого аналізу виникає потреба збереження ребер неописового повного графа `K_V`, що містить `V` вершин. Загальна кількість неупорядкованих пар вершин `(u, v)` (де `0 ≤ u < v < V`) тотожно дорівнює `(V-1)`-му трикутному числу:

```
Total_Edges = T_{V-1} = V(V - 1) / 2
```

Для кожної пари вершин `(u, v)` із умовою `u < v`, унікальний 1D-індекс ребра `edge_id` обчислюється через індексування за трикутними числами:

```
edge_id(u, v) = T_{v-1} + u = v(v - 1) / 2 + u
```

Ця індексація дає змогу будувати компактні структури даних для зберігання ваг ребер графів у суцільному векторі пам'яті без дзеркального дублювання даних для паралельних пар `(u, v)` та `(v, u)`.

В алгоритмах виявлення зіткнень (broadphase collision detection) у фізичних рушіях (Box2D, Bullet Physics) об'єкти виступають вершинами графа. Для перевірки зіткнень між кожною парою з `V` об'єктів створюється масив контактних пар розміром `T_{V-1}`. Використання трикутної індексації дає змогу уникати подвійних перевірок одного й того самого контакту та миттєво знаходити унікальний слот у масиві.

### Детальний розбір реалізації індексації ребер графа

У наведеному нижче коді мовою C++ клас `CompleteGraphIndexer` надає повністю `constexpr` функцію `get_edge_id`. Перевірка умови `if (u > v)` та впорядкування індексів `std::swap(u, v)` ґарантує, що для будь-якої вхідної пари вершин `(3, 7)` або `(7, 3)` буде повернуто один і той самий унікальний `edge_id`. 

Обернена функція `get_vertices_from_edge_id` застосовує метод Ньютона для точного відновлення орієнтованих індексів `(u, v)`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <size_t.h>

/* Обчислення плоского індексу ребра між вершинами u та v (u < v) */
size_t complete_graph_edge_id(size_t u, size_t v) {
    if (u > v) {
        size_t tmp = u;
        u = v;
        v = tmp;
    }
    if (u == v) return SIZE_MAX; // Немає петлі у простому графі
    
    return v * (v - 1) / 2 + u;
}

/* Відновлення пари вершин (u, v) за edge_id */
void complete_graph_inverse_edge_id(size_t edge_id, size_t *out_u, size_t *out_v) {
    uint64_t disc = 8 * (uint64_t)edge_id + 1;
    uint64_t s = 0;
    while ((s + 1) * (s + 1) <= disc) {
        s++;
    }
    
    size_t v = (size_t)(s - 1) / 2 + 1;
    size_t u = edge_id - v * (v - 1) / 2;
    
    if (out_u) *out_u = u;
    if (out_v) *out_v = v;
}
```
```cpp
#include <iostream>
#include <cstddef>
#include <utility>
#include <algorithm>
#include <cstdint>

namespace math {

class CompleteGraphIndexer {
public:
    static constexpr std::size_t total_edges(std::size_t vertices) noexcept {
        return vertices * (vertices - 1) / 2;
    }

    static std::size_t get_edge_id(std::size_t u, std::size_t v) noexcept {
        if (u > v) std::swap(u, v);
        return v * (v - 1) / 2 + u;
    }

    static std::pair<std::size_t, std::size_t> get_vertices_from_edge_id(std::size_t edge_id) noexcept {
        const std::uint64_t disc = 8 * static_cast<std::uint64_t>(edge_id) + 1;
        
        std::uint64_t s = edge_id;
        std::uint64_t y = (s + 1) / 2;
        while (y < s) {
            s = y;
            y = (s + disc / s) / 2;
        }

        const std::size_t v = static_cast<std::size_t>((s - 1) / 2) + 1;
        const std::size_t u = edge_id - v * (v - 1) / 2;
        return {u, v};
    }
};

} // namespace math
```
:::

## Тривимірне пакування тетраедричних тензорів

У тривимірній комп'ютерній графіці та обчислювальному матеріалознавстві узагальненням трикутної індексації є **тетраедрична індексація**. Для тривимірного симетричного тензора або тетраедричної сітки з координатною умовою `0 ≤ k ≤ j ≤ i < N` кількість елементів у перших `i` шарах описується `i`-м тетраедричним числом `TE[i]`:

```
TE[i] = ∑_{r=1}^{i} T[r] = i(i + 1)(i + 2) / 6
```

Плоский 1D-індекс тривимірного елемента `(i, j, k)` обчислюється як сума `i`-го тетраедричного числа, `j`-го трикутного числа та індексу `k`:

```
flat_index_3d(i, j, k) = TE[i] + T[j] + k = i(i + 1)(i + 2) / 6 + j(j + 1) / 2 + k
```

Ця індексація зменшує обсяг пам'яті для 3D симетричних тензорів третього рангу з `N³` до `N³/6`, тобто вивільняє понад 83% обсягу оперативної пам'яті при збереженні точного швидкого прямого доступу.

### Програмна реалізація 3D-тетраедричного тензора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t dim;
    double *data;
} TetrahedralTensor3D;

bool tensor3d_init(TetrahedralTensor3D *tensor, size_t dim) {
    tensor->dim = dim;
    size_t total = dim * (dim + 1) * (dim + 2) / 6;
    tensor->data = (double *)calloc(total, sizeof(double));
    return tensor->data != NULL;
}

void tensor3d_free(TetrahedralTensor3D *tensor) {
    if (tensor->data) {
        free(tensor->data);
        tensor->data = NULL;
    }
    tensor->dim = 0;
}

double tensor3d_get(const TetrahedralTensor3D *tensor, size_t i, size_t j, size_t k) {
    if (k > j || j > i || i >= tensor->dim) return 0.0;
    size_t flat_idx = i * (i + 1) * (i + 2) / 6 + j * (j + 1) / 2 + k;
    return tensor->data[flat_idx];
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstddef>
#include <stdexcept>

namespace math {

template <typename T>
class TetrahedralTensor3D {
private:
    std::size_t dim_;
    std::vector<T> data_;

public:
    explicit TetrahedralTensor3D(std::size_t dim)
        : dim_(dim), data_(dim * (dim + 1) * (dim + 2) / 6, T{}) {}

    std::size_t dimension() const noexcept { return dim_; }
    std::size_t capacity() const noexcept { return data_.size(); }

    T& operator()(std::size_t i, std::size_t j, std::size_t k) {
        if (k > j || j > i || i >= dim_) {
            throw std::out_of_range("Некоректні індекси 3D тетраедричного тензора");
        }
        const std::size_t flat_idx = i * (i + 1) * (i + 2) / 6 + j * (j + 1) / 2 + k;
        return data_[flat_idx];
    }
};

} // namespace math
```
:::

## Паралельне сумування масивів та векторні SIMD-інструкції

У паралельних обчисленнях на графічних процесорах (GPU CUDA/OpenCL) та високопродуктивних CPU-кластерах трикутні числа виникають при балансуванні навантаження між потоками обробки.

Коли кожному `i`-му процесорному ядру доручається обробка `i` елементів (наприклад, у задачах верхньо-трикутної редукції), `k`-тий потік отримує діапазон індексів від `T_{k-1}` до `T_k - 1`. Це дає змогу розподіляти навантаження без міжпотокових колізій і без потреби синхронізації м'ютексів.

Сучасні векторні розширення процесорів (x86 AVX2, AVX-512, ARM Neon) дозволяють обчислювати трикутні суми за допомогою векторних інструкцій `vpmulld` та `vpaddd`, обробляючи по 8 або 16 32-бітних елементів за один такт процесора. Для максимальної ефективності векторної обробки пам'ять під масиви має бути вирівняна по межі 64 байтів (`alignas(64)` у C++ або `posix_memalign` у C).

При векторній редукції префіксних сум векторний регістр розгортає обчислення `8` трикутних кроків паралельно, після чого виконується підсумкове горизонтальне додавання (horizontal reduction `_mm256_reduce_add_epi64`), що прискорює сумування у 4–6 разів порівняно з послідовним скалярним циклом.

## Замір часу виконання та бенчмаркінг (`High-Resolution Clocking`)

Для вимірювання затримок обчислення індексацій та квадратних коренів у C++ використовується високоточний таймер стандарту `<chrono>` (`std::chrono::high_resolution_clock`).

Для запобігання ситуаціям, коли сучасні оптимізувальні компілятори (GCC -O3, Clang) повністю викидають «невикористовуваний» цикл обчислень (dead code elimination), результати обчислення індексів мають передаватися у фейковий споживач або оголошуватися як `volatile`.

## Концептуальні обмеження C++20 та безпека типізації

У сучасному стандарті C++20 шаблони алгоритмів трикутної обробки обмежуються за допомогою концептів (`concepts` із заголовного файла `<concepts>`).

Застосування обмеження `template <std::integral T>` гарантує, що шаблонні функції `get_triangular_index` або `inverse_map` можуть інстанціюватися виключно цілочисельними типами (`int`, `uint64_t`, `size_t`), блокуючи спроби передачі чисел із плаваючою крапкою ще на етапі компіляції. Це усуває цілий клас помилок узгодження типів у складних обчислювальних бібліотеках.

## Методологія модульного тестування та крайні випадки

При розробці системного програмного забезпечення на основі трикутних алгоритмів важливе значення має надійне покриття модульним тестуванням крайніх випадків (edge cases):
1. **Нульове значення (`M = 0`)**: Метод перевірки на трикутність має коректно повертати `true` із порядковим індексом `n = 0`.
2. **Перші трикутні числа (`M = 1, 3, 6, 10, 15`)**: Алгоритм `is_triangular` має повертати відповідні індекси `1, 2, 3, 4, 5`.
3. **Найближчі нетрикутні числа (`M = 2, 4, 5, 7, 8, 9, 11`)**: Перевірка має вертати `false`.
4. **Межа переповнення 64-бітного цілого**: Числа видами `M = 2.30 · 10¹⁸` не повинні викликати арифметичного згортання у виразі `8M + 1`.

## Аналіз складності та продуктивності

Для оцінки ефективності розглянутих алгоритмів зведемо їхні часові та просторові характеристики у підсумкову порівняльну таблицю.

```
-------------------------------------------------------------------------
Алгоритм / Операція            Часова складність   Просторова складність
-------------------------------------------------------------------------
Перевірка is_triangular(M)      O(log(log M))       O(1)
Генерація Пелля (N чисел)       O(N)                O(N)
Пряма індексація flat(i, j)     O(1)                O(1)
Обернена індексація (K -> i,j)  O(log(log K))       O(1)
Трикутне зондування (у середньому) O(1)             O(M)
Індексація ребер графа K_V     O(1)                O(1)
3D Тетраедрична індексація      O(1)                O(1)
-------------------------------------------------------------------------
```

Усі наведені алгоритми демонструють оптимальну часову та просторову складність і є повністю готовими до застосування у розробці високопродуктивних систем.
