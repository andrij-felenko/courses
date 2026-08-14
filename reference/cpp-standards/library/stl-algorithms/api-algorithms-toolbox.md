# 📋 Довідник алгоритмів STL: класифікація, сигнатури та складність

Цей довідник надає повний систематизований розбір сигнатур, механізмів виконання, вимог до категорій ітераторів та асимптотичної складності для алгоритмів стандартної бібліотеки C++ (заголовки `<algorithm>` та `<numeric>`). Для кожного алгоритму наведено традиційний синтаксис пар ітераторів C++98/C++11 та еквівалентні варіанти C++20 Ranges із підтримкою проєкцій.

---

## 1. Немодифікуючі алгоритми пошуку та аналізу

Алгоритми цієї категорії проходять по послідовності без модифікації елементів. Вони працюють із найпростішою категорією `InputIterator` для одноразового проходу або `ForwardIterator` для повторних проходів. Вони не змінюють порядок або стан елементів і надають гарантії безпеки щодо винятків: якщо предикат користувача не кидає винятків, алгоритм також не кидає винятків.

### Пошук першого збігу

```cpp
// Традиційний синтаксис
template <class InputIt, class T>
InputIt find(InputIt first, InputIt last, const T& value);

template <class InputIt, class UnaryPredicate>
InputIt find_if(InputIt first, InputIt last, UnaryPredicate p);

template <class InputIt, class UnaryPredicate>
InputIt find_if_not(InputIt first, InputIt last, UnaryPredicate q);

// C++20 Ranges
namespace std::ranges {
    template <input_range R, class T, class Proj = std::identity>
    borrowed_iterator_t<R> find(R&& r, const T& value, Proj proj = {});
}
```

#### Детальний механізм виконання
Алгоритм `std::find` послідовно проходить від `first` до `last`, розіменовуючи ітератор та порівнюючи отримане значення з `value` за допомогою `operator==`. Виконання негайно зупиняється на першому елементі, для якого порівняння повертає `true`. У виклику `std::find_if` замість оператора рівності значення передається у предикат `p`.

#### Гарантії складності
Складність є лінійною `O(N)`, де `N = distance(first, last)`. Кількість викликів компаратора або предиката не перевищує `N`.

#### Крайові випадки та винятки
Якщо діапазон порожній (`first == last`) або жоден елемент не задовольняє умову, алгоритм повертає ітератор `last`. При передачі ітераторів довільного доступу (`RandomAccessIterator`) асимптотика пошуку залишається лінійною `O(N)`, бо дані неупорядковані.

---

### Кількісний підрахунок та перевірка кванторів

```cpp
// Підрахунок входжень
template <class InputIt, class T>
typename iterator_traits<InputIt>::difference_type
count(InputIt first, InputIt last, const T& value);

template <class InputIt, class UnaryPredicate>
typename iterator_traits<InputIt>::difference_type
count_if(InputIt first, InputIt last, UnaryPredicate p);

// Логічні квантори (C++11)
template <class InputIt, class UnaryPredicate>
bool all_of(InputIt first, InputIt last, UnaryPredicate p);

template <class InputIt, class UnaryPredicate>
bool any_of(InputIt first, InputIt last, UnaryPredicate p);

template <class InputIt, class UnaryPredicate>
bool none_of(InputIt first, InputIt last, UnaryPredicate p);
```

#### Детальний механізм виконання
`count` та `count_if` сканують послідовність від початку до кінця і повертають число типів `difference_type`. Квантори `all_of`, `any_of` та `none_of` здійснюють перевірку з коротким замиканням: `any_of` перериває цикл при першому `true`, тоді як `all_of` та `none_of` переривають цикл при першому `false`.

#### Гарантії складності
У найгіршому випадку робиться ровно `N` перевірок `O(N)`.

#### Крайові випадки
Для порожнього діапазону `[first, last)` квантори `all_of` та `none_of` повертають `true`, а `any_of` повертає `false` відповідно до законів математичної логіки про вакуумну істинність.

---

### Пошук підпослідовностей та сусідніх дублікатів

```cpp
// Пошук двох однакових сусідніх елементів
template <class ForwardIt>
ForwardIt adjacent_find(ForwardIt first, ForwardIt last);

// Пошук першого входження підпослідовності [s_first, s_last)
template <class ForwardIt1, class ForwardIt2>
ForwardIt1 search(ForwardIt1 first, ForwardIt1 last,
                  ForwardIt2 s_first, ForwardIt2 s_last);
```

#### Детальний механізм виконання
`adjacent_find` шукає два сусідні елементи `*i == *(i+1)`. Алгоритм `search` шукає повний збіг підпослідовності. Для складних шаблонів у C++17 додано пошуковці Боєра-Мура (`std::boyer_moore_searcher`).

#### Складність
Для `adjacent_find` — `O(N)`. Для базового `search` — `O(N · M)` у найгіршому випадку.

---

## 2. Модифікуючі та мутуючі алгоритми

Алгоритми цієї групи перезаписують значення, переставляють елементи або змінюють їхні зв'язки. Вони вимагають категорій `OutputIterator`, `ForwardIterator` або `BidirectionalIterator`.

### Копіювання та переміщення

```cpp
// Послідовне копіювання
template <class InputIt, class OutputIt>
OutputIt copy(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class UnaryPredicate>
OutputIt copy_if(InputIt first, InputIt last, OutputIt d_first, UnaryPredicate pred);

// Переміщення елементів через rvalue-посилання (C++11)
template <class InputIt, class OutputIt>
OutputIt move(InputIt first, InputIt last, OutputIt d_first);

// Копіювання у зворотному напрямку (для перекриваються діапазонів)
template <class BidiIt1, class BidiIt2>
BidiIt2 copy_backward(BidiIt1 first, BidiIt1 last, BidiIt2 d_last);
```

#### Детальний механізм виконання
`std::copy` розіменовує ітератор джерела та присвоює значення у приймач. `std::move` перетворює кожен елемент на rvalue через `std::move(*it)` та викликає оператор присвоєння переміщенням.

#### Вимоги до перекриття діапазонів
Цільовий діапазон `[d_first, d_first + N)` не повинен перекриватися з джерелом `[first, last)` у спосіб, коли `d_first` потрапляє всередину джерела. Якщо цільова адреса перекриває кінець джерела, необхідно використовувати `copy_backward`, який ітерується від кінця до початку.

#### Векторні оптимізації
Для тривіально копійованих типів (`std::is_trivially_copyable_v<T> == true`) компілятор за допомогою оптимізацій замінює поелементне копіювання у шаблоні на виклик системної функції `std::memcpy` або `std::memmove`.

---

### Трансформація, генерація та заповнення

```cpp
// Унарна трансформація: destination[i] = op(source[i])
template <class InputIt, class OutputIt, class UnaryOperation>
OutputIt transform(InputIt first, InputIt last, OutputIt d_first, UnaryOperation op);

// Бінарна трансформація: destination[i] = op(source1[i], source2[i])
template <class InputIt1, class InputIt2, class OutputIt, class BinaryOperation>
OutputIt transform(InputIt1 first1, InputIt1 last1, InputIt2 first2,
                  OutputIt d_first, BinaryOperation binary_op);

// Заповнення константою або результатами генератора
template <class ForwardIt, class T>
void fill(ForwardIt first, ForwardIt last, const T& value);

template <class ForwardIt, class Generator>
void generate(ForwardIt first, ForwardIt last, Generator g);
```

#### Детальний механізм виконання
`std::transform` зчитує кожен елемент з одного чи двох джерел, передає їх у трансформаційну функцію і записує результат у приймач. `std::fill` записує константне значення `value`, а `std::generate` записує результат виклику генератора `g()`.

#### Складність
Рівно `N` викликів трансформаційної функції або оператора присвоєння `O(N)`.

---

### Перегрупування та видалення елементів (Remove-Erase)

```cpp
// Зсув небажаних значень у кінець діапазону
template <class ForwardIt, class T>
ForwardIt remove(ForwardIt first, ForwardIt last, const T& value);

template <class ForwardIt, class UnaryPredicate>
ForwardIt remove_if(ForwardIt first, ForwardIt last, UnaryPredicate p);

// Вилучення послідовних однаковим елементів у впорядкованому масиві
template <class ForwardIt>
ForwardIt unique(ForwardIt first, ForwardIt last);
```

#### Детальний механізм виконання та Remove-Erase ідіома
Алгоритми `remove`, `remove_if` та `unique` **не змінюють розмір контейнера та не звільняють пам'ять**. Вони лише перезаписують неугодні елементи тими елементами справа, які мають залишитися, за допомогою оператора присвоєння переміщенням (`move assignment`). 

Алгоритм повертає ітератор `new_end`, який відокремлює нові валідні дані від "залишкового хвоста" елементів у стані `moved-from`. Для фізичного видалення залишкового хвоста викликається метод контейнера `.erase(new_end, end)`.

#### Складність
Лінійна `O(N)` з виконанням не більше `N` перевірок і переміщень.

---

## 3. Сортування, розділення та впорядкування

Ця категорія алгоритмів вимагає категорій `RandomAccessIterator` для досягнення логарифмічно-лінійного часу виконання.

### Повне, стабільне та часткове сортування

```cpp
// Стандартне сортування (Introsort)
template <class RandomIt>
void sort(RandomIt first, RandomIt last);

template <class RandomIt, class Compare>
void sort(RandomIt first, RandomIt last, Compare comp);

// Стабільне сортування (збереження відносного порядку однакових елементів)
template <class RandomIt>
void stable_sort(RandomIt first, RandomIt last);

// Часткове сортування: перші K елементів стають впорядкованими
template <class RandomIt>
void partial_sort(RandomIt first, RandomIt middle, RandomIt last);

// Пошук K-го порядкового елемента (Quickselect)
template <class RandomIt>
void nth_element(RandomIt first, RandomIt nth, RandomIt last);

// Розділення масиву на дві частини за предикатом
template <class ForwardIt, class UnaryPredicate>
ForwardIt partition(ForwardIt first, ForwardIt last, UnaryPredicate p);
```

#### Детальний механізм виконання алгоритмів сортування

- **`std::sort`**: Реалізовано як Introsort. Починає із QuickSort. Якщо глибина рекурсії перевищує `2 · log2(N)`, перемикається на HeapSort для уникнення найгіршого випадку `O(N²)`. На малих підмасивах (менше 16–32 елементів) використовує InsertionSort. Складність — строго `O(N log N)`. Додаткова пам'ять — `O(log N)` для стеку рекурсії.
- **`std::stable_sort`**: Реалізовано на основі модифікованого MergeSort. Якщо системі вдається виділити додатковий буфер пам'яті розміром `O(N)`, складність складає `O(N log N)`. Якщо виділити пам'ять не вдалося, алгоритм виконується за час `O(N log² N)` без додаткової пам'яті.
- **`std::partial_sort`**: Впорядковує лише елементи в діапазоні `[first, middle)`. Решта масиву в `[middle, last)` лишається в невпорядкованому стані. Використовує HeapSort за час `O(N log K)`, де `K = distance(first, middle)`.
- **`std::nth_element`**: Переставляє елементи так, що на позиції `nth` опиняється той елемент, який стояв би там при повному сортуванні. Усі елементи ліворуч від `nth` стають меншими або рівними йому, а елементи праворуч — більшими або рівними. Середня складність — `O(N)`.
- **`std::partition`**: Розділяє елементи на дві частини: ліворуч опиняються ті, для яких предикат повертає `true`, праворуч — `false`. Не вимагає сортування. Складність — строго `O(N)`.

---

## 4. Двійковий пошук на впорядкованих діапазонах

Працюють виключно на діапазонах, які попередньо відсортовані за відповідним компаратором.

```cpp
// Пошук першого елемента, не меншого за значення (>=)
template <class ForwardIt, class T>
ForwardIt lower_bound(ForwardIt first, ForwardIt last, const T& value);

// Пошук першого елемента, строго більшого за значення (>)
template <class ForwardIt, class T>
ForwardIt upper_bound(ForwardIt first, ForwardIt last, const T& value);

// Отримання пари ітераторів [lower_bound, upper_bound)
template <class ForwardIt, class T>
std::pair<ForwardIt, ForwardIt> equal_range(ForwardIt first, ForwardIt last, const T& value);

// Перевірка наявності елемента
template <class ForwardIt, class T>
bool binary_search(ForwardIt first, ForwardIt last, const T& value);
```

#### Детальні гарантії складності
- При передачі `RandomAccessIterator` (наприклад `std::vector::begin()`): кількість порівнянь і кроків складає `O(log N)`.
- При передачі `ForwardIterator` (наприклад `std::list::begin()`): кількість порівнянь складає `O(log N)`, проте кількість переходів по вказівниках вузлів є лінійною `O(N)` через виклики `std::advance`.

---

## 5. Чисельні та математичні алгоритми (`<numeric>`)

Алгоритми обчислення згортки, префіксних сум та скалярних добутків.

```cpp
// Класичне послідовне накопичення (C++98)
template <class InputIt, class T>
T accumulate(InputIt first, InputIt last, T init);

template <class InputIt, class T, class BinaryOperation>
T accumulate(InputIt first, InputIt last, T init, BinaryOperation op);

// Паралельна згортка (C++17)
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOperation>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init, BinaryOperation op);

// Трансформація та згортка (MapReduce)
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T,
          class BinaryOp1, class BinaryOp2>
T transform_reduce(ExecutionPolicy&& policy, ForwardIt1 first1, ForwardIt1 last1,
                 ForwardIt2 first2, T init, BinaryOp1 transform_op, BinaryOp2 reduce_op);

// Генерація послідовності інкрементованих значень (v[0]=val, v[1]=val+1...)
template <class ForwardIt, class T>
void iota(ForwardIt first, ForwardIt last, T value);
```

#### Відмінності `accumulate` та `reduce`
`std::accumulate` виконує строго послідовну ліву згортку від першого елемента до останнього. `std::reduce` з C++17 дає змогу виконувати довільне перегрупування та паралелізацію операцій між нитками процесора. Для коректності результату `std::reduce` вимагає, щоб операція `BinaryOperation` була **асоціативною та комутативною**.

---

## 6. Політики виконання C++17 (Execution Policies)

Заголовок `<execution>` додає параметри політики виконання для понад 60 стандартних алгоритмів:

1. `std::execution::seq` — послідовне виконання в поточному потоці (аналог класичних алгоритмів).
2. `std::execution::par` — паралельне виконання у багаторазових потоках (потокобезпека функцій користувача обов'язкова).
3. `std::execution::par_unseq` — паралельне та векторизоване виконання (дозволяє перекриття інструкцій SIMD; заборонені будь-які м'ютекси чи локальні статичні змінні у предикатах).
4. `std::execution::unseq` (C++20) — векторизоване виконання в єдиному потоці.

Приклад виклику паралельного сортування:
```cpp
#include <algorithm>
#include <execution>
#include <vector>

std::vector<int> data = {/* великий масив */};
std::sort(std::execution::par, data.begin(), data.end());
```
