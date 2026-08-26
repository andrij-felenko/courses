# ⚙️ Реалізація двійкового Buddy-алокатора

Двійковий алокатор близнюків (англ. *binary buddy allocator*) — це класичний алгоритм керування динамічною пам'яттю, запропонований Гаррі Ноултоном у 1965 році та детально проаналізований Дональдом Кнутом. Головна перевага алгоритму полягає в тому, що операції виділення, перевірки суміжності та зворотного злиття вільних блоків виконуються за сталий час `O(1)` завдяки швидкій побітовій арифметиці без необхідності лінійного перебору списків чи збереження службових футерів у кожному виділеному чанку.

Саме цей алгоритм є базовим механізмом підсистеми сторінкового виділення пам'яті (*Page Allocator*) ядра Linux, де вся фізична оперативна пам'ять машини нарізається блоками, розміри яких строго дорівнюють степеням двійки (`1, 2, 4, 8, \dots, 1024` сторінки).

### Принцип роботи та адреси близнюків

Алокатор керує суцільним пулом пам'яті розміром `2ᴹ` байтів. Усі операції виділення пам'яті оперують блоками фіксованих розмірів, кратних степеням двійки:

```
Розмір блоку = 2ᵏ байтів,  де  min_order ≤ k ≤ max_order
```

Внутрішня структура алокатора складається з масиву зв'язних списків вільних блоків (Free Lists), де кожен елемент масиву відповідає за свій порядок `k`.

Коли програма запитує блок розміром `S` байтів:
1. Запитаний розмір округлюється вгору до найближчого степеня двійки `2ᵏ`.
2. Алокатор звертається безпосередньо до списку порядку `k`.
3. Якщо список порядку `k` містить вільний блок, він негайно вилучається й повертається користувачеві.
4. Якщо список порожній, алокатор шукає блок у найближчому вищому списку порядку `k+1`. Знайдений більший блок ділиться на дві рівні половини — **близнюки (buddies)**. Перша половина віддається для задоволення запиту, а друга (близнюк) додається до вільного списку порядку `k`. Якщо списки вищих порядків також порожні, процес рекурсивно підіймається вгору аж до максимального порядку пулу.

#### Математичне доведення адреси близнюка через XOR

Головна перевага двійкової ієрархії полягає в тому, що для будь-якого блоку порядку `k` з відносним зсувом `offset` адреса його парного близнюка відрізняється рівно в одному біті — біті з номером `k`.

Звідси випливає фундаментальна формула обчислення зсуву близнюка за допомогою операції побітового виключного АБО (XOR):

```
buddy_offset = block_offset ^ (1 << k)
```

**Приклад розрахунку:**
Нехай мінімальний порядок `k = 13` (розмір блоку 8 КіБ, `8192` байти).
Розглянемо блок зі зсувом `0x0000`:
- Зсув блоку: `0x0000 = 0b0000000000000000`
- Маска порядку: `1 << 13 = 0x2000 = 0b0010000000000000`
- Зсув близнюка: `0x0000 ^ 0x2000 = 0x2000` (8192 у десятковій системі).

Для блоку зі зсувом `0x2000` формула дає: `0x2000 ^ 0x2000 = 0x0000`.

Ця операція є взаємною та інволютивною: `(A ^ B) ^ B = A`. Вона обчислюється процесором за один машинний такт без доступу до оперативної пам'яті.

### Алгоритм звільнення та рекурсивне злиття

Коли користувач викликає `buddy_free(ptr, size)`:
1. За покажчиком `ptr` та розміром `size` визначається поточний порядок блоку `k`.
2. За формулою `XOR` обчислюється адреса сусіда-близнюка `buddy_ptr`.
3. Алокатор перевіряє бітову карту зайнятості: якщо сусід-близнюк перебуває у вільному стані та має той самий порядок `k`, вони видаляються зі списку порядку `k` і **зливаються** в один неперервний блок порядку `k+1`.
4. Базовою адресою об'єднаного блоку стає мінімальна з двох адрес: `min(block_ptr, buddy_ptr)`.
5. Процес перевірки повторюється для порядку `k+1`, рекурсивно зливаючи блоки вгору, поки сусідній близнюк не виявиться зайнятим або не буде досягнуто максимального розміру всього пулу пам'яті.

### Покроковий життєвий цикл стану списків

Простежимо стан списків вільної пам'яті для пулу розміром 64 КіБ під час серії операцій:

1. **Ініціалізація:** у списку порядку 6 (64 КіБ) лежить 1 блок. Списки порядків 0–5 порожні.
2. **Виділення `A = alloc(8 КіБ)` (порядок 3):** блок 64 КіБ ділиться на два по 32 КіБ. Блок 32 КіБ ділиться на два по 16 КіБ. Блок 16 КіБ ділиться на два по 8 КіБ. Блок `A` повертається. У вільних списках залишаються: 1×8 КіБ (порядок 3), 1×16 КіБ (порядок 4), 1×32 КіБ (порядок 5).
3. **Виділення `B = alloc(8 КіБ)` (порядок 3):** алокатор миттєво віддає наявний вільний блок 8 КіБ. Список порядку 3 стає порожнім.
4. **Звільнення `free(A)`:** алокатор перевіряє близнюка `B`. Близнюк `B` зайнятий, тому блок `A` просто додається до списку порядку 3 без злиття.
5. **Звільнення `free(B)`:** алокатор перевіряє близнюка `A`. Оскільки `A` вільний, вони зливаються у блок 16 КіБ. Далі цей блок 16 КіБ перевіряє свого близнюка 16 КіБ у порядку 4 — той також вільний, відбувається повторне злиття у блок 32 КіБ. Цей блок зливається з близнюком 32 КіБ у порядку 5, повністю відновлюючи первинний суцільний блок 64 КіБ.

### Реалізація на мовах C та C++

Наведемо повнофункціональну інженерну реалізацію Buddy-алокатора для тестового пулу пам'яті обсягом 64 КіБ із мінімальним розміром блоку 1 КіБ (порядки від `10` до `16`, усього 7 розмірних класів).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MIN_ORDER 10       // 2^10 = 1024 байти (1 КіБ)
#define MAX_ORDER 16       // 2^16 = 65536 байтів (64 КіБ)
#define NUM_ORDERS (MAX_ORDER - MIN_ORDER + 1)
#define POOL_SIZE (1 << MAX_ORDER)

typedef struct BlockNode {
    struct BlockNode* next;
} BlockNode;

typedef struct {
    uint8_t memory_pool[POOL_SIZE];
    BlockNode* free_lists[NUM_ORDERS];
    bool is_free[POOL_SIZE / (1 << MIN_ORDER)];
} BuddyAllocator;

static inline size_t order_to_size(int order_idx) {
    return (size_t)1 << (MIN_ORDER + order_idx);
}

static inline int size_to_order(size_t size) {
    size_t actual_size = 1 << MIN_ORDER;
    int order = 0;
    while (actual_size < size && order < NUM_ORDERS - 1) {
        actual_size <<= 1;
        order++;
    }
    return order;
}

void buddy_init(BuddyAllocator* alloc) {
    memset(alloc->free_lists, 0, sizeof(alloc->free_lists));
    memset(alloc->is_free, 0, sizeof(alloc->is_free));

    // Початковий стан: один нерозділений блок максимального порядку
    BlockNode* initial_block = (BlockNode*)alloc->memory_pool;
    initial_block->next = NULL;
    alloc->free_lists[NUM_ORDERS - 1] = initial_block;
    alloc->is_free[0] = true;
}

static void list_remove(BuddyAllocator* alloc, int order_idx, BlockNode* block) {
    BlockNode** curr = &alloc->free_lists[order_idx];
    while (*curr != NULL) {
        if (*curr == block) {
            *curr = block->next;
            return;
        }
        curr = &((*curr)->next);
    }
}

void* buddy_alloc(BuddyAllocator* alloc, size_t size) {
    if (size == 0 || size > POOL_SIZE) return NULL;

    int req_order = size_to_order(size);
    int current_order = req_order;

    // Шукаємо перший непорожній список відповідного або більшого порядку
    while (current_order < NUM_ORDERS && alloc->free_lists[current_order] == NULL) {
        current_order++;
    }

    if (current_order == NUM_ORDERS) {
        return NULL; // Вільна пам'ять потрібного розміру вичерпана
    }

    // Витягуємо блок із голови вільного списку
    BlockNode* block = alloc->free_lists[current_order];
    alloc->free_lists[current_order] = block->next;

    // Рекурсивно розбиваємо блок навпіл, поки не досягнемо потрібного порядку
    while (current_order > req_order) {
        current_order--;
        size_t half_size = order_to_size(current_order);
        BlockNode* buddy = (BlockNode*)((uint8_t*)block + half_size);
        
        buddy->next = alloc->free_lists[current_order];
        alloc->free_lists[current_order] = buddy;
        
        size_t buddy_idx = ((uint8_t*)buddy - alloc->memory_pool) >> MIN_ORDER;
        alloc->is_free[buddy_idx] = true;
    }

    size_t block_idx = ((uint8_t*)block - alloc->memory_pool) >> MIN_ORDER;
    alloc->is_free[block_idx] = false;

    return (void*)block;
}

void buddy_free(BuddyAllocator* alloc, void* ptr, size_t size) {
    if (ptr == NULL || size == 0) return;

    int order = size_to_order(size);
    uint8_t* block_addr = (uint8_t*)ptr;

    while (order < NUM_ORDERS - 1) {
        size_t block_size = order_to_size(order);
        size_t block_offset = block_addr - alloc->memory_pool;
        size_t buddy_offset = block_offset ^ block_size;
        uint8_t* buddy_addr = alloc->memory_pool + buddy_offset;

        size_t buddy_idx = buddy_offset >> MIN_ORDER;

        // Якщо близнюк зайнятий або належить іншому порядку — злиття неможливе
        if (!alloc->is_free[buddy_idx]) {
            break;
        }

        // Видаляємо близнюка з вільного списку
        list_remove(alloc, order, (BlockNode*)buddy_addr);
        alloc->is_free[buddy_idx] = false;

        // Початком злитого блоку стає менша адреса
        if (buddy_addr < block_addr) {
            block_addr = buddy_addr;
        }

        order++;
    }

    // Додаємо злитий блок у список відповідного вищого порядку
    BlockNode* free_block = (BlockNode*)block_addr;
    free_block->next = alloc->free_lists[order];
    alloc->free_lists[order] = free_block;

    size_t final_idx = (block_addr - alloc->memory_pool) >> MIN_ORDER;
    alloc->is_free[final_idx] = true;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <algorithm>

template <size_t MinOrder = 10, size_t MaxOrder = 16>
class BuddyAllocator {
public:
    static constexpr size_t MinBlockSize = 1ULL << MinOrder;
    static constexpr size_t PoolSize = 1ULL << MaxOrder;
    static constexpr size_t NumOrders = MaxOrder - MinOrder + 1;
    static constexpr size_t TotalMinBlocks = PoolSize / MinBlockSize;

    enum class Error {
        OutOfMemory,
        InvalidSize,
        InvalidPointer
    };

    BuddyAllocator() noexcept {
        reset();
    }

    void reset() noexcept {
        free_lists_.fill(nullptr);
        is_free_.fill(false);

        auto* initial_block = reinterpret_cast<BlockNode*>(memory_pool_.data());
        initial_block->next = nullptr;
        free_lists_[NumOrders - 1] = initial_block;
        is_free_[0] = true;
    }

    [[nodiscard]] std::expected<std::span<std::byte>, Error> allocate(size_t size) noexcept {
        if (size == 0 || size > PoolSize) {
            return std::unexpected(Error::InvalidSize);
        }

        const size_t req_order = size_to_order(size);
        size_t current_order = req_order;

        while (current_order < NumOrders && free_lists_[current_order] == nullptr) {
            ++current_order;
        }

        if (current_order == NumOrders) {
            return std::unexpected(Error::OutOfMemory);
        }

        BlockNode* block = free_lists_[current_order];
        free_lists_[current_order] = block->next;

        while (current_order > req_order) {
            --current_order;
            const size_t half_size = order_to_size(current_order);
            auto* buddy = reinterpret_cast<BlockNode*>(reinterpret_cast<std::byte*>(block) + half_size);

            buddy->next = free_lists_[current_order];
            free_lists_[current_order] = buddy;

            const size_t buddy_idx = (reinterpret_cast<std::byte*>(buddy) - memory_pool_.data()) >> MinOrder;
            is_free_[buddy_idx] = true;
        }

        const size_t block_idx = (reinterpret_cast<std::byte*>(block) - memory_pool_.data()) >> MinOrder;
        is_free_[block_idx] = false;

        const size_t allocated_size = order_to_size(req_order);
        return std::span<std::byte>(reinterpret_cast<std::byte*>(block), allocated_size);
    }

    void deallocate(std::span<std::byte> block_span) noexcept {
        if (block_span.empty() || block_span.data() < memory_pool_.data() ||
            block_span.data() >= memory_pool_.data() + PoolSize) {
            return;
        }

        size_t order = size_to_order(block_span.size());
        auto* block_addr = block_span.data();

        while (order < NumOrders - 1) {
            const size_t block_size = order_to_size(order);
            const size_t block_offset = block_addr - memory_pool_.data();
            const size_t buddy_offset = block_offset ^ block_size;
            auto* buddy_addr = memory_pool_.data() + buddy_offset;

            const size_t buddy_idx = buddy_offset >> MinOrder;
            if (!is_free_[buddy_idx]) {
                break;
            }

            list_remove(order, reinterpret_cast<BlockNode*>(buddy_addr));
            is_free_[buddy_idx] = false;

            if (buddy_addr < block_addr) {
                block_addr = buddy_addr;
            }

            ++order;
        }

        auto* free_block = reinterpret_cast<BlockNode*>(block_addr);
        free_block->next = free_lists_[order];
        free_lists_[order] = free_block;

        const size_t final_idx = (block_addr - memory_pool_.data()) >> MinOrder;
        is_free_[final_idx] = true;
    }

private:
    struct BlockNode {
        BlockNode* next{nullptr};
    };

    alignas(std::max_align_t) std::array<std::byte, PoolSize> memory_pool_{};
    std::array<BlockNode*, NumOrders> free_lists_{};
    std::array<bool, TotalMinBlocks> is_free_{};

    [[nodiscard]] static constexpr size_t order_to_size(size_t order_idx) noexcept {
        return 1ULL << (MinOrder + order_idx);
    }

    [[nodiscard]] static constexpr size_t size_to_order(size_t size) noexcept {
        size_t actual_size = 1ULL << MinOrder;
        size_t order = 0;
        while (actual_size < size && order < NumOrders - 1) {
            actual_size <<= 1;
            ++order;
        }
        return order;
    }

    void list_remove(size_t order_idx, BlockNode* target) noexcept {
        BlockNode** curr = &free_lists_[order_idx];
        while (*curr != nullptr) {
            if (*curr == target) {
                *curr = target->next;
                return;
            }
            curr = &((*curr)->next);
        }
    }
};
```
:::

### Аналіз продуктивності та межі застосування

Buddy-алокатор демонструє найвищу швидкість серед усіх відомих алгоритмів виділення довільних розмірів, оскільки пошук списку здійснюється за `O(1)` через бітові зсуви, а коалесценція вимагає лише однієї інструкції `XOR` на кожен рівень ієрархії.

Проте за цю швидкість доводиться платити внутрішньою фрагментацією. Якщо програма виділяє об'єкт розміром 33 КіБ, алокатор змушений надати блок порядку 64 КіБ. Втрати пам'яті становлять:

```
Втрати = 64 КіБ - 33 КіБ = 31 КіБ  (майже 48% виділеного обсягу)
```

У найгіршому теоретичному випадку, коли розмір запиту становить `(2ᵏ⁻¹ + 1)` байтів, внутрішня фрагментація наближається до 50%:

```
Фрагментація = (2ᵏ - (2ᵏ⁻¹ + 1)) / 2ᵏ  ≈  50%
```

Крім того, вирівнювання блоків строго на степені двійки в апаратурі сучасних процесорів створює ризик колізій у кеш-пам'яті L1/L2 (англ. *cache set aliasing*), оскільки покажчики різних блоків мають однакові молодші біти адреси й конкурують за одні й ті самі рядки кешу.

Саме тому в сучасних операційних системах та ігрових рушіях Buddy-алокатор використовують виключно як крупнозернистий менеджер сторінок верхнього рівня (наприклад, для порцій від 4 КіБ до 4 МіБ), поверх якого розгортають дрібнозернисті Slab- або Freelist-алокатори для об'єктів точного розміру.
