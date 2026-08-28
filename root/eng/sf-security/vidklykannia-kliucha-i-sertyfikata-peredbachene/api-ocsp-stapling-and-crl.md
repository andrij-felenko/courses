# 📋 Специфікація інтерфейсів і структур CRL, OCSP та OCSP Stapling

Мережеві протоколи перевірки статусу цифрових сертифікатів (від лат. *certus* — певний + *facere* — робити) стандартизовані комітетом IETF для забезпечення сумісності між клієнтськими пристроями, серверами додатків та центрами сертифікації (CA). У розподілених гетерогенних середовищах клієнтські термінали повинні однозначно інтерпретувати структури даних відкликання незалежно від апаратної платформи чи мови програмування.

Цей довідник описує точні бінарні структури ASN.1 DER, протокольні формати запитів та відповідей, розширення X.509, коди помилок і мережеві контракти для трьох базових механізмів: списків відкликання CRL (RFC 5280), протоколу онлайн-перевірки OCSP (RFC 6960) та розширення TLS OCSP Stapling (RFC 6066 / RFC 7633).

---

## 1. Специфікація списків відкликання сертифікатів (RFC 5280 CRL v2)

Список відкликаних сертифікатів (Certificate Revocation List — CRL) є підписаною центром сертифікації послідовністю ASN.1 DER, яку CA публікує за визначеною адресою розповсюдження (CRL Distribution Point — CRL DP). Клієнтський пристрій повинен підтримувати парсинг версії CRL v2 (числове значення поля `version` дорівнює 1).

### 1.1. Повна структура ASN.1 CertificateList

```asn1
CertificateList ::= SEQUENCE {
    tbsCertList          TBSCertList,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertList ::= SEQUENCE {
    version                 Version OPTIONAL, -- v2 (значення 1)
    signature               AlgorithmIdentifier,
    issuer                  Name,
    thisUpdate              Time,             -- Час публікації поточного CRL
    nextUpdate              Time OPTIONAL,    -- Граничний час чинності (дедлайн)
    revokedCertificates     SEQUENCE OF RevokedCertificateEntry OPTIONAL,
    crlExtensions           [0] EXPLICIT Extensions OPTIONAL
}

RevokedCertificateEntry ::= SEQUENCE {
    userCertificate         CertificateSerialNumber, -- Серійний номер сертифіката
    revocationDate          Time,                    -- Дата фактичного анулювання
    crlEntryExtensions      Extensions OPTIONAL      -- Причина та додаткові атрибути
}
```

### 1.2. Обов'язкові розширення списку CRL (crlExtensions)

Стандарт RFC 5280 визначає набір розширень, які клієнтський стек зобов'язаний обробляти для перевірки цілісності та актуальності списку:

1. **Ідентифікатор ключа центру сертифікації (Authority Key Identifier — AKI, OID `2.5.29.35`)**:
   Містить 160-бітний або 256-бітний геш відкритого ключа CA (`keyIdentifier`). Клієнт звіряє це поле з ідентифікатором ключа в сертифікаті CA, щоб переконатися, що список підписано саме тим ключем, який випустив перевірюваний сертифікат.
2. **Номер списку відкликання (CRL Number, OID `2.5.29.20`)**:
   Монотонно зростаюче ціле невід'ємне число, що збільшується з кожною новою публікацією CRL цим центром сертифікації. Клієнт зобов'язаний зберігати останній оброблений `crlNumber` і відхиляти списки з меншим або рівним номером для захисту від атак повторного відтворення застарілих даних (Replay Attacks).
3. **Покажчик дельта-списку (Delta CRL Indicator, OID `2.5.29.27`)**:
   Критичне розширення (значення `critical = TRUE`), що позначає файл як дельта-список (Delta CRL). Поле містить мінімальний номер базового списку (`BaseCRLNumber`), до якого застосовуються ці зміни. Якщо клієнт має локальний базовий CRL із номером, меншим за `BaseCRLNumber`, він зобов'язаний завантажити новий базовий список повністю.
4. **Точка випуску списку (Issuing Distribution Point, OID `2.5.29.28`)**:
   Визначає область дії CRL: чи містить він тільки сертифікати кінцевих суб'єктів (User Certs), тільки проміжні сертифікати (CA Certs), чи обмежений певними причинами відкликання.

### 1.3. Коди причин відкликання (CRLReason Enum)

Розширення кожного запису `reasonCode` (OID `2.5.29.21`) вказує точну причину скасування сертифіката:

| Код (Enum) | Назва константи | Опис та семантичний сценарій застосування |
|:---|:---|:---|
| `0` | `unspecified` | Причина не вказана (загальне або некласифіковане анулювання). |
| `1` | `keyCompromise` | Приватний ключ кінцевого пристрою або сервера викрадено чи розкрито. |
| `2` | `cACompromise` | Скомпрометовано приватний ключ центру сертифікації (повний крах довіри до гілки). |
| `3` | `affiliationChanged` | Зміна реквізитів суб'єкта (зміна власника пристрою або юридичної особи). |
| `4` | `superseded` | Сертифікат перевипущено з новими параметрами або на новий термін дії. |
| `5` | `cessationOfOperation` | Пристрій або сервер назавжди виведено з експлуатації та списано. |
| `6` | `certificateHold` | Тимчасове призупинення дії (сертифікат може бути розблоковано згодом). |
| `8` | `removeFromCRL` | Видалення із дельта-списку після відновлення дії сертифіката. |
| `9` | `privilegeWithdrawn` | Відкликання адміністративних прав або функціональних ролей пристрою. |

---

## 2. Протокол онлайн-перевірки статусу (RFC 6960 OCSP)

Протокол Online Certificate Status Protocol (OCSP) передає бінарні запити й відповіді у форматі ASN.1 DER поверх прикладного протоколу HTTP (порти 80 або 443).

### 2.1. Формат запиту OCSPRequest та структура CertID

Клієнт формує запит, який однозначно ідентифікує цільовий сертифікат без необхідності передачі його повного тексту:

```asn1
OCSPRequest ::= SEQUENCE {
    tbsRequest           TBSRequest,
    optionalSignature    [0] EXPLICIT Signature OPTIONAL
}

TBSRequest ::= SEQUENCE {
    version             [0] EXPLICIT Version DEFAULT v1 (0),
    requestorName       [1] EXPLICIT GeneralName OPTIONAL,
    requestList             SEQUENCE OF Request,
    requestExtensions   [2] EXPLICIT Extensions OPTIONAL
}

Request ::= SEQUENCE {
    reqCert                    CertID,
    singleRequestExtensions    [0] EXPLICIT Extensions OPTIONAL
}

CertID ::= SEQUENCE {
    hashAlgorithm       AlgorithmIdentifier, -- Зазвичай SHA-256 (OID 2.16.840.1.101.3.4.2.1)
    issuerNameHash      OCTET STRING,        -- Геш байтів поля Subject центру сертифікації
    issuerKeyHash       OCTET STRING,        -- Геш відкритого ключа (PubKey) центру сертифікації
    serialNumber        CertificateSerialNumber -- Серійний номер цільового сертифіката
}
```

#### Розширення захисту від повторів (OCSP Nonce Extension)
Клієнт може додати в поле `requestExtensions` розширення `Nonce` (OID `1.3.6.1.5.5.7.48.1.2`), що містить 16–32 байти криптографічно стійкої випадкової послідовності. Якщо респондер підтримує генерацію відповідей у реальному часі, він копіює цей Nonce у тіло підписаної відповіді. Це гарантує клієнту, що відповідь була згенерована саме у відповідь на цей запит і не є закешованою старою копією.

### 2.2. Формат відповіді OCSPResponse та делегування повноважень

```asn1
OCSPResponse ::= SEQUENCE {
    responseStatus         OCSPResponseStatus,
    responseBytes          [0] EXPLICIT ResponseBytes OPTIONAL
}

OCSPResponseStatus ::= ENUMERATED {
    successful            (0), -- Запит оброблено успішно
    malformedRequest      (1), -- Помилка синтаксису ASN.1 або структури запиту
    internalError         (2), -- Внутрішній збій сервера респондера
    tryLater              (3), -- Тимчасова перевантаженість (повторити пізніше)
    sigRequired           (5), -- Сервер вимагає криптографічного підпису запиту
    unauthorized          (6)  -- Клієнт не має авторизації запитувати цей статус
}

BasicOCSPResponse ::= SEQUENCE {
    tbsResponseData      ResponseData,
    signatureAlgorithm   AlgorithmIdentifier,
    signature            BIT STRING,
    certs                [0] EXPLICIT SEQUENCE OF Certificate OPTIONAL
}

ResponseData ::= SEQUENCE {
    version             [0] EXPLICIT Version DEFAULT v1,
    responderID             ResponderID,     -- За ім'ям (byName) або гешем ключа (byKey)
    producedAt              GeneralizedTime, -- Час підписання структури відповіді
    responses               SEQUENCE OF SingleResponse,
    responseExtensions  [1] EXPLICIT Extensions OPTIONAL
}

SingleResponse ::= SEQUENCE {
    certID                       CertID,
    certStatus                   CertStatus,
    thisUpdate                   GeneralizedTime,
    nextUpdate                   [0] EXPLICIT GeneralizedTime OPTIONAL,
    singleExtensions             [1] EXPLICIT Extensions OPTIONAL
}

CertStatus ::= CHOICE {
    good                [0] IMPLICIT NULL,
    revoked             [1] IMPLICIT RevokedInfo,
    unknown             [2] IMPLICIT UnknownInfo
}

RevokedInfo ::= SEQUENCE {
    revocationTime              GeneralizedTime,
    revocationReason    [0] EXPLICIT CRLReason OPTIONAL
}
```

#### Моделі довіри до підпису OCSP-респондера
Клієнтський криптографічний стек повинен підтримувати дві моделі авторизації підпису:
1. **Прямий підпис CA (Direct CA Signature)**: Відповідь підписана безпосередньо тим самим приватним ключем Root або Intermediate CA, який видав сертифікат.
2. **Делегований респондер (Authorized Responder)**: Відповідь підписана окремим ключем спеціалізованого сервера. У цьому випадку сертифікат респондера повинен:
   - Бути випущений безпосередньо тим самим CA (прямий нащадок);
   - Містити розширення `Extended Key Usage` (EKU) з обов'язковим призначенням `id-kp-OCSPSigning` (OID `1.3.6.1.5.5.7.3.9`);
   - Відповідати правилу: респондер не має права делегувати свої повноваження далі іншим серверам.

### 2.3. Мережевий транспорт OCSP через HTTP

- **MIME-тип запиту**: `Content-Type: application/ocsp-request`
- **MIME-тип відповіді**: `Content-Type: application/ocsp-response`
- **HTTP GET (кешований запит для CDN)**: Якщо розмір бінарного запиту не перевищує 255 байтів, клієнт кодує його в Base64 (URL-safe без символів перенесення) і надсилає GET-запит:
  ```http
  GET /ocsp/MFcwVTBTMFEwCQYFKw4DAhoFAAQU... HTTP/1.1
  Host: ocsp.ca-authority.com
  Accept: application/ocsp-response
  ```
- **HTTP POST (стандартний запит)**:
  ```http
  POST /ocsp HTTP/1.1
  Host: ocsp.ca-authority.com
  Content-Type: application/ocsp-request
  Content-Length: 84

  [бінарні байти ASN.1 DER структури OCSPRequest]
  ```

---

## 3. Специфікація OCSP Stapling (RFC 6066 / RFC 6961 / RFC 7633)

Механізм OCSP Stapling (офіційна назва у специфікації TLS — *Certificate Status Request*) позбавляє клієнта необхідності самостійно взаємодіяти з респондером CA під час кожного з'єднання.

### 3.1. Структура розширення ClientHello (status_request)

Під час ініціалізації TLS-рукостискання клієнт додає розширення `status_request` (тип 5, RFC 6066):

```asn1
struct {
    CertificateStatusType status_type;
    select (status_type) {
        case ocsp: OCSPStatusRequest;
    } request;
} CertificateStatusRequest;

enum { ocsp(1), (255) } CertificateStatusType;

struct {
    ResponderID responder_id_list<0..2^16-1>;
    Extensions  request_extensions<0..2^16-1>;
} OCSPStatusRequest;
```

Якщо клієнт залишає список `responder_id_list` порожнім (довжина 0), це означає готовність прийняти підписану відповідь від будь-якого авторизованого респондера для сертифіката сервера.

### 3.2. Передача статусу у протоколах TLS 1.2 та TLS 1.3

- **TLS 1.2 (RFC 5246 / RFC 6066)**:
  Сервер надсилає окреме повідомлення рукостискання `CertificateStatus` (тип повідомлення 22, код структури 11) безпосередньо після повідомлення `Certificate` і перед `ServerKeyExchange`:
  ```asn1
  struct {
      CertificateStatusType status_type;
      select (status_type) {
          case ocsp: OCSPResponse;
      } response;
  } CertificateStatus;
  ```
- **TLS 1.3 (RFC 8446)**:
  Архітектуру оптимізовано: окреме повідомлення `CertificateStatus` видалено. Замість цього бінарна відповідь OCSP передається безпосередньо всередині розширення `status_request` (тип 5) у списку розширень конкретного сертифіката:
  ```asn1
  struct {
      opaque cert_data<1..2^24-1>;
      Extension extensions<0..2^16-1>;
  } CertificateEntry;
  ```

### 3.3. Розширення обов'язкової прив'язки (OCSP Must-Staple, RFC 7633)

Для унеможливлення атак зі зниженням захисту (Downgrade Attacks), коли зловмисник блокує розширення `status_request` або сервер не надсилає відповідь OCSP, центр сертифікації записує в тіло сертифіката сервера розширення **TLS Feature Extension** (OID `1.3.6.1.5.5.7.1.24`):

```asn1
Features ::= SEQUENCE OF INTEGER

-- Значення 5 позначає обов'язковість розширення status_request (OCSP Stapling)
-- Значення 17 позначає обов'язковість status_request_v2 (Multi-Stapling для всього ланцюжка)
```

#### Алгоритмічний контракт верифікації клієнта
1. Клієнт розбирає розширення сертифіката сервера. Якщо знайдено `Features` зі значенням `5`, встановлюється внутрішній прапорець `must_staple_required = TRUE`.
2. Якщо прапорець `must_staple_required` активний, а сервер не надіслав `OCSPResponse` у процесі рукостискання, клієнт **зобов'язаний негайно розірвати сесію з фатальною помилкою TLS `bad_certificate_status_response (113)`**.
3. Якщо відповідь присутня, клієнт перевіряє:
   - Математичну валідність підпису респондера або CA;
   - Збіг `CertID` із сертифікатом сервера;
   - Умову свіжості за годинником реального часу: `thisUpdate <= Now <= nextUpdate`;
   - Статус сертифіката `certStatus == good`.
4. Будь-яке відхилення від цих умов перериває з'єднання без переходу в режим Soft-Fail.
