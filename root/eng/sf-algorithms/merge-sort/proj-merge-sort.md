# ⚙️ Практичні реалізації Merge Sort: від буферної оптимізації до однозв'язних списків

Наївна академічна реалізація сортування злиттям часто виділяє динамічну пам'ять (`malloc` або `new`) всередині кожного рекурсивного виклику процедури злиття. Для масиву з `n` елементів це призводить до створення `O(n)` дрібних динамічних буферів та виконання `O(n log n)` запитів до системного менеджера пам'яті. У багатопотоковому середовищі часті блокування глобального розподілювача (heap allocator lock contention) та фрагментація адресного простору спричиняють падіння продуктивності у 5–10 разів.

У цьому практичному розділі детально розібрано три оптимізовані інженерні реалізації алгоритму:
1. **Промислове низхідне сортування (Top-Down Merge Sort):** виділення єдиного допоміжного буфера на вході, гібридне перемикання на сортування вставками на малих підмасивах та рання перевірка впорядкованості стику.
2. **Висхідне ітеративне сортування (Bottom-Up Merge Sort):** повна відмова від стеку викликів та техніка подвійного буфера (ping-pong buffering) без зворотного копіювання елементів.
3. **Сортування однозв'язного списку (Linked List Merge Sort):** алгоритм двох вказівників для пошуку середини та чисте переплетення покажчиків із константною додатковою пам'яттю `O(1)`.

---

## 1. Промислове низхідне сортування (Top-Down)

Промислова реалізація усуває три головні джерела накладних витрат:
- **Єдиний допоміжний буфер (Single Auxiliary Buffer):** масив пам'яті `aux` розміром `n` виділяється рівно один раз у точці входу публічної функції та передається за вказівником або посиланням крізь усі рівні рекурсії. Це усуває тисячі повторних алокацій і звільнень пам'яті на купі.
- **Гібридне відсікання (Cutoff to Insertion Sort):** коли розмір робочого діапазону стає меншим за 16–32 елементи (`hi - lo + 1 <= 16`), накладні витрати на виклики функцій, поділ індексів та рекурсивний спуск перевищують час роботи простого прямого циклу. На цьому рівні алгоритм перемикається на локальне [сортування вставками](root:sf-algorithms/insertion-sort), яке працює безпосередньо в регістрах та кек-лініях L1 CPU без додаткових звернень до пам'яті.
- **Перевірка впорядкованості стику (Early Exit Test):** якщо найбільший елемент лівої половини не перевищує найменший елемент правої половини (`arr[mid] <= arr[mid + 1]`), увесь діапазон уже є монотонно зростаючим. Виклик трудомісткої процедури `merge()` пропускається, що забезпечує лінійний час `O(n)` на відсортованих послідовностях.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MERGE_INSERTION_CUTOFF 16

/* Локальне сортування вставками для підмасиву arr[lo..hi] */
static void insertion_sort_range(int *arr, size_t lo, size_t hi) {
    for (size_t i = lo + 1; i <= hi; ++i) {
        int key = arr[i];
        size_t j = i;
        while (j > lo && arr[j - 1] > key) {
            arr[j] = arr[j - 1];
            --j;
        }
        arr[j] = key;
    }
}

/* Злиття двох впорядкованих підмасивів arr[lo..mid] та arr[mid+1..hi] */
static void merge(int *arr, int *aux, size_t lo, size_t mid, size_t hi) {
    /* Копіюємо робочий діапазон у допоміжний буфер */
    for (size_t k = lo; k <= hi; ++k) {
        aux[k] = arr[k];
    }

    size_t i = lo;
    size_t j = mid + 1;
    size_t k = lo;

    /* Двопоінтерне злиття зі збереженням стійкості (<=) */
    while (i <= mid && j <= hi) {
        if (aux[i] <= aux[j]) {
            arr[k++] = aux[i++];
        } else {
            arr[k++] = aux[j++];
        }
    }

    /* Докопіювання залишку лівої частини (якщо права вичерпалася) */
    while (i <= mid) {
        arr[k++] = aux[i++];
    }
    /* Залишок правої частини вже стоїть на своїх місцях у масиві arr */
}

/* Внутрішня рекурсивна функція */
static void merge_sort_recursive(int *arr, int *aux, size_t lo, size_t hi) {
    if (hi - lo + 1 <= MERGE_INSERTION_CUTOFF) {
        insertion_sort_range(arr, lo, hi);
        return;
    }

    size_t mid = lo + (hi - lo) / 2;
    merge_sort_recursive(arr, aux, lo, mid);
    merge_sort_recursive(arr, aux, mid + 1, hi);

    /* Оптимізація: пропуск злиття, якщо половини вже впорядковані */
    if (arr[mid] <= arr[mid + 1]) {
        return;
    }

    merge(arr, aux, lo, mid, hi);
}

/* Публічний інтерфейс сортування злиттям */
bool merge_sort(int *arr, size_t n) {
    if (!arr || n <= 1) {
        return true;
    }

    int *aux = (int *)malloc(n * sizeof(int));
    if (!aux) {
        return false; /* Помилка виділення пам'яті */
    }

    merge_sort_recursive(arr, aux, 0, n - 1);
    free(aux);
    return true;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <concepts>
#include <functional>
#include <utility>

namespace algorithms {

constexpr std::size_t InsertionSortThreshold = 16;

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void insertion_sort_span(std::span<T> data, Compare comp = Compare{}) {
    const std::size_t n = data.size();
    for (std::size_t i = 1; i < n; ++i) {
        T key = std::move(data[i]);
        std::size_t j = i;
        while (j > 0 && comp(key, data[j - 1])) {
            data[j] = std::move(data[j - 1]);
            --j;
        }
        data[j] = std::move(key);
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_top_down(std::span<T> arr, std::span<T> aux, 
                    std::size_t lo, std::size_t mid, std::size_t hi, 
                    Compare comp) {
    for (std::size_t k = lo; k <= hi; ++k) {
        aux[k] = std::move(arr[k]);
    }

    std::size_t i = lo;
    std::size_t j = mid + 1;
    std::size_t k = lo;

    while (i <= mid && j <= hi) {
        /* Збереження стійкості: comp(aux[j], aux[i]) замість <= */
        if (!comp(aux[j], aux[i])) {
            arr[k++] = std::move(aux[i++]);
        } else {
            arr[k++] = std::move(aux[j++]);
        }
    }

    while (i <= mid) {
        arr[k++] = std::move(aux[i++]);
    }
    while (j <= hi) {
        arr[k++] = std::move(aux[j++]);
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort_recursive(std::span<T> arr, std::span<T> aux, 
                          std::size_t lo, std::size_t hi, 
                          Compare comp) {
    if (hi - lo + 1 <= InsertionSortThreshold) {
        insertion_sort_span(arr.subspan(lo, hi - lo + 1), comp);
        return;
    }

    const std::size_t mid = lo + (hi - lo) / 2;
    merge_sort_recursive(arr, aux, lo, mid, comp);
    merge_sort_recursive(arr, aux, mid + 1, hi, comp);

    /* Якщо стик уже впорядкований — злиття не потрібне */
    if (!comp(arr[mid + 1], arr[mid])) {
        return;
    }

    merge_top_down(arr, aux, lo, mid, hi, comp);
}

/* Публічна узагальнена функція сортування злиттям */
template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort(std::span<T> data, Compare comp = Compare{}) {
    if (data.size() <= 1) {
        return;
    }

    std::vector<T> aux(data.size());
    merge_sort_recursive(data, std::span<T>(aux), 0, data.size() - 1, comp);
}

} // namespace algorithms
```
:::

---

## 2. Висхідне ітеративне сортування (Bottom-Up)

Висхідна версія алгоритму повністю усуває рекурсивний стек викликів. Замість поділу масиву згори вниз, алгоритм стартує з блоків одиничного розміру (`width = 1`) і послідовно подвоює їхню ширину на кожному проході (`1 -> 2 -> 4 -> 8 ...`).

Ключова оптимізація полягає у застосуванні **подвійного буфера (ping-pong buffering)**. Замість того, щоб зливати дані в буфер і потім копіювати їх назад у вихідний масив, алгоритм на кожному кроці міняє покажчики `src` та `dst` місцями:
- На парних проходах джерелом є `arr`, а приймачем — `aux`.
- На непарних проходах джерелом стає `aux`, а приймачем — `arr`.
- Це вдвічі скорочує кількість операцій запису в оперативну пам'ять (з `2n log₂ n` до `n log₂ n`), зменшуючи трафік шини пам'яті на 50%.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN_VAL(a, b) (((a) < (b)) ? (a) : (b))

/* Ітеративне злиття двох сусідніх блоків розміром width із src у dst */
static void merge_blocks(const int *src, int *dst, size_t lo, size_t mid, size_t hi) {
    size_t i = lo;
    size_t j = mid;
    size_t k = lo;

    while (i < mid && j < hi) {
        if (src[i] <= src[j]) {
            dst[k++] = src[i++];
        } else {
            dst[k++] = src[j++];
        }
    }

    while (i < mid) {
        dst[k++] = src[i++];
    }
    while (j < hi) {
        dst[k++] = src[j++];
    }
}

/* Висхідне ітеративне сортування злиттям з подвійним буфером */
bool merge_sort_bottom_up(int *arr, size_t n) {
    if (!arr || n <= 1) {
        return true;
    }

    int *aux = (int *)malloc(n * sizeof(int));
    if (!aux) {
        return false;
    }

    int *src = arr;
    int *dst = aux;

    /* Подвоєння ширини блоків: 1, 2, 4, 8, 16 ... */
    for (size_t width = 1; width < n; width *= 2) {
        for (size_t i = 0; i < n; i += 2 * width) {
            size_t lo = i;
            size_t mid = MIN_VAL(i + width, n);
            size_t hi = MIN_VAL(i + 2 * width, n);
            merge_blocks(src, dst, lo, mid, hi);
        }

        /* Зміна ролей буферів (Ping-Pong перемикання) */
        int *temp = src;
        src = dst;
        dst = temp;
    }

    /* Якщо фінальний результат опинився в aux, копіюємо його назад в arr */
    if (src != arr) {
        for (size_t i = 0; i < n; ++i) {
            arr[i] = src[i];
        }
    }

    free(aux);
    return true;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <algorithm>
#include <concepts>
#include <functional>

namespace algorithms {

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_blocks_iterative(std::span<const T> src, std::span<T> dst, 
                           std::size_t lo, std::size_t mid, std::size_t hi, 
                           Compare comp) {
    std::size_t i = lo;
    std::size_t j = mid;
    std::size_t k = lo;

    while (i < mid && j < hi) {
        if (!comp(src[j], src[i])) {
            dst[k++] = src[i++];
        } else {
            dst[k++] = src[j++];
        }
    }

    while (i < mid) {
        dst[k++] = src[i++];
    }
    while (j < hi) {
        dst[k++] = src[j++];
    }
}

template <typename T, typename Compare = std::less<T>>
    requires std::strict_weak_order<Compare, T, T>
void merge_sort_bottom_up(std::span<T> arr, Compare comp = Compare{}) {
    const std::size_t n = arr.size();
    if (n <= 1) {
        return;
    }

    std::vector<T> aux(n);
    std::span<T> src = arr;
    std::span<T> dst = aux;

    for (std::size_t width = 1; width < n; width *= 2) {
        for (std::size_t i = 0; i < n; i += 2 * width) {
            const std::size_t lo = i;
            const std::size_t mid = std::min(i + width, n);
            const std::size_t hi = std::min(i + 2 * width, n);
            merge_blocks_iterative<T, Compare>(src, dst, lo, mid, hi, comp);
        }

        std::swap(src, dst);
    }

    /* Якщо останній прохід записав дані у вектор aux, повертаємо їх в arr */
    if (src.data() != arr.data()) {
        std::copy(src.begin(), src.end(), arr.begin());
    }
}

} // namespace algorithms
```
:::

---

## 3. Сортування однозв'язного списку з O(1) додаткової пам'яті

Для зв'язаних динамічних списків сортування злиттям демонструє фундаментальну перевагу над масивами: воно взагалі не потребує виділення динамічної пам'яті на купі.
- Середина списку знаходиться алгоритмом двох вказівників Флойдівського типу («черепаха і заєць»): повільний вказівник робить 1 крок, а швидкий — 2 кроки. Коли швидкий досягає кінця списку, повільний вказує на точну середину.
- Фаза злиття полягає виключно у зміні напрямку посилань `next` за допомогою фіктивного початкового вузла (dummy head), зберігаючи всі вузли на їхніх вихідних адресах пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct ListNode {
    int val;
    struct ListNode *next;
} ListNode;

/* Пошук середини списку та розрив зв'язку */
static ListNode* split_list(ListNode *head) {
    if (!head || !head->next) {
        return NULL;
    }

    ListNode *slow = head;
    ListNode *fast = head->next;

    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }

    ListNode *mid = slow->next;
    slow->next = NULL; /* Розриваємо список на дві частини */
    return mid;
}

/* Злиття двох впорядкованих списків без виділення вузлів */
static ListNode* merge_lists(ListNode *l1, ListNode *l2) {
    ListNode dummy;
    ListNode *tail = &dummy;
    dummy.next = NULL;

    while (l1 && l2) {
        if (l1->val <= l2->val) {
            tail->next = l1;
            l1 = l1->next;
        } else {
            tail->next = l2;
            l2 = l2->next;
        }
        tail = tail->next;
    }

    tail->next = l1 ? l1 : l2;
    return dummy.next;
}

/* Головна рекурсивна функція сортування списку */
ListNode* sort_list(ListNode *head) {
    if (!head || !head->next) {
        return head;
    }

    ListNode *mid = split_list(head);
    ListNode *left = sort_list(head);
    ListNode *right = sort_list(mid);

    return merge_lists(left, right);
}
```
```cpp
#include <iostream>
#include <memory>
#include <utility>

template <typename T>
struct ForwardNode {
    T val;
    std::unique_ptr<ForwardNode<T>> next;

    explicit ForwardNode(T value) : val(std::move(value)), next(nullptr) {}
};

template <typename T>
class ForwardListSort {
public:
    using NodePtr = std::unique_ptr<ForwardNode<T>>;

    static NodePtr sort(NodePtr head) {
        if (!head || !head->next) {
            return head;
        }

        NodePtr mid = split(head);
        NodePtr left = sort(std::move(head));
        NodePtr right = sort(std::move(mid));

        return merge(std::move(left), std::move(right));
    }

private:
    static NodePtr split(NodePtr& head) {
        if (!head || !head->next) {
            return nullptr;
        }

        ForwardNode<T>* slow = head.get();
        ForwardNode<T>* fast = head->next.get();

        while (fast && fast->next) {
            slow = slow->next.get();
            fast = fast->next->next.get();
        }

        NodePtr mid = std::move(slow->next);
        slow->next = nullptr;
        return mid;
    }

    static NodePtr merge(NodePtr l1, NodePtr l2) {
        NodePtr dummy = std::make_unique<ForwardNode<T>>(T{});
        ForwardNode<T>* tail = dummy.get();

        while (l1 && l2) {
            if (l1->val <= l2->val) {
                NodePtr next_l1 = std::move(l1->next);
                tail->next = std::move(l1);
                l1 = std::move(next_l1);
            } else {
                NodePtr next_l2 = std::move(l2->next);
                tail->next = std::move(l2);
                l2 = std::move(next_l2);
            }
            tail = tail->next.get();
        }

        tail->next = l1 ? std::move(l1) : std::move(l2);
        return std::move(dummy->next);
    }
};
```
:::

---

## 4. Профілювання, апаратні пастки та бенчмарки

Під час практичного використання Merge Sort на сучасних багаторівневих мікроархітектурах процесорів виникають такі ключові апаратні ефекти:

1. **Обмеження пропускної здатності шини оперативної пам'яті (Memory Bandwidth Bottleneck):**
   На відміну від Quicksort, який здійснює обміни всередині вихідного масиву і зберігає високу кек-локальність, сортування злиттям вимагає сумарного запису `2n log₂ n` елементів (або `n log₂ n` із подвійним буфером). Коли розмір вхідного масиву перевищує обсяг кеш-пам'яті L3 (наприклад, 10 000 000 64-бітних чисел, що займають 80 МБ даних плюс 80 МБ буфера), швидкість алгоритму повністю обмежується пропускною здатністю контролера пам'яті DRAM. Вирівнювання виділених буферів за межею 64 байтів (розмір кек-лінії процесора) дозволяє уникнути розщеплених транзакцій читання й запису.

2. **Штрафи передбачення розгалужень (Branch Misprediction Penalty):**
   У внутрішньому циклі злиття умова `aux[i] <= aux[j]` на випадкових рівномірно розподілених даних виконується з імовірністю приблизно 50%. Модуль динамічного передбачення переходів CPU (branch target buffer / branch predictor) зазнає систематичних промахів, що призводить до скидання конвеєра інструкцій та втрати 15–20 процесорних тактів на кожен невдалий прогноз. Для масивів числових типів компілятори C та C++ оптимізують цей цикл через безгілкові інструкції умовного пересилання (`cmov` в архітектурі x86-64 або `csel` в ARM64):

:::tabs
```c
/* Безгілкова форма вибору для числових типів у C */
int cmp = (aux[i] <= aux[j]);
arr[k] = cmp ? aux[i] : aux[j];
i += cmp;
j += (1 - cmp);
k++;
```
```cpp
// Безгілкова форма умовного вибору для числових типів у C++
const bool take_left = (aux[i] <= aux[j]);
arr[k++] = take_left ? aux[i++] : aux[j++];
```
:::

Така безгілкова форма повністю усуває зупинки конвеєра процесора, забезпечуючи однаковий час сортування як на впорядкованих, так і на хаотичних вхідних масивах.
