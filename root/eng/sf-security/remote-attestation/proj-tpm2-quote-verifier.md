# ⚙️ Реалізація верифікатора цитати TPM2_Quote та відновлення стану PCR

Віддалений верифікатор атестації є критичним елементом архітектури нульової довіри (Zero Trust): він приймає від клієнтського вузла апаратну цитату `TPM2_Quote`, цифровий підпис, створений асиметричним ключем атестації (Attestation Key, AK), та послідовний двійковий журнал вимірювань завантаження (TCG Event Log). Завдання сервісу верифікації полягає не просто в перевірці криптографічного підпису, а у відновленні всього ланцюга обчислень: перевірці свіжості виклику за допомогою криптографічного одноразового значення (nonce), валідації полів структури `TPMS_ATTEST` та математичному повторенні (replay) усіх операцій розширення регістрів PCR над записами журналу.

Якщо хоча б один біт у журналі подій змінено, якщо якусь подію видалено або порядок завантаження модулів ядра порушено, відтворений у пам'яті верифікатора підсумковий стан регістра не збіжиться зі значенням `pcrDigest`, завіреним апаратним чипом TPM.

## 1. Архітектура та математична модель верифікації

Уся процедура перевірки цитати опирається на сувору математичну послідовність. На відміну від звичайного цифрового підпису документа, де перевіряється відповідність геша вихідному тексту, атестаційна цитата TPM 2.0 є складеним об'єктом. Чип формує внутрішню структуру `TPMS_ATTEST`, де поле `extraData` заповнюється надісланим сервером одноразовим кодом (nonce), а поле `attested.quote.pcrDigest` містить криптографічний дайджест обраних регістрів PCR.

```
+-----------------------------------------------------------------------------+
| Вхідні дані: Quote Blob (TPM2B_ATTEST), Signature, Nonce, EventLog, AK_Pub  |
+-----------------------------------------------------------------------------+
                                      │
                                      ▼
+─────────────────────────────────────────────────────────────────────────────+
| Фаза 1: Валідація структури TPMS_ATTEST                                     |
| • Перевірка магічного числа: magic == 0xff544347 (TPM_GENERATED_VALUE)      |
| • Перевірка типу структури: type == 0x8018 (TPM_ST_ATTEST_QUOTE)            |
| • Перевірка свіжості: extraData == Client_Nonce                             |
+─────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼
+─────────────────────────────────────────────────────────────────────────────+
| Фаза 2: Криптографічна перевірка підпису                                    |
| • Підпис перевіряється над «сирим» бінарним буфером TPM2B_ATTEST            |
| • Використовується публічний ключ AK (RSA-2048 / ECDSA P-256)               |
+─────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼
+─────────────────────────────────────────────────────────────────────────────+
| Фаза 3: Відтворення TCG Event Log (Replay)                                  |
| • Ініціалізація симульованого регістра: Sim_PCR[i] = 0000...0000            |
| • Для кожного запису: Sim_PCR[i] = SHA256(Sim_PCR[i] || Event_Digest)       |
| • Обчислення композитного геша: Composite = SHA256(Sim_PCR_0 || ... )       |
+─────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼
+─────────────────────────────────────────────────────────────────────────────+
| Фаза 4: Порівняння дайджестів                                               |
| • Composite_Digest == Quoted_PCR_Digest → Підтвердження цілісності системи |
+─────────────────────────────────────────────────────────────────────────────+
```

Для банку SHA-256 кожна операція розширення під час симуляції журналу розраховується за формулою:

```
PCR[i]_new = SHA256(PCR[i]_old || Event_Digest)
```

Початковий стан регістра `PCR[i]_0` для стандартних регістрів 0–15 дорівнює 32 нульовим байтам (`0x00...0x00`), тоді як для регістра локалітетів PCR[16] за замовчуванням встановлюється значення `0xFF...0xFF`. Після того, як верифікатор обробляє останню подію для всіх запитаних регістрів, він обчислює їхній композитний геш (конкатенацію всіх отриманих PCR-значень, пропущену через SHA-256) і зіставляє його з полем `pcrDigest` усередині розпакованої цитати.

Крім перевірки цілісності завантажувальних бінарних файлів, верифікатор аналізує семантику кожного запису логу: відповідність завантаженого ядра дозволеному списку версій, коректність параметрів командного рядка Linux (`/proc/cmdline`) та цілісність початкового образу віртуального диска `initramfs`.

## 2. Реалізація верифікатора мовами C та C++

Нижче наведено модульну реалізацію ядра верифікатора. Варіант на мові C демонструє роботу з низькорівневим інтерфейсом OpenSSL EVP та безпосереднє маніпулювання байтовими буферами. Варіант на мові C++ використовує сучасні ідіоми: безпечні неволодіючі представлення пам'яті `std::span`, контейнери фіксованого розміру `std::array`, RAII-обгортки над ресурсами OpenSSL та тип повернення результату `std::expected` для явної обробки помилок без винятків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/sha.h>

#define TPM_GENERATED_VALUE 0xff544347
#define TPM_ST_ATTEST_QUOTE 0x8018
#define SHA256_DIGEST_LENGTH 32

/* Спрощена структура події логу завантаження */
typedef struct {
    uint32_t pcr_index;
    uint8_t digest[SHA256_DIGEST_LENGTH];
    char event_name[64];
} BootEvent;

/* Результат покрокової верифікації */
typedef struct {
    bool magic_valid;
    bool type_valid;
    bool nonce_valid;
    bool signature_valid;
    bool pcr_match;
} VerificationResult;

/* Функція симуляції розширення регістра PCR: PCR = SHA256(PCR || Digest) */
static void pcr_extend_sha256(uint8_t pcr[SHA256_DIGEST_LENGTH], const uint8_t event_digest[SHA256_DIGEST_LENGTH]) {
    uint8_t buffer[SHA256_DIGEST_LENGTH * 2];
    memcpy(buffer, pcr, SHA256_DIGEST_LENGTH);
    memcpy(buffer + SHA256_DIGEST_LENGTH, event_digest, SHA256_DIGEST_LENGTH);

    SHA256(buffer, sizeof(buffer), pcr);
}

/* Перевірка криптографічного підпису за допомогою OpenSSL EVP */
static bool verify_signature(EVP_PKEY *ak_pubkey, const uint8_t *data, size_t data_len,
                            const uint8_t *sig, size_t sig_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) return false;

    bool valid = false;
    if (EVP_DigestVerifyInit(ctx, NULL, EVP_sha256(), NULL, ak_pubkey) == 1) {
        if (EVP_DigestVerifyUpdate(ctx, data, data_len) == 1) {
            if (EVP_DigestVerifyFinal(ctx, sig, sig_len) == 1) {
                valid = true;
            }
        }
    }

    EVP_MD_CTX_free(ctx);
    return valid;
}

/* Головна функція аналізу цитати та журналу подій */
VerificationResult verify_tpm2_quote(
    const uint8_t *attest_buf, size_t attest_len,
    uint32_t magic, uint16_t type,
    const uint8_t *extra_data, size_t extra_data_len,
    const uint8_t *quoted_pcr_digest,
    const uint8_t *signature, size_t sig_len,
    EVP_PKEY *ak_pubkey,
    const uint8_t *expected_nonce, size_t nonce_len,
    const BootEvent *events, size_t event_count)
{
    VerificationResult res = {0};

    /* 1. Перевірка магічних констант заголовка */
    res.magic_valid = (magic == TPM_GENERATED_VALUE);
    res.type_valid = (type == TPM_ST_ATTEST_QUOTE);

    /* 2. Перевірка свіжості виклику (Nonce) */
    if (extra_data_len == nonce_len && memcmp(extra_data, expected_nonce, nonce_len) == 0) {
        res.nonce_valid = true;
    }

    /* 3. Перевірка цифрового підпису AK над бінарним буфером цитати */
    if (ak_pubkey && signature && sig_len > 0) {
        res.signature_valid = verify_signature(ak_pubkey, attest_buf, attest_len, signature, sig_len);
    }

    /* 4. Відтворення журналу подій для регістра PCR[0] */
    uint8_t simulated_pcr0[SHA256_DIGEST_LENGTH] = {0};
    for (size_t i = 0; i < event_count; i++) {
        if (events[i].pcr_index == 0) {
            pcr_extend_sha256(simulated_pcr0, events[i].digest);
        }
    }

    /* Порівняння відтвореного PCR[0] із підписаним значенням у цитаті */
    if (memcmp(simulated_pcr0, quoted_pcr_digest, SHA256_DIGEST_LENGTH) == 0) {
        res.pcr_match = true;
    }

    return res;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/sha.h>

inline constexpr uint32_t TPM_GENERATED_VALUE = 0xff544347;
inline constexpr uint16_t TPM_ST_ATTEST_QUOTE = 0x8018;
inline constexpr size_t SHA256_LEN = 32;

using Sha256Digest = std::array<uint8_t, SHA256_LEN>;

struct BootEvent {
    uint32_t pcr_index;
    Sha256Digest digest;
    std::string event_name;
};

/* RAII-обгортка для автоматичного керування життєвим циклом контексту OpenSSL */
struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const noexcept {
        if (ctx) EVP_MD_CTX_free(ctx);
    }
};
using UniqueEvpMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

class Tpm2QuoteVerifier {
public:
    static Sha256Digest extend_pcr(const Sha256Digest& current_pcr, const Sha256Digest& event_digest) noexcept {
        std::array<uint8_t, SHA256_LEN * 2> buffer{};
        std::memcpy(buffer.data(), current_pcr.data(), SHA256_LEN);
        std::memcpy(buffer.data() + SHA256_LEN, event_digest.data(), SHA256_LEN);

        Sha256Digest next_pcr{};
        SHA256(buffer.data(), buffer.size(), next_pcr.data());
        return next_pcr;
    }

    static bool verify_signature(
        EVP_PKEY* ak_pubkey,
        std::span<const uint8_t> data,
        std::span<const uint8_t> signature) noexcept
    {
        if (!ak_pubkey) return false;

        UniqueEvpMdCtx ctx(EVP_MD_CTX_new());
        if (!ctx) return false;

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, ak_pubkey) != 1) {
            return false;
        }
        if (EVP_DigestVerifyUpdate(ctx.get(), data.data(), data.size()) != 1) {
            return false;
        }
        return EVP_DigestVerifyFinal(ctx.get(), signature.data(), signature.size()) == 1;
    }

    static std::expected<bool, std::string> verify_attestation(
        std::span<const uint8_t> raw_attest_buf,
        uint32_t magic,
        uint16_t type,
        std::span<const uint8_t> extra_data,
        const Sha256Digest& quoted_pcr_digest,
        std::span<const uint8_t> signature,
        EVP_PKEY* ak_pubkey,
        std::span<const uint8_t> expected_nonce,
        std::span<const BootEvent> event_log)
    {
        if (magic != TPM_GENERATED_VALUE) {
            return std::unexpected("Недійсне магічне число TPM");
        }
        if (type != TPM_ST_ATTEST_QUOTE) {
            return std::unexpected("Тип структури не є TPM_ST_ATTEST_QUOTE");
        }
        if (extra_data.size() != expected_nonce.size() ||
            !std::equal(extra_data.begin(), extra_data.end(), expected_nonce.begin())) {
            return std::unexpected("Невідповідність Nonce: можлива атака повторного відтворення");
        }

        if (!verify_signature(ak_pubkey, raw_attest_buf, signature)) {
            return std::unexpected("Криптографічний підпис AK недійсний");
        }

        /* Відтворення стану регістра PCR[0] */
        Sha256Digest simulated_pcr0{};
        for (const auto& ev : event_log) {
            if (ev.pcr_index == 0) {
                simulated_pcr0 = extend_pcr(simulated_pcr0, ev.digest);
            }
        }

        if (simulated_pcr0 != quoted_pcr_digest) {
            return std::unexpected("Розбіжність PCR: журнал завантаження не відповідає підписаному стану чипа");
        }

        return true;
    }
};
```
:::

## 3. Детальний розбір інженерних пасток та вразливостей

Під час розробки та промислової експлуатації систем віддаленої атестації інженери найчастіше стикаються з чотирма категоріями неочевидних помилок:

### 1. Порядок байтів (Endianness) у бінарних структурах TPM

Специфікація TCG визначає, що всі цілочисельні типи даних у структурах TPM 2.0 серіалізуються суворо у форматі Big-Endian (мережевий порядок байтів). Якщо сервер-верифікатор розгорнуто на архітектурі x86_64 або ARM64 (Little-Endian) і парсер виконує пряме приведення покажчиків до структур C без виклику функцій перетворення `ntohl()` або `be32toh()`, значення полів спотворюються:

```
Значення в мережі (Big-Endian):   0xFF 0x54 0x43 0x47  (TPM_GENERATED_VALUE)
Зчитано як uint32_t на x86_64:    0x47 0x43 0x54 0xFF  (Хибна помилка недійсної структури)
```

Будь-який низькорівневий парсер повинен явно десеріалізувати кожен скалярний заголовок за допомогою бітових зсувів або функцій конвертації порядку байтів.

### 2. Атака усічення журналу (Log Truncation Attack)

Журнал подій TCG Event Log зберігається у звичайній оперативній пам'яті операційної системи (`/sys/kernel/security/tpm0/binary_bios_measurements`). Якщо зловмисник отримав root-доступ до хоста після завантаження, він не може змінити апаратний регістр PCR у чипі TPM, оскільки операція `TPM2_PCR_Extend` є незворотною. Проте зловмисник має повний доступ до читання та редагування файлу журналу подій.

Якщо верифікатор реалізує спрощену логіку перевірки — наприклад, лише сканує список подій у журналі на наявність заборонених бінарних файлів, але не виконує операцію повного відтворення `pcr_extend` з подальшим звірянням із `pcrDigest` цитати, зловмисник може просто видалити запис про завантаження шкідливого модуля ядра з логу. Верифікатор побачить «чистий» лог і помилково визнає вузол безпечним. Звіряння відтвореного значення з апаратно підписаною цитатою є безальтернативною умовою.

### 3. Невідповідність банків гешування (Crypto Bank Mismatch)

Сучасні пристрої TPM 2.0 підтримують одночасне ведення декількох паралельних банків PCR: SHA-1, SHA-256 та SHA-384. При формуванні виклику верифікатор повинен явно передавати бітову маску `TPML_PCR_SELECTION`, вказуючи ідентифікатор алгоритму `TPM_ALG_SHA256`. Якщо клієнт надішле цитату, підписану для банку SHA-1 (де довжина геша становить 20 байтів замість 32), а верифікатор спробує зіставити її з 32-байтним відтвореним дайджестом, виникне збій перевірки цілісності або читання за межами виділеного буфера.

### 4. Контроль перезапусків через `TPMS_CLOCK_INFO`

Структура `TPMS_ATTEST` містить внутрішній лічильник `clockInfo.resetCount`, який збільшується на одиницю при кожному скиданні живлення чипа, та лічильник `restartCount`, що відстежує м'які перезавантаження операційної системи.

Якщо верифікатор веде базу даних стану клієнтських вузлів, він зобов'язаний зберігати останнє зафіксоване значення `resetCount`. Якщо клієнт надсилає свіжу цитату з валідним nonce, але значення `resetCount` зменшилося (або залишилося незмінним після зафіксованого апаратного перезавантаження вузла), це однозначно вказує на атаку підміни: запуск системи у віртуальній машині зі знімка стану (snapshot restore) або спробу перехоплення ідентичності клонованим програмним емулятором vTPM.

Крім того, значення часу `clockInfo.clock` монотонно зростає під час активної роботи чипа. Верифікатор порівнює приріст часу між послідовними цитатами з інтервалом між мережевими опитуваннями, виявляючи аномальні уповільнення або спроби заморожування віртуальної машини для проведення атак на пам'ять.
