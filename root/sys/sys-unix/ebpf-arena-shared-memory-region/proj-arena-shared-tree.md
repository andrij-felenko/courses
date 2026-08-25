# ⚙️ Практична реалізація спільного Radix Tree в BPF Arena

Практичний проект демонструє побудову префіксного дерева (Radix Tree / LPM Trie) для високошвидкісного фільтрування IPv4-адрес безпосередньо у ядрі Linux (eBPF), де дерево динамічно оновлюється демоном простору користувача у спільній пам'яті `BPF_MAP_TYPE_ARENA`. Матеріал розроблено для інженерів мережевих систем, розробників високопродуктивних засобів безпеки та спеціалістів з eBPF для засвоєння практичних паттернів zero-copy обміну складними графами даних між ядром та користувацьким простором без викликів системного API `bpf()` під час обробки кожного пакета.

## 1. Архітектурна концепція та постановка завдання

При розробці мережевих брандмауерів або систем запобігання вторгненням (IPS) на базі eBPF виникає необхідність класифікувати мережеві пакети за їхніми IP-адресами призначення. Стандартна мапа ядра `BPF_MAP_TYPE_LPM_TRIE` дозволяє шукати маски найдовшого збігу (Longest Prefix Match), проте додавання або видалення підмереж з простору користувача вимагає системних викликів `bpf(BPF_MAP_UPDATE_ELEM)`, що створює значну затримку при масовому оновленні правил (наприклад, при завантаженні списків у сотні тисяч IP-адрес).

Шляхом використання `BPF_MAP_TYPE_ARENA` ми будуємо Radix Tree безпосередньо у розрідженому адресному просторі арени. Демон простору користувача алокує нові вузли дерева у спільній пам'яті за допомогою звичайних вказівників, будує нові гілки та атомарно змінює корінь дерева. eBPF-програма трасування, виконуючись на хуку Traffic Control (`SEC("tc")`), розіменовує вказівники коріння за допомогою кваліфікатора `__arena` та здійснює обхід дерева зі швидкістю нативної оперативної пам'яті.

## 2. Структура проекту та розподіл компонентів

Проект складається з трьох ключових вихідних файлів:
1. **`shared_tree.h`**: Спільний заголовочний файл із визначенням C-структур вузлів префіксного дерева, макросів адресного простору `__arena` та атомних прапорів синхронізації.
2. **`bpf_tree_filter.bpf.c`**: eBPF-програма трасування мережевих пакетів (`SEC("tc")`), яка приймає мережевий пакет, витягує IPv4-адресу призначення та виконує швидкий обхід Radix Tree за прямими C-вказівниками.
3. **User-Space Controller (`tree_loader`)**: Програма користувача, яка створює arena-мапу, відображає її через `mmap()`, виділяє сторінки та атомарно вставляє нові маршрути чи правила фільтрації без зупинки роботи eBPF-програми ядра.

## 3. Заголовочний файл спільної пам'яті (`shared_tree.h`)

Заголовочний файл визначає базові структури даних, які використовуються як eBPF-програмою в ядрі, так і завантажувачем у просторі користувача. Особлива увага приділяється уніфікованому виклику кваліфікатора адресного простору `__attribute__((address_space(1)))` для BPF-цілі.

```c
#ifndef SHARED_TREE_H
#define SHARED_TREE_H

#include <stdint.h>

#if defined(__BPF__)
  #define BPF_ARENA_PTR(type) type __attribute__((address_space(1))) *
#else
  #define BPF_ARENA_PTR(type) type *
#endif

#define RADIX_BRANCHES 2

struct radix_node {
    uint32_t prefix;
    uint8_t prefix_len;
    uint8_t action; /* 0 = PASS (пропустити), 1 = DROP (заблокувати) */
    uint16_t pad;
    BPF_ARENA_PTR(struct radix_node) child[RADIX_BRANCHES];
};

struct arena_root_header {
    uint32_t magic;
    uint32_t version;
    uint64_t total_lookups;
    uint64_t total_matches;
    BPF_ARENA_PTR(struct radix_node) root;
};

#define ARENA_MAGIC 0x4152454E /* Магічна константа "AREN" */

#endif /* SHARED_TREE_H */
```

### 3.1 Деталізація полів структур та вирівнювання у пам'яті

- **`struct radix_node`**: Представляє один вузол префіксного дерева. Поле `prefix` містить IP-адресу у мережевому порядку байт, `prefix_len` — довжину маски підмережі (від 0 до 32), `action` — дію при збігу. Поле `pad` вирівнює структуру до 8-байтної межі, що є критично важливим для 64-бітних архітектур x86-64 та ARM64. Масив `child[2]` містить вказівники з макросом `BPF_ARENA_PTR` на ліве (біт 0) та праве (біт 1) піддерево.
- **`struct arena_root_header`**: Розміщується на початку арени за зміщенням `0`. Поле `magic` слугує для верифікації ініціалізації арени. Поля `total_lookups` та `total_matches` є атомарними лічильниками обходу. Поле `root` утримує вказівник на корінь Radix Tree.

## 4. Код eBPF-програми у ядрі (`bpf_tree_filter.bpf.c`)

eBPF-програма компілюється під цільову архітектуру BPF. Вона аналізує кожен incoming пакет на мережевому інтерфейсі, витягує IP-адресу призначення та здійснює обхід дерева за прямими C-вказівниками.

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "shared_tree.h"

char _license[] SEC("license") = "GPL";

struct {
    __uint(type, BPF_MAP_TYPE_ARENA);
    __uint(map_flags, BPF_F_MMAPABLE);
    __uint(max_entries, 1024); /* 1024 сторінки = 4 МБ */
} arena_map SEC(".maps");

SEC("tc")
int filter_traffic(struct __sk_buff *skb)
{
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    /* Минімальна перевірка кордонів буфера Ethernet-заголовка */
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return TC_ACT_OK;

    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return TC_ACT_OK;

    /* Перевірка кордонів IP-заголовка */
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return TC_ACT_OK;

    uint32_t dst_ip = bpf_ntohl(ip->daddr);

    /* Отримання базової адреси заголовка арени */
    struct arena_root_header __arena *hdr = (struct arena_root_header __arena *)bpf_map_lookup_elem(&arena_map, &(uint32_t){0});
    if (!hdr || hdr->magic != ARENA_MAGIC)
        return TC_ACT_OK;

    __sync_fetch_and_add(&hdr->total_lookups, 1);

    /* Прямий обхід дерева за C-вказівниками у спільній пам'яті */
    struct radix_node __arena *curr = hdr->root;
    int action = TC_ACT_OK;

    while (curr) {
        if (curr->action == 1) {
            action = TC_ACT_SHOT; /* Блокування пакета */
            __sync_fetch_and_add(&hdr->total_matches, 1);
            break;
        }

        /* Обчислення біта за довжиною префікса */
        uint32_t bit_idx = 31 - curr->prefix_len;
        uint32_t bit = (dst_ip >> bit_idx) & 1;

        curr = curr->child[bit];
    }

    return action;
}
```

### 4.1 Покроковий аналіз логіки виконання eBPF-програми

1. **Перевірка межі буфера skb**: Для запобігання паніці ядра eBPF Verifier вимагає суворого порівняння вказівників `skb->data` та `skb->data_end` перед кожним розіменуванням заголовка.
2. **Конвертація порядку байт**: Функція `bpf_ntohl()` перетворює IPv4-адресу з мережевого порядку (big-endian) у хостовий порядок для бітових зсувів.
3. **Атомні лічильники**: Виклики `__sync_fetch_and_add` гарантують коректне оновлення статистики обходу без блокувань (lock-free) між багатьма CPU.
4. **Обхід дерева**: Цикл `while (curr)` розіменовує вказівник `curr->child[bit]` за допомогою JIT-маскування адреси arena.
5. **Коди повернення TC**: Функція повертає `TC_ACT_OK` для продовження передачі пакета мережевим стеком ядра або `TC_ACT_SHOT` для негайного знищення заблокованого пакета.

## 5. Контролер простору користувача (User-Space Loader)

Програма користувача створює мапу arena, відображає її у простір користувача за допомогою `mmap()`, будує Radix Tree та публікує його для ядра.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "shared_tree.h"

#define ARENA_SIZE_BYTES (1024 * 4096)

int main(int argc, char **argv)
{
    int map_fd = bpf_map_create(BPF_MAP_TYPE_ARENA, "arena_map", 0, 0, 1024, NULL);
    if (map_fd < 0) {
        perror("bpf_map_create failed");
        return 1;
    }

    void *arena_base = mmap(NULL, ARENA_SIZE_BYTES, PROT_READ | PROT_WRITE, MAP_SHARED, map_fd, 0);
    if (arena_base == MAP_FAILED) {
        perror("mmap failed");
        close(map_fd);
        return 1;
    }

    printf("[+] BPF Arena mmap success: %p\n", arena_base);

    /* Ініціалізація заголовка у спільній пам'яті */
    struct arena_root_header *hdr = (struct arena_root_header *)arena_base;
    hdr->magic = ARENA_MAGIC;
    hdr->version = 1;
    hdr->total_lookups = 0;
    hdr->total_matches = 0;

    /* Алокація коріння дерева безпосередньо у арені */
    struct radix_node *root_node = (struct radix_node *)((char *)arena_base + sizeof(struct arena_root_header));
    memset(root_node, 0, sizeof(struct radix_node));
    root_node->prefix = 0;
    root_node->prefix_len = 0;
    root_node->action = 0;

    /* Створення дочірнього вузла для заблокованої підмережі (наприклад 10.0.0.0/8) */
    struct radix_node *drop_node = root_node + 1;
    memset(drop_node, 0, sizeof(struct radix_node));
    drop_node->prefix = 0x0A000000;
    drop_node->prefix_len = 8;
    drop_node->action = 1; /* DROP */

    /* Прив'язка дочірнього вузла за вказівником арени */
    root_node->child[0] = drop_node;

    /* Атомна публікація коріння дерева для eBPF у ядрі */
    hdr->root = drop_node;
    printf("[+] Radix Tree initialized in shared BPF Arena. Root=%p\n", drop_node);

    printf("[+] Monitoring traffic... Press Enter to exit.\n");
    getchar();

    munmap(arena_base, ARENA_SIZE_BYTES);
    close(map_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "shared_tree.h"

class BpfArenaManager {
private:
    int map_fd_{-1};
    void* arena_base_{MAP_FAILED};
    size_t size_bytes_{0};

public:
    explicit BpfArenaManager(size_t page_count) : size_bytes_(page_count * 4096) {
        map_fd_ = bpf_map_create(BPF_MAP_TYPE_ARENA, "arena_map", 0, 0, static_cast<__u32>(page_count), nullptr);
        if (map_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "bpf_map_create failed");
        }

        arena_base_ = mmap(nullptr, size_bytes_, PROT_READ | PROT_WRITE, MAP_SHARED, map_fd_, 0);
        if (arena_base_ == MAP_FAILED) {
            close(map_fd_);
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
    }

    ~BpfArenaManager() {
        if (arena_base_ != MAP_FAILED) {
            munmap(arena_base_, size_bytes_);
        }
        if (map_fd_ >= 0) {
            close(map_fd_);
        }
    }

    BpfArenaManager(const BpfArenaManager&) = delete;
    BpfArenaManager& operator=(const BpfArenaManager&) = delete;

    [[nodiscard]] void* get_base() const noexcept { return arena_base_; }
    [[nodiscard]] int get_fd() const noexcept { return map_fd_; }
};

int main()
{
    try {
        BpfArenaManager arena(1024);
        std::cout << "[+] BPF Arena mmap success: " << arena.get_base() << std::endl;

        auto* hdr = static_cast<struct arena_root_header*>(arena.get_base());
        hdr->magic = ARENA_MAGIC;
        hdr->version = 1;
        hdr->total_lookups = 0;
        hdr->total_matches = 0;

        auto* root_node = reinterpret_cast<struct radix_node*>(
            static_cast<char*>(arena.get_base()) + sizeof(struct arena_root_header)
        );
        std::memset(root_node, 0, sizeof(struct radix_node));
        root_node->prefix = 0;
        root_node->prefix_len = 0;
        root_node->action = 0;

        auto* drop_node = root_node + 1;
        std::memset(drop_node, 0, sizeof(struct radix_node));
        drop_node->prefix = 0x0A000000;
        drop_node->prefix_len = 8;
        drop_node->action = 1;

        root_node->child[0] = drop_node;
        hdr->root = drop_node;

        std::cout << "[+] Radix Tree initialized in shared BPF Arena. Root=" << drop_node << std::endl;
        std::cout << "[+] Press Enter to terminate loader..." << std::endl;
        std::cin.get();

    } catch (const std::exception& ex) {
        std::cerr << "[-] Error: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
```
:::

### 5.1 Особливості реалізації C++ завантажувача

У C++ версії завантажувача застосовується паттерн RAII (Resource Acquisition Is Initialization) через клас `BpfArenaManager`:
1. Конструктор автоматично ініціалізує мапу та виконує `mmap()`. У разі помилки викликається виняток `std::system_error` із збереженням коду `errno`.
2. Деструктор гарантує виклик `munmap()` та `close()` при виході з області видимості, що повністю запобігає витокам файлових дескрипторів та пам'яті.
3. Конструктор копіювання та оператор присвоєння явно видалені (`= delete`), що гарантує єдине володіння ресурсом мапи у процесі.
4. Явні перетворення типів через `static_cast` та `reinterpret_cast` гарантують сувору типобезпеку мови C++.

## 6. Інструкція зі збірки, розгортання та тестування

Для компиляції та перевірки функціонування проекту виконайте наступні кроки в ОС Linux з ядром 6.8 або новіше.

### 6.1 Збірка eBPF та контролерів

```bash
# 1. Компіляція eBPF програми для цільової архітектури bpf
clang -O2 -g -target bpf -D__BPF__ -c bpf_tree_filter.bpf.c -o bpf_tree_filter.bpf.o

# 2. Компіляція C контролера простору користувача
gcc -O2 tree_loader.c -lbpf -o tree_loader

# 3. Компіляція C++ контролера простору користувача
g++ -O2 -std=c++17 tree_loader.cpp -lbpf -o tree_loader_cpp
```

### 6.2 Завантаження та прив'язка до мережевого інтерфейсу

```bash
# Додавання дисципліни clsact на мережевий інтерфейс eth0
sudo tc qdisc add dev eth0 clsact

# Прив'язка eBPF програми до вхідного трафіку (ingress)
sudo tc filter add dev eth0 ingress bpf da obj bpf_tree_filter.bpf.o sec tc

# Запуск C++ завантажувача для ініціалізації Radix Tree в Arena
sudo ./tree_loader_cpp
```

### 6.3 Перевірка стану мапи через `bpftool`

```bash
# Перегляд мапи arena та її вмісту
sudo bpftool map dump name arena_map

# Перегляд завантажених програм підсистемою TC
sudo bpftool prog show name filter_traffic
```

### 6.4 Типові проблеми розгортання та шляхи їх вирішення

- **Помилка `cannot use arena without JIT`**: упевнитися, що JIT увімкнено через `sysctl -w net.core.bpf_jit_enable=1`.
- **Помилка верифікатора `invalid address_space`**: перевірити використання Clang версії 18+ та прапора `-D__BPF__`.
- **Помилка `mmap failed: Permission denied`**: підвищити привілегії процесу або налаштувати `CAP_BPF`.

Використання прямих C-вказівників у BPF Arena повністю ліквідує накладні витрати на системні виклики та копіювання даних, забезпечуючи нульову затримку (zero-copy) при оновленні графів правил у ядрі.
