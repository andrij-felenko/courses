# ⚙️ Клієнт розподіленого кешу: кільце консистентного хешування та пул сокетів

Клієнтська бібліотека для взаємодії з розподіленим кешем класу Memcached або Redis Cluster бере на себе всю інтелектуальну роботу з маршрутизації ключів, балансування навантаження та оптимізації мережевого обміну. У безсерверних або слабко зв'язаних топологіях (Shared-Nothing) сервери не спілкуються один з одним, тому саме клієнтський рівень гарантує, що запит за конкретним ключем потрапить на правильний фізичний вузол.

Для досягнення максимальної пропускної здатності та стабільної латентності на рівні підмілісекунд архітектура клієнта розподіленого кешу будується на чотирьох фундаментальних механізмах:
1. **Детерміноване консистентне хешування (Consistent Hashing Ring).** Відображення безперервного простору ключів на дискретні фізичні вузли з використанням віртуальних вузлів (vnodes) для рівномірного розподілу навантаження та мінімізації міграції ключів при зміні складу кластера.
2. **Пул постійних TCP-з'єднань (Connection Pooling).** Усунення накладних витрат на тристороннє рукостискання TCP (SYN, SYN/ACK, ACK) та повільний старт TCP (Slow Start) через повторне використання вже відкритих сокетів.
3. **Управління мережевими прапорцями.** Обов'язкове встановлення опції `TCP_NODELAY` для вимкнення алгоритму Нейгла (англ. *Nagle's algorithm*), що запобігає штучним затримкам буферизації дрібних пакетів до 40 мілісекунд.
4. **Станційний парсер мережевих фреймів (Stateful Frame Parser).** Обробка розривів TCP-потоку, коли повний пакет відповіді розбивається операційною системою на кілька окремих мережевих сегментів.

Нижче наведено технічний розбір внутрішньої будови та повнофункціональну реалізацію клієнта розподіленого кешу мовами C та ідіоматичною C++.

---

## 1. Архітектурна схема маршрутизації та обробки запиту

```
Застосунок (Виклик client.get("user:101:profile"))
   │
   ▼
[ 1. Обчислення некриптографічного хешу FNV-1a(Key) ] ──► Отримання 32-бітного числа TargetHash
   │
   ▼
[ 2. Двійковий пошук (Binary Search) на кільці VNodes ] ──► Знаходження першого вузла з Hash >= TargetHash
   │                                                        (З урахуванням замкненого кола / Wrap-around)
   ▼
[ 3. Отримання сокета з пулу з'єднань (Socket Pool) ] ────► Пул виділяє готовий дескриптор FD
   │
   ▼
[ 4. Серіалізація та запис фрейму в TCP-дескриптор ] ───► Системний виклик write() / send()
   │
   ▼
[ 5. Неблокувальне вичитування відповіді та парсинг ] ──► Декодування фрейму (RESP2 або Memcached ASCII)
   │
   ▼
Повернення розпарсеного значення клієнтському коду
```

---

## 2. Реалізація клієнта: Кільце хешів, VNodes та форматування фреймів

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define FNV_PRIME_32 16777619U
#define FNV_OFFSET_32 2166136261U
#define MAX_VNODES_TOTAL 4096
#define MAX_SERVERS 32

/* 32-бітний швидкий некриптографічний алгоритм FNV-1a */
static uint32_t fnv1a_hash(const char *key, size_t len) {
    uint32_t hash = FNV_OFFSET_32;
    for (size_t i = 0; i < len; ++i) {
        hash ^= (uint8_t)key[i];
        hash *= FNV_PRIME_32;
    }
    return hash;
}

typedef struct {
    char host[64];
    int port;
} ServerNode;

typedef struct {
    uint32_t hash;
    size_t server_index;
} VNodeEntry;

typedef struct {
    ServerNode servers[MAX_SERVERS];
    size_t server_count;
    VNodeEntry ring[MAX_VNODES_TOTAL];
    size_t ring_size;
} HashRing;

/* Функція порівняння для впорядкування віртуальних вузлів */
static int compare_vnodes(const void *a, const void *b) {
    const VNodeEntry *va = (const VNodeEntry *)a;
    const VNodeEntry *vb = (const VNodeEntry *)b;
    if (va->hash < vb->hash) return -1;
    if (va->hash > vb->hash) return 1;
    return 0;
}

void hash_ring_init(HashRing *ring) {
    ring->server_count = 0;
    ring->ring_size = 0;
}

bool hash_ring_add_server(HashRing *ring, const char *host, int port, size_t vnodes_per_server) {
    if (ring->server_count >= MAX_SERVERS) return false;
    if (ring->ring_size + vnodes_per_server > MAX_VNODES_TOTAL) return false;

    size_t s_idx = ring->server_count++;
    strncpy(ring->servers[s_idx].host, host, sizeof(ring->servers[s_idx].host) - 1);
    ring->servers[s_idx].host[sizeof(ring->servers[s_idx].host) - 1] = '\0';
    ring->servers[s_idx].port = port;

    char vnode_key[128];
    for (size_t v = 0; v < vnodes_per_server; ++v) {
        snprintf(vnode_key, sizeof(vnode_key), "%s:%d#%zu", host, port, v);
        uint32_t h = fnv1a_hash(vnode_key, strlen(vnode_key));
        ring->ring[ring->ring_size++] = (VNodeEntry){ .hash = h, .server_index = s_idx };
    }

    qsort(ring->ring, ring->ring_size, sizeof(VNodeEntry), compare_vnodes);
    return true;
}

/* Двійковий пошук першого вузла на кільці з hash >= key_hash */
const ServerNode* hash_ring_lookup(const HashRing *ring, const char *key, size_t key_len) {
    if (ring->ring_size == 0) return NULL;

    uint32_t target = fnv1a_hash(key, key_len);
    size_t left = 0;
    size_t right = ring->ring_size;

    while (left < right) {
        size_t mid = left + (right - left) / 2;
        if (ring->ring[mid].hash >= target) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }

    /* Якщо дійшли кінця кола — беремо нульовий вузол (замкнене кільце) */
    size_t chosen_idx = (left == ring->ring_size) ? 0 : left;
    return &ring->servers[ring->ring[chosen_idx].server_index];
}

/* Форматування командного рядка Memcached ASCII */
size_t format_memcached_set(char *buf, size_t max_len, const char *key, const char *val, uint32_t ttl) {
    size_t val_len = strlen(val);
    return snprintf(buf, max_len, "set %s 0 %u %zu\r\n%s\r\n", key, ttl, val_len, val);
}

size_t format_memcached_get(char *buf, size_t max_len, const char *key) {
    return snprintf(buf, max_len, "get %s\r\n", key);
}

int main(void) {
    HashRing ring;
    hash_ring_init(&ring);

    hash_ring_add_server(&ring, "10.0.1.10", 11211, 128);
    hash_ring_add_server(&ring, "10.0.1.11", 11211, 128);
    hash_ring_add_server(&ring, "10.0.1.12", 11211, 128);

    const char *test_keys[] = {"user:101:profile", "session:token_abc", "cart:items_998"};
    char cmd_buf[512];

    for (size_t i = 0; i < 3; ++i) {
        const ServerNode *node = hash_ring_lookup(&ring, test_keys[i], strlen(test_keys[i]));
        format_memcached_get(cmd_buf, sizeof(cmd_buf), test_keys[i]);
        printf("Ключ '%s' -> Вузол %s:%d | Команда: %s", test_keys[i], node->host, node->port, cmd_buf);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <format>
#include <cstdint>
#include <optional>
#include <span>

namespace cache {

// 32-бітний детермінований FNV-1a constexpr хеш
constexpr uint32_t fnv1a(std::string_view key) noexcept {
    uint32_t hash = 2166136261U;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619U;
    }
    return hash;
}

struct ServerEndpoint {
    std::string host;
    uint16_t port;

    auto operator<=>(const ServerEndpoint&) const = default;
};

class ConsistentHashRing {
public:
    struct VNode {
        uint32_t hash;
        size_t server_index;

        bool operator<(const VNode& other) const noexcept {
            return hash < other.hash;
        }
    };

    void add_server(std::string host, uint16_t port, size_t vnodes = 128) {
        size_t s_idx = servers_.size();
        servers_.push_back(ServerEndpoint{std::move(host), port});

        for (size_t v = 0; v < vnodes; ++v) {
            std::string vnode_label = std::format("{}:{}#{}", servers_[s_idx].host, servers_[s_idx].port, v);
            uint32_t h = fnv1a(vnode_label);
            ring_.push_back(VNode{h, s_idx});
        }

        std::sort(ring_.begin(), ring_.end());
    }

    [[nodiscard]] std::optional<ServerEndpoint> lookup(std::string_view key) const noexcept {
        if (ring_.empty()) {
            return std::nullopt;
        }

        uint32_t h = fnv1a(key);
        auto it = std::lower_bound(ring_.begin(), ring_.end(), VNode{h, 0});

        if (it == ring_.end()) {
            it = ring_.begin(); // Замикання кільця (wrap-around)
        }

        return servers_[it->server_index];
    }

    [[nodiscard]] std::span<const ServerEndpoint> servers() const noexcept {
        return servers_;
    }

private:
    std::vector<ServerEndpoint> servers_;
    std::vector<VNode> ring_;
};

// Форматувальник бінарно-безпечного протоколу Redis RESP2
class RespFormatter {
public:
    static std::string format_get(std::string_view key) {
        return std::format("*2\r\n$3\r\nGET\r\n${}\r\n{}\r\n", key.size(), key);
    }

    static std::string format_set(std::string_view key, std::string_view value, uint32_t ex_seconds) {
        return std::format("*4\r\n$3\r\nSET\r\n${}\r\n{}\r\n${}\r\n{}\r\n$2\r\nEX\r\n:{}\r\n",
                           key.size(), key, value.size(), value, ex_seconds);
    }
};

} // namespace cache

int main() {
    cache::ConsistentHashRing ring;
    ring.add_server("10.0.1.10", 6379, 128);
    ring.add_server("10.0.1.11", 6379, 128);
    ring.add_server("10.0.1.12", 6379, 128);

    std::vector<std::string_view> keys = {
        "user:101:profile",
        "session:token_abc",
        "cart:items_998"
    };

    for (auto key : keys) {
        if (auto node = ring.lookup(key)) {
            std::string cmd = cache::RespFormatter::format_get(key);
            std::cout << std::format("Ключ '{}' -> Вузол {}:{}\n", key, node->host, node->port);
        }
    }

    return 0;
}
```
:::

---

## 3. Поглиблений аналіз компонентів реалізації

### 1. Вибір хеш-функції та структура віртуальних вузлів
У наведеній реалізації застосовано алгоритм **FNV-1a**. Він демонструє відмінний коефіцієнт лавинного ефекту (англ. *avalanche effect*) на коротких рядках при мінімальній кількості тактів процесора (одна операція XOR та одне множення на байт). Криптографічні хеші на кшталт SHA-256 або SHA-1 створюють зайве навантаження на процесорні конвеєри, тоді як стандартна бібліотечна функція `std::hash` у C++ не гарантує однакового результату між різними компіляторами або перезапусками процесу, що є неприпустимим для розподіленого узгодження.

Кожен фізичний вузол отримує 128 віртуальних міток (vnodes). Формування мітки у вигляді рядка `host:port#index` забезпечує рівномірне розсіювання точок по всьому 32-бітному колу, запобігаючи виникненню надмірно довгих дуг навантаження.

### 2. Крайовий випадок замикання кільця (Cyclic Wrap-Around)
Простір хеш-значень є циклічним. Якщо хеш запитаного ключа виявляється строго більшим за хеш найостаннішого віртуального вузла в масиві `ring_`, стандартний двійковий пошук `std::lower_bound` повертає ітератор на кінець контейнера (`ring_.end()`). 

Критична вимога коректності алгоритму полягає в явному перехопленні цієї ситуації: у разі досягнення кінця масиву клієнт зобов'язаний повернути **найперший елемент кільця** (`ring_.begin()`), замкнувши коло. Пропуск цієї перевірки призводить до аварійного звернення за межі виділеної пам'яті (Segmentation Fault / Out-of-bounds).

### 3. Мережеві налаштування TCP та уникнення блокувань
Для реального продакшн-середовища на кожен відкритий сокет клієнт зобов'язаний встановити наступні сокетні опції:
- `setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one))` — вимикає затримки пакетів Нейгла, відправляючи байти в мережу негайно.
- `setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout))` — запобігає безкінечному зависанню потоку застосунку в разі апаратного зависання кеш-сервера.
- `setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &one, sizeof(one))` — утримує постійні з'єднання відкритими крізь проміжні фаєрволи та NAT-шлюзи.
- Використання неблокувальних сокетів (`O_NONBLOCK`) у поєднанні з мультиплексуванням `epoll` або `io_uring` для одночасної конвеєризації тисяч запитів.

### 4. Управління пулом з'єднань (Connection Pool) та фрагментація відповідей
Клієнт повинен підтримувати окремий LIFO-пул відкритих дескрипторів для кожного фізичного хоста:
- При виконанні запиту потік забирає вільний сокет із черги за `O(1)`. Якщо всі сокети зайняті, створюється нове з'єднання аж до встановленого максимального ліміту (Max Pool Size).
- Оскільки TCP є потоковим протоколом без збереження меж повідомлень, окрема відповідь `VALUE ... \r\n` може бути розірвана ядром операційної системи на кілька фрагментів по 1460 байтів (розмір MSS — Maximum Segment Size). Клієнтська бібліотека використовує кільцевий буфер (Ring Buffer) із накопиченням байтів до моменту виявлення кінцевого маркера CRLF або зчитування повної кількості байтів, зазначеної в префіксі довжини фрейму.

---

## 4. Пастки та підводні камені при експлуатації

1. **Несинхронізовані карти вузлів між різними інстансами застосунку.** Якщо під час додавання нового сервера список вузлів оновлюється не одночасно у всіх вебсерверах, різні клієнти почнуть шукати той самий ключ на різних серверах. Це призводить до стану розсинхронізації кешу (англ. *cache divergence*) та підвищеного навантаження на первинну базу даних.
2. **Відсутність захисного вимикача (Circuit Breaker).** Якщо один із серверів кешу зазнає повної апаратної відмови, спроба встановити TCP-з'єднання з ним витрачатиме час таймауту ядра (типово 1–3 секунди для TCP SYN). Клієнтська бібліотека повинна містити лічильник послідовних збоїв і тимчасово виключати деградований вузол із кільця на 10–30 секунд, спрямовуючи запити на резервні вузли.
3. **Пакетні операції над багатьма ключами (Scatter-Gather MGET).** Якщо застосунок викликає операцію отримання 100 ключів одночасно, наївна реалізація надсилає 100 послідовних запитів. Правильний розподілений клієнт спочатку групує ключі за їхніми цільовими шардами на основі кільця хешування, формує N окремих пакетних команд `mget` або конвеєрів для N відповідних серверів, відправляє їх паралельно через сокети та об'єднує результати в єдину відповідь (патерн Scatter-Gather).
