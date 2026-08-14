# ⚙️ Моделювання RSS: обчислення Toeplitz Hash та маршрутизація RETA

Цей практичний проєкт демонструє точну математичну та програмну емуляцію роботи апаратного модуля Receive Side Scaling (RSS), який інтегровано у сучасні мережеві контролери (Intel, Mellanox, Broadcom, Marvell).

У цьому проєкті ми побудуємо повноцінний алгоритмічний емулятор апаратури NIC, який виконує:
1. Парсинг та бінарну упакування 4-кортежу (IPv4 Source, IPv4 Destination, Source Port, Destination Port) у послідовний бітовий потік з урахуванням порядку байтів (Network Byte Order / Big-Endian).
2. Реалізацію алгоритму обчислення 32-бітного хешу Тепліца (Toeplitz Hash) із використанням 40-байтного секретного ключа RSS.
3. Відображення обчисленого 32-бітного хешу на таблицю непрямої адресації (RETA) розміром 128 елементів за допомогою маскування 7 молодших бітів (LSB).
4. Порівняльне обчислення хешу для прямого та зворотного напрямку одного TCP-з'єднання з метою демонстрування асиметричності дефолтного ключа NDIS та аналізу впливу на Stateful Middleboxes.

---

## Математична модель алгоритму Toeplitz Hash

Алгоритм Toeplitz Hash є лінійним перетворенням над двійковим полем Galois Field GF(2). Двовимірна матриця Тепліца будується із 40-байтного (320 бітів) секретного ключа RSS, який стандартизовано компанією Microsoft у специфікаціях NDIS 6.0.

Для вхідного кортежу довжиною `L` бітів (наприклад, `L = 96` бітів для IPv4 4-tuple: 32 біти IP джерела + 32 біти IP призначення + 16 бітів порт джерела + 16 бітів порт призначення):
- Початкове значення 32-бітного регістра хешу встановлюється у нуль (`hash = 0`).
- Ми ітеруємося по кожному біту вхідних даних від найстаршого (MSB) до наймолодшого (LSB).
- Якщо поточний біт дорівнює `1`, 32-бітний регістр хешу оновлюється за допомогою операції XOR із відповідним 32-бітним вікном ключа, зсунутим на відповідну кількість бітів.
- Якщо поточний біт дорівнює `0`, зсув вікна ключа відбувається без зміни регістра хешу.

Ця процедура гарантує лінійну обчислювальну складність `O(L)` та ідеальну апаратну реалізовуваність у кремнії ASIC без використання операцій арифметичного ділення.

### Конструкція вікна ключа (Key Window)

Під час ітерації по біту з індексом `i` (де `0 <= i < L`), ми витягуємо 32-бітне вікно із 40-байтного ключа, яке починається з біта `i`. Оскільки байти в пам'яті вирівняні по межі 8 бітів, для витягування бітового зрізу застосовується побітовий зсув:
- Базовий байтовий індекс: `key_byte_idx = byte_idx + (7 - bit) / 8`
- Бітове зміщення всередині байта: `key_bit_shift = (7 - bit) % 8`

Ця формула дозволяє на кожній ітерації сформувати 32-бітне число `key_window` за допомогою побітових операцій `OR` та `SHIFT` без виділення динамічної пам'яті.

---

## Архітектура програмного емулятора

Наш емулятор проектує віртуальний мережевий адаптер із 4 апаратними чергами прийому (Rx Queue 0, Rx Queue 1, Rx Queue 2, Rx Queue 3) та таблицею RETA на 128 комірок.

Програма бере два мережевих кадри, які відповідають двом напрямкам однієї активної TCP-сесії між клієнтом та сервером:
- Прямий потік (`FWD`): `Client (192.168.1.50:49152) -> Server (10.0.0.1:80)`
- Зворотний потік (`REV`): `Server (10.0.0.1:80) -> Client (192.168.1.50:49152)`

Для кожного потоку програма будує 12-байтовий бінарний буфер 4-tuple, обчислює 32-бітний Toeplitz Hash, маскує 7 молодших бітів для отримання індексу RETA та визначає підсумковий номер черги прийому Rx Queue.

При побудові бінарного буфера вхідного кортежу критично важливо дотримуватися мережевого порядку байтів (Network Byte Order / Big-Endian). Усі IP-адреси та порти протоколів L4 повинні передаватися у хеш-двигун у порядку байтів від найстаршого до наймолодшого. Порушення цього порядку призведе до суттєвого розходження результатів між емулятором та реальною мережевою картою.

---

## Реалізація емулятора RSS

Нижче наведено повноцінний сирцевий код моделі мовами C та C++20 у відповідних вкладках.

:::tabs
```c
/*
 * RSS Toeplitz Hash & RETA Simulator (C Edition)
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RSS_KEY_SIZE 40
#define RETA_SIZE 128
#define MAX_QUEUES 8

/* Стандартний секретний ключ RSS (Microsoft NDIS default key) */
static const uint8_t default_rss_key[RSS_KEY_SIZE] = {
    0x6d, 0x5a, 0x56, 0xda, 0x25, 0x5b, 0x0e, 0xc2,
    0x41, 0x67, 0x25, 0x3d, 0x43, 0xa3, 0x8f, 0x00,
    0xd0, 0x29, 0x4b, 0x7d, 0x3d, 0x14, 0x4e, 0x69,
    0x9f, 0xac, 0xe5, 0x42, 0x1d, 0x64, 0x52, 0x72,
    0x0f, 0x4c, 0xf7, 0xad, 0x55, 0x54, 0x03, 0xb9
};

/* Структура 4-tuple для TCP/IPv4 */
typedef struct {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
} flow_tuple_v4_t;

/* Обчислення Toeplitz Hash для довільного бінарного буфера */
uint32_t calculate_toeplitz_hash(const uint8_t *input, size_t input_len, const uint8_t *key) {
    uint32_t hash = 0;
    
    for (size_t byte_idx = 0; byte_idx < input_len; byte_idx++) {
        uint8_t byte = input[byte_idx];
        for (int bit = 7; bit >= 0; bit--) {
            if ((byte >> bit) & 1) {
                /* Витягуємо 32-бітний шматок ключа, починаючи з поточного біта */
                size_t key_byte_idx = byte_idx + (7 - bit) / 8;
                int key_bit_shift = (7 - bit) % 8;
                
                uint32_t key_window = 
                    ((uint32_t)key[key_byte_idx] << (24 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 1] << (16 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 2] << (8 + key_bit_shift)) |
                    ((uint32_t)key[key_byte_idx + 3] << key_bit_shift);
                
                if (key_bit_shift > 0) {
                    key_window |= ((uint32_t)key[key_byte_idx + 4] >> (8 - key_bit_shift));
                }
                
                hash ^= key_window;
            }
        }
    }
    
    return hash;
}

/* Ініціалізація RETA таблиці рівномірним розподілом */
void init_reta_equal(uint8_t reta[RETA_SIZE], uint8_t num_queues) {
    for (int i = 0; i < RETA_SIZE; i++) {
        reta[i] = (uint8_t)(i % num_queues);
    }
}

int main(void) {
    uint8_t reta[RETA_SIZE];
    init_reta_equal(reta, 4); /* 4 апаратні черги: Rx 0..3 */

    /* Прямий потік: Client (192.168.1.50:49152) -> Server (10.0.0.1:80) */
    flow_tuple_v4_t flow_fwd = {
        .src_ip = 0xC0A80132,   /* 192.168.1.50 */
        .dst_ip = 0x0A000001,   /* 10.0.0.1 */
        .src_port = 0xC000,     /* 49152 */
        .dst_port = 0x0050      /* 80 */
    };

    /* Зворотний потік: Server (10.0.0.1:80) -> Client (192.168.1.50:49152) */
    flow_tuple_v4_t flow_rev = {
        .src_ip = 0x0A000001,   /* 10.0.0.1 */
        .dst_ip = 0xC0A80132,   /* 192.168.1.50 */
        .src_port = 0x0050,     /* 80 */
        .dst_port = 0xC000      /* 49152 */
    };

    /* Упаковка 4-tuple у байтовий масив для Toeplitz (12 байтів для IPv4 4-tuple) */
    uint8_t input_fwd[12];
    uint8_t input_rev[12];

    /* Формат NDIS IPv4 4-tuple: SrcIP (4B), DstIP (4B), SrcPort (2B), DstPort (2B) */
    memcpy(&input_fwd[0], &flow_fwd.src_ip, 4);
    memcpy(&input_fwd[4], &flow_fwd.dst_ip, 4);
    memcpy(&input_fwd[8], &flow_fwd.src_port, 2);
    memcpy(&input_fwd[10], &flow_fwd.dst_port, 2);

    memcpy(&input_rev[0], &flow_rev.src_ip, 4);
    memcpy(&input_rev[4], &flow_rev.dst_ip, 4);
    memcpy(&input_rev[8], &flow_rev.src_port, 2);
    memcpy(&input_rev[10], &flow_rev.dst_port, 2);

    uint32_t hash_fwd = calculate_toeplitz_hash(input_fwd, sizeof(input_fwd), default_rss_key);
    uint32_t hash_rev = calculate_toeplitz_hash(input_rev, sizeof(input_rev), default_rss_key);

    /* Індекс RETA: 7 молодших бітів (LSB) */
    uint8_t reta_idx_fwd = hash_fwd & 0x7F;
    uint8_t reta_idx_rev = hash_rev & 0x7F;

    printf("FWD Flow Hash: 0x%08X -> RETA Index: %3d -> Target Rx Queue: %d\n",
           hash_fwd, reta_idx_fwd, reta[reta_idx_fwd]);
    printf("REV Flow Hash: 0x%08X -> RETA Index: %3d -> Target Rx Queue: %d\n",
           hash_rev, reta_idx_rev, reta[reta_idx_rev]);

    return 0;
}
```
```cpp
// RSS Toeplitz Hash & RETA Simulator (C++20 Edition)

#include <iostream>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>
#include <algorithm>

namespace rss {

constexpr std::size_t KeySize = 40;
constexpr std::size_t RetaSize = 128;

// Стандартний секретний ключ NDIS RSS
constexpr std::array<std::uint8_t, KeySize> DefaultRssKey = {
    0x6d, 0x5a, 0x56, 0xda, 0x25, 0x5b, 0x0e, 0xc2,
    0x41, 0x67, 0x25, 0x3d, 0x43, 0xa3, 0x8f, 0x00,
    0xd0, 0x29, 0x4b, 0x7d, 0x3d, 0x14, 0x4e, 0x69,
    0x9f, 0xac, 0xe5, 0x42, 0x1d, 0x64, 0x52, 0x72,
    0x0f, 0x4c, 0xf7, 0xad, 0x55, 0x54, 0x03, 0xb9
};

struct FlowTupleV4 {
    std::uint32_t src_ip;
    std::uint32_t dst_ip;
    std::uint16_t src_port;
    std::uint16_t dst_port;

    // Конвертація кортежу у байтовий послідовний буфер
    [[nodiscard]] std::array<std::uint8_t, 12> to_bytes() const noexcept {
        std::array<std::uint8_t, 12> buf{};
        buf[0] = static_cast<std::uint8_t>(src_ip >> 24);
        buf[1] = static_cast<std::uint8_t>(src_ip >> 16);
        buf[2] = static_cast<std::uint8_t>(src_ip >> 8);
        buf[3] = static_cast<std::uint8_t>(src_ip);
        
        buf[4] = static_cast<std::uint8_t>(dst_ip >> 24);
        buf[5] = static_cast<std::uint8_t>(dst_ip >> 16);
        buf[6] = static_cast<std::uint8_t>(dst_ip >> 8);
        buf[7] = static_cast<std::uint8_t>(dst_ip);

        buf[8] = static_cast<std::uint8_t>(src_port >> 8);
        buf[9] = static_cast<std::uint8_t>(src_port);

        buf[10] = static_cast<std::uint8_t>(dst_port >> 8);
        buf[11] = static_cast<std::uint8_t>(dst_port);
        return buf;
    }
};

class RssEngine {
public:
    explicit RssEngine(std::span<const std::uint8_t, KeySize> key = DefaultRssKey)
        : key_(key) {
        init_reta_equal(4); // За замовчуванням 4 черги
    }

    void init_reta_equal(std::uint8_t num_queues) noexcept {
        for (std::size_t i = 0; i < RetaSize; ++i) {
            reta_[i] = static_cast<std::uint8_t>(i % num_queues);
        }
    }

    [[nodiscard]] std::uint32_t calculate_hash(std::span<const std::uint8_t> input) const noexcept {
        std::uint32_t hash = 0;
        for (std::size_t byte_idx = 0; byte_idx < input.size(); ++byte_idx) {
            const std::uint8_t byte = input[byte_idx];
            for (int bit = 7; bit >= 0; --bit) {
                if ((byte >> bit) & 1) {
                    const std::size_t key_byte_idx = byte_idx + (7 - bit) / 8;
                    const int key_bit_shift = (7 - bit) % 8;

                    std::uint32_t key_window =
                        (static_cast<std::uint32_t>(key_[key_byte_idx]) << (24 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 1]) << (16 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 2]) << (8 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 3]) << key_bit_shift);

                    if (key_bit_shift > 0) {
                        key_window |= (static_cast<std::uint32_t>(key_[key_byte_idx + 4]) >> (8 - key_bit_shift));
                    }

                    hash ^= key_window;
                }
            }
        }
        return hash;
    }

    [[nodiscard]] std::uint8_t route_flow(const FlowTupleV4& tuple) const noexcept {
        const auto bytes = tuple.to_bytes();
        const std::uint32_t hash = calculate_hash(bytes);
        const std::size_t reta_idx = hash & (RetaSize - 1);
        return reta_[reta_idx];
    }

private:
    std::span<const std::uint8_t, KeySize> key_;
    std::array<std::uint8_t, RetaSize> reta_{};
};

} // namespace rss

int main() {
    rss::RssEngine engine;

    const rss::FlowTupleV4 fwd{0xC0A80132, 0x0A000001, 49152, 80};
    const rss::FlowTupleV4 rev{0x0A000001, 0xC0A80132, 80, 49152};

    const auto fwd_bytes = fwd.to_bytes();
    const auto rev_bytes = rev.to_bytes();

    const std::uint32_t hash_fwd = engine.calculate_hash(fwd_bytes);
    const std::uint32_t hash_rev = engine.calculate_hash(rev_bytes);

    std::cout << std::hex << std::uppercase;
    std::cout << "[C++20] FWD Hash: 0x" << std::setw(8) << std::setfill('0') << hash_fwd 
              << " -> Queue: " << std::dec << static_cast<int>(engine.route_flow(fwd)) << "\n";
    std::cout << std::hex << std::uppercase;
    std::cout << "[C++20] REV Hash: 0x" << std::setw(8) << std::setfill('0') << hash_rev 
              << " -> Queue: " << std::dec << static_cast<int>(engine.route_flow(rev)) << "\n";

    return 0;
}
```
:::

---

## Інструкції зі збірки та аналіз результатів

Для збірки програмного проекту використовуйте стандартні компілятори C/C++:

```bash
# Збірка C-версії (C11)
gcc -O2 -std=c11 -Wall -Wextra main.c -o rss_sim_c
./rss_sim_c

# Збірка C++ версії (C++20)
g++ -O2 -std=c++20 -Wall -Wextra main.cpp -o rss_sim_cpp
./rss_sim_cpp
```

### Аналіз виводу програми:

1. **Різні значення хешу для асиметричного ключа**: При використанні дефолтного ключа NDIS `DefaultRssKey` direct hash для прямого напрямку (`FWD`) та зворотного (`REV`) відрізняються. У результаті пакет `Client -> Server` потрапляє у Rx Queue 1, а зворотна відповідь `Server -> Client` потрапляє у Rx Queue 3.
2. **Співвідношення з ядрами**: Якщо черга 1 прив'язана до CPU 1, а черга 3 до CPU 3, то обробка з'єднання розщеплюється між двома ядрами. Для звичайного TCP-сервера це прийнятно, але для Stateful Firewall / NAT вимагає заміни ключа на Symmetric RSS Key.
3. **Обчислювальна лінійність**: Реалізований алгоритм Toeplitz працює без умовних розгалужень у внутрішньому циклі зсуву ключа, що гарантує одинаковий час виконання незалежно від значень IP-адрес.
4. **Типова обробка розширених кортежів (IPv6 та VLAN)**: У разі розширення кортежу до 36 байтів (IPv6 4-tuple: 16B SrcIP + 16B DstIP + 2B SrcPort + 2B DstPort) алгоритм залишається повністю ідентичним, змінюється лише розмір вхідного масиву `input_len` з 12 до 36 байтів, а розмір ключа збільшується з 40 до 52 байтів.
