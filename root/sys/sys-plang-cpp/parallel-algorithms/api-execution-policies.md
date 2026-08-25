# 📋 Довідник інтерфейсу: політики виконання та паралельні алгоритми

Цей довідник містить вичерпний технічний опис інтерфейсів, політик виконання, сигнатур паралельних алгоритмів та правил коректності, визначених у заголовках `<execution>`, `<algorithm>` та `<numeric>` у стандартах C++17 та C++20. Він призначений для використання як строга специфікація при проєктуванні високонавантажених обчислювальних систем, де правильний вибір політики та точне дотримання контрактів відсутності гонок даних визначають стабільність і продуктивність програми.

---

## 1. Архітектура заголовка `<execution>`: типи та глобальні об'єкти політик

Заголовок `<execution>` визначає фундаментальні типи політик виконання, які передаються першим параметром у перевантажені алгоритми стандартної бібліотеки. Кожна політика є спеціальним класом-тегом, який сигналізує компілятору та бібліотечному runtime-планувальнику про допустимі механізми розпаралелювання (потоки, SIMD-векторизація, асинхронні задачі).

### Класи політик виконання

Усі класи політик виконання є типами без власного внутрішнього стану (stateless types). Вони мають загальнодоступні стандартні конструктори за замовчуванням, конструктори копіювання та переміщення, а також деструктори, що гарантовано не викидають винятків (`noexcept`).

```cpp
namespace std::execution {
    // 1. Послідовне детерміноване виконання (C++17)
    class sequenced_policy { /* реалізаційно-визначено */ };

    // 2. Паралельне багатопотокове виконання (C++17)
    class parallel_policy { /* реалізаційно-визначено */ };

    // 3. Паралельне багатопотокове та векторизоване SIMD-виконання (C++17)
    class parallel_unsequenced_policy { /* реалізаційно-визначено */ };

    // 4. Однопотокове векторизоване SIMD-виконання (C++20)
    class unsequenced_policy { /* реалізаційно-визначено */ };
}
```

### Стандартні глобальні екземпляри об'єктів політик

Для зручності використання у клієнтському коді стандарт C++ оголошує глобальні константні об'єкти типу `inline constexpr` у просторі імен `std::execution`:

```cpp
namespace std::execution {
    inline constexpr sequenced_policy            seq{};
    inline constexpr parallel_policy             par{};
    inline constexpr parallel_unsequenced_policy par_unseq{};
    inline constexpr unsequenced_policy          unseq{}; // Введено у C++20
}
```

### Допоміжний типаж перевірки `std::is_execution_policy`

Для метапрограмування на шаблонах, SFINAE-перевірок та концептуальних обмежень у C++20 стандарт надає допоміжну типажну структуру:

```cpp
template <class T>
struct is_execution_policy : std::integral_constant<bool, /* true для офіційних класів політик */> {};

template <class T>
inline constexpr bool is_execution_policy_v = is_execution_policy<T>::value;
```

Вираз `std::is_execution_policy_v<T>` повертає значення `true` виключно для чотирьох стандартних класів політик або для розширень компілятора, які відповідають вимогам стандарту до політик виконання.

---

## 2. Формальні моделі чергування та контракти політик виконання

Кожна політика виконання встановлює чіткі математичні обмеження на спосіб виклику функцій доступу до елементів (Element Access Functions) — лямбда-виразів, унарних та бінарних операцій, функціональних об'єктів.

### Політика `std::execution::seq` (Sequenced Policy)
- **Модель виконання:** Усі виклики функцій користувача виконуються в межах одного викликаючого системного потоку.
- **Порядок операцій:** Операції над елементами впорядковані (sequenced) відносно одна одної, хоча стандарт дозволяє алгоритму виконувати обхід у зворотному чи іншому детермінованому порядку, якщо це зазначено у специфікації алгоритму.
- **Синхронізація:** Дозволено використання будь-яких примітивів блокування (`std::mutex`, `std::unique_lock`), умовних змінних (`std::condition_variable`) та динамічне виділення пам'яті (`malloc`, `new`).
- **Сфера застосування:** Використовується, коли алгоритм повинен виконуватися строго на одному ядрі, або для зневадження (debugging) логіки перед увімкненням багатопотоковості.

### Політика `std::execution::par` (Parallel Policy)
- **Модель виконання:** Обчислення розподіляються між множиною паралельних системних потоків (через пул потоків процесора або планувальник задач).
- **Порядок операцій:** Виклики в межах різних потоків є невпорядкованими відносно один одного (indeterminately sequenced). Проте в межах одного конкретного потоку виконання операції залишаються строго послідовними (не чергуються між собою).
- **Синхронізація:** Дозволено захоплення м'ютексів та атомарні операції, оскільки кожен потік має власний незалежний стек викликів. Програміст несе повну відповідальність за запобігання гонкам даних (Data Races).
- **Сфера застосування:** Підходить для складних операцій над об'єктами, які вимагають синхронізації доступу до зовнішніх спільних ресурсів або виділення динамічної пам'яті під час обробки.

### Політика `std::execution::par_unseq` (Parallel and Unsequenced Policy)
- **Модель виконання:** Обчислення розподіляються між множиною системних потоків, і додатково в межах кожного потоку компілятор має право векторизувати виконання за допомогою векторних інструкцій процесора (SIMD).
- **Порядок операцій:** Операції можуть довільно чергуватися (unsequenced) навіть у межах одного фізичного потоку. Один крок операції над елементом `i` може розпочатися до повного завершення операції над елементом `j` на тому самому ядрі.
- **Синхронізація (Суворі обмеження!):** Категорично заборонено використання будь-яких блокуючих операцій (`std::mutex::lock`), атомарних операцій очікування (`atomic::wait`), викликів динамічного виділення пам'яті через купу (`operator new`, `malloc`) або не-reentrant функцій. Недотримання цієї вимоги призводить до самоблокування потоку (Vectorization Deadlock).
- **Сфера застосування:** Забезпечує максимальну продуктивність для числових масивів та математичних трансформацій на багатоядерних процесорах із широкими векторними регістрами (AVX-512, ARM NEON).

### Політика `std::execution::unseq` (Unsequenced Policy, C++20)
- **Модель виконання:** Обчислення виконуються строго в одному викликаючому потоці ОС, проте компілятор векторизує цикл за допомогою апаратних регістрів SIMD (AVX, SSE, ARM NEON).
- **Порядок операцій:** Операції чергуються між векторними лініями в одному потоці.
- **Синхронізація:** Повністю діють ті самі суворі обмеження на відсутність блокувань та виділення пам'яті, що й для `par_unseq`.
- **Сфера застосування:** Використовується для високоефективної векторизації на одному ядрі без накладних витрат на запуск і синхронізацію пулу потоків ОС.

---

## 3. Гарантії просування вперед (Forward Progress Guarantees)

Стандарт C++ формалізує гарантії просування потоків (Forward Progress Guarantees) для кожної політики виконання, що має вирішальне значення для уникнення взаємних блокувань (livelocks та deadlocks):

1. **Паралельне просування вперед (Concurrent Forward Progress):** 
   Політика `std::execution::par` гарантує, що якщо потік виконав певну кількість кроків, він зрештою зробить крок уперед. Це означає, що якщо потік A очікує завершення дії потоку B (наприклад, через спінлок або м'ютекс), потік B гарантовано отримає процесорний час і завершить роботу.

2. **Слабопаралельне просування вперед (Weakly Parallel Forward Progress):**
   Політики `std::execution::par_unseq` та `std::execution::unseq` надають лише слабкі гарантії просування. Окремі векторні лінії (SIMD lanes) не мають гарантії незалежного просування вперед. Якщо векторна лінія 0 зупиниться в очікуванні події від векторної лінії 1 на тому самому ядрі, лінія 1 ніколи не виконається, оскільки апаратний потік заблоковано на лінії 0.

---

## 4. Специфікація обробки винятків (Exception Handling Specification)

Поведінка винятків у паралельних алгоритмах принципово відрізняється від класичних алгоритмів C++:

### Правило негайної термінації `std::terminate()`
Якщо під час виконання паралельного алгоритму з будь-якою політикою виконання (`seq`, `par`, `par_unseq`, `unseq`) функція користувача (предикат, оператор редукції, проєкція) викидає виняток, який не перехоплюється всередині тіла самої функції, стандарт гарантує негайний виклик **`std::terminate()`**.

Це означає, що паралельний алгоритм не виконує розгортання стеку і не дозволяє перехопити виняток за допомогою зовнішнього блоку `try-catch`. Якщо обробка помилок є необхідною, розробник зобов'язаний самостійно обертати тіло предикату в локальний блок `try-catch` і зберігати інформацію про помилку у потокобезпечний статус.

### Правило виділення ресурсів `std::bad_alloc`
Єдиний виняток, який може бути легально викинутий із виклику паралельного алгоритму, це `std::bad_alloc`. Він викидається безпосередньо runtime-бібліотекою у разі, якщо планувальнику не вдалося виділити необхідну внутрішню пам'ять або структури керування пулом потоків для запуску паралельної задачі.

---

## 5. Повний довідник перевантажень алгоритмів у `<algorithm>`

Усі алгоритми заголовка `<algorithm>`, які підтримують паралельне виконання, приймають політику виконання першим аргументом за універсальним посиланням `ExecutionPolicy&& policy`.

### Вимоги до категорій ітераторів

- Більшість паралельних алгоритмів вимагають тип ітератора не нижче **`ForwardIterator`** (ітератор прямого обходу з підтримкою багаторазового проходження).
- Однопрохідні ітератори (`InputIterator`, `istream_iterator`) заборонені в паралельних версіях, оскільки їх неможливо повторно зчитати в іншому потоці.
- Алгоритми сортування (`std::sort`, `std::stable_sort`) та розбиття вимагають строго **`RandomAccessIterator`** для забезпечення доступу за константний час `O(1)`.

### 1. Модифікуючі та трансформуючі алгоритми

#### `std::for_each` та `std::for_each_n`
Виконує задану унарну функцію для кожного елемента діапазону.

```cpp
template <class ExecutionPolicy, class ForwardIt, class UnaryFunction>
void for_each(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryFunction f);

template <class ExecutionPolicy, class ForwardIt, class Size, class UnaryFunction>
ForwardIt for_each_n(ExecutionPolicy&& policy, ForwardIt first, Size n, UnaryFunction f);
```
- **Параметри:**
  - `policy` — об'єкт політики виконання.
  - `first`, `last` — діапазон елементів `[first, last)`.
  - `n` — кількість елементів для обробки.
  - `f` — функціональний об'єкт з сигнатурою `void f(auto& element)` або `void f(const auto& element)`.
- **Повертане значення:** `for_each` повертає `void` (на відміну від версії C++98, яка повертала копію функтора), `for_each_n` повертає ітератор, зміщений на `n` позицій.
- **Складність:** Рівно `N` застосувань функції `f`.

#### `std::transform` (Унарна та бінарна форми)
Трансформує елементи вхідного діапазону та записує результати у вихідний діапазон.

```cpp
// Унарна трансформація: y[i] = op(x[i])
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class UnaryOperation>
ForwardIt2 transform(ExecutionPolicy&& policy, 
                     ForwardIt1 first1, ForwardIt1 last1, 
                     ForwardIt2 d_first, UnaryOperation unary_op);

// Бінарна трансформація: z[i] = op(x[i], y[i])
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class ForwardIt3, class BinaryOperation>
ForwardIt3 transform(ExecutionPolicy&& policy, 
                     ForwardIt1 first1, ForwardIt1 last1, 
                     ForwardIt2 first2, ForwardIt3 d_first, BinaryOperation binary_op);
```
- **Контракт безпеки пам'яті:** Вихідний діапазон `[d_first, ...)` не повинен перекриватися з вхідним діапазоном, якщо тільки `d_first == first1` (дозволено трансформацію на місці).
- **Повертане значення:** Ітератор на кінець вихідного діапазону `d_first + (last1 - first1)`.

#### `std::fill` та `std::generate`
Паралельне заповнення пам'яті константним значенням або викликами генератора.

```cpp
template <class ExecutionPolicy, class ForwardIt, class T>
void fill(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, const T& value);

template <class ExecutionPolicy, class ForwardIt, class Generator>
void generate(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, Generator gen);
```
- **Застереження щодо `generate`:** Якщо `gen` змінює свій внутрішній стан при кожному виклику (stateful generator), використання політики `par` призведе до race condition, якщо генератор не є потокобезпечним.

### 2. Алгоритми впорядкування та сортування

#### `std::sort` (Паралельне нестабільне сортування)
Впорядковує елементи за зростанням або за вказаним компаратором, використовуючи паралельний Introsort/Quicksort.

```cpp
template <class ExecutionPolicy, class RandomAccessIt>
void sort(ExecutionPolicy&& policy, RandomAccessIt first, RandomAccessIt last);

template <class ExecutionPolicy, class RandomAccessIt, class Compare>
void sort(ExecutionPolicy&& policy, RandomAccessIt first, RandomAccessIt last, Compare comp);
```
- **Вимоги до компаратора:** `comp` повинен задавати строгий слабкий порядок (Strict Weak Ordering).
- **Складність:** `O(N · log N)` порівнянь. Паралельна глибина (Span) складає `O(log² N)`.

#### `std::stable_sort` (Паралельне стабільне сортування)
Впорядковує елементи зі збереженням відносного порядку еквівалентних елементів (використовує паралельний MergeSort з додатковим буфером).

```cpp
template <class ExecutionPolicy, class RandomAccessIt, class Compare>
void stable_sort(ExecutionPolicy&& policy, RandomAccessIt first, RandomAccessIt last, Compare comp);
```

### 3. Алгоритми пошуку, підрахунку та предикатної фільтрації

```cpp
// Пошук першого входження
template <class ExecutionPolicy, class ForwardIt, class T>
ForwardIt find(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, const T& value);

// Пошук за предикатом
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
ForwardIt find_if(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

// Підрахунок елементів
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
typename std::iterator_traits<ForwardIt>::difference_type
count_if(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

// Перевірка умов
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
bool all_of(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
bool any_of(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);
```

---

## 6. Повний довідник числових алгоритмів у `<numeric>`

Числові операції в C++17 були кардинально розширені для підтримки асинхронного та векторного паралелізму.

### 1. Алгоритм `std::reduce` (Паралельна деревоподібна редукція)

Алгоритм `std::reduce` є паралельним еквівалентом `std::accumulate`. Головна відмінність полягає в тому, що порядок групування та виконання операцій є довільним (деревоподібним).

```cpp
// Сигнатура 1: Сума з нульовим початковим значенням типу елементів
template <class ExecutionPolicy, class ForwardIt>
typename std::iterator_traits<ForwardIt>::value_type
reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last);

// Сигнатура 2: Сума з явним значенням init
template <class ExecutionPolicy, class ForwardIt, class T>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init);

// Сигнатура 3: Редукція з користувацьким бінарним оператором
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOp>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init, BinaryOp binary_op);
```
- **Математичний контракт:** `binary_op` **зобов'язаний бути асоціативним та комутативним**. Якщо операція порушує асоціативність (наприклад, множення чисел з плаваючою комою у граничних випадках), результат обчислення може коливатися між різними запусками через різний порядок згортання дерева.

### 2. Алгоритм `std::transform_reduce` (Паралельний Map-Reduce)

Виконує трансформацію вхідних значень і подальше паралельне згортання за один прохід через пам'ять.

```cpp
// Унарна форма (Map -> Reduce): згортання результатів transform_op(x)
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOp, class UnaryOp>
T transform_reduce(ExecutionPolicy&& policy, 
                   ForwardIt first, ForwardIt last, 
                   T init, BinaryOp reduce_op, UnaryOp transform_op);

// Бінарна форма (Скалярний добуток): згортання результатів transform_op(x, y)
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp1, class BinaryOp2>
T transform_reduce(ExecutionPolicy&& policy, 
                   ForwardIt1 first1, ForwardIt1 last1, 
                   ForwardIt2 first2, 
                   T init, BinaryOp1 reduce_op, BinaryOp2 transform_op);
```

### 3. Префіксне сканування: `std::inclusive_scan` та `std::exclusive_scan`

Префіксне сканування (паралельна префіксна сума) перетворює масив значень на масив кумулятивних станів за паралельний час `O(log N)`.

```cpp
// std::inclusive_scan: y[i] = x[0] + ... + x[i]
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2>
ForwardIt2 inclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first);

template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class BinaryOp, class T>
ForwardIt2 inclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, BinaryOp binary_op, T init);

// std::exclusive_scan: y[0] = init, y[i] = init + x[0] + ... + x[i-1]
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T>
ForwardIt2 exclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, T init);

template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp>
ForwardIt2 exclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, T init, BinaryOp binary_op);
```

### 4. Комбіновані операції: `transform_inclusive_scan` та `transform_exclusive_scan`

Ці алгоритми дозволяють спочатку застосувати унарну функцію перетворення до кожного елемента, а потім виконати префіксне сканування без виділення проміжного буфера пам'яті:

```cpp
// Трансформація + інклюзивне сканування
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class BinaryOp, class UnaryOp>
ForwardIt2 transform_inclusive_scan(ExecutionPolicy&& policy, 
                                    ForwardIt1 first, ForwardIt1 last, 
                                    ForwardIt2 d_first, 
                                    BinaryOp binary_op, UnaryOp unary_op);

// Трансформація + ексклюзивне сканування
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp, class UnaryOp>
ForwardIt2 transform_exclusive_scan(ExecutionPolicy&& policy, 
                                    ForwardIt1 first, ForwardIt1 last, 
                                    ForwardIt2 d_first, 
                                    T init, BinaryOp binary_op, UnaryOp unary_op);
```

---

## 7. Практичні пастки та антипатерни використання

При роботі з паралельними алгоритмами розробники найчастіше припускаються наступних фундаментальних помилок:

1. **Захоплення зовнішніх змінних за посиланням без синхронізації:**
   Використання лямбда-виразу `[&sum](int x) { sum += x; }` у виклику `std::for_each(std::execution::par, ...)` призводить до гонки даних (Data Race) над змінною `sum` та невизначеної поведінки програми. Замість цього слід використовувати спеціалізовані операції редукції `std::reduce` або `std::transform_reduce`.

2. **Використання `std::atomic` всередині `std::execution::par_unseq`:**
   Атомарні операції з активним очікуванням (spin-wait) порушують вимоги векторизації, викликаючи взаємне блокування векторних ліній на одному ядрі CPU.

3. **Спроба паралелізації надто малих масивів:**
   Для масивів із кількістю елементів менше 10 000 накладні витрати на розподіл задач між потоками пулу перевищують час виконання послідовного алгоритму на одному ядрі.

4. **Використання не-асоціативних операторів у `std::reduce`:**
   Передача оператора віднімання `std::minus<>` або операцій ділення у `std::reduce` призводить до математично некоректних і недетермінованих результатів.

5. **Хибне розділення пам'яті (False Sharing):**
   Якщо кілька паралельних потоків у предикаті записують результат у сусідні комірки пам'яті (наприклад, у спільний масив лічильників), які розташовані в межах однієї 64-байтової кеш-лінії CPU (Cache Line), протокол узгодженості кешів (MESI) змушений постійно передавати право на запис між ядрами. Це призводить до катастрофічного падіння швидкодії.

6. **NUMA-ефекти та локальність пам'яті:**
   У багатопроцесорних серверах із неоднорідним доступом до пам'яті (NUMA) звернення потоку одного процесорного роз'єму до пам'яті, виділеної на іншому роз'ємі, уповільнює обхід масиву в 2–3 рази. Для досягнення пікової продуктивності дані повинні ініціалізуватися паралельно тими самими потоками, які їх згодом обробляють (first-touch policy).

---

## 8. Вимоги до апаратних бекендів та лінкування бібліотек

Реалізація паралельних алгоритмів у стандартній бібліотеці вимагає підключення відповідних системних бекендів під час компіляції та лінкування:

- **GCC (libstdc++) та Clang (libc++):** За замовчуванням використовують бібліотеку **Intel oneTBB (Threading Building Blocks)**. Для успішної збірки програми вимагається передача прапорця лінкувальника `-ltbb` (наприклад, `g++ -std=c++17 -O3 main.cpp -ltbb`). У разі відсутності бібліотеки TBB компілятор може аварійно завершити лінкування або виконати fallback до послідовного виклику.
- **MSVC (Microsoft Visual C++):** Повністю інтегрує підтримку паралельних алгоритмів у стандартний C Runtime (CRT) через внутрішній пул потоків Windows ThreadPool, не вимагаючи додаткових зовнішніх бібліотек при лінкуванні.
- **NVIDIA HPC SDK (`nvc++`):** Дозволяє транслювати виклики з політикою `std::execution::par` у паралельні ядра графічного процесора CUDA за допомогою прапорця компілятора `-stdpar=gpu`. У цьому режимі компілятор автоматично налаштовує уніфіковану пам'ять (Unified Memory) для прозорої передачі даних між оперативною пам'яттю CPU та відеопам'яттю GPU.

---

## 9. Порівняння складності та апаратних накладних витрат

| Алгоритм | Кількість викликів функції (Work) | Паралельна глибина (Span) | Мінімальна категорія ітератора |
| :--- | :--- | :--- | :--- |
| **`std::for_each`** | `O(N)` | `O(N / P)` | `ForwardIterator` |
| **`std::transform`** | `O(N)` | `O(N / P)` | `ForwardIterator` |
| **`std::sort`** | `O(N · log N)` | `O(log² N)` | `RandomAccessIterator` |
| **`std::stable_sort`** | `O(N · log N)` | `O(log² N)` | `RandomAccessIterator` |
| **`std::reduce`** | `O(N)` | `O(log N)` | `ForwardIterator` |
| **`std::transform_reduce`** | `O(N)` | `O(log N)` | `ForwardIterator` |
| **`std::inclusive_scan`** | `O(N)` | `O(log N)` | `ForwardIterator` |
| **`std::exclusive_scan`** | `O(N)` | `O(log N)` | `ForwardIterator` |

*Де `N` — загальна кількість оброблюваних елементів у діапазоні, `P` — кількість доступних фізичних ядер або векторних ліній SIMD.*
