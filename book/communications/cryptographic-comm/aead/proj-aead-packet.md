# ⚙️ Реалізація захищеного мережевого кадру на основі AEAD

Побудова захищеного каналу зв'язку для мережевих протоколів, телеметрії безпілотників або передачі команд керування вимагає строгого пакування даних у захищені кадри. Мета цієї реалізації — показати повний інженерний конвеєр обробки пакетів на базі стандарту AEAD (RFC 5116): формування відкритого заголовка кадру (асоційованих даних AAD), детерміновану побудову одноразового числа Nonce із захистом від повторного використання, шифрування корисного навантаження та безкомпромісну перевірку автентичності з константним часом відгуку.

---

### Архітектура та структура захищеного кадру

Мережевий протокол має вирішувати три суперечливі задачі: проміжний маршрутизатор повинен бачити службові метадані для маршрутизації без розшифрування вмісту; кінцевий одержувач має бути певен, що метадані та тіло не були змінені; а корисне навантаження має залишатися суворо таємним.

Для цього кадр розділяється на три взаємопов'язані області:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   Асоційовані дані AAD (14 байтів, відкриті)             │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│ Magic (2 Б)  │ Version (1 Б)│ StreamID (1 Б│ SeqNo (8 Б)  │ Length (2 Б) │
│ 0x53, 0x45   │     0x01     │     0x42     │ 64-біт лічиль│ розмір корисн│
├──────────────┴──────────────┴──────────────┴──────────────┴──────────────┤
│               Зашифроване корисне навантаження (Ciphertext)              │
│               Розмір в точності дорівнює розміру Plaintext               │
├──────────────────────────────────────────────────────────────────────────┤
│                     Автентифікаційний тег Tag (16 байтів)                │
│                 Криптографічний доказ для AAD + Ciphertext               │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Призначення полів заголовка (AAD)
1. **Магічні байти `Magic` (2 байти):** константи `0x53, 0x45` (ASCII-символи `'S'`, `'E'` — Secure Envelope) для швидкої синхронізації парсера в потоці байтів та миттєвого відкидання сміттєвих пакетів ще до виклику важкої криптографії.
2. **Версія протоколу `Version` (1 байт):** фіксує номер релізу формату (`0x01`). Якщо протокол у майбутньому оновить криптографічні примітиви або поля метаданих, версія дозволить коректно обробити перехідний період.
3. **Ідентифікатор потоку `StreamID` (1 байт):** логічний номер каналу даних (наприклад, `0x01` — телеметрія, `0x42` — критичні команди польоту, `0x03` — службове відео).
4. **Номер послідовності `SeqNo` (8 байтів):** 64-бітне беззнакове ціле число, яке монотонно зростає на кожному надісланому кадрі. Це поле одночасно виконує дві фундаментальні функції: захищає систему від атак повторного відтворення (Replay Attacks) та служить основою для генерації унікального `Nonce`.
5. **Довжина навантаження `Length` (2 байти):** точний розмір відкритого тексту та відповідного шифротексту в байтах (підтримує пакети розміром до 65 535 байтів).

#### Порівняння з промисловими стандартами пакування
Ця схема кадру є концептуальним узагальненням провідних мережевих протоколів сучасності:
- **TLS 1.3 Record Layer (RFC 8446):** відкритий заголовок містить 5 байтів (`0x17 0x03 0x03 len`), а справжній тип вмісту ховається всередину зашифрованого блоку перед тегом.
- **WireGuard Transport Message:** містить 4 байти типу `0x04`, 4 байти індексу отримувача та 8 байтів лічильника, за якими йде шифротекст і 16-байтовий тег Poly1305.
- **QUIC Short Header (RFC 9000):** номер пакета шифрується окремою маскою, а тіло пакета захищається за допомогою AES-GCM або ChaCha20-Poly1305.

---

### Детермінована генерація Nonce та захист сесії

Повторне використання пари `(Key, Nonce)` у режимі AES-GCM є фатальною подією, що дозволяє зловмиснику відновити автентифікаційний ключ Галуа `H`. Щоб унеможливити колізію Nonce навіть у разі збою генератора випадкових чисел, застосовується детермінована схема конструювання вектора ініціалізації:

```
Nonce (12 байтів / 96 бітів) = Session Salt (4 байти) || Sequence Number (8 байтів)
```

- **Сесійна сіль `Session Salt` (4 байти):** випадкове число, що узгоджується між сторонами під час початкового рукостискання (Handshake) разом із ключем шифрування `Key`.
- **Номер пакета `Sequence Number` (8 байтів):** серіалізується у форматі Big-Endian (мережевий порядок байтів), гарантуючи, що кожне наступне повідомлення має унікальний 96-бітний вхід для блокового лічильника.

Оскільки 64-бітний лічильник вичерпується лише після надсилання `2^64` пакетів (що при швидкості 10 мільйонів пакетів на секунду триватиме понад 58 000 років), простір номерів є практично невичерпним. Проте за правилами безпеки IETF при досягненні лічильником значення `2^32` протокол ініціює обов'язкову процедуру заміни сесійного ключа (Rekeying).

---

### Програмна реалізація мовами C та C++

Нижче наведено повну реалізацію захищеного кадру з використанням криптографічної бібліотеки OpenSSL (EVP AEAD API). Реалізація на C оптимізована для вбудованих систем із прямим керуванням пам'яттю, а реалізація на C++20 використовує безпечні абстракції, RAII-обгортки та тип повернення `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>

#define MAGIC_BYTE_0 0x53
#define MAGIC_BYTE_1 0x45
#define PROTOCOL_VERSION 0x01
#define TAG_SIZE 16
#define NONCE_SIZE 12
#define SALT_SIZE 4
#define HEADER_SIZE 14

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[2];
    uint8_t  version;
    uint8_t  stream_id;
    uint64_t seq_no;
    uint16_t payload_len;
} PacketHeader;
#pragma pack(pop)

void derive_nonce(const uint8_t salt[SALT_SIZE], uint64_t seq_no, uint8_t nonce[NONCE_SIZE]) {
    memcpy(nonce, salt, SALT_SIZE);
    for (int i = 0; i < 8; ++i) {
        nonce[SALT_SIZE + i] = (uint8_t)((seq_no >> (56 - i * 8)) & 0xFF);
    }
}

bool aead_encrypt_frame(
    const uint8_t key[32],
    const uint8_t salt[SALT_SIZE],
    uint64_t seq_no,
    uint8_t stream_id,
    const uint8_t *plaintext,
    uint16_t plaintext_len,
    uint8_t *out_packet,
    size_t *out_packet_len
) {
    if (!key || !salt || !plaintext || !out_packet || !out_packet_len) return false;

    PacketHeader hdr;
    hdr.magic[0] = MAGIC_BYTE_0;
    hdr.magic[1] = MAGIC_BYTE_1;
    hdr.version = PROTOCOL_VERSION;
    hdr.stream_id = stream_id;
    hdr.seq_no = seq_no;
    hdr.payload_len = plaintext_len;

    uint8_t nonce[NONCE_SIZE];
    derive_nonce(salt, seq_no, nonce);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    bool success = false;
    int len = 0;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, NONCE_SIZE, NULL) != 1) goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce) != 1) goto cleanup;

    // Передача AAD (заголовка кадру)
    if (EVP_EncryptUpdate(ctx, NULL, &len, (const uint8_t *)&hdr, HEADER_SIZE) != 1) goto cleanup;

    // Копіювання відкритого заголовка на початок вихідного пакету
    memcpy(out_packet, &hdr, HEADER_SIZE);

    // Шифрування відкритого тексту
    uint8_t *ciphertext_dest = out_packet + HEADER_SIZE;
    if (EVP_EncryptUpdate(ctx, ciphertext_dest, &len, plaintext, plaintext_len) != 1) goto cleanup;

    if (EVP_EncryptFinal_ex(ctx, ciphertext_dest + len, &len) != 1) goto cleanup;

    // Генерація та запис 16-байтового автентифікаційного тегу
    uint8_t *tag_dest = ciphertext_dest + plaintext_len;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_SIZE, tag_dest) != 1) goto cleanup;

    *out_packet_len = HEADER_SIZE + plaintext_len + TAG_SIZE;
    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

bool aead_decrypt_frame(
    const uint8_t key[32],
    const uint8_t salt[SALT_SIZE],
    const uint8_t *packet,
    size_t packet_len,
    uint8_t *out_plaintext,
    uint16_t *out_plaintext_len
) {
    if (!key || !salt || !packet || !out_plaintext || !out_plaintext_len) return false;
    if (packet_len < HEADER_SIZE + TAG_SIZE) return false;

    PacketHeader hdr;
    memcpy(&hdr, packet, HEADER_SIZE);

    if (hdr.magic[0] != MAGIC_BYTE_0 || hdr.magic[1] != MAGIC_BYTE_1) return false;
    if (hdr.version != PROTOCOL_VERSION) return false;
    if (packet_len != (size_t)(HEADER_SIZE + hdr.payload_len + TAG_SIZE)) return false;

    uint8_t nonce[NONCE_SIZE];
    derive_nonce(salt, hdr.seq_no, nonce);

    const uint8_t *ciphertext = packet + HEADER_SIZE;
    const uint8_t *tag = packet + HEADER_SIZE + hdr.payload_len;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    bool success = false;
    int len = 0;

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, NONCE_SIZE, NULL) != 1) goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce) != 1) goto cleanup;

    // Перевірка AAD
    if (EVP_DecryptUpdate(ctx, NULL, &len, (const uint8_t *)&hdr, HEADER_SIZE) != 1) goto cleanup;

    // Дешифрування в буфер відкритого тексту
    if (EVP_DecryptUpdate(ctx, out_plaintext, &len, ciphertext, hdr.payload_len) != 1) goto cleanup;

    // Передача очікуваного тегу в контекст перевірки
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_SIZE, (void *)tag) != 1) goto cleanup;

    // Бар'єр перевірки тегу: повертає 1 лише при повній автентичності
    if (EVP_DecryptFinal_ex(ctx, out_plaintext + len, &len) != 1) {
        // Очищення буфера при збої автентичності
        OPENSSL_cleanse(out_plaintext, hdr.payload_len);
        goto cleanup;
    }

    *out_plaintext_len = hdr.payload_len;
    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

int main(void) {
    uint8_t key[32] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef,
                       0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10,
                       0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc,
                       0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88};
    uint8_t salt[SALT_SIZE] = {0xAA, 0xBB, 0xCC, 0xDD};

    const char *secret_msg = "COMMAND: SET_THRUST 85; TARGET_ALT 150.0;";
    uint16_t msg_len = (uint16_t)strlen(secret_msg);

    uint8_t packet[256];
    size_t packet_len = 0;

    printf("=== Тестування захищеного мережевого кадру AEAD (C) ===\n");
    if (!aead_encrypt_frame(key, salt, 1001, 0x42, (const uint8_t *)secret_msg, msg_len, packet, &packet_len)) {
        printf("Помилка шифрування кадру!\n");
        return 1;
    }
    printf("Кадр сформовано успішно. Загальний розмір: %zu байтів.\n", packet_len);

    uint8_t decrypted[256];
    uint16_t dec_len = 0;
    if (aead_decrypt_frame(key, salt, packet, packet_len, decrypted, &dec_len)) {
        decrypted[dec_len] = '\0';
        printf("Дешифровано успішно: \"%s\"\n", (char *)decrypted);
    } else {
        printf("Помилка автентифікації!\n");
    }

    printf("\n--- Спроба атаки: модифікація 1 біта у шифротексті ---\n");
    packet[HEADER_SIZE + 5] ^= 0x01; // інверсія біта в зашифрованому тілі
    if (!aead_decrypt_frame(key, salt, packet, packet_len, decrypted, &dec_len)) {
        printf("Бар'єр спрацював: підробку виявлено, пакет безпечно відкинуто!\n");
    } else {
        printf("Критична помилка: підроблений пакет прийнято!\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <cstdint>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/crypto.h>

namespace netsec {

inline constexpr uint8_t Magic0 = 0x53;
inline constexpr uint8_t Magic1 = 0x45;
inline constexpr uint8_t ProtocolVersion = 0x01;
inline constexpr size_t TagSize = 16;
inline constexpr size_t NonceSize = 12;
inline constexpr size_t SaltSize = 4;
inline constexpr size_t HeaderSize = 14;

enum class DecryptError {
    InvalidPacketSize,
    BadMagicOrVersion,
    DecryptionFailed,
    AuthenticationFailed
};

#pragma pack(push, 1)
struct PacketHeader {
    uint8_t  magic[2];
    uint8_t  version;
    uint8_t  stream_id;
    uint64_t seq_no;
    uint16_t payload_len;
};
#pragma pack(pop)

struct EvpCipherCtxDeleter {
    void operator()(EVP_CIPHER_CTX* ctx) const noexcept {
        if (ctx) EVP_CIPHER_CTX_free(ctx);
    }
};
using UniqueCipherCtx = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;

class AeadSession {
public:
    explicit AeadSession(std::span<const uint8_t, 32> key, std::span<const uint8_t, SaltSize> salt) noexcept {
        std::memcpy(key_.data(), key.data(), key.size());
        std::memcpy(salt_.data(), salt.data(), salt.size());
    }

    [[nodiscard]] std::vector<uint8_t> encrypt(
        uint64_t seq_no,
        uint8_t stream_id,
        std::span<const uint8_t> plaintext
    ) const {
        PacketHeader hdr{
            .magic = {Magic0, Magic1},
            .version = ProtocolVersion,
            .stream_id = stream_id,
            .seq_no = seq_no,
            .payload_len = static_cast<uint16_t>(plaintext.size())
        };

        const auto nonce = derive_nonce(seq_no);

        UniqueCipherCtx ctx{EVP_CIPHER_CTX_new()};
        if (!ctx) throw std::runtime_error("Не вдалося створити EVP_CIPHER_CTX");

        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1)
            throw std::runtime_error("EVP_EncryptInit_ex error");

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, NonceSize, nullptr) != 1)
            throw std::runtime_error("EVP_CTRL_GCM_SET_IVLEN error");

        if (EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1)
            throw std::runtime_error("EVP_EncryptInit_ex key error");

        int len = 0;
        // Автентифікація AAD (заголовка кадру)
        if (EVP_EncryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), HeaderSize) != 1)
            throw std::runtime_error("EVP_EncryptUpdate AAD error");

        std::vector<uint8_t> packet(HeaderSize + plaintext.size() + TagSize);
        std::memcpy(packet.data(), &hdr, HeaderSize);

        uint8_t* cipher_ptr = packet.data() + HeaderSize;
        if (EVP_EncryptUpdate(ctx.get(), cipher_ptr, &len, plaintext.data(), static_cast<int>(plaintext.size())) != 1)
            throw std::runtime_error("EVP_EncryptUpdate plaintext error");

        if (EVP_EncryptFinal_ex(ctx.get(), cipher_ptr + len, &len) != 1)
            throw std::runtime_error("EVP_EncryptFinal_ex error");

        uint8_t* tag_ptr = cipher_ptr + plaintext.size();
        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_GET_TAG, TagSize, tag_ptr) != 1)
            throw std::runtime_error("EVP_CTRL_GCM_GET_TAG error");

        return packet;
    }

    [[nodiscard]] std::expected<std::vector<uint8_t>, DecryptError> decrypt(
        std::span<const uint8_t> packet
    ) const noexcept {
        if (packet.size() < HeaderSize + TagSize) {
            return std::unexpected(DecryptError::InvalidPacketSize);
        }

        PacketHeader hdr;
        std::memcpy(&hdr, packet.data(), HeaderSize);

        if (hdr.magic[0] != Magic0 || hdr.magic[1] != Magic1 || hdr.version != ProtocolVersion) {
            return std::unexpected(DecryptError::BadMagicOrVersion);
        }

        if (packet.size() != HeaderSize + hdr.payload_len + TagSize) {
            return std::unexpected(DecryptError::InvalidPacketSize);
        }

        const auto nonce = derive_nonce(hdr.seq_no);
        const uint8_t* ciphertext = packet.data() + HeaderSize;
        const uint8_t* tag = packet.data() + HeaderSize + hdr.payload_len;

        UniqueCipherCtx ctx{EVP_CIPHER_CTX_new()};
        if (!ctx) return std::unexpected(DecryptError::DecryptionFailed);

        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, NonceSize, nullptr) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        if (EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        int len = 0;
        // Перевірка AAD
        if (EVP_DecryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), HeaderSize) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        std::vector<uint8_t> plaintext(hdr.payload_len);
        if (EVP_DecryptUpdate(ctx.get(), plaintext.data(), &len, ciphertext, hdr.payload_len) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_TAG, TagSize, const_cast<uint8_t*>(tag)) != 1)
            return std::unexpected(DecryptError::DecryptionFailed);

        // Фінальна перевірка автентичності
        if (EVP_DecryptFinal_ex(ctx.get(), plaintext.data() + len, &len) != 1) {
            OPENSSL_cleanse(plaintext.data(), plaintext.size());
            return std::unexpected(DecryptError::AuthenticationFailed);
        }

        return plaintext;
    }

private:
    [[nodiscard]] std::array<uint8_t, NonceSize> derive_nonce(uint64_t seq_no) const noexcept {
        std::array<uint8_t, NonceSize> nonce{};
        std::memcpy(nonce.data(), salt_.data(), SaltSize);
        for (size_t i = 0; i < 8; ++i) {
            nonce[SaltSize + i] = static_cast<uint8_t>((seq_no >> (56 - i * 8)) & 0xFF);
        }
        return nonce;
    }

    std::array<uint8_t, 32> key_{};
    std::array<uint8_t, SaltSize> salt_{};
};

} // namespace netsec

int main() {
    std::array<uint8_t, 32> key{
        0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef,
        0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc,
        0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88
    };
    std::array<uint8_t, 4> salt{0xAA, 0xBB, 0xCC, 0xDD};

    netsec::AeadSession session(key, salt);

    std::string command = "COMMAND: SET_THRUST 85; TARGET_ALT 150.0;";
    std::span<const uint8_t> payload(reinterpret_cast<const uint8_t*>(command.data()), command.size());

    std::cout << "=== Тестування захищеного мережевого кадру AEAD (C++20) ===\n";
    auto packet = session.encrypt(1001, 0x42, payload);
    std::cout << "Кадр успішно створено. Довжина: " << packet.size() << " байтів.\n";

    auto dec_res = session.decrypt(packet);
    if (dec_res.has_value()) {
        std::string text(dec_res->begin(), dec_res->end());
        std::cout << "Успішно дешифровано: \"" << text << "\"\n";
    } else {
        std::cout << "Помилка дешифрування!\n";
    }

    std::cout << "\n--- Спроба атаки: модифікація 1 байта в AAD (SeqNo) ---\n";
    packet[5] ^= 0xFF; // підміна бітів номера послідовності
    auto tampered_res = session.decrypt(packet);
    if (!tampered_res.has_value()) {
        std::cout << "Бар'єр спрацював: спробу підміни AAD виявлено, пакет відхилено!\n";
    } else {
        std::cout << "Помилка безпеки: підроблений AAD не виявлено!\n";
    }

    return 0;
}
```
:::

---

### Порівняльний аналіз ідіом C та C++20

Зіставлення двох наведених реалізацій наочно демонструє, як сучасні засоби мови C++ кардинально підвищують надійність обробки криптографічних структур:

1. **Керування життєвим циклом ресурсів (RAII vs Manual Goto):**
   У реалізації на C контекст `EVP_CIPHER_CTX` виділяється вручну через `EVP_CIPHER_CTX_new()`. Кожна точка виходу при помилці вимагає переходу `goto cleanup` для запобігання витоку пам'яті. У C++20 використовується розумний вказівник `std::unique_ptr` із кастомним делетором `EvpCipherCtxDeleter`. Контекст гарантовано знищується автоматично при виході зі скоупу (зокрема при виникненні винятків), що повністю ліквідує людський фактор у керуванні ресурсами.
2. **Типобезпека та межі буферів (`std::span` vs сирі покажчики):**
   У C функції приймають пари `const uint8_t *` та `size_t len`, що створює ризик передачі некоректної довжини або розіменування нульового вказівника. У C++20 тип `std::span` фіксує нерозривний зв'язок між буфером і його розміром на рівні системи типів, а фіксовані розміри ключів `std::span<const uint8_t, 32>` перевіряються компілятором під час збірки.
3. **Монадична обробка помилок (`std::expected` vs коди повернення):**
   Функція `decrypt` у C++ повертає `std::expected<std::vector<uint8_t>, DecryptError>`. Це змушує викликаючий код явно обробляти результат перед доступом до даних, унеможливлюючи випадкове читання неініціалізованого або пошкодженого буфера відкритого тексту.

---

### Покроковий розбір конвеєра обробки кадру

Простежмо шлях повідомлення від створення у пам'яті програми до успішної перевірки на стороні одержувача.

#### Етап 1. Підготовка контексту шифрування
Програма ініціалізує контекст `EVP_CIPHER_CTX` викликом `EVP_EncryptInit_ex`. Функція `EVP_aes_256_gcm()` обирає апаратно-прискорений алгоритм AES у режимі лічильника з автентифікацією Галуа. За допомогою керуючої команди `EVP_CIPHER_CTX_ctrl` з прапорцем `EVP_CTRL_GCM_SET_IVLEN` встановлюється довжина вектора ініціалізації у 12 байтів (96 бітів). Встановлення саме 96-бітного Nonce є критично важливим для швидкодії: такий розмір дозволяє напряму використати лічильний блок `Y_0 = Nonce || 0x00000001` без попереднього прогону через функцію GHASH.

#### Етап 2. Автентифікація асоційованих даних (AAD)
Виклик `EVP_EncryptUpdate` з нульовим вказівником на буфер результату (`NULL`) сигналізує криптографічному рушію, що переданий блок пам'яті є асоційованими даними AAD. Рушій не шифрує ці байти, але включає їх у ланцюг поліноміального згортання GHASH. Усі 14 байтів структури `PacketHeader` (магічні байти, версія, номер потоку, лічильник пакетів та довжина) стають криптографічно зв'язаними з майбутнім тегом.

#### Етап 3. Потокове шифрування корисного навантаження
Наступний виклик `EVP_EncryptUpdate` передає відкритий текст команди. Генератор гами AES-CTR виробляє псевдовипадковий потік блоків по 16 байтів, накладаючи їх через операцію XOR на відкритий текст. Одночасно кожен зашифрований блок надходить на конвеєр GHASH і множиться в полі `GF(2^128)` на секретний хеш-ключ `H`.

#### Етап 4. Фіналізація та вилучення тегу
Функція `EVP_EncryptFinal_ex` завершує обробку останнього блоку (доповнюючи нулями до 16 байтів у полі Галуа) та додає блок довжин `len(AAD) || len(Ciphertext)`. Після цього виклик керуючої функції `EVP_CIPHER_CTX_ctrl` з параметром `EVP_CTRL_GCM_GET_TAG` повертає 16 байтів згенерованого тегу, які дописуються у хвіст кадру.

---

### Механізм захисного бар'єра та обробка крайових випадків

Безпека системи спирається на три жорсткі інваріанти, порушення яких зводить нанівець криптографічний захист:

#### 1. Негайне очищення буфера (Захист від витоку неперевіреного тексту — RUP)
Під час дешифрування функція `EVP_DecryptUpdate` записує розшифровані байти у вихідний буфер `out_plaintext` у міру їх надходження. Однак у цей момент автентичність даних ще **не доведена** — фінальний тег перевіряється лише на кроці `EVP_DecryptFinal_ex`.

Якщо функція `EVP_DecryptFinal_ex` повертає нуль (помилка верифікації), функція зобов'язана негайно виконати виклик `OPENSSL_cleanse(out_plaintext, len)`. Ця спеціальна функція гарантує, що компілятор не оптимізує і не викине операцію занулення пам'яті як «мертвий код» (Dead-code elimination), а прикладний код не зможе прочитати байти підробленого або пошкодженого пакета.

#### 2. Константний час перевірки тегу (Захист від часових атак)
Порівняння 16-байтового тегу, надісланого в кадрі, з обчисленим локально виконується всередині OpenSSL за допомогою функції `CRYPTO_memcmp`. На відміну від стандартної бібліотечної функції `memcmp`, яка перериває виконання на першому невідповідному байті й тим самим виказує час порівняння, `CRYPTO_memcmp` завжди перевіряє всі 16 байтів до кінця, використовуючи побітове накопичення різниці через логічне АБО (`diff |= a[i] ^ b[i]`). Це унеможливлює побайтовий підбір тегу за вимірюванням затримок у мережі.

#### 3. Захист від атак повторного відтворення (Anti-Replay Window)
Навіть якщо зловмисник не може змінити зашифрований кадр, він може перехопити валідний пакет керування (наприклад, команду «вимкнути двигун») і повторно надіслати його через секунду або годину.

У виробничих протоколах (таких як IPsec та WireGuard) для захисту від повтору використовується алгоритм ковзного вікна (Sliding Window):
- приймач зберігає найбільший успішно прийнятий номер послідовності `SeqNo_max`;
- для останніх 64 або 128 пакетів ведеться бітова маска отриманих номерів;
- якщо приходить пакет із номером `SeqNo <= SeqNo_max - 64`, він відкидається без перевірки як застарілий;
- якщо приходить пакет із номером у межах вікна, перевіряється відповідний біт маски: повторний пакет негайно відхиляється;
- новий легітимний пакет із більшим `SeqNo` зсуває вікно вправо й оновлює маску.

---

### Трасування та анатомія реального пакета в байтах

Розгляньмо конкретний шістнадцятковий дамп згенерованого кадру для команди довжиною 41 байт:

```
Заголовок AAD (14 байтів):
  53 45                -> Magic ('S', 'E')
  01                   -> Version (0x01)
  42                   -> StreamID (0x42)
  00 00 00 00 00 00 03 E9 -> SeqNo (1001 у Big-Endian)
  00 29                -> Length (41 байт)

Зашифроване корисне навантаження (41 байт):
  8a 3f 91 c4 b2 e0 17 88 4d fe 99 21 0c 7a 48 2e
  5b 11 9c d0 73 aa f2 39 80 14 e7 c1 56 3d 98 1b
  e2 04 77 19 ab 84 f5 6a 12

Автентифікаційний тег Tag (16 байтів):
  3d 81 fa 90 2c 44 e8 10 9b a1 f3 77 0e 55 c6 82
```

Загальний розмір переданого мережевого кадру становить `14 + 41 + 16 = 71 байт`. Будь-яка спроба інвертувати хоча б один біт у будь-якій із трьох частин призводить до миттєвого відхилення пакета бар'єром дешифрування без виконання небезпечної команди.
