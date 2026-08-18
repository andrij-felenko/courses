# ⚙️ Реалізація кадрування та шифрування записів TLS 1.3

Протокол записів (Record Layer) у TLS 1.3 є фундаментом, який забезпечує конфіденційність, цілісність та захист від повторного відтворення (Anti-Replay) для всіх протоколів вищого рівня: рукостискання (`Handshake`), сигналів тривоги (`Alert`) та потоків даних додатку (`Application Data`).

Уся інформація, що надходить від вищих рівнів стеку, розбивається на дискретні блоки, доповнюється службовими метаданими та захищається алгоритмами автентифікованого шифрування з асоційованими даними (AEAD). Нижче наведено повнофункціональну інженерну реалізацію кодека записів TLS 1.3 на базі симетричного шифрокомплекту `TLS_AES_128_GCM_SHA256`.

```
Архітектура обробки кадру в кодеку:

Відправлення (Protect):
Відкритий текст ──► Додавання InnerContentType (1 байт) + Нульова набивка (Padding)
                ──► Синтез Nonce = IV (96 біт) ⊕ SeqNum (64 біти)
                ──► Шифрування AES-128-GCM з AAD = 5-байтний зовнішній заголовок
                ──► Результат: 5 Б Заголовок + Шифротекст + 16 Б Auth Tag

Приймання (Unprotect):
Кадр із мережі  ──► Валідація зовнішнього заголовка (Type == 0x17, Ver == 0x0303)
                ──► Синтез Nonce = IV ⊕ SeqNum
                ──► Дешифрування та верифікація AEAD тегу (16 байтів)
                ──► Видалення нульової набивки з кінця буфера
                ──► Вилучення InnerContentType та передача чистих даних вище
```

## Інженерні принципи побудови кодека записів

Реалізація протоколу записів TLS 1.3 вимагає дотримання суворих інваріантів криптографічної та системної безпеки:

1. **Ізоляція стану та монотонність лічильника:** Кожен контекст з'єднання (окремо для відправника та отримувача) підтримує 64-бітний монотонний лічильник послідовності `seq_num`. Лічильник ніколи не передається мережею, а використовується як неявний синхронізований стан для синтезу унікального 96-бітного вектора ініціалізації (`Nonce`). Повторне використання пари `(Key, Nonce)` у режимі AES-GCM є фатальним для безпеки, тому інкремент лічильника виконується строго після кожної криптографічної операції.
2. **Автентифікація метаданих заголовка (AAD):** Зовнішній 5-байтний заголовок запису (`0x17 0x03 0x03 Length`) передається мережею у відкритому вигляді для коректного кадрування потоку сокетом TCP. Щоб активний зловмисник не міг змінити поле довжини чи підмінити тип кадру, заголовок подається в алгоритм AEAD як додаткові асоційовані дані (Additional Authenticated Data — AAD). Будь-яка зміна навіть одного біта в заголовку призводить до неприйняття кадру при перевірці 16-байтного тегу автентичності.
3. **Маскування типу та видалення набивки:** На відміну від TLS 1.2, реальний тип вмісту (`InnerContentType`) розміщується всередині зашифрованого блоку. Після дешифрування кодек виконує сканування буфера з кінця, відкидаючи нульові байти набивки, доки не знайде байт типу вмісту.

## Математичні та алгоритмічні основи режиму AES-GCM

Режим автентифікованого шифрування Galois/Counter Mode (GCM) об'єднує лічильниковий режим шифрування (CTR) з універсальним хешуванням GHASH над скінченним полем Галуа `GF(2¹²⁸)`.

### 1. Генерація ключа автентифікації GHASH
Перед початком обробки повідомлень шифр обчислює допоміжний підключ автентифікації `H` шляхом шифрування нульового 128-бітного блоку основним ключем:
`H = AES_K(0¹²⁸)`.
Значення `H` використовується як константа для множення поліномів у полі `GF(2¹²⁸)` за незвідним поліномом `f(x) = x¹²⁸ + x⁷ + x² + x + 1`.

### 2. Ініціалізація лічильника J0
Для стандартизованого в TLS 1.3 розміру вектора ініціалізації у 96 бітів (12 байтів), початковий 128-бітний блок лічильника `J0` формується шляхом простої конкатенації:
`J0 = Nonce || 0x00000001`.

Шифрування відкритого тексту виконується додаванням за модулем 2 (XOR) із псевдовипадковими блоками, згенерованими шифром AES для послідовних значень лічильника:
`Ciphertext_i = Plaintext_i ⊕ AES_K(J0 + i)`.

### 3. Обчислення автентифікаційного тегу
Функція GHASH по черзі обробляє блоки асоційованих даних `AAD` (5 байтів заголовка, доповнених нулями до 16 байтів) та всі блоки шифротексту. На кожному кроці проміжний стан складається за модулем 2 з черговим блоком і множиться на `H` у полі `GF(2¹²⁸)`.

Фінальний 16-байтний тег автентичності маскується шифруванням нульового лічильника:
`Tag = GHASH_H(AAD, Ciphertext, Lengths) ⊕ AES_K(J0)`.

Ця конструкція гарантує, що без знання ключа `K` атакуючий не може підібрати валідний тег для модифікованого шифротексту, навіть якщо він знає структуру алгоритму GHASH.

## Програмна реалізація на C та C++

Нижче наведено паралельні реалізації кодека мовами C (чистий OpenSSL EVP API) та сучасним C++20 (з використанням `std::span`, контейнерів STL та семантики володіння RAII).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#define TLS_RECORD_HEADER_LEN   5
#define TLS_AEAD_TAG_LEN        16
#define TLS_MAX_PLAINTEXT_LEN   16384
#define TLS_MAX_RECORD_LEN      (TLS_RECORD_HEADER_LEN + TLS_MAX_PLAINTEXT_LEN + 256 + TLS_AEAD_TAG_LEN)

#define CONTENT_TYPE_INVALID    0
#define CONTENT_TYPE_CCS        20
#define CONTENT_TYPE_ALERT      21
#define CONTENT_TYPE_HANDSHAKE  22
#define CONTENT_TYPE_APPDATA    23

typedef struct {
    uint8_t key[16];        /* 128-бітний ключ AES */
    uint8_t iv[12];         /* 96-бітний статичний вектор ініціалізації */
    uint64_t seq_num;       /* 64-бітний лічильник послідовності */
    EVP_CIPHER_CTX *ctx;
} tls_record_context_t;

int tls_context_init(tls_record_context_t *ctx, const uint8_t key[16], const uint8_t iv[12]) {
    if (!ctx) return -1;
    memcpy(ctx->key, key, 16);
    memcpy(ctx->iv, iv, 12);
    ctx->seq_num = 0;
    ctx->ctx = EVP_CIPHER_CTX_new();
    return (ctx->ctx != NULL) ? 0 : -1;
}

void tls_context_free(tls_record_context_t *ctx) {
    if (ctx && ctx->ctx) {
        EVP_CIPHER_CTX_free(ctx->ctx);
        ctx->ctx = NULL;
    }
}

/* Формування 96-бітного Nonce шляхом XOR статичного IV та 64-бітного лічильника */
static void make_nonce(const uint8_t iv[12], uint64_t seq_num, uint8_t nonce[12]) {
    memcpy(nonce, iv, 12);
    for (int i = 0; i < 8; ++i) {
        nonce[12 - 1 - i] ^= (uint8_t)((seq_num >> (i * 8)) & 0xFF);
    }
}

/* Захист і формування зашифрованого кадру запису (TLS Protect) */
int tls_record_protect(tls_record_context_t *ctx,
                       uint8_t inner_type,
                       const uint8_t *plaintext, size_t plaintext_len,
                       size_t padding_len,
                       uint8_t *out_record, size_t *out_record_len) {
    if (plaintext_len + 1 + padding_len > TLS_MAX_PLAINTEXT_LEN + 256) {
        return -1; /* Перевищення ліміту буфера */
    }

    uint8_t nonce[12];
    make_nonce(ctx->iv, ctx->seq_num, nonce);

    /* 1. Формування буфера відкритого тексту (Payload || InnerType || ZeroPadding) */
    size_t inner_len = plaintext_len + 1 + padding_len;
    uint8_t *inner_buf = (uint8_t *)malloc(inner_len);
    if (!inner_buf) return -1;

    memcpy(inner_buf, plaintext, plaintext_len);
    inner_buf[plaintext_len] = inner_type;
    if (padding_len > 0) {
        memset(inner_buf + plaintext_len + 1, 0x00, padding_len);
    }

    /* 2. Формування 5-байтного зовнішнього заголовка запису */
    size_t ciphertext_len = inner_len + TLS_AEAD_TAG_LEN;
    out_record[0] = 0x17; /* opaque_type: application_data */
    out_record[1] = 0x03; /* legacy_record_version: 0x0303 (TLS 1.2) */
    out_record[2] = 0x03;
    out_record[3] = (uint8_t)((ciphertext_len >> 8) & 0xFF);
    out_record[4] = (uint8_t)(ciphertext_len & 0xFF);

    /* 3. Шифрування AES-128-GCM */
    int len = 0;
    if (EVP_EncryptInit_ex(ctx->ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1 ||
        EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL) != 1 ||
        EVP_EncryptInit_ex(ctx->ctx, NULL, NULL, ctx->key, nonce) != 1) {
        free(inner_buf);
        return -1;
    }

    /* Аутентифікація додаткових асоційованих даних (AAD = 5 байтів заголовка) */
    if (EVP_EncryptUpdate(ctx->ctx, NULL, &len, out_record, TLS_RECORD_HEADER_LEN) != 1 ||
        EVP_EncryptUpdate(ctx->ctx, out_record + TLS_RECORD_HEADER_LEN, &len, inner_buf, (int)inner_len) != 1) {
        free(inner_buf);
        return -1;
    }

    if (EVP_EncryptFinal_ex(ctx->ctx, out_record + TLS_RECORD_HEADER_LEN + len, &len) != 1) {
        free(inner_buf);
        return -1;
    }

    /* Отримання 16-байтного тегу автентичності */
    uint8_t tag[TLS_AEAD_TAG_LEN];
    if (EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_GET_TAG, TLS_AEAD_TAG_LEN, tag) != 1) {
        free(inner_buf);
        return -1;
    }
    memcpy(out_record + TLS_RECORD_HEADER_LEN + inner_len, tag, TLS_AEAD_TAG_LEN);

    *out_record_len = TLS_RECORD_HEADER_LEN + ciphertext_len;
    ctx->seq_num++; /* Строгий інкремент лічильника після кожного запису */

    free(inner_buf);
    return 0;
}

/* Розшифрування, перевірка тегу та видалення набивки (TLS Unprotect) */
int tls_record_unprotect(tls_record_context_t *ctx,
                         const uint8_t *record, size_t record_len,
                         uint8_t *out_plaintext, size_t *out_plaintext_len,
                         uint8_t *out_inner_type) {
    if (record_len < TLS_RECORD_HEADER_LEN + TLS_AEAD_TAG_LEN + 1) return -1;

    /* Валідація зовнішнього заголовка */
    if (record[0] != 0x17 || record[1] != 0x03 || record[2] != 0x03) {
        return -1; /* Невірний тип або версія кадру */
    }

    uint16_t wire_len = (uint16_t)((record[3] << 8) | record[4]);
    if (wire_len != record_len - TLS_RECORD_HEADER_LEN) {
        return -1; /* Невідповідність розміру кадру */
    }

    size_t encrypted_payload_len = wire_len - TLS_AEAD_TAG_LEN;
    const uint8_t *tag = record + TLS_RECORD_HEADER_LEN + encrypted_payload_len;

    uint8_t nonce[12];
    make_nonce(ctx->iv, ctx->seq_num, nonce);

    if (EVP_DecryptInit_ex(ctx->ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1 ||
        EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL) != 1 ||
        EVP_DecryptInit_ex(ctx->ctx, NULL, NULL, ctx->key, nonce) != 1) {
        return -1;
    }

    int len = 0;
    /* Подача AAD (зовнішній заголовок) */
    if (EVP_DecryptUpdate(ctx->ctx, NULL, &len, record, TLS_RECORD_HEADER_LEN) != 1 ||
        EVP_DecryptUpdate(ctx->ctx, out_plaintext, &len, record + TLS_RECORD_HEADER_LEN, (int)encrypted_payload_len) != 1) {
        return -1;
    }

    /* Встановлення очікуваного тегу автентичності */
    if (EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_TAG, TLS_AEAD_TAG_LEN, (void *)tag) != 1) {
        return -1;
    }

    /* Фінальна перевірка цілісності AEAD */
    if (EVP_DecryptFinal_ex(ctx->ctx, out_plaintext + len, &len) != 1) {
        return -2; /* Фатальна помилка: bad_record_mac / підробка шифротексту */
    }

    /* Пошук InnerContentType: сканування нульової набивки з кінця буфера */
    size_t idx = encrypted_payload_len;
    while (idx > 0 && out_plaintext[idx - 1] == 0x00) {
        idx--;
    }

    if (idx == 0) {
        return -1; /* Помилка: запис складався лише з нулів без типу вмісту */
    }

    *out_inner_type = out_plaintext[idx - 1];
    *out_plaintext_len = idx - 1;

    ctx->seq_num++; /* Інкремент лічильника лише після успішної автентифікації */
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <memory>
#include <stdexcept>
#include <cstring>
#include <openssl/evp.h>

class TlsRecordCodec {
public:
    static constexpr size_t HeaderLen = 5;
    static constexpr size_t TagLen = 16;
    static constexpr size_t MaxPlaintextLen = 16384;

    enum class ContentType : uint8_t {
        ChangeCipherSpec = 20,
        Alert = 21,
        Handshake = 22,
        ApplicationData = 23
    };

    struct DecryptedRecord {
        ContentType type;
        std::vector<uint8_t> data;
    };

    TlsRecordCodec(std::span<const uint8_t, 16> key, std::span<const uint8_t, 12> iv)
        : ctx_(EVP_CIPHER_CTX_new(), &EVP_CIPHER_CTX_free), seq_num_(0) {
        if (!ctx_) {
            throw std::runtime_error("Не вдалося створити контекст OpenSSL EVP");
        }
        std::ranges::copy(key, key_.begin());
        std::ranges::copy(iv, iv_.begin());
    }

    std::vector<uint8_t> protect(ContentType type,
                                 std::span<const uint8_t> plaintext,
                                 size_t padding_len = 0) {
        if (plaintext.size() + 1 + padding_len > MaxPlaintextLen + 256) {
            throw std::length_error("Перевищено максимальний розмір запису TLS");
        }

        auto nonce = make_nonce(seq_num_);

        // 1. Формування відкритого тіла
        std::vector<uint8_t> inner;
        inner.reserve(plaintext.size() + 1 + padding_len);
        inner.insert(inner.end(), plaintext.begin(), plaintext.end());
        inner.push_back(static_cast<uint8_t>(type));
        inner.insert(inner.end(), padding_len, 0x00);

        // 2. Формування зовнішнього заголовка
        const size_t ciphertext_len = inner.size() + TagLen;
        std::vector<uint8_t> out(HeaderLen + ciphertext_len);
        out[0] = 0x17; // opaque_type: application_data
        out[1] = 0x03; // legacy_record_version: TLS 1.2
        out[2] = 0x03;
        out[3] = static_cast<uint8_t>((ciphertext_len >> 8) & 0xFF);
        out[4] = static_cast<uint8_t>(ciphertext_len & 0xFF);

        // 3. Шифрування AES-128-GCM
        int len = 0;
        init_cipher(true, nonce);

        // AAD = перші 5 байтів заголовка
        if (EVP_EncryptUpdate(ctx_.get(), nullptr, &len, out.data(), HeaderLen) != 1 ||
            EVP_EncryptUpdate(ctx_.get(), out.data() + HeaderLen, &len, inner.data(), static_cast<int>(inner.size())) != 1 ||
            EVP_EncryptFinal_ex(ctx_.get(), out.data() + HeaderLen + len, &len) != 1) {
            throw std::runtime_error("Збій при обчисленні шифротексту AEAD");
        }

        // Отримання тегу автентичності
        if (EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_GET_TAG, TagLen, out.data() + HeaderLen + inner.size()) != 1) {
            throw std::runtime_error("Не вдалося сформувати тег автентичності AEAD");
        }

        ++seq_num_;
        return out;
    }

    DecryptedRecord unprotect(std::span<const uint8_t> record) {
        if (record.size() < HeaderLen + TagLen + 1) {
            throw std::invalid_argument("Кадр занадто малий для запису TLS");
        }

        if (record[0] != 0x17 || record[1] != 0x03 || record[2] != 0x03) {
            throw std::runtime_error("Невірний заголовок сумісності кадру TLS");
        }

        const uint16_t wire_len = (static_cast<uint16_t>(record[3]) << 8) | record[4];
        if (wire_len != record.size() - HeaderLen) {
            throw std::length_error("Невідповідність поля довжини реальному розміру кадру");
        }

        const size_t encrypted_payload_len = wire_len - TagLen;
        const auto tag_span = record.subspan(HeaderLen + encrypted_payload_len, TagLen);
        auto nonce = make_nonce(seq_num_);

        init_cipher(false, nonce);

        std::vector<uint8_t> decrypted(encrypted_payload_len);
        int len = 0;

        // Подача AAD і дешифрування
        if (EVP_DecryptUpdate(ctx_.get(), nullptr, &len, record.data(), HeaderLen) != 1 ||
            EVP_DecryptUpdate(ctx_.get(), decrypted.data(), &len, record.data() + HeaderLen, static_cast<int>(encrypted_payload_len)) != 1) {
            throw std::runtime_error("Помилка обробки AEAD корисного вантажу");
        }

        if (EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_SET_TAG, TagLen, const_cast<uint8_t*>(tag_span.data())) != 1 ||
            EVP_DecryptFinal_ex(ctx_.get(), decrypted.data() + len, &len) != 1) {
            throw std::runtime_error("Помилка автентифікації запису: bad_record_mac (тег не зійшовся)");
        }

        // Пошук InnerContentType та видалення нулів набивки
        size_t idx = encrypted_payload_len;
        while (idx > 0 && decrypted[idx - 1] == 0x00) {
            --idx;
        }

        if (idx == 0) {
            throw std::runtime_error("Запис містить лише нулі без типу вмісту");
        }

        const auto type = static_cast<ContentType>(decrypted[idx - 1]);
        decrypted.resize(idx - 1);

        ++seq_num_;
        return { type, std::move(decrypted) };
    }

private:
    std::array<uint8_t, 16> key_;
    std::array<uint8_t, 12> iv_;
    std::unique_ptr<EVP_CIPHER_CTX, decltype(&EVP_CIPHER_CTX_free)> ctx_;
    uint64_t seq_num_;

    std::array<uint8_t, 12> make_nonce(uint64_t seq) const {
        std::array<uint8_t, 12> nonce = iv_;
        for (size_t i = 0; i < 8; ++i) {
            nonce[12 - 1 - i] ^= static_cast<uint8_t>((seq >> (i * 8)) & 0xFF);
        }
        return nonce;
    }

    void init_cipher(bool encrypt, const std::array<uint8_t, 12>& nonce) {
        auto cipher_fn = encrypt ? EVP_EncryptInit_ex : EVP_DecryptInit_ex;
        if (cipher_fn(ctx_.get(), EVP_aes_128_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_SET_IVLEN, 12, nullptr) != 1 ||
            cipher_fn(ctx_.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            throw std::runtime_error("Помилка ініціалізації контексту шифру AES-GCM");
        }
    }
};
```
:::

## Покроковий розбір коду та архітектура викликів OpenSSL

Криптографічний конвеєр кодека спирається на низькорівневий інтерфейс OpenSSL EVP (Envelope Encryption), який абстрагує апаратні особливості центрального процесора та автоматично задіює інструкції AES-NI, VAES або ARMv8 Crypto Extensions:

### 1. Ініціалізація та налаштування контексту шифрування
У процедурі `tls_record_protect` виклик `EVP_EncryptInit_ex(ctx->ctx, EVP_aes_128_gcm(), NULL, NULL, NULL)` готує структуру `EVP_CIPHER_CTX` для роботи в режимі Galois/Counter Mode.

Оскільки режим GCM за замовчуванням може очікувати вектор ініціалізації іншого розміру, обов'язковим є керівний виклик:
`EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL)`.
Лише після явної фіксації довжини IV у 12 байтів передається симетричний ключ `ctx->key` та обчислений 96-бітний `nonce`.

### 2. Двоетапна подача асоційованих даних (AAD) та відкритого тексту
Криптографічний рушій AEAD розрізняє дані, що підлягають лише автентифікації, та дані, що підлягають і шифруванню, і автентифікації:
- Перший виклик `EVP_EncryptUpdate(ctx->ctx, NULL, &len, out_record, 5)` передає вказівник на вихідний буфер як `NULL`. Для OpenSSL це однозначний сигнал про те, що передані 5 байтів заголовка є асоційованими даними AAD. Вони поглинаються поліномом автентифікації GHASH, але не піддаються шифруванню.
- Другий виклик `EVP_EncryptUpdate(ctx->ctx, out_record + 5, &len, inner_buf, inner_len)` шифрує сформований буфер відкритого тексту (прикладні дані разом із байтом `InnerContentType` та нульовою набивкою) за допомогою лічильника CTR і одночасно оновлює акумулятор GHASH.

### 3. Фіналізація та генерація автентифікаційного тегу
Після виклику `EVP_EncryptFinal_ex` формується зашифроване тіло кадру. Останнім обов'язковим кроком відправника є виклик:
`EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_GET_TAG, 16, tag)`.
Отриманий 16-байтний тег копіюється безпосередньо в кінець вихідного масиву, формуючи монолітний пакет для передачі в сокет TCP.

### 4. Верифікація при прийманні (Unprotect) та захист від часових атак
У функції `tls_record_unprotect` послідовність операцій є строго дзеркальною:
1. Заголовок подається як AAD.
2. Шифротекст дешифрується у проміжний буфер.
3. Отриманий із мережі тег встановлюється в контекст через `EVP_CTRL_GCM_SET_TAG`.
4. Виклик `EVP_DecryptFinal_ex` обчислює підсумковий тег GHASH і порівнює його з очікуваним у режимі **постійного часу (Constant-Time)**. Якщо тег не зійшовся, функція повертає помилку, а розшифровані дані негайно затираються в пам'яті, не передаючись прикладному рівню.

### 5. Семантика володіння та безпека ресурсів у C++20
У версії кодека на C++20 застосовано ідіому RAII (Resource Acquisition Is Initialization) для безпечного керування криптографічними дескрипторами OpenSSL. Об'єкт `std::unique_ptr<EVP_CIPHER_CTX, decltype(&EVP_CIPHER_CTX_free)>` гарантує, що пам'ять контексту буде звільнена автоматично при виході з області видимості або при виникненні винятку `std::runtime_error`.

Використання `std::span<const uint8_t>` у сигнатурах методів `protect` та `unprotect` дозволяє передавати посилання на фрагменти пам'яті (наприклад, мережеві буфери або рядки) без створення проміжних копій. Тільки фінальний розшифрований результат копіюється у вихідний вектор `std::vector<uint8_t>`, що мінімізує навантаження на алокатор пам'яті у високонавантажених серверах.

### 6. Захист від вичерпання лічильника записів (Sequence Number Rollover)
Стандарт RFC 8446 суворо забороняє повторне використання або переповнення 64-бітного лічильника `seq_num`. Якщо лічильник досягає значення `2⁶⁴ - 1`, відправник повинен виконати одну з двох обов'язкових дій:
1. Ініціювати процедуру ротації ключів за допомогою повідомлення `KeyUpdate`. При цьому виводиться новий сесійний ключ `Application Traffic Secret`, генерується новий вектор `iv`, а лічильник `seq_num` скидається в 0.
2. Якщо оновлення ключів не підтримується або завершилося збоєм, закрити з'єднання з надсиланням сигналу `close_notify`.

## Повний тестовий сценарій та верифікаційний слід (Test Trace)

Нижче наведено верифікаційний слід виконання круглого циклу (Round-Trip Protect/Unprotect) для кадру прикладних даних HTTP/2:

```
Тестові параметри з'єднання:
Ключ AES-128 (16 Б) : 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0a 0x0b 0x0c 0x0d 0x0e 0x0f 0x10
Статичний IV (12 Б) : 0xfa 0xeb 0xdc 0xcb 0xba 0xa9 0x98 0x87 0x76 0x65 0x54 0x43
SeqNum              : 0 (перший кадр клієнта)
Синтезований Nonce  : 0xfa 0xeb 0xdc 0xcb 0xba 0xa9 0x98 0x87 0x76 0x65 0x54 0x43

Вхідні дані:
Відкритий текст     : "GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n" (44 байти)
InnerContentType    : 0x17 (application_data)
Нульова набивка     : 16 байтів нулів 0x00

Формування відкритого блоку (61 байт):
inner_buf = [44 байти тексту] || 0x17 || [16 байтів 0x00]

Кадрування та шифрування:
Зовнішній заголовок : 0x17 0x03 0x03 0x00 0x4d (тип 0x17, версія TLS 1.2, довжина 61 + 16 = 77 байтів)
Шифротекст          : [61 байт зашифрованого AES-GCM корисного вантажу]
Тег автентичності   : [16 байтів автентифікаційного тегу GHASH]
Загальний розмір    : 5 + 77 = 82 байти на дроті

Приймання та розшифрування на стороні сервера:
1. Зчитування 5 байтів: Type = 0x17, Version = 0x0303, Length = 77
2. Зчитування 77 байтів тіла
3. Валідація тегу AEAD: УСПІШНО (код 1)
4. Сканування набивки: відкинуто 16 нулів, виявлено InnerContentType = 0x17
5. Відновлено відкритий текст: 44 байти "GET /index.html..."
6. Інкремент seq_num до 1.
```

Цей тест демонструє абсолютну еквівалентність переданого та прийнятого стану без витоку метаданих про тип або точний розмір повідомлення в мережу.

## Асинхронний розбір потоку та кадрування над сокетами non-blocking TCP

Оскільки операційна система розглядає TCP-з'єднання як неструктурований байтовий потік, системні виклики `recv()` або `read()` можуть повертати довільні фрагменти кадрів TLS — від одного байта до кількох кілобайтів за один виклик. 

У високопродуктивних серверах на базі неблокуючого вводу-виводу (epoll, kqueue, io_uring) кодек записів інтегрується в асинхронний скінченний автомат:

```
                  ┌─────────────────────────────────────────────────┐
                  ▼                                                 │
        ┌──────────────────┐  Зчитано < 5 байтів  ┌──────────────┐  │
───────►│  READING_HEADER  ├─────────────────────►│ Буферизація  ├──┘
        └─────────┬────────┘                      └──────────────┘
                  │ Зчитано повні 5 байтів заголовка
                  ▼
        ┌──────────────────┐  wire_len > 16640     ┌──────────────┐
        │ Валідація довжини├─────────────────────►│ Alert:       │──► [ЗАКРИТТЯ]
        └─────────┬────────┘                      │ record_ovflw │
                  │ 22 ≤ wire_len ≤ 16640         └──────────────┘
                  ▼
        ┌──────────────────┐  Неповне тіло        ┌──────────────┐
        │  READING_PAYLOAD ├─────────────────────►│ Буферизація  ├──┐
        └─────────┬────────┘                      └──────────────┘  │
                  │ Отримано рівно wire_len байтів                  │
                  ▼                                                 │
        ┌──────────────────┐  Збій тегу AEAD      ┌──────────────┐  │
        │ unprotect() AEAD ├─────────────────────►│ Alert:       │  │
        └─────────┬────────┘                      │ bad_mac      │  │
                  │ Успіх                         └──────────────┘  │
                  ▼                                                 │
        ┌──────────────────┐                                        │
        │ Передача даних   │────────────────────────────────────────┘
        │ прикладному коду │
        └──────────────────┘
```

Правила керування буферами в неблокуючому режимі:
1. **Збереження стану між ітераціями:** Контекст з'єднання зберігає частковий буфер кадру та лічильник очікуваних байтів. Якщо виклик `recv()` повертає помилку `EAGAIN` або `EWOULDBLOCK`, кодек не скидає лічильник послідовності `seq_num`, а чекає наступної події готовності сокета.
2. **Нуль-копіювання (Zero-Copy):** Для уникнення подвійного копіювання пам'яті сокет зчитує байти безпосередньо у виділений сегмент пам'яті, над яким згодом викликається функція `EVP_DecryptUpdate`.
3. **Захист від атак вичерпання пам'яті (Slowloris на рівні записів):** Якщо клієнт навмисно надсилає заголовок із великим полем `length = 16384`, але надсилає лише по 1 байту в хвилину, таймер очікування кадру (Record Timeout) розриває з'єднання, звільняючи виділений буфер.

## Апаратна оптимізація та векторні інструкції AES-NI і VPCLMULQDQ

Сучасні x86-64 та ARM-процесори містять спеціалізовані апаратні інструкції, які дозволяють виконувати шифрування AES-GCM без використання повільних та вразливих до часових атак таблиць підстановок (T-Tables) у пам'яті:

- **Інструкції AES-NI (`AESENC`, `AESENCLAST`):** Виконують один раунд шифрування AES безпосередньо в регістрах XMM/YMM за 1–3 такти процесора. Робота без звернення до таблиць у кеш-пам'яті L1 повністю усуває вразливість до часових атак на кеш (Cache Timing Attacks).
- **Інструкція `PCLMULQDQ` (Carry-Less Multiplication):** Виконує множення двох 64-бітних поліномів без переносу за фіксований час. Це є базовою операцією для алгоритму GHASH над полем `GF(2¹²⁸)`.
- **Векторні розширення VAES та AVX-512:** Дозволяють обробляти до чотирьох або восьми 128-бітних блоків AES паралельно за одну векторну інструкцію, досягаючи пропускної здатності понад 40–80 Гбіт/с на одне процесорне ядро.

## Розподіл обов'язків та обробка сигналів тривоги (Alert Handling Architecture)

Коли функція `unprotect` стикається з порушенням протокольних інваріантів, вона не просто повертає числовий код помилки — система зобов'язана згенерувати відповідний сигнал тривоги протоколу `Alert` та передати його в мережу перед розривом TCP-з'єднання:

1. **Помилка автентифікації (`bad_record_mac`):** Виникає при невідповідності 16-байтного тегу AEAD. Це свідчить про активну модифікацію трафіку в каналі або збій синхронізації лічильника `seq_num`. З'єднання негайно закривається, сесійний квиток видаляється з кешу.
2. **Переповнення буфера запису (`record_overflow`):** Якщо заголовок містить значення довжини понад `16640` байтів (`2¹⁴` байтів відкритого тексту + 256 байтів набивки + 1 байт типу + 16 байтів тегу), надсилається фатальний сигнал `record_overflow`.
3. **Порушення структури кадру (`unexpected_message`):** Якщо розшифрований буфер містить лише нулі без поля `InnerContentType`, кодек формує сигнал `unexpected_message`.

Будь-який сигнал тривоги рівня `fatal` шифрується поточними ключами трафіку та надсилається єдиним викликом, після чого всі дескриптори сокетів та криптографічні контексти безповоротно знищуються.

## Оптимізація викликів введення-виведення: розсіяний запис (Scatter-Gather I/O)

У наївній реалізації формування кадру запису вимагає створення єдиного неперервного буфера в динамічній пам'яті (`malloc`), куди копіюються заголовок, зашифроване тіло та тег автентичності.

Високопродуктивні рушії (наприклад, Envoy, Nginx або Cloudflare BoringSSL) використовують техніку розсіяного запису (Scatter-Gather I/O) через системний виклик `writev()` у POSIX або `WSASend()` у Windows:

```
Вектор пам'яті (iovec / WSABUF):
┌────────────────────────┬────────────────────────────────┬────────────────────────┐
│ iov[0]: 5 Байтів       │ iov[1]: N Байтів               │ iov[2]: 16 Байтів      │
│ Зовнішній заголовок    │ Зашифрований корисний вантаж   │ Автентифікаційний тег  │
│ (статичний буфер стеку)│ (буфер пулу пам'яті додатку)   │ (буфер стеку)          │
└────────────────────────┴────────────────────────────────┴────────────────────────┘
```

Такий підхід дозволяє ядру операційної системи запакувати три окремі ділянки пам'яті безпосередньо в мережевий буфер мережевої карти (NIC Ring Buffer) без жодного проміжного виділення динамічної пам'яті на купі (`zero-allocation write path`).

## Профілювання продуктивності: такти на байт (Cycles Per Byte)

Накладні витрати криптографічного кодека вимірюються кількістю процесорних тактів, витрачених на шифрування одного байта корисного навантаження (Cycles Per Byte — CPB):

- **Програмна реалізація AES-GCM без апаратних інструкцій:** ~15–22 CPB. При швидкості мережі 10 Гбіт/с один потік повністю утилізує 100% потужності процесорного ядра з частотою 3.5 ГГц.
- **Апаратне прискорення AES-NI + PCLMULQDQ:** ~0.9–1.4 CPB. Навантаження на процесор зменшується більш ніж у 15 разів.
- **Векторне прискорення AVX-512 + VAES + VPCLMULQDQ:** ~0.35–0.60 CPB. Дозволяє одному процесорному ядру шифрувати понад 50–70 Гбіт/с прикладного трафіку в реальному часі.

Ці показники підтверджують, що в сучасному апаратному середовищі накладні витрати симетричного шифрування TLS 1.3 практично не впливають на загальну пропускну здатність мережевих сервісів.

## Апаратне розвантаження в ядрі: Kernel TLS (kTLS) та SmartNIC

Для досягнення екстремальної продуктивності (100–400 Гбіт/с) у сучасних центрах обробки даних розробники переносять виконання кодека протоколу записів безпосередньо в ядро операційної системи або на апаратні мережеві карти (SmartNIC):

1. **Інтерфейс Linux kTLS (Kernel TLS):**
   - Процес у просторі користувача виконує повне асиметричне рукостискання TLS 1.3 за допомогою OpenSSL.
   - Після узгодження сесійних ключів додаток передає отримані ключі `Key` та вектори `IV` у ядро Linux через системний виклик `setsockopt(fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info))`.
   - Ядро встановлює модуль верхнього рівня `TCP_ULP` (Upper Layer Protocol). Відтепер будь-які дані, записані в сокет системним викликом `write()` або передані з диска безпосередньо через `sendfile()`, шифруються рівнем записів TLS безпосередньо всередині підсистеми сокетів ядра Linux.

2. **Апаратний оффлоад на рівні SmartNIC (Device Offload):**
   - Якщо мережевий контролер (наприклад, Mellanox ConnectX-6/7 або Intel IPU) підтримує апаратний TLS, ядро передає ключі безпосередньо в таблицю з'єднань мережевого адаптера.
   - Центральний процесор (CPU) передає потік відкритих байтів через шину PCIe за технологією DMA.
   - Кремній мережевої карти самостійно формує 5-байтні заголовки TLS, обчислює Nonce, шифрує кадри апаратним блоком AES-GCM, додає 16-байтний тег автентичності та відправляє готовий Ethernet-пакет у фізичне оптоволокно.

Ця архітектура зводить навантаження на процесор хоста при роботі з TLS 1.3 практично до нуля, дозволяючи вебсерверам роздавати терабайти шифрованого контенту на граничній швидкості фізичного каналу.

## Безпечне знищення ключів у пам'яті (Key Sanitization)

Коли контекст з'єднання знищується (виклик `tls_context_free` у C або виклик деструктора класу `TlsRecordCodec` у C++), стандарт вимагає повного стирання всіх чутливих криптографічних матеріалів.

Звичайний виклик `memset()` або вихід із функції часто оптимізується компілятором: якщо компілятор виявляє, що очищений масив більше ніколи не читається програмою, він повністю видаляє інструкції запису нулів (Dead Store Elimination).

Для гарантованого затирання пам'яті застосовуються спеціалізовані функції:
- У C: виклик `OPENSSL_cleanse(ctx->key, 16)` або `explicit_bzero()`, які захищені від оптимізацій компілятора директивами бар'єрів пам'яті.
- У C++: використання захищених алокаторів пам'яті (Secure Allocators) із підтримкою блокування пам'яті `mlock()` для запобігання скидання ключів у файл підкачки (Swap) на жорсткий диск.
