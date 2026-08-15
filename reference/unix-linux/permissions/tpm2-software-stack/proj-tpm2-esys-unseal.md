# ⚙️ Практична реалізація Sealing та Unsealing через TSS2 ESAPI

У цій практичній вставці показано завершений приклад програм мовами C та C++, які використовують системні виклики розширеного API стеку TSS2 (`libtss2-esys`) для апаратного запечатування ключів (Sealing) під стан регістрів конфігурації платформи (PCR 0 та PCR 7) та їх подальшого розпечатування (Unsealing).

## Постановка задачі та системні вимоги

Програма виконує роль підсистеми захисту ключів шифрування диска (LUKS2) або критичних токенів доступу. Головна мета — забезпечити ситуацію, за якої майстер-ключ не зберігається на диску у відкритому вигляді, а створюється як запечатаний блоб під захистом апаратного чипа TPM 2.0.

Для успішного запуску прикладу в системі повинні бути встановлені розробницькі пакети бібліотек `libtss2-dev`, `libtss2-esys0`, `libtss2-tctildr0`, а також наявний доступ до внутрішньоядерного менеджера ресурсів `/dev/tpmrm0`.

### Логіка роботи криптографічного алгоритму

Приклад реалізує повний життєвий цикл управління запечатаним об'єктом.

```
+-------------------------------------------------------------------------+
|                        Алгоритм Sealing / Unsealing                      |
|                                                                         |
|  1. Tss2_TctiLdr_Initialize("device:/dev/tpmrm0")                      |
|  2. Esys_Initialize()                                                   |
|  3. Esys_CreatePrimary() -> SRK Handle                                  |
|  4. Esys_StartAuthSession() -> TPM2_SE_POLICY                           |
|  5. Esys_PolicyPCR(PCR 0, 7) -> Update Session Digest                   |
|  6. Esys_Create(Sens, Public) -> Encrypted Private/Public Pair          |
|  7. Esys_Load(Private, Public) -> Loaded Object Handle                  |
|  8. Esys_Unseal(Loaded Object, Policy Session) -> Recovered Plaintext   |
|  9. Esys_FlushContext() -> Release Handles                              |
+-------------------------------------------------------------------------+
```

1. **Ініціалізація транспорту TCTI:** Відкриття з'єднання з пристроєм `/dev/tpmrm0` через завантажувач `tss2-tctildr` та створення контексту `ESYS_CONTEXT`.
2. **Генерація первинного ключа (Primary Key):** Створення первинного асиметричного ключа RSA-2048 в ієрархії `TPM2_RH_OWNER` на основі детермінованого зерна Primary Seed.
3. **Відкриття сесії політики (Policy Session):** Запуск сесії авторизації типу `TPM2_SE_POLICY` із гешуванням SHA-256.
4. **Фіксація стану регістрів PCR 0 та PCR 7:** Виклик `Esys_PolicyPCR` для додавання поточних підписів завантаження прошивки та Secure Boot до підсумкового `PolicyDigest`.
5. **Запечатування корисного навантаження (Sealing):** Вилучення підсумкового `PolicyDigest` сесії через `Esys_PolicyGetDigest`, запис його у поле `authPolicy` шаблону об'єкта і виклик `Esys_Create` для генерації запечатаного блобу приватної частини `TPM2B_PRIVATE`.
6. **Завантаження та розпечатування (Unseal):** Завантаження приватної/публічної частини у віртуальний простір TPM через `Esys_Load` та вилучення вихідного секрету через `Esys_Unseal` за умови успішного проходження перевірки стану PCR у сесії.
7. **Безпечне вивантаження:** Очищення та скидання дескрипторів пам'яті через `Esys_FlushContext` для запобігання витоку ресурсів у менеджері ресурсів.

## Реалізація мовами C та C++

Нижче наведено два повні, незалежні варіанти реалізації цієї задачі. Перша вкладка демонструє процедурний підхід мовою C із явним викликом точок очищення `goto cleanup`. Друга вкладка показує сучасний ідіоматичний стандарт C++20 із застосуванням RAII-обгорток, шаблонів вилучення ресурсів `std::unique_ptr` та безпечною обробкою винятків.

:::tabs
```c
/* tpm2_seal_lab.c — Приклад Sealing/Unsealing мовою C з очищенням ресурсів */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tctildr.h>

#define CHECK_RC(rc, msg) \
    do { \
        if ((rc) != TSS2_RC_SUCCESS) { \
            fprintf(stderr, "[ПОМИЛКА] %s: 0x%08x\n", (msg), (rc)); \
            goto cleanup; \
        } \
    } while (0)

int main(void) {
    TSS2_RC rc = TSS2_RC_SUCCESS;
    TSS2_TCTI_CONTEXT *tcti_ctx = NULL;
    ESYS_CONTEXT *esys_ctx = NULL;
    ESYS_TR primary_handle = ESYS_TR_NONE;
    ESYS_TR session_handle = ESYS_TR_NONE;
    ESYS_TR loaded_key_handle = ESYS_TR_NONE;

    TPM2B_PRIVATE *out_private = NULL;
    TPM2B_PUBLIC *out_public = NULL;
    TPM2B_SENSITIVE_DATA *unsealed_data = NULL;
    TPM2B_DIGEST *policy_digest = NULL;

    printf("[+] Ініціалізація TCTI та контексту ESAPI...\n");
    rc = Tss2_TctiLdr_Initialize("device:/dev/tpmrm0", &tcti_ctx);
    CHECK_RC(rc, "Неможливо відкрити /dev/tpmrm0");

    rc = Esys_Initialize(&esys_ctx, tcti_ctx, NULL);
    CHECK_RC(rc, "Помилка ініціалізації Esys_Initialize");

    /* 1. Створення Primary Key у Owner ієрархії */
    TPM2B_PUBLIC in_public_primary = {
        .size = 0,
        .publicArea = {
            .type = TPM2_ALG_RSA,
            .nameAlg = TPM2_ALG_SHA256,
            .objectAttributes = (TPMA_OBJECT_USERWITHAUTH |
                                 TPMA_OBJECT_RESTRICTED |
                                 TPMA_OBJECT_DECRYPT |
                                 TPMA_OBJECT_FIXEDTPM |
                                 TPMA_OBJECT_FIXEDPARENT),
            .authPolicy = { .size = 0 },
            .parameters.rsaDetail = {
                .symmetric = {
                    .algorithm = TPM2_ALG_AES,
                    .keyBits.aes = 128,
                    .mode.aes = TPM2_ALG_CFB
                },
                .scheme = { .scheme = TPM2_ALG_NULL },
                .keyBits = 2048,
                .exponent = 0
            },
            .unique.rsa = { .size = 0 }
        }
    };

    printf("[+] Генерація Primary Key в ієрархії TPM2_RH_OWNER...\n");
    rc = Esys_CreatePrimary(
        esys_ctx, ESYS_TR_RH_OWNER,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        &in_public_primary, NULL, NULL,
        &primary_handle, NULL, NULL, NULL, NULL
    );
    CHECK_RC(rc, "Помилка виклику Esys_CreatePrimary");

    /* 2. Відкриття авторизаційної сесії політики */
    printf("[+] Відкриття авторизаційної сесії TPM2_SE_POLICY...\n");
    TPMT_SYM_DEF symmetric_def = {
        .algorithm = TPM2_ALG_NULL
    };
    rc = Esys_StartAuthSession(
        esys_ctx, ESYS_TR_NONE, ESYS_TR_NONE,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        NULL, TPM2_SE_POLICY, &symmetric_def, TPM2_ALG_SHA256,
        &session_handle
    );
    CHECK_RC(rc, "Помилка створення сесії політики");

    /* 3. Оцінка регістрів PCR 0 та PCR 7 у сесії */
    TPML_PCR_SELECTION pcr_selection = {
        .count = 1,
        .pcrSelections = {
            {
                .hash = TPM2_ALG_SHA256,
                .sizeofSelect = 3,
                .pcrSelect = { 0x81, 0x00, 0x00 } /* Біти 0 та 7 заповнені */
            }
        }
    };

    printf("[+] Оновлення digest політики через Esys_PolicyPCR (PCR 0, 7)...\n");
    rc = Esys_PolicyPCR(
        esys_ctx, session_handle,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        NULL, &pcr_selection
    );
    CHECK_RC(rc, "Помилка виконання Esys_PolicyPCR");

    /* 3a. Вилучення підсумкового PolicyDigest сесії */
    rc = Esys_PolicyGetDigest(
        esys_ctx, session_handle,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        &policy_digest
    );
    CHECK_RC(rc, "Помилка отримання PolicyDigest");

    /* 4. Запечатування секретних даних під зафіксовану політику */
    const char secret_payload[] = "MasterDiskKey-32-Bytes-Length!";
    TPM2B_SENSITIVE_CREATE in_sensitive = {
        .size = 0,
        .sensitive = {
            .userAuth = { .size = 0 },
            .data = {
                .size = sizeof(secret_payload),
                .buffer = { 0 }
            }
        }
    };
    memcpy(in_sensitive.sensitive.data.buffer, secret_payload, sizeof(secret_payload));

    TPM2B_PUBLIC in_public_seal = {
        .size = 0,
        .publicArea = {
            .type = TPM2_ALG_KEYEDHASH,
            .nameAlg = TPM2_ALG_SHA256,
            .objectAttributes = (TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
            .authPolicy = { .size = 0 },
            .parameters.keyedHashDetail = {
                .scheme = { .scheme = TPM2_ALG_NULL }
            },
            .unique.keyedHash = { .size = 0 }
        }
    };

    /* Прив'язка об'єкта до розрахованої політики: без цього authPolicy порожній
       і об'єкт із знятим USERWITHAUTH не авторизується взагалі. */
    in_public_seal.publicArea.authPolicy = *policy_digest;

    printf("[+] Створення запечатаного об'єкта в TPM...\n");
    rc = Esys_Create(
        esys_ctx, primary_handle,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        &in_sensitive, &in_public_seal, NULL, NULL,
        &out_private, &out_public, NULL, NULL, NULL
    );
    CHECK_RC(rc, "Помилка запечатування секрету в Esys_Create");

    /* 5. Завантаження запечатаного об'єкта та виконання Unseal */
    rc = Esys_Load(
        esys_ctx, primary_handle,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        out_private, out_public, &loaded_key_handle
    );
    CHECK_RC(rc, "Помилка завантаження запечатаного об'єкта");

    printf("[+] Виконання Esys_Unseal з використанням сесії політики...\n");
    rc = Esys_Unseal(
        esys_ctx, loaded_key_handle,
        session_handle, ESYS_TR_NONE, ESYS_TR_NONE,
        &unsealed_data
    );
    CHECK_RC(rc, "Помилка розпечатування даних (Unseal)");

    printf("[УСПІХ] Розпечатаний секрет: \"%s\"\n", unsealed_data->buffer);

cleanup:
    if (unsealed_data) Esys_Free(unsealed_data);
    if (policy_digest) Esys_Free(policy_digest);
    if (out_private) Esys_Free(out_private);
    if (out_public) Esys_Free(out_public);

    if (loaded_key_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, loaded_key_handle);
    if (session_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, session_handle);
    if (primary_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, primary_handle);

    if (esys_ctx) Esys_Finalize(&esys_ctx);
    if (tcti_ctx) Tss2_TctiLdr_Finalize(&tcti_ctx);

    return (rc == TSS2_RC_SUCCESS) ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
// tpm2_seal_lab.cpp — Ідіоматична реалізація C++20 з використанням RAII та шаблонів
#include <iostream>
#include <algorithm>
#include <memory>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <stdexcept>
#include <format>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tctildr.h>

namespace tpm2 {

// RAII обгортки для автоматичного очищення контекстів TCTI та ESAPI
struct TctiDeleter {
    void operator()(TSS2_TCTI_CONTEXT* ctx) const noexcept {
        if (ctx) Tss2_TctiLdr_Finalize(&ctx);
    }
};
using TctiContextPtr = std::unique_ptr<TSS2_TCTI_CONTEXT, TctiDeleter>;

struct EsysDeleter {
    void operator()(ESYS_CONTEXT* ctx) const noexcept {
        if (ctx) Esys_Finalize(&ctx);
    }
};
using EsysContextPtr = std::unique_ptr<ESYS_CONTEXT, EsysDeleter>;

// RAII обгортка для тимчасових handles об'єктів TPM
class ScopedEsysHandle {
public:
    ScopedEsysHandle(ESYS_CONTEXT* esysCtx, ESYS_TR handle = ESYS_TR_NONE) noexcept
        : m_ctx(esysCtx), m_handle(handle) {}

    ~ScopedEsysHandle() {
        if (m_ctx && m_handle != ESYS_TR_NONE) {
            Esys_FlushContext(m_ctx, m_handle);
        }
    }

    ScopedEsysHandle(const ScopedEsysHandle&) = delete;
    ScopedEsysHandle& operator=(const ScopedEsysHandle&) = delete;

    ScopedEsysHandle(ScopedEsysHandle&& other) noexcept
        : m_ctx(other.m_ctx), m_handle(other.m_handle) {
        other.m_handle = ESYS_TR_NONE;
    }

    [[nodiscard]] ESYS_TR get() const noexcept { return m_handle; }
    [[nodiscard]] ESYS_TR* ptr() noexcept { return &m_handle; }

private:
    ESYS_CONTEXT* m_ctx{nullptr};
    ESYS_TR m_handle{ESYS_TR_NONE};
};

class Tpm2Session {
public:
    explicit Tpm2Session(const std::string& tctiName = "device:/dev/tpmrm0") {
        TSS2_TCTI_CONTEXT* tctiRaw = nullptr;
        TSS2_RC rc = Tss2_TctiLdr_Initialize(tctiName.c_str(), &tctiRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Не вдалося відкрити TCTI: 0x{:08x}", rc));
        }
        m_tcti.reset(tctiRaw);

        ESYS_CONTEXT* esysRaw = nullptr;
        rc = Esys_Initialize(&esysRaw, m_tcti.get(), nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Помилка Esys_Initialize: 0x{:08x}", rc));
        }
        m_esys.reset(esysRaw);
    }

    [[nodiscard]] ESYS_CONTEXT* getContext() const noexcept { return m_esys.get(); }

    std::vector<uint8_t> sealAndUnseal(std::span<const uint8_t> secretData) {
        ESYS_CONTEXT* ctx = m_esys.get();

        // 1. Створення Primary Key
        ScopedEsysHandle primaryKey(ctx);
        TPM2B_PUBLIC primaryTemplate{
            .size = 0,
            .publicArea = {
                .type = TPM2_ALG_RSA,
                .nameAlg = TPM2_ALG_SHA256,
                .objectAttributes = (TPMA_OBJECT_USERWITHAUTH | TPMA_OBJECT_RESTRICTED |
                                     TPMA_OBJECT_DECRYPT | TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
                .parameters = { .rsaDetail = {
                    .symmetric = { .algorithm = TPM2_ALG_AES, .keyBits = { .aes = 128 }, .mode = { .aes = TPM2_ALG_CFB } },
                    .scheme = { .scheme = TPM2_ALG_NULL },
                    .keyBits = 2048, .exponent = 0
                }}
            }
        };

        TSS2_RC rc = Esys_CreatePrimary(ctx, ESYS_TR_RH_OWNER, ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                                        &primaryTemplate, nullptr, nullptr, primaryKey.ptr(), nullptr, nullptr, nullptr, nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_CreatePrimary помилка: 0x{:08x}", rc));
        }

        // 2. Ініціалізація сесії політики PCR
        ScopedEsysHandle policySession(ctx);
        TPMT_SYM_DEF symDef{ .algorithm = TPM2_ALG_NULL };
        rc = Esys_StartAuthSession(ctx, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
                                   nullptr, TPM2_SE_POLICY, &symDef, TPM2_ALG_SHA256, policySession.ptr());
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_StartAuthSession помилка: 0x{:08x}", rc));
        }

        TPML_PCR_SELECTION pcrSel{
            .count = 1,
            .pcrSelections = { {{ .hash = TPM2_ALG_SHA256, .sizeofSelect = 3, .pcrSelect = { 0x81, 0x00, 0x00 } }} }
        };
        rc = Esys_PolicyPCR(ctx, policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, nullptr, &pcrSel);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_PolicyPCR помилка: 0x{:08x}", rc));
        }

        TPM2B_DIGEST* policyDigestRaw = nullptr;
        rc = Esys_PolicyGetDigest(ctx, policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, &policyDigestRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_PolicyGetDigest помилка: 0x{:08x}", rc));
        }
        std::unique_ptr<TPM2B_DIGEST, decltype([](auto* p){ Esys_Free(p); })> policyDigest(policyDigestRaw);

        // 3. Запечатування секрету
        TPM2B_SENSITIVE_CREATE sensitiveData{};
        if (secretData.size() > sizeof(sensitiveData.sensitive.data.buffer)) {
            throw std::runtime_error("Секрет не вміщається у TPM2B_SENSITIVE_DATA");
        }
        sensitiveData.sensitive.data.size = static_cast<UINT16>(secretData.size());
        std::copy(secretData.begin(), secretData.end(), sensitiveData.sensitive.data.buffer);

        TPM2B_PUBLIC sealTemplate{
            .size = 0,
            .publicArea = {
                .type = TPM2_ALG_KEYEDHASH,
                .nameAlg = TPM2_ALG_SHA256,
                .objectAttributes = (TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
                .parameters = { .keyedHashDetail = { .scheme = { .scheme = TPM2_ALG_NULL } } }
            }
        };

        sealTemplate.publicArea.authPolicy = *policyDigest;

        TPM2B_PRIVATE* outPrivateRaw = nullptr;
        TPM2B_PUBLIC* outPublicRaw = nullptr;
        rc = Esys_Create(ctx, primaryKey.get(), ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                         &sensitiveData, &sealTemplate, nullptr, nullptr, &outPrivateRaw, &outPublicRaw, nullptr, nullptr, nullptr);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Create seal помилка: 0x{:08x}", rc));
        }

        std::unique_ptr<TPM2B_PRIVATE, decltype([](auto* p){ Esys_Free(p); })> outPriv(outPrivateRaw);
        std::unique_ptr<TPM2B_PUBLIC, decltype([](auto* p){ Esys_Free(p); })> outPub(outPublicRaw);

        // 4. Завантаження та Unseal
        ScopedEsysHandle loadedObject(ctx);
        rc = Esys_Load(ctx, primaryKey.get(), ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
                       outPriv.get(), outPub.get(), loadedObject.ptr());
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Load помилка: 0x{:08x}", rc));
        }

        TPM2B_SENSITIVE_DATA* unsealedRaw = nullptr;
        rc = Esys_Unseal(ctx, loadedObject.get(), policySession.get(), ESYS_TR_NONE, ESYS_TR_NONE, &unsealedRaw);
        if (rc != TSS2_RC_SUCCESS) {
            throw std::runtime_error(std::format("Esys_Unseal помилка: 0x{:08x}", rc));
        }

        std::unique_ptr<TPM2B_SENSITIVE_DATA, decltype([](auto* p){ Esys_Free(p); })> unsealedPtr(unsealedRaw);
        return {unsealedPtr->buffer, unsealedPtr->buffer + unsealedPtr->size};
    }

private:
    TctiContextPtr m_tcti;
    EsysContextPtr m_esys;
};

} // namespace tpm2

int main() {
    try {
        tpm2::Tpm2Session session("device:/dev/tpmrm0");
        std::string secretText = "Cxx20-Secure-LUKS-MasterKey";
        std::span<const uint8_t> payload(reinterpret_cast<const uint8_t*>(secretText.data()), secretText.size() + 1);

        std::cout << "[+] Виконання Sealing & Unsealing через C++ RAII...\n";
        auto result = session.sealAndUnseal(payload);

        std::cout << "[УСПІХ] Розпечатаний секрет: \"" << reinterpret_cast<const char*>(result.data()) << "\"\n";
    } catch (const std::exception& ex) {
        std::cerr << "[КРИТИЧНА ПОМИЛКА] " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Відстеження викликів та простеження ядра Linux

Під час виконання програми виклики бібліотеки ESAPI транслюються у серію транзакцій запису та читання символьного пристрою `/dev/tpmrm0`. Для трасування викликів та перевірки коректності роботи менеджера ресурсів у системі Linux можна скористатися інструментами `strace` та підсистемою `ftrace`.

### Аналіз викликів за допомогою `strace`

Команда розширеного аналізу показує порядок взаємодії з дескриптором пристрою:

```bash
strace -e trace=openat,write,read,ioctl ./tpm2_seal_lab
```

У журналі системних викликів можна спостерігати:
1. `openat(AT_FDCWD, "/dev/tpmrm0", O_RDWR)` — повертає файловий дескриптор пристрою.
2. `write(fd, "\x80\x02\x00\x00\x00...", 64)` — відправка бінарного кадру виклику `TPM2_CreatePrimary`.
3. `read(fd, "\x80\x02\x00\x00\x00...", 4096)` — отримання відповіді від TPM із новим дескриптором об'єкта.

### Трасування подій ядра через `ftrace`

Ядро Linux надає точки трасування для підсистеми TPM у `/sys/kernel/tracing/events/tpm/`. Для активації аналізу передачі кадрів виконуються наступні команди:

```bash
# Вмикаємо трасування подій викликів TPM
echo 1 | sudo tee /sys/kernel/tracing/events/tpm/tpm_transmit_cmd/enable

# Запускаємо нашу програму
./tpm2_seal_lab

# Зчитуємо системний лог трасування
sudo cat /sys/kernel/tracing/trace | tail -n 20
```

Цей аналіз дозволяє переконатися, що менеджер ресурсів ядра автоматично додає команди `TPM2_ContextSave` та `TPM2_ContextLoad` при виникненні конкуренції за слоти пам'яті SRAM чипа.

## Аналіз архітектурних рішень та пасток реалізації

> 🔧 **Навіщо це.** Безпосередня розробка системного ПЗ мовами C або C++ із залученням ESAPI дає змогу виключити залежності від сторонніх утиліт командного рядка у продуктивному середовищі, знизити накладні витрати на створення нових процесів та зафіксувати точний контроль над кожним кроком сесії політики.

### Переваги застосування C++ RAII над C-стилем

1. **Гарантоване скидання контекстів (`Esys_FlushContext`):** У реалізації C будь-яке дострокове повернення через ручну обробку помилок вимагає блоку `goto cleanup`. Якщо розробник забуде виклики `Esys_FlushContext`, ресурси в SRAM TPM або менеджера ресурсів будуть вичерпані. У C++ клас `ScopedEsysHandle` гарантує виклики `Esys_FlushContext` при виході з області видимості, включаючи розгортання стека під час генерування винятків `std::runtime_error`.
2. **Управління динамічною пам'яттю ESAPI (`Esys_Free`):** Функції ESAPI виділяють вихідні структури `TPM2B_PUBLIC`, `TPM2B_PRIVATE` та `TPM2B_SENSITIVE_DATA` за допомогою системного `malloc`. Використання `std::unique_ptr` із власними deleter-лямбдами виключає витоки пам'яті в демонах із тривалим часом виконання.
3. **Типобезпека даних (`std::span` та `std::string_view`):** Заміна сирих покажчиків `const char*` та `size_t` на сучасні концепції `std::span` мінімізує ризики переповнення буфера при роботі з секретними бінарними ключами.

### Практичні пастки під час роботи з ESAPI

- **Невірне вказування `pcrSelect`:** Передача невірного значення розміру масиву `sizeofSelect` або бітової маски призведе до того, що підсумковий `PolicyDigest` не збігатиметься з розрахованим значенням у TPM, і виклики `Esys_Unseal` повертатимуть помилку `TPM2_RC_PCR_CHANGED`.
- **Захист конфіденційної пам'яті:** Буфери `TPM2B_SENSITIVE_DATA`, що містять розпечатані ключі шифрування диска, не повинні вивантажуватися на swap-розділ диска. Рекомендується застосовувати системні виклики `mlock()` для блокування сторінок пам'яті в RAM та їх очищення через `explicit_bzero` перед звільненням.
- **Шифрування параметрів на шині:** Якщо дані передаються через незашифровану шину SPI, виклики `Esys_StartAuthSession` повинні налаштовувати симетричний алгоритм шифрування сесії (наприклад, `TPM2_ALG_AES`), щоб зашифрувати вихідні результати `Esys_Unseal` до їх передачі по фізичних провідниках.
