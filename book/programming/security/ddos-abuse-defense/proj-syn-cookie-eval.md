# ⚙️ Практична реалізація та валідація TCP SYN Cookies

У класичному мережевому стеку при отриманні вхідного пакета TCP `SYN` операційна система виділяє в пам'яті структуру `struct request_sock` (напіввідкритий сокет) та вносить її до таблиці беклогу прослуховуваного порту. За умов масованої атаки підробленими пакетами (`SYN Flood`) ця таблиця переповнюється, блокуючи легітимні з'єднання.

Завдання полягає у створенні високопродуктивного системного модуля генерації та верифікації безстанкових криптографічних кук (**SYN Cookies** за стандартом RFC 4987). Модуль повинен запаковувати всі критичні параметри з'єднання безпосередньо в 32-бітний початковий порядковий номер відповіді сервера (`ISN`), не виділяючи жодного байта оперативної пам'яті до отримання валідного завершального пакета `ACK`.

---

## 1. Архітектурні вимоги та вибір криптографічного алгоритму

При проектуванні генератора SYN Cookies у ядрі або у вхідному L4-фільтрі (наприклад, у середовищі XDP чи DPDK) інженер стикається з жорсткими обмеженнями бюджету процесорного часу:

1. **Бюджет тактів CPU:** При швидкості вхідного потоку 10–20 мільйонів пакетів на секунду час обробки одного пакета на одному процесорному ядрі не повинен перевищувати **30–50 наносекунд** (близько 100–150 тактів сучасного CPU).
2. **Невідповідність важких гешів:** Класичні криптографічні функції (SHA-256, SHA-3) вимагають від 200 до 600 тактів на блок, що робить їх надто повільними для захисту від гігабітних атак на рівні драйвера.
3. **Захист від атак колізій та відновлення ключа:** Прості некриптографічні хеші (CRC32, MurmurHash, Jenkins) легко піддаються зворотному інжинірингу: зловмисник може відновити секретний ключ і генерувати підроблені валідні ACK-пакети.

Оптимальним вибором для ядра Linux є алгоритм **SipHash-2-4** (або його 32-бітна версія **HalfSipHash**). Він забезпечує криптографічну стійкість до підбору псевдовипадкових функцій (PRF), виконується константний час (захист від атак за часом, *Timing Attacks*) і вимагає лише близько 20–35 тактів процесора на обчислення 26-бітного MAC.

---

## 2. Формат пакування 32-бітного ISN

32-бітне поле порядкового номера відповіді `SYN-ACK` ділиться на три функціональні бітові зони:

```
 31        29 28        26 25                                             0
┌────────────┬────────────┬─────────────────────────────────────────────────┐
│ Час t (3b) │ MSS m (3b) │           Усічений HMAC / Хеш s (26 бітів)       │
└────────────┴────────────┴─────────────────────────────────────────────────┘
```

1. **Мітка часу `t` (біти 31..29, 3 біти):** Повільний лічильник часу з дискретністю 64 секунди: `t = (now_sec >> 6) & 0x07`. Повний цикл з 8 значень (`0..7`) триває `8 × 64 = 512` секунд. Під час перевірки допускається збіг з поточним вікном `t` або попереднім вікном `(t - 1) & 0x07` (допустимий час затримки клієнта — до 64–128 с).
2. **Індекс розміру максимального сегмента `m` (біти 28..26, 3 біти):** Кодує один із восьми стандартних розмірів TCP MSS із фіксованої таблиці значень (наприклад: 536, 1200, 1400, 1440, 1452, 1460, 8960, 9000).
3. **Криптографічний MAC `s` (біти 25..0, 26 бітів):** Результат обчислення криптографічної геш-функції від 4-tuple IP/порту, клієнтського `client_isn`, часового індексу `t` та локального секретного ключа сервера: `Hash(saddr, daddr, sport, dport, client_isn, t, secret) & 0x03FFFFFF`.

---

## 3. Програмна реалізація генератора та валідатора

Нижче наведено повністю робочу системну реалізацію генерації та перевірки SYN Cookies мовами C та C++ з використанням оптимізованого раунду SipHash та безпечної роботи з пам'яттю.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SYNCOOKIE_TIME_SHIFT 6          /* Дискретність вікна: 2^6 = 64 секунди */
#define SYNCOOKIE_TIME_MASK  0x07       /* 3 біти для мітки часу (0..7) */
#define SYNCOOKIE_MSS_MASK   0x07       /* 3 біти для індексу MSS (0..7) */
#define SYNCOOKIE_HASH_MASK  0x03FFFFFF /* 26 бітів для криптографічного MAC */

/* Стандартна таблиця значень TCP MSS для 3-бітного індексу */
static const uint16_t MSS_TABLE[8] = {
    536,   /* Мінімальний IPv4 MSS */
    1200,  /* Безпечний розмір для тунелів */
    1400,  /* Стандартний GRE/IPsec */
    1440,  /* PPPoE / Cloudflare Edge */
    1452,  /* Стандартний PPPoE DSL */
    1460,  /* Типовий Ethernet IPv4 (1500 - 40) */
    8960,  /* Jumbo Frame без заголовків */
    9000   /* Максимальний Ethernet Jumbo Frame */
};

/* Раунд змішування SipHash для швидкого обчислення 26-бітного MAC */
static uint32_t siphash_syn(uint32_t saddr, uint32_t daddr,
                            uint16_t sport, uint16_t dport,
                            uint32_t client_isn, uint32_t time_idx,
                            const uint8_t secret[16]) {
    uint64_t k0, k1;
    memcpy(&k0, secret, 8);
    memcpy(&k1, secret + 8, 8);

    uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
    uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
    uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
    uint64_t v3 = 0x7465646279746573ULL ^ k1;

    uint64_t m0 = ((uint64_t)saddr << 32) | daddr;
    uint64_t m1 = ((uint64_t)sport << 48) | ((uint64_t)dport << 32) | (client_isn ^ time_idx);

    /* Раунд змішування для m0 */
    v3 ^= m0;
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;
    v0 += v3; v3 = (v3 << 21) | (v3 >> (64 - 21)); v3 ^= v0;
    v2 += v1; v1 = (v1 << 17) | (v1 >> (64 - 17)); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
    v0 ^= m0;

    /* Раунд змішування для m1 */
    v3 ^= m1;
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;
    v0 += v3; v3 = (v3 << 21) | (v3 >> (64 - 21)); v3 ^= v0;
    v2 += v1; v1 = (v1 << 17) | (v1 >> (64 - 17)); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
    v0 ^= m1;

    v2 ^= 0xff;
    /* Фіналізація */
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;

    return (uint32_t)((v0 ^ v1 ^ v2 ^ v3) & SYNCOOKIE_HASH_MASK);
}

/* Пошук найближчого індексу MSS, який не перевищує запитаний клієнтом */
static uint32_t select_mss_index(uint16_t client_mss) {
    uint32_t best_idx = 0;
    for (uint32_t i = 0; i < 8; ++i) {
        if (MSS_TABLE[i] <= client_mss) {
            best_idx = i;
        } else {
            break;
        }
    }
    return best_idx;
}

/* Генерація 32-бітного ISN для відповіді SYN-ACK */
uint32_t generate_syn_cookie(uint32_t saddr, uint32_t daddr,
                             uint16_t sport, uint16_t dport,
                             uint32_t client_isn, uint16_t client_mss,
                             uint32_t now_sec, const uint8_t secret[16]) {
    uint32_t time_idx = (now_sec >> SYNCOOKIE_TIME_SHIFT) & SYNCOOKIE_TIME_MASK;
    uint32_t mss_idx = select_mss_index(client_mss);
    uint32_t hash_val = siphash_syn(saddr, daddr, sport, dport, client_isn, time_idx, secret);

    return (time_idx << 29) | (mss_idx << 26) | hash_val;
}

/* Перевірка куки у вхідному пакеті ACK: ack_seq = cookie + 1 */
bool verify_syn_cookie(uint32_t cookie, uint32_t saddr, uint32_t daddr,
                       uint16_t sport, uint16_t dport,
                       uint32_t client_isn, uint32_t now_sec,
                       const uint8_t secret[16], uint16_t *recovered_mss) {
    uint32_t cookie_time = (cookie >> 29) & SYNCOOKIE_TIME_MASK;
    uint32_t cookie_mss_idx = (cookie >> 26) & SYNCOOKIE_MSS_MASK;
    uint32_t cookie_hash = cookie & SYNCOOKIE_HASH_MASK;

    uint32_t current_time = (now_sec >> SYNCOOKIE_TIME_SHIFT) & SYNCOOKIE_TIME_MASK;

    /* Дозволяємо поточне часове вікно або попереднє (вікно допустимості ~64-128 с) */
    uint32_t diff = (current_time - cookie_time) & SYNCOOKIE_TIME_MASK;
    if (diff > 1) {
        return false; /* Кука застаріла або з майбутнього */
    }

    uint32_t expected_hash = siphash_syn(saddr, daddr, sport, dport, client_isn, cookie_time, secret);
    if (expected_hash != cookie_hash) {
        return false; /* Невалідний криптографічний MAC */
    }

    if (recovered_mss) {
        *recovered_mss = MSS_TABLE[cookie_mss_idx];
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>
#include <string_view>
#include <algorithm>
#include <span>

class SynCookieEngine {
public:
    static constexpr uint32_t TimeShift = 6;          // 64 секунди на одне вікно
    static constexpr uint32_t TimeMask  = 0x07;       // 3 біти для часового індексу
    static constexpr uint32_t MssMask   = 0x07;       // 3 біти для індексу MSS
    static constexpr uint32_t HashMask  = 0x03FFFFFF; // 26 бітів для криптографічного MAC

    static constexpr std::array<uint16_t, 8> MssTable = {
        536, 1200, 1400, 1440, 1452, 1460, 8960, 9000
    };

    struct Endpoints {
        uint32_t src_ip;
        uint32_t dst_ip;
        uint16_t src_port;
        uint16_t dst_port;
        uint32_t client_isn;
    };

    explicit SynCookieEngine(std::span<const uint8_t, 16> secret_key) noexcept {
        std::copy(secret_key.begin(), secret_key.end(), secret_.begin());
    }

    [[nodiscard]] uint32_t generate(const Endpoints& ep, uint16_t client_mss, uint32_t now_sec) const noexcept {
        const uint32_t time_idx = (now_sec >> TimeShift) & TimeMask;
        const uint32_t mss_idx = select_mss_index(client_mss);
        const uint32_t mac = compute_mac(ep, time_idx);

        return (time_idx << 29) | (mss_idx << 26) | mac;
    }

    [[nodiscard]] std::optional<uint16_t> verify(uint32_t cookie, const Endpoints& ep, uint32_t now_sec) const noexcept {
        const uint32_t cookie_time = (cookie >> 29) & TimeMask;
        const uint32_t cookie_mss_idx = (cookie >> 26) & MssMask;
        const uint32_t cookie_mac = cookie & HashMask;

        const uint32_t current_time = (now_sec >> TimeShift) & TimeMask;
        const uint32_t diff = (current_time - cookie_time) & TimeMask;

        // Приймаємо лише поточне та попереднє вікно (термін валідності куки 64..128 с)
        if (diff > 1) {
            return std::nullopt;
        }

        if (compute_mac(ep, cookie_time) != cookie_mac) {
            return std::nullopt;
        }

        return MssTable[cookie_mss_idx];
    }

private:
    std::array<uint8_t, 16> secret_{};

    static uint32_t select_mss_index(uint16_t client_mss) noexcept {
        uint32_t best_idx = 0;
        for (size_t i = 0; i < MssTable.size(); ++i) {
            if (MssTable[i] <= client_mss) {
                best_idx = static_cast<uint32_t>(i);
            } else {
                break;
            }
        }
        return best_idx;
    }

    [[nodiscard]] uint32_t compute_mac(const Endpoints& ep, uint32_t time_idx) const noexcept {
        uint64_t k0 = 0, k1 = 0;
        for (int i = 0; i < 8; ++i) {
            k0 |= static_cast<uint64_t>(secret_[i]) << (i * 8);
            k1 |= static_cast<uint64_t>(secret_[i + 8]) << (i * 8);
        }

        uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
        uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
        uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
        uint64_t v3 = 0x7465646279746573ULL ^ k1;

        const uint64_t m0 = (static_cast<uint64_t>(ep.src_ip) << 32) | ep.dst_ip;
        const uint64_t m1 = (static_cast<uint64_t>(ep.src_port) << 48) |
                            (static_cast<uint64_t>(ep.dst_port) << 32) |
                            (ep.client_isn ^ time_idx);

        auto round = [&](uint64_t m) {
            v3 ^= m;
            v0 += v1; v1 = (v1 << 13) | (v1 >> 51); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
            v2 += v3; v3 = (v3 << 16) | (v3 >> 48); v3 ^= v2;
            v0 += v3; v3 = (v3 << 21) | (v3 >> 43); v3 ^= v0;
            v2 += v1; v1 = (v1 << 17) | (v1 >> 47); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
            v0 ^= m;
        };

        round(m0);
        round(m1);

        v2 ^= 0xff;
        v0 += v1; v1 = (v1 << 13) | (v1 >> 51); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
        v2 += v3; v3 = (v3 << 16) | (v3 >> 48); v3 ^= v2;

        return static_cast<uint32_t>((v0 ^ v1 ^ v2 ^ v3) & HashMask);
    }
};
```
:::

---

## 4. Покрокове простеження обробки пакетів

Щоб зрозуміти життєвий цикл з'єднання під час захисту, розглянемо два сценарії поведінки модуля:

### Сценарій А: Атака підробленим SYN-пакетом (IP Spoofing)

1. На мережевий інтерфейс надходить пакет `SYN` із підробленою адресою відправника `203.0.113.50` та портом `45231`.
2. Драйвер або ядро викликає функцію `generate_syn_cookie()`.
3. Модуль обчислює часовий індекс `t = (now >> 6) & 0x07` (наприклад, `t = 3`), знаходить індекс MSS `m = 5` (1460 байтів) та генерує 26-бітний MAC `s = 0x01A3F421`.
4. Сервер формує вихідний пакет `SYN-ACK` із початковим порядковим номером `ISN = (3 << 29) | (5 << 26) | 0x01A3F421 = 0x75A3F421`.
5. Сервер відправляє пакет у мережу і **не створює жодного сокета в пам'яті**.
6. Оскільки адреса `203.0.113.50` не належить зловмиснику, фінальний пакет `ACK` ніколи не повертається. Пам'ять системи лишається на 100% вільною.

### Сценарій Б: Легітимний клієнт завершує рукостискання

1. Справжній клієнт отримує пакет `SYN-ACK` із `server_isn = 0x75A3F421`.
2. Клієнтська операційна система формує третій пакет `ACK` із полем підтвердження `ack_seq = 0x75A3F421 + 1 = 0x75A3F422`.
3. Сервер отримує пакет `ACK`, віднімає одиницю (`0x75A3F421`) і передає значення у функцію `verify_syn_cookie()`.
4. Функція витягує `cookie_time = 3`, `mss_idx = 5`, перевіряє часове відхилення `diff <= 1` та перераховує очікуваний MAC над заголовками вхідного кадру.
5. Результати збігаються: модуль повертає `true` та відновлений розмір сегмента `MSS = 1460`.
6. Тільки зараз операційна система виділяє повноцінну структуру `struct sock` і поміщає нове з'єднання в чергу виклику `accept()`.

---

## 5. Безпечна ротація секретних ключів у виробничому середовищі

Якщо секретний ключ `secret[16]` залишається незмінним протягом місяців, теоретичний зловмисник, що накопичив гігабайти пар (SYN, SYN-ACK), може спробувати відновити ключ за допомогою криптоаналізу.

Для запобігання цьому у виробничих серверах реалізують механізм ковзної ротації двох ключів:
- **`current_secret`:** Активний ключ, який використовується для генерації нових SYN Cookies та їхньої верифікації.
- **`previous_secret`:** Попередній ключ, який використовується **виключно для верифікації** вхідних ACK-пакетів протягом перехідного періоду (2–5 хвилин після ротації).

Раз на кілька годин фоновий таймер генерує новий 128-бітний випадковий масив із криптографічно стійкого генератора псевдовипадкових чисел (CSPRNG, `/dev/urandom`), переміщує старий ключ у `previous_secret` та записує новий у `current_secret`. Це гарантує безшовну ротацію без розриву з'єднань, що перебувають у процесі рукостискання.

---

## 6. Системні параметри ядра Linux та моніторинг

Керування вбудованим механізмом SYN Cookies у ядрі Linux здійснюється через підсистему `sysctl`:

```bash
# Увімкнення SYN Cookies при переповненні черги беклогу (значення 1 за замовчуванням)
sysctl -w net.ipv4.tcp_syncookies=1

# Збільшення розміру черги напіввідкритих з'єднань
sysctl -w net.ipv4.tcp_max_syn_backlog=8192

# Збільшення черги готових сокетів для функції listen()
sysctl -w net.core.somaxconn=4096
```

Перевірка активності захисту в реальному часі здійснюється за допомогою утиліти `nstat` або через читання системного файлу `/proc/net/netstat`:

```bash
# Перегляд кількості згенерованих та перевірених SYN Cookies
nstat -z TcpExtSyncookies*
# TcpExtSyncookiesSent            1452031   0.0
# TcpExtSyncookiesRecv            1449812   0.0
# TcpExtSyncookiesFailed             2219   0.0
```

Якщо лічильник `TcpExtSyncookiesFailed` зростає зі швидкістю понад 100 000 подій на секунду, це свідчить про активну атаку сліпого ACK-флуду, яку слід відсікати на рівні XDP або магістрального фаєрвола.
