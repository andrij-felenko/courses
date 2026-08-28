# 📋 Довідник API стандарту PKCS#11 (Cryptoki v2.40 / v3.0)

Стандарт **PKCS#11** (Public-Key Cryptography Standards #11, також відомий як **Cryptoki**, від англ. *Cryptographic Token Interface*) визначає уніфікований платформонезалежний програмний інтерфейс (API) мовою C для взаємодії застосунків з апаратними модулями безпеки (HSM), смарт-картками, USB-токенами та криптографічними акселераторами.

Головна мета інтерфейсу Cryptoki — надати системі абстракцію апаратного токена, в якому зберігаються криптографічні об'єкти (сертифікати, відкриті та невитягувані приватні ключі), і виконувати над ними обчислювальні операції (генерація ключів, шифрування, накладання та перевірка цифрового підпису, узгодження секретів) без передавання бітів закритого ключа в оперативну пам'ять хоста.

---

## 1. Архітектурна модель Cryptoki

Стандарт PKCS#11 будує дворівневу логічну модель пристроїв:

1. **Слот (Slot, `CK_SLOT_ID`)**: Логічна або фізична точка підключення пристрою (наприклад, USB-порт, зчитувач смарт-карток, канал шини PCIe чи мережевий сокет до мережевого HSM).
2. **Токен (Token)**: Логічний криптографічний пристрій, присутній у слоті. Токен містить енергонезалежну пам'ять для об'єктів, апаратні криптопроцесори та підсистему автентифікації.
3. **Сесія (Session, `CK_SESSION_HANDLE`)**: Логічний канал зв'язку між клієнтським застосунком і конкретним токеном. Сесія може бути у стані «лише для читання» (`CKS_RO_PUBLIC_SESSION`, `CKS_RO_USER_FUNCTIONS`) або «для читання й запису» (`CKS_RW_PUBLIC_SESSION`, `CKS_RW_USER_FUNCTIONS`, `CKS_RW_SO_FUNCTIONS`).
4. **Об'єкт (Object, `CK_OBJECT_HANDLE`)**: Елемент даних, що зберігається в токені або прив'язаний до сесії. Об'єкти класифікуються за класами: дані (`CKO_DATA`), сертифікати (`CKO_CERTIFICATE`), відкриті ключі (`CKO_PUBLIC_KEY`), приватні ключі (`CKO_PRIVATE_KEY`), секретні симетричні ключі (`CKO_SECRET_KEY`) та апаратні профілі.

---

## 2. Базові типи даних та коди помилок

Всі типи даних PKCS#11 починаються з префікса `CK_`, а значення констант — з префікса відповідної категорії (`CKR_` для повертаних кодів, `CKA_` для атрибутів, `CKM_` для механізмів, `CKU_` для типів користувачів).

### 2.1. Основні числові та дескрипторні типи

```c
typedef unsigned char     CK_BYTE;
typedef unsigned char     CK_BBOOL;
typedef unsigned long int CK_ULONG;
typedef CK_ULONG          CK_RV;              /* Return Value / Код повернення */
typedef CK_ULONG          CK_SLOT_ID;         /* Ідентифікатор слота */
typedef CK_ULONG          CK_SESSION_HANDLE;  /* Дескриптор сесії */
typedef CK_ULONG          CK_OBJECT_HANDLE;   /* Дескриптор криптографічного об'єкта */
typedef CK_ULONG          CK_OBJECT_CLASS;    /* Клас об'єкта (CKO_*) */
typedef CK_ULONG          CK_KEY_TYPE;        /* Тип ключа (CKK_*) */
typedef CK_ULONG          CK_MECHANISM_TYPE;  /* Алгоритмічний механізм (CKM_*) */
typedef CK_ULONG          CK_ATTRIBUTE_TYPE;  /* Тип атрибута об'єкта (CKA_*) */
typedef CK_ULONG          CK_USER_TYPE;       /* Роль користувача (CKU_*) */
```

### 2.2. Структура криптографічного атрибута (`CK_ATTRIBUTE`)

Кожен об'єкт у пам'яті токена визначається набором типізованих атрибутів (пари «ключ-значення»):

```c
typedef struct CK_ATTRIBUTE {
    CK_ATTRIBUTE_TYPE type;       /* Наприклад: CKA_CLASS, CKA_LABEL, CKA_VALUE */
    void             *pValue;     /* Вказівник на буфер зі значенням атрибута */
    CK_ULONG          ulValueLen; /* Довжина значення атрибута в байтах */
} CK_ATTRIBUTE;

typedef CK_ATTRIBUTE *CK_ATTRIBUTE_PTR;
```

### 2.3. Структура криптографічного механізму (`CK_MECHANISM`)

Вказує алгоритм та параметри операції:

```c
typedef struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;      /* Наприклад: CKM_ECDSA, CKM_RSA_PKCS_PSS, CKM_SHA256_RSA_PKCS */
    void             *pParameter;     /* Додаткові параметри (наприклад, CK_RSA_PKCS_PSS_PARAMS) */
    CK_ULONG          ulParameterLen; /* Довжина параметрів у байтах (0, якщо без параметрів) */
} CK_MECHANISM;
```

### 2.4. Поширені коди повернення (`CK_RV`)

Функції стандарту PKCS#11 завжди повертають статус виконання типу `CK_RV`:

| Код повернення | Значення | Опис інженерної ситуації |
|---|---|---|
| `CKR_OK` | `0x00000000` | Операція завершилася успішно. |
| `CKR_CRYPTOKI_NOT_INITIALIZED` | `0x00000190` | Застосунок не викликав `C_Initialize` перед іншими функціями. |
| `CKR_SLOT_ID_INVALID` | `0x00000003` | Вказаний номер слота не існує в системі. |
| `CKR_TOKEN_NOT_PRESENT` | `0x000000E0` | У слоті відсутній апаратний токен (витягнуто USB-токен чи смарт-картку). |
| `CKR_PIN_INCORRECT` | `0x000000A0` | Введено невірний PIN-код. Апаратний лічильник невдалих спроб зменшено на 1. |
| `CKR_PIN_LOCKED` | `0x000000A4` | Лічильник невдалих спроб вичерпано. Токен заблоковано до введення адміністративного PUK-коду. |
| `CKR_SESSION_HANDLE_INVALID` | `0x000000B3` | Передано невалідний або закритий дескриптор сесії. |
| `CKR_USER_NOT_LOGGED_IN` | `0x00000101` | Операція вимагає прав користувача (`CKU_USER`), але виклик `C_Login` не виконувався. |
| `CKR_BUFFER_TOO_SMALL` | `0x00000150` | Наданий буфер замалий для збереження результату (наприклад, підпису чи ключа). |
| `CKR_ATTRIBUTE_TYPE_INVALID` | `0x00000012` | Спроба запитати чи встановити непідтримуваний для даного класу об'єкта атрибут. |
| `CKR_ACTION_PROHIBITED` | `0x0000001B` | Спроба порушити політику безпеки (наприклад, зчитати атрибут `CKA_VALUE` у приватного ключа з `CKA_SENSITIVE=TRUE`). |

---

## 3. Обов'язкові атрибути приватних і відкритих ключів

Для гарантії того, що приватний ключ ніколи не зможе бути вивантажений з апаратного токена, стандарт визначає булеві прапорці незворотної політики.

### 3.1. Атрибути безпеки приватного ключа (`CKO_PRIVATE_KEY`)

```
+---------------------+-------------+--------------------------------------------------------+
| Атрибут             | Тип         | Опис та значення за замовчуванням                      |
+---------------------+-------------+--------------------------------------------------------+
| CKA_CLASS           | CK_ULONG    | Завжди CKO_PRIVATE_KEY                                 |
| CKA_KEY_TYPE        | CK_ULONG    | CKK_RSA, CKK_EC (Elliptic Curve), CKK_EDDSA             |
| CKA_TOKEN           | CK_BBOOL    | CK_TRUE — об'єкт зберігається в незалежній пам'яті     |
| CKA_PRIVATE         | CK_BBOOL    | CK_TRUE — доступний лише після успішного C_Login       |
| CKA_LABEL           | Рядок UTF-8 | Людиночитана назва ключа (наприклад, "Production-Root") |
| CKA_ID              | CK_BYTE[]   | Бінарний ідентифікатор ключа (зазвичай SHA-1 від PubKey)|
| CKA_SENSITIVE       | CK_BBOOL    | CK_TRUE — атрибут CKA_VALUE не можна зчитати           |
| CKA_EXTRACTABLE     | CK_BBOOL    | CK_FALSE — ключ НЕ МОЖЕ бути експортований ні в якому  |
|                     |             | відкритому або загорнутому (wrapped) вигляді           |
| CKA_SIGN            | CK_BBOOL    | CK_TRUE — дозволено використання для цифрового підпису |
| CKA_DECRYPT         | CK_BBOOL    | Дозволено операції асиметричного розшифрування         |
| CKA_ALWAYS_AUTHENTICATE | CK_BBOOL| Якщо CK_TRUE — токен вимагає введення PIN або Touch    |
|                     |             | перед кожною окремою операцією C_Sign                  |
+---------------------+-------------+--------------------------------------------------------+
```

> ⚠️ **Інваріант невитягуваності:** Якщо об'єкт створено або згенеровано в токені з прапорцем `CKA_EXTRACTABLE = CK_FALSE`, стандарт PKCS#11 забороняє перемикання цього прапорця у `CK_TRUE`. Ця дія незворотна: ключ назавжди замкнений у кремнії.

---

## 4. Специфікація функцій життєвого циклу сесії та автентифікації

### 4.1. Ініціалізація та завершення роботи бібліотеки

```c
CK_RV C_Initialize(void *pInitArgs);
```
- **Призначення**: Завантажує драйвер PKCS#11, ініціалізує внутрішні потоки та структури пам'яті.
- **Аргументи**: `pInitArgs` — вказівник на структуру `CK_C_INITIALIZE_ARGS` (дозволяє налаштувати роботу з потоками ОС `CKF_OS_LOCKING_OK`) або `NULL`.
- **Коди**: `CKR_OK`, `CKR_CRYPTOKI_ALREADY_INITIALIZED`, `CKR_HOST_MEMORY`.

```c
CK_RV C_Finalize(void *pReserved);
```
- **Призначення**: Коректно закриває всі відкриті сесії та вивільняє ресурси бібліотеки.
- **Аргументи**: `pReserved` — повинен бути `NULL`.

---

### 4.2. Робота зі слотами та сесіями

```c
CK_RV C_GetSlotList(
    CK_BBOOL       tokenPresent, /* CK_TRUE — повернути лише слоти з підключеними токенами */
    CK_SLOT_ID_PTR pSlotList,    /* Масив для збереження ID слотів (або NULL) */
    CK_ULONG_PTR   pulCount      /* Вказівник на кількість слотів */
);
```
- **Шаблон використання**: Викликається двічі:
  1. Перший виклик з `pSlotList = NULL` для отримання необхідного розміру масиву в `*pulCount`.
  2. Застосунок виділяє буфер потрібної довжини.
  3. Другий виклик повертає реальні `CK_SLOT_ID`.

```c
CK_RV C_OpenSession(
    CK_SLOT_ID            slotID,        /* ID цільового слота */
    CK_FLAGS              flags,         /* Прапорці: CKF_SERIAL_SESSION, CKF_RW_SESSION */
    void                 *pApplication,  /* Вказівник користувача для callback-функцій */
    CK_NOTIFY             Notify,        /* Функція сповіщення або NULL */
    CK_SESSION_HANDLE_PTR phSession      /* Вихідний дескриптор створеної сесії */
);
```

```c
CK_RV C_CloseSession(CK_SESSION_HANDLE hSession);
```

---

### 4.3. Автентифікація користувача

```c
CK_RV C_Login(
    CK_SESSION_HANDLE hSession,  /* Дескриптор активної сесії */
    CK_USER_TYPE      userType,  /* CKU_USER (звичайний користувач) або CKU_SO (Security Officer) */
    CK_UTF8CHAR_PTR   pPin,      /* Вказівник на байти PIN-коду (без завершального нуля) */
    CK_ULONG          ulPinLen   /* Довжина PIN-коду в байтах */
);
```
- **Ролі користувачів**:
  - `CKU_USER`: Звичайний користувач токена, має доступ до приватних об'єктів (`CKA_PRIVATE = CK_TRUE`) для підпису та розшифрування.
  - `CKU_SO` (*Security Officer*): Адміністратор безпеки. Може ініціалізувати токен, змінювати PIN користувача, але **не має доступу** до операцій із приватними ключами користувача.
  - `CKU_CONTEXT_SPECIFIC`: Спеціальний режим для повторного введення PIN перед критичною дією (якщо встановлено `CKA_ALWAYS_AUTHENTICATE`).

```c
CK_RV C_Logout(CK_SESSION_HANDLE hSession);
```
- **Призначення**: Завершує автентифікований стан сесії, блокуючи доступ до приватних ключів до наступного успішного `C_Login`.

---

## 5. Специфікація функцій пошуку криптографічних об'єктів

```c
CK_RV C_FindObjectsInit(
    CK_SESSION_HANDLE hSession,   /* Дескриптор сесії */
    CK_ATTRIBUTE_PTR  pTemplate,  /* Шаблон пошуку (масив CK_ATTRIBUTE) */
    CK_ULONG          ulCount     /* Кількість атрибутів у шаблоні */
);

CK_RV C_FindObjects(
    CK_SESSION_HANDLE    hSession,          /* Дескриптор сесії */
    CK_OBJECT_HANDLE_PTR phObject,          /* Вихідний масив знайдених дескрипторів */
    CK_ULONG             ulMaxObjectCount,  /* Максимальна кількість об'єктів за виклик */
    CK_ULONG_PTR         pulObjectCount     /* Фактична кількість знайдених об'єктів */
);

CK_RV C_FindObjectsFinal(CK_SESSION_HANDLE hSession);
```

---

## 6. Специфікація функцій накладання цифрового підпису

Операція цифрового підпису в PKCS#11 складається з двох етапів: ініціалізація алгоритму та власне накладання підпису на геш або потік даних.

```c
CK_RV C_SignInit(
    CK_SESSION_HANDLE hSession,   /* Дескриптор сесії */
    CK_MECHANISM_PTR  pMechanism, /* Вказівник на структуру механізму (CKM_*) */
    CK_OBJECT_HANDLE  hKey        /* Дескриптор приватного ключа */
);
```
- **Призначення**: Переводить сесію у стан підпису, пов'язуючи її з конкретним апаратним ключем та алгоритмом.
- **Підтримувані механізми**:
  - `CKM_ECDSA`: Вхідні дані повинні бути сирим бінарним гешем (наприклад, 32 байти SHA-256). Результат — конкатенація цілих чисел `R || S`.
  - `CKM_RSA_PKCS`: Підпис RSA за стандартом PKCS#1 v1.5 з попереднім форматуванням DigestInfo.
  - `CKM_RSA_PKCS_PSS`: Підпис RSA з імовірнісним маскуванням PSS (потребує структури `CK_RSA_PKCS_PSS_PARAMS`).
  - `CKM_EDDSA`: Підпис за кривою Edwards Ed25519 (RFC 8032).

```c
CK_RV C_Sign(
    CK_SESSION_HANDLE hSession,        /* Дескриптор сесії */
    CK_BYTE_PTR       pData,           /* Вказівник на вхідний дайджест або дані */
    CK_ULONG          ulDataLen,       /* Довжина вхідних даних (наприклад, 32 байти) */
    CK_BYTE_PTR       pSignature,      /* Вихідний буфер для підпису (або NULL для запиту довжини) */
    CK_ULONG_PTR      pulSignatureLen  /* Вказівник на довжину підпису */
);
```

### Двоетапний виклик `C_Sign` (Two-pass Signature Sizing):

```c
/* Крок 1: Запит необхідного розміру підпису */
CK_ULONG sigLen = 0;
CK_RV rv = C_Sign(hSession, digest, 32, NULL, &sigLen);
if (rv != CKR_OK) {
    /* Обробка помилки */
}

/* Крок 2: Виділення пам'яті під буфер та отримання підпису */
CK_BYTE *signature = (CK_BYTE *)malloc(sigLen);
rv = C_Sign(hSession, digest, 32, signature, &sigLen);
if (rv == CKR_OK) {
    /* Підпис успішно накладено в апаратному чипі */
}
```

---

## 7. Генерація пари ключів у токені (`C_GenerateKeyPair`)

Для того, щоб приватний ключ ніколи не з'являвся на хості навіть під час його народження, застосунок викликає функцію апаратної генерації:

```c
CK_RV C_GenerateKeyPair(
    CK_SESSION_HANDLE    hSession,                    /* Дескриптор RW-сесії */
    CK_MECHANISM_PTR     pMechanism,                  /* CKM_EC_KEY_PAIR_GEN або CKM_RSA_PKCS_KEY_PAIR_GEN */
    CK_ATTRIBUTE_PTR     pPublicKeyTemplate,          /* Шаблон відкритого ключа */
    CK_ULONG             ulPublicKeyAttributeCount,   /* Кількість атрибутів відкритого ключа */
    CK_ATTRIBUTE_PTR     pPrivateKeyTemplate,         /* Шаблон приватного ключа */
    CK_ULONG             ulPrivateKeyAttributeCount,  /* Кількість атрибутів приватного ключа */
    CK_OBJECT_HANDLE_PTR phPublicKey,                 /* Дескриптор згенерованого PubKey */
    CK_OBJECT_HANDLE_PTR phPrivateKey                 /* Дескриптор згенерованого PrivKey */
);
```

### Приклад шаблону безпечної генерації ECDSA P-256:

```c
/* OID для кривої secp256r1 / NIST P-256: 1.2.840.10045.3.1.7 */
static CK_BYTE ec_p256_params[] = {
    0x06, 0x08, 0x2A, 0x86, 0x48, 0xCE, 0x3D, 0x03, 0x01, 0x07
};

CK_BBOOL bTrue  = CK_TRUE;
CK_BBOOL bFalse = CK_FALSE;
char privLabel[] = "Secure-Device-ECDSA-Key";
char pubLabel[]  = "Secure-Device-ECDSA-PubKey";

CK_ATTRIBUTE pubTemplate[] = {
    { CKA_TOKEN,         &bTrue,             sizeof(bTrue) },
    { CKA_VERIFY,        &bTrue,             sizeof(bTrue) },
    { CKA_ECDSA_PARAMS,  ec_p256_params,     sizeof(ec_p256_params) },
    { CKA_LABEL,         pubLabel,           strlen(pubLabel) }
};

CK_ATTRIBUTE privTemplate[] = {
    { CKA_TOKEN,         &bTrue,             sizeof(bTrue) },
    { CKA_PRIVATE,       &bTrue,             sizeof(bTrue) },
    { CKA_SENSITIVE,     &bTrue,             sizeof(bTrue) },
    { CKA_EXTRACTABLE,   &bFalse,            sizeof(bFalse) }, /* Заборона експорту назавжди */
    { CKA_SIGN,          &bTrue,             sizeof(bTrue) },
    { CKA_LABEL,         privLabel,          strlen(privLabel) }
};
```

---

## 8. Практичні інваріанти та типові пастки інтеграції

1. **Багатопоточність та блокування (`CKF_OS_LOCKING_OK`)**: Якщо бібліотеку PKCS#11 використовує багатопотоковий сервер, під час виклику `C_Initialize` обов'язково слід передавати структуру `CK_C_INITIALIZE_ARGS` із прапорцем `CKF_OS_LOCKING_OK`. Інакше паралельні виклики `C_Sign` із різних потоків призведуть до пошкодження пам'яті або взаємного блокування (Deadlock) усередині драйвера токена.
2. **Сесійні та токенні об'єкти (`CKA_TOKEN`)**: Якщо при створенні чи генерації ключа атрибут `CKA_TOKEN` встановлено в `CK_FALSE`, ключ створюється як *сесійний об'єкт* (Session Object). Він буде миттєво знищений з пам'яті токена після виклику `C_CloseSession` або відключення живлення токена. Для довготривалих ключів завжди потрібен `CKA_TOKEN = CK_TRUE`.
3. **Обмеження на передавання сирих даних**: Більшість апаратних токенів мають повільні канали зв'язку (USB CCID на швидкості 12 Мбіт/с або послідовні інтерфейси смарт-карток) та обмежену пам'ять буфера. Ніколи не слід надсилати повний мегабайтний файл у виклик `C_Sign` із механізмом `CKM_SHA256_RSA_PKCS`. Завжди обчислюйте геш SHA-256 локально на CPU хоста і передавайте в токен лише готові 32 байти дайджесту з механізмом `CKM_ECDSA` або `CKM_RSA_PKCS`.
