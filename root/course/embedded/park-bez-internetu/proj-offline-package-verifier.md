# Парсер і верифікатор криптографічних офлайн-пакетів прошивки

Цей модуль реалізує потоковий синтаксичний аналізатор і верифікатор автономних контейнерів оновлення, який дає змогу вбудованому мікроконтролеру перевіряти автентичність, цілісність, апаратну цільову сумісність та монотонність версії прошивки без прямого підключення до сервера авторизації.

В ізольованому від мережі середовищі пристрій позбавлений можливості надіслати запит до центру сертифікації для перевірки статусу відкликання сертифікатів (CRL/OCSP) або отримання сесійного одноразового токена. Уся криптографічна інформація, необхідна для безпомилкового ухвалення рішення про прошивку, має міститися всередині самого бінарного пакета. При цьому типовий промисловий мікроконтролер має жорсткі ресурсні обмеження: обсяг оперативної пам'яті (SRAM) часто становить від 32 до 128 КБ, що робить неможливим завантаження цілого образу прошивки (розміром 512 КБ або кілька мегабайтів) у пам'ять для разового обчислення криптографічного підпису.

Обробка бінарного образу повинна відбуватися строго потоково: заголовок пакета аналізується та верифікується першим, після чого корисне навантаження зчитується фіксованими блоками (чанками), перевіряється за проміжними контрольними хешами та записується безпосередньо у неактивний банк Flash-пам'яті (Slot B).

### Модель загроз та інженерні вимоги до офлайн-пакета

Під час розробки офлайн-верифікатора розглядаються такі вектори атак та апаратних відмов:
1. **Підміна або модифікація образу на носії (англ. *tampering*):** зловмисник змінює байти виконуваного коду на USB-флешці чи SD-карті техніка. Відповідь — асиметричний цифровий підпис (Ed25519 або ECDSA P-256), що накладається закритим ключем релізу в захищеному середовищі розробника.
2. **Атака повернення до застарілої версії (англ. *rollback attack*):** нападник бере легітимний, підписаний виробником образ старої версії (наприклад, v1.0), у якій згодом було знайдено критичну вразливість переповнення буфера, і прошиває його замість поточної версії v1.3. Відповідь — апаратні монотонні лічильники версій у eFuse, які унеможливлюють запуск прошивки з версією, нижчою за встановлений апаратний поріг.
3. **Прошивка коду в несумісну плату (англ. *hardware mismatch*):** випадкова спроба залити образ від трифазного лічильника в однофазний або в плату іншої ревізії з іншим розподілом виводів GPIO. Відповідь — сувора звірка унікального `target_hw_id` у підписаному заголовку з ідентифікатором у постійній пам'яті MCU.
4. **Раптове знеструмлення під час запису:** технік випадково висмикнув флешку або зникло живлення під час програмування секторів. Відповідь — дворівнева схема розділів (Slot A / Slot B). Слот A з поточною робочою прошивкою ніколи не модифікується; якщо процес переривається на будь-якому кроці, система гарантовано продовжує виконання зі слота A.

---

### Структура бінарного контейнера офлайн-пакета (`.upkg`)

Контейнер складається з чотирьох послідовних структурних блоків:
- **Заголовок метаданих (128 байтів):** містить магічне число `UPKG`, версію формату пакування, апаратний ідентифікатор цільової платформи (`target_hw_id`), монотонний номер версії прошивки, розмір корисного навантаження, загальний SHA-256 хеш фінального образу та цифровий підпис Ed25519.
- **Таблиця хешів чанків:** лінійний масив 32-байтних хешів SHA-256 (по одному запису на кожен сектор розміром 4096 байтів). Така організація реалізує принцип дерева Меркла: знаючи підписаний заголовок із підсумковим хешем таблиці, контролер перевіряє кожен 4-кілобайтний блок окремо перед стиранням і записом відповідного сектора Flash.
- **Потік корисного навантаження:** бінарні дані прошивки, розбиті на однакові чанки.
- **Блок цифрового підпису квитанції:** службовий резервний сектор, куди контролер після успішної прошивки записує власний криптографічний звіт про виконання операції.

```
+------------------------------------------------------------------------+
| ЗАГОЛОВОК (128 Б): Magic, Target_ID, Monotonic_Ver, Payload_Len, SHA256|
+------------------------------------------------------------------------+
| ЦИФРОВИЙ ПІДПИС ЗАГОЛОВКА (64 Б): Ed25519 Signature (Release Key)      |
+------------------------------------------------------------------------+
| ТАБЛИЦЯ ХЕШІВ ЧАНКІВ: SHA256(Chunk 0), SHA256(Chunk 1), ...           |
+------------------------------------------------------------------------+
| ПОТІК ЧАНКІВ: [Чанк 0: 4 КБ] [Чанк 1: 4 КБ] [Чанк 2: 4 КБ] ...        |
+------------------------------------------------------------------------+
```

---

### Покроковий алгоритм потокової верифікації

Процес обробки пакета розділено на чотири послідовні фази, кожна з яких є суворим гейтом:

1. **Фаза 1: Перевірка метаданих заголовка.**
   Завантажувач зчитує перші 128 байтів файлу з файлової системи FatFS на USB або з буфера потокового шлюзу. Перевіряється сигнатура `0x47504B55` (`UPKG` у форматі Little-Endian). Далі перевіряється поле `target_hw_id` — якщо воно не збігається з кодом моделі, збереженим в OTP/eFuse, парсер негайно повертає помилку `UPKG_ERR_HW_MISMATCH`. Потім аналізується `version_monotonic`: якщо номер версії менший або рівний значенню, прочитаному з апаратних запобіжників чи захищеного EEPROM, повертається `UPKG_ERR_ROLLBACK_DETECTED`.
2. **Фаза 2: Валідація цифрового підпису заголовка.**
   Використовуючи відкритий ключ виробника (`root_public_key`), завантажувач перевіряє 64-байтний підпис Ed25519, накладений на метадані. Оскільки відкритий ключ зашитий у захищений Boot ROM або eFuse, підробити заголовок без знання закритого ключа випуску математично неможливо. Якщо підпис недійсний, Flash-пам'ять пристрою навіть не переводиться в режим запису.
3. **Фаза 3: Потоковий запис чанків та поблоковий контроль цілісності.**
   Контролер ініціалізує лічильник секторів. Для кожного блоку зчитуються 4096 байтів даних у проміжний буфер RAM. Обчислюється SHA-256 хеш блоку, який порівнюється з відповідним елементом у таблиці хешів. Лише після успішного збігу контролер викликає функцію програмування Flash-пам'яті за зміщенням `chunk_idx * 4096` у розділ Slot B. Паралельно оновлюється накопичувальний стан криптографічного хешера для всього образу.
4. **Фаза 4: Фіналізація та генерація квитанції аудиту.**
   Після запису останнього чанка накопичений SHA-256 хеш порівнюється з полем `final_sha256` заголовка. У разі повного збігу завантажувач записує в незалежну область конфігурації (NVS) структуру стану оновлення з прапорцем `PENDING_VERIFY` та встановлює лічильник спроб завантаження (Boot Retry Counter = 3). Контролер генерує підписану квитанцію про результат прошивки для збереження на носії техніка.

---

### Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UPKG_MAGIC              0x47504B55  /* "UPKG" в Little-Endian */
#define UPKG_HEADER_SIZE        128
#define UPKG_SIGNATURE_SIZE     64
#define UPKG_HASH_SIZE          32
#define UPKG_CHUNK_SIZE         4096

typedef enum {
    UPKG_OK = 0,
    UPKG_ERR_INVALID_MAGIC,
    UPKG_ERR_HW_MISMATCH,
    UPKG_ERR_ROLLBACK_DETECTED,
    UPKG_ERR_SIGNATURE_INVALID,
    UPKG_ERR_CHUNK_HASH_MISMATCH,
    UPKG_ERR_FINAL_HASH_MISMATCH,
    UPKG_ERR_FLASH_WRITE
} upkg_status_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t format_version;
    uint16_t target_hw_id;
    uint32_t version_monotonic;
    uint32_t payload_size;
    uint32_t chunk_count;
    uint8_t  final_sha256[UPKG_HASH_SIZE];
    uint8_t  reserved[40];
    uint8_t  signature[UPKG_SIGNATURE_SIZE];
} upkg_header_t;

typedef struct {
    uint16_t my_hw_id;
    uint32_t my_min_allowed_version;
    const uint8_t *root_public_key;
    /* Абстракція запису Flash */
    bool (*flash_erase_slot_b)(uint32_t total_size);
    bool (*flash_write_chunk)(uint32_t offset, const uint8_t *data, uint32_t size);
    /* Криптографічні виклики */
    bool (*ed25519_verify)(const uint8_t *msg, size_t msg_len,
                           const uint8_t *sig, const uint8_t *pub_key);
    void (*sha256_calc)(const uint8_t *data, size_t len, uint8_t *out_hash);
} upkg_verifier_ctx_t;

/* Валідація заголовка офлайн-пакета */
upkg_status_t upkg_validate_header(const upkg_verifier_ctx_t *ctx,
                                    const upkg_header_t *hdr) {
    if (hdr->magic != UPKG_MAGIC) {
        return UPKG_ERR_INVALID_MAGIC;
    }
    if (hdr->target_hw_id != ctx->my_hw_id) {
        return UPKG_ERR_HW_MISMATCH;
    }
    if (hdr->version_monotonic <= ctx->my_min_allowed_version) {
        return UPKG_ERR_ROLLBACK_DETECTED;
    }

    /* Підпис охоплює поля заголовка безпосередньо перед сигнатурою */
    const size_t signed_header_len = sizeof(upkg_header_t) - UPKG_SIGNATURE_SIZE;
    if (!ctx->ed25519_verify((const uint8_t *)hdr, signed_header_len,
                             hdr->signature, ctx->root_public_key)) {
        return UPKG_ERR_SIGNATURE_INVALID;
    }

    return UPKG_OK;
}

/* Обробка одного потокового чанка */
upkg_status_t upkg_process_chunk(const upkg_verifier_ctx_t *ctx,
                                  uint32_t chunk_idx,
                                  const uint8_t *chunk_data,
                                  uint32_t chunk_size,
                                  const uint8_t *expected_chunk_hash) {
    uint8_t calculated_hash[UPKG_HASH_SIZE];
    ctx->sha256_calc(chunk_data, chunk_size, calculated_hash);

    if (memcmp(calculated_hash, expected_chunk_hash, UPKG_HASH_SIZE) != 0) {
        return UPKG_ERR_CHUNK_HASH_MISMATCH;
    }

    uint32_t flash_offset = chunk_idx * UPKG_CHUNK_SIZE;
    if (!ctx->flash_write_chunk(flash_offset, chunk_data, chunk_size)) {
        return UPKG_ERR_FLASH_WRITE;
    }

    return UPKG_OK;
}
```
```cpp
#include <span>
#include <array>
#include <expected>
#include <cstdint>
#include <cstring>
#include <functional>

namespace offline_update {

inline constexpr uint32_t UpkgMagic = 0x47504B55; // "UPKG"
inline constexpr std::size_t HashSize = 32;
inline constexpr std::size_t SignatureSize = 64;
inline constexpr std::size_t ChunkSize = 4096;

enum class UpdateError : uint8_t {
    InvalidMagic,
    HardwareMismatch,
    RollbackDetected,
    SignatureInvalid,
    ChunkHashMismatch,
    FinalHashMismatch,
    FlashWriteFailure
};

struct [[gnu::packed]] PackageHeader {
    uint32_t magic;
    uint16_t format_version;
    uint16_t target_hw_id;
    uint32_t version_monotonic;
    uint32_t payload_size;
    uint32_t chunk_count;
    std::array<uint8_t, HashSize> final_sha256;
    std::array<uint8_t, 40> reserved;
    std::array<uint8_t, SignatureSize> signature;
};

struct DeviceSecurityPolicy {
    uint16_t hardware_id;
    uint32_t min_allowed_version;
    std::span<const uint8_t, 32> root_public_key;
};

class PackageVerifier {
public:
    using VerifyFn = std::function<bool(std::span<const uint8_t>,
                                         std::span<const uint8_t, SignatureSize>,
                                         std::span<const uint8_t, 32>)>;
    using HashFn = std::function<void(std::span<const uint8_t>, std::span<uint8_t, HashSize>)>;
    using FlashWriteFn = std::function<bool(uint32_t offset, std::span<const uint8_t>)>;

    PackageVerifier(DeviceSecurityPolicy policy,
                    VerifyFn verify_sig,
                    HashFn hash_calc,
                    FlashWriteFn flash_writer)
        : policy_(policy),
          verify_sig_(std::move(verify_sig)),
          hash_calc_(std::move(hash_calc)),
          flash_writer_(std::move(flash_writer)) {}

    [[nodiscard]] std::expected<void, UpdateError>
    validateHeader(const PackageHeader& hdr) const {
        if (hdr.magic != UpkgMagic) {
            return std::unexpected(UpdateError::InvalidMagic);
        }
        if (hdr.target_hw_id != policy_.hardware_id) {
            return std::unexpected(UpdateError::HardwareMismatch);
        }
        if (hdr.version_monotonic <= policy_.min_allowed_version) {
            return std::unexpected(UpdateError::RollbackDetected);
        }

        constexpr std::size_t signed_len = sizeof(PackageHeader) - SignatureSize;
        auto signed_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&hdr), signed_len
        );

        if (!verify_sig_(signed_bytes, hdr.signature, policy_.root_public_key)) {
            return std::unexpected(UpdateError::SignatureInvalid);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, UpdateError>
    processChunk(uint32_t chunk_index,
                 std::span<const uint8_t> chunk_data,
                 std::span<const uint8_t, HashSize> expected_hash) const {
        std::array<uint8_t, HashSize> calculated{};
        hash_calc_(chunk_data, calculated);

        if (std::memcmp(calculated.data(), expected_hash.data(), HashSize) != 0) {
            return std::unexpected(UpdateError::ChunkHashMismatch);
        }

        const uint32_t offset = chunk_index * ChunkSize;
        if (!flash_writer_(offset, chunk_data)) {
            return std::unexpected(UpdateError::FlashWriteFailure);
        }

        return {};
    }

private:
    DeviceSecurityPolicy policy_;
    VerifyFn verify_sig_;
    HashFn hash_calc_;
    FlashWriteFn flash_writer_;
};

} // namespace offline_update
```
:::

---

### Критичні пастки розробки та крайові випадки

- **Стирання передчасно (Erase-Before-Verify Trap):** якщо контролер починає прати сектори розділу Slot B до повної перевірки підпису заголовка, пошкоджений файл або зловмисна атака призведе до зайвого зносу комірок Flash-пам'яті (NOR Flash витримує від 10 000 до 100 000 циклів перезапису). Стирати слоти слід лише після того, як валідовано сигнатуру та апаратну сумісність.
- **Збіг монотонної версії при виправленні багів:** під час екстреного випуску хотфіксу розробники іноді забувають інкреметувати лічильник монотонної версії в eFuse, вважаючи патч незначним. Якщо захист від відкату вже прожигає номери у запобіжники, пристрої відхилять хотфікс як підозрілий. Кожен публічний бінарний випуск повинен строго інкрементувати лічильник.
- **Розрив зв'язку посеред запису чанка:** якщо запис 4096-байтного блоку переривається знеструмленням, сектор виявляється наполовину заповненим сміттям. При повторному старті верифікатор повинен звіряти контрольні суми вже записаних блоків і відновлювати запис саме з того чанка, де сталася помилка.
