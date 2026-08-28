# 📋 Інтерфейси стеку TSS2: специфікація ESAPI, FAPI та командний інструментарій

Програмний стек TSS2 (TPM2 Software Stack), розроблений консорціумом TCG, описує стандартизований набір бібліотек C API та утиліт командного рядка для взаємодії з модулями TPM 2.0. Усі заголовочні файли поставляються у системному пакеті `libtss2-dev` (включаючи `tss2_esys.h`, `tss2_fapi.h`, `tss2_tctildr.h`, `tss2_rc.h`).

Стек побудовано за модульним принципом, де кожен шар надає свій рівень абстракції — від низькорівневої передачі бінарних кадрів через TCTI до високорівневого управління об'єктами за допомогою JSON-профілів FAPI.

## 1. Системний шар передачі команд: TCTI API

TCTI (TPM Command Transmission Interface) є найнижчим шаром стеку TSS2, який приховує деталі транспортного зв'язку з апаратним або програмним TPM. Замість прямого відкриття файлів пристроїв програми взаємодіють з TCTI-контекстом `TSS2_TCTI_CONTEXT`.

### Механізм динамічного завантаження TCTI (`tss2_tctildr.h`)

Бібліотека-завантажувач TCTI Ldr дозволяє динамічно підключати потрібний транспортний модуль під час виконання за рядком конфігурації виду `"назва:опції"`.

:::tabs
```c
TSS2_RC Tss2_TctiLdr_Initialize(
    const char *name, 
    TSS2_TCTI_CONTEXT **tcti
);

void Tss2_TctiLdr_Finalize(
    TSS2_TCTI_CONTEXT **tcti
);
```
:::code api-tss2-esapi/cpp/mekhanizm-dynamichnoho.cpp
:::

#### Доступні плагіни транспорту TCTI

- **`"device"` (`libtss2-tcti-device.so`):** Пряма передача байтових масивів у символьний пристрій ядра. Якщо вказано `"device:/dev/tpmrm0"`, записи спрямовуються до вбудованого менеджера ресурсів ядра. Якщо вказано `"device:/dev/tpm0"`, виклики йдуть безпосередньо в апаратний чип.
- **`"tabrmd"` (`libtss2-tcti-tabrmd.so`):** Передача команд через системну шину D-Bus до користувацького демона менеджера ресурсів `tpm2-abrmd`.
- **`"mssim"` (`libtss2-tcti-mssim.so`):** Мережеве підключення через TCP-сокети до програмного емулятора TPM 2.0 (за замовчуванням порти 2321 та 2322).

Якщо у функцію `Tss2_TctiLdr_Initialize` передати значення `NULL`, завантажувач по черзі пробує стандартні транспорти: демон `tpm2-abrmd`, далі пристрої `/dev/tpmrm0` і `/dev/tpm0`, і насамкінець мережевий емулятор mssim.

## 2. Розширений системний API: ESAPI (`tss2_esys.h`)

ESAPI (Enhanced System API) пропонує розробникам повний контроль над внутрішніми операціями TPM 2.0 і водночас бере на себе автоматичне управління криптографічними сесіями авторизації, обчислення HMAC-підписів для параметрів команд та шифрування трафіку шини.

### Концепція ресурсових дескрипторів ESAPI (`ESYS_TR`)

На відміну від низькорівневих числових дескрипторів TPM (`TPM2_HANDLE`), ESAPI оперує віртуальними ресурсовими дескрипторами `ESYS_TR`. Дескриптор `ESYS_TR` обгортає не лише числовий покажчик об'єкта в TPM, але й збережені дані авторизації (паролі, симетричні ключі сесій), шифровані назви об'єктів (Names) та атрибути безпеки.

Існують визначені константи `ESYS_TR`:
- `ESYS_TR_NONE`: Відсутність ресурсу або сесії.
- `ESYS_TR_PASSWORD`: Авторизація за допомогою відкритого пароля (Null Auth або конкретне значення).
- `ESYS_TR_RH_OWNER`: Owner ієрархія.
- `ESYS_TR_RH_ENDORSEMENT`: Endorsement ієрархія.
- `ESYS_TR_RH_NULL`: Ефемерна Null ієрархія.

Це саме `ESYS_TR`-константи, а не числові дескриптори специфікації (`TPM2_RH_OWNER`, `TPM2_RH_ENDORSEMENT`, `TPM2_RH_NULL`): специфікаційне значення, передане у функцію ESAPI, дає помилку невідомого ресурсу.

### Управління системним контекстом ESAPI

Для виконання будь-яких криптографічних операцій необхідно створити головний контекст `ESYS_CONTEXT`, прив'язаний до ініціалізованого транспорту TCTI.

:::tabs
```c
TSS2_RC Esys_Initialize(
    ESYS_CONTEXT **esys_context,
    TSS2_TCTI_CONTEXT *tcti,
    TSS2_ABI_VERSION *abiVersion
);

void Esys_Finalize(
    ESYS_CONTEXT **esys_context
);
```
```cpp
#include <memory>
#include <tss2/tss2_esys.h>

struct EsysDeleter {
    void operator()(ESYS_CONTEXT* ctx) const noexcept {
        if (ctx) Esys_Finalize(&ctx);
    }
};
using EsysContextPtr = std::unique_ptr<ESYS_CONTEXT, EsysDeleter>;
```
:::

### Генерація первинного ключа (`Esys_CreatePrimary`)

Функція `Esys_CreatePrimary` створює первинний ключ в обраній ієрархії на основі її детермінованого зерна (Primary Seed) та переданого шаблону криптографічних параметрів `TPM2B_PUBLIC`.

:::tabs
:::code api-tss2-esapi/c/heneratsiia-pervynnoho.c
:::code api-tss2-esapi/cpp/heneratsiia-pervynnoho.cpp
:::

### Запечатування та розпечатування даних (Sealing / Unsealing)

Операції Sealing в ESAPI реалізуються через створення об'єкта типу `TPM2_ALG_KEYEDHASH` під батьківським первинним ключем. Секретні дані розміщуються у структурі `TPM2B_SENSITIVE_CREATE`.

:::tabs
:::code api-tss2-esapi/c/zapechatuvannia-ta.h
```cpp
// У C++ динамічні структури пам'яті ESAPI вивільняються через std::unique_ptr та Esys_Free
auto freePrivate = [](TPM2B_PRIVATE* p) { Esys_Free(p); };
using UniqueTpmPrivate = std::unique_ptr<TPM2B_PRIVATE, decltype(freePrivate)>;

auto freePublic = [](TPM2B_PUBLIC* p) { Esys_Free(p); };
using UniqueTpmPublic = std::unique_ptr<TPM2B_PUBLIC, decltype(freePublic)>;
```
:::

### Створення та оцінка сесій політик (`Esys_StartAuthSession`, `Esys_PolicyPCR`)

Для розпечатування даних під вимірювання завантаження необхідно розпочати сесію політики `TPM2_SE_POLICY` та оновити її накопичувальний хеш через виклик `Esys_PolicyPCR`.

:::tabs
:::code api-tss2-esapi/c/stvorennia-ta-otsinka.h
```cpp
// У C++ сесія авторизації обгортається в RAII дескриптор, що викликає Esys_FlushContext
ScopedEsysHandle session(esysCtx);
TSS2_RC rc = Esys_StartAuthSession(
    esysCtx, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
    nullptr, TPM2_SE_POLICY, &symDef, TPM2_ALG_SHA256, session.ptr()
);
```
:::

## 3. Специфікація високорівневого API: FAPI (`tss2_fapi.h`)

FAPI (Feature API) виступає найвищим рівнем абстракції TSS2, розробленим для автоматизації рутинних задач криптографічного опису ключів. FAPI використовує профілі конфігурації у форматі JSON (наприклад, `P_RSA2048_SHA256.json`) і замінює байтові дескриптори текстовими шляхами файлової системи.

```
Шляхи об'єктів FAPI:
  "/HS/SRK"                  -> Storage Root Key
  "/HS/SRK/my_luks_key"      -> Запечатаний ключ диска
  "/HE/EK"                   -> Endorsement Key
  "/HE/EK/my_ak_key"         -> Ключ атестації
```

### Основні функції C API FAPI

Конфігураційні профілі FAPI описують деталі криптографічних алгоритмів (довжину ключів, алгоритми гешування, схеми підпису), позбавляючи розробника необхідності заповнювати складні структури `TPM2B_PUBLIC`.

:::tabs
:::code api-tss2-esapi/c/osnovni-funktsii-c-api.h
```cpp
// У C++ високорівневий FAPI контекст обгортається у std::unique_ptr
struct FapiDeleter {
    void operator()(FAPI_CONTEXT* ctx) const noexcept {
        if (ctx) Fapi_Finalize(&ctx);
    }
};
using FapiContextPtr = std::unique_ptr<FAPI_CONTEXT, FapiDeleter>;
```
:::

## 4. Консольний інструментарій `tpm2-tools`

Набір утиліт `tpm2-tools` є консольною обгорткою над ESAPI для використання у скриптах автоматизації та адміністрування Linux. Консольні команди повертають бінарні файли контекстів (`*.ctx`), які містять упаковані дескриптори об'єктів.

### Типовий ланцюжок команд запечатування секрету

:::code api-tss2-esapi/sh/main.sh

### Довідник кодів повернення та помилок стеку TSS2 (`TSS2_RC`)

Коди помилок у стеку TSS2 повертаються у вигляді 32-бітного цілого числа `TSS2_RC`. Найвища частина показує рівень стеку, де виникла помилка (ESAPI, TCTI, FAPI або сам TPM).

- **`TSS2_RC_SUCCESS` (`0x00000000`):** Операція виконана без помилок.
- **`TPM2_RC_INITIALIZE` (`0x00000100`):** TPM не було ініціалізовано або чип вимагає виконання процедури `TPM2_Startup`.
- **`TPM2_RC_FAILURE` (`0x00000101`):** Внутрішня помилка самотестування апаратного чипа TPM.
- **`TPM2_RC_OBJECT_MEMORY`** (попередження групи `RC_WARN`): Нестача внутрішньої пам'яті SRAM чипа для збереження нових об'єктів. Свідчить про використання `/dev/tpm0` замість `/dev/tpmrm0`.
- **`TPM2_RC_PCR_CHANGED`** (помилка групи `RC_VER1`): Значення регістрів PCR змінилися під час виконання дій у рамках сесії політики, авторизацію скасовано.
- **`TSS2_TCTI_RC_IO_ERROR`** (шар TCTI, поле рівня `0x0A`): Помилка вводу-виводу при спробі відправити бінарний кадр у символьний пристрій `/dev/tpmrm0`.

Для аналізу кодів помилок у консолі поставляється утиліта `tpm2_rc_decode` або виклик бібліотечної функції `Tss2_RC_Decode()`, яка декодує 32-бітне число у текстовий рядок із вказівкою компонента та причини відмови.
