# ⚙️ Реалізація таблиці узгодженого хешування Maglev для Anycast-балансувальника

Цей практичний розбір містить повний математичний аналіз, алгоритмічний опис та системну реалізацію таблиці узгодженого хешування Maglev (розробленої інженерами компанії Google для балансування мережевого трафіку). Алгоритм забезпечує стабільний розподіл пакетів між серверами в Anycast-кластерах із часовою складністю диспетчеризації `O(1)` та мінімальним перерозподілом потоків у разі відмови вузлів.

---

## 1. Постановка задачі: чому наївне хешування руйнує сесії

Усередині кожної точки присутності Anycast (Edge PoP) вхідний трафік приймається масивом паралельних L4-балансувальників, підключених до комутаторів за технологією ECMP (англ. *Equal-Cost Multi-Path*). Балансувальник не зберігає повний стан кожного TCP-з'єднання в оперативній пам'яті (щоб уникнути вичерпання пам'яті RAM при мільйонах відкритих сесій та захистити систему від SYN-flood атак), а приймає рішення про вибір цільового бекенд-сервера на основі обчислення хешу від 5-tuple заголовка пакета:

```
5-tuple: (Source IP, Destination IP, Source Port, Destination Port, Protocol)
```

Якщо використати найпростіший алгоритм залишку від ділення на кількість доступних бекендів:

```
backend_index = hash(5-tuple) mod N
```

виникає катастрофічний ефект лавини: щойно один із `N` бекендів виходить із ладу або додається новий сервер (`N` змінюється на `N - 1` або `N + 1`), математичне значення залишку від ділення змінюється майже для **всіх** активних клієнтських сесій. Усі наступні пакети активних TCP-з'єднань надходять на інші бекенди, які не мають сесійного контексту в пам'яті, що викликає генерацію прапорця `TCP RST` і миттєвий обрив завантаження у тисяч користувачів.

Традиційне консистентне хешування на кільці (алгоритм Ketama або Karger ring) зменшує частку перерозподілених ключів до `1/N`, проте операція пошуку на кільці вимагає бінарного пошуку з часовою складністю `O(\log V)` (де `V` — кількість віртуальних вузлів), що створює помітну затримку в пакетній обробці ядра на швидкостях 40–100 Гбіт/с.

Алгоритм **Maglev** розв'язує цю дилему: він забезпечує мінімальний перерозподіл сесій `1/N` (як на кільці) і водночас виконує диспетчеризацію за **одну операцію індексації в пам'яті `O(1)`** за допомогою статичної таблиці пошуку (*Lookup Table*) фіксованого розміру `M`, де `M` — велике просте число.

---

## 2. Математичний механізм заповнення таблиці Maglev

Нехай у нашому розпорядженні є `N` доступних бекенд-серверів та таблиця розміром `M` комірок.

### Крок 1. Генерація псевдовипадкових перестановок

Для кожного бекенда `i` (від `0` до `N - 1`) за допомогою двох незалежних 32-бітних хеш-функцій обчислюються початковий зсув `offset` та крок зміщення `skip`:

```
offset[i] = hash1(backend_name[i]) mod M
skip[i]   = (hash2(backend_name[i]) mod (M - 1)) + 1
```

Оскільки `M` є простим числом, а величина `skip[i]` лежить у строгому діапазоні `1 ≤ skip[i] < M`, найбільший спільний дільник:

```
НСД(skip[i], M) = 1
```

Згідно з фундаментальною теоремою теорії лишків, якщо крок і модуль є взаємно простими числами, лінійна конгруентна послідовність:

```
permutation[i][j] = (offset[i] + j · skip[i]) mod M,    де j = 0, 1, ..., M - 1
```

гарантовано містить усі числа від `0` до `M - 1` рівно по одному разу без повторень і пропусків, утворюючи повну перестановку множини комірок таблиці.

### Крок 2. Раундовий вибір комірок (Round-Robin Filling)

Таблиця `lookup_table` розміром `M` ініціалізується порожніми значеннями `-1`. Алгоритм виконує циклічний обхід бекендів:

```
[Початок: Таблиця розміром M = 7, пуста: [-1, -1, -1, -1, -1, -1, -1]]
  Раунд 1:
    Бекенд 0 пропонує permutation[0][0] -> комірка 3 (вільна -> займає B0)
    Бекенд 1 пропонує permutation[1][0] -> комірка 0 (вільна -> займає B1)
    Бекенд 2 пропонує permutation[2][0] -> комірка 4 (вільна -> займає B2)
  Раунд 2:
    Бекенд 0 пропонує permutation[0][1] -> комірка 0 (зайнята B1! -> бере наступну)
    Бекенд 0 пропонує permutation[0][2] -> комірка 1 (вільна -> займає B0)
  ...
[Кінець: Усі M комірок таблиці рівномірно заповнені ідентифікаторами бекендів]
```

Кожен бекенд зберігає свій поточний покажчик `next_idx`, тому йому не потрібно щоразу перебирати послідовність із самого початку. Складність заповнення таблиці становить `O(M \log M)` у найгіршому випадку та `O(M)` у середньому.

### Крок 3. Диспетчеризація пакета на швидкості інтерфейсу

Коли надходить вхідний пакет, балансувальник обчислює 32-бітний хеш від 5-tuple і виконує одну пряму операцію звернення за індексом до масиву в оперативній пам'яті:

```
target_backend = lookup_table[hash(5-tuple) mod M]
```

Оскільки звернення до масиву не містить розгалужень `if/else`, конвеєр команд процесора не зазнає штрафів за помилкове передбачення переходів (*Branch Misprediction*), що забезпечує максимальну пропускну здатність.

---

## 3. Реалізація алгоритму мовами C та C++

Нижче наведено робочий вихідний код побудови таблиці Maglev та симуляції обробки клієнтських пакетів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define MAGLEV_M 65537  /* Просте число для розміру таблиці */
#define MAX_BACKENDS 16

typedef struct {
    char name[32];
    uint32_t offset;
    uint32_t skip;
    uint32_t next_idx;
    bool is_alive;
} Backend;

typedef struct {
    Backend backends[MAX_BACKENDS];
    int num_backends;
    int lookup_table[MAGLEV_M];
} Maglev;

/* 32-бітний хеш FNV-1a */
static uint32_t fnv1a(const char *str, uint32_t seed) {
    uint32_t hash = 2166136261u ^ seed;
    while (*str) {
        hash ^= (uint8_t)(*str++);
        hash *= 16777619u;
    }
    return hash;
}

/* 5-tuple хешування клієнтського пакета */
static uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip, 
                            uint16_t src_port, uint16_t dst_port, uint8_t proto) {
    uint32_t h = src_ip;
    h ^= (dst_ip << 1) | (dst_ip >> 31);
    h ^= ((uint32_t)src_port << 16) | dst_port;
    h ^= (uint32_t)proto * 0x5bd1e995;
    h ^= h >> 13;
    h *= 0x5bd1e995;
    h ^= h >> 15;
    return h;
}

void maglev_init(Maglev *m) {
    m->num_backends = 0;
    for (int i = 0; i < MAGLEV_M; ++i) {
        m->lookup_table[i] = -1;
    }
}

void maglev_add_backend(Maglev *m, const char *name) {
    if (m->num_backends >= MAX_BACKENDS) return;
    int idx = m->num_backends++;
    strncpy(m->backends[idx].name, name, sizeof(m->backends[idx].name) - 1);
    m->backends[idx].name[sizeof(m->backends[idx].name) - 1] = '\0';
    m->backends[idx].is_alive = true;

    /* Обчислюємо offset та skip за двома різними сідами */
    m->backends[idx].offset = fnv1a(name, 0x12345678) % MAGLEV_M;
    m->backends[idx].skip = (fnv1a(name, 0x87654321) % (MAGLEV_M - 1)) + 1;
}

void maglev_rebuild_table(Maglev *m) {
    for (int i = 0; i < MAGLEV_M; ++i) {
        m->lookup_table[i] = -1;
    }
    for (int i = 0; i < m->num_backends; ++i) {
        m->backends[i].next_idx = 0;
    }

    int filled = 0;
    while (filled < MAGLEV_M) {
        for (int i = 0; i < m->num_backends; ++i) {
            if (!m->backends[i].is_alive) continue;

            uint32_t offset = m->backends[i].offset;
            uint32_t skip = m->backends[i].skip;
            uint32_t j = m->backends[i].next_idx;

            while (true) {
                uint32_t candidate = (offset + j * skip) % MAGLEV_M;
                j++;
                if (m->lookup_table[candidate] == -1) {
                    m->lookup_table[candidate] = i;
                    m->backends[i].next_idx = j;
                    filled++;
                    break;
                }
            }
            if (filled == MAGLEV_M) break;
        }
    }
}

int maglev_dispatch(const Maglev *m, uint32_t src_ip, uint32_t dst_ip,
                    uint16_t src_port, uint16_t dst_port, uint8_t proto) {
    uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
    uint32_t idx = h % MAGLEV_M;
    return m->lookup_table[idx];
}

int main(void) {
    Maglev m;
    maglev_init(&m);
    maglev_add_backend(&m, "srv-app-01.eu-central");
    maglev_add_backend(&m, "srv-app-02.eu-central");
    maglev_add_backend(&m, "srv-app-03.eu-central");
    maglev_add_backend(&m, "srv-app-04.eu-central");

    maglev_rebuild_table(&m);

    printf("Таблицю Maglev розміром %d успішно заповнено для %d бекендів.\n", MAGLEV_M, m.num_backends);

    /* Тестова диспетчеризація клієнтського потоку */
    uint32_t client_ip = 0xC0000201; /* 192.0.2.1 */
    uint32_t vip = 0xC6336401;       /* 198.51.100.1 */
    uint16_t client_port = 54321;
    uint16_t svc_port = 443;
    uint8_t proto = 6; /* TCP */

    int b_idx = maglev_dispatch(&m, client_ip, vip, client_port, svc_port, proto);
    printf("Пакет від 192.0.2.1:%u спрямовано на бекенд [%s]\n", client_port, m.backends[b_idx].name);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <cstdint>
#include <stdexcept>

class MaglevRing {
public:
    static constexpr uint32_t TABLE_SIZE = 65537; // Просте число M

    struct Backend {
        std::string name;
        uint32_t offset{0};
        uint32_t skip{0};
        uint32_t next_idx{0};
        bool is_alive{true};
    };

    explicit MaglevRing(std::vector<std::string> names) {
        backends_.reserve(names.size());
        for (const auto& name : names) {
            add_backend(name);
        }
        rebuild_table();
    }

    void add_backend(std::string_view name) {
        Backend b;
        b.name = std::string(name);
        b.is_alive = true;
        b.offset = fnv1a(name, 0x12345678) % TABLE_SIZE;
        b.skip = (fnv1a(name, 0x87654321) % (TABLE_SIZE - 1)) + 1;
        backends_.push_back(std::move(b));
    }

    void set_backend_status(size_t index, bool alive) {
        if (index >= backends_.size()) throw std::out_of_range("Invalid backend index");
        backends_[index].is_alive = alive;
        rebuild_table();
    }

    void rebuild_table() {
        lookup_table_.fill(-1);
        for (auto& b : backends_) {
            b.next_idx = 0;
        }

        uint32_t filled = 0;
        while (filled < TABLE_SIZE) {
            for (size_t i = 0; i < backends_.size(); ++i) {
                if (!backends_[i].is_alive) continue;

                auto& b = backends_[i];
                while (true) {
                    uint32_t candidate = (b.offset + b.next_idx * b.skip) % TABLE_SIZE;
                    b.next_idx++;
                    if (lookup_table_[candidate] == -1) {
                        lookup_table_[candidate] = static_cast<int>(i);
                        filled++;
                        break;
                    }
                }
                if (filled == TABLE_SIZE) break;
            }
        }
    }

    [[nodiscard]] const Backend& dispatch(uint32_t src_ip, uint32_t dst_ip,
                                          uint16_t src_port, uint16_t dst_port,
                                          uint8_t proto) const {
        uint32_t h = hash_5tuple(src_ip, dst_ip, src_port, dst_port, proto);
        int backend_id = lookup_table_[h % TABLE_SIZE];
        if (backend_id < 0 || static_cast<size_t>(backend_id) >= backends_.size()) {
            throw std::runtime_error("Lookup table uninitialized or empty");
        }
        return backends_[static_cast<size_t>(backend_id)];
    }

private:
    static uint32_t fnv1a(std::string_view str, uint32_t seed) noexcept {
        uint32_t hash = 2166136261u ^ seed;
        for (char c : str) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 16777619u;
        }
        return hash;
    }

    static uint32_t hash_5tuple(uint32_t src_ip, uint32_t dst_ip,
                                uint16_t src_port, uint16_t dst_port,
                                uint8_t proto) noexcept {
        uint32_t h = src_ip;
        h ^= (dst_ip << 1) | (dst_ip >> 31);
        h ^= (static_cast<uint32_t>(src_port) << 16) | dst_port;
        h ^= static_cast<uint32_t>(proto) * 0x5bd1e995;
        h ^= h >> 13;
        h *= 0x5bd1e995;
        h ^= h >> 15;
        return h;
    }

    std::vector<Backend> backends_;
    std::array<int, TABLE_SIZE> lookup_table_;
};

int main() {
    MaglevRing router({
        "srv-app-01.eu-central",
        "srv-app-02.eu-central",
        "srv-app-03.eu-central",
        "srv-app-04.eu-central"
    });

    std::cout << "Таблицю Maglev збудовано на " << MaglevRing::TABLE_SIZE << " комірок.\n";

    uint32_t client_ip = 0xC0000201; // 192.0.2.1
    uint32_t vip = 0xC6336401;       // 198.51.100.1
    uint16_t client_port = 54321;
    uint16_t svc_port = 443;
    uint8_t proto = 6; // TCP

    const auto& target = router.dispatch(client_ip, vip, client_port, svc_port, proto);
    std::cout << "Клієнтський потік спрямовано на: " << target.name << '\n';

    return 0;
}
```
:::

---

## 4. Порівняльний інженерний аналіз та властивості кешу процесора

### Взаємодія з кешем процесора (CPU Cache Locality)

Однією з головних архітектурних переваг Maglev є компактність структури даних. Таблиця з `M = 65537` цілих 32-бітних чисел (`int32_t`) займає в пам'яті:

```
65537 × 4 байти = 262 148 байтів (≈ 256 КБ)
```

Розмір кеш-пам'яті L2 сучасного серверного процесора (наприклад, AMD Zen 4 або Intel Sapphire Rapids) становить від 1 до 2 МБ на одне ядро. Це означає, що вся таблиця Maglev гарантовано й повністю поміщається в кеш L2 процесора, не витісняючи інші дані.

Кожне звернення до таблиці під час обробки чергового пакета обслуговується кешем L2 із затримкою близько 3–5 наносекунд, що дозволяє одному процесорному ядру самостійно диспетчеризувати понад 10 мільйонів пакетів на секунду (10 Mpps) при використанні фреймворків DPDK або XDP.

### Стійкість до відмов: аналіз поведінки пулу

Уявімо кластер із `N = 10` бекендів. Кожен бекенд у таблиці займає приблизно `10%` комірок (`M / 10 ≈ 6553` слоти).

1. **Відмова одного сервера:** Коли сервер 5 виходить із ладу, його слоти в таблиці перерозподіляються між іншими 9 серверами за їхніми наступними пріоритетними перестановками. Рівно `1/10` (10%) клієнтських сесій, які раніше обслуговувалися сервером 5, плавно переходять на інші машини. Решта `90%` сесій, які йшли на сервери 0..4 та 6..9, **залишаються на своїх серверах без жодних змін**.
2. **Введення нового сервера:** Коли додається 11-й сервер, він забирає собі приблизно `1/11` (9%) комірок від усіх наявних вузлів. Лише 9% сесій перенаправляються на новий вузол для наповнення його черги, тоді як 91% клієнтів не відчувають жодних збоїв.

### Вагове балансування (Weighted Backends)

Якщо в кластері є сервери різної обчислювальної потужності (наприклад, старі машини з 32 ядрами та нові з 128 ядрами), Maglev легко підтримує ваговий баланс:
У циклі заповнення таблиці потужніший сервер робить не 1, а кілька кроків підряд (наприклад, 4 кроки вибору комірки за один раунд). У результаті він отримує у 4 рази більше слотів у таблиці пошуку, пропорційно забираючи на себе 80% вхідного трафіку без ускладнення алгоритму диспетчеризації `O(1)`.

### Порівняння з кільцем Ketama та традиційними структурами

| Характеристика | Наївне `hash mod N` | Кільце Ketama (Karger Ring) | Таблиця Maglev (Google) |
|---|---|---|---|
| **Часова складність пошуку** | `O(1)` | `O(\log V)` (бінарний пошук) | `O(1)` (пряма індексація) |
| **Витрати пам'яті** | `O(1)` (немає стану) | `O(V)` (масив хешів вузлів) | `O(M)` (фіксована таблиця 256 КБ) |
| **Частка перерозподілу сесій** | `~100%` (лавина збоїв) | `~1/N` (мінімальна) | `~1/N` (мінімальна) |
| **Локальність у кеші CPU** | Ідеальна | Середня (стрибки пам'яті) | Ідеальна (поміщається в L2) |
| **Придатність для 100G L4** | Непридатна (рве TCP) | Обмежена (високий CPU cost) | Ідеальна (галузевий стандарт) |

---

## 5. Інженерні пастки та рекомендації щодо впровадження

1. **Критичність простоти числа `M`:** Якщо обрати `M = 65536` (степінь двійки), алгоритм зависне при побудові. Будь-який парний `skip` матиме `НСД(skip, 65536) > 1`, через що генератор застрягне в циклі з парних чисел. Число `65537` є простим числом Ферма (`2¹⁶ + 1`), що робить його ідеальним кандидатом.
2. **Атомарне перемикання таблиць у ядрі (RCU):** Під час зміни складу кластера фоновий потік будує нову таблицю в окремому буфері пам'яті, після чого підміняє активний покажчик за допомогою механізму Read-Copy-Update (RCU). Робочі потоки обробки пакетів продовжують вичитувати стару таблицю без блокувань (Lock-Free), а нові пакети миттєво підхоплюють оновлений розподіл.
3. **Хешування симетричного потоку (Symmetric Hashing):** Щоб прямий і зворотний напрямки одного з'єднання потрапляли на один вузол у схемах без DSR, хеш-функція 5-tuple повинна бути комутативною щодо адрес і портів (`src_ip ^ dst_ip` та `src_port ^ dst_port`).
