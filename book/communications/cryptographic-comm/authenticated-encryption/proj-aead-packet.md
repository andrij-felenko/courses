# ⚙️ Проектування захищеного мережевого кадру: AEAD-обгортка, стан Nonce та бар'єр верифікації

Цей практичний розділ демонструє інженерну реалізацію захищеного транспортного протоколу на базі автентифікованого шифрування (AEAD). Тут розбирається двійкове структурування мережевого кадру, керування станом монотонного лічильника векторів ініціалізації (Nonce), криптографічне зв'язування відкритих заголовків (AAD), ковзне вікно захисту від повторів (Anti-Replay Sliding Window), безперервне оновлення ключів (Rekeying), оптимізація нульового копіювання (Zero-Copy I/O), взаємодія з ядром ОС та апаратними прискорювачами (AVX-512, Linux Crypto API), порівняльний аналіз реалізації в індустріальних протоколах (WireGuard, TLS 1.3, QUIC) та суворий константно-часовий бар'єр дешифрування на базі сучасного криптографічного API OpenSSL EVP мовами C та C++.

Головна мета — показати, як уникнути критичних архітектурних пасток реальних систем: витоку неперевіреного відкритого тексту в користувацькі буфери, повторного використання векторів ініціалізації при багатопотокових збоях, десинхронізації пакетів у ненадійних мережах UDP та таймінгових каналів при звірці автентифікаційного тегу.

---

## 1. Специфікація двійкового кадру та розподіл полів

У реальних мережевих протоколах (як-от QUIC, WireGuard або TLS 1.3) кожен пакет складається з відкритих службових метаданих, що необхідні для комутації та демультиплексування з'єднання, та конфіденційного корисного навантаження.

Мережевий рівень не може шифрувати адресну інформацію, номери потоків та ідентифікатори з'єднання, оскільки мережеве обладнання повинно мати доступ до цих полів для маршрутизації без володіння кінцевими сесійними ключами. Водночас будь-яка несанкціонована зміна цих відкритих полів зловмисником у каналі зв'язку може призвести до перенаправлення трафіку, ін'єкції фальшивих команд керування або десинхронізації сесії.

Розв'язанням цієї дилеми є використання механізму асоційованих автентифікованих даних (AAD). Заголовок пакета передається відкритим текстом, але подається на вхід криптографічної схеми автентифікації разом із корисним навантаженням. У результаті автентифікаційний тег покриває як відкритий заголовок, так і зашифроване тіло.

Розглянемо канонічний формат захищеного двійкового кадру:

```
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Magic (0x5345)       |        Protocol Version       |  \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+   |-- AAD (16 байтів)
|          Message Type         |          Reserved             |   |   (Асоційовані дані)
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+   |   [НЕ шифруються]
|                    Sequence Number (64-bit, Hi)               |   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+   |
|                    Sequence Number (64-bit, Lo)               |  /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  \
|                 Encrypted Payload (Ciphertext C)              |   |-- Шифротекст C
|                     (Довжина дорівнює P)                     |   |   [Шифрується]
|                                                               |  /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |  \
|                 Authentication Tag T (16 байтів)              |   |-- Тег T
|                    (AES-GCM / Poly1305 Tag)                   |  /    [Доказ цілісності]
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Призначення полів кадру:
* **Заголовок (AAD, 16 байтів):** Передається у відкритому вигляді. Включає магічне число `Magic` (ідентифікатор протоколу), версію протоколу, тип повідомлення та 64-бітний порядковий номер `Sequence Number`. Оскільки заголовок подається як асоційовані дані `A` на вхід AEAD, будь-яка спроба проміжного маршрутизатора чи зловмисника змінити тип повідомлення або підмінити номер пакета призведе до неспівпадіння тегу `T` на стороні отримувача.
* **Шифротекст `C` (`N` байтів):** Зашифроване тіло повідомлення, розмір якого точно дорівнює розміру відкритого тексту `P` (без оверхеду на заповнення PKCS#7).
* **Тег `T` (16 байтів / 128 бітів):** Криптографічний підпис над конкатенацією `AAD || Ciphertext`, що гарантує цілісність та автентичність усього кадру.

---

## 2. Керування станом Nonce: детермінований лічильник та маска

Щоб унеможливити повтор векторів ініціалізації (Nonce), застосовується підхід стандарту TLS 1.3 (RFC 8446, розділ 5.3):
1. Під час встановлення захищеного сеансу (Handshake) сторони узгоджують 96-бітний статичний сесійний вектор `IV_base`.
2. Кожна сторона підтримує внутрішній 64-бітний монотонний лічильник надісланих пакетів `seq_num` (починаючи з 0).
3. Для кожного кадру 96-бітний Nonce формується як побітовий XOR між `IV_base` та 64-бітним `seq_num`, доповненим зліва 32 нульовими бітами:

```
Nonce = IV_base ⊕ ( 0³² || [ seq_num ]₆₄ )
```

Така конструкція гарантує, що:
* Кожен пакет має суворо унікальний Nonce;
* Сам Nonce не передається явно через мережу (економія 12 байтів у кожному кадрі), оскільки номер послідовності вже присутній у відкритому заголовку AAD;
* При спробі надіслати `2⁶⁴` пакетів сесія обов'язково розривається або ініціюється процедура оновлення сесійних ключів (Key Update / Rekeying).

---

## 3. Захист від повторів у ненадійних мережах: Ковзне вікно (Anti-Replay Window)

У протоколах передачі даних на основі UDP (WireGuard, IPsec, QUIC, DTLS) мережеві маршрутизатори можуть доставляти пакети не за порядком або дублювати їх. Проста перевірка `seq > rx_seq` призведе до того, що будь-який пакет, який затримався в дорозі й прибув після пізнішого пакета, буде помилково відкинуто.

Для розв'язання цієї проблеми впроваджують механізм **ковзного вікна захисту від повторів** (Anti-Replay Sliding Window, RFC 6479) розміром `W = 64` або `W = 128` бітів.

### Алгоритм ковзного вікна:
1. Отримувач підтримує максимальний успішно верифікований номер послідовності `max_seq` та 64-бітну бітову маску `window_bitmap`, де біт `i` позначає статус отримання пакета з номером `max_seq - i`.
2. Коли надходить пакет із номером `seq`:
   * Якщо `seq > max_seq` (новий пакет випереджає вікно): вікно зсувається вліво на `diff = seq - max_seq` позицій, біт 0 встановлюється в 1, а старі біти витісняються.
   * Якщо `seq <= max_seq`, але `max_seq - seq < 64` (пакет потрапляє всередину поточного вікна): перевіряється біт `(window_bitmap & (1ULL << (max_seq - seq)))`. Якщо біт уже дорівнює 1 — це повтор (Replay Attack), пакет негайно відкидається. Якщо 0 — пакет приймається, і після успішної верифікації тегу цей біт встановлюється в 1.
   * Якщо `seq < max_seq - 64` (пакет занадто старий): пакет відкидається без витрат ресурсів процесора на криптографічну перевірку.

---

## 4. Практична реалізація мовами C та C++

Нижче наведено повну промислову реалізацію пакування, шифрування, ковзного вікна, розпакування та верифікації кадру за допомогою алгоритму `AES-256-GCM` бібліотеки OpenSSL EVP.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <arpa/inet.h>
#endif

#define MAGIC_HEADER        0x5345
#define PROTOCOL_VERSION    0x0100
#define AEAD_KEY_SIZE       32   /* 256 бітів AES-GCM */
#define AEAD_IV_SIZE        12   /* 96 бітів Nonce */
#define AEAD_TAG_SIZE       16   /* 128 бітів автентифікаційний тег */
#define REPLAY_WINDOW_SIZE  64   /* Розмір вікна повторів у бітах */

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t version;
    uint16_t msg_type;
    uint16_t reserved;
    uint64_t seq_num;
} PacketHeader;
#pragma pack(pop)

typedef struct {
    uint8_t key[AEAD_KEY_SIZE];
    uint8_t iv_base[AEAD_IV_SIZE];
    uint64_t tx_seq;
    uint64_t rx_max_seq;
    uint64_t replay_bitmap;
} SecureChannel;

/* Ініціалізація захищеного каналу */
void secure_channel_init(SecureChannel *chan, const uint8_t key[AEAD_KEY_SIZE], const uint8_t iv_base[AEAD_IV_SIZE]) {
    memcpy(chan->key, key, AEAD_KEY_SIZE);
    memcpy(chan->iv_base, iv_base, AEAD_IV_SIZE);
    chan->tx_seq = 0;
    chan->rx_max_seq = 0;
    chan->replay_bitmap = 0;
}

/* Формування 96-бітного Nonce шляхом XOR seq_num з IV_base */
static void derive_nonce(const uint8_t iv_base[AEAD_IV_SIZE], uint64_t seq, uint8_t out_nonce[AEAD_IV_SIZE]) {
    memcpy(out_nonce, iv_base, AEAD_IV_SIZE);
    for (int i = 0; i < 8; ++i) {
        out_nonce[AEAD_IV_SIZE - 1 - i] ^= (uint8_t)((seq >> (i * 8)) & 0xFF);
    }
}

/* Перевірка номера послідовності через ковзне вікно (RFC 6479) */
static bool check_replay_window(const SecureChannel *chan, uint64_t seq) {
    if (seq == 0 && chan->rx_max_seq == 0 && chan->replay_bitmap == 0) return true;
    if (seq > chan->rx_max_seq) return true; /* Новий пакет попереду вікна */
    uint64_t diff = chan->rx_max_seq - seq;
    if (diff >= REPLAY_WINDOW_SIZE) return false; /* Пакет занадто старий */
    if (chan->replay_bitmap & (1ULL << diff)) return false; /* Пакет уже був отриманий */
    return true;
}

/* Оновлення стану вікна після успішної верифікації тегу */
static void update_replay_window(SecureChannel *chan, uint64_t seq) {
    if (seq > chan->rx_max_seq) {
        uint64_t diff = seq - chan->rx_max_seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            chan->replay_bitmap = (chan->replay_bitmap << diff) | 1ULL;
        } else {
            chan->replay_bitmap = 1ULL;
        }
        chan->rx_max_seq = seq;
    } else {
        uint64_t diff = chan->rx_max_seq - seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            chan->replay_bitmap |= (1ULL << diff);
        }
    }
}

/* Шифрування кадру (AEAD Encrypt) */
int secure_channel_encrypt_packet(
    SecureChannel *chan,
    uint16_t msg_type,
    const uint8_t *plaintext,
    size_t plaintext_len,
    uint8_t *out_frame,
    size_t *out_frame_len
) {
    if (!chan || !plaintext || !out_frame || !out_frame_len) return -1;

    PacketHeader hdr;
    hdr.magic = htons(MAGIC_HEADER);
    hdr.version = htons(PROTOCOL_VERSION);
    hdr.msg_type = htons(msg_type);
    hdr.reserved = 0;
    hdr.seq_num = htobe64(chan->tx_seq);

    uint8_t nonce[AEAD_IV_SIZE];
    derive_nonce(chan->iv_base, chan->tx_seq, nonce);
    chan->tx_seq++; /* Суворо монотонний інкремент */

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    int ret = -1;
    int len = 0;

    /* 1. Ініціалізація шифру AES-256-GCM */
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, AEAD_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, chan->key, nonce) != 1) goto cleanup;

    /* 2. Подання асоційованих даних AAD (Заголовок кадру) */
    if (EVP_EncryptUpdate(ctx, NULL, &len, (const uint8_t *)&hdr, sizeof(hdr)) != 1) goto cleanup;

    /* 3. Шифрування корисного навантаження (Plaintext -> Ciphertext) */
    uint8_t *ciphertext_dest = out_frame + sizeof(PacketHeader);
    if (EVP_EncryptUpdate(ctx, ciphertext_dest, &len, plaintext, (int)plaintext_len) != 1) goto cleanup;

    /* 4. Завершення шифрування */
    if (EVP_EncryptFinal_ex(ctx, ciphertext_dest + len, &len) != 1) goto cleanup;

    /* 5. Отримання 128-бітного автентифікаційного тегу */
    uint8_t *tag_dest = ciphertext_dest + plaintext_len;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_GET_TAG, AEAD_TAG_SIZE, tag_dest) != 1) goto cleanup;

    /* Запис відкритого заголовка в початок кадру */
    memcpy(out_frame, &hdr, sizeof(hdr));
    *out_frame_len = sizeof(PacketHeader) + plaintext_len + AEAD_TAG_SIZE;
    ret = 0;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    OPENSSL_cleanse(nonce, sizeof(nonce));
    return ret;
}

/* Дешифрування та верифікація кадру (AEAD Decrypt & Verify) */
int secure_channel_decrypt_packet(
    SecureChannel *chan,
    const uint8_t *in_frame,
    size_len_t frame_len,
    uint8_t *out_plaintext,
    size_t *out_plaintext_len,
    uint16_t *out_msg_type
) {
    if (!chan || !in_frame || !out_plaintext || !out_plaintext_len || !out_msg_type) return -1;
    if (frame_len < sizeof(PacketHeader) + AEAD_TAG_SIZE) return -2; /* Пакет надто короткий */

    const PacketHeader *hdr = (const PacketHeader *)in_frame;
    if (ntohs(hdr->magic) != MAGIC_HEADER || ntohs(hdr->version) != PROTOCOL_VERSION) return -3;

    uint64_t seq = be64toh(hdr->seq_num);
    /* Перевірка вікна повторів перед початком дорогих криптографічних розрахунків */
    if (!check_replay_window(chan, seq)) return -4;

    size_t ciphertext_len = frame_len - sizeof(PacketHeader) - AEAD_TAG_SIZE;
    const uint8_t *ciphertext = in_frame + sizeof(PacketHeader);
    const uint8_t *tag = in_frame + sizeof(PacketHeader) + ciphertext_len;

    uint8_t nonce[AEAD_IV_SIZE];
    derive_nonce(chan->iv_base, seq, nonce);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    int ret = -5; /* Код помилки: автентифікація не пройдена */
    int len = 0;

    /* 1. Ініціалізація дешифрування AES-256-GCM */
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, AEAD_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, chan->key, nonce) != 1) goto cleanup;

    /* 2. Подання асоційованих даних AAD (Заголовок) */
    if (EVP_DecryptUpdate(ctx, NULL, &len, (const uint8_t *)hdr, sizeof(PacketHeader)) != 1) goto cleanup;

    /* 3. Дешифрування корисного навантаження у буфер отримувача */
    if (EVP_DecryptUpdate(ctx, out_plaintext, &len, ciphertext, (int)ciphertext_len) != 1) goto cleanup;

    /* 4. Встановлення очікуваного автентифікаційного тегу */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_TAG, AEAD_TAG_SIZE, (void *)tag) != 1) goto cleanup;

    /* 5. БАР'ЄР ВЕРИФІКАЦІЇ: якщо тег не зійшовся, EVP_DecryptFinal_ex повертає <= 0 */
    if (EVP_DecryptFinal_ex(ctx, out_plaintext + len, &len) <= 0) {
        /* Очищення буфера у разі провалу верифікації */
        OPENSSL_cleanse(out_plaintext, ciphertext_len);
        goto cleanup;
    }

    /* Успішна верифікація: оновлюємо вікно повторів і повертаємо дані */
    update_replay_window(chan, seq);
    *out_plaintext_len = ciphertext_len;
    *out_msg_type = ntohs(hdr->msg_type);
    ret = 0;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    OPENSSL_cleanse(nonce, sizeof(nonce));
    return ret;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <span>
#include <array>
#include <expected>
#include <memory>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/crypto.h>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <arpa/inet.h>
#endif

enum class AeadError {
    InvalidInput,
    ContextAllocationFailed,
    CryptoOperationFailed,
    PacketTooShort,
    InvalidHeader,
    ReplayDetected,
    AuthenticationFailed
};

#pragma pack(push, 1)
struct PacketHeader {
    uint16_t magic{0x5345};
    uint16_t version{0x0100};
    uint16_t msg_type{0};
    uint16_t reserved{0};
    uint64_t seq_num{0};
};
#pragma pack(pop)

class AeadChannel {
public:
    static constexpr size_t KeySize = 32;   // AES-256
    static constexpr size_t IvSize  = 12;   // 96-біт Nonce
    static constexpr size_t TagSize = 16;   // 128-біт Tag
    static constexpr size_t WindowSize = 64; // Ковзне вікно

    AeadChannel(std::span<const uint8_t, KeySize> key, std::span<const uint8_t, IvSize> iv_base)
        : tx_seq_(0), rx_max_seq_(0), replay_bitmap_(0) {
        std::memcpy(key_.data(), key.data(), KeySize);
        std::memcpy(iv_base_.data(), iv_base.data(), IvSize);
    }

    ~AeadChannel() {
        OPENSSL_cleanse(key_.data(), key_.size());
        OPENSSL_cleanse(iv_base_.data(), iv_base_.size());
    }

    // Заборона копіювання для запобігання дублюванню лічильників Nonce
    AeadChannel(const AeadChannel&) = delete;
    AeadChannel& operator=(const AeadChannel&) = delete;
    AeadChannel(AeadChannel&&) noexcept = default;
    AeadChannel& operator=(AeadChannel&&) noexcept = default;

    std::expected<std::vector<uint8_t>, AeadError> encrypt(
        uint16_t msg_type,
        std::span<const uint8_t> plaintext
    ) {
        PacketHeader hdr{
            .magic = htons(0x5345),
            .version = htons(0x0100),
            .msg_type = htons(msg_type),
            .reserved = 0,
            .seq_num = htobe64(tx_seq_)
        };

        auto nonce = derive_nonce(tx_seq_);
        tx_seq_++; // Суворо монотонний крок

        auto ctx = make_evp_ctx();
        if (!ctx) return std::unexpected(AeadError::ContextAllocationFailed);

        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_IVLEN, IvSize, nullptr) != 1 ||
            EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        int len = 0;
        // Подання AAD (Заголовок)
        if (EVP_EncryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        std::vector<uint8_t> frame(sizeof(PacketHeader) + plaintext.size() + TagSize);
        std::memcpy(frame.data(), &hdr, sizeof(hdr));

        uint8_t* ciphertext_ptr = frame.data() + sizeof(PacketHeader);
        if (EVP_EncryptUpdate(ctx.get(), ciphertext_ptr, &len, plaintext.data(), static_cast<int>(plaintext.size())) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        if (EVP_EncryptFinal_ex(ctx.get(), ciphertext_ptr + len, &len) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        uint8_t* tag_ptr = ciphertext_ptr + plaintext.size();
        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_GET_TAG, TagSize, tag_ptr) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        OPENSSL_cleanse(nonce.data(), nonce.size());
        return frame;
    }

    struct DecryptedMessage {
        uint16_t msg_type;
        std::vector<uint8_t> payload;
    };

    std::expected<DecryptedMessage, AeadError> decrypt(std::span<const uint8_t> frame) {
        if (frame.size() < sizeof(PacketHeader) + TagSize) {
            return std::unexpected(AeadError::PacketTooShort);
        }

        PacketHeader hdr;
        std::memcpy(&hdr, frame.data(), sizeof(hdr));

        if (ntohs(hdr.magic) != 0x5345 || ntohs(hdr.version) != 0x0100) {
            return std::unexpected(AeadError::InvalidHeader);
        }

        uint64_t seq = be64toh(hdr.seq_num);
        if (!check_replay(seq)) {
            return std::unexpected(AeadError::ReplayDetected);
        }

        size_t ciphertext_len = frame.size() - sizeof(PacketHeader) - TagSize;
        const uint8_t* ciphertext_ptr = frame.data() + sizeof(PacketHeader);
        const uint8_t* tag_ptr = frame.data() + sizeof(PacketHeader) + ciphertext_len;

        auto nonce = derive_nonce(seq);
        auto ctx = make_evp_ctx();
        if (!ctx) return std::unexpected(AeadError::ContextAllocationFailed);

        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_IVLEN, IvSize, nullptr) != 1 ||
            EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        int len = 0;
        // Подання AAD
        if (EVP_DecryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        std::vector<uint8_t> plaintext(ciphertext_len);
        if (EVP_DecryptUpdate(ctx.get(), plaintext.data(), &len, ciphertext_ptr, static_cast<int>(ciphertext_len)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_TAG, TagSize, const_cast<uint8_t*>(tag_ptr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        // Бар'єр верифікації
        if (EVP_DecryptFinal_ex(ctx.get(), plaintext.data() + len, &len) <= 0) {
            OPENSSL_cleanse(plaintext.data(), plaintext.size());
            return std::unexpected(AeadError::AuthenticationFailed);
        }

        update_replay(seq);
        OPENSSL_cleanse(nonce.data(), nonce.size());

        return DecryptedMessage{
            .msg_type = ntohs(hdr.msg_type),
            .payload = std::move(plaintext)
        };
    }

private:
    std::array<uint8_t, KeySize> key_{};
    std::array<uint8_t, IvSize>  iv_base_{};
    uint64_t tx_seq_{0};
    uint64_t rx_max_seq_{0};
    uint64_t replay_bitmap_{0};

    struct EvpCtxDeleter {
        void operator()(EVP_CIPHER_CTX* ptr) const noexcept {
            if (ptr) EVP_CIPHER_CTX_free(ptr);
        }
    };
    using EvpCtxPtr = std::unique_ptr<EVP_CIPHER_CTX, EvpCtxDeleter>;

    static EvpCtxPtr make_evp_ctx() {
        return EvpCtxPtr(EVP_CIPHER_CTX_new());
    }

    std::array<uint8_t, IvSize> derive_nonce(uint64_t seq) const noexcept {
        std::array<uint8_t, IvSize> out;
        std::memcpy(out.data(), iv_base_.data(), IvSize);
        for (size_t i = 0; i < 8; ++i) {
            out[IvSize - 1 - i] ^= static_cast<uint8_t>((seq >> (i * 8)) & 0xFF);
        }
        return out;
    }

    bool check_replay(uint64_t seq) const noexcept {
        if (seq == 0 && rx_max_seq_ == 0 && replay_bitmap_ == 0) return true;
        if (seq > rx_max_seq_) return true;
        uint64_t diff = rx_max_seq_ - seq;
        if (diff >= WindowSize) return false;
        if (replay_bitmap_ & (1ULL << diff)) return false;
        return true;
    }

    void update_replay(uint64_t seq) noexcept {
        if (seq > rx_max_seq_) {
            uint64_t diff = seq - rx_max_seq_;
            if (diff < WindowSize) {
                replay_bitmap_ = (replay_bitmap_ << diff) | 1ULL;
            } else {
                replay_bitmap_ = 1ULL;
            }
            rx_max_seq_ = seq;
        } else {
            uint64_t diff = rx_max_seq_ - seq;
            if (diff < WindowSize) {
                replay_bitmap_ |= (1ULL << diff);
            }
        }
    }
};
```
:::

---

## 5. Анатомія викликів OpenSSL EVP для AEAD

Робота з інтегрованими режимами AEAD в інтерфейсі OpenSSL EVP вимагає чіткого дотримання послідовності кроків, порушення якої призводить до внутрішніх збоїв бібліотеки:

1. **Конфігурація довжини вектора ініціалізації (IV Length):**
   За замовчуванням OpenSSL очікує 12 байтів (96 бітів) для GCM. Якщо протокол використовує нестандартний розмір вектора, виклик `EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, ...)` обов'язково повинен відбуватися **до** виклику `EVP_EncryptInit_ex` з конкретним вказівником на ключ та IV. Інакше бібліотека повертає помилку ініціалізації контексту.
2. **Подання асоційованих даних (AAD Update):**
   Для обробки нешифрованих метаданих викликається `EVP_EncryptUpdate` (або `EVP_DecryptUpdate`), де вказівник на вихідний буфер передається як `NULL`. Це вказує рушію, що дані не потребують шифрування й мають бути передані виключно в поліноміальний акумулятор GHASH. Кількість викликів AAD може бути довільною, але всі вони повинні передувати першому виклику обробки корисного навантаження.
3. **Обробка корисного навантаження (Payload Update):**
   Після подання AAD наступні виклики `EVP_EncryptUpdate` з дійсним вихідним буфером шифрують дані та одночасно оновлюють акумулятор GHASH блоками шифротексту.
4. **Видобування та встановлення тегу (Get/Set Tag):**
   * При шифруванні: `EVP_EncryptFinal_ex` фіналізує обчислення (для потокових режимів GCM/CTR вихідна довжина дорівнює 0), після чого керуюча команда `EVP_CTRL_AEAD_GET_TAG` копіює 16-байтовий тег із внутрішнього стану контексту у вихідний буфер.
   * При дешифруванні: команда `EVP_CTRL_AEAD_SET_TAG` повинна передати очікуваний тег у контекст **до** виклику `EVP_DecryptFinal_ex`. Функція `EVP_DecryptFinal_ex` виконує константно-часову звірку й повертає 1 при успіху або 0 (чи від'ємне число) при неспівпадінні хоча б одного біта.

---

## 6. Протокол динамічного оновлення ключів (Rekeying State Machine)

Навіть при використанні 64-бітного монотонного лічильника існує теоретична та практична межа безпеки кількості повідомлень, зашифрованих на одному ключі.

Для алгоритму AES-GCM стандарт NIST SP 800-38D встановлює жорстке обмеження: під одним ключем дозволено зашифрувати не більше `2³²` пакетів при випадкових Nonce та не більше `2⁶⁴` при лічильниках. Крім того, при передачі гігабітних потоків даних колізія блоків у режимі CTR може призводити до витоку інформації за парадоксом днів народження після обробки `2⁶⁴` 128-бітних блоків.

Для забезпечення досконалої прямої секретності (Forward Secrecy) та захисту від вичерпання простору лічильників високошвидкісні канали реалізують автомат станів оновлення ключів:

```
[ Стан 0: Активний ключ K_n ]
           |
           | Лічильник tx_seq досягає REKEY_THRESHOLD (наприклад, 2³⁰ пакетів)
           v
[ Стан 1: Ініціація Rekeying ]
  - Відправник генерує повідомлення KeyUpdate
  - Обчислюється новий ключ: K_{n+1} = HKDF-Expand-Label(K_n, "rekey", "", 32)
  - Скидається лічильник: tx_seq = 0
           |
           v
[ Стан 2: Фаза перехідного прийому (In-Flight Epoch) ]
  - Отримувач підтримує два активних ключових контексти: Поточний K_n та Новий K_{n+1}
  - Якщо надходить пакет зі старим номером епохи, він дешифрується на K_n
  - Після отримання першого валідного пакета на K_{n+1} старий ключ K_n безповоротно знищується з пам'яті (OPENSSL_cleanse)
```

Такий ступінчастий перехід гарантує, що жоден пакет, який перебував у процесі транспортування через глобальні маршрутизатори Інтернету під час ініціації процедури оновлення, не буде відкинутий або втрачений через неузгодженість ключів.

---

## 7. Векторизація та оптимізація Zero-Copy у високопродуктивних мережах

У високошвидкісних мережевих серверах (100 Гбіт/с Ethernet, DPDK, AF_XDP) копіювання даних між буферами ядра, бібліотеки OpenSSL та програми є головним вузьким місцем, що обмежує пропускну здатність системи.

Для досягнення максимальної продуктивності застосовують метод прямого шифрування за місцем (In-Place Encryption):
1. **Збірка вектора вводу-виводу (Scatter-Gather I/O):**
   Замість виділення єдиного монолітного масиву пам'яті під заголовок, шифротекст і тег, мережевий стек формує структуру з трьох дескрипторів пам'яті (наприклад, масив `struct iovec` у POSIX):
   * `iov[0]`: Буфер заголовка пакета (AAD, 16 байтів).
   * `iov[1]`: Буфер корисного навантаження у виділеному пулі пам'яті DMA мережевої карти.
   * `iov[2]`: Хвостовий буфер для 16 байтів тегу автентичності.
2. **Шифрування за місцем (In-Place Ciphering):**
   Виклик `EVP_EncryptUpdate(ctx, payload_ptr, &len, payload_ptr, payload_len)` виконує перетворення відкритого тексту в шифротекст безпосередньо в тому самому буфері пам'яті DMA без проміжного копіювання.
3. **Апаратна вибірка через DMA:**
   Мережева карта зчитує готовий сформований кадр безпосередньо з системної пам'яті через механізм розсіяного зчитування DMA, що виключає зайві цикли звернення до кеш-пам'яті процесора.

---

## 8. Апаратні прискорювачі та взаємодія з Linux Crypto API

Сучасні високопродуктивні рушії шифрування не виконують математичні операції над двійковими поліномами програмно. Натомість під час запуску системи бібліотека динамічно опитує біти векторних розширень процесора (через `CPUID` або бітову маску `OPENSSL_ia32cap`):

* **Інструкції VAES та VPCLMULQDQ (AVX-512):** Дозволяють паралельно обробляти до чотирьох 128-бітних блоків AES та GHASH в одному 512-бітному регістрі `ZMM`, забезпечуючи обробку трафіку зі швидкістю понад 40 Гбіт/с на одне фізичне ядро процесора.
* **ARMv8 Crypto Extensions:** Інструкції `AESE`/`AESD`/`PMULL` виконують раунди AES та множення в `GF(2¹²⁸)` безпосередньо в регістрах NEON на смартфонах і серверах ARM64.
* **Linux Kernel Crypto API (`AF_ALG`):** У просторі ядра драйвери мережевих тунелів (IPsec XFRM, WireGuard kmod) взаємодіють з апаратними прискорювачами через інтерфейс `crypto_aead` ядра Linux, де дескриптор `struct aead_request` пов'язує ланцюжки списків пам'яті розсіювання (`scatterlist`) з чергами DMA мережевих співпроцесорів.

---

## 9. Реалізація AEAD в індустріальних мережевих протоколах

Різні сучасні мережеві протоколи реалізують парадигму AEAD з урахуванням специфіки свого транспортного середовища:

* **WireGuard (VPN через UDP):**
  Використовує виключно `ChaCha20-Poly1305`. Усі пакети даних (Type 4) мають фіксований 16-байтовий відкритий заголовок: 1 байт типу, 3 байти зарезервовано, 4 байти індексу сесії отримувача (`receiver_index`) та 8 байтів лічильника `counter` (Little-Endian). Цей заголовок передається як AAD, що запобігає спуфінгу індексів з'єднання.
* **TLS 1.3 (RFC 8446 Record Layer):**
  Усунув явний номер запису з мережевого кадру. Номер послідовності `seq_num` підтримується неявно обома сторонами й використовується для XOR з `IV_base`. Відкритий заголовок запису TLS (5 байтів: `0x17 0x03 0x03` та 2 байти довжини) подається як AAD. Усередині шифротексту розміщується відкритий текст разом із байтом справжнього типу контенту (`Content_Type`) та довільною кількістю нульових байтів вирівнювання довжини для захисту від аналізу розміру пакетів (Traffic Analysis).
* **QUIC (RFC 9001, HTTP/3):**
  Реалізує дворівневий криптографічний захист. Повне корисне навантаження кадру шифрується вибраним AEAD-алгоритмом (AES-GCM чи ChaCha20-Poly1305), де відкритий заголовок QUIC є AAD. Після цього відкритий номер пакета в заголовку маскується додатковим одноблоковим шифром (Header Protection Mask), щоб пасивні спостерігачі не могли відстежувати затримки та втрати пакетів клієнта за номерами послідовностей.

---

## 10. Аналіз інженерних пасток при роботі з AEAD

При розробці систем на основі AEAD типово виникають чотири критичні помилки, кожна з яких повністю нівелює математичну стійкість алгоритмів:

### 1. Пастка потокового дешифрування (Unverified Plaintext Streaming)
При отриманні великих файлів (гігабайтних блоків даних) виникає спокуса передавати розшифровані байти безпосередньо в обробник програми в міру надходження блоків через мережевий сокет, до того як надійде фінальний автентифікаційний тег.

Це фатальна архітектурна вразливість: якщо зловмисник маніпулював байтами потоку в каналі зв'язку, програма вже виконала дії над фальшивими даними (наприклад, розпарсила заголовок файлу, виділила пам'ять, створила системні процеси чи виконала команди) до виклику `EVP_DecryptFinal_ex`. Усі дані повинні акумулюватися в ізольованому проміжному буфері й передаватися в бізнес-логіку **виключно після успішної перевірки тегу**. Для передачі великих потоків протокол повинен самостійно фрагментувати потік на невеликі незалежні кадри (наприклад, по 16 КБ або 64 КБ), кожен з яких забезпечується власним тегом і перевіряється окремо.

### 2. Гонка станів лічильника в багатопотокових серверах
Якщо один об'єкт сесії захищеного каналу використовується кількома робочими потоками (worker threads) без суворої атомарної синхронізації або паралельного розбиття простору лічильників, виникає стан гонки (race condition):
* Два потоки можуть одночасно зчитати однаковий `tx_seq` і згенерувати ідентичний Nonce для двох різних повідомлень.
* Як показано в математичному виведенні, це призводить до миттєвого розкриття відкритого тексту за атакою Two-Time Pad та знаходження хеш-підключа `H`.
* Рішення: кожен потік повинен або володіти незалежним сесійним ключем, або використовувати атомарну операцію `fetch_add` над 64-бітним лічильником до початку формування кадру.

### 3. Неконстантний час перевірки тегу (Side-Channel Leaks)
Якщо розробник реалізує власну перевірку тегу за допомогою стандартної функції `memcmp(tag1, tag2, 16)`, процесор завершує виконання інструкції на першому байті, де виявлено неспівпадіння.

Зловмисник, вимірюючи час відповіді сервера на запити з модифікованими тегами, байт за байтом підбирає 128-бітний тег всього за `16 × 256 = 4096` мережевих спроб. У бібліотеці OpenSSL функція `EVP_DecryptFinal_ex` гарантує виконання звірки в строго константному часі через функцію `CRYPTO_memcmp`, де всі 16 байтів XOR-яться в акумулятор без умовних переходів.

### 4. Оптимізація мертвого коду при очищенні пам'яті (Dead Store Elimination)
Коли секретні дані (ключі, проміжні вектори Nonce, відхилені розшифровані буфери) очищаються за допомогою стандартної функції `memset(ptr, 0, size)`, оптимізуючий компілятор C/C++ бачить, що буфер `ptr` більше не використовується до кінця функції чи звільнення пам'яті, і повністю видаляє виклик `memset` як «зайвий».

У результаті секретний матеріал залишається у стеку або купі процесу, звідки може бути викрадений через уразливості виходу за межі буфера (Use-After-Free, Heartbleed). Для гарантованого знищення конфіденційних структур необхідно використовувати захищені платформні виклики: `OPENSSL_cleanse()`, `explicit_bzero()` або `SecureZeroMemory()`.
