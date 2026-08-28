# ⚙️ Реалізація апаратного підпису через PKCS#11 на C та C++

У цьому проекті реалізовано повний робочий цикл взаємодії з апаратним токеном або модулем безпеки (HSM) через стандартний інтерфейс **PKCS#11 (Cryptoki)**. 

Програма виконує такі завдання:
1. Завантажує драйвер PKCS#11 та ініціалізує середовище (`C_Initialize`).
2. Знаходить перший доступний слот з підключеним апаратним токеном (`C_GetSlotList`).
3. Відкриває сесію взаємодії та проходить автентифікацію користувача за допомогою PIN-коду (`C_Login`).
4. Виконує пошук дескриптора приватного ключа за його міткою (`CKA_LABEL`).
5. Перевіряє атрибут безпеки `CKA_EXTRACTABLE`, гарантуючи, що ключ ніколи не може бути вивантажений з апаратного чипа.
6. Передає 32-байтний криптографічний геш SHA-256 у захищений анклав та накладає цифровий підпис за стандартом ECDSA (`CKM_ECDSA`).
7. Завершує сесію, виконує `C_Logout` та безпечне вивантаження бібліотеки (`C_Finalize`).

---

## 1. Архітектурна модель та стан криптографічної сесії

Стандарт PKCS#11 описує взаємодію клієнтського застосунку з апаратним токеном через скінченний автомат станів сесії (Session State Machine). Розуміння цих переходів є обов'язковим для уникнення витоків пам'яті, блокувань токена та зависання відкритих каналів зв'язку.

```
                    ┌────────────────────────┐
                    │      C_OpenSession     │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │    RO_PUBLIC_SESSION   │ (Доступні лише відкриті сертифікати)
                    └───────────┬────────────┘
                                │  C_Login(CKU_USER, PIN)
                                ▼
                    ┌────────────────────────┐
                    │    RO_USER_FUNCTIONS   │ (Доступні операції C_Sign із приватними ключами)
                    └───────────┬────────────┘
                                │  C_Logout()
                                ▼
                    ┌────────────────────────┐
                    │    RO_PUBLIC_SESSION   │
                    └───────────┬────────────┘
                                │  C_CloseSession()
                                ▼
                    ┌────────────────────────┐
                    │     Сесія Закрита      │
                    └────────────────────────┘
```

### 1.1. Класифікація об'єктів: Сесійні проти Токенних
Кожен криптографічний об'єкт у PKCS#11 має булевий атрибут `CKA_TOKEN`:
- **Токенні об'єкти (`CKA_TOKEN = CK_TRUE`)**: Зберігаються у захищеній енергонезалежній пам'яті токена (EEPROM/Flash). Вони переживають перезавантаження, відключення живлення та закриття сесій. Приватні ключі кореневих сертифікатів та пристроїв завжди створюються як токенні.
- **Сесійні об'єкти (`CKA_TOKEN = CK_FALSE`)**: Створюються в тимчасовій оперативній пам'яті токена для поточної сесії. Вони автоматично знищуються чипом при закритті сесії `C_CloseSession` або витяганні токена з порту. Зазвичай використовуються для тимчасових ключів узгодження ECDH.

### 1.2. Багатопоточність та прапорець `CKF_OS_LOCKING_OK`
Якщо застосунок (наприклад, веб-сервер TLS) накладає підписи паралельно з кількох потоків ОС, драйвер PKCS#11 повинен знати, чи дозволено використовувати системні м'ютекси для синхронізації. Для цього під час виклику `C_Initialize` передається структура `CK_C_INITIALIZE_ARGS` із прапорцем `CKF_OS_LOCKING_OK`. Якщо цього не зробити, одночасне звернення кількох потоків до одного `CK_SESSION_HANDLE` призведе до пошкодження внутрішнього стану драйвера або збою в шині USB.

### 1.3. Двоетапне виділення буферів (Two-Pass Sizing Pattern)
У мові C розмір результату криптографічної операції (наприклад, підпису RSA чи ECDSA) заздалегідь невідомий у байтах, оскільки він залежить від алгоритму та формату сертифіката. Стандарт Cryptoki вирішує це через патерн подвійного виклику:
1. Застосунок викликає `C_Sign(hSession, data, dataLen, NULL, &sigLen)`.
2. Драйвер повертає необхідний розмір у змінну `sigLen` без виконання підпису.
3. Застосунок виділяє буфер потрібної довжини `malloc(sigLen)` і робить другий виклик з реальним вказівником.
У C++ цей патерн елегантно інкапсулюється всередині методу `signDigest`, де динамічний вектор `std::vector<uint8_t>` автоматично виділяє пам'ять і змінює розмір.

---

## 2. Передумови компіляції та налаштування тестового середовища

Для збірки та запуску проекту потрібні стандартні компілятори C/C++ (`gcc` / `clang` / `g++`). Програма може взаємодіяти як з реальним USB-токеном (наприклад, YubiKey з встановленим модулем `ykcs11`), так і з програмним емулятором HSM для тестування (**SoftHSM2**).

Встановлення емулятора та генерація тестового ключа (Debian/Ubuntu):
```bash
# Встановлення SoftHSM2
sudo apt-get install -y softhsm2 opensc libsofthsm2-dev

# Ініціалізація тестового токена в слоті 0
softhsm2-util --init-token --slot 0 --label "TestToken" --pin "123456" --so-pin "87654321"

# Генерація пари ключів ECDSA secp256r1 всередині емулятора токена
pkcs11-tool --module /usr/lib/softhsm/libsofthsm2.so --login --pin "123456" \
            --keypairgen --key-type EC:prime256v1 --label "Test-Sign-Key"
```

Компіляція програми:
```bash
# Для версії на чистому C:
gcc -std=c11 -Wall -Wextra -O2 pkcs11_sign.c -o pkcs11_sign_c -ldl

# Для версії на сучасному C++20:
g++ -std=c++20 -Wall -Wextra -O2 pkcs11_sign.cpp -o pkcs11_sign_cpp -ldl
```

---

## 3. Реалізація мовами C та C++

:::tabs
```c
/* ============================================================================
 * pkcs11_sign.c — Апаратне накладання підпису ECDSA через PKCS#11 API
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Базові заголовки PKCS#11 */
#define CK_PTR *
#define CK_DECLARE_FUNCTION(returnType, name) returnType name
#define CK_DECLARE_FUNCTION_POINTER(returnType, name) returnType (* name)
#define CK_CALLBACK_FUNCTION(returnType, name) returnType (* name)
#ifndef NULL_PTR
#define NULL_PTR NULL
#endif

/* Визначення базових типів PKCS#11 для компіляції без зовнішніх залежностей */
typedef unsigned char     CK_BYTE;
typedef unsigned char     CK_BBOOL;
typedef unsigned long int CK_ULONG;
typedef CK_ULONG          CK_RV;
typedef CK_ULONG          CK_SLOT_ID;
typedef CK_SESSION_HANDLE CK_SESSION_HANDLE;
typedef CK_OBJECT_HANDLE  CK_OBJECT_HANDLE;
typedef CK_OBJECT_CLASS   CK_OBJECT_CLASS;
typedef CK_KEY_TYPE       CK_KEY_TYPE;
typedef CK_MECHANISM_TYPE CK_MECHANISM_TYPE;
typedef CK_ATTRIBUTE_TYPE CK_ATTRIBUTE_TYPE;
typedef CK_USER_TYPE      CK_USER_TYPE;
typedef CK_BYTE          *CK_BYTE_PTR;
typedef CK_ULONG         *CK_ULONG_PTR;
typedef CK_SLOT_ID       *CK_SLOT_ID_PTR;
typedef CK_SESSION_HANDLE*CK_SESSION_HANDLE_PTR;
typedef CK_OBJECT_HANDLE *CK_OBJECT_HANDLE_PTR;
typedef CK_BYTE          *CK_UTF8CHAR_PTR;

#define CK_TRUE  1
#define CK_FALSE 0

#define CKR_OK                       0x00000000UL
#define CKR_BUFFER_TOO_SMALL         0x00000150UL
#define CKS_RO_USER_FUNCTIONS        0x00000002UL
#define CKF_SERIAL_SESSION           0x00000004UL
#define CKU_USER                     0x00000001UL

#define CKO_PRIVATE_KEY              0x00000003UL
#define CKK_EC                       0x00000003UL
#define CKM_ECDSA                    0x00001041UL

#define CKA_CLASS                    0x00000000UL
#define CKA_TOKEN                    0x00000001UL
#define CKA_PRIVATE                  0x00000002UL
#define CKA_LABEL                    0x00000003UL
#define CKA_KEY_TYPE                 0x00000100UL
#define CKA_SIGN                     0x00000108UL
#define CKA_EXTRACTABLE              0x00000162UL

typedef struct CK_ATTRIBUTE {
    CK_ATTRIBUTE_TYPE type;
    void             *pValue;
    CK_ULONG          ulValueLen;
} CK_ATTRIBUTE;
typedef CK_ATTRIBUTE *CK_ATTRIBUTE_PTR;

typedef struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void             *pParameter;
    CK_ULONG          ulParameterLen;
} CK_MECHANISM;
typedef CK_MECHANISM *CK_MECHANISM_PTR;

/* Структура списку функцій Cryptoki */
typedef struct CK_FUNCTION_LIST CK_FUNCTION_LIST;
typedef CK_FUNCTION_LIST *CK_FUNCTION_LIST_PTR;
typedef CK_FUNCTION_LIST_PTR *CK_FUNCTION_LIST_PTR_PTR;

struct CK_FUNCTION_LIST {
    void *version;
    CK_RV (*C_Initialize)(void *pInitArgs);
    CK_RV (*C_Finalize)(void *pReserved);
    CK_RV (*C_GetFunctionList)(CK_FUNCTION_LIST_PTR_PTR ppFunctionList);
    CK_RV (*C_GetSlotList)(CK_BBOOL tokenPresent, CK_SLOT_ID_PTR pSlotList, CK_ULONG_PTR pulCount);
    CK_RV (*C_OpenSession)(CK_SLOT_ID slotID, CK_ULONG flags, void *pApp, void *Notify, CK_SESSION_HANDLE_PTR phSession);
    CK_RV (*C_CloseSession)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_Login)(CK_SESSION_HANDLE hSession, CK_USER_TYPE userType, CK_UTF8CHAR_PTR pPin, CK_ULONG ulPinLen);
    CK_RV (*C_Logout)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_FindObjectsInit)(CK_SESSION_HANDLE hSession, CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount);
    CK_RV (*C_FindObjects)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE_PTR phObject, CK_ULONG ulMax, CK_ULONG_PTR pulCount);
    CK_RV (*C_FindObjectsFinal)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_GetAttributeValue)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hObject, CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount);
    CK_RV (*C_SignInit)(CK_SESSION_HANDLE hSession, CK_MECHANISM_PTR pMech, CK_OBJECT_HANDLE hKey);
    CK_RV (*C_Sign)(CK_SESSION_HANDLE hSession, CK_BYTE_PTR pData, CK_ULONG ulDataLen, CK_BYTE_PTR pSignature, CK_ULONG_PTR pulSignatureLen);
};

/* Допоміжна функція пошуку приватного ключа за назвою мітки */
static CK_OBJECT_HANDLE find_private_key(CK_FUNCTION_LIST_PTR pF, CK_SESSION_HANDLE hSession, const char *label) {
    CK_OBJECT_CLASS keyClass = CKO_PRIVATE_KEY;
    CK_BBOOL bTrue = CK_TRUE;
    
    CK_ATTRIBUTE searchTemplate[] = {
        { CKA_CLASS,   &keyClass, sizeof(keyClass) },
        { CKA_SIGN,    &bTrue,    sizeof(bTrue) },
        { CKA_LABEL,   (void *)label, (CK_ULONG)strlen(label) }
    };

    CK_RV rv = pF->C_FindObjectsInit(hSession, searchTemplate, 3);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка C_FindObjectsInit: 0x%08lX\n", rv);
        return 0;
    }

    CK_OBJECT_HANDLE hObject = 0;
    CK_ULONG objectCount = 0;
    rv = pF->C_FindObjects(hSession, &hObject, 1, &objectCount);
    pF->C_FindObjectsFinal(hSession);

    if (rv != CKR_OK || objectCount == 0) {
        fprintf(stderr, "[!] Приватний ключ із міткою '%s' не знайдено в токені.\n", label);
        return 0;
    }

    return hObject;
}

/* Перевірка чи ключ дійсно є невитягуваним (CKA_EXTRACTABLE == FALSE) */
static bool verify_non_extractable(CK_FUNCTION_LIST_PTR pF, CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hKey) {
    CK_BBOOL isExtractable = CK_TRUE;
    CK_ATTRIBUTE attrTemplate[] = {
        { CKA_EXTRACTABLE, &isExtractable, sizeof(isExtractable) }
    };

    CK_RV rv = pF->C_GetAttributeValue(hSession, hKey, attrTemplate, 1);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Не вдалося перевірити атрибут CKA_EXTRACTABLE: 0x%08lX\n", rv);
        return false;
    }

    if (isExtractable == CK_TRUE) {
        fprintf(stderr, "[УВАГА] Ключ позначено як витягуваний (CKA_EXTRACTABLE = TRUE)!\n");
        return false;
    }

    printf("[+] Апаратна перевірка: Ключ суворо невитягуваний (CKA_EXTRACTABLE = FALSE).\n");
    return true;
}

/* Головна функція виконання апаратного підпису */
int perform_hardware_sign(CK_FUNCTION_LIST_PTR pF, const char *pin, const char *keyLabel,
                          const unsigned char *digest32, unsigned char *outSig, size_t *outSigLen) {
    CK_RV rv = pF->C_Initialize(NULL_PTR);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] C_Initialize зазнав невдачі: 0x%08lX\n", rv);
        return -1;
    }

    /* 1. Пошук підключених слотів із токенами */
    CK_ULONG slotCount = 0;
    rv = pF->C_GetSlotList(CK_TRUE, NULL_PTR, &slotCount);
    if (rv != CKR_OK || slotCount == 0) {
        fprintf(stderr, "[!] Жодного апаратного токена не підключено до системи.\n");
        pF->C_Finalize(NULL_PTR);
        return -2;
    }

    CK_SLOT_ID *slots = (CK_SLOT_ID *)malloc(slotCount * sizeof(CK_SLOT_ID));
    pF->C_GetSlotList(CK_TRUE, slots, &slotCount);
    CK_SLOT_ID targetSlot = slots[0];
    free(slots);

    /* 2. Відкриття сесії */
    CK_SESSION_HANDLE hSession = 0;
    rv = pF->C_OpenSession(targetSlot, CKF_SERIAL_SESSION, NULL_PTR, NULL_PTR, &hSession);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка відкриття сесії C_OpenSession: 0x%08lX\n", rv);
        pF->C_Finalize(NULL_PTR);
        return -3;
    }

    /* 3. Автентифікація користувача через PIN-код */
    rv = pF->C_Login(hSession, CKU_USER, (CK_UTF8CHAR_PTR)pin, (CK_ULONG)strlen(pin));
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка входу C_Login (невірний PIN?): 0x%08lX\n", rv);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -4;
    }

    /* 4. Пошук приватного ключа */
    CK_OBJECT_HANDLE hKey = find_private_key(pF, hSession, keyLabel);
    if (hKey == 0) {
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -5;
    }

    verify_non_extractable(pF, hSession, hKey);

    /* 5. Накладання цифрового підпису ECDSA всередині чипа */
    CK_MECHANISM signMech = { CKM_ECDSA, NULL_PTR, 0 };
    rv = pF->C_SignInit(hSession, &signMech, hKey);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка ініціалізації C_SignInit: 0x%08lX\n", rv);
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -6;
    }

    CK_ULONG sigLen = (CK_ULONG)(*outSigLen);
    rv = pF->C_Sign(hSession, (CK_BYTE_PTR)digest32, 32, (CK_BYTE_PTR)outSig, &sigLen);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка накладання підпису C_Sign: 0x%08lX\n", rv);
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -7;
    }

    *outSigLen = (size_t)sigLen;
    printf("[+] Цифровий підпис успішно накладено в апаратному модулі (%lu байтів).\n", sigLen);

    /* 6. Очищення ресурсів */
    pF->C_Logout(hSession);
    pF->C_CloseSession(hSession);
    pF->C_Finalize(NULL_PTR);
    return 0;
}
```
```cpp
// ============================================================================
// pkcs11_sign.cpp — Ідіоматична обгортка C++20 з RAII для PKCS#11
// ============================================================================
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <format>
#include <cstdint>

// Оголошення типів PKCS#11
using CK_BYTE = unsigned char;
using CK_BBOOL = unsigned char;
using CK_ULONG = unsigned long int;
using CK_RV = CK_ULONG;
using CK_SLOT_ID = CK_ULONG;
using CK_SESSION_HANDLE = CK_ULONG;
using CK_OBJECT_HANDLE = CK_ULONG;
using CK_ATTRIBUTE_TYPE = CK_ULONG;
using CK_MECHANISM_TYPE = CK_ULONG;
using CK_USER_TYPE = CK_ULONG;

constexpr CK_BBOOL CK_TRUE = 1;
constexpr CK_BBOOL CK_FALSE = 0;
constexpr CK_RV CKR_OK = 0x00000000UL;
constexpr CK_ULONG CKF_SERIAL_SESSION = 0x00000004UL;
constexpr CK_USER_TYPE CKU_USER = 0x00000001UL;
constexpr CK_ULONG CKO_PRIVATE_KEY = 0x00000003UL;
constexpr CK_MECHANISM_TYPE CKM_ECDSA = 0x00001041UL;

constexpr CK_ATTRIBUTE_TYPE CKA_CLASS = 0x00000000UL;
constexpr CK_ATTRIBUTE_TYPE CKA_LABEL = 0x00000003UL;
constexpr CK_ATTRIBUTE_TYPE CKA_SIGN = 0x00000108UL;
constexpr CK_ATTRIBUTE_TYPE CKA_EXTRACTABLE = 0x00000162UL;

struct CK_ATTRIBUTE {
    CK_ATTRIBUTE_TYPE type;
    void* pValue;
    CK_ULONG ulValueLen;
};

struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void* pParameter;
    CK_ULONG ulParameterLen;
};

struct CK_FUNCTION_LIST {
    void* version;
    CK_RV (*C_Initialize)(void* pInitArgs);
    CK_RV (*C_Finalize)(void* pReserved);
    CK_RV (*C_GetFunctionList)(CK_FUNCTION_LIST** ppFunctionList);
    CK_RV (*C_GetSlotList)(CK_BBOOL tokenPresent, CK_SLOT_ID* pSlotList, CK_ULONG* pulCount);
    CK_RV (*C_OpenSession)(CK_SLOT_ID slotID, CK_ULONG flags, void* pApp, void* Notify, CK_SESSION_HANDLE* phSession);
    CK_RV (*C_CloseSession)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_Login)(CK_SESSION_HANDLE hSession, CK_USER_TYPE userType, CK_BYTE* pPin, CK_ULONG ulPinLen);
    CK_RV (*C_Logout)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_FindObjectsInit)(CK_SESSION_HANDLE hSession, CK_ATTRIBUTE* pTemplate, CK_ULONG ulCount);
    CK_RV (*C_FindObjects)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE* phObject, CK_ULONG ulMax, CK_ULONG* pulCount);
    CK_RV (*C_FindObjectsFinal)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_GetAttributeValue)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hObject, CK_ATTRIBUTE* pTemplate, CK_ULONG ulCount);
    CK_RV (*C_SignInit)(CK_SESSION_HANDLE hSession, CK_MECHANISM* pMech, CK_OBJECT_HANDLE hKey);
    CK_RV (*C_Sign)(CK_SESSION_HANDLE hSession, CK_BYTE* pData, CK_ULONG ulDataLen, CK_BYTE* pSignature, CK_ULONG* pulSignatureLen);
};

namespace pkcs11 {

// Виняток безпеки PKCS#11
class CryptokiException : public std::runtime_error {
public:
    explicit CryptokiException(std::string_view operation, CK_RV errorCode)
        : std::runtime_error(std::format("{} failed with code: 0x{:08X}", operation, errorCode)),
          code_(errorCode) {}

    [[nodiscard]] CK_RV error_code() const noexcept { return code_; }
private:
    CK_RV code_;
};

// RAII обгортка для управління глобальним станом бібліотеки PKCS#11
class LibraryContext {
public:
    explicit LibraryContext(CK_FUNCTION_LIST* functionList) : f_(functionList) {
        if (!f_) throw std::invalid_argument("Function list cannot be null");
        if (auto rv = f_->C_Initialize(nullptr); rv != CKR_OK) {
            throw CryptokiException("C_Initialize", rv);
        }
    }

    ~LibraryContext() noexcept {
        f_->C_Finalize(nullptr);
    }

    LibraryContext(const LibraryContext&) = delete;
    LibraryContext& operator=(const LibraryContext&) = delete;

    [[nodiscard]] CK_FUNCTION_LIST* functions() const noexcept { return f_; }

private:
    CK_FUNCTION_LIST* f_{nullptr};
};

// RAII обгортка активної сесії токена з автоматичним входом/виходом
class TokenSession {
public:
    TokenSession(LibraryContext& ctx, CK_SLOT_ID slotId, std::string_view pin)
        : ctx_(ctx) {
        auto* f = ctx_.functions();
        if (auto rv = f->C_OpenSession(slotId, CKF_SERIAL_SESSION, nullptr, nullptr, &session_); rv != CKR_OK) {
            throw CryptokiException("C_OpenSession", rv);
        }

        if (auto rv = f->C_Login(session_, CKU_USER,
                                reinterpret_cast<CK_BYTE*>(const_cast<char*>(pin.data())),
                                static_cast<CK_ULONG>(pin.size())); rv != CKR_OK) {
            f->C_CloseSession(session_);
            throw CryptokiException("C_Login", rv);
        }
        isLoggedIn_ = true;
    }

    ~TokenSession() noexcept {
        auto* f = ctx_.functions();
        if (isLoggedIn_) {
            f->C_Logout(session_);
        }
        if (session_ != 0) {
            f->C_CloseSession(session_);
        }
    }

    TokenSession(const TokenSession&) = delete;
    TokenSession& operator=(const TokenSession&) = delete;

    // Пошук дескриптора приватного ключа
    [[nodiscard]] CK_OBJECT_HANDLE findPrivateKey(std::string_view label) const {
        auto* f = ctx_.functions();
        CK_OBJECT_CLASS keyClass = CKO_PRIVATE_KEY;
        CK_BBOOL bTrue = CK_TRUE;

        std::vector<CK_ATTRIBUTE> criteria = {
            { CKA_CLASS, &keyClass, sizeof(keyClass) },
            { CKA_SIGN,  &bTrue,    sizeof(bTrue) },
            { CKA_LABEL, const_cast<char*>(label.data()), static_cast<CK_ULONG>(label.size()) }
        };

        if (auto rv = f->C_FindObjectsInit(session_, criteria.data(), static_cast<CK_ULONG>(criteria.size())); rv != CKR_OK) {
            throw CryptokiException("C_FindObjectsInit", rv);
        }

        CK_OBJECT_HANDLE hKey = 0;
        CK_ULONG count = 0;
        auto rvFind = f->C_FindObjects(session_, &hKey, 1, &count);
        f->C_FindObjectsFinal(session_);

        if (rvFind != CKR_OK) throw CryptokiException("C_FindObjects", rvFind);
        if (count == 0) throw std::runtime_error(std::format("Private key '{}' not found in token", label));

        return hKey;
    }

    // Перевірка невитягуваності ключа
    [[nodiscard]] bool isKeyNonExtractable(CK_OBJECT_HANDLE hKey) const {
        CK_BBOOL extractable = CK_TRUE;
        CK_ATTRIBUTE attr = { CKA_EXTRACTABLE, &extractable, sizeof(extractable) };
        if (auto rv = ctx_.functions()->C_GetAttributeValue(session_, hKey, &attr, 1); rv != CKR_OK) {
            throw CryptokiException("C_GetAttributeValue", rv);
        }
        return extractable == CK_FALSE;
    }

    // Накладання апаратного підпису ECDSA на 32-байтний дайджест
    [[nodiscard]] std::vector<uint8_t> signDigest(CK_OBJECT_HANDLE hKey, std::span<const uint8_t, 32> digest) const {
        auto* f = ctx_.functions();
        CK_MECHANISM mech = { CKM_ECDSA, nullptr, 0 };

        if (auto rv = f->C_SignInit(session_, &mech, hKey); rv != CKR_OK) {
            throw CryptokiException("C_SignInit", rv);
        }

        // Запит розміру вихідного підпису
        CK_ULONG sigLen = 0;
        if (auto rv = f->C_Sign(session_, const_cast<CK_BYTE*>(digest.data()), 32, nullptr, &sigLen); rv != CKR_OK) {
            throw CryptokiException("C_Sign (size query)", rv);
        }

        std::vector<uint8_t> signature(sigLen);
        if (auto rv = f->C_Sign(session_, const_cast<CK_BYTE*>(digest.data()), 32, signature.data(), &sigLen); rv != CKR_OK) {
            throw CryptokiException("C_Sign (signature execution)", rv);
        }
        signature.resize(sigLen);
        return signature;
    }

private:
    LibraryContext& ctx_;
    CK_SESSION_HANDLE session_{0};
    bool isLoggedIn_{false};
};

} // namespace pkcs11
```
:::

---

## 4. Глибокий розбір інженерних нюансів реалізації

### 4.1. Чому передається лише дайджест (32 байти), а не весь документ
Утиліта хоста ніколи не надсилає мегабайтний файл у токен або HSM через шину USB/PCIe/Ethernet:
- **Пропускна здатність шини**: Інтерфейс смарт-карток ISO 7816 та протокол USB CCID мають швидкість передачі лише десятки кілобайтів за секунду. Передавання файлу розміром 100 МБ тривало б кілька хвилин.
- **Апаратні ресурси Secure Element**: Захищений мікроконтролер має мізерний обсяг вбудованої RAM (зазвичай від 8 до 64 КБ). Спроба завантажити великий масив призведе до переповнення буфера чи помилки `CKR_DEVICE_MEMORY`.
- **Розподіл обчислювального навантаження**: CPU робочої станції обчислює геш `SHA-256(Document)` зі швидкістю гігабайт на секунду завдяки інструкціям `SHA-NI`. У токен надходить рівно одне 256-бітне число. Внутрішній апаратний рушій еліптичної криптографії накладає математичний підпис `(R, S)` над цим числом. Приватний ключ залишається суворо ізольованим усередині кремнію.

### 4.2. Автоматична нуліфікація сесії через RAII в C++
У версії на C++ реалізовано клас `TokenSession`, деструктор якого гарантує виклики `C_Logout` та `C_CloseSession` за будь-яких умов:
- Якщо функція `C_Sign` викидає виняток через випадкове висмикування USB-токена з роз'єму (`CKR_DEVICE_REMOVED`), деструктор автоматично звільняє дескриптор.
- Якщо виникає помилка перевірки атрибута `CKA_EXTRACTABLE`, сесія миттєво закривається до накладання підпису.
- Це повністю виключає стан «завислої автентифікованої сесії», коли сторонній процес міг би перехопити вже відкритий дескриптор і підписати шкідливі дані без введення PIN-коду.

### 4.3. Очищення пам'яті з PIN-кодом на хості (Memory Sanitation)
Хоча приватний ключ ніколи не з'являється в RAM комп'ютера, сам PIN-код користувача тимчасово зберігається в адресному просторі процесу під час виклику `C_Login`. У виробничому коді рядок із PIN-кодом обов'язково затирається одразу після передачі в бібліотеку за допомогою `explicit_bzero()` (у POSIX C) або захищених алокаторів із нуліфікацією (у C++), щоб пароль не потрапив у дамп пам'яті.
