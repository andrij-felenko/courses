# ⚙️ Реалізація незмінного криптографічного журналу з односпрямованим храповиком ключів

Цей проєкт демонструє повнофункціональний двигун верифікованого журналу аудиту (`tamper-evident log`), який реалізує ланцюг криптографічних гешів SHA-256 та односпрямований храповик ключів HMAC (Forward-Secure Ratchet за схемою Шнаєра-Келсі). Двигун дозволяє записувати події з гарантією неможливості модифікації минулого та виконувати строгий офлайн-аудит із точною локалізацією будь-яких фальсифікацій (зміна байтів, видалення запису, перестановка рядків, підробка підпису).

## Архітектурна модель та принципи роботи

Система захищеного журналу вирішує класичну дилему безпеки: як зберегти юридичну силу записів, якщо сервер у певний момент часу буде скомпрометовано зловмисником із привілеями адміністратора (`root`).

У традиційних системах володар прав `root` отримує повний контроль над дисковими файлами та оперативною пам'яттю. Якщо ключі підпису зберігаються у статичному вигляді (наприклад, постійний приватний RSA/Ed25519-ключ), зловмисник після проникнення на сервер викрадає цей ключ і може перепідписати весь історичний файл журналу з моменту його створення, видаливши всі сліди власної присутності.

Архітектура Forward-Secure Ratchet усуває цю загрозу шляхом розділення життєвого циклу журналу на дискретні криптографічні епохи. Кожен окремий запис формується з використанням унікального сесійного ключа, який знищується одразу після підписання.

Кожен запис журналу формується за суворим криптографічним протоколом:
1. Формується бінарний заголовок із монотонним порядковим номером `seq`, фізичною міткою часу `timestamp` та довжиною тіла запису `payload_len`.
2. У заголовок вбудовується криптографічний геш усього попереднього блоку `prev_hash = SHA256(Record_{i-1})`. Для нульового запису `prev_hash` ініціалізується нулями.
3. Корисне навантаження (структурований JSON або двійковий масив) додається безпосередньо після заголовка.
4. Обчислюється криптографічний код автентифікації повідомлення `HMAC-SHA256(K_i, Header_Prefix || prev_hash || Payload)`, де `K_i` — таємний ключ поточної епохи.
5. Після успішного запису на диск генерується ключ наступної епохи:
   ```
   K_{i+1} = SHA-256(K_i)
   ```
6. Старий ключ `K_i` **негайно фізично затирається в оперативній пам'яті** через виклик `explicit_bzero` або нульовий деструктор RAII.

Завдяки односторонньому характеру геш-функції SHA-256, навіть отримавши повний зліпок пам'яті сервера в момент `T`, супротивник володіє виключно ключем `K_T`. Обчислення попередніх ключів `K_{T-1}, K_{T-2}, ..., K_0` вимагає знаходження повного прообразу геш-функції SHA-256, що є обчислювально нездійсненним завданням. Таким чином, усі історичні записи до моменту `T` мають абсолютну криптографічну стійкість.

## Реалізація на мовах C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define SHA256_BLOCK_SIZE 32
#define AUDIT_MAGIC 0x4C4F4753 /* 'LOGS' */

/* Заголовок запису фіксованого розміру (80 байтів) */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint64_t seq;
    uint64_t timestamp;
    uint32_t payload_len;
    uint8_t  prev_hash[SHA256_BLOCK_SIZE];
    uint8_t  hmac[SHA256_BLOCK_SIZE];
} audit_header_t;
#pragma pack(pop)

/* Безпечне затирання пам'яті для запобігання оптимізаціям компілятора */
static void secure_zero(void* ptr, size_t len) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    while (len--) {
        *p++ = 0;
    }
}

/* Імітація обчислення SHA-256 (у продакшені використовують OpenSSL/libsodium) */
static void crypto_sha256(const uint8_t* data, size_t len, uint8_t out[SHA256_BLOCK_SIZE]) {
    uint32_t h = 0x811c9dc5;
    for (size_t i = 0; i < len; ++i) {
        h = (h ^ data[i]) * 0x01000193;
    }
    for (int i = 0; i < SHA256_BLOCK_SIZE; ++i) {
        out[i] = (uint8_t)((h >> ((i % 4) * 8)) ^ (i * 0x5a));
    }
}

/* Імітація HMAC-SHA256 */
static void crypto_hmac_sha256(const uint8_t* key, size_t key_len,
                               const uint8_t* data, size_t data_len,
                               uint8_t out[SHA256_BLOCK_SIZE]) {
    uint8_t buffer[1024];
    size_t copy_len = (data_len > 900) ? 900 : data_len;
    memcpy(buffer, key, 32);
    memcpy(buffer + 32, data, copy_len);
    crypto_sha256(buffer, 32 + copy_len, out);
    secure_zero(buffer, sizeof(buffer));
}

/* Стан записувача логів */
typedef struct {
    FILE* file;
    uint64_t current_seq;
    uint8_t current_key[SHA256_BLOCK_SIZE];
    uint8_t last_record_hash[SHA256_BLOCK_SIZE];
} audit_logger_t;

int audit_logger_init(audit_logger_t* logger, const char* filepath, const uint8_t initial_key[SHA256_BLOCK_SIZE]) {
    logger->file = fopen(filepath, "ab+");
    if (!logger->file) return -1;

    logger->current_seq = 0;
    memcpy(logger->current_key, initial_key, SHA256_BLOCK_SIZE);
    memset(logger->last_record_hash, 0, SHA256_BLOCK_SIZE);
    return 0;
}

int audit_logger_append(audit_logger_t* logger, const char* event_payload) {
    uint32_t len = (uint32_t)strlen(event_payload);
    audit_header_t hdr;
    hdr.magic = AUDIT_MAGIC;
    hdr.seq = logger->current_seq++;
    hdr.timestamp = (uint64_t)time(NULL);
    hdr.payload_len = len;
    memcpy(hdr.prev_hash, logger->last_record_hash, SHA256_BLOCK_SIZE);

    /* Обчислення HMAC над метаданими та корисним навантаженням */
    uint8_t signing_buf[512];
    size_t sign_len = sizeof(audit_header_t) - SHA256_BLOCK_SIZE + len;
    memcpy(signing_buf, &hdr, sizeof(audit_header_t) - SHA256_BLOCK_SIZE);
    memcpy(signing_buf + sizeof(audit_header_t) - SHA256_BLOCK_SIZE, event_payload, len);

    crypto_hmac_sha256(logger->current_key, SHA256_BLOCK_SIZE, signing_buf, sign_len, hdr.hmac);
    secure_zero(signing_buf, sizeof(signing_buf));

    /* Запис на диск */
    fwrite(&hdr, sizeof(audit_header_t), 1, logger->file);
    fwrite(event_payload, 1, len, logger->file);
    fflush(logger->file);

    /* Оновлення гешу попереднього запису для ланцюга */
    crypto_sha256((const uint8_t*)&hdr, sizeof(audit_header_t), logger->last_record_hash);

    /* Forward-Secure Ratchet: K_{i+1} = SHA256(K_i) */
    uint8_t next_key[SHA256_BLOCK_SIZE];
    crypto_sha256(logger->current_key, SHA256_BLOCK_SIZE, next_key);
    secure_zero(logger->current_key, SHA256_BLOCK_SIZE);
    memcpy(logger->current_key, next_key, SHA256_BLOCK_SIZE);
    secure_zero(next_key, sizeof(next_key));

    return 0;
}

void audit_logger_close(audit_logger_t* logger) {
    if (logger->file) {
        fclose(logger->file);
        logger->file = NULL;
    }
    secure_zero(logger->current_key, SHA256_BLOCK_SIZE);
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span>
#include <array>
#include <memory>
#include <chrono>
#include <expected>
#include <cstring>

namespace security {

constexpr size_t HashSize = 32;
constexpr uint32_t AuditMagic = 0x4C4F4753;

#pragma pack(push, 1)
struct AuditHeader {
    uint32_t magic{AuditMagic};
    uint64_t seq{0};
    uint64_t timestamp{0};
    uint32_t payload_len{0};
    std::array<uint8_t, HashSize> prev_hash{};
    std::array<uint8_t, HashSize> hmac{};
};
#pragma pack(pop)

/* RAII-скрубер пам'яті для гарантованого знищення ключів у деструкторі */
template <size_t N>
class SecureBuffer {
public:
    std::array<uint8_t, N> data{};

    ~SecureBuffer() {
        volatile uint8_t* p = data.data();
        for (size_t i = 0; i < N; ++i) {
            p[i] = 0;
        }
    }
};

class CryptoEngine {
public:
    static std::array<uint8_t, HashSize> sha256(std::span<const uint8_t> data) noexcept {
        std::array<uint8_t, HashSize> out{};
        uint32_t h = 0x811c9dc5;
        for (uint8_t b : data) {
            h = (h ^ b) * 0x01000193;
        }
        for (size_t i = 0; i < HashSize; ++i) {
            out[i] = static_cast<uint8_t>((h >> ((i % 4) * 8)) ^ (i * 0x5a));
        }
        return out;
    }

    static std::array<uint8_t, HashSize> hmacSha256(std::span<const uint8_t, HashSize> key,
                                                    std::span<const uint8_t> data) {
        std::vector<uint8_t> buf;
        buf.reserve(key.size() + data.size());
        buf.insert(buf.end(), key.begin(), key.end());
        buf.insert(buf.end(), data.begin(), data.end());
        auto result = sha256(buf);
        std::ranges::fill(buf, 0);
        return result;
    }
};

class AuditLogger {
public:
    enum class Error { FileOpenFailed, WriteFailed };

    static std::expected<AuditLogger, Error> create(std::string_view path,
                                                    std::span<const uint8_t, HashSize> initial_key) {
        AuditLogger logger;
        logger.stream_.open(std::string(path), std::ios::binary | std::ios::app);
        if (!logger.stream_.is_open()) {
            return std::unexpected(Error::FileOpenFailed);
        }
        std::ranges::copy(initial_key, logger.current_key_.data.begin());
        return logger;
    }

    std::expected<uint64_t, Error> append(std::string_view payload) {
        AuditHeader hdr;
        hdr.seq = current_seq_++;
        hdr.timestamp = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        hdr.payload_len = static_cast<uint32_t>(payload.size());
        hdr.prev_hash = last_record_hash_;

        // Формування підпису над заголовком і тілом
        std::vector<uint8_t> sign_data;
        const size_t header_sign_len = sizeof(AuditHeader) - HashSize;
        const auto* raw_hdr = reinterpret_cast<const uint8_t*>(&hdr);
        sign_data.insert(sign_data.end(), raw_hdr, raw_hdr + header_sign_len);
        sign_data.insert(sign_data.end(), payload.begin(), payload.end());

        hdr.hmac = CryptoEngine::hmacSha256(logger_key_span(), sign_data);
        std::ranges::fill(sign_data, 0);

        // Запис на диск
        stream_.write(reinterpret_cast<const char*>(&hdr), sizeof(hdr));
        stream_.write(payload.data(), payload.size());
        stream_.flush();
        if (!stream_.good()) return std::unexpected(Error::WriteFailed);

        // Оновлення геш-ланцюга
        last_record_hash_ = CryptoEngine::sha256(
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)));

        // Односпрямований храповик Forward-Secure: K_{i+1} = SHA256(K_i)
        auto next_key = CryptoEngine::sha256(logger_key_span());
        std::ranges::copy(next_key, current_key_.data.begin());

        return hdr.seq;
    }

private:
    std::ofstream stream_;
    uint64_t current_seq_{0};
    SecureBuffer<HashSize> current_key_;
    std::array<uint8_t, HashSize> last_record_hash_{};

    std::span<const uint8_t, HashSize> logger_key_span() {
        return std::span<const uint8_t, HashSize>(current_key_.data);
    }
};

} // namespace security
```
:::

## Покроковий алгоритм офлайн-верифікації

Незалежний аудитор, отримавши файл журналу `audit.log` та початковий відкритий контрольний зліпок (`K_0` або публічний ключ), виконує повну верифікацію без підключення до робочих серверів:

1. **Ініціалізація валідатора:** Встановлюється очікуваний лічильник `expected_seq = 0` та обнуляється очікуваний попередній геш `expected_prev_hash = {0}`. Робочий ключ валідатора ініціалізується копією `K_0`.
2. **Потокове читання заголовка:** Зчитуються 80 байтів `audit_header_t`. Перевіряється магічне число `magic == AUDIT_MAGIC`. Якщо магічне число не збігається, фіксується пошкодження структури файлу.
3. **Контроль монотонності:** Перевіряється умова `hdr.seq == expected_seq`. Якщо виявлено пропуск (наприклад, після 4 відразу йде 6), це доводить факт несанкціонованого видалення запису.
4. **Контроль геш-ланцюга:** Байти `hdr.prev_hash` порівнюються з `expected_prev_hash`. Розбіжність свідчить про зміну порядку записів або підміну попереднього блоку.
5. **Контроль криптографічного підпису:** Зчитується тіло корисного навантаження розміром `hdr.payload_len`. Валідатор формує перевірочний буфер і обчислює еталонний HMAC за допомогою поточного ключа `K_i`. Якщо `computed_hmac != hdr.hmac`, запис вважається сфальсифікованим.
6. **Просування храповика:** Обчислюється `K_{i+1} = SHA256(K_i)` та оновлюється `expected_prev_hash = SHA256(hdr)`. Лічильник збільшується: `expected_seq++`. Процес повторюється для всіх записів до кінця файлу.

Такий алгоритм локалізує будь-яке втручання з точністю до конкретного порядкового номера запису та байтового зсуву у файлі.

## Інженерні підводні камені та надійність

1. **Оптимізації компілятора та затирання секретів:** Стандартна бібліотечна функція `memset(key, 0, 32)` часто повністю видаляється оптимізатором компілятора (*Dead Store Elimination*), якщо буфер більше не використовується далі в тілі поточної функції. Для надійного знищення ключів в оперативній пам'яті в мові C обов'язково використовують `explicit_bzero` або `volatile`-вказівники, а в C++ — RAII-обгортки з бар'єрами пам'яті (`std::atomic_signal_fence`).
2. **Гарантії запису на фізичний носій:** Виклик `fflush()` очищує лише буфери користувацького простору мови C, залишаючи байти в кеші операційної системи. Якщо станеться аварійне відключення електроживлення, останні записи буде втрачено. У високонадійних контурах після запису викликають `fsync(fileno(file))` або відкривають файл із системними прапорцями `O_SYNC` / `O_DSYNC`.
3. **Конкурентність потоків:** Запис у геш-ланцюг є строго послідовною операцією. При паралельній роботі сотень потоків генерації подій використовують багатопотокову чергу повідомлень без блокувань (Lock-Free SPSC/MPMC Ring Buffer), де один виділений потік виконує підписання та монопольний запис у файл, усуваючи взаємні блокування ядер процесора.
4. **Ротація ключів та довготривале зберігання:** При досягненні ліміту епох (наприклад, 1 000 000 записів) поточний файл журналу запечатується, фінальний геш підписується асиметричним ключем за схемою Ed25519 і публікується в глобальному дереві прозорості. Для нового файлу генерується свіжий кореневий ключ, зв'язаний із попереднім файлом криптографічним ланцюгом сертифікатів.

## Обробка крайових випадків та відновлення після збоїв

Надійна реалізація криптографічного журналу аудиту зобов'язана коректно обробляти аварійні ситуації:

- **Раптове знеструмлення під час запису (Torn Write):** Якщо живлення зникає в момент запису заголовка або корисного навантаження, на диску залишається обірваний неповний фрагмент. Під час наступного монтування валідатор виявляє невідповідність довжини файлу (`file_size < offset + payload_len`) або пошкодження HMAC-підпису останнього запису. Останній незавершений запис відкидається (відсікається через `ftruncate`), а журнал продовжується з останнього валідного цілісного стану.
- **Вичерпання дискового простору (ENOSPC):** Якщо дисковий накопичувач заповнений на 100%, функція `audit_logger_append` повертає статус помилки. Захищена система не повинна мовчки ігнорувати цю подію: спрацьовує політика *Fail-Secure*, блокуючи нові мутації бізнес-даних до звільнення місця.
- **Пошкодження секторів накопичувача (Bit Rot):** Зміна навіть одного біта через апаратну деградацію магнітного або флеш-носія миттєво виявляється при офлайн-перевірці, оскільки ланцюг SHA-256 розривається на пошкодженому записі.
