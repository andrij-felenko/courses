# ⚙️ Реалізація двонапрямленого списка з вузлами-вартовими

Зв'язаний список є однією з фундаментальних структур даних у комп'ютерних науках, але його наївна реалізація у навчальних посібниках часто потерпає від нестійкого коду з великою кількістю умовних розгалужень вигляду `if (head == NULL)` або `if (node->prev != NULL)`. Додавання чи видалення елемента на початку або в кінці списка вимагає обробки цілої серії окремих крайових випадків. У цій практичній роботі ми детально розберемо та побудуємо законсервовану виробничу реалізацію **двохзв'язаного списка з фіктивним вузлом-вартовим (Sentinel Node)**.

## 1. Проблема крайових випадків у наївній реалізації

У звичайному двохзв'язаному списку порожній стан контейнера виражається двома обнуленими вказівниками у структурі управління: `head = NULL` та `tail = NULL`.

Розглянемо, до яких ускладнень це призводить під час виконання базових операцій:

1. **Вставка в порожній список**: Програміст мусить перевірити `if (head == NULL)` і присвоїти новостворений вузол двом змінним одразу: і `head`, і `tail`.
2. **Вставка на початок непорожнього списка**: Потрібно оновити `head->prev = new_node`, потім `new_node->next = head` і врешті перевизначити саму змінну `head = new_node`.
3. **Вставка у середину**: Вимагає оновлення 4 покажчиків сусідніх вузлів (`prev->next`, `next->prev`, `new_node->prev`, `new_node->next`).
4. **Видалення єдиного елемента**: Потрібно обнулити і `head`, і `tail`.

Такий складний розподіл за гілками умовних операторів у разі найменшої неуважності програміста спричиняє появу висячих покажчиків (Dangling Pointers), розрив зв'язків у пам'яті та важковловимі витоки пам'яті (Memory Leaks).

## 2. Ідея та інваріанти вузла-вартового (Sentinel Node)

Революційним покращенням архітектури списка є додавання фіктивного вартового вузла `head_sentinel`. Цей вузол виділяється раз при створенні списка і існує протягом усього його життєвого циклу. Він не містить корисних даних.

Математичні та структурні інваріанти списка з вартовим:

- **Порожній список**: Покажчики вартового зациклюються самі на себе: `sentinel.next = &sentinel` та `sentinel.prev = &sentinel`.
- **Кільцева структура**: Список стає замкненим кільцем навколо вартового вузла.
- **Перший реальний елемент**: Завжди знаходиться за адресою `sentinel.next`.
- **Останній реальний елемент**: Завжди знаходиться за адресою `sentinel.prev`.
- **Відсутність `NULL`**: Жоден реальний вузол у списку більше ніколи не містить покажчиків `NULL` у полях `next` або `prev`!

Завдяки цим інваріантам операції вставки та видалення для **будь-якого** місця у списку (на початку, в кінці чи всередині) зводяться до абсолютно одинакового 4-рядкового коду без жодного оператора `if`!

## 3. Виробнича реалізація: C та C++

Нижче наведено робочу реалізацію двохзв'язаного списка мовами C та C++.

:::tabs
```c
/* dlist.c — Виробнича реалізація двохзв'язаного списка з вартовим мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node {
    int data;
    struct Node* prev;
    struct Node* next;
} Node;

typedef struct {
    Node sentinel; /* Фіктивний вузол-вартовий */
    size_t size;
} DoublyLinkedList;

/* Ініціалізація порожнього списка */
void dlist_init(DoublyLinkedList* list) {
    list->sentinel.next = &list->sentinel;
    list->sentinel.prev = &list->sentinel;
    list->size = 0;
}

/* Перевірка на порожнечу */
bool dlist_is_empty(const DoublyLinkedList* list) {
    return list->sentinel.next == &list->sentinel;
}

/* Вставка нового вузла між двома наявними вузлами prev_node та next_node */
static void dlist_insert_between(Node* new_node, Node* prev_node, Node* next_node) {
    new_node->prev = prev_node;
    new_node->next = next_node;
    prev_node->next = new_node;
    next_node->prev = new_node;
}

/* Видалення вузла з відв'язуванням покажчиків */
static void dlist_unlink(Node* node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
}

/* Додавання елемента в кінець списка — O(1) */
bool dlist_push_back(DoublyLinkedList* list, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return false;
    
    new_node->data = value;
    /* Вставляємо між останнім вузлом (sentinel.prev) та вартовим (sentinel) */
    dlist_insert_between(new_node, list->sentinel.prev, &list->sentinel);
    list->size++;
    return true;
}

/* Додавання елемента на початок списка — O(1) */
bool dlist_push_front(DoublyLinkedList* list, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return false;
    
    new_node->data = value;
    /* Вставляємо між вартовим (sentinel) та першим вузлом (sentinel.next) */
    dlist_insert_between(new_node, &list->sentinel, list->sentinel.next);
    list->size++;
    return true;
}

/* Видалення вузла з голови списка — O(1) */
bool dlist_pop_front(DoublyLinkedList* list, int* out_value) {
    if (dlist_is_empty(list)) return false;
    
    Node* first = list->sentinel.next;
    if (out_value) *out_value = first->data;
    
    dlist_unlink(first);
    free(first);
    list->size--;
    return true;
}

/* Звільнення всієї пам'яті списка */
void dlist_destroy(DoublyLinkedList* list) {
    Node* current = list->sentinel.next;
    while (current != &list->sentinel) {
        Node* next_node = current->next;
        free(current);
        current = next_node;
    }
    dlist_init(list);
}

int main(void) {
    DoublyLinkedList list;
    dlist_init(&list);

    dlist_push_back(&list, 10);
    dlist_push_back(&list, 20);
    dlist_push_front(&list, 5);

    printf("Розмір списка: %zu\n", list.size);

    int val;
    while (dlist_pop_front(&list, &val)) {
        printf("Вилучено елемент: %d\n", val);
    }

    dlist_destroy(&list);
    return 0;
}
```
```cpp
// dlist.cpp — Ідіоматичний RAII-шаблон двохзв'язаного списка C++20
#include <iostream>
#include <memory>
#include <utility>
#include <cstddef>
#include <string>

template <typename T>
class DoublyLinkedList {
private:
    struct Node {
        T data;
        Node* prev{nullptr};
        Node* next{nullptr};

        template <typename... Args>
        explicit Node(Args&&... args) 
            : data(std::forward<Args>(args)...) {}
    };

    Node sentinel_;
    std::size_t size_{0};

    void insert_between(Node* new_node, Node* prev_node, Node* next_node) noexcept {
        new_node->prev = prev_node;
        new_node->next = next_node;
        prev_node->next = new_node;
        next_node->prev = new_node;
    }

    void unlink(Node* node) noexcept {
        node->prev->next = node->next;
        node->next->prev = node->prev;
    }

public:
    DoublyLinkedList() noexcept {
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
    }

    ~DoublyLinkedList() noexcept {
        clear();
    }

    // Заборона копіювання для простоти управління ресурсами
    DoublyLinkedList(const DoublyLinkedList&) = delete;
    DoublyLinkedList& operator=(const DoublyLinkedList&) = delete;

    // Переміщення списку
    DoublyLinkedList(DoublyLinkedList&& other) noexcept : DoublyLinkedList() {
        if (!other.empty()) {
            sentinel_.next = other.sentinel_.next;
            sentinel_.prev = other.sentinel_.prev;
            sentinel_.next->prev = &sentinel_;
            sentinel_.prev->next = &sentinel_;
            size_ = std::exchange(other.size_, 0);
            other.sentinel_.next = &other.sentinel_;
            other.sentinel_.prev = &other.sentinel_;
        }
    }

    [[nodiscard]] bool empty() const noexcept {
        return sentinel_.next == &sentinel_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return size_;
    }

    template <typename... Args>
    void emplace_back(Args&&... args) {
        auto* new_node = new Node(std::forward<Args>(args)...);
        insert_between(new_node, sentinel_.prev, &sentinel_);
        ++size_;
    }

    void push_back(const T& value) { emplace_back(value); }
    void push_back(T&& value) { emplace_back(std::move(value)); }

    bool pop_front(T& out_value) {
        if (empty()) return false;
        Node* first = sentinel_.next;
        out_value = std::move(first->data);
        unlink(first);
        delete first;
        --size_;
        return true;
    }

    void clear() noexcept {
        Node* current = sentinel_.next;
        while (current != &sentinel_) {
            Node* next_node = current->next;
            delete current;
            current = next_node;
        }
        sentinel_.next = &sentinel_;
        sentinel_.prev = &sentinel_;
        size_ = 0;
    }
};

int main() {
    DoublyLinkedList<std::string> list;
    list.push_back("Комірка 1");
    list.push_back("Комірка 2");
    list.emplace_back("Комірка 3");

    std::cout << "Розмір: " << list.size() << "\n";

    std::string item;
    while (list.pop_front(item)) {
        std::cout << "Отримано: " << item << "\n";
    }

    return 0;
}
```
:::

## 4. Детальний аналіз алгоритмічного кроку вставки

Розберемо фундаментальну функцію `insert_between(new_node, prev_node, next_node)`:

1. **Крок 1: Ініціалізація нових покажчиків**: `new_node->prev = prev_node` та `new_node->next = next_node`. Оскільки `new_node` є ізольованим вузлом у купі, модифікація його полів не впливає на цілісність існуючого списку.
2. **Крок 2: Перенаправлення покажчиків сусідам**: `prev_node->next = new_node` та `next_node->prev = new_node`. Тільки на цьому кроці новий вузол фізично вбудовується у кільце списку.

Сувора послідовність цих дій гарантує, що навіть при виникненні апаратних переривань або асинхронних подій стан списку залишається узгодженим.

## 5. Оптимізація пам'яті за допомогою пулу вузлів (Pool Allocator)

Стандартний підхід із викликом `malloc()` або `new` на кожен вузол створює великі накладні витрати на заголовки аллокатора й спричиняє сильну фрагментацію пам'яті.

Для усунення цієї проблеми у високопродуктивних системах використовується **пул аллокації вузлів (Node Pool Allocator)**:
- Аллокатор заздалегідь виділяє суцільний масив пам'яті на `1000` або `10000` вузлів.
- Вільні вузли організовуються у внутрішній однозв'язаний список вільних блоків (Free List).
- Вставка нового вузла бере готову комірку з пулу за миттєвий час `O(1)` без системного виклику купи.
- Оскільки вузли з пулу розміщені у суцільному масиві, обхід списка зазнає значно меншої кількості промахів кешу L1/L2!

## 6. Багатопотоковість, синхронізація та проблему ABA

При використанні зв'язаних списків у багатопотокових програмах розробники зіштовхуються з важкими проблемами гонки даних (Data Race):

1. **Потреба м'ютексів**: Будь-яка модифікація покажчиків `prev` і `next` мусить виконуватися під захистом взаємного виключення (`std::mutex` у C++ або `pthread_mutex_t` у C).
2. **Lock-Free списки та атомарні операції**: Спроба реалізувати список без блокувань спирається на атомарну інструкцію `Compare-And-Swap` (CAS).
3. **Проблема ABA у Lock-Free списках**: Якщо потік A зчитує вказівник на вузол X, потім потік B видаляє X, звільняє його пам'ять і створює новий вузол Y у **тій самій фізичній адресі**, потік A може хибно вирішити через CAS, що список не змінювався! Для розв'язання проблеми ABA застосовують підрахунок базованих версій (Tagged Pointers), указателі Hazard Pointers або захист за допомогою Read-Copy Update (RCU).

## 7. Інженерні пастки, баги та крайові випадки

Під час проектирования системних списків розробники найчастіше припускаються п'яти типових помилок:

1. **Непослідовна модифікація вказівників при вставці**:
   Якщо спочатку виконати `prev_node->next = new_node`, а лише потім намагатися прочитати `prev_node->next` для ініціалізації `new_node->next`, код прочитає адресу самого `new_node` і створить циклічне зациклення вузла на самого себе!

2. **Використання вилученої пам'яті (Use-After-Free)**:
   Типова помилка у циклі очищення списку:
```text
while (current != NULL) {
    free(current);
    current = current->next; /* БАГ: Зчитування з уже звільненого вузла! */
}
```
   *Виправлення*: Завжди зберігайте адресу наступного вузла у тимчасову змінну `Node* next_node = current->next` до виклику `free(current)`.

3. **Німі витоки пам'яті при винятках у C++**:
   Якщо конструктор типів `T` викидає виняток при створенні об'єкта в `emplace_back()`, оператор `new Node(...)` коректно звільняє пам'ять. Але якщо виняток виникає під час обробки списку, деструктор `~DoublyLinkedList()` повинен мати специфікацію `noexcept` та надійно обходити й звільняти всі вузли, щоб запобігти витоку ресурсів.

4. **Проблема неатомного оновлення розміру**:
   Поле `size` повинно оновлюватися строго синхронно з операціями вставки та видалення. У багатопотокових середовищах довільний доступ до списку вимагає захисту м'ютексом або використання lock-free інтрузивних алгоритмів.
